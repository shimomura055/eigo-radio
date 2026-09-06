# ============================================================
# er012_editorial_b_voices_trial_04.py
# EDITORIAL-B-FAMILY-VOICES-TRIAL-04
# ============================================================
# Lane: Lane B / B Family(Voices-Perspective)。Lane A(OPEN-112/OPEN-117/
# ER-011系)とは独立。管理IDはEDITORIAL-B-FAMILY-VOICES-TRIAL-04。
#
# 目的: EDITORIAL-B-FAMILY-VOICES-TRIAL-03(初回Research Trial)に対する
# ユーザー評価(Voice選びがDiscovery寄りのEvidence/分析軸比較になっていた、
# 体裁が硬い、構成が基本形から外れた)を踏まえ、テーマは変更せず(「固定席
# 復活」、POOL_TOPIC_MASTER.md No.7)、Focus Module(Voices/Perspective
# Focus Module Block)の修正だけでVoicesらしい記事へ改善できるかを再Trial
# する(ユーザー承認済み、2026-09-06、管理ID EDITORIAL-B-FAMILY-VOICES-
# TRIAL-04)。
#
# Research方針: Trial-03のResearch成果(research/配下)を再利用しつつ、
# 「実在するstakeholder perspective(当事者の経験・発言・利害)」が不足して
# いたため、既存の承認済みPerplexity(sonar-pro)呼び出しパターン
# (er011_open112_engagement_reference_cross_topic_ab_trial_11.pyの
# _perplexity_call()を参照して本ファイル内に再実装、新規Production
# Researcherモジュールは作らない)で追加Research(Stage 1B/2B)を行い、
# 個々の当事者が何を経験し・何を大切にし・何を必要とし・何を心配し・
# 何に責任を持ち・何を得て何を失うかに焦点を当てたfactを収集し独立
# verificationを行う。その後Perspective候補(3〜5件)をTrial-03の候補と
# 合わせて抽出し、重複排除・質的基準で2件を選び、Voice設計表付きの
# Verified Fact Ledgerを手作業でcurationする(Trial-03/11と同じ方式)。
#
# Ledger→Writer: Production Writer本体(er003_v1_n3_01_articles_generate.py
# のCOMMON_BLOCK_TEMPLATE/run_one_pattern等)は一切変更しない。B Family
# Common Skeleton(Layer2案)+ Voices Focus Module(Layer3案)を、既存の
# ANCHOR挿入方式(Trial-05/09/10/11と同じ手法)でTrial側からprompt末尾へ
# 追加する。
#
# Point Overlap QA / Point Value QA: ユーザー決定によりmonitoring専用
# (gateにしない、retryを誘発しない)。Production run_one_pattern()は
# これらのQAがflaggedの場合に記事全体retry(最大2回)・NG_REVIEW_REQUIRED
# 早期returnを行う設計のため、そのまま使うとgate化されてしまう。そのため
# 本ファイルにrun_one_pattern()相当のTrial adapter(run_voices_pattern()）
# を実装し、Point Overlap/Value QAの呼び出し・記録はそのまま行うが、
# flagged結果によるretry・早期returnだけを行わないようにする。Fact
# Checker/Ledger Deviation Checker(+Local Rewrite)/Directional Fact
# Precheckのロジック自体はgen.run_one_pattern()から一切変更せずコピーする
# (呼び出す関数・引数・順序は完全に同一)。
#
# 禁止: Production Prompt/code変更、B Family骨格の正式採用、Voice数3以上
# への拡張、Point Overlap/Value QA閾値変更、「品質が良くなるまで」の
# 再生成、Case Story設計、A Family 4層構造の正式化、テーマ自体の変更、
# Git操作(Report内で指示された3ファイルのみを本ファイル完成後に別途
# Bashでcommit)。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
#
# ---- 追記(EDITORIAL-B-FAMILY-VOICES-TRIAL-04、Fableレビューによる修正指示
# 1回目、2026-09-06) ----
# Fableレビュー(run01記事に対して)を踏まえ、Focus Module Block末尾に
# (f)〜(k)の追加指示(Hook・語り口・主語構造・数字数・第三者視点排除・
# 長さ)を追加し、Writer本体をrun02として1回だけ再生成する。Research/
# Verified Fact Ledger/選定した2 Voice/骨格マッピングは変更しない。手で
# 記事を書き換えない。run01の出力(b1b_run01/配下、OUT_DIR直下の
# trial04_summary.json・raw_usage_log_trial04_writer.jsonl・audit/配下)は
# 一切上書きしない。run02の新規出力は全てb1b_run02/配下に閉じ込める
# (Phase A監査ファイル・cost log・summaryも含む)。
from __future__ import annotations

import json
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import requests

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er003_v1_spoken_first_01_r1_generate as sf1r1
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_directional_fact_precheck_08 as dfp
import er010_ledger_local_rewrite_09 as local_rewrite
import er011_point_role_value_planning_01 as point_planning

THEME_ID = "editorial_b_voices_trial_04_assigned_desks"
OUT_DIR = f"er012_output/editorial_b_voices_trial_04"
RESEARCH_DIR = f"{OUT_DIR}/research"
os.makedirs(RESEARCH_DIR, exist_ok=True)

