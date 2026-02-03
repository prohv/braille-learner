import unittest
from modules.braille_mapper import BrailleMapper


class TestBrailleMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = BrailleMapper()

    def test_get_braille_pattern(self):
        self.assertEqual(self.mapper.get_braille_pattern("a"), [1, 0, 0, 0, 0, 0])
        self.assertEqual(self.mapper.get_braille_pattern("b"), [1, 1, 0, 0, 0, 0])
        self.assertEqual(self.mapper.get_braille_pattern("z"), [1, 0, 1, 1, 1, 1])
        self.assertIsNone(self.mapper.get_braille_pattern("1"))
        self.assertIsNone(self.mapper.get_braille_pattern("ab"))

    def test_get_unicode_braille(self):
        self.assertEqual(self.mapper.get_unicode_braille("a"), "\u2801")
        self.assertEqual(self.mapper.get_unicode_braille("z"), "\u2836")
        self.assertIsNone(self.mapper.get_unicode_braille("1"))

    def test_is_valid_character(self):
        self.assertTrue(self.mapper.is_valid_character("a"))
        self.assertTrue(self.mapper.is_valid_character("Z"))
        self.assertFalse(self.mapper.is_valid_character("1"))
        self.assertFalse(self.mapper.is_valid_character("ab"))
        self.assertFalse(self.mapper.is_valid_character(""))

    def test_format_braille_pattern(self):
        self.assertEqual(
            self.mapper.format_braille_pattern([1, 0, 0, 0, 0, 0]), "100000"
        )
        self.assertEqual(
            self.mapper.format_braille_pattern([1, 1, 0, 1, 1, 1]), "110111"
        )

    def test_display_braille_grid(self):
        grid_a = self.mapper.display_braille_grid([1, 0, 0, 0, 0, 0])
        self.assertEqual(grid_a, "● ○\n○ ○\n○ ○")

        grid_b = self.mapper.display_braille_grid([1, 1, 0, 0, 0, 0])
        self.assertEqual(grid_b, "● ○\n● ○\n○ ○")

    def test_get_dots_raised(self):
        self.assertEqual(self.mapper.get_dots_raised([1, 0, 0, 0, 0, 0]), [1])
        self.assertEqual(self.mapper.get_dots_raised([1, 1, 0, 0, 0, 0]), [1, 2])
        self.assertEqual(
            self.mapper.get_dots_raised([1, 0, 1, 1, 1, 1]), [1, 3, 4, 5, 6]
        )
        self.assertEqual(self.mapper.get_dots_raised([0, 0, 0, 0, 0, 0]), [])


if __name__ == "__main__":
    unittest.main()
