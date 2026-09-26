# ============================================================
# er015_standard_a2_6000_generation_first_trial_01.py
# STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01 (Trialのみ、最大VALIDATED、
# Production Prompt/pathは一切変更しない、2026-09-26)
# ============================================================
# 目的: VOCAB-ABCD-STRICT-EXCEPTION-TRIAL-01で判明した「難語を個別に事後
# 置換すると意味変化・冗長化・不自然化が起きる」という問題を受け、A/B/C/D
# 例外分類をさらに複雑化する方向を止め、代わりに「Standard記事を生成する
# 時点で最初から約6,000語中心の自然なA2英語として書き直す」方式(生成一体型、
# generation-first)が機能するかを検証する。
#
# 比較条件:
#   A(Control): 現行Production候補Standard A2 v5 Prompt
#     (er003_v1_n3_01_standard_a2_generate.STANDARD_A2_PROMPT_V5、一字一句
#     無変更のまま`generate_standard_a2()`を直接呼び出す)。
#   B(Trial): Aと同じ構造契約・同じDEVELOPER・同じmodel/effort・同じ
#     retry primitiveだが、語彙段落のみを「生成一体型」指示へ差し替えた
#     Trial専用Prompt(GEN_FIRST_PROMPT_V1、本ファイル内定数)。
#     構築方法: STANDARD_A2_PROMPT_V5から語彙段落の逐語部分文字列
#     (_OLD_VOCAB_BLOCK)だけをstr.replace()で置換する(それ以外の一字一句
#     ---タイトル/文長指示/Story保持/Fact保持/構造契約/出力形式/[Article]
#     テンプレート---はA/Bで完全に同一であることをコードで保証する。
#     置換元テキストが変わっていた場合はimport時にRuntimeErrorでSTOPする)。
#
# 入力Advanced記事(重要な由来確認、委任文の指示に基づく事前調査結果):
#   委任文はer015_output/vocab_abcd_strict_exception_trial_01/
#   advanced_meta_before.md / advanced_sewer_before.mdを入力候補として
#   提示していたが、事前調査で以下が判明したため、本Trialでは使用せず、
#   日本語R2原文からAdvanced v2 Production Prompt
#   (er003_v1_n3_01_advanced_adaptation_generate.generate_advanced_adaptation)
#   を直接呼び出して両記事を新規に再生成する:
#     (1) advanced_sewer_before.md(実体= er015_output/
#         news_natural_advanced_standard_a2_trial_01/a1_advanced_sewer.md)
#         は、Advanced v2 Production Prompt(PROCESS_LABEL=
#         NATURAL_ENGLISH_ADAPTATION)ではなく、その前身であるTrial
#         (NEWS-JA-TO-EN-ADAPTATION-TRIAL-01 arm3 "Natural English"、
#         Sewer固有のpreserve bullet文言)で生成されたものであり、現行
#         Advanced v2 Prompt(語彙ルールv2ブロックを含む)とは異なる。
#     (2) advanced_meta_before.md(実体= er012_output/
#         e_family_two_level_wiring_01/meta/b1b/article.md)は
#         er012_e_family_entertainment_two_level_runner_01.py経由で
#         Advanced v2 Production関数を直接呼び出して生成された点は正しい
#         (git blame/entry_point.json/生成コードで確認済み)。ただし生成
#         コミット(0e028301、2026-09-25)は、語彙ルールv2をProductionへ
#         組み込んだコミット(7c93d146、ADVANCED-VOCAB-V2-PRODUCTION-
#         RESTORE-01)より**前**であり、現行(語彙ルールv2込み)の
#         Advanced v2 Production Promptの出力ではない。
#   上記(1)(2)により、Meta/Sewerとも「現行Advanced v2 Production Prompt」
#   の出力として整合性のある入力を得るため、両記事とも同日・同モジュールで
#   新規に再生成する(日本語原文は変更しない、Fact変更なし、Production
#   moduleは一切変更しない、読み取り専用のimportのみ)。
#   日本語R2原文(APPROVED_FOR_PRODUCTION、配線未完了、Fact変更なし):
#     - Meta:  docs/evidence/news_iterative_r2_adoption_2026-09-24/
#              articles/ai_phone_revision2.md
#     - Sewer: docs/evidence/news_iterative_r2_adoption_2026-09-24/
#              articles/sewer_revision2.md
#
# 依存(re-use、新規ロジックはGEN_FIRST_PROMPT_V1本文・分析集計のみ):
#   - er003_v1_n3_01_standard_a2_generate (std_gen): STANDARD_A2_PROMPT_V5
#     / STANDARD_A2_DEVELOPER / generate_standard_a2 / run_checks /
#     _load_pricing / _compute_cost_jpy (Production module、無変更で再利用)
#   - er003_v1_n3_01_advanced_adaptation_generate (adv_gen):
#     generate_advanced_adaptation (Production module、無変更で再利用)
#   - er003_v1_en_direct_vfl_01_generate (vfl01): get_client /
#     run_writer_with_technical_retry / REASONING_EFFORT (既存Production
#     primitive、B呼び出しにもAと同一のretry機構を使う)
#   - er006_model_routing_contract_01 (routing): require_model
#   - er015_advanced_vocab_rule_trial_01 (v1trial): out_path/save_text/
#     load_text/save_json/load_json/get_client/_rank_of_map/_format_rank
#   - er015_advanced_vocab_rule_trial_01_v2 (v2mod): lemma_candidates_v2/
#     rank_of_word_v2/fact_tokens_check(Standard/Advanced両方で使われて
#     いる既存ロジックをそのまま流用、思想差ゼロを維持)
#   - er015_vocab_abcd_strict_exception_trial_01 (strict_mod):
#     build_candidates(rank=min(surface,lemma)、閾値パラメータ化版)
#   - er015_news_natural_advanced_standard_a2_trial_01 (v1mod、v2mod.v3mod
#     経由): _level_metrics/_strip_title(語数・平均文長・FK概算等の客観
#     指標)
#
# 固定: 6 call(Advanced regen: Meta/Sewer 2回 + Standard A/B: Meta/Sewer
# 各2回=4回)。previous_response_idなし、Web Searchなし、model=
# gpt-5.6-luna、reasoning effort=high。費用上限(Guardrail、暴走防止):
# JPY 40円。超過見込みが判明した時点でSTOPして報告する(PM_GOVERNANCE
# 7-6)。TTSは使用しない(TTS_EXECUTION_MODE=該当なし、TTS call 0)。
#
# 採否推奨はコード側・REPORT側どちらにも書かない(ユーザーが記事本文を
# 読んで判断する)。本スクリプトはSonnetによる事後診断タグ付け
# (固有名詞/公式名称/主題語/意味精度/不要な難語)の材料となる客観データの
# 生成のみを行う。
#
# 実行方法:
#   .venv/Scripts/python.exe er015_standard_a2_6000_generation_first_trial_01.py \
#       --out-dir er015_output/standard_a2_6000_generation_first_trial_01 \
#       --step all
# ============================================================
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er003_v1_n3_01_standard_a2_generate as std_gen
import er006_model_routing_contract_01 as routing
import er015_advanced_vocab_rule_trial_01 as v1trial
import er015_advanced_vocab_rule_trial_01_v2 as v2mod
import er015_vocab_abcd_strict_exception_trial_01 as strict_mod

