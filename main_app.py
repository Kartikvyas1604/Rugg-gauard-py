#!/usr/bin/env python3
"""
RUGGUARD X Bot - Main Flask Application
WSGI-compatible Flask app for production deployment
"""

import os
import json
import threading
import subprocess
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "rugguard-bot-secret-key")

class RugguardBotManager:
    def __init__(self):
        self.bot_status = "Stopped"
        self.bot_logs = []
        self.config_status = "Not Configured"
        self.update_status()
        
    def update_status(self):
        """Update bot status by checking if the RugguardBot process is running"""
        try:
            result = subprocess.run(['pgrep', '-f', 'main.py'], capture_output=True, text=True)
            if result.returncode == 0:
                self.bot_status = "Running"
                try:
                    with open('rugguard_bot.log', 'r') as f:
                        lines = f.readlines()
                        self.bot_logs = [line.strip() for line in lines[-20:] if line.strip()]
                except FileNotFoundError:
                    self.bot_logs = ["Bot is running but log file not found"]
            else:
                self.bot_status = "Stopped"
                self.bot_logs = []
        except Exception as e:
            self.bot_status = "Unknown"
            self.bot_logs = [f"Error checking status: {str(e)}"]
        
    def check_configuration(self):
        """Check if API keys are configured"""
        required_keys = [
            'X_API_KEY', 'X_API_SECRET', 'X_ACCESS_TOKEN', 
            'X_ACCESS_TOKEN_SECRET', 'X_BEARER_TOKEN'
        ]
        
        missing_keys = []
        for key in required_keys:
            if not os.environ.get(key):
                missing_keys.append(key)
        
        if missing_keys:
            self.config_status = f"Missing: {', '.join(missing_keys)}"
            return False
        else:
            self.config_status = "Configured"
            return True

    def get_database_stats(self):
        """Get database statistics"""
        try:
            from models import DatabaseManager
            db = DatabaseManager()
            return db.get_stats()
        except Exception:
            return {
                'total_analyses': 0,
                'recent_analyses': 0,
                'total_tweets': 0,
                'trusted_accounts': 73
            }

