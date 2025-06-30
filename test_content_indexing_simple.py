"""
Simple test for Content Indexing Service
"""

import asyncio
import tempfile
import os
import shutil
from app.services.content_indexing_service import ContentIndexingService, ContentType

async def test_content_indexing():
    """Test basic content indexing functionality"""
    print("🧪 Testing Content Indexing Service...")
    
    # Initialize service
    service = ContentIndexingService()
    print("✅ Service initialized")
    
    # Create temporary test files
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Created temp directory: {temp_dir}")
    
    try:
        # Create sample Python file
        python_file = os.path.join(temp_dir, "test.py")
        with open(python_file, 'w') as f:
            f.write('''
def fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    """Simple calculator"""
    def add(self, a, b):
        return a + b
''')
        
        # Create sample markdown file
        md_file = os.path.join(temp_dir, "README.md")
        with open(md_file, 'w') as f:
            f.write('''
# Test Project

This is a test project for content indexing.

## Features
- Fibonacci calculation
- Basic math operations

## Usage
```python
calc = Calculator()
result = calc.add(2, 3)
```
''')
        
        print("📝 Created test files")
        
        # Test file content extraction
        print("\n🔍 Testing Python file extraction...")
        python_result = await service.extract_file_content(python_file)
        print(f"✅ Python extraction: {python_result.success}")
        print(f"   Chunks extracted: {len(python_result.chunks)}")
        print(f"   Processing time: {python_result.extraction_time:.3f}s")
        
        for i, chunk in enumerate(python_result.chunks[:3]):  # Show first 3 chunks
            print(f"   Chunk {i+1}: {chunk.content_type.value} - {len(chunk.content)} chars")
            print(f"     Preview: {chunk.content[:50]}...")
        
        print("\n📖 Testing Markdown file extraction...")
        md_result = await service.extract_file_content(md_file, content_types=[ContentType.DOCUMENTATION])
        print(f"✅ Markdown extraction: {md_result.success}")
        print(f"   Chunks extracted: {len(md_result.chunks)}")
        print(f"   Processing time: {md_result.extraction_time:.3f}s")
        
        for i, chunk in enumerate(md_result.chunks[:2]):  # Show first 2 chunks
            print(f"   Chunk {i+1}: {chunk.content_type.value} - {len(chunk.content)} chars")
            print(f"     Preview: {chunk.content[:50]}...")
        
        # Test content search (basic test)
        print("\n🔎 Testing content search...")
        search_results = await service.search_content(
            query="fibonacci calculation",
            limit=5
        )
        print(f"✅ Search completed: {len(search_results)} results")
        
        # Test repository stats (will be empty but should not fail)
        print("\n📊 Testing repository stats...")
        stats = await service.get_repository_content_stats("test-repo")
        print(f"✅ Stats retrieved: {stats.get('total_documents', 0)} documents")
        
        print("\n🎉 All content indexing tests completed successfully!")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up temp directory")

if __name__ == "__main__":
    asyncio.run(test_content_indexing())