# ============================================================
# er011_family_a_completion_a2_trend_end_to_end_01_run.py
# 管理ID: FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01(Lane A Step A2)
# ============================================================
# 目的: Wiring後のProduction正式経路(editorial_mode="trend_synthesis"、
# OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01)で既に生成済みの
# Theme2 A2/B1B記事(Key Phrase選定はB1Bのみ完了、A2は未完了)を入力に、
# Production関数のみ(Trialスクリプト経由なし)でScaffold(Preview/
# Comment、記事に対しまだ未実行だったため実行が必要)→Key Phrase(A2の
# み新規実行、B1Bは既存結果をbyte-identical article.mdを確認のうえ再利用)
# →TTS(er003_v1_n3_01_tts_generate.generate_b1_segments/
# generate_a2_segments、既存Production関数を無変更で直接呼ぶ)→Assembly
# (er003_v1_n3_01_assemble.stage_assemble_b1/stage_assemble_a2、既存
# Production関数を無変更で直接呼ぶ)→Audio Validation Gate(OFF経路は
# stage_assemble内部で自動実行済み、ON経路[OPEN-129 opt-in
# required_structure]は追加でread-onlyに直接呼ぶ)まで実行する。
#
# 記事本文(Writer/Fact Checker/Ledger Deviation/Point Overlap QA等)は
# 一切再生成しない(既存article.mdをそのままコピーし、コピー後にsha256で
# 内容変化が無いことを検証する)。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er011_family_a_completion_a2_trend_end_to_end_01_run.py [b1b] [a2]
#   (引数省略時はb1b→a2の順で両方実行)

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl

THEME_ID = "family_a_completion_a2_trend_end_to_end_01"
OUT_DIR = f"er011_output/{THEME_ID}"

# 入力: Wiring後の正式経路(editorial_mode="trend_synthesis")のOK版article.md
SOURCE_ARTICLE = {
    "b1b": "er011_output/open112_trend_synthesis_production_wiring_01/b1b/article.md",
    "a2": "er011_output/open112_trend_synthesis_production_wiring_01/a2_rerun_02/attempt2/article.md",
}
# B1Bは既存Key Phrase結果(REDUNDANCY_PASS)をbyte-identical article.mdの
# 場合に限り再利用する(article本文が同一なのに選定をやり直すのは無駄な
# 追加課金になるため。A2は既存結果が無いため新規実行)。
SOURCE_KEY_PHRASES_B1B = "er011_output/open112_trend_synthesis_production_wiring_01/b1b/key_phrases"

LEVELS = {
    "b1b": {
        "process": "B1_SUPPORT",
        "source_level": "B1-B(N3-01, direct generation)",
        "article_id": "FAMILY_A_COMPLETION_TREND_E2E_01_B1B",
        "run_scaffold": sc.run_b1_scaffold,
    },
    "a2": {
        "process": "A2_SUPPORT",
        "source_level": "A2(V2改1, N3-01)",
        "article_id": "FAMILY_A_COMPLETION_TREND_E2E_01_A2",
        "run_scaffold": sc.run_a2_scaffold,
    },
}


def sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# Step 0: article.mdコピー(記事は再生成しない、byte-identical検証)
# ============================================================
def prepare_article(level: str) -> str:
    level_out_dir = f"{OUT_DIR}/{level}"
    os.makedirs(f"{level_out_dir}/audit", exist_ok=True)
    src_path = SOURCE_ARTICLE[level]
    dst_path = f"{level_out_dir}/article.md"
    with open(src_path, encoding="utf-8") as f:
        src_text = f.read()
    shutil.copyfile(src_path, dst_path)
    with open(dst_path, encoding="utf-8") as f:
        dst_text = f.read()
    assert sha(src_text) == sha(dst_text), f"article.mdコピー時に内容が変化しました: {level}"
    print(f"[E2E][{level}] article.md コピー確認OK(sha256={sha(src_text)[:16]}..., 出典={src_path})")
    return src_text


