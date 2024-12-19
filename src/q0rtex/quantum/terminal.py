from typing import Optional, Dict
from dataclasses import dataclass
from .state import QuantumState
from ..metal.accelerator import MetalAccelerator

@dataclass
class TerminalState:
    quantum: QuantumState
    accelerator: MetalAccelerator
    prompt_history: List[str]
    
class QuantumTerminal:
    def __init__(self):
        self.state = TerminalState(
            quantum=QuantumState(),
            accelerator=MetalAccelerator(),
            prompt_history=[]
        )
        
    async def process_command(self, command: str) -> Dict:
        """Process command with quantum enhancement"""
        # Apply quantum transformation
        enhanced_command = self.state.quantum.transform(command)
        
        # Generate embeddings using Metal
        embeddings = await self.state.accelerator.embed_text(enhanced_command)
        
        # Update history
        self.state.prompt_history.append(command)
        
        return {
            "command": enhanced_command,
            "embeddings": embeddings,
            "metrics": self.state.quantum.get_metrics()
        }
        
    def reset(self):
        """Reset terminal state"""
        self.state.quantum.collapse()
        self.state.prompt_history.clear()

