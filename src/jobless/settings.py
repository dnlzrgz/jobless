import os
import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Self

from dotenv import load_dotenv

from jobless.constants import APP_NAME
from jobless.utils import get_app_dir

APP_DIR: Path = get_app_dir(app_name=APP_NAME)
DB_URL: Path = APP_DIR / "jobs.db"
CONFIG_FILE_PATH = APP_DIR / "config.toml"


@dataclass(frozen=True)
class Settings:
    theme: str = field(
        default="tokyo-night",
        metadata={"env": "JOBLESS_THEME"},
    )
    db_url: str = field(
        default=f"sqlite:///{DB_URL}",
        metadata={"env": "JOBLESS_DB_URL"},
    )

    @classmethod
    def load(cls) -> Self:
        # Make sure the directory exists.
        APP_DIR.mkdir(parents=True, exist_ok=True)

        load_dotenv()
        config_data: dict[str, Any] = {}

        if CONFIG_FILE_PATH.exists():
            with open(CONFIG_FILE_PATH, "rb") as f:
                config_data.update(tomllib.load(f))

        for f in fields(cls):
            env_key = f.metadata.get("env")
            if not env_key:
                continue

            env_val = os.getenv(env_key)
            if env_val:
                config_data[f.name] = env_val

        return cls(**config_data)


if __name__ == "__main__":
    print(Settings.load())
