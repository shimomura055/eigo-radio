"""phase_d_e2e_check.py

USER-TEST-SCRIPT-READABILITY-PROD-01 Phase D専用。既存
docs/pm/tools/user_test_readability_check.py の check_one()をそのまま
import して再利用し(新規E2Eロジックの創作ではない)、対象2 level(new src)
だけをPC/mobileで検証する。TSVは旧srcのままのため、本スクリプトは
--targets(name,src,level,en,ja,expect_highlight_count)を直接指定する。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from user_test_readability_check import build_unified_url, check_one  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--screenshots", default=None)
    ap.add_argument("--play-wait-seconds", type=float, default=4.0)
    args = ap.parse_args()

    targets = [
        {
            "name": "free_address_A2",
            "src": "er012_output/editorial_b_family_voices_a2_production_wiring_01/kp_fix_01/a2/player.html",
            "level": "A2", "en": "One Office, Two Ideas of a Place to Work",
            "ja": "一つのオフィスに、働く場所についての二つの考え方",
            "expect": {"expect_highlight_count": 5, "expect_translation": False},
        },
        {
            "name": "ai_hiring_A2",
            "src": "er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/kp_fix_01/a2/player.html",
            "level": "A2", "en": "When AI Helps Choose Who Gets Hired",
            "ja": "AIが採用を選ぶとき",
            "expect": {"expect_highlight_count": 6, "expect_translation": False},
        },
    ]

    from playwright.sync_api import sync_playwright

    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for viewport, mobile in (({"width": 1280, "height": 800}, False), ({"width": 390, "height": 844}, True)):
            context = browser.new_context(viewport=viewport)
            for t in targets:
                url = build_unified_url(args.base, t["src"], t["level"], t["en"], t["ja"])
                page = context.new_page()
                page.set_default_timeout(20000)
                key = t["name"] + ("_mobile" if mobile else "_pc")
                try:
                    results[key] = check_one(page, t["name"], url, t["expect"], args.screenshots,
                                              args.play_wait_seconds, mobile)
                finally:
                    page.close()
                r = results[key]
                print(f"[{r['status']}] {key}", flush=True)
                for reason in r.get("reasons", []):
                    print(f"    - {reason}", flush=True)
            context.close()
        browser.close()

    all_pass = all(r["status"] == "PASS" for r in results.values())
    summary = {"overall": "PASS" if all_pass else "FAIL", "results": results}
    Path(args.out).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"overall: {summary['overall']}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
