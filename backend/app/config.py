"""Application Configuration"""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001
    API_BASE_URL: str = "http://localhost:8000"
    
    # Database
    DATABASE_URL: str = "postgresql://obsqra:obsqra@localhost:5432/obsqra_db"
    DB_ECHO: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3003"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3003",
        "http://localhost:3000",
        "http://127.0.0.1:3003",
    ]
    
    # Trusted Hosts (for TrustedHostMiddleware)
    # In development, allow all hosts; in production, specify exact hosts
    TRUSTED_HOSTS: List[str] = ["*"]  # "*" allows all hosts, or specify ["localhost", "127.0.0.1", "yourdomain.com"]
    
    # Email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@obsqra.io"
    
    # Starknet
    STARKNET_RPC_URL: str = "https://starknet-sepolia-rpc.publicnode.com"
    RISK_ENGINE_ADDRESS: str = "0x0751c85290c660d738236a12bb362bf64c0a8ef4b1a9cc05dc7000d14fd44d31"  # v2 with orchestration
    STRATEGY_ROUTER_ADDRESS: str = "0x0539d5611c6158a4234f7c4e8e7fe50af7b9502314ca95409f5106ee2f6741d6"  # v2 with deposit/withdraw
    
    # ML Models
    MODEL_VERSION: str = "v1"
    PREDICTION_WINDOW_DAYS: int = 7
    BACKTEST_WINDOW_DAYS: int = 90
    REBALANCE_CHECK_INTERVAL_HOURS: int = 24
    
    # Monitoring
    SENTRY_DSN: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

