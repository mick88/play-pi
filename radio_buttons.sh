#! /bin/sh
### BEGIN INIT INFO
# Provides:          PlayPi hardware button controls
# Required-Start:    $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Handles presses on playback buttons connected to GPIO pins.
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/bin

. /lib/init/vars.sh
. /lib/lsb/init-functions

case "$1" in
  start)
    log_begin_msg "Starting play-pi hardware interface"
    cd /home/pi/src/play-pi
    source bin/activate
    python manage.py gpio_buttons
    log_end_msg $?
    exit 0
    ;;
  stop)
    log_begin_msg "Stopping play-pi hardware interface"

    log_end_msg $?
    exit 0
    ;;
  *)
    echo "Usage: /etc/init.d/radio_buttons.sh {start|stop}"
    exit 1
    ;;
esac