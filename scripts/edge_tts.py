import asyncio
import argparse
import os
import edge_tts

# ==========================================
# CONFIGURATION
# ==========================================
# Voice to use. Examples: 
# "en-US-ChristopherNeural" (Male), "en-US-AriaNeural" (Female)
VOICE = "en-GB-SoniaNeural"

# Rate of speech. Examples: "+0%", "+10%", "-10%"
RATE = "+0%"

# Volume of speech. Examples: "+0%", "+10%", "-10%"
VOLUME = "+0%"

# Default output directory if not specified
DEFAULT_OUTPUT_DIR = "data/audio"
# ==========================================

async def generate_audio(text_file, output_file):
    """
    Generates audio from the text in the text_file using Edge TTS.
    """
    try:
        with open(text_file, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: Text file '{text_file}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    if not text.strip():
        print("Error: Input text file is empty.")
        return

    print(f"Generating audio for '{text_file}'...")
    print(f"Voice: {VOICE}, Rate: {RATE}, Volume: {VOLUME}")
    
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, volume=VOLUME)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    await communicate.save(output_file)
    print(f"Audio saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Generate TTS audio from a text file using Edge TTS.")
    parser.add_argument("input_file", help="Path to the input text file containing the script.")
    parser.add_argument("--output", "-o", help="Path to the output audio file. If not provided, it defaults to data/audio/<input_filename>.mp3")

    args = parser.parse_args()

    input_path = args.input_file
    
    if args.output:
        output_path = args.output
    else:
        # Determine output path based on input filename, saving to same directory
        dir_name = os.path.dirname(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(dir_name, f"{base_name}.mp3")

    asyncio.run(generate_audio(input_path, output_path))

if __name__ == "__main__":
    main()
