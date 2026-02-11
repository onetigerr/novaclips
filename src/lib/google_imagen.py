import os
from pathlib import Path
from typing import List, Optional
from google import genai
from google.genai import types

class GoogleImageGenerator:
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None, location: Optional[str] = None):
        """
        Initialize the GoogleImageGenerator.
        
        Args:
            api_key: Google API Key. If None, tries to read from GOOGLE_API_KEY env var.
            project_id: Optional project to use (if using Vertex AI instead of AI Studio API key).
            location: Optional location if using Vertex AI.
        """
        # Try finding API key
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = location or os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

        if self.api_key:
            # Use AI Studio API Key
            self.client = genai.Client(api_key=self.api_key)
            print("Initialized with API Key.")
        elif self.project_id:
            # Use Vertex AI (credentials implied)
            self.client = genai.Client(vertexai=True, project=self.project_id, location=self.location)
            print(f"Initialized with Vertex AI Project {self.project_id} in {self.location}.")
        else:
            raise ValueError("GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT must be provided.")

    def generate_image(
        self, 
        prompt: str, 
        output_path: str,
        style_reference_paths: Optional[List[str]] = None,
        aspect_ratio: str = "1:1",
        model_name: str = "imagen-4.0-fast-generate-001"
    ) -> str:
        """
        Generate an image using Google Gen AI.
        
        Args:
            prompt: Text prompt for generation.
            output_path: Path to save the generated image.
            style_reference_paths: List of paths to style reference images (optional).
                                   NOTE: Not supported by all models/versions yet.
            aspect_ratio: Aspect ratio string (e.g., "1:1", "16:9").
            model_name: Model to use. 'imagen-4.0-fast-generate-001' is default.
                        User requested 'imagen-4.0-fast-001' (which maps to this).
        
        Returns:
            Path to the saved image.
        """
        
        print(f"Generating image with model: {model_name}")
        print(f"Prompt: {prompt}")
        
        # Prepare contents
        # For Imagen 3, fetching style reference is done via specific parameters if supported.
        # As per current SDK usage for Imagen, we typically pass the prompt.
        
        
        # Determine aspect ratio
        ratio = aspect_ratio # "1:1", "16:9", "4:3", etc.
        full_prompt = prompt
        
        # Check if using a Gemini model (which uses generate_content) vs Imagen model (generate_images)
        is_gemini = "gemini" in model_name.lower() or "flash" in model_name.lower() or "pro" in model_name.lower() or "veo" in model_name.lower()
        
        try:
            if is_gemini:
                print(f"Using Gemini-style generation (generate_content) for model: {model_name}")
                
                # Construct content parts
                contents = [prompt]
                
                if style_reference_paths:
                    print(f"Adding {len(style_reference_paths)} style reference images.")
                    for ref_path in style_reference_paths:
                        # Ensure absolute path resolution
                        p = Path(ref_path).resolve()
                        if p.exists():
                            # We can pass PIL images or file objects. 
                            # google-genai supports passing local file paths directly if using File API, 
                            # or we can read bytes and pass as Part.
                            # For simplicity with the new SDK, let's try reading as bytes/PIL.
                            try:
                                import PIL
                                from PIL import Image
                                img = Image.open(p)
                                contents.append(img)
                            except ImportError as e:
                                print(f"Warning: Could not import PIL: {e}. content not added.")
                            except Exception as e:
                                print(f"Warning: Could not open {p} with PIL: {e}. Skipping.")
                        else:
                            print(f"Warning: Reference image not found: {ref_path}")

                # Config for Gemini Image Generation
                # For Gemini 3 Pro Image, we use generate_content with image_config.
                # output_mime_type in ImageConfig is apparently not supported by the API yet or for this model.
                
                gen_config = types.GenerateContentConfig(
                    image_config=types.ImageConfig(
                        aspect_ratio=ratio
                    )
                )

                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=gen_config
                )
                
                # Extract image from response
                # Response -> candidates -> content -> parts -> inline_data / or executable_code etc.
                # For images, it likely comes as inline_data (base64) or similar.
                
                generated_image_bytes = None
                
                if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if part.inline_data and part.inline_data.mime_type and part.inline_data.mime_type.startswith("image/"):
                            generated_image_bytes = part.inline_data.data
                            break
                        # Sometimes it might be in other fields depending on API version, 
                        # but inline_data is standard for generated media in Gem output.
                
                if generated_image_bytes is None:
                     # Check if it was filtered
                     if response.prompt_feedback:
                         print(f"Prompt Feedback: {response.prompt_feedback}")
                     raise RuntimeError("No image data found in Gemini response.")
                
                # Save
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, "wb") as f:
                    f.write(generated_image_bytes)
                    
                print(f"Image saved to {output_path}")
                return str(output_file)

            else:
                # Legacy Imagen generation
                # Generate image configuration
                config = types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=ratio,
                    include_rai_reason=True,
                    output_mime_type="image/png"
                )

                response = self.client.models.generate_images(
                    model=model_name,
                    prompt=full_prompt,
                    config=config
                )
                
                if response.generated_images:
                    generated_image = response.generated_images[0]
                    
                    if not generated_image.image:
                        # Image was filtered or not returned
                        failure_reason = "Unknown reason"
                        if hasattr(generated_image, 'rai_status_code'):
                             failure_reason = f"RAI Status Code: {generated_image.rai_status_code}"
                        
                        # Try to inspect safety attributes if available
                        raise RuntimeError(f"Image generation returned a response but no image data. This is often due to safety filters. Details: {failure_reason}")

                    image_bytes = generated_image.image.image_bytes
                    
                    if image_bytes is None:
                        raise RuntimeError("Generated image contains no byte data.")

                    # Save the image
                    output_file = Path(output_path)
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(output_file, "wb") as f:
                        f.write(image_bytes)
                        
                    print(f"Image saved to {output_path}")
                    return str(output_file)
                else:
                    raise RuntimeError("No images returned from API.")

        except Exception as e:
            print(f"Error generating image: {e}")
            raise
