# ============================================================
# er015_news_standard_a2_vocab_effectiveness_trial_01.py
# NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01 (ユーザー指示、2026-09-25)
# ============================================================
# 目的: Standard A2 Prompt v2の「最頻出約2,000語を優先する」という指示が
# 実際にどの程度効いているかを、既存Repo/依存で入手可能な頻度リストで測定する。
# 続けて、プロセスを増やさず単一生成のまま語彙制御を強めたv3 Promptを1本だけ
# 生成しv2と比較する(Validator/再生成の多段構成は入れない)。
#
# 対象記事(下水道のみ、既存Advanced Baseline/v1/v2は一切改変しない):
#   Advanced: er015_output/news_natural_advanced_standard_a2_trial_01/
#             a1_advanced_sewer.md (改変禁止)
#   Standard v1: er015_output/news_natural_advanced_standard_a2_trial_01/
#             a2_standard_sewer.md (改変禁止)
#   Standard v2: er015_output/news_standard_a2_prompt_v2_trial_01/
#             a2v2_standard_sewer.md (改変禁止)
#
# 頻度基準: Repo内・既存.venvに信頼できる頻度リストが無かったため(vocab-ref
# stepでのGlob/Grep/pip show結果はvocab_reference.md参照)、無料公開の
# `wordfreq`(Apache-2.0、pip install、ローカル計算、有料APIではない)を
# 1回だけ新規installし、wordfreq.top_n_list("en", 2000)を採用。
#
# 固定: 1 call(下水道Standard v3のみ)、previous_response_idなし、Web Search
# なし、model=gpt-5.6-luna effort=high、Production Prompt/routing/retry/
# fallback/Audio配線は変更しない。Production実装ではない。追加Variation禁止。
# 費用上限: 累計JPY 100円(--budget-jpyで超過見込みならSTOP、暴走防止目的)。
#
# 依存(いずれも無変更・import再利用のみ):
#   - er015_news_natural_advanced_standard_a2_trial_01 (v1mod):
#       out_path/save_text/save_json/load_text/load_json/install_logger,
#       _sha256_of_file, _strip_title, _level_metrics, _fact_tokens,
#       _call_and_record, vfl01.get_client, er015base._load_pricing,
#       WRITER_MODEL/WRITER_EFFORT
#   - er015_news_standard_a2_prompt_v2_trial_01 (v2mod):
#       DEVELOPER_STD_V2, STANDARD_USER_TEMPLATE_V2, METAPHOR_WORDS,
#       _metaphor_presence
#   - wordfreq (新規pip install、Apache-2.0、無料・ローカル): top_n_list
#
# サブコマンド (--step):
#   vocab-ref     : 頻度基準の探索・採用・保存(frequency_top2000.json,
#                   frequency_lemma_set.json, vocab_reference.md)
#   analyze-v2    : Advanced/Standard v1/Standard v2 の content word測定
#                   (vocab_analysis_v2.json/.md)
#   generate-v3   : v3 Prompt(v2からの差分のみ)で下水道Standard v3を1 call生成
#   compare       : v3のvocab測定・v2 vs v3対照・level_metrics・fact_diff・
#                   structure_map・comparison_sewer_v2_v3.md
#   assemble      : cost.json
# ============================================================
from __future__ import annotations

import argparse
import os
import re
import time

import er015_news_natural_advanced_standard_a2_trial_01 as v1mod
import er015_news_standard_a2_prompt_v2_trial_01 as v2mod

WRITER_MODEL = v1mod.WRITER_MODEL     # "gpt-5.6-luna"
WRITER_EFFORT = v1mod.WRITER_EFFORT   # "high"

# ------------------------------------------------------------
# 入力source path(いずれも改変禁止)
# ------------------------------------------------------------
V1_OUT_DIR = os.path.join("er015_output", "news_natural_advanced_standard_a2_trial_01")
V2_OUT_DIR = os.path.join("er015_output", "news_standard_a2_prompt_v2_trial_01")

SEWER_ADVANCED_PATH = os.path.join(V1_OUT_DIR, "a1_advanced_sewer.md")
SEWER_STANDARD_V1_PATH = os.path.join(V1_OUT_DIR, "a2_standard_sewer.md")
SEWER_STANDARD_V2_PATH = os.path.join(V2_OUT_DIR, "a2v2_standard_sewer.md")

ARTICLE_PATHS = {
    "sewer_advanced": SEWER_ADVANCED_PATH,
    "sewer_standard_v1": SEWER_STANDARD_V1_PATH,
    "sewer_standard_v2": SEWER_STANDARD_V2_PATH,
}


def out_path(out_dir: str, *parts: str) -> str:
    return v1mod.out_path(out_dir, *parts)


def install_logger(out_dir: str) -> None:
    v1mod.install_logger(out_dir)


# ------------------------------------------------------------
# 機能語固定リスト(冠詞/前置詞/代名詞/助動詞/be動詞/接続詞/基本的な
# 数量限定詞・否定語・つなぎ言葉。伝統的な content word (名詞・動詞・
# 形容詞・副詞) / function word の区分に準拠。限界: 境界事例
# [particle動詞の一部(up/out等は前置詞リストに含めた)、"like"(前置詞
# 用法と動詞用法の両方があるが本リストでは常に除外しない=content word
# として残す=保守的に「難語候補」側に倒す)]は vocab_reference.md に記録。
# ------------------------------------------------------------
ARTICLES = {"a", "an", "the"}

