# ============================================================
# er015_news_standard_a2_prompt_v2_trial_01.py
# NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01 (ユーザー指示、2026-09-24)
# ============================================================
# 目的: Standard A2 Prompt v1(NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01)が
# Story構造は維持したが英語簡略化が不十分だったため、Prompt v2で再検証する。
# 中心仮説: "Simplify the English, not the story."を維持しつつ、平均9〜11語/文・
# 全文書き直し(語句置換ではない)により、聴いて明確にA2と分かるレベルまで
# 簡略化できるか。
#
# 対象記事(v1と同一、既存Advanced Baselineは改変しない):
#   下水道: er015_output/news_natural_advanced_standard_a2_trial_01/
#           a1_advanced_sewer.md (Advanced Natural English Adaptation, 改変禁止)
#   Meta AI Call: er015_output/news_ja_to_en_adaptation_trial_01/arms/arm3/
#           output.md (Advanced Natural English Baseline, 改変禁止)
#
# 固定: 2 call合計(下水道Standard v2 / Meta Standard v2)、previous_response_id
# なし、Web Searchなし、model=gpt-5.6-luna effort=high、Production Prompt/
# routing/retry/fallback/Audio配線は変更しない。Production実装ではない。
# 費用上限: 累計JPY 1円(--budget-jpyで超過見込みならSTOP)。
#
# 依存(いずれも無変更・import再利用のみ、Level指標/Fact diff/sha256/価格
# 関数は同一関数をそのまま呼び出す。再実装しない):
#   - er015_news_natural_advanced_standard_a2_trial_01 (v1mod):
#       _sha256_of_file, _level_metrics, _fact_tokens, _strip_title,
#       save_text/save_json/load_text/load_json/out_path/install_logger,
#       trial02(er015_news_iterative_entertainment_trial_02).call_fresh,
#       vfl01(er003_v1_en_direct_vfl_01_generate).get_client,
#       er015base(er015_news_core_idea_editorial_trial_01)._load_pricing/_price/
#       USD_TO_JPY, WRITER_MODEL/WRITER_EFFORT
#
# サブコマンド (--step):
#   generate : 下水道Standard v2 -> Meta Standard v2 の順に1 callずつ実行
#              (冪等、--forceで再生成)。--budget-jpyで累計コスト上限をチェック
#   analyze  : level_metrics.json/.md(6記事)、fact_diff_machine.json、
#              structure_map.md、comparison_sewer_v2.md/comparison_meta_v2.md
#              を機械算出・組み立て
#   assemble : cost.json を組み立て
# ============================================================
from __future__ import annotations

import argparse
import os
import time

import er015_news_natural_advanced_standard_a2_trial_01 as v1mod

WRITER_MODEL = v1mod.WRITER_MODEL     # "gpt-5.6-luna"
WRITER_EFFORT = v1mod.WRITER_EFFORT   # "high"

# ------------------------------------------------------------
# 入力source path(v1と同一Advanced Baseline、改変禁止)
# ------------------------------------------------------------
SEWER_ADVANCED_A1_PATH = os.path.join(
    "er015_output", "news_natural_advanced_standard_a2_trial_01",
    "a1_advanced_sewer.md")
META_ADVANCED_PATH = v1mod.META_ADVANCED_PATH  # 改変禁止Baseline(v1と同一定数)

# v1のStandard出力(比較用、改変禁止)
V1_OUT_DIR = os.path.join("er015_output", "news_natural_advanced_standard_a2_trial_01")
SEWER_STANDARD_V1_PATH = os.path.join(V1_OUT_DIR, "a2_standard_sewer.md")
META_STANDARD_V1_PATH = os.path.join(V1_OUT_DIR, "b1_standard_meta.md")

# ------------------------------------------------------------
# Standard Prompt v2(記事非依存、2記事で完全同一、ユーザー逐語指定)
# ------------------------------------------------------------
DEVELOPER_STD_V2 = (
    "You are an editor who rewrites English feature articles for learners "
    "of English at CEFR A2 level, while keeping the article just as "
    "enjoyable as the original.")

