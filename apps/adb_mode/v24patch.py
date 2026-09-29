import io, re

src = io.open('min_adbd.c', encoding='utf-8').read()

# ---- 1. globals: exit flag for clean shutdown on UNBIND ----
src = src.replace(
    'static int diag_ticks;\nstatic int heartbeats;',
    'static int diag_ticks;\nstatic int heartbeats;\nstatic volatile sig_atomic_t g_exit; /* set by the ep0 thread on UNBIND */')

# ---- 2. thread functions: ep0 thread + reader thread ----
# insert before main
anchor = '/* ---------------- main ---------------- */'
threads = '''/* ---------------- ffs-isolation threads (v24) ----------------
 * ROOT CAUSE (closed): the vendor f_fs ignores O_NONBLOCK in BOTH
 * directions — ANY syscall on the ffs fds can block indefinitely.
 * Architecture: every ffs fd is owned by a dedicated thread that IS
 * allowed to block (reader/writer/ep0); the main loop only touches
 * pipes/procfs/usleep (well-behaved). The protocol brain can never
 * be frozen by the USB layer again. */

static void *ep0_thread(void *arg)
{
	(void)arg;
	struct usb_functionfs_event ev;
	for (;;) {
		ssize_t r = read(ep0_fd, &ev, sizeof(ev)); /* blocking OK */
		if (r != (ssize_t)sizeof(ev))
			break;
		logmsg("ffs event type=%d", (int)ev.type);
		if (ev.type == FUNCTIONFS_UNBIND) {
			g_exit = 1;
			break;
		}
	}
	logmsg("ep0 thread done");
	return NULL;
}

/* the ONLY toucher of ep_out_fd: blocking host->device reads */
static void *reader_thread(void *arg)
{
	(void)arg;
	for (;;) {
		ssize_t r = read(ep_out_fd, in_buf + in_len,
				 sizeof(in_buf) - in_len); /* blocking OK */
		if (r < 0) {
			if (errno == EINTR)
				continue;
			logmsg("ep_out read: %s", strerror(errno));
			g_exit = 1;
			break;
		}
		if (r == 0) {
			logmsg("ep_out EOF");
			g_exit = 1;
			break;
		}
		in_len += (size_t)r;
		process_in_stream();
	}
	logmsg("reader thread done");
	return NULL;
}

'''
src = src.replace(anchor, threads + anchor)

# ---- 3. thread-safe stream state: the A_OPEN/CNXN/CLSE handlers run in the
# reader thread; guard have_stream/pending_cmd/wrte_outstanding with q_mutex ----
old_open = '''		if (!have_stream && strncmp(svc, "shell", 5) == 0) {
			remote_id = h->arg0;
			/* "-c command" only: "shell:cmd" -> stash; the main
			 * loop spawns via -c argv (proven). Interactive "shell:"
			 * (no command) -> CLSE (unsupported: ash
			 * interactive on a pipe is the frozen variant). */
			if (svc[5] == ':' && svc[6] != '\\0') {
				size_t cl = strlen(svc + 6);
				if (cl >= sizeof(pending_cmd))
					cl = sizeof(pending_cmd) - 1;
				memcpy(pending_cmd, svc + 6, cl);
				pending_cmd[cl] = '\\0';
				have_stream = 1;
				wrte_outstanding = 0;
				logmsg("OPEN stream (cmd='%s')", pending_cmd);
				send_pkt(A_OKAY, local_id, remote_id, NULL, 0);
			} else {'''
new_open = '''		if (!have_stream && strncmp(svc, "shell", 5) == 0) {
			remote_id = h->arg0;
			/* "-c command" only: "shell:cmd" -> stash; the main
			 * loop feeds it to the startup worker. Interactive
			 * "shell:" (no command) -> CLSE (unsupported here). */
			if (svc[5] == ':' && svc[6] != '\\0') {
				pthread_mutex_lock(&q_mutex);
				size_t cl = strlen(svc + 6);
				if (cl >= sizeof(pending_cmd))
					cl = sizeof(pending_cmd) - 1;
				memcpy(pending_cmd, svc + 6, cl);
				pending_cmd[cl] = '\\0';
				have_stream = 1;
				wrte_outstanding = 0;
				pthread_mutex_unlock(&q_mutex);
				logmsg("OPEN stream (cmd='%s')", pending_cmd);
				send_pkt(A_OKAY, local_id, remote_id, NULL, 0);
			} else {'''
assert old_open in src
src = src.replace(old_open, new_open)

# ---- 4. main loop: strip the ffs reads; keep feed/pump/diag/hb/usleep ----
loop_start = src.index('\tfor (;;) {\n\t\t/* ep0: drain ffs events nonblocking */')
loop_end = src.index('out_dead:\n')
old_loop = src[loop_start:loop_end]

new_loop = '''	for (;;) {
		if (g_exit)
			break;

		/* feed the worker if a command is pending (pipe I/O only) */
		pthread_mutex_lock(&q_mutex);
		int do_feed = have_stream && pending_cmd[0] && worker_in >= 0;
		pthread_mutex_unlock(&q_mutex);
		if (do_feed) {
			pthread_mutex_lock(&q_mutex);
			char cmd[256];
			memcpy(cmd, pending_cmd, sizeof(cmd));
			pending_cmd[0] = '\\0';
			pthread_mutex_unlock(&q_mutex);
			int rc = xwrite(worker_in, cmd, strlen(cmd));
			rc |= xwrite(worker_in, "\\necho ", 6);
			rc |= xwrite(worker_in, DONE_MARK,
				      sizeof(DONE_MARK) - 1);
			rc |= xwrite(worker_in, "\\n", 1);
			logmsg("worker fed rc=%d", rc);
			diag_ticks = 15;
			heartbeats = 15;
		}

		/* worker output pump (pipe reads — well-behaved fds only) */
		pump_worker_out();

		/* diagnostics on the working timer */
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
'''
src = src.replace(old_loop, new_loop)

