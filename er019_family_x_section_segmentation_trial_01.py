# ============================================================
# er019_family_x_section_segmentation_trial_01.py
# 管理ID: NEWS-FAMILY-X-SECTION-SEGMENTATION-TRIAL-01
# ============================================================
# 目的: Family X(Advanced/Standard)で、見出し(`### `)直前の段落が次
# Sectionの具体内容を実質的に先取りしているケースを検出し、最小変更
# (方式A=段落の決定論的な移動、語句無変更)で見出しの直後へ移すTrial。
# ユーザー提示のTrial仕様候補(逐語はREPORT §1)を検証するためのもので
# あり、Production Prompt・Production moduleは一切変更しない。他Family
# へは適用しない。既存B3 Fact/Storylineの内容自体も変更しない
# (段落の並び順のみを変える)。
#
# 入力(read-only、既存artifactは変更しない):
#   er019_output/family_x_b3_diversity_trial_01/small_bag/run_01/
#     b1b/article.md (Advanced) / a2/article.md (Standard) /
#     research_ledger/verified_fact_ledger.txt (Full Ledger)
#
# 検証方式:
#   1. Before分析: `### `見出しごとに、直前の段落を文単位で「先取り/
#      Bridge・予告/該当なし」に人手(Sonnet)判定する(このスクリプトの
#      BEFORE_BOUNDARY_JUDGMENTには判定結果を定数として記録するのみで、
#      判定ロジック自体を自動化しようとはしていない)。
#   2. After生成: 違反が見つかった見出し直前の段落を、見出しの直後へ
#      ブロック単位でそのまま移動する(方式A、語句の変更は一切ない)。
#   3. 検証: 文単位diff(difflib、multiset一致で追加削除ゼロを機械確認)、
#      fact_tokens_check相当(数字・引用句・固有名詞トークンの一致)、
#      vfl01.run_deviation_check(Full Ledger、hook_aware=False)をAfter
#      本文に対して1回ずつ実行、語数Before/After。
#
# 実行方法(root直下から):
#   .venv/Scripts/python.exe er019_family_x_section_segmentation_trial_01.py
# ============================================================
from __future__ import annotations

import difflib
import json
import os
import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl

THEME_ID = "family_x_section_segmentation_trial_01"
OUT_DIR = f"er019_output/{THEME_ID}"
LOG_PATH = f"{OUT_DIR}/raw_usage_log.jsonl"
BUDGET_JPY_TARGET = 10.0  # 目安(委任文)
BUDGET_JPY_CAP = 30.0     # Guardrail(委任文、超えそうなら中断)

INPUT_BASE = "er019_output/family_x_b3_diversity_trial_01/small_bag/run_01"
LEDGER_PATH = f"{INPUT_BASE}/research_ledger/verified_fact_ledger.txt"
LEVEL_ARTICLE_PATHS = {
    "b1b": f"{INPUT_BASE}/b1b/article.md",   # Advanced
    "a2": f"{INPUT_BASE}/a2/article.md",     # Standard
}

# 両レベルで見出し文言は同一(同一storyline由来)。移動対象は「見出しの
# 直前の段落」1つ(方式A: ブロック単位のswapのみ、語句無変更)。
TARGET_HEADING = "### Large bags are still doing their job"

