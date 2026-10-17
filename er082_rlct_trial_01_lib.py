# ============================================================
# er082_rlct_trial_01_lib.py
# FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01 委任_04 (CP1)
# ============================================================
# Trial専用library(Production非接続)。設計正本=docs/research/
# FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/TRIAL_DESIGN_02.md (v2、Opus条件A R-01〜16反映)。
#
# 方針:
# - Production module(vfl01 / b3 / efam / routing / er053_*)は import して「読取のみ」で呼ぶ。
#   モジュール定数・関数の実行時差し替え(monkey-patch)は一切しない。差異は複製関数の引数で表す。
#   (唯一 er005_cost_logger.install は設計R-02が明示的に要求する既存の計測機構で、Productionと同じ使い方。)
# - 出力は er082_output/rlct_trial_01/ 配下のみ。入力成果物は _inputs/ へ複製してから処理する。
# - 有料API呼出は PAID_CONFIRM_TOKEN を run.py が検証したときのみ。dry-runは StubClient(API 0)。
# - 未承認機能のflag・Production配線は作らない(純粋なOffline Trial)。
# ============================================================
from __future__ import annotations

import copy
import datetime
import difflib
import hashlib
import json
import os
import re
import shutil
import time
from contextlib import contextmanager
from types import SimpleNamespace

import er003_v1_en_direct_vfl_01_generate as vfl01
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er012_e_family_entertainment_two_level_runner_01 as efam
import er019_family_x_storyline_b3_fact_selection_01 as b3

THEME_TAG = "RLCT_TRIAL_01"
OUT_ROOT = "er082_output/rlct_trial_01"

# ---- ユーザー承認値(2026-10-17、(b)+任意A)。定数化(T-3) ----
STAGE_CAPS_JPY = {"1a": 493.0, "1b": 493.0, "optA": 54.0}
CUM_CAP_JPY = 1040.0
EXPECTED_TOTAL_JPY = 536.0
DAILY_SOFT_JPY = 1000.0           # 7-9 日次soft budget(JST)
PAID_CONFIRM_TOKEN = "USER_APPROVED_B_OPTA_2026-10-17_CAP1040"

# 呼出前の1call上限見込み(JPY)。超過見込みで呼ばずSTOP(R-02)。実測後に見直す。
EST_VERIFY_FULL_JPY = 30.0
EST_VERIFY_SEL_JPY = 20.0
EST_B3_JPY = 15.0
EST_INJECT_JPY = 10.0

CAP_PER_FACT = 3
CAP_SUFFIX = (
    "\n\n【検索回数の上限(Trial指示)】各Factの確認のためのweb_search呼出は、Fact1件あたり"
    f"{CAP_PER_FACT}回までとしてください。{CAP_PER_FACT}回の検索で確認できなかった場合は、無理に確定せず、"
    "そのFactをAMBIGUOUSと判定し、確認できなかった理由をverification_notesへ記載してください。"
)

STAGE_R = "er052_output/factlock_astra_e2e_trial_01/stage_r"
ARTICLES = {
    "coffee_prices": {"src": "er019_output/coffee_prices/run_fxpw_01", "stage": "1a", "b3_reusable": True,
                       "known_defects": ["F12", "F07", "F16", "F17"]},
    "inbound_tourism": {"src": f"{STAGE_R}/inbound_tourism", "stage": "1a", "b3_reusable": False,
                         "known_defects": ["F05", "F12"]},
    "streaming_price": {"src": f"{STAGE_R}/streaming_price", "stage": "1b", "b3_reusable": False,
                         "known_defects": ["F07"]},
    "openai_copyright": {"src": f"{STAGE_R}/openai_copyright", "stage": "1b", "b3_reusable": False,
                          "known_defects": []},
    "central_bank_mortgage": {"src": f"{STAGE_R}/central_bank_mortgage", "stage": "1b", "b3_reusable": False,
                               "known_defects": []},
}
METHODS = ["M0", "M0b", "M0p", "M1", "M2", "M3"]
# 実走順(設計4-8): 1a冒頭でCoffee M2 smoke、続いてCoffee、inbound。1bはstreaming先頭。
PLAN = {
    "1a": [("coffee_prices", m) for m in ["M0", "M2", "M0b", "M0p", "M1", "M3"]]
          + [("inbound_tourism", m) for m in ["M0", "M0b", "M0p", "M1", "M2", "M3"]],
    "1b": [("streaming_price", m) for m in ["M0", "M0b", "M0p", "M1", "M2", "M3"]]
          + [(a, m) for a in ("openai_copyright", "central_bank_mortgage") for m in ["M0", "M0b", "M1", "M2", "M3"]],
}
# 複製対象(src run dir相対)
INPUT_FILES = [
    "research_ledger/fact_ledger_draft.json",
    "research_ledger/fact_ledger_verification.json",
    "research_ledger/verified_fact_ledger.txt",
    "research_ledger/verdict_counts.json",
    "research_ledger/runtime_evidence.json",
    "research_ledger/audit/verification_full_record.json",
    "research_ledger/audit/researcher_full_record.json",
    "storyline_b3/selected_brief.md",
    "storyline_b3/fact_selection_evidence.json",
    "storyline_b3/full_ledger.json",
    "storyline_b3/runtime_evidence.json",
    "raw_usage_log.jsonl",
]
PROTECTED_CODE = [
    "er019_family_x_entertainment_production_runner_01.py",
    "er012_e_family_entertainment_two_level_runner_01.py",
    "er003_v1_en_direct_vfl_01_generate.py",
    "er019_family_x_storyline_b3_fact_selection_01.py",
    "er002_ja_web_research_r3.py",
    "er005_cost_logger.py",
    "er006_model_routing_contract_01.py",
    "er053_b3_deterministic_producer_01.py",
    "er053_b3_annotation_contract_01.py",
    "er053_risk_flagger_production_01.py",
    "er053_review_queue_01.py",
    "er053_family_x_factlock_ja_writer_01.py",
]
SHARED_QUEUE_ROOT = "review_queue/post_en"


# ------------------------------------------------------------
# 基本I/O
# ------------------------------------------------------------
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return sha256_bytes(f.read())


def load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def save_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def append_jsonl(path: str, row: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: str) -> list:
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def draft_sha(draft: dict) -> str:
    return sha256_bytes(json.dumps(draft, ensure_ascii=False, sort_keys=True).encode("utf-8"))


# ------------------------------------------------------------
# 整合: sha_manifest / tree_listing (R-03)
# ------------------------------------------------------------
def sha_manifest(paths: list) -> dict:
    out = {}
    for p in paths:
        out[p] = sha256_file(p) if os.path.isfile(p) else "MISSING"
    return out


