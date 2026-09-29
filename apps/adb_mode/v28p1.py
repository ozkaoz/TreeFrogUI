import io

src = io.open('min_adbd.c', encoding='utf-8').read()

# ---- 1. globals: sync state + command timeout ----
old = '''static char pending_cmd[256];      /* stashed by A_OPEN, run from main loop */'''
new = '''static char pending_cmd[256];      /* stashed by A_OPEN, run from main loop */

/* ---- sync service (adb pull/push) state ----
 * v1 sync protocol (our banner advertises features=shell only, so the
 * client never negotiates v2): packed little-endian structs, native on
 * MIPS LE. Paths map to /mnt/sdcard/ (the console SD). Runs ENTIRELY in
 * the main loop tick: pure I/O, zero forks, paced by the writer queue.
 */
static int sync_mode;              /* stream is a "sync:" service */
static int sync_fd = -1;           /* file being pushed/pulled */
static int sync_state;             /* 0=idle, 1=recv_data, 2=send_data */
enum { SYNC_IDLE = 0, SYNC_RECV, SYNC_SEND };
static uint8_t sync_in[8 * 1024];
static size_t sync_in_len;
static char sync_path[512];
static uint32_t sync_mtime;        /* push: mtime from DONE */

/* command timeout (self-healing shell): a command whose marker never
 * arrives is reaped and CLSEd so the session stays usable */
static int cmd_deadline;           /* main-loop ticks (10ms each) */
#define CMD_TIMEOUT_TICKS 3000     /* 30 s */'''
assert old in src
src = src.replace(old, new)

