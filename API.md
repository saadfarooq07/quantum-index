# Quandex Neural Engine API Reference

## JAN API Server

The JSON Agentic Neural (JAN) server provides a RESTful API for model deployment and inference.

### Base URL
```
http://localhost:8000/v1
```

### Authentication
```http
Authorization: Bearer <your_api_key>
```

### Endpoints

#### 1. Model Inference
```http
POST /generate
Content-Type: application/json

{
    "model": "llama-3.2",
    "prompt": "Implement a sorting algorithm",
    "temperature": 0.7,
    "max_tokens": 1000,
    "metal_optimize": true
}
```

Response:
```json
{
    "id": "gen_123abc",
    "model": "llama-3.2",
    "choices": [{
        "text": "Here's an implementation...",
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 4,
        "completion_tokens": 150,
        "total_tokens": 154
    },
    "metal_stats": {
        "mps_allocated": "1.2GB",
        "batch_size": 32,
        "processing_time": "1.2s"
    }
}
```

#### 2. Model Management
```http
GET /models
Authorization: Bearer <your_api_key>
```

Response:
```json
{
    "models": [
        {
            "id": "llama-3.2",
            "status": "ready",
            "metal_optimized": true,
            "memory_usage": "12GB"
        },
        {
            "id": "mistral-7b",
            "status": "loading",
            "metal_optimized": true
        }
    ]
}
```

#### 3. Resource Monitoring
```http
GET /stats
Authorization: Bearer <your_api_key>
```

Response:
```json
{
    "metal_device": {
        "name": "Apple M3 Pro",
        "memory_allocated": "24GB",
        "memory_available": "12GB",
        "temperature": "45C"
    },
    "models": {
        "llama-3.2": {
            "requests_per_second": 10,
            "average_latency": "100ms",
            "error_rate": "0.01%"
        }
    }
}
```

## Quandex Neural Engine API

## Overview

The Quandex Neural Engine provides a quantum-inspired API for neural processing on Apple Silicon M3. This document outlines the core APIs and their usage.

## Core APIs

### 1. Metal Acceleration

#### MetalAccelerator
```python
from quandex.metal import MetalAccelerator, MetalConfig

# Initialize accelerator
config = MetalConfig(
    batch_size=32,
    quantization_bits=8
)
accelerator = MetalAccelerator(config)

# Prepare model for Metal execution
model = accelerator.prepare_model(your_model)
```

#### Configuration Options
```python
class MetalConfig:
    device: str = "mps"  # Metal Performance Shaders
    batch_size: int = 32
    max_sequence_length: int = 2048
    quantization_bits: int = 8
    attention_heads: int = 8
```

### 2. Quantum Processing

#### QuantumRAG
```python
from quandex.quantum import QuantumRAG

# Initialize quantum RAG
rag = QuantumRAG(
    embedding_model="BAAI/bge-small-en-v1.5",
    metal_config=metal_config
)

# Process documents
docs = rag.load_documents("path/to/docs")
rag.index_documents(docs)

# Query
answer = rag.answer_question("What is quantum computing?")
```

#### State Management
```python
from quandex.quantum import QuantumState

# Create quantum states
state = QuantumState(
    amplitude=0.707,
    phase=0.0
)

# Apply transformations
transformed = quantum_processor.apply_gate(state, "hadamard")
```

### 3. Reality Metrics

#### RealityCheck
```python
from quandex.reality import RealityMetrics

# Initialize metrics
metrics = RealityMetrics()

# Check token reality
score = metrics.check_token(
    token="example",
    context="This is an example context"
)

# Get detailed metrics
details = metrics.get_detailed_metrics()
```

### 4. Memory Management

#### QuantumMemoryPool
```python
from quandex.memory import QuantumMemoryPool

# Initialize memory pool
pool = QuantumMemoryPool(
    max_states=1000,
    cleanup_threshold=0.75
)

# Allocate states
state_id = pool.allocate_state(quantum_state)

# Release states
pool.release_state(state_id)
```

## Integration Examples

