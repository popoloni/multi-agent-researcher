#!/usr/bin/env python3
"""
CI/CD Test Runner for Multi-Agent Research System

This script is specifically designed for CI/CD environments and provides:
- Structured output for CI systems
- Fast execution with parallel testing
- Coverage reporting for quality gates
- Exit codes for CI pipeline integration
- Minimal output for CI logs

Usage:
    python scripts/ci_test_runner.py [options]
"""

import argparse
import subprocess
import sys
import time
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class CITestResult:
    """CI test result with structured data."""
    category: str
    success: bool
    duration: float
    tests_run: int
    tests_passed: int
    tests_failed: int
    coverage: Optional[float] = None
    error: Optional[str] = None


class CITestRunner:
    """CI/CD optimized test runner."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results: List[CITestResult] = []
        
        # CI-optimized test configurations
        self.test_configs = {
            "non-regression": {
                "command": ["python", "tests/run_non_regression_tests.py", "--validate"],
                "timeout": 30,
                "critical": True,
                "description": "Critical functionality validation"
            },
            "unit": {
                "command": ["python", "-m", "pytest", "tests/unit/", "--cov=app", "--cov-report=term-missing", "-q"],
                "timeout": 60,
                "critical": False,
                "description": "Unit tests with coverage"
            },
            "integration": {
                "command": ["python", "-m", "pytest", "tests/integration/", "-q"],
                "timeout": 90,
                "critical": False,
                "description": "Integration tests"
            },
            "api": {
                "command": ["python", "-m", "pytest", "tests/api/", "-q"],
                "timeout": 60,
                "critical": False,
                "description": "API endpoint tests"
            },
            "agents": {
                "command": ["python", "-m", "pytest", "tests/agents/", "-q"],
                "timeout": 60,
                "critical": False,
                "description": "Agent tests"
            },
            "e2e": {
                "command": ["python", "-m", "pytest", "tests/e2e/", "-q"],
                "timeout": 120,
                "critical": False,
                "description": "End-to-end tests"
            },
            "frontend": {
                "command": ["npm", "run", "test:ci"],
                "timeout": 90,
                "critical": False,
                "description": "Frontend tests",
                "cwd": "frontend"
            }
        }
    
    def run_ci_test(self, category: str, config: Dict) -> CITestResult:
        """Run a single CI test category."""
        print(f"🧪 Running {config['description']}...")
        
        start_time = time.time()
        
        try:
            # Run the test command
            result = subprocess.run(
                config["command"],
                cwd=config.get("cwd", self.project_root),
                capture_output=True,
                text=True,
                timeout=config["timeout"]
            )
            
            duration = time.time() - start_time
            
            # Parse test results
            tests_run, tests_passed, tests_failed = self.parse_test_output(result.stdout, result.stderr)
            
            # Extract coverage if available
            coverage = self.extract_coverage(result.stdout)
            
            # Determine success
            success = result.returncode == 0 and tests_failed == 0
            
            return CITestResult(
                category=category,
                success=success,
                duration=duration,
                tests_run=tests_run,
                tests_passed=tests_passed,
                tests_failed=tests_failed,
                coverage=coverage,
                error=result.stderr if not success else None
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return CITestResult(
                category=category,
                success=False,
                duration=duration,
                tests_run=0,
                tests_passed=0,
                tests_failed=1,
                error=f"Test timed out after {config['timeout']} seconds"
            )
        except Exception as e:
            duration = time.time() - start_time
            return CITestResult(
                category=category,
                success=False,
                duration=duration,
                tests_run=0,
                tests_passed=0,
                tests_failed=1,
                error=str(e)
            )
    
    def parse_test_output(self, stdout: str, stderr: str) -> tuple[int, int, int]:
        """Parse test output to extract test counts."""
        # Default values
        tests_run = 0
        tests_passed = 0
        tests_failed = 0
        
        if stdout:
            # Look for pytest summary
            import re
            
            # Pytest summary pattern
            summary_match = re.search(r'=+ (.*?) in (.*?) =+', stdout)
            if summary_match:
                summary_text = summary_match.group(1)
                
                # Extract test counts
                passed_match = re.search(r'(\d+) passed', summary_text)
                failed_match = re.search(r'(\d+) failed', summary_text)
                error_match = re.search(r'(\d+) error', summary_text)
                
                if passed_match:
                    tests_passed = int(passed_match.group(1))
                if failed_match:
                    tests_failed = int(failed_match.group(1))
                if error_match:
                    tests_failed += int(error_match.group(1))
                
                tests_run = tests_passed + tests_failed
        
        return tests_run, tests_passed, tests_failed
    
    def extract_coverage(self, output: str) -> Optional[float]:
        """Extract coverage percentage from output."""
        if output:
            import re
            coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
            if coverage_match:
                return float(coverage_match.group(1))
        return None
    
    def run_backend_tests(self, categories: List[str] = None) -> List[CITestResult]:
        """Run backend tests in CI mode."""
        if categories is None:
            categories = ["non-regression", "unit", "integration", "api", "agents", "e2e"]
        
        results = []
        
        for category in categories:
            if category not in self.test_configs:
                print(f"⚠️  Unknown test category: {category}")
                continue
            
            config = self.test_configs[category]
            result = self.run_ci_test(category, config)
            results.append(result)
            
            # Print result
            status = "✅ PASSED" if result.success else "❌ FAILED"
            print(f"{status} | {category.upper()} | {result.duration:.2f}s | {result.tests_passed}/{result.tests_run} tests")
            
            if result.coverage:
                print(f"  Coverage: {result.coverage:.1f}%")
            
            if result.error:
                print(f"  Error: {result.error}")
            
            # Stop on critical failures
            if config.get("critical") and not result.success:
                print(f"❌ Critical test category '{category}' failed. Stopping execution.")
                break
        
        return results
    
    def run_frontend_tests(self) -> CITestResult:
        """Run frontend tests in CI mode."""
        config = self.test_configs["frontend"]
        result = self.run_ci_test("frontend", config)
        
        status = "✅ PASSED" if result.success else "❌ FAILED"
        print(f"{status} | FRONTEND | {result.duration:.2f}s | {result.tests_passed}/{result.tests_run} tests")
        
        if result.coverage:
            print(f"  Coverage: {result.coverage:.1f}%")
        
        if result.error:
            print(f"  Error: {result.error}")
        
        return result
    
    def generate_coverage_report(self) -> CITestResult:
        """Generate comprehensive coverage report for CI."""
        print("📊 Generating coverage report...")
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                "python", "-m", "pytest",
                "--cov=app",
                "--cov-report=xml:coverage.xml",
                "--cov-report=term-missing",
                "--cov-fail-under=70",
                "-q"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=120)
            
            duration = time.time() - start_time
            coverage = self.extract_coverage(result.stdout)
            success = result.returncode == 0
            
            return CITestResult(
                category="coverage",
                success=success,
                duration=duration,
                tests_run=1,
                tests_passed=1 if success else 0,
                tests_failed=0 if success else 1,
                coverage=coverage,
                error=result.stderr if not success else None
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return CITestResult(
                category="coverage",
                success=False,
                duration=duration,
                tests_run=1,
                tests_passed=0,
                tests_failed=1,
                error=str(e)
            )
    
    def generate_ci_summary(self) -> Dict:
        """Generate CI-optimized summary."""
        total_tests = sum(r.tests_run for r in self.results)
        total_passed = sum(r.tests_passed for r in self.results)
        total_failed = sum(r.tests_failed for r in self.results)
        total_duration = sum(r.duration for r in self.results)
        
        # Calculate overall coverage
        coverage_results = [r.coverage for r in self.results if r.coverage is not None]
        overall_coverage = sum(coverage_results) / len(coverage_results) if coverage_results else None
        
        # Check if all categories passed
        all_passed = all(r.success for r in self.results)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "overall_coverage": overall_coverage,
            "all_passed": all_passed,
            "categories": [asdict(r) for r in self.results]
        }
    
    def print_ci_summary(self, summary: Dict):
        """Print CI-optimized summary."""
        print("\n" + "=" * 60)
        print("CI TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        print(f"📅 Timestamp: {summary['timestamp']}")
        print(f"⏱️  Total Duration: {summary['total_duration']:.2f}s")
        print(f"📊 Tests: {summary['total_passed']}/{summary['total_tests']} passed")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['overall_coverage']:
            print(f"🎯 Overall Coverage: {summary['overall_coverage']:.1f}%")
        
        print(f"\n📋 Category Results:")
        for result in self.results:
            status = "✅" if result.success else "❌"
            print(f"  {status} {result.category.upper()}: {result.tests_passed}/{result.tests_run} tests ({result.duration:.2f}s)")
            if result.coverage:
                print(f"    Coverage: {result.coverage:.1f}%")
        
        if summary['all_passed']:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n❌ {summary['total_failed']} tests failed")
    
    def save_ci_report(self, summary: Dict, filename: str = "ci_test_report.json"):
        """Save CI test report."""
        report_path = self.project_root / "test-reports" / filename
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 CI test report saved to: {report_path}")
    
    def run_ci_tests(self, 
                    backend_only: bool = False,
                    frontend_only: bool = False,
                    categories: List[str] = None,
                    coverage: bool = True,
                    save_report: bool = True) -> bool:
        """Run CI tests and return success status."""
        
        print("🚀 CI Test Execution Started")
        print("=" * 40)
        
        # Run backend tests
        if not frontend_only:
            backend_results = self.run_backend_tests(categories)
            self.results.extend(backend_results)
        
        # Run frontend tests
        if not backend_only:
            frontend_result = self.run_frontend_tests()
            self.results.append(frontend_result)
        
        # Generate coverage report
        if coverage:
            coverage_result = self.generate_coverage_report()
            self.results.append(coverage_result)
        
        # Generate and print summary
        summary = self.generate_ci_summary()
        self.print_ci_summary(summary)
        
        # Save report
        if save_report:
            self.save_ci_report(summary)
        
        return summary['all_passed']


def main():
    """Main entry point for CI test runner."""
    parser = argparse.ArgumentParser(
        description="CI/CD Test Runner for Multi-Agent Research System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Run only backend tests"
    )
    
    parser.add_argument(
        "--frontend-only",
        action="store_true",
        help="Run only frontend tests"
    )
    
    parser.add_argument(
        "--categories",
        nargs="+",
        choices=["non-regression", "unit", "integration", "api", "agents", "e2e"],
        help="Run specific test categories"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage report generation"
    )
    
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Don't save CI test report"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only non-regression tests (fastest)"
    )
    
    args = parser.parse_args()
    
    runner = CITestRunner()
    
    try:
        # Determine test categories
        categories = None
        if args.quick:
            categories = ["non-regression"]
        elif args.categories:
            categories = args.categories
        
        # Run CI tests
        success = runner.run_ci_tests(
            backend_only=args.backend_only,
            frontend_only=args.frontend_only,
            categories=categories,
            coverage=not args.no_coverage,
            save_report=not args.no_report
        )
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ CI test execution interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 