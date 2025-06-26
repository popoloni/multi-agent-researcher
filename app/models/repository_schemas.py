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