# ============================================================
# er012_b_voices_a2_slowdown_keyphrase_regen_04_runner.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04(Lane B)
# ============================================================
# ユーザー決定(2026-09-08、正式)に基づき、`editorial_b_voices_a2_free_
# address_03`をbaselineとして`.../04/`へコピーし、以下だけを追加で
# 行う(baseline全体の再生成はしない、コスト節約規則を遵守):
#   1. Voice A/B本文(point_one/point_two)へ標準A2の既存6% slowdown
#      (style instruction+6% time-stretch)を適用して再生成する
#      (er012_editorial_b_voices_a2_trial02_runner.
#      generate_voice_body_wide_margin_with_a2_slowdown、既存関数2つを
#      組み合わせただけの新規合成関数、本タスクで追加)。
#   2. Key Phrase 4「stay put」を既存の承認済み再生成経路
#      (review_lock.approve_regenerate() + repro01.
#      generate_key_phrase_component_verified()、いずれもProduction、
#      無変更)で1回だけ再生成し、旧版(Master Audio Store由来、_03のまま
#      保全)と新版を両方保持する。新版がASR verified=Trueなら採用、
#      そうでなければ旧版のまま(個別patchはしない)。
#      重要: Key Phrase英語Componentはer006_master_audio_store_01
#      経由でlevel=None(episode横断で共有)のcacheとして扱われている。
#      本タスクはそのShared Storeのmanifest/cacheへは一切書き込まない
#      (er006_*は共有Production module、変更禁止)。新版はこのepisode
#      専用の新規ローカルファイル(kp4_en_new_v2.wav)としてのみ生成し、
#      Master Audio Storeのgenerate_fn経由(store.get_or_generate)は
#      使わない。
#   3. Fact Checker `REVIEW_REQUIRED`(複合Voice帰属)を、今回のA2に限り
#      ユーザー確認済みとして承認記録を残す(恒久運用にしない旨を明記)。
#   4. 上記を反映して再Assembly、標準player形式でstay put比較行を追加。
#
# 費用上限: 本タスク単独で¥100(このrunが新規に生成する分のみ、_03以前の
# 既存費用は含まない。raw_usage_log.jsonlを_04独自に新規開始する、
# _03_runner.pyと同じ設計)。
from __future__ import annotations

import hashlib
import os
import shutil
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

SRC_DIR = "er012_output/editorial_b_voices_a2_free_address_03"
DST_DIR = "er012_output/editorial_b_voices_a2_free_address_04"

os.environ["A2_TRIAL02_OUT_DIR_OVERRIDE"] = DST_DIR
os.environ["A2_TRIAL02_EPISODE_BASENAME_OVERRIDE"] = "B_Family_A2_Free_Address_Trial04.wav"
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_n3_01_tts_generate as n3_tts  # noqa: E402
import er003_v1_repro01_main_generate as repro01  # noqa: E402
import er005_cost_logger as cl  # noqa: E402
import er011_human_review_lock_01 as review_lock  # noqa: E402
import er012_editorial_b_voices_a2_trial02_runner as r02  # noqa: E402(OUT_DIR override確定後にimport)

BUDGET_JPY_CAP_04 = 100.0  # 委任元指示の上限(本run独自ログのみで判定)


def _copy_baseline() -> None:
    """_03の全出力を_04へコピーする(raw_usage_log.jsonlだけは_04独自に
    新規開始するため除外)。_03_runner.py::_copy_baseline()と同一パターン。"""
    if os.path.exists(DST_DIR):
        print(f"[REGEN04-RUNNER] {DST_DIR} は既に存在するため、コピーをskipします。")
        return
    shutil.copytree(SRC_DIR, DST_DIR)
    old_cost_log = f"{DST_DIR}/a2/audit/raw_usage_log.jsonl"
    if os.path.exists(old_cost_log):
        os.remove(old_cost_log)  # _04独自の新規コストログをcl.install()で作る
    old_episode_wav = f"{DST_DIR}/a2/assembled/B_Family_A2_Free_Address_Trial03.wav"
    if os.path.exists(old_episode_wav):
        os.remove(old_episode_wav)  # _04側はrun_assembly()が新規ファイル名で書き出すため不要

    old_needle = "editorial_b_voices_a2_free_address_03"
    new_needle = "editorial_b_voices_a2_free_address_04"
    text_exts = (".json", ".txt", ".jsonl", ".md", ".html")
    for root, _dirs, files in os.walk(DST_DIR):
        for fn in files:
            if not fn.endswith(text_exts):
                continue
            path = os.path.join(root, fn)
            with open(path, encoding="utf-8") as f:
                content = f.read()
            if old_needle in content:
                content = content.replace(old_needle, new_needle)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
    print(f"[REGEN04-RUNNER] {SRC_DIR} -> {DST_DIR} をコピーしました(baseline再利用、raw_usage_log.jsonlは除外)。")


