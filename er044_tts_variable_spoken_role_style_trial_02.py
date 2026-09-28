# ============================================================
# er044_tts_variable_spoken_role_style_trial_02.py
# TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02(Trial、Production実装なし)
# ============================================================
# 性質: Trial専用script。Production正式path(er0*.py既存ファイル)は
# 一切変更しない。既存Production TTS関数(voice01/news_tail_fix/n3_tts)を
# style_prefix_override引数付きでそのまま呼ぶ(EN側)。JA側は
# er038_tts_all_spoken_role_style_trial_01.generate_ja_role_style
# (Task Bが実装済み、変更禁止・importのみ)をそのまま再利用する。
#
# 詳細根拠: docs/pm/design_tts_variable_spoken_role_style_trial_02.md
#
# 重要な発見(§1-2): delegationが「J0=現状」と想定した日本語style
# 「落ち着いた、自然な話し言葉で」は、実は現行Productionには一切配線
# されていない(Task Bが導入したTrial限定の新規style)。現行Production
# JAは常にp9a.JAPANESE_STYLE_PREFIX(長文instruction)を使う(style
# override機構自体が存在しない)。本scriptのJ0はこの実測値を採用する
# (真のProduction現状)。
#
# --stage all/run_tts_stage全体は本scriptには実装しない(前回インシデント
# 再発防止)。segment×pattern単位の直接関数呼び出しのみを提供する。
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import shutil

import er002_common as common
import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er019_family_x_audio_production_runner_01 as fx_runner
import er020_tts_retry_local_rewrite_01 as retry_primitive
import er038_tts_all_spoken_role_style_trial_01 as t01

MANAGEMENT_ID = "TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02"

# ------------------------------------------------------------
# JA J0(真のProduction現状、design doc §2で実測確認、逐語)
# ------------------------------------------------------------
import er003_b1_p9a_audio as p9a  # noqa: E402

J0_STYLE_JA = p9a.JAPANESE_STYLE_PREFIX  # Production実値そのまま参照(改変しない)

J_PATTERN_STYLES = {
    "J0": J0_STYLE_JA,
    "J1": "落ち着いた、自然な話し言葉で。意味の流れに合わせて軽く抑揚をつけてください。",
    "J2": "落ち着いた、自然な話し言葉で。強調点や話の転換に応じて抑揚をつけてください。大げさにしないでください。",
    "J3": "落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。"
          "演技がかった話し方は避けてください。",
}
for _p, _s in J_PATTERN_STYLES.items():
    if _p != "J0":
        common.assert_no_wpm_specification(_s)

E_PATTERN_STYLES = {
    "FULL_STORY": {
        "E0": "calm, steady news narration",
        "E1": "calm, steady news narration, with a touch of natural inflection that follows the meaning.",
        "E2": "calm, steady news narration with natural emphasis at key points and turns; not dramatic.",
        "E3": "calm, steady news narration, naturally expressive at key points, contrasts, and the "
              "conclusion; understated, not theatrical.",
    },
    "IN_ONE_LINE": {
        "E0": "concise, clear",
        "E1": "concise, clear, with a natural closing tone.",
        "E2": "concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.",
        "E3": "concise, clear, with a slightly more expressive, confident closing landing; understated, "
              "not theatrical.",
    },
    "TOPIC_INTRO": {
        "E0": "brief, clear, engaging news topic introduction",
        "E1": "brief, clear, engaging news topic introduction, with a touch of natural lift.",
        "E2": "brief, clear, engaging news topic introduction with natural emphasis on the topic; not "
              "dramatic.",
        "E3": "brief, clear, engaging news topic introduction, naturally expressive but understated; not "
              "theatrical, not a trailer voice.",
    },
}
for _role, _pmap in E_PATTERN_STYLES.items():
    for _p, _s in _pmap.items():
        common.assert_no_wpm_specification(_s)

JA_SEGMENTS_REQUIRED = ("preview", "comment_1", "comment_2")
JA_SEGMENTS_OPTIONAL = ("comment_3", "comment_4")
EN_SEGMENTS_REQUIRED = ("full_story_part1", "in_one_line")
EN_SEGMENTS_OPTIONAL = ("topic_intro",)

