"""
Advanced AI Engine for enhanced code analysis and intelligent insights
Phase 3 implementation with specialized prompting and multi-model support
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from app.core.model_providers import BaseModelProvider, model_manager
from app.models.repository_schemas import CodeElement, Repository, ElementType
from app.core.config import settings


class AnalysisType(Enum):
    """Types of AI analysis available"""
    CODE_EXPLANATION = "code_explanation"
    IMPROVEMENT_SUGGESTIONS = "improvement_suggestions"
    TEST_GENERATION = "test_generation"
    SECURITY_ANALYSIS = "security_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    REFACTORING_SUGGESTIONS = "refactoring_suggestions"
    DOCUMENTATION_GENERATION = "documentation_generation"
    PATTERN_DETECTION = "pattern_detection"


class ModelComplexity(Enum):
    """Model complexity levels for task assignment"""
    SIMPLE = "simple"      # Basic tasks, fast models
    MEDIUM = "medium"      # Standard analysis, balanced models
    COMPLEX = "complex"    # Deep analysis, powerful models


@dataclass
class AnalysisRequest:
    """Request for AI analysis"""
    analysis_type: AnalysisType
    code_element: CodeElement
    context: Dict[str, Any]
    complexity: ModelComplexity = ModelComplexity.MEDIUM
    streaming: bool = False
    max_tokens: int = 2000


@dataclass
class AnalysisResult:
    """Result of AI analysis"""
    analysis_type: AnalysisType
    element_id: str
    result: Dict[str, Any]
    confidence: float
    processing_time: float
    model_used: str
    timestamp: datetime


class AIPromptTemplates:
    """Specialized prompt templates for different analysis types"""
    
    CODE_EXPLANATION = """
You are an expert code analyst. Analyze the following code and provide a clear, comprehensive explanation.

Code Element: {element_type} - {element_name}
Language: {language}
File: {file_path}

Code:
```{language}
{code_snippet}
```

Context:
- Repository: {repository_name}
- Dependencies: {dependencies}
- Categories: {categories}

Please provide:
1. **Purpose**: What this code does
2. **Functionality**: How it works step by step
3. **Key Components**: Important parts and their roles
4. **Dependencies**: External dependencies and their usage
5. **Complexity**: Complexity assessment and reasoning
6. **Best Practices**: Code quality observations

Format your response as structured JSON:
{{
    "purpose": "Brief description of what the code does",
    "functionality": ["Step 1", "Step 2", "..."],
    "key_components": {{"component": "description"}},
    "dependencies": {{"dependency": "usage"}},
    "complexity": {{"level": "low/medium/high", "reasoning": "explanation"}},
    "best_practices": {{"observations": ["observation1", "observation2"]}},
    "summary": "One-sentence summary"
}}
"""

    IMPROVEMENT_SUGGESTIONS = """
You are a senior software engineer reviewing code for improvements. Analyze the code and suggest specific improvements.

Code Element: {element_type} - {element_name}
Language: {language}
File: {file_path}

Code:
```{language}
{code_snippet}
```

Context:
- Repository: {repository_name}
- Current Categories: {categories}
- Dependencies: {dependencies}

Analyze for:
1. **Performance**: Optimization opportunities
2. **Readability**: Code clarity improvements
3. **Maintainability**: Long-term maintenance considerations
4. **Security**: Potential security issues
5. **Best Practices**: Language/framework best practices
6. **Error Handling**: Exception handling improvements

Provide specific, actionable suggestions with code examples where helpful.

Format as JSON:
{{
    "performance": {{"issues": ["issue1"], "suggestions": ["suggestion1"]}},
    "readability": {{"issues": ["issue1"], "suggestions": ["suggestion1"]}},
    "maintainability": {{"issues": ["issue1"], "suggestions": ["suggestion1"]}},
    "security": {{"issues": ["issue1"], "suggestions": ["suggestion1"]}},
    "best_practices": {{"issues": ["issue1"], "suggestions": ["suggestion1"]}},
    "error_handling": {{"issues": ["issue1"], "suggestions": ["suggestion1"]}},
    "priority_suggestions": ["Most important improvements"],
    "overall_score": {{"current": 7, "potential": 9, "reasoning": "explanation"}}
}}
"""

    TEST_GENERATION = """
You are a test automation expert. Generate comprehensive unit tests for the given code.

Code Element: {element_type} - {element_name}
Language: {language}
File: {file_path}

