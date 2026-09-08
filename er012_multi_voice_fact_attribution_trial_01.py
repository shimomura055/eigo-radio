# ============================================================
# er012_multi_voice_fact_attribution_trial_01.py
# 管理ID: EDITORIAL-B-FAMILY-MULTI-VOICE-FACT-ATTRIBUTION-TRIAL-01(Lane B)
# ============================================================
# 目的(Trial専用、Production非変更):
#   B-Family(複数Voice構成)でFact CheckerがREVIEW_REQUIREDを返す原因が、
#   「複合Voiceへの事実帰属」(=Ledgerの実データを一人称の合成人格へ
#   翻案したため、Fact Checkerが「実在する個人の発言として確認できない」
#   と判定してしまう構造的ミスマッチ)であるという仮説を、既存Ledger/
#   既存article/既存fact_check出力から抽出したclaim単位で検証する。
#
#   候補設計A: Ledgerの[VOICE_1_EVIDENCE]/[VOICE_2_EVIDENCE]タグと
#     section labelをFact Checker相当の分類prompt(このTrial専用prompt。
#     本番fact_checker_prompt_template_r3.txtは変更しない)へ追加で渡し、
#     各claimを次の3区分へ分類させる:
#       ATTRIBUTION_ONLY_SUPPORTED: Ledgerの実evidenceが一人称の合成
#         persona表現に変換されただけで、内容自体はLedgerに支持される
#       FACTUAL_CLAIM_SUPPORTED_BUT_UNCITED: 内容はLedgerにあるが
#         記事本文中に出典が明示されていない
#       UNSUPPORTED_OR_UNVERIFIED: Ledgerのどのevidenceにも対応しない、
#         または独立に検証が必要
#   候補設計B: Ledger evidenceを渡さず、claim文だけから
#     SUBJECTIVE_FIRST_PERSON_EXPERIENCE / OBJECTIVE_FACTUAL_CLAIM の
#     二値のみで分類させる(前段の主観/客観分類器のみのシンプル案)。
#
# 本番コードは一切import/変更しない。本番Fact Checker
# (er002_ja_web_research_r3.make_fact_checker_fn等)や
# er006_model_routing_contract_01のprompt/ロジックは変更しない。
# 使用モデルのみ本番と同一(routing.WRITER_FACT_CHECK_MODEL相当)を
# 参照するが、web_search toolは使わない(コスト抑制、Trialの目的は
# 「分類ロジックの挙動比較」であり独立Web検証の再現ではない)。
#
# 出力: er012_output/multi_voice_fact_attribution_trial_01/ 配下
# 予算上限: 本Trialの新規LLM呼び出しは合計 上限¥50 相当まで
# ============================================================
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()
from openai import OpenAI

import er006_model_routing_contract_01 as routing

OUT_DIR = "er012_output/multi_voice_fact_attribution_trial_01"
os.makedirs(OUT_DIR, exist_ok=True)

MODEL = routing.WRITER_FACT_CHECK_MODEL  # 本番Fact Checkerと同一モデル参照(prompt/toolは別)
REASONING_EFFORT = "low"  # Trialのコスト抑制のため本番(既定)より下げる。Production値には触れない