# ============================================================
# Step 1: Scaffold(記事分割+Preview/Comment、Production関数を無変更で
# 直接呼ぶ。この記事に対しては本タスクが初回実行[Wiring後経路では
# 未実行だったため]。記事本文自体は変更しない)
# ============================================================
def run_scaffold(level: str, article_text: str) -> dict:
    level_out_dir = f"{OUT_DIR}/{level}"
    meta = LEVELS[level]
    parts = sc.split_article_text(article_text)
    save_json(f"{level_out_dir}/parts.json", parts)
    client = sc.get_client()
    with cl.logging_context(THEME_ID, f"scaffold_{level}"):
        support = meta["run_scaffold"](client, parts, level_out_dir, article_text)
    support_status = {k: v.get("status") for k, v in support.items()}
    print(f"[E2E][{level}] Scaffold(Preview/Comment)完了。status={support_status}")
    return parts


# ============================================================
# Step 2: Key Phrase(B1Bは既存REDUNDANCY_PASS結果を再利用、A2は新規実行)
# ============================================================
def prepare_key_phrases(level: str, article_text: str) -> str:
    meta = LEVELS[level]
    level_out_dir = f"{OUT_DIR}/{level}"
    kp_dir = f"{level_out_dir}/key_phrases"

    if level == "b1b":
        src_article_path = SOURCE_ARTICLE["b1b"]
        with open(src_article_path, encoding="utf-8") as f:
            src_article_text = f.read()
        # 既存Key Phrase結果はこのarticle.mdに対して生成されたものである
        # ことをsha256で確認したうえで再利用する(無駄な追加課金を避ける)。
        assert sha(src_article_text) == sha(article_text), (
            "B1B Key Phrase再利用の前提(article.md一致)が崩れています。STOP。")
        os.makedirs(kp_dir, exist_ok=True)
        for name in os.listdir(SOURCE_KEY_PHRASES_B1B):
            shutil.copyfile(f"{SOURCE_KEY_PHRASES_B1B}/{name}", f"{kp_dir}/{name}")
        kp = load_json(f"{kp_dir}/keywords_canonicalized.json")
        with open(f"{level_out_dir}/audit/key_phrase_reuse_note.json", "w", encoding="utf-8") as f:
            json.dump({
                "reused_from": SOURCE_KEY_PHRASES_B1B,
                "reused_from_article": src_article_path,
                "article_sha256_match": True,
                "note": ("既存Wiring後経路(OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01"
                          "§11.2)でREDUNDANCY_PASS到達済みのKey Phrase結果を、article.md本文が"
                          "byte-identicalであることを確認したうえでそのまま再利用した(新規LLM"
                          "呼び出し0件)。"),
            }, f, ensure_ascii=False, indent=2)
        print(f"[E2E][b1b] Key Phrase: 既存REDUNDANCY_PASS結果を再利用(新規LLM呼び出し0件)")
        return "REUSED_REDUNDANCY_PASS"

    # A2: 未実行のため新規実行(Production関数sc.run_key_phrasesを無変更で
    # 直接呼ぶ。B1Bの選定で使ったのと全く同じ関数)。
    with cl.logging_context(THEME_ID, f"keyphrase_{level}"):
        kp = sc.run_key_phrases(article_text, kp_dir, meta["article_id"], meta["source_level"],
                                 process=meta["process"])
    sel_status = kp["selection"]["status"]
    canon_status = (kp.get("canonicalization") or {}).get("status")
    redundancy_status = (kp.get("redundancy_qa") or {}).get("status")
    save_json(f"{level_out_dir}/audit/run_key_phrases_result_summary.json", {
        "selection_status": sel_status, "canonicalization_status": canon_status,
        "redundancy_qa_status": redundancy_status, "redundancy_retry_log": kp.get("redundancy_retry_log"),
    })
    print(f"[E2E][a2] Key Phrase結果: selection={sel_status} canonicalization={canon_status} "
          f"redundancy={redundancy_status}")
    if kp.get("canonicalization") is None or canon_status not in (
            "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        raise RuntimeError(f"A2 Key Phraseパイプライン失敗、STOP。selection={sel_status} "
                            f"canonicalization={canon_status}")
    if redundancy_status == "REDUNDANCY_NG":
        raise RuntimeError("A2 Key Phrase Redundancy QAがretry上限到達後もNG_REVIEW_REQUIRED、STOP。"
                            "既存Loop Budgetを独自判断で回避しない。")
    return redundancy_status or canon_status