def tree_listing(root: str) -> dict:
    """root配下の全ファイルの(size, mtime_ns)。新規ファイル・書込み・削除の検知用。"""
    out = {}
    if not os.path.isdir(root):
        return out
    for dp, _dn, fns in os.walk(root):
        for fn in fns:
            fp = os.path.join(dp, fn)
            st = os.stat(fp)
            out[fp.replace("\\", "/")] = [st.st_size, st.st_mtime_ns]
    return out


def reused_artifact_paths(article: str) -> list:
    src = ARTICLES[article]["src"]
    return [f"{src}/{rel}" for rel in INPUT_FILES]


def integrity_snapshot(articles: list) -> dict:
    code = sha_manifest(PROTECTED_CODE)
    arts = {}
    trees = {}
    for a in articles:
        arts.update(sha_manifest(reused_artifact_paths(a)))
        trees[ARTICLES[a]["src"]] = tree_listing(ARTICLES[a]["src"])
    return {"code": code, "reused_artifacts": arts, "src_trees": trees,
            "shared_review_queue_tree": tree_listing(SHARED_QUEUE_ROOT)}


def compare_snapshots(before: dict, after: dict) -> dict:
    diffs = []
    for sec in ("code", "reused_artifacts", "src_trees", "shared_review_queue_tree"):
        b, a = before.get(sec, {}), after.get(sec, {})
        if sec == "src_trees":
            for root in set(b) | set(a):
                if b.get(root) != a.get(root):
                    diffs.append({"section": sec, "root": root})
        elif b != a:
            for k in sorted(set(b) | set(a)):
                if b.get(k) != a.get(k):
                    diffs.append({"section": sec, "path": k})
    return {"identical": not diffs, "diffs": diffs[:50]}


# ------------------------------------------------------------
# 入力複製 (R-03)
# ------------------------------------------------------------
def copy_inputs(article: str, out_root: str = OUT_ROOT) -> str:
    """src runの再利用入力を <out_root>/<article>/_inputs/ へ複製する。複製後は複製のみ参照する。
    既に複製済みなら sha一致を確認して再利用(不一致は例外)。戻り値=_inputs dir。"""
    src = ARTICLES[article]["src"]
    dst = f"{out_root}/{article}/_inputs"
    manifest = {}
    for rel in INPUT_FILES:
        s, d = f"{src}/{rel}", f"{dst}/{rel}"
        if not os.path.isfile(s):
            raise FileNotFoundError(f"input missing (read-only source): {s}")
        s_sha = sha256_file(s)
        if os.path.isfile(d):
            if sha256_file(d) != s_sha:
                raise RuntimeError(f"_inputs copy differs from source (refuse to overwrite): {d}")
        else:
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copyfile(s, d)
        manifest[rel] = {"src": s, "sha256": s_sha}
    save_json(f"{dst}/_copy_manifest.json", {"article": article, "source_run": src, "files": manifest})
    return dst


def load_article_inputs(inputs_dir: str) -> dict:
    d = {
        "draft": load_json(f"{inputs_dir}/research_ledger/fact_ledger_draft.json"),
        "m0_verification": load_json(f"{inputs_dir}/research_ledger/fact_ledger_verification.json"),
        "m0_ledger_text": load_text(f"{inputs_dir}/research_ledger/verified_fact_ledger.txt"),
        "m0_evidence": load_json(f"{inputs_dir}/storyline_b3/fact_selection_evidence.json"),
        "m0_brief_md": load_text(f"{inputs_dir}/storyline_b3/selected_brief.md"),
        "full_ledger": load_json(f"{inputs_dir}/storyline_b3/full_ledger.json"),
        "ledger_runtime": load_json(f"{inputs_dir}/research_ledger/runtime_evidence.json"),
        "b3_runtime": load_json(f"{inputs_dir}/storyline_b3/runtime_evidence.json"),
        "m0_verification_record": load_json(f"{inputs_dir}/research_ledger/audit/verification_full_record.json"),
    }
    d["topic"] = d["full_ledger"]["topic"]
    d["m0_verdicts"] = {v["fact_id"]: v for v in d["m0_verification"]["verifications"]}
    return d


# ------------------------------------------------------------
# 予算guard (R-02): web_search費用込み。compute_stage_cost_breakdownと同算式
# ------------------------------------------------------------
class BudgetStop(RuntimeError):
    """承認額(Stage上限/累計上限/日次soft)超過見込みでのSTOP。確定ファイルを出さない。"""


def _row_usd(rec: dict, price) -> float:
    provider = rec.get("provider")
    model = rec.get("model_id") or rec.get("model")
    if provider == "openai" and model:
        in_tok = rec.get("input_tokens") or 0
        out_tok = rec.get("output_tokens") or 0
        usd = in_tok * price("openai", model, "input_tokens") / 1e6
        usd += out_tok * price("openai", model, "output_tokens") / 1e6
        usd += efam.web_search_call_usd(rec, price)
        return usd
    return 0.0


def cost_by_stage_tag(log_path: str, theme: str | None = None) -> dict:
    """{stage_tag: {"llm_jpy","web_search_jpy","total_jpy","calls","web_search_calls","input_tokens","output_tokens"}}
    式は er019 compute_stage_cost_breakdown と同一(cached tokenは割引せず入力単価=保守側。web_search込み)。"""
    price = efam._load_pricing()
    out = {}
    for rec in read_jsonl(log_path):
        if theme is not None and rec.get("theme") != theme:
            continue
        stage = rec.get("stage") or "UNTAGGED"
        provider, model = rec.get("provider"), rec.get("model_id") or rec.get("model")
        if not (provider == "openai" and model):
            continue
        in_tok = rec.get("input_tokens") or 0
        out_tok = rec.get("output_tokens") or 0
        llm = (in_tok * price("openai", model, "input_tokens") / 1e6
               + out_tok * price("openai", model, "output_tokens") / 1e6)
        ws = efam.web_search_call_usd(rec, price)
        e = out.setdefault(stage, {"llm_jpy": 0.0, "web_search_jpy": 0.0, "calls": 0, "web_search_calls": 0,
                                   "input_tokens": 0, "output_tokens": 0})
        e["llm_jpy"] += llm * efam.USD_JPY
        e["web_search_jpy"] += ws * efam.USD_JPY
        e["calls"] += 1
        e["web_search_calls"] += rec.get("web_search_call_count") or 0
        e["input_tokens"] += in_tok
        e["output_tokens"] += out_tok
    for e in out.values():
        e["total_jpy"] = round(e["llm_jpy"] + e["web_search_jpy"], 3)
        e["llm_jpy"] = round(e["llm_jpy"], 3)
        e["web_search_jpy"] = round(e["web_search_jpy"], 3)
    return out


def _jst_date(ts: str | None) -> str | None:
    if not ts:
        return None
    try:
        dt = datetime.datetime.fromisoformat(ts)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()


