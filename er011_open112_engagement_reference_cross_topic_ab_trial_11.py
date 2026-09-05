# ============================================================
# er011_open112_engagement_reference_cross_topic_ab_trial_11.py
# OPEN-112-ENGAGEMENT-REFERENCE-CROSS-TOPIC-AB-TRIAL-11
# ============================================================
# 目的: Trial-10(イラン/ホルムズ、単一テーマ)で確認した
#   A: Engagement根底指示あり / Reference Digestなし
#   B: Engagement根底指示あり / Reference Digestあり
# のA/B差を、性質の異なる2テーマ(週4日勤務/ゆっくり滞在型旅行)で追加確認し、
# Reference Digestの効果がテーマに依存する偶然かどうかの判断材料を増やす。
# Production採用判断はしない。
#
# Research方針(このファイル内で完結): 本Trial実行時点でAgentにWebSearch/
# WebFetchツールが与えられていないため、既存の承認済みResearch経路
# (er006_pronunciation_research_01.py等で既に使用実績のあるPerplexity
# chat/completions [model=sonar-pro]をrequests経由で呼び出すパターン)を
# 本ファイル内の新規関数として再利用する。新しいProduction Researcher
# モジュールは作らない。Perplexity料金は`er005_output/cost_baseline_01/
# pricing_snapshot.json`に記載が無いため、Perplexity呼び出し分のコストは
# 推測せず「金額不明」として報告する(OpenAI呼び出し分のみ同snapshotで算出)。
#
# Production変更: なし。既存ファイル(er003_v1_n3_01_articles_generate.py等)は
# 一切変更しない。gen.run_one_pattern()を無変更のまま呼び出す。新Validator・
# 新Fact Checker・新LLM QA・Overlap閾値変更は追加しない(既存QAのみで評価)。
#
# 今回禁止: Production Prompt/code変更、Common Writing Contract正式変更、
# Reference Digest正式実装、Engagement正式実装、News Focus Module正式化、
# Discovery変更、Ledger Production自動化、新Validator、Point Overlap閾値変更、
# Point長変更、Trend severity変更、SSOT上のProduction status変更、
# APPROVED_FOR_PRODUCTION、PRODUCTION_WIRED、Engagement指示文言の改良
# (Trial-10と一字一句同一)、品質が良くなるまでの再生成、テーマ名を前提にした
# Trendの捏造、代替テーマの勝手な選択、Git操作、他Agent起動。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
from __future__ import annotations

import difflib
import json
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import requests

import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er011_no18_specfix_v2_production_run_01 as driver
import er011_open112_trend_synthesis_minimal_prompt_trial_09 as trial09

PHASE_A_BASELINE_DIR = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2_ec_a_precision_21r"
PHASE_A_TOPIC_JA = driver.TOPIC_JA

NEW_THEME_ID = "open112_engagement_reference_cross_topic_ab_trial_11"
OUT_DIR = f"er011_output/{NEW_THEME_ID}"
RESEARCH_DIR = f"{OUT_DIR}/research"
os.makedirs(RESEARCH_DIR, exist_ok=True)

# ------------------------------------------------------------
# Trend Synthesis Focus Module / Anchor(Trial-09と一字一句同一。テーマに
# 依存しない汎用のFocus Module文面のため、テーマだけを差し替えて再利用する)
# ------------------------------------------------------------
ANCHOR = trial09.ANCHOR
TREND_SYNTHESIS_FOCUS_MODULE_BLOCK = trial09.TREND_SYNTHESIS_FOCUS_MODULE_BLOCK

LEVELS = {"b1b": {"label": "B1B", "instruction_attr": "B1_B_DIRECT_INSTRUCTION"}}
MAX_RUNS_PER_LEVEL = 2  # Loop Budget(初回1回、判別困難な場合のみ+1回まで)

THEMES = ["theme1_4day_workweek", "theme2_slow_travel"]

THEME_META = {
    "theme1_4day_workweek": {
        "label": "Theme 1: 週4日勤務",
        "query_topic_en": "four-day workweek adoption trend among Japanese companies 2026",
        "query_topic_ja": "日本企業 週4日勤務 導入 検討 2026年",
    },
    "theme2_slow_travel": {
        "label": "Theme 2: ゆっくり滞在型旅行",
        "query_topic_en": "young Japanese travelers shifting from sightseeing checklist trips to slow long-stay travel 2026",
        "query_topic_ja": "若者 旅行 名所巡り から ゆっくり滞在 変化 2026年",
    },
}