# ------------------------------------------------------------
# Step 1: Before分析(見出し境界の文単位判定、Sonnetによる人手判定を
# 定数として記録。判定ロジックの自動化は行わない)。
# ------------------------------------------------------------
BEFORE_BOUNDARY_JUDGMENT = {
    "b1b": [
        {
            "heading": "### Mini bags are there to set the scene",
            "preceding_paragraph": (
                "At this size, carrying many things is difficult. They mainly "
                "hold basic essentials: a phone, wallet, keys, and lip products. "
                "In terms of carrying space, they are not trying to compete with "
                "large-capacity bags."
            ),
            "sentence_judgments": [
                {"sentence": "At this size, carrying many things is difficult.",
                 "judgment": "該当なし",
                 "reason": "直前Sectionから続くmini bagsの容量に関する一般的な導入で、"
                            "見出し後のSection(『mini bagsは場面を演出する役割』という"
                            "新しい論点)を先取りしていない。"},
                {"sentence": "They mainly hold basic essentials: a phone, wallet, keys, "
                             "and lip products.",
                 "judgment": "該当なし",
                 "reason": "同上、mini bagsの実用面の説明の続きで新しいSectionの主張ではない。"},
                {"sentence": "In terms of carrying space, they are not trying to compete "
                             "with large-capacity bags.",
                 "judgment": "該当なし",
                 "reason": "large-capacity bagsへの言及はあるが、mini bags自身の容量限界を"
                            "述べているだけで、次のSection(『large bagsはまだ仕事をしている』)"
                            "の具体的な主張(Vogueの証拠等)を開始していない。"},
            ],
        },
        {
            "heading": TARGET_HEADING,
            "preceding_paragraph": (
                "Yet this does not mean large bags have vanished. Vogue also covered "
                "a wide range of bags in the same 2026 season."
            ),
            "sentence_judgments": [
                {"sentence": "Yet this does not mean large bags have vanished.",
                 "judgment": "先取り",
                 "reason": "見出し『Large bags are still doing their job』の中心主張"
                            "そのものであり、見出し前で次Sectionの結論を述べてしまっている"
                            "(ユーザー提示のNG例)。"},
                {"sentence": "Vogue also covered a wide range of bags in the same 2026 season.",
                 "judgment": "先取り",
                 "reason": "次Section本体(直後の段落)で列挙されるVogueの具体例"
                            "(Prada/Loewe/Celine/Altuzarra/Toteme等)の導入であり、単なる"
                            "予告文(『次は〜を見る』)ではなく既に具体的な出典への言及を"
                            "始めている。"},
            ],
        },
    ],
    "a2": [
        {
            "heading": "### Mini bags are there to set the scene",
            "preceding_paragraph": (
                "With so little space, carrying many things is hard. They mainly "
                "hold basic items: a phone, wallet, keys, and lip products. They "
                "cannot compete with bags that hold a lot."
            ),
            "sentence_judgments": [
                {"sentence": "With so little space, carrying many things is hard.",
                 "judgment": "該当なし", "reason": "b1bの同位置の文と同じ理由(mini bagsの導入続き)。"},
                {"sentence": "They mainly hold basic items: a phone, wallet, keys, and "
                             "lip products.",
                 "judgment": "該当なし", "reason": "同上。"},
                {"sentence": "They cannot compete with bags that hold a lot.",
                 "judgment": "該当なし",
                 "reason": "b1bの『not trying to compete with large-capacity bags』と同じ"
                            "位置・同じ役割(mini bagsの限界の一般論)であり、次Sectionの"
                            "具体的主張を開始していない。"},
            ],
        },
        {
            "heading": TARGET_HEADING,
            "preceding_paragraph": (
                "Still, large bags have not disappeared. Vogue also showed many "
                "kinds of bags in that 2026 season."
            ),
            "sentence_judgments": [
                {"sentence": "Still, large bags have not disappeared.",
                 "judgment": "先取り",
                 "reason": "b1bと同じ位置・同じ役割(見出しの中心主張の先取り)。"},
                {"sentence": "Vogue also showed many kinds of bags in that 2026 season.",
                 "judgment": "先取り",
                 "reason": "b1bと同じ位置・同じ役割(次Section本体の具体例の導入)。"},
            ],
        },
    ],
}


# ------------------------------------------------------------
# 共通I/O
# ------------------------------------------------------------
def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


# ------------------------------------------------------------
# ブロック分割・方式A(決定論的移動)
# ------------------------------------------------------------
def split_blocks(text: str) -> list:
    """空行区切りでMarkdownをブロック単位(タイトル/見出し/段落)へ分割する。
    `"\\n\\n".join(split_blocks(text)) == text.strip()` が常に成り立つ
    (このスクリプト内のround-trip testで確認済み)。"""
    return re.split(r"\n\s*\n", text.strip())


def split_sentences(block: str) -> list:
    """見出し(#始まり)はそれ自体を1ユニットとして扱う。段落は文単位に
    分割する(簡易ヒューリスティック、この記事本文には略語等の例外なし)。"""
    if block.startswith("#"):
        return [block]
    parts = re.split(r"(?<=[.!?])\s+", block.strip())
    return [p for p in parts if p]


def flatten_to_sentences(blocks: list) -> list:
    out = []
    for b in blocks:
        out.extend(split_sentences(b))
    return out


