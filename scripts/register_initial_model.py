#!/usr/bin/env python3
"""
Register initial model version in Model Registry
"""
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import get_settings
from app.services.model_registry_service import get_model_registry_service
from app.services.model_service import get_model_service

settings = get_settings()


async def register_initial_model():
    """Register the initial model version"""
    if not settings.MODEL_REGISTRY_ADDRESS:
        print("❌ MODEL_REGISTRY_ADDRESS not set in config")
        print("   Please deploy Model Registry first and update config")
        return False
    
    print("📝 Registering initial model version...")
    print(f"   Registry: {settings.MODEL_REGISTRY_ADDRESS}")
    
    try:
        model_service = get_model_service()
        model_info = model_service.get_current_model_version()
        
        model_registry = get_model_registry_service()
        
        version_felt = model_info.get("version_felt", 0x010000)  # v1.0.0
        model_hash_felt = model_info.get("model_hash_felt", 0)
        description = model_info.get("description", "Initial risk scoring model")
        
        print(f"   Version: {model_info.get('version', '1.0.0')} (felt: {hex(version_felt)})")
        print(f"   Model Hash: {model_info.get('model_hash', '')[:16]}... (felt: {hex(model_hash_felt)})")
        print()
        
        tx_hash = await model_registry.register_model_version(
            version_felt=version_felt,
            model_hash_felt=model_hash_felt,
            description=description,
        )
        
        print(f"✅ Model version registered!")
        print(f"   Transaction: {hex(tx_hash)}")
        print()
        
        # Verify registration
        current_model = await model_registry.get_current_model()
        if current_model:
            print("✅ Verification:")
            print(f"   Current version: {current_model.get('version', 'N/A')}")
            print(f"   Model hash: {hex(current_model.get('model_hash', 0))}")
        else:
            print("⚠️  Could not verify registration (may need to wait for block)")
        
        return True
        
    except ValueError as e:
        if "MODEL_REGISTRY_ADDRESS is not configured" in str(e):
            print("❌ MODEL_REGISTRY_ADDRESS not configured")
            print("   Please set it in backend/.env or backend/app/config.py")
        else:
            print(f"❌ Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(register_initial_model())
    sys.exit(0 if success else 1)
