# ============================================================
# er014_output/four_type_observation_01/discovery/finalize_key_phrases_b1b_manual.py
# 管理ID: USER-TEST-AUDIO-COMPLETION-01-DISCOVERY
#
# 目的: Discovery B1B記事のKey Phrase自動選定(方式L選定)が、有限助動詞
# ブロックリストに一致する"have agency"を含む候補しか出さず、複数回
# (計4回、production_set_cost.json記録)KEY_WORDS_STRUCTURE_INVALID/
# REDUNDANCY_NGとなり完走できなかったため、ユーザー判断により今回は
# 選定(Selection)段階のみを人手で行う。
#
# 変更しないもの:
#   - 既存Validator(er003_key_words_canonicalization.validate_canonicalization_item/
#     er003_key_words_min_unit._FINITE_AUX_WORDS等)は一切変更しない。
#   - canonicalization/Redundancy QA(LLM呼び出し)は既存関数
#     (er003_v1_n3_01_scaffold_generate.run_key_phrase_canonicalization/
#     run_key_phrase_redundancy_qa)をそのまま呼ぶ(選定[Selection]段階の
#     run_key_phrase_selection()だけをスキップする)。
#
# 実行方法:
#   .venv/Scripts/python.exe er014_output/four_type_observation_01/discovery/finalize_key_phrases_b1b_manual.py
# ============================================================
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.getcwd())
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import er003_v1_n3_01_scaffold_generate as sc
import er003_key_words_min_unit as p2g

BASE_DIR = "er014_output/four_type_observation_01/discovery"
ARTICLE_PATH = f"{BASE_DIR}/b1b/article.md"
OUT_DIR = f"{BASE_DIR}/key_phrases/b1b"
ARTICLE_ID = "discovery_why_silence_uncomfortable_b1b_manual_selection_2026-09-14"
SOURCE_LEVEL = "B1-B(N3-01, fact-fix complete3, canonical final text, MANUAL SELECTION)"

# ------------------------------------------------------------
# 人手選定5件(2026-09-14、ユーザー指示によるmanual selection)。
# 各source_spanはcanonical B1B本文(article.md)に実在する連続spanの
# コピー(語形変更なし)。有限助動詞ブロックリスト
# (is/are/was/were/has/have/had/will/would/can/could/should/may/might/must)
# を含まないことを選定前に確認済み(このファイル末尾のself-checkでも
# 再確認する)。
# ------------------------------------------------------------
MANUAL_ITEMS = [
    {
        "rank": 1,
        "display_phrase": "nothing to do but think",
        "source_span": "nothing to do but think",
        "source_sentence": (
            "Across 11 studies, participants generally did not enjoy spending six "
            "to fifteen minutes with nothing to do but think."
        ),
        "ja_gloss": "考えることしかすることがない状態",
        "selection_reason": (
            "「〜以外にすることがない」という省略的な構文(nothing to do but+動詞原形)。"
            "butが「〜以外」という除外の意味で働く点が初見のリスナーには聞き取りにくく、"
            "単独でも他の文脈(nothing to do but wait等)で再利用しやすい自然な単位。"
        ),
    },
    {
        "rank": 2,
        "display_phrase": "reduced the feeling of connection",
        "source_span": "reduced the feeling of connection",
        "source_sentence": "For strangers, these longer gaps reduced the feeling of connection.",
        "ja_gloss": "つながっている感覚を弱めた",
        "selection_reason": (
            "動詞reduced+抽象名詞句という構造。「reduced」の目的語が長い名詞句"
            "(the feeling of connection)であるため、聞き取り時に主語・動詞・目的語の"
            "境界を見失いやすい。人間関係・感情の文脈で再利用可能。"
        ),
    },
    {
        "rank": 3,
        "display_phrase": "being in the present moment",
        "source_span": "being in the present moment",
        "source_sentence": (
            "The outdoor setting also brought less boredom and a stronger feeling "
            "of being in the present moment."
        ),
        "ja_gloss": "今この瞬間にいる感覚",
        "selection_reason": (
            "動名詞being+前置詞句という構造で、feeling ofの後に続く形。マインドフルネス"
            "関連の定型表現として他文脈でも頻出し、再利用価値が高い。"
        ),
    },
    {
        "rank": 4,
        "display_phrase": "actively choosing solitude",
        "source_span": "actively choosing solitude",
        "source_sentence": "In one study, actively choosing solitude was associated with relaxation and lower stress.",
        "ja_gloss": "自分から積極的に孤独を選ぶこと",
        "selection_reason": (
            "副詞+動名詞+目的語(actively choosing solitude)という動名詞句。文の主語として"
            "機能しており、動詞的な意味を持つ名詞句を聞き取る負荷が高い。「積極的に選ぶ」"
            "という組み合わせは他の名詞に差し替えて再利用可能(例: actively choosing rest)。"
        ),
    },
    {
        "rank": 5,
        "display_phrase": "complicates any simple cultural story",
        "source_span": "complicates any simple cultural story",
        "source_sentence": "A staged one-to-one tutorial complicates any simple cultural story.",
        "ja_gloss": "単純な文化的な説明を複雑にする",
        "selection_reason": (
            "動詞complicates(三人称単数現在)+目的語という構造。「complicate」は硬めの"
            "学術語彙で、「any simple X」という一般化された言い方と組み合わさることで"
            "文全体の要点(単純な国別ステレオタイプは通用しない)を担っている。"
        ),
    },
]

