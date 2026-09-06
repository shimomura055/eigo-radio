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
#
# ---- 追記(EDITORIAL-B-FAMILY-VOICES-TRIAL-04、Fableレビューによる差し戻し
# 2回目=往復2回目、run03、2026-09-06) ----
# run02に対するユーザー評価(6点の改善指示、docs/pm/ACTIVE_TASK.md参照)を
# 踏まえ、Focus Module Blockを全面的に書き直す(既存(a)〜(k)を整理・統合)。
# 最大の変更は、内部構造としてHook→Voice A→Voice B→Tension→Closingの5区切り
# を明示的に持たせること。既存A Familyパーサ(er002_ja_free_markdown_
# restore_r2.validate_point_structure等)は「###見出しがちょうど2つ」だけを
# hard gateとして検査しており、##(レベル2)見出しの数・文言は一切検査しない
# ことをProduction側コードの読み取り調査で確認した(git blame的な調査、
# Production側は無変更)。そのため、Voice A・Voice Bの2つだけを###(レベル3)
# 見出しにし、Hook・Tension・Closingの3つは##(レベル2)見出しにすることで、
# 既存のWriter構造ゲート(validate_point_structure、h3_count==2)を一切変更
# せずに5区切りを実現できると判断した。ただし、Production側の以下2つの
# 補助パーサはこの5見出し構造を正しく解釈できない(##見出しの扱いが限定的、
# または「## In one line」という特定文言しか終端として認識しない):
#   - er003_v1_spoken_first_01_r1.section_word_counts(語数の内訳集計)
#   - er003_v1_n3_01_articles_generate.split_common_sections_for_point_qa
#     (Point Overlap/Value QAの入力抽出)
# これらのProduction関数自体は変更せず(呼び出しても壊れず、単に不正確な
# 結果を返すだけ)、本ファイル内にTrial専用のsplit_five_voice_sections()を
# 新設し、run03の語数内訳・Point Overlap/Value QA monitoringはこの専用
# parserの出力を使って計算する(「個別に呼ぶ」というACTIVE_TASK指示に対応)。
# Fact Checker/Ledger Deviation Checker/Local Rewrite/Directional Fact
# Precheckはいずれも見出し構造に依存しない(生テキストを扱う)ことを個別に
# 確認済みのため、run_voices_pattern()の該当ロジックをそのままコピーした
# run_voices_pattern_run03()で無変更のまま呼び出す。run01/run02の出力
# (b1b_run01/・b1b_run02/配下、OUT_DIR直下のtracked済みファイル)は一切
# 上書きしない。run03の新規出力は全てb1b_run03/配下に閉じ込める。
#
# ---- 追記(EDITORIAL-B-FAMILY-VOICES-TRIAL-04、Fableレビューによる差し戻し
# 3回目=往復3回目(最終)、run04、2026-09-06) ----
# run03に対するFableレビューで、5区切り構造・見出し・Voice Bの方向性・
# Tension/Closingの狙いは達成と評価された一方、run02からの後退として次の
# 2点が指摘された: (1) Hook後半が企業名(Amazon)・統計・パーセント
# (「83%から55%」等)を含むトレンド要約に戻ってしまった。(2) Voice Aの
# 第2段落が調査数値(87%/74%・80%/67%・37%等)の連続になり、"reported"
# "showed the same pattern"といった分析調の文になった。これはrun02で
# 守られていた「Voiceごとに数字は最大1つ・話し言葉で・人を主語に」という
# 制約が、run03でのFocus Module全面書き直し時に明文化から抜け落ちたことが
# 原因と判断した。そのため、Research/Verified Fact Ledger/選定した2 Voice/
# 5区切り骨格(Hook→Voice A→Voice B→Tension→Closing、###見出し2つ+##見出し
# 3つ)はrun03のまま一切変更せず、Focus Module Block内に「Hookは数字・企業名
# なしの情景+問いのみ」「Voiceごとに数字は最大1つ・人を主語にした話し言葉」
# という制約を明示的に追加/復元する。run01〜run03の出力(b1b_run01/・
# b1b_run02/・b1b_run03/配下、OUT_DIR直下のtracked済みファイル)は一切
# 上書きしない。run04の新規出力は全てb1b_run04/配下に閉じ込める。Writer
# adapter(run_voices_pattern_run03、5区切りparser split_five_voice_
# sections()含む)は無変更のまま関数名も含めてそのまま再利用する(呼び出す
# 関数・引数・順序は完全に同一、テーマ・Research・Voice選定も無変更)。
# Evidence Compression Editorが適用前(Writer生の出力)を保存する
# audit/pre_editor_article.md は、gen._generate_and_compress_article()に
# 既存で組み込まれている機能であり、本ファイル側の追加実装は不要と確認した
# (run03のaudit/pre_editor_article.mdを実査し、"showed the same pattern"
# 等の分析調表現がEditor由来かWriter由来かを事後diffで確認済み、詳細は
# Report参照)。
from __future__ import annotations

