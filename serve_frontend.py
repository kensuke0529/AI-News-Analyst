#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend files
"""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Change to the frontend directory
frontend_dir = Path(__file__).parent / "frontend"
os.chdir(frontend_dir)

PORT = 3000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Frontend server running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop the server")
        
        # Automatically open the browser
        webbrowser.open(f'http://localhost:{PORT}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
