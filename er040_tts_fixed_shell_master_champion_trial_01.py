# ============================================================
# er040_tts_fixed_shell_master_champion_trial_01.py
# TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01(Trial、Production実装なし)
# ============================================================
# 性質: Trial専用script。Production正式path(er0*.py既存ファイル)は一切
# 変更しない。既存Production関数(shared_narration.ensure_fixed_english_
# segment/ensure_fixed_japanese_segment、voice01.generate_charon_english/
# generate_charon_japanese)をそのまま呼び、styleだけをCandidate別に
# 差し替える。JA側はgenerate_charon_japaneseにstyle override引数が無い
# ため、既存precedent(er011_final26_runtime_evidence_01.pyと同じ
# voice01.p9a.JAPANESE_STYLE_PREFIXの一時モンキーパッチ+復元)を使う。
#
# Master Audio StoreはTrial専用path(--trial-store配下)へ実行時
# モンキーパッチで隔離する(er006_master_audio_store_01.py自体は無変更、
# Production Store[er006_output/master_audio_store_01/]は一切書き込まない。
# 読み取りは、Candidate A[Production既存Baseline再利用]のためmanifest.json
# を読み取り専用で参照するのみ)。
#
# 対象: docs/pm/design_tts_fixed_shell_master_champion_trial_01.md
# §1-5の方針により、num_two/num_threeのCandidate Bは新規生成しない
# (Task B[TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01]が同一style文言・同一
# Flash-Liteモデル・同一voiceで既に検証済み・失敗[Human Review Lock、
# OPEN-222]のため、同じ失敗の再現にAPIを消費しない)。
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import shutil

import er002_common as common
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_master_audio_store_01 as store
import er019_family_x_audio_production_runner_01 as fx_runner

MANAGEMENT_ID = "TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01"

# Production Store(read-only参照のみ、書き込みは一切行わない)
PRODUCTION_STORE_MANIFEST_PATH = "er006_output/master_audio_store_01/manifest.json"
PRODUCTION_STORE_AUDIO_DIR = "er006_output/master_audio_store_01/audio"

# ------------------------------------------------------------
# Role style文言(docs/pm/design_tts_all_spoken_role_style_trial_01.md
# §3のTrial Role style表を無変更のまま流用。新規文言は考案しない)
# ------------------------------------------------------------
ROLE_STYLE_EN = {
    "welcome": "warm, brief, welcoming",               # PROGRAM_SECTION_INTRO
    "preview_intro": "warm, brief, welcoming",          # PROGRAM_SECTION_INTRO
    "key_phrases_intro": "brief, clear, inviting",      # KEY_PHRASE_INTRO
    "full_story_intro": "brief, clear, transitional",   # FULL_STORY_INTRO
    "num_one": "brief, clear, neutral",                 # NUMBER_LABEL
    "num_four": "brief, clear, neutral",                # NUMBER_LABEL
    "num_five": "brief, clear, neutral",                # NUMBER_LABEL
    # num_two/num_three: 設計書§1-5により意図的に対象外(既知失敗の再現回避)
}
ROLE_STYLE_JA_POINT_EXPLANATION = "簡潔に、はっきりと"  # NUMBER_LABEL(JA)

for _name, _style in ROLE_STYLE_EN.items():
    common.assert_no_wpm_specification(_style)
common.assert_no_wpm_specification(ROLE_STYLE_JA_POINT_EXPLANATION)

CANDIDATE_B_STYLE_ID = "trial_ch1_role_style"
CANDIDATE_B_STYLE_VERSION = "trial_ch1_role_style_v1"

