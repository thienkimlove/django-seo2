from __future__ import unicode_literals

import re

from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.contrib.contenttypes.models import ContentType

class NotSet(object):
    """A singleton to identify unset values (where None would have meaning)."""

    def __str__(self):
        return "NotSet"

    def __repr__(self):
        return self.__str__()


NotSet = NotSet()


class Literal(object):
    """Wrap literal values so that the system knows to treat them that way."""

    def __init__(self, value):
        self.value = value




def resolve_to_name(path, urlconf=None):
   pass


def _replace_quot(match):
    def unescape(v):
        return v.replace('&quot;', '"').replace('&amp;', '&')

    return '<%s%s>' % (unescape(match.group(1)), unescape(match.group(3)))


def escape_tags(value, valid_tags):
    """
    Strips text from the given html string, leaving only tags.
    This functionality requires BeautifulSoup, nothing will be
    done otherwise.

    This isn't perfect. Someone could put javascript in here:
        <a onClick="alert('hi');">test</a>

        So if you use valid_tags, you still need to trust your data entry.
        Or we could try:
          - only escape the non matching bits
          - use BeautifulSoup to understand the elements, escape everything
            else and remove potentially harmful attributes (onClick).
          - Remove this feature entirely. Half-escaping things securely is
            very difficult, developers should not be lured into a false
            sense of security.
    """
    # 1. escape everything
    value = conditional_escape(value)

    # 2. Reenable certain tags
    if valid_tags:
        # TODO: precompile somewhere once?
        tag_re = re.compile(r'&lt;(\s*/?\s*(%s))(.*?\s*)&gt;' %
                            '|'.join(re.escape(tag) for tag in valid_tags))
        value = tag_re.sub(_replace_quot, value)

    # Allow comments to be hidden
    value = value.replace("&lt;!--", "<!--").replace("--&gt;", "-->")

    return mark_safe(value)


def _get_seo_content_types(seo_models):
    """Returns a list of content types from the models defined in settings."""
    try:
        return [ContentType.objects.get_for_model(m).id for m in seo_models]
    except Exception:  # previously caught DatabaseError
        # Return an empty list if this is called too early
        return []


def get_seo_content_types(seo_models):
    return lazy(_get_seo_content_types, list)(seo_models)
