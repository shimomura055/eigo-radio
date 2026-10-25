# FAMILY-Z-STUDY-TEXT-TRIAL-01 Trial-08専用script(DEV。Production非参照)。run_trial_07.pyを基盤に、倒置(INV)の選定順位だけを下げる。
# Tier1=INV以外の適格候補 / Tier2=適格なINV / Tier3=0件。適格条件(eligible7)・Tier内順位(_order_key)・最大1件はTrial-07と同一。倒置は一律除外しない。
# 再抽出(Step A8)はTrial-07と同一モデル・同一Promptで、INV・CLEFT・CMPの再確認指示1文だけを差し替える(比較条件の同一性)。
#   py run_trial_08.py reselect         # API 0: Trial-07の既存Step A''データへ新順位を適用 -> reselect_08.json
#   py run_trial_08.py dry-run | selftest   # API 0
#   .venv\Scripts\python.exe run_trial_08.py send-a   # 有料(再抽出。TRIAL08_PAID_APPROVED=1 必須)
import sys, os, json, re, hashlib, time, glob, threading
BASE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(BASE, "..", "..", ".."))
sys.path.insert(0, BASE)
import run_trial_04 as t4
import run_trial_07 as t7
from run_trial_06 import Budget, Refused, hard_cost_jpy

WORKS8 = list(t7.WORKS7)                                   # Trial-07と同じ8作品・同じ本文
REEXTRACT = {"gift": 3, "paw": 2, "tth": 2, "promise": 2, "melos": 2}   # 再抽出する作品とN(Trial-07のNに合わせる。理由=DESIGN_08 §3)
OLD_LINE = "特にINV・CLEFT・CMPの3つは、全段落で見落としがないか最後にもう一度確認する。"
NEW_LINE = "特にINV以外の分類(CLEFT・CMP・FRONT・HEAVY・POSTMOD・SPEC・ELL・APPOS)について、全段落で見落としがないか最後にもう一度確認する。"
assert t7.STEPA7.count(OLD_LINE) == 1
STEPA8 = t7.STEPA7.replace(OLD_LINE, NEW_LINE)
def stepa8_prompt(d): return STEPA8.format(label=d["label"], n=len(d["body"]), numbered=d["numbered"])

# ---------- 決定論規則: 倒置を下げた1件選定 ----------
def is_inv(f): return t7._cls(f) == "INV"
def select_tiered(feats):
    """Tier1=INV以外の適格(Trial-07のeligible7と同一条件)をTrial-07の順位で並べる。Tier1が空のときだけTier2=適格なINV。両方空なら0件。
    倒置は除外しない(Tier2として残る)。最大1件。"""
    el = [f for f in feats if t7.eligible7(f)]
    t1 = sorted([f for f in el if not is_inv(f)], key=t7._order_key)
    t2 = sorted([f for f in el if is_inv(f)], key=t7._order_key)
    return (t1 + t2)[:1], ("T1" if t1 else ("T2" if t2 else "T3"))
def rec8(f, tier):
    r = t7.sel_record(f); r["tier"] = tier; return r
def tier_table(feats):
    """全featureについて Tier1/Tier2適格か・不適格理由を記録(見落とし・倒置残存の監査用)"""
    out = []
    for f in feats:
        c = t7._cls(f); why = []
        if not f.get("resolve_ok"): why.append("resolve_fail")
        if f.get("basic_only") in (True, "true", "True"): why.append("basic_only")
        if not t7.materials_ok(f): why.append("no_materials")
        if not t7.teaching_ok(f): why.append("TV=" + str(f.get("teaching_value")))
        if c in t7.MID and not t7.mid_cond(f): why.append("mid_cond")
        if c == "FRONT" and not t7.front_ok(f): why.append("front_kind=" + str(f.get("front_kind")))
        if c == "ELL" and not str(f.get("omitted_words", "")).strip(): why.append("ELL_no_omitted")
        if c not in t7.PRIORITY: why.append("class=" + c)
        elig = t7.eligible7(f)
        out.append(dict(para=f.get("para"), cls=c, tier=(("T2" if is_inv(f) else "T1") if elig else None), eligible=elig, why_not=([] if elig else why),
                        tv=f.get("teaching_value"), tv_ja=f.get("teaching_value_ja"), front_kind=f.get("front_kind"), sentence=f.get("sentence"),
                        single_span_ok=f.get("single_span_ok"), cross_para_flag=f.get("cross_para_flag")))
    return out
def sel_to_stepa8(feats):
    fs, tier = select_tiered(feats)
    return dict(selected=[x for x in (t7.to_selected(f) for f in fs) if x], records=[rec8(f, tier) for f in fs], tier=tier)