# num_two/num_threeのCandidate B既知失敗evidence(§1-5、新規生成しない)
KNOWN_FAILURE_CANDIDATE_B_NUM_TWO_THREE = {
    "num_two": {
        "status": "SKIPPED_KNOWN_FAILURE", "source_management_id": "TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01",
        "evidence_path": "er038_output/tts_all_spoken_role_style_trial_01/hormuz/b1b/audit/review_lock_state.json",
        "open_item": "OPEN-222",
        "reason": "同一style文言(NUMBER_LABEL, \"brief, clear, neutral\")・同一Flash-Liteモデル・"
                   "同一voice(Charon)で既に3attempt全て言語ドリフト(CJK)によりHuman Review Lock到達"
                   "済み。同じ失敗の再現にAPIを消費しないため本Trialでは新規生成しない。",
    },
    "num_three": {
        "status": "SKIPPED_KNOWN_FAILURE", "source_management_id": "TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01",
        "evidence_path": "er038_output/tts_all_spoken_role_style_trial_01/hormuz/b1b/audit/review_lock_state.json",
        "open_item": "OPEN-222",
        "reason": "同上(num_two相当、num_threeも3attempt全て言語ドリフト)。",
    },
}

FIXED_PHRASE_NAMES_EN = list(shared_narration.FIXED_ENGLISH_TEXTS.keys())
FIXED_PHRASE_NAMES_JA = list(shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY.keys())


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


# ------------------------------------------------------------
# Master Audio Store隔離(TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01の
# trial_master_audio_store()と同一パターン、design doc §1-2)
# ------------------------------------------------------------
@contextlib.contextmanager
def trial_master_audio_store(root_dir: str):
    orig = (store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH)
    store.STORE_DIR = root_dir
    store.AUDIO_DIR = f"{root_dir}/audio"
    store.MANIFEST_PATH = f"{root_dir}/manifest.json"
    store.TELEMETRY_PATH = f"{root_dir}/reuse_telemetry.jsonl"
    try:
        yield
    finally:
        store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH = orig


@contextlib.contextmanager
def trial_japanese_style_override(style_text: str):
    """generate_charon_japaneseにstyle override引数が無いため、
    voice01.p9a.JAPANESE_STYLE_PREFIXを一時的に差し替える。既存precedent
    (er011_final26_runtime_evidence_01.py、同一手法)と同じく必ずfinallyで
    復元する。"""
    original = voice01.p9a.JAPANESE_STYLE_PREFIX
    voice01.p9a.JAPANESE_STYLE_PREFIX = style_text
    try:
        yield
    finally:
        voice01.p9a.JAPANESE_STYLE_PREFIX = original


def _wav_metrics(path: str) -> dict:
    samples, framerate, channels, _ = common.read_wav_float(path)
    return common.measure_metrics(samples, framerate)


