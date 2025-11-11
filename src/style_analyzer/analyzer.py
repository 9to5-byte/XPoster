"""Writing style analysis using AI."""

import json
import re
from typing import List, Dict, Any, Optional

from loguru import logger


class StyleAnalyzer:
    """Analyze writing style from samples."""

    def __init__(self, ai_client):
        """Initialize style analyzer.

        Args:
            ai_client: AI client for analysis (OpenAI or Anthropic)
        """
        self.ai_client = ai_client
        self.style_profile: Optional[Dict[str, Any]] = None

    def analyze_samples(self, samples: List[str]) -> Dict[str, Any]:
        """Analyze writing samples to extract style characteristics.

        Args:
            samples: List of text samples

        Returns:
            Dictionary containing style analysis
        """
        if not samples:
            logger.warning("No samples provided for analysis")
            return {}

        logger.info(f"Analyzing {len(samples)} writing samples...")

        # Combine samples for analysis
        combined_text = "\n\n---\n\n".join(samples[:10])  # Use first 10 samples

        prompt = f"""Analyze the following writing samples and extract detailed style characteristics. Focus on:

1. Tone and voice (formal, casual, humorous, serious, etc.)
2. Vocabulary level and word choice patterns
3. Sentence structure (short/long sentences, complexity)
4. Punctuation style
5. Use of emojis, if any
6. Use of hashtags and their style
7. Common phrases or expressions
8. Writing rhythm and flow
9. Topic preferences
10. Personality traits evident in writing

Writing samples:
{combined_text[:8000]}

Provide a detailed JSON analysis with the following structure:
{{
    "tone": "description of overall tone",
    "voice": "description of voice characteristics",
    "vocabulary_level": "simple/moderate/advanced",
    "sentence_style": "description of sentence patterns",
    "punctuation_patterns": ["pattern1", "pattern2"],
    "emoji_usage": "none/rare/moderate/frequent",
    "hashtag_style": "description or none",
    "common_phrases": ["phrase1", "phrase2"],
    "personality_traits": ["trait1", "trait2"],
    "topics_of_interest": ["topic1", "topic2"],
    "writing_quirks": ["quirk1", "quirk2"]
}}"""

        try:
            response = self.ai_client.analyze(prompt)

            # Extract JSON from response
            style_profile = self._extract_json(response)

            if not style_profile:
                logger.error("Failed to extract style profile from AI response")
                return self._create_default_profile(samples)

            # Add quantitative analysis
            style_profile.update(self._quantitative_analysis(samples))

            self.style_profile = style_profile
            logger.info("Style analysis completed successfully")

            return style_profile

        except Exception as e:
            logger.error(f"Error during style analysis: {e}")
            return self._create_default_profile(samples)

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from text response.

        Args:
            text: Text containing JSON

        Returns:
            Parsed JSON dictionary or None
        """
        # Try to find JSON in the response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)

        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Try parsing the entire response
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Could not extract JSON from AI response")
            return None

    def _quantitative_analysis(self, samples: List[str]) -> Dict[str, Any]:
        """Perform quantitative analysis on samples.

        Args:
            samples: List of text samples

        Returns:
            Dictionary with quantitative metrics
        """
        total_text = " ".join(samples)

        # Calculate metrics
        avg_sentence_length = self._calculate_avg_sentence_length(total_text)
        avg_word_length = self._calculate_avg_word_length(total_text)
        emoji_count = len(re.findall(r'[😀-🙏🌀-🗿🚀-🛿]', total_text))
        hashtag_count = len(re.findall(r'#\w+', total_text))
        exclamation_count = total_text.count('!')
        question_count = total_text.count('?')

        return {
            "avg_sentence_length": avg_sentence_length,
            "avg_word_length": avg_word_length,
            "emoji_frequency": emoji_count / len(samples) if samples else 0,
            "hashtag_frequency": hashtag_count / len(samples) if samples else 0,
            "exclamation_frequency": exclamation_count / len(samples) if samples else 0,
            "question_frequency": question_count / len(samples) if samples else 0,
        }

    def _calculate_avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length in words."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.0

        total_words = sum(len(s.split()) for s in sentences)
        return total_words / len(sentences)

    def _calculate_avg_word_length(self, text: str) -> float:
        """Calculate average word length in characters."""
        words = re.findall(r'\b\w+\b', text)

        if not words:
            return 0.0

        total_chars = sum(len(w) for w in words)
        return total_chars / len(words)

    def _create_default_profile(self, samples: List[str]) -> Dict[str, Any]:
        """Create a default style profile from basic analysis.

        Args:
            samples: List of text samples

        Returns:
            Basic style profile
        """
        logger.info("Creating default style profile from quantitative analysis")

        quantitative = self._quantitative_analysis(samples)

        return {
            "tone": "neutral",
            "voice": "conversational",
            "vocabulary_level": "moderate",
            "sentence_style": "varied",
            "punctuation_patterns": ["standard"],
            "emoji_usage": "moderate" if quantitative["emoji_frequency"] > 0.5 else "rare",
            "hashtag_style": "occasional" if quantitative["hashtag_frequency"] > 0.2 else "none",
            "common_phrases": [],
            "personality_traits": ["informative"],
            "topics_of_interest": [],
            "writing_quirks": [],
            **quantitative
        }

    def get_style_prompt(self) -> str:
        """Generate a prompt describing the writing style.

        Returns:
            Style description for content generation
        """
        if not self.style_profile:
            return "Write in a natural, conversational style."

        prompt_parts = []

        prompt_parts.append(f"Tone: {self.style_profile.get('tone', 'neutral')}")
        prompt_parts.append(f"Voice: {self.style_profile.get('voice', 'conversational')}")
        prompt_parts.append(f"Vocabulary: {self.style_profile.get('vocabulary_level', 'moderate')}")

        if self.style_profile.get('personality_traits'):
            traits = ', '.join(self.style_profile['personality_traits'])
            prompt_parts.append(f"Personality: {traits}")

        if self.style_profile.get('common_phrases'):
            phrases = ', '.join(self.style_profile['common_phrases'][:3])
            prompt_parts.append(f"Common phrases: {phrases}")

        # Add quantitative guidelines
        avg_sent_len = self.style_profile.get('avg_sentence_length', 15)
        if avg_sent_len < 10:
            prompt_parts.append("Use short, punchy sentences")
        elif avg_sent_len > 20:
            prompt_parts.append("Use longer, more detailed sentences")

        if self.style_profile.get('emoji_frequency', 0) > 0.5:
            prompt_parts.append("Include emojis occasionally")

        if self.style_profile.get('hashtag_frequency', 0) > 0.2:
            prompt_parts.append("Use relevant hashtags")

        return ". ".join(prompt_parts) + "."
