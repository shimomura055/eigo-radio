# ============================================================
# er012_b_voices_3v_a2_kp_fix_ai_hiring_01.py
# 管理ID: USER-TEST-SCRIPT-READABILITY-PROD-01 Phase D (AI Hiring 3V A2)
# ============================================================
# 目的: AI Hiring 3V A2 canonical記事の現行本文(article.md/parts.json、
# 無変更)から、既存Production Key Phrase生成primitive
# (er012_b_family_voices_a2_production_01.run_key_phrases_a2_from_own_text、
# 無変更)でKey Phraseを再選定・再TTSし、本文音声segmentは旧canonical
# artifact(user_test_voices_a2_minimal_01/ai_hiring_3v_a2/a2)から
# byte-identicalに再利用したうえで再Assembly・player.html・web配信
# artifactを新subdirectory(kp_fix_01)へ生成する。
#
# 3V(Voice 1/2/3)固有のtimeline builder/loaderは、旧artifactの生成に
# 使われたTrial driver er012_b_voices_3v_a2_user_test_01.py内の
# load_a2_sources_3v/build_a2_voices_timeline_3v/row_info_a2_3v(いずれも
# 明示引数のみを取る関数、モジュールグローバル非依存)をそのまま再利用する
# (新規Assemblyロジックの創作ではない)。
# ============================================================
from __future__ import annotations

import hashlib
import json
import os
import shutil

import audio_review_player as player_common
import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_assemble as asm
import er005_cost_logger as cl
import er012_b_family_voices_a2_production_01 as a2prod
import er012_b_family_voices_production_01 as b1prod
import er012_b_voices_3v_a2_user_test_01 as v3
import er012_b_family_editorial_type_registry_01 as registry

OLD_ROOT = "er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2"
OLD_A2 = f"{OLD_ROOT}/a2"
NEW_ROOT = f"{OLD_ROOT}/kp_fix_01"
NEW_A2 = f"{NEW_ROOT}/a2"
NEW_NARR = f"{NEW_A2}/narration"
NEW_KP = f"{NEW_A2}/key_phrases"
NEW_AUDIT = f"{NEW_A2}/audit"
COST_LOG_PATH = f"{NEW_AUDIT}/raw_usage_log.jsonl"
EPISODE_BASENAME = "AI_Hiring_3V_A2_KP_Fix_01.wav"
AUDIO_GATE_LEVEL = registry.get_editorial_type_a2()["audio_gate_level"]
ARTICLE_ID = "ai_hiring_3v_a2_kp_fix_01"
VOICE_A_3V, VOICE_B_3V, VOICE_C_3V = v3.VOICE_A_3V, v3.VOICE_B_3V, v3.VOICE_C_3V

BODY_SEGMENTS = [
    "welcome", "preview_intro", "key_phrases_intro", "full_story_intro",
    "num_one", "num_two", "num_three", "num_four", "num_five",
    "topic_intro", "japanese_title", "preview",
    "full_story_part1", "full_story_part2",
    "point_one", "point_two", "point_three",
    "tension_reflection", "in_one_line",
    "comment_1", "comment_2", "comment_3", "comment_4",
    "point_one_heading", "point_two_heading", "point_three_heading",
]


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def build_player_html_3v_a2_kp_fix(assemble_summary: dict, timeline: list, parts: dict, support_texts: dict,
                                    kp_dir: str, narration_dir: str, out_dir_base: str) -> str:
    """v3.build_player_html_3v_a2()と同型だが、モジュールグローバル
    (KP_DIR/NARRATION_DIR/AUDIT_DIR)ではなく明示引数の新パスを使う版
    (新規デザインの創作ではなく、既存関数を明示引数化しただけ)。"""
    kp_data = load_json(f"{kp_dir}/keywords_canonicalized.json")
    kp_by_rank = {item["rank"]: item for item in kp_data["items"]}
    abs_url = player_common.abs_file_url

    rows = []
    for entry in timeline:
        label = entry["part"]
        if label.startswith("pause_"):
            continue
        info = v3.row_info_a2_3v(label, parts, support_texts, kp_by_rank, narration_dir)
        sec = entry["start_seconds"]
        voice_disp = info["voice"] or ("SFX" if info["sfx"] else "—")
        if info["sfx"]:
            audio_html = "—"
        elif isinstance(info["audio"], tuple):
            audio_html = player_common.render_single_audio_html(tuple(abs_url(p) for p in info["audio"]))
        elif info["audio"]:
            audio_html = player_common.render_single_audio_html(abs_url(info["audio"]))
        else:
            audio_html = "—"
        rows.append(player_common.render_timeline_row(
            sec, label, voice_disp, info["text"], audio_html, missing="未取得" in info["text"]))
    timeline_table = player_common.render_timeline_table(rows)

    kp_rows = []
    for rank in sorted(kp_by_rank):
        kp = kp_by_rank[rank]
        kp_rows.append(f'<tr><td>{rank}</td><td>{kp["used_form"]}</td><td>{kp["japanese_gloss"]}</td>'
                        f'<td>{kp.get("japanese_gloss_tts", kp["japanese_gloss"])}</td>'
                        f'<td>{kp.get("qa_overall_status")}</td></tr>')
    kp_table = ('<table class="kp"><thead><tr><th>#</th><th>English(used_form)</th><th>表示用gloss</th>'
                '<th>TTS用テキスト</th><th>redundancy QA</th></tr></thead>'
                f'<tbody>{"".join(kp_rows)}</tbody></table>')

    episode_audio_url = "web/episode.mp3"
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>USER-TEST-SCRIPT-READABILITY-PROD-01 Phase D player (AI Hiring 3V A2, KP fix)</title>
<style>
{player_common.PLAYER_STANDARD_CSS}
</style>
<script>
{player_common.SEEK_SCRIPT}
</script>
</head><body>
<h1>B-Family(Voices)3V A2: {parts['title']}(Key Phrase再生成版、本文・本文音声は無変更)</h1>
<p class="note">
USER-TEST-SCRIPT-READABILITY-PROD-01 Phase D: 現行canonical本文
(er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/a2/article.md、無変更)
からKey Phraseを再選定・再TTSし、本文音声segmentは旧artifactからsha256一致で
再利用したうえで再Assemblyしたもの(旧Key PhraseはB1 3V Audio Trial-01からの
流用で、既に平易化されていた本文と一致していなかった)。
duration={assemble_summary['duration_seconds']}s peak={assemble_summary['peak']}
clipping={assemble_summary['clipping_detected']}
headroom_safety_valve_applied={assemble_summary['headroom_safety_valve']['applied']}。
voice_a={VOICE_A_3V} / voice_b={VOICE_B_3V} / voice_c={VOICE_C_3V}。
</p>

