"""
Dependency Analysis Agent for Phase 4 Kenobi Code Analysis Agent
Specialized agent for advanced dependency analysis and relationship mapping
"""

import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict, deque
import json
import re

from app.agents.base_agent import BaseAgent
from app.models.repository_schemas import Repository, CodeElement, DependencyGraph, DependencyEdge
from app.services.repository_service import RepositoryService
from app.tools.dependency_analyzer import DependencyAnalyzer
from app.engines.ai_engine import AIEngine


class DependencyAnalysisAgent(BaseAgent):
    """Specialized agent for advanced dependency analysis and relationship mapping"""
    
    def __init__(self, model: str = "llama3.1:8b", provider: str = "ollama"):
        super().__init__(
            model=model,
            name="Dependency Analysis Agent"
        )
        
        self.repository_service = RepositoryService()
        self.dependency_analyzer = DependencyAnalyzer()
        self.ai_engine = AIEngine()
        
        # Analysis cache
        self.dependency_cache: Dict[str, Dict] = {}
        self.relationship_cache: Dict[str, Dict] = {}
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for dependency analysis"""
        return """You are a specialized Dependency Analysis Agent focused on code dependency analysis and relationship mapping.

Your capabilities include:
- Cross-repository dependency analysis
- Dependency impact assessment and change analysis
- Dependency health monitoring and scoring
- Circular dependency detection and resolution
- Architectural pattern and anti-pattern identification
- Integration opportunity discovery

