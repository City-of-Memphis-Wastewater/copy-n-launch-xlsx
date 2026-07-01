#!/usr/bin/env python3 
# SPDX-License-Identifier: MIT
# ./build_executable.py
"""
build_executable.py
Builds the standalone binary (EXE/ELF) using PyInstaller.
"""
from __future__ import annotations
import shutil
import subprocess
import sys
import os
from pathlib import Path
import argparse
import pyhabitat
import tempfile

from pyhabitat.environment import on_macos

##from copy_n_launch_xlsx.datacopy import ensure_data_files_for_build
from copy_n_launch_xlsx._version import get_version, __version__
from copy_n_launch_xlsx.paths import (
        SRC_FOLDER_NAME, APP_NAME, get_ico_icon, get_icns_icon
        )

# --- Configuration ---
CLI_MAIN_FILE = Path.cwd() / 'src' / SRC_FOLDER_NAME / "__main__.py"
DIST_DIR = Path("dist")
DIST_DIR_ONEFILE = DIST_DIR / "onefile" 
DIST_DIR_ONEDIR = DIST_DIR / "onedir" 
STANDARD_MACOS_APP_DIST_DIR = DIST_DIR
BUILD_DIR = Path("build/pyinstaller_work")
RC_TEMPLATE = Path('build_assets') / 'version.rc.template' # Assume this template exists for Windows
RC_FILE = Path('build_assets') / 'version.rc'
IS_WINDOWS_BUILD = pyhabitat.on_windows()
PROJECT_ROOT = Path(__file__).resolve().parent
HOOKS_DIR_ABS = PROJECT_ROOT / "pyinstaller_hooks"

# --- Dynamic Naming Placeholder (Simplified version for this context) ---
def form_dynamic_name(pkg_name: str, version: str) -> str:
    """Creates a standardized binary name descriptor."""

    os_tag = pyhabitat.SystemInfo().get_os_tag()
    arch = pyhabitat.SystemInfo().get_arch()
    py_ver = f"py{sys.version_info.major}{sys.version_info.minor}"
    return f"{pkg_name}-{version}-{py_ver}-{os_tag}-{arch}"

# --- Windows Resource File (version.rc) ---
def generate_rc_file(package_version: str):
    """Generates the .rc file using the provided version string, only on Windows."""
    if not IS_WINDOWS_BUILD: return

    if not RC_TEMPLATE.exists():
        print(f"WARNING: RC template not found at {RC_TEMPLATE}. Skipping version info embedding.", file=sys.stderr)
        return

    # Implementation logic for reading template and writing RC_FILE...
    # (Same as in the previous pipeline script, but simplified here)
    print(f"Placeholder: Generated resource file {RC_FILE} for version {package_version}")
    RC_FILE.write_text("// Placeholder content for versioning", encoding="utf-8")


# --- Setup & Cleanup ---

def setup_dirs():
    """Ensure directories exist."""
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR_ONEFILE.mkdir(parents=True, exist_ok=True)
    DIST_DIR_ONEDIR.mkdir(parents=True, exist_ok=True)

def determine_file_extension():
    if IS_WINDOWS_BUILD:
        return '.exe'
    elif pyhabitat.on_macos():
        return '.app'
    return ''

def clean_artifacts(exe_name: str, mode: str):
    """Clean specific output and build folders based on mode."""
    
    
    # Define what we are cleaning based on mode
    if mode == "onedir":
        # In onedir, PyInstaller creates a directory with the exe_name
        mode_dir = DIST_DIR_ONEDIR
        target = mode_dir / exe_name
    else:
        # In onefile, it's just the .exe (or ELF) file
        mode_dir = DIST_DIR_ONEFILE
        #ext = '.exe' if IS_WINDOWS_BUILD else ''
        ext = determine_file_extension()
        target = mode_dir / f"{exe_name}{ext}"

    if target.exists():
        print(f"Removing old build artifact: {target.resolve()}")
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
    
    # Clean the work directory
    if BUILD_DIR.exists():
        print(f"Removing build/pyinstaller_work folder: {BUILD_DIR.resolve()}")
        shutil.rmtree(BUILD_DIR)

    if IS_WINDOWS_BUILD and RC_FILE.exists():
        RC_FILE.unlink()

# --- Main PyInstaller Execution ---

