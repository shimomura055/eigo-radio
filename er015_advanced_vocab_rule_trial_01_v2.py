# ============================================================
# er015_advanced_vocab_rule_trial_01_v2.py
# ADVANCED-VOCAB-RULE-TRIAL-01 fix01 (Fable差し戻し1回目, 管理ID
# NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02 Phase 2, 2026-09-25)
# ============================================================
# 目的: v1(er015_advanced_vocab_rule_trial_01.py)へのFable差し戻し2点を
# 修正したv2をTrialとして再実行する。Production Prompt/Validator/
# Production pathへは実装しない(Trialのみ、v1同様)。
#
# 修正A(順位算出): v1は「表層形のみ」で順位を算出したため、ユーザーの
# 前処理条件「活用形は可能な範囲でlemmaへ正規化し、同一lemmaを重複カウント
# しない」に違反していた。v2では
#     rank = min(rank(surface), rank(best_lemma_candidate))
# とする。lemma候補は「-s/-es/-ies/-ed/-ing/-ly」の単純規則のみで生成し
# (v1コメントで問題視した既存simple_lemma()の「-er/-est」比較級除去規則は
# 使わない。"sewer"[単数]が"sewer"の末尾-erを比較級とみなして別語"sew"へ
# 誤正規化されるバグは、そもそも-er規則を候補生成に使わないことで回避する。
# これは「表層形へ後退する」代替ではなく、lemma化ロジック自体の修正である)。
# 安全条件として、生成された候補語がwordfreq top20000リストに存在しない
# 場合は採用せず、かつ候補語が元語より4文字以上短い場合(len(candidate) <
# len(original) - 3)は「元語の接尾辞除去で得られたが元語とは別語である
# 可能性が高い」として除外する。
#
# 修正B(Fact不変チェックの見逃し): v1のPromptにはFact不変の一般原則
# (do not remove any fact)はあったが、「引用符内の語・実際に使われた
# 呼称/名称は事実であり語彙置換の対象にしない」という明確化がなかった
# ため、Meta記事の "human concierges"(Metaが労働者を実際にそう呼んだ
# という事実)が誤ってSIMPLIFYされた。v2のRULE_BLOCK_ENに一般則として
# 1文追加する(新しい例外カテゴリを増やすのではなく、既存C[固有名詞]の
# 適用範囲の明確化として扱う。該当語はスキーマ上は既存の
# "KEEP -- proper noun" を使う)。
#
# 依存(re-use): er015_advanced_vocab_rule_trial_01 (v1trial) を
# importし、ARTICLE_PATHS/STRUCTURE_BLOCK/DEVELOPER_MESSAGE/
# TASK_TAIL/build_json_schema/_call_and_parse/sha256_of_file/
# get_client/_load_pricing/RANK_THRESHOLD/BORDERLINE_LOW/HIGH/
# structure_check/_diff_lines/_paragraphs/_headings をそのまま再利用。
# RULE_BLOCK_EN・順位算出・候補抽出(build_candidates)・Decision Log
# 整形(surface/lemma/rank列追加)のみv2として新規実装する。
#
# 固定: 2 call(Meta 1回 + Sewer 1回)。previous_response_idなし、
# Web Searchなし、model=gpt-5.6-luna、reasoning effort=high。
# 費用上限: v1+v2累計 JPY 5円(v1実績 JPY 1.7362円)。
#
# 実行方法:
#   .venv/Scripts/python.exe er015_advanced_vocab_rule_trial_01_v2.py \
#       --out-dir er015_output/advanced_vocab_rule_trial_01/v2 \
#       --step candidates
# ============================================================
from __future__ import annotations

import argparse
import json
import os
from collections import Counter

import er015_advanced_vocab_rule_trial_01 as v1trial

v1mod = v1trial.v1mod
v3mod = v1trial.v3mod
bmod = v1trial.bmod

RANK_THRESHOLD = v1trial.RANK_THRESHOLD
BORDERLINE_LOW = v1trial.BORDERLINE_LOW
BORDERLINE_HIGH = v1trial.BORDERLINE_HIGH
ARTICLE_PATHS = v1trial.ARTICLE_PATHS
STRUCTURE_BLOCK = v1trial.STRUCTURE_BLOCK
DEVELOPER_MESSAGE = v1trial.DEVELOPER_MESSAGE
TASK_TAIL = v1trial.TASK_TAIL

