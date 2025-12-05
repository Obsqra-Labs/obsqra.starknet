"""
Starknet contract client for Obsqra.starknet AI Service

Handles interactions with Cairo contracts on Starknet.
"""

from typing import Dict, Tuple, Optional
from starknet_py.contract import Contract
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.networks import TESTNET
import logging
from config import (
    STARKNET_RPC_URL,
    RISK_ENGINE_ADDRESS,
    STRATEGY_ROUTER_ADDRESS,
    DAO_CONSTRAINT_MANAGER_ADDRESS
)

logger = logging.getLogger(__name__)


class ContractClient:
    """Client for interacting with Obsqra.starknet contracts"""
    
    def __init__(self, private_key: Optional[str] = None):
        """
        Initialize contract client.
        
        Args:
            private_key: Private key for signing transactions (optional for read-only)
        """
        # Initialize provider
        self.gateway_client = GatewayClient(net=TESTNET)
        
        # Initialize account if private key provided
        if private_key:
            key_pair = KeyPair.from_private_key(int(private_key, 16))
            self.account_client = AccountClient(
                client=self.gateway_client,
                key_pair=key_pair,
                chain=StarknetChainId.TESTNET
            )
        else:
            self.account_client = None
        
        # Initialize contracts
        self.risk_engine: Optional[Contract] = None
        self.strategy_router: Optional[Contract] = None
        self.dao_constraint_manager: Optional[Contract] = None
        
    async def initialize_contracts(self):
        """Initialize contract instances"""
        try:
            if RISK_ENGINE_ADDRESS:
                self.risk_engine = await Contract.from_address(
                    address=int(RISK_ENGINE_ADDRESS, 16),
                    provider=self.gateway_client
                )
            
            if STRATEGY_ROUTER_ADDRESS:
                self.strategy_router = await Contract.from_address(
                    address=int(STRATEGY_ROUTER_ADDRESS, 16),
                    provider=self.gateway_client
                )
            
            if DAO_CONSTRAINT_MANAGER_ADDRESS:
                self.dao_constraint_manager = await Contract.from_address(
                    address=int(DAO_CONSTRAINT_MANAGER_ADDRESS, 16),
                    provider=self.gateway_client
                )
            
            logger.info("Contracts initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize contracts: {e}")
            raise
    
    async def calculate_risk_score(
        self,
        utilization: int,
        volatility: int,
        liquidity: int,
        audit_score: int,
        age_days: int
    ) -> int:
        """Calculate risk score using on-chain RiskEngine"""
        if not self.risk_engine:
            raise ValueError("RiskEngine contract not initialized")
        
        try:
            result = await self.risk_engine.functions['calculate_risk_score'].call(
                utilization, volatility, liquidity, audit_score, age_days
            )
            return result[0]  # Return first element of tuple
        except Exception as e:
            logger.error(f"Risk score calculation failed: {e}")
            raise
    
    async def calculate_allocation(
        self,
        aave_risk: int,
        lido_risk: int,
        compound_risk: int,
        aave_apy: int,
        lido_apy: int,
        compound_apy: int
    ) -> Tuple[int, int, int]:
        """Calculate allocation using on-chain RiskEngine"""
        if not self.risk_engine:
            raise ValueError("RiskEngine contract not initialized")
        
        try:
            result = await self.risk_engine.functions['calculate_allocation'].call(
                aave_risk, lido_risk, compound_risk,
                aave_apy, lido_apy, compound_apy
            )
            return (result[0], result[1], result[2])
        except Exception as e:
            logger.error(f"Allocation calculation failed: {e}")
            raise
    
    async def verify_constraints(
        self,
        aave_pct: int,
        lido_pct: int,
        compound_pct: int
    ) -> bool:
        """Verify allocation meets DAO constraints"""
        if not self.dao_constraint_manager:
            raise ValueError("DAOConstraintManager contract not initialized")
        
        try:
            result = await self.dao_constraint_manager.functions['validate_allocation'].call(
                aave_pct, lido_pct, compound_pct
            )
            return result[0]
        except Exception as e:
            logger.error(f"Constraint verification failed: {e}")
            raise
    
    async def get_allocation(self) -> Tuple[int, int, int]:
        """Get current allocation from StrategyRouter"""
        if not self.strategy_router:
            raise ValueError("StrategyRouter contract not initialized")
        
        try:
            result = await self.strategy_router.functions['get_allocation'].call()
            return (result[0], result[1], result[2])
        except Exception as e:
            logger.error(f"Failed to get allocation: {e}")
            raise
    
    async def update_allocation(
        self,
        aave_pct: int,
        lido_pct: int,
        compound_pct: int
    ) -> str:
        """Update allocation on-chain (requires account client)"""
        if not self.strategy_router:
            raise ValueError("StrategyRouter contract not initialized")
        
        if not self.account_client:
            raise ValueError("Account client not initialized (read-only mode)")
        
        try:
            # Verify allocation sums to 10000
            if aave_pct + lido_pct + compound_pct != 10000:
                raise ValueError("Allocation percentages must sum to 10000")
            
            # Call contract
            invocation = await self.strategy_router.functions['update_allocation'].invoke(
                aave_pct, lido_pct, compound_pct,
                max_fee=int(1e15)  # 0.001 ETH
            )
            
            # Wait for transaction
            await invocation.wait_for_acceptance()
            
            logger.info(f"Allocation updated: Aave={aave_pct}, Lido={lido_pct}, Compound={compound_pct}")
            return hex(invocation.hash)
        except Exception as e:
            logger.error(f"Failed to update allocation: {e}")
            raise
    
    async def get_constraints(self) -> Tuple[int, int, int, int]:
        """Get DAO constraints"""
        if not self.dao_constraint_manager:
            raise ValueError("DAOConstraintManager contract not initialized")
        
        try:
            result = await self.dao_constraint_manager.functions['get_constraints'].call()
            return (result[0], result[1], result[2], result[3])
        except Exception as e:
            logger.error(f"Failed to get constraints: {e}")
            raise

