"""
Kenobi Agent - Specialized agent for code analysis and reverse engineering
Enhanced with Phase 2 capabilities: semantic search, dependency analysis, and intelligent categorization
"""
from typing import List, Dict, Any, Optional
import asyncio
import json
from datetime import datetime

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
from app.engines.ai_engine import AIEngine, AnalysisRequest, AnalysisType, ModelComplexity
from app.engines.vector_service import VectorService, VectorDocument
from app.engines.quality_engine import QualityEngine
from app.engines.analytics_engine import analytics_engine
from app.services.cache_service import cache_service
from app.agents.repository_analysis_agent import RepositoryAnalysisAgent
from app.agents.dependency_agent import DependencyAnalysisAgent
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
        
        # Phase 3 advanced engines
        self.ai_engine = AIEngine()
        self.vector_service = VectorService()
        self.quality_engine = QualityEngine()
        
        # Phase 4 agents and services
        self.analytics_engine = analytics_engine
        self.cache_service = cache_service
        self.repository_agent = RepositoryAnalysisAgent(
            repository_service=self.repository_service,
            indexing_service=self.indexing_service,
            vector_service=self.vector_service,
            quality_engine=self.quality_engine
        )
        self.dependency_agent = DependencyAnalysisAgent(
            indexing_service=self.indexing_service,
            vector_service=self.vector_service
        )
        
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
    
    # ==================== PHASE 3: ADVANCED AI CAPABILITIES ====================
    
    async def ai_analyze_code(self, element: CodeElement, analysis_type: AnalysisType, 
                             complexity: ModelComplexity = ModelComplexity.MEDIUM,
                             streaming: bool = False) -> Dict[str, Any]:
        """Perform AI-powered code analysis"""
        
        # Get repository context
        repository = await self.repository_service.get_repository_metadata(element.repository_id)
        
        context = {
            'repository_name': repository.name if repository else 'unknown',
            'language': repository.language.value if repository and repository.language else 'unknown',
            'framework': repository.framework or 'unknown',
            'dependencies': element.dependencies
        }
        
        # Create analysis request
        request = AnalysisRequest(
            analysis_type=analysis_type,
            code_element=element,
            context=context,
            complexity=complexity,
            streaming=streaming
        )
        
        # Perform analysis
        result = await self.ai_engine.analyze_code(request)
        
        return {
            'element_id': element.id,
            'analysis_type': analysis_type.value,
            'result': result.result,
            'confidence': result.confidence,
            'processing_time': result.processing_time,
            'model_used': result.model_used,
            'timestamp': result.timestamp.isoformat()
        }
    
    async def ai_explain_code(self, element: CodeElement) -> Dict[str, Any]:
        """Generate AI explanation of code"""
        return await self.ai_analyze_code(element, AnalysisType.CODE_EXPLANATION)
    
    async def ai_suggest_improvements(self, element: CodeElement) -> Dict[str, Any]:
        """Generate AI improvement suggestions"""
        return await self.ai_analyze_code(element, AnalysisType.IMPROVEMENT_SUGGESTIONS, ModelComplexity.COMPLEX)
    
    async def ai_generate_tests(self, element: CodeElement) -> Dict[str, Any]:
        """Generate AI test cases"""
        return await self.ai_analyze_code(element, AnalysisType.TEST_GENERATION, ModelComplexity.COMPLEX)
    
    async def ai_security_analysis(self, element: CodeElement) -> Dict[str, Any]:
        """Perform AI security analysis"""
        return await self.ai_analyze_code(element, AnalysisType.SECURITY_ANALYSIS, ModelComplexity.COMPLEX)
    
    async def ai_performance_analysis(self, element: CodeElement) -> Dict[str, Any]:
        """Perform AI performance analysis"""
        return await self.ai_analyze_code(element, AnalysisType.PERFORMANCE_ANALYSIS, ModelComplexity.MEDIUM)
    
    async def vector_add_repository(self, repository: Repository) -> Dict[str, Any]:
        """Add repository to vector database"""
        
        # Get all elements for the repository
        filters = SearchFilters()
        filters.repositories = [repository.id]
        candidates = self.indexing_service._get_search_candidates(filters)
        
        added_count = 0
        failed_count = 0
        
        for candidate in candidates:
            try:
                element = self.indexing_service._deserialize_element(candidate)
                success = await self.vector_service.add_code_element(element, repository)
                if success:
                    added_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                print(f"Failed to add element to vector DB: {e}")
                failed_count += 1
        
        return {
            'repository_id': repository.id,
            'elements_added': added_count,
            'elements_failed': failed_count,
            'total_processed': added_count + failed_count
        }
    
    async def vector_similarity_search(self, query: str, limit: int = 10, 
                                     filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform vector similarity search"""
        
        results = await self.vector_service.similarity_search(query, limit, filters)
        
        # Convert to serializable format
        search_results = []
        for result in results:
            search_results.append({
                'document': {
                    'id': result.document.id,
                    'content': result.document.content[:500] + '...' if len(result.document.content) > 500 else result.document.content,
                    'metadata': result.document.metadata
                },
                'similarity_score': result.similarity_score,
                'distance': result.distance,
                'rank': result.rank
            })
        
        return {
            'query': query,
            'results': search_results,
            'total_results': len(search_results)
        }
    
    async def vector_cluster_analysis(self, num_clusters: int = 5, 
                                    filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform vector clustering analysis"""
        
        clusters = await self.vector_service.cluster_documents(num_clusters, filters)
        
        # Convert to serializable format
        cluster_results = []
        for cluster in clusters:
            cluster_results.append({
                'cluster_id': cluster.cluster_id,
                'cluster_size': cluster.cluster_size,
                'intra_cluster_distance': cluster.intra_cluster_distance,
                'documents': [
                    {
                        'id': doc.id,
                        'metadata': doc.metadata
                    }
                    for doc in cluster.documents[:10]  # Limit to first 10 for response size
                ]
            })
        
        return {
            'num_clusters': num_clusters,
            'clusters': cluster_results,
            'total_documents_clustered': sum(c.cluster_size for c in clusters)
        }
    
    async def quality_analyze_element(self, element: CodeElement) -> Dict[str, Any]:
        """Perform comprehensive quality analysis on code element"""
        
        # Get repository context
        repository = await self.repository_service.get_repository_metadata(element.repository_id)
        
        # Perform quality analysis
        report = await self.quality_engine.analyze_quality(element, repository)
        
        # Convert to serializable format
        return {
            'element_id': report.element_id,
            'repository_id': report.repository_id,
            'overall_score': report.overall_score,
            'quality_grade': self.quality_engine._get_quality_grade(report.overall_score),
            'scores': {
                metric.value: {
                    'score': score.score,
                    'max_score': score.max_score,
                    'issues_count': score.issues_count,
                    'trend': score.trend
                }
                for metric, score in report.scores.items()
            },
            'issues': [
                {
                    'metric': issue.metric.value,
                    'severity': issue.severity.value,
                    'title': issue.title,
                    'description': issue.description,
                    'location': issue.location,
                    'line_number': issue.line_number,
                    'suggestion': issue.suggestion,
                    'effort_estimate': issue.effort_estimate,
                    'impact_score': issue.impact_score
                }
                for issue in report.issues
            ],
            'recommendations': report.recommendations,
            'analysis_timestamp': report.analysis_timestamp.isoformat(),
            'processing_time': report.processing_time
        }
    
    async def quality_repository_summary(self, repository_id: str) -> Dict[str, Any]:
        """Get quality summary for entire repository"""
        
        return self.quality_engine.get_repository_quality_summary(repository_id)
    
    async def quality_trends_analysis(self, element_id: str, days: int = 30) -> Dict[str, Any]:
        """Get quality trends for an element"""
        
        trends = self.quality_engine.get_quality_trends(element_id, days)
        
        # Convert to serializable format
        trend_results = {}
        for metric, trend in trends.items():
            trend_results[metric.value] = {
                'trend_direction': trend.trend_direction,
                'trend_strength': trend.trend_strength,
                'prediction': trend.prediction,
                'data_points': len(trend.scores),
                'latest_score': trend.scores[-1] if trend.scores else None
            }
        
        return {
            'element_id': element_id,
            'analysis_period_days': days,
            'trends': trend_results
        }
    
    async def get_ai_statistics(self) -> Dict[str, Any]:
        """Get AI engine usage statistics"""
        
        return self.ai_engine.get_analysis_statistics()
    
    async def get_vector_statistics(self) -> Dict[str, Any]:
        """Get vector database statistics"""
        
        return self.vector_service.get_collection_stats()
    
    async def batch_quality_analysis(self, repository_id: str) -> Dict[str, Any]:
        """Perform batch quality analysis on all elements in repository"""
        
        # Get all elements for the repository
        filters = SearchFilters()
        filters.repositories = [repository_id]
        candidates = self.indexing_service._get_search_candidates(filters)
        
        # Get repository
        repository = await self.repository_service.get_repository_metadata(repository_id)
        
        analyzed_count = 0
        failed_count = 0
        total_score = 0
        
        for candidate in candidates[:50]:  # Limit to 50 elements for performance
            try:
                element = self.indexing_service._deserialize_element(candidate)
                report = await self.quality_engine.analyze_quality(element, repository)
                analyzed_count += 1
                total_score += report.overall_score
            except Exception as e:
                print(f"Failed to analyze element quality: {e}")
                failed_count += 1
        
        avg_score = total_score / max(analyzed_count, 1)
        
        return {
            'repository_id': repository_id,
            'elements_analyzed': analyzed_count,
            'elements_failed': failed_count,
            'average_quality_score': avg_score,
            'quality_grade': self.quality_engine._get_quality_grade(avg_score),
            'repository_summary': await self.quality_repository_summary(repository_id)
        }
    
    async def comprehensive_repository_analysis(self, repository_path: str, repository_name: str) -> Dict[str, Any]:
        """
        Perform comprehensive repository analysis using the Repository Analysis Agent
        """
        try:
            # Check cache first
            cache_key = f"comprehensive_analysis:{repository_name}"
            cached_result = await self.cache_service.get(cache_key)
            if cached_result:
                return cached_result
            
            # Use the provided repository path directly
            # Perform comprehensive analysis
            result = await self.repository_agent.analyze_repository_comprehensive(repository_path, repository_name)
            
            # Cache result for 1 hour
            await self.cache_service.set(cache_key, result, ttl=3600)
            
            return result
            
        except Exception as e:
            return {'error': f"Comprehensive analysis failed: {str(e)}"}
    
    async def monitor_repository_health(self, repository_id: str) -> Dict[str, Any]:
        """
        Monitor repository health with real-time metrics
        """
        try:
            # Check cache first
            cache_key = f"health_monitoring:{repository_id}"
            cached_result = await self.cache_service.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get repository
            repository = await self.repository_service.get_repository_metadata(repository_id)
            if not repository:
                return {'error': f"Repository '{repository_id}' not found"}
            
            # Perform health monitoring
            result = await self.repository_agent.monitor_repository_health(repository.local_path)
            
            # Cache result for 15 minutes
            await self.cache_service.set(cache_key, result, ttl=900)
            
            return result
            
        except Exception as e:
            return {'error': f"Health monitoring failed: {str(e)}"}
    
    async def batch_analyze_repositories(self, repository_paths: List[str], analysis_types: List[str] = None) -> Dict[str, Any]:
        """
        Perform batch analysis on multiple repositories
        """
        try:
            cache_key = f"batch_analysis:{hash(str(repository_paths))}"
            cached_result = await self.cache_service.get(cache_key)
            if cached_result:
                return cached_result
            
            # Default analysis types
            if not analysis_types:
                analysis_types = ['structure', 'quality', 'dependencies', 'security']
            
            # Perform batch analysis
            batch_results = []
            for repo_path in repository_paths:
                repo_name = repo_path.split('/')[-1]
                if 'comprehensive' in analysis_types:
                    result = await self.repository_agent.analyze_repository_comprehensive(repo_path, repo_name)
                else:
                    # Perform selective analysis based on types
                    result = await self._selective_repository_analysis(repo_path, repo_name, analysis_types)
                
                batch_results.append({
                    'repository_path': repo_path,
                    'repository_name': repo_name,
                    'analysis': result
                })
            
            # Compile batch summary
            batch_summary = {
                'total_repositories': len(repository_paths),
                'analysis_types': analysis_types,
                'batch_timestamp': datetime.now().isoformat(),
                'repositories': batch_results,
                'summary_statistics': self._calculate_batch_statistics(batch_results)
            }
            
            # Cache result for 30 minutes
            await self.cache_service.set(cache_key, batch_summary, ttl=1800)
            
            return batch_summary
        except Exception as e:
            return {'error': f"Batch analysis failed: {str(e)}"}
    
    async def compare_repositories(self, repository_ids: List[str], comparison_aspects: List[str] = None) -> Dict[str, Any]:
        """
        Compare two repositories across multiple dimensions
        """
        try:
            if len(repository_ids) < 2:
                return {'error': 'At least 2 repository IDs are required for comparison'}
            
            repository_id_1, repository_id_2 = repository_ids[0], repository_ids[1]
            cache_key = f"repo_comparison:{repository_id_1}:{repository_id_2}"
            cached_result = await self.cache_service.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get repository metadata
            repo1 = await self.repository_service.get_repository_metadata(repository_id_1)
            repo2 = await self.repository_service.get_repository_metadata(repository_id_2)
            
            if not repo1 or not repo2:
                return {'error': 'One or both repositories not found'}
            
            # Default comparison aspects
            if not comparison_aspects:
                comparison_aspects = ['structure', 'quality', 'dependencies', 'complexity']
            
            # Perform repository comparison
            comparison_result = await self.dependency_agent.compare_repositories(
                repo1.local_path, repo2.local_path, comparison_aspects
            )
            
            # Add metadata
            comparison_result.update({
                'repository_1': {
                    'id': repository_id_1,
                    'name': repo1.name,
                    'path': repo1.local_path
                },
                'repository_2': {
                    'id': repository_id_2,
                    'name': repo2.name,
                    'path': repo2.local_path
                },
                'comparison_timestamp': datetime.now().isoformat(),
                'comparison_aspects': comparison_aspects
            })
            
            # Cache result for 45 minutes
            await self.cache_service.set(cache_key, comparison_result, ttl=2700)
            
            return comparison_result
        except Exception as e:
            return {'error': f"Repository comparison failed: {str(e)}"}
    
    async def generate_repository_insights(self, repository_id: str, insight_types: List[str] = None) -> Dict[str, Any]:
        """
        Generate actionable insights for repository improvement
        """
        try:
            cache_key = f"repo_insights:{repository_id}"
            cached_result = await self.cache_service.get(cache_key)
            if cached_result:
                return cached_result
            
            # Get repository metadata
            repository = await self.repository_service.get_repository_metadata(repository_id)
            if not repository:
                return {'error': f"Repository '{repository_id}' not found"}
            
            # Default insight types
            if not insight_types:
                insight_types = ['optimization', 'refactoring', 'testing', 'documentation', 'security']
            
            # Generate insights using repository agent
            insights = await self.repository_agent.generate_actionable_insights(
                repository.local_path, repository.name, insight_types
            )
            
            # Add metadata
            insights.update({
                'repository_id': repository_id,
                'repository_name': repository.name,
                'insights_timestamp': datetime.now().isoformat(),
                'insight_types': insight_types
            })
            
            # Cache result for 1 hour
            await self.cache_service.set(cache_key, insights, ttl=3600)
            
            return insights
        except Exception as e:
            return {'error': f"Insights generation failed: {str(e)}"}
    
    async def _selective_repository_analysis(self, repository_path: str, repository_name: str, analysis_types: List[str]) -> Dict[str, Any]:
        """
        Perform selective analysis based on specified types
        """
        results = {}
        
        if 'structure' in analysis_types:
            results['structure'] = await self.repository_agent._analyze_code_structure(repository_path)
        
        if 'quality' in analysis_types:
            results['quality'] = await self.repository_agent._analyze_repository_quality(repository_path)
        
        if 'dependencies' in analysis_types:
            results['dependencies'] = await self.repository_agent._analyze_dependencies(repository_path)
        
        if 'security' in analysis_types:
            results['security'] = await self.repository_agent._analyze_security_patterns(repository_path)
        
        return results
    
    def _calculate_batch_statistics(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate summary statistics for batch analysis
        """
        total_repos = len(batch_results)
        if total_repos == 0:
            return {}
        
        # Extract health scores
        health_scores = []
        for result in batch_results:
            analysis = result.get('analysis', {})
            if 'overall_health_score' in analysis:
                health_scores.append(analysis['overall_health_score'])
        
        if health_scores:
            avg_health = sum(health_scores) / len(health_scores)
            min_health = min(health_scores)
            max_health = max(health_scores)
        else:
            avg_health = min_health = max_health = 0
        
        return {
            'total_repositories': total_repos,
            'average_health_score': avg_health,
            'min_health_score': min_health,
            'max_health_score': max_health,
            'repositories_analyzed': len([r for r in batch_results if 'error' not in r.get('analysis', {})])
        }

    async def chat_about_repository(self, message: str, repository_id: str, branch: str = "main") -> Dict[str, Any]:
        """
        Chat with Kenobi about repository code using RAG (Retrieval-Augmented Generation)
        """
        try:
            # Get repository metadata
            repository = await self.repository_service.get_repository_metadata(repository_id)
            if not repository:
                return {
                    "answer": "Repository not found. Please make sure the repository is indexed.",
                    "sources": [],
                    "timestamp": datetime.now().isoformat()
                }

            # Search for relevant code elements based on the message
            search_filters = SearchFilters(
                repository_ids=[repository_id],
                languages=None,
                element_types=None,
                max_results=10
            )
            
            # Use semantic search to find relevant code
            search_results = await self.search_code_semantic(message, search_filters)
            
            # Extract relevant context from search results
            context_elements = []
            sources = []
            
            if search_results and 'results' in search_results:
                for result in search_results['results'][:5]:  # Limit to top 5 results
                    element = result.get('element', {})
                    if element:
                        context_elements.append({
                            'name': element.get('name', ''),
                            'type': element.get('element_type', ''),
                            'content': element.get('content', ''),
                            'file_path': element.get('file_path', ''),
                            'line_number': element.get('line_number', 0)
                        })
                        
                        sources.append({
                            'file': element.get('file_path', ''),
                            'line': element.get('line_number', 0),
                            'element_name': element.get('name', ''),
                            'element_type': element.get('element_type', '')
                        })

            # Build context for the AI
            context_text = f"Repository: {repository.get('name', 'Unknown')}\n"
            context_text += f"Language: {repository.get('language', 'Unknown')}\n"
            context_text += f"Branch: {branch}\n\n"
            
            if context_elements:
                context_text += "Relevant code elements:\n\n"
                for element in context_elements:
                    context_text += f"File: {element['file_path']}\n"
                    context_text += f"Type: {element['type']}\n"
                    context_text += f"Name: {element['name']}\n"
                    if element['content']:
                        context_text += f"Content:\n{element['content'][:500]}...\n\n"
            else:
                context_text += "No specific code elements found for this query.\n"

            # Generate response using AI
            prompt = f"""You are Kenobi, a helpful code analysis assistant. A user is asking about their codebase.

Context:
{context_text}

User Question: {message}

Please provide a helpful, accurate response about the code. If you found relevant code elements, reference them in your answer. If you couldn't find specific code related to the question, provide general guidance or ask for clarification.

Keep your response conversational and helpful. Include specific file names and line numbers when referencing code."""

            # Use the AI engine to generate response
            analysis_request = AnalysisRequest(
                content=prompt,
                analysis_type=AnalysisType.EXPLANATION,
                complexity=ModelComplexity.MEDIUM,
                context={
                    "repository_id": repository_id,
                    "branch": branch,
                    "user_message": message
                }
            )
            
            ai_response = await self.ai_engine.analyze(analysis_request)
            
            response_text = ai_response.get('analysis', {}).get('explanation', 
                "I'm sorry, I couldn't generate a response for your question. Please try rephrasing it or ask about specific code elements.")

            return {
                "answer": response_text,
                "sources": sources,
                "timestamp": datetime.now().isoformat(),
                "repository_id": repository_id,
                "branch": branch,
                "context_elements_found": len(context_elements)
            }

        except Exception as e:
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}. Please try again or contact support if the issue persists.",
                "sources": [],
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }