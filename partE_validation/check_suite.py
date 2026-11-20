"""Run the printed-record checks, and require the README to name each one.

Every relative link in the Markdown files has to resolve inside this
repository. The record has 76. Does not call CalculiX or OpenSees. Does not
write the prints, and does not read the floor page.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
LINK = re.compile(r'\[[^\]]*\]\(([^)]+)\)|src="([^"]+)"|srcset="([^"]+)"')
RELATIVE_LINKS = 76


def relative_links(problems):
    count = 0
    for path in sorted(ROOT.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
            continue
        text = path.read_text(encoding="utf-8")
        for match in LINK.finditer(text):
            raw = next(group for group in match.groups() if group)
            target = raw.split()[0]
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            count += 1
            file_part = target.split("#", 1)[0]
            if not file_part:
                continue
            dest = (path.parent / file_part).resolve()
            try:
                dest.relative_to(ROOT)
            except ValueError:
                problems.append(f"{path.relative_to(ROOT)} link leaves the repository: {target}")
                continue
            if not dest.exists():
                problems.append(f"{path.relative_to(ROOT)} -> {target}")
    if count != RELATIVE_LINKS:
        problems.append(f"{count} relative links, the record has {RELATIVE_LINKS}")


def main():
    problems = []
    relative_links(problems)
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
