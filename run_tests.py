#!/usr/bin/env python3
"""
Test runner script for the Multi-Agent Research System.

This script provides easy commands for running different types of tests
with various options and configurations.

Usage:
    python run_tests.py [command] [options]

Commands:
    all              Run all tests
    unit             Run unit tests only
    integration      Run integration tests only
    api              Run API tests only
    frontend         Run frontend tests only
    coverage         Run tests with coverage report
    fast             Run fast tests only (exclude slow)
    slow             Run slow tests only
    report           Generate test reports
    clean            Clean test artifacts
    install          Install test dependencies
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """Test runner for the Multi-Agent Research System."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tests_dir = self.project_root / "tests"
        self.frontend_dir = self.project_root / "frontend"
        
    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> int:
        """Run a shell command and return exit code."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            return 0
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {' '.join(command)}")
            print(f"Exit code: {e.returncode}")
            print(f"Error output: {e.stderr}")
            return e.returncode
    
    def install_dependencies(self) -> int:
        """Install test dependencies."""
        print("Installing test dependencies...")
        
        # Install Python test dependencies
        if (self.project_root / "test-requirements.txt").exists():
            result = self.run_command([
                sys.executable, "-m", "pip", "install", "-r", "test-requirements.txt"
            ])
            if result != 0:
                return result
        
        # Install frontend test dependencies
        if self.frontend_dir.exists():
            print("Installing frontend test dependencies...")
            result = self.run_command(["npm", "install"], cwd=self.frontend_dir)
            if result != 0:
                return result
        
        print("✅ Test dependencies installed successfully")
        return 0
    
    def run_backend_tests(self, test_type: str = "all", coverage: bool = False, 
                         parallel: bool = False, html_report: bool = False) -> int:
        """Run backend tests with specified options."""
        print(f"Running backend tests: {test_type}")
        
        # Build pytest command
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test path based on type
        if test_type == "unit":
            cmd.append("tests/unit/")
        elif test_type == "integration":
            cmd.append("tests/integration/")
        elif test_type == "api":
            cmd.append("tests/api/")
        elif test_type == "agents":
            cmd.append("tests/agents/")
        elif test_type == "fast":
            cmd.extend(["-m", "not slow"])
        elif test_type == "slow":
            cmd.extend(["-m", "slow"])
        else:
            cmd.append("tests/")
        
        # Add coverage if requested
        if coverage:
            cmd.extend([
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-report=xml:coverage.xml",
                "--cov-fail-under=70"
            ])
        
        # Add parallel execution if requested
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Add HTML report if requested
        if html_report:
            cmd.extend([
                "--html=test-reports/report.html",
                "--self-contained-html"
            ])
        
        return self.run_command(cmd)
    
    def run_frontend_tests(self, coverage: bool = False, watch: bool = False) -> int:
        """Run frontend tests with specified options."""
        if not self.frontend_dir.exists():
            print("❌ Frontend directory not found")
            return 1
        
        print("Running frontend tests...")
        
        # Build npm test command
        cmd = ["npm", "test"]
        
        if coverage:
            cmd.extend(["--", "--coverage", "--watchAll=false"])
        elif watch:
            cmd.extend(["--", "--watch"])
        else:
            cmd.extend(["--", "--watchAll=false"])
        
        return self.run_command(cmd, cwd=self.frontend_dir)
    
    def run_all_tests(self, coverage: bool = False, parallel: bool = False) -> int:
        """Run all tests (backend and frontend)."""
        print("Running all tests...")
        
        # Run backend tests
        backend_result = self.run_backend_tests(
            coverage=coverage, 
            parallel=parallel,
            html_report=True
        )
        
        if backend_result != 0:
            print("❌ Backend tests failed")
            return backend_result
        
        # Run frontend tests
        frontend_result = self.run_frontend_tests(coverage=coverage)
        
        if frontend_result != 0:
            print("❌ Frontend tests failed")
            return frontend_result
        
        print("✅ All tests passed")
        return 0
    
    def generate_reports(self) -> int:
        """Generate test reports."""
        print("Generating test reports...")
        
        # Create reports directory
        reports_dir = self.project_root / "test-reports"
        reports_dir.mkdir(exist_ok=True)
        
        # Generate backend test report
        backend_result = self.run_backend_tests(
            coverage=True,
            html_report=True
        )
        
        if backend_result != 0:
            print("❌ Failed to generate backend reports")
            return backend_result
        
        # Generate frontend test report
        frontend_result = self.run_frontend_tests(coverage=True)
        
        if frontend_result != 0:
            print("❌ Failed to generate frontend reports")
            return frontend_result
        
        print("✅ Test reports generated successfully")
        print(f"📊 Reports available in: {reports_dir}")
        return 0
    
    def clean_artifacts(self) -> int:
        """Clean test artifacts."""
        print("Cleaning test artifacts...")
        
        artifacts = [
            "htmlcov",
            "coverage.xml",
            ".coverage",
            "test-reports",
            "test_kenobi.db",
            "__pycache__",
            ".pytest_cache"
        ]
        
        for artifact in artifacts:
            artifact_path = self.project_root / artifact
            if artifact_path.exists():
                if artifact_path.is_file():
                    artifact_path.unlink()
                else:
                    import shutil
                    shutil.rmtree(artifact_path)
                print(f"🧹 Cleaned: {artifact}")
        
        # Clean frontend artifacts
        if self.frontend_dir.exists():
            frontend_artifacts = [
                "coverage",
                "node_modules/.cache"
            ]
            
            for artifact in frontend_artifacts:
                artifact_path = self.frontend_dir / artifact
                if artifact_path.exists():
                    import shutil
                    shutil.rmtree(artifact_path)
                    print(f"🧹 Cleaned frontend: {artifact}")
        
        print("✅ Test artifacts cleaned successfully")
        return 0


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Test runner for Multi-Agent Research System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "command",
        choices=[
            "all", "unit", "integration", "api", "frontend", 
            "coverage", "fast", "slow", "report", "clean", "install"
        ],
        help="Test command to run"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run tests in watch mode (frontend only)"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        if args.command == "install":
            exit_code = runner.install_dependencies()
        elif args.command == "all":
            exit_code = runner.run_all_tests(
                coverage=args.coverage,
                parallel=args.parallel
            )
        elif args.command == "frontend":
            exit_code = runner.run_frontend_tests(
                coverage=args.coverage,
                watch=args.watch
            )
        elif args.command == "report":
            exit_code = runner.generate_reports()
        elif args.command == "clean":
            exit_code = runner.clean_artifacts()
        else:
            exit_code = runner.run_backend_tests(
                test_type=args.command,
                coverage=args.coverage,
                parallel=args.parallel
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