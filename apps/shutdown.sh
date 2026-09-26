#!/bin/sh
# Power off via GPIO (powergpio writes to /dev/mem)
# NOTE: use regular call, NOT exec — exec breaks the shutdown chain
sync
/mnt/sdcard/treefrog/powergpio
exit $?
