# ============================================================
# er013_family_c_future_qa_02.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-REDESIGN-TRIAL-02
# ============================================================
# 目的: Trial-01(er013_family_c_future_qa_01.py、無編集で保持)からの
# 再設計(作業A項目4「本文へ出す条件」・項目5「Future Framing QA」・
# 項目6「完成記事の編集Gate」)。
#
# 前回→今回の変更点:
#   - マーカー体系を拡張([[META]]...[[/META]]=内部メモ、完全除去。
#     [[FACT: <ref_id>]]...[[/FACT]]=現在事実の明示的言及の例外枠、
#     最大2件まで機械的にカウント。[[IMAGINED: ...]]...[[/IMAGINED]]は
#     Trial-01から維持、fcq_v1の関数をそのまま再利用)。
#   - 新設: 完成記事の編集Gate(scan_editorial_gate) - 決定的スキャンで
#     (i)統計値・比率・年次データ、(ii)研究・データ解説を示す語、
#     (iii)製品名(World Scaffold抽出リストと突合)、(iv)冒頭段落が
#     場面で始まるか、(v)FACT例外件数の上限、を判定する。
#   - Future Framing QA v2: Trial-01の5項目に加え、6項目目
#     「研究・データ解説っぽさ」(discovery_style_density)をLLMで判定する
#     (決定的スキャン結果を参考情報として渡す)。
#
# 既存Fact Checker A'/Ledger Deviation Checker関数は一切改変しない
# (Trial-01と同じくimport・呼び出しのみ、閾値・スキーマは無変更)。
# Layer1(枠外の現在事実文)に対する厳格チェックの対象範囲・ルーティング
# 方式はTrial-01を踏襲する(指示書§作業A-7、Fact Safetyは緩和しない)。
#
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import json
import re

import er013_family_c_future_qa_01 as fcq_v1  # IMAGINEDマーカー処理は無編集で再利用

IMAGINED_OPEN_PREFIX = fcq_v1.IMAGINED_OPEN_PREFIX
IMAGINED_CLOSE = fcq_v1.IMAGINED_CLOSE
DEFAULT_LAYER1_PLACEHOLDER = fcq_v1.DEFAULT_LAYER1_PLACEHOLDER

META_OPEN = "[[META]]"
META_CLOSE = "[[/META]]"
FACT_OPEN_PREFIX = "[[FACT:"
FACT_CLOSE = "[[/FACT]]"
MAX_FACT_EXCEPTIONS = 2

_META_BLOCK_RE = re.compile(r"\[\[META\]\](?P<body>.*?)\[\[/META\]\]", re.DOTALL)
_FACT_BLOCK_RE = re.compile(r"\[\[FACT:\s*(?P<ref_id>[^\]]*)\]\](?P<body>.*?)\[\[/FACT\]\]", re.DOTALL)


# ------------------------------------------------------------
# META(内部メモ)抽出・除去
# ------------------------------------------------------------
def extract_meta_blocks(article_text: str) -> list:
    return [{"body": m.group("body").strip(), "start": m.start(), "end": m.end()}
            for m in _META_BLOCK_RE.finditer(article_text or "")]


def strip_meta_blocks(article_text: str) -> str:
    """META内部メモを、内容ごと完全に除去する(読者向け本文にも、
    Fact Check/Deviation/Framing QAのいずれにも一切渡さない)。"""
    return _META_BLOCK_RE.sub("", article_text or "")


# ------------------------------------------------------------
# FACT(現在事実の明示的例外)抽出・除去
# ------------------------------------------------------------
def extract_fact_blocks(article_text: str) -> list:
    return [{"ref_id": (m.group("ref_id") or "").strip(), "body": m.group("body").strip(),
             "start": m.start(), "end": m.end()}
            for m in _FACT_BLOCK_RE.finditer(article_text or "")]


