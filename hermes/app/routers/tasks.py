from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import verify_api_key
from app.models.schemas import TaskCreate, TaskResponse, TaskUpdate
from app.services.repository import repo

project_tasks_router = APIRouter(
    prefix="/projects",
    tags=["Tasks"],
    dependencies=[Depends(verify_api_key)]
)

tasks_router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    dependencies=[Depends(verify_api_key)]
)

@project_tasks_router.post("/{project_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(project_id: UUID, payload: TaskCreate):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        existing = repo.get_task(payload.id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Task with ID '{payload.id}' already exists."
            )

        task = repo.create_task(
            id=payload.id,
            project_id=project_id,
            title=payload.title,
            description=payload.description,
            status=payload.status
        )
        
        repo.create_memory_item(
            project_id=project_id,
            type="task",
            title=payload.title,
            content=f"Task: {payload.title} - {payload.description or ''}",
            source="user",
            confidence=1.0,
            status=payload.status
        )
        
        return task
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@project_tasks_router.get("/{project_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(project_id: UUID):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        return repo.list_tasks(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@tasks_router.patch("/{task_id}", response_model=TaskResponse)
async def patch_task(task_id: str, payload: TaskUpdate):
    existing = repo.get_task(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        updates = payload.model_dump(exclude_unset=True)
        updated_task = repo.update_task(task_id, updates)
        
        project_id = UUID(existing["project_id"])
        repo.create_memory_item(
            project_id=project_id,
            type="task",
            title=payload.title or existing["title"],
            content=f"Task ID {task_id} updated: status={payload.status or existing['status']}",
            source="user",
            confidence=1.0,
            status=payload.status or existing['status']
        )
        
        return updated_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