import json
import os
import re
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
import er008_point_overlap_qa_18 as overlap_qa
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
# EDITORIAL-B-FAMILY-VOICES-TRIAL-04: Fableレビューによる差し戻し2回目。
# run01(b1b_run01/)・run02(b1b_run02/)は保持したまま、Focus Module
# 全面改訂後(5区切り構造)の記事をrun03として別ディレクトリへ生成した。
# EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run04(往復3回目・最終): 5区切り骨格・
# adapterはrun03のまま、Focus Module Blockの制約だけを強化した記事を
# run04として別ディレクトリへ生成する。
RUN_ID = "run04"
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

B_FAMILY_VOICES_FOCUS_MODULE_BLOCK = """【B Family Voices/Perspective Focus Module(EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run04、\
Fableレビューによる差し戻し3回目=往復3回目(最終)への対応、2026-09-06。Production未採用。\
この記事タイプ専用の骨格再定義)】
この記事は、上記で説明されている「Main Story / Point One・Point Two / In One Line」という
一般的な役割定義とは異なる、Voices/Perspective(実在する複数の立場を並立させ、その違いの
奥にあるTensionを発見し、一段深い理解へ着地する)という別の記事タイプです。以下は、上記の
一般的な役割定義・見出し構成を置き換えるのではなく、この記事に限り、それぞれのslotが何を
担い、どのMarkdown見出しで書くかを、より具体的に上書きする指示です。今回の記事では、以下の
役割定義・出力形式を最優先で守ってください。

【最重要・この記事だけの出力形式(5区切り構造)】
上記「記事構成」節にある「Markdownの###見出しをちょうど2つ置く」という指示は、この記事
では次のように解釈してください: ###(レベル3見出し)は必ずちょうど2つだけ使い、それぞれ
1つ目のVoice・2つ目のVoiceの見出しとしてのみ使ってください。それに加えて、##(レベル2
見出し)を3つ使い、Hook・Tension・Closingの見出しとしてください。「Main Storyには見出しを
付けない」「## In one lineという見出し文言を使う」という上記の一般的な指示は、この記事に
限り、以下に置き換わります。記事全体は、必ず次の5つのMarkdown区切りを、この順序で持って
ください(見出し文言は下の例を基本としつつ、内容に応じて自然に言い換えてかまいませんが、
2つ目・3つ目の見出しには、「ここから別のVoiceが始まる」と聞き手に伝わる表現("One Voice:"
"Another Voice:"のような形)を必ず含めてください。"Voice A"/"Voice B"/"Perspective A"の
ような固定ラベル・番号ラベル、賛成/反対のような対称的なラベルは禁止です):

# [Title]

## The Question
[Hookの本文]

### One Voice: [その人物・立場が何者かが伝わる短いフレーズ]
[1つ目のVoiceの本文]

### Another Voice: [その人物・立場が何者かが伝わる短いフレーズ]
[2つ目のVoiceの本文]

## [Tensionの見出し。例: "Why They See It Differently"]
[Tensionの本文]

## [Closingの見出し。例: "What This Tells Us"]
[Closingの本文]

Tensionは、2つ目のVoiceの本文の続きの段落ではなく、独立した見出しを持つ独立したセクション
として書いてください(前回runでは、Tensionが2つ目のVoiceの後半へ溶け込んでしまい、区切りが
不明瞭でした)。

【最も重要な前提: Voiceとは何か】
Voiceとは、データセットでも、トレンドでも、主張(議論の一方の側)でもありません。Voiceとは、
Researchで確認された、実在するstakeholderの視点そのものです。それぞれのVoiceは、その人物・
その立場の人が、実際に何を経験し(experience)、何を大切にし(value)、何を必要とし(need)、
何を心配し(worry about)、何に責任を持ち(are responsible for)、何を得て何を失うのか
(gain or lose)から書いてください。Evidence(発言・調査・事例)はVoiceを裏付けるために
使うのであって、Evidence自体がVoiceになってはいけません。

【Voiceの書き始め方(重要、run02からの追加指示)】
run02のVoiceは、「For an employee who spends most of the week in the office, a desk can
feel like a small home base.」「For another employee, a desk is a choice, not a home
base.」のように、その人物のことを外側から要約・紹介する文で始まっていました。これは
Voiceを「説明されている対象」にしてしまい、当事者の視点そのものとして立ち上がることを
妨げます。Voiceの本文は、"For [a/an] worker who..."のような紹介・要約文で始めない・
多用しないでください。代わりに、Verified Fact Ledgerが示す具体的な状況(その人が実際に
毎日していること・直面していること・使っているもの、目にする光景)から書き始め、そこから
その人の感覚・必要性が自然に浮かび上がるようにしてください。目標は、読み手が「この立場
なら、たしかにそう感じるだろうな」と、外から説明されるのではなく内側から実感できること
です。反論のための藁人形にしないでください。

【Evidenceは脇役であること(重要、run02からの追加指示)】
run02のVoice A第2〜3段落では、"three part-time workers"、"a survey"、"another survey"、
"37%"のように、調査・出典・人数への言及が連続し、記事が再び調査報告のような読み味に
戻りかけました。Factを減らすこと自体が目的ではありませんが、1つのVoiceの中で、
Evidenceの紹介そのものが主役になる文を連続させないでください。その人の経験・価値観・
必要性の描写を主体にし、Evidenceはその描写を裏から支えるためだけに、さりげなく織り
込んでください。文の主語が調査・報告・データ("A survey found...", "One report
described...", "The data show...")になる文、"This suggests that..."のような分析者の
言い回しは書かないでください。

【トーン(重要)】
この記事は、業界レポート・コンサルティングメモ・分析的なブリーフィング・リサーチサマリー
のような読み味にしないでください。Light・conversational・human-centeredに、友人に説明
するような、気軽に読める文章にしてください。専門用語や硬い分析用語を地の文で使うのでは
なく、日常の言葉でその人の感じ方を描いてください。

【Hookの役割と書き方(重要、run02からの追加指示)】
Hook("## The Question")は、これから複数の立場を紹介するテーマ・状況を簡潔に提示する
導入です。どちらの立場が正しいかを示唆したり、結論を先取りしたりしないでください。目安は
100語未満です。run02のHook("Picture an employee arriving at the office...")は、
"Picture..."という呼びかけ型の書き出しであり、既に禁止されている"Imagine..."と同じ
カテゴリの定型表現でした。読み手へ呼びかけたり、命令形・二人称で想像を促したりする表現
("Imagine...", "Picture...", "Think about...", "Consider...", "Now look at..."等)で
始めないでください。代わりに、具体的な情景そのものから、三人称で書き始めてください。
小さく具体的な日常の一場面(誰かがオフィスに来て、席を探す、どこに座るか選ぶ、荷物を
置く、といった動作)を描写し、そこから今回の問いへつなげてください(次の例のような書き方
が考えられますが、この文言自体をコピーせず、この記事のFactに合わせて新しく書いてください:
"Monday morning. One employee walks straight to the same desk they used last week.
Another checks the room and chooses a quiet seat near the window.")。

【Hookに数字・企業名・トレンド要約を入れないこと(重要、run04からの追加指示)】
run03のHookは、情景描写と問いは達成できていましたが、後半で「By September 2026, office
seating is moving in both directions. Amazon returned its Seattle-area and Arlington
headquarters to assigned desks... Across companies, assigned seating fell from 83% to 55%
by 2024.」のように、企業名(固有名詞)・統計・パーセントを含む業界動向の要約へ戻って
しまいました。これはrun01で既に禁止していた「トレンド要約」への逆戻りです。Hookは、情景の
描写と、そこから生まれる問いだけで構成してください。企業名・統計・パーセント・「moving in
both directions」のような業界全体の動向要約をHookに書かないでください。背景となる事実が
どうしても必要な場合でも1文以内にとどめ、数字を使わずに書いてください(例:「一部の会社は
席を決め直し、別の会社は自由席を続けている」程度の、数字を含まない一般的な書き方に
とどめる)。Hookの目安は100語未満のままです。

【Voice内の数字は最大1つ、必ずその人の実感に折り込むこと(重要、run04からの追加指示)】
run03の1つ目のVoiceの第2段落は、「Workers with assigned desks reported a stronger sense of
belonging in a study of more than 16,000 office workers: 87%, compared with 74%...」の
ように、1つの段落に複数の数字(87%/74%・80%/67%・約6割・37%)が連続し、"reported"
"showed the same pattern"のような分析調の文になりました。これはrun02で守られていた
「Voiceごとに数字は最大1つ」というルールが、run03のFocus Module全面書き直し時に明文から
落ちたことが原因です。以下のルールを、この記事全体を通して両方のVoiceに適用してください:
- 1つのVoiceのセクション全体を通して、具体的な数字(パーセント・人数・比率等)は最大1つ
  だけにしてください。複数の数字を並べたり比較したりしないでください。
- その数字は、必ずその人/その立場の人々の実感・経験に折り込み、話し言葉で書いてください。
  例えば、「and they are not alone — most people with a fixed desk say they feel they
  belong」「about four in ten find they drift back to the same seat」のように、人を主語に
  した自然な文にしてください(この文言自体をコピーせず、この記事のFactに合わせて新しく
  書いてください)。
- 「a study of more than 16,000」「reported」「showed the same pattern」「compared with」
  のような、調査・比較を報告する文構造は使わないでください。
- 2つ目のVoiceについても同じルールを適用してください。「In one 2025 street interview with
  50 Japanese office workers, four in five supported...」のような調査主語文・複数比率の
  提示ではなく、1つの数字だけを、その人たちの感じ方として話し言葉で書いてください。

【2つ目のVoiceの見出しの役割(2つ目のVoice)】
1つ目のVoiceとは異なる、もう1つの実在するstakeholder perspectiveを、同様にVerified
Fact Ledgerの事実を用いて描いてください。2つのVoiceは、単に異なる数字・異なるデータを
引用しているだけであってはいけません。責任(responsibility)・動機(incentive)・生きられた
経験(lived experience)・制約(constraint)・価値観(value)・優先順位(priority)のうち、
根本的な部分で異なっている必要があります。

【Voice内に第三者の視点・解決策を混ぜないこと(重要、run02からの追加指示)】
run02では、"A team zone, or a seat reserved when needed, may offer an anchor..."のように、
その当事者自身ではない第三者(設計者・コンサルタント・経営側)の解決策・提案が、Voiceの
中に紛れ込みました。各Voiceのセクションでは、その当事者がどう感じ、何を必要としているかを
描き切ってください。解決策・妥協案・提案は、この記事では基本的に書かないでください
(Solution articleではありません)。第三者(planners/consultants/management)の視点を
Voiceへ持ち込まないでください。デザイン上のアイデアが重要な場合は、それをこの当事者自身が
望んでいること・気づいていることとして表現してください。

【Tensionの役割("## Why They See It Differently"相当)】
「どちらのデータが正しいか」を決めようとしないでください。そうではなく、なぜ両方の
Voiceが、それぞれの立場からは合理的に見えるのかを掘り下げてください。具体的には: なぜ
両方とも理にかなって聞こえるのか / それぞれがどんな前提の違いに立っているのか / それぞれ
が何を優先しているのか / それぞれが(もし何かを測っているとすれば)何を測っているのか /
それぞれの責任範囲がどう違うのか、といった問いを言語化してください。この段落では2つの
Voiceそれぞれが使った事実を横断的に参照してもかまいませんが、Verified Fact Ledgerに無い
新しい因果関係・新しい事実を作り出さないでください。単に「両方とも一理ある」とまとめる
だけの記述にしないでください。解決策の提案はここでも基本的に行わないでください。

【Closingの役割("## What This Tells Us"相当)】
これは要約でも、In One Lineの言い換えでもありません。2つのVoiceを両方見たことによって、
この問題そのものの見え方が、Hook(冒頭の問い)の時点からどう変わったかを書いてください。
「どちらが正しいか」を決めず、「この2つのVoiceを知る前と後で、この問題をどう考えるべきか
がどう変わるか」という一段深い理解へ着地してください。内容はVerified Fact Ledgerが示す
複数のVoiceの構造的な違い(経験・価値観・必要・心配・責任・得失の違い)の範囲内にとどめ、
Ledgerにない新しい因果関係・断定を創作しないでください(Evidence-bounded Interpretation
原則を継続して守ってください)。

【Point Balance原則・言い換え禁止・Point長さ目標(上記既存指示)の扱いについて】
上記の一般的なPoint One/Two役割リスト(切り口・示唆・背景・心理・社会的含意等)は、
この記事では「異なる実在のstakeholder perspectiveを描く」という上記の役割に置き換わり
ます。ただし、「本文の言い換え禁止」「Point同士が同じ役割を担わない」という原則自体は
維持してください。Point One・Point Twoの長さ目標(30-60語、許容範囲25-70語)は、
Discovery/Why記事向けの目安でありこの記事には適用しません。

【記事全体の長さについて(この記事専用、hard/soft gateなし)】
記事全体の総語数は、350〜420語程度を観察用の目安としてよいですが、hard capでもsoft gate
でもありません(run04での変更点: Hook・1つ目のVoiceの数値を1つに絞ることで自然に350語
以上に収まると見込んでいますが、これも観察用の目安であり、長さを目安に合わせるための
不自然な削除・水増しはせず、Voiceの人間らしい描写を削らないでください)。

【禁止事項まとめ(この記事全体を通して)】
- Reference Example由来の定型的な呼びかけ表現("Imagine...", "Picture...", "Think
  about...", "Consider..."等)をコピー・準用すること
- "Voice A"/"Voice B"/"Perspective A"のような固定ラベル・番号ラベル
- 文の主語がEvidence(survey/report/data/study)になる文
- Voiceのセクションへ第三者(設計者・コンサルタント・経営側)の視点を持ち込むこと
- Voiceのセクション内で解決策・妥協案を提案すること
- Hookに企業名・統計・パーセント・「moving in both directions」のような業界動向の
  トレンド要約を入れること(run04からの追加)
- 1つのVoiceのセクション内で具体的な数字を2つ以上使うこと、または「a study of...」
  「reported」「showed the same pattern」「compared with」のような調査・比較を
  報告する文構造を使うこと(run04からの追加)"""


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
# EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run03専用: 5区切り構造(Hook/Voice A/
# Voice B/Tension/Closing)のTrial-only parser。Production側のsplit_common_
# sections_for_point_qa()は「###見出しがちょうど2つ」であることを検出できる
# ため実際には呼び出せてしまうが、point_two_bodyの終端を「## In one line」
# という特定文言でしか検出できず、run03の"## Why They See It Differently"
# "## What This Tells Us"は終端として認識されない(Voice B本文にTension・
# Closingまで混入してしまう)。そのため、5見出し全てを見出し出現順にそのまま
# 抽出する専用parserをここに実装する(Production側のファイルは一切変更
# しない、読み取り専用importのまま)。
# ============================================================
_HEADING_RE = re.compile(r"^(#{2,3})[ \t]+(.+?)\s*$", re.MULTILINE)


