# ============================================================
# er008_shared_point_blueprint_01.py
# A2/B1 Point Structure Semantic Alignment: Shared Point Blueprint
# ============================================================
# ER-008-A2-STORY-B1-SUPPORT-COMPATIBILITY-AUDIT-01(OPEN-63)で発見された
# 「A2/B1のWriterが独立にPoint One/Twoへfactを振り分けるため、Point構造が
# レベル間で食い違う」問題を、生成前の共通設計で防止するためのSchema。
#
# 設計方針(タスク仕様の中心Decision): 互換性を後段Checkerで担保するの
# ではなく、Shared Point BlueprintをSingle Source of Truthとして生成元で
# 担保する。A2/B1は文章・語数・情報量までは共通化しない(各CEFRレベルへ
# 独立最適化されたままでよい)。共通化するのは「どのFactがどちらの
# Pointに属するか」という意味構造だけ。
#
# fact_idはVerified Fact Ledgerの各Factが持つfact_id(例: "FACT-007")を
# そのまま参照する(er003_v1_en_direct_vfl_01_generate.build_verified_
# ledger_text()が"[VERIFIED] FACT-007: ..."の形でWriterへ渡している既存
# 値と同一の文字列)。新しいID体系は導入しない。
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict


# ============================================================
# Schema(dataclass)
# ============================================================
@dataclass
class PointBlueprint:
    role: str  # このPointが記事全体で担う役割(例: "背景となる研究結果とその中心的な発見")
    common_claim: str  # A2・B1の両方に残す中心結論
    common_fact_ids: list = field(default_factory=list)  # 両レベルで扱う代表的fact_id
    optional_b1_fact_ids: list = field(default_factory=list)  # B1だけで扱ってよい追加根拠のfact_id
    required_in_a2_fact_ids: list = field(default_factory=list)  # common_fact_idsのうちA2に必須のもの(subset)
    comment_anchor: str = ""  # このPoint後の共通Commentが参照してよい内容の要約
    prohibited_reference_fact_ids: list = field(default_factory=list)  # この時点では未提示、参照するとネタバレになるfact_id(通常はPoint 2以降のfact_id)


@dataclass
class SharedPointBlueprint:
    topic_id: str
    point_1: PointBlueprint
    point_2: PointBlueprint
    point_transition: str = ""  # 任意: Point1->Point2の関係(例: "研究結果 -> 意味・応用")


def blueprint_to_dict(bp: SharedPointBlueprint) -> dict:
    return asdict(bp)


def blueprint_from_dict(d: dict) -> SharedPointBlueprint:
    return SharedPointBlueprint(
        topic_id=d["topic_id"],
        point_1=PointBlueprint(**d["point_1"]),
        point_2=PointBlueprint(**d["point_2"]),
        point_transition=d.get("point_transition", ""),
    )


# ============================================================
# LLM構造化出力用JSON Schema(Blueprint生成呼び出し用)
# ============================================================
def _point_blueprint_json_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "role": {"type": "string"},
            "common_claim": {"type": "string"},
            "common_fact_ids": {"type": "array", "items": {"type": "string"}},
            "optional_b1_fact_ids": {"type": "array", "items": {"type": "string"}},
            "required_in_a2_fact_ids": {"type": "array", "items": {"type": "string"}},
            "comment_anchor": {"type": "string"},
            "prohibited_reference_fact_ids": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["role", "common_claim", "common_fact_ids", "optional_b1_fact_ids",
                     "required_in_a2_fact_ids", "comment_anchor", "prohibited_reference_fact_ids"],
        "additionalProperties": False,
    }


def shared_point_blueprint_json_schema() -> dict:
    return {
        "name": "shared_point_blueprint",
        "schema": {
            "type": "object",
            "properties": {
                "point_1": _point_blueprint_json_schema(),
                "point_2": _point_blueprint_json_schema(),
                "point_transition": {"type": "string"},
            },
            "required": ["point_1", "point_2", "point_transition"],
            "additionalProperties": False,
        },
        "strict": True,
    }


# ============================================================
# Blueprint生成prompt(Verified Fact Ledger確定後、Writer呼び出し前に実行)
# ============================================================
BLUEPRINT_DEVELOPER_MESSAGE = (
    "あなたはeigo-radioのShared Point Blueprint設計担当です。A2・B1という2つの"
    "CEFRレベル向けWriterが独立に記事を書く前に、両者が共有すべきPoint構造を"
    "決定します。あなた自身は本文を書きません。Verified Fact Ledgerにない事実を"
    "追加してはいけません。"
)

