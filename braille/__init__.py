"""Braille rendering and mapping utilities.

Provides functions for rendering Braille patterns in ASCII and binary formats.
"""

from .render import (
    render_ascii_grid,
    render_unicode_grid,
    format_pattern_binary,
    get_dots_raised,
    DOT_RAISED_ASCII,
    DOT_LOWERED_ASCII,
    print_braille_output,
)

__all__ = [
    "render_ascii_grid",
    "render_unicode_grid",
    "format_pattern_binary",
    "get_dots_raised",
    "DOT_RAISED_ASCII",
    "DOT_LOWERED_ASCII",
    "print_braille_output",
]
