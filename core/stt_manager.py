# core/stt_manager.py

import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

class VoskSTTManager:
    """
    PTT-only speech recognizer with a simple wake-word ("Saul") inside PTT.
    States:
        IDLE        - not listening
        AWAIT_WAKE  - listening but waiting for "Saul"
        IN_COMMAND  - wake-word detected, now capturing commands
    """

    WAKE_VARIANTS = {
        "saul", "saw", "sol", "soul", "so", "sal", "sell", "sahl"
    }

    def __init__(self, model_path, samplerate=16000, blocksize=8000):
        self.model = Model(model_path)
        self.samplerate = samplerate
        self.blocksize = blocksize

        self.recognizer = None
        self.stream = None

        self.state = "IDLE"
        self.command_queue = queue.Queue()

        self._listening = False

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def begin_ptt(self):
        """Call when PTT is pressed."""
        if self._listening:
            return

        self._listening = True
        self.state = "AWAIT_WAKE"
        self._start_stream()

    def end_ptt(self):
        """Call when PTT is released."""
        if not self._listening:
            return

        self._stop_stream()
        self._listening = False
        self.state = "IDLE"

    def get_command_nowait(self):
        """Non-blocking retrieval of recognized commands."""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None

    # ---------------------------------------------------------
    # Audio stream
    # ---------------------------------------------------------

    def _start_stream(self):
        self.recognizer = KaldiRecognizer(self.model, self.samplerate)

        def callback(indata, frames, time, status):
            data = bytes(indata)

            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = (result.get("text") or "").strip()
                if text:
                    self._handle_final(text)
            else:
                partial = json.loads(self.recognizer.PartialResult())
                text = (partial.get("partial") or "").strip()
                if text:
                    self._handle_partial(text)

        self.stream = sd.RawInputStream(
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            dtype="int16",
            channels=1,
            callback=callback,
        )
        self.stream.start()

    def _stop_stream(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.recognizer = None

    # ---------------------------------------------------------
    # Wake-word + command logic
    # ---------------------------------------------------------

    def _handle_partial(self, text):
        if self.state == "AWAIT_WAKE":
            if self._contains_saul(text):
                self.state = "IN_COMMAND"

    def _handle_final(self, text):
        if self.state == "AWAIT_WAKE":
            if self._contains_saul(text):
                after = self._text_after_saul(text)
                if after:
                    self._emit_command(after)
                else:
                    self.state = "IN_COMMAND"
        elif self.state == "IN_COMMAND":
            self._emit_command(text)

    def _emit_command(self, text):
        cleaned = text.strip()
        if cleaned:
            self.command_queue.put(cleaned)
        self.state = "AWAIT_WAKE"

    # ---------------------------------------------------------
    # Wake-word helpers
    # ---------------------------------------------------------

    def _contains_saul(self, text):
        tokens = text.lower().split()
        return any(tok in self.WAKE_VARIANTS for tok in tokens)

    def _text_after_saul(self, text):
        tokens = text.lower().split()
        original = text.split()

        for i, tok in enumerate(tokens):
            if tok in self.WAKE_VARIANTS:
                return " ".join(original[i + 1:])
        return ""
