import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from metal_config import MetalAccelerationConfig
from quantum_hooks import WarpQuantumHooks
from cortex_client import CortexClient

@dataclass 
class TerminalState:
    """Manages the current state of the quantum terminal"""
    quantum_ready: bool = False
    metal_initialized: bool = False
    current_context: Dict[str, Any] = None
    reality_metrics: Dict[str, float] = None
    
class WarpQ0rtexConnector:
    """Connects Warp terminal to the Q0rtex quantum processing system"""
    
    def __init__(self, metal_config: Optional[Dict] = None):
        self.hooks = WarpQuantumHooks()
        self.cortex = CortexClient()
        self.state = TerminalState()
        self.metal_config = MetalAccelerationConfig(
            batch_size=32,
            max_sequence_length=2048,
            quantization_bits=8,
            attention_heads=8,
            **metal_config or {}
        )
        
    async def initialize(self) -> None:
        """Initialize the quantum terminal environment"""
        try:
            # Configure Metal acceleration
            await self.metal_config.initialize_metal()
            self.state.metal_initialized = True
            
            # Set up quantum hooks
            await self.hooks.setup_terminal_hooks()
            self.state.quantum_ready = True
            
            # Initialize cortex connection
            await self.cortex.connect()
            
        except Exception as e:
            self.state.quantum_ready = False
            raise RuntimeError(f"Failed to initialize quantum terminal: {e}")
            
    async def process_command(self, cmd: str) -> str:
        """Process a terminal command through quantum pipeline"""
        if not self.state.quantum_ready:
            await self.initialize()
            
        # Update terminal context
        self.state.current_context = await self.hooks.get_terminal_context()
        
        # Generate quantum-inspired response
        response = await self.cortex.generate_completion(
            prompt=cmd,
            context=self.state.current_context,
            metal_config=self.metal_config
        )
        
        # Update reality metrics
        self.state.reality_metrics = await self.hooks.measure_quantum_state()
        
        return response
        
    async def update_terminal_state(self) -> None:
        """Update the terminal UI state based on quantum metrics"""
        if self.state.reality_metrics:
            await self.hooks.update_terminal_ui(
                quantum_state=self.state.reality_metrics,
                context=self.state.current_context
            )
            
    def get_suggestions(self, partial_cmd: str) -> List[str]:
        """Get quantum-inspired command suggestions"""
        return self.hooks.get_command_suggestions(
            partial_cmd,
            self.state.current_context
        )
        
    async def cleanup(self) -> None:
        """Cleanup quantum resources"""
        await self.hooks.cleanup()
        await self.cortex.disconnect()
        self.state.quantum_ready = False
        self.state.metal_initialized = False

