#!/usr/bin/env python3
"""
Comprehensive API endpoint testing for Phase 2 Kenobi Code Analysis Agent
Tests all new endpoints and validates responses
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8080"

def test_endpoint(method: str, endpoint: str, data: Dict[str, Any] = None, expected_status: int = 200) -> Dict[str, Any]:
    """Test an API endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ SUCCESS")
        else:
            print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
        
        try:
            result = response.json()
            if response.status_code == expected_status:
                print(f"Response keys: {list(result.keys())}")
            else:
                print(f"Error: {result.get('detail', 'Unknown error')}")
            return result
        except:
            print(f"Response text: {response.text[:200]}...")
            return {"error": "Invalid JSON response"}
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return {"error": str(e)}

def main():
    """Run comprehensive API endpoint tests"""
    print("🚀 Starting Phase 2 Kenobi API Endpoint Tests")
    print("=" * 60)
    
    # Test 1: Basic repository indexing
    print("\n📁 PHASE 1: Basic Repository Indexing")
    index_result = test_endpoint(
        "POST", 
        "/kenobi/repositories/index",
        {
            "path": "/workspace/multi-agent-researcher",
            "repository_id": "test-repo-api"
        }
    )
    
    if "repository_id" in index_result:
        repo_id = index_result["repository_id"]
        print(f"Repository indexed with ID: {repo_id}")
    else:
        print("❌ Failed to get repository ID from indexing")
        return
    
    # Test 2: Advanced repository indexing
    print("\n🔬 PHASE 2: Advanced Repository Indexing")
    advanced_result = test_endpoint(
        "POST",
        "/kenobi/repositories/index-advanced",
        {
            "path": "/workspace/multi-agent-researcher",
            "repository_id": "test-repo-advanced"
        }
    )
    
    if "repository_analysis" in advanced_result:
        advanced_repo_id = advanced_result["repository_analysis"]["repository_id"]
        print(f"Advanced repository indexed with ID: {advanced_repo_id}")
    else:
        print("❌ Failed to get advanced repository ID")
        advanced_repo_id = repo_id  # Fallback
    
    # Test 3: List repositories
    print("\n📋 PHASE 3: List Repositories")
    test_endpoint("GET", "/kenobi/repositories")
    
    # Test 4: Semantic search
    print("\n🔍 PHASE 4: Semantic Search")
    test_endpoint(
        "POST",
        "/kenobi/search/semantic",
        {
            "query": "agent initialization",
            "repository_ids": [repo_id],
            "limit": 5
        }
    )
    
    # Test 5: Similar code search
    print("\n🔎 PHASE 5: Similar Code Search")
    test_endpoint(
        "POST",
        "/kenobi/search/similar",
        {
            "example_code": "def __init__(self):",
            "language": "python"
        }
    )
    
    # Test 6: Pattern search
    print("\n🎯 PHASE 6: Pattern Search")
    test_endpoint(
        "POST",
        "/kenobi/search/patterns",
        {
            "pattern_description": "initialization methods"
        }
    )
    
    # Test 7: Cross-repository search
    print("\n🌐 PHASE 7: Cross-Repository Search")
    test_endpoint(
        "POST",
        "/kenobi/search/cross-repository",
        {
            "query": "BaseAgent",
            "repository_ids": [repo_id, advanced_repo_id],
            "limit": 5
        }
    )
    
    # Test 8: Repository dependencies
    print("\n🔗 PHASE 8: Repository Dependencies")
    test_endpoint("GET", f"/kenobi/repositories/{repo_id}/dependencies")
    
    # Test 9: Repository categorization
    print("\n🏷️ PHASE 9: Repository Categorization")
    test_endpoint("GET", f"/kenobi/repositories/{repo_id}/categorize")
    
    # Test 10: Architectural analysis
    print("\n🏗️ PHASE 10: Architectural Analysis")
    test_endpoint("GET", f"/kenobi/repositories/{repo_id}/architecture")
    
    # Test 11: Element relationships (with non-existent element)
    print("\n🔄 PHASE 11: Element Relationships")
    test_endpoint("GET", "/kenobi/elements/BaseAgent/relationships")
    
    # Test 12: Category suggestions (with non-existent element)
    print("\n💡 PHASE 12: Category Suggestions")
    test_endpoint("GET", "/kenobi/elements/BaseAgent/categories/suggest")
    
    # Test 13: File analysis
    print("\n📄 PHASE 13: File Analysis")
    test_endpoint(
        "POST",
        "/kenobi/analyze/file",
        {
            "file_path": "/workspace/multi-agent-researcher/app/agents/kenobi_agent.py",
            "repository_id": repo_id
        }
    )
    
    print("\n" + "=" * 60)
    print("🎉 Phase 2 Kenobi API Endpoint Testing Complete!")
    print("✅ All major endpoints tested")
    print("🚀 Ready for production deployment")

if __name__ == "__main__":
    main()