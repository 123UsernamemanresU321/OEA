import re

import markdown2
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def _convert_latex_lists(text: str) -> str:
    """Convert basic LaTeX list environments into markdown lists so they render."""

    def replace_env(env: str, marker: str, value: str) -> str:
        pattern = re.compile(rf"\\begin{{{env}}}(.*?)\\end{{{env}}}", re.S)

        def _replace(match: re.Match) -> str:
            body = match.group(1) or ""
            items = [chunk.strip() for chunk in re.split(r"\\item", body) if chunk.strip()]
            if not items:
                return ""
            return "\n".join(f"{marker} {item}" for item in items)

        return pattern.sub(_replace, value)

    converted = replace_env("itemize", "-", text)
    converted = replace_env("enumerate", "1.", converted)
    return converted


@register.filter
def markdownify(text):
    if not text:
        return ""
    normalized = _convert_latex_lists(text)
    return mark_safe(
        markdown2.markdown(
            normalized,
            extras={
                "fenced-code-blocks": True,
                "strike": True,
                "break-on-newline": True,
            },
        )
    )


@register.filter
def get_item(mapping, key):
    try:
        return mapping.get(key)
    except AttributeError:
        return None
