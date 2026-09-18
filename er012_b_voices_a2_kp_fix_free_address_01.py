# ============================================================
# er012_b_voices_a2_kp_fix_free_address_01.py
# 管理ID: USER-TEST-SCRIPT-READABILITY-PROD-01 Phase D (Free-Address A2)
# ============================================================
# 目的: Free-Address A2 canonical記事の現行本文(article.md/parts.json、
# 無変更)から、既存Production Key Phrase生成primitive
# (er012_b_family_voices_a2_production_01.run_key_phrases_a2_from_own_text、
# 無変更)でKey Phraseを再選定・再TTSし、本文音声segmentは旧canonical
# artifact(editorial_b_family_voices_a2_production_wiring_01/a2)から
# byte-identicalに再利用したうえで再Assembly・player.html・web配信
# artifactを新subdirectory(kp_fix_01)へ生成する。
#
# 使用primitive(すべて既存Production module、無変更):
#   - er012_b_family_voices_a2_production_01(a2prod):
#       run_key_phrases_a2_from_own_text, load_a2_sources_for_b_family,
#       build_a2_voices_timeline, row_info_a2
#   - er012_b_family_production_runner_01(runner):
#       build_player_html_a2_2v_new_topic, export_web_delivery_a2_2v_new_topic,
#       compute_cost_jpy_so_far
#   - er003_v1_n3_01_assemble(asm): apply_b1_gain, assemble_with_timeline,
#       apply_headroom_safety_valve, SR
#   - er005_cost_logger(cl): install()
# ============================================================
from __future__ import annotations

import hashlib
import json
import os
import shutil

import er002_common as common
import er003_b1_p9a_audio as p9a  # noqa: F401 (a2prod内部で使用、importで整合確認)
import er003_v1_n3_01_assemble as asm
import er005_cost_logger as cl
import er012_b_family_production_runner_01 as runner
import er012_b_family_voices_a2_production_01 as a2prod
import er012_b_family_editorial_type_registry_01 as registry

OLD_ROOT = "er012_output/editorial_b_family_voices_a2_production_wiring_01"
OLD_A2 = f"{OLD_ROOT}/a2"
NEW_ROOT = f"{OLD_ROOT}/kp_fix_01"
NEW_A2 = f"{NEW_ROOT}/a2"
NEW_NARR = f"{NEW_A2}/narration"
NEW_KP = f"{NEW_A2}/key_phrases"
NEW_AUDIT = f"{NEW_A2}/audit"
COST_LOG_PATH = f"{NEW_AUDIT}/raw_usage_log.jsonl"
EPISODE_BASENAME = "B_Family_A2_KP_Fix_01.wav"
AUDIO_GATE_LEVEL = registry.get_editorial_type_a2()["audio_gate_level"]
ARTICLE_ID = "free_address_a2_kp_fix_01"