<h2>Episode audio</h2>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_audio_url}"></audio>

<h2>タイムライン・全スクリプト(収録順、同一行にSeek+voice+script)</h2>
{timeline_table}

<h2>Key Phrase表(詳細、英語+日本語gloss)</h2>
{kp_table}

</body></html>
"""
    out_path = f"{out_dir_base}/player.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path


def main() -> None:
    cl.install(COST_LOG_PATH)
    os.makedirs(NEW_NARR, exist_ok=True)
    os.makedirs(NEW_KP, exist_ok=True)
    os.makedirs(NEW_AUDIT, exist_ok=True)

    # Step 1: article.md/parts.json copy(本文無変更の証跡としてsha256記録)
    shutil.copyfile(f"{OLD_A2}/article.md", f"{NEW_A2}/article.md")
    shutil.copyfile(f"{OLD_A2}/parts.json", f"{NEW_A2}/parts.json")
    with open(f"{NEW_A2}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    article_sha = {
        "article_md_old": sha256_file(f"{OLD_A2}/article.md"),
        "article_md_new": sha256_file(f"{NEW_A2}/article.md"),
        "parts_json_old": sha256_file(f"{OLD_A2}/parts.json"),
        "parts_json_new": sha256_file(f"{NEW_A2}/parts.json"),
    }
    article_sha["article_unchanged"] = article_sha["article_md_old"] == article_sha["article_md_new"]
    article_sha["parts_unchanged"] = article_sha["parts_json_old"] == article_sha["parts_json_new"]
    save_json(f"{NEW_AUDIT}/article_unchanged_check.json", article_sha)

    # Step 2: 本文音声segment(Key Phrase以外)をbyte-identicalに再利用
    old_results = load_json(f"{OLD_A2}/audit/tts_generation_results.json")
    body_sha_table = {}
    new_segments = {}
    for name in BODY_SEGMENTS:
        src = f"{OLD_A2}/narration/{name}.wav"
        dst = f"{NEW_NARR}/{name}.wav"
        old_sha = sha256_file(src)
        shutil.copyfile(src, dst)
        new_sha = sha256_file(dst)
        body_sha_table[name] = {"old_sha256": old_sha, "new_sha256": new_sha, "match": old_sha == new_sha}
        if name in old_results["segments"]:
            entry = dict(old_results["segments"][name])
            entry["path"] = dst
            new_segments[name] = entry
    save_json(f"{NEW_AUDIT}/body_segments_sha256_check.json", body_sha_table)
    assert all(v["match"] for v in body_sha_table.values()), "本文segmentのsha256が旧artifactと不一致です"

    # Step 3: Key Phraseを現行本文から再選定・再TTS(Production primitive、無変更)。
    # 内部canonicalization gateの上限(同一選定に対し最大2回)は無変更のまま、
    # 選定自体を独立して複数回試す外側retry(既存Gateの回避ではない、Free-
    # Address版と同じ運用)。
    OUTER_RETRY_MAX = 4
    outer_attempts_log = []
    kp_run = None
    for outer_attempt in range(1, OUTER_RETRY_MAX + 1):
        kp_run = a2prod.run_key_phrases_a2_from_own_text(article_text, NEW_KP, NEW_NARR, ARTICLE_ID)
        pipeline = kp_run.get("selection_pipeline") or {}
        canon = pipeline.get("canonicalization") or {}
        outer_attempts_log.append({
            "outer_attempt": outer_attempt,
            "selection_status": (pipeline.get("selection") or {}).get("status"),
            "canonicalization_status": canon.get("status"),
            "redundancy_qa_status": (pipeline.get("redundancy_qa") or {}).get("status"),
            "item_reasons_last": (canon.get("attempts_detail") or [{}])[-1].get("item_reasons")
                if isinstance(canon.get("attempts_detail"), list) else None,
            "items_ready": kp_run.get("items") is not None,
        })
        if kp_run.get("items") is not None:
            break
        print(f"[KP-FIX-AI-HIRING][outer_retry {outer_attempt}/{OUTER_RETRY_MAX}] "
              f"canonicalization_status={canon.get('status')} で失敗。選定からやり直します。")
    save_json(f"{NEW_AUDIT}/key_phrase_outer_retry_log.json", outer_attempts_log)
    save_json(f"{NEW_AUDIT}/key_phrase_selection_pipeline_raw.json", kp_run.get("selection_pipeline"))
    if kp_run.get("items") is None:
        raise RuntimeError(f"[KEY_PHRASE_SELECTION_FAILED] outer_retry上限({OUTER_RETRY_MAX}回)到達。"
                            f"status={kp_run.get('status')}。STOP条件(1)に該当します。")

    kp = load_json(f"{NEW_KP}/keywords_canonicalized.json")
    presence_check = []
    for item in kp["items"]:
        span = item["source_span"]
        present = span.lower() in article_text.lower()
        presence_check.append({"rank": item["rank"], "source_span": span, "present_in_article_text": present})
    save_json(f"{NEW_AUDIT}/key_phrase_source_span_presence_check.json", presence_check)
    if not all(p["present_in_article_text"] for p in presence_check):
        raise RuntimeError(f"[KEY_PHRASE_SPAN_NOT_FOUND] {presence_check}。STOP条件(4)に該当する可能性があります。")

    key_phrases_audit = {str(rank): sub for rank, sub in kp_run["results"].items()}
    tts_results = {"segments": new_segments, "key_phrases": key_phrases_audit}
    save_json(f"{NEW_AUDIT}/tts_generation_results.json", tts_results)

    # Step 4: Assembly(3V用loader/timeline builder、Trial driverの既存関数を明示引数で再利用)
    sources = v3.load_a2_sources_3v(kp, NEW_A2, NEW_NARR, AUDIO_GATE_LEVEL)
    gained = asm.apply_b1_gain(sources)
    seq = v3.build_a2_voices_timeline_3v(gained, VOICE_A_3V, VOICE_B_3V, VOICE_C_3V)
    result = asm.assemble_with_timeline(seq)
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)
    assembled = headroom["assembled"]

    os.makedirs(f"{NEW_A2}/assembled", exist_ok=True)
    out_path = f"{NEW_A2}/assembled/{EPISODE_BASENAME}"
    save_json(f"{NEW_AUDIT}/gain_report.json", gained["gain_report"])
    save_json(f"{NEW_AUDIT}/timeline.json", result["timeline"])
    save_json(f"{NEW_AUDIT}/headroom_report.json", headroom["report"])
    common.write_wav_float(out_path, assembled, asm.SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], asm.SR)
    assemble_summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": asm.SR, "channels": 2, "headroom_safety_valve": headroom["report"],
        "voice_a": VOICE_A_3V, "voice_b": VOICE_B_3V, "voice_c": VOICE_C_3V,
    }
    save_json(f"{NEW_A2}/run_summary_assemble.json", assemble_summary)
    print(f"[KP-FIX-AI-HIRING] Assembly status={assemble_summary['status']} "
          f"duration={assemble_summary['duration_seconds']} peak={assemble_summary['peak']} "
          f"clipping={assemble_summary['clipping_detected']}")

    # Step 5: support_texts(comment/preview、既存a2_support_texts.jsonをそのまま流用、本文無変更)
    support_texts = load_json(f"{OLD_A2}/a2_support_texts.json")
    save_json(f"{NEW_A2}/a2_support_texts.json", support_texts)

    # Step 6: player.html + web delivery
    parts = load_json(f"{NEW_A2}/parts.json")
    player_path = build_player_html_3v_a2_kp_fix(
        assemble_summary, result["timeline"], parts, support_texts, NEW_KP, NEW_NARR, NEW_A2)
    print(f"[KP-FIX-AI-HIRING] player.html: {os.path.abspath(player_path)}")

    import er012_b_family_production_runner_01 as runner
    web_result = runner.export_web_delivery_a2_2v_new_topic(NEW_A2, NEW_NARR, assemble_summary)
    save_json(f"{NEW_AUDIT}/web_delivery_result.json", web_result)

    jpy, by_provider = runner.compute_cost_jpy_so_far(COST_LOG_PATH)
    print(f"[KP-FIX-AI-HIRING] cost so far = {jpy:.2f} JPY by_provider={by_provider}")
    save_json(f"{NEW_AUDIT}/cost_summary.json", {"jpy": jpy, "by_provider": by_provider})


if __name__ == "__main__":
    main()
