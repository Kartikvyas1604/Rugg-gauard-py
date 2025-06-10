#!/usr/bin/env python3
"""
WSGI application entry point for the RugguardBot
Compatible with gunicorn and other WSGI servers
"""

import os
import sys
import subprocess
import json
from datetime import datetime

# Simple WSGI application class
class RugguardBotWSGI:
    def __init__(self):
        self.routes = {
            '/': self.dashboard,
            '/api/status': self.api_status,
            '/api/start': self.api_start,
            '/api/stop': self.api_stop,
        }
    
    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        
        if path in self.routes:
            return self.routes[path](environ, start_response)
        else:
            return self.not_found(environ, start_response)
    
    def dashboard(self, environ, start_response):
        status = '200 OK'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        
        # Check bot status
        bot_status = self.check_bot_status()
        config_status = self.check_configuration()
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>RugguardBot - X Account Analyzer</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .header h1 {{ color: #2563eb; margin-bottom: 10px; }}
                .card {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .status {{ font-size: 1.2em; font-weight: bold; padding: 10px; border-radius: 4px; }}
                .status.running {{ background: #dcfce7; color: #166534; }}
                .status.stopped {{ background: #fef2f2; color: #dc2626; }}
                .btn {{ padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }}
                .btn-success {{ background: #10b981; color: white; }}
                .btn-danger {{ background: #ef4444; color: white; }}
                .btn:hover {{ opacity: 0.9; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ RugguardBot</h1>
                    <p>X Account Trustworthiness Analyzer</p>
                </div>
                
                <div class="card">
                    <h3>Bot Status</h3>
                    <div class="status {bot_status.lower()}">{bot_status}</div>
                    <p>Configuration: {config_status}</p>
                    <button class="btn btn-success" onclick="startBot()">Start Bot</button>
                    <button class="btn btn-danger" onclick="stopBot()">Stop Bot</button>
                </div>
                
                <div class="card">
                    <h3>How It Works</h3>
                    <ol>
                        <li>Monitors X for "@projectruggaurd riddle me this" replies</li>
                        <li>Analyzes the original tweet author's trustworthiness</li>
                        <li>Posts detailed analysis report as a reply</li>
                        <li>Cross-references with trusted accounts list</li>
                    </ol>
                </div>
                
                <div class="card">
                    <h3>Configuration</h3>
                    <p>Ensure these environment variables are set in Replit Secrets:</p>
                    <ul>
                        <li>X_API_KEY</li>
                        <li>X_API_SECRET</li>
                        <li>X_ACCESS_TOKEN</li>
                        <li>X_ACCESS_TOKEN_SECRET</li>
                        <li>X_BEARER_TOKEN</li>
                    </ul>
                </div>
            </div>
            
            <script>
                async function startBot() {{
                    try {{
                        const response = await fetch('/api/start', {{ method: 'POST' }});
                        const data = await response.json();
                        alert(data.message);
                        if (data.success) setTimeout(() => location.reload(), 2000);
                    }} catch (error) {{
                        alert('Error: ' + error.message);
                    }}
                }}
                
                async function stopBot() {{
                    try {{
                        const response = await fetch('/api/stop', {{ method: 'POST' }});
                        const data = await response.json();
                        alert(data.message);
                        if (data.success) setTimeout(() => location.reload(), 2000);
                    }} catch (error) {{
                        alert('Error: ' + error.message);
                    }}
                }}
            </script>
        </body>
        </html>
        """
        return [html.encode('utf-8')]
    
    def api_status(self, environ, start_response):
        status = '200 OK'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        
        bot_status = self.check_bot_status()
        config_status = self.check_configuration()
        
        response = {
            'status': bot_status,
            'config': config_status,
            'timestamp': datetime.now().isoformat()
        }
        return [json.dumps(response).encode('utf-8')]
    
    def api_start(self, environ, start_response):
        if environ.get('REQUEST_METHOD') != 'POST':
            return self.method_not_allowed(environ, start_response)
        
        status = '200 OK'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        
        try:
            # Check if bot is already running
            result = subprocess.run(['pgrep', '-f', 'main.py'], capture_output=True, text=True)
            if result.returncode == 0:
                response = {'message': 'Bot is already running', 'success': True}
            else:
                # Start the bot
                subprocess.Popen(['python', 'main.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                response = {'message': 'Bot startup initiated', 'success': True}
        except Exception as e:
            response = {'message': f'Error starting bot: {str(e)}', 'success': False}
        
        return [json.dumps(response).encode('utf-8')]
    
    def api_stop(self, environ, start_response):
        if environ.get('REQUEST_METHOD') != 'POST':
            return self.method_not_allowed(environ, start_response)
        
        status = '200 OK'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        
        try:
            subprocess.run(['pkill', '-f', 'main.py'], capture_output=True, text=True)
            response = {'message': 'Bot stop signal sent', 'success': True}
        except Exception as e:
            response = {'message': f'Error stopping bot: {str(e)}', 'success': False}
        
        return [json.dumps(response).encode('utf-8')]
    
    def not_found(self, environ, start_response):
        status = '404 Not Found'
        headers = [('Content-Type', 'text/html')]
        start_response(status, headers)
        return [b'<h1>404 Not Found</h1>']
    
    def method_not_allowed(self, environ, start_response):
        status = '405 Method Not Allowed'
        headers = [('Content-Type', 'text/html')]
        start_response(status, headers)
        return [b'<h1>405 Method Not Allowed</h1>']
    
    def check_bot_status(self):
        try:
            result = subprocess.run(['pgrep', '-f', 'main.py'], capture_output=True, text=True)
            return "Running" if result.returncode == 0 else "Stopped"
        except:
            return "Unknown"
    
    def check_configuration(self):
        required_keys = ['X_API_KEY', 'X_API_SECRET', 'X_ACCESS_TOKEN', 'X_ACCESS_TOKEN_SECRET', 'X_BEARER_TOKEN']
        missing = [key for key in required_keys if not os.environ.get(key)]
        return "Complete" if not missing else f"Missing: {{', '.join(missing)}}"

# Create the WSGI application instance
app = RugguardBotWSGI()

# For gunicorn compatibility
application = app

if __name__ == "__main__":
    # For direct execution, start a simple HTTP server
    from wsgiref.simple_server import make_server
    with make_server('0.0.0.0', 5000, app) as httpd:
        print("RugguardBot Dashboard running at http://0.0.0.0:5000")
        httpd.serve_forever()