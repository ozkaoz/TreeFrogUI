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
#include <pthread.h>

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

/* child-side trace target (pre/post-exec instrumentation) */
#define ADB_LOG "/mnt/sdcard/ADB_MODE_DEBUG.log"

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

/*
 * ffs state machine: READ_DESCRIPTORS -> READ_STRINGS -> epfiles_create ->
 * FFS_ACTIVE (f_fs.c:330-395). ep1/ep2 exist only AFTER the strings phase.
 * Our descriptors reference no strings (iInterface=0), so the kernel accepts
 * a minimal empty block: str_count=0 + lang_count=0 (f_fs.c:2600 "if we
 * don't need any strings just return").
 */
struct strings_v2 {
	uint32_t magic;     /* FUNCTIONFS_STRINGS_MAGIC */
	uint32_t length;    /* 16 */
	uint32_t str_count; /* 0 — no descriptor string refs */
	uint32_t lang_count;
} __attribute__((packed));

static const struct strings_v2 g_strings = {
	FUNCTIONFS_STRINGS_MAGIC,
	sizeof(struct strings_v2),
	0,
	0,
};

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
static pid_t worker_pid = -1;     /* persistent ash worker */
static int worker_in = -1;         /* daemon -> worker stdin */
static int worker_out = -1;        /* worker stdout -> daemon */
static int wrte_outstanding;       /* one in-flight device->host WRTE */
static char pending_cmd[256];      /* stashed by A_OPEN, run from main loop */
static int diag_ticks;
static int heartbeats;             /* wchan self-diagnostics remaining */

/* host->device reassembly stream (host may split packets arbitrarily) */
static uint8_t in_buf[2 * MAX_PAYLOAD];
static size_t in_len;

/* device->host pending write queue. ROOT CAUSE FIX (2026-09-28,
 * keeper2 experiment): ffs IN-endpoint writes BLOCK until the host
 * consumes them — with no pending host read the daemon froze INSIDE
 * send_pkt (the whole "mute" mystery). ep_in is now O_NONBLOCK and
 * packets are queued here + retried from the main loop: the daemon can
 * never block on a USB write again, whatever the host reader pattern.
 * Layout: [24B header][payload] — the header must go out as its OWN
 * transfer (adb's Windows backend reads exactly-24 header chunks). */
/* v23: dedicated WRITER THREAD. ROOT CAUSE (empirically closed):
 * ffs IN-endpoint writes block until the host consumes them —
 * O_NONBLOCK is IGNORED by this vendor f_fs (v22 froze inside the
 * OKAY write). A write landing in a gap of the adb server's reader
 * pattern froze the WHOLE daemon. Now the main loop NEVER writes
 * ep_in: packets are queued here and a dedicated pthread does the
 * blocking writes. A host-reader stall can only stall the writer —
 * the protocol core keeps processing packets and drains the queue
 * when the reader returns. */
#define Q_SLOTS 8
static uint8_t pkt_q[Q_SLOTS][24 + MAX_PAYLOAD];
static size_t pkt_q_len[Q_SLOTS];
static int q_head, q_tail;
static pthread_mutex_t q_mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t q_cond = PTHREAD_COND_INITIALIZER;

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

/* writer thread: the ONLY place that writes ep_in (blocking OK —
 * dedicated thread; the main loop never freezes on USB writes) */
static void *writer_thread(void *arg)
{
	(void)arg;
	for (;;) {
		pthread_mutex_lock(&q_mutex);
		while (q_head == q_tail)
			pthread_cond_wait(&q_cond, &q_mutex);
		uint8_t *p = pkt_q[q_head];
		size_t len = pkt_q_len[q_head];
		pthread_mutex_unlock(&q_mutex);

		/* header as its OWN USB transfer (adb reads exactly-24
		 * chunks), then payload, then ZLP if 512-multiple */
		if (xwrite(ep_in_fd, p, 24) < 0)
			logmsg("writer: hdr write err=%d", errno);
		if (len > 24) {
			if (xwrite(ep_in_fd, p + 24, len - 24) < 0)
				logmsg("writer: payload err=%d", errno);
			if (((len - 24) & 511) == 0 &&
			    xwrite(ep_in_fd, p, 0) < 0)
				logmsg("writer: zlp err=%d", errno);
		}
		pthread_mutex_lock(&q_mutex);
		q_head = (q_head + 1) % Q_SLOTS;
		pthread_mutex_unlock(&q_mutex);
	}
	return NULL;
}

