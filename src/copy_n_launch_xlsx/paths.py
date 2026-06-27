# src/copy-n-launch-xlsx/paths.py
from __future__ import annotations
from os import path
from pathlib import Path

from .context import config_mngr
APP_DIR = Path.home() / ".copy-n-launch-xlsx"
BLANK_DAILY_XLSX = Path.cwd() / "assets" / "xlsx" / "daily_blank.xlsx"

DEFAULT_FILLED_SHEETS_DIR = APP_DIR / "filled_daily"

#from dworshak_prompt import Obtain
from dworshak_config import DworshakConfig

config_mngr = DworshakConfig(path= APP_DIR)
#obtain_mngr = Obtain(config_path = APP_DIR)

# can i use a string to effectively define the dir where i want the copied and renamed sheet to land?
# it can be in
def pull_in_configured_path_or_use_default():
    filled_sheets_dir = config_mngr.set(service="copy-n-launch",item="filled-sheet-dir",value="",overwrite=False) # creates file and defauly value if it doesn't exist
    filled_sheets_dir = config_mngr.get(service="copy-n-launch",item="filled-sheet-dir") # allows retrieval of edited value

    filled_sheets_path = DEFAULT_FILLED_SHEETS_DIR 
    if filled_sheets_dir == "":
        pass
    else:    
        filled_sheets_path_hypothetical = Path(filled_sheets_dir).expanduser().resolve()
        if filled_sheets_path_hypothetical is not in the form of a a full local path:
            filled_sheets_path = filled_sheets_path_hypothetical
        else:
            pass

    return filled_sheets_path

def ensure_filled_sheet_dir(filled_sheets_path):
    filled_sheet_canary_file = filled_sheets_path / ".canary"
    filled_sheet_canary_file.parent.mkdir(parents=True, exist_ok=True)

filled_sheets_path = pull_in_configured_path_or_use_default()
ensure_filled_sheet_dir(filled_sheets_path)

