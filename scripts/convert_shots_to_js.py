import json
import re
import csv
import os

def parse_srt(srt_path):
    """
    Parses an SRT file and returns a dictionary mapping subtitle index to timing info.
    Returns: {index (int): {'start': str, 'end': str, 'text': str}}
    """
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by double newline to separate blocks
    blocks = content.strip().split('\n\n')
    
    srt_data = {}
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            try:
                index = int(lines[0].strip())
                timing = lines[1].strip()
                if '-->' in timing:
                    start, end = timing.split(' --> ')
                    text = ' '.join(lines[2:])
                    srt_data[index] = {
                        'start': start.strip(),
                        'end': end.strip(),
                        'text': text.strip()
                    }
            except ValueError:
                continue # Skip malformed blocks
                
    return srt_data

def parse_csv(csv_path):
    """
    Parses the CSV file and returns a list of dictionaries.
    """
    shots = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            shots.append(row)
    return shots

def get_timing_from_ids(ids_str, srt_data):
    """
    Calculates the start and end time for a range of IDs.
    ids_str can be "1", "1-3", "1, 2, 3" etc.
    """
    # Normalize IDs string
    ids_str = str(ids_str).strip()
    
    # Parse IDs into a list of integers
    id_list = []
    
    # Handle ranges (e.g., "1-3")
    if '-' in ids_str:
        start_id, end_id = map(int, ids_str.split('-'))
        id_list = list(range(start_id, end_id + 1))
    # Handle comma separated values (e.g. "1, 2, 3" or single "1")
    else:
        # Split by comma and strip
        parts = [p.strip() for p in ids_str.split(',')]
        # Filter empty strings
        parts = [p for p in parts if p]
        id_list = [int(p) for p in parts]
        
    if not id_list:
        return None, None

    # Get start time of the first ID
    first_id = id_list[0]
    last_id = id_list[-1]
    
    start_time = srt_data.get(first_id, {}).get('start', '00:00:00,000')
    end_time = srt_data.get(last_id, {}).get('end', '00:00:00,000')
    
    return start_time, end_time

def main():
    base_dir = '/Users/onetiger/projects/novaclips/data/scenarios/LLMs-explained'
    srt_path = os.path.join(base_dir, 'LLMs-explained.srt')
    csv_path = os.path.join(base_dir, 'shot_list_with_refs.csv')
    js_path = os.path.join(base_dir, 'shot_list.js')
    
    if not os.path.exists(srt_path):
        print(f"Error: SRT file not found at {srt_path}")
        return
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    print("Parsing SRT file...")
    srt_data = parse_srt(srt_path)
    print(f"Loaded {len(srt_data)} subtitle identifiers.")
    
    print("Parsing CSV file...")
    csv_shots = parse_csv(csv_path)
    print(f"Loaded {len(csv_shots)} shots from CSV.")
    
    scenes = []
    
    for row in csv_shots:
        scene_id = row.get('Scene', '').strip()
        ids_str = row.get('IDs', '').strip()
        subtitles = row.get('Subtitles', '').strip()
        image_prompt = row.get('Image Prompt', '').strip()
        reference_images = row.get('Reference Images', '').strip()
        
        # Calculate timing
        start_time, end_time = get_timing_from_ids(ids_str, srt_data)
        
        # Remove milliseconds if present
        if start_time:
            start_time = start_time.split(',')[0]
        if end_time:
            end_time = end_time.split(',')[0]
            
        timing_str = f"{start_time} - {end_time}"
        
        # Clean subtitles (remove extra quotes if any)
        subtitles = subtitles.strip('"').replace('\\"', '"')
        
        # Clean image prompt
        image_prompt = image_prompt.replace('<br>', '\n')

        scenes.append({
            "scene": scene_id,
            "ids": ids_str,
            "timing": timing_str,
            "subtitles": subtitles,
            "image_prompt": image_prompt,
            "reference_images": reference_images
        })
    
    # Write JS file
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write("const shotlist = ")
        json.dump(scenes, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully converted {len(scenes)} scenes to {js_path}")

    # Write JSON file
    json_path = js_path.replace('.js', '.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(scenes, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully converted {len(scenes)} scenes to {json_path}")

if __name__ == "__main__":
    main()
