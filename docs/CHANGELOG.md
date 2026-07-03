# Changelog

All notable changes to this project will be documented in this file.

The format is (read: strives to be) based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.2.14] - 2026-07-03
### Added:
- flatpak manifrst with icon, and desktop file.

---

## [0.2.13] - 2026-07-02
### Added:
- build.yml should now allow Ubuntu PYZ and WHL to be attached to release.
- .github/workflows/flatpak.yml and the yaml manifest in the project root. Flatpak now succeeding (to build, and to test).
 
---

## [0.2.12] - 2026-07-02
### Added:
- AppImage build for Linux, included in release.
- No longer include Linux tar.gz onedir in releases.

---

## [0.2.11] - 2026-07-02
### Added:
- GUI screenshot PNG added to assets and referenced and centered in README.md

---

## [0.2.10] - 2026-07-02
### Added:
- core.py, FileNotFound instead of sys.exit()
- Fix type hint in core for CopyResult return.
- Improve README.md

---

## [0.2.9] - 2026-07-02
### Added:
- helptree SVG asset and reference in README.

---

## [0.2.8] - 2026-07-02
### Added:
- Remove XLSX data file from git tracking. 
- Move defacto blank file location to ~/.copy-n-launch-xlsx/blank/daily_blank.xlsx
- publish.yml
- Set pypi environment on github settings, and add a new pending publisher to pypi.

---

## [0.2.7] - 2026-07-01
### Added:
- License: BSD-2-Clause-Patent

---

## [0.2.6] - 2026-07-01
### Added:
- Stable DWG production on macOS 13 and newer.
- macoS iconset inclusion, test.
 
---

## [0.2.5] - 2026-06-30
### Changed:
- Mess with build_executable.py, hope for a miracle.

---

## [0.2.4] - 2026-06-30
### Changed:
- .dmg support for mac_os.
- buid_executable.py modularity improved.

---

## [0.2.2] - 2026-06-29
### Changed:
- Taskbar icon permanence, using gui.apply_windows_taskbar_icon()

---

## [0.2.1] - 2026-06-29
### Changed:
- Icon changed to green.
- About button.
- build.yml and build_executable.py improved for macOS .app stability, and for build attachment even when other runners are incomplete.

---

## [0.1.7] - 2026-06-29
### Changed:
- Change config file from .env to stable config.json in expected place. 
- Try to package .app for macOS in build_executable.py.

---

## [0.1.4] - 2026-06-29
### Added:
- Use pyinstaller hooks and setuptools.package to ensure /data/ artifacts are included in PyInstaller and shiv builds.

---

## [0.1.3] - 2026-06-29
### Added:
- Use pyhabitat v1.3.2, with more stable cross platform file launching.
- Trim blank spreadsheet.
- Implement aut-dating.
- Simplify GUI.
- Test on WSL.

---

## [0.1.1] - 2026-06-29
### Added:
- Initial release.
- Includes GUI, CLI, webapp, build processes, the core and pathing, etc.
- MVP.

---


