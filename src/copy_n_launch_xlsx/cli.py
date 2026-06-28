#!/usr/bin/env python3
# # src/copy_n_launch_xlsx/cli.py.py
from __future__ import annotations
import typer
import click
from rich.console import Console
import logging
logger=logging.getLogger(__name__)

console = Console(stderr=True)