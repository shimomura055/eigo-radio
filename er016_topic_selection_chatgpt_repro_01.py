# ============================================================
# er016_topic_selection_chatgpt_repro_01.py
# TOPIC-SELECTION-CHATGPT-REPRO-01 (Fable設計、2026-09-24)
# ============================================================
# 目的: ChatGPT(2026-09-23 21:05 JST実行)が得た20候補(Reference Output)と
# 同じ時刻窓・同じ探索思想で、API経由gpt-5.6-lunaが同等品質の20候補を
# 再現できるかのTrial。再現できなければ工程別(検索/選定/Hook/モデル/tool)
# に差分を切り分ける。**Production実装ではない。** Production正式path
# (daily runner・er011_*/er014_*等)は一切変更しない。
#
# 禁止事項(委任文より): Reference Output(20件)をPhase 2(Step A〜E)の
# いかなるPromptにも入れない(模倣防止)。Referenceは Phase 3比較と
# Phase 4診断(a)(b)(c)(d)でのみ使用する。人間・SonnetによるTopic追加・
# 救済・Hook修正・順位差し替えは行わない。
#
# 再利用: er002_ja_web_research_r3(extract_web_search_usage/
# extract_sources)、er005_cost_logger(install/logging_context)、
# er006_model_routing_contract_01(WRITER_MODEL)。
# er016_topic_selection_luna_api_trial_01.pyのパターンを踏襲するが、同ファ
# イルは変更しない(新規ファイルとして作成)。
#
# サブコマンド: audit / probe / discover --sublane 1..8 / select / hooks /
#   verify / final / compare / diag --which a|b|c|d / cost
# 冪等性: 出力ファイルが既に存在する場合、--forceなしでは再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing

load_dotenv()

THEME_TAG = "TOPIC_SELECTION_CHATGPT_REPRO_01"
MODEL_LUNA = routing.WRITER_MODEL  # "gpt-5.6-luna"
MODEL_SOL = "gpt-5.6-sol"
EFFORT_DEFAULT = "medium"
JST = timezone(timedelta(hours=9))
UTC = timezone.utc

WEB_SEARCH_BUDGET = 11  # Phase0(2)+StepA(8)+Phase4a(1) 合計上限

# ------------------------------------------------------------
# サブレーン定義(委任文Phase 2 Step Aより、8サブレーン)
# ------------------------------------------------------------
SUBLANES = {
    1: ("国内一般News", "日本国内News(社会・経済・地域)"),
    2: ("海外一般・国際・経済", "海外一般News・国際・経済"),
    3: ("AI・Technology・Science", "AI・Technology・Science"),
    4: ("Health・睡眠・医療・調査結果", "Health・睡眠・医療・調査結果"),
    5: ("生活・Consumer・Food・コンビニ・新商品・新サービス",
        "生活・Consumer・Food・コンビニ・新商品・新サービス"
        "(PR TIMES等のリリース含む。PRそのものではなく背景に一般化できる"
        "問いがあるかは後工程で判断する)"),
    6: ("Travel・Fashion・Culture・Lifestyle", "Travel・Fashion・Culture・Lifestyle"),
    7: ("Entertainment・Sports・ゲーム・芸能", "Entertainment・Sports・ゲーム・芸能"),
    8: ("SNS・Trend Signal",
        "SNS・Trend Signal(Phase 0で得た2026-09-23話題テーマの実体を"
        "ニュース・記事・商品ページで確認する。Signalの根拠URLと実体URL"
        "を分けて記録する)"),
}
SUBLANE_ALL_TEXT = "\n".join(
    f"- {k}: {v[0]} — {v[1]}" for k, v in SUBLANES.items()
)

PURPOSE_SENTENCE = (
    "English Your Way = 日本人向け英語学習音声番組のNews候補選定Trial。"
    "その時点で世の中に出ている話題をできるだけ広く拾い、その後で"
    "English Your Wayに合うものを厳選します。カテゴリを均等に埋めることが"
    "目的ではありません。"
)

# ------------------------------------------------------------
# Reference Output(ChatGPT 2026-09-23 21:05 JST実行、20候補)
# ** Phase 2(Step A〜E)のいかなるPromptにも使用しない。Phase 3比較・
#    Phase 4診断(a)(b)(c)(d)でのみ使用する。**
# ------------------------------------------------------------
REFERENCE_20 = [
    {"id": 1, "topic_ja": "MetaのAI「Muse」が電話代行の一部を人間スタッフに担当させる実験",
     "hook_ja": "AIに店への電話を頼んだら、裏では人間が話していた？", "type_tags": "AI・身近・逆転"},
    {"id": 2, "topic_ja": "AI企業トップが国連安保理で「AIが人間の制御を超える可能性」を議論",
     "hook_ja": "AIの危険を話し合う場所が、ついに国連安保理になったのはなぜ？", "type_tags": "AI・世界"},
    {"id": 3, "topic_ja": "米中首脳会談でAI・貿易・安全保障が主要テーマに",
     "hook_ja": "アメリカと中国は、なぜAIで\"別々の世界\"を作ろうとしている？", "type_tags": "AI・国際"},
    {"id": 4, "topic_ja": "AIが癌治療を大きく変えるという期待と医師側の慎重論",
     "hook_ja": "AIは本当に\"癌を治す\"ところまで来ている？", "type_tags": "健康・AI"},
    {"id": 5, "topic_ja": "世界初、宇宙飛行中に診断用X線撮影に成功",
     "hook_ja": "宇宙で骨折したら、どうやって病院に行く？", "type_tags": "Science"},
    {"id": 6, "topic_ja": "WHOが避妊方法について新推奨、将来の男性用避妊法にも言及",
     "hook_ja": "避妊は、なぜ今も女性側の負担が大きい？", "type_tags": "健康・社会"},
    {"id": 7, "topic_ja": "日本で「秋になっていびきが増えた」と答える人が多い調査",
     "hook_ja": "秋になると、いびきが増える人がいるのはなぜ？", "type_tags": "健康・生活"},
    {"id": 8, "topic_ja": "日本で「睡眠障害」が診療科名として標榜可能に",
     "hook_ja": "眠れないだけで、病院に行っていいの？", "type_tags": "睡眠・生活"},
    {"id": 9, "topic_ja": "大谷翔平が負傷者リストから約2週間ぶりに復帰予定",
     "hook_ja": "トップ選手は\"完全に治る\"まで待たずに、どう復帰を決める？", "type_tags": "Sports"},
    {"id": 10, "topic_ja": "Threadsで「20年使えるカレンダー」を18年後に見返した投稿が14万回超表示",
     "hook_ja": "20年前の\"未来\"を今見ると、何が一番変わって見える？", "type_tags": "SNS・Nostalgia"},
    {"id": 11, "topic_ja": "ローソンの「おかず1種類だけ」一点突破弁当がSNSで賛否",
     "hook_ja": "おかずが1種類しかない弁当は、\"貧しい\"のか\"合理的\"なのか？", "type_tags": "コンビニ・SNS・俗"},
    {"id": 12, "topic_ja": "無印良品の小型保冷バッグがSNS・口コミで人気",
     "hook_ja": "なぜ今、\"小さい保冷バッグ\"が欲しい人が増えている？", "type_tags": "生活・商品"},
    {"id": 13, "topic_ja": "旅行用の圧縮ポーチが人気",
     "hook_ja": "旅行の荷物は、なぜ毎回バッグいっぱいになる？", "type_tags": "Travel"},
    {"id": 14, "topic_ja": "帝国ホテルの高級感あるエコバッグが話題",
     "hook_ja": "ただのエコバッグに、人はなぜ\"高級感\"を求める？", "type_tags": "Fashion・Consumer"},
    {"id": 15, "topic_ja": "XのAI界隈で「Jev」という意思決定特化型AIが急速に話題化",
     "hook_ja": "AIは\"大きく賢くする\"より、仕事を一つに絞った方が速い？", "type_tags": "SNS・AI"},
    {"id": 16, "topic_ja": "日本香堂が日本の香文化ベースの香水をパリで世界展開",
     "hook_ja": "日本の\"お香\"は、なぜ海外では香水になる？", "type_tags": "Culture"},
    {"id": 17, "topic_ja": "ゲーム『アニモ』スマホ版配信開始、クロスプレイ対応",
     "hook_ja": "ゲームはもう\"どのゲーム機を持っているか\"を気にしなくなる？", "type_tags": "Game・Tech"},
    {"id": 18, "topic_ja": "米倉涼子が映画イベントで「指パッチン」のギネス記録",
     "hook_ja": "\"指パッチン\"にも世界記録がある？", "type_tags": "Entertainment"},
    {"id": 19, "topic_ja": "旅行業界で「安さだけでは選ばれない」消費行動変化を議論",
     "hook_ja": "旅行は安いほどいい――ではなくなっている？", "type_tags": "Travel・Consumer"},
    {"id": 20, "topic_ja": "職場などに人工クラゲ水槽を置くサービス",
     "hook_ja": "オフィスに\"偽物のクラゲ\"を置くと、本当に癒やされる？", "type_tags": "俗・Well-being"},
]

