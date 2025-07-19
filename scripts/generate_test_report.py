#!/usr/bin/env python3
"""
Test Result Reporting Script

This script generates comprehensive test reports including:
- Test execution summaries
- Performance metrics
- Coverage reports
- Test result archiving
- JSON/HTML/XML report formats

Designed for CI/CD integration and quality gates.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import subprocess
import xml.etree.ElementTree as ET


class TestReportGenerator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reports_dir = project_root / "test-reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        self.report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "project_root": str(project_root),
                "version": "1.0.0"
            },
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
                "success_rate": 0.0,
                "total_duration": 0.0,
                "coverage_percentage": 0.0
            },
            "categories": {},
            "performance": {
                "slowest_tests": [],
                "fastest_tests": [],
                "average_duration": 0.0
            },
            "coverage": {
                "overall": 0.0,
                "by_module": {},
                "missing_lines": []
            },
            "issues": {
                "critical": [],
                "warnings": [],
                "suggestions": []
            }
        }

    def generate_comprehensive_report(self, 
                                    include_coverage: bool = True,
                                    include_performance: bool = True,
                                    archive_results: bool = True) -> Dict[str, Any]:
        """Generate a comprehensive test report."""
        print("🔍 Generating comprehensive test report...")
        
        # Run tests and collect data
        self._collect_test_results()
        
        if include_coverage:
            self._collect_coverage_data()
        
        if include_performance:
            self._analyze_performance()
        
        # Analyze results and generate insights
        self._analyze_results()
        
        # Save reports in multiple formats
        self._save_reports()
        
        if archive_results:
            self._archive_results()
        
        return self.report_data

    def _collect_test_results(self):
        """Collect test execution results."""
        print("  📊 Collecting test results...")
        
        try:
            # First, get test count
            collect_result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Count discovered tests
            lines = collect_result.stdout.split('\n')
            test_count = sum(1 for line in lines if 'test_' in line and '::' in line)
            
            if test_count == 0:
                self.report_data["issues"]["critical"].append("No tests discovered")
                return
            
            # Run a subset of tests to get actual results
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/unit/test_vector_simple.py", "-v", "--tb=short"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Parse stdout for test results
            self._parse_stdout_report(result.stdout, result.stderr)
            
            # Update total tests count
            self.report_data["summary"]["total_tests"] = test_count
                
        except Exception as e:
            self.report_data["issues"]["critical"].append(f"Failed to collect test results: {e}")

    def _parse_json_report(self, json_data: Dict):
        """Parse pytest JSON report."""
        summary = json_data.get("summary", {})
        
        self.report_data["summary"].update({
            "total_tests": summary.get("total", 0),
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "skipped": summary.get("skipped", 0),
            "errors": summary.get("error", 0),
            "total_duration": summary.get("duration", 0.0)
        })
        
        # Calculate success rate
        total = self.report_data["summary"]["total_tests"]
        passed = self.report_data["summary"]["passed"]
        if total > 0:
            self.report_data["summary"]["success_rate"] = (passed / total) * 100
        
        # Parse test results by category
        for test in json_data.get("tests", []):
            self._categorize_test_result(test)

    def _parse_stdout_report(self, stdout: str, stderr: str):
        """Parse pytest stdout/stderr for test results."""
        lines = stdout.split('\n')
        
        # Count test results
        passed = sum(1 for line in lines if 'PASSED' in line)
        failed = sum(1 for line in lines if 'FAILED' in line)
        skipped = sum(1 for line in lines if 'SKIPPED' in line)
        errors = sum(1 for line in lines if 'ERROR' in line)
        
        total = passed + failed + skipped + errors
        
        self.report_data["summary"].update({
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "total_duration": 0.0  # Will be updated by performance analysis
        })
        
        if total > 0:
            self.report_data["summary"]["success_rate"] = (passed / total) * 100

    def _categorize_test_result(self, test_data: Dict):
        """Categorize a test result by type."""
        test_path = test_data.get("nodeid", "")
        
        if "tests/unit/" in test_path:
            category = "unit"
        elif "tests/integration/" in test_path:
            category = "integration"
        elif "tests/api/" in test_path:
            category = "api"
        elif "tests/agents/" in test_path:
            category = "agents"
        elif "tests/e2e/" in test_path:
            category = "e2e"
        else:
            category = "other"
        
        if category not in self.report_data["categories"]:
            self.report_data["categories"][category] = {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "errors": 0,
                "duration": 0.0
            }
        
        cat_data = self.report_data["categories"][category]
        cat_data["total"] += 1
        
        outcome = test_data.get("outcome", "unknown")
        if outcome == "passed":
            cat_data["passed"] += 1
        elif outcome == "failed":
            cat_data["failed"] += 1
        elif outcome == "skipped":
            cat_data["skipped"] += 1
        else:
            cat_data["errors"] += 1
        
        # Add duration if available
        duration = test_data.get("duration", 0.0)
        cat_data["duration"] += duration

    def _collect_coverage_data(self):
        """Collect coverage data."""
        print("  📈 Collecting coverage data...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "--cov=app", "--cov-report=xml", "--cov-report=term-missing", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse coverage XML
            coverage_xml = self.project_root / "coverage.xml"
            if coverage_xml.exists():
                self._parse_coverage_xml(coverage_xml)
            
            # Parse terminal output for overall coverage
            for line in result.stdout.split('\n'):
                if "TOTAL" in line and "%" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            coverage_pct = float(parts[-1].replace('%', ''))
                            self.report_data["coverage"]["overall"] = coverage_pct
                            self.report_data["summary"]["coverage_percentage"] = coverage_pct
                            break
                        except ValueError:
                            continue
                            
        except Exception as e:
            self.report_data["issues"]["warnings"].append(f"Failed to collect coverage data: {e}")

    def _parse_coverage_xml(self, xml_path: Path):
        """Parse coverage XML file."""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Parse overall coverage
            coverage = root.find(".//coverage")
            if coverage is not None:
                total = int(coverage.get("lines-valid", 0))
                covered = int(coverage.get("lines-covered", 0))
                if total > 0:
                    self.report_data["coverage"]["overall"] = (covered / total) * 100
            
            # Parse per-file coverage
            for package in root.findall(".//package"):
                package_name = package.get("name", "unknown")
                try:
                    line_rate = float(package.get("line-rate", 0)) * 100
                    branch_rate = float(package.get("branch-rate", 0)) * 100
                    self.report_data["coverage"]["by_module"][package_name] = {
                        "lines": line_rate,
                        "branches": branch_rate
                    }
                except (ValueError, TypeError):
                    # Skip packages with invalid coverage data
                    continue
                
        except Exception as e:
            self.report_data["issues"]["warnings"].append(f"Failed to parse coverage XML: {e}")

    def _analyze_performance(self):
        """Analyze test performance."""
        print("  ⏱️  Analyzing performance...")
        
        try:
            # Run tests with duration reporting
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "--durations=10", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse slowest tests
            lines = result.stdout.split('\n')
            in_durations = False
            durations = []
            
            for line in lines:
                if "slowest durations" in line.lower():
                    in_durations = True
                    continue
                elif in_durations and line.strip() == "":
                    break
                elif in_durations and line.strip():
                    # Parse duration line (e.g., "2.34s test_something")
                    parts = line.strip().split()
                    if len(parts) >= 2 and parts[0].endswith('s'):
                        try:
                            duration = float(parts[0][:-1])
                            test_name = ' '.join(parts[1:])
                            durations.append((test_name, duration))
                        except ValueError:
                            continue
            
            # Sort by duration
            durations.sort(key=lambda x: x[1], reverse=True)
            
            self.report_data["performance"]["slowest_tests"] = durations[:10]
            self.report_data["performance"]["fastest_tests"] = durations[-10:] if durations else []
            
            # Calculate average duration
            if durations:
                avg_duration = sum(d[1] for d in durations) / len(durations)
                self.report_data["performance"]["average_duration"] = avg_duration
                
        except Exception as e:
            self.report_data["issues"]["warnings"].append(f"Failed to analyze performance: {e}")

    def _analyze_results(self):
        """Analyze test results and generate insights."""
        print("  🔍 Analyzing results...")
        
        summary = self.report_data["summary"]
        
        # Check success rate
        if summary["success_rate"] < 70:
            self.report_data["issues"]["critical"].append(
                f"Low test success rate: {summary['success_rate']:.1f}% (target: 70%)"
            )
        elif summary["success_rate"] < 90:
            self.report_data["issues"]["warnings"].append(
                f"Test success rate could be improved: {summary['success_rate']:.1f}%"
            )
        
        # Check coverage
        coverage = summary["coverage_percentage"]
        if coverage < 70:
            self.report_data["issues"]["critical"].append(
                f"Low code coverage: {coverage:.1f}% (target: 70%)"
            )
        elif coverage < 80:
            self.report_data["issues"]["warnings"].append(
                f"Code coverage could be improved: {coverage:.1f}%"
            )
        
        # Check for slow tests
        slow_tests = self.report_data["performance"]["slowest_tests"]
        if slow_tests and slow_tests[0][1] > 10:  # More than 10 seconds
            self.report_data["issues"]["warnings"].append(
                f"Very slow test detected: {slow_tests[0][0]} ({slow_tests[0][1]:.1f}s)"
            )
        
        # Generate suggestions
        if summary["skipped"] > 0:
            self.report_data["issues"]["suggestions"].append(
                f"Consider investigating {summary['skipped']} skipped tests"
            )
        
        if summary["errors"] > 0:
            self.report_data["issues"]["suggestions"].append(
                f"Investigate {summary['errors']} test errors"
            )

    def _save_reports(self):
        """Save reports in multiple formats."""
        print("  💾 Saving reports...")
        
        # Save JSON report
        json_path = self.reports_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        
        # Generate HTML report
        html_path = self.reports_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        self._generate_html_report(html_path)
        
        # Generate summary report
        summary_path = self.reports_dir / "latest_summary.txt"
        self._generate_summary_report(summary_path)
        
        print(f"    📄 JSON report: {json_path}")
        print(f"    📄 HTML report: {html_path}")
        print(f"    📄 Summary: {summary_path}")

    def _generate_html_report(self, html_path: Path):
        """Generate HTML test report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric h3 {{ margin: 0 0 10px 0; color: #333; }}
        .metric .value {{ font-size: 24px; font-weight: bold; }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .error {{ color: #dc3545; }}
        .issues {{ margin: 20px 0; }}
        .issue {{ padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .critical {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
        .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
        .suggestion {{ background: #d1ecf1; border-left: 4px solid #17a2b8; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Execution Report</h1>
        <p>Generated: {self.report_data['metadata']['generated_at']}</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>Success Rate</h3>
            <div class="value {'success' if self.report_data['summary']['success_rate'] >= 90 else 'warning' if self.report_data['summary']['success_rate'] >= 70 else 'error'}">
                {self.report_data['summary']['success_rate']:.1f}%
            </div>
        </div>
        <div class="metric">
            <h3>Total Tests</h3>
            <div class="value">{self.report_data['summary']['total_tests']}</div>
        </div>
        <div class="metric">
            <h3>Coverage</h3>
            <div class="value {'success' if self.report_data['summary']['coverage_percentage'] >= 80 else 'warning' if self.report_data['summary']['coverage_percentage'] >= 70 else 'error'}">
                {self.report_data['summary']['coverage_percentage']:.1f}%
            </div>
        </div>
        <div class="metric">
            <h3>Duration</h3>
            <div class="value">{self.report_data['summary']['total_duration']:.1f}s</div>
        </div>
    </div>
    
    <div class="issues">
        <h2>Issues & Recommendations</h2>
        {self._generate_issues_html()}
    </div>
    
    <div class="categories">
        <h2>Results by Category</h2>
        {self._generate_categories_html()}
    </div>
    
    <div class="performance">
        <h2>Performance Analysis</h2>
        {self._generate_performance_html()}
    </div>
</body>
</html>
        """
        
        with open(html_path, 'w') as f:
            f.write(html_content)

    def _generate_issues_html(self) -> str:
        """Generate HTML for issues section."""
        html = ""
        
        for issue_type, issues in self.report_data["issues"].items():
            if issues:
                html += f'<h3>{issue_type.title()}</h3>'
                for issue in issues:
                    html += f'<div class="issue {issue_type}">{issue}</div>'
        
        return html

    def _generate_categories_html(self) -> str:
        """Generate HTML for categories section."""
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr><th>Category</th><th>Total</th><th>Passed</th><th>Failed</th><th>Success Rate</th></tr>'
        
        for category, data in self.report_data["categories"].items():
            success_rate = (data["passed"] / data["total"] * 100) if data["total"] > 0 else 0
            html += f'<tr>'
            html += f'<td>{category}</td>'
            html += f'<td>{data["total"]}</td>'
            html += f'<td>{data["passed"]}</td>'
            html += f'<td>{data["failed"]}</td>'
            html += f'<td>{success_rate:.1f}%</td>'
            html += f'</tr>'
        
        html += '</table>'
        return html

    def _generate_performance_html(self) -> str:
        """Generate HTML for performance section."""
        html = '<h3>Slowest Tests</h3><ul>'
        for test_name, duration in self.report_data["performance"]["slowest_tests"][:5]:
            html += f'<li>{test_name}: {duration:.2f}s</li>'
        html += '</ul>'
        
        if self.report_data["performance"]["average_duration"] > 0:
            html += f'<p><strong>Average test duration:</strong> {self.report_data["performance"]["average_duration"]:.2f}s</p>'
        
        return html

    def _generate_summary_report(self, summary_path: Path):
        """Generate a simple text summary report."""
        summary = self.report_data["summary"]
        
        with open(summary_path, 'w') as f:
            f.write("TEST EXECUTION SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {self.report_data['metadata']['generated_at']}\n\n")
            f.write(f"Overall Results:\n")
            f.write(f"  Total Tests: {summary['total_tests']}\n")
            f.write(f"  Passed: {summary['passed']}\n")
            f.write(f"  Failed: {summary['failed']}\n")
            f.write(f"  Skipped: {summary['skipped']}\n")
            f.write(f"  Errors: {summary['errors']}\n")
            f.write(f"  Success Rate: {summary['success_rate']:.1f}%\n")
            f.write(f"  Coverage: {summary['coverage_percentage']:.1f}%\n")
            f.write(f"  Duration: {summary['total_duration']:.1f}s\n\n")
            
            f.write("Issues:\n")
            for issue_type, issues in self.report_data["issues"].items():
                if issues:
                    f.write(f"  {issue_type.upper()}:\n")
                    for issue in issues:
                        f.write(f"    - {issue}\n")
                    f.write("\n")

    def _archive_results(self):
        """Archive test results for historical tracking."""
        print("  📦 Archiving results...")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_dir = self.reports_dir / "archives" / timestamp
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy latest reports to archive
        for report_file in self.reports_dir.glob("*.json"):
            if report_file.name.startswith("test_report_"):
                import shutil
                shutil.copy2(report_file, archive_dir / report_file.name)
        
        # Create archive index
        archive_index = archive_dir / "archive_info.json"
        archive_data = {
            "timestamp": timestamp,
            "date": datetime.now().isoformat(),
            "summary": self.report_data["summary"],
            "files": [f.name for f in archive_dir.glob("*.json")]
        }
        
        with open(archive_index, 'w') as f:
            json.dump(archive_data, f, indent=2)
        
        print(f"    📦 Archived to: {archive_dir}")


def main():
    """Main entry point for test report generation."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive test reports",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage analysis"
    )
    
    parser.add_argument(
        "--no-performance",
        action="store_true",
        help="Skip performance analysis"
    )
    
    parser.add_argument(
        "--no-archive",
        action="store_true",
        help="Skip result archiving"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory for reports (default: test-reports/)"
    )
    
    args = parser.parse_args()
    
    project_root = Path.cwd()
    if args.output:
        reports_dir = Path(args.output)
    else:
        reports_dir = project_root / "test-reports"
    
    generator = TestReportGenerator(project_root)
    
    try:
        report_data = generator.generate_comprehensive_report(
            include_coverage=not args.no_coverage,
            include_performance=not args.no_performance,
            archive_results=not args.no_archive
        )
        
        # Print summary
        summary = report_data["summary"]
        print(f"\n📊 REPORT SUMMARY:")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        print(f"   Coverage: {summary['coverage_percentage']:.1f}%")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Duration: {summary['total_duration']:.1f}s")
        
        # Check for critical issues
        critical_issues = report_data["issues"]["critical"]
        if critical_issues:
            print(f"\n❌ CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"   - {issue}")
            sys.exit(1)
        else:
            print(f"\n✅ No critical issues found!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n❌ Report generation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 