V1_COST_JPY_PATH = os.path.join(
    "er015_output", "advanced_vocab_rule_trial_01", "cost.json")
BUDGET_TOTAL_JPY = 5.0

out_path = v1trial.out_path
save_text = v1trial.save_text
load_text = v1trial.load_text
save_json = v1trial.save_json
load_json = v1trial.load_json
sha256_of_file = v1trial.sha256_of_file
get_client = v1trial.get_client
_load_pricing = v1trial._load_pricing
_call_and_parse = v1trial._call_and_parse
build_json_schema = v1trial.build_json_schema
structure_check = v1trial.structure_check
_diff_lines = v1trial._diff_lines


# ------------------------------------------------------------
# Fableが明確化した追記(spec_candidate_ja.md v2追記用、ユーザー仕様原文は
# 改変しない)
# ------------------------------------------------------------
SPEC_CLARIFICATION_JA = """\

## v2追記: Fableが明確化した点(2026-09-25、fix01差し戻しを受けて)

ユーザー仕様原文(上記)は変更しない。以下はFableがC(固有名詞)の適用範囲を
明確化した事項であり、新しい例外カテゴリの追加ではない。

- 引用符内の語や、人物・組織が実際に使った呼称・名称(例: Metaが労働者を
  実際に"human concierges"と呼んだ)は、記事のFact(事実)の一部であり、
  語彙置換の対象にしない。該当語は既存のC(固有名詞)の適用範囲内として
  "KEEP -- proper noun" で記録する(報告上は
  "KEEP -- proper noun / quoted designation" と説明を付す)。
"""

RULE_BLOCK_EN_V2 = v1trial.RULE_BLOCK_EN.replace(
    "Do NOT use \"it is part of a fixed expression / idiom\" as its own "
    "exception category.",
    "Words that appear inside quotation marks in the article, and titles, "
    "designations, or nicknames that a specific person or organization is "
    "reported to have actually used (for example, if the article states "
    "that Meta called certain workers \"human concierges\", the word "
    "\"concierges\" here is part of that reported fact, not an ordinary "
    "vocabulary choice) are facts of the article. Do not simplify such a "
    "word even if it appears in the candidate list below; treat it under "
    "exception C (a proper noun / quoted designation) and mark it \"KEEP "
    "-- proper noun\", explaining in reasoning that it is a quoted "
    "designation that must be kept exactly as reported.\n\n"
    "Do NOT use \"it is part of a fixed expression / idiom\" as its own "
    "exception category.",
    1,
)
assert RULE_BLOCK_EN_V2 != v1trial.RULE_BLOCK_EN, (
    "v2 RULE_BLOCK_EN の置換対象文が見つからない(逐語不一致)")
_rest_v1 = v1trial.RULE_BLOCK_EN.replace(
    "Do NOT use \"it is part of a fixed expression / idiom\" as its own "
    "exception category.", "", 1)
_rest_v2 = RULE_BLOCK_EN_V2.replace(
    "Words that appear inside quotation marks in the article, and titles, "
    "designations, or nicknames that a specific person or organization is "
    "reported to have actually used (for example, if the article states "
    "that Meta called certain workers \"human concierges\", the word "
    "\"concierges\" here is part of that reported fact, not an ordinary "
    "vocabulary choice) are facts of the article. Do not simplify such a "
    "word even if it appears in the candidate list below; treat it under "
    "exception C (a proper noun / quoted designation) and mark it \"KEEP "
    "-- proper noun\", explaining in reasoning that it is a quoted "
    "designation that must be kept exactly as reported.\n\n"
    "Do NOT use \"it is part of a fixed expression / idiom\" as its own "
    "exception category.", "", 1)
assert _rest_v1 == _rest_v2, (
    "v2 RULE_BLOCK_EN で追記対象以外の本文に差異がある(逐語不一致)")


