from __future__ import unicode_literals
from django import template
from django.utils.html import format_html

from play_pi.models import Track

register = template.Library()

rating_glyphs = {
    Track.RATING_THUMBS_UP: 'glyphicon-thumbs-up',
    Track.RATING_THUMBS_DOWN: 'glyphicon-thumbs-down',
}


@register.filter
def track_rating_thumb(track_or_rating):
    """
    Renders glyphicon with rating
    Args:
        track_or_rating: tracks instance or rating value (0-5)

    Returns:
        escaped <span> tag
    """
    rating = track_or_rating.rating if isinstance(track_or_rating, Track) else track_or_rating
    if rating in rating_glyphs:
        return format_html(
            '<span class="glyphicon {} rating-glyph rating-{}"></span>',
            rating_glyphs[rating],
            rating,
        )
    else:
        return ''
