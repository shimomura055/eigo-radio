# ============================================================
# er046_key_phrase_advanced_english_explanation_audio_style_trial_04.py
# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04
# (ユーザー指示, 2026-09-28)
# ============================================================
# 目的: TRIAL-03のAfter("clear, precise, unhurried")はユーザー判断で
# 「遅すぎた」(不採用)。Before("clear, precise, explanatory")と
# unhurriedの中間の自然な速度感を3パターン(A/B/C)探索する。
# Phrase選定・英語解説text生成は一切やり直さない
# (Hormuz既存5 Phrase + TRIAL-02のB候補英語解説textを逐語reuse、
#  TRIAL-03出力を直接reuse元とする)。
#
# reuse方針(delegation指定):
#   - Phrase EN音声 / Before(explanatory)音声 / Reference After
#     (unhurried, 不採用だが速度感参考として掲載)音声:
#     TRIAL-03出力(er042_output/.../hormuz)をそのままコピー再利用
#     (新規TTS callなし)。
#   - A/B/C音声: 新規5件x3スタイル=15件生成
#     (Production同一関数 generate_narration_snippet_verified_strict を
#     Trial Store・style上書きで呼び出し、既存ASR cascade通過必須)。
#
# 完全に隔離: Key Phrase選定ロジック・DB Hybrid・Production Master Audio
# Store(er006_output/master_audio_store_01/)は一切import・変更しない。
# CURRENT_SPEC.mdも無変更。
#
# 実行方法:
#   TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe \
#       er046_key_phrase_advanced_english_explanation_audio_style_trial_04.py \
#       --source-dir "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/hormuz" \
#       --out-dir "er046_output/key_phrase_advanced_english_explanation_audio_style_trial_04/hormuz" \
#       --trial-store "er046_output/key_phrase_advanced_english_explanation_audio_style_trial_04/master_store" \
#       --tts-backend speech_metadata_flash_lite --budget-jpy 10
# ============================================================

from __future__ import annotations

import argparse
import json
import os
import shutil

MANAGEMENT_ID = "KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-04"

BEFORE_STYLE = "clear, precise, explanatory"
REFERENCE_AFTER_STYLE = "clear, precise, unhurried"

VARIANT_STYLES = {
    "A": "clear, precise, at a slightly relaxed pace",
    "B": "clear, precise, at a measured pace, without dragging",
    "C": "clear, precise, carefully paced for understanding, without slowing down",
}


def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_source_reused(source_dir: str) -> dict:
    """TRIAL-03のreused_audio_summary.json(phrase_en, before_explanation_en)
    をそのまま読み込む。LLM不使用、再生成なし。"""
    return load_json(out_path(source_dir, "reused_audio_summary.json"))


def load_source_after(source_dir: str) -> dict:
    """TRIAL-03のafter_audio_summary.json(unhurried, 参考列として使用)を
    そのまま読み込む。"""
    return load_json(out_path(source_dir, "after_audio_summary.json"))


def load_source_rows(source_dir: str) -> list[dict]:
    """TRIAL-03のafter_audio_summary.jsonから、5 Phrase・英語解説text
    (TRIAL-02のB候補、TRIAL-03で確定使用済み)を逐語で読み込む。
    LLM不使用、再生成なし。"""
    after = load_source_after(source_dir)["generated_after_explanation_audio"]
    rows = sorted(after, key=lambda r: r["rank"])
    if len(rows) != 5:
        raise SystemExit(f"[STOP] TRIAL-03 after_audio_summary.jsonのitemsが5件ではありません: {len(rows)}")
    for row in rows:
        if not row.get("text"):
            raise SystemExit(f"[STOP] phrase={row.get('phrase')!r} に英語解説文がありません")
        if row.get("style_prefix_used") != REFERENCE_AFTER_STYLE:
            raise SystemExit(
                f"[STOP] rank={row.get('rank')} のTRIAL-03 style_prefix_used="
                f"{row.get('style_prefix_used')!r} がReference After指定"
                f"({REFERENCE_AFTER_STYLE!r})と一致しません。reuse前提が崩れています。")
        if row.get("status") != "OK":
            raise SystemExit(f"[STOP] rank={row.get('rank')} のTRIAL-03 After音声status={row.get('status')!r}")
    return rows


