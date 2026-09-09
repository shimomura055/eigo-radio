# ============================================================
# er012_ai_screening_ledger_trial_01.py
# EDITORIAL-B-FAMILY-VOICES-AI-SCREENING-LEDGER-TRIAL-01
# ============================================================
# Lane: Lane B / B Family(Voices-Perspective)。Trial専用スクリプト
# (Production Prompt/registry/本文生成は一切行わない)。
#
# 目的: 4V本文Trial(テーマ固定 "Should companies use AI to screen job
# applicants?"、4V=案A: Applicant / Recruiter・Hiring Manager /
# Business・Efficiency / Fairness・Legal・HR Governance)に先立ち、検証済み
# Verified Fact Ledger(4 Voice版)をこのTrialだけで先に作成する。
#
# Research方針(Reconciliation Check結果): B-Family Voice Ledgerの実際の
# 先例(EDITORIAL-B-FAMILY-VOICES-TRIAL-04/05/06/07)は、いずれも
# er011_open112_engagement_reference_cross_topic_ab_trial_11.pyの
# _perplexity_call()パターンを各Trialファイル内に再実装したもの(Perplexity
# sonar-pro、Stage 1B: stakeholder視点fact research、Stage 2B: 独立
# verification)であり、er002_ja_web_research_r3.pyのWriter/FactChecker用
# web_search関数(OpenAI Responses API、A-Family全文生成Writerの一部として
# 設計されたもの、schemaも4-Voice stakeholder fact向けではない)ではない。
# 本Trialでは「新規Research primitiveの独自実装をしない」という制約を、
# 「既存の承認済みPerplexity呼び出しパターンを、Trial-04〜07と全く同じ
# コードのまま(schema/prompt文言のみテーマに合わせて差し替えて)再利用する」
# という意味で満たす(Trial-04〜07自身がこの前提で運用されている)。
# なお本ファイルはer002_ja_web_research_r3もimportし、後段の品質確認
# (build_fact_check_prompt()がvoice_attribution_block込みで読めるか)の
# read-only呼び出しにのみ使う(本文生成・Fact Checker実行は行わない)。
#
# 禁止: Production Prompt/registry編集、SSOT・Git操作、本文生成、音声生成、
# 未検証事実の記載、Research primitiveの独自実装、バックグラウンド待機。
#
# 到達してよいStatus: VALIDATED / REJECTED / USER_DECISION_REQUIRED のみ
# (Production採用判断はしない。Trial用入力資産としての形式・代表性チェック
# のみ)。
from __future__ import annotations

import json
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import requests
from dotenv import load_dotenv

load_dotenv()

import er002_ja_web_research_r3 as r3  # noqa: E402  (read-only互換確認用)
import er005_cost_logger as cl  # noqa: E402

THEME_ID = "editorial_b_family_ai_screening_ledger_trial_01"
OUT_DIR = "er012_output/ai_screening_ledger_trial_01"
RESEARCH_DIR = f"{OUT_DIR}/research"

os.makedirs(RESEARCH_DIR, exist_ok=True)

# ============================================================
# Research: Perplexity sonar-pro
# (Trial-04〜07の_perplexity_call()と完全に同一の実装、無変更でコピー)
# ============================================================
PERPLEXITY_MODEL = "sonar-pro"


