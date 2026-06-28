#!/usr/bin/env python3
# # src/copy_n_launch_xlsx/gui.py
from __future__ import annotations
import pyhabitat
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, PhotoImage
import sys
from pathlib import Path
from typing import Optional
import unicodedata
from importlib.resources import files
import pyhabitat
import ctypes
import threading
import logging
# --- Core Imports ---

from ._version import get_version
from .environment import is_in_dev_environment
from .tk_utils import center_window_on_primary
from .helpers import get_friendly_path
from .paths import APP_NAME, get_target_copy_dir

logger=logging.getLogger(__name__)

class RedirectText:
    """A class to redirect sys.stdout messages to a Tkinter Text widget."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self, *args):
        pass

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
        self.root.geometry("700x500")  # Smaller starting size
        self.root.minsize(600, 400)    # Prevent too-small window

        self._set_icon()

        # --- 2. Widget Construction ---
        self._create_widgets()
        self._initialize_menubar()

    def _initialize_vars(self):
        """Logic that takes time but doesn't need a UI yet."""

        # --- 1. Variable State Management ---
        self.pdf_path = tk.StringVar(value="")
        self.do_export_report_json_var = tk.BooleanVar(value=True)
        self.do_export_report_txt_var = tk.BooleanVar(value=True)
        self.do_export_report_xlsx_var = tk.BooleanVar(value=True)
        self.do_check_external_links = tk.BooleanVar(value=False)

        self.current_report_text = None
        self.current_report_data = None

        # Engine detection
        self.example_string_var = tk.StringVar(value="null")

    # --- Theme & Visual Initialization ---
    def _initialize_forest_theme(self):
        theme_dir = files("pdflinkcheck.data.themes.forest")
        self.root.tk.call("source", str(theme_dir / "forest-light.tcl"))
        self.root.tk.call("source", str(theme_dir / "forest-dark.tcl"))

    def _toggle_theme(self):
        style = ttk.Style(self.root) # Explicitly link style to our root
        if style.theme_use() == "forest-light":
            style.theme_use("forest-dark")
        elif style.theme_use() == "forest-dark":
            style.theme_use("forest-light")

    def _set_icon(self):
        icon_dir = files(".data.icons")
        try:
            png_path = icon_dir.joinpath("Logo-150x150.png")
            if png_path.exists():
                self.icon_img = PhotoImage(file=str(png_path))
                self.root.iconphoto(True, self.icon_img)
        except Exception:
            pass
        try:
            icon_path = icon_dir.joinpath("red_pdf_512px.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass


    def _initialize_menubar(self):
        """Builds the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        tools_menu.add_command(label="Toggle Theme", command=self._toggle_theme)

        tools_menu.add_separator()
        tools_menu.add_command(label="Readme", command=self._show_readme)

    # --- UI Component Building ---

    def _create_widgets(self):
        """Compact layout with reduced padding."""

        # --- Control Frame (Top) ---
        control_frame = ttk.Frame(self.root, padding=(4, 2, 4, 2))
        control_frame.pack(fill='x', pady=(2, 2))

        # === Row 0: File Selection ===
        file_selection_frame = ttk.Frame(control_frame)
        file_selection_frame.grid(row=0, column=0, columnspan=3, padx=0, pady=(2, 4), sticky='ew')

        ttk.Label(file_selection_frame, text="PDF Path:").pack(side=tk.LEFT, padx=(0, 3))
        entry = ttk.Entry(file_selection_frame, textvariable=self.pdf_path)
        entry.pack(side=tk.LEFT, fill='x', expand=True, padx=3)
        ttk.Button(file_selection_frame, text="Browse...", command=self._select_pdf, width=10).pack(side=tk.LEFT, padx=(3, 3))
        ttk.Button(file_selection_frame, text="Copy Path", command=self._copy_pdf_path, width=10).pack(side=tk.LEFT, padx=(0, 0))

        # === Row 1: Configuration & Export Jumps ===
        pdf_library_frame = ttk.LabelFrame(control_frame, text="Backend Engine:")
        pdf_library_frame.grid(row=1, column=0, padx=3, pady=3, sticky='nsew')

        if pdfium_is_available():
            ttk.Radiobutton(pdf_library_frame, text="PDFium", variable=self.pdf_library_var, value=PdfEngine.PDFIUM.name).pack(side='left', padx=5, pady=1)
        if pymupdf_is_available():
            ttk.Radiobutton(pdf_library_frame, text="PyMuPDF", variable=self.pdf_library_var, value=PdfEngine.PYMUPDF.name).pack(side='left', padx=3, pady=1)
        ttk.Radiobutton(pdf_library_frame, text="pypdf", variable=self.pdf_library_var, value=PdfEngine.PYPDF.name).pack(side='left', padx=3, pady=1)

        export_config_frame = ttk.LabelFrame(control_frame, text="Export & Config:")
        export_config_frame.grid(row=1, column=1, padx=3, pady=3, sticky='nsew')

        ttk.Checkbutton(export_config_frame, text="JSON", variable=self.do_export_report_json_var).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(export_config_frame, text="TXT", variable=self.do_export_report_txt_var).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(export_config_frame, text="XLSX", variable=self.do_export_report_xlsx_var).pack(side=tk.LEFT, padx=4)
        ttk.Checkbutton(export_config_frame, text="Ping", variable=self.do_check_external_links).pack(side=tk.LEFT, padx=4)

        self.export_actions_frame = ttk.LabelFrame(control_frame, text="Open Report Files:")
        self.export_actions_frame.grid(row=1, column=2, padx=3, pady=3, sticky='nsew')

        self.btn_open_json = ttk.Button(self.export_actions_frame, text="Open JSON", command=lambda: self._open_export_file("json"), width=10)
        #self.btn_open_json.pack(side=tk.LEFT, padx=3, pady=1)

        self.btn_open_txt = ttk.Button(self.export_actions_frame, text="Open TXT", command=lambda: self._open_export_file("txt"), width=10)
        #self.btn_open_txt.pack(side=tk.LEFT, padx=3, pady=1)

        self.btn_open_browser_to_files = ttk.Button(self.export_actions_frame, text="Show System Explorer", command=lambda: self._show_system_explorer_gui(), width=20)
        self.btn_open_browser_to_files.pack(side=tk.LEFT, padx=3, pady=1)

        # === Row 3: Action Buttons ===
        run_analysis_btn = ttk.Button(control_frame, text="▶ Run Analysis", command=self._run_report_gui, style='Accent.TButton', width=16)
        run_analysis_btn.grid(row=3, column=0, columnspan=2, pady=6, sticky='ew', padx=(0, 3))

        clear_window_btn = ttk.Button(control_frame, text="Clear Output Window", command=self._clear_output_window, width=18)
        clear_window_btn.grid(row=3, column=2, pady=6, sticky='ew', padx=3)

        # Grid configuration
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)

        # --- Output Frame (Bottom) ---
        output_frame = ttk.Frame(self.root, padding=(4, 2, 4, 4))
        output_frame.pack(fill='both', expand=True)

        output_header_frame = ttk.Frame(output_frame)
        output_header_frame.pack(fill='x', pady=(0, 1))

        #ttk.Label(output_header_frame, text="Analysis Report Logs:").pack(side=tk.LEFT, fill='x', expand=True)
        ttk.Label(output_header_frame, text="Output Window:").pack(side=tk.LEFT, fill='x', expand=True)

        ttk.Button(output_header_frame, text="▼ Bottom", command=self._scroll_to_bottom, width=10).pack(side=tk.RIGHT, padx=(0, 2))
        ttk.Button(output_header_frame, text="▲ Top", command=self._scroll_to_top, width=6).pack(side=tk.RIGHT, padx=2)

        # Scrollable Text Area
        text_scroll_frame = ttk.Frame(output_frame)
        text_scroll_frame.pack(fill='both', expand=True, padx=3, pady=3)

        self.output_text = tk.Text(text_scroll_frame, wrap=tk.WORD, state=tk.DISABLED, bg='#2b2b2b', fg='#ffffff', font=('Monospace', 10))
        self.output_text.pack(side=tk.LEFT, fill='both', expand=True)

        scrollbar = ttk.Scrollbar(text_scroll_frame, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text['yscrollcommand'] = scrollbar.set

    # --- Event Handlers & Business Logic ---

    def _select_pdf(self):
        if self.pdf_path.get():
            initialdir = str(Path(self.pdf_path.get()).parent)
        elif pyhabitat.is_msix():
            initialdir = str(Path.home())
        else:
            initialdir = str(Path.cwd())

        file_path = filedialog.askopenfilename(
            initialdir=initialdir,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.pdf_path.set(get_friendly_path(file_path))


    def _get_export_format_selection(self) -> ExportFormat:
        # Build bitmask by checking the state of each BooleanVar directly
        result = ExportFormat.NONE

        if self.do_export_report_json_var.get():
            result |= ExportFormat.JSON
        if self.do_export_report_txt_var.get():
            result |= ExportFormat.TXT
        if self.do_export_report_xlsx_var.get():
            result |= ExportFormat.XLSX
        return result

    def _run_report_gui(self):  
        # from another program

        pdf_path_str = self._assess_pdf_path_str()
        if not pdf_path_str:
            return

        # Parse the GUI checkbox export format boolean variables into a type-safe ExportFormat enum
        export_format = self._get_export_format_selection()

        # Parse the GUI radio PDF engine selection string variable straight back into a type-safe PdfEngine enum
        pdf_library = self._get_pdf_engine_selection()

        # Should we ping external links?
        check_external = self._get_check_external_links_selection()

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete('1.0', tk.END)

        original_stdout = sys.stdout
        sys.stdout = RedirectText(self.output_text)

        print("Running PDF analysis ...")

        # Add input field later
        #check_external = False

        try:
            request = ReportRequest(
                pdf_path=pdf_path_str,
                export_format=export_format,
                pdf_library=pdf_library,
                check_external= check_external
            )
            report_results = run_report_request(request)
            self.current_report_text = report_results.get("text-lines", "")
            self.current_report_data = report_results.get("data", {})

            self.last_json_path = report_results.get("export_files", {}).get("export_path_json")
            self.last_txt_path = report_results.get("export_files", {}).get("export_path_txt")
            self.last_xlsx_path = report_results.get("export_files", {}).get("export_path_xlsx")

        except Exception as e:
            messagebox.showinfo(
                "Engine Fallback",
                f"Error encountered with {pdf_library}: {e}\n\nFalling back to automated library selection."
            )
            self.pdf_library_var.set(PdfEngine.resolve_auto_flag().name)
        finally:
            sys.stdout = original_stdout
            self.output_text.config(state=tk.DISABLED)

    def _show_system_explorer_gui(self) -> None:
        """
        Opens the system file explorer to the directory containing
        the exported reports, with GUI error handling.
        """
        try:
            target_dir = get_target_copy_dir()
            pyhabitat.show_system_explorer(path = target_dir)
        except Exception as e:
            # The GUI catches the error to show a user-friendly popup
            messagebox.showerror("Error", f"Could not open system explorer: {e}")

def start_gui(time_auto_close: int = 0):
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

        # Re-center the MAIN app window before showing it
        app_w, app_h = 700, 500 # known distrubuted size
        app_w, app_h = 800, 500 # stop gap until buttons are reorganized
        # Center and then reveal
        # 2. CONFIG: Set title and geometry while hidden
        center_window_on_primary(root, app_w, app_h)


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
