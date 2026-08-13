from __future__ import annotations

import time
import urllib.request
from pathlib import Path

import wfdb

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


def download_signals(
    record_paths: list[str],
    dest: Path = DATA_DIR,
    retries: int = 3,
    pause: float = 0.05,
) -> tuple[int, int]:
    """
    Download WFDB signal records individually, tolerating transient failures.

    PhysioNet occasionally closes connections during bulk downloads, so each
    record is retried and failures are skipped rather than aborting the run.

    Returns:
        (downloaded, failed) counts.
    """
    dest.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    failed = 0

    for i, rec in enumerate(record_paths, start=1):
        target = dest / f"{rec}.dat"
        if target.exists():
            downloaded += 1
            continue

        for attempt in range(retries):
            try:
                wfdb.dl_files(
                    "ptb-xl",
                    dl_dir=str(dest),
                    files=[f"{rec}.hea", f"{rec}.dat"],
                    keep_subdirs=True,
                )
                downloaded += 1
                break
            except Exception:
                if attempt == retries - 1:
                    failed += 1
                else:
                    time.sleep(2**attempt)  # back off: 1s, 2s, 4s
        time.sleep(pause)

        if i % 100 == 0:
            print(
                f"  {i}/{len(record_paths)} processed "
                f"({downloaded} ok, {failed} failed)"
            )

    return downloaded, failed