def _perplexity_call(theme_id: str, stage: str, model: str, messages: list[dict],
                      response_format: dict | None = None, timeout: float = 180.0) -> dict:
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return {"status": "CREDENTIAL_REQUIRED"}
    payload = {"model": model, "messages": messages}
    if response_format:
        payload["response_format"] = response_format
    t0 = time.time()
    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload, timeout=timeout,
    )
    elapsed = round(time.time() - t0, 3)
    success = resp.status_code == 200
    if not success:
        cl.record({
            "provider": "perplexity", "api": "chat_completions", "model_id": model, "stage": stage,
            "attempt_number": 1, "success": False, "elapsed_seconds": elapsed,
            "usage_source": "N/A_FAILED_CALL", "http_status": resp.status_code,
        })
        return {"status": "FAILED", "http_status": resp.status_code, "elapsed_seconds": elapsed,
                "body": resp.text[:800]}
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    cl.record({
        "provider": "perplexity", "api": "chat_completions", "model_id": data.get("model"), "stage": stage,
        "theme": theme_id, "attempt_number": 1, "success": True, "elapsed_seconds": elapsed,
        "usage_source": "OFFICIAL_API_RESPONSE", "http_status": resp.status_code,
        "input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
    })
    return {
        "status": "OK", "content": content, "citations": data.get("citations", []),
        "search_results": data.get("search_results", []), "model": data.get("model"),
        "response_id": data.get("id"), "elapsed_seconds": elapsed, "usage": usage,
    }


FACT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "facts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fact_id": {"type": "string"},
                    "verified_fact": {"type": "string", "description": "事実そのものの説明(日本語または英語)"},
                    "number_or_stat": {"type": ["string", "null"]},
                    "actor_or_organization": {"type": ["string", "null"]},
                    "stance_or_position": {
                        "type": "string",
                        "description": "この事実がどの立場を支持するか(例: Applicant/応募者、"
                                       "Recruiter・Hiring Manager/採用担当、Business・Efficiency/"
                                       "経営・効率重視、Fairness・Legal・HR Governance/公平性・法規制・"
                                       "HRガバナンス、または共通背景=common)",
                    },
                    "interest_or_stake": {"type": "string", "description": "その立場が何を重視しているか"},
                    "evidence_strength": {
                        "type": "string",
                        "description": "official_statistics / government_official_announcement / "
                                        "company_official_announcement / reputable_media_reporting / "
                                        "industry_survey / private_analysis / advocacy_or_opinion / anecdotal のいずれか",
                    },
                    "counter_or_limitation": {"type": ["string", "null"]},
                    "time_window": {"type": ["string", "null"]},
                    "source_name": {"type": "string"},
                    "source_url": {"type": ["string", "null"]},
                    "publication_date": {"type": ["string", "null"]},
                },
                "required": ["fact_id", "verified_fact", "number_or_stat", "actor_or_organization",
                             "stance_or_position", "interest_or_stake", "evidence_strength",
                             "counter_or_limitation", "time_window", "source_name", "source_url",
                             "publication_date"],
            },
        },
    },
    "required": ["facts"],
}

