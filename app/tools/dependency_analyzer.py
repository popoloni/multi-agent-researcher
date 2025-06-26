"""
Dependency analysis tools for building and analyzing code dependency graphs
"""
import re
import ast
from typing import List, Dict, Set, Tuple, Optional, Any
from collections import defaultdict, deque
from pathlib import Path

from app.models.repository_schemas import (
    Repository, ParsedFile, CodeElement, DependencyGraph, DependencyEdge,
    ImportInfo, ElementType, LanguageType
)

class DependencyAnalyzer:
    """Analyzes code dependencies and builds dependency graphs"""
    
    def __init__(self):
        self.dependency_patterns = {
            LanguageType.PYTHON: {
                'inheritance': r'class\s+(\w+)\s*\([^)]*(\w+)[^)]*\)',
                'composition': r'self\.(\w+)\s*=.*(\w+)\(',
                'method_call': r'(\w+)\.(\w+)\(',
                'import_usage': r'(\w+)\.(\w+)',
            },
            LanguageType.JAVASCRIPT: {
                'inheritance': r'class\s+(\w+)\s+extends\s+(\w+)',
                'composition': r'this\.(\w+)\s*=.*new\s+(\w+)\(',
                'method_call': r'(\w+)\.(\w+)\(',
                'import_usage': r'(\w+)\.(\w+)',
            },
            LanguageType.JAVA: {
                'inheritance': r'class\s+(\w+)\s+extends\s+(\w+)',
                'interface': r'class\s+(\w+)\s+implements\s+(\w+)',
                'composition': r'(\w+)\s+(\w+)\s*=.*new\s+(\w+)\(',
                'method_call': r'(\w+)\.(\w+)\(',
            }
        }
    
    async def build_dependency_graph(self, repository: Repository, files: List[ParsedFile]) -> DependencyGraph:
        """Build a comprehensive dependency graph for the repository"""
        
        edges = []
        element_map = {}
        
        # Build element map for quick lookup
        for file in files:
            for element in file.elements:
                element_map[element.name] = element
                element_map[f"{file.file_path}:{element.name}"] = element
        
        # Analyze dependencies for each file
        for file in files:
            file_edges = await self._analyze_file_dependencies(file, element_map, repository)
            edges.extend(file_edges)
        
        # Add import-based dependencies
        import_edges = self._analyze_import_dependencies(files)
        edges.extend(import_edges)
        
        return DependencyGraph(
            repository_id=repository.id,
            edges=edges,
            metadata={
                'total_elements': len(element_map),
                'total_dependencies': len(edges),
                'analysis_timestamp': str(repository.indexed_at)
            }
        )
    
    async def _analyze_file_dependencies(self, 
                                       file: ParsedFile, 
                                       element_map: Dict[str, CodeElement],
                                       repository: Repository) -> List[DependencyEdge]:
        """Analyze dependencies within a single file"""
        
        edges = []
        
        # Read file content for pattern analysis
        try:
            with open(file.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return edges
        
        # Analyze each element in the file
        for element in file.elements:
            element_edges = self._analyze_element_dependencies(
                element, content, file, element_map
            )
            edges.extend(element_edges)
        
        return edges
    
    def _analyze_element_dependencies(self, 
                                    element: CodeElement, 
                                    file_content: str,
                                    file: ParsedFile,
                                    element_map: Dict[str, CodeElement]) -> List[DependencyEdge]:
        """Analyze dependencies for a specific code element"""
        
        edges = []
        
        # Extract element's code snippet for analysis
        if element.code_snippet:
            snippet = element.code_snippet
        else:
            # Try to extract from file content using line numbers
            lines = file_content.split('\n')
            if element.start_line > 0 and element.end_line > element.start_line:
                snippet = '\n'.join(lines[element.start_line-1:element.end_line])
            else:
                snippet = ""
        
        if not snippet:
            return edges
        
        # Analyze different types of dependencies
        language = file.language
        
        # 1. Inheritance dependencies
        inheritance_deps = self._find_inheritance_dependencies(snippet, element, language)
        edges.extend(inheritance_deps)
        
        # 2. Composition dependencies
        composition_deps = self._find_composition_dependencies(snippet, element, language)
        edges.extend(composition_deps)
        
        # 3. Method call dependencies
        method_call_deps = self._find_method_call_dependencies(snippet, element, element_map)
        edges.extend(method_call_deps)
        
        # 4. Import usage dependencies
        import_deps = self._find_import_usage_dependencies(element, file)
        edges.extend(import_deps)
        
        return edges
    
    def _find_inheritance_dependencies(self, 
                                     snippet: str, 
                                     element: CodeElement,
                                     language: LanguageType) -> List[DependencyEdge]:
        """Find inheritance relationships"""
        
        edges = []
        
        if element.element_type != ElementType.CLASS:
            return edges
        
        patterns = self.dependency_patterns.get(language, {})
        inheritance_pattern = patterns.get('inheritance')
        
        if inheritance_pattern:
            matches = re.finditer(inheritance_pattern, snippet)
            for match in matches:
                if len(match.groups()) >= 2:
                    child_class = match.group(1)
                    parent_class = match.group(2)
                    
                    if child_class == element.name:
                        edges.append(DependencyEdge(
                            from_element=element.full_name,
                            to_element=parent_class,
                            dependency_type="inheritance",
                            strength=1.0
                        ))
        
        return edges
    
    def _find_composition_dependencies(self, 
                                     snippet: str, 
                                     element: CodeElement,
                                     language: LanguageType) -> List[DependencyEdge]:
        """Find composition relationships"""
        
        edges = []
        
        patterns = self.dependency_patterns.get(language, {})
        composition_pattern = patterns.get('composition')
        
        if composition_pattern:
            matches = re.finditer(composition_pattern, snippet)
            for match in matches:
                if len(match.groups()) >= 2:
                    # Extract composed class name
                    composed_class = match.groups()[-1]  # Usually the last group
                    
                    edges.append(DependencyEdge(
                        from_element=element.full_name,
                        to_element=composed_class,
                        dependency_type="composition",
                        strength=0.8
                    ))
        
        return edges
    
    def _find_method_call_dependencies(self, 
                                     snippet: str, 
                                     element: CodeElement,
                                     element_map: Dict[str, CodeElement]) -> List[DependencyEdge]:
        """Find method call dependencies"""
        
        edges = []
        
        # Find method calls in the snippet
        method_call_pattern = r'(\w+)\.(\w+)\('
        matches = re.finditer(method_call_pattern, snippet)
        
        for match in matches:
            object_name = match.group(1)
            method_name = match.group(2)
            
            # Try to resolve the target element
            target_element = None
            
            # Look for exact matches
            if f"{object_name}.{method_name}" in element_map:
                target_element = element_map[f"{object_name}.{method_name}"]
            elif method_name in element_map:
                target_element = element_map[method_name]
            
            if target_element:
                edges.append(DependencyEdge(
                    from_element=element.full_name,
                    to_element=target_element.full_name,
                    dependency_type="method_call",
                    strength=0.6
                ))
        
        return edges
    
    def _find_import_usage_dependencies(self, 
                                      element: CodeElement,
                                      file: ParsedFile) -> List[DependencyEdge]:
        """Find dependencies based on import usage"""
        
        edges = []
        
        # Check if element uses any imported modules
        for import_info in file.imports:
            if import_info.is_local:
                # Check if the element uses this import
                if (import_info.module in element.code_snippet or 
                    (import_info.alias and import_info.alias in element.code_snippet)):
                    
                    edges.append(DependencyEdge(
                        from_element=element.full_name,
                        to_element=import_info.module,
                        dependency_type="import_usage",
                        strength=0.4
                    ))
        
        return edges
    
    def _analyze_import_dependencies(self, files: List[ParsedFile]) -> List[DependencyEdge]:
        """Analyze file-level import dependencies"""
        
        edges = []
        
        for file in files:
            for import_info in file.imports:
                if import_info.is_local:
                    # Create dependency edge for local imports
                    edges.append(DependencyEdge(
                        from_element=file.file_path,
                        to_element=import_info.module,
                        dependency_type="file_import",
                        strength=0.5
                    ))
        
        return edges
    
    def find_circular_dependencies(self, graph: DependencyGraph) -> List[List[str]]:
        """Find circular dependencies in the graph"""
        
        # Build adjacency list
        adj_list = defaultdict(list)
        for edge in graph.edges:
            adj_list[edge.from_element].append(edge.to_element)
        
        # Find strongly connected components using Tarjan's algorithm
        def tarjan_scc():
            index_counter = [0]
            stack = []
            lowlinks = {}
            index = {}
            on_stack = {}
            sccs = []
            
            def strongconnect(node):
                index[node] = index_counter[0]
                lowlinks[node] = index_counter[0]
                index_counter[0] += 1
                stack.append(node)
                on_stack[node] = True
                
                for successor in adj_list[node]:
                    if successor not in index:
                        strongconnect(successor)
                        lowlinks[node] = min(lowlinks[node], lowlinks[successor])
                    elif on_stack.get(successor, False):
                        lowlinks[node] = min(lowlinks[node], index[successor])
                
                if lowlinks[node] == index[node]:
                    component = []
                    while True:
                        w = stack.pop()
                        on_stack[w] = False
                        component.append(w)
                        if w == node:
                            break
                    if len(component) > 1:  # Only cycles with more than 1 node
                        sccs.append(component)
            
            for node in adj_list:
                if node not in index:
                    strongconnect(node)
            
            return sccs
        
        return tarjan_scc()
    
    def calculate_coupling_metrics(self, graph: DependencyGraph) -> Dict[str, Any]:
        """Calculate coupling metrics for the dependency graph"""
        
        # Build element sets
        all_elements = set()
        for edge in graph.edges:
            all_elements.add(edge.from_element)
            all_elements.add(edge.to_element)
        
        # Calculate metrics
        total_elements = len(all_elements)
        total_dependencies = len(graph.edges)
        
        # Calculate fan-in and fan-out for each element
        fan_in = defaultdict(int)
        fan_out = defaultdict(int)
        
        for edge in graph.edges:
            fan_out[edge.from_element] += 1
            fan_in[edge.to_element] += 1
        
        # Calculate average coupling
        avg_fan_in = sum(fan_in.values()) / total_elements if total_elements > 0 else 0
        avg_fan_out = sum(fan_out.values()) / total_elements if total_elements > 0 else 0
        
        # Find highly coupled elements
        high_fan_in = [(elem, count) for elem, count in fan_in.items() if count > avg_fan_in * 2]
        high_fan_out = [(elem, count) for elem, count in fan_out.items() if count > avg_fan_out * 2]
        
        # Calculate dependency density
        max_possible_deps = total_elements * (total_elements - 1)
        dependency_density = total_dependencies / max_possible_deps if max_possible_deps > 0 else 0
        
        return {
            'total_elements': total_elements,
            'total_dependencies': total_dependencies,
            'average_fan_in': avg_fan_in,
            'average_fan_out': avg_fan_out,
            'dependency_density': dependency_density,
            'highly_coupled_elements': {
                'high_fan_in': high_fan_in[:10],  # Top 10
                'high_fan_out': high_fan_out[:10]
            },
            'coupling_distribution': {
                'fan_in_distribution': dict(fan_in),
                'fan_out_distribution': dict(fan_out)
            }
        }
    
    def get_dependency_path(self, 
                          graph: DependencyGraph, 
                          from_element: str, 
                          to_element: str) -> Optional[List[str]]:
        """Find shortest dependency path between two elements"""
        
        # Build adjacency list
        adj_list = defaultdict(list)
        for edge in graph.edges:
            adj_list[edge.from_element].append(edge.to_element)
        
        # BFS to find shortest path
        queue = deque([(from_element, [from_element])])
        visited = {from_element}
        
        while queue:
            current, path = queue.popleft()
            
            if current == to_element:
                return path
            
            for neighbor in adj_list[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None  # No path found