PRONOUNS = {
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us",
    "them", "my", "your", "his", "its", "our", "their", "mine", "yours",
    "hers", "ours", "theirs", "this", "that", "these", "those", "who",
    "whom", "whose", "which", "what", "myself", "yourself", "himself",
    "herself", "itself", "ourselves", "yourselves", "themselves", "one",
    "ones", "someone", "something", "anyone", "anything", "everyone",
    "everything", "nothing", "nobody",
}

PREPOSITIONS = {
    "in", "on", "at", "by", "for", "with", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below",
    "to", "from", "up", "down", "of", "off", "over", "under", "again",
    "further", "once", "out", "as", "near", "since", "without", "within",
    "along", "across", "behind", "beyond", "plus", "except", "around",
    "toward", "towards", "upon", "among", "throughout", "despite", "via",
    "per", "instead",
}

AUX_BE = {
    "be", "am", "is", "are", "was", "were", "been", "being", "have",
    "has", "had", "having", "do", "does", "did", "doing", "will",
    "would", "shall", "should", "may", "might", "must", "can", "could",
    "ought", "isn't", "aren't", "wasn't", "weren't", "don't", "doesn't",
    "didn't", "won't", "wouldn't", "couldn't", "shouldn't", "can't",
    "mustn't", "hasn't", "haven't", "hadn't", "it's", "that's",
    "there's", "let's",
}

CONJUNCTIONS = {
    "and", "but", "or", "nor", "so", "yet", "although", "because",
    "since", "unless", "while", "if", "though", "whether", "than",
    "that",
}

QUANTIFIER_DETERMINERS = {
    "some", "any", "all", "every", "each", "both", "either", "neither",
    "several", "much", "many", "few", "other", "another", "same", "own",
    "more", "most", "less", "least", "no",
}

OTHER_FUNCTION = {
    "not", "there", "also", "very", "too", "just", "only", "then",
    "such", "how", "when", "where", "why",
}

FUNCTION_WORDS = (ARTICLES | PRONOUNS | PREPOSITIONS | AUX_BE |
                   CONJUNCTIONS | QUANTIFIER_DETERMINERS | OTHER_FUNCTION)


# ------------------------------------------------------------
# 簡易lemma正規化(標準ライブラリのみ、規則活用のみ対応。限界:
# 不規則動詞[bring->brought等]・不規則複数[child->children等]は
# 非対応。vocab_reference.mdに限界を明記する)
# ------------------------------------------------------------
_KEEP_ER_EST = {
    "water", "other", "under", "over", "after", "never", "number",
    "proper", "paper", "matter", "letter", "winter", "summer", "answer",
    "weather", "quarter", "order", "power", "corner", "member", "enter",
    "master", "monster", "cancer", "chapter", "finger", "gather",
    "interest",
}


def simple_lemma(word: str) -> str:
    w = word.lower().strip("'")
    if not w:
        return w
    if w.endswith("'s"):
        w = w[:-2]
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 3 and w.endswith("ing"):
        stem = w[:-3]
        if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            stem = stem[:-1]
        return stem
    if len(w) > 3 and w.endswith("ed"):
        stem = w[:-2]
        if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            stem = stem[:-1]
        return stem
    if len(w) > 4 and w.endswith("es") and w[:-2].endswith(("s", "x", "z", "ch", "sh")):
        return w[:-2]
    if (len(w) > 3 and w.endswith("s") and not w.endswith("ss")
            and not w.endswith("us") and not w.endswith("is")
            and not w.endswith("'s")):
        return w[:-1]
    if len(w) > 5 and w.endswith("est") and w not in _KEEP_ER_EST:
        return w[:-3]
    if len(w) > 4 and w.endswith("er") and w not in _KEEP_ER_EST:
        return w[:-2]
    return w


def simple_lemma_candidates(word: str) -> list:
    """simple_lemma()の派生。silent-e(damage+d->damaged,消えたeを復元しない
    limitationへの対処)・重子音消去を候補として複数返す。frequency_lemma_set
    との照合はこの候補集合のいずれかが含まれるかで判定する(標準ライブラリの
    みの簡易ヒューリスティック、辞書は使わない)。"""
    w = word.lower().strip("'")
    if not w:
        return [w]
    if w.endswith("'s"):
        w = w[:-2]
    cands = {w, simple_lemma(word)}
    if len(w) > 3 and w.endswith("ing"):
        stem = w[:-3]
        cands.add(stem)
        cands.add(stem + "e")
        if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            cands.add(stem[:-1])
            cands.add(stem[:-1] + "e")
    if len(w) > 3 and w.endswith("ed"):
        stem = w[:-2]
        cands.add(stem)
        cands.add(stem + "e")
        if len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in "aeiou":
            cands.add(stem[:-1])
            cands.add(stem[:-1] + "e")
    return sorted(cands)


