from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from jobless.constants import APP_NAME
from jobless.utils import get_app_dir

APP_DIR: Path = get_app_dir(app_name=APP_NAME)
DB_URL: Path = APP_DIR / "jobs.db"
CONFIG_FILE_PATH = APP_DIR / "config.toml"


class Settings(BaseSettings):
    theme: str = "tokyo-night"
    db_url: str = f"sqlite:///{DB_URL}"

    model_config = SettingsConfigDict(
        toml_file=CONFIG_FILE_PATH,
        env_prefix="JOBLESS_",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        APP_DIR.mkdir(parents=True, exist_ok=True)

        return (
            env_settings,
            TomlConfigSettingsSource(settings_cls),
        )


if __name__ == "__main__":
    print(Settings().model_dump())
