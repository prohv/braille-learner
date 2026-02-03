"""Text-to-speech feedback module using pyttsx3.

Provides audio confirmation for recognized letters and commands.
Best-effort implementation - gracefully degrades if pyttsx3 or audio backend is unavailable.
"""

import config


class TTSFeedback:
    """Text-to-speech feedback handler.

    Wraps pyttsx3 to provide audio confirmations. If TTS is unavailable,
    the class silently continues without audio feedback.
    """

    def __init__(self):
        self.engine = None
        self.enabled = False
        self._initialize()

    def _initialize(self):
        """Initialize the TTS engine."""
        try:
            import pyttsx3

            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 150)
            self.engine.setProperty("volume", 0.9)
            self.enabled = True
            if config.VERBOSE_MODE:
                print("[VERBOSE] TTS initialized successfully")
        except Exception as e:
            print(f"Failed to initialize TTS: {e}")
            print("TTS disabled. Install alsa-utils for audio playback:")
            print("  sudo apt install alsa-utils")
            self.enabled = False

    def speak_letter(self, char):
        """Speak a letter confirmation.

        Args:
            char: Single character (a-z) to speak
        """
        if not self.enabled:
            return
        message = f"Letter {char.upper()}"
        self._speak(message)

    def speak_exit(self):
        """Speak goodbye message."""
        if not self.enabled:
            return
        self._speak("Goodbye!")

    def speak_error_unrecognized(self):
        """Speak error for unrecognized speech."""
        if not self.enabled:
            return
        self._speak("I didn't understand, please try again")

    def speak_error_invalid(self):
        """Speak error for invalid character."""
        if not self.enabled:
            return
        self._speak("Please say a letter from A to Z")

    def _speak(self, message):
        """Internal speak method.

        Args:
            message: Text to speak
        """
        try:
            if config.VERBOSE_MODE:
                print(f"[VERBOSE] Speaking: {message}")
            self.engine.say(message)
            self.engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")

    def cleanup(self):
        """Clean up TTS engine resources."""
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass
