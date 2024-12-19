import pytest
import asyncio
from unittest.mock import MagicMock

@pytest.fixture
def event_loop():
    """Create and use a new event loop for each test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_warp():
    """Mock Warp terminal interface."""
    mock = MagicMock()
    mock.initialize.return_value = True
    return mock

@pytest.fixture
def mock_metal():
    """Mock Metal acceleration interface."""
    mock = MagicMock()
    mock.device = "mps"
    mock.verify_capabilities.return_value = True
    return mock

@pytest.fixture
def mock_quantum_rag():
    """Mock QuantumRAG interface."""
    mock = MagicMock()
    mock.retrieve.return_value = {"relevance": 0.95, "content": "test"}
    return mock

