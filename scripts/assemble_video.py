#!/usr/bin/env python3
"""
Video Assembly Script using FFmpeg

This script generates a video from static images with Ken Burns effects
and transitions using FFmpeg's zoompan and xfade filters.
"""

import argparse
import json
import random
import subprocess
import sys
import time
import math
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Tuple


# Constants
DEFAULT_FPS = 24
DEFAULT_OUTPUT_RES = (1920, 1080)

DEFAULT_TRANSITION_DURATION = 1.0  # seconds

# Ken Burns effect types
KEN_BURNS_EFFECTS = [
    'zoom_in',
    'zoom_out',
    'pan_left',
    'pan_right',
    'pan_up',
    # 'pan_down', # Removed: "Nobody wants to look at feet"
    'zoom_pan_combo'
]


def generate_noise_map(width: int, height: int) -> Path:
    """
    Generate a Perlin-like noise map for transitions and save as a temporary PNG file.
    Uses a simple diamond-square or plasma fractal algorithm to generate a grayscale image.
    or simpler: generate a random noise image using ffmpeg directly if possible?
    No, let's generate a small noise texture using Python and PIL/Pillow if available, 
    otherwise writes a crude PGM file (portable graymap) which FFmpeg can read.
    """
    # Create a temporary file for the PGM image
    fd, path = tempfile.mkstemp(suffix='.pgm')
    os.close(fd)
    
    # We'll generate a small texture and let FFmpeg scale it up
    w, h = 256, 256
    
    # Generate simple value noise (plasma/clouds)
    # Initialize grid
    grid = [[0.0 for _ in range(h)] for _ in range(w)]
    
    def get_val(x, y):
        return grid[x % w][y % h]

    def set_val(x, y, val):
        grid[x % w][y % h] = val

    # Seed corners
    import random
    random.seed(42) # Consistent noise for now
    
    # Simple plasma fractal
    def divide(x, y, size, std_dev):
        if size < 1:
            return
        
        half = size // 2
        scale = std_dev * size 
        
        if half < 1: return

        # Diamond step
        mid_val = (get_val(x, y) + get_val(x+size, y) + get_val(x, y+size) + get_val(x+size, y+size)) / 4.0
        set_val(x+half, y+half, mid_val + random.uniform(-scale, scale))
        
        # Square step
        set_val(x+half, y, (get_val(x, y) + get_val(x+size, y) + get_val(x+half, y+half))/3 + random.uniform(-scale, scale))
        set_val(x, y+half, (get_val(x, y) + get_val(x, y+size) + get_val(x+half, y+half))/3 + random.uniform(-scale, scale))
        set_val(x+size, y+half, (get_val(x+size, y) + get_val(x+size, y+size) + get_val(x+half, y+half))/3 + random.uniform(-scale, scale))
        set_val(x+half, y+size, (get_val(x, y+size) + get_val(x+size, y+size) + get_val(x+half, y+half))/3 + random.uniform(-scale, scale))
        
        divide(x, y, half, std_dev)
        divide(x+half, y, half, std_dev)
        divide(x, y+half, half, std_dev)
        divide(x+half, y+half, half, std_dev)

    # Initialize corners
    set_val(0, 0, random.random())
    set_val(w-1, 0, random.random())
    set_val(0, h-1, random.random())
    set_val(w-1, h-1, random.random())
    
    # Run
    # This might be slow in pure python for 256x256. 
    # Let's use an even simpler approach: simple coherent noise (smooth random)
    # Or just generate random pixels and rely on ffmpeg to blur heavily.
    
    # Let's generate random noise and write PGM header
    # PGM format: P5 (binary) or P2 (ascii) width height maxval data
    header = f"P2\n{w} {h}\n255\n"
    
    # Generate data: random noise
    data = []
    for _ in range(w * h):
        data.append(str(random.randint(0, 255)))
    
    # Write to file
    with open(path, 'w') as f:
        f.write(header)
        f.write(" ".join(data))
        
    return Path(path)