def split_five_voice_sections(article_text: str) -> dict | None:
    """run03の5区切り構造を見出し出現順(Hook/Voice A/Voice B/Tension/
    Closing)に抽出する。ちょうど5つの##または###見出しがTitleの後に
    連続して登場することを前提とする。想定外の構造(見出し数が5でない等)
    の場合はNoneを返す(呼び出し側はmonitoring不能として記録する)。"""
    title_match = re.match(r"^#[ \t]+.+?\s*\n", article_text)
    if not title_match:
        return None
    body = article_text[title_match.end():]
    matches = list(_HEADING_RE.finditer(body))
    if len(matches) != 5:
        return None
    labels = ["hook", "voice_a", "voice_b", "tension", "closing"]
    result = {}
    for i, label in enumerate(labels):
        heading_text = matches[i].group(2).strip()
        heading_level = len(matches[i].group(1))
        content_start = matches[i].end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        result[f"{label}_heading"] = heading_text
        result[f"{label}_heading_level"] = heading_level
        result[f"{label}_body"] = body[content_start:content_end].strip()
    preamble = body[:matches[0].start()].strip()
    result["unexpected_preamble_before_first_heading"] = preamble
    return result


def run_five_section_point_qa_monitoring(client, sections: dict, writer_model: str, out_dir: str) -> dict:
    """run03専用のPoint Overlap/Value QA monitoring。ACTIVE_TASK指示
    「Voice A/Bをpoint_one/point_two相当として個別に呼ぶ」に対応し、
    gen.run_point_overlap_qa_and_regenerate()を経由せず、その内部で使われて
    いるer008_point_overlap_qa_18.flag_possible_paraphrase()と
    er011_point_role_value_planning_01.run_point_value_qa()を、
    split_five_voice_sections()で抽出したHook/Voice A/Voice Bへ直接個別に
    呼び出す(Production側の2関数自体は無変更)。既存policy通りmonitoring
    専用(flaggedでもretry・早期returnしない、本文も変更しない)。"""
    hook = sections["hook_body"]
    voice_a = sections["voice_a_body"]
    voice_b = sections["voice_b_body"]

    voice_a_vs_hook = overlap_qa.flag_possible_paraphrase(voice_a, hook)
    voice_b_vs_hook = overlap_qa.flag_possible_paraphrase(voice_b, hook)
    voice_a_vs_voice_b = overlap_qa.flag_possible_paraphrase(voice_a, voice_b)
    voice_b_vs_voice_a = overlap_qa.flag_possible_paraphrase(voice_b, voice_a)
    lexical_flagged = any(r["flagged"] for r in
                           (voice_a_vs_hook, voice_b_vs_hook, voice_a_vs_voice_b, voice_b_vs_voice_a))

    value_qa_result = point_planning.run_point_value_qa(
        client, hook, voice_a, voice_b, model=writer_model, reasoning_effort=gen.REASONING_EFFORT)
    value_qa_flagged = value_qa_result["status"] == "NG"

    monitoring_summary = {
        "qa_status": "OK",
        "lexical_flagged": lexical_flagged,
        "value_qa_flagged": value_qa_flagged,
        "note": ("EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run03のユーザー決定によりmonitoring専用。"
                 "flaggedであっても記事全体retry・Point-only regenerationは一切発生させず、"
                 "本文は変更せずそのままFact Checker以降へ進める。gen.run_point_overlap_qa_and_"
                 "regenerate()ではなく、5区切り構造専用のsplit_five_voice_sections()で抽出した"
                 "Voice A/Voice Bを、同じProduction primitive関数(overlap_qa.flag_possible_"
                 "paraphrase / point_planning.run_point_value_qa)へ個別に渡している。"),
        "voice_a_vs_hook": voice_a_vs_hook,
        "voice_b_vs_hook": voice_b_vs_hook,
        "voice_a_vs_voice_b": voice_a_vs_voice_b,
        "voice_b_vs_voice_a": voice_b_vs_voice_a,
        "value_qa_status": value_qa_result["status"],
        "value_qa_result": value_qa_result,
    }
    with open(f"{out_dir}/point_overlap_value_qa_monitoring.json", "w", encoding="utf-8") as f:
        json.dump(monitoring_summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[TRIAL-04][run03] Point Overlap/Value QA monitoring(5区切り専用) "
          f"lexical_flagged={lexical_flagged} value_qa_flagged={value_qa_flagged}(gateにはしない)")
    return monitoring_summary


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


