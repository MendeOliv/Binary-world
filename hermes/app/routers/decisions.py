from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import verify_api_key
from app.models.schemas import DecisionCreate, DecisionUpdate, DecisionResponse
from app.services.repository import repo

project_decisions_router = APIRouter(
    prefix="/projects",
    tags=["Decisions"],
    dependencies=[Depends(verify_api_key)]
)

decisions_router = APIRouter(
    prefix="/decisions",
    tags=["Decisions"],
    dependencies=[Depends(verify_api_key)]
)

@project_decisions_router.post("/{project_id}/decisions", response_model=DecisionResponse, status_code=status.HTTP_201_CREATED)
async def create_decision(project_id: UUID, payload: DecisionCreate):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    try:
        # Check if ID already exists
        existing = repo.get_decision(payload.id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Decision with ID '{payload.id}' already exists."
            )

        decision = repo.create_decision(
            id=payload.id,
            project_id=project_id,
            topic=payload.topic,
            content=payload.content,
            reason=payload.reason,
            source=payload.source,
            confidence=payload.confidence,
            status=payload.status
        )
        
        # Index as memory item
        repo.create_memory_item(
            project_id=project_id,
            type="decision",
            title=payload.topic,
            content=f"Decision: {payload.topic} - {payload.content}",
            source=payload.source,
            confidence=payload.confidence,
            status=payload.status
        )
        
        return decision
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@project_decisions_router.get("/{project_id}/decisions", response_model=List[DecisionResponse])
async def list_decisions(project_id: UUID, status: Optional[str] = None):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    try:
        return repo.list_decisions(project_id, status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@decisions_router.patch("/{decision_id}", response_model=DecisionResponse)
async def patch_decision(decision_id: str, payload: DecisionUpdate):
    existing = repo.get_decision(decision_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Decision not found")

    try:
        updates = payload.model_dump(exclude_unset=True)
        
        if "replaced_by" in updates and updates["replaced_by"] is not None:
            replacement = repo.get_decision(updates["replaced_by"])
            if not replacement:
                raise HTTPException(status_code=404, detail="Replacement decision not found")

        updated_decision = repo.update_decision(decision_id, updates)
        
        # Log update event
        project_id = UUID(existing["project_id"])
        repo.create_memory_item(
            project_id=project_id,
            type="decision",
            title=f"Update to {decision_id}",
            content=f"Decision ID {decision_id} updated: status={payload.status or existing['status']}, replaced_by={payload.replaced_by or existing.get('replaced_by')}",
            source="user",
            confidence=1.0,
            status=payload.status or existing['status']
        )
        
        return updated_decision
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
