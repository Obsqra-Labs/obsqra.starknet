"""
Protocol monitoring service for Obsqra.starknet
"""

import asyncio
import logging
from typing import Dict, Optional, Tuple
from config import STARKNET_RPC_URL, RISK_ENGINE_ADDRESS, STRATEGY_ROUTER_ADDRESS
from risk_model import RiskModel
from contract_client import ContractClient

logger = logging.getLogger(__name__)

class ProtocolMonitor:
    """Monitor DeFi protocols and trigger rebalances"""
    
    def __init__(self, contract_client: Optional[ContractClient] = None):
        self.risk_model = RiskModel()
        self.contract_client = contract_client
        self.protocol_data: Dict[str, Dict] = {}
        self.last_rebalance_block = 0
        self.rebalance_cooldown = 100  # blocks
        
    async def fetch_protocol_data(self, protocol_name: str) -> Dict:
        """Fetch current protocol data"""
        # TODO: Implement actual data fetching from Starknet protocols
        # This is a placeholder
        return {
            "utilization": 5000,  # 50%
            "volatility": 2000,   # 20%
            "liquidity": 0,       # Very High
            "audit_score": 95,
            "age_days": 1000,
            "apy": 300,          # 3.00% in basis points
        }
    
    async def should_rebalance(self, current_block: int) -> bool:
        """Check if rebalancing is needed"""
        # Check cooldown
        if current_block - self.last_rebalance_block < self.rebalance_cooldown:
            return False
        
        # TODO: Check allocation drift, risk changes, APY differentials
        # For now, return False
        return False
    
    async def calculate_optimal_allocation(self) -> Dict[str, int]:
        """Calculate optimal allocation based on risk scores"""
        # Fetch data for all protocols
        aave_data = await self.fetch_protocol_data("aave")
        lido_data = await self.fetch_protocol_data("lido")
        compound_data = await self.fetch_protocol_data("compound")
        
        # Calculate risk scores (use on-chain if available, else off-chain)
        if self.contract_client:
            try:
                aave_risk = await self.contract_client.calculate_risk_score(
                    aave_data["utilization"],
                    aave_data["volatility"],
                    aave_data["liquidity"],
                    aave_data["audit_score"],
                    aave_data["age_days"]
                )
                lido_risk = await self.contract_client.calculate_risk_score(
                    lido_data["utilization"],
                    lido_data["volatility"],
                    lido_data["liquidity"],
                    lido_data["audit_score"],
                    lido_data["age_days"]
                )
                compound_risk = await self.contract_client.calculate_risk_score(
                    compound_data["utilization"],
                    compound_data["volatility"],
                    compound_data["liquidity"],
                    compound_data["audit_score"],
                    compound_data["age_days"]
                )
            except Exception as e:
                logger.warning(f"On-chain risk calculation failed, using off-chain: {e}")
                aave_risk, _, _ = self.risk_model.get_risk_score("aave")
                lido_risk, _, _ = self.risk_model.get_risk_score("lido")
                compound_risk, _, _ = self.risk_model.get_risk_score("compound")
        else:
            aave_risk, _, _ = self.risk_model.get_risk_score("aave")
            lido_risk, _, _ = self.risk_model.get_risk_score("lido")
            compound_risk, _, _ = self.risk_model.get_risk_score("compound")
        
        # Calculate allocation (use on-chain if available)
        if self.contract_client:
            try:
                aave_pct, lido_pct, compound_pct = await self.contract_client.calculate_allocation(
                    aave_risk, lido_risk, compound_risk,
                    aave_data["apy"], lido_data["apy"], compound_data["apy"]
                )
                return {
                    "aave": aave_pct,
                    "lido": lido_pct,
                    "compound": compound_pct,
                }
            except Exception as e:
                logger.warning(f"On-chain allocation calculation failed, using off-chain: {e}")
        
        # Fallback to off-chain calculation
        aave_score = aave_data["apy"] / (aave_risk + 1)
        lido_score = lido_data["apy"] / (lido_risk + 1)
        compound_score = compound_data["apy"] / (compound_risk + 1)
        
        total_score = aave_score + lido_score + compound_score
        
        # Calculate percentages (basis points)
        aave_pct = int((aave_score / total_score) * 10000)
        lido_pct = int((lido_score / total_score) * 10000)
        compound_pct = 10000 - aave_pct - lido_pct
        
        return {
            "aave": aave_pct,
            "lido": lido_pct,
            "compound": compound_pct,
        }
    
    async def trigger_rebalance(self) -> Dict[str, int]:
        """Trigger on-chain rebalancing"""
        try:
            # Calculate optimal allocation
            allocation = await self.calculate_optimal_allocation()
            
            # Verify constraints if contract client available
            if self.contract_client:
                try:
                    is_valid = await self.contract_client.verify_constraints(
                        allocation["aave"],
                        allocation["lido"],
                        allocation["compound"]
                    )
                    
                    if not is_valid:
                        logger.warning("Allocation failed constraint validation")
                        return allocation  # Return but don't update
                    
                    # Update allocation on-chain
                    tx_hash = await self.contract_client.update_allocation(
                        allocation["aave"],
                        allocation["lido"],
                        allocation["compound"]
                    )
                    logger.info(f"Rebalancing executed on-chain: TX={tx_hash}")
                except Exception as e:
                    logger.error(f"On-chain rebalancing failed: {e}")
                    # Return allocation anyway for logging
            else:
                logger.info("Contract client not available, skipping on-chain update")
            
            logger.info(f"Rebalancing triggered: {allocation}")
            return allocation
        except Exception as e:
            logger.error(f"Rebalancing failed: {e}")
            raise
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Starting protocol monitor...")
        
        while True:
            try:
                # TODO: Get current block from Starknet
                current_block = 0  # Placeholder
                
                if await self.should_rebalance(current_block):
                    await self.trigger_rebalance()
                    self.last_rebalance_block = current_block
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                await asyncio.sleep(60)

async def main():
    """Main entry point"""
    monitor = ProtocolMonitor()
    await monitor.monitor_loop()

if __name__ == '__main__':
    asyncio.run(main())


