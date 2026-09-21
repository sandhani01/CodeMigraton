import os
from typing import List, Dict, Any, Tuple, Optional, Set
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, Finding, EvidenceChunk
from app.analysis.ast_analyzer import analyze_code_ast
from app.rag.ingestion import load_dataset_chunks
from app.rag.vector_store import InMemoryVectorStore
from app.rag.retriever import HybridRetriever
from app.llm.analyzer import LLMAnalyzer
from app.validation.citation_validator import CitationValidator

class CodeMigrateService:
    def __init__(self, dataset_path: Optional[str] = None):
        if dataset_path is None:
            dataset_path = os.path.join(os.path.dirname(__file__), "..", "data", "django_breaking_changes.json")
        
        self.dataset_path = os.path.abspath(dataset_path)
        self.vector_store = InMemoryVectorStore()
        self.retriever: Optional[HybridRetriever] = None
        self.llm_analyzer = LLMAnalyzer()
        self.validator = CitationValidator()
        self.initialized = False

    def initialize(self) -> None:
        if self.initialized:
            return
            
        chunks = load_dataset_chunks(self.dataset_path)
        self.vector_store.add_documents(chunks)
        self.retriever = HybridRetriever(self.vector_store)
        self.initialized = True

    def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        if not self.initialized:
            self.initialize()

        detected_symbols = analyze_code_ast(request.code)
        
        findings: List[Finding] = []
        total_evidence_retrieved = 0

        seen_keys = set()
        unique_symbols = []
        for s in detected_symbols:
            key = (s.line, s.name)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_symbols.append(s)

        for sym in unique_symbols:
            evidence = self.retriever.retrieve(
                api_symbol=sym.full_symbol,
                from_version=request.from_version,
                to_version=request.to_version,
                max_evidence=3
            )
            total_evidence_retrieved += len(evidence)

            llm_result = self.llm_analyzer.analyze(
                code_snippet=sym.code_context or request.code,
                line=sym.line,
                symbol=sym.full_symbol,
                from_version=request.from_version,
                to_version=request.to_version,
                evidence=evidence
            )

            finding = self.validator.validate_finding(
                llm_output=llm_result,
                retrieved_evidence=evidence,
                line_number=sym.line,
                symbol_name=sym.full_symbol
            )
            
            if finding.status == "VERIFIED" and finding.change_type not in ("none", "not_affected"):
                findings.append(finding)
            elif finding.status == "UNVERIFIED" and sym.symbol_type == "import":
                findings.append(finding)

        status = "completed" if findings else "completed_clean"
        return AnalysisResponse(
            status=status,
            from_version=request.from_version,
            to_version=request.to_version,
            findings=findings,
            raw_evidence_count=total_evidence_retrieved
        )