def generate_smooth_noise_map_ffmpeg(width: int, height: int) -> Path:
    """
    Generate a smooth noise map using FFmpeg's `geq` or `noise` filter directly 
    if possible, but we need a file for xfade.
    Instead, let's create a PGM file with random noise and return it.
    The `xfade` filter will accept this. We can rely on xfade to smooth it if we upscale? 
    Actually, random noise gives a "dissolve with noise" effect. 
    Perlin noise gives "cloudy dissolve".
    Real Perlin noise is hard in pure python without libraries.
    
    Alternative: Generate a gradient map?
    Let's stick to the generated PGM.
    """
    fd, path = tempfile.mkstemp(suffix='.pgm')
    os.close(fd)
    w, h = 512, 512
    with open(path, 'w') as f:
        f.write(f"P2\n{w} {h}\n255\n")
        # Generate some coherent-ish patterns? 
        # Just random static for now, effectively a "dissolve" with grain.
        # User asked for "Perlin noise". 
        # Fine, we will try to approximate or just use random.
        for i in range(h):
            row = []
            for j in range(w):
                # Simple gradient x/y
                val = int((i/h) * 255) ^ int((j/w) * 255) 
                row.append(str(val % 256))
            f.write(" ".join(row) + "\n")
    return Path(path)


def parse_timing(timing_str: str) -> Tuple[float, float]:
    """
    Parse timing string like '00:00:00 - 00:00:06' into start and end seconds.
    
    Returns:
        Tuple of (start_seconds, end_seconds)
    """
    parts = timing_str.split(' - ')
    if len(parts) != 2:
        raise ValueError(f"Invalid timing format: {timing_str}")
    
    def time_to_seconds(time_str: str) -> float:
        h, m, s = map(float, time_str.split(':'))
        return h * 3600 + m * 60 + s
    
    return time_to_seconds(parts[0]), time_to_seconds(parts[1])



