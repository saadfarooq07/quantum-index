import numpy as np
from typing import List, Dict, Optional
import os
import glob
from dataclasses import dataclass, field

@dataclass
class CodeFragment:
    content: str
    path: str
    start_line: int
    end_line: int
    perplexity: float
    relevance: float = field(default=None)

class QuantumPerplexitySearch:
    def __init__(self):
        self.code_cache: Dict[str, List[CodeFragment]] = {}
        
    def calculate_perplexity(self, code: str) -> float:
        """Calculate perplexity score for a code fragment"""
        tokens = code.split()
        if not tokens:
            return float('inf')
            
        # Simple perplexity calculation based on token frequencies
        frequencies = {}
        for token in tokens:
            frequencies[token] = frequencies.get(token, 0) + 1
            
        probabilities = [frequencies[token] / len(tokens) for token in tokens]
        log_probs = np.log(probabilities)
        perplexity = np.exp(-np.mean(log_probs))
        
        return perplexity
        
    def calculate_relevance(self, content: str, query: str) -> float:
        """Calculate relevance score between content and query"""
        # Convert to lowercase for case-insensitive matching
        content_lower = content.lower()
        query_lower = query.lower()
        
        # Split into words
        content_words = set(content_lower.split())
        query_words = set(query_lower.split())
        
        # Calculate word overlap
        common_words = content_words.intersection(query_words)
        
        # Calculate quantum-specific relevance
        quantum_terms = {'quantum', 'qubit', 'superposition', 'entanglement', 'state', 'vector', 'amplitude'}
        quantum_relevance = len(content_words.intersection(quantum_terms)) / len(quantum_terms)
        
        # Combine word overlap and quantum relevance
        overlap_score = len(common_words) / (len(query_words) + 0.1)  # Add small constant to avoid division by zero
        return (overlap_score + quantum_relevance) / 2

    def index_code(self, content: str, path: str, start_line: int, end_line: int) -> CodeFragment:
        """Index a code fragment"""
        perplexity = self.calculate_perplexity(content)
        
        fragment = CodeFragment(
            content=content,
            path=path,
            start_line=start_line,
            end_line=end_line,
            perplexity=perplexity
        )
        
        if path not in self.code_cache:
            self.code_cache[path] = []
        self.code_cache[path].append(fragment)
        
        return fragment
        
    def index_directory(self, directory: str, file_types: Optional[List[str]] = None) -> None:
        """Index all code files in a directory"""
        if file_types is None:
            file_types = ['.py', '.ts', '.js']
            
        for file_type in file_types:
            pattern = os.path.join(directory, f'**/*{file_type}')
            for file_path in glob.glob(pattern, recursive=True):
                if os.path.isfile(file_path) and not os.path.islink(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            
                            # Skip empty files
                            if not lines:
                                continue
                                
                            # Index file in chunks
                            chunk_size = 50
                            for i in range(0, len(lines), chunk_size):
                                chunk = ''.join(lines[i:i + chunk_size])
                                if chunk.strip():  # Skip empty chunks
                                    self.index_code(
                                        content=chunk,
                                        path=file_path,
                                        start_line=i + 1,
                                        end_line=min(i + chunk_size, len(lines))
                                    )
                    except Exception as e:
                        print(f"Error indexing {file_path}: {e}")
                        
    def search(self, query: str, min_perplexity: float = 0, max_perplexity: float = float('inf')) -> List[CodeFragment]:
        """Search for code using perplexity scores and quantum relevance"""
        results = []
        
        for fragments in self.code_cache.values():
            for fragment in fragments:
                if min_perplexity <= fragment.perplexity <= max_perplexity:
                    relevance = self.calculate_relevance(fragment.content, query)
                    if relevance > 0.1:  # Adjustable threshold
                        fragment.relevance = relevance  # Add relevance score to fragment
                        results.append(fragment)
                        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance, reverse=True)
        return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python quantum_search.py <directory> <search_query>")
        sys.exit(1)
        
    directory = sys.argv[1]
    query = sys.argv[2]
    
    searcher = QuantumPerplexitySearch()
    print(f"Indexing directory: {directory}")
    searcher.index_directory(directory)
    
    print(f"\nSearching for: {query}")
    results = searcher.search(query)
    
    print("\nSearch Results:")
    print("-" * 40)
    
    for i, result in enumerate(results[:5], 1):
        print(f"\n{i}. File: {result.path}")
        print(f"Lines {result.start_line}-{result.end_line}")
        print(f"Relevance Score: {result.relevance:.2f}")
        print("Code:")
        print("-" * 20)
        print(result.content.strip())
        print("-" * 40)
