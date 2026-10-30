# -*- coding: utf-8 -*-
"""最終集計(API 0)。原文§8④の指標: 意味・用法誤り件数 / 一般化成功率 / 自由組合せ混入率 / 良質候補の脱落 / そのまま選べる率 / 戻し率 / 一般化維持率 / 量産単価 / 3件以上ケース数。
0件を『誤り率0』と書かない: すべての件数に Clopper-Pearson 片側95%上限を併記する(委任_02)。
ラベル(Sonnet実読): 旧arm(D/E1L/E1S/E2/E3/E4)の意味・用法=kpg04_work/audit/p0_s_axis_labels.json(P0再監査)、それ以外の旧コード=TRIAL-02/01の実読(MAN3/M1.NG)。
新arm(N1a/N1/N2/N4/N4d)=kpg04_work/audit/new_arm_labels.json(実読+独立評価の根拠確認)。PROD=TRIAL-01 kpg01_manual.NG['Before']+P0再監査。
level: strict=確定NG / boundary=境界例(別集計) / minor=軽微な形と訳の不対応。S軸=意味・用法(ARG_TYPE/SENSE_SHIFT/FRAME_SHIFT/MOD_SHIFT/GLOSS_MISMATCH/GLOSS_SENSE)。
usage: python kpg04_stats.py [--cases ALL14|HELDOUT|a,b] [--arms PROD,D,E1L,E4,N1a,N1,N2,N4]"""
import os, sys, re, json, argparse, collections, math
HERE = os.path.dirname(os.path.abspath(__file__))
OLD1 = os.path.join(HERE, "..", "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01")
OLD2 = os.path.join(HERE, "..", "KP-GENERALIZATION-CHUNK-VALUE-TRIAL-02")
sys.path.insert(0, HERE); sys.path.insert(0, OLD1); sys.path.insert(0, OLD2)
import kpg04_llm as L
import kpg04_methods as M
import kpg04_run as R
import kpg04_eval as E
import kpg03_manual as MAN3
import kpg01_manual as M1

AUD = os.path.join(L.WORK, "audit")
S_CODES = {"ARG_TYPE", "SENSE_SHIFT", "FRAME_SHIFT", "MOD_SHIFT", "GLOSS_MISMATCH", "GLOSS_SENSE"}
LEGACY = ("PROD", "D", "E1L", "E1S", "E2", "E3", "E4")


def up95(k, n):
    """Clopper-Pearson 片側95%上限(二分探索)。"""
    if n == 0:
        return 1.0
    if k >= n:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(60):
        p = (lo + hi) / 2
        cdf = sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
        if cdf > 0.05:
            lo = p
        else:
            hi = p
    return hi


def frac(k, n):
    return f"{k}/{n} ({100 * k / n:.0f}%, 95%上限{100 * up95(k, n):.1f}%)" if n else "-"


def nkey(s):
    return " ".join(M._norm_hw(s))


def load_p0():
    d = json.load(open(os.path.join(AUD, "p0_s_axis_labels.json"), encoding="utf-8"))
    out = {}
    for x in d["labels"]:
        out[(x["case"], nkey(x["span"]), nkey(x["display_form"]), x["gloss"].strip())] = x
    return out


def load_new():
    p = os.path.join(AUD, "new_arm_labels.json")
    d = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"labels": []}
    out = {}
    for x in d["labels"]:
        out[(x["arm"], x["case"], nkey(x["display_form"]))] = x
    return out


P0, NEW = load_p0(), load_new()
_corpus = None


def corpus():
    global _corpus
    if _corpus is None:
        _corpus = R.load_corpus()
    return _corpus


