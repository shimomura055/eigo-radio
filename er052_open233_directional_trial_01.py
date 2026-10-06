"""OPEN-233 方向性(状態変化)系統的読み違い検出 Trial script(委任_01c、非Production、Trial専用)。

Ledger側抽出 -> 記事側blind抽出 -> 機械比較(Python) の3構成:
  same_blind / split_blind / same_nonblind(旧方式の対照群)
既存Productionコードは変更しない(importのみ)。--dry-run はAPIを呼ばない。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ENUM = ["AVAILABLE", "STOPPED", "PAUSED", "INCREASED", "DECREASED", "UNCHANGED", "STARTED",
        "ENDED", "EXPANDED", "NARROWED", "NOT_MENTIONED", "UNCLEAR"]
REVERSED_PAIRS = {frozenset(p) for p in [("AVAILABLE", "STOPPED"), ("AVAILABLE", "PAUSED"),
                                         ("INCREASED", "DECREASED"), ("STARTED", "ENDED"),
                                         ("EXPANDED", "NARROWED")]}
FAMILY_PAIRS = {frozenset(("PAUSED", "STOPPED"))}
CONFIGS = ("same_blind", "split_blind", "same_nonblind")
DEFAULT_MODEL = "gpt-6-luna"  # = er052_open233_self_recovery_stage2_production_01.MODEL
# 単価 USD/1M tokens (in, cached_in, out)。s2p.PRICE_IN/CACHED/OUT と同値。為替 s2p.USD_JPY=156.88
PRICE_TABLE = {"gpt-6-luna": (0.10, 0.01, 0.50),
               # 委任_02追記: 出典 DECISION_LOG_HISTORY.md:5893(実単価 luna入力$0.2/M・出力$1.2M、sol入力$5/M・出力$30/M)。
               # cached単価は出典に無いため入力の1/10と仮定(Trialは保守側でcachedをほぼ使わない)
               "gpt-5.6-luna": (0.20, 0.02, 1.20), "gpt-5.6-sol": (5.0, 0.5, 30.0)}
USD_JPY = 156.88
NO_DIR = "NO_DIRECTION"
SEVERITY = ["SAME", "SAME_FAMILY", "NOT_MENTIONED", "LEDGER_NO_DIRECTION", "UNCLEAR", "REVERSED"]


class BudgetExceeded(Exception):
    pass


def norm_state(s) -> str:
    return s if isinstance(s, str) and s in ENUM else "UNCLEAR"


def compare(ledger_state, article_state, ledger_quote="x", article_quote="x") -> str:
    """機械比較(LLM不使用)。quote欠落/enum外/非対応の相違は UNCLEAR(勝手に重大化しない)。"""
    if ledger_state in (None, "", NO_DIR):
        return "LEDGER_NO_DIRECTION"
    ls, a = norm_state(ledger_state), norm_state(article_state)
    if a == "NOT_MENTIONED":
        return "NOT_MENTIONED"
    if "UNCLEAR" in (ls, a) or ls == "NOT_MENTIONED":
        return "UNCLEAR"
    if not (str(ledger_quote or "").strip() and str(article_quote or "").strip()):
        return "UNCLEAR"
    if ls == a:
        return "SAME"
    pair = frozenset((ls, a))
    if pair in REVERSED_PAIRS:
        return "REVERSED"
    if pair in FAMILY_PAIRS:
        return "SAME_FAMILY"
    return "UNCLEAR"


def worst(labels: list) -> str:
    return max(labels, key=SEVERITY.index) if labels else "LEDGER_NO_DIRECTION"


EV_SCHEMA = {"type": "object", "additionalProperties": False,
             "required": ["subject_x", "result_state", "quote"],
             "properties": {"subject_x": {"type": "string"},
                            "result_state": {"type": "string", "enum": ENUM},
                            "quote": {"type": "string"}}}
LEDGER_SCHEMA = {"name": "ledger_direction", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["has_direction", "events"],
    "properties": {"has_direction": {"type": "boolean"},
                   "events": {"type": "array", "items": EV_SCHEMA}}}}
ARTICLE_SCHEMA = {"name": "article_state", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["result_state", "quote"],
    "properties": {"result_state": {"type": "string", "enum": ENUM}, "quote": {"type": "string"}}}}
_NB_EV = dict(EV_SCHEMA, required=["subject_x", "result_state", "quote", "article_result_state",
                                   "article_quote"],
              properties=dict(EV_SCHEMA["properties"], article_result_state={"type": "string", "enum": ENUM},
                              article_quote={"type": "string"}))
NONBLIND_SCHEMA = {"name": "nonblind_both", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["has_direction", "events"],
    "properties": {"has_direction": {"type": "boolean"}, "events": {"type": "array", "items": _NB_EV}}}}
ENUM_TXT = ", ".join(ENUM)


def ledger_prompt(fact_text: str) -> str:
    return ("次のfact blockは、ある対象の状態変化・方向性(開始/停止/増減/拡大縮小/撤回復元等)を"
            "記述しているか判定せよ。している場合、各事象について対象X(短い名詞句)と"
            f"『事象後の結果状態』を次の固定分類から1つ選べ: {ENUM_TXT}。"
            "複数事象があれば各事象を列挙。quoteは原文からの逐語引用必須。\n\n[fact block]\n" + fact_text)


def article_prompt(subject_x: str, sentence: str, context: str = "", ledger_text: str = "") -> str:
    p = (f"次の文は対象X『{subject_x}』について『事象後の結果状態』を述べているか。"
         f"述べていれば次の固定分類から1つ選べ: {ENUM_TXT}。述べていなければNOT_MENTIONED、"
         "判断できなければUNCLEAR。quoteは文からの逐語引用必須。\n\n")
    if context:
        p += f"[前後文]\n{context}\n\n"
    return p + f"[記事文]\n{sentence}\n"


def nonblind_prompt(fact_text: str, sentence: str, context: str = "") -> str:
    return (ledger_prompt(fact_text) + "\n\n【対照群】さらに各事象について、次の記事文が述べる結果状態を"
            "article_result_state/article_quoteへ(述べていなければNOT_MENTIONED)。\n\n[記事文]\n"
            + sentence + ("\n[前後文]\n" + context if context else ""))


def cost_jpy(model: str, usage: dict, dry_run: bool = False) -> float:
    pr = PRICE_TABLE.get(model)
    if pr is None:
        if not dry_run:
            raise KeyError(f"単価未登録model: {model}(PRICE_TABLEへ登録が必要)")
        pr = PRICE_TABLE[DEFAULT_MODEL]
    it, ct, ot = (usage.get(k) or 0 for k in ("input_tokens", "cached_input_tokens", "output_tokens"))
    return (max(it - ct, 0) / 1e6 * pr[0] + ct / 1e6 * pr[1] + ot / 1e6 * pr[2]) * USD_JPY


class Runner:
    def __init__(self, config, model_ledger=DEFAULT_MODEL, model_article=None, dry_run=True,
                 budget_yen=15.0, out_dir=None, ledger_repeat=1, client=None, effort="high",
                 reuse_article=None):
        assert config in CONFIGS, config
        self.effort, self.reuse_article = effort, reuse_article or {}
        self.n_fail, self.reuse_hits, self.reuse_miss = 0, 0, 0
        self.config, self.dry_run, self.budget = config, dry_run, budget_yen
        self.model_ledger = model_ledger
        self.model_article = model_article or model_ledger
        self.out_dir, self.ledger_repeat, self.client = out_dir, max(1, ledger_repeat), client
        self.cost, self.calls, self.cache, self.prompts = 0.0, 0, {}, []

    def save_state(self, stopped=False):
        if not self.out_dir:
            return
        os.makedirs(self.out_dir, exist_ok=True)
        with open(os.path.join(self.out_dir, f"budget_state_{self.config}.json"), "w", encoding="utf-8") as f:
            json.dump({"config": self.config, "cumulative_jpy": round(self.cost, 6), "budget_jpy": self.budget,
                       "calls": self.calls, "stopped_by_budget": stopped, "dry_run": self.dry_run}, f, indent=1)

    def call(self, model, prompt, schema, dummy, fail=None):
        if self.cost >= self.budget:
            self.save_state(True)
            raise BudgetExceeded(f"累計¥{self.cost:.4f} >= 上限¥{self.budget}")
        self.prompts.append(prompt)
        err = None
        if self.dry_run:
            parsed, usage = dummy(), {"input_tokens": len(prompt) // 2, "output_tokens": 100}
        else:
            import er052_open233_self_recovery_stage2_production_01 as s2p
            for _attempt in (1, 2):  # 失敗callは1回retry、なお失敗ならUNCLEAR(fail)
                try:
                    r = self.client.responses.create(
                        model=model, reasoning={"effort": self.effort},
                        text={"format": {"type": "json_schema", **schema}},
                        input=[{"role": "user", "content": prompt}])
                    parsed, usage = json.loads(r.output_text), s2p._extract_usage(r)
                    err = None
                    break
                except Exception as e:  # noqa
                    err = repr(e)[:300]
            if err:
                parsed, usage = fail, {}
                self.n_fail += 1
        c = cost_jpy(model, usage, self.dry_run)
        self.cost += c
        self.calls += 1
        if self.out_dir:
            os.makedirs(self.out_dir, exist_ok=True)
            with open(os.path.join(self.out_dir, f"call_log_{self.config}.jsonl"), "a", encoding="utf-8") as lf:
                lf.write(json.dumps({"n": self.calls, "model": model, "usage": usage, "jpy": round(c, 6),
                                     "error": err, "prompt_chars": len(prompt)}, ensure_ascii=False) + "\n")
        self.save_state(self.cost > self.budget)
        if self.cost > self.budget:
            raise BudgetExceeded(f"累計¥{self.cost:.4f} > 上限¥{self.budget}")
        return parsed, round(c, 6)

    def ledger_extract(self, row):
        """Ledger側(記事は見せない)。同一fact本文はキャッシュ(1回のみ)。"""
        fact = row.get("ledger_fact_text", "")
        key = ("L", fact)
        if key not in self.cache:
            def dummy():
                st = row.get("expected_ledger_state") or ""
                if st in ("", NO_DIR):
                    return {"has_direction": False, "events": []}
                return {"has_direction": True, "events": [{"subject_x": row.get("subject_x") or "X",
                        "result_state": st, "quote": fact[:30] or "q"}]}
            lfail = {"has_direction": True, "events": [{"subject_x": "", "result_state": "UNCLEAR", "quote": ""}]}
            outs = [self.call(self.model_ledger, ledger_prompt(fact), LEDGER_SCHEMA, dummy, lfail)
                    for _ in range(self.ledger_repeat)]
            self.cache[key] = {"parsed": outs[0][0], "parsed_all": [o[0] for o in outs],
                               "cost": sum(o[1] for o in outs),
                               "repeat_states": [[norm_state(e.get("result_state")) for e in o[0].get("events", [])]
                                                 for o in outs]}
        return self.cache[key]

    def article_extract(self, row, subject_x, rep=0):
        """記事側blind: 対象X+記事文+前後文のみ。Ledger本文/stateは渡さない。reuse指定時は既存結果を再利用(費用0)。"""
        sent, ctx = row.get("article_sentence", ""), row.get("article_context", "")
        hit = self.reuse_article.get((row.get("id"), subject_x, rep))
        if hit is not None:
            self.reuse_hits += 1
            return dict(hit), 0.0
        if self.reuse_article:
            self.reuse_miss += 1
        dummy = lambda: {"result_state": row.get("expected_article_state") or "NOT_MENTIONED",
                         "quote": sent[:30] or "q"}
        return self.call(self.model_article, article_prompt(subject_x, sent, ctx), ARTICLE_SCHEMA, dummy,
                         {"result_state": "UNCLEAR", "quote": ""})

    def nonblind_extract(self, row):
        fact, sent, ctx = (row.get("ledger_fact_text", ""), row.get("article_sentence", ""),
                           row.get("article_context", ""))
        def dummy():
            d = self.ledger_dummy(row)
            for e in d["events"]:
                e["article_result_state"] = row.get("expected_article_state") or "NOT_MENTIONED"
                e["article_quote"] = sent[:30] or "q"
            return d
        return self.call(self.model_ledger, nonblind_prompt(fact, sent, ctx), NONBLIND_SCHEMA, dummy,
                         {"has_direction": True, "events": [{"subject_x": "", "result_state": "UNCLEAR", "quote": "",
                                                              "article_result_state": "UNCLEAR", "article_quote": ""}]})

    def ledger_dummy(self, row):
        st = row.get("expected_ledger_state") or ""
        if st in ("", NO_DIR):
            return {"has_direction": False, "events": []}
        return {"has_direction": True, "events": [{"subject_x": row.get("subject_x") or "X", "result_state": st,
                "quote": (row.get("ledger_fact_text") or "q")[:30]}]}

    def process_row(self, row):
        reps = max(1, int(row.get("repeat") or 1))
        res = {"id": row.get("id"), "fact_id": row.get("fact_id"), "config": self.config, "role": row.get("role"),
               "label": row.get("label"),
               "expected": {k: row.get(k) for k in ("expected_ledger_state", "expected_article_state",
                            "expected_compare", "acceptable_compare", "has_direction")}}
        rep_events, rep_cmp, cost = [], [], 0.0
        if self.config == "same_nonblind":
            for rep in range(reps):
                parsed, c = self.nonblind_extract(row)
                cost += c
                if rep == 0:
                    res["ledger"] = {"has_direction": parsed.get("has_direction")}
                evs = []
                for e in parsed.get("events", []) if parsed.get("has_direction") else []:
                    evs.append({"subject_x": e.get("subject_x"), "ledger_state": norm_state(e.get("result_state")),
                        "article_state": norm_state(e.get("article_result_state")),
                        "article_quote": e.get("article_quote"), "compare": compare(
                            e.get("result_state"), e.get("article_result_state"), e.get("quote"), e.get("article_quote"))})
                rep_events.append(evs)
        else:
            first = "cost_taken" not in self.cache.get(("L", row.get("ledger_fact_text", "")), {})
            led = self.ledger_extract(row)
            if first:
                cost += led["cost"]
                led["cost_taken"] = True
            res["ledger"] = {"has_direction": led["parsed"].get("has_direction"), "repeat_states": led["repeat_states"],
                             "repeat_has_direction": [bool(p.get("has_direction")) for p in led["parsed_all"]]}
            for rep in range(reps):
                parsed = led["parsed_all"][rep % len(led["parsed_all"])]
                evs = []
                for e in parsed.get("events", []) if parsed.get("has_direction") else []:
                    a, c = self.article_extract(row, e.get("subject_x", ""), rep)
                    cost += c
                    evs.append({"subject_x": e.get("subject_x"), "ledger_state": norm_state(e.get("result_state")),
                        "article_state": norm_state(a.get("result_state")), "article_quote": a.get("quote"),
                        "compare": compare(e.get("result_state"), a.get("result_state"), e.get("quote"), a.get("quote"))})
                rep_events.append(evs)
        res["cost_jpy"], res["repeat_events"] = round(cost, 6), rep_events
        res["events"] = rep_events[0]
        rep_cmp = [worst([e["compare"] for e in evs]) if evs else "LEDGER_NO_DIRECTION" for evs in rep_events]
        res["repeat_compares"], res["compare"] = rep_cmp, rep_cmp[0]
        return res


def summarize(runner, results, rows, population=None) -> dict:
    dist = {}
    for r in results:
        dist[r["compare"]] = dist.get(r["compare"], 0) + 1
    exp = lambda r: (r["expected"].get("expected_compare") or "")
    s = {"config": runner.config, "dry_run": runner.dry_run, "n_rows": len(results), "calls": runner.calls,
         "cost_jpy": round(runner.cost, 6), "compare_distribution": dist,
         "true_reversal_detected": sum(1 for r in results if exp(r) == "REVERSED" and r["compare"] == "REVERSED"),
         "reversal_missed": sum(1 for r in results if exp(r) == "REVERSED" and r["compare"] != "REVERSED"),
         "false_reversal_on_normal": sum(1 for r in results if exp(r) != "REVERSED" and r["compare"] == "REVERSED"),
         "n_failed_calls": runner.n_fail, "reuse_hits": runner.reuse_hits, "reuse_miss": runner.reuse_miss,
         "effort": runner.effort,
         "acceptable_ok": sum(1 for r in results if r["compare"] == exp(r) or
                              r["compare"] in (r["expected"].get("acceptable_compare") or [])),
         "undecidable": dist.get("UNCLEAR", 0)}
    lab = [r for r in results if r["expected"].get("expected_ledger_state")]
    if lab:
        hd = lambda r: bool(r["expected"].get("has_direction"))  # testset_01の事前登録has_direction(実key)
        s["ledger_has_direction_accuracy"] = round(sum(bool(r["ledger"]["has_direction"]) == hd(r) for r in lab) / len(lab), 4)
        st = [r for r in lab if hd(r)]
        s["ledger_state_accuracy"] = round(sum(bool(r["events"]) and r["events"][0]["ledger_state"] ==
                                               r["expected"]["expected_ledger_state"] for r in st) / len(st), 4) if st else None
    ar = [r for r in results if r["expected"].get("expected_article_state") and r["events"]]
    s["article_state_accuracy"] = round(sum(r["events"][0]["article_state"] == r["expected"]["expected_article_state"]
                                            for r in ar) / len(ar), 4) if ar else None
    if population:
        n_runs = population.get("n_runs") or population.get("runs")
        tot = (population.get("totals") or {}).get("n_facts") or population.get("total_facts")
        fpr = (population.get("per_run_avg") or {}).get("n_facts") or population.get("facts_per_run") or (
            tot / n_runs if tot and n_runs else None)  # population_01.jsonの実key: totals.n_facts / per_run_avg.n_facts
        if fpr and results:
            dr = sum(1 for r in results if r["events"]) / len(results)
            cpc = runner.cost / runner.calls if runner.calls else 0
            calls_run = fpr * (1 + dr)
            s["per_run_estimate"] = {"facts_per_run": fpr, "direction_rate": round(dr, 4),
                                     "added_calls": round(calls_run, 2), "added_cost_jpy": round(calls_run * cpc, 4),
                                     "note": "概算(testset内direction率を母集団へ外挿)"}
    return s


def dummy_testset() -> list:
    base = {"fixture": "dummy", "article_context": ""}
    return [dict(base, id="d1", fact_id="f1", ledger_fact_text="The service is available in Japan.",
                 article_sentence="The service is no longer offered in Japan.", expected_ledger_state="AVAILABLE",
                 expected_article_state="STOPPED", expected_compare="REVERSED", subject_x="the service"),
            dict(base, id="d2", fact_id="f2", ledger_fact_text="Sales increased by 10 percent.",
                 article_sentence="Sales rose by about ten percent.", expected_ledger_state="INCREASED",
                 expected_article_state="INCREASED", expected_compare="SAME", subject_x="sales"),
            dict(base, id="d3", fact_id="f3", ledger_fact_text="The firm is based in Osaka.",
                 article_sentence="The firm is headquartered in Osaka.", expected_ledger_state=NO_DIR,
                 expected_article_state="", expected_compare="LEDGER_NO_DIRECTION")]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--testset")
    ap.add_argument("--config", choices=CONFIGS, required=True)
    ap.add_argument("--model-ledger", default=DEFAULT_MODEL)
    ap.add_argument("--model-article", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--budget-yen", type=float, default=15.0)
    ap.add_argument("--ledger-repeat", type=int, default=1)
    ap.add_argument("--population")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high"])
    ap.add_argument("--reuse-article-from", default=None, help="same_blind出力dir(results_same_blind.jsonl)")
    a = ap.parse_args(argv)
    if a.config == "split_blind" and not a.dry_run and (not a.model_article or a.model_article == a.model_ledger):
        ap.error("split_blind は --model-article に Ledger側と異なるmodelの指定が必要")
    ma = a.model_article or ("dummy-model-B" if a.config == "split_blind" else None)
    rows = json.load(open(a.testset, encoding="utf-8")) if a.testset else dummy_testset()
    rows = rows.get("items", rows) if isinstance(rows, dict) else rows
    pop = json.load(open(a.population, encoding="utf-8")) if a.population else None
    client = None
    if not a.dry_run:
        import er003_v1_en_direct_vfl_01_generate as vfl01
        client = vfl01.get_client()
    reuse = {}
    if a.reuse_article_from:  # 記事側blind結果の再利用: key=(row id, subject_x, rep)
        with open(os.path.join(a.reuse_article_from, "results_same_blind.jsonl"), encoding="utf-8") as rf:
            for line in rf:
                rr = json.loads(line)
                for i, evs in enumerate(rr.get("repeat_events", [])):
                    for e in evs:
                        reuse[(rr["id"], e.get("subject_x", ""), i)] = {"result_state": e["article_state"],
                                                                         "quote": e.get("article_quote") or ""}
    rn = Runner(a.config, a.model_ledger, ma, a.dry_run, a.budget_yen, a.out_dir, a.ledger_repeat, client,
                a.effort, reuse)
    os.makedirs(a.out_dir, exist_ok=True)
    results, stopped = [], False
    try:
        with open(os.path.join(a.out_dir, f"results_{a.config}.jsonl"), "w", encoding="utf-8") as f:
            for row in rows:
                r = rn.process_row(row)
                results.append(r)
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    except BudgetExceeded as e:
        stopped = True
        print("STOP:", e)
    s = summarize(rn, results, rows, pop)
    s["stopped_by_budget"] = stopped
    s["models"] = {"ledger": rn.model_ledger, "article": rn.model_article}
    with open(os.path.join(a.out_dir, f"summary_{a.config}.json"), "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    rn.save_state(stopped)
    print(json.dumps(s, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
