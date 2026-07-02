# copy-n-launch-xlsx

This program: 

    - Copies a blank spreadsheet file.

    - Renames it, with the date in the filename.

    - Moves the new renamed file to a target folder

In this way, the stable file can be updated in a centralized way. 
Users can safely launch new daily data entry sheets, without needing to choose a file to launch directly.


Sheets should use variable names and possibly tables, for later reference and data aggregation.
Variable names allow the cell locations to be adjusted and not referenced.

Any embedded spreadhseet is specific to the Maxson Wastewater Treatment Operator data input.

---

## How To:

- Place a spreadsheet named daily_blank.xlsx in the filepath: ~/.copy-n-launch-xlsx/blank/


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
