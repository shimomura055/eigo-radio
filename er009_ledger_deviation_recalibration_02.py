# -*- coding: utf-8 -*-
# ============================================================
# er009_ledger_deviation_recalibration_02.py
# ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02
# ============================================================
# 現行Ledger Deviation Checker(er003_v1_en_direct_vfl_01_generate.py::
# run_deviation_check / DEVIATION_PROMPT_TEMPLATE / DEVIATION_JSON_SCHEMA)は
# 「Ledgerの文言とのlexical/scope的な厳密一致」を暗黙に重視しており、
# 意味を変えないparaphrase・A2/B1向け簡略化・Evidenceをまたぐbridge
# sentence・一般的な情景描写までMAJORとして検知してしまう(No.9実データ
# で確認、詳細は完了報告を参照)。
#
# 本モジュールは、その過剰検知を是正した新しいLedger Deviation Checker
# の「候補」実装。Production側(er003_v1_en_direct_vfl_01_generate.py)は
# まだ書き換えず、まずこの候補を
#   (1) No.9の実データ(B1/A2)で旧判定と比較
#   (2) 意図的に危険なfixtureで false negative が起きないか検証
# した上で、問題なければProductionへ正式反映する(このファイル自体を
# Production化するのではなく、検証済みのprompt/schemaをSSOTへ移植する)。
#
# 新しい判定思想:
#   MAJOR = 以下10種類の「意味上のFact差分」のいずれかが明確にtrueの場合のみ
#     changed_fact / changed_scope / changed_causality / changed_certainty /
#     changed_number / changed_actor / changed_negation / changed_comparison /
#     changed_time / unsupported_new_claim
#   MINOR = 意味は保っているが言い回しがやや粗い場合(Productionは止めない)
#   ALLOWED/STYLE = paraphrase・簡略化・bridge sentence・情景描写など
#     (deviationとして報告すらしない)
#
# 10種類のフラグが全てfalseなのにseverity=MAJORが返ってきた場合は、
# プロンプト違反とみなしMINORへ自動降格する(post-hoc validation)。
# overall_statusは、この降格処理後にMAJORが1件でも残るかどうかで
# プログラム側が再計算する(モデルの自己申告に依存しない)。
from __future__ import annotations

import json

import er003_v1_en_direct_vfl_01_generate as vfl01

MODEL = vfl01.MODEL
REASONING_EFFORT = vfl01.REASONING_EFFORT

DEVIATION_FLAG_KEYS = [
    "changed_fact", "changed_scope", "changed_causality", "changed_certainty",
    "changed_number", "changed_actor", "changed_negation", "changed_comparison",
    "changed_time", "unsupported_new_claim",
]

