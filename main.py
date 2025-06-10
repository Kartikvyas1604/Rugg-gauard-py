#!/usr/bin/env python3
"""
RUGGUARD X Bot - Main Entry Point
Entry point that works with both direct execution and gunicorn
"""

import os
import sys

# Check if we're being run by gunicorn
if 'gunicorn' in os.environ.get('SERVER_SOFTWARE', ''):
    # Import the WSGI application for gunicorn
    from simple_main import application as app
else:
    # Regular bot execution
    import time
    import logging
    from datetime import datetime
    from dotenv import load_dotenv

    from bot.monitor import XMonitor
    from bot.analyzer import AccountAnalyzer
    from bot.trusted_accounts import TrustedAccountsManager
    from bot.report_generator import ReportGenerator
    from config import Config
    from models import DatabaseManager

    # Load environment variables
    load_dotenv()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('rugguard_bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)

    class RugguardBot:
        """Main bot class that coordinates all components"""
        
        def __init__(self):
            """Initialize the bot with all necessary components"""
            self.config = Config()
            self.db = DatabaseManager()
            self.monitor = XMonitor(self.config)
            self.analyzer = AccountAnalyzer(self.config)
            self.trusted_accounts = TrustedAccountsManager(self.config)
            self.report_generator = ReportGenerator(self.config)
            
            logger.info("RugguardBot initialized successfully")
        
        def process_trigger(self, trigger_tweet_id, original_tweet_id, original_author_id):
            """
            Process a detected trigger phrase
            
            Args:
                trigger_tweet_id: ID of the tweet containing "@projectruggaurd riddle me this"
                original_tweet_id: ID of the original tweet being replied to
                original_author_id: User ID of the original tweet author
            """
            try:
                logger.info(f"Processing trigger for original author: {original_author_id}")
                
                # Analyze the original tweet author
                analysis_result = self.analyzer.analyze_account(original_author_id)
                if not analysis_result:
                    logger.error(f"Failed to analyze account: {original_author_id}")
                    return False
                
                # Check trusted accounts
                trust_score = self.trusted_accounts.check_trust_score(original_author_id)
                
                # Generate report
                report = self.report_generator.generate_report(
                    analysis_result, 
                    trust_score, 
                    original_author_id
                )
                
                # Post reply
                success = self.monitor.post_reply(trigger_tweet_id, report)
                
                if success:
                    # Save to database
                    self.db.save_user_analysis(
                        original_author_id,
                        analysis_result.get('username', 'unknown'),
                        analysis_result,
                        trust_score.get('trusted_followers_count', 0),
                        analysis_result.get('risk_score', 50)
                    )
                    
                    # Mark tweet as processed
                    self.db.mark_tweet_processed(
                        trigger_tweet_id,
                        original_tweet_id,
                        original_author_id,
                        reply_posted=True
                    )
                    
                    logger.info(f"Successfully processed trigger and posted reply")
                    return True
                else:
                    logger.error("Failed to post reply")
                    return False
                    
            except Exception as e:
                logger.error(f"Error processing trigger: {str(e)}")
                return False
        
        def run(self):
            """Main bot loop"""
            logger.info("Starting RugguardBot...")
            
            # Update trusted accounts list
            self.trusted_accounts.update_trusted_list()
            
            while True:
                try:
                    # Check for triggers
                    triggers = self.monitor.check_for_triggers()
                    
                    for trigger in triggers:
                        # Skip if already processed
                        if self.db.is_tweet_processed(trigger['trigger_tweet_id']):
                            continue
                        
                        # Process the trigger
                        self.process_trigger(
                            trigger['trigger_tweet_id'],
                            trigger['original_tweet_id'],
                            trigger['original_author_id']
                        )
                    
                    # Wait before next check
                    time.sleep(self.config.POLLING_INTERVAL)
                    
                except KeyboardInterrupt:
                    logger.info("Bot stopped by user")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error in main loop: {str(e)}")
                    time.sleep(60)  # Wait longer on errors

    def main():
        """Main function"""
        try:
            # Validate configuration
            config = Config()
            if not config.validate():
                logger.error("Configuration validation failed. Please check your environment variables.")
                sys.exit(1)
            
            # Initialize and run bot
            bot = RugguardBot()
            bot.run()
            
        except Exception as e:
            logger.error(f"Fatal error: {str(e)}")
            sys.exit(1)

    if __name__ == "__main__":
        main()

# For gunicorn compatibility when imported as a module
try:
    from simple_main import app
except ImportError:
    app = None