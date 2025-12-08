#!/usr/bin/env python3
"""
Giza API Key Setup - Real Implementation

Uses UsersClient programmatic API
"""

import sys
import json
from pathlib import Path

def setup_giza_api_key():
    """Set up Giza account and get API key"""
    
    print("\n" + "="*60)
    print("Giza API Key Setup")
    print("="*60 + "\n")
    
    try:
        from giza.cli.commands.users import UsersClient
        from giza.cli.schemas.users import UserCreate
        print("✓ Giza SDK imported\n")
    except ImportError as e:
        print(f"✗ Failed to import Giza SDK: {e}")
        print("Run: pip install giza-sdk\n")
        return False
    
    # Get credentials
    print("Create Giza account:\n")
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
    
    # Initialize client
    client = UsersClient(host="https://api.gizatech.xyz")
    
    # Step 1: Create account
    print("\nStep 1: Creating Giza account...")
    try:
        user_create = UserCreate(
            username=username,
            email=email,
            password=password
        )
        
        response = client.create(user_create)
        print(f"✓ Account created: {username}")
        print(f"  User ID: {response.id if hasattr(response, 'id') else 'N/A'}")
    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower() or "duplicate" in error_msg.lower():
            print(f"⚠️  Account may already exist. Continuing to login...")
        else:
            print(f"✗ Account creation failed: {e}")
            print("\nIf account already exists, continue to login.")
            return False
    
    # Step 2: Login to get token
    print("\nStep 2: Logging in...")
    try:
        client.retrieve_token(user=username, password=password, renew=False)
        print("✓ Logged in successfully!")
        
        # Token should be saved automatically by SDK
        # Check if token exists
        token_file = Path.home() / ".giza" / ".credentials.json"
        if token_file.exists():
            with open(token_file, 'r') as f:
                creds = json.load(f)
                if creds.get('token'):
                    print(f"  Token stored in: {token_file}")
        
    except Exception as e:
        print(f"✗ Login failed: {e}")
        print("\nPlease verify:")
        print("  - Username and password are correct")
        print("  - Email has been verified (check inbox)")
        print("  - Network connection is working\n")
        return False
    
    # Step 3: Create API key
    print("\nStep 3: Generating API key...")
    try:
        # Reinitialize client with token
        client = UsersClient(host="https://api.gizatech.xyz")
        
        api_key_response = client.create_api_key()
        
        # Extract API key from response
        if hasattr(api_key_response, 'api_key'):
            api_key = api_key_response.api_key
        elif hasattr(api_key_response, 'key'):
            api_key = api_key_response.key
        elif isinstance(api_key_response, dict):
            api_key = api_key_response.get('api_key') or api_key_response.get('key')
        else:
            print(f"⚠️  Unexpected response type: {type(api_key_response)}")
            print(f"  Response: {api_key_response}")
            
            # Try retrieve_api_key instead
            print("\nTrying retrieve_api_key...")
            api_key_response = client.retrieve_api_key()
            api_key = api_key_response.api_key if hasattr(api_key_response, 'api_key') else None
        
        if not api_key:
            print("✗ Could not extract API key from response")
            print("\nManual method:")
            print("  1. Visit: https://app.gizatech.xyz")
            print("  2. Login with your credentials")
            print("  3. Navigate to Settings → API Keys")
            print("  4. Generate new key")
            print("  5. Add to backend/.env:")
            print(f"     echo 'GIZA_API_KEY=your_key' >> /opt/obsqra.starknet/backend/.env\n")
            return False
        
        print("\n" + "="*60)
        print("✓ GIZA API KEY GENERATED!")
        print("="*60 + "\n")
        
        # Mask middle of key for display
        masked_key = f"{api_key[:10]}...{api_key[-10:]}" if len(api_key) > 20 else api_key
        print(f"API Key: {masked_key}\n")
        
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
                content += f"\n# Giza API Key for ZK Proof Generation\nGIZA_API_KEY={api_key}\n"
            
            env_file.write_text(content)
            print(f"✓ Saved to: {env_file}\n")
        
        # Save to credentials
        creds_dir = Path.home() / ".giza"
        creds_dir.mkdir(exist_ok=True)
        
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
        
        print("Export to shell:")
        print(f"  export GIZA_API_KEY='{api_key}'\n")
        
        print("Test proof generation:")
        print("  python3 scripts/generate_proof.py --mode single\n")
        
        return True
        
    except Exception as e:
        print(f"✗ API key generation failed: {e}")
        print(f"\nError type: {type(e).__name__}")
        print("\nTry manual setup: docs/GIZA_API_KEY_SETUP.md\n")
        return False


if __name__ == "__main__":
    try:
        success = setup_giza_api_key()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

