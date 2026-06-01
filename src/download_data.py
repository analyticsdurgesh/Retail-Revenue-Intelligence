from __future__ import annotations

import zipfile
from pathlib import Path

import requests

DATA_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
RAW_DIR = Path("data/raw")
ZIP_PATH = RAW_DIR / "online_retail.zip"
XLSX_PATH = RAW_DIR / "Online Retail.xlsx"


def download_file(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size > 0:
        print(f"Already downloaded: {target}")
        return
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with target.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)
    print(f"Downloaded: {target}")


def main() -> None:
    download_file(DATA_URL, ZIP_PATH)
    if not XLSX_PATH.exists():
        with zipfile.ZipFile(ZIP_PATH) as archive:
            archive.extractall(RAW_DIR)
        print(f"Extracted dataset into {RAW_DIR}")
    print("Retail raw data is ready.")


if __name__ == "__main__":
    main()

