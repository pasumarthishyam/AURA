"""
Agent Service - Singleton wrapper around CoreAgentController.
"""
from typing import Optional
import sys
import os
from pathlib import Path

# Load .env file before anything else
from dotenv import load_dotenv

# Find the project root (where .env is located)
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Add parent directory to path for imports
sys.path.insert(0, str(project_root))

from core_controller import CoreAgentController, AgentResult
from brain.brain import Brain
from tools.executor import Executor
from perception.voice import VoiceEngine
from memory.memory_system import MemorySystem
from safety.safety import Safety



class AgentService:
    """
    Singleton service managing the agent lifecycle.
    """
    _instance: Optional["AgentService"] = None
    _agent: Optional[CoreAgentController] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized
    
    def initialize(self) -> dict:
        """
        Initialize all agent components.
        Returns success status and message.
        """
        if self._initialized:
            return {"success": True, "message": "Already initialized"}
        
        try:
            # Initialize components
            brain = Brain()
            executor = Executor()
            perception = VoiceEngine()
            memory = MemorySystem()
            safety = Safety()
            
            # Create controller
            self._agent = CoreAgentController(
                brain=brain,
                executor=executor,
                perception=perception,
                memory=memory,
                safety=safety
            )
            
            self._initialized = True
            return {"success": True, "message": "AURA initialized successfully"}
            
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def run(self, message: str) -> dict:
        """
        Run the agent with a user message.
        Returns the AgentResult as a dict.
        """
        if not self._initialized or self._agent is None:
            return {
                "success": False,
                "message": "Agent not initialized. Call /api/initialize first.",
                "trace": []
            }
        
        try:
            result: AgentResult = self._agent.run(message)
            
            # Convert trace to serializable format
            trace_data = []
            for step in result.trace.steps:
                trace_data.append({
                    "step_id": step.step_id,
                    "action": step.action,
                    "success": step.success,
                    "result": str(step.result) if step.result else None,
                    "observation": str(step.observation) if step.observation else None,
                    "error": step.error,
                    "timestamp": step.timestamp
                })
            
            return {
                "success": result.success,
                "message": result.message,
                "trace": trace_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "trace": []
            }
    
    def get_status(self) -> dict:
        """Get current system status."""
        return {
            "initialized": self._initialized,
            "gpu": "NVIDIA RTX 3050" if self._initialized else "Not active"
        }


# Global instance
agent_service = AgentService()
