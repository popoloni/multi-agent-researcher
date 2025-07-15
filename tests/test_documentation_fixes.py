#!/usr/bin/env python3
"""
Test Documentation Fixes Script
Comprehensive testing of documentation generation and persistence
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

class DocumentationTester:
    def __init__(self, base_url: str = "http://localhost:12000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def test_ai_provider_configuration(self) -> Dict[str, Any]:
        """Test AI provider configuration"""
        print("🤖 Testing AI provider configuration...")
        
        try:
            response = await self.client.get(f"{self.base_url}/system/status")
            if response.status_code == 200:
                data = response.json()
                ai_provider = data.get("ai_provider", "unknown")
                print(f"   ✅ AI Provider: {ai_provider}")
                return {"success": True, "ai_provider": ai_provider}
            else:
                print(f"   ❌ Failed to get system status: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"   ❌ Error testing AI provider: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_documentation_generation(self, repo_id: str) -> Dict[str, Any]:
        """Test documentation generation for a repository"""
        print(f"📝 Testing documentation generation for repository: {repo_id}")
        
        try:
            # Start documentation generation
            response = await self.client.post(
                f"{self.base_url}/kenobi/repositories/{repo_id}/documentation",
                json={"branch": "main"}
            )
            
            if response.status_code != 200:
                print(f"   ❌ Failed to start documentation generation: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
            
            data = response.json()
            task_id = data.get("task_id")
            print(f"   ✅ Documentation generation started, task ID: {task_id}")
            
            # Monitor progress
            max_wait = 300  # 5 minutes
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                status_response = await self.client.get(
                    f"{self.base_url}/kenobi/repositories/{repo_id}/documentation/status/{task_id}"
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status")
                    progress = status_data.get("progress", 0)
                    stage = status_data.get("current_stage", "unknown")
                    
                    print(f"   📊 Progress: {progress}% - {stage}")
                    
                    if status == "completed":
                        print("   ✅ Documentation generation completed!")
                        return {
                            "success": True, 
                            "task_id": task_id,
                            "documentation": status_data.get("documentation")
                        }
                    elif status == "failed":
                        error = status_data.get("error", "Unknown error")
                        print(f"   ❌ Documentation generation failed: {error}")
                        return {"success": False, "error": error}
                
                await asyncio.sleep(5)  # Wait 5 seconds before checking again
            
            print("   ⏰ Documentation generation timed out")
            return {"success": False, "error": "Timeout"}
            
        except Exception as e:
            print(f"   ❌ Error during documentation generation: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_documentation_retrieval(self, repo_id: str) -> Dict[str, Any]:
        """Test documentation retrieval"""
        print(f"📖 Testing documentation retrieval for repository: {repo_id}")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/kenobi/repositories/{repo_id}/documentation"
            )
            
            if response.status_code == 200:
                data = response.json()
                documentation = data.get("documentation")
                
                if documentation:
                    print("   ✅ Documentation retrieved successfully")
                    
                    # Check documentation structure
                    if isinstance(documentation, dict):
                        sections = list(documentation.keys())
                        print(f"   📋 Documentation sections: {sections}")
                        
                        # Check for expected sections
                        expected_sections = ["overview", "api_reference", "architecture", "user_guide"]
                        missing_sections = [s for s in expected_sections if s not in sections]
                        
                        if missing_sections:
                            print(f"   ⚠️  Missing sections: {missing_sections}")
                        else:
                            print("   ✅ All expected sections present")
                        
                        return {
                            "success": True,
                            "documentation": documentation,
                            "sections": sections,
                            "missing_sections": missing_sections
                        }
                    else:
                        print(f"   ⚠️  Documentation format unexpected: {type(documentation)}")
                        return {"success": True, "documentation": documentation, "format_warning": True}
                else:
                    print("   ❌ No documentation found")
                    return {"success": False, "error": "No documentation found"}
            else:
                print(f"   ❌ Failed to retrieve documentation: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"   ❌ Error retrieving documentation: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_documentation_persistence(self, repo_id: str, cycles: int = 3) -> Dict[str, Any]:
        """Test documentation persistence through multiple retrievals"""
        print(f"🔄 Testing documentation persistence ({cycles} cycles)...")
        
        results = []
        
        for i in range(cycles):
            print(f"   🔄 Cycle {i + 1}/{cycles}")
            
            # Retrieve documentation
            result = await self.test_documentation_retrieval(repo_id)
            results.append(result)
            
            if not result["success"]:
                print(f"   ❌ Cycle {i + 1} failed")
                return {"success": False, "failed_cycle": i + 1, "error": result["error"]}
            
            # Wait a bit between cycles
            await asyncio.sleep(2)
        
        # Check consistency
        first_doc = results[0].get("documentation")
        all_consistent = all(
            result.get("documentation") == first_doc 
            for result in results
        )
        
        if all_consistent:
            print("   ✅ Documentation persistence verified - all cycles consistent")
            return {"success": True, "cycles": cycles, "consistent": True}
        else:
            print("   ❌ Documentation persistence failed - inconsistent results")
            return {"success": False, "cycles": cycles, "consistent": False}
    
    async def test_repository_list(self) -> Dict[str, Any]:
        """Get list of available repositories for testing"""
        print("📂 Getting list of repositories...")
        
        try:
            response = await self.client.get(f"{self.base_url}/kenobi/repositories")
            
            if response.status_code == 200:
                data = response.json()
                repositories = data.get("repositories", [])
                
                if repositories:
                    print(f"   ✅ Found {len(repositories)} repositories")
                    for repo in repositories[:5]:  # Show first 5
                        print(f"      - {repo.get('name', 'Unknown')} ({repo.get('id', 'No ID')})")
                    return {"success": True, "repositories": repositories}
                else:
                    print("   ⚠️  No repositories found")
                    return {"success": True, "repositories": []}
            else:
                print(f"   ❌ Failed to get repositories: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"   ❌ Error getting repositories: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive documentation testing"""
        print("🧪 Running Comprehensive Documentation Tests")
        print("=" * 60)
        
        results = {}
        
        # Test 1: AI Provider Configuration
        results["ai_provider"] = await self.test_ai_provider_configuration()
        print()
        
        # Test 2: Get repositories
        results["repositories"] = await self.test_repository_list()
        print()
        
        if not results["repositories"]["success"] or not results["repositories"]["repositories"]:
            print("❌ Cannot continue testing - no repositories available")
            return results
        
        # Use first repository for testing
        test_repo = results["repositories"]["repositories"][0]
        repo_id = test_repo.get("id")
        repo_name = test_repo.get("name", "Unknown")
        
        print(f"🎯 Using repository for testing: {repo_name} ({repo_id})")
        print()
        
        # Test 3: Documentation Generation
        results["generation"] = await self.test_documentation_generation(repo_id)
        print()
        
        # Test 4: Documentation Retrieval
        results["retrieval"] = await self.test_documentation_retrieval(repo_id)
        print()
        
        # Test 5: Documentation Persistence
        results["persistence"] = await self.test_documentation_persistence(repo_id)
        print()
        
        # Summary
        print("📊 Test Summary")
        print("-" * 30)
        
        all_passed = True
        for test_name, test_result in results.items():
            if isinstance(test_result, dict) and test_result.get("success"):
                print(f"✅ {test_name.title()}: PASSED")
            else:
                print(f"❌ {test_name.title()}: FAILED")
                all_passed = False
        
        print()
        if all_passed:
            print("🎉 ALL TESTS PASSED! Documentation system is working correctly.")
        else:
            print("⚠️  SOME TESTS FAILED. Please check the issues above.")
        
        return results
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

async def main():
    """Main test function"""
    tester = DocumentationTester()
    
    try:
        results = await tester.run_comprehensive_test()
        return results
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())