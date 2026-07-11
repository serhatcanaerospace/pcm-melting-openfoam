#!/usr/bin/env python3
"""Repository structure checks for a planned public OpenFOAM case repo."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SECRET_RE = re.compile(r"(/home/dstech|DSTECH_WORKS|claude\.ai/code/artifact|/gpfs/home|dsth\d+|alogin|etur\d+)")


def public_files() -> list[Path]:
    ignored = {".git", "__pycache__", ".pytest_cache", ".venv"}
    ignored_files = {Path("tools/quality_check.py"), Path(".github/workflows/quality.yml")}
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and not any(part in ignored for part in path.parts)
        and path.relative_to(ROOT) not in ignored_files
    ]


def main() -> int:
    missing: list[str] = []
    leaks: list[str] = []

    for rel in ("README.md", "ROADMAP.md", "CASE_INDEX.md", "docs/literature.md"):
        if not (ROOT / rel).exists():
            missing.append(rel)

    case_dirs = sorted((ROOT / "cases").iterdir()) if (ROOT / "cases").exists() else []
    if not case_dirs:
        missing.append("cases/<case>")

    for case_dir in case_dirs:
        if not case_dir.is_dir():
            continue
        for rel in (
            "README.md",
            "USAGE.md",
            "reports/case_report.md",
            "figures/geometry.png",
            "figures/result_summary.png",
            "geometry/model.stl",
        ):
            if not (case_dir / rel).exists():
                missing.append(str(case_dir.relative_to(ROOT) / rel))

    for path in public_files():
        if path.suffix.lower() not in {".md", ".py", ".yml", ".yaml", ".json", ".txt", ".sh"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if SECRET_RE.search(text):
            leaks.append(str(path.relative_to(ROOT)))

    if missing:
        print("Missing expected public files:")
        for item in missing:
            print(f"  - {item}")
    if leaks:
        print("Potential local/private path leaks:")
        for item in leaks:
            print(f"  - {item}")
    if missing or leaks:
        return 1
    print(f"{ROOT.name} public structure OK ({len(case_dirs)} cases).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
