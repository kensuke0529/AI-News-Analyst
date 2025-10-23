#!/usr/bin/env python3
"""
Railway Frontend Server
======================
This script serves the frontend files.
"""
import os
import sys
import http.server
import socketserver
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Serve frontend files"""
    # Get frontend directory
    frontend_dir = Path(__file__).parent.parent / "frontend"
    
    if not frontend_dir.exists():
        print("Frontend directory not found, skipping frontend server")
        return
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Set up server
    port = int(os.environ.get("FRONTEND_PORT", "3000"))
    
    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
    
    try:
        with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
            print(f"Serving frontend at http://0.0.0.0:{port}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Frontend server error: {e}")

if __name__ == "__main__":
    main()
