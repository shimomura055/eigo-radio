# ============================================================
# er014_output/four_type_observation_01/discovery/run_discovery_audio_completion_3.py
# 管理ID: USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-DISCOVERY (Part 1: B1B短文化)
# ============================================================
# 目的: CONT1(run_discovery_audio_completion_2.py)がSTOPしたB1B
# full_story_part2の長文1文脱落問題に対し、ユーザー指定の短文化候補で
# canonical article本文(discovery/b1b/article.md、
# discovery/reader_facing_article_b1b.txt)を変更し、既存正式QA
# (Fact Checker A' + Ledger Deviation Checker = 既存の差分QA関数
# er010_ledger_local_rewrite_09.apply_diff_qa_to_resolved_rewrite、
# + Directional Fact Precheck)を通したうえで、既存Production関数
# (news_tail_fix.generate_news_narration_wide_margin、無変更)で
# full_story_part2のみ再生成し、Assembly以降(既存関数、無変更)まで
# 完走させる。approve_regenerate()は呼ばない(新canonical_textによる
# 新規lockバージョンとして通常のAUTO_PROCESSING経路で進む、CONT1と
# 同じ設計)。
#
# 対象文の変更(意味不変の短文化、ユーザー指定候補):
#   旧: "In a study of 2,557 college students at 12 sites in 11 countries,
#        an everyday activity was enjoyed more than thinking for pleasure
#        in every country tested."
#   新: "In a study of about 2,500 college students in 11 countries, an
#        everyday activity was enjoyed more than thinking for pleasure in
#        every country tested."
# (後半「an everyday activity...in every country tested.」は不変。
#  2,557→about 2,500は丸め、「at 12 sites」の省略は情報の削減であり
#  Ledger F007との矛盾ではない。詳細はb1b/audit/fix02_ledger_
#  consistency_check.jsonへ記録する。)
#
# まだTTSが読み飛ばす場合のみ、意味を変えず2文へ分割する第2候補
# (SENTENCE FIX 2)を用意し、(2)(3)(4)を再実行する(Fact Checker等の
# QA再実行込み)。それでも読み飛ばす場合はSTOP(それ以上の構造変更禁止、
# segment分割等は行わない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er014_output/four_type_observation_01/discovery/run_discovery_audio_completion_3.py --level b1b --sentence-fix
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
_THIS_DIR = os.path.dirname(__file__)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import er003_v1_n3_01_tts_generate as tts_gen  # noqa: E402
import er003_v1_sing01_news_tail_fix as news_tail_fix  # noqa: E402
import er005_cost_logger as cl  # noqa: E402
import run_discovery_audio_completion as base  # noqa: E402  (既存driver、TTS/Assembly/Gate/Web、無変更で再利用)
import run_discovery_complete_2 as qa2  # noqa: E402  (既存driver、正式QA[Fact Checker A'/Ledger Deviation/diff QA]の
                                          # 呼び出し関数・client・routing・THEME_ID・TOPIC_EN・RESEARCH_DIRを再利用)

TASK_ID = "USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-DISCOVERY"
PART1_BUDGET_JPY = 90.0

DISCOVERY_DIR = qa2.BASE_DIR  # "er014_output/four_type_observation_01/discovery"
B1B_CANON_DIR = f"{DISCOVERY_DIR}/b1b"
B1B_BEFORE_FIX02_DIR = f"{DISCOVERY_DIR}/b1b_before_fix02"
READER_FACING_B1B_PATH = f"{DISCOVERY_DIR}/reader_facing_article_b1b.txt"

B1B_AUDIO_DIR = f"{base.OUT_DIR}/b1b"
NARRATION_DIR = f"{B1B_AUDIO_DIR}/narration"
WAV_PATH = f"{NARRATION_DIR}/full_story_part2.wav"
RESULTS_PATH = f"{B1B_AUDIO_DIR}/audit/tts_generation_results.json"
SUMMARY_PATH = f"{B1B_AUDIO_DIR}/run_summary_tts.json"
TRANSFORMS_PATH = f"{base.OUT_DIR}/tts_reading_transforms.json"
PARTS_PATH = f"{B1B_AUDIO_DIR}/parts.json"

