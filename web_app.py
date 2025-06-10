#!/usr/bin/env python3
"""
RugguardBot Web Dashboard
Lightweight web interface using built-in Python HTTP server
"""

import os
import json
import threading
import subprocess
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import http.server
import socketserver

# Global server instance
server_instance = None

class RugguardBotServer:
    def __init__(self, port=5000):
        self.port = port
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
                # Try to get recent logs
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

    def get_dashboard_html(self):
        """Generate dashboard HTML"""
        config_ok = self.check_configuration()
        self.update_status()
        db_stats = self.get_database_stats()
        
        status_color = 'green' if self.bot_status == 'Running' else 'red' if self.bot_status == 'Stopped' else 'orange'
        config_color = 'green' if config_ok else 'red'
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>RugguardBot - X Account Analyzer</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .header h1 {{ font-size: 2.5rem; color: #2563eb; margin-bottom: 8px; }}
                .header p {{ font-size: 1.2rem; color: #64748b; }}
                .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .card {{ background: white; padding: 24px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
                .card h3 {{ font-size: 1.1rem; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; }}
                .status-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
                .status-green {{ background: #10b981; }}
                .status-red {{ background: #ef4444; }}
                .status-orange {{ background: #f59e0b; }}
                .status-text {{ font-size: 1.5rem; font-weight: bold; margin-bottom: 16px; }}
                .text-green {{ color: #10b981; }}
                .text-red {{ color: #ef4444; }}
                .text-orange {{ color: #f59e0b; }}
                .btn {{ padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; }}
                .btn-green {{ background: #10b981; color: white; }}
                .btn-red {{ background: #ef4444; color: white; }}
                .btn-blue {{ background: #2563eb; color: white; }}
                .btn:hover {{ opacity: 0.9; }}
                .btn:disabled {{ background: #9ca3af; cursor: not-allowed; }}
                .stats {{ display: flex; flex-direction: column; gap: 8px; }}
                .stat-row {{ display: flex; justify-content: space-between; }}
                .logs {{ background: #f8f9fa; padding: 16px; border-radius: 8px; max-height: 300px; overflow-y: auto; margin-bottom: 16px; }}
                .log-entry {{ font-family: 'Courier New', monospace; font-size: 0.85rem; margin-bottom: 4px; color: #374151; }}
                .how-it-works {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; text-align: center; }}
                .step {{ padding: 20px; }}
                .step-icon {{ font-size: 2rem; margin-bottom: 12px; }}
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
                        <h3>Bot Status <div class="status-dot status-{status_color}"></div></h3>
                        <div class="status-text text-{status_color}">{self.bot_status}</div>
                        <div>
                            {'<button class="btn btn-red" onclick="stopBot()">Stop Bot</button>' if self.bot_status == 'Running' else f'<button class="btn btn-green" onclick="startBot()" {"disabled" if not config_ok else ""}>Start Bot</button>'}
                        </div>
                    </div>

                    <div class="card">
                        <h3>Configuration <div class="status-dot status-{config_color}"></div></h3>
                        <p style="margin-bottom: 8px; color: #64748b;">{self.config_status}</p>
                        {'' if config_ok else '<p style="font-size: 0.8rem; color: #ef4444;">Configure API keys in Replit Secrets</p>'}
                    </div>

                    <div class="card">
                        <h3>Statistics</h3>
                        <div class="stats">
                            <div class="stat-row">
                                <span style="color: #64748b;">Total Analyses:</span>
                                <span><strong>{db_stats['total_analyses']}</strong></span>
                            </div>
                            <div class="stat-row">
                                <span style="color: #64748b;">Recent (24h):</span>
                                <span><strong>{db_stats['recent_analyses']}</strong></span>
                            </div>
                            <div class="stat-row">
                                <span style="color: #64748b;">Trusted Accounts:</span>
                                <span><strong>{db_stats['trusted_accounts']}</strong></span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3>Recent Activity</h3>
                    <div class="logs">
                        {''.join([f'<div class="log-entry">{log}</div>' for log in self.bot_logs]) if self.bot_logs else '<p style="color: #64748b;">No recent activity logs available</p>'}
                    </div>
                    <button class="btn btn-blue" onclick="refreshLogs()">Refresh Logs</button>
                </div>

                <div class="card">
                    <h3>How It Works</h3>
                    <div class="how-it-works">
                        <div class="step">
                            <div class="step-icon">👀</div>
                            <p><strong>Monitors X/Twitter</strong><br>Watches for "riddle me this" replies</p>
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
                async function startBot() {{
                    try {{
                        const response = await fetch('/api/start', {{ method: 'POST' }});
                        const data = await response.json();
                        alert(data.message);
                        if (data.success) {{
                            setTimeout(() => window.location.reload(), 2000);
                        }}
                    }} catch (error) {{
                        alert('Error starting bot: ' + error.message);
                    }}
                }}

                async function stopBot() {{
                    try {{
                        const response = await fetch('/api/stop', {{ method: 'POST' }});
                        const data = await response.json();
                        alert(data.message);
                        if (data.success) {{
                            setTimeout(() => window.location.reload(), 2000);
                        }}
                    }} catch (error) {{
                        alert('Error stopping bot: ' + error.message);
                    }}
                }}

                function refreshLogs() {{
                    window.location.reload();
                }}

                // Auto-refresh every 30 seconds
                setInterval(() => {{
                    fetch('/api/status')
                        .then(response => response.json())
                        .then(data => console.log('Status updated:', data.status))
                        .catch(error => console.error('Status update failed:', error));
                }}, 30000);
            </script>
        </body>
        </html>
        """

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global server_instance
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = server_instance.get_dashboard_html()
            self.wfile.write(html.encode())
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            server_instance.update_status()
            status = {
                'status': server_instance.bot_status,
                'config': server_instance.config_status,
                'logs': server_instance.bot_logs[-10:]
            }
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        global server_instance
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        if self.path == '/api/start':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if server_instance.check_configuration():
                try:
                    result = subprocess.run(['pgrep', '-f', 'main.py'], capture_output=True, text=True)
                    if result.returncode == 0:
                        response = {'message': 'Bot is already running', 'success': True}
                    else:
                        def start_bot():
                            subprocess.Popen(['python', 'main.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        
                        thread = threading.Thread(target=start_bot)
                        thread.daemon = True
                        thread.start()
                        response = {'message': 'Bot startup initiated - check logs for status', 'success': True}
                except Exception as e:
                    response = {'message': f'Error starting bot: {str(e)}', 'success': False}
            else:
                response = {'message': 'Configuration incomplete. Please set API keys in Replit Secrets.', 'success': False}
            
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/stop':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                subprocess.run(['pkill', '-f', 'main.py'], capture_output=True, text=True)
                response = {'message': 'Bot stop signal sent', 'success': True}
            except Exception as e:
                response = {'message': f'Error stopping bot: {str(e)}', 'success': False}
            
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_server():
    global server_instance
    server_instance = RugguardBotServer(port=5000)
    
    # Try different ports if 5000 is in use
    ports_to_try = [5000, 5001, 8000, 8080, 3000]
    
    for port in ports_to_try:
        try:
            with socketserver.TCPServer(("0.0.0.0", port), RequestHandler) as httpd:
                httpd.allow_reuse_address = True
                print(f"🚀 RugguardBot Dashboard running at http://0.0.0.0:{port}")
                print("📝 Configure your X API keys in Replit Secrets to get started")
                httpd.serve_forever()
                break
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"Port {port} is in use, trying next port...")
                continue
            else:
                raise
        except KeyboardInterrupt:
            print("\n👋 RugguardBot Dashboard stopped")
            break
    else:
        print("❌ Could not find an available port to run the server")

if __name__ == "__main__":
    run_server()