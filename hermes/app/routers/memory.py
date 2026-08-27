from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from ..dependencies import verify_api_key
from ..models.schemas import MemoryItemCreate, MemoryItemResponse
from ..services.repository import repo
from .services.retrieval import retrieval_service

router = APIRouter(
    prefix="/projects",
    tags=["Memory"],
    dependencies=[Depends(verify_api_key)]
)

@router.get("/{project_id}/memory/search", response_model=List[MemoryItemResponse])
async def search_memory(project_id: UUID, q: str = Query(..., min_length=1)):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        raw_items = retrieval_service.retrieve_context(project_id, q)
        
        # Build MemoryItemResponse-compatible dicts from retrieved context items
        response_items = []
        for item in raw_items:
            try:
                response_items.append({
                    "id": str(item["id"]),
                    "project_id": str(project_id),
                    "type": item.get("category", "knowledge"),
                    "title": item.get("title"),
                    "content": item.get("content", ""),
                    "source": item.get("metadata", {}).get("source"),
                    "confidence": item.get("confidence", 1.0),
                    "status": item.get("metadata", {}).get("status"),
                    "created_at": "2026-01-01T00:00:00Z",  # fallback — full objects from DB have this
                    "updated_at": "2026-01-01T00:00:00Z"
                })
            except Exception:
                continue
        return response_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/memory", response_model=MemoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_memory_item(project_id: UUID, payload: MemoryItemCreate):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        item = repo.create_memory_item(
            project_id=project_id,
            type=payload.type,
            title=payload.title,
            content=payload.content,
            source=payload.source,
            confidence=payload.confidence,
            status=payload.status
        )
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
