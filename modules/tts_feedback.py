import pyttsx3
import config


class TTSFeedback:
    def __init__(self):
        self.engine = None
        self.enabled = False
        self._initialize()

    def _initialize(self):
        try:
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
        if not self.enabled:
            return
        message = f"Letter {char.upper()}"
        self._speak(message)

    def speak_exit(self):
        if not self.enabled:
            return
        self._speak("Goodbye!")

    def speak_error_unrecognized(self):
        if not self.enabled:
            return
        self._speak("I didn't understand, please try again")

    def speak_error_invalid(self):
        if not self.enabled:
            return
        self._speak("Please say a letter from A to Z")

    def _speak(self, message):
        try:
            if config.VERBOSE_MODE:
                print(f"[VERBOSE] Speaking: {message}")
            self.engine.say(message)
            self.engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")

    def cleanup(self):
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
