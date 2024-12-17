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
