# ============================================================
# er003_v1_en_direct_vfl_01_generate.py
# ER-003-EN-DIRECT-VFL-01: Verified Fact Ledger方式 A02再実証
# ============================================================
# ER-003-EN-DIRECT-FACT-01のRoot Cause Auditを踏まえ、英語直接生成の
# writerの前段に「Researcher(事実収集)→独立Verification→Verified
# Fact Ledger確定」という工程を追加した実験パイプライン。
#
# 設計思想: Researcherが「何が事実か」を決め、Writerは「その事実を
# どう面白く伝えるか」だけを決める。WriterにFact researchと
# Narrative designを同時に背負わせない。
#
# Production(er002_ja_article_generation.py / er002_ja_web_research_r3.py /
# er003_v1_en_direct_ab_01_generate.py)は一切変更せず、この独立
# スクリプトから関数を読み取り専用でimportするのみ。
#
# writerはこの実験では原則Web検索を使用しない(tools引数を渡さない)。
# 事実入力はVerified Fact Ledgerのみとする。技術的にWeb検索toolを
# 外せない事情が生じた場合は、この方針を勝手に変更せず報告する
# (今回はResponses APIでtools引数を単純に省略するだけで実現でき、
# 技術的な障害はなかった)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_en_direct_vfl_01_generate.py

from __future__ import annotations

import json
import os
import time

from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er002_ja_free_markdown_restore_r2 as restore_r2
import er003_v1_en_direct_ab_01_generate as ab01
import er006_model_routing_contract_01 as routing

load_dotenv()

TOPIC_ID = "A02"
TOPIC = "英国の未成年向け夜間SNS設定"
MASTER_PATH = "er002_v1_2m_masters/hanshin_ja_master.txt"
OUT_DIR = "er003_output/en_direct_vfl_01/A02"

# ER-009-N1-POINT-RETRY-ROUTING-GOVERNANCE-10(2026-08-30)で修正: 以前は
# r3.WRITER_MODEL(ER-002era、"gpt-5.6-sol"のhardcoded literalへ連鎖する
# 古い参照)をそのまま使っており、「Production writerと同一モデル」という
# コメント上の意図に反して、ER-006-MODEL-ROUTING-CONTRACT-01(2026-08-22、
# WriterをLunaへ正式変更)に追従していなかった。このMODELはvfl01からimport
# する多数のDEV/Trialスクリプト(cefr_direct/spoken_first/iran01/
# b1_scaffold/en_direct_vfl_02/er009_n1系等)が`model=MODEL`として直接
# 使うため、参照元をRouting SSOTへ張り替えることで全て一括で追従させる
# (Production本体のer003_v1_n3_01_articles_generate.pyはこのMODEL変数を
# API callへ使っておらず、常にrouting.require_model()を直接呼ぶため影響
# 範囲外)。
MODEL = routing.WRITER_MODEL  # "gpt-5.6-luna"(旧: r3.WRITER_MODEL = "gpt-5.6-sol")
REASONING_EFFORT = r3.WRITER_REASONING_EFFORT  # "high"

A_VERSION_WORD_COUNT = ab01.A_VERSION_WORD_COUNT  # 418(前回実験と同一基準)
LENGTH_LOWER_BOUND = ab01.LENGTH_LOWER_BOUND  # 355
LENGTH_UPPER_BOUND = ab01.LENGTH_UPPER_BOUND  # 481


def get_client():
    from openai import OpenAI
    return OpenAI()


def load_master_full_text() -> str:
    with open(MASTER_PATH, encoding="utf-8") as f:
        return f.read()


