"""Q0rtex: Quantum-inspired terminal with Metal acceleration"""

from q0rtex.plugins.quantum_rag_plugin import QuantumRAGPlugin
from q0rtex.metal.accelerator import MetalAccelerator
from q0rtex.quantum.state import QuantumState, QuantumMetrics

__version__ = "0.1.0"

__all__ = [
    "QuantumRAGPlugin",
    "MetalAccelerator", 
    "QuantumState",
    "QuantumMetrics"
]

