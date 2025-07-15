#!/usr/bin/env python3
"""
Test script to verify the consolidated documentation tools work correctly.
"""
import os
import json
import subprocess
import sys

def test_configuration():
    """Test that configuration loads correctly."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("✓ Configuration loaded successfully")
        print(f"  - Source directory: {config.get('src_dir', 'not set')}")
        print(f"  - Docs directory: {config.get('docs_dir', 'not set')}")
        print(f"  - LLM Provider: {config.get('llm_provider', 'not set')}")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_imports():
    """Test that all required modules can be imported."""
    modules_to_test = [
        'add_doc_links',
        'generate_docs', 
        'folder2word',
        'preprocess_xml'
    ]
    
    success = True
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module}.py imports successfully")
        except ImportError as e:
            print(f"✗ {module}.py import failed: {e}")
            success = False
        except Exception as e:
            print(f"✗ {module}.py has syntax error: {e}")
            success = False
    
    return success

def test_dependencies():
    """Test that required Python packages are available."""
    # Test built-in packages
    builtin_packages = ['json', 'os', 'pathlib', 'logging']
    
    # Test external packages (must match requirements.txt)
    external_packages = [
        ('requests', 'requests>=2.31.0'),
        ('boto3', 'boto3>=1.34.0'),
        ('anthropic', 'anthropic>=0.25.0'),
        ('docx', 'python-docx>=0.8.11'),
        ('markdown', 'markdown>=3.5.0'),
        ('PIL', 'pillow>=10.0.0')
    ]
    
    success = True
    
    # Test built-in packages
    for package in builtin_packages:
        try:
            __import__(package)
            print(f"✓ {package} package available (built-in)")
        except ImportError:
            print(f"✗ {package} package missing (should be built-in)")
            success = False
    
    # Test external packages
    for package, requirement in external_packages:
        try:
            __import__(package)
            print(f"✓ {package} package available")
        except ImportError:
            print(f"✗ {package} package missing - install with: pip install {requirement}")
            success = False
    
    return success

def test_file_structure():
    """Test that all expected files are present."""
    expected_files = [
        'config.json',
        'add_doc_links.py',
        'generate_docs.py',
        'folder2word.py',
        'preprocess_xml.py',
        'README.md',
        'test_src/TestClass.java'
    ]
    
    success = True
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            success = False
    
    return success

def main():
    """Run all tests."""
    print("Testing Consolidated Documentation Tools")
    print("=" * 40)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Configuration", test_configuration),
        ("Dependencies", test_dependencies),
        ("Module Imports", test_imports)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n{test_name} Test:")
        print("-" * 20)
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✓ All tests passed! The consolidated tools are ready to use.")
        print("\nNext steps:")
        print("1. Update config.json with your specific settings")
        print("2. Set up API credentials (ANTHROPIC_API_KEY or AWS profile)")
        print("3. Run: python generate_docs.py")
    else:
        print("✗ Some tests failed. Please address the issues above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
