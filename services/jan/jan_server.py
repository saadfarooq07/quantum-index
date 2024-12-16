from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from m3_ide.api.jan_client import JANClient

app = FastAPI(title="JAN API Server")
client = JANClient()

class CodeAnalysisRequest(BaseModel):
    code: str
    context: Optional[Dict] = None
    quantum_state: Optional[Dict] = None

class CodeAnalysisResponse(BaseModel):
    suggestions: List[str]
    improvements: List[Dict[str, Any]]
    quantum_state: Dict[str, Any]
    confidence: float

@app.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze code using quantum-inspired JAN"""
    try:
        result = client.analyze_code(
            request.code,
            request.context,
            request.quantum_state
        )
        
        # Add timestamp to quantum state
        result['quantum_state']['timestamp'] = datetime.now().isoformat()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time code analysis"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            # Process the code analysis request
            result = client.analyze_code(
                request_data['code'],
                request_data.get('context'),
                request_data.get('quantum_state')
            )
            
            # Add timestamp
            result['quantum_state']['timestamp'] = datetime.now().isoformat()
            
            await websocket.send_json(result)
    except Exception as e:
        await websocket.close(code=1000, reason=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
