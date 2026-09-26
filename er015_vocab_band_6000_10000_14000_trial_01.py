# ============================================================
# er015_vocab_band_6000_10000_14000_trial_01.py
# NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01 (Trial、最大VALIDATED、
# Production Prompt変更禁止、2026-09-26)
# ============================================================
# 目的: 前Trial(STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01)では、6,000語
# ルールを「Prefer」から「生成一体型(generation-first)」へ強めても、実際の
# 6,000語超残存語数はA(Control)とほぼ変わらなかった。本Trialでは、曖昧な
# 「prefer」ではなく「固有名詞等の明示的な3種の除外条件を除き、原則として
# 指定Band以内の語彙だけで記事を書く」という、より強い制約を課したPromptを
# 使い、6,000語/10,000語/14,000語の3条件で同一の共通テンプレート
# (Band数値のみ差し替え)を使って生成した場合の
#   難易度低下 / 自然さ / Storytelling / Fact精度
# のトレードオフを比較する。Standard/Advancedのどちらを正式採用するかの
# 判断はここでは行わない(採否推奨なし、最大VALIDATED)。
#
# 入力(既存の再利用、新規生成なし): STANDARD-A2-6000-GENERATION-FIRST-
# TRIAL-01が現行Advanced v2 Production Prompt(語彙ルールv2込み)から
# 再生成したAdvanced記事2本をそのまま入力として使う(path固定、sha256を
# 実行時に検証・記録する)。
#   - meta:  er015_output/standard_a2_6000_generation_first_trial_01/meta/
#            advanced_input.md
#   - sewer: er015_output/standard_a2_6000_generation_first_trial_01/sewer/
#            advanced_input.md
#
# 生成条件: 3 Band(6,000/10,000/14,000) x 2記事 = 6 call。共通の英語Prompt
# テンプレート(PROMPT_TEMPLATE_VB、本ファイル内定数)にBand数値のみを
# .format()で埋め込む(3条件でテンプレート本文は一字一句同一であることを
# コードでassertする)。model/effort/構造契約は前Trial
# (STANDARD-A2-6000-GENERATION-FIRST-TRIAL-01)と同一:
#   - model: routing.require_model("STANDARD_A2_ADAPTATION",
#            routing.WRITER_MODEL) (= gpt-5.6-luna)
#   - effort: vfl01.REASONING_EFFORT (= "high")
#   - retry primitive: vfl01.run_writer_with_technical_retry
#     (### 見出しちょうど2つを要求する既存の構造Gate、Production/前Trialと
#     完全に同じ関数を無変更で再利用)
#   - 構造契約: "# " 題名 + "### " 2節 + "## In one line"
#
# 除外条件(3種のみ、A/B/C/D例外分類体系は使わない): (1)固有名詞
# (2)推測容易な派生語・複合語 (3)日本語として定着している語。Prompt内の
# 例示語はwastewater/surprisingly/piano/curtain/Meta/Muse/Reutersのみに
# 限定し、Trial対象本文の特定語(septic/sewer/artery/flush/concierge等)は
# 一切例示に使わない(個別語誘導の禁止、委任文の指示)。
#
# 依存(re-use、新規ロジックはPROMPT_TEMPLATE_VB本文・分析集計のみ):
#   - er003_v1_en_direct_vfl_01_generate (vfl01): get_client /
#     run_writer_with_technical_retry / REASONING_EFFORT (Production
#     primitive、無変更で再利用)
#   - er003_v1_n3_01_standard_a2_generate (std_gen): STANDARD_A2_DEVELOPER
#     (developer messageを流用、_load_pricing / _compute_cost_jpy /
#     run_checks も再利用。STANDARD_A2_PROMPT_V5自体は使わない・
#     変更しない)
#   - er006_model_routing_contract_01 (routing): require_model
#   - er015_advanced_vocab_rule_trial_01 (v1trial): out_path/save_text/
#     load_text/save_json/load_json/get_client/_rank_of_map/_format_rank
#   - er015_advanced_vocab_rule_trial_01_v2 (v2mod): lemma_candidates_v2/
#     rank_of_word_v2/fact_tokens_check(既存ロジックをそのまま流用)
#   - er015_vocab_abcd_strict_exception_trial_01 (strict_mod):
#     build_candidates(rank=min(surface,lemma)、閾値パラメータ化版、
#     3 Bandそれぞれで閾値のみ変えて再利用)
#   - er015_news_natural_advanced_standard_a2_trial_01 (v1mod、v2mod.v3mod
#     経由): _level_metrics/_strip_title(語数・平均文長・FK概算等)
#
# 固定: 6 call(3 Band x 2記事)。previous_response_idなし、Web Searchなし、
# model=gpt-5.6-luna、reasoning effort=high。費用上限(Guardrail、暴走
# 防止): JPY 30円(実測見込みJPY 5〜10円)。超過見込みが判明した時点で
# STOPして報告する(PM_GOVERNANCE 7-6)。不要な追加Trial・再生成は禁止
# (各条件1回生成。技術的失敗[構造契約違反・空応答]のみ1回retry)。
# TTSは使用しない(TTS call 0)。
#
# 「実質超過語」の分類(固有名詞/推測容易な派生・複合/日本語定着語/実質
# 超過)はコードでは行わない。コードはrank付きの生の超過語候補リスト
# (build_candidates、固有名詞候補は別枠で保持)を出すところまでに限り、
# 分類自体はSonnetが目視でREPORT/analysis.mdへ記録する(委任文の指示、
# 判断が割れる語は「境界」と明記)。
#
# 採否推奨はコード側・REPORT側どちらにも書かない。
#
# 実行方法:
#   .venv/Scripts/python.exe er015_vocab_band_6000_10000_14000_trial_01.py \
#       --out-dir er015_output/vocab_band_6000_10000_14000_trial_01 \
#       --step all
# ============================================================
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
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

