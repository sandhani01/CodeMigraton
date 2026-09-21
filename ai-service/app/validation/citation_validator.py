from typing import List, Dict, Any, Tuple
from app.schemas.analysis import EvidenceChunk, Citation, Finding

class CitationValidator:
    @staticmethod
    def validate_finding(
        llm_output: Dict[str, Any],
        retrieved_evidence: List[EvidenceChunk],
        line_number: int,
        symbol_name: str
    ) -> Finding:
        
        if not retrieved_evidence:
            return Finding(
                line=line_number,
                symbol=symbol_name,
                status="UNVERIFIED",
                change_type="none",
                explanation="No supporting Django release-note evidence was found in the dataset for this migration window.",
                suggested_fix="No verified migration fix available.",
                citations=[]
            )

        evidence_map: Dict[str, EvidenceChunk] = {
            chunk.document_id: chunk for chunk in retrieved_evidence
        }

        raw_evidence_ids = llm_output.get("evidence_ids", [])
        if isinstance(raw_evidence_ids, str):
            raw_evidence_ids = [raw_evidence_ids]

        valid_citations: List[Citation] = []
        for doc_id in raw_evidence_ids:
            if doc_id in evidence_map:
                chunk = evidence_map[doc_id]
                valid_citations.append(
                    Citation(
                        document_id=chunk.document_id,
                        version=chunk.version,
                        title=chunk.source_section,
                        source_url=chunk.source_url,
                        supporting_text=chunk.description
                    )
                )

        if not valid_citations:
            for chunk in retrieved_evidence:
                if symbol_name.lower() in [s.lower() for s in chunk.symbol_aliases] or symbol_name.lower() in chunk.affected_api.lower():
                    valid_citations.append(
                        Citation(
                            document_id=chunk.document_id,
                            version=chunk.version,
                            title=chunk.source_section,
                            source_url=chunk.source_url,
                            supporting_text=chunk.description
                        )
                    )
                    break

        is_affected = bool(llm_output.get("affected", False))
        
        if is_affected and valid_citations:
            status = "VERIFIED"
            change_type = llm_output.get("change_type", valid_citations[0].supporting_text and "breaking" or "removed")
            explanation = llm_output.get("explanation", valid_citations[0].supporting_text)
            suggested_fix = llm_output.get("suggested_fix", valid_citations[0].supporting_text)
        elif not is_affected and not valid_citations:
            status = "UNVERIFIED"
            change_type = "none"
            explanation = "No evidence found indicating this API is deprecated or removed in the specified version range."
            suggested_fix = "No migration required."
        elif is_affected and not valid_citations:
            status = "UNVERIFIED"
            change_type = "unsupported_claim"
            explanation = "Unverified claim: LLM claimed a breaking change, but no authentic retrieved citation supports this."
            suggested_fix = "Cannot recommend migration without verifiable evidence."
        else:
            status = "VERIFIED"
            change_type = "not_affected"
            explanation = llm_output.get("explanation", "Code is not affected by breaking changes in this migration range.")
            suggested_fix = "No change needed."

        return Finding(
            line=line_number,
            symbol=symbol_name,
            status=status,
            change_type=change_type,
            explanation=explanation,
            suggested_fix=suggested_fix,
            citations=valid_citations
        )
