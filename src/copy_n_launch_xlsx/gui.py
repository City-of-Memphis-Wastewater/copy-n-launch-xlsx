#!/usr/bin/env python3
# # src/copy_n_launch_xlsx/gui.py
from __future__ import annotations
import pyhabitat
import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from pathlib import Path
from typing import Optional
from importlib.resources import files
import pyhabitat
import ctypes
import sys
import logging
# --- Core Imports ---

from copy_n_launch_xlsx.paths import SRC_FOLDER_NAME
from ._version import get_version, __version__
from .tk_utils import center_window_on_primary
from .core import copy_then_rename_and_move_then_try_launch
from .paths import (
            APP_NAME, 
            get_target_copy_dir, 
            LOGO_FILENAME_PNG,
            LOGO_FILENAME_ICO,
            get_icon_path,
            REPO_URL
            )

logger=logging.getLogger(__name__)

APP_W = 100
APP_H = 50


def apply_windows_taskbar_icon():
    """Forces Windows to explicitly cluster this process under its unique ID signature."""
    if pyhabitat.on_windows():
        try:
            # Format standard: 'CompanyName.ProductName.SubProduct.Version'
            myappid = f"CityOfMemphisWastewater.CopyNLaunch.Xlsx.{__version__}"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            print(f"Successfully bound AppUserModelID: {myappid}")
        except Exception as e:
            print(sys.stderr, f"Failed to bind Windows AppUserModelID signature: {e}")