BANDS = [6000, 10000, 14000]
BUDGET_JPY_CAP = 30.0
PER_CALL_CEILING_JPY = 3.0

INPUT_PATHS = {
    "meta": os.path.join(
        "er015_output", "standard_a2_6000_generation_first_trial_01",
        "meta", "advanced_input.md"),
    "sewer": os.path.join(
        "er015_output", "standard_a2_6000_generation_first_trial_01",
        "sewer", "advanced_input.md"),
}


# ------------------------------------------------------------
# Prompt共通テンプレート(Band数値のみ差し替え、それ以外は3条件で一字一句
# 同一)
# ------------------------------------------------------------
DEVELOPER_VB = (
    "You are an editor who rewrites English feature articles so that their "
    "vocabulary stays within a specific word-frequency band, while keeping "
    "the article's facts, storyline, and enjoyment intact."
)

PROMPT_TEMPLATE_VB = """Rewrite this entire article using, as a firm principle, only words within roughly the top {band:,} most common English words.

Do not first write a hard word and then swap out only that one word afterward. Instead, from the first draft, build the whole sentence around words within this band so the full meaning is expressed naturally from the start.

The following are the only three kinds of words allowed to fall outside the top {band:,} words:
(1) A true proper noun: a person's name, a place name, an organization's name, a product or service name, or an official title (for example: Meta, Muse, Reuters).
(2) A derived or compound word whose meaning a learner can easily guess from a simpler word they already know, through a clear prefix, suffix, or a transparent compound (for example: wastewater = waste + water; surprisingly = surprise + -ingly). Do not use this exception for a word that can be split into parts but whose meaning is not easy to predict from those parts.
(3) A word that is a common loanword already established in Japanese, one that a Japanese learner of English would naturally connect to its meaning just from its English form (for example: piano, curtain). Do not use this exception just because a katakana spelling exists for the word; a technical or specialist term, or a word whose English form and Japanese pronunciation do not clearly match each other, is not covered by this exception.

Do not sort each word into a fixed exception category, and do not list or output any candidate words or a classification for each word. Output only the article itself.

Keep every fact exactly as it is: the same actions, cause and effect, who did what, who or what it happened to, quantities, points in time, and the same storyline and central details. Do not turn the article into a summary and do not remove an interesting detail.

Some loss of naturalness is acceptable in service of the vocabulary band above. However, the result must not become grammatically broken, must not change the meaning, must not become too unnatural to use as learning material, must not turn into a pile of clumsy explanatory phrases, and must not repeat the same simple word or phrase in an unnatural way.

Keep the same Markdown structure (the "# " title, the two "### " sections, and the final "## In one line" section); do not add or remove sections.

Output only the English title and the English body.

[Article]
{advanced_article}"""


