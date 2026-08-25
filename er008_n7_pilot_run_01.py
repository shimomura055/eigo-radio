# ============================================================
# er008_n7_pilot_run_01.py
# ER-008-N7-SHARED-POINT-BLUEPRINT-3LEVEL-PILOT-01
# ============================================================
# No.7("Assigned Desks Are Back in Some Offices")を対象に、正式Production
# 相当Pipeline(Research -> Evidence Pack/VFL -> Shared Point Blueprint ->
# B1/A2 Writer -> Fact Check/Ledger Deviation -> Support -> TTS/ASR)を
# 実行するPilot専用runner。
#
# 【今回だけの例外】TTS呼び出し方式のみ、Gemini Batch APIではなく同期
# (client.models.generate_content)を明示的に使う(DEV/VALIDATION用、
# タスク仕様「1. 今回のTTS実行モード」)。er006_batch_tts_wiring_01.
# make_batch_tts_call_fnをこのプロセス内でのみ同期版アダプタへ差し替える
# (Production側の各ファイルは一切変更しない、CURRENT_SPECのBatch標準は
# 無変更)。

from __future__ import annotations

import json
import os
import time

import er005_cost_logger as cl

THEME_ID = "pool_n7_assigned_desks"
OUT_DIR = f"er006_output/pool_pilot_01/{THEME_ID}"
TITLE_EN = "Assigned Desks Are Back in Some Offices"
TOPIC_JA = (
    "一部の職場で「固定席(assigned desk)」が戻ってきている。パンデミック後に広まった"
    "hot-desking(固定の机を割り当てず、空いている机を早い者勝ちで使う方式)に対し、"
    "従業員から不満の声が上がっており、Scotiabank・iCapital Network等の企業が、"
    "静かに固定席への回帰を進めている。背景には、固定席のある従業員の方が「職場への"
    "帰属感」や「集中して働けている感覚」が高いという調査結果や、hot-deskingが従業員の"
    "満足度・職場品質の認識を一貫して下げるという複数の研究レビューがある。一方、"
    "企業全体としては机の共有比率(1人1台の割合)は依然として低下傾向にあり、固定席"
    "回帰は一部の企業・部署にとどまる動きである。"
)


def enable_sync_tts_mode():
    """今回のPilotに限り、Batch TTS call_fn factoryを同期版へ差し替える。
    Production側のファイル(er006_batch_tts_wiring_01.py等)は一切変更
    しない(このプロセス内でのモジュール属性差し替えのみ、かつ復元関数
    disable_sync_tts_modeを対で提供する)。"""
    import er006_batch_tts_wiring_01 as batch_wiring
    import er003_b1_p7a_audio as p7a

    def _sync_call_fn_adapter(model_name, voice_name, client=None, output_path=None, **_ignored):
        return p7a.make_tts_call_fn_for_model(model_name, voice_name, client=client)

    if not hasattr(batch_wiring, "_er008_original_make_batch_tts_call_fn"):
        batch_wiring._er008_original_make_batch_tts_call_fn = batch_wiring.make_batch_tts_call_fn
    batch_wiring.make_batch_tts_call_fn = _sync_call_fn_adapter
    print("[ER-008-N7-PILOT] 同期TTSモードへ切替済み(Batch APIは使用しない、DEV/VALIDATION限定)")


def disable_sync_tts_mode():
    import er006_batch_tts_wiring_01 as batch_wiring
    if hasattr(batch_wiring, "_er008_original_make_batch_tts_call_fn"):
        batch_wiring.make_batch_tts_call_fn = batch_wiring._er008_original_make_batch_tts_call_fn
        print("[ER-008-N7-PILOT] Batch TTSモードへ復元済み")