# ------------------------------------------------------------
# 施策1: Entertainment / Engagement 根底原則(Trial-10と一字一句同一)
# ------------------------------------------------------------
ENTERTAINMENT_ENGAGEMENT_BLOCK = """【Interesting/Engaging/Entertaining原則(今回のTrialで追加する根底品質原則。\
OPEN-112-TREND-ENGAGEMENT-REFERENCE-AB-TRIAL-10、Production未採用)】
記事は、正確でよく整理されているだけでは十分ではありません。聞き手が

- 続きを知りたくなる
- 「そういう見方があるのか」と感じる
- 意外な関係や対比に気づく
- 話として面白いと感じる
- 誰かに話したくなる

と感じられることを目指してください。ただし、面白さを作るためにVerified Fact
Ledgerの範囲を超えてはいけません。以下は禁止です:
- 事実の創作
- Ledgerが支持しない因果関係の主張(unsupported causality)
- 誇張(exaggeration)・扇情的な表現(sensationalism)
- Ledgerにない具体例の追加
- 根拠のない心理描写
- 根拠のない未来予測

目標は「正確 + 面白い + (裏付けがある場合の)意外性 + 聞いていて楽しい」の
組み合わせであり、面白さが正確さより優先されるという意味ではありません。
面白くする余地とFact Ledgerの制約が衝突する場合は、常にFact Ledgerの制約を
優先してください。

【Storytelling原則(時系列の出来事列挙にしない)】
Main Storyを、"A happened. Then B happened. Then C happened. Meanwhile D
happened."のような時系列ニュースダイジェストにしないでください。まず、
「この複数のSignalを一緒に見ると、何が興味深いのか」を先に見つけてください。
そのうえで、それを伝えるために本当に必要なEvidenceだけを選び、ひとつの
Story(throughline)として展開してください。個々の出来事を、起きた順番に
律儀になぞる必要はありません。

Main Storyの冒頭では、Verified Fact Ledgerの範囲内で成立する場合に限り、
以下のいずれかの技法を使うことを検討してください:
- contradiction(矛盾)
- surprising contrast(意外な対比)
- tension(緊張関係)
- reversal(見方の逆転)
- unexpected consequence(意外な結果)
- unanswered question(まだ答えの出ていない問い)
- gap between appearance and reality(見かけと実態のずれ)

これらの技法を無理に使う必要はありません。Ledgerが支持しない「意外性」を
発明することは禁止します。技法を使うかどうかより、記事全体がひとつの
throughlineを持つことを優先してください。"""


# ============================================================
# Research: Verified Fact Ledger構築(Perplexity sonar-pro、既存呼び出し
# パターンの再利用。新規Production Researcherモジュールは作らない)
# ============================================================
PERPLEXITY_MODEL = "sonar-pro"

FACT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "facts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fact_id": {"type": "string"},
                    "verified_fact": {"type": "string",
                                       "description": "事実そのものの説明(日本語または英語)"},
                    "number_or_stat": {"type": ["string", "null"]},
                    "actor_or_organization": {"type": ["string", "null"]},
                    "signal": {"type": "string",
                               "description": "この事実が示す変化・指標は何か"},
                    "signal_direction": {"type": "string",
                                          "description": "increasing/decreasing/mixed/emerging等"},
                    "evidence_strength": {
                        "type": "string",
                        "description": "official_statistics / government_official_announcement / "
                                        "company_official_announcement / reputable_media_reporting / "
                                        "industry_survey / private_analysis / advocacy_or_opinion / anecdotal のいずれか",
                    },
                    "counter_signal_or_limitation": {"type": ["string", "null"]},
                    "time_window": {"type": ["string", "null"]},
                    "source_name": {"type": "string"},
                    "source_url": {"type": ["string", "null"]},
                    "publication_date": {"type": ["string", "null"]},
                },
                "required": ["fact_id", "verified_fact", "number_or_stat", "actor_or_organization",
                             "signal", "signal_direction", "evidence_strength",
                             "counter_signal_or_limitation", "time_window", "source_name",
                             "source_url", "publication_date"],
            },
        },
    },
    "required": ["facts"],
}


def _perplexity_call(theme_id: str, stage: str, model: str, messages: list[dict],
                      response_format: dict | None = None, timeout: float = 90.0) -> dict:
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


FACT_RESEARCH_PROMPT = """あなたはニュース記事のFact Checker/Researcherです。以下のテーマについて、
2026年9月時点で最新の、独立した複数の情報源に基づく事実を調べてください。

【テーマ】
{topic_ja}
({topic_en})

【調査対象として重視してほしい観点】
- 具体的な企業・組織・政府機関の動き(名前・日付・数字を含む)
- 統計・調査データ(公的機関または業界団体・大手調査会社によるもの)
- この変化に対する反証・限界・慎重論(counter-signal)
- この変化がいつ頃から見え始めたか(time window)
- 単一の出来事ではなく、複数の独立した兆候(signal)が存在するか

【出力ルール】
- 最低8件、できれば10件以上のfactを、実際に検索で確認できたものだけ出力してください。
- 検索で確認できない推測・一般論は書かないでください。
- 各factについて、number_or_stat(具体的な数字があれば)、actor_or_organization、
  signal(この事実が示す変化)、signal_direction、evidence_strength、
  counter_signal_or_limitation(あれば)、time_window、source_name、source_url、
  publication_dateを可能な限り埋めてください。分からない項目はnullにしてください。
- evidence_strengthは、公式統計/政府発表/企業公式発表/大手メディア報道/業界調査/
  民間分析/意見記事/anecdotalのどれに当たるかを区別してください。同列に扱わないでください。
- 少なくとも2件は、この変化に対するcounter-signal(反証・限界・慎重論・逆方向の動き)を
  中心に扱うfactにしてください。
"""


