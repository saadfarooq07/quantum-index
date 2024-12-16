from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import psutil
import logging
from typing import Dict, Optional
from .metal_accelerator import MetalAccelerator, MetalConfig
from .pipeline_orchestrator import PipelineOrchestrator, PipelineRequest
from .resource_manager import ResourceManager, ResourcePriority
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cortex")

# Shared resources
resource_manager: Optional[ResourceManager] = None
metal_config: Optional[MetalConfig] = None
accelerator: Optional[MetalAccelerator] = None
pipeline: Optional[PipelineOrchestrator] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize shared resources
    global resource_manager, metal_config, accelerator, pipeline
    resource_manager = await ResourceManager().start()
    metal_config = MetalConfig()
    accelerator = MetalAccelerator(metal_config)
    pipeline = PipelineOrchestrator()
    
    try:
        yield
    finally:
        # Cleanup
        if resource_manager:
            for pid in list(resource_manager.processes.keys()):
                await resource_manager.unregister_process(pid)

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "device": metal_config.device,
        "metal_available": torch.backends.mps.is_available(),
        "torch_version": torch.__version__
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/metrics")
async def get_metrics():
    """Get current system metrics."""
    if not resource_manager:
        return {"error": "Resource manager not initialized"}
    
    try:
        metrics = await resource_manager.get_resource_metrics()
        return {
            "status": "success",
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/register/{process_name}")
async def register_process(process_name: str, priority: ResourcePriority):
    """Register a process for resource management."""
    if not resource_manager:
        return {"error": "Resource manager not initialized"}
    
    try:
        pid = psutil.Process().pid
        await resource_manager.register_process(pid, process_name, priority)
        return {
            "status": "success",
            "pid": pid,
            "message": f"Registered process {process_name} with PID {pid}"
        }
    except Exception as e:
        logger.error(f"Error registering process: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.delete("/unregister/{pid}")
async def unregister_process(pid: int):
    """Unregister a process from resource management."""
    if not resource_manager:
        return {"error": "Resource manager not initialized"}
    
    try:
        await resource_manager.unregister_process(pid)
        return {
            "status": "success",
            "message": f"Unregistered process with PID {pid}"
        }
    except Exception as e:
        logger.error(f"Error unregistering process: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/process")
async def process_pipeline(request: PipelineRequest):
    """
    Process input through the selected ML pipeline
    """
    try:
        result = await pipeline.process(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        workers=2,  # Adjust based on CPU cores
        loop="uvloop",  # Use uvloop for better performance
        log_level="info",
        reload=False  # Disable reload in production
    )