class Budget:
    """Stage上限・累計上限・日次softの全てを呼出ごとに判定する。承認額超過見込みでBudgetStop。"""

    def __init__(self, usage_log: str, stage: str, out_root: str = OUT_ROOT, other_spend_today_jpy: float = 0.0,
                 stage_caps: dict | None = None, cum_cap: float | None = None, daily_soft: float | None = None):
        self.usage_log = usage_log
        self.stage = stage
        self.out_root = out_root
        self.other_today = other_spend_today_jpy
        self.stage_caps = dict(stage_caps or STAGE_CAPS_JPY)
        self.cum_cap = CUM_CAP_JPY if cum_cap is None else cum_cap
        self.daily_soft = DAILY_SOFT_JPY if daily_soft is None else daily_soft
        if stage not in self.stage_caps:
            raise ValueError(f"unknown stage {stage}")

    def spent(self) -> dict:
        price = efam._load_pricing()
        total = 0.0
        by_stage, today = {}, 0.0
        today_jst = _jst_date(datetime.datetime.now(datetime.timezone.utc).isoformat())
        for rec in read_jsonl(self.usage_log):
            if rec.get("theme") != THEME_TAG:
                continue
            jpy = _row_usd(rec, price) * efam.USD_JPY
            grp = str(rec.get("stage") or "UNTAGGED").split("|")[0]
            by_stage[grp] = by_stage.get(grp, 0.0) + jpy
            total += jpy
            if _jst_date(rec.get("timestamp")) == today_jst:
                today += jpy
        return {"total": total, "by_stage": by_stage, "today_trial": today}

    def check(self, est_jpy: float, label: str) -> dict:
        s = self.spent()
        stage_spent = s["by_stage"].get(self.stage, 0.0)
        reasons = []
        if stage_spent + est_jpy > self.stage_caps[self.stage]:
            reasons.append(f"stage_cap[{self.stage}]={self.stage_caps[self.stage]}")
        if s["total"] + est_jpy > self.cum_cap:
            reasons.append(f"cumulative_cap={self.cum_cap}")
        if s["today_trial"] + self.other_today + est_jpy > self.daily_soft:
            reasons.append(f"daily_soft={self.daily_soft}(other_today={self.other_today})")
        if reasons:
            info = {"status": "STOP_BUDGET", "label": label, "est_next_call_jpy": est_jpy, "spent": s,
                    "reasons": reasons, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}
            save_json(f"{self.out_root}/STOP_BUDGET.json", info)
            raise BudgetStop(f"[STOP_BUDGET] {label}: {reasons} spent={s}")
        return s

    def check_before(self, est_jpy: float, label: str) -> dict:
        return self.check(est_jpy, label)

    def check_after(self, label: str) -> dict:
        return self.check(0.0, label + ":after")


# ------------------------------------------------------------
# 呼出文脈 (cl.logging_context + stub向けtag)
# ------------------------------------------------------------
_TAG = {"stage_tag": None}


@contextmanager
def trial_context(stage_tag: str):
    prev = _TAG["stage_tag"]
    _TAG["stage_tag"] = stage_tag
    try:
        with cl.logging_context(THEME_TAG, stage_tag):
            yield
    finally:
        _TAG["stage_tag"] = prev


def ensure_cost_logger(path: str) -> None:
    """プロセス開始時に必ず実行(R-02)。実API呼出はこのlogへ全て記録される。"""
    cl.install(path)


# ------------------------------------------------------------
# Verifier (R-01: Production run_verification_for_topicの複製、Promptのみ引数)
# ------------------------------------------------------------
def build_verifier_prompt(topic: str, draft_subset: dict, cap: bool) -> str:
    base = vfl01.build_verification_prompt(topic, draft_subset)
    return base + CAP_SUFFIX if cap else base


def prompt_diff_evidence(topic: str = "(topic)", draft_subset: dict | None = None) -> str:
    sample = draft_subset or {"facts": [{"fact_id": "F01", "claim": "sample"}]}
    nl = chr(10)
    a = (build_verifier_prompt(topic, sample, False) + nl).splitlines(keepends=True)
    b = (build_verifier_prompt(topic, sample, True) + nl).splitlines(keepends=True)
    return "".join(difflib.unified_diff(a, b, "production_verification_prompt", "trial_capped_prompt", n=1))


def subset_draft(draft: dict, fact_ids: list) -> dict:
    want = list(fact_ids)
    by_id = {f["fact_id"]: f for f in draft["facts"]}
    missing = [i for i in want if i not in by_id]
    if missing:
        raise KeyError(f"fact_ids not in draft: {missing}")
    order = [f["fact_id"] for f in draft["facts"] if f["fact_id"] in set(want)]
    return {"facts": [by_id[i] for i in order]}


def extract_search_calls(response) -> list:
    rows = []
    seq = 0
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) != "web_search_call":
            continue
        seq += 1
        action = getattr(item, "action", None)
        qs = getattr(action, "queries", None) if action is not None else None
        if not qs:
            q = getattr(action, "query", None) if action is not None else None
            qs = [q] if q else []
        rows.append({"seq": seq, "action_type": getattr(action, "type", None) if action is not None else None,
                     "queries": list(qs), "url": getattr(action, "url", None) if action is not None else None,
                     "status": getattr(item, "status", None)})
    return rows


def verify_facts_trial(client, topic: str, draft: dict, fact_ids: list, *, cap: bool, work_dir: str,
                       label: str, stage_tag: str, budget: Budget, est_jpy: float) -> dict:
    """Production run_verification_for_topic の複製。model/reasoning/tools/schema/developer message同一、
    Promptのみ cap引数で差し替え。呼出単位のweb_search_callを web_search_calls.jsonl へ保存。"""
    sub = subset_draft(draft, fact_ids)
    prompt = build_verifier_prompt(topic, sub, cap)
    budget.check_before(est_jpy, f"verify:{label}")
    t0 = time.time()
    with trial_context(stage_tag):
        response = client.responses.create(
            model=vfl01.MODEL,
            reasoning={"effort": vfl01.REASONING_EFFORT},
            tools=[{"type": "web_search"}],
            text={"format": {"type": "json_schema", **vfl01.VERIFICATION_JSON_SCHEMA}},
            input=[
                {"role": "developer", "content": vfl01.VERIFICATION_DEVELOPER_MESSAGE},
                {"role": "user", "content": prompt},
            ],
        )
    latency = time.time() - t0
    budget.check_after(f"verify:{label}")
    parsed = json.loads(response.output_text)
    calls = extract_search_calls(response)
    for c in calls:
        append_jsonl(f"{work_dir}/web_search_calls.jsonl",
                     {"request_label": label, "stage_tag": stage_tag, "fact_ids_in_request": list(fact_ids),
                      "cap_prompt": cap, **c})
    n_facts = len(fact_ids)
    record = {"label": label, "cap_prompt": cap, "fact_ids": list(fact_ids), "model": response.model,
              "response_id": response.id, "latency_seconds": latency,
              "web_search_call_count": len(calls),
              "action_type_counts": _count_by(calls, "action_type"),
              "query_count": sum(len(c["queries"]) for c in calls),
              "calls_per_fact_avg": round(len(calls) / n_facts, 3) if n_facts else None,
              "exceeds_soft_cap_estimate": bool(cap and len(calls) > CAP_PER_FACT * n_facts),
              "prompt_sha256": sha256_bytes(prompt.encode("utf-8"))}
    save_json(f"{work_dir}/verify_{label}.json", {**record, "parsed": parsed, "prompt": prompt})
    return {"parsed": parsed, "record": record}


