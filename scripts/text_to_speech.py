#!/usr/bin/env python3
"""
Simple script to generate speech from text using Gemini TTS API.
"""

import os
import struct
import mimetypes
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Configuration
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / '.env')

INPUT_FILE = "data/audio/LLMs-explained/tts_input.txt"
MODEL_NAME = "gemini-2.5-flash-preview-tts"
VOICE = "Algenib"
CHUNK_SIZE = 400  # words per chunk
TOLERANCE = 30    # words tolerance
api_key = os.getenv("GOOGLE_API_KEY")


def create_wav_header(pcm_data: bytes, sample_rate: int, bits_per_sample: int) -> bytes:
    """
    Create WAV file header for PCM data.
    
    Args:
        pcm_data: Raw PCM audio bytes
        sample_rate: Sample rate (e.g. 24000)
        bits_per_sample: Bits per sample (e.g. 16)
    
    Returns:
        Complete WAV file with header
    """
    num_channels = 1
    data_size = len(pcm_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size
    
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",           # ChunkID
        chunk_size,        # ChunkSize
        b"WAVE",           # Format
        b"fmt ",           # Subchunk1ID
        16,                # Subchunk1Size (PCM)
        1,                 # AudioFormat (PCM)
        num_channels,      # NumChannels
        sample_rate,       # SampleRate
        byte_rate,         # ByteRate
        block_align,       # BlockAlign
        bits_per_sample,   # BitsPerSample
        b"data",           # Subchunk2ID
        data_size          # Subchunk2Size
    )
    return header + pcm_data


def parse_audio_params(mime_type: str) -> tuple[int, int]:
    """
    Extract sample rate and bits from MIME type.
    Example: "audio/L16;codec=pcm;rate=24000" -> (24000, 16)
    """
    rate = 24000  # default
    bits = 16     # default
    
    parts = mime_type.split(";")
    for part in parts:
        part = part.strip()
        if part.lower().startswith("rate="):
            try:
                rate = int(part.split("=", 1)[1])
            except (ValueError, IndexError):
                pass
        elif "L" in part and part.startswith("audio/L"):
            try:
                bits = int(part.split("L", 1)[1])
            except (ValueError, IndexError):
                pass
    
    return rate, bits


def split_text_into_chunks(text: str, target_words: int = 400, tolerance: int = 30) -> list[str]:
    """
    Split text into chunks of approximately target_words, respecting sentence boundaries.
    """
    # Simple sentence splitting on . ! ? followed by space or end of line
    sentences = []
    current_sentence = ""
    
    # Using a simple logic to split sentences to avoid complex regex if possible, 
    # but regex is safer for "Mr." etc. sticking to simple split for now as requested.
    # Actually, let's just split by punctuation marks that end sentences.
    import re
    # Split by (. ! ?) followed by space or newline
    raw_parts = re.split(r'([.!?](?:\s+|$))', text)
    
    # Reassemble with delimiters
    for i in range(0, len(raw_parts) - 1, 2):
        sentences.append(raw_parts[i] + raw_parts[i+1])
    if len(raw_parts) % 2 != 0 and raw_parts[-1]:
        sentences.append(raw_parts[-1])

    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for sentence in sentences:
        sentence_word_count = len(sentence.split())
        
        # If adding this sentence keeps us within tolerance of target or we are way below
        if current_word_count + sentence_word_count <= target_words + tolerance:
            current_chunk.append(sentence)
            current_word_count += sentence_word_count
            
            # If we are in the target range, close the chunk
            if target_words - tolerance <= current_word_count:
                chunks.append("".join(current_chunk).strip())
                current_chunk = []
                current_word_count = 0
        else:
            # If current chunk is not empty, push it
            if current_chunk:
                chunks.append("".join(current_chunk).strip())
            
            # Start new chunk with current sentence
            current_chunk = [sentence]
            current_word_count = sentence_word_count
            
    # Append any remaining text
    if current_chunk:
        chunks.append("".join(current_chunk).strip())
        
    return chunks


def main():
    """Main function to generate speech from text."""
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file")
    
    # Read input text
    input_path = project_root / INPUT_FILE
    text = input_path.read_text(encoding='utf-8')
    
    print(f"Input text ({len(text)} chars)")
    
    chunks = split_text_into_chunks(text, CHUNK_SIZE, TOLERANCE)
    print(f"Split into {len(chunks)} chunks (target {CHUNK_SIZE} words +/- {TOLERANCE})")
    print(f"Using model: {MODEL_NAME}")
    print(f"Voice: {VOICE}\n")
    
    # Initialize client
    client = genai.Client(api_key=api_key)
    
    # Configure for audio output with voice settings
    config = types.GenerateContentConfig(
        response_modalities=["audio"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=VOICE
                )
            )
        )
    )
    
    full_audio_pcm = bytearray()
    sample_rate = 24000
    bits_per_sample = 16
    
    for i, chunk in enumerate(chunks, 1):
        word_count = len(chunk.split())
        print(f"Processing Chunk {i}/{len(chunks)} ({word_count} words)...")
        
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=chunk,
                config=config
            )
            
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.data:
                        raw_audio = part.inline_data.data
                        
                        # Append to full audio
                        full_audio_pcm.extend(raw_audio)
                        
                        # Save individual part
                        wav_audio = create_wav_header(raw_audio, sample_rate, bits_per_sample)
                        part_filename = f"{VOICE}_part_{i}.wav"
                        output_path = project_root / f"data/audio/LLMs-explained/{part_filename}"
                        output_path.write_bytes(wav_audio)
                        
                        print(f"  ✓ Saved part: {part_filename}")
            else:
                print(f"  ✗ No audio data received for chunk {i}")
                
        except Exception as e:
            print(f"  ✗ Error generating audio for chunk {i}: {e}")
            
    # Save full concatenated audio
    if full_audio_pcm:
        full_wav = create_wav_header(bytes(full_audio_pcm), sample_rate, bits_per_sample)
        full_filename = f"{VOICE}_full.wav"
        full_output_path = project_root / f"data/audio/LLMs-explained/{full_filename}"
        full_output_path.write_bytes(full_wav)
        
        print(f"\n✓ Saved full audio: {full_output_path}")
        print(f"  Total size: {len(full_wav)} bytes")
    else:
        print("\n✗ No audio generated to merge.")


if __name__ == "__main__":
    main()
