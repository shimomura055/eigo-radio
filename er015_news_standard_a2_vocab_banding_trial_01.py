# ============================================================
# er015_news_standard_a2_vocab_banding_trial_01.py
# NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01 (ユーザー指示、2026-09-25)
# ============================================================
# 目的: Standard A2の語彙簡略化を「最頻出2,000語を優先」という単一の
# しきい値ではなく、頻度帯(A/B/C/D)によって扱いを変える設計にし、
# あわせて「無理な置換で不自然になるなら自然さを優先してよい」という
# 思想をPromptに追加する。追加LLM call・新Validator・新QA工程・再生成は
# 追加しない(Meta記事から1 callのみ)。Sewer v3(既存Trial成果物、改変
# 禁止)とのクロストピック比較を行う。
#
# 対象記事:
#   Sewer v3 (改変禁止、既存Trial成果物):
#     er015_output/news_standard_a2_vocab_effectiveness_trial_01/
#     a2v3_standard_sewer.md
#   Meta Advanced Baseline (改変禁止、APPROVED_FOR_PRODUCTION配線未完了):
#     er015_output/news_ja_to_en_adaptation_trial_01/arms/arm3/output.md
#     (sha256は er015_output/news_natural_advanced_standard_a2_trial_01/
#     sources.json の meta_advanced_baseline と照合)
#   Meta Standard v1 (B-1, 参考のみ、改変禁止):
#     er015_output/news_natural_advanced_standard_a2_trial_01/
#     b1_standard_meta.md
#
# 頻度帯: wordfreq.top_n_list("en", 20000) (前Trialで新規installした
# 依存を再利用、追加installなし)からlemma単位の順位表を作り、
#   A: 順位 <= 3,000
#   B: 3,001 <= 順位 <= 5,000
#   C: 5,001 <= 順位 <= 10,000
#   D: 順位 > 10,000 (表外=20,000超も含めてこの帯にまとめる)
# として各content wordに割り当てる。記事内で文頭以外に大文字表記される
# 語(Meta/Muse/Reuters等の固有名詞候補、機械ヒューリスティック)は帯とは
# 別枠のproper_nounバケツに分離する(既知の限界: 全て大文字の略語
# [AI等]も同じ判定になり得る)。
#
# 固定: 1 call(Meta Standard v4のみ)、previous_response_idなし、
# Web Searchなし、model=gpt-5.6-luna effort=high、Production Prompt/
# routing/retry/fallback/Audio配線は変更しない。Production実装ではない。
# 追加Variation禁止(v4候補1本のみ)。費用上限: 累計JPY 100円
# (--budget-jpyで超過見込みならSTOP、暴走防止目的)。
#
# 依存(いずれも無変更・import再利用のみ):
#   - er015_news_standard_a2_vocab_effectiveness_trial_01 (v3mod):
#       v1mod/v2mod へのアクセス、extract_content_words,
#       simple_lemma, simple_lemma_candidates, capitalized_positions,
#       FUNCTION_WORDS, measure_vocab, DEVELOPER_STD_V3,
#       STANDARD_USER_TEMPLATE_V3, _V3_FIVE_LINES
#   - er015_news_natural_advanced_standard_a2_trial_01 (v1mod, v3mod経由):
#       out_path/save_text/save_json/load_text/load_json/install_logger,
#       _sha256_of_file, _strip_title, _level_metrics, _fact_tokens,
#       _call_and_record, vfl01.get_client, er015base._load_pricing,
#       WRITER_MODEL/WRITER_EFFORT
#   - er015_news_standard_a2_prompt_v2_trial_01 (v2mod, v3mod経由):
#       METAPHOR_WORDS, _metaphor_presence
#   - wordfreq (既存installを再利用、追加installなし): top_n_list
#
# サブコマンド (--step):
#   bands-baseline : 頻度帯ルックアップの構築 + Sewer v3 / Meta Advanced
#                    Baseline の帯別測定(Meta v4は未生成のため対象外)
#   generate-v4    : v4 Prompt(v3の5行を7行に置換)でMeta Standard v4を
#                    1 call生成
#   evaluate       : Meta v4の帯別測定 + Meta Advanced->v4差分 +
#                    level_metrics + fact_diff + structure_map +
#                    comparison_meta_v4.md + comparison_sewer_v3_meta_v4.md
#   assemble       : cost.json
# ============================================================
from __future__ import annotations

import argparse
import os

import er015_news_standard_a2_vocab_effectiveness_trial_01 as v3mod

v1mod = v3mod.v1mod
v2mod = v3mod.v2mod

WRITER_MODEL = v3mod.WRITER_MODEL     # "gpt-5.6-luna"
WRITER_EFFORT = v3mod.WRITER_EFFORT   # "high"

# ------------------------------------------------------------
# 入力source path(いずれも改変禁止)
# ------------------------------------------------------------
V3_OUT_DIR = os.path.join("er015_output", "news_standard_a2_vocab_effectiveness_trial_01")
V1_OUT_DIR = os.path.join("er015_output", "news_natural_advanced_standard_a2_trial_01")
META_ADAPT_OUT_DIR = os.path.join("er015_output", "news_ja_to_en_adaptation_trial_01")

SEWER_V3_PATH = os.path.join(V3_OUT_DIR, "a2v3_standard_sewer.md")
META_ADVANCED_PATH = os.path.join(META_ADAPT_OUT_DIR, "arms", "arm3", "output.md")
META_STANDARD_V1_PATH = os.path.join(V1_OUT_DIR, "b1_standard_meta.md")
SOURCES_JSON_PATH = os.path.join(V1_OUT_DIR, "sources.json")

BASELINE_ARTICLE_PATHS = {
    "sewer_standard_v3": SEWER_V3_PATH,
    "meta_advanced_baseline": META_ADVANCED_PATH,
}

# ------------------------------------------------------------
# 追加(修正2回目、ユーザー承認): Sewer記事へv4を適用するための入力path
# 既存のMeta処理(上記まで)は一字も変更していない。以下はすべて追加のみ。
# SEWER_ADVANCED_PATHはv3mod(既存Trial)で定義済みの値をそのまま再利用
# (改変禁止の入力なので新規に定義しない)。
# ------------------------------------------------------------
SEWER_ADVANCED_PATH = v3mod.SEWER_ADVANCED_PATH

BAND_EDGES = [("A", 3000), ("B", 5000), ("C", 10000)]  # D = >10000 (残り)


def out_path(out_dir: str, *parts: str) -> str:
    return v1mod.out_path(out_dir, *parts)


def install_logger(out_dir: str) -> None:
    v1mod.install_logger(out_dir)


