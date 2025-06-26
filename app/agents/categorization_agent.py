"""
Specialized agent for intelligent code categorization and classification
"""
import asyncio
import json
from typing import List, Dict, Any, Optional, Set
import re

from app.agents.base_agent import BaseAgent
from app.models.repository_schemas import CodeElement, ElementType, LanguageType
from app.core.model_providers import model_manager

class CategorizationAgent(BaseAgent):
    """Specialized agent for code categorization and classification"""
    
    def __init__(self):
        super().__init__(
            name="Code Categorization Agent",
            model="mistral:7b"
        )
        self.model_manager = model_manager
        
        # Load predefined categories
        self.categories = self._load_category_definitions()
        
        # Pattern-based classification rules
        self.classification_patterns = self._load_classification_patterns()
    
    def get_system_prompt(self) -> str:
        return """You are a specialized AI agent for code categorization and classification.

Your expertise includes:
- Analyzing code elements and assigning appropriate categories
- Understanding architectural patterns and design principles
- Classifying code based on functionality, purpose, and structure
- Providing confidence scores and explanations for categorizations

You help developers understand and organize their codebase by providing intelligent categorization."""
    
    def _load_category_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined category definitions"""
        
        return {
            # Architectural patterns
            'mvc_controller': {
                'description': 'Model-View-Controller pattern controller',
                'keywords': ['controller', 'handler', 'router'],
                'patterns': [r'.*controller.*', r'.*handler.*', r'.*router.*'],
                'element_types': [ElementType.CLASS, ElementType.FUNCTION]
            },
            'mvc_model': {
                'description': 'Data model or entity class',
                'keywords': ['model', 'entity', 'data', 'schema'],
                'patterns': [r'.*model.*', r'.*entity.*', r'.*schema.*'],
                'element_types': [ElementType.CLASS]
            },
            'mvc_view': {
                'description': 'View or presentation layer component',
                'keywords': ['view', 'template', 'component', 'ui'],
                'patterns': [r'.*view.*', r'.*template.*', r'.*component.*'],
                'element_types': [ElementType.CLASS, ElementType.FUNCTION]
            },
            
            # Service patterns
            'service_layer': {
                'description': 'Service layer component',
                'keywords': ['service', 'business', 'logic'],
                'patterns': [r'.*service.*', r'.*business.*'],
                'element_types': [ElementType.CLASS, ElementType.FUNCTION]
            },
            'repository_pattern': {
                'description': 'Repository pattern implementation',
                'keywords': ['repository', 'dao', 'data_access'],
                'patterns': [r'.*repository.*', r'.*dao.*', r'.*data.*access.*'],
                'element_types': [ElementType.CLASS]
            },
            'factory_pattern': {
                'description': 'Factory pattern implementation',
                'keywords': ['factory', 'builder', 'creator'],
                'patterns': [r'.*factory.*', r'.*builder.*', r'.*creator.*'],
                'element_types': [ElementType.CLASS, ElementType.FUNCTION]
            },
            
            # Functional categories
            'data_processing': {
                'description': 'Data processing and transformation',
                'keywords': ['process', 'transform', 'parse', 'convert'],
                'patterns': [r'.*process.*', r'.*transform.*', r'.*parse.*', r'.*convert.*'],
                'element_types': [ElementType.FUNCTION, ElementType.METHOD]
            },
            'validation': {
                'description': 'Data validation and verification',
                'keywords': ['validate', 'verify', 'check', 'ensure'],
                'patterns': [r'.*validate.*', r'.*verify.*', r'.*check.*', r'.*ensure.*'],
                'element_types': [ElementType.FUNCTION, ElementType.METHOD]
            },
            'authentication': {
                'description': 'Authentication and authorization',
                'keywords': ['auth', 'login', 'permission', 'access'],
                'patterns': [r'.*auth.*', r'.*login.*', r'.*permission.*', r'.*access.*'],
                'element_types': [ElementType.CLASS, ElementType.FUNCTION, ElementType.METHOD]
            },
            'database': {
                'description': 'Database operations and queries',
                'keywords': ['db', 'database', 'query', 'sql', 'orm'],
                'patterns': [r'.*db.*', r'.*database.*', r'.*query.*', r'.*sql.*'],
                'element_types': [ElementType.CLASS, ElementType.FUNCTION, ElementType.METHOD]
            },
            'api': {
                'description': 'API endpoints and web services',
                'keywords': ['api', 'endpoint', 'route', 'web', 'rest'],
                'patterns': [r'.*api.*', r'.*endpoint.*', r'.*route.*', r'.*rest.*'],
                'element_types': [ElementType.CLASS, ElementType.FUNCTION, ElementType.METHOD]
            },
            
            # Utility categories
            'utility': {
                'description': 'Utility functions and helpers',
                'keywords': ['util', 'helper', 'tool', 'common'],
                'patterns': [r'.*util.*', r'.*helper.*', r'.*tool.*', r'.*common.*'],
                'element_types': [ElementType.FUNCTION, ElementType.METHOD, ElementType.CLASS]
            },
            'configuration': {
                'description': 'Configuration and settings',
                'keywords': ['config', 'setting', 'option', 'parameter'],
                'patterns': [r'.*config.*', r'.*setting.*', r'.*option.*'],
                'element_types': [ElementType.CLASS, ElementType.VARIABLE]
            },
            'testing': {
                'description': 'Testing and test utilities',
                'keywords': ['test', 'mock', 'stub', 'fixture'],
                'patterns': [r'.*test.*', r'.*mock.*', r'.*stub.*', r'.*fixture.*'],
                'element_types': [ElementType.CLASS, ElementType.FUNCTION, ElementType.METHOD]
            },
            
            # Error handling
            'error_handling': {
                'description': 'Error handling and exception management',
                'keywords': ['error', 'exception', 'handle', 'catch'],
                'patterns': [r'.*error.*', r'.*exception.*', r'.*handle.*'],
                'element_types': [ElementType.CLASS, ElementType.FUNCTION, ElementType.METHOD]
            },
            
            # Performance and optimization
            'caching': {
                'description': 'Caching and performance optimization',
                'keywords': ['cache', 'memo', 'optimize', 'performance'],
                'patterns': [r'.*cache.*', r'.*memo.*', r'.*optimize.*'],
                'element_types': [ElementType.CLASS, ElementType.FUNCTION, ElementType.METHOD]
            },
            
            # Security
            'security': {
                'description': 'Security-related functionality',
                'keywords': ['security', 'encrypt', 'decrypt', 'hash', 'secure'],
                'patterns': [r'.*security.*', r'.*encrypt.*', r'.*hash.*', r'.*secure.*'],
                'element_types': [ElementType.CLASS, ElementType.FUNCTION, ElementType.METHOD]
            }
        }
    
    def _load_classification_patterns(self) -> Dict[LanguageType, Dict[str, List[str]]]:
        """Load language-specific classification patterns"""
        
        return {
            LanguageType.PYTHON: {
                'class_patterns': [
                    r'class\s+(\w*Manager\w*)',
                    r'class\s+(\w*Service\w*)',
                    r'class\s+(\w*Controller\w*)',
                    r'class\s+(\w*Repository\w*)',
                    r'class\s+(\w*Factory\w*)',
                    r'class\s+(\w*Builder\w*)',
                    r'class\s+(\w*Handler\w*)',
                    r'class\s+(\w*Processor\w*)',
                    r'class\s+(\w*Validator\w*)',
                    r'class\s+(\w*Exception\w*)',
                    r'class\s+(\w*Error\w*)'
                ],
                'function_patterns': [
                    r'def\s+(get_\w+)',
                    r'def\s+(set_\w+)',
                    r'def\s+(create_\w+)',
                    r'def\s+(update_\w+)',
                    r'def\s+(delete_\w+)',
                    r'def\s+(validate_\w+)',
                    r'def\s+(process_\w+)',
                    r'def\s+(handle_\w+)',
                    r'def\s+(parse_\w+)',
                    r'def\s+(convert_\w+)'
                ],
                'decorator_patterns': [
                    r'@property',
                    r'@staticmethod',
                    r'@classmethod',
                    r'@cached_property',
                    r'@lru_cache',
                    r'@app\.route',
                    r'@api\.route',
                    r'@login_required',
                    r'@admin_required'
                ]
            },
            LanguageType.JAVASCRIPT: {
                'class_patterns': [
                    r'class\s+(\w*Manager\w*)',
                    r'class\s+(\w*Service\w*)',
                    r'class\s+(\w*Controller\w*)',
                    r'class\s+(\w*Component\w*)',
                    r'class\s+(\w*Handler\w*)'
                ],
                'function_patterns': [
                    r'function\s+(get\w+)',
                    r'function\s+(set\w+)',
                    r'function\s+(create\w+)',
                    r'function\s+(update\w+)',
                    r'function\s+(delete\w+)',
                    r'const\s+(\w+)\s*=.*=>'
                ]
            },
            LanguageType.JAVA: {
                'class_patterns': [
                    r'class\s+(\w*Manager\w*)',
                    r'class\s+(\w*Service\w*)',
                    r'class\s+(\w*Controller\w*)',
                    r'class\s+(\w*Repository\w*)',
                    r'class\s+(\w*Factory\w*)',
                    r'class\s+(\w*Exception\w*)'
                ],
                'annotation_patterns': [
                    r'@Controller',
                    r'@Service',
                    r'@Repository',
                    r'@Component',
                    r'@RestController',
                    r'@Entity',
                    r'@Table'
                ]
            }
        }
    
    async def categorize_element(self, element: CodeElement, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Categorize a single code element"""
        
        categories = set()
        
        # Apply pattern-based categorization
        pattern_categories = self._apply_pattern_categorization(element)
        categories.update(pattern_categories)
        
        # Apply semantic categorization
        semantic_categories = await self._apply_semantic_categorization(element)
        categories.update(semantic_categories)
        
        # Apply context-based categorization
        if context:
            context_categories = self._apply_context_categorization(element, context)
            categories.update(context_categories)
        
        # Filter and validate categories
        valid_categories = self._validate_categories(list(categories), element)
        
        return valid_categories
    
    async def categorize_elements_batch(self, elements: List[CodeElement]) -> Dict[str, List[str]]:
        """Categorize multiple elements efficiently"""
        
        results = {}
        
        # Process elements in batches for efficiency
        batch_size = 10
        for i in range(0, len(elements), batch_size):
            batch = elements[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [self.categorize_element(element) for element in batch]
            batch_results = await asyncio.gather(*tasks)
            
            # Store results
            for element, categories in zip(batch, batch_results):
                results[element.full_name] = categories
        
        return results
    
    async def suggest_categories(self, element: CodeElement) -> Dict[str, Any]:
        """Suggest categories with confidence scores"""
        
        suggestions = {}
        
        # Get all possible categories
        all_categories = await self.categorize_element(element)
        
        # Calculate confidence scores for each category
        for category in all_categories:
            confidence = self._calculate_category_confidence(element, category)
            suggestions[category] = {
                'confidence': confidence,
                'reasoning': self._explain_categorization(element, category)
            }
        
        # Sort by confidence
        sorted_suggestions = dict(sorted(suggestions.items(), key=lambda x: x[1]['confidence'], reverse=True))
        
        return {
            'element': {
                'name': element.name,
                'type': element.element_type.value
            },
            'suggested_categories': sorted_suggestions,
            'top_category': list(sorted_suggestions.keys())[0] if sorted_suggestions else None
        }
    
    async def analyze_repository_categories(self, elements: List[CodeElement]) -> Dict[str, Any]:
        """Analyze category distribution across a repository"""
        
        # Categorize all elements
        categorization_results = await self.categorize_elements_batch(elements)
        
        # Analyze distribution
        category_counts = {}
        element_type_categories = {}
        
        for element_id, categories in categorization_results.items():
            # Find the element
            element = next((e for e in elements if e.full_name == element_id), None)
            if not element:
                continue
            
            element_type = element.element_type.value
            if element_type not in element_type_categories:
                element_type_categories[element_type] = {}
            
            for category in categories:
                # Overall counts
                category_counts[category] = category_counts.get(category, 0) + 1
                
                # By element type
                if category not in element_type_categories[element_type]:
                    element_type_categories[element_type][category] = 0
                element_type_categories[element_type][category] += 1
        
        # Calculate insights
        total_elements = len(elements)
        most_common_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Identify architectural patterns
        architectural_insights = self._identify_architectural_patterns(category_counts)
        
        return {
            'total_elements': total_elements,
            'total_categories': len(category_counts),
            'category_distribution': category_counts,
            'most_common_categories': most_common_categories,
            'categories_by_element_type': element_type_categories,
            'architectural_insights': architectural_insights,
            'categorization_coverage': len(categorization_results) / total_elements if total_elements > 0 else 0
        }
    
    def _apply_pattern_categorization(self, element: CodeElement) -> List[str]:
        """Apply pattern-based categorization rules"""
        
        categories = []
        element_name_lower = element.name.lower()
        
        # Check each category definition
        for category_name, category_def in self.categories.items():
            # Check if element type matches
            if element.element_type not in category_def['element_types']:
                continue
            
            # Check keyword matches
            for keyword in category_def['keywords']:
                if keyword in element_name_lower:
                    categories.append(category_name)
                    break
            
            # Check pattern matches
            for pattern in category_def['patterns']:
                if re.search(pattern, element_name_lower):
                    categories.append(category_name)
                    break
        
        return categories
    
    async def _apply_semantic_categorization(self, element: CodeElement) -> List[str]:
        """Apply AI-based semantic categorization"""
        
        categories = []
        
        # Use element description and code snippet for semantic analysis
        text_for_analysis = []
        
        if element.description:
            text_for_analysis.append(element.description)
        
        if element.code_snippet:
            # Use first few lines of code snippet
            snippet_lines = element.code_snippet.split('\n')[:5]
            text_for_analysis.append('\n'.join(snippet_lines))
        
        if not text_for_analysis:
            return categories
        
        analysis_text = '\n'.join(text_for_analysis)
        
        # For now, use simple keyword-based analysis
        # In a full implementation, this would use AI/LLM for semantic understanding
        semantic_keywords = {
            'data_processing': ['process', 'transform', 'convert', 'parse', 'format'],
            'validation': ['validate', 'check', 'verify', 'ensure', 'assert'],
            'database': ['query', 'select', 'insert', 'update', 'delete', 'sql'],
            'api': ['request', 'response', 'endpoint', 'route', 'http'],
            'authentication': ['login', 'password', 'token', 'auth', 'permission'],
            'error_handling': ['try', 'except', 'catch', 'error', 'exception'],
            'testing': ['test', 'assert', 'mock', 'verify', 'expect']
        }
        
        analysis_lower = analysis_text.lower()
        for category, keywords in semantic_keywords.items():
            if any(keyword in analysis_lower for keyword in keywords):
                categories.append(category)
        
        return categories
    
    def _apply_context_categorization(self, element: CodeElement, context: Dict[str, Any]) -> List[str]:
        """Apply context-based categorization"""
        
        categories = []
        
        # File path context
        if 'file_path' in context:
            file_path = context['file_path'].lower()
            
            if 'test' in file_path:
                categories.append('testing')
            elif 'api' in file_path or 'route' in file_path:
                categories.append('api')
            elif 'model' in file_path:
                categories.append('mvc_model')
            elif 'view' in file_path:
                categories.append('mvc_view')
            elif 'controller' in file_path:
                categories.append('mvc_controller')
            elif 'service' in file_path:
                categories.append('service_layer')
            elif 'util' in file_path or 'helper' in file_path:
                categories.append('utility')
            elif 'config' in file_path:
                categories.append('configuration')
        
        # Repository context
        if 'repository_language' in context:
            language = context['repository_language']
            # Language-specific categorization could be applied here
        
        return categories
    
    def _validate_categories(self, categories: List[str], element: CodeElement) -> List[str]:
        """Validate and filter categories"""
        
        valid_categories = []
        
        for category in categories:
            if category in self.categories:
                category_def = self.categories[category]
                
                # Check if element type is valid for this category
                if element.element_type in category_def['element_types']:
                    valid_categories.append(category)
        
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for category in valid_categories:
            if category not in seen:
                seen.add(category)
                result.append(category)
        
        return result
    
    def _calculate_category_confidence(self, element: CodeElement, category: str) -> float:
        """Calculate confidence score for a category assignment"""
        
        if category not in self.categories:
            return 0.0
        
        category_def = self.categories[category]
        confidence = 0.0
        
        # Base confidence for element type match
        if element.element_type in category_def['element_types']:
            confidence += 0.3
        
        # Keyword match confidence
        element_name_lower = element.name.lower()
        keyword_matches = sum(1 for keyword in category_def['keywords'] if keyword in element_name_lower)
        confidence += min(0.4, keyword_matches * 0.2)
        
        # Pattern match confidence
        pattern_matches = sum(1 for pattern in category_def['patterns'] if re.search(pattern, element_name_lower))
        confidence += min(0.3, pattern_matches * 0.15)
        
        return min(1.0, confidence)
    
    def _explain_categorization(self, element: CodeElement, category: str) -> str:
        """Explain why an element was assigned to a category"""
        
        if category not in self.categories:
            return "Unknown category"
        
        category_def = self.categories[category]
        reasons = []
        
        # Check keyword matches
        element_name_lower = element.name.lower()
        matched_keywords = [kw for kw in category_def['keywords'] if kw in element_name_lower]
        if matched_keywords:
            reasons.append(f"Contains keywords: {', '.join(matched_keywords)}")
        
        # Check pattern matches
        matched_patterns = []
        for pattern in category_def['patterns']:
            if re.search(pattern, element_name_lower):
                matched_patterns.append(pattern)
        if matched_patterns:
            reasons.append(f"Matches naming patterns")
        
        # Element type
        reasons.append(f"Element type ({element.element_type.value}) is suitable for this category")
        
        return "; ".join(reasons) if reasons else "General classification"
    
    def _identify_architectural_patterns(self, category_counts: Dict[str, int]) -> Dict[str, Any]:
        """Identify architectural patterns from category distribution"""
        
        insights = {}
        
        # Check for MVC pattern
        mvc_categories = ['mvc_controller', 'mvc_model', 'mvc_view']
        mvc_count = sum(category_counts.get(cat, 0) for cat in mvc_categories)
        if mvc_count > 0:
            insights['mvc_pattern'] = {
                'detected': True,
                'strength': min(1.0, mvc_count / 10),  # Normalize to 0-1
                'components': {cat: category_counts.get(cat, 0) for cat in mvc_categories}
            }
        
        # Check for service layer pattern
        service_count = category_counts.get('service_layer', 0)
        if service_count > 0:
            insights['service_layer_pattern'] = {
                'detected': True,
                'strength': min(1.0, service_count / 5),
                'count': service_count
            }
        
        # Check for repository pattern
        repo_count = category_counts.get('repository_pattern', 0)
        if repo_count > 0:
            insights['repository_pattern'] = {
                'detected': True,
                'strength': min(1.0, repo_count / 3),
                'count': repo_count
            }
        
        # Overall architecture assessment
        total_architectural = sum(category_counts.get(cat, 0) for cat in 
                                ['mvc_controller', 'mvc_model', 'mvc_view', 'service_layer', 'repository_pattern'])
        total_elements = sum(category_counts.values())
        
        if total_elements > 0:
            architectural_ratio = total_architectural / total_elements
            insights['architectural_organization'] = {
                'ratio': architectural_ratio,
                'assessment': self._assess_architectural_organization(architectural_ratio)
            }
        
        return insights
    
    def _assess_architectural_organization(self, ratio: float) -> str:
        """Assess the level of architectural organization"""
        
        if ratio > 0.7:
            return "Highly organized with clear architectural patterns"
        elif ratio > 0.4:
            return "Well-organized with some architectural patterns"
        elif ratio > 0.2:
            return "Moderately organized with basic patterns"
        else:
            return "Limited architectural organization detected"