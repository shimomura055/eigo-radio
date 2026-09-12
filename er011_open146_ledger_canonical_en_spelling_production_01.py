# ============================================================
# er011_open146_ledger_canonical_en_spelling_production_01.py
# OPEN-146-LEDGER-CANONICAL-EN-SPELLING-PRODUCTION-WIRING-01
# ============================================================
# 目的: 「日本語情報源由来のLedgerに日本語表記しかない固有名詞を、Writerが
# 実行ごとに推測でローマ字化し、Fact Checkerに到達しなければ検出されない」
# というfailure mode(FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-TRIAL-
# DESIGN-01で定義、FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15で
# 候補(a)がVALIDATED)への、ユーザー承認済み(2026-09-12「#12 A-Family /
# News Ledger公式英語表記のProduction採用⇒採用」、`APPROVED_FOR_
# PRODUCTION`)Production配線。詳細はCURRENT_SPEC.md「Cross-level仕様」
# 節「Ledger canonical_en_spelling」行を参照。
#
# 設計方針(Trial-15の実証済み方式をそのまま踏襲し、既存Production関数
# 本体[build_common_block/COMMON_BLOCK_TEMPLATE/r3.make_writer_research_fn]
# は一切改変しない):
#
# 1. Verified Fact LedgerのSchemaへ`canonical_en_spelling: <日本語表記> =
#    <English>`行(任意フィールド)を追加する。既存Ledger(この行が無い
#    もの)には一切影響しない(本モジュールの全関数は、この行が無い
#    Ledgerに対して常にno-op/空文字列を返す=英語一次情報源テーマ
#    [Health/Household等]では発火しない)。
# 2. Research/Ledger作成は現状、自動Pythonパイプラインではなく、Ledger
#    作成担当(Sonnet)がWebSearch/WebFetchで手動作成する運用である
#    (CURRENT_SPEC.md「News Editorial Mode」節「Research/Ledger供給経路」
#    行、FAMILY-A-NEWS-JA-PERSON-NAME-ROMANIZATION-TRIAL-DESIGN-01 1-2節
#    で確認済み。`generate_test.py`のNAME_GLOSSARY機構は無関係な別番組
#    専用スクリプトの死蔵コードであり、現行Production経路には存在しない)。
#    よって本モジュールは「Ledger作成時に呼び出す再利用可能な関数群」
#    として提供し、存在しない自動生成パイプラインへの自動フック配線は
#    行わない。次回News Ledger作成時からこれらの関数を使うことを、Ledger
#    作成のSOPとしてCURRENT_SPEC.mdに明記する。
# 3. Writerへの伝達は、build_common_block()/COMMON_BLOCK_TEMPLATEを一切
#    変更せず、Ledgerテキスト自体に1文追記する(Trial-15と同一方式)。
#    これにより、この行が無いLedgerではbuild_common_block()の出力は
#    完全にbyte不変のまま(呼び出し元がverified_ledger_text引数へ渡す
#    テキスト自体が変わらないため)。
# 4. Fact Checkerには、r3.build_fact_check_prompt()への後方互換オプション
#    引数(canonical_spelling_block、既定""、OPEN-131のvoice_attribution_
#    blockと同型パターン)として、canonical_en_spelling一覧との照合依頼を
#    追加する。既定""の場合、r3.build_fact_check_prompt()の出力は本引数
#    追加以前とbyte単位で完全に同一。
#
# API呼び出し(Web検索・LLM)はこのモジュールの関数を実際に呼び出した
# 時のみ発生する(import時・テスト時には一切発生しない)。テストでは
# client/researchやextraction関数をモックで注入する。
# ============================================================
from __future__ import annotations

import json
import re
from typing import Any, Optional

import er002_ja_free_markdown_restore as restore
import er002_ja_web_research_r3 as r3

# ============================================================
# ブロック1: Ledger内の既存canonical_en_spelling行の検出・抽出
# ============================================================
LEDGER_CANONICAL_FIELD_RE = re.compile(
    r"^canonical_en_spelling:\s*(?P<ja>.+?)\s*=\s*(?P<en>.+?)\s*$", re.MULTILINE)


