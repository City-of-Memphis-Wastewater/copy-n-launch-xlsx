# src/copy-n-launch-xlsx/paths.py
from __future__ import annotations
from os import path
from pathlib import Path

from .context import config_mngr
APP_DIR = Path.home() / ".copy-n-launch-xlsx"
BLANK_DAILY_XLSX = Path.cwd() / "assets" / "xlsx" / "daily_blank.xlsx"

hardcoded_default_path_filled_sheet_dir = APP_DIR / "filled"

#from dworshak_prompt import Obtain
from dworshak_config import DworshakConfig

config_mngr = DworshakConfig(path= APP_DIR)
#obtain_mngr = Obtain(config_path = APP_DIR)

# can i use a string to effectively define the dir where i want the copied and renamed sheet to land?
# it can be in 
filled_sheets_dir = config_mngr.set(service="copy-n-launch",item="filled-sheet-dir",value="",overwrite=False) # creates file and defauly value if it doesn't exist
filled_sheets_dir = config_mngr.get(service="copy-n-launch",item="filled-sheet-dir") # allows retrieval of edited value

if filled_sheet_dir.resolve() is not a full local path, or if it is an empty string:
    use the hardcoded_default_path_filled_sheet_dir