def _sha256_of(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ------------------------------------------------------------
# Candidate A: Production既存Master(検証済み)をそのまま再利用する。
# 新規TTS/ASR呼び出しは一切行わない。Production Store読み取りのみ
# (書き込みなし)。
# ------------------------------------------------------------
def ensure_candidate_a_from_production(key: "store.MasterAudioKey", out_path: str,
                                        production_manifest: dict) -> dict:
    master_id = key.master_audio_id()
    entry = production_manifest.get(master_id)
    if entry is None or not os.path.exists(entry["audio_path"]):
        return {
            "status": "PRODUCTION_MASTER_NOT_FOUND", "master_audio_id": master_id,
            "key": key.as_dict(), "reused_from_production": False, "cost_jpy": 0.0,
        }
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    shutil.copyfile(entry["audio_path"], out_path)
    metrics = _wav_metrics(out_path)
    qa = entry.get("qa_evidence") or {}
    return {
        "status": "OK", "path": out_path, "reused_from_production": True,
        "master_audio_id": master_id, "production_audio_path": entry["audio_path"],
        "production_created_at": entry.get("created_at"),
        "asr_verified": qa.get("asr_verified"), "asr_text": qa.get("asr_text"),
        "sha256": _sha256_of(out_path), "metrics": metrics, "key": key.as_dict(),
        "cost_jpy": 0.0,
    }


# ------------------------------------------------------------
# Candidate B: Flash-Lite + Role style短文(既存Trial Role style表の値を
# 無変更のまま流用)。既存生成関数(voice01.generate_charon_english/
# generate_charon_japanese)をTrial Store経由で直接呼ぶ。
# ------------------------------------------------------------
def ensure_candidate_b_english(name: str, out_dir: str) -> dict:
    text = shared_narration.FIXED_ENGLISH_TEXTS[name]
    style = ROLE_STYLE_EN[name]
    out_path = f"{out_dir}/{MANAGEMENT_ID}_candB/shell/narration/{name}.wav"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    key = store.MasterAudioKey(
        language="en", speaker_voice="Charon", tts_model_id=shared_narration.TTS_MODEL_FLASH_LITE,
        canonical_text=text, level=None,
        style_instruction_id=CANDIDATE_B_STYLE_ID, style_instruction_version=CANDIDATE_B_STYLE_VERSION,
    )
    with cl.segment_context(f"candB_{name}"):
        result = store.get_or_generate(
            key, out_path,
            lambda p: voice01.generate_charon_english(
                text, p, style_prefix_override=style, tts_backend="speech_metadata_flash_lite"))
    result["candidate"] = "B"
    result["style_prefix_used"] = style
    result["canonical_text"] = text
    result["role"] = "PROGRAM_SECTION_INTRO" if name in ("welcome", "preview_intro") else (
        "KEY_PHRASE_INTRO" if name == "key_phrases_intro" else (
            "FULL_STORY_INTRO" if name == "full_story_intro" else "NUMBER_LABEL"))
    return result


def ensure_candidate_b_japanese_point_explanation(out_dir: str) -> dict:
    text = shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY["point_explanation"]
    out_path = f"{out_dir}/{MANAGEMENT_ID}_candB/shell/narration/point_explanation.wav"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    key = store.MasterAudioKey(
        language="ja", speaker_voice="Charon", tts_model_id=shared_narration.TTS_MODEL_FLASH_LITE,
        canonical_text=text, level=None,
        style_instruction_id=CANDIDATE_B_STYLE_ID, style_instruction_version=CANDIDATE_B_STYLE_VERSION,
    )
    with cl.segment_context("candB_point_explanation"):
        with trial_japanese_style_override(ROLE_STYLE_JA_POINT_EXPLANATION):
            result = store.get_or_generate(
                key, out_path,
                lambda p: voice01.generate_charon_japanese(
                    text, p, text, max_attempts=3, tts_backend="speech_metadata_flash_lite"))
    result["candidate"] = "B"
    result["style_prefix_used"] = ROLE_STYLE_JA_POINT_EXPLANATION
    result["canonical_text"] = text
    result["role"] = "NUMBER_LABEL(JA)"
    return result


# ------------------------------------------------------------
# Candidate C: 既存2.5 Pro系(structured_separation、既定backend、style
# override無し=Production既定style)。shared_narrationの既存関数を
# そのままTrial Store経由で呼ぶ(Trial専用別実装で乖離させない)。
# ------------------------------------------------------------
def ensure_candidate_c_english(name: str, out_dir: str) -> dict:
    narration_dir = f"{out_dir}/{MANAGEMENT_ID}_candC/shell/narration"
    os.makedirs(narration_dir, exist_ok=True)
    with cl.segment_context(f"candC_{name}"):
        result = shared_narration.ensure_fixed_english_segment(
            name, narration_dir, tts_backend="structured_separation")
    result["candidate"] = "C"
    result["canonical_text"] = shared_narration.FIXED_ENGLISH_TEXTS[name]
    result["style_prefix_used"] = "(既定 charon_english_fixed_shell、override無し)"
    return result


def ensure_candidate_c_japanese_point_explanation(out_dir: str) -> dict:
    narration_dir = f"{out_dir}/{MANAGEMENT_ID}_candC/shell/narration"
    os.makedirs(narration_dir, exist_ok=True)
    with cl.segment_context("candC_point_explanation"):
        result = shared_narration.ensure_fixed_japanese_segment(
            "point_explanation", narration_dir, tts_backend="structured_separation")
    result["candidate"] = "C"
    result["canonical_text"] = shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY["point_explanation"]
    result["style_prefix_used"] = "(既定 charon_japanese_fixed_shell、override無し)"
    return result


# ------------------------------------------------------------
# Orchestration
# ------------------------------------------------------------
def run_all_candidates(out_dir: str, trial_store_dir: str, candidates: list[str]) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    production_manifest = load_json(PRODUCTION_STORE_MANIFEST_PATH)

    results = {"A": {}, "B": {}, "C": {}}

    if "A" in candidates:
        # Candidate Aは新規TTS/ASR呼び出しなし(Production再利用のみ)なので
        # Trial Store隔離の外で実行してよい(Production manifestの読み取り
        # 専用アクセスのみ)。
        candidate_a_dir = f"{out_dir}/{MANAGEMENT_ID}_candA/shell/narration"
        os.makedirs(candidate_a_dir, exist_ok=True)
        for name in FIXED_PHRASE_NAMES_EN:
            key = shared_narration._make_english_key(
                shared_narration.FIXED_ENGLISH_TEXTS[name], tts_backend="speech_metadata_flash_lite")
            out_path = f"{candidate_a_dir}/{name}.wav"
            r = ensure_candidate_a_from_production(key, out_path, production_manifest)
            r["canonical_text"] = shared_narration.FIXED_ENGLISH_TEXTS[name]
            r["style_prefix_used"] = "既存Production v2_flash_lite_short_style(FALLBACK[0])"
            results["A"][name] = r
        for name in FIXED_PHRASE_NAMES_JA:
            key = shared_narration._make_japanese_key(
                shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY[name], tts_backend="speech_metadata_flash_lite")
            out_path = f"{candidate_a_dir}/{name}.wav"
            r = ensure_candidate_a_from_production(key, out_path, production_manifest)
            r["canonical_text"] = shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY[name]
            r["style_prefix_used"] = "既存Production v1 flash-lite(override無し)"
            results["A"][name] = r

    with trial_master_audio_store(trial_store_dir):
        if "B" in candidates:
            for name in FIXED_PHRASE_NAMES_EN:
                if name in ("num_two", "num_three"):
                    results["B"][name] = dict(KNOWN_FAILURE_CANDIDATE_B_NUM_TWO_THREE[name])
                    results["B"][name]["canonical_text"] = shared_narration.FIXED_ENGLISH_TEXTS[name]
                    continue
                results["B"][name] = ensure_candidate_b_english(name, out_dir)
            for name in FIXED_PHRASE_NAMES_JA:
                results["B"][name] = ensure_candidate_b_japanese_point_explanation(out_dir)

        if "C" in candidates:
            for name in FIXED_PHRASE_NAMES_EN:
                results["C"][name] = ensure_candidate_c_english(name, out_dir)
            for name in FIXED_PHRASE_NAMES_JA:
                results["C"][name] = ensure_candidate_c_japanese_point_explanation(out_dir)

    save_json(f"{out_dir}/champion_trial_results.json", {
        "management_id": MANAGEMENT_ID, "candidates": results,
        "role_style_en": ROLE_STYLE_EN, "role_style_ja_point_explanation": ROLE_STYLE_JA_POINT_EXPLANATION,
    })
    return results


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default="A,B,C")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--trial-store", required=True)
    parser.add_argument("--budget-jpy", type=float, required=True)
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    candidates = [c.strip().upper() for c in args.candidates.split(",") if c.strip()]
    os.makedirs(args.out_dir, exist_ok=True)
    cl.install(f"{args.out_dir}/raw_usage_log.jsonl")

    with cl.logging_context(MANAGEMENT_ID, "champion_trial"):
        run_all_candidates(args.out_dir, args.trial_store, candidates)

    final_jpy, by_provider = fx_runner.compute_cost_jpy_so_far(f"{args.out_dir}/raw_usage_log.jsonl")
    print(f"[ER040-CHAMPION-TRIAL] candidates={candidates} out_dir={args.out_dir} "
          f"累計費用(JPY)={final_jpy:.2f} by_provider={by_provider}")
    fx_runner.assert_budget_ok(args.out_dir, args.budget_jpy, "after champion trial")


if __name__ == "__main__":
    main()
