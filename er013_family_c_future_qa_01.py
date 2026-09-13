# ============================================================
# er013_family_c_future_qa_01.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-PROTOTYPE-TRIAL-01
# ============================================================
# 目的: Family C(Future)記事本文中の想像パッセージ([[IMAGINED: ...]]
# ... [[/IMAGINED]]マーカーで区切られた部分)を機械的に抽出し、
#   (a) Layer 1(枠外の現在事実文)のみを既存Fact Checker A'
#       (er002_ja_web_research_r3.py)・既存Ledger Deviation Checker
#       (er003_v1_en_direct_vfl_01_generate.py::run_deviation_check)へ
#       渡すための「想像パッセージをプレースホルダ化した本文」を作る、
#   (b) 読者向け最終本文(マーカー除去済み、自然な語りのまま)を作る、
#   (c) Layer 2/3(想像パッセージ)向けの新設Future Framing QAを実行する、
# ためのルーティング関数群を提供する。
#
# 既存Fact Checker A'/Ledger Deviation Checker関数は一切改変しない
# (import・呼び出しのみ、閾値・スキーマは無変更)。本ファイルはルーティング
# 層のみを新設する(EDITORIAL-FUTURE-ARTICLE-DESIGN-01_REPORT.md §3-3
# 案(a): Writerに明示マーカーで区切らせ、QA側で機械的に抽出する方式)。
#
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import json
import re
from typing import Optional

IMAGINED_OPEN_PREFIX = "[[IMAGINED:"
IMAGINED_CLOSE = "[[/IMAGINED]]"

# [[IMAGINED: <timeframe>]] ... [[/IMAGINED]] を非貪欲・複数行対応で抽出する。
_IMAGINED_BLOCK_RE = re.compile(
    r"\[\[IMAGINED:\s*(?P<timeframe>[^\]]*)\]\](?P<body>.*?)\[\[/IMAGINED\]\]",
    re.DOTALL,
)

DEFAULT_LAYER1_PLACEHOLDER = "(この段落は想像した未来の場面のため、Fact Check対象から除外されています。)"


def extract_imagined_blocks(article_text: str) -> list:
    """本文中の[[IMAGINED: ...]]...[[/IMAGINED]]ブロックを全て抽出する。
    戻り値は各ブロックの{timeframe, body, start, end}のリスト(出現順)。
    bodyは前後の空白のみstripし、内部の改行・文章はそのまま保持する
    (読者向け本文の語りをそのまま評価できるようにするため)。"""
    blocks = []
    for m in _IMAGINED_BLOCK_RE.finditer(article_text or ""):
        blocks.append({
            "timeframe": (m.group("timeframe") or "").strip(),
            "body": m.group("body").strip(),
            "start": m.start(), "end": m.end(),
        })
    return blocks


def validate_markers_balanced(article_text: str) -> dict:
    """開始・終了マーカーの数が一致しているか、入れ子・重複がないかを
    機械的に確認する。マーカー抽出ロジックが暗黙に前提とする条件を
    明示的に検証する(不一致があれば、抽出結果を信頼せずSTOPすべき)。"""
    text = article_text or ""
    open_count = text.count(IMAGINED_OPEN_PREFIX)
    close_count = text.count(IMAGINED_CLOSE)
    matched_blocks = len(_IMAGINED_BLOCK_RE.findall(text))
    balanced = (open_count == close_count == matched_blocks)
    return {
        "balanced": balanced, "open_count": open_count, "close_count": close_count,
        "matched_blocks": matched_blocks,
    }


def strip_markers_for_reader(article_text: str) -> str:
    """マーカー自体だけを取り除き、内部の語り本文(自然な導入文を含む)は
    そのまま残す。読者向け最終本文はこの関数の出力を使う。"""
    def _replace(m: "re.Match") -> str:
        return m.group("body")
    return _IMAGINED_BLOCK_RE.sub(_replace, article_text or "")


def build_layer1_placeholder_text(article_text: str, placeholder: str = DEFAULT_LAYER1_PLACEHOLDER) -> str:
    """想像パッセージ全体(マーカーごと)をプレースホルダへ置換した本文を
    作る。既存Fact Checker A'・Ledger Deviation Checkerには、この関数の
    出力(記事全文ではなく枠外テキストのみ)を渡す設計(想像した具体的な
    未来像がunsupported_new_claim/changed_certaintyとして誤検知される
    ことを、閾値緩和ではなくルーティングで防ぐ)。"""
    def _replace(m: "re.Match") -> str:
        return placeholder
    return _IMAGINED_BLOCK_RE.sub(_replace, article_text or "")


