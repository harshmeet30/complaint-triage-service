"""Single verification entry point, used locally and by CI.

    python scripts/verify.py

Runs lint, format check and tests. Add further gates (eval harness) to STEPS as they are built.
Exits non-zero on the first failure.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ENV = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}

STEPS: list[tuple[str, list[str]]] = [
    ("lint", [sys.executable, "-m", "ruff", "check", "."]),
    ("tests", [sys.executable, "-m", "pytest", "-q"]),
    ("eval", [sys.executable, "-m", "triage.evaluate"]),
]


def main() -> int:
    for name, cmd in STEPS:
        print(f"\n=== {name}: {' '.join(cmd[2:])} ===", flush=True)
        if subprocess.run(cmd, env=ENV).returncode != 0:
            print(f"\nVERIFY FAILED at step: {name}")
            return 1
    print("\nVERIFY PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
