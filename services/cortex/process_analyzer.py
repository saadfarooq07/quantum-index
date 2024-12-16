from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import psutil
import torch
import numpy as np
from collections import deque
import networkx as nx
from datetime import datetime
import asyncio
from .metal_accelerator import MetalAccelerator, MetalConfig
from transformers import AutoModel, AutoTokenizer

@dataclass
class ProcessMetrics:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    num_threads: int
    status: str
    create_time: float
    children: List[int]
    parent: Optional[int]
    connections: List[Dict]
    io_counters: Optional[Dict]
    anomaly_score: float = 0.0
    context_score: float = 0.0

class ProcessAnalyzer:
    def __init__(self, metal_config: Optional[MetalConfig] = None):
        self.metal_config = metal_config or MetalConfig()
        self.accelerator = MetalAccelerator(self.metal_config)
        self.process_graph = nx.DiGraph()
        self.history = {}  # pid -> deque(ProcessMetrics)
        self.history_length = 100
        self.embeddings_cache = {}
        
        # Load M3-optimized models
        self.load_models()
        
        # Start background tasks
        self.running = True
        self.update_task = asyncio.create_task(self._update_loop())
    
    async def _update_loop(self):
        """Background task to update process metrics and relationships"""
        while self.running:
            await self.update_process_graph()
            await asyncio.sleep(1)
    
    def load_models(self):
        """Load models optimized for M3"""
        self.model = AutoModel.from_pretrained("microsoft/codebert-base")
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        self.model = self.accelerator.prepare_model(self.model)
    
    async def update_process_graph(self):
        """Update process graph with current system state"""
        new_graph = nx.DiGraph()
        processes = {}
        
        # Collect all processes
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 
                                       'memory_percent', 'num_threads', 'status',
                                       'create_time', 'connections', 'io_counters']):
            try:
                pinfo = proc.info
                parent = proc.parent().pid if proc.parent() else None
                children = [p.pid for p in proc.children()]
                
                metrics = ProcessMetrics(
                    pid=pinfo['pid'],
                    name=pinfo['name'],
                    cpu_percent=pinfo['cpu_percent'] or 0.0,
                    memory_percent=pinfo['memory_percent'] or 0.0,
                    num_threads=pinfo['num_threads'],
                    status=pinfo['status'],
                    create_time=pinfo['create_time'],
                    children=children,
                    parent=parent,
                    connections=pinfo['connections'],
                    io_counters=pinfo['io_counters']
                )
                
                # Update history
                if metrics.pid not in self.history:
                    self.history[metrics.pid] = deque(maxlen=self.history_length)
                self.history[metrics.pid].append(metrics)
                
                # Calculate anomaly score
                metrics.anomaly_score = self._calculate_anomaly_score(metrics)
                
                # Calculate context score using M3 model
                metrics.context_score = await self._calculate_context_score(metrics)
                
                processes[metrics.pid] = metrics
                new_graph.add_node(metrics.pid, **metrics.__dict__)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Add edges for relationships
        for pid, metrics in processes.items():
            # Parent-child relationships
            if metrics.parent:
                new_graph.add_edge(metrics.parent, pid, type='parent')
            for child in metrics.children:
                new_graph.add_edge(pid, child, type='child')
            
            # Network connections
            for conn in metrics.connections:
                if conn.raddr and conn.raddr[0]:
                    new_graph.add_edge(pid, f"net:{conn.raddr[0]}:{conn.raddr[1]}", 
                                     type='network')
        
        self.process_graph = new_graph
        return self.process_graph
    
    def _calculate_anomaly_score(self, metrics: ProcessMetrics) -> float:
        """Calculate anomaly score using historical data"""
        if len(self.history[metrics.pid]) < 2:
            return 0.0
            
        history = list(self.history[metrics.pid])
        
        # Calculate rate of change
        cpu_change = np.diff([h.cpu_percent for h in history])
        mem_change = np.diff([h.memory_percent for h in history])
        
        # Calculate z-scores
        cpu_zscore = np.abs(np.mean(cpu_change) / (np.std(cpu_change) + 1e-6))
        mem_zscore = np.abs(np.mean(mem_change) / (np.std(mem_change) + 1e-6))
        
        # Combine scores
        return float(0.6 * cpu_zscore + 0.4 * mem_zscore)
    
    async def _calculate_context_score(self, metrics: ProcessMetrics) -> float:
        """Calculate context relevance score using M3 model"""
        # Create process context
        context = f"""
        Process: {metrics.name} (PID: {metrics.pid})
        Status: {metrics.status}
        Threads: {metrics.num_threads}
        Network: {len(metrics.connections)} connections
        """
        
        # Get embedding
        inputs = self.tokenizer(
            context,
            max_length=512,
            truncation=True,
            padding=True,
            return_tensors="pt"
        ).to(self.accelerator.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1)
            
        # Cache embedding
        self.embeddings_cache[metrics.pid] = embedding
        
        # Calculate similarity with other processes
        if len(self.embeddings_cache) > 1:
            similarities = []
            for other_pid, other_emb in self.embeddings_cache.items():
                if other_pid != metrics.pid:
                    sim = torch.cosine_similarity(embedding, other_emb)
                    similarities.append(float(sim))
            return float(np.mean(similarities))
        
        return 0.0
    
    def get_process_insights(self, pid: int) -> Dict:
        """Get detailed insights for a specific process"""
        if pid not in self.process_graph:
            return {}
            
        process = self.process_graph.nodes[pid]
        
        # Get subgraph of related processes
        related = nx.ego_graph(self.process_graph, pid, radius=2)
        
        # Calculate relationship metrics
        relationship_score = len(related) / len(self.process_graph)
        
        # Get historical trends
        if pid in self.history:
            history = list(self.history[pid])
            cpu_trend = np.mean([h.cpu_percent for h in history[-10:]])
            mem_trend = np.mean([h.memory_percent for h in history[-10:]])
        else:
            cpu_trend = mem_trend = 0.0
        
        return {
            "process": process,
            "num_related": len(related) - 1,
            "relationship_score": relationship_score,
            "cpu_trend": cpu_trend,
            "mem_trend": mem_trend,
            "anomaly_score": process["anomaly_score"],
            "context_score": process["context_score"],
            "related_processes": [
                {
                    "pid": n,
                    "relationship": related.edges[pid, n]["type"] 
                        if (pid, n) in related.edges else "indirect"
                } for n in related.nodes if n != pid
            ]
        }
    
    async def stop(self):
        """Stop the analyzer and cleanup"""
        self.running = False
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