/* Send one ADB packet as TWO separate ffs writes = TWO USB transfers
 * (header, then payload) — same as real adbd (daemon/usb.cpp Write():
 * header block + payload blocks; usb_ffs zero_mask ZLP). adb's Windows
 * backend reads each header with a chunked read that REQUIRES exactly
 * 24 bytes (transport_usb.cpp UsbReadMessage: n != 24 -> connection
 * terminated). One combined write delivers header+payload in a single
 * USB transfer and adb drops the device (root cause of the 2026-09-27
 * CNXN loop). Payload sized as a multiple of the HS maxpacket (512)
 * additionally needs a ZLP so the transfer boundary is explicit. */
static int send_pkt(uint32_t cmd, uint32_t arg0, uint32_t arg1,
		    const void *data, uint32_t len)
{
	uint8_t hdr[24];
	struct amessage *h = (struct amessage *)hdr;

	if (len > MAX_PAYLOAD)
		return -1;
	memset(hdr, 0, sizeof(hdr));
	h->command = cmd;
	h->arg0 = arg0;
	h->arg1 = arg1;
	h->data_length = len;
	h->data_check = len ? crc32_buf(data, len) : 0; /* payload-only crc */
	h->magic = cmd ^ 0xffffffffU;

	/* enqueue for the writer thread (main loop never writes ep_in) */
	pthread_mutex_lock(&q_mutex);
	int next = (q_tail + 1) % Q_SLOTS;
	if (next == q_head) {
		logmsg("q full — dropping pkt 0x%08x", cmd);
		pthread_mutex_unlock(&q_mutex);
		return -1;
	}
	memcpy(pkt_q[q_tail], hdr, 24);
	pkt_q_len[q_tail] = 24;
	if (len && data) {
		memcpy(pkt_q[q_tail] + 24, data, len);
		pkt_q_len[q_tail] = 24 + len;
	}
	q_tail = next;
	pthread_cond_signal(&q_cond);
	pthread_mutex_unlock(&q_mutex);
	return 0;
}


/* ---------------- shell worker (persistent ash) ----------------
 * ARCHITECTURE (v11): the daemon NEVER forks from the packet-handler
 * context — every fork+exec from inside handle_host_pkt froze in
 * execve on this console (2026-09-28, all theories eliminated: fd
 * collisions, fd0, prctl, RAM/SD exec, argv length 1..80, fork
 * ordinal, 4KB stack frame). The ONLY fork+exec shape that ALWAYS
 * completes is the one spawned from main-loop/top-level context
 * (startup selftest: 100% success across every session).
 * Model: ONE interactive ash worker with pipes; commands flow as
 * stdin lines; "cmd\nexit\n" per -c open so the worker EOFs and the
 * stream CLSEs (adb shell returns). The main loop respawns the
 * worker at top level when a new OPEN needs one. Ash's OWN fork+exec
 * for commands is v3-proven ("uname: invalid option" output flowed). */

static void worker_teardown(int kill_worker, int send_clse)
{
	if (kill_worker) {
		if (worker_pid > 0) {
			kill(worker_pid, SIGKILL);
			waitpid(worker_pid, NULL, 0);
			worker_pid = -1;
		}
		if (worker_out >= 0) {
			close(worker_out);
			worker_out = -1;
		}
	}
	if (send_clse && have_stream && ep_in_fd >= 0) {
		send_pkt(A_CLSE, local_id, remote_id, NULL, 0);
		wrte_outstanding = 0;
	}
	have_stream = 0;
	pending_cmd[0] = '\0';
}

static void ctrace(const char *msg)
{
	int t = open(ADB_LOG, O_WRONLY | O_APPEND | O_CREAT, 0644);
	if (t >= 0) {
		dprintf(t, "child[%d]: %s\n", (int)getpid(), msg);
		close(t);
	}
}

/* self-diagnostics: sample the worker's /proc state into the log.
 * The daemon itself runs fine in the live state, and /proc is RAM —
 * this is the NCM-free way to see WHY the worker is mute. */
