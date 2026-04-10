# core/tts_cache.py
# Synthesizes radio lines using LuxTTS with persistent on-disk cache.
# On first run: synthesizes all lines and saves to disk.
# On subsequent runs: loads from disk (instant startup).

import os
import sys
import re
import hashlib
import threading
import numpy as np
import soundfile as sf
from core.assets import AssetMap


# Add LuxTTS to path
_LUXTTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "LuxTTS")
if os.path.exists(_LUXTTS_PATH):
    sys.path.insert(0, _LUXTTS_PATH)


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
    LuxTTS voice cloning with persistent on-disk cache.
    All static radio lines are pre-cached. Dynamic lines synthesized on first use and cached.
    Subsequent app launches: zero synthesis, all audio loaded instantly from disk.
    """

    CACHE_DIR = "assets/voices/cache"
    SAMPLE_RATE = 24000  # Output sample rate

    def __init__(self, av_manager):
        self._av = av_manager
        self._lux_tts = None
        self._speaker_embedding = None
        self._speaker_wav = AssetMap.get_voice("default")
        self._latents_ready = threading.Event()
        self._animation_enabled = True  # Enable by default

        os.makedirs(self.CACHE_DIR, exist_ok=True)
        
        # Eager loading - pre-load model at startup for instant first response
        self._prime_latents()

    def set_animation_enabled(self, enabled: bool):
        """Enable/disable animation. When disabled, saves CPU/GPU in Engineer mode."""
        self._animation_enabled = enabled
        if not enabled:
            self._av.stop_animation()

    def _ensure_model_loaded(self):
        """Lazy load - load model on first TTS request."""
        if self._latents_ready.is_set():
            return
        self._prime_latents()

    def _prime_latents(self):
        """Load LuxTTS model and encode speaker embedding."""
        try:
            from zipvoice.luxvoice import LuxTTS
            
            self._lux_tts = LuxTTS('YatharthS/LuxTTS', device='cuda')
            
            self._speaker_embedding = self._lux_tts.encode_prompt(self._speaker_wav, rms=0.01)
            
            self._latents_ready.set()
        except Exception as e:
            try:
                from zipvoice.luxvoice import LuxTTS
                self._lux_tts = LuxTTS('YatharthS/LuxTTS', device='cpu', threads=4)
                self._speaker_embedding = self._lux_tts.encode_prompt(self._speaker_wav, rms=0.01)
                self._latents_ready.set()
            except Exception as e2:
                pass

    def preload(self, all_texts: list[str]):
        if not all_texts:
            return
        if not self._latents_ready.wait(timeout=120):
            return

        processed_texts = [_numbers_to_words(t) for t in all_texts]
        missing = [t for t in processed_texts if not os.path.exists(self._cached_path(t))]
        if missing:
            threading.Thread(target=self._background_build, args=(missing,), daemon=True).start()

    def _background_build(self, texts: list[str]):
        self._ensure_model_loaded()
        
        for i, text in enumerate(texts):
            if self._synthesize_and_save(text, num_steps=4):
                pass
        
    def _cached_path(self, text: str) -> str:
        # text should already be processed by _numbers_to_words()
        key = _cache_key(text)
        return os.path.join(self.CACHE_DIR, f"{key}.npy")

    def _synthesize_and_save(self, text: str, num_steps: int = 4) -> bool:
        """Synthesize and save to cache.
        
        Args:
            text: Text to synthesize
            num_steps: 4 = balanced speed/quality
        """
        processed = _numbers_to_words(text)
        
        if not self._latents_ready.wait(timeout=60):
            return False
        
        try:
            wav = self._lux_tts.generate_speech(processed, self._speaker_embedding, num_steps=num_steps)
            wav = wav.numpy().squeeze()
            
            wav_24k = wav[::2]
            
            path = self._cached_path(processed)
            np.save(path, wav_24k)
            
            return True
        except Exception as e:
            print(f"[TTS] Synthesis error for '{text}': {e}")
            return False

    def _synthesize_and_play_background(self, text: str, animation: str | None):
        """Synthesize in background, cache it, then play."""
        self._ensure_model_loaded()  # Lazy load on first use
        
        processed = _numbers_to_words(text)
        if not self._latents_ready.wait(timeout=60):
            return
        try:
            wav = self._lux_tts.generate_speech(processed, self._speaker_embedding, num_steps=4)
            wav = wav.numpy().squeeze()
            wav_24k = wav[::2]
            
            path = self._cached_path(processed)
            np.save(path, wav_24k)
            
            self._av.play_tts_audio(wav_24k, self.SAMPLE_RATE, animation=animation)
        except Exception as e:
            pass

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
        
        # Skip animation if disabled (Engineer mode)
        effective_animation = animation if self._animation_enabled else None
        
        path = self._cached_path(processed)
        if os.path.exists(path):
            # Cache hit - play instantly from disk
            audio = np.load(path)
            self._av.play_tts_audio(audio, self.SAMPLE_RATE, animation=effective_animation)
        else:
            # Cache miss - synthesize in background thread
            # Don't block the main thread
            threading.Thread(
                target=self._synthesize_and_play_background,
                args=(processed, effective_animation),
                daemon=True
            ).start()

    def shutdown(self):
        pass