def render_prompt(band: int, advanced_article: str) -> str:
    return PROMPT_TEMPLATE_VB.format(band=band, advanced_article=advanced_article)


def _assert_template_band_only_diff() -> None:
    """3条件のPromptが「Band数値のみ」差し替わっており、それ以外の文言が
    一字一句同一であることを機械的に保証する(サンプル記事本文で3条件を
    レンダリングし、band文字列を共通トークンへ置換した後の文字列が完全
    一致することを確認する)。"""
    sample_article = "[SAMPLE]"
    rendered = {}
    for band in BANDS:
        text = render_prompt(band, sample_article)
        band_comma = f"{band:,}"
        rendered[band] = text.replace(f"top {band_comma} most common",
                                       "top <BAND> most common").replace(
            f"outside the top {band_comma} words", "outside the top <BAND> words")
    values = list(rendered.values())
    if any(v != values[0] for v in values):
        raise RuntimeError(
            "[STOP] PROMPT_TEMPLATE_VBが3条件でBand数値以外にも差異が"
            "あります(委任文の前提「Band数値のみ差異」が崩れています)。")


_assert_template_band_only_diff()

PROMPT_SHA256_BY_BAND = {
    band: hashlib.sha256(render_prompt(band, "{advanced_article}").encode("utf-8")).hexdigest()
    for band in BANDS
}


# ------------------------------------------------------------
# 生成
# ------------------------------------------------------------
def generate_band_article(band: int, advanced_text: str, *, client=None,
                           model: str | None = None, effort: str = "high",
                           max_retries: int = 1) -> dict:
    if effort != vfl01.REASONING_EFFORT:
        raise ValueError(
            f"[STOP] effort='{effort}' はvfl01.REASONING_EFFORT="
            f"'{vfl01.REASONING_EFFORT}' と不一致です。")
    if client is None:
        client = vfl01.get_client()
    requested_model = model or routing.require_model(
        "STANDARD_A2_ADAPTATION", routing.WRITER_MODEL)

    prompt = render_prompt(band, advanced_text)
    price_fn = std_gen._load_pricing()

    t0 = time.time()
    result = vfl01.run_writer_with_technical_retry(
        client, prompt, max_attempts=max_retries + 1, model=requested_model,
        developer=DEVELOPER_VB)
    elapsed = round(time.time() - t0, 3)

    if result["status"] not in ("STRUCTURE_PASS", "STRUCTURE_INVALID"):
        raise RuntimeError(
            f"[STOP][band={band}] {max_retries + 1}回試行しても生成に失敗"
            f"しました: status={result['status']} attempts={result['attempts']}")
    if result["status"] != "STRUCTURE_PASS":
        raise RuntimeError(
            f"[STOP][band={band}] {max_retries + 1}回試行してもcontract"
            f"構造(### 見出しちょうど2つ)を満たせませんでした: "
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
        "band": band,
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
        "prompt_sha256": PROMPT_SHA256_BY_BAND[band],
    }


# ------------------------------------------------------------
# 予算Guardrail
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


def _guard_budget(out_dir: str,
                   estimated_next_call_jpy_ceiling: float = PER_CALL_CEILING_JPY):
    total_so_far = _running_total_jpy(out_dir)
    if total_so_far + estimated_next_call_jpy_ceiling > BUDGET_JPY_CAP:
        raise RuntimeError(
            f"[STOP] 予算Guardrail超過見込み: 現在まで JPY {total_so_far:.4f} "
            f"+ 次callceiling見込み JPY {estimated_next_call_jpy_ceiling} > "
            f"上限 JPY {BUDGET_JPY_CAP}")


