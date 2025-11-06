#!/usr/bin/env python3
"""Check WAV file headers to diagnose parameter mismatches"""
import struct
from pathlib import Path

def read_wav_header(filepath):
    """Read and parse WAV header information"""
    try:
        with open(filepath, 'rb') as f:
            # Read RIFF header
            riff = f.read(4)
            if riff != b'RIFF':
                return None, f"Not a RIFF file (got {riff})"
            
            file_size = struct.unpack('<I', f.read(4))[0]
            wave = f.read(4)
            if wave != b'WAVE':
                return None, f"Not a WAVE file (got {wave})"
            
            # Find fmt chunk
            while True:
                chunk_id = f.read(4)
                if not chunk_id:
                    return None, "No fmt chunk found"
                chunk_size = struct.unpack('<I', f.read(4))[0]
                
                if chunk_id == b'fmt ':
                    fmt_data = f.read(chunk_size)
                    audio_format = struct.unpack('<H', fmt_data[0:2])[0]
                    num_channels = struct.unpack('<H', fmt_data[2:4])[0]
                    sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
                    byte_rate = struct.unpack('<I', fmt_data[8:12])[0]
                    block_align = struct.unpack('<H', fmt_data[12:14])[0]
                    bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0]
                    
                    return {
                        'audio_format': audio_format,
                        'num_channels': num_channels,
                        'sample_rate': sample_rate,
                        'byte_rate': byte_rate,
                        'block_align': block_align,
                        'bits_per_sample': bits_per_sample,
                        'file_size': file_size
                    }, None
                else:
                    # Skip this chunk
                    f.seek(chunk_size, 1)
    except Exception as e:
        return None, str(e)

# Check chunks 7, 8, 9
for i in [7, 8, 9]:
    filepath = Path(f'Podcast_Audio_{i}.wav')
    if filepath.exists():
        info, error = read_wav_header(filepath)
        print(f"\n{'='*60}")
        print(f"Podcast_Audio_{i}.wav:")
        if error:
            print(f"  ✗ Error: {error}")
        else:
            print(f"  Audio Format: {info['audio_format']} (1=PCM)")
            print(f"  Channels: {info['num_channels']}")
            print(f"  Sample Rate: {info['sample_rate']} Hz")
            print(f"  Bits per Sample: {info['bits_per_sample']}")
            print(f"  Block Align: {info['block_align']}")
            print(f"  Byte Rate: {info['byte_rate']}")
            print(f"  File Size: {info['file_size']} bytes")
    else:
        print(f"\nPodcast_Audio_{i}.wav: NOT FOUND")
