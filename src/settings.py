import json

from pydantic import BaseModel, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DataSourceSettings(BaseModel):
    BASE_URL: str
    VENUES: list[str]
    LOOK_AHEAD_DAYS: int

    @validator("VENUES", pre=True)
    def validate(cls, val):
        return json.loads(val)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    DEBUG: bool = False

    SENDER_EMAIL: str
    SENDER_EMAIL_PASSWORD: str
    RECEIVER_EMAILS: list[str]
    EMAIL_SUBJECT: str

    SMTP_SERVER: str
    SMTP_PORT: int

    CLUBSPARK: DataSourceSettings
    BETTER: DataSourceSettings


settings = Settings()
