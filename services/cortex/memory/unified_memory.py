"""
Unified Memory Management for M3 Architecture
"""
import torch
import numpy as np
from typing import Dict, Optional, Any
import threading
import weakref
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class MemoryRegion:
    """Memory region allocation details"""
    size: int
    in_use: bool
    last_access: float
    priority: int

class UnifiedMemoryManager:
    """Manage unified memory allocation for M3"""
    
    def __init__(self, max_memory_gb: int = 24):  # Default 24GB for safe allocation
        self.max_memory = max_memory_gb * 1024 * 1024 * 1024  # Convert to bytes
        self.allocated_regions: Dict[int, MemoryRegion] = {}
        self.lock = threading.Lock()
        self._cleanup_executor = ThreadPoolExecutor(max_workers=1)
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    
    def allocate(self, size: int, priority: int = 0) -> Optional[int]:
        """Allocate memory with priority"""
        with self.lock:
            if self._get_total_allocated() + size > self.max_memory:
                self._cleanup_low_priority()
            
            if self._get_total_allocated() + size <= self.max_memory:
                region_id = len(self.allocated_regions)
                self.allocated_regions[region_id] = MemoryRegion(
                    size=size,
                    in_use=True,
                    last_access=time.time(),
                    priority=priority
                )
                return region_id
            return None
    
    def free(self, region_id: int):
        """Free allocated memory region"""
        with self.lock:
            if region_id in self.allocated_regions:
                del self.allocated_regions[region_id]
    
    def _cleanup_low_priority(self):
        """Clean up low priority allocations"""
        with self.lock:
            to_remove = []
            for region_id, region in self.allocated_regions.items():
                if not region.in_use and region.priority < 1:
                    to_remove.append(region_id)
            
            for region_id in to_remove:
                self.free(region_id)
    
    def _get_total_allocated(self) -> int:
        """Get total allocated memory"""
        return sum(region.size for region in self.allocated_regions.values())


class MetalMemoryOptimizer:
    """Optimize Metal memory usage"""
    
    def __init__(self):
        self.memory_manager = UnifiedMemoryManager()
        self.tensor_cache: Dict[str, weakref.ref] = {}
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    
    def optimize_tensor(self, tensor: torch.Tensor, name: str = "") -> torch.Tensor:
        """Optimize tensor memory allocation"""
        # Move to Metal device if available
        if self.device.type == "mps":
            tensor = tensor.to(self.device)
        
        # Cache using weak references
        if name:
            self.tensor_cache[name] = weakref.ref(tensor)
        
        return tensor
    
    def clear_cache(self):
        """Clear tensor cache"""
        self.tensor_cache.clear()
        if self.device.type == "mps":
            torch.mps.empty_cache()


class MemoryPool:
    """Memory pool for efficient tensor allocation"""
    
    def __init__(self, initial_size: int = 1024):
        self.pool: Dict[int, torch.Tensor] = {}
        self.available_sizes = [initial_size]
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    
    def get_tensor(self, size: int) -> torch.Tensor:
        """Get tensor from pool or allocate new"""
        best_size = min((s for s in self.available_sizes if s >= size), default=None)
        
        if best_size is None:
            # Allocate new size class
            new_size = max(size, max(self.available_sizes) * 2)
            self.available_sizes.append(new_size)
            tensor = torch.empty(new_size, device=self.device)
            self.pool[new_size] = tensor
            return tensor[:size]
        
        return self.pool[best_size][:size]
    
    def clear(self):
        """Clear memory pool"""
        self.pool.clear()
        if self.device.type == "mps":
            torch.mps.empty_cache()