def assert_budget_ok_04(note: str = "") -> float:
    jpy, by_provider = r02.compute_cost_jpy_so_far()
    print(f"[REGEN04-RUNNER][cost] so far={jpy:.2f} JPY by_provider={by_provider} ({note})")
    if jpy > BUDGET_JPY_CAP_04:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {jpy:.2f} JPY > cap {BUDGET_JPY_CAP_04} JPY. Stopping ({note}).")
    return jpy


def _regenerate_voice_bodies(voice_a: str, voice_b: str) -> dict:
    """point_one/point_two(Voice A/B)を標準A2の既存6% slowdownで
    再生成し、tts_generation_results.json/run_summary_tts.jsonを
    この2segment分だけ更新する(他segmentは_03のまま無変更)。"""
    parts = r02.load_json(f"{r02.A2_DIR}/parts.json")
    tts_results_path = f"{r02.AUDIT_DIR}/tts_generation_results.json"
    data = r02.load_json(tts_results_path)

    diff_table = []
    for name, text, voice_name in (
        ("point_one", parts["point_one_body"], voice_a),
        ("point_two", parts["point_two_body"], voice_b),
    ):
        out_path = f"{r02.NARRATION_DIR}/{name}.wav"
        before_sha256 = hashlib.sha256(open(out_path, "rb").read()).hexdigest() if os.path.exists(out_path) else None
        before_duration = n3_tts.a2_slowdown.read_wav_duration_seconds(out_path) if os.path.exists(out_path) else None

        tts_input = n3_tts.tts_safe_news_en(text)
        print(f"[REGEN04-RUNNER] {name}再生成({voice_name}、標準A2 6% slowdown適用)...")
        with cl.segment_context(name):
            result = r02.generate_voice_body_wide_margin_with_a2_slowdown(name, tts_input, out_path, voice_name)
        result["canonical_text"] = text
        data["segments"][name] = result

        after_duration = n3_tts.a2_slowdown.read_wav_duration_seconds(out_path) if os.path.exists(out_path) else None
        diff_table.append({
            "segment": name, "voice": voice_name, "status": result.get("status"),
            "slowdown_applied": result.get("slowdown_info") is not None,
            "before_sha256": before_sha256, "after_sha256": p9a_sha256(out_path),
            "before_duration_seconds": before_duration, "after_duration_seconds": after_duration,
        })
        assert_budget_ok_04(f"after {name} regen")

    r02.save_json(tts_results_path, data)
    run_summary_path = f"{r02.A2_DIR}/run_summary_tts.json"
    run_summary = r02.load_json(run_summary_path)
    for row in diff_table:
        run_summary["segment_status"][row["segment"]] = row["status"]
    r02.save_json(run_summary_path, run_summary)
    r02.save_json(f"{r02.AUDIT_DIR}/voice_body_slowdown_diff_04.json", diff_table)
    print(f"[REGEN04-RUNNER] Voice A/B slowdown適用結果: {diff_table}")
    return {"diff_table": diff_table, "results": {row["segment"]: data["segments"][row["segment"]] for row in diff_table}}


