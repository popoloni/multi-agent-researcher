"""
Content Indexing Service for RAG Integration
Task 3.2: Content Extraction and Indexing Pipeline

This service extracts and indexes repository content for comprehensive RAG context,
building on the Vector Database Service foundation.
"""

import asyncio
import logging
import os
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import hashlib

from app.services.vector_database_service import (
    VectorDatabaseService, 
    DocumentType, 
    IndexingResult
)
from app.services.documentation_service import DocumentationService
from app.services.analysis_service import AnalysisService
from app.services.database_service import database_service
from app.models.repository_schemas import Repository, CodeElement
from app.tools.code_parser import CodeParser

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Types of content that can be extracted and indexed"""
    SOURCE_CODE = "source_code"
    DOCUMENTATION = "documentation"
    README = "readme"
    COMMENTS = "comments"
    DOCSTRINGS = "docstrings"
    CONFIGURATION = "configuration"
    TESTS = "tests"
    MARKDOWN = "markdown"
    TEXT = "text"


@dataclass
class ContentChunk:
    """A chunk of content extracted from repository"""
    id: str
    content: str
    content_type: ContentType
    file_path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    metadata: Dict[str, Any] = None
    parent_element: Optional[str] = None  # For nested content
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ExtractionResult:
    """Result of content extraction from a file"""
    file_path: str
    chunks: List[ContentChunk]
    extraction_time: float
    success: bool
    error_message: Optional[str] = None
    total_chunks: int = 0
    
    def __post_init__(self):
        self.total_chunks = len(self.chunks)


@dataclass
class IndexingProgress:
    """Progress tracking for repository indexing"""
    repository_id: str
    total_files: int
    processed_files: int
    total_chunks: int
    indexed_chunks: int
    failed_chunks: int
    start_time: datetime
    current_file: Optional[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    @property
    def progress_percentage(self) -> float:
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100
    
    @property
    def indexing_percentage(self) -> float:
        if self.total_chunks == 0:
            return 0.0
        return (self.indexed_chunks / self.total_chunks) * 100


class ContentIndexingService:
    """
    Service for extracting and indexing repository content for RAG integration.
    
    Features:
    - Multi-format content extraction (code, docs, markdown, etc.)
    - Intelligent chunking strategies
    - Incremental indexing support
    - Progress tracking and monitoring
    - Error handling and recovery
    - Content deduplication
    """
    
    def __init__(self):
        self.vector_db_service = VectorDatabaseService()
        self.documentation_service = DocumentationService()
        self.analysis_service = AnalysisService()
        self.db_service = database_service
        self.code_parser = CodeParser()
        
        # Configuration
        self.max_chunk_size = 1000  # Maximum characters per chunk
        self.overlap_size = 100     # Overlap between chunks
        self.min_chunk_size = 50    # Minimum chunk size
        
        # File type mappings
        self.code_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go', 
            '.rs', '.php', '.rb', '.swift', '.kt', '.scala', '.r', '.sql'
        }
        self.doc_extensions = {
            '.md', '.rst', '.txt', '.doc', '.docx', '.pdf'
        }
        self.config_extensions = {
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'
        }
        
        # Progress tracking
        self.indexing_progress: Dict[str, IndexingProgress] = {}
        
        logger.info("ContentIndexingService initialized")
    
    async def index_repository_content(
        self, 
        repository_id: str,
        incremental: bool = False,
        content_types: Optional[List[ContentType]] = None
    ) -> IndexingProgress:
        """
        Extract and index all content from a repository.
        
        Args:
            repository_id: Repository identifier
            incremental: Only index new/changed content
            content_types: Specific content types to index
            
        Returns:
            IndexingProgress with final status and metrics
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting content indexing for repository {repository_id}")
            
            # Get repository information
            repository = await self._get_repository(repository_id)
            if not repository:
                raise ValueError(f"Repository {repository_id} not found")
            
            # Initialize progress tracking
            progress = IndexingProgress(
                repository_id=repository_id,
                total_files=0,
                processed_files=0,
                total_chunks=0,
                indexed_chunks=0,
                failed_chunks=0,
                start_time=start_time
            )
            self.indexing_progress[repository_id] = progress
            
            # Get list of files to process
            files_to_process = await self._get_files_to_process(
                repository, incremental, content_types
            )
            progress.total_files = len(files_to_process)
            
            logger.info(f"Found {len(files_to_process)} files to process")
            
            # Process files in batches for better performance
            batch_size = 10
            for i in range(0, len(files_to_process), batch_size):
                batch = files_to_process[i:i + batch_size]
                await self._process_file_batch(repository, batch, progress)
            
            # Final progress update
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"Content indexing completed for repository {repository_id}: "
                f"{progress.indexed_chunks} chunks indexed in {processing_time:.2f}s"
            )
            
            return progress
            
        except Exception as e:
            logger.error(f"Content indexing failed for repository {repository_id}: {e}")
            if repository_id in self.indexing_progress:
                self.indexing_progress[repository_id].errors.append(str(e))
            raise
    
    async def extract_file_content(
        self, 
        file_path: str, 
        content_types: Optional[List[ContentType]] = None
    ) -> ExtractionResult:
        """
        Extract content chunks from a single file.
        
        Args:
            file_path: Path to the file
            content_types: Specific content types to extract
            
        Returns:
            ExtractionResult with extracted chunks
        """
        start_time = datetime.now()
        
        try:
            if not os.path.exists(file_path):
                return ExtractionResult(
                    file_path=file_path,
                    chunks=[],
                    extraction_time=0.0,
                    success=False,
                    error_message="File not found"
                )
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            # Determine file type and extract content
            chunks = []
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in self.code_extensions:
                chunks.extend(await self._extract_code_content(file_path, content))
            
            if file_ext in self.doc_extensions or file_path.endswith('README'):
                chunks.extend(await self._extract_documentation_content(file_path, content))
            
            if file_ext in self.config_extensions:
                chunks.extend(await self._extract_configuration_content(file_path, content))
            
            # Always extract general text chunks as fallback
            if not chunks or ContentType.TEXT in (content_types or []):
                chunks.extend(await self._extract_text_chunks(file_path, content))
            
            # Filter by requested content types
            if content_types:
                chunks = [chunk for chunk in chunks if chunk.content_type in content_types]
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ExtractionResult(
                file_path=file_path,
                chunks=chunks,
                extraction_time=processing_time,
                success=True
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Content extraction failed for {file_path}: {e}")
            
            return ExtractionResult(
                file_path=file_path,
                chunks=[],
                extraction_time=processing_time,
                success=False,
                error_message=str(e)
            )
    
    async def search_content(
        self,
        query: str,
        repository_id: Optional[str] = None,
        content_types: Optional[List[ContentType]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search indexed content using semantic similarity.
        
        Args:
            query: Search query
            repository_id: Limit search to specific repository
            content_types: Filter by content types
            limit: Maximum number of results
            
        Returns:
            List of search results with content and metadata
        """
        try:
            # Convert content types to document types
            document_types = []
            if content_types:
                for content_type in content_types:
                    if content_type == ContentType.SOURCE_CODE:
                        document_types.extend([DocumentType.FUNCTION, DocumentType.CLASS, DocumentType.METHOD])
                    elif content_type == ContentType.DOCUMENTATION:
                        document_types.append(DocumentType.DOCUMENTATION)
                    elif content_type == ContentType.README:
                        document_types.append(DocumentType.README)
                    elif content_type == ContentType.COMMENTS:
                        document_types.append(DocumentType.COMMENT)
            
            # Search using vector database service
            search_results = await self.vector_db_service.search_documents(
                query=query,
                repository_id=repository_id,
                document_types=document_types if document_types else None,
                limit=limit
            )
            
            # Format results for content indexing context
            formatted_results = []
            for result in search_results:
                formatted_result = {
                    "content": result.document.content,
                    "file_path": result.file_path,
                    "content_type": result.document.metadata.get("content_type", "unknown"),
                    "similarity_score": result.similarity_score,
                    "line_numbers": result.line_numbers,
                    "context": result.context,
                    "metadata": result.document.metadata
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Content search failed: {e}")
            return []
    
    async def get_indexing_progress(self, repository_id: str) -> Optional[IndexingProgress]:
        """Get current indexing progress for a repository"""
        return self.indexing_progress.get(repository_id)
    
    async def get_repository_content_stats(self, repository_id: str) -> Dict[str, Any]:
        """Get content statistics for a repository"""
        try:
            # Get documents from vector database
            repo_docs = await self.vector_db_service.get_repository_documents(repository_id)
            
            # Analyze content types
            content_type_counts = {}
            total_content_length = 0
            file_paths = set()
            
            for doc in repo_docs:
                content_type = doc.metadata.get("content_type", "unknown")
                content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
                total_content_length += len(doc.content)
                
                if "file_path" in doc.metadata:
                    file_paths.add(doc.metadata["file_path"])
            
            return {
                "repository_id": repository_id,
                "total_documents": len(repo_docs),
                "total_files": len(file_paths),
                "content_types": content_type_counts,
                "total_content_length": total_content_length,
                "average_document_length": total_content_length / len(repo_docs) if repo_docs else 0,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get content stats for repository {repository_id}: {e}")
            return {
                "repository_id": repository_id,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    # Private helper methods
    
    async def _get_repository(self, repository_id: str) -> Optional[Repository]:
        """Get repository information from database"""
        try:
            async with self.db_service.session_factory() as session:
                from sqlalchemy import text
                result = await session.execute(
                    text("SELECT * FROM repositories WHERE id = ?"),
                    (repository_id,)
                )
                row = result.fetchone()
                
                if row:
                    return Repository(
                        id=row[0],
                        name=row[1],
                        url=row[2],
                        local_path=row[3],
                        # Add other fields as needed
                    )
                return None
                
        except Exception as e:
            logger.error(f"Failed to get repository {repository_id}: {e}")
            return None
    
    async def _get_files_to_process(
        self, 
        repository: Repository, 
        incremental: bool, 
        content_types: Optional[List[ContentType]]
    ) -> List[str]:
        """Get list of files to process based on criteria"""
        files = []
        
        if not repository.local_path or not os.path.exists(repository.local_path):
            logger.warning(f"Repository path not found: {repository.local_path}")
            return files
        
        # Walk through repository directory
        for root, dirs, filenames in os.walk(repository.local_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'node_modules', '__pycache__', 'venv', 'env'}]
            
            for filename in filenames:
                if filename.startswith('.'):
                    continue
                
                file_path = os.path.join(root, filename)
                file_ext = os.path.splitext(filename)[1].lower()
                
                # Filter by content types if specified
                if content_types:
                    should_include = False
                    for content_type in content_types:
                        if content_type == ContentType.SOURCE_CODE and file_ext in self.code_extensions:
                            should_include = True
                        elif content_type == ContentType.DOCUMENTATION and (file_ext in self.doc_extensions or filename == 'README'):
                            should_include = True
                        elif content_type == ContentType.CONFIGURATION and file_ext in self.config_extensions:
                            should_include = True
                    
                    if not should_include:
                        continue
                
                # Check if file should be processed (incremental logic)
                if incremental:
                    # TODO: Implement incremental logic based on file modification time
                    # and existing index timestamps
                    pass
                
                files.append(file_path)
        
        return files
    
    async def _process_file_batch(
        self, 
        repository: Repository, 
        file_batch: List[str], 
        progress: IndexingProgress
    ):
        """Process a batch of files concurrently"""
        tasks = []
        for file_path in file_batch:
            task = self._process_single_file(repository, file_path, progress)
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_single_file(
        self, 
        repository: Repository, 
        file_path: str, 
        progress: IndexingProgress
    ):
        """Process a single file and index its content"""
        try:
            progress.current_file = file_path
            
            # Extract content from file
            extraction_result = await self.extract_file_content(file_path)
            
            if not extraction_result.success:
                progress.errors.append(f"Failed to extract {file_path}: {extraction_result.error_message}")
                progress.processed_files += 1
                return
            
            progress.total_chunks += len(extraction_result.chunks)
            
            # Index each chunk
            for chunk in extraction_result.chunks:
                try:
                    # Convert content type to document type
                    document_type = self._content_type_to_document_type(chunk.content_type)
                    
                    # Prepare metadata
                    metadata = {
                        **chunk.metadata,
                        "content_type": chunk.content_type.value,
                        "file_path": chunk.file_path,
                        "chunk_id": chunk.id,
                        "line_start": chunk.line_start,
                        "line_end": chunk.line_end,
                        "parent_element": chunk.parent_element,
                        "repository_path": repository.local_path,
                        "indexed_at": datetime.now().isoformat()
                    }
                    
                    # Index the chunk
                    indexing_result = await self.vector_db_service.index_document(
                        content=chunk.content,
                        metadata=metadata,
                        document_type=document_type,
                        repository_id=repository.id
                    )
                    
                    if indexing_result.success:
                        progress.indexed_chunks += 1
                    else:
                        progress.failed_chunks += 1
                        progress.errors.append(f"Failed to index chunk {chunk.id}: {indexing_result.error_message}")
                        
                except Exception as e:
                    progress.failed_chunks += 1
                    progress.errors.append(f"Error indexing chunk {chunk.id}: {str(e)}")
            
            progress.processed_files += 1
            
        except Exception as e:
            progress.errors.append(f"Error processing file {file_path}: {str(e)}")
            progress.processed_files += 1
    
    async def _extract_code_content(self, file_path: str, content: str) -> List[ContentChunk]:
        """Extract code-specific content (functions, classes, methods)"""
        chunks = []
        
        try:
            # Use existing code parser to extract code elements
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.py':
                # Parse Python code
                code_elements = await self._parse_python_code(content)
                
                for element in code_elements:
                    chunk = ContentChunk(
                        id=str(uuid.uuid4()),
                        content=element.get("code", ""),
                        content_type=ContentType.SOURCE_CODE,
                        file_path=file_path,
                        line_start=element.get("line_start"),
                        line_end=element.get("line_end"),
                        metadata={
                            "element_type": element.get("type", "unknown"),
                            "element_name": element.get("name", ""),
                            "docstring": element.get("docstring", ""),
                            "complexity": element.get("complexity", 0)
                        }
                    )
                    chunks.append(chunk)
            
            # Extract comments and docstrings
            comment_chunks = await self._extract_comments(file_path, content)
            chunks.extend(comment_chunks)
            
        except Exception as e:
            logger.warning(f"Failed to extract code content from {file_path}: {e}")
        
        return chunks
    
    async def _extract_documentation_content(self, file_path: str, content: str) -> List[ContentChunk]:
        """Extract documentation content with intelligent chunking"""
        chunks = []
        
        try:
            # Split content into sections based on headers
            if file_path.endswith('.md'):
                sections = self._split_markdown_sections(content)
                
                for i, section in enumerate(sections):
                    if len(section.strip()) < self.min_chunk_size:
                        continue
                    
                    chunk = ContentChunk(
                        id=str(uuid.uuid4()),
                        content=section,
                        content_type=ContentType.DOCUMENTATION,
                        file_path=file_path,
                        metadata={
                            "section_index": i,
                            "is_markdown": True,
                            "word_count": len(section.split())
                        }
                    )
                    chunks.append(chunk)
            else:
                # For other documentation, use paragraph-based chunking
                paragraphs = self._split_into_paragraphs(content)
                
                for i, paragraph in enumerate(paragraphs):
                    if len(paragraph.strip()) < self.min_chunk_size:
                        continue
                    
                    chunk = ContentChunk(
                        id=str(uuid.uuid4()),
                        content=paragraph,
                        content_type=ContentType.DOCUMENTATION,
                        file_path=file_path,
                        metadata={
                            "paragraph_index": i,
                            "word_count": len(paragraph.split())
                        }
                    )
                    chunks.append(chunk)
                    
        except Exception as e:
            logger.warning(f"Failed to extract documentation content from {file_path}: {e}")
        
        return chunks
    
    async def _extract_configuration_content(self, file_path: str, content: str) -> List[ContentChunk]:
        """Extract configuration file content"""
        chunks = []
        
        try:
            # For configuration files, treat the entire content as one chunk
            # unless it's very large
            if len(content) <= self.max_chunk_size:
                chunk = ContentChunk(
                    id=str(uuid.uuid4()),
                    content=content,
                    content_type=ContentType.CONFIGURATION,
                    file_path=file_path,
                    metadata={
                        "config_type": os.path.splitext(file_path)[1][1:],  # Remove the dot
                        "line_count": len(content.split('\n'))
                    }
                )
                chunks.append(chunk)
            else:
                # Split large config files into logical sections
                text_chunks = await self._extract_text_chunks(file_path, content)
                for text_chunk in text_chunks:
                    text_chunk.content_type = ContentType.CONFIGURATION
                    chunks.append(text_chunk)
                    
        except Exception as e:
            logger.warning(f"Failed to extract configuration content from {file_path}: {e}")
        
        return chunks
    
    async def _extract_text_chunks(self, file_path: str, content: str) -> List[ContentChunk]:
        """Extract general text chunks with overlap"""
        chunks = []
        
        try:
            # Split content into chunks with overlap
            if len(content) <= self.max_chunk_size:
                chunk = ContentChunk(
                    id=str(uuid.uuid4()),
                    content=content,
                    content_type=ContentType.TEXT,
                    file_path=file_path,
                    metadata={
                        "chunk_index": 0,
                        "total_chunks": 1,
                        "character_count": len(content)
                    }
                )
                chunks.append(chunk)
            else:
                # Split into overlapping chunks
                start = 0
                chunk_index = 0
                
                while start < len(content):
                    end = min(start + self.max_chunk_size, len(content))
                    
                    # Try to break at word boundaries
                    if end < len(content):
                        last_space = content.rfind(' ', start, end)
                        if last_space > start:
                            end = last_space
                    
                    chunk_content = content[start:end].strip()
                    
                    if len(chunk_content) >= self.min_chunk_size:
                        chunk = ContentChunk(
                            id=str(uuid.uuid4()),
                            content=chunk_content,
                            content_type=ContentType.TEXT,
                            file_path=file_path,
                            metadata={
                                "chunk_index": chunk_index,
                                "character_start": start,
                                "character_end": end,
                                "character_count": len(chunk_content)
                            }
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                    
                    # Move start position with overlap
                    start = max(end - self.overlap_size, start + 1)
                    
                # Update total chunks metadata
                for chunk in chunks:
                    chunk.metadata["total_chunks"] = len(chunks)
                    
        except Exception as e:
            logger.warning(f"Failed to extract text chunks from {file_path}: {e}")
        
        return chunks
    
    async def _extract_comments(self, file_path: str, content: str) -> List[ContentChunk]:
        """Extract comments and docstrings from code"""
        chunks = []
        
        try:
            lines = content.split('\n')
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Define comment patterns for different languages
            comment_patterns = {
                '.py': [r'#.*', r'""".*?"""', r"'''.*?'''"],
                '.js': [r'//.*', r'/\*.*?\*/'],
                '.java': [r'//.*', r'/\*.*?\*/'],
                '.cpp': [r'//.*', r'/\*.*?\*/'],
                '.c': [r'//.*', r'/\*.*?\*/'],
            }
            
            patterns = comment_patterns.get(file_ext, [r'#.*'])  # Default to Python-style
            
            for i, line in enumerate(lines):
                for pattern in patterns:
                    matches = re.findall(pattern, line, re.DOTALL)
                    for match in matches:
                        if len(match.strip()) > self.min_chunk_size:
                            chunk = ContentChunk(
                                id=str(uuid.uuid4()),
                                content=match.strip(),
                                content_type=ContentType.COMMENTS,
                                file_path=file_path,
                                line_start=i + 1,
                                line_end=i + 1,
                                metadata={
                                    "comment_type": "inline" if "//" in pattern or "#" in pattern else "block"
                                }
                            )
                            chunks.append(chunk)
                            
        except Exception as e:
            logger.warning(f"Failed to extract comments from {file_path}: {e}")
        
        return chunks
    
    async def _parse_python_code(self, content: str) -> List[Dict[str, Any]]:
        """Parse Python code to extract functions, classes, and methods"""
        try:
            import ast
            
            tree = ast.parse(content)
            elements = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    elements.append({
                        "type": "function",
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno,
                        "code": ast.get_source_segment(content, node),
                        "docstring": ast.get_docstring(node) or "",
                        "args": [arg.arg for arg in node.args.args]
                    })
                elif isinstance(node, ast.ClassDef):
                    elements.append({
                        "type": "class",
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno,
                        "code": ast.get_source_segment(content, node),
                        "docstring": ast.get_docstring(node) or "",
                        "bases": [base.id for base in node.bases if hasattr(base, 'id')]
                    })
            
            return elements
            
        except Exception as e:
            logger.warning(f"Failed to parse Python code: {e}")
            return []
    
    def _split_markdown_sections(self, content: str) -> List[str]:
        """Split markdown content into sections based on headers"""
        sections = []
        current_section = []
        
        for line in content.split('\n'):
            if line.startswith('#') and current_section:
                # Start of new section
                sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections
    
    def _split_into_paragraphs(self, content: str) -> List[str]:
        """Split content into paragraphs"""
        paragraphs = []
        current_paragraph = []
        
        for line in content.split('\n'):
            if line.strip() == '':
                if current_paragraph:
                    paragraphs.append('\n'.join(current_paragraph))
                    current_paragraph = []
            else:
                current_paragraph.append(line)
        
        if current_paragraph:
            paragraphs.append('\n'.join(current_paragraph))
        
        return paragraphs
    
    def _content_type_to_document_type(self, content_type: ContentType) -> DocumentType:
        """Convert ContentType to DocumentType for vector database"""
        mapping = {
            ContentType.SOURCE_CODE: DocumentType.CODE_FILE,
            ContentType.DOCUMENTATION: DocumentType.DOCUMENTATION,
            ContentType.README: DocumentType.README,
            ContentType.COMMENTS: DocumentType.COMMENT,
            ContentType.DOCSTRINGS: DocumentType.COMMENT,
            ContentType.CONFIGURATION: DocumentType.CODE_FILE,
            ContentType.TESTS: DocumentType.CODE_FILE,
            ContentType.MARKDOWN: DocumentType.DOCUMENTATION,
            ContentType.TEXT: DocumentType.CODE_FILE,
        }
        return mapping.get(content_type, DocumentType.CODE_FILE)


# Global instance
content_indexing_service = ContentIndexingService()