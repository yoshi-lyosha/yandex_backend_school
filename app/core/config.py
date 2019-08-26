from pydantic import BaseSettings


class Settings(BaseSettings):
    server_name: str = None
    server_host: str = None
    server_port: int = None

    database_url = "sqlite:///./app.db"

    class Config:
        env_prefix = ""
        case_insensitive = True


config = Settings()
