from __future__ import annotations
import re


def to_bullets_html(text: str, color: str = "#94a3b8") -> str:
    """Convert a paragraph into HTML bullet points split on sentence boundaries."""
    if not text:
        return ""
    # Split on sentence endings, or on explicit newlines
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    parts = [p.strip().rstrip(".") for p in parts if len(p.strip()) > 8]
    if not parts:
        return f'<span style="color:{color}">{text}</span>'
    if len(parts) == 1:
        return f'<span style="color:{color}">{parts[0]}</span>'
    items = "".join(
        f'<li style="margin-bottom:0.25rem;color:{color}">{p}</li>'
        for p in parts
    )
    return (
        f'<ul style="margin:0.3rem 0 0;padding-left:1.1rem;font-size:inherit;line-height:1.5">'
        f"{items}</ul>"
    )
