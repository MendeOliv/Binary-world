import json
from typing import Any, Dict, List, Optional
import httpx
from anthropic import Anthropic
import google.generativeai as genai
from groq import Groq
from app.config import settings

class AIProviderService:
    def __init__(self):
        # Initialize clients lazily to prevent errors if keys are missing initially
        self._anthropic_client: Optional[Anthropic] = None
        self._groq_client: Optional[Groq] = None
        self._gemini_configured = False

    @property
    def anthropic_client(self) -> Anthropic:
        if not self._anthropic_client:
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not configured.")
            self._anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        return self._anthropic_client

    @property
    def groq_client(self) -> Groq:
        if not self._groq_client:
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not configured.")
            self._groq_client = Groq(api_key=settings.GROQ_API_KEY)
        return self._groq_client

    def configure_gemini(self):
        if not self._gemini_configured:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not configured.")
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._gemini_configured = True

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        provider: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        """
        Generates text using the configured provider. Automatically routes to fallbacks
        if the primary provider fails or has no key configured.
        """
        # Determine provider sequence (primary first, then fallback list)
        primary = (provider or settings.PRIMARY_PROVIDER).lower()
        
        fallback_sequence = [primary]
        for p in ["anthropic", "gemini", "groq", "nvidia"]:
            if p not in fallback_sequence:
                fallback_sequence.append(p)

        last_error = None
        for prov in fallback_sequence:
            try:
                if prov == "anthropic" and settings.ANTHROPIC_API_KEY:
                    return self._call_anthropic(system_prompt, user_prompt, json_mode)
                elif prov == "gemini" and settings.GEMINI_API_KEY:
                    return self._call_gemini(system_prompt, user_prompt, json_mode)
                elif prov == "groq" and settings.GROQ_API_KEY:
                    return self._call_groq(system_prompt, user_prompt, json_mode)
                elif prov == "nvidia" and settings.NVIDIA_API_KEY:
                    return self._call_nvidia(system_prompt, user_prompt, json_mode)
            except Exception as e:
                print(f"Provider {prov} call failed: {e}. Trying fallback...")
                last_error = e

        # If we reach here, all attempted providers failed
        error_msg = f"All LLM providers failed. Last error: {last_error}"
        print(error_msg)
        raise RuntimeError(error_msg)

    # --- Anthropic Claude API Call ---
    def _call_anthropic(self, system_prompt: str, user_prompt: str, json_mode: bool) -> str:
        client = self.anthropic_client
        
        # Anthropic supports system prompts in a separate parameter
        model = "claude-3-5-sonnet-20241022"
        
        # Prepare content
        prompt = user_prompt
        if json_mode:
            prompt += "\n\nCRITICAL: Respond ONLY with a valid JSON object. Do not include markdown code block formatting (like ```json), commentary or extra text."

        message = client.messages.create(
            model=model,
            max_tokens=4000,
            temperature=0.0 if json_mode else 0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    # --- Google Gemini API Call ---
    def _call_gemini(self, system_prompt: str, user_prompt: str, json_mode: bool) -> str:
        self.configure_gemini()
        
        model_name = "gemini-1.5-flash"
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt
        )
        
        generation_config = {}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"
            generation_config["temperature"] = 0.0
        else:
            generation_config["temperature"] = 0.7

        response = model.generate_content(
            user_prompt,
            generation_config=generation_config
        )
        return response.text

    # --- Groq Llama API Call ---
    def _call_groq(self, system_prompt: str, user_prompt: str, json_mode: bool) -> str:
        client = self.groq_client
        model = "llama-3.3-70b-versatile"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response_format = {"type": "json_object"} if json_mode else None
        
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.0 if json_mode else 0.7,
            response_format=response_format
        )
        return completion.choices[0].message.content

    # --- NVIDIA NIM API Call ---
    def _call_nvidia(self, system_prompt: str, user_prompt: str, json_mode: bool) -> str:
        # Call NVIDIA NIM using standard OpenAI compatibility endpoint via HTTP POST
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta/llama3-70b-instruct", # standard model on NVIDIA NIM
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0 if json_mode else 0.7,
            "max_tokens": 1024
        }
        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
            
        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]

# Single global instance
ai_provider = AIProviderService()