def p9a_sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _regenerate_stay_put_key_phrase() -> dict:
    """Key Phrase「stay put」を既存の承認済み再生成経路で1回だけ
    再生成する(Master Audio Storeのcache/manifestへは一切書き込まない、
    新規ローカルファイルのみ)。"""
    kp_path = f"{r02.KP_DIR}/keywords_canonicalized.json"
    kp = r02.load_json(kp_path)
    item = next(it for it in kp["items"] if it["used_form"] == "stay put")
    rank = item["rank"]
    used_form = item["used_form"]
    tts_text = n3_tts.tts_safe_kp_en(used_form)

    old_path = f"{r02.NARRATION_DIR}/kp{rank}_en.wav"
    preserved_old_path = f"{r02.NARRATION_DIR}/kp{rank}_en_old_v1.wav"
    shutil.copyfile(old_path, preserved_old_path)

    kp_reuse_path = f"{r02.AUDIT_DIR}/key_phrase_reuse_and_regen.json"
    kp_reuse = r02.load_json(kp_reuse_path)
    old_entry = kp_reuse[str(rank)]["english"]
    old_qa_summary = (f"status={old_entry.get('status')} asr_text={old_entry.get('asr_text')!r} "
                       f"disfluency_checked={old_entry.get('disfluency_checked')} "
                       f"(flagged={(old_entry.get('disfluency_evidence') or {}).get('flagged')}) "
                       f"reused_from_master_audio_store={old_entry.get('reused')}")

    new_path = f"{r02.NARRATION_DIR}/kp{rank}_en_new_v2.wav"
    approval_record_path = f"{r02.AUDIT_DIR}/stay_put_regen_user_approval_04.json"
    approval = review_lock.approve_regenerate(new_path, tts_text, approved_by="user")
    approval_note = {
        "approval_record": approval, "approved_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "management_id": "EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04",
        "scope": "Key Phrase 'stay put'(rank=4)英語Component、語末/t/可聴性改善比較のための1回だけの再生成",
        "note": "2026-09-08ユーザー決定・今回限り・恒久運用にしない",
    }
    r02.save_json(approval_record_path, approval_note)

    print(f"[REGEN04-RUNNER] Key Phrase {rank}「stay put」1回だけ再生成(承認記録: {approval_record_path})...")
    with cl.segment_context(f"kp{rank}_en_regen_v2"):
        new_result = repro01.generate_key_phrase_component_verified(tts_text, new_path)
    assert_budget_ok_04("after stay put regen")

    qa_pass = new_result.get("status") == "OK" and new_result.get("asr_verified") is True
    new_qa_summary = (f"status={new_result.get('status')} asr_text={new_result.get('asr_text')!r} "
                       f"asr_verified={new_result.get('asr_verified')} "
                       f"disfluency_checked={new_result.get('disfluency_checked')} "
                       f"(flagged={(new_result.get('disfluency_evidence') or {}).get('flagged')})")
    adopted = "new" if qa_pass else "old"
    if adopted == "new":
        shutil.copyfile(new_path, old_path)
        # tts_generation_results.json / key_phrase_reuse_and_regen.json双方の
        # rank=4 englishエントリを、Assembly Gateが実際に参照する新結果へ更新する
        # (used_form・disfluency_checked等の証跡ごと差し替え、旧resultはold_pathに
        # 別途保全済みのため失われない)。
        new_result_for_gate = dict(new_result)
        new_result_for_gate["used_form"] = used_form
        kp_reuse[str(rank)]["english"] = new_result_for_gate
        r02.save_json(kp_reuse_path, kp_reuse)

        tts_results_path = f"{r02.AUDIT_DIR}/tts_generation_results.json"
        tts_data = r02.load_json(tts_results_path)
        tts_data["key_phrases"][str(rank)]["english"] = new_result_for_gate
        r02.save_json(tts_results_path, tts_data)
        print(f"[REGEN04-RUNNER] stay put: 新版採用(QA PASS)。kp{rank}_en.wavを新版へ差し替え。")
    else:
        print(f"[REGEN04-RUNNER] stay put: 新版がQA NG(またはstatus!=OK)のため旧版を維持。個別patchはしない。")

    comparison = {
        "rank": rank, "used_form": used_form, "tts_text": tts_text,
        "old_path": preserved_old_path, "new_path": new_path, "adopted": adopted,
        "old_qa_summary": old_qa_summary, "new_qa_summary": new_qa_summary,
        "approval_record_path": approval_record_path, "new_result": new_result,
    }
    r02.save_json(f"{r02.AUDIT_DIR}/stay_put_comparison_04.json", comparison)
    return comparison