v3mod = v2mod.v3mod
v1mod = v3mod.v1mod

lemma_candidates_v2 = v2mod.lemma_candidates_v2
rank_of_word_v2 = v2mod.rank_of_word_v2
fact_tokens_check = v2mod.fact_tokens_check
level_metrics = v1mod._level_metrics
strip_title = v1mod._strip_title
extract_content_words = v3mod.extract_content_words
capitalized_positions = v3mod.capitalized_positions
build_candidates = strict_mod.build_candidates

out_path = v1trial.out_path
save_text = v1trial.save_text
load_text = v1trial.load_text
save_json = v1trial.save_json
load_json = v1trial.load_json
_rank_of_map = v1trial._rank_of_map
_format_rank = v1trial._format_rank

RANK_THRESHOLD = 6000
BORDERLINE_LOW = 5000
BORDERLINE_HIGH = 6000
BUDGET_JPY_CAP = 40.0

JA_SOURCE_PATHS = {
    "meta": os.path.join(
        "docs", "evidence", "news_iterative_r2_adoption_2026-09-24",
        "articles", "ai_phone_revision2.md"),
    "sewer": os.path.join(
        "docs", "evidence", "news_iterative_r2_adoption_2026-09-24",
        "articles", "sewer_revision2.md"),
}

# 由来確認済みの前回誤入力(参考記録のみ、本Trialでは使用しない)
PREVIOUS_MISATTRIBUTED_INPUT = {
    "meta": os.path.join(
        "er012_output", "e_family_two_level_wiring_01", "meta", "b1b",
        "article.md"),
    "sewer": os.path.join(
        "er015_output", "news_natural_advanced_standard_a2_trial_01",
        "a1_advanced_sewer.md"),
}


