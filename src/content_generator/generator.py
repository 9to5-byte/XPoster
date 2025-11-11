"""Content generation for tweets and replies."""

import random
from typing import Optional, List, Dict, Any

from loguru import logger


class ContentGenerator:
    """Generate tweets and replies in user's writing style."""

    def __init__(self, ai_client, style_analyzer, config):
        """Initialize content generator.

        Args:
            ai_client: AI client for generation
            style_analyzer: Style analyzer with learned style
            config: Application configuration
        """
        self.ai_client = ai_client
        self.style_analyzer = style_analyzer
        self.config = config

    def generate_tweet(
        self,
        topic: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """Generate a new tweet.

        Args:
            topic: Optional topic to tweet about
            context: Optional context or inspiration

        Returns:
            Generated tweet text
        """
        style_prompt = self.style_analyzer.get_style_prompt()

        # Build the generation prompt
        prompt_parts = [
            "Generate a single tweet (max 280 characters) that sounds natural and authentic.",
            f"\nWriting style requirements: {style_prompt}"
        ]

        if topic:
            prompt_parts.append(f"\nTopic: {topic}")

        if context:
            prompt_parts.append(f"\nContext/Inspiration: {context}")

        # Add content preferences
        if self.config.get("content_generation.include_hashtags"):
            max_hashtags = self.config.get("content_generation.max_hashtags", 3)
            prompt_parts.append(f"\nInclude up to {max_hashtags} relevant hashtags if appropriate.")

        if self.config.get("content_generation.include_emojis"):
            if self.style_analyzer.style_profile and \
               self.style_analyzer.style_profile.get("emoji_frequency", 0) > 0.5:
                prompt_parts.append("\nInclude emojis where they feel natural.")

        prompt_parts.append("\nIMPORTANT: Return ONLY the tweet text, nothing else. No quotes, no explanations.")

        prompt = "\n".join(prompt_parts)

        try:
            temperature = self.config.get("content_generation.temperature", 0.8)
            tweet = self.ai_client.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=100
            )

            # Clean up the response
            tweet = self._clean_tweet(tweet)

            logger.info(f"Generated tweet: {tweet[:50]}...")
            return tweet

        except Exception as e:
            logger.error(f"Failed to generate tweet: {e}")
            return self._fallback_tweet()

    def generate_reply(
        self,
        original_tweet: str,
        original_author: Optional[str] = None
    ) -> str:
        """Generate a reply to a tweet.

        Args:
            original_tweet: The tweet to reply to
            original_author: Optional author screen name

        Returns:
            Generated reply text
        """
        style_prompt = self.style_analyzer.get_style_prompt()

        # Build the generation prompt
        prompt_parts = [
            "Generate a thoughtful and engaging reply to the following tweet.",
            f"\nOriginal tweet: {original_tweet}"
        ]

        if original_author:
            prompt_parts.append(f"\nReplying to: @{original_author}")

        prompt_parts.append(f"\nWriting style requirements: {style_prompt}")
        prompt_parts.append("\nThe reply should:")
        prompt_parts.append("- Be relevant and add value to the conversation")
        prompt_parts.append("- Sound natural and authentic")
        prompt_parts.append("- Be max 280 characters")
        prompt_parts.append("- Not be overly promotional or spammy")

        prompt_parts.append("\nIMPORTANT: Return ONLY the reply text, nothing else. No quotes, no explanations.")

        prompt = "\n".join(prompt_parts)

        try:
            temperature = self.config.get("content_generation.temperature", 0.8)
            reply = self.ai_client.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=100
            )

            # Clean up the response
            reply = self._clean_tweet(reply)

            logger.info(f"Generated reply: {reply[:50]}...")
            return reply

        except Exception as e:
            logger.error(f"Failed to generate reply: {e}")
            return self._fallback_reply()

    def generate_tweet_ideas(self, count: int = 5) -> List[str]:
        """Generate topic ideas for tweets.

        Args:
            count: Number of ideas to generate

        Returns:
            List of tweet topic ideas
        """
        style_profile = self.style_analyzer.style_profile

        prompt_parts = [
            f"Generate {count} interesting and engaging tweet topic ideas.",
        ]

        if style_profile and style_profile.get("topics_of_interest"):
            topics = ", ".join(style_profile["topics_of_interest"][:5])
            prompt_parts.append(f"\nPreferred topics: {topics}")

        prompt_parts.append("\nProvide diverse topics that would make for engaging tweets.")
        prompt_parts.append("Return as a numbered list, one topic per line.")

        prompt = "\n".join(prompt_parts)

        try:
            response = self.ai_client.generate(
                prompt=prompt,
                temperature=0.9,
                max_tokens=300
            )

            # Parse the ideas
            ideas = []
            for line in response.split("\n"):
                line = line.strip()
                # Remove numbering
                if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                    # Remove leading number, dash, or asterisk
                    idea = line.lstrip("0123456789.-* ").strip()
                    if idea:
                        ideas.append(idea)

            logger.info(f"Generated {len(ideas)} tweet ideas")
            return ideas[:count]

        except Exception as e:
            logger.error(f"Failed to generate tweet ideas: {e}")
            return []

    def _clean_tweet(self, text: str) -> str:
        """Clean up generated tweet text.

        Args:
            text: Raw generated text

        Returns:
            Cleaned tweet text
        """
        # Remove quotes if present
        text = text.strip().strip('"\'')

        # Remove "Tweet:" or similar prefixes
        prefixes = ["tweet:", "reply:", "response:", "here's the tweet:", "here is the tweet:"]
        for prefix in prefixes:
            if text.lower().startswith(prefix):
                text = text[len(prefix):].strip()

        # Ensure it's within length
        if len(text) > 280:
            text = text[:277] + "..."

        return text.strip()

    def _fallback_tweet(self) -> str:
        """Generate a simple fallback tweet."""
        fallbacks = [
            "Thinking about innovation and the future of technology.",
            "Excited about what's next!",
            "Just sharing some thoughts today.",
            "Interesting times we're living in.",
            "Always learning, always growing."
        ]
        return random.choice(fallbacks)

    def _fallback_reply(self) -> str:
        """Generate a simple fallback reply."""
        fallbacks = [
            "Interesting perspective!",
            "Thanks for sharing this!",
            "Great point!",
            "This is thought-provoking.",
            "Appreciate the insights!"
        ]
        return random.choice(fallbacks)

    def should_reply_to_tweet(self, tweet: Dict[str, Any]) -> bool:
        """Decide whether to reply to a tweet based on relevance.

        Args:
            tweet: Tweet data

        Returns:
            True if should reply, False otherwise
        """
        # Check probability threshold
        reply_probability = self.config.get("replies.reply_probability", 0.3)

        if random.random() > reply_probability:
            return False

        # Check if tweet contains monitored keywords
        keywords = self.config.get("replies.keywords_to_monitor", [])

        if not keywords:
            return True

        tweet_text = tweet.get("text", "").lower()

        for keyword in keywords:
            if keyword.lower() in tweet_text:
                logger.info(f"Tweet matches keyword '{keyword}'")
                return True

        return False
