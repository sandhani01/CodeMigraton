"""Document Ingestion & Meaningful Chunking for Django Breaking Changes.

Loads release-note dataset, cleans content, attaches structured metadata,
and formats each entry as a retrieval-optimized chunk.
"""

import json
import os
from typing import List, Dict, Any
from app.schemas.analysis import EvidenceChunk


def format_chunk_content(entry: Dict[str, Any]) -> str:
    """Creates a rich, natural language chunk representation for semantic retrieval."""
    aliases_str = ", ".join(entry.get("symbol_aliases", []))
    labels_str = ", ".join(entry.get("labels", []))
    
    return (
        f"Django {entry.get('version')} Release Notes: {entry.get('source_section')}\n"
        f"Affected API: {entry.get('affected_api')}\n"
        f"Aliases: {aliases_str}\n"
        f"Change Type: {entry.get('change_type')}\n"
        f"Description: {entry.get('description')}\n"
        f"Migration / Replacement: {entry.get('replacement')}\n"
        f"Tags: {labels_str}"
    )


def load_dataset_chunks(dataset_path: str) -> List[EvidenceChunk]:
    """Loads dataset entries and parses them into structured EvidenceChunk objects."""
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found at: {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chunks: List[EvidenceChunk] = []
    for item in data:
        content_text = format_chunk_content(item)
        chunk = EvidenceChunk(
            document_id=item["document_id"],
            library=item.get("library", "django"),
            version=str(item["version"]),
            change_type=item.get("change_type", "breaking"),
            affected_api=item["affected_api"],
            symbol_aliases=item.get("symbol_aliases", [item["affected_api"]]),
            source_section=item.get("source_section", "Release Notes"),
            source_url=item["source_url"],
            description=item["description"],
            replacement=item.get("replacement", ""),
            labels=item.get("labels", []),
            content_text=content_text
        )
        chunks.append(chunk)

    return chunks
