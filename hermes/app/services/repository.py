from typing import Any, Dict, List, Optional
from uuid import UUID
from supabase import create_client, Client
from .config import settings

class SupabaseRepository:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )

    # --- Project Operations ---
    def create_project(self, name: str, status: Optional[str] = None, current_phase_id: Optional[str] = None) -> Dict[str, Any]:
        data = {"name": name, "status": status, "current_phase_id": current_phase_id}
        response = self.client.table("projects").insert(data).execute()
        
        # Initialize an empty state snapshot row for this project
        if response.data:
            project_id = response.data[0]["id"]
            self.create_initial_state(UUID(project_id))
            
        return response.data[0] if response.data else {}

    def list_projects(self) -> List[Dict[str, Any]]:
        response = self.client.table("projects").select("*").execute()
        return response.data or []

    def get_project(self, project_id: UUID) -> Optional[Dict[str, Any]]:
        response = self.client.table("projects").select("*").eq("id", str(project_id)).execute()
        return response.data[0] if response.data else None

    # --- State Operations (Snapshot table) ---
    def create_initial_state(self, project_id: UUID) -> Dict[str, Any]:
        data = {
            "project_id": str(project_id),
            "current_phase": {},
            "completed": [],
            "in_progress": [],
            "next": [],
            "open_questions": []
        }
        response = self.client.table("state").insert(data).execute()
        return response.data[0] if response.data else {}

    def get_project_state(self, project_id: UUID) -> Optional[Dict[str, Any]]:
        response = self.client.table("state").select("*").eq("project_id", str(project_id)).execute()
        return response.data[0] if response.data else None

    def update_project_state(self, project_id: UUID, state_data: Dict[str, Any]) -> Dict[str, Any]:
        data = {
            "project_id": str(project_id),
            **state_data
        }
        response = self.client.table("state").upsert(data).execute()
        return response.data[0] if response.data else {}

    # --- Decision Operations (IDs are text, ex: DEC-001) ---
    def create_decision(
        self,
        id: str,
        project_id: UUID,
        topic: str,
        content: str,
        reason: Optional[str] = None,
        source: str = "user",
        confidence: float = 1.0,
        status: str = "active",
        replaced_by: Optional[str] = None
    ) -> Dict[str, Any]:
        data = {
            "id": id,
            "project_id": str(project_id),
            "topic": topic,
            "content": content,
            "reason": reason,
            "source": source,
            "confidence": confidence,
            "status": status,
            "replaced_by": replaced_by
        }
        response = self.client.table("decisions").insert(data).execute()
        return response.data[0] if response.data else {}

    def list_decisions(self, project_id: UUID, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = self.client.table("decisions").select("*").eq("project_id", str(project_id))
        if status:
            query = query.eq("status", status)
        response = query.execute()
        return response.data or []

    def get_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        response = self.client.table("decisions").select("*").eq("id", decision_id).execute()
        return response.data[0] if response.data else None

    def update_decision(self, decision_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        response = self.client.table("decisions").update(updates).eq("id", decision_id).execute()
        return response.data[0] if response.data else None

    def revoke_decision(self, decision_id: str, replaced_by_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        updates = {
            "status": "revoked",
            "replaced_by": replaced_by_id
        }
        return self.update_decision(decision_id, updates)

    def search_decisions_fts(self, project_id: UUID, query_text: str) -> List[Dict[str, Any]]:
        response = self.client.table("decisions") \
            .select("*") \
            .eq("project_id", str(project_id)) \
            .text_search("content", query_text) \
            .execute()
        return response.data or []

    # --- Requirement Operations (IDs are text, ex: REQ-001) ---
    def create_requirement(
        self,
        id: str,
        project_id: UUID,
        content: str,
        status: str = "pending"
    ) -> Dict[str, Any]:
        data = {
            "id": id,
            "project_id": str(project_id),
            "content": content,
            "status": status
        }
        response = self.client.table("requirements").insert(data).execute()
        return response.data[0] if response.data else {}

    def list_requirements(self, project_id: UUID) -> List[Dict[str, Any]]:
        response = self.client.table("requirements").select("*").eq("project_id", str(project_id)).execute()
        return response.data or []

    def get_requirement(self, requirement_id: str) -> Optional[Dict[str, Any]]:
        response = self.client.table("requirements").select("*").eq("id", requirement_id).execute()
        return response.data[0] if response.data else None

    def search_requirements_fts(self, project_id: UUID, query_text: str) -> List[Dict[str, Any]]:
        response = self.client.table("requirements") \
            .select("*") \
            .eq("project_id", str(project_id)) \
            .text_search("content", query_text) \
            .execute()
        return response.data or []

    # --- Task Operations (IDs are text, ex: TASK-001) ---
    def create_task(
        self,
        id: str,
        project_id: UUID,
        title: str,
        description: Optional[str] = None,
        status: str = "pending"
    ) -> Dict[str, Any]:
        data = {
            "id": id,
            "project_id": str(project_id),
            "title": title,
            "description": description,
            "status": status
        }
        response = self.client.table("tasks").insert(data).execute()
        return response.data[0] if response.data else {}

    def list_tasks(self, project_id: UUID) -> List[Dict[str, Any]]:
        response = self.client.table("tasks").select("*").eq("project_id", str(project_id)).execute()
        return response.data or []

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        response = self.client.table("tasks").select("*").eq("id", task_id).execute()
        return response.data[0] if response.data else None

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        response = self.client.table("tasks").update(updates).eq("id", task_id).execute()
        return response.data[0] if response.data else None

    def search_tasks_fts(self, project_id: UUID, query_text: str) -> List[Dict[str, Any]]:
        response = self.client.table("tasks") \
            .select("*") \
            .eq("project_id", str(project_id)) \
            .text_search("description", query_text) \
            .execute()
        return response.data or []

    # --- Memory Item Operations ---
    def create_memory_item(
        self,
        project_id: UUID,
        type: str,
        content: str,
        title: Optional[str] = None,
        source: Optional[str] = None,
        confidence: float = 1.0,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        data = {
            "project_id": str(project_id),
            "type": type,
            "title": title,
            "content": content,
            "source": source,
            "confidence": confidence,
            "status": status
        }
        response = self.client.table("memory_items").insert(data).execute()
        return response.data[0] if response.data else {}

    def get_memory_items(self, project_id: UUID) -> List[Dict[str, Any]]:
        response = self.client.table("memory_items").select("*").eq("project_id", str(project_id)).execute()
        return response.data or []

    def search_memory_items_fts(self, project_id: UUID, query_text: str) -> List[Dict[str, Any]]:
        response = self.client.table("memory_items") \
            .select("*") \
            .eq("project_id", str(project_id)) \
            .text_search("content", query_text) \
            .execute()
        return response.data or []

    # --- Conflict Operations ---
    def create_conflict(
        self,
        project_id: UUID,
        item_a_id: str,
        item_b_id: str,
        description: str
    ) -> Dict[str, Any]:
        data = {
            "project_id": str(project_id),
            "item_a_id": item_a_id,
            "item_b_id": item_b_id,
            "description": description,
            "resolved": False
        }
        response = self.client.table("conflicts").insert(data).execute()
        return response.data[0] if response.data else {}

    def list_conflicts(self, project_id: UUID, resolved: Optional[bool] = None) -> List[Dict[str, Any]]:
        query = self.client.table("conflicts").select("*").eq("project_id", str(project_id))
        if resolved is not None:
            query = query.eq("resolved", resolved)
        response = query.execute()
        return response.data or []

    def resolve_conflict(self, conflict_id: UUID, resolution: str) -> Optional[Dict[str, Any]]:
        updates = {
            "resolved": True,
            "resolution": resolution
        }
        response = self.client.table("conflicts").update(updates).eq("id", str(conflict_id)).execute()
        return response.data[0] if response.data else None

    # --- Request Logging Operations ---
    def create_request_log(
        self,
        project_id: UUID,
        question: str,
        retrieved_ids: List[str],
        reason: Optional[str] = None,
        model_used: Optional[str] = None
    ) -> Dict[str, Any]:
        data = {
            "project_id": str(project_id),
            "question": question,
            "retrieved_ids": retrieved_ids,
            "reason": reason,
            "model_used": model_used
        }
        response = self.client.table("request_logs").insert(data).execute()
        return response.data[0] if response.data else {}

    def list_request_logs(self, project_id: UUID) -> List[Dict[str, Any]]:
        response = self.client.table("request_logs").select("*").eq("project_id", str(project_id)).order("created_at", desc=True).execute()
        return response.data or []

# Single global repository instance
repo = SupabaseRepository()