STAGE_ESTIMATE_JPY = {
    "diffqa": 20.0,
    "directional": 6.0,
    "tts": 20.0,
}

OLD_SENTENCE = (
    "In a study of 2,557 college students at 12 sites in 11 countries, an everyday activity was "
    "enjoyed more than thinking for pleasure in every country tested."
)
NEW_SENTENCE_1 = (
    "In a study of about 2,500 college students in 11 countries, an everyday activity was enjoyed "
    "more than thinking for pleasure in every country tested."
)
NEW_SENTENCE_2SPLIT = (
    "In a study of about 2,500 college students in 11 countries, an everyday activity was enjoyed "
    "more than thinking for pleasure. This was true in every country tested."
)

SENTENCE_FIX_NOTE = (
    "USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-DISCOVERY: ユーザー指定の短文化候補。Ledger F007の実測値"
    "(N=2,557; 12 sites; 11 countries)を、精度自体に意味がないため丸め・簡略化する(Spoken-first "
    "Number Treatment原則、CURRENT_SPEC.md該当節と同種)。'about 2,500'は2,557の概数化(丸め)、"
    "'at 12 sites'の省略は情報の削減であり、Ledgerとの矛盾ではない(サイト数を偽らない、単に言及しない"
    "だけ)。'in 11 countries'・'an everyday activity was enjoyed more than thinking for pleasure in "
    "every country tested'は不変。CONT1(数字読み整形のみ)で3attempt中3回この文が音声から脱落した"
    "ため、文自体を短くしてTTSの安定性を改善することを試みる。"
)


# ============================================================
# Step 0: Ledger整合確認(決定的、API不使用)
# ============================================================
def build_ledger_consistency_check() -> dict:
    with open(f"{qa2.RESEARCH_DIR}/verified_fact_ledger.txt", encoding="utf-8") as f:
        ledger_text = f.read()
    f007_lines = []
    capture = False
    for line in ledger_text.splitlines():
        if line.startswith("[VERIFIED] F007:"):
            capture = True
        elif capture and line.startswith("[VERIFIED] F0"):
            break
        if capture:
            f007_lines.append(line)
    f007_block = "\n".join(f007_lines)
    result = {
        "task_id": TASK_ID,
        "fact_id": "F007",
        "ledger_f007_block": f007_block,
        "old_sentence": OLD_SENTENCE,
        "new_sentence_candidate_1": NEW_SENTENCE_1,
        "new_sentence_candidate_2_split": NEW_SENTENCE_2SPLIT,
        "assessment": (
            "Ledger F007の実測値はN=2,557participants(college students); 12 sites; 11 countries。"
            "候補文は'about 2,500'(2,557の概数化、丸め)・'in 11 countries'(Ledgerと完全一致)を使い、"
            "'at 12 sites'を省略する。数の丸めはSpoken-first Number Treatment原則(精度自体に意味が"
            "ない数字は丸め・概数化してよい)と整合し、サイト数の省略は新しい主張の追加ではなく既存"
            "情報の一部を述べないだけであり、Ledgerとの矛盾(scope expansion/causal strengthening/"
            "invented connection等)には該当しない。「an everyday activity was enjoyed more than "
            "thinking for pleasure in every country tested」の部分はLedgerの結論(every country "
            "sampledで一貫)と一致し不変。"
        ),
        "verified_at": datetime.now(timezone.utc).isoformat(),
    }
    return result


# ============================================================
# Step 1: canonical article退避
# ============================================================
def backup_before_fix02() -> None:
    os.makedirs(B1B_BEFORE_FIX02_DIR, exist_ok=True)
    if os.path.isdir(B1B_CANON_DIR) and not os.path.isdir(f"{B1B_BEFORE_FIX02_DIR}/b1b"):
        shutil.copytree(B1B_CANON_DIR, f"{B1B_BEFORE_FIX02_DIR}/b1b")
    if os.path.exists(READER_FACING_B1B_PATH) and not os.path.exists(
            f"{B1B_BEFORE_FIX02_DIR}/reader_facing_article_b1b.txt"):
        shutil.copy2(READER_FACING_B1B_PATH, f"{B1B_BEFORE_FIX02_DIR}/reader_facing_article_b1b.txt")
    print(f"[FIX02] canonical article退避完了: {B1B_BEFORE_FIX02_DIR}")


