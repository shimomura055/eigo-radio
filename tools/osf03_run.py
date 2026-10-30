# ONE-STEP-FURTHER-CORNER-TRIAL-01 委任_03: Trial専用ランナー(Production非接触)。
# 使い方: OSF_PAID=1 py osf03_run.py <stage> [args]   stage: regress | extract <model> | gen | audit | final
import sys, os, json, re, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import osf03_lib as L
import osf03_prompts as P
OUT = L.OUT
AUD1, AUD2 = "gemini-4-argon", "gemini-3.1-pro-preview"   # 独立監査(生成=OpenAI系列とは別ベンダー)。AUD1=最新上位、AUD2=別世代の第2監査
CELLS = [f"{f}_{l}" for f in "yxz" for l in ("std", "adv")]
def jdump(o, name): json.dump(o, open(os.path.join(OUT, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
def jload(name): return json.load(open(os.path.join(OUT, name), encoding="utf-8"))
def fmt_items(items, keys):
    return "\n".join(json.dumps({k: it.get(k, "") for k in keys}, ensure_ascii=False) for it in items)
def _prev_primary(cell):
    O = L.g1.OUT
    def L2(n): return json.load(open(os.path.join(O, n + ".json"), encoding="utf-8"))
    items = L2(f"{cell}__v2__s1")["result"]["items"]
    if cell == "y_adv": return [L2("y_adv__v2__s2")["result"]["items"][0]]
    if cell in ("x_adv", "z_std"):
        fx = L2(f"{cell}__pointfix__s1")["after"]; key = fx["core_expression"]
        return [fx if key in i["core_expression"] else i for i in items]
    return items
# ---------------- 回帰セット ----------------
def regression_items():
    R = [
        dict(id="NG1", src="原文§4 NG①", expect="FAIL", base_expression="they can help me", base_meaning_ja="(その人たちは)私を助けてくれる", base_frame="they can help me", further_expression="These notes give me something to work with.", further_frame="These notes give me something to work with."),
        dict(id="NG2", src="原文§4 NG②", expect="FAIL", base_expression="think only about my own feelings", base_meaning_ja="自分の気持ちだけを考える", base_frame="think only about my own feelings", further_expression="I'm sad, but I don't want to make this about me.", further_frame="I'm sad, but I don't want to make this about me."),
        dict(id="NG3", src="原文§4 NG③", expect="FAIL", base_expression="I'm nervous.", base_meaning_ja="私は緊張している", base_frame="I'm nervous.", further_expression="I'm nervous, but I'm trying not to let it show.", further_frame="I'm nervous, but I'm trying not to let it show."),
        dict(id="NG4", src="原文§4 NG④", expect="FAIL", base_expression="I think she's upset because…", base_meaning_ja="彼女が動揺しているのは…だからだと思う", base_frame="I think she's upset because…", further_expression="I may be reading too much into her short reply, but…", further_frame="I may be reading too much into her short reply, but…"),
        dict(id="NG5", src="原文§4 NG⑤", expect="FAIL", base_expression="be upset", base_meaning_ja="動揺している、取り乱している", base_frame="She was upset.", further_expression="be distressed", further_frame="She was distressed."),
        dict(id="G1", src="原文§3 良例①", expect="PASS", base_expression="make some progress", base_meaning_ja="ある程度進展する", base_frame="We made some progress.", further_expression="make some headway", further_frame="We made some headway."),
        dict(id="G2", src="原文§3 良例②", expect="PASS_WITH_DIFF以上でdiff検出(無条件PASS不可)", base_expression="You should decide.", base_meaning_ja="あなたが決めるべきだ(助言)", base_frame="You should decide.", further_expression="It's your call to make.", further_frame="It's your call to make."),
        dict(id="G3", src="原文§3 良方向③", expect="PASS_WITH_DIFF以上でdiff検出(無条件PASS不可)", base_expression="I'll try this.", base_meaning_ja="これを試してみる", base_frame="I'll try this.", further_expression="I'll see where this takes me.", further_frame="I'll see where this takes me."),
    ]
    k = 0
    for cell in CELLS:
        for it in _prev_primary(cell):
            k += 1
            R.append(dict(id=f"P{k:02d}", src=f"前回主候補 {cell}", cell=cell, expect="(前回の判定。5類型NGを含むはず)", base_expression=it["basic_en"], base_meaning_ja=it["basic_ja"], base_frame=it["basic_en"], further_expression=it["core_expression"] + " | " + it["further_en"], further_frame=it["further_en"], prev_item=it))
    return R
AKEYS = ["id", "base_expression", "base_meaning_ja", "base_frame", "further_expression", "further_meaning_ja", "further_frame"]
def run_audit_A(items, existing, tag, model):
    pr = P.AUDIT_A.format(codes=P.DEFECT_CODES, existing=existing or "(none given)", items=fmt_items(items, AKEYS))
    text, c, el = L.call_gemini(model, pr, tag)
    return {r["id"]: r for r in L.parse(text)["results"]}, c, el
def run_audit_B(items, existing, level, tag, model):
    keys = ["id", "base_expression", "base_meaning_ja", "further_expression", "further_meaning_ja", "frame_base_en", "frame_further_en", "point_ja"]
    pr = P.AUDIT_B.format(existing=existing or "(none)", level=level, items=fmt_items(items, keys))
    text, c, el = L.call_gemini(model, pr, tag)
    return {r["id"]: r for r in L.parse(text)["results"]}, c, el
def regress(tagsuffix=""):
    R = regression_items(); ids = [r["id"] for r in R]
    for r in R: r.setdefault("further_meaning_ja", "")
    L.init_gemini()
    res = {"items": R, "A": {}, "mech": {}}
    for r in R: res["mech"][r["id"]] = L.check_candidate(r["base_frame"], r["further_frame"], r["base_expression"], r["further_expression"], [])
    out = {}; cost = 0
    def one(m):
        nonlocal cost
        a, c, el = run_audit_A(R, "", f"regress{tagsuffix}__A__{m}", m); out[m] = a; cost += c
    ths = [threading.Thread(target=one, args=(m,)) for m in (AUD1, AUD2)]
    [t.start() for t in ths]; [t.join() for t in ths]
    res["A"] = out; res["cost"] = round(cost, 3)
    jdump(res, f"regress{tagsuffix}__result.json")
    print("cost", res["cost"], "spent", round(L.spent(), 3))
    for r in R:
        i = r["id"]; v1 = out[AUD1].get(i, {}); v2 = out[AUD2].get(i, {})
        print(f"{i:4} mech={res['mech'][i]} | {AUD1.split('-')[1]}:{v1.get('v')}{v1.get('f')} dp={v1.get('dp')} {v1.get('diff')}{v1.get('why')} | {AUD2.split('-')[1]}:{v2.get('v')}{v2.get('f')} dp={v2.get('dp')} {v2.get('diff')}{v2.get('why')}")
if __name__ == "__main__":
    st = sys.argv[1]
    if st == "regress": regress(sys.argv[2] if len(sys.argv) > 2 else "")
    elif st == "show_regress":
        for r in regression_items(): print(r["id"], r["src"], "|", r["base_expression"], "->", r["further_expression"])

# ---------------- Step1 抽出 ----------------
_T = None
def inputs(cell):
    global _T
    if _T is None: _T = L.g1._load_nt().load_targets()
    return L.g1.inputs_for(cell, _T)
def existing_text(inp):
    kp = [e for e, _ in inp["kp"]]
    return "; ".join(f"{e}({gl})" if gl else e for e, gl in inp["kp"]), kp, inp["grammar"]
def extract(model, cells, n=8, effort=None, round_tag="", exclude=None):
    res = {}
    def one(cell):
        inp = inputs(cell); sents = L.numbered_sentences(inp["body"]); numbered = "\n".join(f"[{i}] {s}" for i, s in enumerate(sents))
        kp_txt, kp, gram = existing_text(inp)
        pr = P.EXTRACT.format(level=P.LEVEL_TXT[inp["lv"]], numbered=numbered, kp=kp_txt, grammar="; ".join(gram) or "(なし)", n=n)
        if exclude:
            ex = exclude.get(cell, [])
            pr = pr.replace("# 規則", "# 検討済みで除外する基本表現(これらと同じ核は選ばない。ほかの、置換価値のある基本表現を探す)" + chr(10) + "- " + "; ".join(ex) + chr(10) + chr(10) + "# 規則", 1)
        tg = f"extract{round_tag}__{cell}__{model}"; rawp = os.path.join(OUT, "raw", tg + ".txt")
        try:
            doc = L.parse(open(rawp, encoding="utf-8").read()); c = 0.0; el = 0.0   # 既に取得済みのraw(費用は初回に計上済み)を再利用
        except Exception:
            text, c, el = L.call_openai(model, pr, tg, max_out=12000, effort=effort)
            try: doc = L.parse(text)
            except Exception:
                text, c2, el2 = L.call_openai(model, pr, tg + "_retry", max_out=16000, effort=effort); c += c2; el += el2; doc = L.parse(text)
        kept = []; dropped = []
        for cd in doc["candidates"]:
            why = L.check_extraction(cd, inp["body"], kp, gram)
            (dropped if why else kept).append({**cd, "mech": why})
        res[cell] = {"model": model, "cost_jpy": c, "elapsed_sec": el, "kept": kept, "dropped": dropped, "n_sentences": len(sents)}
    ths = [threading.Thread(target=one, args=(c,)) for c in cells]; [t.start() for t in ths]; [t.join() for t in ths]
    for cell in cells:
        jdump(res[cell], f"extract{round_tag}__{cell}.json"); r = res[cell]
        print(cell, f"kept={len(r['kept'])} dropped={len(r['dropped'])} cost={r['cost_jpy']} {r['elapsed_sec']}s")
        for k in r["kept"]: print("   OK  ", k["prototype"], "<-", k["target_span"], "|", k["meaning_ja"], "| sid", k["sentence_id"])
        for k in r["dropped"]: print("   DROP", k["prototype"], "<-", k["target_span"], k["mech"])
    print("spent", round(L.spent(), 3))
if __name__ == "__main__" and sys.argv[1] == "extract":
    extract(sys.argv[2], sys.argv[3].split(","), effort=(sys.argv[4] if len(sys.argv) > 4 else None))
if __name__ == "__main__" and sys.argv[1] == "extract3":   # 第3ラウンド(sol・低推論)。第2ラウンドまでのkept/droppedを除外
    cells = sys.argv[2].split(",")
    def _all(c):
        o = []
        for t in ("", "_r2"):
            try: d = jload(f"extract{t}__{c}.json"); o += [b["prototype"] for b in d["kept"] + d["dropped"]]
            except Exception: pass
        return o
    extract("gpt-6.1-sol", cells, n=5, effort="low", round_tag="_r3", exclude={c: _all(c) for c in cells})
if __name__ == "__main__" and sys.argv[1] == "extract2":
    cells = sys.argv[2].split(","); exc = {c: [b["prototype"] for b in jload(f"extract__{c}.json")["kept"] + jload(f"extract__{c}.json")["dropped"]] for c in cells}
    extract("gpt-6-luna", cells, n=10, round_tag="_r2", exclude=exc)

# ---------------- Step2 生成(記事全文・Storyline・人物心理は渡さない) ----------------
GEN_MODEL = "gpt-6.1-sol"
def gen_family(f, k=2, effort=None, model=GEN_MODEL):
    items = []; base_by_id = {}
    for lv in ("std", "adv"):
        cell = f"{f}_{lv}"; ex = jload(f"extract__{cell}.json")
        for i, b in enumerate(ex["kept"]):
            bid = f"{cell}:{i}"; items.append({"id": bid, "level": lv, "prototype": b["prototype"], "meaning_ja": b["meaning_ja"], "must_preserve": b.get("must_preserve", [])})
            base_by_id[bid] = b
    pr = P.GEN.format(criteria=P.GEN_CRITERIA, std=P.LEVEL_TXT["std"], adv=P.LEVEL_TXT["adv"], items="\n".join(json.dumps(x, ensure_ascii=False) for x in items), k=k)
    text, c, el = L.call_openai(model, pr, f"gen__{f}__{model}", max_out=16000, effort=effort)
    doc = L.parse(text)
    # 機械検査
    cells = {}
    for lv in ("std", "adv"):
        cell = f"{f}_{lv}"; inp = inputs(cell); cells[cell] = [e for e, _ in inp["kp"]]
    out = []
    for r in doc["results"]:
        bid = r["id"]; cell = bid.split(":")[0]; b = base_by_id.get(bid)
        if not b: continue
        for rank, cd in enumerate(r.get("candidates", []), 1):
            mech = L.check_candidate(cd.get("frame_base_en", ""), cd.get("frame_further_en", ""), b["prototype"], cd["further_expression"], cells[cell])
            out.append({"cid": f"{bid}#{rank}", "base_id": bid, "cell": cell, "base": b, "rank": rank, **cd, "mech": mech})
    jdump({"model": model, "cost_jpy": c, "elapsed_sec": el, "candidates": out, "n_bases": len(items)}, f"gen__{f}.json")
    n_ok = sum(1 for o in out if not [m for m in o["mech"] if not m.startswith("FLAG")])
    print(f, "bases", len(items), "cands", len(out), "mech_ok", n_ok, "cost", c, f"{el}s", "spent", round(L.spent(), 3))
    for o in out: print("  ", o["cid"], "|", o["base"]["prototype"], "->", o["further_expression"], "|", o["frame_base_en"], "=>", o["frame_further_en"], "|", o["mech"])
if __name__ == "__main__" and sys.argv[1] == "gen":
    gen_family(sys.argv[2], effort=(sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None))

# ---------------- Step3 Gate A(argon=決定、別ベンダー) ----------------
def a_items(cands):
    return [{"id": c["cid"], "level": c["cell"].split("_")[1], "base_expression": c["base"]["prototype"], "base_meaning_ja": c["base"]["meaning_ja"], "base_frame": c["frame_base_en"], "further_expression": c["further_expression"], "further_meaning_ja": c["further_meaning_ja"], "further_frame": c["frame_further_en"], "must_preserve": c["base"].get("must_preserve", [])} for c in cands]
def existing_family(f):
    parts = []
    for lv in ("std", "adv"):
        kp_txt, kp, gram = existing_text(inputs(f"{f}_{lv}")); parts.append(f"[{lv}] KP/Word: {kp_txt}; 文法: {'; '.join(gram) or '(なし)'}")
    return " / ".join(parts)
def gate_a(f, model=AUD1, tag="A", only=None):
    g = jload(f"gen__{f}.json"); cands = [c for c in g["candidates"] if not [m for m in c["mech"] if not m.startswith("FLAG")]]
    if only: cands = [c for c in cands if c["cid"] in only]
    if not cands: print(f, "no candidates"); return
    L.init_gemini()
    pr = P.AUDIT_A.format(codes=P.DEFECT_CODES, existing=existing_family(f), items=fmt_items(a_items(cands), ["id", "level", "base_expression", "base_meaning_ja", "base_frame", "further_expression", "further_meaning_ja", "further_frame", "must_preserve"]))
    text, c, el = L.call_gemini(model, pr, f"gateA__{f}__{tag}__{model}")
    res = {r["id"]: r for r in L.parse(text)["results"]}
    jdump({"model": model, "cost_jpy": c, "elapsed_sec": el, "results": res}, f"gateA__{f}__{tag}.json")
    print(f, "cost", c, f"{el}s", "spent", round(L.spent(), 3))
    for cd in cands:
        r = res.get(cd["cid"], {}); print("  ", cd["cid"], cd["base"]["prototype"], "->", cd["further_expression"], "|", r.get("v"), r.get("f"), "dp=", r.get("dp"), r.get("diff"), r.get("why"))
if __name__ == "__main__" and sys.argv[1] == "gateA":
    ths = [threading.Thread(target=gate_a, args=(f,)) for f in sys.argv[2].split(",")]; [t.start() for t in ths]; [t.join() for t in ths]

# ---------------- Step4 Gate B(Gate A通過のみ) ----------------
def gate_b(f, model=AUD1, tag="A", btag="B"):
    g = jload(f"gen__{f}.json"); byid = {c["cid"]: c for c in g["candidates"]}
    ga = jload(f"gateA__{f}__{tag}.json")["results"]
    pas = [byid[i] for i, r in ga.items() if r.get("v") in ("PASS", "PASS_WITH_DIFF") and i in byid]
    if not pas: print(f, "no passers"); return
    L.init_gemini()
    items = [{"id": c["cid"], "level": c["cell"].split("_")[1], "base_expression": c["base"]["prototype"], "further_expression": c["further_expression"], "further_meaning_ja": c["further_meaning_ja"], "frame_base_en": c["frame_base_en"], "frame_further_en": c["frame_further_en"], "point_ja": c.get("point_ja", "")} for c in pas]
    pr = P.AUDIT_B.format(existing=existing_family(f), level="Standard=A2〜B1の日本語話者 / Advanced=B1〜B2の日本語話者(itemのlevelに従う)", items=fmt_items(items, list(items[0].keys())))
    text, c, el = L.call_gemini(model, pr, f"gateB__{f}__{btag}__{model}")
    res = {r["id"]: r for r in L.parse(text)["results"]}
    jdump({"model": model, "cost_jpy": c, "elapsed_sec": el, "results": res}, f"gateB__{f}__{btag}.json")
    print(f, "cost", c, f"{el}s", "spent", round(L.spent(), 3))
    for cd in pas:
        r = res.get(cd["cid"], {}); print("  ", cd["cid"], cd["further_expression"], "| d,w,b,l,c =", [r.get(k) for k in "dwblc"], r.get("bf"), "|+", r.get("st"), "|-", r.get("wk"))
if __name__ == "__main__" and sys.argv[1] == "gateB":
    ths = [threading.Thread(target=gate_b, args=(f,)) for f in sys.argv[2].split(",")]; [t.start() for t in ths]; [t.join() for t in ths]


def gen_r3(cells=("x_std", "x_adv", "y_adv"), k=2, effort="low", model=GEN_MODEL):
    items = []; base_by_id = {}
    for cell in cells:
        ex = jload(f"extract_r3__{cell}.json"); lv = cell.split("_")[1]
        for i, b in enumerate(ex["kept"]):
            bid = f"{cell}:r3_{i}"; items.append({"id": bid, "level": lv, "prototype": b["prototype"], "meaning_ja": b["meaning_ja"], "must_preserve": b.get("must_preserve", [])}); base_by_id[bid] = b
    pr = P.GEN.format(criteria=P.GEN_CRITERIA, std=P.LEVEL_TXT["std"], adv=P.LEVEL_TXT["adv"], items=chr(10).join(json.dumps(x, ensure_ascii=False) for x in items), k=k)
    text, c, el = L.call_openai(model, pr, f"gen_r3__{model}", max_out=10000, effort=effort)
    doc = L.parse(text); out = []
    kps = {cell: [e for e, _ in inputs(cell)["kp"]] for cell in cells}
    for r in doc["results"]:
        bid = r["id"]; b = base_by_id.get(bid); cell = bid.split(":")[0]
        if not b: continue
        for rank, cd in enumerate(r.get("candidates", []), 1):
            mech = L.check_candidate(cd.get("frame_base_en", ""), cd.get("frame_further_en", ""), b["prototype"], cd["further_expression"], kps[cell])
            out.append({"cid": f"{bid}#{rank}", "base_id": bid, "cell": cell, "base": b, "rank": rank, **cd, "mech": mech})
    jdump({"model": model, "cost_jpy": c, "elapsed_sec": el, "candidates": out, "n_bases": len(items)}, "gen_r3.json")
    print("r3 bases", len(items), "cands", len(out), "cost", c, f"{el}s", "spent", round(L.spent(), 3))
    for o in out: print("  ", o["cid"], "|", o["base"]["prototype"], "->", o["further_expression"], "|", o["frame_base_en"], "=>", o["frame_further_en"], "|", o["mech"])
if __name__ == "__main__" and sys.argv[1] == "gen_r3": gen_r3()

# ---------------- 最終: 本文参照の用法整合確認 + (第3ラウンド分は)Gate B ----------------
def b_ok(r): return all((r.get(k) or 0) >= 4 for k in "dwlc") and (r.get("b") or 0) >= 3 and not r.get("bf")
def round1_finalists(per_cell=2):
    out = []
    for f in "yxz":
        g = jload(f"gen__{f}.json"); byid = {c["cid"]: c for c in g["candidates"]}
        ga = jload(f"gateA__{f}__A.json")["results"]; gb = jload(f"gateB__{f}__B.json")["results"]
        ok = [(sum(gb[i].get(k) or 0 for k in "dwblc"), i) for i, r in ga.items() if r.get("v") in ("PASS", "PASS_WITH_DIFF") and i in gb and b_ok(gb[i])]
        by_cell = {}
        for sc, i in sorted(ok, reverse=True): by_cell.setdefault(byid[i]["cell"], []).append(i)
        for cell, ids in by_cell.items():
            for i in ids[:per_cell]: out.append((byid[i], False))
    return out
def final_items(cands_needB):
    items = []
    for c, needB in cands_needB:
        b = c["base"]; items.append({"id": c["cid"], "cell": c["cell"], "quote": b["quote"], "target_span": b["target_span"], "prototype": b["prototype"], "meaning_ja": b["meaning_ja"], "must_preserve": b.get("must_preserve", []), "further_expression": c["further_expression"], "further_meaning_ja": c["further_meaning_ja"], "frame_base_en": c["frame_base_en"], "frame_further_en": c["frame_further_en"], "point_ja": c.get("point_ja", ""), "needB": needB})
    return items
def final_stage(model=AUD1, dry=False):
    cl = round1_finalists(); r3 = jload("gen_r3.json")["candidates"]
    seen_protos = {c2["base"]["prototype"] for c2, _ in cl}   # 同一基本表現(別cellで既に第1ラウンド検討済み)の再検査は費用節約のため省く(x_adv: all by oneself はx_stdで検討済み)
    prev_bases = set()
    for f in "yxz":
        for c2 in jload(f"gen__{f}.json")["candidates"]: prev_bases.add(c2["base"]["prototype"])
    cl += [(c, True) for c in r3 if not [m for m in c["mech"] if not m.startswith("FLAG")] and c["base"]["prototype"] not in prev_bases]
    items = final_items(cl)
    arts = []; ex = []
    for cell in CELLS:
        inp = inputs(cell); arts.append(f"[{cell}] {P.LEVEL_TXT[inp['lv']].split('(')[0]}" + chr(10) + inp["body"]); kp_txt, kp, gram = existing_text(inp); ex.append(f"[{cell}] KP/Word: {kp_txt}; 文法: {'; '.join(gram) or '(なし)'}")
    pr = P.FINAL.format(articles=(chr(10) * 2).join(arts), existing=chr(10).join(ex), codes=P.DEFECT_CODES, items=chr(10).join(json.dumps(x, ensure_ascii=False) for x in items))
    print("final items", len(items), "prompt chars", len(pr))
    if dry:
        for x in items: print("  ", x["id"], x["prototype"], "->", x["further_expression"], "| needB", x["needB"])
        return
    L.init_gemini()
    text, c, el = L.call_gemini(model, pr, f"final__{model}")
    res = {r["id"]: r for r in L.parse(text)["results"]}
    jdump({"model": model, "cost_jpy": c, "elapsed_sec": el, "items": items, "results": res}, "final.json")
    print("cost", c, f"{el}s", "spent", round(L.spent(), 3))
    for x in items:
        r = res.get(x["id"], {}); print("  ", x["id"], x["further_expression"], "|", r.get("v"), r.get("f"), "ex/pr/mn/sn/sm", [r.get(k) for k in ("ex", "pr", "mn", "sn", "sm")], "|", r.get("diff"), r.get("why"), "| B", [r.get(k) for k in "dwblc"], r.get("bf"), r.get("wk"))
        print("       sub:", r.get("sub"))
if __name__ == "__main__" and sys.argv[1] == "final": final_stage(dry=(len(sys.argv) > 2 and sys.argv[2] == "dry"))

# ---------------- 最終選定(決定規則: Gate A通過 かつ 本文参照の最終確認PASS かつ Gate B閾値(d,w,l,c>=4, b>=3, 旗なし)。同点はB合計順。各cell最大2) ----------------
def select():
    fin = jload("final.json"); res = fin["results"]; items = {x["id"]: x for x in fin["items"]}
    gens = {}
    for f in "yxz":
        for c in jload(f"gen__{f}.json")["candidates"]: gens[c["cid"]] = c
    for c in jload("gen_r3.json")["candidates"]: gens[c["cid"]] = c
    gb = {}
    for f in "yxz": gb.update(jload(f"gateB__{f}__B.json")["results"])
    ga = {}
    for f in "yxz": ga.update(jload(f"gateA__{f}__A.json")["results"])
    rows = []
    for cid, x in items.items():
        r = res[cid]; c = gens[cid]; r3 = ":r3_" in cid
        bsc = r if r3 else gb.get(cid, {})
        a_ok = True if r3 else ga.get(cid, {}).get("v") in ("PASS", "PASS_WITH_DIFF")
        f_ok = r.get("v") == "PASS"; b_pass = b_ok(bsc)
        rows.append({"cid": cid, "cell": c["cell"], "round": 3 if r3 else 1, "gateA": ("final-with-article(frame-A skipped)" if r3 else ga.get(cid, {}).get("v")), "final": r.get("v"), "B": [bsc.get(k) for k in "dwblc"], "bf": bsc.get("bf"), "wk": bsc.get("wk"), "pass_all": bool(a_ok and f_ok and b_pass), "sum": sum((bsc.get(k) or 0) for k in "dwblc")})
    sel = {}
    for cell in CELLS:
        el = sorted([r for r in rows if r["cell"] == cell and r["pass_all"]], key=lambda r: -r["sum"])[:2]
        sel[cell] = [e["cid"] for e in el]
    jdump({"rows": rows, "selected": sel}, "select.json")
    for cell in CELLS: print(cell, sel[cell])
    return sel
if __name__ == "__main__" and sys.argv[1] == "select": select()
