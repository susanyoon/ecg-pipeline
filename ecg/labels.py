from __future__ import annotations

import ast
from pathlib import Path

import pandas as pd

SCP_PATH = Path("data/ptbxl/scp_statements.csv")


def load_superclass_map(path: Path = SCP_PATH) -> dict[str, str]:
    """
    Build a code -> superclass mapping from scp_statements.csv,
    keeping only diagnostic codes.
    """
    df = pd.read_csv(path, index_col=0)
    diagnostic = df[df["diagnostic"] == 1]
    return diagnostic["diagnostic_class"].to_dict()


def parse_scp_codes(raw: str) -> dict[str, float]:
    """
    Parse the scp_codes cell, e.g. "{'NORM': 100.0}" -> dict.
    """
    return ast.literal_eval(raw)


def superclasses_for_record(
    scp_codes: dict[str, float], superclass_map: dict[str, str]
) -> list[str]:
    """
    Map a record's SCP codes to its distinct diagnostic superclasses.

    Only codes present in the diagnostic map contribute;
    the rest (rhythm/form codes) are ignored for classification.
    """
    classes = set()
    for code in scp_codes:
        if code in superclass_map:
            classes.add(superclass_map[code])
    return sorted(classes)
