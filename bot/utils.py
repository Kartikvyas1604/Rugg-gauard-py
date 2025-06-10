"""
Utility functions for the RugguardBot
"""

import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int, window_seconds: int):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = []
    
    def can_make_call(self) -> bool:
        """Check if a call can be made within rate limits"""
        now = time.time()
        
        # Remove old calls outside the window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.window_seconds]
        
        return len(self.calls) < self.max_calls
    
    def make_call(self):
        """Record a call"""
        self.calls.append(time.time())
    
    def wait_time(self) -> float:
        """Get time to wait before next call"""
        if self.can_make_call():
            return 0
        
        # Find the oldest call in the current window
        now = time.time()
        oldest_call = min(self.calls)
        return self.window_seconds - (now - oldest_call)

class DataCache:
    """Simple in-memory cache for API responses"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            data, expiry = self.cache[key]
            if time.time() < expiry:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        if ttl is None:
            ttl = self.default_ttl
        expiry = time.time() + ttl
        self.cache[key] = (value, expiry)
    
    def clear_expired(self):
        """Clear expired entries"""
        now = time.time()
        expired_keys = [key for key, (_, expiry) in self.cache.items() if now >= expiry]
        for key in expired_keys:
            del self.cache[key]

class ProcessedTweetsTracker:
    """Track processed tweets to avoid duplicates"""
    
    def __init__(self, max_entries: int = 1000):
        self.processed = set()
        self.max_entries = max_entries
        self.last_cleanup = time.time()
    
    def is_processed(self, tweet_id: str) -> bool:
        """Check if tweet has been processed"""
        return tweet_id in self.processed
    
    def mark_processed(self, tweet_id: str):
        """Mark tweet as processed"""
        self.processed.add(tweet_id)
        
        # Cleanup old entries periodically
        if len(self.processed) > self.max_entries:
            self._cleanup()
    
    def _cleanup(self):
        """Remove old entries to prevent memory bloat"""
        if time.time() - self.last_cleanup > 3600:  # Cleanup every hour
            # Keep only the most recent entries (simple approach)
            if len(self.processed) > self.max_entries:
                processed_list = list(self.processed)
                self.processed = set(processed_list[-self.max_entries//2:])
            self.last_cleanup = time.time()

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if division by zero"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default

def format_number(num: int) -> str:
    """Format number with K/M suffixes"""
    try:
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(num)
    except (TypeError, ValueError):
        return "0"

def calculate_time_ago(timestamp: datetime) -> str:
    """Calculate human-readable time ago string"""
    try:
        now = datetime.now()
        if timestamp.tzinfo:
            timestamp = timestamp.replace(tzinfo=None)
        
        diff = now - timestamp
        
        if diff.days > 365:
            return f"{diff.days // 365}y ago"
        elif diff.days > 30:
            return f"{diff.days // 30}mo ago"
        elif diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "now"
    except Exception:
        return "unknown"

def clean_text(text: str) -> str:
    """Clean text for analysis"""
    try:
        if not text:
            return ""
        
        # Remove URLs
        import re
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions and hashtags for analysis
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    except Exception:
        return ""

def generate_cache_key(*args) -> str:
    """Generate a cache key from arguments"""
    try:
        key_string = "|".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()
    except Exception:
        return str(hash(str(args)))

def validate_tweet_id(tweet_id: str) -> bool:
    """Validate if a string is a valid tweet ID"""
    try:
        # Tweet IDs are numeric strings
        int(tweet_id)
        return len(tweet_id) >= 10  # Minimum realistic length
    except (ValueError, TypeError):
        return False

def validate_user_id(user_id: str) -> bool:
    """Validate if a string is a valid user ID"""
    try:
        # User IDs are numeric strings
        int(user_id)
        return len(user_id) >= 5  # Minimum realistic length
    except (ValueError, TypeError):
        return False

def sanitize_username(username: str) -> str:
    """Sanitize username for safe processing"""
    try:
        if not username:
            return ""
        
        # Remove @ symbol and convert to lowercase
        username = username.lstrip('@').lower()
        
        # Remove any non-alphanumeric characters except underscore
        import re
        username = re.sub(r'[^a-z0-9_]', '', username)
        
        return username
    except Exception:
        return ""

def log_api_call(endpoint: str, user_id: str = None, success: bool = True):
    """Log API call for monitoring"""
    try:
        status = "SUCCESS" if success else "FAILED"
        user_info = f" for user {user_id}" if user_id else ""
        logger.info(f"API call to {endpoint}{user_info}: {status}")
    except Exception:
        pass  # Don't let logging errors break the application

def handle_api_error(error: Exception, context: str = "") -> str:
    """Handle API errors and return appropriate error message"""
    try:
        error_str = str(error).lower()
        
        if "rate limit" in error_str:
            return "rate_limit"
        elif "not found" in error_str or "404" in error_str:
            return "not_found"
        elif "forbidden" in error_str or "403" in error_str:
            return "forbidden"
        elif "unauthorized" in error_str or "401" in error_str:
            return "unauthorized"
        else:
            return "general_error"
    except Exception:
        return "general_error"

def retry_on_failure(func, max_retries: int = 3, delay: float = 1.0):
    """Retry function on failure with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            wait_time = delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
            time.sleep(wait_time)

def load_json_file(filepath: str) -> Dict:
    """Safely load JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"JSON file not found: {filepath}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {filepath}: {str(e)}")
        return {}
    except Exception as e:
        logger.error(f"Error loading JSON file {filepath}: {str(e)}")
        return {}

def save_json_file(filepath: str, data: Dict) -> bool:
    """Safely save JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {filepath}: {str(e)}")
        return False

class ConfigValidator:
    """Validate configuration settings"""
    
    @staticmethod
    def validate_positive_int(value: Any, name: str, minimum: int = 1) -> int:
        """Validate positive integer configuration"""
        try:
            int_value = int(value)
            if int_value < minimum:
                raise ValueError(f"{name} must be at least {minimum}")
            return int_value
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid {name}: {str(e)}")
    
    @staticmethod
    def validate_positive_float(value: Any, name: str, minimum: float = 0.0) -> float:
        """Validate positive float configuration"""
        try:
            float_value = float(value)
            if float_value < minimum:
                raise ValueError(f"{name} must be at least {minimum}")
            return float_value
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid {name}: {str(e)}")
    
    @staticmethod
    def validate_url(value: str, name: str) -> str:
        """Validate URL configuration"""
        try:
            if not value.startswith(('http://', 'https://')):
                raise ValueError(f"{name} must be a valid URL")
            return value
        except Exception as e:
            raise ValueError(f"Invalid {name}: {str(e)}")
