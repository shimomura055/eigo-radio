# ============================================================
# er011_open112_trend_theme2_b_final_audio_rerun_02.py
# OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-02
# ============================================================
# 目的: Theme 2(若者の旅行、B条件)A2/B1の完成音声を、ユーザー承認
# (2026-09-06:「A/BのProduction wiring完了後、Theme 2のA2/B1完成音声を
# 1回だけ再実行してよい」)に基づき「追加1回のみ」再実行する。
#
# 前提(RERUN-01からの差分): RERUN-01(`er011_open112_trend_theme2_b_
# final_audio_rerun_01.py`)は、Key Phrase選定候補5件中1件が"median"で
# 日本語glossに括弧書き補足(「（中央値）」)を含んだため、既存の構造
# Hard Requirement Validator(`p2g.validate_min_unit_selection`)が
# `KEY_WORDS_STRUCTURE_INVALID`と判定し、A2・B1とも選定段でSTOPした
# (`OPEN-112-TREND-THEME2-B-FINAL-AUDIO-RERUN-01_REPORT.md`参照)。
# その後、`KEYPHRASE-JA-GLOSS-NO-PARENTHETICAL-PROD-WIRING-01`で選定
# Prompt(`b1_p2_keywords_l_prompt_template.txt`)へ「日本語グロスに
# 括弧内の別訳・専門用語・補足を併記しない」趣旨の1句を追加配線し、
# runtime evidence(`er011_output/kp_ja_gloss_no_parenthetical_prod_
# wiring_01/`)でTheme 2 A2/B1(Trial-12記事)双方が構造Validatorを
# 通過することを確認した。本スクリプトはRERUN-01と同一ロジック(コード
# 差分はTHEME_ID/OUT_DIR/article_id等の識別子のみ、本文reuse・Key
# Phrase選定・音声生成・Assembleのロジックは無変更)で、承認済みの
# 「追加1回のみ」の完成音声再実行を実施する。
#
# 条件(ACTIVE_TASK.md参照、RERUN-01と同一):
#   - 本文/Preview/Comment(A2 14 segment・B1 13 segment)はTrial-13の
#     音声を再利用する(review_lock RESOLVED+canonical text sha256一致
#     検証のうえコピー、再TTSしない)。再利用skipロジックは
#     er011_open117_keyphrase_display_tts_separation_trial_02.py
#     (Phase 2 Trial-02)の prepare_level_inputs/reuse_non_kp_segments/
#     _expected_canonical_text をほぼそのまま踏襲する。
#   - Key Phraseのみ、最新Production経路(HEAD=f624a5c時点、表示用/TTS用
#     分離[japanese_gloss/japanese_gloss_tts]・数値placeholder型回避・
#     gloss自然さ基準がすべて選定Prompt/Human Review基準へ配線済み)で
#     選定→canonicalization→Redundancy QA→英語Component→日本語gloss
#     (TTS用フィールド使用)→ASR検証→Assemblyまで実行する。
#     Trial-02と異なり、選定Promptのdisplay/TTS分離はもはやTrial限定の
#     アダプタではなくProduction本体(b1_p2_keywords_l_prompt_template.txt)
#     に配線済みのため、Production関数(sc.run_key_phrases)をそのまま
#     直接呼ぶ(選定Promptのコピー・書き換えは行わない)。
#   - Production関数は無変更。TTSはStandard同期(TTS_EXECUTION_MODE=
#     STANDARD、docs/pm/PM_GOVERNANCE.md 7節)。
#   - 1回だけ。Gate/Human Review Lockで停止したら、override・fallback
#     追加・上限緩和・手動unblock・再選定・場当たり修正は一切行わず
#     打ち切る(片方のlevelが止まっても他方は独立実行可)。
#
# 到達してよいStatus: USER_FINAL_AUDIO_REVIEW_REQUIRED(完成)/
# USER_DECISION_REQUIRED(Gate/Lockで打ち切り)。
# APPROVED_FOR_PRODUCTION・PRODUCTION_WIRED・status格上げは対象外
# (本タスクでは判定しない)。

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration

THEME_ID = "open112_trend_theme2_b_final_audio_rerun_02"
OUT_DIR = f"er011_output/{THEME_ID}"

# 本文/Preview/Comment再利用元(review_lock RESOLVED確認済み、完成音声を
# 実際に生成済みのTrial)。
TRIAL13_DIR = "er011_output/open112_trend_theme2_b_full_audio_trial_13"

