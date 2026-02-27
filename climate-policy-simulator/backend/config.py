from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    k2_api_base_url: str = "https://api.mbzuai.ac.ae/v1"
    k2_api_key: str = "changeme"
    k2_model_name: str = "k2-think-v2"

    chroma_persist_dir: str = "./chroma_db"
    log_level: str = "INFO"


settings = Settings()
