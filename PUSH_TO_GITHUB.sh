#!/bin/bash
# Quick script to push to GitHub

cd /opt/obsqra.starknet

# Option 1: Use Personal Access Token (recommended)
# Create token at: https://github.com/settings/tokens
# Then run:
# git push https://YOUR_TOKEN@github.com/Obsqra-Labs/obsqra.starknet.git main

# Option 2: Setup SSH key
# ssh-keygen -t ed25519 -C "your_email@example.com"
# cat ~/.ssh/id_ed25519.pub  # Add this to GitHub
# git remote set-url origin git@github.com:Obsqra-Labs/obsqra.starknet.git
# git push origin main

# Option 3: Use gh CLI (if installed)
# gh auth login
# git push origin main

echo "Ready to push. Choose authentication method above."
echo "Current commits ready:"
git log --oneline -5

