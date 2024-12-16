from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from quantum_rag import QuantumRAG, RealityMetrics, MetalConfig

app = FastAPI(title="Cortex API Server")

# Initialize Quantum RAG with Metal acceleration
metal_config = MetalConfig(
    batch_size=32,
    max_sequence_length=2048,
    quantization_bits=8
)
quantum_rag = QuantumRAG(metal_config=metal_config)

class GenerateRequest(BaseModel):
    prompt: str
    context: Dict[str, Any] | None = None

class GenerateResponse(BaseModel):
    ideas: List[str]
    metrics: Dict[str, float]
    device_info: Dict[str, str]
    status: str

class FeedbackRequest(BaseModel):
    session_id: str
    feedback_score: float
    comments: str | None = None

@app.post("/generate", response_model=GenerateResponse)
async def generate_ideas(request: GenerateRequest):
    """Generate creative ideas using quantum-inspired RAG"""
    try:
        # Retrieve and validate using quantum RAG
        docs, metrics = await quantum_rag.retrieve_and_validate(request.prompt)
        
        # Extract ideas from retrieved documents
        ideas = [doc.page_content.split('\n')[0] for doc in docs]
        
        # Get device information
        device_info = quantum_rag.get_device_info()
        
        return GenerateResponse(
            ideas=ideas,
            metrics={
                "token_confidence": metrics.token_confidence,
                "context_coherence": metrics.context_coherence,
                "retrieval_relevance": metrics.retrieval_relevance,
                "human_trust": metrics.human_trust
            },
            device_info=device_info,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit human feedback for reality metrics adjustment"""
    try:
        quantum_rag.update_human_trust(request.feedback_score)
        return {"status": "success", "message": "Feedback incorporated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    device_info = quantum_rag.get_device_info()
    return {
        "status": "healthy",
        "metal_acceleration": device_info
    }
