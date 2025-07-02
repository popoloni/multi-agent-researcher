#!/usr/bin/env python3
"""
Test Documentation Volatility Fix
Specifically tests the navigation scenario: Documentation → Functionalities → Documentation
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

class DocumentationVolatilityTester:
    def __init__(self, base_url: str = "http://localhost:12000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def test_navigation_persistence(self, repo_id: str) -> Dict[str, Any]:
        """Test documentation persistence through navigation scenario"""
        print("🔄 Testing Documentation Volatility Fix")
        print("=" * 60)
        
        results = {
            "initial_load": None,
            "after_generation": None,
            "after_functionalities_call": None,
            "final_verification": None,
            "persistence_verified": False
        }
        
        try:
            # Step 1: Initial documentation load
            print("📖 Step 1: Initial documentation load")
            initial_response = await self.client.get(
                f"{self.base_url}/kenobi/repositories/{repo_id}/documentation"
            )
            
            if initial_response.status_code == 200:
                initial_data = initial_response.json()
                results["initial_load"] = {
                    "status": "success",
                    "has_documentation": bool(initial_data.get("documentation")),
                    "doc_keys": list(initial_data.get("documentation", {}).keys()) if isinstance(initial_data.get("documentation"), dict) else []
                }
                print(f"   ✅ Initial load: {results['initial_load']['has_documentation']}")
            else:
                results["initial_load"] = {"status": "failed", "code": initial_response.status_code}
                print(f"   ❌ Initial load failed: {initial_response.status_code}")
            
            # Step 2: Generate documentation if not present
            if not results["initial_load"]["has_documentation"]:
                print("📝 Step 2: Generating documentation")
                gen_response = await self.client.post(
                    f"{self.base_url}/kenobi/repositories/{repo_id}/documentation",
                    json={"branch": "main"}
                )
                
                if gen_response.status_code == 200:
                    task_id = gen_response.json().get("task_id")
                    print(f"   ⏳ Generation started, task ID: {task_id}")
                    
                    # Wait for completion
                    await self._wait_for_generation(repo_id, task_id)
                    
                    # Verify generation
                    after_gen_response = await self.client.get(
                        f"{self.base_url}/kenobi/repositories/{repo_id}/documentation"
                    )
                    
                    if after_gen_response.status_code == 200:
                        after_gen_data = after_gen_response.json()
                        results["after_generation"] = {
                            "status": "success",
                            "has_documentation": bool(after_gen_data.get("documentation")),
                            "doc_keys": list(after_gen_data.get("documentation", {}).keys()) if isinstance(after_gen_data.get("documentation"), dict) else []
                        }
                        print(f"   ✅ After generation: {results['after_generation']['has_documentation']}")
                    else:
                        results["after_generation"] = {"status": "failed", "code": after_gen_response.status_code}
                        print(f"   ❌ After generation check failed: {after_gen_response.status_code}")
                else:
                    results["after_generation"] = {"status": "failed", "code": gen_response.status_code}
                    print(f"   ❌ Generation failed: {gen_response.status_code}")
            else:
                results["after_generation"] = results["initial_load"]
                print("   ✅ Documentation already exists, skipping generation")
            
            # Step 3: Simulate functionalities page call (this is what causes the issue)
            print("🔧 Step 3: Simulating functionalities page access")
            func_response = await self.client.get(
                f"{self.base_url}/kenobi/repositories/{repo_id}/functionalities"
            )
            
            if func_response.status_code == 200:
                func_data = func_response.json()
                results["after_functionalities_call"] = {
                    "status": "success",
                    "functionalities_count": len(func_data.get("functionalities", []))
                }
                print(f"   ✅ Functionalities loaded: {results['after_functionalities_call']['functionalities_count']} items")
            else:
                results["after_functionalities_call"] = {"status": "failed", "code": func_response.status_code}
                print(f"   ❌ Functionalities call failed: {func_response.status_code}")
            
            # Step 4: Critical test - Check if documentation still exists after functionalities call
            print("🎯 Step 4: CRITICAL TEST - Documentation persistence after navigation")
            await asyncio.sleep(2)  # Small delay to simulate navigation timing
            
            final_response = await self.client.get(
                f"{self.base_url}/kenobi/repositories/{repo_id}/documentation"
            )
            
            if final_response.status_code == 200:
                final_data = final_response.json()
                results["final_verification"] = {
                    "status": "success",
                    "has_documentation": bool(final_data.get("documentation")),
                    "doc_keys": list(final_data.get("documentation", {}).keys()) if isinstance(final_data.get("documentation"), dict) else [],
                    "same_as_before": False
                }
                
                # Compare with previous state
                if results["after_generation"] and results["after_generation"]["status"] == "success":
                    before_keys = set(results["after_generation"]["doc_keys"])
                    after_keys = set(results["final_verification"]["doc_keys"])
                    results["final_verification"]["same_as_before"] = before_keys == after_keys
                
                print(f"   📊 Final documentation present: {results['final_verification']['has_documentation']}")
                print(f"   📊 Same as before navigation: {results['final_verification']['same_as_before']}")
                
                # Determine if persistence is verified
                results["persistence_verified"] = (
                    results["final_verification"]["has_documentation"] and
                    results["final_verification"]["same_as_before"]
                )
                
            else:
                results["final_verification"] = {"status": "failed", "code": final_response.status_code}
                print(f"   ❌ Final verification failed: {final_response.status_code}")
                results["persistence_verified"] = False
            
            # Step 5: Multiple rapid calls to test cache consistency
            print("⚡ Step 5: Testing cache consistency with rapid calls")
            consistency_results = []
            
            for i in range(5):
                rapid_response = await self.client.get(
                    f"{self.base_url}/kenobi/repositories/{repo_id}/documentation"
                )
                
                if rapid_response.status_code == 200:
                    rapid_data = rapid_response.json()
                    consistency_results.append({
                        "call": i + 1,
                        "has_documentation": bool(rapid_data.get("documentation")),
                        "doc_keys_count": len(rapid_data.get("documentation", {}).keys()) if isinstance(rapid_data.get("documentation"), dict) else 0
                    })
                else:
                    consistency_results.append({
                        "call": i + 1,
                        "has_documentation": False,
                        "error": rapid_response.status_code
                    })
                
                await asyncio.sleep(0.5)  # Small delay between calls
            
            # Check consistency
            has_docs = [r["has_documentation"] for r in consistency_results]
            doc_counts = [r.get("doc_keys_count", 0) for r in consistency_results if "doc_keys_count" in r]
            
            all_consistent = len(set(has_docs)) == 1 and len(set(doc_counts)) <= 1
            results["cache_consistency"] = {
                "results": consistency_results,
                "all_consistent": all_consistent,
                "has_documentation_consistent": len(set(has_docs)) == 1,
                "doc_count_consistent": len(set(doc_counts)) <= 1
            }
            
            print(f"   📊 Cache consistency: {all_consistent}")
            
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results["error"] = str(e)
            results["persistence_verified"] = False
        
        return results
    
    async def _wait_for_generation(self, repo_id: str, task_id: str, max_wait: int = 300):
        """Wait for documentation generation to complete"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                status_response = await self.client.get(
                    f"{self.base_url}/kenobi/repositories/{repo_id}/documentation/status/{task_id}"
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get("status")
                    progress = status_data.get("progress", 0)
                    
                    print(f"   ⏳ Generation progress: {progress}%")
                    
                    if status == "completed":
                        print("   ✅ Generation completed!")
                        return True
                    elif status == "failed":
                        print(f"   ❌ Generation failed: {status_data.get('error', 'Unknown error')}")
                        return False
                
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"   ⚠️  Error checking generation status: {e}")
                await asyncio.sleep(5)
        
        print("   ⏰ Generation timed out")
        return False
    
    async def run_comprehensive_volatility_test(self) -> Dict[str, Any]:
        """Run comprehensive volatility test"""
        print("🧪 Documentation Volatility Test Suite")
        print("=" * 60)
        
        # Get repositories
        try:
            repos_response = await self.client.get(f"{self.base_url}/kenobi/repositories")
            if repos_response.status_code != 200:
                return {"error": "Failed to get repositories", "code": repos_response.status_code}
            
            repositories = repos_response.json().get("repositories", [])
            if not repositories:
                return {"error": "No repositories found"}
            
            # Use first repository for testing
            test_repo = repositories[0]
            repo_id = test_repo.get("id")
            repo_name = test_repo.get("name", "Unknown")
            
            print(f"🎯 Testing with repository: {repo_name} ({repo_id})")
            print()
            
            # Run the navigation persistence test
            results = await self.test_navigation_persistence(repo_id)
            
            # Summary
            print()
            print("📊 TEST SUMMARY")
            print("-" * 40)
            
            if results.get("persistence_verified"):
                print("🎉 ✅ VOLATILITY ISSUE FIXED!")
                print("   Documentation persists through navigation")
            else:
                print("❌ ⚠️  VOLATILITY ISSUE STILL EXISTS")
                print("   Documentation does not persist through navigation")
            
            if results.get("cache_consistency", {}).get("all_consistent"):
                print("✅ Cache consistency verified")
            else:
                print("⚠️  Cache consistency issues detected")
            
            print()
            print("📋 Detailed Results:")
            for step, result in results.items():
                if step not in ["persistence_verified", "error"]:
                    status = "✅" if (isinstance(result, dict) and result.get("status") == "success") else "❌"
                    print(f"   {status} {step}: {result}")
            
            return results
            
        except Exception as e:
            return {"error": f"Test suite failed: {e}"}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

async def main():
    """Main test function"""
    tester = DocumentationVolatilityTester()
    
    try:
        results = await tester.run_comprehensive_volatility_test()
        return results
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())