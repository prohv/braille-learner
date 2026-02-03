"""Voice-Controlled Braille Learning Device

Main entry point using Vosk-based recognition with grammar constraint.
Designed for single-letter recognition on Raspberry Pi.
"""

import argparse
import signal
import sys
import time

import config
from speech.vosk_recognizer import (
    VoskLetterRecognizer,
    check_vosk_installation,
    check_model_exists,
)
from speech.intent import parse_intent, IntentType
from audio.utils import AudioLevelMeter
from display import ServoDisplay, SimulationDisplay
from braille.mapping import get_braille_pattern
from audio.feedback import TTSFeedback
from braille.render import (
    render_ascii_grid,
    format_pattern_binary,
    get_dots_raised,
)


class BrailleLearner:
    """
    Main application controller for Braille learning device.

    Manages the complete workflow:
    1. Listen for speech (via Vosk recognizer)
    2. Parse intent (letter or command)
    3. Display Braille pattern
    4. Provide audio feedback
    5. Wait, then reset
    """

    def __init__(
        self,
        simulate=False,
        verbose=False,
        list_devices=False,
        test_mic=False,
        level_meter=False,
    ):
        # Mode detection
        if list_devices:
            self.mode = "list_devices"
        elif test_mic:
            self.mode = "test_mic"
        elif level_meter:
            self.mode = "level_meter"
        else:
            self.mode = "normal"

        # Configuration
        config.SIMULATION_MODE = simulate
        config.VERBOSE_MODE = verbose

        # Components (initialized in initialize())
        self.recognizer = None
        self.display = None
        self.mapper = None
        self.tts = None
        self.running = False

        # Signal handler
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print("\n\nShutting down gracefully...")
        self.running = False

    def initialize(self):
        """Initialize all components."""
        # Mode-specific initialization
        if self.mode == "list_devices":
            return  # No initialization needed

        if self.mode == "level_meter":
            return  # No initialization needed

        # Check Vosk installation
        if not check_vosk_installation():
            print("Error: Vosk not installed.")
            print("Install with: uv add vosk")
            sys.exit(1)

        # Check model exists
        if not check_model_exists():
            print("Error: Vosk model not found.")
            print("Download with: python download_vosk_model.py")
            sys.exit(1)

        try:
            # Initialize components
            self.recognizer = VoskLetterRecognizer()
            self.tts = TTSFeedback()

            # Choose display based on mode
            if config.SIMULATION_MODE:
                self.display = SimulationDisplay()
            else:
                self.display = ServoDisplay()

            self.running = True

            if self.mode != "test_mic":
                self._print_welcome()

        except Exception as e:
            print(f"Failed to initialize: {e}")
            print("\nTroubleshooting:")
            print("1. Check Vosk model is downloaded: python download_vosk_model.py")
            print("2. Check microphone is connected: python main.py --list-devices")
            print("3. For hardware mode, ensure servos are connected properly")
            sys.exit(1)

    def _print_welcome(self):
        """Print welcome message."""
        print("\nVoice-Controlled Braille Learning Device")
        print("=" * 42)
        print(f"Mode: {'SIMULATION' if config.SIMULATION_MODE else 'HARDWARE'}")
        print(f"Verbose: {'ON' if config.VERBOSE_MODE else 'OFF'}")
        print("\nInstructions:")
        print("- Speak a letter A-Z (e.g., 'a', 'bee', 'cee', 'double u')")
        print("- Or say 'letter X' (e.g., 'letter bee')")
        print("- Say 'exit' to quit")
        print("- Press Ctrl+C to quit\n")

    def run(self):
        """Run the application based on mode."""
        if self.mode == "list_devices":
            self._run_list_devices()
        elif self.mode == "test_mic":
            self._run_test_mic()
        elif self.mode == "level_meter":
            self._run_level_meter()
        else:
            self._run_normal()

    def _run_list_devices(self):
        """List available audio devices and exit."""
        recognizer = VoskLetterRecognizer()
        recognizer.print_devices()

    def _run_test_mic(self):
        """Test microphone with live Vosk recognition."""
        print("\n=== Microphone Test Mode ===")
        print("Speak letters or commands. Press Ctrl+C to stop.\n")

        self.recognizer.test_microphone(duration=30.0)

    def _run_level_meter(self):
        """Run audio level meter for debugging."""
        print("\n=== Audio Level Meter ===")
        print("Shows real-time audio levels. Useful for checking microphone.")

        meter = AudioLevelMeter(threshold=getattr(config, "SILENCE_THRESHOLD", 500))
        meter.run(duration=None)  # Run until Ctrl+C

    def _run_normal(self):
        """Main learning loop."""
        while self.running:
            try:
                # Listen for speech
                phrase = self.recognizer.recognize_stream()

                if phrase is None:
                    # Timeout or no speech detected
                    self.tts.speak_error_unrecognized()
                    print("I didn't understand, please try again\n")
                    continue

                # Parse intent
                intent = parse_intent(phrase)

                if intent.type == IntentType.EXIT:
                    print("\nExiting...")
                    self.tts.speak_exit()
                    break

                elif intent.type == IntentType.LETTER:
                    self._process_letter(intent.value)

                else:
                    # Unknown phrase
                    self.tts.speak_error_unrecognized()
                    print(f"I didn't understand '{phrase}', please try again\n")
                    continue

            except Exception as e:
                print(f"Error: {e}\n")
                continue

    def _process_letter(self, char: str):
        """
        Process a recognized letter.

        Displays the Braille pattern with proper timing:
        1. Set display pattern
        2. Print output and speak
        3. Wait for DISPLAY_DURATION
        4. Reset display
        """
        # Get pattern
        pattern = get_braille_pattern(char)
        if pattern is None:
            self.tts.speak_error_invalid()
            print(f"Invalid character: {char}")
            return

        # 1. Set display pattern (non-blocking)
        self.display.set_pattern(pattern)

        # 2. Print output
        self._print_output(char, pattern)

        # 3. Audio feedback
        self.tts.speak_letter(char)
        print(f"Voice feedback: Letter {char.upper()}")

        # 4. Wait (timing controlled here, not in display layer)
        print(f"Displaying for {config.DISPLAY_DURATION} seconds...")
        time.sleep(config.DISPLAY_DURATION)

        # 5. Reset display
        self.display.reset()
        print("\nResetting for next input...\n")

    def _print_output(self, char: str, pattern):
        """Print Braille output to console."""
        print(f"\nRecognized: {char.upper()}")

        # ASCII grid
        grid = render_ascii_grid(pattern)
        print("\nBraille Grid:")
        print(grid)

        # Binary representation
        binary = format_pattern_binary(pattern)
        print(f"\nPattern: [{binary}]")

        # Raised dots info
        dots = get_dots_raised(pattern)
        print(f"Dots raised: {dots}")

    def cleanup(self):
        """Clean up all resources."""
        if self.display:
            self.display.cleanup()
        if self.tts:
            self.tts.cleanup()
        print("Goodbye!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Voice-Controlled Braille Learning Device"
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run in simulation mode (no hardware)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio devices and exit",
    )
    parser.add_argument(
        "--test-mic",
        action="store_true",
        help="Test microphone with live Vosk recognition",
    )
    parser.add_argument(
        "--level-meter",
        action="store_true",
        help="Show audio level meter for debugging",
    )

    args = parser.parse_args()

    # Create learner
    learner = BrailleLearner(
        simulate=args.simulate,
        verbose=args.verbose,
        list_devices=args.list_devices,
        test_mic=args.test_mic,
        level_meter=args.level_meter,
    )

    # Run
    try:
        learner.initialize()
        learner.run()
    finally:
        learner.cleanup()


if __name__ == "__main__":
    main()
