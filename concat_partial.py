#!/usr/bin/env python3
"""
Quick concatenation script for partial podcast (skipping missing chunks).
Useful when quota ran out but some chunks were already generated.
"""
import wave
from pathlib import Path
import re

p = Path('.')
files = sorted(p.glob('Podcast_Audio_*.wav'))

if not files:
    print("No Podcast_Audio_*.wav files found!")
    exit(1)

# Sort by numeric index
def index_from_name(fn: Path):
    m = re.search(r'_(\d+)\.', fn.name)
    if m:
        return int(m.group(1))
    return 0

files = sorted(files, key=index_from_name)
print(f"Found {len(files)} chunk files:")
for f in files:
    print(f"  {f.name}")

# Check WAV params
params = None
frames = []
total_size = 0

for fpath in files:
    with wave.open(str(fpath), 'rb') as w:
        p_info = w.getparams()
        if params is None:
            params = p_info
            print(f"\nWAV params: {p_info.nchannels} channels, {p_info.sampwidth} bytes/sample, {p_info.framerate} Hz")
        else:
            if (p_info.nchannels, p_info.sampwidth, p_info.framerate) != (params.nchannels, params.sampwidth, params.framerate):
                print(f"⚠ {fpath.name} has incompatible params, skipping")
                continue
        
        data = w.readframes(w.getnframes())
        frames.append(data)
        total_size += len(data)
        print(f"  ✓ {fpath.name}: {len(data)} bytes")

# Write concatenated file
output_wav = 'Podcast_Audio_full.wav'
print(f"\nConcatenating {len(frames)} chunks ({total_size} bytes) into {output_wav}...")

with wave.open(output_wav, 'wb') as out:
    out.setnchannels(params.nchannels)
    out.setsampwidth(params.sampwidth)
    out.setframerate(params.framerate)
    out.writeframes(b''.join(frames))

print(f"✓ Partial podcast created: {output_wav}")
print(f"  (Note: {len(files)} chunks of {len(files)} total)")
