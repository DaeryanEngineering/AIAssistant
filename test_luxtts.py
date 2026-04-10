# test_luxtts.py - Standalone LuxTTS test with Saul's voice
import os
import sys

# Change to project root
os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')

print("="*60)
print("LUXTTS TEST - Voice Cloning for Saul")
print("="*60)

# Add LuxTTS to path
luxtts_path = os.path.join(os.getcwd(), "LuxTTS")
if os.path.exists(luxtts_path):
    sys.path.insert(0, luxtts_path)
    print(f"Added to path: {luxtts_path}")

# Import LuxTTS
print("\nImporting LuxTTS...")
try:
    from zipvoice.luxvoice import LuxTTS
    print("SUCCESS: LuxTTS imported!")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Load model
print("\nLoading LuxTTS model...")
try:
    lux_tts = LuxTTS('YatharthS/LuxTTS', device='cuda')
    print("Loaded on GPU (CUDA)")
except Exception as e:
    print(f"GPU failed ({e}), trying CPU...")
    try:
        lux_tts = LuxTTS('YatharthS/LuxTTS', device='cpu', threads=4)
        print("Loaded on CPU")
    except Exception as e2:
        print(f"CPU failed: {e2}")
        sys.exit(1)

# Encode reference audio
saul_wav = "assets/voices/saul.wav"
if not os.path.exists(saul_wav):
    print(f"ERROR: {saul_wav} not found!")
    sys.exit(1)

print(f"\nEncoding {saul_wav}...")
print("(First encode takes ~10-30 seconds for model download)")
try:
    encoded_prompt = lux_tts.encode_prompt(saul_wav, rms=0.01)
    print("Encoding complete!")
except Exception as e:
    print(f"Encoding failed: {e}")
    sys.exit(1)

# Create output directory
os.makedirs("test_luxtts_output", exist_ok=True)

# Test phrases from Saul's radio lines
test_texts = [
    ("1_greeting", "Hey, what's up?"),
    ("2_deploy_ers", "Deploy ERS, Push now."),
    ("3_box_lap", "Box this lap, Confirm when you're ready."),
    ("4_gap_ahead", "Gap ahead, P2 Hamilton eight tenths."),
    ("5_session_start", "Session starting, Focus."),
    ("6_safety_car", "Safety car deployed."),
    ("7_battery_low", "Battery low, Save ERS."),
    ("8_race_start", "Lights out and away we go."),
]

print("\n" + "="*60)
print("GENERATING TEST SAMPLES")
print("="*60)

import soundfile as sf

for filename, text in test_texts:
    print(f"\n[{filename}] {text}")
    try:
        wav = lux_tts.generate_speech(text, encoded_prompt, num_steps=4)
        wav = wav.numpy().squeeze()
        
        # Convert 48kHz to 24kHz for Saul's system
        wav_24k = wav[::2]  # Take every 2nd sample
        
        output_path = f"test_luxtts_output/{filename}.wav"
        sf.write(output_path, wav_24k, 24000)
        
        duration = len(wav) / 48000
        print(f"    Saved: {output_path} ({duration:.1f}s)")
    except Exception as e:
        print(f"    ERROR: {e}")

print("\n" + "="*60)
print("DONE!")
print("="*60)
print("\nListen to files in test_luxtts_output/")
print("All files are 24kHz WAV format compatible with Saul")