def _count_by(rows: list, key: str) -> dict:
    out = {}
    for r in rows:
        k = r.get(key) or "unknown"
        out[k] = out.get(k, 0) + 1
    return out


# ------------------------------------------------------------
# 候補Ledger描画 ([UNVERIFIED]対応) / B3 (R-06)
# ------------------------------------------------------------
FACT_ID_LINE_RE_TRIAL = re.compile(
    r"^\[(?:VERIFIED|UNVERIFIED|AMBIGUOUS[^\]]*)\]\s+([A-Za-z0-9_\-]+):", re.MULTILINE)
UNVERIFIED_TAG = "[UNVERIFIED]"
VERIFIED_PHRASE = "独立検証済みのFull Fact Ledger"
UNVERIFIED_PHRASE = ("独立検証前のFull Fact Ledger候補(各Factには[VERIFIED]/[AMBIGUOUS]/[UNVERIFIED]のタグが付いています。"
                     "[UNVERIFIED]は未検証で、選定後に選ばれたFactだけを独立検証します)")


def extract_ids_trial(ledger_text: str) -> list:
    return sorted(set(FACT_ID_LINE_RE_TRIAL.findall(ledger_text or "")))


def render_candidate_ledger(draft: dict, verdicts: dict) -> str:
    """verdicts: {fact_id: {"verdict","verification_notes"}}。VERIFIED/AMBIGUOUS=Production関数で描画、
    未検証=[UNVERIFIED](+Researcherのambiguity欄)、REJECTED=候補本文から外す。draft順。"""
    blocks = []
    for fact in draft["facts"]:
        v = verdicts.get(fact["fact_id"])
        if v is None:
            lines = [f"{UNVERIFIED_TAG} {fact['fact_id']}: {fact['claim']}"]
            for key, label in (("scope", "scope"), ("conditions", "conditions"), ("date_or_period", "date_or_period")):
                if fact.get(key):
                    lines.append(f"  {label}: {fact[key]}")
            if fact.get("numeric_value"):
                lines.append(f"  numeric_value: {fact['numeric_value']} (numeric_scope: {fact.get('numeric_scope') or '未指定'})")
            if fact.get("causal_strength") and fact["causal_strength"] != "NOT_APPLICABLE":
                lines.append(f"  causal_strength: {fact['causal_strength']}")
            if fact.get("ambiguity"):
                lines.append(f"  researcher_ambiguity: {fact['ambiguity']}")
            if fact.get("notes_for_writer"):
                lines.append(f"  notes_for_writer: {fact['notes_for_writer']}")
            lines.append("")
            blocks.append("\n".join(lines))
            continue
        if v["verdict"] == "REJECTED":
            continue
        text, _counts, _kept = vfl01.build_verified_ledger_text({"facts": [fact]}, {"verifications": [{
            "fact_id": fact["fact_id"], "verdict": v["verdict"],
            "verification_notes": v.get("verification_notes", "")}]})
        blocks.append(text)
    return "\n".join(blocks)


def build_user_prompt_trial(topic: str, ledger_text: str, allow_unverified: bool) -> str:
    tmpl = b3.USER_PROMPT_TEMPLATE
    if allow_unverified:
        if tmpl.count(VERIFIED_PHRASE) != 1:
            raise RuntimeError("[STOP] B3 Prompt側の想定文言が変わった。設計v2 R-06の差分は『検証済み』の語とタグのみ。Fable確認が必要")
        tmpl = tmpl.replace(VERIFIED_PHRASE, UNVERIFIED_PHRASE)
    return tmpl.format(topic=topic, ledger_text=ledger_text, fact_test_definitions=b3.FACT_TEST_DEFINITIONS_JA)


class B3TechnicalFailure(RuntimeError):
    def __init__(self, msg, attempts_log):
        super().__init__(msg)
        self.attempts_log = attempts_log


def select_b3_trial(client, topic: str, ledger_text: str, *, work_dir: str, label: str, stage_tag: str,
                    budget: Budget, extra_note: str = "", allow_unverified: bool = False,
                    est_jpy: float = EST_B3_JPY) -> dict:
    """run_storyline_b3_selection の複製(同じ検証・技術retry構造: 全IDのテスト網羅+1回の技術retry)。
    差異=ID抽出regex([UNVERIFIED]対応)・Promptの『検証済み』語(allow_unverified時のみ)・logging theme。
    model=routing.require_model経由、返却modelを照合(不一致はSTOP)。"""
    model = routing.require_model("FAMILY_X_STORYLINE_B3", routing.PROCESS_MODEL_MAP["FAMILY_X_STORYLINE_B3"])
    ledger_ids = extract_ids_trial(ledger_text)
    attempts_log, last_exc = [], None
    for attempt in (1, 2):
        note = extra_note if attempt == 1 else extra_note + b3.RETRY_APPEND_NOTE
        budget.check_before(est_jpy, f"b3:{label}#{attempt}")
        user_prompt = build_user_prompt_trial(topic, ledger_text, allow_unverified) + note
        t0 = time.time()
        try:
            with trial_context(stage_tag):
                response = client.responses.create(
                    model=model, reasoning={"effort": vfl01.REASONING_EFFORT},
                    text={"format": {"type": "json_schema", **b3.STORYLINE_B3_JSON_SCHEMA}},
                    input=[{"role": "developer", "content": b3.DEVELOPER_MESSAGE},
                           {"role": "user", "content": user_prompt}])
            budget.check_after(f"b3:{label}#{attempt}")
            parsed = json.loads(response.output_text)
        except BudgetStop:
            raise
        except Exception as exc:  # noqa: BLE001
            attempts_log.append({"attempt": attempt, "error": str(exc)[:500]})
            last_exc = exc
            continue
        if not str(response.model or "").startswith(model):
            raise RuntimeError(f"[STOP] B3返却modelが{model}で始まらない: {response.model!r}")
        errors = b3.validate_selection_output(parsed, ledger_ids)
        hard = [e for e in errors if not e.startswith("RECHECK_NOTE_MISSING")]
        attempts_log.append({"attempt": attempt, "validation_errors": errors})
        if not hard:
            res = {"parsed": parsed, "model": response.model, "response_id": response.id,
                   "latency_seconds": time.time() - t0, "attempts": attempt, "retried": attempt > 1,
                   "soft_warnings": errors, "ledger_fact_ids": ledger_ids, "attempts_log": attempts_log,
                   "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
                   "allow_unverified": allow_unverified}
            save_json(f"{work_dir}/b3_{label}.json", {**res, "user_prompt": user_prompt})
            return res
    raise B3TechnicalFailure(f"[STOP] B3: 2回試行しても技術的に有効な出力を得られない label={label} "
                             f"attempts_log={attempts_log} last_exc={last_exc}", attempts_log)