def validate_fact_markers_balanced(article_text: str) -> dict:
    text = article_text or ""
    open_count = text.count(FACT_OPEN_PREFIX)
    close_count = text.count(FACT_CLOSE)
    matched_blocks = len(_FACT_BLOCK_RE.findall(text))
    return {"balanced": (open_count == close_count == matched_blocks),
            "open_count": open_count, "close_count": close_count, "matched_blocks": matched_blocks}


def strip_fact_markers_keep_body(article_text: str) -> str:
    """FACTマーカー自体だけを取り除き、内部の文(平易な言い換え)は
    そのまま残す(読者向け本文・Layer1 Fact Check対象テキストの両方で
    使う)。"""
    return _FACT_BLOCK_RE.sub(lambda m: m.group("body"), article_text or "")


def check_fact_markers_inside_imagined(imagined_blocks: list) -> list:
    """[[FACT: ...]]が[[IMAGINED: ...]]の内側に紛れ込んでいないかを確認する
    (設計上、現在事実の明示例外は枠外でのみ使う想定のため、内側に出現した
    場合はissueとして記録する)。"""
    issues = []
    for b in imagined_blocks:
        if FACT_OPEN_PREFIX in b.get("body", ""):
            issues.append({"type": "fact_marker_inside_imagined", "timeframe": b.get("timeframe")})
    return issues


# ------------------------------------------------------------
# ルーティング統合(v2): META除去→IMAGINED抽出(fcq_v1再利用)→
# FACT抽出→reader_text/layer1_textの組み立て。
# ------------------------------------------------------------
def route_article_for_qa_v2(article_text: str, layer1_placeholder: str = DEFAULT_LAYER1_PLACEHOLDER) -> dict:
    meta_blocks = extract_meta_blocks(article_text)
    text_no_meta = strip_meta_blocks(article_text)

    marker_check_imagined = fcq_v1.validate_markers_balanced(text_no_meta)
    imagined_blocks = fcq_v1.extract_imagined_blocks(text_no_meta)
    marker_check_fact = validate_fact_markers_balanced(text_no_meta)
    fact_blocks = extract_fact_blocks(text_no_meta)
    fact_inside_imagined_issues = check_fact_markers_inside_imagined(imagined_blocks)

    reader_text = strip_fact_markers_keep_body(fcq_v1.strip_markers_for_reader(text_no_meta))
    layer1_text_for_fact_check = strip_fact_markers_keep_body(
        fcq_v1.build_layer1_placeholder_text(text_no_meta, placeholder=layer1_placeholder))

    leakage_by_block = []
    for b in imagined_blocks:
        hits = fcq_v1.detect_present_tense_leakage(b["body"])
        if hits:
            leakage_by_block.append({"timeframe": b["timeframe"], "hits": hits})
    unhedged_future_hits = fcq_v1.detect_unhedged_future_claims(layer1_text_for_fact_check)

    return {
        "meta_blocks": meta_blocks,
        "marker_check_imagined": marker_check_imagined,
        "marker_check_fact": marker_check_fact,
        "fact_inside_imagined_issues": fact_inside_imagined_issues,
        "imagined_blocks": imagined_blocks,
        "fact_blocks": fact_blocks,
        "reader_text": reader_text,
        "layer1_text_for_fact_check": layer1_text_for_fact_check,
        "present_tense_leakage_heuristic": leakage_by_block,
        "unhedged_future_claims_outside_markers_heuristic": unhedged_future_hits,
    }


# ============================================================
# 完成記事の編集Gate(新設、決定的スキャン、¥0)
# ============================================================
_DIGIT_TOKEN_RE = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")
_YEAR_ONLY_RE = re.compile(r"^(19|20)\d{2}$")
_RESEARCH_TERMS_RE = re.compile(
    r"\b(stud(?:y|ies)|research(?:ers?)?|surveys?|reports?|scientists?|findings|according to)\b",
    re.IGNORECASE,
)
_SPELLED_NUMBER_RATIO_RE = re.compile(
    r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\s+of\s+"
    r"(one|two|three|four|five|six|seven|eight|nine|ten)\b",
    re.IGNORECASE,
)
DEFAULT_CURRENT_YEAR = 2026  # 未来のtimeframe年(この年より後)は統計とみなさない(EDITORIAL-FUTURE-FAMILY-C-REDESIGN-TRIAL-02実施時点の年)


