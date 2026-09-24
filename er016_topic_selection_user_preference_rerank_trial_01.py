# ============================================================
# er016_topic_selection_user_preference_rerank_trial_01.py
# TOPIC-SELECTION-USER-PREFERENCE-RERANK-TRIAL-01 (Fable設計、2026-09-24)
# ============================================================
# 目的: ユーザーの実評価済みTeacher Data(57件、点数+Topic+Hook)を
# few-shot/preference examplesとして直接モデルへ渡し、同一Candidate Pool
# をLuna/Terra/Sol/Jevがユーザー嗜好に沿って順位付けできるかを比較する
# Trial。Production実装ではない。Production正式path(daily runner等)は
# 一切変更しない。
#
# 禁止事項: Teacher Dataを抽象Ruleへ圧縮すること/モデルごとにPrompt条件
# を変えること/既知評価TopicのCandidate Pool混入/Jev API keyの表示・
# log保存・commit・report記載(環境変数JEV_API_KEYを参照するのみ)。
#
# 再利用: er002_ja_web_research_r3(extract_web_search_usage/
# extract_sources)、er005_cost_logger(install/logging_context)、
# er006_model_routing_contract_01(WRITER_MODEL)。
# er016_topic_selection_chatgpt_repro_01.pyはimportのみ
# (REFERENCE_CONTAMINATION_KEYWORDS)。既存script(search_trial_03/
# reference_process_trial_01/chatgpt_repro_01/chatgpt_repro_01_cont02)は
# 一切変更しない(出力ファイルをreadするのみ)。
#
# --step: teacher-check / jev-probe / pool / cost-estimate / rerank
# 冪等性: 出力ファイルが既に存在する場合、--forceなしでは再実行しない。
# ============================================================
from __future__ import annotations

import argparse
import difflib
import hashlib
import itertools
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

import er002_ja_web_research_r3 as r3
import er005_cost_logger as cl
import er016_topic_selection_chatgpt_repro_01 as repro01

load_dotenv()

THEME_TAG = "TOPIC_SELECTION_USER_PREFERENCE_RERANK_TRIAL_01"
MODEL_LUNA = "gpt-5.6-luna"
MODEL_TERRA = "gpt-5.6-terra"
MODEL_SOL = "gpt-5.6-sol"
EFFORT_DEFAULT = "medium"
JST = timezone(timedelta(hours=9))

TEACHER_PATH = "docs/pm/topic_selection_user_eval_dataset.json"
WINDOW_START_JST = "2026-09-22T21:05:00+09:00"
BUDGET_JPY = 150.0
USD_TO_JPY = 160

# --------------------------------------------------------------
# Jev Native Decisions API(ユーザー提示仕様、fix02委任文より逐語転記)
# --------------------------------------------------------------
JEV_BASE_URL = "https://www.jevai.org"
JEV_DECISIONS_PATH = "/api/v1/decisions"
JEV_MAX_BODY_BYTES = 32 * 1024
# score questionのcriteriaは2〜10レベル制約(jev_api_notes.md)。
# Luna等の1〜10スケールに近づけるため10レベルを採用し、返る0始まりの
# probability-weighted averageへ+1する線形変換をpredicted_score_1_10に使う。
JEV_SCORE_LEVELS = [f"Level {i}" for i in range(1, 11)]
JEV_EVAL_OBJECTIVE_JA = (
    "このユーザーが英語学習用News Audioとして続きを聞きたいと思う度合いを"
    "評価してください。"
)
JEV_TASK_TEXT_JA = (
    "このユーザーが英語学習用News Audioとして続きを聞きたいと思う度合いを、"
    "次のcandidateについて評価してください。"
)
JEV_BATCH_N = 10  # 60件を6 batch(10件ずつ)。根拠はjev_decision_schema.md
                  # (当初32 KiB制約からN=20を選んだが、実接続でN=20の20問
                  # 一括callが502[Cloudflare Bad Gateway]を繰り返し、N=5の
                  # batch5 probeは成功したため、信頼性を優先しN=10へ変更)。

# UGCドメイン(委任文指定)
UGC_DOMAIN_RE = re.compile(
    r"(note\.com|reddit\.com|minkara\.[a-z.]+|ameblo\.jp|hatenablog\.[a-z.]+"
    r"|x\.com|twitter\.com|instagram\.com|gravity[a-z.]*|threads\.net)",
    re.IGNORECASE,
)

