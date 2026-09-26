# ============================================================
# er015_standard_vocab_abcd_alignment_trial_01.py
# STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01 (Trialのみ、最大VALIDATED、
# Production Prompt変更禁止、2026-09-26)
# ============================================================
# 目的: AdvancedとStandardで語彙ルールの思想に差をつけない、という
# ユーザー方針のもと、Advanced v2(ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01
# でProduction採用済み)と同一のABCD例外構造・同一の一般原則を、
# 閾値だけをStandardの頻度ライン(6,000位)に差し替えてStandard v5本文
# (Production E2E版、Before)へ適用した場合にどうなるかをTrialとして
# 検証する。Production Prompt(er003_v1_n3_01_standard_a2_generate.py /
# er003_v1_n3_01_advanced_adaptation_generate.py)は一切変更しない。
#
# 「思想差ゼロ」の担保方法: er015_advanced_vocab_rule_trial_01_v2.py の
# RULE_BLOCK_EN_V2(Production ADVANCED_VOCAB_RULE_V2_BLOCKと同じ内容の
# Trial版本体)をベースに、"12,000" -> "6,000" の数字置換のみを行う
# (assertで置換件数を確認、他の一字一句は変更しない)。TASK_TAILの
# BORDERLINE参考範囲コメントも同様に "10,000-12,000" -> "5,000-6,000" の
# 数字置換のみ。DEVELOPER_MESSAGEのみ、テスト対象がCEFR B1(Advanced)では
# なくCEFR A2(Standard)であるという文脈上の正確性のために
# "CEFR B1 (\"Advanced\")" -> "CEFR A2 (\"Standard\")" と表記を改める
# (これは語彙ルール本体[RULE_BLOCK_EN]の思想・文言ではなく、タスク説明の
# 呼称のみの変更であることをprompt_diff_advanced_v2_vs_standard.mdで
# 明示する)。
#
# ランク算出ロジック(修正A同等、v2から流用): rank = min(rank(surface),
# rank(best lemma candidate))。lemma候補は-s/-es/-ies/-ed/-ing/-lyの
# 単純規則のみ(-er/-est比較級除去は使わない)。fact_tokens_checkも
# v2のロジックをそのまま流用する。
#
# 依存(re-use、新規ロジックは閾値のみ):
#   - er015_advanced_vocab_rule_trial_01 (v1trial): out_path/save_text/
#     load_text/save_json/load_json/sha256_of_file/get_client/
#     _load_pricing/_call_and_parse/build_json_schema/structure_check/
#     _diff_lines/DEVELOPER_MESSAGE/STRUCTURE_BLOCK/TASK_TAIL/v1mod
#   - er015_advanced_vocab_rule_trial_01_v2 (v2mod): lemma_candidates_v2/
#     rank_of_word_v2/fact_tokens_check/RULE_BLOCK_EN_V2/v3mod/bmod
#
# 入力(Standard v5本文、Before、Production E2E版):
#   - Meta: er012_output/e_family_two_level_wiring_01/meta/a2/article.md
#   - Sewer: er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/
#     a2v5_standard_sewer.md
# 順位ソース: wordfreq 3.1.1 top_n_list('en', 20000)(既存installそのまま
# 再利用、追加installなし。同一method/versionは
# er015_output/news_standard_a2_vocab_banding_trial_01/
# frequency_rank_top20000.jsonが既に記録している)。
#
# 固定: 2 call(Meta 1回 + Sewer 1回)。previous_response_idなし、
# Web Searchなし、model=gpt-5.6-luna(v1trial._call_and_parseが使う既存
# 設定をそのまま再利用)、reasoning effort=high。費用上限 JPY 5円
# (本Trial単独の予算、他の管理IDの累計とは合算しない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er015_standard_vocab_abcd_alignment_trial_01.py \
#       --out-dir er015_output/standard_vocab_abcd_alignment_trial_01 \
#       --step candidates
# ============================================================
from __future__ import annotations

import argparse
import difflib
import os
from collections import Counter

import er015_advanced_vocab_rule_trial_01 as v1trial
import er015_advanced_vocab_rule_trial_01_v2 as v2mod

