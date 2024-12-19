import re
import asyncio
import time
from dataclasses import dataclass
from typing import List, Optional

from ..metal.accelerator import MetalTimer
from ..quantum.state import QuantumState

@dataclass
class BreathingPattern:
    action: str  # "in" or "out"
    duration: float = 4.0  # seconds

class QuantumMeditationHandler:
    QGROUND_PATTERN = r"<qGround:(\w+):(\w+):((?:[^:]+:)*[^:]+)::(\w+)::>"

    def __init__(self):
        self.metal_timer = MetalTimer()
        self.quantum_state = QuantumState()
        self.is_active = False

    async def process_command(self, command: str) -> Optional[str]:
        """Process a qGround meditation command."""
        match = re.match(self.QGROUND_PATTERN, command)
        if not match:
            return None
            
        action, type_, pattern, end_action = match.groups()
        
        if action == "start" and end_action == "stop":
            return await self._handle_meditation_sequence(type_, pattern)
        
        return None
        
    async def _handle_meditation_sequence(self, type_: str, pattern: str) -> str:
        """Handle a meditation sequence."""
        if type_ != "breathe":
            return "Only breathing meditation supported"
            
        self.is_active = True
        patterns = self._parse_breathing_pattern(pattern)
        
        try:
            async with self.metal_timer.acceleration():
                for p in patterns:
                    if not self.is_active:
                        break
                    await self._execute_breath(p)
                    await self.quantum_state.sync()
        finally:
            self.is_active = False
            
        return "Meditation complete"
        
    def _parse_breathing_pattern(self, pattern: str) -> List[BreathingPattern]:
        """Parse breathing pattern from command string."""
        actions = pattern.split(':')
        return [BreathingPattern(action=a) for a in actions]
        
    async def _execute_breath(self, pattern: BreathingPattern):
        """Execute a single breath pattern with Metal-accelerated timing."""
        start = self.metal_timer.get_time()
        
        message = f"Breath {pattern.action}..."
        print(message, end='', flush=True)
        
        while (self.metal_timer.get_time() - start) < pattern.duration:
            if not self.is_active:
                break
            await asyncio.sleep(0.1)
            
        print("\r" + " " * len(message) + "\r", end='', flush=True)
        
    def stop(self):
        """Stop the current meditation sequence."""
        self.is_active = False