def _is_allowed_future_year_token(token: str, current_year: int) -> bool:
    stripped = token.replace(",", "")
    m = _YEAR_ONLY_RE.match(stripped)
    if not m:
        return False
    try:
        return int(stripped) > current_year
    except ValueError:
        return False


def scan_numeric_hits(text: str, current_year: int = DEFAULT_CURRENT_YEAR) -> list:
    """統計値・比率・年次データ等の数字を検出する(決定的スキャン)。
    未来のtimeframeとして使われる、current_yearより後の4桁の年単独表記
    (例: "around 2035"の2035)は許容する(統計ではなく時間軸宣言のため)。"""
    hits = []
    for m in _DIGIT_TOKEN_RE.finditer(text or ""):
        token = m.group(0)
        if _is_allowed_future_year_token(token, current_year):
            continue
        lo, hi = max(0, m.start() - 30), min(len(text), m.end() + 30)
        hits.append({"token": token, "context": text[lo:hi].strip()})
    return hits


def scan_research_term_hits(text: str) -> list:
    return [m.group(0) for m in _RESEARCH_TERMS_RE.finditer(text or "")]


def scan_product_name_hits(text: str, banned_product_names: list) -> list:
    lowered = (text or "").lower()
    return [name for name in (banned_product_names or []) if name and name.lower() in lowered]


def get_opening_paragraph(reader_text: str) -> str:
    """先頭の見出し(#で始まる行)・空行をスキップし、最初の本文段落を返す。"""
    lines = (reader_text or "").split("\n")
    collected, started = [], False
    for line in lines:
        stripped = line.strip()
        if not started:
            if not stripped or stripped.startswith("#"):
                continue
            started = True
        if not stripped:
            if collected:
                break
            continue
        collected.append(stripped)
    return " ".join(collected)


_SCENE_CUE_RE = re.compile(
    r"\b(morning|evening|night|tonight|today|weekend|kitchen|home|house|table|"
    r"picture|imagine|you|she|he|they|walk|wake|sit|watch|listen)\b",
    re.IGNORECASE,
)