static void worker_diag(int tick)
{
	char path[64], buf[512], wbuf[80];
	ssize_t r;
	int fd;

	if (worker_pid <= 0)
		return;
	snprintf(path, sizeof(path), "/proc/%d/stat", (int)worker_pid);
	fd = open(path, O_RDONLY);
	if (fd < 0) {
		logmsg("diag t=%d: /proc/%d/stat gone (worker dead?)",
		       tick, (int)worker_pid);
		return;
	}
	r = read(fd, buf, sizeof(buf) - 1);
	close(fd);
	if (r <= 0)
		return;
	buf[r] = '\0';
	/* state = char after the last ') ' of the comm field */
	char *close_paren = strrchr(buf, ')');
	char state = (close_paren && close_paren[1] == ' ') ?
			     close_paren[2] : '?';
	wbuf[0] = '\0';
	snprintf(path, sizeof(path), "/proc/%d/wchan", (int)worker_pid);
	fd = open(path, O_RDONLY);
	if (fd >= 0) {
		r = read(fd, wbuf, sizeof(wbuf) - 1);
		close(fd);
		if (r <= 0)
			snprintf(wbuf, sizeof(wbuf), "<unreadable>");
		else
			wbuf[r < (ssize_t)sizeof(wbuf) - 1 ?
				     r : (ssize_t)sizeof(wbuf) - 1] = '\0';
	} else {
		snprintf(wbuf, sizeof(wbuf), "<no wchan>");
	}
	logmsg("diag t=%d state=%c wchan=%s", tick, state, wbuf);
}

/* Interactive ash worker, spawned ONCE AT STARTUP — before the gadget
 * binds: the only fork+exec state proven to complete AND run (the
 * live-gadget state mutes any newly-exec'd process: ash-alive logged
 * then silence, 2026-09-28 v13/v14 evidence). Commands are fed as
 * stdin lines; completion detected via the DONE_MARK echoed by the
 * daemon itself after each command (pump filters it and CLSEs). */
static int worker_spawn(void)
{
	int in_pipe[2], out_pipe[2];

	if (pipe(in_pipe) < 0 || pipe(out_pipe) < 0)
		return -1;
	pid_t pid = fork();
	if (pid < 0)
		return -1;
	if (pid == 0) {
		ctrace("worker: pre-exec");
		close(in_pipe[1]);
		close(out_pipe[0]);
		dup2(in_pipe[0], 0);
		dup2(out_pipe[1], 1);
		dup2(out_pipe[1], 2);
		close(in_pipe[0]);
		close(out_pipe[1]);
		setenv("PATH", "/tmp/bin:/bin:/sbin:/usr/bin:/usr/sbin", 1);
		/* v20: worker = cat — the simplest possible stdin->stdout
		 * pumper. Eliminates ash entirely: if cat answers the feed,
		 * ash is the problem; if cat also mutes, the kernel pipe
		 * wake path is broken. */
		const char *bb = access("/tmp/bin/busybox", X_OK) == 0 ?
				  "/tmp/bin/busybox" : "/bin/busybox";
		execl(bb, "busybox", "cat", (char *)NULL);
		ctrace("worker: exec FAILED (see errno)");
		{
			int t = open(ADB_LOG, O_WRONLY | O_APPEND | O_CREAT,
				     0644);
			if (t >= 0) {
				dprintf(t, "child[%d]: exec errno=%d\n",
					(int)getpid(), errno);
				close(t);
			}
		}
		_exit(127);
	}
	close(in_pipe[0]);
	close(out_pipe[1]);
	worker_in = in_pipe[1];
	worker_out = out_pipe[0];
	fcntl(worker_out, F_SETFL, O_NONBLOCK);
	worker_pid = pid;
	logmsg("worker pid=%d up (startup, interactive)", pid);
	return 0;
}

/* forward worker stdout as WRTE (respecting 1-packet flow control).
 * Scans for the completion marker (echoed by the daemon after every
 * fed command): everything before it is command output; on marker ->
 * CLSE (adb shell returns). The worker stays alive for the next OPEN.
 * Marker may split across reads: the tail is held back while it could
 * still be a marker prefix. */
#define DONE_MARK "@@R36SX_DONE@@"

