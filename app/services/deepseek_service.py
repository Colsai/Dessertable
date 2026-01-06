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

        prompt = f"""Based on these customer reviews for {restaurant_name}, write a single complete sentence that summarizes the positive aspects of their desserts.

Reviews:
{combined_reviews}

Requirements:
- Write ONE complete grammatical sentence
- Focus ONLY on desserts (ice cream, cakes, pastries, sweet treats, etc.)
- Summarize what customers love about the desserts
- Use 10-15 words
- Make it sound natural and enticing, like: "Place has excellent matcha drinks for good moments"
- Do NOT mention service, atmosphere, or non-dessert items

Respond with ONLY the sentence, nothing else. No fragments or incomplete phrases."""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a persuasive food marketer who creates compelling sales pitches for dessert restaurants. Focus exclusively on desserts and make people crave them."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.7
            )

            description = response.choices[0].message.content.strip()

            # Verify it's 10-15 words
            word_count = len(description.split())
            if word_count < 10:
                # If too short, return None to use fallback
                return None
            elif word_count > 15:
                # Truncate to 15 words
                words = description.split()[:15]
                description = ' '.join(words)

            return description

        except Exception as e:
            print(f"Warning: Failed to generate AI description for {restaurant_name}: {e}")
            return None
