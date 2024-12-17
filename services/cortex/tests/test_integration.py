import pytest
import numpy as np
from hypothesis import given, strategies as st
from pathlib import Path

from quantum_nexus.qortex import QFabric
from quantum_nexus.orchestrator import QuantumOrchestrator
from quantum_nexus.neural_loom import NeuralLoom
from quantum_nexus.metal import MetalDevice

class TestQuantumNexusIntegration:
    @pytest.fixture(scope="module")
    def metal_device(self):
        return MetalDevice()
    
    @pytest.fixture(scope="module")
    def quantum_system(self, metal_device):
        return {
            'qfabric': QFabric(metal_device),
            'orchestrator': QuantumOrchestrator(metal_device),
            'neural_loom': NeuralLoom(metal_device)
        }
    
    def test_metal_initialization(self, metal_device):
        """Test Metal device initialization and shader compilation"""
        assert metal_device.is_available()
        assert metal_device.compile_shader("NeuralLoom.metal")
        assert metal_device.compile_shader("SuperpositionShader.metal")
    
    @given(batch_size=st.integers(min_value=1, max_value=32))
    def test_neural_loom_forward(self, quantum_system, batch_size):
        """Test Neural Loom forward pass with different batch sizes"""
        input_data = np.random.randn(batch_size, 4).astype(np.float16)
        neural_loom = quantum_system['neural_loom']
        
        output = neural_loom.forward(input_data)
        assert output.shape == input_data.shape
        assert not np.isnan(output).any()
    
    def test_quantum_orchestration(self, quantum_system):
        """Test quantum state orchestration and measurement"""
        orchestrator = quantum_system['orchestrator']
        
        # Create quantum states
        states = orchestrator.create_parallel_states(num_states=4)
        assert len(states) == 4
        
        # Apply quantum operations
        modified_states = orchestrator.apply_operations(states)
        assert len(modified_states) == len(states)
        
        # Measure states
        measurements = orchestrator.measure_states(modified_states)
        assert all(0 <= m <= 1 for m in measurements)
    
    def test_qfabric_memory_pool(self, quantum_system):
        """Test Q-Fabric memory pool allocation and management"""
        qfabric = quantum_system['qfabric']
        
        # Allocate memory
        pool = qfabric.create_memory_pool(size_mb=128)
        assert pool.available_memory > 0
        
        # Test memory operations
        data = np.random.randn(1000, 4).astype(np.float16)
        buffer = pool.allocate_buffer(data.nbytes)
        assert buffer is not None
        
        # Write and read data
        pool.write_to_buffer(buffer, data)
        read_data = pool.read_from_buffer(buffer)
        np.testing.assert_array_almost_equal(data, read_data)
    
    def test_system_integration(self, quantum_system):
        """Test full system integration with all components"""
        qfabric = quantum_system['qfabric']
        orchestrator = quantum_system['orchestrator']
        neural_loom = quantum_system['neural_loom']
        
        # Create quantum state
        input_state = np.random.randn(16, 4).astype(np.float16)
        
        # Process through Q-Fabric
        quantum_state = qfabric.process_state(input_state)
        
        # Orchestrate quantum operations
        orchestrated_state = orchestrator.process_quantum_state(quantum_state)
        
        # Process through Neural Loom
        final_output = neural_loom.process(orchestrated_state)
        
        assert final_output.shape == input_state.shape
        assert not np.isnan(final_output).any()
