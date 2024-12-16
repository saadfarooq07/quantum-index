import os
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class M3Config:
    """Configuration for M3-optimized components"""
    mps_enabled: bool = True
    num_threads: int = 8
    memory_limit: int = 32 * 1024  # 32GB in MB
    cache_size: int = 4 * 1024  # 4GB in MB
    quantization: str = "int8"
    
@dataclass
class ModelConfig:
    """Configuration for AI models"""
    nemotron_api_key: str
    hf_api_key: str
    model_cache_dir: str
    max_batch_size: int = 32
    streaming: bool = True
    
@dataclass
class RAGConfig:
    """Configuration for RAG system"""
    chunk_size: int = 512
    chunk_overlap: int = 64
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    similarity_metric: str = "cosine"
    
@dataclass
class QuantumConfig:
    """Configuration for quantum-inspired features"""
    state_dim: int = 1024
    superposition_depth: int = 8
    entanglement_preserve: bool = True

class IDEConfig:
    """Global IDE configuration"""
    def __init__(self):
        self.m3 = M3Config()
        self.model = ModelConfig(
            nemotron_api_key=os.getenv("NVIDIA_NGC_KEY", ""),
            hf_api_key=os.getenv("HF_API_KEY", ""),
            model_cache_dir=os.path.expanduser("~/.cache/m3_ide/models")
        )
        self.rag = RAGConfig()
        self.quantum = QuantumConfig()
        
    @property
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return bool(self.model.nemotron_api_key and self.model.hf_api_key)
        
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            "m3": self.m3.__dict__,
            "model": self.model.__dict__,
            "rag": self.rag.__dict__,
            "quantum": self.quantum.__dict__
        }
        
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'IDEConfig':
        """Create configuration from dictionary"""
        config = cls()
        config.m3 = M3Config(**config_dict.get("m3", {}))
        config.model = ModelConfig(**config_dict.get("model", {}))
        config.rag = RAGConfig(**config_dict.get("rag", {}))
        config.quantum = QuantumConfig(**config_dict.get("quantum", {}))
        return config