# ------------------------------------------------------------
# STEP: sha256照合(Meta Advanced Baselineのみ。Sewer v3は既存Trial
# 成果物をそのままpathで参照するため照合対象は元記事のみ)
# ------------------------------------------------------------
def _verify_meta_advanced_sha256() -> str:
    sources = v1mod.load_json(SOURCES_JSON_PATH)
    expected = sources["meta_advanced_baseline"]["sha256"]
    actual = v1mod._sha256_of_file(META_ADVANCED_PATH)
    if actual != expected:
        raise SystemExit(
            f"[STOP] meta_advanced_baseline sha256 mismatch: "
            f"expected={expected} actual={actual}")
    return actual


# ------------------------------------------------------------
# 頻度帯ルックアップ(lemma -> 最小順位)の構築
# ------------------------------------------------------------
def _build_lemma_rank_map(wordlist: list) -> dict:
    rank_map = {}
    for idx, w in enumerate(wordlist, start=1):
        lem = v3mod.simple_lemma(w)
        if lem not in rank_map:
            rank_map[lem] = idx
    return rank_map


def _band_of_rank(rank: int) -> str:
    for label, ceiling in BAND_EDGES:
        if rank <= ceiling:
            return label
    return "D"


def _word_band(word: str, rank_map: dict):
    """word (surface form) の帯とその根拠rank(見つからなければNone)を返す。"""
    candidates = v3mod.simple_lemma_candidates(word)
    ranks = [rank_map[c] for c in candidates if c in rank_map]
    if not ranks:
        return "D", None
    best = min(ranks)
    return _band_of_rank(best), best


# ------------------------------------------------------------
# 記事1本の帯別測定(proper noun別枠)
# ------------------------------------------------------------
def measure_bands(text: str, rank_map: dict) -> dict:
    content_tokens = v3mod.extract_content_words(text)
    token_total = len(content_tokens)

    distinct_lower = sorted(set(w.lower() for w in content_tokens))
    per_word = {}
    for w in distinct_lower:
        cap_info = v3mod.capitalized_positions(text, w)
        is_proper = cap_info["capitalized_non_sentence_initial"] > 0
        if is_proper:
            per_word[w] = {"bucket": "proper_noun", "rank": None,
                            "capitalized_info": cap_info}
        else:
            band, rank = _word_band(w, rank_map)
            per_word[w] = {"bucket": band, "rank": rank}

    bucket_counts_token = {"A": 0, "B": 0, "C": 0, "D": 0, "proper_noun": 0}
    bucket_words = {"A": [], "B": [], "C": [], "D": [], "proper_noun": []}
    for tok in content_tokens:
        key = tok.lower()
        bucket = per_word[key]["bucket"]
        bucket_counts_token[bucket] += 1

    for key, info in per_word.items():
        entry = {"word": key, "rank": info.get("rank"),
                  "count": sum(1 for t in content_tokens if t.lower() == key)}
        bucket_words[info["bucket"]].append(entry)
    for bucket in bucket_words:
        bucket_words[bucket].sort(key=lambda d: -d["count"])

    return {
        "content_word_token_total": token_total,
        "content_word_distinct_total": len(distinct_lower),
        "bucket_token_counts": bucket_counts_token,
        "bucket_distinct_counts": {k: len(v) for k, v in bucket_words.items()},
        "bucket_words": bucket_words,
    }


def _bands_md_table(label: str, m: dict) -> list:
    lines = [f"### {label}\n",
             "| 帯 | 異なり語数 | 延べ語数 |",
             "|---|---|---|"]
    for b in ["A", "B", "C", "D", "proper_noun"]:
        lines.append(f"| {b} | {m['bucket_distinct_counts'][b]} | "
                      f"{m['bucket_token_counts'][b]} |")
    lines.append(f"\ncontent word 延べ={m['content_word_token_total']} "
                 f"異なり={m['content_word_distinct_total']}\n")
    for b in ["A", "B", "C", "D", "proper_noun"]:
        words = m["bucket_words"][b]
        if not words:
            continue
        lines.append(f"\n#### {label} — 帯{b}語一覧(異なり語、出現回数順)\n")
        lines.append("| 語 | 頻度順位(lemma最小) | 出現回数 |")
        lines.append("|---|---|---|")
        for w in words:
            lines.append(f"| {w['word']} | {w['rank']} | {w['count']} |")
    return lines


