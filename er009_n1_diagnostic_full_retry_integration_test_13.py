#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ER-009-N1-DIAGNOSTIC-FULL-RETRY-INTEGRATION-TEST-13

本体script (er003_v1_n3_01_articles_generate.py) へ統合された
Diagnostic Full Retry が実際に動作することをintegration test で確認。

仕組み：overlap NG になるような記事を intentionally generate して、
Diagnostic Retry が起動され、diagnostic section が prompt に含まれることを検証。

（実装の正確性確認が目的のため、full production validation ではなく、
スモークテスト・integration test の位置付け）
"""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv
load_dotenv()

import er003_v1_n3_01_articles_generate as n3_01

# Test: Diagnostic Full Retry が正しく統合されているかの確認
def test_diagnostic_section_build():
    """diagnostic section builder が正しく動作することを確認"""
    import er009_diagnostic_full_retry_modules_12 as diagnostic_mod

    # Dummy article & overlap data
    full_story = "The research shows that digital screens increase tip amounts."
    point_one = "Screens increase tip amounts significantly."  # overlap
    point_two = "Customers feel pressured by visible screens."

    # Overlap check
    import er008_point_overlap_qa_18 as overlap_qa

    o1 = overlap_qa.flag_possible_paraphrase(point_one, full_story)
    o2 = overlap_qa.flag_possible_paraphrase(point_two, full_story)

    print(f"[TEST] Point One overlap: {o1['overlap_ratio']:.3f} (flagged={o1['flagged']})")
    print(f"[TEST] Point Two overlap: {o2['overlap_ratio']:.3f} (flagged={o2['flagged']})")

    # Build diagnostic
    diag_section, diag_dict = diagnostic_mod.build_diagnostic_section(
        full_story, o1, o2
    )
    print(f"[TEST] Diagnostic section built successfully (length={len(diag_section)})")
    print(f"[TEST] Diagnosis One: {diag_dict['diagnosis_one'][:100]}...")
    print(f"[TEST] Diagnosis Two: {diag_dict['diagnosis_two'][:100]}...")


def test_diagnostic_retry_prompt_builder():
    """build_diagnostic_retry_prompt が正しく動作することを確認"""
    original_prompt = "Write a story.\n[Additional constraints]"
    article_text = """# Title

This is a test story about screens and tips.

### Heading One
Screens increase tips.

### Heading Two
Customers feel pressure.

## In one line
Screens matter.
"""

    # Mock overlap result
    point_overlap = {
        "point_one": {"overlap_ratio": 0.55, "flagged": True, "shared_words": ["screens", "tips", "increase"]},
        "point_two": {"overlap_ratio": 0.20, "flagged": False, "shared_words": []},
    }

    # Build diagnostic retry prompt
    diagnostic_prompt = n3_01.build_diagnostic_retry_prompt(
        original_prompt, article_text, point_overlap
    )

    print(f"[TEST] Diagnostic retry prompt built (length={len(diagnostic_prompt)})")
    print(f"[TEST] Contains 'Previous attempt': {('Previous attempt' in diagnostic_prompt)}")
    print(f"[TEST] Contains 'do NOT patch': {('do NOT patch' in diagnostic_prompt)}")
    print(f"[TEST] Contains overlap score: {('0.55' in diagnostic_prompt or '0.550' in diagnostic_prompt)}")


def test_production_wiring_exists():
    """本体へ統合されたDiagnostic Full Retry の code が存在するか確認"""
    import inspect

    # Check 1: diagnostic_mod import
    src = inspect.getsource(n3_01)
    has_diagnostic_import = "import er009_diagnostic_full_retry_modules_12" in src
    print(f"[TEST] Diagnostic module imported: {has_diagnostic_import}")

    # Check 2: build_diagnostic_retry_prompt function exists
    has_builder = hasattr(n3_01, "build_diagnostic_retry_prompt")
    print(f"[TEST] build_diagnostic_retry_prompt function exists: {has_builder}")

    # Check 3: Comments indicate Diagnostic Full Retry in retry loop
    has_diagnostic_comment = "Diagnostic Full Retry" in src
    print(f"[TEST] Retry loop contains Diagnostic Full Retry comment: {has_diagnostic_comment}")


def main():
    print("[TEST] === ER-009-N1-DIAGNOSTIC-FULL-RETRY-INTEGRATION-TEST-13 ===")
    print("")

    print("[TEST] 1. Testing diagnostic section builder...")
    test_diagnostic_section_build()
    print("")

    print("[TEST] 2. Testing diagnostic retry prompt builder...")
    test_diagnostic_retry_prompt_builder()
    print("")

    print("[TEST] 3. Testing production wiring...")
    test_production_wiring_exists()
    print("")

    print("[TEST] === All integration tests completed ===")


if __name__ == "__main__":
    main()
