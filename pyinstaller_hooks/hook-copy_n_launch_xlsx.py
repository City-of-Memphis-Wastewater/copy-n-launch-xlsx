# pyinstaller_hooks/hook-copy_n_launch_xlsx.py
from __future__ import annotations
from PyInstaller.utils.hooks import collect_data_files

# This automatically collects all non-python source files inside your package layout
datas = collect_data_files('copy_n_launch_xlsx', include_py_files=False)