# EDITORIAL-B-FAMILY-VOICES-TRIAL-04での変更点: Trial-03のTOPIC_JAは
# 「個別事例に注目する立場 vs 業界全体のデータに注目する立場」という
# 測定基準比較の枠組みをここで既に指定しており、これがVoice選定・記事の
# 骨格をDiscovery寄り(Evidence/分析軸の比較)に誘導した一因と考えられる
# (ユーザー評価#1)。テーマ(固定席復活)そのものは変更しないが、今回は
# どの2つの立場を対比させるかを先に固定せず、状況を中立的に提示するに
# とどめ、実際にどのstakeholder perspectiveを描くかはResearchと
# Verified Fact Ledgerのcuration(下記)に委ねる。
TOPIC_JA = (
    "2026年9月時点、オフィスの座席運用が変わりつつある。パンデミック下で広がった"
    "フリーアドレス制(ホットデスキング、社員が毎日座席を選ぶ方式)をやめ、社員一人"
    "ひとりに専用の「固定席」を再び割り当てる動きが一部の企業で見られる一方、"
    "デスク共有(ホットデスキング)を維持・拡大する企業も依然として多い。この記事の"
    "中心テーマは、『固定席派 vs フリーアドレス派』のどちらが正しいかを決めることでは"
    "なく、この同じ状況を実際に生きている複数の当事者(例えば、日々オフィスで働く人、"
    "チームや職場の運営に責任を持つ人など)が、それぞれ何を経験し、何を大切にし、"
    "何を心配し、何に責任を持っているのかを、実在する発言・調査・事例に基づいて"
    "具体的に描き、そのうえで、なぜ同じ状況が立場によって違って見えるのかを理解する"
    "ことである。"
)

LABEL = "B1B"
# EDITORIAL-B-FAMILY-VOICES-TRIAL-04: Fableレビューによる修正指示1回目。
# run01(b1b_run01/)は保持したまま、Focus Module修正後の記事をrun02として
# 別ディレクトリへ生成する。
RUN_ID = "run02"
LEVEL_OUT_DIR = f"{OUT_DIR}/{LABEL.lower()}_{RUN_ID}"


# ============================================================
# Research: Perplexity sonar-pro(既存承認済み呼び出しパターンの再実装、
# er011_open112_engagement_reference_cross_topic_ab_trial_11.py参照)
# ============================================================
PERPLEXITY_MODEL = "sonar-pro"


def _perplexity_call(theme_id: str, stage: str, model: str, messages: list[dict],
                      response_format: dict | None = None, timeout: float = 120.0) -> dict:
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
                        "description": "この事実がどの立場を支持するか(例: 経営陣/オフィス回帰派、"
                                       "従業員/柔軟な働き方派、新人教育担当、不動産/職場設計コンサル、"
                                       "フリーアドレス継続派 等)",
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

