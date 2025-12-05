#!/usr/bin/env python3
"""
Full deployment script - creates new wallet, funds it, deploys contracts
"""
import asyncio
import json
import os
from pathlib import Path
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.hash.selector import get_selector_from_name
from starknet_py.contract import Contract

# Configuration
RPC_URL = "https://starknet-sepolia.infura.io/v3/f658a7a274b943c3890cbcd7e46f1ca4"
EXISTING_ADDRESS = "0x01cf4C4a9e8E138f70318af37CEb7E63B95EBCDFEb28bc7FeC966a250df1c6Bd"
EXISTING_PRIVATE_KEY = "0x04d871184e90d8c7399256180b4576d0e257b58dfeca4ae00f7565c02bcfc218"

# OpenZeppelin account class hash (standard on Sepolia)
ACCOUNT_CLASS_HASH = 0x04c6d6cf894f8bc96bb9c525e6853e5483177841f7388f74a46cfda6f028c755

# Contract paths
CONTRACTS_DIR = Path("/opt/obsqra.starknet/contracts/target/dev")
RISK_ENGINE = CONTRACTS_DIR / "obsqra_contracts_RiskEngine.contract_class.json"
DAO_MANAGER = CONTRACTS_DIR / "obsqra_contracts_DAOConstraintManager.contract_class.json"
STRATEGY_ROUTER = CONTRACTS_DIR / "obsqra_contracts_StrategyRouter.contract_class.json"


