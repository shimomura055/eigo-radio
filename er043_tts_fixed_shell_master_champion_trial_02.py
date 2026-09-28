# ============================================================
# er043_tts_fixed_shell_master_champion_trial_02.py
# TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02(Trial、Production実装なし)
# ============================================================
# 性質: Trial専用script。Production正式path(er0*.py既存ファイル)は一切
# 変更しない。既存Production関数(voice01.generate_charon_english/
# generate_charon_japanese)をそのまま呼び、styleだけをCandidate/group別に
# 差し替える。JA側style override手法・Master Audio Store隔離手法は、
# `er040_tts_fixed_shell_master_champion_trial_01.py`の既存実装を
# そのままimportして流用する(独自の再実装をしない、delegation指示通り)。
#
# 対象: docs/pm/design_tts_fixed_shell_master_champion_trial_02.md。
# 詳細な設計判断(num_fourをグループ3[5個set]へ含める理由、モデル選択の
# 理由、style文言の逐語記録)は設計書を参照。
#
# 実行は必ずphrase単位/group単位で分割し(`--phrases`)、1コマンドで
# 全20新規生成を一括実行しない(前回インシデント再発防止、delegation
# 「実行安全」節)。champion_trial_results.jsonは実行の都度、既存内容へ
# 追記・上書きマージする(複数回の分割実行を1つの結果ファイルへ集約する)。
from __future__ import annotations

import argparse
import json
import os

import er002_common as common
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_master_audio_store_01 as store
import er019_family_x_audio_production_runner_01 as fx_runner
import er040_tts_fixed_shell_master_champion_trial_01 as champ1

MANAGEMENT_ID = "TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02"

# Production Store(read-only参照のみ、書き込みは一切行わない)。
# champ1の定数をそのまま使う(独自定義しない、path誤りによる別store
# 混入を防ぐ)。
PRODUCTION_STORE_MANIFEST_PATH = champ1.PRODUCTION_STORE_MANIFEST_PATH

# ------------------------------------------------------------
# Phrase group定義(design doc §2-1)
# ------------------------------------------------------------
GROUP1_NO_COMPLAINT = ["welcome", "preview_intro", "key_phrases_intro"]
GROUP2_FULL_STORY_INTRO = ["full_story_intro"]
GROUP3_NUM_SET = ["num_one", "num_two", "num_three", "num_four", "num_five"]
GROUP4_JA_POINT_EXPLANATION = ["point_explanation"]

ALL_PHRASE_NAMES = (GROUP1_NO_COMPLAINT + GROUP2_FULL_STORY_INTRO
                     + GROUP3_NUM_SET + GROUP4_JA_POINT_EXPLANATION)

# ------------------------------------------------------------
# Style文言(design doc §2-4〜§2-7に逐語記録済み、ここでは同じ文字列を
# 定数として保持する)。新規文言はTRIAL-01の既知失敗文言
# ("brief, clear, neutral")を避け、design doc §3の理由により
# num_two/num_threeも含め新規生成する。
# ------------------------------------------------------------
STYLE_TEXT_GROUP1 = "natural, clear, conversational"
STYLE_TEXT_GROUP2_PACE = ("natural, clear, conversational, unhurried pace, "
                           "with a brief pause before continuing")
STYLE_TEXT_GROUP3_B = ("calm, steady, declarative tone, even volume and pace "
                        "across the set, ending each word with a clear falling "
                        "pitch, stated plainly, never rising like a question")
STYLE_TEXT_GROUP3_C = ("measured, matter-of-fact delivery, consistent energy "
                        "and tempo for every word, plain falling pitch at the "
                        "end, spoken as a flat statement, not a question")
STYLE_TEXT_GROUP4_B_JA = "自然な抑揚をつけて、はっきりと落ち着いた調子で話す"
STYLE_TEXT_GROUP4_C_JA = "やわらかい自然な抑揚で、簡潔かつ丁寧に伝える"

for _style in (STYLE_TEXT_GROUP1, STYLE_TEXT_GROUP2_PACE,
               STYLE_TEXT_GROUP3_B, STYLE_TEXT_GROUP3_C):
    common.assert_no_wpm_specification(_style)
common.assert_no_wpm_specification(STYLE_TEXT_GROUP4_B_JA)
common.assert_no_wpm_specification(STYLE_TEXT_GROUP4_C_JA)


