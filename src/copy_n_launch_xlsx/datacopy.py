#!/usr/bin/env python3 
# src/copy_n_launch_xlsx/datacopy.py
from __future__ import annotations
import shutil
import sys
from pathlib import Path
import importlib.resources as resources

from copy_n_launch_xlsx.paths import SRC_FOLDER_NAME

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# --- COPY README FILE TO PACKAGE DATA ---
def ensure_package_readme(source_root_path: Path, package_data_path: Path):
    """Copies the root README.md file into the expected package data path."""
    source = source_root_path / "README.md"
    destination = package_data_path / "src" / SRC_FOLDER_NAME / "data" / "README.md"

    if not source.exists():
        print(f"FATAL: Root README file not found at {source}!", file=sys.stderr)
        sys.exit(1)

    print(f"Ensuring package README is copied to: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True) # Ensure data dir exists
    shutil.copy2(source, destination) # copy2 preserves metadata


def ensure_data_files_for_build():
    print(f"PROJECT_ROOT = {PROJECT_ROOT}")
    ensure_package_readme(PROJECT_ROOT, PROJECT_ROOT)


def get_data_root() -> Path:
    """
    Returns the path to the 'data' bundled directory.
    Works for both source code and installed package.
    """
    try:
        # Python ≥3.9: use importlib.resources.files
        return resources.files(SRC_FOLDER_NAME) / "data"
    except Exception:
        # Fallback: assume running from source
        return Path(__file__).resolve().parent / "data"

if __name__ == "__main__":
    ensure_data_files_for_build()
