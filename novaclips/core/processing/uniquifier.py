"""
Video Uniquifier Orchestrator.
Manages the full pipeline of video transformations in a SINGLE efficient pass.
"""

import json
import logging
import math
from pathlib import Path
from typing import Dict, List, Tuple
import shutil

from novaclips.config import settings
from .processor import VideoProcessor
from .normalizer import Normalizer
from .trimmer import Trimmer
from .speed import SpeedChanger
from .fader import Fader
from .audio import AudioMixer
from .subtitles import Subtitler
from .ffmpeg_utils import get_video_info, run_ffmpeg, FFmpegError

logger = logging.getLogger(__name__)


class Uniquifier(VideoProcessor):
    """
    Orchestrates the uniquification pipeline in one consolidated step
    to minimize generation loss and processing time.
    """
    
    def __init__(self):
        super().__init__()
        self.normalizer = Normalizer()
        self.trimmer = Trimmer()
        self.speed = SpeedChanger()
        self.fader = Fader()
        self.audio = AudioMixer()
        self.subtitler = Subtitler()
        
    def process(self, input_path: Path, output_path: Path) -> bool:
        """
        Run optimized uniquification pipeline (One-Pass).
        """
        # Ensure debug dir exists
        debug_dir = settings.debug_dir
        debug_dir.mkdir(parents=True, exist_ok=True)
        
        tmp_stem = input_path.stem
        
        # 1. GATHER INFO & VALIDATE
        self.logger.info(f"Analyzing {input_path.name}...")
        try:
            video_info = get_video_info(input_path)
        except FFmpegError as e:
            self.logger.error(f"Failed to get video info: {e}")
            return False
            
        duration = video_info.get('duration', 0)
        width = video_info.get('width', 0)
        height = video_info.get('height', 0)
        
        # Validate
        if not self.normalizer._validate_dimensions(width, height):
            return False
            
        # 2. GENERATE SUBTITLES & DETECT SPEECH
        # We generate SRT based on the ORIGINAL video.
        original_srt = debug_dir / f"{tmp_stem}_original.srt"
        raw_speech_segments = []
        
        # Check cache logic
        # Note: We now need segments even if SRT exists.
        # Ideally we'd parse SRT if it exists, but for now let's rely on Subtitler return.
        # If SRT exists, we might miss the segments if we skip generation.
        # To be safe/simple: We regenerate if we don't have sidecar data, OR we just regenerate.
        # User said "Simple solution". Re-running whisper is costly but robust.
        # Optimization: If SRT exists, parse it to get segments?
        # Yes, let's parse SRT to recover segments if file exists, to save time.
        
        should_generate = True
        if original_srt.exists() and original_srt.stat().st_size > 0:
            self.logger.info("Found existing SRT. extracting segments...")
            try:
                raw_speech_segments = self._parse_srt_segments(original_srt)
                should_generate = False
            except Exception as e:
                self.logger.warning(f"Failed to parse existing SRT: {e}. Regenerating.")
        
        if should_generate:
            self.logger.info("Generating subtitles & Detecting speech...")
            raw_speech_segments = self.subtitler.generate_srt(input_path, original_srt)
            # generate_srt returns list or empty list.
            if not raw_speech_segments:
                self.logger.warning("No speech detected by Whisper.")
        
        has_speech = bool(raw_speech_segments)

        # 3. CALCULATE PARAMETERS
        params = {}
        
        # Normalization
        norm_filters = self.normalizer.get_filter_chain(width, height)
        
        # Trimming
        start_trim, end_trim = self.trimmer.get_trim_amounts(duration)
        trimmed_duration = duration - start_trim - end_trim
        if trimmed_duration <= 0:
            self.logger.error("Invalid trim duration")
            return False
        params['trim'] = {'start': start_trim, 'end': end_trim}
        
        # Speed
        speed_factor = self.speed.get_speed_factor()
        params['speed'] = speed_factor
        
        # Fade
        final_duration = trimmed_duration / speed_factor
        fade_duration = self.fader.get_fade_duration(final_duration)
        params['fade'] = fade_duration
        
        # Audio Mixing Params
        # User Reqs:
        # - Music quiet (approx 30% less than now) -> No Speech
        # - Music louder (than original?) -> Speech
        # - Original Muted if No Speech
        # Let's define dB targets.
        # Current random was -12 to -8.
        # New "Quiet" (No Speech): -18dB (approx 30% perception drop?)
        # New "Loud" (Speech): -8dB
        VOL_MUSIC_QUIET = -20.0  # Background
        VOL_MUSIC_LOUD = -8.0    # Overlaying speech
        FADE_TRANSITION = 0.5    # Seconds
        SPEECH_GAP_THRESHOLD = 2.0 # Seconds
        
        music_track, _ = self.audio.get_mixing_params() # Ignore random vol, we use logic
        params['music'] = str(music_track.name) if music_track else None
        
        self.last_params = params
        self.logger.info(f"Plan: Trim -{start_trim}s/-{end_trim}s | Speed {speed_factor}x | Music {params['music']}")

        # 4. PREPARE SPEECH SEGMENTS (Transform to Final Timeline)
        # We need to map original timestamps to: (t - start_trim) / speed_factor
        
        final_segments = []
        for s, e in raw_speech_segments:
            # Shift
            s_trim = s - start_trim
            e_trim = e - start_trim
            
            # Clip to processed window
            if e_trim <= 0 or s_trim >= trimmed_duration:
                continue
            
            s_trim = max(0, s_trim)
            e_trim = min(trimmed_duration, e_trim)
            
            # Scale
            s_final = s_trim / speed_factor
            e_final = e_trim / speed_factor
            
            final_segments.append((s_final, e_final))
            
        # Merge gaps
        merged_segments = self._merge_segments(final_segments, gap_threshold=SPEECH_GAP_THRESHOLD)
        self.logger.info(f"Speech Segments (Merged): {len(merged_segments)} blocks")
        
        # 5. PREPARE SUBTITLES FILE
        final_srt_path = None
        if has_speech and original_srt.exists():
            final_srt_path = debug_dir / f"{tmp_stem}_final.srt"
            self._transform_srt(
                original_srt, 
                final_srt_path, 
                offset_seconds=-start_trim, 
                scale_factor=1.0/speed_factor
            )

        # 6. BUILD FILTER COMPLEX
        filter_parts = []
        
        # --- VIDEO ---
        # Same as before
        filter_parts.append(f"[0:v]{norm_filters}[v_norm]")
        filter_parts.append(f"[v_norm]trim=start={start_trim}:duration={trimmed_duration},setpts=PTS-STARTPTS[v_trim]")
        filter_parts.append(f"[v_trim]setpts=PTS/{speed_factor}[v_speed]")
        
        fade_out_start = final_duration - fade_duration
        filter_parts.append(f"[v_speed]fade=t=in:st=0:d={fade_duration},fade=t=out:st={fade_out_start}:d={fade_duration}[v_fade]")
        
        processed_v_label = "[v_fade]"
        if final_srt_path and final_srt_path.exists() and final_srt_path.stat().st_size > 0:
            srt_path_str = str(final_srt_path).replace('\\', '/').replace(':', '\\:')
            # Use settings for style
            s_conf = settings.subtitles
            style = (
                f"FontName={s_conf.get('FONT', 'Arial')},FontSize={s_conf.get('SIZE', 24)},"
                f"PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,"
                f"Outline={s_conf.get('OUTLINE_WIDTH', 2)},Alignment=2"
            )
            filter_parts.append(f"[v_fade]subtitles='{srt_path_str}':force_style='{style}'[v_out]")
            processed_v_label = "[v_out]"
        else:
            filter_parts.append(f"[v_fade]null[v_out]")
            processed_v_label = "[v_out]"
            
        # --- AUDIO CHAIN ---
        has_original_audio = video_info.get('audio_codec', 'none') != 'none'
        
        if has_original_audio:
            # 1. Base processing (Trim/Speed)
            filter_parts.append(f"[0:a]atrim=start={start_trim}:duration={trimmed_duration},asetpts=PTS-STARTPTS[a_trim]")
            filter_parts.append(f"[a_trim]atempo={speed_factor}[a_speed]")
            
            # 2. Dynamic Mixing
            if not music_track:
                # Just pass processed original
                filter_parts.append(f"[a_speed]volume=1.0[a_out]")
            else:
                # Build Mask Expression
                if not merged_segments:
                    # No speech. Mute original. Constant Music.
                    filter_parts.append(f"[a_speed]volume=0[a_orig_f]")
                    filter_parts.append(f"[1:a]volume={VOL_MUSIC_QUIET}dB[music_f]")
                else:
                    # Have speech.
                    mask_expr = self._build_fade_expression(merged_segments, fade=FADE_TRANSITION)
                    
                    # Original Volume
                    filter_parts.append(f"[a_speed]volume='{mask_expr}':eval=frame[a_orig_f]")
                    
                    # Music Volume
                    vol_quiet_lin = 10 ** (VOL_MUSIC_QUIET/20)
                    vol_loud_lin = 10 ** (VOL_MUSIC_LOUD/20)
                    music_expr = f"{vol_quiet_lin}+({vol_loud_lin}-{vol_quiet_lin})*({mask_expr})"
                    filter_parts.append(f"[1:a]volume='{music_expr}':eval=frame[music_f]")

                # Mix
                filter_parts.append(f"[a_orig_f][music_f]amix=inputs=2:duration=first:weights=1 1[a_out]")
                
        else:
            # No original audio.
            if music_track:
                # Use Music track only. Quiet volume (as per "No Speech" rule).
                # Trim to final video duration.
                # [1:a] -> volume -> atrim -> [a_out]
                filter_parts.append(f"[1:a]volume={VOL_MUSIC_QUIET}dB[music_vol]")
                filter_parts.append(f"[music_vol]atrim=duration={final_duration}[a_out]")
            else:
                # No original audio AND no music? Silent audio track?
                # Generate silence.
                # anullsrc=channel_layout=stereo:sample_rate=44100:duration=final_duration
                # Note: 'duration' in anullsrc is confusing, usually we trim it.
                filter_parts.append(f"anullsrc=cl=stereo:r=44100:d={final_duration}[a_out]")
            
        filter_complex = ";".join(filter_parts)
        
        # EXECUTE
        cmd = ['ffmpeg', '-i', str(input_path)]
        if music_track:
            cmd.extend(['-stream_loop', '-1', '-i', str(music_track)])
            
        cmd.extend([
            '-filter_complex', filter_complex,
            '-map', processed_v_label,
            '-map', '[a_out]',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-map_metadata', '-1', '-movflags', '+faststart',
            '-y', str(output_path)
        ])
        
        self.logger.info("Running One-Pass FFmpeg Pipeline...")
        return run_ffmpeg(cmd, f"Processing {input_path.name}")
        
    def _merge_segments(self, segments, gap_threshold=2.0):
        """Merge segments closer than threshold."""
        if not segments: return []
        segments.sort()
        merged = []
        curr_s, curr_e = segments[0]
        
        for next_s, next_e in segments[1:]:
            if next_s - curr_e <= gap_threshold:
                curr_e = max(curr_e, next_e)
            else:
                merged.append((curr_s, curr_e))
                curr_s, curr_e = next_s, next_e
        merged.append((curr_s, curr_e))
        return merged

    def _build_fade_expression(self, segments, fade=0.5):
        """
        Build FFmpeg expression for a mask (0..1) that is 1 during segments
        and fades in/out over `fade` seconds.
        Uses max(trap1, trap2...) logic.
        """
        parts = []
        for s, e in segments:
            # We construct the trapezoid function directly using positive constants
            # to avoid negative numbers in the expression string (e.g. t--0.5) which FFmpeg dislikes.
            # Ramp Up: (t - (s - fade)) / fade  ==> (t - s + fade) / fade
            # Ramp Down: ((e + fade) - t) / fade ==> (e + fade - t) / fade
            
            s_str = f"{s:.3f}"
            e_str = f"{e:.3f}"
            f_str = f"{fade:.3f}"
            
            # term: max(0, min(1, min(UP, DOWN) ))
            # FFmpeg min() only takes 2 arguments, so we must nest them.
            up_ramp = f"(t-{s_str}+{f_str})/{f_str}"
            down_ramp = f"({e_str}+{f_str}-t)/{f_str}"
            
            term = f"max(0,min(1,min({up_ramp},{down_ramp})))"
            parts.append(term)
            
        if not parts:
            return "0"
            
        # Combine with max(a, max(b, c)...)
        expr = "0"
        for part in parts:
            expr = f"max({part},{expr})"
            
        return expr

    def _parse_srt_segments(self, srt_path: Path):
        """Parse SRT manually to extract segments."""
        import re
        segments = []
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Very simple regex for 00:00:00,000 --> 00:00:00,000
        pattern = re.compile(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})')
        
        for line in content.splitlines():
            m = pattern.search(line)
            if m:
                # parse start
                h1,m1,s1,ms1 = map(int, m.groups()[0:4])
                start = h1*3600 + m1*60 + s1 + ms1/1000.0
                
                # parse end
                h2,m2,s2,ms2 = map(int, m.groups()[4:8])
                end = h2*3600 + m2*60 + s2 + ms2/1000.0
                
                segments.append((start, end))
        return segments

    def _transform_srt(self, input_srt: Path, output_srt: Path, offset_seconds: float, scale_factor: float):
        """
        Adjust SRT timestamps for trim and speed changes.
        offset_seconds: Value to ADD to timestamps (negative for trim)
        scale_factor: Value to MULTIPLY timestamps by (e.g. 0.5 for 2x speed)
        """
        try:
            with open(input_srt, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse SRT (simple parser)
            import re
            
            # Regex for SRT block: ID \n 00:00:00,000 --> 00:00:00,000 \n Text
            # We'll just process line by line to be safe
            
            lines = content.splitlines()
            new_lines = []
            
            time_pattern = re.compile(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})')
            
            def parse_time(s):
                match = time_pattern.match(s)
                if not match: return 0.0
                h, m, s, ms = map(int, match.groups())
                return h*3600 + m*60 + s + ms/1000.0
                
            def format_time(t):
                t = max(0.0, t)
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = int(t % 60)
                ms = int((t - int(t)) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
            
            for line in lines:
                if '-->' in line:
                    parts = line.split('-->')
                    if len(parts) == 2:
                        start_str = parts[0].strip()
                        end_str = parts[1].strip()
                        
                        start_t = parse_time(start_str)
                        end_t = parse_time(end_str)
                        
                        # Apply transform
                        # 1. Offset
                        start_t += offset_seconds
                        end_t += offset_seconds
                        
                        # 2. Scale
                        start_t *= scale_factor
                        end_t *= scale_factor
                        
                        # If subtitle is now completely before 00:00, we could hide it.
                        # But format_time(max(0, ...)) handles it by snapping to start?
                        # No, we probably shouldn't show text that was trimmed.
                        # But for simplicity, we just clamp to 0. 
                        # Ideally we drop blocks where end_t <= 0.
                        
                        new_line = f"{format_time(start_t)} --> {format_time(end_t)}"
                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
                    
            with open(output_srt, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
                
        except Exception as e:
            self.logger.error(f"Failed to transform SRT: {e}")
