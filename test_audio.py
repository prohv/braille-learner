#!/usr/bin/env python3

from utils.audio_helper import (
    list_audio_devices,
    find_input_device,
    detect_best_sample_rate,
)


def main():
    print("Audio Device Test")
    print("=" * 60)

    print("\n1. Listing all audio devices...")
    list_audio_devices()

    print("\n2. Finding input devices...")
    input_devices = find_input_device()

    print("\n3. Detecting best sample rate...")
    best_rate = detect_best_sample_rate()
    print(f"\nRecommended sample rate: {best_rate} Hz")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("\nIf you have audio issues, note the above information.")


if __name__ == "__main__":
    main()