# ------------------------------------------------------------
# B(生成一体型)Prompt構築: STANDARD_A2_PROMPT_V5の語彙段落のみを置換
# ------------------------------------------------------------
_OLD_VOCAB_BLOCK = (
    "Prefer words within roughly the 6,000 most common English words.\n"
    "If a word is clearly outside that range, replace it when a simpler "
    "natural alternative exists.\n"
    "Do not force a replacement if it makes the sentence less natural or "
    "changes the meaning.\n"
    "Proper names are excluded from this rule.\n"
    "Essential technical terms may remain when a simpler equivalent would "
    "lose important meaning.\n"
    "Do not add an explanation for a hard word; make the sentence around "
    "it simple instead.\n"
    "Keep the metaphor words when they are simple enough for A2 learners "
    "(for example, stage, backstage, lead role, curtain)."
)

_NEW_VOCAB_BLOCK_GEN_FIRST = (
    "As a basic principle, write naturally using words within roughly the "
    "top 6,000 most common English words. Do not generate a hard word "
    "first and then swap out only that one word afterward; instead, from "
    "the first draft, build the whole sentence around simpler words so its "
    "meaning is expressed naturally from the start (for example: instead "
    "of writing a hard word X and later replacing just X, restructure the "
    "entire sentence around easy words that already carry the same "
    "meaning).\n"
    "Do not change the meaning: keep the same action, cause and effect, "
    "actor, object, quantity, time, and facts. A simplification that "
    "changes what actually happens (for example, turning \"flush\" into "
    "\"use\") is not allowed.\n"
    "Do not escape one hard word by repeatedly adding long, unnatural "
    "explanatory phrases; that makes the writing heavy. Keep it light and "
    "direct, the way the rest of the article already reads.\n"
    "Keep the storytelling: this is not a summary. Do not cut an "
    "interesting detail or part of the storyline, and do not mechanically "
    "remove a metaphor. Simplify only the wording, not the story.\n"
    "A true proper noun, an official name, a name essential to the "
    "article's subject, or a word whose simpler natural alternative would "
    "clearly break meaning precision may stay even if it is outside the "
    "top 6,000 words.\n"
    "Do not sort each word into fixed exception categories, and do not "
    "list candidate words or output a classification for each word. "
    "Writing one naturally good CEFR A2 article matters more than "
    "labeling exceptions."
)

if _OLD_VOCAB_BLOCK not in std_gen.STANDARD_A2_PROMPT_V5:
    raise RuntimeError(
        "[STOP] Production STANDARD_A2_PROMPT_V5の語彙段落テキストが想定と"
        "異なります。GEN_FIRST_PROMPT_V1の構築前提が崩れているため、"
        "サイレントに誤ったBプロンプトを使わないよう停止します。"
    )

GEN_FIRST_PROMPT_V1 = std_gen.STANDARD_A2_PROMPT_V5.replace(
    _OLD_VOCAB_BLOCK, _NEW_VOCAB_BLOCK_GEN_FIRST)

if GEN_FIRST_PROMPT_V1 == std_gen.STANDARD_A2_PROMPT_V5:
    raise RuntimeError("[STOP] GEN_FIRST_PROMPT_V1がA(Control)と同一です。")

GEN_FIRST_PROMPT_SHA256 = hashlib.sha256(
    GEN_FIRST_PROMPT_V1.encode("utf-8")).hexdigest()
CONTROL_PROMPT_SHA256_OBSERVED = hashlib.sha256(
    std_gen.STANDARD_A2_PROMPT_V5.encode("utf-8")).hexdigest()


