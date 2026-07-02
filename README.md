# copy-n-launch-xlsx

```
pip install copy-n-launch-xlsx
```

---

## Purpose:

This program: 

    - Copies a blank spreadsheet file.

    - Renames it, with the date in the filename.

    - Moves the new renamed file to a target folder

In this way, the stable file can be updated in a centralized way. 
Users can safely launch new daily data entry sheets, without needing to choose a file to launch directly.

---

## Blurb

A new twist on one of the classic data entry problems: Spreadsheet templating.

Still relevant in 2026? Apparently, because this app is now in daily use by the operators at my wastewater treatment plant. 

And now, the code is open source as well (thank you Memphis taxpayers). 

BYOS (bring your own spreadsheet).

One button. A new dated copy everyday. A simple solution for a simple problem.

Tested on macOS, WSL, Windows11, and Termux on Android.

---

## XLSX Best Practices

Sheets should use Name Manager variable names and possibly tables, for later reference and data aggregation.
Variable names allow the cell locations to be adjusted and not referenced.

---

## How To:

- Place a spreadsheet named daily_blank.xlsx in the filepath: ~/.copy-n-launch-xlsx/blank/

Blank template:

~/.copy-n-launch-xlsx/blank/daily_blank.xlsx

Generated files:

~/.copy-n-launch-xlsx/filled/daily-YYYY-MM-DD.xlsx

---

## Helptree

See the `copy-n-launch-xlsx` Typer CLI structure.

```
cnlx helptree
```

<p align="center">
  <img src="https://raw.githubusercontent.com/City-of-Memphis-Wastewater/copy-n-launch-xlsx/main/assets/copy-n-launch-xlsx_v0.2.9_helptree.svg" width="100%" alt="Screenshot of the CLI helptree">
</p>
`helptree` is a utility function for Typer CLIs, imported from the `typer-helptree` library.

- GitHub: https://github.com/City-of-Memphis-Wastewater/typer-helptree
- PyPI: https://pypi.org/project/typer-helptree/

---