# ============================================================
# EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run03専用Writer Trial adapter。
# 上のrun_voices_pattern()と、Fact Checker/Ledger Deviation Checker/Local
# Rewrite/Directional Fact Precheckの呼び出し・引数・順序は完全に同一
# (一切変更せずコピー)。差分は以下2点のみ:
#   (1) Point Overlap/Value QA monitoring: gen.run_point_overlap_qa_and_
#       regenerate()/gen.split_common_sections_for_point_qa()の代わりに、
#       5区切り構造専用のsplit_five_voice_sections()+
#       run_five_section_point_qa_monitoring()を使う(理由は上記コメント
#       参照: Production側の終端検出が「## In one line」という特定文言に
#       固定されており、run03の見出し文言では正しく終端を検出できないため)。
#   (2) 語数内訳(length_report): sf1r1.section_word_counts()は「in one
#       line」という文言を含まない##見出しの内容(run03ではHook・Tension・
#       Closingの3つ全て)を集計から丸ごと落とす(実測検証済み、intro=0・
#       in_one_line=0になる)。###見出しのpoint_one/point_two自体はrun03が
#       常にちょうど2つしか使わない設計のため実測上は正しい値を返すが、
#       Hook/Tension/Closingが完全に欠落するため記事全体の語数内訳としては
#       使えない。そのため、run03ではHook/Voice A/Voice B/Tension/Closing
#       それぞれの正確な語数をsplit_five_voice_sections()から算出する。
#       sf1r1.section_word_counts()自体は無変更のまま引き続き呼び出し、
#       参考値としてlength_report.jsonに残す(スキーマ互換性のため)が、
#       5区切りの正確な内訳は別途five_section_length_report.jsonへ保存する。
# ============================================================
def _five_section_length_report(article_text: str) -> dict | None:
    sections = split_five_voice_sections(article_text)
    if sections is None:
        return None
    counts = {
        key: ab01.compute_word_count(sections[f"{key}_body"])
        for key in ("hook", "voice_a", "voice_b", "tension", "closing")
    }
    counts["total_of_five_sections"] = sum(counts.values())
    counts["headings"] = {
        key: sections[f"{key}_heading"] for key in ("hook", "voice_a", "voice_b", "tension", "closing")
    }
    counts["unexpected_preamble_before_first_heading"] = sections["unexpected_preamble_before_first_heading"]
    return counts