v3mod = v2mod.v3mod
bmod = v2mod.bmod
v1mod = v1trial.v1mod

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
_format_rank = v1trial._format_rank
_rank_of_map = v1trial._rank_of_map

lemma_candidates_v2 = v2mod.lemma_candidates_v2
rank_of_word_v2 = v2mod.rank_of_word_v2
fact_tokens_check = v2mod.fact_tokens_check

# ------------------------------------------------------------
# Standard閾値(ユーザー仕様: 6,000位超を平易化候補。近傍語5,000〜6,000は
# BORDERLINE可視化用の参考渡し)
# ------------------------------------------------------------
RANK_THRESHOLD = 6000
BORDERLINE_LOW = 5000
BORDERLINE_HIGH = 6000

BUDGET_TOTAL_JPY = 5.0

ARTICLE_PATHS = {
    "meta": os.path.join(
        "er012_output", "e_family_two_level_wiring_01", "meta", "a2",
        "article.md"),
    "sewer": os.path.join(
        "er015_output", "news_standard_a2_vocab_6000_cutoff_trial_01",
        "a2v5_standard_sewer.md"),
}

ARTICLE_SOURCE_NOTE = {
    "meta": ("Standard v5 Before。Production E2E版(\"some of the calls\""
              "文言を含む、er012_output/e_family_two_level_wiring_01/meta/"
              "a2/article.md)。"),
    "sewer": ("Standard v5 Before(6,000語ラインで生成済みのSewer代表記事、"
              "er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/"
              "a2v5_standard_sewer.md)。"),
}


# ------------------------------------------------------------
# Prompt: Advanced v2と同一文言、閾値のみ6,000へ置換
# ------------------------------------------------------------
def _replace_exact(text: str, old: str, new: str, expected_count: int) -> str:
    actual_count = text.count(old)
    if actual_count != expected_count:
        raise AssertionError(
            f"置換対象文字列の出現回数が想定と異なる: old={old!r} "
            f"expected={expected_count} actual={actual_count}")
    return text.replace(old, new)


RULE_BLOCK_EN_STANDARD = _replace_exact(
    v2mod.RULE_BLOCK_EN_V2, "12,000", "6,000", 2)

TASK_TAIL_STANDARD = _replace_exact(
    v1trial.TASK_TAIL, "10,000-12,000", "5,000-6,000", 1)

DEVELOPER_MESSAGE_STANDARD = _replace_exact(
    v1trial.DEVELOPER_MESSAGE,
    "CEFR B1 (\"Advanced\")", "CEFR A2 (\"Standard\")", 1)

STRUCTURE_BLOCK = v1trial.STRUCTURE_BLOCK  # 記事構造契約は記事固有、CEFR非依存のためそのまま再利用


def _unified_diff_md(label: str, before: str, after: str) -> list:
    diff = list(difflib.unified_diff(
        before.splitlines(), after.splitlines(),
        fromfile=f"{label} (Advanced v2)", tofile=f"{label} (Standard)",
        lineterm=""))
    return diff


