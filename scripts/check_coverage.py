#!/usr/bin/env python3
"""
Coverage Threshold Checker

This script checks if test coverage meets minimum thresholds and provides
detailed reporting for CI/CD integration.
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CoverageChecker:
    def __init__(self, min_coverage: float = 70.0):
        self.min_coverage = min_coverage
        self.coverage_data = {}
        self.results = {
            "overall_coverage": 0.0,
            "threshold": min_coverage,
            "passed": False,
            "details": {},
            "warnings": [],
            "errors": []
        }

    def check_coverage_files(self) -> bool:
        """Check for coverage report files and load data."""
        coverage_files = [
            ".coverage",
            "htmlcov/index.html",
            "coverage.xml",
            "coverage.json"
        ]
        
        found_files = []
        for file_path in coverage_files:
            if os.path.exists(file_path):
                found_files.append(file_path)
        
        if not found_files:
            self.results["errors"].append("No coverage files found. Run tests with coverage first.")
            return False
        
        print(f"Found coverage files: {found_files}")
        return True

    def load_coverage_data(self) -> bool:
        """Load coverage data from available sources."""
        # Try to load from coverage.xml first (most reliable for CI)
        if os.path.exists("coverage.xml"):
            return self._load_xml_coverage()
        elif os.path.exists("coverage.json"):
            return self._load_json_coverage()
        elif os.path.exists(".coverage"):
            return self._load_dot_coverage()
        else:
            self.results["errors"].append("No readable coverage data found")
            return False

    def _load_xml_coverage(self) -> bool:
        """Load coverage data from coverage.xml."""
        try:
            tree = ET.parse("coverage.xml")
            root = tree.getroot()
            
            # Extract overall coverage percentage
            coverage_elem = root.find(".//coverage")
            if coverage_elem is not None:
                line_rate = coverage_elem.get("line-rate")
                if line_rate:
                    self.results["overall_coverage"] = float(line_rate) * 100
                    return True
            
            self.results["errors"].append("Could not parse coverage percentage from XML")
            return False
            
        except Exception as e:
            self.results["errors"].append(f"Error parsing coverage.xml: {e}")
            return False

    def _load_json_coverage(self) -> bool:
        """Load coverage data from coverage.json."""
        try:
            with open("coverage.json", "r") as f:
                data = json.load(f)
                
            if "totals" in data and "percent_covered" in data["totals"]:
                self.results["overall_coverage"] = data["totals"]["percent_covered"]
                return True
            else:
                self.results["errors"].append("Invalid coverage.json format")
                return False
                
        except Exception as e:
            self.results["errors"].append(f"Error parsing coverage.json: {e}")
            return False

    def _load_dot_coverage(self) -> bool:
        """Load coverage data from .coverage file using coverage.py."""
        try:
            import coverage
            cov = coverage.Coverage()
            cov.load()
            
            # Get total coverage
            total_coverage = cov.report()
            if total_coverage is not None:
                self.results["overall_coverage"] = total_coverage
                return True
            else:
                self.results["errors"].append("Could not calculate coverage from .coverage")
                return False
                
        except ImportError:
            self.results["errors"].append("coverage.py not available for .coverage parsing")
            return False
        except Exception as e:
            self.results["errors"].append(f"Error loading .coverage: {e}")
            return False

    def check_threshold(self) -> bool:
        """Check if coverage meets minimum threshold."""
        coverage = self.results["overall_coverage"]
        threshold = self.results["threshold"]
        
        self.results["passed"] = coverage >= threshold
        
        if not self.results["passed"]:
            self.results["errors"].append(
                f"Coverage {coverage:.1f}% is below threshold {threshold}%"
            )
        
        return self.results["passed"]

    def generate_report(self) -> str:
        """Generate a human-readable report."""
        coverage = self.results["overall_coverage"]
        threshold = self.results["threshold"]
        status = "✅ PASSED" if self.results["passed"] else "❌ FAILED"
        
        report = f"""
📊 COVERAGE REPORT
==================
Status: {status}
Coverage: {coverage:.1f}%
Threshold: {threshold}%
Difference: {coverage - threshold:+.1f}%

"""
        
        if self.results["warnings"]:
            report += "⚠️  WARNINGS:\n"
            for warning in self.results["warnings"]:
                report += f"  - {warning}\n"
            report += "\n"
        
        if self.results["errors"]:
            report += "❌ ERRORS:\n"
            for error in self.results["errors"]:
                report += f"  - {error}\n"
            report += "\n"
        
        return report

    def save_results(self, output_file: str = "coverage_results.json"):
        """Save results to JSON file for CI consumption."""
        try:
            with open(output_file, "w") as f:
                json.dump(self.results, f, indent=2)
            print(f"Results saved to {output_file}")
        except Exception as e:
            print(f"Warning: Could not save results to {output_file}: {e}")

    def run(self) -> bool:
        """Run the complete coverage check."""
        print("🔍 Checking coverage files...")
        if not self.check_coverage_files():
            return False
        
        print("📊 Loading coverage data...")
        if not self.load_coverage_data():
            return False
        
        print("🎯 Checking threshold...")
        passed = self.check_threshold()
        
        # Generate and display report
        report = self.generate_report()
        print(report)
        
        # Save results for CI
        self.save_results()
        
        return passed


def main():
    parser = argparse.ArgumentParser(description="Check test coverage against threshold")
    parser.add_argument(
        "--min-coverage", 
        type=float, 
        default=70.0,
        help="Minimum coverage percentage (default: 70.0)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="coverage_results.json",
        help="Output file for results (default: coverage_results.json)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"🔍 Coverage Checker")
        print(f"📊 Minimum coverage: {args.min_coverage}%")
        print(f"📁 Output file: {args.output}")
        print()
    
    checker = CoverageChecker(min_coverage=args.min_coverage)
    success = checker.run()
    
    # Exit with appropriate code for CI
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 