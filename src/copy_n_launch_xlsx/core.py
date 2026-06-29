# src/copy_n_launch_xlsx/core.py

from __future__ import annotations
from datetime import date
from pathlib import Path
import shutil
import subprocess
import sys
import openpyxl
import logging
import pyhabitat

logger = logging.getLogger(__name__)

from .paths import BLANK_DAILY_XLSX, get_target_copy_dir

FILENAME_FORMAT = "daily_%Y-%m-%d.xlsx"

def build_filename(day: date | None = None) -> str:
    if day is None:
        day = date.today()
    filename = day.strftime(FILENAME_FORMAT)
    return filename



def copy_then_rename_and_move_then_try_launch() -> Path:
    target_dir = get_target_copy_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    destination = target_dir / build_filename()
    logger.debug(f"{destination=}")
    # Check if the file is already there
    if destination.exists():
        logger.info(f"Daily file already exists at {destination}. Skipping copy. Launching existing file.")
        pyhabitat.launch_file(destination)
        return destination
    
    # Open/save if you later want to update named ranges,
    # dates, workbook properties, etc.
    wb = openpyxl.load_workbook(destination)

    # future edits go here
    set_date_in_spreadsheet(wb)

    wb.save(destination)

    pyhabitat.launch_file(destination)

    return destination


def set_date_in_spreadsheet(wb):
    from datetime import date
    from openpyxl.workbook.defined_names import DefinedName

    # --- Adjust the Data: Update Named Range "date" ---
    today_str = date.today().strftime("%m/%d/%Y")

    if "date" in wb.defined_names:
        defn = wb.defined_names["date"]
        
        # Scenario A: The name maps to a cell reference, e.g., Sheet1!$A$1
        # we parse out the sheet and coordinate to write directly to the cell
        if "!" in defn.value:
            sheet_name, cell_coord = defn.value.split("!")
            sheet_name = sheet_name.strip("'")      # Strip potential quote wrapping
            cell_coord = cell_coord.replace("$", "") # Strip absolute reference anchoring
            
            if sheet_name in wb.sheetnames:
                wb[sheet_name][cell_coord] = today_str
                logger.debug(f"Updated cell {defn.value} assigned to named range 'date' to {today_str}.")
        
        # Scenario B: The name is a direct global formula/string variable expression, e.g., ="06/29/2026"
        else:
            defn.value = f'="{today_str}"'
            logger.debug(f"Updated global value expression for named range 'date' to {today_str}.")
    else:
        # Fallback: Create it as a global value string expression if it doesn't exist yet
        new_name = DefinedName("date", attr_text=f'="{today_str}"')
        wb.defined_names.add(new_name)
        logger.debug(f"Named range 'date' not found. Created global expression variable set to {today_str}.")

    # --------------------------------------------------