FACT_RESEARCH_PROMPT = """あなたはニュース記事のFact Checker/Researcherです。以下のテーマについて、
2026年9月時点で実在する当事者(具体的な役割・組織・肩書を持つ人、または明確に定義された
属性グループ)が、実際に何を経験し、何を大切にし、何を必要とし、何を心配し、何に責任を
持ち、何を得て何を失うのかが分かる、具体的な事実(発言・インタビュー・体験談・当事者を
対象にした調査結果・実在する法規制・公的資料)を調べてください。

【テーマ】
企業が採用選考でAI(応募書類のスクリーニング、適性テストのスコアリング、動画面接の
自動評価など)を使うべきかどうか(Should companies use AI to screen job applicants?)。
英語圏(米国・英国等)・日本の事例のいずれも対象。

【調査対象として重視してほしい4つの立場(必ずこの4つ全てについて、実在の発言・調査・
資料に基づくfactを集めてください。単一の立場に偏らないでください)】
1. Applicant(応募者): AIスクリーニングを受ける側の応募者が、実際に何を経験し、何を
   不安に感じ、何を不公平だと感じているか(例: 落選理由が分からない、バイアスへの懸念、
   AIに「対策」しなければならないというプレッシャー、実際にAI選考で不利益を受けたと
   証言する応募者の実例)
2. Recruiter・Hiring Manager(採用担当・人事責任者): 実際にAIツールを業務で使う、または
   使うかどうかを判断する立場の人が、何を効率化として評価し、何を懸念しているか(応募者
   数の急増への対応、時間短縮、精度への疑問、最終判断への関与度 等)
3. Business・Efficiency(経営・事業効率の立場): 経営者・事業責任者が、コスト削減・
   採用スピード・スケーラビリティの観点からAI選考導入をどう評価しているか(実在する
   企業の導入事例・経営层の発言・ROIに関する調査)
4. Fairness・Legal・HR Governance(公平性・法規制・HRガバナンスの立場): 弁護士・
   規制当局・研究者・人事ガバナンス専門家が、AI採用選考の合法性・公平性・監査可能性に
   ついて何を指摘しているか(実在する法規制の現状、例えばNYC Local Law 144、EU AI Act
   のハイリスクAI分類、米国EEOC/州法の動き、日本国内の議論があれば、監査・バイアス
   検証の実務)

【共通evidence(Hook/Tension/Closing用)】
上記4つの立場のfactに加え、共通背景として以下も収集してください: 企業のAI採用ツール
導入率(実在する調査)、法規制の現状(上記Fairness/Legal項目と重複してよい)、AI
スクリーニングツールを提供する主要企業・製品の実例。

【出力ルール】
- 最低16件、できれば24件以上のfactを、実際に検索で確認できたものだけ出力してください
- 検索で確認できない推測・一般論は書かないでください
- 各factについて、number_or_stat、actor_or_organization、stance_or_position、
  interest_or_stake、evidence_strength、counter_or_limitation、time_window、source_name、
  source_url、publication_dateを可能な限り埋めてください。分からない項目はnullにしてください
- stance_or_positionには、上記4つの立場のいずれか(applicant / recruiter_hiring_manager /
  business_efficiency / fairness_legal_hr_governance)、または共通背景の場合はcommonと
  明記してください
- 4つの立場それぞれについて、最低3件以上のfactを含めてください(単一の立場に偏らない
  ことを厳守してください)
- evidence_strengthは、公式統計/政府発表/企業公式発表/大手メディア報道/業界調査/民間分析/
  意見記事/anecdotalのどれに当たるかを区別してください
"""


def research_facts() -> dict:
    with cl.logging_context(THEME_ID, "research_facts"):
        result = _perplexity_call(
            THEME_ID, "research_facts", PERPLEXITY_MODEL,
            [{"role": "user", "content": FACT_RESEARCH_PROMPT}],
            response_format={"type": "json_schema", "json_schema": {"schema": FACT_JSON_SCHEMA}})
    return result


VERIFICATION_PROMPT = """あなたは独立したFact Verifierです。以下は、別の調査担当が先に作成した
factのリストです。あなたはこのリストを事前情報として与えられていますが、それを鵜呑みにせず、
それぞれのfactについて改めて独立に検索し、以下を判定してください:

- CONFIRMED(独立した検索で同じ内容が確認できた)
- PARTIALLY_CONFIRMED(数字や日付など一部に食い違いがある。食い違いの内容を具体的に書く)
- COULD_NOT_CONFIRM(独立した検索で確認できなかった)
- CONTRADICTED(独立した検索結果と矛盾する)

【検証対象のfactリスト】
{facts_json}

各factについて、fact_id、verdict、explanation(判定理由。食い違いがあれば具体的な数字・日付を
挙げて説明)、independent_source_name、independent_source_url を出力してください。
"""

VERIFICATION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "verifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fact_id": {"type": "string"},
                    "verdict": {"type": "string",
                                "enum": ["CONFIRMED", "PARTIALLY_CONFIRMED", "COULD_NOT_CONFIRM", "CONTRADICTED"]},
                    "explanation": {"type": "string"},
                    "independent_source_name": {"type": ["string", "null"]},
                    "independent_source_url": {"type": ["string", "null"]},
                },
                "required": ["fact_id", "verdict", "explanation", "independent_source_name",
                             "independent_source_url"],
            },
        },
    },
    "required": ["verifications"],
}