def extract_content_words(text: str) -> list:
    """本文(タイトル除く)からcontent word(小文字化)のトークン列を返す。"""
    _, body = v1mod._strip_title(text)
    raw_words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", body)
    content = []
    for w in raw_words:
        lw = w.lower()
        if lw in FUNCTION_WORDS:
            continue
        content.append(w)
    return content


def capitalized_positions(text: str, word_lower: str) -> dict:
    """word_lowerが本文中で先頭大文字/文頭以外で出現したかを調べる
    (固有名詞候補判定の補助、機械ヒューリスティックのみ)。"""
    _, body = v1mod._strip_title(text)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]
    cap_non_initial = 0
    cap_total = 0
    total = 0
    for s in sentences:
        tokens = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", s)
        for idx, t in enumerate(tokens):
            if t.lower() != word_lower:
                continue
            total += 1
            if t[0].isupper():
                cap_total += 1
                if idx != 0:
                    cap_non_initial += 1
    return {"total_occurrences": total, "capitalized_occurrences": cap_total,
            "capitalized_non_sentence_initial": cap_non_initial}


# ------------------------------------------------------------
# STEP: vocab-ref (頻度基準の探索・採用・保存)
# ------------------------------------------------------------
def cmd_vocab_ref(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    import wordfreq
    top2000 = wordfreq.top_n_list("en", 2000)
    v1mod.save_json(out_path(out_dir, "frequency_top2000.json"), {
        "source_package": "wordfreq",
        "source_package_version": "3.1.1",
        "source_url": "https://github.com/rspeer/wordfreq/",
        "license": "Apache-2.0",
        "retrieved": "2026-09-25 (pip install wordfreq, .venv, 新規install)",
        "method": "wordfreq.top_n_list('en', 2000)",
        "note": ("wordfreqはSUBTLEX/Wikipedia/News/Books/Twitter/Reddit/"
                 "OpenSubtitles等の複数コーパス(Exquisite Corpus)を統合した"
                 "頻度データを同梱。コード本体はApache-2.0。個別コーパスの"
                 "利用条件はwordfreqのREADME/該当論文に準拠(本Trialでは"
                 "頻度順位の参照のみに使用し、コーパス原文は取得・再配布"
                 "していない)。"),
        "top_2000_wordforms": top2000,
    })

    lemma_set = sorted(set(simple_lemma(w) for w in top2000))
    v1mod.save_json(out_path(out_dir, "frequency_lemma_set.json"), {
        "method": "simple_lemma() (標準ライブラリのみの規則活用正規化、"
                  "不規則活用は非対応)",
        "source_wordform_count": len(top2000),
        "lemma_count_after_normalization": len(lemma_set),
        "lemma_set": lemma_set,
    })

    ref_md = f"""# vocab_reference.md — 採用した頻度基準(NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01)

## 探索手順と結果

1. Repo内探索: `Glob **/*{{ngsl,NGSL,oxford,gsl,wordlist,word_list,frequency,cefr}}*`
   および `Grep pattern="ngsl|oxford 3000|wordfreq|cefr" -i` を実行。
   ヒットしたファイルはいずれも既存Report/Prompt内の「CEFR」という語句への
   言及のみで、実体を持つ頻度リストファイル・CEFR語彙リストファイルは
   Repo内に存在しなかった。
2. .venv既存依存確認: `pip show wordfreq` / `pip show nltk` / `pip show spacy`
   はいずれも `Package(s) not found`(未導入)。
3. 無料公開の頻度リストを1回だけ新規取得: `pip install wordfreq`
   (PyPI, Apache-2.0ライセンス, ローカル計算・無料、有料APIではない)を実行し
   `wordfreq==3.1.1` を導入。`wordfreq.top_n_list("en", 2000)` で英語の
   頻度上位2,000語形(wordform)を取得した。

## 採用基準

- 「約2,000語圏」= `wordfreq.top_n_list("en", 2000)` が返す上位2,000語形。
- 圏内/圏外の判定は **lemma化した集合同士の比較** で行う: 上位2,000語形を
  `simple_lemma()`(標準ライブラリのみ、複数形/三単現/過去形/-ing/比較級・
  最上級の規則活用のみ簡易正規化)でlemma化し重複除去した集合
  (`frequency_lemma_set.json`、{len(lemma_set)}語)を「頻度圏内」の基準集合
  とする。記事側のcontent wordも同じ`simple_lemma()`でlemma化してから
  この集合に含まれるかを判定する。

## 限界(既知)

- `simple_lemma()`は不規則活用(bring→brought、child→children等)に
  対応していない。該当語は圏外判定になりうる(誤判定リスクとして記録)。
- `wordfreq`の頻度データは複数コーパスの統合値であり、CEFR A2公式語彙
  リスト(例: Cambridge English Profile)そのものではない。「高頻度語」
  であることと「A2レベルとして学習指導要領上適切」であることは同義では
  ない。本Trialでは代替指標として使用する。
- lemma化により2,000語形が{len(lemma_set)}lemmaに縮約されている
  (同一lemmaの活用形が複数含まれるため)。「頻度圏内」の実質カバー範囲は
  語形2,000個より若干狭い可能性がある。
"""
    v1mod.save_text(out_path(out_dir, "vocab_reference.md"), ref_md)
    print(f"[OK] vocab-ref written. top2000 wordforms -> "
          f"{len(lemma_set)} lemmas (frequency_lemma_set.json)")


def _load_lemma_set(out_dir: str) -> set:
    data = v1mod.load_json(out_path(out_dir, "frequency_lemma_set.json"))
    return set(data["lemma_set"])


# ------------------------------------------------------------
# 語彙測定コア(article_key -> vocab measurement dict)
# ------------------------------------------------------------
def _in_scope(word: str, lemma_set: set) -> bool:
    return any(c in lemma_set for c in simple_lemma_candidates(word))


def measure_vocab(text: str, lemma_set: set) -> dict:
    content_tokens = extract_content_words(text)
    token_total = len(content_tokens)
    lemma_pairs = [(w, simple_lemma(w), _in_scope(w, lemma_set)) for w in content_tokens]
    in_scope_tokens = [w for w, lem, ok in lemma_pairs if ok]
    out_scope_tokens = [w for w, lem, ok in lemma_pairs if not ok]

    distinct_lower = sorted(set(w.lower() for w in content_tokens))
    out_scope_distinct = {}
    for w, lem, ok in lemma_pairs:
        if ok:
            continue
        key = w.lower()
        if key not in out_scope_distinct:
            out_scope_distinct[key] = {"surface_examples": set(), "lemma": lem, "count": 0}
        out_scope_distinct[key]["count"] += 1
        out_scope_distinct[key]["surface_examples"].add(w)

    out_scope_list = []
    for key, d in sorted(out_scope_distinct.items(), key=lambda kv: -kv[1]["count"]):
        out_scope_list.append({
            "word": key,
            "lemma": d["lemma"],
            "count": d["count"],
            "surface_forms": sorted(d["surface_examples"]),
        })

    return {
        "content_word_token_total": token_total,
        "content_word_distinct_total": len(distinct_lower),
        "in_scope_token_count": len(in_scope_tokens),
        "out_scope_token_count": len(out_scope_tokens),
        "in_scope_token_ratio": (round(len(in_scope_tokens) / token_total, 4)
                                  if token_total else None),
        "out_scope_distinct_count": len(out_scope_list),
        "out_scope_distinct_ratio": (round(len(out_scope_list) / len(distinct_lower), 4)
                                       if distinct_lower else None),
        "out_scope_words": out_scope_list,
    }


# ------------------------------------------------------------
# STEP: analyze-v2 (Advanced / Standard v1 / Standard v2 のcontent word測定)
# ------------------------------------------------------------
def cmd_analyze_v2(out_dir: str) -> None:
    lemma_set = _load_lemma_set(out_dir)
    result = {}
    for key, path in ARTICLE_PATHS.items():
        text = v1mod.load_text(path)
        result[key] = measure_vocab(text, lemma_set)
    v1mod.save_json(out_path(out_dir, "vocab_analysis_v2.json"), result)

    label = {"sewer_advanced": "下水道 Advanced(改変禁止Baseline)",
              "sewer_standard_v1": "下水道 Standard v1",
              "sewer_standard_v2": "下水道 Standard v2"}
    lines = ["# vocab_analysis_v2.md — content word / 頻度2,000語圏 測定"
             "(Advanced/Standard v1/Standard v2)\n",
             "| 記事 | content word(延べ) | content word(異なり) | "
             "圏内(延べ)割合 | 圏外(異なり)数 | 圏外(異なり)割合 |",
             "|---|---|---|---|---|---|"]
    for key in ["sewer_advanced", "sewer_standard_v1", "sewer_standard_v2"]:
        m = result[key]
        lines.append(f"| {label[key]} | {m['content_word_token_total']} | "
                      f"{m['content_word_distinct_total']} | "
                      f"{m['in_scope_token_ratio']} | "
                      f"{m['out_scope_distinct_count']} | "
                      f"{m['out_scope_distinct_ratio']} |")

    lines.append("\n## 実効性評価(Advanced比、圏外[異なり語]の減少)\n")
    adv_out = result["sewer_advanced"]["out_scope_distinct_count"]
    v1_out = result["sewer_standard_v1"]["out_scope_distinct_count"]
    v2_out = result["sewer_standard_v2"]["out_scope_distinct_count"]
    adv_out_tok = result["sewer_advanced"]["out_scope_token_count"]
    v1_out_tok = result["sewer_standard_v1"]["out_scope_token_count"]
    v2_out_tok = result["sewer_standard_v2"]["out_scope_token_count"]
    lines.append(f"- 圏外(異なり語)数: Advanced {adv_out} -> v1 {v1_out} "
                  f"(-{adv_out - v1_out}) -> v2 {v2_out} "
                  f"(Advanced比 -{adv_out - v2_out})")
    lines.append(f"- 圏外(延べ語)数: Advanced {adv_out_tok} -> v1 {v1_out_tok} "
                  f"(-{adv_out_tok - v1_out_tok}) -> v2 {v2_out_tok} "
                  f"(Advanced比 -{adv_out_tok - v2_out_tok})")

    for key in ["sewer_advanced", "sewer_standard_v1", "sewer_standard_v2"]:
        lines.append(f"\n## {label[key]} 圏外語一覧(異なり語、出現回数順)\n")
        lines.append("| 語 | lemma | 出現回数 | 表層形 |")
        lines.append("|---|---|---|---|")
        for w in result[key]["out_scope_words"]:
            lines.append(f"| {w['word']} | {w['lemma']} | {w['count']} | "
                          f"{', '.join(w['surface_forms'])} |")

    v1mod.save_text(out_path(out_dir, "vocab_analysis_v2.md"), "\n".join(lines))
    print(f"[OK] vocab_analysis_v2.json/.md written. "
          f"v2 out_scope_distinct={v2_out} (Advanced {adv_out}, v1 {v1_out})")
    return result


# ------------------------------------------------------------
# v3 Prompt(v2からの差分のみ、ユーザー逐語指定の2行->5行置換。
# developerはv2と一字も変えない)
# ------------------------------------------------------------
DEVELOPER_STD_V3 = v2mod.DEVELOPER_STD_V2  # v2と同一(一字も変えない)

_V2_TWO_LINES = (
    "Prefer common, high-frequency English words (roughly the 2,000 most "
    "common words).\n"
    "Keep harder words only when they are necessary to understand the "
    "topic (for example, a technical term or a name). Do not add an "
    "explanation for a hard word; make the sentences around it simple "
    "instead."
)

_V3_FIVE_LINES = (
    "Use common, everyday words whenever a simpler word can express the "
    "same meaning.\n"
    "Do not keep a difficult word just because it appears in the "
    "original article.\n"
    "Keep a word above A2 level only if replacing it would lose an "
    "important fact or meaning (for example, a name, or a technical "
    "term with no simple equivalent).\n"
    "Do not add an explanation for a hard word; make the sentence "
    "around it simple instead.\n"
    "Before you finish, check every difficult word in your draft and "
    "replace each non-essential one with simpler English."
)

assert _V2_TWO_LINES in v2mod.STANDARD_USER_TEMPLATE_V2, (
    "v2 template内に置換対象の2行が見つからない(逐語不一致)")

STANDARD_USER_TEMPLATE_V3 = v2mod.STANDARD_USER_TEMPLATE_V2.replace(
    _V2_TWO_LINES, _V3_FIVE_LINES)

assert STANDARD_USER_TEMPLATE_V3 != v2mod.STANDARD_USER_TEMPLATE_V2
# それ以外の本文が一字も変わっていないことの機械確認(該当2行を除いた
# 残り全文が完全一致するか)
_v2_rest = v2mod.STANDARD_USER_TEMPLATE_V2.replace(_V2_TWO_LINES, "")
_v3_rest = STANDARD_USER_TEMPLATE_V3.replace(_V3_FIVE_LINES, "")
assert _v2_rest == _v3_rest, "v2/v3で置換対象以外の本文に差異がある"


# ------------------------------------------------------------
# STEP: generate-v3 (下水道Advanced -> v3 Prompt -> 1 call)
# ------------------------------------------------------------
def cmd_generate_v3(out_dir: str, budget_jpy: float, force: bool) -> None:
    os.makedirs(out_dir, exist_ok=True)
    sewer_advanced_text = v1mod.load_text(SEWER_ADVANCED_PATH)

    v1mod.save_text(
        out_path(out_dir, "prompt_standard_v3.txt"),
        "DEVELOPER:\n" + DEVELOPER_STD_V3 + "\n\n"
        "USER TEMPLATE ({advanced_article} is substituted):\n" +
        STANDARD_USER_TEMPLATE_V3)

    diff_md = (
        "# prompt_diff_v2_v3.md — Standard Prompt v2 -> v3 差分(語彙制御強化のみ)\n\n"
        "developerはv2と一字も変えていない。変更したのはuser template内の"
        "次の2行のみで、それ以外の本文(段落順・改行含む)は一字も変えていない"
        "(機械assertで確認済み)。\n\n"
        "## v2の該当2行(置換対象、逐語)\n\n```\n" + _V2_TWO_LINES + "\n```\n\n"
        "## v3の置換後5行(逐語)\n\n```\n" + _V3_FIVE_LINES + "\n```\n\n"
        "## v2 developer(逐語、v3と同一文)\n\n```\n" + DEVELOPER_STD_V3 + "\n```\n\n"
        "## v3 user template全文(逐語)\n\n```\n" + STANDARD_USER_TEMPLATE_V3 + "\n```\n\n"
        "## 変更意図\n\n"
        "- v2の「roughly the 2,000 most common words」という数値目標の提示は、"
        "モデルに具体的な語彙判定手段を与えないため、実効性が弱い可能性がある"
        "(analyze-v2のvocab_analysis_v2.mdで圏外語が実測された)。\n"
        "- v3では「圏外語だから難しい」ではなく「簡単な語で同じ意味を表せる"
        "なら簡単な語を使う」という判断基準そのものを明示し、\"Do not keep a "
        "difficult word just because it appears in the original article.\"で"
        "Advanced由来の語をそのまま残す慣性を明示的に禁止した。\n"
        "- 「必要性の基準」を「事実・意味を失う場合のみ難語を残す」に絞り、"
        "最後に難語を見直す self-check 手順(\"Before you finish, check "
        "every difficult word...\")を追加した。\n"
        "- 追加した行数は3行(2行->5行)。Promptを過剰に長くしないため、"
        "既存のmetaphor保持指示・Story保持指示・Fact保持指示には触れていない。\n"
    )
    v1mod.save_text(out_path(out_dir, "prompt_diff_v2_v3.md"), diff_md)

    install_logger(out_dir)
    client = v1mod.vfl01.get_client()
    pricing = v1mod.er015base._load_pricing()

    a2v3_user = STANDARD_USER_TEMPLATE_V3.format(advanced_article=sewer_advanced_text)
    a2v3_output = out_path(out_dir, "a2v3_standard_sewer.md")
    a2v3_meta = out_path(out_dir, "a2v3_standard_sewer.meta.json")
    m = v1mod._call_and_record(client, pricing, DEVELOPER_STD_V3, a2v3_user,
                                "a2v3_standard_sewer", a2v3_output, a2v3_meta, force)
    total_jpy = m.get("cost_jpy", 0.0)
    if total_jpy > budget_jpy:
        stop = {"stop_reason": "budget exceeded after sewer v3 call",
                "total_jpy": total_jpy, "budget_jpy": budget_jpy}
        v1mod.save_json(out_path(out_dir, "stop_reason.json"), stop)
        print(f"[STOP] budget exceeded after sewer v3: {total_jpy} > {budget_jpy}")
        raise SystemExit(1)

    print(f"[DONE] generate-v3 complete. cost_jpy={round(total_jpy, 4)} "
          f"budget_jpy={budget_jpy}")


# ------------------------------------------------------------
# STEP: compare (v3 vocab測定 / v2 vs v3対照 / level_metrics / fact_diff /
# structure_map / comparison_sewer_v2_v3.md)
# ------------------------------------------------------------
def cmd_compare_vocab(out_dir: str) -> dict:
    lemma_set = _load_lemma_set(out_dir)
    v3_path = out_path(out_dir, "a2v3_standard_sewer.md")
    text = v1mod.load_text(v3_path)
    result = {"sewer_standard_v3": measure_vocab(text, lemma_set)}
    v1mod.save_json(out_path(out_dir, "vocab_analysis_v3.json"), result)

    v2_result = v1mod.load_json(out_path(out_dir, "vocab_analysis_v2.json"))
    v2_out_words = {w["word"]: w for w in v2_result["sewer_standard_v2"]["out_scope_words"]}
    v3_out_words = {w["word"]: w for w in result["sewer_standard_v3"]["out_scope_words"]}

    disappeared = sorted(set(v2_out_words) - set(v3_out_words))
    remained = sorted(set(v2_out_words) & set(v3_out_words))
    new_in_v3 = sorted(set(v3_out_words) - set(v2_out_words))

    lines = ["# vocab_analysis_v3.md — v3 content word測定 + v2 vs v3対照\n",
             "| 記事 | content word(延べ) | content word(異なり) | "
             "圏内(延べ)割合 | 圏外(異なり)数 | 圏外(異なり)割合 |",
             "|---|---|---|---|---|---|"]
    v3m = result["sewer_standard_v3"]
    v2m = v2_result["sewer_standard_v2"]
    lines.append(f"| 下水道 Standard v2 | {v2m['content_word_token_total']} | "
                  f"{v2m['content_word_distinct_total']} | "
                  f"{v2m['in_scope_token_ratio']} | "
                  f"{v2m['out_scope_distinct_count']} | "
                  f"{v2m['out_scope_distinct_ratio']} |")
    lines.append(f"| 下水道 Standard v3 | {v3m['content_word_token_total']} | "
                  f"{v3m['content_word_distinct_total']} | "
                  f"{v3m['in_scope_token_ratio']} | "
                  f"{v3m['out_scope_distinct_count']} | "
                  f"{v3m['out_scope_distinct_ratio']} |")

    lines.append(f"\n## v2 vs v3 圏外語対照(異なり語ベース)\n")
    lines.append(f"- v2圏外 {len(v2_out_words)}語 -> v3圏外 {len(v3_out_words)}語 "
                  f"({len(v2_out_words) - len(v3_out_words):+d})")
    lines.append(f"- 消えた語(v2圏外→v3圏内 or 未使用): {len(disappeared)}語")
    lines.append(f"- 残った語(v2/v3とも圏外): {len(remained)}語")
    lines.append(f"- 新たに出た語(v3のみ圏外): {len(new_in_v3)}語")

    lines.append("\n### 消えた語\n")
    lines.append(", ".join(disappeared) if disappeared else "(なし)")
    lines.append("\n### 残った語(出現回数付き、v3側)\n")
    if remained:
        for w in remained:
            lines.append(f"- {w} (v2:{v2_out_words[w]['count']}回, "
                          f"v3:{v3_out_words[w]['count']}回)")
    else:
        lines.append("(なし)")
    lines.append("\n### 新たに出た語(v3のみ、出現回数付き)\n")
    if new_in_v3:
        for w in new_in_v3:
            lines.append(f"- {w} (v3:{v3_out_words[w]['count']}回)")
    else:
        lines.append("(なし)")

    lines.append("\n## v3圏外語一覧(異なり語、出現回数順)\n")
    lines.append("| 語 | lemma | 出現回数 | 表層形 |")
    lines.append("|---|---|---|---|")
    for w in v3m["out_scope_words"]:
        lines.append(f"| {w['word']} | {w['lemma']} | {w['count']} | "
                      f"{', '.join(w['surface_forms'])} |")

    v1mod.save_text(out_path(out_dir, "vocab_analysis_v3.md"), "\n".join(lines))
    print(f"[OK] vocab_analysis_v3.json/.md written. v3 out_scope_distinct="
          f"{v3m['out_scope_distinct_count']} (v2 {v2m['out_scope_distinct_count']}); "
          f"disappeared={len(disappeared)} remained={len(remained)} new={len(new_in_v3)}")
    return {"disappeared": disappeared, "remained": remained, "new_in_v3": new_in_v3}


def cmd_compare_levels(out_dir: str) -> dict:
    files = {
        "sewer_advanced": SEWER_ADVANCED_PATH,
        "sewer_standard_v1": SEWER_STANDARD_V1_PATH,
        "sewer_standard_v2": SEWER_STANDARD_V2_PATH,
        "sewer_standard_v3": out_path(out_dir, "a2v3_standard_sewer.md"),
    }
    metrics = {}
    for key, path in files.items():
        text = v1mod.load_text(path)
        metrics[key] = v1mod._level_metrics(text)
    v1mod.save_json(out_path(out_dir, "level_metrics.json"), metrics)

    label_map = {
        "sewer_advanced": "下水道 Advanced",
        "sewer_standard_v1": "下水道 Standard v1",
        "sewer_standard_v2": "下水道 Standard v2",
        "sewer_standard_v3": "下水道 Standard v3",
    }
    md_lines = ["# level_metrics.md — Level比較(下水道4段階、参考値、機械判定は"
                "最終判断に用いない)\n",
                "| 記事 | words | sentences | avg words/sent | avg syll/word | "
                "long-sent(>=20w)率 | subordinator/100w | FK grade(heuristic) |",
                "|---|---|---|---|---|---|---|---|"]
    for key in ["sewer_advanced", "sewer_standard_v1", "sewer_standard_v2", "sewer_standard_v3"]:
        m = metrics[key]
        md_lines.append(
            f"| {label_map[key]} | {m['word_count']} | {m['sentence_count']} | "
            f"{m['avg_sentence_length_words']} | {m['avg_syllables_per_word_heuristic']} | "
            f"{m['long_sentence_ratio_ge20words']} | {m['subordinators_per_100_words']} | "
            f"{m['flesch_kincaid_grade_heuristic']} |")
    adv_avg = metrics["sewer_advanced"]["avg_sentence_length_words"]
    v1_avg = metrics["sewer_standard_v1"]["avg_sentence_length_words"]
    v2_avg = metrics["sewer_standard_v2"]["avg_sentence_length_words"]
    v3_avg = metrics["sewer_standard_v3"]["avg_sentence_length_words"]
    md_lines.append(f"\n## 平均語/文の変化(参考)\n")
    md_lines.append(f"- Advanced {adv_avg} -> v1 {v1_avg} -> v2 {v2_avg} -> v3 {v3_avg} "
                     f"(v2比 {round(v3_avg - v2_avg, 2):+.2f}語、"
                     f"9〜11語/文目標との差: {round(v3_avg - 10, 2):+.2f})")
    v1mod.save_text(out_path(out_dir, "level_metrics.md"), "\n".join(md_lines))
    print("[OK] level_metrics.json / level_metrics.md written (4 articles)")
    return metrics


def cmd_compare_fact_diff(out_dir: str) -> dict:
    adv_path = SEWER_ADVANCED_PATH
    v3_path = out_path(out_dir, "a2v3_standard_sewer.md")
    adv = v1mod._fact_tokens(v1mod.load_text(adv_path))
    v3 = v1mod._fact_tokens(v1mod.load_text(v3_path))
    result = {
        "advanced_to_v3": {
            "advanced": adv,
            "v3": v3,
            "numbers_missing_in_v3": sorted(set(adv["numbers"]) - set(v3["numbers"])),
            "numbers_added_in_v3": sorted(set(v3["numbers"]) - set(adv["numbers"])),
            "proper_nouns_missing_in_v3": sorted(set(adv["proper_nouns"]) - set(v3["proper_nouns"])),
            "proper_nouns_added_in_v3": sorted(set(v3["proper_nouns"]) - set(adv["proper_nouns"])),
        }
    }
    v1mod.save_json(out_path(out_dir, "fact_diff_machine.json"), result)
    print("[OK] fact_diff_machine.json written (advanced_to_v3)")
    return result


def cmd_compare_structure_map(out_dir: str) -> None:
    sewer_adv = v1mod.load_text(SEWER_ADVANCED_PATH)
    sewer_v1 = v1mod.load_text(SEWER_STANDARD_V1_PATH)
    sewer_v2 = v1mod.load_text(SEWER_STANDARD_V2_PATH)
    sewer_v3 = v1mod.load_text(out_path(out_dir, "a2v3_standard_sewer.md"))

    def para_count(text: str) -> int:
        _, body = v1mod._strip_title(text)
        return len([p for p in body.split("\n\n") if p.strip()])

    lines = ["# structure_map.md — 段落対応・Reveal/比喩/Ending保持確認"
             "・比喩語保持有無(下水道4段階)\n"]
    lines.append("## 段落数対応\n")
    lines.append(f"- Advanced {para_count(sewer_adv)}段落 / v1 {para_count(sewer_v1)}段落 "
                  f"/ v2 {para_count(sewer_v2)}段落 / v3 {para_count(sewer_v3)}段落")

    lines.append("\n## 比喩語保持有無(語単位、大小無視の部分一致、"
                  "v2mod.METAPHOR_WORDSをそのまま再利用)\n")
    lines.append("| 語 | Advanced | v1 | v2 | v3 |")
    lines.append("|---|---|---|---|---|")
    sets = {
        "adv": v2mod._metaphor_presence(sewer_adv),
        "v1": v2mod._metaphor_presence(sewer_v1),
        "v2": v2mod._metaphor_presence(sewer_v2),
        "v3": v2mod._metaphor_presence(sewer_v3),
    }
    for w in v2mod.METAPHOR_WORDS:
        row = [w]
        for key in ["adv", "v1", "v2", "v3"]:
            row.append("○" if sets[key].get(w) else "-")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("\n## Reveal / 比喩表現の文体 / Ending 位置(手動確認、○×)\n")
    v3_lower = sewer_v3.lower()
    reveal_ok = ("combined septic tank" in v3_lower and
                 "small water-treatment" in v3_lower)
    metaphor_marker_ok = ("like a hidden main artery" in v3_lower or
                           "is like" in v3_lower) and "washing machine" in v3_lower
    ending_ok = "surprisingly familiar place" in v3_lower
    lines.append(f"- Reveal(下水道→合併浄化槽への切り替え説明段落): "
                  f"{'○' if reveal_ok else '×(要確認)'}")
    lines.append(f"- 中心比喩(main artery / washing machineが直喩[like/as]"
                  f"のまま保持され、事実文化していないか): "
                  f"{'○' if metaphor_marker_ok else '×(要確認、本文参照)'}")
    lines.append(f"- Ending logic(\"surprisingly familiar place\"の結び): "
                  f"{'○' if ending_ok else '×(要確認)'}")

    v1mod.save_text(out_path(out_dir, "structure_map.md"), "\n".join(lines))
    print(f"[OK] structure_map.md written. reveal={reveal_ok} "
          f"metaphor_marker={metaphor_marker_ok} ending={ending_ok}")


def cmd_compare_comparison_md(out_dir: str) -> None:
    sewer_adv = v1mod.load_text(SEWER_ADVANCED_PATH)
    sewer_v2 = v1mod.load_text(SEWER_STANDARD_V2_PATH)
    sewer_v3 = v1mod.load_text(out_path(out_dir, "a2v3_standard_sewer.md"))
    md = (
        "# comparison_sewer_v2_v3.md — 下水道: Advanced -> Standard v2 -> Standard v3\n\n"
        "## Advanced (改変禁止Baseline)\n\n" + sewer_adv + "\n\n---\n\n"
        "## Standard v2 (NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01)\n\n" + sewer_v2 + "\n\n---\n\n"
        "## Standard v3 (NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01)\n\n" + sewer_v3 + "\n"
    )
    v1mod.save_text(out_path(out_dir, "comparison_sewer_v2_v3.md"), md)
    print("[OK] comparison_sewer_v2_v3.md written")


def cmd_compare(out_dir: str) -> None:
    cmd_compare_vocab(out_dir)
    cmd_compare_levels(out_dir)
    cmd_compare_fact_diff(out_dir)
    cmd_compare_structure_map(out_dir)
    cmd_compare_comparison_md(out_dir)


# ------------------------------------------------------------
# STEP: assemble (cost.json)
# ------------------------------------------------------------
def cmd_assemble(out_dir: str) -> None:
    meta_path = out_path(out_dir, "a2v3_standard_sewer.meta.json")
    calls = []
    total_jpy = 0.0
    if os.path.exists(meta_path):
        m = v1mod.load_json(meta_path)
        calls.append(m)
        total_jpy += m.get("cost_jpy", 0.0)
    else:
        print(f"[WARN] missing meta: {meta_path}")
    cost = {
        "calls": calls,
        "total_cost_jpy": round(total_jpy, 4),
        "budget_jpy": 100,
        "within_budget": total_jpy <= 100,
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
                     choices=["vocab-ref", "analyze-v2", "generate-v3",
                              "compare", "assemble"])
    ap.add_argument("--budget-jpy", type=float, default=100.0)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.step == "vocab-ref":
        cmd_vocab_ref(args.out_dir)
    elif args.step == "analyze-v2":
        cmd_analyze_v2(args.out_dir)
    elif args.step == "generate-v3":
        cmd_generate_v3(args.out_dir, args.budget_jpy, args.force)
    elif args.step == "compare":
        cmd_compare(args.out_dir)
    elif args.step == "assemble":
        cmd_assemble(args.out_dir)


if __name__ == "__main__":
    main()
