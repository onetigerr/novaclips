#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# WARNING: DO NOT RUN THIS SCRIPT WITHOUT EXPLICIT USER PERMISSION.
# THIS SCRIPT CONSUMES PAID CREDITS FOR IMAGE GENERATION.
# COST MONEY. DO NOT AUTO-RUN.
# -----------------------------------------------------------------------------

import argparse
import sys
import re
import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Set
from dotenv import load_dotenv

# Add project root to path to import lib
# Assuming this script is in [Root]/scripts/
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

# Load environment variables
load_dotenv(project_root / '.env')

from lib.google_imagen import GoogleImageGenerator



# Constants
# DEFAULT_MODEL = "imagen-4.0-fast-generate-001"
DEFAULT_MODEL = "gemini-3-pro-image-preview"
DEFAULT_ASPECT_RATIO = "16:9"
VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
PICTURES_DIR_NAME = "pictures"
GENERATIONS_DIR_NAME = "generations"
SHOT_ID_PADDING = 2

def load_scenario_json(file_path: Path) -> List[Dict[str, str]]:
    """
    Loads the scenario data from a JSON file.
    Returns a list of dictionaries, where each dict represents a shot.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Scenario file not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding JSON file: {e}")

    if not isinstance(data, list):
        raise ValueError("JSON root must be a list of shot objects.")

    return data

def get_reference_images(shot_data: Dict[str, str], pictures_dir: Path) -> List[str]:
    """
    Extracts reference image filenames from the shot data and resolves their full paths.
    """
    ref_string = shot_data.get("reference_images", "")
    if not ref_string:
        return []

    # Split by comma and strip whitespace
    image_names = [name.strip() for name in ref_string.split(',')]
    
    valid_images = []
    for name in image_names:
        if not name:
            continue
            
        file_path = pictures_dir / name
        if file_path.exists() and file_path.is_file():
             valid_images.append(str(file_path))
             continue

        # Try with different extensions if not found
        stem = Path(name).stem
        found = False
        for ext in VALID_IMAGE_EXTENSIONS:
            candidate = pictures_dir / (stem + ext)
            if candidate.exists() and candidate.is_file():
                valid_images.append(str(candidate))
                found = True
                break
        
        if not found:
            print(f"Warning: Reference image not found: {name}")

    return valid_images

def clean_prompt(prompt: str) -> str:
    """
    Cleans up the prompt text by removing markdown formatting.
    """
    if not prompt:
        return ""
        
    # Remove bolding (**text**)
    prompt = prompt.replace('**', '')
    
    # Replace <br> with newlines
    prompt = prompt.replace('<br>', '\n')
    
    return prompt

def main():
    parser = argparse.ArgumentParser(description="Generate images from a usage scenario JSON file.")
    parser.add_argument("scenario_path", type=str, help="Path to the scenario JSON file.")
    parser.add_argument("--shot", type=str, help="Specific shot ID to generate (e.g. '01').")
    parser.add_argument("--execute", action="store_true", help="Execute the generation (calls API). Default is Dry Run.")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help=f"Model name to use. Default matches lib: {DEFAULT_MODEL}")
    parser.add_argument("--aspect-ratio", type=str, default=DEFAULT_ASPECT_RATIO, choices=["1:1", "16:9", "4:3", "9:16", "3:4"], help=f"Aspect ratio of the generated image. Default is '{DEFAULT_ASPECT_RATIO}'.")

    args = parser.parse_args()
    
    scenario_file = Path(args.scenario_path).resolve()
    if not scenario_file.exists():
        print(f"Error: File not found: {scenario_file}")
        sys.exit(1)
        
    scenario_dir = scenario_file.parent
    pictures_dir = scenario_dir / PICTURES_DIR_NAME

    if not pictures_dir.exists():
        print(f"Warning: '{PICTURES_DIR_NAME}' directory not found at {pictures_dir}")
    
    print(f"Scenario File: {scenario_file}")
    
    try:
        shots = load_scenario_json(scenario_file)
    except Exception as e:
        print(f"Error loading scenario: {e}")
        sys.exit(1)

    if not shots:
        print("No shots found in JSON file.")
        sys.exit(1)
        
    print(f"Found {len(shots)} shots.")

    output_dir = scenario_dir / GENERATIONS_DIR_NAME
    if args.execute:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    generator: Optional[GoogleImageGenerator] = None
    if args.execute:
        try:
            generator = GoogleImageGenerator()
        except Exception as e:
            print(f"Error initializing generator: {e}")
            sys.exit(1)
            
    target_shots = set()
    if args.shot:
        # Support comma-separated list and ranges (e.g. "1, 3-5")
        parts = args.shot.split(',')
        for part in parts:
            clean_part = part.strip()
            if not clean_part:
                continue
                
            if '-' in clean_part:
                # Handle range "start-end"
                try:
                    start_str, end_str = clean_part.split('-')
                    start = int(start_str)
                    end = int(end_str)
                    
                    if start > end:
                        start, end = end, start
                        
                    for i in range(start, end + 1):
                        target_shots.add(str(i).zfill(SHOT_ID_PADDING))
                except ValueError:
                    print(f"Warning: Invalid range format '{clean_part}'. Ignoring.")
            else:
                # Handle single ID
                target_shots.add(clean_part.zfill(SHOT_ID_PADDING))

    print(f"\nMode: {'EXECUTION (Calling API)' if args.execute else 'DRY RUN (Printing Prompts)'}")
    print("=" * 60)

    count = 0
    
    for shot in shots:
        shot_id = shot.get("scene", "??")
        
        # Filter logic
        if target_shots:
            params_id = shot_id.zfill(SHOT_ID_PADDING)
            if params_id not in target_shots:
                continue
                
        count += 1
        raw_prompt = shot.get("image_prompt", "")
        prompt_text = clean_prompt(raw_prompt)
        
        reference_images = get_reference_images(shot, pictures_dir)
        
        print(f"\n[Shot {shot_id}]")
        
        if not args.execute:
            print(f"Prompt:\n{prompt_text}")
            print(f"Style References: {[Path(p).name for p in reference_images]}")
            print(f"Output Path: {output_dir / f'shot_{shot_id}.png'}")
        else:
            print(f"Generating Shot {shot_id}...")
            output_path = output_dir / f"shot_{shot_id}.png"
            
            try:
                # Ensure generator is not None for static analysis and safety
                assert generator is not None, "Generator not initialized even though execute mode is on"

                result_path = generator.generate_image(
                    prompt=prompt_text,
                    output_path=str(output_path),
                    style_reference_paths=reference_images,
                    aspect_ratio=args.aspect_ratio,
                    model_name=args.model
                )
                print(f"SUCCESS: Saved to {result_path}")
            except Exception as e:
                print(f"FAILED: {e}")

    if count == 0 and target_shots:
        print(f"Warning: No shots found matching {args.shot}")

if __name__ == "__main__":
    main()