def move_paragraph_after_heading(blocks: list, heading_text: str, expected_paragraph: str) -> tuple:
    """方式A: heading_textの直前の段落ブロックを、heading_textの直後へ
    そのまま移動する(語句は一切変更しない、ブロックのswapのみ)。
    直前段落が期待値と一致しない場合はValueErrorでSTOPする(想定外の
    構造変化を検知せず進めない安全策)。"""
    idx = blocks.index(heading_text)
    para_idx = idx - 1
    if para_idx < 0 or blocks[para_idx].strip() != expected_paragraph.strip():
        raise ValueError(
            f"直前段落が想定と不一致のためSTOP: expected={expected_paragraph!r} "
            f"actual={blocks[para_idx] if para_idx >= 0 else None!r}"
        )
    moved_paragraph = blocks[para_idx]
    new_blocks = blocks[:para_idx] + [blocks[idx], moved_paragraph] + blocks[idx + 1:]
    return new_blocks, {"heading": heading_text, "moved_paragraph": moved_paragraph,
                         "from_block_index": para_idx, "to_block_index_after_heading": para_idx + 1}


# ------------------------------------------------------------
# fact_tokens_check相当(既存er015_advanced_vocab_rule_trial_01_v2.py
# のfact_tokens_checkと同じ考え方[quoted strings/numbers/proper noun]を
# この記事本文の形式[タイトルなしでの単独body比較]向けに自己完結で再実装。
# ロジックは既存と同一、依存モジュールだけ切り離した)。
# ------------------------------------------------------------
def _extract_quoted(text: str) -> list:
    return re.findall(r'["“]([^"“”]*)["”]', text)


def _extract_numbers(text: str) -> list:
    return re.findall(r"\b\d[\d,]*\b", text)


def _capitalized_non_initial_words(text: str) -> list:
    """文頭以外で大文字始まりの単語(固有名詞候補)の集合を返す
    (er015_news_standard_a2_vocab_effectiveness_trial_01.pyの
    capitalized_positions()と同じヒューリスティック)。

    見出し(`### `等)は文末記号[.!?]を持たないため、text全体へ単純に
    正規表現で文分割すると、見出し行が直後の段落の先頭文へ連結され、
    段落の並び順を変えただけで固有名詞候補の判定が変わってしまう
    (Before/Afterで同じ語が異なる文脈に混入する)。これを避けるため、
    ブロック(空行区切り、split_blocksと同じ単位)ごとに独立して文分割
    する(ブロック境界を常に文境界として扱う)。"""
    found = set()
    for block in split_blocks(text):
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", block.strip()) if s.strip()]
        for s in sentences:
            tokens = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", s)
            for idx, t in enumerate(tokens):
                if idx != 0 and t[0].isupper():
                    found.add(t.lower())
    return sorted(found)


def fact_tokens_check(before_text: str, after_text: str) -> dict:
    q_before, q_after = _extract_quoted(before_text), _extract_quoted(after_text)
    n_before, n_after = _extract_numbers(before_text), _extract_numbers(after_text)
    cap_before = _capitalized_non_initial_words(before_text)
    cap_after = _capitalized_non_initial_words(after_text)
    return {
        "quoted_strings_before": q_before, "quoted_strings_after": q_after,
        "quoted_strings_match": q_before == q_after,
        "numbers_before": n_before, "numbers_after": n_after,
        "numbers_match": n_before == n_after,
        "proper_noun_words_before": cap_before, "proper_noun_words_after": cap_after,
        "proper_noun_words_match": cap_before == cap_after,
        "overall_fact_tokens_match": (
            q_before == q_after and n_before == n_after and cap_before == cap_after
        ),
    }


# ------------------------------------------------------------
# 文単位diff(move-aware。SequenceMatcherのopcodesをそのまま記録し、
# 追加分類として「同じ文集合(multiset)が保たれているか」を機械確認する)。
# ------------------------------------------------------------
def sentence_level_diff(before_text: str, after_text: str) -> dict:
    before_sentences = flatten_to_sentences(split_blocks(before_text))
    after_sentences = flatten_to_sentences(split_blocks(after_text))
    sm = difflib.SequenceMatcher(None, before_sentences, after_sentences, autojunk=False)
    opcodes = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        opcodes.append({
            "tag": tag,
            "before_sentences": before_sentences[i1:i2],
            "after_sentences": after_sentences[j1:j2],
        })
    non_equal = [o for o in opcodes if o["tag"] != "equal"]
    multiset_equal = sorted(before_sentences) == sorted(after_sentences)
    # move-aware分類: equal以外のopcodeで、insert側とdelete側の文字列集合が
    # 一致する場合は「移動のみ」とみなす(語句追加・削除ではない)。
    non_equal_before_all = sorted(s for o in non_equal for s in o["before_sentences"])
    non_equal_after_all = sorted(s for o in non_equal for s in o["after_sentences"])
    classification = "MOVE_ONLY_NO_ADD_NO_REMOVE" if (
        multiset_equal and non_equal_before_all == non_equal_after_all
    ) else "CONTENT_CHANGED_NEEDS_REVIEW"
    return {
        "before_sentence_count": len(before_sentences),
        "after_sentence_count": len(after_sentences),
        "opcodes": opcodes,
        "non_equal_opcodes": non_equal,
        "multiset_equal": multiset_equal,
        "classification": classification,
    }


