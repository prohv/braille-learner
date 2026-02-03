"""Tests for the intent parser module."""

import unittest
from speech.intent import (
    Intent,
    IntentType,
    parse_intent,
    LETTER_PHRASES,
    get_all_letter_phrases,
    get_exit_phrases,
    build_vosk_grammar,
)


class TestIntentParser(unittest.TestCase):
    """Test cases for intent parsing."""

    def test_direct_single_letters(self):
        """Test direct single-letter inputs."""
        for letter in "abcdefghijklmnopqrstuvwxyz":
            with self.subTest(letter=letter):
                intent = parse_intent(letter)
                self.assertEqual(intent.type, IntentType.LETTER)
                self.assertEqual(intent.value, letter)

    def test_common_variants(self):
        """Test common letter name variants."""
        test_cases = [
            ("bee", "b"),
            ("be", "b"),
            ("cee", "c"),
            ("see", "c"),
            ("sea", "c"),
            ("dee", "d"),
            ("gee", "g"),
            ("aitch", "h"),
            ("eye", "i"),
            ("jay", "j"),
            ("kay", "k"),
            ("el", "l"),
            ("em", "m"),
            ("en", "n"),
            ("oh", "o"),
            ("pee", "p"),
            ("cue", "q"),
            ("queue", "q"),
            ("are", "r"),
            ("ess", "s"),
            ("tee", "t"),
            ("tea", "t"),
            ("you", "u"),
            ("vee", "v"),
            ("double u", "w"),
            ("double you", "w"),
            ("ex", "x"),
            ("why", "y"),
            ("zee", "z"),
            ("zed", "z"),
        ]

        for phrase, expected_letter in test_cases:
            with self.subTest(phrase=phrase):
                intent = parse_intent(phrase)
                self.assertEqual(intent.type, IntentType.LETTER)
                self.assertEqual(intent.value, expected_letter)

    def test_prefixed_letters(self):
        """Test 'letter X' prefix forms."""
        test_cases = [
            ("letter a", "a"),
            ("letter bee", "b"),
            ("letter cee", "c"),
            ("letter double u", "w"),
            ("letter zee", "z"),
        ]

        for phrase, expected_letter in test_cases:
            with self.subTest(phrase=phrase):
                intent = parse_intent(phrase)
                self.assertEqual(intent.type, IntentType.LETTER)
                self.assertEqual(intent.value, expected_letter)

    def test_exit_commands(self):
        """Test exit command recognition."""
        for phrase in ["exit", "quit", "stop"]:
            with self.subTest(phrase=phrase):
                intent = parse_intent(phrase)
                self.assertEqual(intent.type, IntentType.EXIT)
                self.assertEqual(intent.value, "")

    def test_unknown_phrases(self):
        """Test that unknown phrases return UNKNOWN intent."""
        unknown_phrases = [
            "hello",
            "world",
            "braille",
            "learning",
            "device",
            "the quick brown fox",
            "123",
            "",
        ]

        for phrase in unknown_phrases:
            with self.subTest(phrase=phrase):
                intent = parse_intent(phrase)
                self.assertEqual(intent.type, IntentType.UNKNOWN)

    def test_case_insensitive(self):
        """Test that parsing is case-insensitive."""
        test_cases = [
            ("BEE", "b"),
            ("Letter A", "a"),
            ("EXIT", None),  # EXIT has no value field
            ("Double U", "w"),
        ]

        for phrase, expected in test_cases:
            with self.subTest(phrase=phrase):
                intent = parse_intent(phrase)
                if expected:
                    self.assertEqual(intent.value, expected)

    def test_whitespace_handling(self):
        """Test that extra whitespace is handled."""
        test_cases = [
            ("  a  ", "a"),
            (" letter b ", "b"),
            ("  exit  ", None),  # EXIT type check
        ]

        for phrase, expected in test_cases:
            with self.subTest(phrase=phrase):
                intent = parse_intent(phrase)
                if expected:
                    self.assertEqual(intent.value, expected)
                else:
                    self.assertEqual(intent.type, IntentType.EXIT)


class TestGrammarBuilding(unittest.TestCase):
    """Test cases for grammar building functions."""

    def test_get_all_letter_phrases(self):
        """Test that all letter phrases are returned."""
        phrases = get_all_letter_phrases()

        # Should include direct forms
        self.assertIn("a", phrases)
        self.assertIn("bee", phrases)
        self.assertIn("double u", phrases)

        # Should include prefixed forms
        self.assertIn("letter a", phrases)
        self.assertIn("letter bee", phrases)
        self.assertIn("letter double u", phrases)

    def test_get_exit_phrases(self):
        """Test exit phrases."""
        phrases = get_exit_phrases()
        self.assertIn("exit", phrases)
        self.assertIn("quit", phrases)
        self.assertIn("stop", phrases)

    def test_build_vosk_grammar(self):
        """Test complete grammar building."""
        grammar = build_vosk_grammar()

        # Should be a list
        self.assertIsInstance(grammar, list)

        # Should include letters
        self.assertIn("a", grammar)
        self.assertIn("bee", grammar)
        self.assertIn("letter a", grammar)

        # Should include exit
        self.assertIn("exit", grammar)


class TestIntentEquality(unittest.TestCase):
    """Test Intent object equality."""

    def test_equal_intents(self):
        """Test that equal intents compare equal."""
        intent1 = Intent(IntentType.LETTER, "a")
        intent2 = Intent(IntentType.LETTER, "a")
        self.assertEqual(intent1, intent2)

    def test_different_types(self):
        """Test that different types are not equal."""
        intent1 = Intent(IntentType.LETTER, "a")
        intent2 = Intent(IntentType.EXIT)
        self.assertNotEqual(intent1, intent2)

    def test_different_values(self):
        """Test that different values are not equal."""
        intent1 = Intent(IntentType.LETTER, "a")
        intent2 = Intent(IntentType.LETTER, "b")
        self.assertNotEqual(intent1, intent2)


if __name__ == "__main__":
    unittest.main()
