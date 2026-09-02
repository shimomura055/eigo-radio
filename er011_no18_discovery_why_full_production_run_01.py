# ============================================================
# er011_no18_discovery_why_full_production_run_01.py
# ER-011-NO18-DISCOVERY-WHY-FULL-PRODUCTION-RUN-01
# ============================================================
# No.9までにProduction Wiredされた現行仕様(Storytelling First・No Jargon・
# Evidence Compression方式C・Point overlap QA + Diagnostic Full Retry・
# Fact Checker policy[FAIL=blocking/REVIEW_REQUIRED=advisory]・Ledger
# Deviation Checker[hook-aware]・Local Rewrite Loop・Formatting禁止・
# Key Phrase Minimal->English Lock retry[function-word/article reduction
# 込み]・A2 6% slowdown・外来語検出ゲート・固有名詞ASR音韻類似度チェック・
# Audio Validation Gate等)を、新規Topic No.18「Why Is It So Hard to
# Ignore a Notification?」(Discovery/Why型、POOL_TOPIC_MASTER.md No.18
# として新規登録)で正式Production実行するための専用runner。
#
# er009_n1_production_integration_01.py(No.9正式Production runner)を
# テンプレートとし、Topic/出力先だけを差し替える。パイプライン自体は
# 作り直さず、既存の共有関数(er006_pool_pilot_01_research/writer/
# support.py、er003_v1_n3_01_tts_generate.py、er003_v1_n3_01_assemble.py)
# をそのままimportして使う(旧script・DEV専用経路・手動bypass・一時
# fixtureは使わない)。No.9限定の`default` one-off asset・No.9固有の
# article overrideは一切継承しない(ユーザー指示、ER-011-NO18-01 §5)。
#
# 【今回の指示(ユーザー、2026-09-02)】TTSは同期型(Standard同期TTS経路、
# enable_sync_tts_mode)を使う。Production Batch経路(er006_batch_tts_
# wiring_01.py)自体は一切変更せず、このプロセス内でのみモジュール属性を
# 差し替える(disable_sync_tts_modeで対で復元)。No.9で使われたのと同一の
# 差し替え方式をそのまま再利用する。

from __future__ import annotations

import json
import time

import er005_cost_logger as cl

THEME_ID = "pool_n18_notifications"
OUT_DIR = f"er006_output/pool_pilot_01/{THEME_ID}"
TITLE_EN = "Why Is It So Hard to Ignore a Notification?"
TOPIC_JA = (
    "スマートフォンの通知音や振動が、なぜ実際に画面を見なくても集中を乱すのかを"
    "扱う。査読付き実験研究(Upshaw, Stevens, Ganis, Zabelina、2022年11月17日、"
    "PLOS ONE誌)は、大学生73名にNavon文字課題(960試行)を行わせながら、通知音・"
    "無関係な統制音のいずれかを試行に重ねた。行動データでは通知音を伴った試行の"
    "方が統制音の試行より反応が有意に遅く、脳波(EEG)データでは通知音の方が"
    "注意資源の追加投入を示すN2成分の振幅が有意に大きかった。参加者は画面を見ても"
    "触ってもいないにもかかわらず、通知音そのものが自動的・不随意的に注意を奪い、"
    "課題遂行のために追加の認知制御努力を強いていたことを示している。もう一つの"
    "査読付き研究(Skowronek, Seifert, Lindberg、Paderborn大学、2023年6月8日、"
    "Scientific Reports誌)は、大学生42名を対象に、電源を切ったスマートフォンを"
    "机上に置いた状態と別室へ移した状態とで集中力テスト(d2-Rテスト)の成績を比較し、"
    "スマートフォンが机上にあるだけで注意成績(99.71 対 108.95)・処理速度"
    "(98.48 対 108.57)がいずれも有意に低下することを示した。通知は一度も鳴って"
    "いないにもかかわらず、スマートフォンの物理的な存在そのものが限られた注意資源の"
    "一部を消費し続けており、実際に通知が鳴る前から「いつでも反応できる」構えを"
    "強いられている可能性を示す。この2つの研究を背景に、Pew Research Centerの"
    "全米調査(2018年8月22日発表、10代743人・保護者1,058人を対象に2018年3月7日"
    "から4月10日にかけて実施)は、10代の72%が起床後まず通知やメッセージを確認"
    "すると回答し、約4割が携帯電話を手元に持っていないと不安・孤独・動揺を感じると"
    "回答したことを報告しており、通知確認をやめにくいという体験が、ごく一部の人の"
    "特殊な習慣ではなく、幅広い年齢層に共通する日常的な現象であることを示している。"
)
JAPANESE_TITLE_JA = "通知を無視するのが、なぜこんなに難しいのか"


# ============================================================
# 【今回指示】Standard同期TTSモード切替(No.9・er009_n1_production_
# integration_01.pyと同一方式)
# ============================================================
def enable_sync_tts_mode():
    """No.18はユーザー指示によりStandard同期TTSを使う(Production Batch
    経路は変更しない、このプロセス内でのみモジュール属性を差し替える)。"""
    import er006_batch_tts_wiring_01 as batch_wiring
    import er003_b1_p7a_audio as p7a

    def _sync_call_fn_adapter(model_name, voice_name, client=None, output_path=None, **_ignored):
        return p7a.make_tts_call_fn_for_model(model_name, voice_name, client=client)

    if not hasattr(batch_wiring, "_er011_original_make_batch_tts_call_fn"):
        batch_wiring._er011_original_make_batch_tts_call_fn = batch_wiring.make_batch_tts_call_fn
    batch_wiring.make_batch_tts_call_fn = _sync_call_fn_adapter
    print("[ER-011-NO18] 同期TTSモードへ切替済み(Batch APIは使用しない、ユーザー指示によるNo.18限定)")


def disable_sync_tts_mode():
    import er006_batch_tts_wiring_01 as batch_wiring
    if hasattr(batch_wiring, "_er011_original_make_batch_tts_call_fn"):
        batch_wiring.make_batch_tts_call_fn = batch_wiring._er011_original_make_batch_tts_call_fn
        print("[ER-011-NO18] Batch TTSモードへ復元済み")


# ============================================================
# Stage 1: Research(Evidence Pack -> VFL -> Verification)
# ============================================================
def run_research_stage() -> dict:
    import er006_pool_pilot_01_research as research_mod
    import er006_pool_pilot_01_ledger as ledger_mod

    sources = json.load(open(f"{OUT_DIR}/research/raw_sources.json", encoding="utf-8"))["sources"]
    t0 = time.time()
    with cl.logging_context(THEME_ID, "research"):
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
    with cl.logging_context(THEME_ID, "writer"):
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
    with cl.logging_context(THEME_ID, "support"):
        result = support_mod.run_support_for_theme(client, THEME_ID, OUT_DIR, ledger_text, blueprint=None)
    elapsed = round(time.time() - t0, 1)
    print(f"[{THEME_ID}] Baseline Support完了(blueprint=None, comment anchor不使用)。elapsed={elapsed}s")
    return result


# ============================================================
# Stage 4: TTS(No.18指定Standard同期API) + Assembly(B1/A2)
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
    print(f"[{THEME_ID}] Audio完了(No.18指定Standard同期TTS)。timing={timing}")
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
        print("usage: er011_no18_discovery_why_full_production_run_01.py [research|writer|support|audio]")
