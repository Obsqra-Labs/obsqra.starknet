#!/usr/bin/env python3
"""
Direct Giza API Integration

Bypasses CLI issues by using REST API directly
"""

import requests
import json
import os
from pathlib import Path

GIZA_API_BASE = "https://api.gizatech.xyz/api/v1"


def create_giza_account_direct(username: str, email: str, password: str) -> dict:
    """Create Giza account via REST API"""
    
    print(f"\nCreating Giza account: {username} ({email})")
    
    response = requests.post(
        f"{GIZA_API_BASE}/users",
        json={
            "username": username,
            "email": email,
            "password": password
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code in [200, 201]:
        print("✓ Account created successfully!")
        return response.json()
    else:
        print(f"✗ Account creation failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None


def login_giza_direct(username: str, password: str) -> str:
    """Login to Giza and get access token"""
    
    print(f"\nLogging in as: {username}")
    
    response = requests.post(
        f"{GIZA_API_BASE}/users/login",
        json={
            "username": username,
            "password": password
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token') or data.get('token')
        print("✓ Login successful!")
        return token
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None


def create_api_key_direct(access_token: str) -> str:
    """Create API key using access token"""
    
    print("\nGenerating API key...")
    
    response = requests.post(
        f"{GIZA_API_BASE}/api-keys",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json={"name": "obsqra-backend"}
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        api_key = data.get('api_key') or data.get('key')
        print("✓ API key generated!")
        return api_key
    else:
        print(f"✗ API key creation failed: {response.status_code}")
        print(f"  Response: {response.text}")
        return None


def save_api_key(api_key: str, username: str, email: str):
    """Save API key to configuration files"""
    
    # Save to backend .env
    env_file = Path("/opt/obsqra.starknet/backend/.env")
    if env_file.exists():
        content = env_file.read_text()
        
        # Check if already exists
        if "GIZA_API_KEY" in content:
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith("GIZA_API_KEY"):
                    new_lines.append(f"GIZA_API_KEY={api_key}")
                else:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
        else:
            content += f"\n\n# Giza API Key for ZK Proof Generation\nGIZA_API_KEY={api_key}\n"
        
        env_file.write_text(content)
        print(f"\n✓ API key saved to: {env_file}")
    
    # Save credentials file
    creds_dir = Path.home() / ".giza"
    creds_dir.mkdir(exist_ok=True)
    
    creds_file = creds_dir / "credentials.json"
    creds_file.write_text(json.dumps({
        "username": username,
        "email": email,
        "api_key": api_key
    }, indent=2))
    
    print(f"✓ Credentials saved to: {creds_file}")
    
    # Export to shell
    print(f"\n✓ To use immediately, run:")
    print(f"  export GIZA_API_KEY='{api_key}'")


def main():
    """Main entry point"""
    
    print("\n" + "="*60)
    print("Giza Account Setup (Direct API)")
    print("="*60 + "\n")
    
    print("This will create a Giza account and generate an API key")
    print("for zero-knowledge proof generation.\n")
    
    # Get credentials
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    password_confirm = input("Confirm Password: ").strip()
    
    if password != password_confirm:
        print("\n✗ Passwords do not match!")
        return
    
    if len(password) < 8:
        print("\n✗ Password must be at least 8 characters!")
        return
    
    print("\n" + "="*60)
    
    # Create account
    account_result = create_giza_account_direct(username, email, password)
    
    if not account_result:
        print("\n⚠️  Account creation failed.")
        print("The account may already exist. Try logging in instead.\n")
        
        # Try login with existing account
        proceed = input("Try logging in with existing account? [Y/n]: ").strip().lower()
        if proceed == 'n':
            return
    
    # Login
    access_token = login_giza_direct(username, password)
    
    if not access_token:
        print("\n✗ Login failed. Cannot proceed.")
        print("\nAlternative: Visit https://app.gizatech.xyz to create account manually\n")
        return
    
    # Create API key
    api_key = create_api_key_direct(access_token)
    
    if not api_key:
        print("\n✗ API key generation failed.")
        print("\nAlternative: Visit https://app.gizatech.xyz to generate API key manually\n")
        return
    
    # Save
    save_api_key(api_key, username, email)
    
    print("\n" + "="*60)
    print("✓ SETUP COMPLETE!")
    print("="*60 + "\n")
    
    print(f"API Key: {api_key}\n")
    
    print("Next steps:")
    print("1. Export the key: export GIZA_API_KEY='" + api_key + "'")
    print("2. Test proof generation: python3 scripts/generate_proof.py --mode single")
    print("3. Restart backend to load new key")
    print("")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.\n")
    except Exception as e:
        print(f"\n✗ Setup failed: {e}\n")
        print("See docs/GIZA_API_KEY_SETUP.md for alternative methods\n")