def research_theme_facts(theme_id: str) -> dict:
    meta = THEME_META[theme_id]
    prompt = FACT_RESEARCH_PROMPT.format(topic_ja=meta["query_topic_ja"], topic_en=meta["query_topic_en"])
    with cl.logging_context(theme_id, "research_facts"):
        result = _perplexity_call(
            theme_id, "research_facts", PERPLEXITY_MODEL,
            [{"role": "user", "content": prompt}],
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


def verify_theme_facts(theme_id: str, facts_json_text: str) -> dict:
    prompt = VERIFICATION_PROMPT.format(facts_json=facts_json_text)
    with cl.logging_context(theme_id, "verify_facts"):
        result = _perplexity_call(
            theme_id, "verify_facts", PERPLEXITY_MODEL,
            [{"role": "user", "content": prompt}],
            response_format={"type": "json_schema", "json_schema": {"schema": VERIFICATION_JSON_SCHEMA}})
    return result


REFERENCE_DISCOVERY_PROMPT = """次のテーマについて、英語圏の質の高いニュース/雑誌メディアが書いた、
構成・切り口が優れている記事を3〜5本探してください(2025〜2026年に公開されたもの優先)。

テーマ: {topic_en}

各記事について、publisher、title、url、published_dateを出力してください。事実の中身は
不要です(記事を探すことだけが目的です)。
"""

REFERENCE_DISCOVERY_SCHEMA = {
    "type": "object",
    "properties": {
        "articles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "publisher": {"type": "string"},
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "published_date": {"type": ["string", "null"]},
                },
                "required": ["publisher", "title", "url", "published_date"],
            },
        },
    },
    "required": ["articles"],
}


def discover_reference_articles(theme_id: str) -> dict:
    meta = THEME_META[theme_id]
    prompt = REFERENCE_DISCOVERY_PROMPT.format(topic_en=meta["query_topic_en"])
    with cl.logging_context(theme_id, "reference_discovery"):
        result = _perplexity_call(
            theme_id, "reference_discovery", PERPLEXITY_MODEL,
            [{"role": "user", "content": prompt}],
            response_format={"type": "json_schema", "json_schema": {"schema": REFERENCE_DISCOVERY_SCHEMA}})
    return result


REFERENCE_STRUCTURE_PROMPT = """以下の記事URLを読み、それぞれについて「構成・切り口・見せ方」だけを
観察して報告してください。これは絶対に厳守してください:

- 記事中の具体的な数字・統計・日付・固有名詞(社名・人名・地名)・直接引用・因果関係の
  主張は、一切書き出さないでください(要約にもしないでください)。
- あなたが書いてよいのは、次の5項目だけです: opening_technique(書き出しの技法)、
  central_angle(記事の中心的な切り口)、interesting_contrast(記事が使っている対比・意外性の
  構造)、structural_technique(記事全体の構成上の技法)、why_it_feels_engaging(なぜ読者を
  引き込むと感じるか)。
- 上記5項目はすべて、技法の説明として抽象的に書いてください(例:「ある主張を先に示し、
  直後にそれを覆す情報を出す」のような書き方は良いですが、その主張・覆す情報の具体的中身は
  書かないでください)。

対象記事:
{article_list}
"""

REFERENCE_STRUCTURE_SCHEMA = {
    "type": "object",
    "properties": {
        "observations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "opening_technique": {"type": "string"},
                    "central_angle": {"type": "string"},
                    "interesting_contrast": {"type": "string"},
                    "structural_technique": {"type": "string"},
                    "why_it_feels_engaging": {"type": "string"},
                },
                "required": ["url", "opening_technique", "central_angle", "interesting_contrast",
                             "structural_technique", "why_it_feels_engaging"],
            },
        },
    },
    "required": ["observations"],
}


def analyze_reference_structure(theme_id: str, articles: list[dict]) -> dict:
    article_list = "\n".join(f"- {a['publisher']}: {a['title']} ({a['url']})" for a in articles)
    prompt = REFERENCE_STRUCTURE_PROMPT.format(article_list=article_list)
    with cl.logging_context(theme_id, "reference_structure_analysis"):
        result = _perplexity_call(
            theme_id, "reference_structure_analysis", PERPLEXITY_MODEL,
            [{"role": "user", "content": prompt}],
            response_format={"type": "json_schema", "json_schema": {"schema": REFERENCE_STRUCTURE_SCHEMA}})
    return result


# ============================================================
# Ledger / Topic(Research実施済み、research/配下の手作業curationファイルを読み込む)
# ============================================================
with open(f"{RESEARCH_DIR}/theme1_verified_fact_ledger.txt", encoding="utf-8") as _f:
    THEME1_LEDGER_TEXT = _f.read()
