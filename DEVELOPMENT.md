# Development Setup Guide

## Prerequisites

1. **System Requirements**
   - macOS Sonoma or later
   - Apple Silicon M3 Pro
   - Xcode 15.0 or later
   - Python 3.10+
   - Conda or Miniconda

2. **Environment Setup**

```bash
# Create and activate conda environment
conda env create -f services/cortex/environment.yml
conda activate quantum-env

# Set Metal environment variables
export METAL_DEVICE_WRAPPER_TYPE=1
export PYTORCH_ENABLE_MPS_FALLBACK=1
export METAL_DEBUG_ERROR_MODE=1

# Install Metal development tools
xcode-select --install
```

3. **Build Metal Components**

```bash
cd services/cortex/QuantumTUI-Swift
swift build -c release
```

4. **Verify Installation**

```bash
# Run integration tests
pytest services/cortex/tests/test_integration.py -v

# Check Metal device
python -c "import torch; print(f'Metal device available: {torch.backends.mps.is_available()}')"
```

## Development Workflow

1. **Code Organization**
   ```
   quantum-index/
   ├── services/
   │   └── cortex/
   │       ├── QuantumTUI-Swift/  # Metal & Swift components
   │       ├── tests/             # Integration tests
   │       ├── config/            # Configuration files
   │       └── quantum_nexus/     # Python modules
   ```

2. **Running Components**

   a) Start Quantum Orchestrator:
   ```bash
   python -m quantum_nexus.orchestrator
   ```

   b) Launch Neural Loom:
   ```bash
   python -m quantum_nexus.neural_loom
   ```

   c) Start Quantum IDE:
   ```bash
   ./QuantumTUI-Swift/.build/release/quantum-ide
   ```

3. **Development Best Practices**

   - Run tests before committing:
     ```bash
     pytest
     mypy quantum_nexus
     black quantum_nexus
     ```
   
   - Monitor Metal performance:
     ```bash
     sudo powermetrics --samplers gpu_power
     ```

## Debugging

1. **Metal Shader Debugging**
   - Use Xcode's Metal debugger
   - Enable validation layers:
     ```bash
     export METAL_DEVICE_WRAPPER_TYPE=2
     ```

2. **Python Debugging**
   - Use `rich` for enhanced debug output
   - Enable Metal debug logs:
     ```bash
     export METAL_DEBUG_ERROR_MODE=2
     ```

## Performance Optimization

1. **Metal Profiling**
   - Use Metal System Trace
   - Monitor memory allocation
   - Track shader performance

2. **Neural Loom Optimization**
   - Profile model inference
   - Monitor batch processing
   - Optimize memory usage

## Contributing

1. **Code Style**
   - Python: Follow PEP 8
   - Swift: Follow Apple's style guide
   - Metal: Follow Metal best practices

2. **Testing**
   - Write unit tests for new features
   - Update integration tests
   - Verify Metal performance

3. **Documentation**
   - Update API documentation
   - Document Metal shaders
   - Keep configuration examples updated
