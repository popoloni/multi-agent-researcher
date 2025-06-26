"""
Specialized agent for intelligent code search and discovery
"""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import re

from app.agents.base_agent import BaseAgent
from app.services.indexing_service import IndexingService, SearchFilters, SearchResult
from app.models.repository_schemas import ElementType, LanguageType, CodeElement
from app.core.model_providers import model_manager

class CodeSearchAgent(BaseAgent):
    """Specialized agent for intelligent code search"""
    
    def __init__(self):
        super().__init__(
            name="Code Search Agent",
            model="mistral:7b"
        )
        self.indexing_service = IndexingService()
        self.model_manager = model_manager
        
        # Search intent patterns
        self.intent_patterns = {
            'find_class': [
                r'find.*class.*(?:named|called)\s+(\w+)',
                r'(?:class|classes).*(?:named|called)\s+(\w+)',
                r'show.*class.*(\w+)'
            ],
            'find_function': [
                r'find.*function.*(?:named|called)\s+(\w+)',
                r'(?:function|functions).*(?:named|called)\s+(\w+)',
                r'show.*function.*(\w+)'
            ],
            'find_method': [
                r'find.*method.*(?:named|called)\s+(\w+)',
                r'(?:method|methods).*(?:named|called)\s+(\w+)',
                r'show.*method.*(\w+)'
            ],
            'find_similar': [
                r'find.*similar.*to\s+(\w+)',
                r'(?:similar|like)\s+(\w+)',
                r'code.*like.*(\w+)'
            ],
            'find_dependencies': [
                r'(?:dependencies|depends).*(?:of|for)\s+(\w+)',
                r'what.*(?:uses|depends on)\s+(\w+)',
                r'find.*(?:using|calling)\s+(\w+)'
            ],
            'find_by_language': [
                r'find.*(?:in|written in)\s+(python|javascript|java|go|c#)',
                r'(?:python|javascript|java|go|c#).*code',
                r'show.*(?:python|javascript|java|go|c#)'
            ]
        }
    
    async def search_code(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform intelligent code search with intent recognition"""
        
        # Analyze search intent
        intent_analysis = await self._analyze_search_intent(query)
        
        # Build search filters based on intent
        filters = self._build_search_filters(intent_analysis, context)
        
        # Perform search
        if intent_analysis['intent'] == 'find_similar' and intent_analysis['target']:
            # Find similar code elements
            results = await self._search_similar_code(intent_analysis['target'], filters)
        else:
            # Perform semantic search
            results = await self.indexing_service.search_code(query, filters)
        
        # Enhance results with additional context
        enhanced_results = await self._enhance_search_results(results, intent_analysis)
        
        return {
            'query': query,
            'intent': intent_analysis,
            'results': enhanced_results,
            'total_results': len(enhanced_results),
            'search_filters': self._serialize_filters(filters)
        }
    
    async def search_by_example(self, example_code: str, language: str) -> Dict[str, Any]:
        """Find code similar to a given example"""
        
        # Create a temporary code element for the example
        from app.tools.code_parser import CodeParser
        
        parser = CodeParser()
        
        # Parse the example code
        temp_file = f"example.{self._get_file_extension(language)}"
        parsed_file = parser.parse_file(temp_file, example_code)
        
        if not parsed_file.elements:
            return {
                'error': 'Could not parse example code',
                'results': []
            }
        
        # Use the first element as reference
        reference_element = parsed_file.elements[0]
        
        # Generate embedding for the example
        from app.tools.embedding_tools import EmbeddingTools
        embedding_tools = EmbeddingTools()
        example_embedding = await embedding_tools.generate_code_embedding(reference_element)
        
        # Search for similar elements
        filters = SearchFilters()
        if language:
            filters.languages = [LanguageType(language.lower())]
        
        candidates = self.indexing_service._get_search_candidates(filters)
        similar_results = []
        
        for candidate in candidates:
            if candidate['embedding']:
                import pickle
                candidate_embedding = pickle.loads(candidate['embedding'])
                similarity = embedding_tools.calculate_similarity(example_embedding, candidate_embedding)
                
                if similarity > 0.3:  # Threshold for similarity
                    element = self.indexing_service._deserialize_element(candidate)
                    context = await self.indexing_service._get_element_context(element)
                    result = SearchResult(element, similarity, context)
                    similar_results.append(result)
        
        # Sort by similarity
        similar_results.sort(key=lambda x: x.similarity, reverse=True)
        
        return {
            'example_code': example_code,
            'language': language,
            'reference_element': {
                'type': reference_element.element_type.value,
                'name': reference_element.name
            },
            'results': await self._enhance_search_results(similar_results[:20], {'intent': 'find_similar'}),
            'total_results': len(similar_results)
        }
    
    async def find_code_patterns(self, pattern_description: str) -> Dict[str, Any]:
        """Find code that matches a described pattern"""
        
        # Expand the pattern description using AI
        expanded_query = await self._expand_pattern_query(pattern_description)
        
        # Search with expanded query
        filters = SearchFilters()
        filters.max_results = 30
        
        results = await self.indexing_service.search_code(expanded_query, filters)
        
        # Group results by pattern type
        pattern_groups = await self._group_by_patterns(results)
        
        return {
            'pattern_description': pattern_description,
            'expanded_query': expanded_query,
            'pattern_groups': pattern_groups,
            'total_results': len(results)
        }
    
    async def discover_code_relationships(self, element_name: str) -> Dict[str, Any]:
        """Discover relationships and dependencies for a code element"""
        
        # Find the element first
        filters = SearchFilters()
        filters.max_results = 5
        
        element_results = await self.indexing_service.search_code(element_name, filters)
        
        if not element_results:
            return {
                'error': f'Element "{element_name}" not found',
                'relationships': {}
            }
        
        target_element = element_results[0].element
        
        # Find dependencies
        dependencies = await self._find_element_dependencies(target_element)
        
        # Find dependents (what depends on this element)
        dependents = await self._find_element_dependents(target_element)
        
        # Find similar elements
        similar_elements = await self._search_similar_code(target_element.full_name, SearchFilters())
        
        return {
            'element': {
                'name': target_element.name,
                'type': target_element.element_type.value,
                'description': target_element.description
            },
            'relationships': {
                'dependencies': dependencies,
                'dependents': dependents,
                'similar_elements': similar_elements[:10]
            }
        }
    
    def get_system_prompt(self) -> str:
        return """You are a specialized AI agent for intelligent code search and discovery.

Your expertise includes:
- Understanding natural language queries about code
- Performing semantic search across codebases
- Analyzing search intent and context
- Finding similar code patterns and structures
- Providing relevant and ranked search results

You help developers find and discover code efficiently using advanced search capabilities."""
    
    async def _analyze_search_intent(self, query: str) -> Dict[str, Any]:
        """Analyze the intent behind a search query"""
        
        query_lower = query.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    target = match.group(1) if match.groups() else None
                    return {
                        'intent': intent,
                        'target': target,
                        'confidence': 0.8,
                        'matched_pattern': pattern
                    }
        
        # Default to general search
        return {
            'intent': 'general_search',
            'target': None,
            'confidence': 0.5,
            'matched_pattern': None
        }
    
    def _build_search_filters(self, intent_analysis: Dict[str, Any], context: Optional[Dict[str, Any]]) -> SearchFilters:
        """Build search filters based on intent and context"""
        
        filters = SearchFilters()
        
        # Set element type filter based on intent
        if intent_analysis['intent'] == 'find_class':
            filters.element_types = [ElementType.CLASS]
        elif intent_analysis['intent'] == 'find_function':
            filters.element_types = [ElementType.FUNCTION]
        elif intent_analysis['intent'] == 'find_method':
            filters.element_types = [ElementType.METHOD]
        
        # Set language filter if specified
        if intent_analysis['intent'] == 'find_by_language' and intent_analysis['target']:
            try:
                language = LanguageType(intent_analysis['target'].lower())
                filters.languages = [language]
            except ValueError:
                pass
        
        # Apply context filters
        if context:
            if 'repository_id' in context:
                filters.repositories = [context['repository_id']]
            elif 'repository_ids' in context and context['repository_ids']:
                filters.repositories = context['repository_ids']
            if 'languages' in context:
                filters.languages = context['languages']
            if 'max_results' in context:
                filters.max_results = context['max_results']
        
        return filters
    
    async def _search_similar_code(self, element_identifier: str, filters: SearchFilters) -> List[SearchResult]:
        """Search for code similar to a specific element"""
        
        return await self.indexing_service.search_similar_code(element_identifier, filters)
    
    async def _enhance_search_results(self, results: List[SearchResult], intent_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance search results with additional context and insights"""
        
        enhanced = []
        
        for result in results:
            enhanced_result = {
                'element': {
                    'name': result.element.name,
                    'type': result.element.element_type.value,
                    'full_name': result.element.full_name,
                    'description': result.element.description,
                    'categories': result.element.categories,
                    'code_snippet': result.element.code_snippet[:500] if result.element.code_snippet else "",
                    'complexity_score': result.element.complexity_score
                },
                'relevance': {
                    'similarity_score': result.similarity,
                    'rank_score': result.rank_score
                },
                'context': result.context,
                'insights': await self._generate_result_insights(result, intent_analysis)
            }
            
            enhanced.append(enhanced_result)
        
        return enhanced
    
    async def _generate_result_insights(self, result: SearchResult, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights for a search result"""
        
        insights = {
            'relevance_reason': self._explain_relevance(result, intent_analysis),
            'usage_context': self._infer_usage_context(result.element),
            'complexity_assessment': self._assess_complexity(result.element)
        }
        
        return insights
    
    def _explain_relevance(self, result: SearchResult, intent_analysis: Dict[str, Any]) -> str:
        """Explain why this result is relevant"""
        
        if intent_analysis['intent'] == 'find_class':
            return f"Class '{result.element.name}' matches your search criteria"
        elif intent_analysis['intent'] == 'find_function':
            return f"Function '{result.element.name}' matches your search criteria"
        elif intent_analysis['intent'] == 'find_similar':
            return f"Similar code pattern with {result.similarity:.2f} similarity score"
        else:
            return f"Semantic match with {result.similarity:.2f} relevance score"
    
    def _infer_usage_context(self, element: CodeElement) -> str:
        """Infer the usage context of a code element"""
        
        if element.element_type == ElementType.CLASS:
            if 'manager' in element.name.lower():
                return "Management/Controller class"
            elif 'service' in element.name.lower():
                return "Service layer component"
            elif 'model' in element.name.lower():
                return "Data model/Entity"
            else:
                return "General purpose class"
        elif element.element_type == ElementType.FUNCTION:
            if element.name.startswith('get_'):
                return "Data retrieval function"
            elif element.name.startswith('create_'):
                return "Object creation function"
            elif element.name.startswith('update_'):
                return "Data modification function"
            else:
                return "General utility function"
        else:
            return "Code element"
    
    def _assess_complexity(self, element: CodeElement) -> str:
        """Assess the complexity of a code element"""
        
        if element.complexity_score is None:
            return "Unknown complexity"
        
        if element.complexity_score < 2:
            return "Low complexity - simple and straightforward"
        elif element.complexity_score < 5:
            return "Medium complexity - moderate logic"
        else:
            return "High complexity - complex logic and multiple paths"
    
    async def _expand_pattern_query(self, pattern_description: str) -> str:
        """Expand a pattern description into a more detailed search query"""
        
        # For now, return the original description
        # In a full implementation, this would use AI to expand the query
        return pattern_description
    
    async def _group_by_patterns(self, results: List[SearchResult]) -> Dict[str, List[Dict[str, Any]]]:
        """Group search results by detected patterns"""
        
        patterns = {
            'classes': [],
            'functions': [],
            'methods': [],
            'utilities': []
        }
        
        for result in results:
            element_type = result.element.element_type
            
            if element_type == ElementType.CLASS:
                patterns['classes'].append(self._serialize_result(result))
            elif element_type == ElementType.FUNCTION:
                patterns['functions'].append(self._serialize_result(result))
            elif element_type == ElementType.METHOD:
                patterns['methods'].append(self._serialize_result(result))
            else:
                patterns['utilities'].append(self._serialize_result(result))
        
        return patterns
    
    def _serialize_result(self, result: SearchResult) -> Dict[str, Any]:
        """Serialize a search result for JSON output"""
        
        return {
            'name': result.element.name,
            'type': result.element.element_type.value,
            'description': result.element.description,
            'similarity': result.similarity,
            'code_snippet': result.element.code_snippet[:200] if result.element.code_snippet else ""
        }
    
    async def _find_element_dependencies(self, element: CodeElement) -> List[Dict[str, Any]]:
        """Find what this element depends on"""
        
        # This would query the dependency graph
        # For now, return empty list
        return []
    
    async def _find_element_dependents(self, element: CodeElement) -> List[Dict[str, Any]]:
        """Find what depends on this element"""
        
        # This would query the dependency graph
        # For now, return empty list
        return []
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for a language"""
        
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'java': 'java',
            'go': 'go',
            'csharp': 'cs'
        }
        
        return extensions.get(language.lower(), 'txt')
    
    def _serialize_filters(self, filters: SearchFilters) -> Dict[str, Any]:
        """Serialize search filters for JSON output"""
        
        return {
            'languages': [lang.value for lang in filters.languages],
            'element_types': [et.value for et in filters.element_types],
            'repositories': filters.repositories,
            'categories': filters.categories,
            'min_similarity': filters.min_similarity,
            'max_results': filters.max_results
        }