def verify_before_reusable(reused: dict) -> dict:
    """TRIAL-03のbefore_explanation_enエントリがBEFORE_STYLEと完全一致し、
    augmentationが発生していないことを機械確認する。rankをkeyにした辞書
    を返す。"""
    by_rank = {}
    for item in reused.get("reused", []):
        if item.get("label") != "before_explanation_en":
            continue
        rank = item["rank"]
        style_used = item.get("style_prefix_used")
        if style_used != BEFORE_STYLE:
            raise SystemExit(
                f"[STOP] rank={rank} のTRIAL-03 before style_prefix_used={style_used!r} が "
                f"Before指定({BEFORE_STYLE!r})と一致しません。reuseせず報告してください。")
        by_rank[rank] = item
    if len(by_rank) != 5:
        raise SystemExit(f"[STOP] before_explanation_enが5件ではありません: {len(by_rank)}")
    return by_rank


# ============================================================
# STEP: reuse (Phrase EN + Before[explanatory] + Reference After[unhurried]。
# 新規TTS callなし)
# ============================================================
def cmd_reuse(source_dir: str, out_dir: str) -> None:
    reused_src = load_source_reused(source_dir)
    before_by_rank = verify_before_reusable(reused_src)
    after_rows = load_source_rows(source_dir)
    after_by_rank = {r["rank"]: r for r in after_rows}

    phrase_by_rank = {item["rank"]: item for item in reused_src.get("reused", [])
                       if item.get("label") == "phrase_en"}
    if len(phrase_by_rank) != 5:
        raise SystemExit(f"[STOP] phrase_enが5件ではありません: {len(phrase_by_rank)}")

    audio_dir = out_path(out_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    reused = []
    for rank in sorted(phrase_by_rank):
        phrase_entry = phrase_by_rank[rank]
        phrase = phrase_entry["phrase"]

        phrase_dst = out_path(audio_dir, f"kp{rank}_phrase_en.wav")
        if not os.path.exists(phrase_entry["dst"]):
            raise SystemExit(f"[STOP] Phrase EN音声が見つかりません: {phrase_entry['dst']}")
        shutil.copyfile(phrase_entry["dst"], phrase_dst)
        reused.append({"rank": rank, "phrase": phrase, "label": "phrase_en",
                        "src": phrase_entry["dst"], "dst": phrase_dst,
                        "reused": True, "regenerated": False})

        before_meta = before_by_rank[rank]
        before_dst = out_path(audio_dir, f"kp{rank}_before_en.wav")
        if not os.path.exists(before_meta["dst"]):
            raise SystemExit(f"[STOP] Before音声が見つかりません: {before_meta['dst']}")
        shutil.copyfile(before_meta["dst"], before_dst)
        reused.append({
            "rank": rank, "phrase": phrase, "label": "before_explanation_en",
            "src": before_meta["dst"], "dst": before_dst, "reused": True, "regenerated": False,
            "style_prefix_used": before_meta.get("style_prefix_used"),
            "text": before_meta.get("text"),
            "duration_seconds": before_meta.get("duration_seconds"),
            "asr_verified": before_meta.get("asr_verified"),
            "asr_text": before_meta.get("asr_text"),
            "retry_count": before_meta.get("retry_count"),
            "source_management_id": "KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03",
        })

        after_meta = after_by_rank[rank]
        after_src = after_meta["path"]
        after_dst = out_path(audio_dir, f"kp{rank}_reference_after_en.wav")
        if not os.path.exists(after_src):
            raise SystemExit(f"[STOP] Reference After音声が見つかりません: {after_src}")
        shutil.copyfile(after_src, after_dst)
        reused.append({
            "rank": rank, "phrase": phrase, "label": "reference_after_explanation_en",
            "src": after_src, "dst": after_dst, "reused": True, "regenerated": False,
            "style_prefix_used": after_meta.get("style_prefix_used"),
            "text": after_meta.get("text"),
            "duration_seconds": after_meta.get("duration_seconds"),
            "asr_verified": after_meta.get("asr_verified"),
            "asr_text": after_meta.get("asr_text"),
            "retry_count": after_meta.get("retry_count"),
            "source_management_id": "KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03",
        })

    save_json(out_path(out_dir, "reused_audio_summary.json"),
              {"management_id": MANAGEMENT_ID, "reused": reused})
    print(f"[OK] reuse complete: {len(reused)} files copied (0 new TTS call)")


# ============================================================
# STEP: variant audio (新規15 call、Production同一関数、Trial Store隔離)
# ============================================================
def cmd_variant_audio(source_dir: str, out_dir: str, trial_store: str, tts_backend: str,
                       budget_jpy: float) -> None:
    if os.environ.get("TTS_EXECUTION_MODE") != "STANDARD":
        raise SystemExit(
            "[STOP] Variant音声生成にはTTS_EXECUTION_MODE=STANDARDの明示が必要です"
            "(delegation T-2)。")

    import er003_v1_repro01_main_generate as repro01
    import er005_cost_logger as cl
    import er019_family_x_audio_production_runner_01 as fx_runner
    import er038_tts_all_spoken_role_style_trial_01 as role_trial

    rows = load_source_rows(source_dir)
    audio_dir = out_path(out_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    generated = []
    usage_log_path = out_path(out_dir, "variant_audio_raw_usage_log.jsonl")
    cl.install(usage_log_path)
    stopped = False
    with cl.logging_context(MANAGEMENT_ID, "tts"), role_trial.trial_master_audio_store(trial_store):
        for row in rows:
            if stopped:
                break
            rank = row["rank"]
            phrase = row["phrase"]
            explanation = row["text"]
            for label, style in VARIANT_STYLES.items():
                out_wav = out_path(audio_dir, f"kp{rank}_variant_{label}_en.wav")
                with cl.segment_context(f"kp{rank}_variant_{label}_en"):
                    r = repro01.generate_narration_snippet_verified_strict(
                        explanation, "en", out_wav, explanation,
                        max_extra_chars=max(20, len(explanation) // 2),
                        max_attempts=2,
                        safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS,
                        style_prefix_override=style, disfluency_qa=True,
                        asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT,
                        enable_non_latin_cascade=True, tts_backend=tts_backend)
                r["rank"] = rank
                r["phrase"] = phrase
                r["role"] = f"KEY_PHRASE_EXPLANATION_EN_VARIANT_{label}_TRIAL_04"
                r["variant_label"] = label
                r["style_prefix_used"] = style
                generated.append(r)
                cumulative_jpy, _ = fx_runner.compute_cost_jpy_so_far(usage_log_path)
                print(f"[OK] audio kp{rank}_variant_{label}_en.wav status={r.get('status')} "
                      f"cumulative_jpy={round(cumulative_jpy, 4)}")
                if cumulative_jpy > budget_jpy:
                    stop = {"stop_reason": "budget exceeded during variant-audio generation",
                            "total_jpy": round(cumulative_jpy, 4), "budget_jpy": budget_jpy}
                    save_json(out_path(out_dir, "variant_audio_stop_reason.json"), stop)
                    print(f"[STOP] budget exceeded: {round(cumulative_jpy, 4)} > {budget_jpy}")
                    stopped = True
                    break

    final_jpy, by_provider = fx_runner.compute_cost_jpy_so_far(usage_log_path)
    audio_summary = {
        "management_id": MANAGEMENT_ID,
        "generated_variant_audio": generated,
        "total_new_audio_cost_jpy": round(final_jpy, 4),
        "cost_by_provider": by_provider,
    }
    save_json(out_path(out_dir, "variant_audio_summary.json"), audio_summary)
    print(f"[DONE] variant audio complete. new_cost_jpy={round(final_jpy, 4)} budget_jpy={budget_jpy}")


# ============================================================
# CLI
# ============================================================
def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=MANAGEMENT_ID)
    p.add_argument("--source-dir", required=True,
                    help="TRIAL-03 output hormuz dir (reused_audio_summary.json, after_audio_summary.json)")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--budget-jpy", type=float, default=10.0)
    p.add_argument("--trial-store", default=None, help="Variant音声生成用Trial専用Master Store")
    p.add_argument("--tts-backend", default="speech_metadata_flash_lite")
    p.add_argument("--skip-reuse", action="store_true", help="reuseステップをskip(variant専用再実行用)")
    p.add_argument("--skip-variant", action="store_true", help="variantステップをskip(reuse専用実行用)")
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    if not args.skip_reuse:
        cmd_reuse(args.source_dir, args.out_dir)
    if not args.skip_variant:
        trial_store = args.trial_store or out_path(args.out_dir, "..", "master_store")
        cmd_variant_audio(args.source_dir, args.out_dir, trial_store, args.tts_backend, args.budget_jpy)


if __name__ == "__main__":
    main()
