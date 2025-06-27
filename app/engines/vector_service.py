"""
Vector Database Service for advanced semantic search and embeddings
Phase 3 implementation with ChromaDB integration and neural embeddings
"""

import asyncio
import json
import numpy as np
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("ChromaDB not available, falling back to in-memory storage")

from app.models.repository_schemas import CodeElement, Repository
from app.tools.embedding_tools import EmbeddingTools


class EmbeddingModel(Enum):
    """Available embedding models"""
    HASH_BASED = "hash_based"           # Fast hash-based embeddings
    SENTENCE_TRANSFORMER = "sentence_transformer"  # Neural embeddings
    OPENAI_ADA = "openai_ada"          # OpenAI embeddings
    COHERE = "cohere"                  # Cohere embeddings


class VectorOperation(Enum):
    """Types of vector operations"""
    SIMILARITY_SEARCH = "similarity_search"
    CLUSTERING = "clustering"
    CLASSIFICATION = "classification"
    ANOMALY_DETECTION = "anomaly_detection"


@dataclass
class VectorDocument:
    """Document stored in vector database"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class SimilarityResult:
    """Result of similarity search"""
    document: VectorDocument
    similarity_score: float
    distance: float
    rank: int


@dataclass
class ClusterResult:
    """Result of clustering operation"""
    cluster_id: int
    documents: List[VectorDocument]
    centroid: List[float]
    cluster_size: int
    intra_cluster_distance: float


class VectorService:
    """Advanced vector database service with ChromaDB integration"""
    
    def __init__(self, 
                 persist_directory: str = "/tmp/kenobi_vectors",
                 embedding_model: EmbeddingModel = EmbeddingModel.HASH_BASED,
                 collection_name: str = "kenobi_code_vectors"):
        
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        
        # Initialize embedding tools
        self.embedding_tools = EmbeddingTools()
        
        # Initialize vector database
        self.client = None
        self.collection = None
        self._initialize_database()
        
        # In-memory fallback storage
        self.memory_store: Dict[str, VectorDocument] = {}
        self.embeddings_cache: Dict[str, List[float]] = {}
    
    def _initialize_database(self):
        """Initialize ChromaDB or fallback to in-memory storage"""
        
        if CHROMADB_AVAILABLE:
            try:
                # Initialize ChromaDB client
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                
                # Get or create collection
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"description": "Kenobi code analysis vectors"}
                )
                
                print(f"ChromaDB initialized with collection: {self.collection_name}")
                
            except Exception as e:
                print(f"ChromaDB initialization failed: {e}")
                print("Falling back to in-memory storage")
                self.client = None
                self.collection = None
        else:
            print("Using in-memory vector storage")
    
    async def generate_embedding(self, text: str, model: Optional[EmbeddingModel] = None) -> List[float]:
        """Generate embedding for text using specified model"""
        
        if model is None:
            model = self.embedding_model
        
        # Check cache first
        cache_key = f"{model.value}:{hashlib.md5(text.encode()).hexdigest()}"
        if cache_key in self.embeddings_cache:
            return self.embeddings_cache[cache_key]
        
        try:
            if model == EmbeddingModel.HASH_BASED:
                # Use existing hash-based embedding
                embedding = self.embedding_tools._create_hash_embedding(text)
                
            elif model == EmbeddingModel.SENTENCE_TRANSFORMER:
                # Neural embeddings using sentence transformers
                embedding = await self._generate_neural_embedding(text)
                
            elif model == EmbeddingModel.OPENAI_ADA:
                # OpenAI Ada embeddings
                embedding = await self._generate_openai_embedding(text)
                
            elif model == EmbeddingModel.COHERE:
                # Cohere embeddings
                embedding = await self._generate_cohere_embedding(text)
                
            else:
                # Fallback to hash-based
                embedding = self.embedding_tools._create_hash_embedding(text)
            
            # Cache the embedding
            self.embeddings_cache[cache_key] = embedding
            return embedding
            
        except Exception as e:
            print(f"Embedding generation failed: {e}")
            # Fallback to hash-based embedding
            return self.embedding_tools._create_hash_embedding(text)
    
    async def _generate_neural_embedding(self, text: str) -> List[float]:
        """Generate neural embedding using sentence transformers"""
        
        try:
            from sentence_transformers import SentenceTransformer
            
            # Load model (cache it for reuse)
            if not hasattr(self, '_sentence_model'):
                self._sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Generate embedding
            embedding = self._sentence_model.encode(text)
            return embedding.tolist()
            
        except ImportError:
            print("sentence-transformers not available, falling back to hash-based")
            return self.embedding_tools._create_hash_embedding(text)
    
    async def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate OpenAI Ada embedding"""
        
        try:
            import openai
            from app.core.config import settings
            
            if not hasattr(settings, 'openai_api_key') or not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            
            response = await client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            print(f"OpenAI embedding failed: {e}")
            return self.embedding_tools._create_hash_embedding(text)
    
    async def _generate_cohere_embedding(self, text: str) -> List[float]:
        """Generate Cohere embedding"""
        
        try:
            import cohere
            from app.core.config import settings
            
            if not hasattr(settings, 'cohere_api_key') or not settings.cohere_api_key:
                raise ValueError("Cohere API key not configured")
            
            co = cohere.AsyncClient(settings.cohere_api_key)
            
            response = await co.embed(
                texts=[text],
                model="embed-english-v3.0"
            )
            
            return response.embeddings[0]
            
        except Exception as e:
            print(f"Cohere embedding failed: {e}")
            return self.embedding_tools._create_hash_embedding(text)
    
    async def add_document(self, document: VectorDocument) -> bool:
        """Add document to vector database"""
        
        try:
            # Generate embedding if not provided
            if document.embedding is None:
                document.embedding = await self.generate_embedding(document.content)
            
            if self.collection is not None:
                # Add to ChromaDB
                self.collection.add(
                    ids=[document.id],
                    documents=[document.content],
                    metadatas=[document.metadata],
                    embeddings=[document.embedding]
                )
            else:
                # Add to in-memory store
                self.memory_store[document.id] = document
            
            return True
            
        except Exception as e:
            print(f"Failed to add document: {e}")
            return False
    
    async def add_code_element(self, element: CodeElement, repository: Repository) -> bool:
        """Add code element as vector document"""
        
        # Create document content
        content = f"""
Element: {element.name}
Type: {element.element_type.value}
File: {element.file_path}
Description: {element.description}
Categories: {', '.join(element.categories)}
Code:
{element.code_snippet}
        """.strip()
        
        # Create metadata
        metadata = {
            'element_id': element.id,
            'repository_id': element.repository_id,
            'repository_name': repository.name,
            'element_type': element.element_type.value,
            'element_name': element.name,
            'file_path': element.file_path,
            'categories': element.categories,
            'language': repository.language.value if repository.language else 'unknown',
            'complexity_score': element.complexity_score or 0,
            'lines_of_code': len(element.code_snippet.split('\n')) if element.code_snippet else 0
        }
        
        # Create vector document
        document = VectorDocument(
            id=element.id,
            content=content,
            metadata=metadata
        )
        
        return await self.add_document(document)
    
    async def similarity_search(self, 
                              query: str, 
                              limit: int = 10,
                              filters: Optional[Dict[str, Any]] = None) -> List[SimilarityResult]:
        """Perform similarity search"""
        
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            
            if self.collection is not None:
                # Use ChromaDB for search
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=filters
                )
                
                # Convert to SimilarityResult objects
                similarity_results = []
                for i, doc_id in enumerate(results['ids'][0]):
                    document = VectorDocument(
                        id=doc_id,
                        content=results['documents'][0][i],
                        metadata=results['metadatas'][0][i],
                        embedding=results.get('embeddings', [None])[0]
                    )
                    
                    similarity_results.append(SimilarityResult(
                        document=document,
                        similarity_score=1 - results['distances'][0][i],  # Convert distance to similarity
                        distance=results['distances'][0][i],
                        rank=i + 1
                    ))
                
                return similarity_results
            
            else:
                # Use in-memory search
                return await self._memory_similarity_search(query_embedding, limit, filters)
                
        except Exception as e:
            print(f"Similarity search failed: {e}")
            return []
    
    async def _memory_similarity_search(self, 
                                      query_embedding: List[float], 
                                      limit: int,
                                      filters: Optional[Dict[str, Any]] = None) -> List[SimilarityResult]:
        """Perform similarity search using in-memory storage"""
        
        results = []
        
        for doc_id, document in self.memory_store.items():
            # Apply filters
            if filters:
                if not self._apply_filters(document.metadata, filters):
                    continue
            
            # Generate embedding if not cached
            if document.embedding is None:
                document.embedding = await self.generate_embedding(document.content)
            
            # Calculate similarity
            similarity = self.embedding_tools.calculate_similarity(
                query_embedding, 
                document.embedding
            )
            
            results.append(SimilarityResult(
                document=document,
                similarity_score=similarity,
                distance=1 - similarity,
                rank=0  # Will be set after sorting
            ))
        
        # Sort by similarity and limit results
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        results = results[:limit]
        
        # Set ranks
        for i, result in enumerate(results):
            result.rank = i + 1
        
        return results
    
    def _apply_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Apply filters to metadata"""
        
        for key, value in filters.items():
            if key not in metadata:
                return False
            
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            else:
                if metadata[key] != value:
                    return False
        
        return True
    
    async def cluster_documents(self, 
                              num_clusters: int = 5,
                              filters: Optional[Dict[str, Any]] = None) -> List[ClusterResult]:
        """Perform clustering on documents"""
        
        try:
            # Get all documents
            if self.collection is not None:
                # Get from ChromaDB
                results = self.collection.get(
                    where=filters,
                    include=['documents', 'metadatas', 'embeddings']
                )
                
                documents = []
                embeddings = []
                
                for i, doc_id in enumerate(results['ids']):
                    doc = VectorDocument(
                        id=doc_id,
                        content=results['documents'][i],
                        metadata=results['metadatas'][i],
                        embedding=results['embeddings'][i]
                    )
                    documents.append(doc)
                    embeddings.append(results['embeddings'][i])
            
            else:
                # Get from memory
                documents = []
                embeddings = []
                
                for document in self.memory_store.values():
                    if filters and not self._apply_filters(document.metadata, filters):
                        continue
                    
                    if document.embedding is None:
                        document.embedding = await self.generate_embedding(document.content)
                    
                    documents.append(document)
                    embeddings.append(document.embedding)
            
            if len(documents) < num_clusters:
                num_clusters = len(documents)
            
            # Perform K-means clustering
            clusters = await self._perform_clustering(documents, embeddings, num_clusters)
            return clusters
            
        except Exception as e:
            print(f"Clustering failed: {e}")
            return []
    
    async def _perform_clustering(self, 
                                documents: List[VectorDocument], 
                                embeddings: List[List[float]], 
                                num_clusters: int) -> List[ClusterResult]:
        """Perform K-means clustering"""
        
        try:
            from sklearn.cluster import KMeans
            import numpy as np
            
            # Convert to numpy array
            X = np.array(embeddings)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(X)
            
            # Group documents by cluster
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(documents[i])
            
            # Create cluster results
            cluster_results = []
            for cluster_id, cluster_docs in clusters.items():
                # Calculate centroid
                centroid = kmeans.cluster_centers_[cluster_id].tolist()
                
                # Calculate intra-cluster distance
                cluster_embeddings = [embeddings[documents.index(doc)] for doc in cluster_docs]
                intra_distance = np.mean([
                    np.linalg.norm(np.array(emb) - np.array(centroid))
                    for emb in cluster_embeddings
                ])
                
                cluster_results.append(ClusterResult(
                    cluster_id=int(cluster_id),
                    documents=cluster_docs,
                    centroid=centroid,
                    cluster_size=len(cluster_docs),
                    intra_cluster_distance=float(intra_distance)
                ))
            
            return cluster_results
            
        except ImportError:
            print("scikit-learn not available for clustering")
            return []
        except Exception as e:
            print(f"Clustering computation failed: {e}")
            return []
    
    async def get_document(self, document_id: str) -> Optional[VectorDocument]:
        """Get document by ID"""
        
        try:
            if self.collection is not None:
                # Get from ChromaDB
                results = self.collection.get(
                    ids=[document_id],
                    include=['documents', 'metadatas', 'embeddings']
                )
                
                if results['ids']:
                    return VectorDocument(
                        id=results['ids'][0],
                        content=results['documents'][0],
                        metadata=results['metadatas'][0],
                        embedding=results['embeddings'][0] if results['embeddings'] else None
                    )
            else:
                # Get from memory
                return self.memory_store.get(document_id)
                
        except Exception as e:
            print(f"Failed to get document: {e}")
        
        return None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document by ID"""
        
        try:
            if self.collection is not None:
                # Delete from ChromaDB
                self.collection.delete(ids=[document_id])
            else:
                # Delete from memory
                if document_id in self.memory_store:
                    del self.memory_store[document_id]
            
            return True
            
        except Exception as e:
            print(f"Failed to delete document: {e}")
            return False
    
    async def update_document(self, document: VectorDocument) -> bool:
        """Update existing document"""
        
        try:
            # Delete old version
            await self.delete_document(document.id)
            
            # Add new version
            return await self.add_document(document)
            
        except Exception as e:
            print(f"Failed to update document: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection"""
        
        try:
            if self.collection is not None:
                # Get ChromaDB stats
                count = self.collection.count()
                
                # Get sample of documents for analysis
                sample = self.collection.peek(limit=100)
                
                # Analyze metadata
                languages = {}
                element_types = {}
                repositories = {}
                
                for metadata in sample.get('metadatas', []):
                    lang = metadata.get('language', 'unknown')
                    languages[lang] = languages.get(lang, 0) + 1
                    
                    elem_type = metadata.get('element_type', 'unknown')
                    element_types[elem_type] = element_types.get(elem_type, 0) + 1
                    
                    repo = metadata.get('repository_name', 'unknown')
                    repositories[repo] = repositories.get(repo, 0) + 1
                
                return {
                    'total_documents': count,
                    'embedding_model': self.embedding_model.value,
                    'collection_name': self.collection_name,
                    'languages': languages,
                    'element_types': element_types,
                    'repositories': repositories,
                    'cache_size': len(self.embeddings_cache)
                }
            
            else:
                # Get memory stats
                count = len(self.memory_store)
                
                languages = {}
                element_types = {}
                repositories = {}
                
                for doc in self.memory_store.values():
                    metadata = doc.metadata
                    
                    lang = metadata.get('language', 'unknown')
                    languages[lang] = languages.get(lang, 0) + 1
                    
                    elem_type = metadata.get('element_type', 'unknown')
                    element_types[elem_type] = element_types.get(elem_type, 0) + 1
                    
                    repo = metadata.get('repository_name', 'unknown')
                    repositories[repo] = repositories.get(repo, 0) + 1
                
                return {
                    'total_documents': count,
                    'embedding_model': self.embedding_model.value,
                    'storage_type': 'memory',
                    'languages': languages,
                    'element_types': element_types,
                    'repositories': repositories,
                    'cache_size': len(self.embeddings_cache)
                }
                
        except Exception as e:
            print(f"Failed to get collection stats: {e}")
            return {'error': str(e)}
    
    def clear_cache(self):
        """Clear embeddings cache"""
        self.embeddings_cache.clear()
    
    def reset_collection(self):
        """Reset the entire collection (use with caution!)"""
        
        try:
            if self.collection is not None:
                # Reset ChromaDB collection
                self.client.delete_collection(self.collection_name)
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Kenobi code analysis vectors"}
                )
            else:
                # Clear memory store
                self.memory_store.clear()
            
            # Clear cache
            self.clear_cache()
            
            print("Vector collection reset successfully")
            
        except Exception as e:
            print(f"Failed to reset collection: {e}")


# Global vector service instance
vector_service = VectorService()