# EDITORIAL-B-FAMILY-VOICES-TRIAL-04での変更点: Trial-03のFACT_RESEARCH_
# PROMPTは「立場(stance_or_position)」ごとの事実・統計を集めるものだった
# ため、結果的に「集計データ」「adoption率」中心のfactが多く集まり、
# 個々の当事者の生きた経験・発言・心配・責任の記述が薄かった(ユーザー
# 評価#1)。今回はTrial-03のfactをそのまま再利用しつつ、それに不足して
# いた「stakeholder自身の経験・価値観・必要・心配・責任・得失」を明示的に
# 狙って追加Researchする(Stage 1B/2B、ファイル名はstakeholder付き)。
FACT_RESEARCH_PROMPT = """あなたはニュース記事のFact Checker/Researcherです。以下のテーマについて、
2026年9月時点で実在する当事者(具体的な役割・組織・肩書を持つ人、または明確に定義された
属性グループ)が、実際に何を経験し、何を大切にし、何を必要とし、何を心配し、何に責任を
持ち、何を得て何を失うのかが分かる、具体的な事実(発言・インタビュー・体験談・当事者を
対象にした調査結果)を調べてください。**業界全体のadoption率や市場規模のような集計統計
だけのfactは対象外です**(そうしたデータは既に別途収集済みです)。

【テーマ】
オフィスにおける「固定席」の復活: パンデミック下で広がったフリーアドレス制(ホットデスキング、
社員が毎日座席を選ぶ方式)を取りやめ、社員一人ひとりに専用のデスクを再び割り当てる企業が
一部で増えている一方、デスク共有を維持・拡大する企業も多い(英語圏・日本のいずれの事例も
対象)。(assigned desks return / end of hot-desking / hybrid office redesign 2025-2026)

【調査対象として重視してほしい当事者(複数の異なる立場を必ず含めてください。以下に限定
されませんが、できるだけ「実在の個人の発言」「当事者を対象にした調査での生の回答」を
優先してください)】
- 週の大半をオフィスで過ごす社員(固定席に何を感じているか: 集中・所属感・自分の場所と
  しての愛着・毎日の設営の手間 等)
- 出社頻度が低い、または在宅勤務を好む社員(固定席の割り当てに何を感じているか: 自由・
  柔軟性への欲求、使わない席への割り当てをどう思うか、公平感 等)
- チーム・部署のマネージャーや新人教育担当(座席運用が部下やチーム運営にどう影響するか:
  メンタリング・目が届く範囲・チームの一体感への責任)
- オフィス運営・ファシリティ担当者やワークプレイス戦略責任者(自分の職務としての責任:
  スペースコスト・稼働率管理・従業員満足度のバランスをどう取っているか、実名の発言があれば
  優先)
- 不動産・ワークプレイス戦略コンサルタント個人の発言(企業に何を助言しているか、その助言の
  根拠にしている価値観)
- 労働組合・従業員代表・独立研究者による、当事者への影響に関する意見・調査(あれば)

【出力ルール】
- 最低8件、できれば12件以上のfactを、実際に検索で確認できたものだけ出力してください
- 検索で確認できない推測・一般論は書かないでください
- 集計統計・adoption率だけのfact(実名個人の発言や当事者への調査の生の回答を伴わないもの)は
  優先度を下げてください
- 各factについて、number_or_stat、actor_or_organization、stance_or_position、
  interest_or_stake、evidence_strength、counter_or_limitation、time_window、source_name、
  source_url、publication_dateを可能な限り埋めてください。分からない項目はnullにしてください
- interest_or_stakeには、可能な範囲で「経験/価値/必要/心配/責任/得失」のうちどれに該当するか
  分かるように具体的に書いてください
- evidence_strengthは、公式統計/政府発表/企業公式発表/大手メディア報道/業界調査/民間分析/
  意見記事/anecdotalのどれに当たるかを区別してください
- 少なくとも4つの異なるstance_or_position(異なる当事者の種類)のfactを含めてください
  (単一の立場に偏らないでください)
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
    # EDITORIAL-B-FAMILY-VOICES-TRIAL-04: Trial-03のresearch/配下(raw_facts_
    # research.json等)はそのまま再利用する(再取得しない、Trial-03の
    # ファイルは無変更)。ここではTrial-03に不足していたstakeholder視点の
    # factだけを追加Research(Stage 1B/2B)し、stakeholder付きの別ファイル名で
    # research/配下に保存する。
    cl.install(f"{OUT_DIR}/raw_usage_log_trial04_research.jsonl")
    print("[TRIAL-04][Research] Stage 1B: stakeholder視点のfact research"
          "(Perplexity sonar-pro)開始...")
    facts_result = research_facts()
    with open(f"{RESEARCH_DIR}/raw_facts_research_stakeholder.json", "w", encoding="utf-8") as f:
        json.dump(facts_result, f, ensure_ascii=False, indent=2, default=str)
    if facts_result.get("status") != "OK":
        print(f"[TRIAL-04][Research] fact research失敗: {facts_result}")
        return
    print(f"[TRIAL-04][Research] Stage 1B完了。model={facts_result.get('model')} "
          f"response_id={facts_result.get('response_id')}")

    print("[TRIAL-04][Research] Stage 2B: 独立verification(Perplexity sonar-pro)開始...")
    verify_result = verify_facts(facts_result["content"])
    with open(f"{RESEARCH_DIR}/raw_facts_verification_stakeholder.json", "w", encoding="utf-8") as f:
        json.dump(verify_result, f, ensure_ascii=False, indent=2, default=str)
    if verify_result.get("status") != "OK":
        print(f"[TRIAL-04][Research] verification失敗: {verify_result}")
        return
    print(f"[TRIAL-04][Research] Stage 2B完了。model={verify_result.get('model')} "
          f"response_id={verify_result.get('response_id')}")
    print("[TRIAL-04][Research] 完了。raw結果をresearch/配下に保存しました。"
          "次に手作業でPerspective候補整理・Verified Fact Ledgerをcurationしてください。")


# ============================================================
# B Family Common Skeleton(Layer2案)+ Voices Focus Module(Layer3案)
# ANCHOR挿入方式(Trial-05/09/10/11と同じ手法)
# ============================================================
ANCHOR = "【Spoken-first原則(数字の扱い)】"

B_FAMILY_VOICES_FOCUS_MODULE_BLOCK = """【B Family Voices/Perspective Focus Module(今回のTrialで修正する、\
この記事タイプ専用の骨格再定義。EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run02\
(Fableレビューによる修正指示1回目)、Production未採用)】
この記事は、上記で説明されている「Main Story / Point One・Point Two / In One Line」という
一般的な役割定義とは異なる、Voices/Perspective(実在する複数の立場を並立させ、その違いの
奥にあるTensionを発見し、一段深い理解へ着地する)という別の記事タイプです。以下は、上記の
一般的な役割定義を置き換えるのではなく、この記事に限り、それぞれのslotが何を担うかを
より具体的に上書きする指示です。今回の記事では、以下の役割定義を優先してください。

【最も重要な前提: Voiceとは何か】
Voiceとは、データセットでも、トレンドでも、主張(議論の一方の側)でもありません。Voiceとは、
Researchで確認された、実在するstakeholderの視点そのものです。それぞれのVoiceは、その人物・
その立場の人が、実際に何を経験し(experience)、何を大切にし(value)、何を必要とし(need)、
何を心配し(worry about)、何に責任を持ち(are responsible for)、何を得て何を失うのか
(gain or lose)から書いてください。「〜という調査結果がある」「〜というデータが示す」を
主語にした説明ではなく、「その人にとって、これはどういう毎日なのか」を主語にして書いて
ください。Evidence(発言・調査・事例)はVoiceを裏付けるために使うのであって、Evidence自体が
Voiceになってはいけません。数字や調査結果を並べるだけの記述にならないよう、常に「この人は
何を感じているか」に立ち返ってください。

読み手がVoiceのセクションを読んだときに、「この立場なら、たしかにそう感じるだろうな」と
思えることが最も重要なゴールです。反論のための藁人形にしないでください。

