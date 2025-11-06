# To run this code you need to install the following dependencies:
# pip install google-genai

import base64
import mimetypes
import os
import re
import struct
import time
import httpx
import httpcore
import random
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError


def retry_on_rate_limit(func, max_retries=3, base_delay=1):
    """Retry a function with exponential backoff on rate limit errors."""
    for attempt in range(max_retries):
        try:
            return func()
        except ClientError as e:
            if e.status_code == 429:  # Rate limit exceeded
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Rate limit exceeded. Retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    print("Max retries exceeded. Please check your Gemini API quota and billing.")
                    raise e
            else:
                # Re-raise non-rate-limit errors
                raise e


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to: {file_name}")


def convert_to_wav(data: bytes, mime_type: str) -> bytes:
    """
    Convert raw PCM-like audio data into a WAV container by prepending a
    proper RIFF/WAVE header. This handles cases like mime_type "audio/L16;rate=24000"
    where the API returns raw PCM bytes.
    """
    params = parse_audio_mime_type(mime_type)
    bits_per_sample = params.get("bits_per_sample") or 16
    sample_rate = params.get("rate") or 24000
    num_channels = params.get("channels") or 1

    data_size = len(data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        chunk_size,
        b"WAVE",
        b"fmt ",
        16,
        1,  # PCM
        num_channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size,
    )
    return header + data


def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
    """Parse bits per sample and sample rate from an audio MIME type string.

    Examples:
      - "audio/L16;rate=24000"
      - "audio/L16;codec=pcm;rate=24000"

    Returns a dict with keys: bits_per_sample (int), rate (int), channels (int)
    """
    bits_per_sample = 16
    rate = 24000
    channels = 1

    if not mime_type:
        return {"bits_per_sample": bits_per_sample, "rate": rate, "channels": channels}

    parts = [p.strip() for p in mime_type.split(";") if p.strip()]
    for p in parts:
        low = p.lower()
        if low.startswith("rate="):
            try:
                rate = int(p.split("=", 1)[1])
            except Exception:
                pass
        elif low.startswith("audio/l") and "l" in low:
            # e.g. L16
            try:
                bits_per_sample = int(re.split(r"l", low, maxsplit=1)[1])
            except Exception:
                pass
        elif low.startswith("channels=") or low.startswith("ch="):
            try:
                channels = int(p.split("=", 1)[1])
            except Exception:
                pass

    return {"bits_per_sample": bits_per_sample, "rate": rate, "channels": channels}


def get_extension_and_needs_wav(mime_type: str) -> tuple[str, bool]:
    """Return a file extension for the mime_type and whether the raw data
    needs a WAV header (i.e., it's raw PCM like L16) or already a container
    (mp3, ogg, m4a, etc.).
    """
    if not mime_type:
        return ".wav", True
    mt = mime_type.split(";", 1)[0].strip().lower()
    # Common container types
    mapping = {
        "audio/mpeg": (".mp3", False),
        "audio/mp3": (".mp3", False),
        "audio/ogg": (".ogg", False),
        "audio/webm": (".webm", False),
        "audio/mp4": (".m4a", False),
        "audio/x-m4a": (".m4a", False),
        "audio/x-wav": (".wav", False),
        "audio/wav": (".wav", False),
        "audio/wave": (".wav", False),
    }
    if mt in mapping:
        return mapping[mt]

    # Raw PCM / L16 types (these need a WAV header)
    if "l16" in mt or "audio/l" in mt or "pcm" in mt or mt.startswith("audio/l"):
        return ".wav", True

    # Fallback: try python's mimetypes
    ext = mimetypes.guess_extension(mt)
    if ext:
        return ext, False

    # Default to wav + add header
    return ".wav", True


