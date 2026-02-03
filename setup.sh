#!/bin/bash

set -e

echo "Setting up Voice-Controlled Braille Learning Device..."

# System dependencies
sudo apt update
sudo apt install -y python3-dev portaudio19-dev espeak-ng

echo ""
echo "NOTE: For audio playback (TTS), you may need alsa-utils:"
echo "  sudo apt install alsa-utils"
echo ""

# Check uv
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Install with:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install Python deps
echo "Installing Python dependencies..."
uv pip install -e .

# Download Vosk model
echo ""
echo "Downloading Vosk model (one-time)..."
python download_vosk_model.py

echo ""
echo "Setup complete!"
echo ""
echo "Recommended first steps:"
echo "1. List audio devices:"
echo "   python main.py --list-devices"
echo ""
echo "2. Test your microphone:"
echo "   python main.py --test-mic"
echo ""
echo "3. Run the application:"
echo "   python main.py --simulate"
echo ""
echo "4. For hardware mode:"
echo "   python main.py"