【トーン(重要)】
この記事は、業界レポート・コンサルティングメモ・分析的なブリーフィング・リサーチサマリー
のような読み味にしないでください。Light・conversational・human-centeredに、気軽に読める
文章にしてください。専門用語や硬い分析用語(「測定基準」「利害」「対称的」等の学術的な
言葉)を地の文で使うのではなく、日常の言葉でその人の感じ方を描いてください。Evidenceは
必要ですが、記事の主役にはしないでください。

【Main Story slotの役割(この記事ではQuestion/Hookとして書く)】
Main Story(タイトル直下、###見出しの前)は、通常のMain Storyのような出来事の全体像の
説明ではなく、短いQuestion/Hook(導入)として書いてください。ここでは、これから複数の
立場を紹介するテーマ・状況を簡潔に提示するだけにとどめ、どちらの立場が正しいかを示唆
したり、結論を先取りしたりしないでください。目安は100語未満です。

【### 見出し1つ目の役割(1つ目のVoice)】
Verified Fact Ledgerで示された、実在する1つのstakeholder perspectiveを描いてください。
見出しは、その人物・立場が何者であるかが伝わる自然な言葉にしてください("Voice 1"・
"Perspective A"・賛成/反対のような対称的・固定的なラベルは禁止です)。本文では、上記の
「最も重要な前提」に沿って、その立場の人が日々何を経験し、何を大切にし、何を必要とし、
何を心配しているかを、Verified Fact Ledgerにある事実(発言・調査・具体的な体験談)で
裏付けながら描いてください。

【### 見出し2つ目の役割(2つ目のVoice + Tension、新しい見出しを追加しない)】
まず、1つ目のVoiceとは異なる、もう1つの実在するstakeholder perspectiveを、同様にVerified
Fact Ledgerの事実を用いて描いてください。2つのVoiceは、単に異なる数字・異なるデータを
引用しているだけであってはいけません。責任(responsibility)・動機(incentive)・生きられた
経験(lived experience)・制約(constraint)・価値観(value)・優先順位(priority)のうち、
根本的な部分で異なっている必要があります。1つ目のVoiceと同じ対立軸の強さ違いのバリエー
ション(例: 「強く賛成」対「弱く賛成」)にもしないでください。

2つ目のVoiceの本文を書き終えたあとに、この同じ###見出しのセクション内で(新しい見出しを
追加せず、ラベルも付けず、自然な段落として)、続けて以下の役割を持つ内容を書いて
ください(これをこのTrialでは作業名として"Tension"と呼びますが、本文中に"Tension"と
いう語自体を書かないでください):
- 「どちらのデータが正しいか」を決めようとしないでください。そうではなく、なぜ両方の
  Voiceが、それぞれの立場からは合理的に見えるのかを掘り下げてください。具体的には:
  なぜ両方とも理にかなって聞こえるのか / それぞれがどんな前提の違いに立っているのか /
  それぞれが何を優先しているのか / それぞれが(もし何かを測っているとすれば)何を測って
  いるのか / それぞれの責任範囲がどう違うのか、といった問いを言語化してください
- この段落では2つのVoiceそれぞれが使った事実を横断的に参照してもかまいませんが、
  Verified Fact Ledgerに無い新しい因果関係・新しい事実を作り出さないでください
- 単に「両方とも一理ある」とまとめるだけの記述にしないでください

【In One Line見出し以降(Closing)の役割】
通常のIn One Line(現象への一言要約)とは異なり、この記事のClosingは要約であってはいけ
ません。Tensionから導かれる、この問題に対するもう一段深い理解を示してください。「どちらが
正しいか」を決めないでください。この内容もVerified Fact Ledgerが示す複数のVoiceの構造的な
違い(経験・価値観・必要・心配・責任・得失の違い)の範囲内にとどめ、Ledgerにない新しい
因果関係・断定を創作しないでください(Evidence-bounded Interpretation原則を継続して
守ってください)。

【Point Balance原則・言い換え禁止・Point長さ目標(上記既存指示)の扱いについて】
上記の一般的なPoint One/Two役割リスト(切り口・示唆・背景・心理・社会的含意等)は、
この記事では「異なる実在のstakeholder perspectiveを描く」という上記の役割に置き換わり
ます。ただし、「本文の言い換え禁止」「Point同士が同じ役割を担わない」という原則自体は
維持してください(2つのVoiceが同じ利害・立場のバリエーションにならないこと、という
上記の指示と同じ趣旨です)。Point One・Point Twoの長さ目標(30-60語、許容範囲25-70語)
は、Discovery/Why記事向けの目安であり、この記事のVoiceセクションはそれぞれの立場を
十分に描くために、その目安を超えて構いません(Tensionを含む2つ目のVoiceセクションは
さらに長くなることを想定しています)。目安の下限・上限に合わせるための不自然な削除・
水増しはしないでください。長さを揃えるためにVoiceの人間らしい描写を削らないでください。

【Hook・語り口に関する追加指示(EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run02、Fableレビューに
よる修正指示1回目。以下は上記の指示への追加であり、置き換えではありません。前回(run01)
の記事はHookがニュース/分析調で始まり、Evidenceの提示自体が文の主語になっている箇所が
複数あり、Voice Bに第三者の視点が混入していたため、その3点を修正するための指示です)】
Apply the following rules (f)-(k) in addition to everything above.

(f) Open with a small, concrete everyday scene involving a person (arriving at the office,
looking for a seat, unpacking, choosing where to sit today), then pose the question. Do not
open with company trends, dates, or "two directions".

