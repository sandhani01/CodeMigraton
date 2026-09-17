"""CodeMigrate Step 1 - AI/RAG Interactive Demonstration CLI.

Demonstrates:
- Mode A (Without RAG): Unassisted LLM guesswork without external citations.
- Mode B (CodeMigrate):
    * Deterministic AST API detection
    * Version-filtered RAG evidence retrieval
    * Visible RAG evidence display
    * Grounded LLM reasoning
    * Deterministic Citation Validation Layer
- Real Scenarios:
    1. Django 4.0 -> 5.1 Breaking Changes (django.utils.timezone.utc & get_storage_class)
    2. Django 3.2 -> 5.1 Routing Migration (django.conf.urls.url)
    3. Grounding Rule Enforcement (Standard / unchanged code without evidence)
"""

import sys
import os

# Add ai-service to sys.path
sys.path.insert(0, os.path.abspath("ai-service"))

from app.schemas.analysis import AnalysisRequest
from app.service import CodeMigrateService
from app.analysis.ast_analyzer import analyze_code_ast
from app.llm.analyzer import LLMAnalyzer


def print_banner(text: str):
    print("\n" + "=" * 65)
    print(f" {text}")
    print("=" * 65)


def print_section(title: str):
    print(f"\n---------------- {title} ----------------")


def run_demo():
    print_banner("CODEMIGRATE — DJANGO MIGRATION ANALYSIS CORE")
    print("Step 1: AI/RAG Proof of Concept Prototype")
    
    # Initialize service
    service = CodeMigrateService()
    service.initialize()
    llm = LLMAnalyzer()

    # =========================================================================
    # SCENARIO 1: Real Django 4.0 -> Django 5.1 Breaking Change
    # =========================================================================
    from_ver_1 = "4.0"
    to_ver_1 = "5.1"
    code_1 = """from django.utils.timezone import utc
from django.core.files.storage import get_storage_class
import datetime

# Older Django 4.0 patterns
current_time = datetime.datetime.now(tz=utc)
storage = get_storage_class('my.custom.Storage')()
"""

    print_banner(f"SCENARIO 1: DJANGO {from_ver_1} ===> DJANGO {to_ver_1}")
    print("[DETECTED SOURCE CODE]")
    print(code_1.strip())

    # -------------------------------------------------------------
    # Mode A: Without RAG
    # -------------------------------------------------------------
    print_banner("EXPERIMENT: MODE A — WITHOUT RAG (RAW LLM)")
    print("Sending code directly to raw LLM without external evidence...")
    mode_a_res = llm.analyze_unassisted_mode_a(code_1, from_ver_1, to_ver_1)
    print(mode_a_res)
    print("\n[Analysis]: Notice that raw LLM cannot provide verified document IDs,")
    print("            exact release-note URLs, or mathematically proven citations.")

    # -------------------------------------------------------------
    # Mode B: CodeMigrate
    # -------------------------------------------------------------
    print_banner("EXPERIMENT: MODE B — CODEMIGRATE (AST + RAG + CITATION VALIDATION)")

    # 1. AST Analysis
    print_section("1. AST CODE ANALYSIS")
    symbols_1 = analyze_code_ast(code_1)
    for s in symbols_1:
        print(f"Line {s.line:>2} | Type: {s.symbol_type:<16} | Symbol: {s.full_symbol}")

    # 2. Make RAG Visible
    print_section("2. RAG EVIDENCE RETRIEVAL (MAKING RAG VISIBLE)")
    for sym in ["django.utils.timezone.utc", "django.core.files.storage.get_storage_class"]:
        evidence_list = service.retriever.retrieve(sym, from_ver_1, to_ver_1, max_evidence=2)
        print(f"\nQuery Symbol: {sym}")
        for idx, ev in enumerate(evidence_list, 1):
            print(f"  [{idx}] {ev.document_id} — Django {ev.version} ({ev.source_section})")
            print(f"      Change Type : {ev.change_type.upper()}")
            print(f"      Description : {ev.description}")
            print(f"      Replacement : {ev.replacement}")
            print(f"      Source URL  : {ev.source_url}")

    # 3. AI Analysis & Citation Validation
    print_section("3. AI ANALYSIS & CITATION VALIDATION")
    req_1 = AnalysisRequest(
        code=code_1,
        library="django",
        from_version=from_ver_1,
        to_version=to_ver_1
    )
    result_1 = service.analyze(req_1)

    for finding in result_1.findings:
        print(f"\nLine {finding.line}: {finding.symbol}")
        print(f"Status          : {finding.status}")
        print(f"Change Type     : {finding.change_type.upper()}")
        print(f"Explanation     : {finding.explanation}")
        print(f"Suggested Fix   : {finding.suggested_fix}")
        if finding.citations:
            print("Citations:")
            for cit in finding.citations:
                print(f"  • [{cit.document_id}] Django {cit.version} Release Notes")
                print(f"    URL: {cit.source_url}")

    # =========================================================================
    # SCENARIO 2: URL Routing Migration (Django 3.2 -> Django 5.1)
    # =========================================================================
    from_ver_2 = "3.2"
    to_ver_2 = "5.1"
    code_2 = """from django.conf.urls import url

urlpatterns = [
    url(r'^home/$', home_view),
]"""

    print_banner(f"SCENARIO 2: DJANGO {from_ver_2} ===> DJANGO {to_ver_2} (URL ROUTING)")
    print("[DETECTED SOURCE CODE]")
    print(code_2.strip())

    req_2 = AnalysisRequest(
        code=code_2,
        library="django",
        from_version=from_ver_2,
        to_version=to_ver_2
    )
    result_2 = service.analyze(req_2)
    for finding in result_2.findings:
        print(f"\nLine {finding.line}: {finding.symbol}")
        print(f"Status          : {finding.status}")
        print(f"Change Type     : {finding.change_type.upper()}")
        print(f"Explanation     : {finding.explanation}")
        print(f"Suggested Fix   : {finding.suggested_fix}")
        for cit in finding.citations:
            print(f"Citation        : [{cit.document_id}] {cit.title} -> {cit.source_url}")

    # =========================================================================
    # SCENARIO 3: Grounding Rule (No Evidence / Refusal to Hallucinate)
    # =========================================================================
    print_banner("SCENARIO 3: GROUNDING RULE (NO EVIDENCE -> NO CLAIM)")
    clean_code = """from django.core.cache import cache

def fetch_profile(uid):
    return cache.get(f'user_{uid}')
"""
    print("[INPUT CODE WITH UNCHANGED API]")
    print(clean_code.strip())

    req_3 = AnalysisRequest(
        code=clean_code,
        library="django",
        from_version="4.0",
        to_version="5.1"
    )
    result_3 = service.analyze(req_3)

    print_section("AI ANALYSIS & CITATION VALIDATION")
    if not result_3.findings:
        print("Status          : VERIFIED CLEAN")
        print("Findings        : 0 breaking changes detected.")
        print("Grounding Rule  : System strictly refused to hallucinate any claims.")
    else:
        for f in result_3.findings:
            print(f"Status: {f.status} | {f.explanation}")

    print_banner("ALL DEMONSTRATION SCENARIOS COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    run_demo()