BLUEPRINT_PROMPT_TEMPLATE = """【今回のテーマ(日本語)】
{topic}

【Verified Fact Ledger】
{verified_ledger_text}

【あなたのタスク】
上記のLedgerに含まれる主要Factを、Point One・Point Twoの2つへ割り振り、
Shared Point Blueprintを作成してください。

このBlueprintの目的:
- A2 WriterとB1 Writerが独立に本文を書いても、「どのFactがどちらのPointに
  属するか」「各Pointの中心結論(common_claim)は何か」が両レベルで一致するように
  すること
- B1だけが使ってよい追加の詳細Fact(optional_fact)と、両レベルで扱うべき代表的
  Fact(common_fact)を区別すること
- 各Point後に流す共通Comment(A2・B1で共用する可能性がある短い橋渡し文)が、
  安全に参照してよい内容(comment_anchor)を明示すること

【厳守事項】
- common_claimは、A2の平易な語彙でもB1の自然な語彙でも表現できる、具体的すぎない
  中心結論にしてください(「支払い以上の価値がある」のような、Ledgerの一部の
  Factにしか根拠がない主張をcommon_claimにしないでください。それはoptional_
  b1_fact_idsに属するFactの範囲に留めてください)
- common_fact_idsに入れるFactは、A2の平易な語彙でも(数値を丸める・省略する
  ことはあっても)説明可能なものを選んでください
- 数値の細部・研究者名・引用・複数の限定条件が絡む詳細なFactはoptional_b1_
  fact_idsへ入れてください(A2は省略してよい、B1は使ってよい)
- comment_anchorは、common_fact_idsとcommon_claimの範囲だけで書ける1〜2文の
  要約にしてください。optional_b1_fact_idsの内容を含めないでください
- Point Oneのprohibited_reference_fact_idsには、Point Twoに割り振ったfact_id
  (common・optional問わず)を全て含めてください(Point One後のCommentが
  Point Twoの内容を先出ししないようにするため)
- 同じfact_idを両方のPointへ重複して割り振らないでください
- Point One・Point Twoの関係は、並列である必要はありません(原因→結果、
  研究結果→意味・応用、事実→判断軸等でもかまいません)。実際の記事の論理に
  従ってpoint_transitionへ簡潔に記述してください"""


def build_blueprint_prompt(topic_ja: str, verified_ledger_text: str) -> str:
    return BLUEPRINT_PROMPT_TEMPLATE.format(topic=topic_ja, verified_ledger_text=verified_ledger_text)


