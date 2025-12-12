#!/usr/bin/env python3
"""
Тест полного пайплайна уникализации с оптимизированными субтитрами.
"""
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from novaclips.core.processing.uniquifier import Uniquifier

def main():
    video = Path("/Users/onetiger/projects/py/novaclips/data/storage/raw/tg_111424_20251208_132414.mp4")
    output = Path("./data/tests/pipeline_test/final_output.mp4")
    output.parent.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("ПОЛНЫЙ ТЕСТ ПАЙПЛАЙНА УНИКАЛИЗАЦИИ")
    print("="*80)
    print(f"\n📹 Входное видео: {video.name}")
    print(f"📁 Выходной файл: {output}")
    print(f"🔧 DEBUG файлы: data/storage/debug/")
    print("\n" + "="*80)
    print("ЭТАПЫ ПАЙПЛАЙНА:")
    print("="*80)
    print("  1. Normalizer   - нормализация 1080x1920, 30fps")
    print("  2. Trimmer      - обрезка краёв")
    print("  3. SpeedChanger - изменение скорости ±3-7%")
    print("  4. Fader        - fade-in/out эффекты")
    print("  5. Subtitler    - субтитры (medium модель, 6 CPU потоков)")
    print("  6. AudioMixer   - наложение фоновой музыки")
    print("="*80)
    
    print("\n⏳ Запуск пайплайна...\n")
    
    uniquifier = Uniquifier()
    
    start = time.time()
    
    success = uniquifier.process(video, output)
    
    elapsed = time.time() - start
    
    print("\n" + "="*80)
    if success:
        print("✅ ПАЙПЛАЙН ЗАВЕРШЕН УСПЕШНО!")
        print("="*80)
        print(f"\n⏱️  Общее время: {elapsed:.1f} секунд ({elapsed/60:.1f} минут)")
        print(f"\n📊 Результаты:")
        print(f"  ✓ Финальное видео: {output}")
        print(f"  ✓ Размер: {output.stat().st_size / (1024*1024):.1f} MB")
        
        # Показать параметры трансформаций
        params = uniquifier.get_last_transform_params()
        print(f"\n📋 Параметры трансформаций:")
        print(params)
        
        # Проверить промежуточные файлы в debug
        from novaclips.config import settings
        debug_dir = settings.debug_dir
        debug_files = list(debug_dir.glob("*.mp4"))
        
        print(f"\n🔍 DEBUG файлы ({len(debug_files)}):")
        for f in sorted(debug_files):
            size_mb = f.stat().st_size / (1024*1024)
            print(f"  • {f.name:<40} ({size_mb:.1f} MB)")
        
        # Проверить SRT файл
        srt_files = list(debug_dir.glob("*.srt"))
        if srt_files:
            print(f"\n📄 Субтитры:")
            for srt in srt_files:
                print(f"  • {srt.name}")
                with open(srt, 'r') as f:
                    lines = f.readlines()
                    # Показать распознанный текст
                    print(f"\n  Распознанный текст:")
                    for i in range(2, len(lines), 4):
                        if i < len(lines):
                            print(f"    {lines[i].strip()}")
        
    else:
        print("❌ ПАЙПЛАЙН ЗАВЕРШИЛСЯ С ОШИБКОЙ!")
        print("="*80)
        return 1
    
    print("\n" + "="*80)
    print("✓ ТЕСТ ЗАВЕРШЕН")
    print("="*80)
    return 0

if __name__ == "__main__":
    exit(main())