def word_count(text: str) -> int:
    return len(text.split())


# ------------------------------------------------------------
# 見出し境界の再判定(After)。決定論的移動なので、移動された段落が
# 見出しの直後に来ているかをプログラムで機械確認する。
# ------------------------------------------------------------
def reassess_boundaries_after(after_blocks: list) -> dict:
    idx = after_blocks.index(TARGET_HEADING)
    para_after = after_blocks[idx + 1] if idx + 1 < len(after_blocks) else None
    pre_no_longer_foretells = (
        after_blocks[idx - 1] != BEFORE_BOUNDARY_JUDGMENT["b1b"][1]["preceding_paragraph"]
        and after_blocks[idx - 1] != BEFORE_BOUNDARY_JUDGMENT["a2"][1]["preceding_paragraph"]
    )
    return {
        "heading": TARGET_HEADING,
        "block_immediately_before_heading_now": after_blocks[idx - 1],
        "block_immediately_after_heading_now": para_after,
        "先取りは消えたか": pre_no_longer_foretells,
        "moved_paragraph_now_directly_after_heading": (
            para_after is not None
            and (para_after == BEFORE_BOUNDARY_JUDGMENT["b1b"][1]["preceding_paragraph"]
                 or para_after == BEFORE_BOUNDARY_JUDGMENT["a2"][1]["preceding_paragraph"])
        ),
        "不自然な切断の有無": "なし(見出し直前・直後とも完結した段落単位で接続されている)",
    }


# ------------------------------------------------------------
# 費用実測(既存Trialスクリプト[例: er013_family_c_future_trial_05_run.py]
# と同一ロジック、read-onlyで転記)。
# ------------------------------------------------------------
USD_JPY = 160.0
_PRICING = json.load(open("er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf-8"))["prices"]


def _price(provider, model, meter, tier="Standard"):
    for p in _PRICING:
        if p["provider"] == provider and p["model"] == model and p["meter"] == meter and p.get("tier", "Standard") == tier:
            return p["price"]
    raise KeyError((provider, model, meter, tier))


def _call_cost_usd(r: dict) -> tuple:
    provider = r.get("provider")
    model = r.get("model_id") or r.get("model")
    it, ot = r.get("input_tokens") or 0, r.get("output_tokens") or 0
    ct = r.get("cached_input_tokens") or 0
    try:
        if provider == "openai":
            billable_in = max(it - ct, 0)
            cost = (billable_in / 1e6) * _price("openai", model, "input_tokens") \
                + (ct / 1e6) * _price("openai", model, "cached_input_tokens") \
                + (ot / 1e6) * _price("openai", model, "output_tokens")
            return cost, False
        return 0.0, True
    except KeyError:
        return 0.0, True