# ============================================================
# Step 3: TTS(Production関数を無変更で直接呼ぶ)
# ============================================================
def run_tts(level: str) -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    with cl.logging_context(THEME_ID, f"tts_{level}"):
        if level == "b1b":
            result = tts_gen.generate_b1_segments(theme)
        else:
            result = tts_gen.generate_a2_segments(theme)
    return result


# ============================================================
# Step 4: Assembly(Production関数を無変更で直接呼ぶ。内部でAudio
# Validation Gate OFF経路[required_structure未指定]が自動実行される)
# ============================================================
def run_assembly(level: str) -> dict:
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    assemble_fn = asm.stage_assemble_b1 if level == "b1b" else asm.stage_assemble_a2
    with cl.logging_context(THEME_ID, f"assemble_{level}"):
        try:
            result = assemble_fn(theme)
            result["gate_off_result"] = "PASS"
        except RuntimeError as e:
            result = {"status": "GATE_BLOCKED", "gate_off_result": "BLOCKED", "error": str(e)}
    return result


# ============================================================
# Step 5: Audio Validation Gate opt-in ON経路(OPEN-129、read-only、
# Production関数asm.verify_episode_audio_validation_gate/
# asm.derive_a_family_required_structureを無変更で直接呼ぶ。既存の
# er011_open129_structural_completeness_production_wiring_evidence_01.py
# と同一の呼び出しパターン)。
# ============================================================
def run_gate_opt_in_check(level: str) -> dict:
    level_out_dir = f"{OUT_DIR}/{level}"
    gate_level = "B1" if level == "b1b" else "A2"
    rs = asm.derive_a_family_required_structure(gate_level)
    try:
        asm.verify_episode_audio_validation_gate(level_out_dir, gate_level, required_structure=rs)
        return {"gate_on_result": "PASS"}
    except RuntimeError as e:
        return {"gate_on_result": "BLOCKED", "gate_on_message": str(e)[:800]}


# ============================================================
# A2継続(FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01継続、Fable委任
# 「修正指示1回目」): 前回runはgenerate_a2_segments内の
# `JAPANESE_TITLES[theme_id]`KeyErrorでSTOPした(A-Family共通の
# 未解決gap、Trend固有ではない)。Fable判定(既存前例をそのまま適用):
# 標準A2の日本語タイトルは「英語タイトルの直訳を定数として人手供給」する
# 既存パターン(`er011_open112_trend_theme2_b_full_audio_trial_13.py`、
# `EDITORIAL-B-FAMILY-VOICES-A2-CROSS-AUDIT-AND-FIX-03_REPORT.md`B-2で
# 標準A2にも共通することを確認済み)がすでに承認済み前例として存在する
# ため、新しい仕様判断ではなく既存前例の適用として日本語タイトルを人手
# 供給する(自動翻訳ステップの新設はここでは行わない、OPEN item候補として
# Reportに記載のみ)。
#
# 日本語タイトル文言(原文タイトル "Young Travelers Want Trips at Their
# Own Pace — But Stays Are Still Short" の直訳。新しい主張・数字を追加
# しない、Trial-13/B-2と同一規約):
A2_JAPANESE_TITLE = "自分のペースで旅行したい若い旅行者たち――でも滞在日数はまだ短いまま"