def _group_of(name: str) -> str:
    if name in GROUP1_NO_COMPLAINT:
        return "group1_no_complaint"
    if name in GROUP2_FULL_STORY_INTRO:
        return "group2_full_story_intro_pace"
    if name in GROUP3_NUM_SET:
        return "group3_num_set"
    if name in GROUP4_JA_POINT_EXPLANATION:
        return "group4_ja_point_explanation"
    raise ValueError(f"未知のphrase名: {name}")


def _style_for(name: str, candidate: str) -> tuple[str, str, str]:
    """(style_text, style_instruction_id, style_instruction_version)を返す。"""
    group = _group_of(name)
    if group == "group1_no_complaint":
        version = "v1_sample_b" if candidate == "B" else "v1_sample_c"
        return STYLE_TEXT_GROUP1, "trial_ch2_repeat_baseline_style", version
    if group == "group2_full_story_intro_pace":
        version = "v1_pace_b" if candidate == "B" else "v1_pace_c"
        return STYLE_TEXT_GROUP2_PACE, "trial_ch2_full_story_intro_pace", version
    if group == "group3_num_set":
        if candidate == "B":
            return STYLE_TEXT_GROUP3_B, "trial_ch2_num_set_style_b", "v1"
        return STYLE_TEXT_GROUP3_C, "trial_ch2_num_set_style_c", "v1"
    if group == "group4_ja_point_explanation":
        if candidate == "B":
            return STYLE_TEXT_GROUP4_B_JA, "trial_ch2_point_explanation_style_b", "v1"
        return STYLE_TEXT_GROUP4_C_JA, "trial_ch2_point_explanation_style_c", "v1"
    raise ValueError(f"未知のgroup: {group}")


ROLE_LABELS = {
    "welcome": "PROGRAM_SECTION_INTRO", "preview_intro": "PROGRAM_SECTION_INTRO",
    "key_phrases_intro": "KEY_PHRASE_INTRO", "full_story_intro": "FULL_STORY_INTRO",
    "num_one": "NUMBER_LABEL", "num_two": "NUMBER_LABEL", "num_three": "NUMBER_LABEL",
    "num_four": "NUMBER_LABEL", "num_five": "NUMBER_LABEL",
    "point_explanation": "NUMBER_LABEL(JA)",
}


def ensure_new_candidate_english(name: str, candidate: str, out_dir: str) -> dict:
    text = shared_narration.FIXED_ENGLISH_TEXTS[name]
    style_text, style_id, style_version = _style_for(name, candidate)
    out_path = f"{out_dir}/{MANAGEMENT_ID}_cand{candidate}/shell/narration/{name}.wav"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    key = store.MasterAudioKey(
        language="en", speaker_voice="Charon", tts_model_id=shared_narration.TTS_MODEL_FLASH_LITE,
        canonical_text=text, level=None,
        style_instruction_id=style_id, style_instruction_version=style_version,
    )
    with cl.segment_context(f"cand{candidate}_{name}"):
        result = store.get_or_generate(
            key, out_path,
            lambda p: voice01.generate_charon_english(
                text, p, style_prefix_override=style_text, tts_backend="speech_metadata_flash_lite"))
    result["candidate"] = candidate
    result["style_prefix_used"] = style_text
    result["canonical_text"] = text
    result["role"] = ROLE_LABELS[name]
    result["group"] = _group_of(name)
    return result


def ensure_new_candidate_japanese_point_explanation(candidate: str, out_dir: str) -> dict:
    name = "point_explanation"
    text = shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY[name]
    style_text, style_id, style_version = _style_for(name, candidate)
    out_path = f"{out_dir}/{MANAGEMENT_ID}_cand{candidate}/shell/narration/{name}.wav"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    key = store.MasterAudioKey(
        language="ja", speaker_voice="Charon", tts_model_id=shared_narration.TTS_MODEL_FLASH_LITE,
        canonical_text=text, level=None,
        style_instruction_id=style_id, style_instruction_version=style_version,
    )
    with cl.segment_context(f"cand{candidate}_{name}"):
        with champ1.trial_japanese_style_override(style_text):
            result = store.get_or_generate(
                key, out_path,
                lambda p: voice01.generate_charon_japanese(
                    text, p, text, max_attempts=6, tts_backend="speech_metadata_flash_lite"))
    result["candidate"] = candidate
    result["style_prefix_used"] = style_text
    result["canonical_text"] = text
    result["role"] = ROLE_LABELS[name]
    result["group"] = _group_of(name)
    return result


