import httpx
import json
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
from ..core.config import ModelConfig

class NemotronModel:
    """Integration with Nemotron-4 340B model"""
    def __init__(self, config: ModelConfig):
        self.config = config
        self.api_base = "https://api.nvidia.com/v1/nemotron"
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {config.nemotron_api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
    async def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stop_sequences: Optional[list] = None
    ) -> AsyncGenerator[str, None]:
        """Stream responses from the model"""
        payload = {
            "model": "nemotron-4-340b-instruct",
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stop": stop_sequences or [],
            "stream": True
        }
        
        async with self.client.stream(
            "POST",
            f"{self.api_base}/completions",
            json=payload
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if "choices" in data and data["choices"]:
                        yield data["choices"][0]["text"]
                        
    async def generate(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """Generate a complete response"""
        response_chunks = []
        async for chunk in self.generate_stream(prompt, **kwargs):
            response_chunks.append(chunk)
        return "".join(response_chunks)
        
    async def analyze_code(
        self,
        code: str,
        task: str = "analyze"
    ) -> Dict[str, Any]:
        """Analyze code using the model"""
        prompt = f"""Analyze the following code and provide insights about its:
1. Structure and organization
2. Potential improvements
3. Performance considerations
4. Security implications

Code:
```
{code}
```

Task: {task}"""

        response = await self.generate(prompt, max_tokens=500)
        
        # Parse response into structured format
        sections = response.split("\n\n")
        analysis = {}
        
        current_section = None
        for section in sections:
            if section.strip().endswith(":"):
                current_section = section.strip()[:-1].lower()
                analysis[current_section] = []
            elif current_section:
                analysis[current_section].append(section.strip())
                
        return analysis
        
    async def generate_synthetic_data(
        self,
        schema: Dict[str, Any],
        num_samples: int = 10
    ) -> list:
        """Generate synthetic data based on schema"""
        prompt = f"""Generate {num_samples} synthetic data samples following this schema:
{json.dumps(schema, indent=2)}

Format each sample as valid JSON."""

        response = await self.generate(prompt, max_tokens=1000)
        
        try:
            # Extract JSON objects from response
            samples = []
            current_sample = ""
            bracket_count = 0
            
            for char in response:
                if char == "{":
                    bracket_count += 1
                elif char == "}":
                    bracket_count -= 1
                    
                current_sample += char
                
                if bracket_count == 0 and current_sample.strip():
                    try:
                        sample = json.loads(current_sample)
                        samples.append(sample)
                        current_sample = ""
                    except json.JSONDecodeError:
                        pass
                        
            return samples[:num_samples]
        except Exception as e:
            print(f"Error parsing synthetic data: {e}")
            return []
            
    async def close(self):
        """Close the client connection"""
        await self.client.aclose()
        
    async def __aenter__(self):
        """Context manager entry"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