def run_pyinstaller(
        dynamic_exe_name: str, 
        main_script_path: Path,
        mode: str = "onedir",
        ):
    """
    Run PyInstaller to build the executable.
    """
    
    print(f"--- {SRC_FOLDER_NAME} Executable Builder ---")

    #ext = '.exe' if IS_WINDOWS_BUILD else ''
    ext = determine_file_extension()
    app_filename = f"{dynamic_exe_name}{ext}"
    if mode == "onefile":
        mode_dist_path = DIST_DIR_ONEFILE 
        app_path = DIST_DIR_ONEFILE/ app_filename
    elif mode  == "onedir":
        if pyhabitat.on_macos():
            app_path = STANDARD_MACOS_APP_DIST_DIR / app_filename # true before move
        else:
            mode_dist_path = DIST_DIR_ONEDIR
            app_path = DIST_DIR_ONEDIR / dynamic_exe_name / app_filename

    mode_dist_path.mkdir(parents=True, exist_ok=True)

    print(f"Executable is located at: {app_path.resolve()}") 

    # Clean and Setup
    clean_artifacts(exe_name=dynamic_exe_name, mode=mode)
    setup_dirs()

    
    # PyInstaller Command Construction
    base_command = [
        #'pyinstaller',
        sys.executable, "-m", "PyInstaller",
        '--noconfirm',
        '--clean',
        f'--name={dynamic_exe_name}',

        # --- Crucial for resolving package structure and relative imports ---
        f'--paths={PROJECT_ROOT / "src"}',

        # --- Include your non-py data folders into the built bundle layout ---
        f'--add-data={PROJECT_ROOT / "src" / SRC_FOLDER_NAME / "data"}{os.path.pathsep}{SRC_FOLDER_NAME}/data',
        
        # Output paths
        f'--workpath={BUILD_DIR / "work"}',
        f'--specpath={BUILD_DIR}',

        # --- Add the Hooks Directory ---
        f'--additional-hooks-dir={HOOKS_DIR_ABS}', # 

        #'--log-level=DEBUG',

    ]
    if pyhabitat.on_macos():
        flag = f'--distpath={STANDARD_MACOS_APP_DIST_DIR}'
    else:
        flag = f'--distpath={mode_dist_path}'
    base_command.append(flag)


    # msix.yml and build.yml have been adjusted to expect either onefile or onedir
    if mode == "onefile": 
        onedir_or_onefile_flag = '--onefile'
        base_command.append(onedir_or_onefile_flag)
    else: # default
        if not pyhabitat.on_macos():
            onedir_or_onefile_flag = '--onedir'
            base_command.append(onedir_or_onefile_flag)
    
    # Prepare for MSIX
    is_windowed_build = (IS_WINDOWS_BUILD or pyhabitat.on_macos()) and (mode == "onedir")
    if is_windowed_build:
        flag = '--windowed'
        base_command.append(flag)
    else:
        print("Building without the --noconsole or --windowed flag, to favor CLI usage for the artifact, because GUI is not available.")

    # Add Windows resource file if applicable
    if IS_WINDOWS_BUILD and RC_FILE.exists():
        #base_command.append(f'--version-file={RC_FILE.name}')
        base_command.append(f'--version-file={RC_FILE.resolve()}')
        base_command.append(
            f"--icon={get_ico_icon().resolve()}"
        )

    if False and pyhabitat.on_macos():
        base_command.append(
            f"--icon={get_icns_icon().resolve()}"
        )
    base_command.append(str(main_script_path.resolve()))

    # Determine execution path (Run PyInstaller directly, assuming it's in PATH/venv)
    full_command = base_command
    print(f"Executing PyInstaller: {' '.join(full_command)}")

    # 6. Execute
    try:
        # Pass environment variables to ensure venv dependencies are found
        subprocess.run(full_command, check=True, env=os.environ.copy()) 
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller failed with exit code {e.returncode}!", file=sys.stderr)
        raise SystemExit(e.returncode)
    purge_raw_unix_structure_from_macos_build(dynamic_exe_name)
    print("\n--- PyInstaller Build Complete ---")
    return app_path.resolve(), app_filename