# ---------- API 0: Trial-07データへの再適用 ----------
def load07(w):
    return [json.load(open(os.path.join(BASE, f"OUTPUT_07_{w}_r{i}_STEPA_DEV.json"), encoding="utf-8")) for i in range(1, t7.NSAMP7[w] + 1)]
def reselect():
    out = {}
    for w in WORKS8:
        rows = []
        for i, j in enumerate(load07(w), 1):
            F = j["features"]; old = t7.select_one(F); new, tier = select_tiered(F)
            rows.append(dict(run=f"r{i}", old=[t7.sel_record(f) for f in old], new=[rec8(f, tier) for f in new], tier=tier, table=tier_table(F),
                             changed=([(f['para'], t7._cls(f)) for f in old] != [(f['para'], t7._cls(f)) for f in new])))
        out[w] = rows
    json.dump(out, open(os.path.join(BASE, "reselect_08.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out

# ---------- 有料: 再抽出(Step A8) ----------
MAXOUT_A = t7.MAXOUT_A; CAP_A8 = 11.0
def usage_spent8(): return sum(json.load(open(p, encoding="utf-8"))["cost_jpy_at_160"] for p in glob.glob(os.path.join(BASE, "usage_08_*.json")))
_ERR = {"n": 0}; _ERR_LOCK = threading.Lock()
def make_real_llm(budget, maxout_for):
    def real_llm(prompt, tag):
        assert os.environ.get("TRIAL08_PAID_APPROVED") == "1", "paid call refused"
        maxout = maxout_for(tag); hard = hard_cost_jpy(prompt, maxout)
        budget.acquire(hard, tag); actual = 0.0
        try:
            from dotenv import load_dotenv; load_dotenv(os.path.join(ROOT, ".env"))
            from openai import OpenAI
            c = OpenAI(); t0 = time.time()
            r = c.responses.create(model="gpt-6-luna", input=[{"role": "user", "content": prompt}], max_output_tokens=maxout)
            el = time.time() - t0; u = r.usage
            cached = getattr(u.input_tokens_details, "cached_tokens", 0)
            usd = (u.input_tokens - cached) * 0.10 / 1e6 + cached * 0.01 / 1e6 + u.output_tokens * 0.50 / 1e6
            actual = usd * 160
            d = {"tag": tag, "model_requested": "gpt-6-luna", "model_actual": r.model, "response_id": r.id, "status": getattr(r, "status", None), "elapsed_sec": round(el, 1),
                 "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(), "input_tokens": u.input_tokens, "cached_input_tokens": cached,
                 "output_tokens": u.output_tokens, "reasoning_tokens": getattr(u.output_tokens_details, "reasoning_tokens", None),
                 "max_output_tokens": maxout, "hard_reserved_jpy": round(hard, 4), "cost_usd": round(usd, 6), "cost_jpy_at_160": round(actual, 4)}
            json.dump(d, open(os.path.join(BASE, f"usage_08_{tag}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            open(os.path.join(BASE, f"_raw_08_{tag}.txt"), "w", encoding="utf-8", newline="\n").write(r.output_text or "")
            return r.output_text, d
        except Refused: raise
        except Exception:
            with _ERR_LOCK:
                _ERR["n"] += 1
                if _ERR["n"] >= 2: budget.abort()
            raise
        finally: budget.release(hard, actual, tag)
    return real_llm
def run_stepa8(work, runid, llm):
    d = t7.work_data7(work); tag = f"08_{runid}_stepA8_{work}"
    r = llm(stepa8_prompt(d), tag)
    path = os.path.join(BASE, f"OUTPUT_08_{work}_{runid}_STEPA_DEV.json")
    try: j = t7.parse_stepa7(r[0], d, None)
    except Exception as e: j = dict(parse_error=repr(e)[:300], raw_file=f"_raw_{tag}.txt", features=[], no_feature_paras=[], uncovered_paras=[])
    j["rule_selected"] = sel_to_stepa8(j["features"]); j["tier_table"] = tier_table(j["features"]); j["usage"] = r[1]
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(j, ensure_ascii=False, indent=1))
    return j
def batch_a8(llm):
    from concurrent.futures import ThreadPoolExecutor
    jobs = [(w, f"r{i}") for w, n in REEXTRACT.items() for i in range(1, n + 1)]; errs = {}
    def one(w, r):
        try: run_stepa8(w, r, llm)
        except Exception as e: errs[f"{w}_{r}"] = repr(e)[:300]
    with ThreadPoolExecutor(max_workers=len(jobs)) as ex: list(ex.map(lambda x: one(*x), jobs))
    return errs

def dry_run():
    out = {}
    for w in WORKS8:
        d = t7.work_data7(w); p = stepa8_prompt(d); n = REEXTRACT.get(w, 0)
        if n: open(os.path.join(BASE, f"_prompt_08_{w}_stepA8.txt"), "w", encoding="utf-8", newline="\n").write(p)
        out[w] = dict(n=n, prompt_chars=len(p), hard_jpy=round(hard_cost_jpy(p, MAXOUT_A), 3), sha=hashlib.sha256(p.encode()).hexdigest()[:12])
    out["n_calls"] = sum(REEXTRACT.values())
    out["worst_case_all_jpy"] = round(sum(v["hard_jpy"] * v["n"] for v in out.values() if isinstance(v, dict)), 2)
    json.dump(out, open(os.path.join(BASE, "dryrun_08.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out

def selftest():
    # Prompt差分は再確認指示1文のみ(Trial-07と同一Prompt)
    d = t7.work_data7("gift"); p7 = t7.stepa7_prompt(d); p8 = stepa8_prompt(d)
    assert p7.replace(OLD_LINE, NEW_LINE) == p8 and OLD_LINE in p7 and OLD_LINE not in p8 and NEW_LINE in p8
    t7.leak_check()                                  # 日本語のみの差し替えで例文が本文へ漏れない(Trial-07と同じassert)
    for w in WORKS8: assert NEW_LINE in t7._head(stepa8_prompt(t7.work_data7(w)))
    # 規則: 倒置は一律除外しない。Tier1(非INV適格)があればINVより優先、無ければINV、どちらも無ければ0件
    g = t7.work_data7("gift")
    def mk(*fs): return t7._parse(g, list(fs))
    inv = t7._mf(g, "P22", "INV", si=0, mq="Inside were")
    pm = t7._mf(g, "P4", "POSTMOD", si=1, mq="handed down")
    s, t = select_tiered(mk(inv)["features"]); assert [f["para"] for f in s] == ["P22"] and t == "T2"            # INVのみ -> 倒置が残る(一律除外ではない)
    s, t = select_tiered(mk(pm)["features"]); assert [f["para"] for f in s] == ["P4"] and t == "T1"
    both = mk(inv, pm)["features"]
    s, t = select_tiered(both); assert [f["para"] for f in s] == ["P4"] and t == "T1"                              # 旧規則ならINV(P22)が先頭
    assert [f["para"] for f in t7.select_one(both)] == ["P22"]                                                     # Trial-07規則との差(=優先順位だけ)
    s, t = select_tiered(mk(t7._mf(g, "P22", "INV", si=0, mq="Inside were", tv="LOW"))["features"]); assert s == [] and t == "T3"   # 単純な倒置(TV=LOW)は無理に選ばない
    s, t = select_tiered(mk(inv, t7._mf(g, "P4", "POSTMOD", si=1, mq="handed down", tv="LOW"))["features"]); assert [f["para"] for f in s] == ["P22"] and t == "T2"   # Tier1がLOW -> INVが残る
    assert select_tiered(mk(t7._mf(g, "P22", "INV", si=0, mq="Inside were", basic=True))["features"])[0] == []
    assert select_tiered([])[1] == "T3"
    # Tier内順位はTrial-07と同一(強クラス > 中クラス、段落番号)
    ig = t7.work_data7("ig_nobel")
    mix = t7._parse(ig, [t7._mf(ig, "P2", "POSTMOD", mq="published"), t7._mf(ig, "P4", "CLEFT", mq="what you got"), t7._mf(ig, "P5", "CMP", mq="more than")])["features"]
    assert [f["para"] for f in select_tiered(mix)[0]] == ["P4"] == [f["para"] for f in t7.select_one(mix)]
    assert len(select_tiered(mix + both)[0]) == 1                                                                  # 最大1件
    print("selftest08 OK")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "dry-run": print(json.dumps(dry_run(), ensure_ascii=False, indent=1))
    elif cmd == "selftest": selftest()
    elif cmd == "reselect":
        o = reselect()
        for w in WORKS8:
            for r in o[w]: print(w, r["run"], "old", [(m["para"], m["feature_class"]) for m in r["old"]], "new", [(m["para"], m["feature_class"]) for m in r["new"]], r["tier"], "CHANGED" if r["changed"] else "")
    elif cmd == "send-a":
        bg = Budget(CAP_A8, usage_spent8()); t0 = time.time()
        errs = batch_a8(make_real_llm(bg, lambda tag: MAXOUT_A))
        json.dump({"errors": errs, "spent_jpy": bg.spent, "log": bg.log, "elapsed": round(time.time() - t0, 1)}, open(os.path.join(BASE, "batch_08a_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("done", errs, round(bg.spent, 4))
