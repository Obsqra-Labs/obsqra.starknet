#!/usr/bin/env python3
"""
Giza Account Setup using SDK Functions Directly

Bypasses CLI Typer issues by calling SDK functions directly
"""

import sys
import os
from pathlib import Path

def setup_giza():
    """Set up Giza account and get API key"""
    
    print("\n" + "="*60)
    print("Giza Account Setup (Direct SDK)")
    print("="*60 + "\n")
    
    try:
        from giza.cli.commands import users
        print("✓ Giza SDK imported\n")
    except ImportError as e:
        print(f"✗ Failed to import Giza SDK: {e}")
        print("Run: pip install giza-sdk\n")
        return False
    
    print("This will create a Giza account and generate an API key.\n")
    
    # Get credentials
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Password (min 8 chars): ").strip()
    password_confirm = input("Confirm Password: ").strip()
    
    if password != password_confirm:
        print("\n✗ Passwords do not match!\n")
        return False
    
    if len(password) < 8:
        print("\n✗ Password must be at least 8 characters!\n")
        return False
    
    print("\n" + "-"*60)
    
    # Step 1: Create account
    print("\nStep 1: Creating Giza account...")
    try:
        result = users.create(
            username=username,
            email=email,
            password=password,
            confirm_password=password_confirm
        )
        print(f"✓ Account created: {username}")
    except Exception as e:
        print(f"⚠️  Account creation error: {e}")
        print("   Account may already exist. Trying login...\n")
    
    # Step 2: Login
    print("\nStep 2: Logging in...")
    try:
        login_result = users.login(
            username=username,
            password=password,
            renew=False
        )
        print("✓ Logged in successfully!")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        print("\nPossible issues:")
        print("  - Incorrect credentials")
        print("  - Account not verified (check email)")
        print("  - Network connectivity")
        print("\nTry manual setup: docs/GIZA_API_KEY_SETUP.md\n")
        return False
    
    # Step 3: Create API key
    print("\nStep 3: Generating API key...")
    try:
        api_key_result = users.create_api_key()
        
        # Extract API key from result
        api_key = None
        if isinstance(api_key_result, dict):
            api_key = api_key_result.get('api_key') or api_key_result.get('key')
        elif isinstance(api_key_result, str):
            api_key = api_key_result
        elif hasattr(api_key_result, 'api_key'):
            api_key = api_key_result.api_key
        
        if not api_key:
            print(f"⚠️  API key response: {api_key_result}")
            print("   Couldn't extract API key from response")
            print("\nTry manual method:")
            print("  1. Login at https://app.gizatech.xyz")
            print("  2. Navigate to API Keys")
            print("  3. Generate new key")
            print("  4. Add to backend/.env\n")
            return False
        
        print("\n" + "="*60)
        print("✓ GIZA API KEY GENERATED!")
        print("="*60 + "\n")
        
        print(f"API Key: {api_key}\n")
        
        # Save to backend .env
        env_file = Path("/opt/obsqra.starknet/backend/.env")
        if env_file.exists():
            content = env_file.read_text()
            
            if "GIZA_API_KEY" in content:
                # Update existing
                lines = []
                for line in content.split('\n'):
                    if line.startswith("GIZA_API_KEY"):
                        lines.append(f"GIZA_API_KEY={api_key}")
                    else:
                        lines.append(line)
                content = '\n'.join(lines)
            else:
                # Add new
                content += f"\n# Giza API Key\nGIZA_API_KEY={api_key}\n"
            
            env_file.write_text(content)
            print(f"✓ Saved to: {env_file}\n")
        
        # Save to credentials
        creds_dir = Path.home() / ".giza"
        creds_dir.mkdir(exist_ok=True)
        
        import json
        creds_file = creds_dir / "credentials.json"
        creds_file.write_text(json.dumps({
            "username": username,
            "email": email,
            "api_key": api_key
        }, indent=2))
        
        print(f"✓ Credentials saved to: {creds_file}\n")
        
        print("="*60)
        print("SETUP COMPLETE!")
        print("="*60 + "\n")
        
        print("Export to current shell:")
        print(f"  export GIZA_API_KEY='{api_key}'\n")
        
        print("Test proof generation:")
        print("  python3 scripts/generate_proof.py --mode single\n")
        
        print("Restart backend:")
        print("  # Backend will auto-load from .env\n")
        
        return True
        
    except Exception as e:
        print(f"✗ API key generation failed: {e}")
        print("\nTry manual method: docs/GIZA_API_KEY_SETUP.md\n")
        return False


if __name__ == "__main__":
    try:
        success = setup_giza()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        sys.exit(1)

