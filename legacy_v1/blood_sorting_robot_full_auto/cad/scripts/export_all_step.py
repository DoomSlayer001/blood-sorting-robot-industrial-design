from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

for script in [
    "generate_custom_parts.py",
    "generate_fallback_standard_parts.py",
    "build_step_assembly.py",
]:
    subprocess.run([sys.executable, str(HERE / script)], check=True)
