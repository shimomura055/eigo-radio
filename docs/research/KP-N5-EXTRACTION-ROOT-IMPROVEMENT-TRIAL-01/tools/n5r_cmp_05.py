"""Trial専用(API 0・LLM呼出なし)。委任_05: 現行N5 cap7 とA案(E2+A10 cap10)の記事別比較データ(ev05/comparison_05.json)と比較表fragment(ev05/tables_05.md、freq_05.md)を生成する。
GEN5/VER5/CHK5の結果は fixture trial_items(Trial03 N5正式出力) / ev05/gen_cache_05_*.json(今回実行) / ev02/gen_cache_*.json(委任_02)のみを使い、手作業の一般形は使わない。
注意: Windowsでは必ず PYTHONUTF8=1 で実行する。"""
import sys, os, json, glob, itertools, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n5r_lib_02 as L
n5 = L.n5
EV2 = os.path.join(L.TD, "ev02"); EV5 = os.path.join(L.TD, "ev05")
fx = L.fixture()
CASES = [("untidi_a2", "Family X untidiness_family_resource(Std)"), ("untidi_b1b", "Family X untidiness_family_resource(Adv)"),
         ("melos_a2", "Family Z 走れメロス(Std)"), ("moon_b1b", "Family X moon_shrinking(Adv)"), ("surname_b1b", "Family Y surname_choice(Adv)")]

# 担当者(Sonnet)の暫定評価(主観。基準: 高=非自明な意味・用法を持つ汎用表現で一般形が自然かつ意味が正確 / 中=有用だが基礎的・場面限定・一般形が弱い /
# 低=基礎語の自由な組合せ、一般形が過度に一般的、記事固有)。ユーザー判断の材料であり判定ではない。
RATING = {
    "hear someone out": "高", "get heated": "高", "put something away": "高", "not so fast": "高", "in someone's place": "高", "take offense": "高", "let go of": "高",
    "hold someone back": "高", "can't help thinking": "高", "in the way": "高",
    "take something away from": "中", "make something work": "中", "turn something into": "中", "turn into": "中", "rely on": "中", "in session": "中", "speak for": "中",
    "something in the way": "中", "in sight": "中", "leave something out": "中", "take something seriously": "中", "take points away": "中", "need another look": "中", "in a way": "中",
    "take up space": "中", "apply something to": "中", "give someone a chance": "中", "leave for": "中", "pull someone under": "中", "lose one's trust in": "中", "win trust": "中",
    "lose one's life": "中", "rise above something": "中", "keep one's eye on": "中", "offer clues to": "中", "work out": "中", "work out how much": "中", "way off": "中", "up close": "中",
    "keep something from escaping": "中", "a record of": "中", "on the other hand": "中", "take measurements": "中", "shoving match": "中", "at ease": "中", "give something up": "中",
    "only natural": "中", "keep something in sight": "中", "as a result": "中", "lead to": "中", "spoil the look": "中", "without question": "中", "far from": "中",
    "end up taking points away": "低", "come from": "低", "look at": "低", "ask for": "低", "come back": "低", "stand up": "低", "put something on": "低", "hold on": "低", "care about": "低",
    "move away": "低", "have no problem": "低", "no problem at all": "低", "walking stick": "低", "keep something in": "低", "step back": "低", "put something down": "低", "miss something": "低",
    "miss dose": "低", "live together": "低", "help with": "低", "another way to look at": "低",
    "take one's job seriously": "中", "stop people from missing doses": "低", "no wonder": "中", "do one's job": "中", "on the job": "中", "dismiss something without question": "中",
    "without asking for": "低", "for once": "中", "too soon to say": "中", "than meets the eye": "高", "in other words": "中", "for now": "中", "again and again": "中",
}


def rate(df):
    return RATING.get((df or "").lower(), "—")


def J(p):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def ov(a, b):
    return L.norm_key(a) == L.norm_key(b) or n5._contains(a, b) or n5._contains(b, a)


def gen_of(case, span):
    """優先: fixture trial_items(現行N5正式出力) > ev05 cache > ev02 cache。未処理=None。"""
    k = L.norm_key(span)
    for x in fx["cases"][case]["trial_items"]:
        if L.norm_key(x["source_span"]) == k:
            ck = x.get("check") or {}
            return {"outcome": "kept", "display_form": x["display_form"], "gloss_ja": x["gloss_ja"], "relation": ck.get("relation"), "verify": (x.get("verify") or {}).get("verdict"),
                    "reverted": bool(x.get("reverted")), "source": "fixture_trial03_N5"}
    c5 = J(f"{EV5}/gen_cache_05_{case}.json"); c2 = J(f"{EV2}/gen_cache_{case}.json")
    if k in c5:
        return dict(c5[k], source=c5[k].get("source", "ev05_run"))
    if k in c2:
        return dict(c2[k], source="ev02_gen_cache")
    return None