(g) Inside each Voice, the grammatical subject of nearly every sentence must be the person or
people of that Voice (what they do, feel, need, worry about). Never write sentences whose
subject is a survey, report, analysis, study, or figure ("A survey found...", "One report
described...", "The data show..."). Do not use analyst phrasing such as "This suggests
that...", "showed the same pattern", "reported belonging".

(h) Use at most one number per Voice, and fold it into the person's perspective in spoken form
("and they are not alone — most people with a fixed desk say they feel they belong"; "about
four in ten workers in free-address offices find they drift back to the same seat"). Keep
exact figures only where the Verified Fact Ledger requires them; otherwise prefer "most",
"about four in ten" over exact percentages. The Spoken-first原則(数字の扱い)below still
applies in full.

(i) Do not import third-party viewpoints (planners, consultants, management) into a worker's
Voice. If a design idea matters, express it as what this worker wants or notices.

(j) Tone target: light, conversational, human-centered, as if explaining to a friend; short
sentences; no report vocabulary.

(k) Length: aim for roughly 350-420 words in total; achieve this by removing survey-style
sentences, not by cutting the human details. Tension and Closing may stay close to the
previous run's length and content."""


def build_candidate_template() -> str:
    assert ANCHOR in gen.COMMON_BLOCK_TEMPLATE, (
        "アンカー文字列がgen.COMMON_BLOCK_TEMPLATE内に見つかりません。Production側のtemplateが"
        "本Trial設計時から変更されている可能性があるため中断してください(STOP条件)。")
    assert gen.COMMON_BLOCK_TEMPLATE.count(ANCHOR) == 1, (
        "アンカー文字列が複数回出現しています。挿入位置が一意に定まらないため中断してください。")
    return gen.COMMON_BLOCK_TEMPLATE.replace(
        ANCHOR, B_FAMILY_VOICES_FOCUS_MODULE_BLOCK + "\n\n" + ANCHOR, 1)


def build_candidate_prompt(candidate_template: str, master_full_text: str, topic: str,
                            verified_ledger_text: str, instruction: str) -> str:
    common_block = candidate_template.format(
        hanshin_master_full_text=master_full_text, topic=topic,
        verified_ledger_text=verified_ledger_text,
        shared_point_blueprint_block="", evidence_compression_block="")
    return gen.build_prompt(common_block, instruction)


def run_phase_a(audit_dir: str) -> dict:
    # EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run02: 監査ファイルの出力先を
    # 呼び出し元から受け取るように変更(run01のOUT_DIR/audit/配下を上書き
    # しないため、run02からはLEVEL_OUT_DIR/audit/配下を渡す)。
    os.makedirs(audit_dir, exist_ok=True)
    candidate_template = build_candidate_template()
    with open(f"{audit_dir}/phase_a_candidate_template.txt", "w", encoding="utf-8") as f:
        f.write(candidate_template)
    with open(f"{audit_dir}/phase_a_b_family_voices_focus_module_block.txt", "w", encoding="utf-8") as f:
        f.write(B_FAMILY_VOICES_FOCUS_MODULE_BLOCK)

    reconstructed = gen.COMMON_BLOCK_TEMPLATE.replace(
        ANCHOR, B_FAMILY_VOICES_FOCUS_MODULE_BLOCK + "\n\n" + ANCHOR, 1)
    clean_single_insert = (reconstructed == candidate_template)
    result = {"clean_single_insert_confirmed": clean_single_insert,
              "baseline_len": len(gen.COMMON_BLOCK_TEMPLATE), "candidate_len": len(candidate_template)}
    with open(f"{audit_dir}/phase_a_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[TRIAL-04][Phase A] clean_single_insert_confirmed={clean_single_insert}")
    return {"result": result, "phase_a_pass": clean_single_insert, "candidate_template": candidate_template}


# ============================================================
# Writer Trial adapter: gen.run_one_pattern()相当だが、Point Overlap QA /
# Point Value QAをmonitoring専用にする(flaggedでもretry・早期returnしない)。
# それ以外(Point Role Planning / Fact Checker / Ledger Deviation Checker /
# Local Rewrite / Directional Fact Precheck)の呼び出し・引数・順序は
# gen.run_one_pattern()から一切変更せずコピーする。Production変更はゼロ
# (既存ファイルへの書き込みは行わない、既存関数を読み取り専用でimportして
# 呼び出すだけ)。
# ============================================================
def run_voices_pattern(client, theme_id: str, label: str, prompt: str, verified_ledger_text: str,
                        topic: str, out_dir: str, apply_evidence_compression: bool = True,
                        apply_directional_fact_precheck: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    writer_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)

    role_plan_result = point_planning.run_point_role_planning(
        client, topic, verified_ledger_text, model=writer_model, reasoning_effort=gen.REASONING_EFFORT)
    with open(f"{out_dir}/audit/point_role_planning_initial.json", "w", encoding="utf-8") as f:
        json.dump(role_plan_result, f, ensure_ascii=False, indent=2, default=str)
    prompt_with_plan = prompt + "\n" + point_planning.build_role_planning_block(role_plan_result["parsed"])

    gen_result = gen._generate_and_compress_article(
        client, theme_id, label, prompt_with_plan, out_dir, apply_evidence_compression, writer_model)
    if gen_result["status"] != "OK":
        return {"label": label, "status": gen_result["status"], "article_text": None}
    article_text = gen_result["article_text"]
    fact_usage_report = gen_result["fact_usage_report"]
    evidence_compression_applied = gen_result["evidence_compression_applied"]

    # --- Point Overlap QA / Point Value QA: monitoring専用(ユーザー決定#6)。
    # single pass、flaggedでも記事全体retry・Point-only regeneration・早期
    # returnは一切行わない。呼び出す関数自体はgen.run_one_pattern()と同一。
    print(f"[TRIAL-04][{theme_id}] {label}: Point Overlap/Value QA(monitoring専用、single pass)開始...")
    point_qa_result = gen.run_point_overlap_qa_and_regenerate(
        client, article_text, verified_ledger_text, model=writer_model,
        reasoning_effort=gen.REASONING_EFFORT, out_dir=out_dir)
    overlap_report = point_qa_result.get("report") or {}
    lexical_flagged = point_qa_result["status"] == "OK" and any(
        overlap_report.get(key, {}).get("before_overlap", {}).get("flagged")
        for key in ("point_one", "point_two"))

    sections_for_value_qa = gen.split_common_sections_for_point_qa(article_text)
    value_qa_result = None
    value_qa_flagged = False
    if sections_for_value_qa is not None:
        value_qa_result = point_planning.run_point_value_qa(
            client, sections_for_value_qa["full_story"], sections_for_value_qa["point_one_body"],
            sections_for_value_qa["point_two_body"], model=writer_model, reasoning_effort=gen.REASONING_EFFORT)
        with open(f"{out_dir}/audit/point_value_qa_monitoring.json", "w", encoding="utf-8") as f:
            json.dump(value_qa_result, f, ensure_ascii=False, indent=2, default=str)
        value_qa_flagged = value_qa_result["status"] == "NG"

    monitoring_summary = {
        "qa_status": point_qa_result["status"],
        "lexical_flagged": lexical_flagged,
        "value_qa_flagged": value_qa_flagged,
        "note": ("EDITORIAL-B-FAMILY-VOICES-TRIAL-04のユーザー決定によりmonitoring専用。"
                 "flaggedであっても記事全体retry・Point-only regenerationは一切発生させず、"
                 "本文は変更せずそのままFact Checker以降へ進める。"),
        "point_one_vs_point_two": overlap_report.get("point_one_vs_point_two"),
        "point_two_vs_point_one": overlap_report.get("point_two_vs_point_one"),
        "point_one": overlap_report.get("point_one"),
        "point_two": overlap_report.get("point_two"),
        "value_qa_status": value_qa_result["status"] if value_qa_result else None,
        "value_qa_result": value_qa_result,
    }
    with open(f"{out_dir}/point_overlap_value_qa_monitoring.json", "w", encoding="utf-8") as f:
        json.dump(monitoring_summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[TRIAL-04][{theme_id}] {label}: monitoring結果 lexical_flagged={lexical_flagged} "
          f"value_qa_flagged={value_qa_flagged}(gateにはしない、そのまま続行)")

    # --- 以下、gen.run_one_pattern()のFact Checker/Ledger Deviation
    # Checker/Local Rewrite/Directional Fact Precheckロジックを、呼び出す
    # 関数・引数・順序とも一切変更せずそのままコピーする ---
    metrics = gen.compute_metrics(article_text)
    section_wc = sf1r1.section_word_counts(article_text)
    length_report = {
        **section_wc, "total": metrics["word_count"],
        "point_one_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_one"] <= gen.POINT_TARGET_UPPER,
        "point_one_within_tolerance": gen.POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= gen.POINT_TOLERANCE_UPPER,
        "point_two_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_two"] <= gen.POINT_TARGET_UPPER,
        "point_two_within_tolerance": gen.POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= gen.POINT_TOLERANCE_UPPER,
        "total_within_soft_range": gen.TOTAL_SOFT_LOWER <= metrics["word_count"] <= gen.TOTAL_SOFT_UPPER,
    }
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
        json.dump(length_report, f, ensure_ascii=False, indent=2)
    print(f"[TRIAL-04][{theme_id}] {label}: metrics={metrics} sections={section_wc}")

    print(f"[TRIAL-04][{theme_id}] {label}: fact checker呼び出し開始...")
    fc_prompt = r3.build_fact_check_prompt(topic, article_text, [])

    def make_fc_fn():
        return r3.make_fact_checker_fn(
            fc_prompt, model=routing.require_model("WRITER_FACT_CHECK", routing.WRITER_FACT_CHECK_MODEL))

    fc_result, fc_status, fc_attempts, fc_model, fc_response_id, fc_search_usage, fc_sources = \
        r3.run_fact_checker_with_gates(make_fc_fn, sleep_fn=time.sleep)
    verdict = fc_result.get("verdict") if fc_result else None
    print(f"[TRIAL-04][{theme_id}] {label}: fact_check status={fc_status} verdict={verdict}")
    fact_qa_record = {
        "label": label, "final_status": fc_status, "model": fc_model, "response_id": fc_response_id,
        "web_search_call_count": fc_search_usage["web_search_call_count"] if fc_search_usage else None,
        "attempts": len(fc_attempts), "result": fc_result,
    }
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fact_qa_record, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/fact_check_attempts.json", "w", encoding="utf-8") as f:
        json.dump(fc_attempts, f, ensure_ascii=False, indent=2, default=str)

    if verdict == "FAIL":
        print(f"[TRIAL-04][{theme_id}] {label}: fact checkerがFAILと判定しました。自動続行せず"
              f"NG_REVIEW_REQUIREDとして報告します(ledger逸脱チェック以降は実行しません)。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
            "fact_status": fc_status, "fact_verdict": verdict, "fact_check_result": fc_result,
            "fact_usage_report": fact_usage_report,
            "evidence_compression_applied": evidence_compression_applied,
            "point_overlap_value_qa_monitoring": monitoring_summary,
        }

    print(f"[TRIAL-04][{theme_id}] {label}: ledger逸脱チェック開始(Hook-aware)...")
    ledger_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
    print(f"[TRIAL-04][{theme_id}] {label}: deviation overall_status="
          f"{deviation_result['parsed']['overall_status']} deviations={len(deviation_result['parsed']['deviations'])}")

    local_rewrite_results = []
    local_rewrite_cycles = []
    cycle = 0
    previously_seen_claims = set()

    def _run_check_window(window_text: str) -> dict:
        r = vfl01.run_deviation_check(client, verified_ledger_text, window_text,
                                       model=ledger_model, hook_aware=True)
        return r["parsed"]

    major_items = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]

    while major_items and cycle < local_rewrite.MAX_REWRITE_CYCLES:
        cycle += 1
        newly_discovered_claims = [d["claim_in_article"] for d in major_items
                                    if d["claim_in_article"] not in previously_seen_claims]
        print(f"[TRIAL-04][{theme_id}] {label}: Local Rewrite cycle {cycle}/"
              f"{local_rewrite.MAX_REWRITE_CYCLES} - Ledger MAJOR {len(major_items)}件を検出"
              f"({len(newly_discovered_claims)}件は新規)。局所Rewrite開始...")

        cycle_results = []
        sentences = local_rewrite.split_sentences(article_text)
        for idx, deviation in enumerate(major_items, start=1):
            target, location_method = local_rewrite.locate_target_sentence(
                deviation["claim_in_article"], article_text)
            if target is None:
                cycle_results.append({
                    "cycle": cycle, "item_idx": idx, "original_ng_sentence": deviation["claim_in_article"],
                    "issue": deviation["issue"], "explanation": deviation["explanation"],
                    "attempts": [], "final_text": None, "resolved": False,
                    "human_review_required": True, "location_method": "not_found",
                })
                continue
            try:
                sidx = sentences.index(target)
            except ValueError:
                sidx = -1
            before_ctx = sentences[sidx - 1] if 0 <= sidx - 1 else ""
            after_ctx = sentences[sidx + 1] if 0 <= sidx and sidx + 1 < len(sentences) else ""
            point_context = local_rewrite.extract_point_context(article_text, target)
            point_context_found = point_context is not None
            if point_context is None:
                point_context = f"{before_ctx} {target} {after_ctx}".strip()
            r = local_rewrite.rewrite_ng_item(client, ledger_model, gen.REASONING_EFFORT,
                                               verified_ledger_text, point_context, target,
                                               deviation, before_ctx, after_ctx, _run_check_window)
            r["cycle"] = cycle
            r["item_idx"] = idx
            r["location_method"] = location_method
            r["point_context_found"] = point_context_found
            r["point_context"] = point_context
            cycle_results.append(r)
            print(f"[TRIAL-04][{theme_id}] {label}: cycle {cycle} NG item {idx}: resolved={r['resolved']} "
                  f"human_review={r['human_review_required']} attempts={len(r['attempts'])}")

        article_text = local_rewrite.apply_rewrites(article_text, cycle_results)
        article_text = gen.normalize_article_formatting(article_text)
        with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(article_text)

        metrics = gen.compute_metrics(article_text)
        section_wc = sf1r1.section_word_counts(article_text)
        length_report = {
            **section_wc, "total": metrics["word_count"],
            "point_one_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_one"] <= gen.POINT_TARGET_UPPER,
            "point_one_within_tolerance": gen.POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= gen.POINT_TOLERANCE_UPPER,
            "point_two_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_two"] <= gen.POINT_TARGET_UPPER,
            "point_two_within_tolerance": gen.POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= gen.POINT_TOLERANCE_UPPER,
            "total_within_soft_range": gen.TOTAL_SOFT_LOWER <= metrics["word_count"] <= gen.TOTAL_SOFT_UPPER,
        }
        with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
            json.dump(length_report, f, ensure_ascii=False, indent=2)

        print(f"[TRIAL-04][{theme_id}] {label}: cycle {cycle} Local Rewrite後、Ledger全体を再判定...")
        deviation_result = vfl01.run_deviation_check(
            client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
        recheck_major = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
        print(f"[TRIAL-04][{theme_id}] {label}: cycle {cycle} 再判定 overall_status="
              f"{deviation_result['parsed']['overall_status']} MAJOR={len(recheck_major)}件")

        previously_seen_claims |= {d["claim_in_article"] for d in major_items}
        local_rewrite_results.extend(cycle_results)
        local_rewrite_cycles.append({
            "cycle": cycle, "targeted_major_count": len(major_items),
            "newly_discovered_claims": newly_discovered_claims, "results": cycle_results,
            "full_recheck_overall_status": deviation_result["parsed"]["overall_status"],
            "full_recheck_major_count": len(recheck_major),
            "full_recheck_remaining_major_claims": [d["claim_in_article"] for d in recheck_major],
        })
        major_items = recheck_major

    cycle_exhausted = bool(major_items) and cycle >= local_rewrite.MAX_REWRITE_CYCLES
    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/deviation_full_record.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in deviation_result.items() if k != "parsed"}, f, ensure_ascii=False,
                   indent=2, default=str)
    with open(f"{out_dir}/audit/local_rewrite_results.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_results, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/audit/local_rewrite_cycles.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_cycles, f, ensure_ascii=False, indent=2, default=str)

    remaining_major = major_items
    any_human_review = any(r.get("human_review_required") for r in local_rewrite_results)
    if remaining_major or any_human_review:
        print(f"[TRIAL-04][{theme_id}] {label}: Local Rewrite cycleを尽くしてもLedger MAJORが残存、"
              f"またはhuman_review_requiredな項目があります。NG_REVIEW_REQUIREDとして報告します。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": gen.compute_metrics(article_text),
            "fact_status": fc_status, "fact_verdict": verdict,
            "ledger_status": deviation_result["parsed"]["overall_status"],
            "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
            "local_rewrite_results": local_rewrite_results, "local_rewrite_cycles": local_rewrite_cycles,
            "local_rewrite_cycle_exhausted": cycle_exhausted,
            "fact_usage_report": fact_usage_report,
            "evidence_compression_applied": evidence_compression_applied,
            "point_overlap_value_qa_monitoring": monitoring_summary,
        }

    directional_precheck_status = None
    if apply_directional_fact_precheck:
        print(f"[TRIAL-04][{theme_id}] {label}: 比較方向Fact事前チェック開始...")
        vfl_path = f"{os.path.dirname(out_dir)}/research/stage_b3_vfl.json"
        directional_result = dfp.audit_article_directional_facts(
            article_text, verified_ledger_text, vfl_path=vfl_path)
        directional_precheck_status = directional_result["overall_status"]
        with open(f"{out_dir}/audit/directional_fact_precheck.json", "w", encoding="utf-8") as f:
            json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[TRIAL-04][{theme_id}] {label}: 比較方向Fact事前チェック完了。"
              f"overall_status={directional_precheck_status}")

    return {
        "label": label, "status": "OK", "article_text": article_text,
        "metrics": metrics, "section_word_counts": section_wc, "length_report": length_report,
        "fact_status": fc_status, "fact_verdict": verdict,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "local_rewrite_results": local_rewrite_results, "local_rewrite_cycles": local_rewrite_cycles,
        "local_rewrite_cycle_exhausted": cycle_exhausted,
        "fact_usage_report": fact_usage_report,
        "evidence_compression_applied": evidence_compression_applied,
        "point_overlap_value_qa_monitoring": monitoring_summary,
        "directional_fact_precheck_status": directional_precheck_status,
    }


