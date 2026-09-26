/*
 * min_adbd — minimal ADB daemon over USB FunctionFS (R36SX / MIPS32r2)
 *
 * r36sx-hclinux 9-6f: shell/debug channel that must NOT trigger the AVP blue
 * overlay. FunctionFS exposes a vendor-specific interface (class 0xFF,
 * subclass 0x42, protocol 0x01 — plain ADB), no netdev, no u_ether, no PPP:
 * same traffic profile as CDC-ACM serial shell (proven overlay-free).
 *
 * Scope (deliberately minimal, one stream at a time):
 *   - CNXN handshake (non-secure: no AUTH, no RSA)
 *   - "shell:" service only (ADB v1 raw stream; we advertise features=shell,
 *     so the host will NOT negotiate shell_v2/PTY)
 *   - flow control: exactly one outstanding device->host WRTE
 *   - everything else (sync/push/pull/tcp/...) -> CLSE
 *
 * ffs mount, gadget creation and UDC binding are done by adb_mode.sh; this
 * daemon only: ep0 descriptors -> open ep1/ep2 -> serve ADB.
 *
 * Build (see apps/adb_mode/README.md):
 *   mips-mti-linux-gnu-gcc -static -Os -o adbd min_adbd.c
 */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#include <linux/usb/ch9.h>
#include <linux/usb/functionfs.h>

/* ---------------- ADB wire protocol ---------------- */

#define A_SYNC 0x434e5953U /* "SYNC" */
#define A_CNXN 0x4e584e43U /* "CNXN" */
#define A_OPEN 0x4e45504fU /* "OPEN" */
#define A_OKAY 0x59414b4fU /* "OKAY" */
#define A_CLSE 0x45534c43U /* "CLSE" */
#define A_WRTE 0x45545257U /* "WRTE" */
#define A_AUTH 0x48545541U /* "AUTH" */

#define A_VERSION 0x01000001U
#define MAX_PAYLOAD 4096U

/* CNXN payload: identity + features. "shell" only (v1 raw) on purpose. */
#define CNXN_PAYLOAD "device::ro.product.name=R36SX;ro.product.model=R36SX V2.6;" \
	"ro.serialno=R36SX0001;ro.build.tags=test-keys;features=shell"

struct amessage {
	uint32_t command;
	uint32_t arg0;
	uint32_t arg1;
	uint32_t data_length;
	uint32_t data_check;
	uint32_t magic;
} __attribute__((packed));

/* ---------------- ffs descriptor sets (V2, fs + hs) ---------------- */

struct ep_desc {
	uint8_t bLength;
	uint8_t bDescriptorType;
	uint8_t bEndpointAddress;
	uint8_t bmAttributes;
	uint16_t wMaxPacketSize;
	uint8_t bInterval;
} __attribute__((packed));

struct if_desc {
	uint8_t bLength;
	uint8_t bDescriptorType;
	uint8_t bInterfaceNumber;
	uint8_t bAlternateSetting;
	uint8_t bNumEndpoints;
	uint8_t bInterfaceClass;    /* 0xFF vendor-specific */
	uint8_t bInterfaceSubClass; /* 0x42 ADB */
	uint8_t bInterfaceProtocol; /* 0x01 ADB */
	uint8_t iInterface;
} __attribute__((packed));

struct desc_block {
	struct if_desc iface;
	struct ep_desc ep_in;  /* first -> ep1 file (bulk IN, device->host) */
	struct ep_desc ep_out; /* second -> ep2 file (bulk OUT, host->device) */
} __attribute__((packed));

struct descs_v2 {
	uint32_t magic;    /* FUNCTIONFS_DESCRIPTORS_MAGIC_V2 */
	uint32_t length;   /* whole chunk length */
	uint32_t flags;    /* FUNCTIONFS_HAS_FS_DESC | FUNCTIONFS_HAS_HS_DESC */
	uint32_t fs_count; /* 3 */
	uint32_t hs_count; /* 3 */
	struct desc_block fs;
	struct desc_block hs;
} __attribute__((packed));

#define DESC_BLOCK_LEN (sizeof(struct desc_block))

