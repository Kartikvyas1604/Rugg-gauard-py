"""
X Monitor Module
Handles monitoring of X replies and trigger detection
"""

import tweepy
import logging
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class XMonitor:
    """Monitors X for trigger phrases and manages API interactions"""
    
    def __init__(self, config):
        self.config = config
        self.api_v1 = None
        self.api_v2 = None
        self.client = None
        self.last_checked = datetime.now() - timedelta(minutes=5)
        self.processed_tweets = set()
        
        self._initialize_api()
    
    def _initialize_api(self):
        """Initialize Twitter API clients"""
        try:
            # Initialize API v1.1 for posting replies
            auth = tweepy.OAuth1UserHandler(
                self.config.X_API_KEY,
                self.config.X_API_SECRET,
                self.config.X_ACCESS_TOKEN,
                self.config.X_ACCESS_TOKEN_SECRET
            )
            self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Initialize API v2 for advanced features
            self.client = tweepy.Client(
                bearer_token=self.config.X_BEARER_TOKEN,
                consumer_key=self.config.X_API_KEY,
                consumer_secret=self.config.X_API_SECRET,
                access_token=self.config.X_ACCESS_TOKEN,
                access_token_secret=self.config.X_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True
            )
            
            # Test API connection
            self.client.get_me()
            logger.info("X API connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize X API: {str(e)}")
            raise
    
    def check_for_triggers(self) -> List[Dict]:
        """
        Check for new trigger phrases in replies
        
        Returns:
            List of trigger events with tweet IDs and original author info
        """
        triggers = []
        
        try:
            # Search for recent tweets containing the trigger phrase
            # Handle mention-based trigger phrase properly
            if self.config.TRIGGER_PHRASE.startswith('@'):
                # For mention-based triggers, search for the phrase without quotes
                query = f'{self.config.TRIGGER_PHRASE} -is:retweet'
            else:
                query = f'"{self.config.TRIGGER_PHRASE}" -is:retweet'
            
            # If monitoring specific account, add it to query
            if self.config.MONITORED_ACCOUNT:
                query += f" to:{self.config.MONITORED_ACCOUNT}"
            
            # Search for tweets
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=10,
                tweet_fields=['created_at', 'author_id', 'in_reply_to_user_id', 'referenced_tweets'],
                expansions=['author_id', 'in_reply_to_user_id', 'referenced_tweets.id'],
                since_id=self._get_last_tweet_id()
            )
            
            if not tweets.data:
                return triggers
            
            for tweet in tweets.data:
                if tweet.id in self.processed_tweets:
                    continue
                
                # Check if this is a reply and contains exact trigger phrase
                if self._is_valid_trigger(tweet):
                    trigger_info = self._extract_trigger_info(tweet, tweets.includes)
                    if trigger_info:
                        triggers.append(trigger_info)
                        self.processed_tweets.add(tweet.id)
            
            self.last_checked = datetime.now()
            
        except Exception as e:
            logger.error(f"Error checking for triggers: {str(e)}")
        
        return triggers
    
    def _is_valid_trigger(self, tweet) -> bool:
        """Check if tweet is a valid trigger"""
        # Must be a reply
        if not tweet.in_reply_to_user_id:
            return False
        
        # Must contain exact trigger phrase (case insensitive)
        tweet_text = tweet.text.lower()
        trigger_phrase = self.config.TRIGGER_PHRASE.lower()
        
        # Handle mention variations (@projectruggaurd vs @projectrugguard)
        if '@projectruggaurd riddle me this' in tweet_text or '@projectrugguard riddle me this' in tweet_text:
            pass  # Valid trigger found
        elif trigger_phrase in tweet_text:
            pass  # Fallback to config trigger phrase
        else:
            return False
        
        # Must be recent enough
        tweet_time = tweet.created_at.replace(tzinfo=None)
        if datetime.now() - tweet_time > timedelta(hours=1):
            return False
        
        return True
    
    def _extract_trigger_info(self, tweet, includes) -> Optional[Dict]:
        """Extract information about the trigger and original tweet"""
        try:
            # Find the original tweet being replied to
            original_tweet_id = None
            original_author_id = None
            
            # Look for referenced tweets
            if hasattr(tweet, 'referenced_tweets') and tweet.referenced_tweets:
                for ref in tweet.referenced_tweets:
                    if ref.type == 'replied_to':
                        original_tweet_id = ref.id
                        break
            
            # Get original tweet details
            if original_tweet_id:
                try:
                    original_tweet = self.client.get_tweet(
                        original_tweet_id,
                        tweet_fields=['author_id']
                    )
                    if original_tweet.data:
                        original_author_id = original_tweet.data.author_id
                except Exception as e:
                    logger.error(f"Error getting original tweet: {str(e)}")
                    return None
            
            if not original_author_id:
                logger.warning(f"Could not determine original author for trigger tweet {tweet.id}")
                return None
            
            return {
                'trigger_tweet_id': tweet.id,
                'original_tweet_id': original_tweet_id,
                'original_author_id': original_author_id,
                'trigger_time': tweet.created_at
            }
            
        except Exception as e:
            logger.error(f"Error extracting trigger info: {str(e)}")
            return None
    
    def _get_last_tweet_id(self) -> Optional[str]:
        """Get the ID of the last processed tweet for pagination"""
        # This would typically be stored in a database or file
        # For now, return None to get recent tweets
        return None
    
    def post_reply(self, tweet_id: str, message: str) -> bool:
        """
        Post a reply to a tweet
        
        Args:
            tweet_id: ID of the tweet to reply to
            message: Reply message content
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure message is within character limit
            if len(message) > 280:
                message = message[:275] + "..."
            
            # Post reply using API v2
            response = self.client.create_tweet(
                text=message,
                in_reply_to_tweet_id=tweet_id
            )
            
            if response.data:
                logger.info(f"Posted reply to tweet {tweet_id}")
                return True
            else:
                logger.error(f"Failed to post reply to tweet {tweet_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error posting reply: {str(e)}")
            return False
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """
        Get detailed user information
        
        Args:
            user_id: X user ID
        
        Returns:
            Dictionary with user information or None if error
        """
        try:
            user = self.client.get_user(
                id=user_id,
                user_fields=[
                    'created_at', 'description', 'public_metrics',
                    'verified', 'location', 'profile_image_url'
                ]
            )
            
            if user.data:
                return {
                    'id': user.data.id,
                    'username': user.data.username,
                    'name': user.data.name,
                    'created_at': user.data.created_at,
                    'description': user.data.description or '',
                    'followers_count': user.data.public_metrics['followers_count'],
                    'following_count': user.data.public_metrics['following_count'],
                    'tweet_count': user.data.public_metrics['tweet_count'],
                    'listed_count': user.data.public_metrics['listed_count'],
                    'verified': user.data.verified,
                    'location': user.data.location,
                    'profile_image_url': user.data.profile_image_url
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user info for {user_id}: {str(e)}")
            return None
    
    def get_user_tweets(self, user_id: str, max_results: int = 20) -> List[Dict]:
        """
        Get recent tweets from a user
        
        Args:
            user_id: X user ID
            max_results: Maximum number of tweets to retrieve
        
        Returns:
            List of tweet information dictionaries
        """
        try:
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                tweet_fields=[
                    'created_at', 'public_metrics', 'context_annotations',
                    'lang', 'possibly_sensitive', 'reply_settings'
                ]
            )
            
            if not tweets.data:
                return []
            
            tweet_list = []
            for tweet in tweets.data:
                tweet_info = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'retweet_count': tweet.public_metrics['retweet_count'],
                    'like_count': tweet.public_metrics['like_count'],
                    'reply_count': tweet.public_metrics['reply_count'],
                    'quote_count': tweet.public_metrics['quote_count'],
                    'lang': tweet.lang,
                    'possibly_sensitive': tweet.possibly_sensitive
                }
                tweet_list.append(tweet_info)
            
            return tweet_list
            
        except Exception as e:
            logger.error(f"Error getting tweets for user {user_id}: {str(e)}")
            return []