with open(f"{RESEARCH_DIR}/theme2_verified_fact_ledger.txt", encoding="utf-8") as _f:
    THEME2_LEDGER_TEXT = _f.read()

THEME1_TOPIC_JA = (
    "2026年9月時点、日本企業における選択的週休3日制・週4日勤務は、目立つ個別の動きと、"
    "全国統計上の実態との間に興味深いギャップが生じている。日本たばこ産業(JT)は2026年"
    "6月、2027年4月から選択的週休3日制を導入すると発表し、日立製作所・パナソニック"
    "ホールディングス・ファーストリテイリング・ロート製薬など複数の大手企業がすでに"
    "何らかの形で週休3日・週4日勤務の制度を導入している。求人サイトIndeed Japanの"
    "データでは、「週休3日」に関する求人件数がこの5年で5.3倍、検索件数が3.6倍に増えて"
    "おり、日本経済新聞の調査でも従業員が最も導入を希望する制度の一つに週休3日制が"
    "挙がっている。しかし、厚生労働省の公式統計「就労条件総合調査」によれば、「何らかの"
    "週休3日制」を採用している企業の割合は、2024年度調査の1.6%から2025年度調査では"
    "0.9%へとむしろ低下している。さらに、パナソニックホールディングスでは制度自体は"
    "用意されていても、実際に週休3日・4日を選択している社員はごく一部にとどまるという"
    "報道もある。つまり今回の記事が扱うのは、単純な「導入が増えている」という話ではなく、"
    "目立つ発表・関心の高まりと、全国レベルでの実際の普及率(むしろ足元で縮小)との間に"
    "広がるギャップという、Trend Synthesisタイプの記事である。"
)

THEME2_TOPIC_JA = (
    "2026年9月時点、日本の若者(とくに男性)の旅行に対する意識には、「もっと自分の"
    "ペースで、ゆっくり過ごしたい」という願望の高まりがいくつもの独立した調査で確認"
    "されている。日本交通公社(JTBF)の2025年調査では、29歳以下の男性が好む旅行"
    "スタイルの上位に「ひとり旅」(25.2%)・「趣味を深める旅行」(24.3%)が挙がり、海外"
    "旅行経験のある日本のZ世代の約9割が「ツアー内に自由時間が欲しい」と回答し、その"
    "うち約8割が半日以上の自由時間を希望している。じゃらんリサーチセンターの調査では、"
    "1カ月休暇が取れた場合に希望する旅行日数として「1週間程度」と答えた人が24.1%で"
    "最多だった。しかし、同じじゃらんリサーチセンターの別の調査(2024年秋)では、実際の"
    "旅行意向者の宿泊日数は平均1.8泊・中央値2.0泊にとどまっている。観光庁の「令和7年版"
    "観光白書」も、政策的課題として「一人当たり旅行回数の増加や滞在長期化を図る必要が"
    "ある」と明記しており、これは現時点では滞在がまだ十分に長期化していないことを政府"
    "自身が認めた形になっている。また、29歳以下の女性では「有名な観光地を巡る」ことへの"
    "関心が依然として44.7%と高く、性別によって傾向は異なる。今回の記事が扱うのは、"
    "「名所巡りからゆっくり滞在へ、すでに完全に変わった」という単純な話ではなく、意識・"
    "願望としてのスロー志向の高まりと、実際に測定されている短い滞在日数との間のギャップ"
    "という、Trend Synthesisタイプの記事である。"
)

THEME_TOPIC = {"theme1_4day_workweek": THEME1_TOPIC_JA, "theme2_slow_travel": THEME2_TOPIC_JA}
THEME_LEDGER = {"theme1_4day_workweek": THEME1_LEDGER_TEXT, "theme2_slow_travel": THEME2_LEDGER_TEXT}

