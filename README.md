# copy-n-launch-xlsx

<p align="center">
  <img src="https://github.com/City-of-Memphis-Wastewater/copy-n-launch-xlsx/blob/dev/assets/copy-n-launch-xlsx_gui_v0.2.10.png" width="100%" alt="Screenshot of the GUI">
</p>

The best way to launch this application is to install the CLI using `pipx`, or to download a release binary.

```
pipx install copy-n-launch-xlsx
cnlx gui
```

**Download binaries here:** [Releases](https://github.com/City-of-Memphis-Wastewater/copy-n-launch-xlsx/releases/)

[![Socket Badge](https://badge.socket.dev/pypi/package/copy-n-launch-xlsx)](https://socket.dev/pypi/package/copy-n-launch-xlsx)

---

## Purpose

This program: 

- Copies a blank spreadsheet file.

- Renames it, with the date in the filename.

- Moves the new renamed file to a target folder

In this way, the stable file can be updated in a centralized way. 
Users can safely launch new daily data entry sheets, without needing to choose a file to launch directly.

---

## Blurb

Spreadsheet templating isn't a new problem.

It's been solved many different ways over the years.

This is just one more solution—built around a very simple workflow that's now used every day by operators at my wastewater treatment plant.

Bring your own spreadsheet.

Click one button.

Get today's dated copy, ready for data entry.

The code is open source (thank you, Memphis taxpayers), and it's been tested on macOS, Windows 11, WSL, and Termux on Android.

---

## XLSX Best Practices

Sheets should use Name Manager variable names and possibly tables, for reference and data aggregation.
Variable names allow the cell locations to be adjusted and not referenced.

---

## How To

- Place a spreadsheet named daily_blank.xlsx in the filepath: ~/.copy-n-launch-xlsx/blank/

Blank template:

~/.copy-n-launch-xlsx/blank/daily_blank.xlsx

- Hit the single green button.

Automatically generated files:

~/.copy-n-launch-xlsx/filled/daily-YYYY-MM-DD.xlsx

---

## Helptree

See the `copy-n-launch-xlsx` Typer CLI structure.

```
cnlx helptree
```

<p align="center">
  <img src="https://raw.githubusercontent.com/City-of-Memphis-Wastewater/copy-n-launch-xlsx/main/assets/copy-n-launch-xlsx_v0.2.10_helptree.svg" width="100%" alt="Screenshot of the CLI helptree">
</p>
`helptree` is a utility function for Typer CLIs, imported from the `typer-helptree` library.

- GitHub: https://github.com/City-of-Memphis-Wastewater/typer-helptree
- PyPI: https://pypi.org/project/typer-helptree/

---

## Operator Data Entry Instructions Specific to Maxson Wastewater Treatment Facility

Generally this workflow applies to any context, with the exception of: 

- Color meanings
- "Print" page
- The XLIMS reference

Or any other information relating to a specific spreadsheet design.

The specific spreadsheet in question is maintained separately in the Maxson SharePoint. 

<p align="center">
  <img src="https://github.com/City-of-Memphis-Wastewater/copy-n-launch-xlsx/blob/dev/assets/copy-n-launch-xlsx_workflow-instructions_v0.2.12.png" width="100%" alt="Instruction PNG">
</p>

```instructions
Instructions:
At midnight, ensure that the file is saved, and then print the "Print" page.
Only the "Print" page is necessary, for data entry into XLIMS.
One printed and saved, close the file.
Do NOT delete any data from the file.

A brand new, dated spreadsheet will be used for the next day.
At the start of each day, after midnight, hit the green button in the Copy-N-Launch-XLSX interface.
This will generate the fresh daily sheet, automatically dated and empty, ready for data entry.
At any time, you can save and close the current spreadsheet.
Hitting the green Launch Daily Spreadsheet button will reopen it, or generate a new one as necessary.
```

---

## Source code

**Source code:** [Repository](https://github.com/City-of-Memphis-Wastewater/copy-n-launch-xlsx/)