Code:
```{language}
{code_snippet}
```

Context:
- Repository: {repository_name}
- Dependencies: {dependencies}
- Framework: {framework}

Generate tests that cover:
1. **Happy Path**: Normal operation scenarios
2. **Edge Cases**: Boundary conditions and edge cases
3. **Error Cases**: Exception handling and error conditions
4. **Integration**: Interaction with dependencies
5. **Performance**: Performance-critical scenarios if applicable

Provide:
- Test framework recommendations
- Complete test code
- Test data setup
- Mocking strategies for dependencies

Format as JSON:
{{
    "test_framework": "recommended framework",
    "test_code": "complete test code",
    "test_cases": [
        {{"name": "test_name", "description": "what it tests", "type": "happy_path/edge_case/error_case"}}
    ],
    "setup_code": "test setup and fixtures",
    "mock_strategies": {{"dependency": "mocking approach"}},
    "coverage_analysis": {{"estimated_coverage": 85, "uncovered_scenarios": ["scenario1"]}},
    "additional_recommendations": ["recommendation1"]
}}
"""

    SECURITY_ANALYSIS = """
You are a cybersecurity expert analyzing code for security vulnerabilities and risks.

Code Element: {element_type} - {element_name}
Language: {language}
File: {file_path}

Code:
```{language}
{code_snippet}
```

Context:
- Repository: {repository_name}
- Dependencies: {dependencies}
- Categories: {categories}

Analyze for security issues:
1. **Input Validation**: User input handling
2. **Authentication**: Authentication mechanisms
3. **Authorization**: Access control
4. **Data Protection**: Sensitive data handling
5. **Injection Attacks**: SQL, XSS, command injection
6. **Cryptography**: Encryption and hashing
7. **Dependencies**: Third-party security risks

Provide severity levels (Critical, High, Medium, Low) and remediation steps.

Format as JSON:
{{
    "vulnerabilities": [
        {{
            "type": "vulnerability_type",
            "severity": "Critical/High/Medium/Low",
            "description": "detailed description",
            "location": "specific code location",
            "remediation": "how to fix",
            "cwe_id": "CWE-XXX if applicable"
        }}
    ],
    "security_score": {{"score": 7, "max": 10, "reasoning": "explanation"}},
    "recommendations": ["security improvement recommendations"],
    "compliance_notes": ["relevant compliance considerations"]
}}
"""

    PERFORMANCE_ANALYSIS = """
You are a performance optimization expert. Analyze the code for performance bottlenecks and optimization opportunities.

Code Element: {element_type} - {element_name}
Language: {language}
File: {file_path}

Code:
```{language}
{code_snippet}
```

Context:
- Repository: {repository_name}
- Dependencies: {dependencies}
- Framework: {framework}

Analyze for:
1. **Time Complexity**: Algorithm efficiency
2. **Space Complexity**: Memory usage
3. **I/O Operations**: Database, file, network operations
4. **Caching**: Caching opportunities
5. **Concurrency**: Parallelization potential
6. **Resource Usage**: CPU, memory, network efficiency

Provide specific optimization recommendations with expected impact.

