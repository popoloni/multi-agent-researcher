"""
Repository management service for Kenobi agent
"""
import os
import uuid
import subprocess
import asyncio
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime

from app.models.repository_schemas import (
    Repository, RepositoryAnalysis, ParsedFile, LanguageType, CloneStatus, CloneProgressUpdate
)
from app.tools.code_parser import CodeParser
from app.services.github_service import github_service
from app.services.database_service import database_service
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

class RepositoryService:
    """Service for managing and analyzing repositories"""
    
    def __init__(self):
        self.code_parser = CodeParser()
        self.repositories: Dict[str, Repository] = {}  # Keep for cache
        self.analyses: Dict[str, RepositoryAnalysis] = {}
        self.clone_progress_callbacks: Dict[str, Callable] = {}
        
        # NEW: Add database service integration
        self.db_service = database_service
        self.cache_service = cache_service
        self._initialized = False
    
    async def initialize(self):
        """Initialize database and migrate existing data"""
        if self._initialized:
            return
            
        try:
            # Initialize database service
            await self.db_service.initialize()
            
            # Migrate existing in-memory repositories to database
            await self._migrate_existing_repositories()
            
            # Load existing repositories from database into cache
            await self._load_repositories_from_database()
            
            self._initialized = True
            logger.info("Repository service initialized with database integration")
            
        except Exception as e:
            logger.error(f"Failed to initialize repository service: {e}")
            # Continue with in-memory storage as fallback
            logger.warning("Continuing with in-memory storage only")
    
    async def _migrate_existing_repositories(self):
        """Migrate existing in-memory repositories to database"""
        if not self.repositories:
            return
            
        migrated_count = 0
        for repo_id, repository in self.repositories.items():
            try:
                await self.db_service.save_repository(repository)
                migrated_count += 1
                logger.info(f"Migrated repository {repo_id} to database")
            except Exception as e:
                logger.error(f"Failed to migrate repository {repo_id}: {e}")
        
        logger.info(f"Migrated {migrated_count} repositories to database")
    
    async def _load_repositories_from_database(self):
        """Load existing repositories from database into cache"""
        try:
            db_repositories = await self.db_service.list_repositories()
            for repository in db_repositories:
                self.repositories[repository.id] = repository
            
            logger.info(f"Loaded {len(db_repositories)} repositories from database into cache")
            
        except Exception as e:
            logger.error(f"Failed to load repositories from database: {e}")
    
    async def _ensure_initialized(self):
        """Ensure the service is initialized before operations"""
        if not self._initialized:
            await self.initialize()
    
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
    
    async def clone_github_repository(
        self, 
        owner: str, 
        repo: str, 
        branch: str = "main",
        local_name: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> Repository:
        """
        Clone a GitHub repository with enhanced progress tracking and error handling
        
        Args:
            owner: GitHub repository owner
            repo: Repository name
            branch: Branch to clone (default: main)
            local_name: Local directory name (default: repo name)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Repository object
        """
        repo_id = str(uuid.uuid4())
        
        try:
            # Update progress: Starting
            await self._update_clone_progress(
                repo_id, CloneStatus.PENDING, 0.0, 
                "Validating repository access...", progress_callback
            )
            
            # Validate repository access
            if not await github_service.validate_repository_access(owner, repo):
                raise Exception(f"Repository {owner}/{repo} not found or not accessible")
            
            # Get repository metadata
            github_metadata = await github_service.get_repository_info(owner, repo)
            
            # Update progress: Preparing
            await self._update_clone_progress(
                repo_id, CloneStatus.CLONING, 10.0,
                "Preparing clone operation...", progress_callback
            )
            
            # Prepare local path with unique directory
            local_dir_name = local_name or repo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_dir = f"{local_dir_name}_{owner}_{timestamp}"
            local_path = f"/tmp/kenobi_repos/{unique_dir}"
            
            # Clean up existing directory if it exists
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
            
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Update progress: Cloning
            await self._update_clone_progress(
                repo_id, CloneStatus.CLONING, 20.0,
                f"Cloning repository from GitHub...", progress_callback
            )
            
            # Clone repository with progress tracking
            clone_url = github_metadata['clone_url']
            await self._clone_with_progress(
                clone_url, local_path, branch, repo_id, progress_callback
            )
            
            # Update progress: Analyzing
            await self._update_clone_progress(
                repo_id, CloneStatus.CLONING, 80.0,
                "Analyzing repository structure...", progress_callback
            )
            
            # Create repository object with GitHub metadata
            repository = await self._create_repository_from_path(
                local_path, clone_url, repo_id, owner, repo, branch, github_metadata
            )
            
            # Update progress: Completed
            await self._update_clone_progress(
                repo_id, CloneStatus.COMPLETED, 100.0,
                "Repository cloned successfully!", progress_callback
            )
            
            return repository
            
        except Exception as e:
            # Update progress: Failed
            await self._update_clone_progress(
                repo_id, CloneStatus.FAILED, 0.0,
                f"Clone failed: {str(e)}", progress_callback, error=str(e)
            )
            
            # Clean up on failure
            local_path = f"/tmp/kenobi_repos/{local_name or repo}"
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
            
            raise Exception(f"Failed to clone GitHub repository {owner}/{repo}: {str(e)}")
    
    async def _clone_with_progress(
        self, 
        clone_url: str, 
        local_path: str, 
        branch: str,
        repo_id: str,
        progress_callback: Optional[Callable] = None
    ):
        """Clone repository with progress tracking"""
        try:
            # Clone with specific branch
            cmd = ['git', 'clone', '--branch', branch, '--single-branch', clone_url, local_path]
            
            # Run git clone
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Monitor progress (simplified - git clone doesn't provide detailed progress)
            progress_steps = [30.0, 40.0, 50.0, 60.0, 70.0]
            for i, progress in enumerate(progress_steps):
                await asyncio.sleep(0.5)  # Small delay to simulate progress
                await self._update_clone_progress(
                    repo_id, CloneStatus.CLONING, progress,
                    f"Downloading repository files... ({i+1}/{len(progress_steps)})",
                    progress_callback
                )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown git error"
                raise Exception(f"Git clone failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Clone with progress failed: {str(e)}")
            raise
    
    async def _create_repository_from_path(
        self,
        local_path: str,
        url: str,
        repo_id: str,
        github_owner: str,
        github_repo: str,
        branch: str,
        github_metadata: Dict[str, Any]
    ) -> Repository:
        """Create repository object from local path with GitHub metadata"""
        
        repo_name = os.path.basename(local_path)
        
        # Detect primary language and framework
        language, framework = self._detect_language_and_framework(local_path)
        
        # Calculate repository statistics
        file_count, line_count, size_bytes = self._calculate_repo_stats(local_path)
        
        # Create repository with GitHub metadata
        repository = Repository(
            id=repo_id,
            name=repo_name,
            url=url,
            local_path=local_path,
            language=language,
            framework=framework,
            description=github_metadata.get('description'),
            indexed_at=datetime.utcnow(),
            file_count=file_count,
            line_count=line_count,
            size_bytes=size_bytes,
            github_owner=github_owner,
            github_repo=github_repo,
            clone_status=CloneStatus.COMPLETED,
            clone_progress=100.0,
            github_metadata=github_metadata,
            branch=branch
        )
        
        # Save to database first
        try:
            await self.db_service.save_repository(repository)
            logger.debug(f"Saved cloned repository {repo_id} to database")
        except Exception as e:
            logger.error(f"Failed to save cloned repository {repo_id} to database: {e}")
            # Continue with in-memory storage
        
        # Store repository in cache
        self.repositories[repo_id] = repository
        return repository
    
    async def _update_clone_progress(
        self,
        repo_id: str,
        status: CloneStatus,
        progress: float,
        message: str,
        progress_callback: Optional[Callable] = None,
        error: Optional[str] = None
    ):
        """Update clone progress and notify callback if provided"""
        
        progress_update = CloneProgressUpdate(
            repository_id=repo_id,
            status=status,
            progress=progress,
            message=message,
            error=error
        )
        
        # Update repository if it exists
        if repo_id in self.repositories:
            self.repositories[repo_id].clone_status = status
            self.repositories[repo_id].clone_progress = progress
        
        # Call progress callback if provided
        if progress_callback:
            try:
                await progress_callback(progress_update)
            except Exception as e:
                logger.error(f"Progress callback failed: {str(e)}")
        
        logger.info(f"Clone progress [{repo_id}]: {status.value} - {progress:.1f}% - {message}")
    
    def register_clone_progress_callback(self, repo_id: str, callback: Callable):
        """Register a progress callback for a specific repository clone"""
        self.clone_progress_callbacks[repo_id] = callback
    
    def unregister_clone_progress_callback(self, repo_id: str):
        """Unregister a progress callback"""
        self.clone_progress_callbacks.pop(repo_id, None)
    
    async def get_clone_status(self, repo_id: str) -> Optional[CloneProgressUpdate]:
        """Get current clone status for a repository"""
        if repo_id in self.repositories:
            repo = self.repositories[repo_id]
            return CloneProgressUpdate(
                repository_id=repo_id,
                status=repo.clone_status,
                progress=repo.clone_progress,
                message=f"Repository {repo.name} - {repo.clone_status.value}",
                error=None
            )
        return None
    
    async def cancel_clone(self, repo_id: str) -> bool:
        """Cancel an ongoing clone operation"""
        try:
            # Update status to failed
            await self._update_clone_progress(
                repo_id, CloneStatus.FAILED, 0.0,
                "Clone operation cancelled by user"
            )
            
            # Clean up partial clone if it exists
            if repo_id in self.repositories:
                repo = self.repositories[repo_id]
                if os.path.exists(repo.local_path):
                    shutil.rmtree(repo.local_path)
                
                # Remove from repositories
                del self.repositories[repo_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel clone {repo_id}: {str(e)}")
            return False
    
    async def scan_local_directory(self, path: str, url: Optional[str] = None) -> Repository:
        """Scan a local directory and create repository metadata"""
        await self._ensure_initialized()
        
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
        
        # Save to database first
        try:
            await self.db_service.save_repository(repository)
            logger.debug(f"Saved repository {repo_id} to database")
        except Exception as e:
            logger.error(f"Failed to save repository {repo_id} to database: {e}")
            # Continue with in-memory storage
        
        # Update cache
        self.repositories[repo_id] = repository
        
        return repository
    
    async def get_repository_metadata(self, repo_id: str) -> Optional[Repository]:
        """Get repository metadata with cache-first strategy"""
        await self._ensure_initialized()
        
        # Try cache first
        if repo_id in self.repositories:
            logger.debug(f"Repository {repo_id} found in cache")
            return self.repositories[repo_id]
        
        # Fallback to database
        try:
            repository = await self.db_service.get_repository(repo_id)
            if repository:
                # Update cache
                self.repositories[repo_id] = repository
                logger.debug(f"Repository {repo_id} loaded from database and cached")
                return repository
        except Exception as e:
            logger.error(f"Failed to load repository {repo_id} from database: {e}")
        
        logger.debug(f"Repository {repo_id} not found")
        return None
    
    async def list_repositories(self) -> List[Repository]:
        """List all managed repositories with database sync"""
        await self._ensure_initialized()
        
        # If cache is empty, try to load from database
        if not self.repositories:
            try:
                db_repositories = await self.db_service.list_repositories()
                for repository in db_repositories:
                    self.repositories[repository.id] = repository
                logger.debug(f"Loaded {len(db_repositories)} repositories from database")
            except Exception as e:
                logger.error(f"Failed to load repositories from database: {e}")
        
        return list(self.repositories.values())
    
    async def add_repository(self, repo_data: Dict[str, Any]) -> Repository:
        """Add repository with database persistence"""
        await self._ensure_initialized()
        
        repository = Repository(**repo_data)
        
        # Save to database first
        try:
            await self.db_service.save_repository(repository)
            logger.debug(f"Saved repository {repository.id} to database")
        except Exception as e:
            logger.error(f"Failed to save repository {repository.id} to database: {e}")
            # Continue with in-memory storage
        
        # Update cache
        self.repositories[repository.id] = repository
        
        return repository
    
    async def update_repository(self, repo_id: str, updates: Dict[str, Any]) -> Optional[Repository]:
        """Update repository with database persistence"""
        await self._ensure_initialized()
        
        # Get existing repository
        repository = await self.get_repository_metadata(repo_id)
        if not repository:
            return None
        
        # Apply updates
        updated_data = repository.model_dump()
        updated_data.update(updates)
        updated_repository = Repository(**updated_data)
        
        # Save to database
        try:
            await self.db_service.save_repository(updated_repository)
            logger.debug(f"Updated repository {repo_id} in database")
        except Exception as e:
            logger.error(f"Failed to update repository {repo_id} in database: {e}")
            # Continue with in-memory storage
        
        # Update cache
        self.repositories[repo_id] = updated_repository
        
        return updated_repository
    
    async def delete_repository(self, repo_id: str) -> bool:
        """Delete repository from database and cache"""
        await self._ensure_initialized()
        
        # Get repository info before deletion
        repository = await self.get_repository_metadata(repo_id)
        if not repository:
            logger.warning(f"Repository {repo_id} not found for deletion")
            return False
        
        success = True
        
        # Remove from database
        try:
            await self.db_service.delete_repository(repo_id)
            logger.debug(f"Deleted repository {repo_id} from database")
        except Exception as e:
            logger.error(f"Failed to delete repository {repo_id} from database: {e}")
            success = False
        
        # Remove from cache
        if repo_id in self.repositories:
            del self.repositories[repo_id]
            logger.debug(f"Removed repository {repo_id} from cache")
        
        # Remove analysis if exists
        if repo_id in self.analyses:
            del self.analyses[repo_id]
            logger.debug(f"Removed analysis for repository {repo_id}")
        
        # Clean up local files if they exist
        if repository.local_path and os.path.exists(repository.local_path):
            try:
                shutil.rmtree(repository.local_path)
                logger.debug(f"Cleaned up local files for repository {repo_id}")
            except Exception as e:
                logger.error(f"Failed to clean up local files for repository {repo_id}: {e}")
                success = False
        
        return success
    
    async def analyze_repository(self, repo_id: str) -> RepositoryAnalysis:
        """Perform complete analysis of a repository"""
        repository = await self.get_repository_metadata(repo_id)
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
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cs', '.go', '.r', '.R', '.ipynb'}
        
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
            '.r': LanguageType.R,
            '.R': LanguageType.R,
            '.ipynb': LanguageType.JUPYTER,
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
        
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cs', '.go', '.r', '.R', '.ipynb'}
        
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
            # Simple framework detection based on imports and file patterns
            if file.language == LanguageType.PYTHON:
                for element in file.elements:
                    if 'django' in element.code_snippet.lower():
                        frameworks.add('Django')
                    elif 'flask' in element.code_snippet.lower():
                        frameworks.add('Flask')
                    elif 'fastapi' in element.code_snippet.lower():
                        frameworks.add('FastAPI')
            elif file.language == LanguageType.JAVASCRIPT:
                if 'react' in file.file_path.lower() or any('react' in elem.code_snippet.lower() for elem in file.elements):
                    frameworks.add('React')
                elif 'angular' in file.file_path.lower() or any('angular' in elem.code_snippet.lower() for elem in file.elements):
                    frameworks.add('Angular')
                elif 'vue' in file.file_path.lower() or any('vue' in elem.code_snippet.lower() for elem in file.elements):
                    frameworks.add('Vue')
        
        return list(frameworks)

    async def check_repository_health(self, repo_id: str) -> Dict[str, Any]:
        """
        Check the health of a repository by verifying file existence and integrity
        
        Returns:
            Dict with health status, missing files, and recommendations
        """
        try:
            repository = await self.get_repository_metadata(repo_id)
            if not repository:
                return {
                    "healthy": False,
                    "status": "repository_not_found",
                    "message": f"Repository {repo_id} not found in database",
                    "missing_files": [],
                    "recommendations": ["Repository metadata missing from database"]
                }
            
            # Check if local path exists
            repo_path = Path(repository.local_path)
            if not repo_path.exists():
                return {
                    "healthy": False,
                    "status": "local_path_missing",
                    "message": f"Repository local path does not exist: {repository.local_path}",
                    "missing_files": ["entire_repository"],
                    "recommendations": [
                        "Repository files are completely missing",
                        "Auto-recovery available: re-clone from source",
                        f"Original URL: {repository.url}" if repository.url else "No source URL available"
                    ]
                }
            
            # Check if it's a valid repository directory
            if not (repo_path / '.git').exists() and not any(repo_path.iterdir()):
                return {
                    "healthy": False,
                    "status": "empty_directory",
                    "message": f"Repository directory is empty: {repository.local_path}",
                    "missing_files": ["repository_content"],
                    "recommendations": [
                        "Repository directory exists but is empty",
                        "Auto-recovery available: re-clone from source"
                    ]
                }
            
            # Check file accessibility and count
            code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cs', '.go', '.r', '.R', '.ipynb'}
            accessible_files = 0
            missing_files = []
            total_expected = repository.file_count or 0
            
            try:
                for file_path in repo_path.rglob('*'):
                    if file_path.is_file() and file_path.suffix in code_extensions:
                        # Skip common directories to ignore
                        if any(part in str(file_path) for part in ['.git', 'node_modules', '__pycache__', '.venv', 'venv']):
                            continue
                        
                        try:
                            # Try to read the file
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                f.read(100)  # Read first 100 chars to verify accessibility
                            accessible_files += 1
                        except Exception as e:
                            missing_files.append({
                                "file": str(file_path.relative_to(repo_path)),
                                "error": str(e)
                            })
                            
            except Exception as e:
                return {
                    "healthy": False,
                    "status": "directory_access_error",
                    "message": f"Cannot access repository directory: {str(e)}",
                    "missing_files": ["directory_access_failed"],
                    "recommendations": ["Directory access failed", "Check permissions or re-clone repository"]
                }
            
            # Determine health status
            if accessible_files == 0:
                return {
                    "healthy": False,
                    "status": "no_accessible_files",
                    "message": "No code files are accessible in the repository",
                    "missing_files": missing_files,
                    "recommendations": [
                        "No code files found or accessible",
                        "Repository may be corrupted",
                        "Auto-recovery recommended: re-clone from source"
                    ]
                }
            
            # Check if file count significantly differs from expected
            file_count_diff = abs(accessible_files - total_expected) if total_expected > 0 else 0
            file_count_threshold = max(5, total_expected * 0.1)  # 10% or at least 5 files
            
            if total_expected > 0 and file_count_diff > file_count_threshold:
                return {
                    "healthy": False,
                    "status": "file_count_mismatch",
                    "message": f"File count mismatch: expected ~{total_expected}, found {accessible_files}",
                    "missing_files": missing_files,
                    "accessible_files": accessible_files,
                    "expected_files": total_expected,
                    "recommendations": [
                        "Significant file count difference detected",
                        "Repository may be partially corrupted or incomplete",
                        "Consider re-cloning to ensure completeness"
                    ]
                }
            
            # Repository is healthy
            return {
                "healthy": True,
                "status": "healthy",
                "message": "Repository is healthy and accessible",
                "accessible_files": accessible_files,
                "expected_files": total_expected,
                "missing_files": missing_files,
                "recommendations": [] if not missing_files else [
                    f"{len(missing_files)} files have access issues but repository is mostly functional"
                ]
            }
            
        except Exception as e:
            logger.error(f"Health check failed for repository {repo_id}: {str(e)}")
            return {
                "healthy": False,
                "status": "health_check_failed",
                "message": f"Health check failed: {str(e)}",
                "missing_files": ["health_check_error"],
                "recommendations": ["Health check system error", "Manual investigation required"]
            }

    async def auto_recover_repository(self, repo_id: str, force: bool = False) -> Dict[str, Any]:
        """
        Automatically recover a repository by re-cloning from its source URL
        
        Args:
            repo_id: Repository ID to recover
            force: Force recovery even if repository appears healthy
            
        Returns:
            Dict with recovery status and details
        """
        try:
            # Get repository metadata
            repository = await self.get_repository_metadata(repo_id)
            if not repository:
                return {
                    "success": False,
                    "status": "repository_not_found",
                    "message": f"Repository {repo_id} not found",
                    "actions_taken": []
                }
            
            # Check if recovery is needed (unless forced)
            if not force:
                health_check = await self.check_repository_health(repo_id)
                if health_check["healthy"]:
                    return {
                        "success": True,
                        "status": "recovery_not_needed",
                        "message": "Repository is healthy, no recovery needed",
                        "actions_taken": ["health_check_passed"]
                    }
            
            # Check if we have a source URL to recover from
            if not repository.url:
                return {
                    "success": False,
                    "status": "no_source_url",
                    "message": "Cannot recover repository: no source URL available",
                    "actions_taken": ["checked_metadata"]
                }
            
            logger.info(f"Starting auto-recovery for repository {repo_id} from {repository.url}")
            actions_taken = ["initiated_recovery"]
            
            # Backup existing metadata
            original_metadata = {
                "id": repository.id,
                "name": repository.name,
                "url": repository.url,
                "language": repository.language,
                "framework": repository.framework,
                "description": repository.description,
                "github_owner": repository.github_owner,
                "github_repo": repository.github_repo,
                "branch": repository.branch
            }
            actions_taken.append("backed_up_metadata")
            
            # Clean up existing directory if it exists
            repo_path = Path(repository.local_path)
            if repo_path.exists():
                try:
                    import shutil
                    shutil.rmtree(repository.local_path)
                    actions_taken.append("cleaned_existing_directory")
                except Exception as e:
                    logger.warning(f"Failed to clean existing directory {repository.local_path}: {e}")
                    actions_taken.append("cleanup_failed_but_continuing")
            
            # Determine recovery method based on URL type
            if repository.url.startswith(('https://github.com/', 'http://github.com/', 'git@github.com:')):
                # GitHub repository - use enhanced clone method
                try:
                    import re
                    github_pattern = r'(?:https?://github\.com/|git@github\.com:)([^/]+)/([^/\.]+)(?:\.git)?/?$'
                    match = re.match(github_pattern, repository.url)
                    
                    if not match:
                        raise ValueError("Invalid GitHub URL format")
                    
                    owner, repo_name = match.groups()
                    branch = repository.branch or "main"
                    
                    # Re-clone using GitHub method
                    new_repository = await self.clone_github_repository(
                        owner=owner,
                        repo=repo_name,
                        branch=branch,
                        local_name=repository.name
                    )
                    actions_taken.append("re_cloned_from_github")
                    
                except Exception as e:
                    logger.error(f"GitHub clone failed during recovery: {e}")
                    # Fallback to regular git clone
                    try:
                        new_repository = await self.clone_repository(
                            repo_url=repository.url,
                            local_path=repository.local_path
                        )
                        actions_taken.append("re_cloned_with_git_fallback")
                    except Exception as fallback_error:
                        return {
                            "success": False,
                            "status": "clone_failed",
                            "message": f"Recovery failed: {fallback_error}",
                            "actions_taken": actions_taken + ["github_clone_failed", "git_fallback_failed"]
                        }
            else:
                # Regular git repository
                try:
                    new_repository = await self.clone_repository(
                        repo_url=repository.url,
                        local_path=repository.local_path
                    )
                    actions_taken.append("re_cloned_with_git")
                except Exception as e:
                    return {
                        "success": False,
                        "status": "clone_failed",
                        "message": f"Recovery failed: {e}",
                        "actions_taken": actions_taken + ["git_clone_failed"]
                    }
            
            # Update the repository ID to maintain consistency
            if new_repository.id != repo_id:
                # Update the new repository to use the original ID
                old_id = new_repository.id
                new_repository.id = repo_id
                
                # Update in repositories dict
                if old_id in self.repositories:
                    del self.repositories[old_id]
                self.repositories[repo_id] = new_repository
                
                # Update in database
                try:
                    await self.db_service.save_repository(new_repository)
                    actions_taken.append("updated_repository_id")
                except Exception as e:
                    logger.warning(f"Failed to update repository in database: {e}")
                    actions_taken.append("database_update_failed")
            
            # Verify recovery success
            post_recovery_health = await self.check_repository_health(repo_id)
            if post_recovery_health["healthy"]:
                actions_taken.append("recovery_verified")
                
                # Clear any existing analysis cache to force re-analysis
                if repo_id in self.analyses:
                    del self.analyses[repo_id]
                    actions_taken.append("cleared_analysis_cache")
                
                logger.info(f"Successfully recovered repository {repo_id}")
                return {
                    "success": True,
                    "status": "recovery_successful",
                    "message": f"Repository {repository.name} successfully recovered",
                    "actions_taken": actions_taken,
                    "new_file_count": new_repository.file_count,
                    "new_line_count": new_repository.line_count
                }
            else:
                return {
                    "success": False,
                    "status": "recovery_verification_failed",
                    "message": "Repository was re-cloned but health check still fails",
                    "actions_taken": actions_taken + ["post_recovery_health_check_failed"],
                    "health_details": post_recovery_health
                }
                
        except Exception as e:
            logger.error(f"Auto-recovery failed for repository {repo_id}: {str(e)}")
            return {
                "success": False,
                "status": "recovery_system_error",
                "message": f"Recovery system error: {str(e)}",
                "actions_taken": ["recovery_system_error"]
            }

    async def analyze_repository_with_health_check(self, repo_id: str, auto_recover: bool = True) -> RepositoryAnalysis:
        """
        Analyze repository with automatic health checking and recovery
        
        Args:
            repo_id: Repository ID to analyze
            auto_recover: Whether to attempt auto-recovery if health check fails
            
        Returns:
            RepositoryAnalysis object
            
        Raises:
            ValueError: If repository not found or recovery fails
            Exception: If analysis fails after successful health check
        """
        try:
            # First, check repository health
            health_check = await self.check_repository_health(repo_id)
            
            if not health_check["healthy"]:
                logger.warning(f"Repository {repo_id} health check failed: {health_check['message']}")
                
                if auto_recover and health_check["status"] in ["local_path_missing", "empty_directory", "no_accessible_files"]:
                    logger.info(f"Attempting auto-recovery for repository {repo_id}")
                    
                    recovery_result = await self.auto_recover_repository(repo_id)
                    
                    if recovery_result["success"]:
                        logger.info(f"Auto-recovery successful for repository {repo_id}")
                        # Re-check health after recovery
                        post_recovery_health = await self.check_repository_health(repo_id)
                        if not post_recovery_health["healthy"]:
                            raise ValueError(f"Repository {repo_id} still unhealthy after recovery: {post_recovery_health['message']}")
                    else:
                        raise ValueError(f"Repository {repo_id} is unhealthy and auto-recovery failed: {recovery_result['message']}")
                else:
                    # Auto-recovery not enabled or not applicable
                    raise ValueError(f"Repository {repo_id} is unhealthy: {health_check['message']}. Health status: {health_check['status']}")
            
            # Proceed with normal analysis
            return await self.analyze_repository(repo_id)
            
        except ValueError:
            # Re-raise ValueError as is (these are expected repository issues)
            raise
        except Exception as e:
            logger.error(f"Analysis with health check failed for repository {repo_id}: {str(e)}")
            raise Exception(f"Repository analysis failed: {str(e)}")