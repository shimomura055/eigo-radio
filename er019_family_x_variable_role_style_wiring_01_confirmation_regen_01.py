# ============================================================
# er019_family_x_variable_role_style_wiring_01_confirmation_regen_01.py
# TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B、2026-09-28)
# ============================================================
# 性質: 確認用再生成(¥20上限、部分実行専用の小スクリプト)。
#
# runner(er019_family_x_audio_production_runner_01.py)のCLIは--stage tts
# 実行時にlevel全体(a2/b1bそれぞれ12segment前後+Key Phrase)を一括生成し、
# segment単位の部分実行引数を持たない。delegation記載の代替方針に従い、
# runnerを直接呼ばず、runnerが実際に使うのと同じ低レベル生成関数を、対象
# segmentのみ直接呼び出す(記事text自体の再生成は行わない、Hormuzの既存
# Flash-Lite run[tts_backend=speech_metadata_flash_lite確認済み]から
# parts.json/support textをreadonly再利用する)。
#
# 対象(13 segment、tts_backend="speech_metadata_flash_lite"固定):
#   Standard(A2) JA 5件: preview, comment_1〜4
#     -> n3_tts.generate_a2_japanese_with_reading_safety(style_prefix_override=J3)
#   Advanced(B1B) EN 6件: topic_intro, full_story_part1,
#     full_story_part2_heading, full_story_part2, full_story_part3_heading,
#     in_one_line
#     -> voice01.generate_charon_english / news_tail_fix.generate_news_
#        narration_wide_margin / point_headings.generate(E2/E0[headingは対象外])
#   Standard(A2) EN 2件: full_story_part1, in_one_line
#     -> n3_tts.generate_a2_segment_with_slowdown(E2 + A2_SLOWER_PACE_
#        INSTRUCTION連結、slower重畳の実測用)
#
# 実行方法:
#   TTS_EXECUTION_MODE=STANDARD .venv/Scripts/python.exe \
#     er019_family_x_variable_role_style_wiring_01_confirmation_regen_01.py
from __future__ import annotations

import hashlib
import json
import os

import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_point_headings_aoede as point_headings
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er033_tts_flash_lite_family_x_styles_01 as fl_styles

_SOURCE_DIR = (
    "er019_output/family_x_audio_production_wiring_01/"
    "family_x_b3_diversity_trial_01/hormuz__run_06_flashlite_full_kp"
)
_OUT_DIR = (
    "er019_output/family_x_audio_production_wiring_01/"
    "variable_role_style_wiring_regression_01/hormuz"
)
_TTS_BACKEND = "speech_metadata_flash_lite"
_BUDGET_JPY = 20.0
_MANAGEMENT_ID = "TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01"


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def _cost_so_far_jpy(cost_log_path: str) -> float:
    import er019_family_x_audio_production_runner_01 as runner
    jpy, _by_provider = runner.compute_cost_jpy_so_far(cost_log_path)
    return jpy


