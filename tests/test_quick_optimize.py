#!/usr/bin/env python3
"""
Быстрый тест оптимизации small модели с лучшими параметрами.
"""

import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_subtitle_recognition import SubtitleRecognitionTest

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    video_path = Path("/Users/onetiger/projects/py/novaclips/data/storage/raw/tg_111424_20251208_132414.mp4")
    output_dir = Path("./data/tests/subtitle_final_optimized")
    
    print("\n" + "="*80)
    print("ТЕСТ ОПТИМИЗИРОВАННОЙ МОДЕЛИ SMALL")
    print("="*80)
    print("\nПроблема:")
    print("  • distil-large-v3: не работает на русском (выдаёт английский)")
    print("  • medium: слишком медленная (160 секунд)")
    print("  • small: быстрая (9 секунд), но плохое качество")
    print("\nРешение:")
    print("  • Оптимизируем small с лучшими параметрами:")
    print("    - beam_size=10 (лучшее качество)")
    print("    - language='ru' (принудительно русский)")
    print("    - vad_filter=True (удаление тишины)")
    print("="*80 + "\n")
    
    configs = [
        {
            'name': 'baseline_small',
            'beam_size': 5,
            'vad': False,
            'lang': None
        },
        {
            'name': 'beam10',
            'beam_size': 10,
            'vad': False,
            'lang': None
        },
        {
            'name': 'beam10_ru',
            'beam_size': 10,
            'vad': False,
            'lang': 'ru'
        },
        {
            'name': 'beam10_ru_vad',
            'beam_size': 10,
            'vad': True,
            'lang': 'ru'
        }
    ]
    
    print(f"Тестирую {len(configs)} конфигурации...\n")
    
    results = []
    
    for i, config in enumerate(configs, 1):
        print(f"[{i}/{len(configs)}] Тест: {config['name']}")
        print(f"  Параметры: beam={config['beam_size']}, vad={config['vad']}, lang={config['lang']}")
        
        test = SubtitleRecognitionTest(
            video_path=video_path,
            output_dir=output_dir / config['name'],
            model_size="small",
            device="cpu",
            compute_type="int8"
        )
        
        try:
            stats = test.run_transcription(
                beam_size=config['beam_size'],
                language=config['lang'],
                vad_filter=config['vad']
            )
            
            test.save_text(stats['results'], "output.txt")
            
            text = '\n'.join([s['text'] for s in stats['results']])
            
            print(f"  ✓ Время: {stats['total_time']:.1f}s")
            print(f"  ✓ Текст:")
            for seg in stats['results']:
                print(f"      {seg['text']}")
            print()
            
            results.append({
                'name': config['name'],
                'beam': config['beam_size'],
                'vad': config['vad'],
                'lang': config['lang'] or 'auto',
                'time': stats['total_time'],
                'text': text,
                'segments': stats['segments_count'],
                'chars': stats['total_chars']
            })
            
        except Exception as e:
            print(f"  ✗ Ошибка: {e}\n")
    
    # Сводка
    print("\n" + "="*80)
    print("СРАВНИТЕЛЬНАЯ ТАБЛИЦА")
    print("="*80)
    print(f"{'Конфигурация':<20} {'Beam':<6} {'VAD':<6} {'Lang':<6} {'Время':<10} {'Символов':<10}")
    print("-"*80)
    for r in results:
        print(
            f"{r['name']:<20} "
            f"{r['beam']:<6} "
            f"{'Да' if r['vad'] else 'Нет':<6} "
            f"{r['lang']:<6} "
            f"{r['time']:<10.1f} "
            f"{r['chars']:<10}"
        )
    
    print("\n" + "="*80)
    print("РАСПОЗНАННЫЙ ТЕКСТ")
    print("="*80)
    for r in results:
        print(f"\n### {r['name']}")
        print(r['text'])
    
    # Найти лучший результат
    print("\n" + "="*80)
    print("РЕКОМЕНДАЦИЯ")
    print("="*80)
    
    # Ищем конфигурацию с лучшим соотношением качество/скорость
    # Берём beam10_ru как оптимальную
    best = next((r for r in results if r['name'] == 'beam10_ru'), results[-1])
    
    print(f"\n✓ Рекомендуемая конфигурация: {best['name']}")
    print(f"  - beam_size: {best['beam']}")
    print(f"  - language: {best['lang']}")
    print(f"  - vad_filter: {best['vad']}")
    print(f"  - Время обработки: {best['time']:.1f}s")
    print(f"\nТекст:")
    print(best['text'])
    
    print("\n" + "="*80)
    print("ГОТОВО!")
    print("="*80)
    print(f"Результаты сохранены в: {output_dir}")
    
    return best


if __name__ == "__main__":
    best = main()
