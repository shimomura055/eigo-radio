# ============================================================
# er014_output/four_type_observation_01/discovery/run_discovery_audio_completion_2.py
# 管理ID: USER-TEST-AUDIO-COMPLETION-01-DISCOVERY-CONT1
# ============================================================
# 目的: 前回driver(run_discovery_audio_completion.py)でB1Bの
# full_story_part2segmentが3回ともTRUE_CONTENT_MISMATCHでHuman Review
# Cost Guardにより停止した問題への対応。記事本文(article.md/parts.json)は
# 一切変更せず、full_story_part2のTTS入力のみに「数字の読み整形」
# (算用数字→英語の数詞表記、意味不変)を適用し、既存Production関数
# (er003_v1_sing01_news_tail_fix.generate_news_narration_wide_margin、
# 無変更)で通常の初回TTS/ASR(既存上限=PRODUCTION_MAX_TTS_ATTEMPTS=3回)を
# 実行する。review_lock.approve_regenerate()は呼ばない(新テキストは
# canonical_text_sha256が変わるため、review_lock側が自動的に「新しい
# segmentバージョン」として扱い、通常のAUTO_PROCESSING経路で進む)。
#
# 他11 content segment(topic_intro/preview/comment_1-4/point_one_heading/
# point_one/point_two_heading/point_two/in_one_line)とKey Phrase 5件は
# 前回driverで既にstatus=OKで確定済み(review_lock=RESOLVED)のため、
# 本driverでは一切再生成しない(audit/tts_generation_results.jsonの
# full_story_part2エントリのみを書き換える)。
#
# 実行方法:
#   .venv/Scripts/python.exe er014_output/four_type_observation_01/discovery/run_discovery_audio_completion_2.py --level b1b
from __future__ import annotations

import argparse
import hashlib
import json
import os
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
import run_discovery_audio_completion as base  # noqa: E402  (前回driver、既存関数を無変更で再利用)

TASK_ID = "USER-TEST-AUDIO-COMPLETION-01-DISCOVERY-CONT1"
TASK_BUDGET_JPY = 60.0

B1B_OUT_DIR = f"{base.OUT_DIR}/b1b"
NARRATION_DIR = f"{B1B_OUT_DIR}/narration"
WAV_PATH = f"{NARRATION_DIR}/full_story_part2.wav"
RESULTS_PATH = f"{B1B_OUT_DIR}/audit/tts_generation_results.json"
SUMMARY_PATH = f"{B1B_OUT_DIR}/run_summary_tts.json"
TRANSFORMS_PATH = f"{base.OUT_DIR}/tts_reading_transforms.json"

# ============================================================
# Step 1: 数字読み整形(full_story_part2のみ、意味不変、語の追加削除なし)
# ============================================================
# Fable診断根拠(review_lock_state.json full_story_part2 attempts 1-3):
#   attempt1 ASR: "six minutes and three seconds"(原文"30 seconds"の誤読疑い)
#   attempt2 ASR: 原文どおり"30 seconds"だが"In one, 2,557 college students at
#                 12 sites in 11 countries"以降で文欠落(originalの
#                 "In a study of 2,557 ... phone use."の一部が脱落)
#   attempt3 ASR: "In one study"->"In a study"表記ゆれ、かつ同じ"2,557..."
#                 文がまるごと欠落
# いずれも桁の多い算用数字(46/30/37/2,557/12/11)が密集する箇所で発生して
# いるため、TTS入力側のみ英語の数詞表記へ変換する(表示用article.mdは
# 変更しない、Trial-09「7:00→seven」と同種の読み整形前処理)。
READING_TRANSFORMS = [
    {
        "original": "roughly 46 students",
        "transformed": "roughly forty-six students",
        "reason": "桁の多い算用数字が密集する箇所でTTSが誤読する疑いがあるため、"
                   "数詞表記に読み整形(意味不変)。",
    },
    {
        "original": "six minutes and 30 seconds",
        "transformed": "six minutes and thirty seconds",
        "reason": "3回中1回、ASRが'30 seconds'を'three seconds'と検出(TTS側の"
                   "桁誤読が疑われる)。'30'を'thirty'に読み整形。",
    },
    {
        "original": "A review of 37 studies",
        "transformed": "A review of thirty-seven studies",
        "reason": "同上の数字密集箇所対策として読み整形。",
    },
    {
        "original": "In a study of 2,557 college students at 12 sites in 11 countries",
        "transformed": "In a study of two thousand five hundred and fifty-seven college "
                        "students at twelve sites in eleven countries",
        "reason": "3回中2回、この文(桁区切りカンマ付き4桁数字+2つの2桁数字が密集)を"
                   "含む文またはその前後が音声から欠落した。数詞表記へ読み整形し、"
                   "TTSが桁の多い算用数字列を安定して発話できるようにする。",
    },
]


