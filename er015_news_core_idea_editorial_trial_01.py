# ============================================================
# er015_news_core_idea_editorial_trial_01.py
# NEWS-CORE-IDEA-EDITORIAL-TRIAL-01 (Fable設計、2026-09-23)
# ============================================================
# 目的: News記事の「解説記事へ途中で戻る」問題(H1〜H4仮説)を検証する
# ため、Core Idea中心・Evidence選択方式のPrompt/フロー5系統(T0〜T4)を
# Writer=gpt-5.6-luna(routing.WRITER_MODEL)で各1回ずつ生成し、Fact Gate・
# 予備採点・コスト記録を行うTrial専用スクリプト。**Production実装ではない**。
#
# Production正式path(er011_*/er014_*等)は一切変更しない。本ファイルからは
# 既存Production moduleを「import利用」または「同型の最小実装」でのみ使う。
# 具体的には:
#   - er003_v1_en_direct_vfl_01_generate(vfl01): MODEL(=routing.WRITER_MODEL
#     ="gpt-5.6-luna")/REASONING_EFFORT(="high")/get_client() をそのまま
#     再利用する。Fact Ledger収集のcall構造(client.responses.create(model=
#     vfl01.MODEL, reasoning={"effort":...}, tools=[web_search], text=
#     json_schema形式))はer011_news_stage3_new_theme_ledger_trial_09.py
#     272-340行(run_researcher_for_topic)と同型だが、スキーマ・プロンプト
#     文面は本Trial専用に新規作成した最小実装であり、元ファイルは無変更。
#   - er002_ja_web_research_r3(r3): extract_web_search_usage/extract_sources
#     をそのまま再利用する。
#   - er005_cost_logger(cl): install/logging_context をそのまま再利用し、
#     全API callのusage(model実値・token数・web_search_call数)を自動記録
#     する(Production呼び出しコードは一切変更しない、monkeypatch方式)。
#
# サブコマンド: research / source_note / run --arm T0|T1|T2|T3|T4
#   [--step ...] / fact_gate --arm ... / cost
# 冪等性: 出力ファイルが既に存在する場合、--force なしでは再実行しない
# (品質理由のみでの再生成を防ぐガード)。
# ============================================================
from __future__ import annotations

import argparse
import json
import os

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl

THEME_TAG = "NEWS_CORE_IDEA_EDITORIAL_TRIAL_01"
WRITER_MODEL = vfl01.MODEL  # "gpt-5.6-luna" (= routing.WRITER_MODEL)
WRITER_EFFORT = vfl01.REASONING_EFFORT  # "high" (Production Writerと同一値)
# Production Writer呼び出し以外(Research/Source Note/Stage A/Stage B/
# Fact Gate Checker)は、委任文が値統一を義務づけているのはWriter呼び出しの
# みであるため、費用抑制のためSonnetの設計判断として"medium"を使う
# (RESULT_PACKETに明記する)。Research呼び出しのみ、er011のRun structureに
# 忠実な再現を優先しWRITER_EFFORTと同じ値("high")を使う。
NON_WRITER_EFFORT = "medium"

TOPIC_LINE = "老朽化する下水道をめぐり、一部自治体が合併浄化槽への切り替えを検討"
TOPIC_SENTENCE_T3 = (
    "老朽化する下水道をめぐり、一部の自治体が、下水道をやめて各家庭の"
    "合併処理浄化槽へ切り替えることを検討している。"
)

REQUIRED_COVERAGE = """\
【必ずカバーすべき観点(確認できないものはLedgerに入れないこと)】
1. 南伊豆町の事例(何を検討/決定したか、時期)
2. 国(国土交通省・環境省)の下水道→浄化槽転換に関する方針・制度・時期
3. 人口減少と下水道の維持費・更新の関係(数字は出典付きで1〜2件まで)
4. 合併処理浄化槽の仕組み(台所・風呂の排水も処理)
5. 転換・撤去費用への支援の有無
6. 他自治体の検討件数(「32自治体・54区域」という数字は、出典を実際に
   web_searchで確認できた場合のみ含めること。確認できなければこの数字は
   Ledgerに入れないこと)
7. 国会での議論の有無

上記のいずれについても、web_searchで確認できない場合は無理に事実を
作らず、Ledgerに含めないこと。数字・日付は出典に実際に書かれている
とおりに書き、推測で丸めたり補ったりしないこと。"""