# ---- 2. sync helpers (place before handle_host_pkt) ----
anchor = '''/* ---------------- host->device packet handling ---------------- */'''
helpers = '''/* ---- sync service implementation ---- */

/* map an adb path to the console SD: strip leading '/' and an optional
 * "sdcard" prefix, prepend /mnt/sdcard/ */
static void sync_map_path(const char *in, char *out, size_t outsz)
{
	const char *p = in;
	while (*p == '/')
		p++;
	if (strncmp(p, "sdcard", 6) == 0 && (p[6] == '/' || p[6] == '\\0'))
		p += p[6] == '/' ? 7 : 6;
	snprintf(out, outsz, "/mnt/sdcard/%s", p);
}

/* free slots in the writer queue */
static int q_space(void)
{
	pthread_mutex_lock(&q_mutex);
	int used = (q_tail - q_head + Q_SLOTS) % Q_SLOTS;
	pthread_mutex_unlock(&q_mutex);
	return Q_SLOTS - 1 - used;
}

static void sync_reply(const void *buf, size_t n)
{
	send_pkt(A_WRTE, local_id, remote_id, buf, n);
}

static void sync_fail(const char *msg)
{
	uint8_t out[8 + 256];
	uint32_t id = ID_FAIL_MK;
	uint32_t msglen = (uint32_t)strlen(msg);
	memcpy(out, &id, 4);
	memcpy(out + 4, &msglen, 4);
	memcpy(out + 8, msg, msglen);
	sync_reply(out, 8 + msglen);
}

/* process one step of the sync protocol; called from the main loop tick */
static void sync_tick(void)
{
	if (q_space() < 2)
		return;

	if (sync_state == SYNC_RECV) {
		/* stream the file out in DATA chunks */
		uint8_t out[8 + 4088];
		uint32_t id_data = ID_DATA_MK;
		ssize_t r = read(sync_fd, out + 8, 4088);
		if (r > 0) {
			uint32_t sz = (uint32_t)r;
			memcpy(out, &id_data, 4);
			memcpy(out + 4, &sz, 4);
			sync_reply(out, 8 + (size_t)r);
		} else {
			struct stat st;
			uint32_t id_done = ID_DONE_MK;
			uint32_t mtime = 0;
			if (fstat(sync_fd, &st) == 0)
				mtime = (uint32_t)st.st_mtime;
			close(sync_fd);
			sync_fd = -1;
			sync_state = SYNC_IDLE;
			memcpy(out, &id_done, 4);
			memcpy(out + 4, &mtime, 4);
			sync_reply(out, 8);
			logmsg("sync: pull done mtime=%u", mtime);
		}
		return;
	}

	/* parse requests from sync_in */
	while (sync_in_len >= 8 && q_space() >= 2) {
		uint32_t id, len;
		memcpy(&id, sync_in, 4);
		memcpy(&len, sync_in + 4, 4);

		if (id == ID_QUIT_MK) {
			logmsg("sync: QUIT");
			sync_in_len = 0;
			pthread_mutex_lock(&q_mutex);
			int hs = have_stream;
			have_stream = 0;
			sync_mode = 0;
			pthread_mutex_unlock(&q_mutex);
			if (hs)
				send_pkt(A_CLSE, local_id, remote_id, NULL, 0);
			return;
		}
		if (id == ID_RECV_MK) {
			if (sync_in_len < 8 + len)
				return;
			if (len >= sizeof(sync_path) - 32)
				goto eat;
			memcpy(sync_path, sync_in + 8, len);
			sync_path[len] = '\\0';
			memmove(sync_in, sync_in + 8 + len, sync_in_len - 8 - len);
			sync_in_len -= 8 + len;
			char mapped[512];
			sync_map_path(sync_path, mapped, sizeof(mapped));
			sync_fd = open(mapped, O_RDONLY);
			if (sync_fd < 0) {
				logmsg("sync: pull open FAIL %s (%s)", mapped, strerror(errno));
				sync_fail(strerror(errno));
			} else {
				logmsg("sync: pull %s", mapped);
				sync_state = SYNC_RECV;
			}
			continue;
		}
		if (id == ID_SEND_MK) {
			if (sync_in_len < 8 + len)
				return;
			if (len >= sizeof(sync_path) - 32)
				goto eat;
			memcpy(sync_path, sync_in + 8, len);
			sync_path[len] = '\\0';
			/* SEND v1 path: "path,mode" */
			char *comma = strrchr(sync_path, ',');
			uint32_t mode = 0644;
			if (comma) {
				*comma = '\\0';
				mode = (uint32_t)strtoul(comma + 1, NULL, 8);
			}
			memmove(sync_in, sync_in + 8 + len, sync_in_len - 8 - len);
			sync_in_len -= 8 + len;
			char mapped[512];
			sync_map_path(sync_path, mapped, sizeof(mapped));
			sync_fd = open(mapped, O_WRONLY | O_CREAT | O_TRUNC, mode);
			if (sync_fd < 0) {
				logmsg("sync: push open FAIL %s (%s)", mapped, strerror(errno));
				sync_fail(strerror(errno));
			} else {
				logmsg("sync: push %s (mode=%o)", mapped, mode);
				sync_state = SYNC_SEND;
			}
			continue;
		}
		if (id == ID_DATA_MK && sync_state == SYNC_SEND) {
			if (sync_in_len < 8 + len)
				return;
			if (sync_fd >= 0)
				xwrite(sync_fd, sync_in + 8, len);
			memmove(sync_in, sync_in + 8 + len, sync_in_len - 8 - len);
			sync_in_len -= 8 + len;
			continue;
		}
		if (id == ID_DONE_MK && sync_state == SYNC_SEND) {
			memcpy(&sync_mtime, sync_in + 4, 4);
			memmove(sync_in, sync_in + 8, sync_in_len - 8);
			sync_in_len -= 8;
			if (sync_fd >= 0) {
				fsync(sync_fd);
				close(sync_fd);
				sync_fd = -1;
			}
			sync_state = SYNC_IDLE;
			uint32_t ok = ID_OKAY_MK, zero = 0;
			uint8_t out[8];
			memcpy(out, &ok, 4);
			memcpy(out + 4, &zero, 4);
			sync_reply(out, 8);
			logmsg("sync: push done mtime=%u", sync_mtime);
			continue;
		}
		if (id == ID_STAT_MK || id == ID_LSTAT_MK) {
			if (sync_in_len < 8 + len)
				return;
			if (len >= sizeof(sync_path) - 32)
				goto eat;
			memcpy(sync_path, sync_in + 8, len);
			sync_path[len] = '\\0';
			memmove(sync_in, sync_in + 8 + len, sync_in_len - 8 - len);
			sync_in_len -= 8 + len;
			char mapped[512];
			sync_map_path(sync_path, mapped, sizeof(mapped));
			struct stat st;
			uint8_t out[16];
			uint32_t mid = ID_STAT_MK;
			uint32_t mode = 0, size = 0, mtime = 0;
			if (stat(mapped, &st) == 0) {
				mode = (uint32_t)st.st_mode;
				size = (uint32_t)st.st_size;
				mtime = (uint32_t)st.st_mtime;
			}
			memcpy(out, &mid, 4);
			memcpy(out + 4, &mode, 4);
			memcpy(out + 8, &size, 4);
			memcpy(out + 12, &mtime, 4);
			sync_reply(out, 16);
			continue;
		}
eat:
		/* unknown id: drop the whole buffer (resync not possible) */
		logmsg("sync: unknown id 0x%08x len=%u — dropping", id, len);
		sync_in_len = 0;
	}
}

/* ---------------- host->device packet handling ---------------- */'''
assert anchor in src
src = src.replace(anchor, helpers, 1)

# the MK id constants (before the helpers)
src = src.replace('#define CMD_TIMEOUT_TICKS 3000     /* 30 s */',
'''#define CMD_TIMEOUT_TICKS 3000     /* 30 s */

/* sync protocol ids (MKID: little-endian 4-char codes) */
#define ID_STAT_MK   0x54415453U /* "STAT" */
#define ID_LSTAT_MK  0x54534c53U /* "LST2"-> unused; real LSTAT is "STAT" too in v1 via id reuse */
#define ID_RECV_MK   0x56434552U /* "RECV" */
#define ID_SEND_MK   0x444e4553U /* "SEND" */
#define ID_DATA_MK   0x41544144U /* "DATA" */
#define ID_DONE_MK   0x454e4f44U /* "DONE" */
#define ID_OKAY_MK   0x59414b4fU /* "OKAY" */
#define ID_FAIL_MK   0x4c494146U /* "FAIL" */
#define ID_QUIT_MK   0x54495551U /* "QUIT" */''')

io.open('min_adbd.c', 'w', encoding='utf-8').write(src)
print('V28_PART1_OK')
