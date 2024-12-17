Copyright 2024 Saad Farooq (saad.farooq07@gmail.com)
All rights reserved.

# Quandex Neural Engine

A high-performance neural processing engine optimized for Apple Silicon M3, featuring the JAN API server for advanced model deployment and inference.

## Core Features

### 1. Neural Engine Integration
- **Metal Performance Shaders**: Direct integration with M3's Neural Engine
- **Model Optimization**: GGUF format optimization for LLaMA 3.2
- **Dynamic Memory Management**: Optimized for unified memory architecture

### 2. JAN API Server
- **Model Deployment**: Efficient model serving through JSON Agentic Neural server
- **Metal Acceleration**: M3-optimized inference pipeline
- **Resource Management**: Dynamic resource allocation based on model requirements

### 3. Performance Features
- **LLaMA 3.2 Support**: Metal-accelerated inference for latest models
- **Memory Optimization**: Efficient unified memory management
- **Batch Processing**: Dynamic batch size adjustment for optimal throughput

## System Requirements

- macOS Sonoma or later
- Apple Silicon M3 Pro (or newer)
- 36GB Unified Memory (recommended)
- Xcode 15.0+ (for Metal development)

## Model Integration

```python
# Initialize Quandex Engine
from quandex import QuandexEngine, ModelConfig

engine = QuandexEngine(
    model="llama-3.2",
    metal_optimize=True
)

# Process through JAN API
result = await engine.process(
    input_text,
    temperature=0.7
)
```

## Metal Performance

Leverages Metal Performance Shaders for neural processing:
```python
# Metal-optimized inference
processor = MetalModelProcessor()
result = processor.run_inference(
    model="llama-3.2",
    input_tokens=tokens
)

# Monitor resource usage
stats = engine.get_metal_stats()
print(f"MPS Memory Usage: {stats['mps_allocated']} bytes")
```

## Development

1. Clone the repository:
```bash
git clone https://github.com/saadfarooq07/quantum-index.git
cd quantum-index
```

2. Create environment:
```bash
conda env create -f services/cortex/environment.yml
conda activate quandex-env
```

3. Configure Metal:
```bash
export METAL_DEVICE_WRAPPER_TYPE=1
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

## Model Support

Currently supported models:
- LLaMA 3.2 (Metal-optimized)
- Mistral AI (coming soon)
- Claude 3 (planned)
- Custom GGUF models

## License

Copyright 2024 Saad Farooq (saad.farooq07@gmail.com)
All rights reserved.

## Acknowledgments
- Built on top of the Windsurf IDE platform
- Utilizes Codeium's base language server capabilities