# ------------------------------------------------------------
# 案2 loop (R-06, ユーザー§4の手順)
# ------------------------------------------------------------
def build_reselect_note(rejected: list, verdicts: dict, draft: dict, unverified_ids: list) -> str:
    lines = ["\n\n【再選定の指示(Trial)】前回選んだFactのうち、独立検証でREJECTED(不合格)となったものがあります。"
             "REJECTEDのFactは候補一覧から外しました。REJECTEDのFactは選定してはいけません(選定禁止)。"
             "REJECTEDなしでStorylineが成立するか再評価し、必要なら別のFactを選び直してください。"
             "Storylineも必要なら見直してください。"]
    for rid in rejected:
        lines.append(f"- REJECTED {rid}: {verdicts[rid].get('verification_notes', '')}")
    done = [i for i, v in verdicts.items() if v["verdict"] != "REJECTED"]
    if done:
        lines.append("【検証済みFactの判定】")
        for i in done:
            lines.append(f"- {i}: {verdicts[i]['verdict']} / {verdicts[i].get('verification_notes', '')[:300]}")
    if unverified_ids:
        lines.append("【未検証の候補】" + ", ".join(unverified_ids)
                     + " (新たに選んだFactだけを選定後に独立検証します)")
    return "\n".join(lines)


CONFIRM_CONSTRAINT = ("このFactを使う場合、Storyline・Briefでは不確実性・留保条件を明示し、"
                      "無条件の断定をしてはならない")


def build_confirm_note(rejected: list, ambiguous_new: list, verdicts: dict, draft: dict, unverified_ids: list) -> str:
    """委任_07 D2: 最終B3確認パス用note。REJECTEDのみの場合は既存build_reselect_noteと同一文面(挙動不変)。
    AMBIGUOUS(B3が検証結果を見ずに選んだもの)がある場合は、REJECTED/AMBIGUOUS各ID+理由+使用上の制約、
    検証済み他Factの判定、未検証候補、Storyline再評価の指示を含める。"""
    if rejected and not ambiguous_new:
        return build_reselect_note(rejected, verdicts, draft, unverified_ids)
    lines = ["\n\n【最終確認の指示(Trial)】前回選んだFactの独立検証が終わりました。検証結果を踏まえ、"
             "Storylineの構成を再評価し、必要ならFactを選び直してください。"
             "REJECTEDのFactは選定してはいけません(選定禁止)。AMBIGUOUSのFactは無条件に断定してはいけません。"]
    for rid in rejected:
        lines.append(f"- REJECTED {rid}: {verdicts[rid].get('verification_notes', '')}"
                     "(候補一覧から外しました。選定禁止)")
    for aid in ambiguous_new:
        lines.append(f"- AMBIGUOUS {aid}: {verdicts[aid].get('verification_notes', '')[:600]}"
                     f" / 使用上の制約: {CONFIRM_CONSTRAINT}")
    others = [i for i, v in verdicts.items() if v["verdict"] != "REJECTED" and i not in set(ambiguous_new)]
    if others:
        lines.append("【検証済みの他のFactの判定】")
        for i in others:
            lines.append(f"- {i}: {verdicts[i]['verdict']} / {verdicts[i].get('verification_notes', '')[:300]}")
    if unverified_ids:
        lines.append("【未検証の候補】" + ", ".join(unverified_ids)
                     + " (新たに選んだFactだけを選定後に独立検証します)")
    lines.append("Storylineの構成を再評価し、必要ならFactを選び直してください。")
    return "\n".join(lines)


def _ambiguous_unseen(sel_ids: list, verdicts: dict, sel_visible: dict) -> list:
    """D1(ii): 選定FactのうちAMBIGUOUSで、sel生成B3呼出の候補Ledgerに[AMBIGUOUS]として見えていなかったもの。"""
    return [i for i in sel_ids if verdicts[i]["verdict"] == "AMBIGUOUS"
            and (sel_visible.get(i) or {}).get("verdict") != "AMBIGUOUS"]


