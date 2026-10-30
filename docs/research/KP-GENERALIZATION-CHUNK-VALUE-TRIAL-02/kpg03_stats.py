# -*- coding: utf-8 -*-
"""集計: 方式D(前回、Before基準)と新方式E1L/E1S/E2/E3/E4の比較。
主評価: 自由な組合せ混入率 / 一般化成功率 / 意味・用法正確性 / 修正せず選べる率 / 良質候補の脱落。
参考: 3件以上選べるケース率 / 提示数 / 難易度分布 / run間ばらつき。母集団差(各armが実行済みのケース集合)を必ず表示する。
usage: python kpg03_stats.py [--mock] [--arms D,E1L,...] [--cases ALL14]"""
import os, sys, re, json, argparse, collections
HERE = os.path.dirname(os.path.abspath(__file__))
OLD = os.path.join(HERE, "..", "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01")
sys.path.insert(0, HERE); sys.path.insert(0, OLD)
import kpg03_manual as MAN3
import kpg01_manual as M1
import kpg03_llm as L

ALL14 = ["untidi_a2", "ai_cha_b1b", "jwst_m_a2", "jwst_m_b1b", "meta_w_b1b", "untidi_b1b", "ai_cha_a2", "meta_w_a2", "aiisland_b1b", "surname_b1b",
         "melos_a2", "ignobel_a2", "ignobel_b1b", "tesla_b1b"]
HARD6 = ALL14[:6]
GROUP = {c: "必須(Family X選定4記事)" for c in ALL14[:8]}
GROUP.update({"aiisland_b1b": "汎化(X/Y/Z)", "surname_b1b": "汎化(X/Y/Z)", "melos_a2": "汎化(X/Y/Z)", "ignobel_a2": "未使用記事", "ignobel_b1b": "未使用記事", "tesla_b1b": "未使用記事",
              "moon_a2": "汎化(X/Y/Z)", "moon_b1b": "汎化(X/Y/Z)", "melos_b1b": "汎化(X/Y/Z)"})
ARMS_ALL = ["D", "E1L", "E1S", "E2", "E3", "E4"]

# ---- 必須9例のパターン(display_form/source_spanで判定。目的=ユーザー指定の改善対象)
def _has(items, pat, field="display_form"):
    return any(re.search(pat, i[field].lower()) for i in items)
REQ9 = [
    ("G1 take points away from -> take something away from", ["untidi_a2", "untidi_b1b"], lambda it: ("ok" if _has(it, r"^take something away from$") else "ng_ungen" if _has(it, r"take points away", "display_form") else "absent")),
    ("G2 make life work -> make something work", ["untidi_a2"], lambda it: "ok" if _has(it, r"^make something work$") else ("ng_ungen" if _has(it, r"make life work") else "absent")),
    ("G3 at the time of writing -> at the time of", ["meta_w_a2"], lambda it: "ok" if _has(it, r"^at the time of$") else ("ng_ungen" if _has(it, r"at the time of writing") else "absent")),
    ("G4 narrow down the source -> narrow down", ["jwst_m_a2", "jwst_m_b1b"], lambda it: "ok" if _has(it, r"^narrow (something )?down$") else "absent"),
    ("G5 turn the usual steps around -> turn something around", ["jwst_m_a2"], lambda it: "ok" if _has(it, r"^turn something around$") else "absent"),
    ("V1 confirm a clear fall/drop(提示されない=良)", ["ai_cha_a2", "ai_cha_b1b"], lambda it: "ng_free" if _has(it, r"confirm a clear", "source_span") else "ok"),
    ("V2 make room for(提示=良)", ["meta_w_a2", "meta_w_b1b"], lambda it: "ok" if _has(it, r"make room for") else "absent"),
    ("V3 blow a whistle(提示=良)", ["ai_cha_a2"], lambda it: "ok" if _has(it, r"blow a whistle") else "absent"),
    ("V4 sales pitch(提示=良)", ["ai_cha_a2", "ai_cha_b1b"], lambda it: "ok" if _has(it, r"sales pitch") else "absent"),
    ("NEW1 deep image / point-like object(提示されない=良)", ["jwst_m_a2", "jwst_m_b1b"], lambda it: "ng_free" if (_has(it, r"deep image") or _has(it, r"point-like object")) else "ok"),
]


