"""
Repository and code analysis data models for Kenobi agent
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class LanguageType(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    UNKNOWN = "unknown"

class ElementType(str, Enum):
    """Types of code elements"""
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    INTERFACE = "interface"
    ENUM = "enum"
    VARIABLE = "variable"
    CONSTANT = "constant"
    MODULE = "module"
    COMPONENT = "component"  # For frontend frameworks
    SERVICE = "service"
    CONTROLLER = "controller"

class CloneStatus(str, Enum):
    """Repository clone status"""
    PENDING = "pending"
    CLONING = "cloning"
    COMPLETED = "completed"
    FAILED = "failed"

class Repository(BaseModel):
    """Repository metadata and information"""
    id: str = Field(..., description="Unique repository identifier")
    name: str = Field(..., description="Repository name")
    url: Optional[str] = Field(None, description="Repository URL if cloned from remote")
    local_path: str = Field(..., description="Local filesystem path")
    language: LanguageType = Field(..., description="Primary programming language")
    framework: Optional[str] = Field(None, description="Detected framework (React, Spring, etc.)")
    description: Optional[str] = Field(None, description="Repository description")
    indexed_at: datetime = Field(default_factory=datetime.utcnow, description="Last indexing timestamp")
    file_count: int = Field(0, description="Number of files in repository")
    line_count: int = Field(0, description="Total lines of code")
    size_bytes: int = Field(0, description="Repository size in bytes")
    
    # GitHub-specific fields
    github_owner: Optional[str] = Field(None, description="GitHub repository owner")
    github_repo: Optional[str] = Field(None, description="GitHub repository name")
    clone_status: CloneStatus = Field(CloneStatus.COMPLETED, description="Repository clone status")
    clone_progress: float = Field(0.0, description="Clone progress percentage (0-100)")
    github_metadata: Optional[Dict[str, Any]] = Field(None, description="GitHub repository metadata")
    branch: Optional[str] = Field(None, description="Repository branch being used")
    
class ImportInfo(BaseModel):
    """Information about imports/dependencies"""
    module: str = Field(..., description="Imported module name")
    alias: Optional[str] = Field(None, description="Import alias if any")
    is_local: bool = Field(..., description="Whether import is from local codebase")
    import_type: str = Field(..., description="Type of import (from, import, require, etc.)")

class CodeElement(BaseModel):
    """Individual code element (class, function, etc.)"""
    id: str = Field(..., description="Unique element identifier")
    repository_id: str = Field(..., description="Parent repository ID")
    file_path: str = Field(..., description="Relative path to file")
    element_type: ElementType = Field(..., description="Type of code element")
    name: str = Field(..., description="Element name")
    full_name: str = Field(..., description="Fully qualified name")
    description: str = Field("", description="AI-generated description")
    categories: List[str] = Field(default_factory=list, description="Assigned categories")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies on other elements")
    imports: List[ImportInfo] = Field(default_factory=list, description="Import statements")
    code_snippet: str = Field("", description="Code snippet")
    start_line: int = Field(0, description="Starting line number")
    end_line: int = Field(0, description="Ending line number")
    complexity_score: Optional[float] = Field(None, description="Complexity metric")
    
class ParsedFile(BaseModel):
    """Parsed file information"""
    file_path: str = Field(..., description="File path")
    language: LanguageType = Field(..., description="Programming language")
    elements: List[CodeElement] = Field(default_factory=list, description="Extracted code elements")
    imports: List[ImportInfo] = Field(default_factory=list, description="File-level imports")
    line_count: int = Field(0, description="Number of lines")
    size_bytes: int = Field(0, description="File size in bytes")
    parse_errors: List[str] = Field(default_factory=list, description="Parsing errors if any")

class DependencyEdge(BaseModel):
    """Dependency relationship between code elements"""
    from_element: str = Field(..., description="Source element ID")
    to_element: str = Field(..., description="Target element ID")
    dependency_type: str = Field(..., description="Type of dependency (inheritance, composition, etc.)")
    strength: float = Field(1.0, description="Dependency strength (0-1)")

class DependencyGraph(BaseModel):
    """Repository dependency graph"""
    repository_id: str = Field(..., description="Repository ID")
    nodes: List[str] = Field(default_factory=list, description="Element IDs")
    edges: List[DependencyEdge] = Field(default_factory=list, description="Dependency relationships")
    circular_dependencies: List[List[str]] = Field(default_factory=list, description="Detected cycles")
    
class RepositoryAnalysis(BaseModel):
    """Complete repository analysis result"""
    repository: Repository = Field(..., description="Repository metadata")
    files: List[ParsedFile] = Field(default_factory=list, description="Parsed files")
    dependency_graph: DependencyGraph = Field(..., description="Dependency graph")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Analysis metrics")
    categories_used: List[str] = Field(default_factory=list, description="Categories found in codebase")
    frameworks_detected: List[str] = Field(default_factory=list, description="Detected frameworks")
    
class IndexingResult(BaseModel):
    """Result of repository indexing operation"""
    repository_id: str = Field(..., description="Repository ID")
    success: bool = Field(..., description="Whether indexing succeeded")
    files_processed: int = Field(0, description="Number of files processed")
    elements_extracted: int = Field(0, description="Number of code elements extracted")
    errors: List[str] = Field(default_factory=list, description="Indexing errors")
    processing_time: float = Field(0.0, description="Processing time in seconds")

# Request/Response models for API
class RepositoryIndexRequest(BaseModel):
    """Request to index a repository"""
    path: str = Field(..., description="Local path or Git URL")
    name: Optional[str] = Field(None, description="Repository name override")
    force_reindex: bool = Field(False, description="Force re-indexing if already exists")

class CodeSearchRequest(BaseModel):
    """Request to search code"""
    query: str = Field(..., description="Search query")
    repository_ids: Optional[List[str]] = Field(None, description="Limit search to specific repositories")
    element_types: Optional[List[ElementType]] = Field(None, description="Filter by element types")
    languages: Optional[List[LanguageType]] = Field(None, description="Filter by languages")
    categories: Optional[List[str]] = Field(None, description="Filter by categories")
    limit: int = Field(10, description="Maximum results to return")

class CodeSearchResult(BaseModel):
    """Code search result"""
    element: CodeElement = Field(..., description="Found code element")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    context: str = Field("", description="Additional context about the match")

class MultiRepoSearchResult(BaseModel):
    """Multi-repository search result"""
    query: str = Field(..., description="Original search query")
    results: List[CodeSearchResult] = Field(default_factory=list, description="Search results")
    total_found: int = Field(0, description="Total number of matches")
    repositories_searched: List[str] = Field(default_factory=list, description="Repository IDs searched")
    search_time: float = Field(0.0, description="Search time in seconds")

class FileAnalysisRequest(BaseModel):
    """Request to analyze a single file"""
    file_path: str = Field(..., description="Path to file")
    content: Optional[str] = Field(None, description="File content (if not reading from path)")
    language: Optional[LanguageType] = Field(None, description="Language override")
    include_dependencies: bool = Field(True, description="Whether to analyze dependencies")

# GitHub-specific schemas
class GitHubSearchRequest(BaseModel):
    """Request to search GitHub repositories"""
    query: str = Field(..., description="Search query")
    language: Optional[str] = Field(None, description="Programming language filter")
    sort: str = Field("stars", description="Sort by: stars, forks, help-wanted-issues, updated")
    order: str = Field("desc", description="Sort order: asc or desc")
    per_page: int = Field(30, description="Results per page (max 100)")
    page: int = Field(1, description="Page number")

class GitHubCloneRequest(BaseModel):
    """Request to clone a GitHub repository"""
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    branch: str = Field("main", description="Branch to clone")
    local_name: Optional[str] = Field(None, description="Local directory name (defaults to repo name)")

class GitHubRepositoryInfo(BaseModel):
    """GitHub repository information"""
    id: int = Field(..., description="GitHub repository ID")
    name: str = Field(..., description="Repository name")
    full_name: str = Field(..., description="Full repository name (owner/repo)")
    owner: str = Field(..., description="Repository owner")
    description: Optional[str] = Field(None, description="Repository description")
    language: Optional[str] = Field(None, description="Primary language")
    stars: int = Field(0, description="Star count")
    forks: int = Field(0, description="Fork count")
    issues: int = Field(0, description="Open issues count")
    size: int = Field(0, description="Repository size in KB")
    default_branch: str = Field("main", description="Default branch")
    clone_url: str = Field(..., description="Clone URL")
    html_url: str = Field(..., description="GitHub web URL")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    pushed_at: Optional[str] = Field(None, description="Last push timestamp")
    topics: List[str] = Field(default_factory=list, description="Repository topics")
    license: Optional[str] = Field(None, description="License name")
    archived: bool = Field(False, description="Is archived")
    disabled: bool = Field(False, description="Is disabled")
    private: bool = Field(False, description="Is private")
    fork: bool = Field(False, description="Is fork")

class GitHubBranch(BaseModel):
    """GitHub branch information"""
    name: str = Field(..., description="Branch name")
    sha: str = Field(..., description="Commit SHA")
    protected: bool = Field(False, description="Is protected branch")
    commit_url: str = Field(..., description="Commit URL")

class GitHubSearchResponse(BaseModel):
    """GitHub search response"""
    repositories: List[GitHubRepositoryInfo] = Field(default_factory=list, description="Found repositories")
    total_count: int = Field(0, description="Total number of results")
    incomplete_results: bool = Field(False, description="Are results incomplete")
    page: int = Field(1, description="Current page")
    per_page: int = Field(30, description="Results per page")
    has_next: bool = Field(False, description="Has next page")

class CloneProgressUpdate(BaseModel):
    """Clone progress update"""
    repository_id: str = Field(..., description="Repository ID")
    status: CloneStatus = Field(..., description="Current status")
    progress: float = Field(0.0, description="Progress percentage (0-100)")
    message: str = Field("", description="Status message")
    error: Optional[str] = Field(None, description="Error message if failed")