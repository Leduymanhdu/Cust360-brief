"""
Run script for Customer 360 Backend API server.
"""
import sys
import os

# Ensure the backend directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"=================================================")
    print(f" Customer 360 Backend API Server")
    print(f" Running at: http://127.0.0.1:{port}")
    print(f" Health check: http://127.0.0.1:{port}/api/health")
    print(f"=================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