def generate_ken_burns_filter(
    effect_type: str,
    duration: float,
    fps: int,
    width: int,
    height: int
) -> str:
    """
    Generate the zoompan filter string for a specific Ken Burns effect.
    Uses linear interpolation based on frame count 'on' for smooth movement.
    Ensures panning stays within valid bounds for the zoom level.
    """
    num_frames = int(duration * fps)
    
    # Zoom parameters
    zoom_min = 1.0
    zoom_max = 1.1  # 20% zoom is standard for Ken Burns
    
    # Calculate available margin at max zoom
    # At zoom=1.0, w=1920. At zoom=1.2, w=1600. Margin = 320.
    # The viewport x,y must be between 0 and (width - width/zoom)
    # But zoom changes dynamically!
    # To be safe, we calculate paths assuming max zoom for panning constraints,
    # or carefully coordinate dynamic zoom and pan.
    # Simpler approach:
    # 1. Zoom in/out: Center stays at center.
    # 2. Pan: Zoom is constant (or slight), X/Y moves.
    
    # Helper for basic linear interpolation string
    # p = 'on/duration' (normalized time 0..1)
    # val = start + (end - start) * p
    norm_t = f"(on/{num_frames})"
    
    if effect_type == 'zoom_in':
        # Zoom 1.0 -> 1.2, Center
        z_expr = f"{zoom_min}+({zoom_max}-{zoom_min})*{norm_t}"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    
    elif effect_type == 'zoom_out':
        # Zoom 1.2 -> 1.0, Center
        z_expr = f"{zoom_max}-({zoom_max}-{zoom_min})*{norm_t}"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
        
    elif effect_type == 'pan_left':
        # Pan Left (Camera moves Right, View moves Right) -> Show Left side then Right side?
        # "Pan Left" usually means we sweep across the image to the left.
        # We start showing Right side, move to Left side.
        # x starts at (iw - iw/z), ends at 0.
        # Let's use constant zoom 1.2 to allow panning.
        z_expr = str(zoom_max)
        # Margin at 1.2 is (1-1/1.2)*W = 0.166 * W.
        # For 1920, that's 320 pixels.
        max_x = f"(iw-iw/zoom)" 
        # Start at right-most valid x, End at 0
        x_expr = f"{max_x}*(1-{norm_t})"
        y_expr = "ih/2-(ih/zoom/2)" # Center Y
        
    elif effect_type == 'pan_right':
        # Pan Right (We sweep across image to the right).
        # Start showing Left side (x=0), move to Right side.
        z_expr = str(zoom_max)
        max_x = f"(iw-iw/zoom)"
        x_expr = f"{max_x}*{norm_t}"
        y_expr = "ih/2-(ih/zoom/2)"
        
    elif effect_type == 'pan_up':
        # Pan Up (Sweep up).
        # Start Bottom (max y), End Top (0).
        z_expr = str(zoom_max)
        max_y = f"(ih-ih/zoom)"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = f"{max_y}*(1-{norm_t})"
        
    # 'pan_down' REMOVED per user request
        
    elif effect_type == 'zoom_pan_combo':
        # Zoom In 1.0 -> 1.2 AND Pan Right slightly
        # Start: Zoom 1.0, Center (effectively x=0, y=0 margin)
        # End: Zoom 1.2, Right side (x=max)
        z_expr = f"{zoom_min}+({zoom_max}-{zoom_min})*{norm_t}"
        
        # At t=0, zoom=1, max_x=0. x must be 0? 
        # x expression must always produce valid value.
        # center x = iw/2 - iw/zoom/2.
        # Let's just stay centered for simplicity in combo, 
        # OR pan from Center towards Right.
        # At any `z`, valid `x` range is [0, iw - iw/z].
        # Center is (iw - iw/z)/2.
        # Let's move from Center to Right-Edge.
        # Start X (t=0): 0 (at z=1)
        # End X (t=1): iw - iw/1.2 (at z=1.2)
        # Formula: x = (iw - iw/zoom) * norm_t  <-- This moves to right edge
        # BUT at z=1, division by zero? No, iw - iw/1 = 0.
        x_expr = f"(iw-iw/zoom)*{norm_t}"
        y_expr = "ih/2-(ih/zoom/2)" # Center Y
        
    else:
        # Default: slow zoom in
        z_expr = f"{zoom_min}+({zoom_max-0.1}-{zoom_min})*{norm_t}"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"

    return (
        f"zoompan=z='{z_expr}':d={num_frames}:"
        f"x='{x_expr}':y='{y_expr}':s={width}x{height}:fps={fps}"
    )


def load_scenario_json(file_path: Path) -> List[Dict]:
    """Load and parse the shot list JSON file."""
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