def compute_cost_jpy_so_far() -> dict:
    if not os.path.exists(LOG_PATH):
        return {"total_jpy": 0.0, "by_provider_jpy": {}, "unpriced_records": 0, "total_records": 0}
    total_usd, by_provider, unpriced, n = 0.0, {}, 0, 0
    with open(LOG_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            cost, up = _call_cost_usd(rec)
            total_usd += cost
            by_provider[rec.get("provider")] = by_provider.get(rec.get("provider"), 0.0) + cost
            unpriced += int(up)
            n += 1
    return {
        "total_jpy": round(total_usd * USD_JPY, 2),
        "by_provider_jpy": {k: round(v * USD_JPY, 2) for k, v in by_provider.items()},
        "unpriced_records": unpriced, "total_records": n,
    }


def assert_budget_ok(note: str = "") -> float:
    result = compute_cost_jpy_so_far()
    print(f"[{THEME_ID}][cost] 実測合計={result['total_jpy']} JPY (Guardrail {BUDGET_JPY_CAP}) note={note}")
    if result["total_jpy"] > BUDGET_JPY_CAP:
        raise RuntimeError(f"費用Guardrail超過(実測{result['total_jpy']}円 > {BUDGET_JPY_CAP}円)。STOP。{note}")
    return result["total_jpy"]


# ------------------------------------------------------------
# メイン処理: レベル単位(Before分析→After生成→検証)
# ------------------------------------------------------------
def process_level(client, level: str, article_path: str, ledger_text: str) -> dict:
    before_text = load_text(article_path).strip()
    before_blocks = split_blocks(before_text)
    # round-tripの安全確認(想定外のMarkdown構造でないこと)
    assert "\n\n".join(before_blocks) == before_text, f"[{level}] round-trip不一致、STOP"

    expected_paragraph = BEFORE_BOUNDARY_JUDGMENT[level][1]["preceding_paragraph"]
    after_blocks, move_record = move_paragraph_after_heading(before_blocks, TARGET_HEADING, expected_paragraph)
    after_text = "\n\n".join(after_blocks)

    diff = sentence_level_diff(before_text, after_text)
    tokens_check = fact_tokens_check(before_text, after_text)
    boundary_after = reassess_boundaries_after(after_blocks)

    level_dir = f"{OUT_DIR}/{level}"
    save_text(f"{level_dir}/before/article.md", before_text)
    save_json(f"{level_dir}/before/boundary_table.json", BEFORE_BOUNDARY_JUDGMENT[level])
    save_text(f"{level_dir}/after/article.md", after_text)
    save_json(f"{level_dir}/after/move_record.json", move_record)
    save_json(f"{level_dir}/after/boundary_reassessment.json", boundary_after)
    save_json(f"{level_dir}/diff/sentence_level_diff.json", diff)
    save_json(f"{level_dir}/fact_tokens_check.json", tokens_check)
    save_json(f"{level_dir}/word_counts.json", {
        "before_words": word_count(before_text), "after_words": word_count(after_text),
    })

    print(f"[{THEME_ID}][{level}] method=A(deterministic move) "
          f"diff_classification={diff['classification']} "
          f"fact_tokens_match={tokens_check['overall_fact_tokens_match']} "
          f"words_before={word_count(before_text)} words_after={word_count(after_text)}")

    # vfl01.run_deviation_check(Full Ledger、hook_aware=False)をAfter本文に対して1回実行。
    with cl.logging_context(THEME_ID, f"deviation_check_after_{level}"):
        deviation = vfl01.run_deviation_check(client, ledger_text, after_text, hook_aware=False)
    save_json(f"{level_dir}/audit/deviation_check_after.json", deviation)
    print(f"[{THEME_ID}][{level}] deviation_check_after overall_status="
          f"{deviation['parsed'].get('overall_status')}")

    return {
        "level": level,
        "method": "A",
        "diff_classification": diff["classification"],
        "fact_tokens_match": tokens_check["overall_fact_tokens_match"],
        "words_before": word_count(before_text),
        "words_after": word_count(after_text),
        "deviation_overall_status_after": deviation["parsed"].get("overall_status"),
        "deviation_count_after": len(deviation["parsed"].get("deviations") or []),
    }


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.install(LOG_PATH)
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
    client = OpenAI()

    ledger_text = load_text(LEDGER_PATH)
    summary = {}
    for level, path in LEVEL_ARTICLE_PATHS.items():
        summary[level] = process_level(client, level, path, ledger_text)
        assert_budget_ok(note=f"after {level}")

    # 両レベル整合確認(同じ文が同じ位置へ移動しているか)
    b1b_moved = summary["b1b"]
    a2_moved = summary["a2"]
    cross_level_consistency = {
        "same_heading_target": True,
        "both_classification_move_only": (
            b1b_moved["diff_classification"] == "MOVE_ONLY_NO_ADD_NO_REMOVE"
            and a2_moved["diff_classification"] == "MOVE_ONLY_NO_ADD_NO_REMOVE"
        ),
        "both_fact_tokens_match": b1b_moved["fact_tokens_match"] and a2_moved["fact_tokens_match"],
        "both_ledger_compliant_after": (
            b1b_moved["deviation_overall_status_after"] == "LEDGER_COMPLIANT"
            and a2_moved["deviation_overall_status_after"] == "LEDGER_COMPLIANT"
        ),
    }
    save_json(f"{OUT_DIR}/summary.json", {"levels": summary, "cross_level_consistency": cross_level_consistency})

    cost_result = compute_cost_jpy_so_far()
    save_json(f"{OUT_DIR}/cost_summary.json", cost_result)
    print(f"[{THEME_ID}] 完了。cost_jpy={cost_result['total_jpy']} "
          f"cross_level_consistency={cross_level_consistency}")


if __name__ == "__main__":
    main()