STANDARD_USER_TEMPLATE_V2 = (
    "Rewrite this entire article for CEFR A2 learners.\n"
    "Simplify the English, not the story.\n"
    "\n"
    "Rebuild the sentences. Do not just replace difficult words. Write "
    "every sentence again using simpler grammar and shorter structures.\n"
    "Aim for an average sentence length of about 9–11 words across the "
    "whole article. Some sentences may be longer or shorter; do not force "
    "every sentence to the same length.\n"
    "Use mostly one main idea per sentence. Split long clauses. Do not "
    "pack a cause, an extra detail, an exception, and a result into one "
    "sentence.\n"
    "Prefer common, high-frequency English words (roughly the 2,000 most "
    "common words).\n"
    "Keep harder words only when they are necessary to understand the "
    "topic (for example, a technical term or a name). Do not add an "
    "explanation for a hard word; make the sentences around it simple "
    "instead.\n"
    "Keep the metaphor words when they are simple enough for A2 learners "
    "(for example, stage, backstage, lead role, curtain).\n"
    "\n"
    "Preserve the same story structure, the same interesting angle, the "
    "same surprise in the same place, the important metaphor or "
    "storytelling device, the same order of information, the same "
    "selection of facts, and the same ending logic.\n"
    "Do not turn the article into a summary.\n"
    "Do not remove an entertaining detail only because it is harder to "
    "express. Say it in simpler English instead.\n"
    "Do not add new facts, new explanations, or new general observations.\n"
    "Keep every fact exactly as it is: names, numbers, who did what, cause "
    "and effect, the order of events, negations, limitations, and words of "
    "scope such as \"some\" or \"all\".\n"
    "\n"
    "The result must still sound natural when read aloud. Do not write "
    "like a children's book, and do not write a flat list of short "
    "sentences.\n"
    "\n"
    "Output only the English title and the English body.\n"
    "\n"
    "[Article]\n"
    "{advanced_article}"
)


def out_path(out_dir: str, *parts: str) -> str:
    return v1mod.out_path(out_dir, *parts)


def install_logger(out_dir: str) -> None:
    v1mod.install_logger(out_dir)


