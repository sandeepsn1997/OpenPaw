"""Vector database service for RAG (Retrieval Augmented Generation)."""

import json
import os
from typing import List, Optional, Tuple

import numpy as np

# FAISS imports - optional dependency
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class VectorStore:
    """Vector store for semantic search and RAG."""

    def __init__(self, dimension: int = 384, index_path: str = "./data/faiss.index"):
        """
        Initialize vector store.
        
        Args:
            dimension: Dimension of embeddings (default 384 for all-MiniLM-L6-v2)
            index_path: Path to save FAISS index
        """
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS not installed. Install with: pip install faiss-cpu")
        
        self.dimension = dimension
        self.index_path = index_path
        self.index = None
        self.documents = []
        self.metadata = {}
        
        # Create index directory if it doesn't exist
        os.makedirs(os.path.dirname(index_path) or ".", exist_ok=True)
        
        # Load or create index
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing index or create new one."""
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            # Load metadata
            metadata_path = self.index_path.replace(".index", ".json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self.metadata = data.get("metadata", {})
        else:
            # Create new index
            self.index = faiss.IndexFlatL2(self.dimension)

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadata: Optional[List[dict]] = None,
    ) -> None:
        """
        Add documents with embeddings to the index.
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadata: Optional metadata for each document
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents and embeddings must match")
        
        # Convert embeddings to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Add to FAISS index
        self.index.add(embeddings_array)
        
        # Store documents and metadata
        start_idx = len(self.documents)
        for i, doc in enumerate(documents):
            doc_id = str(start_idx + i)
            self.documents.append(doc)
            
            if metadata and i < len(metadata):
                self.metadata[doc_id] = metadata[i]
            else:
                self.metadata[doc_id] = {"source": "unknown"}
        
        # Save index and metadata
        self._save()

    def search(
        self,
        query_embedding: List[float],
        k: int = 5,
    ) -> List[Tuple[str, float, dict]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
        
        Returns:
            List of (document, distance, metadata) tuples
        """
        query_array = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_array, k)
        
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx >= 0 and idx < len(self.documents):
                doc = self.documents[int(idx)]
                metadata = self.metadata.get(str(idx), {})
                results.append((doc, float(distance), metadata))
        
        return results

    def delete_document(self, doc_id: int) -> None:
        """Delete a document from the index."""
        if doc_id < len(self.documents):
            self.documents[doc_id] = None
            if str(doc_id) in self.metadata:
                del self.metadata[str(doc_id)]
            self._save()

    def _save(self) -> None:
        """Save index and metadata to disk."""
        faiss.write_index(self.index, self.index_path)
        
        metadata_path = self.index_path.replace(".index", ".json")
        with open(metadata_path, "w") as f:
            json.dump(
                {
                    "documents": self.documents,
                    "metadata": self.metadata,
                },
                f,
            )

    def clear(self) -> None:
        """Clear all documents and index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.metadata = {}
        self._save()

    def size(self) -> int:
        """Get number of documents in index."""
        return len(self.documents)


class EmbeddingService:
    """Service for generating embeddings."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding service.
        
        Args:
            model_name: Hugging Face model name for embeddings
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        return self.model.encode(text, convert_to_numpy=True).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


class RAGService:
    """Retrieval Augmented Generation service."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_service: EmbeddingService,
    ):
        """Initialize RAG service."""
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    def add_knowledge(
        self,
        documents: List[str],
        metadata: Optional[List[dict]] = None,
    ) -> None:
        """Add documents to knowledge base."""
        embeddings = self.embedding_service.embed_batch(documents)
        self.vector_store.add_documents(documents, embeddings, metadata)

    def retrieve(
        self,
        query: str,
        k: int = 5,
    ) -> List[Tuple[str, float, dict]]:
        """Retrieve relevant documents for query."""
        query_embedding = self.embedding_service.embed(query)
        return self.vector_store.search(query_embedding, k)

    def get_context(self, query: str, k: int = 5) -> str:
        """Get formatted context for LLM from retrieved documents."""
        results = self.retrieve(query, k)
        
        if not results:
            return ""
        
        context_parts = []
        for i, (doc, distance, metadata) in enumerate(results, 1):
            context_parts.append(f"[{i}] {doc}\n(similarity: {1 / (1 + distance):.2%})")
        
        return "\n\n".join(context_parts)