def has_canonical_en_spelling(ledger_text: str) -> bool:
    """Ledger本文に`canonical_en_spelling:`行が1つでもあるかを判定する。
    英語一次情報源テーマ(Health/Household等)のLedgerにはこの行が登場
    しないため、常にFalseを返す(非発火)。"""
    return bool(LEDGER_CANONICAL_FIELD_RE.search(ledger_text))


def extract_canonical_en_spelling_entries(ledger_text: str) -> list[dict]:
    """Ledger本文から`canonical_en_spelling: <ja> = <en>`行をすべて抽出する。
    無ければ空リストを返す。"""
    return [{"ja": m.group("ja").strip(), "en": m.group("en").strip()}
            for m in LEDGER_CANONICAL_FIELD_RE.finditer(ledger_text)]


# ============================================================
# ブロック2: Writerへの伝達(Ledgerテキストへの1文追記のみ。
# build_common_block()/COMMON_BLOCK_TEMPLATEは無改変)。文言は
# FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15の
# HARNESS_INSTRUCTION_SENTENCEとbyte単位で完全に同一(Trial-15の実証済み
# 文言をそのまま踏襲し、再検証なしの文言変更を避ける。ヘッダーの
# "Trial-15"表記も含め無変更)。
# ============================================================
CANONICAL_SPELLING_WRITER_INSTRUCTION = (
    "\n\n=== 固有名詞の英語表記について(Trial-15、Ledger内での伝達) ===\n"
    "このLedgerに`canonical_en_spelling: <日本語表記> = <English>`という形式で\n"
    "記載がある固有名詞は、必ずこの英語表記をそのまま使用すること。自己判断で\n"
    "別のローマ字表記を作らないこと。\n"
)


def append_canonical_spelling_instruction_if_present(ledger_text: str) -> str:
    """Ledger本文に`canonical_en_spelling:`行がある場合のみ、Writerへの
    伝達用1文を末尾へ追記する。無い場合はledger_textをそのまま返す
    (byte不変)。呼び出し側(er003_v1_n3_01_articles_generate.py::
    run_theme())は、load_text(theme["ledger_path"])の結果をこの関数へ
    通してからbuild_common_block()へ渡す。"""
    if not has_canonical_en_spelling(ledger_text):
        return ledger_text
    return ledger_text + CANONICAL_SPELLING_WRITER_INSTRUCTION


# ============================================================
# ブロック3: Fact Checkerへの照合項目追加。
# r3.build_fact_check_prompt()の後方互換オプション引数として渡す。
# ============================================================
def build_canonical_spelling_fact_check_block(ledger_text: str) -> str:
    """Ledgerにcanonical_en_spelling行がある場合のみ、Fact Checkerプロンプト
    末尾へ追記する照合依頼ブロックを構築する。無い場合は""を返す
    (r3.build_fact_check_prompt()のcanonical_spelling_block引数は既定""
    のため、この場合Fact Checkerプロンプトは本機能追加以前とbyte単位で
    完全に同一)。"""
    entries = extract_canonical_en_spelling_entries(ledger_text)
    if not entries:
        return ""
    lines = [
        "【固有名詞の英語表記についての確認事項】",
        "以下はVerified Fact Ledgerに記載された、確認済みの公式英語表記です。"
        "記事本文中の対応する固有名詞の綴りがこの表記と一致しているか確認し、"
        "異なる場合はcontradictionsに具体的に記載してください。",
    ]
    for e in entries:
        lines.append(f"- {e['ja']} = {e['en']}")
    return "\n".join(lines)


