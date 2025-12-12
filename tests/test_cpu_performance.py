#!/usr/bin/env python3
"""
Быстрый тест производительности с CPU_THREADS: 6
"""
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from novaclips.core.processing.subtitles import Subtitler

def main():
    video = Path("/Users/onetiger/projects/py/novaclips/data/storage/raw/tg_111424_20251208_132414.mp4")
    output = Path("./data/tests/cpu_threads_test/medium_6threads.mp4")
    output.parent.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ: medium модель с CPU_THREADS: 6")
    print("="*80)
    print(f"\nВидео: {video.name}")
    print(f"Модель: medium")
    print(f"CPU потоков: 6 (физических ядер)")
    print("\nЗапуск...\n")
    
    subtitler = Subtitler()
    
    print(f"Конфигурация:")
    print(f"  model_size: {subtitler.model_size}")
    print(f"  device: {subtitler.device}")
    print(f"  cpu_threads: {subtitler.cpu_threads}")
    print(f"  language: {subtitler.language}")
    print(f"  beam_size: {subtitler.beam_size}")
    print()
    
    start = time.time()
    
    success = subtitler.process(video, output)
    
    elapsed = time.time() - start
    
    print("\n" + "="*80)
    if success:
        print("✓ УСПЕШНО!")
        print("="*80)
        print(f"\n⏱️  Время обработки: {elapsed:.1f} секунд ({elapsed/60:.2f} минут)")
        
        # Сравнение с предыдущим результатом
        prev_time = 160  # из предыдущих тестов
        speedup = prev_time / elapsed
        saved = prev_time - elapsed
        
        print(f"\n📊 Сравнение:")
        print(f"  Без CPU_THREADS (4 потока по умолчанию): {prev_time}s")
        print(f"  С CPU_THREADS: 6:                         {elapsed:.1f}s")
        print(f"  Ускорение:                                 {speedup:.2f}x")
        print(f"  Сэкономлено времени:                       {saved:.1f}s ({saved/60:.1f} минут)")
        
        # Показать результат
        srt_file = output.with_suffix('.srt')
        if srt_file.exists():
            print(f"\n📄 Распознанный текст:")
            with open(srt_file, 'r') as f:
                lines = f.readlines()
                # Показать только текст (каждая 3я строка после номера и времени)
                for i in range(2, len(lines), 4):
                    if i < len(lines):
                        print(f"  {lines[i].strip()}")
    else:
        print("✗ ОШИБКА!")
        print("="*80)
        return 1
    
    print("\n" + "="*80)
    return 0

if __name__ == "__main__":
    exit(main())
