import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.tts_cache import TTSCache, _numbers_to_words
from core.assets import AssetMap

class MockAV:
    """Mock audio/video manager for standalone caching."""
    def play_audio(self, name): pass
    def play_tts_audio(self, audio, sample_rate, animation=None): pass
    def clear_queue(self): pass

def main():
    print("Initializing TTS for caching...")
    
    # Initialize TTS
    av = MockAV()
    tts = TTSCache(av)
    
    # Wait for latents
    print("Waiting for speaker latents...")
    if not tts._latents_ready.wait(timeout=120):
        print("ERROR: Latents not ready within 120 seconds")
        return
    
    print("Speaker latents ready!")
    
    # Load all radio lines including position gain/lost permutations
    from core.radio_lines import RadioLines
    all_lines = list(RadioLines.get_all_static_with_positions())
    all_lines.extend(RadioLines.get_all_f1_mode())
    
    print(f"Found {len(all_lines)} static lines")
    
    # Add the startup line
    all_lines.append("I'm ready, Shawn")
    
    # Process lines through _numbers_to_words to match cache key format
    processed_lines = [_numbers_to_words(line) for line in all_lines]
    
    # Filter to missing (check processed path)
    missing = []
    for proc in processed_lines:
        if not os.path.exists(tts._cached_path(proc)):
            missing.append(proc)
    
    print(f"Need to cache {len(missing)} lines")
    
    if not missing:
        print("All lines already cached!")
        return
    
    # Cache them
    print("Caching lines...")
    for i, text in enumerate(missing):
        tts._synthesize_and_save(text)
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(missing)}")
    
    print(f"Done! Cached {len(missing)} lines")

if __name__ == "__main__":
    main()
