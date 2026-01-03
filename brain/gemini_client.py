import os
import google.generativeai as genai
from typing import List, Dict, Any, Optional

class GeminiClient:
    """
    Wrapper for Google's Gemini API to serve as the agent's brain.
    """
    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API Key not found. Please set GOOGLE_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=64,
                max_output_tokens=8192,
                # response_mime_type removed for SDK compatibility
            )
        )
        self.chat_session = None

    def start_chat(self, history: List[Dict[str, str]] = None):
        """
        Initializes a chat session with history.
        """
        gemini_history = []
        if history:
            for msg in history:
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})
        
        self.chat_session = self.model.start_chat(history=gemini_history)

    def generate_response(self, prompt: str) -> str:
        """
        Sends a prompt to the model and returns the text response.
        """
        if not self.chat_session:
            self.start_chat()
            
        try:
            response = self.chat_session.send_message(prompt)
            return response.text
        except Exception as e:
            return f"{{\"type\": \"ERROR\", \"message\": \"Gemini API Error: {str(e)}\"}}"

    def generate_content_oneshot(self, prompt: str, image_path: str = None) -> str:
        """
        One-off generation, useful for vision tasks.
        """
        content = [prompt]
        if image_path:
             # In a real scenario, we'd load the image data here using PIL or similar
             pass 
        
        response = self.model.generate_content(content)
        return response.text
