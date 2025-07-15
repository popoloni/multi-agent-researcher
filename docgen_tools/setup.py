#!/usr/bin/env python3
"""
Setup script for the consolidated documentation tools.
Automates dependency installation and basic configuration.
"""
import os
import sys
import subprocess
import json

def install_dependencies():
    """Install required Python packages."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def create_sample_config():
    """Create a sample configuration file if one doesn't exist."""
    if os.path.exists('config.json'):
        print("✓ Configuration file already exists")
        return True
    
    print("Creating sample configuration...")
    sample_config = {
        "llm_provider": "bedrock",
        "model": "eu.anthropic.claude-3-5-sonnet-20240620-v1:0",
        "aws_profile": "your-profile-name",
        "aws_region": "eu-west-1",
        "src_dir": "test_src",
        "docs_dir": "component_doc",
        "doc_name": "documentation.docx",
        "doc_concise": False,
        "max_tokens": 128000,
        "temperature": 0.2,
        "top_p": 0.85,
        "top_k": 20,
        "general_system_prompt": "You are an expert code analyst and technical documentation writer..."
    }
    
    try:
        with open('config.json', 'w') as f:
            json.dump(sample_config, f, indent=4)
        print("✓ Sample configuration created")
        print("  Please edit config.json with your specific settings")
        return True
    except Exception as e:
        print(f"✗ Failed to create configuration: {e}")
        return False

def check_environment():
    """Check if the environment is ready."""
    print("Checking environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher required")
        return False
    else:
        print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if pip is available
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✓ pip is available")
    except subprocess.CalledProcessError:
        print("✗ pip is not available")
        return False
    
    return True

def setup_aws_instructions():
    """Show AWS setup instructions."""
    print("\n" + "="*50)
    print("AWS BEDROCK SETUP INSTRUCTIONS")
    print("="*50)
    print("""
1. Log into AWS Console
2. Go to IAM and create a user with Bedrock permissions
3. Generate access keys for the user
4. Copy the credentials text provided by AWS
5. Add to ~/.aws/credentials (Linux/Mac) or %USERPROFILE%\\.aws\\credentials (Windows)

Example credentials format:
[your-profile-name]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
aws_session_token = YOUR_SESSION_TOKEN

6. Update config.json with your profile name:
   "aws_profile": "your-profile-name"
""")

def setup_anthropic_instructions():
    """Show Anthropic setup instructions."""
    print("\n" + "="*50)
    print("ANTHROPIC API SETUP INSTRUCTIONS")
    print("="*50)
    print("""
1. Go to https://console.anthropic.com/
2. Create an account or log in
3. Navigate to API Keys section
4. Create a new API key
5. Set environment variable:

Windows (PowerShell):
$env:ANTHROPIC_API_KEY = "your-api-key-here"

Linux/Mac:
export ANTHROPIC_API_KEY="your-api-key-here"

6. Update config.json:
   "llm_provider": "anthropic"
""")

def main():
    """Main setup function."""
    print("Consolidated Documentation Tools Setup")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        print("✗ Environment check failed")
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("✗ Dependency installation failed")
        return 1
    
    # Create sample config
    if not create_sample_config():
        print("✗ Configuration setup failed")
        return 1
    
    # Run tests
    print("\nRunning validation tests...")
    try:
        import test_tools
        if test_tools.main() == 0:
            print("✓ All tests passed!")
        else:
            print("! Some tests failed - check dependencies")
    except Exception as e:
        print(f"! Could not run tests: {e}")
    
    # Show configuration instructions
    print("\n" + "="*50)
    print("NEXT STEPS")
    print("="*50)
    print("1. Choose your LLM provider:")
    print("   - AWS Bedrock (recommended for enterprise)")
    print("   - Anthropic API (easier for individual use)")
    print()
    print("2. Follow the setup instructions below")
    print()
    print("3. Edit config.json with your specific settings")
    print()
    print("4. Run: python generate_docs.py")
    
    while True:
        choice = input("\nWhich LLM provider setup instructions would you like to see? (bedrock/anthropic/skip): ").lower()
        if choice == 'bedrock':
            setup_aws_instructions()
            break
        elif choice == 'anthropic':
            setup_anthropic_instructions()
            break
        elif choice == 'skip':
            break
        else:
            print("Please enter 'bedrock', 'anthropic', or 'skip'")
    
    print("\n" + "="*50)
    print("Setup complete! See docs/SETUP.md for detailed instructions.")
    print("="*50)
    return 0

if __name__ == "__main__":
    sys.exit(main())
