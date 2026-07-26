# modules/speech_output.py
# Piper TTS wrapper with speech queue and is_speaking flag.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import queue
import threading
import sounddevice as sd
import numpy as np
from piper import PiperVoice
import config


class SpeechOutput:
    def __init__(self, model_path=None):
        model_path = model_path or config.PIPER_MODEL_PATH
        print(f"[SpeechOutput] Loading Piper voice from {model_path} ...")
        self.voice = PiperVoice.load(model_path)
        print("[SpeechOutput] Piper voice loaded.")

        self._queue = queue.Queue(maxsize=3)
        self._is_speaking = False   # True while audio is playing
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

    @property
    def is_speaking(self):
        return self._is_speaking or not self._queue.empty()

    def speak(self, text):
        """Non-blocking. Adds to queue. Drops if full."""
        if not text:
            return
        try:
            self._queue.put_nowait(text)
        except queue.Full:
            print(f"[SpeechOutput] Queue full, dropping: \"{text}\"")

    def speak_now(self, text):
        """Urgent — clears queue and speaks immediately."""
        if not text:
            return
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
        self._queue.put_nowait(text)

    def _worker_loop(self):
        while True:
            text = self._queue.get()
            self._is_speaking = True
            try:
                self._synthesize_and_play(text)
            except Exception as e:
                print(f"[SpeechOutput] Error: {e}")
            finally:
                self._is_speaking = False
                self._queue.task_done()

    def _synthesize_and_play(self, text):
        print(f"[SpeechOutput] Speaking: \"{text}\"")
        audio_chunks = []
        sample_rate = None
        for chunk in self.voice.synthesize(text):
            audio_chunks.append(chunk.audio_float_array)
            if sample_rate is None:
                sample_rate = chunk.sample_rate
        if not audio_chunks:
            return
        full_audio = np.concatenate(audio_chunks)
        sd.play(full_audio, samplerate=sample_rate)
        sd.wait()


if __name__ == "__main__":
    import time
    tts = SpeechOutput()
    tts.speak("Vision system ready.")
    tts.speak("Person ahead, two metres.")
    time.sleep(10)