_EN_SEGMENT_ROLE = {
    "full_story_part1": "FULL_STORY", "full_story_part2": "FULL_STORY", "full_story_part3": "FULL_STORY",
    "in_one_line": "IN_ONE_LINE", "topic_intro": "TOPIC_INTRO",
}

# ------------------------------------------------------------
# J0/E0 reuse元(design doc §1-1/§1-3、read-onlyでコピーするのみ)
# ------------------------------------------------------------
J0_REUSE_SOURCE_DIR = (
    "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/"
    "hormuz__run_06_flashlite_full_kp/a2/narration")
E0_REUSE_SOURCE_DIR = "er038_output/tts_all_spoken_role_style_trial_01/hormuz/b1b/narration"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _reuse_copy(src: str, dst: str, style_used: str, role: str, canonical_text: str, note: str) -> dict:
    if not os.path.exists(src):
        return {"status": "STOPPED", "reason": f"reuse対象の音声が見つかりません: {src}"}
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    return {
        "status": "OK", "reused": True, "reused_from": src, "path": dst,
        "style_prefix_used": style_used, "role": role, "canonical_text": canonical_text,
        "sha256": _sha256(dst), "note": note,
    }


@contextlib.contextmanager
def trial_master_audio_store(root_dir: str):
    """t01.trial_master_audio_store()と同一機構(Production Storeは
    一切読み書きしない、本Trial専用path)。t01側の実装をそのまま使う。"""
    with t01.trial_master_audio_store(root_dir):
        yield


# ------------------------------------------------------------
# JA generation(J1-J3のみ、J0はreuse)
# ------------------------------------------------------------
def generate_ja_pattern_segment(text: str, out_path: str, pattern: str, tts_backend: str,
                                 known_key_phrase_terms=None) -> dict:
    style = J_PATTERN_STYLES[pattern]
    with cl.segment_context(f"vr2_{pattern}"):
        r = t01.generate_ja_role_style(
            text, out_path, style, "Aoede", n3_tts._generate_a2_japanese_minimal_instruction,
            tts_backend, max_extra_chars=40, known_key_phrase_terms=known_key_phrase_terms)
    r["canonical_text"] = text
    r["style_prefix_used"] = style
    r["pattern"] = pattern
    return r


# ------------------------------------------------------------
# EN generation(E1-E3のみ、E0はreuse)
# ------------------------------------------------------------
def generate_en_pattern_segment(segment_name: str, text: str, out_path: str, pattern: str,
                                 tts_backend: str) -> dict:
    role = _EN_SEGMENT_ROLE[segment_name]
    style = E_PATTERN_STYLES[role][pattern]
    with cl.segment_context(f"vr2_{pattern}"):
        if segment_name == "topic_intro":
            r = voice01.generate_charon_english(
                n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(text)), out_path,
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(
                    "topic_intro"),
                enable_pronunciation_resolver=True, style_prefix_override=style, tts_backend=tts_backend)
        else:
            disfluency_qa = (segment_name == "in_one_line")
            r = news_tail_fix.generate_news_narration_wide_margin(
                n3_tts.tts_safe_news_en(text), out_path,
                disfluency_qa=disfluency_qa,
                enable_connected_speech_equivalence_layer=retry_primitive.connected_speech_enabled_for(
                    segment_name),
                enable_repetition_qa=(segment_name in fx_runner._BODY_SEGMENT_NAMES),
                enable_pronunciation_resolver=True, style_prefix_override=style, tts_backend=tts_backend)
    r["canonical_text"] = text
    r["style_prefix_used"] = style
    r["pattern"] = pattern
    r["role"] = role
    return r