# ============================================================
# Step 2: 正式QA(Fact Checker A' + Ledger Deviation Checker = 既存
# diff QA関数apply_diff_qa_to_resolved_rewrite、+ Directional Fact
# Precheck)を1文の差替えへ適用する。
# ============================================================
def run_sentence_fix_qa(article_text_old: str, old_sentence: str, new_sentence: str, label: str,
                          client, ledger_model_b1b: str, fact_checker_model: str,
                          verified_ledger_text: str) -> dict:
    assert article_text_old.count(old_sentence) == 1, (
        f"[{label}] 置換対象文字列の出現回数が1ではありません: {old_sentence!r}")
    block = qa2.base.find_block_by_substring(article_text_old, old_sentence)
    if block is None:
        raise RuntimeError(f"[{label}] 対象文が見つかりません: {old_sentence!r}")

    rewrite_result = qa2.build_operator_rewrite_result(old_sentence, new_sentence, "F007", SENTENCE_FIX_NOTE)
    with qa2.prev_driver.cl.logging_context(qa2.THEME_ID, f"b1b_{label}_diffqa"):
        rewrite_result = qa2.prev_driver.local_rewrite.apply_diff_qa_to_resolved_rewrite(
            rewrite_result, client, qa2.TOPIC_EN, block["before"], block["after"],
            verified_ledger_text, ledger_model_b1b, fact_checker_model)
    os.makedirs(f"{B1B_CANON_DIR}/audit", exist_ok=True)
    with open(f"{B1B_CANON_DIR}/audit/fix02_{label}_diffqa.json", "w", encoding="utf-8") as f:
        json.dump(rewrite_result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[FIX02][{label}] diff QA(Fact Checker A'+Ledger Deviation Checker): "
          f"resolved={rewrite_result['resolved']} human_review_required={rewrite_result['human_review_required']} "
          f"blocks_acceptance={rewrite_result['diff_qa'].get('blocks_acceptance')} "
          f"fact_check_verdict={rewrite_result['diff_qa'].get('fact_check_verdict')}")

    if rewrite_result["human_review_required"]:
        return {"ok": False, "stage": "diffqa", "diff_qa": rewrite_result,
                "reason": "diff QA(Fact Checker A'/Ledger Deviation Checker)がblocks_acceptance=Trueと判定"}

    new_article_text = qa2.prev_driver.local_rewrite.apply_rewrites(article_text_old, [rewrite_result])
    new_article_text = qa2.prev_driver.artgen.normalize_article_formatting(new_article_text)

    vfl_path = f"{qa2.RESEARCH_DIR}/stage_b3_vfl.json"
    with qa2.prev_driver.cl.logging_context(qa2.THEME_ID, f"b1b_{label}_directional"):
        directional_result = qa2.prev_driver.dfp.audit_article_directional_facts(
            new_article_text, verified_ledger_text, vfl_path=vfl_path)
    with open(f"{B1B_CANON_DIR}/audit/fix02_{label}_directional.json", "w", encoding="utf-8") as f:
        json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[FIX02][{label}] Directional Fact Precheck(non-blocking): "
          f"overall_status={directional_result['overall_status']}")

    return {"ok": True, "new_article_text": new_article_text, "diff_qa": rewrite_result,
            "directional": directional_result}


# ============================================================
# Step 3: canonical article/reader-facing/audio側article.md/parts.jsonを
# 新テキストへ反映する。
# ============================================================
def commit_new_article_text(new_article_text: str) -> dict:
    with open(f"{B1B_CANON_DIR}/article.md", "w", encoding="utf-8") as f:
        f.write(new_article_text)
    with open(READER_FACING_B1B_PATH, "w", encoding="utf-8") as f:
        f.write(new_article_text)

    # audio/b1b/article.mdへ反映(既存base.prepare_article、sha256一致検証込み)
    refreshed_text = base.prepare_article("b1b")
    assert refreshed_text == new_article_text, "[FIX02] audio側article.mdの反映内容が不一致です。STOP。"

    import er003_v1_n3_01_scaffold_generate as sc
    new_parts = sc.split_article_text(new_article_text)
    old_parts = base.load_json(PARTS_PATH)
    changed_keys = [k for k in old_parts if old_parts.get(k) != new_parts.get(k)]
    print(f"[FIX02] parts.json再計算: 変更キー={changed_keys}(part2以外が変化した場合は要確認)")
    base.save_json(PARTS_PATH, new_parts)
    return {"new_parts": new_parts, "changed_keys": changed_keys}


