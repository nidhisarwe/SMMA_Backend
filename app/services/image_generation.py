import os
from typing import List, Dict, Optional
from pathlib import Path
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ImageGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.output_dir = Path("output/generated_images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_single_image(self, prompt: str, style_prompt: Optional[str] = None) -> str:
        full_prompt = f"{prompt}, {style_prompt}" if style_prompt else prompt

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"inputs": full_prompt},
            )

            if response.status_code != 200:
                logger.error(f"Image generation failed: {response.text}")
                return None

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}.jpg"
            output_path = self.output_dir / filename

            with open(output_path, "wb") as f:
                f.write(response.content)

            return str(output_path)

        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None

    def batch_generate(self, prompts: List[Dict], content_type: str = "image") -> List[str]:
        if content_type != "image":
            logger.warning(f"Unsupported content type: {content_type}")
            return []

        generated_files = []

        for prompt_data in prompts:
            main_prompt = prompt_data.get("prompt", "")
            style_prompt = prompt_data.get("style_prompt", None)

            if not main_prompt:
                continue

            image_path = self.generate_single_image(main_prompt, style_prompt)
            if image_path:
                generated_files.append(image_path)

        return generated_files