def verify_facts(facts_json_text: str) -> dict:
    prompt = VERIFICATION_PROMPT.format(facts_json=facts_json_text)
    with cl.logging_context(THEME_ID, "verify_facts"):
        result = _perplexity_call(
            THEME_ID, "verify_facts", PERPLEXITY_MODEL,
            [{"role": "user", "content": prompt}],
            response_format={"type": "json_schema", "json_schema": {"schema": VERIFICATION_JSON_SCHEMA}})
    return result


def run_research_stage() -> None:
    cl.install(f"{OUT_DIR}/raw_usage_log_ledger_trial01_research.jsonl")
    print("[LEDGER-TRIAL-01][Research] Stage 1B: 4-stakeholder視点のfact research"
          "(Perplexity sonar-pro)開始...")
    facts_result = research_facts()
    with open(f"{RESEARCH_DIR}/raw_facts_research_4voice.json", "w", encoding="utf-8") as f:
        json.dump(facts_result, f, ensure_ascii=False, indent=2, default=str)
    if facts_result.get("status") != "OK":
        print(f"[LEDGER-TRIAL-01][Research] fact research失敗: {facts_result}")
        return
    print(f"[LEDGER-TRIAL-01][Research] Stage 1B完了。model={facts_result.get('model')} "
          f"response_id={facts_result.get('response_id')}")

    print("[LEDGER-TRIAL-01][Research] Stage 2B: 独立verification(Perplexity sonar-pro)開始...")
    verify_result = verify_facts(facts_result["content"])
    with open(f"{RESEARCH_DIR}/raw_facts_verification_4voice.json", "w", encoding="utf-8") as f:
        json.dump(verify_result, f, ensure_ascii=False, indent=2, default=str)
    if verify_result.get("status") != "OK":
        print(f"[LEDGER-TRIAL-01][Research] verification失敗: {verify_result}")
        return
    print(f"[LEDGER-TRIAL-01][Research] Stage 2B完了。model={verify_result.get('model')} "
          f"response_id={verify_result.get('response_id')}")
    print("[LEDGER-TRIAL-01][Research] 完了。raw結果をresearch/配下に保存しました。"
          "次に手作業でVoice別Verified Fact Ledgerをcurationしてください。")


# ============================================================
# Round 2(追加Research): Round 1の結果を実査した結果、
# fairness_legal_hr_governance(NYC Local Law 144関連)に事実が偏り、
# applicant/business_efficiency/recruiter側が薄い・個人の生きた経験に
# 乏しいことが判明したため、代表性を補うための追加Stage 1B/2Bを実施する。
# Round 1と同じ_perplexity_call()パターンをそのまま再利用(新規ロジック
# なし)。
# ============================================================
FACT_RESEARCH_PROMPT_ROUND2 = """あなたはニュース記事のFact Checker/Researcherです。以下のテーマについて、
2026年9月時点で実在する当事者の具体的な事実を追加で調べてください(既に一部Research済み
ですが、NYC Local Law 144の監査要件に事実が偏っていたため、それ以外の角度を優先してください)。

【テーマ】
企業が採用選考でAI(応募書類のスクリーニング、適性テストのスコアリング、動画面接の
自動評価など)を使うべきかどうか(Should companies use AI to screen job applicants?)。

【今回優先してほしい角度(NYC Local Law 144の監査要件の説明は今回は不要です。それ以外を
探してください)】
1. Applicant(応募者)個人の生きた経験: 実名または具体的な個人が、AIスクリーニングで
   落選した・不利益を受けたと証言している実際のニュース記事・訴訟・体験談(米国・英国・
   日本いずれも可)
2. Recruiter・Hiring Manager(採用担当)の実際の利用実感: 採用担当者が実際にAIツールを
   使ってみてどう感じたか(時間短縮の実感、精度への疑問、応募者からの反発への対応、
   最終判断にどこまでAIを関与させているか)についての、実在する調査・記事・発言
3. Business・Efficiency(経営・効率)の定量的な効果: 企業がAI採用ツールでどれだけ
   採用スピード・コスト・応募者数処理能力を改善したと報告しているか(実在する企業の
   導入事例、業界調査によるROI・時間短縮の数値)
4. 共通背景としてのAI採用ツール導入率: 業界全体でどれくらいの企業が採用選考にAIを
   使っているか(SHRM、Gartner、LinkedIn、その他信頼できる調査機関による実在の数値)、
   および米国以外の法規制の動き(EU AI Actにおける採用AIの「high-risk」分類など)

【出力ルール】
- 最低10件、できれば16件以上のfactを、実際に検索で確認できたものだけ出力してください
- 検索で確認できない推測・一般論は書かないでください
- 各factについて、number_or_stat、actor_or_organization、stance_or_position、
  interest_or_stake、evidence_strength、counter_or_limitation、time_window、source_name、
  source_url、publication_dateを可能な限り埋めてください。分からない項目はnullにしてください
- stance_or_positionには、applicant / recruiter_hiring_manager / business_efficiency /
  fairness_legal_hr_governance / common のいずれかを明記してください
- 4つの立場(fairness_legal_hr_governanceも含む、ただしLL144監査要件の繰り返しは不要、
  EU AI Act等の別角度で)それぞれについて、最低2件以上のfactを含めてください
"""


