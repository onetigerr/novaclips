import os
import sys
import argparse
from dotenv import load_dotenv

# Add src to python path to allow importing lib
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from lib.google_imagen import GoogleImageGenerator

def main():
    parser = argparse.ArgumentParser(description="Test Google Image Generation")
    parser.add_argument("prompt", help="Text prompt for image generation")
    parser.add_argument("--output", default="output.png", help="Output file path")
    parser.add_argument("--style-refs", nargs="+", help="Paths to style reference images")
    parser.add_argument("--model", default="imagen-4.0-fast-generate-001", help="Model name (e.g. imagen-4.0-fast-generate-001)")
    
    args = parser.parse_args()
    
    # Load .env variables
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        return

    try:
        generator = GoogleImageGenerator(api_key=api_key)
        
        print(f"Generating image for prompt: '{args.prompt}'")
        if args.style_refs:
            print(f"Using style references: {args.style_refs}")
            
        output_path = generator.generate_image(
            prompt=args.prompt,
            output_path=args.output,
            style_reference_paths=args.style_refs,
            model_name=args.model
        )
        
        print(f"Successfully generated image at: {output_path}")
        
    except Exception as e:
        print(f"Failed to generate image: {e}")

if __name__ == "__main__":
    main()