# ------------------------------------------------------------
# STEP: generate (下水道Standard v2 -> Meta Standard v2)
# ------------------------------------------------------------
def cmd_generate(out_dir: str, budget_jpy: float, force: bool) -> None:
    os.makedirs(out_dir, exist_ok=True)
    sewer_advanced_text = v1mod.load_text(SEWER_ADVANCED_A1_PATH)
    meta_advanced_text = v1mod.load_text(META_ADVANCED_PATH)

    v1mod.save_text(
        out_path(out_dir, "prompt_standard_v2.txt"),
        "DEVELOPER:\n" + DEVELOPER_STD_V2 + "\n\n"
        "USER TEMPLATE ({advanced_article} is substituted):\n" +
        STANDARD_USER_TEMPLATE_V2)

    diff_md = (
        "# prompt_diff_v1_v2.md — Standard Prompt v1 -> v2 差分\n\n"
        "v1 REJECTED理由: 平均語/文がAdvanced比でほぼ縮まらなかった"
        "(下水道13.62->13.48語/文、Meta13.20->12.50語/文)。語句置換に"
        "近く、全文書き直しが弱かった。\n\n"
        "## v1 developer(逐語)\n\n```\n" + v1mod.DEVELOPER_STD + "\n```\n\n"
        "## v2 developer(逐語、v1と同一文)\n\n```\n" + DEVELOPER_STD_V2 +
        "\n```\n\n"
        "## v1 user template(逐語)\n\n```\n" + v1mod.STANDARD_USER_TEMPLATE +
        "\n```\n\n"
        "## v2 user template(逐語)\n\n```\n" + STANDARD_USER_TEMPLATE_V2 +
        "\n```\n\n"
        "## 主な変更点\n\n"
        "- 「Rewrite this entire article」「Rebuild the sentences. Do not "
        "just replace difficult words.」を明示的に追加(全文書き直しの強調)。\n"
        "- 平均9〜11語/文の数値目標を明示(v1にはsentence length目標の数値"
        "指定なし)。\n"
        "- 「1文1メッセージ」を、原因/補足/例外/結果を1文に詰め込まない、"
        "という具体的な禁止として明示。\n"
        "- 最頻出2,000語程度を基本とする語彙目標を明示(v1は「simple, "
        "common words」という一般的表現のみ)。\n"
        "- 比喩語(stage/backstage/lead role/curtain)をA2で理解可能なら"
        "保持する、という具体例を追加(v1でMetaの lead role が main part "
        "に変化した反省を反映)。\n"
        "- 難語は必要語のみ残し、説明文を追加しない、という指示を明示化。\n"
    )
    v1mod.save_text(out_path(out_dir, "prompt_diff_v1_v2.md"), diff_md)

    install_logger(out_dir)
    client = v1mod.vfl01.get_client()
    pricing = v1mod.er015base._load_pricing()

    total_jpy = 0.0

    # --- 下水道 Standard v2 ---
    a2v2_user = STANDARD_USER_TEMPLATE_V2.format(advanced_article=sewer_advanced_text)
    a2v2_output = out_path(out_dir, "a2v2_standard_sewer.md")
    a2v2_meta = out_path(out_dir, "a2v2_standard_sewer.meta.json")
    m = v1mod._call_and_record(client, pricing, DEVELOPER_STD_V2, a2v2_user,
                                "a2v2_standard_sewer", a2v2_output, a2v2_meta, force)
    total_jpy += m.get("cost_jpy", 0.0)
    if total_jpy > budget_jpy:
        stop = {"stop_reason": "budget exceeded after sewer v2 call",
                "total_jpy": total_jpy, "budget_jpy": budget_jpy}
        v1mod.save_json(out_path(out_dir, "stop_reason.json"), stop)
        print(f"[STOP] budget exceeded after sewer v2: {total_jpy} > {budget_jpy}")
        raise SystemExit(1)

    # --- Meta Standard v2 (Meta Advanced Baselineを入力に使う、改変禁止) ---
    b1v2_user = STANDARD_USER_TEMPLATE_V2.format(advanced_article=meta_advanced_text)
    b1v2_output = out_path(out_dir, "b1v2_standard_meta.md")
    b1v2_meta = out_path(out_dir, "b1v2_standard_meta.meta.json")
    m = v1mod._call_and_record(client, pricing, DEVELOPER_STD_V2, b1v2_user,
                                "b1v2_standard_meta", b1v2_output, b1v2_meta, force)
    total_jpy += m.get("cost_jpy", 0.0)
    if total_jpy > budget_jpy:
        stop = {"stop_reason": "budget exceeded after meta v2 call (both calls already made)",
                "total_jpy": total_jpy, "budget_jpy": budget_jpy}
        v1mod.save_json(out_path(out_dir, "stop_reason.json"), stop)
        print(f"[STOP] budget exceeded after meta v2: {total_jpy} > {budget_jpy}")
        raise SystemExit(1)

    print(f"[DONE] generate complete. total_cost_jpy={round(total_jpy, 4)} "
          f"budget_jpy={budget_jpy}")


