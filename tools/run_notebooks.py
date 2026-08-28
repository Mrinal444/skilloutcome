"""Execute the workflow notebook."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "skilloutcome_workflow.ipynb"


def main() -> None:
    command = [sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute", str(NOTEBOOK), "--output", "skilloutcome_workflow-executed.ipynb", "--ExecutePreprocessor.timeout=120"]
    subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
