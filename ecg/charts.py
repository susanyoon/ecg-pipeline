from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def plot_confusion_matrix(cm: list[list[int]], output_path: str) -> None:
    """Save a labeled confusion matrix figure."""
    cm_arr = np.array(cm)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm_arr, cmap="Blues")

    labels = ["Abnormal", "Normal"]
    ax.set_xticks([0, 1], labels)
    ax.set_yticks([0, 1], labels)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix — Normal vs Abnormal ECG")

    for i in range(2):
        for j in range(2):
            ax.text(
                j,
                i,
                str(cm_arr[i, j]),
                ha="center",
                va="center",
                color="black" if cm_arr[i, j] < cm_arr.max() / 2 else "white",
            )

    fig.colorbar(im)
    fig.tight_layout()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