# ------------------------------------------------------------
# STEP: bands-baseline
# ------------------------------------------------------------
def cmd_bands_baseline(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    meta_sha = _verify_meta_advanced_sha256()

    import wordfreq
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_map = _build_lemma_rank_map(top20000)

    v1mod.save_json(out_path(out_dir, "frequency_rank_top20000.json"), {
        "source_package": "wordfreq",
        "source_package_version": "3.1.1",
        "license": "Apache-2.0",
        "retrieved": ("既存install再利用(NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-"
                      "TRIAL-01で新規pip installしたもの。本Trialでは追加install"
                      "なし)"),
        "method": "wordfreq.top_n_list('en', 20000)",
        "band_edges": {"A": "rank<=3000", "B": "3001<=rank<=5000",
                        "C": "5001<=rank<=10000",
                        "D": "rank>10000 (表外=20,000超を含む)"},
        "lemma_rank_map_size": len(rank_map),
        "note": ("順位はlemma単位(simple_lemma()による規則活用正規化のみ、"
                 "不規則活用は非対応)の最小順位(=最も高頻度な活用形の順位)"
                 "を採用。simple_lemma_candidates()による複数候補のいずれかが"
                 "rank_mapに存在すればその最小値を使う。"),
    })

    result = {}
    for key, path in BASELINE_ARTICLE_PATHS.items():
        text = v1mod.load_text(path)
        result[key] = measure_bands(text, rank_map)
    v1mod.save_json(out_path(out_dir, "vocab_bands_baseline.json"), result)

    lines = ["# vocab_bands_baseline.md — 頻度帯別測定(Sewer v3 / Meta Advanced "
             "Baseline、Meta v4は未生成のため本stepでは対象外)\n",
             f"Meta Advanced Baseline sha256照合: 一致 ({meta_sha[:16]}...)\n"]
    lines += _bands_md_table("Sewer Standard v3", result["sewer_standard_v3"])
    lines += _bands_md_table("Meta Advanced Baseline", result["meta_advanced_baseline"])
    v1mod.save_text(out_path(out_dir, "vocab_bands_baseline.md"), "\n".join(lines))

    print(f"[OK] bands-baseline written. sewer_v3 D(distinct)="
          f"{result['sewer_standard_v3']['bucket_distinct_counts']['D']} "
          f"meta_advanced D(distinct)="
          f"{result['meta_advanced_baseline']['bucket_distinct_counts']['D']}")


# ------------------------------------------------------------
# v4 Prompt(v3の5行 -> 7行に置換。developer・他の行は一字も変えない)
# ------------------------------------------------------------
DEVELOPER_STD_V4 = v3mod.DEVELOPER_STD_V3  # v3と同一(一字も変えない)

_V4_SEVEN_LINES = (
    "Use common, everyday words whenever a simpler word can express the "
    "same meaning.\n"
    "Do not keep a difficult word just because it appears in the "
    "original article.\n"
    "Think about how common a word is: very common words are fine; "
    "fairly common words may stay if they sound natural; uncommon words "
    "should usually be replaced when a clearly simpler natural choice "
    "exists; rare words should be replaced unless they are names, "
    "essential technical terms, or a key metaphor.\n"
    "Do not replace a difficult word if the replacement sounds less "
    "natural or is not clearly easier. Prefer natural, simple English "
    "over forced simplification.\n"
    "When simplifying vocabulary, prefer a common natural phrase over "
    "an awkward one-word replacement.\n"
    "Do not add an explanation for a hard word; make the sentence "
    "around it simple instead.\n"
    "Before you finish, check every difficult word in your draft. "
    "Replace it only if a clearly simpler and natural choice exists."
)

assert v3mod._V3_FIVE_LINES in v3mod.STANDARD_USER_TEMPLATE_V3, (
    "v3 template内に置換対象の5行が見つからない(逐語不一致)")

STANDARD_USER_TEMPLATE_V4 = v3mod.STANDARD_USER_TEMPLATE_V3.replace(
    v3mod._V3_FIVE_LINES, _V4_SEVEN_LINES)

assert STANDARD_USER_TEMPLATE_V4 != v3mod.STANDARD_USER_TEMPLATE_V3
_v3_rest = v3mod.STANDARD_USER_TEMPLATE_V3.replace(v3mod._V3_FIVE_LINES, "")
_v4_rest = STANDARD_USER_TEMPLATE_V4.replace(_V4_SEVEN_LINES, "")
assert _v3_rest == _v4_rest, "v3/v4で置換対象以外の本文に差異がある"
assert DEVELOPER_STD_V4 == v3mod.DEVELOPER_STD_V3


# ------------------------------------------------------------
# STEP: generate-v4 (Meta Advanced Baseline -> v4 Prompt -> 1 call)
# ------------------------------------------------------------
def cmd_generate_v4(out_dir: str, budget_jpy: float, force: bool) -> None:
    os.makedirs(out_dir, exist_ok=True)
    _verify_meta_advanced_sha256()
    meta_advanced_text = v1mod.load_text(META_ADVANCED_PATH)

    v1mod.save_text(
        out_path(out_dir, "prompt_standard_v4.txt"),
        "DEVELOPER:\n" + DEVELOPER_STD_V4 + "\n\n"
        "USER TEMPLATE ({advanced_article} is substituted):\n" +
        STANDARD_USER_TEMPLATE_V4)

    diff_md = (
        "# prompt_diff_v3_v4.md — Standard Prompt v3 -> v4 差分"
        "(頻度帯思想+自然さ優先のみ)\n\n"
        "developerはv3と一字も変えていない。変更したのはuser template内の"
        "次の5行のみで、それ以外の本文(段落順・改行含む、比喩語保持の行を"
        "含む)は一字も変えていない(機械assertで確認済み)。\n\n"
        "## v3の該当5行(置換対象、逐語)\n\n```\n" + v3mod._V3_FIVE_LINES + "\n```\n\n"
        "## v4の置換後7行(逐語)\n\n```\n" + _V4_SEVEN_LINES + "\n```\n\n"
        "## v4 developer(逐語、v3と同一文)\n\n```\n" + DEVELOPER_STD_V4 + "\n```\n\n"
        "## v4 user template全文(逐語)\n\n```\n" + STANDARD_USER_TEMPLATE_V4 + "\n```\n\n"
        "## 変更意図\n\n"
        "- v3は「簡単な語で同じ意味を表せるなら簡単な語を使う」という二値的な"
        "判断基準のみで、頻度の高低による段階的な扱いの違いを与えていなかった"
        "(結果としてinstallation->putting in、collects->gathers、"
        "distant->farawayのような不自然な一語置換が発生した)。\n"
        "- v4では「very common/fairly common/uncommon/rare」という4段階の"
        "頻度感覚を言語化し、頻度帯が下がるほど置換寄りにする一方、"
        "「置換後が自然でない・明確に簡単でないなら置換しない」という歯止めを"
        "明示した。\n"
        "- 「一語での不自然な置換より、自然な言い換えフレーズを優先する」行を"
        "追加し、awkward one-word replacement(putting inのような不自然置換)"
        "を狙って抑制する。\n"
        "- 最後のself-check行を「非本質的な難語を全て置換する」から「明確に"
        "簡単で自然な代替がある場合のみ置換する」に変更し、無理な置換の"
        "強制を弱めた。\n"
        "- 追加した行数は2行(5行->7行)。Promptを過剰に長くしないため、"
        "既存のmetaphor保持指示・Story保持指示・Fact保持指示には触れていない。\n"
    )
    v1mod.save_text(out_path(out_dir, "prompt_diff_v3_v4.md"), diff_md)

    install_logger(out_dir)
    client = v1mod.vfl01.get_client()
    pricing = v1mod.er015base._load_pricing()

    b1v4_user = STANDARD_USER_TEMPLATE_V4.format(advanced_article=meta_advanced_text)
    b1v4_output = out_path(out_dir, "b1v4_standard_meta.md")
    b1v4_meta = out_path(out_dir, "b1v4_standard_meta.meta.json")
    m = v1mod._call_and_record(client, pricing, DEVELOPER_STD_V4, b1v4_user,
                                "b1v4_standard_meta", b1v4_output, b1v4_meta, force)
    total_jpy = m.get("cost_jpy", 0.0)
    if total_jpy > budget_jpy:
        stop = {"stop_reason": "budget exceeded after meta v4 call",
                "total_jpy": total_jpy, "budget_jpy": budget_jpy}
        v1mod.save_json(out_path(out_dir, "stop_reason.json"), stop)
        print(f"[STOP] budget exceeded after meta v4: {total_jpy} > {budget_jpy}")
        raise SystemExit(1)
    text = v1mod.load_text(b1v4_output)
    if not text.strip():
        stop = {"stop_reason": "empty output after retry (meta v4)"}
        v1mod.save_json(out_path(out_dir, "stop_reason.json"), stop)
        print("[STOP] empty output after retry (meta v4)")
        raise SystemExit(1)

    print(f"[DONE] generate-v4 complete. cost_jpy={round(total_jpy, 4)} "
          f"budget_jpy={budget_jpy} retried={m.get('retried')} "
          f"model={m.get('response_model_actual')}")


# ------------------------------------------------------------
# 追加(修正2回目、ユーザー承認): --article sewer 用のgenerate-v4/evaluate
# 以降のcmd_generate_v4/cmd_evaluate*(Meta用)は一切変更していない。
# 全て新規関数の追加のみ。v4 Prompt(DEVELOPER_STD_V4/STANDARD_USER_
# TEMPLATE_V4)はMeta用と完全に同一のものをそのまま再利用する(一字も
# 変えない)。
# ------------------------------------------------------------
def _verify_or_write_prompt_v4_file(out_dir: str) -> str:
    """v4 Prompt(developer+user template)を文字列として構築し、既存の
    prompt_standard_v4.txt(Meta実行時に書き込み済み)とsha256が一致する
    か確認する(『v4 Promptをそのまま、一字も変えず使う』制約の機械的
    証跡)。一致すれば上書きしない。ファイルが無い場合のみ新規に書き込む
    (bands-baseline/generate-v4[meta]が未実行のケースのフォールバック)。
    """
    import hashlib
    composed = ("DEVELOPER:\n" + DEVELOPER_STD_V4 + "\n\n"
                "USER TEMPLATE ({advanced_article} is substituted):\n" +
                STANDARD_USER_TEMPLATE_V4)
    composed_sha = hashlib.sha256(composed.encode("utf-8")).hexdigest()
    dst = out_path(out_dir, "prompt_standard_v4.txt")
    if os.path.exists(dst):
        existing_sha = v1mod._sha256_of_file(dst)
        if existing_sha != composed_sha:
            raise SystemExit(
                "[STOP] prompt_standard_v4.txt sha256 mismatch (v4 Promptを"
                "一字も変えず使う制約に違反する可能性): "
                f"existing={existing_sha} composed={composed_sha}")
    else:
        v1mod.save_text(dst, composed)
        existing_sha = composed_sha
    return existing_sha


def cmd_generate_v4_sewer(out_dir: str, budget_jpy: float, force: bool) -> None:
    os.makedirs(out_dir, exist_ok=True)
    prompt_sha = _verify_or_write_prompt_v4_file(out_dir)

    sewer_adv_text = v1mod.load_text(SEWER_ADVANCED_PATH)
    sewer_adv_sha = v1mod._sha256_of_file(SEWER_ADVANCED_PATH)

    v1mod.save_json(out_path(out_dir, "sewer_v4_generation_sources.json"), {
        "sewer_advanced_path": SEWER_ADVANCED_PATH,
        "sewer_advanced_sha256": sewer_adv_sha,
        "prompt_standard_v4_sha256": prompt_sha,
        "note": ("sewer_advancedのsha256は、sources.json(Meta用、"
                 "news_natural_advanced_standard_a2_trial_01)に既存の期待値"
                 "エントリが無いため、突合対象ではなく実測値の記録(逐語"
                 "入力の証跡)。prompt_standard_v4_sha256はMeta実行時に"
                 "書き込まれたprompt_standard_v4.txtとの一致を確認済み"
                 "(一字も変えていない)。"),
    })

    install_logger(out_dir)
    client = v1mod.vfl01.get_client()
    pricing = v1mod.er015base._load_pricing()

    a2v4_user = STANDARD_USER_TEMPLATE_V4.format(advanced_article=sewer_adv_text)
    a2v4_output = out_path(out_dir, "a2v4_standard_sewer.md")
    a2v4_meta = out_path(out_dir, "a2v4_standard_sewer.meta.json")
    m = v1mod._call_and_record(client, pricing, DEVELOPER_STD_V4, a2v4_user,
                                "a2v4_standard_sewer", a2v4_output, a2v4_meta,
                                force)
    total_jpy = m.get("cost_jpy", 0.0)
    if total_jpy > budget_jpy:
        stop = {"stop_reason": "budget exceeded after sewer v4 call",
                "total_jpy": total_jpy, "budget_jpy": budget_jpy}
        v1mod.save_json(out_path(out_dir, "stop_reason_sewer.json"), stop)
        print(f"[STOP] budget exceeded after sewer v4: {total_jpy} > {budget_jpy}")
        raise SystemExit(1)
    text = v1mod.load_text(a2v4_output)
    if not text.strip():
        stop = {"stop_reason": "empty output after retry (sewer v4)"}
        v1mod.save_json(out_path(out_dir, "stop_reason_sewer.json"), stop)
        print("[STOP] empty output after retry (sewer v4)")
        raise SystemExit(1)

    print(f"[DONE] generate-v4 (sewer) complete. cost_jpy={round(total_jpy, 4)} "
          f"budget_jpy={budget_jpy} retried={m.get('retried')} "
          f"model={m.get('response_model_actual')} "
          f"sewer_advanced_sha256={sewer_adv_sha[:16]}...")


# ------------------------------------------------------------
# STEP: evaluate
# ------------------------------------------------------------
def cmd_evaluate_bands(out_dir: str) -> dict:
    import wordfreq
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_map = _build_lemma_rank_map(top20000)

    v4_path = out_path(out_dir, "b1v4_standard_meta.md")
    v4_text = v1mod.load_text(v4_path)
    v4_result = measure_bands(v4_text, rank_map)

    baseline = v1mod.load_json(out_path(out_dir, "vocab_bands_baseline.json"))
    adv_result = baseline["meta_advanced_baseline"]

    all_result = dict(baseline)
    all_result["meta_standard_v4"] = v4_result
    v1mod.save_json(out_path(out_dir, "vocab_bands_all.json"), all_result)

    # Meta Advanced -> v4 の「D帯(かつproper_nounでない)」異なり語差分
    def hard_words(m):
        s = set()
        for b in ["C", "D"]:
            for w in m["bucket_words"][b]:
                s.add(w["word"])
        return s

    adv_hard = hard_words(adv_result)
    v4_hard = hard_words(v4_result)
    disappeared = sorted(adv_hard - v4_hard)
    remained = sorted(adv_hard & v4_hard)
    new_hard = sorted(v4_hard - adv_hard)

    lines = ["# vocab_bands_evaluate.md — Meta v4帯別測定 + "
             "Meta Advanced -> v4 (帯C/D)差分\n"]
    lines += _bands_md_table("Meta Standard v4", v4_result)
    lines.append("\n## Meta Advanced Baseline -> v4 の帯C/D(異なり語)差分\n")
    lines.append(f"- Advanced 帯C/D {len(adv_hard)}語 -> v4 帯C/D "
                 f"{len(v4_hard)}語 ({len(adv_hard) - len(v4_hard):+d})")
    lines.append(f"- 消えた語(Advancedで帯C/D、v4では帯C/Dでない/未使用): "
                 f"{len(disappeared)}語")
    lines.append(f"- 残った語(Advanced/v4とも帯C/D): {len(remained)}語")
    lines.append(f"- 新たに出た語(v4のみ帯C/D): {len(new_hard)}語")
    lines.append("\n### 消えた語\n")
    lines.append(", ".join(disappeared) if disappeared else "(なし)")
    lines.append("\n### 残った語\n")
    lines.append(", ".join(remained) if remained else "(なし)")
    lines.append("\n### 新たに出た語\n")
    lines.append(", ".join(new_hard) if new_hard else "(なし)")
    v1mod.save_text(out_path(out_dir, "vocab_bands_evaluate.md"), "\n".join(lines))

    print(f"[OK] evaluate-bands written. v4 C/D(distinct)={len(v4_hard)} "
          f"(Advanced {len(adv_hard)}); disappeared={len(disappeared)} "
          f"remained={len(remained)} new={len(new_hard)}")
    return {"disappeared": disappeared, "remained": remained, "new": new_hard}


def cmd_evaluate_levels(out_dir: str) -> dict:
    files = {
        "meta_advanced_baseline": META_ADVANCED_PATH,
        "meta_standard_v1": META_STANDARD_V1_PATH,
        "meta_standard_v4": out_path(out_dir, "b1v4_standard_meta.md"),
    }
    metrics = {}
    for key, path in files.items():
        text = v1mod.load_text(path)
        metrics[key] = v1mod._level_metrics(text)
    v1mod.save_json(out_path(out_dir, "level_metrics.json"), metrics)

    label_map = {
        "meta_advanced_baseline": "Meta Advanced Baseline",
        "meta_standard_v1": "Meta Standard v1 (B-1)",
        "meta_standard_v4": "Meta Standard v4",
    }
    md_lines = ["# level_metrics.md — Level比較(Meta 3段階、参考値、機械判定は"
                "最終判断に用いない)\n",
                "| 記事 | words | sentences | avg words/sent | avg syll/word | "
                "long-sent(>=20w)率 | subordinator/100w | FK grade(heuristic) |",
                "|---|---|---|---|---|---|---|---|"]
    for key in ["meta_advanced_baseline", "meta_standard_v1", "meta_standard_v4"]:
        m = metrics[key]
        md_lines.append(
            f"| {label_map[key]} | {m['word_count']} | {m['sentence_count']} | "
            f"{m['avg_sentence_length_words']} | {m['avg_syllables_per_word_heuristic']} | "
            f"{m['long_sentence_ratio_ge20words']} | {m['subordinators_per_100_words']} | "
            f"{m['flesch_kincaid_grade_heuristic']} |")

    # Sewer v3の既存level_metricsを参考として引用(再計算しない)
    sewer_existing = v1mod.load_json(out_path(V3_OUT_DIR, "level_metrics.json"))
    sv3 = sewer_existing.get("sewer_standard_v3")
    if sv3:
        md_lines.append(f"| Sewer Standard v3 (参考、既存計算値を引用) | "
                          f"{sv3['word_count']} | {sv3['sentence_count']} | "
                          f"{sv3['avg_sentence_length_words']} | "
                          f"{sv3['avg_syllables_per_word_heuristic']} | "
                          f"{sv3['long_sentence_ratio_ge20words']} | "
                          f"{sv3['subordinators_per_100_words']} | "
                          f"{sv3['flesch_kincaid_grade_heuristic']} |")

    adv_avg = metrics["meta_advanced_baseline"]["avg_sentence_length_words"]
    v1_avg = metrics["meta_standard_v1"]["avg_sentence_length_words"]
    v4_avg = metrics["meta_standard_v4"]["avg_sentence_length_words"]
    md_lines.append(f"\n## 平均語/文の変化(参考)\n")
    md_lines.append(f"- Advanced {adv_avg} -> Standard v1 {v1_avg} -> "
                     f"Standard v4 {v4_avg} (v1比 {round(v4_avg - v1_avg, 2):+.2f}語、"
                     f"9〜11語/文目標との差: {round(v4_avg - 10, 2):+.2f})")
    v1mod.save_text(out_path(out_dir, "level_metrics.md"), "\n".join(md_lines))
    print("[OK] level_metrics.json / level_metrics.md written (Meta 3段階 "
          "+ Sewer v3参考)")
    return metrics


def cmd_evaluate_fact_diff(out_dir: str) -> dict:
    adv = v1mod._fact_tokens(v1mod.load_text(META_ADVANCED_PATH))
    v4 = v1mod._fact_tokens(v1mod.load_text(out_path(out_dir, "b1v4_standard_meta.md")))
    result = {
        "advanced_to_v4": {
            "advanced": adv,
            "v4": v4,
            "numbers_missing_in_v4": sorted(set(adv["numbers"]) - set(v4["numbers"])),
            "numbers_added_in_v4": sorted(set(v4["numbers"]) - set(adv["numbers"])),
            "proper_nouns_missing_in_v4": sorted(set(adv["proper_nouns"]) - set(v4["proper_nouns"])),
            "proper_nouns_added_in_v4": sorted(set(v4["proper_nouns"]) - set(adv["proper_nouns"])),
        }
    }
    v1mod.save_json(out_path(out_dir, "fact_diff_machine.json"), result)
    print("[OK] fact_diff_machine.json written (advanced_to_v4)")
    return result


def cmd_evaluate_structure_map(out_dir: str) -> None:
    meta_adv = v1mod.load_text(META_ADVANCED_PATH)
    meta_v1 = v1mod.load_text(META_STANDARD_V1_PATH)
    meta_v4 = v1mod.load_text(out_path(out_dir, "b1v4_standard_meta.md"))
    sewer_v3 = v1mod.load_text(SEWER_V3_PATH)

    def para_count(text: str) -> int:
        _, body = v1mod._strip_title(text)
        return len([p for p in body.split("\n\n") if p.strip()])

    lines = ["# structure_map.md — 段落対応・Reveal/比喩/Ending保持確認・"
             "比喩語保持有無(Meta 3段階 + Sewer v3参考)\n"]
    lines.append("## 段落数対応\n")
    lines.append(f"- Meta: Advanced {para_count(meta_adv)}段落 / "
                 f"Standard v1 {para_count(meta_v1)}段落 / "
                 f"Standard v4 {para_count(meta_v4)}段落")
    lines.append(f"- Sewer Standard v3(参考): {para_count(sewer_v3)}段落")

    lines.append("\n## 比喩語保持有無(語単位、大小無視の部分一致、"
                 "v2mod.METAPHOR_WORDSをそのまま再利用)\n")
    lines.append("| 語 | Meta Advanced | Meta v1 | Meta v4 | Sewer v3(参考) |")
    lines.append("|---|---|---|---|---|")
    sets = {
        "adv": v2mod._metaphor_presence(meta_adv),
        "v1": v2mod._metaphor_presence(meta_v1),
        "v4": v2mod._metaphor_presence(meta_v4),
        "sewer_v3": v2mod._metaphor_presence(sewer_v3),
    }
    for w in v2mod.METAPHOR_WORDS:
        row = [w]
        for key in ["adv", "v1", "v4", "sewer_v3"]:
            row.append("○" if sets[key].get(w) else "-")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("\n## Reveal / Ending / \"some parts of the calls\" 保持"
                 "(手動確認、○×)\n")
    v4_lower = meta_v4.lower()
    reveal_ok = ("human concierges" in v4_lower and "backstage" in v4_lower)
    ending_ok = ("who is speaking on the stage" in v4_lower and
                 "who is behind the curtain" in v4_lower)
    scope_ok = "some parts of the calls" in v4_lower
    lines.append(f"- Reveal(human conciergesがAIの代わりに対応していた、"
                 f"backstageの発見という段落構成): {'○' if reveal_ok else '×(要確認)'}")
    lines.append(f"- Ending logic(\"Who is speaking on the stage? And who is "
                 f"behind the curtain?\"の結び): {'○' if ending_ok else '×(要確認)'}")
    lines.append(f"- 数量表現\"some parts of the calls\"の維持(修正禁止指定): "
                 f"{'○' if scope_ok else '×(要確認、本文参照)'}")

    v1mod.save_text(out_path(out_dir, "structure_map.md"), "\n".join(lines))
    print(f"[OK] structure_map.md written. reveal={reveal_ok} "
          f"ending={ending_ok} scope_some_parts={scope_ok}")


def cmd_evaluate_comparison_md(out_dir: str) -> None:
    meta_adv = v1mod.load_text(META_ADVANCED_PATH)
    meta_v1 = v1mod.load_text(META_STANDARD_V1_PATH)
    meta_v4 = v1mod.load_text(out_path(out_dir, "b1v4_standard_meta.md"))
    md = (
        "# comparison_meta_v4.md — Meta: Advanced -> Standard v1 (B-1) -> "
        "Standard v4\n\n"
        "## Advanced (改変禁止Baseline)\n\n" + meta_adv + "\n\n---\n\n"
        "## Standard v1 (B-1, NEWS-JA-TO-EN-ADAPTATION-TRIAL-01系、改変禁止)"
        "\n\n" + meta_v1 + "\n\n---\n\n"
        "## Standard v4 (NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01)\n\n" +
        meta_v4 + "\n"
    )
    v1mod.save_text(out_path(out_dir, "comparison_meta_v4.md"), md)

    sewer_v3 = v1mod.load_text(SEWER_V3_PATH)
    cross_md = (
        "# comparison_sewer_v3_meta_v4.md — 頻度帯+自然さ優先の方針が別Topicで"
        "同様に機能するかのクロス比較\n\n"
        "## Sewer Standard v3(下水道、旧方針: 2値判断のみ、NEWS-STANDARD-A2-"
        "VOCAB-EFFECTIVENESS-TRIAL-01)\n\n" + sewer_v3 + "\n\n---\n\n"
        "## Meta Standard v4(Meta、新方針: 頻度帯4段階+自然さ優先、本Trial)"
        "\n\n" + meta_v4 + "\n"
    )
    v1mod.save_text(out_path(out_dir, "comparison_sewer_v3_meta_v4.md"), cross_md)
    print("[OK] comparison_meta_v4.md / comparison_sewer_v3_meta_v4.md written")


def cmd_evaluate(out_dir: str) -> None:
    cmd_evaluate_bands(out_dir)
    cmd_evaluate_levels(out_dir)
    cmd_evaluate_fact_diff(out_dir)
    cmd_evaluate_structure_map(out_dir)
    cmd_evaluate_comparison_md(out_dir)


# ------------------------------------------------------------
# 追加(修正2回目、ユーザー承認): --article sewer 用のevaluate一式
# 上のcmd_evaluate*(Meta用)は無変更。すべて新規関数の追加のみ。
# ------------------------------------------------------------
def cmd_evaluate_sewer_bands(out_dir: str) -> dict:
    import wordfreq
    top20000 = wordfreq.top_n_list("en", 20000)
    rank_map = _build_lemma_rank_map(top20000)

    sewer_adv_text = v1mod.load_text(SEWER_ADVANCED_PATH)
    sewer_v3_text = v1mod.load_text(SEWER_V3_PATH)
    sewer_v4_text = v1mod.load_text(out_path(out_dir, "a2v4_standard_sewer.md"))

    result = {
        "sewer_advanced": measure_bands(sewer_adv_text, rank_map),
        "sewer_standard_v3": measure_bands(sewer_v3_text, rank_map),
        "sewer_standard_v4": measure_bands(sewer_v4_text, rank_map),
    }
    v1mod.save_json(out_path(out_dir, "vocab_bands_sewer_all.json"), result)

    lines = ["# vocab_bands_sewer_evaluate.md — Sewer 頻度帯別測定 "
             "(Advanced / Standard v3 / Standard v4、3段階)\n"]
    lines += _bands_md_table("Sewer Advanced", result["sewer_advanced"])
    lines += _bands_md_table("Sewer Standard v3", result["sewer_standard_v3"])
    lines += _bands_md_table("Sewer Standard v4", result["sewer_standard_v4"])

    def hard_words(m, bands):
        s = set()
        for b in bands:
            for w in m["bucket_words"][b]:
                s.add(w["word"])
        return s

    for bands, label in [(["C", "D"], "C/D"), (["B", "C", "D"], "B/C/D")]:
        adv_hard = hard_words(result["sewer_advanced"], bands)
        v3_hard = hard_words(result["sewer_standard_v3"], bands)
        v4_hard = hard_words(result["sewer_standard_v4"], bands)
        lines.append(f"\n## 帯{label}(異なり語)の3段階推移(Advanced -> v3 -> v4)\n")
        lines.append(f"- 異なり語数: Advanced {len(adv_hard)} -> v3 {len(v3_hard)} "
                     f"-> v4 {len(v4_hard)}")
        lines.append(f"- Advancedのみ(v3・v4いずれにも帯{label}として残らない): "
                     f"{', '.join(sorted(adv_hard - v3_hard - v4_hard)) or '(なし)'}")
        lines.append(f"- Advanced/v3/v4いずれも帯{label}のまま(そのまま残存の候補): "
                     f"{', '.join(sorted(adv_hard & v3_hard & v4_hard)) or '(なし)'}")
        lines.append(f"- Advancedでは帯{label}でなく、v4で新たに帯{label}になった語"
                     f"(難語化候補): "
                     f"{', '.join(sorted(v4_hard - adv_hard)) or '(なし)'}")
        lines.append(f"- v3では帯{label}だがv4では帯{label}でない語"
                     f"(v3->v4で解消された候補): "
                     f"{', '.join(sorted(v3_hard - v4_hard)) or '(なし)'}")
        lines.append(f"- Advancedでは帯{label}だったがv3で既に解消され、v4でも"
                     f"帯{label}のままに戻っていない語: "
                     f"{', '.join(sorted((adv_hard - v3_hard) - v4_hard)) or '(なし)'}")

    v1mod.save_text(out_path(out_dir, "vocab_bands_sewer_evaluate.md"),
                     "\n".join(lines))
    print("[OK] evaluate-sewer-bands written "
          f"(adv/v3/v4 distinct C/D="
          f"{len(hard_words(result['sewer_advanced'], ['C','D']))}/"
          f"{len(hard_words(result['sewer_standard_v3'], ['C','D']))}/"
          f"{len(hard_words(result['sewer_standard_v4'], ['C','D']))})")
    return result


def cmd_evaluate_sewer_levels(out_dir: str) -> dict:
    files = {
        "sewer_advanced": SEWER_ADVANCED_PATH,
        "sewer_standard_v3": SEWER_V3_PATH,
        "sewer_standard_v4": out_path(out_dir, "a2v4_standard_sewer.md"),
    }
    metrics = {}
    for key, path in files.items():
        text = v1mod.load_text(path)
        metrics[key] = v1mod._level_metrics(text)
    v1mod.save_json(out_path(out_dir, "level_metrics_sewer.json"), metrics)

    label_map = {
        "sewer_advanced": "Sewer Advanced",
        "sewer_standard_v3": "Sewer Standard v3",
        "sewer_standard_v4": "Sewer Standard v4",
    }
    md_lines = ["# level_metrics_sewer.md — Level比較(Sewer 3段階、参考値、"
                "機械判定は最終判断に用いない)\n",
                "| 記事 | words | sentences | avg words/sent | avg syll/word | "
                "long-sent(>=20w)率 | subordinator/100w | FK grade(heuristic) |",
                "|---|---|---|---|---|---|---|---|"]
    for key in ["sewer_advanced", "sewer_standard_v3", "sewer_standard_v4"]:
        m = metrics[key]
        md_lines.append(
            f"| {label_map[key]} | {m['word_count']} | {m['sentence_count']} | "
            f"{m['avg_sentence_length_words']} | {m['avg_syllables_per_word_heuristic']} | "
            f"{m['long_sentence_ratio_ge20words']} | {m['subordinators_per_100_words']} | "
            f"{m['flesch_kincaid_grade_heuristic']} |")

    adv_avg = metrics["sewer_advanced"]["avg_sentence_length_words"]
    v3_avg = metrics["sewer_standard_v3"]["avg_sentence_length_words"]
    v4_avg = metrics["sewer_standard_v4"]["avg_sentence_length_words"]
    md_lines.append("\n## 平均語/文の変化(参考)\n")
    md_lines.append(f"- Advanced {adv_avg} -> Standard v3 {v3_avg} -> "
                     f"Standard v4 {v4_avg} (v3比 {round(v4_avg - v3_avg, 2):+.2f}語)")
    v1mod.save_text(out_path(out_dir, "level_metrics_sewer.md"),
                     "\n".join(md_lines))
    print("[OK] level_metrics_sewer.json / level_metrics_sewer.md written")
    return metrics


def cmd_evaluate_sewer_fact_diff(out_dir: str) -> dict:
    adv = v1mod._fact_tokens(v1mod.load_text(SEWER_ADVANCED_PATH))
    v4 = v1mod._fact_tokens(
        v1mod.load_text(out_path(out_dir, "a2v4_standard_sewer.md")))
    result = {
        "advanced_to_v4": {
            "advanced": adv,
            "v4": v4,
            "numbers_missing_in_v4": sorted(set(adv["numbers"]) - set(v4["numbers"])),
            "numbers_added_in_v4": sorted(set(v4["numbers"]) - set(adv["numbers"])),
            "proper_nouns_missing_in_v4": sorted(
                set(adv["proper_nouns"]) - set(v4["proper_nouns"])),
            "proper_nouns_added_in_v4": sorted(
                set(v4["proper_nouns"]) - set(adv["proper_nouns"])),
        }
    }
    v1mod.save_json(out_path(out_dir, "fact_diff_machine_sewer.json"), result)
    print("[OK] fact_diff_machine_sewer.json written (advanced_to_v4)")
    return result


def cmd_evaluate_sewer_structure_map(out_dir: str) -> None:
    sewer_adv = v1mod.load_text(SEWER_ADVANCED_PATH)
    sewer_v3 = v1mod.load_text(SEWER_V3_PATH)
    sewer_v4 = v1mod.load_text(out_path(out_dir, "a2v4_standard_sewer.md"))

    def para_count(text: str) -> int:
        _, body = v1mod._strip_title(text)
        return len([p for p in body.split("\n\n") if p.strip()])

    lines = ["# structure_map_sewer.md — 段落対応・Reveal/比喩/Ending保持確認・"
             "比喩語保持有無(Sewer 3段階: Advanced/v3/v4)\n"]
    lines.append("## 段落数対応\n")
    lines.append(f"- Advanced {para_count(sewer_adv)}段落 / "
                 f"Standard v3 {para_count(sewer_v3)}段落 / "
                 f"Standard v4 {para_count(sewer_v4)}段落")

    lines.append("\n## 比喩語保持有無(語単位、大小無視の部分一致、"
                 "v2mod.METAPHOR_WORDSをそのまま再利用)\n")
    lines.append("| 語 | Advanced | v3 | v4 |")
    lines.append("|---|---|---|---|")
    sets = {
        "adv": v2mod._metaphor_presence(sewer_adv),
        "v3": v2mod._metaphor_presence(sewer_v3),
        "v4": v2mod._metaphor_presence(sewer_v4),
    }
    for w in v2mod.METAPHOR_WORDS:
        row = [w]
        for key in ["adv", "v3", "v4"]:
            row.append("○" if sets[key].get(w) else "-")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("\n## Reveal / 中心比喩(main artery / washing machine)の直喩維持 "
                 "/ Ending 位置(手動確認、○×。v3mod既存Trialの判定文言を再利用し"
                 "v4にも同じ基準を適用)\n")
    v4_lower = sewer_v4.lower()
    reveal_ok = ("combined septic tank" in v4_lower and
                 "small water-treatment" in v4_lower)
    metaphor_marker_ok = (("like a hidden main artery" in v4_lower or
                            "is like" in v4_lower) and
                           "washing machine" in v4_lower)
    ending_ok = "surprisingly familiar place" in v4_lower
    lines.append(f"- Reveal(下水道->合併浄化槽への切り替え説明段落、v3で使われた"
                 f"表現がv4にもあるか): {'○' if reveal_ok else '×(要確認、本文参照)'}")
    lines.append(f"- 中心比喩(main artery / washing machineが直喩[like/as]のまま"
                 f"保持され、事実文化していないか): "
                 f"{'○' if metaphor_marker_ok else '×(要確認、本文参照)'}")
    lines.append(f"- Ending logic(\"surprisingly familiar place\"の結び、v3と同じ"
                 f"表現がv4にもあるか): {'○' if ending_ok else '×(要確認、本文参照)'}")
    lines.append("\n(注: reveal/ending判定はv3で使われた逐語表現の残存チェックで"
                 "あり、v4がv3と異なる自然な言い回しで同じ内容を表現していても"
                 "×になり得る。機械判定であり、最終判断はSonnet目視"
                 "[§本文参照]・Fable評価に委ねる。)")

    v1mod.save_text(out_path(out_dir, "structure_map_sewer.md"),
                     "\n".join(lines))
    print(f"[OK] structure_map_sewer.md written. reveal={reveal_ok} "
          f"metaphor_marker={metaphor_marker_ok} ending={ending_ok}")


def cmd_evaluate_sewer_comparison_md(out_dir: str) -> None:
    sewer_adv = v1mod.load_text(SEWER_ADVANCED_PATH)
    sewer_v3 = v1mod.load_text(SEWER_V3_PATH)
    sewer_v4 = v1mod.load_text(out_path(out_dir, "a2v4_standard_sewer.md"))
    md = (
        "# comparison_sewer_v3_v4.md — Sewer: Advanced -> Standard v3 -> "
        "Standard v4\n\n"
        "## Advanced (改変禁止Baseline)\n\n" + sewer_adv + "\n\n---\n\n"
        "## Standard v3 (NEWS-STANDARD-A2-VOCAB-EFFECTIVENESS-TRIAL-01、"
        "改変禁止)\n\n" + sewer_v3 + "\n\n---\n\n"
        "## Standard v4 (NEWS-STANDARD-A2-VOCAB-BANDING-TRIAL-01、本Trial"
        "追加)\n\n" + sewer_v4 + "\n"
    )
    v1mod.save_text(out_path(out_dir, "comparison_sewer_v3_v4.md"), md)
    print("[OK] comparison_sewer_v3_v4.md written")


def cmd_evaluate_sewer(out_dir: str) -> None:
    cmd_evaluate_sewer_bands(out_dir)
    cmd_evaluate_sewer_levels(out_dir)
    cmd_evaluate_sewer_fact_diff(out_dir)
    cmd_evaluate_sewer_structure_map(out_dir)
    cmd_evaluate_sewer_comparison_md(out_dir)


# ------------------------------------------------------------
# STEP: assemble (cost.json)
# ------------------------------------------------------------
def cmd_assemble(out_dir: str) -> None:
    meta_path = out_path(out_dir, "b1v4_standard_meta.meta.json")
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
        "additional_llm_call_count": len(calls),
        "total_cost_jpy": round(total_jpy, 4),
        "budget_jpy": 100,
        "within_budget": total_jpy <= 100,
    }
    v1mod.save_json(out_path(out_dir, "cost.json"), cost)
    print(f"[OK] cost.json written. total_cost_jpy={round(total_jpy, 4)} "
          f"within_budget={cost['within_budget']} "
          f"additional_llm_call_count={len(calls)}")


