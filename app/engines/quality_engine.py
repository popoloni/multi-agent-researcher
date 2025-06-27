"""
Code Quality Engine for comprehensive code analysis and quality metrics
Phase 3 implementation with advanced quality assessment and trend analysis
"""

import ast
import re
import math
import time
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from app.models.repository_schemas import CodeElement, Repository, ElementType, LanguageType


class QualityMetric(Enum):
    """Types of quality metrics"""
    CYCLOMATIC_COMPLEXITY = "cyclomatic_complexity"
    MAINTAINABILITY_INDEX = "maintainability_index"
    CODE_DUPLICATION = "code_duplication"
    TECHNICAL_DEBT = "technical_debt"
    SECURITY_SCORE = "security_score"
    PERFORMANCE_SCORE = "performance_score"
    READABILITY_SCORE = "readability_score"
    TEST_COVERAGE = "test_coverage"
    DOCUMENTATION_COVERAGE = "documentation_coverage"
    DEPENDENCY_HEALTH = "dependency_health"


class QualitySeverity(Enum):
    """Severity levels for quality issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class QualityIssue:
    """Individual quality issue"""
    metric: QualityMetric
    severity: QualitySeverity
    title: str
    description: str
    location: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    effort_estimate: Optional[str] = None  # Time to fix
    impact_score: float = 0.0  # 0-10 scale


@dataclass
class QualityScore:
    """Quality score for a specific metric"""
    metric: QualityMetric
    score: float  # 0-10 scale
    max_score: float = 10.0
    issues_count: int = 0
    trend: Optional[str] = None  # "improving", "declining", "stable"


@dataclass
class QualityReport:
    """Comprehensive quality report"""
    element_id: str
    repository_id: str
    overall_score: float
    scores: Dict[QualityMetric, QualityScore]
    issues: List[QualityIssue]
    recommendations: List[str]
    analysis_timestamp: datetime
    processing_time: float


@dataclass
class QualityTrend:
    """Quality trend over time"""
    metric: QualityMetric
    timestamps: List[datetime]
    scores: List[float]
    trend_direction: str  # "improving", "declining", "stable"
    trend_strength: float  # 0-1 scale
    prediction: Optional[float] = None  # Predicted next score


class QualityEngine:
    """Advanced code quality analysis engine"""
    
    def __init__(self):
        self.quality_history: Dict[str, List[QualityReport]] = {}
        self.quality_thresholds = self._initialize_thresholds()
        self.security_patterns = self._initialize_security_patterns()
        self.performance_patterns = self._initialize_performance_patterns()
    
    def _initialize_thresholds(self) -> Dict[QualityMetric, Dict[str, float]]:
        """Initialize quality thresholds for different severity levels"""
        
        return {
            QualityMetric.CYCLOMATIC_COMPLEXITY: {
                'excellent': 5,
                'good': 10,
                'moderate': 15,
                'poor': 25,
                'critical': 50
            },
            QualityMetric.MAINTAINABILITY_INDEX: {
                'excellent': 85,
                'good': 70,
                'moderate': 50,
                'poor': 25,
                'critical': 10
            },
            QualityMetric.CODE_DUPLICATION: {
                'excellent': 3,
                'good': 5,
                'moderate': 10,
                'poor': 20,
                'critical': 30
            },
            QualityMetric.READABILITY_SCORE: {
                'excellent': 8.5,
                'good': 7.0,
                'moderate': 5.5,
                'poor': 4.0,
                'critical': 2.0
            }
        }
    
    def _initialize_security_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize security vulnerability patterns"""
        
        return {
            'sql_injection': {
                'patterns': [
                    r'execute\s*\(\s*["\'].*%.*["\']',
                    r'query\s*\(\s*["\'].*\+.*["\']',
                    r'SELECT.*\+.*FROM',
                    r'INSERT.*\+.*VALUES'
                ],
                'severity': QualitySeverity.HIGH,
                'description': 'Potential SQL injection vulnerability'
            },
            'xss_vulnerability': {
                'patterns': [
                    r'innerHTML\s*=.*\+',
                    r'document\.write\s*\(',
                    r'eval\s*\(',
                    r'dangerouslySetInnerHTML'
                ],
                'severity': QualitySeverity.HIGH,
                'description': 'Potential XSS vulnerability'
            },
            'hardcoded_secrets': {
                'patterns': [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'api_key\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                    r'token\s*=\s*["\'][^"\']+["\']'
                ],
                'severity': QualitySeverity.CRITICAL,
                'description': 'Hardcoded secrets detected'
            },
            'weak_crypto': {
                'patterns': [
                    r'md5\s*\(',
                    r'sha1\s*\(',
                    r'DES\s*\(',
                    r'RC4\s*\('
                ],
                'severity': QualitySeverity.MEDIUM,
                'description': 'Weak cryptographic algorithm'
            }
        }
    
    def _initialize_performance_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize performance anti-patterns"""
        
        return {
            'nested_loops': {
                'patterns': [
                    r'for.*for.*for',  # Triple nested loops
                    r'while.*while.*while'
                ],
                'severity': QualitySeverity.MEDIUM,
                'description': 'Deeply nested loops may cause performance issues'
            },
            'inefficient_string_concat': {
                'patterns': [
                    r'\+\s*=.*["\']',  # String concatenation in loops
                    r'str\s*\+\s*str'
                ],
                'severity': QualitySeverity.LOW,
                'description': 'Inefficient string concatenation'
            },
            'database_in_loop': {
                'patterns': [
                    r'for.*execute\s*\(',
                    r'while.*query\s*\(',
                    r'for.*save\s*\('
                ],
                'severity': QualitySeverity.HIGH,
                'description': 'Database operations in loops'
            },
            'memory_leak_potential': {
                'patterns': [
                    r'global\s+\w+\s*=\s*\[\]',
                    r'cache\s*=\s*\{\}',
                    r'setInterval\s*\(',
                    r'addEventListener.*without.*removeEventListener'
                ],
                'severity': QualitySeverity.MEDIUM,
                'description': 'Potential memory leak'
            }
        }
    
    async def analyze_quality(self, element: CodeElement, repository: Repository) -> QualityReport:
        """Perform comprehensive quality analysis on code element"""
        
        start_time = time.time()
        
        # Initialize scores and issues
        scores = {}
        issues = []
        
        # Analyze different quality metrics
        if element.code_snippet:
            # Cyclomatic complexity
            complexity_score, complexity_issues = self._analyze_cyclomatic_complexity(element)
            scores[QualityMetric.CYCLOMATIC_COMPLEXITY] = complexity_score
            issues.extend(complexity_issues)
            
            # Maintainability index
            maintainability_score, maintainability_issues = self._analyze_maintainability(element)
            scores[QualityMetric.MAINTAINABILITY_INDEX] = maintainability_score
            issues.extend(maintainability_issues)
            
            # Security analysis
            security_score, security_issues = self._analyze_security(element)
            scores[QualityMetric.SECURITY_SCORE] = security_score
            issues.extend(security_issues)
            
            # Performance analysis
            performance_score, performance_issues = self._analyze_performance(element)
            scores[QualityMetric.PERFORMANCE_SCORE] = performance_score
            issues.extend(performance_issues)
            
            # Readability analysis
            readability_score, readability_issues = self._analyze_readability(element)
            scores[QualityMetric.READABILITY_SCORE] = readability_score
            issues.extend(readability_issues)
            
            # Documentation coverage
            doc_score, doc_issues = self._analyze_documentation(element)
            scores[QualityMetric.DOCUMENTATION_COVERAGE] = doc_score
            issues.extend(doc_issues)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(scores)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(scores, issues)
        
        # Create quality report
        report = QualityReport(
            element_id=element.id,
            repository_id=element.repository_id,
            overall_score=overall_score,
            scores=scores,
            issues=issues,
            recommendations=recommendations,
            analysis_timestamp=datetime.now(),
            processing_time=time.time() - start_time
        )
        
        # Store in history for trend analysis
        if element.id not in self.quality_history:
            self.quality_history[element.id] = []
        self.quality_history[element.id].append(report)
        
        return report
    
    def _analyze_cyclomatic_complexity(self, element: CodeElement) -> Tuple[QualityScore, List[QualityIssue]]:
        """Analyze cyclomatic complexity"""
        
        issues = []
        complexity = 1  # Base complexity
        
        if not element.code_snippet:
            return QualityScore(QualityMetric.CYCLOMATIC_COMPLEXITY, 10.0), issues
        
        try:
            # Count decision points
            decision_patterns = [
                r'\bif\b', r'\belif\b', r'\belse\b',
                r'\bfor\b', r'\bwhile\b',
                r'\btry\b', r'\bexcept\b', r'\bfinally\b',
                r'\band\b', r'\bor\b',
                r'\?.*:', r'case\s+.*:',
                r'catch\s*\(', r'switch\s*\('
            ]
            
            for pattern in decision_patterns:
                matches = re.findall(pattern, element.code_snippet, re.IGNORECASE)
                complexity += len(matches)
            
            # Calculate score (inverse relationship with complexity)
            thresholds = self.quality_thresholds[QualityMetric.CYCLOMATIC_COMPLEXITY]
            
            if complexity <= thresholds['excellent']:
                score = 10.0
            elif complexity <= thresholds['good']:
                score = 8.0
            elif complexity <= thresholds['moderate']:
                score = 6.0
            elif complexity <= thresholds['poor']:
                score = 4.0
            else:
                score = 2.0
            
            # Create issues for high complexity
            if complexity > thresholds['moderate']:
                severity = QualitySeverity.HIGH if complexity > thresholds['poor'] else QualitySeverity.MEDIUM
                
                issues.append(QualityIssue(
                    metric=QualityMetric.CYCLOMATIC_COMPLEXITY,
                    severity=severity,
                    title=f"High cyclomatic complexity ({complexity})",
                    description=f"This {element.element_type.value} has a cyclomatic complexity of {complexity}, which exceeds recommended thresholds.",
                    location=f"{element.file_path}:{element.name}",
                    suggestion="Consider breaking this into smaller, more focused functions/methods",
                    effort_estimate="2-4 hours" if complexity < 25 else "1-2 days",
                    impact_score=min(complexity / 10, 10.0)
                ))
            
            return QualityScore(
                metric=QualityMetric.CYCLOMATIC_COMPLEXITY,
                score=score,
                issues_count=len(issues)
            ), issues
            
        except Exception as e:
            print(f"Complexity analysis failed: {e}")
            return QualityScore(QualityMetric.CYCLOMATIC_COMPLEXITY, 5.0), issues
    
    def _analyze_maintainability(self, element: CodeElement) -> Tuple[QualityScore, List[QualityIssue]]:
        """Analyze maintainability index"""
        
        issues = []
        
        if not element.code_snippet:
            return QualityScore(QualityMetric.MAINTAINABILITY_INDEX, 10.0), issues
        
        try:
            lines = element.code_snippet.split('\n')
            total_lines = len(lines)
            code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            # Calculate various factors
            avg_line_length = sum(len(line) for line in lines) / max(total_lines, 1)
            comment_ratio = (total_lines - code_lines) / max(total_lines, 1)
            
            # Get complexity from previous analysis or estimate
            complexity = element.complexity_score or self._estimate_complexity(element.code_snippet)
            
            # Calculate maintainability index (simplified version)
            # Based on Halstead metrics and cyclomatic complexity
            volume = code_lines * math.log2(max(avg_line_length, 1))
            maintainability_index = max(0, 171 - 5.2 * math.log(volume) - 0.23 * complexity - 16.2 * math.log(code_lines))
            
            # Normalize to 0-10 scale
            score = min(maintainability_index / 10, 10.0)
            
            # Create issues for low maintainability
            thresholds = self.quality_thresholds[QualityMetric.MAINTAINABILITY_INDEX]
            
            if maintainability_index < thresholds['moderate']:
                severity = QualitySeverity.HIGH if maintainability_index < thresholds['poor'] else QualitySeverity.MEDIUM
                
                issues.append(QualityIssue(
                    metric=QualityMetric.MAINTAINABILITY_INDEX,
                    severity=severity,
                    title=f"Low maintainability index ({maintainability_index:.1f})",
                    description="This code has low maintainability due to complexity, size, or lack of documentation.",
                    location=f"{element.file_path}:{element.name}",
                    suggestion="Refactor to reduce complexity, add comments, and break into smaller units",
                    effort_estimate="4-8 hours",
                    impact_score=8.0 - score
                ))
            
            return QualityScore(
                metric=QualityMetric.MAINTAINABILITY_INDEX,
                score=score,
                issues_count=len(issues)
            ), issues
            
        except Exception as e:
            print(f"Maintainability analysis failed: {e}")
            return QualityScore(QualityMetric.MAINTAINABILITY_INDEX, 5.0), issues
    
    def _analyze_security(self, element: CodeElement) -> Tuple[QualityScore, List[QualityIssue]]:
        """Analyze security vulnerabilities"""
        
        issues = []
        vulnerability_count = 0
        total_severity_score = 0
        
        if not element.code_snippet:
            return QualityScore(QualityMetric.SECURITY_SCORE, 10.0), issues
        
        # Check for security patterns
        for vuln_type, config in self.security_patterns.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, element.code_snippet, re.IGNORECASE)
                
                for match in matches:
                    vulnerability_count += 1
                    
                    # Calculate severity score
                    severity_scores = {
                        QualitySeverity.CRITICAL: 10,
                        QualitySeverity.HIGH: 7,
                        QualitySeverity.MEDIUM: 4,
                        QualitySeverity.LOW: 2
                    }
                    total_severity_score += severity_scores[config['severity']]
                    
                    # Find line number
                    line_number = element.code_snippet[:match.start()].count('\n') + 1
                    
                    issues.append(QualityIssue(
                        metric=QualityMetric.SECURITY_SCORE,
                        severity=config['severity'],
                        title=f"Security vulnerability: {vuln_type.replace('_', ' ').title()}",
                        description=config['description'],
                        location=f"{element.file_path}:{element.name}",
                        line_number=line_number,
                        suggestion=self._get_security_suggestion(vuln_type),
                        effort_estimate=self._get_security_effort(config['severity']),
                        impact_score=severity_scores[config['severity']]
                    ))
        
        # Calculate security score
        if vulnerability_count == 0:
            score = 10.0
        else:
            # Penalize based on number and severity of vulnerabilities
            penalty = min(total_severity_score / 2, 9.0)
            score = max(10.0 - penalty, 1.0)
        
        return QualityScore(
            metric=QualityMetric.SECURITY_SCORE,
            score=score,
            issues_count=len(issues)
        ), issues
    
    def _analyze_performance(self, element: CodeElement) -> Tuple[QualityScore, List[QualityIssue]]:
        """Analyze performance issues"""
        
        issues = []
        performance_issues_count = 0
        total_impact = 0
        
        if not element.code_snippet:
            return QualityScore(QualityMetric.PERFORMANCE_SCORE, 10.0), issues
        
        # Check for performance anti-patterns
        for pattern_type, config in self.performance_patterns.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, element.code_snippet, re.IGNORECASE)
                
                for match in matches:
                    performance_issues_count += 1
                    
                    # Calculate impact score
                    impact_scores = {
                        QualitySeverity.HIGH: 8,
                        QualitySeverity.MEDIUM: 5,
                        QualitySeverity.LOW: 2
                    }
                    impact = impact_scores[config['severity']]
                    total_impact += impact
                    
                    # Find line number
                    line_number = element.code_snippet[:match.start()].count('\n') + 1
                    
                    issues.append(QualityIssue(
                        metric=QualityMetric.PERFORMANCE_SCORE,
                        severity=config['severity'],
                        title=f"Performance issue: {pattern_type.replace('_', ' ').title()}",
                        description=config['description'],
                        location=f"{element.file_path}:{element.name}",
                        line_number=line_number,
                        suggestion=self._get_performance_suggestion(pattern_type),
                        effort_estimate=self._get_performance_effort(config['severity']),
                        impact_score=impact
                    ))
        
        # Calculate performance score
        if performance_issues_count == 0:
            score = 10.0
        else:
            # Penalize based on number and impact of issues
            penalty = min(total_impact / 3, 8.0)
            score = max(10.0 - penalty, 2.0)
        
        return QualityScore(
            metric=QualityMetric.PERFORMANCE_SCORE,
            score=score,
            issues_count=len(issues)
        ), issues
    
    def _analyze_readability(self, element: CodeElement) -> Tuple[QualityScore, List[QualityIssue]]:
        """Analyze code readability"""
        
        issues = []
        
        if not element.code_snippet:
            return QualityScore(QualityMetric.READABILITY_SCORE, 10.0), issues
        
        try:
            lines = element.code_snippet.split('\n')
            code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            
            # Calculate readability factors
            avg_line_length = sum(len(line) for line in code_lines) / max(len(code_lines), 1)
            long_lines = len([line for line in code_lines if len(line) > 120])
            
            # Check for naming conventions
            poor_names = self._check_naming_conventions(element.code_snippet)
            
            # Check for magic numbers
            magic_numbers = self._find_magic_numbers(element.code_snippet)
            
            # Calculate score
            score = 10.0
            
            # Penalize long lines
            if long_lines > 0:
                score -= min(long_lines * 0.5, 2.0)
                issues.append(QualityIssue(
                    metric=QualityMetric.READABILITY_SCORE,
                    severity=QualitySeverity.LOW,
                    title=f"Long lines detected ({long_lines} lines > 120 chars)",
                    description="Long lines reduce code readability",
                    location=f"{element.file_path}:{element.name}",
                    suggestion="Break long lines into multiple lines",
                    effort_estimate="30 minutes",
                    impact_score=2.0
                ))
            
            # Penalize poor naming
            if poor_names > 0:
                score -= min(poor_names * 0.3, 2.0)
                issues.append(QualityIssue(
                    metric=QualityMetric.READABILITY_SCORE,
                    severity=QualitySeverity.MEDIUM,
                    title=f"Poor naming conventions ({poor_names} instances)",
                    description="Variable/function names should be descriptive",
                    location=f"{element.file_path}:{element.name}",
                    suggestion="Use descriptive names for variables and functions",
                    effort_estimate="1-2 hours",
                    impact_score=3.0
                ))
            
            # Penalize magic numbers
            if magic_numbers > 0:
                score -= min(magic_numbers * 0.2, 1.5)
                issues.append(QualityIssue(
                    metric=QualityMetric.READABILITY_SCORE,
                    severity=QualitySeverity.LOW,
                    title=f"Magic numbers detected ({magic_numbers} instances)",
                    description="Magic numbers should be replaced with named constants",
                    location=f"{element.file_path}:{element.name}",
                    suggestion="Replace magic numbers with named constants",
                    effort_estimate="1 hour",
                    impact_score=2.0
                ))
            
            score = max(score, 1.0)
            
            return QualityScore(
                metric=QualityMetric.READABILITY_SCORE,
                score=score,
                issues_count=len(issues)
            ), issues
            
        except Exception as e:
            print(f"Readability analysis failed: {e}")
            return QualityScore(QualityMetric.READABILITY_SCORE, 5.0), issues
    
    def _analyze_documentation(self, element: CodeElement) -> Tuple[QualityScore, List[QualityIssue]]:
        """Analyze documentation coverage"""
        
        issues = []
        
        if not element.code_snippet:
            return QualityScore(QualityMetric.DOCUMENTATION_COVERAGE, 10.0), issues
        
        try:
            # Check for docstrings/comments
            has_docstring = '"""' in element.code_snippet or "'''" in element.code_snippet
            has_comments = '#' in element.code_snippet or '//' in element.code_snippet
            
            # Calculate documentation ratio
            lines = element.code_snippet.split('\n')
            comment_lines = len([line for line in lines if line.strip().startswith(('#', '//'))])
            docstring_lines = 0
            
            # Count docstring lines
            if '"""' in element.code_snippet:
                docstring_matches = re.findall(r'""".*?"""', element.code_snippet, re.DOTALL)
                docstring_lines = sum(match.count('\n') + 1 for match in docstring_matches)
            
            total_lines = len(lines)
            doc_ratio = (comment_lines + docstring_lines) / max(total_lines, 1)
            
            # Calculate score
            score = 5.0  # Base score
            
            if has_docstring:
                score += 3.0
            if has_comments:
                score += 1.0
            if doc_ratio > 0.2:
                score += 1.0
            
            score = min(score, 10.0)
            
            # Create issues for poor documentation
            if not has_docstring and element.element_type in [ElementType.CLASS, ElementType.FUNCTION, ElementType.METHOD]:
                issues.append(QualityIssue(
                    metric=QualityMetric.DOCUMENTATION_COVERAGE,
                    severity=QualitySeverity.MEDIUM,
                    title="Missing docstring",
                    description=f"This {element.element_type.value} lacks a docstring",
                    location=f"{element.file_path}:{element.name}",
                    suggestion="Add a descriptive docstring explaining purpose, parameters, and return value",
                    effort_estimate="15-30 minutes",
                    impact_score=3.0
                ))
            
            if doc_ratio < 0.1:
                issues.append(QualityIssue(
                    metric=QualityMetric.DOCUMENTATION_COVERAGE,
                    severity=QualitySeverity.LOW,
                    title="Low documentation coverage",
                    description="Code lacks sufficient comments and documentation",
                    location=f"{element.file_path}:{element.name}",
                    suggestion="Add comments to explain complex logic and business rules",
                    effort_estimate="1-2 hours",
                    impact_score=2.0
                ))
            
            return QualityScore(
                metric=QualityMetric.DOCUMENTATION_COVERAGE,
                score=score,
                issues_count=len(issues)
            ), issues
            
        except Exception as e:
            print(f"Documentation analysis failed: {e}")
            return QualityScore(QualityMetric.DOCUMENTATION_COVERAGE, 5.0), issues
    
    def _estimate_complexity(self, code: str) -> int:
        """Estimate cyclomatic complexity from code"""
        
        complexity = 1
        decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'and', 'or']
        
        for keyword in decision_keywords:
            complexity += code.lower().count(keyword)
        
        return complexity
    
    def _check_naming_conventions(self, code: str) -> int:
        """Check for poor naming conventions"""
        
        poor_names = 0
        
        # Find variable names (simplified)
        var_patterns = [
            r'\b[a-z]\b',  # Single letter variables
            r'\b\w*\d+\w*\b',  # Variables with numbers
            r'\b[A-Z]{2,}\b'  # All caps (except constants)
        ]
        
        for pattern in var_patterns:
            matches = re.findall(pattern, code)
            poor_names += len(matches)
        
        return poor_names
    
    def _find_magic_numbers(self, code: str) -> int:
        """Find magic numbers in code"""
        
        # Find numeric literals (excluding 0, 1, -1)
        number_pattern = r'\b(?<![\w.])[2-9]\d*(?![\w.])\b'
        matches = re.findall(number_pattern, code)
        
        return len(matches)
    
    def _calculate_overall_score(self, scores: Dict[QualityMetric, QualityScore]) -> float:
        """Calculate overall quality score"""
        
        if not scores:
            return 5.0
        
        # Weight different metrics
        weights = {
            QualityMetric.CYCLOMATIC_COMPLEXITY: 0.2,
            QualityMetric.MAINTAINABILITY_INDEX: 0.2,
            QualityMetric.SECURITY_SCORE: 0.25,
            QualityMetric.PERFORMANCE_SCORE: 0.15,
            QualityMetric.READABILITY_SCORE: 0.1,
            QualityMetric.DOCUMENTATION_COVERAGE: 0.1
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for metric, score in scores.items():
            weight = weights.get(metric, 0.1)
            weighted_sum += score.score * weight
            total_weight += weight
        
        return weighted_sum / max(total_weight, 1)
    
    def _generate_recommendations(self, scores: Dict[QualityMetric, QualityScore], issues: List[QualityIssue]) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        # Priority recommendations based on scores
        for metric, score in scores.items():
            if score.score < 6.0:
                if metric == QualityMetric.CYCLOMATIC_COMPLEXITY:
                    recommendations.append("Reduce cyclomatic complexity by breaking down complex functions")
                elif metric == QualityMetric.SECURITY_SCORE:
                    recommendations.append("Address security vulnerabilities immediately")
                elif metric == QualityMetric.PERFORMANCE_SCORE:
                    recommendations.append("Optimize performance bottlenecks")
                elif metric == QualityMetric.READABILITY_SCORE:
                    recommendations.append("Improve code readability with better naming and formatting")
                elif metric == QualityMetric.DOCUMENTATION_COVERAGE:
                    recommendations.append("Add comprehensive documentation and comments")
        
        # Add specific recommendations based on critical issues
        critical_issues = [issue for issue in issues if issue.severity == QualitySeverity.CRITICAL]
        if critical_issues:
            recommendations.insert(0, "Address critical security vulnerabilities immediately")
        
        high_issues = [issue for issue in issues if issue.severity == QualitySeverity.HIGH]
        if len(high_issues) > 3:
            recommendations.append("Consider a comprehensive refactoring to address multiple high-priority issues")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _get_security_suggestion(self, vuln_type: str) -> str:
        """Get security-specific suggestions"""
        
        suggestions = {
            'sql_injection': "Use parameterized queries or prepared statements",
            'xss_vulnerability': "Sanitize user input and use safe DOM manipulation methods",
            'hardcoded_secrets': "Move secrets to environment variables or secure configuration",
            'weak_crypto': "Use strong cryptographic algorithms (AES, SHA-256, etc.)"
        }
        
        return suggestions.get(vuln_type, "Review security best practices for this vulnerability type")
    
    def _get_performance_suggestion(self, pattern_type: str) -> str:
        """Get performance-specific suggestions"""
        
        suggestions = {
            'nested_loops': "Consider using more efficient algorithms or data structures",
            'inefficient_string_concat': "Use string builders or join operations for multiple concatenations",
            'database_in_loop': "Use batch operations or move database calls outside the loop",
            'memory_leak_potential': "Ensure proper cleanup and avoid global state accumulation"
        }
        
        return suggestions.get(pattern_type, "Review performance best practices")
    
    def _get_security_effort(self, severity: QualitySeverity) -> str:
        """Get effort estimate for security fixes"""
        
        efforts = {
            QualitySeverity.CRITICAL: "Immediate (1-4 hours)",
            QualitySeverity.HIGH: "High priority (4-8 hours)",
            QualitySeverity.MEDIUM: "Medium priority (2-4 hours)",
            QualitySeverity.LOW: "Low priority (1-2 hours)"
        }
        
        return efforts.get(severity, "Variable")
    
    def _get_performance_effort(self, severity: QualitySeverity) -> str:
        """Get effort estimate for performance fixes"""
        
        efforts = {
            QualitySeverity.HIGH: "1-2 days",
            QualitySeverity.MEDIUM: "4-8 hours",
            QualitySeverity.LOW: "1-2 hours"
        }
        
        return efforts.get(severity, "Variable")
    
    def get_quality_trends(self, element_id: str, days: int = 30) -> Dict[QualityMetric, QualityTrend]:
        """Get quality trends for an element over time"""
        
        if element_id not in self.quality_history:
            return {}
        
        # Filter reports by time range
        cutoff_date = datetime.now() - timedelta(days=days)
        reports = [r for r in self.quality_history[element_id] if r.analysis_timestamp >= cutoff_date]
        
        if len(reports) < 2:
            return {}
        
        trends = {}
        
        # Analyze trends for each metric
        for metric in QualityMetric:
            timestamps = []
            scores = []
            
            for report in reports:
                if metric in report.scores:
                    timestamps.append(report.analysis_timestamp)
                    scores.append(report.scores[metric].score)
            
            if len(scores) >= 2:
                # Calculate trend
                trend = self._calculate_trend(scores)
                
                trends[metric] = QualityTrend(
                    metric=metric,
                    timestamps=timestamps,
                    scores=scores,
                    trend_direction=trend['direction'],
                    trend_strength=trend['strength'],
                    prediction=trend.get('prediction')
                )
        
        return trends
    
    def _calculate_trend(self, scores: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and strength"""
        
        if len(scores) < 2:
            return {'direction': 'stable', 'strength': 0.0}
        
        # Simple linear trend calculation
        n = len(scores)
        x = list(range(n))
        
        # Calculate slope
        x_mean = sum(x) / n
        y_mean = sum(scores) / n
        
        numerator = sum((x[i] - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # Determine trend direction and strength
        if abs(slope) < 0.1:
            direction = 'stable'
            strength = 0.0
        elif slope > 0:
            direction = 'improving'
            strength = min(abs(slope), 1.0)
        else:
            direction = 'declining'
            strength = min(abs(slope), 1.0)
        
        # Simple prediction (next value)
        if len(scores) >= 3:
            prediction = scores[-1] + slope
            prediction = max(0, min(prediction, 10))  # Clamp to valid range
        else:
            prediction = None
        
        return {
            'direction': direction,
            'strength': strength,
            'prediction': prediction
        }
    
    def get_repository_quality_summary(self, repository_id: str) -> Dict[str, Any]:
        """Get quality summary for entire repository"""
        
        # Get all reports for this repository
        repo_reports = []
        for element_reports in self.quality_history.values():
            repo_reports.extend([r for r in element_reports if r.repository_id == repository_id])
        
        if not repo_reports:
            return {'error': 'No quality data available for this repository'}
        
        # Get latest reports for each element
        latest_reports = {}
        for report in repo_reports:
            if (report.element_id not in latest_reports or 
                report.analysis_timestamp > latest_reports[report.element_id].analysis_timestamp):
                latest_reports[report.element_id] = report
        
        reports = list(latest_reports.values())
        
        # Calculate summary statistics
        overall_scores = [r.overall_score for r in reports]
        avg_score = sum(overall_scores) / len(overall_scores)
        
        # Count issues by severity
        all_issues = []
        for report in reports:
            all_issues.extend(report.issues)
        
        issues_by_severity = {}
        for severity in QualitySeverity:
            issues_by_severity[severity.value] = len([i for i in all_issues if i.severity == severity])
        
        # Calculate metric averages
        metric_averages = {}
        for metric in QualityMetric:
            scores = []
            for report in reports:
                if metric in report.scores:
                    scores.append(report.scores[metric].score)
            
            if scores:
                metric_averages[metric.value] = sum(scores) / len(scores)
        
        return {
            'repository_id': repository_id,
            'total_elements_analyzed': len(reports),
            'overall_average_score': avg_score,
            'issues_by_severity': issues_by_severity,
            'metric_averages': metric_averages,
            'last_analysis': max(r.analysis_timestamp for r in reports).isoformat(),
            'quality_grade': self._get_quality_grade(avg_score)
        }
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade"""
        
        if score >= 9.0:
            return 'A+'
        elif score >= 8.5:
            return 'A'
        elif score >= 8.0:
            return 'A-'
        elif score >= 7.5:
            return 'B+'
        elif score >= 7.0:
            return 'B'
        elif score >= 6.5:
            return 'B-'
        elif score >= 6.0:
            return 'C+'
        elif score >= 5.5:
            return 'C'
        elif score >= 5.0:
            return 'C-'
        elif score >= 4.0:
            return 'D'
        else:
            return 'F'


# Global quality engine instance
quality_engine = QualityEngine()