/* http_file_proxy.c — file-based HTTP proxy for the R36SX console.
 * Plan B for internet via ADB (the adb reverse device-initiated OPEN
 * is not processed by the Windows ADB server v37).
 *
 * Architecture:
 *   CONSOLE (this program): listens on 0.0.0.0:3128
 *     1. Accept HTTP request from wget/curl
 *     2. Save raw request to /mnt/sdcard/.proxy/req
 *     3. Create trigger /mnt/sdcard/.proxy/go
 *     4. Poll for /mnt/sdcard/.proxy/resp (PC fetches and pushes it)
 *     5. Send response to the HTTP client
 *     6. Cleanup and loop
 *
 *   PC (companion loop): polls for trigger, pulls request,
 *   fetches via curl/Invoke-WebRequest, pushes response.
 *
 * Build: mips-mti-linux-gnu-gcc -static -Os -s -o http_proxy http_file_proxy.c
 * Deploy: adb push http_proxy /treefrog/http_proxy
 * Console: chmod +x /treefrog/http_proxy && /treefrog/http_proxy &
 * Console: export http_proxy=http://127.0.0.1:3128
 * PC: powershell -File proxy_pc.ps1
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/stat.h>

#define PORT       3128
#define PROXY_DIR  "/mnt/sdcard/.proxy"
#define REQ_FILE   PROXY_DIR "/req"
#define RESP_FILE  PROXY_DIR "/resp"
#define GO_FILE    PROXY_DIR "/go"
#define LOG_FILE   "/mnt/sdcard/.proxy/log"
#define MAX_REQ    (64 * 1024)
#define MAX_RESP   (4 * 1024 * 1024) /* 4MB response cap */

static void logmsg(const char *msg)
{
	FILE *f = fopen(LOG_FILE, "a");
	if (f) {
		fprintf(f, "%s\n", msg);
		fclose(f);
	}
}

static int wait_for_file(const char *path, int timeout_sec)
{
	int elapsed = 0;
	while (elapsed < timeout_sec) {
		struct stat st;
		if (stat(path, &st) == 0 && st.st_size >= 0)
			return 0;
		usleep(200000); /* 200ms */
		elapsed++;
	}
	return -1;
}

int main(void)
{
	int srv, one = 1;
	struct sockaddr_in addr;

	mkdir(PROXY_DIR, 0755);
	unlink(REQ_FILE);
	unlink(RESP_FILE);
	unlink(GO_FILE);

	srv = socket(AF_INET, SOCK_STREAM, 0);
	if (srv < 0) {
		logmsg("socket failed");
		return 1;
	}
	setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one));

	memset(&addr, 0, sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = htonl(INADDR_ANY);
	addr.sin_port = htons(PORT);

	if (bind(srv, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
		logmsg("bind failed");
		return 1;
	}
	if (listen(srv, 4) < 0) {
		logmsg("listen failed");
		return 1;
	}
	logmsg("http_file_proxy listening on :3128");

	for (;;) {
		struct sockaddr_in cli;
		socklen_t clen = sizeof(cli);
		int cfd = accept(srv, (struct sockaddr *)&cli, &clen);
		if (cfd < 0) {
			if (errno == EINTR)
				continue;
			logmsg("accept failed");
			continue;
		}

		/* 1. read the full HTTP request */
		static char req[MAX_REQ];
		int req_len = 0;
		int header_end = -1;
		int content_len = 0;

		while (req_len < MAX_REQ - 1) {
			int r = read(cfd, req + req_len, MAX_REQ - 1 - req_len);
			if (r <= 0)
				break;
			req_len += r;
			req[req_len] = 0;

			/* find end of headers */
			if (header_end < 0) {
				char *p = strstr(req, "\r\n\r\n");
				if (p) {
					header_end = (p + 4) - req;
					/* parse Content-Length */
					char *cl = strcasestr(req, "Content-Length:");
					if (cl)
						content_len = atoi(cl + 15);
				}
			}
			/* done when we have headers + body */
			if (header_end > 0 && req_len >= header_end + content_len)
				break;
			/* done for simple GET (no body) */
			if (header_end > 0 && content_len == 0 &&
			    req_len > header_end)
				break;
			/* done if connection closed */
			if (r == 0)
				break;
		}
		req[req_len] = 0;

		/* 2. save request */
		FILE *f = fopen(REQ_FILE, "w");
		if (!f) {
			close(cfd);
			continue;
		}
		fwrite(req, 1, req_len, f);
		fclose(f);

		/* 3. trigger */
		int gfd = open(GO_FILE, O_CREAT | O_WRONLY, 0644);
		if (gfd >= 0)
			close(gfd);

		/* 4. wait for response (30s timeout) */
		if (wait_for_file(RESP_FILE, 150) < 0) {
			const char *err =
				"HTTP/1.0 504 Gateway Timeout\r\n"
				"Content-Type: text/plain\r\n"
				"Content-Length: 9\r\n"
				"\r\n"
				"timeout\n";
			write(cfd, err, strlen(err));
			unlink(GO_FILE);
			unlink(REQ_FILE);
			close(cfd);
			continue;
		}

		/* 5. send response */
		f = fopen(RESP_FILE, "r");
		if (f) {
			static char resp[MAX_RESP];
			int rlen = fread(resp, 1, MAX_RESP, f);
			fclose(f);
			if (rlen > 0)
				write(cfd, resp, rlen);
		}

		/* 6. cleanup */
		unlink(RESP_FILE);
		unlink(GO_FILE);
		unlink(REQ_FILE);
		close(cfd);
	}
	return 0;
}
