# core/tts_cache.py
# Synthesizes radio lines using XTTS v2 with persistent on-disk cache.
# On first run: synthesizes all lines and saves to disk.
# On subsequent runs: loads from disk (instant startup).

import os
import re
import hashlib
import threading
import numpy as np
from TTS.api import TTS
from core.assets import AssetMap


def _numbers_to_words(text: str) -> str:
    def _replace_num(m):
        val = m.group(0)
        try:
            num = float(val)
        except ValueError:
            return val
        if '.' in val:
            whole, frac = val.split('.', 1)
            whole_w = _int_to_words(int(whole)) if whole else 'zero'
            frac_w = ' '.join(_DIGIT_WORDS[int(d)] for d in frac if d.isdigit())
            return f"{whole_w} point {frac_w}"
        return _int_to_words(int(num))

    text = re.sub(r'\bP(\d+)\b', lambda m: f"P {_int_to_words(int(m.group(1)))}", text)
    text = re.sub(r'\d+\.?\d*', _replace_num, text)
    return text


_DIGIT_WORDS = ['zero', 'one', 'two', 'three', 'four',
                'five', 'six', 'seven', 'eight', 'nine']


def _int_to_words(n: int) -> str:
    if n == 0:
        return 'zero'
    if n < 0:
        return 'minus ' + _int_to_words(-n)
    parts = []
    for label, div in [('trillion', 1_000_000_000_000),
                       ('billion', 1_000_000_000),
                       ('million', 1_000_000),
                       ('thousand', 1_000),
                       ('hundred', 100)]:
        if n >= div:
            parts.append(_int_to_words(n // div))
            parts.append(label)
            n %= div
    ones = ['', 'one', 'two', 'three', 'four', 'five', 'six',
            'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve',
            'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen',
            'eighteen', 'nineteen']
    tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty',
            'sixty', 'seventy', 'eighty', 'ninety']
    if n >= 20:
        parts.append(tens[n // 10] + ('' if n % 10 == 0 else '-' + ones[n % 10]))
    elif n > 0:
        parts.append(ones[n])
    return ' '.join(parts)


def _cache_key(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


class TTSCache:
    """
    XTTS v2 TTS with persistent on-disk cache.
    All static radio lines are pre-cached. Dynamic lines synthesized on first use and cached.
    Subsequent app launches: zero synthesis, all audio loaded instantly from disk.
    """

    CACHE_DIR = "assets/voices/cache"

    def __init__(self, av_manager):
        self._av = av_manager
        self._model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        self._speaker_wav = AssetMap.get_voice("default")
        self._gpt_latent = None
        self._spk_embedding = None
        self._latents_ready = threading.Event()

        os.makedirs(self.CACHE_DIR, exist_ok=True)
        threading.Thread(target=self._prime_latents, daemon=True).start()

    def _prime_latents(self):
        try:
            xtts = self._model.synthesizer.tts_model
            gpt, spk = xtts.get_conditioning_latents(audio_path=self._speaker_wav)
            self._gpt_latent = gpt
            self._spk_embedding = spk
            self._latents_ready.set()
            print("[TTS] Speaker latents ready")
        except Exception as e:
            print(f"[TTS] Failed to prime latents: {e}")

    def preload(self, all_texts: list[str]):
        if not all_texts:
            return
        if not self._latents_ready.wait(timeout=60):
            print("[TTS] Latents not ready, skipping preload")
            return

        missing = [t for t in all_texts if not os.path.exists(self._cached_path(t))]
        if missing:
            print(f"[TTS] Caching {len(missing)} static lines in background...")
            threading.Thread(target=self._background_build, args=(missing,), daemon=True).start()
        else:
            print(f"[TTS] All {len(all_texts)} static lines loaded from disk (instant)")

    def _background_build(self, texts: list[str]):
        for i, text in enumerate(texts):
            self._synthesize_and_save(text)
            if (i + 1) % 50 == 0:
                print(f"[TTS] Cache build: {i+1}/{len(texts)}")
        print(f"[TTS] Cache build complete: {len(texts)} lines")

    def _cached_path(self, text: str) -> str:
        key = _cache_key(_numbers_to_words(text))
        return os.path.join(self.CACHE_DIR, f"{key}.npy")

    def _synthesize_and_save(self, text: str) -> bool:
        processed = _numbers_to_words(text)
        key = _cache_key(processed)
        path = os.path.join(self.CACHE_DIR, f"{key}.npy")
        if os.path.exists(path):
            return True
        try:
            result = self._model.synthesizer.tts_model.inference(
                processed, "en", self._gpt_latent, self._spk_embedding,
            )
            audio = np.array(result["wav"], dtype=np.float32)
            np.save(path, audio)
            return True
        except Exception as e:
            print(f"[TTS] Synthesis error for '{text}': {e}")
            return False

    def speak(
        self,
        text: str,
        *,
        priority: bool = False,
        radio: bool = False,
        play_beep: bool = False,
        animation: str | None = None,
    ) -> None:
        if not text:
            return
        processed = _numbers_to_words(text)
        if priority:
            self._av.clear_queue()
        if play_beep:
            self._av.play_audio("radio_beep")
        path = self._cached_path(processed)
        if os.path.exists(path):
            audio = np.load(path)
            self._av.play_tts_audio(audio, 24000, animation=animation)
        else:
            self._synthesize_and_save(processed)
            path = self._cached_path(processed)
            if os.path.exists(path):
                audio = np.load(path)
                self._av.play_tts_audio(audio, 24000, animation=animation)

    def shutdown(self):
        pass