# ------------------------------------------------------------
# 想像パッセージ内の現在事実の紛れ込み検出(heuristic regex、
# Future Framing QA[LLM]の判定を補助する一次スクリーニング。
# これ自体はFact Checker A'の代替ではなく、見落とし防止用の追加信号)。
# ------------------------------------------------------------
_PRESENT_LEAKAGE_TRIGGER_RE = re.compile(
    r"\b(already|currently|as of (?:today|now|this year)|right now|today)\b",
    re.IGNORECASE,
)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def detect_present_tense_leakage(block_body: str) -> list:
    """想像パッセージ本文内で、「現在は既に〜だ」型の現在事実主張が
    紛れ込んでいる疑いのある箇所を検出する(heuristic、文単位で
    already/today/currently等のトリガー語を含む文を抽出する一次
    スクリーニング。verbとトリガー語の語順を問わない。最終判定は
    Future Framing QA[LLM]が行う)。"""
    body = block_body or ""
    sentences = _SENTENCE_SPLIT_RE.split(body) if body else []
    return [s.strip() for s in sentences if s.strip() and _PRESENT_LEAKAGE_TRIGGER_RE.search(s)]


# ------------------------------------------------------------
# 枠外(Layer 1)での未来断定検出(heuristic regex、item(5)の一次
# スクリーニング。厳密な意味論判定はFuture Framing QA[LLM]に委ねる)。
# ------------------------------------------------------------
_HEDGE_WORDS_RE = re.compile(
    r"\b(may|might|could|would|possibly|perhaps|if|one possible|imagine|picture|"
    r"suppose|likely|expect(?:ed)?|forecast|predict(?:ed|ion)?|scenario)\b",
    re.IGNORECASE,
)
_UNHEDGED_FUTURE_RE = re.compile(r"\bwill\b", re.IGNORECASE)


def detect_unhedged_future_claims(layer1_placeholder_text: str, window: int = 80) -> list:
    """枠外(Layer1プレースホルダ後の本文)で"will"が使われている文の
    前後windowにhedge語が見当たらない箇所を検出する(heuristic)。
    確定事実化の疑いがある箇所の一次スクリーニングであり、最終判定は
    Future Framing QA(LLM)が行う。"""
    text = layer1_placeholder_text or ""
    hits = []
    for m in _UNHEDGED_FUTURE_RE.finditer(text):
        lo, hi = max(0, m.start() - window), min(len(text), m.end() + window)
        context = text[lo:hi]
        if not _HEDGE_WORDS_RE.search(context):
            hits.append(context.strip())
    return hits


def route_article_for_qa(article_text: str, layer1_placeholder: str = DEFAULT_LAYER1_PLACEHOLDER) -> dict:
    """記事全文から、(a)読者向け最終本文、(b)Fact Check/Deviation Check
    へ渡すLayer1限定テキスト(想像パッセージをプレースホルダ化)、
    (c)想像パッセージ一覧、(d)マーカー整合性チェック結果、(e)heuristic
    一次スクリーニング結果、をまとめて返す。"""
    marker_check = validate_markers_balanced(article_text)
    imagined_blocks = extract_imagined_blocks(article_text)
    reader_text = strip_markers_for_reader(article_text)
    layer1_text = build_layer1_placeholder_text(article_text, placeholder=layer1_placeholder)

    leakage_by_block = []
    for b in imagined_blocks:
        hits = detect_present_tense_leakage(b["body"])
        if hits:
            leakage_by_block.append({"timeframe": b["timeframe"], "hits": hits})

    unhedged_future_hits = detect_unhedged_future_claims(layer1_text)

    return {
        "marker_check": marker_check,
        "imagined_blocks": imagined_blocks,
        "reader_text": reader_text,
        "layer1_text_for_fact_check": layer1_text,
        "present_tense_leakage_heuristic": leakage_by_block,
        "unhedged_future_claims_outside_markers_heuristic": unhedged_future_hits,
    }


# ============================================================
# Future Framing QA(新設、LLM 1回。Layer 2/3[想像パッセージ]専用)
# ============================================================
FUTURE_FRAMING_QA_DEVELOPER_MESSAGE = (
    "あなたは、記事内の「想像した未来の場面」だけを対象に、事実と想像の"
    "区別が適切に保たれているかを判定するQA担当者です。想像そのものを"
    "禁止したり、感情的な描写を減点したりしないでください。判定対象は"
    "あくまで(1)未来が確定事実として断定されていないか、(2)現在事実の"
    "捏造がないか、(3)仮定が読み手に分かる形で示されているか、"
    "(4)研究・出典・データ説明が場面の主役になっていないか、"
    "(5)未来が本文の他の場所で確定事実として語られていないか、の5点です。"
)

