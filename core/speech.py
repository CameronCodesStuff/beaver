import json
import queue

import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)


class SpeechEngine:
    def __init__(self, model_path, on_partial=None, samplerate=16000):
        self.model = Model(model_path)
        self.samplerate = samplerate
        self.rec = KaldiRecognizer(self.model, samplerate)
        self.rec.SetWords(False)
        self.on_partial = on_partial
        self._q = queue.Queue()

    def _callback(self, indata, frames, time_info, status):
        self._q.put(bytes(indata))

    def results(self):
        with sd.RawInputStream(
            samplerate=self.samplerate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self._callback,
        ):
            while True:
                data = self._q.get()
                if self.rec.AcceptWaveform(data):
                    res = json.loads(self.rec.Result())
                    text = res.get("text", "")
                    if text:
                        yield text
                else:
                    if self.on_partial:
                        pres = json.loads(self.rec.PartialResult())
                        partial = pres.get("partial", "")
                        if partial:
                            self.on_partial(partial)
