from __future__ import unicode_literals

import time

import RPi.GPIO as gpio
from django.core.management import BaseCommand

from play_pi.utils import mpd_client


class Command(BaseCommand):
    BCM_PLAY = 18
    BCM_NEXT = 17
    BCM_PREV = 22
    BCM_STOP = 27
    BCM_VOL_UP = 20
    BCM_VOL_DOWN = 21
    BCM_ALL = BCM_PLAY, BCM_NEXT, BCM_PREV, BCM_STOP, BCM_VOL_UP, BCM_VOL_DOWN

    def on_button_press(self, channel):
        with mpd_client() as client:
            if channel == self.BCM_PLAY:
                if client.status().get('state', '') == 'play':
                    client.pause()
                    print "Pause"
                else:
                    client.play()
                    print "Play"
            elif channel == self.BCM_NEXT:
                client.next()
                print "Next"
            elif channel == self.BCM_PREV:
                client.previous()
                print "Previous"
            elif channel == self.BCM_STOP:
                client.stop()
                print "Stopped"
            elif channel == self.BCM_VOL_UP:
                status = client.status()
                volume = int(status['volume']) + 5
                if volume > 100:
                    volume = 100
                client.setvol(volume)
                print "Volume set to {}".format(volume)
            elif channel == self.BCM_VOL_DOWN:
                status = client.status()
                volume = int(status['volume']) - 5
                if volume < 0:
                    volume = 0
                client.setvol(volume)
                print "Volume set to {}".format(volume)

    def handle(self, *args, **options):
        gpio.setmode(gpio.BCM)

        for channel in self.BCM_ALL:
            gpio.setup(channel, gpio.IN, pull_up_down=gpio.PUD_UP)
            gpio.add_event_detect(channel, gpio.FALLING, bouncetime=250, callback=self.on_button_press)

        print 'Running... Press CTRL+C to stop'
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print 'Finished'
        finally:
            gpio.cleanup()
