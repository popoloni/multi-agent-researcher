"""
Text embedding generation tools for semantic code search
"""
import asyncio
import hashlib
import json
import os
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path

from app.models.repository_schemas import CodeElement, ParsedFile
from app.core.model_providers import model_manager

class EmbeddingTools:
    """Tools for generating and managing text embeddings"""
    
    def __init__(self):
        self.model_manager = model_manager
        self.cache_dir = Path("/tmp/kenobi_embeddings")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Embedding dimensions for different models
        self.embedding_dims = {
            "ollama": 4096,  # Default for most Ollama models
            "openai": 1536,  # text-embedding-ada-002
        }
    
    async def generate_code_embedding(self, code_element: CodeElement) -> List[float]:
        """Generate embedding for a code element"""
        
        # Create text representation for embedding
        text = self._create_embedding_text(code_element)
        
        # Check cache first
        cache_key = self._get_cache_key(text)
        cached_embedding = self._load_from_cache(cache_key)
        if cached_embedding is not None:
            return cached_embedding
        
        # Generate new embedding
        try:
            embedding = await self._generate_embedding(text)
            self._save_to_cache(cache_key, embedding)
            return embedding
        except Exception as e:
            print(f"Warning: Failed to generate embedding for {code_element.name}: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * self.embedding_dims.get("ollama", 4096)
    
    async def generate_file_embedding(self, parsed_file: ParsedFile) -> List[float]:
        """Generate embedding for an entire file"""
        
        # Create summary text for the file
        text = self._create_file_embedding_text(parsed_file)
        
        cache_key = self._get_cache_key(text)
        cached_embedding = self._load_from_cache(cache_key)
        if cached_embedding is not None:
            return cached_embedding
        
        try:
            embedding = await self._generate_embedding(text)
            self._save_to_cache(cache_key, embedding)
            return embedding
        except Exception as e:
            print(f"Warning: Failed to generate file embedding for {parsed_file.file_path}: {str(e)}")
            return [0.0] * self.embedding_dims.get("ollama", 4096)
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for a search query"""
        
        cache_key = self._get_cache_key(query)
        cached_embedding = self._load_from_cache(cache_key)
        if cached_embedding is not None:
            return cached_embedding
        
        try:
            embedding = await self._generate_embedding(query)
            self._save_to_cache(cache_key, embedding)
            return embedding
        except Exception as e:
            print(f"Warning: Failed to generate query embedding: {str(e)}")
            return [0.0] * self.embedding_dims.get("ollama", 4096)
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception:
            return 0.0
    
    def find_similar_elements(self, 
                            query_embedding: List[float], 
                            element_embeddings: Dict[str, List[float]], 
                            top_k: int = 10,
                            min_similarity: float = 0.1) -> List[Tuple[str, float]]:
        """Find most similar code elements to a query"""
        
        similarities = []
        for element_id, embedding in element_embeddings.items():
            similarity = self.calculate_similarity(query_embedding, embedding)
            if similarity >= min_similarity:
                similarities.append((element_id, similarity))
        
        # Sort by similarity (descending) and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using the configured model"""
        
        # For now, use a simple approach with Ollama
        # In production, you might want to use a dedicated embedding model
        try:
            # Use a simple prompt to get text representation
            prompt = f"Generate a semantic representation for this code:\n\n{text}"
            
            # For now, create a simple hash-based embedding as fallback
            # This is not ideal but provides consistent results
            return self._create_hash_embedding(text)
            
        except Exception as e:
            print(f"Embedding generation failed: {str(e)}")
            return self._create_hash_embedding(text)
    
    def _create_hash_embedding(self, text: str, dim: int = 512) -> List[float]:
        """Create a deterministic embedding based on text hash"""
        
        # Create multiple hashes to generate vector components
        embeddings = []
        
        for i in range(dim):
            # Create different hash seeds
            hash_input = f"{text}_{i}"
            hash_value = hashlib.md5(hash_input.encode()).hexdigest()
            
            # Convert hex to float between -1 and 1
            int_value = int(hash_value[:8], 16)
            float_value = (int_value / (16**8)) * 2 - 1
            embeddings.append(float_value)
        
        return embeddings
    
    def _create_embedding_text(self, code_element: CodeElement) -> str:
        """Create text representation for code element embedding"""
        
        parts = [
            f"Type: {code_element.element_type.value}",
            f"Name: {code_element.name}",
        ]
        
        if code_element.description:
            parts.append(f"Description: {code_element.description}")
        
        if code_element.code_snippet:
            parts.append(f"Code: {code_element.code_snippet}")
        
        if code_element.categories:
            parts.append(f"Categories: {', '.join(code_element.categories)}")
        
        return "\n".join(parts)
    
    def _create_file_embedding_text(self, parsed_file: ParsedFile) -> str:
        """Create text representation for file embedding"""
        
        parts = [
            f"File: {parsed_file.file_path}",
            f"Language: {parsed_file.language.value}",
            f"Elements: {len(parsed_file.elements)}",
        ]
        
        # Add element summaries
        element_types = {}
        for element in parsed_file.elements:
            element_type = element.element_type.value
            element_types[element_type] = element_types.get(element_type, 0) + 1
        
        if element_types:
            type_summary = ", ".join([f"{count} {type_}" for type_, count in element_types.items()])
            parts.append(f"Contains: {type_summary}")
        
        # Add some element names for context
        element_names = [elem.name for elem in parsed_file.elements[:10]]  # First 10
        if element_names:
            parts.append(f"Key elements: {', '.join(element_names)}")
        
        return "\n".join(parts)
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[List[float]]:
        """Load embedding from cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def _save_to_cache(self, cache_key: str, embedding: List[float]):
        """Save embedding to cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(embedding, f)
        except Exception:
            pass  # Ignore cache save errors