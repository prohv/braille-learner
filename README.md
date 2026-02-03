# Voice-Controlled Braille Learning Device

A compact, interactive electronic device that converts spoken alphanumeric input into tactile Braille patterns. Built for Raspberry Pi with offline speech recognition and servo-controlled tactile feedback.

## Features

- **Offline Speech Recognition**: Uses Vosk for accurate voice input (A-Z letters)
- **Audio Feedback**: Confirms recognized characters with text-to-speech
- **Tactile Output**: 6 servo motors display Braille patterns
- **Simulation Mode**: Test without hardware using CLI output
- **Verbose Mode**: Debug output for development and troubleshooting

## Hardware Requirements

- Raspberry Pi (3B+ or newer recommended)
- Microphone (USB or HAT)
- 6x Servo motors (SG90 or similar)
- External power supply for servos
- Mechanical structure for tactile pins

## Software Requirements

- Python 3.8+
- uv (package manager)

## Installation

### 1. Clone the repository

```bash
cd Braille-Learner
```

### 2. Run setup script

```bash
chmod +x setup.sh
./setup.sh
```

This installs system dependencies and Python packages.

### 3. Download Vosk model

```bash
python download_model.py
```

This downloads the small English model (~40MB) to `models/vosk-model-small-en-us-0.15/`.

### 4. Test audio devices (optional)

```bash
python test_audio.py
```

This shows available audio devices and detects the best sample rate for your microphone.

### Manual model download

If the download script fails, download manually:
1. Visit: https://alphacephei.com/vosk/models
2. Download: vosk-model-small-en-us-0.15.zip
3. Extract to: models/vosk-model-small-en-us-0.15/

## Usage

### Simulation Mode (no hardware)

```bash
python main.py --simulate
```

### Hardware Mode

```bash
python main.py
```

### Verbose Mode

```bash
python main.py --simulate --verbose
```

## GPIO Pin Configuration

The default configuration uses these GPIO pins:

```
Dot 1: GPIO 17 (top-left)
Dot 2: GPIO 27 (mid-left)
Dot 3: GPIO 22 (bottom-left)
Dot 4: GPIO 5  (top-right)
Dot 5: GPIO 6  (mid-right)
Dot 6: GPIO 13 (bottom-right)
```

Edit `config.py` to change pin assignments.

## Braille Dot Layout

```
1 o o 4
2 o o 5
3 o o 6
```

## Operation

1. Speak a letter (A-Z) into the microphone
2. The device recognizes the letter and speaks it back
3. The Braille pattern is displayed:
   - Hardware: Servos raise the corresponding dots
   - Simulation: ASCII grid shows the pattern
4. The pattern displays for 10 seconds
5. All dots reset to the lowered position
6. System waits for next input

Say "exit" or press Ctrl+C to quit.

## CLI Output Example

```
Voice-Controlled Braille Learning Device
==========================================
Mode: SIMULATION
Verbose: ON

Instructions:
- Speak a letter A-Z to see the Braille pattern
- Say 'exit' to quit
- Press Ctrl+C to quit

Listening...
Recognized: A
Braille: ⠁ [100000]

Braille Grid:
● ○
○ ○
○ ○

Dots raised: [1]
Voice feedback: Letter A
Displaying for 10 seconds...

Resetting for next input...
```

## Configuration

Edit `config.py` to customize:

- `SERVO_PINS`: GPIO pin numbers for each servo
- `SERVO_ANGLES`: Raised (0°) and lowered (90°) positions
- `DISPLAY_DURATION`: Time to keep Braille raised (default: 10s)
- `LISTENING_TIMEOUT`: Time to wait for speech (default: 5s)
- `VERBOSE_MODE`: Enable debug output
- `AUTO_DETECT_SAMPLE_RATE`: Auto-detect microphone sample rate (default: True)
- `AUDIO_SAMPLE_RATE`: Fallback sample rate (default: 16000 Hz)
- `AUDIO_DEVICE_INDEX`: Specific audio device to use (default: None = system default)

## Testing

Run unit tests:

```bash
python -m pytest tests/
```

Or run individual test files:

```bash
python tests/test_braille_mapper.py
python tests/test_servo_controller.py
```

## Troubleshooting

### "Failed to initialize speech recognizer"

- Ensure the Vosk model is downloaded: `python download_model.py`
- Check model path in `config.py` matches actual location

### "Invalid sample rate" error (-9997)

- Run the audio test: `python test_audio.py`
- The app now auto-detects the best sample rate
- If issues persist, check your microphone's supported sample rates in the test output

### "aplay: command not found"

- Install alsa-utils for audio playback (TTS):
  ```bash
  sudo apt install alsa-utils
  ```

### "gpiozero not available"

- Install system dependencies: `sudo apt install python3-gpiozero`
- Or run in simulation mode: `python main.py --simulate`

### No audio input

- Run `python test_audio.py` to check available devices
- Check microphone is connected and recognized: `arecord -l`
- Test microphone: `arecord -f cd test.wav`

### Servos not moving

- Verify GPIO connections match `config.py`
- Check external power supply is connected
- Test servos individually with `gpiozero` examples

## License

MIT License

## Authors

- Siddhant Jain - 24BCI0190
- Harsh Vardhan Singh - 24BCI0147

## Acknowledgments

- Vosk Speech Recognition Toolkit
- gpiozero GPIO library
- pyttsx3 Text-to-Speech
