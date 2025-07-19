#!/usr/bin/env python3
"""
Coverage badge generator for the Multi-Agent Research System.

This script generates coverage badges for the README by:
1. Running coverage analysis
2. Extracting coverage percentage
3. Generating SVG badge
4. Updating README with badge
"""

import subprocess
import sys
import os
import re
from pathlib import Path
from typing import Tuple, Optional


class CoverageBadgeGenerator:
    """Generate coverage badges for the project."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.badges_dir = self.project_root / "imgs" / "badges"
        self.badges_dir.mkdir(parents=True, exist_ok=True)
        
    def run_coverage_analysis(self) -> Optional[float]:
        """Run coverage analysis and return coverage percentage."""
        try:
            # Run pytest with coverage
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=xml",
                "-q"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Coverage analysis failed: {result.stderr}")
                return None
            
            # Extract coverage percentage from output
            coverage_match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', result.stdout)
            if coverage_match:
                return float(coverage_match.group(1))
            
            return None
            
        except Exception as e:
            print(f"Error running coverage analysis: {e}")
            return None
    
    def get_badge_color(self, coverage: float) -> str:
        """Get badge color based on coverage percentage."""
        if coverage >= 90:
            return "brightgreen"
        elif coverage >= 80:
            return "green"
        elif coverage >= 70:
            return "yellowgreen"
        elif coverage >= 60:
            return "yellow"
        elif coverage >= 50:
            return "orange"
        else:
            return "red"
    
    def generate_svg_badge(self, coverage: float, color: str) -> str:
        """Generate SVG badge content."""
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="120" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <mask id="a">
    <rect width="120" height="20" rx="3" fill="#fff"/>
  </mask>
  <g mask="url(#a)">
    <path fill="#555" d="M0 0h67v20H0z"/>
    <path fill="{color}" d="M67 0h53v20H67z"/>
    <path fill="url(#b)" d="M0 0h120v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="33.5" y="15" fill="#010101" fill-opacity=".3">coverage</text>
    <text x="33.5" y="14">coverage</text>
    <text x="93.5" y="15" fill="#010101" fill-opacity=".3">{coverage:.1f}%</text>
    <text x="93.5" y="14">{coverage:.1f}%</text>
  </g>
</svg>'''
    
    def save_badge(self, svg_content: str, filename: str = "coverage.svg"):
        """Save SVG badge to file."""
        badge_path = self.badges_dir / filename
        badge_path.write_text(svg_content)
        print(f"Badge saved to: {badge_path}")
    
    def update_readme_badge(self, coverage: float) -> bool:
        """Update README with coverage badge."""
        readme_path = self.project_root / "README.md"
        if not readme_path.exists():
            print("README.md not found")
            return False
        
        readme_content = readme_path.read_text()
        
        # Badge URL pattern
        badge_url = f"![Coverage](imgs/badges/coverage.svg)"
        
        # Check if badge already exists
        if "![Coverage]" in readme_content:
            # Replace existing badge
            readme_content = re.sub(
                r'!\[Coverage\]\([^)]+\)',
                badge_url,
                readme_content
            )
        else:
            # Add badge after the title
            title_match = re.search(r'^# (.+)$', readme_content, re.MULTILINE)
            if title_match:
                insert_pos = readme_content.find('\n', readme_content.find(title_match.group(0))) + 1
                readme_content = (
                    readme_content[:insert_pos] +
                    f"\n{badge_url}\n\n" +
                    readme_content[insert_pos:]
                )
        
        readme_path.write_text(readme_content)
        print(f"README updated with coverage badge: {coverage:.1f}%")
        return True
    
    def generate_badge(self) -> bool:
        """Generate coverage badge and update README."""
        print("Running coverage analysis...")
        coverage = self.run_coverage_analysis()
        
        if coverage is None:
            print("Failed to get coverage percentage")
            return False
        
        print(f"Coverage: {coverage:.1f}%")
        
        # Generate badge
        color = self.get_badge_color(coverage)
        svg_content = self.generate_svg_badge(coverage, color)
        
        # Save badge
        self.save_badge(svg_content)
        
        # Update README
        self.update_readme_badge(coverage)
        
        return True


def main():
    """Main entry point."""
    generator = CoverageBadgeGenerator()
    
    if generator.generate_badge():
        print("✅ Coverage badge generated successfully")
        sys.exit(0)
    else:
        print("❌ Failed to generate coverage badge")
        sys.exit(1)


if __name__ == "__main__":
    main() 