import queue
import threading

import pyttsx3

from core import config


class Speaker:
    def __init__(self):
        self._q = queue.Queue()
        self._speaking = threading.Event()
        self._stop_flag = threading.Event()
        self._sapi = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def is_speaking(self):
        return self._speaking.is_set()

    def _get_sapi(self):
        if self._sapi is None:
            try:
                import win32com.client
                self._sapi = win32com.client.Dispatch("SAPI.SpVoice")
            except Exception:
                self._sapi = False
        return self._sapi

    def _speak_sapi(self, text):
        voice = self._get_sapi()
        if not voice:
            return False
        # 1 = SVSFlagsAsync, 2 = SVSFPurgeBeforeSpeak
        voice.Speak(text, 1)
        while voice.WaitUntilDone(80) is False:
            if self._stop_flag.is_set():
                voice.Speak("", 3)  # async + purge => stop immediately
                return True
        return True

    def _speak_pyttsx(self, text):
        engine = pyttsx3.init()
        engine.setProperty("rate", config.TTS_RATE)
        if config.TTS_VOICE_INDEX is not None:
            voices = engine.getProperty("voices")
            if 0 <= config.TTS_VOICE_INDEX < len(voices):
                engine.setProperty("voice", voices[config.TTS_VOICE_INDEX].id)
        engine.say(text)
        engine.runAndWait()
        try:
            engine.stop()
        except Exception:
            pass

    def _run(self):
        while True:
            text = self._q.get()
            if text is None:
                break
            if self._stop_flag.is_set():
                self._stop_flag.clear()
                continue
            self._speaking.set()
            try:
                # Prefer SAPI because it supports instant interruption
                if not self._speak_sapi(text):
                    self._speak_pyttsx(text)
            except Exception:
                try:
                    self._speak_pyttsx(text)
                except Exception:
                    pass
            self._speaking.clear()
            self._stop_flag.clear()

    def say(self, text):
        if text:
            self._q.put(text)

    def stop(self):
        # Drop anything queued and signal the current utterance to halt
        try:
            while True:
                self._q.get_nowait()
        except queue.Empty:
            pass
        self._stop_flag.set()