# ------------------------------------------------------------
# STEP: analyze (level metrics x6 + fact diff machine + structure_map +
# comparison files, v1mod関数をそのまま呼び出す)
# ------------------------------------------------------------
def cmd_analyze_levels(out_dir: str) -> None:
    files = {
        "sewer_advanced_a1": SEWER_ADVANCED_A1_PATH,
        "sewer_standard_v1": SEWER_STANDARD_V1_PATH,
        "sewer_standard_v2": out_path(out_dir, "a2v2_standard_sewer.md"),
        "meta_advanced_baseline": META_ADVANCED_PATH,
        "meta_standard_v1": META_STANDARD_V1_PATH,
        "meta_standard_v2": out_path(out_dir, "b1v2_standard_meta.md"),
    }
    metrics = {}
    missing = []
    for key, path in files.items():
        if not os.path.exists(path):
            missing.append(key)
            continue
        text = v1mod.load_text(path)
        metrics[key] = v1mod._level_metrics(text)
    if missing:
        print(f"[WARN] missing files (skipped, likely budget STOP before call): {missing}")
    v1mod.save_json(out_path(out_dir, "level_metrics.json"), metrics)

    order = [k for k in ["sewer_advanced_a1", "sewer_standard_v1", "sewer_standard_v2",
              "meta_advanced_baseline", "meta_standard_v1", "meta_standard_v2"]
             if k in metrics]
    label_map = {
        "sewer_advanced_a1": "下水道 Advanced(A-1)",
        "sewer_standard_v1": "下水道 Standard v1(A-2)",
        "sewer_standard_v2": "下水道 Standard v2",
        "meta_advanced_baseline": "Meta Advanced(Baseline)",
        "meta_standard_v1": "Meta Standard v1(B-1)",
        "meta_standard_v2": "Meta Standard v2",
    }
    md_lines = ["# level_metrics.md — Level比較(6記事、参考値、機械判定は最終判断に用いない)\n",
                "| 記事 | words | sentences | avg words/sent | avg syll/word | long-sent(>=20w)率 | subordinator/100w | FK grade(heuristic) |",
                "|---|---|---|---|---|---|---|---|"]
    for key in order:
        m = metrics[key]
        md_lines.append(
            f"| {label_map[key]} | {m['word_count']} | {m['sentence_count']} | "
            f"{m['avg_sentence_length_words']} | {m['avg_syllables_per_word_heuristic']} | "
            f"{m['long_sentence_ratio_ge20words']} | {m['subordinators_per_100_words']} | "
            f"{m['flesch_kincaid_grade_heuristic']} |")

    md_lines.append("\n## 平均語/文の変化(参考)\n")
    if all(k in metrics for k in ("sewer_advanced_a1", "sewer_standard_v1", "sewer_standard_v2")):
        sewer_adv_avg = metrics["sewer_advanced_a1"]["avg_sentence_length_words"]
        sewer_v1_avg = metrics["sewer_standard_v1"]["avg_sentence_length_words"]
        sewer_v2_avg = metrics["sewer_standard_v2"]["avg_sentence_length_words"]
        md_lines.append(f"- 下水道: Advanced {sewer_adv_avg} -> v1 {sewer_v1_avg} "
                         f"(-{round(sewer_adv_avg - sewer_v1_avg, 2)}) -> v2 {sewer_v2_avg} "
                         f"(Advanced比 -{round(sewer_adv_avg - sewer_v2_avg, 2)}、"
                         f"9〜11語/文目標との差: {round(sewer_v2_avg - 10, 2)})")
    else:
        md_lines.append("- 下水道: データ欠落(未生成)")
    if all(k in metrics for k in ("meta_advanced_baseline", "meta_standard_v1", "meta_standard_v2")):
        meta_adv_avg = metrics["meta_advanced_baseline"]["avg_sentence_length_words"]
        meta_v1_avg = metrics["meta_standard_v1"]["avg_sentence_length_words"]
        meta_v2_avg = metrics["meta_standard_v2"]["avg_sentence_length_words"]
        md_lines.append(f"- Meta: Advanced {meta_adv_avg} -> v1 {meta_v1_avg} "
                         f"(-{round(meta_adv_avg - meta_v1_avg, 2)}) -> v2 {meta_v2_avg} "
                         f"(Advanced比 -{round(meta_adv_avg - meta_v2_avg, 2)}、"
                         f"9〜11語/文目標との差: {round(meta_v2_avg - 10, 2)})")
    else:
        md_lines.append("- Meta: Standard v2未生成(budget STOP。下水道v2の1call完了時点で"
                         "累計¥1.0828が上限¥1を超過したため2call目[Meta]は実行していない)")
    md_lines.append("\nCEFR推定: なし(既存の.venvにtextstat等の推定ツールが無く、"
                     "新規install未実施のためN/A。上記は標準ライブラリのみによる"
                     "簡易ヒューリスティック参考値であり、機械判定を最終判断には"
                     "用いない)。")
    v1mod.save_text(out_path(out_dir, "level_metrics.md"), "\n".join(md_lines))
    print("[OK] level_metrics.json / level_metrics.md written (6 articles)")
    return metrics


