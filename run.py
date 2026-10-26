import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"\n=======================================================")
    print(f"  CivicPulse Backend API Server")
    print(f"  Serving at: http://{host}:{port}")
    print(f"  API Docs / Health: http://{host}:{port}/api/v1/health")
    print(f"=======================================================\n")
    app.run(host=host, port=port, debug=True)
