# ============================================================
# er011_point_role_value_planning_01.py
# ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01: Point Role Planning + Point Value QA
# ============================================================
# 背景: No.18 A2のPoint Two("addictive by design"の議論について)は、
# 既存のPoint Overlap QA(er008_point_overlap_qa_18.py、Full Storyとの
# lexical overlap)を通過した(Point Oneとは異なる語彙を使っていた)が、
# 内容は「特定の対象・条件での傾向であり、全員には当てはまらない」
# 「医療的な依存症を診断するものではない」という一般的な留保のみで構成
# されており、リスナーへの新しい理解・示唆を何も加えていなかった。
#
# 既存のPoint Balance prompt(er003_v1_n3_01_articles_generate.py の
# COMMON_BLOCK_TEMPLATE)は「Pointが何を書いてよいか」(切り口・示唆・
# 背景・心理・社会的含意等)は列挙していたが、「留保・免責事項だけで
# Point枠を構成してはいけない」「新しい価値を加えなければならない」とは
# 一度も明示していなかった。既存のPoint Overlap QA(lexical overlap)も
# 「Full Storyと語彙的に似ているか」だけを見ており、「Pointが実際に
# 新しい価値を持っているか」は判定していなかった。これが、No.18のような
# 「重複はしていないが無価値」なPointをすり抜けさせていた根本原因。
#
# 本モジュールは2段構成の一般仕様を追加する(記事固有のハードコードでは
# なく、全テーマ共通で動作する):
#   1. Point Role Planning: Full Article Writer呼び出しの直前に、
#      Verified Fact Ledgerに基づいてPoint One/Twoの役割・新しい示唆・
#      根拠・「だから何なのか」・重複禁止事項を明示的に計画させ、その
#      計画をWriter promptへ挿入する(生成前の計画)。
#   2. Point Value QA: 生成後、実際のPoint本文が「新しい価値」を持って
#      いるかを独立したLLM呼び出しで判定する(生成後のQA、Point Role
#      Planningを守ったかどうかとは独立に判定する)。

from __future__ import annotations

import json
from typing import Any, Optional

# ============================================================
# 1. Point Role Planning
# ============================================================

ROLE_PLANNING_DEVELOPER_MESSAGE = (
    "英語ニュースpodcastのPoint One/Twoを実際に書く前に、Verified Fact "
    "Ledgerに基づいて、それぞれが担う役割と、聞き手に新しく持ち帰って"
    "もらうべき内容を具体的に計画してください。"
)

_ROLE_PLAN_FIELDS = (
    "role", "new_listener_takeaway", "evidence_anchor", "why_it_matters",
    "must_not_overlap_with_full_story", "must_not_overlap_with_other_point",
)


def _role_plan_item_schema() -> dict:
    return {
        "type": "object",
        "properties": {f: {"type": "string"} for f in _ROLE_PLAN_FIELDS},
        "required": list(_ROLE_PLAN_FIELDS),
        "additionalProperties": False,
    }


ROLE_PLANNING_JSON_SCHEMA = {
    "name": "point_role_value_planning",
    "schema": {
        "type": "object",
        "properties": {"point_one": _role_plan_item_schema(), "point_two": _role_plan_item_schema()},
        "required": ["point_one", "point_two"],
        "additionalProperties": False,
    },
    "strict": True,
}

ROLE_PLANNING_PROMPT_TEMPLATE = """これから、以下のVerified Fact Ledgerに基づいて、英語ニュースpodcast記事の
Point One・Point Twoを書きます。本文を書く前に、まず両方の設計を計画して
ください。

【今回のテーマ】
{topic}

【Verified Fact Ledger】
{verified_ledger_text}

Point One・Point Twoそれぞれについて、以下を具体的に(このLedger固有の
内容で、どんな記事にも当てはまるテンプレート的な一般論にならないように)
決めてください:

- role: このPointが記事の中で担う具体的な役割(例: 意外な詳細、方法論上の
  ニュアンス、歴史的な対比、心理的な理由。固定テンプレートではなく、この
  Ledgerに合わせて決めること)
- new_listener_takeaway: 聞き手がこのPointを聞いて新しく持ち帰る、具体的な
  理解・示唆・視点(Full Storyを聞いただけでは得られないもの)
- evidence_anchor: このPointの内容が、Verified Fact Ledgerのどの事実・
  データに基づくか
- why_it_matters: このPointが「だから何なのか」に対して与える具体的な答え
  (単なる一般的な留保・免責事項ではなく、聞き手にとっての意味)
- must_not_overlap_with_full_story: Full Storyで既に説明される意味のうち、
  このPointで繰り返してはいけない具体的な内容
- must_not_overlap_with_other_point: もう一方のPointが担う内容のうち、
  このPointで重複させてはいけない具体的な内容

【禁止(重要)】
以下のようなPointは、たとえPoint OneとPoint Twoの文字列が違っていても
価値が無いとみなされます。計画段階でこれらを避けてください:
- 研究上の限界・一般化上の注意・免責事項だけで構成されるPoint
- Full Storyの要約・言い換えに留まるPoint
- もう一方のPointの要約・言い換えになっているPoint
- 「だから何なのか」を説明できないPoint
- 他のどんな記事にもほぼそのまま流用できる一般論
- 新しい理解・解釈・意外性・具体的示唆のいずれも加えていないPoint

必要な留保・注意書き自体を書くこと自体は禁止されていませんが、それだけで
Point枠全体を使わないでください(留保は、新しい価値を含む内容に添える
補足として書いてください)。

【出力】
point_one/point_twoそれぞれについて、上記6項目を1〜2文の英語で簡潔に
記述してください(内部設計用であり、リスナーには見せません)。
"""