def norm_core(s):
    s = re.sub(r"[.,;:!?\"()]", "", s.lower()).strip()
    return re.sub(r"^(the|a|an) ", "", s)


def load_arm(arm, cid, mock, suffix=""):
    if arm == "D":
        p = os.path.join(OLD, "kpg01_work", "results", f"{cid}__D_luna.json")
        if not os.path.exists(p): return None
        r = json.load(open(p, encoding="utf-8"))
        return {"items": r["items"], "cost_jpy": r.get("cost_jpy")}
    p = os.path.join(L.WORK, "mock_results" if mock else "results", f"{cid}__{arm}{suffix}.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def code_of(arm, cid, it, mock):
    """Returns (code or None, judged?)"""
    d = it["display_form"]
    if arm == "D":
        if (cid, d) in MAN3.D_OVERRIDE: return MAN3.D_OVERRIDE[(cid, d)], True
        r = M1.NG.get(cid, {}).get("D_luna", {}).get(d)
        if r is None: return None, True
        if "易しい" in r and "自由" not in r: return None, True
        return ("FREE" if "自由" in r else "GEN" if any(k in r for k in ("未一般化", "過一般化", "時制", "受動")) else "MEAN" if "語義" in r else "OTHER"), True
    judged = (arm, cid) in MAN3.JUDGED
    m = MAN3.MAN.get(arm, {}).get(cid, {}).get(d)
    return (m[0] if m else None), judged


def stats(arm, cases, mock):
    t = collections.Counter(); per_case = {}
    diff = collections.Counter(); done = []
    for cid in cases:
        r = load_arm(arm, cid, mock)
        if r is None: continue
        done.append(cid)
        its = r["items"]; k = collections.Counter(); unj = 0
        for it in its:
            c, j = code_of(arm, cid, it, mock)
            if not j: unj += 1
            k[c or "OK"] += 1
            diff[it.get("difficulty") or "?"] += 1
            applied = norm_core(it["source_span"]) != norm_core(it["display_form"])
            t["applied"] += applied
            t["applied_gen_fail"] += (applied and c == "GEN")
        per_case[cid] = dict(n=len(its), ok=k["OK"], codes=dict(k), unj=unj, cost=r.get("cost_jpy"))
        t["n"] += len(its); t["ok"] += k["OK"]; t["unj"] += unj
        for cd in MAN3.CODES: t[cd] += k[cd]
        t["ge3"] += k["OK"] >= 3
    return dict(arm=arm, cases=done, t=t, per_case=per_case, diff=dict(diff))


def loss_vs_D(arm, cases, mock):
    """Dで『修正せず選べた』候補が、armに残っているか(spanのcore or display_form一致)。"""
    lost, tot = [], 0
    for cid in cases:
        d, a = load_arm("D", cid, mock), load_arm(arm, cid, mock)
        if not d or not a: continue
        akeys = {norm_core(i["source_span"]) for i in a["items"]} | {i["display_form"].lower() for i in a["items"]}
        for it in d["items"]:
            c, _ = code_of("D", cid, it, mock)
            if c is None:
                tot += 1
                if norm_core(it["source_span"]) not in akeys and it["display_form"].lower() not in akeys:
                    lost.append((cid, it["display_form"]))
    return lost, tot


def pct(a, b):
    return f"{a}/{b} ({100*a/b:.0f}%)" if b else "-"


def report(arms, cases, mock):
    ss = {a: stats(a, cases, mock) for a in arms}
    unj = sum(ss[a]["t"]["unj"] for a in arms)
    if unj:
        print(f"**注意: Sonnet実読が未記入の候補が{unj}件あり、『修正せず選べる』等はOK扱いの暫定値(kpg03_manual.MAN/JUDGEDを記入して再集計)。**\n")
    print("## 母集団(各armが実行済みのケース)")
    for a, s in ss.items():
        print(f"- {a}: {len(s['cases'])}ケース {','.join(s['cases'])}")
    common = [c for c in cases if all(c in ss[a]["cases"] for a in arms)]
    print(f"- 全armで共通のケース: {len(common)} ({','.join(common)}) ※率は各arm自身の母集団。厳密比較は共通ケースの表を参照\n")
    for label, cs in (("各arm自身の母集団", None), ("共通ケースのみ(母集団差を除去)", common)):
        print(f"## 主評価・参考指標 [{label}]")
        print("| arm | 提示数(n) | 修正せず選べる | 自由な組合せ混入率 | 一般化成功率(一般化適用分) | 意味・用法正確性 | 3件以上ケース | 平均提示数 | 未判定 |")
        print("|---|---|---|---|---|---|---|---|---|")
        for a in arms:
            s = ss[a] if cs is None else stats(a, cs, mock)
            t = s["t"]; nc = len(s["cases"])
            print(f"| {a} | {t['n']} | {pct(t['ok'], t['n'])} | {pct(t['FREE'], t['n'])} | {pct(t['applied']-t['applied_gen_fail'], t['applied'])} | {pct(t['n']-t['MEAN'], t['n'])} | {pct(t['ge3'], nc)} | {t['n']/nc:.1f} | {t['unj']} |" if nc else f"| {a} | - |")
        print()
    print("## 良質候補の脱落(Dで修正せず選べた候補が残っているか)")
    for a in arms:
        if a == "D": continue
        lost, tot = loss_vs_D(a, cases, mock)
        print(f"- {a}: 脱落 {len(lost)}/{tot} " + ", ".join(f"{c}:{d}" for c, d in lost[:12]) + (" …" if len(lost) > 12 else ""))
    print("\n## 難易度分布(参考。易しい表現は除外しない)")
    for a in arms:
        print(f"- {a}: {ss[a]['diff']}")
    print("\n## 必須例+ユーザー指摘例(ok=達成 / absent=提示なし / ng_*=悪い状態)")
    print("| 例 | " + " | ".join(arms) + " |"); print("|---|" + "---|" * len(arms))
    for name, cs, fn in REQ9:
        row = []
        for a in arms:
            res = []
            for cid in cs:
                r = load_arm(a, cid, mock)
                res.append(fn(r["items"]) if r else "-")
            row.append("/".join(res))
        print(f"| {name} | " + " | ".join(row) + " |")
    print("\n## ケース別(ok/n: コード内訳)")
    for cid in cases:
        row = []
        for a in arms:
            pc = ss[a]["per_case"].get(cid)
            row.append(f"{a} {pc['ok']}/{pc['n']}" if pc else f"{a} -")
        print(f"- {cid}: " + " | ".join(row))
    # 費用
    print("\n## 費用(円/レベル、cache hit分は0。台帳=" + ("mock" if mock else "実費") + ")")
    for a in arms:
        cs = [c for c in ss[a]["cases"]]
        costs = [ss[a]["per_case"][c]["cost"] for c in cs if ss[a]["per_case"][c]["cost"] is not None]
        print(f"- {a}: 平均¥{sum(costs)/len(costs):.2f} / 合計¥{sum(costs):.2f} ({len(costs)}ケース)" if costs else f"- {a}: -")
    # run間ばらつき
    rr = []
    for a in arms:
        if a == "D": continue
        for cid in cases:
            r1, r2 = load_arm(a, cid, mock), load_arm(a, cid, mock, "_r2")
            if r1 and r2:
                s1 = {i["display_form"] for i in r1["items"]}; s2 = {i["display_form"] for i in r2["items"]}
                rr.append((a, cid, len(s1 & s2), len(s1 | s2)))
    if rr:
        print("\n## run間ばらつき(同一入力・SALT違い。共通/和集合)")
        for a, cid, i, u in rr: print(f"- {a} {cid}: 提示形の一致 {i}/{u}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--mock", action="store_true"); ap.add_argument("--arms", default=",".join(ARMS_ALL)); ap.add_argument("--cases", default="ALL14")
    a = ap.parse_args()
    cases = ALL14 if a.cases == "ALL14" else a.cases.split(",")
    report(a.arms.split(","), cases, a.mock)
