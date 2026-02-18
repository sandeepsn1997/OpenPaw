from typing import List, Dict, Optional
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from ..db import get_db
from ..database import MemoryDB
from ..services.persistent_memory import PersistentMemoryService
from ..services.vector_db import VectorStore, EmbeddingService, RAGService

router = APIRouter(tags=["knowledge"])

# --- SCHEMAS ---

class MemoryFile(BaseModel):
    filename: str
    content: str

class KnowledgeDoc(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    title: str
    content: str
    type: str
    chunks: int
    createdAt: datetime

# --- RAG ENDPOINTS (Standard Knowledge Base) ---

@router.get("/", response_model=List[KnowledgeDoc])
@router.get("", response_model=List[KnowledgeDoc])
def list_knowledge(db: Session = Depends(get_db)):
    """List all RAG knowledge documents."""
    try:
        # Filter docs of type 'knowledge'
        docs = db.query(MemoryDB).filter(MemoryDB.memory_type == "knowledge").all()
        if not docs:
            return []
            
        results = []
        for d in docs:
            # Parse tags
            tag_parts = d.tags.split(",") if d.tags else ["Untitled", ".md"]
            title = tag_parts[0] if len(tag_parts) > 0 else "Untitled"
            ext = tag_parts[1] if len(tag_parts) > 1 else ".md"
            
            results.append(KnowledgeDoc(
                id=d.id,
                title=title,
                content=d.content,
                type=ext,
                chunks=len(d.content) // 500 + 1,
                createdAt=d.created_at if d.created_at else datetime.utcnow()
            ))
        return results
    except Exception as e:
        print(f"CRITICAL ERROR in list_knowledge: {e}")
        return []

@router.get("/debug")
def debug_knowledge():
    """Verify router activity."""
    return {"status": "knowledge_router_active", "timestamp": datetime.utcnow().isoformat()}

@router.post("/upload", response_model=KnowledgeDoc)
def upload_knowledge(
    title: str = Form(...),
    content: str = Form(...),
    type: str = Form(".md"),
    db: Session = Depends(get_db)
):
    """Upload a new document to the RAG knowledge base."""
    doc_id = str(uuid.uuid4())
    
    # Save to database
    db_doc = MemoryDB(
        id=doc_id,
        content=content,
        memory_type="knowledge",
        tags=f"{title},{type}"
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # Add to Vector Store (Non-blocking attempt)
    try:
        vs = VectorStore()
        es = EmbeddingService()
        rag = RAGService(vs, es)
        rag.add_knowledge([content], metadata=[{"id": doc_id, "title": title}])
    except Exception as e:
        print(f"Vector Store indexing skipped/failed: {e}")

    return KnowledgeDoc(
        id=doc_id,
        title=title,
        content=content,
        type=type,
        chunks=len(content) // 500 + 1,
        createdAt=db_doc.created_at
    )

@router.delete("/{doc_id}")
def delete_knowledge(doc_id: str, db: Session = Depends(get_db)):
    """Delete a document from the RAG knowledge base."""
    db_doc = db.query(MemoryDB).filter(MemoryDB.id == doc_id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(db_doc)
    db.commit()
    return {"status": "success"}

# --- PERSISTENT MEMORY ENDPOINTS (Soul, User Info, etc.) ---

@router.get("/persistent", response_model=List[str])
def list_memory_files():
    """List available persistent memory files."""
    try:
        service = PersistentMemoryService()
        return service.files
    except Exception as e:
        print(f"Error listing memory files: {e}")
        return []

@router.get("/persistent/{filename}", response_model=MemoryFile)
def get_memory_file(filename: str):
    """Get the content of a persistent memory file."""
    service = PersistentMemoryService()
    if filename not in service.files:
        raise HTTPException(status_code=404, detail="File not found")
    
    content = service.get_file_content(filename)
    return MemoryFile(filename=filename, content=content)

@router.put("/persistent/{filename}")
def update_memory_file(filename: str, file_data: MemoryFile):
    """Update the content of a persistent memory file."""
    service = PersistentMemoryService()
    if filename not in service.files:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        service.update_memory(filename, file_data.content)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