LEVELS = {
    "b1b": {
        "source_level": "B1-B(N3-01, direct generation)",
        "process": "B1_SUPPORT",
        "support_file": "b1_support_texts.json",
        "article_id": "THEME2_B1_FINALAUDIORERUN02",
        "reused_segments": [
            "topic_intro", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
            "point_one_heading", "point_two_heading", "full_story_part1", "full_story_part2",
            "point_one", "point_two", "in_one_line",
        ],
    },
    "a2": {
        "source_level": "A2(V2改1, N3-01)",
        "process": "A2_SUPPORT",
        "support_file": "a2_support_texts.json",
        "article_id": "THEME2_A2_FINALAUDIORERUN02",
        "reused_segments": [
            "topic_intro", "japanese_title", "preview", "comment_1", "comment_2", "comment_3",
            "comment_4", "point_one_heading", "point_two_heading", "full_story_part1",
            "full_story_part2", "point_one", "point_two", "in_one_line",
        ],
    },
}


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


# ============================================================
# Step 1: 記事本文非依存の13/14 segmentをTrial-13から再利用
# (er011_open117_keyphrase_display_tts_separation_trial_02.py の
# prepare_level_inputs/reuse_non_kp_segments/_expected_canonical_text と
# 同じロジック。Production変更なし、コピーのみ。)
# ============================================================
def prepare_level_inputs(level: str) -> dict:
    meta = LEVELS[level]
    src_dir = f"{TRIAL13_DIR}/{level}"
    dst_dir = f"{OUT_DIR}/{level}"
    os.makedirs(f"{dst_dir}/audit", exist_ok=True)
    os.makedirs(f"{dst_dir}/narration", exist_ok=True)
    os.makedirs(f"{dst_dir}/key_phrases", exist_ok=True)

    shutil.copyfile(f"{src_dir}/article.md", f"{dst_dir}/article.md")
    with open(f"{src_dir}/article.md", encoding="utf-8") as f:
        src_text = f.read()
    with open(f"{dst_dir}/article.md", encoding="utf-8") as f:
        dst_text = f.read()
    assert src_text == dst_text, f"article.mdコピー時に内容が変化しました: {level}"

    shutil.copyfile(f"{src_dir}/parts.json", f"{dst_dir}/parts.json")
    shutil.copyfile(f"{src_dir}/{meta['support_file']}", f"{dst_dir}/{meta['support_file']}")

    return {"article_text": src_text, "parts": load_json(f"{dst_dir}/parts.json"),
            "support": load_json(f"{dst_dir}/{meta['support_file']}")}


def _expected_canonical_text(name: str, parts: dict, support: dict):
    if name == "topic_intro":
        return f"Today's topic is {parts['title']}."
    if name == "japanese_title":
        return None  # 記事本文以外の独立ソースが無いため、Trial-13記録値をそのまま信頼する
    if name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        return support[name]
    if name in ("point_one_heading", "point_two_heading"):
        return parts[name]
    if name == "full_story_part1":
        return parts["part1"]
    if name == "full_story_part2":
        return parts["part2"]
    if name == "point_one":
        return parts["point_one_body"]
    if name == "point_two":
        return parts["point_two_body"]
    if name == "in_one_line":
        return parts["in_one_line"]
    raise ValueError(f"未知のsegment名: {name}")


