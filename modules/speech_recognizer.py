from faster_whisper import WhisperModel
import pyaudio
import numpy as np
import io
import wave
import tempfile
import os
import config
from utils.audio_helper import get_default_input_device, detect_best_sample_rate


class SpeechRecognizer:
    def __init__(self):
        self.model = None
        self.p = None
        self.stream = None
        self.sample_rate = config.AUDIO_SAMPLE_RATE
        self.device_index = config.AUDIO_DEVICE_INDEX
        self._initialize()

    def _initialize(self):
        try:
            detected_rate = detect_best_sample_rate(self.device_index)
            if detected_rate:
                self.sample_rate = detected_rate
                config.AUDIO_SAMPLE_RATE = detected_rate
                if config.VERBOSE_MODE:
                    print(f"[VERBOSE] Detected sample rate: {self.sample_rate} Hz")

            self.model = WhisperModel(
                config.WHISPER_MODEL_SIZE,
                device=config.WHISPER_DEVICE,
                compute_type=config.WHISPER_COMPUTE_TYPE,
            )

            self.p = pyaudio.PyAudio()

            if config.VERBOSE_MODE:
                device_info = get_default_input_device()
                if device_info:
                    print(f"[VERBOSE] Using input device: {device_info['name']}")

        except Exception as e:
            print(f"Failed to initialize speech recognizer: {e}")
            raise

    def listen(self):
        try:
            if config.DEBUG_MIC_MODE:
                return self._debug_mic_mode()

            audio_data = self._capture_audio()

            if len(audio_data) < int(self.sample_rate * config.MIN_SPEECH_DURATION * 2):
                if config.VERBOSE_MODE:
                    print(f"[VERBOSE] Audio too short: {len(audio_data)} bytes")
                return None

            temp_file = self._save_to_wav(audio_data, self.sample_rate)

            text = self._transcribe_audio(temp_file)

            os.unlink(temp_file)

            return text

        except Exception as e:
            print(f"Error during speech recognition: {e}")
            return None

    def _capture_audio(self):
        stream_kwargs = {
            "format": pyaudio.paInt16,
            "channels": 1,
            "rate": self.sample_rate,
            "input": True,
            "frames_per_buffer": 512,
        }

        if self.device_index is not None:
            stream_kwargs["input_device_index"] = self.device_index

        stream = self.p.open(**stream_kwargs)

        frames = []
        silent_frames = 0
        speech_detected = False
        total_frames = 0
        max_frames = int(self.sample_rate * config.MAX_RECORDING_DURATION / 512)

        while total_frames < max_frames:
            data = stream.read(512, exception_on_overflow=False)
            rms = self._calculate_rms(data)

            if config.VERBOSE_MODE:
                status = "SPEECH" if rms > config.SILENCE_THRESHOLD else "SILENT"
                print(f"[VERBOSE] RMS: {rms:6.1f} | {status}")

            if rms > config.SILENCE_THRESHOLD:
                if not speech_detected:
                    if config.VERBOSE_MODE:
                        print(f"[VERBOSE] Speech detected (RMS: {rms:.1f})")
                speech_detected = True
                silent_frames = 0
                frames.append(data)
            elif speech_detected:
                silent_frames += 1
                frames.append(data)

                silence_frames_needed = int(
                    config.SILENCE_DURATION * self.sample_rate / 512
                )
                if silent_frames >= silence_frames_needed:
                    if config.VERBOSE_MODE:
                        print(f"[VERBOSE] Silence detected, stopping recording")
                    break

            total_frames += 1

        stream.close()
        return b"".join(frames)

    def _debug_mic_mode(self):
        print("\n=== Microphone Debug Mode ===")
        print(f"Current threshold: {config.SILENCE_THRESHOLD}")
        print("Speak into your microphone to see RMS values...")
        print("Press Ctrl+C to exit\n")

        stream_kwargs = {
            "format": pyaudio.paInt16,
            "channels": 1,
            "rate": self.sample_rate,
            "input": True,
            "frames_per_buffer": 512,
        }

        if self.device_index is not None:
            stream_kwargs["input_device_index"] = self.device_index

        stream = self.p.open(**stream_kwargs)

        try:
            while True:
                data = stream.read(512, exception_on_overflow=False)
                rms = self._calculate_rms(data)
                status = "🟢 SPEECH" if rms > config.SILENCE_THRESHOLD else "🔴 SILENT"
                print(
                    f"RMS: {rms:6.1f} | Threshold: {config.SILENCE_THRESHOLD:5d} | {status}"
                )
        except KeyboardInterrupt:
            print("\n\nDebug mode ended")
        finally:
            stream.close()

        return None

    def test_threshold(self):
        print("\n=== Silence Threshold Test ===")
        print("This will help you find the optimal threshold for your microphone.")
        print("Speak a few words at normal volume during the recording.")
        print("\nPress Enter when ready to start...")
        input()

        stream_kwargs = {
            "format": pyaudio.paInt16,
            "channels": 1,
            "rate": self.sample_rate,
            "input": True,
            "frames_per_buffer": 512,
        }

        if self.device_index is not None:
            stream_kwargs["input_device_index"] = self.device_index

        stream = self.p.open(**stream_kwargs)

        print("Recording (3 seconds)...")
        rms_values = []
        for _ in range(int(self.sample_rate * 3 / 512)):
            data = stream.read(512, exception_on_overflow=False)
            rms = self._calculate_rms(data)
            rms_values.append(rms)

        stream.close()

        min_rms = min(rms_values)
        max_rms = max(rms_values)
        avg_rms = sum(rms_values) / len(rms_values)
        suggested_threshold = int(min_rms + (max_rms - min_rms) * 0.3)

        print(f"\nAudio Analysis:")
        print(f"  Minimum RMS:  {min_rms:.1f}")
        print(f"  Maximum RMS:  {max_rms:.1f}")
        print(f"  Average RMS:  {avg_rms:.1f}")
        print(f"\nSuggested threshold: {suggested_threshold}")
        print(f"Current threshold:   {config.SILENCE_THRESHOLD}")

        response = input(f"\nUpdate threshold to {suggested_threshold}? (y/n): ")
        if response.lower() == "y":
            config.SILENCE_THRESHOLD = suggested_threshold
            print(f"Threshold updated to {suggested_threshold}")

    def _calculate_rms(self, audio_data):
        if len(audio_data) == 0:
            return 0.0

        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        if len(audio_array) == 0:
            return 0.0

        audio_array = audio_array[np.isfinite(audio_array)]

        if len(audio_array) == 0:
            return 0.0

        mean_squared = np.mean(audio_array**2)

        if not np.isfinite(mean_squared) or mean_squared < 0:
            return 0.0

        rms = np.sqrt(mean_squared)
        if not np.isfinite(rms):
            return 0.0

        return rms

    def _is_silent(self, audio_data, threshold):
        rms = self._calculate_rms(audio_data)
        return rms < threshold

    def _save_to_wav(self, audio_data, sample_rate):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.close()

        with wave.open(temp_file.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data)

        return temp_file.name

    def _transcribe_audio(self, wav_path):
        try:
            segments, info = self.model.transcribe(
                wav_path,
                language=config.WHISPER_LANGUAGE,
                beam_size=config.WHISPER_BEAM_SIZE,
                vad_filter=True,
                vad_parameters={
                    "min_silence_duration_ms": int(config.SILENCE_DURATION * 1000),
                    "min_speech_duration_ms": int(config.MIN_SPEECH_DURATION * 1000),
                },
            )

            full_text = "".join([seg.text for seg in segments])
            text = full_text.lower().strip()

            if config.VERBOSE_MODE:
                print(
                    f"[VERBOSE] Detected language: {info.language} (prob: {info.language_probability:.2f})"
                )
                print(f"[VERBOSE] Transcribed text: {text}")

            return self._process_text(text)

        except Exception as e:
            print(f"Transcription error: {e}")
            return None

    def _process_text(self, text):
        if not text:
            return None

        words = text.split()

        for word in words:
            word = word.strip().lower()

            if word == "exit":
                return "exit"

            if len(word) == 1 and word.isalpha():
                return word

        return None

    def cleanup(self):
        if self.p:
            try:
                self.p.terminate()
            except:
                pass
