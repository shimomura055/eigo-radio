# ============================================================
# er009_n1_production_integration_01.py
# ER-009-N1-PRODUCTION-INTEGRATION-01
# ============================================================
# No.8までにProduction Wiredした現行仕様(Point overlap threshold 0.40・
# Writer Point Balance Prompt強化版・Evidence Compression方式C・
# Directional Fact Precheck・Fact Checker retry cap・A2 6% slowdown・
# 外来語検出ゲート・固有名詞ASR音韻類似度チェック・Audio Validation Gate等)
# を、新規Topic No.9「Why the Tip Screen Always Suggests More Than You
# Meant to Give」で実地統合検証するための専用runner。
#
# er008_n8_baseline_run_01.py(No.8正式Production生成)をテンプレートとし、
# Topic/出力先だけを差し替えて実行する。パイプライン自体は作り直さず、
# 既存の共有関数(er006_pool_pilot_01_research/writer/support.py、
# er003_v1_n3_01_tts_generate.py、er003_v1_n3_01_assemble.py)をそのまま
# importして使う(旧script・DEV専用経路・手動bypass・一時fixtureは使わない)。
#
# 【今回だけの指示(ユーザー、2026-08-29)】No.9は実ユーザー検証用のため、
# TTSはProduction Batch API(client.batches.create())ではなく、No.7の
# Pilot検証(er008_n7_pilot_run_01.py)で使われていたStandard同期TTS経路
# (enable_sync_tts_mode)を使う。Production Batch経路(er006_batch_tts_
# wiring_01.py)自体は一切変更せず、このプロセス内でのみモジュール属性を
# 差し替える(disable_sync_tts_modeで対で復元)。音声品質・ASR Cascade・
# Validator・Disfluency QA・Assembly Gateの基準はProductionと同一のまま
# 変更しない(TTS呼び出し方式だけがStandardに変わる)。
#
# 現行仕様として自動的に適用されるもの(コード変更不要、共有関数側に
# 既定Trueで組み込み済み):
#   - Evidence Compression方式C(apply_evidence_compression_editor既定True)
#   - Directional Fact Precheck(apply_directional_fact_precheck既定True)
#   - A2英語7segmentへの6% slowdown(generate_a2_segment_with_slowdown)
#   - 外来語検出ゲート(classify_foreign_tokens_in_japanese_text)
#   - 固有名詞ASR音韻類似度チェック(entity phonetic corroboration)
#   - Audio Validation Gate(verify_episode_audio_validation_gate)
#   - Point overlap threshold 0.40 + Writer Point Balance Prompt強化版
#     (er003_v1_n3_01_articles_generate.pyのinstruction定数に既に反映済み)

from __future__ import annotations

import json
import time

import er005_cost_logger as cl

THEME_ID = "pool_n9_tip_screens"
OUT_DIR = f"er006_output/pool_pilot_01/{THEME_ID}"
TITLE_EN = "Why the Tip Screen Always Suggests More Than You Meant to Give"
TOPIC_JA = (
    "レジやレストランの会計画面で表示される「おすすめチップ額」が、なぜ実際に払う"
    "つもりだった額より高めに設定されがちなのかを扱う。ニューヨーク市タクシーの"
    "クレジットカード決済画面1300万件超を分析した査読付き学術研究(Haggag and Paci、"
    "2014年、American Economic Journal: Applied Economics誌、運賃が15ドルを境に"
    "表示される推奨チップ率の組み合わせが不連続に変わることを利用したregression"
    "discontinuity分析)は、画面が最初に示す推奨チップ率(default)が実際のチップ額に"
    "大きな因果的影響を持つことを示した一方、推奨率を高く設定しすぎると、逆に"
    "クレジットカードでのチップを一切払わない客の割合が増えるという副作用も報告した。"
    "Rutgers大学New Jersey State Policy Labの政策レポート(Michael Lahr、2022年)は、"
    "米国の飲食店チップ相場が1970年代初頭の約10〜15%から1990年代末には約20%へ上昇し、"
    "現在のデジタル決済画面では35%もの推奨額が示されることがあると指摘し、現金の"
    "チップ皿からデジタル画面へ移行したことで、店員の目の前でチップ率を選ぶという"
    "社会的プレッシャー(「罪悪感チップ」)が生まれたと分析する。こうした状況への"
    "消費者の反発は2026年に入り強まっており、飲食店技術企業Popmenuが2026年4月に"
    "発表した消費者調査(Popmenu、2026年4月8日発表)では、回答者の78%が「チップの"
    "慣行がばかげたものになった」と回答し、44%が前年よりチップを減らしたと回答、"
    "デジタル画面でチップを促された際に「払わなければ」と感じる人の割合も2025年9月の"
    "66%から2026年には59%へ低下、画面上の推奨額ではなく自分でカスタム額(多くは"
    "より低い額)を選ぶ人が36%に上るなど、推奨チップ画面そのものへの疲弊が"
    "広がっていることを報告している。"
)
JAPANESE_TITLE_JA = "会計画面がいつも「多め」のチップを提案してくる理由"