static const struct descs_v2 g_descs = {
	.magic = FUNCTIONFS_DESCRIPTORS_MAGIC_V2,
	.length = sizeof(struct descs_v2),
	.flags = FUNCTIONFS_HAS_FS_DESC | FUNCTIONFS_HAS_HS_DESC,
	.fs_count = 3,
	.hs_count = 3,
	.fs = {
		.iface = { 9, USB_DT_INTERFACE, 0, 0, 2, 0xff, 0x42, 0x01, 0 },
		.ep_in = { 7, USB_DT_ENDPOINT, 0x81, USB_ENDPOINT_XFER_BULK, 64, 0 },
		.ep_out = { 7, USB_DT_ENDPOINT, 0x02, USB_ENDPOINT_XFER_BULK, 64, 0 },
	},
	.hs = {
		.iface = { 9, USB_DT_INTERFACE, 0, 0, 2, 0xff, 0x42, 0x01, 0 },
		.ep_in = { 7, USB_DT_ENDPOINT, 0x81, USB_ENDPOINT_XFER_BULK, 512, 0 },
		.ep_out = { 7, USB_DT_ENDPOINT, 0x02, USB_ENDPOINT_XFER_BULK, 512, 0 },
	},
};

/* ---------------- state ---------------- */

static int ep0_fd = -1, ep_in_fd = -1, ep_out_fd = -1;
static const char *g_dir = "/dev/ffs-adb";

static int have_stream;            /* shell service open */
static uint32_t local_id = 1;     /* our stream id */
static uint32_t remote_id;        /* host stream id */
static pid_t shell_pid = -1;
static int stdin_w = -1;          /* parent -> shell stdin */
static int stdout_r = -1;          /* shell stdout -> parent */
static int wrte_outstanding;      /* one in-flight device->host WRTE */

/* host->device reassembly stream (host may split packets arbitrarily) */
static uint8_t in_buf[2 * MAX_PAYLOAD];
static size_t in_len;

static void logmsg(const char *fmt, ...)
{
	va_list ap;
	va_start(ap, fmt);
	fputs("min_adbd: ", stderr);
	vfprintf(stderr, fmt, ap);
	fputc('\n', stderr);
	va_end(ap);
	fflush(stderr);
}

/* ---------------- crc32 (zlib/adb compatible) ---------------- */

static uint32_t crc_table[256];

static void crc32_init(void)
{
	for (uint32_t i = 0; i < 256; i++) {
		uint32_t c = i;
		for (int k = 0; k < 8; k++)
			c = (c & 1) ? 0xedb88320U ^ (c >> 1) : c >> 1;
		crc_table[i] = c;
	}
}

static uint32_t crc32_buf(const void *data, size_t len)
{
	const uint8_t *p = data;
	uint32_t c = 0xffffffffU;
	for (size_t i = 0; i < len; i++)
		c = crc_table[(c ^ p[i]) & 0xff] ^ (c >> 8);
	return c ^ 0xffffffffU;
}

/* ---------------- low-level io ---------------- */

static ssize_t xread(int fd, void *buf, size_t n)
{
	size_t got = 0;
	while (got < n) {
		ssize_t r = read(fd, (char *)buf + got, n - got);
		if (r < 0) {
			if (errno == EINTR)
				continue;
			return -1;
		}
		if (r == 0)
			break;
		got += (size_t)r;
	}
	return (ssize_t)got;
}

static int xwrite(int fd, const void *buf, size_t n)
{
	const char *p = buf;
	while (n) {
		ssize_t r = write(fd, p, n);
		if (r < 0) {
			if (errno == EINTR)
				continue;
			return -1;
		}
		p += r;
		n -= (size_t)r;
	}
	return 0;
}

/* one ADB packet -> single ffs write (header+payload in one USB request) */
static int send_pkt(uint32_t cmd, uint32_t arg0, uint32_t arg1,
		    const void *data, uint32_t len)
{
	uint8_t pkt[24 + MAX_PAYLOAD];
	struct amessage *h = (struct amessage *)pkt;

	if (len > MAX_PAYLOAD)
		return -1;
	memset(pkt, 0, sizeof(pkt));
	h->command = cmd;
	h->arg0 = arg0;
	h->arg1 = arg1;
	h->data_length = len;
	h->data_check = len ? crc32_buf(data, len) : 0; /* payload-only crc */
	h->magic = cmd ^ 0xffffffffU;
	if (len && data)
		memcpy(pkt + 24, data, len);
	return xwrite(ep_in_fd, pkt, 24 + len);
}

/* ---------------- shell service ---------------- */

