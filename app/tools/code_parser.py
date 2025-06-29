"""
Multi-language code parser for extracting code elements and dependencies
"""
import ast
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from app.models.repository_schemas import (
    ParsedFile, CodeElement, ImportInfo, LanguageType, ElementType
)

class CodeParser:
    """Multi-language code parser"""
    
    def __init__(self):
        self.language_extensions = {
            '.py': LanguageType.PYTHON,
            '.js': LanguageType.JAVASCRIPT,
            '.jsx': LanguageType.JAVASCRIPT,
            '.ts': LanguageType.TYPESCRIPT,
            '.tsx': LanguageType.TYPESCRIPT,
            '.java': LanguageType.JAVA,
            '.cs': LanguageType.CSHARP,
            '.go': LanguageType.GO,
            '.r': LanguageType.R,
            '.R': LanguageType.R,
            '.ipynb': LanguageType.JUPYTER,
        }
    
    def detect_language(self, file_path: str) -> LanguageType:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        return self.language_extensions.get(ext, LanguageType.UNKNOWN)
    
    def parse_file(self, file_path: str, content: Optional[str] = None) -> ParsedFile:
        """Parse a single file and extract code elements"""
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                return ParsedFile(
                    file_path=file_path,
                    language=LanguageType.UNKNOWN,
                    parse_errors=[f"Failed to read file: {str(e)}"]
                )
        
        language = self.detect_language(file_path)
        
        # Get file stats
        try:
            stat = os.stat(file_path)
            size_bytes = stat.st_size
        except:
            size_bytes = len(content.encode('utf-8'))
        
        line_count = len(content.splitlines())
        
        # Parse based on language
        elements = []
        imports = []
        parse_errors = []
        
        try:
            if language == LanguageType.PYTHON:
                elements, imports = self._parse_python(file_path, content)
            elif language in [LanguageType.JAVASCRIPT, LanguageType.TYPESCRIPT]:
                elements, imports = self._parse_javascript(file_path, content)
            elif language == LanguageType.JAVA:
                elements, imports = self._parse_java(file_path, content)
            elif language == LanguageType.GO:
                elements, imports = self._parse_go(file_path, content)
            elif language == LanguageType.R:
                elements, imports = self._parse_r(file_path, content)
            elif language == LanguageType.JUPYTER:
                elements, imports = self._parse_jupyter(file_path, content)
            else:
                # For unsupported languages, do basic text analysis
                elements = self._parse_generic(file_path, content)
                
        except Exception as e:
            parse_errors.append(f"Parsing error: {str(e)}")
        
        return ParsedFile(
            file_path=file_path,
            language=language,
            elements=elements,
            imports=imports,
            line_count=line_count,
            size_bytes=size_bytes,
            parse_errors=parse_errors
        )
    
    def _parse_python(self, file_path: str, content: str) -> Tuple[List[CodeElement], List[ImportInfo]]:
        """Parse Python file using AST"""
        elements = []
        imports = []
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            # Return empty lists if syntax error
            return elements, imports
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(ImportInfo(
                        module=alias.name,
                        alias=alias.asname,
                        is_local=self._is_local_import(alias.name),
                        import_type="import"
                    ))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        imports.append(ImportInfo(
                            module=f"{node.module}.{alias.name}",
                            alias=alias.asname,
                            is_local=self._is_local_import(node.module),
                            import_type="from"
                        ))
        
        # Extract code elements
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                elements.append(self._create_python_element(
                    file_path, node, ElementType.CLASS, content
                ))
            elif isinstance(node, ast.FunctionDef):
                # Check if it's a method (inside a class)
                element_type = ElementType.METHOD if self._is_method(node, tree) else ElementType.FUNCTION
                elements.append(self._create_python_element(
                    file_path, node, element_type, content
                ))
        
        return elements, imports
    
    def _parse_javascript(self, file_path: str, content: str) -> Tuple[List[CodeElement], List[ImportInfo]]:
        """Parse JavaScript/TypeScript file using regex patterns"""
        elements = []
        imports = []
        
        # Extract imports (ES6 and CommonJS)
        import_patterns = [
            r'import\s+(?:{[^}]+}|\w+|\*\s+as\s+\w+)\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'const\s+(?:{[^}]+}|\w+)\s*=\s*require\([\'"]([^\'"]+)[\'"]\)',
            r'import\s*\([\'"]([^\'"]+)[\'"]\)',
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                module = match.group(1)
                imports.append(ImportInfo(
                    module=module,
                    alias=None,
                    is_local=self._is_local_import(module),
                    import_type="import"
                ))
        
        # Extract functions
        function_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))'
        for match in re.finditer(function_pattern, content, re.MULTILINE):
            name = match.group(1) or match.group(2)
            if name:
                line_num = content[:match.start()].count('\n') + 1
                elements.append(CodeElement(
                    id=f"{file_path}:{name}",
                    repository_id="",  # Will be set later
                    file_path=file_path,
                    element_type=ElementType.FUNCTION,
                    name=name,
                    full_name=f"{file_path}:{name}",
                    start_line=line_num,
                    end_line=line_num,  # Simplified
                    code_snippet=self._extract_snippet(content, match.start(), match.end())
                ))
        
        # Extract classes
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?'
        for match in re.finditer(class_pattern, content):
            name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            elements.append(CodeElement(
                id=f"{file_path}:{name}",
                repository_id="",
                file_path=file_path,
                element_type=ElementType.CLASS,
                name=name,
                full_name=f"{file_path}:{name}",
                start_line=line_num,
                end_line=line_num,
                code_snippet=self._extract_snippet(content, match.start(), match.end())
            ))
        
        # Extract React components
        component_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)\s*=>|function)'
        for match in re.finditer(component_pattern, content):
            name = match.group(1)
            # Check if it looks like a React component (starts with capital letter)
            if name[0].isupper():
                line_num = content[:match.start()].count('\n') + 1
                elements.append(CodeElement(
                    id=f"{file_path}:{name}",
                    repository_id="",
                    file_path=file_path,
                    element_type=ElementType.COMPONENT,
                    name=name,
                    full_name=f"{file_path}:{name}",
                    start_line=line_num,
                    end_line=line_num,
                    code_snippet=self._extract_snippet(content, match.start(), match.end())
                ))
        
        return elements, imports
    
    def _parse_java(self, file_path: str, content: str) -> Tuple[List[CodeElement], List[ImportInfo]]:
        """Parse Java file using regex patterns"""
        elements = []
        imports = []
        
        # Extract imports
        import_pattern = r'import\s+(?:static\s+)?([^;]+);'
        for match in re.finditer(import_pattern, content):
            module = match.group(1).strip()
            imports.append(ImportInfo(
                module=module,
                alias=None,
                is_local=self._is_local_import(module),
                import_type="import"
            ))
        
        # Extract classes
        class_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+|final\s+)?class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            elements.append(CodeElement(
                id=f"{file_path}:{name}",
                repository_id="",
                file_path=file_path,
                element_type=ElementType.CLASS,
                name=name,
                full_name=f"{file_path}:{name}",
                start_line=line_num,
                end_line=line_num,
                code_snippet=self._extract_snippet(content, match.start(), match.end())
            ))
        
        # Extract methods
        method_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*{'
        for match in re.finditer(method_pattern, content):
            name = match.group(1)
            # Skip constructors and common keywords
            if name not in ['if', 'for', 'while', 'switch', 'try', 'catch']:
                line_num = content[:match.start()].count('\n') + 1
                elements.append(CodeElement(
                    id=f"{file_path}:{name}",
                    repository_id="",
                    file_path=file_path,
                    element_type=ElementType.METHOD,
                    name=name,
                    full_name=f"{file_path}:{name}",
                    start_line=line_num,
                    end_line=line_num,
                    code_snippet=self._extract_snippet(content, match.start(), match.end())
                ))
        
        return elements, imports
    
    def _parse_go(self, file_path: str, content: str) -> Tuple[List[CodeElement], List[ImportInfo]]:
        """Parse Go file using regex patterns"""
        elements = []
        imports = []
        
        # Extract imports
        import_pattern = r'import\s+(?:\(\s*([^)]+)\s*\)|"([^"]+)")'
        for match in re.finditer(import_pattern, content, re.DOTALL):
            if match.group(1):  # Multi-line import
                for line in match.group(1).split('\n'):
                    line = line.strip().strip('"')
                    if line:
                        imports.append(ImportInfo(
                            module=line,
                            alias=None,
                            is_local=self._is_local_import(line),
                            import_type="import"
                        ))
            elif match.group(2):  # Single import
                imports.append(ImportInfo(
                    module=match.group(2),
                    alias=None,
                    is_local=self._is_local_import(match.group(2)),
                    import_type="import"
                ))
        
        # Extract functions
        func_pattern = r'func\s+(?:\([^)]*\)\s+)?(\w+)\s*\([^)]*\)'
        for match in re.finditer(func_pattern, content):
            name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            elements.append(CodeElement(
                id=f"{file_path}:{name}",
                repository_id="",
                file_path=file_path,
                element_type=ElementType.FUNCTION,
                name=name,
                full_name=f"{file_path}:{name}",
                start_line=line_num,
                end_line=line_num,
                code_snippet=self._extract_snippet(content, match.start(), match.end())
            ))
        
        # Extract types/structs
        type_pattern = r'type\s+(\w+)\s+struct'
        for match in re.finditer(type_pattern, content):
            name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            elements.append(CodeElement(
                id=f"{file_path}:{name}",
                repository_id="",
                file_path=file_path,
                element_type=ElementType.CLASS,  # Treat struct as class
                name=name,
                full_name=f"{file_path}:{name}",
                start_line=line_num,
                end_line=line_num,
                code_snippet=self._extract_snippet(content, match.start(), match.end())
            ))
        
        return elements, imports
    
    def _parse_r(self, file_path: str, content: str) -> Tuple[List[CodeElement], List[ImportInfo]]:
        """Parse R file using regex patterns"""
        elements = []
        imports = []
        
        # Extract library imports
        import_patterns = [
            r'library\s*\(\s*([^)]+)\s*\)',
            r'require\s*\(\s*([^)]+)\s*\)',
            r'source\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                module = match.group(1).strip('\'"')
                imports.append(ImportInfo(
                    module=module,
                    alias=None,
                    is_local=module.endswith('.R') or module.endswith('.r'),
                    import_type="library"
                ))
        
        # Extract function definitions
        function_pattern = r'(\w+)\s*<-\s*function\s*\([^)]*\)'
        for match in re.finditer(function_pattern, content):
            name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            elements.append(CodeElement(
                id=f"{file_path}:{name}",
                repository_id="",
                file_path=file_path,
                element_type=ElementType.FUNCTION,
                name=name,
                full_name=f"{file_path}:{name}",
                start_line=line_num,
                end_line=line_num,
                code_snippet=self._extract_snippet(content, match.start(), match.end() + 50)
            ))
        
        # Extract variable assignments (for major data objects)
        variable_pattern = r'(\w+)\s*<-\s*(?!function)'
        for match in re.finditer(variable_pattern, content):
            name = match.group(1)
            # Skip common temporary variables
            if len(name) > 2 and name not in ['i', 'j', 'k', 'x', 'y', 'z', 'tmp', 'temp']:
                line_num = content[:match.start()].count('\n') + 1
                elements.append(CodeElement(
                    id=f"{file_path}:{name}",
                    repository_id="",
                    file_path=file_path,
                    element_type=ElementType.VARIABLE,
                    name=name,
                    full_name=f"{file_path}:{name}",
                    start_line=line_num,
                    end_line=line_num,
                    code_snippet=self._extract_snippet(content, match.start(), match.end() + 30)
                ))
        
        return elements, imports
    
    def _parse_jupyter(self, file_path: str, content: str) -> Tuple[List[CodeElement], List[ImportInfo]]:
        """Parse Jupyter notebook file"""
        import json
        elements = []
        imports = []
        
        try:
            notebook = json.loads(content)
            cells = notebook.get('cells', [])
            
            for i, cell in enumerate(cells):
                if cell.get('cell_type') == 'code':
                    cell_source = ''.join(cell.get('source', []))
                    if cell_source.strip():
                        # Parse each code cell as Python
                        try:
                            cell_elements, cell_imports = self._parse_python(f"{file_path}:cell_{i}", cell_source)
                            elements.extend(cell_elements)
                            imports.extend(cell_imports)
                        except:
                            # If Python parsing fails, create a generic code element
                            elements.append(CodeElement(
                                id=f"{file_path}:cell_{i}",
                                repository_id="",
                                file_path=file_path,
                                element_type=ElementType.FUNCTION,
                                name=f"cell_{i}",
                                full_name=f"{file_path}:cell_{i}",
                                start_line=i + 1,
                                end_line=i + 1,
                                code_snippet=cell_source[:200] + "..." if len(cell_source) > 200 else cell_source
                            ))
                            
        except json.JSONDecodeError:
            # If JSON parsing fails, treat as generic file
            pass
            
        return elements, imports
    
    def _parse_generic(self, file_path: str, content: str) -> List[CodeElement]:
        """Generic parsing for unsupported languages"""
        elements = []
        
        # Look for function-like patterns
        patterns = [
            r'def\s+(\w+)',  # Python-like
            r'function\s+(\w+)',  # JavaScript-like
            r'(\w+)\s*\([^)]*\)\s*{',  # C-like
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                elements.append(CodeElement(
                    id=f"{file_path}:{name}",
                    repository_id="",
                    file_path=file_path,
                    element_type=ElementType.FUNCTION,
                    name=name,
                    full_name=f"{file_path}:{name}",
                    start_line=line_num,
                    end_line=line_num,
                    code_snippet=self._extract_snippet(content, match.start(), match.end())
                ))
        
        return elements
    
    def _create_python_element(self, file_path: str, node: ast.AST, element_type: ElementType, content: str) -> CodeElement:
        """Create CodeElement from Python AST node"""
        name = node.name
        line_start = node.lineno
        line_end = getattr(node, 'end_lineno', line_start)
        
        # Extract code snippet
        lines = content.splitlines()
        snippet_lines = lines[line_start-1:line_end] if line_end else [lines[line_start-1]]
        snippet = '\n'.join(snippet_lines)
        
        return CodeElement(
            id=f"{file_path}:{name}",
            repository_id="",  # Will be set later
            file_path=file_path,
            element_type=element_type,
            name=name,
            full_name=f"{file_path}:{name}",
            start_line=line_start,
            end_line=line_end or line_start,
            code_snippet=snippet[:500]  # Limit snippet size
        )
    
    def _is_method(self, node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if a function is a method (inside a class)"""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                if node in parent.body:
                    return True
        return False
    
    def _is_local_import(self, module: str) -> bool:
        """Determine if an import is local to the project"""
        # Simple heuristic: local imports start with . or don't contain common package prefixes
        if module.startswith('.'):
            return True
        
        common_packages = [
            'os', 'sys', 'json', 'datetime', 'typing', 'collections',
            'react', 'angular', 'vue', 'express', 'lodash',
            'java.util', 'java.io', 'javax',
            'fmt', 'os', 'io', 'net/http'
        ]
        
        for pkg in common_packages:
            if module.startswith(pkg):
                return False
        
        return True
    
    def _extract_snippet(self, content: str, start: int, end: int, max_length: int = 200) -> str:
        """Extract a code snippet around the given position"""
        snippet = content[start:end]
        if len(snippet) > max_length:
            snippet = snippet[:max_length] + "..."
        return snippet