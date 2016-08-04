from __future__ import unicode_literals

from django.db import models
from django.utils.safestring import mark_safe


def get_action_choices():
    """
    Generate choices for action field based on methods in the gpio_buttons command
    Returns:

    """
    from hardware.management.commands.gpio_buttons import Command
    import re
    pattern = re.compile(r'^on_(?P<name>\w+)_press$')
    choices = []
    for member in dir(Command):
        match = pattern.match(member)
        if match:
            action = match.groupdict()['name']
            name = action.replace('_', ' ').title()
            choices.append((action, name))
    return choices


class GpioButton(models.Model):
    bcm_pin = models.PositiveSmallIntegerField(help_text=mark_safe('Pin number in <a href="https://pinout.xyz/" target="_blank">BCM numbering</a>.'))
    action = models.CharField(max_length=32, choices=get_action_choices())
    enable = models.BooleanField(blank=True, help_text='Enable this button/pin', default=True)
