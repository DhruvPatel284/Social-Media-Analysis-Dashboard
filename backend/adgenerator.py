from flask import jsonify
import base64
import aiohttp
import asyncio
import logging
from typing import List, Dict
from config import GROQ_API_KEY, SEGMIND_API_KEY
from groq import Groq
import re

logger = logging.getLogger(__name__)

class AdImageGenerator:
    def __init__(self):
        self.groq_api_key = GROQ_API_KEY
        self.segmind_api_key = SEGMIND_API_KEY
        self.groq_client = Groq(api_key=GROQ_API_KEY)


    async def _generate_prompts(self, category: str) -> List[str]:
        """Generate image prompts using Groq"""
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an advertising expert. Create 6 clear, detailed image prompts for SDXL image generation."
                    },
                    {
                        "role": "user",
                        "content": f"""Generate 6 different advertising image prompts for ${category}. Each prompt should be self-contained and focus on different aspects: lifestyle, product showcase, emotional appeal, and brand story."""
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=1000
            )
            
            prompts = response.choices[0].message.content.split('\n')
            # Clean and filter prompts
            return [
                re.sub(r'^\d+\.\s*', '', p).strip()  # Use regex to remove numbering
                for p in prompts
                if p.strip() and not p.startswith(('Note:', '-'))
            ][:6] 
                
        except Exception as e:
            logger.error(f"Error generating prompts: {str(e)}")
            raise

    async def _generate_single_image(self, session: aiohttp.ClientSession, prompt: str) -> Dict:
        """Generate a single image using Segmind"""
        try:
            async with session.post(
                "https://api.segmind.com/v1/sdxl1.0-txt2img",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": self.segmind_api_key
                },
                json={
                    "prompt": prompt,
                    "negative_prompt": "blurry, low quality, distorted, unrealistic",
                    "style": "base",
                    "samples": 1,
                    "scheduler": "UniPC",
                    "num_inference_steps": 25,
                    "guidance_scale": 7.5,
                    "seed": -1,
                    "img_width": 1024,
                    "img_height": 1024,
                    "refiner": True,
                    "base64": True
                }
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Segmind API error: {error_text}")
                
                data = await response.json()
                base64_data = data.get('image', '')
                
                if not base64_data.startswith('data:image'):
                    base64_data = f"data:image/png;base64,{base64_data}"
                
                return {
                    "prompt": prompt,
                    "image": base64_data
                }
        except Exception as e:
            logger.error(f"Error generating image for prompt '{prompt}': {str(e)}")
            return {
                "prompt": prompt,
                "error": str(e)
            }

    async def generate_ad_images(self, category: str) -> Dict:
        """Generate multiple ad images for a category"""
        try:
            # Generate prompts
            prompts = await self._generate_prompts(category)
            
            # Generate images in parallel
            async with aiohttp.ClientSession() as session:
                tasks = [
                    self._generate_single_image(session, prompt)
                    for prompt in prompts
                ]
                results = await asyncio.gather(*tasks)
            
            # Format results
            successful_images = [r for r in results if 'image' in r]
            failed_images = [r for r in results if 'error' in r]
            
            return {
                "category": category,
                "generated_images": successful_images,
                "failed_generations": failed_images,
                "metadata": {
                    "total_attempts": len(results),
                    "successful": len(successful_images),
                    "failed": len(failed_images)
                }
            }
        except Exception as e:
            logger.error(f"Error in generate_ad_images: {str(e)}")
            return {
                "error": str(e),
                "category": category
            }