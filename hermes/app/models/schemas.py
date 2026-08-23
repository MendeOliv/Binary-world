from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    status: Optional[str] = None
    current_phase_id: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- State Schemas (Project State Snapshot) ---
class StateBase(BaseModel):
    current_phase: Dict[str, Any] = Field(default_factory=dict)
    completed: List[Any] = Field(default_factory=list)
    in_progress: List[Any] = Field(default_factory=list)
    next: List[Any] = Field(default_factory=list)
    open_questions: List[Any] = Field(default_factory=list)

class StateUpdate(StateBase):
    pass

class StateResponse(StateBase):
    project_id: UUID
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Decision Schemas ---
class DecisionBase(BaseModel):
    topic: str
    content: str
    reason: Optional[str] = None
    source: str = "user" # user or model_inference
    confidence: float = 1.0
    status: str = "active" # active or revoked

class DecisionCreate(DecisionBase):
    id: str = Field(..., description="Custom decision ID, e.g. DEC-001")

class DecisionUpdate(BaseModel):
    topic: Optional[str] = None
    content: Optional[str] = None
    reason: Optional[str] = None
    source: Optional[str] = None
    confidence: Optional[float] = None
    status: Optional[str] = None
    replaced_by: Optional[str] = None

class DecisionResponse(DecisionBase):
    id: str
    project_id: UUID
    replaced_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Requirement Schemas ---
class RequirementBase(BaseModel):
    content: str
    status: str = "pending"

class RequirementCreate(RequirementBase):
    id: str = Field(..., description="Custom requirement ID, e.g. REQ-001")

class RequirementResponse(RequirementBase):
    id: str
    project_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# --- Task Schemas ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending" # pending, in_progress, done

class TaskCreate(TaskBase):
    id: str = Field(..., description="Custom task ID, e.g. TASK-001")

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class TaskResponse(TaskBase):
    id: str
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Memory Item Schemas ---
class MemoryItemBase(BaseModel):
    type: str # decision, requirement, task, state, knowledge, history
    title: Optional[str] = None
    content: str
    source: Optional[str] = None
    confidence: float = 1.0
    status: Optional[str] = None

class MemoryItemCreate(MemoryItemBase):
    pass

class MemoryItemResponse(MemoryItemBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Conflict Schemas ---
class ConflictBase(BaseModel):
    item_a_id: str
    item_b_id: str
    description: str
    resolved: bool = False
    resolution: Optional[str] = None

class ConflictCreate(ConflictBase):
    pass

class ConflictResponse(ConflictBase):
    id: UUID
    project_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# --- Chat Schemas ---
class ChatRequest(BaseModel):
    message: str
    provider: Optional[str] = None

class ExtractedMemory(BaseModel):
    decisions: List[DecisionCreate] = Field(default_factory=list)
    revoked_decisions: List[str] = Field(default_factory=list) # IDs of decisions to revoke
    requirements: List[RequirementCreate] = Field(default_factory=list)
    tasks: List[TaskCreate] = Field(default_factory=list)
    state: Optional[StateUpdate] = None

class ChatResponse(BaseModel):
    response: str
    requires_clarification: bool
    clarification_question: Optional[str] = None
    project_id: UUID
    extracted_memory: Optional[ExtractedMemory] = None

# --- Request Log Schemas ---
class RequestLogResponse(BaseModel):
    id: UUID
    project_id: UUID
    question: str
    retrieved_ids: List[str]
    reason: Optional[str] = None
    model_used: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
