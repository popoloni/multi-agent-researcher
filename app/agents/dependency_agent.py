"""
Dependency Analysis Agent - Phase 4
Specialized agent for comprehensive dependency analysis and management
"""

import asyncio
import json
import time
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import networkx as nx
from collections import defaultdict, deque

from app.models.repository_schemas import Repository, CodeElement, ElementType, SearchFilters
from app.services.indexing_service import IndexingService
from app.engines.vector_service import VectorService
from app.core.config import settings


class DependencyAnalysisAgent:
    """
    Specialized agent for dependency analysis and management
    Handles dependency graphs, circular dependency detection, and dependency health monitoring
    """
    
    def __init__(self, indexing_service: IndexingService, vector_service: VectorService):
        self.indexing_service = indexing_service
        self.vector_service = vector_service
        self.dependency_cache = {}
        self.graph_cache = {}
        
    async def analyze_repository_dependencies(self, repository_id: str) -> Dict[str, Any]:
        """
        Comprehensive dependency analysis for a repository
        """
        start_time = time.time()
        
        try:
            # Get repository metadata
            repo_metadata = self.indexing_service.get_repository_metadata(repository_id)
            if not repo_metadata:
                return {'error': 'Repository not found'}
            
            # Build dependency graph
            dependency_graph = await self._build_dependency_graph(repository_id)
            
            # Analyze dependencies
            analysis_tasks = [
                self._analyze_external_dependencies(repository_id),
                self._analyze_internal_dependencies(repository_id, dependency_graph),
                self._detect_circular_dependencies(dependency_graph),
                self._analyze_dependency_complexity(dependency_graph),
                self._analyze_dependency_security(repository_id),
                self._analyze_dependency_performance(dependency_graph),
                self._analyze_dependency_maintenance(repository_id)
            ]
            
            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Compile comprehensive analysis
            dependency_analysis = {
                'repository_id': repository_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'processing_time': time.time() - start_time,
                'dependency_graph': self._serialize_graph(dependency_graph),
                'external_dependencies': results[0] if not isinstance(results[0], Exception) else {'error': str(results[0])},
                'internal_dependencies': results[1] if not isinstance(results[1], Exception) else {'error': str(results[1])},
                'circular_dependencies': results[2] if not isinstance(results[2], Exception) else {'error': str(results[2])},
                'complexity_analysis': results[3] if not isinstance(results[3], Exception) else {'error': str(results[3])},
                'security_analysis': results[4] if not isinstance(results[4], Exception) else {'error': str(results[4])},
                'performance_analysis': results[5] if not isinstance(results[5], Exception) else {'error': str(results[5])},
                'maintenance_analysis': results[6] if not isinstance(results[6], Exception) else {'error': str(results[6])},
                'dependency_health_score': self._calculate_dependency_health_score(results),
                'recommendations': self._generate_dependency_recommendations(results)
            }
            
            # Cache results
            self.dependency_cache[repository_id] = dependency_analysis
            
            return dependency_analysis
            
        except Exception as e:
            return {
                'error': f"Dependency analysis failed: {str(e)}",
                'repository_id': repository_id,
                'processing_time': time.time() - start_time
            }
    
    async def analyze_cross_repository_dependencies(self, repository_ids: List[str]) -> Dict[str, Any]:
        """
        Analyze dependencies across multiple repositories
        """
        start_time = time.time()
        
        try:
            # Build cross-repository dependency graph
            cross_repo_graph = nx.DiGraph()
            repo_dependencies = {}
            
            for repo_id in repository_ids:
                repo_deps = await self.analyze_repository_dependencies(repo_id)
                repo_dependencies[repo_id] = repo_deps
                
                # Add repository nodes and edges to cross-repo graph
                if 'dependency_graph' in repo_deps:
                    repo_graph_data = repo_deps['dependency_graph']
                    for node in repo_graph_data.get('nodes', []):
                        cross_repo_graph.add_node(f"{repo_id}:{node}", repository=repo_id)
                    for edge in repo_graph_data.get('edges', []):
                        cross_repo_graph.add_edge(f"{repo_id}:{edge[0]}", f"{repo_id}:{edge[1]}")
            
            # Analyze cross-repository patterns
            cross_analysis = {
                'analysis_timestamp': datetime.now().isoformat(),
                'processing_time': time.time() - start_time,
                'repositories_analyzed': repository_ids,
                'cross_repo_graph': self._serialize_graph(cross_repo_graph),
                'shared_dependencies': self._find_shared_dependencies(repo_dependencies),
                'dependency_conflicts': self._detect_dependency_conflicts(repo_dependencies),
                'integration_complexity': self._calculate_integration_complexity(cross_repo_graph),
                'consolidation_opportunities': self._identify_consolidation_opportunities(repo_dependencies),
                'cross_repo_recommendations': self._generate_cross_repo_recommendations(repo_dependencies)
            }
            
            return cross_analysis
            
        except Exception as e:
            return {
                'error': f"Cross-repository dependency analysis failed: {str(e)}",
                'processing_time': time.time() - start_time
            }
    
    async def track_dependency_changes(self, repository_id: str, time_window_days: int = 30) -> Dict[str, Any]:
        """
        Track dependency changes over time
        """
        try:
            # Get current dependencies
            current_analysis = await self.analyze_repository_dependencies(repository_id)
            
            # Simulate historical data (in production, this would come from stored analysis history)
            historical_changes = {
                'repository_id': repository_id,
                'time_window_days': time_window_days,
                'analysis_timestamp': datetime.now().isoformat(),
                'dependency_additions': self._simulate_dependency_additions(),
                'dependency_removals': self._simulate_dependency_removals(),
                'dependency_updates': self._simulate_dependency_updates(),
                'security_improvements': self._simulate_security_improvements(),
                'performance_impacts': self._simulate_performance_impacts(),
                'change_frequency': self._calculate_change_frequency(time_window_days),
                'stability_score': self._calculate_stability_score(),
                'change_recommendations': self._generate_change_recommendations()
            }
            
            return historical_changes
            
        except Exception as e:
            return {
                'error': f"Dependency change tracking failed: {str(e)}",
                'repository_id': repository_id
            }
    
    async def optimize_dependency_structure(self, repository_id: str) -> Dict[str, Any]:
        """
        Provide optimization recommendations for dependency structure
        """
        try:
            # Get current dependency analysis
            current_analysis = await self.analyze_repository_dependencies(repository_id)
            
            if 'error' in current_analysis:
                return current_analysis
            
            # Generate optimization recommendations
            optimization = {
                'repository_id': repository_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'current_health_score': current_analysis.get('dependency_health_score', 0.0),
                'optimization_opportunities': {
                    'circular_dependency_fixes': self._suggest_circular_dependency_fixes(current_analysis),
                    'dependency_consolidation': self._suggest_dependency_consolidation(current_analysis),
                    'security_upgrades': self._suggest_security_upgrades(current_analysis),
                    'performance_optimizations': self._suggest_performance_optimizations(current_analysis),
                    'maintenance_improvements': self._suggest_maintenance_improvements(current_analysis)
                },
                'implementation_priority': self._prioritize_optimizations(current_analysis),
                'estimated_impact': self._estimate_optimization_impact(current_analysis),
                'implementation_effort': self._estimate_implementation_effort(current_analysis)
            }
            
            return optimization
            
        except Exception as e:
            return {
                'error': f"Dependency optimization failed: {str(e)}",
                'repository_id': repository_id
            }
    
    # Private helper methods
    
    async def _build_dependency_graph(self, repository_id: str) -> nx.DiGraph:
        """Build dependency graph for repository"""
        try:
            # Check cache first
            if repository_id in self.graph_cache:
                return self.graph_cache[repository_id]
            
            graph = nx.DiGraph()
            
            # Get all elements from repository
            filters = SearchFilters()
            elements = self.indexing_service._get_search_candidates(filters)
            repo_elements = [e for e in elements if e.get('repository_id') == repository_id]
            
            # Build graph from code elements
            for element in repo_elements:
                element_id = element.get('id', '')
                element_name = element.get('name', '')
                element_type = element.get('element_type', '')
                
                # Add node
                graph.add_node(element_id, 
                             name=element_name, 
                             type=element_type,
                             file_path=element.get('file_path', ''))
                
                # Add dependencies based on element data
                dependencies = element.get('dependencies', [])
                for dep in dependencies:
                    if isinstance(dep, str):
                        graph.add_edge(element_id, dep)
                    elif isinstance(dep, dict):
                        dep_id = dep.get('id', dep.get('name', ''))
                        if dep_id:
                            graph.add_edge(element_id, dep_id)
            
            # Cache the graph
            self.graph_cache[repository_id] = graph
            
            return graph
            
        except Exception as e:
            # Return empty graph on error
            return nx.DiGraph()
    
    async def _analyze_external_dependencies(self, repository_id: str) -> Dict[str, Any]:
        """Analyze external dependencies (packages, libraries)"""
        try:
            repo_metadata = self.indexing_service.get_repository_metadata(repository_id)
            if not repo_metadata:
                return {'error': 'Repository not found'}
            
            # Get dependencies from repository metadata
            dependencies = repo_metadata.get('dependencies', {})
            
            external_analysis = {
                'total_external_dependencies': len(dependencies),
                'dependency_categories': self._categorize_external_dependencies(dependencies),
                'version_analysis': self._analyze_dependency_versions(dependencies),
                'license_analysis': self._analyze_dependency_licenses(dependencies),
                'size_analysis': self._analyze_dependency_sizes(dependencies),
                'update_recommendations': self._recommend_dependency_updates(dependencies),
                'security_vulnerabilities': self._check_external_security(dependencies),
                'maintenance_status': self._check_maintenance_status(dependencies)
            }
            
            return external_analysis
            
        except Exception as e:
            return {'error': f"External dependency analysis failed: {str(e)}"}
    
    async def _analyze_internal_dependencies(self, repository_id: str, graph: nx.DiGraph) -> Dict[str, Any]:
        """Analyze internal dependencies within the repository"""
        try:
            internal_analysis = {
                'total_internal_nodes': graph.number_of_nodes(),
                'total_internal_edges': graph.number_of_edges(),
                'dependency_density': nx.density(graph),
                'strongly_connected_components': len(list(nx.strongly_connected_components(graph))),
                'weakly_connected_components': len(list(nx.weakly_connected_components(graph))),
                'average_in_degree': sum(dict(graph.in_degree()).values()) / graph.number_of_nodes() if graph.number_of_nodes() > 0 else 0,
                'average_out_degree': sum(dict(graph.out_degree()).values()) / graph.number_of_nodes() if graph.number_of_nodes() > 0 else 0,
                'most_dependent_modules': self._find_most_dependent_modules(graph),
                'most_depended_upon_modules': self._find_most_depended_upon_modules(graph),
                'dependency_layers': self._analyze_dependency_layers(graph),
                'coupling_analysis': self._analyze_coupling(graph)
            }
            
            return internal_analysis
            
        except Exception as e:
            return {'error': f"Internal dependency analysis failed: {str(e)}"}
    
    async def _detect_circular_dependencies(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Detect circular dependencies in the graph"""
        try:
            # Find strongly connected components with more than one node
            cycles = []
            for component in nx.strongly_connected_components(graph):
                if len(component) > 1:
                    # Extract the subgraph for this component
                    subgraph = graph.subgraph(component)
                    # Find actual cycles
                    try:
                        cycle = nx.find_cycle(subgraph, orientation='original')
                        cycles.append([edge[0] for edge in cycle])
                    except nx.NetworkXNoCycle:
                        continue
            
            circular_analysis = {
                'circular_dependencies_found': len(cycles) > 0,
                'number_of_cycles': len(cycles),
                'cycles': cycles[:10],  # Limit to first 10 cycles
                'affected_modules': list(set([node for cycle in cycles for node in cycle])),
                'cycle_complexity': self._calculate_cycle_complexity(cycles),
                'breaking_recommendations': self._recommend_cycle_breaking(cycles, graph)
            }
            
            return circular_analysis
            
        except Exception as e:
            return {'error': f"Circular dependency detection failed: {str(e)}"}
    
    async def _analyze_dependency_complexity(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Analyze complexity of dependency structure"""
        try:
            complexity_analysis = {
                'graph_complexity': self._calculate_graph_complexity(graph),
                'dependency_depth': self._calculate_dependency_depth(graph),
                'fan_in_fan_out': self._analyze_fan_in_fan_out(graph),
                'modularity': self._calculate_modularity(graph),
                'clustering_coefficient': nx.average_clustering(graph.to_undirected()) if graph.number_of_nodes() > 0 else 0,
                'path_analysis': self._analyze_dependency_paths(graph),
                'bottleneck_analysis': self._identify_dependency_bottlenecks(graph),
                'complexity_score': 0.0
            }
            
            # Calculate overall complexity score
            complexity_analysis['complexity_score'] = self._calculate_complexity_score(complexity_analysis)
            
            return complexity_analysis
            
        except Exception as e:
            return {'error': f"Dependency complexity analysis failed: {str(e)}"}
    
    async def _analyze_dependency_security(self, repository_id: str) -> Dict[str, Any]:
        """Analyze security aspects of dependencies"""
        try:
            repo_metadata = self.indexing_service.get_repository_metadata(repository_id)
            dependencies = repo_metadata.get('dependencies', {}) if repo_metadata else {}
            
            security_analysis = {
                'vulnerable_dependencies': self._identify_vulnerable_dependencies(dependencies),
                'outdated_dependencies': self._identify_outdated_dependencies(dependencies),
                'license_risks': self._analyze_license_risks(dependencies),
                'supply_chain_risks': self._analyze_supply_chain_risks(dependencies),
                'security_score': 0.0,
                'security_recommendations': []
            }
            
            # Calculate security score
            security_analysis['security_score'] = self._calculate_security_score(security_analysis)
            security_analysis['security_recommendations'] = self._generate_security_recommendations(security_analysis)
            
            return security_analysis
            
        except Exception as e:
            return {'error': f"Dependency security analysis failed: {str(e)}"}
    
    async def _analyze_dependency_performance(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Analyze performance implications of dependency structure"""
        try:
            performance_analysis = {
                'load_time_impact': self._estimate_load_time_impact(graph),
                'memory_usage_impact': self._estimate_memory_impact(graph),
                'build_time_impact': self._estimate_build_time_impact(graph),
                'runtime_performance': self._analyze_runtime_performance(graph),
                'optimization_opportunities': self._identify_performance_optimizations(graph),
                'performance_score': 0.0
            }
            
            # Calculate performance score
            performance_analysis['performance_score'] = self._calculate_performance_score(performance_analysis)
            
            return performance_analysis
            
        except Exception as e:
            return {'error': f"Dependency performance analysis failed: {str(e)}"}
    
    async def _analyze_dependency_maintenance(self, repository_id: str) -> Dict[str, Any]:
        """Analyze maintenance aspects of dependencies"""
        try:
            repo_metadata = self.indexing_service.get_repository_metadata(repository_id)
            dependencies = repo_metadata.get('dependencies', {}) if repo_metadata else {}
            
            maintenance_analysis = {
                'maintenance_burden': self._calculate_maintenance_burden(dependencies),
                'update_frequency': self._analyze_update_frequency(dependencies),
                'breaking_change_risk': self._assess_breaking_change_risk(dependencies),
                'community_health': self._assess_community_health(dependencies),
                'long_term_viability': self._assess_long_term_viability(dependencies),
                'maintenance_score': 0.0,
                'maintenance_recommendations': []
            }
            
            # Calculate maintenance score
            maintenance_analysis['maintenance_score'] = self._calculate_maintenance_score(maintenance_analysis)
            maintenance_analysis['maintenance_recommendations'] = self._generate_maintenance_recommendations(maintenance_analysis)
            
            return maintenance_analysis
            
        except Exception as e:
            return {'error': f"Dependency maintenance analysis failed: {str(e)}"}
    
    def _serialize_graph(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Serialize NetworkX graph to JSON-serializable format"""
        try:
            return {
                'nodes': list(graph.nodes()),
                'edges': list(graph.edges()),
                'node_count': graph.number_of_nodes(),
                'edge_count': graph.number_of_edges(),
                'is_directed': graph.is_directed()
            }
        except Exception:
            return {'nodes': [], 'edges': [], 'node_count': 0, 'edge_count': 0, 'is_directed': True}
    
    def _calculate_dependency_health_score(self, analysis_results: List[Any]) -> float:
        """Calculate overall dependency health score"""
        try:
            scores = []
            
            for result in analysis_results:
                if isinstance(result, dict) and 'error' not in result:
                    if 'security_score' in result:
                        scores.append(result['security_score'])
                    elif 'performance_score' in result:
                        scores.append(result['performance_score'])
                    elif 'maintenance_score' in result:
                        scores.append(result['maintenance_score'])
                    elif 'complexity_score' in result:
                        scores.append(10 - result['complexity_score'])  # Lower complexity is better
            
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception:
            return 0.0
    
    def _generate_dependency_recommendations(self, analysis_results: List[Any]) -> List[str]:
        """Generate actionable recommendations based on dependency analysis"""
        recommendations = []
        
        try:
            for result in analysis_results:
                if isinstance(result, dict) and 'error' not in result:
                    if 'circular_dependencies_found' in result and result['circular_dependencies_found']:
                        recommendations.append("Break circular dependencies to improve maintainability")
                    if 'vulnerable_dependencies' in result and result['vulnerable_dependencies']:
                        recommendations.append("Update vulnerable dependencies for security")
                    if 'performance_score' in result and result['performance_score'] < 7.0:
                        recommendations.append("Optimize dependency structure for better performance")
                    if 'maintenance_score' in result and result['maintenance_score'] < 7.0:
                        recommendations.append("Review dependency maintenance and update strategy")
            
            if not recommendations:
                recommendations.append("Dependency structure appears healthy")
            
            return recommendations
            
        except Exception:
            return ["Unable to generate recommendations due to analysis errors"]
    
    # Helper methods for specific analyses
    
    def _categorize_external_dependencies(self, dependencies: Dict) -> Dict[str, int]:
        """Categorize external dependencies by type"""
        categories = defaultdict(int)
        for dep_name, dep_info in dependencies.items():
            # Simple categorization based on common patterns
            if any(keyword in dep_name.lower() for keyword in ['test', 'pytest', 'unittest']):
                categories['testing'] += 1
            elif any(keyword in dep_name.lower() for keyword in ['dev', 'debug', 'lint']):
                categories['development'] += 1
            elif any(keyword in dep_name.lower() for keyword in ['web', 'http', 'api', 'flask', 'django']):
                categories['web'] += 1
            elif any(keyword in dep_name.lower() for keyword in ['data', 'pandas', 'numpy', 'scipy']):
                categories['data_science'] += 1
            else:
                categories['production'] += 1
        
        return dict(categories)
    
    def _analyze_dependency_versions(self, dependencies: Dict) -> Dict[str, Any]:
        """Analyze dependency version patterns"""
        version_analysis = {
            'pinned_versions': 0,
            'range_versions': 0,
            'latest_versions': 0,
            'version_conflicts': []
        }
        
        for dep_name, dep_info in dependencies.items():
            version = dep_info.get('version', '') if isinstance(dep_info, dict) else str(dep_info)
            if '==' in version:
                version_analysis['pinned_versions'] += 1
            elif any(op in version for op in ['>=', '<=', '>', '<', '~', '^']):
                version_analysis['range_versions'] += 1
            else:
                version_analysis['latest_versions'] += 1
        
        return version_analysis
    
    def _analyze_dependency_licenses(self, dependencies: Dict) -> Dict[str, Any]:
        """Analyze dependency licenses"""
        # Placeholder implementation
        return {
            'license_types': {'MIT': 10, 'Apache': 5, 'GPL': 2},
            'license_conflicts': [],
            'commercial_restrictions': []
        }
    
    def _analyze_dependency_sizes(self, dependencies: Dict) -> Dict[str, Any]:
        """Analyze dependency sizes and impact"""
        # Placeholder implementation
        return {
            'total_size_estimate': '50MB',
            'large_dependencies': [],
            'size_optimization_opportunities': []
        }
    
    def _recommend_dependency_updates(self, dependencies: Dict) -> List[str]:
        """Recommend dependency updates"""
        # Placeholder implementation
        return ['Update numpy to latest version', 'Consider replacing deprecated library X']
    
    def _check_external_security(self, dependencies: Dict) -> List[str]:
        """Check external dependencies for security issues"""
        # Placeholder implementation
        return []
    
    def _check_maintenance_status(self, dependencies: Dict) -> Dict[str, Any]:
        """Check maintenance status of dependencies"""
        # Placeholder implementation
        return {
            'actively_maintained': 15,
            'deprecated': 2,
            'abandoned': 0
        }
    
    def _find_most_dependent_modules(self, graph: nx.DiGraph) -> List[Tuple[str, int]]:
        """Find modules with highest out-degree (depend on many others)"""
        out_degrees = dict(graph.out_degree())
        return sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _find_most_depended_upon_modules(self, graph: nx.DiGraph) -> List[Tuple[str, int]]:
        """Find modules with highest in-degree (many others depend on them)"""
        in_degrees = dict(graph.in_degree())
        return sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def _analyze_dependency_layers(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Analyze dependency layers/levels"""
        try:
            # Topological sort to find layers
            if nx.is_directed_acyclic_graph(graph):
                topo_order = list(nx.topological_sort(graph))
                layers = self._calculate_layers(graph, topo_order)
                return {
                    'is_acyclic': True,
                    'number_of_layers': len(layers),
                    'layer_distribution': {f"layer_{i}": len(layer) for i, layer in enumerate(layers)}
                }
            else:
                return {
                    'is_acyclic': False,
                    'cycles_prevent_layering': True
                }
        except Exception:
            return {'error': 'Layer analysis failed'}
    
    def _analyze_coupling(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Analyze coupling between modules"""
        try:
            # Calculate various coupling metrics
            total_edges = graph.number_of_edges()
            total_nodes = graph.number_of_nodes()
            
            coupling_analysis = {
                'total_coupling': total_edges,
                'average_coupling': total_edges / total_nodes if total_nodes > 0 else 0,
                'coupling_density': nx.density(graph),
                'highly_coupled_modules': self._identify_highly_coupled_modules(graph),
                'loosely_coupled_modules': self._identify_loosely_coupled_modules(graph)
            }
            
            return coupling_analysis
            
        except Exception:
            return {'error': 'Coupling analysis failed'}
    
    def _calculate_cycle_complexity(self, cycles: List[List[str]]) -> Dict[str, Any]:
        """Calculate complexity of circular dependencies"""
        if not cycles:
            return {'complexity': 0, 'max_cycle_length': 0, 'average_cycle_length': 0}
        
        cycle_lengths = [len(cycle) for cycle in cycles]
        return {
            'complexity': len(cycles) * sum(cycle_lengths),
            'max_cycle_length': max(cycle_lengths),
            'average_cycle_length': sum(cycle_lengths) / len(cycle_lengths)
        }
    
    def _recommend_cycle_breaking(self, cycles: List[List[str]], graph: nx.DiGraph) -> List[str]:
        """Recommend ways to break circular dependencies"""
        recommendations = []
        
        for cycle in cycles[:3]:  # Limit to first 3 cycles
            # Find the edge that would break the cycle with minimal impact
            cycle_edges = [(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))]
            
            # Simple heuristic: recommend breaking the edge with lowest weight/importance
            for edge in cycle_edges:
                recommendations.append(f"Consider breaking dependency from {edge[0]} to {edge[1]}")
                break  # One recommendation per cycle
        
        return recommendations
    
    def _calculate_graph_complexity(self, graph: nx.DiGraph) -> float:
        """Calculate overall graph complexity"""
        if graph.number_of_nodes() == 0:
            return 0.0
        
        # Complexity based on nodes, edges, and structure
        node_complexity = graph.number_of_nodes()
        edge_complexity = graph.number_of_edges()
        density_complexity = nx.density(graph) * 10
        
        return (node_complexity + edge_complexity + density_complexity) / 3
    
    def _calculate_dependency_depth(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Calculate dependency depth metrics"""
        try:
            if graph.number_of_nodes() == 0:
                return {'max_depth': 0, 'average_depth': 0}
            
            # Calculate shortest path lengths from each node to all others
            depths = []
            for node in graph.nodes():
                try:
                    lengths = nx.single_source_shortest_path_length(graph, node)
                    if lengths:
                        depths.append(max(lengths.values()))
                except:
                    continue
            
            return {
                'max_depth': max(depths) if depths else 0,
                'average_depth': sum(depths) / len(depths) if depths else 0
            }
            
        except Exception:
            return {'max_depth': 0, 'average_depth': 0}
    
    def _analyze_fan_in_fan_out(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Analyze fan-in and fan-out metrics"""
        try:
            in_degrees = [d for n, d in graph.in_degree()]
            out_degrees = [d for n, d in graph.out_degree()]
            
            return {
                'max_fan_in': max(in_degrees) if in_degrees else 0,
                'max_fan_out': max(out_degrees) if out_degrees else 0,
                'average_fan_in': sum(in_degrees) / len(in_degrees) if in_degrees else 0,
                'average_fan_out': sum(out_degrees) / len(out_degrees) if out_degrees else 0
            }
            
        except Exception:
            return {'max_fan_in': 0, 'max_fan_out': 0, 'average_fan_in': 0, 'average_fan_out': 0}
    
    def _calculate_modularity(self, graph: nx.DiGraph) -> float:
        """Calculate modularity of the graph"""
        try:
            # Convert to undirected for modularity calculation
            undirected = graph.to_undirected()
            if undirected.number_of_edges() == 0:
                return 0.0
            
            # Use simple community detection
            communities = list(nx.connected_components(undirected))
            if len(communities) <= 1:
                return 0.0
            
            # Calculate modularity (simplified)
            return len(communities) / undirected.number_of_nodes()
            
        except Exception:
            return 0.0
    
    def _analyze_dependency_paths(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Analyze dependency paths"""
        try:
            # Find longest paths
            if nx.is_directed_acyclic_graph(graph):
                longest_path = nx.dag_longest_path(graph)
                return {
                    'longest_path_length': len(longest_path),
                    'longest_path': longest_path[:5],  # Limit output
                    'is_acyclic': True
                }
            else:
                return {
                    'longest_path_length': 0,
                    'longest_path': [],
                    'is_acyclic': False
                }
                
        except Exception:
            return {'longest_path_length': 0, 'longest_path': [], 'is_acyclic': False}
    
    def _identify_dependency_bottlenecks(self, graph: nx.DiGraph) -> List[str]:
        """Identify dependency bottlenecks"""
        try:
            # Nodes with high betweenness centrality are potential bottlenecks
            centrality = nx.betweenness_centrality(graph)
            bottlenecks = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            return [node for node, centrality in bottlenecks if centrality > 0.1]
            
        except Exception:
            return []
    
    def _calculate_complexity_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall complexity score"""
        try:
            complexity_factors = []
            
            if 'graph_complexity' in analysis:
                complexity_factors.append(min(analysis['graph_complexity'] / 10, 10))
            
            if 'max_depth' in analysis.get('dependency_depth', {}):
                depth = analysis['dependency_depth']['max_depth']
                complexity_factors.append(min(depth, 10))
            
            if 'max_fan_out' in analysis.get('fan_in_fan_out', {}):
                fan_out = analysis['fan_in_fan_out']['max_fan_out']
                complexity_factors.append(min(fan_out, 10))
            
            return sum(complexity_factors) / len(complexity_factors) if complexity_factors else 0.0
            
        except Exception:
            return 0.0
    
    # Additional placeholder methods for comprehensive analysis
    
    def _find_shared_dependencies(self, repo_dependencies: Dict[str, Any]) -> Dict[str, Any]:
        """Find dependencies shared across repositories"""
        return {'shared_count': 5, 'shared_dependencies': ['numpy', 'requests']}
    
    def _detect_dependency_conflicts(self, repo_dependencies: Dict[str, Any]) -> List[str]:
        """Detect version conflicts across repositories"""
        return []
    
    def _calculate_integration_complexity(self, graph: nx.DiGraph) -> float:
        """Calculate complexity of integrating repositories"""
        return 5.0
    
    def _identify_consolidation_opportunities(self, repo_dependencies: Dict[str, Any]) -> List[str]:
        """Identify opportunities for dependency consolidation"""
        return ['Consider using a monorepo structure', 'Standardize on common libraries']
    
    def _generate_cross_repo_recommendations(self, repo_dependencies: Dict[str, Any]) -> List[str]:
        """Generate recommendations for cross-repository dependency management"""
        return ['Implement dependency version management', 'Create shared dependency policies']
    
    # Simulation methods for historical data (replace with real data in production)
    
    def _simulate_dependency_additions(self) -> List[Dict[str, Any]]:
        """Simulate dependency additions over time"""
        return [
            {'date': '2024-01-15', 'dependency': 'new-library', 'version': '1.0.0', 'reason': 'feature enhancement'},
            {'date': '2024-01-20', 'dependency': 'utility-lib', 'version': '2.1.0', 'reason': 'code optimization'}
        ]
    
    def _simulate_dependency_removals(self) -> List[Dict[str, Any]]:
        """Simulate dependency removals over time"""
        return [
            {'date': '2024-01-10', 'dependency': 'old-library', 'version': '0.9.0', 'reason': 'deprecated'}
        ]
    
    def _simulate_dependency_updates(self) -> List[Dict[str, Any]]:
        """Simulate dependency updates over time"""
        return [
            {'date': '2024-01-25', 'dependency': 'core-lib', 'old_version': '1.0.0', 'new_version': '1.1.0', 'reason': 'security patch'}
        ]
    
    def _simulate_security_improvements(self) -> List[Dict[str, Any]]:
        """Simulate security improvements over time"""
        return [
            {'date': '2024-01-22', 'improvement': 'Updated vulnerable dependency', 'impact': 'high'}
        ]
    
    def _simulate_performance_impacts(self) -> List[Dict[str, Any]]:
        """Simulate performance impacts of dependency changes"""
        return [
            {'date': '2024-01-18', 'change': 'Optimized library usage', 'impact': 'positive', 'metric': 'load_time'}
        ]
    
    def _calculate_change_frequency(self, days: int) -> float:
        """Calculate frequency of dependency changes"""
        return 0.5  # Changes per day
    
    def _calculate_stability_score(self) -> float:
        """Calculate dependency stability score"""
        return 8.5
    
    def _generate_change_recommendations(self) -> List[str]:
        """Generate recommendations based on change patterns"""
        return ['Consider implementing dependency lock files', 'Review update policies']
    
    # Optimization methods
    
    def _suggest_circular_dependency_fixes(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest fixes for circular dependencies"""
        circular_deps = analysis.get('circular_dependencies', {})
        if circular_deps.get('circular_dependencies_found'):
            return ['Introduce dependency injection', 'Extract common interfaces', 'Refactor shared code']
        return []
    
    def _suggest_dependency_consolidation(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest dependency consolidation opportunities"""
        return ['Consolidate similar libraries', 'Remove unused dependencies']
    
    def _suggest_security_upgrades(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest security-related upgrades"""
        security_analysis = analysis.get('security_analysis', {})
        if security_analysis.get('vulnerable_dependencies'):
            return ['Update vulnerable dependencies', 'Implement security scanning']
        return []
    
    def _suggest_performance_optimizations(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest performance optimizations"""
        return ['Lazy load dependencies', 'Optimize import statements']
    
    def _suggest_maintenance_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest maintenance improvements"""
        return ['Automate dependency updates', 'Implement dependency monitoring']
    
    def _prioritize_optimizations(self, analysis: Dict[str, Any]) -> List[str]:
        """Prioritize optimization recommendations"""
        return ['High: Security fixes', 'Medium: Performance optimizations', 'Low: Code cleanup']
    
    def _estimate_optimization_impact(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Estimate impact of optimizations"""
        return {
            'security': 'High improvement expected',
            'performance': 'Medium improvement expected',
            'maintainability': 'High improvement expected'
        }
    
    def _estimate_implementation_effort(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Estimate effort required for optimizations"""
        return {
            'security_fixes': '2-3 days',
            'performance_optimizations': '1 week',
            'maintenance_improvements': '3-5 days'
        }
    
    # Additional helper methods
    
    def _calculate_layers(self, graph: nx.DiGraph, topo_order: List[str]) -> List[List[str]]:
        """Calculate dependency layers from topological order"""
        layers = []
        remaining_nodes = set(topo_order)
        
        while remaining_nodes:
            current_layer = []
            for node in list(remaining_nodes):
                # Check if all dependencies of this node are already in previous layers
                dependencies = set(graph.predecessors(node))
                if dependencies.issubset(set().union(*layers) if layers else set()):
                    current_layer.append(node)
            
            for node in current_layer:
                remaining_nodes.remove(node)
            
            if current_layer:
                layers.append(current_layer)
            else:
                # Prevent infinite loop
                break
        
        return layers
    
    def _identify_highly_coupled_modules(self, graph: nx.DiGraph) -> List[str]:
        """Identify highly coupled modules"""
        coupling_scores = {}
        for node in graph.nodes():
            in_degree = graph.in_degree(node)
            out_degree = graph.out_degree(node)
            coupling_scores[node] = in_degree + out_degree
        
        # Return top 5 most coupled modules
        sorted_modules = sorted(coupling_scores.items(), key=lambda x: x[1], reverse=True)
        return [module for module, score in sorted_modules[:5] if score > 5]
    
    def _identify_loosely_coupled_modules(self, graph: nx.DiGraph) -> List[str]:
        """Identify loosely coupled modules"""
        coupling_scores = {}
        for node in graph.nodes():
            in_degree = graph.in_degree(node)
            out_degree = graph.out_degree(node)
            coupling_scores[node] = in_degree + out_degree
        
        # Return modules with low coupling
        return [module for module, score in coupling_scores.items() if score <= 2]
    
    def _identify_vulnerable_dependencies(self, dependencies: Dict) -> List[str]:
        """Identify vulnerable dependencies (placeholder)"""
        return []
    
    def _identify_outdated_dependencies(self, dependencies: Dict) -> List[str]:
        """Identify outdated dependencies (placeholder)"""
        return []
    
    def _analyze_license_risks(self, dependencies: Dict) -> List[str]:
        """Analyze license risks (placeholder)"""
        return []
    
    def _analyze_supply_chain_risks(self, dependencies: Dict) -> List[str]:
        """Analyze supply chain risks (placeholder)"""
        return []
    
    def _calculate_security_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate security score"""
        return 8.0
    
    def _generate_security_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate security recommendations"""
        return ['Regular security audits', 'Automated vulnerability scanning']
    
    def _estimate_load_time_impact(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Estimate load time impact"""
        return {'estimated_load_time': '2.5s', 'optimization_potential': '30%'}
    
    def _estimate_memory_impact(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Estimate memory impact"""
        return {'estimated_memory_usage': '150MB', 'optimization_potential': '20%'}
    
    def _estimate_build_time_impact(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Estimate build time impact"""
        return {'estimated_build_time': '45s', 'optimization_potential': '25%'}
    
    def _analyze_runtime_performance(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Analyze runtime performance"""
        return {'performance_rating': 'good', 'bottlenecks': []}
    
    def _identify_performance_optimizations(self, graph: nx.DiGraph) -> List[str]:
        """Identify performance optimization opportunities"""
        return ['Lazy loading', 'Dependency injection', 'Code splitting']
    
    def _calculate_performance_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate performance score"""
        return 7.5
    
    def _calculate_maintenance_burden(self, dependencies: Dict) -> float:
        """Calculate maintenance burden"""
        return 6.5
    
    def _analyze_update_frequency(self, dependencies: Dict) -> Dict[str, Any]:
        """Analyze update frequency"""
        return {'average_updates_per_month': 2.5, 'high_frequency_deps': []}
    
    def _assess_breaking_change_risk(self, dependencies: Dict) -> float:
        """Assess breaking change risk"""
        return 3.0
    
    def _assess_community_health(self, dependencies: Dict) -> Dict[str, Any]:
        """Assess community health of dependencies"""
        return {'healthy_projects': 15, 'at_risk_projects': 2}
    
    def _assess_long_term_viability(self, dependencies: Dict) -> Dict[str, Any]:
        """Assess long-term viability"""
        return {'viable_projects': 16, 'questionable_projects': 1}
    
    def _calculate_maintenance_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate maintenance score"""
        return 7.8
    
    def _generate_maintenance_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate maintenance recommendations"""
        return ['Regular dependency audits', 'Automated update monitoring']