import os
import re
import subprocess
import shutil
import sys
from pathlib import Path

# Find generated audio chunks
p = Path('.')
files = sorted(p.glob('IVSC_Podcast_German_Audio_*.*'))
if not files:
    print('No IVSC_Podcast_German_Audio_* files found. Run IVSC_Podcast_German.py first.')
    sys.exit(1)

# Sort by numeric index in filename
def index_from_name(fn: Path):
    m = re.search(r'_(\d+)\.', fn.name)
    if m:
        return int(m.group(1))
    # fallback: return 0
    return 0

files = sorted(files, key=index_from_name)
print('Found chunk files:', [f.name for f in files])

# Detect ffmpeg
ffmpeg = shutil.which('ffmpeg')
output_wav = 'IVSC_Podcast_German_full.wav'
output_mp3 = 'IVSC_Podcast_German_full.mp3'

if ffmpeg:
    print('ffmpeg found at', ffmpeg)
    # Create concat list file
    list_file = 'ff_concat_list.txt'
    with open(list_file, 'w', encoding='utf-8') as f:
        for file in files:
            # ffmpeg concat list expects: file 'path'
            f.write("file '{}\n".format(str(file).replace("'", "'\\''")))
    # Try to create WAV with consistent sample rate and channels by re-encoding
    cmd = [ffmpeg, '-y', '-f', 'concat', '-safe', '0', '-i', list_file,
           '-vn', '-acodec', 'pcm_s16le', '-ar', '24000', '-ac', '1', output_wav]
    print('Running ffmpeg to produce', output_wav)
    try:
        subprocess.run(cmd, check=True)
        print('Created', output_wav)
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print('ffmpeg failed to create WAV:', e)
        print('Trying to produce MP3 instead...')
        cmd2 = [ffmpeg, '-y', '-f', 'concat', '-safe', '0', '-i', list_file,
                '-vn', '-acodec', 'libmp3lame', '-b:a', '192k', output_mp3]
        try:
            subprocess.run(cmd2, check=True)
            print('Created', output_mp3)
            sys.exit(0)
        except subprocess.CalledProcessError as e2:
            print('ffmpeg also failed for MP3:', e2)
            sys.exit(2)
else:
    print('ffmpeg not found. Attempting pure-Python WAV concat if all chunks are WAV with matching params.')
    import wave

    def is_wav_file(path: Path):
        try:
            with wave.open(str(path), 'rb') as w:
                return True
        except Exception:
            return False

    wav_files = [f for f in files if is_wav_file(f)]
    if len(wav_files) != len(files):
        print('Not all chunk files are WAV or some are unreadable. Please install ffmpeg and rerun this script.')
        sys.exit(3)

    # Check params
    params = None
    frames = []
    total_frames = 0
    for fpath in wav_files:
        with wave.open(str(fpath), 'rb') as w:
            p = w.getparams()
            if params is None:
                params = p
            else:
                # Compare channels, sampwidth, framerate
                if (p.nchannels, p.sampwidth, p.framerate) != (params.nchannels, params.sampwidth, params.framerate):
                    print('Incompatible WAV params between files. Install ffmpeg to re-encode and concatenate.')
                    sys.exit(4)
            data = w.readframes(w.getnframes())
            frames.append(data)
            total_frames += w.getnframes()

    # Write concatenated wav
    out = wave.open(output_wav, 'wb')
    out.setnchannels(params.nchannels)
    out.setsampwidth(params.sampwidth)
    out.setframerate(params.framerate)
    out.writeframes(b''.join(frames))
    out.close()
    print('Created', output_wav, 'by pure-Python concatenation')
    sys.exit(0)
