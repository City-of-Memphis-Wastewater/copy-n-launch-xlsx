# src/copy_n_launch_xlsx/external_web_launch.py
from __future__ import annotations
from .context import SERVICE
from .paths import config_mngr

def launch_configured_website(service:str|None=None,item:str|None=None)->str:
    if service is None:
        service = SERVICE

    config_mngr.set(service=SERVICE,item="filled-sheet-dir",value="",overwrite=False) # creates file and defauly value if it doesn't exist
    url = config_mngr.get(service="copy-n-launch",item="filled-sheet-dir") # allows retrieval of edited value

    # If the user left it blank, or it's purely whitespace, use the default path
    if not url or not str(url).strip():
        return None
    return url