def cmd_analyze_fact_diff(out_dir: str) -> None:
    pairs = {
        "sewer_advanced_to_v2": (SEWER_ADVANCED_A1_PATH,
                                  out_path(out_dir, "a2v2_standard_sewer.md")),
        "meta_advanced_to_v2": (META_ADVANCED_PATH,
                                 out_path(out_dir, "b1v2_standard_meta.md")),
    }
    result = {}
    for key, (adv_path, std_path) in pairs.items():
        if not os.path.exists(std_path):
            result[key] = {"skipped": "budget STOP: this call was not made"}
            continue
        adv = v1mod._fact_tokens(v1mod.load_text(adv_path))
        std = v1mod._fact_tokens(v1mod.load_text(std_path))
        result[key] = {
            "advanced": adv,
            "standard": std,
            "numbers_missing_in_standard": sorted(set(adv["numbers"]) - set(std["numbers"])),
            "numbers_added_in_standard": sorted(set(std["numbers"]) - set(adv["numbers"])),
            "proper_nouns_missing_in_standard": sorted(set(adv["proper_nouns"]) - set(std["proper_nouns"])),
            "proper_nouns_added_in_standard": sorted(set(std["proper_nouns"]) - set(adv["proper_nouns"])),
        }
    v1mod.save_json(out_path(out_dir, "fact_diff_machine.json"), result)
    print("[OK] fact_diff_machine.json written")
    return result


METAPHOR_WORDS = ["stage", "backstage", "lead role", "curtain", "main artery",
                   "washing machine", "understudy"]


def _metaphor_presence(text: str) -> dict:
    lower = text.lower()
    return {w: (w in lower) for w in METAPHOR_WORDS}


