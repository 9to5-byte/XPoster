"""Configuration management for XPoster."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from loguru import logger


class Config:
    """Configuration manager for XPoster."""

    def __init__(self):
        """Initialize configuration."""
        # Load environment variables
        load_dotenv()

        # Set up paths
        self.project_root = Path(__file__).parent.parent
        self.config_path = self.project_root / "config" / "settings.yaml"
        self.data_path = self.project_root / "data"
        self.writing_samples_path = self.data_path / "writing_samples"
        self.training_data_path = self.data_path / "training_data"

        # Create directories if they don't exist
        self.writing_samples_path.mkdir(parents=True, exist_ok=True)
        self.training_data_path.mkdir(parents=True, exist_ok=True)

        # Load YAML configuration
        self.settings = self._load_yaml_config()

        # Twitter/X API credentials
        self.twitter_api_key = os.getenv("TWITTER_API_KEY")
        self.twitter_api_secret = os.getenv("TWITTER_API_SECRET")
        self.twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.twitter_access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

        # AI provider settings
        self.ai_provider = os.getenv("AI_PROVIDER", "openai")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")

        # Database
        self.database_url = os.getenv("DATABASE_URL", f"sqlite:///{self.data_path}/xposter.db")

        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load YAML configuration file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found at {self.config_path}, using defaults")
            return {}

        with open(self.config_path, "r") as f:
            return yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key (supports nested keys with dots)."""
        keys = key.split(".")
        value = self.settings

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        required_vars = [
            ("TWITTER_API_KEY", self.twitter_api_key),
            ("TWITTER_API_SECRET", self.twitter_api_secret),
            ("TWITTER_ACCESS_TOKEN", self.twitter_access_token),
            ("TWITTER_ACCESS_TOKEN_SECRET", self.twitter_access_token_secret),
        ]

        missing = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing.append(var_name)

        # Check AI provider
        if self.ai_provider == "openai" and not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        elif self.ai_provider == "anthropic" and not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")

        if missing:
            logger.error(f"Missing required configuration: {', '.join(missing)}")
            logger.error("Please create a .env file based on .env.example")
            return False

        return True


# Global config instance
config = Config()
