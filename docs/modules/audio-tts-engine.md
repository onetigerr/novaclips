# Модуль: audio.tts_engine

> **Назначение:** Генерация озвучки (Text-to-Speech) с поддержкой нескольких провайдеров.

---

## Обзор

Модуль отвечает за:
- Нормализацию текста для TTS
- Генерацию озвучки через API (OpenAI, ElevenLabs)
- Получение word-level timestamps
- Fallback между провайдерами

---

## Входные/Выходные данные

**Вход:** `planning/scenes.yaml` + `planning/config.yaml`
**Выход:** 
- `audio/voice.mp3` — озвучка
- `audio/voice.json` — timestamps

---

## API

### Python

```python
from novaclips.audio.tts_engine import TTSEngine

engine = TTSEngine(provider="openai", voice="alloy", language="ru")
engine.synthesize_project(
    scenes_path="planning/scenes.yaml",
    output_audio="audio/voice.mp3",
    output_json="audio/voice.json"
)
```

### CLI

```bash
novaclips audio synthesize --project data/projects/my-video --voice alloy
```

---

## Структура кода

```
src/novaclips/audio/tts_engine/
├── __init__.py
├── engine.py           # TTSEngine
├── providers/
│   ├── base.py         # BaseTTSProvider
│   ├── openai_tts.py   # OpenAI
│   └── elevenlabs.py   # ElevenLabs
├── normalizer.py       # TextNormalizer
└── models.py           # Pydantic модели
```

---

## Нормализация текста

```python
class TextNormalizer:
    def normalize(self, text: str) -> str:
        """Числа→слова, %→проценты, $→долларов"""
        text = self._normalize_numbers(text)    # "2024" → "две тысячи..."
        text = self._normalize_percentages(text) # "50%" → "пятьдесят процентов"
        text = self._normalize_currencies(text)  # "$100" → "сто долларов"
        return text
```

---

## Провайдеры

### OpenAI TTS

```python
class OpenAITTSProvider(BaseTTSProvider):
    VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    def synthesize(self, text: str, voice: str, speed: float) -> TTSResult:
        response = self.client.audio.speech.create(
            model="tts-1-hd", voice=voice, input=text, speed=speed
        )
        word_boundaries = self._extract_via_whisper(response.content)
        return TTSResult(audio_bytes=response.content, word_boundaries=word_boundaries)
```

### ElevenLabs

```python
class ElevenLabsTTSProvider(BaseTTSProvider):
    def synthesize(self, text: str, voice: str, speed: float) -> TTSResult:
        response = self.client.text_to_speech.convert_with_timestamps(...)
        # ElevenLabs возвращает word boundaries нативно
        return TTSResult(audio_bytes=response.audio, word_boundaries=response.alignment)
```

---

## Модели данных

```python
@dataclass
class WordBoundary:
    word: str
    start_sec: float
    end_sec: float

@dataclass
class TTSResult:
    audio_bytes: bytes
    duration_sec: float
    word_boundaries: List[WordBoundary]
```

---

## Формат voice.json

```json
{
  "duration_sec": 245.5,
  "word_boundaries": [
    {"word": "Сегодня", "start_sec": 0.0, "end_sec": 0.45, "scene_id": 1}
  ],
  "scene_boundaries": [
    {"scene_id": 1, "start_sec": 0.0, "end_sec": 15.3}
  ]
}
```

---

## Зависимости

```
openai>=1.0
elevenlabs>=1.0
pydub>=0.25
openai-whisper>=20231117
num2words>=0.5
```

---

## Тестирование

```bash
pytest tests/audio/test_tts_engine.py -v
```