# ============================================================
# 【今回限定】Standard同期TTSモード切替(er008_n7_pilot_run_01.pyと同一方式)
# ============================================================
def enable_sync_tts_mode():
    """No.9はユーザー指示によりStandard同期TTSを使う(Production Batch
    経路は変更しない、このプロセス内でのみモジュール属性を差し替える)。"""
    import er006_batch_tts_wiring_01 as batch_wiring
    import er003_b1_p7a_audio as p7a

    def _sync_call_fn_adapter(model_name, voice_name, client=None, output_path=None, **_ignored):
        return p7a.make_tts_call_fn_for_model(model_name, voice_name, client=client)

    if not hasattr(batch_wiring, "_er009_original_make_batch_tts_call_fn"):
        batch_wiring._er009_original_make_batch_tts_call_fn = batch_wiring.make_batch_tts_call_fn
    batch_wiring.make_batch_tts_call_fn = _sync_call_fn_adapter
    print("[ER-009-N1] 同期TTSモードへ切替済み(Batch APIは使用しない、ユーザー指示によるNo.9限定)")


def disable_sync_tts_mode():
    import er006_batch_tts_wiring_01 as batch_wiring
    if hasattr(batch_wiring, "_er009_original_make_batch_tts_call_fn"):
        batch_wiring.make_batch_tts_call_fn = batch_wiring._er009_original_make_batch_tts_call_fn
        print("[ER-009-N1] Batch TTSモードへ復元済み")


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
# Stage 2: A2/B1 Writer(Baseline、blueprint=None)
# ============================================================
def run_writer_stage_baseline() -> dict:
    import er003_v1_en_direct_ab_01_generate as ab01
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_writer as writer_mod

    client = vfl01.get_client()
    master_full_text = ab01.load_master_full_text()
    ledger_path = f"{OUT_DIR}/research/verified_fact_ledger.txt"

    t0 = time.time()
    result = writer_mod.run_writer_for_theme(
        client, master_full_text, THEME_ID, TOPIC_JA, ledger_path, OUT_DIR, blueprint=None)
    elapsed = round(time.time() - t0, 1)
    print(f"[{THEME_ID}] Baseline Writer完了(blueprint=None)。elapsed={elapsed}s")
    for label, r in result["results"].items():
        print(f"  {label}: status={r.get('status')} fact_verdict={r.get('fact_verdict')} "
              f"ledger_status={r.get('ledger_status')}")
    return result


# ============================================================
# Stage 3: Support(Preview/Comment1-4、Baseline、blueprint=None)
# ============================================================
def run_support_stage_baseline() -> dict:
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er006_pool_pilot_01_support as support_mod

    client = vfl01.get_client()
    ledger_text = open(f"{OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()

    t0 = time.time()
    result = support_mod.run_support_for_theme(client, THEME_ID, OUT_DIR, ledger_text, blueprint=None)
    elapsed = round(time.time() - t0, 1)
    print(f"[{THEME_ID}] Baseline Support完了(blueprint=None, comment anchor不使用)。elapsed={elapsed}s")
    return result


# ============================================================
# Stage 4: TTS(No.9限定Standard同期API) + Assembly(B1/A2)
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
        timing["tts_b1"] = round(time.time() - t0, 2)

        t1 = time.time()
        with cl.logging_context(THEME_ID, "tts_a2_sync"):
            a2_tts_summary = tts_gen.generate_a2_segments(theme)
        timing["tts_a2"] = round(time.time() - t1, 2)
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

    with open(f"{OUT_DIR}/audio_timing.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] Audio完了(No.9限定Standard同期TTS)。timing={timing}")
    print(f"  B1 TTS: {b1_tts_summary['segment_status']}")
    print(f"  A2 TTS: {a2_tts_summary['segment_status']}")
    print(f"  B1 Assemble: {b1_assemble_summary}")
    print(f"  A2 Assemble: {a2_assemble_summary}")
    return {"b1_tts": b1_tts_summary, "a2_tts": a2_tts_summary,
            "b1_assemble": b1_assemble_summary, "a2_assemble": a2_assemble_summary, "timing": timing}


if __name__ == "__main__":
    import sys
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    stage = sys.argv[1] if len(sys.argv) > 1 else None
    if stage == "research":
        run_research_stage()
    elif stage == "writer":
        run_writer_stage_baseline()
    elif stage == "support":
        run_support_stage_baseline()
    elif stage == "audio":
        run_audio_stage()
    else:
        print("usage: er009_n1_production_integration_01.py [research|writer|support|audio]")
