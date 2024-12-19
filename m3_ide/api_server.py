from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn
import asyncio
from typing import Dict, Any, Optional, List
import numpy as np
import time
import os
from .metal_utils import MetalCompute
from transformers import AutoTokenizer
import json
from datetime import datetime
import logging
import psutil
import threading
from collections import deque
from functools import partial

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('metal_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.request_times = deque(maxlen=1000)
        self.error_counts = {}
        self.last_gc_time = time.time()
        self.metal_usage = deque(maxlen=100)
        self.start_time = time.time()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        while True:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                
                # Update metal usage (simplified)
                self.metal_usage.append({
                    'timestamp': time.time(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent
                })
                
                # Garbage collection if needed
                if time.time() - self.last_gc_time > 300:  # 5 minutes
                    self._cleanup_old_data()
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(5)  # Back off on error
    
    def _cleanup_old_data(self):
        current_time = time.time()
        self.last_gc_time = current_time
    
    def record_request(self, duration: float, endpoint: str, status_code: int):
        self.request_times.append({
            'timestamp': time.time(),
            'duration': duration,
            'endpoint': endpoint,
            'status_code': status_code
        })
    
    def record_error(self, error_type: str, error_message: str):
        if error_type not in self.error_counts:
            self.error_counts[error_type] = []
        self.error_counts[error_type].append({
            'timestamp': time.time(),
            'message': error_message
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        current_time = time.time()
        
        # Calculate request metrics
        recent_requests = [r for r in self.request_times 
                         if current_time - r['timestamp'] < 300]  # Last 5 minutes
        
        if recent_requests:
            avg_latency = sum(r['duration'] for r in recent_requests) / len(recent_requests)
            success_rate = sum(1 for r in recent_requests if r['status_code'] < 400) / len(recent_requests)
        else:
            avg_latency = 0
            success_rate = 1
        
        # Calculate Metal usage
        recent_metal = list(self.metal_usage)
        if recent_metal:
            avg_cpu = sum(m['cpu_percent'] for m in recent_metal) / len(recent_metal)
            avg_memory = sum(m['memory_percent'] for m in recent_metal) / len(recent_metal)
        else:
            avg_cpu = 0
            avg_memory = 0
        
        return {
            'uptime_seconds': current_time - self.start_time,
            'request_metrics': {
                'total_requests': len(self.request_times),
                'recent_requests': len(recent_requests),
                'average_latency': avg_latency,
                'success_rate': success_rate
            },
            'error_metrics': {
                error_type: len(errors)
                for error_type, errors in self.error_counts.items()
            },
            'system_metrics': {
                'cpu_percent': avg_cpu,
                'memory_percent': avg_memory,
                'metal_utilization': min(avg_cpu / 100, 1.0)  # Simplified metric
            }
        }

class APIRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: Optional[int] = Field(default=100, ge=1, le=512)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    stream: Optional[bool] = False

class EmbeddingRequest(BaseModel):
    text: str
    quantize: bool = True

class SearchRequest(BaseModel):
    query_embedding: List[float]
    top_k: int = Field(default=10, ge=1, le=100)

class MetalAccelerator:
    def __init__(self):
        self.shader_path = os.path.join(os.path.dirname(__file__), 'Shaders.metal')
        self.metal = MetalCompute(self.shader_path)
        self.tokenizer = AutoTokenizer.from_pretrained('gpt2')
        self.monitor = PerformanceMonitor()
        
    async def initialize(self):
        if not self.metal.initialize():
            raise RuntimeError("Failed to initialize Metal resources")
        logger.info(f"Metal accelerator initialized on device: {self.metal.device.name()}")
        return self.metal.shared_buffers
    
    async def process_request_stream(self, request: APIRequest):
        """Process request with streaming support"""
        try:
            # Tokenize input
            tokens = self.tokenizer.encode(request.prompt)
            if len(tokens) > self.metal.MAX_SEQ_LENGTH:
                tokens = tokens[:self.metal.MAX_SEQ_LENGTH]
            
            # Process tokens in chunks
            chunk_size = 32  # Adjust based on performance needs
            for i in range(0, len(tokens), chunk_size):
                chunk = tokens[i:i + chunk_size]
                
                # Convert chunk to float array
                input_data = np.array(chunk, dtype=np.float32) / self.tokenizer.vocab_size
                
                # Process through Metal pipeline
                result = self.metal.process_sequence(input_data)
                if result is None:
                    raise RuntimeError("Metal processing failed")
                
                # Convert result back to tokens
                result_tokens = (result * self.tokenizer.vocab_size).astype(np.int32)
                response = self.tokenizer.decode(result_tokens)
                
                # Yield chunk result
                yield {
                    "choices": [{
                        "text": response,
                        "index": 0,
                        "finish_reason": None
                    }]
                }
            
            # Final response
            yield {
                "choices": [{
                    "text": "",
                    "index": 0,
                    "finish_reason": "stop"
                }]
            }
            
        except Exception as e:
            logger.error(f"Error in stream processing: {e}", exc_info=True)
            self.monitor.record_error("stream_processing", str(e))
            raise

    async def process_request(self, request: APIRequest) -> str:
        start_time = time.time()
        success = False
        
        try:
            # Tokenize input
            tokens = self.tokenizer.encode(request.prompt)
            if len(tokens) > self.metal.MAX_SEQ_LENGTH:
                tokens = tokens[:self.metal.MAX_SEQ_LENGTH]
            
            # Convert tokens to float array
            input_data = np.array(tokens, dtype=np.float32) / self.tokenizer.vocab_size
            
            # Process through Metal pipeline
            result = self.metal.process_sequence(input_data)
            if result is None:
                raise RuntimeError("Metal processing failed")
            
            # Convert result back to tokens
            result_tokens = (result * self.tokenizer.vocab_size).astype(np.int32)
            response = self.tokenizer.decode(result_tokens)
            
            success = True
            return response
            
        finally:
            duration = time.time() - start_time
            self.monitor.record_request(
                duration=duration,
                endpoint="/v1/completions",
                status_code=200 if success else 500
            )

    async def create_embedding(self, request: EmbeddingRequest):
        try:
            # Tokenize input
            tokens = self.tokenizer.encode(request.text)
            if len(tokens) > self.metal.MAX_SEQ_LENGTH:
                tokens = tokens[:self.metal.MAX_SEQ_LENGTH]
            
            # Convert to embeddings
            input_data = np.array(tokens, dtype=np.float32) / self.tokenizer.vocab_size
            embedding = self.metal.process_sequence(input_data)
            
            if embedding is None:
                raise RuntimeError("Embedding generation failed")
            
            # Quantize if requested
            if request.quantize:
                embedding = self.metal.quantize_embeddings(embedding)
                if embedding is None:
                    raise RuntimeError("Quantization failed")
            
            return embedding
        
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}", exc_info=True)
            self.monitor.record_error("embedding", str(e))
            raise

    async def vector_search(self, request: SearchRequest):
        try:
            # Convert query to numpy array
            query = np.array(request.query_embedding, dtype=np.uint8)
            
            # Load database (in practice, you'd want to cache this)
            database = self.metal.shared_buffers.get('embedding_database')
            if database is None:
                raise HTTPException(status_code=400, detail="No embedding database loaded")
            
            # Perform IP search
            indices, scores = self.metal.ip_search(
                query, database, k=request.top_k
            )
            
            if indices is None or scores is None:
                raise RuntimeError("Search failed")
            
            return indices, scores
        
        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}", exc_info=True)
            self.monitor.record_error("search", str(e))
            raise

app = FastAPI(
    title="Metal-Accelerated API Server",
    description="High-performance API server leveraging Apple Metal for acceleration",
    version="1.0.0"
)
metal_accelerator = MetalAccelerator()

@app.on_event("startup")
async def startup():
    await metal_accelerator.initialize()

@app.post("/v1/completions")
async def completions(request: APIRequest, background_tasks: BackgroundTasks):
    try:
        if request.stream:
            # Return streaming response
            return StreamingResponse(
                metal_accelerator.process_request_stream(request),
                media_type="text/event-stream"
            )
        
        # Use Metal acceleration for processing
        result = await metal_accelerator.process_request(request)
        
        response = {
            "id": f"metal-{request.model}-{int(time.time())}",
            "object": "text_completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "text": result,
                "index": 0,
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(request.prompt),
                "completion_tokens": len(result),
                "total_tokens": len(request.prompt) + len(result)
            }
        }
        
        # Log request asynchronously
        background_tasks.add_task(
            logger.info,
            f"Processed request: {json.dumps(response, indent=2)}"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        metal_accelerator.monitor.record_error("request_processing", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/embeddings")
async def create_embedding(request: EmbeddingRequest, background_tasks: BackgroundTasks):
    try:
        start_time = time.time()
        
        # Generate embedding
        embedding = await metal_accelerator.create_embedding(request)
        
        response = {
            "object": "embedding",
            "embedding": embedding.tolist(),
            "index": 0,
            "model": "metal-m3"
        }
        
        # Log request
        duration = time.time() - start_time
        metal_accelerator.monitor.record_request(
            duration=duration,
            endpoint="/v1/embeddings",
            status_code=200
        )
        
        background_tasks.add_task(
            logger.info,
            f"Generated embedding: shape={embedding.shape}, quantized={request.quantize}"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}", exc_info=True)
        metal_accelerator.monitor.record_error("embedding", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/search")
async def vector_search(request: SearchRequest, background_tasks: BackgroundTasks):
    try:
        start_time = time.time()
        
        # Perform vector search
        indices, scores = await metal_accelerator.vector_search(request)
        
        response = {
            "object": "search_results",
            "results": [
                {
                    "index": int(idx),
                    "score": float(score)
                }
                for idx, score in zip(indices, scores)
            ],
            "model": "metal-m3"
        }
        
        # Log request
        duration = time.time() - start_time
        metal_accelerator.monitor.record_request(
            duration=duration,
            endpoint="/v1/search",
            status_code=200
        )
        
        background_tasks.add_task(
            logger.info,
            f"Vector search: top_k={request.top_k}, results={len(indices)}"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in vector search: {str(e)}", exc_info=True)
        metal_accelerator.monitor.record_error("search", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    try:
        device_info = metal_accelerator.metal.device
        is_healthy = (
            device_info is not None and
            not device_info.isLowPower() and
            device_info.maxBufferLength() > 0
        )
        
        response = {
            "status": "healthy" if is_healthy else "degraded",
            "metal_device": device_info.name(),
            "timestamp": int(time.time())
        }
        
        return response
    except Exception as e:
        metal_accelerator.monitor.record_error("health_check", str(e))
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/metrics")
async def get_metrics():
    try:
        metrics = metal_accelerator.monitor.get_metrics()
        device_info = metal_accelerator.metal.device
        
        return {
            "metrics": metrics,
            "device": {
                "name": device_info.name(),
                "is_low_power": device_info.isLowPower(),
                "max_buffer_length": device_info.maxBufferLength()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        metal_accelerator.monitor.record_error("metrics", str(e))
        raise HTTPException(status_code=500, detail="Failed to get metrics")

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