# ============================================================
# ブロック4: 固有名詞抽出(最小実装)。既存entity抽出機構は現行
# Production経路に存在しないことを確認済み(FAMILY-A-NEWS-JA-PERSON-
# NAME-ROMANIZATION-TRIAL-DESIGN-01 1節。`generate_test.py`のNAME_
# GLOSSARY機構は無関係な別番組専用スクリプトの死蔵コードであり、現行
# Production経路には引き継がれていない)。よって最小実装として、Web検索
# ツールを使わない通常のLLM呼び出し1回でLedger本文から日本語固有名詞
# 候補を抽出する(Web検索confirmationより低コスト)。英語一次情報源
# テーマ(Health/Household等)ではLedger本文に日本語固有名詞が登場しない
# ため、モデルは空リストを返すことが期待され、以降のWeb検索research
# 呼び出しへは進まない(=追加費用が発生しない)。
# ============================================================
PROPER_NOUN_EXTRACTION_PROMPT_TEMPLATE = """以下はニュース記事のVerified Fact Ledger本文です。この中から、
日本語表記でしか記載されていない固有名詞(人名・チーム/組織名・地名・
施設名など)で、英語記事本文へ変換する際にローマ字表記が一意に定まらない
可能性があるものだけを抽出してください。

対象外(抽出しないこと):
- 既に本文中に英語表記(アルファベット)が併記されている固有名詞
- 一般名詞・役職名・普通名詞
- 英語圏の人名・組織名(そもそも日本語表記の問題がないため)

Ledger本文:
{ledger_text}

出力形式(厳守、他の説明文は書かない): 対象が無ければ{{"entities": []}}を
返してください。対象がある場合は以下のJSON形式のみで出力してください。

{{"entities": [{{"ja": "<日本語表記>", "context": "<何者か、検索の手掛かりになる短い説明>"}}]}}
"""


def build_proper_noun_extraction_prompt(ledger_text: str) -> str:
    return PROPER_NOUN_EXTRACTION_PROMPT_TEMPLATE.format(ledger_text=ledger_text)


class ProperNounExtractionSchemaError(ValueError):
    """固有名詞抽出LLM応答がJSONとして解析できない、または期待するschema
    (entities配列、各要素にja/context)を満たさない場合。"""


def parse_proper_noun_extraction_output(raw_text: str) -> list[dict]:
    try:
        parsed = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError) as e:
        raise ProperNounExtractionSchemaError(f"JSON解析に失敗しました: {e}") from e
    if not isinstance(parsed, dict) or "entities" not in parsed or not isinstance(parsed["entities"], list):
        raise ProperNounExtractionSchemaError("'entities'配列がありません")
    entities = []
    for item in parsed["entities"]:
        if not isinstance(item, dict) or "ja" not in item:
            raise ProperNounExtractionSchemaError(f"entities要素の形式が不正です: {item!r}")
        entities.append({"ja": str(item["ja"]).strip(), "context": str(item.get("context", "")).strip()})
    return entities


