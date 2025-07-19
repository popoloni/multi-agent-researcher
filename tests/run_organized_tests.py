#!/usr/bin/env python3
"""
Organized test runner for the Multi-Agent Research System.

This script runs tests based on the new organized structure:
- Unit tests: Individual service/function tests
- Integration tests: Service interaction tests  
- API tests: FastAPI endpoint tests
- Agent tests: Agent-specific tests
- E2E tests: End-to-end workflow tests
- Frontend tests: React component tests

Usage:
    python tests/run_organized_tests.py [category] [options]

Categories:
    unit           Run unit tests only
    integration    Run integration tests only
    api            Run API tests only
    agents         Run agent tests only
    e2e            Run E2E tests only
    frontend       Run frontend tests only
    backend        Run all backend tests (unit + integration + api + agents + e2e)
    all            Run all tests (backend + frontend)
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class OrganizedTestRunner:
    """Test runner for the organized test structure."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
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
    
    def run_backend_tests(self, category: str, coverage: bool = False, 
                         parallel: bool = False, html_report: bool = False) -> int:
        """Run backend tests for a specific category."""
        print(f"Running {category} tests...")
        
        # Build pytest command
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test path based on category
        if category == "unit":
            cmd.append("tests/unit/")
        elif category == "integration":
            cmd.append("tests/integration/")
        elif category == "api":
            cmd.append("tests/api/")
        elif category == "agents":
            cmd.append("tests/agents/")
        elif category == "e2e":
            cmd.append("tests/e2e/")
        elif category == "backend":
            cmd.append("tests/unit/ tests/integration/ tests/api/ tests/agents/ tests/e2e/")
        else:
            print(f"Unknown category: {category}")
            return 1
        
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
        """Run frontend tests."""
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
            "backend", 
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
    
    def list_test_files(self, category: str) -> None:
        """List test files in a category."""
        if category == "unit":
            test_dir = self.tests_dir / "unit"
        elif category == "integration":
            test_dir = self.tests_dir / "integration"
        elif category == "api":
            test_dir = self.tests_dir / "api"
        elif category == "agents":
            test_dir = self.tests_dir / "agents"
        elif category == "e2e":
            test_dir = self.tests_dir / "e2e"
        elif category == "frontend":
            test_dir = self.tests_dir / "frontend"
        else:
            print(f"Unknown category: {category}")
            return
        
        if not test_dir.exists():
            print(f"❌ Test directory not found: {test_dir}")
            return
        
        print(f"\n📁 Test files in {category}:")
        for test_file in test_dir.rglob("*.py"):
            if test_file.name != "__init__.py":
                print(f"  - {test_file.relative_to(self.tests_dir)}")
        
        # List frontend test files
        if category == "frontend":
            for test_file in test_dir.rglob("*.test.js*"):
                print(f"  - {test_file.relative_to(self.tests_dir)}")
    
    def show_test_stats(self) -> None:
        """Show statistics about the test organization."""
        print("\n📊 Test Organization Statistics:")
        
        categories = ["unit", "integration", "api", "agents", "e2e", "frontend"]
        total_files = 0
        
        for category in categories:
            if category == "frontend":
                test_dir = self.tests_dir / "frontend"
                files = list(test_dir.rglob("*.test.js*"))
            else:
                test_dir = self.tests_dir / category
                files = list(test_dir.rglob("*.py"))
                files = [f for f in files if f.name != "__init__.py"]
            
            count = len(files)
            total_files += count
            print(f"  {category.capitalize()}: {count} files")
        
        print(f"\nTotal test files: {total_files}")
        
        # Show directory structure
        print("\n📁 Test Directory Structure:")
        self._print_directory_tree(self.tests_dir, max_depth=3)
    
    def _print_directory_tree(self, path: Path, max_depth: int = 3, current_depth: int = 0):
        """Print directory tree structure."""
        if current_depth > max_depth:
            return
        
        indent = "  " * current_depth
        if path.is_dir():
            print(f"{indent}📁 {path.name}/")
            for item in sorted(path.iterdir()):
                if item.name not in ["__pycache__", ".pytest_cache"]:
                    self._print_directory_tree(item, max_depth, current_depth + 1)
        else:
            if path.suffix in [".py", ".js", ".jsx"]:
                print(f"{indent}📄 {path.name}")


def main():
    """Main entry point for the organized test runner."""
    parser = argparse.ArgumentParser(
        description="Organized test runner for Multi-Agent Research System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "category",
        nargs="?",
        default="all",
        choices=[
            "unit", "integration", "api", "agents", "e2e", 
            "frontend", "backend", "all"
        ],
        help="Test category to run"
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
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List test files in category"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show test organization statistics"
    )
    
    args = parser.parse_args()
    
    runner = OrganizedTestRunner()
    
    try:
        if args.stats:
            runner.show_test_stats()
            return
        
        if args.list:
            runner.list_test_files(args.category)
            return
        
        if args.category == "all":
            exit_code = runner.run_all_tests(
                coverage=args.coverage,
                parallel=args.parallel
            )
        elif args.category == "frontend":
            exit_code = runner.run_frontend_tests(
                coverage=args.coverage,
                watch=args.watch
            )
        elif args.category == "backend":
            exit_code = runner.run_backend_tests(
                "backend",
                coverage=args.coverage,
                parallel=args.parallel
            )
        else:
            exit_code = runner.run_backend_tests(
                args.category,
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