DEVIATION_JSON_SCHEMA_V2 = {
    "name": "ledger_deviation_check_v2",
    "schema": {
        "type": "object",
        "properties": {
            "deviations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "claim_in_article": {"type": "string"},
                        "issue": {"type": "string"},
                        "severity": {"type": "string", "enum": ["MINOR", "MAJOR"]},
                        "changed_fact": {"type": "boolean"},
                        "changed_scope": {"type": "boolean"},
                        "changed_causality": {"type": "boolean"},
                        "changed_certainty": {"type": "boolean"},
                        "changed_number": {"type": "boolean"},
                        "changed_actor": {"type": "boolean"},
                        "changed_negation": {"type": "boolean"},
                        "changed_comparison": {"type": "boolean"},
                        "changed_time": {"type": "boolean"},
                        "unsupported_new_claim": {"type": "boolean"},
                        "explanation": {"type": "string"},
                    },
                    "required": [
                        "claim_in_article", "issue", "severity", "changed_fact", "changed_scope",
                        "changed_causality", "changed_certainty", "changed_number", "changed_actor",
                        "changed_negation", "changed_comparison", "changed_time",
                        "unsupported_new_claim", "explanation",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["deviations"],
        "additionalProperties": False,
    },
    "strict": True,
}

DEVIATION_DEVELOPER_MESSAGE_V2 = (
    "あなたはLedger Fact Safetyの検証担当です。記事の面白さやスタイルは評価せず、"
    "意味上のFactがVerified Fact Ledgerの範囲内に収まっているかだけを判定してください。"
    "paraphrase・簡略化・語順変更・bridge sentence・文体の違いは、意味が変わらない限り"
    "deviationとして報告しないでください。"
)

DEVIATION_PROMPT_TEMPLATE_V2 = """以下の記事本文が、Verified Fact Ledgerが保証する「意味上のFact」の
範囲内に収まっているかを、Fact Safetyの観点のみで確認してください。

【Verified Fact Ledger】
{verified_ledger_text}

【検証対象の記事】
{article_text}

【判定対象は次の10種類の意味変化のみです】
- changed_fact: Ledgerに存在しない、またはLedgerと矛盾する具体的事実を主張している
- changed_scope: Ledgerが確認した対象(誰が・どこで・いつ・どの集団か)を超えて一般化・拡張している
- changed_causality: 相関を因果に変えている、または因果の方向を変えている
- changed_certainty: Ledgerでは仮説・自己申告・専門家の解釈にすぎないものを、断定的な事実であるかのように強めている
- changed_number: 数値・割合・件数をLedgerと異なる値に変えている(単位の違いだけの言い換えは含まない)
- changed_actor: 発言主体・調査主体をLedgerと異なる人物・組織にすり替えている
- changed_negation: 肯定・否定を反転させている
- changed_comparison: 比較の方向(より多い/少ない、より高い/低い等)を反転・変更している
- changed_time: 時期・年代をLedgerと異なるものに変えている
- unsupported_new_claim: Ledgerに全く存在しない新しい具体的主張を追加している

【deviationとして報告しないもの(許容範囲)】
- 自然なparaphrase、A2/B1向けの平易な言い換え、語順変更、同義語への置換
- 出典名を一般的な言い方(a report, a studyなど)に置き換えること自体
- 意味を変えない軽いbridge sentence(異なるEvidence間をつなぐだけの文)
- 明確な新規Factを伴わない一般的な情景描写(例: 支払い画面はレストランやカフェにもある、
  という一般常識レベルの前置き)
- Ledgerの特定の一文と一字一句一致しないが、同じ意味を保っている表現

【判定ルール】
- 上記10種類のいずれかが明確にtrueである場合のみ、severityをMAJORにしてください。
- 10種類すべてがfalseなのにMAJORにすることは禁止です。
- 意味はおおむね保っているが言い回しがやや粗い場合(出典に勝手な肩書きを補う、
  自己申告の調査結果を断定的な行動として書く等)はMINORとして記録してください。
- 判断に迷う場合は、「記事の主張がLedgerの主張とほぼ同じ意味を保っているか」を
  最優先の基準にしてください。厳密な文言一致は求めません。
- 各deviationについて、上記10種類のフラグ全てにtrue/falseを明示し、
  explanationでどのフラグに基づいてその判定になったかを一言で説明してください。

該当するdeviationがなければ、deviationsを空配列にしてください。"""


def run_deviation_check_v2(client, verified_ledger_text: str, article_text: str, model: str = MODEL) -> dict:
    prompt = DEVIATION_PROMPT_TEMPLATE_V2.format(
        verified_ledger_text=verified_ledger_text, article_text=article_text)
    response = client.responses.create(
        model=model,
        reasoning={"effort": REASONING_EFFORT},
        text={"format": {"type": "json_schema", **DEVIATION_JSON_SCHEMA_V2}},
        input=[
            {"role": "developer", "content": DEVIATION_DEVELOPER_MESSAGE_V2},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    raw_parsed = json.loads(text)
    parsed = _apply_post_hoc_validation(raw_parsed)
    return {
        "prompt": prompt, "raw_text": text, "raw_parsed": raw_parsed, "parsed": parsed,
        "model": response.model, "response_id": response.id,
    }


def _apply_post_hoc_validation(raw_parsed: dict) -> dict:
    """モデルがseverity=MAJORを返したが10種類のフラグが全てfalseの場合、
    プロンプト違反とみなしMINORへ自動降格する。overall_statusは、この
    降格処理後にMAJORが1件でも残るかどうかをプログラム側で再計算する
    (モデルの自己申告するoverall_statusフィールドには依存しない設計)。"""
    deviations = []
    for d in raw_parsed.get("deviations", []):
        d = dict(d)
        any_flag_true = any(bool(d.get(k)) for k in DEVIATION_FLAG_KEYS)
        if d.get("severity") == "MAJOR" and not any_flag_true:
            d["severity"] = "MINOR"
            d["auto_downgraded"] = True
            d["issue"] = f"[AUTO-DOWNGRADED: no fact-deviation flag true] {d.get('issue', '')}"
        else:
            d["auto_downgraded"] = False
        deviations.append(d)
    overall_status = "LEDGER_DEVIATION" if any(d["severity"] == "MAJOR" for d in deviations) else "LEDGER_COMPLIANT"
    return {"deviations": deviations, "overall_status": overall_status}


if __name__ == "__main__":
    import sys

    OUT_DIR = "er006_output/pool_pilot_01/pool_n9_tip_screens"
    LEDGER_TEXT = open(f"{OUT_DIR}/research/verified_fact_ledger.txt", encoding="utf-8").read()

    levels = sys.argv[1:] or ["b1b", "a2"]
    client = vfl01.get_client()
    summary = {}
    for level in levels:
        article_text = open(f"{OUT_DIR}/{level}/article.md", encoding="utf-8").read()
        print(f"[{level}] v2 ledger逸脱チェック実行開始...")
        result = run_deviation_check_v2(client, LEDGER_TEXT, article_text)
        parsed = result["parsed"]
        out_path = f"{OUT_DIR}/{level}/ledger_deviation_v2_candidate.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"raw_parsed": result["raw_parsed"], "parsed": parsed}, f, ensure_ascii=False, indent=2)
        print(f"[{level}] v2 overall_status={parsed['overall_status']} deviations={len(parsed['deviations'])}")
        for d in parsed["deviations"]:
            flags = [k for k in DEVIATION_FLAG_KEYS if d.get(k)]
            print(f"  {d['severity']}: {d.get('claim_in_article', '')[:60]!r} flags={flags} "
                  f"downgraded={d.get('auto_downgraded')}")
        summary[level] = {
            "overall_status": parsed["overall_status"],
            "major_count": sum(1 for d in parsed["deviations"] if d["severity"] == "MAJOR"),
            "minor_count": sum(1 for d in parsed["deviations"] if d["severity"] == "MINOR"),
        }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