def research_facts_round2() -> dict:
    with cl.logging_context(THEME_ID, "research_facts_round2"):
        result = _perplexity_call(
            THEME_ID, "research_facts_round2", PERPLEXITY_MODEL,
            [{"role": "user", "content": FACT_RESEARCH_PROMPT_ROUND2}],
            response_format={"type": "json_schema", "json_schema": {"schema": FACT_JSON_SCHEMA}})
    return result


def verify_facts_round2(facts_json_text: str) -> dict:
    prompt = VERIFICATION_PROMPT.format(facts_json=facts_json_text)
    with cl.logging_context(THEME_ID, "verify_facts_round2"):
        result = _perplexity_call(
            THEME_ID, "verify_facts_round2", PERPLEXITY_MODEL,
            [{"role": "user", "content": prompt}],
            response_format={"type": "json_schema", "json_schema": {"schema": VERIFICATION_JSON_SCHEMA}})
    return result


def run_research_stage_round2() -> None:
    cl.install(f"{OUT_DIR}/raw_usage_log_ledger_trial01_research_round2.jsonl")
    print("[LEDGER-TRIAL-01][Research round2] Stage 1B開始...")
    facts_result = research_facts_round2()
    with open(f"{RESEARCH_DIR}/raw_facts_research_4voice_round2.json", "w", encoding="utf-8") as f:
        json.dump(facts_result, f, ensure_ascii=False, indent=2, default=str)
    if facts_result.get("status") != "OK":
        print(f"[LEDGER-TRIAL-01][Research round2] fact research失敗: {facts_result}")
        return
    print(f"[LEDGER-TRIAL-01][Research round2] Stage 1B完了。model={facts_result.get('model')}")

    print("[LEDGER-TRIAL-01][Research round2] Stage 2B開始...")
    verify_result = verify_facts_round2(facts_result["content"])
    with open(f"{RESEARCH_DIR}/raw_facts_verification_4voice_round2.json", "w", encoding="utf-8") as f:
        json.dump(verify_result, f, ensure_ascii=False, indent=2, default=str)
    if verify_result.get("status") != "OK":
        print(f"[LEDGER-TRIAL-01][Research round2] verification失敗: {verify_result}")
        return
    print(f"[LEDGER-TRIAL-01][Research round2] Stage 2B完了。model={verify_result.get('model')}")
    print("[LEDGER-TRIAL-01][Research round2] 完了。")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "round2":
        run_research_stage_round2()
    else:
        run_research_stage()
