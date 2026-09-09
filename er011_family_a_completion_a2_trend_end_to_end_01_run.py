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
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl
import er011_human_review_lock_01 as review_lock

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
# B1B継続(FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01継続、Fable委任
# 「修正指示2回目」): Key Phrase 5 日本語gloss「形になり始める」
# (kp5_ja_charon)がHUMAN_REVIEW_REQUIRED(標準2回+fallback1回、合計上限
# 3回とも不合格、final_status=STOPPED)で止まっている。
#
# ユーザー決定(2026-09-09、A2-UDR-1=(a)): 承認済み再生成経路
# (review_lock.approve_regenerate()、EDITORIAL-B-FAMILY-VOICES-TRIAL-09-
# HEADING-REGEN-AND-FULL-EPISODE-03の前例)であと1回だけ再生成する
# (1回限り、同一文言での追加retryはしない)。通れば結果を採用しB1Bの
# Trend End-to-End確認を完了方向へ進める。今回も不合格の場合は同じ文言で
# 追加retryせず、既存Key Phrase選定経路(Selection→Canonicalization→
# Redundancy QA、sc.run_key_phrases、Production関数を無変更で直接呼ぶ)で
# 新たに得られる選定結果のうちrank5候補だけをKey Phrase 5の差し替え候補
# として採用する(rank1-4は既に承認済み・TTS済みのため変更しない。記事
# 本文自体も再生成しない)。
# ============================================================
B1B_KP5_SEGMENT = "kp5_ja_charon"
B1B_KP5_OUT_PATH = f"{OUT_DIR}/b1b/narration/{B1B_KP5_SEGMENT}.wav"
B1B_CONTINUATION_DIR = f"{OUT_DIR}/b1b/kp5_regen_and_completion_01"
B1B_CONTINUATION_COST_LOG = f"{B1B_CONTINUATION_DIR}/raw_usage_log_kp5_regen_and_completion_01.jsonl"

B1B_KP5_APPROVAL_RATIONALE = (
    "ユーザー決定(2026-09-09、管理ID FAMILY-A-COMPLETION-A2-TREND-END-TO-"
    "END-01継続、A2-UDR-1=(a)): B1B Key Phrase 5 日本語gloss「形になり始"
    "める」(kp5_ja_charon)を、承認済み再生成経路(review_lock.approve_"
    "regenerate())であと1回だけ再生成することを承認する。根拠(前例): "
    "EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03"
    "(review_lock.approve_regenerate()による1回限りの再生成承認)。通らな"
    "い場合は同一文言での追加retryをせず、既存Key Phrase選定経路で別候補"
    "へ差し替える(ユーザー決定の一部)。"
)


def _b1b_kp5_regenerate_once() -> dict:
    """kp5_ja_charonを承認済み経路であと1回だけ再生成する。呼ぶのは
    Production関数(tts_gen.generate_charon_japanese_with_reading_safety
    -> voice01.generate_charon_japanese、@review_lock.guarded_generate("ja")
    でガードされた既存関数)のみで、この関数自体は薄いorchestrationに
    留める(Production関数は無変更)。"""
    b1_out_dir = f"{OUT_DIR}/b1b"
    kp = load_json(f"{b1_out_dir}/key_phrases/keywords_canonicalized.json")
    item5 = next(it for it in kp["items"] if it["rank"] == 5)
    ja_gloss_tts, fallback_derived = tts_gen.resolve_key_phrase_ja_gloss_tts(item5)
    used_form = item5["used_form"]

    prior_lock = load_json(f"{b1_out_dir}/audit/review_lock_state.json").get(B1B_KP5_SEGMENT, {})
    if prior_lock.get("state") != "HUMAN_REVIEW_REQUIRED":
        raise RuntimeError(
            f"想定外のlock状態(HUMAN_REVIEW_REQUIREDのはず): {prior_lock.get('state')}。"
            "STOP(別segmentでのLock発動、または既に処理済みの可能性があります)。")

    approved_at = time.strftime("%Y-%m-%dT%H:%M:%S")
    approval_entry = review_lock.approve_regenerate(B1B_KP5_OUT_PATH, ja_gloss_tts, approved_by="user")
    save_json(f"{B1B_CONTINUATION_DIR}/audit/user_approval_record_kp5_regen_01.json", {
        "management_id": "FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01",
        "segment_id": B1B_KP5_SEGMENT, "canonical_text": ja_gloss_tts,
        "approved_by": "user", "approved_at": approved_at,
        "rationale": B1B_KP5_APPROVAL_RATIONALE,
        "prior_lock_state_before_approval": prior_lock,
        "review_lock_entry_after_approval": approval_entry,
    })
    print(f"[B1B-CONT] approve_regenerate() 実行完了: state={approval_entry.get('state')}")

    result = tts_gen.generate_charon_japanese_with_reading_safety(
        ja_gloss_tts, B1B_KP5_OUT_PATH, tts_gen.expected_substring_ja(ja_gloss_tts),
        known_key_phrase_terms=[used_form])
    print(f"[B1B-CONT] kp5_ja_charon 再生成結果: status={result.get('status')}")

    # 既存Production/Gateが読むaudit記録(tts_generation_results.json)を、
    # このcallで得た実結果で更新する(Trial-09 heading_regen_03と同一パターン)。
    tts_results_path = f"{b1_out_dir}/audit/tts_generation_results.json"
    tts_results = load_json(tts_results_path)
    entry = dict(result)
    entry["canonical_text"] = ja_gloss_tts
    entry["display_gloss"] = item5["japanese_gloss"]
    entry["japanese_gloss_tts_fallback_derived"] = fallback_derived
    tts_results["key_phrases"]["5"]["japanese"] = entry
    save_json(tts_results_path, tts_results)
    print(f"[B1B-CONT] tts_generation_results.json のkey_phrases['5']['japanese']を更新: "
          f"status={entry.get('status')}")

    new_lock = load_json(f"{b1_out_dir}/audit/review_lock_state.json").get(B1B_KP5_SEGMENT, {})
    summary = {
        "segment_id": B1B_KP5_SEGMENT, "canonical_text": ja_gloss_tts, "used_form": used_form,
        "generate_result_status": result.get("status"), "generate_result": result,
        "review_lock_entry_after_generate": new_lock,
    }
    save_json(f"{B1B_CONTINUATION_DIR}/audit/kp5_regen_01_result.json", summary)
    return summary


