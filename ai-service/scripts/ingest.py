"""Document Ingestion Script for CodeMigrate Step 1.

Pipeline:
    Dataset -> Load -> Clean -> Create Chunks -> Attach Metadata -> Embed -> Vector Store
"""

import sys
import os

# Add ai-service to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.rag.ingestion import load_dataset_chunks
from app.rag.vector_store import InMemoryVectorStore


def run_ingestion():
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "django_breaking_changes.json"))
    print("=" * 60)
    print(" CODEMIGRATE INGESTION PIPELINE")
    print("=" * 60)
    print(f"Loading dataset from: {dataset_path}")

    chunks = load_dataset_chunks(dataset_path)
    print(f"Loaded and validated {len(chunks)} breaking change chunks.")

    # Inspect sample metadata
    sample = chunks[0]
    print("\n--- Sample Document Metadata ---")
    print(f"Document ID    : {sample.document_id}")
    print(f"Library        : {sample.library}")
    print(f"Version        : {sample.version}")
    print(f"Change Type    : {sample.change_type}")
    print(f"Affected API   : {sample.affected_api}")
    print(f"Source Section : {sample.source_section}")
    print(f"Source URL     : {sample.source_url}")
    print(f"Description    : {sample.description}")
    print(f"Replacement    : {sample.replacement}")

    # Build vector store & index
    print("\nGenerating embeddings and indexing in vector store...")
    vector_store = InMemoryVectorStore()
    vector_store.add_documents(chunks)
    print(f"Indexed {len(vector_store.chunks)} documents into memory.")
    print(f"Embedding dimensions: {vector_store.embeddings.shape}")

    # Verification query
    print("\nTesting retrieval index for 'django.utils.timezone.utc'...")
    matches = vector_store.search_exact("django.utils.timezone.utc", from_version="4.0", to_version="5.1")
    print(f"Exact matches in (4.0 < v <= 5.1): {len(matches)}")
    for m in matches:
        print(f"  - [{m.document_id}] Django {m.version}: {m.change_type.upper()}")

    print("\nIngestion pipeline verified successfully!")


if __name__ == "__main__":
    run_ingestion()
