import json
from typing import Any, Dict, List, Optional
from .services.ai_providers import ai_provider

class ConflictDetector:
    def __init__(self):
        pass

    def detect_conflicts(self, retrieved_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Scans retrieved context items and flags any active contradictions.
        Returns a dict:
        {
            "has_conflict": bool,
            "conflict_description": str or None,
            "conflicting_item_ids": list of UUID strings
        }
        """
        # If there are fewer than 2 items, there can't be a conflict
        if len(retrieved_items) < 2:
            return {
                "has_conflict": False,
                "conflict_description": None,
                "conflicting_item_ids": []
            }

        # Formulate a simplified summary of retrieved items for the LLM
        items_summary = []
        for item in retrieved_items:
            items_summary.append({
                "id": str(item.get("id")),
                "category": item.get("category"),
                "content": item.get("content"),
                "status": item.get("metadata", {}).get("status", "active")
            })

        system_prompt = (
            "You are the Conflict Detector module of the Hermes backend orchestrator.\n"
            "Your task is to review a list of retrieved database items (decisions, state, tasks, requirements) "
            "and check if any ACTIVE items contradict each other.\n"
            "An active conflict exists if two pieces of active information are mutually exclusive, "
            "contain opposite instructions, or directly clash (e.g. one decision says 'Use SQL' and another "
            "active decision says 'Use MongoDB').\n"
            "If an item is revoked, ignore it. Focus only on active items.\n\n"
            "You must respond ONLY with a JSON object in this exact format:\n"
            "{\n"
            "  \"has_conflict\": true or false,\n"
            "  \"conflict_description\": \"Detailed explanation of the contradiction, or null if none\",\n"
            "  \"conflicting_item_ids\": [\"uuid-1\", \"uuid-2\"] (list of ids causing the conflict, or empty array)\n"
            "}"
        )

        user_prompt = f"Review the following retrieved items and detect if there are conflicts:\n\n{json.dumps(items_summary, indent=2)}"

        try:
            # We call the LLM in JSON mode. We can use the primary provider.
            # Keep it fast and simple.
            raw_response = ai_provider.generate_text(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                json_mode=True
            )
            
            # Parse response
            # Clean up response if it has extra markdown wrappers (just in case)
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                # strip code block wrappers if any
                lines = cleaned.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned = "\n".join(lines).strip()
                
            result = json.loads(cleaned)
            return {
                "has_conflict": bool(result.get("has_conflict", False)),
                "conflict_description": result.get("conflict_description"),
                "conflicting_item_ids": result.get("conflicting_item_ids", [])
            }
        except Exception as e:
            # If the check fails, we print and log, but do not block the pipeline with a conflict.
            print(f"Error during conflict detection: {e}")
            return {
                "has_conflict": False,
                "conflict_description": None,
                "conflicting_item_ids": []
            }

# Single global instance
conflict_detector = ConflictDetector()