# ------------------------------------------------------------
# 修正A: lemma候補生成(-s/-es/-ies/-ed/-ing/-ly の単純規則のみ。
# -er/-est比較級除去は使わない[sewer->sewバグの回避])
# ------------------------------------------------------------
def lemma_candidates_v2(word: str) -> list:
    w = word.lower().strip("'")
    if not w:
        return []
    if w.endswith("'s"):
        w = w[:-2]
    cands = set()

    if len(w) > 4 and w.endswith("ies"):
        cands.add(w[:-3] + "y")

    if len(w) > 4 and w.endswith("es") and w[:-2].endswith(
            ("s", "x", "z", "ch", "sh")):
        cands.add(w[:-2])

    if len(w) > 3 and w.endswith("ed"):
        stem = w[:-2]
        cands.add(stem)
        cands.add(stem + "e")
        if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            cands.add(stem[:-1])
            cands.add(stem[:-1] + "e")

    if len(w) > 3 and w.endswith("ing"):
        stem = w[:-3]
        cands.add(stem)
        cands.add(stem + "e")
        if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            cands.add(stem[:-1])
            cands.add(stem[:-1] + "e")

    if len(w) > 4 and w.endswith("ily"):
        cands.add(w[:-3] + "y")
    elif len(w) > 4 and w.endswith("ly"):
        cands.add(w[:-2])

    if (len(w) > 3 and w.endswith("s") and not w.endswith("ss")
            and not w.endswith("us") and not w.endswith("is")):
        cands.add(w[:-1])

    # 安全条件: 元語より4文字以上短い候補は除外(元語の接尾辞除去で
    # 得られたが実質的には別語である可能性が高いもの。v1で問題になった
    # "sewer"(5文字)->"sew"(3文字、差2)クラスは-er規則自体を使わない
    # ため本ルールでは生成されないが、将来の規則追加に対する保険として
    # 汎用的に適用する)。
    safe = {c for c in cands if c and len(c) >= len(w) - 3}
    safe.add(w)
    return sorted(safe)


def rank_of_word_v2(word: str, rank_of: dict) -> dict:
    w = word.lower()
    surface_rank = rank_of.get(w)
    lemma_cands = lemma_candidates_v2(w)
    lemma_found = sorted(
        ((c, rank_of[c]) for c in lemma_cands if c in rank_of and c != w),
        key=lambda x: x[1])
    best_lemma = lemma_found[0] if lemma_found else (None, None)

    all_found = []
    if surface_rank is not None:
        all_found.append((w, surface_rank, "surface"))
    if best_lemma[0] is not None:
        all_found.append((best_lemma[0], best_lemma[1], "lemma"))
    if all_found:
        best_word, best_rank, best_source = min(all_found, key=lambda x: x[1])
    else:
        best_word, best_rank, best_source = None, None, None

    return {
        "surface": w,
        "surface_rank": surface_rank,
        "lemma_candidates_considered": lemma_cands,
        "lemma_used": best_lemma[0],
        "lemma_rank": best_lemma[1],
        "rank": best_rank,
        "rank_source": best_source,
        "rank_word": best_word,
    }


def build_candidates_v2(text: str, rank_of: dict) -> dict:
    import wordfreq

    tokens = v3mod.extract_content_words(text)
    groups = {}
    for t in tokens:
        lw = t.lower()
        groups.setdefault(lw, []).append(t)

    candidates = []
    borderline = []
    excluded_proper = []
    all_words = {}
    for lw, forms in groups.items():
        most_common = Counter(forms).most_common(1)[0][0]
        cap = v3mod.capitalized_positions(text, lw)
        is_proper = cap["capitalized_non_sentence_initial"] > 0
        rk = rank_of_word_v2(lw, rank_of)
        rank = rk["rank"]
        zf = None
        if rank is None:
            zf = wordfreq.zipf_frequency(lw, "en")

        entry = {
            "word": lw,
            "actual_form": most_common,
            "surface_forms": sorted(set(forms)),
            "count": len(forms),
            "surface_rank": rk["surface_rank"],
            "lemma_candidates_considered": rk["lemma_candidates_considered"],
            "lemma_used": rk["lemma_used"],
            "lemma_rank": rk["lemma_rank"],
            "rank": rank,
            "rank_source": rk["rank_source"],
            "zipf_frequency": zf,
            "rank_display": v1trial._format_rank(rank, zf),
        }
        all_words[lw] = entry

        if is_proper:
            excluded_proper.append(entry)
            continue
        if rank is None or rank > RANK_THRESHOLD:
            candidates.append(entry)
        elif BORDERLINE_LOW <= rank <= BORDERLINE_HIGH:
            borderline.append(entry)

    def sort_key(e):
        return (0, e["zipf_frequency"]) if e["rank"] is None else (1, e["rank"])

    candidates.sort(key=sort_key)
    borderline.sort(key=lambda e: e["rank"])

    return {
        "content_word_token_total": len(tokens),
        "distinct_word_total": len(groups),
        "candidate_count": len(candidates),
        "borderline_count": len(borderline),
        "excluded_proper_noun_count": len(excluded_proper),
        "candidates": candidates,
        "borderline_reference": borderline,
        "excluded_proper_nouns": excluded_proper,
        "all_words_by_lower": all_words,
    }