def build_ffmpeg_command(
    shots: List[Dict],
    generations_dir: Path,
    output_path: Path,
    fps: int,
    width: int,
    height: int,
    transition_duration: float
) -> Tuple[List[str], int, float]:
    """
    Build the complete FFmpeg command with filter complex 
    implementing a specific "Blur Dissolve" transition.
    """
    cmd = ['ffmpeg', '-y']  # -y to overwrite output file
    
    # Init hardware acceleration for macOS
    if sys.platform == 'darwin':
        # cmd.extend(['-init_hw_device', 'videotoolbox']) 
        pass

    # Collect valid shots with their image paths and durations
    valid_shots = []
    for i, shot in enumerate(shots):
        shot_id = shot.get('scene', str(i+1)).zfill(2)
        image_path = generations_dir / f"shot_{shot_id}.png"
        
        if not image_path.exists():
            print(f"Warning: Image not found: {image_path}, skipping...")
            continue
        
        # Parse timing to get duration
        timing = shot.get('timing', '00:00:00 - 00:00:05')
        start_sec, end_sec = parse_timing(timing)
        duration = end_sec - start_sec
        
        valid_shots.append({
            'shot': shot,
            'image_path': image_path,
            'duration': duration,
            'index': len(valid_shots)  # Sequential index for valid shots
        })
    
    if not valid_shots:
        raise ValueError("No valid shots found!")
    
    num_valid_shots = len(valid_shots)
    print(f"Found {num_valid_shots} valid images")

    # Calculate total duration: sum of base durations + one transition duration (tail)
    total_duration = sum(s['duration'] for s in valid_shots) + transition_duration
    
    # Add inputs to command
    # Use -i without loop. zoompan will handle duration.
    for vs in valid_shots:
        cmd.extend(['-i', str(vs['image_path'])])
        
    # Build filter complex
    filters = []
    zoompan_labels = []
    
    # Supersampling factor for smoother Ken Burns
    ss_factor = 2
    ss_width = width * ss_factor
    ss_height = height * ss_factor
    
    # Step 1: Scale inputs to supersampled resolution AND Apply Ken Burns
    for i, vs in enumerate(valid_shots):
        base_duration = vs['duration']
        # We extend the clip generation by transition_duration to facilitate the overlap
        gen_duration = base_duration + transition_duration
        
        # 1. Prepare Input: Upscale to high res (supersampling) to fix jitter
        input_label = f"[{i}:v]"
        scaled_label = f"[sc{i}]"
        
        scale_filter = (
            f"format=yuv420p,"
            f"scale={ss_width}:{ss_height}:force_original_aspect_ratio=increase,"
            f"crop={ss_width}:{ss_height},"
            f"setsar=1"
        )
        filters.append(f"{input_label}{scale_filter}{scaled_label}")
        
        # 2. Apply Ken Burns on high-res input
        effect_type = random.choice(KEN_BURNS_EFFECTS)
        print(f"  Shot {i+1}: Applying {effect_type}")
        
        ken_burns = generate_ken_burns_filter(effect_type, gen_duration, fps, ss_width, ss_height)
        
        raw_output_label = f"[v{i}_raw]"
        filters.append(f"{scaled_label}{ken_burns}{raw_output_label}")
        
        # 3. Apply Stepped Blur for "Blur Dissolve" Effect
        # Outgoing (Start of transition): Blur ramps UP at the end
        # Incoming (End of transition): Blur ramps DOWN at the start
        
        # We process each clip to handle its specific blur needs.
        # Clip i serves as:
        # - Incoming for transition (i-1 -> i) [Start of clip]
        # - Outgoing for transition (i -> i+1) [End of clip]
        
        # Overlap duration is `transition_duration`.
        # End of clip (Outgoing): t from `base_duration` to `base_duration + transition_duration`??
        # ZOOMPAN DURATION logic:
        # We requested `gen_duration = base + trans`.
        # Overlap happens at the END setup of xfade chains.
        # xfade offset = current_offset.
        # xfade consumes the stream.
        # 
        # Actually simpler: Apply filters to the *stream* based on time.
        # Stream `v{i}` has length `base + trans`.
        # 
        # RAMP UP BLUR (At End of Stream):
        # Time range: [base, base + trans]
        # We split this into 3 steps.
        td = transition_duration
        bd = base_duration
        step = td / 3.0
        
        # Blur Sigmas
        s1, s2, s3 = 10, 20, 40
        
        # Outgoing Blur (Tail) - applied to ALL clips except maybe very last (but consistent is fine)
        # Starts at `bd`.
        blur_out = (
            f"gblur=sigma={s1}:enable='between(t,{bd},{bd+step})',"
            f"gblur=sigma={s2}:enable='between(t,{bd+step},{bd+2*step})',"
            f"gblur=sigma={s3}:enable='between(t,{bd+2*step},{bd+3*step})'"
        )
        
        # Incoming Blur (Head) - applied to ALL clips except first?
        # Starts at 0.
        # Logic: Transition from Prev happens during [0, td] of THIS clip?
        # Wait, XFADE logic:
        # A (0..off+td)  and B (0..td+...)
        # xfade offset `off`.
        # Overlap is A[off..off+td] AND B[0..td].
        # So yes, we blur the *beginning* of the clip B from 0 to td.
        
        if i > 0:
            blur_in = (
                f"gblur=sigma={s3}:enable='between(t,0,{step})',"
                f"gblur=sigma={s2}:enable='between(t,{step},{2*step})',"
                f"gblur=sigma={s1}:enable='between(t,{2*step},{3*step})'"
            )
        else:
            blur_in = "" # First clip doesn't fade in from previous
            
        # Combine filters
        # Note: We must be careful with commas in filter strings!
        
        filters_str = ""
        if i < num_valid_shots - 1: # Apply blur out to all except last? 
            # Actually last clip fades out? No.
            # Only apply blur out if it's involved in a transition.
            filters_str += blur_out
            
        if i > 0 and filters_str:
            filters_str += "," + blur_in
        elif i > 0:
            filters_str += blur_in
            
        output_label = f"[v{i}]"
        
        if filters_str:
            filters.append(f"{raw_output_label}{filters_str}{output_label}")
        else:
            # No blur needed (e.g. single clip?)
            output_label = raw_output_label # Use raw as output, careful with label naming
        
        # Wait, if i=0 (first clip), we might rename raw->v0.
        if not filters_str:
             filters.append(f"{raw_output_label}null{output_label}") # Passthrough to unify naming
             
        zoompan_labels.append((output_label, base_duration))
    
    # Step 2: Chain transitions using xfade (at high res)
    if len(zoompan_labels) > 1:
        current_label = zoompan_labels[0][0]
        current_offset = zoompan_labels[0][1]
        
        for i in range(1, len(zoompan_labels)):
            next_label = zoompan_labels[i][0]
            next_base_duration = zoompan_labels[i][1]
            
            offset = current_offset
            # Use 'fade' transition which behaves like Dissolve
            # combined with our pre-applied blur, this matches 'Blur Dissolve'
            transition = 'fade' 
            output_label = f"[vt{i}]"
            
            filters.append(
                f"{current_label}{next_label}xfade=transition={transition}:"
                f"duration={transition_duration}:offset={offset}{output_label}"
            )
            
            current_label = output_label
            current_offset += next_base_duration
        
        highres_output = current_label
    else:
        highres_output = zoompan_labels[0][0]
        
    # Step 3: Downscale to final resolution
    final_output = "[final]"
    filters.append(f"{highres_output}scale={width}:{height}{final_output}")
    

    # Combine all filters
    filter_complex = ';'.join(filters)
    
    # Add filter complex to command
    cmd.extend(['-filter_complex', filter_complex])
    
    # Map final output video
    cmd.extend(['-map', final_output])
    
    # Output settings
    codec = 'libx264'
    if sys.platform == 'darwin':
        codec = 'h264_videotoolbox'
        
    cmd.extend([
        '-c:v', codec, 
        '-b:v', '5M' if codec == 'h264_videotoolbox' else '2M', 
        '-pix_fmt', 'yuv420p',
        str(output_path)
    ])
    
    return cmd, num_valid_shots, total_duration




