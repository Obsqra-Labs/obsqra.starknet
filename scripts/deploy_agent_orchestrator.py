#!/usr/bin/env python3
"""
Deploy AgentOrchestrator contract to Starknet Sepolia
"""

import asyncio
import os
import json
from pathlib import Path
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.account.account import Account
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.models import StarknetChainId
from starknet_py.contract import Contract
from starknet_py.common import create_sierra_compiled_contract


# Configuration
RPC_URL = "https://starknet-sepolia.g.alchemy.com/v2/EvhYN6geLrdvbYHVRgPJ7"
CHAIN_ID = StarknetChainId.SEPOLIA

# Account details from existing setup
ACCOUNT_ADDRESS = 0x05fe812551bec726f1bf5026d5fb88f06ed411a753fb4468f9e19ebf8ced1b3d

# Contract paths
CONTRACTS_DIR = Path(__file__).parent.parent / "contracts"
SIERRA_PATH = CONTRACTS_DIR / "target/dev/obsqra_contracts_AgentOrchestrator.contract_class.json"
CASM_PATH = CONTRACTS_DIR / "target/dev/obsqra_contracts_AgentOrchestrator.compiled_contract_class.json"


async def main():
    print("=" * 50)
    print(" DEPLOYING AGENT ORCHESTRATOR")
    print("=" * 50)
    
    # Get private key from environment
    private_key = os.environ.get("STARKNET_PRIVATE_KEY")
    if not private_key:
        print("\nERROR: STARKNET_PRIVATE_KEY environment variable not set")
        print("\nTo get your private key, you need to know your keystore password.")
        print("You can export from keystore using:")
        print("  starkli signer keystore inspect /root/.starkli-wallets/deployer/keystore.json")
        print("\nOr set it manually:")
        print("  export STARKNET_PRIVATE_KEY=0x...")
        return
    
    # Parse private key
    if private_key.startswith("0x"):
        private_key = int(private_key, 16)
    else:
        private_key = int(private_key)
    
    print(f"\n1. Connecting to Sepolia...")
    client = FullNodeClient(node_url=RPC_URL)
    
    # Create account
    key_pair = KeyPair.from_private_key(private_key)
    account = Account(
        client=client,
        address=ACCOUNT_ADDRESS,
        key_pair=key_pair,
        chain=CHAIN_ID
    )
    
    print(f"   Account: {hex(account.address)}")
    
    # Check account balance
    balance = await account.get_balance()
    print(f"   Balance: {balance / 1e18:.6f} ETH")
    
    if balance < 0.001 * 1e18:
        print("\nERROR: Insufficient balance. Need at least 0.001 ETH for deployment.")
        return
    
    # Load contract
    print(f"\n2. Loading contract...")
    
    if not SIERRA_PATH.exists():
        print(f"\nERROR: Sierra file not found: {SIERRA_PATH}")
        print("Run 'scarb build' in the contracts directory first.")
        return
    
    if not CASM_PATH.exists():
        print(f"\nERROR: CASM file not found: {CASM_PATH}")
        print("Run 'scarb build' in the contracts directory first.")
        return
    
    with open(SIERRA_PATH, "r") as f:
        sierra_content = f.read()
    
    with open(CASM_PATH, "r") as f:
        casm_content = f.read()
    
    print(f"   Sierra: {SIERRA_PATH}")
    print(f"   CASM: {CASM_PATH}")
    
    # Declare contract
    print(f"\n3. Declaring contract...")
    
    try:
        declare_result = await Contract.declare_v3(
            account=account,
            compiled_contract=sierra_content,
            compiled_contract_casm=casm_content,
            auto_estimate=True
        )
        
        await declare_result.wait_for_acceptance()
        class_hash = declare_result.class_hash
        print(f"   Class Hash: {hex(class_hash)}")
        print(f"   Tx Hash: {hex(declare_result.hash)}")
        
    except Exception as e:
        if "is already declared" in str(e) or "StarknetErrorCode.CLASS_ALREADY_DECLARED" in str(e):
            # Try to get class hash from compiled contract
            sierra_json = json.loads(sierra_content)
            # Use a different method to get class hash if already declared
            print("   Contract already declared, getting existing class hash...")
            # Calculate class hash locally
            from starknet_py.hash.class_hash import compute_sierra_class_hash
            class_hash = compute_sierra_class_hash(json.loads(sierra_content))
            print(f"   Existing Class Hash: {hex(class_hash)}")
        else:
            print(f"\nERROR declaring contract: {e}")
            return
    
    # Deploy contract
    print(f"\n4. Deploying contract with owner: {hex(ACCOUNT_ADDRESS)}")
    
    try:
        deploy_result = await Contract.deploy_contract_v3(
            account=account,
            class_hash=class_hash,
            constructor_args={"owner": ACCOUNT_ADDRESS},
            auto_estimate=True
        )
        
        await deploy_result.wait_for_acceptance()
        contract_address = deploy_result.deployed_contract.address
        print(f"   Contract Address: {hex(contract_address)}")
        print(f"   Tx Hash: {hex(deploy_result.hash)}")
        
    except Exception as e:
        print(f"\nERROR deploying contract: {e}")
        return
    
    # Save deployment info
    print(f"\n5. Saving deployment info...")
    
    deploy_info = {
        "class_hash": hex(class_hash),
        "contract_address": hex(contract_address),
        "owner": hex(ACCOUNT_ADDRESS),
        "network": "sepolia"
    }
    
    deploy_file = Path(__file__).parent.parent / ".agent_orchestrator.deployed"
    with open(deploy_file, "w") as f:
        f.write(f"AGENT_ORCHESTRATOR_CLASS_HASH={hex(class_hash)}\n")
        f.write(f"AGENT_ORCHESTRATOR_ADDRESS={hex(contract_address)}\n")
        f.write(f"OWNER={hex(ACCOUNT_ADDRESS)}\n")
    
    print(f"   Saved to: {deploy_file}")
    
    # Final summary
    print("\n" + "=" * 50)
    print(" DEPLOYMENT COMPLETE")
    print("=" * 50)
    print(f"\nClass Hash:      {hex(class_hash)}")
    print(f"Contract Address: {hex(contract_address)}")
    print(f"\nAdd to frontend/.env.local:")
    print(f"NEXT_PUBLIC_AGENT_ORCHESTRATOR_ADDRESS={hex(contract_address)}")


if __name__ == "__main__":
    asyncio.run(main())
