# modules/speech_input.py
# Offline speech recognition using faster-whisper.
# Uses simple volume threshold for speech detection (no Silero VAD)
# since mic audio is clean and volume-based detection is reliable.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import threading
import queue
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
CHUNK_SIZE = 1600          # 100ms chunks
VOLUME_THRESHOLD = 0.05    # minimum volume to consider as speech
MIN_SPEECH_CHUNKS = 4      # chunks needed to confirm speech started
SILENCE_CHUNKS_TO_STOP = 20  # ~1.5 seconds silence stops recording
MAX_RECORD_CHUNKS = 70     # max ~7 seconds


class SpeechInput:
    def __init__(self, model_size="small", device="cpu", compute_type="int8"):
        print(f"[SpeechInput] Loading Whisper {model_size} model...")
        self._whisper = WhisperModel(model_size, device=device,
                                     compute_type=compute_type)
        print("[SpeechInput] Whisper loaded.")

        self._audio_queue = queue.Queue()
        self._result_queue = queue.Queue()
        self._running = False

    def _is_speech(self, chunk):
        return np.max(np.abs(chunk)) >= VOLUME_THRESHOLD

    def _transcribe(self, audio):
        try:
            segments, _ = self._whisper.transcribe(
                audio, language="en", beam_size=1, vad_filter=True
            )
            text = " ".join(s.text.strip() for s in segments).strip().lower()
            return text if text else None
        except Exception as e:
            print(f"[SpeechInput] Transcription error: {e}")
            return None

    def _audio_callback(self, indata, frames, time, status):
        chunk = indata[:, 0].copy()
        self._audio_queue.put(chunk)

    def _listen_loop(self):
        print("[SpeechInput] Listening for commands...")

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                            dtype='float32', blocksize=CHUNK_SIZE,
                            callback=self._audio_callback):

            recording = []
            speech_count = 0
            silence_count = 0
            is_recording = False

            while self._running:
                try:
                    chunk = self._audio_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                speech = self._is_speech(chunk)

                if not is_recording:
                    if speech:
                        speech_count += 1
                        recording.append(chunk)
                        if speech_count >= MIN_SPEECH_CHUNKS:
                            print("[SpeechInput] Speech detected, recording...")
                            is_recording = True
                            silence_count = 0
                    else:
                        speech_count = 0
                        recording = []
                else:
                    recording.append(chunk)
                    if speech:
                        silence_count = 0
                    else:
                        silence_count += 1

                    if (silence_count >= SILENCE_CHUNKS_TO_STOP or
                            len(recording) >= MAX_RECORD_CHUNKS):

                        print("[SpeechInput] Transcribing...")
                        audio = np.concatenate(recording)
                        text = self._transcribe(audio)

                        if text:
                            print(f"[SpeechInput] Recognized: \"{text}\"")
                            self._result_queue.put(text)
                        else:
                            print("[SpeechInput] No speech recognized.")

                        recording = []
                        speech_count = 0
                        silence_count = 0
                        is_recording = False

    def start(self):
        if self._running:
            return
        self._running = True
        t = threading.Thread(target=self._listen_loop, daemon=True)
        t.start()
        print("[SpeechInput] Listening started.")

    def stop(self):
        self._running = False

    def get_command(self):
        try:
            return self._result_queue.get_nowait()
        except queue.Empty:
            return None


# ---------- Standalone test ----------
if __name__ == "__main__":
    import time
    asr = SpeechInput()
    asr.start()
    print("Speak a command clearly. Ctrl+C to stop.")
    try:
        while True:
            cmd = asr.get_command()
            if cmd:
                print(f"Got command: \"{cmd}\"")
            time.sleep(0.1)
    except KeyboardInterrupt:
        asr.stop()
        print("Stopped.")
