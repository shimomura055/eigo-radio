# ============================================================
# er042_key_phrase_advanced_english_explanation_audio_style_trial_03.py
# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03
# (ユーザー指示Task 1, 2026-09-28)
# ============================================================
# 目的: Advanced Key Phrase英語解説の "text" 仕様は既にユーザーが正式
# 採用済み(APPROVED_FOR_PRODUCTION、
# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02のB候補5件、Production
# wiringは未実施)。本Trialは音声Styleだけを比較する:
#   Before: "clear, precise, explanatory"
#   After : "clear, precise, unhurried"
# Hormuzの既存5 Key Phrase・既存英語解説文(TRIAL-02のB候補)を完全に
# 逐語再利用し、Phrase・解説文の再生成/再選定は一切行わない。
#
# reuse方針(delegation指定):
#   - Phrase EN音声: er041 outputに既にコピーされている既存Hormuz
#     artifactをそのまま再コピー(新規TTS callなし)。
#   - Before音声: er041が実際に生成した英語解説音声(5件)は
#     style_prefix_used == "clear, precise, explanatory" であることを
#     機械確認済み(本scriptでも再確認する)。一致していればwavをそのまま
#     コピー再利用し、新規TTS callを行わない。
#   - After音声: 既存音声が存在しないため、5件新規生成する
#     (Production同一関数 generate_narration_snippet_verified_strict を
#     Trial Store・style上書きで呼び出し、既存ASR cascade通過必須)。
#
# 完全に隔離: Key Phrase選定ロジック・DB Hybrid・Production Master Audio
# Store(er006_output/master_audio_store_01/)は一切import・変更しない。
# CURRENT_SPEC.mdも無変更。
#
# 実行方法:
#   TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe \
#       er042_key_phrase_advanced_english_explanation_audio_style_trial_03.py \
#       --source-dir "er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz" \
#       --out-dir "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/hormuz" \
#       --trial-store "er042_output/key_phrase_advanced_english_explanation_audio_style_trial_03/master_store" \
#       --tts-backend speech_metadata_flash_lite --budget-jpy 10
# ============================================================

from __future__ import annotations

import argparse
import json
import os
import shutil

MANAGEMENT_ID = "KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-AUDIO-STYLE-TRIAL-03"

BEFORE_STYLE = "clear, precise, explanatory"
AFTER_STYLE = "clear, precise, unhurried"


def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_source_rows(source_dir: str) -> list[dict]:
    """er041 outputのsummary.jsonから、5 Phrase・candidate_b_english_
    explanation(既存確定値)を逐語で読み込む。LLM不使用、再生成なし。"""
    summary = load_json(out_path(source_dir, "summary.json"))
    rows = sorted(summary["items"], key=lambda r: r["rank"])
    if len(rows) != 5:
        raise SystemExit(f"[STOP] er041 summary.jsonのitemsが5件ではありません: {len(rows)}")
    for row in rows:
        if not row.get("candidate_b_english_explanation"):
            raise SystemExit(f"[STOP] phrase={row.get('phrase')!r} に英語解説文がありません")
    return rows


def load_source_audio_summary(source_dir: str) -> dict:
    return load_json(out_path(source_dir, "audio_summary.json"))


def verify_before_style_reusable(audio_summary: dict) -> dict:
    """er041が生成したBefore(explanation)音声のstyle_prefix_usedが
    BEFORE_STYLEと完全一致し、pronunciation resolverによるaugmentation
    が発生していない(= 最終的にTTSへ渡された文字列 == raw style)ことを
    機械確認する。rankをkeyにした辞書を返す。"""
    generated = audio_summary.get("generated_new_explanation_audio", [])
    by_rank = {}
    for item in generated:
        rank = item["rank"]
        style_used = item.get("style_prefix_used")
        hints_applied = (item.get("en_pronunciation_resolver_info") or {}).get("hints_applied")
        if style_used != BEFORE_STYLE:
            raise SystemExit(
                f"[STOP] rank={rank} のer041 style_prefix_used={style_used!r} が "
                f"Before指定({BEFORE_STYLE!r})と一致しません。reuseは行わず、STOPして"
                "報告してください(delegationのreuse前提が崩れています)。")
        if hints_applied:
            raise SystemExit(
                f"[STOP] rank={rank} は発音resolverによるstyle augmentationが発生して"
                "おり、raw style文字列と最終TTS送出文字列が一致しない可能性がありま"
                "す。reuseせず報告してください。")
        if item.get("status") != "OK":
            raise SystemExit(f"[STOP] rank={rank} のer041 Before音声status={item.get('status')!r}")
        by_rank[rank] = item
    return by_rank