def make_proper_noun_extraction_fn(ledger_text: str, client: Optional[Any] = None,
                                    model: str = r3.WRITER_MODEL,
                                    reasoning_effort: str = "medium"):
    """Web検索ツールを使わない通常のLLM呼び出し関数を返す。戻り値は
    (raw_text, model, response_id)の3値タプル。reasoning_effortの既定は
    "medium"(単純な抽出タスクのため、r3.WRITER_REASONING_EFFORT="high"
    より低コストな値を明示指定。Trial-15のconfirmation呼び出しと同じ
    "medium"に揃えた。関数自体の既定引数のみであり、r3.WRITER_REASONING_
    EFFORT自体は無変更)。"""
    if client is None:
        from dotenv import load_dotenv
        load_dotenv()
        from openai import OpenAI
        client = OpenAI()

    prompt = build_proper_noun_extraction_prompt(ledger_text)

    def extraction_fn():
        response = client.responses.create(
            model=model,
            reasoning={"effort": reasoning_effort},
            input=[
                {"role": "developer", "content": r3.NEUTRAL_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
        text = getattr(response, "output_text", None)
        if not text or not text.strip():
            raise restore.GenerationEmptyOrBrokenError("固有名詞抽出応答が空です")
        return text, response.model, response.id

    extraction_fn.model = model
    extraction_fn.reasoning_effort = reasoning_effort
    extraction_fn.uses_web_search_tool = False
    return extraction_fn


# ============================================================
# ブロック5: 公式英語表記confirmation(Web検索)。既存Production関数
# r3.make_writer_research_fn()を無改変で再利用する
# (FAMILY-A-NEWS-LEDGER-CANONICAL-EN-SPELLING-TRIAL-15 段階1と同一方式、
# 対象entitiesのみTrial-15の固定10件からLedger本文由来の可変集合へ
# 一般化した)。
# ============================================================
RESEARCH_INSTRUCTION_TEMPLATE = """あなたは固有名詞の英語表記調査担当です。以下の日本語の固有名詞
それぞれについて、公式サイト・一次情報源(該当する場合はNPB公式・
球団公式サイト・政府/自治体公式サイト等)をWeb検索で確認し、英語圏の
報道・公式表記で実際に使われている公式な英語表記(ローマ字表記)を
1件ずつ特定してください。

対象一覧:
{entity_list}

出力形式(厳守、他の説明文は書かない): 対象1件につき1行、以下の形式
のみで出力してください。

CANONICAL: <日本語表記> = <English Spelling> | SOURCE: <確認したURL>

複数の情報源で表記が割れている場合は、最も公式性の高い情報源を優先し、
その理由をSOURCE列の後に括弧書きで簡潔に添えてください。
"""


def build_research_instruction(entities: list[dict]) -> str:
    entity_list = "\n".join(
        f"- {e['ja']}({e['context']})" if e.get("context") else f"- {e['ja']}"
        for e in entities)
    return RESEARCH_INSTRUCTION_TEMPLATE.format(entity_list=entity_list)


CANONICAL_LINE_RE = re.compile(
    r"CANONICAL:\s*(?P<ja>.+?)\s*=\s*(?P<en>.+?)\s*\|\s*SOURCE:\s*(?P<rest>.+)$")


def parse_canonical_research_lines(text: str) -> list[dict]:
    parsed = []
    for line in text.splitlines():
        line = line.strip()
        m = CANONICAL_LINE_RE.match(line)
        if not m:
            continue
        rest = m.group("rest").strip()
        url_match = re.match(r"(\S+)", rest)
        url = url_match.group(1) if url_match else rest
        note = rest[len(url):].strip() if url_match else ""
        parsed.append({"ja": m.group("ja").strip(), "en": m.group("en").strip(),
                        "url": url, "note": note})
    return parsed


def run_canonical_spelling_research(entities: list[dict], client: Optional[Any] = None) -> dict:
    """既存Production関数r3.make_writer_research_fn()を無改変で再利用し、
    1回のAPI実行内でentities全件の公式英語表記をWeb検索で確認する
    (Trial-15段階1と同一方式)。entitiesが空リストの場合は、API呼び出しを
    一切行わず空の結果を返す(英語一次情報源テーマでの不要な検索費用を
    避ける=非発火)。"""
    if not entities:
        return {"raw_text": None, "model": None, "response_id": None,
                "search_usage": None, "sources": [], "parsed": [], "skipped": True}
    user_message = build_research_instruction(entities)
    research_fn = r3.make_writer_research_fn(user_message, client=client, reasoning_effort="medium")
    text, model, response_id, search_usage, sources = research_fn()
    parsed = parse_canonical_research_lines(text)
    return {"raw_text": text, "model": model, "response_id": response_id,
            "search_usage": search_usage, "sources": sources, "parsed": parsed, "skipped": False}


# ============================================================
# ブロック6: Ledger本文への追記(Ledger作成担当が使う。存在しない
# 自動生成パイプラインへの自動フックは行わない、CURRENT_SPEC.md参照)。
# ============================================================
def build_canonical_spelling_ledger_section(canonical_entries: list[dict]) -> str:
    """Web検索で確認したcanonical_entries([{"ja","en",...}, ...])から、
    Verified Fact Ledger本文の末尾へ追記する`canonical_en_spelling:`
    セクションを構築する。空リストの場合は""を返す。"""
    if not canonical_entries:
        return ""
    lines = [
        "", "=== 固有名詞の公式英語表記(Web検索で確認済み) ===",
        "作成方法: Ledger本文中の日本語固有名詞に対し、Web検索"
        "(WRITER_MODELのweb_searchツール)で公式英語表記を確認した。", "",
    ]
    for e in canonical_entries:
        lines.append(f"canonical_en_spelling: {e['ja']} = {e['en']}")
    return "\n".join(lines) + "\n"


def append_canonical_spelling_section(ledger_text: str, canonical_entries: list[dict]) -> str:
    """Ledger本文の末尾へcanonical_en_spellingセクションを追記する。
    canonical_entriesが空の場合はledger_textをそのまま返す(byte不変)。"""
    section = build_canonical_spelling_ledger_section(canonical_entries)
    if not section:
        return ledger_text
    return ledger_text + "\n" + section
