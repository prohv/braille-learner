"""Tests for Braille rendering functions."""

import unittest
from braille import (
    render_ascii_grid,
    render_unicode_grid,
    format_pattern_binary,
    get_dots_raised,
    DOT_RAISED_ASCII,
    DOT_LOWERED_ASCII,
)


class TestRenderAsciiGrid(unittest.TestCase):
    """Test cases for ASCII grid rendering."""

    def test_letter_a(self):
        """Test letter A (only dot 1 raised)."""
        pattern = [1, 0, 0, 0, 0, 0]
        expected = "O .\n. .\n. ."
        self.assertEqual(render_ascii_grid(pattern), expected)

    def test_letter_b(self):
        """Test letter B (dots 1 and 2 raised)."""
        pattern = [1, 1, 0, 0, 0, 0]
        expected = "O .\nO .\n. ."
        self.assertEqual(render_ascii_grid(pattern), expected)

    def test_letter_c(self):
        """Test letter C (dots 1 and 4 raised)."""
        pattern = [1, 0, 0, 1, 0, 0]
        expected = "O O\n. .\n. ."
        self.assertEqual(render_ascii_grid(pattern), expected)

    def test_all_raised(self):
        """Test all dots raised."""
        pattern = [1, 1, 1, 1, 1, 1]
        expected = "O O\nO O\nO O"
        self.assertEqual(render_ascii_grid(pattern), expected)

    def test_all_lowered(self):
        """Test all dots lowered."""
        pattern = [0, 0, 0, 0, 0, 0]
        expected = ". .\n. .\n. ."
        self.assertEqual(render_ascii_grid(pattern), expected)

    def test_invalid_pattern_length(self):
        """Test that invalid pattern length raises error."""
        with self.assertRaises(ValueError):
            render_ascii_grid([1, 0, 0])  # Too short

        with self.assertRaises(ValueError):
            render_ascii_grid([1, 0, 0, 0, 0, 0, 0])  # Too long


class TestFormatPatternBinary(unittest.TestCase):
    """Test cases for binary pattern formatting."""

    def test_letter_a(self):
        """Test letter A binary format."""
        pattern = [1, 0, 0, 0, 0, 0]
        self.assertEqual(format_pattern_binary(pattern), "100000")

    def test_all_ones(self):
        """Test all dots raised."""
        pattern = [1, 1, 1, 1, 1, 1]
        self.assertEqual(format_pattern_binary(pattern), "111111")

    def test_all_zeros(self):
        """Test all dots lowered."""
        pattern = [0, 0, 0, 0, 0, 0]
        self.assertEqual(format_pattern_binary(pattern), "000000")


class TestGetDotsRaised(unittest.TestCase):
    """Test cases for getting raised dot numbers."""

    def test_letter_a(self):
        """Test letter A returns [1]."""
        pattern = [1, 0, 0, 0, 0, 0]
        self.assertEqual(get_dots_raised(pattern), [1])

    def test_letter_b(self):
        """Test letter B returns [1, 2]."""
        pattern = [1, 1, 0, 0, 0, 0]
        self.assertEqual(get_dots_raised(pattern), [1, 2])

    def test_all_raised(self):
        """Test all dots raised returns [1, 2, 3, 4, 5, 6]."""
        pattern = [1, 1, 1, 1, 1, 1]
        self.assertEqual(get_dots_raised(pattern), [1, 2, 3, 4, 5, 6])

    def test_none_raised(self):
        """Test no dots raised returns empty list."""
        pattern = [0, 0, 0, 0, 0, 0]
        self.assertEqual(get_dots_raised(pattern), [])


class TestAsciiConstants(unittest.TestCase):
    """Test that ASCII constants are correct."""

    def test_dot_characters(self):
        """Test raised and lowered characters."""
        self.assertEqual(DOT_RAISED_ASCII, "O")
        self.assertEqual(DOT_LOWERED_ASCII, ".")


if __name__ == "__main__":
    unittest.main()
