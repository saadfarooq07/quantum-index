from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import docling
import json

app = FastAPI(title="Docling API Server")
analyzer = docling.DocumentAnalyzer()

class AnalysisRequest(BaseModel):
    text: str
    context: Optional[Dict] = None
    quantum_state: Optional[Dict] = None

class AnalysisResponse(BaseModel):
    entities: List[Dict[str, Any]]
    topics: List[str]
    summary: str
    quantum_state: Dict[str, Any]
    confidence: float

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(request: AnalysisRequest):
    """Analyze text using Docling"""
    try:
        result = analyzer.analyze(
            request.text,
            context=request.context,
            quantum_state=request.quantum_state
        )
        
        # Add timestamp to quantum state
        result['quantum_state']['timestamp'] = datetime.now().isoformat()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and analyze a document file"""
    try:
        content = await file.read()
        text = content.decode()
        
        result = analyzer.analyze(
            text,
            context={"filename": file.filename},
            quantum_state=None
        )
        
        # Add timestamp to quantum state
        result['quantum_state'] = {
            "timestamp": datetime.now().isoformat(),
            "filename": file.filename
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