def _candidates_block_text(candidates: list) -> str:
    lines = []
    for e in candidates:
        lines.append(f"- word=\"{e['word']}\" actual_form=\"{e['actual_form']}\" "
                      f"frequency_rank=\"{e['rank_display']}\"")
    return "\n".join(lines) if lines else "(none)"


def _borderline_block_text(borderline: list) -> str:
    lines = []
    for e in borderline:
        lines.append(f"- word=\"{e['word']}\" actual_form=\"{e['actual_form']}\" "
                      f"frequency_rank=\"{e['rank_display']}\"")
    return "\n".join(lines) if lines else "(none in this band for this article)"


# ------------------------------------------------------------
# STEP: candidates
# ------------------------------------------------------------
def cmd_candidates(out_dir: str) -> None:
    import wordfreq

    os.makedirs(out_dir, exist_ok=True)
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = v1trial._rank_of_map(top20000)

    save_json(out_path(out_dir, "frequency_rank_top20000_source.json"), {
        "source_package": "wordfreq",
        "source_package_version": "3.1.1",
        "license": "Apache-2.0",
        "method": "wordfreq.top_n_list('en', 20000) (v1と同一method・"
                  "同一version)",
        "ranking_unit": ("rank = min(rank(surface form), rank(best lemma "
                          "candidate)). lemma候補は-s/-es/-ies/-ed/-ing/-ly "
                          "の単純規則のみで生成(-er/-est比較級除去は使わない、"
                          "理由はer015_advanced_vocab_rule_trial_01_v2.py "
                          "冒頭コメント参照。v1のFable差し戻し修正A)。"),
        "rank_threshold": RANK_THRESHOLD,
        "borderline_band": [BORDERLINE_LOW, BORDERLINE_HIGH],
    })

    spec_v1_path = os.path.join(
        "er015_output", "advanced_vocab_rule_trial_01", "spec_candidate_ja.md")
    spec_v1_text = load_text(spec_v1_path)
    save_text(out_path(out_dir, "spec_candidate_ja.md"),
              spec_v1_text + SPEC_CLARIFICATION_JA)

    for key, path in ARTICLE_PATHS.items():
        text = load_text(path)
        result = build_candidates_v2(text, rank_of)
        save_json(out_path(out_dir, f"candidates_{key}.json"), result)
        print(f"[OK] candidates_{key}.json written. "
              f"candidate_count={result['candidate_count']} "
              f"borderline_count={result['borderline_count']} "
              f"excluded_proper={result['excluded_proper_noun_count']}")


# ------------------------------------------------------------
# STEP: run (Meta 1 call, Sewer 1 call)
# ------------------------------------------------------------
def _prior_cost_jpy() -> float:
    if not os.path.exists(V1_COST_JPY_PATH):
        return 0.0
    return load_json(V1_COST_JPY_PATH).get("total_cost_jpy", 0.0)


