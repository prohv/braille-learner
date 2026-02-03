"""Braille mapping module.

Provides functions to map characters to Braille dot patterns and vice versa.
"""

import config


def get_braille_pattern(char):
    """Get the 6-dot Braille pattern for a character.

    Args:
        char: Single alphabetic character (a-z, case insensitive)

    Returns:
        List of 6 integers (0 or 1) representing dots 1-6, or None if invalid
    """
    char = char.lower()
    return config.BRAILLE_MAP.get(char, None)


def get_unicode_braille(char):
    """Get Unicode Braille character for a letter.

    Args:
        char: Single alphabetic character (a-z, case insensitive)

    Returns:
        Unicode Braille character, or None if invalid
    """
    char = char.lower()
    return config.UNICODE_BRAILLE.get(char, None)


def is_valid_character(char):
    """Check if a character is a valid single letter.

    Args:
        char: Character to validate

    Returns:
        True if char is a single alphabetic character
    """
    return len(char) == 1 and char.isalpha()


def format_pattern_binary(pattern):
    """Format a Braille pattern as a binary string.

    Args:
        pattern: List of 6 integers (0 or 1)

    Returns:
        Binary string representation (e.g., "110000" for 'a')
    """
    return "".join(["1" if p else "0" for p in pattern])


def get_dots_raised(pattern):
    """Get list of raised dot numbers from a pattern.

    Args:
        pattern: List of 6 integers (0 or 1)

    Returns:
        List of dot numbers (1-6) that are raised
    """
    return [i + 1 for i, dot in enumerate(pattern) if dot == 1]
