from typing import Dict, List, Optional, Set
import networkx as nx
import torch
import numpy as np
from dataclasses import dataclass
from .process_analyzer import ProcessAnalyzer, ProcessMetrics
from .metal_accelerator import MetalAccelerator, MetalConfig

@dataclass
class ProcessCluster:
    processes: List[int]
    center_pid: int
    similarity_score: float
    resource_impact: float
    interaction_score: float

class ProcessWeb:
    def __init__(self, 
                 analyzer: ProcessAnalyzer,
                 metal_config: Optional[MetalConfig] = None):
        self.analyzer = analyzer
        self.metal_config = metal_config or MetalConfig()
        self.accelerator = MetalAccelerator(self.metal_config)
        self.clusters: List[ProcessCluster] = []
        self.interaction_graph = nx.DiGraph()
        
    async def update(self):
        """Update the process web with current system state"""
        # Get latest process graph
        process_graph = self.analyzer.process_graph
        
        # Build interaction graph
        self.interaction_graph = nx.DiGraph()
        
        # Add process nodes
        for pid, data in process_graph.nodes(data=True):
            if isinstance(pid, int):  # Skip network nodes
                self.interaction_graph.add_node(
                    pid,
                    **{k: v for k, v in data.items() if k != 'connections'}
                )
        
        # Add weighted edges based on interactions
        for pid1 in self.interaction_graph.nodes():
            for pid2 in self.interaction_graph.nodes():
                if pid1 != pid2:
                    weight = self._calculate_interaction_weight(
                        process_graph, pid1, pid2
                    )
                    if weight > 0:
                        self.interaction_graph.add_edge(pid1, pid2, weight=weight)
        
        # Update clusters
        await self._update_clusters()
    
    def _calculate_interaction_weight(self, 
                                   graph: nx.DiGraph, 
                                   pid1: int, 
                                   pid2: int) -> float:
        """Calculate interaction weight between two processes"""
        weight = 0.0
        
        # Parent-child relationship
        if graph.has_edge(pid1, pid2) and graph.edges[pid1, pid2]['type'] in ['parent', 'child']:
            weight += 0.5
            
        # Network connection
        p1_nets = {n for n in graph.neighbors(pid1) if isinstance(n, str) and n.startswith('net:')}
        p2_nets = {n for n in graph.neighbors(pid2) if isinstance(n, str) and n.startswith('net:')}
        shared_nets = p1_nets.intersection(p2_nets)
        if shared_nets:
            weight += 0.3 * len(shared_nets)
            
        # Context similarity
        if pid1 in self.analyzer.embeddings_cache and pid2 in self.analyzer.embeddings_cache:
            sim = torch.cosine_similarity(
                self.analyzer.embeddings_cache[pid1],
                self.analyzer.embeddings_cache[pid2]
            )
            weight += 0.2 * float(sim)
            
        return min(weight, 1.0)
    
    async def _update_clusters(self):
        """Update process clusters using spectral clustering"""
        if len(self.interaction_graph) < 2:
            return
            
        # Create adjacency matrix
        adj_matrix = nx.adjacency_matrix(self.interaction_graph).todense()
        adj_tensor = torch.tensor(adj_matrix, device=self.accelerator.device)
        
        # Spectral clustering
        laplacian = torch.diag(adj_tensor.sum(1)) - adj_tensor
        eigenvalues, eigenvectors = torch.linalg.eigh(laplacian)
        
        # Determine number of clusters (using eigengap heuristic)
        n_clusters = 1 + torch.argmax(torch.diff(eigenvalues[:10])).item()
        n_clusters = min(max(n_clusters, 2), len(self.interaction_graph) // 2)
        
        # K-means clustering on eigenvectors
        features = eigenvectors[:, :n_clusters]
        features = features / (torch.norm(features, dim=1, keepdim=True) + 1e-8)
        
        # Initialize centroids
        indices = torch.randperm(len(features))[:n_clusters]
        centroids = features[indices]
        
        # Simple k-means
        for _ in range(10):
            # Assign clusters
            distances = torch.cdist(features, centroids)
            cluster_assignments = torch.argmin(distances, dim=1)
            
            # Update centroids
            for k in range(n_clusters):
                mask = cluster_assignments == k
                if mask.any():
                    centroids[k] = features[mask].mean(0)
        
        # Create ProcessCluster objects
        self.clusters = []
        nodes = list(self.interaction_graph.nodes())
        
        for k in range(n_clusters):
            cluster_pids = [nodes[i] for i, c in enumerate(cluster_assignments) if c == k]
            if cluster_pids:
                # Find center process (highest degree centrality)
                subgraph = self.interaction_graph.subgraph(cluster_pids)
                center_pid = max(
                    cluster_pids,
                    key=lambda p: nx.degree_centrality(subgraph)[p]
                )
                
                # Calculate cluster metrics
                similarity_score = self._calculate_cluster_similarity(cluster_pids)
                resource_impact = self._calculate_resource_impact(cluster_pids)
                interaction_score = self._calculate_interaction_score(cluster_pids)
                
                self.clusters.append(ProcessCluster(
                    processes=cluster_pids,
                    center_pid=center_pid,
                    similarity_score=similarity_score,
                    resource_impact=resource_impact,
                    interaction_score=interaction_score
                ))
    
    def _calculate_cluster_similarity(self, pids: List[int]) -> float:
        """Calculate average similarity between processes in cluster"""
        if len(pids) < 2:
            return 0.0
            
        similarities = []
        for i, pid1 in enumerate(pids):
            for pid2 in pids[i+1:]:
                if pid1 in self.analyzer.embeddings_cache and pid2 in self.analyzer.embeddings_cache:
                    sim = torch.cosine_similarity(
                        self.analyzer.embeddings_cache[pid1],
                        self.analyzer.embeddings_cache[pid2]
                    )
                    similarities.append(float(sim))
        
        return float(np.mean(similarities)) if similarities else 0.0
    
    def _calculate_resource_impact(self, pids: List[int]) -> float:
        """Calculate total resource impact of cluster"""
        total_cpu = sum(self.interaction_graph.nodes[p]['cpu_percent'] for p in pids)
        total_mem = sum(self.interaction_graph.nodes[p]['memory_percent'] for p in pids)
        return float(0.5 * (total_cpu + total_mem) / 100.0)
    
    def _calculate_interaction_score(self, pids: List[int]) -> float:
        """Calculate interaction density within cluster"""
        if len(pids) < 2:
            return 0.0
            
        subgraph = self.interaction_graph.subgraph(pids)
        n = len(pids)
        max_edges = n * (n - 1)  # Directed graph
        return float(len(subgraph.edges) / max_edges if max_edges > 0 else 0.0)
    
    def get_cluster_insights(self, pid: int) -> Dict:
        """Get insights about the cluster containing a process"""
        for cluster in self.clusters:
            if pid in cluster.processes:
                return {
                    "cluster": cluster,
                    "processes": [
                        self.analyzer.get_process_insights(p)
                        for p in cluster.processes
                    ],
                    "relationships": [
                        {
                            "source": u,
                            "target": v,
                            "weight": self.interaction_graph.edges[u, v]["weight"]
                        }
                        for u, v in self.interaction_graph.edges()
                        if u in cluster.processes and v in cluster.processes
                    ]
                }
        return None
