"""Repository-relative paths used by notebooks and helper modules."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data" / "backup-artifacts"
OFFSHORE_MICROGRID_DATA_DIR = DATA_ROOT / "offshore-microgrid"
MGT_MODEL_DIR = DATA_ROOT / "mgt-model"
OUTPUT_ROOT = PROJECT_ROOT / "outputs"


def require_path(path):
    """Return a path if it exists, otherwise raise a useful setup error."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Required repository artifact is missing: {path}. "
            "Check that data/backup-artifacts has been restored before running notebooks."
        )
    return path


def output_path(*parts):
    """Create and return a path under outputs/."""
    path = OUTPUT_ROOT.joinpath(*parts)
    path.mkdir(parents=True, exist_ok=True)
    return path
