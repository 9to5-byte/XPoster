"""Twitter/X API client."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

import tweepy
from loguru import logger


class TwitterClient:
    """Client for interacting with Twitter/X API."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str,
        bearer_token: Optional[str] = None
    ):
        """Initialize Twitter client.

        Args:
            api_key: Twitter API key
            api_secret: Twitter API secret
            access_token: Access token
            access_token_secret: Access token secret
            bearer_token: Optional bearer token for v2 API
        """
        # Initialize v1.1 API (for posting)
        auth = tweepy.OAuth1UserHandler(
            api_key,
            api_secret,
            access_token,
            access_token_secret
        )
        self.api_v1 = tweepy.API(auth)

        # Initialize v2 client (for better read functionality)
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )

        # Verify credentials
        try:
            user = self.api_v1.verify_credentials()
            self.user_id = user.id_str
            self.screen_name = user.screen_name
            logger.info(f"Authenticated as @{self.screen_name}")
        except Exception as e:
            logger.error(f"Failed to authenticate: {e}")
            raise

    def post_tweet(self, text: str) -> Optional[Dict[str, Any]]:
        """Post a new tweet.

        Args:
            text: Tweet text (max 280 characters)

        Returns:
            Tweet data or None if failed
        """
        try:
            if len(text) > 280:
                logger.warning(f"Tweet too long ({len(text)} chars), truncating...")
                text = text[:277] + "..."

            response = self.client.create_tweet(text=text)

            logger.info(f"Posted tweet: {text[:50]}...")
            return {
                "id": response.data["id"],
                "text": text,
                "created_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return None

    def reply_to_tweet(self, tweet_id: str, text: str) -> Optional[Dict[str, Any]]:
        """Reply to a tweet.

        Args:
            tweet_id: ID of tweet to reply to
            text: Reply text

        Returns:
            Reply data or None if failed
        """
        try:
            if len(text) > 280:
                logger.warning(f"Reply too long ({len(text)} chars), truncating...")
                text = text[:277] + "..."

            response = self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=tweet_id
            )

            logger.info(f"Posted reply to {tweet_id}: {text[:50]}...")
            return {
                "id": response.data["id"],
                "text": text,
                "reply_to": tweet_id,
                "created_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to post reply: {e}")
            return None

    def get_mentions(self, since_id: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent mentions.

        Args:
            since_id: Only get mentions after this tweet ID
            max_results: Maximum number of mentions to retrieve

        Returns:
            List of mention data
        """
        try:
            kwargs = {
                "max_results": min(max_results, 100),
                "tweet_fields": ["created_at", "author_id", "conversation_id"]
            }

            if since_id:
                kwargs["since_id"] = since_id

            response = self.client.get_users_mentions(
                id=self.user_id,
                **kwargs
            )

            if not response.data:
                return []

            mentions = []
            for tweet in response.data:
                mentions.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "author_id": tweet.author_id,
                    "created_at": tweet.created_at.isoformat(),
                    "conversation_id": tweet.conversation_id
                })

            logger.info(f"Retrieved {len(mentions)} mentions")
            return mentions

        except Exception as e:
            logger.error(f"Failed to get mentions: {e}")
            return []

    def search_recent_tweets(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for recent tweets matching a query.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of tweet data
        """
        try:
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=["created_at", "author_id", "public_metrics"]
            )

            if not response.data:
                return []

            tweets = []
            for tweet in response.data:
                tweets.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "author_id": tweet.author_id,
                    "created_at": tweet.created_at.isoformat(),
                    "metrics": tweet.public_metrics
                })

            logger.info(f"Found {len(tweets)} tweets for query: {query}")
            return tweets

        except Exception as e:
            logger.error(f"Failed to search tweets: {e}")
            return []

    def get_home_timeline(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get tweets from home timeline.

        Args:
            max_results: Maximum number of tweets

        Returns:
            List of tweet data
        """
        try:
            tweets_data = self.api_v1.home_timeline(count=max_results)

            tweets = []
            for tweet in tweets_data:
                tweets.append({
                    "id": tweet.id_str,
                    "text": tweet.text,
                    "author_id": tweet.user.id_str,
                    "author_screen_name": tweet.user.screen_name,
                    "created_at": tweet.created_at.isoformat()
                })

            logger.info(f"Retrieved {len(tweets)} tweets from home timeline")
            return tweets

        except Exception as e:
            logger.error(f"Failed to get home timeline: {e}")
            return []

    def get_my_recent_tweets(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get user's own recent tweets.

        Args:
            max_results: Maximum number of tweets

        Returns:
            List of tweet data
        """
        try:
            response = self.client.get_users_tweets(
                id=self.user_id,
                max_results=min(max_results, 100),
                tweet_fields=["created_at"]
            )

            if not response.data:
                return []

            tweets = []
            for tweet in response.data:
                tweets.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat()
                })

            return tweets

        except Exception as e:
            logger.error(f"Failed to get user tweets: {e}")
            return []
