import pyaudio
import vosk
import json
import config
from utils.audio_helper import detect_best_sample_rate, get_default_input_device


class SpeechRecognizer:
    def __init__(self):
        self.model = None
        self.rec = None
        self.p = None
        self.stream = None
        self.sample_rate = config.AUDIO_SAMPLE_RATE
        self.device_index = config.AUDIO_DEVICE_INDEX
        self._initialize()

    def _initialize(self):
        try:
            self.model = vosk.Model(config.VOSK_MODEL_PATH)
            self.p = pyaudio.PyAudio()

            if config.AUTO_DETECT_SAMPLE_RATE:
                detected_rate = detect_best_sample_rate(self.device_index)
                if detected_rate:
                    self.sample_rate = detected_rate
                    config.AUDIO_SAMPLE_RATE = detected_rate
                    if config.VERBOSE_MODE:
                        print(
                            f"[VERBOSE] Using detected sample rate: {self.sample_rate} Hz"
                        )

            self.rec = vosk.KaldiRecognizer(self.model, self.sample_rate)

            if config.VERBOSE_MODE:
                device_info = get_default_input_device()
                if device_info:
                    print(
                        f"[VERBOSE] Using input device: {device_info['name']} ({device_info['index']})"
                    )

        except Exception as e:
            print(f"Failed to initialize speech recognizer: {e}")
            print(f"Make sure the Vosk model is downloaded to {config.VOSK_MODEL_PATH}")
            print(
                f"If sample rate issues persist, try running: python utils/audio_helper.py"
            )
            raise

    def listen(self):
        try:
            stream_kwargs = {
                "format": pyaudio.paInt16,
                "channels": 1,
                "rate": self.sample_rate,
                "input": True,
                "frames_per_buffer": 8192,
            }

            if self.device_index is not None:
                stream_kwargs["input_device_index"] = self.device_index

            self.stream = self.p.open(**stream_kwargs)

            self.stream.start_stream()
            print("Listening...")

            frames = []
            import time

            start_time = time.time()

            while time.time() - start_time < config.LISTENING_TIMEOUT:
                data = self.stream.read(4096, exception_on_overflow=False)
                frames.append(data)

                if len(frames) > 50:
                    audio_data = b"".join(frames)
                    if self.rec.AcceptWaveform(audio_data):
                        result = json.loads(self.rec.Result())
                        text = result.get("text", "").strip().lower()
                        frames = []
                        if text:
                            if config.VERBOSE_MODE:
                                print(f"[VERBOSE] Recognized text: {text}")
                            return self._process_text(text)

            final_result = json.loads(self.rec.FinalResult())
            text = final_result.get("text", "").strip().lower()
            if text:
                if config.VERBOSE_MODE:
                    print(f"[VERBOSE] Final result: {text}")
                return self._process_text(text)

            if config.VERBOSE_MODE:
                print("[VERBOSE] No speech detected")
            return None

        except Exception as e:
            print(f"Error during speech recognition: {e}")
            return None
        finally:
            self._cleanup_stream()

    def _process_text(self, text):
        words = text.split()

        for word in words:
            if word == "exit":
                return "exit"

            if len(word) == 1 and word.isalpha():
                return word.lower()

        return None

    def _cleanup_stream(self):
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None

    def cleanup(self):
        self._cleanup_stream()
        if self.p:
            try:
                self.p.terminate()
            except:
                pass
