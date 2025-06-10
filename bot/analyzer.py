"""
Account Analyzer Module
Performs comprehensive analysis of X accounts
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from textblob import TextBlob
import statistics

logger = logging.getLogger(__name__)

class AccountAnalyzer:
    """Analyzes X accounts for trustworthiness indicators"""
    
    def __init__(self, config):
        self.config = config
        self.suspicious_keywords = [
            'pump', 'moon', 'lambo', 'diamond hands', 'hodl', 'ape',
            'guaranteed', 'returns', 'investment opportunity', 'exclusive',
            'limited time', 'act now', 'don\'t miss out', 'financial advice'
        ]
        self.positive_keywords = [
            'research', 'analysis', 'education', 'community', 'development',
            'building', 'learning', 'discussing', 'sharing', 'helping'
        ]
    
    def analyze_account(self, user_id: str) -> Optional[Dict]:
        """
        Perform comprehensive account analysis
        
        Args:
            user_id: X user ID to analyze
        
        Returns:
            Dictionary with analysis results or None if error
        """
        try:
            from .monitor import XMonitor
            monitor = XMonitor(self.config)
            
            # Get user information
            user_info = monitor.get_user_info(user_id)
            if not user_info:
                logger.error(f"Could not retrieve user info for {user_id}")
                return None
            
            # Get user tweets
            user_tweets = monitor.get_user_tweets(user_id, self.config.MAX_RECENT_TWEETS)
            
            # Perform analysis
            analysis = {
                'user_id': user_id,
                'username': user_info['username'],
                'name': user_info['name'],
                'account_age': self._calculate_account_age(user_info['created_at']),
                'follower_following_ratio': self._calculate_follower_ratio(user_info),
                'bio_analysis': self._analyze_bio(user_info['description']),
                'engagement_analysis': self._analyze_engagement(user_tweets),
                'content_analysis': self._analyze_content(user_tweets),
                'activity_patterns': self._analyze_activity_patterns(user_tweets),
                'verification_status': user_info['verified'],
                'raw_metrics': {
                    'followers_count': user_info['followers_count'],
                    'following_count': user_info['following_count'],
                    'tweet_count': user_info['tweet_count'],
                    'listed_count': user_info['listed_count']
                },
                'risk_score': 0  # Will be calculated based on analysis
            }
            
            # Calculate overall risk score
            analysis['risk_score'] = self._calculate_risk_score(analysis)
            
            logger.info(f"Completed analysis for user {user_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing account {user_id}: {str(e)}")
            return None
    
    def _calculate_account_age(self, created_at: datetime) -> Dict:
        """Calculate account age and related metrics"""
        try:
            now = datetime.now()
            if created_at.tzinfo:
                created_at = created_at.replace(tzinfo=None)
            
            age_delta = now - created_at
            age_days = age_delta.days
            
            return {
                'days': age_days,
                'months': age_days // 30,
                'years': age_days // 365,
                'is_new': age_days < self.config.MIN_ACCOUNT_AGE_DAYS,
                'created_date': created_at.strftime('%Y-%m-%d')
            }
        except Exception as e:
            logger.error(f"Error calculating account age: {str(e)}")
            return {'days': 0, 'months': 0, 'years': 0, 'is_new': True, 'created_date': 'unknown'}
    
    def _calculate_follower_ratio(self, user_info: Dict) -> Dict:
        """Analyze follower to following ratio"""
        try:
            followers = user_info['followers_count']
            following = user_info['following_count']
            
            if following == 0:
                ratio = followers  # Following no one but has followers
            else:
                ratio = followers / following
            
            return {
                'ratio': round(ratio, 2),
                'followers': followers,
                'following': following,
                'is_suspicious': ratio > self.config.SUSPICIOUS_FOLLOWER_RATIO or (followers > 1000 and following < 10),
                'interpretation': self._interpret_follower_ratio(ratio, followers, following)
            }
        except Exception as e:
            logger.error(f"Error calculating follower ratio: {str(e)}")
            return {'ratio': 0, 'followers': 0, 'following': 0, 'is_suspicious': True, 'interpretation': 'Error calculating'}
    
    def _interpret_follower_ratio(self, ratio: float, followers: int, following: int) -> str:
        """Interpret follower ratio meaning"""
        if ratio > 100:
            return "Very high ratio - possible influencer or suspicious bot activity"
        elif ratio > 10:
            return "High ratio - established account or selective following"
        elif ratio > 1:
            return "Balanced ratio - normal engagement pattern"
        elif ratio > 0.1:
            return "Low ratio - active in following others"
        else:
            return "Very low ratio - following much more than followers"
    
    def _analyze_bio(self, bio: str) -> Dict:
        """Analyze user bio for keywords and patterns"""
        try:
            if not bio:
                return {
                    'length': 0,
                    'has_bio': False,
                    'suspicious_keywords': [],
                    'positive_keywords': [],
                    'contains_links': False,
                    'risk_level': 'medium'
                }
            
            bio_lower = bio.lower()
            
            # Check for suspicious keywords
            found_suspicious = [kw for kw in self.suspicious_keywords if kw in bio_lower]
            found_positive = [kw for kw in self.positive_keywords if kw in bio_lower]
            
            # Check for links
            contains_links = bool(re.search(r'http[s]?://|www\.|\.[a-z]{2,}', bio))
            
            # Determine risk level
            risk_level = 'low'
            if len(found_suspicious) > 2:
                risk_level = 'high'
            elif len(found_suspicious) > 0:
                risk_level = 'medium'
            elif len(found_positive) > 0:
                risk_level = 'low'
            
            return {
                'length': len(bio),
                'has_bio': True,
                'suspicious_keywords': found_suspicious,
                'positive_keywords': found_positive,
                'contains_links': contains_links,
                'risk_level': risk_level,
                'text': bio[:100] + '...' if len(bio) > 100 else bio
            }
            
        except Exception as e:
            logger.error(f"Error analyzing bio: {str(e)}")
            return {'length': 0, 'has_bio': False, 'suspicious_keywords': [], 'positive_keywords': [], 'contains_links': False, 'risk_level': 'high'}
    
    def _analyze_engagement(self, tweets: List[Dict]) -> Dict:
        """Analyze engagement patterns"""
        try:
            if not tweets:
                return {
                    'avg_likes': 0,
                    'avg_retweets': 0,
                    'avg_replies': 0,
                    'engagement_rate': 0,
                    'pattern': 'no_data'
                }
            
            likes = [t['like_count'] for t in tweets]
            retweets = [t['retweet_count'] for t in tweets]
            replies = [t['reply_count'] for t in tweets]
            
            avg_likes = statistics.mean(likes) if likes else 0
            avg_retweets = statistics.mean(retweets) if retweets else 0
            avg_replies = statistics.mean(replies) if replies else 0
            
            # Calculate engagement rate (simplified)
            total_engagement = sum(likes) + sum(retweets) + sum(replies)
            engagement_rate = total_engagement / len(tweets) if tweets else 0
            
            # Determine engagement pattern
            pattern = self._classify_engagement_pattern(avg_likes, avg_retweets, avg_replies)
            
            return {
                'avg_likes': round(avg_likes, 1),
                'avg_retweets': round(avg_retweets, 1),
                'avg_replies': round(avg_replies, 1),
                'engagement_rate': round(engagement_rate, 1),
                'pattern': pattern,
                'total_tweets_analyzed': len(tweets)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing engagement: {str(e)}")
            return {'avg_likes': 0, 'avg_retweets': 0, 'avg_replies': 0, 'engagement_rate': 0, 'pattern': 'error'}
    
    def _classify_engagement_pattern(self, likes: float, retweets: float, replies: float) -> str:
        """Classify engagement pattern"""
        if likes > 100 and retweets > 20:
            return "high_engagement"
        elif likes > 10 and retweets > 2:
            return "moderate_engagement"
        elif likes > 1:
            return "low_engagement"
        else:
            return "minimal_engagement"
    
    def _analyze_content(self, tweets: List[Dict]) -> Dict:
        """Analyze tweet content for sentiment and topics"""
        try:
            if not tweets:
                return {
                    'sentiment_score': 0,
                    'sentiment_label': 'neutral',
                    'topics': [],
                    'language_distribution': {},
                    'suspicious_content_count': 0
                }
            
            # Combine all tweet text
            all_text = ' '.join([t['text'] for t in tweets])
            
            # Sentiment analysis
            blob = TextBlob(all_text)
            sentiment_score = blob.sentiment.polarity
            
            if sentiment_score > 0.1:
                sentiment_label = 'positive'
            elif sentiment_score < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            # Language distribution
            languages = [t.get('lang', 'unknown') for t in tweets]
            lang_dist = {}
            for lang in languages:
                lang_dist[lang] = lang_dist.get(lang, 0) + 1
            
            # Check for suspicious content
            suspicious_count = 0
            for tweet in tweets:
                text_lower = tweet['text'].lower()
                if any(kw in text_lower for kw in self.suspicious_keywords):
                    suspicious_count += 1
            
            # Extract common topics (simplified)
            topics = self._extract_topics(all_text)
            
            return {
                'sentiment_score': round(sentiment_score, 3),
                'sentiment_label': sentiment_label,
                'topics': topics,
                'language_distribution': lang_dist,
                'suspicious_content_count': suspicious_count,
                'suspicious_content_ratio': round(suspicious_count / len(tweets), 2) if tweets else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            return {'sentiment_score': 0, 'sentiment_label': 'neutral', 'topics': [], 'language_distribution': {}, 'suspicious_content_count': 0}
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract common topics from text (simplified approach)"""
        try:
            # Simple keyword-based topic extraction
            crypto_keywords = ['bitcoin', 'ethereum', 'crypto', 'blockchain', 'defi', 'nft', 'solana', 'token']
            finance_keywords = ['trading', 'investment', 'market', 'price', 'profit', 'loss', 'portfolio']
            tech_keywords = ['development', 'coding', 'programming', 'software', 'app', 'web3']
            
            text_lower = text.lower()
            topics = []
            
            if any(kw in text_lower for kw in crypto_keywords):
                topics.append('cryptocurrency')
            if any(kw in text_lower for kw in finance_keywords):
                topics.append('finance')
            if any(kw in text_lower for kw in tech_keywords):
                topics.append('technology')
            
            return topics
            
        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            return []
    
    def _analyze_activity_patterns(self, tweets: List[Dict]) -> Dict:
        """Analyze posting activity patterns"""
        try:
            if not tweets:
                return {
                    'posting_frequency': 'no_data',
                    'recent_activity': False,
                    'consistent_activity': False
                }
            
            # Sort tweets by date
            sorted_tweets = sorted(tweets, key=lambda x: x['created_at'], reverse=True)
            
            # Check recent activity (last 7 days)
            now = datetime.now()
            recent_cutoff = now - timedelta(days=7)
            
            recent_tweets = []
            for tweet in sorted_tweets:
                tweet_time = tweet['created_at']
                if tweet_time.tzinfo:
                    tweet_time = tweet_time.replace(tzinfo=None)
                if tweet_time > recent_cutoff:
                    recent_tweets.append(tweet)
            
            recent_activity = len(recent_tweets) > 0
            
            # Determine posting frequency
            if len(tweets) >= 20:
                oldest_tweet = sorted_tweets[-1]['created_at']
                if oldest_tweet.tzinfo:
                    oldest_tweet = oldest_tweet.replace(tzinfo=None)
                days_span = (now - oldest_tweet).days
                if days_span > 0:
                    tweets_per_day = len(tweets) / days_span
                    if tweets_per_day > 5:
                        frequency = 'very_high'
                    elif tweets_per_day > 2:
                        frequency = 'high'
                    elif tweets_per_day > 0.5:
                        frequency = 'moderate'
                    else:
                        frequency = 'low'
                else:
                    frequency = 'burst'
            else:
                frequency = 'low'
            
            return {
                'posting_frequency': frequency,
                'recent_activity': recent_activity,
                'recent_tweets_count': len(recent_tweets),
                'consistent_activity': frequency in ['moderate', 'high']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing activity patterns: {str(e)}")
            return {'posting_frequency': 'error', 'recent_activity': False, 'consistent_activity': False}
    
    def _calculate_risk_score(self, analysis: Dict) -> float:
        """Calculate overall risk score (0-100, higher = more risky)"""
        try:
            risk_score = 0
            
            # Account age factor
            if analysis['account_age']['is_new']:
                risk_score += 25
            
            # Follower ratio factor
            if analysis['follower_following_ratio']['is_suspicious']:
                risk_score += 20
            
            # Bio analysis factor
            bio_risk = analysis['bio_analysis']['risk_level']
            if bio_risk == 'high':
                risk_score += 20
            elif bio_risk == 'medium':
                risk_score += 10
            
            # Content analysis factor
            suspicious_ratio = analysis['content_analysis']['suspicious_content_ratio']
            risk_score += suspicious_ratio * 15
            
            # Engagement pattern factor
            engagement_pattern = analysis['engagement_analysis']['pattern']
            if engagement_pattern == 'minimal_engagement':
                risk_score += 10
            elif engagement_pattern == 'high_engagement':
                risk_score -= 5  # Subtract for good engagement
            
            # Activity pattern factor
            if not analysis['activity_patterns']['consistent_activity']:
                risk_score += 10
            
            # Verification status (reduce risk if verified)
            if analysis['verification_status']:
                risk_score -= 15
            
            # Ensure score is within bounds
            risk_score = max(0, min(100, risk_score))
            
            return round(risk_score, 1)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return 50.0  # Default medium risk
