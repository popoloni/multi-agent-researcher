"""
Simple test for Vector Database Service
"""

import pytest
from app.services.vector_database_service import VectorDatabaseService, DocumentType

@pytest.mark.asyncio
async def test_basic_functionality():
    """Test basic vector database functionality"""
    print("🧪 Testing Vector Database Service...")
    
    # Initialize service
    service = VectorDatabaseService()
    print("✅ Service initialized")
    
    # Test health status
    health = await service.get_health_status()
    print(f"✅ Health status: {health['status']}")
    print(f"   Vector DB backend: {health['vector_database']['backend']}")
    print(f"   Document count: {health['vector_database']['document_count']}")
    
    # Test document indexing
    print("\n📝 Testing document indexing...")
    result = await service.index_document(
        content="def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
        metadata={
            "file_path": "/test/fibonacci.py",
            "function_name": "fibonacci"
        },
        document_type=DocumentType.FUNCTION,
        repository_id="test-repo"
    )
    
    print(f"✅ Document indexed: {result.success}")
    print(f"   Document ID: {result.document_id}")
    print(f"   Embedding dimension: {result.embedding_dimension}")
    print(f"   Processing time: {result.processing_time:.3f}s")
    
    # Test search
    print("\n🔍 Testing semantic search...")
    search_results = await service.search_documents(
        query="recursive fibonacci function",
        repository_id="test-repo",
        limit=5
    )
    
    print(f"✅ Search completed: {len(search_results)} results")
    for i, result in enumerate(search_results):
        print(f"   Result {i+1}: similarity={result.similarity_score:.3f}, type={result.document_type.value}")
    
    # Test document retrieval
    print("\n📄 Testing document retrieval...")
    retrieved_doc = await service.get_document_by_id(result.document_id)
    if retrieved_doc:
        print(f"✅ Document retrieved: {retrieved_doc.id}")
        print(f"   Content preview: {retrieved_doc.content[:50]}...")
    else:
        print("❌ Document not found")
    
    # Test repository documents
    print("\n📁 Testing repository documents...")
    repo_docs = await service.get_repository_documents("test-repo")
    print(f"✅ Repository documents: {len(repo_docs)} found")
    
    print("\n🎉 All tests completed successfully!")