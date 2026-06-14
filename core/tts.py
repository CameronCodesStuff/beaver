import queue
import threading

import pyttsx3

from core import config


class Speaker:
    def __init__(self):
        self._q = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        engine = pyttsx3.init()
        engine.setProperty("rate", config.TTS_RATE)
        if config.TTS_VOICE_INDEX is not None:
            voices = engine.getProperty("voices")
            if 0 <= config.TTS_VOICE_INDEX < len(voices):
                engine.setProperty("voice", voices[config.TTS_VOICE_INDEX].id)
        while True:
            text = self._q.get()
            if text is None:
                break
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception:
                pass

    def say(self, text):
        if text:
            self._q.put(text)
