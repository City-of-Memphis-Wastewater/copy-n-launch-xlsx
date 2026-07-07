#!/usr/bin/env python3
# # src/copy_n_launch_xlsx/__init__.py
from __future__ import annotations
import os

from ._version import __version__

# 1. Clean public facing mapping
__all__ = [
    "__version__",
    "get_target_copy_dir",
    "copy_then_launch",
    "CopyResult",
    "__gui_easteregg_enabled__", # Re-added for REPL discovery
]

def _check_easteregg_env() -> bool:
    """Helper to dynamically read environment state at call-time."""
    env_flag = os.environ.get('CNLX_GUI_EASTEREGG', '').strip().lower()
    return env_flag in ('true', '1', 'yes', 'on')

# 2. Fully dynamic attribute routing
def __getattr__(name: str):
    if name == "get_target_copy_dir":
        from .paths import get_target_copy_dir
        return get_target_copy_dir

    if name == "copy_then_launch":
        from .core import copy_then_launch
        return copy_then_launch

    if name == "CopyResult":
        from .core import CopyResult
        return CopyResult
    
    # Dynamic boolean evaluation for the breadcrumb attribute
    if name == "__gui_easteregg_enabled__":
        return _check_easteregg_env()

    # Dynamic lookups for the GUI function invocation
    if name == "start_gui":
        def _missing_gui():
            raise RuntimeError(
                "start_gui requires pyhabitat and a Tkinter-capable environment"
            )
        _missing_gui.__name__ = "start_gui"
        _missing_gui.__doc__ = (
            "GUI support is unavailable in this environment."
        )
        if _check_easteregg_env():
            try:
                import pyhabitat
                if pyhabitat.tkinter_is_available():
                    from .gui import start_gui
                    return start_gui
            except ImportError:
                pass

            return _missing_gui

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# 3. Dynamic introspection reflecting runtime changes
def __dir__():
    exported = list(__all__)
    if _check_easteregg_env():
        exported.append("start_gui")

    return sorted(exported + [
        "__builtins__", "__cached__", "__doc__", "__file__",
        "__getattr__", "__dir__", "__loader__", "__name__", "__package__", "__path__", "__spec__"
    ])
