# Флоу создания визуалов (Manual LLM Workflow)

> **Цель:** Пошаговая инструкция по генерации промптов для картинок с помощью LLM (ChatGPT/Claude).
> **Входные данные:** У вас должны быть файлы `script.md` (сценарий) и `subtitles.ass` (субтитры, если есть).

Прикрепите файлы сценария и субтитров к диалогу с LLM перед началом работы.

---

## Этап 1: Разработка визуального стиля (Visual Concept)

**Что делаем:** Определяем общую стилистику ролика, цветовую гамму и атмосферу.
**Результат:** Текстовое описание стиля, которое будет добавляться во все промпты для консистентности.

**Промпт для LLM:**
```text
You are the Art Director for a YouTube channel.
Analyze the attached script.

Your task is to propose a unified visual style for the video content.
The video will consist of changing illustrations (Static Image + Camera Motion).

1. Describe the Atmosphere (Mood & Tone).
2. Propose a Color Palette — specify 3-4 main colors.
3. Describe the Illustration Style (e.g., Digital Art, Cinematic Realistic, Vector Flat, Watercolor, etc.).
4. Formulate a "Style Token" — a short paragraph (2-3 sentences) that we will append to the end of every image prompt to ensure consistency across all generated images.

Provide the result in a structured format.
```

---

## Этап 2: Создание референсов (Reference Images)

**Что делаем:** Превращаем слова в **картинки**. Нам нужно получить 2-3 эталонных изображения, чтобы убедиться, что стиль выглядит круто, и использовать их как визуальный ориентир.
**Результат:** Генерируем реальные файлы: `Character Sheet` и `Style Reference`.

**Промпт для LLM:**
```text
Now we need to generate the ACTUAL Reference Images to freeze our style.
Please write 2 distinct image generation prompts for me:

1. **Character Sheet Prompt:**
   Write a descriptive prompt to generate a character sheet for [Character Name].
   Include: "Split view, front view, side view, multiple expressions, white background".
   
2. **Style Reference Prompt:**
   Write a descriptive prompt for a key scene that perfectly captures our [Style Token].

I will generate these images in my AI tool (DALL-E 3 / Veo).
I would like you to make drawing style more like Arcane series. Don't make it fantasy looking. I mean only graphics. Not characters. Characters should be modern and techy.  
```

> **Действие человека:** 
> 1. Скопируйте промпты и сгенерируйте картинки.
> 2. Выберите лучшие варианты. **Это ваши референсы.** 
> 3. (Опционально) Если вы используете ChatGPT с DALL-E, вы можете продолжить в том же чате, и он будет "помнить" сгенерированное. Если нет — просто держите эти картинки перед глазами.

---

## Этап 2.5: Фиксация контекста (Context Block)

**Что делаем:** Формируем текстовый блок, который опишет наши *утвержденные* референсы.
**Зачем:** OpenAI/Veo любят подробные описания. Мы возьмем то, что реально получилось на картинках, и опишем это словами.

**Промпт для LLM:**
```text
Great, I have generated the reference images and they look perfect.
Now, create a "Context Block" that I will attach to every system prompt.

Combine:
1. The detailed visual description of the STYLE we just achieved.
2. The detailed visual description of the CHARACTER we just achieved.

Format it as a single paragraph starting with "Visual Style & Character Context: ..."
```


---

## Этап 3: Создание шот-листа (Shotlist)

**Что делаем:** Разбиваем сценарий на сцены.
**Формат:** JSON. Это позволит в будущем скармливать этот файл скрипту-генератору.

**Промпт для LLM:**
```text
I have generated the reference images.
Check attached files. 

Now let's create a detailed shotlist.
Use the script. Break it down into scenes every 5-10 seconds of speech.

OUTPUT FORMAT: JSON
Return a single JSON array of objects.

```json
[
  {
    "id": 1,
    "timing": "00:00-00:05",
    "voiceover": "Brief text...",
    "visual_idea": "Description of the scene...",
    "shot_type": "Close-up/Wide/Medium"
  }
]
```

Criteria for visual ideas:
- Concrete images that can be drawn.
- Avoid abstract concepts.
- Vary the shot types.
```

---

## Этап 4: Генерация промптов (Prompt Engineering)

**Что делаем:** Формируем массив готовых промптов.
**Результат:** JSON-файл, готовый для отправки в API.

**Промпт для LLM:**
```text
You are a Visual Prompt Engineer for OpenAI DALL-E 3 / Google Veo.

Using the JSON shotlist, generate a new JSON array with ready-to-use prompts.

Rules:
1. **Integrate Style:** explicitly describe the style in every prompt.
2. **Integrate Character:** include full character description if present.
3. **Composition:** Describe camera/lighting.

OUTPUT FORMAT: JSON

```json
[
  {
    "id": 1,
    "prompt": "[Scene Description]. [Character Description]. [Style Description]. Wide cinematic shot, 16:9 aspect ratio."
  }
]
```
```

---

## Этап 5: Проверка и итерации (Quality Control)

**Что делаем:** Генерируем тестовые картинки и корректируем промпты.
- Если картинка не соответствует: просим LLM переписать промпт, указывая, что именно не так ("Make the hero older", "Remove text from background").
- Если стиль "плывет": напоминаем LLM использовать Style Token.

**Совет:** Генерируйте изображения пачками по 5-10 штук, чтобы поддерживать поток.
