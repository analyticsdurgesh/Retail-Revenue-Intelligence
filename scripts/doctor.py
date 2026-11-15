"""Check that this computer (or Codespace) is ready for the project, in plain words.

Run it from the project folder, any time something feels off:

    python scripts/doctor.py

It only uses Python's standard library, so it works before you install anything.
Every problem it finds comes with the exact command that fixes it, for macOS /
Linux and for Windows PowerShell. If a fix does not work, paste the WHOLE output
into the project's doubt forum: it holds no passwords or personal data.
"""
from __future__ import annotations

import importlib.metadata
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WINDOWS = platform.system() == "Windows"
MIN_PYTHON = (3, 11)
DATASET_HOST = "https://archive.ics.uci.edu/"
problems = 0


def say(mark: str, text: str, fix: str = "") -> None:
    print(f"  {mark} {text}")
    for line in fix.strip("\n").splitlines():
        print(f"      {line}")


def bad(text: str, fix: str) -> None:
    global problems
    problems += 1
    say("✗", text, fix)


def environment() -> str:
    if os.environ.get("CODESPACES") == "true":
        return "GitHub Codespace"
    if os.environ.get("REMOTE_CONTAINERS") == "true" or os.environ.get("DEVCONTAINER") == "true":
        return "dev container"
    if sys.prefix != getattr(sys, "base_prefix", sys.prefix):
        return "virtual environment (venv)"
    return ""


def check_python() -> None:
    version = ".".join(map(str, sys.version_info[:3]))
    if sys.version_info[:2] >= MIN_PYTHON:
        say("✓", f"Python {version}")
    else:
        bad(f"Python {version} is too old: this project needs 3.11 or newer",
            "Install Python 3.11+ from https://www.python.org/downloads/ , then make the venv again.")


def check_isolation() -> None:
    where = environment()
    if where:
        say("✓", f"An isolated environment: {where}")
        return
    if WINDOWS:
        fix = ("python -m venv .venv\n.venv\\Scripts\\Activate.ps1\npip install -r requirements.txt\n"
               "If PowerShell says running scripts is disabled, run this once, then activate again:\n"
               "Set-ExecutionPolicy -Scope CurrentUser RemoteSigned")
    else:
        fix = "python3 -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt"
    bad("You are not inside a virtual environment, so packages land in your system Python",
        f"From this folder, run:\n{fix}\n(Your prompt then starts with (.venv).)")


def required_packages() -> list[tuple[str, str]]:
    wanted = []
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*([A-Za-z0-9_.\-]+)\s*>=\s*([0-9][0-9.]*)", line)
        if match:
            wanted.append((match.group(1), match.group(2)))
    return wanted


def as_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", version)[:3])


def check_packages() -> None:
    missing, old, found = [], [], []
    for name, minimum in required_packages():
        try:
            version = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            missing.append(name)
            continue
        (old if as_tuple(version) < as_tuple(minimum) else found).append(f"{name} {version}")
    total = len(found) + len(missing) + len(old)
    if not missing and not old:
        say("✓", f"Packages: all {total} from requirements.txt are installed")
        return
    pip = "pip install -r requirements.txt"
    if missing:
        bad(f"Missing packages: {', '.join(missing)}", f"With your environment active, run:\n{pip}")
    if old:
        bad(f"Packages older than requirements.txt asks for: {', '.join(old)}", f"Run:\n{pip} --upgrade")


def check_git() -> None:
    if not shutil.which("git"):
        bad("git is not installed", "Install it from https://git-scm.com/downloads , then open a new terminal.")
        return
    def value(key: str) -> str:
        done = subprocess.run(["git", "config", key], capture_output=True, text=True, cwd=ROOT)
        return done.stdout.strip()
    if value("user.name") and value("user.email"):
        say("✓", "git knows your name and email (your commits will be yours)")
    else:
        bad("git does not know your name or email yet",
            'git config --global user.name "Your Name"\ngit config --global user.email "you@example.com"\n'
            "(Use the email of your GitHub account.)")
    origin = value("remote.origin.url")
    if "analyticsdurgesh/" in origin.lower():
        bad("This folder is a copy of the ORIGINAL repository, not your fork",
            "Fork the project on GitHub (the Fork button), then clone YOUR fork:\n"
            "git clone https://github.com/<your-username>/Retail-Revenue-Intelligence.git\n"
            "In a Codespace: open the Codespace from your fork's page instead.")
    elif origin:
        say("✓", f"Working in your own repository ({origin.split('github.com')[-1].lstrip(':/')})")


def check_folder() -> None:
    markers = ["src/download_data.py", "src/prepare_data.py", "dashboard/app.py", "requirements.txt"]
    missing = [m for m in markers if not (ROOT / m).exists()]
    if missing:
        bad(f"Project files missing: {', '.join(missing)}", "Run this from the project folder, the one that contains src/ and dashboard/.")
    else:
        say("✓", "Project files are all here")


def check_disk_and_write() -> None:
    free_gb = shutil.disk_usage(ROOT).free / 1e9
    if free_gb < 1:
        bad(f"Only {free_gb:.1f} GB free on this disk", "The dataset and its outputs need about 1 GB. Free some space first.")
    else:
        say("✓", f"Disk space: {free_gb:.0f} GB free")
    probe = ROOT / "data" / "processed" / ".doctor-write-test"
    try:
        probe.parent.mkdir(parents=True, exist_ok=True)
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        say("✓", "The project folder is writable")
    except OSError as error:
        bad(f"Cannot write inside the project folder ({error.strerror})",
            "Move the project into your home folder (not a system or OneDrive-synced folder) and try again.")


def check_network() -> None:
    try:
        request = urllib.request.Request(DATASET_HOST, method="HEAD", headers={"User-Agent": "prepnplaced-doctor"})
        with urllib.request.urlopen(request, timeout=8):
            pass
        say("✓", "Internet: the UCI dataset site answers")
    except Exception as error:  # noqa: BLE001 — any failure here is the network's
        bad(f"Cannot reach the dataset site ({type(error).__name__})",
            "Module 1 downloads the data from archive.ics.uci.edu. College or office Wi-Fi sometimes\n"
            "blocks it: try a phone hotspot, or open the project in a GitHub Codespace.")


def check_data() -> None:
    raw = ROOT / "data" / "raw" / "Online Retail.xlsx"
    if raw.exists():
        say("✓", f"Data: {raw.name} downloaded ({raw.stat().st_size / 1e6:.1f} MB)")
    else:
        say("·", "Data: not downloaded yet (that is Module 1: python src/download_data.py)")


def main() -> int:
    print("PrepNPlaced doctor: checking your setup for Retail Revenue Intelligence\n")
    print(f"  · {platform.system()} {platform.release()}, Python at {sys.executable}")
    for check in (check_python, check_isolation, check_packages, check_git, check_folder, check_disk_and_write, check_network, check_data):
        check()
    if problems:
        print(f"\n{problems} thing{'s' if problems > 1 else ''} to fix, above. If a fix does not work, paste this whole output into the doubt forum.")
        return 1
    print("\nREADY. Next: python src/download_data.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