def write_prompt_diff(out_dir: str) -> None:
    lines = ["# prompt_diff_advanced_v2_vs_standard.md\n",
             "## 目的\n",
             "AdvancedとStandardで語彙ルールの思想に差をつけないという"
             "ユーザー方針の確認として、Production採用済みAdvanced v2"
             "(ADVANCED-VOCAB-V2-PRODUCTION-RESTORE-01)のTrial版本体"
             "(RULE_BLOCK_EN_V2、Production ADVANCED_VOCAB_RULE_V2_BLOCKと"
             "同内容)と、本Trialで使うStandard版プロンプトの差分を"
             "逐語で示す。\n",
             "## 結論\n",
             "- RULE_BLOCK_EN(語彙ルール本体、A/B/C/D例外・引用符内呼称の"
             "扱い・一般原則)は **\"12,000\" -> \"6,000\" の数字2箇所のみ**"
             "が差分。他は一字一句同一(以下diff参照、数字行以外の`-`/`+`"
             "行が無いことを目視確認できる)。\n",
             "- TASK_TAIL(BORDERLINE参考範囲コメント)は **\"10,000-12,000\""
             " -> \"5,000-6,000\" の数字1箇所のみ**が差分。\n",
             "- DEVELOPER_MESSAGEのみ、テスト対象がCEFR B1(Advanced)ではなく"
             "CEFR A2(Standard)であるという**文脈上の呼称**を"
             "`CEFR B1 (\"Advanced\")` -> `CEFR A2 (\"Standard\")`と"
             "改めた(語彙ルール本体の思想・文言の変更ではなく、タスク説明"
             "文の対象レベル表記のみの変更)。\n",
             "\n## 1. RULE_BLOCK_EN diff (Advanced v2 -> Standard)\n",
             "```diff",
             *_unified_diff_md("RULE_BLOCK_EN", v2mod.RULE_BLOCK_EN_V2,
                                RULE_BLOCK_EN_STANDARD),
             "```\n",
             "## 2. TASK_TAIL diff (Advanced v2/v1 -> Standard)\n",
             "```diff",
             *_unified_diff_md("TASK_TAIL", v1trial.TASK_TAIL,
                                TASK_TAIL_STANDARD),
             "```\n",
             "## 3. DEVELOPER_MESSAGE diff (Advanced v2/v1 -> Standard、"
             "開示済み例外)\n",
             "```diff",
             *_unified_diff_md("DEVELOPER_MESSAGE", v1trial.DEVELOPER_MESSAGE,
                                DEVELOPER_MESSAGE_STANDARD),
             "```\n",
             "## 4. Production側の思想差チェック(参考、本ファイルは§7の"
             "元データ)\n",
             "Production Advanced v2 (`er003_v1_n3_01_advanced_adaptation_"
             "generate.py` ADVANCED_VOCAB_RULE_V2_BLOCK)とProduction "
             "Standard v5 (`er003_v1_n3_01_standard_a2_generate.py` "
             "STANDARD_A2_PROMPT_V5の語彙6行)の思想差は"
             "STANDARD-VOCAB-ABCD-ALIGNMENT-TRIAL-01_REPORT.md §7参照"
             "(Production変更はしない、所見のみ)。\n"]
    save_text(out_path(out_dir, "prompt_diff_advanced_v2_vs_standard.md"),
              "\n".join(lines))


# ------------------------------------------------------------
# 候補語抽出(v2のlemma順位ロジックを流用、閾値のみ6,000/5,000-6,000)
# ------------------------------------------------------------
def build_candidates(text: str, rank_of: dict) -> dict:
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
            "rank_display": _format_rank(rank, zf),
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


def new_rare_words_in_after(before_cand: dict, after_words: dict) -> list:
    """After新出語のうち、6,000超(または表外)のものを一覧化する
    (難語->難語置換の見逃しが無いかのチェック用)。"""
    before_all_lowers = set(before_cand["all_words_by_lower"].keys())
    new_words = []
    for lw, e in after_words.items():
        if lw in before_all_lowers:
            continue
        if e["rank"] is None or e["rank"] > RANK_THRESHOLD:
            new_words.append(e)
    new_words.sort(key=lambda e: (0, e["zipf_frequency"]) if e["rank"] is None
                    else (1, e["rank"]))
    return new_words


# ------------------------------------------------------------
# STEP: candidates
# ------------------------------------------------------------
def cmd_candidates(out_dir: str) -> None:
    import wordfreq

    os.makedirs(out_dir, exist_ok=True)
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = _rank_of_map(top20000)

    save_json(out_path(out_dir, "frequency_rank_top20000_source.json"), {
        "source_package": "wordfreq",
        "source_package_version": "3.1.1",
        "license": "Apache-2.0",
        "method": "wordfreq.top_n_list('en', 20000) (既存install再利用、"
                  "er015_output/news_standard_a2_vocab_banding_trial_01/"
                  "frequency_rank_top20000.jsonと同一method・同一version)",
        "ranking_unit": ("rank = min(rank(surface form), rank(best lemma "
                          "candidate))。lemma候補は-s/-es/-ies/-ed/-ing/-ly "
                          "の単純規則のみ(-er/-est比較級除去は使わない)。"
                          "er015_advanced_vocab_rule_trial_01_v2.pyの"
                          "lemma_candidates_v2/rank_of_word_v2をそのまま"
                          "流用。"),
        "rank_threshold": RANK_THRESHOLD,
        "borderline_band": [BORDERLINE_LOW, BORDERLINE_HIGH],
        "article_source_note": ARTICLE_SOURCE_NOTE,
    })

    write_prompt_diff(out_dir)

    for key, path in ARTICLE_PATHS.items():
        text = load_text(path)
        result = build_candidates(text, rank_of)
        save_json(out_path(out_dir, f"candidates_{key}.json"), result)
        print(f"[OK] candidates_{key}.json written. "
              f"candidate_count={result['candidate_count']} "
              f"borderline_count={result['borderline_count']} "
              f"excluded_proper={result['excluded_proper_noun_count']}")


