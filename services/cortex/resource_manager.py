import psutil
import torch
import asyncio
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import numpy as np
import logging
from contextlib import asynccontextmanager

class ResourcePriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

@dataclass
class ProcessInfo:
    pid: int
    name: str
    priority: ResourcePriority
    memory_usage: float
    cpu_usage: float
    gpu_usage: Optional[float]
    created_at: float
    last_active: float

class ResourceThresholds:
    CPU_HIGH = 80.0
    CPU_CRITICAL = 90.0
    MEMORY_HIGH = 80.0
    MEMORY_CRITICAL = 90.0
    GPU_HIGH = 80.0
    GPU_CRITICAL = 90.0

class ResourceManager:
    def __init__(self):
        self.processes: Dict[int, ProcessInfo] = {}
        self.metal_device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.resource_locks: Dict[str, asyncio.Lock] = {
            "cpu": asyncio.Lock(),
            "memory": asyncio.Lock(),
            "gpu": asyncio.Lock()
        }
        self.managed_pids: Set[int] = set()
        self.logger = logging.getLogger("ResourceManager")
        self.metrics = {}
        self._setup_logging()
        
    async def start(self):
        """Initialize the resource manager and start monitoring"""
        self.monitor_task = asyncio.create_task(self.monitor_resources())
        return self
    
    def _setup_logging(self):
        handler = logging.FileHandler("resource_manager.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    async def register_process(self, pid: int, name: str, priority: ResourcePriority) -> None:
        """Register a new process for resource management"""
        try:
            process = psutil.Process(pid)
            info = ProcessInfo(
                pid=pid,
                name=name,
                priority=priority,
                memory_usage=process.memory_percent(),
                cpu_usage=process.cpu_percent(),
                gpu_usage=None,  # Will be updated by monitor
                created_at=process.create_time(),
                last_active=process.create_time()
            )
            self.processes[pid] = info
            self.managed_pids.add(pid)
            self.logger.info(f"Registered process {name} (PID: {pid}) with {priority} priority")
        except psutil.NoSuchProcess:
            self.logger.error(f"Failed to register process {pid}: Process not found")
    
    async def unregister_process(self, pid: int) -> None:
        """Unregister a process from resource management"""
        if pid in self.processes:
            del self.processes[pid]
            self.managed_pids.remove(pid)
            self.logger.info(f"Unregistered process {pid}")
    
    @asynccontextmanager
    async def resource_lock(self, resource_type: str, priority: ResourcePriority):
        """Acquire a resource lock with priority-based waiting"""
        lock = self.resource_locks[resource_type]
        wait_time = 0.1 * (4 - priority.value)  # Higher priority = shorter wait
        
        while True:
            if await self._can_acquire_resource(resource_type, priority):
                async with lock:
                    try:
                        yield
                    finally:
                        await self._release_resource(resource_type)
                break
            await asyncio.sleep(wait_time)
    
    async def _can_acquire_resource(self, resource_type: str, priority: ResourcePriority) -> bool:
        """Check if a resource can be acquired based on current usage and priority"""
        current_usage = await self._get_resource_usage(resource_type)
        
        if priority == ResourcePriority.CRITICAL:
            return True  # Critical processes always get resources
        
        thresholds = {
            "cpu": (ResourceThresholds.CPU_HIGH, ResourceThresholds.CPU_CRITICAL),
            "memory": (ResourceThresholds.MEMORY_HIGH, ResourceThresholds.MEMORY_CRITICAL),
            "gpu": (ResourceThresholds.GPU_HIGH, ResourceThresholds.GPU_CRITICAL)
        }
        
        high, critical = thresholds[resource_type]
        
        if current_usage >= critical:
            return priority.value >= ResourcePriority.HIGH
        elif current_usage >= high:
            return priority.value >= ResourcePriority.MEDIUM
        return True
    
    async def _release_resource(self, resource_type: str) -> None:
        """Release a resource lock"""
        self.logger.debug(f"Released {resource_type} resource")
    
    async def _get_resource_usage(self, resource_type: str) -> float:
        """Get current resource usage percentage"""
        if resource_type == "cpu":
            return psutil.cpu_percent()
        elif resource_type == "memory":
            return psutil.virtual_memory().percent
        elif resource_type == "gpu":
            if torch.backends.mps.is_available():
                # Estimate MPS usage based on active processes
                return len([p for p in self.processes.values() if p.gpu_usage is not None]) * 10.0
            return 0.0
    
    async def monitor_resources(self):
        """Monitor system resources and manage processes."""
        while True:
            try:
                # Get current resource usage
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Update metrics
                self.metrics = {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used': memory.used,
                    'memory_total': memory.total
                }
                
                # Check for high resource usage
                if cpu_percent > 80 or memory.percent > 80:
                    # Get all processes sorted by CPU usage
                    processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                        try:
                            if proc.info['pid'] in self.processes:
                                processes.append(proc)
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                    
                    # Sort by CPU usage
                    processes.sort(key=lambda x: x.info['cpu_percent'], reverse=True)
                    
                    # Suspend high CPU processes with low priority
                    for proc in processes:
                        if (proc.info['cpu_percent'] > 50 and 
                            self.processes[proc.info['pid']]['priority'] == ResourcePriority.LOW):
                            try:
                                proc.suspend()
                                await asyncio.sleep(5)  # Give system time to recover
                                proc.resume()
                            except psutil.NoSuchProcess:
                                continue
                
                # Cleanup dead processes
                for pid in list(self.processes.keys()):
                    if not psutil.pid_exists(pid):
                        del self.processes[pid]
                
                await asyncio.sleep(2)  # Reduced monitoring frequency
            except Exception as e:
                logging.error(f"Error in resource monitoring: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def get_resource_metrics(self) -> Dict:
        """Get current resource metrics for monitoring"""
        return self.metrics