FUTURE_FRAMING_QA_PROMPT_TEMPLATE = """テーマ: {topic}

【Layer 1(現在の事実、参考: この範囲を確定事実として使ってよい)】
{layer1_reference_text}

【判定対象: 想像した未来のパッセージ(記事から抽出、番号付き)】
{imagined_blocks_text}

【記事全文中でこれらの想像パッセージ以外の部分(枠外)からの抜粋、
未来を断定的に語っていないかの参考用】
{layer1_body_excerpt}

上記を踏まえ、以下5項目を判定してください:
1. framing_violations: 想像パッセージ内で、未来が確定事実であるかの
   ように断定されている箇所(「これは想像・予測である」と読み手が
   理解できない書き方になっている箇所)。
2. fabricated_present_facts: 想像パッセージ内に紛れ込んだ、Layer 1の
   現在の事実と矛盾する、または裏付けのない「現在は既に〜だ」という
   現在時制の主張。
3. unlabeled_assumptions: 想像の前提となる仮定が、本文中で読み手に
   分かる形で示されていない箇所(暗黙の仮定のまま断定している箇所)。
4. discovery_style_leakage: 研究・出典・サンプルサイズ・方法論の説明が、
   想像パッセージの主役になっている箇所。
5. future_stated_as_fact_outside_scenes: 枠外の抜粋の中で、未来が
   確定事実として断定されている箇所。

該当箇所がなければ、その配列は空にしてください。overall_statusは、
1つでも明確な該当箇所があればREVIEW_REQUIRED、深刻な断定・捏造が
複数あればFAIL、いずれもなければPASSとしてください。"""


FUTURE_FRAMING_QA_JSON_SCHEMA = {
    "name": "family_c_future_framing_qa_v1",
    "schema": {
        "type": "object",
        "properties": {
            "framing_violations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"claim": {"type": "string"}, "issue": {"type": "string"}},
                    "required": ["claim", "issue"], "additionalProperties": False,
                },
            },
            "fabricated_present_facts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"claim": {"type": "string"}, "issue": {"type": "string"}},
                    "required": ["claim", "issue"], "additionalProperties": False,
                },
            },
            "unlabeled_assumptions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"claim": {"type": "string"}, "issue": {"type": "string"}},
                    "required": ["claim", "issue"], "additionalProperties": False,
                },
            },
            "discovery_style_leakage": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"claim": {"type": "string"}, "issue": {"type": "string"}},
                    "required": ["claim", "issue"], "additionalProperties": False,
                },
            },
            "future_stated_as_fact_outside_scenes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"claim": {"type": "string"}, "issue": {"type": "string"}},
                    "required": ["claim", "issue"], "additionalProperties": False,
                },
            },
            "overall_status": {"type": "string", "enum": ["PASS", "REVIEW_REQUIRED", "FAIL"]},
        },
        "required": ["framing_violations", "fabricated_present_facts", "unlabeled_assumptions",
                     "discovery_style_leakage", "future_stated_as_fact_outside_scenes", "overall_status"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_future_framing_qa_prompt(topic: str, layer1_reference_text: str, imagined_blocks: list,
                                    layer1_body_excerpt: str) -> str:
    blocks_text = "\n\n".join(
        f"[{i + 1}] (timeframe: {b['timeframe']})\n{b['body']}" for i, b in enumerate(imagined_blocks)
    ) or "(想像パッセージなし)"
    return FUTURE_FRAMING_QA_PROMPT_TEMPLATE.format(
        topic=topic, layer1_reference_text=layer1_reference_text,
        imagined_blocks_text=blocks_text, layer1_body_excerpt=layer1_body_excerpt)


def run_future_framing_qa(client, topic: str, layer1_reference_text: str, imagined_blocks: list,
                           layer1_body_excerpt: str, model: str, reasoning_effort: str) -> dict:
    """Future Framing QA(新設、Layer2/3専用)。web_search toolは使わない
    (内部整合性の判定のみであり、新規調査は行わない)。"""
    prompt = build_future_framing_qa_prompt(topic, layer1_reference_text, imagined_blocks, layer1_body_excerpt)
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **FUTURE_FRAMING_QA_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": FUTURE_FRAMING_QA_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    parsed = json.loads(text)
    return {"prompt": prompt, "raw_text": text, "parsed": parsed,
            "model": response.model, "response_id": response.id}