def cmd_run(out_dir: str, force: bool) -> None:
    import wordfreq

    os.makedirs(out_dir, exist_ok=True)
    v1mod.install_logger(out_dir)
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = v1trial._rank_of_map(top20000)

    client = get_client()
    pricing = _load_pricing()
    prior_jpy = _prior_cost_jpy()
    total_jpy = prior_jpy
    print(f"[INFO] prior (v1) cost_jpy={round(prior_jpy, 4)}, "
          f"cumulative budget={BUDGET_TOTAL_JPY}")

    for key, path in ARTICLE_PATHS.items():
        dst = out_path(out_dir, f"{key}_raw_response.json")
        if os.path.exists(dst) and not force:
            existing = load_json(dst)
            total_jpy += existing.get("meta", {}).get("cost_jpy", 0.0)
            print(f"[SKIP] existing: {dst} (cumulative so far="
                  f"{round(total_jpy, 4)} JPY)")
            continue

        article_text = load_text(path)
        cand_result = build_candidates_v2(article_text, rank_of)
        n_candidates = cand_result["candidate_count"]
        candidates_block = _candidates_block_text(cand_result["candidates"])
        borderline_block = _borderline_block_text(cand_result["borderline_reference"])

        user_message = (RULE_BLOCK_EN_V2 + "\n" + STRUCTURE_BLOCK[key] + "\n\n" +
                         TASK_TAIL.format(candidates_block=candidates_block,
                                           borderline_block=borderline_block,
                                           article_text=article_text))
        schema = build_json_schema(n_candidates)

        save_text(out_path(out_dir, f"prompt_advanced_vocab_rule_v2_{key}.txt"),
                  "DEVELOPER:\n" + DEVELOPER_MESSAGE + "\n\nUSER:\n" + user_message)

        parsed, raw_text, meta = _call_and_parse(
            client, pricing, DEVELOPER_MESSAGE, user_message, schema, key, n_candidates)
        meta["article_path"] = path
        meta["article_sha256"] = sha256_of_file(path)
        meta["candidate_count"] = n_candidates

        result = {"article": key, "candidates_input": cand_result,
                  "parsed": parsed, "raw_output_text": raw_text, "meta": meta}
        save_json(dst, result)

        total_jpy += meta["cost_jpy"]
        print(f"[OK] {key}: model={meta['response_model_actual']} "
              f"elapsed={meta['elapsed_seconds']}s cost_jpy={meta['cost_jpy']} "
              f"retried={meta['retried']} n_candidates={n_candidates} "
              f"cumulative_jpy(v1+v2)={round(total_jpy, 4)}")

        if parsed is None:
            stop = {"stop_reason": f"parse/technical failure after retry ({key})",
                    "parse_error": meta["parse_error"]}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] parse/technical failure after retry ({key})")
            raise SystemExit(1)

        if total_jpy > BUDGET_TOTAL_JPY:
            stop = {"stop_reason": f"cumulative budget (v1+v2) exceeded after {key}",
                    "total_jpy": round(total_jpy, 4), "budget_jpy": BUDGET_TOTAL_JPY}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] cumulative budget exceeded after {key}: "
                  f"{round(total_jpy, 4)} > {BUDGET_TOTAL_JPY}")
            raise SystemExit(1)

    print(f"[DONE] run complete. cumulative_cost_jpy(v1+v2)={round(total_jpy, 4)} "
          f"budget_jpy={BUDGET_TOTAL_JPY}")


# ------------------------------------------------------------
# 修正D: Fact不変チェック(コード側検証)
# ------------------------------------------------------------
import re as _re


def _extract_quoted(text: str) -> list:
    return _re.findall(r'["“]([^"“”]*)["”]', text)


def _extract_numbers(text: str) -> list:
    return _re.findall(r"\b\d[\d,]*\b", text)


def fact_tokens_check(before_text: str, after_text: str) -> dict:
    q_before = _extract_quoted(before_text)
    q_after = _extract_quoted(after_text)
    n_before = _extract_numbers(before_text)
    n_after = _extract_numbers(after_text)

    cap_before = sorted(set(
        w for w in _re.findall(r"[A-Za-z]+", before_text)
        if v3mod.capitalized_positions(before_text, w.lower())
        ["capitalized_non_sentence_initial"] > 0))
    cap_after = sorted(set(
        w for w in _re.findall(r"[A-Za-z]+", after_text)
        if v3mod.capitalized_positions(after_text, w.lower())
        ["capitalized_non_sentence_initial"] > 0))

    return {
        "quoted_strings_before": q_before,
        "quoted_strings_after": q_after,
        "quoted_strings_match": q_before == q_after,
        "numbers_before": n_before,
        "numbers_after": n_after,
        "numbers_match": n_before == n_after,
        "proper_noun_words_before": cap_before,
        "proper_noun_words_after": cap_after,
        "proper_noun_words_match": cap_before == cap_after,
        "overall_fact_tokens_match": (
            q_before == q_after and n_before == n_after
            and cap_before == cap_after),
    }


