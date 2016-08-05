from __future__ import unicode_literals

import time

from django.core.management import BaseCommand

from play_pi.utils import mpd_client


class Command(BaseCommand):
    def on_play_press(self, client):
        if client.status().get('state', '') == 'play':
            client.pause()
            self.stdout.write("Pause")
        else:
            client.play()
            self.stdout.write("Play")

    def on_next_press(self, client):
        client.next()
        self.stdout.write("Next")

    def on_previous_press(self, client):
        client.previous()
        self.stdout.write("Previous")

    def on_stop_press(self, client):
        client.stop()
        self.stdout.write("Stopped")

    def on_volume_up_press(self, client):
        status = client.status()
        volume = int(status['volume']) + 5
        if volume > 100:
            volume = 100
        client.setvol(volume)
        self.stdout.write("Volume set to {}".format(volume))

    def on_volume_down_press(self, client):
        status = client.status()
        volume = int(status['volume']) - 5
        if volume < 0:
            volume = 0
        client.setvol(volume)
        self.stdout.write("Volume set to {}".format(volume))

    def setup(self):
        import RPi.GPIO as gpio
        from hardware.models import GpioButton
        gpio.setmode(gpio.BCM)

        buttons = list(GpioButton.objects.filter(enable=True))
        actions = {button.bcm_pin: getattr(self, 'on_{}_press'.format(button.action)) for button in buttons}

        def on_press(channel):
            with mpd_client() as client:
                actions[channel](client)

        for button in buttons:
            gpio.setup(button.bcm_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
            gpio.add_event_detect(button.bcm_pin, gpio.FALLING, bouncetime=250, callback=on_press)
            self.stdout.write('Setup {} button on BCM {}'.format(button.get_action_display(), button.bcm_pin))

        if not buttons:
            self.stderr.write('There are no buttons setup. Did you forget to enable buttons in admin?')

    def cleanup(self):
        import RPi.GPIO as gpio
        gpio.cleanup()

    def handle(self, *args, **options):
        from hardware.models import GpioButton
        try:
            self.setup()
            self.stdout.write('Running... Press CTRL+C to stop')
            buttons = None
            while True:
                new_buttons = set(GpioButton.objects.filter(enable=True).values_list('bcm_pin', 'action'))
                if new_buttons != buttons:
                    buttons = new_buttons
                    self.stdout.write('Change detected in button configuration. Reloading...')
                    self.cleanup()
                    self.setup()
                time.sleep(10)
        except KeyboardInterrupt:
            self.stdout.write('Finished')
        finally:
            self.cleanup()