def generate_standard_a2_gen_first(advanced_text: str, *, client=None,
                                    model: str | None = None,
                                    effort: str = "high",
                                    max_retries: int = 1) -> dict:
    """Aと同じ構造契約・DEVELOPER・model/effort・retry primitiveを使い、
    語彙段落だけをGEN_FIRST_PROMPT_V1(本ファイル内Trial専用定数)に差し
    替えて生成する。std_gen.generate_standard_a2()と同型の戻り値(dict)を
    返す(Production module自体は変更しない、呼び出しのみ独立実装)。"""
    if effort != vfl01.REASONING_EFFORT:
        raise ValueError(
            f"[STOP] effort='{effort}' はvfl01.REASONING_EFFORT="
            f"'{vfl01.REASONING_EFFORT}' と不一致です。")
    if client is None:
        client = vfl01.get_client()
    requested_model = model or routing.require_model(
        "STANDARD_A2_ADAPTATION", routing.WRITER_MODEL)

    prompt = GEN_FIRST_PROMPT_V1.format(advanced_article=advanced_text)
    price_fn = std_gen._load_pricing()

    t0 = time.time()
    result = vfl01.run_writer_with_technical_retry(
        client, prompt, max_attempts=max_retries + 1, model=requested_model,
        developer=std_gen.STANDARD_A2_DEVELOPER)
    elapsed = round(time.time() - t0, 3)

    if result["status"] not in ("STRUCTURE_PASS", "STRUCTURE_INVALID"):
        raise RuntimeError(
            f"[GEN_FIRST] {max_retries + 1}回試行しても生成に失敗しました: "
            f"status={result['status']} attempts={result['attempts']}")
    if result["status"] != "STRUCTURE_PASS":
        raise RuntimeError(
            f"[GEN_FIRST] {max_retries + 1}回試行してもcontract構造"
            f"(### 見出しちょうど2つ)を満たせませんでした: "
            f"attempts={result['attempts']}")

    text = result["raw_text"]
    model_actual = result["model"]
    response_id = result["response_id"]
    attempts_detail = result["attempts"]
    attempts = len(attempts_detail)
    retried = attempts > 1
    fallback_detected = (model_actual != requested_model)

    usage_dict = result.get("usage") or {}
    input_tokens = usage_dict.get("input_tokens")
    cached_tokens = usage_dict.get("cached_input_tokens")
    output_tokens = usage_dict.get("output_tokens")

    cost_usd, cost_jpy = std_gen._compute_cost_jpy(
        price_fn, model_actual, input_tokens or 0, cached_tokens or 0,
        output_tokens or 0)

    checks = std_gen.run_checks(advanced_text, text)

    return {
        "text": text,
        "model_id_actual": model_actual,
        "model_id_requested": requested_model,
        "response_id": response_id,
        "usage": usage_dict,
        "cost_usd": cost_usd,
        "cost_jpy": cost_jpy,
        "attempts": attempts,
        "retried": retried,
        "fallback_detected": fallback_detected,
        "elapsed_seconds": elapsed,
        "structure_status": result["status"],
        "checks": checks,
    }


# ------------------------------------------------------------
# 予算Guardrail(実行前チェック、超過見込み時はSTOP)
# ------------------------------------------------------------
def _running_total_jpy(out_dir: str) -> float:
    cost_path = out_path(out_dir, "cost_calls.json")
    if not os.path.exists(cost_path):
        return 0.0
    calls = load_json(cost_path)
    return sum(c.get("cost_jpy", 0.0) for c in calls)


def _append_call_cost(out_dir: str, call_record: dict) -> None:
    cost_path = out_path(out_dir, "cost_calls.json")
    calls = load_json(cost_path) if os.path.exists(cost_path) else []
    calls.append(call_record)
    save_json(cost_path, calls)


def _guard_budget(out_dir: str, estimated_next_call_jpy_ceiling: float = 5.0):
    total_so_far = _running_total_jpy(out_dir)
    if total_so_far + estimated_next_call_jpy_ceiling > BUDGET_JPY_CAP:
        raise RuntimeError(
            f"[STOP] 予算Guardrail超過見込み: 現在まで JPY {total_so_far:.4f} "
            f"+ 次callceiling見込み JPY {estimated_next_call_jpy_ceiling} > "
            f"上限 JPY {BUDGET_JPY_CAP}")


