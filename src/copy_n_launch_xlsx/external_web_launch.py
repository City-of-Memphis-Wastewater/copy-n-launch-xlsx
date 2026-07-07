# src/copy_n_launch_xlsx/external_web_launch.py
from __future__ import annotations
import webbrowser
import logging

from .context import SERVICE
from .paths import config_mngr

logger = logging.getLogger(__name__)

ITEM_WEB_REF_0 = "web-address-0"

def launch_configured_website(service:str|None=None,item:str|None=None)->str:
    if service is None:
        service = SERVICE
    if item is None:
        item = ITEM_WEB_REF_0
    
    config_mngr.set(service=SERVICE,item=item,value="",overwrite=False) # creates file and defauly value if it doesn't exist
    url = config_mngr.get(service=SERVICE,item=item) # allows retrieval of edited value

    # If the user left it blank, or it's purely whitespace, use the default path
    if not url or not str(url).strip():
        return None
    
    launch_web_url(url)
    return url

def launch_web_url(url: str) -> bool:
    """
    Opens the specified URL in the user's default browser using the standard library.
    
    Returns:
        bool: True if the browser was successfully launched, False otherwise.
    """
    try:
        # new=2 opens the URL in a new tab if possible
        success = webbrowser.open(url, new=2)
        if not success:
            logger.error(f"Failed to open URL via webbrowser module: {url}")
        return success
    except Exception as e:
        logger.error(f"An error occurred while trying to launch the URL: {e}")
        return False