def old_code(arm, cid, it):
    """旧実読(TRIAL-01/02)を新コードへ写す。returns (code|None, reason|None)。"""
    d = it["display_form"]
    if arm == "PROD":
        nr = M1.NG.get(cid, {}).get("Before", {})
        r = next((v for k, v in nr.items() if k.lower() == d.lower() or k.lower() == it["source_span"].lower()), None)
        if r is None or ("易しい" in r and "自由" not in r):
            return None, None
        if any(k in r for k in ("自由", "断片", "塊でない", "節の")):
            return "FREE", r
        if any(k in r for k in ("未一般化", "本文固有", "未原型化", "大文字", "Now")):
            return "UNDER_GEN", r
        return "OTHER", r
    if arm == "D":
        if (cid, d) in MAN3.D_OVERRIDE:
            c, r = MAN3.D_OVERRIDE[(cid, d)], "TRIAL-02の実読(D)"
        else:
            r = M1.NG.get(cid, {}).get("D_luna", {}).get(d)
            if r is None or ("易しい" in r and "自由" not in r):
                return None, None
            c = "FREE" if "自由" in r else "GEN" if any(k in r for k in ("未一般化", "過一般化", "時制", "受動")) else "MEAN" if "語義" in r else "OTHER"
    else:
        m = MAN3.MAN.get(arm, {}).get(cid, {}).get(d)
        if not m:
            return None, None
        c, r = m[0], m[1]
    if c is None:
        return None, None
    if c == "MEAN":
        return (None, None) if d in ("take a turn", "set a limit") else ("OTHER", r)     # 原文§2-C: 意味を損なわない修飾語除去は許容
    if c == "GEN":
        return "UNDER_GEN", r
    return c, r


def label(arm, cid, it):
    """returns (code|None, level|None, reason|None)。S軸ラベル優先。"""
    if arm in LEGACY:
        k = (cid, nkey(it["source_span"]), nkey(it["display_form"]), (it.get("gloss_ja") or "").strip())
        x = P0.get(k)
        if x:
            return x["code"], x["level"], x["reason"]
        oc, rs = old_code(arm, cid, it)
        return (oc, "strict_N", rs or "TRIAL-02/01の実読") if oc else (None, None, None)
    x = NEW.get((arm, cid, nkey(it["display_form"])))
    return (x["code"], x["level"], x["reason"]) if x else (None, None, None)


def applied(it):
    """一般化が適用された(形が本文と異なる。戻していない)。"""
    if it.get("reverted"):
        return False
    return nkey(it["display_form"]) != nkey(M.src_form(it["source_span"])) and nkey(it["display_form"]) != nkey(re.sub(r"^(the|a|an) ", "", M.src_form(it["source_span"])))


def norm_core(s):
    s = re.sub(r"[.,;:!?\"()]", "", s.lower()).strip()
    return re.sub(r"^(the|a|an) ", "", s)


def items_of(arm, cid):
    return E.load_arm_items(arm, cid, corpus())


def cost_of(arm, cid):
    if arm == "PROD":
        return None
    if arm.startswith("N"):
        p = os.path.join(L.WORK, "results", f"{cid}__{arm}.json")
    elif arm == "D":
        p = os.path.join(OLD1, "kpg01_work", "results", f"{cid}__D_luna.json")
    else:
        p = os.path.join(OLD2, "kpg03_work", "results", f"{cid}__{arm}.json")
        if not os.path.exists(p):
            p = os.path.join(L.WORK, "results", f"{cid}__{arm}.json")
    return json.load(open(p, encoding="utf-8")).get("cost_jpy") if os.path.exists(p) else None


def collect(arm, cases):
    rows, done = [], []
    for cid in cases:
        its = items_of(arm, cid)
        if its is None:
            continue
        done.append(cid)
        for it in its:
            c, lv, rs = label(arm, cid, it)
            rows.append(dict(case=cid, it=it, code=c, level=lv, reason=rs))
    return rows, done


def summarize(arm, cases):
    rows, done = collect(arm, cases)
    n = len(rows)
    s_strict = [r for r in rows if r["code"] in S_CODES and r["level"] == "strict"]
    s_bound = [r for r in rows if r["code"] in S_CODES and r["level"] == "boundary"]
    s_minor = [r for r in rows if r["code"] in S_CODES and r["level"] == "minor"]
    free = [r for r in rows if r["code"] == "FREE"]
    nax = [r for r in rows if r["code"] in ("NAT", "UNDER_GEN", "OVER_GEN", "OTHER")]
    ok_strict = [r for r in rows if not r["code"]]
    app = [r for r in rows if applied(r["it"])]
    app_ng = [r for r in app if r["code"] and r["code"] != "FREE"]
    rev = [r for r in rows if r["it"].get("reverted")]
    ge3 = sum(1 for cid in done if sum(1 for r in rows if r["case"] == cid and not r["code"]) >= 3)
    costs = [c for c in (cost_of(arm, cid) for cid in done) if c is not None]
    return dict(arm=arm, cases=done, n=n, s_strict=s_strict, s_bound=s_bound, s_minor=s_minor, free=free, nax=nax, ok=ok_strict, app=app, app_ng=app_ng, rev=rev, ge3=ge3, costs=costs, rows=rows)


