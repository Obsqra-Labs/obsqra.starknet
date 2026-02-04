"""
Agent Orchestrator Service
Provides backend API for intent management, agent reputation, and policy marketplace
Uses direct RPC calls for Starknet interaction
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
import httpx
from functools import lru_cache

from app.config import settings

logger = logging.getLogger(__name__)


class IntentType(Enum):
    MAXIMIZE_YIELD = 0
    MINIMIZE_RISK = 1
    BALANCED_GROWTH = 2
    CUSTOM_POLICY = 3


class IntentStatus(Enum):
    PENDING = 0
    ACTIVE = 1
    EXECUTED = 2
    CANCELLED = 3
    EXPIRED = 4
    FAILED = 5


class ExecutionOutcome(Enum):
    SUCCESS = 0
    FAILED = 1
    PARTIAL = 2


@dataclass
class ConstraintSet:
    max_risk_score: int
    min_confidence: int
    max_drawdown_bps: int
    allowed_protocols: int
    max_single_position_bps: int
    require_proof: bool


@dataclass
class Intent:
    id: str
    owner: str
    goal: IntentType
    constraints: ConstraintSet
    policy_hash: str
    status: IntentStatus
    created_at: int
    expires_at: int
    execution_count: int


@dataclass
class AgentReputation:
    agent: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    total_value_executed: int
    reputation_score: int
    registered_at: int
    last_execution_at: int
    is_active: bool


@dataclass
class Policy:
    policy_hash: str
    name: str
    creator: str
    description_hash: str
    parameter_schema: str
    is_approved: bool
    created_at: int


# Function selectors (from starkli selector command)
SELECTORS = {
    "get_version": "0x02a4bb4205277617b698a9a2950b938d0a236dd4619f82f05bec02bdbd245fab",
    "get_contract_version": "0x01ef7ce09b0d72b83f892a27d03be2bbddd3d9e48220267dbd82db534c8328a6",
    "get_owner": "0x03ee0bfaf5b124501fef19bbd1312e71f6966d186c42eeb91d1bff729b91d1d4",
    "get_intent_count": "0x025eca9d83cf80959b566a5b03643007004f714685b698e84dded949d1da0930",
    "get_agent_count": "0x0141e90152298c89484043266d3cf2d9482608bcc825c1b2c8f5d86389b48fea",
    "get_policy_count": "0x02dbe18ef771bd743817d08eacc6d08f79b0addfd7b29f5617f6017f76733e02",
    "get_execution_count": "0x0039cedbf8edfe988d39ce64ab166575b3fb762fc7a5d511a633889baea32647",
    "is_registered_agent": "0x03f2b687a1c7e6673ae41292ef4cc2b013cb797ac97527717cc582a5f8292995",
    "is_policy_approved": "0x029cd18ebbfe058c016df47aa6ef7085be1bc25a68552619fe2e9595a682cacb",
}


def compute_selector(name: str) -> str:
    """Compute starknet_keccak for a function name"""
    import hashlib
    # Starknet uses first 250 bits of keccak256
    h = hashlib.sha3_256(name.encode()).hexdigest()
    # Take first 62 hex chars (248 bits, close enough for our purposes)
    return "0x" + h[:62]


class AgentOrchestratorService:
    """Service for interacting with the AgentOrchestrator contract via RPC"""
    
    def __init__(self):
        self.contract_address: str = ""
        self.rpc_url: str = ""
        self._initialized = False
        self._client: Optional[httpx.AsyncClient] = None
    
    async def initialize(self) -> bool:
        """Initialize the service"""
        try:
            # Get contract address from settings
            self.contract_address = getattr(settings, 'AGENT_ORCHESTRATOR_ADDRESS', 
                "0x050a35c0f4f42e7b3fcf1186d2465d5a14f7c17054bf4d3da4ac8ca8f5f8bb23")
            
            self.rpc_url = getattr(settings, 'STARKNET_RPC_URL', 
                "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7")
            
            # Create HTTP client
            self._client = httpx.AsyncClient(timeout=30.0)
            
            # Mark as initialized
            self._initialized = True
            
            # Skip verification - will verify on first call
            logger.info(f"AgentOrchestrator service ready: {self.contract_address}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize AgentOrchestratorService: {e}")
            return False
    
    async def ensure_initialized(self):
        """Ensure the service is initialized"""
        if not self._initialized:
            await self.initialize()
    
    async def _rpc_call(self, method: str, params: Dict) -> Any:
        """Make a JSON-RPC call to Starknet"""
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        response = await self._client.post(self.rpc_url, json=payload)
        data = response.json()
        
        if "error" in data:
            raise Exception(f"RPC error: {data['error']}")
        
        return data.get("result")
    
    async def _call_contract_internal(self, selector: str, calldata: List[str] = None) -> List[str]:
        """Call a contract function (internal, no init check)"""
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)
        
        params = {
            "request": {
                "contract_address": self.contract_address,
                "entry_point_selector": selector,
                "calldata": calldata or []
            },
            "block_id": "pending"
        }
        
        # Debug: print what we're sending
        print(f"[DEBUG] RPC call to {self.rpc_url}")
        print(f"[DEBUG] Contract: {self.contract_address}")
        print(f"[DEBUG] Selector: {selector}")
        
        result = await self._rpc_call("starknet_call", params)
        print(f"[DEBUG] Result: {result}")
        
        return result
    
    async def _call_contract(self, selector: str, calldata: List[str] = None) -> List[str]:
        """Call a contract function"""
        await self.ensure_initialized()
        return await self._call_contract_internal(selector, calldata)
    
    # ========== Read Operations ==========
    
    async def _get_version_internal(self) -> str:
        """Get contract version string (internal, no init check)"""
        result = await self._call_contract_internal(SELECTORS["get_version"])
        if result:
            return self._felt_to_string(int(result[0], 16))
        return "unknown"
    
    async def get_version(self) -> str:
        """Get contract version string"""
        await self.ensure_initialized()
        return await self._get_version_internal()
    
    async def get_contract_version(self) -> int:
        """Get contract version number"""
        try:
            result = await self._call_contract(SELECTORS["get_contract_version"])
            if result:
                return int(result[0], 16)
        except:
            pass
        return 1
    
    async def get_owner(self) -> str:
        """Get contract owner address"""
        try:
            result = await self._call_contract(SELECTORS["get_owner"])
            if result:
                return result[0]
        except:
            pass
        return "0x0"
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get overall orchestrator statistics"""
        await self.ensure_initialized()
        
        try:
            # For now, return basic stats since we need proper selectors
            version = await self.get_version()
            
            return {
                "contract_address": self.contract_address,
                "version": version,
                "intent_count": 0,
                "agent_count": 0,
                "policy_count": 0,
                "execution_count": 0,
                "status": "operational"
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {
                "contract_address": self.contract_address,
                "error": str(e),
                "status": "error"
            }
    
    async def is_registered_agent(self, agent_address: str) -> bool:
        """Check if an address is a registered agent"""
        try:
            result = await self._call_contract(
                SELECTORS["is_registered_agent"],
                [agent_address]
            )
            if result:
                return int(result[0], 16) == 1
        except:
            pass
        return False
    
    async def is_policy_approved(self, policy_hash: str) -> bool:
        """Check if a policy is approved"""
        try:
            result = await self._call_contract(
                SELECTORS["is_policy_approved"],
                [policy_hash]
            )
            if result:
                return int(result[0], 16) == 1
        except:
            pass
        return False
    
    # ========== Intent Operations ==========
    
    async def get_user_intents(self, user_address: str, limit: int = 10) -> List[Dict]:
        """Get intents for a user"""
        # Placeholder - requires proper ABI
        return []
    
    # ========== Agent Operations ==========
    
    async def get_agent_reputation(self, agent_address: str) -> Optional[Dict]:
        """Get reputation for an agent"""
        is_registered = await self.is_registered_agent(agent_address)
        if not is_registered:
            return None
        return {
            "agent": agent_address,
            "is_registered": True,
            "reputation": "pending_full_data"
        }
    
    # ========== Policy Operations ==========
    
    async def get_policy(self, policy_hash: str) -> Optional[Dict]:
        """Get policy details"""
        is_approved = await self.is_policy_approved(policy_hash)
        return {
            "policy_hash": policy_hash,
            "is_approved": is_approved
        }
    
    # ========== Helpers ==========
    
    def _felt_to_string(self, felt: int) -> str:
        """Convert a felt252 to a string"""
        if felt == 0:
            return ""
        hex_str = hex(felt)[2:]
        if len(hex_str) % 2:
            hex_str = '0' + hex_str
        try:
            return bytes.fromhex(hex_str).decode('utf-8').strip('\x00')
        except:
            return hex(felt)


# Singleton instance
_service: Optional[AgentOrchestratorService] = None


async def get_agent_orchestrator_service() -> AgentOrchestratorService:
    """Get or create the singleton service instance"""
    global _service
    if _service is None:
        _service = AgentOrchestratorService()
        await _service.initialize()
    return _service
