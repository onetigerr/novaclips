import logging
import base64
import os
import json
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class DescriptionGenerator:
    """
    Generates description and hashtags using Groq Vision API.
    Model: llama-3.2-90b-vision-preview
    """
    
    def __init__(self):
        try:
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                logger.warning("GROQ_API_KEY not found in environment")
                self.client = None
            else:
                self.client = Groq(api_key=api_key)
        except ImportError:
            logger.error("Groq library not installed. Please run 'pip install groq'")
            self.client = None

    def generate(self, collage_path: Path, subtitles_text: Optional[str] = None) -> Dict[str, str]:
        """
        Returns JSON dict: {'title': str, 'description': str, 'hashtags': str, 'slug': str}
        """
        if not self.client:
            return {}

        # Encode image
        try:
            with open(collage_path, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to read collage: {e}")
            return {}

        # Construct Prompt
        prompt = (
            "You are a YouTube Shorts expert. Analyze the attached image (keyframes from a video) "
        )
        if subtitles_text:
            # Truncate subs if too long
            prompt += f"and the following audio transcript:\n\n{subtitles_text[:2000]}\n\n"
        
        prompt += (
            "Create a viral, engaging metadata for this video.\n"
            "Return ONLY a JSON object with these fields:\n"
            "- title: A short, punchy title (max 50 chars)\n"
            "- description: A 2-3 sentence engaging description including a call to action.\n"
            "- hashtags: 3-5 relevant hashtags (e.g. #shorts #viral)\n"
            "- slug: A short filename-safe slug based on the title (e.g. funny-cat-fails)\n"
            "Do not include markdown formatting (```json), just the raw JSON."
        )

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encoded_image}",
                                },
                            },
                        ],
                    }
                ],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                temperature=0.7,
                stream=False,
                response_format={"type": "json_object"}
            )
            
            content = chat_completion.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Groq Vision API failed: {e}. Falling back to Text-Only.")
            # Fallback to Text-Only using Llama 3.3
            try:
                txt_prompt = (
                    "You are a YouTube Shorts expert. "
                    "Analyze the following audio transcript from a video:\n\n"
                    f"{subtitles_text[:3000] if subtitles_text else 'No subtitles available.'}\n\n"
                    "Create a viral, engaging metadata for this video.\n"
                    "Return ONLY a JSON object with these fields:\n"
                    "- title: A short, punchy title (max 50 chars)\n"
                    "- description: A 2-3 sentence engaging description including a call to action.\n"
                    "- hashtags: 3-5 relevant hashtags (e.g. #shorts #viral)\n"
                    "- slug: A short filename-safe slug based on the title (e.g. funny-cat-fails)\n"
                    "Do not include markdown formatting (```json), just the raw JSON."
                )
                
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "user", "content": txt_prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                content = chat_completion.choices[0].message.content
                return json.loads(content)
            except Exception as e2:
                 logger.error(f"Groq Text API fallback failed: {e2}")
                 return {}
