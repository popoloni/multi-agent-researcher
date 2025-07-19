#!/usr/bin/env python3
"""
Non-Regression Test Runner

This script runs the critical functionality tests that must always pass.
These tests are designed to be:
- Fast (complete in <30 seconds)
- Reliable (no flaky tests)
- Comprehensive (cover all critical functionality)
- Non-destructive (don't modify production data)

Usage:
    python tests/run_non_regression_tests.py [options]
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional


class NonRegressionTestRunner:
    """Runner for non-regression tests."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_file = self.project_root / "tests" / "e2e" / "test_critical_functionality.py"
        
    def run_critical_tests(self, verbose: bool = False, coverage: bool = False) -> int:
        """Run critical functionality tests."""
        print("🚀 Running Non-Regression Test Suite...")
        print("=" * 50)
        
        start_time = time.time()
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_file),
            "--tb=short",
            "--maxfail=1",
            "--durations=10"
        ]
        
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        if coverage:
            cmd.extend([
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov/critical",
                "--cov-fail-under=70"
            ])
        
        try:
            # Run tests
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=not verbose,
                text=True
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n⏱️  Test execution time: {duration:.2f} seconds")
            
            if result.returncode == 0:
                print("✅ All critical functionality tests passed!")
                return 0
            else:
                print("❌ Critical functionality tests failed!")
                if not verbose:
                    print("Error output:")
                    print(result.stderr)
                return result.returncode
                
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return 1
    
    def run_smoke_tests(self) -> int:
        """Run quick smoke tests for basic functionality."""
        print("🔥 Running Smoke Tests...")
        print("=" * 30)
        
        smoke_tests = [
            "tests/e2e/test_critical_functionality.py::TestCriticalApplicationStartup::test_application_starts_successfully",
            "tests/e2e/test_critical_functionality.py::TestCriticalApplicationStartup::test_health_endpoint_responds",
            "tests/e2e/test_critical_functionality.py::TestCriticalAPIEndpoints::test_repositories_api_endpoint"
        ]
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-q",
            "--tb=short",
            "--maxfail=1"
        ] + smoke_tests
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Smoke tests passed!")
                return 0
            else:
                print("❌ Smoke tests failed!")
                print(result.stderr)
                return result.returncode
                
        except Exception as e:
            print(f"❌ Error running smoke tests: {e}")
            return 1
    
    def run_performance_tests(self) -> int:
        """Run performance tests for critical endpoints."""
        print("⚡ Running Performance Tests...")
        print("=" * 35)
        
        performance_tests = [
            "tests/e2e/test_critical_functionality.py::TestCriticalPerformance"
        ]
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-v",
            "--tb=short",
            "--benchmark-only"
        ] + performance_tests
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Performance tests passed!")
                return 0
            else:
                print("❌ Performance tests failed!")
                return result.returncode
                
        except Exception as e:
            print(f"❌ Error running performance tests: {e}")
            return 1
    
    def list_critical_tests(self) -> None:
        """List all critical tests."""
        print("📋 Critical Functionality Tests:")
        print("=" * 40)
        
        test_categories = [
            "Application Startup",
            "Repository Operations", 
            "Documentation Generation",
            "Chat Functionality",
            "Research System",
            "API Endpoints",
            "Frontend Components",
            "System Integration",
            "Error Handling",
            "Performance"
        ]
        
        for i, category in enumerate(test_categories, 1):
            print(f"{i:2d}. {category}")
        
        print(f"\nTotal test categories: {len(test_categories)}")
        print("Run with --verbose to see individual test details")
    
    def validate_test_file(self) -> bool:
        """Validate that the critical test file exists."""
        if not self.test_file.exists():
            print(f"❌ Critical test file not found: {self.test_file}")
            return False
        
        print(f"✅ Critical test file found: {self.test_file}")
        return True


def main():
    """Main entry point for non-regression test runner."""
    parser = argparse.ArgumentParser(
        description="Non-Regression Test Runner for Multi-Agent Research System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run only smoke tests (fastest)"
    )
    
    parser.add_argument(
        "--performance",
        action="store_true", 
        help="Run performance tests"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List critical test categories"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate test file exists"
    )
    
    args = parser.parse_args()
    
    runner = NonRegressionTestRunner()
    
    try:
        if args.validate:
            success = runner.validate_test_file()
            sys.exit(0 if success else 1)
        
        if args.list:
            runner.list_critical_tests()
            return
        
        if args.smoke:
            exit_code = runner.run_smoke_tests()
        elif args.performance:
            exit_code = runner.run_performance_tests()
        else:
            exit_code = runner.run_critical_tests(
                verbose=args.verbose,
                coverage=args.coverage
            )
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n❌ Test execution interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 