
import os
import re

def main():
    input_file = "/Users/onetiger/projects/novaclips/data/scenarios/LLMs-explained/shot_list.md"
    output_file = "/Users/onetiger/projects/novaclips/data/scenarios/LLMs-explained/shot_list_with_refs.md"

    # Rules for mapping content to images
    # Tuple format: (Image Filename, [List of Regex Keywords])
    rules = [
        ("items_768.jpeg", [
            r"interface", r"ui\b", r"hologram", r"tablet", r"device", r"screen", 
            r"monitor", r"techwear", r"geometric", r"backpack", r"lego", r"brick", 
            r"scale", r"conveyor", r"machine", r"robot", r"isometric", r"glitch",
            r"token", r"block", r"cube", r"toolkit", r"scissors", r"\bobject\b",
            r"machinery", r"server rack", r"balance", r"lock", r"key"
        ]),
        ("whiteboard_768.jpeg", [
             r"whiteboard", r"diagram", r"chart", r"graph", r"note", r"sticky", 
             r"post-it", r"checklist", r"outline", r"frame", r"slate", r"paper"
        ]),
        ("architect_768.jpeg", [
            r"architect", r"young man", r"character", r"holding", r"sitting", 
            r"standing", r"looking", r"hands", r"\buser\b", r"detective", r"person"
        ]),
        ("sunny_768.jpeg", [
             r"cafe", r"park", r"street", r"outdoor", r"\bday\b", r"\bsun\b", 
             r"warm", r"natural light", r"coffee shop", r"urban"
        ]),
        ("dark_768.jpeg", [
             r"cyberpunk", r"neon", r"\bdark\b", r"night", r"void", r"black", 
             r"shadow", r"volumetric", r"cinematic", r"deep cobalt", 
             r"glow", r"\bdim\b", r"glitchy red"
        ]),
        ("office_768.jpeg", [
             r"office", r"\bwork\b", r"desk", r"meeting", r"room", r"indoor", 
             r"studio", r"workshop", r"gym", r"restaurant", r"library"
        ]),
        ("persons_768.jpeg", [
             r"people", r"crowd", r"group", r"team", r"extra", r"persons"
        ])
    ]

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    final_lines = []
    header_found = False
    
    for line in lines:
        stripped = line.strip()
        
        # Pass through non-table lines
        if not stripped.startswith("|"):
            final_lines.append(line)
            continue
            
        parts = stripped.strip("|").split("|")
        # Cleaning parts whitespace
        parts = [p.strip() for p in parts]
        
        # Check for Header
        if "Image Prompt" in line and not header_found:
            # Reconstruct header with new column
            new_line = "|" + "|".join([f" {p} " for p in parts]) + "| Reference Images |\n"
            final_lines.append(new_line)
            header_found = True
            continue
            
        # Check for Separator
        if set(stripped.replace("|", "").replace(" ", "")) <= set("-:") and header_found:
             # Match the separator style
             new_line = "|" + "|".join([f" {p} " for p in parts]) + "| :--- |\n"
             final_lines.append(new_line)
             continue
        
        # Process Data Row
        if header_found and len(parts) >= 5: # Ensure we have enough columns
            image_prompt = parts[4].lower() # 5th column is Prompt (index 4)
            full_row_text = " ".join(parts).lower() # Use full row text for better context matching? 
                                                    # Actually user said "Image Prompt" specifically.
                                                    # Stick to image_prompt.
            
            # Additional Context: Subject description is usually "Subject: ... " inside image prompt column
            # We strictly stick to parsing that column.
            
            matched_refs = []
            
            # Apply Rules
            for image_file, keywords in rules:
                # Check if any keyword matches
                if any(re.search(k, image_prompt) for k in keywords):
                    matched_refs.append(image_file)
                
                # Limit to 2 images max
                if len(matched_refs) >= 2:
                    break
            
            # Deduplicate just in case
            matched_refs = list(dict.fromkeys(matched_refs))
            
            ref_string = ", ".join(matched_refs)
            
            # Reconstruct the line
            # We need to preserve original spacing if possible, but markdown table extract/rebuild is safer
            # to just standardise.
            new_line = "|" + "|".join([f" {p} " for p in parts]) + f"| {ref_string} |\n"
            final_lines.append(new_line)

        else:
            # Fallback for weird lines inside table structure
            final_lines.append(line)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)

    print(f"Successfully generated {output_file}")

if __name__ == "__main__":
    main()
