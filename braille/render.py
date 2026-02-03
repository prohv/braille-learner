"""Braille display rendering utilities.

Provides both ASCII and Unicode (legacy) rendering options.
Default is ASCII for maximum compatibility.
"""

from typing import List


# ASCII characters for Braille dots
DOT_RAISED_ASCII = "O"
DOT_LOWERED_ASCII = "."

# Unicode characters (legacy, not recommended)
DOT_RAISED_UNICODE = "\u25cf"  # ●
DOT_LOWERED_UNICODE = "\u25cb"  # ○


def render_ascii_grid(pattern: List[int]) -> str:
    """
    Render a Braille pattern as ASCII art using O and . characters.

    Args:
        pattern: List of 6 integers (0 or 1), representing dots 1-6:
                1 o o 4
                2 o o 5
                3 o o 6

    Returns:
        Multi-line string with ASCII grid representation.

    Example:
        >>> render_ascii_grid([1, 0, 0, 0, 0, 0])  # Letter A
        'O .\n. .\n. .'

        >>> render_ascii_grid([1, 1, 0, 0, 0, 0])  # Letter B
        'O .\nO .\n. .'
    """
    if len(pattern) != 6:
        raise ValueError(f"Pattern must have exactly 6 elements, got {len(pattern)}")

    # Map pattern to characters
    chars = [DOT_RAISED_ASCII if p else DOT_LOWERED_ASCII for p in pattern]

    # Layout: 1 4
    #         2 5
    #         3 6
    lines = [
        f"{chars[0]} {chars[3]}",  # Top row: dot 1, dot 4
        f"{chars[1]} {chars[4]}",  # Middle row: dot 2, dot 5
        f"{chars[2]} {chars[5]}",  # Bottom row: dot 3, dot 6
    ]

    return "\n".join(lines)


def render_unicode_grid(pattern: List[int]) -> str:
    """
    Render a Braille pattern using Unicode filled/empty circles.

    Args:
        pattern: List of 6 integers (0 or 1)

    Returns:
        Multi-line string with Unicode grid representation.

    Note:
        Not recommended for terminal compatibility. Use render_ascii_grid instead.
    """
    if len(pattern) != 6:
        raise ValueError(f"Pattern must have exactly 6 elements, got {len(pattern)}")

    chars = [DOT_RAISED_UNICODE if p else DOT_LOWERED_UNICODE for p in pattern]

    lines = [
        f"{chars[0]} {chars[3]}",
        f"{chars[1]} {chars[4]}",
        f"{chars[2]} {chars[5]}",
    ]

    return "\n".join(lines)


def format_pattern_binary(pattern: List[int]) -> str:
    """
    Format a Braille pattern as a binary string.

    Args:
        pattern: List of 6 integers (0 or 1)

    Returns:
        Binary string like "100000" for letter A.
    """
    if len(pattern) != 6:
        raise ValueError(f"Pattern must have exactly 6 elements, got {len(pattern)}")

    return "".join("1" if p else "0" for p in pattern)


def get_dots_raised(pattern: List[int]) -> List[int]:
    """
    Get list of raised dot numbers (1-indexed).

    Args:
        pattern: List of 6 integers (0 or 1)

    Returns:
        List of raised dot numbers (1-6).

    Example:
        >>> get_dots_raised([1, 0, 0, 0, 0, 0])
        [1]

        >>> get_dots_raised([1, 1, 0, 0, 0, 0])
        [1, 2]
    """
    if len(pattern) != 6:
        raise ValueError(f"Pattern must have exactly 6 elements, got {len(pattern)}")

    return [i + 1 for i, p in enumerate(pattern) if p == 1]


def print_braille_output(char: str, pattern: List[int], use_ascii: bool = True) -> None:
    """
    Print complete Braille character output including grid and metadata.

    Args:
        char: The character (e.g., 'a')
        pattern: 6-element pattern list
        use_ascii: If True, use ASCII (O/.), else Unicode (●/○)
    """
    print(f"\nRecognized: {char.upper()}")

    if use_ascii:
        grid = render_ascii_grid(pattern)
        print("\nBraille Grid:")
        print(grid)
    else:
        grid = render_unicode_grid(pattern)
        binary = format_pattern_binary(pattern)
        print(f"\nBraille: {grid} [{binary}]")

    dots = get_dots_raised(pattern)
    print(f"\nDots raised: {dots}")
