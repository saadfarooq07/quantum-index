import torch
import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class MetalConfig:
    device: str = "mps" if torch.backends.mps.is_available() else "cpu"
    batch_size: int = 32
    max_sequence_length: int = 2048
    quantization_bits: int = 8
    attention_heads: int = 8

class MetalAccelerator:
    def __init__(self, config: Optional[MetalConfig] = None):
        self.config = config or MetalConfig()
        self.device = torch.device(self.config.device)
        
    def prepare_model(self, model: torch.nn.Module) -> torch.nn.Module:
        """Optimize model for Metal execution"""
        model = model.to(self.device)
        if self.config.quantization_bits == 8:
            model = torch.quantization.quantize_dynamic(
                model, {torch.nn.Linear}, dtype=torch.qint8
            )
        return model
    
    def prepare_embeddings(self, embeddings: np.ndarray) -> torch.Tensor:
        """Convert embeddings to Metal-optimized format"""
        return torch.from_numpy(embeddings).to(self.device)
    
    def batch_process(self, inputs: List[torch.Tensor]) -> List[torch.Tensor]:
        """Process inputs in optimized batches"""
        batches = [inputs[i:i + self.config.batch_size] 
                  for i in range(0, len(inputs), self.config.batch_size)]
        
        results = []
        for batch in batches:
            batch_tensor = torch.stack(batch).to(self.device)
            with torch.no_grad():
                result = self._process_batch(batch_tensor)
            results.extend(result)
        
        return results
    
    def _process_batch(self, batch: torch.Tensor) -> List[torch.Tensor]:
        """Internal batch processing with Metal optimization"""
        # Apply attention mechanism
        batch_size, seq_length, hidden_size = batch.shape
        attention_mask = torch.ones(batch_size, seq_length).to(self.device)
        
        # Split into attention heads
        batch = batch.view(batch_size, seq_length, 
                         self.config.attention_heads, -1)
        
        # Compute attention scores
        scores = torch.matmul(batch, batch.transpose(-2, -1)) / np.sqrt(hidden_size)
        scores = scores.masked_fill(attention_mask.unsqueeze(1).unsqueeze(2) == 0, float('-inf'))
        attention_weights = torch.softmax(scores, dim=-1)
        
        # Apply attention
        attended = torch.matmul(attention_weights, batch)
        return [tensor for tensor in attended]

    @staticmethod
    def is_metal_available() -> bool:
        """Check if Metal acceleration is available"""
        return torch.backends.mps.is_available()
    
    def get_device_info(self) -> Dict[str, str]:
        """Get information about the Metal device"""
        return {
            "device": str(self.device),
            "metal_available": str(self.is_metal_available()),
            "batch_size": str(self.config.batch_size),
            "quantization": f"{self.config.quantization_bits}-bit"
        }