# ------------------------------------------------------------
# STEP: run (Meta 1 call, Sewer 1 call)
# ------------------------------------------------------------
def cmd_run(out_dir: str, force: bool) -> None:
    import wordfreq

    os.makedirs(out_dir, exist_ok=True)
    v1mod.install_logger(out_dir)
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = _rank_of_map(top20000)

    client = get_client()
    pricing = _load_pricing()
    total_jpy = 0.0
    print(f"[INFO] budget={BUDGET_TOTAL_JPY} (本Trial単独、他管理IDと合算しない)")

    for key, path in ARTICLE_PATHS.items():
        dst = out_path(out_dir, f"{key}_raw_response.json")
        if os.path.exists(dst) and not force:
            existing = load_json(dst)
            total_jpy += existing.get("meta", {}).get("cost_jpy", 0.0)
            print(f"[SKIP] existing: {dst} (cumulative so far="
                  f"{round(total_jpy, 4)} JPY)")
            continue

        article_text = load_text(path)
        cand_result = build_candidates(article_text, rank_of)
        n_candidates = cand_result["candidate_count"]
        candidates_block = _candidates_block_text(cand_result["candidates"])
        borderline_block = _borderline_block_text(cand_result["borderline_reference"])

        user_message = (RULE_BLOCK_EN_STANDARD + "\n" + STRUCTURE_BLOCK[key] +
                         "\n\n" +
                         TASK_TAIL_STANDARD.format(
                             candidates_block=candidates_block,
                             borderline_block=borderline_block,
                             article_text=article_text))
        schema = build_json_schema(n_candidates)

        save_text(out_path(out_dir, f"prompt_standard_vocab_abcd_{key}.txt"),
                  "DEVELOPER:\n" + DEVELOPER_MESSAGE_STANDARD +
                  "\n\nUSER:\n" + user_message)

        parsed, raw_text, meta = _call_and_parse(
            client, pricing, DEVELOPER_MESSAGE_STANDARD, user_message, schema,
            key, n_candidates)
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
              f"cumulative_jpy={round(total_jpy, 4)}")

        if parsed is None:
            stop = {"stop_reason": f"parse/technical failure after retry ({key})",
                    "parse_error": meta["parse_error"]}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] parse/technical failure after retry ({key})")
            raise SystemExit(1)

        if total_jpy > BUDGET_TOTAL_JPY:
            stop = {"stop_reason": f"budget exceeded after {key}",
                    "total_jpy": round(total_jpy, 4), "budget_jpy": BUDGET_TOTAL_JPY}
            save_json(out_path(out_dir, "stop_reason.json"), stop)
            print(f"[STOP] budget exceeded after {key}: "
                  f"{round(total_jpy, 4)} > {BUDGET_TOTAL_JPY}")
            raise SystemExit(1)

    print(f"[DONE] run complete. total_cost_jpy={round(total_jpy, 4)} "
          f"budget_jpy={BUDGET_TOTAL_JPY}")


