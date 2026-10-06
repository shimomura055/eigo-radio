"""OPEN-233 方向性読み違い検出 Trial-02 script(非Production、Trial専用)。

same_blind構成を維持。記事側AIは「Ledger側のどの対象(subject_x)について述べているか」を
1 callで選び、選択された事象のみPythonで比較する(総当たり比較禁止)。
共通部品(compare/ENUM/cost_jpy/Runner.call)は TRIAL-01 scriptからimport(TRIAL-01は変更しない)。
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys

import er052_open233_directional_trial_01 as t1
from er052_open233_directional_trial_01 import (BudgetExceeded, ENUM, ENUM_TXT, NO_DIR, SEVERITY,  # noqa: F401
                                                compare, norm_state, worst)

NONE = "NONE"
ARTICLE_SCHEMA = {"name": "article_selected_state", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["selected_subject", "result_state", "quote"],
    "properties": {"selected_subject": {"type": "string"},
                   "result_state": {"type": "string", "enum": ENUM}, "quote": {"type": "string"}}}}
FAIL_ARTICLE = {"selected_subject": "__CALL_FAILED__", "result_state": "UNCLEAR", "quote": ""}


def article_prompt(labels: list, sentence: str, context: str = "") -> str:
    """記事側blind。入力はsubject_xラベル一覧+記事文+前後文のみ(Ledger state/quote/本文は渡さない)。"""
    lab = "\n".join(f"- {x}" for x in labels)
    p = ("次の記事文は、下の対象のうちどれについて『事象後の結果状態』を述べているか。1つ選べ"
         f"(どれも述べていなければ selected_subject に {NONE} と答える)。"
         "selected_subject は対象一覧の文字列をそのまま返すこと。"
         f"選んだ対象の結果状態を次の固定分類から1つ選べ: {ENUM_TXT}。"
         "判断できなければUNCLEAR。quoteは記事文からの逐語引用必須。\n\n"
         f"[対象一覧]\n{lab}\n\n")
    if context:
        p += f"[前後文]\n{context}\n\n"
    return p + f"[記事文]\n{sentence}\n"


def unique_labels(events: list) -> list:
    """subject_xを重複除去・出現順固定で返す(空ラベルは除外)。"""
    out = []
    for e in events or []:
        s = (e.get("subject_x") or "").strip()
        if s and s not in out:
            out.append(s)
    return out


def compare_selected(events: list, selected: str, a_state, a_quote) -> dict:
    """選択subjectのeventのみ比較(他subjectのeventは一切見ない)。同一subjectの複数eventは
    SAME/SAME_FAMILYがあればそれ、なければworst。"""
    labels = unique_labels(events)
    if selected == NONE:
        return {"compare": "NOT_MENTIONED", "ledger_state": None, "ledger_quote": None}
    if selected not in labels:
        return {"compare": "UNCLEAR", "ledger_state": None, "ledger_quote": None}
    cands = [e for e in events if (e.get("subject_x") or "").strip() == selected]
    res = [(compare(e.get("result_state"), a_state, e.get("quote"), a_quote), e) for e in cands]
    pick = next(((c, e) for c, e in res if c in ("SAME", "SAME_FAMILY")), None)
    if pick is None:
        c = worst([c for c, _ in res])
        pick = next((c2, e) for c2, e in res if c2 == c)
    return {"compare": pick[0], "ledger_state": norm_state(pick[1].get("result_state")),
            "ledger_quote": pick[1].get("quote")}


class Runner(t1.Runner):
    """TRIAL-01 Runner.call(budget/call_log/retry/dry-run)を流用。config名=出力ファイル接尾辞。"""

    def __init__(self, tag, model=t1.DEFAULT_MODEL, dry_run=True, budget_yen=10.0, out_dir=None,
                 client=None, effort="high", ledger_cache=None):
        super().__init__("same_blind", model, None, dry_run, budget_yen, out_dir, 1, client, effort)
        self.config, self.ledger_cache = tag, ledger_cache or {}

    def ledger_events(self, row, repeat):
        """Ledger側(記事を見せない)をrepeat回。戻り値 {rep1: events, ...}。"""
        fact = row.get("ledger_fact_text", "")
        st = row.get("expected_ledger_state") or ""

        def dummy():
            if st in ("", NO_DIR):
                return {"has_direction": False, "events": []}
            return {"has_direction": True, "events": [{"subject_x": row.get("subject_x") or "X",
                                                       "result_state": st, "quote": fact[:30] or "q"}]}
        lfail = {"has_direction": True, "events": [{"subject_x": "", "result_state": "UNCLEAR", "quote": ""}]}
        out = {}
        for i in range(1, repeat + 1):
            p, _ = self.call(self.model_ledger, t1.ledger_prompt(fact), t1.LEDGER_SCHEMA, dummy, lfail)
            out[f"rep{i}"] = p.get("events", []) if p.get("has_direction") else []
        return out

    def article_select(self, row, labels):
        sent, ctx = row.get("article_sentence", ""), row.get("article_context", "")

        def dummy():
            if not row.get("expected_article_state"):
                return {"selected_subject": NONE, "result_state": "NOT_MENTIONED", "quote": ""}
            pick = row.get("subject_x") if row.get("subject_x") in labels else labels[0]
            return {"selected_subject": pick, "result_state": row["expected_article_state"], "quote": sent[:30] or "q"}
        return self.call(self.model_ledger, article_prompt(labels, sent, ctx), ARTICLE_SCHEMA, dummy, FAIL_ARTICLE)

    def process_row(self, row):
        fid = row.get("fact_id")
        reps_cache = self.ledger_cache.get(fid)
        if reps_cache is None:
            raise KeyError(f"ledger_cacheにfact_idなし: {fid}")
        n_rep = max(1, min(int(row.get("repeat") or 1), len(reps_cache)))
        res = {k: row.get(k) for k in ("id", "fact_id", "label", "origin", "expected_compare",
                                       "acceptable_compare", "expected_event_subject")}
        cost, repeats = 0.0, []
        for i in range(1, n_rep + 1):
            events = reps_cache[f"rep{i}"]
            labels = unique_labels(events)
            rec = {"rep": i, "ledger_events_subjects": labels, "selected_subject": None, "ledger_state": None,
                   "article_state": None, "compare": "LEDGER_NO_DIRECTION", "ledger_quote": None, "article_quote": None}
            if labels:
                a, c = self.article_select(row, labels)
                cost += c
                rec["selected_subject"], rec["article_state"] = a.get("selected_subject"), norm_state(a.get("result_state"))
                rec["article_quote"] = a.get("quote")
                r = compare_selected(events, a.get("selected_subject"), a.get("result_state"), a.get("quote"))
                rec.update(compare=r["compare"], ledger_state=r["ledger_state"], ledger_quote=r["ledger_quote"])
            repeats.append(rec)
        res.update(repeats=repeats, final_compare_rep0=repeats[0]["compare"],
                   final_compares=[r["compare"] for r in repeats], cost_jpy=round(cost, 6))
        return res


def shard_items(rows: list, i: int, n: int) -> list:
    """id順にn分割したi番目(1始まり、連続区間)。"""
    rs = sorted(rows, key=lambda r: str(r.get("id")))
    return rs[(i - 1) * len(rs) // n: i * len(rs) // n]


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def input_hash(cache, model, effort, n_shards, testset_rows) -> str:
    """shard間の条件同一性hash(cache/prompt/schema/model/effort/shard数/testset)。"""
    return _sha({"cache": cache, "prompt": article_prompt(["A", "B"], "S", "C"), "schema": ARTICLE_SCHEMA,
                 "model": model, "effort": effort, "n_shards": n_shards, "testset": testset_rows})


def summarize(results: list, rows_by_id: dict) -> dict:
    by = {}
    for r in results:
        b = by.setdefault(r.get("label"), {"n": 0, "reversed_rep0": 0, "reversed_any": 0, "unclear": 0,
                                           "not_mentioned": 0})
        b["n"] += 1
        b["reversed_rep0"] += r["final_compare_rep0"] == "REVERSED"
        b["reversed_any"] += "REVERSED" in r["final_compares"]
        b["unclear"] += r["final_compare_rep0"] == "UNCLEAR"
        b["not_mentioned"] += r["final_compare_rep0"] == "NOT_MENTIONED"
    gold = {r["id"]: {"hits": sum(c == "REVERSED" for c in r["final_compares"]), "reps": len(r["final_compares"])}
            for r in results if r.get("expected_compare") == "REVERSED" and len(r["final_compares"]) > 1}
    return {"n_items": len(results), "by_label": by, "gold_detail": gold,
            "n_calls": sum(len([x for x in r["repeats"] if x["selected_subject"] is not None]) for r in results),
            "cost_jpy": round(sum(r["cost_jpy"] for r in results), 6)}


def merge(d: str, ledger_dir: str | None = None) -> dict:
    metas = sorted(glob.glob(os.path.join(d, "run_meta_shard_*.json")))
    ms = [json.load(open(p, encoding="utf-8")) for p in metas]
    if not ms:
        raise SystemExit("MERGE STOP: run_meta_shard_*.json なし")
    if len({m["input_hash"] for m in ms}) != 1:
        raise SystemExit("MERGE STOP: shard間のinput_hash不一致(cache/prompt/model/effort/testsetが異なる)")
    n = ms[0]["n_shards"]
    if sorted(m["shard"] for m in ms) != list(range(1, n + 1)):
        raise SystemExit(f"MERGE STOP: shard欠落/重複 {[m['shard'] for m in ms]} (n={n})")
    results = []
    for p in sorted(glob.glob(os.path.join(d, "results_shard_*.jsonl"))):
        results += [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]
    ids = [r["id"] for r in results]
    if len(ids) != len(set(ids)):
        raise SystemExit("MERGE STOP: id重複")
    if sum(m["n_items_expected"] for m in ms) != len(results):
        raise SystemExit("MERGE STOP: 件数が期待値と不一致(予算停止等で未完のshardあり)")
    results.sort(key=lambda r: str(r["id"]))
    s = summarize(results, {})
    s["ledger_cost_jpy"], s["ledger_calls"] = 0.0, 0
    if ledger_dir:
        lm = json.load(open(os.path.join(ledger_dir, "ledger_meta.json"), encoding="utf-8"))
        s["ledger_cost_jpy"], s["ledger_calls"] = lm["cost_jpy"], lm["n_calls"]
    s["cost_jpy"] = round(s["cost_jpy"] + s["ledger_cost_jpy"], 6)
    s["n_calls_article"], s["n_calls"] = sum(m["calls"] for m in ms), sum(m["calls"] for m in ms) + s["ledger_calls"]
    s["input_hash"], s["n_shards"] = ms[0]["input_hash"], n
    with open(os.path.join(d, "results_merged.jsonl"), "w", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in results)
    with open(os.path.join(d, "summary_merged.json"), "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    return s


def _load_rows(path):
    rows = json.load(open(path, encoding="utf-8")) if path else t1.dummy_testset()
    return rows.get("items", rows) if isinstance(rows, dict) else rows


def _dump(obj, path, indent=1):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)


def run_ledger_only(a, rows, client):
    rn = Runner("ledger", a.model, a.dry_run, a.budget_yen, a.out_dir, client, a.effort)
    cache = {}
    for row in rows:
        if row.get("fact_id") not in cache:
            cache[row["fact_id"]] = rn.ledger_events(row, a.ledger_repeat)
    _dump(cache, os.path.join(a.out_dir, "ledger_cache.json"))
    _dump({"cost_jpy": round(rn.cost, 6), "n_calls": rn.calls, "model": a.model, "effort": a.effort,
           "ledger_repeat": a.ledger_repeat, "n_facts": len(cache)}, os.path.join(a.out_dir, "ledger_meta.json"))
    print(f"ledger-only done: facts={len(cache)} calls={rn.calls} cost={rn.cost:.4f}")


def run_shard(a, rows, client):
    i, n = (int(x) for x in a.article_shard.split("/"))
    cache = json.load(open(a.ledger_cache, encoding="utf-8"))
    rn = Runner(f"shard_{i}of{n}", a.model, a.dry_run, a.budget_yen, a.out_dir, client, a.effort, cache)
    mine = shard_items(rows, i, n)
    ts = sorted((str(r.get("id")), r.get("article_sentence"), r.get("fact_id")) for r in rows)
    meta = {"shard": i, "n_shards": n, "input_hash": input_hash(cache, a.model, a.effort, n, ts),
            "n_items_expected": len(mine), "model": a.model, "effort": a.effort, "calls": 0}
    mp = os.path.join(a.out_dir, f"run_meta_shard_{i}of{n}.json")
    _dump(meta, mp)
    done = 0
    try:
        with open(os.path.join(a.out_dir, f"results_shard_{i}of{n}.jsonl"), "w", encoding="utf-8") as f:
            for row in mine:
                f.write(json.dumps(rn.process_row(row), ensure_ascii=False) + "\n")
                done += 1
    except BudgetExceeded as e:
        print("STOP:", e)
    meta.update(calls=rn.calls, cost_jpy=round(rn.cost, 6), n_items_done=done, n_failed_calls=rn.n_fail)
    _dump(meta, mp)
    print(f"shard {i}/{n}: items={done}/{len(mine)} calls={rn.calls} cost={rn.cost:.4f}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--testset")
    ap.add_argument("--model", default=t1.DEFAULT_MODEL)
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--budget-yen", type=float, default=10.0)
    ap.add_argument("--out-dir")
    ap.add_argument("--ledger-only", action="store_true")
    ap.add_argument("--ledger-repeat", type=int, default=3)
    ap.add_argument("--article-shard", help="i/n")
    ap.add_argument("--ledger-cache")
    ap.add_argument("--merge", metavar="DIR")
    ap.add_argument("--ledger-dir", help="merge時にLedger側費用(ledger_meta.json)を加算")
    a = ap.parse_args(argv)
    if a.merge:
        print(json.dumps(merge(a.merge, a.ledger_dir), ensure_ascii=False))
        return 0
    if not a.out_dir:
        ap.error("--out-dir 必須")
    if not a.ledger_only and not (a.article_shard and a.ledger_cache):
        ap.error("--article-shard i/n と --ledger-cache が必要(または --ledger-only / --merge)")
    os.makedirs(a.out_dir, exist_ok=True)
    rows = _load_rows(a.testset)
    client = None
    if not a.dry_run:
        import er003_v1_en_direct_vfl_01_generate as vfl01
        client = vfl01.get_client()
    (run_ledger_only if a.ledger_only else run_shard)(a, rows, client)
    return 0


if __name__ == "__main__":
    sys.exit(main())