# ------------------------------------------------------------
# STEP: advanced (Meta/Sewer各1回、genuine Advanced v2 Production再生成)
# ------------------------------------------------------------
def cmd_advanced(out_dir: str, force: bool) -> None:
    os.makedirs(out_dir, exist_ok=True)
    client = vfl01.get_client()
    provenance = {}
    for key, ja_path in JA_SOURCE_PATHS.items():
        article_dir = out_path(out_dir, key)
        os.makedirs(article_dir, exist_ok=True)
        adv_out = out_path(article_dir, "advanced_input.md")
        raw_out = out_path(article_dir, "advanced_raw_response.json")
        if os.path.exists(adv_out) and os.path.exists(raw_out) and not force:
            print(f"[SKIP] advanced {key} already generated: {adv_out}")
            continue
        _guard_budget(out_dir, estimated_next_call_jpy_ceiling=5.0)
        ja_text = load_text(ja_path)
        ja_sha256_lf_normalized = hashlib.sha256(
            ja_text.encode("utf-8")).hexdigest()
        with open(ja_path, "rb") as f:
            ja_sha256_raw_bytes = hashlib.sha256(f.read()).hexdigest()

        result = adv_gen.generate_advanced_adaptation(ja_text, client=client)

        save_text(adv_out, result.text)
        save_json(raw_out, {
            "stage": f"advanced_{key}",
            "ja_article_path": ja_path,
            "ja_article_sha256_lf_normalized": ja_sha256_lf_normalized,
            "ja_article_sha256_raw_bytes": ja_sha256_raw_bytes,
            "model_requested": result.model_id_requested,
            "response_model_actual": result.model_id_actual,
            "fallback_detected": result.fallback_detected,
            "response_id": result.response_id,
            "usage": result.usage,
            "cost_usd": result.cost_usd,
            "cost_jpy": result.cost_jpy,
            "attempts": result.attempts,
            "retried": result.retried,
            "structure_status": result.structure_status,
            "elapsed_seconds": result.elapsed_seconds,
            "process_label": adv_gen.PROCESS_LABEL,
        })
        _append_call_cost(out_dir, {
            "stage": f"advanced_{key}", "cost_jpy": result.cost_jpy})
        provenance[key] = {
            "ja_article_path": ja_path,
            "ja_article_sha256_lf_normalized": ja_sha256_lf_normalized,
            "ja_article_sha256_raw_bytes": ja_sha256_raw_bytes,
            "advanced_output_path": adv_out,
            "advanced_output_sha256": hashlib.sha256(
                result.text.encode("utf-8")).hexdigest(),
            "response_id": result.response_id,
            "model_id_actual": result.model_id_actual,
            "retried": result.retried,
            "structure_status": result.structure_status,
        }
        print(f"[OK] advanced {key}: cost_jpy={result.cost_jpy} "
              f"retried={result.retried} status={result.structure_status}")
    prov_path = out_path(out_dir, "advanced_regeneration_provenance.json")
    existing = load_json(prov_path) if os.path.exists(prov_path) else {}
    existing.update(provenance)
    save_json(prov_path, existing)


