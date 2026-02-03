# Модуль: audio.timestamp_extractor

> **Назначение:** Извлечение word-level timestamps из аудио через Whisper.

---

## Обзор

Модуль используется когда TTS API не возвращает timestamps нативно. Использует Whisper для транскрипции с точными временными метками.

---

## Входные/Выходные данные

**Вход:** `audio/voice.mp3`
**Выход:** `audio/voice.json` (word_boundaries)

---

## API

```python
from novaclips.audio.timestamp_extractor import TimestampExtractor

extractor = TimestampExtractor(model="base", language="ru")

boundaries = extractor.extract(
    audio_path="audio/voice.mp3",
    output_path="audio/voice.json"
)
```

---

## Реализация

```python
import whisper
from typing import List
from dataclasses import dataclass

@dataclass
class WordBoundary:
    word: str
    start_sec: float
    end_sec: float

class TimestampExtractor:
    def __init__(self, model: str = "base", language: str = "ru"):
        self.model = whisper.load_model(model)
        self.language = language
    
    def extract(self, audio_path: str) -> List[WordBoundary]:
        """Извлекает word-level timestamps."""
        result = self.model.transcribe(
            audio_path,
            word_timestamps=True,
            language=self.language
        )
        
        boundaries = []
        for segment in result.get("segments", []):
            for word_info in segment.get("words", []):
                boundaries.append(WordBoundary(
                    word=word_info["word"].strip(),
                    start_sec=word_info["start"],
                    end_sec=word_info["end"]
                ))
        
        return boundaries
```

---

## Модели Whisper

| Модель | Размер | Скорость | Качество |
|--------|--------|----------|----------|
| tiny | 39M | ★★★★★ | ★ |
| base | 74M | ★★★★ | ★★ |
| small | 244M | ★★★ | ★★★ |
| medium | 769M | ★★ | ★★★★ |
| large | 1550M | ★ | ★★★★★ |

**Рекомендация для MVP:** `base` — баланс скорости и качества.

---

## Зависимости

```
openai-whisper>=20231117
torch>=2.0
```