def select_then_verify(client, topic: str, draft: dict, *, work_dir: str, stage_prefix: str, budget: Budget,
                       cap: bool, max_reselect: int = 2, shared_initial: dict | None = None,
                       est_verify_jpy: float = EST_VERIFY_SEL_JPY, est_b3_jpy: float = EST_B3_JPY,
                       resume: dict | None = None) -> dict:
    """戻り値 status=COMPLETED | UNRESOLVED。UNRESOLVEDでは確定ledger/briefを返さない。
    委任_07(ユーザー#107): 選定Factの検証後、(i)REJECTEDなし かつ (ii)AMBIGUOUSは全て選定B3呼出の候補Ledgerで
    既に提示済み、の両方を満たすときだけ確定する。満たさなければ検証結果をB3へ返す(再選定/確認パス)。
    初回B3後のB3呼出は再選定と確認パスを合算して max_reselect(=2)回まで。
    resume(1a補正用)={"sel","verdicts","sel_visible","sel_label","b3_used"}: 既存methodの最終sel・検証結果から再開。"""
    all_ids = [f["fact_id"] for f in draft["facts"]]
    rounds: list = []
    n_reselect = n_confirm = 0
    if resume is None:
        verdicts: dict = {}
        if shared_initial is not None:
            sel = shared_initial
        else:
            sel = select_b3_trial(client, topic, render_candidate_ledger(draft, verdicts), work_dir=work_dir,
                                  label="initial", stage_tag=f"{stage_prefix}|b3_initial", budget=budget,
                                  allow_unverified=True, est_jpy=est_b3_jpy)
            save_json(f"{work_dir}/initial_b3.json", sel)
        sel_visible, sel_label, trigger, b3_used = {}, "initial", "INITIAL", 0
    else:
        verdicts = copy.deepcopy(resume["verdicts"])
        sel, sel_visible = resume["sel"], copy.deepcopy(resume["sel_visible"])
        sel_label, trigger, b3_used = resume["sel_label"], "RESUMED_FROM_SOURCE_FINAL", resume["b3_used"]
    b3_before = b3_used
    shared_flag = shared_initial is not None

    def _counts():
        return {"reselect_count": n_reselect, "confirm_pass_count": n_confirm,
                "b3_calls_after_initial": b3_used, "b3_calls_before_this_run": b3_before}

    while True:
        r = len(rounds)
        sel_ids = list(sel["parsed"]["selected_fact_ids"])
        to_verify = [i for i in all_ids if i in sel_ids and i not in verdicts]   # 検証済みは再利用
        rnd = {"round": r, "trigger": trigger, "b3_label": sel_label, "selected_fact_ids": sel_ids,
               "verified_now": to_verify,
               "reused_verdicts": [i for i in sel_ids if i in verdicts and i not in to_verify]}
        if to_verify:
            vres = verify_facts_trial(client, topic, draft, to_verify, cap=cap, work_dir=work_dir,
                                      label=f"r{r}", stage_tag=f"{stage_prefix}|verify_sel_r{r}", budget=budget,
                                      est_jpy=est_verify_jpy)
            got = {v["fact_id"]: v for v in vres["parsed"]["verifications"]}
            for i in to_verify:
                v = got.get(i)
                if v is None:      # Productionと同じ安全側(検証結果なし=AMBIGUOUS)
                    v = {"fact_id": i, "verdict": "AMBIGUOUS", "verification_notes": "(検証結果なし、安全側でAMBIGUOUS扱い)"}
                    rnd.setdefault("missing_verification", []).append(i)
                verdicts[i] = {"verdict": v["verdict"], "verification_notes": v["verification_notes"], "round": r}
            rnd["verify_record"] = vres["record"]
        rejected = [i for i in sel_ids if verdicts[i]["verdict"] == "REJECTED"]
        ambiguous = [i for i in sel_ids if verdicts[i]["verdict"] == "AMBIGUOUS"]
        amb_unseen = _ambiguous_unseen(sel_ids, verdicts, sel_visible)
        if rejected or amb_unseen:
            confirm = "REQUIRED"
        elif not ambiguous:
            confirm = "NOT_NEEDED_ALL_VERIFIED"
        else:
            confirm = "NOT_NEEDED_AMBIGUOUS_ALREADY_VISIBLE"
        rnd.update({"rejected": rejected, "ambiguous_selected": ambiguous, "ambiguous_unseen": amb_unseen,
                    "ambiguous_visible_to_b3": not amb_unseen, "confirm_pass": confirm})
        rounds.append(rnd)
        if confirm != "REQUIRED":
            return _finalize_sel(draft, sel, sel_ids, verdicts, rounds, shared_flag, sel_visible, _counts())
        if b3_used >= max_reselect:
            unmet = (["REJECTED_SELECTED"] if rejected else []) + (["AMBIGUOUS_NOT_CONFIRMED"] if amb_unseen else [])
            res = {"status": "UNRESOLVED", "reason": "RESELECT_LIMIT_REACHED", "max_reselect": max_reselect,
                   "unmet": unmet, "rejected_at_limit": rejected, "ambiguous_unconfirmed_at_limit": amb_unseen,
                   "rounds": rounds, "verdicts": verdicts, **_counts()}
            save_json(f"{work_dir}/unresolved.json", res)
            return res
        unverified = [i for i in all_ids if i not in verdicts]
        note = build_confirm_note(rejected, amb_unseen, verdicts, draft, unverified)
        candidate = render_candidate_ledger(draft, verdicts)
        if rejected:
            kind, trigger = "reselect", ("RESELECT_REJECTED+CONFIRM_AMBIGUOUS" if amb_unseen else "RESELECT_REJECTED")
        else:
            kind, trigger = "confirm", "CONFIRM_AMBIGUOUS"
        label = f"{kind}{b3_used + 1}"
        visible_now = copy.deepcopy(verdicts)           # この呼出の候補Ledgerに見えている判定
        try:
            sel = select_b3_trial(client, topic, candidate, work_dir=work_dir, label=label,
                                  stage_tag=f"{stage_prefix}|b3_{label}", budget=budget,
                                  extra_note=note, allow_unverified=True, est_jpy=est_b3_jpy)
        except B3TechnicalFailure as exc:
            b3_used += 1
            rej_picked = any("UNKNOWN_FACT_ID" in str(a) and any(x in str(a) for x in rejected)
                             for a in exc.attempts_log)
            res = {"status": "UNRESOLVED",
                   "reason": "B3_TECHNICAL_FAILURE" + ("_REJECTED_ID_RESELECTED" if rej_picked else ""),
                   "rejected_reselected_detected": rej_picked, "attempts_log": exc.attempts_log,
                   "rounds": rounds, "verdicts": verdicts, **_counts()}
            save_json(f"{work_dir}/unresolved.json", res)
            return res
        b3_used += 1
        if kind == "reselect":
            n_reselect += 1
        else:
            n_confirm += 1
        sel_visible, sel_label = visible_now, label
        # REJECTED IDを選び直そうとして(技術retryで)修正された場合も痕跡として記録
        rej_try = [a for a in sel["attempts_log"] if any("UNKNOWN_FACT_ID" in str(e) and any(x in str(e) for x in rejected)
                                                         for e in a.get("validation_errors", []))]
        rounds[-1]["rejected_reselect_attempts_detected"] = len(rej_try)


def _finalize_sel(draft, sel, sel_ids, verdicts, rounds, shared, sel_visible=None, counts=None) -> dict:
    # 防御: REJECTED混入・AMBIGUOUS未提示のままの確定は構造上起こさない(起きたら実装バグとして停止)
    if any(verdicts[i]["verdict"] == "REJECTED" for i in sel_ids):
        raise AssertionError("REJECTED selected at finalize")
    if sel_visible is not None and _ambiguous_unseen(sel_ids, verdicts, sel_visible):
        raise AssertionError("AMBIGUOUS finalized without being shown to B3")
    facts = [f for f in draft["facts"] if f["fact_id"] in set(sel_ids)]
    ledger_text, counts_v, kept = vfl01.build_verified_ledger_text(
        {"facts": facts}, {"verifications": [{"fact_id": f["fact_id"], "verdict": verdicts[f["fact_id"]]["verdict"],
                                              "verification_notes": verdicts[f["fact_id"]]["verification_notes"]}
                                             for f in facts]})
    counts = counts or {"reselect_count": len(rounds) - 1, "confirm_pass_count": 0,
                        "b3_calls_after_initial": len(rounds) - 1, "b3_calls_before_this_run": 0}
    return {"status": "COMPLETED", "selection": sel, "selected_fact_ids": sel_ids, "verdicts": verdicts,
            "ledger_text": ledger_text, "verdict_counts": counts_v, "rounds": rounds,
            "shared_initial_b3": shared, "final_confirm_pass": rounds[-1]["confirm_pass"], **counts}


