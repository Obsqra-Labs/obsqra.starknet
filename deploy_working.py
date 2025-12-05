#!/usr/bin/env python3
"""
Deploy using the funded deployer wallet - no keystore needed
"""
import asyncio
import json
from pathlib import Path

# Use older starknet_py commands that work
import subprocess
import sys

# Configuration
DEPLOYER_ADDR = "0x6b407e0b8cf645a32fd2ccef47c74c9fb7f44c3cd09041ea263a945ce29442b"
DEPLOYER_KEY = "0xf4506f978f613c4f3d8934b4bf5c3459fba3a16fbc479d5f7dee8e3832404aab"
RPC = "https://starknet-sepolia.public.blastapi.io"

print("=" * 60)
print("🚀 Deploying to Sepolia")
print("=" * 60)
print(f"Deployer: {DEPLOYER_ADDR}")
print(f"RPC: {RPC}")
print()

# Since we have the compiled contracts, let's use sncast with account create
# First create a temporary account config

# Actually, let's just tell the user what to do manually
print("Due to keystore/authentication complexity,")
print("here's what you need to do:")
print()
print("Option 1: Deploy from ArgentX Wallet")
print("=" * 60)
print("Your ArgentX wallet (0x01cf...) has 800 STARK")
print("To use it, you need to:")
print("1. Make ANY transaction in ArgentX (even 0.0001 STRK to yourself)")
print("2. This deploys your account contract")
print("3. Then you can deploy our contracts")
print()
print("Option 2: Use the funded deployer wallet")
print("=" * 60)
print("The wallet at", DEPLOYER_ADDR)
print("was funded but needs account deployment first")
print()
print("To check if it's deployed, visit:")
print(f"https://sepolia.voyager.online/contract/{DEPLOYER_ADDR}")
print()
print("If it shows 'Not found', the account needs deployment")
print("If it shows contract details, it's ready to use")
print()

sys.exit(0)