# ------------------------------------------------------------
# STEP: generate (A/B、Meta/Sewer各2回)
# ------------------------------------------------------------
def cmd_generate(out_dir: str, force: bool) -> None:
    client = vfl01.get_client()
    for key in ("meta", "sewer"):
        article_dir = out_path(out_dir, key)
        adv_path = out_path(article_dir, "advanced_input.md")
        if not os.path.exists(adv_path):
            raise RuntimeError(
                f"[STOP] {adv_path} が存在しません。先に --step advanced を"
                "実行してください。")
        advanced_text = load_text(adv_path)

        # --- A (Control) ---
        a_out = out_path(article_dir, "a_v5.md")
        a_raw = out_path(article_dir, "a_v5_raw_response.json")
        if os.path.exists(a_out) and os.path.exists(a_raw) and not force:
            print(f"[SKIP] A {key} already generated: {a_out}")
        else:
            _guard_budget(out_dir, estimated_next_call_jpy_ceiling=5.0)
            a_result = std_gen.generate_standard_a2(advanced_text, client=client)
            save_text(a_out, a_result.text)
            save_json(a_raw, {
                "stage": f"a_v5_{key}",
                "model_requested": a_result.model_id_requested,
                "response_model_actual": a_result.model_id_actual,
                "fallback_detected": a_result.fallback_detected,
                "response_id": a_result.response_id,
                "usage": a_result.usage,
                "cost_usd": a_result.cost_usd,
                "cost_jpy": a_result.cost_jpy,
                "attempts": a_result.attempts,
                "retried": a_result.retried,
                "structure_status": a_result.structure_status,
                "elapsed_seconds": a_result.elapsed_seconds,
                "checks": a_result.checks,
                "prompt_sha256": std_gen.STANDARD_A2_PROMPT_SHA256,
            })
            _append_call_cost(out_dir, {
                "stage": f"a_v5_{key}", "cost_jpy": a_result.cost_jpy})
            print(f"[OK] A {key}: cost_jpy={a_result.cost_jpy} "
                  f"retried={a_result.retried} "
                  f"status={a_result.structure_status}")

        # --- B (Gen-First) ---
        b_out = out_path(article_dir, "b_gen_first.md")
        b_raw = out_path(article_dir, "b_gen_first_raw_response.json")
        if os.path.exists(b_out) and os.path.exists(b_raw) and not force:
            print(f"[SKIP] B {key} already generated: {b_out}")
        else:
            _guard_budget(out_dir, estimated_next_call_jpy_ceiling=5.0)
            b_result = generate_standard_a2_gen_first(
                advanced_text, client=client)
            save_text(b_out, b_result["text"])
            save_json(b_raw, {
                "stage": f"b_gen_first_{key}",
                "model_requested": b_result["model_id_requested"],
                "response_model_actual": b_result["model_id_actual"],
                "fallback_detected": b_result["fallback_detected"],
                "response_id": b_result["response_id"],
                "usage": b_result["usage"],
                "cost_usd": b_result["cost_usd"],
                "cost_jpy": b_result["cost_jpy"],
                "attempts": b_result["attempts"],
                "retried": b_result["retried"],
                "structure_status": b_result["structure_status"],
                "elapsed_seconds": b_result["elapsed_seconds"],
                "checks": b_result["checks"],
                "prompt_sha256": GEN_FIRST_PROMPT_SHA256,
            })
            _append_call_cost(out_dir, {
                "stage": f"b_gen_first_{key}",
                "cost_jpy": b_result["cost_jpy"]})
            print(f"[OK] B {key}: cost_jpy={b_result['cost_jpy']} "
                  f"retried={b_result['retried']} "
                  f"status={b_result['structure_status']}")


# ------------------------------------------------------------
# STEP: analyze (残存語・Fact/意味差・客観指標)
# ------------------------------------------------------------
def _residual_words(text: str, rank_of: dict) -> list:
    """threshold(6,000)超(top20000圏外含む)の残存語一覧(固有名詞候補も
    含めてすべて列挙、rank付き)。build_candidatesのcandidates
    (非固有名詞・閾値超)+excluded_proper_nouns(固有名詞候補、閾値超のみ
    抽出)を統合する。"""
    result = build_candidates(
        text, rank_of, RANK_THRESHOLD, BORDERLINE_LOW, BORDERLINE_HIGH)
    residual = list(result["candidates"])
    for e in result["excluded_proper_nouns"]:
        if e["rank"] is None or e["rank"] > RANK_THRESHOLD:
            e2 = dict(e)
            e2["proper_noun_candidate"] = True
            residual.append(e2)
    for e in residual:
        e.setdefault("proper_noun_candidate", False)

    def sort_key(e):
        return (0, e["zipf_frequency"]) if e["rank"] is None else (1, e["rank"])
    residual.sort(key=sort_key)
    return residual


def _paragraph_count(text: str) -> int:
    _, body = strip_title(text)
    paras = [p for p in body.split("\n\n") if p.strip()]
    return len(paras)


def cmd_analyze(out_dir: str) -> None:
    import wordfreq
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = _rank_of_map(top20000)

    for key in ("meta", "sewer"):
        article_dir = out_path(out_dir, key)
        advanced_text = load_text(out_path(article_dir, "advanced_input.md"))
        a_text = load_text(out_path(article_dir, "a_v5.md"))
        b_text = load_text(out_path(article_dir, "b_gen_first.md"))

        analysis = {"article": key}
        for label, text in (("advanced", advanced_text), ("a_v5", a_text),
                             ("b_gen_first", b_text)):
            residual = _residual_words(text, rank_of)
            metrics = level_metrics(text)
            analysis[label] = {
                "level_metrics": metrics,
                "paragraph_count": _paragraph_count(text),
                "residual_word_count_over_6000": len(residual),
                "residual_words": [
                    {
                        "word": e["word"],
                        "actual_form": e["actual_form"],
                        "count": e["count"],
                        "rank": e["rank"],
                        "rank_source": e["rank_source"],
                        "rank_display": e["rank_display"],
                        "proper_noun_candidate": e["proper_noun_candidate"],
                    }
                    for e in residual
                ],
            }

        analysis["fact_tokens_check_advanced_vs_a"] = fact_tokens_check(
            advanced_text, a_text)
        analysis["fact_tokens_check_advanced_vs_b"] = fact_tokens_check(
            advanced_text, b_text)

        save_json(out_path(article_dir, "analysis_data.json"), analysis)
        print(f"[OK] analyze {key}: "
              f"A residual={analysis['a_v5']['residual_word_count_over_6000']} "
              f"B residual={analysis['b_gen_first']['residual_word_count_over_6000']}")