# ============================================================
# kp5差し替え(1回限りの承認済み再生成が再度不合格だった場合のみ実行)
# ============================================================
def _b1b_kp5_replace_via_selection_pipeline() -> dict:
    """kp5_ja_charonの承認済み再生成(1回限り)が再度不合格だった場合の
    差し替え経路。既存Key Phrase選定経路(sc.run_key_phrases、Selection→
    Canonicalization→Redundancy QA、Production関数を無変更で直接呼ぶ)で
    フル5件の新規選定を実行し、そのうちrank5候補だけをKey Phrase 5の
    差し替え候補として採用する(rank1-4は既承認・既TTS済みのため変更
    しない、新規選定側のrank1-4は破棄する)。採用前に「旧rank1-4(既承認)
    + 新rank5候補」という最終5件セットでRedundancy QA
    (sc.run_key_phrase_redundancy_qa、Production関数)を再実行し、
    旧rank1-4との重複が無いことを確認する。"""
    b1_out_dir = f"{OUT_DIR}/b1b"
    kp_dir = f"{b1_out_dir}/key_phrases"
    replacement_dir = f"{B1B_CONTINUATION_DIR}/kp5_replacement_selection_01"
    os.makedirs(replacement_dir, exist_ok=True)

    with open(SOURCE_ARTICLE["b1b"], encoding="utf-8") as f:
        article_text = f.read()

    old_kp = load_json(f"{kp_dir}/keywords_canonicalized.json")
    old_item5 = next(it for it in old_kp["items"] if it["rank"] == 5)
    old_items_1to4 = [it for it in old_kp["items"] if it["rank"] != 5]

    fresh = sc.run_key_phrases(
        article_text, replacement_dir, LEVELS["b1b"]["article_id"] + "_KP5_REPLACEMENT",
        LEVELS["b1b"]["source_level"], process=LEVELS["b1b"]["process"])
    save_json(f"{B1B_CONTINUATION_DIR}/audit/kp5_replacement_fresh_selection_result_summary.json", {
        "selection_status": fresh["selection"]["status"],
        "canonicalization_status": (fresh.get("canonicalization") or {}).get("status"),
        "redundancy_qa_status": (fresh.get("redundancy_qa") or {}).get("status"),
    })
    if fresh.get("canonicalization") is None or fresh["canonicalization"]["status"] not in (
            "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        raise RuntimeError(
            f"kp5差し替え用フル新規選定が失敗しました。selection={fresh['selection']['status']} "
            f"canonicalization={(fresh.get('canonicalization') or {}).get('status')}。STOP。")

    new_items_all = fresh["canonicalization"]["merged"]["items"]
    new_item5 = next(it for it in new_items_all if it["rank"] == 5)

    merged_final_items = sorted(old_items_1to4 + [new_item5], key=lambda it: it["rank"])
    final_check_dir = f"{replacement_dir}/final_merged_redundancy_check"
    os.makedirs(final_check_dir, exist_ok=True)
    redundancy = sc.run_key_phrase_redundancy_qa(
        article_text, merged_final_items, final_check_dir,
        LEVELS["b1b"]["article_id"] + "_KP5_REPLACEMENT_FINAL", process=LEVELS["b1b"]["process"])

    save_json(f"{B1B_CONTINUATION_DIR}/audit/kp5_replacement_candidate_and_reason.json", {
        "old_candidate": old_item5, "new_candidate": new_item5,
        "reason": (
            "承認済み再生成(review_lock.approve_regenerate())を1回実施したが、"
            "kp5_ja_charon(『形になり始める』)は標準経路2回+fallback経路1回(このrunの"
            "3回、通算では以前のrunと合わせて6回)ともASR検証でTRUE_CONTENT_MISMATCHとなり"
            "不合格だった(『なり』周辺の発話が繰り返し欠落/混同される既知の困難ワードと判断)。"
            "ユーザー決定(2026-09-09、A2-UDR-1(a))に従い、同一文言での追加retryはせず、"
            "既存Key Phrase選定経路(Selection→Canonicalization→Redundancy QA)で新規に"
            "選定された別候補へ差し替えた。"),
        "final_merged_redundancy_qa_status": redundancy.get("status"),
    })

    if redundancy.get("status") == "REDUNDANCY_NG":
        raise RuntimeError(
            f"kp5差し替え候補が旧rank1-4とのRedundancy QAでNG(duplicate_pairs="
            f"{redundancy.get('duplicate_pairs')})。既存Loop Budgetの範囲を超える追加retryは"
            "本タスクの委任範囲外のため、ここでSTOPし報告します。")

    final_kp_doc = {"items": merged_final_items, "overall_status": redundancy.get("status")}
    save_json(f"{kp_dir}/keywords_canonicalized.json", final_kp_doc)
    print(f"[B1B-CONT][KP5-REPLACE] keywords_canonicalized.json rank5を差し替え: "
          f"旧={old_item5['used_form']!r} 新={new_item5['used_form']!r}")

    narration_dir = f"{b1_out_dir}/narration"
    new_used_form = new_item5["used_form"]
    ja_gloss_tts, fallback_derived = tts_gen.resolve_key_phrase_ja_gloss_tts(new_item5)

    en_out_path = f"{narration_dir}/kp5_en.wav"
    en_result = tts_gen.shared_narration.ensure_key_phrase_english_component(
        tts_gen.tts_safe_kp_en(new_used_form), en_out_path)
    print(f"[B1B-CONT][KP5-REPLACE] 新kp5_en生成: status={en_result.get('status')} "
          f"reused={en_result.get('reused')}")

    ja_out_path = f"{narration_dir}/{B1B_KP5_SEGMENT}.wav"
    ja_result = tts_gen.generate_charon_japanese_with_reading_safety(
        ja_gloss_tts, ja_out_path, tts_gen.expected_substring_ja(ja_gloss_tts),
        known_key_phrase_terms=[new_used_form])
    print(f"[B1B-CONT][KP5-REPLACE] 新kp5_ja_charon生成: status={ja_result.get('status')}")

    tts_results_path = f"{b1_out_dir}/audit/tts_generation_results.json"
    tts_results = load_json(tts_results_path)
    en_entry = dict(en_result)
    en_entry["canonical_text"] = new_used_form
    ja_entry = dict(ja_result)
    ja_entry["canonical_text"] = ja_gloss_tts
    ja_entry["display_gloss"] = new_item5["japanese_gloss"]
    ja_entry["japanese_gloss_tts_fallback_derived"] = fallback_derived
    tts_results["key_phrases"]["5"] = {"english": en_entry, "japanese": ja_entry}
    save_json(tts_results_path, tts_results)

    summary = {
        "old_candidate": old_item5, "new_candidate": new_item5,
        "final_merged_redundancy_qa_status": redundancy.get("status"),
        "english_result_status": en_result.get("status"), "japanese_result_status": ja_result.get("status"),
        "final_status": "OK" if (en_result.get("status") == "OK" and ja_result.get("status") == "OK") else "NG",
    }
    save_json(f"{B1B_CONTINUATION_DIR}/audit/kp5_replacement_result.json", summary)
    return summary