# ------------------------------------------------------------
# Reference Digest観察メモ(実際にPerplexity[sonar-pro]で収集した実在Reference記事
# について、事実を含まない「構成・切り口」だけをLLMに観察させた結果を、Trial-10と
# 同じ人間可読フォーマットへ整形したもの。数字・固有名詞・引用は含まれていない
# ことを目視確認済み[research/theme{1,2}_reference_structure_parsed.json参照])。
# ------------------------------------------------------------
REFERENCE_OBSERVATION_NOTES_THEME1 = """
Reference 1(経済メディア、著名経営者の未来予測を扱った記事):
- Opening technique: 話題性の高い人物の象徴的な発言をフックとして冒頭に置き、
  「この人たちがこう言っている」という意外性から読者の好奇心を立ち上げる。
- Central angle: 複数の経営者の発言を軸に、まだ起きていない変化を未来予測・テック
  潮流として扱い、読者に先回りして検討させる。
- Interesting contrast: 「夢のような未来像」と「現状の勤務スタイル」を対比させ、
  期待と懐疑を同時に提示する。複数のリーダーが語るレベル感の違いも並べる。
- Structural technique: 前半で主要な発言・予測をコンパクトに並べて「潮流」を提示し、
  後半で背景・関連議論を重ねる「見取り図→ディテール」型の構成。
- Why it feels engaging: 著名人の未来予測を並べることで「本当にこうなるのか?」
  という思考実験を誘発し、複数視点を短いフレーズでテンポよく提示する。

Reference 2(ビジネスメディア、かつて期待された制度の「失速」を扱う記事):
- Opening technique: 「あの話はどこへ行ったのか?」という、読者の記憶にある話題を
  問いかける導入で、かつての期待感を思い起こさせながら現在との落差を見せる。
- Central angle: かつて盛り上がったアイデアが環境変化で勢いを失っているという
  「失速ストーリー」を軸に、現在の雰囲気・力関係の変化を描く。
- Interesting contrast: 過去の熱気と現在の冷え込みを時間軸で対比。労働者にとって
  魅力的な制度と、経営側が重視する成果・統制への志向を並べ、利害のズレを見せる。
- Structural technique: 冒頭で「一時期盛り上がった理想像」を描写し、すぐ現在の
  雰囲気に切り替える。中盤で要因を複数列挙し、終盤は「一時休止」の印象で締める。
- Why it feels engaging: かつての期待を思い出させたうえで現実を示す構成が、軽い
  ショックと納得感を同時に与える。

Reference 3(国際メディア、文化的ステレオタイプと新しい試みの対比を扱う記事):
- Opening technique: 国の働き方に関する象徴的なイメージを提示し、それと対照的な
  新しい試みを並べ、「そんな国がこういうことを始めている」という意外性から導入する。
- Central angle: 「働く文化が強い社会が、労働時間短縮を試す」という構図で、政策的な
  試みと社会の価値観のズレ・調整過程を描く。
- Interesting contrast: 長時間労働が当たり前の文化と、短い労働週を推進する政策目標を
  対比。制度導入の意図と、企業・個人が抱く懸念・期待を並べる。
- Structural technique: 前半で政策的方針を説明し「何が試されているのか」を整理した
  うえで、後半で個々の働き手の視点・反応を紹介する二段構え。
- Why it feels engaging: 文化的ステレオタイプと真逆の方向へ進もうとする動きを描く
  ことで、「本当にそんな変化が起きるのか?」という好奇心を喚起する。

Reference 4(分析系記事、世界的潮流か限定的実験かを検討する記事):
- Opening technique: タイトルで読者が抱きがちなイメージ(世界的トレンド)と、別の
  可能性(限定的な実験)を並列させ、最初から問いの構図を提示する。
- Central angle: 「新しい働き方は世界的潮流なのか、それとも一部の実験にとどまるのか」
  という二項対立の問いを、証拠を積み上げて検討する分析的な切り口。
- Interesting contrast: 理想的なキャッチフレーズとしての「世界的トレンド」という
  イメージと、実際に恒久導入されている割合の小ささを対比し、イメージと現実のギャップ
  を示す。
- Structural technique: 冒頭で現状を一文で整理し、直後に複数の国・地域の事例を
  紹介。中盤で統計的指標を整理し「なぜ思ったほど広がっていないのか」を分析。終盤で
  今後のシナリオを示す「現状評価→原因分析→提言」型の論説構造。
- Why it feels engaging: あえて熱狂を少し冷ますような冷静なデータ分析を行うことで、
  「分かったつもり」をほどきながら新しい理解を与える。
"""