def reuse_non_kp_segments(level: str, parts: dict, support: dict) -> dict:
    """Trial-13の13/14 segment(記事本文非依存の共有shell音声[welcome等]は
    含まない、それらはProduction Assembly側が別経路で自動供給する)を、
    生成関数を一切呼ばず、wavファイル+tts_generation_results.jsonエントリ
    をそのままコピー再利用する。前提(wav存在+review_lock RESOLVED+
    canonical text sha256一致)を満たさない場合はSTOPする(自動的な緩和は
    しない)。"""
    meta = LEVELS[level]
    src_dir = f"{TRIAL13_DIR}/{level}"
    dst_dir = f"{OUT_DIR}/{level}"
    src_results = load_json(f"{src_dir}/audit/tts_generation_results.json")
    src_lock = load_json(f"{src_dir}/audit/review_lock_state.json")

    reused_results = {}
    reuse_report = []
    for name in meta["reused_segments"]:
        entry = src_results["segments"].get(name)
        if entry is None:
            raise RuntimeError(f"Trial-13の{level}/{name}がtts_generation_results.jsonに"
                               "見つかりません(STOP)。")
        lock_entry = src_lock.get(name)
        if not lock_entry or lock_entry.get("state") != "RESOLVED":
            raise RuntimeError(f"Trial-13の{level}/{name}はreview_lock RESOLVEDではありません"
                               f"(state={lock_entry}、STOP)。再利用の前提を満たさないため、"
                               "手動確認が必要です。")
        wav_path = f"{src_dir}/narration/{name}.wav"
        if not os.path.exists(wav_path):
            raise RuntimeError(f"Trial-13の{level}/{name}.wavが存在しません(STOP)。")

        expected_text = _expected_canonical_text(name, parts, support)
        recorded_text = entry.get("canonical_text")
        if recorded_text is None:
            recorded_text = entry.get("text")
        if expected_text is not None:
            if sha(expected_text) != sha(recorded_text):
                raise RuntimeError(
                    f"Trial-13の{level}/{name}のcanonical text hashが、本Runが読み込んだ"
                    "article.md/parts.json/support textsから独立に再構成した期待値と一致"
                    f"しません(STOP、再利用不可)。expected_sha256={sha(expected_text)!r} "
                    f"recorded_sha256={sha(recorded_text)!r}")
            text_check = "VERIFIED_MATCH"
        else:
            text_check = "TRUSTED_FROM_TRIAL13_RECORD(no_independent_source)"

        for suffix in ("", "_original"):
            src_wav = f"{src_dir}/narration/{name}{suffix}.wav"
            if os.path.exists(src_wav):
                shutil.copyfile(src_wav, f"{dst_dir}/narration/{name}{suffix}.wav")

        reused_results[name] = entry
        reuse_report.append({
            "segment": name, "lock_state": lock_entry.get("state"), "status": entry.get("status"),
            "canonical_text_sha256": sha(recorded_text), "text_check": text_check,
        })
    return {"segments": reused_results, "reuse_report": reuse_report}


# ============================================================
# Step 2: Key Phrase再選定(Production関数をそのまま直接呼ぶ、
# Trial限定のPromptコピーは行わない)
# ============================================================
def build_kp_tts_map(merged_items: list) -> list:
    """Production canonicalization結果(japanese_gloss=表示用、
    japanese_gloss_tts=TTS用、KEYPHRASE-DISPLAY-TTS-SEPARATION-PROD-
    WIRING-01で配線済み)から、TTS呼び出しに使うテキストを
    tts_gen.resolve_key_phrase_ja_gloss_tts()(Production関数)で解決する。"""
    rows = []
    for item in sorted(merged_items, key=lambda it: it["rank"]):
        tts_text, used_fallback = tts_gen.resolve_key_phrase_ja_gloss_tts(item)
        rows.append({
            "rank": item["rank"], "key_phrase": item["key_phrase"], "used_form": item["used_form"],
            "display_gloss": item["japanese_gloss"], "tts_text": tts_text,
            "tts_text_fallback_derived": used_fallback,
        })
    return rows


# ============================================================
# Step 3: Key Phrase音声(英語Component+日本語gloss)の新規生成
# (Production関数を直接呼ぶ、review_lock/gateはこれらのProduction関数
# 内部でそのまま自動的に動作する)
# ============================================================
# 注意(既知の制約): Production側のretry loop(generate_narration_snippet_
# verified_strict)は、attemptごとに同一out_pathへ上書きするため、関数
# 呼び出しが返った時点でdisk上に残るのは「最後のattempt」の音声だけ
# (attempt 1〜3の音声は、この関数呼び出し内で既に上書き済みで復元
# できない)。Production側のretry loop自体を変更する権限は本タスクに
# 無いため、ここでは「関数が返った直後に残っている最後のattemptの音声」
# を保全する(best-effort)。ASR raw出力・reason等の全attempt分の記録は
# attempts_log/fallback_attempts_logとしてtts_generation_results.jsonに
# そのまま残る(こちらは全attempt分が揃っている)。
STOPPED_EVIDENCE_STATUSES = ("STOPPED", "ASR_VALIDATION_UNCERTAIN", "HUMAN_REVIEW_LOCKED")


