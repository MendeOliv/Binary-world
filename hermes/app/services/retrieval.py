from typing import Any, Dict, List, Optional
from uuid import UUID
from app.services.repository import repo

class RetrievalService:
    def __init__(self):
        pass

    def retrieve_context(self, project_id: UUID, query_text: str) -> List[Dict[str, Any]]:
        """
        Retrieves context items from the database that are relevant to the query.
        Queries memory_items, decisions, requirements, and tasks using Postgres FTS,
        combining and deduplicating results.
        """
        clean_query = query_text.strip()
        if not clean_query:
            return []

        combined_results = []
        retrieved_ids = set()

        # Helper to avoid duplicates
        def add_result(item_id: str, category: str, content: str, title: Optional[str] = None, metadata: Optional[dict] = None):
            dedup_key = f"{category}:{item_id}"
            if dedup_key not in retrieved_ids:
                combined_results.append({
                    "id": item_id,
                    "category": category,
                    "title": title,
                    "content": content,
                    "confidence": 1.0,
                    "metadata": metadata or {}
                })
                retrieved_ids.add(dedup_key)

        # 1. Search Decisions FTS
        try:
            decisions = repo.search_decisions_fts(project_id, clean_query)
            for dec in decisions:
                if dec.get("status") != "revoked":
                    add_result(
                        item_id=dec["id"],
                        category="decision",
                        content=dec["content"],
                        title=dec["topic"],
                        metadata={"status": dec["status"], "reason": dec.get("reason"), "source": dec.get("source")}
                    )
        except Exception as e:
            print(f"Decisions FTS query failed: {e}")

        # 2. Search Requirements FTS
        try:
            requirements = repo.search_requirements_fts(project_id, clean_query)
            for req in requirements:
                add_result(
                    item_id=req["id"],
                    category="requirement",
                    content=req["content"],
                    title=f"Requirement {req['id']}",
                    metadata={"status": req["status"]}
                )
        except Exception as e:
            print(f"Requirements FTS query failed: {e}")

        # 3. Search Tasks FTS
        try:
            tasks = repo.search_tasks_fts(project_id, clean_query)
            for task in tasks:
                add_result(
                    item_id=task["id"],
                    category="task",
                    content=task.get("description") or "",
                    title=task["title"],
                    metadata={"status": task["status"]}
                )
        except Exception as e:
            print(f"Tasks FTS query failed: {e}")

        # 4. Search Memory Items FTS
        try:
            memories = repo.search_memory_items_fts(project_id, clean_query)
            for mem in memories:
                add_result(
                    item_id=str(mem["id"]),
                    category=mem.get("type", "knowledge"),
                    content=mem["content"],
                    title=mem.get("title"),
                    metadata={"status": mem.get("status"), "source": mem.get("source")}
                )
        except Exception as e:
            print(f"Memory Items FTS query failed: {e}")

        # 5. If nothing was found, fall back to listing recent active elements to provide some context
        if not combined_results:
            try:
                active_decisions = repo.list_decisions(project_id, status="active")[:5]
                for dec in active_decisions:
                    add_result(
                        item_id=dec["id"],
                        category="decision",
                        content=dec["content"],
                        title=dec["topic"],
                        metadata={"status": dec["status"]}
                    )
                
                recent_memories = repo.get_memory_items(project_id)[:10]
                for mem in recent_memories:
                    add_result(
                        item_id=str(mem["id"]),
                        category=mem.get("type", "knowledge"),
                        content=mem["content"],
                        title=mem.get("title"),
                        metadata={"status": mem.get("status")}
                    )
            except Exception as e:
                print(f"Fallback context listing failed: {e}")

        return combined_results

    def generate_embeddings(self, text: str) -> List[float]:
        """
        Placeholder for pgvector embeddings generation.
        """
        return []

# Single global instance
retrieval_service = RetrievalService()