def purge_raw_unix_structure_from_macos_build(dynamic_exe_name):
    if pyhabitat.on_macos():
        # --- PURGE THE DUPLICATE RAW UNIX FOLDER STRUCTURE ---
        duplicate_cli_dir = Path("dist") / dynamic_exe_name
        if duplicate_cli_dir.exists() and duplicate_cli_dir.is_dir():
            print(f"Cleaning up duplicate raw Unix folder: {duplicate_cli_dir.resolve()}")
            shutil.rmtree(duplicate_cli_dir)

def move_macos_app(macos_app_filename):
    from pathlib import Path
    import shutil

    src = STANDARD_MACOS_APP_DIST_DIR / macos_app_filename
    dst = DIST_DIR_ONEDIR  / macos_app_filename
    dst.parent.mkdir(parents=True, exist_ok=True)

    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.move(str(src), str(dst))
        return dst
    return None

def build_macos_dmg(app: Path) -> Path:
    if app.suffix != ".app":
        raise ValueError(f"Expected a .app bundle, got {app}")

    if shutil.which("create-dmg") is None:
        raise RuntimeError("create-dmg is not installed. Install with: brew install create-dmg")

    upload_dir = Path("dist/upload")
    upload_dir.mkdir(parents=True, exist_ok=True)

    dmg = upload_dir / f"{app.stem}.dmg"

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        staged = tmp / app.name
        shutil.copytree(app, staged)

        subprocess.run(
            [
                "create-dmg",
                "--volname",
                f"{APP_NAME} {__version__}",
                "--window-size",
                "600",
                "400",
                "--icon-size",
                "100",
                "--icon",
                staged.name,
                "150",
                "180",
                "--app-drop-link",
                "450",
                "180",
                str(dmg.resolve()),
                str(tmp),
            ],
            check=True,
        )

    return dmg

def executable_for_testing(path: Path) -> Path:
    if pyhabitat.on_macos() and path.suffix == ".app":
        return path / "Contents" / "MacOS" / path.stem
    return path

def run_build_executable():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices = ("onedir","onefile"),
        default = "onedir",
        help = "PyInstaller build mode.",
        )
    args = parser.parse_args()
    try:
        package_version = get_version()
        if package_version == "0.0.0":
            print("FATAL: Cannot find package version in pyproject.toml.", file=sys.stderr)
            sys.exit(1)
        
        # 0. Ensure data files are available to build package
        ##ensure_data_files_for_build()

        # 1. Ensure PyInstaller is installed (if you haven't done it manually)
        # uv run python -m pip install pyinstaller 
        
        # 2. Generate RC file (conditionally)
        generate_rc_file(package_version)

        # 3. Determine the executable name (without the extension)
        executable_descriptor = form_dynamic_name(SRC_FOLDER_NAME, package_version)
        if args.mode == "onefile":
            executable_descriptor += "-onefile"

        # 4. Run the installer
        app_path, app_filename = run_pyinstaller(
            executable_descriptor, 
            CLI_MAIN_FILE, 
            mode = args.mode,
            )

        # Only test GUI if we aren't in a headless CI environment
        # GitHub Actions sets the GITHUB_ACTIONS environment variable to 'true'
        is_ci = os.environ.get('GITHUB_ACTIONS') == 'true'

        # Only run text-based --help check if we aren't a hidden-window GUI binary
        is_windowed_build = (IS_WINDOWS_BUILD) and (args.mode == "onedir") and pyhabitat.tkinter_is_available()

        #if is_ci:
        #    print("[CI DETECTED] Skipping CLI help text check to prevent headless stream hangs.")
        if is_windowed_build:
            print("Skipping CLI help text check because artifact was built with --windowed.")
        elif not pyhabitat.on_macos():
            print("Testing the PyInstaller artifact...")
            subprocess.run([str(app_path), "--help"], check=True)

        print(f"pyhabitat.tkinter_is_available() = {pyhabitat.tkinter_is_available()}")
        if pyhabitat.tkinter_is_available() and not is_ci:
            print(f"Testing GUI for {str(app_path)}...")
            exe = executable_for_testing(app_path)
            subprocess.run([str(exe), "gui", "--auto-close", "1000"], check=True)
        print("Testing complete.")


        if pyhabitat.on_macos():
            #app = move_macos_app(app_path) or app_path
            app = move_macos_app(app_filename) or app_path 
            dmg = build_macos_dmg(app)
            #build_macos_dmg(path)

    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        print(f"An unhandled error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    
if __name__ == "__main__":
    run_build_executable()