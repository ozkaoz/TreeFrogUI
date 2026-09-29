/* fb_clear — trigger the AVP display re-composition that clears the
 * blue overlay. Same technique as the video player / picoarch init:
 * re-apply the current video mode (FBIOPUT_VSCREENINFO) + a blank/unblank
 * cycle (FBIOBLANK). The AVP re-composites its layers and the overlay
 * film is dropped (empirically validated: "playing a video clears the
 * film" — the video path does exactly these ioctls).
 *
 * Build: mips-mti-linux-gnu-gcc -static -Os -s -o fb_clear fb_clear.c
 * Usage: fb_clear              (immediate)
 *        fb_clear <seconds>    (wait N seconds, then clear — for the
 *                              ~30s overlay trigger window)
 */
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/fb.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>

int main(int argc, char **argv)
{
	int fd;
	struct fb_var_screeninfo vinfo;
	int i;

	if (argc > 1) {
		int delay = atoi(argv[1]);
		if (delay > 0)
			sleep(delay);
	}

	fd = open("/dev/fb0", O_RDWR);
	if (fd < 0) {
		fprintf(stderr, "fb_clear: open /dev/fb0: %s\n",
			strerror(errno));
		return 1;
	}

	if (ioctl(fd, FBIOGET_VSCREENINFO, &vinfo) < 0) {
		fprintf(stderr, "fb_clear: FBIOGET: %s\n", strerror(errno));
		close(fd);
		return 1;
	}

	/* re-apply the SAME mode — forces the display driver to
	 * re-initialize the pipeline and notify the AVP */
	for (i = 0; i < 3; i++) {
		if (ioctl(fd, FBIOPUT_VSCREENINFO, &vinfo) < 0)
			fprintf(stderr, "fb_clear: FBIOPUT[%d]: %s\n", i,
				strerror(errno));
		usleep(50000);
	}

	/* blank + unblank — forces the compositor to redraw */
	ioctl(fd, FBIOBLANK, FB_BLANK_POWERDOWN);
	usleep(100000);
	ioctl(fd, FBIOBLANK, FB_BLANK_UNBLANK);
	usleep(100000);

	/* a second round for good measure */
	ioctl(fd, FBIOPUT_VSCREENINFO, &vinfo);
	ioctl(fd, FBIOBLANK, FB_BLANK_POWERDOWN);
	usleep(50000);
	ioctl(fd, FBIOBLANK, FB_BLANK_UNBLANK);

	close(fd);
	return 0;
}