# ------------------------------------------------------------
# STEP: analyze
# ------------------------------------------------------------
def _decision_log_md(article_label: str, decisions: list, cand_by_word: dict) -> str:
    lines = [f"### {article_label} Decision Log\n",
             "| Word | surface | lemma | 採用rank | 判定 | 例外/理由 | Before | After |",
             "|---|---|---|---|---|---|---|---|"]
    for d in decisions:
        before = d["before_sentence"].replace("|", "\\|")
        after = d["after_sentence"].replace("|", "\\|")
        reasoning = d["reasoning"].replace("|", "\\|")
        c = cand_by_word.get(d["word"], {})
        surface_rank = c.get("surface_rank")
        surface_disp = f"{surface_rank:,}" if surface_rank else "(none in top20000)"
        lemma_used = c.get("lemma_used")
        lemma_rank = c.get("lemma_rank")
        if lemma_used and lemma_rank:
            lemma_disp = f"{lemma_used}:{lemma_rank:,}"
        elif lemma_used:
            lemma_disp = f"{lemma_used}:(none in top20000)"
        else:
            lemma_disp = "(none)"
        lines.append(
            f"| {d['actual_form']} | {surface_disp} | {lemma_disp} | "
            f"{d['frequency_rank']} | {d['decision']} | {reasoning} | "
            f"{before} | {after} |")
    return "\n".join(lines)


def cmd_analyze(out_dir: str) -> None:
    import wordfreq

    top20000 = wordfreq.top_n_list("en", 20000)
    rank_of = _rank_of_map(top20000)
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

        after_cand = build_candidates(after_text, rank_of)
        struct = structure_check(key, before_text, after_text)
        new_rare = new_rare_words_in_after(
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
            "rank_threshold": RANK_THRESHOLD,
            "borderline_band": [BORDERLINE_LOW, BORDERLINE_HIGH],
            "candidate_count": before_cand["candidate_count"],
            "decision_counts": dict(decision_counts),
            "structure_check": struct,
            "word_count_before": before_levels["word_count"],
            "word_count_after": after_levels["word_count"],
            "word_count_diff": after_levels["word_count"] - before_levels["word_count"],
            "sentence_count_before": before_levels["sentence_count"],
            "sentence_count_after": after_levels["sentence_count"],
            "sentence_count_diff": after_levels["sentence_count"] - before_levels["sentence_count"],
            "new_rare_words_gt6000_in_after": new_rare,
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
                  f"# {key}_decision_log.md\n\n"
                  "凡例: surface=表層形のtop20000内順位, lemma=採用された"
                  "lemma候補(word:順位、未使用または表外は(none)), "
                  "採用rank=min(surface,lemma)としてモデルへ渡した値, "
                  "例外/理由=モデルの判定理由(A/B/C/Dまたは平易化理由)。\n\n" +
                  _decision_log_md(label, decisions, cand_by_word) +
                  f"\n\n### notes_on_ambiguous_cases\n\n{notes}\n")

        diff_md = [f"# {key}_diff.md\n",
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
# STEP: assemble
# ------------------------------------------------------------
def cmd_assemble(out_dir: str) -> None:
    calls = []
    total_jpy = 0.0
    for key in ARTICLE_PATHS:
        raw_path = out_path(out_dir, f"{key}_raw_response.json")
        if not os.path.exists(raw_path):
            print(f"[WARN] missing: {raw_path}")
            continue
        raw = load_json(raw_path)
        calls.append(raw["meta"])
        total_jpy += raw["meta"].get("cost_jpy", 0.0)
    cost = {
        "calls": calls,
        "total_cost_jpy": round(total_jpy, 4),
        "budget_jpy": BUDGET_TOTAL_JPY,
        "within_budget": total_jpy <= BUDGET_TOTAL_JPY,
    }
    save_json(out_path(out_dir, "cost.json"), cost)
    print(f"[OK] cost.json written. total_cost_jpy={round(total_jpy, 4)} "
          f"within_budget={cost['within_budget']}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--step", required=True,
                     choices=["candidates", "run", "analyze", "assemble"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.step == "candidates":
        cmd_candidates(args.out_dir)
    elif args.step == "run":
        cmd_run(args.out_dir, args.force)
    elif args.step == "analyze":
        cmd_analyze(args.out_dir)
    elif args.step == "assemble":
        cmd_assemble(args.out_dir)


if __name__ == "__main__":
    main()