Format as JSON:
{{
    "performance_issues": [
        {{
            "type": "issue_type",
            "severity": "High/Medium/Low",
            "description": "detailed description",
            "impact": "performance impact",
            "optimization": "specific optimization",
            "expected_improvement": "estimated improvement"
        }}
    ],
    "complexity_analysis": {{"time": "O(n)", "space": "O(1)", "reasoning": "explanation"}},
    "optimization_opportunities": ["opportunity1", "opportunity2"],
    "performance_score": {{"current": 6, "potential": 9, "bottlenecks": ["bottleneck1"]}},
    "monitoring_recommendations": ["what to monitor for performance"]
}}
"""


class AIEngine:
    """Advanced AI engine for intelligent code analysis"""
    
    def __init__(self):
        self.model_manager = model_manager
        self.analysis_cache: Dict[str, AnalysisResult] = {}
        self.prompt_templates = AIPromptTemplates()
        # Default model attributes for compatibility
        self.model_name = settings.LEAD_AGENT_MODEL if hasattr(settings, 'LEAD_AGENT_MODEL') else 'llama3.2:1b'
        self.provider_name = settings.AI_PROVIDER if hasattr(settings, 'AI_PROVIDER') else 'ollama'
    
    def _select_model(self, complexity: ModelComplexity, analysis_type: AnalysisType) -> str:
        """Select the best model for the given complexity and analysis type"""
        
        # Use specific model for documentation generation if configured
        if analysis_type == AnalysisType.DOCUMENTATION_GENERATION:
            return settings.DOCUMENTATION_MODEL
        
        # Model selection strategy based on complexity
        if complexity == ModelComplexity.COMPLEX:
            # Use most powerful available model
            if hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY:
                return settings.AVAILABLE_MODELS["claude-4-opus"]
            elif hasattr(settings, 'openai_api_key') and settings.openai_api_key:
                return 'gpt-4'
        
        elif complexity == ModelComplexity.MEDIUM:
            # Use balanced model
            if hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY:
                return settings.LEAD_AGENT_MODEL
        
        # Default to local model for simple tasks or when others unavailable
        return 'llama3.2:1b'
    
    def _build_prompt(self, analysis_type: AnalysisType, request: AnalysisRequest) -> str:
        """Build specialized prompt for analysis type"""
        
        element = request.code_element
        context = request.context
        
        # Common context variables
        prompt_vars = {
            'element_type': element.element_type.value,
            'element_name': element.name,
            'language': context.get('language', 'unknown'),
            'file_path': element.file_path,
            'code_snippet': element.code_snippet,
            'repository_name': context.get('repository_name', 'unknown'),
            'dependencies': ', '.join(context.get('dependencies', [])),
            'categories': ', '.join(element.categories),
            'framework': context.get('framework', 'unknown')
        }
        
        # Select appropriate template
        template_map = {
            AnalysisType.CODE_EXPLANATION: self.prompt_templates.CODE_EXPLANATION,
            AnalysisType.IMPROVEMENT_SUGGESTIONS: self.prompt_templates.IMPROVEMENT_SUGGESTIONS,
            AnalysisType.TEST_GENERATION: self.prompt_templates.TEST_GENERATION,
            AnalysisType.SECURITY_ANALYSIS: self.prompt_templates.SECURITY_ANALYSIS,
            AnalysisType.PERFORMANCE_ANALYSIS: self.prompt_templates.PERFORMANCE_ANALYSIS,
        }
        
        template = template_map.get(analysis_type, self.prompt_templates.CODE_EXPLANATION)
        return template.format(**prompt_vars)
    
    async def analyze_code(self, request: AnalysisRequest) -> AnalysisResult:
        """Perform AI analysis on code element"""
        
        start_time = time.time()
        
        # Check cache first
        cache_key = f"{request.analysis_type.value}:{request.code_element.id}"
        if cache_key in self.analysis_cache:
            cached_result = self.analysis_cache[cache_key]
            # Return cached result if less than 1 hour old
            if (datetime.now() - cached_result.timestamp).seconds < 3600:
                return cached_result
        
        # Select appropriate model
        model_name = self._select_model(request.complexity, request.analysis_type)
        
        # Build specialized prompt
        prompt = self._build_prompt(request.analysis_type, request)
        
        try:
            # Get AI response using model manager
            if request.streaming:
                # For streaming responses, return async generator
                return self._stream_analysis(model_name, prompt, request, start_time)
            else:
                # Standard response
                messages = [{"role": "user", "content": prompt}]
                response, _ = await self.model_manager.call_model(
                    model_name, 
                    messages, 
                    max_tokens=request.max_tokens
                )
                
                # Parse response
                result_data = self._parse_ai_response(response, request.analysis_type)
                
                # Calculate confidence based on response quality
                confidence = self._calculate_confidence(result_data, request.analysis_type)
                
                processing_time = time.time() - start_time
                
                result = AnalysisResult(
                    analysis_type=request.analysis_type,
                    element_id=request.code_element.id,
                    result=result_data,
                    confidence=confidence,
                    processing_time=processing_time,
                    model_used=model_name,
                    timestamp=datetime.now()
                )
                
                # Cache result
                self.analysis_cache[cache_key] = result
                
                return result
                
        except Exception as e:
            # Fallback to simpler analysis if AI fails
            return self._fallback_analysis(request, str(e), time.time() - start_time)
    
    async def _stream_analysis(self, model_name: str, prompt: str, 
                             request: AnalysisRequest, 
                             start_time: float) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream AI analysis results in real-time"""
        
        try:
            # For now, streaming is not implemented with the model manager
            # Fall back to regular response
            messages = [{"role": "user", "content": prompt}]
            response, _ = await self.model_manager.call_model(
                model_name, 
                messages, 
                max_tokens=request.max_tokens
            )
            
            # Yield the complete response as chunks
            yield {
                'type': 'chunk',
                'content': response,
                'analysis_type': request.analysis_type.value,
                'element_id': request.code_element.id,
                'model': model_name
            }
            
            # Final completion message
            yield {
                'type': 'complete',
                'processing_time': time.time() - start_time,
                'analysis_type': request.analysis_type.value,
                'element_id': request.code_element.id
            }
            
        except Exception as e:
            yield {
                'type': 'error',
                'error': str(e),
                'analysis_type': request.analysis_type.value,
                'element_id': request.code_element.id
            }
    
    def _parse_ai_response(self, response: str, analysis_type: AnalysisType) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        
        try:
            # Try to extract JSON from response
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_str = response[json_start:json_end].strip()
            elif '{' in response and '}' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
            else:
                # Fallback to plain text response
                return {'raw_response': response, 'parsed': False}
            
            parsed_data = json.loads(json_str)
            parsed_data['parsed'] = True
            return parsed_data
            
        except json.JSONDecodeError:
            # Return raw response if JSON parsing fails
            return {'raw_response': response, 'parsed': False}
    
    def _calculate_confidence(self, result_data: Dict[str, Any], analysis_type: AnalysisType) -> float:
        """Calculate confidence score for analysis result"""
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence if response was properly parsed
        if result_data.get('parsed', False):
            confidence += 0.3
        
        # Analysis type specific confidence adjustments
        if analysis_type == AnalysisType.CODE_EXPLANATION:
            if 'purpose' in result_data and 'functionality' in result_data:
                confidence += 0.2
        
        elif analysis_type == AnalysisType.IMPROVEMENT_SUGGESTIONS:
            if 'priority_suggestions' in result_data and result_data.get('priority_suggestions'):
                confidence += 0.2
        
        elif analysis_type == AnalysisType.SECURITY_ANALYSIS:
            if 'vulnerabilities' in result_data and 'security_score' in result_data:
                confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _fallback_analysis(self, request: AnalysisRequest, error: str, processing_time: float) -> AnalysisResult:
        """Provide fallback analysis when AI fails"""
        
        element = request.code_element
        
        fallback_data = {
            'error': f"AI analysis failed: {error}",
            'fallback_analysis': {
                'element_type': element.element_type.value,
                'element_name': element.name,
                'file_path': element.file_path,
                'basic_info': {
                    'lines_of_code': len(element.code_snippet.split('\n')) if element.code_snippet else 0,
                    'categories': element.categories,
                    'dependencies': len(element.dependencies)
                }
            },
            'recommendations': [
                'Manual code review recommended',
                'Consider using static analysis tools',
                'Check AI service availability'
            ]
        }
        
        return AnalysisResult(
            analysis_type=request.analysis_type,
            element_id=element.id,
            result=fallback_data,
            confidence=0.1,  # Low confidence for fallback
            processing_time=processing_time,
            model_used='fallback',
            timestamp=datetime.now()
        )
    
    async def batch_analyze(self, requests: List[AnalysisRequest]) -> List[AnalysisResult]:
        """Perform batch analysis on multiple code elements"""
        
        # Process requests concurrently
        tasks = [self.analyze_code(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create error result
                error_result = self._fallback_analysis(
                    requests[i], 
                    str(result), 
                    0.0
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get statistics about AI analysis usage"""
        
        if not self.analysis_cache:
            return {'total_analyses': 0}
        
        results = list(self.analysis_cache.values())
        
        return {
            'total_analyses': len(results),
            'analysis_types': {
                analysis_type.value: len([r for r in results if r.analysis_type == analysis_type])
                for analysis_type in AnalysisType
            },
            'average_confidence': sum(r.confidence for r in results) / len(results),
            'average_processing_time': sum(r.processing_time for r in results) / len(results),
            'models_used': {
                model: len([r for r in results if r.model_used == model])
                for model in set(r.model_used for r in results)
            },
            'cache_hit_rate': 0.0  # TODO: Implement cache hit tracking
        }
    
    def clear_cache(self):
        """Clear analysis cache"""
        self.analysis_cache.clear()


# Global AI engine instance
ai_engine = AIEngine()