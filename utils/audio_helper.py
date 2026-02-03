import pyaudio
import config


def list_audio_devices():
    """List all available audio devices with their capabilities."""
    p = pyaudio.PyAudio()
    print("\nAvailable Audio Devices:")
    print("=" * 60)

    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        name = info["name"]
        max_input = info["maxInputChannels"]
        max_output = info["maxOutputChannels"]
        default_sample_rate = int(info["defaultSampleRate"])

        device_type = ""
        if max_input > 0 and max_output > 0:
            device_type = "Input/Output"
        elif max_input > 0:
            device_type = "Input Only"
        elif max_output > 0:
            device_type = "Output Only"

        if device_type:
            print(f"\nDevice {i}: {name}")
            print(f"  Type: {device_type}")
            print(f"  Max Input Channels: {max_input}")
            print(f"  Max Output Channels: {max_output}")
            print(f"  Default Sample Rate: {default_sample_rate} Hz")

    p.terminate()


def find_input_device():
    """Find the best available input device."""
    p = pyaudio.PyAudio()

    input_devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:
            input_devices.append(
                {
                    "index": i,
                    "name": info["name"],
                    "default_sample_rate": int(info["defaultSampleRate"]),
                    "max_input_channels": info["maxInputChannels"],
                }
            )

    p.terminate()

    if not input_devices:
        print("No input devices found!")
        return None

    print("\nInput Devices:")
    for device in input_devices:
        print(
            f"  {device['index']}: {device['name']} ({device['default_sample_rate']} Hz)"
        )

    return input_devices


def get_default_input_device():
    """Get the default input device and its sample rate."""
    p = pyaudio.PyAudio()

    try:
        default_device = p.get_default_input_device_info()
        device_index = default_device["index"]
        default_sample_rate = int(default_device["defaultSampleRate"])
        device_name = default_device["name"]

        p.terminate()

        return {
            "index": device_index,
            "name": device_name,
            "sample_rate": default_sample_rate,
        }
    except Exception as e:
        print(f"Error getting default input device: {e}")
        p.terminate()
        return None


def test_sample_rate(device_index=None, sample_rate=None):
    """Test if a sample rate is supported by the device."""
    p = pyaudio.PyAudio()

    if device_index is None:
        try:
            device_index = p.get_default_input_device_info()["index"]
        except:
            device_index = None

    if sample_rate is None:
        try:
            sample_rate = int(
                p.get_device_info_by_index(device_index)["defaultSampleRate"]
            )
        except:
            sample_rate = 16000

    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024,
        )
        stream.close()
        p.terminate()
        return True
    except Exception as e:
        p.terminate()
        return False


def detect_best_sample_rate(device_index=None):
    """Detect the best supported sample rate for the device."""
    common_rates = [16000, 22050, 44100, 48000]

    device_info = get_default_input_device()
    if device_info:
        default_rate = device_info["sample_rate"]
        if test_sample_rate(device_index, default_rate):
            print(f"Using default sample rate: {default_rate} Hz")
            return default_rate

    print("Testing common sample rates...")
    for rate in common_rates:
        if test_sample_rate(device_index, rate):
            print(f"Found working sample rate: {rate} Hz")
            return rate

    print("No working sample rate found, using 16000 Hz")
    return 16000
