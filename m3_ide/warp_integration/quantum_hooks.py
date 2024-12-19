import os
from typing import Any, Callable, Dict, Optional
from .quantum_state import QuantumState, QuantumVisualization
from .warp_commands import CommandProcessor

class WarpQuantumHooks:
    def __init__(self):
        self.state = QuantumState()
        self.viz = QuantumVisualization()
        self.cmd_processor = CommandProcessor()
        self.hooks: Dict[str, Callable] = {}

    def register_hook(self, event: str, callback: Callable) -> None:
        """Register a hook for terminal events."""
        self.hooks[event] = callback

    def command_pre_execute(self, command: str) -> str:
        """Pre-process command with quantum suggestions."""
        return self.cmd_processor.enhance_command(command, self.state)

    def command_post_execute(self, command: str, result: Any) -> None:
        """Update quantum state after command execution."""
        self.state.update_from_result(result)
        self.viz.update_display(self.state)

    def handle_terminal_event(self, event: str, data: Dict[str, Any]) -> None:
        """Handle terminal events with quantum context."""
        if event in self.hooks:
            self.hooks[event](data, self.state)

    @property
    def quantum_environment(self) -> Dict[str, str]:
        """Get quantum-aware environment variables."""
        return {
            "QUANTUM_STATE": self.state.serialize(),
            "WARP_QUANTUM_ENABLED": "1",
            "METAL_DEVICE_ENABLED": "1"
        }