LEDGER_VOICE_EVIDENCE_BLOCK = """
[VOICE_1_EVIDENCE] 1-01(fact_001): Gensler調査、固定席保有者は所属感87%/74%、集中80%/67%。source: Bisnow(Gensler調査引用)
[VOICE_1_EVIDENCE] 1-02(fact_003): LinkedIn News特集、ホットデスキングへの反発理由=衛生懸念・パーソナルスペース喪失(他人が使った机やキーボードへの不安、私物を置けないストレス)。source: LinkedIn News
[VOICE_1_EVIDENCE] 1-03(fact_004): Forbes 2024調査、固定席なし従業員は職場を「非人間的」「方向感覚を失う」「精神的に疲れる」と表現する傾向。Salesforce等が固定席復活。source: Forbes/LinkedIn
[VOICE_1_EVIDENCE] 1-05(fact_007固定席側): note「REAL VOICE #05」、フリーアドレス勤務パート社員が「自分の席がないので落ち着かない」「私物置き場に困る」と発言。source: note
[VOICE_1_EVIDENCE] 1-06(fact_009): ITmedia MONOist 2024調査、フリーアドレス勤務者の36.8%が「席が固定化しがちだ」と回答。source: MONOist(ITmedia)
[VOICE_1_EVIDENCE] 1-07(fact_008固定席側): TOKYO MX+街頭インタビュー、50人中10人が固定席支持、理由=「席探しが面倒」「チーム分散でコミュニケーション困難」。source: TOKYO MX+

[VOICE_2_EVIDENCE] 2-01(fact_008自由席側): TOKYO MX+同インタビュー、50人中40人が自由席支持、理由=「気分で環境を変えられる」「人間関係から距離を取りたい時に席を変えられる」。source: TOKYO MX+
[VOICE_2_EVIDENCE] 2-02(fact_012): Carr Workplaces記事、企業リーダー12人、「その日必要な思考に応じて場所を選ぶ」「集中用の静かなゾーン/協働用オープンエリアなど認知ゾーンを選べることが生産性・満足度を高める」。source: Carr Workplacesブログ
[VOICE_2_EVIDENCE] 2-03(fact_007自由席側): note「REAL VOICE #05」、フリーアドレス勤務パート社員、毎日違う席で他部署の人と話しやすくなったと発言。source: note
[VOICE_2_EVIDENCE] 2-04(fact_014): CNET Japan 2020記事、在宅勤務長期化で自分の作業環境を持った従業員は、オフィスで必ずしも固定席を必要としなくなったと報道。source: CNET Japan

[CROSS_REFERENCE] X-01(fact_002): Amazon CEOアンディ・ジャシー、2024年9月社内メモでシアトル本社のホットデスキング廃止・固定席復帰方針(欧州拠点はホットデスキング継続)。source: Business Insider
"""

# er012_output/editorial_b_voices_a2_free_address_03/a2/audit/fact_check.json の
# unsupported_specific_claims(実データ、無変更で転記)+ 検証用control 2件。
CLAIMS = [
    {
        "id": "voiceA_desk_experience",
        "section": "voice_a_body(One Voice)",
        "source_run": "editorial_b_voices_a2_free_address_03/a2 fact_check.json",
        "claim_text": (
            "記事冒頭の「毎朝空席を探す」「机やキーボードを他人が使ったことを心配する」"
            "「同じ机・引き出し・眺めが帰属意識や安定感を与える」という一人称の経験は、"
            "発言者・企業・調査名・調査対象が示されておらず、実在する発言として確認できない。"
        ),
        "ground_truth_should_flag": False,
        "ground_truth_note": "VOICE_1_EVIDENCE 1-01/1-02/1-03/1-05の複数実factを一人称の合成personaへ翻案したもの。内容自体はLedgerに支持される(帰属のみの問題)。",
    },
    {
        "id": "voiceB_seat_choice_experience",
        "section": "voice_b_body(Another Voice)",
        "source_run": "editorial_b_voices_a2_free_address_03/a2 fact_check.json",
        "claim_text": (
            "「静かな場所」「他部署の近く」「気まずい仕事上の関係から距離を置くための席」を"
            "日によって選ぶという一人称の経験も、出典のない引用風表現であり、実在の当事者発言か、"
            "筆者による創作・要約か判定できない。"
        ),
        "ground_truth_should_flag": False,
        "ground_truth_note": "VOICE_2_EVIDENCE 2-01/2-02に対応する内容の合成persona化。帰属のみの問題。",
    },
    {
        "id": "voiceB_wfh_reason",
        "section": "voice_b_body(Another Voice)",
        "source_run": "editorial_b_voices_a2_free_address_03/a2 fact_check.json",
        "claim_text": (
            "「在宅勤務で自分の場所を持つようになったため、オフィスに固定席は不要になった」という"
            "個人の心理・理由は、出典がなく確認できない。"
        ),
        "ground_truth_should_flag": False,
        "ground_truth_note": "VOICE_2_EVIDENCE 2-04(CNET Japan)に直接対応。帰属のみの問題。",
    },
    {
        "id": "tension_repeated_desk_use",
        "section": "tension_body(Where the Difference Comes From)",
        "source_run": "editorial_b_voices_a2_free_address_03/a2 fact_check.json",
        "claim_text": (
            "「フリーアドレス制では、同じ人が同じ机を頻繁に使うことがある」という主張は一定の"
            "研究知見と整合する可能性はあるが、記事内には具体的な調査・事例がなく、本文の形では"
            "確認不十分である。"
        ),
        "ground_truth_should_flag": False,
        "ground_truth_note": "VOICE_1_EVIDENCE 1-06(MONOist 36.8%)に直接対応。Ledger上は支持されているが本文中の出典明示がない(帰属・引用表記の問題であり捏造ではない)。",
    },
    {
        "id": "control_positive_fabricated",
        "section": "tension_body(想定挿入・positive control)",
        "source_run": "本Trialで追加した検証用control(実記事には存在しない)",
        "claim_text": (
            "この記事によれば、2030年までに世界の全企業がフリーアドレス制を廃止することが"
            "法律で義務付けられている。"
        ),
        "ground_truth_should_flag": True,
        "ground_truth_note": "Ledgerのどのevidenceにも対応しない、明確に捏造された制度的主張。positive control(false acceptを検出するため)。",
    },
    {
        "id": "control_negative_generic_opinion",
        "section": "voice_b_body(想定挿入・negative control)",
        "source_run": "本Trialで追加した検証用control(実記事には存在しない)",
        "claim_text": (
            "私は、その日の気分に合わせて席を変えられることを、単純に心地よいと感じている。"
        ),
        "ground_truth_should_flag": False,
        "ground_truth_note": "個人の主観的な好みの表明のみで、具体的な検証可能主張を含まない。negative control(false rejectを検出するため)。",
    },
]

