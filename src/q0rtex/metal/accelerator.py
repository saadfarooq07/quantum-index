import torch
from typing import List, Dict
import torch.mps as mps

class MetalAccelerator:
    def __init__(self):
        self.device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
        self.model = None
        self.performance_metrics = {}
        
    def initialize_model(self):
        """Initialize the Metal-optimized model"""
        # Configure for M3 Pro GPU
        if torch.backends.mps.is_available():
            torch.mps.set_per_process_memory_fraction(0.7)
            torch.mps.empty_cache()
            
    async def embed_text(self, text: str) -> torch.Tensor:
        """Generate embeddings using Metal acceleration"""
        with torch.autocast(device_type="mps"):
            embeddings = self.model(text)
            return embeddings.to(self.device)
            
    def get_performance_metrics(self) -> Dict:
        """Get Metal performance statistics"""
        return {
            "device": str(self.device),
            "memory_allocated": torch.mps.current_allocated_memory() if self.device.type == "mps" else 0,
            "max_memory": torch.mps.max_memory_allocated() if self.device.type == "mps" else 0
        }

import torch
from typing import List, Dict
import torch.mps as mps

class MetalAccelerator:
    def __init__(self):
        self.device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
        self.model = None
        self.performance_metrics = {}
        
    def initialize_model(self):
        """Initialize the Metal-optimized model"""
        # Configure for M3 Pro GPU
        if torch.backends.mps.is_available():
            torch.mps.set_per_process_memory_fraction(0.7)
            torch.mps.empty_cache()
            
    async def embed_text(self, text: str) -> torch.Tensor:
        """Generate embeddings using Metal acceleration"""
        with torch.autocast(device_type="mps"):
            embeddings = self.model(text)
            return embeddings.to(self.device)
            
    def get_performance_metrics(self) -> Dict:
        """Get Metal performance statistics"""
        return {
            "device": str(self.device),
            "memory_allocated": torch.mps.current_allocated_memory() if self.device.type == "mps" else 0,
            "max_memory": torch.mps.max_memory_allocated() if self.device.type == "mps" else 0
        }

