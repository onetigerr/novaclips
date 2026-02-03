# Модуль: visuals.image_generator

> **Назначение:** Генерация картинок для сцен через API (DALL-E, Midjourney, Stable Diffusion).

---

## Обзор

Модуль отвечает за:
- Генерацию картинок по промптам
- Поддержку нескольких провайдеров
- Retry при неудачах
- Сохранение и именование файлов

---

## Входные/Выходные данные

**Вход:** `planning/scenes.yaml` (промпты из visual.prompt)
**Выход:** `frames/scene-001.png`, `frames/scene-002.png`, ...

---

## API

### Python

```python
from novaclips.visuals.image_generator import ImageGenerator

generator = ImageGenerator(provider="openai", style="photorealistic")
generator.generate_all(
    scenes_path="planning/scenes.yaml",
    output_dir="frames/",
    resolution="1920x1080"
)

# Регенерация одной сцены
generator.regenerate_scene(scene_id=3, output_dir="frames/")
```

### CLI

```bash
novaclips visuals generate --project data/projects/my-video --provider openai
novaclips visuals regenerate --project data/projects/my-video --scene 3
```

---

## Структура кода

```
src/novaclips/visuals/image_generator/
├── __init__.py
├── generator.py        # ImageGenerator
├── providers/
│   ├── base.py         # BaseImageProvider
│   ├── openai_dalle.py # DALL-E
│   └── replicate_sd.py # Stable Diffusion via Replicate
├── prompt_enhancer.py  # Улучшение промптов
└── models.py
```

---

## Провайдеры

### DALL-E (OpenAI)

```python
class OpenAIDalleProvider(BaseImageProvider):
    def generate(self, prompt: str, size: str = "1792x1024") -> bytes:
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,  # 1024x1024, 1792x1024, 1024x1792
            quality="hd",
            n=1
        )
        image_url = response.data[0].url
        return self._download_image(image_url)
```

### Stable Diffusion (Replicate)

```python
class ReplicateSDProvider(BaseImageProvider):
    def generate(self, prompt: str, size: str = "1920x1080") -> bytes:
        output = replicate.run(
            "stability-ai/sdxl:...",
            input={
                "prompt": prompt,
                "width": 1920,
                "height": 1080,
                "num_outputs": 1
            }
        )
        return self._download_image(output[0])
```

---

## Улучшение промптов

```python
class PromptEnhancer:
    """Добавляет style prefix/suffix к промптам."""
    
    STYLES = {
        "photorealistic": "Ultra-realistic photograph, 8K, professional lighting, ",
        "illustration": "Digital illustration, vibrant colors, modern style, ",
        "minimalist": "Clean minimalist design, solid colors, simple shapes, "
    }
    
    def enhance(self, prompt: str, style: str, visual_type: str) -> str:
        prefix = self.STYLES.get(style, "")
        suffix = ", high quality, detailed"
        return f"{prefix}{prompt}{suffix}"
```

---

## Модели данных

```python
@dataclass
class ImageRequest:
    scene_id: int
    prompt: str
    visual_type: str  # diagram, example, metaphor...
    resolution: str = "1920x1080"

@dataclass
class ImageResult:
    scene_id: int
    image_bytes: bytes
    file_path: str
    prompt_used: str
```

---

## Основной генератор

```python
class ImageGenerator:
    def __init__(self, provider: str = "openai", style: str = "photorealistic"):
        self.provider = self._init_provider(provider)
        self.enhancer = PromptEnhancer()
        self.style = style
    
    def generate_all(self, scenes_path: str, output_dir: str, resolution: str):
        scenes = self._load_scenes(scenes_path)
        
        for scene in scenes:
            # Улучшаем промпт
            enhanced_prompt = self.enhancer.enhance(
                scene.visual.prompt,
                self.style,
                scene.visual.type
            )
            
            # Генерируем с retry
            for attempt in range(3):
                try:
                    image_bytes = self.provider.generate(enhanced_prompt, resolution)
                    break
                except Exception as e:
                    if attempt == 2:
                        raise
                    time.sleep(2 ** attempt)
            
            # Сохраняем
            output_path = f"{output_dir}/scene-{scene.id:03d}.png"
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
```

---

## Зависимости

```
openai>=1.0
replicate>=0.20
pillow>=10.0
requests>=2.31
```

---

## Тестирование

```bash
pytest tests/visuals/test_image_generator.py -v
```
