"""AI client wrapper for OpenAI and Anthropic."""

from typing import Optional

from loguru import logger


class AIClient:
    """Unified AI client for different providers."""

    def __init__(self, provider: str, api_key: str, model: str):
        """Initialize AI client.

        Args:
            provider: AI provider (openai or anthropic)
            api_key: API key for the provider
            model: Model to use
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model

        if self.provider == "openai":
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        elif self.provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

        logger.info(f"Initialized {provider} client with model {model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.8,
        max_tokens: int = 500
    ) -> str:
        """Generate text using the AI model.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        try:
            if self.provider == "openai":
                return self._generate_openai(prompt, system_prompt, temperature, max_tokens)
            elif self.provider == "anthropic":
                return self._generate_anthropic(prompt, system_prompt, temperature, max_tokens)
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate text using OpenAI."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content.strip()

    def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate text using Anthropic Claude."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)

        return response.content[0].text.strip()

    def analyze(self, prompt: str) -> str:
        """Analyze text (used for style analysis).

        Args:
            prompt: Analysis prompt

        Returns:
            Analysis result
        """
        system_prompt = "You are an expert writing style analyzer. Provide detailed, accurate analysis in the requested format."
        return self.generate(prompt, system_prompt=system_prompt, temperature=0.3, max_tokens=2000)
