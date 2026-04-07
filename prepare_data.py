"""
Launcher only: adds the repo root to ``sys.path`` and runs ``src.cli.prepare_data.main``.

Run from the repository root::

    python prepare_data.py

Equivalent::

    python -m src.cli.prepare_data
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.cli.prepare_data import main

if __name__ == "__main__":
    main()
