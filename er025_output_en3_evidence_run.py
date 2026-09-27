# ============================================================
# er025_output_en3_evidence_run.py
# PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01(Sonnet修正1回目)
# EN-3 runtime evidence: BLOCKER-1是正後、"plus"/"surplus"/"minister"を
# 含む回帰fixtureと、Family X small_bagの実segment textでhits=0(誤注入
# ゼロ)を機械確認する。費用¥0(API呼び出しなし、Ledger読み取りのみ)。
# ============================================================
from __future__ import annotations

import json

import er006_pronunciation_ledger_01 as ledger
import er006_pronunciation_tts_injection_01 as inject

OUT_PATH = "er025_output/pronunciation_resolution_phase2_evidence_01/en3_evidence_summary.json"


def main():
    results = {"regression_fixture": {}, "family_x_small_bag_segments": {}}

    # 1) 回帰fixture(委任文指定どおり)
    regression_texts = {
        "plus_via_surplus": "The government reported a budget surplus this quarter.",
        "mini_via_minister": "The finance minister announced new measures today.",
        "plus_literal_word": "We saw a plus sign on the whiteboard.",
    }
    for name, text in regression_texts.items():
        augmented, hits = inject.augment_style_prefix_with_pronunciation("Speak naturally.", text)
        results["regression_fixture"][name] = {
            "text": text, "hits": hits, "augmented_equals_input": augmented == "Speak naturally.",
        }

    # 2) Family X small_bag実segment(Stage 3c artifact、parts.jsonから抽出)
    parts_path = ("er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/"
                  "small_bag__run_02/a2/parts.json")
    parts = json.load(open(parts_path, encoding="utf-8"))
    # full_story系のみ対象(mini/Toteme/Altuzarra等の固有名詞が実際に出現する本文)
    for key in ("part1", "body2", "body3"):
        text = parts.get(key) if isinstance(parts.get(key), str) else None
        if not text:
            continue
        augmented, hits = inject.augment_style_prefix_with_pronunciation("Speak naturally.", text)
        results["family_x_small_bag_segments"][key] = {
            "text_excerpt": text[:200], "hits": hits,
        }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"saved: {OUT_PATH}")
    print(json.dumps(results, ensure_ascii=False, indent=2)[:3000])


if __name__ == "__main__":
    main()
