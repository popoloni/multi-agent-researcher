#!/usr/bin/env python3
"""
Simple HTTP server that serves React build files with proper routing support
"""

import http.server
import socketserver
import os
import mimetypes
from urllib.parse import urlparse

class ReactHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='build', **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_GET(self):
        # Parse the URL
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Remove leading slash
        if path.startswith('/'):
            path = path[1:]
        
        # If no path or path doesn't exist, serve index.html (for React routing)
        if not path or not os.path.exists(os.path.join('build', path)):
            # Check if it's a static file request
            if path.startswith('static/') or path in ['favicon.ico', 'manifest.json']:
                # Let the parent handle static files
                super().do_GET()
                return
            else:
                # Serve index.html for React routes
                self.path = '/index.html'
        
        super().do_GET()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    PORT = 12002
    
    with socketserver.TCPServer(("", PORT), ReactHandler) as httpd:
        print(f"Serving React app on port {PORT}")
        print(f"Access at: http://localhost:{PORT}")
        httpd.serve_forever()