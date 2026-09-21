from typing import List, Tuple, Optional
import numpy as np
from app.schemas.analysis import EvidenceChunk
from app.rag.embeddings import LightweightEmbeddingModel
from app.rag.version_filter import is_version_in_range

class InMemoryVectorStore:
    def __init__(self):
        self.chunks: List[EvidenceChunk] = []
        self.embeddings: Optional[np.ndarray] = None
        self.embedding_model = LightweightEmbeddingModel()

    def add_documents(self, chunks: List[EvidenceChunk]) -> None:
        self.chunks.extend(chunks)
        texts = [chunk.content_text for chunk in self.chunks]
        self.embedding_model.fit(texts)
        self.embeddings = self.embedding_model.embed_batch(texts)

    def search_vector(
        self,
        query: str,
        from_version: Optional[str] = None,
        to_version: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.05
    ) -> List[Tuple[EvidenceChunk, float]]:
        if self.embeddings is None or len(self.chunks) == 0:
            return []

        query_vec = self.embedding_model.embed_text(query)
        scores = np.dot(self.embeddings, query_vec)

        results: List[Tuple[EvidenceChunk, float]] = []
        for idx, score in enumerate(scores):
            chunk = self.chunks[idx]
            
            if from_version and to_version:
                if not is_version_in_range(chunk.version, from_version, to_version):
                    continue

            if score >= min_score:
                results.append((chunk, float(score)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def search_exact(
        self,
        symbol_name: str,
        from_version: Optional[str] = None,
        to_version: Optional[str] = None
    ) -> List[EvidenceChunk]:
        matches: List[EvidenceChunk] = []
        sym_lower = symbol_name.lower()
        
        for chunk in self.chunks:
            if from_version and to_version:
                if not is_version_in_range(chunk.version, from_version, to_version):
                    continue

            aliases = [a.lower() for a in chunk.symbol_aliases]
            affected = chunk.affected_api.lower()
            
            if (
                sym_lower == affected
                or sym_lower in aliases
                or (len(sym_lower) > 3 and (sym_lower in affected or any(sym_lower in a for a in aliases)))
            ):
                matches.append(chunk)

        return matches
