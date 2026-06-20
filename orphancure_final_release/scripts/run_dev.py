"""Dev runner script — start the Streamlit app."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(ROOT / "app" / "main.py"),
         "--server.headless", "true"],
        cwd=str(ROOT),
    )


if __name__ == "__main__":
    main()