# ============================================================
# Stage 1: Research(Evidence Pack -> VFL -> Verification)
# ============================================================
def run_research_stage() -> dict:
    import er006_pool_pilot_01_research as research_mod
    import er006_pool_pilot_01_ledger as ledger_mod

    sources = json.load(open(f"{OUT_DIR}/research/raw_sources.json", encoding="utf-8"))["sources"]
    t0 = time.time()
    result = research_mod.run_research_for_theme(THEME_ID, f"{OUT_DIR}/research", TITLE_EN, sources)
    ledger_text = ledger_mod.build_ledger_text_from_vfl(
        result["vfl"]["parsed"], result["evidence_pack"]["parsed"], TITLE_EN)
    ledger_path = f"{OUT_DIR}/research/verified_fact_ledger.txt"
    with open(ledger_path, "w", encoding="utf-8") as f:
        f.write(ledger_text)
    elapsed = round(time.time() - t0, 1)
    print(f"[{THEME_ID}] Research+Ledger完了。elapsed={elapsed}s ledger_path={ledger_path}")
    return {"ledger_path": ledger_path, "elapsed": elapsed, "research_result": result}


# ============================================================
# Stage 2: Shared Point Blueprint(実LLM初回生成)
# ============================================================
def run_blueprint_stage() -> dict:
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_model_routing_contract_01 as routing
    import er008_shared_point_blueprint_01 as blueprint_mod
    import er008_point_blueprint_validator_01 as validator_mod

    ledger_path = f"{OUT_DIR}/research/verified_fact_ledger.txt"
    verified_ledger_text = open(ledger_path, encoding="utf-8").read()
    client = vfl01.get_client()

    t0 = time.time()
    with cl.logging_context(THEME_ID, "shared_point_blueprint"):
        model = routing.require_model("SHARED_POINT_BLUEPRINT", routing.WRITER_MODEL)
        result = blueprint_mod.run_blueprint_generation(client, TOPIC_JA, verified_ledger_text, model=model)
    elapsed = round(time.time() - t0, 1)

    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    with open(f"{OUT_DIR}/audit/shared_point_blueprint_raw.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    parsed = dict(result["parsed"])
    parsed["topic_id"] = THEME_ID
    blueprint = blueprint_mod.blueprint_from_dict(parsed)
    with open(f"{OUT_DIR}/shared_point_blueprint.json", "w", encoding="utf-8") as f:
        json.dump(blueprint_mod.blueprint_to_dict(blueprint), f, ensure_ascii=False, indent=2)

    schema_result = validator_mod.validate_blueprint_schema(blueprint)
    with open(f"{OUT_DIR}/audit/shared_point_blueprint_schema_validation.json", "w", encoding="utf-8") as f:
        json.dump({"ok": schema_result.ok,
                    "violations": [v.__dict__ for v in schema_result.violations]}, f, ensure_ascii=False, indent=2)

    print(f"[{THEME_ID}] Blueprint生成完了。elapsed={elapsed}s schema_ok={schema_result.ok} "
          f"input_tokens={result['input_tokens']} output_tokens={result['output_tokens']}")
    if not schema_result.ok:
        for v in schema_result.violations:
            print(f"  [SCHEMA FAIL] {v.check}: {v.message}")
    return {"blueprint": blueprint, "schema_result": schema_result, "elapsed": elapsed,
            "input_tokens": result["input_tokens"], "output_tokens": result["output_tokens"],
            "model": result["model"]}


# ============================================================
# Stage 3: A2/B1 Writer(Shared Point Blueprintを共通入力として渡す)
# ============================================================
def load_blueprint():
    import er008_shared_point_blueprint_01 as blueprint_mod
    parsed = json.load(open(f"{OUT_DIR}/shared_point_blueprint.json", encoding="utf-8"))
    return blueprint_mod.blueprint_from_dict(parsed)


def run_writer_stage() -> dict:
    import er003_v1_en_direct_ab_01_generate as ab01
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_writer as writer_mod

    blueprint = load_blueprint()
    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    ledger_path = f"{OUT_DIR}/research/verified_fact_ledger.txt"

    t0 = time.time()
    result = writer_mod.run_writer_for_theme(
        client, master_full_text, THEME_ID, TOPIC_JA, ledger_path, OUT_DIR, blueprint=blueprint)
    elapsed = round(time.time() - t0, 1)
    print(f"[{THEME_ID}] Writer完了。elapsed={elapsed}s")
    for label, r in result["results"].items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')} fact_usage_report={r.get('fact_usage_report')}")
    return result


# ============================================================
# Stage 4: Structural Validator(A2/B1のfact利用申告をBlueprintと突き合わせる)
# ============================================================
def run_structural_validation_stage() -> dict:
    import er008_point_blueprint_validator_01 as validator_mod

    blueprint = load_blueprint()
    a2_usage = json.load(open(f"{OUT_DIR}/a2/audit/fact_usage_report.json", encoding="utf-8"))
    b1_usage = json.load(open(f"{OUT_DIR}/b1b/audit/fact_usage_report.json", encoding="utf-8"))

    result = validator_mod.validate_topic(blueprint, a2_writer_usage=a2_usage, b1_writer_usage=b1_usage)
    print(f"[{THEME_ID}] Structural Validation(Writer段階): ok={result.ok}")
    for v in result.violations:
        print(f"  [FAIL] {v.check}: {v.message}")
    with open(f"{OUT_DIR}/audit/structural_validation_writer_stage.json", "w", encoding="utf-8") as f:
        json.dump({"ok": result.ok, "violations": [v.__dict__ for v in result.violations]},
                    f, ensure_ascii=False, indent=2)
    return result


# ============================================================
# Stage 5: Support(Preview/Comment1-4)。B1のComment3/4はBlueprintの
# comment_anchorを使う(er003_v1_n3_01_scaffold_generate.run_b1_scaffold
# のblueprint引数経由)。
# ============================================================
def run_support_stage() -> dict:
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_support as support_mod

    blueprint = load_blueprint()
    client = vfl01.get_client()
    ledger_text = open(f"{OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()

    t0 = time.time()
    result = support_mod.run_support_for_theme(client, THEME_ID, OUT_DIR, ledger_text, blueprint=blueprint)
    elapsed = round(time.time() - t0, 1)
    print(f"[{THEME_ID}] Support完了。elapsed={elapsed}s")
    return result


def run_structural_validation_comments_stage() -> dict:
    import er008_point_blueprint_validator_01 as validator_mod

    blueprint = load_blueprint()
    b1_dir = f"{OUT_DIR}/b1b"
    b1_gen = json.load(open(f"{b1_dir}/audit/b1_support_generation.json", encoding="utf-8"))
    c3_refs = (b1_gen.get("comment_3") or {}).get("referenced_fact_ids")
    c4_refs = (b1_gen.get("comment_4") or {}).get("referenced_fact_ids")
    print(f"[{THEME_ID}] Comment 3 referenced_fact_ids={c3_refs}")
    print(f"[{THEME_ID}] Comment 4 referenced_fact_ids={c4_refs}")

    result = validator_mod.check_comment_fact_reference(blueprint, "point_1", c3_refs or [])
    result2 = validator_mod.check_comment_fact_reference(blueprint, "point_2", c4_refs or [])
    ok = result.ok and result2.ok
    print(f"[{THEME_ID}] Structural Validation(Comment段階): ok={ok}")
    for v in result.violations + result2.violations:
        print(f"  [FAIL] {v.check}: {v.message}")
    with open(f"{OUT_DIR}/audit/structural_validation_comment_stage.json", "w", encoding="utf-8") as f:
        json.dump({"ok": ok, "comment_3_refs": c3_refs, "comment_4_refs": c4_refs,
                    "violations": [v.__dict__ for v in (result.violations + result2.violations)]},
                    f, ensure_ascii=False, indent=2)
    return {"ok": ok}


JAPANESE_TITLE_JA = "一部の職場で「固定席」が戻ってきている"


# ============================================================
# Stage 6: TTS(同期モード、DEV/VALIDATION限定) + Assembly(B1/A2)
# ============================================================
def run_audio_stage() -> dict:
    import er003_v1_n3_01_tts_generate as tts_gen
    import er003_v1_n3_01_assemble as asm

    tts_gen.JAPANESE_TITLES.update({THEME_ID: JAPANESE_TITLE_JA})
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    timing = {}

    enable_sync_tts_mode()
    try:
        t0 = time.time()
        with cl.logging_context(THEME_ID, "tts_b1_sync"):
            b1_tts_summary = tts_gen.generate_b1_segments(theme)
        timing["tts_b1_sync"] = round(time.time() - t0, 2)

        t1 = time.time()
        with cl.logging_context(THEME_ID, "tts_a2_sync"):
            a2_tts_summary = tts_gen.generate_a2_segments(theme)
        timing["tts_a2_sync"] = round(time.time() - t1, 2)
    finally:
        disable_sync_tts_mode()

    t2 = time.time()
    with cl.logging_context(THEME_ID, "assemble_b1"):
        b1_assemble_summary = asm.stage_assemble_b1(theme)
    timing["assemble_b1"] = round(time.time() - t2, 2)

    t3 = time.time()
    with cl.logging_context(THEME_ID, "assemble_a2"):
        a2_assemble_summary = asm.stage_assemble_a2(theme)
    timing["assemble_a2"] = round(time.time() - t3, 2)

    with open(f"{OUT_DIR}/audio_timing_sync.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] Audio完了(同期TTS)。timing={timing}")
    print(f"  B1 TTS: {b1_tts_summary['segment_status']}")
    print(f"  A2 TTS: {a2_tts_summary['segment_status']}")
    print(f"  B1 Assemble: {b1_assemble_summary}")
    print(f"  A2 Assemble: {a2_assemble_summary}")
    return {"b1_tts": b1_tts_summary, "a2_tts": a2_tts_summary,
            "b1_assemble": b1_assemble_summary, "a2_assemble": a2_assemble_summary, "timing": timing}


# ============================================================
# Stage 7: Middle/Bridge組み立て(新規TTS無し。A2の本文系segment+B1の
# Preview/Comment1-4を、既に生成済みの同期TTS音声のまま組み合わせる)。
# er003_v1_n3_01_assemble.pyのB1 timeline構造(Charon Comment/Aoede本文の
# 既存pause値)をそのまま踏襲し、本文側の音源だけをA2の音声へ差し替える。
# Production側のassembleファイル自体は変更しない(このPilot専用関数として
# 実装)。
# ============================================================
def build_middle_timeline_and_assemble(theme: dict) -> dict:
    import er002_common as common
    import er003_b1_p9a_audio as p9a
    import er003_v1_n3_01_assemble as asm

    out_dir_a2 = f"{theme['out_dir']}/a2"
    out_dir_b1 = f"{theme['out_dir']}/b1b"
    out_dir_mid = f"{theme['out_dir']}/middle"
    os.makedirs(f"{out_dir_mid}/assembled", exist_ok=True)
    os.makedirs(f"{out_dir_mid}/audit", exist_ok=True)

    a2_sources = asm.load_a2_sources(theme)
    a2_parts = asm.apply_a2_gain(a2_sources)  # A2本文側の既存gain値をそのまま再利用
    b1_sources = asm.load_b1_sources(theme)   # B1のraw(gain前)音源からPreview/Comment1-4のみ使う

    # B1のPreview/Comment1-4を、A2のtarget_rms(a2_parts["gain_report"]["target_rms"])
    # へ合わせ直す(新規TTSではなく、既存音声の音量調整のみ)。
    target_rms = a2_parts["gain_report"]["target_rms"]
    b1_comment_stereo = {}
    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
        mono = b1_sources["b1_segments"][name]
        gain = p9a.compute_gain_for_target_rms(mono, target_rms)
        b1_comment_stereo[name] = p9a.mono_24k_to_stereo_target(mono * gain)

    # Welcome/Preview intro/Key phrases intro/Full story intro/Outroは、
    # B1側のCharon版をtarget_rmsへ合わせ直して使う(voice一貫性のため)。
    b1_shell_stereo = {}
    for name in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro"):
        mono = b1_sources["narration"][name]
        gain = p9a.compute_gain_for_target_rms(mono, target_rms)
        b1_shell_stereo[name] = p9a.mono_24k_to_stereo_target(mono * gain)
    outro_gain = p9a.compute_gain_for_target_rms(b1_sources["outro"]["samples"], p9a.rms(a2_parts["intro"]))
    outro_stereo = (b1_sources["outro"]["samples"] * outro_gain
                     * asm.OUTRO_EXTRA_GAIN_LINEAR * asm.OUTRO_FURTHER_EXTRA_GAIN_LINEAR)

    kp_blocks = asm.build_a2_key_phrase_blocks(a2_parts)  # ER-008推奨: A2 Key Phraseを流用
    kp_labels = tuple(f"Key Phrase {i + 1}" for i in range(len(kp_blocks)))

    seq = [
        ("Intro", a2_parts["intro"]),
        ("Welcome (Charon, B1)", b1_shell_stereo["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro (A2)", a2_parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Japanese title (A2)", a2_parts["japanese_title"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 1", a2_parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro (Charon, B1)", b1_shell_stereo["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Preview (Charon, B1)", b1_comment_stereo["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", a2_parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro (Charon, B1)", b1_shell_stereo["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    for label, block in zip(kp_labels, kp_blocks):
        seq.append((label, block))
    seq += [
        ("Notification 3", a2_parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro (Charon, B1)", b1_shell_stereo["full_story_intro"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 1 (Charon, B1)", b1_comment_stereo["comment_1"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Full Story Part 1 (Aoede, A2)", a2_parts["a2_segments"]["full_story_part1"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 2 (Charon, B1)", b1_comment_stereo["comment_2"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Full Story Part 2 (Aoede, A2)", a2_parts["a2_segments"]["full_story_part2"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 3 (Charon, Bridge, B1)", b1_comment_stereo["comment_3"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Point One cue)", a2_parts["point_notification"]),
        ("Point One semantic heading (Aoede, A2)", a2_parts["a2_segments"]["point_one_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        ("Point One (Aoede, A2)", a2_parts["a2_segments"]["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(asm.NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Point Two cue)", a2_parts["point_notification"]),
        ("Point Two semantic heading (Aoede, A2)", a2_parts["a2_segments"]["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(asm.HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        ("Point Two (Aoede, A2)", a2_parts["a2_segments"]["point_two"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 4 (Charon, B1)", b1_comment_stereo["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("In One Line (Aoede, A2)", a2_parts["a2_segments"]["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(asm.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro (Charon, B1)", outro_stereo),
    ]

    result = asm.assemble_with_timeline(seq)
    assembled = result["assembled"]
    out_path = f"{out_dir_mid}/assembled/English_Your_Way_MIDDLE_{THEME_ID.upper()}.wav"
    common.write_wav_float(out_path, assembled, asm.SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], asm.SR)

    with open(f"{out_dir_mid}/audit/timeline.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": asm.SR, "channels": 2, "new_tts_calls": 0, "new_asr_calls": 0,
        "reused_a2_segment_count": 12, "reused_b1_segment_count": 5,
    }
    with open(f"{out_dir_mid}/run_summary_assemble.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[N7-MIDDLE-ASSEMBLE] status={summary['status']} duration={summary['duration_seconds']} "
          f"peak={summary['peak']} clipping={summary['clipping_detected']} out_path={out_path}")
    return summary


if __name__ == "__main__":
    import sys
    stage = sys.argv[1] if len(sys.argv) > 1 else "research"
    if stage == "research":
        run_research_stage()
    elif stage == "blueprint":
        run_blueprint_stage()
    elif stage == "writer":
        run_writer_stage()
    elif stage == "validate_writer":
        run_structural_validation_stage()
    elif stage == "support":
        run_support_stage()
    elif stage == "validate_comments":
        run_structural_validation_comments_stage()
    elif stage == "audio":
        run_audio_stage()
    elif stage == "middle":
        theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
        build_middle_timeline_and_assemble(theme)
    else:
        print(f"unknown stage: {stage}")
