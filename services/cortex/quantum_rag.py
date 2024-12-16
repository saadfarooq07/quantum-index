from typing import List, Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from metal_accelerator import MetalAccelerator, MetalConfig
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Milvus
from langchain.schema import Document

@dataclass
class RealityMetrics:
    token_confidence: float
    context_coherence: float
    retrieval_relevance: float
    human_trust: float
    warning_flags: int = 0

class QuantumRAG:
    def __init__(
        self,
        embedding_model: str = "BAAI/bge-small-en-v1.5",
        metal_config: Optional[MetalConfig] = None,
        milvus_uri: str = "localhost:19530"
    ):
        self.accelerator = MetalAccelerator(metal_config)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": self.accelerator.device}
        )
        self.vector_store = Milvus(
            embedding_function=self.embeddings,
            connection_args={"uri": milvus_uri}
        )
        self.reality_metrics = []
        
    async def retrieve_and_validate(
        self, 
        query: str, 
        k: int = 5
    ) -> Tuple[List[Document], RealityMetrics]:
        """Retrieve relevant documents and validate reality"""
        # Generate query embedding with Metal acceleration
        query_embedding = await self._generate_embedding(query)
        
        # Retrieve similar documents
        docs = await self._retrieve_documents(query_embedding, k)
        
        # Validate retrieval with quantum-inspired metrics
        metrics = await self._compute_reality_metrics(query, docs)
        
        # Store metrics for adaptive learning
        self.reality_metrics.append(metrics)
        
        return docs, metrics
    
    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embeddings using Metal-accelerated model"""
        embedding = self.embeddings.embed_query(text)
        return self.accelerator.prepare_embeddings(embedding)
    
    async def _retrieve_documents(
        self, 
        embedding: np.ndarray, 
        k: int
    ) -> List[Document]:
        """Retrieve similar documents from vector store"""
        return self.vector_store.similarity_search_by_vector(embedding, k)
    
    async def _compute_reality_metrics(
        self, 
        query: str, 
        docs: List[Document]
    ) -> RealityMetrics:
        """Compute quantum-inspired reality metrics"""
        # Token confidence based on embedding similarity
        token_confidence = self._compute_token_confidence(query, docs)
        
        # Context coherence using quantum-inspired measurement
        context_coherence = self._compute_context_coherence(docs)
        
        # Retrieval relevance using superposition principle
        retrieval_relevance = self._compute_retrieval_relevance(query, docs)
        
        # Human trust factor (initialized to 1.0, updated through feedback)
        human_trust = 1.0
        
        return RealityMetrics(
            token_confidence=token_confidence,
            context_coherence=context_coherence,
            retrieval_relevance=retrieval_relevance,
            human_trust=human_trust
        )
    
    def _compute_token_confidence(
        self, 
        query: str, 
        docs: List[Document]
    ) -> float:
        """Compute token confidence using quantum measurement"""
        query_embedding = self.embeddings.embed_query(query)
        doc_embeddings = [
            self.embeddings.embed_query(doc.page_content) 
            for doc in docs
        ]
        
        # Compute superposition state
        superposition = np.mean(doc_embeddings, axis=0)
        
        # Measure similarity as quantum probability
        similarity = np.dot(query_embedding, superposition) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(superposition)
        )
        
        return float(abs(similarity))
    
    def _compute_context_coherence(self, docs: List[Document]) -> float:
        """Compute context coherence using entanglement-inspired metric"""
        doc_embeddings = [
            self.embeddings.embed_query(doc.page_content) 
            for doc in docs
        ]
        
        # Compute pairwise "entanglement" between documents
        coherence_sum = 0.0
        for i in range(len(doc_embeddings)):
            for j in range(i + 1, len(doc_embeddings)):
                similarity = np.dot(doc_embeddings[i], doc_embeddings[j]) / (
                    np.linalg.norm(doc_embeddings[i]) * 
                    np.linalg.norm(doc_embeddings[j])
                )
                coherence_sum += abs(similarity)
        
        n_pairs = (len(docs) * (len(docs) - 1)) / 2
        return float(coherence_sum / max(1, n_pairs))
    
    def _compute_retrieval_relevance(
        self, 
        query: str, 
        docs: List[Document]
    ) -> float:
        """Compute retrieval relevance using quantum measurement"""
        query_embedding = self.embeddings.embed_query(query)
        relevance_scores = []
        
        for doc in docs:
            doc_embedding = self.embeddings.embed_query(doc.page_content)
            # Compute quantum-inspired probability amplitude
            amplitude = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            # Convert to probability
            probability = abs(amplitude) ** 2
            relevance_scores.append(probability)
        
        return float(np.mean(relevance_scores))
    
    def update_human_trust(self, feedback_score: float):
        """Update human trust factor based on feedback"""
        if self.reality_metrics:
            current_metrics = self.reality_metrics[-1]
            current_metrics.human_trust = feedback_score
            
    def get_device_info(self) -> Dict[str, str]:
        """Get information about the Metal device configuration"""
        return self.accelerator.get_device_info()
