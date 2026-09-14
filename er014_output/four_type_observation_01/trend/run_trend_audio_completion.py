# ============================================================
# er014_output/four_type_observation_01/trend/run_trend_audio_completion.py
# 管理ID: USER-TEST-AUDIO-COMPLETION-01-TREND
# ============================================================
# 目的: 完成済みcanonical article(trend/a2/article.md、trend/b1b/article.md、
# 本文は再生成しない)を、既存Production関数のみ(er003_v1_n3_01_scaffold_
# generate.run_key_phrases/run_a2_scaffold/run_b1_scaffold、
# er003_v1_n3_01_tts_generate.generate_a2_segments/generate_b1_segments、
# er003_v1_n3_01_assemble.stage_assemble_a2/stage_assemble_b1/
# verify_episode_audio_validation_gate、いずれも無変更で直接呼ぶ)で音声化し、
# 完成episode(WAV+配信用mp3)+Web試聴player(相対パス参照)まで仕上げる。
#
# 前例(er011_family_a_completion_a2_trend_end_to_end_01_run.py、
# 管理ID FAMILY-A-COMPLETION-A2-TREND-END-TO-END-01)と同一の呼び出し
# パターンを、本タスクのTrend記事(er014_output/.../trend/a2,b1b/article.md)
# 向けに最小接続したdriver。split_article_text()がすでにPoint One/Two
# 見出し(###)+In one line(##)構造を汎用的に扱うため、Trend Synthesis記事
# 固有の追加実装は不要だった(gapなし)。唯一の既知gapはA2のJAPANESE_TITLES
# 辞書(theme_id単位、既存前例と同一の人手供給パターンを踏襲、後述)。
#
# 実行方法(root直下から、レベルごとに個別実行):
#   .venv/Scripts/python.exe er014_output/four_type_observation_01/trend/run_trend_audio_completion.py --level a2
#   .venv/Scripts/python.exe er014_output/four_type_observation_01/trend/run_trend_audio_completion.py --level b1b
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

# PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-01: 正式リリース前はStandard同期を使う。
os.environ["TTS_EXECUTION_MODE"] = "STANDARD"

# 本driverはer014_output配下(root直下ではない)にあるため、root直下の
# Production module(er003_*/er005_*/er006_*/audio_review_player等)を
# importできるようroot dirをsys.pathへ追加する(実行コマンド自体は
# root直下から呼ぶ想定だが、import解決のため明示的に追加しておく)。
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import soundfile as sf

import audio_review_player as arp
import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl
import er006_audio_cost_pilot_02_shared_narration as shared_narration

THEME_ID = "trend_audio_completion_01"
TREND_DIR = "er014_output/four_type_observation_01/trend"
OUT_DIR = f"{TREND_DIR}/audio"
LOG_PATH = f"{OUT_DIR}/raw_usage_log_audio_completion.jsonl"

SOURCE_ARTICLE = {
    "a2": f"{TREND_DIR}/a2/article.md",
    "b1b": f"{TREND_DIR}/b1b/article.md",
}

# A2はgenerate_a2_segments()内でJAPANESE_TITLES[theme_id]を直接参照する
# (既存gap、Trend固有ではなくA-Family共通。前例[FAMILY-A-COMPLETION-A2-
# TREND-END-TO-END-01継続]と同一パターンで、原文タイトルの直訳を人手で
# 定数供給する。新しい主張・数字は追加しない)。
# 原文タイトル: "The Smartphone Screen Is Still Here. It Is Just Sharing the Work"
A2_JAPANESE_TITLE = "スマートフォンの画面はまだここにある――ただ、その役割を分け合っているだけだ"

LEVELS = {
    "b1b": {
        "process": "B1_SUPPORT",
        "source_level": "B1-B(N3-01, direct generation, Trend Synthesis)",
        "article_id": "TREND_AUDIO_COMPLETION_01_B1B",
        "run_scaffold": sc.run_b1_scaffold,
        "gate_level": "B1",
        "assemble_fn_name": "stage_assemble_b1",
    },
    "a2": {
        "process": "A2_SUPPORT",
        "source_level": "A2(N3-01, Trend Synthesis)",
        "article_id": "TREND_AUDIO_COMPLETION_01_A2",
        "run_scaffold": sc.run_a2_scaffold,
        "gate_level": "A2",
        "assemble_fn_name": "stage_assemble_a2",
    },
}

BUDGET_JPY = 150.0  # A2+B1B合計(ユーザー指定上限)

PRICING_PATH = "er005_output/cost_baseline_01/pricing_snapshot.json"
USD_JPY = 160.0


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
# コスト集計(既存raw_usage_log.jsonlをer005_output/cost_baseline_01/
# pricing_snapshot.jsonの単価で換算するだけの読み取り専用集計。
# Production生成ロジックは一切変更しない)
# ============================================================
def _load_pricing():
    with open(PRICING_PATH, encoding="utf-8") as f:
        return json.load(f)["prices"]


PRICING = _load_pricing()


def _price(provider, model, meter, tier="Standard"):
    for p in PRICING:
        if (p["provider"] == provider and p["model"] == model and p["meter"] == meter
                and p.get("tier", "Standard") == tier):
            return p["price"]
    return None


def _call_cost_usd(rec: dict) -> float:
    if rec.get("success") is False:
        return 0.0
    provider = rec.get("provider")
    model = rec.get("model_id")
    if provider == "azure":
        dur = rec.get("audio_duration_submitted_seconds") or 0.0
        price = _price("azure", "real-time transcription (S0/S1 standard tier)", "audio_hour")
        return (dur / 3600.0) * (price or 0.0)
    it = rec.get("input_tokens") or 0
    ot = rec.get("output_tokens") or 0
    ct = rec.get("cached_input_tokens") or 0
    billable_in = max(it - ct, 0)
    in_price = _price(provider, model, "input_tokens")
    out_price = _price(provider, model, "output_tokens")
    cached_price = _price(provider, model, "cached_input_tokens")
    if in_price is None or out_price is None:
        return 0.0
    if cached_price is None:
        cached_price = in_price
    return (billable_in / 1e6) * in_price + (ct / 1e6) * cached_price + (ot / 1e6) * out_price