async def main():
    print("=" * 60)
    print("Obsqra Starknet Full Deployment")
    print("=" * 60)
    print()
    
    # Initialize client
    print(f"Connecting to: {RPC_URL}")
    client = FullNodeClient(node_url=RPC_URL)
    print("✓ Connected")
    print()
    
    # Step 1: Generate new wallet
    print("=" * 60)
    print("Step 1: Creating New Deployment Wallet")
    print("=" * 60)
    
    # Generate random key pair
    from secrets import randbits
    private_key = randbits(256)
    key_pair = KeyPair.from_private_key(private_key)
    
    print(f"Private Key: {hex(private_key)}")
    print(f"Public Key:  {hex(key_pair.public_key)}")
    
    # Calculate account address
    # For OpenZeppelin account: hash(class_hash, salt, public_key, 0)
    from starknet_py.hash.address import compute_address
    salt = 0
    calldata = [key_pair.public_key]
    
    new_account_address = compute_address(
        class_hash=ACCOUNT_CLASS_HASH,
        constructor_calldata=calldata,
        salt=salt,
        deployer_address=0
    )
    
    print(f"New Address: {hex(new_account_address)}")
    print()
    
    # Save wallet info
    wallet_info = {
        "address": hex(new_account_address),
        "private_key": hex(private_key),
        "public_key": hex(key_pair.public_key),
        "class_hash": hex(ACCOUNT_CLASS_HASH),
        "salt": hex(salt)
    }
    
    with open("/opt/obsqra.starknet/.deployer_wallet.json", "w") as f:
        json.dump(wallet_info, f, indent=2)
    
    print("✓ Wallet info saved to .deployer_wallet.json")
    print()
    
    # Step 2: Fund new wallet (from existing wallet)
    print("=" * 60)
    print("Step 2: Funding New Wallet")
    print("=" * 60)
    print()
    print("Initializing existing account...")
    
    existing_key_pair = KeyPair.from_private_key(int(EXISTING_PRIVATE_KEY, 16))
    existing_account = Account(
        client=client,
        address=EXISTING_ADDRESS,
        key_pair=existing_key_pair,
        chain=StarknetChainId.TESTNET
    )
    
    # Check if existing account is deployed
    try:
        nonce = await client.get_contract_nonce(EXISTING_ADDRESS)
        print(f"Existing account nonce: {nonce}")
        print("✓ Existing account is deployed")
    except Exception as e:
        print(f"✗ Existing account not deployed: {e}")
        print()
        print("SOLUTION: In ArgentX, send 0.0001 STRK to yourself to deploy the account")
        print("Then run this script again")
        return
    
    # Send 0.01 STRK to new wallet for deployment + gas
    print(f"Sending 0.01 STRK to new wallet...")
    
    # STRK token address on Sepolia
    STRK_ADDRESS = 0x04718f5a0fc34cc1af16a1cdee98ffb20c31f5cd61d6ab07201858f4287c938d
    
    transfer_call = {
        "contract_address": STRK_ADDRESS,
        "entry_point_selector": get_selector_from_name("transfer"),
        "calldata": [
            new_account_address,
            int(0.01 * 10**18),  # 0.01 STRK
            0  # high bits
        ]
    }
    
    try:
        tx = await existing_account.execute(
            calls=transfer_call,
            max_fee=int(1e16)
        )
        print(f"Transfer TX: {hex(tx.transaction_hash)}")
        await client.wait_for_tx(tx.transaction_hash)
        print("✓ Transfer confirmed")
    except Exception as e:
        print(f"✗ Transfer failed: {e}")
        return
    
    print()
    
    # Step 3: Deploy new account
    print("=" * 60)
    print("Step 3: Deploying New Account Contract")
    print("=" * 60)
    print()
    
    # Create account instance
    new_account = Account(
        client=client,
        address=new_account_address,
        key_pair=key_pair,
        chain=StarknetChainId.TESTNET
    )
    
    # Deploy account
    try:
        deploy_result = await new_account.sign_deploy_account_transaction(
            class_hash=ACCOUNT_CLASS_HASH,
            contract_address_salt=salt,
            constructor_calldata=calldata,
            max_fee=int(1e16)
        )
        
        print(f"Deploy TX: {hex(deploy_result.transaction_hash)}")
        await client.wait_for_tx(deploy_result.transaction_hash)
        print(f"✓ Account deployed at: {hex(new_account_address)}")
    except Exception as e:
        print(f"✗ Deploy failed: {e}")
        return
    
    print()
    
    # Step 4: Declare contracts
    print("=" * 60)
    print("Step 4: Declaring Contracts")
    print("=" * 60)
    print()
    
    class_hashes = {}
    
    for name, path in [
        ("RiskEngine", RISK_ENGINE),
        ("DAOConstraintManager", DAO_MANAGER),
        ("StrategyRouter", STRATEGY_ROUTER)
    ]:
        print(f"Declaring {name}...")
        
        with open(path, 'r') as f:
            compiled_contract = json.load(f)
        
        try:
            declare_result = await new_account.sign_declare_transaction(
                compiled_contract=compiled_contract,
                max_fee=int(1e16)
            )
            
            await client.wait_for_tx(declare_result.transaction_hash)
            class_hashes[name] = declare_result.class_hash
            
            print(f"  ✓ Class Hash: {hex(declare_result.class_hash)}")
            print(f"  TX: {hex(declare_result.transaction_hash)}")
        except Exception as e:
            if "is already declared" in str(e):
                print(f"  ⚠ Already declared (this is OK)")
                # Try to extract class hash from compiled contract
                import hashlib
                # For now, skip if already declared
            else:
                print(f"  ✗ Error: {e}")
        
        print()
    
    # Step 5: Deploy contract instances
    print("=" * 60)
    print("Step 5: Deploying Contract Instances")
    print("=" * 60)
    print()
    
    if "RiskEngine" in class_hashes:
        print("Deploying RiskEngine...")
        try:
            deploy_call = await new_account.sign_invoke_transaction(
                calls={
                    "contract_address": 0x01,  # UDC address
                    "entry_point_selector": get_selector_from_name("deployContract"),
                    "calldata": [
                        class_hashes["RiskEngine"],
                        0,  # salt
                        0,  # unique
                        1,  # calldata_len
                        new_account_address  # owner
                    ]
                },
                max_fee=int(1e16)
            )
            
            await client.wait_for_tx(deploy_call.transaction_hash)
            print(f"  ✓ Deployed")
            print(f"  TX: {hex(deploy_call.transaction_hash)}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print()
    print("=" * 60)
    print("Deployment Complete!")
    print("=" * 60)
    print()
    print(f"New Deployer Wallet: {hex(new_account_address)}")
    print(f"Wallet details saved to: .deployer_wallet.json")
    print()
    
    # Save deployment info
    deployment_info = {
        "deployer_address": hex(new_account_address),
        "class_hashes": {k: hex(v) for k, v in class_hashes.items()},
        "network": "sepolia",
        "rpc": RPC_URL
    }
    
    with open("/opt/obsqra.starknet/.deployment.json", "w") as f:
        json.dump(deployment_info, f, indent=2)
    
    print("Deployment info saved to: .deployment.json")


if __name__ == "__main__":
    asyncio.run(main())