def run_blueprint_generation(client, topic_ja: str, verified_ledger_text: str, model: str) -> dict:
    """Shared Point Blueprintを実際にLLMへ生成させる(有料API呼び出し)。
    modelは呼び出し側がER-006-MODEL-ROUTING-CONTRACT-01のSSOT(routing.
    require_model)経由で明示指定すること(このモジュール自身はSSOTを
    直接importしない、既存の各Writer/Support呼び出しと同じ規約)。

    【注意】この関数はコードとして実装済みだが、Task本文の非対象事項
    (有料Writer APIによる新規記事生成が必要な場合は実行前承認)に従い、
    本タスクの完了時点では実際に呼び出していない。"""
    prompt = build_blueprint_prompt(topic_ja, verified_ledger_text)
    response = client.responses.create(
        model=model,
        reasoning={"effort": "medium"},
        text={"format": {"type": "json_schema", **shared_point_blueprint_json_schema()}},
        input=[
            {"role": "developer", "content": BLUEPRINT_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    parsed = json.loads(response.output_text)
    return {
        "prompt": prompt, "raw_text": response.output_text, "parsed": parsed,
        "model": response.model, "response_id": response.id,
        "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens,
    }


# ============================================================
# Writer/Support prompt挿入用のテキストblock変換
# ============================================================
def render_blueprint_for_writer(bp: SharedPointBlueprint, level: str) -> str:
    """A2/B1 Writerのprompt(COMMON_BLOCK_TEMPLATE)へ挿入するテキスト
    block。levelは"a2"または"b1"(A2はoptional_b1_fact_idsを省略してよい
    ことを明示、B1はそれも使ってよいことを明示する以外は同一内容)。"""
    def fmt_point(label: str, p: PointBlueprint) -> str:
        lines = [
            f"{label} role: {p.role}",
            f"{label} common_claim(必ず維持する中心結論): {p.common_claim}",
            f"{label} common_fact_ids(両レベル共通、必ずこのPointに置く): {', '.join(p.common_fact_ids) or '(なし)'}",
        ]
        if level == "a2":
            if p.required_in_a2_fact_ids:
                lines.append(f"{label} required_in_a2_fact_ids(A2でも省略しない): "
                              f"{', '.join(p.required_in_a2_fact_ids)}")
            lines.append(f"{label} 上記以外のcommon_fact_idsは、A2の平易さのために省略してよい"
                         f"(ただしcommon_claimは維持すること)")
        else:
            if p.optional_b1_fact_ids:
                lines.append(f"{label} optional_b1_fact_ids(B1のみ使ってよい追加根拠): "
                              f"{', '.join(p.optional_b1_fact_ids)}")
        return "\n".join(lines)

    parts = [
        "【Shared Point Blueprint(重要、Point構造の共通設計)】",
        "以下は、A2版・B1版の両方が従うべきPoint One/Point Twoの意味構造です。",
        "文章・語数・表現は各レベルで自由に最適化してよいですが、以下のfact_idの",
        "Point所属(どちらのPointに属するか)だけは、A2/B1で絶対に変えないで",
        "ください(同じfact_idを別のPointへ移動させない)。",
        "",
        fmt_point("[Point One]", bp.point_1),
        "",
        fmt_point("[Point Two]", bp.point_2),
    ]
    if bp.point_transition:
        parts.append(f"\n[Point One -> Point Twoの関係]: {bp.point_transition}")
    parts.append(
        "\n【出力形式への追加(重要)】\n"
        "記事本文(Markdown)を書き終えたら、最後に、Point One・Point Twoそれぞれで"
        "実際に使ったfact_idを、以下の形式のfenced code blockで1つだけ追加してください"
        "(本文とは別に、記事の一番最後に置いてください。これは音声化されないメタ"
        "データです)。\n"
        "```json\n"
        '{"point_1_fact_ids_used": ["FACT-xxx", ...], "point_2_fact_ids_used": ["FACT-xxx", ...]}\n'
        "```\n"
        "実際に本文で言及・使用したfact_idだけを列挙してください(Blueprintに列挙"
        "されているが本文で使わなかったfact_idは含めないでください)。"
    )
    return "\n".join(parts)


def render_comment_anchor_block(bp: SharedPointBlueprint, point_key: str) -> str:
    """Support(Comment)生成のcontextへ渡す、当該Point後のComment anchor
    block。point_keyは"point_1"または"point_2"。"""
    p = bp.point_1 if point_key == "point_1" else bp.point_2
    lines = [
        f"【このPoint後のCommentが参照してよい内容(comment_anchor)】",
        p.comment_anchor,
        "",
        "上記のcomment_anchorの範囲だけを参照してください。この時点でまだ提示されて"
        "いない内容(特に、まだ聞いていないPointの内容)を先取りして参照しないで"
        "ください。B1のみが使う可能性のある追加の数字・研究詳細・固有名詞は、"
        "comment_anchorに明記されていない限り参照しないでください。",
        "\n【出力形式への追加(重要)】\n"
        "Commentの本文を書き終えたら、最後に、実際に参照したfact_idを以下の形式の"
        "fenced code blockで1つだけ追加してください(音声化されないメタデータです)。\n"
        "```json\n"
        '{"referenced_fact_ids": ["FACT-xxx", ...]}\n'
        "```",
    ]
    if point_key == "point_1" and p.prohibited_reference_fact_ids:
        lines.insert(2, f"【まだ参照してはいけないfact_id(Point Two以降の内容)】: "
                        f"{', '.join(p.prohibited_reference_fact_ids)}")
    return "\n".join(lines)


# ============================================================
# 末尾fenced JSON blockの抽出・除去(既存article_text/comment textの
# 構造(TTS入力・split_article_text等)を一切変更しないための処理)
# ============================================================
_TRAILING_JSON_FENCE_RE = re.compile(r"\n?```json\s*\n(.*?)\n```\s*$", re.DOTALL)


def extract_trailing_metadata_block(raw_text: str) -> tuple:
    """raw_textの末尾にある```json ... ```блокを抽出し、パースして返す。
    抽出できた場合は(除去後のtext, パース済みdict)を、無い場合は
    (raw_textそのまま, None)を返す。Blueprint未使用の既存呼び出し(旧来の
    Writer/Support出力)にはこのblockが無いため、常にNoneを返し元の
    テキストをそのまま使う(完全な後方互換)。"""
    if not raw_text:
        return raw_text, None
    m = _TRAILING_JSON_FENCE_RE.search(raw_text)
    if not m:
        return raw_text, None
    clean_text = raw_text[:m.start()].rstrip()
    try:
        parsed = json.loads(m.group(1))
    except json.JSONDecodeError:
        return raw_text, None
    return clean_text, parsed
