#!/usr/bin/env python3
"""
Simple HTTP server for the Multi-Agent Researcher UI
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

def serve_ui(port=8081, directory=None):
    """Serve the UI on the specified port"""
    
    if directory is None:
        # Get the directory where this script is located
        directory = Path(__file__).parent
    
    # Change to the UI directory
    os.chdir(directory)
    
    # Create server
    handler = http.server.SimpleHTTPRequestHandler
    
    # Add CORS headers for development
    class CORSRequestHandler(handler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
    
    with socketserver.TCPServer(("", port), CORSRequestHandler) as httpd:
        print(f"🚀 Multi-Agent Researcher UI")
        print(f"📱 Serving at: http://localhost:{port}")
        print(f"📁 Directory: {directory}")
        print(f"🔗 API Backend: http://localhost:12000")
        print(f"📖 API Docs: http://localhost:12000/docs")
        print(f"\n💡 Make sure the API server is running on port 12000")
        print(f"   Start it with: python run.py")
        print(f"\n🛑 Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped")
            sys.exit(0)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Serve Multi-Agent Researcher UI')
    parser.add_argument('--port', '-p', type=int, default=8081, 
                       help='Port to serve on (default: 8081)')
    parser.add_argument('--directory', '-d', type=str, 
                       help='Directory to serve (default: current directory)')
    
    args = parser.parse_args()
    
    serve_ui(args.port, args.directory)