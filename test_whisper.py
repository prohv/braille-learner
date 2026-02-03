#!/usr/bin/env python3

from faster_whisper import WhisperModel
import config


def test_whisper():
    print("Testing Faster Whisper...")
    print(f"Model size: {config.WHISPER_MODEL_SIZE}")
    print(f"Device: {config.WHISPER_DEVICE}")
    print(f"Compute type: {config.WHISPER_COMPUTE_TYPE}")

    try:
        print("\nLoading model (may download on first run)...")
        model = WhisperModel(
            config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
        )
        print("Model loaded successfully!")
        print(f"\nWhisper is ready to use.")
        print(f"Model will be cached in: ~/.cache/huggingface/hub/")
        return True
    except Exception as e:
        print(f"\nFailed to load model: {e}")
        print("Make sure faster-whisper is installed:")
        print("  uv pip install faster-whisper numpy")
        return False


if __name__ == "__main__":
    test_whisper()
