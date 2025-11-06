#!/usr/bin/env python3
"""
Generate only missing Podcast_Audio_{i}.wav chunks and concatenate into Podcast_Audio_full.wav.
This uses conservative pacing to avoid rate limits: small chunk sizes, short retries, and delays between chunks.
"""
import os
import re
import time
import struct
from pathlib import Path
from dotenv import load_dotenv

# Load AI client lazily to fail fast if no key
load_dotenv()
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("✗ GEMINI_API_KEY not set in environment (.env). Aborting.")
    raise SystemExit(1)

try:
    from google import genai
    from google.genai import types
    from google.genai.errors import ClientError
except Exception as e:
    print("✗ Could not import google-genai client. Make sure it's installed in the venv:")
    print("  pip install google-genai")
    raise

# Simple chunking logic (same approach as main script)
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

# Read script
SCRIPT_PATH = Path("script.txt")
if not SCRIPT_PATH.exists():
    print("✗ script.txt not found in project root. Please add it and try again.")
    raise SystemExit(1)

full_text = SCRIPT_PATH.read_text(encoding="utf-8")
chunks = chunk_text(full_text, max_chars=1500)
print(f"✓ Script loaded ({len(full_text)} chars) -> {len(chunks)} chunks")

# Determine missing chunks
existing = set()
for p in Path('.').glob('Podcast_Audio_*.wav'):
    m = re.search(r'_(\d+)\.', p.name)
    if m:
        existing.add(int(m.group(1)))

missing = [i for i in range(len(chunks)) if i not in existing]
print(f"✓ Existing chunks: {sorted(list(existing))}")
print(f"⚠ Missing chunks: {missing}")
if not missing:
    print("All chunks already present — nothing to generate.")
