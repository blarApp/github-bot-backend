import json

from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

from .models import Integration, Repos


class CommonAdmin(admin.ModelAdmin):
    def metadata_view(self, obj):
        if obj.metadata is not None:
            response = json.dumps(obj.metadata, sort_keys=True, indent=2)
            formatter = HtmlFormatter(style="colorful")
            response = highlight(response, JsonLexer(), formatter)
            style = "<style>" + formatter.get_style_defs() + "</style><br>"
            return mark_safe(style + response)
        return ""



admin.site.register(Integration)
admin.site.register(Repos)