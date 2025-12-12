#!/usr/bin/env python3
"""
Скрипт для быстрого тестирования различных параметров модели small.
Помогает найти оптимальные настройки без необходимости переключаться на medium.

Usage:
    python tests/test_subtitle_optimization.py
"""

import logging
from pathlib import Path

from tests.test_subtitle_recognition import SubtitleRecognitionTest

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    video_path = Path("/Users/onetiger/projects/py/novaclips/data/storage/raw/tg_111424_20251208_132414.mp4")
    base_output = Path("./data/tests/subtitle_optimization")
    
    logger.info("="*80)
    logger.info("TESTING DIFFERENT PARAMETERS FOR 'small' MODEL")
    logger.info("="*80)
    
    # Набор тестов с разными параметрами
    test_configs = [
        {
            'name': 'baseline',
            'beam_size': 5,
            'vad_filter': False,
            'language': None
        },
        {
            'name': 'beam_10',
            'beam_size': 10,
            'vad_filter': False,
            'language': None
        },
        {
            'name': 'with_vad',
            'beam_size': 5,
            'vad_filter': True,
            'language': None
        },
        {
            'name': 'forced_ru',
            'beam_size': 5,
            'vad_filter': False,
            'language': 'ru'
        },
        {
            'name': 'beam_10_ru',
            'beam_size': 10,
            'vad_filter': False,
            'language': 'ru'
        },
        {
            'name': 'beam_10_vad_ru',
            'beam_size': 10,
            'vad_filter': True,
            'language': 'ru'
        }
    ]
    
    results = []
    
    for config in test_configs:
        logger.info(f"\n{'='*80}")
        logger.info(f"Testing: {config['name']}")
        logger.info(f"  beam_size={config['beam_size']}, vad={config['vad_filter']}, lang={config['language']}")
        logger.info(f"{'='*80}")
        
        output_dir = base_output / config['name']
        
        test = SubtitleRecognitionTest(
            video_path=video_path,
            output_dir=output_dir,
            model_size="small",
            device="cpu",
            compute_type="int8"
        )
        
        stats = test.run_transcription(
            beam_size=config['beam_size'],
            language=config['language'],
            vad_filter=config['vad_filter']
        )
        
        # Save results
        test.save_srt(stats['results'], "output.srt")
        test.save_text(stats['results'], "output.txt")
        test.save_detailed_report(stats, "report.txt")
        
        # Collect for summary
        results.append({
            'config': config['name'],
            'beam_size': config['beam_size'],
            'vad_filter': config['vad_filter'],
            'language': config['language'] or 'auto',
            'segments': stats['segments_count'],
            'chars': stats['total_chars'],
            'time': stats['total_time'],
            'text': '\n'.join([s['text'] for s in stats['results']])
        })
    
    # Create summary
    summary_path = base_output / "optimization_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write("OPTIMIZATION TESTS FOR 'small' MODEL\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"{'Config':<20} {'Beam':<6} {'VAD':<6} {'Lang':<6} {'Segs':<6} {'Chars':<8} {'Time':<10}\n")
        f.write("-"*80 + "\n")
        
        for r in results:
            f.write(
                f"{r['config']:<20} "
                f"{r['beam_size']:<6} "
                f"{'Yes' if r['vad_filter'] else 'No':<6} "
                f"{r['language']:<6} "
                f"{r['segments']:<6} "
                f"{r['chars']:<8} "
                f"{r['time']:<10.2f}\n"
            )
        
        f.write("\n" + "="*80 + "\n")
        f.write("RECOGNIZED TEXT BY CONFIGURATION\n")
        f.write("="*80 + "\n\n")
        
        for r in results:
            f.write(f"### {r['config']}\n")
            f.write(f"beam_size={r['beam_size']}, vad={r['vad_filter']}, lang={r['language']}\n")
            f.write("-"*80 + "\n")
            f.write(r['text'] + "\n")
            f.write("\n")
    
    logger.info(f"\n{'='*80}")
    logger.info("OPTIMIZATION TESTS COMPLETE!")
    logger.info(f"{'='*80}")
    logger.info(f"Summary saved to: {summary_path}")
    logger.info(f"\nResults saved to: {base_output}/")
    logger.info(f"Check individual configurations in subdirectories:\n")
    for config in test_configs:
        logger.info(f"  - {config['name']}/")


if __name__ == "__main__":
    main()
