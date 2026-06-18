from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Orchestrix"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True


API_V1_PREFIX: str = "/api/v1"

model_config = SettingsConfigDict(
    env_file=".env",
    case_sensitive=True
)


settings = Settings()
