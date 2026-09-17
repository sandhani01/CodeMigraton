"""Hybrid Retriever combining Exact Symbol Matching, Vector Search, and Version Filtering.
"""

from typing import List, Dict, Set
from app.schemas.analysis import EvidenceChunk
from app.rag.vector_store import InMemoryVectorStore


class HybridRetriever:
    def __init__(self, vector_store: InMemoryVectorStore):
        self.vector_store = vector_store

    def retrieve(
        self,
        api_symbol: str,
        from_version: str,
        to_version: str,
        max_evidence: int = 4
    ) -> List[EvidenceChunk]:
        """Retrieves evidence chunks for a given detected API symbol within the version range."""
        seen_doc_ids: Set[str] = set()
        combined_evidence: List[EvidenceChunk] = []

        # 1. Exact API / Alias Matching (High Precision)
        exact_matches = self.vector_store.search_exact(
            symbol_name=api_symbol,
            from_version=from_version,
            to_version=to_version
        )
        for chunk in exact_matches:
            if chunk.document_id not in seen_doc_ids:
                seen_doc_ids.add(chunk.document_id)
                combined_evidence.append(chunk)

        # 2. Semantic Vector Search (High Recall)
        query = f"Django {api_symbol} migration from {from_version} to {to_version} breaking change removed deprecated"
        vector_matches = self.vector_store.search_vector(
            query=query,
            from_version=from_version,
            to_version=to_version,
            top_k=max_evidence
        )
        for chunk, score in vector_matches:
            if chunk.document_id not in seen_doc_ids:
                seen_doc_ids.add(chunk.document_id)
                combined_evidence.append(chunk)

        # Return capped evidence
        return combined_evidence[:max_evidence]
