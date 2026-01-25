"""Application Configuration"""

from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
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
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3003",
        "http://localhost:3000",
        "http://127.0.0.1:3003",
        "https://starknet.obsqra.fi",  # Production frontend
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string or list, filtering out '*'."""
        if isinstance(v, str):
            # Split comma-separated string and filter out '*'
            origins = [origin.strip() for origin in v.split(",") if origin.strip() and origin.strip() != "*"]
            return origins if origins else v.split(",")  # Return original if all were '*'
        elif isinstance(v, list):
            # Filter out '*' from list
            return [origin for origin in v if origin != "*"]
        return v
    
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
    # Optional comma-separated RPC list for failover (falls back to STARKNET_RPC_URL)
    STARKNET_RPC_URLS: str = ""
    STARKNET_RPC_RETRY_ATTEMPTS: int = 2
    STARKNET_RPC_RETRY_BACKOFF_SEC: float = 0.75
    STARKNET_NETWORK: str = "sepolia"  # 'sepolia' or 'mainnet'
    RISK_ENGINE_ADDRESS: str = "0x007c2463376a0d21dbccde4c6d59bf8b0649973ca1f88865466b58d81dcbe86d"  # v2.2 with fixed 2-protocol allocation
    STRATEGY_ROUTER_ADDRESS: str = "0x01888e3f3d6cd137e63ff1a090a1e2c9ed5754162a8d5739364aba657fab20e4"  # v2 with ETH + protocol integration + deposit function (redeployed 2025-12-09 with new class hash)
    # Read-only data RPC (defaults to STARKNET_RPC_URL if unset)
    DATA_RPC_URL: str = ""
    DATA_NETWORK: str = ""  # optional override for data network
    # Optional zkML oracle contract (Cairo demo)
    ZKML_ORACLE_ADDRESS: str = ""
    # Optional zkML proof paths (Integrity/Stone)
    ZKML_PROOF_JSON_PATH: str = ""
    ZKML_PROOF_CALLDATA_PATH: str = ""
    ZKML_PROOF_JSON_PATH_CAIRO0: str = ""
    ZKML_PROOF_JSON_PATH_CAIRO1: str = ""
    ZKML_PROOF_CALLDATA_PATH_CAIRO0: str = ""
    ZKML_PROOF_CALLDATA_PATH_CAIRO1: str = ""
    INTEGRITY_PROOF_SERIALIZER_BIN: str = ""
    # Integrity proof settings (match verify-on-starknet.sh)
    INTEGRITY_LAYOUT: str = "recursive"
    INTEGRITY_HASHER: str = "keccak_160_lsb"
    INTEGRITY_STONE_VERSION: str = "stone5"
    INTEGRITY_MEMORY_VERIFICATION: str = "strict"
    # Demo override (allow execution even if proof not verified)
    ALLOW_UNVERIFIED_EXECUTION: bool = False
    # Ekubo API pair for metrics (default: ETH/USDC on Starknet mainnet)
    EKUBO_CHAIN_ID: str = "0x534e5f4d41494e"  # SN_MAIN
    EKUBO_TOKEN_A: str = "0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"  # ETH
    EKUBO_TOKEN_B: str = "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8"  # USDC
    
    # L1 Settlement (Atlantic)
    ATLANTIC_API_KEY: str = ""  # Herodotus API key
    ATLANTIC_BASE_URL: str = "https://atlantic.api.herodotus.cloud"
    ALLOW_FAKE_FACT_HASH: bool = False  # Only set to True for local mock mode
    
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