def _load_existing_results(out_dir: str) -> dict:
    path = f"{out_dir}/champion_trial_results.json"
    if os.path.exists(path):
        return champ1.load_json(path)
    return {"management_id": MANAGEMENT_ID, "candidates": {"A": {}, "B": {}, "C": {}}}


def run_selected(out_dir: str, trial_store_dir: str, candidates: list[str],
                  phrases: list[str]) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    results = _load_existing_results(out_dir)
    results.setdefault("candidates", {"A": {}, "B": {}, "C": {}})

    if "A" in candidates:
        production_manifest = champ1.load_json(PRODUCTION_STORE_MANIFEST_PATH)
        candidate_a_dir = f"{out_dir}/{MANAGEMENT_ID}_candA/shell/narration"
        os.makedirs(candidate_a_dir, exist_ok=True)
        for name in phrases:
            if name in GROUP4_JA_POINT_EXPLANATION:
                key = shared_narration._make_japanese_key(
                    shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY[name],
                    tts_backend="speech_metadata_flash_lite")
                out_path = f"{candidate_a_dir}/{name}.wav"
                r = champ1.ensure_candidate_a_from_production(key, out_path, production_manifest)
                r["canonical_text"] = shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY[name]
                r["style_prefix_used"] = "既存Production v1(override無し、既定JAPANESE_STYLE_PREFIX)"
            else:
                key = shared_narration._make_english_key(
                    shared_narration.FIXED_ENGLISH_TEXTS[name], tts_backend="speech_metadata_flash_lite")
                out_path = f"{candidate_a_dir}/{name}.wav"
                r = champ1.ensure_candidate_a_from_production(key, out_path, production_manifest)
                r["canonical_text"] = shared_narration.FIXED_ENGLISH_TEXTS[name]
                r["style_prefix_used"] = "既存Production v2_flash_lite_short_style(FALLBACK[0])"
            r["role"] = ROLE_LABELS[name]
            r["group"] = _group_of(name)
            results["candidates"]["A"][name] = r

    with champ1.trial_master_audio_store(trial_store_dir):
        for candidate in ("B", "C"):
            if candidate not in candidates:
                continue
            for name in phrases:
                if name in GROUP4_JA_POINT_EXPLANATION:
                    results["candidates"][candidate][name] = \
                        ensure_new_candidate_japanese_point_explanation(candidate, out_dir)
                else:
                    results["candidates"][candidate][name] = \
                        ensure_new_candidate_english(name, candidate, out_dir)

    champ1.save_json(f"{out_dir}/champion_trial_results.json", results)
    return results


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default="A,B,C")
    parser.add_argument("--phrases", default="all",
                         help="comma区切りのphrase名、または'all'(既定はA,B,C全10 phraseだが"
                              "delegationにより分割実行を強く推奨)")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--trial-store", required=True)
    parser.add_argument("--budget-jpy", type=float, required=True)
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    candidates = [c.strip().upper() for c in args.candidates.split(",") if c.strip()]
    if args.phrases.strip().lower() == "all":
        phrases = list(ALL_PHRASE_NAMES)
    else:
        phrases = [p.strip() for p in args.phrases.split(",") if p.strip()]
        for p in phrases:
            if p not in ALL_PHRASE_NAMES:
                raise ValueError(f"未知のphrase名: {p}")
    os.makedirs(args.out_dir, exist_ok=True)
    cl.install(f"{args.out_dir}/raw_usage_log.jsonl")

    with cl.logging_context(MANAGEMENT_ID, "champion_trial"):
        run_selected(args.out_dir, args.trial_store, candidates, phrases)

    final_jpy, by_provider = fx_runner.compute_cost_jpy_so_far(f"{args.out_dir}/raw_usage_log.jsonl")
    print(f"[ER043-CHAMPION-TRIAL] candidates={candidates} phrases={phrases} "
          f"累計費用(JPY)={final_jpy:.2f} by_provider={by_provider}")
    fx_runner.assert_budget_ok(args.out_dir, args.budget_jpy, "after champion trial")


if __name__ == "__main__":
    main()