# ============================================================
# Step 1: Fact Ledger生成(Researcher、Web検索あり、Narrativeは書かない)
# ============================================================
FACT_LEDGER_JSON_SCHEMA = {
    "name": "verified_fact_ledger_draft",
    "schema": {
        "type": "object",
        "properties": {
            "facts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "fact_id": {"type": "string"},
                        "claim": {"type": "string"},
                        "subject": {"type": "string"},
                        "date_or_period": {"type": ["string", "null"]},
                        "scope": {"type": ["string", "null"]},
                        "conditions": {"type": ["string", "null"]},
                        "numeric_value": {"type": ["string", "null"]},
                        "numeric_scope": {"type": ["string", "null"]},
                        "causal_strength": {
                            "type": "string",
                            "enum": ["OBSERVED_REPORTED", "CORRELATIONAL", "CAUSAL_STATED_BY_SOURCE", "NOT_APPLICABLE"],
                        },
                        "source_title": {"type": "string"},
                        "source_url": {"type": "string"},
                        "source_type": {
                            "type": "string",
                            "enum": ["PRIMARY_GOVERNMENT_OR_REGULATOR", "OFFICIAL_REPORT_OR_STUDY", "RELIABLE_SECONDARY_NEWS", "OTHER"],
                        },
                        "support_level": {
                            "type": "string",
                            "enum": ["DIRECTLY_STATED", "INFERRED_FROM_SOURCE", "PARTIALLY_STATED"],
                        },
                        "ambiguity": {"type": ["string", "null"]},
                        "notes_for_writer": {"type": ["string", "null"]},
                    },
                    "required": [
                        "fact_id", "claim", "subject", "date_or_period", "scope", "conditions",
                        "numeric_value", "numeric_scope", "causal_strength", "source_title",
                        "source_url", "source_type", "support_level", "ambiguity", "notes_for_writer",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["facts"],
        "additionalProperties": False,
    },
    "strict": True,
}

RESEARCHER_DEVELOPER_MESSAGE = (
    "あなたはFact Researcherです。記事本文・Narrative・比喩は一切書かず、"
    "構造化されたFactだけを収集・整理してください。"
)

RESEARCHER_PROMPT_TEMPLATE = """今回のテーマについて、Webで調査し、Verified Fact Ledgerの下書きを作成してください。

【今回のテーマ】
{topic}

【役割】
あなたはResearcherです。以下を行いません:
- 記事本文を書く
- Narrativeを作る
- 比喩を考える
- 阪神マスターのstyleを模倣する
あなたが行うのは、Factだけを収集・整理することです。

【Source優先順位】
1. 政府・規制当局等の一次資料
2. 公式調査・報告書
3. 信頼できる二次資料
一次Sourceで確認できるFactを、二次Sourceだけで確定しないでください。

【特に注意して構造化すべき観点(今回のテーマに当てはまる場合のみ)】

1. 対象範囲: 年齢・人数・期間・地域等、Factが適用される範囲(scope)を数値の母集団と混同せずに特定する
2. 制度・仕様の適用条件: default設定なのか常時適用なのか、変更・例外が認められるか等、時間的・条件的scopeを明確にする。一次資料内で表現が揺れている場合は、より明確な一次Sourceを追加で検索する。それでも確定できない場合は、断定せずambiguityフィールドへその旨を明記する
3. 数値の内訳: ある数字が全体を指すのか、特定のサブグループ・条件を指すのかを明確にする。一次資料で直接確認できる場合のみnumeric_valueとして確定し、確認できない場合は推測で数字を作らず、numeric_valueをnullにしてambiguityへその旨を記録する
4. 観察・相関・因果の区別: 変化・効果・傾向等について、観察・報告なのか、相関なのか、Source自身が因果関係を主張しているのかを、causal_strengthで区別する。Sourceより強い因果表現(caused/produced/proved等)を後工程のwriterが使わないよう、causal_strengthとnotes_for_writerで明示する

【出力形式】
各Factについて、fact_id・claim・subject・date_or_period・scope・conditions・numeric_value・
numeric_scope・causal_strength・source_title・source_url・source_type・support_level・
ambiguity・notes_for_writerを埋めてください(該当しない項目はnullで構いません)。
数字・期間・対象範囲があるFactについては、該当項目を必ず明示してください。"""


def build_researcher_prompt(topic: str = TOPIC) -> str:
    return RESEARCHER_PROMPT_TEMPLATE.format(topic=topic)


def run_researcher(client) -> dict:
    prompt = build_researcher_prompt()
    response = client.responses.create(
        model=MODEL,
        reasoning={"effort": REASONING_EFFORT},
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **FACT_LEDGER_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": RESEARCHER_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    search_usage = r3.extract_web_search_usage(response)
    sources = r3.extract_sources(response)
    parsed = json.loads(text)
    return {
        "prompt": prompt, "raw_text": text, "parsed": parsed, "model": response.model,
        "response_id": response.id, "search_usage": search_usage, "sources": sources,
    }


# ============================================================
# Step 2: Fact Ledger Verification(writerとは独立した別API呼び出し)
# ============================================================
VERIFICATION_JSON_SCHEMA = {
    "name": "fact_ledger_verification",
    "schema": {
        "type": "object",
        "properties": {
            "verifications": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "fact_id": {"type": "string"},
                        "verdict": {"type": "string", "enum": ["VERIFIED", "AMBIGUOUS", "REJECTED"]},
                        "verification_notes": {"type": "string"},
                    },
                    "required": ["fact_id", "verdict", "verification_notes"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["verifications"],
        "additionalProperties": False,
    },
    "strict": True,
}

VERIFICATION_DEVELOPER_MESSAGE = (
    "あなたはFact Ledgerの独立検証担当です。Ledgerを書き直さず、各Factの正しさだけを判定してください。"
)

VERIFICATION_PROMPT_TEMPLATE = """以下のFact Ledger下書きを、Ledger自身のsource_urlだけを鵜呑みにせず、
独立してWeb検索により再照合してください。

【対象テーマ】
{topic}

【検証対象のFact Ledger下書き】
{ledger_json}

【検証観点】
- FactがSourceに実際に存在するか
- 数字のscopeが正しいか(母集団と個別条件を混同していないか)
- 対象群と全体を混同していないか
- 日付・時間帯が正しいか
- 制度の適用範囲が正しいか(特に時間帯限定かどうか)
- 条件が抜けていないか
- 因果関係を過剰に強めていないか
- Source間で矛盾していないか
- 曖昧なFactを無理に確定していないか

各fact_idについて、VERIFIED / AMBIGUOUS / REJECTEDのいずれかで判定し、
判定理由をverification_notesへ記載してください。"""


def build_verification_prompt(topic: str, ledger_parsed: dict) -> str:
    ledger_json = json.dumps(ledger_parsed, ensure_ascii=False, indent=2)
    return VERIFICATION_PROMPT_TEMPLATE.format(topic=topic, ledger_json=ledger_json)


def run_verification(client, ledger_parsed: dict) -> dict:
    prompt = build_verification_prompt(TOPIC, ledger_parsed)
    response = client.responses.create(
        model=MODEL,
        reasoning={"effort": REASONING_EFFORT},
        tools=[{"type": "web_search"}],
        text={"format": {"type": "json_schema", **VERIFICATION_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": VERIFICATION_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    search_usage = r3.extract_web_search_usage(response)
    sources = r3.extract_sources(response)
    parsed = json.loads(text)
    return {
        "prompt": prompt, "raw_text": text, "parsed": parsed, "model": response.model,
        "response_id": response.id, "search_usage": search_usage, "sources": sources,
    }


def build_verified_ledger_text(ledger_parsed: dict, verification_parsed: dict) -> tuple:
    verdict_map = {v["fact_id"]: v for v in verification_parsed["verifications"]}
    lines = []
    counts = {"VERIFIED": 0, "AMBIGUOUS": 0, "REJECTED": 0}
    kept_facts = []
    for fact in ledger_parsed["facts"]:
        v = verdict_map.get(fact["fact_id"])
        verdict = v["verdict"] if v else "AMBIGUOUS"
        counts[verdict] = counts.get(verdict, 0) + 1
        if verdict == "REJECTED":
            continue
        kept_facts.append({**fact, "verification_verdict": verdict,
                            "verification_notes": v["verification_notes"] if v else "(検証結果なし、安全側でAMBIGUOUS扱い)"})
        tag = "[VERIFIED]" if verdict == "VERIFIED" else "[AMBIGUOUS - 断定禁止、曖昧さを保持すること]"
        lines.append(f"{tag} {fact['fact_id']}: {fact['claim']}")
        if fact.get("scope"):
            lines.append(f"  scope: {fact['scope']}")
        if fact.get("conditions"):
            lines.append(f"  conditions: {fact['conditions']}")
        if fact.get("numeric_value"):
            lines.append(f"  numeric_value: {fact['numeric_value']} (numeric_scope: {fact.get('numeric_scope') or '未指定'})")
        if fact.get("date_or_period"):
            lines.append(f"  date_or_period: {fact['date_or_period']}")
        if fact.get("causal_strength") and fact["causal_strength"] != "NOT_APPLICABLE":
            lines.append(f"  causal_strength: {fact['causal_strength']}")
        if verdict == "AMBIGUOUS":
            lines.append(f"  ambiguity_note: {fact.get('ambiguity') or v.get('verification_notes', '')}")
        if fact.get("notes_for_writer"):
            lines.append(f"  notes_for_writer: {fact['notes_for_writer']}")
        lines.append("")
    return "\n".join(lines), counts, kept_facts


# ============================================================
# Step 3: English Narrative Writer(Web検索なし、Verified Fact Ledgerのみ使用)
# ============================================================
WRITER_DEVELOPER_MESSAGE = "英語の記事を作成してください。"

WRITER_PROMPT_TEMPLATE = """以下は、私が良いと評価している日本語記事です。

【マスター記事】

{hanshin_master_full_text}

【今回のテーマ】

{topic}

この阪神記事が良いのは、全体の概要を面白く展開し、ポイントでは本文とは別の切り口から解説し、
最後に一言でまとめることで、聞き手が飽きない設計になっている点です。

このセンスで、今回のテーマの記事全文をMarkdownで書いてください。

阪神や野球固有の表現をコピーするのではなく、今回の題材に合う表現を使ってください。

ポイント部分には、Markdownの「###」見出しをちょうど2つ置いてください。

【今回のFact源について(重要)】
今回は、あなた自身によるWeb検索や新しい具体的事実の追加を行わないでください。
以下のVerified Fact Ledgerだけを事実源として使用してください。

{verified_ledger_text}

【Fact Ledger使用上の制約】
- Verified Fact Ledgerにない具体的Factを追加しないでください
- 数字を別のscopeへ結び付けないでください(例: 全体の参加者数を特定の条件群の人数として書かない)
- 時間条件を別の制度項目へ拡張しないでください(例: ある制度がmidnight-6amに限定されるとしても、別の制度項目まで同じ時間帯に限定されるとは書かない)
- [AMBIGUOUS]と印のあるFactは断定しないでください。曖昧さを保ったまま書くか、記事から省いてください
- 複数のFactを物語として自然にまとめてもかまいませんが、Fact同士の関係(誰が・何を・いつ・どの範囲で)を変えないでください
- Sourceにない導入の場面描写(scene-setting)自体は使ってかまいません。ただし、その場面描写に具体的なFact claim(数字・制度の適用条件等)を接続しないでください

記事本文の分量は、目安{a_version_word_count}語程度、許容範囲は{lower_bound}語から{upper_bound}語としてください
(目安であり、厳密な制約ではありません)。"""


def build_writer_prompt(master_full_text: str, verified_ledger_text: str) -> str:
    return WRITER_PROMPT_TEMPLATE.format(
        hanshin_master_full_text=master_full_text, topic=TOPIC,
        verified_ledger_text=verified_ledger_text,
        a_version_word_count=A_VERSION_WORD_COUNT,
        lower_bound=LENGTH_LOWER_BOUND, upper_bound=LENGTH_UPPER_BOUND,
    )


def run_writer_no_search(client, user_message: str, model: str = MODEL) -> dict:
    """Web検索toolを渡さない(tools引数を省略するだけで実現でき、技術的障害はなかった)。
    modelはER-006-MODEL-ROUTING-CONTRACT-01以降、呼び出し側がSSOT
    (er006_model_routing_contract_01)経由で明示指定できる(未指定時は
    モジュール既定のMODEL)。"""
    response = client.responses.create(
        model=model,
        reasoning={"effort": REASONING_EFFORT},
        input=[
            {"role": "developer", "content": WRITER_DEVELOPER_MESSAGE},
            {"role": "user", "content": user_message},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("writer応答が空です")
    return {"raw_text": text, "model": response.model, "response_id": response.id}


def run_writer_with_technical_retry(client, user_message: str, max_attempts: int = 2, model: str = MODEL) -> dict:
    attempts = []
    for attempt in range(1, max_attempts + 1):
        try:
            result = run_writer_no_search(client, user_message, model=model)
        except Exception as e:
            attempts.append({"attempt": attempt, "status": "TECHNICAL_FAILED", "error": f"{type(e).__name__}: {e}"})
            if attempt < max_attempts:
                time.sleep(2)
                continue
            return {"status": "TECHNICAL_GENERATION_FAILED", "attempts": attempts, "raw_text": None}
        structure = restore_r2.validate_point_structure(result["raw_text"])
        attempts.append({
            "attempt": attempt, "status": structure.status, "model": result["model"],
            "response_id": result["response_id"], "h3_count": structure.h3_count,
            "headings": structure.headings, "raw_text": result["raw_text"],
        })
        if structure.status == "STRUCTURE_PASS":
            return {"status": "STRUCTURE_PASS", "attempts": attempts, **result}
        if attempt < max_attempts:
            continue
        return {"status": "STRUCTURE_INVALID", "attempts": attempts, **result}
    return {"status": "TECHNICAL_GENERATION_FAILED", "attempts": attempts, "raw_text": None}


# ============================================================
# Step 5: Ledger逸脱チェック(fact checkerとは別、Ledgerとの整合性のみ確認)
# ============================================================
# ER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02: 旧v1判定(Ledger文言との
# lexical/scope的な厳密一致を暗黙に重視)は、意味を変えないparaphrase・
# A2/B1向け簡略化・Evidence間のbridge sentence・一般的な情景描写まで
# MAJORとして誤検知していたことがNo.9実データで判明した(詳細は
# DECISION_LOGのER-009-N1-LEDGER-DEVIATION-RECALIBRATION-02項目)。
# v2は「10種類の意味上のFact差分のいずれかが明確にtrueの場合のみ
# MAJOR」という基準に再設計し、No.9実データでの誤検知解消と、
# 意図的に危険な9種のfixture(数値/主体/scope/因果/確信度/否定/比較/
# 時期/新規主張の改変)全件のMAJOR検知維持を確認した上でProductionへ
# 反映した(候補検証は`er009_ledger_deviation_recalibration_02.py`/
# `er009_ledger_deviation_recalibration_02_test.py`)。
DEVIATION_FLAG_KEYS = [
    "changed_fact", "changed_scope", "changed_causality", "changed_certainty",
    "changed_number", "changed_actor", "changed_negation", "changed_comparison",
    "changed_time", "unsupported_new_claim",
]

DEVIATION_JSON_SCHEMA = {
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

DEVIATION_DEVELOPER_MESSAGE = (
    "あなたはLedger Fact Safetyの検証担当です。記事の面白さやスタイルは評価せず、"
    "意味上のFactがVerified Fact Ledgerの範囲内に収まっているかだけを判定してください。"
    "paraphrase・簡略化・語順変更・bridge sentence・文体の違いは、意味が変わらない限り"
    "deviationとして報告しないでください。"
)

DEVIATION_PROMPT_TEMPLATE = """以下の記事本文が、Verified Fact Ledgerが保証する「意味上のFact」の
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


def _apply_deviation_post_hoc_validation(raw_parsed: dict) -> dict:
    """モデルがseverity=MAJORを返したが10種類のフラグが全てfalseの場合、
    プロンプト違反とみなしMINORへ自動降格する。overall_statusは、この
    降格処理後にMAJORが1件でも残るかどうかをプログラム側で再計算する
    (モデルが自己申告するoverall_statusフィールドは使わない設計)。"""
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


def run_deviation_check(client, verified_ledger_text: str, article_text: str, model: str = MODEL) -> dict:
    prompt = DEVIATION_PROMPT_TEMPLATE.format(verified_ledger_text=verified_ledger_text, article_text=article_text)
    response = client.responses.create(
        model=model,
        reasoning={"effort": REASONING_EFFORT},
        text={"format": {"type": "json_schema", **DEVIATION_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": DEVIATION_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    raw_parsed = json.loads(text)
    parsed = _apply_deviation_post_hoc_validation(raw_parsed)
    return {"prompt": prompt, "raw_text": text, "raw_parsed": raw_parsed, "parsed": parsed,
            "model": response.model, "response_id": response.id}


# ============================================================
# メイン実行
# ============================================================
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    client = get_client()
    master_full_text = load_master_full_text()

    # --- Step 1: Fact Ledger生成 ---
    print("[VFL] Step1: Researcher呼び出し開始...")
    researcher_result = run_researcher(client)
    print(f"[VFL] Step1完了: facts={len(researcher_result['parsed']['facts'])} "
          f"web_search_calls={researcher_result['search_usage']['web_search_call_count']}")
    with open(f"{OUT_DIR}/fact_ledger_draft.json", "w", encoding="utf-8") as f:
        json.dump(researcher_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/researcher_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in researcher_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    # --- Step 2: Verification ---
    print("[VFL] Step2: Verification呼び出し開始...")
    verification_result = run_verification(client, researcher_result["parsed"])
    verdict_counts_raw = {}
    for v in verification_result["parsed"]["verifications"]:
        verdict_counts_raw[v["verdict"]] = verdict_counts_raw.get(v["verdict"], 0) + 1
    print(f"[VFL] Step2完了: {verdict_counts_raw} "
          f"web_search_calls={verification_result['search_usage']['web_search_call_count']}")
    with open(f"{OUT_DIR}/fact_ledger_verification.json", "w", encoding="utf-8") as f:
        json.dump(verification_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/verification_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in verification_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    verified_ledger_text, counts, kept_facts = build_verified_ledger_text(
        researcher_result["parsed"], verification_result["parsed"])
    with open(f"{OUT_DIR}/verified_fact_ledger.txt", "w", encoding="utf-8") as f:
        f.write(verified_ledger_text)
    with open(f"{OUT_DIR}/verified_fact_ledger_structured.json", "w", encoding="utf-8") as f:
        json.dump({"counts": counts, "kept_facts": kept_facts}, f, ensure_ascii=False, indent=2)
    print(f"[VFL] Verified Ledger確定: {counts}")

    writer_prompt = build_writer_prompt(master_full_text, verified_ledger_text)
    with open(f"{OUT_DIR}/audit/writer_prompt.txt", "w", encoding="utf-8") as f:
        f.write(writer_prompt)

    # --- Step 3+4+5: Run-1 / Run-2(独立生成、writer→fact checker→deviation check) ---
    for run_label in ("run1", "run2"):
        print(f"[VFL] {run_label}: writer呼び出し開始...")
        writer_result = run_writer_with_technical_retry(client, writer_prompt)
        with open(f"{OUT_DIR}/audit/{run_label}_writer_attempts.json", "w", encoding="utf-8") as f:
            json.dump(writer_result["attempts"], f, ensure_ascii=False, indent=2, default=str)

        if writer_result["status"] != "STRUCTURE_PASS" or not writer_result.get("raw_text"):
            print(f"[VFL] {run_label}: writer失敗 status={writer_result['status']}")
            continue

        raw_text = writer_result["raw_text"]
        with open(f"{OUT_DIR}/{run_label}_article.md", "w", encoding="utf-8") as f:
            f.write(raw_text)

        structure = restore_r2.validate_point_structure(raw_text)
        word_count = ab01.compute_word_count(raw_text)
        diagnostics = {
            "run": run_label, "model": writer_result["model"], "response_id": writer_result["response_id"],
            "technical_attempts": len(writer_result["attempts"]), "structure_status": structure.status,
            "h3_count": structure.h3_count, "word_count": word_count,
            "length_lower_bound_words": LENGTH_LOWER_BOUND, "length_upper_bound_words": LENGTH_UPPER_BOUND,
            "length_status": "WITHIN_SOFT_TARGET" if LENGTH_LOWER_BOUND <= word_count <= LENGTH_UPPER_BOUND else "OUTSIDE_SOFT_TARGET",
        }
        with open(f"{OUT_DIR}/{run_label}_diagnostics.json", "w", encoding="utf-8") as f:
            json.dump(diagnostics, f, ensure_ascii=False, indent=2)
        print(f"[VFL] {run_label}: word_count={word_count} structure={structure.status}")

        # 独立fact checker(Production r3ロジックをそのまま再利用、Web検索あり)
        print(f"[VFL] {run_label}: fact checker呼び出し開始...")
        fc_prompt = r3.build_fact_check_prompt(TOPIC, raw_text, [])

        def make_fc_fn():
            return r3.make_fact_checker_fn(fc_prompt)

        fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = r3.run_fact_checker_with_gates(
            make_fc_fn, sleep_fn=time.sleep)
        print(f"[VFL] {run_label}: fact_check status={fc_status} verdict={fc_result.get('verdict') if fc_result else None}")
        fact_qa_record = {
            "run": run_label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
            "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
            "attempts": len(fc_attempts), "result": fc_result,
        }
        with open(f"{OUT_DIR}/{run_label}_fact_qa.json", "w", encoding="utf-8") as f:
            json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
        with open(f"{OUT_DIR}/audit/{run_label}_fact_check_attempts.json", "w", encoding="utf-8") as f:
            json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

        # Ledger逸脱チェック
        print(f"[VFL] {run_label}: ledger逸脱チェック開始...")
        deviation_result = run_deviation_check(client, verified_ledger_text, raw_text)
        print(f"[VFL] {run_label}: deviation overall_status={deviation_result['parsed']['overall_status']} "
              f"deviations={len(deviation_result['parsed']['deviations'])}")
        with open(f"{OUT_DIR}/{run_label}_ledger_deviation.json", "w", encoding="utf-8") as f:
            json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
        with open(f"{OUT_DIR}/audit/{run_label}_deviation_full_record.json", "w", encoding="utf-8") as f:
            json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False, indent=2, default=str)

    print("[VFL] 完了。")


if __name__ == "__main__":
    main()