# Initialize bot manager
bot_manager = RugguardBotManager()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    bot_manager.update_status()
    config_ok = bot_manager.check_configuration()
    db_stats = bot_manager.get_database_stats()
    
    status_color = 'green' if bot_manager.bot_status == 'Running' else 'red' if bot_manager.bot_status == 'Stopped' else 'orange'
    config_color = 'green' if config_ok else 'red'
    
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RugguardBot - X Account Analyzer</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 40px; }
            .header h1 { font-size: 2.5rem; color: #2563eb; margin-bottom: 8px; }
            .header p { font-size: 1.2rem; color: #64748b; }
            .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .card { background: white; padding: 24px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .card h3 { font-size: 1.1rem; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; }
            .status-dot { width: 12px; height: 12px; border-radius: 50%; }
            .status-green { background: #10b981; }
            .status-red { background: #ef4444; }
            .status-orange { background: #f59e0b; }
            .status-text { font-size: 1.5rem; font-weight: bold; margin-bottom: 16px; }
            .text-green { color: #10b981; }
            .text-red { color: #ef4444; }
            .text-orange { color: #f59e0b; }
            .btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; }
            .btn-green { background: #10b981; color: white; }
            .btn-red { background: #ef4444; color: white; }
            .btn-blue { background: #2563eb; color: white; }
            .btn:hover { opacity: 0.9; }
            .btn:disabled { background: #9ca3af; cursor: not-allowed; }
            .stats { display: flex; flex-direction: column; gap: 8px; }
            .stat-row { display: flex; justify-content: space-between; }
            .logs { background: #f8f9fa; padding: 16px; border-radius: 8px; max-height: 300px; overflow-y: auto; margin-bottom: 16px; }
            .log-entry { font-family: 'Courier New', monospace; font-size: 0.85rem; margin-bottom: 4px; color: #374151; }
            .how-it-works { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; text-align: center; }
            .step { padding: 20px; }
            .step-icon { font-size: 2rem; margin-bottom: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ RugguardBot</h1>
                <p>X Account Trustworthiness Analyzer</p>
            </div>

            <div class="cards">
                <div class="card">
                    <h3>Bot Status <div class="status-dot status-{{ status_color }}"></div></h3>
                    <div class="status-text text-{{ status_color }}">{{ bot_status }}</div>
                    <div>
                        {% if bot_status == 'Running' %}
                            <button class="btn btn-red" onclick="stopBot()">Stop Bot</button>
                        {% else %}
                            <button class="btn btn-green" onclick="startBot()" {% if not config_ok %}disabled{% endif %}>Start Bot</button>
                        {% endif %}
                    </div>
                </div>

                <div class="card">
                    <h3>Configuration <div class="status-dot status-{{ config_color }}"></div></h3>
                    <p style="margin-bottom: 8px; color: #64748b;">{{ config_status }}</p>
                    {% if not config_ok %}
                        <p style="font-size: 0.8rem; color: #ef4444;">Configure API keys in Replit Secrets</p>
                    {% endif %}
                </div>

                <div class="card">
                    <h3>Statistics</h3>
                    <div class="stats">
                        <div class="stat-row">
                            <span style="color: #64748b;">Total Analyses:</span>
                            <span><strong>{{ db_stats.total_analyses }}</strong></span>
                        </div>
                        <div class="stat-row">
                            <span style="color: #64748b;">Recent (24h):</span>
                            <span><strong>{{ db_stats.recent_analyses }}</strong></span>
                        </div>
                        <div class="stat-row">
                            <span style="color: #64748b;">Trusted Accounts:</span>
                            <span><strong>{{ db_stats.trusted_accounts }}</strong></span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>Recent Activity</h3>
                <div class="logs">
                    {% if bot_logs %}
                        {% for log in bot_logs %}
                            <div class="log-entry">{{ log }}</div>
                        {% endfor %}
                    {% else %}
                        <p style="color: #64748b;">No recent activity logs available</p>
                    {% endif %}
                </div>
                <button class="btn btn-blue" onclick="refreshLogs()">Refresh Logs</button>
            </div>

            <div class="card">
                <h3>How It Works</h3>
                <div class="how-it-works">
                    <div class="step">
                        <div class="step-icon">👀</div>
                        <p><strong>Monitors X/Twitter</strong><br>Watches for "@projectruggaurd riddle me this" replies</p>
                    </div>
                    <div class="step">
                        <div class="step-icon">🔍</div>
                        <p><strong>Analyzes Accounts</strong><br>Checks trustworthiness indicators</p>
                    </div>
                    <div class="step">
                        <div class="step-icon">📊</div>
                        <p><strong>Provides Report</strong><br>Replies with detailed analysis</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function startBot() {
                try {
                    const response = await fetch('/api/start', { method: 'POST' });
                    const data = await response.json();
                    alert(data.message);
                    if (data.success) {
                        setTimeout(() => window.location.reload(), 2000);
                    }
                } catch (error) {
                    alert('Error starting bot: ' + error.message);
                }
            }

            async function stopBot() {
                try {
                    const response = await fetch('/api/stop', { method: 'POST' });
                    const data = await response.json();
                    alert(data.message);
                    if (data.success) {
                        setTimeout(() => window.location.reload(), 2000);
                    }
                } catch (error) {
                    alert('Error stopping bot: ' + error.message);
                }
            }

            function refreshLogs() {
                window.location.reload();
            }

            setInterval(() => {
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => console.log('Status updated:', data.status))
                    .catch(error => console.error('Status update failed:', error));
            }, 30000);
        </script>
    </body>
    </html>
    """
    
    return render_template_string(template, 
                                bot_status=bot_manager.bot_status,
                                config_ok=config_ok,
                                config_status=bot_manager.config_status,
                                bot_logs=bot_manager.bot_logs,
                                db_stats=db_stats,
                                status_color=status_color,
                                config_color=config_color)

@app.route('/api/status')
def api_status():
    """API endpoint for status updates"""
    bot_manager.update_status()
    return jsonify({
        'status': bot_manager.bot_status,
        'config': bot_manager.config_status,
        'logs': bot_manager.bot_logs[-10:]
    })

@app.route('/api/start', methods=['POST'])
def api_start():
    """Start the bot"""
    if not bot_manager.check_configuration():
        return jsonify({
            'message': 'Configuration incomplete. Please set API keys in Replit Secrets.',
            'success': False
        })
    
    try:
        result = subprocess.run(['pgrep', '-f', 'main.py'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({
                'message': 'Bot is already running',
                'success': True
            })
        
        def start_bot():
            subprocess.Popen(['python', 'main.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        thread = threading.Thread(target=start_bot)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Bot startup initiated - check logs for status',
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'message': f'Error starting bot: {str(e)}',
            'success': False
        })

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop the bot"""
    try:
        subprocess.run(['pkill', '-f', 'main.py'], capture_output=True, text=True)
        return jsonify({
            'message': 'Bot stop signal sent',
            'success': True
        })
    except Exception as e:
        return jsonify({
            'message': f'Error stopping bot: {str(e)}',
            'success': False
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)