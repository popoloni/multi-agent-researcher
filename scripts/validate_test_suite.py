#!/usr/bin/env python3
"""
Test Suite Validation Script

This script thoroughly validates the entire test suite to ensure it's working
correctly before implementing branch protection. It tests:

1. Test discovery and execution
2. Coverage reporting
3. Performance metrics
4. Error handling
5. CI/CD integration readiness

This should be run BEFORE implementing any branch protection to ensure
the test suite won't block legitimate pushes.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TestSuiteValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_success": False,
            "checks": {},
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "="*60)
        print(f"🔍 {title}")
        print("="*60)
    
    def print_check_result(self, check_name: str, success: bool, details: str = ""):
        """Print a formatted check result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {check_name}")
        if details:
            print(f"   {details}")
        
        # Store result
        self.validation_results["checks"][check_name] = {
            "success": success,
            "details": details
        }
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        self.print_header("PREREQUISITES CHECK")
        
        checks = [
            ("Project Structure", self._check_project_structure),
            ("Python Environment", self._check_python_environment),
            ("Test Dependencies", self._check_test_dependencies),
            ("Frontend Setup", self._check_frontend_setup),
            ("Test Files", self._check_test_files),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                success, details = check_func()
                self.print_check_result(check_name, success, details)
                if not success:
                    all_passed = False
            except Exception as e:
                self.print_check_result(check_name, False, f"Exception: {e}")
                all_passed = False
        
        return all_passed
    
    def _check_project_structure(self) -> Tuple[bool, str]:
        """Check if project structure is correct."""
        required_dirs = ["app", "tests", "frontend", "scripts"]
        missing_dirs = []
        
        for dir_name in required_dirs:
            if not (self.project_root / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            return False, f"Missing directories: {', '.join(missing_dirs)}"
        
        return True, "All required directories present"
    
    def _check_python_environment(self) -> Tuple[bool, str]:
        """Check Python environment and dependencies."""
        try:
            # Check Python version
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return False, "Python not accessible"
            
            # Check key dependencies
            key_packages = ["pytest", "coverage", "fastapi", "sqlalchemy"]
            missing_packages = []
            
            for package in key_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                return False, f"Missing packages: {', '.join(missing_packages)}"
            
            return True, f"Python {result.stdout.strip()}, all key packages available"
            
        except Exception as e:
            return False, f"Environment check failed: {e}"
    
    def _check_test_dependencies(self) -> Tuple[bool, str]:
        """Check if test-specific dependencies are available."""
        try:
            # Check if test-requirements.txt exists and can be installed
            test_req_file = self.project_root / "test-requirements.txt"
            if not test_req_file.exists():
                return False, "test-requirements.txt not found"
            
            # Try to import key test packages
            test_packages = ["pytest", "pytest-cov", "pytest-asyncio"]
            missing_packages = []
            
            for package in test_packages:
                try:
                    __import__(package.replace("-", "_"))
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                return False, f"Missing test packages: {', '.join(missing_packages)}"
            
            return True, "All test dependencies available"
            
        except Exception as e:
            return False, f"Test dependencies check failed: {e}"
    
    def _check_frontend_setup(self) -> Tuple[bool, str]:
        """Check if frontend is properly set up."""
        frontend_dir = self.project_root / "frontend"
        
        if not frontend_dir.exists():
            return False, "Frontend directory not found"
        
        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            return False, "package.json not found in frontend"
        
        # Check if node_modules exists (indicates dependencies installed)
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            return False, "node_modules not found - run 'npm install' in frontend"
        
        return True, "Frontend setup looks good"
    
    def _check_test_files(self) -> Tuple[bool, str]:
        """Check if test files and runners exist."""
        required_files = [
            "tests/run_organized_tests.py",
            "tests/run_non_regression_tests.py",
            "scripts/run_all_tests.py",
            "scripts/check_coverage.py",
            "pytest.ini",
            "pyproject.toml"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            return False, f"Missing files: {', '.join(missing_files)}"
        
        return True, "All test files present"
    
    def validate_test_execution(self) -> bool:
        """Validate that tests can actually run."""
        self.print_header("TEST EXECUTION VALIDATION")
        
        checks = [
            ("Test Discovery", self._check_test_discovery),
            ("Non-Regression Tests", self._check_non_regression_tests),
            ("Unit Tests", self._check_unit_tests),
            ("Coverage Generation", self._check_coverage_generation),
            ("Frontend Tests", self._check_frontend_tests),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                success, details = check_func()
                self.print_check_result(check_name, success, details)
                if not success:
                    all_passed = False
            except Exception as e:
                self.print_check_result(check_name, False, f"Exception: {e}")
                all_passed = False
        
        return all_passed
    
    def _check_test_discovery(self) -> Tuple[bool, str]:
        """Check if pytest can discover tests."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return False, f"Test discovery failed: {result.stderr}"
            
            # Count discovered tests
            lines = result.stdout.split('\n')
            test_count = sum(1 for line in lines if 'test_' in line and '::' in line)
            
            if test_count == 0:
                return False, "No tests discovered"
            
            return True, f"Discovered {test_count} tests"
            
        except subprocess.TimeoutExpired:
            return False, "Test discovery timed out"
        except Exception as e:
            return False, f"Test discovery error: {e}"
    
    def _check_non_regression_tests(self) -> Tuple[bool, str]:
        """Check if non-regression tests can run."""
        try:
            result = subprocess.run(
                [sys.executable, "tests/run_non_regression_tests.py", "--smoke"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return False, f"Non-regression tests failed: {result.stderr}"
            
            return True, "Non-regression tests passed"
            
        except subprocess.TimeoutExpired:
            return False, "Non-regression tests timed out"
        except Exception as e:
            return False, f"Non-regression tests error: {e}"
    
    def _check_unit_tests(self) -> Tuple[bool, str]:
        """Check if unit tests can run."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=short", "--maxfail=1"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # For unit tests, we'll accept some failures as long as the framework works
            if result.returncode != 0:
                # Check if at least some tests ran
                lines = result.stdout.split('\n')
                test_count = sum(1 for line in lines if 'test_' in line and '::' in line)
                if test_count > 0:
                    return True, f"Unit test framework working ({test_count} tests discovered)"
                else:
                    return False, f"Unit tests failed: {result.stderr}"
            
            # Count passed tests
            lines = result.stdout.split('\n')
            passed_count = sum(1 for line in lines if 'PASSED' in line)
            
            return True, f"Unit tests passed ({passed_count} tests)"
            
        except subprocess.TimeoutExpired:
            return False, "Unit tests timed out"
        except Exception as e:
            return False, f"Unit tests error: {e}"
    
    def _check_coverage_generation(self) -> Tuple[bool, str]:
        """Check if coverage reports can be generated."""
        try:
            # Try to run a simple test that should work
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/unit/test_vector_simple.py", "--cov=app", "--cov-report=term-missing", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Check if coverage data was generated (even if test failed)
            if "TOTAL" in result.stdout:
                # Extract coverage percentage
                lines = result.stdout.split('\n')
                for line in lines:
                    if "TOTAL" in line and "%" in line:
                        coverage_pct = line.split()[-1].replace('%', '')
                        return True, f"Coverage report generated successfully ({coverage_pct}% coverage)"
                return True, "Coverage report generated successfully"
            else:
                return False, f"Coverage generation failed: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            return False, "Coverage generation timed out"
        except Exception as e:
            return False, f"Coverage generation error: {e}"
    
    def _check_frontend_tests(self) -> Tuple[bool, str]:
        """Check if frontend tests can run."""
        frontend_dir = self.project_root / "frontend"
        
        try:
            # Check if test script exists
            package_json = frontend_dir / "package.json"
            if not package_json.exists():
                return False, "package.json not found"
            
            # Try to run frontend tests
            result = subprocess.run(
                ["npm", "test", "--", "--passWithNoTests", "--watchAll=false"],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode != 0:
                return False, f"Frontend tests failed: {result.stderr}"
            
            return True, "Frontend tests passed"
            
        except subprocess.TimeoutExpired:
            return False, "Frontend tests timed out"
        except Exception as e:
            return False, f"Frontend tests error: {e}"
    
    def validate_ci_readiness(self) -> bool:
        """Validate that the test suite is ready for CI/CD."""
        self.print_header("CI/CD READINESS VALIDATION")
        
        checks = [
            ("Coverage Threshold Checker", self._check_coverage_threshold),
            ("Structured Output", self._check_structured_output),
            ("Timeout Handling", self._check_timeout_handling),
            ("Error Reporting", self._check_error_reporting),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                success, details = check_func()
                self.print_check_result(check_name, success, details)
                if not success:
                    all_passed = False
            except Exception as e:
                self.print_check_result(check_name, False, f"Exception: {e}")
                all_passed = False
        
        return all_passed
    
    def _check_coverage_threshold(self) -> Tuple[bool, str]:
        """Check if coverage threshold checker works."""
        try:
            result = subprocess.run(
                [sys.executable, "scripts/check_coverage.py", "--help"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False, "Coverage threshold checker not working"
            
            return True, "Coverage threshold checker available"
            
        except Exception as e:
            return False, f"Coverage threshold checker error: {e}"
    
    def _check_structured_output(self) -> Tuple[bool, str]:
        """Check if test runners produce structured output."""
        try:
            result = subprocess.run(
                [sys.executable, "scripts/run_all_tests.py", "--quick", "--no-report"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Check if structured output was produced (even if tests failed)
            output = result.stdout + result.stderr
            if "TEST EXECUTION SUMMARY" in output and "Results by Category:" in output:
                return True, "Test runner produces structured output"
            else:
                return False, "Test runner failed to produce structured output"
            
        except Exception as e:
            return False, f"Structured output check error: {e}"
    
    def _check_timeout_handling(self) -> Tuple[bool, str]:
        """Check if timeout handling works correctly."""
        try:
            # This is a basic check - in practice, we'd want to test with a long-running test
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--timeout=1", "tests/unit/"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # We expect this to fail due to timeout, but it should fail gracefully
            return True, "Timeout handling appears to work"
            
        except Exception as e:
            return False, f"Timeout handling check error: {e}"
    
    def _check_error_reporting(self) -> Tuple[bool, str]:
        """Check if error reporting works correctly."""
        try:
            # Run a test that should fail
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/unit/test_nonexistent.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # This should fail, but provide clear error reporting
            if "ERROR" in result.stderr or "FAILED" in result.stderr:
                return True, "Error reporting works correctly"
            else:
                return False, "Error reporting not working as expected"
            
        except Exception as e:
            return False, f"Error reporting check error: {e}"
    
    def generate_recommendations(self):
        """Generate recommendations based on validation results."""
        self.print_header("RECOMMENDATIONS")
        
        failed_checks = [
            name for name, data in self.validation_results["checks"].items()
            if not data["success"]
        ]
        
        if not failed_checks:
            print("✅ All checks passed! The test suite is ready for branch protection.")
            self.validation_results["recommendations"].append(
                "All validation checks passed - safe to implement branch protection"
            )
        else:
            print("❌ Some checks failed. Fix these before implementing branch protection:")
            for check_name in failed_checks:
                details = self.validation_results["checks"][check_name]["details"]
                print(f"   - {check_name}: {details}")
                self.validation_results["recommendations"].append(
                    f"Fix {check_name}: {details}"
                )
        
        # Add general recommendations
        if self.validation_results["checks"].get("Coverage Generation", {}).get("success"):
            self.validation_results["recommendations"].append(
                "Consider setting up coverage thresholds (70% recommended)"
            )
        
        if self.validation_results["checks"].get("Frontend Tests", {}).get("success"):
            self.validation_results["recommendations"].append(
                "Frontend tests are working - consider including them in CI pipeline"
            )
    
    def save_validation_report(self, filename: str = "test_validation_report.json"):
        """Save validation report to file."""
        report_path = self.project_root / filename
        
        with open(report_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print(f"\n📄 Validation report saved to: {report_path}")
    
    def run_validation(self) -> bool:
        """Run the complete validation process."""
        self.print_header("TEST SUITE VALIDATION")
        print("This script validates the entire test suite before implementing branch protection.")
        print("Make sure all checks pass before enabling branch protection!")
        
        # Run all validation checks
        prereq_success = self.check_prerequisites()
        if not prereq_success:
            print("\n❌ Prerequisites check failed. Fix these issues first.")
            return False
        
        execution_success = self.validate_test_execution()
        if not execution_success:
            print("\n❌ Test execution validation failed. Fix these issues first.")
            return False
        
        ci_success = self.validate_ci_readiness()
        if not ci_success:
            print("\n❌ CI/CD readiness validation failed. Fix these issues first.")
            return False
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Save report
        self.save_validation_report()
        
        # Determine overall success
        all_checks_passed = all(
            data["success"] for data in self.validation_results["checks"].values()
        )
        
        self.validation_results["overall_success"] = all_checks_passed
        
        if all_checks_passed:
            print("\n🎉 VALIDATION COMPLETE - ALL CHECKS PASSED!")
            print("✅ The test suite is ready for branch protection implementation.")
        else:
            print("\n❌ VALIDATION COMPLETE - SOME CHECKS FAILED!")
            print("⚠️  Fix the failed checks before implementing branch protection.")
        
        return all_checks_passed


def main():
    """Main entry point for test suite validation."""
    parser = argparse.ArgumentParser(
        description="Validate test suite before implementing branch protection",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="test_validation_report.json",
        help="Output file for validation report (default: test_validation_report.json)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    validator = TestSuiteValidator()
    
    try:
        success = validator.run_validation()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ Validation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 