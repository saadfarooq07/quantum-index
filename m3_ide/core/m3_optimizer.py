import torch
import numpy as np
from typing import Optional, List, Dict, Any
from .config import M3Config

class M3Optimizer:
    """Optimizes model execution for M3 chips"""
    def __init__(self, config: M3Config):
        self.config = config
        self.device = self._setup_device()
        self._setup_thread_pool()
        
    def _setup_device(self) -> torch.device:
        """Set up MPS device if available"""
        if self.config.mps_enabled and torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
        
    def _setup_thread_pool(self) -> None:
        """Configure thread pool for optimal M3 performance"""
        torch.set_num_threads(self.config.num_threads)
        if hasattr(torch, 'set_num_interop_threads'):
            torch.set_num_interop_threads(self.config.num_threads // 2)
            
    def quantize_model(self, model: torch.nn.Module) -> torch.nn.Module:
        """Quantize model to INT8 if supported"""
        if self.config.quantization == "int8":
            try:
                return torch.quantization.quantize_dynamic(
                    model,
                    {torch.nn.Linear},
                    dtype=torch.qint8
                )
            except Exception as e:
                print(f"Quantization failed: {e}")
                return model
        return model
        
    def optimize_memory(self, model: torch.nn.Module) -> None:
        """Optimize memory usage for M3 chip"""
        # Enable gradient checkpointing if available
        if hasattr(model, 'gradient_checkpointing_enable'):
            model.gradient_checkpointing_enable()
            
        # Move model to MPS device if available
        model.to(self.device)
        
        # Clear CUDA cache if using MPS
        if self.device.type == "mps":
            torch.mps.empty_cache()
            
    def create_execution_plan(self, model: torch.nn.Module, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Create optimized execution plan for inputs"""
        plan = {
            "device": self.device,
            "batch_size": self._optimal_batch_size(inputs),
            "precision": "int8" if self.config.quantization == "int8" else "fp32",
            "thread_count": self.config.num_threads
        }
        
        # Add memory optimization hints
        if hasattr(model, "get_memory_footprint"):
            plan["memory_footprint"] = model.get_memory_footprint()
            
        return plan
        
    def _optimal_batch_size(self, inputs: Dict[str, Any]) -> int:
        """Calculate optimal batch size based on input size and memory"""
        total_size = sum(
            tensor.element_size() * tensor.nelement()
            for tensor in inputs.values()
            if isinstance(tensor, torch.Tensor)
        )
        
        # Adjust batch size based on available memory
        available_memory = self.config.memory_limit * 1024 * 1024  # Convert to bytes
        return min(32, max(1, available_memory // (total_size * 2)))
        
    def profile_execution(self, model: torch.nn.Module, inputs: Dict[str, Any]) -> Dict[str, float]:
        """Profile model execution for performance metrics"""
        metrics = {}
        
        # Measure memory usage
        if self.device.type == "mps":
            metrics["memory_allocated"] = torch.mps.current_allocated_memory() / 1024**2
            metrics["memory_reserved"] = torch.mps.driver_allocated_memory() / 1024**2
            
        # Measure execution time
        start_event = torch.cuda.Event(enable_timing=True)
        end_event = torch.cuda.Event(enable_timing=True)
        
        start_event.record()
        with torch.no_grad():
            model(**inputs)
        end_event.record()
        
        torch.cuda.synchronize()
        metrics["execution_time"] = start_event.elapsed_time(end_event)
        
        return metrics
        
    def cleanup(self) -> None:
        """Clean up resources"""
        if self.device.type == "mps":
            torch.mps.empty_cache()
        torch.cuda.empty_cache()
