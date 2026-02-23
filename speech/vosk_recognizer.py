"""Vosk streaming speech recognizer with grammar constraint.

Optimized for single-letter recognition on Raspberry Pi.
Uses constrained vocabulary for deterministic, fast recognition.
"""

import json
import time
from pathlib import Path
from typing import Optional, List, Dict
import config

# Optional imports - fail gracefully if not available
try:
    import vosk

    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    vosk = None

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    pyaudio = None

from speech.intent import build_vosk_grammar
from audio.utils import get_default_input_device


class VoskRecognizerError(Exception):
    """Custom exception for Vosk recognizer errors."""

    pass


class VoskLetterRecognizer:
    """
    Streaming Vosk recognizer optimized for letter recognition.

    Uses grammar constraint to limit recognition to letter names
    and commands only, providing deterministic, fast results.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        sample_rate: Optional[int] = None,
        device_index: Optional[int] = None,
    ):
        """
        Initialize Vosk recognizer.

        Args:
            model_path: Path to Vosk model directory. If None, uses config default.
            sample_rate: Audio sample rate. If None, auto-detects from device.
            device_index: Audio device index. If None, uses default device.
        """
        if not VOSK_AVAILABLE:
            raise VoskRecognizerError(
                "Vosk not installed. Install with: pip install vosk"
            )

        if not PYAUDIO_AVAILABLE:
            raise VoskRecognizerError(
                "PyAudio not installed. Install with: pip install pyaudio"
            )

        self.model_path = model_path or "models/vosk-model-small-en-us-0.15"
        self.device_index = device_index
        self.sample_rate = sample_rate or self._detect_sample_rate()

        self.model = None
        self.recognizer = None
        self._grammar = None

        self._initialize_model()

    def _detect_sample_rate(self) -> int:
        """Detect appropriate sample rate from input device."""
        try:
            device_info = get_default_input_device()
            if device_info:
                detected_rate = device_info.get("sample_rate", 16000)
                if config.VERBOSE_MODE:
                    print(f"[VERBOSE] Auto-detected sample rate: {detected_rate} Hz")
                return detected_rate
        except Exception as e:
            if config.VERBOSE_MODE:
                print(f"[VERBOSE] Could not detect sample rate: {e}")

        return 16000  # Safe default

    def _initialize_model(self) -> None:
        """Load Vosk model and create recognizer with grammar."""
        model_dir = Path(self.model_path)

        if not model_dir.exists():
            raise VoskRecognizerError(
                f"Vosk model not found at {self.model_path}\n"
                f"Download with: python download_vosk_model.py"
            )

        try:
            self.model = vosk.Model(str(model_dir))

            # Build grammar for letter recognition
            self._grammar = build_vosk_grammar()

            if config.VERBOSE_MODE:
                print(f"[VERBOSE] Loaded Vosk model from {self.model_path}")
                print(f"[VERBOSE] Grammar size: {len(self._grammar)} phrases")

            # Create recognizer with grammar constraint to focus on single letters
            # Add [unk] token to capture out-of-vocabulary noise instead of forcing false positives
            grammar_list = list(self._grammar) if isinstance(self._grammar, set) else self._grammar
            if "[unk]" not in grammar_list:
                grammar_list.append("[unk]")
            grammar_json = json.dumps(grammar_list)
            
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate, grammar_json)
            self.recognizer.SetWords(True)

            if config.VERBOSE_MODE:
                print("[VERBOSE] Vosk recognizer initialized (constrained with grammar)")

        except Exception as e:
            raise VoskRecognizerError(f"Failed to initialize Vosk: {e}")

    def recognize_stream(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Listen to audio stream and return recognized phrase.

        Streams audio from microphone and processes with Vosk.
        Returns when a final result is available or timeout reached.

        Args:
            timeout: Maximum time to listen in seconds. If None, uses config default.

        Returns:
            Recognized phrase string, or None if timeout/cancelled/no speech.

        Example:
            >>> recognizer = VoskLetterRecognizer()
            >>> phrase = recognizer.recognize_stream(timeout=10.0)
            >>> print(phrase)  # "bee" or "letter a" or "exit"
        """
        timeout = timeout or getattr(config, "MAX_RECORDING_DURATION", 10.0)

        if not self.recognizer:
            raise VoskRecognizerError("Recognizer not initialized")

        # Open audio stream
        p = pyaudio.PyAudio()

        try:
            stream_kwargs = {
                "format": pyaudio.paInt16,
                "channels": 1,
                "rate": self.sample_rate,
                "input": True,
                "frames_per_buffer": 2048,  # Larger buffer for stability
            }

            if self.device_index is not None:
                stream_kwargs["input_device_index"] = self.device_index

            stream = p.open(**stream_kwargs)
            stream.start_stream()

            if config.VERBOSE_MODE:
                print(f"[VERBOSE] Audio stream opened (rate={self.sample_rate})")

            print("Listening... (speak a letter)")

            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    # Read audio chunk
                    data = stream.read(2048, exception_on_overflow=False)

                    # Process with Vosk
                    if self.recognizer.AcceptWaveform(data):
                        # Got a final result
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "").strip()

                        if text:
                            # Calculate confidence score
                            words = result.get("result", [])
                            if words:
                                # Get average confidence
                                avg_conf = sum(w.get("conf", 0.0) for w in words) / len(words)
                                if avg_conf < 0.50:
                                    if config.VERBOSE_MODE:
                                        print(f"[VERBOSE] Rejected '{text}' due to low confidence: {avg_conf:.2f}")
                                    continue

                            if config.VERBOSE_MODE:
                                print(f"[VERBOSE] Recognized: '{text}' (Conf: {avg_conf:.2f})" if words else f"[VERBOSE] Recognized: '{text}'")
                            return text

                        # Empty result, continue listening
                        if config.VERBOSE_MODE:
                            print("[VERBOSE] Empty result, continuing...")

                except OSError:
                    # Audio overflow, skip this chunk
                    continue

            # Timeout reached
            if config.VERBOSE_MODE:
                print(f"[VERBOSE] Timeout reached ({timeout}s)")

            return None

        finally:
            # Cleanup
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
            p.terminate()

            if config.VERBOSE_MODE:
                print("[VERBOSE] Audio stream closed")

    def test_microphone(self, duration: float = 5.0) -> None:
        """
        Test microphone with live Vosk recognition.

        Shows partial and final results in real-time.
        Useful for verifying audio setup and recognition quality.

        Args:
            duration: Test duration in seconds.
        """
        if not self.recognizer:
            raise VoskRecognizerError("Recognizer not initialized")

        p = pyaudio.PyAudio()

        try:
            stream_kwargs = {
                "format": pyaudio.paInt16,
                "channels": 1,
                "rate": self.sample_rate,
                "input": True,
                "frames_per_buffer": 2048,
            }

            if self.device_index is not None:
                stream_kwargs["input_device_index"] = self.device_index

            stream = p.open(**stream_kwargs)
            stream.start_stream()

            print(f"\n=== Microphone Test ({duration}s) ===")
            print("Speak letters or commands. Press Ctrl+C to stop early.\n")

            start_time = time.time()
            last_partial = ""

            try:
                while time.time() - start_time < duration:
                    data = stream.read(2048, exception_on_overflow=False)

                    # Check for partial result
                    partial_result = self.recognizer.PartialResult()
                    partial_data = json.loads(partial_result)
                    partial_text = partial_data.get("partial", "").strip()

                    if partial_text and partial_text != last_partial:
                        print(f"[Partial] {partial_text}")
                        last_partial = partial_text

                    # Check for final result
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "").strip()

                        if text:
                            print(f"\n✓ Final: '{text}'\n")
                            last_partial = ""

            except KeyboardInterrupt:
                print("\n\nTest stopped by user.")

            print("Test complete.")

        finally:
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
            p.terminate()

    def list_devices(self) -> List[Dict]:
        """
        List available audio input devices.

        Returns:
            List of device info dictionaries with index, name, sample rate.
        """
        if not PYAUDIO_AVAILABLE:
            raise VoskRecognizerError("PyAudio not available")

        p = pyaudio.PyAudio()
        devices = []

        try:
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)

                # Only include input devices
                if info.get("maxInputChannels", 0) > 0:
                    devices.append(
                        {
                            "index": i,
                            "name": info.get("name", "Unknown"),
                            "sample_rate": int(info.get("defaultSampleRate", 16000)),
                            "channels": info.get("maxInputChannels", 0),
                        }
                    )
        finally:
            p.terminate()

        return devices

    def print_devices(self) -> None:
        """Print available audio devices in a formatted list."""
        devices = self.list_devices()

        print("\n=== Available Audio Input Devices ===\n")

        if not devices:
            print("No input devices found!")
            print("Check that your microphone is connected.")
            return

        for device in devices:
            print(f"  [{device['index']}] {device['name']}")
            print(f"      Sample Rate: {device['sample_rate']} Hz")
            print(f"      Channels: {device['channels']}")
            print()

        # Show default
        try:
            p = pyaudio.PyAudio()
            default = p.get_default_input_device_info()
            print(f"Default device: [{default['index']}] {default['name']}")
            p.terminate()
        except Exception:
            pass


def check_vosk_installation() -> bool:
    """
    Check if Vosk is properly installed.

    Returns:
        True if Vosk is available, False otherwise.
    """
    return VOSK_AVAILABLE


def check_model_exists(path: Optional[str] = None) -> bool:
    """
    Check if Vosk model exists at given path.

    Args:
        path: Model path to check. If None, uses config default.

    Returns:
        True if model directory exists, False otherwise.
    """
    path = path or "models/vosk-model-small-en-us-0.15"
    return Path(path).exists()