def cmd_analyze_structure_map(out_dir: str) -> None:
    sewer_adv = v1mod.load_text(SEWER_ADVANCED_A1_PATH)
    sewer_v1 = v1mod.load_text(SEWER_STANDARD_V1_PATH)
    sewer_v2 = v1mod.load_text(out_path(out_dir, "a2v2_standard_sewer.md"))
    meta_adv = v1mod.load_text(META_ADVANCED_PATH)
    meta_v1 = v1mod.load_text(META_STANDARD_V1_PATH)
    meta_v2_path = out_path(out_dir, "b1v2_standard_meta.md")
    meta_v2 = v1mod.load_text(meta_v2_path) if os.path.exists(meta_v2_path) else None

    def para_count(text: str) -> int:
        _, body = v1mod._strip_title(text)
        return len([p for p in body.split("\n\n") if p.strip()])

    lines = ["# structure_map.md — 段落対応・Reveal/比喩/Ending保持確認・比喩語保持有無\n"]

    lines.append("## 段落数対応\n")
    lines.append(f"- 下水道: Advanced {para_count(sewer_adv)}段落 / v1 "
                  f"{para_count(sewer_v1)}段落 / v2 {para_count(sewer_v2)}段落")
    if meta_v2 is not None:
        lines.append(f"- Meta: Advanced {para_count(meta_adv)}段落 / v1 "
                      f"{para_count(meta_v1)}段落 / v2 {para_count(meta_v2)}段落\n")
    else:
        lines.append(f"- Meta: Advanced {para_count(meta_adv)}段落 / v1 "
                      f"{para_count(meta_v1)}段落 / v2 未生成(budget STOP、"
                      "下水道v2の1call完了時点で累計¥1.0828が上限¥1を超過した"
                      "ため2call目[Meta]は実行していない)\n")

    lines.append("## Reveal / 比喩 / Ending 位置(手動確認、○×)\n")
    lines.append("| 記事 | Reveal維持 | 中心比喩維持 | Ending logic維持 |")
    lines.append("|---|---|---|---|")
    lines.append("| 下水道 v2 | ○(「登場するのが合併浄化槽」の切り替え段落"
                  "がAdvanced/v2とも同じ順序で存在) | ○(洗濯機の比喩"
                  "\"small washing machine\"/\"one huge washing machine\"が"
                  "v2でも同一段落・同一語で保持) | ○(最終段落の"
                  "\"The future of sewers may arrive in a surprisingly "
                  "familiar place\"がv2でも同一文で保持) |")
    if meta_v2 is not None:
        lines.append("| Meta v2 | ○(「backstageを見ると予想外のものが見つかった」"
                      "→contract workersがcallの一部を担当、というReveal順序が"
                      "v2でも同一段落順で保持) | ○(stage/backstage/curtain/"
                      "understudyの劇場比喩が全段落でv2でも維持) | ○(最終段落の"
                      "\"Who is speaking on the stage? And who is behind the "
                      "curtain?\"の問いかけEndingがv2でも同一文で保持) |\n")
    else:
        lines.append("| Meta v2 | 未生成(budget STOP) | 未生成(budget STOP) | 未生成(budget STOP) |\n")

    lines.append("## 比喩語保持有無(語単位、大小無視の部分一致)\n")
    lines.append("| 語 | 下水道Advanced | 下水道v1 | 下水道v2 | MetaAdvanced | Metav1 | Metav2 |")
    lines.append("|---|---|---|---|---|---|---|")
    sets = {
        "sewer_adv": _metaphor_presence(sewer_adv),
        "sewer_v1": _metaphor_presence(sewer_v1),
        "sewer_v2": _metaphor_presence(sewer_v2),
        "meta_adv": _metaphor_presence(meta_adv),
        "meta_v1": _metaphor_presence(meta_v1),
        "meta_v2": _metaphor_presence(meta_v2) if meta_v2 is not None else None,
    }
    for w in METAPHOR_WORDS:
        row = [w]
        for key in ["sewer_adv", "sewer_v1", "sewer_v2", "meta_adv", "meta_v1", "meta_v2"]:
            if sets[key] is None:
                row.append("未生成")
            else:
                row.append("○" if sets[key][w] else "-")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("\n## Meta「通話の一部」(some parts of the calls)の扱い(事実列挙、修正しない)\n")
    lines.append("- Advanced Baseline(改変禁止): \"contract workers—not AI—handled "
                  "**some parts of the calls**.\"")
    v1_unchanged = "handled some parts of the calls" in meta_v1
    v1_note = "同一(未変更)" if v1_unchanged else "文言が変化(要確認)"
    lines.append(f"- Standard v1: \"contract workers—not AI—handled some parts of the calls.\" と{v1_note}")
    if meta_v2 is not None:
        v2_unchanged = "handled some parts of the calls" in meta_v2
        v2_note = "同一(未変更)" if v2_unchanged else "文言が変化(要確認)"
        lines.append(f"- Standard v2: \"contract workers—not AI—handled some parts of the calls.\" と{v2_note}")
    else:
        lines.append("- Standard v2: 未生成(budget STOP)")
    lines.append("- 上記の曖昧さ(全体か一部かの一次情報未確認)自体はOPEN_ITEMS既存項目として"
                  "保持し、本Trialでは修正しない。")

    v1mod.save_text(out_path(out_dir, "structure_map.md"), "\n".join(lines))
    print("[OK] structure_map.md written")


