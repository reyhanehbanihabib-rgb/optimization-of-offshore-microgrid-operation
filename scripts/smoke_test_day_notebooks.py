"""Smoke-test setup/data/model cells for the seven Day notebooks."""

from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks" / "01-optimization"


def main():
    notebooks = sorted(
        NOTEBOOK_DIR.glob("Offshore Microgrid Optimization - IM - GF - Day *.ipynb")
    )
    for notebook_path in notebooks:
        notebook = nbformat.read(notebook_path, as_version=4)
        notebook.cells = notebook.cells[:7]
        client = NotebookClient(
            notebook,
            timeout=300,
            kernel_name="python3",
            resources={"metadata": {"path": str(ROOT)}},
        )
        client.execute()
        print(f"{notebook_path.name}: setup smoke passed")


if __name__ == "__main__":
    main()
