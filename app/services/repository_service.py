"""
Repository management service for Kenobi agent
"""
import os
import uuid
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.repository_schemas import (
    Repository, RepositoryAnalysis, ParsedFile, LanguageType
)
from app.tools.code_parser import CodeParser

class RepositoryService:
    """Service for managing and analyzing repositories"""
    
    def __init__(self):
        self.code_parser = CodeParser()
        self.repositories: Dict[str, Repository] = {}
        self.analyses: Dict[str, RepositoryAnalysis] = {}
    
    async def clone_repository(self, repo_url: str, local_path: Optional[str] = None) -> Repository:
        """Clone a repository from URL"""
        if local_path is None:
            # Generate a local path based on repo name
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            local_path = f"/tmp/kenobi_repos/{repo_name}"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        try:
            # Clone the repository
            subprocess.run(['git', 'clone', repo_url, local_path], check=True, capture_output=True)
            
            # Create repository object
            repo = await self.scan_local_directory(local_path, repo_url)
            return repo
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to clone repository: {e.stderr.decode()}")
    
    async def scan_local_directory(self, path: str, url: Optional[str] = None) -> Repository:
        """Scan a local directory and create repository metadata"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Directory not found: {path}")
        
        repo_id = str(uuid.uuid4())
        repo_name = os.path.basename(path)
        
        # Detect primary language and framework
        language, framework = self._detect_language_and_framework(path)
        
        # Calculate repository statistics
        file_count, line_count, size_bytes = self._calculate_repo_stats(path)
        
        repository = Repository(
            id=repo_id,
            name=repo_name,
            url=url,
            local_path=path,
            language=language,
            framework=framework,
            indexed_at=datetime.utcnow(),
            file_count=file_count,
            line_count=line_count,
            size_bytes=size_bytes
        )
        
        # Store repository
        self.repositories[repo_id] = repository
        
        return repository
    
    async def get_repository_metadata(self, repo_id: str) -> Optional[Repository]:
        """Get repository metadata by ID"""
        return self.repositories.get(repo_id)
    
    async def list_repositories(self) -> List[Repository]:
        """List all managed repositories"""
        return list(self.repositories.values())
    
    async def analyze_repository(self, repo_id: str) -> RepositoryAnalysis:
        """Perform complete analysis of a repository"""
        repository = self.repositories.get(repo_id)
        if not repository:
            raise ValueError(f"Repository not found: {repo_id}")
        
        # Check if analysis already exists and is recent
        if repo_id in self.analyses:
            existing = self.analyses[repo_id]
            if existing.repository.indexed_at >= repository.indexed_at:
                return existing
        
        # Perform analysis
        files = await self._analyze_files(repository)
        dependency_graph = self._build_dependency_graph(files)
        metrics = self._calculate_metrics(files, dependency_graph)
        categories_used = self._extract_categories(files)
        frameworks_detected = self._detect_frameworks(files)
        
        analysis = RepositoryAnalysis(
            repository=repository,
            files=files,
            dependency_graph=dependency_graph,
            metrics=metrics,
            categories_used=categories_used,
            frameworks_detected=frameworks_detected
        )
        
        # Store analysis
        self.analyses[repo_id] = analysis
        
        return analysis
    
    async def _analyze_files(self, repository: Repository) -> List[ParsedFile]:
        """Analyze all code files in the repository"""
        files = []
        repo_path = Path(repository.local_path)
        
        # Define file extensions to analyze
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cs', '.go'}
        
        # Walk through repository
        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in code_extensions:
                # Skip common directories to ignore
                if any(part in str(file_path) for part in ['.git', 'node_modules', '__pycache__', '.venv', 'venv']):
                    continue
                
                try:
                    # Parse the file
                    relative_path = str(file_path.relative_to(repo_path))
                    parsed_file = self.code_parser.parse_file(str(file_path))
                    
                    # Update file path to be relative
                    parsed_file.file_path = relative_path
                    
                    # Update element repository IDs
                    for element in parsed_file.elements:
                        element.repository_id = repository.id
                        element.id = f"{repository.id}:{relative_path}:{element.name}"
                        element.full_name = f"{repository.name}:{relative_path}:{element.name}"
                    
                    files.append(parsed_file)
                    
                except Exception as e:
                    # Create a file with error information
                    error_file = ParsedFile(
                        file_path=str(file_path.relative_to(repo_path)),
                        language=LanguageType.UNKNOWN,
                        parse_errors=[f"Analysis failed: {str(e)}"]
                    )
                    files.append(error_file)
        
        return files
    
    def _detect_language_and_framework(self, path: str) -> tuple[LanguageType, Optional[str]]:
        """Detect primary language and framework from repository structure"""
        repo_path = Path(path)
        
        # Count files by extension
        extension_counts = {}
        framework_indicators = {}
        
        for file_path in repo_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                extension_counts[ext] = extension_counts.get(ext, 0) + 1
                
                # Check for framework indicators
                if file_path.name == 'package.json':
                    framework_indicators['node'] = True
                elif file_path.name == 'requirements.txt':
                    framework_indicators['python'] = True
                elif file_path.name == 'pom.xml':
                    framework_indicators['java_maven'] = True
                elif file_path.name == 'go.mod':
                    framework_indicators['go'] = True
                elif file_path.name == 'Cargo.toml':
                    framework_indicators['rust'] = True
        
        # Determine primary language
        language_mapping = {
            '.py': LanguageType.PYTHON,
            '.js': LanguageType.JAVASCRIPT,
            '.jsx': LanguageType.JAVASCRIPT,
            '.ts': LanguageType.TYPESCRIPT,
            '.tsx': LanguageType.TYPESCRIPT,
            '.java': LanguageType.JAVA,
            '.cs': LanguageType.CSHARP,
            '.go': LanguageType.GO,
        }
        
        primary_language = LanguageType.UNKNOWN
        max_count = 0
        
        for ext, count in extension_counts.items():
            if ext in language_mapping and count > max_count:
                max_count = count
                primary_language = language_mapping[ext]
        
        # Detect framework
        framework = None
        if 'node' in framework_indicators:
            if primary_language in [LanguageType.JAVASCRIPT, LanguageType.TYPESCRIPT]:
                # Try to detect specific framework
                package_json_path = repo_path / 'package.json'
                if package_json_path.exists():
                    try:
                        import json
                        with open(package_json_path) as f:
                            package_data = json.load(f)
                        
                        dependencies = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
                        
                        if 'react' in dependencies:
                            framework = 'React'
                        elif '@angular/core' in dependencies:
                            framework = 'Angular'
                        elif 'vue' in dependencies:
                            framework = 'Vue'
                        elif 'express' in dependencies:
                            framework = 'Express'
                        else:
                            framework = 'Node.js'
                    except:
                        framework = 'Node.js'
        elif 'python' in framework_indicators:
            framework = 'Python'
        elif 'java_maven' in framework_indicators:
            framework = 'Maven'
        elif 'go' in framework_indicators:
            framework = 'Go'
        
        return primary_language, framework
    
    def _calculate_repo_stats(self, path: str) -> tuple[int, int, int]:
        """Calculate repository statistics"""
        repo_path = Path(path)
        file_count = 0
        line_count = 0
        size_bytes = 0
        
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cs', '.go'}
        
        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in code_extensions:
                # Skip common directories to ignore
                if any(part in str(file_path) for part in ['.git', 'node_modules', '__pycache__']):
                    continue
                
                try:
                    file_count += 1
                    size_bytes += file_path.stat().st_size
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        line_count += len(f.readlines())
                except:
                    pass  # Skip files that can't be read
        
        return file_count, line_count, size_bytes
    
    def _build_dependency_graph(self, files: List[ParsedFile]):
        """Build dependency graph from parsed files"""
        from app.models.repository_schemas import DependencyGraph, DependencyEdge
        
        # For now, return a simple dependency graph
        # This will be enhanced in Phase 2
        nodes = []
        edges = []
        
        for file in files:
            for element in file.elements:
                nodes.append(element.id)
        
        return DependencyGraph(
            repository_id=files[0].elements[0].repository_id if files and files[0].elements else "",
            nodes=nodes,
            edges=edges,
            circular_dependencies=[]
        )
    
    def _calculate_metrics(self, files: List[ParsedFile], dependency_graph) -> Dict[str, Any]:
        """Calculate repository metrics"""
        total_elements = sum(len(f.elements) for f in files)
        total_files = len(files)
        total_lines = sum(f.line_count for f in files)
        
        # Count by element type
        element_type_counts = {}
        for file in files:
            for element in file.elements:
                element_type_counts[element.element_type.value] = element_type_counts.get(element.element_type.value, 0) + 1
        
        # Count by language
        language_counts = {}
        for file in files:
            language_counts[file.language.value] = language_counts.get(file.language.value, 0) + 1
        
        return {
            'total_elements': total_elements,
            'total_files': total_files,
            'total_lines': total_lines,
            'element_type_counts': element_type_counts,
            'language_counts': language_counts,
            'avg_elements_per_file': total_elements / total_files if total_files > 0 else 0,
            'avg_lines_per_file': total_lines / total_files if total_files > 0 else 0
        }
    
    def _extract_categories(self, files: List[ParsedFile]) -> List[str]:
        """Extract all categories used in the codebase"""
        categories = set()
        for file in files:
            for element in file.elements:
                categories.update(element.categories)
        return list(categories)
    
    def _detect_frameworks(self, files: List[ParsedFile]) -> List[str]:
        """Detect frameworks used in the codebase"""
        frameworks = set()
        
        for file in files:
            for import_info in file.imports:
                module = import_info.module.lower()
                
                # Framework detection based on imports
                if 'react' in module:
                    frameworks.add('React')
                elif 'angular' in module or '@angular' in module:
                    frameworks.add('Angular')
                elif 'vue' in module:
                    frameworks.add('Vue')
                elif 'express' in module:
                    frameworks.add('Express')
                elif 'django' in module:
                    frameworks.add('Django')
                elif 'flask' in module:
                    frameworks.add('Flask')
                elif 'spring' in module:
                    frameworks.add('Spring')
        
        return list(frameworks)