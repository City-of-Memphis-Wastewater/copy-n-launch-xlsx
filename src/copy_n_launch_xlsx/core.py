# src/copy_n_launch_xlsx/core.py

from __future__ import annotations
from datetime import date
from pathlib import Path
import shutil
import openpyxl
import logging
from typing import Optional
from dataclasses import dataclass
import pyhabitat
from datetime import date
from openpyxl.workbook.defined_name import DefinedName
import sys

logger = logging.getLogger(__name__)

from .paths import BLANK_DAILY_XLSX, get_target_copy_dir

FILENAME_FORMAT = "daily_%Y-%m-%d.xlsx"

@dataclass
class CopyResult:
    destination: Optional[str] = None
    is_new: Optional[bool] = False

    @property
    def status_message(self) -> str:
        """Statuses."""
        return {
            True: "File copied.",
            False: "File exists.",
            None: "Exited."
        }.get(self.is_new, "Error.")

    def __bool__(self):
        return self.destination is not None
    

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
        #return destination
        return CopyResult(destination=destination,is_new=False)
    if BLANK_DAILY_XLSX.exists():
        shutil.copy2(BLANK_DAILY_XLSX, destination)
    else:
        print(f"Please put daily_blank.xlsx in the expected place: {BLANK_DAILY_XLSX}")
        sys.exit(0)
    # Open/save if you later want to update named ranges,
    # dates, workbook properties, etc.
    wb = openpyxl.load_workbook(destination)

    # future edits go here
    set_date_in_spreadsheet(wb)
    wb.save(destination)
    

    pyhabitat.launch_file(destination)

    #return destination
    return CopyResult(destination=destination,is_new=True)


def set_date_in_spreadsheet(wb):

    today_str = date.today().strftime("%m/%d/%Y")

    if "date" in wb.defined_names:
        defn = wb.defined_names["date"]
        
        # Use whichever field contains the reference string
        raw_value = defn.value if defn.value else defn.attr_text
        
        if raw_value and "!" in raw_value:
            sheet_name, cell_coord = raw_value.split("!")
            sheet_name = sheet_name.strip("'")      # Strip potential quote wrapping
            cell_coord = cell_coord.replace("$", "") # Strip absolute reference anchoring
            
            if sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                ws[cell_coord] = today_str
                logger.debug(f"Successfully updated cell {cell_coord} on sheet '{sheet_name}' to {today_str}.")
        else:
            defn.value = f'="{today_str}"'
            logger.debug(f"Updated global value expression for named range 'date' to {today_str}.")
    else:
        new_name = DefinedName("date", attr_text=f'="{today_str}"')
        wb.defined_names.add(new_name)
        logger.debug(f"Named range 'date' not found. Created global expression variable set to {today_str}.")