def run_b1b_continuation() -> dict:
    print("===== [B1B-CONT] 開始 =====")
    os.makedirs(f"{B1B_CONTINUATION_DIR}/audit", exist_ok=True)
    cl.install(B1B_CONTINUATION_COST_LOG)

    b1_out_dir = f"{OUT_DIR}/b1b"
    narration_dir = f"{b1_out_dir}/narration"

    # 他segment(前回OK分)をbyte-for-byte再利用することの記録(sha256
    # manifest、kp5_ja_charon自体は今回書き換えるため対象外)。
    reuse_manifest = {}
    for fname in sorted(os.listdir(narration_dir)):
        full_path = f"{narration_dir}/{fname}"
        if fname.endswith(".wav") and os.path.isfile(full_path) and fname != f"{B1B_KP5_SEGMENT}.wav":
            with open(full_path, "rb") as f:
                reuse_manifest[fname] = hashlib.sha256(f.read()).hexdigest()
    save_json(f"{B1B_CONTINUATION_DIR}/audit/pre_existing_segments_sha256_manifest.json", reuse_manifest)
    print(f"[B1B-CONT] 既存segment(kp5_ja_charon以外){len(reuse_manifest)}件のsha256を記録"
          "(byte-for-byte再利用、変更なしの確認用)。")

    # 冪等性ガード: このcontinuation出力ディレクトリに既にkp5_regen_01_result.json
    # が存在する場合(=このタスク内で承認済み1回限りの再生成を既に実行済み)、
    # 二度目のapprove_regenerate()呼び出しを避けるため再実行せず前回結果を再利用
    # する(同一文言での2回目の承認・再生成は絶対に行わない)。
    regen_result_path = f"{B1B_CONTINUATION_DIR}/audit/kp5_regen_01_result.json"
    if os.path.exists(regen_result_path):
        regen_summary = load_json(regen_result_path)
        print("[B1B-CONT] 既存のkp5_regen_01_result.jsonを検出、承認済み再生成(1回限り)は"
              f"実行済みのためスキップします(前回結果: status="
              f"{regen_summary.get('generate_result_status')})。")
    else:
        with cl.logging_context(THEME_ID, "b1b_kp5_regen"):
            regen_summary = _b1b_kp5_regenerate_once()

    replacement_summary = None
    kp5_final_ok = regen_summary["generate_result_status"] == "OK"
    if not kp5_final_ok:
        print("[B1B-CONT] kp5_ja_charon再生成はNGでした。同一文言での追加retryはせず、"
              "既存Key Phrase選定経路(Selection→Canonicalization→Redundancy QA)で"
              "別候補への差し替えを実行します。")
        replacement_result_path = f"{B1B_CONTINUATION_DIR}/audit/kp5_replacement_result.json"
        if os.path.exists(replacement_result_path):
            replacement_summary = load_json(replacement_result_path)
            print("[B1B-CONT] 既存のkp5_replacement_result.jsonを検出、差し替え済みのため"
                  f"再実行せず前回結果を再利用します(前回結果: final_status="
                  f"{replacement_summary.get('final_status')})。")
        else:
            with cl.logging_context(THEME_ID, "b1b_kp5_replace"):
                replacement_summary = _b1b_kp5_replace_via_selection_pipeline()
        kp5_final_ok = replacement_summary.get("final_status") == "OK"

    assemble_result = None
    gate_on = None
    if kp5_final_ok:
        with cl.logging_context(THEME_ID, "assemble_b1b_continuation"):
            try:
                assemble_result = asm.stage_assemble_b1({"theme_id": THEME_ID, "out_dir": OUT_DIR})
                assemble_result["gate_off_result"] = "PASS"
            except RuntimeError as e:
                assemble_result = {"status": "GATE_BLOCKED", "gate_off_result": "BLOCKED", "error": str(e)}
        print(f"[B1B-CONT] Assembly(Gate OFF経路)結果: {assemble_result.get('gate_off_result')}")

        if assemble_result.get("gate_off_result") == "PASS":
            rs = asm.derive_a_family_required_structure("B1")
            try:
                asm.verify_episode_audio_validation_gate(b1_out_dir, "B1", required_structure=rs)
                gate_on = {"gate_on_result": "PASS"}
            except RuntimeError as e:
                gate_on = {"gate_on_result": "BLOCKED", "gate_on_message": str(e)[:800]}
        else:
            gate_on = {"gate_on_result": "SKIPPED_ASSEMBLE_NOT_PASS"}
        print(f"[B1B-CONT] Gate opt-in ON経路結果: {gate_on.get('gate_on_result')}")

    result = {
        "level": "b1b_continuation",
        "kp5_regen": regen_summary, "kp5_replacement": replacement_summary,
        "assemble_result": assemble_result, "gate_opt_in_result": gate_on,
        "reuse_manifest_count": len(reuse_manifest),
    }
    save_json(f"{B1B_CONTINUATION_DIR}/b1b_continuation_summary.json", result)
    print("[B1B-CONT] 完了。")
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

    # B1B継続専用の呼び出し(kp5_ja_charon再生成承認、上記参照)。
    if levels == ["b1b_continuation"]:
        result = run_b1b_continuation()
        return {"b1b_continuation": result}

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
