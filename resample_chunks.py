#!/usr/bin/env python3
"""Resample chunks 8 and 9 from 22050 Hz to 24000 Hz to match other chunks"""
import struct
import array

def resample_audio(input_file, output_file, target_rate=24000):
    """Resample a WAV file to target sample rate using linear interpolation"""
    
    # Read input WAV
    with open(input_file, 'rb') as f:
        # Read header (44 bytes)
        header = f.read(44)
        
        # Parse key params
        num_channels = struct.unpack('<H', header[22:24])[0]
        source_rate = struct.unpack('<I', header[24:28])[0]
        bits_per_sample = struct.unpack('<H', header[34:36])[0]
        
        print(f"Input: {input_file}")
        print(f"  Source rate: {source_rate} Hz")
        print(f"  Target rate: {target_rate} Hz")
        print(f"  Channels: {num_channels}")
        print(f"  Bits per sample: {bits_per_sample}")
        
        # Read audio data
        audio_data = f.read()
    
    # Convert bytes to samples
    if bits_per_sample == 16:
        samples = array.array('h')  # signed short
        samples.frombytes(audio_data)
    else:
        raise ValueError(f"Unsupported bits per sample: {bits_per_sample}")
    
    # Resample using linear interpolation
    ratio = source_rate / target_rate
    num_output_samples = int(len(samples) / ratio)
    resampled = array.array('h')
    
    for i in range(num_output_samples):
        # Calculate source position
        src_pos = i * ratio
        src_idx = int(src_pos)
        
        # Linear interpolation
        if src_idx + 1 < len(samples):
            frac = src_pos - src_idx
            sample = samples[src_idx] * (1 - frac) + samples[src_idx + 1] * frac
            resampled.append(int(sample))
        elif src_idx < len(samples):
            resampled.append(samples[src_idx])
    
    # Create new WAV with resampled data
    resampled_bytes = resampled.tobytes()
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = target_rate * block_align
    chunk_size = 36 + len(resampled_bytes)
    
    new_header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        chunk_size,
        b"WAVE",
        b"fmt ",
        16,
        1,  # PCM
        num_channels,
        target_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        len(resampled_bytes),
    )
    
    # Write output
    with open(output_file, 'wb') as f:
        f.write(new_header + resampled_bytes)
    
    print(f"  ✓ Resampled to {target_rate} Hz: {output_file}")
    print(f"  Output samples: {len(resampled)}")
    print()

# Resample chunks 8 and 9
for i in [8, 9]:
    input_file = f'Podcast_Audio_{i}.wav'
    output_file = f'Podcast_Audio_{i}_resampled.wav'
    resample_audio(input_file, output_file, target_rate=24000)
    
    # Replace original with resampled
    import os
    os.replace(output_file, input_file)
    print(f"  ✓ Replaced {input_file} with resampled version\n")

print("="*60)
print("✓ Resampling complete!")
print("All chunks now use 24000 Hz sample rate")