static void pump_worker_out(void)
{
	static uint8_t chunk[MAX_PAYLOAD];
	static uint8_t hold[32];
	static size_t hold_len;
	size_t mlen = sizeof(DONE_MARK) - 1;

	if (!have_stream || wrte_outstanding || worker_out < 0)
		return;
	/* complete a held-back tail first */
	if (hold_len) {
		ssize_t r = read(worker_out, hold + hold_len,
				 sizeof(hold) - hold_len);
		if (r < 0) {
			if (errno == EAGAIN || errno == EINTR)
				return;
		}
		if (r <= 0) {
			/* EOF/err with a held tail: flush it then teardown */
			if (send_pkt(A_WRTE, local_id, remote_id, hold,
				     (uint32_t)hold_len) == 0)
				wrte_outstanding = 1;
			hold_len = 0;
			logmsg("worker eof/err after hold (r=%zd)", r);
			worker_teardown(0, 1);
			worker_pid = -1;
			if (worker_out >= 0) {
				close(worker_out);
				worker_out = -1;
			}
			return;
		}
		hold_len += (size_t)r;
		uint8_t *m = memmem(hold, hold_len, DONE_MARK, mlen);
		if (m) {
			size_t pre = (size_t)(m - hold);
			/* strip the marker line's leading newline */
			if (pre > 0 && hold[pre - 1] == '\n')
				pre--;
			if (pre && send_pkt(A_WRTE, local_id, remote_id,
					    hold, (uint32_t)pre) == 0)
				wrte_outstanding = 1;
			logmsg("done-marker (held path) pre=%zu", pre);
			hold_len = 0;
			worker_teardown(0, 1);
			return;
		}
		/* not a marker: flush the whole hold minus a possible
		 * partial-marker tail */
		size_t send_now = hold_len;
		for (size_t k = 1; k < mlen && k < hold_len; k++) {
			if (hold[hold_len - k] == DONE_MARK[0] &&
			    hold_len - k + mlen > hold_len &&
			    memcmp(hold + hold_len - k, DONE_MARK,
				   k) == 0) {
				send_now = hold_len - k;
				break;
			}
		}
		if (send_now) {
			if (send_pkt(A_WRTE, local_id, remote_id, hold,
				     (uint32_t)send_now) == 0)
				wrte_outstanding = 1;
			memmove(hold, hold + send_now, hold_len - send_now);
			hold_len -= send_now;
		}
		if (hold_len >= mlen)
			hold_len = 0; /* impossible marker: drop */
		return;
	}
	/* fresh read */
	ssize_t r = read(worker_out, chunk, sizeof(chunk));
	if (r > 0) {
		size_t len = (size_t)r;
		uint8_t *m = memmem(chunk, len, DONE_MARK, mlen);
		if (m) {
			size_t pre = (size_t)(m - chunk);
			if (pre > 0 && chunk[pre - 1] == '\n')
				pre--;
			if (pre && send_pkt(A_WRTE, local_id, remote_id,
					    chunk, (uint32_t)pre) == 0)
				wrte_outstanding = 1;
			logmsg("done-marker pre=%zu total=%zu", pre, len);
			hold_len = 0;
			worker_teardown(0, 1); /* CLSE; worker stays alive */
			return;
		}
		/* hold back a possible partial-marker tail */
		size_t send_now = len;
		for (size_t k = 1; k < mlen && k < len; k++) {
			if (chunk[len - k] == DONE_MARK[0] &&
			    memcmp(chunk + len - k, DONE_MARK, k) == 0) {
				send_now = len - k;
				break;
			}
		}
		if (send_now) {
			if (send_pkt(A_WRTE, local_id, remote_id, chunk,
				     (uint32_t)send_now) == 0)
				wrte_outstanding = 1;
			logmsg("pump: %zu bytes rc=0", send_now);
		}
		if (send_now < len) {
			hold_len = len - send_now;
			memcpy(hold, chunk + send_now, hold_len);
		}
	} else if (r == 0 || (r < 0 && errno != EAGAIN && errno != EINTR)) {
		logmsg("worker eof/err (r=%zd errno=%d)", r, errno);
		worker_teardown(0, 1);
		worker_pid = -1;
		if (worker_out >= 0) {
			close(worker_out);
			worker_out = -1;
		}
	}
}

/* ---------------- host->device packet handling ---------------- */

static void selftest_exec(const char *tag);

