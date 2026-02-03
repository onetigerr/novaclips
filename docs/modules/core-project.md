# Модуль: core.project

> **Назначение:** Парсинг сценария, создание структуры проекта и управление конфигурацией.

---

## Обзор

Модуль `core.project` является фундаментом всей системы. Он:
- Парсит markdown-сценарий с разметкой сцен
- Создаёт структуру папок проекта
- Генерирует конфигурационные файлы
- Валидирует входные данные

---

## Входные данные

### Файл: `script/script-final.md`

```markdown
---
title: Название видео
duration_target: 5-10 min
voice: alloy
language: ru
---

## Сцена 1: Hook
[VISUAL: type=example, prompt="Описание визуала для генерации"]

Текст озвучки для этой сцены...

## Сцена 2: Основной контент
[VISUAL: type=diagram, prompt="Инфографика с тремя пунктами"]

Продолжение текста...
```

### Формат разметки `[VISUAL: ...]`

| Параметр | Обязательный | Описание |
|----------|--------------|----------|
| `type` | Да | Тип визуала: `example`, `diagram`, `checklist`, `timeline`, `metaphor`, `quote`, `infographic`, `character` |
| `prompt` | Да | Промпт для генерации картинки (в кавычках) |
| `duration` | Нет | Переопределение длительности сцены в секундах |
| `transition` | Нет | Переход: `fade`, `dissolve`, `slide`, `none` (default: `fade`) |

---

## Выходные данные

### Файл: `planning/scenes.yaml`

```yaml
scenes:
  - id: 1
    title: "Hook"
    text: "Текст озвучки для этой сцены..."
    visual:
      type: example
      prompt: "Описание визуала для генерации"
      duration: null
      transition: fade
    word_count: 8
    estimated_duration_sec: 4.8

  - id: 2
    title: "Основной контент"
    text: "Продолжение текста..."
    visual:
      type: diagram
      prompt: "Инфографика с тремя пунктами"
      duration: null
      transition: fade
    word_count: 2
    estimated_duration_sec: 1.2

metadata:
  total_scenes: 2
  total_words: 10
  estimated_duration_sec: 6.0
  language: ru
```

### Файл: `planning/config.yaml`

```yaml
project:
  title: "Название видео"
  duration_target: "5-10 min"
  created_at: "2024-01-15T10:00:00Z"

audio:
  voice: alloy
  language: ru
  speed: 1.0

video:
  resolution: "1920x1080"
  fps: 30
  format: mp4

subtitles:
  enabled: true
  style: karaoke
  font: "Inter"
  font_size: 48
```

---

## API модуля

### Python Interface

```python
from novaclips.core.project import ProjectParser

# Инициализация
parser = ProjectParser(project_path="data/projects/my-video")

# Парсинг сценария
result = parser.parse_script("script/script-final.md")

# Доступ к данным
scenes = result.scenes          # List[Scene]
config = result.config          # ProjectConfig
metadata = result.metadata      # ScriptMetadata

# Сохранение артефактов
parser.save_scenes("planning/scenes.yaml")
parser.save_config("planning/config.yaml")
```

### CLI Interface

```bash
# Парсинг сценария
novaclips project parse \
  --project data/projects/my-video \
  --script script/script-final.md

# Валидация сценария (без сохранения)
novaclips project validate \
  --project data/projects/my-video \
  --script script/script-final.md

# Создание структуры нового проекта
novaclips project init \
  --name "my-video" \
  --template default
```

---

## Структура кода

```
src/novaclips/core/project/
├── __init__.py
├── parser.py           # Основной парсер сценария
├── models.py           # Pydantic модели данных
├── validators.py       # Валидаторы входных данных
├── templates.py        # Шаблоны проектов
└── exceptions.py       # Кастомные исключения
```

---

## Модели данных (Pydantic)

### Scene