# 汚染検査用のキーワード(各Reference項目の識別性の高い語)
REFERENCE_CONTAMINATION_KEYWORDS = [
    "Muse", "国連安保理", "米中首脳会談", "癌治療", "宇宙飛行中", "診断用X線",
    "WHO", "避妊", "いびき", "睡眠障害", "大谷翔平", "20年使えるカレンダー",
    "ローソン", "一点突破弁当", "無印良品", "保冷バッグ", "圧縮ポーチ",
    "帝国ホテル", "エコバッグ", "Jev", "日本香堂", "アニモ", "米倉涼子",
    "指パッチン", "人工クラゲ",
]


# ------------------------------------------------------------
# ヘルパー
# ------------------------------------------------------------
def out_path(out_dir: str, *parts: str) -> str:
    return os.path.join(out_dir, *parts)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def skip_if_exists(path: str, force: bool) -> bool:
    if os.path.exists(path) and not force:
        print(f"[SKIP] 既存出力あり(--forceなし): {path}")
        return True
    return False


def install_logger(out_dir: str) -> None:
    cl.install(out_path(out_dir, "raw_usage_log.jsonl"))


def get_client():
    from openai import OpenAI
    return OpenAI()


def run_meta_path(out_dir: str) -> str:
    return out_path(out_dir, "run_meta.json")


def load_run_meta(out_dir: str) -> dict:
    path = run_meta_path(out_dir)
    if not os.path.exists(path):
        raise RuntimeError(
            f"run_meta.jsonが見つかりません({path})。先にprobeを実行して"
            "窓(window_start/window_end)を確定してください。"
        )
    return load_json(path)


def log_web_search_call(out_dir: str, stage: str) -> None:
    path = out_path(out_dir, "web_search_log.json")
    entries = []
    if os.path.exists(path):
        entries = load_json(path)
    entries.append({"stage": stage, "logged_at_jst": datetime.now(JST).isoformat()})
    save_json(path, entries)
    print(f"[web_search_log] total_explicit_calls={len(entries)} / budget={WEB_SEARCH_BUDGET}")


def call_model(client, developer: str, user: str, schema=None, web_search=False,
                stage="", model=MODEL_LUNA, effort=EFFORT_DEFAULT, out_dir=None,
                retried=False):
    """1回のAPI技術的retryのみを許可する(品質理由の再実行は禁止)。"""
    kwargs = dict(
        model=model,
        reasoning={"effort": effort},
        input=[
            {"role": "developer", "content": developer},
            {"role": "user", "content": user},
        ],
    )
    if schema is not None:
        kwargs["text"] = {"format": {"type": "json_schema", **schema}}
    if web_search:
        kwargs["tools"] = [{"type": "web_search"}]
    try:
        with cl.logging_context(THEME_TAG, stage):
            response = client.responses.create(**kwargs)
    except Exception as exc:
        if retried:
            raise
        print(f"[RETRY] {stage}: 技術的retry 1回目 ({exc})")
        time.sleep(2)
        return call_model(client, developer, user, schema=schema,
                           web_search=web_search, stage=stage, model=model,
                           effort=effort, out_dir=out_dir, retried=True)
    if response.model != model:
        raise RuntimeError(
            f"STOP条件該当: actual model_idが要求モデルと異なる(stage={stage}, "
            f"requested={model}, actual={response.model})"
        )
    if web_search and out_dir is not None:
        log_web_search_call(out_dir, stage)
    return response


def response_meta(response, prompt: str, developer: str, extra: dict = None) -> dict:
    meta = {
        "prompt": prompt,
        "developer_message": developer,
        "model_requested": response.model,
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


# ------------------------------------------------------------
# audit (Phase 1) — phase1_audit.mdは手動で先に作成済み。存在確認のみ。
# ------------------------------------------------------------
def cmd_audit(args):
    path = out_path(args.out_dir, "phase1_audit.md")
    if not os.path.exists(path):
        raise RuntimeError(
            f"{path} が見つかりません。Phase 1差分表(3列表)をAPI実行前に"
            "作成してください(委任文Phase 1参照)。"
        )
    print(f"[OK] audit: {path} 確認済み(Phase 1差分表はAPI実行前に手動作成済み)。"
          "Phase 0/2へ進んでよい。")


# ------------------------------------------------------------
# probe (Phase 0): 固定窓(2026-09-22 21:05〜2026-09-23 21:05 JST)の
# アーカイブSignal取得可否プローブ。最大2回。
# ------------------------------------------------------------
PROBE_SCHEMA = {
    "name": "archive_signal_probe",
    "schema": {
        "type": "object",
        "properties": {
            "accessible_themes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "theme_name": {"type": "string"},
                        "source_page": {"type": "string"},
                        "evidence_url": {"type": "string"},
                        "time_as_shown": {"type": ["string", "null"]},
                    },
                    "required": ["theme_name", "source_page", "evidence_url",
                                 "time_as_shown"],
                    "additionalProperties": False,
                },
            },
            "inaccessible_sources": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["accessible_themes", "inaccessible_sources"],
        "additionalProperties": False,
    },
    "strict": True,
}


def _probe_prompt(window_start: str, window_end: str, attempt: int) -> str:
    extra = ""
    if attempt == 2:
        extra = (
            "\n\n(1回目の探索で十分な件数が得られませんでした。Google Trends"
            "日本の日次アーカイブ、Yahoo!リアルタイム検索の話題ページの"
            "アーカイブ、Twittrend等の時間別アーカイブ、Togetter/ねとらぼ/"
            "ITmedia等の当日まとめ記事など、より広い種類のアーカイブ的"
            "ページを試してください。)"
        )
    return f"""2026年9月23日(特に夕方〜21時、JST)に日本のSNS/検索で話題
だったテーマを、当時の状況を示すアーカイブページ(Google Trends日本の
日次アーカイブ、Yahoo!リアルタイム検索の話題ページのアーカイブ、
Twittrend等の時間別アーカイブ、Togetter/ねとらぼ/ITmedia等の当日まとめ
記事等)から、実際にアクセスできたものだけ取得してください。

対象窓(JST): {window_start} 〜 {window_end}

各テーマについて、テーマ名(theme_name)・アクセスしたページ名
(source_page)・根拠URL(evidence_url)・そのページに表示されている
時刻表記そのまま(time_as_shown、無ければnull)をJSONで返してください。

実際にアクセスできなかったsource(試みたが失敗した、またはアクセス手段が
無かったもの)は、inaccessible_sourcesにその名前を列挙してください。
推測でテーマを作らないでください。{extra}"""


