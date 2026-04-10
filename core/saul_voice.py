# core/saul_voice.py
# RVC (Retrieval-Voice-Conversion) voice conversion for Saul
# This provides an alternative to LuxTTS for voice cloning

import torch
import numpy as np
import soundfile as sf


class SaulVoice:
    """
    Voice conversion using RVC (Retrieval-Voice-Conversion).
    Converts any input audio to Saul's voice using a trained RVC model.
    """
    
    def __init__(self, model_path: str, index_path: str = None, device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Lazy import to avoid loading RVC if not used
        try:
            from vc_infer_pipeline import VC
            self.vc = VC(model_path, index_path, device=self.device)
            self.loaded = True
            print(f"[SaulVoice] RVC model loaded on {self.device}")
        except ImportError as e:
            print(f"[SaulVoice] RVC not available: {e}")
            self.vc = None
            self.loaded = False

    def convert(
        self, 
        input_wav_path: str, 
        f0_method: str = "rmvpe",
        index_rate: float = 0.5,
        protect: float = 0.33
    ) -> tuple:
        """
        Convert an input WAV/MP3 file into Saul's voice.
        
        Args:
            input_wav_path: Path to input audio file
            f0_method: Pitch extraction method ("rmvpe", "harvest", "crepe")
            index_rate: Index rate for retrieval (0-1)
            protect: Protection parameter
            
        Returns:
            tuple: (audio_array, sample_rate)
        """
        if not self.loaded or self.vc is None:
            raise RuntimeError("RVC model not loaded")
        
        # Run RVC pipeline
        audio_bytes = self.vc.pipeline(
            input_audio_path=input_wav_path,
            f0_method=f0_method,
            index_rate=index_rate,
            protect=protect
        )
        
        # Convert bytes → numpy array
        audio, sr = sf.read(audio_bytes)
        return audio.astype(np.float32), sr

    def convert_audio(
        self,
        audio: np.ndarray,
        sample_rate: int,
        f0_method: str = "rmvpe",
        index_rate: float = 0.5,
        protect: float = 0.33
    ) -> tuple:
        """
        Convert a numpy audio array into Saul's voice.
        Useful for real-time conversion of TTS output.
        
        Args:
            audio: Input audio as numpy array
            sample_rate: Sample rate of input audio
            f0_method: Pitch extraction method
            index_rate: Index rate for retrieval
            protect: Protection parameter
            
        Returns:
            tuple: (audio_array, sample_rate)
        """
        # Save to temp file, convert, read back
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            sf.write(tmp.name, audio, sample_rate)
            tmp_path = tmp.name
        
        try:
            return self.convert(tmp_path, f0_method, index_rate, protect)
        finally:
            os.unlink(tmp_path)