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

mkdir -p models

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Test your microphone threshold (optional but recommended):"
echo "   python main.py --test-threshold"
echo ""
echo "2. Debug microphone mode (optional):"
echo "   python main.py --debug-mic"
echo ""
echo "3. Run the application:"
echo "   python main.py --simulate"
echo ""
echo "4. For hardware mode:"
echo "   python main.py"
echo ""
echo "Note: Faster Whisper model will auto-download on first run (~46MB for tiny model)"
echo "Models are cached in: ~/.cache/huggingface/hub/"
