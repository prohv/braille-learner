"""Intent parsing for letter recognition.

Maps recognized phrases (from Vosk) to canonical intents.
Handles letter name variants and optional "letter" prefix.
"""

from enum import Enum, auto


class IntentType(Enum):
    """Types of recognized intents."""

    LETTER = auto()
    EXIT = auto()
    UNKNOWN = auto()


class Intent:
    """Represents a parsed user intent."""

    def __init__(self, intent_type: IntentType, value: str = ""):
        self.type = intent_type
        self.value = value  # 'a'..'z' for LETTER, empty for others

    def __repr__(self):
        if self.type == IntentType.LETTER:
            return f"Intent(LETTER, '{self.value}')"
        return f"Intent({self.type.name})"

    def __eq__(self, other):
        if not isinstance(other, Intent):
            return False
        return self.type == other.type and self.value == other.value


# Mapping of acceptable phrases to canonical letters
# Supports multiple variants for each letter (e.g., "bee", "be" both → "b")
LETTER_PHRASES = {
    # A
    "a": "a", "ay": "a", "hey": "a", "hay": "a", "eh": "a", "day": "a",
    # B
    "b": "b", "bee": "b", "be": "b", "me": "b", "we": "b",
    # C
    "c": "c", "cee": "c", "see": "c", "sea": "c", "she": "c",
    # D
    "d": "d", "dee": "d", "the": "d", "they": "d", "there": "d",
    # E
    "e": "e", "ee": "e", "he": "e",
    # F
    "f": "f", "ef": "f", "if": "f", "off": "f", "half": "f",
    # G
    "g": "g", "gee": "g", "jee": "g",
    # H
    "h": "h", "aitch": "h", "age": "h", "eight": "h",
    # I
    "i": "i", "eye": "i", "hi": "i", "high": "i",
    # J
    "j": "j", "jay": "j",
    # K
    "k": "k", "kay": "k", "okay": "k", "gay": "k",
    # L
    "l": "l", "el": "l", "hell": "l", "all": "l", "ill": "l",
    # M
    "m": "m", "em": "m", "am": "m", "um": "m", "them": "m",
    # N
    "n": "n", "en": "n", "an": "n", "in": "n", "and": "n", "end": "n",
    # O
    "o": "o", "oh": "o", "zero": "o", "owe": "o",
    # P
    "p": "p", "pee": "p", "pe": "p",
    # Q
    "q": "q", "cue": "q", "queue": "q",
    # R
    "r": "r", "are": "r", "or": "r", "our": "r", "hour": "r",
    # S
    "s": "s", "ess": "s", "yes": "s", "is": "s", "as": "s",
    # T
    "t": "t", "tee": "t", "tea": "t", "to": "t", "two": "t", "tree": "t",
    # U
    "u": "u", "you": "u", "hue": "u", "who": "u",
    # V
    "v": "v", "vee": "v",
    # W
    "w": "w", "double u": "w", "double you": "w",
    # X
    "x": "x", "ex": "x", "axe": "x", "acts": "x",
    # Y
    "y": "y", "why": "y", "while": "y", "wa": "y",
    # Z
    "z": "z", "zee": "z", "zed": "z", "ze": "z"
}

# Commands
EXIT_PHRASES = {"exit", "quit", "stop"}


def parse_intent(phrase: str) -> Intent:
    """
    Parse a recognized phrase into an intent.

    Handles:
    - Direct letter names: "a", "bee", "cee", "double u"
    - Prefixed letters: "letter a", "letter bee", "letter double u"
    - Commands: "exit", "quit", "stop"

    Args:
        phrase: The recognized text from speech recognition

    Returns:
        Intent object representing the parsed intent

    Examples:
        >>> parse_intent("a")
        Intent(LETTER, 'a')
        >>> parse_intent("bee")
        Intent(LETTER, 'b')
        >>> parse_intent("letter cee")
        Intent(LETTER, 'c')
        >>> parse_intent("double u")
        Intent(LETTER, 'w')
        >>> parse_intent("exit")
        Intent(EXIT)
        >>> parse_intent("hello world")
        Intent(UNKNOWN)
    """
    if not phrase:
        return Intent(IntentType.UNKNOWN)

    # Normalize: lowercase, strip whitespace and '[unk]' tags
    normalized = phrase.lower().replace("[unk]", "").strip()

    # If the phrase became empty after removing [unk], it's unknown
    if not normalized:
        return Intent(IntentType.UNKNOWN)

    # Check for "letter " prefix
    if normalized.startswith("letter "):
        # Remove prefix and parse the rest
        rest = normalized[7:].strip()  # 7 = len("letter ")
        if rest in LETTER_PHRASES:
            return Intent(IntentType.LETTER, LETTER_PHRASES[rest])

    # Check if it's a direct letter phrase
    if normalized in LETTER_PHRASES:
        return Intent(IntentType.LETTER, LETTER_PHRASES[normalized])

    # Check if it's an exit command
    if normalized in EXIT_PHRASES:
        return Intent(IntentType.EXIT)

    # Unknown phrase
    return Intent(IntentType.UNKNOWN)


def get_all_letter_phrases() -> set:
    """
    Get all acceptable letter phrases (for building Vosk grammar).

    Returns:
        Set of all phrases that should be recognized
    """
    phrases = set(LETTER_PHRASES.keys())

    # Add prefixed versions
    prefixed = {f"letter {phrase}" for phrase in phrases}
    phrases.update(prefixed)

    return phrases


def get_exit_phrases() -> set:
    """Get exit command phrases."""
    return set(EXIT_PHRASES)


def build_vosk_grammar() -> list:
    """
    Build the complete grammar list for Vosk.

    Returns:
        List of all acceptable phrases for Vosk grammar constraint
    """
    grammar = []

    # Add all letter phrases (direct and prefixed)
    for phrase in LETTER_PHRASES.keys():
        grammar.append(phrase)
        grammar.append(f"letter {phrase}")

    # Add exit commands
    grammar.extend(EXIT_PHRASES)

    return grammar
