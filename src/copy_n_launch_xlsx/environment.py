# src/copy_n_launch_xlsx/environment.py
from __future__ import annotations
from functools import cache
import pyhabitat
import os

@cache
def is_in_dev_environment():
    if pyhabitat.is_in_git_repo(os.path.dirname(current_file_path)):
        return True
    else:
        return False
