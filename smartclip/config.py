from pathlib import Path
import os
RETENTION_SECONDS = 72 * 60 * 60
def data_dir():
    path = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share")) / "SmartClipboardManager"
    path.mkdir(parents=True, exist_ok=True)
    return path
def database_path():
    return data_dir() / "clipboard.db"
