# ============================================================
# er011_news_stage3_new_theme_ledger_trial_09_b1b_full_pipeline.py
# 管理ID: FAMILY-A-NEWS-STAGE3-NEW-THEME-LEDGER-TRIAL-09(News Completion
# 実走evidence用、B1B 1本のみ)
# ============================================================
# 目的: Step1で生成済みのB1B OK版article.md(focus_hint条件、run2、
# fact_verdict=PASS、point overlap NG無し)を入力に、Key Phrase選定→TTS→
# Assembly→Audio Validation Gate→playerまでをProduction関数のみ(無変更)
# で通し、theme->research->Ledger->Writer->QA->artifactの実走evidenceと
# する。記事本文(Writer/Fact Checker/Ledger Deviation/Point Overlap QA)
# は一切再生成しない(既存article.mdをそのままコピーし、sha256一致で確認)。
# Production/Prompt/共有module編集なし、Git操作なし。
#
# パイプライン構成はer011_family_a_completion_a2_trend_end_to_end_01_run.py
# のprepare_article/run_scaffold/prepare_key_phrases(B1B新規実行版)/
# run_tts/run_assembly/run_gate_opt_in_checkと同一パターン(そのファイル
# 自体はimportせず、同型の呼び出し構造をsc/tts_gen/asm生Production関数へ
# 直接適用する。理由: そのファイルはTheme2固有のSOURCE_ARTICLE定数・KP5
# 差し替えワークアラウンドを多数含み、本Trialの単純なB1B 1本完走には
# 不要な依存を持ち込むため、Production関数だけを個別にimportする)。
#
# 費用上限: \60(別枠)。Lock発動時はSTOP(既存er011_human_review_lock_01の
# 独自回避は行わない)。
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

import audio_review_player as arp
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er011_tts_cooldown_observation_01 as cooldown_obs
import er011_tts_cooldown_observation_harness_helpers_01 as cooldown_helpers

THEME_ID = "news_stage3_new_theme_ledger_trial_09_b1b_full"
OUT_DIR = f"er011_output/{THEME_ID}"
LEVEL_OUT_DIR = f"{OUT_DIR}/b1b"

SOURCE_ARTICLE = "er011_output/news_stage3_new_theme_ledger_trial_09/b1b/focus_hint/run2/article.md"
ARTICLE_ID = "NEWS_STAGE3_TRIAL09_B1B_FULL"
SOURCE_LEVEL = "B1-B(N3-01, direct generation)"
PROCESS = "B1_SUPPORT"


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# Step 0: article.mdコピー(記事は再生成しない、byte-identical検証)
# ============================================================
def prepare_article() -> str:
    os.makedirs(f"{LEVEL_OUT_DIR}/audit", exist_ok=True)
    dst_path = f"{LEVEL_OUT_DIR}/article.md"
    with open(SOURCE_ARTICLE, encoding="utf-8") as f:
        src_text = f.read()
    shutil.copyfile(SOURCE_ARTICLE, dst_path)
    with open(dst_path, encoding="utf-8") as f:
        dst_text = f.read()
    assert sha(src_text) == sha(dst_text), "article.mdコピー時に内容が変化しました"
    print(f"[B1B-FULL] article.md コピー確認OK(sha256={sha(src_text)[:16]}..., 出典={SOURCE_ARTICLE})")
    return src_text


# ============================================================
# Step 1: Scaffold(記事分割+Preview/Comment、Production関数を無変更で
# 直接呼ぶ)
# ============================================================
def run_scaffold(article_text: str) -> dict:
    parts = sc.split_article_text(article_text)
    save_json(f"{LEVEL_OUT_DIR}/parts.json", parts)
    client = sc.get_client()
    with cl.logging_context(THEME_ID, "scaffold_b1b"):
        support = sc.run_b1_scaffold(client, parts, LEVEL_OUT_DIR, article_text)
    support_status = {k: v.get("status") for k, v in support.items()}
    print(f"[B1B-FULL] Scaffold(Preview/Comment)完了。status={support_status}")
    return parts