def retention(arm, base, cases):
    """基準arm(E1L等)で○だった候補(同span)のうち、arm側で: 脱落 / 一般化維持(基準が一般化適用済みの候補のみ分母) / 戻し。"""
    drop, tot, gen_tot, gen_keep, lost_gen = [], 0, 0, 0, []
    for cid in cases:
        b, a = items_of(base, cid), items_of(arm, cid)
        if b is None or a is None:
            continue
        amap = collections.defaultdict(list)
        for it in a:
            amap[norm_core(it["source_span"])].append(it)
            amap[norm_core(it["display_form"])].append(it)
        for it in b:
            c, _, _ = label(base, cid, it)
            if c:
                continue
            tot += 1
            hit = amap.get(norm_core(it["source_span"])) or amap.get(norm_core(it["display_form"]))
            if not hit:
                drop.append((cid, it["display_form"]))
                continue
            if applied(it):
                gen_tot += 1
                if any(applied(h) for h in hit):
                    gen_keep += 1
                else:
                    lost_gen.append((cid, it["source_span"], it["display_form"], hit[0]["display_form"]))
    return dict(tot=tot, drop=drop, gen_tot=gen_tot, gen_keep=gen_keep, lost_gen=lost_gen)


def report(arms, cases, base="E1L", out=sys.stdout):
    P = lambda *a: print(*a, file=out)
    ss = {a: summarize(a, cases) for a in arms}
    P("## 母集団(各armが実行済みのケース)")
    for a, s in ss.items():
        P(f"- {a}: {len(s['cases'])}ケース / 提示{s['n']}件")
    P("\n## 指標(分母は各arm自身の提示件数。0件でも『誤り率0』とは書かず95%上限を併記)")
    P("| arm | 提示n | 意味・用法NG(確定) | 境界例 | 軽微(訳の不対応) | 自由組合せ混入 | 自然さ等(N軸) | そのまま選べる率(確定NG・境界・軽微を除く) | 一般化適用 | 一般化成功率 | 戻し数(率) | 3件以上ケース |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for a, s in ss.items():
        n = s["n"]
        sel = sum(1 for r in s["rows"] if not r["code"])
        P(f"| {a} | {n} | {frac(len(s['s_strict']), n)} | {len(s['s_bound'])} | {len(s['s_minor'])} | {frac(len(s['free']), n)} | {len(s['nax'])} | {frac(sel, n)} | "
          f"{len(s['app'])} | {frac(len(s['app']) - len(s['app_ng']), len(s['app']))} | {frac(len(s['rev']), n)} | {s['ge3']}/{len(s['cases'])} |")
    P("\n## 意味・用法NG(確定)の内訳")
    for a, s in ss.items():
        P(f"- {a}: " + ("; ".join(f"{r['case']}:{r['it']['display_form']}[{r['code']}]" for r in s["s_strict"]) or "なし") +
          ((" / 境界: " + "; ".join(f"{r['case']}:{r['it']['display_form']}[{r['code']}]" for r in s["s_bound"])) if s["s_bound"] else ""))
    P(f"\n## 良質候補の維持(基準={base}で○だった候補)")
    for a in arms:
        if a == base or a == "PROD" or a not in ss:
            continue
        rt = retention(a, base, cases)
        P(f"- {a}: 脱落 {frac(len(rt['drop']), rt['tot'])} {[x[1] for x in rt['drop']][:10]} / 一般化維持 {frac(rt['gen_keep'], rt['gen_tot'])} 失った一般化 {rt['lost_gen'][:8]}")
    P("\n## 費用(円/レベル。台帳のcache原価を含む『全課金した場合』の見積。1記事セット=2レベル)")
    for a, s in ss.items():
        if s["costs"]:
            m = sum(s["costs"]) / len(s["costs"])
            P(f"- {a}: 平均¥{m:.2f}/レベル → 約¥{2 * m:.2f}/記事セット(70円比 {200 * m / 70:.1f}%) ({len(s['costs'])}レベル)")
    return ss


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="ALL14"); ap.add_argument("--arms", default="PROD,D,E1L,E4,N1a,N1,N2,N4,N4d"); ap.add_argument("--base", default="E1L")
    a = ap.parse_args()
    cases = {"ALL14": R.ALL14, "HELDOUT": R.HELDOUT, "HARD6": R.HARD6}.get(a.cases) or a.cases.split(",")
    report(a.arms.split(","), cases, a.base)
