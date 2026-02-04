"""Application Configuration"""

from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
import os

# Repo root (backend/app/config.py -> app -> backend -> root) for optional .env.sepolia
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_SEPOLIA = _REPO_ROOT / ".env.sepolia"


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001
    API_BASE_URL: str = "http://localhost:8001"
    
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
        "http://localhost:3004",
        "http://localhost:3000",
        "http://127.0.0.1:3003",
        "http://127.0.0.1:3004",
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
    STARKNET_RPC_URL: str = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
    # Optional comma-separated RPC list for failover (falls back to STARKNET_RPC_URL)
    STARKNET_RPC_URLS: str = ""
    STARKNET_RPC_RETRY_ATTEMPTS: int = 3
    STARKNET_RPC_RETRY_BACKOFF_SEC: float = 0.75
    STARKNET_MAX_FEE_WEI: int = 20000000000000000  # 0.02 STRK default
    STARKNET_NETWORK: str = "sepolia"  # 'sepolia' or 'mainnet'
    RISK_ENGINE_ADDRESS: str = "0x052fe4c3f3913f6be76677104980bff78d224d5760b91f02700e8c8275ac6e68"  # v4 Stage 3A (parameterized model) - Jan 2026 deployment
    STRATEGY_ROUTER_ADDRESS: str = "0x07ec6aa6f5499e9490cce33152c9f9058f18e90d353032fcb3ca1bfe30c98c73"  # v3.5 (proof-gated risk engine)
    AGENT_ORCHESTRATOR_ADDRESS: str = "0x050a35c0f4f42e7b3fcf1186d2465d5a14f7c17054bf4d3da4ac8ca8f5f8bb23"  # Stage 5 Agent Orchestrator
    # Read-only data RPC (defaults to STARKNET_RPC_URL if unset)
    DATA_RPC_URL: str = ""
    DATA_NETWORK: str = ""  # optional override for data network
    # Optional zkML oracle contract (Cairo demo)
    ZKML_ORACLE_ADDRESS: str = ""
    # Model Registry (zkML provenance)
    MODEL_REGISTRY_ADDRESS: str = "0x06ab2595007be01ffb7e51bd28339f870be36402eed9034b109fd479e7469adc"  # Sepolia
    MODEL_REGISTRY_ADMIN_KEY: str = ""
    # Optional zkML proof paths (Integrity/Stone)
    ZKML_PROOF_JSON_PATH: str = ""
    ZKML_PROOF_CALLDATA_PATH: str = ""
    ZKML_PROOF_JSON_PATH_CAIRO0: str = ""
    ZKML_PROOF_JSON_PATH_CAIRO1: str = ""
    ZKML_PROOF_CALLDATA_PATH_CAIRO0: str = ""
    ZKML_PROOF_CALLDATA_PATH_CAIRO1: str = ""
    INTEGRITY_PROOF_SERIALIZER_BIN: str = ""
    # Integrity proof settings (match verify-on-starknet.sh)
    # RESOLVED: Stone v3 (1414a545...) generates stone6 proofs, not stone5.
    # Using stone6 to match Stone v3 behavior (includes n_verifier_friendly_commitment_layers in hash).
    # Both stone5 and stone6 verifiers are registered in public FactRegistry.
    INTEGRITY_LAYOUT: str = "recursive"  # Canonical Integrity layout
    INTEGRITY_HASHER: str = "keccak_160_lsb"
    INTEGRITY_STONE_VERSION: str = "stone6"  # CONFIRMED: Stone v3 (1414a545...) generates stone6 proofs
    INTEGRITY_MEMORY_VERIFICATION: str = "strict"
    # Timeout for Cairo execution (increased for recursive layout)
    INTEGRITY_CAIRO_TIMEOUT: int = 300  # 5 minutes (was 120s)
    # Demo override (allow execution even if proof not verified)
    ALLOW_UNVERIFIED_EXECUTION: bool = False
    # Ekubo API pair for metrics (default: ETH/USDC on Starknet mainnet)
    EKUBO_CHAIN_ID: str = "0x534e5f4d41494e"  # SN_MAIN
    EKUBO_TOKEN_A: str = "0x49d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7"  # ETH
    EKUBO_TOKEN_B: str = "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8"  # USDC
    
    # L1 Settlement (Atlantic)
    ATLANTIC_API_KEY: str = ""  # Herodotus API key
    ATLANTIC_BASE_URL: str = "https://atlantic.api.herodotus.cloud"
    ALLOW_FAKE_FACT_HASH: bool = False  # DEPRECATED: Always False in strict Stone-only mode. No fake fact hashes allowed.
    
    # Backend Wallet (for automated execution)
    BACKEND_WALLET_ADDRESS: str = ""  # Set in .env
    BACKEND_WALLET_PRIVATE_KEY: str = ""  # Set in .env - KEEP SECRET!
    
    # Stage 3A: Parameterized model (on-chain weights)
    PARAMETERIZED_MODEL_ENABLED: bool = True
    MODEL_PARAMS_TABLE: str = "model_parameters"

    # ML Models
    MODEL_VERSION: str = "v1"
    PREDICTION_WINDOW_DAYS: int = 7
    BACKTEST_WINDOW_DAYS: int = 90
    REBALANCE_CHECK_INTERVAL_HOURS: int = 24
    
    # Monitoring
    SENTRY_DSN: str = ""
    
    class Config:
        # Load backend/.env; also repo-root .env.sepolia if present (e.g. Alchemy RPC for deploys)
        env_file = [".env", str(_ENV_SEPOLIA)] if _ENV_SEPOLIA.exists() else ".env"
        case_sensitive = True
        extra = "ignore"  # Allow .env.sepolia to have extra vars (e.g. NETWORK, DEPLOYER_ADDRESS)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
