from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    pinecone_api_key: str = ""
    pinecone_environment: str = "gcp-starter"
    pinecone_index_name: str = "compliance-policies"
    
    google_api_key: str = ""
    database_url: str = "sqlite+aiosqlite:///./data/compliance.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
