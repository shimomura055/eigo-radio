# -*- coding: utf-8 -*-
"""maq_driver_02.py  FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01 委任_05 Phase 3 (DEV/Trial専用driver、maq_driver_01.pyの記事別対応版)
maq_driver_01.py(META用)からの差分: 記事設定(--slug coffee_prices|hormuz)、Ledger元引数化、hormuzのA新規生成、案別cap/見積token記事別化、
残予算ゲート(既消費+Phase3累計<=550、プロセス間共有ledger)。writer/B3の呼出手順は01と同一。

(以下は01の説明)

JA記事(META)を工程別モデル配置(C/D/E案、A案は既存複製)で生成する Trial 専用 driver。
- Production経路(er019 production runner)は import しない。Production module (er053 W-1 / er019 B3 / producer / contract) は
  **無改変のまま import** し、Prompt定数・純関数・B3関数・決定論producerを再利用する(方式Y、DESIGN_01 2節)。
- API呼出部のみ driver 側。model gate は routing.require_model_or_override(理由つき。monkeypatchしない)。
- 出力は er052_output/ja_article_quality_model_allocation_trial_01/runs/<案>/ 配下のみ。
- 各案は別processで実行する(cost logger global競合回避)。 `python maq_driver_01.py run --arm C|D|E`
- 予算: 各API call直前に「案累計+保守見積(A実測token x 1.5) <= 案cap」を検査、超過は実行せずSTOP。
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import er003_audio_tts_asr_safety as safety          # noqa: E402
import er005_cost_logger as cl                       # noqa: E402
import er006_model_routing_contract_01 as routing    # noqa: E402
import er019_family_x_ja_writer_o_r1_r2_01 as jaw    # noqa: E402
import er019_family_x_storyline_b3_fact_selection_01 as b3   # noqa: E402
import er053_family_x_factlock_ja_writer_01 as w1    # noqa: E402
import er053_b3_deterministic_producer_01 as annot   # noqa: E402
from er053_b3_annotation_contract_01 import validate_annotated_b3   # noqa: E402

TRIAL_ID = "FAMILY-X-JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01"
OVERRIDE_REASON = "JA-ARTICLE-QUALITY-MODEL-ALLOCATION-TRIAL-01 DEV/Trial(ユーザー指定の工程別モデル配置)。Production不変"
THEME_TAG = "MAQ_TRIAL_01"
USD_JPY = 160.0
LUNA, ASTRA, SOL = "gpt-6-luna", "gpt-6-astra", "gpt-6.1-sol"
EFFORT = "high"
RUNS_02 = os.path.join(HERE, "runs_02")
PRIOR_SPENT_JPY = 109.11          # 既消費(Phase 2 META)
TRIAL_CUM_CAP_JPY = 550.0         # ユーザー決定 2026-10-11: Trial累計上限
COFFEE_TOPIC = ("Current news/lifestyle topic: why coffee prices have risen so sharply and why a cup of coffee now costs more. "
                "Using only facts confirmed by web search (International Coffee Organization, USDA reports, Reuters/AP/Bloomberg-level reporting, "
                "company announcements), cover recent coffee bean price levels and changes (with dates, and whether arabica or robusta), the reported causes "
                "(weather and harvest conditions in producing countries, currency, supply and demand, tariffs if reported), and the reported effect on retail or "
                "cafe prices for consumers. Separate confirmed facts from forecasts, and do not present one cause as the only cause unless the source says so. "
                "Do not invent details and do not use the assistant's own prior knowledge.")
ARTICLES = {
    "coffee_prices": {
        "topic": COFFEE_TOPIC,
        "ledger_src": os.path.join(ROOT, "er019_output", "coffee_prices", "run_l3_01", "research_ledger", "verified_fact_ledger.txt"),
        "ledger_sha": "e94a50c1d22686d52bd65beca4272650ecc8286de54629c3d8dfb42fa397ef7b",
        "a_existing": os.path.join(ROOT, "er019_output", "coffee_prices", "run_l3_01"),     # A既存(再利用)。Noneなら新規生成
        "caps": {"A": None, "C": 97.0, "D": 129.0, "E": 50.0},
        # A実測(coffee run_l3_01)。stage -> (input, output(reasoning込み))。A案モデル(b3=Luna,r0=Luna,r1=Astra,r2=Astra)での値
        "base_tokens": {"b3": (6241, 7456), "r0": (2437, 6296), "r1": (696, 2131), "r2": (765, 2305)},
    },
    "hormuz": {
        "topic": "ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応",
        "ledger_src": os.path.join(ROOT, "er019_output", "family_x_refresh_e2e_01", "hormuz", "run_03", "research_ledger", "verified_fact_ledger.txt"),
        "ledger_sha": "9bd6834e68e7e4378ba0ebccdd84c0128df2a5cd0aca7c1e84df612ae77ae1a6",
        "a_existing": None,
        "caps": {"A": 56.0, "C": 76.0, "D": 97.0, "E": 40.0},
        # PHASE3_PREP_01 2節: input=Ledger長比補正、output=META/coffee実測平均
        "base_tokens": {"b3": (3130, 5855), "r0": (1800, 4932), "r1": (600, 2184), "r2": (750, 2098)},
    },
}
# META Phase2実測のモデル別出力比(A案モデルを1.0): PHASE3_PREP_01 2節
OUT_RATIO = {"b3": {LUNA: 1.0, ASTRA: 1.262, SOL: 0.852}, "r0": {LUNA: 1.0, ASTRA: 1.202, SOL: 1.359},
             "r1": {ASTRA: 1.0, LUNA: 0.436, SOL: 0.549}, "r2": {ASTRA: 1.0, LUNA: 0.955, SOL: 1.200}}
SLUG = None
TOPIC = LEDGER_SHA = A_RUN = LEDGER_SRC = RUNS = A_EXISTING = None
PHASE_LEDGER = os.path.join(RUNS_02, "phase3_spend_ledger.jsonl")
PRICING_SNAPSHOT = os.path.join(ROOT, "er005_output", "cost_baseline_01", "pricing_snapshot.json")
B3_ALLOWED_MODELS = (LUNA, ASTRA, SOL)      # B3には Production routing process が無いので、Trial許可リストで fail-closed

# 案定義(正式比較表)。B3列=B3 LLMのmodel(Noneは再利用)。cap=案別上限(JPY)
ARMS = {
    "A": {"b3": LUNA, "r0": LUNA, "r1": ASTRA, "r2": ASTRA, "cap": None},
    "C": {"b3": None, "r0": ASTRA, "r1": LUNA, "r2": LUNA, "cap": 55.0},
    "D": {"b3": ASTRA, "r0": LUNA, "r1": LUNA, "r2": LUNA, "cap": 75.0},
    "E": {"b3": SOL, "r0": SOL, "r1": SOL, "r2": SOL, "cap": 45.0},
}
# 保守見積の基準token(A案実測 META: in/out、reasoning込み)。x1.5を保守見積とする
EST_TOKENS = {}


def configure(slug: str, runs_root: str | None = None) -> None:
    """記事設定を module global へ反映(1 process = 1 slug)。A_RUN=B3再利用元(C案の copy_b3_from)。"""
    global SLUG, TOPIC, LEDGER_SHA, A_RUN, LEDGER_SRC, RUNS, A_EXISTING, EST_TOKENS
    a = ARTICLES[slug]
    SLUG, TOPIC, LEDGER_SHA, LEDGER_SRC, A_EXISTING = slug, a["topic"], a["ledger_sha"], a["ledger_src"], a["a_existing"]
    RUNS = os.path.join(runs_root or RUNS_02, slug)
    A_RUN = A_EXISTING or os.path.join(RUNS, "A")
    for arm, cap in a["caps"].items():
        ARMS[arm]["cap"] = cap
    EST_TOKENS = {}   # (stage_key, model) -> (in, out)
    for k, (i, o) in a["base_tokens"].items():
        for m, r in OUT_RATIO[k].items():
            EST_TOKENS[(k, m)] = (i, o * r)
CONSERVATIVE_FACTOR = 1.5


class BudgetStop(RuntimeError):
    pass


class CompatStop(RuntimeError):
    """モデル/effort/json_schemaの非受理(400系)。降格・自動再試行しない。"""


# ---------------- helpers ----------------
def sha_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def sha_file(p: str) -> str:
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def wt(p, text):
    w1.wt(p, text)


def wj(p, obj):
    w1.wj(p, obj)


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


_PRICES = None


def price_table() -> dict:
    """pricing_snapshot.json の Standard 単価 {model: (in, cached, out)} USD/1M。"""
    global _PRICES
    if _PRICES is None:
        snap = json.load(open(PRICING_SNAPSHOT, encoding="utf-8"))
        tab = {}
        for e in snap["prices"]:
            if e.get("tier") != "Standard":
                continue
            m = tab.setdefault(e["model"], {})
            m[e["meter"]] = float(e["price"])
        _PRICES = {k: (v["input_tokens"], v["cached_input_tokens"], v["output_tokens"])
                   for k, v in tab.items() if {"input_tokens", "cached_input_tokens", "output_tokens"} <= set(v)}
    return _PRICES


def cost_jpy(model: str, in_tok: int, cached: int, out_tok: int) -> float:
    pi, pc, po = price_table()[model]
    usd = ((in_tok - cached) * pi + cached * pc + out_tok * po) / 1e6
    return usd * USD_JPY


def conservative_estimate_jpy(stage: str, model: str) -> float:
    if stage.startswith("storyline_b3"):
        k = "b3"
    elif stage.startswith("w1_r0"):
        k = "r0"
    elif stage.startswith("w1_astra_r1"):
        k = "r1"
    elif stage.startswith("w1_astra_r2"):
        k = "r2"
    else:
        raise BudgetStop(f"見積対象外のstage '{stage}'(未知stageはfail-closed)")
    if (k, model) not in EST_TOKENS:
        raise BudgetStop(f"見積対象外の(stage,model)=({k},{model})(fail-closed)")
    i, o = EST_TOKENS[(k, model)]
    return cost_jpy(model, i, 0, o) * CONSERVATIVE_FACTOR


def _is_compat_error(exc) -> bool:
    code = getattr(exc, "status_code", None)
    return code is not None and 400 <= int(code) < 500 and int(code) != 429


# ---------------- Phase 3 共有 spend ledger(プロセス間、全体残予算ゲート) ----------------
def _phase_lock():
    lock = PHASE_LEDGER + ".lock"
    os.makedirs(os.path.dirname(lock), exist_ok=True)
    for _ in range(1200):
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return lock
        except FileExistsError:
            time.sleep(0.05)
    raise BudgetStop("phase ledger lock取得失敗")


def phase_total_and_reserve(reserve_jpy: float, key: str) -> float:
    """ロック内で Phase3確定額+他processの未決予約 を集計し、既消費+それ+今回予約 > 550 ならBudgetStop。通れば予約を書く。戻り値=既消費+確定額。"""
    lock = _phase_lock()
    try:
        settled, open_res = 0.0, {}
        if os.path.exists(PHASE_LEDGER):
            for ln in open(PHASE_LEDGER, encoding="utf-8"):
                if not ln.strip():
                    continue
                r = json.loads(ln)
                if r["t"] == "reserve":
                    open_res[r["key"]] = r["jpy"]
                elif r["t"] == "settle":
                    open_res.pop(r["key"], None)
                    settled += r["jpy"]
        total = PRIOR_SPENT_JPY + settled + sum(open_res.values()) + reserve_jpy
        if total > TRIAL_CUM_CAP_JPY:
            raise BudgetStop(f"[STOP] 累計上限: 既消費{PRIOR_SPENT_JPY}+Phase3確定{settled:.2f}+予約中{sum(open_res.values()):.2f}+今回見積{reserve_jpy:.2f}={total:.2f} > {TRIAL_CUM_CAP_JPY}")
        with open(PHASE_LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": "reserve", "key": key, "jpy": round(reserve_jpy, 4), "ts": now_iso()}) + "\n")
        return PRIOR_SPENT_JPY + settled
    finally:
        os.remove(lock)


def phase_settle(key: str, jpy: float) -> None:
    lock = _phase_lock()
    try:
        with open(PHASE_LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": "settle", "key": key, "jpy": round(jpy, 4), "ts": now_iso()}) + "\n")
    finally:
        os.remove(lock)


# ---------------- 予算・usage記録つき client wrapper ----------------
class GuardedClient:
    """real.responses.create を kwargs そのまま呼ぶ薄い wrapper。
    各call前: prompt sha/model/入力sha/残予算を表示、案累計+保守見積>capならBudgetStop(APIを呼ばない)。
    各call後: usage(input/cached/output/reasoning)・USD/JPY・秒・actual model_id を記録。リクエストは一切改変しない。"""

    def __init__(self, real, arm: str, cap_jpy, ledger_path: str | None, verbose: bool = True, phase_gate: bool = False):
        self._real, self.arm, self.cap, self.ledger_path, self.verbose = real, arm, cap_jpy, ledger_path, verbose
        self.phase_gate = phase_gate
        self._seq = 0
        self.responses = self
        self.records: list = []
        self.spent = 0.0
        self.compat_failed = None
        self.last_text_by_stage: dict = {}

    def create(self, **kw):
        stage = cl._CONTEXT.get("stage") or "unknown"
        model = kw["model"]
        if self.compat_failed:
            raise CompatStop(f"以前の非受理で停止中: {self.compat_failed}")
        est = conservative_estimate_jpy(stage, model)
        remaining = None if self.cap is None else self.cap - self.spent
        if self.cap is not None and self.spent + est > self.cap:
            raise BudgetStop(f"[STOP] 予算: arm={self.arm} stage={stage} model={model} 累計{self.spent:.2f}+保守見積{est:.2f} > cap{self.cap}")
        res_key = None
        prior_cum = None
        if self.phase_gate:
            self._seq += 1
            res_key = f"{SLUG}:{self.arm}:{self._seq}:{stage}:{os.getpid()}"
            prior_cum = phase_total_and_reserve(est, res_key)
        inp = kw.get("input")
        in_sha = sha_text(json.dumps(inp, ensure_ascii=False, sort_keys=True))
        user_sha = sha_text(next((m["content"] for m in inp if m.get("role") == "user"), ""))
        if self.verbose:
            print(f"[MAQ][{self.arm}][pre-call] stage={stage} model={model} effort={kw.get('reasoning', {}).get('effort')} "
                  f"user_prompt_sha={user_sha[:12]} input_sha={in_sha[:12]} json_schema={'text' in kw} "
                  f"spent={self.spent:.2f} est={est:.2f} remaining={'-' if remaining is None else f'{remaining:.2f}'} trial_cum_before={prior_cum} trial_remaining={None if prior_cum is None else round(TRIAL_CUM_CAP_JPY - prior_cum, 2)}", flush=True)
        t0 = time.time()
        try:
            resp = self._real.responses.create(**kw)
        except Exception as exc:  # noqa: BLE001
            rec = {"stage": stage, "model_requested": model, "failed": True, "error_type": type(exc).__name__,
                   "status_code": getattr(exc, "status_code", None), "error": str(exc)[:300], "sec": round(time.time() - t0, 1),
                   "jpy": 0.0, "note": "例外のためusage不明(通常、受理されない呼出は課金なし)"}
            self.records.append(rec)
            self._log(rec)
            if res_key:
                phase_settle(res_key, 0.0)
            if _is_compat_error(exc):
                self.compat_failed = f"{type(exc).__name__}:{rec['status_code']}:{rec['error'][:120]}"
            raise
        sec = time.time() - t0
        u = getattr(resp, "usage", None)
        in_tok = getattr(u, "input_tokens", 0) or 0
        out_tok = getattr(u, "output_tokens", 0) or 0
        cached = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0
        reasoning = getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", 0) or 0
        jpy = cost_jpy(model, in_tok, cached, out_tok)
        self.spent += jpy
        if res_key:
            phase_settle(res_key, jpy)
        rec = {"stage": stage, "model_requested": model, "model_returned": getattr(resp, "model", None),
               "response_id": getattr(resp, "id", None), "input_tokens": in_tok, "cached_input_tokens": cached,
               "output_tokens": out_tok, "reasoning_tokens": reasoning, "usd": round(jpy / USD_JPY, 6), "jpy": round(jpy, 4),
               "sec": round(sec, 1), "user_prompt_sha256": user_sha, "input_sha256": in_sha,
               "effort": kw.get("reasoning", {}).get("effort"), "json_schema": "text" in kw, "timestamp": now_iso()}
        self.records.append(rec)
        self.last_text_by_stage[stage] = getattr(resp, "output_text", None)
        self._log(rec)
        if self.verbose:
            print(f"[MAQ][{self.arm}][post-call] stage={stage} model_returned={rec['model_returned']} in={in_tok} out={out_tok} "
                  f"reasoning={reasoning} jpy={jpy:.3f} cum={self.spent:.2f} sec={rec['sec']}", flush=True)
        return resp

    def _log(self, rec):
        if self.ledger_path:
            os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
            with open(self.ledger_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"arm": self.arm, "trial": TRIAL_ID, **rec}, ensure_ascii=False) + "\n")


# ---------------- Writer (run_w1_writer の1対1写し。modelのみ引数) ----------------
def call_writer_r0(client, model: str, user: str, stage: str):
    routing.require_model_or_override("FAMILY_X_FACTLOCK_R0", model, OVERRIDE_REASON)
    with cl.logging_context(THEME_TAG, stage):
        resp = client.responses.create(
            model=model, reasoning={"effort": EFFORT},
            input=[{"role": "developer", "content": jaw.DEVELOPER_MESSAGE}, {"role": "user", "content": user}])
    if not str(getattr(resp, "model", "")).startswith(model):
        raise w1.ProvenanceViolation(f"[STOP] R0段のmodelが{model}で始まらない: {getattr(resp, 'model', None)}")
    return resp


def call_writer_revise(client, model: str, user: str, stage: str, retries: int = 2):
    routing.require_model_or_override("FAMILY_X_FACTLOCK_REVISE", model, OVERRIDE_REASON)
    last = None
    for i in range(1 + retries):
        try:
            with cl.logging_context(THEME_TAG, stage):
                resp = client.responses.create(model=model, reasoning={"effort": EFFORT}, input=[{"role": "user", "content": user}])
            if not str(getattr(resp, "model", "")).startswith(model):
                raise w1.ProvenanceViolation(f"[STOP] R1/R2段のmodelが{model}で始まらない: {getattr(resp, 'model', None)}")
            return resp
        except (w1.ProvenanceViolation, BudgetStop, CompatStop):
            raise
        except Exception as e:  # noqa: BLE001   Productionと同じ: 一時エラーは最大2回再試行
            last = e
            if _is_compat_error(e):
                raise CompatStop(f"R1/R2 非受理: {e!r}"[:300])
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"Writer API失敗(再試行{retries}回後): {last!r}")


def run_writer(out_dir: str, client, r0_model: str, r1_model: str, r2_model: str) -> dict:
    """er053.run_w1_writer と同一手順(予算guardはclient wrapper側)。出力ファイル構造・内容も同一。"""
    annotated = validate_annotated_b3(out_dir)
    storyline, _facts_text = w1.parse_brief_md(annotated.annotated_md_text)
    news_text = annotated.news_field_text
    routing.require_model_or_override("FAMILY_X_FACTLOCK_R0", r0_model, OVERRIDE_REASON)
    routing.require_model_or_override("FAMILY_X_FACTLOCK_REVISE", r1_model, OVERRIDE_REASON)
    routing.require_model_or_override("FAMILY_X_FACTLOCK_REVISE", r2_model, OVERRIDE_REASON)
    d = os.path.join(out_dir, "ja_writer")
    fdir = os.path.join(d, "factlock")
    ev = {"chain_method": "MAQ_TRIAL_" + w1.CHAIN_METHOD, "models": {"r0": r0_model, "r1": r1_model, "r2": r2_model},
          "override_reason": OVERRIDE_REASON, "annotated_md_sha256": annotated.annotated_md_sha256,
          "annotation_manifest_producer": annotated.producer, "verbatim_shas": w1.verbatim_shas(),
          "writer_constraints_sha256": sha_text(annotated.constraints_text), "news_field_sha256": sha_text(news_text),
          "symbol_qa": {}, "started": now_iso()}

    prompt0 = w1.build_r0_prompt(storyline, news_text)
    resp0 = call_writer_r0(client, r0_model, prompt0, "w1_r0")
    text0 = resp0.output_text.strip()
    r0_calls = [{"stage": "w1_r0", **w1._resp_meta(resp0), "prompt_sha256": sha_text(prompt0)}]
    f0 = safety.detect_prohibited_symbols(text0, language="ja")
    ev["symbol_qa"]["r0"] = {"findings_first": f0, "regenerated": False}
    if safety.symbol_gate_requires_stop(f0):
        prompt0b = w1.build_r0_symbol_regen_prompt(storyline, news_text, f0)
        resp0b = call_writer_r0(client, r0_model, prompt0b, "w1_r0_symbol_regen")
        text0b = resp0b.output_text.strip()
        r0_calls.append({"stage": "w1_r0_symbol_regen", **w1._resp_meta(resp0b), "prompt_sha256": sha_text(prompt0b)})
        f0b = safety.detect_prohibited_symbols(text0b, language="ja")
        ev["symbol_qa"]["r0"].update({"regenerated": True, "findings_after": f0b, "pre_regen_response_id": r0_calls[0]["response_id"]})
        if safety.symbol_gate_requires_stop(f0b):
            wt(os.path.join(d, "audit", "rejected_w1_r0_symbol.md"), text0b)
            raise w1.JASymbolCheckStopError("r0_symbol", f"[STOP] R0記号QA: 再生成後も残存(findings={f0b})", text0b, f0b)
        text0 = text0b
    for c in r0_calls:
        c["model_requested"] = r0_model
        c["model_mismatch"] = bool(c["model"]) and not str(c["model"]).startswith(r0_model)
    clean0 = w1.clean_ja_for_next(text0).strip() + "\n"
    wt(os.path.join(fdir, "r0_with_tags.md"), text0)
    wt(os.path.join(fdir, "r0.md"), clean0)
    tags_used = sorted({t for m in w1.TAG_RE.finditer(text0) for t in w1.tag_ids(m.group(0))})
    r0_meta = {"writer_calls": r0_calls, "tags_used": tags_used, "marks_echoed": len(w1.MARK_RE.findall(text0)),
               "facts_in_brief": list(w1.parse_annotated_facts(annotated.annotated_md_text)), "r0_echo": w1.detect_r0_echo(clean0),
               "r0_sha256": sha_text(clean0), "r0_prompt_sha256": sha_text(prompt0)}
    wj(os.path.join(fdir, "r0_meta.json"), r0_meta)

    def revise_stage(model: str, src_path: str, stage_tag: str):
        src = w1.rdt(src_path)
        user = w1.USER_TMPL.format(body=src.strip())
        t0 = time.time()
        resp = call_writer_revise(client, model, user, stage_tag)
        raw = (resp.output_text or "").strip()
        p = w1.postprocess_ja(raw)
        meta = {"requested_model": model, "model": resp.model, "reasoning": {"effort": EFFORT},
                "previous_response_id_used": False, "developer_message": None, "service_tier": None,
                "user_message_sha256": sha_text(user), "response_id": resp.id, "sec": round(time.time() - t0, 1),
                "output_chars": len(raw),
                "usage": {"input_tokens": getattr(resp.usage, "input_tokens", None),
                          "output_tokens": getattr(resp.usage, "output_tokens", None)}}
        return raw, p, meta

    raw1, p1, m1 = revise_stage(r1_model, os.path.join(fdir, "r0.md"), "w1_astra_r1")
    wt(os.path.join(fdir, "r1.raw.md"), raw1)
    wj(os.path.join(fdir, "r1.response.json"), m1)
    wt(os.path.join(fdir, "r1.p1.md"), p1)

    raw2, p2, m2 = revise_stage(r2_model, os.path.join(fdir, "r1.raw.md"), "w1_astra_r2")
    wt(os.path.join(fdir, "r2.raw.md"), raw2)
    wj(os.path.join(fdir, "r2.response.json"), m2)
    final = w1.clean_ja_for_next(p2)
    f2 = safety.detect_prohibited_symbols(final, language="ja")
    ev["symbol_qa"]["r2"] = {"method": "A_rerun_r2_once_same_r1_raw", "findings_first": f2, "rerun": False, "response_ids": [m2["response_id"]]}
    r2_meta_all = [m2]
    if safety.symbol_gate_requires_stop(f2):
        wt(os.path.join(fdir, "r2.first.raw.md"), raw2)
        wt(os.path.join(fdir, "r2.first.final_rejected.md"), final)
        raw2b, p2b, m2b = revise_stage(r2_model, os.path.join(fdir, "r1.raw.md"), "w1_astra_r2_symbol_rerun")
        wt(os.path.join(fdir, "r2.rerun.raw.md"), raw2b)
        wj(os.path.join(fdir, "r2.rerun.response.json"), m2b)
        r2_meta_all.append(m2b)
        final_b = w1.clean_ja_for_next(p2b)
        f2b = safety.detect_prohibited_symbols(final_b, language="ja")
        ev["symbol_qa"]["r2"].update({"rerun": True, "findings_after": f2b, "response_ids": [m2["response_id"], m2b["response_id"]]})
        if safety.symbol_gate_requires_stop(f2b):
            wt(os.path.join(d, "audit", "rejected_w1_r2_symbol.md"), final_b)
            raise w1.JASymbolCheckStopError("r2_symbol", f"[STOP] R2記号QA: 再実行後も残存(findings={f2b})", final_b, f2b)
        final, p2, m2 = final_b, p2b, m2b
    for m in r2_meta_all + [m1]:
        m["model_mismatch"] = not str(m["model"] or "").startswith(m["requested_model"])
    echo = w1.detect_r0_echo(final)
    wt(os.path.join(d, "original.md"), clean0)
    wt(os.path.join(d, "revision1.md"), p1)
    ev.update({"original": {"model": r0_calls[-1]["model"], "response_id": r0_calls[-1]["response_id"], "model_requested": r0_model, "r0_calls": r0_calls},
               "r1": m1, "r2": m2, "r2_all_attempts": r2_meta_all, "r2_echo_after_revision": echo,
               "title": w1.extract_title(final), "ja_text_sha256": sha_text(final), "finished": now_iso()})
    wj(os.path.join(d, "runtime_evidence.json"), ev)
    wt(os.path.join(d, "revision2.md"), final)
    return {"ja_text": final, "title": ev["title"], "runtime_evidence": ev}


# ---------------- B3 ----------------
def run_b3_stage(client, out_dir: str, model: str) -> dict:
    """B3①: Production関数 run_storyline_b3_selection をmodel差替で呼ぶ。成果物はProduction runnerの run_storyline_b3 と同形式。"""
    if model not in B3_ALLOWED_MODELS:
        raise RuntimeError(f"B3 modelが許可リスト外: {model}")
    ledger_text = w1.rdt(os.path.join(out_dir, "research_ledger", "verified_fact_ledger.txt"))
    sdir = os.path.join(out_dir, "storyline_b3")
    os.makedirs(sdir, exist_ok=True)
    selection = b3.run_storyline_b3_selection(client, TOPIC, ledger_text, model=model, effort=EFFORT)
    ids = selection["ledger_fact_ids"]
    wj(os.path.join(sdir, "full_ledger.json"), b3.build_full_ledger_record(TOPIC, ledger_text, ids))
    brief_md = b3.build_selected_brief_markdown(selection)
    wt(os.path.join(sdir, "selected_brief.md"), brief_md)
    ev = {"selected_storyline": selection["parsed"]["selected_storyline"], "full_ledger_fact_ids": ids,
          "fact_tests": selection["parsed"]["fact_tests"], "selected_fact_ids": selection["parsed"]["selected_fact_ids"],
          "selected_fact_brief_text": selection["parsed"]["selected_fact_brief"], "recheck_note": selection["parsed"]["recheck_note"],
          "soft_warnings": selection["soft_warnings"]}
    wj(os.path.join(sdir, "fact_selection_evidence.json"), ev)
    wj(os.path.join(sdir, "runtime_evidence.json"), {
        "model_id_actual": selection["model"], "response_id": selection["response_id"], "latency_seconds": selection["latency_seconds"],
        "attempts": selection["attempts"], "retried": selection["retried"], "prompt_shas": selection["prompt_shas"],
        "attempts_log": selection["attempts_log"], "model_requested": model})
    return selection


def produce_annotation(out_dir: str) -> dict:
    return annot.produce_annotated_b3(out_dir)


def prepare_inputs(out_dir: str, copy_b3_from: str | None = None) -> None:
    """Ledgerをバイト複製(sha assert)。copy_b3_fromがあればstoryline_b3(LLM出力部)を複製。"""
    src = LEDGER_SRC
    assert sha_file(src) == LEDGER_SHA, "Ledger元 sha不一致"
    dst = os.path.join(out_dir, "research_ledger", "verified_fact_ledger.txt")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    assert sha_file(dst) == LEDGER_SHA
    if copy_b3_from:
        sd = os.path.join(out_dir, "storyline_b3")
        os.makedirs(sd, exist_ok=True)
        for n in ("full_ledger.json", "selected_brief.md", "fact_selection_evidence.json", "runtime_evidence.json"):
            shutil.copyfile(os.path.join(copy_b3_from, "storyline_b3", n), os.path.join(sd, n))


def module_shas() -> dict:
    mods = ["er053_family_x_factlock_ja_writer_01.py", "er019_family_x_storyline_b3_fact_selection_01.py",
            "er053_b3_deterministic_producer_01.py", "er053_b3_annotation_contract_01.py",
            "er019_family_x_ja_writer_o_r1_r2_01.py", "er006_model_routing_contract_01.py"]
    return {m: sha_file(os.path.join(ROOT, m)) for m in mods}


def write_export(out_dir: str, arm: str, records: list, extra_ev: dict) -> dict:
    ex = os.path.join(out_dir, "export")
    os.makedirs(ex, exist_ok=True)
    sd = os.path.join(out_dir, "storyline_b3")
    ev = json.load(open(os.path.join(sd, "fact_selection_evidence.json"), encoding="utf-8"))
    for src, dst in ((os.path.join(sd, "selected_brief_annotated.md"), "selected_brief_annotated.md"),
                     (os.path.join(sd, "writer_constraints.txt"), "writer_constraints.txt"),
                     (os.path.join(out_dir, "ja_writer", "factlock", "r0.md"), "r0.md"),
                     (os.path.join(out_dir, "ja_writer", "factlock", "r1.p1.md"), "r1.md"),
                     (os.path.join(out_dir, "ja_writer", "revision2.md"), "r2.md")):
        shutil.copyfile(src, os.path.join(ex, dst))
    wt(os.path.join(ex, "selected_fact_ids"), "\n".join(ev["selected_fact_ids"]) + "\n")
    wt(os.path.join(ex, "storyline"), ev["selected_storyline"] + "\n")
    tot = {"jpy": round(sum(r.get("jpy", 0) or 0 for r in records), 4), "usd": round(sum(r.get("usd", 0) or 0 for r in records), 6),
           "sec": round(sum(r.get("sec", 0) or 0 for r in records), 1),
           "input_tokens": sum(r.get("input_tokens", 0) or 0 for r in records), "output_tokens": sum(r.get("output_tokens", 0) or 0 for r in records),
           "reasoning_tokens": sum(r.get("reasoning_tokens", 0) or 0 for r in records)}
    usage = {"arm": arm, "usd_jpy": USD_JPY, "stages": records, "total": tot}
    wj(os.path.join(out_dir, "usage.json"), usage)
    wj(os.path.join(ex, "usage.json"), usage)
    return usage


# ---------------- arm 実行 ----------------
def run_arm(arm: str, client_real=None, out_root: str | None = None, ledger_global: str | None = None, phase_gate: bool = True) -> dict:
    assert SLUG, "configure(slug)未実行"
    out_root = out_root or RUNS
    cfg = ARMS[arm]
    assert arm in ("C", "D", "E") or (arm == "A" and A_EXISTING is None), "課金実行はC/D/E(+Aは既存なしのslugのみ)。B=保留"
    out_dir = os.path.join(out_root, arm)
    if os.path.exists(os.path.join(out_dir, "usage.json")):
        raise RuntimeError(f"{arm}は既に実行済み(1案1回のみ・自動追加なし): {out_dir}")
    os.makedirs(out_dir, exist_ok=True)
    mods_before = module_shas()
    ledger_path = os.path.join(out_dir, "cost_ledger_maq_01.jsonl")
    if client_real is None:
        cl.install(os.path.join(out_dir, "raw_usage_log.jsonl"))
        client_real = jaw.vfl01.get_client()
    client = GuardedClient(client_real, arm, cfg["cap"], ledger_path, phase_gate=phase_gate)
    status = {"arm": arm, "slug": SLUG, "models": {k: cfg[k] for k in ("b3", "r0", "r1", "r2")}, "cap_jpy": cfg["cap"], "started": now_iso(), "stop": None}
    try:
        if cfg["b3"] is None:       # C: A案のB3(LLM出力部)を再利用。B3新規LLM生成なし
            assert os.path.exists(os.path.join(A_RUN, "storyline_b3", "selected_brief_annotated.md")), f"C案: A案のB3が未生成: {A_RUN}"
            prepare_inputs(out_dir, copy_b3_from=A_RUN)
            status["b3_source"] = "A_reuse"
        else:
            prepare_inputs(out_dir)
            run_b3_stage(client, out_dir, cfg["b3"])
            status["b3_source"] = f"new:{cfg['b3']}"
        res = produce_annotation(out_dir)
        status["annotated_md_sha256"] = res["annotated_md_sha256"]
        if arm == "C":              # 再利用の健全性: Aと注記済みB3がバイト一致
            for n in ("selected_brief_annotated.md", "writer_constraints.txt"):
                a = open(os.path.join(A_RUN, "storyline_b3", n), "rb").read()
                c = open(os.path.join(out_dir, "storyline_b3", n), "rb").read()
                assert a == c, f"C案のB3再利用: {n}がAとバイト不一致"
            status["c_reuse_annotated_identical_to_A"] = True
        run_writer(out_dir, client, cfg["r0"], cfg["r1"], cfg["r2"])
        status["result"] = "OK"
    except (BudgetStop, CompatStop, w1.JASymbolCheckStopError, w1.ProvenanceViolation, w1.TagLeak, RuntimeError, AssertionError) as e:
        status["result"] = "STOP"
        status["stop"] = f"{type(e).__name__}: {str(e)[:600]}"
        if client.compat_failed:
            status["stop"] += f" / compat_failed={client.compat_failed}"
        print(f"[MAQ][{arm}] STOP: {status['stop']}", flush=True)
    status["finished"] = now_iso()
    status["spent_jpy"] = round(client.spent, 4)
    status["module_shas_unchanged"] = (mods_before == module_shas())
    wj(os.path.join(out_dir, "runtime_evidence.json"), {**status, "trial": TRIAL_ID, "override_reason": OVERRIDE_REASON,
                                                       "ledger_sha256": LEDGER_SHA, "topic": TOPIC, "module_shas": mods_before,
                                                       "verbatim_shas": w1.verbatim_shas(), "b3_prompt_shas": b3.prompt_shas(),
                                                       "call_records": client.records})
    if status["result"] == "OK":
        write_export(out_dir, arm, client.records, status)
    else:
        wj(os.path.join(out_dir, "usage_partial.json"), {"arm": arm, "stages": client.records, "spent_jpy": status["spent_jpy"]})
    print(f"[MAQ][{arm}] result={status['result']} spent_jpy={status['spent_jpy']}", flush=True)
    return status


def prepare_a(out_root: str | None = None) -> dict:
    """A案: 既存 run_regen_01 から複製のみ(新規課金0)。usageは raw_usage_log.jsonl から単価で再計算。"""
    assert A_EXISTING, "prepare_aはA既存があるslugのみ"
    out_root = out_root or RUNS
    out_dir = os.path.join(out_root, "A")
    prepare_inputs(out_dir, copy_b3_from=A_RUN)
    sd_src = os.path.join(A_RUN, "storyline_b3")
    sd = os.path.join(out_dir, "storyline_b3")
    for n in ("selected_brief_annotated.md", "writer_constraints.txt", "annotation.json", "annotation_manifest.json"):
        shutil.copyfile(os.path.join(sd_src, n), os.path.join(sd, n))
    shutil.copytree(os.path.join(A_RUN, "ja_writer"), os.path.join(out_dir, "ja_writer"), dirs_exist_ok=True)
    records = []
    for line in open(os.path.join(A_RUN, "raw_usage_log.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        if r["stage"] not in ("storyline_b3", "w1_r0", "w1_astra_r1", "w1_astra_r2"):
            continue
        assert r.get("success", True), "A既存のraw_usage_logに失敗recordあり(要確認)"
        j = cost_jpy(r["model_id"], r["input_tokens"], r.get("cached_input_tokens") or 0, r["output_tokens"])
        records.append({"stage": r["stage"], "model_requested": r["model_id"], "model_returned": r["model_id"], "response_id": r["response_id"],
                        "input_tokens": r["input_tokens"], "cached_input_tokens": r.get("cached_input_tokens") or 0,
                        "output_tokens": r["output_tokens"], "reasoning_tokens": r.get("reasoning_tokens"), "usd": round(j / USD_JPY, 6),
                        "jpy": round(j, 4), "sec": r["elapsed_seconds"], "source": os.path.relpath(os.path.join(A_RUN, "raw_usage_log.jsonl"), ROOT) + "(既存実測・再利用0円)"})
    usage = write_export(out_dir, "A", records, {})
    # 検証: 複製がA runとバイト一致
    for rel in ("ja_writer/revision2.md", "storyline_b3/selected_brief_annotated.md", "storyline_b3/selected_brief.md"):
        assert sha_file(os.path.join(out_dir, rel)) == sha_file(os.path.join(A_RUN, rel)), rel
    wj(os.path.join(out_dir, "runtime_evidence.json"), {
        "arm": "A", "slug": SLUG, "source": os.path.relpath(A_RUN, ROOT) + "(複製のみ・新規課金0)", "models": ARMS["A"],
        "r2_sha256": sha_file(os.path.join(out_dir, "ja_writer", "revision2.md")), "ledger_sha256": LEDGER_SHA,
        "b3_raw_note": "A案のB3 raw生文字列(response.output_text逐語)は既存artifactに無い。b3_raw.jsonは作らず fact_selection_evidence.json(parsed)を正とする",
        "source_runtime_evidence": json.load(open(os.path.join(A_RUN, "ja_writer", "runtime_evidence.json"), encoding="utf-8"))})
    return usage


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True, choices=sorted(ARTICLES))
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare-a")
    r = sub.add_parser("run")
    r.add_argument("--arm", required=True, choices=["A", "C", "D", "E"])
    a = ap.parse_args()
    configure(a.slug)
    if a.cmd == "prepare-a":
        u = prepare_a()
        print(json.dumps(u["total"], ensure_ascii=False))
    else:
        st = run_arm(a.arm)
        sys.exit(0 if st["result"] == "OK" else 2)
