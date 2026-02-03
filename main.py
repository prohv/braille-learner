import argparse
import signal
import sys
import config

from modules.speech_recognizer import SpeechRecognizer
from modules.braille_mapper import BrailleMapper
from modules.tts_feedback import TTSFeedback
from modules.servo_controller import ServoController


class BrailleLearner:
    def __init__(self, simulate=False, verbose=False):
        config.SIMULATION_MODE = simulate
        config.VERBOSE_MODE = verbose

        self.speech_recognizer = None
        self.braille_mapper = BrailleMapper()
        self.tts = None
        self.servo_controller = None
        self.running = False

        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        print("\n\nShutting down gracefully...")
        self.running = False

    def initialize(self):
        try:
            self.speech_recognizer = SpeechRecognizer()
            self.tts = TTSFeedback()
            self.servo_controller = ServoController()

            self._print_welcome()
            self.running = True

        except Exception as e:
            print(f"Failed to initialize: {e}")
            print("\nPlease make sure the Vosk model is installed:")
            print("python download_model.py")
            sys.exit(1)

    def _print_welcome(self):
        print("\nVoice-Controlled Braille Learning Device")
        print("=" * 42)
        print(f"Mode: {'SIMULATION' if config.SIMULATION_MODE else 'HARDWARE'}")
        print(f"Verbose: {'ON' if config.VERBOSE_MODE else 'OFF'}")
        print("\nInstructions:")
        print("- Speak a letter A-Z to see the Braille pattern")
        print("- Say 'exit' to quit")
        print("- Press Ctrl+C to quit\n")

    def run(self):
        while self.running:
            try:
                result = self.speech_recognizer.listen()

                if result == "exit":
                    print("\nExiting...")
                    self.tts.speak_exit()
                    break

                if result is None:
                    self.tts.speak_error_unrecognized()
                    print("I didn't understand, please try again\n")
                    continue

                if not self.braille_mapper.is_valid_character(result):
                    self.tts.speak_error_invalid()
                    print("Please say a letter from A to Z\n")
                    continue

                self._process_character(result)

            except Exception as e:
                print(f"Error: {e}\n")
                continue

    def _process_character(self, char):
        pattern = self.braille_mapper.get_braille_pattern(char)
        unicode_braille = self.braille_mapper.get_unicode_braille(char)
        grid = self.braille_mapper.display_braille_grid(pattern)
        pattern_str = self.braille_mapper.format_braille_pattern(pattern)
        dots_raised = self.braille_mapper.get_dots_raised(pattern)

        print(f"\nRecognized: {char.upper()}")
        print(f"Braille: {unicode_braille} [{pattern_str}]\n")
        print("Braille Grid:")
        print(grid)
        print(f"\nDots raised: {dots_raised}")

        self.servo_controller.display_braille(pattern, char)

        self.tts.speak_letter(char)
        print(f"Voice feedback: Letter {char.upper()}")
        print(f"Displaying for {config.DISPLAY_DURATION} seconds...")
        print("\nResetting for next input...\n")

    def cleanup(self):
        if self.speech_recognizer:
            self.speech_recognizer.cleanup()
        if self.tts:
            self.tts.cleanup()
        if self.servo_controller:
            self.servo_controller.cleanup()
        print("Goodbye!")


def main():
    parser = argparse.ArgumentParser(
        description="Voice-Controlled Braille Learning Device"
    )
    parser.add_argument(
        "--simulate", action="store_true", help="Run in simulation mode (no hardware)"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    learner = BrailleLearner(simulate=args.simulate, verbose=args.verbose)

    try:
        learner.initialize()
        learner.run()
    finally:
        learner.cleanup()


if __name__ == "__main__":
    main()
