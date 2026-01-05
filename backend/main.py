"""
AURA Backend API
FastAPI server exposing the agent functionality.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router as api_router
from backend.api.websocket import router as ws_router
from backend.services.agent_service import agent_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("🚀 AURA Backend starting...")
    
    # Auto-initialize agent on startup
    print("🔧 Auto-initializing AURA agent...")
    result = agent_service.initialize()
    if result["success"]:
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Initialization failed: {result['message']}")
    
    yield
    print("👋 AURA Backend shutting down...")


app = FastAPI(
    title="AURA API",
    description="Backend API for AURA AI Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Allow Angular dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(api_router, prefix="/api", tags=["API"])
app.include_router(ws_router, tags=["WebSocket"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
