import os
from pathlib import Path


def get_data_path(app_name: str, filename: str) -> Path:
    if os.name == "nt":  # Windows
        base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:  # POSIX
        base = Path.home() / ".local" / "share"

    path = base / app_name
    path.mkdir(parents=True, exist_ok=True)
    return path / filename