# ------------------------------------------------------------
# STEP: generate (3 Band x 2記事 = 6 call)
# ------------------------------------------------------------
def _band_file_stub(band: int) -> str:
    return f"band_{band}"


def cmd_generate(out_dir: str, force: bool) -> None:
    os.makedirs(out_dir, exist_ok=True)
    client = vfl01.get_client()
    for key, in_path in INPUT_PATHS.items():
        article_dir = out_path(out_dir, key)
        os.makedirs(article_dir, exist_ok=True)

        if not os.path.exists(in_path):
            raise RuntimeError(f"[STOP] 入力が存在しません: {in_path}")
        advanced_text = load_text(in_path)
        with open(in_path, "rb") as f:
            input_sha256_raw = hashlib.sha256(f.read()).hexdigest()
        input_sha256_lf = hashlib.sha256(
            advanced_text.encode("utf-8")).hexdigest()

        input_out = out_path(article_dir, "input.md")
        if not os.path.exists(input_out) or force:
            save_text(input_out, advanced_text)
        save_json(out_path(article_dir, "input_provenance.json"), {
            "source_path": in_path,
            "sha256_raw_bytes": input_sha256_raw,
            "sha256_lf_normalized": input_sha256_lf,
        })

        for band in BANDS:
            stub = _band_file_stub(band)
            out_md = out_path(article_dir, f"{stub}.md")
            out_raw = out_path(article_dir, f"{stub}_raw_response.json")
            if os.path.exists(out_md) and os.path.exists(out_raw) and not force:
                print(f"[SKIP] {key} band={band} already generated: {out_md}")
                continue
            _guard_budget(out_dir)
            result = generate_band_article(band, advanced_text, client=client)
            save_text(out_md, result["text"])
            save_json(out_raw, {
                "stage": f"{stub}_{key}",
                "band": band,
                "model_requested": result["model_id_requested"],
                "response_model_actual": result["model_id_actual"],
                "fallback_detected": result["fallback_detected"],
                "response_id": result["response_id"],
                "usage": result["usage"],
                "cost_usd": result["cost_usd"],
                "cost_jpy": result["cost_jpy"],
                "attempts": result["attempts"],
                "retried": result["retried"],
                "structure_status": result["structure_status"],
                "elapsed_seconds": result["elapsed_seconds"],
                "checks": result["checks"],
                "prompt_sha256": result["prompt_sha256"],
            })
            _append_call_cost(out_dir, {
                "stage": f"{stub}_{key}", "band": band,
                "cost_jpy": result["cost_jpy"]})
            print(f"[OK] {key} band={band}: cost_jpy={result['cost_jpy']} "
                  f"retried={result['retried']} "
                  f"status={result['structure_status']} "
                  f"model_actual={result['model_id_actual']}")


