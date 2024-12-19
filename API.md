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

## Metal-Accelerated API Server Documentation

## Overview
High-performance API server leveraging Apple Metal for hardware-accelerated computation. The server provides text processing, quantum circuit simulation, and cryptographic operations with SIMD optimization.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API does not require authentication. For production use, implement appropriate authentication mechanisms.

## Endpoints

### 1. Text Completions
Generate text completions using Metal-accelerated processing.

**Endpoint:** `/v1/completions`  
**Method:** POST  
**Content-Type:** application/json

#### Request Body
```json
{
    "model": "metal-m3",
    "prompt": "Your input text here",
    "max_tokens": 100,
    "temperature": 0.7,
    "stream": false
}
```

#### Parameters
- `model` (string, required): Model identifier (currently supports "metal-m3")
- `prompt` (string, required): Input text for completion
- `max_tokens` (integer, optional): Maximum number of tokens to generate (default: 100, max: 512)
- `temperature` (float, optional): Sampling temperature (default: 0.7, range: 0.0-2.0)
- `stream` (boolean, optional): Enable streaming responses (default: false)

#### Response
```json
{
    "id": "metal-m3-1640995200",
    "object": "text_completion",
    "created": 1640995200,
    "model": "metal-m3",
    "choices": [
        {
            "text": "Generated completion text",
            "index": 0,
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    }
}
```

### 2. Health Check
Check the server and Metal device status.

**Endpoint:** `/health`  
**Method:** GET

#### Response
```json
{
    "status": "healthy",
    "metal_device": "Apple M3 Pro",
    "timestamp": 1640995200
}
```

### 3. Metrics
Get server performance metrics and device information.

**Endpoint:** `/metrics`  
**Method:** GET

#### Response
```json
{
    "metrics": {
        "total_requests": 100,
        "successful_requests": 95,
        "failed_requests": 5,
        "average_latency": 0.15,
        "metal_utilization": 0.75
    },
    "device": {
        "name": "Apple M3 Pro",
        "is_low_power": false,
        "max_buffer_length": 1073741824
    },
    "timestamp": "2024-12-18T19:57:45-08:00"
}
```

## Error Handling

### Error Response Format
```json
{
    "detail": "Error message describing what went wrong"
}
```

### Common Error Codes
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Requested resource not found
- `500 Internal Server Error`: Server-side processing error

## Metal Compute Features

### 1. SIMD-Optimized Operations
- Matrix multiplication using SIMD groups
- Multi-head attention with SIMD optimization
- Token embedding with positional encoding

### 2. Quantum Circuit Simulation
- Support for quantum gate operations
- Complex number arithmetic
- State vector manipulation

### 3. Cryptographic Operations
- Hardware-accelerated hashing
- Secure mixing functions
- Parallel processing of large data sets

### 4. Neural Network Functions
- Multiple activation functions (ReLU, GELU, Sigmoid, Tanh)
- Layer normalization
- Feed-forward network processing

## Performance Monitoring

### Metrics Tracked
- Request success/failure rates
- Average request latency
- Metal device utilization
- Memory usage
- Throughput

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking
- Performance metrics

## Best Practices

1. **Request Size**
   - Keep prompts under 512 tokens for optimal performance
   - Use streaming for long-running operations

2. **Rate Limiting**
   - Implement appropriate rate limiting for production use
   - Monitor Metal device utilization

3. **Error Handling**
   - Always check response status codes
   - Implement proper retry logic with exponential backoff

4. **Performance**
   - Use batch processing when possible
   - Monitor metrics endpoint for system health
   - Implement proper caching strategies
