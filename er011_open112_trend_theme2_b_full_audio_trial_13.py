# ============================================================
# er011_open112_trend_theme2_b_full_audio_trial_13.py
# OPEN-112-TREND-THEME2-B-A2-B1-FULL-AUDIO-TRIAL-13
# ============================================================
# 目的: Trial-12で生成済みのTheme 2 B条件(Engagement根底指示+Reference
# Digest)A2/B1 article.md(本文は一切変更しない)を、既存Production音声
# 経路を無変更のまま使い、Preview・Key Phrase・Comment等を含む完成形の
# episode音声にする(Trial音声。Production採用判断はしない)。
#
# Production変更: なし。以下の本番関数をすべて無変更のまま呼び出す。
#   - er006_pool_pilot_01_support.py::run_support_for_theme()
#       (内部でer003_v1_n3_01_scaffold_generate.py::split_article_text/
#       run_b1_scaffold/run_a2_scaffold/run_key_phrasesを無変更で呼ぶ)
#   - er003_v1_n3_01_tts_generate.py::generate_b1_segments/generate_a2_segments
#   - er003_v1_n3_01_assemble.py::stage_assemble_b1/stage_assemble_a2
#     (Audio Validation Gate・Human Review Lockはこの内部で自動発火。
#     このscriptからは一切override・fallback追加・上限緩和を行わない)
#
# Topic Masterへの登録は行わない(Theme 2はTopic Master未登録のまま)。
# JAPANESE_TITLES辞書への実行時追記は、er006_pool_pilot_01_audio.pyで
# 確立済みの既存パターン(production側ファイル自体は無変更、dictへの
# 追記のみ)をそのまま踏襲する。
#
# 到達してよいStatus: USER_FINAL_AUDIO_REVIEW_REQUIRED / USER_DECISION_REQUIRED
# のみ。Gate/Lockで止まった場合はD4に従い、override・追加fallback・
# human_approved_segments.json等による手動unblockを一切行わずSTOPする。

from __future__ import annotations

import json
import os
import shutil
import sys
import time
import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er005_cost_logger as cl
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_n3_01_assemble as asm
import er006_pool_pilot_01_support as sup

THEME_ID = "open112_trend_theme2_b_full_audio_trial_13"
OUT_DIR = f"er011_output/{THEME_ID}"

TRIAL12_DIR = "er011_output/open112_trend_theme2_b_a2_b1_text_trial_12"
SOURCE_ARTICLES = {
    "b1b": f"{TRIAL12_DIR}/b1b_run01/article.md",
    "a2": f"{TRIAL12_DIR}/a2_run01/article.md",
}
LEDGER_PATH = f"{TRIAL12_DIR}/research/theme2_verified_fact_ledger_CORRECTED_trial12.txt"

# ER-006-MASTER-AUDIO-STORE-01パターン踏襲(er006_pool_pilot_01_audio.py
# 参照)。production側のtts_gen.JAPANESE_TITLESファイル自体は変更せず、
# 実行時にdictへ本Trial専用の1エントリだけ追記する。原文タイトル
# "Young Japan Wants Slower Trips. The Plans Are Still Short" の直訳
# (新しい主張・数字を追加しない、Preview系の答え先出し原則にも抵触しない
# 記事タイトルの日本語化)。
JAPANESE_TITLE = "「ゆっくりした旅」を求める若い世代、旅の計画はまだ短い"
tts_gen.JAPANESE_TITLES.update({THEME_ID: JAPANESE_TITLE})


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def prepare_input_articles() -> None:
    """Trial-12のarticle.mdをそのまま(1バイトも変更せず)OUT_DIR配下へ
    コピーする。Production経路(run_support_for_theme)がout_dir/{label}/
    article.mdを読む設計のため、コピー先のディレクトリ構造だけ合わせる。"""
    for label, src in SOURCE_ARTICLES.items():
        dst_dir = f"{OUT_DIR}/{label}"
        os.makedirs(f"{dst_dir}/audit", exist_ok=True)
        shutil.copyfile(src, f"{dst_dir}/article.md")
        src_text = load_text(src)
        dst_text = load_text(f"{dst_dir}/article.md")
        assert src_text == dst_text, f"article.mdコピー時に内容が変化しました: {label}"
    print(f"[TRIAL-13] article.md(B1/A2とも)をTrial-12から無変更でコピーしました。")