```python
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class VisualType(str, Enum):
    EXAMPLE = "example"
    DIAGRAM = "diagram"
    CHECKLIST = "checklist"
    TIMELINE = "timeline"
    METAPHOR = "metaphor"
    QUOTE = "quote"
    INFOGRAPHIC = "infographic"
    CHARACTER = "character"

class TransitionType(str, Enum):
    FADE = "fade"
    DISSOLVE = "dissolve"
    SLIDE = "slide"
    NONE = "none"

class Visual(BaseModel):
    type: VisualType
    prompt: str
    duration: Optional[float] = None  # секунды
    transition: TransitionType = TransitionType.FADE

class Scene(BaseModel):
    id: int
    title: str
    text: str
    visual: Visual
    word_count: int
    estimated_duration_sec: float  # ~0.6 сек на слово

class ScriptMetadata(BaseModel):
    total_scenes: int
    total_words: int
    estimated_duration_sec: float
    language: str
```

### ProjectConfig

```python
class AudioConfig(BaseModel):
    voice: str = "alloy"
    language: str = "ru"
    speed: float = 1.0

class VideoConfig(BaseModel):
    resolution: str = "1920x1080"
    fps: int = 30
    format: str = "mp4"

class SubtitleConfig(BaseModel):
    enabled: bool = True
    style: str = "karaoke"
    font: str = "Inter"
    font_size: int = 48

class ProjectConfig(BaseModel):
    title: str
    duration_target: str
    created_at: str
    audio: AudioConfig
    video: VideoConfig
    subtitles: SubtitleConfig
```

---

## Алгоритм парсинга

### Шаг 1: Парсинг YAML frontmatter

```python
import yaml
import re

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Извлекает YAML frontmatter из markdown."""
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError("Missing YAML frontmatter")
    
    frontmatter = yaml.safe_load(match.group(1))
    body = match.group(2)
    
    return frontmatter, body
```

### Шаг 2: Разбиение на сцены

```python
def split_into_scenes(body: str) -> list[dict]:
    """Разбивает markdown на сцены по заголовкам ## Сцена N:"""
    pattern = r'^## Сцена (\d+):\s*(.+)$'
    scenes = []
    current_scene = None
    
    for line in body.split('\n'):
        match = re.match(pattern, line)
        if match:
            if current_scene:
                scenes.append(current_scene)
            current_scene = {
                'id': int(match.group(1)),
                'title': match.group(2),
                'content': []
            }
        elif current_scene:
            current_scene['content'].append(line)
    
    if current_scene:
        scenes.append(current_scene)
    
    return scenes
```

### Шаг 3: Извлечение VISUAL тега

```python
def parse_visual_tag(content: str) -> Visual:
    """Парсит тег [VISUAL: ...]"""
    pattern = r'\[VISUAL:\s*(.+?)\]'
    match = re.search(pattern, content)
    
    if not match:
        raise ValueError("Missing [VISUAL: ...] tag")
    
    params_str = match.group(1)
    params = {}
    
    # Парсинг параметров: type=value, prompt="text with spaces"
    param_pattern = r'(\w+)=(?:"([^"]+)"|(\S+))'
    for m in re.finditer(param_pattern, params_str):
        key = m.group(1)
        value = m.group(2) or m.group(3)
        params[key] = value
    
    return Visual(
        type=VisualType(params['type']),
        prompt=params['prompt'],
        duration=float(params['duration']) if 'duration' in params else None,
        transition=TransitionType(params.get('transition', 'fade'))
    )
```

### Шаг 4: Извлечение текста озвучки

```python
def extract_voice_text(content: str) -> str:
    """Извлекает текст для озвучки (исключая теги)."""
    # Удаляем [VISUAL: ...] теги
    text = re.sub(r'\[VISUAL:.*?\]', '', content)
    # Удаляем пустые строки и лишние пробелы
    text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
    return text
```

### Шаг 5: Расчёт метрик

```python
def calculate_metrics(text: str) -> tuple[int, float]:
    """Считает слова и примерную длительность."""
    words = len(text.split())
    # Средняя скорость речи: ~150 слов/мин = 0.4 сек/слово
    # Для русского языка чуть медленнее: ~0.5-0.6 сек/слово
    SECONDS_PER_WORD = 0.6
    duration = words * SECONDS_PER_WORD
    return words, duration
```

---

## Валидация

### Правила валидации

