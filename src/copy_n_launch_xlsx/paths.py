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
LOGO_FILENAME_PNG = "max-green_1024x1024.png"
LOGO_FILENAME_ICNS = "max-green.icns"
LOGO_FILENAME_ICO = "max-green_256x256.ico"
DEFAULT_FILLED_SHEETS_DIR = APP_DIR / "filled_daily"
REPO_URL = "https://github.com/City-of-Memphis-Wastewater/copy-n-launch-xlsx"


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


def get_png_icon() -> Path:
    return Path(get_icon_path(LOGO_FILENAME_PNG))

def get_ico_icon() -> Path:
    return Path(get_icon_path(LOGO_FILENAME_ICO))

def get_icns_icon() -> Path:
    return Path(get_icon_path(LOGO_FILENAME_ICNS))

# can i use a string to effectively define the dir where i want the copied and renamed sheet to land?
# it can be in
def pull_in_configured_path_or_use_default():
    config_mngr.set(service="copy-n-launch",item="filled-sheet-dir",value="",overwrite=False) # creates file and defauly value if it doesn't exist
    configured_str = config_mngr.get(service="copy-n-launch",item="filled-sheet-dir") # allows retrieval of edited value

    # If the user left it blank, or it's purely whitespace, use the default path
    if not configured_str or not str(configured_str).strip():
        return DEFAULT_FILLED_SHEETS_DIR

    # Expand variables like ~ and resolve to absolute clean paths safely
    resolved_path = Path(str(configured_str).strip()).expanduser().resolve()
    
    # Validation fallback if they typed a relative path or junk string
    if not resolved_path.is_absolute():
        logger.warning(f"Configured path '{configured_str}' is invalid or relative. Using default.")
        return DEFAULT_FILLED_SHEETS_DIR

    return resolved_path
def ensure_filled_sheet_dir(filled_sheets_path):
    filled_sheet_canary_file = filled_sheets_path / ".canary"
    filled_sheet_canary_file.parent.mkdir(parents=True, exist_ok=True)

def get_target_copy_dir():
    filled_sheets_dir = pull_in_configured_path_or_use_default()
    ensure_filled_sheet_dir(filled_sheets_dir)
    return filled_sheets_dir