# ---- 5. pump: guard wrte_outstanding under q_mutex ----
old_pump_guard = '''	if (!have_stream || wrte_outstanding || worker_out < 0)
		return;'''
new_pump_guard = '''	pthread_mutex_lock(&q_mutex);
	if (!have_stream || wrte_outstanding || worker_out < 0) {
		pthread_mutex_unlock(&q_mutex);
		return;
	}
	pthread_mutex_unlock(&q_mutex);'''
assert old_pump_guard in src
src = src.replace(old_pump_guard, new_pump_guard)
# and the set of wrte_outstanding=1 in the pump paths:
src = src.replace('''			if (send_pkt(A_WRTE, local_id, remote_id, hold,
				     (uint32_t)hold_len) == 0)
				wrte_outstanding = 1;''',
'''			if (send_pkt(A_WRTE, local_id, remote_id, hold,
				     (uint32_t)hold_len) == 0) {
				pthread_mutex_lock(&q_mutex);
				wrte_outstanding = 1;
				pthread_mutex_unlock(&q_mutex);
			}''')
src = src.replace('''			if (send_pkt(A_WRTE, local_id, remote_id,
				    hold, (uint32_t)pre) == 0)
				wrte_outstanding = 1;''',
'''			if (send_pkt(A_WRTE, local_id, remote_id,
				    hold, (uint32_t)pre) == 0) {
				pthread_mutex_lock(&q_mutex);
				wrte_outstanding = 1;
				pthread_mutex_unlock(&q_mutex);
			}''')
src = src.replace('''			if (send_pkt(A_WRTE, local_id, remote_id, chunk,
				     (uint32_t)send_now) == 0)
				wrte_outstanding = 1;''',
'''			if (send_pkt(A_WRTE, local_id, remote_id, chunk,
				     (uint32_t)send_now) == 0) {
				pthread_mutex_lock(&q_mutex);
				wrte_outstanding = 1;
				pthread_mutex_unlock(&q_mutex);
			}''')
src = src.replace('''		if (send_pkt(A_WRTE, local_id, remote_id,
				    chunk, (uint32_t)pre) == 0)
				wrte_outstanding = 1;''',
'''		if (send_pkt(A_WRTE, local_id, remote_id,
				    chunk, (uint32_t)pre) == 0) {
				pthread_mutex_lock(&q_mutex);
				wrte_outstanding = 1;
				pthread_mutex_unlock(&q_mutex);
			}''')
src = src.replace('''		if (pre && send_pkt(A_WRTE, local_id, remote_id,
				    chunk, (uint32_t)pre) == 0)
			wrte_outstanding = 1;''',
'''		if (pre && send_pkt(A_WRTE, local_id, remote_id,
				    chunk, (uint32_t)pre) == 0) {
			pthread_mutex_lock(&q_mutex);
			wrte_outstanding = 1;
			pthread_mutex_unlock(&q_mutex);
		}''')

# ---- 6. A_OKAY handler: clear under mutex; no pump call (main loop pumps) ----
old_okay = '''	case A_OKAY:
		wrte_outstanding = 0;
		pump_worker_out();
		break;'''
new_okay = '''	case A_OKAY:
		pthread_mutex_lock(&q_mutex);
		wrte_outstanding = 0;
		pthread_mutex_unlock(&q_mutex);
		break; /* the main-loop pump picks it up on its next tick */'''
assert old_okay in src
src = src.replace(old_okay, new_okay)

# ---- 7. CNXN stale reset + CLSE: guard under q_mutex ----
old_cnxn_reset = '''		if (have_stream) {
			logmsg("CNXN with stale stream — resetting");
			worker_teardown(1, 0);
		}'''
new_cnxn_reset = '''		pthread_mutex_lock(&q_mutex);
		if (have_stream) {
			pthread_mutex_unlock(&q_mutex);
			logmsg("CNXN with stale stream — resetting");
			worker_teardown(1, 0);
		} else {
			pthread_mutex_unlock(&q_mutex);
		}'''
assert old_cnxn_reset in src
src = src.replace(old_cnxn_reset, new_cnxn_reset)

# ---- 8. launch the three threads before the main loop ----
old_launch = '''	pthread_t wth;
	if (pthread_create(&wth, NULL, writer_thread, NULL) != 0)
		logmsg("WARN: writer thread create failed");

	for (;;) {'''
new_launch = '''	pthread_t wth, rth, eth;
	if (pthread_create(&wth, NULL, writer_thread, NULL) != 0)
		logmsg("WARN: writer thread create failed");
	if (pthread_create(&rth, NULL, reader_thread, NULL) != 0)
		logmsg("WARN: reader thread create failed");
	if (pthread_create(&eth, NULL, ep0_thread, NULL) != 0)
		logmsg("WARN: ep0 thread create failed");
	logmsg("threads up (writer/reader/ep0)");

	for (;;) {'''
assert old_launch in src
src = src.replace(old_launch, new_launch)

# ---- 9. remove the leftover 'out_dead:' label block after the loop ----
src = src.replace('''		usleep(10000);
	}
out_dead:
	worker_teardown(1, 0);
	return 0;''', '''		usleep(10000);
	}
	logmsg("main loop done (g_exit=%d)", (int)g_exit);
	worker_teardown(1, 0);
	return 0;''')

io.open('min_adbd.c', 'w', encoding='utf-8').write(src)
print('V24_PATCH_OK')