# ============================================================
# Step 4: 読み整形一覧の更新(part2内の他3件の数字読み整形はCONT1のまま
# 維持、旧'2,557...'transformを新文の数字読み整形へ差し替える)。
# ============================================================
def build_reading_transforms(new_part2_text: str, label: str) -> list:
    if "This was true in every country tested." in new_part2_text:
        # 2文分割版: 前半のみ数字読み整形の対象。
        number_original = (
            "In a study of about 2,500 college students in 11 countries, an everyday activity was "
            "enjoyed more than thinking for pleasure.")
        number_transformed = (
            "In a study of about two thousand five hundred college students in eleven countries, an "
            "everyday activity was enjoyed more than thinking for pleasure.")
    else:
        number_original = NEW_SENTENCE_1
        number_transformed = (
            "In a study of about two thousand five hundred college students in eleven countries, an "
            "everyday activity was enjoyed more than thinking for pleasure in every country tested.")

    transforms = [
        {
            "original": "roughly 46 students",
            "transformed": "roughly forty-six students",
            "reason": "CONT1から継続(桁の多い算用数字の誤読対策、意味不変)。",
        },
        {
            "original": "six minutes and 30 seconds",
            "transformed": "six minutes and thirty seconds",
            "reason": "CONT1から継続。",
        },
        {
            "original": "A review of 37 studies",
            "transformed": "A review of thirty-seven studies",
            "reason": "CONT1から継続。",
        },
        {
            "original": number_original,
            "transformed": number_transformed,
            "reason": (f"[{TASK_ID}] 旧'2,557college students at 12 sites in 11 countries'の読み整形を、"
                       f"短文化後の新文('about 2,500 college students in 11 countries')向けへ更新。"
                       f"'about 2,500'->'about two thousand five hundred'、'11 countries'->'eleven "
                       f"countries'(意味不変、桁の多い算用数字の読み整形)。"),
        },
    ]
    for t in transforms:
        assert new_part2_text.count(t["original"]) == 1, (
            f"[{label}] 読み整形対象文字列の出現回数が1ではありません: {t['original']!r}")
    return transforms


def apply_reading_transforms(text: str, transforms: list) -> str:
    out = text
    for t in transforms:
        out = out.replace(t["original"], t["transformed"], 1)
    return out


def reverse_reading_transforms(text: str, transforms: list) -> str:
    out = text
    for t in reversed(transforms):
        assert out.count(t["transformed"]) == 1, f"round-trip失敗: {t['transformed']!r}"
        out = out.replace(t["transformed"], t["original"], 1)
    return out


