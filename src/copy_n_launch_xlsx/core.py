# src/copy_n_launch_xlsx/core.py

from __future__ import annotations
from datetime import date
from pathlib import Path
import shutil
import subprocess
import sys

import openpyxl

from .paths import BLANK_DAILY_XLSX, get_target_copy_dir


def build_filename(day: date | None = None) -> str:
    if day is None:
        day = date.today()

    return f"daily_{day:%Y-%m-%d}.xlsx"


def launch_file(path: Path) -> None:
    if sys.platform.startswith("win"):
        import os
        os.startfile(path)

    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)

    else:
        subprocess.run(["xdg-open", str(path)], check=False)


def copy_then_rename_and_move_then_try_launch() -> Path:
    target_dir = get_target_copy_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    destination = target_dir / build_filename()

    shutil.copy2(BLANK_DAILY_XLSX, destination)

    # Open/save if you later want to update named ranges,
    # dates, workbook properties, etc.
    wb = openpyxl.load_workbook(destination)

    #
    # future edits go here
    #

    wb.save(destination)

    launch_file(destination)

    return destination