static void shell_teardown(int send_clse)
{
	if (stdin_w >= 0) {
		close(stdin_w);
		stdin_w = -1;
	}
	if (shell_pid > 0) {
		kill(shell_pid, SIGKILL);
		waitpid(shell_pid, NULL, 0);
		shell_pid = -1;
	}
	if (stdout_r >= 0) {
		close(stdout_r);
		stdout_r = -1;
	}
	if (send_clse && have_stream && ep_in_fd >= 0) {
		send_pkt(A_CLSE, local_id, remote_id, NULL, 0);
		wrte_outstanding = 0;
	}
	have_stream = 0;
}

static int shell_start(const char *service)
{
	int in_pipe[2], out_pipe[2];
	const char *cmd = service + 5; /* skip "shell"; ":cmd" or "" */

	if (pipe(in_pipe) < 0 || pipe(out_pipe) < 0)
		return -1;

	pid_t pid = fork();
	if (pid < 0)
		return -1;
	if (pid == 0) {
		prctl(PR_SET_PDEATHSIG, SIGKILL, 0, 0, 0);
		close(in_pipe[1]);
		close(out_pipe[0]);
		dup2(in_pipe[0], 0);
		dup2(out_pipe[1], 1);
		dup2(out_pipe[1], 2);
		close(in_pipe[0]);
		close(out_pipe[1]);
		/* v1 raw: no PTY, interactive sh or "sh -c <cmd>" */
		if (cmd[0] == ':' && cmd[1] != '\0')
			execl("/bin/sh", "sh", "-c", cmd + 1, (char *)NULL);
		else
			execl("/bin/sh", "sh", (char *)NULL);
		_exit(127);
	}
	close(in_pipe[0]);
	close(out_pipe[1]);
	stdin_w = in_pipe[1];
	stdout_r = out_pipe[0];
	/* non-blocking: pump_shell_out() is also called from A_OKAY handling
	 * where no poll() guarantee exists — EAGAIN must mean "nothing yet" */
	fcntl(stdout_r, F_SETFL, O_NONBLOCK);
	shell_pid = pid;
	have_stream = 1;
	wrte_outstanding = 0;
	logmsg("shell pid=%d service='%s'", pid, service);
	return 0;
}

/* forward shell stdout as WRTE (respecting 1-packet flow control) */
static void pump_shell_out(void)
{
	static uint8_t chunk[MAX_PAYLOAD];
	if (!have_stream || wrte_outstanding || stdout_r < 0)
		return;
	ssize_t r = read(stdout_r, chunk, sizeof(chunk));
	if (r > 0) {
		if (send_pkt(A_WRTE, local_id, remote_id, chunk, (uint32_t)r) == 0)
			wrte_outstanding = 1;
	} else if (r == 0 || (r < 0 && errno != EAGAIN && errno != EINTR)) {
		logmsg("shell eof/err (r=%zd errno=%d)", r, errno);
		shell_teardown(1);
	}
}

/* ---------------- host->device packet handling ---------------- */

static void handle_host_pkt(const struct amessage *h, const uint8_t *data,
			    uint32_t len)
{
	switch (h->command) {
	case A_CNXN:
		send_pkt(A_CNXN, A_VERSION, MAX_PAYLOAD, CNXN_PAYLOAD,
			 (uint32_t)strlen(CNXN_PAYLOAD));
		break;
	case A_AUTH:
		/* non-secure device: re-assert connection identity */
		send_pkt(A_CNXN, A_VERSION, MAX_PAYLOAD, CNXN_PAYLOAD,
			 (uint32_t)strlen(CNXN_PAYLOAD));
		break;
	case A_OPEN:
		if (!have_stream && len >= 5 && len < MAX_PAYLOAD &&
		    strncmp((const char *)data, "shell", 5) == 0) {
			remote_id = h->arg0;
			if (shell_start((const char *)data) == 0)
				send_pkt(A_OKAY, local_id, remote_id, NULL, 0);
			else
				send_pkt(A_CLSE, local_id, h->arg0, NULL, 0);
		} else {
			/* only one stream; reject other services */
			send_pkt(A_CLSE, local_id, h->arg0, NULL, 0);
		}
		break;
	case A_OKAY:
		wrte_outstanding = 0;
		pump_shell_out();
		break;
	case A_WRTE:
		if (have_stream && h->arg0 == remote_id && stdin_w >= 0)
			xwrite(stdin_w, data, len);
		send_pkt(A_OKAY, local_id, remote_id, NULL, 0);
		break;
	case A_CLSE:
		shell_teardown(0);
		send_pkt(A_CLSE, local_id, h->arg0, NULL, 0);
		break;
	default:
		break;
	}
}