def main() -> None:
    narration_dir = f"{_OUT_DIR}/narration"
    audit_dir = f"{_OUT_DIR}/audit"
    os.makedirs(narration_dir, exist_ok=True)
    os.makedirs(audit_dir, exist_ok=True)

    manifest_path = "er006_output/master_audio_store_01/manifest.json"
    manifest_sha_before = _sha256_file(manifest_path)

    cost_log_path = f"{_OUT_DIR}/raw_usage_log.jsonl"
    cl.install(cost_log_path)

    a2_parts = _load_json(f"{_SOURCE_DIR}/a2/parts.json")
    a2_support = _load_json(f"{_SOURCE_DIR}/a2/a2_support_texts.json")
    b1_parts = _load_json(f"{_SOURCE_DIR}/b1b/parts.json")

    results = {}
    stopped_early = False
    stop_reason = None

    def _budget_ok(note: str) -> bool:
        nonlocal stopped_early, stop_reason
        jpy = _cost_so_far_jpy(cost_log_path)
        print(f"[VW1B-CONFIRM][cost] so far={jpy:.2f} JPY ({note})")
        if jpy > _BUDGET_JPY:
            stopped_early = True
            stop_reason = f"budget guard: {jpy:.2f} JPY > cap {_BUDGET_JPY} JPY (at {note})"
            print(f"[VW1B-CONFIRM][BUDGET_GUARD] {stop_reason}")
            return False
        return True

    with cl.logging_context("variable_role_style_wiring_regression_01/hormuz", "tts_confirmation"):
        # --------------------------------------------------------
        # Standard(A2) JA 5件: preview, comment_1-4 (J3)
        # --------------------------------------------------------
        for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
            if not _budget_ok(f"before {name}"):
                break
            text = a2_support[name]
            with cl.segment_context(name):
                r = n3_tts.generate_a2_japanese_with_reading_safety(
                    text, f"{narration_dir}/{name}.wav", n3_tts.expected_substring_ja(text),
                    style_prefix_override=fl_styles.FAMILY_X_ROLE_STYLE_JA,
                    tts_backend=_TTS_BACKEND)
            r["canonical_text"] = text
            r["expected_style_prefix"] = fl_styles.FAMILY_X_ROLE_STYLE_JA
            results[f"a2_ja_{name}"] = r

        # --------------------------------------------------------
        # Advanced(B1B) EN 6件
        # --------------------------------------------------------
        if not stopped_early and _budget_ok("before b1b_topic_intro"):
            topic_intro_text = f"Today's topic is {b1_parts['title']}."
            with cl.segment_context("b1b_topic_intro"):
                r = voice01.generate_charon_english(
                    n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_intro_text)),
                    f"{narration_dir}/b1b_topic_intro.wav",
                    enable_pronunciation_resolver=True,
                    style_prefix_override=fl_styles.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"],
                    tts_backend=_TTS_BACKEND)
            r["canonical_text"] = topic_intro_text
            r["expected_style_prefix"] = fl_styles.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"]
            results["b1b_topic_intro"] = r

        for name, text in (("b1b_full_story_part1", b1_parts["part1"]),
                            ("b1b_in_one_line", b1_parts["in_one_line"])):
            if stopped_early or not _budget_ok(f"before {name}"):
                break
            role = "IN_ONE_LINE" if name == "b1b_in_one_line" else "FULL_STORY"
            with cl.segment_context(name):
                r = news_tail_fix.generate_news_narration_wide_margin(
                    n3_tts.tts_safe_news_en(text), f"{narration_dir}/{name}.wav",
                    disfluency_qa=(name == "b1b_in_one_line"),
                    enable_pronunciation_resolver=True,
                    style_prefix_override=fl_styles.FAMILY_X_ROLE_STYLE_EN[role],
                    tts_backend=_TTS_BACKEND)
            r["canonical_text"] = text
            r["expected_style_prefix"] = fl_styles.FAMILY_X_ROLE_STYLE_EN[role]
            results[name] = r

        for heading_name, heading_text in (("b1b_full_story_part2_heading", b1_parts["heading1"]),
                                            ("b1b_full_story_part3_heading", b1_parts["heading2"])):
            if stopped_early or not _budget_ok(f"before {heading_name}"):
                break
            with cl.segment_context(heading_name):
                r = point_headings.generate(
                    n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(heading_text)),
                    f"{narration_dir}/{heading_name}.wav",
                    style_prefix_override=fl_styles.FAMILY_X_ROLE_STYLE_EN["HEADING_READOUT"],
                    tts_backend=_TTS_BACKEND)
            r["canonical_text"] = heading_text
            r["expected_style_prefix"] = fl_styles.FAMILY_X_ROLE_STYLE_EN["HEADING_READOUT"]
            results[heading_name] = r

        if not stopped_early and _budget_ok("before b1b_full_story_part2"):
            body_text = b1_parts["body2"]
            with cl.segment_context("b1b_full_story_part2"):
                r = news_tail_fix.generate_news_narration_wide_margin(
                    n3_tts.tts_safe_news_en(body_text), f"{narration_dir}/b1b_full_story_part2.wav",
                    disfluency_qa=False, enable_pronunciation_resolver=True,
                    style_prefix_override=fl_styles.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"],
                    tts_backend=_TTS_BACKEND)
            r["canonical_text"] = body_text
            r["expected_style_prefix"] = fl_styles.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"]
            results["b1b_full_story_part2"] = r

        # --------------------------------------------------------
        # Standard(A2) EN 2件: slower重畳の実測
        # --------------------------------------------------------
        for name, text in (("a2_en_full_story_part1", a2_parts["part1"]),
                            ("a2_en_in_one_line", a2_parts["in_one_line"])):
            if stopped_early or not _budget_ok(f"before {name}"):
                break
            role = "IN_ONE_LINE" if name == "a2_en_in_one_line" else "FULL_STORY"
            combined_style = f"{fl_styles.FAMILY_X_ROLE_STYLE_EN[role]}\n{n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip()}"
            import er002_common as common
            common.assert_no_wpm_specification(combined_style)
            tts_input = n3_tts.tts_safe_news_en(text)
            sub = n3_tts.first_words(text)
            with cl.segment_context(name):
                r = n3_tts.generate_a2_segment_with_slowdown(
                    tts_input, f"{narration_dir}/{name}.wav", sub,
                    style_prefix_override=combined_style,
                    disfluency_qa=(name == "a2_en_in_one_line"),
                    tts_backend=_TTS_BACKEND)
            r["canonical_text"] = text
            r["expected_style_prefix"] = combined_style
            results[name] = r

    manifest_sha_after = _sha256_file(manifest_path)
    final_cost_jpy = _cost_so_far_jpy(cost_log_path)

    summary = {
        "management_id": _MANAGEMENT_ID,
        "source_dir": _SOURCE_DIR,
        "tts_backend": _TTS_BACKEND,
        "budget_jpy_cap": _BUDGET_JPY,
        "final_cost_jpy": final_cost_jpy,
        "stopped_early": stopped_early,
        "stop_reason": stop_reason,
        "segment_count_executed": len(results),
        "segment_status": {k: v.get("status") for k, v in results.items()},
        "master_audio_store_manifest_sha256_before": manifest_sha_before,
        "master_audio_store_manifest_sha256_after": manifest_sha_after,
        "master_audio_store_manifest_unchanged": manifest_sha_before == manifest_sha_after,
    }
    _save_json(f"{audit_dir}/confirmation_regen_results.json", {"segments": results, "summary": summary})
    _save_json(f"{audit_dir}/confirmation_regen_summary.json", summary)
    print(f"[VW1B-CONFIRM] done. final_cost_jpy={final_cost_jpy:.2f} "
          f"segment_count={len(results)} stopped_early={stopped_early} "
          f"manifest_unchanged={summary['master_audio_store_manifest_unchanged']}")


if __name__ == "__main__":
    main()
