# coding=utf-8
from __future__ import unicode_literals, absolute_import

from django import template
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def play_button(item, css_classes='', label=''):
    """ Renders play button """
    if hasattr(item, 'html_id'):
        fragment = '#' + item.html_id
    else:
        fragment = ''
    if label:
        label = ' ' + label
    return format_html(
        "<a href='#' class='btn-play {css_classes}' onclick='{play_function_name}([{item_id}])'>▶{label}</a>",
        url=reverse('play', args=(item.type_name(), item.id)),
        fragment=fragment,
        css_classes=css_classes,
        label=label,
        item_id=item.id,
        play_function_name='playTracks' if item.type_name() == 'track' else 'playRadios',
    )