Provide detailed dependency insights with actionable recommendations for improving code architecture and reducing coupling."""
    
    async def analyze_cross_repository_dependencies(self, repository_ids: List[str]) -> Dict[str, Any]:
        """Analyze dependencies across multiple repositories"""
        try:
            cross_repo_analysis = {
                "repository_ids": repository_ids,
                "analysis_timestamp": datetime.now().isoformat(),
                "repositories": {},
                "cross_dependencies": [],
                "shared_dependencies": {},
                "dependency_conflicts": [],
                "integration_points": [],
                "recommendations": []
            }
            
            # Analyze each repository
            for repo_id in repository_ids:
                try:
                    repository = await self.repository_service.get_repository_metadata(repo_id)
                    if repository:
                        repo_analysis = await self._analyze_single_repository_dependencies(repository)
                        cross_repo_analysis["repositories"][repo_id] = repo_analysis
                except Exception as e:
                    cross_repo_analysis["repositories"][repo_id] = {"error": str(e)}
            
            # Find cross-repository relationships
            cross_repo_analysis["cross_dependencies"] = await self._find_cross_repository_dependencies(
                cross_repo_analysis["repositories"]
            )
            
            # Identify shared dependencies
            cross_repo_analysis["shared_dependencies"] = await self._identify_shared_dependencies(
                cross_repo_analysis["repositories"]
            )
            
            # Detect conflicts
            cross_repo_analysis["dependency_conflicts"] = await self._detect_dependency_conflicts(
                cross_repo_analysis["repositories"]
            )
            
            # Find integration points
            cross_repo_analysis["integration_points"] = await self._find_integration_points(
                cross_repo_analysis["repositories"]
            )
            
            # Generate recommendations
            cross_repo_analysis["recommendations"] = await self._generate_cross_repo_recommendations(
                cross_repo_analysis
            )
            
            return cross_repo_analysis
            
        except Exception as e:
            return {
                "error": f"Cross-repository dependency analysis failed: {str(e)}",
                "repository_ids": repository_ids,
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    async def analyze_dependency_impact(self, element_id: str) -> Dict[str, Any]:
        """Analyze the impact of changes to a specific code element"""
        try:
            # Get the element
            element = await self.repository_service.indexing_service.get_element_by_id(element_id)
            if not element:
                raise ValueError(f"Element {element_id} not found")
            
            repository = await self.repository_service.get_repository_metadata(element["repository_id"])
            dependency_graph = await self.dependency_analyzer.build_dependency_graph(repository)
            
            impact_analysis = {
                "element_id": element_id,
                "element_name": element.get("name", ""),
                "element_type": element.get("element_type", ""),
                "analysis_timestamp": datetime.now().isoformat(),
                "direct_dependents": [],
                "indirect_dependents": [],
                "dependency_chain": [],
                "impact_scope": {},
                "risk_assessment": {},
                "change_recommendations": []
            }
            
            # Find direct dependents
            impact_analysis["direct_dependents"] = await self._find_direct_dependents(
                element, dependency_graph
            )
            
            # Find indirect dependents (transitive dependencies)
            impact_analysis["indirect_dependents"] = await self._find_indirect_dependents(
                element, dependency_graph
            )
            
            # Build dependency chain
            impact_analysis["dependency_chain"] = await self._build_dependency_chain(
                element, dependency_graph
            )
            
            # Calculate impact scope
            impact_analysis["impact_scope"] = await self._calculate_impact_scope(
                impact_analysis["direct_dependents"],
                impact_analysis["indirect_dependents"]
            )
            
            # Assess risk
            impact_analysis["risk_assessment"] = await self._assess_change_risk(
                element, impact_analysis
            )
            
            # Generate change recommendations
            impact_analysis["change_recommendations"] = await self._generate_change_recommendations(
                element, impact_analysis
            )
            
            return impact_analysis
            
        except Exception as e:
            return {
                "error": f"Dependency impact analysis failed: {str(e)}",
                "element_id": element_id,
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    async def analyze_dependency_health(self, repository_id: str) -> Dict[str, Any]:
        """Analyze overall dependency health of a repository"""
        try:
            repository = await self.repository_service.get_repository_metadata(repository_id)
            dependency_graph = await self.dependency_analyzer.build_dependency_graph(repository)
            
            health_analysis = {
                "repository_id": repository_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "overall_health_score": 0.0,
                "health_metrics": {},
                "issues": [],
                "strengths": [],
                "recommendations": []
            }
            
            # Calculate health metrics
            health_metrics = await self._calculate_dependency_health_metrics(dependency_graph)
            health_analysis["health_metrics"] = health_metrics
            
            # Calculate overall health score
            health_analysis["overall_health_score"] = await self._calculate_overall_health_score(
                health_metrics
            )
            
            # Identify issues and strengths
            health_analysis["issues"] = await self._identify_dependency_issues(health_metrics)
            health_analysis["strengths"] = await self._identify_dependency_strengths(health_metrics)
            
            # Generate recommendations
            health_analysis["recommendations"] = await self._generate_health_recommendations(
                health_metrics, health_analysis["issues"]
            )
            
            return health_analysis
            
        except Exception as e:
            return {
                "error": f"Dependency health analysis failed: {str(e)}",
                "repository_id": repository_id,
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    async def find_dependency_patterns(self, repository_id: str) -> Dict[str, Any]:
        """Find common dependency patterns in the repository"""
        try:
            repository = await self.repository_service.get_repository_metadata(repository_id)
            elements = await self.repository_service.indexing_service.get_repository_elements(repository_id)
            
            pattern_analysis = {
                "repository_id": repository_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "patterns": {},
                "anti_patterns": {},
                "architectural_insights": {},
                "pattern_recommendations": []
            }
            
            # Analyze dependency patterns
            pattern_analysis["patterns"] = await self._analyze_dependency_patterns(elements)
            
            # Identify anti-patterns
            pattern_analysis["anti_patterns"] = await self._identify_dependency_anti_patterns(elements)
            
            # Extract architectural insights
            pattern_analysis["architectural_insights"] = await self._extract_architectural_insights(
                elements, pattern_analysis["patterns"]
            )
            
            # Generate pattern recommendations
            pattern_analysis["pattern_recommendations"] = await self._generate_pattern_recommendations(
                pattern_analysis
            )
            
            return pattern_analysis
            
        except Exception as e:
            return {
                "error": f"Dependency pattern analysis failed: {str(e)}",
                "repository_id": repository_id,
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_single_repository_dependencies(self, repository: Repository) -> Dict[str, Any]:
        """Analyze dependencies for a single repository"""
        try:
            dependency_graph = await self.dependency_analyzer.build_dependency_graph(repository)
            elements = await self.repository_service.indexing_service.get_repository_elements(repository.id)
            
            analysis = {
                "repository_name": repository.name,
                "total_dependencies": len(dependency_graph.dependencies),
                "internal_dependencies": 0,
                "external_dependencies": 0,
                "dependency_types": {},
                "most_depended_upon": [],
                "least_depended_upon": [],
                "orphaned_elements": []
            }
            
            # Categorize dependencies
            for dep in dependency_graph.edges:
                # Assume internal if both elements are in the same repository
                is_internal = True  # Simplified logic
                if is_internal:
                    analysis["internal_dependencies"] += 1
                else:
                    analysis["external_dependencies"] += 1
                
                dep_type = dep.dependency_type
                analysis["dependency_types"][dep_type] = analysis["dependency_types"].get(dep_type, 0) + 1
            
            # Find most/least depended upon elements
            dependency_counts = defaultdict(int)
            for dep in dependency_graph.edges:
                dependency_counts[dep.to_element] += 1
            
            sorted_deps = sorted(dependency_counts.items(), key=lambda x: x[1], reverse=True)
            analysis["most_depended_upon"] = sorted_deps[:10]
            analysis["least_depended_upon"] = sorted_deps[-10:]
            
            # Find orphaned elements (no dependencies)
            all_elements = {elem.get("id", "") for elem in elements}
            dependent_elements = {dep.to_element for dep in dependency_graph.edges}
            analysis["orphaned_elements"] = list(all_elements - dependent_elements)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Single repository analysis failed: {str(e)}"}
    
    async def _find_cross_repository_dependencies(self, repositories: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Find dependencies that cross repository boundaries"""
        cross_dependencies = []
        
        try:
            # Compare each repository pair
            repo_ids = list(repositories.keys())
            for i, repo1_id in enumerate(repo_ids):
                for repo2_id in repo_ids[i+1:]:
                    repo1_data = repositories.get(repo1_id, {})
                    repo2_data = repositories.get(repo2_id, {})
                    
                    if "error" in repo1_data or "error" in repo2_data:
                        continue
                    
                    # Look for potential cross-dependencies
                    # This is a simplified heuristic - in practice, you'd need more sophisticated analysis
                    repo1_name = repo1_data.get("repository_name", "")
                    repo2_name = repo2_data.get("repository_name", "")
                    
                    if repo1_name and repo2_name:
                        cross_dependencies.append({
                            "source_repository": repo1_id,
                            "target_repository": repo2_id,
                            "relationship_type": "potential_integration",
                            "confidence": 0.5
                        })
            
            return cross_dependencies
            
        except Exception as e:
            return [{"error": f"Cross-dependency analysis failed: {str(e)}"}]
    
    async def _identify_shared_dependencies(self, repositories: Dict[str, Dict]) -> Dict[str, Any]:
        """Identify dependencies shared across repositories"""
        shared_deps = defaultdict(list)
        
        try:
            for repo_id, repo_data in repositories.items():
                if "error" in repo_data:
                    continue
                
                dependency_types = repo_data.get("dependency_types", {})
                for dep_type, count in dependency_types.items():
                    shared_deps[dep_type].append({
                        "repository_id": repo_id,
                        "count": count
                    })
            
            # Filter to only truly shared dependencies
            truly_shared = {}
            for dep_type, repo_list in shared_deps.items():
                if len(repo_list) > 1:
                    truly_shared[dep_type] = repo_list
            
            return truly_shared
            
        except Exception as e:
            return {"error": f"Shared dependency analysis failed: {str(e)}"}
    
    async def _detect_dependency_conflicts(self, repositories: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Detect potential dependency conflicts between repositories"""
        conflicts = []
        
        try:
            # This is a simplified conflict detection
            # In practice, you'd analyze version conflicts, incompatible dependencies, etc.
            
            repo_ids = list(repositories.keys())
            for i, repo1_id in enumerate(repo_ids):
                for repo2_id in repo_ids[i+1:]:
                    repo1_data = repositories.get(repo1_id, {})
                    repo2_data = repositories.get(repo2_id, {})
                    
                    if "error" in repo1_data or "error" in repo2_data:
                        continue
                    
                    # Check for conflicting dependency patterns
                    repo1_types = set(repo1_data.get("dependency_types", {}).keys())
                    repo2_types = set(repo2_data.get("dependency_types", {}).keys())
                    
                    common_types = repo1_types & repo2_types
                    if len(common_types) > 3:  # Arbitrary threshold
                        conflicts.append({
                            "repository_1": repo1_id,
                            "repository_2": repo2_id,
                            "conflict_type": "overlapping_dependencies",
                            "common_dependencies": list(common_types),
                            "severity": "medium"
                        })
            
            return conflicts
            
        except Exception as e:
            return [{"error": f"Conflict detection failed: {str(e)}"}]
    
    async def _find_integration_points(self, repositories: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Find potential integration points between repositories"""
        integration_points = []
        
        try:
            # Look for repositories with complementary functionality
            repo_ids = list(repositories.keys())
            
            for i, repo1_id in enumerate(repo_ids):
                for repo2_id in repo_ids[i+1:]:
                    repo1_data = repositories.get(repo1_id, {})
                    repo2_data = repositories.get(repo2_id, {})
                    
                    if "error" in repo1_data or "error" in repo2_data:
                        continue
                    
                    # Simple heuristic for integration potential
                    repo1_external = repo1_data.get("external_dependencies", 0)
                    repo2_external = repo2_data.get("external_dependencies", 0)
                    
                    if repo1_external > 0 and repo2_external > 0:
                        integration_points.append({
                            "repository_1": repo1_id,
                            "repository_2": repo2_id,
                            "integration_type": "api_integration",
                            "potential": "medium",
                            "reason": "Both repositories have external dependencies"
                        })
            
            return integration_points
            
        except Exception as e:
            return [{"error": f"Integration point analysis failed: {str(e)}"}]
    
    async def _generate_cross_repo_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for cross-repository management"""
        recommendations = []
        
        try:
            # Recommendation based on conflicts
            conflicts = analysis.get("dependency_conflicts", [])
            if conflicts:
                recommendations.append({
                    "type": "conflict_resolution",
                    "priority": "high",
                    "title": "Resolve Dependency Conflicts",
                    "description": f"Found {len(conflicts)} potential dependency conflicts",
                    "action": "Review and resolve conflicting dependencies between repositories"
                })
            
            # Recommendation based on shared dependencies
            shared_deps = analysis.get("shared_dependencies", {})
            if len(shared_deps) > 5:
                recommendations.append({
                    "type": "consolidation",
                    "priority": "medium",
                    "title": "Consider Dependency Consolidation",
                    "description": f"Found {len(shared_deps)} shared dependency types",
                    "action": "Consider creating shared libraries or consolidating common dependencies"
                })
            
            # Recommendation based on integration points
            integration_points = analysis.get("integration_points", [])
            if integration_points:
                recommendations.append({
                    "type": "integration",
                    "priority": "low",
                    "title": "Explore Integration Opportunities",
                    "description": f"Found {len(integration_points)} potential integration points",
                    "action": "Evaluate opportunities for repository integration or API sharing"
                })
            
            return recommendations
            
        except Exception as e:
            return [{"type": "error", "description": f"Failed to generate recommendations: {str(e)}"}]
    
    async def _find_direct_dependents(self, element: Dict, dependency_graph: DependencyGraph) -> List[Dict[str, Any]]:
        """Find elements that directly depend on the given element"""
        direct_dependents = []
        element_id = element.get("id", "")
        
        for dep in dependency_graph.edges:
            if dep.to_element == element_id:
                direct_dependents.append({
                    "element_id": dep.from_element,
                    "dependency_type": dep.dependency_type,
                    "is_internal": True  # Simplified logic
                })
        
        return direct_dependents
    
    async def _find_indirect_dependents(self, element: Dict, dependency_graph: DependencyGraph) -> List[Dict[str, Any]]:
        """Find elements that indirectly depend on the given element"""
        indirect_dependents = []
        element_id = element.get("id", "")
        
        # Build adjacency list for traversal
        dependents = defaultdict(list)
        for dep in dependency_graph.edges:
            dependents[dep.to_element].append(dep.from_element)
        
        # BFS to find all indirect dependents
        visited = set()
        queue = deque([element_id])
        visited.add(element_id)
        
        while queue:
            current = queue.popleft()
            for dependent in dependents[current]:
                if dependent not in visited:
                    visited.add(dependent)
                    queue.append(dependent)
                    if dependent != element_id:  # Exclude the original element
                        indirect_dependents.append({
                            "element_id": dependent,
                            "dependency_path_length": len(visited) - 1
                        })
        
        return indirect_dependents
    
    async def _build_dependency_chain(self, element: Dict, dependency_graph: DependencyGraph) -> List[List[str]]:
        """Build dependency chains from the element"""
        chains = []
        element_id = element.get("id", "")
        
        # Build adjacency list
        dependencies = defaultdict(list)
        for dep in dependency_graph.edges:
            dependencies[dep.from_element].append(dep.to_element)
        
        # DFS to find all dependency chains
        def dfs(current_id: str, path: List[str], visited: Set[str]):
            if current_id in visited:  # Circular dependency
                return
            
            visited.add(current_id)
            path.append(current_id)
            
            if current_id not in dependencies or not dependencies[current_id]:
                # End of chain
                chains.append(path.copy())
            else:
                for next_id in dependencies[current_id]:
                    dfs(next_id, path, visited.copy())
            
            path.pop()
        
        dfs(element_id, [], set())
        return chains[:10]  # Limit to first 10 chains
    
    async def _calculate_impact_scope(self, direct_dependents: List[Dict], indirect_dependents: List[Dict]) -> Dict[str, Any]:
        """Calculate the scope of impact for changes"""
        return {
            "direct_impact_count": len(direct_dependents),
            "indirect_impact_count": len(indirect_dependents),
            "total_impact_count": len(direct_dependents) + len(indirect_dependents),
            "impact_level": self._determine_impact_level(len(direct_dependents), len(indirect_dependents))
        }
    
    def _determine_impact_level(self, direct_count: int, indirect_count: int) -> str:
        """Determine impact level based on dependent counts"""
        total = direct_count + indirect_count
        
        if total == 0:
            return "none"
        elif total <= 5:
            return "low"
        elif total <= 15:
            return "medium"
        elif total <= 30:
            return "high"
        else:
            return "critical"
    
    async def _assess_change_risk(self, element: Dict, impact_analysis: Dict) -> Dict[str, Any]:
        """Assess the risk of changing the element"""
        impact_level = impact_analysis.get("impact_scope", {}).get("impact_level", "none")
        element_type = element.get("element_type", "")
        
        risk_factors = {
            "impact_risk": impact_level,
            "type_risk": "high" if element_type in ["interface", "base_class"] else "medium",
            "complexity_risk": "medium",  # Would need code analysis
            "test_coverage_risk": "unknown"  # Would need test analysis
        }
        
        # Calculate overall risk
        risk_scores = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        avg_risk = sum(risk_scores.get(risk, 2) for risk in risk_factors.values()) / len(risk_factors)
        
        overall_risk = "low"
        if avg_risk >= 3:
            overall_risk = "high"
        elif avg_risk >= 2:
            overall_risk = "medium"
        
        return {
            "overall_risk": overall_risk,
            "risk_factors": risk_factors,
            "risk_score": round(avg_risk, 2)
        }
    
    async def _generate_change_recommendations(self, element: Dict, impact_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate recommendations for safely changing the element"""
        recommendations = []
        
        risk_level = impact_analysis.get("risk_assessment", {}).get("overall_risk", "medium")
        impact_count = impact_analysis.get("impact_scope", {}).get("total_impact_count", 0)
        
        if risk_level == "high" or impact_count > 10:
            recommendations.append({
                "type": "testing",
                "priority": "high",
                "title": "Comprehensive Testing Required",
                "description": "High impact change requires extensive testing",
                "action": "Create comprehensive test suite covering all dependent elements"
            })
        
        if impact_count > 5:
            recommendations.append({
                "type": "communication",
                "priority": "medium",
                "title": "Coordinate with Team",
                "description": f"Change affects {impact_count} other elements",
                "action": "Notify team members and coordinate changes to dependent code"
            })
        
        recommendations.append({
            "type": "versioning",
            "priority": "medium",
            "title": "Consider Versioning Strategy",
            "description": "Implement proper versioning for breaking changes",
            "action": "Use semantic versioning and deprecation warnings where appropriate"
        })
        
        return recommendations
    
    async def _calculate_dependency_health_metrics(self, dependency_graph: DependencyGraph) -> Dict[str, Any]:
        """Calculate comprehensive dependency health metrics"""
        total_deps = len(dependency_graph.edges)
        
        if total_deps == 0:
            return {"total_dependencies": 0, "health_score": 1.0}
        
        # Count different types of dependencies (simplified - assume all internal for now)
        internal_deps = total_deps  # Simplified logic
        external_deps = 0
        
        # Find circular dependencies
        circular_deps = self.dependency_analyzer.find_circular_dependencies(dependency_graph)
        
        # Calculate coupling metrics
        coupling_metrics = self.dependency_analyzer.calculate_coupling_metrics(dependency_graph)
        
        return {
            "total_dependencies": total_deps,
            "internal_dependencies": internal_deps,
            "external_dependencies": external_deps,
            "circular_dependencies": len(circular_deps),
            "internal_ratio": internal_deps / total_deps,
            "external_ratio": external_deps / total_deps,
            "circular_ratio": len(circular_deps) / total_deps,
            "coupling_metrics": coupling_metrics
        }
    
    async def _calculate_overall_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall dependency health score"""
        score = 1.0
        
        # Penalize high circular dependency ratio
        circular_ratio = metrics.get("circular_ratio", 0)
        score -= circular_ratio * 0.5
        
        # Prefer balanced internal/external ratio
        internal_ratio = metrics.get("internal_ratio", 0.5)
        if internal_ratio < 0.3 or internal_ratio > 0.9:
            score -= 0.2
        
        # Consider coupling metrics
        coupling = metrics.get("coupling_metrics", {}).get("average_coupling", 0.5)
        if coupling > 0.7:
            score -= 0.3
        
        return max(0.0, min(1.0, score))
    
    async def _identify_dependency_issues(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify dependency-related issues"""
        issues = []
        
        if metrics.get("circular_dependencies", 0) > 0:
            issues.append({
                "type": "circular_dependencies",
                "severity": "high",
                "description": f"Found {metrics['circular_dependencies']} circular dependencies",
                "impact": "Can cause build failures and maintenance issues"
            })
        
        if metrics.get("external_ratio", 0) > 0.8:
            issues.append({
                "type": "high_external_dependencies",
                "severity": "medium",
                "description": "High ratio of external dependencies",
                "impact": "Increased risk of external changes breaking the system"
            })
        
        coupling = metrics.get("coupling_metrics", {}).get("average_coupling", 0)
        if coupling > 0.7:
            issues.append({
                "type": "high_coupling",
                "severity": "medium",
                "description": "High coupling between components",
                "impact": "Reduced modularity and increased maintenance complexity"
            })
        
        return issues
    
    async def _identify_dependency_strengths(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify dependency-related strengths"""
        strengths = []
        
        if metrics.get("circular_dependencies", 0) == 0:
            strengths.append({
                "type": "no_circular_dependencies",
                "description": "No circular dependencies detected",
                "benefit": "Clean architecture with clear dependency flow"
            })
        
        internal_ratio = metrics.get("internal_ratio", 0)
        if 0.4 <= internal_ratio <= 0.8:
            strengths.append({
                "type": "balanced_dependencies",
                "description": "Good balance of internal and external dependencies",
                "benefit": "Healthy mix of modularity and external library usage"
            })
        
        coupling = metrics.get("coupling_metrics", {}).get("average_coupling", 0)
        if coupling < 0.5:
            strengths.append({
                "type": "low_coupling",
                "description": "Low coupling between components",
                "benefit": "High modularity and maintainability"
            })
        
        return strengths
    
    async def _generate_health_recommendations(self, metrics: Dict[str, Any], issues: List[Dict]) -> List[Dict[str, Any]]:
        """Generate recommendations for improving dependency health"""
        recommendations = []
        
        for issue in issues:
            if issue["type"] == "circular_dependencies":
                recommendations.append({
                    "type": "refactoring",
                    "priority": "high",
                    "title": "Eliminate Circular Dependencies",
                    "description": "Refactor code to remove circular dependencies",
                    "action": "Use dependency inversion or extract common interfaces"
                })
            
            elif issue["type"] == "high_external_dependencies":
                recommendations.append({
                    "type": "dependency_management",
                    "priority": "medium",
                    "title": "Review External Dependencies",
                    "description": "Evaluate necessity of external dependencies",
                    "action": "Consider consolidating or replacing some external dependencies"
                })
            
            elif issue["type"] == "high_coupling":
                recommendations.append({
                    "type": "architecture",
                    "priority": "medium",
                    "title": "Reduce Component Coupling",
                    "description": "Improve modularity by reducing coupling",
                    "action": "Use interfaces, dependency injection, or event-driven patterns"
                })
        
        return recommendations
    
    async def _analyze_dependency_patterns(self, elements: List[Dict]) -> Dict[str, Any]:
        """Analyze common dependency patterns"""
        patterns = {
            "layered_architecture": 0,
            "dependency_injection": 0,
            "factory_pattern": 0,
            "observer_pattern": 0,
            "singleton_pattern": 0
        }
        
        # Simple pattern detection based on naming and structure
        for element in elements:
            name = element.get("name", "").lower()
            element_type = element.get("element_type", "")
            
            if "factory" in name:
                patterns["factory_pattern"] += 1
            elif "singleton" in name:
                patterns["singleton_pattern"] += 1
            elif "observer" in name or "listener" in name:
                patterns["observer_pattern"] += 1
            elif element_type == "interface" or "interface" in name:
                patterns["dependency_injection"] += 1
        
        return patterns
    
    async def _identify_dependency_anti_patterns(self, elements: List[Dict]) -> Dict[str, Any]:
        """Identify dependency anti-patterns"""
        anti_patterns = {
            "god_object": 0,
            "circular_dependency": 0,
            "tight_coupling": 0,
            "dependency_hell": 0
        }
        
        # Simple anti-pattern detection
        for element in elements:
            dependencies = element.get("dependencies", [])
            
            if len(dependencies) > 20:  # Arbitrary threshold
                anti_patterns["god_object"] += 1
            elif len(dependencies) > 10:
                anti_patterns["tight_coupling"] += 1
        
        return anti_patterns
    
    async def _extract_architectural_insights(self, elements: List[Dict], patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Extract architectural insights from dependency analysis"""
        insights = {
            "architecture_style": "unknown",
            "modularity_score": 0.0,
            "separation_of_concerns": 0.0,
            "architectural_recommendations": []
        }
        
        # Determine likely architecture style
        if patterns.get("layered_architecture", 0) > patterns.get("factory_pattern", 0):
            insights["architecture_style"] = "layered"
        elif patterns.get("dependency_injection", 0) > 5:
            insights["architecture_style"] = "dependency_injection"
        else:
            insights["architecture_style"] = "mixed"
        
        # Calculate modularity score based on dependency distribution
        total_elements = len(elements)
        if total_elements > 0:
            avg_dependencies = sum(len(elem.get("dependencies", [])) for elem in elements) / total_elements
            insights["modularity_score"] = max(0.0, 1.0 - (avg_dependencies / 20))  # Normalize
        
        return insights
    
    async def _generate_pattern_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on pattern analysis"""
        recommendations = []
        
        patterns = analysis.get("patterns", {})
        anti_patterns = analysis.get("anti_patterns", {})
        
        if anti_patterns.get("god_object", 0) > 0:
            recommendations.append({
                "type": "refactoring",
                "priority": "high",
                "title": "Break Down God Objects",
                "description": f"Found {anti_patterns['god_object']} potential god objects",
                "action": "Refactor large classes/modules into smaller, focused components"
            })
        
        if patterns.get("dependency_injection", 0) < 3 and len(analysis.get("patterns", {})) > 10:
            recommendations.append({
                "type": "architecture",
                "priority": "medium",
                "title": "Consider Dependency Injection",
                "description": "Low usage of dependency injection pattern",
                "action": "Implement dependency injection to improve testability and modularity"
            })
        
        return recommendations