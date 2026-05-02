import os
import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from jobless.constants import APP_NAME
from jobless.utils import get_app_dir

APP_DIR: Path = get_app_dir(app_name=APP_NAME)
DB_URL: Path = APP_DIR / "jobs.db"
CONFIG_FILE_PATH = APP_DIR / "config.toml"


@dataclass(frozen=True, slots=True)
class Settings:
    theme: str = field(
        default="tokyo-night",
        metadata={"env": "JOBLESS_THEME"},
    )
    db_url: str = field(
        default=f"sqlite:///{DB_URL}",
        metadata={"env": "JOBLESS_DB_URL"},
    )


def load_settings(
    app_dir: Path = APP_DIR, config_path: Path = CONFIG_FILE_PATH
) -> Settings:
    # Make sure the directory exists.
    app_dir.mkdir(parents=True, exist_ok=True)
    load_dotenv()

    config_data: dict[str, Any] = {}

    if config_path.exists():
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
            if isinstance(data, dict):
                config_data.update(data)

    for f in fields(Settings):
        env_key = f.metadata.get("env")
        if not env_key:
            continue

        env_val = os.getenv(env_key)
        if env_val:
            config_data[f.name] = env_val

    return Settings(**config_data)


if __name__ == "__main__":
    settings = load_settings(APP_DIR, CONFIG_FILE_PATH)
    print(settings)
