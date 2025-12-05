"""
Configuration for Obsqra.starknet AI Service
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Network configuration
STARKNET_NETWORK = os.getenv('STARKNET_NETWORK', 'sepolia')
STARKNET_RPC_URL = os.getenv('STARKNET_RPC_URL', 'https://starknet-sepolia.public.blastapi.io/rpc/v0_7')

# Contract addresses
RISK_ENGINE_ADDRESS = os.getenv('RISK_ENGINE_ADDRESS', '')
STRATEGY_ROUTER_ADDRESS = os.getenv('STRATEGY_ROUTER_ADDRESS', '')
DAO_CONSTRAINT_MANAGER_ADDRESS = os.getenv('DAO_CONSTRAINT_MANAGER_ADDRESS', '')

# Service configuration
AI_SERVICE_PORT = int(os.getenv('AI_SERVICE_PORT', '8000'))
AI_SERVICE_HOST = os.getenv('AI_SERVICE_HOST', 'localhost')

