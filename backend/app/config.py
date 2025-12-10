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
    RISK_ENGINE_ADDRESS: str = "0x007c2463376a0d21dbccde4c6d59bf8b0649973ca1f88865466b58d81dcbe86d"  # v2.2 with fixed 2-protocol allocation
    STRATEGY_ROUTER_ADDRESS: str = "0x01888e3f3d6cd137e63ff1a090a1e2c9ed5754162a8d5739364aba657fab20e4"  # v2 with ETH + protocol integration + deposit function (redeployed 2025-12-09 with new class hash)
    
    # Backend Wallet (for automated execution)
    BACKEND_WALLET_ADDRESS: str = ""  # Set in .env
    BACKEND_WALLET_PRIVATE_KEY: str = ""  # Set in .env - KEEP SECRET!
    
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

