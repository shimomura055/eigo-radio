# -*- coding: utf-8 -*-
"""W-1 golden fixture 生成(Phase 2 C1、2026-10-10、課金API 0件)。

C2(旧jaw/Fact Check撤去)の**前**のHEAD上で、Trial経路(fl.apply_factlock_patches() 適用下の jaw.build_original_prompt)が
実際に合成するR0 Promptと記号再生成Promptを、注記済みbrief全件について保存する。
C2後は jaw.build_original_prompt のsha自体が変わる(must_fix/full_ledger_text引数削除)ため、Production
`build_r0_prompt()` の同一性は**この出力との文字列完全一致**で担保する(DESIGN_03 15-2 #1)。

fixture母集団(パスで確定):
  annotation_final : er052_output/factlock_astra_e2e_trial_01/annotation/final/<slug>/selected_brief_factlock.md  9本
  new_arm_runs     : er052_output/factlock_astra_e2e_trial_01/runs/<slug>/new/storyline_b3/selected_brief.md      8本
実行: .venv/Scripts/python.exe -X utf8 er053_output/risk_flagger_production_wiring_01/gen_w1_golden_01.py
出力: er053_output/risk_flagger_production_wiring_01/golden/w1_golden_prompts_01.json
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, REPO)
os.chdir(REPO)

import er003_audio_tts_asr_safety as safety  # noqa: E402
import er019_family_x_ja_writer_o_r1_r2_01 as jaw  # noqa: E402
import er052_factlock_astra_e2e_runner_01 as e2e  # noqa: E402
import er052_factlock_writer_trial_01_run as fl  # noqa: E402

T = "er052_output/factlock_astra_e2e_trial_01"
SLUGS_FINAL = ["byd_recall", "central_bank_mortgage", "hormuz", "meta", "openai_copyright", "semiconductor_earnings", "small_bag",
               "space_weapons", "streaming_price"]
SLUGS_RUNS = ["byd_recall", "hormuz", "meta", "openai_copyright", "semiconductor_earnings", "small_bag", "space_weapons", "streaming_price"]
SAMPLE_TEXT = "これはテスト（括弧）です。時刻は11:04…です。"   # 記号QA再生成Promptの固定サンプル入力


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def trial_prompts(md_path):
    text = open(md_path, encoding="utf-8").read()          # text mode(Trialのrdtと同じ)
    storyline, facts = e2e.parse_brief_md(text)
    saved = fl.apply_factlock_patches()
    try:
        r0 = jaw.build_original_prompt(storyline, facts)
        findings = safety.detect_prohibited_symbols(SAMPLE_TEXT, language="ja")
        assert safety.symbol_gate_requires_stop(findings)
        regen = jaw.build_original_prompt(storyline, facts) + "\n\n" + safety.build_symbol_violation_prompt_note(findings)
    finally:
        fl.restore_factlock_patches(saved)
    return {"md_path": md_path.replace("\\", "/"), "md_sha256": sha(text), "storyline": storyline, "r0_prompt": r0,
            "r0_prompt_sha256": sha(r0), "regen_prompt": regen, "regen_prompt_sha256": sha(regen)}


def main():
    out = {"generated_for": "RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C1", "sample_text_for_regen": SAMPLE_TEXT,
           "annotation_final": {}, "new_arm_runs": {}}
    for s in SLUGS_FINAL:
        out["annotation_final"][s] = trial_prompts(f"{T}/annotation/final/{s}/selected_brief_factlock.md")
    for s in SLUGS_RUNS:
        out["new_arm_runs"][s] = trial_prompts(f"{T}/runs/{s}/new/storyline_b3/selected_brief.md")
    d = os.path.join(REPO, "er053_output", "risk_flagger_production_wiring_01", "golden")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "w1_golden_prompts_01.json")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("written", p, len(out["annotation_final"]), len(out["new_arm_runs"]))


if __name__ == "__main__":
    main()