/* consume complete ADB packets from the host->device byte stream */
static void process_in_stream(void)
{
	const struct amessage *h = (const struct amessage *)in_buf;

	for (;;) {
		if (in_len < 24)
			return;
		if (h->magic != (h->command ^ 0xffffffffU))
			goto drop; /* corrupt stream: resync is out of scope */
		if (h->data_length > MAX_PAYLOAD)
			goto drop;
		if (in_len < 24 + h->data_length)
			return;
		handle_host_pkt(h, in_buf + 24, h->data_length);
		size_t consumed = 24 + h->data_length;
		in_len -= consumed;
		memmove(in_buf, in_buf + consumed, in_len);
	}
	return;
drop:
	logmsg("bad packet (cmd=0x%08x len=%u) — dropping stream", h->command,
	       (unsigned)in_len);
	in_len = 0;
}

/* ---------------- main ---------------- */

int main(int argc, char **argv)
{
	char path[256];
	struct pollfd pfd[4];

	if (argc > 1)
		g_dir = argv[1];

	crc32_init();
	signal(SIGPIPE, SIG_IGN);

	snprintf(path, sizeof(path), "%s/ep0", g_dir);
	/* O_NONBLOCK: the event-drain loop must not block when drained */
	ep0_fd = open(path, O_RDWR | O_NONBLOCK);
	if (ep0_fd < 0) {
		logmsg("open %s: %s", path, strerror(errno));
		return 1;
	}
	/*
	 * Descriptor write must complete before the endpoints are opened.
	 * xwrite() on a non-blocking fd with an empty queue still writes
	 * (ffs ep0 accepts writes when no transfer is pending), but be
	 * defensive: block for this one ioctl-like write via fcntl.
	 */
	fcntl(ep0_fd, F_SETFL, O_RDWR);
	if (xwrite(ep0_fd, &g_descs, sizeof(g_descs)) < 0) {
		logmsg("write descriptors: %s", strerror(errno));
		return 1;
	}
	fcntl(ep0_fd, F_SETFL, O_RDWR | O_NONBLOCK);

	snprintf(path, sizeof(path), "%s/ep1", g_dir);
	ep_in_fd = open(path, O_RDWR);
	snprintf(path, sizeof(path), "%s/ep2", g_dir);
	ep_out_fd = open(path, O_RDWR);
	if (ep_in_fd < 0 || ep_out_fd < 0) {
		logmsg("open endpoints: %s", strerror(errno));
		return 1;
	}
	logmsg("ready: ffs=%s (ff/42/01, 2 bulk eps)", g_dir);

	for (;;) {
		int n = 0;
		pfd[n].fd = ep0_fd;
		pfd[n].events = POLLIN;
		n++;
		pfd[n].fd = ep_out_fd;
		pfd[n].events = POLLIN;
		n++;
		int shell_idx = -1;
		if (have_stream && stdout_r >= 0) {
			shell_idx = n;
			pfd[n].fd = stdout_r;
			pfd[n].events = POLLIN;
			n++;
		}
		int rc = poll(pfd, (nfds_t)n, -1);
		if (rc < 0) {
			if (errno == EINTR)
				continue;
			logmsg("poll: %s", strerror(errno));
			break;
		}

		if (pfd[0].revents & (POLLERR | POLLHUP)) {
			logmsg("ep0 err/hup — exiting");
			break;
		}
		if (pfd[0].revents & POLLIN) {
			struct usb_functionfs_event ev;
			while (xread(ep0_fd, &ev, sizeof(ev)) ==
			       (ssize_t)sizeof(ev)) {
				if (ev.type == FUNCTIONFS_UNBIND ||
				    ev.type == FUNCTIONFS_DISABLE)
					logmsg("ffs event type=%d", ev.type);
			}
		}
		if (pfd[1].revents & (POLLERR | POLLHUP)) {
			logmsg("ep_out err/hup — exiting");
			break;
		}
		if (pfd[1].revents & POLLIN) {
			ssize_t r = read(ep_out_fd, in_buf + in_len,
					 sizeof(in_buf) - in_len);
			if (r < 0) {
				if (errno != EAGAIN && errno != EINTR) {
					logmsg("ep_out read: %s",
					       strerror(errno));
					break;
				}
			} else if (r == 0) {
				logmsg("ep_out EOF — exiting");
				break;
			} else {
				in_len += (size_t)r;
				process_in_stream();
			}
		}
		if (shell_idx >= 0 && pfd[shell_idx].revents & POLLIN)
			pump_shell_out();
	}

	shell_teardown(0);
	return 0;
}