def run_support_stage(client) -> dict:
    ledger_text = load_text(LEDGER_PATH)
    t0 = time.time()
    result = sup.run_support_for_theme(client, THEME_ID, OUT_DIR, ledger_text, blueprint=None)
    elapsed = round(time.time() - t0, 2)
    print(f"[TRIAL-13] Support stage完了。elapsed={elapsed}s")
    return {"result": result, "elapsed": elapsed}


def run_audio_stage() -> dict:
    """er006_pool_pilot_01_audio.py::run_audio_for_theme()と同じ本番関数
    呼び出しだが、B1側のAudio Validation Gate(stage_assemble_b1)が
    RuntimeErrorで止まってもA2側(stage_assemble_a2)は独立して実行できる
    よう、assembleだけ個別にtry/exceptで囲む(ユーザー決定D4: B1がSTOPして
    もA2が安全に独立実行可能なら実施してよい)。TTS生成(generate_b1_
    segments/generate_a2_segments)はそもそも例外を投げない設計
    (STOPPEDはsegment単位のstatus値として返る)。"""
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    timing = {}
    out = {}

    t0 = time.time()
    with cl.logging_context(THEME_ID, "tts_b1"):
        out["b1_tts"] = tts_gen.generate_b1_segments(theme)
    timing["tts_b1"] = round(time.time() - t0, 2)

    t1 = time.time()
    with cl.logging_context(THEME_ID, "tts_a2"):
        out["a2_tts"] = tts_gen.generate_a2_segments(theme)
    timing["tts_a2"] = round(time.time() - t1, 2)

    t2 = time.time()
    try:
        with cl.logging_context(THEME_ID, "assemble_b1"):
            out["b1_assemble"] = asm.stage_assemble_b1(theme)
    except RuntimeError as e:
        out["b1_assemble"] = {"status": "GATE_BLOCKED", "error": str(e)}
        print(f"[TRIAL-13] B1 Assemble GATE_BLOCKED: {e}")
    timing["assemble_b1"] = round(time.time() - t2, 2)

    t3 = time.time()
    try:
        with cl.logging_context(THEME_ID, "assemble_a2"):
            out["a2_assemble"] = asm.stage_assemble_a2(theme)
    except RuntimeError as e:
        out["a2_assemble"] = {"status": "GATE_BLOCKED", "error": str(e)}
        print(f"[TRIAL-13] A2 Assemble GATE_BLOCKED: {e}")
    timing["assemble_a2"] = round(time.time() - t3, 2)

    with open(f"{OUT_DIR}/audio_timing.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)

    print(f"[TRIAL-13] Audio stage完了。timing={timing}")
    print(f"  B1 TTS: {out['b1_tts']['segment_status']}")
    print(f"  A2 TTS: {out['a2_tts']['segment_status']}")
    print(f"  B1 Assemble: {out['b1_assemble']}")
    print(f"  A2 Assemble: {out['a2_assemble']}")
    return {"out": out, "timing": timing}


def support_stage_already_done() -> bool:
    """OPEN-112-TREND-THEME2-B-A2-B1-FULL-AUDIO-TRIAL-13(Sonnet 2回目・
    再開)専用のresume判定。sup.run_support_for_theme()自体には既存出力の
    再利用/skip機構が無く(Production側は無変更のためここでは変更しない)、
    無条件に再実行するとLLMでSupport文面を再生成してしまう。これは(a)
    無駄な追加課金だけでなく、(b) 生成結果が非決定的なため本文が変わり
    うる = canonical_text_sha256が変わり、1回目Sonnet実行で既にRESOLVED
    済みのB1 preview/comment_1-4等のReview Lockキャッシュを無効化して
    しまう(再TTSを誘発する)リスクがある。そのため、両levelのsupport
    出力ファイルが既に存在する場合はSupport stageを丸ごとskipし、
    Audio stage(TTS/ASR、既存のReview Lock機構により1回目で成功済みの
    segmentは自動的に0 API callで再利用される)へ直接進む。この判定は
    Trial script内だけの追加であり、Production関数(sup.run_support_for_
    theme/tts_gen.generate_*_segments/asm.stage_assemble_*)は一切変更
    しない。"""
    required = [
        f"{OUT_DIR}/support_stage_summary.json",
        f"{OUT_DIR}/b1b/b1_support_texts.json",
        f"{OUT_DIR}/b1b/parts.json",
        f"{OUT_DIR}/b1b/key_phrases/keywords_canonicalized.json",
        f"{OUT_DIR}/a2/a2_support_texts.json",
        f"{OUT_DIR}/a2/parts.json",
        f"{OUT_DIR}/a2/key_phrases/keywords_canonicalized.json",
    ]
    return all(os.path.exists(p) for p in required)


def run_assemble_only_stage() -> dict:
    """Sonnet 3回目(2026-09-06)追加。generate_b1_segments/generate_a2_
    segmentsを再度呼ぶと、review_lock.guarded_generateはRESOLVED済み
    segmentもproceed=Trueを返す設計(HUMAN_REVIEW_REQUIREDのみブロック)
    のため、既にRESOLVED済みのsegmentまでTTS/ASRが再実行され二重課金に
    なることが実測で判明した(topic_intro/preview/comment_1-4が2回目の
    resume runで再課金された)。Assembly(asm.stage_assemble_b1/
    stage_assemble_a2)自体はnarration wavファイルを読み込むだけで新規
    TTS呼び出しを行わないため、generate_*_segmentsを呼ばずAssemblyだけを
    直接呼ぶ。Production関数(stage_assemble_b1/stage_assemble_a2)は
    無変更で呼ぶ。Audio Validation Gate(verify_episode_audio_validation_
    gate)が検出するSTOPPED/HUMAN_REVIEW_REQUIRED segmentへのoverride・
    fallbackはここでも一切行わない(D4)。"""
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    timing = {}
    out = {}

    t2 = time.time()
    try:
        with cl.logging_context(THEME_ID, "assemble_b1"):
            out["b1_assemble"] = asm.stage_assemble_b1(theme)
    except RuntimeError as e:
        out["b1_assemble"] = {"status": "GATE_BLOCKED", "error": str(e)}
        print(f"[TRIAL-13][ASSEMBLE-ONLY] B1 Assemble GATE_BLOCKED: {e}")
    timing["assemble_b1"] = round(time.time() - t2, 2)

    t3 = time.time()
    try:
        with cl.logging_context(THEME_ID, "assemble_a2"):
            out["a2_assemble"] = asm.stage_assemble_a2(theme)
    except RuntimeError as e:
        out["a2_assemble"] = {"status": "GATE_BLOCKED", "error": str(e)}
        print(f"[TRIAL-13][ASSEMBLE-ONLY] A2 Assemble GATE_BLOCKED: {e}")
    timing["assemble_a2"] = round(time.time() - t3, 2)

    with open(f"{OUT_DIR}/audio_timing_assemble_only.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)

    print(f"[TRIAL-13][ASSEMBLE-ONLY] 完了。timing={timing}")
    print(f"  B1 Assemble: {out['b1_assemble']}")
    print(f"  A2 Assemble: {out['a2_assemble']}")
    return {"out": out, "timing": timing}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log_trial13.jsonl")

    if "--assemble-only" in sys.argv:
        print("[TRIAL-13][ASSEMBLE-ONLY] narration segment再生成をskipし、"
              "既存の検証済みwavファイルだけを使ってAssembly(stage_assemble_b1/"
              "stage_assemble_a2)のみを実行します(article.mdコピー・Support stage・"
              "generate_*_segmentsは呼びません)。")
        summary = run_assemble_only_stage()
        with open(f"{OUT_DIR}/audio_stage_summary_assemble_only.json", "w", encoding="utf-8") as f:
            json.dump(summary["out"], f, ensure_ascii=False, indent=2, default=str)
        print("[TRIAL-13][ASSEMBLE-ONLY] 完了。")
        return

    prepare_input_articles()

    client = sc.get_client()

    if support_stage_already_done():
        print("[TRIAL-13][RESUME] Support stage出力(b1b/a2とも support_texts.json・"
              "parts.json・key_phrases/keywords_canonicalized.json)が既に存在するため、"
              "Support stageの再実行をskipし、Audio stageから再開します"
              "(既存TTS/ASR Review Lockにより1回目で成功済みのsegmentは再課金なしで再利用されます)。")
    else:
        support_summary = run_support_stage(client)
        with open(f"{OUT_DIR}/support_stage_summary.json", "w", encoding="utf-8") as f:
            json.dump(support_summary["result"], f, ensure_ascii=False, indent=2, default=str)

    audio_summary = run_audio_stage()
    with open(f"{OUT_DIR}/audio_stage_summary.json", "w", encoding="utf-8") as f:
        json.dump(audio_summary["out"], f, ensure_ascii=False, indent=2, default=str)

    print("[TRIAL-13] 全stage完了。")


if __name__ == "__main__":
    main()
