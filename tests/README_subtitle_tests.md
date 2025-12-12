# Subtitle Recognition Tests

## Описание

Набор тестов для экспериментов с распознаванием субтитров. Позволяет протестировать разные модели Whisper, настройки и получить детальную статистику качества распознавания.

## Доступные модели

- `tiny` - ~75 MB, самая быстрая, низкое качество
- `base` - ~150 MB, быстрая, среднее качество
- `small` - ~500 MB, умеренная скорость, хорошее качество (**текущая по умолчанию**)
- `medium` - ~1.5 GB, медленнее, лучше качество
- `large-v2` - ~3 GB, медленная, отличное качество
- `large-v3` - ~3 GB, самая новая, лучшее качество

## Использование

### Базовый тест с одной моделью

```bash
# Тест с моделью small (по умолчанию)
python tests/test_subtitle_recognition.py

# Тест с другой моделью
python tests/test_subtitle_recognition.py --model tiny
python tests/test_subtitle_recognition.py --model medium
```

### Сравнение нескольких моделей

```bash
# Сравнить 3 модели
python tests/test_subtitle_recognition.py --compare tiny base small

# Сравнить все легкие модели
python tests/test_subtitle_recognition.py --compare tiny base small medium
```

### Настройки качества

```bash
# Увеличить beam size для лучшего качества (медленнее)
python tests/test_subtitle_recognition.py --model small --beam-size 10

# Включить VAD фильтр (удаление тишины)
python tests/test_subtitle_recognition.py --model small --vad-filter

# Получить временные метки для каждого слова
python tests/test_subtitle_recognition.py --model small --word-timestamps
```

### GPU и производительность

```bash
# Использовать GPU (если доступен)
python tests/test_subtitle_recognition.py --model small --device cuda --compute-type float16

# CPU с разными типами вычислений
python tests/test_subtitle_recognition.py --model small --device cpu --compute-type int8
python tests/test_subtitle_recognition.py --model small --device cpu --compute-type float32
```

### Указать язык

```bash
# Автоопределение языка (по умолчанию)
python tests/test_subtitle_recognition.py --model small

# Принудительно указать русский язык
python tests/test_subtitle_recognition.py --model small --language ru

# Указать английский язык
python tests/test_subtitle_recognition.py --model small --language en
```

### Свой видеофайл

```bash
# Указать другой видеофайл
python tests/test_subtitle_recognition.py --video /path/to/video.mp4 --model small
```

## Результаты

Результаты сохраняются в `./data/tests/subtitle_recognition/[model_name]/`:

- `{model}.srt` - субтитры в формате SRT
- `{model}.txt` - только текст (без временных меток)
- `{model}_report.txt` - детальный отчет с метриками

### Пример структуры результатов

```
data/tests/subtitle_recognition/
├── small/
│   ├── small.srt
│   ├── small.txt
│   └── small_report.txt
├── medium/
│   ├── medium.srt
│   ├── medium.txt
│   └── medium_report.txt
└── comparison_summary.txt  (при использовании --compare)
```

## Метрики в отчете

Каждый отчет включает:

- **Model Info**: размер модели, устройство, параметры
- **Language Detection**: определенный язык и вероятность
- **Statistics**: количество сегментов, символов
- **Performance**: время загрузки модели, время транскрипции
- **Segment Details**: полная транскрипция с временными метками и метриками качества для каждого сегмента

## Рекомендации

### Для быстрых экспериментов
```bash
python tests/test_subtitle_recognition.py --compare tiny base small
```

### Для проверки качества
```bash
python tests/test_subtitle_recognition.py --model small --beam-size 10 --vad-filter
```

### Для production
```bash
# Сначала тестируем разные модели
python tests/test_subtitle_recognition.py --compare small medium large-v3

# Потом выбираем оптимальную по соотношению скорость/качество
```

## Анализ результатов

1. **Сравните файлы `.txt`** - какая модель лучше распознает текст
2. **Проверьте `_report.txt`** - метрики качества (avg_logprob, no_speech_prob)
3. **Сравните время** - скорость обработки разных моделей
4. **Проверьте `.srt`** - точность временных меток

## Troubleshooting

### Модель загружается слишком долго
- Используйте меньшую модель (tiny, base)
- Модели кэшируются после первой загрузки

### Плохое качество распознавания
- Попробуйте большую модель (medium, large-v3)
- Увеличьте beam_size (--beam-size 10)
- Включите VAD фильтр (--vad-filter)
- Принудительно укажите язык (--language ru)

### Out of memory на GPU
- Используйте CPU (--device cpu)
- Используйте меньшую модель
- Используйте int8 вместо float16 (--compute-type int8)