# 前回runの既存a2/(Scaffold・Key Phrase=REDUNDANCY_PASS到達済み、TTSは
# topic_intro成功直後にKeyErrorでSTOP)は保持したまま、新規runはa2/配下の
# サブディレクトリ(a2/rerun_01/)へ出力する。Scaffold/Key Phraseは既存
# a2/の成果物をarticle.md sha256一致確認のうえ再利用し、新規LLM呼び出しを
# 増やさない(既存レポートで確認済みの結果を再利用するだけ)。
A2_CONTINUATION_ROOT = f"{OUT_DIR}/a2/rerun_01"


def run_a2_continuation() -> dict:
    old_a2_dir = f"{OUT_DIR}/a2"
    new_a2_dir = f"{A2_CONTINUATION_ROOT}/a2"
    os.makedirs(f"{new_a2_dir}/audit", exist_ok=True)
    cl.install(f"{A2_CONTINUATION_ROOT}/raw_usage_log_a2_continuation_01.jsonl")

    # Step 0: article.md(既存a2/を出典と再照合のうえコピー、記事は
    # 再生成しない)
    with open(f"{old_a2_dir}/article.md", encoding="utf-8") as f:
        article_text = f.read()
    with open(SOURCE_ARTICLE["a2"], encoding="utf-8") as f:
        src_text = f.read()
    assert sha(article_text) == sha(src_text), "旧a2/article.mdが出典と不一致、STOP。"
    shutil.copyfile(f"{old_a2_dir}/article.md", f"{new_a2_dir}/article.md")
    print(f"[E2E-A2-CONT] article.md sha256一致確認OK(sha256={sha(article_text)[:16]}...)")

    # Step 1: Scaffold成果物(既存a2/で完了済み、article.md一致確認済みの
    # ため再利用。新規LLM呼び出し0件)
    shutil.copyfile(f"{old_a2_dir}/parts.json", f"{new_a2_dir}/parts.json")
    shutil.copyfile(f"{old_a2_dir}/a2_support_texts.json", f"{new_a2_dir}/a2_support_texts.json")
    shutil.copyfile(f"{old_a2_dir}/audit/a2_support_generation.json",
                     f"{new_a2_dir}/audit/a2_support_generation.json")
    print("[E2E-A2-CONT] Scaffold成果物を既存a2/から再利用(新規LLM呼び出し0件)")

    # Step 2: Key Phrase成果物(既存a2/でREDUNDANCY_PASS到達済み、再利用。
    # 新規LLM呼び出し0件)
    os.makedirs(f"{new_a2_dir}/key_phrases", exist_ok=True)
    for name in os.listdir(f"{old_a2_dir}/key_phrases"):
        shutil.copyfile(f"{old_a2_dir}/key_phrases/{name}", f"{new_a2_dir}/key_phrases/{name}")
    print("[E2E-A2-CONT] Key Phrase成果物を既存a2/から再利用(新規LLM呼び出し0件)")

    # Step 3: 日本語タイトル登録(人手介在3箇所目。既存前例パターン
    # tts_gen.JAPANESE_TITLES.update({theme_id: 直訳})をそのまま踏襲、
    # tts_gen.py自体は無変更)
    tts_gen.JAPANESE_TITLES.update({THEME_ID: A2_JAPANESE_TITLE})
    print(f"[E2E-A2-CONT] JAPANESE_TITLES登録(人手供給・直訳): {A2_JAPANESE_TITLE!r}")

    # Step 4: TTS(Production関数generate_a2_segmentsを無変更で直接呼ぶ。
    # theme['out_dir']をA2_CONTINUATION_ROOTにすることで、実ファイルは
    # A2_CONTINUATION_ROOT/a2/配下に出力される)
    theme = {"theme_id": THEME_ID, "out_dir": A2_CONTINUATION_ROOT}
    with cl.logging_context(THEME_ID, "tts_a2_continuation"):
        tts_result = tts_gen.generate_a2_segments(theme)
    print(f"[E2E-A2-CONT] TTS完了。segment_status={tts_result.get('segment_status')}")

    # Step 5: Assembly(Production関数stage_assemble_a2を無変更で直接
    # 呼ぶ。内部でAudio Validation Gate OFF経路が自動実行される)
    with cl.logging_context(THEME_ID, "assemble_a2_continuation"):
        try:
            assemble_result = asm.stage_assemble_a2(theme)
            assemble_result["gate_off_result"] = "PASS"
        except RuntimeError as e:
            assemble_result = {"status": "GATE_BLOCKED", "gate_off_result": "BLOCKED", "error": str(e)}
    print(f"[E2E-A2-CONT] Assembly(Gate OFF経路)結果: {assemble_result.get('gate_off_result')}")

    # Step 6: Audio Validation Gate opt-in ON経路(OPEN-129、read-only)
    if assemble_result.get("gate_off_result") == "PASS":
        rs = asm.derive_a_family_required_structure("A2")
        try:
            asm.verify_episode_audio_validation_gate(new_a2_dir, "A2", required_structure=rs)
            gate_on = {"gate_on_result": "PASS"}
        except RuntimeError as e:
            gate_on = {"gate_on_result": "BLOCKED", "gate_on_message": str(e)[:800]}
    else:
        gate_on = {"gate_on_result": "SKIPPED_ASSEMBLE_NOT_PASS"}
    print(f"[E2E-A2-CONT] Gate opt-in ON経路結果: {gate_on.get('gate_on_result')}")

    result = {
        "level": "a2_continuation", "japanese_title": A2_JAPANESE_TITLE,
        "tts_result": tts_result, "assemble_result": assemble_result,
        "gate_opt_in_result": gate_on,
    }
    save_json(f"{A2_CONTINUATION_ROOT}/a2_continuation_summary.json", result)
    print("[E2E-A2-CONT] 完了。")
    return result


