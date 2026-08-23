from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import verify_api_key
from app.models.schemas import ChatRequest, ChatResponse
from app.services.repository import repo
from app.services.orchestrator import orchestrator

router = APIRouter(
    prefix="/projects",
    tags=["Chat & Orchestrator"],
    dependencies=[Depends(verify_api_key)]
)

@router.post("/{project_id}/chat", response_model=ChatResponse)
async def project_chat(project_id: UUID, payload: ChatRequest):
    # Verify project exists
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # Run orchestrator pipeline
        result = orchestrator.run_pipeline(
            project_id=project_id,
            query=payload.message,
            forced_provider=payload.provider
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