# RedirectText
class GuiApp:

    # --- Lifecycle & Initialization ---

    def __init__(self, root: tk.Tk):
        self.root = root

        # Do NOT load theme yet.
        # Run the "heavy" initialization first
        self._initialize_vars()

        # NOW load the theme (this takes ~100-300ms)
        self._initialize_forest_theme()

        # Apply the theme
        style = ttk.Style()
        style.configure(".", padding=2)                # global min padding
        style.configure("TFrame", padding=2)
        style.configure("TLabelFrame", padding=(4,2))
        style.configure("TButton", padding=4)
        style.configure("TCheckbutton", padding=2)
        style.configure("TRadiobutton", padding=2)
        style.theme_use("forest-dark")

        self.root.title(f"{APP_NAME} v{get_version()}")  # Short title
        self.root.geometry(f"{APP_W}x{APP_H}")  # Smaller starting size
        self.root.minsize(600, 50)    # Prevent too-small window

        self._set_icon()

        # --- 2. Widget Construction ---
        self._create_widgets()
        #self._initialize_menubar()

    def _initialize_vars(self):
        """Build necessary tk variables."""
        pass

    # --- Theme & Visual Initialization ---
    def _initialize_forest_theme(self):
        theme_dir = files(f"{SRC_FOLDER_NAME}.data.themes.forest")
        self.root.tk.call("source", str(theme_dir / "forest-light.tcl"))
        self.root.tk.call("source", str(theme_dir / "forest-dark.tcl"))

    def _toggle_theme(self):
        style = ttk.Style(self.root) # Explicitly link style to our root
        if style.theme_use() == "forest-light":
            style.theme_use("forest-dark")
        elif style.theme_use() == "forest-dark":
            style.theme_use("forest-light")

    def _set_icon(self):
        try:
            png_path = get_icon_path(LOGO_FILENAME_PNG)
            if png_path.exists():
                self.icon_img = PhotoImage(file=str(png_path))
                self.root.iconphoto(True, self.icon_img)
        except Exception:
            pass
        try:
            ico_path = get_icon_path(LOGO_FILENAME_ICO)
            if ico_path.exists():
                self.root.iconbitmap(str(ico_path))
        except Exception:
            pass


    def _initialize_menubar(self):
        """Builds the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        #tools_menu.add_command(label="Toggle Theme", command=self._toggle_theme)

        #tools_menu.add_separator()
        #tools_menu.add_command(label="Readme", command=self._show_readme)

    def _show_readme(self):
        """Placeholder for the missing readme method."""
        messagebox.showinfo("Readme", "Copy 'n Launch XLSX utility.")

    # --- UI Component Building ---

    def _magic_button(self):
        return None# self._show_system_explorer_gui()
    
    def _about_button(self):
        messagebox.showinfo(
            "About",
            f"URL: \n\n{REPO_URL} \n\nFor help, please see Clayton Bennett or Keith Presson."
        )
    def _create_widgets(self):
        """Compact layout with reduced padding."""

        # --- Control Frame (Top) ---
        control_frame = ttk.Frame(self.root, padding=(4, 2, 4, 2))
        control_frame.pack(fill='x', pady=(2, 2))

        self.btn_open_browser_to_files = ttk.Button(control_frame, text="About", command=lambda: self._about_button(), width=12) # Magic Button
        self.btn_open_browser_to_files.grid(row=1, column=2, columnspan=2, pady=6, sticky='ew', padx=(0, 3))

        # === Row 3: Action Buttons ===
        run_analysis_btn = ttk.Button(control_frame, text="▶ Launch Daily Spreadsheet", command=self._launch_sheet, style='Accent.TButton', width=16) #
        run_analysis_btn.grid(row=1, column=0, columnspan=2, pady=6, sticky='ew', padx=(0, 3))

        # Grid configuration
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)

    def _launch_sheet(self):
        try:
            result = copy_then_rename_and_move_then_try_launch()
            destination = result.destination

            if result.is_new:
                logger.debug(f"Created\n{destination}\n")
                messagebox.showinfo(
                    "Success",
                    f"New file created\n\n{destination}"
                )
            elif not result.is_new:
                logger.debug(f"File exists\n{destination}\n")
                messagebox.showinfo(
                    "File exists",
                    f"File exists\n\n{destination}"
                )
            else:
                logger.debug(f"Edge case\n{destination}\n")
                messagebox.showinfo(
                    "Edge case",
                    f"Edge case\n\n{destination}"
                )
        except FileExistsError as e:
            messagebox.showwarning(
                "Already Exists",
                f"Today's spreadsheet already exists.\n\n{e}",
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e),
            )

    def _show_system_explorer_gui(self) -> None:
        """
        Opens the system file explorer to the directory containing
        the exported files, with GUI error handling.
        """
        try:
            target_dir = get_target_copy_dir()
            pyhabitat.show_system_explorer(path = target_dir)
        except Exception as e:
            # The GUI catches the error to show a user-friendly popup
            messagebox.showerror("Error", f"Could not open system explorer: {e}")

def start_gui(time_auto_close: int = 0):

    apply_windows_taskbar_icon()

    # 1. Initialize Root and Splash instantly
    root = tk.Tk()
    root.withdraw() # Hide the ugly default window for a split second

    from .splash import SplashFrame
    splash = SplashFrame(root)
    root.update() # Force drawing the splash screen

    # App Initialization
    logger.debug(f"Run {APP_NAME}")
    try:
        app = GuiApp(root=root)
    except Exception as e:
        print(f"Critical Startup Error: {e}",file=sys.stderr)
        logging.debug(f"Startup Error: {e}")
        root.destroy()
        return

    # === Artificial Loading Delay ===4
    DEV_DELAY = False
    if DEV_DELAY:
        import time
        for _ in range(40):
            if not root.winfo_exists(): return
            time.sleep(0.05)
            root.update()
    # ====================================

    # Handover
    if root.winfo_exists():
        splash.teardown() # The Splash cleans itself up

        # Restore window borders/decorations
        root.overrideredirect(False)

        # Re-center the app window before showing it
        # Center and then reveal
        # 2. CONFIG: Set title and geometry while hidden
        center_window_on_primary(root, APP_W, APP_H)


        root.config(cursor="arrow")


        root.deiconify()


        # Focus is safer than 'topmost' for the mouse cursor
        root.focus_force()

        # Only use lift(), avoid wm_attributes("-topmost", True) if possible on WSL
        if not pyhabitat.on_wsl():
            root.lift()
            root.wm_attributes("-topmost", True)
            root.after(200, lambda: root.wm_attributes("-topmost", False))
        else:
            # On WSL, just lift and hope for the best without locking the Z-order
            root.lift()

        if pyhabitat.on_windows():
            try:
                hwnd = root.winfo_id()
                ctypes.windll.user32.SetForegroundWindow(hwnd)
            except:
                pass

        if time_auto_close > 0:
            root.after(time_auto_close, root.destroy)


        root.mainloop()
    logger.debug(f"{APP_NAME}: gui closed.")

if __name__ == "__main__":
    start_gui()