# 除外した主な候補と除外理由(選定作業ログ)。
EXCLUDED_CANDIDATES = [
    {
        "candidate": "have agency",
        "source_sentence": "Quiet can therefore function differently when people have agency and a mental path to follow.",
        "reason": (
            "ユーザー指示により今回は不採用。語彙動詞haveが既存Validatorの有限助動詞"
            "ブロックリスト(_FINITE_AUX_WORDS)に一致し、KEY_WORDS_STRUCTURE_INVALIDと"
            "なる(過去4回の自動選定試行すべてでこの1件が原因、production_set_cost.json"
            "記録)。本文を書き換えて回避することはしない。Validator誤検知はOpen Item化する。"
        ),
    },
    {
        "candidate": "a mental path to follow",
        "source_sentence": "Quiet can therefore function differently when people have agency and a mental path to follow.",
        "reason": (
            "有限助動詞は含まないため構造上は選定可能だが、過去のRedundancy QA試行"
            "(call2)で'occupy their thoughts'との意味重複(meaning_overlap FAIL)が"
            "指摘された概念(考える方向性を持つこと)に近い。本セットの'actively choosing "
            "solitude'(孤独を選ぶという行為の主体性)と概念が近接するリスクを避けるため、"
            "今回は不採用。"
        ),
    },
    {
        "candidate": "occupy their thoughts",
        "source_sentence": (
            "In another study, students told to occupy their thoughts for a brief "
            "period reported better mood, greater relaxation, and lower arousal afterward."
        ),
        "reason": (
            "過去試行(call2)でcanonicalization段階のqa_traceable_contiguous_span不合格"
            "(their→one's正規化でspan追跡性が壊れる)歴があり、'a mental path to follow'"
            "との重複指摘も受けた。今回は同種のリスクを避けるため不採用。"
        ),
    },
    {
        "candidate": "lasted four seconds",
        "source_sentence": "In one version, a single silence lasted four seconds.",
        "reason": "有限助動詞は含まないが、他4件と比べてListening Blocker価値(意味の抽象度・学習再利用性)が低いと判断し不採用。",
    },
    {
        "candidate": "mixed picture",
        "source_sentence": "Research on the body shows the same mixed picture.",
        "reason": "2語のみで短く、単独では文脈依存度が高いため今回の5件には含めなかった。",
    },
    {
        "candidate": "thinking for pleasure",
        "source_sentence": (
            "In a study of 2,557 college students at 12 sites in 11 countries, an "
            "everyday activity was enjoyed more than thinking for pleasure in every "
            "country tested."
        ),
        "reason": "良い候補だが、選定5件の中で'nothing to do but think'と概念(何もしないで考えること)が近く、重複回避のため不採用。",
    },
]