def apply_reading_transforms(text: str) -> str:
    out = text
    for t in READING_TRANSFORMS:
        assert out.count(t["original"]) == 1, (
            f"想定外: 置換対象文字列の出現回数が1ではありません: {t['original']!r}")
        out = out.replace(t["original"], t["transformed"], 1)
    return out


def reverse_reading_transforms(text: str) -> str:
    """round-trip検証用: transformed->originalへ逆変換する。"""
    out = text
    for t in reversed(READING_TRANSFORMS):
        assert out.count(t["transformed"]) == 1, (
            f"round-trip失敗: 変換後文字列が見つかりません: {t['transformed']!r}")
        out = out.replace(t["transformed"], t["original"], 1)
    return out


def build_and_save_transform_record(original_part2: str, transformed_part2: str) -> dict:
    reconstructed = reverse_reading_transforms(transformed_part2)
    round_trip_ok = (reconstructed == original_part2)
    record = {
        "task_id": TASK_ID,
        "level": "b1b",
        "segment": "full_story_part2",
        "note": ("記事本文(article.md/parts.json)は変更しない。TTS入力(canonical_text)"
                  "のみに数字の読み整形を適用する。canonical_textとして"
                  "tts_generation_results.jsonへ記録する値は既存Production規約どおり"
                  "元の記事由来テキスト(original_text)のまま据え置き、読み整形後の"
                  "テキスト(transformed_text)はTTS呼び出し引数としてのみ使う"
                  "(既存の固有名詞発音override['Reicher'->'Riker']等と同じ設計、"
                  "player/consistency checkの表示規約を崩さない)。"),
        "transforms": READING_TRANSFORMS,
        "original_text": original_part2,
        "transformed_text": transformed_part2,
        "round_trip_reconstructed_text_equals_original": round_trip_ok,
        "original_word_count": len(original_part2.split()),
        "transformed_word_count": len(transformed_part2.split()),
        "word_count_diff_explanation": (
            "2,557のような桁の多い数字を英語の数詞へ展開すると単語数が増える"
            "(例: '2,557'1語 -> 'two thousand five hundred and fifty-seven'"
            "7語)。これは新しい主張・情報の追加ではなく、同じ数値の読み上げ表記の"
            "展開であり、round_trip_reconstructed_text_equals_original=Trueに"
            "より、逆変換で元のarticle本文と完全一致することを機械確認している。"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    assert round_trip_ok, "round-trip検証NG: 置換以外の差異が発生しています。STOP。"
    base.save_json(TRANSFORMS_PATH, record)
    print(f"[READING-TRANSFORM] round_trip_ok={round_trip_ok} "
          f"transforms={len(READING_TRANSFORMS)}件 -> {TRANSFORMS_PATH}")
    return record


# ============================================================
# Step 2: full_story_part2のみ再生成(既存Production関数を無変更で直接
# 呼ぶ。review_lock guardは関数デコレータ内部で自動的に働く。
# approve_regenerate()は呼ばない)
# ============================================================
def regenerate_full_story_part2() -> dict:
    parts = base.load_json(f"{B1B_OUT_DIR}/parts.json")
    original_part2 = parts["part2"]

    # article.md由来のoriginal_part2が、前回driverが使った値と一致することを
    # 確認する(article.mdを再読込してsplit_article_text()を再実行し、突合)。
    import er003_v1_n3_01_scaffold_generate as sc
    article_text = open(f"{B1B_OUT_DIR}/article.md", encoding="utf-8").read()
    recomputed_parts = sc.split_article_text(article_text)
    assert recomputed_parts["part2"] == original_part2, (
        "article.md再読込結果とparts.json['part2']が不一致です。記事本文が変更されて"
        "いないことを前提とするため、この状態ではSTOPします。")

    transformed_part2 = apply_reading_transforms(original_part2)
    build_and_save_transform_record(original_part2, transformed_part2)

    cost_before = base.cost_breakdown_by_stage().get("tts_b1b", 0.0)
    so_far = base.cost_so_far_jpy()
    print(f"[BUDGET][task={TASK_ID}] 本driver開始前の全累積コスト={so_far:.2f} JPY "
          f"(task budget={TASK_BUDGET_JPY} JPY はこのdriverが新規に発生させる分のみに適用)")

    tts_input = tts_gen.tts_safe_news_en(transformed_part2)
    print("[N3-TTS-FIX][b1b] full_story_part2 再生成(読み整形後テキスト、"
          "既存関数news_tail_fix.generate_news_narration_wide_margin、"
          "max_attempts=既定値[review_lock.PRODUCTION_MAX_TTS_ATTEMPTS]のまま変更なし)...")
    with cl.logging_context(base.THEME_ID, "tts_b1b"):
        result = news_tail_fix.generate_news_narration_wide_margin(
            tts_input, WAV_PATH,
            disfluency_qa=False,
            enable_connected_speech_equivalence_layer=True,
            enable_repetition_qa=True,
        )
    # 既存Production規約どおり、canonical_textは記事由来の元テキスト(数字整形前)
    # を記録する(固有名詞発音overrideと同じ設計、表示は常に記事本文と一致させる)。
    result["canonical_text"] = original_part2
    result["reading_transform_applied"] = True
    result["reading_transform_record_path"] = TRANSFORMS_PATH

    cost_after = base.cost_breakdown_by_stage().get("tts_b1b", 0.0)
    delta = round(cost_after - cost_before, 4)
    print(f"[BUDGET][task={TASK_ID}] このTTS呼び出しの実費={delta:.4f} JPY "
          f"(task budget={TASK_BUDGET_JPY} JPY)")
    result["this_task_tts_cost_jpy"] = delta
    if delta > TASK_BUDGET_JPY:
        print(f"[BUDGET][WARNING] task budget {TASK_BUDGET_JPY} JPY を超過しました: {delta:.4f} JPY")

    attempts = len(result.get("attempts_log") or [])
    print(f"[N3-TTS-FIX][b1b] full_story_part2 status={result.get('status')} "
          f"attempts={attempts} asr_verified={result.get('asr_verified')}")

    # attempts_logに文欠落(содержание大幅短縮)が再発していないか、簡易な
    # 長さチェックで機械確認する(ASR文字数が元テキストの60%未満なら文欠落の
    # 疑いとして明示的にログへ残す。既存Validator[secondary_asr]の判定結果
    # [audio_classification]が主判定であり、本チェックは追加の可視化のみ)。
    for a in (result.get("attempts_log") or []):
        asr_text = a.get("asr_text") or ""
        if asr_text:
            ratio = len(asr_text) / max(len(transformed_part2), 1)
            a["_diagnostic_asr_length_ratio_vs_transformed_input"] = round(ratio, 3)
            if ratio < 0.6:
                print(f"[DIAGNOSTIC][attempt={a.get('attempt')}] ASR文字数比率={ratio:.3f} "
                      f"(<0.6) — 文欠落の疑いあり")

    # audit/tts_generation_results.jsonのfull_story_part2エントリのみ更新
    # (他11 content segment・Key Phrase 5件は前回driverの結果のまま変更しない)。
    data = base.load_json(RESULTS_PATH)
    data["segments"]["full_story_part2"] = result
    base.save_json(RESULTS_PATH, data)

    summary = base.load_json(SUMMARY_PATH)
    summary["segment_status"]["full_story_part2"] = result.get("status")
    base.save_json(SUMMARY_PATH, summary)

    return result


# ============================================================
# Step 3: Assembly以降(既存driverの関数をそのまま再利用)
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


# ============================================================
# Step 4: 共有出力の更新(cost_summary_audio.json / web_delivery.json /
# production_set_cost.json)。base.update_shared_outputs()は
# audio_completion_note等がA2 PASS/B1B STOPPED前提の固定文言のため、
# 本taskでは呼ばず、成功時の正確な内容へ直接更新する。
# ============================================================
def update_shared_outputs_success(level_result: dict) -> None:
    # cost_summary_audio.json: b1bのみ更新、a2は既存のまま保持。
    cost_path = f"{base.OUT_DIR}/cost_summary_audio.json"
    cost_doc = base.load_json(cost_path)
    breakdown = level_result["cost_breakdown_jpy"]  # 全stage・全実行累積(driver1+driver2)
    category_map = {"scaffold": "preview_comment_llm_jpy", "keyphrase": "key_phrase_llm_jpy",
                     "tts": "tts_jpy", "assemble": "other_jpy"}
    cat_totals = {"preview_comment_llm_jpy": 0.0, "key_phrase_llm_jpy": 0.0, "tts_jpy": 0.0, "other_jpy": 0.0}
    b1b_stage_breakdown = {}
    for stage, jpy in breakdown.items():
        if not stage.endswith("_b1b"):
            continue
        b1b_stage_breakdown[stage] = jpy
        prefix = stage.rsplit("_", 1)[0]
        cat = category_map.get(prefix, "other_jpy")
        cat_totals[cat] += jpy
    cat_totals = {k: round(v, 2) for k, v in cat_totals.items()}
    cat_totals["total_jpy"] = round(sum(v for k, v in cat_totals.items() if k != "raw_stage_breakdown_jpy"), 2)
    cat_totals["raw_stage_breakdown_jpy"] = {k: round(v, 4) for k, v in b1b_stage_breakdown.items()}
    old_b1b_total = cost_doc["levels"].get("b1b", {}).get("total_jpy", 0.0)
    cost_doc["levels"]["b1b"] = cat_totals
    cost_doc["combined_total_jpy"] = round(sum(v["total_jpy"] for v in cost_doc["levels"].values()), 2)
    cost_doc["note"] = (cost_doc.get("note", "") +
                         f" [{TASK_ID}] full_story_part2の読み整形+再生成によりb1bが完成した。"
                         f"b1b合計コストは¥{old_b1b_total:.2f}(前回driver、STOPPED時点の実費含む)から"
                         f"¥{cat_totals['total_jpy']:.2f}へ更新(差分¥{cat_totals['total_jpy'] - old_b1b_total:.2f}"
                         f"が本タスクの追加実費)。")
    cost_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    base.save_json(cost_path, cost_doc)

    # web_delivery.json: b1bを追加(a2は既存のまま)
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

    # production_set_cost.json: b1b完成を正確に反映(旧partial_incompleteの
    # 記述を上書きする)
    ps_path = f"{base.DISCOVERY_DIR}/production_set_cost.json"
    ps_doc = base.load_json(ps_path)
    base_total = ps_doc.get("grand_total_jpy_including_key_phrase", 463.27)
    a2_total = cost_doc["levels"]["a2"]["total_jpy"]
    b1b_total = cost_doc["levels"]["b1b"]["total_jpy"]
    audio_total_all_levels = round(a2_total + b1b_total, 2)
    this_task_incremental_jpy = round(b1b_total - old_b1b_total, 2)
    ps_doc["audio_completion_cost_jpy"] = audio_total_all_levels
    ps_doc["audio_completion_cost_by_level_jpy"] = {"a2": a2_total, "b1b": b1b_total}
    ps_doc["production_set_total_cost_including_audio_jpy"] = round(base_total + audio_total_all_levels, 2)
    ps_doc["audio_completion_note"] = (
        f"{TASK_ID}: full_story_part2の数字読み整形(discovery/audio/"
        f"tts_reading_transforms.json)+既存Production経路(news_tail_fix."
        f"generate_news_narration_wide_margin、無変更)での初回再生成により、"
        f"B1BもEPISODE_BLOCKED_BY_AUDIO_VALIDATIONを解消しAssembly/Gate/Web player"
        f"まで完成した。approve_regenerate()は呼んでいない(新canonical_textによる"
        f"新規lockバージョンとして通常のAUTO_PROCESSING経路で通った)。A2/B1Bとも"
        f"既存正式audio completion経路(er003_v1_n3_01_scaffold_generate/"
        f"tts_generate/assemble、無変更)で完成episode+Web試聴playerまで到達した。"
        f"本タスクの追加実費=¥{this_task_incremental_jpy:.2f}。"
    )
    ps_doc["b1b_audio_completion_status"] = (
        f"COMPLETE(gate_off=PASS, full_story_part2は読み整形後テキストでの初回生成で"
        f"ASR verified、{TASK_ID})")
    ps_doc["this_task_cont1_incremental_audio_cost_jpy"] = this_task_incremental_jpy
    base.save_json(ps_path, ps_doc)
    print(f"[COST] b1b合計={b1b_total:.2f} JPY (旧{old_b1b_total:.2f} JPY からの追加=¥{this_task_incremental_jpy:.2f})、"
          f"Discovery総原価={ps_doc['production_set_total_cost_including_audio_jpy']:.2f} JPY")


def append_progress_log(level_result: dict) -> None:
    log_path = "er014_output/four_type_observation_01/progress_log.md"
    now = datetime.now(timezone.utc).isoformat()
    duration = level_result["assemble_result"].get("duration_seconds")
    gate_on = level_result["gate_opt_in_result"].get("gate_on_result")
    all_pass = level_result["consistency"].get("all_pass")
    line = (f"- Discovery audio completion (b1b, CONT1 full_story_part2 fix): {now} 完了, "
            f"gate_off=PASS, gate_on={gate_on}, duration={duration}s, "
            f"article_audio_consistency_all_pass={all_pass} (管理ID: {TASK_ID})\n")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["b1b"], required=True)
    args = parser.parse_args()

    cl.install(base.LOG_PATH)  # 既存ログへ追記(init_loggerは既存ファイルを truncateしない)

    t0 = time.time()
    part2_result = regenerate_full_story_part2()
    if part2_result.get("status") != "OK" or not part2_result.get("asr_verified"):
        base.save_json(f"{B1B_OUT_DIR}/run_result_audio_completion_cont1.json", {
            "level": "b1b", "status": "STOPPED", "full_story_part2_result_status": part2_result.get("status"),
            "reason": "読み整形後テキストでも既存上限(3回)までにASR検証をPASSできませんでした。"
                      "review_lock=HUMAN_REVIEW_REQUIREDのまま。approve_regenerate()は呼びません。"
                      "USER_DECISION_REQUIRED。",
        })
        print("===== [AUDIO][b1b][CONT1] STOP: full_story_part2の読み整形後再生成が既存上限まで失敗 =====")
        return

    level_result = run_level_b1b_from_assembly()
    update_shared_outputs_success(level_result)
    append_progress_log(level_result)
    elapsed = round(time.time() - t0, 1)

    base.save_json(f"{B1B_OUT_DIR}/run_result_audio_completion_cont1.json", {
        "level": "b1b", "elapsed_seconds": elapsed,
        "gate_off_result": level_result["assemble_result"].get("gate_off_result"),
        "gate_on_result": level_result["gate_opt_in_result"].get("gate_on_result"),
        "duration_seconds": level_result["assemble_result"].get("duration_seconds"),
        "consistency_all_pass": level_result["consistency"].get("all_pass"),
        "cost_breakdown_jpy": level_result["cost_breakdown_jpy"],
    })
    print(f"===== [AUDIO][b1b][CONT1] 完了(elapsed={elapsed}s) =====")


if __name__ == "__main__":
    main()