# ------------------------------------------------------------
# Orchestration(segment×pattern単位、部分実行のみ)
# ------------------------------------------------------------
def run_ja_segment(theme_out_dir: str, segment_name: str, patterns: list, tts_backend: str) -> dict:
    out_dir = f"{theme_out_dir}/a2"
    narration_dir = f"{out_dir}/narration_vr2"
    os.makedirs(narration_dir, exist_ok=True)
    support = load_json(f"{theme_out_dir}/a2/a2_support_texts.json")
    text = support[segment_name]
    results = {}
    trial_store_dir = f"{theme_out_dir}/master_store"
    with trial_master_audio_store(trial_store_dir):
        for pattern in patterns:
            out_path = f"{narration_dir}/{segment_name}_{pattern}.wav"
            if pattern == "J0":
                src = f"{J0_REUSE_SOURCE_DIR}/{segment_name}.wav"
                results[pattern] = _reuse_copy(
                    src, out_path, J0_STYLE_JA, "PREVIEW" if segment_name == "preview" else "COMMENT",
                    text,
                    "真のProduction現状音声をread-onlyでreuse(design doc §1-3、"
                    "hormuz__run_06_flashlite_full_kp、asr_verified=true実測確認済み、"
                    "style override機構自体が現行Productionに存在しないため生成コード"
                    "パスは実質同一)。")
            else:
                results[pattern] = generate_ja_pattern_segment(text, out_path, pattern, tts_backend)
    return {"segment": segment_name, "language": "ja", "results": results}


def run_en_segment(theme_out_dir: str, segment_name: str, patterns: list, tts_backend: str) -> dict:
    out_dir = f"{theme_out_dir}/b1b"
    narration_dir = f"{out_dir}/narration_vr2"
    os.makedirs(narration_dir, exist_ok=True)
    parts = load_json(f"{theme_out_dir}/b1b/parts.json")
    if segment_name == "topic_intro":
        text = f"Today's topic is {parts['title']}."
    else:
        text = parts[{"full_story_part1": "part1", "in_one_line": "in_one_line"}[segment_name]]
    role = _EN_SEGMENT_ROLE[segment_name]
    results = {}
    trial_store_dir = f"{theme_out_dir}/master_store"
    with trial_master_audio_store(trial_store_dir):
        for pattern in patterns:
            out_path = f"{narration_dir}/{segment_name}_{pattern}.wav"
            if pattern == "E0":
                src = f"{E0_REUSE_SOURCE_DIR}/{segment_name}.wav"
                results[pattern] = _reuse_copy(
                    src, out_path, E_PATTERN_STYLES[role]["E0"], role, text,
                    "TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01(Task B、er038)b1b出力をread-onlyで"
                    "reuse(design doc §1-1、style値がProduction FAMILY_X_ROLE_STYLE_EN["
                    f"{role!r}]と完全一致することを実測確認済み、"
                    "en_pronunciation_resolver_info.hints_applied=false実測確認済み)。")
            else:
                results[pattern] = generate_en_pattern_segment(segment_name, text, out_path, pattern, tts_backend)
    return {"segment": segment_name, "language": "en", "results": results}


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-run", required=True)
    parser.add_argument("--segment", required=True,
                         help="1つのsegment_id(preview/comment_1..4/full_story_part1/in_one_line/topic_intro)")
    parser.add_argument("--language", required=True, choices=("ja", "en"))
    parser.add_argument("--patterns", required=True, help="カンマ区切り(例: J1,J2,J3 または E0,E1,E2,E3)")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--tts-backend", default="speech_metadata_flash_lite",
                         choices=("structured_separation", "speech_metadata_flash_lite"))
    parser.add_argument("--budget-jpy", type=float, required=True)
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    cl.install(f"{args.out_dir}/raw_usage_log.jsonl")
    patterns = [p.strip() for p in args.patterns.split(",") if p.strip()]

    with cl.logging_context("tts_variable_spoken_role_style_trial_02", "tts"):
        if args.language == "ja":
            summary = run_ja_segment(args.out_dir, args.segment, patterns, args.tts_backend)
        else:
            summary = run_en_segment(args.out_dir, args.segment, patterns, args.tts_backend)

    result_path = f"{args.out_dir}/results/{args.language}_{args.segment}.json"
    save_json(result_path, summary)
    fx_runner.assert_budget_ok(args.out_dir, args.budget_jpy, f"after {args.language}:{args.segment}")

    final_jpy, by_provider = fx_runner.compute_cost_jpy_so_far(f"{args.out_dir}/raw_usage_log.jsonl")
    print(f"[ER044-TRIAL] segment={args.segment} language={args.language} patterns={patterns} "
          f"累計費用(JPY)={final_jpy:.2f} by_provider={by_provider}")
    print(f"[ER044-TRIAL] result saved: {result_path}")


if __name__ == "__main__":
    main()