static void handle_host_pkt(const struct amessage *h, const uint8_t *data,
			    uint32_t len)
{
	switch (h->command) {
	case A_CNXN:
		/* A new connection resets any orphaned stream state: a
		 * previous host may have vanished mid-stream (probe, crash,
		 * unplug) leaving have_stream stuck — that would CLSE-reject
		 * every OPEN of the new connection (evidence 2026-09-27:
		 * server OPEN -> CLSE loop after a probe left a stream open). */
		if (have_stream) {
			logmsg("CNXN with stale stream — resetting");
			worker_teardown(1, 0);
		}
		send_pkt(A_CNXN, A_VERSION, MAX_PAYLOAD, CNXN_PAYLOAD,
			 (uint32_t)strlen(CNXN_PAYLOAD));
		break;
	case A_AUTH:
		/* non-secure device: re-assert connection identity */
		send_pkt(A_CNXN, A_VERSION, MAX_PAYLOAD, CNXN_PAYLOAD,
			 (uint32_t)strlen(CNXN_PAYLOAD));
		break;
	case A_OPEN: {
		/* Defensive copy: the service string must be NUL-terminated
		 * (real adb sends it, len includes the NUL); never let the
		 * parser read past data_length. NO FORK HERE — see the
		 * worker architecture note above. */
		static char svc[MAX_PAYLOAD];
		uint32_t sl = len < MAX_PAYLOAD - 1 ? len : MAX_PAYLOAD - 1;

		memcpy(svc, data, sl);
		svc[sl] = '\0';
		if (!have_stream && strncmp(svc, "shell", 5) == 0) {
			remote_id = h->arg0;
			/* "-c command" only: "shell:cmd" -> stash; the main
			 * loop spawns via -c argv (proven). Interactive
			 * "shell:" (no command) -> CLSE (unsupported: ash
			 * interactive on a pipe is the frozen variant). */
			if (svc[5] == ':' && svc[6] != '\0') {
				size_t cl = strlen(svc + 6);
				if (cl >= sizeof(pending_cmd))
					cl = sizeof(pending_cmd) - 1;
				memcpy(pending_cmd, svc + 6, cl);
				pending_cmd[cl] = '\0';
				have_stream = 1;
				wrte_outstanding = 0;
				logmsg("OPEN stream (cmd='%s')", pending_cmd);
				send_pkt(A_OKAY, local_id, remote_id, NULL, 0);
			} else {
				logmsg("OPEN interactive — rejected (ash on pipe frozen)");
				send_pkt(A_CLSE, local_id, h->arg0, NULL, 0);
			}
		} else {
			/* only one stream; reject other services */
			send_pkt(A_CLSE, local_id, h->arg0, NULL, 0);
		}
		break;
	}
	case A_OKAY:
		wrte_outstanding = 0;
		pump_worker_out();
		break;
	case A_WRTE:
		/* -c only: no interactive stdin. Swallow (OKAY keeps the
		 * flow control sane) — nothing to forward to. */
		send_pkt(A_OKAY, local_id, remote_id, NULL, 0);
		break;
	case A_CLSE:
		worker_teardown(1, 0);
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

static volatile sig_atomic_t g_alarm_fired;
static void alarm_handler(int sig)
{
	(void)sig;
	g_alarm_fired = 1;
}

/*
 * Startup self-test: fork + exec(RAM sh) + pipe in the daemon's own
 * context. Evidence 2026-09-28: shells fork (pid logged) but never write
 * to the pipe nor exit — the child freezes. This tells us whether
 * fork+exec completes HERE. 3 s alarm guard; logs the outcome either way.
 */
static void selftest_exec(const char *tag)
{
	int p[2];
	char buf[80];
	ssize_t n;

	if (pipe(p) < 0) {
		logmsg("%s selftest: pipe FAIL errno=%d", tag, errno);
		return;
	}
	pid_t pid = fork();
	if (pid < 0) {
		logmsg("%s selftest: fork FAIL errno=%d", tag, errno);
		return;
	}
	if (pid == 0) {
		close(p[0]);
		dup2(p[1], 1);
		dup2(p[1], 2);
		close(p[1]);
		close(0);
		setenv("PATH", "/tmp/bin:/bin:/sbin:/usr/bin:/usr/sbin", 1);
		/* exercise builtin AND an external applet (uname) — the
		 * v8 selftest only proved builtins */
		const char *sh = access("/tmp/bin/sh", X_OK) == 0 ?
				 "/tmp/bin/sh" : "/bin/sh";
		execl(sh, "sh", "-c",
		      "echo selftest-ok; /tmp/bin/busybox uname -m",
		      (char *)NULL);
		_exit(127);
	}
	close(p[1]);
	signal(SIGALRM, alarm_handler);
	g_alarm_fired = 0;
	alarm(3);
	n = read(p[0], buf, sizeof(buf) - 1);
	int saved = errno;
	alarm(0);
	signal(SIGALRM, SIG_DFL);
	if (g_alarm_fired || (n < 0 && saved == EINTR)) {
		logmsg("%s selftest: STUCK (n=%zd) — fork+exec does not complete in daemon context",
		       tag, n);
	} else if (n > 0) {
		size_t e = (size_t)n < sizeof(buf) - 1 ? (size_t)n : sizeof(buf) - 1;
		while (e > 0 && (buf[e - 1] == '\n' || buf[e - 1] == '\r'))
			e--;
		buf[e] = '\0';
		logmsg("%s selftest: fork+exec OK — '%s'", tag, buf);
	} else {
		logmsg("%s selftest: EOF without output (n=%zd errno=%d)",
		       tag, n, saved);
	}
	close(p[0]);
	waitpid(pid, NULL, 0);
}

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
	if (xwrite(ep0_fd, &g_strings, sizeof(g_strings)) < 0) {
		logmsg("write strings: %s", strerror(errno));
		return 1;
	}
	fcntl(ep0_fd, F_SETFL, O_RDWR | O_NONBLOCK);

	snprintf(path, sizeof(path), "%s/ep1", g_dir);
	/* O_NONBLOCK: ffs IN writes block until the host consumes — the
	 * daemon must never freeze on a write (root cause of the whole
	 * shell-mute mystery; see out_pending note) */
	ep_in_fd = open(path, O_RDWR | O_NONBLOCK);
	snprintf(path, sizeof(path), "%s/ep2", g_dir);
	/* nonblocking: the main loop is a watcher-style spin (usleep +
	 * nonblocking checks) — poll()'s hrtimer path never fires on this
	 * vendor kernel (evidence: 1000ms poll timeouts never returned,
	 * while the exit_watcher's usleep cycles work perfectly) */
	ep_out_fd = open(path, O_RDWR | O_NONBLOCK);
	if (ep_in_fd < 0 || ep_out_fd < 0) {
		logmsg("open endpoints: %s", strerror(errno));
		return 1;
	}
	logmsg("ready: ffs=%s (ff/42/01, 2 bulk eps)", g_dir);
	selftest_exec("startup");
	if (worker_spawn() != 0)
		logmsg("WARN: worker spawn failed — shells will CLSE");

	pthread_t wth;
	if (pthread_create(&wth, NULL, writer_thread, NULL) != 0)
		logmsg("WARN: writer thread create failed");

	for (;;) {

		/* WATCHER-STYLE LOOP (no poll()): this console's vendor
		 * kernel never fires poll()'s hrtimer timeout (v18-v21
		 * evidence: 1000ms poll timeouts never returned; the
		 * exit_watcher's usleep cycles work flawlessly). Every fd
		 * is nonblocking; usleep(10ms) paces the spin. */

		/* ep0: drain ffs events nonblocking */
		for (;;) {
			struct usb_functionfs_event ev;
			ssize_t r = read(ep0_fd, &ev, sizeof(ev));
			if (r != (ssize_t)sizeof(ev))
				break;
			logmsg("ffs event type=%d", (int)ev.type);
		}

		/* ep_out: host->device stream, nonblocking */
		for (;;) {
			ssize_t r = read(ep_out_fd, in_buf + in_len,
					 sizeof(in_buf) - in_len);
			if (r < 0) {
				if (errno != EAGAIN && errno != EINTR) {
					logmsg("ep_out read: %s",
					       strerror(errno));
					goto out_dead;
				}
				break;
			}
			if (r == 0) {
				logmsg("ep_out EOF — exiting");
				goto out_dead;
			}
			in_len += (size_t)r;
			process_in_stream();
		}

		/* feed the worker if a command is pending (pipe I/O) */
		if (have_stream && pending_cmd[0] && worker_in >= 0) {
			int rc = xwrite(worker_in, pending_cmd,
					strlen(pending_cmd));
			rc |= xwrite(worker_in, "\necho ", 6);
			rc |= xwrite(worker_in, DONE_MARK,
				      sizeof(DONE_MARK) - 1);
			rc |= xwrite(worker_in, "\n", 1);
			pending_cmd[0] = '\0';
			logmsg("worker fed rc=%d", rc);
			diag_ticks = 15;
			heartbeats = 15;
		}

		/* worker output pump (nonblocking) */
		pump_worker_out();

		/* diagnostics sampling on the working timer (usleep) */
		if (diag_ticks > 0) {
			worker_diag(16 - diag_ticks);
			diag_ticks--;
		}
		if (heartbeats > 0) {
			logmsg("hb alive hb=%d", 16 - heartbeats);
			heartbeats--;
		}

		usleep(10000);
	}
out_dead:
	worker_teardown(1, 0);
	return 0;
}
