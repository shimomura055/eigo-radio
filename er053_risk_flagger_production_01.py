# -*- coding: utf-8 -*-
"""er053_risk_flagger_production_01.py
RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C1(追加のみ、2026-10-10)。Risk Flagger(RF) Production module。

役割: 完成した英語記事(Advanced=b1b / Standard=a2)を、完全な検証済み台帳(verified_fact_ledger.txt)と照らし、
「人間が確認した方がよい文」の候補(Flag)を列挙する。**合否判定しない・記事を書き換えない・Productionを止めない**
(非Blocking)。結果はReview Queue(er053_review_queue_01)へ保存され、人間(ChatGPT側のHuman Review)が読む。
RF結果から分岐するSTOP/Rewrite/削除/再生成/自動retryは無い(API技術retryのみ)。

C1の段階ではどのProduction runnerからも呼ばれない(C2で配線)。Trial module(er050/er051/er052*)はimportしない。

4条件(逐次実行。er005_cost_loggerの_CONTEXTがglobalで並列だとstage tagが競合するため):
  luna A3 / luna A4 / gemini35fl A3 / gemini35fl A4
  - Luna   = gpt-6-luna, reasoning effort=medium, OpenAI SDK(Responses API)。SDK patch(er005_cost_logger.install)が
             自動で費用を記録するため、本moduleは手動記録しない(二重記録しない)。
  - Gemini = gemini-3.5-flash-lite, REST(generateContent)。SDK patchの外なので、本moduleが
             er005_cost_logger.record()でprovider="gemini"互換レコードを書く。output_tokensにthinking tokensを含める。
  Prompt(A3/A4 system)はWRITER-DEV-RISK-FLAGGER ANTENNA-TRIAL-01のantenna_prompts.antenna_system(3/4)と
  byte-identical(sha256をtestで固定)。Gemini adapterはmeta_rollback_crossmodel_01/xm_driver.pyのbuild_request/
  parse_responseの移植(Provider既定のまま、thinkingConfig等は送らない)。

呼出契約: er005_cost_logger.logging_context()ブロックの**外**で呼ぶこと(本moduleが条件ごとに
stage="risk_flag.<model_key>.<A3|A4>.<level>" のcontextを自前で張る)。ブロック内で呼ばれた場合は
結果warningsに記録する(RFを止めない)。
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import secrets
import time

import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er053_en_sentence_splitter_01 as splitter

SCHEMA_VERSION = "rf_production_v1"
THEME_TAG = "RISK_FLAGGER_PRODUCTION_01"
HERE = os.path.dirname(os.path.abspath(__file__))
PRICING_SNAPSHOT_PATH = os.path.join(HERE, "er005_output", "cost_baseline_01", "pricing_snapshot.json")
USD_JPY = 160.0                      # efam.USD_JPY と同値(testで一致を固定)
EFFORT = "medium"
MAX_OUT = 8000
HTTP_TIMEOUT = 240
TRANSIENT_RETRIES = 2                # 一時障害(API例外)
FORMAT_RETRIES = 1                   # JSON/schema違反
LEVELS = ("b1b", "a2")               # b1b=Advanced, a2=Standard

# ------------------------------------------------------------
# A3 / A4 system prompt(antenna_prompts.py から byte-identical 移植。文言変更禁止)
# 出典: er052_output/writer_dev_risk_flagger_01/antenna_trial_01/antenna_prompts.py(+detectors/prompts_flagger.py
#       の COMMON_HEAD / COMMON_OUT)。antenna_system(level) = COMMON_HEAD + _ROLE + _V1 + _DEF + _V2
#       + final_paragraph(level) + COMMON_OUT。final_paragraph(L>=2) = _RANGE[2..L]の連結 + _CLOSING。
# ------------------------------------------------------------
_COMMON_HEAD = (
    'あなたは記事の校閲補助です。記事の各文を、根拠である台帳Fact(事実の一覧、記事全体の根拠)と照らし、人間が確認した方がよい箇所にFlagを立てます。合否判定・修正案の提示・書き換えはしません。\n'
    '入力はJSONで、facts(fact_id, text: 台帳の全Fact)と sentences(sid, text, before, after)です。判定対象は sentences の text だけです。factsは根拠として参照するだけで、判定対象ではありません。before/afterは文脈で、判定対象ではありません。台帳は日本語、記事の文は英語や日本語のことがあります。\n'
)

_COMMON_OUT = (
    '\n'
    '出力はJSON1個のみ(前後に説明文を付けない):\n'
    '{"flags":[{"sentence_id":"<sid>","type":"<タイプ名>","fact_ids":["<fact_id>"],"confidence":0.0-1.0,"severity":"重大|非重大","question":"人間向けの確認質問を日本語1文"}]}\n'
    'Flagが無ければ {"flags":[]}。sentence_idとfact_idsは入力に存在するIDのみ使うこと。questionは1文で、断定せず『〜ではありませんか』の形で、どの語とどの語が食い違うかを示す。\n'
)

_ROLE = (
    'あなたの役割は、台帳Factと食い違って読者に誤った事実を伝えうる『重大』な箇所だけを列挙することです。'
)

_V1 = (
    '軽微な言い換え・省略・表現の硬さ・文体の問題は出さないでください。'
)

_DEF = (
    '重大候補の例: rollback反転 / 主体対象入替 / 否定反転 / 数量時系列 / 不在断定(各タイプの定義: 動作の向きの反転、主体や対象や範囲の入替、肯定否定の反転、数値・日付・順序の変更、台帳にない不在の断定)。typeには上の5つのいずれか、当てはまらなければ『その他』。severityは常に『重大』。confidenceは正直に付けること: '
)

_V2 = (
    '疑いが小さくても重大の可能性が少しでもあれば低めの確信度(0.1〜0.4)で出してよい(人間に見せるかどうかは後で確信度の閾値で決める)。'
)

_RANGE_2 = (
    '台帳どおりの文は出さない。候補にするのは、(a) 台帳と明確に食い違う文に加えて、(b) 台帳の言い換え・要約・一般化・範囲の広げ縮めによって、台帳が述べているより強い意味、または別の範囲・意味に読める文。'
)

_RANGE_3 = (
    '(c) 台帳に対応するFactはあるが、数値・日付・固有名・主体・範囲・順序のどれかが台帳と一致しているか確認しきれない文。出すかどうか迷う場合は、出さない側ではなく出す側に倒し、確信度を低めに付ける。'
)

_RANGE_4 = (
    '(d) 台帳のどのFactにも対応する記述が見つからない事実の主張(数値・日付・固有名・因果・理由・仕組み・不在・断定のいずれかを含む文)。食い違いまでは言えず台帳で確認できないだけの文は、確信度を低く付ける。対応するFactが無い場合、fact_idsは空配列でよい。(e) 注意書き(ambiguity_note、conditions、notes_for_writerなど)が付いたFactに関わる文で、その注意書きが落ちて断定的に読める文。'
)

_CLOSING = (
    '\n'
    '出力件数に目標・下限・上限はありません。各文について『この文は人間に確認させる価値があるか』を自分で判断し、価値があると判断した文だけを出してください。該当する文が無ければ {"flags":[]} で構いません。'
)


def _system(level: int) -> str:
    ranges = {2: _RANGE_2, 3: _RANGE_3, 4: _RANGE_4}
    fp = "".join(ranges[k] for k in range(2, level + 1)) + _CLOSING
    return _COMMON_HEAD + _ROLE + _V1 + _DEF + _V2 + fp + _COMMON_OUT


A3_SYSTEM = _system(3)
A4_SYSTEM = _system(4)
A3_SYSTEM_SHA256 = "9d9950428419c3af824cc5b8676a4b564f96aeb87657c547d418cc86ef3538e9"
A4_SYSTEM_SHA256 = "c87b95e5bcf1b5c266b8978c5688849eb339a6087efbcaf56bb7399ed128ef01"
SYSTEM_BY_CONDITION = {"A3": A3_SYSTEM, "A4": A4_SYSTEM}


def sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# import時に固定shaと照合(Promptがdriftしたらimportできない=fail-closed)
assert sha256_text(A3_SYSTEM) == A3_SYSTEM_SHA256, "A3 system prompt sha drift"
assert sha256_text(A4_SYSTEM) == A4_SYSTEM_SHA256, "A4 system prompt sha drift"

# ------------------------------------------------------------
# 4条件・model定義
# ------------------------------------------------------------
MODEL_SPECS = {
    "luna": {"provider": "openai", "routing_key": "FAMILY_X_RF_LUNA", "model_id": "gpt-6-luna", "label": "Luna"},
    "gemini35fl": {"provider": "gemini", "routing_key": "FAMILY_X_RF_GEMINI", "model_id": "gemini-3.5-flash-lite",
                   "label": "Gemini 3.5 Flash-Lite"},
}
CONDITIONS = (("luna", "A3"), ("luna", "A4"), ("gemini35fl", "A3"), ("gemini35fl", "A4"))   # この順に逐次実行

# schema検証(run_flagger_01.validate_flags 相当)
TYPES = ["rollback反転", "主体対象入替", "否定反転", "数量時系列", "不在断定"]
CAUSAL_TYPE = "因果創作"
VALID_TYPES = tuple(TYPES) + (CAUSAL_TYPE, "その他")
VALID_SEVERITY = ("重大", "非重大")


class LedgerIncomplete(Exception):
    """台帳の見出し数と解析件数が一致しない(完全性assert失敗)。RF_UNAVAILABLE(ledger_incomplete)になる。"""

    def __init__(self, message: str, n_broad: int = 0, n_hdr: int = 0, n_parsed: int = 0, examples=None):
        super().__init__(message)
        self.n_broad, self.n_hdr, self.n_parsed, self.examples = n_broad, n_hdr, n_parsed, list(examples or [])


class BudgetCheckStop(RuntimeError):
    """呼出側から渡された budget_check が例外を出した(予算超過STOP等)。RFの非Blocking対象外で、必ず伝播する。"""


class ArticleModifiedError(RuntimeError):
    """RF実行中に記事ファイルのsha256が変わった(RFは記事を書き換えない契約の違反)。"""


# ------------------------------------------------------------
# 台帳parser(FIX01補正regex対応: `[AMBIGUOUS - note] FACT-ID: text` の見出し)
# 出典: post_en_trial_01/post_en_common.py HDR + detectors/ledger_restore_01.py parse_ledger_text
# ------------------------------------------------------------
LEDGER_HDR_RE = re.compile(r"^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$")


def parse_ledger_text(txt: str) -> list:
    """台帳テキスト -> [{fact_id, text}]。textはブロック全文(1行目の接頭辞は除去)。空行でブロック終端。"""
    facts, cur = [], None
    for ln in txt.splitlines():
        m = LEDGER_HDR_RE.match(ln)
        if m:
            cur = {"fact_id": m.group("id"), "lines": [m.group("text")]}
            facts.append(cur)
        elif cur is not None and ln.strip():
            cur["lines"].append(ln.rstrip())
        elif cur is not None and not ln.strip():
            cur = None
    return [{"fact_id": f["fact_id"], "text": "\n".join(f["lines"])} for f in facts]


def parse_ledger_complete(txt: str) -> list:
    """完全性assert付き。`[`で始まる行数 == 見出し(LEDGER_HDR_RE)行数 == 解析件数 かつ 1件以上。
    不一致は LedgerIncomplete(決定論: 同じ台帳テキストなら常に同じ結果)。"""
    lines = txt.splitlines()
    broad = [ln for ln in lines if ln.startswith("[")]
    hdr = [ln for ln in lines if LEDGER_HDR_RE.match(ln)]
    facts = parse_ledger_text(txt)
    if not (len(broad) == len(hdr) == len(facts)) or not facts:
        examples = [ln[:100] for ln in broad if not LEDGER_HDR_RE.match(ln)][:3]
        raise LedgerIncomplete(
            f"ledger_incomplete: broad={len(broad)} hdr={len(hdr)} parsed={len(facts)}",
            len(broad), len(hdr), len(facts), examples)
    return facts


# ------------------------------------------------------------
# 入力構築(POST-EN Trialと同一方式: facts全件 + 記事の全文を文分割。before/afterは空=LLM入力に文脈を入れない)
# ------------------------------------------------------------
def build_units(article_text: str, facts: list) -> dict:
    sents = [{"sid": sid, "text": t, "before": "", "after": ""} for sid, t in splitter.split_sentences_en(article_text)]
    return {"facts": [{"fact_id": f["fact_id"], "text": f["text"]} for f in facts], "sentences": sents}


def build_user(unit: dict) -> str:
    """LLMへ渡すuser入力(prompts_flagger.build_user と同一のJSON)。ラベル・出典パス等は渡さない。"""
    return json.dumps({
        "facts": [{"fact_id": f["fact_id"], "text": f["text"]} for f in unit["facts"]],
        "sentences": [{"sid": s["sid"], "text": s["text"], "before": s.get("before", ""), "after": s.get("after", "")}
                      for s in unit["sentences"]],
    }, ensure_ascii=False)


def validate_flags(text: str, unit: dict):
    """戻り値 (flags_or_None, violations)。run_flagger_01.validate_flags(d2モード)相当。"""
    try:
        obj = json.loads(text)
    except Exception as e:  # noqa: BLE001
        m = re.search(r"\{.*\}", text or "", flags=re.S)   # 前後に文が付いた場合の救済(1回だけ)
        if not m:
            return None, ["json_parse_error:%s" % type(e).__name__]
        try:
            obj = json.loads(m.group(0))
        except Exception:  # noqa: BLE001
            return None, ["json_parse_error:%s" % type(e).__name__]
    if not isinstance(obj, dict) or not isinstance(obj.get("flags"), list):
        return None, ["flags_missing"]
    sids = {s["sid"] for s in unit["sentences"]}
    fids = {f["fact_id"] for f in unit["facts"]}
    v, out = [], []
    for i, fl in enumerate(obj["flags"]):
        if not isinstance(fl, dict):
            v.append("flag%d_not_object" % i)
            continue
        n0 = len(v)
        if fl.get("sentence_id") not in sids:
            v.append("flag%d_sentence_id_invalid" % i)
        typ = fl.get("type")
        if typ not in VALID_TYPES:
            v.append("flag%d_type_invalid" % i)
        if fl.get("severity") not in VALID_SEVERITY:
            v.append("flag%d_severity_invalid" % i)
        c = fl.get("confidence")
        if isinstance(c, bool) or not isinstance(c, (int, float)) or not 0 <= c <= 1:
            v.append("flag%d_confidence_invalid" % i)
        q = fl.get("question")
        if not isinstance(q, str) or not q.strip():
            v.append("flag%d_question_missing" % i)
        fi = fl.get("fact_ids")
        if not isinstance(fi, list) or any(x not in fids for x in fi):
            v.append("flag%d_fact_ids_invalid" % i)
        if len(v) == n0:
            out.append({"sentence_id": fl["sentence_id"], "type": typ, "fact_ids": list(fi),
                        "confidence": round(float(c), 2), "severity": fl["severity"], "question": q.strip()})
    if v:
        return None, v
    return out, []


# ------------------------------------------------------------
# 単価・費用(fail-closed: 未登録はPricingNotFoundError、0円扱いにしない)
# ------------------------------------------------------------
def load_prices(model_id: str, provider: str, pricing_path: str = PRICING_SNAPSHOT_PATH) -> dict:
    """Standard tierの {input_tokens, cached_input_tokens, output_tokens} (USD/1M tokens)。
    input/outputのいずれかが未登録なら PricingNotFoundError。cachedが未登録ならinput単価を使う(安全側)。"""
    with open(pricing_path, encoding="utf-8") as f:
        prices = json.load(f)["prices"]
    got = {}
    for p in prices:
        if p.get("provider") == provider and p.get("model") == model_id and p.get("tier", "Standard") == "Standard":
            got[p.get("meter")] = p.get("price")
    for meter in ("input_tokens", "output_tokens"):
        if meter not in got:
            raise routing.PricingNotFoundError(f"[STOP] 単価未登録model: {provider}/{model_id} meter={meter}")
    got.setdefault("cached_input_tokens", got["input_tokens"])
    return got


def cost_jpy(prices: dict, input_tokens: int, output_tokens: int, cached_tokens: int = 0) -> float:
    """G-2式: (非cached input)×in + cached×cached単価 + output(thinking含む)×out、円換算 ×USD_JPY。"""
    cached = min(cached_tokens or 0, input_tokens or 0)
    usd = (((input_tokens or 0) - cached) * prices["input_tokens"] + cached * prices["cached_input_tokens"]
           + (output_tokens or 0) * prices["output_tokens"]) / 1e6
    return usd * USD_JPY


# ------------------------------------------------------------
# Provider adapter(API呼出部。testではstubを差し替える)
# ------------------------------------------------------------
def build_request(model_key: str, model_id: str, system: str, user: str):
    """(endpoint, extra_headers(秘密なし), body)。dry-runと実呼出に同じ関数を使う。xm_driver.build_requestの移植。"""
    p = MODEL_SPECS[model_key]["provider"]
    if p == "openai":
        return ("openai-sdk:responses.create", {},
                {"model": model_id, "instructions": system, "input": user,
                 "reasoning": {"effort": EFFORT}, "max_output_tokens": MAX_OUT})
    if p == "gemini":    # thinkingConfig/temperature/responseMimeTypeは送らない(Provider既定)
        return ("https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % model_id,
                {"content-type": "application/json"},
                {"systemInstruction": {"parts": [{"text": system}]},
                 "contents": [{"role": "user", "parts": [{"text": user}]}],
                 "generationConfig": {"maxOutputTokens": MAX_OUT}})
    raise ValueError(p)


def parse_gemini_response(j: dict):
    """-> (text, usage, response_id, model_id_returned)。output_tokens = candidates + thoughts(thinking込み)。"""
    cands = j.get("candidates") or [{}]
    parts = (cands[0].get("content") or {}).get("parts", [])
    txt = "".join(x.get("text", "") for x in parts if not x.get("thought"))
    u = j.get("usageMetadata", {})
    th = u.get("thoughtsTokenCount", 0) or 0
    usage = {"input_tokens": u.get("promptTokenCount", 0) or 0,
             "output_tokens": (u.get("candidatesTokenCount", 0) or 0) + th,
             "reasoning_tokens": th,
             "cached_tokens": u.get("cachedContentTokenCount", 0) or 0,
             "finish_reason": cands[0].get("finishReason")}
    return txt, usage, j.get("responseId"), j.get("modelVersion")


def _load_env():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:  # noqa: BLE001
        pass


def _key(name: str) -> str:
    k = os.environ.get(name)
    if not k:
        _load_env()
        k = os.environ.get(name)
    if not k:
        raise RuntimeError("環境変数 %s が未設定(値は出力しない)" % name)
    return k


def default_call_fn(model_key: str, model_id: str, system: str, user: str):
    """実API呼出(C1ではtestから呼ばない)。戻り値 (text, usage, response_id, model_id_returned)。
    Luna=OpenAI SDK(SDK patchが自動で費用記録)。Gemini=REST(本moduleがcl.recordする: _record_gemini_cost)。"""
    endpoint, hdr, body = build_request(model_key, model_id, system, user)
    if MODEL_SPECS[model_key]["provider"] == "openai":
        from openai import OpenAI
        resp = OpenAI(api_key=_key("OPENAI_API_KEY")).responses.create(**body)
        u = resp.usage
        usage = {"input_tokens": getattr(u, "input_tokens", None) or 0,
                 "output_tokens": getattr(u, "output_tokens", None) or 0,
                 "reasoning_tokens": getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", None),
                 "cached_tokens": getattr(getattr(u, "input_tokens_details", None), "cached_tokens", None) or 0}
        return resp.output_text, usage, resp.id, getattr(resp, "model", model_id)
    import requests
    h = dict(hdr)
    h["x-goog-api-key"] = _key("GEMINI_API_KEY")
    r = requests.post(endpoint, headers=h, json=body, timeout=HTTP_TIMEOUT)
    try:
        j = r.json()
    except Exception:  # noqa: BLE001
        j = {"_non_json": r.text[:500]}
    if r.status_code != 200:
        raise RuntimeError("HTTP %s: %s" % (r.status_code, json.dumps(j, ensure_ascii=False)[:300]))
    return parse_gemini_response(j)


def _record_gemini_cost(model_id: str, usage: dict, response_id, elapsed: float, attempt: int, success: bool, error: str = None,
                        prices: dict = None):
    """GeminiはSDK patchの外(REST)なので、er005_cost_logger互換レコードを本moduleが書く(Lunaは書かない)。
    logger未初期化(init_logger未呼出)でもRFは止めない(戻り値でwarningを返す)。"""
    entry = {"provider": "gemini", "api": "rest.generateContent(text)", "model_id": model_id,
             "response_id": response_id, "attempt_number": attempt, "success": success,
             "elapsed_seconds": round(elapsed, 3),
             "usage_source": "OFFICIAL_API_RESPONSE" if success else "N/A_FAILED_CALL"}
    if success:
        entry.update({"input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
                      "total_tokens": (usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0),
                      "cached_input_tokens": usage.get("cached_tokens"),
                      "reasoning_tokens": usage.get("reasoning_tokens")})
        if prices is not None:
            # C3-2(G-4): audio側compute_cost_jpy_so_farは cost_usd があればそれを実額として採用する。
            # model_idは pinned model(単価キー)、output_tokensはthinking込み、cost_usdはG-2式(cached割引込み)。
            entry["cost_usd"] = cost_jpy(prices, usage.get("input_tokens") or 0, usage.get("output_tokens") or 0,
                                         usage.get("cached_tokens") or 0) / USD_JPY
    else:
        entry["error"] = (error or "")[:500]
    try:
        cl.record(entry)
        return None
    except Exception as e:  # noqa: BLE001
        return "cost_logger_record_failed: %s" % type(e).__name__


# ------------------------------------------------------------
# 1条件の実行(技術retry: transient 2 / format 1。RF結果で分岐するretryは無い)
# ------------------------------------------------------------
def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def run_condition(model_key, condition, level, model_id, unit, user, prices, call_fn, sleep_fn, budget_check, raw_out, warnings):
    system = SYSTEM_BY_CONDITION[condition]
    provider = MODEL_SPECS[model_key]["provider"]
    stage = "risk_flag.%s.%s.%s" % (model_key, condition, level)
    cond = {"model_key": model_key, "condition": condition, "article_level": level,
            "model_id_requested": model_id, "model_id_returned": None, "provider": provider,
            "status": "RF_UNAVAILABLE", "reason": None, "api_calls": 0, "input_tokens": 0, "output_tokens": 0,
            "cached_tokens": 0, "cost_jpy": 0.0, "flag_count": 0, "response_ids": [],
            "system_prompt_sha256": sha256_text(system), "model_mismatch": False, "elapsed_s": 0.0}
    flags, fmt_used, trans_used = None, 0, 0
    t_start = time.time()
    attempt_no = 0
    while True:
        if budget_check is not None:       # 予算超過STOPは握りつぶさず伝播(既存安全装置を回避しない)
            try:
                budget_check()
            except Exception as e:  # noqa: BLE001
                raise BudgetCheckStop(f"{type(e).__name__}: {e}") from e
        attempt_no += 1
        ts = _now()
        t0 = time.time()
        with cl.logging_context(THEME_TAG, stage):
            try:
                text, usage, rid, mid = call_fn(model_key, model_id, system, user)
            except Exception as e:  # noqa: BLE001
                el = time.time() - t0
                if provider == "gemini":
                    w = _record_gemini_cost(model_id, {}, None, el, attempt_no, False, f"{type(e).__name__}: {e}")
                    if w:
                        warnings.append(w)
                raw_out.append({"model_key": model_key, "condition": condition, "attempt": attempt_no, "ts": ts,
                                "error": f"{type(e).__name__}: {str(e)[:300]}"})
                if trans_used < TRANSIENT_RETRIES:
                    trans_used += 1
                    sleep_fn(2 * trans_used)
                    continue
                cond["reason"] = f"transient_exhausted: {type(e).__name__}"
                break
            el = time.time() - t0
            if provider == "gemini":
                w = _record_gemini_cost(model_id, usage, rid, el, attempt_no, True, prices=prices)
                if w:
                    warnings.append(w)
        cond["api_calls"] += 1
        in_t, out_t, c_t = usage.get("input_tokens") or 0, usage.get("output_tokens") or 0, usage.get("cached_tokens") or 0
        c = cost_jpy(prices, in_t, out_t, c_t)
        cond["input_tokens"] += in_t
        cond["output_tokens"] += out_t
        cond["cached_tokens"] += c_t
        cond["cost_jpy"] += c
        cond["model_id_returned"] = mid
        if rid:
            cond["response_ids"].append(rid)
        if mid and not str(mid).startswith(model_id):
            cond["model_mismatch"] = True
            warnings.append(f"model_id_mismatch: {model_key}/{condition} requested={model_id} returned={mid}")
        got, viol = validate_flags(text, unit)
        raw_out.append({"model_key": model_key, "condition": condition, "attempt": attempt_no, "ts": ts,
                        "system_prompt_sha256": cond["system_prompt_sha256"], "response_text": text, "usage": usage,
                        "response_id": rid, "model_id": mid, "violations": viol, "cost_jpy": c})
        if got is not None:
            flags = got
            break
        if fmt_used < FORMAT_RETRIES:
            fmt_used += 1
            continue
        cond["reason"] = "format_invalid: " + ";".join(viol[:3])
        break
    cond["elapsed_s"] = round(time.time() - t_start, 2)
    if flags is not None:
        cond["status"] = "OK"
        cond["flag_count"] = len(flags)
    cond["cost_jpy"] = round(cond["cost_jpy"], 6)
    return cond, (flags or [])


# ------------------------------------------------------------
# OR統合・重複統合(キー article_id + article_level + sentence_id)
# ------------------------------------------------------------
def merge_issues(article_id: str, level: str, unit: dict, per_condition_flags: list) -> list:
    """per_condition_flags: [(cond_dict, flags)]。同一文のA3/A4・Luna/Geminiは1 issueへOR統合し、
    detected_by[]に model×A3/A4×confidence を保持(raw応答はqueue側のraw/に別途保持)。"""
    order = {s["sid"]: i for i, s in enumerate(unit["sentences"])}
    text_by = {s["sid"]: s["text"] for s in unit["sentences"]}
    merged = {}
    for cond, flags in per_condition_flags:
        for fl in flags:
            sid = fl["sentence_id"]
            it = merged.setdefault(sid, {
                "article_id": article_id, "article_level": level, "sentence_id": sid, "sentence_text": text_by[sid],
                "related_fact_ids": [], "flag_reasons": [], "detected_by": [], "confidence": 0.0})
            for fid in fl["fact_ids"]:
                if fid not in it["related_fact_ids"]:
                    it["related_fact_ids"].append(fid)
            reason = {"type": fl["type"], "question": fl["question"]}
            if reason not in it["flag_reasons"]:
                it["flag_reasons"].append(reason)
            it["detected_by"].append({
                "model_key": cond["model_key"], "model_id": cond["model_id_returned"] or cond["model_id_requested"],
                "condition": cond["condition"], "confidence": fl["confidence"], "type": fl["type"],
                "fact_ids": list(fl["fact_ids"]), "question": fl["question"], "severity": fl["severity"]})
            it["confidence"] = max(it["confidence"], fl["confidence"])
    return [merged[k] for k in sorted(merged, key=lambda s: order[s])]


def compute_model_stats(level: str, conditions: list, issues: list, status: str) -> dict:
    """この1記事×1Levelの MODEL_STATS(model別)。Level別・記事横断の集計は aggregate_model_stats()。"""
    stats = {}
    for mk in MODEL_SPECS:
        cs = [c for c in conditions if c["model_key"] == mk]
        ok = [c for c in cs if c["status"] == "OK"]
        sids_by_cond = {c["condition"]: set() for c in cs}
        for it in issues:
            for d in it["detected_by"]:
                if d["model_key"] == mk:
                    sids_by_cond.setdefault(d["condition"], set()).add(it["sentence_id"])
        a3, a4 = sids_by_cond.get("A3", set()), sids_by_cond.get("A4", set())
        n_flags = {cd: sum(c["flag_count"] for c in ok if c["condition"] == cd) for cd in ("A3", "A4")}
        stats[mk] = {
            "article_level": level, "articles_processed": 1 if cs else 0,
            "conditions_ok": len(ok), "conditions_unavailable": len(cs) - len(ok),
            "article_unavailable": 1 if cs and not ok else 0, "article_partial": 1 if cs and ok and len(ok) < len(cs) else 0,
            "api_calls": sum(c["api_calls"] for c in cs), "input_tokens": sum(c["input_tokens"] for c in cs),
            "output_tokens": sum(c["output_tokens"] for c in cs), "cost_jpy": round(sum(c["cost_jpy"] for c in cs), 6),
            "a3_flag_count": n_flags["A3"], "a4_flag_count": n_flags["A4"],
            "unique_issue": len(a3 | a4), "overlap_a3_a4": len(a3 & a4),
            "zero_flag_article": 1 if ok and not (a3 | a4) else 0,
        }
    stats["_all"] = {"article_level": level, "article_status": status, "unique_issue": len(issues),
                     "cost_jpy": round(sum(c["cost_jpy"] for c in conditions), 6),
                     "issues_by_both_models": sum(1 for it in issues if {d["model_key"] for d in it["detected_by"]} == set(MODEL_SPECS))}
    return stats


def aggregate_model_stats(per_run_stats: list) -> dict:
    """[(article_level, model_stats_dict)...] -> {level: {model_key: 合計}}。"""
    out = {}
    for level, st in per_run_stats:
        for mk, row in st.items():
            if mk.startswith("_"):
                continue
            agg = out.setdefault(level, {}).setdefault(mk, {})
            for k, v in row.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    agg[k] = agg.get(k, 0) + v
    return out


# ------------------------------------------------------------
# entry_point.json への記録(RF_UNAVAILABLE/PARTIAL/OK の可視化。原子的書込)
# ------------------------------------------------------------
def record_to_entry_point(out_dir: str, result: dict):
    """out_dir/entry_point.json の "risk_flagger"[level] に要約を書く(既存キーは変更しない)。失敗しても例外は伝播しない。"""
    try:
        p = os.path.join(out_dir, "entry_point.json")
        data = {}
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
        summ = {k: result.get(k) for k in ("status", "reason", "rf_run_id", "article_sha256", "ledger_sha256",
                                           "splitter_version", "timestamp", "producer", "run_label")}
        summ["issue_count"] = len(result.get("issues", []))
        summ["conditions"] = [{k: c.get(k) for k in ("model_key", "condition", "status", "reason", "flag_count", "cost_jpy")}
                              for c in result.get("conditions", [])]
        data.setdefault("risk_flagger", {})[result["article_level"]] = summ
        os.makedirs(out_dir, exist_ok=True)
        tmp = p + ".tmp%d" % os.getpid()
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, p)
        return None
    except Exception as e:  # noqa: BLE001
        return "entry_point_record_failed: %s" % type(e).__name__


def new_rf_run_id() -> str:
    return "rf%s-%s" % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), secrets.token_hex(2))


# ------------------------------------------------------------
# メインAPI(非Blocking: API/台帳/単価の問題は RF_UNAVAILABLE として返し、例外にしない)
# ------------------------------------------------------------
def run_risk_flagger(*, article_path: str, ledger_path: str, article_id: str, article_level: str, out_dir: str = None,
                     call_fn=None, rf_run_id: str = None, sleep_fn=time.sleep, pricing_path: str = PRICING_SNAPSHOT_PATH,
                     budget_check=None, producer: str = None, run_label: str = None, dry_run: bool = False,
                     record_entry_point: bool = True) -> dict:
    """1記事×1Levelに対して4条件を逐次実行し、OR統合した結果dictを返す。

    戻り値の status: OK(4条件とも成功) / PARTIAL(一部成功) / RF_UNAVAILABLE(全滅・台帳不完全・単価未登録など)。
    記事は書き換えない(開始時と終了時のsha256を比較し、変わっていたら ArticleModifiedError)。
    budget_check: 呼出前に毎回呼ぶcallable(例 efam.assert_budget_ok のラッパ)。例外はそのまま伝播する(予算STOPを回避しない)。
    dry_run=True: API呼出なし。入力・request本体・見積に必要な情報だけ返す。"""
    if article_level not in LEVELS:
        raise ValueError("article_level must be one of %s" % (LEVELS,))
    call_fn = call_fn or default_call_fn
    rf_run_id = rf_run_id or new_rf_run_id()
    warnings = []
    if cl._CONTEXT.get("stage") is not None or cl._CONTEXT.get("theme") is not None:
        warnings.append("called_inside_logging_context: RFは cl.logging_context ブロックの外で呼ぶ契約(stage tagは条件ごとに自前contextで上書きする)")
    with open(article_path, "rb") as f:
        article_bytes = f.read()
    article_sha = sha256_bytes(article_bytes)
    result = {"schema_version": SCHEMA_VERSION, "article_id": article_id, "article_level": article_level,
              "article_sha256": article_sha, "article_path": article_path, "ledger_path": ledger_path,
              "ledger_sha256": None, "rf_run_id": rf_run_id, "timestamp": _now(), "status": "RF_UNAVAILABLE",
              "reason": None, "splitter_version": splitter.SPLITTER_VERSION, "producer": producer, "run_label": run_label,
              "sentences": [], "facts": [], "conditions": [], "issues": [], "unlocated_flags": [], "raw": [],
              "model_stats": {}, "warnings": warnings, "dry_run": dry_run}
    try:
        article_text = article_bytes.decode("utf-8")
        with open(ledger_path, "rb") as f:
            ledger_bytes = f.read()
        result["ledger_sha256"] = sha256_bytes(ledger_bytes)
        result["ledger_text"] = ledger_bytes.decode("utf-8")
        try:
            facts = parse_ledger_complete(result["ledger_text"])
        except LedgerIncomplete as e:
            result["reason"] = "ledger_incomplete"
            result["ledger_incomplete_detail"] = {"n_broad": e.n_broad, "n_hdr": e.n_hdr, "n_parsed": e.n_parsed, "examples": e.examples}
            raise
        unit = build_units(article_text, facts)
        if not unit["sentences"]:
            result["reason"] = "no_sentences"
            raise ValueError("no_sentences")
        result["sentences"] = unit["sentences"]
        result["facts"] = unit["facts"]
        user = build_user(unit)
        result["user_sha256"] = sha256_text(user)
        # model contract / 単価: いずれも**最初のAPI呼出より前**に検証(fail-closed。Gemini単価が未登録ならRFは1回も呼ばない)
        model_ids, prices = {}, {}
        for mk, spec in MODEL_SPECS.items():
            model_ids[mk] = routing.require_model(spec["routing_key"], spec["model_id"])
            prices[mk] = load_prices(model_ids[mk], spec["provider"], pricing_path)
        result["requests"] = {f"{mk}.{cd}": {"endpoint": build_request(mk, model_ids[mk], SYSTEM_BY_CONDITION[cd], user)[0],
                                              "system_prompt_sha256": sha256_text(SYSTEM_BY_CONDITION[cd]), "model_id": model_ids[mk]}
                              for mk, cd in CONDITIONS}
        if dry_run:
            result["status"], result["reason"] = "DRY_RUN", None
            return result
        per = []
        for mk, cd in CONDITIONS:             # 逐次(並列化しない)
            cond, flags = run_condition(mk, cd, article_level, model_ids[mk], unit, user, prices[mk], call_fn, sleep_fn,
                                        budget_check, result["raw"], warnings)
            result["conditions"].append(cond)
            per.append((cond, flags))
        ok = [c for c in result["conditions"] if c["status"] == "OK"]
        result["status"] = "OK" if len(ok) == len(CONDITIONS) else ("PARTIAL" if ok else "RF_UNAVAILABLE")
        if result["status"] != "OK":
            result["reason"] = "; ".join(f"{c['model_key']}.{c['condition']}:{c['reason']}" for c in result["conditions"] if c["status"] != "OK")
        result["issues"] = merge_issues(article_id, article_level, unit, per)
        result["model_stats"] = compute_model_stats(article_level, result["conditions"], result["issues"], result["status"])
    except (routing.ModelContractViolation, routing.PricingNotFoundError) as e:
        result["status"] = "RF_UNAVAILABLE"
        result["reason"] = result["reason"] or ("model_contract_violation" if isinstance(e, routing.ModelContractViolation) else "pricing_not_found")
        result["error_detail"] = str(e)[:300]
    except BudgetCheckStop:
        raise
    except Exception as e:  # noqa: BLE001  非Blocking: 想定外もRF_UNAVAILABLEとして可視化
        result["status"] = "RF_UNAVAILABLE"
        result["reason"] = result["reason"] or ("unexpected_exception: %s" % type(e).__name__)
        result["error_detail"] = str(e)[:300]
    # 記事sha不変assert(RFは記事を書き換えない)
    with open(article_path, "rb") as f:
        after = sha256_bytes(f.read())
    if after != article_sha:
        raise ArticleModifiedError(f"article sha changed during RF: {article_sha} -> {after} ({article_path})")
    if not result["model_stats"]:
        result["model_stats"] = compute_model_stats(article_level, result["conditions"], result["issues"], result["status"])
    if result["status"] in ("RF_UNAVAILABLE", "PARTIAL"):
        print("[WARN][RF] %s article_id=%s level=%s reason=%s (非Blocking: 次工程へ進みます)"
              % (result["status"], article_id, article_level, result["reason"]))
    if out_dir and record_entry_point and not dry_run:
        w = record_to_entry_point(out_dir, result)
        if w:
            warnings.append(w)
    return result
