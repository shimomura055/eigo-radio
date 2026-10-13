# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 是正①のdry-run(API 0円)。
既存のINVALID job(Coffee Std a2、2 job x 内部2 attempt)の選定結果itemと、記録済みのLLM出力(各attempt parsed)を再利用し、
修正後のcanonicalization入力・Rule7判定がどう変わるかを示す。LLMは呼ばない。"""
import json
import er003_key_words_canonicalization as kc

BASE = "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_m2p0_n01_01/a2"
OUT = "er071_output/m2p0_n01_production_wiring_01/completion_01/fix1_dryrun_01.json"
res = {"purpose": "是正① dry-run(LLM呼出なし、記録済みLLM出力を修正後validatorへ再投入)", "jobs": []}
for sub in ("key_phrases_d02_attempt_invalid", "key_phrases"):
    sel = json.load(open(f"{BASE}/{sub}/key_phrases_db_hybrid/../keywords_runtime_metadata.json", encoding="utf-8"))
    items = sel["kp_backend_attempts_detail"][0]["parsed"]["items"]
    canon = json.load(open(f"{BASE}/{sub}/canonicalization_runtime_metadata.json", encoding="utf-8"))
    view = kc.canonicalization_view_items(items)
    job = {"job": sub, "recorded_final_status": canon["final_status"],
           "span_expansion": [{"rank": v["rank"], "display_phrase": v.get("display_phrase"),
                               "original_source_span": v.get("source_span_original", v.get("source_span")),
                               "canonicalization_source_span": v["source_span"]}
                              for v in view if "source_span_original" in v],
           "attempts": []}
    for a in canon["attempts_detail"]:
        before = {"status": a["status"], "item_reasons": a.get("item_reasons")}
        after = kc.validate_canonicalization_response(a["parsed"], items)
        job["attempts"].append({"attempt": a["attempt"], "recorded": before,
                                "replayed_with_fix": {"status": after["status"], "item_reasons": after["item_reasons"],
                                                      "items_requiring_review": after["items_requiring_review"]}})
    res["jobs"].append(job)
res["note"] = ("LLMは呼んでいない。修正後は拡張span('based on interviews')が原文連続部分文字列のため、記録済みLLM出力"
               "('based on interviews')がRule7を満たす。ただし修正後入力でLLMが同じ出力を返すかは正式経路での再実行(委任_02)で確認する。")
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for j in res["jobs"]:
    print(j["job"], j["recorded_final_status"], [(a["attempt"], a["recorded"]["status"], "->", a["replayed_with_fix"]["status"]) for a in j["attempts"]], j["span_expansion"])
