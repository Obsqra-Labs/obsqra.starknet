#!/usr/bin/env python3
"""
Interactive Giza Account Setup

Creates a Giza account and generates an API key
"""

import sys
import os
import json
from pathlib import Path

def setup_giza_account():
    """Set up Giza account and get API key"""
    
    print("\n" + "="*60)
    print("Giza Account Setup")
    print("="*60 + "\n")
    
    try:
        # Try using the SDK directly
        print("Attempting to create Giza account via SDK...\n")
        
        # Import Giza SDK
        try:
            from giza.client import GizaClient
            from giza.cli import users
            print("✓ Giza SDK imported successfully\n")
        except ImportError as e:
            print(f"✗ Giza SDK import failed: {e}\n")
            print("Please install: pip install giza-agents\n")
            return False
        
        # Get user credentials
        print("Please provide your Giza account details:\n")
        
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        password_confirm = input("Confirm Password: ").strip()
        
        if password != password_confirm:
            print("\n✗ Passwords do not match!")
            return False
        
        print("\nCreating Giza account...")
        
        # Try to create user using SDK
        try:
            # This is the approach from Giza docs
            from giza.commands import users as user_commands
            
            # Create user
            result = user_commands.create(
                username=username,
                password=password,
                email=email
            )
            
            print(f"\n✓ Account created successfully!")
            print(f"  Username: {username}")
            print(f"  Email: {email}\n")
            
        except Exception as create_error:
            print(f"\n⚠️  SDK creation method failed: {create_error}")
            print("\nTrying alternative method...\n")
            
            # Alternative: Use requests directly
            import requests
            
            api_url = "https://api.gizatech.xyz"  # Adjust if needed
            
            response = requests.post(
                f"{api_url}/api/v1/users",
                json={
                    "username": username,
                    "email": email,
                    "password": password
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                print("✓ Account created successfully!\n")
            else:
                print(f"✗ Account creation failed: {response.status_code}")
                print(f"  Response: {response.text}\n")
                return False
        
        # Now try to login and get API key
        print("Logging in to Giza...")
        
        try:
            # Login
            from giza.commands import users as user_commands
            
            token = user_commands.login(
                username=username,
                password=password
            )
            
            print("✓ Logged in successfully!\n")
            
            # Create API key
            print("Generating API key...")
            
            api_key_result = user_commands.create_api_key()
            
            if api_key_result:
                api_key = api_key_result.get('api_key') or api_key_result.get('key')
                
                print("\n" + "="*60)
                print("✓ GIZA API KEY GENERATED!")
                print("="*60 + "\n")
                print(f"API Key: {api_key}\n")
                
                # Save to file
                env_file = Path("/opt/obsqra.starknet/backend/.env")
                
                # Read existing .env
                env_content = ""
                if env_file.exists():
                    env_content = env_file.read_text()
                
                # Add or update GIZA_API_KEY
                if "GIZA_API_KEY" in env_content:
                    # Replace existing
                    lines = env_content.split('\n')
                    new_lines = []
                    for line in lines:
                        if line.startswith("GIZA_API_KEY"):
                            new_lines.append(f"GIZA_API_KEY={api_key}")
                        else:
                            new_lines.append(line)
                    env_content = '\n'.join(new_lines)
                else:
                    # Add new
                    env_content += f"\n\n# Giza API Key for ZK Proof Generation\nGIZA_API_KEY={api_key}\n"
                
                env_file.write_text(env_content)
                
                print(f"✓ API key saved to: {env_file}\n")
                
                # Also export to current environment
                os.environ['GIZA_API_KEY'] = api_key
                
                print("To use the API key in your current shell, run:")
                print(f"  export GIZA_API_KEY='{api_key}'\n")
                
                # Save credentials securely
                creds_file = Path.home() / ".giza" / "credentials.json"
                creds_file.parent.mkdir(exist_ok=True)
                
                creds_file.write_text(json.dumps({
                    "username": username,
                    "email": email,
                    "api_key": api_key
                }, indent=2))
                
                print(f"✓ Credentials saved to: {creds_file}\n")
                
                print("="*60)
                print("Setup Complete!")
                print("="*60 + "\n")
                
                print("Test with: python3 scripts/generate_proof.py --mode single\n")
                
                return True
            
        except Exception as login_error:
            print(f"\n✗ Login/API key generation failed: {login_error}\n")
            
            print("Alternative: Manual Setup")
            print("="*60)
            print("1. Visit: https://app.gizatech.xyz")
            print("2. Create account manually")
            print("3. Navigate to API Keys section")
            print("4. Generate new API key")
            print("5. Save to .env file:")
            print(f"   echo 'GIZA_API_KEY=your_key' >> {Path('/opt/obsqra.starknet/backend/.env')}")
            print("="*60 + "\n")
            
            return False
        
    except Exception as e:
        print(f"\n✗ Setup failed: {e}\n")
        print("Please refer to: docs/GIZA_API_KEY_SETUP.md\n")
        return False


def check_existing_api_key():
    """Check if API key already exists"""
    
    # Check environment
    if os.getenv('GIZA_API_KEY'):
        print("✓ GIZA_API_KEY found in environment\n")
        return True
    
    # Check .env file
    env_file = Path("/opt/obsqra.starknet/backend/.env")
    if env_file.exists():
        content = env_file.read_text()
        if "GIZA_API_KEY" in content and "your_key" not in content.lower():
            print("✓ GIZA_API_KEY found in .env file\n")
            # Extract and show
            for line in content.split('\n'):
                if line.startswith("GIZA_API_KEY"):
                    key = line.split('=')[1].strip()
                    print(f"  Key: {key[:20]}...{key[-10:]}\n")
                    return True
    
    # Check credentials file
    creds_file = Path.home() / ".giza" / "credentials.json"
    if creds_file.exists():
        try:
            creds = json.loads(creds_file.read_text())
            if creds.get('api_key'):
                print("✓ API key found in credentials file\n")
                print(f"  Key: {creds['api_key'][:20]}...{creds['api_key'][-10:]}\n")
                return True
        except:
            pass
    
    return False


def main():
    """Main entry point"""
    
    print("\n" + "="*60)
    print("Giza API Key Setup")
    print("="*60 + "\n")
    
    # Check if already set up
    if check_existing_api_key():
        print("API key already configured!")
        response = input("Create new API key anyway? [y/N]: ").strip().lower()
        if response != 'y':
            print("\nSetup cancelled.\n")
            return
    
    # Run setup
    success = setup_giza_account()
    
    if success:
        print("✓ All done! You can now generate real ZK proofs.\n")
    else:
        print("⚠️  Setup incomplete. See docs/GIZA_API_KEY_SETUP.md for alternatives.\n")


if __name__ == "__main__":
    main()