def run_writer_stage() -> dict:
    ledger_path = f"{RESEARCH_DIR}/verified_fact_ledger.txt"
    if not os.path.exists(ledger_path):
        raise SystemExit(f"Curated ledger not found at {ledger_path}. Run research stage and curate first.")
    with open(ledger_path, encoding="utf-8") as f:
        verified_ledger_text = f.read()

    # EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run02: Phase A監査ファイルは
    # LEVEL_OUT_DIR(b1b_run02/)配下へ出力し、run01のOUT_DIR/audit/配下を
    # 上書きしない。
    phase_a = run_phase_a(f"{LEVEL_OUT_DIR}/audit")
    if not phase_a["phase_a_pass"]:
        print("[TRIAL-04] Phase Aで意図しない差分を検出したため、Writerへ進まずSTOPします。")
        return {"phase_a": phase_a, "phase_b": None, "status": "STOP_PHASE_A_UNEXPECTED_DIFF"}

    client = vfl01.get_client()
    # run02のcost logはrun01のraw_usage_log_trial04_writer.jsonl(既存tracked
    # ファイル)へ追記して混在させないよう、b1b_run02/配下の別ファイルへ出力する。
    cl.install(f"{LEVEL_OUT_DIR}/raw_usage_log_trial04_writer_run02.jsonl")
    master_full_text = ab01.load_master_full_text()

    candidate_prompt = build_candidate_prompt(
        phase_a["candidate_template"], master_full_text, TOPIC_JA, verified_ledger_text,
        gen.B1_B_DIRECT_INSTRUCTION)

    print(f"[TRIAL-04] Writer呼び出し開始(run_voices_pattern、adapter経由)...")
    t0 = time.time()
    with cl.logging_context(THEME_ID, "writer_b1b_run02"):
        result = run_voices_pattern(
            client, THEME_ID, LABEL, candidate_prompt, verified_ledger_text, TOPIC_JA, LEVEL_OUT_DIR)
    elapsed = time.time() - t0
    result["elapsed_seconds"] = round(elapsed, 1)

    with open(f"{LEVEL_OUT_DIR}/audit/candidate_prompt_used.txt", "w", encoding="utf-8") as f:
        f.write(candidate_prompt)

    # run01のOUT_DIR/trial04_summary.json(既存tracked)を上書きしないよう、
    # run02専用のsummaryファイル名をLEVEL_OUT_DIR配下に出力する。
    with open(f"{LEVEL_OUT_DIR}/trial04_summary_run02.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in result.items() if k != "article_text"}, f, ensure_ascii=False,
                   indent=2, default=str)

    print(f"[TRIAL-04] 完了。status={result.get('status')} fact_verdict={result.get('fact_verdict')} "
          f"ledger_status={result.get('ledger_status')} elapsed={result['elapsed_seconds']}s")
    return {"phase_a": phase_a, "phase_b": result, "status": "DONE"}


def main() -> None:
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage == "research":
        run_research_stage()
    elif stage == "write":
        run_writer_stage()
    else:
        run_research_stage()
        run_writer_stage()


if __name__ == "__main__":
    main()
