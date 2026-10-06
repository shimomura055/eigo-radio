"""OPEN-233 方向性読み違い検出 Trial-03 script(非Production、Trial専用)。

v2(trial_02)との差分のみ実装: 修正1=時間的位置(phase: INTERIM/FINAL/SINGLE)の区別、
修正2=事象選択がNONEのときのみ各事象を個別確認する限定フォールバック。他はv2をimport流用。
config X=phase照合なし+NONEフォールバック / Y=phase照合+NONEフォールバック。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import er052_open233_directional_trial_01 as t1
import er052_open233_directional_trial_02 as t2
from er052_open233_directional_trial_01 import (BudgetExceeded, ENUM, ENUM_TXT, NO_DIR,  # noqa: F401
                                                compare, norm_state, worst)
from er052_open233_directional_trial_02 import (NONE, shard_items, unique_labels, _dump, _sha)  # noqa: F401

LPHASE = ["INTERIM", "FINAL", "SINGLE"]
APHASE = ["INTERIM", "FINAL", "UNSPECIFIED"]
EV_SCHEMA = {"type": "object", "additionalProperties": False,
             "required": ["subject_x", "result_state", "phase", "quote"],
             "properties": {"subject_x": {"type": "string"}, "result_state": {"type": "string", "enum": ENUM},
                            "phase": {"type": "string", "enum": LPHASE}, "quote": {"type": "string"}}}
LEDGER_SCHEMA = {"name": "ledger_direction_phase", "strict": True, "schema": {
    "type": "object", "additionalProperties": False, "required": ["has_direction", "events"],
    "properties": {"has_direction": {"type": "boolean"}, "events": {"type": "array", "items": EV_SCHEMA}}}}
ARTICLE_SCHEMA = {"name": "article_selected_state_phase", "strict": True, "schema": {
    "type": "object", "additionalProperties": False,
    "required": ["selected_subject", "result_state", "phase", "quote"],
    "properties": {"selected_subject": {"type": "string"}, "result_state": {"type": "string", "enum": ENUM},
                   "phase": {"type": "string", "enum": APHASE}, "quote": {"type": "string"}}}}
FAIL_ARTICLE = {"selected_subject": "__CALL_FAILED__", "result_state": "UNCLEAR", "phase": "UNSPECIFIED", "quote": ""}
FAIL_FB = {"result_state": "UNCLEAR", "quote": ""}


def ledger_prompt(fact_text: str) -> str:
    """v1 ledger prompt + phase追記(途中=INTERIM、結末=FINAL、区別なし=SINGLE)。"""
    return (t1.ledger_prompt(fact_text).split("\n\n[fact block]")[0]
            + "\n同じ対象について途中の変化と最終状態が両方ある場合、途中の変化=INTERIM、結末・最終状態=FINAL"
              "として別の事象に分けよ。区別がない単一事象=SINGLE。各事象にphaseを付けること。"
            + "\n\n[fact block]\n" + fact_text)


def article_prompt(labels: list, sentence: str, context: str = "") -> str:
    """記事側blind。ラベル一覧+記事文+前後文のみ。Ledgerのphase/state/quoteは渡さない。"""
    return (t2.article_prompt(labels, sentence, context).split("\n\n[対象一覧]")[0]
            + "\nさらにphaseを答えよ: 文が『一時的・途中の動き』(briefly/initially/temporarily等)を述べていれば"
              "INTERIM、結末・現状を述べていればFINAL、判断できなければUNSPECIFIED。"
            + "\n\n[対象一覧]" + t2.article_prompt(labels, sentence, context).split("\n\n[対象一覧]")[1])


def norm_lphase(e: dict) -> str:
    p = e.get("phase")
    return p if p in LPHASE else "SINGLE"  # 欠落/不正はSINGLE扱い


def norm_aphase(p) -> str:
    return p if p in APHASE else "UNSPECIFIED"


def phase_ok(article_phase: str, ledger_phase: str) -> bool:
    """INTERIM記事文↔INTERIM事象のみ。FINAL/UNSPECIFIED↔FINAL/SINGLE。"""
    if article_phase == "INTERIM":
        return ledger_phase == "INTERIM"
    return ledger_phase in ("FINAL", "SINGLE")


def compare_phase(events: list, selected: str, a_state, a_quote, a_phase) -> dict:
    """構成Y: 選択subjectのeventからphase一致eventを一意に選びcompare。SAME優先tie-breakは使わない。
    一致phaseが複数ある場合はFINAL>SINGLE>INTERIMの固定順で先頭1つ。該当なし=UNCLEAR。"""
    blank = {"compare": "UNCLEAR", "ledger_state": None, "ledger_quote": None, "matched_event_phase": None}
    if selected == NONE:
        return dict(blank, compare="NOT_MENTIONED")
    if selected not in unique_labels(events):
        return blank
    ap = norm_aphase(a_phase)
    cands = [e for e in events if (e.get("subject_x") or "").strip() == selected and phase_ok(ap, norm_lphase(e))]
    if not cands:
        return blank
    cands.sort(key=lambda e: ["FINAL", "SINGLE", "INTERIM"].index(norm_lphase(e)))
    e = cands[0]
    return {"compare": compare(e.get("result_state"), a_state, e.get("quote"), a_quote),
            "ledger_state": norm_state(e.get("result_state")), "ledger_quote": e.get("quote"),
            "matched_event_phase": norm_lphase(e)}


def compare_x(events: list, selected: str, a_state, a_quote) -> dict:
    """構成X: phase照合なし。v2 compare_selected(SAME優先)そのまま。"""
    r = t2.compare_selected(events, selected, a_state, a_quote)
    return dict(r, matched_event_phase=None)


AGG_ORDER = ["SAME", "SAME_FAMILY", "NOT_MENTIONED", "UNCLEAR"]


def aggregate_fallback(compares: list) -> str:
    """1つでもREVERSED→REVERSED。他はSAME>SAME_FAMILY>NOT_MENTIONED>UNCLEAR。空=NOT_MENTIONED。"""
    if not compares:
        return "NOT_MENTIONED"
    if "REVERSED" in compares:
        return "REVERSED"
    for c in AGG_ORDER:
        if c in compares:
            return c
    return "UNCLEAR"


class Runner(t2.Runner):
    def __init__(self, tag, config="Y", **kw):
        assert config in ("X", "Y"), config
        super().__init__(tag, **kw)
        self.cfg, self.fb_cost, self.fb_calls = config, 0.0, 0

    def ledger_events(self, row, repeat):
        fact, st = row.get("ledger_fact_text", ""), row.get("expected_ledger_state") or ""

        def dummy():
            if st in ("", NO_DIR):
                return {"has_direction": False, "events": []}
            return {"has_direction": True, "events": [{"subject_x": row.get("subject_x") or "X", "result_state": st,
                                                       "phase": "SINGLE", "quote": fact[:30] or "q"}]}
        lfail = {"has_direction": True, "events": [{"subject_x": "", "result_state": "UNCLEAR",
                                                    "phase": "SINGLE", "quote": ""}]}
        out = {}
        for i in range(1, repeat + 1):
            p, _ = self.call(self.model_ledger, ledger_prompt(fact), LEDGER_SCHEMA, dummy, lfail)
            out[f"rep{i}"] = p.get("events", []) if p.get("has_direction") else []
        return out

    def article_select(self, row, labels):
        sent, ctx = row.get("article_sentence", ""), row.get("article_context", "")

        def dummy():
            if row.get("expected_article_state") in (None, "", "NOT_MENTIONED"):
                return {"selected_subject": NONE, "result_state": "NOT_MENTIONED", "phase": "UNSPECIFIED", "quote": ""}
            pick = row.get("subject_x") if row.get("subject_x") in labels else labels[0]
            return {"selected_subject": pick, "result_state": row["expected_article_state"],
                    "phase": row.get("expected_article_phase") or "UNSPECIFIED", "quote": sent[:30] or "q"}
        return self.call(self.model_ledger, article_prompt(labels, sent, ctx), ARTICLE_SCHEMA, dummy, FAIL_ARTICLE)

    def article_single(self, row, subject_x):
        """フォールバック用の個別確認call(TRIAL-01方式、Ledger state/quoteは渡さない)。"""
        sent, ctx = row.get("article_sentence", ""), row.get("article_context", "")
        dummy = lambda: {"result_state": row.get("expected_article_state") or "NOT_MENTIONED",
                         "quote": sent[:30] or "q"}
        return self.call(self.model_ledger, t1.article_prompt(subject_x, sent, ctx), t1.ARTICLE_SCHEMA, dummy, FAIL_FB)

    def fallback(self, row, events, a_phase):
        """NONE選択時のみ呼ぶ。Yは記事phaseと不一致のeventを比較しない。戻り値=(compare, details, calls, cost)。"""
        ap, details, comps, cost = norm_aphase(a_phase), [], [], 0.0
        for e in events:
            lp = norm_lphase(e)
            subj = (e.get("subject_x") or "").strip()
            if not subj or (self.cfg == "Y" and not phase_ok(ap, lp)):
                continue
            a, c = self.article_single(row, subj)
            cost += c
            a_state = norm_state(a.get("result_state"))
            cmp_ = compare(e.get("result_state"), a_state, e.get("quote"), a.get("quote"))
            comps.append(cmp_)
            details.append({"subject_x": subj, "phase": lp, "ledger_state": norm_state(e.get("result_state")),
                            "article_state": a_state, "compare": cmp_})
        return aggregate_fallback(comps), details, len(details), cost

    def process_rep(self, row, i, events):
        labels = unique_labels(events)
        rec = {"rep": i, "ledger_events_subjects": labels, "selected_subject": None, "ledger_state": None,
               "article_state": None, "compare": "LEDGER_NO_DIRECTION", "ledger_quote": None, "article_quote": None,
               "article_phase": None, "matched_event_phase": None, "fallback_used": False, "fallback_calls": 0,
               "fallback_details": []}
        cost = 0.0
        if not labels:
            return rec, cost, 0.0
        a, c = self.article_select(row, labels)
        cost += c
        sel = a.get("selected_subject")
        rec.update(selected_subject=sel, article_state=norm_state(a.get("result_state")),
                   article_quote=a.get("quote"), article_phase=norm_aphase(a.get("phase")))
        if self.cfg == "Y":
            r = compare_phase(events, sel, a.get("result_state"), a.get("quote"), a.get("phase"))
        else:
            r = compare_x(events, sel, a.get("result_state"), a.get("quote"))
        rec.update(compare=r["compare"], ledger_state=r["ledger_state"], ledger_quote=r["ledger_quote"],
                   matched_event_phase=r["matched_event_phase"])
        fbc = 0.0
        if sel == NONE:  # NONEのときのみフォールバック
            cmp_, det, n, fbc = self.fallback(row, events, a.get("phase"))
            rec.update(compare=cmp_, fallback_used=True, fallback_calls=n, fallback_details=det)
            self.fb_cost += fbc
            self.fb_calls += n
        return rec, cost + fbc, fbc

    def process_row(self, row):
        fid = row.get("fact_id")
        rc = self.ledger_cache.get(fid)
        if rc is None:
            raise KeyError(f"ledger_cacheにfact_idなし: {fid}")
        n_rep = max(1, min(int(row.get("repeat") or 1), len(rc)))
        res = {k: row.get(k) for k in ("id", "fact_id", "label", "origin", "expected_compare",
                                       "acceptable_compare", "expected_event_subject")}
        res["is_heldout"] = bool(row.get("heldout"))
        cost, fbc_tot, repeats = 0.0, 0.0, []
        for i in range(1, n_rep + 1):
            rec, c, fbc = self.process_rep(row, i, rc[f"rep{i}"])
            cost, fbc_tot = cost + c, fbc_tot + fbc
            repeats.append(rec)
        res.update(repeats=repeats, final_compare_rep0=repeats[0]["compare"],
                   final_compares=[r["compare"] for r in repeats], cost_jpy=round(cost, 6),
                   fallback_cost_jpy=round(fbc_tot, 6))
        return res


def input_hash(cache, model, effort, n_shards, testset_rows, config) -> str:
    return _sha({"cache": cache, "prompt": article_prompt(["A", "B"], "S", "C"), "schema": ARTICLE_SCHEMA,
                 "model": model, "effort": effort, "n_shards": n_shards, "testset": testset_rows, "config": config,
                 "fb_prompt": t1.article_prompt("A", "S", "C")})


def _merge_partial(d: str, ledger_dir, expected_ids) -> None:
    """件数不一致のみ許容するmerge(hash/shard欠落/id重複の検証は維持)。欠落idをmerge_meta.jsonへ記録。"""
    ms = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(d, "run_meta_shard_*.json")))]
    if not ms:
        raise SystemExit("MERGE STOP: run_meta_shard_*.json なし")
    if len({m["input_hash"] for m in ms}) != 1:
        raise SystemExit("MERGE STOP: shard間のinput_hash不一致")
    n = ms[0]["n_shards"]
    if sorted(m["shard"] for m in ms) != list(range(1, n + 1)):
        raise SystemExit("MERGE STOP: shard欠落/重複")
    results = []
    for p in sorted(glob.glob(os.path.join(d, "results_shard_*.jsonl"))):
        results += [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]
    ids = [r["id"] for r in results]
    if len(ids) != len(set(ids)):
        raise SystemExit("MERGE STOP: id重複")
    results.sort(key=lambda r: str(r["id"]))
    s = t2.summarize(results, {})
    s["ledger_cost_jpy"], s["ledger_calls"] = 0.0, 0
    if ledger_dir:
        lm = json.load(open(os.path.join(ledger_dir, "ledger_meta.json"), encoding="utf-8"))
        s["ledger_cost_jpy"], s["ledger_calls"] = lm["cost_jpy"], lm["n_calls"]
    s["cost_jpy"] = round(s["cost_jpy"] + s["ledger_cost_jpy"], 6)
    s["n_calls_article"], s["n_calls"] = sum(m["calls"] for m in ms), sum(m["calls"] for m in ms) + s["ledger_calls"]
    s["input_hash"], s["n_shards"] = ms[0]["input_hash"], n
    missing = sorted(set(map(str, expected_ids or [])) - {str(i) for i in ids})
    s["partial"], s["missing_ids"] = True, missing
    with open(os.path.join(d, "results_merged.jsonl"), "w", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in results)
    with open(os.path.join(d, "summary_merged.json"), "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    _dump({"partial": True, "missing_ids": missing, "n_results": len(results), "n_expected": len(expected_ids or [])},
          os.path.join(d, "merge_meta.json"))


def merge(d: str, ledger_dir: str | None = None, allow_partial: bool = False, expected_ids=None) -> dict:
    """検証(hash/shard欠落/id重複/件数)はv2 mergeを流用し、summaryをv3項目で再計算。"""
    if allow_partial:
        _merge_partial(d, ledger_dir, expected_ids)
    else:
        t2.merge(d, ledger_dir)  # 検証と results_merged.jsonl 生成
    results = [json.loads(x) for x in open(os.path.join(d, "results_merged.jsonl"), encoding="utf-8") if x.strip()]
    s = json.load(open(os.path.join(d, "summary_merged.json"), encoding="utf-8"))
    reps = [r2 for r in results for r2 in r["repeats"]]
    fb_calls = sum(r2["fallback_calls"] for r2 in reps)
    fb_cost = round(sum(r.get("fallback_cost_jpy", 0.0) for r in results), 6)
    s["fallback_used_reps"] = sum(1 for r2 in reps if r2["fallback_used"])
    s["fallback_calls"] = fb_calls
    s["cost_breakdown_jpy"] = {"ledger": s["ledger_cost_jpy"], "article_normal": round(
        sum(r["cost_jpy"] for r in results) - fb_cost, 6), "article_fallback": fb_cost}
    s["n_calls_article_fallback"] = fb_calls
    s["n_heldout"] = sum(1 for r in results if r.get("is_heldout"))
    with open(os.path.join(d, "summary_merged.json"), "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    return s


def run_ledger_only(a, rows, client):
    rn = Runner("ledger", a.config, model=a.model, dry_run=a.dry_run, budget_yen=a.budget_yen,
                out_dir=a.out_dir, client=client, effort=a.effort)
    cache = {}
    for row in rows:
        if row.get("fact_id") not in cache:
            cache[row["fact_id"]] = rn.ledger_events(row, a.ledger_repeat)
    n_missing = sum(1 for reps in cache.values() for evs in reps.values() for e in evs if e.get("phase") not in LPHASE)
    _dump(cache, os.path.join(a.out_dir, "ledger_cache.json"))
    _dump({"cost_jpy": round(rn.cost, 6), "n_calls": rn.calls, "model": a.model, "effort": a.effort,
           "ledger_repeat": a.ledger_repeat, "n_facts": len(cache), "phase_missing_treated_as_SINGLE": n_missing},
          os.path.join(a.out_dir, "ledger_meta.json"))
    print(f"ledger-only done: facts={len(cache)} calls={rn.calls} cost={rn.cost:.4f} phase_missing={n_missing}")


def run_shard(a, rows, client):
    i, n = (int(x) for x in a.article_shard.split("/"))
    cache = json.load(open(a.ledger_cache, encoding="utf-8"))
    rn = Runner(f"{a.config}_shard_{i}of{n}", a.config, model=a.model, dry_run=a.dry_run, budget_yen=a.budget_yen,
                out_dir=a.out_dir, client=client, effort=a.effort, ledger_cache=cache)
    mine = shard_items(rows, i, n)
    ts = sorted((str(r.get("id")), r.get("article_sentence"), r.get("fact_id")) for r in rows)
    meta = {"shard": i, "n_shards": n, "config": a.config, "input_hash": input_hash(cache, a.model, a.effort, n, ts, a.config),
            "n_items_expected": len(mine), "model": a.model, "effort": a.effort, "calls": 0}
    mp = os.path.join(a.out_dir, f"run_meta_shard_{i}of{n}.json")
    rp = os.path.join(a.out_dir, f"results_shard_{i}of{n}.jsonl")
    prior_calls, prior_cost, done_ids = 0, 0.0, set()
    if a.resume:
        if os.path.exists(mp):
            old = json.load(open(mp, encoding="utf-8"))
            if old.get("input_hash") != meta["input_hash"]:
                raise SystemExit("RESUME STOP: input_hash不一致(既存run_metaと条件が異なる)")
        if os.path.exists(rp):
            exp_n = {str(r.get("id")): max(1, min(int(r.get("repeat") or 1), len(cache.get(r.get("fact_id"), {}) or {1: 1}))) for r in mine}
            old_rows = [json.loads(x) for x in open(rp, encoding="utf-8") if x.strip()]
            good = [r for r in old_rows if len(r.get("repeats", [])) >= exp_n.get(str(r["id"]), 1)]
            if len(good) != len(old_rows):  # 部分完了id(repeat途中)は削除して再実行
                with open(rp, "w", encoding="utf-8") as f:
                    f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in good)
            done_ids = {str(r["id"]) for r in good}
        lp = os.path.join(a.out_dir, f"call_log_{a.config}_shard_{i}of{n}.jsonl")
        if os.path.exists(lp):
            lg = [json.loads(x) for x in open(lp, encoding="utf-8") if x.strip()]
            prior_calls, prior_cost = len(lg), sum(x.get("jpy", 0) or 0 for x in lg)
        todo = [r for r in mine if str(r.get("id")) not in done_ids]
    else:
        todo = mine
        _dump(meta, mp)
    if a.only_ids:
        keep = set(a.only_ids.split(","))
        todo = [r for r in todo if str(r.get("id")) in keep]
    done = len(done_ids)
    try:
        with open(rp, "a" if a.resume else "w", encoding="utf-8") as f:
            for row in todo:
                f.write(json.dumps(rn.process_row(row), ensure_ascii=False) + "\n")
                f.flush()
                done += 1
    except BudgetExceeded as e:
        print("STOP:", e)
    meta.update(calls=prior_calls + rn.calls, cost_jpy=round(prior_cost + rn.cost, 6), n_items_done=done,
                n_failed_calls=rn.n_fail, fallback_calls=rn.fb_calls, fallback_cost_jpy=round(rn.fb_cost, 6),
                resumed=bool(a.resume), step_calls=rn.calls, step_cost_jpy=round(rn.cost, 6))
    _dump(meta, mp)
    print(f"shard {i}/{n} [{a.config}]: items={done}/{len(mine)} step_calls={rn.calls} fb_calls={rn.fb_calls} step_cost={rn.cost:.4f}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--testset")
    ap.add_argument("--config", choices=["X", "Y"], default="Y")
    ap.add_argument("--population", help="指定時、testset行のpopulation欄が一致する行のみ使用")
    ap.add_argument("--model", default=t1.DEFAULT_MODEL)
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--budget-yen", type=float, default=8.0)
    ap.add_argument("--out-dir")
    ap.add_argument("--ledger-only", action="store_true")
    ap.add_argument("--ledger-repeat", type=int, default=3)
    ap.add_argument("--article-shard", help="i/n")
    ap.add_argument("--ledger-cache")
    ap.add_argument("--resume", action="store_true", help="既存results_shardの完了済みidをskipして追記")
    ap.add_argument("--only-ids", help="resume時に実行するidのカンマ区切り(優先順位制御用)")
    ap.add_argument("--allow-partial", action="store_true", help="merge時に欠落idを許容しmerge_meta.missing_idsへ記録")
    ap.add_argument("--merge", metavar="DIR")
    ap.add_argument("--ledger-dir", help="merge時にLedger側費用(ledger_meta.json)を加算")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if a.merge:
        exp = None
        if a.testset:
            rws = t2._load_rows(a.testset)
            if a.population:
                rws = [r for r in rws if r.get("population") == a.population]
            exp = [str(r.get("id")) for r in rws]
        print(json.dumps(merge(a.merge, a.ledger_dir, a.allow_partial, exp), ensure_ascii=False))
        return 0
    if not a.out_dir:
        ap.error("--out-dir 必須")
    if not a.ledger_only and not (a.article_shard and a.ledger_cache):
        ap.error("--article-shard i/n と --ledger-cache が必要(または --ledger-only / --merge)")
    os.makedirs(a.out_dir, exist_ok=True)
    rows = t2._load_rows(a.testset)
    if a.population:
        rows = [r for r in rows if r.get("population") == a.population]
    client = None
    if not a.dry_run:
        import er003_v1_en_direct_vfl_01_generate as vfl01
        client = vfl01.get_client()
    (run_ledger_only if a.ledger_only else run_shard)(a, rows, client)
    return 0


if __name__ == "__main__":
    sys.exit(main())
