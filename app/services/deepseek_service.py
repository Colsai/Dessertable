from typing import List, Dict, Optional
import os
from openai import OpenAI


class DeepSeekService:
    """Service for generating AI descriptions using DeepSeek"""

    def __init__(self):
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")

        # DeepSeek uses OpenAI-compatible API
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    def generate_dessert_description(self, restaurant_name: str, reviews: List[Dict]) -> Optional[str]:
        """
        Generate a 10-15 word sales pitch focusing on desserts based on reviews

        Args:
            restaurant_name: Name of the restaurant
            reviews: List of review dictionaries from Google Places API

        Returns:
            Short sales pitch (10-15 words) or None if generation fails
        """
        if not reviews:
            return None

        # Extract review texts (limit to first 5 reviews to avoid token limits)
        review_texts = []
        for review in reviews[:5]:
            if 'text' in review:
                review_texts.append(review['text'])

        if not review_texts:
            return None

        # Combine reviews into prompt
        combined_reviews = "\n\n".join(review_texts)

        prompt = f"""Based on these customer reviews for {restaurant_name}, write a single short sentence capturing what makes their desserts special.

Reviews:
{combined_reviews}

Requirements:
- Write ONE short, complete sentence
- Focus ONLY on desserts (ice cream, cakes, pastries, sweet treats, etc.)
- Use 10 words or fewer — be punchy and vivid
- Sound warm and personal, like something a happy customer would say
- Examples: "Great pastries that make me happy", "Delicious banana bread in a quiet environment", "Dreamy ice cream that hits every time"
- Do NOT mention service, atmosphere, or non-dessert items

Respond with ONLY the sentence, nothing else."""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a happy dessert lover summarizing your favorite spots in one short, vivid sentence. Keep it under 10 words and make it feel personal and warm."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=30,
                temperature=0.8
            )

            description = response.choices[0].message.content.strip()

            # Strip surrounding quotes if the model added them
            if description.startswith('"') and description.endswith('"'):
                description = description[1:-1].strip()

            # Enforce 10-word max by truncating
            word_count = len(description.split())
            if word_count > 10:
                words = description.split()[:10]
                description = ' '.join(words)

            if not description:
                return None

            return description

        except Exception as e:
            print(f"Warning: Failed to generate AI description for {restaurant_name}: {e}")
            return None