def cmd_probe(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "phase0_probe.json")
    if skip_if_exists(path, args.force):
        return
    os.makedirs(out_dir, exist_ok=True)
    save_json(run_meta_path(out_dir), {
        "search_index_as_of_jst": datetime.now(JST).isoformat(),
        "window_start_jst": args.window_start,
        "window_end_jst": args.window_end,
        "model": MODEL_LUNA,
        "effort": EFFORT_DEFAULT,
        "note": "window_start/window_endは2026-09-23 21:05 JST基準の固定窓"
                "(実行時刻に連動しない)。search_index_as_of_jstは本Trial"
                "実行時刻(参考、検索インデックスの実態時点)。",
    })
    install_logger(out_dir)
    client = get_client()

    developer = (
        "あなたはTrend/SNS Discoveryの調査担当です。実際にweb_searchツールで"
        "アクセスできたページの情報だけを報告してください。アクセスできな"
        "かった・確認できなかったsourceについて推測で埋めることは禁止です。"
    )

    attempt = 1
    user = _probe_prompt(args.window_start, args.window_end, attempt)
    response = call_model(client, developer, user, schema=PROBE_SCHEMA,
                           web_search=True, stage="phase0_probe_1", out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)
    save_json(out_path(out_dir, "prompts", "phase0_probe_1.json"),
              {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", "phase0_probe_1.json"), meta)

    accessible = parsed["accessible_themes"]
    inaccessible = parsed["inaccessible_sources"]
    calls_made = 1

    if len(accessible) < 10 and args.max_calls >= 2:
        attempt = 2
        user2 = _probe_prompt(args.window_start, args.window_end, attempt)
        response2 = call_model(client, developer, user2, schema=PROBE_SCHEMA,
                                web_search=True, stage="phase0_probe_2", out_dir=out_dir)
        parsed2 = json.loads(response2.output_text)
        meta2 = response_meta(response2, user2, developer)
        save_json(out_path(out_dir, "prompts", "phase0_probe_2.json"),
                  {"developer": developer, "user": user2})
        save_json(out_path(out_dir, "raw_responses", "phase0_probe_2.json"), meta2)
        # 重複除去(evidence_url基準)して結合
        seen = {t["evidence_url"] for t in accessible}
        for t in parsed2["accessible_themes"]:
            if t["evidence_url"] not in seen:
                accessible.append(t)
                seen.add(t["evidence_url"])
        inaccessible = list(set(inaccessible) | set(parsed2["inaccessible_sources"]))
        calls_made = 2

    verdict = "PASS" if len(accessible) >= 10 else "FAIL_SNS_LANE_DEGRADED"
    result = {
        "window_start_jst": args.window_start,
        "window_end_jst": args.window_end,
        "accessible_themes": accessible,
        "inaccessible_sources": inaccessible,
        "accessible_theme_count": len(accessible),
        "verdict": verdict,
        "calls_made": calls_made,
        "note": "verdict=FAIL_SNS_LANE_DEGRADEDの場合でも全体STOPはしない。"
                "Step A サブレーン8(SNS)はSignal取得不可として続行し、"
                "REPORTに制約として明記する(委任文Phase 0)。",
    }
    save_json(path, result)
    print(f"[OK] probe: accessible_theme_count={len(accessible)} verdict={verdict} "
          f"calls_made={calls_made} model={meta['response_model_actual']}")


# ------------------------------------------------------------
# discover (Phase 2 Step A): サブレーン1〜8、各1回
# ------------------------------------------------------------
def _step_a_candidate_schema(sublane: int) -> dict:
    base_props = {
        "title": {"type": "string"},
        "source_name": {"type": "string"},
        "url": {"type": "string"},
        "published_time_as_shown": {"type": ["string", "null"]},
        "published_time_iso": {"type": ["string", "null"]},
        "time_uncertain": {"type": "boolean"},
        "summary_ja": {"type": "string"},
        "sublane": {"type": "integer"},
        "country_scope": {"type": "string"},
        "is_pr_or_ad": {"type": "boolean"},
    }
    base_required = list(base_props.keys())
    if sublane == 8:
        base_props.update({
            "signal_source_url": {"type": ["string", "null"]},
            "signal_time_as_shown": {"type": ["string", "null"]},
            "entity_url": {"type": ["string", "null"]},
        })
        base_required += ["signal_source_url", "signal_time_as_shown", "entity_url"]
    return {
        "type": "object",
        "properties": base_props,
        "required": base_required,
        "additionalProperties": False,
    }


def _step_a_schema(sublane: int) -> dict:
    return {
        "name": f"step_a_discovery_sublane_{sublane}",
        "schema": {
            "type": "object",
            "properties": {
                "candidates": {
                    "type": "array",
                    "items": _step_a_candidate_schema(sublane),
                },
            },
            "required": ["candidates"],
            "additionalProperties": False,
        },
        "strict": True,
    }


def cmd_discover(args):
    out_dir = args.out_dir
    sublane = args.sublane
    path = out_path(out_dir, f"stepA_{sublane}.json")
    if skip_if_exists(path, args.force):
        return
    meta_run = load_run_meta(out_dir)
    install_logger(out_dir)
    client = get_client()

    name, desc = SUBLANES[sublane]
    sns_note = ""
    if sublane == 8:
        probe_path = out_path(out_dir, "phase0_probe.json")
        phase0_themes = []
        if os.path.exists(probe_path):
            phase0_themes = load_json(probe_path).get("accessible_themes", [])
        sns_note = (
            "\n\n【Phase 0で取得済みの2026-09-23話題テーマ(Signal)】\n"
            f"{json.dumps(phase0_themes, ensure_ascii=False, indent=2)}\n\n"
            "このレーンはSNS・Trend Discoveryです。上記Signalは『今、日本人が"
            "何に反応しているか』を見つけるための手がかりであり、Factの出典"
            "ではありません。各テーマについて、実体となるニュース・記事・"
            "商品ページ・出来事を別途web_searchで確認し、実体を確認できた"
            "ものだけ候補にしてください。signal_source_url(Phase 0で得た"
            "根拠URL)、signal_time_as_shown(その時刻表記)、entity_url"
            "(実体を確認できたURL。確認できなければnull、捏造しない)を"
            "分けて記録してください。"
        )

    developer = (
        "あなたはNews Discovery担当です。web_searchツールで実際に見つけた"
        "記事・話題だけを報告してください。存在しない記事やURLを作らない"
        "でください。候補のurlは検索結果の引用に実際に現れたURLのみを"
        "使用し、記憶や推測でURLを組み立てないでください。"
    )
    user = f"""対象窓(JST、固定): {meta_run['window_start_jst']} 〜 {meta_run['window_end_jst']}
この窓に公開・話題化した候補を探してください。検索query・調査の過程で
「2026年9月23日」等の日付語を積極的に使ってください。窓より前や後に
公開された記事は候補にしないでください。公開時刻が確認できない場合は
無理に断定せず、time_uncertain: trueと正直に記してください。

【今回探索するサブレーン】
{sublane}. {name}: {desc}

【全サブレーン一覧(参考、今回はこのサブレーンだけを探索してください)】
{SUBLANE_ALL_TEXT}

【目的】
{PURPOSE_SENTENCE}
{sns_note}

日本語媒体を優先し、英語媒体も含めてください。候補は幅広く、重要度で
絞らないでください。

このサブレーンで、対象窓内に公開・話題化した候補を12〜15件、JSONで
返してください。各候補について、title(原題)・source_name・url
(検索結果の引用に現れたURLのみ)・published_time_as_shown(ページ表示の
時刻表記そのまま)・published_time_iso(推定ISO8601、不明ならnull)・
time_uncertain(bool)・summary_ja(記事内容に基づく2〜3文)・sublane
(整数 {sublane})・country_scope(日本/世界/特定国名など)・is_pr_or_ad
(広告/PR記事らしければtrue)を埋めてください。"""

    response = call_model(client, developer, user, schema=_step_a_schema(sublane),
                           web_search=True, stage=f"stepA_{sublane}", out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)

    save_json(path, {"sublane": sublane, "candidates": parsed["candidates"]})
    save_json(out_path(out_dir, "prompts", f"stepA_{sublane}.json"),
              {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", f"stepA_{sublane}.json"), meta)
    print(f"[OK] discover[sublane={sublane}]: candidates={len(parsed['candidates'])} "
          f"model={meta['response_model_actual']} sources={len(meta['sources'])}")


# ------------------------------------------------------------
# select (Phase 2 Step B): 全候補結合→最大40件選定+dedupe_group
# ------------------------------------------------------------
def _merge_candidates_raw(out_dir: str) -> list:
    """8サブレーンのstepA_<n>.jsonを機械的に結合し、candidate_idを連番で
    付与する。同時にurl_in_citationsをraw_responses/stepA_<n>.jsonの
    sourcesから機械的に判定する(内容の取捨選択は行わない)。"""
    raw_path = out_path(out_dir, "candidates_raw.json")
    if os.path.exists(raw_path):
        return load_json(raw_path)["candidates"]
    merged = []
    cid = 0
    for sublane in range(1, 9):
        lane_path = out_path(out_dir, f"stepA_{sublane}.json")
        if not os.path.exists(lane_path):
            raise RuntimeError(f"stepA_{sublane}.jsonが見つかりません。discover "
                                f"--sublane {sublane} を先に実行してください。")
        lane_data = load_json(lane_path)
        meta_path = out_path(out_dir, "raw_responses", f"stepA_{sublane}.json")
        cited_urls = set()
        if os.path.exists(meta_path):
            meta = load_json(meta_path)
            cited_urls = {s["url"] for s in meta.get("sources", []) if s.get("url")}
        for c in lane_data["candidates"]:
            cid += 1
            c = dict(c)
            c["candidate_id"] = f"C{cid:03d}"
            c["url_in_citations"] = c.get("url") in cited_urls
            merged.append(c)
    save_json(raw_path, {"candidates": merged, "total": len(merged)})
    return merged


STEP_B_SCHEMA = {
    "name": "step_b_selection",
    "schema": {
        "type": "object",
        "properties": {
            "selections": {
                "type": "array",
                "maxItems": 40,
                "items": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {"type": "string"},
                        "dedupe_group": {"type": "string"},
                        "reason_ja": {"type": "string"},
                    },
                    "required": ["candidate_id", "dedupe_group", "reason_ja"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["selections"],
        "additionalProperties": False,
    },
    "strict": True,
}


def cmd_select(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "stepB_selected.json")
    if skip_if_exists(path, args.force):
        return
    raw_candidates = _merge_candidates_raw(out_dir)
    install_logger(out_dir)
    client = get_client()

    compact = [
        {
            "candidate_id": c["candidate_id"],
            "title": c["title"],
            "source_name": c["source_name"],
            "sublane": c["sublane"],
            "summary_ja": c["summary_ja"],
            "published_time_as_shown": c["published_time_as_shown"],
            "time_uncertain": c["time_uncertain"],
            "is_pr_or_ad": c["is_pr_or_ad"],
        }
        for c in raw_candidates
    ]

    developer = (
        "あなたはNews素材の選定担当です。以下の観点だけで『素材として"
        "面白くなり得るか』を判断してください。カテゴリを均等に埋める"
        "ことは目的ではありません。"
    )
    user = f"""以下は今回のStep Aで見つかった全候補です(重複含む)。

【候補一覧】
{json.dumps(compact, ensure_ascii=False, indent=2)}

【選定観点(Step B)】
- 身近に感じられるか
- 純粋に理由を知りたくなるか
- 意外性があるか
- 生活に関係するか
- 人に話したくなるか
- 軽く面白いか
- 大きな世界の変化を示しているか

上記観点で『素材として面白くなり得る』候補を最大40件選んでください。
同一の話題・出来事を指す候補には同じdedupe_group文字列を付け、話題が
異なる候補には異なるdedupe_groupを付けてください(1件だけに絞り込む
必要はありません。同じ話題のグループとして印を付けるだけで構いません)。
各選定についてcandidate_id・dedupe_group・reason_ja(選定理由1文)を
返してください。"""

    response = call_model(client, developer, user, schema=STEP_B_SCHEMA,
                           web_search=False, stage="stepB_select", out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)

    save_json(path, {"selections": parsed["selections"],
                      "selected_count": len(parsed["selections"]),
                      "total_raw": len(raw_candidates)})
    save_json(out_path(out_dir, "prompts", "stepB_select.json"),
              {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", "stepB_select.json"), meta)
    print(f"[OK] select: total_raw={len(raw_candidates)} "
          f"selected={len(parsed['selections'])} model={meta['response_model_actual']}")


# ------------------------------------------------------------
# hooks (Phase 2 Step C): Step B選定分にHook生成
# ------------------------------------------------------------
STEP_C_SCHEMA = {
    "name": "step_c_hooks",
    "schema": {
        "type": "object",
        "properties": {
            "hooks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {"type": "string"},
                        "hook_ja": {"type": "string"},
                        "hook_en": {"type": "string"},
                        "answer_in_source": {"type": "string"},
                        "category": {
                            "type": "string",
                            "enum": ["AI/Tech", "Lifestyle", "Health", "Science",
                                     "Entertainment", "Sports", "Consumer",
                                     "Hard News", "Business/Economy",
                                     "Environment", "Other"],
                        },
                        "distance_to_japan": {
                            "type": "string",
                            "enum": ["近い", "中", "遠い"],
                        },
                        "distance_to_japan_reason": {"type": "string"},
                    },
                    "required": ["candidate_id", "hook_ja", "hook_en",
                                 "answer_in_source", "category",
                                 "distance_to_japan", "distance_to_japan_reason"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["hooks"],
        "additionalProperties": False,
    },
    "strict": True,
}

STEP_C_INSTRUCTION = """【Hookの作り方(Step C)】
元記事のHeadlineをそのまま疑問形にするのではありません。Newsの内容を
一段抽象化・再解釈して、「なぜそれを知りたいのか」をHook化してください。

例1: 台風で街が停電したというNews
  → Hook: 「電気が消えた街では、最初に何が使えなくなる？」
例2: MetaのAIが店への電話代行を行うというNews
  → Hook: 「AIに店への電話を頼んだら、裏では人間が話していた？」

【絶対条件】
(1) 釣りタイトル・誇張を禁止する。
(2) 元記事では答えられない疑問を作らない。
(3) Fact以上の断定をしない。
(4) Hookの問いに対して、元News内容から実質的に答えられる必要がある。
answer_in_sourceには、そのHookに記事内容で実質的に答えられる箇所の要約を
1〜2文で書いてください。記事内容で答えられない場合は、
answer_in_sourceに文字列 "NOT_IN_SOURCE" とだけ書いてください
(「答えは不明」「記事には書いていない」のような曖昧な書き方は禁止です。
答えられないなら明確に"NOT_IN_SOURCE"と書いてください)。"""


def cmd_hooks(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "stepC_hooks.json")
    if skip_if_exists(path, args.force):
        return
    raw_candidates = {c["candidate_id"]: c for c in _merge_candidates_raw(out_dir)}
    selected = load_json(out_path(out_dir, "stepB_selected.json"))["selections"]
    install_logger(out_dir)
    client = get_client()

    compact = []
    for s in selected:
        c = raw_candidates.get(s["candidate_id"])
        if c is None:
            continue
        compact.append({
            "candidate_id": c["candidate_id"],
            "title": c["title"],
            "source_name": c["source_name"],
            "url": c["url"],
            "sublane": c["sublane"],
            "summary_ja": c["summary_ja"],
            "published_time_as_shown": c["published_time_as_shown"],
            "time_uncertain": c["time_uncertain"],
        })

    developer = (
        "あなたはHook Writerです。記事に対応していないHookは禁止です。"
    )
    user = f"""以下はStep Bで選ばれた候補一覧です(candidate_idごとに1件)。
各候補について、日本人ユーザーが一瞬目を止め、聞きたくなるHookを
作成してください。

{STEP_C_INSTRUCTION}

【候補一覧】
{json.dumps(compact, ensure_ascii=False, indent=2)}

各候補(candidate_id)について、hook_ja・hook_en・answer_in_source・
category(AI/Tech・Lifestyle・Health・Science・Entertainment・Sports・
Consumer・Hard News・Business/Economy・Environment・Otherのいずれか)・
distance_to_japan(近い/中/遠いのいずれか)・distance_to_japan_reason
(1文)を埋めてJSONで返してください。全candidate_idについて出力して
ください。"""

    response = call_model(client, developer, user, schema=STEP_C_SCHEMA,
                           web_search=False, stage="stepC_hooks", out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)

    sel_by_id = {s["candidate_id"]: s for s in selected}
    hooks_by_id = {h["candidate_id"]: h for h in parsed["hooks"]}
    enriched = []
    not_covered = []
    for cid, sel in sel_by_id.items():
        raw = raw_candidates.get(cid)
        hook = hooks_by_id.get(cid)
        if raw is None or hook is None:
            not_covered.append(cid)
            continue
        merged = dict(raw)
        merged["dedupe_group"] = sel["dedupe_group"]
        merged["select_reason_ja"] = sel["reason_ja"]
        merged.update(hook)
        enriched.append(merged)

    save_json(path, {"candidates": enriched, "not_covered_candidate_ids": not_covered,
                      "total_selected": len(selected), "total_hooked": len(enriched)})
    save_json(out_path(out_dir, "prompts", "stepC_hooks.json"),
              {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", "stepC_hooks.json"), meta)
    print(f"[OK] hooks: total_selected={len(selected)} hooked={len(enriched)} "
          f"not_covered={len(not_covered)} model={meta['response_model_actual']}")


# ------------------------------------------------------------
# verify (Phase 2 Step D、スクリプトのみ、LLMなし)
# ------------------------------------------------------------
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; EigoRadioTopicReproBot/1.0; "
                  "+research trial, non-production)"
}
HTTP_TIMEOUT = 15


def _fetch(url: str):
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=HTTP_TIMEOUT,
                             allow_redirects=True)
        return resp, None
    except Exception as exc:
        return None, str(exc)[:300]


def _extract_published_time(html: str):
    soup = BeautifulSoup(html, "html.parser")
    for prop in ("article:published_time", "og:article:published_time",
                 "article:published"):
        tag = soup.find("meta", attrs={"property": prop})
        if tag and tag.get("content"):
            return tag["content"], f"meta[property={prop}]"
    for name in ("pubdate", "date", "publish-date", "sailthru.date",
                 "parsely-pub-date"):
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return tag["content"], f"meta[name={name}]"
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
        except Exception:
            continue
        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if not isinstance(item, dict):
                continue
            nodes = item.get("@graph", [item]) if isinstance(item.get("@graph"), list) else [item]
            for node in nodes:
                if isinstance(node, dict) and node.get("datePublished"):
                    return node["datePublished"], "json-ld:datePublished"
    time_tag = soup.find("time", attrs={"datetime": True})
    if time_tag and time_tag.get("datetime"):
        return time_tag["datetime"], "time[datetime]"
    return None, None


def _classify_window(verified_raw: str, window_start_iso: str, window_end_iso: str):
    from dateutil import parser as dtparser
    w_start = dtparser.isoparse(window_start_iso).astimezone(UTC)
    w_end = dtparser.isoparse(window_end_iso).astimezone(UTC)
    try:
        dt = dtparser.parse(verified_raw)
    except Exception:
        return None, None, "unverifiable"
    tz_assumed = False
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
        tz_assumed = True
    dt_utc = dt.astimezone(UTC)
    if w_start <= dt_utc <= w_end:
        return dt_utc.isoformat(), tz_assumed, "within_window"
    return dt_utc.isoformat(), tz_assumed, "outside_window"


def _classify_reachability(url: str):
    resp, err = _fetch(url)
    if err is not None or resp is None:
        return {"status_class": "unreachable_error", "http_status": None, "error": err}
    code = resp.status_code
    if code == 200:
        cls = "ok"
    elif code == 403:
        cls = "forbidden_bot_block"
    elif code == 404:
        cls = "not_found"
    else:
        cls = f"http_error_{code}"
    return {"status_class": cls, "http_status": code, "error": None, "resp": resp}


def cmd_verify(args):
    out_dir = args.out_dir
    suffix = getattr(args, "out_suffix", None)
    fname = f"stepD_verify_{suffix}.json" if suffix else "stepD_verify.json"
    path = out_path(out_dir, fname)
    if skip_if_exists(path, args.force):
        return
    apply_citation_rule = not getattr(args, "no_citation_rule", False)
    hooked = load_json(out_path(out_dir, "stepC_hooks.json"))["candidates"]
    meta_run = load_run_meta(out_dir)
    w_start = meta_run["window_start_jst"]
    w_end = meta_run["window_end_jst"]

    results = []
    for c in hooked:
        url = c["url"]
        reach = _classify_reachability(url)
        entry = {
            "candidate_id": c["candidate_id"],
            "url": url,
            "url_in_citations": c.get("url_in_citations"),
            "http_status": reach["http_status"],
            "status_class": reach["status_class"],
            "fetch_error": reach["error"],
            "answer_in_source": c.get("answer_in_source"),
        }
        window_classification = "unverifiable"
        published_time_verified = None
        verified_source_method = None
        if reach["status_class"] == "ok":
            raw_time, method = _extract_published_time(reach["resp"].text)
            if raw_time is not None:
                verified_iso, tz_assumed, window_classification = _classify_window(
                    raw_time, w_start, w_end)
                published_time_verified = verified_iso
                verified_source_method = method
        entry["published_time_verified"] = published_time_verified
        entry["verified_source_method"] = verified_source_method
        entry["window_classification"] = window_classification

        reasons = []
        if reach["status_class"] == "not_found":
            reasons.append("not_found_404")
        if window_classification == "outside_window":
            reasons.append("outside_window")
        if c.get("answer_in_source") == "NOT_IN_SOURCE":
            reasons.append("answer_not_in_source")
        if apply_citation_rule and c.get("url_in_citations") is False:
            reasons.append("url_not_in_citations")
        entry["disqualified"] = len(reasons) > 0
        entry["disqualify_reasons"] = reasons
        entry["note"] = None
        if reach["status_class"] == "forbidden_bot_block":
            entry["note"] = "到達不能(bot拒否の可能性、403)。失格にはしない。"
        elif window_classification == "unverifiable":
            entry["note"] = ((entry["note"] or "") +
                              " 公開時刻メタ情報を取得できずunverifiable。"
                              "失格にはしない。")
        if not apply_citation_rule and c.get("url_in_citations") is False:
            entry["note"] = ((entry["note"] or "") +
                              " url_in_citations=false(FIX-01: 除外ルール"
                              "撤回のため記録のみ、失格にはしない)。")
        results.append(entry)

    disqualified_count = sum(1 for r in results if r["disqualified"])
    passed = [r["candidate_id"] for r in results if not r["disqualified"]]
    by_id = {c["candidate_id"]: c for c in hooked}
    passed_candidates = []
    for cid in passed:
        merged = dict(by_id[cid])
        v = next(r for r in results if r["candidate_id"] == cid)
        merged["url_in_citations"] = v["url_in_citations"]
        merged["http_status"] = v["http_status"]
        merged["status_class"] = v["status_class"]
        merged["published_time_verified"] = v["published_time_verified"]
        merged["window_classification"] = v["window_classification"]
        passed_candidates.append(merged)

    reason_counts = {}
    for r in results:
        for reason in r["disqualify_reasons"]:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

    save_json(path, {
        "results": results,
        "passed_candidates": passed_candidates,
        "total_checked": len(results),
        "disqualified_count": disqualified_count,
        "passed_count": len(passed_candidates),
        "disqualify_reason_counts": reason_counts,
    })
    print(f"[OK] verify: checked={len(results)} disqualified={disqualified_count} "
          f"passed={len(passed_candidates)} reasons={reason_counts}")


# ------------------------------------------------------------
# final (Phase 2 Step E): Step D通過分から最終20件選定
# ------------------------------------------------------------
STEP_E_SCHEMA = {
    "name": "step_e_final_selection",
    "schema": {
        "type": "object",
        "properties": {
            "selections": {
                "type": "array",
                "maxItems": 20,
                "items": {
                    "type": "object",
                    "properties": {
                        "rank": {"type": "integer"},
                        "candidate_id": {"type": "string"},
                        "selection_reason_ja": {"type": "string"},
                    },
                    "required": ["rank", "candidate_id", "selection_reason_ja"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["selections"],
        "additionalProperties": False,
    },
    "strict": True,
}

STEP_E_CRITERIA = """【最終選定の観点(ユーザー指示§1・§4の要旨)】
- 探索範囲の広さを活かせているか(特定分野に偏りすぎない)
- Topic自体の質(内容が具体的で、裏づけがあるか)
- 多様性(同じような話題ばかりにしない)
- 日本人との距離: 評価すべきは国ではなく、日本人ユーザーが『それ、ちょっと
  知りたい』と思う心理的距離にあるかどうか。特定国の国内事情だけで完結し
  接点が薄い話題は優先度を下げるが、世界的な構図で日本にも波及しうるもの
  は積極的に残してよい。
- 俗っぽさ: 俗っぽい・軽い話題も意図的に含める(政治・戦争・外交Newsばかり
  にしない)
- Hookの質: 一段抽象化・再解釈されたHookになっているか
- 「聞きたくなる」品質: 音声で説明しやすく、人に話したくなるか

【機械的制約】
- dedupe_groupが同じ候補は1件だけ選んでください。
- Hookの文言(hook_ja/hook_en)は書き換えないでください(Step Cのものを
  そのまま使います。この工程ではrank・candidate_id・selection_reason_ja
  のみを決めてください)。"""


def cmd_final(args):
    out_dir = args.out_dir
    out_suffix = getattr(args, "out_suffix", None)
    in_suffix = getattr(args, "in_suffix", None)
    out_fname = f"stepE_final_{out_suffix}.json" if out_suffix else "stepE_final.json"
    in_fname = f"stepD_verify_{in_suffix}.json" if in_suffix else "stepD_verify.json"
    path = out_path(out_dir, out_fname)
    if skip_if_exists(path, args.force):
        return
    passed = load_json(out_path(out_dir, in_fname))["passed_candidates"]
    install_logger(out_dir)
    client = get_client()
    stage = f"stepE_final_{out_suffix}" if out_suffix else "stepE_final"
    prompt_fname = f"stepE_final_{out_suffix}.json" if out_suffix else "stepE_final.json"

    compact = [
        {
            "candidate_id": c["candidate_id"],
            "title": c["title"],
            "source_name": c["source_name"],
            "sublane": c["sublane"],
            "summary_ja": c["summary_ja"],
            "hook_ja": c["hook_ja"],
            "hook_en": c["hook_en"],
            "category": c["category"],
            "distance_to_japan": c["distance_to_japan"],
            "distance_to_japan_reason": c["distance_to_japan_reason"],
            "dedupe_group": c["dedupe_group"],
            "is_pr_or_ad": c["is_pr_or_ad"],
            "country_scope": c["country_scope"],
            "window_classification": c["window_classification"],
        }
        for c in passed
    ]

    developer = (
        "あなたはFinal Editorです。以下の条件をすべて守って最大20件を"
        "順位付きで選んでください。20件に満たない場合は無理に埋めず、"
        "実際に選べる数だけ返してください。"
    )
    user = f"""以下はStep D(整合・実在検証)を通過した候補のHook付き情報です。

{STEP_E_CRITERIA}

【候補一覧】
{json.dumps(compact, ensure_ascii=False, indent=2)}

上記観点に基づき、最大20件をrank(1が最上位)付きで選び、各選定について
candidate_id・selection_reason_ja(2〜3文)を返してください。"""

    response = call_model(client, developer, user, schema=STEP_E_SCHEMA,
                           web_search=False, stage=stage, out_dir=out_dir)
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)

    selections = sorted(parsed["selections"], key=lambda s: s["rank"])
    by_id = {c["candidate_id"]: c for c in passed}
    resolved = []
    unresolved_ids = []
    for s in selections:
        c = by_id.get(s["candidate_id"])
        if c is None:
            unresolved_ids.append(s["candidate_id"])
            continue
        merged = dict(c)
        merged["rank"] = s["rank"]
        merged["selection_reason_ja"] = s["selection_reason_ja"]
        resolved.append(merged)

    save_json(path, {
        "selections_raw": selections,
        "resolved": resolved,
        "unresolved_candidate_ids": unresolved_ids,
        "selected_count": len(resolved),
    })
    save_json(out_path(out_dir, "prompts", prompt_fname),
              {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", prompt_fname), meta)
    print(f"[OK] final: selected_count={len(resolved)} "
          f"unresolved={len(unresolved_ids)} model={meta['response_model_actual']}")


# ------------------------------------------------------------
# compare (Phase 3): 汚染検査+Hook形式判定+分布+プール内包含
# ------------------------------------------------------------
NOUN_TOKEN_RE = re.compile(r"[一-龥ァ-ヶA-Za-z0-9]{2,}")


def _tokenize_noun_like(text: str) -> set:
    return set(NOUN_TOKEN_RE.findall(text or ""))


def classify_hook_format(source_title: str, hook_ja: str) -> dict:
    """委任文Phase 3の定義: 元titleとの共通名詞率>50%かつ文末「でしょうか」
    → 疑問文化。それ以外は一段抽象化・再解釈、と判定する(閾値・方式を
    出力に残す)。"""
    title_tokens = _tokenize_noun_like(source_title)
    hook_tokens = _tokenize_noun_like(hook_ja)
    if not title_tokens:
        common_ratio = 0.0
    else:
        common_ratio = len(title_tokens & hook_tokens) / len(title_tokens)
    ends_with_deshouka = bool(re.search(r"でしょうか[？?]?\s*$", (hook_ja or "").strip()))
    is_question_ification = common_ratio > 0.5 and ends_with_deshouka
    return {
        "common_noun_ratio": round(common_ratio, 3),
        "ends_with_deshouka": ends_with_deshouka,
        "classification": "question_ification" if is_question_ification else "reinterpretation",
        "method": "NOUN_TOKEN_RE=[一-龥ァ-ヶA-Za-z0-9]{2,}で抽出したトークン集合の"
                  "Jaccard分子(共通トークン数/元titleトークン数)>0.5、かつ"
                  "hook_jaが「でしょうか」で終わる場合のみquestion_ification、"
                  "それ以外はreinterpretation。",
    }


def check_reference_contamination(out_dir: str) -> dict:
    """Phase 2(Step A〜E)のprompts/配下ファイルにReferenceの識別語が
    含まれていないかを機械的に検査する。"""
    phase2_prefixes = ("stepA_", "stepB_", "stepC_", "stepE_")
    prompts_dir = out_path(out_dir, "prompts")
    checked_files = []
    hits = []
    if os.path.exists(prompts_dir):
        for fname in sorted(os.listdir(prompts_dir)):
            if not fname.startswith(phase2_prefixes):
                continue
            fpath = os.path.join(prompts_dir, fname)
            with open(fpath, encoding="utf-8") as f:
                content = f.read()
            checked_files.append(fname)
            for kw in REFERENCE_CONTAMINATION_KEYWORDS:
                if kw in content:
                    hits.append({"file": fname, "keyword": kw})
    return {
        "checked_files": checked_files,
        "contamination_hits": hits,
        "contaminated": len(hits) > 0,
    }


def cmd_compare(args):
    out_dir = args.out_dir
    out_suffix = getattr(args, "out_suffix", None)
    in_suffix = getattr(args, "in_suffix", None)
    out_fname = f"phase3_compare_{out_suffix}.json" if out_suffix else "phase3_compare.json"
    in_fname = f"stepE_final_{in_suffix}.json" if in_suffix else "stepE_final.json"
    path = out_path(out_dir, out_fname)
    if skip_if_exists(path, args.force):
        return
    final = load_json(out_path(out_dir, in_fname))["resolved"]
    raw_pool = load_json(out_path(out_dir, "candidates_raw.json"))["candidates"]

    contamination = check_reference_contamination(out_dir)

    luna_hook_format = [
        {
            "candidate_id": c["candidate_id"],
            "title": c["title"],
            "hook_ja": c["hook_ja"],
            **classify_hook_format(c["title"], c["hook_ja"]),
        }
        for c in final
    ]
    reference_hook_format = [
        {
            "reference_id": r["id"],
            "topic_ja": r["topic_ja"],
            "hook_ja": r["hook_ja"],
            **classify_hook_format(r["topic_ja"], r["hook_ja"]),
        }
        for r in REFERENCE_20
    ]

    category_dist = {}
    distance_dist = {}
    for c in final:
        category_dist[c["category"]] = category_dist.get(c["category"], 0) + 1
        distance_dist[c["distance_to_japan"]] = distance_dist.get(c["distance_to_japan"], 0) + 1

    light_categories = {"Consumer", "Entertainment", "Other"}
    light_keywords = ["コンビニ", "SNS", "話題", "商品", "グッズ"]
    luna_light_count = sum(
        1 for c in final
        if c["category"] in light_categories
        or any(kw in c["summary_ja"] for kw in light_keywords)
    )
    reference_light_keywords = ["俗", "SNS", "コンビニ"]
    reference_light_count = sum(
        1 for r in REFERENCE_20
        if any(kw in r["type_tags"] for kw in reference_light_keywords)
    )

    pool_inclusion = []
    for r in REFERENCE_20:
        ref_tokens = _tokenize_noun_like(r["topic_ja"])
        matched = None
        best_overlap = 0
        for c in raw_pool:
            cand_text = (c.get("title", "") or "") + " " + (c.get("summary_ja", "") or "")
            cand_tokens = _tokenize_noun_like(cand_text)
            if not ref_tokens:
                continue
            overlap = len(ref_tokens & cand_tokens) / len(ref_tokens)
            if overlap > best_overlap:
                best_overlap = overlap
                matched = c
        pool_inclusion.append({
            "reference_id": r["id"],
            "topic_ja": r["topic_ja"],
            "best_overlap_ratio": round(best_overlap, 3),
            "found_in_pool_heuristic": best_overlap > 0.3,
            "matched_candidate_id": matched["candidate_id"] if matched and best_overlap > 0.3 else None,
            "matched_title": matched["title"] if matched and best_overlap > 0.3 else None,
        })

    result = {
        "contamination_check": contamination,
        "luna_hook_format": luna_hook_format,
        "reference_hook_format": reference_hook_format,
        "luna_category_distribution": category_dist,
        "luna_distance_distribution": distance_dist,
        "luna_light_topic_count": luna_light_count,
        "reference_light_topic_count_by_type_tag_keyword": reference_light_count,
        "reference_distance_note": "Referenceには距離ラベルが無いため、Sonnetによる"
                                    "代替ラベル付けは行わない(不明のまま記録)。",
        "reference_source_note": "Referenceにはsource媒体情報が無いため、国内媒体"
                                  "比率の直接比較はできない(不明のまま記録)。",
        "step_a_pool_inclusion_heuristic": pool_inclusion,
        "pool_inclusion_method": "reference topic_jaとcandidates_raw各件のtitle+"
                                  "summary_jaのnoun-likeトークン重複率(reference側"
                                  "トークン数分の分母)が0.3超の場合found_in_poolと"
                                  "する簡易ヒューリスティック。",
    }
    save_json(path, result)
    print(f"[OK] compare: contaminated={contamination['contaminated']} "
          f"luna_final_count={len(final)} pool_size={len(raw_pool)}")


# ------------------------------------------------------------
# diag (Phase 4): a/b/c/d
# ------------------------------------------------------------
DIAG_A_SCHEMA = {
    "name": "diag_a_reference_findability",
    "schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "reference_id": {"type": "integer"},
                        "found": {"type": "boolean"},
                        "url": {"type": ["string", "null"]},
                        "published_time_as_shown": {"type": ["string", "null"]},
                        "notes": {"type": "string"},
                    },
                    "required": ["reference_id", "found", "url",
                                 "published_time_as_shown", "notes"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["results"],
        "additionalProperties": False,
    },
    "strict": True,
}


def cmd_diag_a(args, client, out_dir):
    path = out_path(out_dir, "phase4_diag_a.json")
    if skip_if_exists(path, args.force):
        return
    items = [{"reference_id": r["id"], "topic_ja": r["topic_ja"]} for r in REFERENCE_20]
    developer = (
        "あなたはNews検索の診断担当です。実際にweb_searchで見つかった"
        "ページの情報だけを報告してください。見つからなければfound:false"
        "とし、urlを作らないでください。"
    )
    user = f"""以下20件のNews素材それぞれについて、2026年9月22日〜23日に
公開された元記事・実体ページをweb_searchで見つけられるか探してください。

【素材一覧】
{json.dumps(items, ensure_ascii=False, indent=2)}

各reference_idについて、found(bool)・url(見つかった場合のみ、実際の
検索結果引用URL)・published_time_as_shown(ページ表示の時刻表記)・
notes(検索の様子や見つからなかった場合の状況、1文)をJSONで返して
ください。全reference_idについて出力してください。"""

    response = call_model(client, developer, user, schema=DIAG_A_SCHEMA,
                           web_search=True, stage="phase4_diag_a", out_dir=out_dir,
                           model=MODEL_LUNA, effort=EFFORT_DEFAULT)
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)
    save_json(path, parsed)
    save_json(out_path(out_dir, "prompts", "phase4_diag_a.json"),
              {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", "phase4_diag_a.json"), meta)
    found_count = sum(1 for r in parsed["results"] if r["found"])
    print(f"[OK] diag_a: found={found_count}/20 model={meta['response_model_actual']}")


DIAG_BCD_SCHEMA = {
    "name": "diag_bcd_hooks",
    "schema": {
        "type": "object",
        "properties": {
            "hooks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "reference_id": {"type": "integer"},
                        "hook_ja": {"type": "string"},
                        "hook_en": {"type": "string"},
                    },
                    "required": ["reference_id", "hook_ja", "hook_en"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["hooks"],
        "additionalProperties": False,
    },
    "strict": True,
}


def _diag_bcd_prompt():
    items = [{"reference_id": r["id"], "topic_ja": r["topic_ja"]} for r in REFERENCE_20]
    developer = "あなたはHook Writerです。記事に対応していないHookは禁止です。"
    user = f"""以下はNews素材一覧です(Hookは付いていません)。各素材について、
日本人ユーザーが一瞬目を止め、聞きたくなるHookを作成してください。

{STEP_C_INSTRUCTION}

【素材一覧】
{json.dumps(items, ensure_ascii=False, indent=2)}

各reference_idについて、hook_ja・hook_enを埋めてJSONで返してください。
全reference_idについて出力してください。"""
    return developer, user


def cmd_diag_b(args, client, out_dir):
    path = out_path(out_dir, "phase4_diag_b.json")
    if skip_if_exists(path, args.force):
        return
    developer, user = _diag_bcd_prompt()
    response = call_model(client, developer, user, schema=DIAG_BCD_SCHEMA,
                           web_search=False, stage="phase4_diag_b", out_dir=out_dir,
                           model=MODEL_LUNA, effort=EFFORT_DEFAULT)
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)

    by_ref = {r["id"]: r for r in REFERENCE_20}
    formatted = []
    question_ification_count = 0
    for h in parsed["hooks"]:
        ref = by_ref.get(h["reference_id"], {})
        fmt = classify_hook_format(ref.get("topic_ja", ""), h["hook_ja"])
        if fmt["classification"] == "question_ification":
            question_ification_count += 1
        formatted.append({**h, "reference_topic_ja": ref.get("topic_ja"),
                           "reference_hook_ja": ref.get("hook_ja"), **fmt})
    majority_question_ification = question_ification_count > len(parsed["hooks"]) / 2

    save_json(path, {"hooks": formatted, "model": meta["response_model_actual"],
                      "effort": EFFORT_DEFAULT,
                      "question_ification_count": question_ification_count,
                      "total": len(parsed["hooks"]),
                      "majority_question_ification": majority_question_ification})
    save_json(out_path(out_dir, "prompts", "phase4_diag_b.json"),
              {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", "phase4_diag_b.json"), meta)
    print(f"[OK] diag_b: question_ification={question_ification_count}/"
          f"{len(parsed['hooks'])} majority={majority_question_ification} "
          f"model={meta['response_model_actual']}")


def cmd_diag_c(args, client, out_dir):
    path = out_path(out_dir, "phase4_diag_c.json")
    if skip_if_exists(path, args.force):
        return
    diag_b_path = out_path(out_dir, "phase4_diag_b.json")
    if not os.path.exists(diag_b_path):
        raise RuntimeError("phase4_diag_b.jsonが見つかりません。diag --which b を"
                            "先に実行してください。")
    diag_b = load_json(diag_b_path)
    if not diag_b.get("majority_question_ification"):
        save_json(path, {
            "executed": False,
            "reason": "phase4_diag_bのquestion_ification判定が過半数でなかった"
                      "ため、条件(委任文Phase 4(c))を満たさず未実施。",
        })
        print("[SKIP] diag_c: 条件未達(majority_question_ification=false)のため未実施")
        return

    pricing = load_json("er005_output/cost_baseline_01/pricing_snapshot.json")["prices"]
    has_sol_price = any(p["provider"] == "openai" and p["model"] == MODEL_SOL
                         for p in pricing)
    if not has_sol_price:
        save_json(path, {"executed": False,
                          "reason": f"{MODEL_SOL}の単価情報がpricing_snapshot.jsonに無い。"})
        print(f"[SKIP] diag_c: {MODEL_SOL}価格情報なし")
        return

    developer, user = _diag_bcd_prompt()
    try:
        response = call_model(client, developer, user, schema=DIAG_BCD_SCHEMA,
                               web_search=False, stage="phase4_diag_c", out_dir=out_dir,
                               model=MODEL_SOL, effort=EFFORT_DEFAULT)
    except Exception as exc:
        save_json(path, {"executed": False, "reason": f"API呼び出し失敗: {exc}"})
        print(f"[SKIP] diag_c: API呼び出し失敗 ({exc})")
        return
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)
    by_ref = {r["id"]: r for r in REFERENCE_20}
    formatted = []
    for h in parsed["hooks"]:
        ref = by_ref.get(h["reference_id"], {})
        fmt = classify_hook_format(ref.get("topic_ja", ""), h["hook_ja"])
        formatted.append({**h, "reference_topic_ja": ref.get("topic_ja"),
                           "reference_hook_ja": ref.get("hook_ja"), **fmt})
    save_json(path, {"executed": True, "hooks": formatted,
                      "model": meta["response_model_actual"], "effort": EFFORT_DEFAULT})
    save_json(out_path(out_dir, "prompts", "phase4_diag_c.json"),
              {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", "phase4_diag_c.json"), meta)
    print(f"[OK] diag_c: model={meta['response_model_actual']}")


def cmd_diag_d(args, client, out_dir):
    path = out_path(out_dir, "phase4_diag_d.json")
    if skip_if_exists(path, args.force):
        return
    developer, user = _diag_bcd_prompt()
    response = call_model(client, developer, user, schema=DIAG_BCD_SCHEMA,
                           web_search=False, stage="phase4_diag_d", out_dir=out_dir,
                           model=MODEL_LUNA, effort="high")
    parsed = json.loads(response.output_text)
    meta = response_meta(response, user, developer)
    by_ref = {r["id"]: r for r in REFERENCE_20}
    formatted = []
    for h in parsed["hooks"]:
        ref = by_ref.get(h["reference_id"], {})
        fmt = classify_hook_format(ref.get("topic_ja", ""), h["hook_ja"])
        formatted.append({**h, "reference_topic_ja": ref.get("topic_ja"),
                           "reference_hook_ja": ref.get("hook_ja"), **fmt})
    save_json(path, {"hooks": formatted, "model": meta["response_model_actual"],
                      "effort": "high"})
    save_json(out_path(out_dir, "prompts", "phase4_diag_d.json"),
              {"developer": developer, "user": user})
    save_json(out_path(out_dir, "raw_responses", "phase4_diag_d.json"), meta)
    print(f"[OK] diag_d: model={meta['response_model_actual']} effort=high")


def cmd_diag(args):
    out_dir = args.out_dir
    install_logger(out_dir)
    client = get_client()
    which = args.which
    if which == "a":
        cmd_diag_a(args, client, out_dir)
    elif which == "b":
        cmd_diag_b(args, client, out_dir)
    elif which == "c":
        cmd_diag_c(args, client, out_dir)
    elif which == "d":
        cmd_diag_d(args, client, out_dir)
    else:
        raise ValueError(f"unknown --which: {which}")


# ------------------------------------------------------------
# cost
# ------------------------------------------------------------
def _price(pricing, provider, model, meter):
    return next(p["price"] for p in pricing
                if p["provider"] == provider and p["model"] == model
                and p["meter"] == meter)


def cmd_cost(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "cost.json")
    if skip_if_exists(path, args.force):
        return
    pricing = load_json("er005_output/cost_baseline_01/pricing_snapshot.json")["prices"]
    usd_to_jpy = 160
    ws_price = _price(pricing, "openai", "N/A (tool, all models)", "web_search_call")

    def model_prices(model_name):
        return (
            _price(pricing, "openai", model_name, "input_tokens"),
            _price(pricing, "openai", model_name, "cached_input_tokens"),
            _price(pricing, "openai", model_name, "output_tokens"),
        )

    price_cache = {}

    log_path = out_path(out_dir, "raw_usage_log.jsonl")
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
    total_calls = 0
    total_ws_calls = 0
    for e in entries:
        if e.get("provider") != "openai" or not e.get("success", True):
            continue
        stage = e.get("stage") or "unknown"
        model_name = e.get("model") or MODEL_LUNA
        if model_name not in price_cache:
            try:
                price_cache[model_name] = model_prices(model_name)
            except StopIteration:
                price_cache[model_name] = model_prices(MODEL_LUNA)
        p_in, p_cached, p_out = price_cache[model_name]
        it = e.get("input_tokens") or 0
        ct = e.get("cached_input_tokens") or 0
        ot = e.get("output_tokens") or 0
        ws = e.get("web_search_call_count") or 0
        billable_in = max(it - ct, 0)
        usd = (billable_in / 1_000_000) * p_in + (ct / 1_000_000) * p_cached \
            + (ot / 1_000_000) * p_out + (ws / 1000) * ws_price
        s = by_stage.setdefault(stage, {"calls": 0, "input_tokens": 0,
                                         "cached_input_tokens": 0, "output_tokens": 0,
                                         "web_search_call_count": 0, "usd": 0.0,
                                         "model": model_name})
        s["calls"] += 1
        s["input_tokens"] += it
        s["cached_input_tokens"] += ct
        s["output_tokens"] += ot
        s["web_search_call_count"] += ws
        s["usd"] += usd
        total_usd += usd
        total_calls += 1
        total_ws_calls += ws

    ws_log_path = out_path(out_dir, "web_search_log.json")
    explicit_ws_calls = len(load_json(ws_log_path)) if os.path.exists(ws_log_path) else 0

    by_stage_jpy = {
        stage: {**vals, "jpy": round(vals["usd"] * usd_to_jpy, 1)}
        for stage, vals in by_stage.items()
    }
    result = {
        "by_stage": by_stage_jpy,
        "total_usd": round(total_usd, 4),
        "total_jpy": round(total_usd * usd_to_jpy, 1),
        "total_openai_calls": total_calls,
        "total_internal_web_search_call_count": total_ws_calls,
        "explicit_web_search_call_count": explicit_ws_calls,
        "explicit_web_search_budget": WEB_SEARCH_BUDGET,
        "explicit_web_search_within_budget": explicit_ws_calls <= WEB_SEARCH_BUDGET,
        "usd_to_jpy": usd_to_jpy,
        "cost_ceiling_jpy": 400,
        "within_cost_ceiling": round(total_usd * usd_to_jpy, 1) <= 400,
    }
    save_json(path, result)
    print(f"[OK] cost: total_jpy={result['total_jpy']} calls={total_calls} "
          f"explicit_ws={explicit_ws_calls}/{WEB_SEARCH_BUDGET} "
          f"within_ceiling={result['within_cost_ceiling']}")


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_audit = sub.add_parser("audit")
    p_audit.add_argument("--out-dir", required=True)
    p_audit.set_defaults(func=cmd_audit)

    p_probe = sub.add_parser("probe")
    p_probe.add_argument("--out-dir", required=True)
    p_probe.add_argument("--max-calls", type=int, default=2)
    p_probe.add_argument("--window-start", required=True)
    p_probe.add_argument("--window-end", required=True)
    p_probe.add_argument("--force", action="store_true")
    p_probe.set_defaults(func=cmd_probe)

    p_discover = sub.add_parser("discover")
    p_discover.add_argument("--out-dir", required=True)
    p_discover.add_argument("--sublane", required=True, type=int, choices=list(range(1, 9)))
    p_discover.add_argument("--window-start", required=False)
    p_discover.add_argument("--window-end", required=False)
    p_discover.add_argument("--force", action="store_true")
    p_discover.set_defaults(func=cmd_discover)

    p_select = sub.add_parser("select")
    p_select.add_argument("--out-dir", required=True)
    p_select.add_argument("--force", action="store_true")
    p_select.set_defaults(func=cmd_select)

    p_hooks = sub.add_parser("hooks")
    p_hooks.add_argument("--out-dir", required=True)
    p_hooks.add_argument("--force", action="store_true")
    p_hooks.set_defaults(func=cmd_hooks)

    p_verify = sub.add_parser("verify")
    p_verify.add_argument("--out-dir", required=True)
    p_verify.add_argument("--force", action="store_true")
    p_verify.add_argument("--out-suffix", default=None,
                           help="出力ファイル名に付与するsuffix(例: fix01)。"
                                "指定時は既存stepD_verify.jsonを上書きしない。")
    p_verify.add_argument("--no-citation-rule", action="store_true",
                           help="FIX-01: url_in_citations=falseによる失格"
                                "ルールを適用しない(値は記録のみ残す)。")
    p_verify.set_defaults(func=cmd_verify)

    p_final = sub.add_parser("final")
    p_final.add_argument("--out-dir", required=True)
    p_final.add_argument("--force", action="store_true")
    p_final.add_argument("--out-suffix", default=None)
    p_final.add_argument("--in-suffix", default=None,
                          help="入力stepD_verify_<suffix>.jsonのsuffix")
    p_final.set_defaults(func=cmd_final)

    p_compare = sub.add_parser("compare")
    p_compare.add_argument("--out-dir", required=True)
    p_compare.add_argument("--force", action="store_true")
    p_compare.add_argument("--out-suffix", default=None)
    p_compare.add_argument("--in-suffix", default=None,
                            help="入力stepE_final_<suffix>.jsonのsuffix")
    p_compare.set_defaults(func=cmd_compare)

    p_diag = sub.add_parser("diag")
    p_diag.add_argument("--out-dir", required=True)
    p_diag.add_argument("--which", required=True, choices=["a", "b", "c", "d"])
    p_diag.add_argument("--force", action="store_true")
    p_diag.set_defaults(func=cmd_diag)

    p_cost = sub.add_parser("cost")
    p_cost.add_argument("--out-dir", required=True)
    p_cost.add_argument("--force", action="store_true")
    p_cost.set_defaults(func=cmd_cost)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