# ------------------------------------------------------------
# 出力(run-dir形)とFact Lock/RF整合 (4-5)
# ------------------------------------------------------------
def write_run_layout(method_dir: str, topic: str, ledger_text: str, selection: dict, extra_runtime: dict) -> None:
    """Production run-dirと同じ形で method_dir に書く(契約検証・producer入力用)。確定ファイルはここだけ。"""
    parsed = selection["parsed"]
    ledger_ids = extract_ids_trial(ledger_text)
    save_text(f"{method_dir}/research_ledger/verified_fact_ledger.txt", ledger_text)
    save_json(f"{method_dir}/storyline_b3/full_ledger.json", b3.build_full_ledger_record(topic, ledger_text, ledger_ids))
    save_text(f"{method_dir}/storyline_b3/selected_brief.md",
              b3.build_selected_brief_markdown({"parsed": parsed}))
    save_json(f"{method_dir}/storyline_b3/fact_selection_evidence.json", {
        "selected_storyline": parsed["selected_storyline"], "full_ledger_fact_ids": ledger_ids,
        "fact_tests": parsed["fact_tests"], "selected_fact_ids": parsed["selected_fact_ids"],
        "selected_fact_brief_text": parsed["selected_fact_brief"], "recheck_note": parsed["recheck_note"],
        "soft_warnings": selection.get("soft_warnings", [])})
    save_json(f"{method_dir}/storyline_b3/runtime_evidence.json", {
        "model_id_actual": selection.get("model"), "response_id": selection.get("response_id"),
        "attempts": selection.get("attempts"), "retried": selection.get("retried"),
        "attempts_log": selection.get("attempts_log"), **extra_runtime})


def assert_under_out_root(path: str, out_root: str = OUT_ROOT) -> None:
    ap, ar = os.path.abspath(path), os.path.abspath(out_root)
    if os.path.commonpath([ap, ar]) != ar:
        raise RuntimeError(f"[STOP] 出力先がTrial領域外: {path}")


def contract_check(method_dir: str, out_root: str = OUT_ROOT) -> dict:
    """JPY0。複製dir(er082配下)に対し producer -> validate_annotated_b3、台帳完全性(parse_ledger_complete)。
    producerは入力dirの注記artifact削除・evidence上書きを行うので、Production/既存成果物dirには決して向けない。"""
    assert_under_out_root(method_dir, out_root)
    import er053_b3_annotation_contract_01 as contract
    import er053_b3_deterministic_producer_01 as prod
    import er053_risk_flagger_production_01 as rfp
    res = {"method_dir": method_dir, "producer": None, "validate": None, "ledger_complete": None}
    try:
        p = prod.produce_annotated_b3(method_dir)
        res["producer"] = {"status": "PASS", "n_facts": p["n_facts"], "llm_calls": p["manifest"]["llm_calls"]}
    except Exception as exc:  # noqa: BLE001
        res["producer"] = {"status": "FAIL", "error": f"{type(exc).__name__}: {str(exc)[:400]}"}
    if res["producer"]["status"] == "PASS":
        try:
            contract.validate_annotated_b3(method_dir)
            res["validate"] = {"status": "PASS"}
        except Exception as exc:  # noqa: BLE001
            res["validate"] = {"status": "FAIL", "error": f"{type(exc).__name__}: {str(exc)[:400]}"}
    try:
        facts = rfp.parse_ledger_complete(load_text(f"{method_dir}/research_ledger/verified_fact_ledger.txt"))
        res["ledger_complete"] = {"status": "PASS", "n_facts": len(facts)}
    except Exception as exc:  # noqa: BLE001
        res["ledger_complete"] = {"status": "FAIL", "error": f"{type(exc).__name__}: {str(exc)[:300]}"}
    res["all_pass"] = all((res[k] or {}).get("status") == "PASS" for k in ("producer", "validate", "ledger_complete"))
    return res


# ------------------------------------------------------------
# 指標: Jaccard / verdict遷移 / 既知欠陥3値 / R-07中心Fact
# ------------------------------------------------------------
def jaccard(a: list, b: list) -> float | None:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return None
    return round(len(sa & sb) / len(sa | sb), 3)


def verdict_transitions(m0_verdicts: dict, method_verdicts: dict) -> dict:
    trans, promotions, demotions = {}, [], []
    rank = {"REJECTED": 0, "AMBIGUOUS": 1, "VERIFIED": 2}
    for fid, v in method_verdicts.items():
        base = (m0_verdicts.get(fid) or {}).get("verdict")
        key = f"{base}->{v['verdict']}"
        trans[key] = trans.get(key, 0) + 1
        if base and rank[v["verdict"]] > rank[base]:
            promotions.append(fid)
        if base == "VERIFIED" and v["verdict"] != "VERIFIED":
            demotions.append(fid)
    return {"counts": trans, "promotions_to_verified_or_up": promotions, "demotions_from_verified": demotions}


def known_defect_status(article: str, final_ids: list, final_verdicts: dict) -> dict:
    out = {}
    for fid in ARTICLES[article]["known_defects"]:
        if fid not in final_ids:
            out[fid] = "c_not_selected"
        elif final_verdicts.get(fid, {}).get("verdict") == "VERIFIED":
            out[fid] = "b_selected_missed_NG"
        else:
            out[fid] = "a_selected_detected"
    return out


_NUM_RE = re.compile(r"\d[\d,\.]*")


def central_facts(storyline: str, draft: dict) -> list:
    """R-07: 『中心Fact』=Storyline行が言及するFact(機械的ヒューリスティック。最終判定はSonnet+Fable)。
    言及の判定=Factのnumeric/claim中の数値表記(2桁以上)がStoryline文に現れる、またはclaimの8文字以上の連続部分がStorylineに現れる。"""
    out = []
    for f in draft["facts"]:
        text = " ".join(str(f.get(k) or "") for k in ("claim", "numeric_value"))
        nums = {n.strip(",.") for n in _NUM_RE.findall(text) if len(n.strip(",.")) >= 2}
        hit = any(n in storyline for n in nums)
        if not hit:
            claim = str(f.get("claim") or "")
            for i in range(0, max(0, len(claim) - 8)):
                if claim[i:i + 8] in storyline:
                    hit = True
                    break
        if hit:
            out.append(f["fact_id"])
    return out


def ambiguous_central_assertions(storyline: str, draft: dict, final_verdicts: dict) -> dict:
    c = central_facts(storyline, draft)
    amb = [i for i in c if final_verdicts.get(i, {}).get("verdict") == "AMBIGUOUS"]
    return {"central_fact_ids": c, "ambiguous_central_fact_ids": amb, "count": len(amb),
            "note": "候補件数(機械抽出)。『断定しているか』の最終判定はSonnet+Fable独立判定(R-07、測定のみ)"}


