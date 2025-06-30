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
            
            # Prepare local path
            local_dir_name = local_name or repo
            local_path = f"/tmp/kenobi_repos/{local_dir_name}"
            
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
        
        # Remove from database
        try:
            await self.db_service.delete_repository(repo_id)
            logger.debug(f"Deleted repository {repo_id} from database")
        except Exception as e:
            logger.error(f"Failed to delete repository {repo_id} from database: {e}")
        
        # Remove from cache
        if repo_id in self.repositories:
            del self.repositories[repo_id]
        
        # Remove analysis if exists
        if repo_id in self.analyses:
            del self.analyses[repo_id]
        
        return True
    
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