class RolePlanningModelMismatchError(RuntimeError):
    pass


def run_point_role_planning(client: Any, topic: str, verified_ledger_text: str, model: str,
                             reasoning_effort: str) -> dict:
    """Full Article Writer呼び出しの直前に実行する、小さな独立したJSON
    schema呼び出し。article_textには依存しない(まだ存在しないため)。"""
    prompt = ROLE_PLANNING_PROMPT_TEMPLATE.format(topic=topic, verified_ledger_text=verified_ledger_text)
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **ROLE_PLANNING_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": ROLE_PLANNING_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    if response.model != model:
        raise RolePlanningModelMismatchError(
            f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    text = getattr(response, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Point Role Planning応答が空です")
    parsed = json.loads(text)
    return {"parsed": parsed, "model": response.model, "response_id": response.id, "prompt": prompt}


def build_role_planning_block(planning: dict) -> str:
    """記事生成promptへ挿入するテキストブロック(日本語指示、Point One/Two
    本文は引き続き英語で書かせる)。"""
    p1 = planning["point_one"]
    p2 = planning["point_two"]
    return f"""
【Point One / Point Twoの計画(Point Role Planning、必ず従うこと)】
この記事のPoint One・Point Twoについて、本文を書く前に以下の設計を行い
ました。Point One・Point Twoの本文を書く際は、この設計に厳密に従って
ください。

Point One:
- role: {p1['role']}
- 聞き手が新しく持ち帰るべき内容: {p1['new_listener_takeaway']}
- 根拠(Verified Fact Ledger内): {p1['evidence_anchor']}
- だから何なのか: {p1['why_it_matters']}
- Full Storyと重複させてはいけない内容: {p1['must_not_overlap_with_full_story']}
- Point Twoと重複させてはいけない内容: {p1['must_not_overlap_with_other_point']}

Point Two:
- role: {p2['role']}
- 聞き手が新しく持ち帰るべき内容: {p2['new_listener_takeaway']}
- 根拠(Verified Fact Ledger内): {p2['evidence_anchor']}
- だから何なのか: {p2['why_it_matters']}
- Full Storyと重複させてはいけない内容: {p2['must_not_overlap_with_full_story']}
- Point Oneと重複させてはいけない内容: {p2['must_not_overlap_with_other_point']}

研究上の限界・免責事項だけでPoint枠全体を構成しないでください。留保は、
新しい価値を含む内容に添える補足としてのみ書いてください。"""


# ============================================================
# 2. Point Value QA(生成後、実際の本文を判定する)
# ============================================================

VALUE_QA_DEVELOPER_MESSAGE = (
    "英語ニュースpodcast記事のPoint One/Twoの本文を読み、それぞれが"
    "リスナーにとって新しい価値を実際に加えているかを厳格に判定してください。"
)

VALUE_QA_FIELDS = (
    "qa_not_caveat_only",
    "qa_not_full_story_paraphrase",
    "qa_not_other_point_paraphrase",
    "qa_explains_why_it_matters",
    "qa_specific_not_generic",
    "qa_adds_new_value",
)


def _value_qa_item_schema() -> dict:
    props = {f: {"type": "string", "enum": ["PASS", "FAIL"]} for f in VALUE_QA_FIELDS}
    props["reasoning"] = {"type": "string"}
    return {"type": "object", "properties": props, "required": list(props.keys()),
            "additionalProperties": False}


POINT_VALUE_QA_JSON_SCHEMA = {
    "name": "point_value_qa",
    "schema": {
        "type": "object",
        "properties": {"point_one": _value_qa_item_schema(), "point_two": _value_qa_item_schema()},
        "required": ["point_one", "point_two"],
        "additionalProperties": False,
    },
    "strict": True,
}

VALUE_QA_PROMPT_TEMPLATE = """以下はある英語ニュースpodcast記事のFull Story・Point One・Point Twoです。
Point One・Point Twoそれぞれについて、以下6項目を判定してください
(それぞれPASS/FAIL)。

- qa_not_caveat_only: このPointが、研究上の限界・一般化上の注意・免責事項
  だけで構成されていない場合PASS(それらに加えて実質的な新しい内容がある
  場合もPASS。留保だけでPoint枠全体が終わっている場合はFAIL)
- qa_not_full_story_paraphrase: Full Storyの要約・言い換えに留まっていない
  場合PASS(Full Storyの中心的なlogic・結論を語彙だけ変えて繰り返している
  場合はFAIL)
- qa_not_other_point_paraphrase: もう一方のPointの要約・言い換えになって
  いない場合PASS
- qa_explains_why_it_matters: 「だから何なのか」を具体的に説明できている
  場合PASS(聞き手にとっての具体的な意味・示唆がある場合)
- qa_specific_not_generic: この記事のLedger固有の内容に基づいており、他の
  どんな記事にもほぼそのまま流用できる一般論になっていない場合PASS
- qa_adds_new_value: 新しい理解・解釈・意外性・具体的示唆のいずれかを
  実際に加えている場合PASS(Full Storyだけを聞いた場合と比べて、聞き手の
  理解が実際に深まっている場合)

reasoningには、判定理由を1〜2文の日本語で書いてください(特にFAILの場合は
具体的な理由を明記してください)。

【Full Story】
{full_story}

【Point One】
{point_one_body}

【Point Two】
{point_two_body}
"""


class ValueQaModelMismatchError(RuntimeError):
    pass


def build_value_qa_prompt(full_story: str, point_one_body: str, point_two_body: str) -> str:
    return VALUE_QA_PROMPT_TEMPLATE.format(
        full_story=full_story, point_one_body=point_one_body, point_two_body=point_two_body)


def _validate_value_qa_item(item: dict) -> dict:
    failing = [f for f in VALUE_QA_FIELDS if item.get(f) not in ("PASS", "FAIL")]
    if failing:
        return {"ok": False, "reasons": [f"フィールド不正: {failing}"]}
    fail_fields = [f for f in VALUE_QA_FIELDS if item[f] == "FAIL"]
    return {"ok": True, "fail_fields": fail_fields, "reasoning": item.get("reasoning", "")}


def run_point_value_qa(client: Any, full_story: str, point_one_body: str, point_two_body: str,
                        model: str, reasoning_effort: str) -> dict:
    prompt = build_value_qa_prompt(full_story, point_one_body, point_two_body)
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **POINT_VALUE_QA_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": VALUE_QA_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    if response.model != model:
        raise ValueQaModelMismatchError(
            f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    text = getattr(response, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Point Value QA応答が空です")
    parsed = json.loads(text)

    result = {"model": response.model, "response_id": response.id, "prompt": prompt, "parsed": parsed}
    per_point = {}
    overall_ok = True
    for key in ("point_one", "point_two"):
        item = parsed.get(key)
        if not isinstance(item, dict):
            overall_ok = False
            per_point[key] = {"ok": False, "reasons": [f"'{key}'がオブジェクトでない"]}
            continue
        validated = _validate_value_qa_item(item)
        per_point[key] = validated
        if not validated["ok"] or validated.get("fail_fields"):
            overall_ok = False
    result["per_point"] = per_point
    result["status"] = "PASS" if overall_ok else "NG"
    return result


def build_value_qa_diagnostic_note(value_qa_result: dict) -> str:
    """Diagnostic Full Retry prompt末尾へ追加する、Point Value QA NGの
    診断メモ(英語、既存のDiagnostic Full Retryセクションと同じ言語)。"""
    lines = ["[Point Value QA — a previous attempt failed a listener-value check, do NOT repeat "
             "these problems]"]
    for key, label in (("point_one", "Point One"), ("point_two", "Point Two")):
        entry = value_qa_result.get("per_point", {}).get(key, {})
        fail_fields = entry.get("fail_fields") or []
        if fail_fields:
            lines.append(f"- {label} failed: {', '.join(fail_fields)}. Reason: {entry.get('reasoning', '')}")
    lines.append("Rewrite so each Point clearly adds new listener value (a specific new "
                 "understanding, interpretation, surprising detail, or concrete implication) "
                 "beyond the Full Story and beyond the other Point — not just a caveat or a "
                 "generic disclaimer.")
    return "\n".join(lines)
