import os
import sys
sys.path.append('/opt/homebrew/lib/python3.13/site-packages')  # Add Homebrew Python path

import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import json
from dataclasses import dataclass
from collections import Counter
import torch
from transformers import AutoTokenizer, AutoModel
import faiss

@dataclass
class CodeQuantization:
    original_path: str
    token_vectors: np.ndarray
    char_mapping: Dict[int, Tuple[int, int]]  # token_idx -> (start_char, end_char)
    metadata: Dict

class QuantumCodeIndexer:
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.dimension = 768  # CodeBERT embedding dimension
        self.quantizer = faiss.IndexIVFPQ(
            faiss.IndexFlatL2(self.dimension),  # coarse quantizer
            self.dimension,  # dimension
            1024,  # number of centroids
            8,  # number of sub-vectors
            8   # bits per code (usually 8)
        )
        
    def tokenize_and_embed(self, code: str) -> Tuple[np.ndarray, Dict[int, Tuple[int, int]]]:
        """Tokenize code and create character-level mapping"""
        tokens = self.tokenizer(code, return_tensors="pt", truncation=True, max_length=512)
        char_mapping = {}
        
        # Get character-level mapping
        offset = 0
        for i, token_id in enumerate(tokens.input_ids[0]):
            token = self.tokenizer.decode([token_id])
            char_mapping[i] = (offset, offset + len(token))
            offset += len(token)
            
        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**tokens)
            embeddings = outputs.last_hidden_state[0].numpy()
            
        return embeddings, char_mapping

    def quantize_code(self, file_path: str) -> CodeQuantization:
        """Quantize a single code file"""
        with open(file_path, 'r') as f:
            code = f.read()
            
        embeddings, char_mapping = self.tokenize_and_embed(code)
        
        metadata = {
            'file_path': file_path,
            'file_size': len(code),
            'extension': Path(file_path).suffix,
            'token_count': len(embeddings)
        }
        
        return CodeQuantization(
            original_path=file_path,
            token_vectors=embeddings,
            char_mapping=char_mapping,
            metadata=metadata
        )

    def build_quantum_index(self, code_files: List[str]) -> Tuple[faiss.Index, List[CodeQuantization]]:
        """Build a quantum-enhanced search index from code files"""
        all_vectors = []
        quantizations = []
        
        for file_path in code_files:
            try:
                quant = self.quantize_code(file_path)
                all_vectors.append(quant.token_vectors)
                quantizations.append(quant)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                
        # Concatenate all vectors
        vectors = np.vstack(all_vectors)
        
        # Train the quantizer
        self.quantizer.train(vectors)
        
        # Add vectors to the index
        self.quantizer.add(vectors)
        
        return self.quantizer, quantizations

    def search_code(self, query: str, k: int = 5) -> List[Tuple[str, float, Dict]]:
        """Search the quantized code index"""
        query_embedding, _ = self.tokenize_and_embed(query)
        
        # Get mean of query embeddings
        query_vector = np.mean(query_embedding, axis=0).reshape(1, -1)
        
        # Search the index
        D, I = self.quantizer.search(query_vector, k)
        
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < len(self.quantizations):
                quant = self.quantizations[idx]
                results.append((
                    quant.original_path,
                    float(dist),
                    quant.metadata
                ))
                
        return results

def process_directory(root_dir: str) -> None:
    """Process an entire directory and create a quantum index"""
    indexer = QuantumCodeIndexer()
    
    # Collect all code files
    code_files = []
    for ext in ['.py', '.ts', '.js', '.json', '.md']:
        code_files.extend(Path(root_dir).rglob(f'*{ext}'))
    
    # Build the index
    index, quantizations = indexer.build_quantum_index([str(f) for f in code_files])
    
    # Save the index and metadata
    output_dir = Path(root_dir) / 'quantum-index'
    output_dir.mkdir(exist_ok=True)
    
    # Save the FAISS index
    faiss.write_index(index, str(output_dir / 'code.index'))
    
    # Save metadata
    metadata = {
        'files': [q.metadata for q in quantizations],
        'total_files': len(quantizations),
        'index_dimension': indexer.dimension
    }
    
    with open(output_dir / 'metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Quantum index created at {output_dir}")
    print(f"Processed {len(quantizations)} files")
    print(f"Index dimension: {indexer.dimension}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python quantize.py <directory>")
        sys.exit(1)
    
    process_directory(sys.argv[1])