def cost_breakdown_by_stage() -> dict:
    """stage文字列(例: "scaffold_a2"/"keyphrase_a2"/"tts_a2")ごとにJPYを合算する。"""
    breakdown: dict[str, float] = {}
    if not os.path.exists(LOG_PATH):
        return breakdown
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            stage = rec.get("stage") or "unknown"
            breakdown[stage] = breakdown.get(stage, 0.0) + _call_cost_usd(rec) * USD_JPY
    return {k: round(v, 4) for k, v in breakdown.items()}


def cost_so_far_jpy() -> float:
    return round(sum(cost_breakdown_by_stage().values()), 4)


def check_budget(next_stage_note: str) -> None:
    so_far = cost_so_far_jpy()
    print(f"[BUDGET] so_far={so_far:.2f} JPY / budget={BUDGET_JPY} JPY (次段階: {next_stage_note})")
    if so_far >= BUDGET_JPY:
        raise RuntimeError(
            f"費用上限到達のためSTOP: so_far={so_far:.2f} JPY >= budget={BUDGET_JPY} JPY "
            f"(次段階「{next_stage_note}」を実行せず停止)")


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
    print(f"[AUDIO][{level}] article.md コピー確認OK(sha256={sha(src_text)[:16]}..., 出典={src_path})")
    return src_text


# ============================================================
# Step 1: Scaffold(Preview/Comment、Production関数を無変更で直接呼ぶ)
# ============================================================
def run_scaffold(level: str, article_text: str) -> dict:
    level_out_dir = f"{OUT_DIR}/{level}"
    meta = LEVELS[level]
    parts = sc.split_article_text(article_text)
    save_json(f"{level_out_dir}/parts.json", parts)
    support_path = f"{level_out_dir}/{'a2_support_texts.json' if level == 'a2' else 'b1_support_texts.json'}"
    if os.path.exists(support_path):
        # 再実行(resume): 既に生成済みのPreview/Commentを再利用し、LLM
        # 呼び出しを追加しない(前回runの成果物、無駄な追加課金・非決定的な
        # 再生成を避ける)。
        support = load_json(support_path)
        print(f"[AUDIO][{level}] Scaffold: 既存成果物を再利用(新規LLM呼び出し0件): {support_path}")
        return parts
    client = sc.get_client()
    with cl.logging_context(THEME_ID, f"scaffold_{level}"):
        support = meta["run_scaffold"](client, parts, level_out_dir, article_text)
    support_status = {k: v.get("status") for k, v in support.items()}
    print(f"[AUDIO][{level}] Scaffold(Preview/Comment)完了。status={support_status}")
    return parts


