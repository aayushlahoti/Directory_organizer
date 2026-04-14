import shutil
import json
from pathlib import Path
from datetime import datetime


LOG_FILE = "undo_log.json"


def move_file(file: Path, destination_folder: Path, dry_run: bool = False) -> None:
    """
    Moves a file to the destination folder safely.
    If a file with the same name already exists, it appends a counter suffix.

    Args:
        file: Source file Path.
        destination_folder: Target folder Path.
        dry_run: If True, only prints what would happen without moving.
    """
    destination_folder.mkdir(parents=True, exist_ok=True)
    dest = destination_folder / file.name

    # Handle filename conflicts by appending a counter
    if dest.exists() and dest.resolve() != file.resolve():
        counter = 1
        stem = file.stem
        suffix = file.suffix
        while dest.exists():
            dest = destination_folder / f"{stem}_{counter}{suffix}"
            counter += 1

    if dry_run:
        return  # Caller handles printing for dry run

    shutil.move(str(file), str(dest))
    _log_move(str(file), str(dest))


def _log_move(src: str, dest: str) -> None:
    """Appends a move entry to the undo log."""
    log = _load_log()
    log.append({
        "src": src,
        "dest": dest,
        "time": str(datetime.now())
    })
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def _load_log() -> list:
    """Loads the undo log from disk. Returns empty list if not found."""
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def undo_last(dry_run: bool = False) -> list[dict]:
    """
    Reverses all moves from the last organizer run.

    Args:
        dry_run: If True, only returns what would be undone without moving.

    Returns:
        List of dicts with 'src' and 'dest' showing what was (or would be) undone.
    """
    log = _load_log()

    if not log:
        return []

    results = []

    for entry in reversed(log):
        src = entry["src"]
        dest = entry["dest"]
        result = {"src": src, "dest": dest, "status": "ok"}

        if not dry_run:
            dest_path = Path(dest)
            src_path = Path(src)

            if not dest_path.exists():
                result["status"] = "missing"
            else:
                try:
                    src_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(dest_path), str(src_path))
                except Exception as e:
                    result["status"] = f"error: {e}"

        results.append(result)

    # Clear the log after undo
    if not dry_run:
        Path(LOG_FILE).unlink(missing_ok=True)

    return results