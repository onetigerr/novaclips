#!/usr/bin/env python3
"""
Тест для экспериментов с распознаванием субтитров.
Позволяет протестировать разные модели Whisper и настройки.

Usage:
    python tests/test_subtitle_recognition.py [--video PATH] [--model MODEL] [--device DEVICE]

Examples:
    python tests/test_subtitle_recognition.py --model tiny
    python tests/test_subtitle_recognition.py --model base --device cuda
    python tests/test_subtitle_recognition.py --model small --beam-size 10
"""

import argparse
import logging
import time
from pathlib import Path
from typing import List, Dict, Any

from faster_whisper import WhisperModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SubtitleRecognitionTest:
    """Тестирование распознавания субтитров с разными моделями."""
    
    AVAILABLE_MODELS = [
        "tiny",      # ~75 MB, fastest, lowest quality
        "base",      # ~150 MB, fast, low quality
        "small",     # ~500 MB, moderate speed, good quality
        "medium",    # ~1.5 GB, slower, better quality
        "large-v2",  # ~3 GB, slowest, best quality
        "large-v3",  # ~3 GB, latest, best quality
    ]
    
    def __init__(
        self,
        video_path: Path,
        output_dir: Path,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        self.video_path = Path(video_path)
        self.output_dir = Path(output_dir)
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized test with:")
        logger.info(f"  Video: {self.video_path}")
        logger.info(f"  Model: {self.model_size}")
        logger.info(f"  Device: {self.device}")
        logger.info(f"  Compute type: {self.compute_type}")
        logger.info(f"  Output: {self.output_dir}")
    
    def run_transcription(
        self,
        beam_size: int = 5,
        language: str = None,
        task: str = "transcribe",
        vad_filter: bool = False,
        word_timestamps: bool = False
    ) -> Dict[str, Any]:
        """
        Запуск транскрипции с заданными параметрами.
        
        Args:
            beam_size: Размер луча для beam search (больше = точнее, но медленнее)
            language: Язык аудио (None = автоопределение)
            task: "transcribe" или "translate" (для перевода на английский)
            vad_filter: Использовать ли VAD фильтр для удаления тишины
            word_timestamps: Получать ли временные метки для каждого слова
            
        Returns:
            Статистика распознавания
        """
        logger.info("="*80)
        logger.info(f"Starting transcription with beam_size={beam_size}, lang={language}, vad={vad_filter}")
        
        start_time = time.time()
        
        try:
            # Load model
            logger.info(f"Loading {self.model_size} model...")
            model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded in {load_time:.2f}s")
            
            # Transcribe
            logger.info("Transcribing...")
            transcribe_start = time.time()
            
            segments, info = model.transcribe(
                str(self.video_path),
                beam_size=beam_size,
                language=language,
                task=task,
                vad_filter=vad_filter,
                word_timestamps=word_timestamps
            )
            
            # Collect results
            results = []
            total_chars = 0
            
            for segment in segments:
                segment_data = {
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip(),
                    'avg_logprob': segment.avg_logprob,
                    'no_speech_prob': segment.no_speech_prob
                }
                
                if word_timestamps and hasattr(segment, 'words'):
                    segment_data['words'] = [
                        {
                            'word': w.word,
                            'start': w.start,
                            'end': w.end,
                            'probability': w.probability
                        }
                        for w in segment.words
                    ]
                
                results.append(segment_data)
                total_chars += len(segment_data['text'])
            
            transcribe_time = time.time() - transcribe_start
            total_time = time.time() - start_time
            
            # Statistics
            stats = {
                'model_size': self.model_size,
                'device': self.device,
                'beam_size': beam_size,
                'language': language or info.language,
                'language_probability': info.language_probability,
                'duration': info.duration,
                'vad_filter': vad_filter,
                'segments_count': len(results),
                'total_chars': total_chars,
                'load_time': load_time,
                'transcribe_time': transcribe_time,
                'total_time': total_time,
                'results': results
            }
            
            logger.info(f"Detected language: {stats['language']} (probability: {stats['language_probability']:.2%})")
            logger.info(f"Duration: {stats['duration']:.2f}s")
            logger.info(f"Segments: {stats['segments_count']}")
            logger.info(f"Total characters: {stats['total_chars']}")
            logger.info(f"Transcription time: {transcribe_time:.2f}s")
            logger.info(f"Total time: {total_time:.2f}s")
            
            return stats
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            raise
    
    def save_srt(self, results: List[Dict[str, Any]], filename: str):
        """Сохранить результаты в SRT формате."""
        srt_path = self.output_dir / filename
        
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(results, start=1):
                start = self._format_timestamp(segment['start'])
                end = self._format_timestamp(segment['end'])
                text = segment['text']
                
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")
        
        logger.info(f"Saved SRT to: {srt_path}")
        return srt_path
    
    def save_text(self, results: List[Dict[str, Any]], filename: str):
        """Сохранить только текст."""
        txt_path = self.output_dir / filename
        
        with open(txt_path, "w", encoding="utf-8") as f:
            for segment in results:
                f.write(segment['text'] + "\n")
        
        logger.info(f"Saved text to: {txt_path}")
        return txt_path
    
    def save_detailed_report(self, stats: Dict[str, Any], filename: str):
        """Сохранить детальный отчет с метриками."""
        report_path = self.output_dir / filename
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("SUBTITLE RECOGNITION TEST REPORT\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Model: {stats['model_size']}\n")
            f.write(f"Device: {stats['device']}\n")
            f.write(f"Beam Size: {stats['beam_size']}\n")
            f.write(f"VAD Filter: {stats['vad_filter']}\n")
            f.write(f"\n")
            
            f.write(f"Detected Language: {stats['language']}\n")
            f.write(f"Language Probability: {stats['language_probability']:.2%}\n")
            f.write(f"Video Duration: {stats['duration']:.2f}s\n")
            f.write(f"\n")
            
            f.write(f"Segments Count: {stats['segments_count']}\n")
            f.write(f"Total Characters: {stats['total_chars']}\n")
            f.write(f"\n")
            
            f.write(f"Model Load Time: {stats['load_time']:.2f}s\n")
            f.write(f"Transcription Time: {stats['transcribe_time']:.2f}s\n")
            f.write(f"Total Time: {stats['total_time']:.2f}s\n")
            f.write(f"\n")
            
            f.write("="*80 + "\n")
            f.write("TRANSCRIPTION RESULTS\n")
            f.write("="*80 + "\n\n")
            
            for i, segment in enumerate(stats['results'], start=1):
                f.write(f"[{i}] {self._format_timestamp(segment['start'])} --> {self._format_timestamp(segment['end'])}\n")
                f.write(f"    {segment['text']}\n")
                f.write(f"    (avg_logprob: {segment['avg_logprob']:.3f}, no_speech_prob: {segment['no_speech_prob']:.3f})\n")
                f.write(f"\n")
        
        logger.info(f"Saved detailed report to: {report_path}")
        return report_path
    
    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Форматирование временной метки в HH:MM:SS,mmm."""
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        mils = int((seconds - int(seconds)) * 1000)
        
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{mils:03d}"


def compare_models(video_path: Path, output_dir: Path, models: List[str]):
    """Сравнить несколько моделей на одном видео."""
    logger.info("="*80)
    logger.info("COMPARING MODELS")
    logger.info("="*80)
    
    comparison_results = []
    
    for model_name in models:
        logger.info(f"\nTesting model: {model_name}")
        
        test = SubtitleRecognitionTest(
            video_path=video_path,
            output_dir=output_dir / model_name,
            model_size=model_name,
            device="cpu",
            compute_type="int8"
        )
        
        stats = test.run_transcription(beam_size=5)
        
        # Save results
        test.save_srt(stats['results'], f"{model_name}.srt")
        test.save_text(stats['results'], f"{model_name}.txt")
        test.save_detailed_report(stats, f"{model_name}_report.txt")
        
        comparison_results.append({
            'model': model_name,
            'language': stats['language'],
            'lang_prob': stats['language_probability'],
            'segments': stats['segments_count'],
            'chars': stats['total_chars'],
            'time': stats['total_time']
        })
    
    # Save comparison summary
    summary_path = output_dir / "comparison_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write("MODEL COMPARISON SUMMARY\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"{'Model':<15} {'Lang':<8} {'Prob':<8} {'Segs':<8} {'Chars':<10} {'Time (s)':<10}\n")
        f.write("-"*80 + "\n")
        
        for r in comparison_results:
            f.write(
                f"{r['model']:<15} "
                f"{r['language']:<8} "
                f"{r['lang_prob']:<8.2%} "
                f"{r['segments']:<8} "
                f"{r['chars']:<10} "
                f"{r['time']:<10.2f}\n"
            )
    
    logger.info(f"\nComparison summary saved to: {summary_path}")
    logger.info("\n" + "="*80)
    logger.info("COMPARISON COMPLETE")
    logger.info("="*80)


def main():
    parser = argparse.ArgumentParser(
        description="Test subtitle recognition with different Whisper models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with single model
  python tests/test_subtitle_recognition.py --model small

  # Test with different beam size
  python tests/test_subtitle_recognition.py --model small --beam-size 10

  # Compare multiple models
  python tests/test_subtitle_recognition.py --compare tiny base small

  # Use GPU
  python tests/test_subtitle_recognition.py --model small --device cuda --compute-type float16

  # Enable VAD filter
  python tests/test_subtitle_recognition.py --model small --vad-filter
        """
    )
    
    parser.add_argument(
        "--video",
        type=str,
        default="/Users/onetiger/projects/py/novaclips/data/storage/raw/tg_111424_20251208_132414.mp4",
        help="Path to video file (default: provided test video)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="./data/tests/subtitle_recognition",
        help="Output directory for results (default: ./data/tests/subtitle_recognition)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="small",
        choices=SubtitleRecognitionTest.AVAILABLE_MODELS,
        help="Whisper model size (default: small)"
    )
    
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device to use (default: cpu)"
    )
    
    parser.add_argument(
        "--compute-type",
        type=str,
        default="int8",
        choices=["int8", "float16", "float32"],
        help="Compute type (default: int8)"
    )
    
    parser.add_argument(
        "--beam-size",
        type=int,
        default=5,
        help="Beam size for beam search (default: 5, higher = better quality but slower)"
    )
    
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Force specific language (default: auto-detect)"
    )
    
    parser.add_argument(
        "--vad-filter",
        action="store_true",
        help="Enable VAD filter to remove silence"
    )
    
    parser.add_argument(
        "--word-timestamps",
        action="store_true",
        help="Generate word-level timestamps"
    )
    
    parser.add_argument(
        "--compare",
        nargs="+",
        choices=SubtitleRecognitionTest.AVAILABLE_MODELS,
        help="Compare multiple models (e.g., --compare tiny base small)"
    )
    
    args = parser.parse_args()
    
    video_path = Path(args.video)
    output_dir = Path(args.output)
    
    # Validate video file
    if not video_path.exists():
        logger.error(f"Video file not found: {video_path}")
        return 1
    
    # Comparison mode
    if args.compare:
        compare_models(video_path, output_dir, args.compare)
        return 0
    
    # Single model test
    test = SubtitleRecognitionTest(
        video_path=video_path,
        output_dir=output_dir,
        model_size=args.model,
        device=args.device,
        compute_type=args.compute_type
    )
    
    stats = test.run_transcription(
        beam_size=args.beam_size,
        language=args.language,
        vad_filter=args.vad_filter,
        word_timestamps=args.word_timestamps
    )
    
    # Save results
    test.save_srt(stats['results'], f"{args.model}.srt")
    test.save_text(stats['results'], f"{args.model}.txt")
    test.save_detailed_report(stats, f"{args.model}_report.txt")
    
    logger.info("\n" + "="*80)
    logger.info("TEST COMPLETE!")
    logger.info("="*80)
    logger.info(f"Results saved to: {output_dir}")
    
    return 0


if __name__ == "__main__":
    exit(main())
