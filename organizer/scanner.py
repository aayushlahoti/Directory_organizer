from pathlib import Path


def scan_directory(path: str, recursive: bool = False) -> list[Path]:
    """
    Scans a directory and returns a list of all files.

    Args:
        path: Path to the directory to scan.
        recursive: If True, scans subdirectories as well.

    Returns:
        List of Path objects for each file found.

    Raises:
        NotADirectoryError: If the given path is not a directory.
        FileNotFoundError: If the given path does not exist.
    """
    base = Path(path).resolve()

    if not base.exists():
        raise FileNotFoundError(f"Directory not found: {base}")

    if not base.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {base}")

    pattern = "**/*" if recursive else "*"
    files = [f for f in base.glob(pattern) if f.is_file()]

    return files