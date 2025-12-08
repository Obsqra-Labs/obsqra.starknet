#!/usr/bin/env python3
"""
Local Deployment Script for Obsqra Starknet Contracts

Deploys all contracts to a local Katana/Devnet instance.
Usage: python3 deploy_local.py [--rpc-url URL] [--account ACCOUNT]
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.net.models import StarknetChainId


class LocalDeployment:
    def __init__(self, rpc_url: str = "http://localhost:5050"):
        self.rpc_url = rpc_url
        self.client = FullNodeClient(node_url=rpc_url)
        self.contracts_dir = Path(__file__).parent.parent / "contracts" / "target" / "dev"
        
        # Katana default test account
        self.account_address = 0x1
        self.private_key = 0x1  # Katana default private key
        
    async def connect(self) -> bool:
        """Check connection to local node"""
        try:
            block = await self.client.get_block_number()
            print(f"✓ Connected to Starknet node (block {block})")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to {self.rpc_url}: {e}")
            return False
    
    async def read_sierra_class(self, contract_name: str) -> dict:
        """Read Sierra contract class from JSON"""
        file_path = self.contracts_dir / f"obsqra_contracts_{contract_name}.contract_class.json"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Contract not found: {file_path}")
        
        with open(file_path, "r") as f:
            return json.load(f)
    
    async def deploy_risk_engine(self, account: Account) -> str:
        """Deploy RiskEngine contract"""
        print("\n1. Deploying RiskEngine...")
        
        sierra_class = await self.read_sierra_class("RiskEngine")
        owner = 0x123  # Local test address
        
        # Create contract instance and deploy
        from starknet_py.net.udc_deployer.deployer import Deployer
        
        deployer = Deployer()
        deploy_result = await deployer.deploy_contract(
            account=account,
            class_hash=sierra_class,
            constructor_args=[owner],
            unique=False
        )
        
        contract_address = deploy_result.deployed_address
        print(f"   ✓ RiskEngine deployed at: {hex(contract_address)}")
        
        return hex(contract_address)
    
    async def deploy_dao_manager(self, account: Account) -> str:
        """Deploy DAOConstraintManager contract"""
        print("\n2. Deploying DAOConstraintManager...")
        
        sierra_class = await self.read_sierra_class("DAOConstraintManager")
        owner = 0x123
        max_single = 6000
        min_diversification = 3
        max_volatility = 5000
        min_liquidity = 1000000
        
        from starknet_py.net.udc_deployer.deployer import Deployer
        
        deployer = Deployer()
        deploy_result = await deployer.deploy_contract(
            account=account,
            class_hash=sierra_class,
            constructor_args=[
                owner,
                max_single,
                min_diversification,
                max_volatility,
                min_liquidity
            ],
            unique=False
        )
        
        contract_address = deploy_result.deployed_address
        print(f"   ✓ DAOConstraintManager deployed at: {hex(contract_address)}")
        
        return hex(contract_address)
    
    async def deploy_strategy_router(self, account: Account, risk_engine_addr: str) -> str:
        """Deploy StrategyRouter contract"""
        print("\n3. Deploying StrategyRouter...")
        
        sierra_class = await self.read_sierra_class("StrategyRouter")
        owner = 0x123
        aave = 0x456
        lido = 0x789
        compound = 0xabc
        risk_engine = int(risk_engine_addr, 16)
        
        from starknet_py.net.udc_deployer.deployer import Deployer
        
        deployer = Deployer()
        deploy_result = await deployer.deploy_contract(
            account=account,
            class_hash=sierra_class,
            constructor_args=[
                owner,
                aave,
                lido,
                compound,
                risk_engine
            ],
            unique=False
        )
        
        contract_address = deploy_result.deployed_address
        print(f"   ✓ StrategyRouter deployed at: {hex(contract_address)}")
        
        return hex(contract_address)
    
    async def save_addresses(self, addresses: dict):
        """Save contract addresses to .env.local"""
        env_content = """# Local Deployment Addresses
RPC_URL=http://localhost:5050
ACCOUNT=katana_0

# Contract Addresses
RISK_ENGINE_ADDRESS={risk_engine}
DAO_MANAGER_ADDRESS={dao_manager}
STRATEGY_ROUTER_ADDRESS={strategy_router}

# Test Data
OWNER_ADDRESS=0x123
AAVE_ADDRESS=0x456
LIDO_ADDRESS=0x789
COMPOUND_ADDRESS=0xabc
""".format(**addresses)
        
        env_file = Path(".env.local")
        env_file.write_text(env_content)
        print(f"\n✓ Addresses saved to {env_file}")
    
    async def deploy_all(self):
        """Deploy all contracts"""
        # Check connection
        if not await self.connect():
            sys.exit(1)
        
        print("\n" + "="*50)
        print("Obsqra Local Deployment")
        print("="*50)
        
        try:
            # Create account
            signer = StarkCurveSigner(
                public_key=self.account_address,
                private_key=self.private_key
            )
            account = Account(
                client=self.client,
                address=self.account_address,
                signer=signer,
                chain=StarknetChainId.TESTNET
            )
            
            # Deploy contracts
            risk_engine = await self.deploy_risk_engine(account)
            dao_manager = await self.deploy_dao_manager(account)
            strategy_router = await self.deploy_strategy_router(account, risk_engine)
            
            # Save addresses
            await self.save_addresses({
                "risk_engine": risk_engine,
                "dao_manager": dao_manager,
                "strategy_router": strategy_router
            })
            
            print("\n" + "="*50)
            print("DEPLOYMENT SUMMARY")
            print("="*50)
            print(f"Risk Engine:            {risk_engine}")
            print(f"DAO Manager:            {dao_manager}")
            print(f"Strategy Router:        {strategy_router}")
            print("\n✓ All contracts deployed successfully!")
            print("\nNext steps:")
            print("1. Start frontend: cd frontend && npm run dev")
            print("2. Visit http://localhost:3000")
            print("3. Test with local contracts")
            
        except Exception as e:
            print(f"\n✗ Deployment failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


async def main():
    deployment = LocalDeployment()
    await deployment.deploy_all()


if __name__ == "__main__":
    asyncio.run(main())

