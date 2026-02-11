
import os
import re

def main():
    input_file = "/Users/onetiger/projects/novaclips/data/scenarios/LLMs-explained/shot_list.md"
    output_file = "/Users/onetiger/projects/novaclips/data/scenarios/LLMs-explained/shot_list_with_refs_fixed.md"

    # Categories with Regex and associated Image
    # Order in list doesn't matter for priority, we define priority later.
    categories = {
        "whiteboard": {
            "image": "whiteboard_768.jpeg",
            "regex": [r"whiteboard", r"diagram", r"\bchart\b", r"\bgraph\b", r"checklist", r"outline", r"\bframe\b", r"\bslate\b", r"paper", r"post-it", r"sticky note"]
        },
        "sunny": {
            "image": "sunny_768.jpeg",
            "regex": [r"cafe", r"coffee shop", r"park", r"street", r"outdoor", r"\bday\b", r"\bsun\b", r"warm lighting", r"natural light", r"urban"]
        },
        "dark": {
            "image": "dark_768.jpeg",
            "regex": [r"cyberpunk", r"neon", r"void", r"black", r"shadow", r"volumetric", r"cinematic", r"deep cobalt", r"glow", r"\bdim\b", r"glitchy red", r"darkness", r"\bdark\b"]
        },
        "office": {
            "image": "office_768.jpeg",
            "regex": [r"office", r"\bwork\b", r"desk", r"meeting", r"room", r"indoor", r"studio", r"workshop", r"gym", r"restaurant", r"library"]
        },
        "architect": {
            "image": "architect_768.jpeg",
            "regex": [r"architect", r"young man", r"character", r"holding", r"sitting", r"standing", r"looking", r"hands", r"detective", r"person"]
        },
        "persons": {
            "image": "persons_768.jpeg",
            "regex": [r"people", r"crowd", r"group", r"team", r"extra", r"persons"]
        },
        "items": {
            "image": "items_768.jpeg",
            "regex": [r"interface", r"ui\b", r"hologram", r"tablet", r"device", r"screen", r"monitor", r"techwear", r"geometric", r"backpack", r"lego", r"brick", r"scale", r"conveyor", r"machine", r"robot", r"isometric", r"glitch", r"token", r"block", r"cube", r"toolkit", r"scissors", r"\bobject\b", r"machinery", r"server rack", r"balance", r"lock", r"key"]
        }
    }

    # Priority List (Higher index = Lower priority? No, let's sort by this list)
    # 1. Whiteboard (Specific prop that dominates the scene)
    # 2. Location (Sunny, Office) - Critical for atmosphere
    # 3. Architect - Layout specific
    # 4. Location (Dark) - Atmosphere
    # 5. Persons / Items - Backup
    
    priority_order = ["whiteboard", "sunny", "architect", "dark", "office", "persons", "items"]

    def get_refs(prompt_text):
        prompt_lower = prompt_text.lower()
        matched_categories = set()

        for cat_name, data in categories.items():
            for pattern in data["regex"]:
                if re.search(pattern, prompt_lower):
                    matched_categories.add(cat_name)
                    break
        
        # Sort matches by priority
        sorted_matches = sorted(list(matched_categories), key=lambda x: priority_order.index(x))
        
        # Select top unique images (max 2)
        selected_images = []
        for cat in sorted_matches:
            img = categories[cat]["image"]
            if img not in selected_images:
                selected_images.append(img)
            if len(selected_images) >= 2:
                break
        
        return selected_images

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    final_lines = []
    header_found = False
    
    for line in lines:
        stripped = line.strip()
        
        # Pass through non-table lines
        if not stripped.startswith("|") or "---" in line:
            # Handle separator line for new column validation
            if "---" in line and header_found and "Reference Images" not in line:
                 # If we are reprocessing original file, it won't have the col.
                 # If we are reprocessing `with_refs`, it might.
                 # Let's assume input is standard MD.
                 pass
            final_lines.append(line)
            continue
            
        parts = stripped.strip("|").split("|")
        # Cleaning parts
        parts = [p.strip() for p in parts]
        
        # Header processing
        if "Image Prompt" in line and not header_found:
             # Check if header already has Reference Images (if re-running on output)
             if "Reference Images" in line:
                 final_lines.append(line)
             else:
                 new_line = "|" + "|".join([f" {p} " for p in parts]) + "| Reference Images |\n"
                 final_lines.append(new_line)
                 # Add separator line immediately after? No, loop handles it.
                 # Wait, separator line logic in previous script was fragile.
                 # Let's just append the separator line if the NEXT line is separator.
             header_found = True
             continue
        
        # Separator Line logic check
        # The loop condition `or "---" in line` above skips this block for separator lines.
        # So we need to handle separator in the `if not stripped...` block?
        # Actually, let's look at the `final_lines.append(line)` above.
        # If we are adding a column, we need to extend the separator line too.
        
    # RESTARTING LOOP LOGIC FOR CLEANER SEPARATOR HANDLING
    
    final_lines = []
    header_found = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 1. Header Row
        if "Image Prompt" in line and "Reference Images" not in line:
            parts = stripped.strip("|").split("|")
            new_line = "|" + "|".join([f" {p.strip()} " for p in parts]) + "| Reference Images |\n"
            final_lines.append(new_line)
            header_found = True
            continue
            
        # 2. Separator Row (immediately follows header usually)
        if set(stripped.replace("|", "").replace(" ", "")) <= set("-:") and header_found:
             if len(stripped.split("|")) < len(final_lines[-1].split("|")): # If separator is shorter than header
                 new_line = stripped.rstrip("|") + " :--- |\n" # Add extra column
                 # Fix formatting roughly
                 final_lines.append(new_line)
             else:
                 final_lines.append(line)
             continue
             
        # 3. Data Row
        if header_found and stripped.startswith("|"):
            parts = stripped.strip("|").split("|")
            if len(parts) >= 5: # Assuming Prompt is 5th col (index 4)
                image_prompt = parts[4]
                
                refs = get_refs(image_prompt)
                ref_str = ", ".join(refs)
                
                # Reconstruct
                # parts[0] is usually empty matching string before first |? 
                # split("|") on "| a | b |" gives ["", " a ", " b ", ""]
                # line.strip("|").split("|") gives [" a ", " b "]
                
                new_line = "|" + "|".join([f" {p.strip()} " for p in parts]) + f"| {ref_str} |\n"
                final_lines.append(new_line)
            else:
                 final_lines.append(line)
        else:
            final_lines.append(line)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    
    print(f"Generated {output_file}")

if __name__ == "__main__":
    main()