### 1. Complete Pipeline
```python
from quandex import QuantumPipeline

# Initialize pipeline
pipeline = QuantumPipeline(
    metal_config=metal_config,
    model_config=model_config
)

# Process input
result = pipeline.process(
    input_text="Your input here",
    reality_check=True
)
```

### 2. Custom Model Integration
```python
from quandex import ModelAdapter

# Create model adapter
adapter = ModelAdapter(
    model_path="path/to/model",
    metal_optimize=True
)

# Use adapter
output = adapter.generate(
    prompt="Your prompt",
    max_tokens=100
)
```

## Best Practices

### 1. Memory Optimization
- Use appropriate batch sizes (32 recommended)
- Enable 8-bit quantization when possible
- Monitor memory pressure
- Clean up unused states

### 2. Performance Tuning
- Use Metal acceleration
- Enable dynamic batching
- Optimize thread groups
- Monitor reality metrics

### 3. Reality Anchoring
- Always validate outputs
- Monitor coherence scores
- Set appropriate thresholds
- Handle edge cases

## Error Handling

### Common Errors
```python
from quandex.exceptions import (
    MetalError,
    QuantumStateError,
    RealityCheckError
)

try:
    result = pipeline.process(input_text)
except MetalError as e:
    print(f"Metal acceleration error: {e}")
except QuantumStateError as e:
    print(f"Quantum state error: {e}")
except RealityCheckError as e:
    print(f"Reality check failed: {e}")
```

## Advanced Features

### 1. Custom Quantum Gates
```python
from quandex.quantum import QuantumGate

# Define custom gate
class CustomGate(QuantumGate):
    def apply(self, state):
        # Implementation
        pass

# Register gate
quantum_processor.register_gate("custom", CustomGate())
```

### 2. Reality Metric Extensions
```python
from quandex.reality import BaseMetric

# Define custom metric
class CustomMetric(BaseMetric):
    def calculate(self, token, context):
        # Implementation
        pass

# Register metric
metrics.register_metric("custom", CustomMetric())
```

## Performance Monitoring

### 1. Metrics Collection
```python
from quandex.monitoring import MetricsCollector

# Initialize collector
collector = MetricsCollector()

# Record metrics
collector.record_latency(50)  # ms
collector.record_memory_usage(1024)  # MB
collector.record_reality_score(0.95)
```

### 2. Performance Analysis
```python
from quandex.monitoring import PerformanceAnalyzer

# Analyze performance
analyzer = PerformanceAnalyzer(collector)
report = analyzer.generate_report()
```

## Python SDK

### Installation
```bash
pip install quandex-client
```

### Usage

```python
from quandex import QuandexClient

# Initialize client
client = QuandexClient(api_key="your_api_key")

# Generate text
response = await client.generate(
    model="llama-3.2",
    prompt="Explain quantum computing",
    temperature=0.7,
    metal_optimize=True
)

# Stream responses
async for chunk in client.stream_generate(
    model="llama-3.2",
    prompt="Write a story",
    metal_optimize=True
):
    print(chunk.text, end="")

# Get model stats
stats = await client.get_model_stats("llama-3.2")
print(f"Memory usage: {stats['memory_usage']}")
```

## Error Codes

| Code | Description |
|------|-------------|
| 400  | Bad Request - Invalid parameters |
| 401  | Unauthorized - Invalid API key |
| 404  | Model not found |
| 429  | Rate limit exceeded |
| 500  | Internal server error |
| 503  | Model is loading or unavailable |

## Rate Limits

- 10 requests per second per API key
- 1000 requests per day per API key
- Burst limit: 20 requests per second

## Best Practices

1. **Metal Optimization**
   - Enable `metal_optimize=true` for M3-optimized inference
   - Monitor memory usage through `/stats` endpoint
   - Adjust batch size based on your needs

2. **Error Handling**
   - Implement exponential backoff for rate limits
   - Handle streaming timeouts gracefully
   - Monitor model loading status

3. **Resource Management**
   - Pre-load frequently used models
   - Monitor memory usage
   - Use streaming for long responses
