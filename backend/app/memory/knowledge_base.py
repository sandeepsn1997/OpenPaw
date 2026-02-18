"""Knowledge base loader and manager."""

from pathlib import Path
from typing import List, Optional

from ..services.vector_db import RAGService


class KnowledgeBase:
    """Knowledge base loader and retrieval."""

    def __init__(self, rag_service: RAGService, knowledge_dir: Optional[Path] = None):
        """
        Initialize knowledge base.
        
        Args:
            rag_service: RAG service for vector search
            knowledge_dir: Directory containing knowledge files
        """
        self.rag_service = rag_service
        self.knowledge_dir = knowledge_dir or Path("./knowledge")
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_files: List[str] = []

    def load_knowledge_files(self) -> None:
        """Load all knowledge files."""
        # Load markdown files
        for file_path in self.knowledge_dir.glob("*.md"):
            self._load_file(file_path)

        # Load text files
        for file_path in self.knowledge_dir.glob("*.txt"):
            self._load_file(file_path)

        print(f"Loaded {len(self.loaded_files)} knowledge files")

    def _load_file(self, file_path: Path) -> None:
        """Load a single knowledge file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Split content into chunks for embedding
            chunks = self._chunk_content(content, chunk_size=500)
            
            # Add to knowledge base
            metadata = [{"source": file_path.name, "type": file_path.suffix}] * len(chunks)
            self.rag_service.add_knowledge(chunks, metadata)
            
            self.loaded_files.append(file_path.name)
        except Exception as e:
            print(f"Failed to load knowledge file {file_path}: {e}")

    def _chunk_content(self, content: str, chunk_size: int = 500) -> List[str]:
        """Split content into chunks."""
        words = content.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if len(" ".join(current_chunk)) >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def search(self, query: str, top_k: int = 5) -> List[str]:
        """Search knowledge base."""
        results = self.rag_service.retrieve(query, k=top_k)
        return [doc for doc, _, _ in results]

    def get_context(self, query: str, max_docs: int = 5) -> str:
        """Get formatted context for query."""
        return self.rag_service.get_context(query, max_docs)

    def add_document(self, title: str, content: str) -> None:
        """Add a new document to knowledge base."""
        # Save to file
        file_path = self.knowledge_dir / f"{title}.md"
        file_path.write_text(content, encoding="utf-8")

        # Add to vector DB
        chunks = self._chunk_content(content)
        metadata = [{"source": title, "type": ".md"}] * len(chunks)
        self.rag_service.add_knowledge(chunks, metadata)

        self.loaded_files.append(title)
