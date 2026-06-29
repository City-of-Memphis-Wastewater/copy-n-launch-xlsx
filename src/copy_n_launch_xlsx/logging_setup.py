# src/copy_n_launch_xlsx/logging_setup.py
from __future__ import annotations
import logging
import sys
import traceback
from .paths import LOG_FILE_PATH

logger = logging.getLogger("copy_n_launch_xlsx")

def configure_logging_for_application(debug: bool = False, verbose: bool = False) -> None:
    """Configures the application-level logger using standard built-in formats."""
    
    # Priority: debug > verbose (info) > default (WARNING)
    if debug:
        level = logging.DEBUG
        fmt = "%(levelname)-7s %(message)s"  # Left-aligned level name for neatness
    elif verbose:
        level = logging.INFO
        fmt = "%(message)s"
    else:
        level = logging.WARNING
        fmt = "%(levelname)s: %(message)s"

    logger.setLevel(level)

    # Prevent leakage to root logger
    logger.propagate = False

    # Safely clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Route strictly to stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)

    logger.debug("Debug logging enabled for app.")
    logger.info("Verbose logging enabled for app.")


def log_traceback(logger_instance):
    if logger_instance.level <= logging.DEBUG:
        traceback.print_exc(file=sys.stderr)


# --- Error Logging (File Bound) ---

def setup_error_logger():
    """Configures a basic file logger that records warnings and errors."""
    error_log = logging.getLogger('copy_n_launch_xlsx_error_logger')
    error_log.setLevel(logging.WARNING)
    error_log.propagate = False 

    # Check if file handler already exists to prevent duplicates
    if not any(isinstance(h, logging.FileHandler) for h in error_log.handlers):
        file_handler = logging.FileHandler(LOG_FILE_PATH, mode='a')
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        error_log.addHandler(file_handler)

    return error_log

error_logger = setup_error_logger()