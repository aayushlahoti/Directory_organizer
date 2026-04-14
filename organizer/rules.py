from pathlib import Path
from datetime import datetime
import yaml


def load_config(config_path: str = "config.yaml") -> dict:
    """
    Loads sorting rules from a YAML config file.

    Args:
        config_path: Path to the YAML config file.

    Returns:
        Parsed config as a dict.

    Raises:
        FileNotFoundError: If config file doesn't exist.
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def classify_by_type(file: Path, rules: dict) -> str:
    """
    Classifies a file by its extension.

    Args:
        file: Path object of the file.
        rules: The full rules dict from config (config["rules"]).

    Returns:
        Folder name string like 'Images', 'Documents', etc.
    """
    ext = file.suffix.lower()
    type_rules = rules.get("type", {})

    for folder, extensions in type_rules.items():
        if ext in extensions:
            return folder

    return "Others"


def classify_by_size(file: Path, rules: dict) -> str:
    """
    Classifies a file by its size in bytes.

    Args:
        file: Path object of the file.
        rules: The full rules dict from config (config["rules"]).

    Returns:
        Folder name string like 'Small', 'Medium', 'Large', 'Huge'.
    """
    try:
        size = file.stat().st_size
    except OSError:
        return "Unknown"

    size_rules = rules.get("size", {})

    for folder, bounds in size_rules.items():
        low = bounds[0]
        high = bounds[1]  # Can be None for the last bucket (no upper limit)

        if high is None:
            if size >= low:
                return folder
        else:
            if low <= size < high:
                return folder

    return "Others"


def classify_by_date(file: Path, rules: dict) -> str:
    """
    Classifies a file by its last modified date.

    Args:
        file: Path object of the file.
        rules: The full rules dict from config (config["rules"]).

    Returns:
        Folder name string like '2025-01', '2024-12', etc.
    """
    try:
        mtime = file.stat().st_mtime
    except OSError:
        return "Unknown"

    dt = datetime.fromtimestamp(mtime)
    date_format = rules.get("date", {}).get("format", "%Y-%m")

    return dt.strftime(date_format)