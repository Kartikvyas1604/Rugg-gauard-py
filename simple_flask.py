#!/usr/bin/env python3
"""
Simple Flask implementation for RugguardBot
"""

import os
import json
import threading
import time
from datetime import datetime
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

class RugguardBotServer:
    def __init__(self, port=5000):
        self.port = port
        self.bot_status = "Stopped"
        self.bot_logs = []
        self.config_status = "Not Configured"
        self._update_bot_status()
        
    def _update_bot_status(self):
        """Update bot status by checking if the RugguardBot process is running"""
        try:
            import subprocess
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

    def get_dashboard_html(self):
        """Generate dashboard HTML"""
        config_ok = self.check_configuration()
        self._update_bot_status()  # Update status before generating HTML
        
        # Get database stats if available
        db_stats = {}
        try:
            from models import DatabaseManager
            db = DatabaseManager()
            db_stats = db.get_stats()
        except Exception:
            db_stats = {
                'total_analyses': 0,
                'recent_analyses': 0,
                'total_tweets': 0,
                'trusted_accounts': 73
            }
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>RugguardBot - X Account Analyzer</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script>
                tailwind.config = {{
                    theme: {{
                        extend: {{
                            colors: {{
                                'primary': '#3b82f6',
                                'primary-dark': '#1e40af',
                                'secondary': '#64748b',
                                'accent': '#06b6d4',
                                'success': '#10b981',
                                'warning': '#f59e0b',
                                'error': '#ef4444'
                            }},
                            animation: {{
                                'pulse-slow': 'pulse 3s infinite',
                                'bounce-slow': 'bounce 2s infinite'
                            }}
                        }}
                    }}
                }}
            </script>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <style>
                body {{ font-family: 'Inter', sans-serif; }}
                .gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
                .card-shadow {{ box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); }}
                .glass {{ backdrop-filter: blur(16px) saturate(180%); background-color: rgba(255, 255, 255, 0.75); border: 1px solid rgba(209, 213, 219, 0.3); }}
                .status-indicator {{ position: relative; display: inline-block; }}
                .status-indicator::before {{ content: ''; position: absolute; top: 50%; left: -12px; transform: translateY(-50%); width: 8px; height: 8px; border-radius: 50%; }}
                .status-success::before {{ background-color: #10b981; box-shadow: 0 0 6px #10b981; }}
                .status-warning::before {{ background-color: #f59e0b; box-shadow: 0 0 6px #f59e0b; }}
                .status-error::before {{ background-color: #ef4444; box-shadow: 0 0 6px #ef4444; }}
                .terminal {{ background: linear-gradient(145deg, #1a1a1a, #2d2d2d); color: #00ff41; font-family: 'Monaco', 'Menlo', monospace; }}
                .metric-card {{ transition: all 0.3s ease; }}
                .metric-card:hover {{ transform: translateY(-2px); }}
            </style>
        </head>
        <body class="min-h-screen gradient-bg">
            <div class="min-h-screen py-8 px-4">
                <!-- Header -->
                <div class="max-w-6xl mx-auto mb-8">
                    <div class="text-center text-white">
                        <div class="inline-flex items-center justify-center w-20 h-20 bg-white/20 rounded-full mb-4 backdrop-blur-lg">
                            <span class="text-4xl">🛡️</span>
                        </div>
                        <h1 class="text-5xl font-bold mb-2">RugguardBot</h1>
                        <p class="text-xl text-white/80 font-medium">Advanced X Account Trustworthiness Analyzer</p>
                        <div class="w-24 h-1 bg-gradient-to-r from-accent to-primary mx-auto mt-4 rounded-full"></div>
                    </div>
                </div>

                <div class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <!-- Configuration Status -->
                    <div class="lg:col-span-2">
                        <div class="glass rounded-2xl p-6 card-shadow">
                            <div class="flex items-center justify-between mb-4">
                                <h2 class="text-2xl font-bold text-gray-800 flex items-center">
                                    <span class="status-indicator status-{'success' if config_ok else 'error'} pl-4">Configuration Status</span>
                                </h2>
                                <div class="{'bg-success' if config_ok else 'bg-error'} text-white px-3 py-1 rounded-full text-sm font-medium">
                                    {'Ready' if config_ok else 'Setup Required'}
                                </div>
                            </div>
                            <div class="space-y-3">
                                <div class="flex items-center justify-between">
                                    <span class="text-gray-600 font-medium">API Configuration:</span>
                                    <span class="font-semibold text-gray-800">{self.config_status}</span>
                                </div>
                                <div class="{'bg-green-50 border border-green-200 text-green-800' if config_ok else 'bg-red-50 border border-red-200 text-red-800'} p-4 rounded-lg">
                                    {'✅ All X API credentials are properly configured and ready!' if config_ok else '❌ Missing X API credentials - Please configure your Twitter API keys to proceed'}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Bot Status -->
                    <div>
                        <div class="glass rounded-2xl p-6 card-shadow">
                            <h2 class="text-xl font-bold text-gray-800 mb-4 flex items-center">
                                <span class="status-indicator status-{'success' if self.bot_status == 'Running' else 'warning'} pl-4">Bot Status</span>
                            </h2>
                            <div class="space-y-3">
                                <div class="text-center">
                                    <div class="{'bg-success text-white' if self.bot_status == 'Running' else 'bg-warning text-white'} w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-2 {'animate-pulse-slow' if self.bot_status == 'Running' else ''}">
                                        <span class="text-2xl">{'🟢' if self.bot_status == 'Running' else '🟡'}</span>
                                    </div>
                                    <p class="font-bold text-lg text-gray-800">{self.bot_status}</p>
                                    <p class="text-sm text-gray-500">{datetime.now().strftime('%H:%M:%S')}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Statistics Grid -->
                    <div class="lg:col-span-3">
                        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
                            <div class="glass rounded-xl p-4 metric-card">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <p class="text-sm font-medium text-gray-600">Total Analyses</p>
                                        <p class="text-2xl font-bold text-primary">{db_stats.get('total_analyses', 0)}</p>
                                    </div>
                                    <div class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                                        <span class="text-xl">📊</span>
                                    </div>
                                </div>
                            </div>
                            <div class="glass rounded-xl p-4 metric-card">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <p class="text-sm font-medium text-gray-600">Recent (24h)</p>
                                        <p class="text-2xl font-bold text-accent">{db_stats.get('recent_analyses', 0)}</p>
                                    </div>
                                    <div class="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center">
                                        <span class="text-xl">⚡</span>
                                    </div>
                                </div>
                            </div>
                            <div class="glass rounded-xl p-4 metric-card">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <p class="text-sm font-medium text-gray-600">Processed Tweets</p>
                                        <p class="text-2xl font-bold text-success">{db_stats.get('total_tweets', 0)}</p>
                                    </div>
                                    <div class="w-12 h-12 bg-success/10 rounded-lg flex items-center justify-center">
                                        <span class="text-xl">🐦</span>
                                    </div>
                                </div>
                            </div>
                            <div class="glass rounded-xl p-4 metric-card">
                                <div class="flex items-center justify-between">
                                    <div>
                                        <p class="text-sm font-medium text-gray-600">Trusted Accounts</p>
                                        <p class="text-2xl font-bold text-warning">{db_stats.get('trusted_accounts', 73)}</p>
                                    </div>
                                    <div class="w-12 h-12 bg-warning/10 rounded-lg flex items-center justify-center">
                                        <span class="text-xl">🔒</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Controls -->
                    <div class="lg:col-span-2">
                        <div class="glass rounded-2xl p-6 card-shadow">
                            <h2 class="text-xl font-bold text-gray-800 mb-6">Bot Controls</h2>
                            <div class="flex flex-wrap gap-3">
                                <button 
                                    onclick="startBot()" 
                                    {'disabled' if not config_ok else ''}
                                    class="{'bg-gray-400 cursor-not-allowed' if not config_ok else 'bg-success hover:bg-green-600'} text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 shadow-lg">
                                    <span>▶️</span>
                                    <span>{'Configure API Keys First' if not config_ok else 'Start Bot'}</span>
                                </button>
                                <button 
                                    onclick="stopBot()"
                                    class="bg-error hover:bg-red-600 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 shadow-lg">
                                    <span>⏹️</span>
                                    <span>Stop Bot</span>
                                </button>
                                <button 
                                    onclick="refreshStatus()"
                                    class="bg-primary hover:bg-primary-dark text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2 shadow-lg">
                                    <span>🔄</span>
                                    <span>Refresh</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Setup Instructions -->
                    <div>
                        <div class="glass rounded-2xl p-6 card-shadow">
                            <h2 class="text-xl font-bold text-gray-800 mb-4 flex items-center">
                                <span class="text-2xl mr-2">⚙️</span>
                                Setup Guide
                            </h2>
                            <div class="space-y-4">
                                <p class="text-gray-600">Get your X API credentials to start analyzing accounts:</p>
                                <div class="bg-blue-50 border-l-4 border-primary p-4 rounded-lg">
                                    <ol class="space-y-2 text-sm">
                                        <li class="flex items-start">
                                            <span class="bg-primary text-white w-5 h-5 rounded-full flex items-center justify-center text-xs mr-2 mt-0.5 font-bold">1</span>
                                            <span>Visit <a href="https://developer.twitter.com" target="_blank" class="text-primary hover:text-primary-dark font-medium underline">Twitter Developer Portal</a></span>
                                        </li>
                                        <li class="flex items-start">
                                            <span class="bg-primary text-white w-5 h-5 rounded-full flex items-center justify-center text-xs mr-2 mt-0.5 font-bold">2</span>
                                            <span>Create an app and generate API keys</span>
                                        </li>
                                        <li class="flex items-start">
                                            <span class="bg-primary text-white w-5 h-5 rounded-full flex items-center justify-center text-xs mr-2 mt-0.5 font-bold">3</span>
                                            <span>Add these secrets to your Replit environment:</span>
                                        </li>
                                    </ol>
                                </div>
                                <div class="grid grid-cols-1 gap-2 text-xs">
                                    <div class="bg-gray-100 rounded p-2 font-mono">X_API_KEY</div>
                                    <div class="bg-gray-100 rounded p-2 font-mono">X_API_SECRET</div>
                                    <div class="bg-gray-100 rounded p-2 font-mono">X_ACCESS_TOKEN</div>
                                    <div class="bg-gray-100 rounded p-2 font-mono">X_ACCESS_TOKEN_SECRET</div>
                                    <div class="bg-gray-100 rounded p-2 font-mono">X_BEARER_TOKEN</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Activity Logs -->
                    <div class="lg:col-span-3">
                        <div class="glass rounded-2xl p-6 card-shadow">
                            <div class="flex items-center justify-between mb-4">
                                <h2 class="text-xl font-bold text-gray-800 flex items-center">
                                    <span class="text-2xl mr-2">📋</span>
                                    Activity Logs
                                </h2>
                                <div class="flex items-center space-x-2 text-sm text-gray-500">
                                    <span class="w-2 h-2 bg-success rounded-full animate-pulse"></span>
                                    <span>Live Feed</span>
                                </div>
                            </div>
                            <div class="terminal rounded-lg p-4 h-64 overflow-y-auto border">
                                <div class="space-y-1 text-sm">
                                    {'<br>'.join(self.bot_logs[-20:]) if self.bot_logs else '<div class="text-center text-green-400 py-8"><div class="text-4xl mb-2">🚀</div><div>Bot logs will appear here once started</div><div class="text-xs mt-2 opacity-70">Configure API keys and start the bot to see real-time activity</div></div>'}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // Show toast notifications instead of alerts
                function showToast(message, type = 'info') {{
                    const toast = document.createElement('div');
                    toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full`;
                    
                    const colors = {{
                        'success': 'bg-green-500 text-white',
                        'error': 'bg-red-500 text-white',
                        'info': 'bg-blue-500 text-white',
                        'warning': 'bg-yellow-500 text-white'
                    }};
                    
                    toast.className += ` ${{colors[type] || colors.info}}`;
                    toast.textContent = message;
                    
                    document.body.appendChild(toast);
                    
                    setTimeout(() => {{
                        toast.style.transform = 'translateX(0)';
                    }}, 100);
                    
                    setTimeout(() => {{
                        toast.style.transform = 'translateX(100%)';
                        setTimeout(() => document.body.removeChild(toast), 300);
                    }}, 3000);
                }}

                function startBot() {{
                    const button = document.querySelector('[onclick="startBot()"]');
                    const originalText = button.innerHTML;
                    button.innerHTML = '<span class="animate-spin">⏳</span> <span>Starting...</span>';
                    button.disabled = true;
                    
                    fetch('/api/start', {{method: 'POST'}})
                        .then(r => r.json())
                        .then(data => {{
                            showToast(data.message, data.success !== false ? 'success' : 'error');
                            setTimeout(refreshStatus, 1000);
                        }})
                        .catch(e => {{
                            showToast('Failed to start bot: ' + e.message, 'error');
                        }})
                        .finally(() => {{
                            button.innerHTML = originalText;
                            button.disabled = false;
                        }});
                }}
                
                function stopBot() {{
                    const button = document.querySelector('[onclick="stopBot()"]');
                    const originalText = button.innerHTML;
                    button.innerHTML = '<span class="animate-spin">⏳</span> <span>Stopping...</span>';
                    button.disabled = true;
                    
                    fetch('/api/stop', {{method: 'POST'}})
                        .then(r => r.json())
                        .then(data => {{
                            showToast(data.message, 'success');
                            setTimeout(refreshStatus, 1000);
                        }})
                        .catch(e => {{
                            showToast('Failed to stop bot: ' + e.message, 'error');
                        }})
                        .finally(() => {{
                            button.innerHTML = originalText;
                            button.disabled = false;
                        }});
                }}
                
                function refreshStatus() {{
                    const button = document.querySelector('[onclick="refreshStatus()"]');
                    const originalText = button.innerHTML;
                    button.innerHTML = '<span class="animate-spin">🔄</span> <span>Refreshing...</span>';
                    
                    setTimeout(() => {{
                        location.reload();
                    }}, 500);
                }}
                
                // Auto-refresh every 30 seconds
                setInterval(() => {{
                    fetch('/api/status')
                        .then(r => r.json())
                        .then(data => {{
                            // Update status indicators without full page reload
                            const statusElements = document.querySelectorAll('[data-status]');
                            statusElements.forEach(el => {{
                                if (el.dataset.status === 'bot') {{
                                    el.textContent = data.status;
                                }}
                            }});
                        }})
                        .catch(() => {{
                            // Silent fail for auto-refresh
                        }});
                }}, 30000);

                // Add smooth transitions and interactions
                document.addEventListener('DOMContentLoaded', function() {{
                    // Add hover effects to metric cards
                    const metricCards = document.querySelectorAll('.metric-card');
                    metricCards.forEach(card => {{
                        card.addEventListener('mouseenter', function() {{
                            this.style.transform = 'translateY(-4px) scale(1.02)';
                        }});
                        card.addEventListener('mouseleave', function() {{
                            this.style.transform = 'translateY(0) scale(1)';
                        }});
                    }});
                }});
            </script>
        </body>
        </html>
        """

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Extract server_instance from kwargs before calling super()
        self.server_instance = kwargs.pop('server_instance', None)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = self.server_instance.get_dashboard_html()
            self.wfile.write(html.encode())
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = {
                'status': self.server_instance.bot_status,
                'config': self.server_instance.config_status,
                'logs': self.server_instance.bot_logs[-10:]
            }
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/start':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if self.server_instance.check_configuration():
                try:
                    # Try to start the bot by checking if it's already running
                    import threading
                    import subprocess
                    
                    # Check if bot is already running
                    result = subprocess.run(['pgrep', '-f', 'main.py'], capture_output=True, text=True)
                    if result.returncode == 0:
                        self.server_instance.bot_status = "Running"
                        response = {'message': 'Bot is already running', 'success': True}
                    else:
                        # Start the bot in background
                        def start_bot_background():
                            try:
                                subprocess.Popen(['python', 'main.py'], 
                                               stdout=subprocess.DEVNULL, 
                                               stderr=subprocess.DEVNULL)
                            except Exception as e:
                                print(f"Error starting bot: {e}")
                        
                        thread = threading.Thread(target=start_bot_background)
                        thread.daemon = True
                        thread.start()
                        
                        self.server_instance.bot_status = "Starting..."
                        response = {'message': 'Bot startup initiated - check logs for status', 'success': True}
                        
                except Exception as e:
                    self.server_instance.bot_status = "Error"
                    response = {'message': f'Failed to start bot: {str(e)}', 'success': False}
            else:
                response = {'message': 'Cannot start - API keys not configured', 'success': False}
            
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/api/stop':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                import subprocess
                # Try to stop the bot process
                result = subprocess.run(['pkill', '-f', 'main.py'], capture_output=True)
                if result.returncode == 0:
                    self.server_instance.bot_status = "Stopped"
                    response = {'message': 'Bot stopped successfully', 'success': True}
                else:
                    self.server_instance.bot_status = "Stopped"
                    response = {'message': 'Bot was not running', 'success': True}
            except Exception as e:
                response = {'message': f'Error stopping bot: {str(e)}', 'success': False}
            
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_server():
    """Start the web server"""
    import socket
    
    # Find an available port
    PORT = 5000
    while PORT < 5010:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', PORT))
                break
        except OSError:
            PORT += 1
    
    server_instance = RugguardBotServer(PORT)
    
    def handler(*args, **kwargs):
        return MyHTTPRequestHandler(*args, server_instance=server_instance, **kwargs)
    
    with socketserver.TCPServer(("0.0.0.0", PORT), handler) as httpd:
        print(f"🚀 RugguardBot Dashboard running at http://0.0.0.0:{PORT}")
        print("📝 Configure your X API keys in Replit Secrets to get started")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()