# ------------------------------------------------------------
# STEP: analyze
# ------------------------------------------------------------
def _decision_log_md_v2(article_label: str, decisions: list, cand_by_word: dict) -> str:
    lines = [f"### {article_label} Decision Log (v2, surface/lemma/rank付き)\n",
             "| Word | Surface Rank | Lemma(採用) | Lemma Rank | 採用Rank | "
             "判定 | 理由 | Before | After |",
             "|---|---|---|---|---|---|---|---|---|"]
    for d in decisions:
        before = d["before_sentence"].replace("|", "\\|")
        after = d["after_sentence"].replace("|", "\\|")
        reasoning = d["reasoning"].replace("|", "\\|")
        c = cand_by_word.get(d["word"], {})
        surface_rank = c.get("surface_rank")
        lemma_used = c.get("lemma_used") or "(none)"
        lemma_rank = c.get("lemma_rank")
        lines.append(
            f"| {d['actual_form']} | {surface_rank if surface_rank else '(none in top20000)'} "
            f"| {lemma_used} | {lemma_rank if lemma_rank else '(none in top20000)'} "
            f"| {d['frequency_rank']} | {d['decision']} | {reasoning} | "
            f"{before} | {after} |")
    return "\n".join(lines)


def cmd_analyze(out_dir: str) -> None:
    import wordfreq

    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = v1trial._rank_of_map(top20000)
    lemma_rank_map = bmod._build_lemma_rank_map(top20000)

    for key, path in ARTICLE_PATHS.items():
        raw = load_json(out_path(out_dir, f"{key}_raw_response.json"))
        before_text = load_text(path)
        after_text = raw["parsed"]["after_text"]
        decisions = raw["parsed"]["decisions"]
        notes = raw["parsed"]["notes_on_ambiguous_cases"]
        before_cand = raw["candidates_input"]
        cand_by_word = before_cand["all_words_by_lower"]

        save_text(out_path(out_dir, f"{key}_before.md"), before_text)
        save_text(out_path(out_dir, f"{key}_after.md"), after_text)

        after_cand = build_candidates_v2(after_text, rank_of)
        struct = structure_check(key, before_text, after_text)
        new_rare = v1trial.new_rare_words_in_after(
            before_cand, after_cand["all_words_by_lower"])

        before_levels = v1mod._level_metrics(before_text)
        after_levels = v1mod._level_metrics(after_text)

        band_before = bmod.measure_bands(before_text, lemma_rank_map)
        band_after = bmod.measure_bands(after_text, lemma_rank_map)

        decision_counts = Counter(d["decision"] for d in decisions)
        diff_lines = _diff_lines(before_text, after_text)
        fact_check = fact_tokens_check(before_text, after_text)

        metrics = {
            "article": key,
            "candidate_count": before_cand["candidate_count"],
            "decision_counts": dict(decision_counts),
            "structure_check": struct,
            "word_count_before": before_levels["word_count"],
            "word_count_after": after_levels["word_count"],
            "word_count_diff": after_levels["word_count"] - before_levels["word_count"],
            "sentence_count_before": before_levels["sentence_count"],
            "sentence_count_after": after_levels["sentence_count"],
            "sentence_count_diff": after_levels["sentence_count"] - before_levels["sentence_count"],
            "new_rare_words_gt12000_in_after": new_rare,
            "band_before_lemma_reference": band_before["bucket_token_counts"],
            "band_after_lemma_reference": band_after["bucket_token_counts"],
            "notes_on_ambiguous_cases": notes,
            "cost_jpy": raw["meta"]["cost_jpy"],
            "retried": raw["meta"]["retried"],
            "fact_tokens_check": fact_check,
        }
        save_json(out_path(out_dir, f"{key}_metrics.json"), metrics)
        save_json(out_path(out_dir, f"{key}_fact_tokens_check.json"), fact_check)

        label = "Meta" if key == "meta" else "Sewer"
        save_text(out_path(out_dir, f"{key}_decision_log.md"),
                  f"# {key}_decision_log.md (v2)\n\n" +
                  _decision_log_md_v2(label, decisions, cand_by_word) +
                  f"\n\n### notes_on_ambiguous_cases\n\n{notes}\n")

        diff_md = [f"# {key}_diff.md (v2)\n",
                   "## unified diff (Before -> After, full text)\n",
                   "```diff", *diff_lines, "```\n",
                   "## SIMPLIFY decisions のみ(宣言された変更文)\n"]
        for d in decisions:
            if d["decision"] == "SIMPLIFY":
                diff_md.append(f"- **{d['actual_form']}**\n"
                               f"  - Before: {d['before_sentence']}\n"
                               f"  - After: {d['after_sentence']}\n")
        save_text(out_path(out_dir, f"{key}_diff.md"), "\n".join(diff_md))

        print(f"[OK] {key}: analyze done. decision_counts={dict(decision_counts)} "
              f"structure_match(heading={struct['headings_match']}, "
              f"paragraph={struct['paragraph_count_match']}) "
              f"word_diff={metrics['word_count_diff']} "
              f"new_rare_words={len(new_rare)} "
              f"fact_tokens_match={fact_check['overall_fact_tokens_match']}")


