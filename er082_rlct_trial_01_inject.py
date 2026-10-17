# ============================================================
# er082_rlct_trial_01_inject.py  (任意A: 故障注入、Trial専用)
# ============================================================
# M0/M0bの採用Factの数値・日付・方向語を1か所だけ改変した「複製Fact」を2〜3件/記事つくり、
# 上限なし/上限付きVerifierで検証する。期待=REJECTED。VERIFIEDで通過したら検出漏れ=重大NG。
# 元のdraft・Ledger・B3は変更しない(Trial領域_inputsの複製からも読むだけ。注入Factは別ファイル)。
# 結果は『通常記事における誤り検出率の保証』ではない(5記事・2〜3件では統計的に保証できない)。
# ============================================================
from __future__ import annotations

import argparse
import copy
import os
import re
import sys

import er082_rlct_trial_01_lib as lib
from er082_rlct_trial_01_lib import ARTICLES, OUT_ROOT, Budget, BudgetStop, load_json, save_json

_NUM = re.compile(r"(?<![\d.,])(\d[\d,]*\.?\d*)(?![\d])")
_YEAR = re.compile(r"(?<!\d)(20\d\d)(?!\d)")
_WORD_SWAPS = [("過去最高", "過去最低"), ("最多", "最少"), ("上昇", "下落"), ("増加", "減少"), ("以上", "未満")]


def _scale_number(tok: str) -> str:
    raw = tok.replace(",", "")
    dec = len(raw.split(".")[1]) if "." in raw else 0
    new = float(raw) * 1.37 if float(raw) != 0 else 1.0
    if dec == 0:
        s = str(int(round(new)))
        if s == raw:
            s = str(int(raw) + 7)
    else:
        s = f"{new:.{dec}f}"
    if "," in tok and dec == 0:
        s = f"{int(s):,}"
    return s


def _replace_in(f: dict, fields: tuple, old: str, new: str, pattern) -> bool:
    changed = False
    for k in fields:
        v = f.get(k)
        if isinstance(v, str):
            nv = pattern.sub(lambda m: new if m.group(1) == old else m.group(0), v)
            if nv != v:
                f[k] = nv
                changed = True
    return changed


def mutate_fact(fact: dict, kind: str) -> dict | None:
    """kind in numeric/date/direction。適用できなければNone。元factは変更しない(deepcopy)。"""
    f = copy.deepcopy(fact)
    if kind == "numeric":
        for k in ("numeric_value", "claim"):
            for m in _NUM.finditer(str(f.get(k) or "")):
                tok = m.group(1)
                if len(tok.replace(",", "").replace(".", "")) >= 2 and not _YEAR.fullmatch(tok):
                    new = _scale_number(tok)
                    if _replace_in(f, ("claim", "numeric_value"), tok, new, _NUM):
                        return {"fact": f, "detail": f"{tok}->{new}"}
        return None
    if kind == "date":
        for k in ("date_or_period", "claim"):
            m = _YEAR.search(str(f.get(k) or ""))
            if m:
                old, new = m.group(1), str(int(m.group(1)) - 1)
                if _replace_in(f, ("claim", "date_or_period"), old, new, _YEAR):
                    return {"fact": f, "detail": f"{old}->{new}"}
        return None
    if kind == "direction":
        claim = str(f.get("claim") or "")
        for a, b in _WORD_SWAPS:
            if a in claim:
                f["claim"] = claim.replace(a, b, 1)
                return {"fact": f, "detail": f"{a}->{b}"}
        return None
    raise ValueError(kind)


def build_injected(draft: dict, selected_ids: list, max_n: int = 3) -> list:
    """採用Factを優先し、種類(numeric/date/direction)が重ならないよう最大max_n件。"""
    by_id = {f["fact_id"]: f for f in draft["facts"]}
    order = [i for i in selected_ids if i in by_id] + [i for i in by_id if i not in selected_ids]
    out, used_kinds, used_src = [], set(), set()
    for kind in ("numeric", "date", "direction", "numeric"):
        if len(out) >= max_n:
            break
        for fid in order:
            if fid in used_src:
                continue
            if kind in used_kinds and kind != "numeric":
                break
            m = mutate_fact(by_id[fid], kind)
            if m is None:
                continue
            nf = m["fact"]
            nf["fact_id"] = f"INJ_{fid}_{kind}_{len(out) + 1}"
            out.append({"orig_fact_id": fid, "kind": kind, "detail": m["detail"],
                        "original_claim": by_id[fid]["claim"], "mutated_claim": nf["claim"],
                        "expected": "REJECTED", "fact": nf})
            used_kinds.add(kind)
            used_src.add(fid)
            break
    return out


