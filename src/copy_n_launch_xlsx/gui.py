
#!/usr/bin/env python3
# # src/copy_n_launch_xlsx/gui.py
from __future__ import annotations
import pyhabitat
import logging
logger=logging.getLogger(__name__)

def start_gui():
    logger.debug(f"Not yet implemented.")

def start_gui(time_auto_close: int = 0):
    # 1. Initialize Root and Splash instantly
    root = tk.Tk()
    root.withdraw() # Hide the ugly default window for a split second

    from pdflinkcheck.splash import SplashFrame
    splash = SplashFrame(root)
    root.update() # Force drawing the splash screen

    # app = PDFLinkCheckApp(root=root)
    # App Initialization
    logger.debug("Run PDF Link Check Engine")
    try:
        app = PDFLinkCheckApp(root=root)
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
    logger.debug("pdflinkcheck: gui closed.")

if __name__ == "__main__":
    start_gui()