# ------------------------------------------------------------
# dry-run用 StubClient (API 0。保存済み出力から合成)
# ------------------------------------------------------------
class StubClient:
    """OpenAI Responses互換の最小stub。API呼出0。使用量は stub_usage_log に synthetic として記録する。"""

    def __init__(self, scenario: dict, stub_usage_log: str):
        self.sc = scenario
        self.log = stub_usage_log
        self.n = 0
        self.calls = 0
        self.b3_n = 0
        self.responses = SimpleNamespace(create=self._create)

    # -- helpers
    def _record(self, model, in_tok, out_tok, ws_calls):
        row = {"theme": THEME_TAG, "stage": _TAG["stage_tag"], "provider": "openai", "api": "responses.create",
               "model_id": model, "attempt_number": self.n, "success": True,
               "usage_source": "SYNTHETIC_DRYRUN_STUB", "web_search_call_count": ws_calls,
               "input_tokens": in_tok, "output_tokens": out_tok,
               "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(), "dry_run_stub": True}
        append_jsonl(self.log, row)

    def _create(self, **kw):
        self.n += 1
        self.calls += 1
        name = kw["text"]["format"]["name"]
        prompt = kw["input"][-1]["content"]
        if name == vfl01.VERIFICATION_JSON_SCHEMA["name"]:
            return self._verify(kw, prompt)
        if name == b3.STORYLINE_B3_JSON_SCHEMA["name"]:
            return self._b3(kw, prompt)
        raise RuntimeError(f"StubClient: unsupported schema {name}")

    def _resp(self, kw, parsed, calls, in_tok, out_tok):
        out_items = [SimpleNamespace(type="web_search_call", status="completed", action=a) for a in calls]
        self._record(kw["model"], in_tok, out_tok, len(calls))
        return SimpleNamespace(output=out_items, output_text=json.dumps(parsed, ensure_ascii=False),
                               model=self.sc.get("model_override") or kw["model"], id=f"stub_resp_{self.n}",
                               usage=SimpleNamespace(input_tokens=in_tok, output_tokens=out_tok))

    # -- verification stub
    def _verify(self, kw, prompt):
        ids = re.findall(r'"fact_id":\s*"([^"]+)"', prompt)
        capped = "【検索回数の上限(Trial指示)】" in prompt
        base = self.sc["m0_verdicts"]
        per = max(1, round(self.sc["m0_total_ws_calls"] / max(1, self.sc["n_facts_all"])))
        vers, calls = [], []
        for fid in ids:
            if fid.startswith("INJ_"):
                missed = fid in self.sc.get("inject_missed_ids", set())
                verdict, note = ("VERIFIED", "[stub] 検出漏れを模擬") if missed else ("REJECTED", "[stub] 改変値を不一致と判定")
            else:
                b = base.get(fid, {"verdict": "AMBIGUOUS", "verification_notes": "[stub] no stored verdict"})
                verdict, note = b["verdict"], "[stub:stored M0 verdict] " + str(b["verification_notes"])[:160]
                if capped and verdict == "VERIFIED" and int(hashlib.sha256(fid.encode()).hexdigest(), 16) % 7 == 0:
                    verdict, note = "AMBIGUOUS", "[stub] 上限3回内で確認できず(合成の降格)"
            vers.append({"fact_id": fid, "verdict": verdict, "verification_notes": note})
            k = min(per, CAP_PER_FACT) if capped else per
            for j in range(k):
                calls.append(SimpleNamespace(type=("search" if j == 0 else ("open_page" if j % 2 else "find")),
                                             queries=[f"[stub] {fid} q{j}"] if j == 0 else None,
                                             query=None, url=None if j == 0 else f"https://example.invalid/{fid}/{j}"))
        return self._resp(kw, {"verifications": vers}, calls, 20000 + 4000 * len(calls) + len(prompt) // 3,
                          500 + 250 * len(ids))

    # -- B3 stub
    def _b3(self, kw, prompt):
        ids = sorted(set(FACT_ID_LINE_RE_TRIAL.findall(prompt)))
        stored = list(self.sc["m0_evidence"]["selected_fact_ids"])
        story = self.sc["m0_evidence"]["selected_storyline"]
        forced = self.sc.get("b3_force_ids")
        script = self.sc.get("b3_script")          # 委任_07: B3呼出順に返すFact ID列(確認パス再現用)
        if script is not None and self.b3_n < len(script):
            forced = script[self.b3_n]
        self.b3_n += 1
        if forced is not None:
            sel = [i for i in forced if i in ids] if not self.sc.get("b3_force_allow_unknown") else list(forced)
        else:
            sel = [i for i in stored if i in ids]
            extra = [i for i in self.sc.get("b3_initial_extra_ids", []) if i in ids and "選定禁止" not in prompt]
            for i in extra:
                if i not in sel:
                    sel.append(i)
            for i in ids:               # 取りこぼした分(REJECTEDで外れた等)を未選定候補から補充
                if len(sel) >= len(stored):
                    break
                if i not in sel:
                    sel.append(i)
        claims = {}
        for fid in ids:
            m = re.search(rf"^\[[^\]]*\]\s+{re.escape(fid)}:\s*(.*)$", prompt, re.MULTILINE)
            claims[fid] = m.group(1) if m else ""
        fact_tests = [{"fact_id": i, "test1_answer": "NO", "test2_answer": "YES", "test3_answer": "YES",
                       "test4_answer": "NO", "decision": "selected" if i in sel else "excluded",
                       "reason": "[stub]"} for i in ids if not i.startswith("__")]
        if forced is not None and self.sc.get("b3_force_allow_unknown"):
            fact_tests = [t for t in fact_tests if t["fact_id"] in ids] + \
                         [{"fact_id": i, "test1_answer": "NO", "test2_answer": "YES", "test3_answer": "YES",
                           "test4_answer": "NO", "decision": "selected", "reason": "[stub]"} for i in sel if i not in ids]
        brief = story + "\n" + "\n".join(f"- {claims.get(i, '')}" for i in sel)
        parsed = {"selected_storyline": story, "fact_tests": fact_tests, "selected_fact_ids": sel,
                  "selected_fact_brief": brief, "recheck_note": ("[stub] 6件以上" if len(sel) >= 6 else None)}
        return self._resp(kw, parsed, [], len(prompt) // 2, 1800)


def contract_check_ledger_only(method_dir: str) -> dict:
    """M0p用(B3なし): 台帳完全性(parse_ledger_complete)のみ。JPY0。"""
    import er053_risk_flagger_production_01 as rfp
    try:
        facts = rfp.parse_ledger_complete(load_text(f"{method_dir}/research_ledger/verified_fact_ledger.txt"))
        return {"status": "PASS", "n_facts": len(facts)}
    except Exception as exc:  # noqa: BLE001
        return {"status": "FAIL", "error": f"{type(exc).__name__}: {str(exc)[:300]}"}
