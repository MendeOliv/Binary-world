from typing import Any, Dict, List
import tiktoken

class ContextBuilder:
    def __init__(self):
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.encoding = None

    def estimate_tokens(self, text: str) -> int:
        """
        Estimates the number of tokens in a text block.
        Falls back to character division if tiktoken is not available.
        """
        if self.encoding:
            return len(self.encoding.encode(text))
        return len(text) // 4  # Rough heuristic

    def build_context(self, retrieved_items: List[Dict[str, Any]], token_limit: int = 6000) -> str:
        """
        Builds a structured context string from retrieved database items, prioritizing based on trust hierarchy:
        1. Confirmed Decisions (highest trust)
        2. Official States
        3. Requirements
        4. Inferred / General Memory Items (lowest trust)
        
        Applies strict token limits. If context exceeds token_limit, items are discarded
        from the bottom of the hierarchy first.
        """
        # Separate items by trust hierarchy categories
        confirmed_decisions = []
        official_states = []
        requirements = []
        general_memories = []

        for item in retrieved_items:
            category = item.get("category", "").lower()
            content = item.get("content", "")
            
            # Check metadata or category
            status = item.get("metadata", {}).get("status", "")
            
            if category == "decision" and status != "revoked":
                confirmed_decisions.append(content)
            elif category == "state" or (category == "general" and "State:" in content):
                official_states.append(content)
            elif category == "requirement" or category == "task":
                requirements.append(content)
            else:
                general_memories.append(content)

        # Build context sequentially, keeping track of tokens
        context_parts = []
        
        # Helper to safely append items and respect token limit
        def append_section(title: str, items: List[str]):
            if not items:
                return
            section_header = f"\n=== {title} ===\n"
            current_tokens = self.estimate_tokens("".join(context_parts))
            
            section_parts = []
            for idx, item in enumerate(items, 1):
                item_str = f"{idx}. {item}\n"
                item_tokens = self.estimate_tokens(item_str)
                
                # Check if this item would exceed our budget
                if current_tokens + self.estimate_tokens(section_header) + self.estimate_tokens("".join(section_parts)) + item_tokens > token_limit:
                    print(f"Token limit of {token_limit} reached. Omitting subsequent context items in {title}.")
                    break
                section_parts.append(item_str)
                
            if section_parts:
                context_parts.append(section_header)
                context_parts.extend(section_parts)

        # Append sections in order of trust hierarchy (highest first)
        append_section("CONFIRMED DECISIONS (HIGH TRUST)", confirmed_decisions)
        append_section("OFFICIAL STATE AND METADATA", official_states)
        append_section("REQUIREMENTS AND ACTIVE TASKS", requirements)
        append_section("INFERRED CONTEXT AND MEMORY (LOW TRUST)", general_memories)

        joined_context = "".join(context_parts).strip()
        if not joined_context:
            return "No relevant context found in database."
            
        return joined_context

# Single global instance
context_builder = ContextBuilder()
