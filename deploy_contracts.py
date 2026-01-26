#!/usr/bin/env python3
"""
Starknet Contract Deployment Script
Uses starknet.py to deploy RiskEngine and StrategyRouterV2 to Sepolia testnet
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Optional

try:
    from starknet_py.net.client import Client
    from starknet_py.net.signer import KeyPair, BaseSigner
    from starknet_py.account.account import Account
    from starknet_py.contract import Contract, ContractFunction
except ImportError:
    print("ERROR: starknet.py not installed")
    print("Install with: pip install starknet-py")
    sys.exit(1)


class DeploymentConfig:
    """Configuration for testnet deployment"""
    
    # Account credentials from /root/.starknet_accounts/starknet_open_zeppelin_accounts.json
    ACCOUNT_ADDRESS = 0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d
    PRIVATE_KEY = 0x7fd44d52324945e2d9f2e62bd2dadb794e2274dbd0955251aeca6cc96153afc
    PUBLIC_KEY = 0x7bd46bce89bf8ce1b3c9fdd4eeedcf5be135f62dde4a6c71948cd50caff59ea
    
    # RPC endpoints - try each until one works
    RPC_URLS = [
        "https://sepolia.starknet.io",  # Official Starknet Sepolia RPC
        "https://starknet-sepolia.public.blastapi.io/rpc/v0_7",  # Blast (may be down)
        "https://rpc.reddio.com/starknet-sepolia",  # Community RPC
    ]
    
    # Contract paths
    RISK_ENGINE_PATH = "/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_RiskEngine.contract_class.json"
    STRATEGY_ROUTER_PATH = "/opt/obsqra.starknet/contracts/target/dev/obsqra_contracts_StrategyRouterV2.contract_class.json"
    
    # Output file for deployment info
    DEPLOYMENT_INFO = "/opt/obsqra.starknet/deployment_info.json"


class ContractDeployer:
    """Handle contract deployment to Starknet"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.account: Optional[Account] = None
        self.deployment_info = {
            "network": "sepolia",
            "account": hex(DeploymentConfig.ACCOUNT_ADDRESS),
            "timestamp": None,
            "contracts": {}
        }
    
    async def connect(self) -> bool:
        """Try to connect to a working RPC endpoint"""
        print("🔍 Trying RPC endpoints...")
        
        for rpc_url in DeploymentConfig.RPC_URLS:
            try:
                print(f"  Trying: {rpc_url}...", end=" ", flush=True)
                self.client = Client(node_url=rpc_url)
                
                # Test connectivity
                chain_id = await self.client.get_chain_id()
                print(f"✓ Connected (Chain: {chain_id})")
                
                # Setup account
                key_pair = KeyPair.from_private_key(DeploymentConfig.PRIVATE_KEY)
                self.account = Account(
                    client=self.client,
                    address=DeploymentConfig.ACCOUNT_ADDRESS,
                    key_pair=key_pair
                )
                return True
                
            except Exception as e:
                print(f"✗ Failed ({str(e)[:50]}...)")
                continue
        
        print("✗ Could not connect to any RPC endpoint")
        return False
    
    def _load_contract_class(self, path: str) -> Dict:
        """Load contract class from JSON file"""
        if not Path(path).exists():
            raise FileNotFoundError(f"Contract file not found: {path}")
        
        with open(path, 'r') as f:
            return json.load(f)
    
    async def declare_contract(self, name: str, contract_path: str) -> Optional[str]:
        """Declare a contract class"""
        try:
            print(f"\n📋 Declaring {name}...")
            print(f"   Loading from: {contract_path}")
            
            contract_class = self._load_contract_class(contract_path)
            print(f"   ✓ Loaded (type: {contract_class.get('abi_type', 'unknown')})")
            
            # Prepare declaration
            print(f"   Declaring on Sepolia...", end=" ", flush=True)
            
            # Create declare transaction
            declare_tx = await self.account.declare(
                compiled_contract=contract_class,
                compiled_contract_casm=None,
                auto_estimate=True
            )
            
            class_hash = hex(declare_tx.class_hash) if hasattr(declare_tx, 'class_hash') else hex(declare_tx.declared_class_hash)
            tx_hash = hex(declare_tx.hash)
            
            print(f"✓")
            print(f"   TX Hash: {tx_hash}")
            print(f"   Class Hash: {class_hash}")
            
            self.deployment_info["contracts"][name] = {
                "status": "declared",
                "class_hash": class_hash,
                "tx_hash": tx_hash,
                "contract_path": contract_path
            }
            
            return class_hash
            
        except Exception as e:
            print(f"\n✗ Failed to declare {name}: {str(e)}")
            self.deployment_info["contracts"][name] = {
                "status": "failed",
                "error": str(e)
            }
            return None
    
    async def deploy_all(self) -> bool:
        """Deploy all contracts"""
        print("=" * 70)
        print("STARKNET CONTRACT DEPLOYMENT")
        print("=" * 70)
        print(f"Account: {hex(DeploymentConfig.ACCOUNT_ADDRESS)}")
        print(f"Network: Sepolia Testnet")
        print()
        
        # Connect to network
        if not await self.connect():
            return False
        
        print()
        print("=" * 70)
        print("CONTRACT DECLARATIONS")
        print("=" * 70)
        
        # Declare RiskEngine
        risk_engine_hash = await self.declare_contract(
            "RiskEngine",
            DeploymentConfig.RISK_ENGINE_PATH
        )
        
        if not risk_engine_hash:
            print("\n✗ Failed to declare RiskEngine. Stopping deployment.")
            return False
        
        # Declare StrategyRouter
        strategy_router_hash = await self.declare_contract(
            "StrategyRouterV2",
            DeploymentConfig.STRATEGY_ROUTER_PATH
        )
        
        if not strategy_router_hash:
            print("\n✗ Failed to declare StrategyRouterV2. Stopping deployment.")
            return False
        
        # Save deployment info
        self._save_deployment_info()
        return True
    
    def _save_deployment_info(self):
        """Save deployment info to file"""
        try:
            from datetime import datetime
            self.deployment_info["timestamp"] = datetime.now().isoformat()
            
            with open(DeploymentConfig.DEPLOYMENT_INFO, 'w') as f:
                json.dump(self.deployment_info, f, indent=2)
            
            print(f"\n✓ Deployment info saved to: {DeploymentConfig.DEPLOYMENT_INFO}")
        except Exception as e:
            print(f"\n✗ Failed to save deployment info: {e}")


async def main():
    """Main deployment function"""
    deployer = ContractDeployer()
    
    try:
        success = await deployer.deploy_all()
        
        if success:
            print("\n" + "=" * 70)
            print("✓ DEPLOYMENT SUCCESSFUL")
            print("=" * 70)
            print("\nNext steps:")
            print("1. View deployment info: cat /opt/obsqra.starknet/deployment_info.json")
            print("2. For each contract, save the class_hash")
            print("3. Use class hashes to deploy contract instances")
            print("4. Update backend with contract addresses")
            return 0
        else:
            print("\n" + "=" * 70)
            print("✗ DEPLOYMENT FAILED")
            print("=" * 70)
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠ Deployment cancelled by user")
        return 130
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
