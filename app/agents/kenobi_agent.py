"""
Kenobi Agent - Specialized agent for code analysis and reverse engineering
Enhanced with Phase 2 capabilities: semantic search, dependency analysis, and intelligent categorization
"""
from typing import List, Dict, Any, Optional
import asyncio
import json

from app.agents.base_agent import BaseAgent
from app.models.repository_schemas import (
    Repository, RepositoryAnalysis, CodeElement, DependencyGraph
)
from app.services.repository_service import RepositoryService
from app.services.indexing_service import IndexingService, SearchFilters
from app.agents.code_search_agent import CodeSearchAgent
from app.agents.categorization_agent import CategorizationAgent
from app.tools.dependency_analyzer import DependencyAnalyzer
from app.tools.embedding_tools import EmbeddingTools
from app.core.config import settings

class KenobiAgent(BaseAgent):
    """Specialized agent for code analysis and reverse engineering"""
    
    def __init__(self):
        super().__init__(
            model=getattr(settings, 'KENOBI_MODEL', settings.LEAD_AGENT_MODEL),
            name="Kenobi Code Analysis Agent"
        )
        self.repository_service = RepositoryService()
        
        # Phase 2 capabilities
        self.indexing_service = IndexingService()
        self.code_search_agent = CodeSearchAgent()
        self.categorization_agent = CategorizationAgent()
        self.dependency_analyzer = DependencyAnalyzer()
        self.embedding_tools = EmbeddingTools()
        
    def get_system_prompt(self) -> str:
        return """You are Kenobi, a specialized AI agent for code analysis and reverse engineering.

Your expertise includes:
- Analyzing code repositories and understanding their structure
- Extracting meaningful descriptions of code elements (classes, functions, etc.)
- Understanding code dependencies and relationships
- Categorizing code elements based on their purpose and patterns
- Providing insights about code architecture and design patterns

When analyzing code:
1. Focus on understanding the PURPOSE and FUNCTIONALITY of each code element
2. Consider the CONTEXT provided by imports and dependencies
3. Identify DESIGN PATTERNS and architectural decisions
4. Categorize elements based on their role in the system
5. Provide clear, concise descriptions that would help other developers understand the code

Always think step by step and provide structured, actionable insights."""

    async def analyze_repository(self, repo_path: str) -> RepositoryAnalysis:
        """Analyze a complete repository"""
        
        # Skip thinking step for now to avoid LLM timeouts
        # thinking = await self.think(f"Analyzing repository at: {repo_path}")
        
        # Scan and analyze the repository
        repository = await self.repository_service.scan_local_directory(repo_path)
        analysis = await self.repository_service.analyze_repository(repository.id)
        
        # Enhance analysis with AI insights
        enhanced_analysis = await self._enhance_analysis_with_ai(analysis)
        
        return enhanced_analysis
    
    async def generate_code_description(self, code_element: CodeElement, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate AI-enhanced description for a code element"""
        
        # Prepare context information
        context_info = ""
        if context:
            if 'imports' in context:
                context_info += f"Imports: {', '.join(context['imports'])}\n"
            if 'dependencies' in context:
                context_info += f"Dependencies: {', '.join(context['dependencies'])}\n"
            if 'file_context' in context:
                context_info += f"File context: {context['file_context']}\n"
        
        prompt = f"""
        Analyze this code element and provide a clear, concise description:
        
        Element Type: {code_element.element_type.value}
        Name: {code_element.name}
        File: {code_element.file_path}
        
        {context_info}
        
        Code:
        ```
        {code_element.code_snippet}
        ```
        
        Provide a description that explains:
        1. What this code element does
        2. Its purpose in the system
        3. Key functionality or behavior
        4. Any notable patterns or design decisions
        
        Keep the description concise but informative (2-3 sentences).
        """
        
        description = await self._call_llm(prompt, max_tokens=500)
        
        # Clean up the description
        description = description.strip()
        if description.startswith('"') and description.endswith('"'):
            description = description[1:-1]
        
        return description
    
    async def categorize_code_element(self, code_element: CodeElement, available_categories: List[str]) -> List[str]:
        """Categorize a code element using AI"""
        
        categories_str = ", ".join(available_categories)
        
        prompt = f"""
        Categorize this code element by selecting the most appropriate categories from the list below.
        
        Element: {code_element.name} ({code_element.element_type.value})
        File: {code_element.file_path}
        Description: {code_element.description}
        
        Code:
        ```
        {code_element.code_snippet}
        ```
        
        Available categories: {categories_str}
        
        Select 1-3 most relevant categories and return them as a JSON array.
        Consider the element's purpose, functionality, and role in the system.
        
        Example response: ["Authentication", "API", "Service"]
        """
        
        response = await self._call_llm(prompt, max_tokens=200)
        
        try:
            # Try to parse JSON response
            categories = json.loads(response.strip())
            if isinstance(categories, list):
                # Filter to only include valid categories
                valid_categories = [cat for cat in categories if cat in available_categories]
                return valid_categories[:3]  # Limit to 3 categories
        except:
            pass
        
        # Fallback: try to extract categories from text
        found_categories = []
        response_lower = response.lower()
        for category in available_categories:
            if category.lower() in response_lower:
                found_categories.append(category)
                if len(found_categories) >= 3:
                    break
        
        return found_categories
    
    async def analyze_dependencies(self, repository: Repository) -> DependencyGraph:
        """Analyze dependencies in a repository"""
        
        # Get repository analysis
        analysis = await self.repository_service.analyze_repository(repository.id)
        
        # For now, return the basic dependency graph
        # This will be enhanced in Phase 2 with more sophisticated dependency analysis
        return analysis.dependency_graph
    
    async def explain_code_functionality(self, code_element: CodeElement) -> str:
        """Provide detailed explanation of code functionality"""
        
        prompt = f"""
        Provide a detailed technical explanation of this code element:
        
        Element: {code_element.name} ({code_element.element_type.value})
        File: {code_element.file_path}
        
        Code:
        ```
        {code_element.code_snippet}
        ```
        
        Explain:
        1. What this code does step by step
        2. Input parameters and return values (if applicable)
        3. Key algorithms or logic used
        4. How it fits into the larger system
        5. Any potential issues or improvements
        
        Provide a technical but accessible explanation.
        """
        
        explanation = await self._call_llm(prompt, max_tokens=1000)
        return explanation.strip()
    
    async def _enhance_analysis_with_ai(self, analysis: RepositoryAnalysis) -> RepositoryAnalysis:
        """Enhance repository analysis with AI-generated insights"""
        
        # For now, skip AI enhancement to avoid timeouts during testing
        # This will be re-enabled once we optimize the LLM calls
        
        # Generate basic descriptions for code elements
        for file in analysis.files:
            for element in file.elements:
                if not element.description:
                    # Generate a basic description without LLM
                    element.description = self._generate_basic_description(element)
        
        # Add basic insights to metrics
        insights = self._generate_basic_insights(analysis)
        analysis.metrics['ai_insights'] = insights
        
        return analysis
    
    def _generate_basic_description(self, element: CodeElement) -> str:
        """Generate a basic description without LLM"""
        element_type = element.element_type.value
        name = element.name
        
        if element_type == "class":
            return f"Class {name} - defines a data structure or object with methods and properties"
        elif element_type == "function":
            return f"Function {name} - performs a specific operation or computation"
        elif element_type == "method":
            return f"Method {name} - performs an operation within a class context"
        elif element_type == "variable":
            return f"Variable {name} - stores data or configuration values"
        elif element_type == "import":
            return f"Import statement - brings external functionality into the module"
        else:
            return f"{element_type.title()} {name} - code element with specific functionality"
    
    def _generate_basic_insights(self, analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Generate basic insights without LLM"""
        repo = analysis.repository
        metrics = analysis.metrics
        
        # Determine complexity based on metrics
        total_elements = metrics.get('total_elements', 0)
        total_files = metrics.get('total_files', 0)
        
        if total_elements < 50:
            complexity = "Low"
        elif total_elements < 200:
            complexity = "Medium"
        else:
            complexity = "High"
        
        # Determine architecture pattern
        element_types = metrics.get('element_type_counts', {})
        if element_types.get('class', 0) > element_types.get('function', 0):
            architecture = "Object-oriented design with class-based structure"
        else:
            architecture = "Functional design with procedure-based structure"
        
        return {
            'architecture': architecture,
            'organization': f"Well-structured {repo.language.value} codebase with {total_files} files",
            'improvements': "Consider adding documentation and type hints for better maintainability",
            'characteristics': f"{repo.language.value} codebase with {total_elements} code elements",
            'complexity_level': complexity
        }
    
    async def _generate_repository_insights(self, analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Generate high-level insights about the repository"""
        
        # Prepare summary information
        repo = analysis.repository
        metrics = analysis.metrics
        
        summary = f"""
        Repository: {repo.name}
        Language: {repo.language.value}
        Framework: {repo.framework or 'Unknown'}
        Files: {metrics.get('total_files', 0)}
        Code Elements: {metrics.get('total_elements', 0)}
        Lines of Code: {metrics.get('total_lines', 0)}
        
        Element Types: {metrics.get('element_type_counts', {})}
        Frameworks Detected: {analysis.frameworks_detected}
        """
        
        prompt = f"""
        Analyze this repository and provide insights:
        
        {summary}
        
        Provide insights about:
        1. Overall architecture and design patterns
        2. Code organization and structure
        3. Potential areas for improvement
        4. Notable characteristics or patterns
        5. Complexity assessment
        
        Return insights as a JSON object with keys: architecture, organization, improvements, characteristics, complexity_level.
        """
        
        try:
            response = await self._call_llm(prompt, max_tokens=800)
            
            # Try to parse JSON
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                insights = json.loads(json_str)
                return insights
        except:
            pass
        
        # Fallback insights
        return {
            'architecture': 'Analysis pending',
            'organization': 'Standard structure detected',
            'improvements': 'Detailed analysis required',
            'characteristics': f"{repo.language.value} codebase with {metrics.get('total_elements', 0)} elements",
            'complexity_level': 'Medium'
        }
    
    # ========== Phase 2: Advanced Capabilities ==========
    
    async def index_repository_advanced(self, repository_path: str) -> Dict[str, Any]:
        """Index repository with advanced semantic search and dependency analysis"""
        
        # First, perform standard repository analysis
        analysis = await self.analyze_repository(repository_path)
        
        # Index with advanced indexing service
        indexing_result = await self.indexing_service.index_repository(
            analysis.repository, 
            analysis.files
        )
        
        # Enhance with categorization
        all_elements = []
        for file in analysis.files:
            all_elements.extend(file.elements)
        
        categorization_analysis = await self.categorization_agent.analyze_repository_categories(all_elements)
        
        return {
            'repository_analysis': {
                'repository_id': analysis.repository.id,
                'name': analysis.repository.name,
                'language': analysis.repository.language.value,
                'files_count': len(analysis.files),
                'elements_count': sum(len(f.elements) for f in analysis.files)
            },
            'indexing_result': indexing_result,
            'categorization_analysis': categorization_analysis,
            'status': 'completed'
        }
    
    async def search_code_semantic(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform semantic code search across indexed repositories"""
        
        return await self.code_search_agent.search_code(query, context)
    
    async def search_similar_code(self, example_code: str, language: str) -> Dict[str, Any]:
        """Find code similar to a given example"""
        
        return await self.code_search_agent.search_by_example(example_code, language)
    
    async def find_code_patterns(self, pattern_description: str) -> Dict[str, Any]:
        """Find code that matches a described pattern"""
        
        return await self.code_search_agent.find_code_patterns(pattern_description)
    
    async def analyze_code_relationships(self, element_name: str) -> Dict[str, Any]:
        """Discover relationships and dependencies for a code element"""
        
        return await self.code_search_agent.discover_code_relationships(element_name)
    
    async def categorize_code_elements(self, repository_id: str) -> Dict[str, Any]:
        """Categorize all code elements in a repository"""
        
        # Get repository elements from indexing service
        filters = SearchFilters()
        filters.repositories = [repository_id]
        filters.max_results = 1000  # Get all elements
        
        candidates = self.indexing_service._get_search_candidates(filters)
        elements = [self.indexing_service._deserialize_element(candidate) for candidate in candidates]
        
        # Perform categorization analysis
        categorization_results = await self.categorization_agent.categorize_elements_batch(elements)
        repository_analysis = await self.categorization_agent.analyze_repository_categories(elements)
        
        return {
            'repository_id': repository_id,
            'element_categorizations': categorization_results,
            'repository_analysis': repository_analysis,
            'total_elements': len(elements)
        }
    
    async def get_dependency_insights(self, repository_id: str) -> Dict[str, Any]:
        """Get comprehensive dependency analysis for a repository"""
        
        return await self.indexing_service.get_dependency_insights(repository_id)
    
    async def suggest_element_categories(self, element_id: str) -> Dict[str, Any]:
        """Suggest categories for a specific code element"""
        
        # Get element from indexing service
        filters = SearchFilters()
        candidates = self.indexing_service._get_search_candidates(filters)
        
        target_element = None
        for candidate in candidates:
            if candidate['id'] == element_id or candidate['full_name'] == element_id:
                target_element = self.indexing_service._deserialize_element(candidate)
                break
        
        if not target_element:
            return {'error': f'Element {element_id} not found'}
        
        return await self.categorization_agent.suggest_categories(target_element)
    
    async def analyze_repository_architecture(self, repository_id: str) -> Dict[str, Any]:
        """Perform comprehensive architectural analysis of a repository"""
        
        # Get dependency insights
        dependency_insights = await self.get_dependency_insights(repository_id)
        
        # Get categorization analysis
        categorization_analysis = await self.categorize_code_elements(repository_id)
        
        # Combine insights for architectural assessment
        architectural_analysis = {
            'repository_id': repository_id,
            'dependency_analysis': dependency_insights,
            'categorization_analysis': categorization_analysis['repository_analysis'],
            'architectural_patterns': self._identify_architectural_patterns(
                dependency_insights, 
                categorization_analysis['repository_analysis']
            ),
            'recommendations': self._generate_architectural_recommendations(
                dependency_insights,
                categorization_analysis['repository_analysis']
            )
        }
        
        return architectural_analysis
    
    async def cross_repository_search(self, query: str, repository_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Search across multiple repositories"""
        
        filters = SearchFilters()
        if repository_ids:
            filters.repositories = repository_ids
        filters.max_results = 100
        
        # Perform semantic search
        search_results = await self.indexing_service.search_code(query, filters)
        
        # Group results by repository
        results_by_repo = {}
        for result in search_results:
            repo_id = result.context.get('repository_id', 'unknown')
            if repo_id not in results_by_repo:
                results_by_repo[repo_id] = []
            
            results_by_repo[repo_id].append({
                'element': {
                    'name': result.element.name,
                    'type': result.element.element_type.value,
                    'description': result.element.description,
                    'file_path': result.context.get('file_path', ''),
                },
                'similarity': result.similarity,
                'rank_score': result.rank_score
            })
        
        return {
            'query': query,
            'total_results': len(search_results),
            'repositories_searched': len(results_by_repo),
            'results_by_repository': results_by_repo
        }
    
    def _identify_architectural_patterns(self, 
                                       dependency_insights: Dict[str, Any], 
                                       categorization_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Identify architectural patterns from dependency and categorization analysis"""
        
        patterns = {}
        
        # Extract pattern information from categorization
        if 'architectural_insights' in categorization_analysis:
            arch_insights = categorization_analysis['architectural_insights']
            patterns.update(arch_insights)
        
        # Add dependency-based patterns
        if 'coupling_metrics' in dependency_insights:
            coupling = dependency_insights['coupling_metrics']
            
            patterns['coupling_analysis'] = {
                'average_fan_in': coupling.get('average_fan_in', 0),
                'average_fan_out': coupling.get('average_fan_out', 0),
                'dependency_density': coupling.get('dependency_density', 0),
                'assessment': self._assess_coupling_level(coupling)
            }
        
        # Check for circular dependencies
        if 'circular_dependencies' in dependency_insights:
            circular_deps = dependency_insights['circular_dependencies']
            patterns['circular_dependencies'] = {
                'count': len(circular_deps),
                'severity': 'high' if len(circular_deps) > 5 else 'medium' if len(circular_deps) > 0 else 'none'
            }
        
        return patterns
    
    def _assess_coupling_level(self, coupling_metrics: Dict[str, Any]) -> str:
        """Assess the coupling level based on metrics"""
        
        density = coupling_metrics.get('dependency_density', 0)
        avg_fan_out = coupling_metrics.get('average_fan_out', 0)
        
        if density > 0.3 or avg_fan_out > 10:
            return "High coupling - consider refactoring for better modularity"
        elif density > 0.1 or avg_fan_out > 5:
            return "Medium coupling - acceptable but monitor for growth"
        else:
            return "Low coupling - well-modularized design"
    
    def _generate_architectural_recommendations(self, 
                                              dependency_insights: Dict[str, Any],
                                              categorization_analysis: Dict[str, Any]) -> List[str]:
        """Generate architectural improvement recommendations"""
        
        recommendations = []
        
        # Check coupling metrics
        if 'coupling_metrics' in dependency_insights:
            coupling = dependency_insights['coupling_metrics']
            if coupling.get('dependency_density', 0) > 0.3:
                recommendations.append("Consider reducing coupling by introducing interfaces and dependency injection")
        
        # Check circular dependencies
        if 'circular_dependencies' in dependency_insights:
            circular_count = len(dependency_insights['circular_dependencies'])
            if circular_count > 0:
                recommendations.append(f"Resolve {circular_count} circular dependencies to improve maintainability")
        
        # Check architectural organization
        if 'architectural_organization' in categorization_analysis.get('architectural_insights', {}):
            org_ratio = categorization_analysis['architectural_insights']['architectural_organization'].get('ratio', 0)
            if org_ratio < 0.3:
                recommendations.append("Consider adopting clearer architectural patterns (MVC, Service Layer, etc.)")
        
        # Check for missing patterns
        category_dist = categorization_analysis.get('category_distribution', {})
        if category_dist.get('testing', 0) == 0:
            recommendations.append("Add unit tests to improve code reliability")
        
        if category_dist.get('error_handling', 0) < category_dist.get('api', 0):
            recommendations.append("Improve error handling coverage, especially for API endpoints")
        
        if not recommendations:
            recommendations.append("Code architecture appears well-organized - continue current practices")
        
        return recommendations