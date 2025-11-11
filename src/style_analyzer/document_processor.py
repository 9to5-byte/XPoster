"""Document processing for style learning."""

import json
import re
from pathlib import Path
from typing import List, Dict, Any

from loguru import logger


class DocumentProcessor:
    """Process documents to extract writing samples."""

    def __init__(self, samples_dir: Path):
        """Initialize document processor.

        Args:
            samples_dir: Directory containing writing samples
        """
        self.samples_dir = Path(samples_dir)
        self.samples_dir.mkdir(parents=True, exist_ok=True)

    def load_samples(self) -> List[str]:
        """Load all writing samples from the samples directory.

        Returns:
            List of text samples
        """
        samples = []

        # Supported file types
        extensions = [".txt", ".md", ".text"]

        for ext in extensions:
            for file_path in self.samples_dir.glob(f"*{ext}"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            samples.append(content)
                            logger.info(f"Loaded sample from {file_path.name}")
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")

        logger.info(f"Loaded {len(samples)} writing samples")
        return samples

    def add_sample(self, content: str, filename: str = None) -> Path:
        """Add a new writing sample.

        Args:
            content: Text content to add
            filename: Optional filename (will be generated if not provided)

        Returns:
            Path to the saved sample file
        """
        if not filename:
            # Generate filename based on timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sample_{timestamp}.txt"

        file_path = self.samples_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Added new writing sample: {filename}")
        return file_path

    def split_into_segments(self, text: str, min_length: int = 100) -> List[str]:
        """Split text into smaller segments for analysis.

        Args:
            text: Text to split
            min_length: Minimum length for each segment

        Returns:
            List of text segments
        """
        # Split by paragraphs
        paragraphs = re.split(r"\n\n+", text)

        segments = []
        current_segment = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_segment) + len(para) < min_length:
                current_segment += para + "\n\n"
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = para + "\n\n"

        # Add the last segment
        if current_segment.strip():
            segments.append(current_segment.strip())

        return segments

    def extract_tweets(self, text: str) -> List[str]:
        """Extract tweet-sized segments from text.

        Args:
            text: Text to extract from

        Returns:
            List of tweet-sized segments
        """
        # Split by sentences
        sentences = re.split(r"[.!?]+", text)

        tweets = []
        current_tweet = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Check if adding this sentence would exceed tweet length
            if len(current_tweet) + len(sentence) + 2 <= 280:  # +2 for punctuation
                current_tweet += sentence + ". "
            else:
                if current_tweet.strip():
                    tweets.append(current_tweet.strip())
                current_tweet = sentence + ". "

        # Add the last tweet
        if current_tweet.strip():
            tweets.append(current_tweet.strip())

        return tweets

    def save_training_data(self, data: Dict[str, Any], filename: str) -> Path:
        """Save processed training data.

        Args:
            data: Training data dictionary
            filename: Output filename

        Returns:
            Path to saved file
        """
        from ..config import config

        output_path = config.training_data_path / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved training data to {filename}")
        return output_path

    def load_training_data(self, filename: str) -> Dict[str, Any]:
        """Load processed training data.

        Args:
            filename: Input filename

        Returns:
            Training data dictionary
        """
        from ..config import config

        input_path = config.training_data_path / filename
        if not input_path.exists():
            logger.warning(f"Training data file not found: {filename}")
            return {}

        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)
