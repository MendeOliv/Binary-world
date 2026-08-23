import json
from typing import Any, Dict, List, Optional
from uuid import UUID
from app.services.ai_providers import ai_provider
from app.services.repository import repo

class MemoryExtractor:
    def __init__(self):
        pass

    def extract_and_persist(
        self,
        project_id: UUID,
        user_message: str,
        ai_response: str,
        retrieved_context: str
    ) -> Dict[str, Any]:
        """
        Analyzes the interaction, extracts new decisions, state, tasks, and requirements.
        Persists them to Supabase, respecting custom text IDs and the snapshot state structure.
        """
        system_prompt = (
            "You are the Memory Extractor module of the Hermes backend orchestrator.\n"
            "Your job is to analyze the conversation between the user and the AI assistant, "
            "and extract any changes to project decisions, project state snapshot, tasks, or requirements.\n\n"
            "Here are the rules for IDs:\n"
            "- Decisions must have text IDs starting with 'DEC-' (e.g., DEC-001, DEC-002). "
            "Review the retrieved context to see existing IDs and pick the next logical number.\n"
            "- Requirements must have text IDs starting with 'REQ-' (e.g., REQ-001, REQ-002).\n"
            "- Tasks must have text IDs starting with 'TASK-' (e.g., TASK-001, TASK-002).\n\n"
            "Here is the protocol for decisions:\n"
            "- A decision is a commitment to a specific path, technology, rule, or architecture.\n"
            "- If a new decision replaces an old decision, you must identify the ID of the old decision "
            "being replaced in the 'replaces_decision_id' field.\n\n"
            "You must return ONLY a JSON object in this exact format:\n"
            "{\n"
            "  \"decisions\": [\n"
            "    {\n"
            "      \"id\": \"DEC-00X\",\n"
            "      \"topic\": \"Short topic name\",\n"
            "      \"content\": \"Full description of the decision\",\n"
            "      \"reason\": \"Why this decision was made\",\n"
            "      \"source\": \"model_inference\" or \"user\",\n"
            "      \"confidence\": 0.95,\n"
            "      \"status\": \"active\",\n"
            "      \"replaces_decision_id\": \"DEC-00Y\" (ID of decision to revoke, or null)\n"
            "    }\n"
            "  ],\n"
            "  \"requirements\": [\n"
            "    {\n"
            "      \"id\": \"REQ-00X\",\n"
            "      \"content\": \"Full requirement description\",\n"
            "      \"status\": \"pending\"\n"
            "    }\n"
            "  ],\n"
            "  \"tasks\": [\n"
            "    {\n"
            "      \"id\": \"TASK-00X\",\n"
            "      \"title\": \"Title of task\",\n"
            "      \"description\": \"Description\",\n"
            "      \"status\": \"pending\"\n"
            "    }\n"
            "  ],\n"
            "  \"state\": {\n"
            "    \"current_phase\": {\"name\": \"name\", \"details\": \"...\"},\n"
            "    \"completed\": [\"step 1\", \"step 2\"],\n"
            "    \"in_progress\": [\"step 3\"],\n"
            "    \"next\": [\"step 4\"],\n"
            "    \"open_questions\": [\"question 1\"]\n"
            "  }\n"
            "}"
        )

        user_prompt = (
            f"Retrieved Context:\n{retrieved_context}\n\n"
            f"User Message:\n{user_message}\n\n"
            f"AI Response:\n{ai_response}\n\n"
            "Extract new/updated elements:"
        )

        extracted_data = {
            "decisions": [],
            "requirements": [],
            "tasks": [],
            "state": None
        }

        try:
            raw_response = ai_provider.generate_text(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                json_mode=True
            )
            
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                lines = cleaned.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned = "\n".join(lines).strip()

            extracted_data = json.loads(cleaned)
        except Exception as e:
            print(f"Error during memory extraction parsing: {e}")
            return extracted_data

        persisted_summary = {
            "decisions_created": 0,
            "decisions_revoked": 0,
            "requirements_created": 0,
            "tasks_created": 0,
            "state_updated": 0,
            "memory_items_created": 0
        }

        # 1. Persist Decisions (with custom text IDs and revocation logic)
        for dec in extracted_data.get("decisions", []):
            try:
                dec_id = dec.get("id")
                topic = dec.get("topic")
                content = dec.get("content")
                reason = dec.get("reason")
                source = dec.get("source", "model_inference")
                confidence = float(dec.get("confidence", 1.0))
                status = dec.get("status", "active")
                replaces_id = dec.get("replaces_decision_id")
                
                # Check for null values
                if replaces_id == "null":
                    replaces_id = None
                
                # Check if decision ID already exists
                existing = repo.get_decision(dec_id)
                if existing:
                    # Update decision instead of inserting new
                    updates = {
                        "topic": topic,
                        "content": content,
                        "reason": reason,
                        "source": source,
                        "confidence": confidence,
                        "status": status,
                        "replaced_by": replaces_id
                    }
                    repo.update_decision(dec_id, updates)
                else:
                    # Insert new decision
                    repo.create_decision(
                        id=dec_id,
                        project_id=project_id,
                        topic=topic,
                        content=content,
                        reason=reason,
                        source=source,
                        confidence=confidence,
                        status=status,
                        replaced_by=None
                    )
                
                persisted_summary["decisions_created"] += 1
                
                # Also log this decision as a memory_item
                repo.create_memory_item(
                    project_id=project_id,
                    type="decision",
                    title=topic,
                    content=f"Decision: {topic} - {content}",
                    source=source,
                    confidence=confidence,
                    status=status
                )
                persisted_summary["memory_items_created"] += 1

                # If replacing a previous decision, revoke the old one and link them
                if replaces_id:
                    repo.revoke_decision(replaces_id, dec_id)
                    persisted_summary["decisions_revoked"] += 1
                    
                    repo.create_memory_item(
                        project_id=project_id,
                        type="decision",
                        title=f"Revocation of {replaces_id}",
                        content=f"Revoked Decision {replaces_id}. Replaced by: {dec_id} ({topic})",
                        source="model_inference",
                        confidence=1.0,
                        status="revoked"
                    )
            except Exception as ex:
                print(f"Failed to persist decision {dec}: {ex}")

        # 2. Persist Requirements
        for req in extracted_data.get("requirements", []):
            try:
                req_id = req.get("id")
                content = req.get("content")
                status = req.get("status", "pending")
                
                existing = repo.get_requirement(req_id)
                if not existing:
                    repo.create_requirement(
                        id=req_id,
                        project_id=project_id,
                        content=content,
                        status=status
                    )
                    persisted_summary["requirements_created"] += 1
                    
                    repo.create_memory_item(
                        project_id=project_id,
                        type="requirement",
                        title=f"Requirement {req_id}",
                        content=f"Requirement: {content}",
                        source="model_inference",
                        confidence=1.0,
                        status=status
                    )
                    persisted_summary["memory_items_created"] += 1
            except Exception as ex:
                print(f"Failed to persist requirement {req}: {ex}")

        # 3. Persist Tasks
        for task in extracted_data.get("tasks", []):
            try:
                task_id = task.get("id")
                title = task.get("title")
                desc = task.get("description")
                status = task.get("status", "pending")
                
                existing = repo.get_task(task_id)
                if existing:
                    updates = {
                        "title": title,
                        "description": desc,
                        "status": status
                    }
                    repo.update_task(task_id, updates)
                else:
                    repo.create_task(
                        id=task_id,
                        project_id=project_id,
                        title=title,
                        description=desc,
                        status=status
                    )
                    persisted_summary["tasks_created"] += 1
                    
                    repo.create_memory_item(
                        project_id=project_id,
                        type="task",
                        title=title,
                        content=f"Task: {title} - {desc or ''}",
                        source="model_inference",
                        confidence=1.0,
                        status=status
                    )
                    persisted_summary["memory_items_created"] += 1
            except Exception as ex:
                print(f"Failed to persist task {task}: {ex}")

        # 4. Persist State snapshot
        state_snapshot = extracted_data.get("state")
        if state_snapshot:
            try:
                repo.update_project_state(project_id, state_snapshot)
                persisted_summary["state_updated"] += 1
                
                repo.create_memory_item(
                    project_id=project_id,
                    type="state",
                    title="State Snapshot Update",
                    content=f"State Updated: current_phase={json.dumps(state_snapshot.get('current_phase'))}",
                    source="model_inference",
                    confidence=1.0
                )
                persisted_summary["memory_items_created"] += 1
            except Exception as ex:
                print(f"Failed to persist state snapshot: {ex}")

        return {
            "extracted": extracted_data,
            "persisted_summary": persisted_summary
        }

# Single global instance
memory_extractor = MemoryExtractor()
