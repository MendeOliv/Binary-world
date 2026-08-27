import json
from typing import Any, Dict, List, Optional
from uuid import UUID
from .services.repository import repo
from .services.retrieval import retrieval_service
from .services.context_builder import context_builder
from .services.conflict_detector import conflict_detector
from .services.memory_extractor import memory_extractor
from .services.ai_providers import ai_provider
from .config import settings

class OrchestratorService:
    def __init__(self):
        pass

    def check_context_sufficiency(
        self,
        query: str,
        retrieved_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Determines if retrieved items provide sufficient context to answer the user query.
        Uses a quick evaluation prompt in JSON mode.
        """
        # Formulate items summary
        items_summary = []
        for item in retrieved_items:
            items_summary.append({
                "id": str(item.get("id")),
                "category": item.get("category"),
                "title": item.get("title"),
                "content": item.get("content")
            })

        system_prompt = (
            "You are the Sufficiency Checker module of the Hermes backend orchestrator.\n"
            "Your task is to analyze the user's query and the list of retrieved database items, "
            "and determine if the retrieved context is SUFFICIENT to formulate a complete, accurate response, "
            "or if critical information is missing, causing ambiguity.\n\n"
            "If the user query is a general question, greeting, or does not require project-specific facts, "
            "it is automatically sufficient (is_sufficient: true).\n"
            "If the query requires project details that are not in the retrieved items, is_sufficient is false.\n\n"
            "Respond ONLY with a JSON object in this exact format:\n"
            "{\n"
            "  \"is_sufficient\": true or false,\n"
            "  \"reasoning\": \"A short explanation of why it is or isn't sufficient\",\n"
            "  \"clarification_question\": \"If is_sufficient is false, formulate a clear clarification question for the user. If true, set to null\"\n"
            "}"
        )

        user_prompt = (
            f"User Query: {query}\n\n"
            f"Retrieved Database Items:\n{json.dumps(items_summary, indent=2)}\n\n"
            "Check sufficiency:"
        )

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

            result = json.loads(cleaned)
            return {
                "is_sufficient": bool(result.get("is_sufficient", True)),
                "reasoning": result.get("reasoning", ""),
                "clarification_question": result.get("clarification_question")
            }
        except Exception as e:
            print(f"Error during sufficiency check: {e}")
            return {
                "is_sufficient": True,
                "reasoning": "Failsafe bypass due to evaluation error",
                "clarification_question": None
            }

    def run_pipeline(
        self,
        project_id: UUID,
        query: str,
        forced_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the main pipeline:
        1. Query relevant items from Supabase.
        2. Detect conflicts.
        3. Check context sufficiency.
        4. If insufficient or conflict: return clarification directly.
        5. If sufficient: build context -> call AI model -> extract new memories -> persist -> log.
        """
        # 1. Query relevant items
        retrieved_items = retrieval_service.retrieve_context(project_id, query)
        retrieved_ids = [str(item["id"]) for item in retrieved_items]

        # 2. Check for active conflicts first
        conflict_result = conflict_detector.detect_conflicts(retrieved_items)
        
        is_sufficient = True
        clarification_question = None
        reasoning = "Information is sufficient and free of active conflicts."

        if conflict_result["has_conflict"]:
            is_sufficient = False
            reasoning = f"Conflict detected: {conflict_result['conflict_description']}"
            clarification_question = (
                f"Detectei um conflito nas decisões ou requisitos ativos que impede uma resposta precisa:\n"
                f"{conflict_result['conflict_description']}\n\n"
                f"Por favor, clarifique qual é a diretiva correta a seguir."
            )
        else:
            # 3. If no conflict, run sufficiency evaluator
            sufficiency_result = self.check_context_sufficiency(query, retrieved_items)
            is_sufficient = sufficiency_result["is_sufficient"]
            reasoning = sufficiency_result["reasoning"]
            clarification_question = sufficiency_result["clarification_question"]

        # 4. If not sufficient (either due to conflict or missing info), bypass LLM logic
        if not is_sufficient:
            # Log the insufficient retrieval query (using request_logs)
            repo.create_request_log(
                project_id=project_id,
                question=query,
                retrieved_ids=retrieved_ids,
                reason=reasoning,
                model_used=forced_provider or settings.PRIMARY_PROVIDER
            )
            
            return {
                "response": clarification_question or "Preciso de mais informações para responder.",
                "requires_clarification": True,
                "clarification_question": clarification_question,
                "project_id": project_id,
                "extracted_memory": None
            }

        # 5. Build minimal context
        context_str = context_builder.build_context(retrieved_items)

        # 6. Call AI model (with context)
        system_prompt = (
            "You are the core reasoning engine of Código Binário. "
            "You have access to the project's confirmed decisions, requirements, tasks, and state "
            "recalled from the database.\n"
            "Use the provided context to answer the user's question accurately.\n"
            "Do not contradict the active decisions or requirements. "
            "Keep your responses technical, concise, and focused."
        )
        
        user_prompt = (
            f"Here is the relevant project context retrieved from the database:\n"
            f"----------------------------------------\n"
            f"{context_str}\n"
            f"----------------------------------------\n\n"
            f"User Message: {query}\n\n"
            f"Response:"
        )

        model_name = forced_provider or settings.PRIMARY_PROVIDER
        ai_response = ai_provider.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            provider=forced_provider
        )

        # 7. Post-process: extract and persist memories
        extraction_result = memory_extractor.extract_and_persist(
            project_id=project_id,
            user_message=query,
            ai_response=ai_response,
            retrieved_context=context_str
        )

        # 8. Register request logs for observability
        repo.create_request_log(
            project_id=project_id,
            question=query,
            retrieved_ids=retrieved_ids,
            reason=f"Sufficiency check: {reasoning}. Extracted: {json.dumps(extraction_result.get('persisted_summary'))}",
            model_used=model_name
        )

        # Build response payload
        return {
            "response": ai_response,
            "requires_clarification": False,
            "clarification_question": None,
            "project_id": project_id,
            "extracted_memory": extraction_result.get("extracted")
        }

# Single global instance
orchestrator = OrchestratorService()