# ------------------------------------------------------------
# STEP: assemble (cost.json / runtime_evidence.json / prompt_diff)
# ------------------------------------------------------------
def cmd_assemble(out_dir: str) -> None:
    calls_path = out_path(out_dir, "cost_calls.json")
    calls = load_json(calls_path) if os.path.exists(calls_path) else []
    total_cost_jpy = round(sum(c.get("cost_jpy", 0.0) for c in calls), 4)
    save_json(out_path(out_dir, "cost.json"), {
        "calls": calls,
        "total_cost_jpy": total_cost_jpy,
        "budget_jpy_guardrail": BUDGET_JPY_CAP,
        "within_budget": total_cost_jpy <= BUDGET_JPY_CAP,
    })

    runtime_evidence = {"calls": []}
    for key in ("meta", "sewer"):
        article_dir = out_path(out_dir, key)
        for stage_file in ("advanced_raw_response.json", "a_v5_raw_response.json",
                            "b_gen_first_raw_response.json"):
            p = out_path(article_dir, stage_file)
            if os.path.exists(p):
                d = load_json(p)
                runtime_evidence["calls"].append({
                    "article": key,
                    "stage": d.get("stage"),
                    "model_requested": d.get("model_requested"),
                    "response_model_actual": d.get("response_model_actual"),
                    "fallback_detected": d.get("fallback_detected"),
                    "response_id": d.get("response_id"),
                    "retried": d.get("retried"),
                    "attempts": d.get("attempts"),
                    "structure_status": d.get("structure_status"),
                })
    save_json(out_path(out_dir, "runtime_evidence.json"), runtime_evidence)

    diff_lines = list(difflib.unified_diff(
        std_gen.STANDARD_A2_PROMPT_V5.splitlines(keepends=True),
        GEN_FIRST_PROMPT_V1.splitlines(keepends=True),
        fromfile="A (Control, Standard v5 Production Prompt, unchanged)",
        tofile="B (Trial, Generation-First 6000)"))
    diff_md = (
        "# prompt_diff_a_vs_b.md\n\n"
        "STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01\n\n"
        f"A sha256(観測値, Production定数`STANDARD_A2_PROMPT_SHA256`とは"
        f"正規化方式が異なる可能性があるため'観測値'と明記)="
        f"{CONTROL_PROMPT_SHA256_OBSERVED}\n\n"
        f"B sha256={GEN_FIRST_PROMPT_SHA256}\n\n"
        "## A(Control)全文\n\n```text\n" + std_gen.STANDARD_A2_PROMPT_V5 +
        "\n```\n\n"
        "## B(Trial、Generation-First)全文\n\n```text\n" +
        GEN_FIRST_PROMPT_V1 + "\n```\n\n"
        "## 逐語diff(unified diff)\n\n```diff\n" + "".join(diff_lines) +
        "\n```\n"
    )
    save_text(out_path(out_dir, "prompt_diff_a_vs_b.md"), diff_md)
    print("[OK] assemble: cost.json / runtime_evidence.json / "
          "prompt_diff_a_vs_b.md written")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True,
                         choices=["advanced", "generate", "analyze",
                                  "assemble", "all"])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    if args.step in ("advanced", "all"):
        cmd_advanced(args.out_dir, args.force)
    if args.step in ("generate", "all"):
        cmd_generate(args.out_dir, args.force)
    if args.step in ("analyze", "all"):
        cmd_analyze(args.out_dir)
    if args.step in ("assemble", "all"):
        cmd_assemble(args.out_dir)


if __name__ == "__main__":
    main()