def preserve_stopped_audio_evidence(level_out_dir: str, label: str, result: dict, wav_path: str) -> None:
    status = result.get("status")
    if status == "OK" or status not in STOPPED_EVIDENCE_STATUSES:
        return
    evidence_dir = f"{level_out_dir}/audit/stopped_audio_evidence"
    os.makedirs(evidence_dir, exist_ok=True)
    if os.path.exists(wav_path):
        dst = f"{evidence_dir}/{label}_last_attempt_status_{status}.wav"
        shutil.copyfile(wav_path, dst)
        print(f"[RERUN02] {label}: status={status} のためlast attempt音声を保全: {dst}")
    else:
        print(f"[RERUN02] {label}: status={status} だが音声ファイルが存在しません"
              f"(TTS呼び出し自体が発生していないgate STOPの可能性): {wav_path}")
    with open(f"{evidence_dir}/{label}_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)


def generate_kp_audio_b1(level_out_dir: str, kp_map: list) -> dict:
    narration_dir = f"{level_out_dir}/narration"
    kp_results = {}
    for row in kp_map:
        rank = row["rank"]
        used_form = row["used_form"]
        tts_text = row["tts_text"]
        print(f"[RERUN02][b1b] Key Phrase {rank} 英語Component生成: {used_form!r}...")
        with cl.segment_context(f"kp{rank}_english"):
            en_path = f"{narration_dir}/kp{rank}_en.wav"
            en_r = shared_narration.ensure_key_phrase_english_component(
                tts_gen.tts_safe_kp_en(used_form), en_path)
        preserve_stopped_audio_evidence(level_out_dir, f"kp{rank}_en", en_r, en_path)
        print(f"[RERUN02][b1b] Key Phrase {rank} 日本語(TTS用テキスト)生成: {tts_text!r} "
              f"(表示用: {row['display_gloss']!r})...")
        with cl.segment_context(f"kp{rank}_japanese"):
            ja_path = f"{narration_dir}/kp{rank}_ja_charon.wav"
            ja_r = tts_gen.generate_charon_japanese_with_reading_safety(
                tts_text, ja_path,
                tts_gen.expected_substring_ja(tts_text), known_key_phrase_terms=[used_form])
        preserve_stopped_audio_evidence(level_out_dir, f"kp{rank}_ja_charon", ja_r, ja_path)
        ja_r["display_gloss"] = row["display_gloss"]
        ja_r["tts_text_fallback_derived"] = row["tts_text_fallback_derived"]
        kp_results[rank] = {"english": en_r, "japanese": ja_r}
    return kp_results


def generate_kp_audio_a2(level_out_dir: str, kp_map: list) -> dict:
    narration_dir = f"{level_out_dir}/narration"
    kp_results = {}
    for i, row in enumerate(kp_map, start=1):
        rank = row["rank"]
        used_form = row["used_form"]
        tts_text = row["tts_text"]
        print(f"[RERUN02][a2] Key Phrase {rank} 英語Component生成: {used_form!r}...")
        with cl.segment_context(f"kp{rank}_english"):
            en_path = f"{narration_dir}/kp{rank}_en.wav"
            en_r = shared_narration.ensure_key_phrase_english_component(
                tts_gen.tts_safe_kp_en(used_form), en_path)
        preserve_stopped_audio_evidence(level_out_dir, f"kp{rank}_en", en_r, en_path)
        print(f"[RERUN02][a2] meaning_{i}(TTS用テキスト)生成: {tts_text!r} "
              f"(表示用: {row['display_gloss']!r})...")
        with cl.segment_context(f"kp{rank}_japanese_meaning"):
            meaning_path = f"{narration_dir}/meaning_{i}.wav"
            ja_r = tts_gen.generate_a2_japanese_with_reading_safety(
                tts_text, meaning_path,
                tts_gen.expected_substring_ja(tts_text), max_extra_chars=30,
                known_key_phrase_terms=[used_form])
        preserve_stopped_audio_evidence(level_out_dir, f"meaning_{i}", ja_r, meaning_path)
        ja_r["display_gloss"] = row["display_gloss"]
        ja_r["tts_text_fallback_derived"] = row["tts_text_fallback_derived"]
        kp_results[rank] = {"english": en_r, "japanese_meaning": ja_r}
    return kp_results


# ============================================================
# Level単位のオーケストレーション
# ============================================================
def run_level(level: str) -> dict:
    meta = LEVELS[level]
    level_out_dir = f"{OUT_DIR}/{level}"
    inputs = prepare_level_inputs(level)
    article_text = inputs["article_text"]

    kp_dir = f"{level_out_dir}/key_phrases"
    print(f"[RERUN02][{level}] Key Phrase選定+Canonicalization+Redundancy QA "
          "(Production経路、sc.run_key_phrases、無変更)開始...")
    with cl.logging_context(THEME_ID, f"keyphrase_{level}"):
        kp = sc.run_key_phrases(article_text, kp_dir, meta["article_id"], meta["source_level"],
                                 process=meta["process"])

    sel_status = kp["selection"]["status"]
    canon_status = (kp.get("canonicalization") or {}).get("status")
    redundancy_status = (kp.get("redundancy_qa") or {}).get("status")
    print(f"[RERUN02][{level}] Key Phrase結果: selection={sel_status} "
          f"canonicalization={canon_status} redundancy={redundancy_status} "
          f"overall_status={kp.get('status')}")

    with open(f"{level_out_dir}/audit/run_key_phrases_result_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "selection_status": sel_status, "canonicalization_status": canon_status,
            "redundancy_qa_status": redundancy_status,
            "redundancy_retry_log": kp.get("redundancy_retry_log"),
        }, f, ensure_ascii=False, indent=2, default=str)

    if kp.get("canonicalization") is None or canon_status not in (
            "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        return {"level": level, "status": "STOP_KEY_PHRASE_PIPELINE_FAILED", "kp": kp}

    merged_items = kp["canonicalization"]["merged"]["items"]
    kp_map = build_kp_tts_map(merged_items)
    with open(f"{level_out_dir}/audit/kp_display_tts_map.json", "w", encoding="utf-8") as f:
        json.dump(kp_map, f, ensure_ascii=False, indent=2)

    print(f"[RERUN02][{level}] 本文{len(meta['reused_segments'])}segmentをTrial-13(review_lock "
          "RESOLVED確認済み)から再利用(再TTSしない)...")
    reused = reuse_non_kp_segments(level, inputs["parts"], inputs["support"])

    print(f"[RERUN02][{level}] Key Phrase音声(英語+日本語、TTS用テキスト)を新規生成...")
    with cl.logging_context(THEME_ID, f"kp_tts_{level}"):
        if level == "b1b":
            kp_results = generate_kp_audio_b1(level_out_dir, kp_map)
        else:
            kp_results = generate_kp_audio_a2(level_out_dir, kp_map)

    all_results = {"segments": reused["segments"], "key_phrases": kp_results}
    with open(f"{level_out_dir}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    if level == "b1b":
        kp_audio_status = {r: {"en": v["english"].get("status"), "ja": v["japanese"].get("status")}
                            for r, v in kp_results.items()}
    else:
        kp_audio_status = {r: {"en": v["english"].get("status"), "ja": v["japanese_meaning"].get("status")}
                            for r, v in kp_results.items()}
    print(f"[RERUN02][{level}] Key Phrase音声status={kp_audio_status}")

    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    assemble_fn = asm.stage_assemble_b1 if level == "b1b" else asm.stage_assemble_a2
    try:
        with cl.logging_context(THEME_ID, f"assemble_{level}"):
            assemble_result = assemble_fn(theme)
    except RuntimeError as e:
        assemble_result = {"status": "GATE_BLOCKED", "error": str(e)}
        print(f"[RERUN02][{level}] Assemble GATE_BLOCKED: {e}")

    return {
        "level": level, "status": "DONE", "kp_selection_status": sel_status,
        "kp_canonicalization_status": canon_status, "kp_redundancy_status": redundancy_status,
        "kp_overall_status": kp.get("status"), "kp_map": kp_map, "reuse_report": reused["reuse_report"],
        "kp_audio_status": kp_audio_status, "assemble_result": assemble_result,
    }


def main() -> dict:
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

    results = {}
    for level in ["b1b", "a2"]:
        print(f"===== [RERUN02] level={level} 開始 =====")
        try:
            results[level] = run_level(level)
        except RuntimeError as e:
            results[level] = {"level": level, "status": "STOP", "error": str(e)}
            print(f"[RERUN02][{level}] STOP: {e}")

    with open(f"{OUT_DIR}/rerun02_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print("[RERUN02] 完了。")
    return results


if __name__ == "__main__":
    main()