CANDIDATE_B_SCHEMA = {
    "name": "candidate_b_classification",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "classification": {
                            "type": "string",
                            "enum": ["SUBJECTIVE_FIRST_PERSON_EXPERIENCE", "OBJECTIVE_FACTUAL_CLAIM"],
                        },
                        "should_still_require_review": {"type": "boolean"},
                        "reason": {"type": "string"},
                    },
                    "required": ["id", "classification", "should_still_require_review", "reason"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["items"],
        "additionalProperties": False,
    },
    "strict": True,
}

CANDIDATE_A_SCHEMA = {
    "name": "candidate_a_classification",
    "schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "classification": {
                            "type": "string",
                            "enum": [
                                "ATTRIBUTION_ONLY_SUPPORTED",
                                "FACTUAL_CLAIM_SUPPORTED_BUT_UNCITED",
                                "UNSUPPORTED_OR_UNVERIFIED",
                            ],
                        },
                        "matched_evidence_ids": {"type": "array", "items": {"type": "string"}},
                        "should_still_require_review": {"type": "boolean"},
                        "reason": {"type": "string"},
                    },
                    "required": [
                        "id", "classification", "matched_evidence_ids",
                        "should_still_require_review", "reason",
                    ],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["items"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_candidate_b_prompt(claims: list[dict]) -> str:
    claim_lines = "\n".join(
        f"- id={c['id']} / section={c['section']}\n  claim_text: {c['claim_text']}"
        for c in claims
    )
    return f"""あなたは、記事内の「主張」を、後段のFact Checkerへ渡す前に分類する担当者です。
以下の各claim_textについて、次の2区分のいずれかに分類してください。

- SUBJECTIVE_FIRST_PERSON_EXPERIENCE: 一人称の体験・心情・好みの表明であり、外部の
  事実・統計・制度・出来事についての検証可能な主張を含まない
- OBJECTIVE_FACTUAL_CLAIM: 外部の事実・統計・制度・出来事についての検証可能な主張を含む

分類に加えて、should_still_require_review(このclaimは依然としてFact Checkerによる
Web検証・人間レビューが必要か)をtrue/falseで判定してください。

【分類対象】
{claim_lines}

指定されたJSON形式のフィールドだけで回答してください。"""


def build_candidate_a_prompt(claims: list[dict], ledger_block: str) -> str:
    claim_lines = "\n".join(
        f"- id={c['id']} / section={c['section']}\n  claim_text: {c['claim_text']}"
        for c in claims
    )
    return f"""あなたは、複数Voice構成の記事における「事実帰属」を判定する担当者です。
この記事は、Verified Fact Ledgerの実evidenceを、Voice(一人称の合成persona)ごとに
まとめて翻案したものです。各Voiceの一人称の発言は、実在する単一個人の発言ではなく、
Ledger上の複数の実evidence(調査・報道・インタビュー)を、そのVoiceの視点で
合成したものです。これはこの記事シリーズの既知の設計であり、捏造ではありません。

【Verified Fact Ledger(該当部分の抜粋、evidence IDタグ付き)】
{ledger_block}

以下の各claim_textについて、次の3区分のいずれかに分類してください。

- ATTRIBUTION_ONLY_SUPPORTED: claimの内容が、上記Ledgerのいずれかのevidence
  (該当Voiceに対応するタグ、または関連タグ)に実質的に対応しており、問題は
  「一人称の合成persona表現になっている」という帰属表現の性質だけである
- FACTUAL_CLAIM_SUPPORTED_BUT_UNCITED: claimの内容はLedgerのevidenceに対応するが、
  記事本文中に出典・調査名などの明示がなく、読者から見ると未検証に見える
- UNSUPPORTED_OR_UNVERIFIED: 上記Ledgerのどのevidenceにも実質的に対応せず、
  独立した検証(Web検索等)が必要、または明確に対応するevidenceがない

matched_evidence_idsには、対応すると判断したevidence ID(例: "1-01", "2-04")を
列挙してください(対応するものがなければ空配列)。

分類に加えて、should_still_require_review(このclaimは依然として人間レビューが
必要か。ATTRIBUTION_ONLY_SUPPORTEDは原則false、UNSUPPORTED_OR_UNVERIFIEDは原則true
とすべきですが、あなた自身の判断で決めてください)をtrue/falseで判定してください。

【分類対象】
{claim_lines}

指定されたJSON形式のフィールドだけで回答してください。"""


def call_classifier(prompt: str, schema: dict, model: str, reasoning_effort: str, client: OpenAI):
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **schema}},
        input=prompt,
    )
    text = getattr(response, "output_text", None)
    usage = getattr(response, "usage", None)
    usage_dict = None
    if usage is not None:
        try:
            usage_dict = usage.model_dump()
        except Exception:
            usage_dict = str(usage)
    return {
        "text": text,
        "parsed": json.loads(text) if text else None,
        "response_id": getattr(response, "id", None),
        "model": model,
        "usage": usage_dict,
    }


