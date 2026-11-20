"""Run the printed-record checks, and require the README to name each one.

Does not call CalculiX or OpenSees. Does not write the prints, and does not
read the floor page.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent


def main():
    problems = []
    scripts = sorted(path for path in HERE.glob("check_*.py") if path.name != Path(__file__).name)
    if len(scripts) != 10:
        problems.append(f"{len(scripts)} record checks, the README lists 10")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) if not env.get("PYTHONPATH") else str(ROOT) + os.pathsep + env["PYTHONPATH"]
    for path in scripts:
        rel = f"partE_validation/{path.name}"
        if rel not in readme:
            problems.append(f"README does not name {rel}")
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            tail = (result.stdout or result.stderr).strip().splitlines()
            problems.append(f"{path.name} failed: {tail[-1] if tail else 'no output'}")
    if problems:
        print("\n".join(problems))
        return 1
    print("SUITE_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
