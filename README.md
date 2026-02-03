# Voice-Controlled Braille Learning Device

A compact, interactive electronic device that converts spoken letter names into tactile Braille patterns. Built for Raspberry Pi with offline speech recognition (Vosk) and servo-controlled tactile feedback.

## Features

- **Offline Speech Recognition**: Uses Vosk with constrained grammar for reliable single-letter recognition
- **Letter Name Recognition**: Accepts letter names like "bee", "cee", "double u", or "letter X" format
- **Audio Feedback**: Confirms recognized characters with text-to-speech
- **Tactile Output**: 6 servo motors display Braille patterns
- **Simulation Mode**: Test without hardware using CLI output
- **Debug Tools**: Device listing, microphone testing, and audio level meter
- **Deterministic Recognition**: Grammar-constrained vocabulary prevents false positives

## Hardware Requirements

- Raspberry Pi 4 or 5 (3B+ may work but not recommended)
- Microphone (USB or HAT)
- 6x Servo motors (SG90 or similar)
- External power supply for servos
- Mechanical structure for tactile pins

## Software Requirements

- Python 3.9+
- uv (package manager)

## Installation

### 1. Clone the repository

```bash
cd Braille-Learner
```

### 2. Install dependencies

```bash
uv add vosk numpy
```

### 3. Download Vosk model

```bash
python download_vosk_model.py
```

This downloads the Vosk English model (~40MB) to `models/vosk-model-small-en-us-0.15/`.

### 4. Test audio setup (optional)

```bash
# List available audio devices
python main.py --list-devices

# Test microphone with live recognition
python main.py --test-mic

# Check audio levels
python main.py --level-meter
```

## Usage

### Quick Start

```bash
# Simulation mode (no hardware required)
python main.py --simulate

# Hardware mode (requires Raspberry Pi + servos)
python main.py
```

### All CLI Options

```bash
python main.py --help
```

Options:
- `--simulate`: Run in simulation mode (no hardware)
- `--verbose`: Enable verbose output
- `--list-devices`: List available audio devices and exit
- `--test-mic`: Test microphone with live Vosk recognition
- `--level-meter`: Show audio level meter for debugging

### Speaking Letters

The device recognizes letter names in multiple formats:

**Direct letter names:**
- "a", "b", "c" (single letters)
- "bee", "cee", "dee" (phonetic names)
- "double u", "double you" (for W)
- "zee", "zed" (for Z)

**With "letter" prefix (more reliable):**
- "letter a", "letter bee", "letter cee"
- "letter double u"

**Exit command:**
- "exit", "quit", or "stop"

### Example Session

```
Voice-Controlled Braille Learning Device
==========================================
Mode: SIMULATION
Verbose: OFF

Instructions:
- Speak a letter A-Z (e.g., 'a', 'bee', 'cee', 'double u')
- Or say 'letter X' (e.g., 'letter bee')
- Say 'exit' to quit
- Press Ctrl+C to quit

Listening... (speak a letter)

Recognized: B

Braille Grid:
O .
O .
. .

Pattern: [110000]
Dots raised: [1, 2]
Voice feedback: Letter B
Displaying for 10 seconds...

Resetting for next input...

Listening... (speak a letter)
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
1 O O 4
2 O O 5
3 O O 6
```

(O = raised dot, . = lowered dot)

## Configuration

Edit `config.py` to customize:

- `SERVO_PINS`: GPIO pin numbers for each servo
- `SERVO_ANGLES`: Raised (0°) and lowered (90°) positions
- `DISPLAY_DURATION`: Time to keep Braille raised (default: 10s)
- `VERBOSE_MODE`: Enable debug output
- `MAX_RECORDING_DURATION`: Maximum recording time (default: 10s)

### Recognized Letter Phrases

The grammar includes these letter name variants:

- **A**: a, ay
- **B**: b, bee, be
- **C**: c, cee, see, sea
- **D**: d, dee
- **E**: e, ee
- **F**: f, ef
- **G**: g, gee
- **H**: h, aitch
- **I**: i, eye
- **J**: j, jay
- **K**: k, kay
- **L**: l, el
- **M**: m, em
- **N**: n, en
- **O**: o, oh
- **P**: p, pee
- **Q**: q, cue, queue
- **R**: r, are
- **S**: s, ess
- **T**: t, tee, tea
- **U**: u, you
- **V**: v, vee
- **W**: w, double u, double you
- **X**: x, ex
- **Y**: y, why
- **Z**: z, zee, zed

All phrases can also be prefixed with "letter" (e.g., "letter bee").

## Architecture

The application uses a clean, modular architecture:

```
speech/
  intent.py         - Intent parser (maps phrases to letters/commands)
  vosk_recognizer.py - Vosk streaming recognizer with grammar

audio/
  utils.py          - Audio utilities (RMS calculation, device listing)

display/
  base.py           - Display abstraction (ServoDisplay, SimulationDisplay)

braille/
  render.py         - ASCII grid rendering (O/.)

tests/
  test_intent.py    - Intent parser tests
  test_braille_render.py - ASCII rendering tests
```

## Testing

Run unit tests:

```bash
# All tests
uv run python -m unittest discover tests/

# Intent parser tests
uv run python -m unittest tests.test_intent -v

# Braille rendering tests
uv run python -m unittest tests.test_braille_render -v
```

## Troubleshooting

### "Failed to initialize speech recognition"

- Check Vosk is installed: `uv add vosk`
- Check model is downloaded: `python download_vosk_model.py`
- Model location: `models/vosk-model-small-en-us-0.15/`

### "No audio devices found"

- Check microphone is connected: `python main.py --list-devices`
- Install audio system libraries:
  ```bash
  sudo apt install portaudio19-dev
  ```

### Speech not recognized

- Use `--test-mic` to verify microphone works
- Try "letter X" format (e.g., "letter bee") for better recognition
- Speak clearly and close to microphone
- Check `--level-meter` to verify audio input levels

### "I didn't understand 'hello world'"

This is correct behavior! The device only recognizes letter names and exit commands. It rejects unknown phrases to prevent false positives.

### "aplay: command not found" (TTS)

- Install alsa-utils for audio playback:
  ```bash
  sudo apt install alsa-utils
  ```
- TTS is optional - the device works without it

### "gpiozero not available"

- Install system dependencies:
  ```bash
  sudo apt install python3-gpiozero
  ```
- Or run in simulation mode: `python main.py --simulate`

### Recognition is slow

- Vosk on Raspberry Pi 4/5 should be fast (< 500ms)
- If slow, check CPU usage: `htop`
- Consider disabling verbose mode to reduce overhead

### Servos not moving

- Verify GPIO connections match `config.py`
- Check external power supply is connected (servos need more power than Pi GPIO can provide)
- Test servos individually with `gpiozero` examples

### How do I add more commands?

Edit `speech/intent.py`:
1. Add phrases to `EXIT_PHRASES` for exit commands
2. Create new intent types in `IntentType` enum
3. Update `parse_intent()` function

## Migration from Faster Whisper

This project has migrated from Faster Whisper to Vosk for better single-letter recognition reliability. Key improvements:

- **Grammar constraint**: Only recognizes letter names, no false positives
- **Faster**: Streaming recognition without file I/O overhead
- **Deterministic**: Same input always produces same output
- **Offline**: No model downloads during runtime

## License

MIT License

## Authors

- Siddhant Jain - 24BCI0190
- Harsh Vardhan Singh - 24BCI0147

## Acknowledgments

- [Vosk](https://alphacephei.com/vosk/) - Offline speech recognition toolkit
- [gpiozero](https://gpiozero.readthedocs.io/) - GPIO library for Raspberry Pi
- [pyttsx3](https://pypi.org/project/pyttsx3/) - Text-to-Speech library