def run_voices_pattern_run03(client, theme_id: str, label: str, prompt: str, verified_ledger_text: str,
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

    # --- Point Overlap QA / Point Value QA: monitoring専用、5区切り構造専用
    # parser経由(理由は上記コメント参照)。
    print(f"[TRIAL-04][{theme_id}] {label}: Point Overlap/Value QA(monitoring専用、5区切り版)開始...")
    five_sections = split_five_voice_sections(article_text)
    if five_sections is None:
        monitoring_summary = {
            "qa_status": "SKIPPED",
            "lexical_flagged": False, "value_qa_flagged": False,
            "note": ("split_five_voice_sections()が想定する5見出し構造(Title後に##/###見出しが"
                     "ちょうど5つ、Hook/Voice A/Voice B/Tension/Closingの順)を検出できなかった"
                     "ため、Point Overlap/Value QA monitoringはmonitoring不能として記録する。"),
        }
        with open(f"{out_dir}/point_overlap_value_qa_monitoring.json", "w", encoding="utf-8") as f:
            json.dump(monitoring_summary, f, ensure_ascii=False, indent=2, default=str)
        print(f"[TRIAL-04][{theme_id}] {label}: 5区切り構造が検出できずQA monitoring不能として記録しました。")
    else:
        monitoring_summary = run_five_section_point_qa_monitoring(client, five_sections, writer_model, out_dir)

    # --- 以下、gen.run_one_pattern()のFact Checker/Ledger Deviation
    # Checker/Local Rewrite/Directional Fact Precheckロジックを、呼び出す
    # 関数・引数・順序とも一切変更せずそのままコピーする(run_voices_pattern()
    # と同一)。length_reportのみ5区切り版へ差し替える。---
    metrics = gen.compute_metrics(article_text)
    section_wc = sf1r1.section_word_counts(article_text)
    five_section_report = _five_section_length_report(article_text)
    length_report = {
        **section_wc, "total": metrics["word_count"],
        "point_one_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_one"] <= gen.POINT_TARGET_UPPER,
        "point_one_within_tolerance": gen.POINT_TOLERANCE_LOWER <= section_wc["point_one"] <= gen.POINT_TOLERANCE_UPPER,
        "point_two_within_target": gen.POINT_TARGET_LOWER <= section_wc["point_two"] <= gen.POINT_TARGET_UPPER,
        "point_two_within_tolerance": gen.POINT_TOLERANCE_LOWER <= section_wc["point_two"] <= gen.POINT_TOLERANCE_UPPER,
        "total_within_soft_range": gen.TOTAL_SOFT_LOWER <= metrics["word_count"] <= gen.TOTAL_SOFT_UPPER,
        "sf1r1_section_word_counts_note": ("sf1r1.section_word_counts()はrun03の5見出し構造を"
            "正確には解釈しない(「in one line」を含まない##見出し=Hook/Tension/Closingの内容を"
            "header_skipとして集計から丸ごと落とす。intro/in_one_lineは常に0になる。point_one/"
            "point_twoの値自体はrun03が###見出しを常にちょうど2つ[Voice A/Voice Bのみ]しか使わない"
            "設計のため実測上は正しいが、Hook/Tension/Closingが欠落するため記事全体の内訳としては"
            "使えない)。参考値としてのみ残す。正確な内訳はfive_section_length_report.jsonを参照。"),
    }
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/length_report.json", "w", encoding="utf-8") as f:
        json.dump(length_report, f, ensure_ascii=False, indent=2)
    if five_section_report is not None:
        with open(f"{out_dir}/five_section_length_report.json", "w", encoding="utf-8") as f:
            json.dump(five_section_report, f, ensure_ascii=False, indent=2)
    print(f"[TRIAL-04][{theme_id}] {label}: metrics={metrics} five_section_report={five_section_report}")

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
            "five_section_length_report": five_section_report,
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
        five_section_report = _five_section_length_report(article_text)
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
        if five_section_report is not None:
            with open(f"{out_dir}/five_section_length_report.json", "w", encoding="utf-8") as f:
                json.dump(five_section_report, f, ensure_ascii=False, indent=2)

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
            "five_section_length_report": five_section_report,
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
        "five_section_length_report": five_section_report,
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

    # EDITORIAL-B-FAMILY-VOICES-TRIAL-04 run04(往復3回目・最終): Phase A監査
    # ファイルはLEVEL_OUT_DIR(b1b_run04/)配下へ出力し、run01/run02/run03の
    # OUT_DIR配下・b1b_run02/・b1b_run03/配下を一切上書きしない。5区切り
    # 骨格・Writer adapter(run_voices_pattern_run03)はrun03のまま無変更で
    # 再利用する(Focus Module Blockの制約強化のみがrun04の差分)。
    phase_a = run_phase_a(f"{LEVEL_OUT_DIR}/audit")
    if not phase_a["phase_a_pass"]:
        print("[TRIAL-04] Phase Aで意図しない差分を検出したため、Writerへ進まずSTOPします。")
        return {"phase_a": phase_a, "phase_b": None, "status": "STOP_PHASE_A_UNEXPECTED_DIFF"}

    client = vfl01.get_client()
    # run04のcost logはrun01/run02/run03の既存tracked cost logへ追記して
    # 混在させないよう、b1b_run04/配下の別ファイルへ出力する。
    cl.install(f"{LEVEL_OUT_DIR}/raw_usage_log_trial04_writer_run04.jsonl")
    master_full_text = ab01.load_master_full_text()

    candidate_prompt = build_candidate_prompt(
        phase_a["candidate_template"], master_full_text, TOPIC_JA, verified_ledger_text,
        gen.B1_B_DIRECT_INSTRUCTION)

    print(f"[TRIAL-04] Writer呼び出し開始(run_voices_pattern_run03、adapter経由、run04出力)...")
    t0 = time.time()
    with cl.logging_context(THEME_ID, "writer_b1b_run04"):
        result = run_voices_pattern_run03(
            client, THEME_ID, LABEL, candidate_prompt, verified_ledger_text, TOPIC_JA, LEVEL_OUT_DIR)
    elapsed = time.time() - t0
    result["elapsed_seconds"] = round(elapsed, 1)

    with open(f"{LEVEL_OUT_DIR}/audit/candidate_prompt_used.txt", "w", encoding="utf-8") as f:
        f.write(candidate_prompt)

    # run01/run02/run03のtracked summaryファイルを上書きしないよう、run04
    # 専用のsummaryファイル名をLEVEL_OUT_DIR配下に出力する。
    with open(f"{LEVEL_OUT_DIR}/trial04_summary_run04.json", "w", encoding="utf-8") as f:
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