| Правило | Тип | Сообщение об ошибке |
|---------|-----|---------------------|
| Есть frontmatter | Error | "Missing YAML frontmatter" |
| Есть `title` в frontmatter | Error | "Missing 'title' in frontmatter" |
| Минимум 1 сцена | Error | "Script must have at least 1 scene" |
| Каждая сцена имеет `[VISUAL:]` | Error | "Scene {id} missing [VISUAL:] tag" |
| `type` валидный | Error | "Invalid visual type: {type}" |
| `prompt` не пустой | Error | "Empty prompt in scene {id}" |
| Hook в первые 10 сек | Warning | "Consider adding a hook in the first 10 seconds" |
| Есть CTA | Warning | "Consider adding a CTA at the end" |

### Пример валидатора

```python
from typing import List
from dataclasses import dataclass

@dataclass
class ValidationIssue:
    level: str  # "error" | "warning"
    message: str
    scene_id: Optional[int] = None

def validate_script(scenes: List[Scene], config: ProjectConfig) -> List[ValidationIssue]:
    issues = []
    
    if not scenes:
        issues.append(ValidationIssue("error", "Script must have at least 1 scene"))
    
    for scene in scenes:
        if not scene.visual.prompt:
            issues.append(ValidationIssue(
                "error", 
                f"Empty prompt in scene {scene.id}",
                scene.id
            ))
    
    # Warning: нет hook в начале
    if scenes and scenes[0].estimated_duration_sec > 10:
        issues.append(ValidationIssue(
            "warning",
            "Consider adding a shorter hook in the first 10 seconds"
        ))
    
    return issues
```

---

## Зависимости

```
pyyaml>=6.0
pydantic>=2.0
```

---

## Тестирование

### Unit тесты

```python
# tests/core/test_project_parser.py

import pytest
from novaclips.core.project import ProjectParser

def test_parse_simple_script():
    content = '''---
title: Test Video
voice: alloy
---

## Сцена 1: Hook
[VISUAL: type=example, prompt="Test prompt"]

This is the first scene.
'''
    parser = ProjectParser()
    result = parser.parse_string(content)
    
    assert len(result.scenes) == 1
    assert result.scenes[0].title == "Hook"
    assert result.scenes[0].visual.type == "example"
    assert result.scenes[0].text == "This is the first scene."

def test_parse_visual_tag():
    tag = '[VISUAL: type=diagram, prompt="Complex prompt with spaces", transition=dissolve]'
    visual = parse_visual_tag(tag)
    
    assert visual.type == VisualType.DIAGRAM
    assert visual.prompt == "Complex prompt with spaces"
    assert visual.transition == TransitionType.DISSOLVE
```

### Интеграционные тесты

```bash
# Запуск всех тестов модуля
pytest tests/core/test_project*.py -v

# Запуск с coverage
pytest tests/core/ --cov=src/novaclips/core/project --cov-report=html
```

---

## Обработка ошибок

```python
class ProjectError(Exception):
    """Базовое исключение модуля."""
    pass

class ScriptParseError(ProjectError):
    """Ошибка парсинга сценария."""
    def __init__(self, message: str, line: int = None):
        self.line = line
        super().__init__(f"Line {line}: {message}" if line else message)

class ValidationError(ProjectError):
    """Ошибка валидации."""
    def __init__(self, issues: List[ValidationIssue]):
        self.issues = issues
        errors = [i for i in issues if i.level == "error"]
        super().__init__(f"Validation failed with {len(errors)} errors")
```

---

## Примеры использования

### Пример 1: Создание нового проекта

```python
from novaclips.core.project import ProjectParser

# Инициализация проекта
parser = ProjectParser(project_path="data/projects/my-video")
parser.init_project()  # Создаёт структуру папок

# Парсинг сценария
result = parser.parse_script("script/script-final.md")

# Вывод информации
print(f"Найдено {len(result.scenes)} сцен")
print(f"Примерная длительность: {result.metadata.estimated_duration_sec / 60:.1f} мин")

# Сохранение
parser.save_all()
```

### Пример 2: CLI использование

```bash
# Создать новый проект
novaclips project init --name "tutorial-video"

# Отредактировать сценарий
nano data/projects/tutorial-video/script/script-final.md

# Распарсить и проверить
novaclips project parse --project data/projects/tutorial-video

# Вывод:
# ✓ Parsed 5 scenes
# ✓ Estimated duration: 4.5 min
# ⚠ Warning: Consider adding a CTA at the end
# 
# Saved:
#   - planning/scenes.yaml
#   - planning/config.yaml
```