# ------------------------------------------------------------
# STEP: candidates-diff (v1 vs v2 候補語比較表)
# ------------------------------------------------------------
def cmd_candidates_diff(out_dir: str) -> None:
    v1_dir = os.path.join("er015_output", "advanced_vocab_rule_trial_01")
    for key in ARTICLE_PATHS:
        v1_cand = load_json(os.path.join(v1_dir, f"candidates_{key}.json"))
        v2_cand = load_json(out_path(out_dir, f"candidates_{key}.json"))
        v1_words = {e["word"]: e for e in v1_cand["candidates"]}
        v2_words = {e["word"]: e for e in v2_cand["candidates"]}
        all_words = sorted(set(v1_words) | set(v2_words))

        lines = [f"# {key}_candidates_diff.md (v1 vs v2)\n",
                 "| Word | v1候補? | v1 Rank(surface) | v2候補? | v2 Rank"
                 "(min surface/lemma) | v2 lemma採用 | 変化 |",
                 "|---|---|---|---|---|---|---|"]
        for w in all_words:
            in_v1 = w in v1_words
            in_v2 = w in v2_words
            v1_rank = v1_words[w]["rank_display"] if in_v1 else "-"
            v2_rank = v2_words[w]["rank_display"] if in_v2 else "-"
            v2_lemma = v2_words[w].get("lemma_used") if in_v2 else (
                v2_cand["all_words_by_lower"].get(w, {}).get("lemma_used"))
            if in_v1 and not in_v2:
                change = "v2で候補から除外(lemma順位が閾値未満)"
            elif in_v2 and not in_v1:
                change = "v2で新規候補化"
            else:
                change = "変化なし(両方候補)"
            lines.append(f"| {w} | {'○' if in_v1 else '-'} | {v1_rank} | "
                          f"{'○' if in_v2 else '-'} | {v2_rank} | "
                          f"{v2_lemma or '-'} | {change} |")
        save_text(out_path(out_dir, f"{key}_candidates_diff.md"), "\n".join(lines))
        print(f"[OK] {key}_candidates_diff.md written. "
              f"v1_count={len(v1_words)} v2_count={len(v2_words)}")


# ------------------------------------------------------------
# STEP: assemble
# ------------------------------------------------------------
def cmd_assemble(out_dir: str) -> None:
    calls = []
    total_jpy_v2 = 0.0
    for key in ARTICLE_PATHS:
        raw_path = out_path(out_dir, f"{key}_raw_response.json")
        if not os.path.exists(raw_path):
            print(f"[WARN] missing: {raw_path}")
            continue
        raw = load_json(raw_path)
        calls.append(raw["meta"])
        total_jpy_v2 += raw["meta"].get("cost_jpy", 0.0)
    prior_jpy = _prior_cost_jpy()
    total_jpy = prior_jpy + total_jpy_v2
    cost = {
        "calls": calls,
        "v1_cost_jpy": round(prior_jpy, 4),
        "v2_cost_jpy": round(total_jpy_v2, 4),
        "total_cost_jpy_v1_plus_v2": round(total_jpy, 4),
        "budget_jpy": BUDGET_TOTAL_JPY,
        "within_budget": total_jpy <= BUDGET_TOTAL_JPY,
    }
    save_json(out_path(out_dir, "cost.json"), cost)
    print(f"[OK] cost.json written. total_cost_jpy(v1+v2)="
          f"{round(total_jpy, 4)} within_budget={cost['within_budget']}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--step", required=True,
                     choices=["candidates", "run", "analyze",
                              "candidates-diff", "assemble"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.step == "candidates":
        cmd_candidates(args.out_dir)
    elif args.step == "run":
        cmd_run(args.out_dir, args.force)
    elif args.step == "analyze":
        cmd_analyze(args.out_dir)
    elif args.step == "candidates-diff":
        cmd_candidates_diff(args.out_dir)
    elif args.step == "assemble":
        cmd_assemble(args.out_dir)


if __name__ == "__main__":
    main()