def build_and_save_transform_record(original_part2: str, transformed_part2: str, transforms: list,
                                     label: str) -> dict:
    reconstructed = reverse_reading_transforms(transformed_part2, transforms)
    round_trip_ok = (reconstructed == original_part2)
    record = {
        "task_id": TASK_ID, "level": "b1b", "segment": "full_story_part2", "label": label,
        "transforms": transforms,
        "original_text": original_part2, "transformed_text": transformed_part2,
        "round_trip_reconstructed_text_equals_original": round_trip_ok,
        "original_word_count": len(original_part2.split()),
        "transformed_word_count": len(transformed_part2.split()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    assert round_trip_ok, "round-trip検証NG: 置換以外の差異が発生しています。STOP。"
    base.save_json(TRANSFORMS_PATH, record)
    print(f"[FIX02][{label}] 読み整形記録: round_trip_ok={round_trip_ok} transforms={len(transforms)}件")
    return record


# ============================================================
# Step 5: full_story_part2のみTTS再生成(既存Production関数を無変更で
# 直接呼ぶ)。
# ============================================================
def regenerate_full_story_part2(new_part2_text: str, label: str) -> dict:
    transforms = build_reading_transforms(new_part2_text, label)
    transformed_part2 = apply_reading_transforms(new_part2_text, transforms)
    build_and_save_transform_record(new_part2_text, transformed_part2, transforms, label)

    tts_input = tts_gen.tts_safe_news_en(transformed_part2)
    print(f"[FIX02][{label}] full_story_part2 再生成(既存関数news_tail_fix."
          f"generate_news_narration_wide_margin、max_attempts=既定値のまま変更なし)...")
    with cl.logging_context(base.THEME_ID, "tts_b1b"):
        result = news_tail_fix.generate_news_narration_wide_margin(
            tts_input, WAV_PATH,
            disfluency_qa=False,
            enable_connected_speech_equivalence_layer=True,
            enable_repetition_qa=True,
        )
    result["canonical_text"] = new_part2_text
    result["reading_transform_applied"] = True
    result["reading_transform_record_path"] = TRANSFORMS_PATH
    result["fix02_label"] = label

    for a in (result.get("attempts_log") or []):
        asr_text = a.get("asr_text") or ""
        if asr_text:
            ratio = len(asr_text) / max(len(transformed_part2), 1)
            a["_diagnostic_asr_length_ratio_vs_transformed_input"] = round(ratio, 3)
            if ratio < 0.6:
                print(f"[DIAGNOSTIC][{label}][attempt={a.get('attempt')}] ASR文字数比率={ratio:.3f} "
                      f"(<0.6) — 文欠落の疑いあり")

    data = base.load_json(RESULTS_PATH)
    data["segments"]["full_story_part2"] = result
    base.save_json(RESULTS_PATH, data)
    summary = base.load_json(SUMMARY_PATH)
    summary["segment_status"]["full_story_part2"] = result.get("status")
    base.save_json(SUMMARY_PATH, summary)

    attempts = len(result.get("attempts_log") or [])
    print(f"[FIX02][{label}] full_story_part2 status={result.get('status')} attempts={attempts} "
          f"asr_verified={result.get('asr_verified')}")
    return result


# ============================================================
# Step 6: Assembly以降(既存driverの関数をそのまま再利用、CONT1と同一
# パターン)。
# ============================================================
def run_level_b1b_from_assembly() -> dict:
    assemble_result = base.run_assembly("b1b")
    if assemble_result.get("gate_off_result") != "PASS":
        raise RuntimeError(f"[b1b] Assembly(Gate OFF経路)がPASSしませんでした、STOP: {assemble_result}")
    gate_on = base.run_gate_opt_in_check("b1b")
    consistency = base.build_consistency_check("b1b")
    web = base.build_player_and_web_delivery("b1b", assemble_result)
    return {
        "level": "b1b", "assemble_result": assemble_result, "gate_opt_in_result": gate_on,
        "consistency": consistency, "web": web,
        "cost_breakdown_jpy": base.cost_breakdown_by_stage(),
    }


def update_shared_outputs_success(level_result: dict, fix_label: str) -> None:
    cost_path = f"{base.OUT_DIR}/cost_summary_audio.json"
    cost_doc = base.load_json(cost_path)
    breakdown = level_result["cost_breakdown_jpy"]
    category_map = {"scaffold": "preview_comment_llm_jpy", "keyphrase": "key_phrase_llm_jpy",
                     "tts": "tts_jpy", "assemble": "other_jpy"}
    cat_totals = {"preview_comment_llm_jpy": 0.0, "key_phrase_llm_jpy": 0.0, "tts_jpy": 0.0, "other_jpy": 0.0}
    b1b_stage_breakdown = {}
    for stage, jpy in breakdown.items():
        if not stage.startswith("b1b_") and not stage.endswith("_b1b"):
            continue
        b1b_stage_breakdown[stage] = jpy
        prefix = stage.rsplit("_", 1)[0] if stage.endswith("_b1b") else "other"
        cat = category_map.get(prefix, "other_jpy")
        cat_totals[cat] += jpy
    cat_totals = {k: round(v, 2) for k, v in cat_totals.items()}
    cat_totals["total_jpy"] = round(sum(v for k, v in cat_totals.items() if k != "raw_stage_breakdown_jpy"), 2)
    cat_totals["raw_stage_breakdown_jpy"] = {k: round(v, 4) for k, v in b1b_stage_breakdown.items()}
    old_b1b_total = cost_doc["levels"].get("b1b", {}).get("total_jpy", 0.0)
    cost_doc["levels"]["b1b"] = cat_totals
    cost_doc["combined_total_jpy"] = round(sum(v["total_jpy"] for v in cost_doc["levels"].values()), 2)
    cost_doc["note"] = (cost_doc.get("note", "") +
                         f" [{TASK_ID}] 短文化({fix_label})+full_story_part2再生成によりb1bが完成した。"
                         f"b1b合計コストは¥{old_b1b_total:.2f}(CONT1までの実費)から"
                         f"¥{cat_totals['total_jpy']:.2f}へ更新(差分¥{cat_totals['total_jpy'] - old_b1b_total:.2f}"
                         f"が本タスクの追加実費)。")
    cost_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    base.save_json(cost_path, cost_doc)

    wd_path = f"{base.OUT_DIR}/web_delivery.json"
    wd_doc = base.load_json(wd_path)
    manifest = level_result["web"]["mp3_manifest"]
    over_50mb = [m for m in manifest if m["size_mb"] >= 50.0]
    wd_doc["levels"]["b1b"] = {
        "player_path": level_result["web"]["player_path"].replace("\\", "/"),
        "mp3_files": manifest, "all_under_50mb": len(over_50mb) == 0,
    }
    wd_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    base.save_json(wd_path, wd_doc)

    ps_path = f"{DISCOVERY_DIR}/production_set_cost.json"
    ps_doc = base.load_json(ps_path)
    a2_total = cost_doc["levels"]["a2"]["total_jpy"]
    b1b_total = cost_doc["levels"]["b1b"]["total_jpy"]
    audio_total_all_levels = round(a2_total + b1b_total, 2)
    this_task_incremental_jpy = round(b1b_total - old_b1b_total, 2)
    ps_doc["audio_completion_cost_jpy"] = audio_total_all_levels
    ps_doc["audio_completion_cost_by_level_jpy"] = {"a2": a2_total, "b1b": b1b_total}
    ps_doc["production_set_total_cost_including_audio_jpy"] = round(
        ps_doc.get("grand_total_jpy_including_key_phrase", 463.27) + audio_total_all_levels, 2)
    ps_doc["audio_completion_note"] = (
        ps_doc.get("audio_completion_note", "") +
        f" [{TASK_ID}] full_story_part2の短文化({fix_label}、ユーザー指定候補、Ledger F007整合確認済み、"
        f"discovery/b1b/audit/fix02_{fix_label}_diffqa.json+fix02_{fix_label}_directional.json)+既存"
        f"Production経路(news_tail_fix.generate_news_narration_wide_margin、無変更)での再生成により、"
        f"B1Bが完成しAssembly/Gate/Web playerまで到達した。approve_regenerate()は呼んでいない。"
        f"本タスクの追加実費=¥{this_task_incremental_jpy:.2f}。")
    ps_doc["b1b_audio_completion_status"] = (
        f"COMPLETE(gate_off=PASS, full_story_part2は短文化後テキストでの再生成でASR verified、"
        f"fix_label={fix_label}, {TASK_ID})")
    ps_doc["this_task_fix02_incremental_audio_cost_jpy"] = this_task_incremental_jpy
    base.save_json(ps_path, ps_doc)
    print(f"[COST] b1b合計={b1b_total:.2f} JPY (旧{old_b1b_total:.2f} JPY からの追加=¥{this_task_incremental_jpy:.2f})")


def append_cross_level_consistency_note() -> None:
    path = f"{DISCOVERY_DIR}/cross_level_consistency.md"
    note = (
        f"\n## {TASK_ID} B1B短文化とA2のCross-Level Consistency\n\n"
        "B1Bのfull_story_part2該当文は短文化後「In a study of about 2,500 college students in 11 "
        "countries, an everyday activity was enjoyed more than thinking for pleasure in every country "
        "tested.」へ変更した。A2側は「In a study of 2,557 college students at 12 sites in 11 countries, "
        "an everyday activity was more enjoyable than thinking for pleasure in every country tested.」の"
        "ままで本タスクでは変更していない。両者の差(2,557 vs about 2,500、12 sites の有無)はLevel間の"
        "解像度差(A2はより正確な数値+siteを保持、B1BはTTS安定性のため丸め、CEFR-A2/B1レベル別の数値"
        "精度運用は既存のSpoken-first Number Treatment原則の範囲内)であり、矛盾ではない。\n"
    )
    with open(path, "a", encoding="utf-8") as f:
        f.write(note)
    print(f"[FIX02] cross_level_consistency.md 追記完了: {path}")


def append_progress_log(level_result: dict, fix_label: str) -> None:
    log_path = f"{DISCOVERY_DIR}/progress_log.md"
    now = datetime.now(timezone.utc).isoformat()
    duration = level_result["assemble_result"].get("duration_seconds")
    gate_on = level_result["gate_opt_in_result"].get("gate_on_result")
    all_pass = level_result["consistency"].get("all_pass")
    line = (f"- Discovery audio completion (b1b, FIX-02 sentence fix={fix_label}): {now} 完了, "
            f"gate_off=PASS, gate_on={gate_on}, duration={duration}s, "
            f"article_audio_consistency_all_pass={all_pass} (管理ID: {TASK_ID})\n")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)


def try_one_sentence_fix(article_text_old: str, old_sentence: str, new_sentence: str, label: str,
                          client, ledger_model_b1b: str, fact_checker_model: str,
                          verified_ledger_text: str) -> dict:
    qa_result = run_sentence_fix_qa(article_text_old, old_sentence, new_sentence, label,
                                     client, ledger_model_b1b, fact_checker_model, verified_ledger_text)
    if not qa_result["ok"]:
        return {"ok": False, "stage": "qa", "label": label, "detail": qa_result}

    commit_result = commit_new_article_text(qa_result["new_article_text"])
    parts = commit_result["new_parts"]
    part2_result = regenerate_full_story_part2(parts["part2"], label)
    if part2_result.get("status") != "OK" or not part2_result.get("asr_verified"):
        return {"ok": False, "stage": "tts", "label": label, "part2_result": part2_result}
    return {"ok": True, "label": label, "part2_result": part2_result, "qa_result": qa_result,
            "commit_result": commit_result}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["b1b"], required=True)
    parser.add_argument("--sentence-fix", action="store_true")
    args = parser.parse_args()

    cl.install(base.LOG_PATH)
    baseline_cost = base.cost_so_far_jpy()
    print(f"[FIX02][BUDGET] task開始前の全累積コスト(audio_completion log)={baseline_cost:.2f} JPY "
          f"(task budget=¥{PART1_BUDGET_JPY} JPYはこのdriverが新規発生させる分のみに適用)")

    backup_before_fix02()
    ledger_check = build_ledger_consistency_check()
    os.makedirs(f"{B1B_CANON_DIR}/audit", exist_ok=True)
    with open(f"{B1B_CANON_DIR}/audit/fix02_ledger_consistency_check.json", "w", encoding="utf-8") as f:
        json.dump(ledger_check, f, ensure_ascii=False, indent=2, default=str)
    print(f"[FIX02] Ledger整合確認完了(API不使用): {B1B_CANON_DIR}/audit/fix02_ledger_consistency_check.json")

    with open(f"{qa2.RESEARCH_DIR}/verified_fact_ledger.txt", encoding="utf-8") as f:
        verified_ledger_text = f.read()

    client = qa2.prev_driver.vfl01.get_client()
    ledger_model_b1b = qa2.prev_driver.routing.require_model("B1_WRITER", qa2.prev_driver.routing.WRITER_MODEL)
    fact_checker_model = qa2.prev_driver.routing.require_model(
        "WRITER_FACT_CHECK", qa2.prev_driver.routing.WRITER_FACT_CHECK_MODEL)

    with open(f"{B1B_CANON_DIR}/article.md", encoding="utf-8") as f:
        article_text_original = f.read()

    rewrite_log_lines = [f"\n# {TASK_ID}(B1B短文化、Part 1)\n"]

    attempt1 = try_one_sentence_fix(
        article_text_original, OLD_SENTENCE, NEW_SENTENCE_1, "fix02_1sentence",
        client, ledger_model_b1b, fact_checker_model, verified_ledger_text)

    rewrite_log_lines.append("## Attempt 1(1文短文化)\n")
    rewrite_log_lines.append(f"  旧: {OLD_SENTENCE}\n")
    rewrite_log_lines.append(f"  新: {NEW_SENTENCE_1}\n")
    rewrite_log_lines.append(f"  結果: ok={attempt1['ok']} stage={attempt1.get('stage')}\n\n")

    final_attempt = attempt1
    if not attempt1["ok"] and attempt1.get("stage") == "tts":
        print("===== [FIX02] Attempt 1(1文短文化)でもTTSが読み飛ばしを解消できず、"
              "2文分割(Attempt 2)を試みます =====")
        attempt2 = try_one_sentence_fix(
            article_text_original, OLD_SENTENCE, NEW_SENTENCE_2SPLIT, "fix02_2split",
            client, ledger_model_b1b, fact_checker_model, verified_ledger_text)
        rewrite_log_lines.append("## Attempt 2(2文分割、意味不変)\n")
        rewrite_log_lines.append(f"  旧: {OLD_SENTENCE}\n")
        rewrite_log_lines.append(f"  新: {NEW_SENTENCE_2SPLIT}\n")
        rewrite_log_lines.append(f"  結果: ok={attempt2['ok']} stage={attempt2.get('stage')}\n\n")
        final_attempt = attempt2

    with open(f"{DISCOVERY_DIR}/rewrite_log.md", "a", encoding="utf-8") as f:
        f.writelines(rewrite_log_lines)

    if not final_attempt["ok"]:
        base.save_json(f"{B1B_AUDIO_DIR}/run_result_fix02.json", {
            "level": "b1b", "status": "STOPPED", "task_id": TASK_ID,
            "attempt1": {"ok": attempt1["ok"], "stage": attempt1.get("stage")},
            "attempt2_attempted": not attempt1["ok"] and attempt1.get("stage") == "tts",
            "final_attempt_label": final_attempt.get("label"),
            "final_attempt_stage": final_attempt.get("stage"),
            "reason": "既存上限までに読み飛ばしを解消できなかった、またはQAでblocks_acceptance=Trueと判定された。"
                      "それ以上の構造変更(segment分割等)は行わずSTOPします。USER_DECISION_REQUIRED。",
        })
        print(f"===== [FIX02][b1b] STOP: {final_attempt.get('stage')}段階で完了できませんでした =====")
        return

    level_result = run_level_b1b_from_assembly()
    update_shared_outputs_success(level_result, final_attempt["label"])
    append_cross_level_consistency_note()
    append_progress_log(level_result, final_attempt["label"])

    incremental = round(base.cost_so_far_jpy() - baseline_cost, 2)
    base.save_json(f"{B1B_AUDIO_DIR}/run_result_fix02.json", {
        "level": "b1b", "status": "COMPLETE", "task_id": TASK_ID,
        "final_attempt_label": final_attempt["label"],
        "gate_off_result": level_result["assemble_result"].get("gate_off_result"),
        "gate_on_result": level_result["gate_opt_in_result"].get("gate_on_result"),
        "duration_seconds": level_result["assemble_result"].get("duration_seconds"),
        "consistency_all_pass": level_result["consistency"].get("all_pass"),
        "cost_breakdown_jpy": level_result["cost_breakdown_jpy"],
        "this_task_incremental_cost_jpy": incremental,
    })
    print(f"===== [FIX02][b1b] 完了(final_attempt_label={final_attempt['label']}, "
          f"this_task_incremental_cost_jpy=¥{incremental:.2f}, budget=¥{PART1_BUDGET_JPY}) =====")


if __name__ == "__main__":
    main()
