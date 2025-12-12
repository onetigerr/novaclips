#!/usr/bin/env python3
"""
Автоматический тест оптимальной модели.
Тестирует distil-large-v3 - быстрая модель с качеством как у large.
"""

import logging
from pathlib import Path
import sys

# Добавляем путь к модулю
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_subtitle_recognition import SubtitleRecognitionTest

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    video_path = Path("/Users/onetiger/projects/py/novaclips/data/storage/raw/tg_111424_20251208_132414.mp4")
    output_dir = Path("./data/tests/subtitle_final")
    
    logger.info("="*80)
    logger.info("ТЕСТИРОВАНИЕ ОПТИМАЛЬНОЙ МОДЕЛИ")
    logger.info("="*80)
    logger.info("")
    logger.info("Проблема:")
    logger.info("  - small: быстро (9с), но плохое качество")
    logger.info("  - medium: отличное качество, но медленно (160с)")
    logger.info("")
    logger.info("Решение:")
    logger.info("  - Тестируем distil-large-v3: качество ~как у large, скорость в 6х быстрее")
    logger.info("="*80)
    
    # Тест distil-large-v3
    logger.info("\n[1/2] Тестирование distil-large-v3...")
    
    test_distil = SubtitleRecognitionTest(
        video_path=video_path,
        output_dir=output_dir / "distil-large-v3",
        model_size="distil-large-v3",
        device="cpu",
        compute_type="int8"
    )
    
    try:
        stats_distil = test_distil.run_transcription(
            beam_size=5,
            language="ru",
            vad_filter=False
        )
        
        test_distil.save_srt(stats_distil['results'], "output.srt")
        test_distil.save_text(stats_distil['results'], "output.txt")
        
        logger.info(f"\n✓ Distil-large-v3 результат:")
        logger.info(f"  Время: {stats_distil['total_time']:.2f}s")
        logger.info(f"  Текст:")
        for seg in stats_distil['results']:
            logger.info(f"    {seg['text']}")
            
    except Exception as e:
        logger.error(f"✗ Distil-large-v3 не доступна: {e}")
        logger.info("\n[FALLBACK] Пробуем оптимизировать small с лучшими параметрами...")
        stats_distil = None
    
    # Если distil не работает, оптимизируем small
    if stats_distil is None:
        logger.info("\n[2/2] Оптимизация small с beam_size=10 + language=ru...")
        
        test_small_opt = SubtitleRecognitionTest(
            video_path=video_path,
            output_dir=output_dir / "small-optimized",
            model_size="small",
            device="cpu",
            compute_type="int8"
        )
        
        stats_small = test_small_opt.run_transcription(
            beam_size=10,
            language="ru",
            vad_filter=True
        )
        
        test_small_opt.save_srt(stats_small['results'], "output.srt")
        test_small_opt.save_text(stats_small['results'], "output.txt")
        
        logger.info(f"\n✓ Small оптимизированная результат:")
        logger.info(f"  Время: {stats_small['total_time']:.2f}s")
        logger.info(f"  Текст:")
        for seg in stats_small['results']:
            logger.info(f"    {seg['text']}")
    
    logger.info("\n" + "="*80)
    logger.info("ТЕСТ ЗАВЕРШЕН")
    logger.info("="*80)
    logger.info(f"Результаты в: {output_dir}")


if __name__ == "__main__":
    main()