# ------------------------------------------------------------
# 追加(修正2回目、ユーザー承認): --article sewer 用のassemble
# 既存のcmd_assemble(Meta用、cost.json)は無変更。Sewer分はcost_sewer.json
# へ別ファイルとして記録し、既存のcost.jsonを上書きしない。
# ------------------------------------------------------------
def cmd_assemble_sewer(out_dir: str) -> None:
    meta_path = out_path(out_dir, "a2v4_standard_sewer.meta.json")
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
        "additional_llm_call_count": len(calls),
        "total_cost_jpy": round(total_jpy, 4),
        "budget_jpy": 100,
        "within_budget": total_jpy <= 100,
        "note": ("本Trial(修正2回目、Sewer article)専用のcost記録。Meta分"
                 "(修正1回目、既存cost.json)とは別ファイル。合算する場合は"
                 "cost.json.total_cost_jpy + このファイルのtotal_cost_jpy。"),
    }
    v1mod.save_json(out_path(out_dir, "cost_sewer.json"), cost)
    print(f"[OK] cost_sewer.json written. total_cost_jpy={round(total_jpy, 4)} "
          f"within_budget={cost['within_budget']} "
          f"additional_llm_call_count={len(calls)}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--step", required=True,
                     choices=["bands-baseline", "generate-v4",
                              "evaluate", "assemble"])
    ap.add_argument("--budget-jpy", type=float, default=100.0)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--article", choices=["meta", "sewer"], default="meta",
                     help=("追加[修正2回目、ユーザー承認]: 対象記事。meta="
                           "既存Meta処理(無変更)、sewer=Sewer記事へv4を"
                           "適用する新規追加パス。省略時はmetaでありMeta"
                           "処理は従来通り。"))
    args = ap.parse_args()

    if args.step == "bands-baseline":
        cmd_bands_baseline(args.out_dir)
    elif args.step == "generate-v4":
        if args.article == "sewer":
            cmd_generate_v4_sewer(args.out_dir, args.budget_jpy, args.force)
        else:
            cmd_generate_v4(args.out_dir, args.budget_jpy, args.force)
    elif args.step == "evaluate":
        if args.article == "sewer":
            cmd_evaluate_sewer(args.out_dir)
        else:
            cmd_evaluate(args.out_dir)
    elif args.step == "assemble":
        if args.article == "sewer":
            cmd_assemble_sewer(args.out_dir)
        else:
            cmd_assemble(args.out_dir)


if __name__ == "__main__":
    main()