_FINITE_AUX = p2g._FINITE_AUX_WORDS


def _self_check(article_text: str) -> None:
    for item in MANUAL_ITEMS:
        span = item["source_span"]
        assert span in article_text, f"source_spanが本文に存在しません: {span!r}"
        assert span in item["source_sentence"], f"source_spanがsource_sentence内にありません: {span!r}"
        assert item["source_sentence"] in article_text, f"source_sentenceが本文に存在しません: {item['source_sentence']!r}"
        tokens = [t.lower() for t in span.replace("-", " ").split()]
        aux_hit = [t for t in tokens if t.strip(".,;:") in _FINITE_AUX]
        assert not aux_hit, f"有限助動詞ブロックリストに一致するトークンがあります: {span!r} -> {aux_hit}"
        word_count = len(span.split())
        assert 1 <= word_count <= 5, f"1〜5語の範囲外です: {span!r} ({word_count}語)"
    ranks = [item["rank"] for item in MANUAL_ITEMS]
    assert ranks == [1, 2, 3, 4, 5], f"rankが1..5の連番になっていません: {ranks}"
    print("[MANUAL-KP-B1B] self-check OK: 5件すべてsource_span/有限助動詞/語数条件を満たしています。")


def main() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(ARTICLE_PATH, encoding="utf-8") as f:
        article_text = f.read()

    _self_check(article_text)

    canon = sc.run_key_phrase_canonicalization(
        article_text, MANUAL_ITEMS, OUT_DIR, ARTICLE_ID, process="B1_SUPPORT")
    print(f"[MANUAL-KP-B1B] canonicalization status={canon['status']}")

    result = {"selection_mode": "manual_user_decision_2026-09-14", "canonicalization": canon,
               "redundancy_qa": None}

    if canon["status"] not in ("CANONICALIZATION_PASS", "CANONICALIZATION_REVIEW_REQUIRED"):
        print(f"[MANUAL-KP-B1B] STOP: canonicalizationがPASS/REVIEW_REQUIREDになりませんでした: {canon['status']}")
        with open(f"{OUT_DIR}/manual_finalize_result_summary.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        return result

    merged_items = canon["merged"]["items"]
    redundancy = sc.run_key_phrase_redundancy_qa(
        article_text, merged_items, OUT_DIR, ARTICLE_ID, process="B1_SUPPORT")
    print(f"[MANUAL-KP-B1B] redundancy_qa status={redundancy['status']} "
          f"duplicate_pairs={redundancy['duplicate_pairs']}")
    result["redundancy_qa"] = redundancy

    # keywords_canonicalized.jsonにselection_modeを追記(既存形式のitems配列は
    # そのまま、トップレベルにmetaフィールドを1つ追加するのみ)。
    kc_path = f"{OUT_DIR}/keywords_canonicalized.json"
    with open(kc_path, encoding="utf-8") as f:
        kc_doc = json.load(f)
    if isinstance(kc_doc, dict) and "items" in kc_doc:
        kc_doc_out = kc_doc
    else:
        kc_doc_out = {"items": kc_doc}
    kc_doc_out["selection_mode"] = "manual_user_decision_2026-09-14"
    kc_doc_out["overall_status"] = canon["merged"]["overall_status"]
    kc_doc_out["redundancy_qa_status"] = redundancy["status"]
    with open(kc_path, "w", encoding="utf-8") as f:
        json.dump(kc_doc_out, f, ensure_ascii=False, indent=2)

    with open(f"{OUT_DIR}/manual_finalize_result_summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    return result


if __name__ == "__main__":
    r = main()
    print(json.dumps({
        "canonicalization_status": r["canonicalization"]["status"],
        "redundancy_qa_status": (r["redundancy_qa"] or {}).get("status"),
    }, ensure_ascii=False))