def _record_fact_checker_human_review_approval() -> str:
    """Fact Checker REVIEW_REQUIRED(複合Voice帰属)の、今回のA2に限る
    ユーザー確認済み扱いの承認記録(record_human_approval()相当、新規
    audit record)。record_human_approval()自体[er003_v1_n3_01_assemble.py、
    無変更]は音声segmentのASR検証state向けに設計されており、Fact
    Checkerのtext QA verdictを扱う本用途には意味的に合わないため、
    同じ「明示的な承認記録を書面で残す」思想の専用recordを新規に作る
    (対象=A2本文の複合Voice帰属、恒久運用にはしない旨を明記)。"""
    article_text = open(f"{r02.A2_DIR}/article.md", encoding="utf-8").read()
    path = f"{r02.AUDIT_DIR}/fact_checker_review_required_human_approval_04.json"
    record = {
        "management_id": "EDITORIAL-B-FAMILY-VOICES-A2-SLOWDOWN-AND-KEYPHRASE-REGEN-04",
        "approved_by": "user", "approved_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "fact_checker_verdict": "REVIEW_REQUIRED",
        "scope": "A2本文の複合Voice帰属(Voice A/Bの一人称語り、実在の個人発言ではないB-Family "
                 "genre自体の性質に起因するunsupported_specific_claims)",
        "article_sha256": hashlib.sha256(article_text.encode("utf-8")).hexdigest(),
        "note": "2026-09-08ユーザー決定・今回限り・恒久運用にしない(B-Family genre全体の "
                "REVIEW_REQUIRED扱いを恒久ルール化する決定ではない)。",
    }
    r02.save_json(path, record)
    print(f"[REGEN04-RUNNER] Fact Checker REVIEW_REQUIRED 人間承認記録: {path}")
    return path


def main() -> None:
    _copy_baseline()
    cl.install(r02.COST_LOG_PATH)

    resolution = r02.load_json(f"{r02.AUDIT_DIR}/voice_resolution.json")
    voice_a, voice_b = resolution["voice_a"], resolution["voice_b"]
    reasons = resolution["reasons"]

    voice_regen = _regenerate_voice_bodies(voice_a, voice_b)
    stay_put_comparison = _regenerate_stay_put_key_phrase()
    fact_checker_approval_path = _record_fact_checker_human_review_approval()

    assemble_summary = r02.run_assembly(voice_a, voice_b)
    if assemble_summary.get("status") != "OK":
        print(f"[REGEN04-RUNNER] Assembly status={assemble_summary.get('status')}のためPlayerを生成しません。")
        return

    parts = r02.load_json(f"{r02.A2_DIR}/parts.json")
    support_texts = r02.load_json(f"{r02.A2_DIR}/a2_support_texts.json")
    timeline = r02.load_json(f"{r02.AUDIT_DIR}/timeline.json")
    player_path = r02.build_player_html(assemble_summary, timeline, parts, support_texts, voice_a, voice_b,
                                         reasons, stay_put_comparison=stay_put_comparison)
    print(f"[REGEN04-RUNNER] player.html: {os.path.abspath(player_path)}")

    jpy, by_provider = r02.compute_cost_jpy_so_far()
    print(f"[REGEN04-RUNNER] 完了。今回の追加TTS費用(_04独自ログ)={jpy:.4f} JPY by_provider={by_provider}")
    print(f"[REGEN04-RUNNER] Voice A/B diff table: {voice_regen['diff_table']}")
    print(f"[REGEN04-RUNNER] stay put比較: adopted={stay_put_comparison['adopted']}")
    print(f"[REGEN04-RUNNER] Fact Checker承認記録: {fact_checker_approval_path}")
    print(f"[REGEN04-RUNNER] Assembly: duration={assemble_summary['duration_seconds']}s "
          f"peak={assemble_summary['peak']} clipping={assemble_summary['clipping_detected']}")


if __name__ == "__main__":
    main()