MACHINE_GATE_EXCLUDE = {
    "PR_ADVERTORIAL", "AFFILIATE_RANKING", "SALE_PRICE",
    "UGC_PERSONAL", "LISTING_PAGE",
}
GATE_CATEGORIES = [
    "NEWS_FEATURE", "PRODUCT_PHENOMENON", "PR_ADVERTORIAL",
    "AFFILIATE_RANKING", "SALE_PRICE", "UGC_PERSONAL", "LISTING_PAGE",
    "UNCLEAR",
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


def call_model(client, developer: str, user: str, schema=None, stage="",
                model=MODEL_LUNA, effort=EFFORT_DEFAULT, retried=False):
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
    try:
        with cl.logging_context(THEME_TAG, stage):
            response = client.responses.create(**kwargs)
    except Exception as exc:
        if retried:
            raise
        print(f"[RETRY] {stage}: 技術的retry 1回目 ({exc})")
        time.sleep(2)
        return call_model(client, developer, user, schema=schema, stage=stage,
                           model=model, effort=effort, retried=True)
    if response.model != model:
        raise RuntimeError(
            f"STOP条件該当: actual model_idが要求モデルと異なる(stage={stage}, "
            f"requested={model}, actual={response.model})"
        )
    return response


def response_meta(response, extra: dict = None) -> dict:
    meta = {
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
    if extra:
        meta.update(extra)
    return meta


def normalize_url(u: str) -> str:
    if not u:
        return ""
    u = u.strip()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    u = u.split("?")[0].split("#")[0]
    u = u.rstrip("/")
    return u.lower()


# ------------------------------------------------------------
# Jev client ヘルパー
# ------------------------------------------------------------
def build_teacher_state() -> dict:
    """全stepで共通・byte単位で同一のstateを返す(委任文『同一stateを維持』)。"""
    d = load_json(TEACHER_PATH)
    items = []
    for key in ("dataset_r", "dataset_a", "dataset_b"):
        for it in d.get(key, []):
            items.append({
                "dataset_id": it.get("dataset_id"),
                "topic_ja": it.get("topic_ja"),
                "hook_ja": it.get("hook_ja"),
                "user_score": it.get("user_score"),
            })
    return {
        "evaluation_objective": JEV_EVAL_OBJECTIVE_JA,
        "preference_examples": items,
    }


def jev_score_question(candidate: dict) -> dict:
    return {
        "type": "score",
        "instructions": {
            "task": JEV_TASK_TEXT_JA,
            "candidate": {
                "topic_ja": candidate.get("topic_ja"),
                "summary_ja": candidate.get("summary_ja"),
                "source_name": candidate.get("source_name"),
            },
        },
        "criteria": JEV_SCORE_LEVELS,
    }


def mask_key_in_obj(obj, key: str):
    """objをJSON文字列化してkey(および先頭8文字)の出現有無を確認し、
    見つかった場合はマスクした上で再パースして返す。戻り値: (masked_obj, leak_found)。
    """
    if not key:
        return obj, False
    text = json.dumps(obj, ensure_ascii=False)
    leak_found = False
    if key in text:
        leak_found = True
        text = text.replace(key, "***MASKED_JEV_API_KEY***")
    prefix8 = key[:8]
    if len(prefix8) >= 8 and prefix8 in text:
        leak_found = True
        text = text.replace(prefix8, "***MASKED_JEV_KEY_PREFIX***")
    return json.loads(text), leak_found


def call_jev(api_key: str, state: dict, questions: dict, stage: str,
             max_429_waits: int = 2):
    """Jev Native Decisions API(POST /api/v1/decisions)を1回呼ぶ。
    429時のみRetry-Afterに従い最大max_429_waits回待機して再試行する
    (連打禁止、委任文STOP条件)。戻り値はdictで、鍵は一切含めない。
    """
    url = JEV_BASE_URL + JEV_DECISIONS_PATH
    body = {"state": state, "questions": questions}
    body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
    if len(body_bytes) > JEV_MAX_BODY_BYTES:
        raise SystemExit(
            f"STOP: Jev request body({len(body_bytes)} bytes)が32 KiB上限を"
            f"超過(stage={stage})。委任文STOP条件『Teacher 57件が32 KiBに"
            "収まらない』に準じ、送信を中止する。"
        )
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    waits = 0
    attempts = []

    def _filtered_headers(h):
        return {
            k: v for k, v in h.items()
            if "rate" in k.lower() or "retry" in k.lower() or "limit" in k.lower()
        }

    while True:
        t0 = time.time()
        resp = requests.post(url, data=body_bytes, headers=headers, timeout=30)
        elapsed_ms = round((time.time() - t0) * 1000, 1)
        attempts.append({
            "status_code": resp.status_code,
            "elapsed_ms": elapsed_ms,
            "rate_limit_headers": _filtered_headers(resp.headers),
        })
        if resp.status_code == 429 and waits < max_429_waits:
            retry_after = resp.headers.get("Retry-After")
            wait_s = float(retry_after) if retry_after and retry_after.isdigit() else 5.0
            print(f"[429] {stage}: Retry-After={retry_after} -> {wait_s}s待機"
                  f"({waits + 1}/{max_429_waits})")
            time.sleep(wait_s)
            waits += 1
            continue
        break
    rate_limit_headers = _filtered_headers(resp.headers)
    try:
        resp_json = resp.json()
    except ValueError:
        resp_json = None
    result = {
        "stage": stage,
        "status_code": resp.status_code,
        "elapsed_ms": elapsed_ms,
        "request_body_bytes": len(body_bytes),
        "rate_limit_headers": rate_limit_headers,
        "response_headers_content_type": resp.headers.get("Content-Type"),
        "response_json": resp_json,
        "response_text_if_not_json": None if resp_json is not None else resp.text[:2000],
        "waits_429": waits,
        "attempts": attempts,
    }
    masked, leak_found = mask_key_in_obj(result, api_key)
    masked["key_leak_found_in_response"] = leak_found
    return masked


def extract_jev_answers(resp_json) -> dict:
    """response.dataからanswersを抽出する(実測schemaに合わせflexibleに探す)。"""
    if not isinstance(resp_json, dict):
        return {}
    data = resp_json.get("data")
    if isinstance(data, dict):
        if isinstance(data.get("answers"), dict):
            return data["answers"]
        return data
    result = resp_json.get("result")
    if isinstance(result, dict) and isinstance(result.get("answers"), dict):
        return result["answers"]
    return {}


def jev_score_to_1_10(raw_score) -> float | None:
    if raw_score is None:
        return None
    try:
        return round(float(raw_score) + 1, 4)
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------
# Preference Prompt (Luna/Terra/Sol、fix03委任文STEP 3の逐語)
# ------------------------------------------------------------
PREFERENCE_DEVELOPER = (
    "You predict how much one specific listener would want to keep "
    "listening to an English-learning news audio piece about each topic."
)

PREFERENCE_SCHEMA = {
    "name": "preference_rerank",
    "schema": {
        "type": "object",
        "properties": {
            "preference_summary": {"type": "string"},
            "predictions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "predicted_score": {"type": "number"},
                        "reason": {"type": "string"},
                    },
                    "required": ["id", "predicted_score", "reason"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["preference_summary", "predictions"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_preference_user(teacher_items: list, pool_sorted: list) -> str:
    """委任文STEP 3のuser Promptを逐語構築する(地の文は一字一句そのまま、
    [Rated examples]/[Candidates]のみ実データのJSON Linesで埋める)。
    """
    rated_lines = [
        json.dumps({
            "dataset_id": it.get("dataset_id"),
            "topic_ja": it.get("topic_ja"),
            "hook_ja": it.get("hook_ja"),
            "user_score": it.get("user_score"),
        }, ensure_ascii=False)
        for it in teacher_items
    ]
    cand_lines = [
        json.dumps({
            "id": c["id"],
            "topic_ja": c.get("topic_ja"),
            "summary_ja": c.get("summary_ja"),
            "media": c.get("source_name"),
        }, ensure_ascii=False)
        for c in pool_sorted
    ]
    return (
        "Below are 57 topics that this listener has already rated from 1 "
        "(would not want to listen) to 10 (would definitely want to "
        "listen). Each item shows the topic, the hook that was attached at "
        "the time, and the listener's score. Note: the score reflects the "
        "topic together with that hook, so a low score does not always "
        "mean the topic itself is bad.\n\n"
        "[Rated examples]\n"
        + "\n".join(rated_lines) + "\n\n"
        "First, in 5–8 sentences, describe in your own words what "
        "separates the topics this listener rates high from the ones they "
        "rate low. Do not use a fixed checklist; infer it from the "
        "examples.\n\n"
        "Then, for each candidate below, predict the score this listener "
        "would give it as a topic for an English-learning news audio piece "
        "(1–10), and give one short reason. Predict the listener's "
        "wish to keep listening — not the topic's social importance "
        "or news value.\n\n"
        "[Candidates]\n"
        + "\n".join(cand_lines) + "\n\n"
        'Return JSON: {"preference_summary": string, "predictions": '
        '[{"id": string, "predicted_score": number, "reason": string}]}.'
    )


# ------------------------------------------------------------
# STEP 0: teacher-check
# ------------------------------------------------------------
def cmd_teacher_check(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "teacher_check.json")
    if skip_if_exists(path, args.force):
        return
    d = load_json(TEACHER_PATH)
    result = {"datasets": {}, "all_topics": []}
    ok = True
    for key in ("dataset_r", "dataset_a", "dataset_b"):
        items = d.get(key, [])
        missing_score = [it.get("item_no") for it in items
                          if it.get("user_score") is None]
        missing_topic = [it.get("item_no") for it in items
                          if not it.get("topic_ja")]
        result["datasets"][key] = {
            "n": len(items),
            "missing_score_item_no": missing_score,
            "missing_topic_item_no": missing_topic,
        }
        if missing_score or missing_topic:
            ok = False
        for it in items:
            result["all_topics"].append(
                {"dataset_id": it.get("dataset_id"), "item_no": it.get("item_no"),
                 "topic_ja": it.get("topic_ja")}
            )
    total_n = sum(v["n"] for v in result["datasets"].values())
    result["total_n"] = total_n
    if total_n != 57:
        ok = False
    from collections import Counter
    counts = Counter(t["topic_ja"] for t in result["all_topics"])
    dups = {k: v for k, v in counts.items() if v > 1}
    result["duplicate_topic_ja"] = dups
    result["complete"] = ok
    save_json(path, result)
    print(f"[OK] teacher-check: total_n={total_n} complete={ok} "
          f"duplicates={len(dups)}")
    if not ok:
        print("[STOP] Teacher Dataが不完全(件数/欠落/重複)。STOP条件該当。")
        raise SystemExit(1)


# ------------------------------------------------------------
# STEP 1: jev-probe(1件接続確認、fix02: ユーザー提示仕様で実接続)
# ------------------------------------------------------------
def cmd_jev_probe(args):
    out_dir = args.out_dir
    probe_path = out_path(out_dir, "jev_probe.json")
    stop_path = out_path(out_dir, "stop_reason.json")
    if skip_if_exists(probe_path, args.force):
        return
    key_present = bool(os.environ.get("JEV_API_KEY"))
    result = {
        "checked_at_jst": datetime.now(JST).isoformat(),
        "jev_api_key_present": key_present,
        "endpoint": JEV_BASE_URL + JEV_DECISIONS_PATH,
        "docs_notes_path": out_path(out_dir, "jev_api_notes.md"),
        "task_text_verbatim": JEV_TASK_TEXT_JA,
        "evaluation_objective_verbatim": JEV_EVAL_OBJECTIVE_JA,
    }
    if not key_present:
        stop_reason = {
            "reason": "JEV_KEY_MISSING",
            "detail": "JEV_API_KEYが環境変数に存在しない(bool=False)。",
            "action": "USER_DECISION_REQUIRED。",
            "checked_at_jst": result["checked_at_jst"],
        }
        save_json(probe_path, result)
        save_json(stop_path, stop_reason)
        print("[STOP] JEV_API_KEY不在。")
        return

    api_key = os.environ["JEV_API_KEY"]
    state = build_teacher_state()
    pool = load_json(out_path(out_dir, "candidate_pool.json"))
    c001 = next(c for c in pool if c["id"] == "C001")
    questions = {"C001": jev_score_question(c001)}
    call_result = call_jev(api_key, state, questions, stage="jev_probe_1call")
    result["state_bytes"] = len(json.dumps(state, ensure_ascii=False).encode("utf-8"))
    result["call_result"] = call_result
    resp_json = call_result.get("response_json")
    code_ok = isinstance(resp_json, dict) and resp_json.get("code") == 0
    answers = extract_jev_answers(resp_json) if code_ok else {}
    c001_answer = answers.get("C001")
    result["code_ok"] = code_ok
    result["answers_c001_raw"] = c001_answer
    if isinstance(c001_answer, dict) and "score" in c001_answer:
        result["scale_note"] = (
            "response['data']['answers']['C001']['score']はdocs記載どおり"
            "0始まりprobability-weighted average(0〜9連続値)と推定。"
            "predicted_score_1_10 = raw_score + 1 の線形変換を適用する"
            "(この変換はTop20の相対順位に影響しない)。"
        )
        result["predicted_score_1_10"] = jev_score_to_1_10(c001_answer.get("score"))
    else:
        result["scale_note"] = (
            "response構造がdocs記載のscore fieldと一致しなかった。実測値を"
            "answers_c001_rawに保存し、後続stepで実応答構造に合わせて解析"
            "する。"
        )
    save_json(probe_path, result)
    if not code_ok:
        stop_reason = {
            "reason": "JEV_CONNECTION_FAILED",
            "detail": (
                f"1件接続確認でcode==0を得られなかった(status_code="
                f"{call_result.get('status_code')}、response="
                f"{json.dumps(resp_json, ensure_ascii=False)[:500]})。"
                "委任文STOP条件『仕様と実応答が不一致でschemaを特定できない』"
                "に該当する可能性がある。"
            ),
            "action": "USER_DECISION_REQUIRED。",
            "checked_at_jst": result["checked_at_jst"],
        }
        save_json(stop_path, stop_reason)
        print(f"[STOP] jev-probe: 接続確認失敗(status_code="
              f"{call_result.get('status_code')})。stop_reason.json保存。")
        return
    print(f"[OK] jev-probe: code==0確認、status_code="
          f"{call_result.get('status_code')}、elapsed_ms="
          f"{call_result.get('elapsed_ms')}、"
          f"predicted_score_1_10={result.get('predicted_score_1_10')}")


# ------------------------------------------------------------
# STEP 1b: jev-probe-batch5(C001〜C005、payload/latency/rate limit確認)
# ------------------------------------------------------------
def cmd_jev_probe_batch5(args):
    out_dir = args.out_dir
    out_p = out_path(out_dir, "jev_probe_batch5.json")
    stop_path = out_path(out_dir, "stop_reason.json")
    if skip_if_exists(out_p, args.force):
        return
    probe_path = out_path(out_dir, "jev_probe.json")
    if not os.path.exists(probe_path):
        raise SystemExit("STOP: jev-probe未実行。先に --step jev-probe を実行すること。")
    probe = load_json(probe_path)
    if not probe.get("code_ok"):
        print("[STOP] jev-probe未成功のためbatch5を実行しない。")
        return
    api_key = os.environ["JEV_API_KEY"]
    state = build_teacher_state()
    pool = load_json(out_path(out_dir, "candidate_pool.json"))
    five = [c for c in pool if c["id"] in ("C001", "C002", "C003", "C004", "C005")]
    questions = {c["id"]: jev_score_question(c) for c in five}
    # 採用方式: 1 call・questions 5問(理由はresult["batch_method_reason"]参照)。
    call_result = call_jev(api_key, state, questions, stage="jev_probe_batch5")
    resp_json = call_result.get("response_json")
    code_ok = isinstance(resp_json, dict) and resp_json.get("code") == 0
    answers = extract_jev_answers(resp_json) if code_ok else {}
    has_usage_info = False
    if isinstance(resp_json, dict):
        text_repr = json.dumps(resp_json, ensure_ascii=False).lower()
        has_usage_info = any(
            k in text_repr for k in ("usage", "\"cost\"", "token", "billing", "credit")
        )
    result = {
        "checked_at_jst": datetime.now(JST).isoformat(),
        "batch_method": "1_call_5_questions",
        "batch_method_reason": (
            "docs(/docs, /jev-api)はPOST /api/v1/decisionsが単一requestで"
            "複数named questionsを受け付けると明記しており("
            "'questions[id]: One typed judgment'、複数id可)、questions数の"
            "上限記載はbody 32 KiBの制約のみ。5件は32 KiB制約内に収まるため"
            "(実測bytesはrequest_body_bytes参照)、5回の個別callより1 call・"
            "5 questionsの方がcall数を抑えられ、委任のstep4『60件を決定論的"
            "batchで処理』とも整合するため採用した。"
        ),
        "code_ok": code_ok,
        "call_result": call_result,
        "answers_raw": answers,
        "has_usage_or_cost_info": has_usage_info,
        "usage_status": "PRESENT" if has_usage_info else "Jev cost UNKNOWN",
    }
    save_json(out_p, result)
    if not code_ok:
        stop_reason = {
            "reason": "JEV_BATCH5_FAILED",
            "detail": f"batch5でcode!=0(status_code={call_result.get('status_code')})。",
            "action": "USER_DECISION_REQUIRED。",
            "checked_at_jst": result["checked_at_jst"],
        }
        save_json(stop_path, stop_reason)
        print("[STOP] jev-probe-batch5: 失敗。stop_reason.json保存。")
        return
    # 残りcall見込み: 60件をJEV_BATCH_N(=20)ずつで処理 => ceil(60/20)=3 call
    remaining_calls = -(-60 // JEV_BATCH_N)
    if not has_usage_info and remaining_calls > 15:
        stop_reason = {
            "reason": "JEV_COST_UNKNOWN_AND_TOO_LARGE",
            "detail": (
                f"usage/cost情報が応答に含まれず(Jev cost UNKNOWN)、残りの"
                f"想定call数({remaining_calls})が15を超えるため¥150管理不能"
                "と判断しSTOPする。"
            ),
            "action": "USER_DECISION_REQUIRED。",
            "checked_at_jst": result["checked_at_jst"],
        }
        save_json(stop_path, stop_reason)
        print("[STOP] Jev cost UNKNOWN かつ 残りcall数が15超。")
        return
    print(f"[OK] jev-probe-batch5: code==0、has_usage_info={has_usage_info}、"
          f"想定残りcall数={remaining_calls}(<=15のため続行)。")


# ------------------------------------------------------------
# STEP 2: pool
# ------------------------------------------------------------
def _load_search_trial_03_pool():
    d = load_json("er016_output/topic_selection_search_trial_03/pool_final.json")
    out = []
    for c in d.get("candidates", []):
        out.append({
            "raw_title": c.get("title"),
            "summary_ja": c.get("summary_ja"),
            "url": c.get("url"),
            "source_name": c.get("source_name"),
            "published_time_iso": c.get("published_time_iso"),
            "source_gate_category": (
                "PR_ADVERTORIAL" if c.get("is_pr_or_ad_guess") or
                c.get("machine_pr_signal") else c.get("source_gate_category")
            ),
            "origin": "topic_selection_search_trial_03/pool_final.json",
        })
    return out


def _load_reference_process_pool():
    d = load_json("er016_output/topic_selection_reference_process_trial_01/pool.json")
    out = []
    exclude_reason_prefixes = ("UGC_EXCLUDE", "PR_RELEASE", "PR_SURVEY_RELEASE",
                                "AD_SUBDOMAIN_CONTENT", "CONTENT_MARKETING",
                                "UNIV_PRESS_RELEASE")
    for cid, c in d.get("candidates", {}).items():
        status = c.get("status")
        if status == "dropped":
            reason = c.get("drop_reason") or ""
            if reason.startswith("DUPLICATE") or reason.startswith("SAME_AS"):
                continue  # 既にkept/replaced側に同一事象が残っている
            if any(reason.startswith(p) for p in exclude_reason_prefixes):
                continue  # UGC/PR系はSource Gate除外のまま維持
            # それ以外(窓外・一般性・トーン等)は候補へ復帰可(委任文の指示)
        out.append({
            "raw_title": c.get("topic_ja"),
            "summary_ja": c.get("summary_2sent_ja"),
            "url": c.get("url"),
            "source_name": c.get("source_name"),
            "published_time_iso": None,
            "source_gate_category": None,
            "origin": f"topic_selection_reference_process_trial_01/pool.json"
                      f"[{cid},status={status}]",
        })
    return out


def _load_generic_pool(path, origin_label):
    d = load_json(path)
    out = []
    for c in d.get("candidates", []):
        out.append({
            "raw_title": c.get("title"),
            "summary_ja": c.get("summary_ja"),
            "url": c.get("url"),
            "source_name": c.get("source_name"),
            "published_time_iso": c.get("published_time_iso"),
            "source_gate_category": (
                "PR_ADVERTORIAL" if c.get("is_pr_or_ad") else None
            ),
            "origin": origin_label,
        })
    return out


def machine_gate(cand: dict) -> str | None:
    """機械signalで確定できるカテゴリを返す。確定できなければNone。"""
    url = cand.get("url") or ""
    if UGC_DOMAIN_RE.search(url):
        return "UGC_PERSONAL"
    if cand.get("source_gate_category") in GATE_CATEGORIES:
        return cand["source_gate_category"]
    return None


CLASSIFY_SCHEMA = {
    "name": "source_gate_classify",
    "schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "category": {"type": "string", "enum": GATE_CATEGORIES},
                        "reason": {"type": "string"},
                    },
                    "required": ["id", "category", "reason"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["results"],
        "additionalProperties": False,
    },
    "strict": True,
}

CLASSIFY_DEVELOPER = (
    "You classify Japanese news/web candidates for a source-quality gate. "
    "Categories: NEWS_FEATURE (independent news/feature reporting), "
    "PRODUCT_PHENOMENON (a product or social phenomenon covered as news, "
    "not an ad), PR_ADVERTORIAL (PR release, sponsored, advertorial), "
    "AFFILIATE_RANKING (affiliate-style ranking/comparison article), "
    "SALE_PRICE (sale/discount/coupon focused article), "
    "UGC_PERSONAL (personal blog/UGC post), "
    "LISTING_PAGE (a list/search-result page, not a single article), "
    "UNCLEAR (cannot tell). Classify strictly from the given title/summary/"
    "source/url only."
)


def classify_batch(client, out_dir, items, batch_idx):
    lines = []
    for it in items:
        lines.append(json.dumps({
            "id": it["cand_id"], "title": it["raw_title"],
            "summary": it["summary_ja"], "source": it["source_name"],
            "url": it["url"],
        }, ensure_ascii=False))
    user = "Classify each of the following candidates.\n\n" + "\n".join(lines)
    resp = call_model(client, CLASSIFY_DEVELOPER, user, schema=CLASSIFY_SCHEMA,
                       stage=f"gate_classify_{batch_idx}", model=MODEL_LUNA)
    data = json.loads(resp.output_text)
    save_json(out_path(out_dir, "prompts", f"gate_classify_{batch_idx}.json"),
              {"developer": CLASSIFY_DEVELOPER, "user": user})
    save_json(out_path(out_dir, "raw_responses", f"gate_classify_{batch_idx}.json"),
              response_meta(resp))
    return {r["id"]: r for r in data["results"]}


CONTAM_SCHEMA = {
    "name": "contamination_check",
    "schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {"type": "string"},
                        "same_event_as_teacher": {"type": "boolean"},
                        "reason": {"type": "string"},
                    },
                    "required": ["candidate_id", "same_event_as_teacher", "reason"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["results"],
        "additionalProperties": False,
    },
    "strict": True,
}

CONTAM_DEVELOPER = (
    "You check whether a candidate news topic refers to the SAME real-world "
    "event/topic as a teacher-data topic that a listener has already rated, "
    "even if phrased differently. Judge based on the underlying event, not "
    "surface wording."
)


def contamination_batch(client, out_dir, pairs, batch_idx):
    lines = []
    for p in pairs:
        lines.append(json.dumps({
            "candidate_id": p["cand_id"], "candidate_topic": p["cand_topic"],
            "teacher_topic": p["teacher_topic"], "teacher_hook": p["teacher_hook"],
        }, ensure_ascii=False))
    user = ("For each pair below, judge if candidate_topic refers to the same "
            "underlying event as teacher_topic/teacher_hook.\n\n" + "\n".join(lines))
    resp = call_model(client, CONTAM_DEVELOPER, user, schema=CONTAM_SCHEMA,
                       stage=f"contamination_{batch_idx}", model=MODEL_LUNA)
    data = json.loads(resp.output_text)
    save_json(out_path(out_dir, "prompts", f"contamination_{batch_idx}.json"),
              {"developer": CONTAM_DEVELOPER, "user": user})
    save_json(out_path(out_dir, "raw_responses", f"contamination_{batch_idx}.json"),
              response_meta(resp))
    return {r["candidate_id"]: r for r in data["results"]}


def cmd_pool(args):
    out_dir = args.out_dir
    path = out_path(out_dir, "candidate_pool.json")
    if skip_if_exists(path, args.force):
        return
    install_logger(out_dir)

    raw = []
    raw += _load_search_trial_03_pool()
    raw += _load_reference_process_pool()
    raw += _load_generic_pool(
        "er016_output/topic_selection_chatgpt_repro_01_cont02/pool_new.json",
        "topic_selection_chatgpt_repro_01_cont02/pool_new.json")
    raw += _load_generic_pool(
        "er016_output/topic_selection_chatgpt_repro_01/candidates_raw.json",
        "topic_selection_chatgpt_repro_01/candidates_raw.json")

    stats = {"raw_total": len(raw)}

    # --- URL正規化dedup ---
    seen = set()
    deduped = []
    for c in raw:
        nu = normalize_url(c.get("url") or "")
        if not nu or nu in seen:
            continue
        seen.add(nu)
        c["norm_url"] = nu
        deduped.append(c)
    stats["after_url_dedup"] = len(deduped)

    # --- id付与 ---
    for i, c in enumerate(deduped):
        c["cand_id"] = f"RAW{i+1:04d}"

    # --- 機械Source Gate ---
    machine_excluded = []
    unclear = []
    machine_kept = []
    for c in deduped:
        cat = machine_gate(c)
        if cat is None:
            unclear.append(c)
        elif cat in MACHINE_GATE_EXCLUDE:
            c["source_gate_category"] = cat
            c["source_gate_stage"] = "machine"
            machine_excluded.append(c)
        elif cat == "UNCLEAR":
            unclear.append(c)
        else:
            c["source_gate_category"] = cat
            c["source_gate_stage"] = "machine"
            machine_kept.append(c)
    stats["machine_excluded"] = len(machine_excluded)
    stats["machine_kept"] = len(machine_kept)
    stats["needs_luna_classification"] = len(unclear)

    client = get_client()

    # --- Luna分類(UNCLEAR分のみ、40件/batch) ---
    luna_excluded = []
    luna_kept = []
    BATCH = 40
    for bi in range(0, len(unclear), BATCH):
        batch = unclear[bi:bi + BATCH]
        results = classify_batch(client, out_dir, batch, bi // BATCH)
        for c in batch:
            r = results.get(c["cand_id"])
            cat = r["category"] if r else "UNCLEAR"
            c["source_gate_category"] = cat
            c["source_gate_stage"] = "luna"
            c["source_gate_reason"] = r["reason"] if r else "no_result"
            if cat in MACHINE_GATE_EXCLUDE or cat == "UNCLEAR":
                luna_excluded.append(c)
            else:
                luna_kept.append(c)
    stats["luna_excluded"] = len(luna_excluded)
    stats["luna_kept"] = len(luna_kept)

    gated = machine_kept + luna_kept
    stats["after_source_gate"] = len(gated)

    save_json(out_path(out_dir, "gate_result.json"), {
        "stats": stats,
        "machine_excluded_sample": [
            {"cand_id": c["cand_id"], "title": c.get("raw_title"),
             "category": c.get("source_gate_category"), "url": c.get("url")}
            for c in machine_excluded
        ],
        "luna_excluded_sample": [
            {"cand_id": c["cand_id"], "title": c.get("raw_title"),
             "category": c.get("source_gate_category"),
             "reason": c.get("source_gate_reason"), "url": c.get("url")}
            for c in luna_excluded
        ],
    })

    # --- 既知評価Topic混入検査(difflib >= 0.5) ---
    teacher = load_json(TEACHER_PATH)
    teacher_items = []
    for key in ("dataset_r", "dataset_a", "dataset_b"):
        for it in teacher.get(key, []):
            teacher_items.append({
                "dataset_id": it.get("dataset_id"), "item_no": it.get("item_no"),
                "topic_ja": it.get("topic_ja") or "", "hook_ja": it.get("hook_ja") or "",
            })

    def best_match(topic_ja):
        best = (0.0, None)
        for t in teacher_items:
            r1 = difflib.SequenceMatcher(None, topic_ja, t["topic_ja"]).ratio()
            r2 = difflib.SequenceMatcher(None, topic_ja, t["hook_ja"]).ratio()
            r = max(r1, r2)
            if r > best[0]:
                best = (r, t)
        return best

    auto_exclude = []
    borderline = []
    clean = []
    for c in gated:
        ratio, t = best_match(c.get("raw_title") or "")
        c["contamination_best_ratio"] = round(ratio, 3)
        c["contamination_best_match"] = (
            f"{t['dataset_id']}#{t['item_no']}:{t['topic_ja']}" if t else None
        )
        if ratio >= 0.65:
            auto_exclude.append(c)
        elif ratio >= 0.5:
            borderline.append(c)
        else:
            clean.append(c)

    luna_contam_excluded = []
    if borderline:
        pairs = []
        for c in borderline:
            ratio, t = best_match(c.get("raw_title") or "")
            pairs.append({
                "cand_id": c["cand_id"], "cand_topic": c.get("raw_title"),
                "teacher_topic": t["topic_ja"], "teacher_hook": t["hook_ja"],
            })
        results = {}
        CBATCH = 30
        for bi in range(0, len(pairs), CBATCH):
            results.update(contamination_batch(client, out_dir,
                                                 pairs[bi:bi + CBATCH], bi // CBATCH))
        for c in borderline:
            r = results.get(c["cand_id"])
            if r and r["same_event_as_teacher"]:
                c["contamination_reason"] = r["reason"]
                luna_contam_excluded.append(c)
            else:
                c["contamination_reason"] = r["reason"] if r else "no_result_kept"
                clean.append(c)

    final = clean
    stats["contamination_auto_excluded"] = len(auto_exclude)
    stats["contamination_borderline"] = len(borderline)
    stats["contamination_luna_excluded"] = len(luna_contam_excluded)
    stats["contamination_kept_after_check"] = len(final)

    save_json(out_path(out_dir, "contamination_result.json"), {
        "stats": {
            "auto_excluded_ge_0.65": len(auto_exclude),
            "borderline_0.5_to_0.65": len(borderline),
            "luna_excluded_from_borderline": len(luna_contam_excluded),
        },
        "auto_excluded": [
            {"cand_id": c["cand_id"], "title": c.get("raw_title"),
             "ratio": c["contamination_best_ratio"],
             "match": c["contamination_best_match"]}
            for c in auto_exclude
        ],
        "luna_excluded": [
            {"cand_id": c["cand_id"], "title": c.get("raw_title"),
             "ratio": c["contamination_best_ratio"],
             "match": c["contamination_best_match"],
             "reason": c.get("contamination_reason")}
            for c in luna_contam_excluded
        ],
    })

    # --- 目標50件(40-60)に整形。超過時は各origin均等になるよう間引き ---
    target_min, target_max = 40, 60
    stats["final_before_trim"] = len(final)
    if len(final) > target_max:
        # originごとに束ね、ラウンドロビンでtarget件数まで採用
        from collections import defaultdict
        by_origin = defaultdict(list)
        for c in final:
            by_origin[c["origin"].split("[")[0]].append(c)
        ordered = []
        idx = 0
        keys = list(by_origin.keys())
        while len(ordered) < target_max and any(by_origin.values()):
            k = keys[idx % len(keys)]
            if by_origin[k]:
                ordered.append(by_origin[k].pop(0))
            idx += 1
            if idx > 10000:
                break
        final = ordered

    stats["final_pool_n"] = len(final)
    stats["target_range"] = [target_min, target_max]
    stats["needs_supplemental_search"] = len(final) < target_min

    pool_out = []
    for i, c in enumerate(final):
        pool_out.append({
            "id": f"C{i+1:03d}",
            "topic_ja": (c.get("raw_title") or "")[:200],
            "summary_ja": c.get("summary_ja") or "",
            "url": c.get("url"),
            "source_name": c.get("source_name"),
            "published_time_iso": c.get("published_time_iso"),
            "origin_trial": c.get("origin"),
            "source_class": c.get("source_gate_category"),
            "source_gate_stage": c.get("source_gate_stage"),
            "contamination_best_ratio": c.get("contamination_best_ratio"),
        })

    save_json(path, pool_out)
    sha256 = hashlib.sha256(
        json.dumps(pool_out, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    save_json(out_path(out_dir, "candidate_pool_sha256.json"), {"sha256": sha256})
    save_json(out_path(out_dir, "pool_pipeline_stats.json"), stats)

    print(f"[OK] pool: raw={stats['raw_total']} after_dedup="
          f"{stats['after_url_dedup']} after_gate={stats['after_source_gate']} "
          f"after_contamination={stats['contamination_kept_after_check']} "
          f"final={stats['final_pool_n']} sha256={sha256[:16]}...")
    if stats["needs_supplemental_search"]:
        print("[WARN] final_pool_n < 40。最小限の追加Search(--max-search-calls)"
              "が必要(未実装、既存Poolのみで下限未達)。")


# ------------------------------------------------------------
# verify-fixed (fix03委任文: 再作成禁止の固定物を機械再確認)
# ------------------------------------------------------------
def cmd_verify_fixed(args):
    out_dir = args.out_dir
    pool_path = out_path(out_dir, "candidate_pool.json")
    sha_path = out_path(out_dir, "candidate_pool_sha256.json")
    if not os.path.exists(pool_path) or not os.path.exists(sha_path):
        raise SystemExit(
            "STOP: candidate_pool.json/candidate_pool_sha256.jsonが存在しない"
            "(既存Poolを再作成せず使うのが前提のため、無ければ先に--step pool "
            "を実行済みの出力を確認すること)。"
        )
    pool = load_json(pool_path)
    recomputed_pool_sha = hashlib.sha256(
        json.dumps(pool, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    recorded_pool_sha = load_json(sha_path)["sha256"]
    pool_sha_match = recomputed_pool_sha == recorded_pool_sha
    pool_n_ok = len(pool) == 60

    d = load_json(TEACHER_PATH)
    teacher_n = sum(len(d.get(k, [])) for k in ("dataset_r", "dataset_a", "dataset_b"))
    teacher_ok = teacher_n == 57

    ok = pool_sha_match and pool_n_ok and teacher_ok
    result = {
        "pool_sha256_recorded": recorded_pool_sha,
        "pool_sha256_recomputed": recomputed_pool_sha,
        "pool_sha256_match": pool_sha_match,
        "pool_n": len(pool),
        "pool_n_ok": pool_n_ok,
        "teacher_total_n": teacher_n,
        "teacher_ok": teacher_ok,
        "overall_ok": ok,
        "checked_at_jst": datetime.now(JST).isoformat(),
    }
    save_json(out_path(out_dir, "verify_fixed.json"), result)
    print(f"[{'OK' if ok else 'STOP'}] verify-fixed: pool_sha_match="
          f"{pool_sha_match} pool_n={len(pool)} teacher_n={teacher_n}")
    if not ok:
        raise SystemExit(
            f"STOP: verify-fixed不一致(委任文STOP条件『Candidate Poolが変わる/"
            f"Teacher Dataが変わる』に該当)。詳細={result}"
        )


# ------------------------------------------------------------
# cost-estimate
# ------------------------------------------------------------
def _price(pricing, provider, model, meter):
    try:
        return next(p["price"] for p in pricing
                    if p["provider"] == provider and p["model"] == model
                    and p["meter"] == meter)
    except StopIteration:
        return None


def compute_actual_cost_jpy(out_dir: str) -> dict:
    """raw_usage_log.jsonl(THEME_TAG分)から実績costを集計する。単価が
    pricing_snapshot.jsonに無いモデル(Terra等)はjpyを合計へ含めず
    'UNKNOWN_PRICING'として件数のみ記録する(捏造しない)。cmd_cost_estimate
    と--step rerank(L/T/S)の予算上限チェックの両方から呼ばれる共通ロジック。
    """
    pricing = load_json("er005_output/cost_baseline_01/pricing_snapshot.json")["prices"]

    def model_prices(model_name):
        return (
            _price(pricing, "openai", model_name, "input_tokens"),
            _price(pricing, "openai", model_name, "cached_input_tokens"),
            _price(pricing, "openai", model_name, "output_tokens"),
        )

    log_path = out_path(out_dir, "raw_usage_log.jsonl")
    entries = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    entries = [e for e in entries if e.get("theme") == THEME_TAG]

    by_model = {}
    total_jpy = 0.0
    for e in entries:
        if e.get("provider") != "openai" or not e.get("success", True):
            continue
        # 注記(2026-09-25実測で発覚・修正): er005_cost_logger.record()は
        # モデルIDを"model_id"キーで書き込む("model"キーは存在しない)。旧
        # 実装はe.get("model")を参照しており常にNoneとなりMODEL_LUNAへ
        # フォールバックしていたため、Terra/Sol呼び出しの実績costがLuna単価
        # で誤集計されていた(Luna単発callのみだった従来利用では顕在化せず)。
        model_name = e.get("model_id") or e.get("model") or MODEL_LUNA
        prices = model_prices(model_name)
        if any(p is None for p in prices):
            by_model.setdefault(model_name, {"calls": 0, "jpy": "UNKNOWN_PRICING"})
            by_model[model_name]["calls"] += 1
            continue
        p_in, p_cached, p_out = prices
        it = e.get("input_tokens") or 0
        ct = e.get("cached_input_tokens") or 0
        ot = e.get("output_tokens") or 0
        billable_in = max(it - ct, 0)
        usd = (billable_in / 1_000_000) * p_in + (ct / 1_000_000) * p_cached \
            + (ot / 1_000_000) * p_out
        jpy = usd * USD_TO_JPY
        entry = by_model.setdefault(model_name, {"calls": 0, "jpy": 0.0})
        if entry["jpy"] == "UNKNOWN_PRICING":
            continue
        entry["calls"] += 1
        entry["jpy"] += jpy
        total_jpy += jpy

    return {"total_jpy_known_models_only": round(total_jpy, 2), "by_model": by_model}


def cmd_cost_estimate(args):
    out_dir = args.out_dir
    cost = compute_actual_cost_jpy(out_dir)
    total_jpy = cost["total_jpy_known_models_only"]
    by_model = cost["by_model"]
    budget = getattr(args, "budget_jpy", BUDGET_JPY)

    jev_cost_status = "NOT_YET_PROBED"
    batch5_path = out_path(out_dir, "jev_probe_batch5.json")
    if os.path.exists(batch5_path):
        b5 = load_json(batch5_path)
        jev_cost_status = b5.get("usage_status", "UNKNOWN")

    result = {
        "budget_jpy": budget,
        "actual_so_far_jpy": total_jpy,
        "by_model": by_model,
        "jev_cost_status": jev_cost_status,
        "within_budget": total_jpy <= budget,
        "note": "OpenAI課金分(pool step・rerank L/T/S等)の実績(known price "
                "modelsのみ合算)。Terra等、pricing_snapshot.jsonに単価が無い"
                "モデルはjpyへ含めず'UNKNOWN_PRICING'として件数のみ記録する"
                "(捏造しない)。Jevはresponseにusage/costフィールドが無い場合"
                "jev_cost_statusに'Jev cost UNKNOWN'を記録する(本Trialでは"
                "Jev armはDEFERRED、新規callは発生しない)。",
    }
    save_json(out_path(out_dir, "cost_estimate.json"), result)
    print(f"[OK] cost-estimate: actual_so_far={total_jpy} JPY "
          f"(budget={budget}) jev_cost_status={jev_cost_status}")


# ------------------------------------------------------------
# rerank
# ------------------------------------------------------------
def cmd_rerank_jev(args):
    out_dir = args.out_dir
    arm_dir = out_path(out_dir, "arms", "J")
    pred_path = os.path.join(arm_dir, "predictions.json")
    if skip_if_exists(pred_path, args.force):
        return
    stop_path = out_path(out_dir, "stop_reason.json")
    if os.path.exists(stop_path):
        print(f"[STOP] Jev arm実施不能(理由: {stop_path}参照)。")
        raise SystemExit(1)
    probe_path = out_path(out_dir, "jev_probe.json")
    if not os.path.exists(probe_path) or not load_json(probe_path).get("code_ok"):
        raise SystemExit("STOP: jev-probeが成功していない。先に --step jev-probe を実行すること。")

    api_key = os.environ["JEV_API_KEY"]
    state = build_teacher_state()
    pool = load_json(out_path(out_dir, "candidate_pool.json"))
    pool_sha = load_json(out_path(out_dir, "candidate_pool_sha256.json"))["sha256"]
    pool_sorted = sorted(pool, key=lambda c: c["id"])  # id昇順(委任文指定)

    predictions = {}
    batch_meta = []
    model_actual_values = set()
    for bi, start in enumerate(range(0, len(pool_sorted), JEV_BATCH_N)):
        if bi > 0:
            # 実測(2026-09-24): N=20(20問一括)は502(Cloudflare Bad Gateway)
            # を繰り返した。N=10へ縮小した上でbatch間8秒間隔を設ける
            # (連打回避)。この経緯はjev_decision_schema.mdへ記録する。
            time.sleep(8)
        batch = pool_sorted[start:start + JEV_BATCH_N]
        questions = {c["id"]: jev_score_question(c) for c in batch}
        call_result = call_jev(api_key, state, questions,
                                stage=f"jev_rerank_batch_{bi:02d}")
        save_json(os.path.join(arm_dir, "raw", f"batch_{bi:02d}.json"), call_result)
        resp_json = call_result.get("response_json")
        code_ok = isinstance(resp_json, dict) and resp_json.get("code") == 0
        if not code_ok:
            sc = call_result.get("status_code")
            reason = (
                "429が最大待機後も解決しない(委任文STOP条件)"
                if sc == 429 else
                f"HTTP {sc}(5xxインフラエラー、Retry-Afterヘッダ="
                f"{call_result.get('rate_limit_headers', {}).get('Retry-After')})"
                if sc and sc >= 500 else
                "仕様と実応答が不一致でschemaを特定できない(委任文STOP条件)"
            )
            save_json(stop_path, {
                "reason": "JEV_RERANK_RATE_LIMITED_OR_UNSTABLE",
                "detail": (
                    f"batch_{bi:02d}(N={JEV_BATCH_N}件)でcode!=0"
                    f"(status_code={sc})。理由: {reason}。単一candidate probe"
                    "(jev-probe)と5件probe(jev-probe-batch5)は成功したが、"
                    "60件抽出用の複数questions一括call(N=20およびN=10で試行)"
                    "は複数回・時間を空けた再試行(N=20で60秒超待機後の再試行"
                    "含む)でも429または502(Cloudflare Bad Gateway、"
                    "Retry-After:60)が解消しなかった。委任文STOP条件"
                    "『429が解決しない(Retry-Afterに従い最大2回待機、連打"
                    "禁止)』に該当すると判断しSTOPする。"
                ),
                "action": "USER_DECISION_REQUIRED。",
                "checked_at_jst": datetime.now(JST).isoformat(),
                "attempted_batch_sizes": [20, 10],
                "successful_calls": ["jev_probe (1 candidate)",
                                      "jev_probe_batch5 (5 candidates)"],
            })
            raise SystemExit(
                f"STOP: rerank batch_{bi:02d}でcode!=0(status_code={sc})。理由: {reason}。"
            )
        if isinstance(resp_json, dict) and isinstance(resp_json.get("data"), dict):
            model_actual_values.add(resp_json["data"].get("model"))
        answers = extract_jev_answers(resp_json)
        for c in batch:
            ans = answers.get(c["id"], {})
            raw_score = ans.get("score") if isinstance(ans, dict) else None
            predictions[c["id"]] = {
                "id": c["id"],
                "predicted_score_1_10": jev_score_to_1_10(raw_score),
                "raw_score": raw_score,
                "reason": ans.get("legend") if isinstance(ans, dict) else None,
            }
        batch_meta.append({
            "batch_idx": bi,
            "candidate_ids": [c["id"] for c in batch],
            "request_body_bytes": call_result.get("request_body_bytes"),
            "elapsed_ms": call_result.get("elapsed_ms"),
            "status_code": call_result.get("status_code"),
        })

    save_json(pred_path, list(predictions.values()))
    ranked = sorted(
        [p for p in predictions.values() if p["predicted_score_1_10"] is not None],
        key=lambda p: p["predicted_score_1_10"], reverse=True,
    )
    save_json(os.path.join(arm_dir, "top20.json"), ranked[:20])
    save_json(os.path.join(arm_dir, "api_meta.json"), {
        "endpoint": JEV_BASE_URL + JEV_DECISIONS_PATH,
        "model_field": "omitted(service default)",
        "response_model_actual_values": list(model_actual_values),
        "batch_count": len(batch_meta),
        "batch_n": JEV_BATCH_N,
        "pool_sha256": pool_sha,
        "batches": batch_meta,
    })
    print(f"[OK] rerank arms=J: {len(predictions)}件scored、"
          f"{len(batch_meta)} batch、top20保存。")


JEV_DEFERRED_MSG = (
    "DEFERRED: Jev armは2026-09-25のユーザー方針変更により正式にDEFERRED。"
    "理由: TypeSafe公式Jevは現在新規登録不可・公式API access取得不可であり、"
    "非公式Jevサービス(www.jevai.org)は比較対象に使用しない。既存Jev client"
    "実装(cmd_rerank_jev/call_jev等)は削除せず保持するが、このguardにより "
    "--arms にJを含む呼び出しは即座に終了しJevへは接続しない。access取得後、"
    "同じ60件Pool・同じTeacher Data・同じ評価条件で追加測定可能。詳細は "
    "jev_deferred.md参照。"
)


def cmd_rerank_lts(args, arms: list):
    """Luna/Terra/Sol(L/T/S)のrerank(fix03委任文STEP 3逐語Prompt)。"""
    out_dir = args.out_dir
    budget_jpy = args.budget_jpy
    install_logger(out_dir)

    model_map = {"L": MODEL_LUNA, "T": MODEL_TERRA, "S": MODEL_SOL}
    unknown_arms = [a for a in arms if a not in model_map]
    if unknown_arms:
        raise SystemExit(f"STOP: 未対応のarm指定: {unknown_arms}(対応: L,T,S)")

    pool = load_json(out_path(out_dir, "candidate_pool.json"))
    pool_sha = load_json(out_path(out_dir, "candidate_pool_sha256.json"))["sha256"]
    pool_sorted = sorted(pool, key=lambda c: c["id"])
    teacher = build_teacher_state()["preference_examples"]
    prompt_user = build_preference_user(teacher, pool_sorted)
    prompt_sha256 = hashlib.sha256(prompt_user.encode("utf-8")).hexdigest()
    save_json(out_path(out_dir, "prompts", "rerank_lts_shared_prompt.json"), {
        "developer": PREFERENCE_DEVELOPER,
        "user": prompt_user,
        "user_sha256": prompt_sha256,
        "note": "L/T/Sで完全同一の入力文字列(sha256一致で保証)。",
    })

    client = None
    for arm in arms:
        arm_dir = out_path(out_dir, "arms", arm)
        pred_path = os.path.join(arm_dir, "predictions.json")
        if skip_if_exists(pred_path, args.force):
            continue

        cost_so_far = compute_actual_cost_jpy(out_dir)["total_jpy_known_models_only"]
        if cost_so_far >= budget_jpy:
            raise SystemExit(
                f"STOP: 予算上限到達(budget_jpy={budget_jpy}, "
                f"actual_so_far_jpy={cost_so_far})。arm={arm}の呼び出し前に停止"
                "(委任文STOP条件『¥100超過見込み』)。"
            )
        if client is None:
            client = get_client()
        model_id = model_map[arm]
        t0 = time.time()
        resp = call_model(client, PREFERENCE_DEVELOPER, prompt_user,
                           schema=PREFERENCE_SCHEMA, stage=f"rerank_{arm}",
                           model=model_id, effort=EFFORT_DEFAULT)
        elapsed = time.time() - t0
        data = json.loads(resp.output_text)
        preds = data.get("predictions", [])
        pool_ids = {c["id"] for c in pool_sorted}
        got_ids = {p.get("id") for p in preds}
        missing_ids = sorted(pool_ids - got_ids)

        retry_note = None
        if missing_ids:
            print(f"[RETRY] arm={arm}: {len(missing_ids)}件score欠落。同一Prompt"
                  "で1回のみ再実行。")
            t1 = time.time()
            resp_retry = call_model(client, PREFERENCE_DEVELOPER, prompt_user,
                                     schema=PREFERENCE_SCHEMA,
                                     stage=f"rerank_{arm}_retry",
                                     model=model_id, effort=EFFORT_DEFAULT)
            elapsed_retry = time.time() - t1
            data_retry = json.loads(resp_retry.output_text)
            preds_retry = data_retry.get("predictions", [])
            got_ids_retry = {p.get("id") for p in preds_retry}
            still_missing = sorted(pool_ids - got_ids_retry)
            retry_note = {
                "reason": "初回callで60件中一部score欠落",
                "first_call_missing_ids": missing_ids,
                "first_call_missing_n": len(missing_ids),
                "retry_call_missing_ids": still_missing,
                "retry_call_missing_n": len(still_missing),
                "retry_elapsed_seconds": round(elapsed_retry, 3),
            }
            if len(got_ids_retry) >= len(got_ids):
                data, preds, resp, elapsed = data_retry, preds_retry, resp_retry, elapsed_retry
                missing_ids = still_missing

        os.makedirs(arm_dir, exist_ok=True)
        save_json(pred_path, preds)
        ranked = sorted(
            [p for p in preds if isinstance(p.get("predicted_score"), (int, float))],
            key=lambda p: p["predicted_score"], reverse=True,
        )
        save_json(os.path.join(arm_dir, "top20.json"), ranked[:20])
        save_json(os.path.join(arm_dir, "top10.json"), ranked[:10])
        with open(os.path.join(arm_dir, "preference_summary.txt"),
                  "w", encoding="utf-8") as f:
            f.write(data.get("preference_summary", ""))
        save_json(os.path.join(arm_dir, "api_meta.json"), response_meta(resp, {
            "arm": arm,
            "model_requested": model_id,
            "effort": EFFORT_DEFAULT,
            "prompt_user_sha256": prompt_sha256,
            "pool_sha256": pool_sha,
            "elapsed_seconds": round(elapsed, 3),
            "n_candidates": len(pool_sorted),
            "n_predictions": len(preds),
            "missing_ids_final": missing_ids,
            "retry": retry_note,
        }))
        cost_after = compute_actual_cost_jpy(out_dir)["total_jpy_known_models_only"]
        print(f"[OK] rerank arm={arm} model_requested={model_id} "
              f"model_actual={resp.model} n_predictions={len(preds)} "
              f"missing_final={len(missing_ids)} cost_so_far_jpy={cost_after}")


def cmd_rerank(args):
    out_dir = args.out_dir
    arms = [a for a in args.arms.split(",") if a]
    if "J" in arms:
        print(f"[DEFERRED] {JEV_DEFERRED_MSG}")
        raise SystemExit(1)
    cmd_rerank_lts(args, arms)


def spearman_all(xs: list, ys: list):
    n = len(xs)
    if n < 2:
        return None

    def rank(vals):
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        ranks = [0.0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg_rank = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranks[order[k]] = avg_rank
            i = j + 1
        return ranks

    rx, ry = rank(xs), rank(ys)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return round(1 - (6 * d2) / (n * (n ** 2 - 1)), 4)


def cmd_assemble(args):
    out_dir = args.out_dir
    candidate_arms = ["L", "T", "S"]
    arm_ids = [a for a in candidate_arms
               if os.path.exists(out_path(out_dir, "arms", a, "predictions.json"))]
    if len(arm_ids) < 2:
        raise SystemExit(
            f"STOP: assembleには最低2 arm(L/T/Sのうち)のpredictions.jsonが"
            f"必要。現状存在するarm: {arm_ids}。"
        )

    pool = load_json(out_path(out_dir, "candidate_pool.json"))
    all_ids = sorted(c["id"] for c in pool)

    scores = {a: {p["id"]: p["predicted_score"]
                  for p in load_json(out_path(out_dir, "arms", a, "predictions.json"))
                  if isinstance(p.get("predicted_score"), (int, float))}
              for a in arm_ids}
    tops20 = {a: [p["id"] for p in load_json(out_path(out_dir, "arms", a, "top20.json"))]
              for a in arm_ids}
    tops10 = {a: [p["id"] for p in load_json(out_path(out_dir, "arms", a, "top10.json"))]
              for a in arm_ids}

    lines = [f"# model_agreement (arms present: {','.join(arm_ids)})\n\n"]
    pair_results = []
    for a, b in itertools.combinations(arm_ids, 2):
        overlap20 = set(tops20[a]) & set(tops20[b])
        overlap10 = set(tops10[a]) & set(tops10[b])
        common_ids = [i for i in all_ids if i in scores[a] and i in scores[b]]
        rho = spearman_all([scores[a][i] for i in common_ids],
                            [scores[b][i] for i in common_ids])
        pair_results.append({
            "pair": f"{a} vs {b}", "top20_overlap": len(overlap20),
            "top10_overlap": len(overlap10), "n_common": len(common_ids),
            "spearman": rho,
        })
        lines.append(f"- {a} vs {b}: top20重複={len(overlap20)}/20, "
                      f"top10重複={len(overlap10)}/10, "
                      f"Spearman(n={len(common_ids)})={rho}\n")
    with open(out_path(out_dir, "model_agreement.md"), "w", encoding="utf-8") as f:
        f.writelines(lines)

    table_lines = [
        "# predicted_scores_all (全60件candidate、arm別predicted_score)\n\n",
        "| id | " + " | ".join(arm_ids) + " |\n",
        "|---|" + "---|" * len(arm_ids) + "\n",
    ]
    for cid in all_ids:
        row = [cid] + [str(scores[a].get(cid, "")) for a in arm_ids]
        table_lines.append("| " + " | ".join(row) + " |\n")
    with open(out_path(out_dir, "predicted_scores_all.md"), "w", encoding="utf-8") as f:
        f.writelines(table_lines)

    save_json(out_path(out_dir, "preference_summary.json"), {
        "arms": arm_ids, "top20": tops20, "top10": tops10,
        "pair_agreement": pair_results,
    })
    print(f"[OK] assemble: arms={arm_ids} model_agreement.md / "
          "predicted_scores_all.md / preference_summary.json 保存。")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--step", required=True,
                        choices=["teacher-check", "jev-probe",
                                 "jev-probe-batch5", "pool", "verify-fixed",
                                 "cost-estimate", "rerank", "assemble"])
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--target", type=int, default=50)
    parser.add_argument("--max-search-calls", type=int, default=4)
    parser.add_argument("--budget-jpy", type=float, default=BUDGET_JPY)
    parser.add_argument("--arms", default="J,L,T,S")
    parser.add_argument("--env-file", default=None,
                         help="指定時、load_dotenv(path, override=True)で明示読込"
                              "(値はログ・出力に一切含めない)。")
    args = parser.parse_args()

    if args.env_file:
        load_dotenv(args.env_file, override=True)

    os.makedirs(args.out_dir, exist_ok=True)

    if args.step == "teacher-check":
        cmd_teacher_check(args)
    elif args.step == "jev-probe":
        cmd_jev_probe(args)
    elif args.step == "jev-probe-batch5":
        cmd_jev_probe_batch5(args)
    elif args.step == "pool":
        cmd_pool(args)
    elif args.step == "verify-fixed":
        cmd_verify_fixed(args)
    elif args.step == "cost-estimate":
        cmd_cost_estimate(args)
    elif args.step == "rerank":
        cmd_rerank(args)
    elif args.step == "assemble":
        cmd_assemble(args)


if __name__ == "__main__":
    main()
