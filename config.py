"""
Configuration settings for the RugguardBot
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the bot"""
    
    def __init__(self):
        # X API Configuration
        self.X_API_KEY = os.getenv('X_API_KEY', '')
        self.X_API_SECRET = os.getenv('X_API_SECRET', '')
        self.X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN', '')
        self.X_ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET', '')
        self.X_BEARER_TOKEN = os.getenv('X_BEARER_TOKEN', '')
        
        # Bot Configuration
        self.TRIGGER_PHRASE = os.getenv('TRIGGER_PHRASE', '@projectruggaurd riddle me this')
        self.MONITORED_ACCOUNT = os.getenv('MONITORED_ACCOUNT', '')  # Empty means monitor all
        self.POLLING_INTERVAL = int(os.getenv('POLLING_INTERVAL', '60'))  # seconds
        
        # Trusted Accounts Configuration
        self.TRUSTED_ACCOUNTS_URL = os.getenv(
            'TRUSTED_ACCOUNTS_URL', 
            'https://raw.githubusercontent.com/devsyrem/turst-list/main/list'
        )
        self.TRUSTED_ACCOUNTS_UPDATE_INTERVAL = int(os.getenv('TRUSTED_ACCOUNTS_UPDATE_INTERVAL', '3600'))  # seconds
        self.MIN_TRUSTED_FOLLOWERS = int(os.getenv('MIN_TRUSTED_FOLLOWERS', '3'))  # Changed to 3 as per bounty
        
        # Analysis Configuration
        self.MAX_RECENT_TWEETS = int(os.getenv('MAX_RECENT_TWEETS', '20'))
        self.MIN_ACCOUNT_AGE_DAYS = int(os.getenv('MIN_ACCOUNT_AGE_DAYS', '30'))
        self.SUSPICIOUS_FOLLOWER_RATIO = float(os.getenv('SUSPICIOUS_FOLLOWER_RATIO', '10.0'))
        
        # Rate Limiting
        self.API_RATE_LIMIT_WINDOW = int(os.getenv('API_RATE_LIMIT_WINDOW', '900'))  # 15 minutes
        self.MAX_API_CALLS_PER_WINDOW = int(os.getenv('MAX_API_CALLS_PER_WINDOW', '100'))
        
        # Logging
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'rugguard_bot.log')
    
    def validate(self):
        """Validate that all required configuration is present"""
        required_fields = [
            'X_API_KEY',
            'X_API_SECRET', 
            'X_ACCESS_TOKEN',
            'X_ACCESS_TOKEN_SECRET',
            'X_BEARER_TOKEN'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(self, field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"Missing required configuration: {', '.join(missing_fields)}")
            return False
        
        return True
    
    def get_api_credentials(self):
        """Get API credentials as a dictionary"""
        return {
            'consumer_key': self.X_API_KEY,
            'consumer_secret': self.X_API_SECRET,
            'access_token': self.X_ACCESS_TOKEN,
            'access_token_secret': self.X_ACCESS_TOKEN_SECRET,
            'bearer_token': self.X_BEARER_TOKEN
        }