BODY_SEGMENTS = [
    "welcome", "preview_intro", "key_phrases_intro", "full_story_intro",
    "num_one", "num_two", "num_three", "num_four", "num_five",
    "topic_intro", "japanese_title", "preview",
    "full_story_part1", "full_story_part2", "point_one", "point_two",
    "tension_reflection", "in_one_line",
    "comment_1", "comment_2", "comment_3", "comment_4",
    "point_one_heading", "point_two_heading",
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
        # 共有固定narration(welcome/preview_intro/key_phrases_intro/
        # full_story_intro/num_one〜five)はMaster Audio Store経由の共有
        # segmentであり、この記事固有のtts_generation_results.jsonには
        # 元々記録されていない(Gate側もこのjsonのkeyに存在しないsegmentは
        # チェック対象外、既存挙動どおり)。存在するsegmentのみ引き継ぐ。
        if name in old_results["segments"]:
            entry = dict(old_results["segments"][name])
            entry["path"] = dst
            new_segments[name] = entry
    save_json(f"{NEW_AUDIT}/body_segments_sha256_check.json", body_sha_table)
    assert all(v["match"] for v in body_sha_table.values()), "本文segmentのsha256が旧artifactと不一致です"

    # Step 3: Key Phraseを現行本文から再選定・再TTS(Production primitive、無変更)。
    # run_key_phrases_a2_from_own_text()内部のcanonicalization gateは既存
    # 上限(同一選定結果に対し最大2回)のまま無変更。ここでの外側retryは、
    # 選定(Selection)自体からやり直す独立した新規呼び出しであり、内部Gateの
    # 上限を回避・無効化するものではない(選定はLLMの確率的出力のため、
    # 別のcandidate 5件になれば構造的に安全なケースがあるための再試行、
    # kp5_regen_and_completion_01等の先例と同じ「再実行すれば別の結果になる」
    # 運用に倣う)。上限OUTER_RETRY_MAXまで失敗したらSTOP条件(1)として報告する。
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
        print(f"[KP-FIX-FREE-ADDRESS][outer_retry {outer_attempt}/{OUTER_RETRY_MAX}] "
              f"canonicalization_status={canon.get('status')} で失敗。選定からやり直します。")
    save_json(f"{NEW_AUDIT}/key_phrase_outer_retry_log.json", outer_attempts_log)
    save_json(f"{NEW_AUDIT}/key_phrase_selection_pipeline_raw.json", kp_run.get("selection_pipeline"))
    if kp_run.get("items") is None:
        raise RuntimeError(f"[KEY_PHRASE_SELECTION_FAILED] outer_retry上限({OUTER_RETRY_MAX}回)到達。"
                            f"status={kp_run.get('status')}。STOP条件(1)に該当します。")

    kp = load_json(f"{NEW_KP}/keywords_canonicalized.json")
    # 本文実在確認(機械確認): source_spanが現行article_textに実在するか
    presence_check = []
    for item in kp["items"]:
        span = item["source_span"]
        present = span.lower() in article_text.lower()
        presence_check.append({"rank": item["rank"], "source_span": span, "present_in_article_text": present})
    save_json(f"{NEW_AUDIT}/key_phrase_source_span_presence_check.json", presence_check)
    if not all(p["present_in_article_text"] for p in presence_check):
        raise RuntimeError(f"[KEY_PHRASE_SPAN_NOT_FOUND] {presence_check}。STOP条件(4)に該当する可能性があります。")

    key_phrases_audit = {}
    for rank_str, sub in kp_run["results"].items():
        key_phrases_audit[str(rank_str)] = sub

    # Step 4: audit/tts_generation_results.json統合(Gate用)
    tts_results = {"segments": new_segments, "key_phrases": key_phrases_audit}
    save_json(f"{NEW_AUDIT}/tts_generation_results.json", tts_results)

    # Step 5: Assembly(既存Production primitiveをそのまま呼ぶ、新規ロジックなし)
    voice_res = load_json(f"{OLD_A2}/audit/voice_resolution.json")
    voice_a, voice_b = voice_res["voice_a"], voice_res["voice_b"]

    sources = a2prod.load_a2_sources_for_b_family(kp, NEW_A2, NEW_NARR, AUDIO_GATE_LEVEL)
    gained = asm.apply_b1_gain(sources)
    seq = a2prod.build_a2_voices_timeline(gained, voice_a, voice_b)
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
    import er003_b1_p9a_audio as p9a_local
    assemble_summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a_local.peak(assembled), 5),
        "sample_rate": asm.SR, "channels": 2, "headroom_safety_valve": headroom["report"],
        "voice_a": voice_a, "voice_b": voice_b,
    }
    save_json(f"{NEW_A2}/run_summary_assemble.json", assemble_summary)
    print(f"[KP-FIX-FREE-ADDRESS] Assembly status={assemble_summary['status']} "
          f"duration={assemble_summary['duration_seconds']} peak={assemble_summary['peak']} "
          f"clipping={assemble_summary['clipping_detected']}")

    # Step 6: support_texts(comment/preview/japanese_title、旧記録から復元、本文無変更なので流用可)
    support_texts = {
        "comment_1": old_results["segments"]["comment_1"].get("canonical_text"),
        "comment_2": old_results["segments"]["comment_2"].get("canonical_text"),
        "comment_3": old_results["segments"]["comment_3"].get("canonical_text"),
        "comment_4": old_results["segments"]["comment_4"].get("canonical_text"),
        "preview": old_results["segments"]["preview"].get("canonical_text"),
        "japanese_title": old_results["segments"]["japanese_title"].get("text"),
    }
    save_json(f"{NEW_A2}/a2_support_texts.json", support_texts)

    # Step 7: player.html + web delivery(既存Production汎用関数、明示引数)
    parts = load_json(f"{NEW_A2}/parts.json")
    player_path = runner.build_player_html_a2_2v_new_topic(
        assemble_summary, result["timeline"], parts, support_texts, voice_a, voice_b, {},
        NEW_A2, NEW_NARR, NEW_KP, {"theme_id": "free_address_a2_kp_fix_01"})
    print(f"[KP-FIX-FREE-ADDRESS] player.html: {os.path.abspath(player_path)}")

    web_result = runner.export_web_delivery_a2_2v_new_topic(NEW_A2, NEW_NARR, assemble_summary)
    save_json(f"{NEW_AUDIT}/web_delivery_result.json", web_result)

    jpy, by_provider = runner.compute_cost_jpy_so_far(COST_LOG_PATH)
    print(f"[KP-FIX-FREE-ADDRESS] cost so far = {jpy:.2f} JPY by_provider={by_provider}")
    save_json(f"{NEW_AUDIT}/cost_summary.json", {"jpy": jpy, "by_provider": by_provider})


if __name__ == "__main__":
    main()
