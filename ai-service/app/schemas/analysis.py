from typing import List, Optional
from pydantic import BaseModel, Field

class AnalysisRequest(BaseModel):
    code: str = Field(..., description="Source code written in older Django")
    library: str = Field(default="django", description="Target library (default: django)")
    from_version: str = Field(default="4.0", description="Source/starting version (e.g. 4.0)")
    to_version: str = Field(default="5.1", description="Target version (e.g. 5.1)")

class Citation(BaseModel):
    document_id: str = Field(..., description="Unique dataset document identifier (e.g. django-5.0-001)")
    version: str = Field(..., description="Django version where the change occurred")
    title: str = Field(..., description="Title or section name of the release notes")
    source_url: str = Field(..., description="Official documentation URL")
    supporting_text: str = Field(..., description="Exact supporting text / description")

class Finding(BaseModel):
    line: int = Field(..., description="Source line number where the affected API was detected")
    symbol: str = Field(..., description="Affected API symbol name")
    status: str = Field(..., description="VERIFIED if grounded in retrieved evidence, otherwise UNVERIFIED")
    change_type: str = Field(..., description="Type of change: removed, deprecated, breaking, or none")
    explanation: str = Field(..., description="Grounded explanation of what changed")
    suggested_fix: str = Field(..., description="Recommended migration path or replacement")
    citations: List[Citation] = Field(default_factory=list, description="Verified citations")

class AnalysisResponse(BaseModel):
    status: str = Field(..., description="Analysis status (e.g. completed, unverified)")
    from_version: str
    to_version: str
    findings: List[Finding]
    raw_evidence_count: int = Field(default=0, description="Total evidence chunks retrieved")

class EvidenceChunk(BaseModel):
    document_id: str
    library: str
    version: str
    change_type: str
    affected_api: str
    symbol_aliases: List[str] = Field(default_factory=list)
    source_section: str
    source_url: str
    description: str
    replacement: str
    labels: List[str] = Field(default_factory=list)
    content_text: str = Field(default="", description="Full text representation for retrieval")