# ------------------------------------------------------------
# STEP: analyze (残存語[生]・Fact/意味差・客観指標。分類自体はSonnetが
# 事後にanalysis.mdへ手動記録する)
# ------------------------------------------------------------
def _residual_words(text: str, rank_of: dict, threshold: int) -> list:
    """threshold超(top20000圏外含む)の残存語一覧(固有名詞候補も含めて
    すべて列挙、rank付き)。build_candidatesのcandidates(非固有名詞候補・
    閾値超)+excluded_proper_nouns(固有名詞候補、閾値超のみ抽出)を統合
    する。borderline_low/highはthreshold自体と同値にして無効化する
    (本Trialでは境界帯の別集計は使わず、閾値超か否かのみで一覧化する)。"""
    result = build_candidates(text, rank_of, threshold, threshold, threshold)
    residual = list(result["candidates"])
    for e in result["excluded_proper_nouns"]:
        if e["rank"] is None or e["rank"] > threshold:
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

    for key in INPUT_PATHS:
        article_dir = out_path(out_dir, key)
        advanced_text = load_text(out_path(article_dir, "input.md"))

        analysis = {"article": key}
        residual_at_zero = _residual_words(advanced_text, rank_of, 0)
        analysis["input"] = {
            "level_metrics": level_metrics(advanced_text),
            "paragraph_count": _paragraph_count(advanced_text),
        }

        for band in BANDS:
            stub = _band_file_stub(band)
            text = load_text(out_path(article_dir, f"{stub}.md"))
            residual = _residual_words(text, rank_of, band)
            metrics = level_metrics(text)
            analysis[stub] = {
                "band": band,
                "level_metrics": metrics,
                "paragraph_count": _paragraph_count(text),
                "residual_word_count_over_band": len(residual),
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
            analysis[f"fact_tokens_check_input_vs_{stub}"] = fact_tokens_check(
                advanced_text, text)

        save_json(out_path(article_dir, "analysis_data.json"), analysis)
        counts = {f"band_{b}": analysis[_band_file_stub(b)]["residual_word_count_over_band"]
                  for b in BANDS}
        print(f"[OK] analyze {key}: residual_counts={counts}")


# ------------------------------------------------------------
# STEP: assemble (cost.json / runtime_evidence.json / prompt_band_template.md)
# ------------------------------------------------------------
def cmd_assemble(out_dir: str) -> None:
    calls_path = out_path(out_dir, "cost_calls.json")
    calls = load_json(calls_path) if os.path.exists(calls_path) else []
    total_cost_jpy = round(sum(c.get("cost_jpy", 0.0) for c in calls), 4)
    by_band = {}
    for b in BANDS:
        by_band[f"band_{b}"] = round(
            sum(c.get("cost_jpy", 0.0) for c in calls if c.get("band") == b), 4)
    save_json(out_path(out_dir, "cost.json"), {
        "calls": calls,
        "total_cost_jpy": total_cost_jpy,
        "cost_jpy_by_band": by_band,
        "budget_jpy_guardrail": BUDGET_JPY_CAP,
        "within_budget": total_cost_jpy <= BUDGET_JPY_CAP,
    })

    runtime_evidence = {"calls": []}
    for key in INPUT_PATHS:
        article_dir = out_path(out_dir, key)
        for band in BANDS:
            stub = _band_file_stub(band)
            p = out_path(article_dir, f"{stub}_raw_response.json")
            if os.path.exists(p):
                d = load_json(p)
                runtime_evidence["calls"].append({
                    "article": key,
                    "band": band,
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

    lines = ["# prompt_band_template.md\n",
             "NEWS-VOCAB-BAND-6000-10000-14000-TRIAL-01\n",
             "共通テンプレート(3条件でBand数値のみ差異。他の文言は一字一句"
             "同一であることをコードでassert済み: "
             "`_assert_template_band_only_diff()`)。\n",
             f"DEVELOPER message:\n\n```text\n{DEVELOPER_VB}\n```\n",
             "## テンプレート全文(`{band}`/`{advanced_article}`はプレース"
             "ホルダのまま)\n",
             f"```text\n{PROMPT_TEMPLATE_VB}\n```\n",
             "## Band別 sha256(advanced_articleプレースホルダは`"
             "{advanced_article}`のまま計算)\n"]
    for band in BANDS:
        lines.append(f"- band={band}: sha256={PROMPT_SHA256_BY_BAND[band]}")
    save_text(out_path(out_dir, "prompt_band_template.md"), "\n".join(lines) + "\n")
    print("[OK] assemble: cost.json / runtime_evidence.json / "
          "prompt_band_template.md written")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True,
                         choices=["generate", "analyze", "assemble", "all"])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    if args.step in ("generate", "all"):
        cmd_generate(args.out_dir, args.force)
    if args.step in ("analyze", "all"):
        cmd_analyze(args.out_dir)
    if args.step in ("assemble", "all"):
        cmd_assemble(args.out_dir)


if __name__ == "__main__":
    main()
