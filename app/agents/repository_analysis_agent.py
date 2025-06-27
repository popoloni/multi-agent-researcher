"""
Repository Analysis Agent for Phase 4 Kenobi Code Analysis Agent
Specialized agent for comprehensive repository analysis and insights
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

from app.agents.base_agent import BaseAgent
from app.models.repository_schemas import Repository, CodeElement, RepositoryAnalysis
from app.services.repository_service import RepositoryService
from app.tools.dependency_analyzer import DependencyAnalyzer
from app.engines.quality_engine import QualityEngine
from app.engines.ai_engine import AIEngine
from app.engines.vector_service import VectorService


class RepositoryAnalysisAgent(BaseAgent):
    """Specialized agent for deep repository analysis and insights"""
    
    def __init__(self, model: str = "llama3.1:8b", provider: str = "ollama"):
        super().__init__(
            model=model,
            name="Repository Analysis Agent"
        )
        
        self.repository_service = RepositoryService()
        self.dependency_analyzer = DependencyAnalyzer()
        self.quality_engine = QualityEngine()
        self.ai_engine = AIEngine()
        self.vector_service = VectorService()
        
        # Analysis cache
        self.analysis_cache: Dict[str, Dict] = {}
        self.cache_ttl = timedelta(hours=1)
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for repository analysis"""
        return """You are a specialized Repository Analysis Agent focused on comprehensive code repository analysis.

Your capabilities include:
- Code structure analysis and organization assessment
- Quality metrics calculation and evaluation
- Dependency analysis and relationship mapping
- Pattern detection and architectural insights
- Complexity analysis and maintainability scoring
- Performance optimization recommendations

Provide detailed, actionable insights with specific recommendations for improvement.
Focus on code quality, maintainability, and architectural best practices."""
    
    async def analyze_repository_comprehensive(self, repository_id: str) -> Dict[str, Any]:
        """Perform comprehensive repository analysis"""
        try:
            # Check cache first
            cache_key = f"comprehensive_{repository_id}"
            if self._is_cache_valid(cache_key):
                return self.analysis_cache[cache_key]["data"]
            
            repository = await self.repository_service.get_repository_metadata(repository_id)
            if not repository:
                raise ValueError(f"Repository {repository_id} not found")
            
            # Parallel analysis tasks
            tasks = [
                self._analyze_code_structure(repository),
                self._analyze_quality_metrics(repository),
                self._analyze_dependencies(repository),
                self._analyze_patterns(repository),
                self._analyze_complexity(repository),
                self._analyze_maintainability(repository)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            analysis = {
                "repository_id": repository_id,
                "repository_name": repository.name,
                "analysis_timestamp": datetime.now().isoformat(),
                "code_structure": results[0] if not isinstance(results[0], Exception) else {},
                "quality_metrics": results[1] if not isinstance(results[1], Exception) else {},
                "dependencies": results[2] if not isinstance(results[2], Exception) else {},
                "patterns": results[3] if not isinstance(results[3], Exception) else {},
                "complexity": results[4] if not isinstance(results[4], Exception) else {},
                "maintainability": results[5] if not isinstance(results[5], Exception) else {},
                "overall_score": 0.0,
                "recommendations": []
            }
            
            # Calculate overall score
            analysis["overall_score"] = self._calculate_overall_score(analysis)
            
            # Generate recommendations
            analysis["recommendations"] = await self._generate_recommendations(analysis)
            
            # Cache result
            self._cache_result(cache_key, analysis)
            
            return analysis
            
        except Exception as e:
            return {
                "error": f"Repository analysis failed: {str(e)}",
                "repository_id": repository_id,
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_code_structure(self, repository: Repository) -> Dict[str, Any]:
        """Analyze code structure and organization"""
        try:
            elements = await self.repository_service.indexing_service.get_repository_elements(repository.id)
            
            # Count by type
            type_counts = {}
            language_counts = {}
            file_counts = {}
            
            for element in elements:
                # Element types
                element_type = element.get("element_type", "unknown")
                type_counts[element_type] = type_counts.get(element_type, 0) + 1
                
                # Languages
                language = element.get("language", "unknown")
                language_counts[language] = language_counts.get(language, 0) + 1
                
                # File extensions
                file_path = element.get("file_path", "")
                if file_path:
                    ext = Path(file_path).suffix
                    file_counts[ext] = file_counts.get(ext, 0) + 1
            
            # Calculate structure metrics
            total_elements = len(elements)
            avg_elements_per_file = total_elements / len(file_counts) if file_counts else 0
            
            return {
                "total_elements": total_elements,
                "element_types": type_counts,
                "languages": language_counts,
                "file_extensions": file_counts,
                "avg_elements_per_file": round(avg_elements_per_file, 2),
                "structure_score": self._calculate_structure_score(type_counts, total_elements)
            }
            
        except Exception as e:
            return {"error": f"Structure analysis failed: {str(e)}"}
    
    async def _analyze_quality_metrics(self, repository: Repository) -> Dict[str, Any]:
        """Analyze repository quality metrics"""
        try:
            elements = await self.repository_service.indexing_service.get_repository_elements(repository.id)
            
            quality_scores = []
            detailed_metrics = {
                "complexity": [],
                "maintainability": [],
                "readability": [],
                "documentation": [],
                "security": []
            }
            
            # Analyze each element
            for element in elements[:50]:  # Limit for performance
                try:
                    code_element = self._dict_to_code_element(element)
                    quality_result = await self.quality_engine.analyze_element_quality(code_element)
                    
                    if "overall_score" in quality_result:
                        quality_scores.append(quality_result["overall_score"])
                        
                        # Collect detailed metrics
                        metrics = quality_result.get("metrics", {})
                        for metric_name, metric_data in metrics.items():
                            if metric_name in detailed_metrics and isinstance(metric_data, dict):
                                score = metric_data.get("score", 0)
                                detailed_metrics[metric_name].append(score)
                                
                except Exception as e:
                    continue
            
            # Calculate averages
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            avg_metrics = {}
            for metric_name, scores in detailed_metrics.items():
                avg_metrics[metric_name] = sum(scores) / len(scores) if scores else 0
            
            return {
                "average_quality_score": round(avg_quality, 2),
                "elements_analyzed": len(quality_scores),
                "detailed_metrics": {k: round(v, 2) for k, v in avg_metrics.items()},
                "quality_distribution": self._calculate_quality_distribution(quality_scores)
            }
            
        except Exception as e:
            return {"error": f"Quality analysis failed: {str(e)}"}
    
    async def _analyze_dependencies(self, repository: Repository) -> Dict[str, Any]:
        """Analyze repository dependencies"""
        try:
            dependency_graph = await self.dependency_analyzer.build_dependency_graph(repository)
            
            # Calculate dependency metrics
            total_dependencies = len(dependency_graph.dependencies)
            circular_deps = await self.dependency_analyzer.find_circular_dependencies(dependency_graph)
            coupling_metrics = await self.dependency_analyzer.calculate_coupling_metrics(dependency_graph)
            
            # Analyze dependency patterns
            internal_deps = sum(1 for dep in dependency_graph.dependencies if dep.is_internal)
            external_deps = total_dependencies - internal_deps
            
            return {
                "total_dependencies": total_dependencies,
                "internal_dependencies": internal_deps,
                "external_dependencies": external_deps,
                "circular_dependencies": len(circular_deps),
                "coupling_metrics": coupling_metrics,
                "dependency_health_score": self._calculate_dependency_health(
                    total_dependencies, len(circular_deps), coupling_metrics
                )
            }
            
        except Exception as e:
            return {"error": f"Dependency analysis failed: {str(e)}"}
    
    async def _analyze_patterns(self, repository: Repository) -> Dict[str, Any]:
        """Analyze code patterns and anti-patterns"""
        try:
            elements = await self.repository_service.indexing_service.get_repository_elements(repository.id)
            
            patterns_found = {
                "design_patterns": [],
                "architectural_patterns": [],
                "anti_patterns": [],
                "code_smells": []
            }
            
            # Analyze patterns in code elements
            for element in elements[:30]:  # Limit for performance
                try:
                    code_element = self._dict_to_code_element(element)
                    
                    # Use AI to detect patterns
                    pattern_analysis = await self.ai_engine.analyze_code(
                        code_element.code_snippet,
                        "pattern_detection",
                        {"element_type": code_element.element_type}
                    )
                    
                    if "patterns" in pattern_analysis:
                        for pattern_type, pattern_list in pattern_analysis["patterns"].items():
                            if pattern_type in patterns_found:
                                patterns_found[pattern_type].extend(pattern_list)
                                
                except Exception:
                    continue
            
            # Count unique patterns
            pattern_counts = {}
            for pattern_type, pattern_list in patterns_found.items():
                pattern_counts[pattern_type] = len(set(pattern_list))
            
            return {
                "pattern_counts": pattern_counts,
                "patterns_found": patterns_found,
                "pattern_score": self._calculate_pattern_score(pattern_counts)
            }
            
        except Exception as e:
            return {"error": f"Pattern analysis failed: {str(e)}"}
    
    async def _analyze_complexity(self, repository: Repository) -> Dict[str, Any]:
        """Analyze code complexity metrics"""
        try:
            elements = await self.repository_service.indexing_service.get_repository_elements(repository.id)
            
            complexity_metrics = {
                "cyclomatic_complexity": [],
                "cognitive_complexity": [],
                "lines_of_code": [],
                "function_length": []
            }
            
            for element in elements:
                try:
                    code_snippet = element.get("code_snippet", "")
                    if not code_snippet:
                        continue
                    
                    # Calculate basic metrics
                    lines = len(code_snippet.split('\n'))
                    complexity_metrics["lines_of_code"].append(lines)
                    
                    # Estimate complexity based on code patterns
                    cyclomatic = self._estimate_cyclomatic_complexity(code_snippet)
                    complexity_metrics["cyclomatic_complexity"].append(cyclomatic)
                    
                    if element.get("element_type") == "function":
                        complexity_metrics["function_length"].append(lines)
                        
                except Exception:
                    continue
            
            # Calculate averages and distributions
            avg_metrics = {}
            for metric_name, values in complexity_metrics.items():
                if values:
                    avg_metrics[f"avg_{metric_name}"] = round(sum(values) / len(values), 2)
                    avg_metrics[f"max_{metric_name}"] = max(values)
                    avg_metrics[f"min_{metric_name}"] = min(values)
            
            return {
                "complexity_metrics": avg_metrics,
                "complexity_score": self._calculate_complexity_score(avg_metrics)
            }
            
        except Exception as e:
            return {"error": f"Complexity analysis failed: {str(e)}"}
    
    async def _analyze_maintainability(self, repository: Repository) -> Dict[str, Any]:
        """Analyze code maintainability factors"""
        try:
            elements = await self.repository_service.indexing_service.get_repository_elements(repository.id)
            
            maintainability_factors = {
                "documentation_coverage": 0,
                "test_coverage_estimate": 0,
                "naming_quality": 0,
                "modularity_score": 0,
                "duplication_estimate": 0
            }
            
            documented_elements = 0
            test_elements = 0
            total_elements = len(elements)
            
            for element in elements:
                # Check documentation
                description = element.get("description", "")
                if description and len(description) > 20:
                    documented_elements += 1
                
                # Check for test files
                file_path = element.get("file_path", "")
                if "test" in file_path.lower() or "spec" in file_path.lower():
                    test_elements += 1
            
            # Calculate factors
            if total_elements > 0:
                maintainability_factors["documentation_coverage"] = documented_elements / total_elements
                maintainability_factors["test_coverage_estimate"] = test_elements / total_elements
            
            # Estimate other factors
            maintainability_factors["naming_quality"] = await self._estimate_naming_quality(elements)
            maintainability_factors["modularity_score"] = await self._estimate_modularity(elements)
            
            overall_maintainability = sum(maintainability_factors.values()) / len(maintainability_factors)
            
            return {
                "maintainability_factors": {k: round(v, 2) for k, v in maintainability_factors.items()},
                "overall_maintainability": round(overall_maintainability, 2),
                "maintainability_grade": self._get_maintainability_grade(overall_maintainability)
            }
            
        except Exception as e:
            return {"error": f"Maintainability analysis failed: {str(e)}"}
    
    async def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate improvement recommendations based on analysis"""
        recommendations = []
        
        try:
            # Quality recommendations
            quality_metrics = analysis.get("quality_metrics", {})
            if quality_metrics.get("average_quality_score", 0) < 0.7:
                recommendations.append({
                    "type": "quality",
                    "priority": "high",
                    "title": "Improve Code Quality",
                    "description": "Overall code quality is below recommended threshold",
                    "action": "Focus on improving code documentation, reducing complexity, and enhancing readability"
                })
            
            # Dependency recommendations
            dependencies = analysis.get("dependencies", {})
            if dependencies.get("circular_dependencies", 0) > 0:
                recommendations.append({
                    "type": "architecture",
                    "priority": "medium",
                    "title": "Resolve Circular Dependencies",
                    "description": f"Found {dependencies.get('circular_dependencies')} circular dependencies",
                    "action": "Refactor code to eliminate circular dependencies and improve modularity"
                })
            
            # Complexity recommendations
            complexity = analysis.get("complexity", {})
            complexity_metrics = complexity.get("complexity_metrics", {})
            if complexity_metrics.get("avg_cyclomatic_complexity", 0) > 10:
                recommendations.append({
                    "type": "complexity",
                    "priority": "medium",
                    "title": "Reduce Code Complexity",
                    "description": "Average cyclomatic complexity is high",
                    "action": "Break down complex functions into smaller, more manageable pieces"
                })
            
            # Maintainability recommendations
            maintainability = analysis.get("maintainability", {})
            factors = maintainability.get("maintainability_factors", {})
            if factors.get("documentation_coverage", 0) < 0.5:
                recommendations.append({
                    "type": "documentation",
                    "priority": "low",
                    "title": "Improve Documentation",
                    "description": "Documentation coverage is below 50%",
                    "action": "Add comprehensive documentation to functions and classes"
                })
            
            return recommendations
            
        except Exception as e:
            return [{"type": "error", "description": f"Failed to generate recommendations: {str(e)}"}]
    
    def _calculate_overall_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall repository score"""
        scores = []
        
        # Quality score
        quality_score = analysis.get("quality_metrics", {}).get("average_quality_score", 0)
        scores.append(quality_score * 0.3)  # 30% weight
        
        # Dependency health
        dep_score = analysis.get("dependencies", {}).get("dependency_health_score", 0)
        scores.append(dep_score * 0.2)  # 20% weight
        
        # Pattern score
        pattern_score = analysis.get("patterns", {}).get("pattern_score", 0)
        scores.append(pattern_score * 0.2)  # 20% weight
        
        # Complexity score
        complexity_score = analysis.get("complexity", {}).get("complexity_score", 0)
        scores.append(complexity_score * 0.15)  # 15% weight
        
        # Maintainability score
        maint_score = analysis.get("maintainability", {}).get("overall_maintainability", 0)
        scores.append(maint_score * 0.15)  # 15% weight
        
        return round(sum(scores), 2)
    
    def _calculate_structure_score(self, type_counts: Dict[str, int], total_elements: int) -> float:
        """Calculate structure organization score"""
        if total_elements == 0:
            return 0.0
        
        # Prefer balanced distribution of element types
        type_diversity = len(type_counts) / max(1, total_elements / 10)
        return min(1.0, type_diversity)
    
    def _calculate_quality_distribution(self, quality_scores: List[float]) -> Dict[str, int]:
        """Calculate quality score distribution"""
        distribution = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        
        for score in quality_scores:
            if score >= 0.9:
                distribution["excellent"] += 1
            elif score >= 0.7:
                distribution["good"] += 1
            elif score >= 0.5:
                distribution["fair"] += 1
            else:
                distribution["poor"] += 1
        
        return distribution
    
    def _calculate_dependency_health(self, total_deps: int, circular_deps: int, coupling_metrics: Dict) -> float:
        """Calculate dependency health score"""
        if total_deps == 0:
            return 1.0
        
        # Penalize circular dependencies
        circular_penalty = circular_deps / total_deps
        
        # Consider coupling metrics
        coupling_score = coupling_metrics.get("average_coupling", 0.5)
        
        health_score = 1.0 - circular_penalty - (coupling_score * 0.3)
        return max(0.0, min(1.0, health_score))
    
    def _calculate_pattern_score(self, pattern_counts: Dict[str, int]) -> float:
        """Calculate pattern usage score"""
        good_patterns = pattern_counts.get("design_patterns", 0) + pattern_counts.get("architectural_patterns", 0)
        bad_patterns = pattern_counts.get("anti_patterns", 0) + pattern_counts.get("code_smells", 0)
        
        if good_patterns + bad_patterns == 0:
            return 0.5
        
        return good_patterns / (good_patterns + bad_patterns)
    
    def _calculate_complexity_score(self, metrics: Dict[str, float]) -> float:
        """Calculate complexity score (lower complexity = higher score)"""
        avg_complexity = metrics.get("avg_cyclomatic_complexity", 5)
        
        # Normalize complexity (ideal is around 5, penalize above 10)
        if avg_complexity <= 5:
            return 1.0
        elif avg_complexity <= 10:
            return 1.0 - ((avg_complexity - 5) / 5) * 0.5
        else:
            return max(0.0, 0.5 - ((avg_complexity - 10) / 10) * 0.5)
    
    def _get_maintainability_grade(self, score: float) -> str:
        """Get maintainability grade"""
        if score >= 0.9:
            return "A+"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B"
        elif score >= 0.6:
            return "C"
        elif score >= 0.5:
            return "D"
        else:
            return "F"
    
    def _estimate_cyclomatic_complexity(self, code: str) -> int:
        """Estimate cyclomatic complexity from code"""
        # Simple heuristic based on control flow keywords
        complexity_keywords = ["if", "elif", "else", "for", "while", "try", "except", "case", "switch"]
        complexity = 1  # Base complexity
        
        for keyword in complexity_keywords:
            complexity += code.lower().count(keyword)
        
        return complexity
    
    async def _estimate_naming_quality(self, elements: List[Dict]) -> float:
        """Estimate naming quality of code elements"""
        good_names = 0
        total_names = 0
        
        for element in elements:
            name = element.get("name", "")
            if name:
                total_names += 1
                # Simple heuristics for good naming
                if (len(name) > 3 and 
                    not name.startswith("_") and 
                    any(c.isupper() for c in name[1:]) or "_" in name):
                    good_names += 1
        
        return good_names / total_names if total_names > 0 else 0.5
    
    async def _estimate_modularity(self, elements: List[Dict]) -> float:
        """Estimate code modularity"""
        # Count unique files and modules
        files = set()
        for element in elements:
            file_path = element.get("file_path", "")
            if file_path:
                files.add(file_path)
        
        # More files with fewer elements per file indicates better modularity
        elements_per_file = len(elements) / len(files) if files else 1
        
        # Ideal is around 10-20 elements per file
        if elements_per_file <= 20:
            return 1.0
        else:
            return max(0.0, 1.0 - ((elements_per_file - 20) / 50))
    
    def _dict_to_code_element(self, element_dict: Dict) -> CodeElement:
        """Convert dictionary to CodeElement"""
        return CodeElement(
            id=element_dict.get("id", ""),
            repository_id=element_dict.get("repository_id", ""),
            file_path=element_dict.get("file_path", ""),
            element_type=element_dict.get("element_type", ""),
            name=element_dict.get("name", ""),
            description=element_dict.get("description", ""),
            categories=element_dict.get("categories", []),
            dependencies=element_dict.get("dependencies", []),
            code_snippet=element_dict.get("code_snippet", ""),
            language=element_dict.get("language", ""),
            start_line=element_dict.get("start_line", 0),
            end_line=element_dict.get("end_line", 0)
        )
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is valid"""
        if cache_key not in self.analysis_cache:
            return False
        
        cache_entry = self.analysis_cache[cache_key]
        return datetime.now() - cache_entry["timestamp"] < self.cache_ttl
    
    def _cache_result(self, cache_key: str, data: Dict[str, Any]):
        """Cache analysis result"""
        self.analysis_cache[cache_key] = {
            "timestamp": datetime.now(),
            "data": data
        }
        
        # Clean old cache entries
        cutoff_time = datetime.now() - self.cache_ttl
        self.analysis_cache = {
            k: v for k, v in self.analysis_cache.items()
            if v["timestamp"] > cutoff_time
        }