REFERENCE_OBSERVATION_NOTES_THEME2 = """
Reference 1(旅行業界ニュース、観光政策と旅のスタイルを結びつける記事):
- Opening technique: 政策的な大枠を先に置き、その後で旅のスタイルを解決策として
  接続する導入。
- Central angle: 観光の量をめぐる大きな方針と、より分散・長期滞在型の旅の考え方を
  結びつける切り口。
- Interesting contrast: 大きな集客目標の話と、混雑をならすための旅のスタイルを
  並置し、拡大と緩和を同時に語る構造。
- Structural technique: 冒頭で問題設定を提示し、中盤で考え方の転換を示し、終盤で
  実践的な含意へ寄せる三段構成。
- Why it feels engaging: 大きな方向性と身近な旅行体験をひとつの線で結び、抽象的な
  テーマを具体的な読後感に落とし込む。

Reference 2(PR/マーケティング系メディア、調査データを行動様式から読み解く記事):
- Opening technique: まず行動のタイプ分け(予定管理のしかた)を示し、そこから旅の
  意識に話を広げる分析型の導入。
- Central angle: 予定管理のしかたという行動様式から、旅のしやすさや旅への向き合い方
  を読み解く切り口。
- Interesting contrast: きっちり組み立てる態度と、気分に合わせて動く態度を対比し、
  その違いを旅行意識の差として見せる。
- Structural technique: 属性の比較で読者の注意をつかみ、次に意識面の差へ進み、最後に
  全体傾向を回収する積み上げ型の構成。
- Why it feels engaging: 自分の普段の行動に引き寄せて読めるため、調査記事でありながら
  自己診断的な面白さがある。

Reference 3(旅行ガイド系メディア、「スロー」の定義から入る記事):
- Opening technique: 定義を先に与えてから、その定義を体感できる行動の例へ移る説明型
  の導入。
- Central angle: 旅を「多くを見ること」ではなく「深く滞在すること」として再定義する
  切り口。
- Interesting contrast: 観光的な消費の発想と、暮らしに近づく発想を対比し、旅の価値
  基準を反転させる。
- Structural technique: 概念説明のあとに行動指針を並べ、さらに細かな実践例で肉付け
  する、ガイド型の段階構成。
- Why it feels engaging: 抽象論で終わらず、すぐ試せる行動イメージに落とすことで、
  読み手が自分の旅に置き換えやすくなる。

Reference 4(ラグジュアリー旅行系メディア、家族向け旅程を提案する記事):
- Opening technique: タイトル段階で旅のスタイルと対象読者像を重ね、すぐに読者を
  絞り込む入り方。
- Central angle: ゆったりした旅を、上質さや家族向け体験と結びつけて提案する切り口。
- Interesting contrast: 速く回る効率型の旅と、余白を楽しむ余裕型の旅を対比し、後者を
  魅力的に見せる。
- Structural technique: 移動・滞在・体験の流れに沿って旅程を組む、実用ガイドとしての
  順序立てが中心。
- Why it feels engaging: 抽象的な理念ではなく、具体的な旅の流れとして見せることで、
  完成形を想像しやすくする。
"""

THEME_REFERENCE_NOTES = {
    "theme1_4day_workweek": REFERENCE_OBSERVATION_NOTES_THEME1,
    "theme2_slow_travel": REFERENCE_OBSERVATION_NOTES_THEME2,
}

# ------------------------------------------------------------
# 施策2: Reference Digest(Bのみ)。Trial-10と同一のprompt構造・同一の
# 承認済みcontract(B1_WRITER)を再利用し、テーマごとの観察メモだけを差し替える。
# ------------------------------------------------------------
REFERENCE_DIGEST_PROMPT = """あなたはeigo-radioのニュース記事Writerを補助する、構成・切り口専門の
編集アシスタントです。以下は、今回のTrendテーマと同じ/近いテーマを扱った、
質の高い4本の記事について、人間の編集者が「構成・切り口・見せ方」だけを
観察してまとめた生メモです。

このメモには、意図的に具体的な事実(数字・日付・固有名詞・引用・因果関係の
主張)は一切含まれていません。あなたの仕事は、このメモを土台に、今回の
Writer(別の記事を書くAI)へ渡す「Reference Digest」を整形することです。

【生メモ】
{notes}

【出力ルール(絶対厳守)】
- 出力は日本語で構いません。Reference 1〜4それぞれについて、
  Opening technique / Central angle / Interesting contrast /
  Structural technique / Why it feels engaging の5項目を簡潔に書いてください。
- 最後に、統合Digestとして以下を書いてください:
  useful opening patterns / useful contrasts / useful story structures /
  possible angles(ただし今回のFact Ledgerの範囲内でも使えそうな、
  抽象的な切り口の型のみ。具体的なFactを提案しないこと) /
  techniques to avoid chronological listing
- 具体的な数字・日付・固有名詞(社名・人名・メディア名・地名の追加)・
  引用・出来事は、一切新しく書き加えないでください。生メモに無い具体的な
  Factを絶対に作り出さないでください。
- 表現・文章そのものの模倣・転載はしないでください(技法の説明であって、
  文章のコピーではありません)。
- 冒頭に必ず次の警告文をそのまま含めてください:
  「これはFact Ledgerではありません。数字・日付・出来事・引用・行為者・
  因果説明・予測など、具体的Factは一切含みません。Reference Articlesの
  表現・文章のコピーもしないでください。ここにあるのは構成・切り口・
  見せ方のヒントだけです。事実は必ずVerified Fact Ledgerだけを根拠に
  してください。」
"""


def build_reference_digest(client, theme_id: str) -> dict:
    """Reference Digest生成(Bのみ・実LLM呼び出し)。既存の承認済みcontract
    (B1_WRITERプロセス、routing.WRITER_MODEL)を再利用する(Production routing
    fileへの変更なし)。"""
    model = routing.require_model("B1_WRITER", routing.WRITER_MODEL)
    notes = THEME_REFERENCE_NOTES[theme_id]
    prompt = REFERENCE_DIGEST_PROMPT.format(notes=notes)
    with cl.logging_context(f"{theme_id}_b", "reference_digest_generation"):
        response = client.responses.create(model=model, input=prompt)
    text = getattr(response, "output_text", None)
    if not text:
        chunks = []
        for item in getattr(response, "output", []) or []:
            for c in getattr(item, "content", []) or []:
                if getattr(c, "text", None):
                    chunks.append(c.text)
        text = "\n".join(chunks)
    return {"text": text.strip(), "model": model, "response_id": getattr(response, "id", None)}


