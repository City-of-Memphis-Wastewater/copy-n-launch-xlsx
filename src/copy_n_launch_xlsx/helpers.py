# src/copy_n_launch_xlsx/helpers.py
from __future__ import annotations
from pathlib import Path
import pyhabitat
import os

def get_friendly_path(full_path: str) -> str:
    """

    Returns an absolute path on Windows, or a tilde-shortened path on Linux.
    Ensures system calls don't break on Windows while maintaining Linux UX.

    """
    try:
        p = Path(full_path).resolve()
    except Exception:
        # If resolution fails (e.g. permission error), use the raw path
        p = Path(full_path)

    if pyhabitat.on_windows():
        return str(p)

    # Linux/macOS: Try to provide the friendly tilde shortcut
    try:
        home = Path.home()
        # is_relative_to was added in Python 3.9
        if hasattr(p, "is_relative_to") and p.is_relative_to(home):
            return f"~{os.sep}{p.relative_to(home)}"
        elif str(p).startswith(str(home)):
            # Fallback for Python < 3.9
            return str(p).replace(str(home), "~", 1)
    except Exception:
        # If home directory can't be determined, return absolute path
        pass

    return str(p)

