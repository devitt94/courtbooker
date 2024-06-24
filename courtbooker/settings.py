import json

from pydantic import BaseModel, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DataSourceSettings(BaseModel):
    BASE_URL: str
    VENUES: list[str] = []
    LOOK_AHEAD_DAYS: int = 7

    @validator("VENUES", pre=True)
    def validate(cls, val):
        if isinstance(val, list):
            return val
        return json.loads(val)

    def __hash__(self) -> int:
        return super().__hash__()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    DEBUG: bool = False

    CLUBSPARK: DataSourceSettings
    BETTER: DataSourceSettings

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int

    REFRESH_COOLDOWN_MINUTES: int = 60

    @property
    def data_sources(self) -> list[DataSourceSettings]:
        return {
            "better": self.BETTER,
            "clubspark": self.CLUBSPARK,
        }

    @property
    def POSTGRES_CONNECTION_STRING(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@postgres:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


app_settings = Settings()