def build_reference_digest_block(digest_text: str) -> str:
    return ("【Reference Digest(構成・切り口の参考。Fact sourceではない。"
            "OPEN-112-ENGAGEMENT-REFERENCE-CROSS-TOPIC-AB-TRIAL-11、Production未採用)】\n"
            + digest_text)


# ------------------------------------------------------------
# Template構築(A/B 2バリアント、テーマ非依存。Trial-10と同一構造)
# ------------------------------------------------------------
def build_candidate_template(variant: str, reference_digest_block: str | None = None) -> str:
    assert ANCHOR in gen.COMMON_BLOCK_TEMPLATE, (
        "アンカー文字列がgen.COMMON_BLOCK_TEMPLATE内に見つかりません。Production側のtemplateが"
        "本Trial設計時から変更されている可能性があるため中断してください(STOP条件)。")
    blocks = [TREND_SYNTHESIS_FOCUS_MODULE_BLOCK, ENTERTAINMENT_ENGAGEMENT_BLOCK]
    if variant == "B":
        assert reference_digest_block is not None
        blocks.append(reference_digest_block)
    insertion = "\n\n".join(blocks)
    return gen.COMMON_BLOCK_TEMPLATE.replace(ANCHOR, insertion + "\n\n" + ANCHOR, 1)


def build_candidate_prompt(candidate_template: str, master_full_text: str, topic: str,
                            verified_ledger_text: str, instruction: str) -> str:
    common_block = candidate_template.format(
        hanshin_master_full_text=master_full_text, topic=topic,
        verified_ledger_text=verified_ledger_text,
        shared_point_blueprint_block="", evidence_compression_block="")
    return gen.build_prompt(common_block, instruction)


# ------------------------------------------------------------
# Phase A: 静的差分確認(テーマ非依存の機械的検証。Trial-10と同じ設計)
# ------------------------------------------------------------
def run_phase_a(master_full_text: str, phase_a_ledger_text: str,
                 reference_digest_block_for_check: str) -> dict:
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    templates = {
        "A": build_candidate_template("A"),
        "B": build_candidate_template("B", reference_digest_block_for_check),
    }
    for variant, tpl in templates.items():
        with open(f"{OUT_DIR}/audit/candidate_template_{variant}.txt", "w", encoding="utf-8") as f:
            f.write(tpl)

    results = {}
    for variant, candidate_template in templates.items():
        for level, meta in LEVELS.items():
            instruction = getattr(gen, meta["instruction_attr"])
            candidate_prompt = build_candidate_prompt(
                candidate_template, master_full_text, PHASE_A_TOPIC_JA, phase_a_ledger_text, instruction)
            baseline_path = f"{PHASE_A_BASELINE_DIR}/{level}/audit/prompt.txt"
            with open(baseline_path, encoding="utf-8") as f:
                baseline_prompt = f.read()

            key = f"{variant}_{level}"
            with open(f"{OUT_DIR}/audit/phase_a_candidate_prompt_{key}.txt", "w", encoding="utf-8") as f:
                f.write(candidate_prompt)

            insertion = ("\n\n".join(
                [TREND_SYNTHESIS_FOCUS_MODULE_BLOCK, ENTERTAINMENT_ENGAGEMENT_BLOCK]
                + ([reference_digest_block_for_check] if variant == "B" else [])))
            reconstructed = baseline_prompt.replace(ANCHOR, insertion + "\n\n" + ANCHOR, 1)

            sm = difflib.SequenceMatcher(a=baseline_prompt, b=candidate_prompt, autojunk=False)
            opcodes = sm.get_opcodes()
            non_equal = [op for op in opcodes if op[0] != "equal"]
            unexpected = [op for op in non_equal if op[0] != "insert"]
            insert_ops = [op for op in non_equal if op[0] == "insert"]
            clean_single_insert = (len(unexpected) == 0 and len(insert_ops) == 1
                                    and reconstructed == candidate_prompt)

            results[key] = {
                "baseline_len": len(baseline_prompt), "candidate_len": len(candidate_prompt),
                "op_counts": {tag: sum(1 for o in opcodes if o[0] == tag) for tag in
                              ("equal", "insert", "delete", "replace")},
                "unexpected_op_count": len(unexpected),
                "clean_single_insert_confirmed": clean_single_insert,
            }
            print(f"[TRIAL-11][Phase A][{key}] op_counts={results[key]['op_counts']} "
                  f"clean_single_insert_confirmed={clean_single_insert}")

    phase_a_pass = all(r["clean_single_insert_confirmed"] for r in results.values())
    with open(f"{OUT_DIR}/audit/phase_a_result.json", "w", encoding="utf-8") as f:
        json.dump({"results": results, "phase_a_pass": phase_a_pass}, f, ensure_ascii=False, indent=2)
    print(f"[TRIAL-11][Phase A] phase_a_pass={phase_a_pass}")
    return {"results": results, "phase_a_pass": phase_a_pass, "templates": templates}


