from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    hefeng_weather_key: str = ""
    amap_key: str = ""
    amap_secret: str = ""
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    
    weather_api_timeout: int = 5000
    travel_api_timeout: int = 5000
    llm_timeout: int = 60000
    
    rate_limit_requests: int = 60
    rate_limit_period: int = 60
    
    redis_url: str = "redis://localhost:6379"
    
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