def ident(case, span):
    g = gen_of(case, span)
    return ("df:" + g["display_form"].lower()) if g and g["outcome"] == "kept" else ("sp:" + L.norm_key(span))


def drop_reason(g):
    if not g:
        return "GEN未処理"
    if g["outcome"] == "dropped":
        return f"{g.get('drop_stage')}: {'; '.join(g.get('reasons') or [])[:120]}"
    probs = []
    if g.get("cmu"):
        probs.append("CMU:" + ";".join(g["cmu"])[:60])
    if g.get("words_ok") is False:
        probs.append("5語超")
    return " / ".join(probs)


def usable(g):
    return bool(g) and g["outcome"] == "kept" and not g.get("cmu") and g.get("words_ok", True)


def jac(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 1.0


out = {}
md = []
for case, title in CASES:
    text = fx["cases"][case]["text"]
    reps = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(f"{EV2}/rep_{case}_*.json"), key=lambda f: int(f.split("_")[-1].split(".")[0]))]
    cur = fx["cases"][case]["trial_items"]
    A_by_rep = {r["rep"]: L.pick_A10(r["pools"]["E2"]["judged"], text, 10) for r in reps}
    A0_by_rep = {r["rep"]: r["picks"]["A0"] for r in reps}
    ids = {rp: [ident(case, c["span"]) for c in lst] for rp, lst in A_by_rep.items()}
    score = {rp: (sum(jac(ids[rp], ids[q]) for q in ids if q != rp) / max(1, len(ids) - 1)) for rp in ids}
    rep_sel = sorted(ids, key=lambda rp: (-score[rp], rp))[0]
    freq = {}
    for rp, lst in A_by_rep.items():
        seen = set()
        for c in lst:
            i = ident(case, c["span"])
            if i in seen:
                continue
            seen.add(i)
            d = freq.setdefault(i, {"n": 0, "spans": {}, "reps": []})
            d["n"] += 1; d["reps"].append(rp); d["spans"][c["span"]] = d["spans"].get(c["span"], 0) + 1
    pairs = [len(set(ids[a]) & set(ids[b])) for a, b in itertools.combinations(sorted(ids), 2)]
    paired = []
    for rp in A_by_rep:
        a0 = [ident(case, c["span"]) for c in A0_by_rep[rp]]
        paired.append({"rep": rp, "n_a0": len(a0), "a0_in_a10": sum(1 for i in a0 if i in ids[rp])})
    Arows = []
    for rank, c in enumerate(A_by_rep[rep_sel], 1):
        g = gen_of(case, c["span"])
        Arows.append({"rank": rank, "span": c["span"], "difficulty": c["difficulty"], "chunk_type": c["chunk_type"], "origin": c.get("n5_origin"), "gen": g, "usable": usable(g),
                      "drop": drop_reason(g), "freq": freq[ident(case, c["span"])]["n"]})
    Crows = [{"span": x["source_span"], "display_form": x["display_form"], "gloss_ja": x["gloss_ja"], "relation": (x.get("check") or {}).get("relation"), "difficulty": x.get("difficulty")} for x in cur]
    for a in Arows:
        a["match"] = None
        for ci, cr in enumerate(Crows):
            if ov(a["span"], cr["span"]) or (a["gen"] and a["gen"]["outcome"] == "kept" and a["gen"]["display_form"].lower() == cr["display_form"].lower()):
                a["match"] = ci
                break
        a["cls"] = ("共通" if a["match"] is not None else "追加") if a["usable"] else ("QA脱落(現行N5と共通のspan)" if a["match"] is not None else "QA脱落(追加候補)")
    matched = {a["match"] for a in Arows if a["match"] is not None}
    for ci, cr in enumerate(Crows):
        cr["cls"] = "共通(A案cap10にも入る)" if ci in matched else "脱落(A案cap10に入らない)"
    out[case] = {"title": title, "n_reps": len(reps), "rep_sel": rep_sel, "medoid_scores": score, "cur": Crows, "A": Arows,
                 "freq": {k: {"n": v["n"], "spans": v["spans"]} for k, v in sorted(freq.items(), key=lambda kv: -kv[1]["n"])},
                 "pair_common_mean": (sum(pairs) / len(pairs)) if pairs else None, "pair_common_min": min(pairs) if pairs else None, "pair_common_max": max(pairs) if pairs else None,
                 "paired_a0": paired, "A_by_rep": {rp: [c["span"] for c in lst] for rp, lst in A_by_rep.items()}}