# ============================================================
# Step 2: Key Phrase(A2/B1B双方とも本記事に対しては未生成のため新規実行。
# run_key_phrases()内部にRedundancy QA retryループが既にある[最大
# KEY_PHRASE_REDUNDANCY_RETRY_MAX回]、driver側で追加retryはしない)。
# ============================================================
def prepare_key_phrases(level: str, article_text: str) -> dict:
    meta = LEVELS[level]
    level_out_dir = f"{OUT_DIR}/{level}"
    kp_dir = f"{level_out_dir}/key_phrases"
    canon_path = f"{kp_dir}/keywords_canonicalized.json"
    summary_path = f"{level_out_dir}/audit/run_key_phrases_result_summary.json"
    if os.path.exists(canon_path) and os.path.exists(summary_path):
        # 再実行(resume): 既存Key Phrase結果(前回run)を再利用し、LLM
        # 呼び出しを追加しない(選定は非決定的なため、再実行すると別の
        # Key Phraseに変わりうる。前回runで既にCANONICALIZATION_PASS/
        # REDUNDANCY_PASS等に到達済みの結果をそのまま使う)。
        prior_summary = load_json(summary_path)
        canon = load_json(canon_path)
        print(f"[AUDIO][{level}] Key Phrase: 既存成果物を再利用(新規LLM呼び出し0件)。"
              f"prior_summary={prior_summary}")
        return {
            "selection_status": prior_summary.get("selection_status"),
            "canonicalization_status": prior_summary.get("canonicalization_status"),
            "redundancy_qa_status": prior_summary.get("redundancy_qa_status"),
            "redundancy_retry_attempts": prior_summary.get("redundancy_retry_attempts", 0),
            "items": canon["items"],
        }
    # 委任文の明示許可: 「Validator不合格時は入口再呼び出し最大3回」。
    # run_key_phrase_selection()自体はmax_attempts=1(既存Production
    # 仕様)で内部retryを持たないため、KEY_WORDS_STRUCTURE_INVALID等の
    # 構造検証不合格時は、sc.run_key_phrases()という「入口」を最大3回
    # まで呼び直す(Redundancy QA自体のretryは既存関数内で完結済み、
    # ここでの3回は入口呼び出し全体の再試行)。
    ENTRY_RETRY_MAX = 3
    kp = None
    sel_status = canon_status = redundancy_status = None
    entry_attempts_log = []
    for entry_attempt in range(1, ENTRY_RETRY_MAX + 1):
        check_budget(f"keyphrase_{level}_entry_attempt{entry_attempt}")
        with cl.logging_context(THEME_ID, f"keyphrase_{level}"):
            kp = sc.run_key_phrases(article_text, kp_dir, meta["article_id"], meta["source_level"],
                                     process=meta["process"])
        sel_status = kp["selection"]["status"]
        canon_status = (kp.get("canonicalization") or {}).get("status")
        redundancy_status = (kp.get("redundancy_qa") or {}).get("status")
        entry_attempts_log.append({"entry_attempt": entry_attempt, "selection_status": sel_status,
                                    "canonicalization_status": canon_status,
                                    "redundancy_qa_status": redundancy_status})
        print(f"[AUDIO][{level}] Key Phrase結果(入口呼び出し{entry_attempt}/{ENTRY_RETRY_MAX}): "
              f"selection={sel_status} canonicalization={canon_status} redundancy={redundancy_status}")
        if sel_status == "KEY_WORDS_STRUCTURE_PASS" and canon_status in (
                "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
            break
    save_json(f"{level_out_dir}/audit/run_key_phrases_result_summary.json", {
        "selection_status": sel_status, "canonicalization_status": canon_status,
        "redundancy_qa_status": redundancy_status, "redundancy_retry_log": kp.get("redundancy_retry_log"),
        "redundancy_retry_attempts": kp.get("redundancy_retry_attempts"),
        "entry_attempts_log": entry_attempts_log,
    })
    if kp.get("canonicalization") is None or canon_status not in (
            "CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        raise RuntimeError(f"[{level}] Key Phraseパイプライン失敗、STOP(入口呼び出し{ENTRY_RETRY_MAX}回到達)。"
                            f"selection={sel_status} canonicalization={canon_status}")
    if redundancy_status == "REDUNDANCY_NG":
        raise RuntimeError(f"[{level}] Key Phrase Redundancy QAがretry上限到達後もNG_REVIEW_REQUIRED、STOP。"
                            "既存Loop Budgetを独自判断で回避しない。")
    return {
        "selection_status": sel_status, "canonicalization_status": canon_status,
        "redundancy_qa_status": redundancy_status,
        "redundancy_retry_attempts": kp.get("redundancy_retry_attempts", 0),
        "items": kp["canonicalization"]["merged"]["items"],
    }


# ============================================================
# Step 3: TTS(Production関数を無変更で直接呼ぶ。A2のみJAPANESE_TITLES
# 人手供給が既存gapとして必要、既存前例[FAMILY-A-COMPLETION-A2-TREND-
# END-TO-END-01継続]と同一パターン)。
# ============================================================
def run_tts(level: str) -> dict:
    level_out_dir = f"{OUT_DIR}/{level}"
    results_path = f"{level_out_dir}/audit/tts_generation_results.json"
    summary_path = f"{level_out_dir}/run_summary_tts.json"
    if os.path.exists(results_path) and os.path.exists(summary_path):
        # 再実行(resume): 前回runで既にTTSを実行済み(一部STOPPEDを含む
        # 場合もある)。ここでは全segmentを再生成せず、既存run_summary_
        # tts.jsonをそのまま返す(STOPPEDが残っていればrun_level()側の
        # retry_a2_stopped_segments()が対象segmentのみ再TTSする)。
        print(f"[AUDIO][{level}] TTS: 既存成果物を再利用(全segment再生成はしない): {results_path}")
        return load_json(summary_path)
    if level == "a2":
        tts_gen.JAPANESE_TITLES.update({THEME_ID: A2_JAPANESE_TITLE})
        print(f"[AUDIO][a2] JAPANESE_TITLES登録(人手供給・直訳、既存gap前例踏襲): {A2_JAPANESE_TITLE!r}")
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    with cl.logging_context(THEME_ID, f"tts_{level}"):
        if level == "b1b":
            result = tts_gen.generate_b1_segments(theme)
        else:
            result = tts_gen.generate_a2_segments(theme)
    return result


# ============================================================
# Step 3b: STOPPED segment再TTS(A2のみ想定。初回run結果、full_story_
# part1/2・point_one/point_two のいずれかがTRUE_CONTENT_MISMATCH等で
# "STOPPED"になった場合、既存Production関数
# tts_gen.generate_a2_segment_with_slowdown()自体は一切変更せず、同じ
# 引数(style_prefix_override=A2_ENGLISH_STYLE_PREFIX_SLOWER・
# enable_connected_speech_equivalence_layer=True・enable_repetition_qa=True、
# 本番run_a2_segments()内の該当segmentと同一設定)で再度呼ぶだけ(=人間が
# 「もう一度生成し直す」操作と同じ、既存の標準2回+fallback1回のASR
# retry機構自体は毎回内部でそのまま働く)。上限を超えて無限retryしない
# よう、driver側でA2_RETRY_MAX_ROUNDS回までに独自キャップする。
# ============================================================
A2_RETRY_MAX_ROUNDS = 2
A2_RETRYABLE_SEGMENTS = ("full_story_part1", "full_story_part2", "point_one", "point_two")


def retry_a2_stopped_segments(max_rounds: int = A2_RETRY_MAX_ROUNDS) -> dict:
    level_out_dir = f"{OUT_DIR}/a2"
    narration_dir = f"{level_out_dir}/narration"
    parts = load_json(f"{level_out_dir}/parts.json")
    results_path = f"{level_out_dir}/audit/tts_generation_results.json"
    summary_path = f"{level_out_dir}/run_summary_tts.json"

    seg_specs = {
        "full_story_part1": parts["part1"],
        "full_story_part2": parts["part2"],
        "point_one": parts["point_one_body"],
        "point_two": parts["point_two_body"],
    }
    rounds_log = []
    for round_i in range(1, max_rounds + 1):
        data = load_json(results_path)
        stopped = [n for n in A2_RETRYABLE_SEGMENTS if data["segments"].get(n, {}).get("status") != "OK"]
        if not stopped:
            break
        check_budget(f"tts_a2_retry_round{round_i}")
        print(f"[AUDIO][a2][retry round {round_i}] STOPPEDのまま再TTS対象: {stopped}")
        for name in stopped:
            text = seg_specs[name]
            if name in ("point_one", "point_two"):
                sc.assert_no_point_number_label(text, name)
            tts_input = tts_gen.tts_safe_news_en(text)
            with cl.logging_context(THEME_ID, "tts_a2_retry"):
                with cl.segment_context(name):
                    r = tts_gen.generate_a2_segment_with_slowdown(
                        tts_input, f"{narration_dir}/{name}.wav", tts_gen.first_words(text),
                        style_prefix_override=tts_gen.A2_ENGLISH_STYLE_PREFIX_SLOWER,
                        disfluency_qa=False,
                        enable_connected_speech_equivalence_layer=True,
                        enable_repetition_qa=True)
            r["canonical_text"] = text
            data["segments"][name] = r
            rounds_log.append({"round": round_i, "segment": name, "status": r.get("status")})
        save_json(results_path, data)
        summary = load_json(summary_path) if os.path.exists(summary_path) else {}
        summary["segment_status"] = {k: v.get("status") for k, v in data["segments"].items()}
        save_json(summary_path, summary)

    final = load_json(results_path)
    still_stopped = [n for n in A2_RETRYABLE_SEGMENTS if final["segments"].get(n, {}).get("status") != "OK"]
    return {"rounds_log": rounds_log, "still_stopped": still_stopped}


# ============================================================
# Step 3c: B1B STOPPED segment再TTS(A2と同型のretry。comment_1-4は
# voice01.generate_charon_english、full_story_part1/2・point_one/two・
# in_one_lineはnews_tail_fix.generate_news_narration_wide_margin、
# いずれも既存Production関数を無変更で同一引数のまま再度呼ぶだけ)。
# ============================================================
B1B_RETRY_MAX_ROUNDS = 2
B1B_COMMENT_SEGMENTS = ("comment_1", "comment_2", "comment_3", "comment_4")
B1B_NEWS_SEGMENTS = ("full_story_part1", "full_story_part2", "point_one", "point_two", "in_one_line")


def retry_b1b_stopped_segments(max_rounds: int = B1B_RETRY_MAX_ROUNDS) -> dict:
    level_out_dir = f"{OUT_DIR}/b1b"
    narration_dir = f"{level_out_dir}/narration"
    parts = load_json(f"{level_out_dir}/parts.json")
    support = load_json(f"{level_out_dir}/b1_support_texts.json")
    results_path = f"{level_out_dir}/audit/tts_generation_results.json"
    summary_path = f"{level_out_dir}/run_summary_tts.json"

    comment_texts = {n: support[n] for n in B1B_COMMENT_SEGMENTS}
    news_texts = {
        "full_story_part1": parts["part1"], "full_story_part2": parts["part2"],
        "point_one": parts["point_one_body"], "point_two": parts["point_two_body"],
        "in_one_line": parts["in_one_line"],
    }

    rounds_log = []
    for round_i in range(1, max_rounds + 1):
        data = load_json(results_path)
        stopped_comments = [n for n in B1B_COMMENT_SEGMENTS if data["segments"].get(n, {}).get("status") != "OK"]
        stopped_news = [n for n in B1B_NEWS_SEGMENTS if data["segments"].get(n, {}).get("status") != "OK"]
        if not stopped_comments and not stopped_news:
            break
        check_budget(f"tts_b1b_retry_round{round_i}")
        print(f"[AUDIO][b1b][retry round {round_i}] STOPPEDのまま再TTS対象: "
              f"comments={stopped_comments} news={stopped_news}")
        for name in stopped_comments:
            text = comment_texts[name]
            with cl.logging_context(THEME_ID, "tts_b1b_retry"):
                with cl.segment_context(name):
                    r = tts_gen.voice01.generate_charon_english(
                        text, f"{narration_dir}/{name}.wav",
                        style_prefix_override=tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM, disfluency_qa=True)
            r["canonical_text"] = text
            data["segments"][name] = r
            rounds_log.append({"round": round_i, "segment": name, "status": r.get("status")})
        for name in stopped_news:
            text = news_texts[name]
            if name in ("point_one", "point_two"):
                sc.assert_no_point_number_label(text, name)
            with cl.logging_context(THEME_ID, "tts_b1b_retry"):
                with cl.segment_context(name):
                    r = tts_gen.news_tail_fix.generate_news_narration_wide_margin(
                        tts_gen.tts_safe_news_en(text), f"{narration_dir}/{name}.wav",
                        disfluency_qa=(name == "in_one_line"),
                        enable_connected_speech_equivalence_layer=(
                            name in ("full_story_part1", "full_story_part2", "point_one", "point_two")),
                        enable_repetition_qa=(
                            name in ("full_story_part1", "full_story_part2", "point_one", "point_two")))
            r["canonical_text"] = text
            data["segments"][name] = r
            rounds_log.append({"round": round_i, "segment": name, "status": r.get("status")})
        save_json(results_path, data)
        summary = load_json(summary_path) if os.path.exists(summary_path) else {}
        summary["segment_status"] = {k: v.get("status") for k, v in data["segments"].items()}
        save_json(summary_path, summary)

    final = load_json(results_path)
    still_stopped = [n for n in (B1B_COMMENT_SEGMENTS + B1B_NEWS_SEGMENTS)
                      if final["segments"].get(n, {}).get("status") != "OK"]
    return {"rounds_log": rounds_log, "still_stopped": still_stopped}


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
# Step 5: Audio Validation Gate opt-in ON経路(read-only、
# Production関数asm.verify_episode_audio_validation_gate/
# asm.derive_a_family_required_structureを無変更で直接呼ぶ)
# ============================================================
def run_gate_opt_in_check(level: str) -> dict:
    level_out_dir = f"{OUT_DIR}/{level}"
    meta = LEVELS[level]
    rs = asm.derive_a_family_required_structure(meta["gate_level"])
    try:
        asm.verify_episode_audio_validation_gate(level_out_dir, meta["gate_level"], required_structure=rs)
        result = {"gate_on_result": "PASS"}
    except RuntimeError as e:
        result = {"gate_on_result": "BLOCKED", "gate_on_message": str(e)[:800]}
    save_json(f"{level_out_dir}/audit/gate_opt_in_check.json", result)
    save_json(f"{level_out_dir}/audio_validation.json", {
        "gate_off_result": "PASS", "gate_on_result": result["gate_on_result"],
        "gate_on_message": result.get("gate_on_message"), "gate_level": meta["gate_level"],
    })
    return result


# ============================================================
# Step 6: 記事⇔音声内容の一致確認(read-only)。article.mdからsplit_
# article_text()を再実行しparts.jsonと突合、かつTTS結果の各segmentの
# canonical_textがarticle由来であること・全content segmentがOK/
# verifiedであることを確認する。
# ============================================================
A2_CONTENT_SEGMENT_NAMES = (
    "topic_intro", "japanese_title", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
    "full_story_part1", "full_story_part2", "point_one_heading", "point_one", "point_two_heading",
    "point_two", "in_one_line",
)
B1B_CONTENT_SEGMENT_NAMES = (
    "topic_intro", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
    "full_story_part1", "full_story_part2", "point_one_heading", "point_one", "point_two_heading",
    "point_two", "in_one_line",
)


def build_consistency_check(level: str) -> dict:
    level_out_dir = f"{OUT_DIR}/{level}"
    article_text = open(f"{level_out_dir}/article.md", encoding="utf-8").read()
    recomputed_parts = sc.split_article_text(article_text)
    saved_parts = load_json(f"{level_out_dir}/parts.json")
    structure_match = recomputed_parts == saved_parts

    tts_results = load_json(f"{level_out_dir}/audit/tts_generation_results.json")
    seg = tts_results["segments"]
    names = A2_CONTENT_SEGMENT_NAMES if level == "a2" else B1B_CONTENT_SEGMENT_NAMES
    checked = []
    unverified = []
    for name in names:
        entry = seg.get(name)
        if entry is None:
            unverified.append({"segment": name, "reason": "MISSING"})
            continue
        status_ok = entry.get("status") == "OK" or entry.get("verified") is True
        checked.append({"segment": name, "status": entry.get("status"), "verified": entry.get("verified")})
        if not status_ok:
            unverified.append({"segment": name, "status": entry.get("status"), "verified": entry.get("verified")})

    kp_unverified = []
    kp_checked = []
    for rank, kpv in tts_results.get("key_phrases", {}).items():
        en_status = kpv["english"].get("status")
        ja_status = kpv["japanese_meaning"].get("status")
        kp_checked.append({"rank": rank, "en_status": en_status, "ja_status": ja_status})
        if en_status != "OK" or ja_status != "OK":
            kp_unverified.append({"rank": rank, "en_status": en_status, "ja_status": ja_status})

    result = {
        "level": level,
        "article_structure_roundtrip_match": structure_match,
        "content_segments_checked": checked,
        "content_segments_unverified": unverified,
        "key_phrases_checked": kp_checked,
        "key_phrases_unverified": kp_unverified,
        "all_pass": structure_match and not unverified and not kp_unverified,
        "note": ("article.mdを再読込しsplit_article_text()を再実行した結果とparts.json(TTS入力の元)が"
                 "byte-identicalであること、かつ全content segment/Key Phraseの生成ステータスがOK/"
                 "verifiedであることを確認した(既存Production TTS関数内部でASR verify済みのため、"
                 "本チェックはstatus/verifiedフラグの再確認+記事構造の再突合のみ行う)。"),
    }
    save_json(f"{level_out_dir}/article_audio_consistency.json", result)
    return result


# ============================================================
# Step 7: mp3変換(soundfile、既存前例[er011_family_a_trend_synthesis_
# ai_manufacturing_production_run_01_a2_player.py]と同一方式)+
# Web試聴player(相対パス参照のみ、file:///・絶対パス禁止)
# ============================================================
def wav_to_mp3(src_wav_path: str, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    data, sr = sf.read(src_wav_path)
    sf.write(out_path, data, sr, format="MP3")


def canonical_text_of(entry: dict) -> str:
    return entry.get("canonical_text") or entry.get("text", "")


def build_player_and_web_delivery(level: str, assemble_summary: dict) -> dict:
    level_out_dir = f"{OUT_DIR}/{level}"
    web_dir = f"{level_out_dir}/web"
    seg_dir = f"{web_dir}/segments"
    os.makedirs(seg_dir, exist_ok=True)

    tts_results = load_json(f"{level_out_dir}/audit/tts_generation_results.json")
    timeline = load_json(f"{level_out_dir}/audit/timeline.json")
    kp_canon = load_json(f"{level_out_dir}/key_phrases/keywords_canonicalized.json")
    parts = load_json(f"{level_out_dir}/parts.json")
    seg = tts_results["segments"]
    kp_items_by_rank = {it["rank"]: it for it in kp_canon["items"]}
    start_by_part = {t["part"]: t["start_seconds"] for t in timeline}

    def seg_audio_rel(name: str) -> str:
        src = f"{level_out_dir}/narration/{name}.wav"
        out_path = f"{seg_dir}/{name}.mp3"
        wav_to_mp3(src, out_path)
        return f"web/segments/{name}.mp3"

    rows = []

    def add(part_name: str, label: str, voice: str, script_html: str, audio_names):
        sec = start_by_part.get(part_name)
        if sec is None:
            return
        if audio_names is None:
            audio_html = "—"
        else:
            if isinstance(audio_names, (list, tuple)):
                urls = [seg_audio_rel(n) for n in audio_names]
            else:
                urls = seg_audio_rel(audio_names)
            audio_html = arp.render_single_audio_html(urls)
        rows.append(arp.render_timeline_row(sec, label, voice, script_html, audio_html,
                                             missing=(audio_names is None)))

    add("Intro", "Intro", "—(SFX)", "音楽ジングル(ナレーションなし、固定音源)", None)

    if level == "a2":
        add("Welcome", "Welcome", "Charon(固定文言)", shared_narration.FIXED_ENGLISH_TEXTS["welcome"], "welcome")
        add("Topic intro", "Topic intro", "Aoede(英語)", canonical_text_of(seg["topic_intro"]), "topic_intro")
        add("Japanese title", "Japanese title", "Aoede(日本語)", canonical_text_of(seg["japanese_title"]),
            "japanese_title")
        add("Notification 1", "Notification 1", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
        add("Preview intro", "Preview intro", "Charon(固定文言)", shared_narration.FIXED_ENGLISH_TEXTS["preview_intro"],
            "preview_intro")
        add("Point explanation", "Point explanation", "Charon(固定文言、日本語)",
            shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY["point_explanation"], "point_explanation")
        add("Preview", "Preview", "Aoede(日本語)", canonical_text_of(seg["preview"]), "preview")
        add("Notification 2", "Notification 2", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
        add("Key phrases intro", "Key phrases intro", "Charon(固定文言)",
            shared_narration.FIXED_ENGLISH_TEXTS["key_phrases_intro"], "key_phrases_intro")
        for rank in range(1, 6):
            item = kp_items_by_rank[rank]
            ja_gloss = item["japanese_gloss"]
            ja_gloss_tts = item.get("japanese_gloss_tts", ja_gloss)
            gloss_note = "" if ja_gloss_tts == ja_gloss else f"(TTS読み上げ用: {ja_gloss_tts})"
            add(f"Key Phrase {rank}", f"Key Phrase {rank}", "Aoede(英語+日本語)",
                f"英語: {item['used_form']}<br>日本語gloss(表示用): {ja_gloss}{gloss_note}",
                [f"kp{rank}_en", f"meaning_{rank}"])
        add("Notification 3", "Notification 3", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
        add("Full story intro", "Full story intro", "Charon(固定文言)",
            shared_narration.FIXED_ENGLISH_TEXTS["full_story_intro"], "full_story_intro")
        add("Comment 1", "Comment 1", "Aoede(日本語)", canonical_text_of(seg["comment_1"]), "comment_1")
        add("Full Story Part 1", "Full Story Part 1", "Aoede(英語)",
            canonical_text_of(seg["full_story_part1"]).replace("\n", "<br>"), "full_story_part1")
        add("Comment 2", "Comment 2", "Aoede(日本語)", canonical_text_of(seg["comment_2"]), "comment_2")
        add("Full Story Part 2", "Full Story Part 2", "Aoede(英語)",
            canonical_text_of(seg["full_story_part2"]).replace("\n", "<br>"), "full_story_part2")
        add("Comment 3", "Comment 3", "Aoede(日本語)", canonical_text_of(seg["comment_3"]), "comment_3")
        add("Point Notification (Point One cue)", "Point Notification(Point One)", "—(SFX)",
            "効果音(読み上げなし、固定音源)", None)
        add("Point One semantic heading", "Point One heading", "Aoede(英語、わずかに減速)",
            canonical_text_of(seg["point_one_heading"]), "point_one_heading")
        add("Point One", "Point One", "Aoede(英語、わずかに減速)", canonical_text_of(seg["point_one"]), "point_one")
        add("Point Notification (Point Two cue)", "Point Notification(Point Two)", "—(SFX)",
            "効果音(読み上げなし、固定音源)", None)
        add("Point Two semantic heading", "Point Two heading", "Aoede(英語、わずかに減速)",
            canonical_text_of(seg["point_two_heading"]), "point_two_heading")
        add("Point Two", "Point Two", "Aoede(英語、わずかに減速)", canonical_text_of(seg["point_two"]), "point_two")
        add("Comment 4", "Comment 4", "Aoede(日本語)", canonical_text_of(seg["comment_4"]), "comment_4")
        add("In One Line", "In One Line", "Aoede(英語、わずかに減速)", canonical_text_of(seg["in_one_line"]),
            "in_one_line")
        add("Outro", "Outro", "—(SFX)", "音楽ジングル(ナレーションなし、固定音源)", None)
    else:
        add("Welcome (Charon)", "Welcome (Charon)", "Charon(固定文言)",
            shared_narration.FIXED_ENGLISH_TEXTS["welcome"], "welcome_charon")
        add("Topic intro (Charon)", "Topic intro (Charon)", "Charon(英語)",
            canonical_text_of(seg["topic_intro"]), "topic_intro")
        add("Notification 1", "Notification 1", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
        add("Preview intro (Charon)", "Preview intro (Charon)", "Charon(固定文言)",
            shared_narration.FIXED_ENGLISH_TEXTS["preview_intro"], "preview_intro_charon")
        add("Preview (Charon)", "Preview (Charon)", "Charon(英語)", canonical_text_of(seg["preview"]), "preview")
        add("Notification 2", "Notification 2", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
        add("Key phrases intro (Charon)", "Key phrases intro (Charon)", "Charon(固定文言)",
            shared_narration.FIXED_ENGLISH_TEXTS["key_phrases_intro"], "key_phrases_intro_charon")
        for rank in range(1, 6):
            item = kp_items_by_rank[rank]
            add(f"Key Phrase {rank}", f"Key Phrase {rank}", "Aoede(英語)/Charon(日本語)",
                f"英語: {item['used_form']}<br>日本語gloss: {item['japanese_gloss']}",
                [f"kp{rank}_en", f"kp{rank}_ja_charon"])
        add("Notification 3", "Notification 3", "—(SFX)", "効果音(読み上げなし、固定音源)", None)
        add("Full story intro (Charon)", "Full story intro (Charon)", "Charon(固定文言)",
            shared_narration.FIXED_ENGLISH_TEXTS["full_story_intro"], "full_story_intro_charon")
        add("Comment 1 (Charon)", "Comment 1 (Charon)", "Charon(英語)", canonical_text_of(seg["comment_1"]),
            "comment_1")
        add("Full Story Part 1 (Aoede)", "Full Story Part 1 (Aoede)", "Aoede(英語)",
            canonical_text_of(seg["full_story_part1"]).replace("\n", "<br>"), "full_story_part1")
        add("Comment 2 (Charon)", "Comment 2 (Charon)", "Charon(英語)", canonical_text_of(seg["comment_2"]),
            "comment_2")
        add("Full Story Part 2 (Aoede)", "Full Story Part 2 (Aoede)", "Aoede(英語)",
            canonical_text_of(seg["full_story_part2"]).replace("\n", "<br>"), "full_story_part2")
        add("Comment 3 (Charon, Bridge)", "Comment 3 (Charon, Bridge)", "Charon(英語)",
            canonical_text_of(seg["comment_3"]), "comment_3")
        add("Point Notification (Point One cue)", "Point Notification(Point One)", "—(SFX)",
            "効果音(読み上げなし、固定音源)", None)
        add("Point One semantic heading (Aoede)", "Point One heading (Aoede)", "Aoede(英語)",
            canonical_text_of(seg["point_one_heading"]), "point_one_heading")
        add("Point One (Aoede)", "Point One (Aoede)", "Aoede(英語)", canonical_text_of(seg["point_one"]),
            "point_one")
        add("Point Notification (Point Two cue)", "Point Notification(Point Two)", "—(SFX)",
            "効果音(読み上げなし、固定音源)", None)
        add("Point Two semantic heading (Aoede)", "Point Two heading (Aoede)", "Aoede(英語)",
            canonical_text_of(seg["point_two_heading"]), "point_two_heading")
        add("Point Two (Aoede)", "Point Two (Aoede)", "Aoede(英語)", canonical_text_of(seg["point_two"]),
            "point_two")
        add("Comment 4 (Charon)", "Comment 4 (Charon)", "Charon(英語)", canonical_text_of(seg["comment_4"]),
            "comment_4")
        add("In One Line (Aoede)", "In One Line (Aoede)", "Aoede(英語)", canonical_text_of(seg["in_one_line"]),
            "in_one_line")
        add("Outro (Charon)", "Outro (Charon)", "—(SFX)", "音楽ジングル(ナレーションなし、固定音源)", None)

    episode_mp3_path = f"{web_dir}/episode.mp3"
    wav_to_mp3(assemble_summary["out_path"], episode_mp3_path)
    episode_rel = "web/episode.mp3"

    level_label = "A2" if level == "a2" else "B1-B"
    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>USER-TEST-AUDIO-COMPLETION-01-TREND {level_label}</title>
<style>
{arp.PLAYER_STANDARD_CSS}
</style>
</head>
<body>
<h1>USER-TEST-AUDIO-COMPLETION-01-TREND — Level: {level_label} — 完成episode音声</h1>
<p class="note">
記事: 「{parts.get('title')}」(Trend Synthesis、本文は再生成していない。
出典: er014_output/four_type_observation_01/trend/{level}/article.md)。
duration={assemble_summary['duration_seconds']}s / peak={assemble_summary['peak']} /
clipping={assemble_summary['clipping_detected']}。
音声はmp3変換のみ(このplayerと同階層のweb/配下へ新規変換)、
リンクは全て相対パス参照(file:///・絶対パス不使用)。
</p>
<audio id="episode_audio" class="main" controls preload="none" src="{episode_rel}"></audio>

<h2>{level_label} タイムライン・全スクリプト・Key Phrase(実際に読み上げられた内容、収録順)</h2>
{arp.render_timeline_table(rows)}

<h2>{level_label} 記事全文(article.md)</h2>
<pre class="article">{_html_escape(open(f"{level_out_dir}/article.md", encoding="utf-8").read())}</pre>

<script>
{arp.SEEK_SCRIPT}
</script>
</body>
</html>
"""
    player_path = f"{level_out_dir}/player.html"
    with open(player_path, "w", encoding="utf-8") as f:
        f.write(html)

    mp3_files = [episode_mp3_path] + [f"{seg_dir}/{fn}" for fn in os.listdir(seg_dir)]
    mp3_manifest = []
    for p in mp3_files:
        size_bytes = os.path.getsize(p)
        data, sr = sf.read(p)
        duration_s = round(len(data) / sr, 3)
        mp3_manifest.append({"path": p.replace("\\", "/"), "size_bytes": size_bytes,
                              "size_mb": round(size_bytes / (1024 * 1024), 3), "duration_seconds": duration_s})
    return {"level": level, "player_path": player_path, "mp3_manifest": mp3_manifest}


def _html_escape(s: str) -> str:
    import html as html_mod
    return html_mod.escape(s)


# ============================================================
# 実行本体
# ============================================================
def run_level(level: str) -> dict:
    print(f"===== [AUDIO] level={level} 開始 =====")
    check_budget(f"scaffold_{level}")
    article_text = prepare_article(level)
    run_scaffold(level, article_text)

    check_budget(f"keyphrase_{level}")
    kp_result = prepare_key_phrases(level, article_text)

    check_budget(f"tts_{level}")
    tts_result = run_tts(level)

    retry_result = None
    if level == "a2":
        stopped_now = [n for n in A2_RETRYABLE_SEGMENTS
                       if tts_result.get("segment_status", {}).get(n) != "OK"]
        if stopped_now:
            print(f"[AUDIO][a2] TTS初回でSTOPPEDのsegmentを検出: {stopped_now}。"
                  f"既存Production関数を同一引数で最大{A2_RETRY_MAX_ROUNDS}回まで再実行する。")
            retry_result = retry_a2_stopped_segments()
            if retry_result["still_stopped"]:
                raise RuntimeError(
                    f"[a2] STOP: {A2_RETRY_MAX_ROUNDS}回再TTSしてもsegment "
                    f"{retry_result['still_stopped']}がSTOPPEDのままです(既存retry/fallback機構が既に"
                    "使い切られている状態。上限回数を独自判断でさらに引き上げない。ユーザー判断が必要)。")
    elif level == "b1b":
        stopped_now = [n for n in (B1B_COMMENT_SEGMENTS + B1B_NEWS_SEGMENTS)
                       if tts_result.get("segment_status", {}).get(n) != "OK"]
        if stopped_now:
            print(f"[AUDIO][b1b] TTS初回でSTOPPEDのsegmentを検出: {stopped_now}。"
                  f"既存Production関数を同一引数で最大{B1B_RETRY_MAX_ROUNDS}回まで再実行する。")
            retry_result = retry_b1b_stopped_segments()
            if retry_result["still_stopped"]:
                raise RuntimeError(
                    f"[b1b] STOP: {B1B_RETRY_MAX_ROUNDS}回再TTSしてもsegment "
                    f"{retry_result['still_stopped']}がSTOPPEDのままです(既存retry/fallback機構が既に"
                    "使い切られている状態。上限回数を独自判断でさらに引き上げない。ユーザー判断が必要)。")

    assemble_result = run_assembly(level)
    if assemble_result.get("gate_off_result") != "PASS":
        raise RuntimeError(f"[{level}] Assembly(Gate OFF経路)がPASSしませんでした、STOP: {assemble_result}")

    gate_on = run_gate_opt_in_check(level)
    consistency = build_consistency_check(level)
    web = build_player_and_web_delivery(level, assemble_result)

    return {
        "level": level, "kp_result": kp_result, "tts_result": tts_result, "retry_result": retry_result,
        "assemble_result": assemble_result, "gate_opt_in_result": gate_on,
        "consistency": consistency, "web": web,
        "cost_breakdown_jpy": cost_breakdown_by_stage(),
    }


def update_shared_outputs(level: str, level_result: dict) -> None:
    # cost_summary_audio.json(level別、stageカテゴリ別)
    cost_path = f"{OUT_DIR}/cost_summary_audio.json"
    cost_doc = load_json(cost_path) if os.path.exists(cost_path) else {"levels": {}}
    breakdown = level_result["cost_breakdown_jpy"]
    category_map = {"scaffold": "preview_comment_llm_jpy", "keyphrase": "key_phrase_llm_jpy",
                     "tts": "tts_jpy", "assemble": "other_jpy"}
    cat_totals = {"preview_comment_llm_jpy": 0.0, "key_phrase_llm_jpy": 0.0, "tts_jpy": 0.0, "other_jpy": 0.0}
    for stage, jpy in breakdown.items():
        prefix = stage.rsplit("_", 1)[0]
        cat = category_map.get(prefix, "other_jpy")
        cat_totals[cat] += jpy
    cat_totals = {k: round(v, 2) for k, v in cat_totals.items()}
    cat_totals["total_jpy"] = round(sum(cat_totals.values()), 2)
    cat_totals["raw_stage_breakdown_jpy"] = breakdown
    cost_doc["levels"][level] = cat_totals
    cost_doc["budget_jpy"] = BUDGET_JPY
    cost_doc["combined_total_jpy"] = round(sum(v["total_jpy"] for v in cost_doc["levels"].values()), 2)
    cost_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_json(cost_path, cost_doc)

    # web_delivery.json(level別mp3一覧+50MB以下確認)
    wd_path = f"{OUT_DIR}/web_delivery.json"
    wd_doc = load_json(wd_path) if os.path.exists(wd_path) else {"levels": {}}
    manifest = level_result["web"]["mp3_manifest"]
    over_50mb = [m for m in manifest if m["size_mb"] >= 50.0]
    wd_doc["levels"][level] = {
        "player_path": level_result["web"]["player_path"].replace("\\", "/"),
        "mp3_files": manifest, "all_under_50mb": len(over_50mb) == 0,
    }
    wd_doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_json(wd_path, wd_doc)

    # production_set_cost.json更新(既報¥174.03+音声化追加費)
    ps_path = f"{TREND_DIR}/production_set_cost.json"
    ps_doc = load_json(ps_path)
    base_total = ps_doc.get("production_set_total_cost_jpy", 174.03)
    audio_total_all_levels = cost_doc["combined_total_jpy"]
    ps_doc["audio_completion_cost_jpy"] = audio_total_all_levels
    ps_doc["audio_completion_cost_by_level_jpy"] = {
        lvl: v["total_jpy"] for lvl, v in cost_doc["levels"].items()
    }
    ps_doc["production_set_total_cost_including_audio_jpy"] = round(174.03 + audio_total_all_levels, 2)
    ps_doc["audio_completion_note"] = (
        "USER-TEST-AUDIO-COMPLETION-01-TREND: 既存正式audio completion経路(er003_v1_n3_01_scaffold_generate/"
        "tts_generate/assemble、無変更)でA2/B1B完成episode+Web試聴playerまで仕上げた追加費用。"
        "本文Writer/Fact Checker/QA(¥174.03)には50:50配賦しない。"
    )
    save_json(ps_path, ps_doc)


def append_progress_log(level: str, level_result: dict) -> None:
    log_path = f"er014_output/four_type_observation_01/progress_log.md"
    now = datetime.now(timezone.utc).isoformat()
    duration = level_result["assemble_result"].get("duration_seconds")
    gate_on = level_result["gate_opt_in_result"].get("gate_on_result")
    all_pass = level_result["consistency"].get("all_pass")
    line = (f"- Trend audio completion ({level}): {now} 完了, gate_off=PASS, gate_on={gate_on}, "
            f"duration={duration}s, article_audio_consistency_all_pass={all_pass}, "
            f"level_cost_jpy={sum(level_result['cost_breakdown_jpy'].values()):.2f} "
            f"(管理ID: USER-TEST-AUDIO-COMPLETION-01-TREND)\n")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["a2", "b1b"], required=True)
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(LOG_PATH)

    t0 = time.time()
    level_result = run_level(args.level)
    update_shared_outputs(args.level, level_result)
    append_progress_log(args.level, level_result)
    elapsed = round(time.time() - t0, 1)

    save_json(f"{OUT_DIR}/{args.level}/run_result_audio_completion.json", {
        "level": args.level, "elapsed_seconds": elapsed,
        "gate_off_result": level_result["assemble_result"].get("gate_off_result"),
        "gate_on_result": level_result["gate_opt_in_result"].get("gate_on_result"),
        "duration_seconds": level_result["assemble_result"].get("duration_seconds"),
        "consistency_all_pass": level_result["consistency"].get("all_pass"),
        "cost_breakdown_jpy": level_result["cost_breakdown_jpy"],
        "cost_total_jpy": round(sum(level_result["cost_breakdown_jpy"].values()), 2),
    })
    print(f"===== [AUDIO] level={args.level} 完了(elapsed={elapsed}s) =====")


if __name__ == "__main__":
    main()