FACT_LEDGER_SCHEMA = {
    "name": "sewage_fact_ledger",
    "schema": {
        "type": "object",
        "properties": {
            "facts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "category": {"type": "string"},
                        "claim": {"type": "string"},
                        "date_or_period": {"type": ["string", "null"]},
                        "causal_strength": {
                            "type": "string",
                            "enum": [
                                "OBSERVED_REPORTED",
                                "CORRELATIONAL",
                                "CAUSAL_STATED_BY_SOURCE",
                                "NOT_APPLICABLE",
                            ],
                        },
                        "source_title": {"type": "string"},
                        "source_url": {"type": "string"},
                        "quote": {"type": "string"},
                        "ambiguity": {"type": ["string", "null"]},
                    },
                    "required": [
                        "id", "category", "claim", "date_or_period", "causal_strength",
                        "source_title", "source_url", "quote", "ambiguity",
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

FACT_GATE_SCHEMA = {
    "name": "fact_gate_check",
    "schema": {
        "type": "object",
        "properties": {
            "claims": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "sentence": {"type": "string"},
                        "classification": {
                            "type": "string",
                            "enum": ["SUPPORTED", "COMMON_KNOWLEDGE", "UNSUPPORTED"],
                        },
                        "supporting_fact_ids": {"type": "array", "items": {"type": "string"}},
                        "is_causal_claim": {"type": "boolean"},
                        "causal_support_note": {"type": ["string", "null"]},
                    },
                    "required": [
                        "sentence", "classification", "supporting_fact_ids",
                        "is_causal_claim", "causal_support_note",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["claims"],
        "additionalProperties": False,
    },
    "strict": True,
}

# ------------------------------------------------------------
# Writer Prompt(全文。ユーザー指示により改変禁止。[プレースホルダ]のみ
# 差し込む)
# ------------------------------------------------------------
T0_TEMPLATE = """以下のニュースを、友人に「これ、ちょっと面白くない？」と話すような読み物にしてください。

ニュースの中から、最も意外な事実ではなく、最も面白い「見方」を一つ選んでください。その見方に必要な事実だけを使い、ニュース全体を説明しようとしないでください。

語り口は自然で軽快にします。新聞、行政資料、学校教材のような文章にはしません。難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が、音声で一度聞いて理解できる程度を目安にします。

遠い地域だけの特殊な話に見える場合は、読者の暮らしや、より大きな社会の変化とのつながりを一度だけ示してください。ただし、話を無理に広げる必要はありません。

事実関係は厳守し、架空の出来事や発言は加えません。

テーマ：老朽化する下水道をめぐり、一部自治体が合併浄化槽への切り替えを検討

長さ：800～1000字

出力はタイトルと本文のみ。

[ニュース]
{news}"""

T1_TEMPLATE = """以下のニュースを、友人に「これ、ちょっと面白くない？」と話すような読み物にしてください。

ニュースの中から、最も面白い「見方」を一つ選び、その見方に必要な事実だけを使ってください。

語り口は自然で軽快に。日本語を勉強している外国人が、音声で一度聞いて分かる言葉で。

事実関係は厳守し、架空の出来事や発言は加えません。

長さ：800～1000字

出力はタイトルと本文のみ。

[ニュース]
{news}"""

T4_TEMPLATE = """以下のニュースを、友人に「これ、ちょっと面白くない？」と話すような読み物にしてください。

ニュースの中から、最も意外な事実ではなく、最も面白い「見方」を一つ選んでください。その見方に必要な事実だけを使い、ニュース全体を説明しようとしないでください。その見方が分かった後で、読み手がもう一度「え、そうなの？」となることを一つ、記事の後半に置いてください。

語り口は自然で軽快にします。新聞、行政資料、学校教材のような文章にはしません。難しい内容は、短く簡単な日本語に言い換えてください。日本語を勉強している外国人が、音声で一度聞いて理解できる程度を目安にします。

遠い地域だけの特殊な話に見える場合は、読者の暮らしや、より大きな社会の変化とのつながりを一度だけ示してください。ただし、話を無理に広げる必要はありません。

事実関係は厳守し、架空の出来事や発言は加えません。

テーマ：老朽化する下水道をめぐり、一部自治体が合併浄化槽への切り替えを検討

長さ：800～1000字

出力はタイトルと本文のみ。

[ニュース]
{news}"""

T2_STAGE_A_TEMPLATE = """次のニュース素材を読み、「このニュース、ちょっと面白くない？」と友人に話すときの「見方」を3つ考えてください。
それぞれについて、次の4点を書いてください。
- 見方(1文)
- なぜ面白いか(1〜2文)
- この見方を話すのに本当に必要な事実(素材の番号で2〜4件)
- この見方を受け入れた後、さらに「え、そうなの？」となる展開(1文。素材の事実で支えられるものだけ。番号も添える)
最後に、このテーマに元々興味がない人が最後まで聞きたくなる順に3つを並べ、1位の理由を2文で書いてください。

[ニュース素材]
{source_note}
[事実一覧]
{ledger_numbered}"""

T3_STAGE_A_TEMPLATE = """テーマ：{topic}

このテーマについて、事実を調べる前の段階で、「この話、ちょっと面白くない？」と友人に話せそうな「見方」または「問い」を3つ考えてください。
それぞれについて：
- 見方／問い(1文)
- なぜ面白そうか(1〜2文)
- この見方が本当かどうかを確かめるために調べるべきこと(1〜2点)
最後に、このテーマに元々興味がない人が最後まで聞きたくなる順に並べてください。"""

WRITER_FROM_VIEWPOINT_TEMPLATE = """次の「見方」で、友人に「これ、ちょっと面白くない？」と話すような読み物を書いてください。

見方：{viewpoint}
その先の展開：{expansion}

使ってよい事実：
{facts_prose}

語り口は自然で軽快に。日本語を勉強している外国人が、音声で一度聞いて分かる言葉で。

ここに無い事実や発言は加えません。

長さ：800～1000字

出力はタイトルと本文のみ。"""


# ------------------------------------------------------------
# ヘルパー
# ------------------------------------------------------------
def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def skip_if_exists(path: str, force: bool) -> bool:
    if os.path.exists(path) and not force:
        print(f"[SKIP] 既存出力あり(--forceなし): {path}")
        return True
    return False


def install_logger(out_dir: str) -> None:
    cl.install(out_path(out_dir, "raw_usage_log.jsonl"))


def call_luna(client, developer: str, user: str, schema=None, web_search=False,
              effort=WRITER_EFFORT, stage="", extra_input=None):
    kwargs = dict(
        model=WRITER_MODEL,
        reasoning={"effort": effort},
        input=[
            {"role": "developer", "content": developer},
            {"role": "user", "content": user},
        ],
    )
    if extra_input:
        kwargs["input"].extend(extra_input)
    if schema is not None:
        kwargs["text"] = {"format": {"type": "json_schema", **schema}}
    if web_search:
        kwargs["tools"] = [{"type": "web_search"}]
    with cl.logging_context(THEME_TAG, stage):
        response = client.responses.create(**kwargs)
    return response


def response_meta(response, prompt: str, developer: str, extra: dict = None) -> dict:
    meta = {
        "prompt": prompt,
        "developer_message": developer,
        "model_requested": WRITER_MODEL,
        "response_model_actual": response.model,
        "response_id": response.id,
    }
    usage = getattr(response, "usage", None)
    if usage is not None:
        meta["usage"] = {
            "input_tokens": getattr(usage, "input_tokens", None),
            "output_tokens": getattr(usage, "output_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        }
    search_usage = r3.extract_web_search_usage(response)
    meta["web_search_usage"] = search_usage
    meta["sources"] = r3.extract_sources(response)
    if extra:
        meta.update(extra)
    return meta


def ledger_numbered_text(ledger: dict) -> str:
    lines = []
    for fact in ledger["facts"]:
        lines.append(
            f"{fact['id']}. [{fact['category']}] {fact['claim']}"
            f"(時期: {fact.get('date_or_period') or '不明'}、"
            f"出典: {fact['source_title']} / {fact['source_url']})"
        )
    return "\n".join(lines)


# ------------------------------------------------------------
# research
# ------------------------------------------------------------
# 注(CONT-01、Fable判断によるSTOP解除・上限再定義): --max-searchesは
# 「Sonnetが明示的に発行するweb_search付きresponses.create呼び出し回数」の
# 上限であり、1回のcall内でモデル(gpt-5.6-luna)が自律的に行う内部
# web_search_call数はこの値では制御できない(Responses APIの技術的制約)。
# 本Trialのresearch実行では、明示呼び出し1回に対し内部web_search_callが
# 13回発生した(2026-09-23実測、約¥26)。Fableはこれを「代理指標(回数)」
# ではなく「費用・目的の限定」という本来の趣旨に照らして許容し、Ledger
# (15件、実在一次資料に基づく)を容認した上で続行を指示した
# (docs/pm/delegation_log/NEWS-CORE-IDEA-EDITORIAL-TRIAL-01_CONT-01.md)。
def cmd_research(args):
    out_dir = args.out_dir
    ledger_json_path = out_path(out_dir, "ledger.json")
    if skip_if_exists(ledger_json_path, args.force):
        return
    install_logger(out_dir)
    client = vfl01.get_client()

    developer = (
        "あなたはFact Researcherです。記事本文・比喩・Narrativeは一切書かず、"
        "web_searchツールで実際に確認できた事実だけを、出典URL・出典中の該当箇所の"
        "短い引用(quote)とともに構造化してください。確認できない事項は含めないで"
        "ください。"
    )
    user = f"""今回のテーマについて、Webで調査し、Fact Ledgerを作成してください。

【テーマ】
{TOPIC_LINE}

{REQUIRED_COVERAGE}

各Factについて、id(F1, F2, ...)・category・claim・date_or_period・
causal_strength・source_title・source_url・quote(出典本文からの短い引用、
120字以内)・ambiguity(該当なければnull)を埋めてください。
番号id・出典は必ず全件埋め、quoteは出典に実在する表現の引用にしてください。
10〜15件を目安にしてください。"""

    response = call_luna(
        client, developer, user, schema=FACT_LEDGER_SCHEMA, web_search=True,
        effort=WRITER_EFFORT, stage="research",
    )
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)

    ledger = {"facts": parsed["facts"], "source": "research", "topic": TOPIC_LINE}
    save_json(ledger_json_path, ledger)
    save_json(out_path(out_dir, "research_api_meta.json"), meta)
    save_text(out_path(out_dir, "ledger.md"), ledger_numbered_text(ledger))
    print(f"[OK] research: facts={len(ledger['facts'])} "
          f"web_search_call_count={meta['web_search_usage']['web_search_call_count']} "
          f"model={meta['response_model_actual']}")


# ------------------------------------------------------------
# source_note
# ------------------------------------------------------------
def cmd_source_note(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "source_note.md")
    if skip_if_exists(path, args.force):
        return
    install_logger(out_dir)
    client = vfl01.get_client()
    ledger = load_json(out_path(out_dir, "ledger.json"))

    developer = (
        "あなたはニュース記事の素材(Source Note)を作る編集者です。"
        "与えられた事実一覧だけを使い、中立的な短報を書いてください。"
        "事実一覧にない事実や数字は一切加えないでください。"
    )
    user = f"""以下の事実一覧だけを使って、300〜400字の中立的なニュース素材を
書いてください。新聞の短報のような文体で、番号は付けないでください。
事実一覧にない事実や意見は加えないでください。

【事実一覧】
{ledger_numbered_text(ledger)}"""
    if args.extra_instruction:
        user += f"\n\n【追加指示(前回生成の混入事実を除くため)】\n{args.extra_instruction}"

    response = call_luna(
        client, developer, user, schema=None, web_search=False,
        effort=NON_WRITER_EFFORT, stage="source_note",
    )
    text = response.output_text.strip()
    meta = response_meta(response, user, developer)
    save_text(path, text)
    save_json(out_path(out_dir, "source_note_api_meta.json"), meta)
    print(f"[OK] source_note: {len(text)}字 model={meta['response_model_actual']}")


# ------------------------------------------------------------
# run --arm T0 / T1 / T4 (single-step baseline系)
# ------------------------------------------------------------
def _run_baseline_style(args, template: str):
    out_dir = args.out_dir
    arm_dir = out_path(out_dir, args.arm)
    article_path = out_path(arm_dir, "article.md")
    if skip_if_exists(article_path, args.force):
        return
    install_logger(out_dir)
    client = vfl01.get_client()
    source_note = load_text(out_path(out_dir, "source_note.md")).strip()

    prompt = template.format(news=source_note)
    developer = "あなたは日本語のニュースを分かりやすく面白く伝える書き手です。"
    response = call_luna(
        client, developer, prompt, schema=None, web_search=False,
        effort=WRITER_EFFORT, stage=f"{args.arm}_writer",
    )
    article = response.output_text.strip()
    meta = response_meta(response, prompt, developer, extra={"arm": args.arm})
    save_text(out_path(arm_dir, "prompt.txt"), prompt)
    save_text(article_path, article)
    save_json(out_path(arm_dir, "api_meta.json"), meta)
    body_len = len(article)
    print(f"[OK] {args.arm}: {body_len}字 model={meta['response_model_actual']}")


# ------------------------------------------------------------
# run --arm T2 (--step stageA / writer)
# ------------------------------------------------------------
def _run_t2(args):
    out_dir = args.out_dir
    arm_dir = out_path(out_dir, "T2")
    step = args.step or "stageA"

    if step == "stageA":
        raw_path = out_path(arm_dir, "stage_a_raw.txt")
        if skip_if_exists(raw_path, args.force):
            return
        install_logger(out_dir)
        client = vfl01.get_client()
        ledger = load_json(out_path(out_dir, "ledger.json"))
        source_note = load_text(out_path(out_dir, "source_note.md")).strip()
        prompt = T2_STAGE_A_TEMPLATE.format(
            source_note=source_note, ledger_numbered=ledger_numbered_text(ledger)
        )
        developer = "あなたはニュースの面白い切り口を考える編集者です。"
        response = call_luna(
            client, developer, prompt, schema=None, web_search=False,
            effort=NON_WRITER_EFFORT, stage="T2_stageA",
        )
        text = response.output_text.strip()
        meta = response_meta(response, prompt, developer)
        save_text(out_path(arm_dir, "stage_a_prompt.txt"), prompt)
        save_text(raw_path, text)
        save_json(out_path(arm_dir, "stage_a_api_meta.json"), meta)
        print(f"[OK] T2 stageA: model={meta['response_model_actual']}\n---\n{text}\n---")
        print("[NEXT] Sonnetが手動でcandidates.jsonを作成後、--step writer を実行すること。")
        return

    if step == "writer":
        article_path = out_path(arm_dir, "article.md")
        if skip_if_exists(article_path, args.force):
            return
        candidates = load_json(out_path(arm_dir, "candidates.json"))
        selected = candidates["selected"]
        facts_prose = "\n".join(f"- {t}" for t in selected["facts_prose"])
        prompt = WRITER_FROM_VIEWPOINT_TEMPLATE.format(
            viewpoint=selected["viewpoint"], expansion=selected["expansion"],
            facts_prose=facts_prose,
        )
        install_logger(out_dir)
        client = vfl01.get_client()
        developer = "あなたは日本語のニュースを分かりやすく面白く伝える書き手です。"
        response = call_luna(
            client, developer, prompt, schema=None, web_search=False,
            effort=WRITER_EFFORT, stage="T2_writer",
        )
        article = response.output_text.strip()
        meta = response_meta(response, prompt, developer, extra={"arm": "T2"})
        save_text(out_path(arm_dir, "prompt.txt"), prompt)
        save_text(article_path, article)
        save_json(out_path(arm_dir, "api_meta.json"), meta)
        print(f"[OK] T2 writer: {len(article)}字 model={meta['response_model_actual']}")
        return

    raise SystemExit(f"未知のstep: {step}")


# ------------------------------------------------------------
# run --arm T3 (--step stageA / stageB_search / writer)
# ------------------------------------------------------------
def _run_t3(args):
    out_dir = args.out_dir
    arm_dir = out_path(out_dir, "T3")
    step = args.step or "stageA"

    if step == "stageA":
        raw_path = out_path(arm_dir, "stage_a_raw.txt")
        if skip_if_exists(raw_path, args.force):
            return
        install_logger(out_dir)
        client = vfl01.get_client()
        prompt = T3_STAGE_A_TEMPLATE.format(topic=TOPIC_SENTENCE_T3)
        developer = "あなたはニュースの面白い切り口を考える編集者です。事実調査はまだ行いません。"
        response = call_luna(
            client, developer, prompt, schema=None, web_search=False,
            effort=NON_WRITER_EFFORT, stage="T3_stageA",
        )
        text = response.output_text.strip()
        meta = response_meta(response, prompt, developer)
        save_text(out_path(arm_dir, "stage_a_prompt.txt"), prompt)
        save_text(raw_path, text)
        save_json(out_path(arm_dir, "stage_a_api_meta.json"), meta)
        print(f"[OK] T3 stageA: model={meta['response_model_actual']}\n---\n{text}\n---")
        print("[NEXT] Sonnetが手動でLedgerと突合し、必要ならstageB_searchを実行すること。")
        return

    if step == "stageB_search":
        # 委任のT3最小確認用: Ledgerで支えられない候補をweb_searchで確認する。
        # --query-file にSonnetが用意したprompt文(1件)を指定する。
        n = args.search_index
        result_path = out_path(arm_dir, f"stageB_search_{n}.json")
        if skip_if_exists(result_path, args.force):
            return
        install_logger(out_dir)
        client = vfl01.get_client()
        query_prompt = load_text(args.query_file).strip()
        developer = (
            "あなたはFact Researcherです。指定された1点について、web_searchで"
            "確認できる場合のみ、出典URL・引用・日付とともに回答してください。"
            "確認できない場合は「確認できない」と明記してください。"
        )
        response = call_luna(
            client, developer, query_prompt, schema=None, web_search=True,
            effort=NON_WRITER_EFFORT, stage="T3_stageB_search",
        )
        text = response.output_text.strip()
        meta = response_meta(response, query_prompt, developer)
        save_json(result_path, {"query_prompt": query_prompt, "answer": text, "meta": meta})
        print(f"[OK] T3 stageB_search#{n}: "
              f"web_search_call_count={meta['web_search_usage']['web_search_call_count']}\n"
              f"---\n{text}\n---")
        return

    if step == "stageB_expand":
        # --selected-file にSonnetが用意した{"viewpoint":..., "facts_prose":[...]}を指定
        expansion_path = out_path(arm_dir, "stageB_expansion.json")
        if skip_if_exists(expansion_path, args.force):
            return
        install_logger(out_dir)
        client = vfl01.get_client()
        selected = load_json(args.selected_file)
        facts_prose = "\n".join(f"- {t}" for t in selected["facts_prose"])
        prompt = f"""次の「見方」を受け入れた後、読み手がさらに「え、そうなの？」となる
展開を1文だけ考えてください。以下の事実だけで支えられるものにしてください。

見方：{selected['viewpoint']}

使ってよい事実：
{facts_prose}

出力は展開の1文のみ。"""
        developer = "あなたはニュースの面白い切り口を考える編集者です。"
        response = call_luna(
            client, developer, prompt, schema=None, web_search=False,
            effort=NON_WRITER_EFFORT, stage="T3_stageB_expand",
        )
        text = response.output_text.strip()
        meta = response_meta(response, prompt, developer)
        save_json(expansion_path, {"prompt": prompt, "expansion": text, "meta": meta})
        print(f"[OK] T3 stageB_expand: {text}")
        return

    if step == "writer":
        article_path = out_path(arm_dir, "article.md")
        if skip_if_exists(article_path, args.force):
            return
        stage_b = load_json(out_path(arm_dir, "stage_b.json"))
        selected = stage_b["selected"]
        facts_prose = "\n".join(f"- {t}" for t in selected["facts_prose"])
        prompt = WRITER_FROM_VIEWPOINT_TEMPLATE.format(
            viewpoint=selected["viewpoint"], expansion=selected["expansion"],
            facts_prose=facts_prose,
        )
        install_logger(out_dir)
        client = vfl01.get_client()
        developer = "あなたは日本語のニュースを分かりやすく面白く伝える書き手です。"
        response = call_luna(
            client, developer, prompt, schema=None, web_search=False,
            effort=WRITER_EFFORT, stage="T3_writer",
        )
        article = response.output_text.strip()
        meta = response_meta(response, prompt, developer, extra={"arm": "T3"})
        save_text(out_path(arm_dir, "prompt.txt"), prompt)
        save_text(article_path, article)
        save_json(out_path(arm_dir, "api_meta.json"), meta)
        print(f"[OK] T3 writer: {len(article)}字 model={meta['response_model_actual']}")
        return

    raise SystemExit(f"未知のstep: {step}")


def cmd_run(args):
    if args.arm == "T0":
        _run_baseline_style(args, T0_TEMPLATE)
    elif args.arm == "T1":
        _run_baseline_style(args, T1_TEMPLATE)
    elif args.arm == "T4":
        _run_baseline_style(args, T4_TEMPLATE)
    elif args.arm == "T2":
        _run_t2(args)
    elif args.arm == "T3":
        _run_t3(args)
    else:
        raise SystemExit(f"未知のarm: {args.arm}")


# ------------------------------------------------------------
# fact_gate --arm S|T0|T1|T2|T3|T4
# ------------------------------------------------------------
def _article_text_for_arm(out_dir: str, arm: str) -> str:
    if arm == "S":
        return load_text(out_path(out_dir, "source_note.md")).strip()
    return load_text(out_path(out_dir, arm, "article.md")).strip()


def cmd_fact_gate(args):
    out_dir = args.out_dir
    arm = args.arm
    if arm == "S":
        result_path = out_path(out_dir, "source_note_fact_gate.json")
    else:
        result_path = out_path(out_dir, arm, "fact_gate.json")
    if skip_if_exists(result_path, args.force):
        return

    install_logger(out_dir)
    client = vfl01.get_client()
    ledger = load_json(out_path(out_dir, "ledger.json"))
    ledger_extra_path = out_path(out_dir, "T3", "ledger_extra.json")
    ledger_text = ledger_numbered_text(ledger)
    if arm == "T3" and os.path.exists(ledger_extra_path):
        extra = load_json(ledger_extra_path)
        ledger_text += "\n" + ledger_numbered_text({"facts": extra["facts"]})

    article_text = _article_text_for_arm(out_dir, arm)

    developer = (
        "あなたはFact Checkerです。記事中の事実主張を1文ずつ抽出し、"
        "各主張がFact Ledgerの番号で支えられるか、一般常識か、根拠がないか"
        "(UNSUPPORTED)を判定してください。比喩や感想(例:「変な商売だ」)は"
        "事実主張として扱わないでください。因果関係を述べている文は"
        "is_causal_claimをtrueにし、根拠の有無をcausal_support_noteに"
        "書いてください。"
    )
    user = f"""【Fact Ledger】
{ledger_text}

【判定対象の記事】
{article_text}"""

    response = call_luna(
        client, developer, user, schema=FACT_GATE_SCHEMA, web_search=False,
        effort=NON_WRITER_EFFORT, stage=f"fact_gate_{arm}",
    )
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)
    result = {
        "arm": arm,
        "llm_classification": parsed["claims"],
        "llm_meta": meta,
        "sonnet_manual_review": None,  # Sonnetが手動確認後に追記する
    }
    save_json(result_path, result)
    unsupported = [c for c in parsed["claims"] if c["classification"] == "UNSUPPORTED"]
    causal = [c for c in parsed["claims"] if c["is_causal_claim"]]
    print(f"[OK] fact_gate {arm}: claims={len(parsed['claims'])} "
          f"UNSUPPORTED={len(unsupported)} causal_claims={len(causal)} "
          f"model={meta['response_model_actual']}")
    for c in unsupported:
        print(f"  UNSUPPORTED: {c['sentence']}")
    for c in causal:
        print(f"  CAUSAL: {c['sentence']} | note={c['causal_support_note']}")


# ------------------------------------------------------------
# cost
# ------------------------------------------------------------
USD_TO_JPY = 160


def _load_pricing():
    path = "er005_output/cost_baseline_01/pricing_snapshot.json"
    return json.load(open(path, encoding="utf-8"))["prices"]


def _price(pricing, provider, model, meter):
    for p in pricing:
        if p["provider"] == provider and p["model"] == model and p["meter"] == meter:
            return p["price"]
    return None


def cmd_cost(args):
    out_dir = args.out_dir
    log_path = out_path(out_dir, "raw_usage_log.jsonl")
    pricing = _load_pricing()
    luna_in = _price(pricing, "openai", "gpt-5.6-luna", "input_tokens")
    luna_cached = _price(pricing, "openai", "gpt-5.6-luna", "cached_input_tokens")
    luna_out = _price(pricing, "openai", "gpt-5.6-luna", "output_tokens")
    ws_price_per_1000 = _price(pricing, "openai", "N/A (tool, all models)", "web_search_call")

    entries = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    entries = [e for e in entries if e.get("theme") == THEME_TAG]

    by_stage = {}
    total_usd = 0.0
    total_ws_calls = 0
    total_input = total_output = total_cached = 0
    for e in entries:
        stage = e.get("stage") or "UNKNOWN"
        it = e.get("input_tokens") or 0
        ct = e.get("cached_input_tokens") or 0
        ot = e.get("output_tokens") or 0
        ws = e.get("web_search_call_count") or 0
        billable_in = max(it - ct, 0)
        usd = 0.0
        if luna_in is not None:
            usd += (billable_in / 1_000_000) * luna_in
        if luna_cached is not None:
            usd += (ct / 1_000_000) * luna_cached
        if luna_out is not None:
            usd += (ot / 1_000_000) * luna_out
        if ws_price_per_1000 is not None:
            usd += (ws / 1000) * ws_price_per_1000
        by_stage.setdefault(stage, {"calls": 0, "input_tokens": 0, "cached_input_tokens": 0,
                                     "output_tokens": 0, "web_search_call_count": 0, "usd": 0.0})
        s = by_stage[stage]
        s["calls"] += 1
        s["input_tokens"] += it
        s["cached_input_tokens"] += ct
        s["output_tokens"] += ot
        s["web_search_call_count"] += ws
        s["usd"] += usd
        total_usd += usd
        total_ws_calls += ws
        total_input += it
        total_output += ot
        total_cached += ct

    for s in by_stage.values():
        s["jpy"] = round(s["usd"] * USD_TO_JPY, 2)

    result = {
        "theme": THEME_TAG,
        "by_stage": by_stage,
        "total_calls": len(entries),
        "total_input_tokens": total_input,
        "total_cached_input_tokens": total_cached,
        "total_output_tokens": total_output,
        "total_web_search_call_count": total_ws_calls,
        "total_usd": round(total_usd, 4),
        "total_jpy": round(total_usd * USD_TO_JPY, 2),
        "usd_to_jpy": USD_TO_JPY,
        "pricing_source": "er005_output/cost_baseline_01/pricing_snapshot.json",
    }
    save_json(out_path(out_dir, "cost.json"), result)

    web_search_log = {
        "definition_note": (
            "CONT-01(Fable判断)によりcapの単位を「web_search付き"
            "responses.create明示呼び出し回数」に再定義。内部web_search_call"
            "回数(モデルが1 call内で自律的に行う検索回数)はResponses APIの"
            "技術的制約により呼び出し側から制御できないため、cap対象外・"
            "記録のみ。"
        ),
        "research_explicit_calls": by_stage.get("research", {}).get("calls", 0),
        "research_internal_web_search_call_count": by_stage.get("research", {}).get(
            "web_search_call_count", 0),
        "t3_stageB_search_explicit_calls": by_stage.get("T3_stageB_search", {}).get("calls", 0),
        "t3_stageB_search_internal_web_search_call_count": by_stage.get(
            "T3_stageB_search", {}).get("web_search_call_count", 0),
        "total_internal_web_search_call_count": total_ws_calls,
        "research_explicit_call_cap": 1,
        "t3_stageB_search_explicit_call_cap": 2,
        # 旧定義(内部web_search回数ベース)との互換のため参考値として残す
        "research_web_search_call_count": by_stage.get("research", {}).get("web_search_call_count", 0),
        "t3_stageB_search_web_search_call_count": by_stage.get("T3_stageB_search", {}).get(
            "web_search_call_count", 0),
        "total_web_search_call_count": total_ws_calls,
    }
    save_json(out_path(out_dir, "web_search_log.json"), web_search_log)

    print(f"[OK] cost: total_jpy={result['total_jpy']} total_calls={result['total_calls']} "
          f"total_web_search_call_count={total_ws_calls}")
    for stage, s in sorted(by_stage.items()):
        print(f"  {stage}: calls={s['calls']} jpy={s['jpy']} ws={s['web_search_call_count']}")


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="NEWS-CORE-IDEA-EDITORIAL-TRIAL-01")
    sub = parser.add_subparsers(dest="command", required=True)

    p_research = sub.add_parser("research")
    p_research.add_argument("--out-dir", required=True)
    p_research.add_argument(
        "--max-searches", type=int, default=6,
        help=(
            "[CONT-01で意味を再定義] web_searchツール付きresponses.create "
            "呼び出し(Sonnetが明示的に発行する回数)の上限。1回のcall内で"
            "モデルが自律的に行う内部web_search_call数はこの引数では制御"
            "できない(Responses APIの技術的制約)。内部回数はweb_search_log.json"
            "へ記録するのみで、この上限には含めない。"
        ),
    )
    p_research.add_argument("--force", action="store_true")
    p_research.set_defaults(func=cmd_research)

    p_sn = sub.add_parser("source_note")
    p_sn.add_argument("--out-dir", required=True)
    p_sn.add_argument("--force", action="store_true")
    p_sn.add_argument("--extra-instruction", default=None)
    p_sn.set_defaults(func=cmd_source_note)

    p_run = sub.add_parser("run")
    p_run.add_argument("--arm", required=True, choices=["T0", "T1", "T2", "T3", "T4"])
    p_run.add_argument("--out-dir", required=True)
    p_run.add_argument("--force", action="store_true")
    p_run.add_argument("--step", default=None,
                        help="T2: stageA|writer / T3: stageA|stageB_search|stageB_expand|writer")
    p_run.add_argument(
        "--max-extra-searches", type=int, default=2,
        help=(
            "[CONT-01で意味を再定義] T3 stageB_searchでSonnetが明示的に"
            "発行するweb_search付きresponses.create呼び出しの上限回数"
            "(=stageB_search_<n>.jsonの生成回数上限)。1 call内でモデルが"
            "自律的に行う内部web_search_call数はこの引数では制御できない。"
            "内部回数はweb_search_log.jsonへ記録するのみ。"
        ),
    )
    p_run.add_argument("--query-file", default=None, help="T3 stageB_search用")
    p_run.add_argument("--search-index", type=int, default=1, help="T3 stageB_search用")
    p_run.add_argument("--selected-file", default=None, help="T3 stageB_expand用")
    p_run.set_defaults(func=cmd_run)

    p_fg = sub.add_parser("fact_gate")
    p_fg.add_argument("--arm", required=True, choices=["S", "T0", "T1", "T2", "T3", "T4"])
    p_fg.add_argument("--out-dir", required=True)
    p_fg.add_argument("--force", action="store_true")
    p_fg.set_defaults(func=cmd_fact_gate)

    p_cost = sub.add_parser("cost")
    p_cost.add_argument("--out-dir", required=True)
    p_cost.set_defaults(func=cmd_cost)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
