#!/usr/bin/env python3
"""
Test script for Kenobi agent functionality
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.kenobi_agent import KenobiAgent

async def test_kenobi():
    """Test Kenobi agent functionality"""
    print("Testing Kenobi agent...")
    
    try:
        # Initialize Kenobi agent
        kenobi = KenobiAgent()
        print(f"✓ Kenobi agent initialized: {kenobi.name}")
        
        # Test repository analysis
        repo_path = "/tmp/kenobi_test_repo"
        print(f"Analyzing repository: {repo_path}")
        
        analysis = await kenobi.analyze_repository(repo_path)
        print(f"✓ Repository analysis completed")
        print(f"  - Repository: {analysis.repository.name}")
        print(f"  - Language: {analysis.repository.language.value}")
        print(f"  - Files analyzed: {len(analysis.files)}")
        print(f"  - Elements found: {sum(len(f.elements) for f in analysis.files)}")
        
        # Print some details
        for file in analysis.files[:2]:  # Show first 2 files
            print(f"  File: {file.file_path}")
            print(f"    Elements: {len(file.elements)}")
            for element in file.elements[:3]:  # Show first 3 elements
                print(f"      - {element.element_type.value}: {element.name}")
        
        print("✓ Test completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_kenobi())