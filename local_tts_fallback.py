import os
import re
import time
import struct
from pathlib import Path
try:
    import pyttsx3
except Exception:
    print('pyttsx3 not installed. Run: pip install pyttsx3')
    raise

# Load chunks from script.txt
def chunk_text(text, max_chars=1500):
    import re
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) + 2 <= max_chars:
            current = (current + "\n\n" + p).strip()
        else:
            if current:
                chunks.append(current)
            if len(p) <= max_chars:
                current = p
            else:
                sentences = re.split(r'(?<=[.!?])\s+', p)
                cur2 = ""
                for s in sentences:
                    if len(cur2) + len(s) + 1 <= max_chars:
                        cur2 = (cur2 + " " + s).strip()
                    else:
                        if cur2:
                            chunks.append(cur2)
                        cur2 = s
                if cur2:
                    current = cur2
                else:
                    current = ""
    if current:
        chunks.append(current)
    return chunks

SCRIPT = Path('script.txt')
if not SCRIPT.exists():
    print('script.txt not found; cannot proceed')
    raise SystemExit(1)

text = SCRIPT.read_text(encoding='utf-8')
chunks = chunk_text(text, max_chars=1500)
print(f'Chunks total: {len(chunks)}')

# Find missing chunk indices
existing = set()
for p in Path('.').glob('Podcast_Audio_*.wav'):
    m = re.search(r'_(\d+)\.', p.name)
    if m:
        existing.add(int(m.group(1)))
missing = [i for i in range(len(chunks)) if i not in existing]
print('Existing chunks:', sorted(existing))
print('Missing chunks:', missing)
if not missing:
    print('No missing chunks to synthesize locally.')
    raise SystemExit(0)

engine = pyttsx3.init()
# Choose a German voice if present
voices = engine.getProperty('voices')
german_voice = None
for v in voices:
    name = v.name.lower() + ' ' + (getattr(v, 'id', '')).lower()
    if 'german' in name or 'de_' in name or 'de-' in name or 'deu' in name:
        german_voice = v.id
        break
if german_voice:
    engine.setProperty('voice', german_voice)
    print('Using German voice:', german_voice)
else:
    print('German voice not found, using default voice')

rate = engine.getProperty('rate')
engine.setProperty('rate', 150)  # slightly slower for clarity

for idx in missing:
    filename = f'Podcast_Audio_{idx}.wav'
    print(f'Synthesizing chunk {idx} -> {filename} (len={len(chunks[idx])} chars)')
    engine.save_to_file(chunks[idx], filename)
    engine.runAndWait()
    # small pause
    time.sleep(1)
    print('  saved', filename)

# After generating missing pieces, concatenate all chunks
chunk_files = sorted([str(p) for p in Path('.').glob('Podcast_Audio_*.wav') if p.name != 'Podcast_Audio_full.wav'], key=lambda x: int(re.search(r'_(\d+)\.', x).group(1)))
print('Files to concatenate:', chunk_files)

# Read WAV params from first file
with open(chunk_files[0], 'rb') as f:
    hdr = f.read(44)
    num_channels = int.from_bytes(hdr[8:10], 'little')
    sample_rate = int.from_bytes(hdr[24:28], 'little')
    bits_per_sample = int.from_bytes(hdr[34:36], 'little')

audio_data = b''
for cf in chunk_files:
    with open(cf, 'rb') as f:
        f.seek(44)
        audio_data += f.read()

bytes_per_sample = bits_per_sample // 8
block_align = num_channels * bytes_per_sample
byte_rate = sample_rate * block_align
chunk_size = 36 + len(audio_data)

wav_header = struct.pack(
    "<4sI4s4sIHHIIHH4sI",
    b"RIFF", chunk_size, b"WAVE",
    b"fmt ", 16, 1, num_channels, sample_rate, byte_rate, block_align, bits_per_sample,
    b"data", len(audio_data)
)

out_name = 'Podcast_Audio_full.wav'
with open(out_name, 'wb') as out:
    out.write(wav_header + audio_data)
print('✓ Created', out_name)