# ------------------------------------------------------------
# Phase B: A/B実生成(実Production関数を無変更のまま使用)
# ------------------------------------------------------------
def run_pattern(client, candidate_template: str, master_full_text: str, theme_id: str, level: str,
                 variant: str, run_idx: int) -> dict:
    meta = LEVELS[level]
    instruction = getattr(gen, meta["instruction_attr"])
    topic = THEME_TOPIC[theme_id]
    ledger_text = THEME_LEDGER[theme_id]
    candidate_prompt = build_candidate_prompt(candidate_template, master_full_text, topic, ledger_text,
                                               instruction)
    theme_id_variant = f"{theme_id}_{variant.lower()}"
    level_out_dir = f"{OUT_DIR}/{theme_id}/{variant}_{level}_run{run_idx:02d}"

    print(f"[TRIAL-11][Phase B] theme={theme_id} variant={variant} {meta['label']} run{run_idx}: "
          f"gen.run_one_pattern()(実Production関数、無変更)開始...")
    t0 = time.time()
    with cl.logging_context(theme_id_variant, f"writer_{level}_run{run_idx:02d}"):
        result = gen.run_one_pattern(
            client, theme_id_variant, meta["label"], candidate_prompt, ledger_text, topic, level_out_dir)
    elapsed = time.time() - t0
    result["elapsed_seconds"] = round(elapsed, 1)
    result["variant"] = variant
    result["theme_id"] = theme_id

    with open(f"{level_out_dir}/audit/candidate_prompt_used.txt", "w", encoding="utf-8") as f:
        f.write(candidate_prompt)

    writer_model = None
    try:
        with open(f"{level_out_dir}/audit/writer_attempts.json", encoding="utf-8") as f:
            attempts = json.load(f)
        pass_attempt = next((a for a in attempts if a["status"] == "STRUCTURE_PASS"), None)
        writer_model = pass_attempt.get("model") if pass_attempt else None
    except FileNotFoundError:
        pass
    result["writer_model_actual"] = writer_model

    print(f"[TRIAL-11][Phase B] theme={theme_id} variant={variant} {meta['label']} run{run_idx}: 完了。"
          f"status={result.get('status')} fact_verdict={result.get('fact_verdict')} "
          f"ledger_status={result.get('ledger_status')} writer_model={writer_model} "
          f"elapsed={result['elapsed_seconds']}s")
    return result


def main() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    master_full_text = ab01.load_master_full_text()
    with open(f"{PHASE_A_BASELINE_DIR}/research/verified_fact_ledger.txt", encoding="utf-8") as f:
        phase_a_ledger_text = f.read()

    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_trial11.jsonl")

    digest_blocks = {}
    for theme_id in THEMES:
        print(f"[TRIAL-11] Reference Digest生成(theme={theme_id}, Bのみ、実LLM呼び出し)開始...")
        digest_result = build_reference_digest(client, theme_id)
        with open(f"{RESEARCH_DIR}/{theme_id}_reference_digest_raw.json", "w", encoding="utf-8") as f:
            json.dump(digest_result, f, ensure_ascii=False, indent=2, default=str)
        block = build_reference_digest_block(digest_result["text"])
        with open(f"{RESEARCH_DIR}/{theme_id}_reference_digest_block_used.txt", "w", encoding="utf-8") as f:
            f.write(block)
        digest_blocks[theme_id] = block
        print(f"[TRIAL-11] Reference Digest生成完了(theme={theme_id})。model={digest_result['model']} "
              f"response_id={digest_result['response_id']}")

    phase_a = run_phase_a(master_full_text, phase_a_ledger_text, digest_blocks[THEMES[0]])
    if not phase_a["phase_a_pass"]:
        print("[TRIAL-11] Phase Aで意図しない差分を検出したため、Phase Bへ進まずSTOPします。")
        return {"phase_a": phase_a, "phase_b": None, "status": "STOP_PHASE_A_UNEXPECTED_DIFF"}

    phase_b = {}
    for theme_id in THEMES:
        templates = {
            "A": build_candidate_template("A"),
            "B": build_candidate_template("B", digest_blocks[theme_id]),
        }
        phase_b[theme_id] = {}
        for variant in ["A", "B"]:
            phase_b[theme_id][variant] = run_pattern(
                client, templates[variant], master_full_text, theme_id, "b1b", variant, 1)

    with open(f"{OUT_DIR}/trial11_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "phase_a": phase_a["results"],
            "phase_b": {t: {v: {k: val for k, val in r.items() if k != "article_text"}
                             for v, r in variants.items()} for t, variants in phase_b.items()},
        }, f, ensure_ascii=False, indent=2, default=str)

    print(f"[TRIAL-11] 完了。summary -> {OUT_DIR}/trial11_summary.json")
    return {"phase_a": phase_a, "phase_b": phase_b, "status": "DONE"}


if __name__ == "__main__":
    main()
