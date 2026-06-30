# src/copy-n-launch-xlsx/paths.py
from __future__ import annotations
from pathlib import Path
from importlib.resources import files
from dworshak_config import DworshakConfig
from dworshak_env import DworshakEnv
import logging

APP_NAME = "copy-n-launch-xlsx"
SRC_FOLDER_NAME = "copy_n_launch_xlsx" 
APP_DIR = Path.home() / f".{APP_NAME}"
LOGO_FILENAME_PNG = "max-blue_1024x1024.png"
LOGO_FILENAME_ICO = "max-blue_256x256.ico"
DEFAULT_FILLED_SHEETS_DIR = APP_DIR / "filled_daily"


BLANK_DAILY_XLSX = (
    files("copy_n_launch_xlsx")
    / "data"
    / "xlsx"
    / "daily_blank.xlsx"
)

config_mngr = DworshakConfig(path= APP_DIR / "config.json")
env_mngr = DworshakEnv()

logger = logging.getLogger(__name__)

# --- Configuration ---

try:
    # Use the home directory and append the tool's name
    APP_DIR = Path.home() / f".{APP_NAME}"
except Exception as e:
    logger.debug(f"Falling back to tmp dir: {e}")
    # Fallback if Path.home() fails in certain environments (e.g., some CI runners)
    APP_DIR = Path(f"/tmp/.{APP_NAME}_temp")

# Ensure the directory exists
APP_DIR.mkdir(parents=True, exist_ok=True)
# Define the log file path
LOG_FILE_PATH = APP_DIR / f"{APP_NAME}_errors.log"

def get_icon_path(filename: str) -> Path:
    return files("copy_n_launch_xlsx.data.icons").joinpath(filename)

# can i use a string to effectively define the dir where i want the copied and renamed sheet to land?
# it can be in
def pull_in_configured_path_or_use_default():
    filled_sheets_dir_configured = config_mngr.set(service="copy-n-launch",item="filled-sheet-dir",value="",overwrite=False) # creates file and defauly value if it doesn't exist
    filled_sheets_dir_configured = config_mngr.get(service="copy-n-launch",item="filled-sheet-dir") # allows retrieval of edited value

    filled_sheets_dir = DEFAULT_FILLED_SHEETS_DIR 
    if not filled_sheets_dir_configured == "":  
        filled_sheets_path_hypothetical = Path(filled_sheets_dir_configured).expanduser().resolve()
        if filled_sheets_path_hypothetical.is_absolute(): # is in the form of a a full local path:
            filled_sheets_dir = filled_sheets_path_hypothetical

    return filled_sheets_dir

def pull_in_env_path_or_use_default():
    filled_sheets_dir_configured = env_mngr.set("TARGETCOPYDIR",value="",overwrite=False) # creates file and defauly value if it doesn't exist
    filled_sheets_dir_configured = env_mngr.get("TARGETCOPYDIR") # allows retrieval of edited value

    filled_sheets_dir = DEFAULT_FILLED_SHEETS_DIR 
    if not filled_sheets_dir_configured == "":  
        filled_sheets_path_hypothetical = Path(filled_sheets_dir_configured).expanduser().resolve()
        if filled_sheets_path_hypothetical.is_absolute(): # is in the form of a a full local path:
            filled_sheets_dir = filled_sheets_path_hypothetical

    return filled_sheets_dir

def ensure_filled_sheet_dir(filled_sheets_path):
    filled_sheet_canary_file = filled_sheets_path / ".canary"
    filled_sheet_canary_file.parent.mkdir(parents=True, exist_ok=True)

def get_target_copy_dir():
    filled_sheets_dir = pull_in_configured_path_or_use_default()
    #filled_sheets_dir = pull_in_env_path_or_use_default()
    ensure_filled_sheet_dir(filled_sheets_dir)
    return filled_sheets_dir