def generate():
    print("\n" + "="*60)
    print("PODCAST GENERATION STARTED")
    print("="*60)
    
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )
    print("✓ Gemini API client initialized")

    model = "models/gemini-2.5-pro-preview-tts"
    print(f"✓ Using model: {model}")
    
    # Load full text from script.txt
    try:
        with open("script.txt", "r", encoding="utf-8") as f:
            full_text = f.read()
        print(f"✓ Loaded script.txt ({len(full_text)} characters)")
    except FileNotFoundError:
        print("✗ Error: script.txt not found. Please create script.txt with the podcast content.")
        raise
    # Chunking helper: split by paragraphs and sentences to keep chunk size reasonable
    def chunk_text(text, max_chars=3000):
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

    chunks = chunk_text(full_text, max_chars=1500)
    print(f"✓ Text split into {len(chunks)} chunks (max 1500 chars each)")
    for i, c in enumerate(chunks[:3]):  # Show first 3 chunk sizes
        print(f"  Chunk {i+1}: {len(c)} chars")
    if len(chunks) > 3:
        print(f"  ... and {len(chunks)-3} more chunks")

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        response_modalities=["audio"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker="Speaker 1",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Sulafat"
                            )
                        ),
                    ),
                    types.SpeakerVoiceConfig(
                        speaker="Speaker 2",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Sadachbia"
                            )
                        ),
                    ),
                ]
            ),
        ),
    )
    print("✓ TTS configuration created (Speaker 1: Sulafat, Speaker 2: Sadachbia)")

    file_index = 0
    print("\n" + "-"*60)
    print("GENERATING AUDIO CHUNKS")
    print("-"*60)

    # Iterate chunks and call API per chunk with robust streaming + fallback to non-streaming
    for idx, chunk_text_item in enumerate(chunks):
        print(f"\n[{idx+1}/{len(chunks)}] Processing chunk (len={len(chunk_text_item)} chars)...")
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=chunk_text_item)])]
        # Try streaming with retries and jitter
        stream_attempts = 0
        max_stream_attempts = 10  # Increased from 5 to 10
        while stream_attempts < max_stream_attempts:
            try:
                stream = client.models.generate_content_stream(model=model, contents=contents, config=generate_content_config)
                for chunk in stream:
                    if (
                        chunk.candidates is None
                        or chunk.candidates[0].content is None
                        or chunk.candidates[0].content.parts is None
                    ):
                        continue
                    if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
                        file_name = f"Podcast_Audio_{file_index}"
                        file_index += 1
                        inline_data = chunk.candidates[0].content.parts[0].inline_data
                        data_buffer = inline_data.data
                        file_extension, needs_wav = get_extension_and_needs_wav(inline_data.mime_type)
                        if needs_wav:
                            # Add WAV header around raw PCM bytes
                            data_buffer = convert_to_wav(inline_data.data, inline_data.mime_type)
                        save_binary_file(f"{file_name}{file_extension}", data_buffer)
                    else:
                        print(chunk.text)
                # success for this chunk
                print(f"  ✓ Chunk {idx+1} completed successfully (stream)")
                break
            except (httpx.RemoteProtocolError, httpcore.RemoteProtocolError) as e:
                stream_attempts += 1
                # Use non-streaming fallback sooner (after just 2 streaming attempts)
                if stream_attempts >= 2:
                    print(f"  ⚠ Stream disconnect {stream_attempts} times — switching to non-streaming fallback")
                    try:
                        resp = client.models.generate_content(model=model, contents=contents, config=generate_content_config)
                        # extract inline_data from resp if present
                        if getattr(resp, 'candidates', None):
                            cand = resp.candidates[0]
                            content = getattr(cand, 'content', None)
                            if content and getattr(content, 'parts', None):
                                part0 = content.parts[0]
                                if getattr(part0, 'inline_data', None) and getattr(part0.inline_data, 'data', None):
                                    inline = part0.inline_data
                                    file_name = f"Podcast_Audio_{file_index}"
                                    file_index += 1
                                    data_buffer = inline.data
                                    file_extension, needs_wav = get_extension_and_needs_wav(inline.mime_type)
                                    if needs_wav:
                                        data_buffer = convert_to_wav(inline.data, inline.mime_type)
                                    save_binary_file(f"{file_name}{file_extension}", data_buffer)
                                    print(f"  ✓ Chunk {idx+1} completed successfully (non-streaming fallback)")
                                    break
                        print("Non-streaming response did not contain audio inline_data; see response repr: ", repr(resp))
                        break
                    except ClientError as ce:
                        print("Fallback ClientError:", ce)
                        raise
                    except Exception as e2:
                        print("Fallback non-streaming failed:", e2)
                        raise
                else:
                    # Shorter retry delay for streaming attempts
                    delay = 2 + random.uniform(0, 1)
                    print(f"  ⚠ Stream disconnect (attempt {stream_attempts}/2): retrying in {delay:.1f}s...")
                    time.sleep(delay)
            except ClientError as ce:
                # API error like quota or invalid key
                status = getattr(ce, 'status_code', 'N/A')
                error_msg = getattr(ce, 'error', getattr(ce, 'args', None))
                print(f"  ✗ API error {status}: {error_msg}")
                if status == 429:
                    # Rate limit: wait longer before retrying
                    stream_attempts += 1
                    delay = (5 ** stream_attempts) + random.uniform(0, 2)
                    print(f"  ⚠ Rate limited (quota exceeded). Waiting {delay:.1f}s before retry (attempt {stream_attempts}/{max_stream_attempts})")
                    time.sleep(delay)
                    if stream_attempts < max_stream_attempts:
                        continue
                raise
            except Exception as e:
                stream_attempts += 1
                delay = (3 ** stream_attempts) + random.uniform(0, 1)
                print(f"  ⚠ Unexpected error: {str(e)[:80]}... Retry in {delay:.1f}s (attempt {stream_attempts}/{max_stream_attempts})")
                time.sleep(delay)
                if stream_attempts >= max_stream_attempts:
                    raise

            # small pause between chunks
        time.sleep(0.6)
    print("\n" + "-"*60)
    print("CONCATENATING AUDIO CHUNKS")
    print("-"*60)
    import subprocess
    from pathlib import Path
    import wave
    
    p = Path('.')
    files = sorted(p.glob('Podcast_Audio_*.*'))
    if not files:
        print("✗ No chunk files found!")
        return
    
    # Sort by numeric index
    def index_from_name(fn: Path):
        m = re.search(r'_(\d+)\.', fn.name)
        if m:
            return int(m.group(1))
        return 0
    
    files = sorted(files, key=index_from_name)
    print(f"✓ Found {len(files)} chunk files to concatenate")
    for f in files:
        print(f"    {f.name}")
    
    # Try ffmpeg first
    ffmpeg = None
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=2)
        if result.returncode == 0:
            ffmpeg = True
            print("✓ ffmpeg found — using for optimal concatenation")
    except Exception:
        print("⚠ ffmpeg not found — falling back to pure Python WAV concatenation")
    
    if ffmpeg:
        list_file = 'ff_concat_list.txt'
        with open(list_file, 'w', encoding='utf-8') as f:
            for file in files:
                f.write(f"file '{file}'\n")
        output_wav = 'Podcast_Audio_full.wav'
        cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', list_file,
               '-vn', '-acodec', 'pcm_s16le', '-ar', '24000', '-ac', '1', output_wav]
        print(f"Running ffmpeg to produce {output_wav}...")
        subprocess.run(cmd, check=False)
        print(f"✓ Final podcast created: {output_wav}")
    else:
        # Pure Python WAV concatenation
        def is_wav_file(path: Path):
            try:
                with wave.open(str(path), 'rb') as w:
                    return True
            except Exception:
                return False
        
        wav_files = [f for f in files if is_wav_file(f)]
        if len(wav_files) != len(files):
            print(f"⚠ Warning: {len(files) - len(wav_files)} files are not valid WAV, concatenating {len(wav_files)} valid files")
            files = wav_files
        
        if not files:
            print("✗ No valid WAV files to concatenate!")
            return
        
        # Check params
        params = None
        frames = []
        total_size = 0
        for fpath in files:
            with wave.open(str(fpath), 'rb') as w:
                p = w.getparams()
                if params is None:
                    params = p
                    print(f"✓ WAV params: {p.nchannels} channels, {p.sampwidth} bytes/sample, {p.framerate} Hz")
                else:
                    if (p.nchannels, p.sampwidth, p.framerate) != (params.nchannels, params.sampwidth, params.framerate):
                        print(f"⚠ Warning: {fpath} has incompatible params, skipping.")
                        continue
                data = w.readframes(w.getnframes())
                frames.append(data)
                total_size += len(data)
                print(f"    {fpath.name}: {len(data)} bytes")
        
        output_wav = 'Podcast_Audio_full.wav'
        print(f"Creating {output_wav} with {total_size} bytes of audio data...")
        with wave.open(output_wav, 'wb') as out:
            out.setnchannels(params.nchannels)
            out.setsampwidth(params.sampwidth)
            out.setframerate(params.framerate)
            out.writeframes(b''.join(frames))
        print(f"✓ Final podcast created: {output_wav}")


if __name__ == "__main__":
    # Load .env (if present) and ensure GEMINI_API_KEY is available
    load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        print("✗ GEMINI_API_KEY not found in environment. Please add it to a .env file or export it as an environment variable.")
    else:
        print("✓ GEMINI_API_KEY found in environment")
        try:
            # Clean up old chunk files before regenerating
            import glob
            old_files = glob.glob("Podcast_Audio_*")
            if old_files:
                print(f"\nCleaning up {len(old_files)} old chunk files...")
                for old_file in old_files:
                    try:
                        os.remove(old_file)
                        print(f"  Removed: {old_file}")
                    except Exception as e:
                        print(f"  ✗ Could not remove {old_file}: {e}")
            
            generate()
            print("\n" + "="*60)
            print("✓ PODCAST GENERATION COMPLETE!")
            print("="*60)
        except Exception as e:
            print("\n" + "="*60)
            print(f"✗ ERROR: {e}")
            print("="*60)
            import traceback
            traceback.print_exc()
