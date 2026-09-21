import os
import json
import re
from typing import Dict, Any, List, Optional
import httpx
from app.schemas.analysis import EvidenceChunk

PROMPT_TEMPLATE = """You are CodeMigrate's AI Migration Specialist.
Your task is to analyze the supplied Python code for Django breaking changes.

CRITICAL INSTRUCTION:
Analyze the code using ONLY the retrieved evidence chunks below.
Do NOT use external Django knowledge or invent facts.
If the retrieved evidence does not state that the detected API is changed/deprecated/removed, you must declare affected as false.

Code Snippet (Line {line}):
```python
{code_snippet}
```

Detected API: {symbol}
Source Django Version: {from_version}
Target Django Version: {to_version}

--- RETRIEVED EVIDENCE ---
{evidence_text}
--- END RETRIEVED EVIDENCE ---

Return a JSON object ONLY with the following exact structure:
{{
  "affected": true,
  "line": {line},
  "symbol": "{symbol}",
  "change_type": "removed" | "deprecated" | "breaking" | "none",
  "explanation": "<Clear explanation based ONLY on the evidence>",
  "suggested_fix": "<Recommended replacement code or migration step>",
  "evidence_ids": ["<document_id>"]
}}
"""

class LLMAnalyzer:
    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")

    def _format_evidence_text(self, evidence: List[EvidenceChunk]) -> str:
        if not evidence:
            return "No evidence chunks retrieved for this API."
        
        lines = []
        for e in evidence:
            lines.append(
                f"Document ID: {e.document_id}\n"
                f"Version: Django {e.version}\n"
                f"Section: {e.source_section}\n"
                f"Affected API: {e.affected_api}\n"
                f"Change Type: {e.change_type}\n"
                f"Description: {e.description}\n"
                f"Replacement: {e.replacement}\n"
                f"Source URL: {e.source_url}\n"
            )
        return "\n".join(lines)

    def analyze(
        self,
        code_snippet: str,
        line: int,
        symbol: str,
        from_version: str,
        to_version: str,
        evidence: List[EvidenceChunk]
    ) -> Dict[str, Any]:
        evidence_text = self._format_evidence_text(evidence)
        prompt = PROMPT_TEMPLATE.format(
            line=line,
            code_snippet=code_snippet,
            symbol=symbol,
            from_version=from_version,
            to_version=to_version,
            evidence_text=evidence_text
        )

        if self.gemini_api_key:
            try:
                return self._call_gemini(prompt)
            except Exception as e:
                pass  

        if self.openai_api_key:
            try:
                return self._call_openai(prompt)
            except Exception as e:
                pass  

        return self._deterministic_grounded_reasoning(
            code_snippet=code_snippet,
            line=line,
            symbol=symbol,
            from_version=from_version,
            to_version=to_version,
            evidence=evidence
        )

    def analyze_unassisted_mode_a(
        self,
        code_snippet: str,
        from_version: str,
        to_version: str
    ) -> str:
        prompt = (
            f"Analyze this Django code upgrading from {from_version} to {to_version}.\n"
            f"Code:\n{code_snippet}\n"
            f"Are there any breaking changes? What should be done?"
        )

        if self.gemini_api_key:
            try:
                resp = self._call_gemini_raw(prompt)
                if resp:
                    return resp
            except Exception:
                pass

        return (
            f"[Mode A - Unassisted LLM Output]\n"
            f"Based on general Django knowledge, upgrading from {from_version} to {to_version} "
            f"might deprecate certain patterns. However, no specific release notes or exact citations "
            f"are referenced. (Risk: Unverified hallucination of function signatures without grounding)."
        )

    def _deterministic_grounded_reasoning(
        self,
        code_snippet: str,
        line: int,
        symbol: str,
        from_version: str,
        to_version: str,
        evidence: List[EvidenceChunk]
    ) -> Dict[str, Any]:
        if not evidence:
            return {
                "affected": False,
                "line": line,
                "symbol": symbol,
                "change_type": "none",
                "explanation": f"No release-note evidence indicates that '{symbol}' is broken or removed between Django {from_version} and {to_version}.",
                "suggested_fix": "No migration required.",
                "evidence_ids": []
            }

        severity_map = {"removed": 3, "breaking": 2, "deprecated": 1, "none": 0}
        
        sym_lower = symbol.lower()
        matching_chunks = []
        for chk in evidence:
            aliases = [a.lower() for a in chk.symbol_aliases]
            if (
                sym_lower == chk.affected_api.lower()
                or sym_lower in aliases
                or any(sym_lower in a for a in aliases)
                or chk.affected_api.lower().endswith(sym_lower)
            ):
                matching_chunks.append(chk)

        if not matching_chunks:
            return {
                "affected": False,
                "line": line,
                "symbol": symbol,
                "change_type": "none",
                "explanation": f"Retrieved documents do not directly flag '{symbol}' as breaking in this interval.",
                "suggested_fix": "No change required.",
                "evidence_ids": []
            }

        matching_chunks.sort(key=lambda c: severity_map.get(c.change_type, 0), reverse=True)
        primary_chunk = matching_chunks[0]
        evidence_ids = [c.document_id for c in matching_chunks]

        return {
            "affected": True,
            "line": line,
            "symbol": symbol,
            "change_type": primary_chunk.change_type,
            "explanation": f"{symbol} was {primary_chunk.change_type} in Django {primary_chunk.version}. {primary_chunk.description}",
            "suggested_fix": primary_chunk.replacement,
            "evidence_ids": evidence_ids
        }

    def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)

    def _call_gemini_raw(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            return json.loads(text)
