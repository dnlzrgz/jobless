from importlib.metadata import version
from pathlib import Path

from jobless.utils import get_app_dir

APP_NAME = "jobless"
APP_VERSION = version(APP_NAME)
APP_DIR: Path = get_app_dir(app_name=APP_NAME)
DB_URL: Path = APP_DIR / "jobs.db"
CONFIG_FILE_PATH = APP_DIR / "config.toml"