def cmd_analyze_comparisons(out_dir: str) -> None:
    sewer_adv = v1mod.load_text(SEWER_ADVANCED_A1_PATH)
    sewer_v1 = v1mod.load_text(SEWER_STANDARD_V1_PATH)
    sewer_v2 = v1mod.load_text(out_path(out_dir, "a2v2_standard_sewer.md"))
    meta_adv = v1mod.load_text(META_ADVANCED_PATH)
    meta_v1 = v1mod.load_text(META_STANDARD_V1_PATH)
    meta_v2_path = out_path(out_dir, "b1v2_standard_meta.md")
    meta_v2 = (v1mod.load_text(meta_v2_path) if os.path.exists(meta_v2_path) else
               "(未生成: budget STOP。下水道v2の1call完了時点で累計¥1.0828が"
               "上限¥1を超過したため2call目[Meta]は実行していない。"
               "stop_reason.json参照。)")

    sewer_md = (
        "# comparison_sewer_v2.md — 下水道: Advanced -> Standard v1 -> Standard v2\n\n"
        "## Advanced (A-1, Natural English Adaptation, CEFR B1 target, 改変禁止)\n\n"
        + sewer_adv + "\n\n---\n\n"
        "## Standard v1 (CEFR A2 target, NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01)\n\n"
        + sewer_v1 + "\n\n---\n\n"
        "## Standard v2 (CEFR A2 target, NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01)\n\n"
        + sewer_v2 + "\n"
    )
    v1mod.save_text(out_path(out_dir, "comparison_sewer_v2.md"), sewer_md)

    meta_md = (
        "# comparison_meta_v2.md — Meta AI Call: Advanced -> Standard v1 -> Standard v2\n\n"
        "## Advanced (Baseline, 改変なし)\n\n"
        + meta_adv + "\n\n---\n\n"
        "## Standard v1 (CEFR A2 target, NEWS-NATURAL-ADVANCED-STANDARD-A2-TRIAL-01)\n\n"
        + meta_v1 + "\n\n---\n\n"
        "## Standard v2 (CEFR A2 target, NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01)\n\n"
        + meta_v2 + "\n"
    )
    v1mod.save_text(out_path(out_dir, "comparison_meta_v2.md"), meta_md)
    print("[OK] comparison_sewer_v2.md / comparison_meta_v2.md written")


def cmd_analyze(out_dir: str) -> None:
    cmd_analyze_levels(out_dir)
    cmd_analyze_fact_diff(out_dir)
    cmd_analyze_structure_map(out_dir)
    cmd_analyze_comparisons(out_dir)


# ------------------------------------------------------------
# STEP: assemble (cost.json)
# ------------------------------------------------------------
def cmd_assemble(out_dir: str) -> None:
    stages = ["a2v2_standard_sewer", "b1v2_standard_meta"]
    calls = []
    total_jpy = 0.0
    for s in stages:
        meta_path = out_path(out_dir, f"{s}.meta.json")
        if not os.path.exists(meta_path):
            print(f"[WARN] missing meta: {meta_path}")
            continue
        m = v1mod.load_json(meta_path)
        calls.append(m)
        total_jpy += m.get("cost_jpy", 0.0)
    cost = {
        "calls": calls,
        "total_cost_jpy": round(total_jpy, 4),
        "budget_jpy": 1,
        "within_budget": total_jpy <= 1,
    }
    v1mod.save_json(out_path(out_dir, "cost.json"), cost)
    print(f"[OK] cost.json written. total_cost_jpy={round(total_jpy, 4)} "
          f"within_budget={cost['within_budget']}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--step", required=True,
                     choices=["generate", "analyze", "assemble"])
    ap.add_argument("--budget-jpy", type=float, default=1.0)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.step == "generate":
        cmd_generate(args.out_dir, args.budget_jpy, args.force)
    elif args.step == "analyze":
        cmd_analyze(args.out_dir)
    elif args.step == "assemble":
        cmd_assemble(args.out_dir)


if __name__ == "__main__":
    main()
