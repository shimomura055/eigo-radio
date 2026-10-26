# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICE1-MALE7-TRIAL-01: 集計・区間推定・Phase 2対象/推奨条件の機械判定(DESIGN_01の規則そのまま。API 0)。
使い方: py ym7_summarize_01.py --in measure/samples_01.json --design DESIGN_01.md --out RESULT_01.md --json measure/summary_01.json [--phase 1|2]
 --phase 1: Phase 2対象Voiceを機械判定(DESIGN_01 §6)。--phase 2: 推奨条件(§7)も判定。DESIGN_01.mdのsha256を出力に記録(固定後の改変検出)。"""
import argparse, hashlib, json, os, sys
from collections import defaultdict
import numpy as np

VOICES = ["Algieba", "Schedar", "Fenrir", "Orus", "Puck", "Iapetus", "Sadaltager"]
LV = {"a2": "Standard", "b1b": "Advanced"}
CELLS = [(lv, b) for lv in ("a2", "b1b") for b in (1, 2, 3)]
B_BOOT = 10000
SEED = 20261026
ALPHA0 = 0.5          # Jeffreys型の弱い事前(0件でも区間が0幅にならない)
OLD_SRC = ("run01_prod", "v1cand")       # 過去日に生成された再利用(感度分析で除外)


def seed_for(*keys):
    h = hashlib.sha256(("|".join(map(str, keys)) + str(SEED)).encode()).hexdigest()
    return int(h[:12], 16)


def cell_arrays(rows, key):
    d = defaultdict(list)
    for r in rows:
        v = r.get(key)
        d[(r["level"], r["body"])].append(float(v) if v is not None else 0.0)
    return d


def boot_draws(rows, key, cells, tag):
    """cell層別ブートストラップ: 各cellを復元抽出→cell平均→cell等重み平均。return draws(B,), point。cell欠落/空は除外して cells_used を返す。"""
    ca = cell_arrays(rows, key)
    used = [c for c in cells if len(ca.get(c, [])) > 0]
    if not used:
        return None, None, used
    rng = np.random.default_rng(seed_for("boot", tag, key))
    acc = np.zeros(B_BOOT)
    pt = 0.0
    for c in used:
        x = np.array(ca[c])
        idx = rng.integers(0, len(x), size=(B_BOOT, len(x)))
        acc += x[idx].mean(axis=1)
        pt += x.mean()
    return acc / len(used), pt / len(used), used


def pois_draws(rows, key, cells, tag, binary=False):
    """Gamma-Poisson(件数)/Beta-Binomial(2値)の事後からcell等重み平均を描く。0件でも区間が潰れない。"""
    ca = cell_arrays(rows, key)
    used = [c for c in cells if len(ca.get(c, [])) > 0]
    if not used:
        return None
    rng = np.random.default_rng(seed_for("pois", tag, key))
    acc = np.zeros(B_BOOT)
    for c in used:
        x = np.array(ca[c])
        n, s = len(x), x.sum()
        if binary:
            acc += rng.beta(ALPHA0 + s, ALPHA0 + n - s, size=B_BOOT)
        else:
            acc += rng.gamma(ALPHA0 + s, 1.0 / n, size=B_BOOT)
    return acc / len(used)


def interval(rows, key, cells, tag, binary=False, union=True):
    bd, pt, used = boot_draws(rows, key, cells, tag)
    if bd is None:
        return None
    lo, hi = np.percentile(bd, [2.5, 97.5])
    if union and key in ("mid_long1000", "long1000_n", "clause_long1000", "bad_mid", "bad_any", "rep_flag_i", "asr_fail_i"):
        pd = pois_draws(rows, key, cells, tag, binary=binary)
        plo, phi = np.percentile(pd, [2.5, 97.5])
        lo, hi = min(lo, plo), max(hi, phi)
    return {"mean": float(pt), "lo": float(lo), "hi": float(hi), "cells_used": len(used), "draws": bd}


def prep(rows):
    for r in rows:
        r["rep_flag_i"] = 1 if r.get("rep_flag") else 0
        r["asr_fail_i"] = 0 if r.get("asr_verified") else 1
    return rows


def voice_stats(rows, voice, cells, tag):
    rs = [r for r in rows if r["voice"] == voice and r["kind"] == "main" and (r["level"], r["body"]) in cells]
    if not rs:
        return None
    out = {"n": len(rs), "n_fresh": sum(1 for r in rs if r["origin"] == "fresh"), "n_reuse": sum(1 for r in rs if r["origin"] == "reuse"),
           "n_takes_fresh": len({(r["level"], r["body"], r["take"]) for r in rs if r["origin"] == "fresh"})}
    for key, binary in (("mid_long1000", False), ("long1000_n", False), ("occ_pct", False), ("max_ms", False), ("bad_mid", True), ("bad_any", True), ("rep_flag_i", True), ("asr_fail_i", True)):
        iv = interval(rs, key, cells, tag, binary=binary)
        out[key] = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in iv.items() if k != "draws"}
        out[key + "_draws"] = iv["draws"]
    out["worst_max_ms"] = max(r["max_ms"] for r in rs)
    out["asr_pass"] = 1 - out["asr_fail_i"]["mean"]
    out["cells_n"] = {f"{LV[lv]}-本文{b}": sum(1 for r in rs if r["level"] == lv and r["body"] == b) for lv, b in cells}
    return out


def strip(d):
    return {k: v for k, v in d.items() if not k.endswith("_draws")}


def decide_phase2(S):
    """DESIGN_01 §6(事前固定): S=pooled voice_stats。"""
    prim = {v: S[v]["mid_long1000"] for v in S if S[v]}
    best = min(prim, key=lambda v: prim[v]["mean"])
    dropped = [v for v in prim if v != "Algieba" and prim[v]["lo"] > prim[best]["hi"]]
    alive = [v for v in prim if v not in dropped]
    ranked = sorted(alive, key=lambda v: prim[v]["mean"])
    sep = all(prim[v]["lo"] > prim[best]["hi"] for v in prim if v != best)       # bestが全員から区間分離
    top = ranked[:3]
    if "Algieba" not in top and "Algieba" in alive:
        top = ranked[:2] + ["Algieba"]
    phase2 = [] if sep else top
    return {"best_by_mean": best, "dropped": dropped, "alive": alive, "ranked_alive": ranked, "best_separated_from_all": sep, "phase2_voices": phase2,
            "phase2_max_takes": 12 * len(phase2)}


def recommend(S, SL, takes):
    """DESIGN_01 §7(事前固定)。S=pooled, SL={level:{voice:stats}}。候補ごとに全条件を機械判定。"""
    A = S["Algieba"]
    res = {}
    take_ok = defaultdict(lambda: [0, 0])
    for t in takes:
        take_ok[t["voice"]][1] += 1
        take_ok[t["voice"]][0] += 1 if t.get("status") == "OK" else 0
    for v in VOICES:
        if v == "Algieba" or not S.get(v):
            continue
        c = S[v]
        pa, pc = A["mid_long1000"], c["mid_long1000"]
        improve = pc["mean"] < pa["mean"]
        sep = pc["hi"] < pa["lo"]
        half = c["bad_mid"]["mean"] <= 0.5 * A["bad_mid"]["mean"]
        lvl_ok = all(SL[lv][v]["mid_long1000"]["mean"] <= SL[lv]["Algieba"]["mid_long1000"]["mean"] for lv in SL if SL[lv].get(v) and SL[lv].get("Algieba"))
        asr_ok = c["asr_pass"] >= A["asr_pass"]
        rep_ok = c["rep_flag_i"]["mean"] <= A["rep_flag_i"]["mean"]
        ok_t, n_t = take_ok.get(v, [0, 0])
        take_ok_rate = (ok_t / n_t) if n_t else None
        det_ok = (n_t >= 10) and take_ok_rate is not None and take_ok_rate >= 0.9
        cond = {"improve_point": improve, "sep_or_halved_bad_take": bool(sep or half), "interval_separated": bool(sep), "bad_take_halved": bool(half),
                "both_levels_not_worse": lvl_ok, "asr_pass_ge_algieba": asr_ok, "rep_flag_le_algieba": rep_ok,
                "deterministic_issue_free(fresh take OK>=0.9 & n>=10)": det_ok, "fresh_take_ok_rate": take_ok_rate, "fresh_takes": n_t}
        cond["ALL_MET"] = bool(improve and (sep or half) and lvl_ok and asr_ok and rep_ok and det_ok)
        res[v] = cond
    cands = [v for v in res if res[v]["ALL_MET"]]
    cands.sort(key=lambda v: S[v]["mid_long1000"]["mean"])
    return {"per_voice": res, "recommend_candidates": cands, "candidate_top": (cands[0] if cands else None)}


def variance_shares(rows):
    """主要指標(mid_long1000)の平方和分解(不均衡のため近似・周辺SS)。"""
    x = np.array([r["mid_long1000"] for r in rows], float)
    g = x.mean()
    tot = ((x - g) ** 2).sum()

    def ss(keyf):
        d = defaultdict(list)
        for r, xi in zip(rows, x):
            d[keyf(r)].append(xi)
        return sum(len(v) * (np.mean(v) - g) ** 2 for v in d.values())
    cell = ss(lambda r: (r["voice"], r["level"], r["body"]))
    return {"total_SS": float(tot), "voice_marginal": float(ss(lambda r: r["voice"]) / tot) if tot else 0, "body_marginal": float(ss(lambda r: r["body"]) / tot) if tot else 0,
            "level_marginal": float(ss(lambda r: r["level"]) / tot) if tot else 0, "cells(Voice×本文×レベル)": float(cell / tot) if tot else 0,
            "within_cell(同条件の生成ばらつき)": float(1 - cell / tot) if tot else 0}


def fmt_iv(d, nd=2):
    return f"{d['mean']:.{nd}f} [{d['lo']:.{nd}f}, {d['hi']:.{nd}f}]"


def table(S, title, cells_note=""):
    L = [f"### {title}", cells_note, "",
         "| Voice | n(fresh/reuse) | 文中≥1.0s回/sample(主要) 平均[95%区間] | 全≥1.0s回/sample | 占有率% | 最長停止ms(平均 / 最悪) | 悪いtake率P(文中≥1s≧1) [区間] | ASR合格率 | Repetition旗率 |",
         "|---|---|---|---|---|---|---|---|---|"]
    for v in VOICES:
        s = S.get(v)
        if not s:
            L.append(f"| {v} | 0 | - | - | - | - | - | - | - |")
            continue
        L.append(f"| {v} | {s['n']} ({s['n_fresh']}/{s['n_reuse']}) | {fmt_iv(s['mid_long1000'])} | {fmt_iv(s['long1000_n'])} | {s['occ_pct']['mean']:.1f} | {s['max_ms']['mean']:.0f} / {s['worst_max_ms']} | "
                 f"{fmt_iv(s['bad_mid'])} | {100 * s['asr_pass']:.0f}% | {100 * s['rep_flag_i']['mean']:.0f}% |")
    return L


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--design", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--phase", type=int, default=1)
    a = ap.parse_args(argv)
    rows = prep([r for r in json.load(open(a.inp, encoding="utf-8")) if r["voice"] in VOICES])
    takes_p = a.inp.replace(".json", "_takes.json")
    takes = json.load(open(takes_p, encoding="utf-8")) if os.path.exists(takes_p) else []
    design_sha = hashlib.sha256(open(a.design, "rb").read()).hexdigest()
    main_rows = [r for r in rows if r["kind"] == "main"]
    S = {v: voice_stats(main_rows, v, CELLS, "pooled") for v in VOICES}
    SL = {lv: {v: voice_stats(main_rows, v, [c for c in CELLS if c[0] == lv], lv) for v in VOICES} for lv in ("a2", "b1b")}
    SB = {(lv, b): {v: voice_stats(main_rows, v, [(lv, b)], f"{lv}{b}") for v in VOICES} for lv, b in CELLS}
    # 感度分析
    first = [r for r in main_rows if r["attempt"] == 1]
    S_first = {v: voice_stats(first, v, CELLS, "first") for v in VOICES}
    new_only = [r for r in main_rows if not (r["origin"] == "reuse" and r["src"] in OLD_SRC)]
    S_new = {v: voice_stats(new_only, v, CELLS, "newonly") for v in VOICES}
    ph2 = decide_phase2(S)
    rec = recommend(S, SL, takes) if a.phase >= 2 else recommend(S, SL, takes)
    # Algieba差
    diffs = {}
    for v in VOICES:
        if v == "Algieba" or not S.get(v) or not S.get("Algieba"):
            continue
        d = S[v]["mid_long1000_draws"] - S["Algieba"]["mid_long1000_draws"]
        lo, hi = np.percentile(d, [2.5, 97.5])
        diffs[v] = {"delta_mean": float(S[v]["mid_long1000"]["mean"] - S["Algieba"]["mid_long1000"]["mean"]), "boot_lo": float(lo), "boot_hi": float(hi),
                    "P(v<Algieba)": float((d < 0).mean())}
    vs = variance_shares(main_rows)
    out = {"design_sha256": design_sha, "phase": a.phase, "n_samples_main": len(main_rows), "n_fallback_excluded": sum(1 for r in rows if r["kind"] != "main"),
           "pooled": {v: strip(S[v]) for v in VOICES if S[v]}, "by_level": {lv: {v: strip(SL[lv][v]) for v in VOICES if SL[lv][v]} for lv in SL},
           "by_cell": {f"{lv}_b{b}": {v: strip(SB[(lv, b)][v]) for v in VOICES if SB[(lv, b)][v]} for lv, b in CELLS},
           "sens_first_attempt": {v: strip(S_first[v]) for v in VOICES if S_first[v]}, "sens_new_only": {v: strip(S_new[v]) for v in VOICES if S_new[v]},
           "phase2_decision": ph2, "recommendation_check": rec, "diff_vs_algieba": diffs, "variance_shares": vs}
    json.dump(out, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))

    L = [f"# RESULT_01(自動生成。DESIGN_01 sha256={design_sha[:16]}…、Phase {a.phase}集計、B={B_BOOT}、seed={SEED})", "",
         f"main sample={len(main_rows)}(minimal_fallback等の別条件{out['n_fallback_excluded']}件は除外)。unit=raw attempt 1本。区間=cell層別ブートストラップ(Voice内で本文×レベル6cellを等重み)"
         "と、件数/2値は Jeffreys型 Gamma-Poisson/Beta 事後の**広い方**(0件でも区間が潰れない)。fresh=今回生成、reuse=前回Trial(Algieba/Schedarのみ)。", ""]
    L += table(S, "7名比較表(全レベル・全本文、6cell等重み)")
    for lv in ("a2", "b1b"):
        L += [""] + table(SL[lv], f"{LV[lv]}のみ(3本文等重み)")
    for lv, b in CELLS:
        L += [""] + table(SB[(lv, b)], f"{LV[lv]} 本文{b}")
    L += ["", "### Algieba比(主要指標の差、bootstrap 95%)", "| Voice | Δ(文中≥1s回/sample) | 95%区間 | P(Voice<Algieba) |", "|---|---|---|---|"]
    for v, d in diffs.items():
        L.append(f"| {v} | {d['delta_mean']:+.3f} | [{d['boot_lo']:+.3f}, {d['boot_hi']:+.3f}] | {d['P(v<Algieba)']:.2f} |")
    L += ["", "### 感度分析", ""] + table(S_first, "初回attempt(attempt==1)のみ") + [""] + table(S_new, "過去日の再利用(run01_prod/v1cand)を除外")
    L += ["", "### 切り分け(主要指標の平方和寄与、不均衡のため近似の周辺SS)"] + [f"- {k}: {v:.3f}" if k != "total_SS" else f"- total_SS: {v:.1f}" for k, v in vs.items()]
    L += ["", ("### Phase 2対象の機械判定(DESIGN_01 §6)" if a.phase == 1 else "### Phase 2対象の機械判定(DESIGN_01 §6)を現在の全データで再計算した値(参考)。**実際のPhase 2対象はPhase 1終了時点の判定=measure/summary_phase1_01.json(Puck, Orus, Algieba)で、これを実行した**"), "```", json.dumps(ph2, ensure_ascii=False, indent=1), "```", "",
          "### 推奨条件の機械判定(DESIGN_01 §7)", "```", json.dumps(rec, ensure_ascii=False, indent=1), "```"]
    open(a.out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(json.dumps({"phase2": ph2, "recommend": rec["recommend_candidates"], "n": len(main_rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
