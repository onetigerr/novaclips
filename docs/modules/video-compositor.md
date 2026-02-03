# Модуль: video.compositor

> **Назначение:** Сборка видео из картинок + аудио с переходами и motion-эффектами.

---

## Обзор

Модуль отвечает за:
- Сборку видео из последовательности картинок
- Синхронизацию с аудиодорожкой
- Добавление переходов (fade, dissolve)
- Ken Burns эффект (zoom/pan)

---

## Входные/Выходные данные

**Вход:**
- `frames/scene-*.png` — картинки
- `audio/voice.mp3` — озвучка
- `planning/timing.yaml` — тайминг сцен

**Выход:** `video/draft.mp4`

---

## API

### Python

```python
from novaclips.video.compositor import VideoCompositor

compositor = VideoCompositor(
    resolution="1920x1080",
    fps=30,
    transition="fade",
    motion="zoom_slow"
)

compositor.compose(
    frames_dir="frames/",
    timing_path="planning/timing.yaml",
    audio_path="audio/voice.mp3",
    output_path="video/draft.mp4"
)
```

### CLI

```bash
novaclips video compose \
  --project data/projects/my-video \
  --transition fade \
  --motion zoom_slow
```

---

## Структура кода

```
src/novaclips/video/compositor/
├── __init__.py
├── compositor.py       # VideoCompositor
├── timeline.py         # Расчёт тайминга
├── transitions.py      # Переходы
├── motion.py           # Ken Burns эффекты
└── ffmpeg_builder.py   # Построитель FFmpeg команд
```

---

## Расчёт тайминга (timing.yaml)

```yaml
scenes:
  - scene_id: 1
    start_sec: 0.0
    end_sec: 15.3
    duration_sec: 15.3
    frame_path: "frames/scene-001.png"
    transition_in: fade
    transition_out: fade
    motion: zoom_in
    
  - scene_id: 2
    start_sec: 15.3
    end_sec: 45.2
    duration_sec: 29.9
    frame_path: "frames/scene-002.png"
```

---

## Переходы

```python
class TransitionType(Enum):
    NONE = "none"
    FADE = "fade"
    DISSOLVE = "dissolve"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"

class Transitions:
    FADE_DURATION = 0.5  # секунды
    
    @staticmethod
    def get_ffmpeg_filter(transition: TransitionType, duration: float) -> str:
        if transition == TransitionType.FADE:
            return f"fade=t=in:st=0:d={duration},fade=t=out:st={{end}}:d={duration}"
        elif transition == TransitionType.DISSOLVE:
            return f"xfade=transition=dissolve:duration={duration}:offset={{offset}}"
        return ""
```

---

## Ken Burns эффект

```python
class MotionType(Enum):
    NONE = "none"
    ZOOM_IN = "zoom_in"      # Медленное приближение
    ZOOM_OUT = "zoom_out"    # Медленное отдаление
    PAN_LEFT = "pan_left"    # Панорама влево
    PAN_RIGHT = "pan_right"  # Панорама вправо

class Motion:
    @staticmethod
    def get_ffmpeg_filter(motion: MotionType, duration: float) -> str:
        if motion == MotionType.ZOOM_IN:
            # Zoom от 1.0 до 1.1
            return f"zoompan=z='min(zoom+0.0005,1.1)':d={int(duration*30)}:s=1920x1080"
        elif motion == MotionType.ZOOM_OUT:
            return f"zoompan=z='if(lte(zoom,1.0),1.1,max(1.0,zoom-0.0005))':d={int(duration*30)}"
        return ""
```

---

## FFmpeg команда

```python
class FFmpegBuilder:
    def build_composition_command(
        self,
        scenes: List[SceneTiming],
        audio_path: str,
        output_path: str
    ) -> str:
        # Пример итоговой команды
        cmd = [
            "ffmpeg", "-y",
            # Входные изображения
            "-loop", "1", "-t", "15.3", "-i", "frames/scene-001.png",
            "-loop", "1", "-t", "29.9", "-i", "frames/scene-002.png",
            # Аудио
            "-i", audio_path,
            # Фильтры
            "-filter_complex", self._build_filter_complex(scenes),
            # Выходные параметры
            "-map", "[outv]",
            "-map", "2:a",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path
        ]
        return cmd
    
    def _build_filter_complex(self, scenes: List[SceneTiming]) -> str:
        filters = []
        
        # Scale и motion для каждой сцены
        for i, scene in enumerate(scenes):
            filters.append(f"[{i}:v]scale=1920:1080,{scene.motion_filter}[v{i}]")
        
        # Concat все сцены
        inputs = ''.join(f"[v{i}]" for i in range(len(scenes)))
        filters.append(f"{inputs}concat=n={len(scenes)}:v=1:a=0[outv]")
        
        return ";".join(filters)
```

---

## Основной композитор

```python
class VideoCompositor:
    def compose(
        self,
        frames_dir: str,
        timing_path: str,
        audio_path: str,
        output_path: str
    ):
        # 1. Загружаем тайминг
        timing = self._load_timing(timing_path)
        
        # 2. Валидируем файлы
        self._validate_frames(frames_dir, timing)
        
        # 3. Строим FFmpeg команду
        cmd = self.ffmpeg_builder.build_composition_command(
            scenes=timing.scenes,
            audio_path=audio_path,
            output_path=output_path
        )
        
        # 4. Запускаем FFmpeg
        subprocess.run(cmd, check=True)
```

---

## Зависимости

```
pyyaml>=6.0
pydantic>=2.0
# FFmpeg должен быть установлен в системе
```

---

## Тестирование

```bash
pytest tests/video/test_compositor.py -v
```
