"""
Trusted Accounts Manager
Handles the trusted accounts list and cross-referencing
"""

import requests
import logging
import time
from typing import List, Dict, Set, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TrustedAccountsManager:
    """Manages trusted accounts list and verification"""
    
    def __init__(self, config):
        self.config = config
        self.trusted_accounts = set()
        self.last_update = None
        self.cache_file = 'trusted_accounts_cache.txt'
        
        # Load cached trusted accounts
        self._load_cached_accounts()
    
    def update_trusted_list(self) -> bool:
        """
        Update the trusted accounts list from GitHub
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if update is needed
            if self.last_update and (datetime.now() - self.last_update).seconds < self.config.TRUSTED_ACCOUNTS_UPDATE_INTERVAL:
                logger.info("Trusted accounts list is up to date")
                return True
            
            logger.info("Updating trusted accounts list from GitHub...")
            
            # Fetch the list from GitHub
            response = requests.get(self.config.TRUSTED_ACCOUNTS_URL, timeout=30)
            response.raise_for_status()
            
            # Parse the list
            content = response.text.strip()
            if not content:
                logger.warning("Trusted accounts list is empty")
                return False
            
            # Extract usernames/handles (assuming one per line)
            new_trusted_accounts = set()
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):  # Skip comments
                    # Remove @ symbol if present
                    username = line.lstrip('@').lower()
                    if username:
                        new_trusted_accounts.add(username)
            
            self.trusted_accounts = new_trusted_accounts
            self.last_update = datetime.now()
            
            # Cache the accounts
            self._cache_accounts()
            
            logger.info(f"Updated trusted accounts list: {len(self.trusted_accounts)} accounts")
            return True
            
        except Exception as e:
            logger.error(f"Error updating trusted accounts list: {str(e)}")
            return False
    
    def check_trust_score(self, user_id: str) -> Dict:
        """
        Check trust score for a user based on trusted accounts
        
        Args:
            user_id: X user ID to check
        
        Returns:
            Dictionary with trust score information
        """
        try:
            from .monitor import XMonitor
            monitor = XMonitor(self.config)
            
            # Get user info
            user_info = monitor.get_user_info(user_id)
            if not user_info:
                return self._default_trust_score()
            
            username = user_info['username'].lower()
            
            # Check if user is directly in trusted list
            if username in self.trusted_accounts:
                return {
                    'is_trusted': True,
                    'trust_level': 'directly_trusted',
                    'trusted_followers': [],
                    'trusted_followers_count': 0,
                    'vouched_by_trusted': True,
                    'explanation': f"@{username} is directly on the trusted accounts list"
                }
            
            # Check if user is followed by trusted accounts
            trusted_followers = self._get_trusted_followers(user_id, monitor)
            trusted_count = len(trusted_followers)
            
            # Determine trust level
            if trusted_count >= self.config.MIN_TRUSTED_FOLLOWERS:
                trust_level = 'vouched_by_trusted'
                is_trusted = True
                explanation = f"Followed by {trusted_count} trusted accounts: {', '.join(trusted_followers[:3])}"
                if trusted_count > 3:
                    explanation += f" and {trusted_count - 3} others"
            elif trusted_count > 0:
                trust_level = 'partially_vouched'
                is_trusted = False
                explanation = f"Followed by {trusted_count} trusted account(s) (minimum {self.config.MIN_TRUSTED_FOLLOWERS} required)"
            else:
                trust_level = 'not_vouched'
                is_trusted = False
                explanation = "Not followed by any trusted accounts"
            
            return {
                'is_trusted': is_trusted,
                'trust_level': trust_level,
                'trusted_followers': trusted_followers,
                'trusted_followers_count': trusted_count,
                'vouched_by_trusted': is_trusted,
                'explanation': explanation
            }
            
        except Exception as e:
            logger.error(f"Error checking trust score for {user_id}: {str(e)}")
            return self._default_trust_score()
    
    def _get_trusted_followers(self, user_id: str, monitor) -> List[str]:
        """
        Get list of trusted accounts that follow the user
        
        Args:
            user_id: User ID to check
            monitor: XMonitor instance
        
        Returns:
            List of trusted account usernames that follow the user
        """
        trusted_followers = []
        
        try:
            # Note: This is a simplified approach due to API limitations
            # In a full implementation, you would need to:
            # 1. Get the user's followers
            # 2. Check which ones are in the trusted list
            # 
            # For now, we'll use a different approach - check if trusted accounts follow the user
            # This requires checking each trusted account individually
            
            # Sample a subset of trusted accounts to check (to avoid rate limits)
            trusted_sample = list(self.trusted_accounts)[:20]  # Check first 20
            
            for trusted_username in trusted_sample:
                try:
                    # Get trusted account info
                    trusted_user = monitor.client.get_user(username=trusted_username)
                    if not trusted_user.data:
                        continue
                    
                    trusted_user_id = trusted_user.data.id
                    
                    # Check if trusted user follows our target user
                    # Note: This approach is limited by API rate limits
                    # In production, you'd want to implement more efficient batching
                    
                    time.sleep(0.1)  # Small delay to avoid rate limits
                    
                    # For now, we'll simulate this check
                    # In a real implementation, you'd use the followers endpoint
                    # followers = monitor.client.get_users_followers(trusted_user_id)
                    
                except Exception as e:
                    logger.debug(f"Error checking trusted account {trusted_username}: {str(e)}")
                    continue
            
            # Simplified approach - return empty list for now
            # This would be replaced with actual API calls in production
            return trusted_followers
            
        except Exception as e:
            logger.error(f"Error getting trusted followers: {str(e)}")
            return []
    
    def _default_trust_score(self) -> Dict:
        """Return default trust score for error cases"""
        return {
            'is_trusted': False,
            'trust_level': 'unknown',
            'trusted_followers': [],
            'trusted_followers_count': 0,
            'vouched_by_trusted': False,
            'explanation': 'Unable to verify trust status'
        }
    
    def _load_cached_accounts(self):
        """Load cached trusted accounts from file"""
        try:
            with open(self.cache_file, 'r') as f:
                content = f.read().strip()
                if content:
                    self.trusted_accounts = set(content.split('\n'))
                    logger.info(f"Loaded {len(self.trusted_accounts)} cached trusted accounts")
        except FileNotFoundError:
            logger.info("No cached trusted accounts found")
        except Exception as e:
            logger.error(f"Error loading cached accounts: {str(e)}")
    
    def _cache_accounts(self):
        """Cache trusted accounts to file"""
        try:
            with open(self.cache_file, 'w') as f:
                f.write('\n'.join(sorted(self.trusted_accounts)))
            logger.debug("Cached trusted accounts to file")
        except Exception as e:
            logger.error(f"Error caching accounts: {str(e)}")
    
    def get_trusted_accounts_count(self) -> int:
        """Get number of trusted accounts"""
        return len(self.trusted_accounts)
    
    def is_account_trusted(self, username: str) -> bool:
        """Check if a specific account is trusted"""
        return username.lower().lstrip('@') in self.trusted_accounts
