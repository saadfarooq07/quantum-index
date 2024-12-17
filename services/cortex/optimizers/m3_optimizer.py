"""
M3 Optimization Layer for Metal Performance
"""
import torch
import numpy as np
from typing import Dict, List, Optional
import psutil
import logging

logger = logging.getLogger(__name__)

class M3ResourceMonitor:
    """Monitor and manage M3 system resources"""
    
    MEMORY_PRESSURE_THRESHOLD = 0.75  # 75% memory usage threshold
    
    def __init__(self):
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.initial_batch_size = 32
        self.current_batch_size = self.initial_batch_size
    
    def check_memory_pressure(self) -> float:
        """Check system memory pressure"""
        memory = psutil.virtual_memory()
        pressure = memory.percent / 100.0
        logger.info(f"Current memory pressure: {pressure:.2%}")
        return pressure
    
    def adjust_batch_size(self) -> int:
        """Dynamically adjust batch size based on memory pressure"""
        pressure = self.check_memory_pressure()
        
        if pressure > self.MEMORY_PRESSURE_THRESHOLD:
            self.current_batch_size = max(1, self.current_batch_size // 2)
            logger.warning(f"Memory pressure high, reducing batch size to {self.current_batch_size}")
        elif pressure < self.MEMORY_PRESSURE_THRESHOLD * 0.5:
            self.current_batch_size = min(self.initial_batch_size, self.current_batch_size * 2)
            logger.info(f"Memory pressure low, increasing batch size to {self.current_batch_size}")
        
        return self.current_batch_size


class M3Optimizer:
    """Optimize processing for M3 chips using Metal"""
    
    def __init__(self):
        self.resource_monitor = M3ResourceMonitor()
        self.device = self.resource_monitor.device
        self.batch_size = self.resource_monitor.current_batch_size
    
    def optimize_batch(self, tokens: torch.Tensor) -> torch.Tensor:
        """Process tokens in optimized batches"""
        self.batch_size = self.resource_monitor.adjust_batch_size()
        
        batches = torch.split(tokens, self.batch_size)
        results = []
        
        for batch in batches:
            # Move batch to MPS device
            batch = batch.to(self.device)
            
            # Process using Metal-optimized operations
            with torch.mps.device():
                processed = self._process_batch(batch)
            
            results.append(processed.cpu())
        
        return torch.cat(results)
    
    def _process_batch(self, batch: torch.Tensor) -> torch.Tensor:
        """Metal-optimized batch processing"""
        # Use native Metal operations where possible
        return torch.nn.functional.gelu(batch)  # Example activation


class MetalTensorProcessor:
    """Process tensors using Metal Performance Shaders"""
    
    def __init__(self):
        self.optimizer = M3Optimizer()
        self.cache: Dict[str, torch.Tensor] = {}
    
    def process_tensors(self, 
                       input_tensors: List[torch.Tensor], 
                       cache_key: Optional[str] = None) -> torch.Tensor:
        """Process tensors with caching support"""
        if cache_key and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Concatenate and process tensors
        combined = torch.cat(input_tensors)
        result = self.optimizer.optimize_batch(combined)
        
        if cache_key:
            self.cache[cache_key] = result
        
        return result
    
    def clear_cache(self):
        """Clear tensor cache when memory pressure is high"""
        if self.optimizer.resource_monitor.check_memory_pressure() > M3ResourceMonitor.MEMORY_PRESSURE_THRESHOLD:
            self.cache.clear()
            logger.info("Cleared tensor cache due to high memory pressure")


def get_metal_config() -> Dict:
    """Get current Metal configuration"""
    return {
        "device": "mps" if torch.backends.mps.is_available() else "cpu",
        "memory_pressure": psutil.virtual_memory().percent,
        "mps_available": torch.backends.mps.is_available(),
        "mps_current_allocated": torch.mps.current_allocated_memory() if torch.backends.mps.is_available() else 0,
        "mps_driver_version": torch.backends.mps.get_device_name() if torch.backends.mps.is_available() else None
    }
