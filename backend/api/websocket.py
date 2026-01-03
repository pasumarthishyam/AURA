"""
WebSocket handler for streaming chat responses.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from backend.services.agent_service import agent_service


router = APIRouter()


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat.
    Currently non-streaming, but ready for future enhancement.
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            request = json.loads(data)
            message = request.get("message", "")
            
            if not agent_service.is_initialized:
                await websocket.send_json({
                    "type": "error",
                    "content": "Agent not initialized"
                })
                continue
            
            # Send thinking indicator
            await websocket.send_json({
                "type": "thinking",
                "content": "Processing..."
            })
            
            # Run agent
            result = agent_service.run(message)
            
            # Send response
            await websocket.send_json({
                "type": "response",
                "content": result["message"],
                "success": result["success"],
                "trace": result["trace"]
            })
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": str(e)
        })
