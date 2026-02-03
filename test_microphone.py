#!/usr/bin/env python3

import pyaudio
import vosk
import json
import time
from utils.audio_helper import get_default_input_device, detect_best_sample_rate


def test_microphone():
    print("Microphone Test")
    print("=" * 60)

    device_info = get_default_input_device()
    if not device_info:
        print("No default input device found!")
        return False

    print(f"\nUsing device: {device_info['name']}")
    print(f"Default sample rate: {device_info['sample_rate']} Hz")

    sample_rate = detect_best_sample_rate()
    print(f"Detected sample rate: {sample_rate} Hz")

    print("\nInitializing Vosk model...")
    try:
        model = vosk.Model("models/vosk-model-small-en-us-0.15")
        rec = vosk.KaldiRecognizer(model, sample_rate)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Failed to load model: {e}")
        return False

    print("\nTesting microphone capture...")
    print("Speak a single letter (A-Z)...")
    print("(Waiting 5 seconds)\n")

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=8192,
    )

    stream.start_stream()

    frames = []
    start_time = time.time()

    while time.time() - start_time < 5:
        data = stream.read(4096, exception_on_overflow=False)
        frames.append(data)

        if len(frames) > 50:
            audio_data = b"".join(frames)
            if rec.AcceptWaveform(audio_data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip().lower()
                frames = []
                if text:
                    print(f"Recognized: {text}")
                    break

    if not frames:
        final_result = json.loads(rec.FinalResult())
        text = final_result.get("text", "").strip().lower()
        if text:
            print(f"Recognized (final): {text}")
        else:
            print("No speech detected")

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("\n" + "=" * 60)
    print("Test complete!")
    return True


if __name__ == "__main__":
    test_microphone()
