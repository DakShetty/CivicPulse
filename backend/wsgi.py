import sys
from pathlib import Path

# Ensure project root is in sys.path when running as a script
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
