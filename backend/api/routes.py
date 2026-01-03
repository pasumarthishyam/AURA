"""
REST API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.agent_service import agent_service


router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    success: bool
    message: str
    trace: list


class InitResponse(BaseModel):
    success: bool
    message: str


class StatusResponse(BaseModel):
    initialized: bool
    gpu: str


@router.post("/initialize", response_model=InitResponse)
async def initialize_agent():
    """Initialize the AURA agent system."""
    result = agent_service.initialize()
    return InitResponse(**result)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the agent and get a response."""
    if not agent_service.is_initialized:
        raise HTTPException(
            status_code=400,
            detail="Agent not initialized. Call /api/initialize first."
        )
    
    result = agent_service.run(request.message)
    return ChatResponse(**result)


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get the current system status."""
    result = agent_service.get_status()
    return StatusResponse(**result)
