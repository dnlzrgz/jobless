import os
import sys
from pathlib import Path


from jobless.constants import APP_NAME


def get_app_dir(app_name: str) -> Path:
    """
    Returns the standard OS-specific config directory.
    Windows: %APPDATA%/app_slug
    macOS: ~/Library/Application Support/app_name
    Linux: XDG_CONFIG_HOME/slug-name or ~/.config/app_slug
    """

    app_slug = APP_NAME.lower().replace(" ", "-")

    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", Path.home()))
        return base / app_slug

    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support" / APP_NAME

    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg_config) if xdg_config else Path.home() / ".config"
    return base / app_slug