else:
    client = genai.Client(api_key=API_KEY)
    model = "models/gemini-2.5-pro-preview-tts"

    # Reuse the same TTS config as main script
    # WICHTIG: multi_speaker_voice_config erfordert IMMER genau 2 Speaker!
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        response_modalities=["audio"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker="Speaker 1",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Sulafat")
                        ),
                    ),
                    types.SpeakerVoiceConfig(
                        speaker="Speaker 2",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Sadachbia")
                        ),
                    ),
                ]
            ),
        ),
    )
    print("✓ TTS config erstellt (Speaker 1: Sulafat, Speaker 2: Sadachbia)")

    for idx in missing:
        text_chunk = chunks[idx]
        print('\n' + '='*60)
        print(f"[{idx+1}/{len(chunks)}] Generating chunk {idx} (len={len(text_chunk)} chars)")

        contents = [types.Content(role="user", parts=[types.Part.from_text(text=text_chunk)])]

        # We'll attempt streaming once; if it fails, fallback to non-streaming immediately
        try:
            stream = None
            try:
                stream = client.models.generate_content_stream(model=model, contents=contents, config=generate_content_config)
                # collect inline data from the first audio part we find
                saved = False
                for part in stream:
                    if (getattr(part, 'candidates', None) and
                        getattr(part.candidates[0].content, 'parts', None)):
                        p0 = part.candidates[0].content.parts[0]
                        if getattr(p0, 'inline_data', None) and getattr(p0.inline_data, 'data', None):
                            filename = f"Podcast_Audio_{idx}.wav"
                            data = p0.inline_data.data
                            mime_type = getattr(p0.inline_data, 'mime_type', 'audio/wav')
                            
                            # Check if we need to add WAV header for raw PCM
                            if 'l16' in mime_type.lower() or 'pcm' in mime_type.lower():
                                print(f"  ℹ Raw PCM detected ({mime_type}), adding WAV header...")
                                # Parse audio params and create WAV header
                                import struct
                                params = {'bits_per_sample': 16, 'rate': 24000, 'channels': 1}
                                if 'rate=' in mime_type:
                                    params['rate'] = int(mime_type.split('rate=')[1].split(';')[0].split(',')[0])
                                
                                data_size = len(data)
                                bytes_per_sample = params['bits_per_sample'] // 8
                                block_align = params['channels'] * bytes_per_sample
                                byte_rate = params['rate'] * block_align
                                chunk_size = 36 + data_size
                                
                                header = struct.pack(
                                    "<4sI4s4sIHHIIHH4sI",
                                    b"RIFF", chunk_size, b"WAVE",
                                    b"fmt ", 16, 1, params['channels'], params['rate'], 
                                    byte_rate, block_align, params['bits_per_sample'],
                                    b"data", data_size
                                )
                                data = header + data
                            
                            with open(filename, 'wb') as f:
                                f.write(data)
                            print(f"  ✓ Saved chunk {idx} -> {filename}")
                            saved = True
                            break
                if saved:
                    # polite pacing
                    print("  ⏱ Waiting 3s before next chunk")
                    time.sleep(3)
                    continue
                else:
                    print("  ⚠ Streaming returned no inline audio — trying non-streaming fallback")
            except Exception as e_stream:
                print(f"  ⚠ Stream attempt failed: {str(e_stream)[:200]}")

            # Non-streaming fallback
            try:
                resp = client.models.generate_content(model=model, contents=contents, config=generate_content_config)
                if getattr(resp, 'candidates', None):
                    cand = resp.candidates[0]
                    content = getattr(cand, 'content', None)
                    if content and getattr(content, 'parts', None):
                        p0 = content.parts[0]
                        if getattr(p0, 'inline_data', None) and getattr(p0.inline_data, 'data', None):
                            filename = f"Podcast_Audio_{idx}.wav"
                            data = p0.inline_data.data
                            mime_type = getattr(p0.inline_data, 'mime_type', 'audio/wav')
                            
                            # Check if we need to add WAV header for raw PCM
                            if 'l16' in mime_type.lower() or 'pcm' in mime_type.lower():
                                print(f"  ℹ Raw PCM detected ({mime_type}), adding WAV header...")
                                import struct
                                params = {'bits_per_sample': 16, 'rate': 24000, 'channels': 1}
                                if 'rate=' in mime_type:
                                    params['rate'] = int(mime_type.split('rate=')[1].split(';')[0].split(',')[0])
                                
                                data_size = len(data)
                                bytes_per_sample = params['bits_per_sample'] // 8
                                block_align = params['channels'] * bytes_per_sample
                                byte_rate = params['rate'] * block_align
                                chunk_size = 36 + data_size
                                
                                header = struct.pack(
                                    "<4sI4s4sIHHIIHH4sI",
                                    b"RIFF", chunk_size, b"WAVE",
                                    b"fmt ", 16, 1, params['channels'], params['rate'], 
                                    byte_rate, block_align, params['bits_per_sample'],
                                    b"data", data_size
                                )
                                data = header + data
                            
                            with open(filename, 'wb') as f:
                                f.write(data)
                            print(f"  ✓ Saved chunk {idx} -> {filename} (fallback)")
                            print("  ⏱ Waiting 3s before next chunk")
                            time.sleep(3)
                            continue
                print(f"  ✗ Non-streaming response did not contain audio for chunk {idx}; response: {repr(resp)[:300]}")
            except ClientError as ce:
                status = getattr(ce, 'status_code', 'N/A')
                print(f"  ✗ ClientError status={status}: {ce}")
                if status == 429:
                    print("  ✗ Quota/rate limit hit (429). Stop generating further chunks.")
                    break
                else:
                    print("  ✗ Unexpected ClientError — aborting")
                    break
            except Exception as e2:
                print(f"  ✗ Non-streaming fallback failed: {e2}")
                break

        except Exception as e:
            print(f"  ✗ Failed to generate chunk {idx}: {e}")
            # if it's a quota error we likely saw it above; stop
            break

# After attempting missing chunks, run concat (reuse concat_partial logic)
print('\n' + '='*60)
print('Attempting to concatenate available chunk files into Podcast_Audio_full.wav')
# gather chunk filenames in order
chunk_files = sorted([str(p) for p in Path('.').glob('Podcast_Audio_*.wav') if p.name != 'Podcast_Audio_full.wav'], key=lambda x: int(re.search(r'_(\d+)\.', x).group(1)))
if not chunk_files:
    print('No chunk files to concatenate. Exiting.')
    raise SystemExit(0)

# Read WAV params from first file
with open(chunk_files[0], 'rb') as f:
    hdr = f.read(44)
    num_channels = int.from_bytes(hdr[8:10], 'little')
    sample_rate = int.from_bytes(hdr[24:28], 'little')
    bits_per_sample = int.from_bytes(hdr[34:36], 'little')

# concatenate raw data
audio_data = b''
for cf in chunk_files:
    with open(cf, 'rb') as f:
        f.seek(44)
        data = f.read()
        audio_data += data

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

print(f"✓ Concatenation complete: {out_name} (contained {len(chunk_files)} chunks)")
print('Done.')
