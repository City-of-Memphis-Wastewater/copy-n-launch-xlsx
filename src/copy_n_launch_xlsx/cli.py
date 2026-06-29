#!/usr/bin/env python3
# # src/copy_n_launch_xlsx/cli.py.py
from __future__ import annotations
import typer
import click
from typing import Literal, List, Dict, Optional, Union
from typer.models import OptionInfo
from pathlib import Path
import pyhabitat
import sys
import os
from importlib.resources import files
from typer_helptree import add_typer_helptree
from rich.console import Console
import logging
logger=logging.getLogger(__name__)

from .paths import APP_NAME
from .context import DESCRIPTION_STR
from .logging_setup import configure_logging_for_application
from ._version import __version__
from .core import copy_then_rename_and_move_then_try_launch
from .webapp import run_webapp

console = Console(stderr=True)

# Force Rich to always enable colors, even when running from a .pyz bundle
os.environ["FORCE_COLOR"] = "1"
# Optional but helpful for full terminal feature detection
os.environ["TERM"] = "xterm-256color"

app = typer.Typer(
    name=APP_NAME,
    help=f"DESCRIPTION_STR (v{__version__})",
    add_completion=False,
    invoke_without_command = True,
    no_args_is_help = False,
    context_settings={"ignore_unknown_options": True,
                      "allow_extra_args": True,
                      "help_option_names": ["-h", "--help"]},
)

@app.callback(invoke_without_command=True, no_args_is_help=False)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", is_flag=True),
    debug: bool = typer.Option(False, "--debug","-d", is_flag=True),
    verbose: bool = typer.Option(False, "--verbose","-v", is_flag=True),
):
    if version:
        typer.echo(__version__)
        raise typer.Exit()

    configure_logging_for_application(debug,verbose)

    # Join the string from the command line arg and log debug to show the command.
    full_command_list = sys.argv
    command_string = " ".join(full_command_list)
    logging.debug(f"command:\n{command_string}\n")

    if ctx.invoked_subcommand is None:
        gui_command()

add_typer_helptree(app = app, console = console, version = __version__, hidden = False)

@app.command(name="copylaunch")
def copyrenamelaunch(
    )->None:
    """
    Run the core function.
    """
    result = copy_then_rename_and_move_then_try_launch()
    destination = result.destination

    if result.is_new:
        logger.debug(f"Created\n{destination}\n")
    elif not result.is_new:
        logger.debug(f"File exists\n{destination}\n")

@app.command(name="webapp")
def webapp(
    )->None:
    """
    Serve the web interface to localhost.
    """
    run_webapp()


@app.command(name="gui")
def gui_command(
    auto_close: int = typer.Option(0,
                                   "--auto-close", "-c",
                                   help = "Delay in milliseconds after which the GUI window will close (for automated testing). Use 0 to disable auto-closing.",
                                   min=0)
    )->None:
    """
    Launch tkinter-based GUI.
    """
    assured_auto_close_value = 0

    if isinstance(auto_close, OptionInfo):
        # Case 1: Called implicitly from main() (with no args)
        # We received the metadata object, so use the function's default value (0).
        # We don't need to do anything here since final_auto_close_value is already 0.
        pass
    else:
        # Case 2: Called explicitly by Typer
        # Typer has successfully converted the command line argument, and auto_close is an int.
        assured_auto_close_value = int(auto_close)

    if not pyhabitat.tkinter_is_available():
        _gui_failure_msg()
        return

    from .gui import start_gui
    start_gui(time_auto_close = assured_auto_close_value)

def _gui_failure_msg():
    console.print("[bold red]GUI failed to launch[/bold red]")
    console.print("Use cli or webapp instead.")
    console.print(f"pyhabitat.tkinter_is_available() = {pyhabitat.tkinter_is_available()}")
    console.print(f"pyhabitat.on_termux() = {pyhabitat.on_termux()}")
    
if __name__ == "__main__":
    app()
