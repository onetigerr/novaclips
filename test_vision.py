from dotenv import load_dotenv
load_dotenv()
from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

try:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                        },
                    },
                ],
            }
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )
    print("SUCCESS")
    print(chat_completion.choices[0].message.content)
except Exception as e:
    print(f"FAILED: {e}")