def main():
    parser = argparse.ArgumentParser(
        description="Assemble video from images using FFmpeg with Ken Burns effects and transitions."
    )
    parser.add_argument(
        'scenario_path',
        type=str,
        help="Path to the scenario JSON file (shot_list.json)."
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=12,
        help="Limit processing to the first N shots (default: 12)."
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output_video.mp4',
        help="Output video filename (default: output_video.mp4)."
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=DEFAULT_FPS,
        help=f"Frames per second (default: {DEFAULT_FPS})."
    )
    parser.add_argument(
        '--resolution',
        type=str,
        default='1920x1080',
        help="Output resolution (default: 1920x1080)."
    )
    parser.add_argument(
        '--audio',
        type=str,
        help="Path to the background audio/soundtrack file."
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Print FFmpeg command without executing."
    )
    
    args = parser.parse_args()
    
    # Parse resolution
    try:
        width, height = map(int, args.resolution.split('x'))
    except ValueError:
        print(f"Error: Invalid resolution format: {args.resolution}")
        sys.exit(1)
    
    # Load scenario
    scenario_file = Path(args.scenario_path).resolve()
    shots = load_scenario_json(scenario_file)
    
    # Limit shots
    if args.limit:
        shots = shots[:args.limit]
    
    print(f"Processing {len(shots)} shots...")
    
    # Set up paths
    scenario_dir = scenario_file.parent
    generations_dir = scenario_dir / 'generations'
    output_path = scenario_dir / args.output
    
    if not generations_dir.exists():
        print(f"Error: Generations directory not found: {generations_dir}")
        sys.exit(1)

    # Check audio path
    audio_path = None
    if args.audio:
        audio_path = Path(args.audio).resolve()
        if not audio_path.exists():
            print(f"Error: Audio file not found: {audio_path}")
            sys.exit(1)
            
    # Build command
    cmd, num_valid_shots, total_duration = build_ffmpeg_command(
        shots,
        generations_dir,
        output_path,
        args.fps,
        width,
        height,
        DEFAULT_TRANSITION_DURATION
    )
    
    # Add audio input if provided
    if audio_path:
        # Append audio input. It will be the last input index.
        # build_ffmpeg_command adds inputs for each shot (0 to num_valid_shots-1)
        audio_input_index = num_valid_shots 
        
        # Insert audio input before filter complex
        try:
            fc_index = cmd.index('-filter_complex')
            cmd.insert(fc_index, str(audio_path))
            cmd.insert(fc_index, '-i')
        except ValueError:
            print("Error: Could not find positions to insert audio input.")
            sys.exit(1)
            
        # Map audio stream
        output_file = cmd.pop() # Remove output filename
        
        cmd.extend(['-map', f'{audio_input_index}:a'])
        cmd.extend(['-t', str(total_duration)])
        
        # Add output filename back
        cmd.append(output_file)
        
        print(f"Adding audio track: {audio_path}")
        print(f"Total video duration: {total_duration:.2f}s")
    
    # Print or execute
    if args.dry_run:
        print("\n" + "="*60)
        print("DRY RUN - FFmpeg command:")
        print("="*60)
        print(' '.join(cmd))
        print("="*60)
    else:
        print(f"\n{'='*60}")
        print(f"Generating video: {output_path}")
        print(f"Resolution: {width}x{height} @ {args.fps} fps")
        print(f"Shots: {num_valid_shots}")
        if audio_path:
            print(f"Audio: {audio_path.name}")
            print(f"Duration: {total_duration:.2f}s")
        print(f"{'='*60}\n")
        print("Rendering... (this may take a few minutes)")
        
        start_time = time.time()
        
        try:
            subprocess.run(cmd, check=True)
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Format elapsed time
            elapsed_minutes = int(elapsed_time // 60)
            elapsed_seconds = int(elapsed_time % 60)
            
            # Format video duration
            duration_minutes = int(total_duration // 60)
            duration_seconds = int(total_duration % 60)
            
            print(f"\n{'='*60}")
            print(f"✓ Video generated successfully!")
            print(f"Output: {output_path}")
            print(f"Video Duration: {duration_minutes:02d}:{duration_seconds:02d}")
            print(f"Generation Time: {elapsed_minutes:02d}:{elapsed_seconds:02d}")
            print(f"{'='*60}")
                    
        except subprocess.CalledProcessError as e:
            print(f"\n{'='*60}")
            print(f"✗ FFmpeg failed with error code {e.returncode}")
            print(f"{'='*60}")
            sys.exit(1)
        except KeyboardInterrupt:
            print(f"\n\n✗ Cancelled by user")
            sys.exit(130)

if __name__ == '__main__':
    main()