# ============================================================
# Level単位のオーケストレーション
# ============================================================
def run_level(level: str) -> dict:
    print(f"===== [E2E] level={level} 開始 =====")
    article_text = prepare_article(level)
    run_scaffold(level, article_text)
    kp_status = prepare_key_phrases(level, article_text)
    tts_result = run_tts(level)
    assemble_result = run_assembly(level)
    gate_on = run_gate_opt_in_check(level) if assemble_result.get("gate_off_result") == "PASS" else \
        {"gate_on_result": "SKIPPED_ASSEMBLE_NOT_PASS"}
    return {
        "level": level, "kp_status": kp_status, "tts_result": tts_result,
        "assemble_result": assemble_result, "gate_opt_in_result": gate_on,
    }


def main() -> dict:
    levels = sys.argv[1:] or ["b1b", "a2"]

    # A2継続専用の呼び出し(日本語タイトル人手供給を含む、上記参照)。
    # 通常のlevelループ(b1b/a2)とは別経路(既存a2/出力を上書きしない)。
    if levels == ["a2_continuation"]:
        result = run_a2_continuation()
        print("[E2E-A2-CONT] 完了。")
        return {"a2_continuation": result}

    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")

    # Trend Gate 6条件・Mode判定(人手介在1箇所目)の記録を、既存のWiring後
    # 経路のrun_metadata.jsonから複製する(記事は再生成しないため再判定は
    # 行わない。同一article.mdに対する既存の手動判定記録を引き継ぐ)。
    wiring_metadata = load_json("er011_output/open112_trend_synthesis_production_wiring_01/run_metadata.json")
    save_json(f"{OUT_DIR}/run_metadata_inherited_from_wiring_01.json", wiring_metadata)

    results = {}
    for level in levels:
        try:
            results[level] = run_level(level)
        except (RuntimeError, AssertionError) as e:
            results[level] = {"level": level, "status": "STOP", "error": str(e)}
            print(f"[E2E][{level}] STOP: {e}")

    save_json(f"{OUT_DIR}/e2e_run_summary.json", results)
    print("[E2E] 完了。")
    return results


if __name__ == "__main__":
    main()