def scan_editorial_gate(reader_text: str, fact_blocks: list, banned_product_names: list,
                         current_year: int = DEFAULT_CURRENT_YEAR) -> dict:
    """完成記事(読者向け本文)に対する決定的スキャン+ルールベース判定。
    FAILは以下いずれか1つでも該当する場合:
      (i) 統計値・比率・年次データの残存、(ii) 研究・データ解説を示す語、
      (iii) product_names_mentionedとの一致、(iv) FACT例外件数が上限超過、
      (v) 冒頭段落に(i)(ii)が残存。
    冒頭段落の「場面らしさ」(scene cue)は決定的判定には使わない
    heuristic補助情報として記録するのみ(Trial-01 §7 item3の教訓: 正規表現
    ベースの意味論判定は偽陽性のリスクがあるため、blockingにはしない)。"""
    numeric_hits = scan_numeric_hits(reader_text, current_year=current_year)
    research_hits = scan_research_term_hits(reader_text)
    product_hits = scan_product_name_hits(reader_text, banned_product_names)
    spelled_ratio_hits = _SPELLED_NUMBER_RATIO_RE.findall(reader_text or "")

    fact_count = len(fact_blocks or [])
    fact_within_limit = fact_count <= MAX_FACT_EXCEPTIONS

    opening_paragraph = get_opening_paragraph(reader_text)
    opening_numeric_hits = scan_numeric_hits(opening_paragraph, current_year=current_year)
    opening_research_hits = scan_research_term_hits(opening_paragraph)
    opening_scene_cue_heuristic = bool(_SCENE_CUE_RE.search(opening_paragraph))

    fail_reasons = []
    if numeric_hits:
        fail_reasons.append(f"numeric_hits={len(numeric_hits)}")
    if research_hits:
        fail_reasons.append(f"research_term_hits={len(research_hits)}")
    if product_hits:
        fail_reasons.append(f"product_name_hits={product_hits}")
    if not fact_within_limit:
        fail_reasons.append(f"fact_exception_count={fact_count} (limit={MAX_FACT_EXCEPTIONS})")
    if opening_numeric_hits:
        fail_reasons.append(f"opening_paragraph_numeric_hits={len(opening_numeric_hits)}")
    if opening_research_hits:
        fail_reasons.append(f"opening_paragraph_research_hits={len(opening_research_hits)}")

    return {
        "numeric_hits": numeric_hits,
        "research_term_hits": research_hits,
        "product_name_hits": product_hits,
        "spelled_number_ratio_heuristic_hits": spelled_ratio_hits,
        "fact_exception_count": fact_count,
        "fact_exception_within_limit": fact_within_limit,
        "opening_paragraph": opening_paragraph,
        "opening_paragraph_numeric_hits": opening_numeric_hits,
        "opening_paragraph_research_hits": opening_research_hits,
        "opening_paragraph_scene_cue_heuristic": opening_scene_cue_heuristic,
        "overall_status": "FAIL" if fail_reasons else "PASS",
        "fail_reasons": fail_reasons,
    }


# ============================================================
# Future Framing QA v2(新設、LLM 1回。Layer2/3[想像パッセージ]+完成記事の
# 「研究・データ解説っぽさ」を判定。Trial-01の5項目+新設6項目目)。
# ============================================================
FUTURE_FRAMING_QA_V2_DEVELOPER_MESSAGE = (
    "あなたは、記事内の「想像した未来の場面」と、記事全体の構成が場面・"
    "感情・選択を主役にできているかを判定するQA担当者です。想像そのものを"
    "禁止したり、感情的な描写を減点したりしないでください。判定対象は"
    "(1)未来が確定事実として断定されていないか、(2)現在事実の捏造が"
    "ないか、(3)仮定が読み手に分かる形で示されているか、(4)研究・出典・"
    "データ説明が場面の主役になっていないか、(5)未来が本文の他の場所で"
    "確定事実として語られていないか、(6)記事全体が研究・データ解説の"
    "ように読めるか(場面・感情・選択の比率が十分か)、の6点です。"
)

FUTURE_FRAMING_QA_V2_PROMPT_TEMPLATE = """テーマ: {topic}

【Layer 1(現在の事実、参考: この範囲を確定事実として使ってよい)】
{layer1_reference_text}

【判定対象1: 想像した未来のパッセージ(記事から抽出、番号付き)】
{imagined_blocks_text}

【判定対象2: 完成記事の読者向け本文全文(マーカー除去済み)】
{reader_text}

【参考: 決定的スキャンの結果(数字・研究語の残存件数。この結果を鵜呑みに
せず、あなた自身でも文脈から判定してください)】
{deterministic_scan_summary}

上記を踏まえ、以下6項目を判定してください:
1. framing_violations: 想像パッセージ内で、未来が確定事実であるかの
   ように断定されている箇所。
2. fabricated_present_facts: 想像パッセージ内に紛れ込んだ、Layer 1の
   現在の事実と矛盾する、または裏付けのない「現在は既に〜だ」という
   現在時制の主張。
3. unlabeled_assumptions: 想像の前提となる仮定が、本文中で読み手に
   分かる形で示されていない箇所。
4. discovery_style_leakage: 研究・出典・サンプルサイズ・方法論の説明が、
   想像パッセージの主役になっている箇所。
5. future_stated_as_fact_outside_scenes: 想像パッセージ以外の部分で、
   未来が確定事実として断定されている箇所。
6. discovery_style_density: 記事全体(読者向け本文全文)が、場面・感情・
   選択ではなく、研究・データ解説として読める箇所(冒頭が統計や調査結果の
   説明から始まっている、製品名・仕様の列挙が前に出ている、Research結果を
   読者へ説明する構造になっている、等)。該当箇所があれば具体的に引用して
   ください。

該当箇所がなければ、その配列は空にしてください。overall_statusは、
1つでも明確な該当箇所があればREVIEW_REQUIRED、深刻な断定・捏造・研究
解説化が複数あればFAIL、いずれもなければPASSとしてください。"""


