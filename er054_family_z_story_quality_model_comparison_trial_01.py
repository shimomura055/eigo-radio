# -*- coding: utf-8 -*-
"""FAMILY-Z-STORY-QUALITY-MODEL-COMPARISON-TRIAL-01 委任_01: Story品質評価方式A〜D比較Trial専用driver。

【状態】委任_01は設計・乾式(--mode mock)・費用見積(--mode estimate)のみ。--mode real は有料APIのため
        --approved-budget-jpy(ユーザー承認の費用上限)が無いと起動しない。委任_01では未実行。
【範囲】Trial専用(到達上限VALIDATED)。Family Z Production・Writer/Prompt/Routing・既存Story Pool正式仕様は変更しない。
        Production runnerからimportされない。Trial routing key FAMILY_Z_TRIAL_STORY_QUALITY_EVAL(gpt-6-luna)を流用(Production key不変)。
【Blind】前回Luna評価結果(PHASE_C_RESULTS_02 / phase_c_eval / SEALED_PAST_RESULTS_L01_L06 等)は本driverから読まない(deny guard)。
        過去評価はPromptにも入れない。
【並列】方式×作品×rep を1taskとし、taskごとに別ファイルへ書く(同一ファイル書込みなし)。累計費用は lock で保護。
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import er054_family_z_story_pool_trial_common_01 as common

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_POOL = os.path.join(ROOT, "er054_output", "family_z_story_pool_trial_01")
SRC = os.path.join(BASE_POOL, "sources")
SCREEN = os.path.join(BASE_POOL, "screening")
OUT_BASE = os.path.join(ROOT, "er054_output", "family_z_story_quality_model_comparison_trial_01")
PROMPT_DIR = os.path.join(OUT_BASE, "prompts")
PRICING_SNAPSHOT = os.path.join(ROOT, "er005_output", "cost_baseline_01", "pricing_snapshot.json")
USD_JPY = 160.0

ROUTING_KEY = common.KEY_QUALITY                      # Trial専用key(Production key不変)
PRIMARY_MODEL = common.resolve_trial_model(ROUTING_KEY)  # gpt-6-luna
ALLOWED_MODELS = (PRIMARY_MODEL,)
REASONING_EFFORT = "medium"                           # 全方式同一(temperature系は推論モデルのため指定しない)
EVAL_VERSION = "family_z_story_quality_model_comparison_v1"

METHODS = ("A", "B", "C", "D")
WORKS = ("L01", "L02", "L03", "L04", "L05", "L07", "L08", "L09", "L10")  # L06除外
SRC_DIR = {"L04": "L04_ru"}
LANG = {"L04": "ロシア語(原語原作)"}

# 方式ごとの採点軸キー(schema_method_*_v1.json と整合。testで検証)
AXES = {
    "A": ("A", "B", "C", "D"),
    "B": ("A", "B", "C", "D"),
    "C": ("hook", "development", "aftertaste", "originality"),
    "D": ("extractability", "loss_severity", "reproducibility", "style_independence"),
}
SCORE_METHODS = ("A", "C", "D")  # 1〜5点方式。Bは verdict(PASS/WEAK/FAIL)

# 封印(Blind): 前回のLuna評価結果・封印済み過去評価。新driverは読まない。
SEALED_DENY = ("SEALED_PAST_RESULTS", "PHASE_C_RESULTS", "PHASE_C_EVAL", "PHASE_C_COST", "PHASE_D_COMPARISON",
               "phase_c_eval", "phase_c_dry_run", "STORY_POOL_01", "SCREENING_TABLE", "RESULT_01.md")


class SealedAccessError(RuntimeError):
    pass


def assert_not_sealed(path: str) -> str:
    p = str(path).replace("\\", "/")
    for n in SEALED_DENY:
        if n.lower() in p.lower():
            raise SealedAccessError(f"STOP(Blind): 封印対象(前回評価結果/過去評価)の読込は禁止: {path}")
    return path


# ------------------------------------------------------------ Prompt(方式別md + 共通骨子)
DEVELOPER_BASE = (
    "あなたは英語学習マガジンのFiction編集部の評価者である。与えられた『原作本文』だけを根拠に、"
    "その作品を『英語の短編(280〜420語、A2〜B1向け)へ再話するための素材』として評価する。"
    "作品の知名度・評判・過去の評価・あなたの記憶に頼らず、本文に書かれていることだけで判断すること。"
    "引用(evidence_quotes)は本文中の連続した文字列をそのままコピーしたものに限る"
    "(言い換え・要約・結合・省略記号は禁止。ロシア語本文の引用はロシア語のままコピーし、日本語に訳さない)。"
    "1個あたり60文字(英語・ロシア語は25語)以内。出力は指定のJSONのみ。"
)

USER_FRAME = """[評価対象]
作品ID: {work_id}
タイトル: {title}
言語: {lang}
本文の長さ: {size_note}