# ============================================================
# Step 2: Key Phrase(新規実行、Production関数sc.run_key_phrasesを無変更で
# 直接呼ぶ)
# ============================================================
def prepare_key_phrases(article_text: str) -> dict:
    kp_dir = f"{LEVEL_OUT_DIR}/key_phrases"
    with cl.logging_context(THEME_ID, "keyphrase_b1b"):
        kp = sc.run_key_phrases(article_text, kp_dir, ARTICLE_ID, SOURCE_LEVEL, process=PROCESS)
    sel_status = kp["selection"]["status"]
    canon_status = (kp.get("canonicalization") or {}).get("status")
    redundancy_status = (kp.get("redundancy_qa") or {}).get("status")
    save_json(f"{LEVEL_OUT_DIR}/audit/run_key_phrases_result_summary.json", {
        "selection_status": sel_status, "canonicalization_status": canon_status,
        "redundancy_qa_status": redundancy_status, "redundancy_retry_log": kp.get("redundancy_retry_log"),
    })
    print(f"[B1B-FULL] Key Phrase結果: selection={sel_status} canonicalization={canon_status} "
          f"redundancy={redundancy_status}")
    if kp.get("canonicalization") is None or canon_status not in (
            "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        raise RuntimeError(f"Key Phraseパイプライン失敗、STOP。selection={sel_status} canonicalization={canon_status}")
    if redundancy_status == "REDUNDANCY_NG":
        raise RuntimeError("Key Phrase Redundancy QAがretry上限到達後もNG_REVIEW_REQUIRED、STOP。"
                            "既存Loop Budgetを独自判断で回避しない。")
    return kp


# ============================================================
# Step 3: TTS(Production関数を無変更で直接呼ぶ)
# ============================================================
def run_tts() -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    with cl.logging_context(THEME_ID, "tts_b1b"):
        result = tts_gen.generate_b1_segments(theme)
    return result


# ============================================================
# Step 3b: TTS retry cool-down 20分観測フック(Trial限定、既定OFF)
# (TTS-RETRY-COOLDOWN-20MIN-OBSERVATION-TRIAL-01_REPORT.md 2.2節の配線指示)
# ============================================================
def run_cooldown_observation_stage(tts_result: dict) -> dict:
    """`TTS_COOLDOWN_OBSERVATION`が"1"の場合のみ、tts_result内でstatusが
    STOPPEDだったsegmentについてcooldown観測を実行する(既定OFFではno-op、
    Production側review_lock_state.json/tts_generation_results.json/最終
    成果物wavは一切変更しない)。Production runner組み込みなし。"""
    if os.environ.get("TTS_COOLDOWN_OBSERVATION") != "1":
        return {"status": "SKIPPED_DISABLED", "jobs": 0}

    narration_dir = f"{LEVEL_OUT_DIR}/narration"
    results_path = f"{LEVEL_OUT_DIR}/audit/tts_generation_results.json"
    tts_results_full = json.load(open(results_path, "r", encoding="utf-8")) if os.path.exists(results_path) else {}
    segments_meta = tts_results_full.get("segments", {})
    stopped_segments = [seg_id for seg_id, status in (tts_result.get("segment_status") or {}).items()
                         if status not in ("OK", None)]

    jobs = []
    skipped = []
    for segment_id in stopped_segments:
        three = cooldown_helpers.load_three_attempt_records(narration_dir, segment_id)
        if not three:
            skipped.append({"segment_id": segment_id, "reason": "no_exactly_three_consecutive_ng_records"})
            continue
        canonical_text = (segments_meta.get(segment_id) or {}).get("canonical_text")
        if canonical_text is None:
            skipped.append({"segment_id": segment_id, "reason": "canonical_text_not_found"})
            continue
        binding = cooldown_helpers.build_b1_single_attempt_binding(segment_id, canonical_text, narration_dir)
        if binding is None:
            skipped.append({"segment_id": segment_id, "reason": "no_single_attempt_binding_for_segment_type"})
            continue
        fn, args, kwargs = binding
        jobs.append({
            "level_dir": LEVEL_OUT_DIR, "segment_id": segment_id, "canonical_text": canonical_text,
            "language": "ja" if kwargs.get("language") == "ja" else "en",
            "three_attempt_records": three, "params": dict(kwargs),
            "single_attempt_fn": fn, "single_attempt_args": args, "single_attempt_kwargs": kwargs,
        })

    observations = cooldown_obs.run_batch_observations(jobs) if jobs else []
    summary = {"status": "RAN" if jobs else "NO_ELIGIBLE_SEGMENTS", "jobs": len(jobs),
               "skipped": skipped, "observations": observations}
    save_json(f"{LEVEL_OUT_DIR}/audit/tts_cooldown_observation_stage_summary.json", summary)
    print(f"[{THEME_ID}] TTS cooldown観測: jobs={len(jobs)} skipped={len(skipped)}")
    return summary


# ============================================================
# Step 4: Assembly(Production関数を無変更で直接呼ぶ。内部でAudio
# Validation Gate OFF経路が自動実行される)
# ============================================================
def run_assembly() -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    with cl.logging_context(THEME_ID, "assemble_b1b"):
        try:
            result = asm.stage_assemble_b1(theme)
            result["gate_off_result"] = "PASS"
        except RuntimeError as e:
            result = {"status": "GATE_BLOCKED", "gate_off_result": "BLOCKED", "error": str(e)}
    return result


# ============================================================
# Step 5: Audio Validation Gate opt-in ON経路(OPEN-129、read-only、
# Production関数を無変更で直接呼ぶ)
# ============================================================
def run_gate_opt_in_check() -> dict:
    rs = asm.derive_a_family_required_structure("B1")
    try:
        asm.verify_episode_audio_validation_gate(LEVEL_OUT_DIR, "B1", required_structure=rs)
        return {"gate_on_result": "PASS"}
    except RuntimeError as e:
        return {"gate_on_result": "BLOCKED", "gate_on_message": str(e)[:800]}


def main() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

    article_text = prepare_article()
    run_scaffold(article_text)
    kp_result = prepare_key_phrases(article_text)
    tts_result = run_tts()
    cooldown_result = run_cooldown_observation_stage(tts_result)
    assemble_result = run_assembly()
    gate_on = run_gate_opt_in_check() if assemble_result.get("gate_off_result") == "PASS" else \
        {"gate_on_result": "SKIPPED(gate_off_blocked)"}

    summary = {
        "kp_status": {
            "selection": kp_result["selection"]["status"],
            "canonicalization": (kp_result.get("canonicalization") or {}).get("status"),
            "redundancy_qa": (kp_result.get("redundancy_qa") or {}).get("status"),
        },
        "tts_result_keys": list(tts_result.keys()) if isinstance(tts_result, dict) else None,
        "cooldown_observation": {k: v for k, v in cooldown_result.items() if k != "observations"},
        "assemble_result": {k: v for k, v in assemble_result.items() if k != "article_text"},
        "gate_opt_in_result": gate_on,
    }
    save_json(f"{OUT_DIR}/b1b_full_pipeline_summary.json", summary)
    print(f"[B1B-FULL] 完了。gate_off={assemble_result.get('gate_off_result')} "
          f"gate_on={gate_on.get('gate_on_result')}")
    return summary


if __name__ == "__main__":
    main()
