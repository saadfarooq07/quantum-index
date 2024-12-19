import pytest
from asyncio import Future
from unittest.mock import MagicMock, patch

from q0rtex.quantum.state import QuantumState
from q0rtex.metal.accelerator import MetalAccelerator

@pytest.fixture
def quantum_state():
    return QuantumState(dimension=2)

@pytest.fixture
def metal_accel():
    return MetalAccelerator(device="mps")

@pytest.mark.asyncio
async def test_quantum_initialization(quantum_state):
    """Test quantum state initialization with Metal acceleration."""
    assert quantum_state.dimension == 2
    assert quantum_state.is_valid()

@pytest.mark.asyncio
async def test_metal_acceleration(metal_accel):
    """Test Metal Performance Shaders (MPS) acceleration."""
    assert metal_accel.device == "mps"
    assert await metal_accel.verify_capabilities()

@pytest.mark.asyncio
async def test_terminal_integration():
    """Test quantum-enhanced terminal integration."""
    with patch('q0rtex.core.terminal.TerminalManager') as mock_term:
        mock_term.return_value.initialize = Future()
        mock_term.return_value.initialize.set_result(True)
        assert await mock_term.return_value.initialize

