from __future__ import annotations

import urllib.request
from pathlib import Path

DATA_DIR = Path("data/ptbxl")
BASE_URL = "https://physionet.org/files/ptb-xl/1.0.3"

METADATA_FILES = ["ptbxl_database.csv", "scp_statements.csv"]


def download_metadata(dest: Path = DATA_DIR) -> None:
    """
    Download the PTB-XL metadata CSVs (small; a few MB).
    """
    dest.mkdir(parents=True, exist_ok=True)
    for name in METADATA_FILES:
        target = dest / name
        if target.exists():
            print(f"{name} already present, skipping.")
            continue
        url = f"{BASE_URL}/{name}"
        print(f"Downloading {name} ...")
        urllib.request.urlretrieve(url, target)
    print("Metadata download complete.")
