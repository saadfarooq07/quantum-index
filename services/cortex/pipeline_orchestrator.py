from typing import Optional, Union, Dict, List
import torch
from transformers import AutoModel, AutoTokenizer
from .metal_accelerator import MetalAccelerator, MetalConfig
import httpx
from pydantic import BaseModel
import numpy as np
from enum import Enum

class ModelType(str, Enum):
    LOCAL_M3 = "local_m3"
    REMOTE_NVIDIA = "remote_nvidia"
    AUTO = "auto"  # Automatically choose based on input size and model availability

class PipelineType(str, Enum):
    CORTEX = "cortex"      # General purpose neural processing
    JAN = "jan"           # JAX-based numerical acceleration
    GRAPH_ML = "graph_ml"  # Graph neural networks

class PipelineRequest(BaseModel):
    input_text: Union[str, List[str]]
    model_type: ModelType = ModelType.AUTO
    pipeline_type: PipelineType
    max_length: int = 2048
    temperature: float = 0.7
    remote_endpoint: Optional[str] = None

class PipelineOrchestrator:
    def __init__(self):
        self.metal_config = MetalConfig()
        self.accelerator = MetalAccelerator(self.metal_config)
        self.local_models: Dict[str, torch.nn.Module] = {}
        self.tokenizers: Dict[str, AutoTokenizer] = {}
        
    async def _load_local_model(self, pipeline_type: PipelineType):
        """Load appropriate model based on pipeline type"""
        if pipeline_type not in self.local_models:
            if pipeline_type == PipelineType.CORTEX:
                model_name = "facebook/opt-350m"  # Smaller model optimized for M3
            elif pipeline_type == PipelineType.JAN:
                model_name = "google/flan-t5-small"  # Good for numerical tasks
            elif pipeline_type == PipelineType.GRAPH_ML:
                model_name = "microsoft/graphormer-base"  # Graph-focused model
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
            
            # Optimize for Metal
            model = self.accelerator.prepare_model(model)
            
            self.local_models[pipeline_type] = model
            self.tokenizers[pipeline_type] = tokenizer
    
    async def _process_local(self, request: PipelineRequest) -> Dict:
        """Process using local M3 acceleration"""
        await self._load_local_model(request.pipeline_type)
        
        model = self.local_models[request.pipeline_type]
        tokenizer = self.tokenizers[request.pipeline_type]
        
        inputs = tokenizer(
            request.input_text,
            max_length=request.max_length,
            truncation=True,
            padding=True,
            return_tensors="pt"
        ).to(self.metal_config.device)
        
        with torch.no_grad():
            outputs = model(**inputs)
            
        return {
            "embeddings": outputs.last_hidden_state.mean(dim=1).cpu().numpy().tolist(),
            "model_type": "local_m3",
            "pipeline": request.pipeline_type
        }
    
    async def _process_remote(self, request: PipelineRequest) -> Dict:
        """Process using remote NVIDIA model"""
        if not request.remote_endpoint:
            raise ValueError("Remote endpoint must be specified for NVIDIA processing")
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                request.remote_endpoint,
                json={
                    "inputs": request.input_text,
                    "parameters": {
                        "max_length": request.max_length,
                        "temperature": request.temperature
                    }
                }
            )
            return response.json()
    
    def _should_use_remote(self, request: PipelineRequest) -> bool:
        """Determine if we should use remote processing"""
        if request.model_type == ModelType.LOCAL_M3:
            return False
        elif request.model_type == ModelType.REMOTE_NVIDIA:
            return True
            
        # Auto decision based on input size and complexity
        if isinstance(request.input_text, list):
            total_length = sum(len(text) for text in request.input_text)
        else:
            total_length = len(request.input_text)
            
        # Use remote for large inputs or graph processing
        return total_length > 10000 or request.pipeline_type == PipelineType.GRAPH_ML
    
    async def process(self, request: PipelineRequest) -> Dict:
        """Main processing entry point"""
        use_remote = self._should_use_remote(request)
        
        try:
            if use_remote:
                return await self._process_remote(request)
            else:
                return await self._process_local(request)
        except Exception as e:
            # Fallback to remote if local processing fails
            if not use_remote and request.remote_endpoint:
                return await self._process_remote(request)
            raise e