def score(claims: list[dict], parsed_items: list[dict]) -> dict:
    by_id = {c["id"]: c for c in claims}
    result_by_id = {it["id"]: it for it in parsed_items}
    false_accept = []  # ground truth should_flag=True だが should_still_require_review=False
    false_reject = []  # ground truth should_flag=False だが should_still_require_review=True
    correct = []
    for cid, c in by_id.items():
        r = result_by_id.get(cid)
        if r is None:
            continue
        gt = c["ground_truth_should_flag"]
        pred = r["should_still_require_review"]
        if gt and not pred:
            false_accept.append(cid)
        elif not gt and pred:
            false_reject.append(cid)
        else:
            correct.append(cid)
    return {
        "false_accept_ids": false_accept,
        "false_reject_ids": false_reject,
        "correct_ids": correct,
        "false_accept_count": len(false_accept),
        "false_reject_count": len(false_reject),
        "correct_count": len(correct),
        "total": len(by_id),
    }


def main():
    client = OpenAI()
    run_log = {"started_at": datetime.now(timezone.utc).isoformat(), "model": MODEL,
               "reasoning_effort": REASONING_EFFORT}

    # Candidate B: 主観/客観の二値分類のみ(Ledger evidenceを渡さない)
    prompt_b = build_candidate_b_prompt(CLAIMS)
    with open(f"{OUT_DIR}/candidate_b_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt_b)
    result_b = call_classifier(prompt_b, CANDIDATE_B_SCHEMA, MODEL, REASONING_EFFORT, client)
    with open(f"{OUT_DIR}/candidate_b_result.json", "w", encoding="utf-8") as f:
        json.dump(result_b, f, ensure_ascii=False, indent=2)
    score_b = score(CLAIMS, result_b["parsed"]["items"]) if result_b["parsed"] else None
    with open(f"{OUT_DIR}/candidate_b_score.json", "w", encoding="utf-8") as f:
        json.dump(score_b, f, ensure_ascii=False, indent=2)

    # Candidate A: Voice別evidenceタグを渡した3値分類
    prompt_a = build_candidate_a_prompt(CLAIMS, LEDGER_VOICE_EVIDENCE_BLOCK)
    with open(f"{OUT_DIR}/candidate_a_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt_a)
    result_a = call_classifier(prompt_a, CANDIDATE_A_SCHEMA, MODEL, REASONING_EFFORT, client)
    with open(f"{OUT_DIR}/candidate_a_result.json", "w", encoding="utf-8") as f:
        json.dump(result_a, f, ensure_ascii=False, indent=2)
    score_a = score(CLAIMS, result_a["parsed"]["items"]) if result_a["parsed"] else None
    with open(f"{OUT_DIR}/candidate_a_score.json", "w", encoding="utf-8") as f:
        json.dump(score_a, f, ensure_ascii=False, indent=2)

    run_log["candidate_b_score"] = score_b
    run_log["candidate_a_score"] = score_a
    run_log["candidate_b_usage"] = result_b["usage"]
    run_log["candidate_a_usage"] = result_a["usage"]
    run_log["finished_at"] = datetime.now(timezone.utc).isoformat()
    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(run_log, f, ensure_ascii=False, indent=2)

    with open(f"{OUT_DIR}/claims_input.json", "w", encoding="utf-8") as f:
        json.dump(CLAIMS, f, ensure_ascii=False, indent=2)

    print("=== Candidate B (subjective/objective only) ===")
    print(json.dumps(score_b, ensure_ascii=False, indent=2))
    print("=== Candidate A (Voice-evidence-aware) ===")
    print(json.dumps(score_a, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


def build_candidate_a2_prompt(claims: list[dict], ledger_block: str) -> str:
    claim_lines = "\n".join(
        f"- id={c['id']} / section={c['section']}\n  claim_text: {c['claim_text']}"
        for c in claims
    )
    return f"""あなたは、複数Voice構成の記事における「事実帰属」を判定する担当者です。
この記事シリーズの既定フォーマットでは、Voice(一人称の合成persona)本文は、
そのVoiceに割り当てられたLedger evidence(調査・報道・インタビュー)を、
一人称の語りへ翻案したものであり、本文中に出典・調査名・数値を逐一明記する
ことは仕様上想定されていません(Voice本文はナレーションであり脚注ではない
ため)。したがって、Voice本文中のclaimがそのVoiceに割り当てられたLedger
evidenceの内容と実質的に対応していれば、「本文中に出典が書かれていない」
こと自体を理由にレビュー要求してはいけません。レビューが必要なのは、
(1) Ledgerのどのevidenceにも実質的に対応しない場合、または
(2) Voice本文ではない箇所(Tension/Closing等の地の文としての客観的主張、
比率・数値・研究結果への直接言及)で、具体的な出典明示が読者にとって
本来期待される場合、のいずれかだけです。

【Verified Fact Ledger(該当部分の抜粋、evidence IDタグ付き)】
{ledger_block}

以下の各claim_textについて、次の3区分のいずれかに分類してください。

- ATTRIBUTION_ONLY_SUPPORTED: Voice本文中の一人称の語りとして書かれており、
  内容が該当Voiceに割り当てられたLedger evidenceに実質的に対応する
  (本文中に出典明記がなくても、Voiceのナレーションである限りこれに該当する)
- FACTUAL_CLAIM_SUPPORTED_BUT_UNCITED: Voice本文ではない地の文(Tension/
  Closing等)で、具体的な比率・数値・研究名への言及を伴う客観的主張として
  書かれており、Ledgerには対応するevidenceがあるが、地の文としての出典明示が
  読者にとって本来期待される
- UNSUPPORTED_OR_UNVERIFIED: 上記Ledgerのどのevidenceにも実質的に対応せず、
  独立した検証(Web検索等)が必要、または明確に対応するevidenceがない

matched_evidence_idsには、対応すると判断したevidence ID(例: "1-01", "2-04")を
列挙してください(対応するものがなければ空配列)。

分類に加えて、should_still_require_review(このclaimは依然として人間レビューが
必要か)をtrue/falseで判定してください。ATTRIBUTION_ONLY_SUPPORTEDは原則false、
UNSUPPORTED_OR_UNVERIFIEDは原則trueとしてください。

【分類対象】
{claim_lines}

指定されたJSON形式のフィールドだけで回答してください。"""


def main_a2():
    client = OpenAI()
    prompt_a2 = build_candidate_a2_prompt(CLAIMS, LEDGER_VOICE_EVIDENCE_BLOCK)
    with open(f"{OUT_DIR}/candidate_a2_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt_a2)
    result_a2 = call_classifier(prompt_a2, CANDIDATE_A_SCHEMA, MODEL, REASONING_EFFORT, client)
    with open(f"{OUT_DIR}/candidate_a2_result.json", "w", encoding="utf-8") as f:
        json.dump(result_a2, f, ensure_ascii=False, indent=2)
    score_a2 = score(CLAIMS, result_a2["parsed"]["items"]) if result_a2["parsed"] else None
    with open(f"{OUT_DIR}/candidate_a2_score.json", "w", encoding="utf-8") as f:
        json.dump(score_a2, f, ensure_ascii=False, indent=2)
    print("=== Candidate A' (Voice-narration-aware, refined) ===")
    print(json.dumps(score_a2, ensure_ascii=False, indent=2))
    print(json.dumps(result_a2["usage"], ensure_ascii=False, indent=2))


if __name__ == "__main__" and os.environ.get("RUN_A2_ONLY"):
    main_a2()