{criteria}

[原作本文(原文のまま、要約・省略なし)]
<<<BEGIN_SOURCE_TEXT
{text}
END_SOURCE_TEXT>>>"""


def _section(md: str, name: str) -> str:
    m = re.search(rf"^## {name}\s*\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    if not m:
        raise RuntimeError(f"STOP: promptに## {name} セクションが無い")
    return m.group(1).strip()


def load_method(method: str) -> dict:
    if method not in METHODS:
        raise RuntimeError(f"unknown method {method}")
    with open(os.path.join(PROMPT_DIR, f"method_{method}_v1.md"), encoding="utf-8") as f:
        md = f.read()
    with open(os.path.join(PROMPT_DIR, f"schema_method_{method}_v1.json"), encoding="utf-8") as f:
        schema = json.load(f)
    return {"method": method, "developer": DEVELOPER_BASE + "\n" + _section(md, "DEVELOPER_ADDENDUM"),
            "criteria": _section(md, "USER_CRITERIA"), "schema": schema}


def build_unit(wid: str) -> dict:
    if wid not in WORKS:
        raise RuntimeError(f"STOP: {wid} は比較対象外(L06除外)")
    p = assert_not_sealed(os.path.join(SRC, SRC_DIR.get(wid, wid), "text_plain.txt"))
    with open(p, encoding="utf-8") as f:
        text = f.read().strip()
    chars = len(re.sub(r"\s", "", text))
    return {"work_id": wid, "text": text, "chars_no_ws": chars, "lang": LANG.get(wid, "日本語"), "size_note": f"約{chars}文字"}


def load_title(wid: str) -> str:
    """screening JSONからtitle_jaのみ取得(他キーは使わない)。"""
    with open(assert_not_sealed(os.path.join(SCREEN, f"{wid}.json")), encoding="utf-8") as f:
        return json.load(f)["title_ja"]


def build_messages(m: dict, unit: dict, title: str) -> list:
    user = USER_FRAME.format(work_id=unit["work_id"], title=title, lang=unit["lang"], size_note=unit["size_note"],
                             criteria=m["criteria"], text=unit["text"])
    return [{"role": "developer", "content": m["developer"]}, {"role": "user", "content": user}]


# ------------------------------------------------------------ 決定論の検証
def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", "", s)


def verify_quotes(method: str, parsed: dict, source_text: str) -> dict:
    """引用が原文の連続文字列か(文字列一致)のみを決定論で検証。原作理解の誤りとは別物(分析側で区別)。"""
    src = normalize_ws(source_text)
    per = {ax: [normalize_ws(q) in src for q in parsed[ax]["evidence_quotes"]] for ax in AXES[method]}
    total = sum(len(v) for v in per.values())
    bad = sum(v.count(False) for v in per.values())
    return {"per_axis": per, "quote_total": total, "unverified_quote_count": bad, "all_verified": bad == 0}


def validate_parsed(method: str, parsed: dict, schema: dict) -> None:
    props = schema["schema"]["properties"]
    for k in schema["schema"]["required"]:
        if k not in parsed:
            raise ValueError(f"missing key: {k}")
    for ax in AXES[method]:
        if ax not in props:
            raise ValueError(f"axis {ax} not in schema")
        if method == "B":
            if parsed[ax]["verdict"] not in ("PASS", "WEAK", "FAIL"):
                raise ValueError(f"bad verdict {ax}")
        else:
            if parsed[ax]["score"] not in (1, 2, 3, 4, 5):
                raise ValueError(f"bad score {ax}")


# ------------------------------------------------------------ 費用(単価はpricing_snapshot、他model流用禁止)
def load_prices(model: str) -> dict:
    with open(PRICING_SNAPSHOT, encoding="utf-8", errors="replace") as f:
        snap = json.load(f)
    pr = {}
    for p in snap["prices"]:
        if p["model"] == model and p.get("tier") == "Standard" and p["meter"] in ("input_tokens", "cached_input_tokens", "output_tokens"):
            pr[p["meter"]] = p["price"]
    if len(pr) < 3:
        raise RuntimeError(f"STOP: {model} の単価が未登録。他modelの流用は禁止。")
    return pr


def cost_jpy(pr: dict, in_tok: int, out_tok: int) -> float:
    return (in_tok / 1e6 * pr["input_tokens"] + out_tok / 1e6 * pr["output_tokens"]) * USD_JPY


# 前回Trialの実測入力トークン(作品別。前回usage実績の数値のみ転記。評価内容は含まない)。方式別Prompt差分(+tok)を加算して見積に使う。
MEASURED_INPUT_TOK = {"L01": 9929, "L02": 6110, "L03": 5953, "L04": 5309, "L05": 5981, "L07": 6413, "L08": 8253, "L09": 5101, "L10": 6691}
METHOD_PROMPT_DELTA_TOK = {"A": 700, "B": 900, "C": 700, "D": 900}      # 前回promptより基準文が長い分の想定
METHOD_OUT_TOK_POINT = {"A": 2200, "B": 2800, "C": 2200, "D": 3000}     # 前回実績1,780〜2,147(平均約1,974)を基準に出力量で補正
CAP_FACTOR = 1.5
SEC_PER_CALL = {"A": 20, "B": 25, "C": 20, "D": 27}                     # 前回実績15〜18秒/回を基準


def estimate(n_reps: int, works=WORKS, methods=METHODS) -> dict:
    pr = load_prices(PRIMARY_MODEL)
    per_method, tot = {}, 0.0
    for m in methods:
        rows = {w: round(cost_jpy(pr, MEASURED_INPUT_TOK[w] + METHOD_PROMPT_DELTA_TOK[m], METHOD_OUT_TOK_POINT[m]), 4) for w in works}
        one_pass = sum(rows.values())
        per_method[m] = {"per_work_per_call_jpy": rows, "one_rep_total_jpy": round(one_pass, 3),
                         "n_reps_total_jpy": round(one_pass * n_reps, 3), "cap_x1_5_jpy": round(one_pass * n_reps * CAP_FACTOR, 3),
                         "calls": len(works) * n_reps}
        tot += one_pass * n_reps
    return {"n_reps": n_reps, "prices_usd_per_1m": pr, "usd_jpy": USD_JPY, "per_method": per_method,
            "total_point_jpy": round(tot, 3), "total_cap_jpy": round(tot * CAP_FACTOR, 3),
            "calls": len(works) * len(methods) * n_reps}


def per_call_cap_jpy(method: str, wid: str) -> float:
    pr = load_prices(PRIMARY_MODEL)
    return cost_jpy(pr, MEASURED_INPUT_TOK[wid] + METHOD_PROMPT_DELTA_TOK[method], METHOD_OUT_TOK_POINT[method]) * CAP_FACTOR


# ------------------------------------------------------------ モックclient(乾式。API呼出なし)
class MockClient:
    """OpenAI Responses API互換の最小モック。method/work/repで決定論的にスコアを変え(分析scriptの動作確認用)、
    引用は本文から連続文字列を切り出す。bad_quote=Trueなら原文に無い引用を返す。"""
    def __init__(self, bad_quote: bool = False, force_contradiction: bool = True):
        self.calls = 0
        self.bad_quote = bad_quote
        self.force_contradiction = force_contradiction
        self._lock = threading.Lock()
        self.responses = self

    def create(self, **kw):
        with self._lock:
            self.calls += 1
        user = kw["input"][1]["content"]
        method = re.search(r"\[方式(.)", user).group(1)
        wid = re.search(r"作品ID: (L\d\d)", user).group(1)
        body = user.split("<<<BEGIN_SOURCE_TEXT\n", 1)[1].split("\nEND_SOURCE_TEXT>>>", 1)[0].replace("\n", "")
        rep_noise = random.Random(f"{method}-{wid}-{threading.get_ident() % 2}-{self.calls % 3}")  # rep間のゆらぎ(非決定でよい乾式用)
        base = random.Random(f"{method}-{wid}")
        q = lambda i: "this quote is not in the source" if self.bad_quote else body[i * 80: i * 80 + 20]
        kf = {"central_event": f"mock central event of {wid}", "main_characters": ["mock"], "turning_point": "mock", "ending": "mock"}

        def sc():
            s = base.randint(2, 5)
            if rep_noise.random() < 0.25:
                s = max(1, min(5, s + rep_noise.choice([-1, 1])))
            return s
        out = {"key_facts": kf}
        for i, ax in enumerate(AXES[method]):
            if method == "B":
                out[ax] = {"verdict": base.choice(["PASS", "WEAK", "FAIL", "PASS"]), "evidence_quotes": [q(i)], "reason": "mock", "weakness": "なし"}
            else:
                out[ax] = {"score": sc(), "evidence_quotes": [q(i)], "reason": "mock"}
        if self.force_contradiction and wid == "L05":   # 矛盾検出ロジックの動作確認用: 魅力が失われると書いて高得点
            ax = AXES[method][-1]
            if method == "B":
                out[ax].update(verdict="PASS", reason="文体が魅力の中心で短縮すると魅力が失われる")
            else:
                out[ax].update(score=5, reason="文体が魅力の中心で短縮すると魅力が失われる")
        if method == "B":
            out["consistency_check"] = {"self_reported_weaknesses": [], "contradictions_found": [], "verdicts_revised": False}
            out["overall"] = {"verdict": "PASS", "comment": "mock"}
        else:
            out["overall"] = {"score": sc(), "comment": "mock"}
        if method == "C":
            out["memorable_point"] = "mock"
        if method == "D":
            out["lost_in_compression"] = [{"element": "mock", "severity": base.choice(["low", "medium", "high"])}]
            out["must_keep"] = ["mock"]
            out["retelling_sketch"] = ["a", "b", "c"]

        class U:
            input_tokens = 5000
            output_tokens = 2000

        class R:
            model = kw["model"]
            id = "mock-response"
            output_text = json.dumps(out, ensure_ascii=False)
            usage = U()
        return R()


# ------------------------------------------------------------ 1 task(方式×作品×rep)
class ModelMismatch(RuntimeError):
    pass


def _write(path: str, rec: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)


def _call_with_backoff(client, kwargs, max_attempts: int = 3):
    """rate limit(429)のみ待って再試行(失敗応答は課金されない)。その他の例外はそのまま上げる。"""
    for i in range(max_attempts):
        try:
            return client.responses.create(**kwargs)
        except Exception as e:  # noqa
            if "ratelimit" in type(e).__name__.lower() and i < max_attempts - 1:
                time.sleep(5 * (2 ** i))
                continue
            raise


def run_task(method: str, wid: str, rep: int, model: str, client, out_dir: str, mock: bool) -> dict:
    model = common.check_model(ROUTING_KEY, model)         # 許可外モデルはAPI前にfail-closed
    if model not in ALLOWED_MODELS:
        raise RuntimeError(f"STOP: {model} は許可モデル外")
    m = load_method(method)
    unit = build_unit(wid)
    title = load_title(wid)
    messages = build_messages(m, unit, title)
    kwargs = dict(model=model, reasoning={"effort": REASONING_EFFORT}, input=messages,
                  text={"format": {"type": "json_schema", **m["schema"]}})
    t0 = time.time()
    resp = _call_with_backoff(client, kwargs)
    elapsed = round(time.time() - t0, 2)
    actual = getattr(resp, "model", None)
    usage = getattr(resp, "usage", None)
    u = {"input_tokens": getattr(usage, "input_tokens", None), "output_tokens": getattr(usage, "output_tokens", None)} if usage else None
    rec = {"method": method, "work_id": wid, "rep": rep, "eval_version": EVAL_VERSION, "mock": mock, "requested_model": model,
           "actual_model_id": actual, "routing_key": ROUTING_KEY, "reasoning_effort": REASONING_EFFORT, "usage": u,
           "elapsed_sec": elapsed, "response_id": getattr(resp, "id", None),
           "prompt_sha256": hashlib.sha256(json.dumps(messages, ensure_ascii=False).encode("utf-8")).hexdigest(),
           "developer_message": m["developer"], "evaluated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
           "cost_jpy": round(cost_jpy(load_prices(model), u["input_tokens"], u["output_tokens"]), 5) if u and u["input_tokens"] is not None else None,
           "unit": {"chars_no_ws": unit["chars_no_ws"], "lang": unit["lang"]}}
    path = os.path.join(out_dir, model.replace("/", "_"), method, f"{wid}_rep{rep}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not mock and not (actual and str(actual).startswith(model)):
        rec["error"] = f"STOP: actual model_idが要求と異なる requested={model} actual={actual}"
        _write(path, rec)
        raise ModelMismatch(rec["error"])
    try:
        parsed = json.loads(resp.output_text)
        validate_parsed(method, parsed, m["schema"])
        rec["result"] = parsed
        rec["quote_verification"] = verify_quotes(method, parsed, unit["text"])
    except Exception as e:  # 応答は課金済みのため原文を残す(再試行しない)
        rec["error"] = f"parse/validate: {type(e).__name__}: {e}"
        rec["raw_output_text"] = getattr(resp, "output_text", None)
    _write(path, rec)
    return rec


class BudgetGuard:
    """累計費用が承認上限に達するか、次callの上限見積(x1.5)を足すと超える場合は以降のcallを止める。"""
    def __init__(self, budget_jpy: float):
        self.budget = budget_jpy
        self.spent = 0.0
        self.stopped = False
        self.reason = ""
        self._lock = threading.Lock()

    def can_start(self, next_cap: float) -> bool:
        with self._lock:
            if self.stopped:
                return False
            if self.spent + next_cap > self.budget:
                self.stopped, self.reason = True, f"STOP: 累計{self.spent:.2f}円+次call上限{next_cap:.2f}円が承認上限{self.budget:.2f}円を超過"
                return False
            return True

    def add(self, jpy: float) -> None:
        with self._lock:
            self.spent += jpy

    def stop(self, reason: str) -> None:
        with self._lock:
            self.stopped, self.reason = True, reason


def run_all(methods, works, reps, model, client, out_dir, workers, mock, guard=None):
    tasks = [(m, w, r) for r in range(1, reps + 1) for m in methods for w in works]

    def _do(t):
        m, w, r = t
        if guard is not None and not guard.can_start(per_call_cap_jpy(m, w)):
            return {"method": m, "work_id": w, "rep": r, "skipped": guard.reason}
        try:
            rec = run_task(m, w, r, model, client, out_dir, mock)
        except ModelMismatch as e:
            if guard:
                guard.stop(str(e))
            return {"method": m, "work_id": w, "rep": r, "error": str(e)}
        if guard is not None and rec.get("cost_jpy"):
            guard.add(rec["cost_jpy"])
        return rec
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(_do, tasks))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["mock", "real", "estimate"], default="mock")
    ap.add_argument("--models", nargs="+", default=[PRIMARY_MODEL])
    ap.add_argument("--methods", nargs="+", default=list(METHODS))
    ap.add_argument("--works", nargs="*", default=list(WORKS))
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--approved-budget-jpy", type=float, default=0.0, help="ユーザーが承認した費用上限(円)。0ならrealは起動しない")
    args = ap.parse_args()
    for mdl in args.models:
        if mdl not in ALLOWED_MODELS:
            sys.exit(f"STOP: {mdl} は許可モデル外(Trial固定=gpt-6-luna。Astra/Sol等の限定比較はユーザー承認後に別委任)。許可: {ALLOWED_MODELS}")
    for m in args.methods:
        if m not in METHODS:
            sys.exit(f"STOP: 未知の方式 {m}")

    if args.mode == "estimate":
        for n in (2, 3):
            est = estimate(n)
            with open(os.path.join(OUT_BASE, f"COST_ESTIMATE_N{n}.json"), "w", encoding="utf-8") as f:
                json.dump(est, f, ensure_ascii=False, indent=2)
            print(n, est["total_point_jpy"], est["total_cap_jpy"], est["calls"])
        return

    if args.mode == "mock":
        out = args.out_dir or os.path.join(OUT_BASE, "mock_run")
        client = MockClient()
        recs = run_all(args.methods, args.works, args.reps, args.models[0], client, out, args.workers, True, None)
        bad = run_task(args.methods[0], args.works[0], 1, args.models[0], MockClient(bad_quote=True), os.path.join(out, "_bad_quote_check"), True)
        summary = {"mock_calls": client.calls, "n_records": len(recs), "errors": [r for r in recs if r.get("error")],
                   "bad_quote_detected": not bad["quote_verification"]["all_verified"], "out_dir": out}
        with open(os.path.join(out, "MOCK_RUN_SUMMARY.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(json.dumps({k: summary[k] for k in ("mock_calls", "n_records", "bad_quote_detected")}, ensure_ascii=False), "errors:", len(summary["errors"]))
        return

    # ---- real: 有料API。ユーザー承認の費用上限が必須(委任_01では実行しない)
    if args.approved_budget_jpy <= 0:
        sys.exit("STOP: 有料API(real)はユーザーの費用上限承認(--approved-budget-jpy > 0)が無いと起動しない。")
    est_ = estimate(args.reps, tuple(args.works), tuple(args.methods))
    if est_["total_cap_jpy"] > args.approved_budget_jpy:
        sys.exit(f"STOP: 上限見積{est_['total_cap_jpy']:.2f}円が承認上限{args.approved_budget_jpy:.2f}円を超える。")
    from dotenv import load_dotenv  # lazy import
    load_dotenv()
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    out = args.out_dir or os.path.join(OUT_BASE, "real_run")
    os.makedirs(out, exist_ok=True)
    cl.install(os.path.join(out, "raw_usage_log.jsonl"))
    client = vfl01.get_client()
    guard = BudgetGuard(args.approved_budget_jpy)
    with cl.logging_context("FAMILY_Z_STORY_QUALITY_MODEL_COMPARISON_TRIAL_01", "eval"):
        recs = run_all(args.methods, args.works, args.reps, args.models[0], client, out, args.workers, False, guard)
    print(json.dumps({"spent_jpy": round(guard.spent, 3), "stopped": guard.stopped, "reason": guard.reason,
                      "n_ok": sum(1 for r in recs if "result" in r), "n_err": sum(1 for r in recs if r.get("error") or r.get("skipped"))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
