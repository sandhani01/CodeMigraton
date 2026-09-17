# CodeMigrate — Step 1: AI/RAG Proof of Concept

A prototype demonstrating deterministic code analysis combined with version-aware RAG for Python/Django migrations.

## Architecture

```text
                    CodeMigrate Step 1

                    Python Code
                         │
                         ▼
                   Python AST
                         │
                         ▼
                Extract Django APIs
                         │
                         ▼
                  Retrieval Query
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       Exact API search       Vector search
              │                     │
              └──────────┬──────────┘
                         ▼
                 Version filtering (packaging.version)
                         │
                         ▼
                 Relevant evidence
                         │
                         ▼
                       LLM
                         │
                         ▼
               Structured analysis
                         │
                         ▼
              Citation validation
                         │
                         ▼
                  Final finding
```

---

## Key Features

1. **Deterministic AST Code Analyzer**: Uses Python's standard library `ast` module to locate Django imports, function calls, and attribute lookups with exact source line numbers.
2. **Strict Semantic Version Filtering**: Enforces `from_version < change_version <= to_version` with `packaging.version.parse`.
3. **Transparent In-Memory Vector Store**: Calculates vector cosine similarities without heavy opaque frameworks.
4. **Grounded LLM Reasoning**: Restricts the model to reason strictly from retrieved evidence and output structured JSON.
5. **Deterministic Citation Validation**: Every document ID, source section, and URL is verified against stored evidence before granting `VERIFIED` status.
6. **Strict Grounding Rule**: Unsubstantiated claims are rejected as `UNVERIFIED`.

---

## Quick Start

### 1. Activate Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Run the Interactive CLI Demonstration
```powershell
python demo.py
```
This demonstrates:
* **Mode A (Without RAG)**: Shows unassisted LLM speculation without proof.
* **Mode B (CodeMigrate)**: Runs AST -> RAG Evidence Retrieval -> Grounded Reasoning -> Citation Validation.
* **Grounding Rule**: Demonstrates refusal to make unverified claims on unaffected APIs.

### 3. Run the Ingestion Pipeline
```powershell
python ai-service\scripts\ingest.py
```

### 4. Run Automated Test Suite
```powershell
python ai-service\tests\test_api.py
```

### 5. Launch the FastAPI Service
```powershell
python -m uvicorn app.main:app --app-dir ai-service --reload --port 8000
```
Interactive Swagger UI: `http://127.0.0.1:8000/docs`

Endpoint:
```http
POST /analyze
Content-Type: application/json

{
  "code": "from django.utils.timezone import utc\nnow = utc",
  "library": "django",
  "from_version": "4.0",
  "to_version": "5.1"
}
```
