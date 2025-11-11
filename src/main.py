"""Main application entry point for XPoster."""

import sys
import time
from pathlib import Path

from loguru import logger

from .config import config
from .ai_client import AIClient
from .style_analyzer import StyleAnalyzer, DocumentProcessor
from .twitter_client import TwitterClient
from .content_generator import ContentGenerator
from .scheduler import PostingScheduler


class XPoster:
    """Main XPoster application."""

    def __init__(self):
        """Initialize XPoster."""
        # Configure logging
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            level=config.log_level
        )

        # Add file logging
        log_dir = config.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        logger.add(
            log_dir / "xposter.log",
            rotation="1 day",
            retention="7 days",
            level="DEBUG"
        )

        self.initialized = False
        self.ai_client = None
        self.style_analyzer = None
        self.document_processor = None
        self.twitter_client = None
        self.content_generator = None
        self.scheduler = None

    def initialize(self):
        """Initialize all components."""
        logger.info("Initializing XPoster...")

        # Validate configuration
        if not config.validate():
            logger.error("Configuration validation failed")
            return False

        try:
            # Initialize AI client
            if config.ai_provider == "openai":
                self.ai_client = AIClient(
                    provider="openai",
                    api_key=config.openai_api_key,
                    model=config.openai_model
                )
            else:
                self.ai_client = AIClient(
                    provider="anthropic",
                    api_key=config.anthropic_api_key,
                    model=config.anthropic_model
                )

            # Initialize document processor and style analyzer
            self.document_processor = DocumentProcessor(config.writing_samples_path)
            self.style_analyzer = StyleAnalyzer(self.ai_client)

            # Initialize Twitter client
            self.twitter_client = TwitterClient(
                api_key=config.twitter_api_key,
                api_secret=config.twitter_api_secret,
                access_token=config.twitter_access_token,
                access_token_secret=config.twitter_access_token_secret,
                bearer_token=config.twitter_bearer_token
            )

            # Initialize content generator
            self.content_generator = ContentGenerator(
                self.ai_client,
                self.style_analyzer,
                config
            )

            # Initialize scheduler
            self.scheduler = PostingScheduler(
                self.twitter_client,
                self.content_generator,
                config
            )

            self.initialized = True
            logger.info("XPoster initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize XPoster: {e}")
            return False

    def train_style(self):
        """Train the style analyzer on writing samples."""
        if not self.initialized:
            logger.error("XPoster not initialized")
            return False

        logger.info("Loading writing samples...")
        samples = self.document_processor.load_samples()

        if not samples:
            logger.warning("No writing samples found!")
            logger.info(f"Please add text files to: {config.writing_samples_path}")
            return False

        logger.info(f"Training on {len(samples)} samples...")
        style_profile = self.style_analyzer.analyze_samples(samples)

        # Save the style profile
        self.document_processor.save_training_data(
            style_profile,
            "style_profile.json"
        )

        logger.info("Style training completed!")
        return True

    def load_style(self):
        """Load previously trained style profile."""
        if not self.initialized:
            logger.error("XPoster not initialized")
            return False

        try:
            style_profile = self.document_processor.load_training_data("style_profile.json")

            if style_profile:
                self.style_analyzer.style_profile = style_profile
                logger.info("Loaded existing style profile")
                return True
            else:
                logger.warning("No saved style profile found")
                return False

        except Exception as e:
            logger.error(f"Failed to load style profile: {e}")
            return False

    def start_automation(self):
        """Start automated posting and replying."""
        if not self.initialized:
            logger.error("XPoster not initialized")
            return False

        # Ensure style is trained or loaded
        if not self.style_analyzer.style_profile:
            logger.info("No style profile loaded, attempting to load or train...")

            if not self.load_style():
                logger.info("No saved profile found, training new one...")
                if not self.train_style():
                    logger.error("Failed to train style, cannot start automation")
                    return False

        logger.info("Starting automation...")
        self.scheduler.start()

        logger.info("Automation started! Press Ctrl+C to stop.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping automation...")
            self.scheduler.stop()
            logger.info("Automation stopped")

        return True

    def post_now(self, topic: str = None):
        """Post a tweet immediately."""
        if not self.initialized:
            logger.error("XPoster not initialized")
            return False

        # Ensure style is trained or loaded
        if not self.style_analyzer.style_profile:
            if not self.load_style():
                if not self.train_style():
                    logger.error("Failed to train style")
                    return False

        logger.info("Generating and posting tweet...")

        if topic:
            tweet_text = self.content_generator.generate_tweet(topic=topic)
        else:
            # Generate topic ideas first
            ideas = self.content_generator.generate_tweet_ideas(count=3)
            topic = ideas[0] if ideas else None
            tweet_text = self.content_generator.generate_tweet(topic=topic)

        if tweet_text:
            result = self.twitter_client.post_tweet(tweet_text)

            if result:
                logger.info(f"✓ Posted: {tweet_text}")
                return True

        logger.error("Failed to post tweet")
        return False

    def add_sample(self, file_path: str):
        """Add a writing sample from a file."""
        if not self.initialized:
            logger.error("XPoster not initialized")
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            filename = Path(file_path).name
            self.document_processor.add_sample(content, filename)

            logger.info(f"Added sample: {filename}")
            logger.info("Run 'train' command to update style profile")
            return True

        except Exception as e:
            logger.error(f"Failed to add sample: {e}")
            return False


def main():
    """Main entry point for CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="XPoster - Automated X/Twitter posting with personalized style"
    )

    parser.add_argument(
        "command",
        choices=["init", "train", "start", "post", "add-sample"],
        help="Command to execute"
    )

    parser.add_argument(
        "--topic",
        type=str,
        help="Topic for post command"
    )

    parser.add_argument(
        "--file",
        type=str,
        help="File path for add-sample command"
    )

    args = parser.parse_args()

    app = XPoster()

    if args.command == "init":
        logger.info("Initializing XPoster...")
        if app.initialize():
            logger.info("✓ Initialization successful!")
            logger.info(f"Add writing samples to: {config.writing_samples_path}")
        else:
            logger.error("✗ Initialization failed")
            sys.exit(1)

    elif args.command == "train":
        if not app.initialize():
            sys.exit(1)
        if app.train_style():
            logger.info("✓ Style training successful!")
        else:
            logger.error("✗ Style training failed")
            sys.exit(1)

    elif args.command == "start":
        if not app.initialize():
            sys.exit(1)
        app.start_automation()

    elif args.command == "post":
        if not app.initialize():
            sys.exit(1)
        if not app.post_now(topic=args.topic):
            sys.exit(1)

    elif args.command == "add-sample":
        if not args.file:
            logger.error("--file argument required for add-sample command")
            sys.exit(1)
        if not app.initialize():
            sys.exit(1)
        if not app.add_sample(args.file):
            sys.exit(1)


if __name__ == "__main__":
    main()
