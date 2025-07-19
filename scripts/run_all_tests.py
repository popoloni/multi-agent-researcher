#!/usr/bin/env python3
"""
Automated Test Runner for Multi-Agent Research System

This script provides comprehensive automated test execution for:
- Backend tests (unit, integration, api, agents, e2e)
- Frontend tests (components, services)
- Non-regression tests
- Coverage reporting
- Performance testing

Usage:
    python scripts/run_all_tests.py [options]
"""

import argparse
import subprocess
import sys
import time
import os
import signal
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestResult:
    """Test execution result."""
    category: str
    success: bool
    duration: float
    output: str
    error: Optional[str] = None
    coverage: Optional[float] = None


class AutomatedTestRunner:
    """Comprehensive automated test runner."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
        # Test categories and their configurations
        self.test_categories = {
            "non-regression": {
                "description": "Critical functionality tests",
                "command": ["python", "tests/run_non_regression_tests.py"],
                "timeout": 60,
                "critical": True
            },
            "unit": {
                "description": "Unit tests",
                "command": ["python", "tests/run_organized_tests.py", "unit", "--coverage"],
                "timeout": 120,
                "critical": False
            },
            "integration": {
                "description": "Integration tests",
                "command": ["python", "tests/run_organized_tests.py", "integration"],
                "timeout": 180,
                "critical": False
            },
            "api": {
                "description": "API endpoint tests",
                "command": ["python", "tests/run_organized_tests.py", "api"],
                "timeout": 120,
                "critical": False
            },
            "agents": {
                "description": "Agent-specific tests",
                "command": ["python", "tests/run_organized_tests.py", "agents"],
                "timeout": 120,
                "critical": False
            },
            "e2e": {
                "description": "End-to-end tests",
                "command": ["python", "tests/run_organized_tests.py", "e2e"],
                "timeout": 300,
                "critical": False
            },
            "frontend": {
                "description": "Frontend component tests",
                "command": ["npm", "run", "test:ci"],
                "timeout": 180,
                "critical": False,
                "cwd": "frontend"
            }
        }
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "=" * 60)
        print(f"🚀 {title}")
        print("=" * 60)
    
    def print_result(self, result: TestResult):
        """Print a formatted test result."""
        status = "✅ PASSED" if result.success else "❌ FAILED"
        duration = f"{result.duration:.2f}s"
        
        print(f"\n{status} | {result.category.upper()} | {duration}")
        print("-" * 50)
        
        if result.error:
            print(f"Error: {result.error}")
        
        if result.coverage:
            print(f"Coverage: {result.coverage:.1f}%")
    
    def run_command(self, command: List[str], timeout: int, cwd: Optional[str] = None) -> TestResult:
        """Run a command and return the result."""
        category = command[0] if command else "unknown"
        start_time = time.time()
        
        try:
            # Run the command
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            duration = time.time() - start_time
            
            # Extract coverage if available
            coverage = None
            if result.stdout:
                # Look for coverage percentage in output
                import re
                coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', result.stdout)
                if coverage_match:
                    coverage = float(coverage_match.group(1))
            
            return TestResult(
                category=category,
                success=result.returncode == 0,
                duration=duration,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                coverage=coverage
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return TestResult(
                category=category,
                success=False,
                duration=duration,
                output="",
                error=f"Test timed out after {timeout} seconds"
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                category=category,
                success=False,
                duration=duration,
                output="",
                error=str(e)
            )
    
    def check_prerequisites(self) -> bool:
        """Check if prerequisites are met."""
        print("🔍 Checking prerequisites...")
        
        # Check if we're in the right directory
        if not (self.project_root / "app").exists():
            print("❌ Error: app directory not found. Please run from project root.")
            return False
        
        # Check if test directories exist
        test_dirs = ["tests/unit", "tests/integration", "tests/api", "tests/agents", "tests/e2e"]
        for test_dir in test_dirs:
            if not (self.project_root / test_dir).exists():
                print(f"❌ Error: {test_dir} directory not found.")
                return False
        
        # Check if test runners exist
        test_runners = [
            "tests/run_organized_tests.py",
            "tests/run_non_regression_tests.py"
        ]
        for runner in test_runners:
            if not (self.project_root / runner).exists():
                print(f"❌ Error: {runner} not found.")
                return False
        
        # Check if frontend exists
        if not (self.project_root / "frontend").exists():
            print("❌ Error: frontend directory not found.")
            return False
        
        print("✅ Prerequisites check passed")
        return True
    
    def run_backend_tests(self, categories: List[str] = None) -> List[TestResult]:
        """Run backend tests."""
        if categories is None:
            categories = ["non-regression", "unit", "integration", "api", "agents", "e2e"]
        
        results = []
        
        for category in categories:
            if category not in self.test_categories:
                print(f"⚠️  Unknown test category: {category}")
                continue
            
            config = self.test_categories[category]
            print(f"\n🧪 Running {config['description']}...")
            
            result = self.run_command(
                config["command"],
                config["timeout"],
                config.get("cwd")
            )
            
            result.category = category
            results.append(result)
            self.print_result(result)
            
            # Stop on critical failures
            if config.get("critical") and not result.success:
                print(f"❌ Critical test category '{category}' failed. Stopping execution.")
                break
        
        return results
    
    def run_frontend_tests(self) -> TestResult:
        """Run frontend tests."""
        print("\n🧪 Running frontend tests...")
        
        config = self.test_categories["frontend"]
        result = self.run_command(
            config["command"],
            config["timeout"],
            config["cwd"]
        )
        
        result.category = "frontend"
        self.print_result(result)
        return result
    
    def generate_coverage_report(self) -> TestResult:
        """Generate comprehensive coverage report."""
        print("\n📊 Generating coverage report...")
        
        start_time = time.time()
        
        try:
            # Run coverage for backend
            result = subprocess.run([
                "python", "-m", "pytest",
                "--cov=app",
                "--cov-report=html:htmlcov/automated",
                "--cov-report=xml:coverage.xml",
                "--cov-report=term-missing",
                "-q"
            ], cwd=self.project_root, capture_output=True, text=True, timeout=300)
            
            duration = time.time() - start_time
            
            # Extract coverage percentage
            coverage = None
            if result.stdout:
                import re
                coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', result.stdout)
                if coverage_match:
                    coverage = float(coverage_match.group(1))
            
            success = result.returncode == 0
            
            return TestResult(
                category="coverage",
                success=success,
                duration=duration,
                output=result.stdout,
                error=result.stderr if not success else None,
                coverage=coverage
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                category="coverage",
                success=False,
                duration=duration,
                output="",
                error=str(e)
            )
    
    def generate_summary_report(self) -> Dict:
        """Generate a summary report of all test results."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(r.duration for r in self.results)
        
        # Calculate overall coverage
        coverage_results = [r.coverage for r in self.results if r.coverage is not None]
        overall_coverage = sum(coverage_results) / len(coverage_results) if coverage_results else None
        
        # Group results by category
        results_by_category = {}
        for result in self.results:
            if result.category not in results_by_category:
                results_by_category[result.category] = []
            results_by_category[result.category].append(result)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "overall_coverage": overall_coverage,
            "results_by_category": results_by_category,
            "all_passed": failed_tests == 0
        }
    
    def print_summary(self, summary: Dict):
        """Print a formatted summary report."""
        self.print_header("TEST EXECUTION SUMMARY")
        
        print(f"📅 Timestamp: {summary['timestamp']}")
        print(f"⏱️  Total Duration: {summary['total_duration']:.2f}s")
        print(f"📊 Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['overall_coverage']:
            print(f"🎯 Overall Coverage: {summary['overall_coverage']:.1f}%")
        
        print(f"\n📋 Results by Category:")
        for category, results in summary['results_by_category'].items():
            passed = sum(1 for r in results if r.success)
            total = len(results)
            status = "✅" if passed == total else "❌"
            print(f"  {status} {category.upper()}: {passed}/{total} passed")
        
        if summary['all_passed']:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n❌ {summary['failed_tests']} test categories failed")
        
        # Print detailed results
        print(f"\n📝 Detailed Results:")
        for result in self.results:
            status = "✅" if result.success else "❌"
            duration = f"{result.duration:.2f}s"
            coverage_info = f" ({result.coverage:.1f}%)" if result.coverage else ""
            print(f"  {status} {result.category.upper()}: {duration}{coverage_info}")
    
    def save_report(self, summary: Dict, filename: str = "test_report.json"):
        """Save test report to file."""
        report_path = self.project_root / "test-reports" / filename
        report_path.parent.mkdir(exist_ok=True)
        
        # Convert dataclasses to dict for JSON serialization
        report_data = {
            "summary": summary,
            "detailed_results": [
                {
                    "category": r.category,
                    "success": r.success,
                    "duration": r.duration,
                    "coverage": r.coverage,
                    "error": r.error
                }
                for r in self.results
            ]
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Test report saved to: {report_path}")
        
        # Also save a CI-friendly version
        ci_report_path = self.project_root / "ci_test_results.json"
        ci_data = {
            "timestamp": summary["timestamp"],
            "overall_success": summary["all_passed"],
            "total_duration": summary["total_duration"],
            "success_rate": summary["success_rate"],
            "overall_coverage": summary["overall_coverage"],
            "test_results": [
                {
                    "type": r.category,
                    "success": r.success,
                    "duration": r.duration,
                    "coverage": r.coverage,
                    "error": r.error if not r.success else None
                }
                for r in self.results
            ]
        }
        
        with open(ci_report_path, 'w') as f:
            json.dump(ci_data, f, indent=2)
        
        print(f"📄 CI report saved to: {ci_report_path}")
        
        return ci_data
    
    def run_all_tests(self, 
                     backend_only: bool = False,
                     frontend_only: bool = False,
                     categories: List[str] = None,
                     coverage: bool = True,
                     save_report: bool = True) -> bool:
        """Run all tests and return success status."""
        
        self.print_header("AUTOMATED TEST EXECUTION")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
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
        summary = self.generate_summary_report()
        self.print_summary(summary)
        
        # Save report
        if save_report:
            self.save_report(summary)
        
        return summary['all_passed']


def main():
    """Main entry point for automated test runner."""
    parser = argparse.ArgumentParser(
        description="Automated Test Runner for Multi-Agent Research System",
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
        help="Don't save test report"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only non-regression tests (fastest)"
    )
    
    args = parser.parse_args()
    
    runner = AutomatedTestRunner()
    
    try:
        # Determine test categories
        categories = None
        if args.quick:
            categories = ["non-regression"]
        elif args.categories:
            categories = args.categories
        
        # Run tests
        success = runner.run_all_tests(
            backend_only=args.backend_only,
            frontend_only=args.frontend_only,
            categories=categories,
            coverage=not args.no_coverage,
            save_report=not args.no_report
        )
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ Test execution interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 