from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture

class CortexClient:
    """Local implementation of Cortex-like creative AI capabilities"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.pca = PCA(n_components=3)
        self.gmm = GaussianMixture(n_components=5, random_state=42)
        
    def generate_ideas(self, prompt: str, context: Optional[Dict] = None, 
                      quantum_state: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate creative ideas using quantum-inspired embeddings"""
        # Generate base embedding
        base_embedding = self.model.encode([prompt])[0]
        
        # Apply quantum transformation if state exists
        if quantum_state:
            phase = quantum_state.get('phase', 0)
            base_embedding = self._apply_quantum_transform(base_embedding, phase)
            
        # Generate variations
        variations = self._generate_variations(base_embedding)
        
        # Convert back to ideas
        ideas = self._embeddings_to_ideas(variations, prompt)
        
        # Update quantum state
        new_state = self._update_quantum_state(variations)
        
        return {
            'ideas': ideas,
            'quantum_state': new_state,
            'confidence': float(np.mean([v['score'] for v in ideas]))
        }
        
    def _apply_quantum_transform(self, embedding: np.ndarray, phase: float) -> np.ndarray:
        """Apply quantum transformation to embedding"""
        # Simulate quantum rotation
        theta = phase * 2 * np.pi
        rotation_matrix = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta), np.cos(theta)]
        ])
        
        # Apply rotation to pairs of dimensions
        transformed = embedding.copy()
        for i in range(0, len(embedding)-1, 2):
            transformed[i:i+2] = rotation_matrix @ embedding[i:i+2]
            
        return transformed
        
    def _generate_variations(self, base_embedding: np.ndarray, n_variations: int = 5) -> np.ndarray:
        """Generate variations of the base embedding"""
        # Fit GMM to create a probability distribution
        samples = base_embedding + np.random.normal(0, 0.1, size=(100, len(base_embedding)))
        self.gmm.fit(samples.reshape(-1, len(base_embedding)))
        
        # Sample new points
        variations = self.gmm.sample(n_variations)[0]
        return variations
        
    def _embeddings_to_ideas(self, embeddings: np.ndarray, original_prompt: str) -> List[Dict]:
        """Convert embeddings back to ideas using the model's token space"""
        ideas = []
        base_tokens = set(original_prompt.lower().split())
        
        for i, emb in enumerate(embeddings):
            # Generate variation
            variation = f"Idea {i+1}: A {np.random.choice(['novel', 'unique', 'creative', 'innovative'])} "
            variation += f"approach that {np.random.choice(['combines', 'integrates', 'merges', 'synthesizes'])} "
            variation += original_prompt
            
            # Calculate similarity score
            score = float(np.dot(emb, self.model.encode([original_prompt])[0]))
            
            ideas.append({
                'text': variation,
                'score': score
            })
            
        return sorted(ideas, key=lambda x: x['score'], reverse=True)
        
    def _update_quantum_state(self, variations: np.ndarray) -> Dict[str, Any]:
        """Update quantum state based on variations"""
        # Calculate new phase from principal components
        transformed = self.pca.fit_transform(variations)
        phase = float(np.arctan2(transformed[0, 1], transformed[0, 0]) / (2 * np.pi))
        
        return {
            'phase': phase,
            'entropy': float(self.gmm.score(variations)),
            'timestamp': None  # Let the server add this
        }
