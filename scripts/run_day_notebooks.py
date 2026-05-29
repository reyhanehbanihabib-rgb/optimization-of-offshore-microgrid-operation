"""Execute the seven main Day notebooks and keep their outputs."""

from pathlib import Path
import os

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks" / "01-optimization"
os.environ.setdefault("OFFSHORE_MG_MAX_ITR", "1")


def main():
    notebooks = sorted(
        NOTEBOOK_DIR.glob("Offshore Microgrid Optimization - IM - GF - Day *.ipynb")
    )
    for notebook_path in notebooks:
        print(f"Running {notebook_path.name}", flush=True)
        notebook = nbformat.read(notebook_path, as_version=4)
        client = NotebookClient(
            notebook,
            timeout=7200,
            kernel_name="python3",
            resources={"metadata": {"path": str(ROOT)}},
        )
        try:
            client.execute()
        except CellExecutionError:
            nbformat.write(notebook, notebook_path)
            raise
        except Exception:
            nbformat.write(notebook, notebook_path)
            raise
        nbformat.write(notebook, notebook_path)
        print(f"Finished {notebook_path.name}", flush=True)


if __name__ == "__main__":
    main()
