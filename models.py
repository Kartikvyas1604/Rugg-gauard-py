"""
Database Models for RugguardBot
"""

import os
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading

class DatabaseManager:
    """SQLite database manager for RugguardBot"""
    
    def __init__(self, db_path: str = "rugguard_bot.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    username TEXT,
                    analysis_data TEXT NOT NULL,
                    trust_score REAL,
                    risk_score REAL,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, analyzed_at)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processed_tweets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tweet_id TEXT UNIQUE NOT NULL,
                    original_tweet_id TEXT,
                    original_author_id TEXT,
                    trigger_user_id TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reply_posted BOOLEAN DEFAULT FALSE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trusted_accounts_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    module TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON user_analyses(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tweet_id ON processed_tweets(tweet_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON trusted_accounts_cache(username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_log_level ON bot_logs(level)')
            
            conn.commit()
            conn.close()
    
    def save_user_analysis(self, user_id: str, username: str, analysis_data: Dict, 
                          trust_score: float = 0.0, risk_score: float = 0.0) -> bool:
        """Save user analysis to database"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO user_analyses 
                    (user_id, username, analysis_data, trust_score, risk_score)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, username, json.dumps(analysis_data), trust_score, risk_score))
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"Error saving user analysis: {e}")
            return False
    
    def get_user_analysis(self, user_id: str, max_age_hours: int = 24) -> Optional[Dict]:
        """Get recent user analysis from database"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
                cursor.execute('''
                    SELECT analysis_data, trust_score, risk_score, analyzed_at
                    FROM user_analyses 
                    WHERE user_id = ? AND analyzed_at > ?
                    ORDER BY analyzed_at DESC LIMIT 1
                ''', (user_id, cutoff_time))
                
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    return {
                        'analysis_data': json.loads(result[0]),
                        'trust_score': result[1],
                        'risk_score': result[2],
                        'analyzed_at': result[3]
                    }
                return None
        except Exception as e:
            print(f"Error getting user analysis: {e}")
            return None
    
    def mark_tweet_processed(self, tweet_id: str, original_tweet_id: Optional[str] = None,
                           original_author_id: Optional[str] = None, trigger_user_id: Optional[str] = None,
                           reply_posted: bool = False) -> bool:
        """Mark tweet as processed"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO processed_tweets 
                    (tweet_id, original_tweet_id, original_author_id, trigger_user_id, reply_posted)
                    VALUES (?, ?, ?, ?, ?)
                ''', (tweet_id, original_tweet_id or '', original_author_id or '', trigger_user_id or '', reply_posted))
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"Error marking tweet as processed: {e}")
            return False
    
    def is_tweet_processed(self, tweet_id: str) -> bool:
        """Check if tweet has been processed"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT 1 FROM processed_tweets WHERE tweet_id = ?', (tweet_id,))
                result = cursor.fetchone()
                conn.close()
                
                return result is not None
        except Exception as e:
            print(f"Error checking if tweet processed: {e}")
            return False
    
    def cache_trusted_accounts(self, accounts: List[str]) -> bool:
        """Cache trusted accounts list"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Clear old cache
                cursor.execute('DELETE FROM trusted_accounts_cache')
                
                # Insert new accounts
                for username in accounts:
                    cursor.execute(
                        'INSERT INTO trusted_accounts_cache (username) VALUES (?)',
                        (username.strip(),)
                    )
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"Error caching trusted accounts: {e}")
            return False
    
    def get_cached_trusted_accounts(self) -> List[str]:
        """Get cached trusted accounts"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT username FROM trusted_accounts_cache')
                results = cursor.fetchall()
                conn.close()
                
                return [row[0] for row in results]
        except Exception as e:
            print(f"Error getting cached trusted accounts: {e}")
            return []
    
    def log_event(self, level: str, message: str, module: Optional[str] = None) -> bool:
        """Log bot events to database"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO bot_logs (level, message, module)
                    VALUES (?, ?, ?)
                ''', (level, message, module))
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"Error logging event: {e}")
            return False
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent bot logs"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT level, message, module, created_at
                    FROM bot_logs 
                    ORDER BY created_at DESC LIMIT ?
                ''', (limit,))
                
                results = cursor.fetchall()
                conn.close()
                
                return [
                    {
                        'level': row[0],
                        'message': row[1],
                        'module': row[2],
                        'created_at': row[3]
                    }
                    for row in results
                ]
        except Exception as e:
            print(f"Error getting recent logs: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get bot statistics"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Total analyses
                cursor.execute('SELECT COUNT(*) FROM user_analyses')
                total_analyses = cursor.fetchone()[0]
                
                # Recent analyses (last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                cursor.execute('SELECT COUNT(*) FROM user_analyses WHERE analyzed_at > ?', (cutoff_time,))
                recent_analyses = cursor.fetchone()[0]
                
                # Total processed tweets
                cursor.execute('SELECT COUNT(*) FROM processed_tweets')
                total_tweets = cursor.fetchone()[0]
                
                # Trusted accounts count
                cursor.execute('SELECT COUNT(*) FROM trusted_accounts_cache')
                trusted_accounts = cursor.fetchone()[0]
                
                conn.close()
                
                return {
                    'total_analyses': total_analyses,
                    'recent_analyses': recent_analyses,
                    'total_tweets': total_tweets,
                    'trusted_accounts': trusted_accounts
                }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                'total_analyses': 0,
                'recent_analyses': 0,
                'total_tweets': 0,
                'trusted_accounts': 0
            }
    
    def cleanup_old_data(self, days: int = 30) -> bool:
        """Clean up old data from database"""
        try:
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cutoff_time = datetime.now() - timedelta(days=days)
                
                # Clean old analyses
                cursor.execute('DELETE FROM user_analyses WHERE analyzed_at < ?', (cutoff_time,))
                
                # Clean old processed tweets
                cursor.execute('DELETE FROM processed_tweets WHERE processed_at < ?', (cutoff_time,))
                
                # Clean old logs
                cursor.execute('DELETE FROM bot_logs WHERE created_at < ?', (cutoff_time,))
                
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
            return False