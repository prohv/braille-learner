"""Audio utilities for safe audio processing.

Functions for device detection, stream creation, and safe RMS calculation.
Designed to be robust and avoid common pitfalls (NaN, overflow, etc.).
"""

from typing import Optional, List, Dict
import numpy as np

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    pyaudio = None


def list_audio_devices() -> List[Dict]:
    """
    List all available audio input devices.

    Returns:
        List of dictionaries with device info (index, name, sample_rate, channels).
    """
    if not PYAUDIO_AVAILABLE:
        raise RuntimeError("PyAudio not available")

    p = pyaudio.PyAudio()
    devices = []

    try:
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)

            # Only include input devices
            if info.get("maxInputChannels", 0) > 0:
                devices.append(
                    {
                        "index": int(info["index"]),
                        "name": str(info.get("name", "Unknown")),
                        "sample_rate": int(info.get("defaultSampleRate", 16000)),
                        "channels": int(info.get("maxInputChannels", 0)),
                        "default": False,  # Will be updated below
                    }
                )

        # Mark default device
        try:
            default_info = p.get_default_input_device_info()
            default_idx = default_info["index"]
            for device in devices:
                if device["index"] == default_idx:
                    device["default"] = True
        except:
            pass

    finally:
        p.terminate()

    return devices


def get_default_input_device() -> Optional[Dict]:
    """
    Get information about the default input device.

    Returns:
        Device info dictionary, or None if no default device.
    """
    if not PYAUDIO_AVAILABLE:
        return None

    p = pyaudio.PyAudio()

    try:
        info = p.get_default_input_device_info()
        return {
            "index": int(info["index"]),
            "name": str(info.get("name", "Unknown")),
            "sample_rate": int(info.get("defaultSampleRate", 16000)),
            "channels": int(info.get("maxInputChannels", 0)),
        }
    except Exception:
        return None
    finally:
        p.terminate()


def calculate_rms(audio_data: bytes) -> float:
    """
    Calculate RMS (Root Mean Square) of audio buffer safely.

    This is the proper way to calculate audio energy level.
    Converts to float32 before squaring to prevent int16 overflow.
    Handles NaN and invalid values gracefully.

    Args:
        audio_data: Raw audio bytes (16-bit PCM)

    Returns:
        RMS value as float. Returns 0.0 for empty or invalid data.
    """
    # Check for empty data
    if not audio_data or len(audio_data) == 0:
        return 0.0

    # Convert bytes to numpy array
    try:
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
    except:
        return 0.0

    if len(audio_array) == 0:
        return 0.0

    # CRITICAL: Convert to float32 BEFORE squaring to prevent overflow!
    # int16 values range from -32768 to 32767
    # Squaring int16: (-32768)^2 = 1,073,676,288 which exceeds int32 max (2,147,483,647)
    # This causes overflow and NaN values
    audio_float = audio_array.astype(np.float32)

    # Calculate mean of squares
    mean_squared = np.mean(audio_float**2)

    # Check for invalid values
    if not np.isfinite(mean_squared) or mean_squared < 0:
        return 0.0

    # Calculate RMS
    rms = np.sqrt(mean_squared)

    # Final safety check
    if not np.isfinite(rms):
        return 0.0

    return float(rms)


def detect_best_sample_rate(device_index: Optional[int] = None) -> int:
    """
    Detect the best sample rate for an audio device.

    Tries the device's default rate first, then falls back to common rates.

    Args:
        device_index: Device index to test. If None, uses default device.

    Returns:
        Recommended sample rate (one of: 16000, 22050, 44100, 48000).
    """
    if not PYAUDIO_AVAILABLE:
        return 16000

    p = pyaudio.PyAudio()

    try:
        # Get device info
        if device_index is None:
            try:
                device_info = p.get_default_input_device_info()
                device_index = device_info["index"]
                default_rate = int(device_info.get("defaultSampleRate", 16000))

                # Test if default rate works
                if _test_sample_rate(p, device_index, default_rate):
                    return default_rate
            except:
                pass
        else:
            try:
                device_info = p.get_device_info_by_index(device_index)
                default_rate = int(device_info.get("defaultSampleRate", 16000))

                if _test_sample_rate(p, device_index, default_rate):
                    return default_rate
            except:
                pass

        # Try common rates in order of preference
        common_rates = [16000, 22050, 44100, 48000]

        for rate in common_rates:
            if _test_sample_rate(p, device_index, rate):
                return rate

        # Fallback to safe default
        return 16000

    finally:
        p.terminate()


def _test_sample_rate(p: pyaudio.PyAudio, device_index: int, rate: int) -> bool:
    """
    Test if a sample rate is supported by the device.

    Args:
        p: PyAudio instance
        device_index: Device index to test
        rate: Sample rate to test

    Returns:
        True if rate works, False otherwise.
    """
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024,
        )
        stream.close()
        return True
    except:
        return False


class AudioLevelMeter:
    """
    Real-time audio level meter for debugging.

    Displays RMS values with visual indicators (bar graph).
    Useful for finding optimal silence threshold.
    """

    def __init__(self, threshold: int = 500, device_index: Optional[int] = None):
        self.threshold = threshold
        self.device_index = device_index
        self.sample_rate = 16000

    def run(self, duration: Optional[float] = None) -> None:
        """
        Run the level meter.

        Args:
            duration: Run for this many seconds. If None, run until Ctrl+C.
        """
        if not PYAUDIO_AVAILABLE:
            print("PyAudio not available")
            return

        # Detect sample rate
        self.sample_rate = detect_best_sample_rate(self.device_index)

        p = pyaudio.PyAudio()

        try:
            stream_kwargs = {
                "format": pyaudio.paInt16,
                "channels": 1,
                "rate": self.sample_rate,
                "input": True,
                "frames_per_buffer": 1024,
            }

            if self.device_index is not None:
                stream_kwargs["input_device_index"] = self.device_index

            stream = p.open(**stream_kwargs)
            stream.start_stream()

            print("\n=== Audio Level Meter ===")
            print(f"Threshold: {self.threshold}")
            print("Legend: 🔴 = below threshold, 🟢 = above threshold")
            print("Press Ctrl+C to stop\n")

            start_time = time.time()

            try:
                while True:
                    # Check duration
                    if duration and (time.time() - start_time) >= duration:
                        break

                    # Read audio
                    data = stream.read(1024, exception_on_overflow=False)
                    rms = calculate_rms(data)

                    # Create bar graph
                    bar_length = int(min(rms / 50, 40))  # Scale to ~40 chars max
                    bar = "█" * bar_length

                    # Status indicator
                    status = "🟢" if rms > self.threshold else "🔴"

                    # Print line (overwrite previous)
                    print(f"\r{status} RMS: {rms:7.1f} |{bar:<40}|", end="", flush=True)

            except KeyboardInterrupt:
                pass

            print("\n\nLevel meter stopped.")

        finally:
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass
            p.terminate()
