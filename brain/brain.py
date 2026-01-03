import json
import re
from brain.gemini_client import GeminiClient
from brain.prompt import SYSTEM_PROMPT


class Brain:
    """
    Decision-making component.
    Uses Google Gemini to decide the next action.
    """

    def __init__(self):
        # Initialize Gemini Client
        self.llm = GeminiClient()

    def next_action(
        self,
        goal: str,
        memory_context: str,
        last_observation,
        last_error,
        step_state,
    ) -> dict:
        """
        Decide the next action or STOP.
        """

        prompt = f"""
{SYSTEM_PROMPT}

USER GOAL:
{goal}

RELEVANT MEMORY:
{memory_context}

LAST OBSERVATION:
{last_observation}

LAST ERROR:
{last_error}

CURRENT STEP:
{step_state.step_count}

Respond with JSON only.
"""

        raw_output = self.llm.generate_response(prompt)
        
        # --- Clean Markdown Fencing ---
        # Gemini often supports "```json ... ```"
        clean_output = self._clean_json(raw_output)

        # --- Strict JSON enforcement ---
        try:
            action = json.loads(clean_output)
        except json.JSONDecodeError:
            # Emergency fallback (safe stop)
            return {
                "type": "STOP",
                "message": f"Stopped due to invalid model output: {raw_output[:100]}..."
            }

        # --- Minimal validation ---
        if "type" not in action:
            return {
                "type": "STOP",
                "message": "Stopped due to malformed action (missing 'type')."
            }

        return action

    def _clean_json(self, text: str) -> str:
        """
        Removes markdown code fences if present.
        """
        text = text.strip()
        # Remove ```json and ``` or just ```
        if text.startswith("```"):
            # Find the first newline
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[first_newline+1:]
            # Remove trailing ```
            if text.endswith("```"):
                text = text[:-3]
        return text.strip()
