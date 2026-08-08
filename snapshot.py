# This is snapshot utility which creates a zip archive of a project directory,
# excluding certain files and directories.
# It can be run from the command line with various options for specifying
# the project path, output directory, dry run mode, verbosity,
# and compression level. The utility also generates metadata about
# the snapshot in a JSON file within the zip archive.
# Snapshot is named as <project_name>ddMonYYHHMMSS.zip,
# where ddMonYYHHMMSS is the timestamp of when the snapshot was created. This is
#!/usr/bin/env python3
#!/usr/bin/env python3

# Snapshot is named as <project_name>ddMonYYHHMMSS.zip,
# where ddMonYYHHMMSS is the timestamp when the snapshot was created.
#
# Snapshots are stored outside the project directory in the location
# configured by SNAPSHOT_DIR.
"""
Portable Project Snapshot Utility v2.0

Usage:
    python snapshot.py
    python snapshot.py <project_path>
    python snapshot.py --dry-run
    python snapshot.py --verbose
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

VERSION = "2.0"

# ==========================================================
# Snapshot Configuration
# ==========================================================

SNAPSHOT_DIR = Path(
    r"C:\Users\rahul\Documents\AI Trainings\MyProjects\Project Snapshots\RagOps_Snapshots"
)

EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage",
    "snapshots",
}
EXCLUDED_FILES = {".env", "Thumbs.db", ".DS_Store"}

TECH_MARKERS = {
    "Python": ["pyproject.toml", "requirements.txt", "setup.py"],
    "Node.js": ["package.json"],
    "Docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
    "GitHub Actions": [".github"],
}


def should_skip(p: Path) -> bool:
    if p.is_dir():
        return p.name in EXCLUDED_DIRS
    if p.name in EXCLUDED_FILES or p.name.startswith(".env."):
        return True
    return p.suffix.lower() in {".pyc", ".pyo", ".pyd", ".log"}


def scan(root):
    files = []
    folders = 0
    skipped = 0
    size = 0
    for cur, dirs, names in os.walk(root):
        cp = Path(cur)
        keep = []
        for d in dirs:
            dp = cp / d
            if should_skip(dp):
                skipped += 1
            else:
                keep.append(d)
                folders += 1
        dirs[:] = keep
        for n in names:
            fp = cp / n
            if should_skip(fp):
                skipped += 1
                continue
            files.append(fp)
            try:
                size += fp.stat().st_size
            except OSError:
                pass
    return files, folders, skipped, size


def tree(root):
    lines = [root.name]

    def walk(path, prefix=""):
        entries = [
            e
            for e in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            if not should_skip(e)
        ]
        for i, e in enumerate(entries):
            c = "└── " if i == len(entries) - 1 else "├── "
            lines.append(prefix + c + e.name)
            if e.is_dir():
                walk(e, prefix + ("    " if i == len(entries) - 1 else "│   "))

    walk(root)
    return "\n".join(lines)


def detect(root):
    found = []
    for tech, markers in TECH_MARKERS.items():
        for m in markers:
            if (root / m).exists():
                found.append(tech)
                break
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    if not root.is_dir():
        sys.exit("Invalid project.")
    files, folders, skipped, size = scan(root)
    out = SNAPSHOT_DIR
    created = not out.exists()
    out.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%d%b%Y%H%M%S")
    zip_path = out / f"{root.name}_{ts}.zip"
    print(f"Project : {root.name}")
    print(f"Location: {root}")
    print(
        "Created snapshots folder." if created else "Using existing snapshots folder."
    )
    print(f"Files: {len(files)}  Skipped: {skipped}")
    if args.dry_run:
        return
    start = time.time()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        manifest = []
        for f in files:
            rel = f.relative_to(root)
            z.write(f, rel)
            st = f.stat()
            manifest.append(
                [str(rel), st.st_size, datetime.fromtimestamp(st.st_mtime).isoformat()]
            )
            if args.verbose:
                print(rel)
        meta = {
            "project": root.name,
            "created": datetime.now().isoformat(),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "files": len(files),
            "folders": folders,
            "size_mb": round(size / 1024 / 1024, 2),
            "version": VERSION,
        }
        z.writestr("snapshot-info.json", json.dumps(meta, indent=2))
        z.writestr("project-tree.txt", tree(root))
        import io

        sio = io.StringIO()
        w = csv.writer(sio)
        w.writerow(["Path", "Size", "Modified"])
        w.writerows(manifest)
        z.writestr("file-manifest.csv", sio.getvalue())
        ai = f"""# AI Context

Project: {root.name}

Technologies Detected:
{chr(10).join("- " + t for t in detect(root)) or "- Unknown"}

Statistics
- Files: {len(files)}
- Folders: {folders}
- Size (MB): {round(size / 1024 / 1024, 2)}

Top-Level Items:
{chr(10).join("- " + p.name for p in sorted(root.iterdir()) if not should_skip(p))}
"""
        z.writestr("AI_CONTEXT.md", ai)
    print(f"\nSnapshot created:\n{zip_path}")
    print(f"Completed in {time.time() - start:.2f}s")

    env_file = root / ".env"

    if env_file.exists():
        env_backup = out / f".env_{ts}"
        env_backup.write_bytes(env_file.read_bytes())
        print(f".env backup created:\n{env_backup}")

        recover = out / f"RECOVER_PROJECT_{ts}.md"

    recover.write_text(
        f"""# Project Recovery

    Project
    -------
    {root.name}

    Snapshot
    --------
    {zip_path.name}

    Python Version:
    <detected version>

    Platform:
    <detected platform>

    Snapshot Created:
    <timestamp>

    Recovery Steps
    --------------

    1. Extract the zip archive.

    2. Create virtual environment

    python -m venv .venv

    3. Activate environment

    Windows

    .venv\\Scripts\\activate

    4. Install packages

    pip install -r requirements.txt

    5. Run database migrations

    alembic upgrade head

    6. Start backend

    run_backend.bat

    7. Open Swagger

    http://localhost:8002/docs

    8. Restore .env

    Copy

    .env_{ts}

    to

    .env

    9. Verify

    - Database connection
    - Upload sample document
    - Health endpoint
    """,
        encoding="utf-8",
    )

    print(f"Recovery guide created:\n{recover}")


if __name__ == "__main__":
    main()
