from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application settings
    app_name: str = "FastAPI Boilerplate"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    
    # CORS settings
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # API Keys and External Services
    huggingface_api_key: str = ""
    zendesk_api_key: str = ""
    zendesk_domain: str = ""
    zendesk_email: str = ""
    azure_openai_api_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings() 