#!/bin/bash

echo "Setting up Voice-Controlled Braille Learning Device..."

sudo apt update
sudo apt install -y python3-dev portaudio19-dev ffmpeg espeak-ng

echo ""
echo "NOTE: For audio playback (TTS), you may need to install alsa-utils:"
echo "  sudo apt install alsa-utils"
echo ""

if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

uv pip install -e .

mkdir -p models

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Download the Vosk model:"
echo "   python download_model.py"
echo ""
echo "2. Check your audio devices (optional):"
echo "   python test_audio.py"
echo ""
echo "3. Run the application:"
echo "   python main.py --simulate"
echo ""
echo "4. For hardware mode:"
echo "   python main.py"
echo ""
