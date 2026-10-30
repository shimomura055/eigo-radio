# -*- coding: utf-8 -*-
"""FAMILY-X-SELECTED-4 委任_04 H2: er021 Å<->angstrom(s)等価の是正後、JWST Std/Adv full_story_part2_k3のHR Lock
(偽NG[ASR比較の仕様ギャップ]由来)を既存Production機構(er011 approve_regenerate -> REGENERATE_APPROVED)で解除する。
前例: er019_family_x_stage3e_human_review_lock_approve_01.py(根本原因修正済みsegmentに限る)。新Gate/閾値なし。API 0。
approve_regenerateへ渡すtextは guarded関数が受け取る tts_safe_news_en(canonical_text) と同一(sha一致を事前assert)。"""
import json, sys
import er003_v1_n3_01_tts_generate as tg
import er011_human_review_lock_01 as rl
R = "er019_output/family_x_audio_production_wiring_01/jwst_mystery_emission_line__run_fx4_01"
for lv in ("a2", "b1b"):
    res = json.load(open(f"{R}/{lv}/audit/tts_generation_results.json", encoding="utf-8"))["segments"]["full_story_part2_k3"]
    lock = json.load(open(f"{R}/{lv}/audit/review_lock_state.json", encoding="utf-8"))["full_story_part2_k3"]
    text = tg.tts_safe_news_en(res["canonical_text"])
    assert rl._text_hash(text) == lock["canonical_text_sha256"], lv
    assert lock["state"] == "HUMAN_REVIEW_REQUIRED", (lv, lock["state"])
    if "--apply" in sys.argv:
        r = rl.approve_regenerate(f"{R}/{lv}/narration/full_story_part2_k3.wav", text, approved_by="FAMILY-X-SELECTED-4_delegation04_H2_fix_11-8")
        print(lv, "->", r["state"])
    else:
        print(lv, "dry-run ok sha match")