# ============================================================
# STEP: reuse (Phrase EN + Before explanation。新規TTS callなし)
# ============================================================
def cmd_reuse(source_dir: str, out_dir: str) -> dict:
    rows = load_source_rows(source_dir)
    audio_summary_src = load_source_audio_summary(source_dir)
    before_by_rank = verify_before_style_reusable(audio_summary_src)

    audio_dir = out_path(out_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    reused = []
    for row in rows:
        rank = row["rank"]
        phrase = row["phrase"]

        phrase_en_src = out_path(source_dir, "audio", f"kp{rank}_en.wav")
        phrase_en_dst = out_path(audio_dir, f"kp{rank}_phrase_en.wav")
        if not os.path.exists(phrase_en_src):
            raise SystemExit(f"[STOP] Phrase EN音声が見つかりません: {phrase_en_src}")
        shutil.copyfile(phrase_en_src, phrase_en_dst)
        reused.append({"rank": rank, "phrase": phrase, "label": "phrase_en",
                        "src": phrase_en_src, "dst": phrase_en_dst,
                        "reused": True, "regenerated": False})

        before_src = out_path(source_dir, "audio", f"kp{rank}_explanation_en.wav")
        before_dst = out_path(audio_dir, f"kp{rank}_before_en.wav")
        if not os.path.exists(before_src):
            raise SystemExit(f"[STOP] Before英語解説音声が見つかりません: {before_src}")
        shutil.copyfile(before_src, before_dst)
        before_meta = before_by_rank[rank]
        reused.append({
            "rank": rank, "phrase": phrase, "label": "before_explanation_en",
            "src": before_src, "dst": before_dst, "reused": True, "regenerated": False,
            "style_prefix_used": before_meta.get("style_prefix_used"),
            "text": before_meta.get("text"),
            "duration_seconds": before_meta.get("duration_seconds"),
            "asr_verified": before_meta.get("asr_verified"),
            "asr_text": before_meta.get("asr_text"),
            "retry_count": before_meta.get("retry_count"),
            "source_management_id": "KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02",
        })

    save_json(out_path(out_dir, "reused_audio_summary.json"),
              {"management_id": MANAGEMENT_ID, "reused": reused})
    print(f"[OK] reuse complete: {len(reused)} files copied (0 new TTS call)")
    return {"rows": rows}


# ============================================================
# STEP: after audio (新規5 call、Production同一関数、Trial Store隔離)
# ============================================================
def cmd_after_audio(source_dir: str, out_dir: str, trial_store: str, tts_backend: str,
                     budget_jpy: float) -> None:
    if os.environ.get("TTS_EXECUTION_MODE") != "STANDARD":
        raise SystemExit(
            "[STOP] After音声生成にはTTS_EXECUTION_MODE=STANDARDの明示が必要です"
            "(delegation T-2)。")

    import er003_v1_repro01_main_generate as repro01
    import er005_cost_logger as cl
    import er019_family_x_audio_production_runner_01 as fx_runner
    import er038_tts_all_spoken_role_style_trial_01 as role_trial

    rows = load_source_rows(source_dir)
    audio_dir = out_path(out_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    generated = []
    usage_log_path = out_path(out_dir, "after_audio_raw_usage_log.jsonl")
    cl.install(usage_log_path)
    with cl.logging_context(MANAGEMENT_ID, "tts"), role_trial.trial_master_audio_store(trial_store):
        for row in rows:
            rank = row["rank"]
            phrase = row["phrase"]
            explanation = row["candidate_b_english_explanation"]
            out_wav = out_path(audio_dir, f"kp{rank}_after_en.wav")
            with cl.segment_context(f"kp{rank}_after_en"):
                r = repro01.generate_narration_snippet_verified_strict(
                    explanation, "en", out_wav, explanation,
                    max_extra_chars=max(20, len(explanation) // 2),
                    max_attempts=2,
                    safety_margin_seconds=repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS,
                    style_prefix_override=AFTER_STYLE, disfluency_qa=True,
                    asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT,
                    enable_non_latin_cascade=True, tts_backend=tts_backend)
            r["rank"] = rank
            r["phrase"] = phrase
            r["role"] = "KEY_PHRASE_EXPLANATION_EN_AFTER_TRIAL_03"
            r["style_prefix_used"] = AFTER_STYLE
            generated.append(r)
            cumulative_jpy, _ = fx_runner.compute_cost_jpy_so_far(usage_log_path)
            print(f"[OK] audio kp{rank}_after_en.wav status={r.get('status')} "
                  f"cumulative_jpy={round(cumulative_jpy, 4)}")
            if cumulative_jpy > budget_jpy:
                stop = {"stop_reason": "budget exceeded during after-audio generation",
                        "total_jpy": round(cumulative_jpy, 4), "budget_jpy": budget_jpy}
                save_json(out_path(out_dir, "after_audio_stop_reason.json"), stop)
                print(f"[STOP] budget exceeded: {round(cumulative_jpy, 4)} > {budget_jpy}")
                break

    final_jpy, by_provider = fx_runner.compute_cost_jpy_so_far(usage_log_path)
    audio_summary = {
        "management_id": MANAGEMENT_ID,
        "generated_after_explanation_audio": generated,
        "total_new_audio_cost_jpy": round(final_jpy, 4),
        "cost_by_provider": by_provider,
    }
    save_json(out_path(out_dir, "after_audio_summary.json"), audio_summary)
    print(f"[DONE] after audio complete. new_cost_jpy={round(final_jpy, 4)} budget_jpy={budget_jpy}")


# ============================================================
# CLI
# ============================================================
def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=MANAGEMENT_ID)
    p.add_argument("--source-dir", required=True,
                    help="er041 output hormuz dir (summary.json, audio_summary.json, audio/)")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--budget-jpy", type=float, default=10.0)
    p.add_argument("--trial-store", default=None, help="After音声生成用Trial専用Master Store")
    p.add_argument("--tts-backend", default="speech_metadata_flash_lite")
    p.add_argument("--skip-reuse", action="store_true", help="reuseステップをskip(after専用再実行用)")
    p.add_argument("--skip-after", action="store_true", help="afterステップをskip(reuse専用実行用)")
    return p


def main() -> None:
    args = build_arg_parser().parse_args()
    if not args.skip_reuse:
        cmd_reuse(args.source_dir, args.out_dir)
    if not args.skip_after:
        trial_store = args.trial_store or out_path(args.out_dir, "..", "master_store")
        cmd_after_audio(args.source_dir, args.out_dir, trial_store, args.tts_backend, args.budget_jpy)


if __name__ == "__main__":
    main()
