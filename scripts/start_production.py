#!/usr/bin/env python3
"""
Production startup script for AI News Analyst
Handles both backend and frontend services with proper process management
"""

import subprocess
import sys
import os
import signal
import time
from pathlib import Path

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print("\n🛑 Shutting down AI News Analyst...")
    sys.exit(0)

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting backend server...")
    return subprocess.Popen([
        sys.executable, "run_backend.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def start_frontend():
    """Start the frontend server"""
    print("🌐 Starting frontend server...")
    return subprocess.Popen([
        sys.executable, "serve_frontend.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main():
    """Main startup function"""
    print("=" * 60)
    print("🤖 AI News Analyst - Production Startup")
    print("=" * 60)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check if we're in the right directory
    if not Path("backend/main.py").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("   Please set it in your .env file or environment")
        sys.exit(1)
    
    print("✅ Environment check passed")
    
    # Start services
    backend_process = None
    frontend_process = None
    
    try:
        # Start backend
        backend_process = subprocess.Popen([
            sys.executable, "scripts/run_backend.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)  # Give backend time to start
        
        # Start frontend
        frontend_process = subprocess.Popen([
            sys.executable, "scripts/serve_frontend.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)  # Give frontend time to start
        
        print("\n🎉 AI News Analyst is running!")
        print("📱 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8002")
        print("📊 API Status: http://localhost:8002/api/status")
        print("\n💡 Token Limit: 5000 tokens per day")
        print("🔄 Press Ctrl+C to stop")
        print("=" * 60)
        
        # Keep the main process alive
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process died unexpectedly")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend process died unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up processes
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        print("✅ Shutdown complete")

if __name__ == "__main__":
    main()
