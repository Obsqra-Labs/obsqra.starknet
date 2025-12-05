#!/bin/bash
echo "Creating keystore with your private key..."
echo ""
echo "Your private key: 0x04d871184e90d8c7399256180b4576d0e257b58dfeca4ae00f7565c02bcfc218"
echo ""
echo "When prompted:"
echo "1. Enter your private key (shown above)"
echo "2. Create a password (remember it!)"
echo ""

mkdir -p ~/.starkli-wallets/deployer
starkli signer keystore from-key ~/.starkli-wallets/deployer/keystore.json
