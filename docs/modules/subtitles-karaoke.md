# Модуль: subtitles.karaoke

> **Назначение:** Добавление karaoke-эффекта к субтитрам (подсветка текущего слова).

---

## Обзор

Модуль добавляет эффект караоке: каждое слово подсвечивается в момент произнесения. Использует ASS-теги для анимации.

---

## Входные/Выходные данные

**Вход:** 
- `subtitles/subs.ass` — базовые субтитры
- `audio/voice.json` — word timestamps

**Выход:** `subtitles/subs-karaoke.ass`

---

## API

```python
from novaclips.subtitles.karaoke import KaraokeEffect

effect = KaraokeEffect(
    highlight_color="#FF69B4",  # Розовый
    background_box=True
)

effect.apply(
    subtitles_path="subtitles/subs.ass",
    timestamps_path="audio/voice.json",
    output_path="subtitles/subs-karaoke.ass"
)
```

---

## Алгоритм

1. Загружаем word boundaries из voice.json
2. Для каждой строки субтитров:
   - Находим слова и их тайминги
   - Генерируем ASS-события с подсветкой текущего слова
   - Добавляем фоновый бокс под активным словом

---

## ASS теги для караоке

```python
class KaraokeEffect:
    def generate_karaoke_line(
        self, 
        words: List[WordBoundary],
        highlight_color: str
    ) -> str:
        """Генерирует ASS-строку с караоке-эффектом."""
        parts = []
        
        for i, word in enumerate(words):
            duration_cs = int((word.end_sec - word.start_sec) * 100)
            
            # ASS тег: \k{длительность} — караоке
            # Или \K — мгновенная подсветка
            parts.append(f"{{\\kf{duration_cs}}}{word.word}")
        
        return " ".join(parts)
    
    def generate_highlight_box(
        self,
        word: str,
        x: int, y: int,
        color: str
    ) -> str:
        """Генерирует рисунок фонового бокса."""
        # ASS drawing mode для бокса
        w, h = self._measure_text(word)
        padding = 10
        
        return (
            f"{{\\p1\\c&H{color}&}}"
            f"m 0 0 l {w+padding*2} 0 l {w+padding*2} {h+padding*2} l 0 {h+padding*2}"
            f"{{\\p0}}"
        )
```

---

## Стиль подсветки

```python
@dataclass
class KaraokeStyle:
    highlight_color: str = "&H00B469FF"  # RGB: FF69B4 (розовый)
    normal_color: str = "&H00FFFFFF"      # Белый
    background_box: bool = True
    box_color: str = "&H00B469FF"
    box_padding: int = 10
    box_radius: int = 8  # Скругление
```

---

## Зависимости

```
pydantic>=2.0
```
