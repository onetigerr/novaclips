# Модуль: subtitles.generator

> **Назначение:** Генерация субтитров в формате ASS из word timestamps.

---

## Обзор

Модуль отвечает за:
- Создание ASS/SRT субтитров
- Разбиение текста на строки по длине/смыслу
- Применение стилей (шрифт, цвет, позиция)

---

## Входные/Выходные данные

**Вход:** `audio/voice.json` (word_boundaries)
**Выход:** `subtitles/subs.ass`

---

## API

### Python

```python
from novaclips.subtitles.generator import SubtitleGenerator

generator = SubtitleGenerator(
    font="Inter",
    font_size=48,
    max_chars_per_line=35,
    position="bottom"
)

generator.generate(
    timestamps_path="audio/voice.json",
    output_path="subtitles/subs.ass"
)
```

### CLI

```bash
novaclips subtitles generate --project data/projects/my-video
```

---

## Структура кода

```
src/novaclips/subtitles/generator/
├── __init__.py
├── generator.py        # SubtitleGenerator
├── line_breaker.py     # Разбиение на строки
├── ass_writer.py       # Запись ASS формата
└── models.py
```

---

## Разбиение на строки

```python
class LineBreaker:
    """Разбивает поток слов на строки субтитров."""
    
    def __init__(self, max_chars: int = 35, max_words: int = 6):
        self.max_chars = max_chars
        self.max_words = max_words
    
    def break_into_lines(self, words: List[WordBoundary]) -> List[SubtitleLine]:
        lines = []
        current_line = []
        current_chars = 0
        
        for word in words:
            word_len = len(word.word)
            
            # Проверка: поместится ли слово в текущую строку
            if (current_chars + word_len + 1 > self.max_chars or 
                len(current_line) >= self.max_words):
                # Сохраняем текущую строку
                if current_line:
                    lines.append(self._create_line(current_line))
                current_line = [word]
                current_chars = word_len
            else:
                current_line.append(word)
                current_chars += word_len + 1
        
        if current_line:
            lines.append(self._create_line(current_line))
        
        return lines
    
    def _create_line(self, words: List[WordBoundary]) -> SubtitleLine:
        return SubtitleLine(
            text=" ".join(w.word for w in words),
            start_sec=words[0].start_sec,
            end_sec=words[-1].end_sec,
            words=words
        )
```

---

## ASS формат

```python
class ASSWriter:
    """Генерирует файл ASS."""
    
    def write(self, lines: List[SubtitleLine], style: SubtitleStyle, path: str):
        content = self._generate_header(style)
        content += self._generate_styles(style)
        content += self._generate_events(lines)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_header(self, style: SubtitleStyle) -> str:
        return f"""[Script Info]
Title: NovaClips Subtitles
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

"""
    
    def _generate_styles(self, style: SubtitleStyle) -> str:
        return f"""[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: Default,{style.font},{style.font_size},&H00FFFFFF,&H00000000,&H80000000,1,2,0,2,10,10,50

"""
    
    def _generate_events(self, lines: List[SubtitleLine]) -> str:
        result = "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        
        for line in lines:
            start = self._format_time(line.start_sec)
            end = self._format_time(line.end_sec)
            text = line.text.upper()  # Заглавные буквы
            result += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"
        
        return result
    
    def _format_time(self, sec: float) -> str:
        """Конвертирует секунды в ASS формат H:MM:SS.CS"""
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = sec % 60
        return f"{h}:{m:02d}:{s:05.2f}"
```

---

## Модели данных

```python
@dataclass
class SubtitleLine:
    text: str
    start_sec: float
    end_sec: float
    words: List[WordBoundary]

@dataclass
class SubtitleStyle:
    font: str = "Inter"
    font_size: int = 48
    primary_color: str = "&H00FFFFFF"  # Белый
    outline_color: str = "&H00000000"  # Чёрный
    outline_width: int = 2
    alignment: int = 2  # Bottom center
```

---

## Зависимости

```
pydantic>=2.0
```

---

## Тестирование

```bash
pytest tests/subtitles/test_generator.py -v
```
