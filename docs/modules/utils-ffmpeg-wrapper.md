# Модуль: utils.ffmpeg_wrapper

> **Назначение:** Высокоуровневая обёртка над FFmpeg для частых операций с видео/аудио.

---

## Обзор

Модуль предоставляет:
- Простой API для FFmpeg команд
- Обработку ошибок
- Логирование прогресса
- Типизированные операции

---

## API

```python
from novaclips.utils.ffmpeg_wrapper import FFmpeg

ffmpeg = FFmpeg()

# Конвертация видео
ffmpeg.convert(
    input_path="input.mp4",
    output_path="output.mp4",
    codec="libx264",
    crf=23
)

# Склейка аудио
ffmpeg.concat_audio(
    inputs=["part1.mp3", "part2.mp3"],
    output="full.mp3"
)

# Вшивание субтитров
ffmpeg.burn_subtitles(
    video_path="video.mp4",
    subtitles_path="subs.ass",
    output_path="final.mp4"
)

# Извлечение аудио
ffmpeg.extract_audio(
    video_path="video.mp4",
    output_path="audio.mp3"
)

# Loudness normalization
ffmpeg.normalize_audio(
    input_path="audio.mp3",
    output_path="normalized.mp3",
    target_lufs=-14
)
```

---

## Структура кода

```
src/novaclips/utils/ffmpeg_wrapper/
├── __init__.py
├── wrapper.py          # Основной класс FFmpeg
├── commands.py         # Построитель команд
├── progress.py         # Парсер прогресса
└── exceptions.py
```

---

## Основной класс

```python
import subprocess
from pathlib import Path

class FFmpeg:
    def __init__(self, executable: str = "ffmpeg"):
        self.executable = executable
        self._check_installation()
    
    def _check_installation(self):
        """Проверяет, что FFmpeg установлен."""
        try:
            result = subprocess.run(
                [self.executable, "-version"],
                capture_output=True, check=True
            )
        except FileNotFoundError:
            raise FFmpegNotFoundError("FFmpeg not installed")
    
    def _run(self, args: list, progress_callback=None) -> str:
        """Запускает FFmpeg команду."""
        cmd = [self.executable, "-y"] + args
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise FFmpegError(f"FFmpeg failed: {stderr.decode()}")
        
        return stdout.decode()
    
    def burn_subtitles(
        self,
        video_path: str,
        subtitles_path: str,
        output_path: str
    ):
        """Вшивает субтитры в видео."""
        # Экранируем путь для FFmpeg
        subs_escaped = subtitles_path.replace(":", "\\:")
        
        args = [
            "-i", video_path,
            "-vf", f"ass='{subs_escaped}'",
            "-c:a", "copy",
            output_path
        ]
        self._run(args)
    
    def concat_audio(self, inputs: list, output: str):
        """Склеивает аудиофайлы."""
        # Создаём список файлов
        list_content = "\n".join(f"file '{p}'" for p in inputs)
        list_path = Path(output).parent / "concat_list.txt"
        list_path.write_text(list_content)
        
        args = [
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_path),
            "-c", "copy",
            output
        ]
        self._run(args)
        list_path.unlink()
    
    def normalize_audio(
        self,
        input_path: str,
        output_path: str,
        target_lufs: float = -14
    ):
        """Нормализует громкость аудио."""
        args = [
            "-i", input_path,
            "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
            output_path
        ]
        self._run(args)
    
    def image_to_video(
        self,
        image_path: str,
        duration: float,
        output_path: str,
        fps: int = 30
    ):
        """Создаёт видео из статичной картинки."""
        args = [
            "-loop", "1",
            "-i", image_path,
            "-t", str(duration),
            "-c:v", "libx264",
            "-r", str(fps),
            "-pix_fmt", "yuv420p",
            output_path
        ]
        self._run(args)
```

---

## Исключения

```python
class FFmpegError(Exception):
    """Базовая ошибка FFmpeg."""
    pass

class FFmpegNotFoundError(FFmpegError):
    """FFmpeg не установлен."""
    pass

class InvalidInputError(FFmpegError):
    """Неверный входной файл."""
    pass
```

---

## Зависимости

```
# FFmpeg должен быть установлен в системе
# brew install ffmpeg (macOS)
# apt install ffmpeg (Ubuntu)
```
