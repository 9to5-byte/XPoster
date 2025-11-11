"""Automated posting and reply scheduler."""

import random
from datetime import datetime, time
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from loguru import logger


class PostingScheduler:
    """Scheduler for automated posting and replying."""

    def __init__(
        self,
        twitter_client,
        content_generator,
        config
    ):
        """Initialize scheduler.

        Args:
            twitter_client: Twitter API client
            content_generator: Content generator
            config: Application configuration
        """
        self.twitter_client = twitter_client
        self.content_generator = content_generator
        self.config = config

        self.scheduler = BackgroundScheduler()
        self.posts_today = 0
        self.last_mention_id: Optional[str] = None

    def start(self):
        """Start the scheduler."""
        # Schedule posting if enabled
        if self.config.get("posting.enabled", True):
            self._schedule_posting()

        # Schedule reply monitoring if enabled
        if self.config.get("replies.enabled", True):
            self._schedule_reply_monitoring()

        self.scheduler.start()
        logger.info("Scheduler started")

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    def _schedule_posting(self):
        """Schedule automated tweet posting."""
        # Get posting configuration
        max_posts = self.config.get("posting.max_posts_per_day", 10)
        start_hour = self.config.get("posting.posting_hours.start", 9)
        end_hour = self.config.get("posting.posting_hours.end", 21)

        # Calculate interval between posts
        active_hours = end_hour - start_hour
        if active_hours <= 0:
            logger.warning("Invalid posting hours configuration")
            return

        interval_minutes = (active_hours * 60) // max_posts

        # Add some randomization
        min_interval = int(interval_minutes * 0.8)
        max_interval = int(interval_minutes * 1.2)

        logger.info(
            f"Scheduling posts: {max_posts}/day, "
            f"interval: {min_interval}-{max_interval} minutes, "
            f"hours: {start_hour}-{end_hour}"
        )

        # Schedule with random intervals
        self.scheduler.add_job(
            self._post_tweet_job,
            IntervalTrigger(minutes=random.randint(min_interval, max_interval)),
            id="post_tweet",
            replace_existing=True
        )

        # Reset daily counter at midnight
        self.scheduler.add_job(
            self._reset_daily_counter,
            CronTrigger(hour=0, minute=0),
            id="reset_counter",
            replace_existing=True
        )

    def _schedule_reply_monitoring(self):
        """Schedule monitoring for tweets to reply to."""
        check_interval = self.config.get("replies.check_interval_minutes", 30)

        logger.info(f"Scheduling reply monitoring: every {check_interval} minutes")

        self.scheduler.add_job(
            self._monitor_and_reply_job,
            IntervalTrigger(minutes=check_interval),
            id="monitor_replies",
            replace_existing=True
        )

    def _post_tweet_job(self):
        """Job to post a new tweet."""
        try:
            # Check if within posting hours
            now = datetime.now().time()
            start_time = time(self.config.get("posting.posting_hours.start", 9), 0)
            end_time = time(self.config.get("posting.posting_hours.end", 21), 0)

            if not (start_time <= now <= end_time):
                logger.debug("Outside posting hours, skipping")
                return

            # Check daily limit
            max_posts = self.config.get("posting.max_posts_per_day", 10)
            if self.posts_today >= max_posts:
                logger.info("Daily post limit reached, skipping")
                return

            # Generate tweet ideas and pick one
            ideas = self.content_generator.generate_tweet_ideas(count=3)

            if not ideas:
                logger.warning("No tweet ideas generated, using random topic")
                topic = None
            else:
                topic = random.choice(ideas)

            # Generate and post tweet
            tweet_text = self.content_generator.generate_tweet(topic=topic)

            if tweet_text:
                result = self.twitter_client.post_tweet(tweet_text)

                if result:
                    self.posts_today += 1
                    logger.info(f"Posted tweet ({self.posts_today}/{max_posts} today)")

        except Exception as e:
            logger.error(f"Error in post tweet job: {e}")

    def _monitor_and_reply_job(self):
        """Job to monitor mentions and timeline for reply opportunities."""
        try:
            # Check mentions
            mentions = self.twitter_client.get_mentions(
                since_id=self.last_mention_id,
                max_results=10
            )

            if mentions:
                # Update last mention ID
                self.last_mention_id = mentions[0]["id"]

                # Reply to mentions
                for mention in mentions:
                    self._reply_to_mention(mention)

            # Also check home timeline for reply opportunities
            self._monitor_timeline()

        except Exception as e:
            logger.error(f"Error in monitor and reply job: {e}")

    def _reply_to_mention(self, mention: dict):
        """Reply to a mention.

        Args:
            mention: Mention data
        """
        try:
            # Generate reply
            reply_text = self.content_generator.generate_reply(
                original_tweet=mention["text"]
            )

            if reply_text:
                result = self.twitter_client.reply_to_tweet(
                    tweet_id=mention["id"],
                    text=reply_text
                )

                if result:
                    logger.info(f"Replied to mention {mention['id']}")

        except Exception as e:
            logger.error(f"Error replying to mention: {e}")

    def _monitor_timeline(self):
        """Monitor home timeline for reply opportunities."""
        try:
            max_replies = self.config.get("replies.max_replies_per_check", 5)

            # Get recent tweets from timeline
            tweets = self.twitter_client.get_home_timeline(max_results=20)

            replies_sent = 0

            for tweet in tweets:
                if replies_sent >= max_replies:
                    break

                # Skip our own tweets
                if tweet.get("author_id") == self.twitter_client.user_id:
                    continue

                # Decide whether to reply
                if self.content_generator.should_reply_to_tweet(tweet):
                    reply_text = self.content_generator.generate_reply(
                        original_tweet=tweet["text"],
                        original_author=tweet.get("author_screen_name")
                    )

                    if reply_text:
                        result = self.twitter_client.reply_to_tweet(
                            tweet_id=tweet["id"],
                            text=reply_text
                        )

                        if result:
                            replies_sent += 1
                            logger.info(f"Replied to tweet {tweet['id']}")

        except Exception as e:
            logger.error(f"Error monitoring timeline: {e}")

    def _reset_daily_counter(self):
        """Reset daily post counter."""
        logger.info(f"Resetting daily counter (was {self.posts_today})")
        self.posts_today = 0

    def post_now(self, topic: Optional[str] = None):
        """Manually trigger a post immediately.

        Args:
            topic: Optional topic to post about
        """
        logger.info(f"Manual post triggered{' with topic: ' + topic if topic else ''}")
        tweet_text = self.content_generator.generate_tweet(topic=topic)

        if tweet_text:
            result = self.twitter_client.post_tweet(tweet_text)

            if result:
                self.posts_today += 1
                logger.info("Manual post successful")
                return result

        logger.error("Manual post failed")
        return None