json.dump(out, open(f"{EV5}/comparison_05.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

HDR = "| 区分 | 現行N5 cap7: source_span → display_form | 日本語の意味 | A案 cap10: source_span → display_form | 日本語の意味 | 価値(暫定) | cap10入り頻度 / SEL難易度・型 / CHK5 relation |\n|---|---|---|---|---|---|---|"
for case, title in CASES:
    d = out[case]
    md.append(f"### {case} — {title}(E2 {d['n_reps']}rep、代表rep={d['rep_sel']})\n")
    md.append(HDR)
    used = set()
    for a in d["A"]:
        ci = a["match"]
        cr = d["cur"][ci] if ci is not None else None
        if ci is not None:
            used.add(ci)
        g = a["gen"]
        left = f"`{cr['span']}` → `{cr['display_form']}`" if cr else "—"
        leftg = cr["gloss_ja"] if cr else "—"
        if g and g["outcome"] == "kept":
            right = f"`{a['span']}` → `{g['display_form']}`"
            if not usable(g):
                right += f" [{a['drop']}]"
        else:
            right = f"`{a['span']}` → (" + (a["drop"] if g else "未処理") + ")"
        rightg = g["gloss_ja"] if g and g["outcome"] == "kept" else "—"
        rt = rate(g["display_form"]) if g and g["outcome"] == "kept" else "—"
        rl = (rate(cr["display_form"]) + "→" if cr and rate(cr["display_form"]) != rt else "") + rt if cr else rt
        md.append(f"| {a['cls']} | {left} | {leftg} | {right} | {rightg} | {rl} | {a['freq']}/{d['n_reps']}rep、{a['difficulty']}、{a['chunk_type']}、{(g or {}).get('relation') or ''} |")
    for ci, cr in enumerate(d["cur"]):
        if ci in used:
            continue
        md.append(f"| {cr['cls']} | `{cr['span']}` → `{cr['display_form']}` | {cr['gloss_ja']} | — | — | {rate(cr['display_form'])} | 現行N5のみ({cr['difficulty']}) |")
    md.append("")
open(f"{EV5}/tables_05.md", "w", encoding="utf-8").write("\n".join(md))
for case, _ in CASES:
    d = out[case]
    print(case, "reps", d["n_reps"], "rep_sel", d["rep_sel"], "cur", len(d["cur"]), "A", len(d["A"]), "usable", sum(a["usable"] for a in d["A"]),
          "pair_common mean", round(d["pair_common_mean"], 2) if d["pair_common_mean"] is not None else None)

# ---- 評価分布(代表rep) と 頻度表 ----
fq = ["## 付録A: セル別 A案cap10の候補別出現頻度(全rep、display_form単位)\n"]
summ = []
for case, title in CASES:
    d = out[case]
    cnt_cur = collections.Counter(rate(c["display_form"]) for c in d["cur"])
    cnt_a = collections.Counter(rate(a["gen"]["display_form"]) if a["usable"] else "脱落" for a in d["A"])
    summ.append((case, dict(cnt_cur), dict(cnt_a)))
    fq.append(f"### {case} — {title}({d['n_reps']}rep)\n")
    fq.append("| 出現/rep | display_form(GEN5出力) | 代表source_span(出現数) | 日本語の意味 | relation | 価値(暫定) | 現行N5 |\n|---|---|---|---|---|---|---|")
    for k, f in d["freq"].items():
        sp = max(f["spans"], key=f["spans"].get)
        g = gen_of(case, sp)
        if g and g["outcome"] == "kept":
            df = g["display_form"]; gl = g["gloss_ja"]; rel = g.get("relation") or ""
        else:
            df = "(" + (drop_reason(g) if g else "未処理") + ")"; gl = "—"; rel = ""
        incur = "✓" if any(ov(sp, c["span"]) or (g and g["outcome"] == "kept" and g["display_form"].lower() == c["display_form"].lower()) for c in d["cur"]) else ""
        fq.append(f"| {f['n']}/{d['n_reps']} | `{df}` | " + ", ".join(f"`{x}`({n})" for x, n in sorted(f["spans"].items(), key=lambda kv: -kv[1])) + f" | {gl} | {rel} | {rate(df)} | {incur} |")
    fq.append("")
open(f"{EV5}/freq_05.md", "w", encoding="utf-8").write("\n".join(fq))
json.dump(summ, open(f"{EV5}/rating_summary_05.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for c, a, b in summ:
    print("rating", c, "cur", a, "A10", b)
