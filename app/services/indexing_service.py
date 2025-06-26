"""
Advanced indexing service for code search and retrieval
"""
import asyncio
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import pickle

from app.models.repository_schemas import (
    Repository, ParsedFile, CodeElement, DependencyGraph, 
    LanguageType, ElementType
)
from pydantic import BaseModel, Field
from app.tools.embedding_tools import EmbeddingTools
from app.tools.dependency_analyzer import DependencyAnalyzer

class SearchFilters:
    """Search filter configuration"""
    
    def __init__(self):
        self.languages: List[LanguageType] = []
        self.element_types: List[ElementType] = []
        self.repositories: List[str] = []
        self.categories: List[str] = []
        self.min_similarity: float = 0.1
        self.max_results: int = 50

class SearchResult(BaseModel):
    """Search result with relevance scoring"""
    
    element: CodeElement = Field(..., description="Code element found")
    similarity: float = Field(..., description="Similarity score")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    rank_score: float = Field(..., description="Ranking score")
    
    def __init__(self, element: CodeElement = None, similarity: float = 0.0, context: Dict[str, Any] = None, **data):
        if element is not None:
            data.update({
                'element': element,
                'similarity': similarity,
                'context': context or {},
                'rank_score': similarity
            })
        super().__init__(**data)

class IndexingService:
    """Advanced indexing service for semantic code search"""
    
    def __init__(self, db_path: str = "/tmp/kenobi_index.db"):
        self.db_path = db_path
        self.embedding_tools = EmbeddingTools()
        self.dependency_analyzer = DependencyAnalyzer()
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for indexing"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Repositories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repositories (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                language TEXT NOT NULL,
                indexed_at TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Code elements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_elements (
                id TEXT PRIMARY KEY,
                repository_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                element_type TEXT NOT NULL,
                name TEXT NOT NULL,
                full_name TEXT NOT NULL,
                description TEXT,
                categories TEXT,
                code_snippet TEXT,
                start_line INTEGER,
                end_line INTEGER,
                complexity_score REAL,
                embedding BLOB,
                FOREIGN KEY (repository_id) REFERENCES repositories (id)
            )
        ''')
        
        # Files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                repository_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                language TEXT NOT NULL,
                line_count INTEGER,
                size_bytes INTEGER,
                embedding BLOB,
                indexed_at TIMESTAMP,
                FOREIGN KEY (repository_id) REFERENCES repositories (id)
            )
        ''')
        
        # Dependencies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repository_id TEXT NOT NULL,
                from_element TEXT NOT NULL,
                to_element TEXT NOT NULL,
                dependency_type TEXT NOT NULL,
                strength REAL,
                FOREIGN KEY (repository_id) REFERENCES repositories (id)
            )
        ''')
        
        # Create indexes for better search performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_elements_repo ON code_elements (repository_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_elements_type ON code_elements (element_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_elements_name ON code_elements (name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_repo ON files (repository_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_deps_repo ON dependencies (repository_id)')
        
        conn.commit()
        conn.close()
    
    async def index_repository(self, repository: Repository, files: List[ParsedFile]) -> Dict[str, Any]:
        """Index a complete repository with all its files and dependencies"""
        
        start_time = datetime.now()
        
        # Store repository metadata
        await self._store_repository(repository)
        
        # Index all files and their elements
        total_elements = 0
        for file in files:
            await self._index_file(repository.id, file)
            total_elements += len(file.elements)
        
        # Build and store dependency graph
        dependency_graph = await self.dependency_analyzer.build_dependency_graph(repository, files)
        await self._store_dependency_graph(dependency_graph)
        
        # Calculate and store repository metrics
        metrics = await self._calculate_repository_metrics(repository.id, files, dependency_graph)
        
        end_time = datetime.now()
        indexing_time = (end_time - start_time).total_seconds()
        
        return {
            'repository_id': repository.id,
            'files_indexed': len(files),
            'elements_indexed': total_elements,
            'dependencies_found': len(dependency_graph.edges),
            'indexing_time_seconds': indexing_time,
            'metrics': metrics
        }
    
    async def update_index(self, repository_id: str, changed_files: List[str]) -> Dict[str, Any]:
        """Update index for specific changed files"""
        
        # Remove old entries for changed files
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for file_path in changed_files:
            cursor.execute('DELETE FROM code_elements WHERE repository_id = ? AND file_path = ?', 
                         (repository_id, file_path))
            cursor.execute('DELETE FROM files WHERE repository_id = ? AND file_path = ?', 
                         (repository_id, file_path))
        
        conn.commit()
        conn.close()
        
        # Re-index the changed files
        # This would require re-parsing the files, which we'll implement later
        return {
            'repository_id': repository_id,
            'updated_files': len(changed_files),
            'status': 'updated'
        }
    
    async def search_code(self, query: str, filters: SearchFilters) -> List[SearchResult]:
        """Perform semantic search across indexed code"""
        
        # Generate query embedding
        query_embedding = await self.embedding_tools.generate_query_embedding(query)
        
        # Get candidate elements from database
        candidates = self._get_search_candidates(filters)
        
        # Calculate similarities and rank results
        results = []
        for element_data in candidates:
            element = self._deserialize_element(element_data)
            
            # Load element embedding
            if element_data['embedding']:
                element_embedding = pickle.loads(element_data['embedding'])
                similarity = self.embedding_tools.calculate_similarity(query_embedding, element_embedding)
                
                if similarity >= filters.min_similarity:
                    context = await self._get_element_context(element)
                    result = SearchResult(element, similarity, context)
                    results.append(result)
        
        # Sort by similarity and apply ranking
        results.sort(key=lambda x: x.similarity, reverse=True)
        
        # Apply additional ranking factors
        for result in results:
            result.rank_score = self._calculate_rank_score(result, query)
        
        # Re-sort by rank score
        results.sort(key=lambda x: x.rank_score, reverse=True)
        
        return results[:filters.max_results]
    
    async def search_similar_code(self, element_id: str, filters: SearchFilters) -> List[SearchResult]:
        """Find code elements similar to a given element"""
        
        # Get the reference element
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM code_elements WHERE id = ?', (element_id,))
        ref_data = cursor.fetchone()
        
        if not ref_data:
            return []
        
        # Get reference embedding
        if ref_data[12]:  # embedding column
            ref_embedding = pickle.loads(ref_data[12])
        else:
            return []
        
        # Get candidates and calculate similarities
        candidates = self._get_search_candidates(filters)
        results = []
        
        for element_data in candidates:
            if element_data['id'] == element_id:  # Skip self
                continue
                
            if element_data['embedding']:
                element_embedding = pickle.loads(element_data['embedding'])
                similarity = self.embedding_tools.calculate_similarity(ref_embedding, element_embedding)
                
                if similarity >= filters.min_similarity:
                    element = self._deserialize_element(element_data)
                    context = await self._get_element_context(element)
                    result = SearchResult(element, similarity, context)
                    results.append(result)
        
        results.sort(key=lambda x: x.similarity, reverse=True)
        conn.close()
        
        return results[:filters.max_results]
    
    async def get_dependency_insights(self, repository_id: str) -> Dict[str, Any]:
        """Get dependency analysis insights for a repository"""
        
        # Load dependency graph
        dependency_graph = await self._load_dependency_graph(repository_id)
        
        if not dependency_graph:
            return {}
        
        # Calculate metrics
        coupling_metrics = self.dependency_analyzer.calculate_coupling_metrics(dependency_graph)
        circular_deps = self.dependency_analyzer.find_circular_dependencies(dependency_graph)
        
        return {
            'coupling_metrics': coupling_metrics,
            'circular_dependencies': circular_deps,
            'total_dependencies': len(dependency_graph.edges),
            'dependency_types': self._analyze_dependency_types(dependency_graph)
        }
    
    async def _store_repository(self, repository: Repository):
        """Store repository metadata"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO repositories 
            (id, name, path, language, indexed_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            repository.id,
            repository.name,
            repository.local_path,
            repository.language.value,
            repository.indexed_at,
            json.dumps({})  # Additional metadata can be stored here
        ))
        
        conn.commit()
        conn.close()
    
    async def _index_file(self, repository_id: str, file: ParsedFile):
        """Index a single file and its elements"""
        
        # Generate file embedding
        file_embedding = await self.embedding_tools.generate_file_embedding(file)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store file metadata
        file_id = f"{repository_id}:{file.file_path}"
        cursor.execute('''
            INSERT OR REPLACE INTO files 
            (id, repository_id, file_path, language, line_count, size_bytes, embedding, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_id,
            repository_id,
            file.file_path,
            file.language.value,
            file.line_count,
            file.size_bytes,
            pickle.dumps(file_embedding),
            datetime.now()
        ))
        
        # Store code elements
        for element in file.elements:
            element_embedding = await self.embedding_tools.generate_code_embedding(element)
            
            cursor.execute('''
                INSERT OR REPLACE INTO code_elements 
                (id, repository_id, file_path, element_type, name, full_name, 
                 description, categories, code_snippet, start_line, end_line, 
                 complexity_score, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                element.full_name,
                repository_id,
                file.file_path,
                element.element_type.value,
                element.name,
                element.full_name,
                element.description,
                json.dumps(element.categories),
                element.code_snippet,
                element.start_line,
                element.end_line,
                element.complexity_score,
                pickle.dumps(element_embedding)
            ))
        
        conn.commit()
        conn.close()
    
    async def _store_dependency_graph(self, graph: DependencyGraph):
        """Store dependency graph in database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing dependencies for this repository
        cursor.execute('DELETE FROM dependencies WHERE repository_id = ?', (graph.repository_id,))
        
        # Store new dependencies
        for edge in graph.edges:
            cursor.execute('''
                INSERT INTO dependencies 
                (repository_id, from_element, to_element, dependency_type, strength)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                graph.repository_id,
                edge.from_element,
                edge.to_element,
                edge.dependency_type,
                edge.strength
            ))
        
        conn.commit()
        conn.close()
    
    def _get_search_candidates(self, filters: SearchFilters) -> List[Dict[str, Any]]:
        """Get candidate elements based on filters"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        # Build query based on filters
        query = 'SELECT * FROM code_elements WHERE 1=1'
        params = []
        
        if filters.repositories:
            placeholders = ','.join(['?' for _ in filters.repositories])
            query += f' AND repository_id IN ({placeholders})'
            params.extend(filters.repositories)
        
        if filters.element_types:
            placeholders = ','.join(['?' for _ in filters.element_types])
            query += f' AND element_type IN ({placeholders})'
            params.extend([et.value for et in filters.element_types])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in results]
    
    def _deserialize_element(self, element_data: Dict[str, Any]) -> CodeElement:
        """Convert database row to CodeElement object"""
        
        return CodeElement(
            id=element_data['id'],
            repository_id=element_data['repository_id'],
            file_path=element_data['file_path'],
            element_type=ElementType(element_data['element_type']),
            name=element_data['name'],
            full_name=element_data['full_name'],
            description=element_data['description'] or "",
            categories=json.loads(element_data['categories'] or '[]'),
            code_snippet=element_data['code_snippet'] or "",
            line_start=element_data['start_line'] or 0,
            line_end=element_data['end_line'] or 0,
            complexity_score=element_data['complexity_score']
        )
    
    async def _get_element_context(self, element: CodeElement) -> Dict[str, Any]:
        """Get contextual information for an element"""
        
        return {
            'file_path': element.full_name.split(':')[0] if ':' in element.full_name else "",
            'element_type': element.element_type.value,
            'categories': element.categories,
            'complexity': element.complexity_score or 0.0
        }
    
    def _calculate_rank_score(self, result: SearchResult, query: str) -> float:
        """Calculate enhanced ranking score"""
        
        base_score = result.similarity
        
        # Boost score based on element type relevance
        type_boost = {
            ElementType.CLASS: 1.2,
            ElementType.FUNCTION: 1.1,
            ElementType.METHOD: 1.0,
            ElementType.VARIABLE: 0.8
        }
        
        element_type_boost = type_boost.get(result.element.element_type, 1.0)
        
        # Boost score if query terms appear in element name
        name_boost = 1.0
        query_terms = query.lower().split()
        element_name = result.element.name.lower()
        
        for term in query_terms:
            if term in element_name:
                name_boost += 0.3
        
        # Complexity penalty (simpler code might be more relevant)
        complexity_penalty = 1.0
        if result.element.complexity_score:
            complexity_penalty = max(0.5, 1.0 - (result.element.complexity_score / 10.0))
        
        return base_score * element_type_boost * name_boost * complexity_penalty
    
    async def _calculate_repository_metrics(self, 
                                          repository_id: str, 
                                          files: List[ParsedFile],
                                          dependency_graph: DependencyGraph) -> Dict[str, Any]:
        """Calculate comprehensive repository metrics"""
        
        total_elements = sum(len(f.elements) for f in files)
        total_lines = sum(f.line_count for f in files)
        
        # Language distribution
        language_counts = {}
        for file in files:
            lang = file.language.value
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        # Element type distribution
        element_type_counts = {}
        for file in files:
            for element in file.elements:
                elem_type = element.element_type.value
                element_type_counts[elem_type] = element_type_counts.get(elem_type, 0) + 1
        
        # Dependency metrics
        coupling_metrics = self.dependency_analyzer.calculate_coupling_metrics(dependency_graph)
        
        return {
            'total_files': len(files),
            'total_elements': total_elements,
            'total_lines': total_lines,
            'language_distribution': language_counts,
            'element_type_distribution': element_type_counts,
            'coupling_metrics': coupling_metrics,
            'avg_elements_per_file': total_elements / len(files) if files else 0,
            'avg_lines_per_file': total_lines / len(files) if files else 0
        }
    
    async def _load_dependency_graph(self, repository_id: str) -> Optional[DependencyGraph]:
        """Load dependency graph from database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM dependencies WHERE repository_id = ?', (repository_id,))
        rows = cursor.fetchall()
        
        if not rows:
            return None
        
        from app.models.repository_schemas import DependencyEdge
        
        edges = []
        for row in rows:
            edges.append(DependencyEdge(
                from_element=row[2],
                to_element=row[3],
                dependency_type=row[4],
                strength=row[5]
            ))
        
        conn.close()
        
        return DependencyGraph(
            repository_id=repository_id,
            edges=edges,
            metadata={}
        )
    
    def _analyze_dependency_types(self, graph: DependencyGraph) -> Dict[str, int]:
        """Analyze distribution of dependency types"""
        
        type_counts = {}
        for edge in graph.edges:
            dep_type = edge.dependency_type
            type_counts[dep_type] = type_counts.get(dep_type, 0) + 1
        
        return type_counts