FUTURE_FRAMING_QA_V2_JSON_SCHEMA = {
    "name": "family_c_future_framing_qa_v2",
    "schema": {
        "type": "object",
        "properties": {
            "framing_violations": {
                "type": "array",
                "items": {"type": "object", "properties": {"claim": {"type": "string"}, "issue": {"type": "string"}},
                          "required": ["claim", "issue"], "additionalProperties": False},
            },
            "fabricated_present_facts": {
                "type": "array",
                "items": {"type": "object", "properties": {"claim": {"type": "string"}, "issue": {"type": "string"}},
                          "required": ["claim", "issue"], "additionalProperties": False},
            },
            "unlabeled_assumptions": {
                "type": "array",
                "items": {"type": "object", "properties": {"claim": {"type": "string"}, "issue": {"type": "string"}},
                          "required": ["claim", "issue"], "additionalProperties": False},
            },
            "discovery_style_leakage": {
                "type": "array",
                "items": {"type": "object", "properties": {"claim": {"type": "string"}, "issue": {"type": "string"}},
                          "required": ["claim", "issue"], "additionalProperties": False},
            },
            "future_stated_as_fact_outside_scenes": {
                "type": "array",
                "items": {"type": "object", "properties": {"claim": {"type": "string"}, "issue": {"type": "string"}},
                          "required": ["claim", "issue"], "additionalProperties": False},
            },
            "discovery_style_density": {
                "type": "array",
                "items": {"type": "object", "properties": {"claim": {"type": "string"}, "issue": {"type": "string"}},
                          "required": ["claim", "issue"], "additionalProperties": False},
            },
            "overall_status": {"type": "string", "enum": ["PASS", "REVIEW_REQUIRED", "FAIL"]},
        },
        "required": ["framing_violations", "fabricated_present_facts", "unlabeled_assumptions",
                     "discovery_style_leakage", "future_stated_as_fact_outside_scenes",
                     "discovery_style_density", "overall_status"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_future_framing_qa_v2_prompt(topic: str, layer1_reference_text: str, imagined_blocks: list,
                                       reader_text: str, deterministic_scan_summary: str) -> str:
    blocks_text = "\n\n".join(
        f"[{i + 1}] (timeframe: {b['timeframe']})\n{b['body']}" for i, b in enumerate(imagined_blocks)
    ) or "(想像パッセージなし)"
    return FUTURE_FRAMING_QA_V2_PROMPT_TEMPLATE.format(
        topic=topic, layer1_reference_text=layer1_reference_text, imagined_blocks_text=blocks_text,
        reader_text=reader_text, deterministic_scan_summary=deterministic_scan_summary)


def run_future_framing_qa_v2(client, topic: str, layer1_reference_text: str, imagined_blocks: list,
                              reader_text: str, deterministic_scan_summary: str, model: str,
                              reasoning_effort: str) -> dict:
    prompt = build_future_framing_qa_v2_prompt(
        topic, layer1_reference_text, imagined_blocks, reader_text, deterministic_scan_summary)
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **FUTURE_FRAMING_QA_V2_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": FUTURE_FRAMING_QA_V2_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    parsed = json.loads(text)
    return {"prompt": prompt, "raw_text": text, "parsed": parsed,
            "model": response.model, "response_id": response.id}