def run_injection(article: str, client, budget: Budget, out_root: str, usage_log: str, dry_run: bool) -> dict:
    inputs_dir = lib.copy_inputs(article, out_root)
    data = lib.load_article_inputs(inputs_dir)
    draft_before = lib.draft_sha(data["draft"])
    injected = build_injected(data["draft"], data["m0_evidence"]["selected_fact_ids"])
    if len(injected) < 2:
        raise RuntimeError(f"[STOP] 注入Factを2件以上作れない: {article}")
    outd = f"{out_root}/{article}/optA"
    os.makedirs(f"{outd}/_work", exist_ok=True)
    save_json(f"{out_root}/{article}/_inputs/injected_facts.json",
              [{k: v for k, v in i.items() if k != "fact"} | {"injected_fact_id": i["fact"]["fact_id"]} for i in injected])
    inj_draft = {"facts": [i["fact"] for i in injected]}
    ids = [i["fact"]["fact_id"] for i in injected]
    rows = []
    for cap in (False, True):
        label = "capped" if cap else "uncapped"
        v = lib.verify_facts_trial(client, data["topic"], inj_draft, ids, cap=cap, work_dir=f"{outd}/_work",
                                   label=label, stage_tag=f"optA|{article}|inject|{label}", budget=budget,
                                   est_jpy=lib.EST_INJECT_JPY)
        got = {x["fact_id"]: x for x in v["parsed"]["verifications"]}
        for i in injected:
            fid = i["fact"]["fact_id"]
            verdict = (got.get(fid) or {}).get("verdict", "NO_RESULT")
            rows.append({"variant": label, "injected_fact_id": fid, "orig_fact_id": i["orig_fact_id"],
                         "kind": i["kind"], "verdict": verdict,
                         "outcome": {"REJECTED": "detected", "AMBIGUOUS": "not_passed_as_verified(partial)",
                                     "VERIFIED": "MISSED_CRITICAL_NG"}.get(verdict, "NO_RESULT_treated_as_not_detected")})
    missed = [r for r in rows if r["outcome"] == "MISSED_CRITICAL_NG"]
    res = {"article": article, "dry_run": dry_run, "n_injected": len(injected), "rows": rows,
           "missed_critical_ng": missed, "critical_ng": bool(missed),
           "original_draft_unchanged": lib.draft_sha(lib.load_article_inputs(inputs_dir)["draft"]) == draft_before,
           "cost": {"total_jpy": round(sum(
               v["total_jpy"] for k, v in lib.cost_by_stage_tag(usage_log, theme=lib.THEME_TAG).items()
               if k.startswith(f"optA|{article}|")), 3)},
           "disclaimer": "故障注入の結果は通常記事における誤り検出率の保証ではない(ユーザー§5)",
           "basis": "SYNTHETIC_DRYRUN_STUB(検出はstubの設定でありVerifierの能力を示さない)" if dry_run
           else "OFFICIAL_API_RESPONSE"}
    save_json(f"{outd}/result.json", res)
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--paid-confirm", default=None)
    ap.add_argument("--article", required=True)
    ap.add_argument("--out", default=OUT_ROOT)
    ap.add_argument("--other-spend-today-jpy", type=float, default=0.0)
    a = ap.parse_args(argv)
    if a.dry_run == bool(a.paid_confirm):
        raise SystemExit("--dry-run か --paid-confirm のどちらか一方だけ指定する")
    if a.paid_confirm and a.paid_confirm != lib.PAID_CONFIRM_TOKEN:
        raise SystemExit("--paid-confirm トークン不一致")
    out = a.out
    os.makedirs(out, exist_ok=True)
    before = lib.integrity_snapshot([a.article])
    lib.save_json(f"{out}/optA_integrity_before.json", before)
    lib.ensure_cost_logger(f"{out}/raw_usage_log.jsonl")
    if a.dry_run:
        usage_log = f"{out}/optA_stub_usage_log.jsonl"
        if os.path.exists(usage_log):
            os.remove(usage_log)
        data = lib.load_article_inputs(lib.copy_inputs(a.article, out))
        client = lib.StubClient({"m0_verdicts": data["m0_verdicts"], "m0_evidence": data["m0_evidence"],
                                 "n_facts_all": len(data["draft"]["facts"]), "m0_total_ws_calls": 14}, usage_log)
    else:
        usage_log = f"{out}/raw_usage_log.jsonl"
        client = lib.vfl01.get_client()
    budget = Budget(usage_log, "optA", out_root=out, other_spend_today_jpy=a.other_spend_today_jpy)
    rc = 0
    try:
        res = run_injection(a.article, client, budget, out, usage_log, a.dry_run)
        print(f"[optA] {a.article}: injected={res['n_injected']} critical_ng={res['critical_ng']} cost={res['cost']}")
    except BudgetStop as exc:
        print(str(exc))
        rc = 4
    after = lib.integrity_snapshot([a.article])
    cmp_ = lib.compare_snapshots(before, after)
    lib.save_json(f"{out}/optA_integrity_check.json", cmp_)
    if not cmp_["identical"]:
        print("[STOP] integrity mismatch", cmp_["diffs"][:5])
        return 5
    return rc


if __name__ == "__main__":
    sys.exit(main())
