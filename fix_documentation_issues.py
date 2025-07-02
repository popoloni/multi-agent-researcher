#!/usr/bin/env python3
"""
Fix Documentation Issues Script
Clears Python cache, resets documentation database, and verifies configuration
"""

import os
import sys
import shutil
import sqlite3
import asyncio
from pathlib import Path

def clear_python_cache():
    """Clear all Python cache files"""
    print("🧹 Clearing Python cache...")
    
    # Find and remove __pycache__ directories
    cache_dirs = []
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dirs.append(os.path.join(root, '__pycache__'))
    
    for cache_dir in cache_dirs:
        try:
            shutil.rmtree(cache_dir)
            print(f"   ✅ Removed {cache_dir}")
        except Exception as e:
            print(f"   ⚠️  Failed to remove {cache_dir}: {e}")
    
    # Find and remove .pyc files
    pyc_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                pyc_files.append(os.path.join(root, file))
    
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            print(f"   ✅ Removed {pyc_file}")
        except Exception as e:
            print(f"   ⚠️  Failed to remove {pyc_file}: {e}")
    
    print(f"🎉 Python cache cleared: {len(cache_dirs)} directories, {len(pyc_files)} files")

def reset_documentation_database():
    """Clear documentation entries from database"""
    print("🗃️  Resetting documentation database...")
    
    db_path = "kenobi.db"
    if not os.path.exists(db_path):
        print("   ℹ️  Database file not found, nothing to clear")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if documentation table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documentation'")
        if cursor.fetchone():
            # Count existing documentation entries
            cursor.execute("SELECT COUNT(*) FROM documentation")
            count = cursor.fetchone()[0]
            
            # Clear documentation table
            cursor.execute("DELETE FROM documentation")
            conn.commit()
            
            print(f"   ✅ Cleared {count} documentation entries from database")
        else:
            print("   ℹ️  Documentation table not found")
        
        conn.close()
        
    except Exception as e:
        print(f"   ⚠️  Failed to reset database: {e}")

def verify_environment_config():
    """Verify environment configuration"""
    print("🔧 Verifying environment configuration...")
    
    # Check .env file
    env_path = ".env"
    if os.path.exists(env_path):
        print("   ✅ .env file found")
        
        with open(env_path, 'r') as f:
            env_content = f.read()
            
        # Check AI_PROVIDER setting
        if "AI_PROVIDER=anthropic" in env_content:
            print("   ✅ AI_PROVIDER set to anthropic")
        elif "AI_PROVIDER=ollama" in env_content:
            print("   ⚠️  AI_PROVIDER set to ollama (should be anthropic)")
        else:
            print("   ⚠️  AI_PROVIDER not found in .env")
        
        # Check for Anthropic API key
        if "ANTHROPIC_API_KEY=" in env_content and "your_anthropic_api_key_here" not in env_content:
            print("   ✅ ANTHROPIC_API_KEY configured")
        else:
            print("   ⚠️  ANTHROPIC_API_KEY not properly configured")
            
    else:
        print("   ❌ .env file not found")

async def test_model_manager():
    """Test model manager configuration"""
    print("🤖 Testing model manager configuration...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, '.')
        
        from app.core.config import settings
        from app.core.model_providers import model_manager
        
        print(f"   ✅ AI_PROVIDER: {settings.AI_PROVIDER}")
        print(f"   ✅ DOCUMENTATION_MODEL: {settings.DOCUMENTATION_MODEL}")
        
        # Test model manager initialization
        print("   ✅ Model manager loaded successfully")
        
        # Test provider status
        status = await model_manager.check_provider_status()
        for provider, is_available in status.items():
            status_icon = "✅" if is_available else "❌"
            print(f"   {status_icon} {provider}: {'Available' if is_available else 'Not available'}")
        
    except Exception as e:
        print(f"   ❌ Model manager test failed: {e}")

def main():
    """Main function"""
    print("🔧 Documentation Issues Fix Script")
    print("=" * 50)
    
    # Step 1: Clear Python cache
    clear_python_cache()
    print()
    
    # Step 2: Reset documentation database
    reset_documentation_database()
    print()
    
    # Step 3: Verify environment configuration
    verify_environment_config()
    print()
    
    # Step 4: Test model manager
    asyncio.run(test_model_manager())
    print()
    
    print("🎉 Fix script completed!")
    print()
    print("📋 Next steps:")
    print("1. Restart the backend server: ./restart_backend.sh")
    print("2. Test documentation generation with a repository")
    print("3. Verify Anthropic API is used (check backend logs)")
    print("4. Test documentation persistence through navigation")

if __name__ == "__main__":
    main()