# ENDUSER-TRANSLATION-CONTEXT-TRIAL-01 委任_02 本格Trial runner(Trial専用。Production経路へは接続しない)。
# Production関数 er135_enduser_translate_01.translate_part をそのまま呼ぶ。Prompt本文・モデル・routingは不変。変わるのは
#  (1)翻訳Promptの文脈欄に入る文list、(2)因子Vのとき verify Promptへ文脈ブロックを足す(判定基準本文は不変)、(3)方式Gのとき同levelの評価part群を1回のtranslate_partで訳す。
# cache_dirは使い捨てtempdir。出力は --out(本Trial dir配下のev0*_*)のみ。ledger=呼出ごと(ledger_<cond>.jsonl)。
import json, os, sys, time, tempfile, shutil, argparse, glob, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.getcwd()
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import ctx_methods_02 as CM
CONDS = {  # cond -> (context method, V, group)
    "A": ("A", False, False), "Ap": ("A", False, False),
    "C": ("C", False, False), "CV": ("C", True, False),
    "D": ("D", False, False), "DV": ("D", True, False),
    "E": ("E", False, False), "EV": ("E", True, False),
    "G": ("A", False, True)}
VERIFY_CONTEXT_LABEL = "# 文脈(判定対象ではない。語義・指示対象を理解するための参考。同じパートの他の文)\n"
TRIAL_DIR = os.path.normpath(os.path.join(HERE, ".."))


def spent_total():
    s = 0.0
    for f in glob.glob(os.path.join(TRIAL_DIR, "ev[0-9][0-9]_*", "ledger_*.jsonl")):
        if os.path.basename(os.path.dirname(f)).startswith(("ev02", "ev03", "ev04")):
            continue
        for ln in open(f, encoding="utf-8"):
            try:
                s += json.loads(ln).get("cost_jpy") or 0.0
            except Exception:
                pass
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cond", required=True, choices=sorted(CONDS))
    ap.add_argument("--split", required=True, choices=["dev", "heldout", "custom"])
    ap.add_argument("--sets", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stop-line", type=float, default=72.0)
    ap.add_argument("--hard-cap", type=float, default=85.0)
    ap.add_argument("--only-parts", default="", help="comma-separated slug/level/part")
    ap.add_argument("--tag", default="", help="ledger/parts file suffix")
    ap.add_argument("--mock", action="store_true", help="API 0 test mode (never used for paid runs)")
    a = ap.parse_args()
    import er135_enduser_translate_01 as TR
    if not a.mock:
        from dotenv import load_dotenv
        load_dotenv(r"C:\Users\tensh\eigo-radio\.env")
    os.makedirs(a.out, exist_ok=True)
    method, useV, group = CONDS[a.cond]
    name = a.cond + (("_" + a.tag) if a.tag else "")
    ledger_p = os.path.join(a.out, f"ledger_{name}.jsonl")
    parts_p = os.path.join(a.out, f"parts_{name}.jsonl")
    calls_p = os.path.join(a.out, f"calls_{name}.jsonl")
    done = set()
    if os.path.exists(parts_p):
        for ln in open(parts_p, encoding="utf-8"):
            done.add(json.loads(ln)["unit"])
    sets = json.load(open(a.sets, encoding="utf-8"))
    entries = sets["dev"] if a.split == "dev" else sets["heldout"] if a.split == "heldout" else sets["dev"] + sets["heldout"]
    if a.only_parts:
        want = set(a.only_parts.split(","))
        entries = [e for e in entries if f"{e['slug']}/{e['level']}/{e['part']}" in want]
    arts = {}

    def art(slug):
        if slug not in arts:
            arts[slug] = json.load(open(os.path.join(ROOT, "user_test", slug, "enduser", "data", "article.json"), encoding="utf-8"))
        return arts[slug]

    units = []
    if group:
        by = {}
        for e in entries:
            by.setdefault((e["slug"], e["level"]), []).append(e)
        for (slug, lv), es in by.items():
            units.append({"unit": f"{slug}/{lv}/GROUP", "slug": slug, "level": lv, "family": es[0]["family"], "entries": es})
    else:
        for e in entries:
            units.append({"unit": f"{e['slug']}/{e['level']}/{e['part']}", "slug": e["slug"], "level": e["level"], "family": e["family"], "entries": [e]})
    spent_run = 0.0
    for u in units:
        if u["unit"] in done:
            continue
        for sen in (os.path.join(TRIAL_DIR, "STOP"), os.path.join(a.out, "STOP")):
            if os.path.exists(sen):
                print("STOP sentinel", sen)
                sys.exit(3)
        tot = spent_total()
        if tot >= a.hard_cap:
            print("HARD CAP reached", tot)
            sys.exit(4)
        if tot >= a.stop_line:
            print("STOP LINE reached (record; continue only until hard cap)", round(tot, 3), flush=True)
        sents = []
        ctx = []
        if group:
            pi = 0
            for e in u["entries"]:
                last = None
                for s in e["sentences"]:
                    if s["para"] != last:
                        pi += 1
                        last = s["para"]
                    sents.append({"sid": s["sid"], "en": s["en"], "para": pi})
        else:
            e = u["entries"][0]
            sents = [{"sid": s["sid"], "en": s["en"], "para": s["para"]} for s in e["sentences"]]
            ctx = CM.build_context(method, art(u["slug"]), u["level"], e["part"])
        ctx_lines = [c["en"] for c in ctx]
        if a.mock:
            class Inner:
                def __init__(s):
                    s.calls = []

                def __call__(s, kind, prompt):
                    if kind == "translate":
                        tg = prompt.split(TR.TRANSLATE_TARGET_LABEL, 1)[1].split("\n# 前回", 1)[0].split("\n# 出力形式", 1)[0]
                        ids = re.findall(r"^(\d+)\. (.*)$", tg, re.M)
                        text = json.dumps({"translations": [{"id": int(i), "ja": "これは訳です" + chr(0x3041 + int(i)) + "。"} for i, t in ids]}, ensure_ascii=False)
                    else:
                        n = len(re.findall(r"^\d+\. EN:", prompt, re.M))
                        text = json.dumps({"results": [{"id": i, "ok": True} for i in range(1, n + 1)]})
                    s.calls.append({"kind": kind, "response_model": TR.MODEL, "usage": {"input_tokens": len(prompt), "output_tokens": 10}, "response_id": "mock", "cost_jpy": 0.0})
                    return text
            inner = Inner()
        else:
            inner = TR.DefaultLLM()
        state = {"ctx": list(ctx_lines), "double": False, "log": [], "wall": 0.0}

        class W:
            calls = inner.calls

            def __call__(s, kind, prompt):
                if kind == "translate":
                    prod_ctx = []
                    if TR.TRANSLATE_CONTEXT_LABEL in prompt:   # Production自身の同part他段落文脈(再試行ラウンド)
                        blk = prompt.split(TR.TRANSLATE_CONTEXT_LABEL, 1)[1].split(TR.TRANSLATE_TARGET_LABEL, 1)[0]
                        prod_ctx = [ln[2:] for ln in blk.split("\n") if ln.startswith("- ")]
                    merged = list(ctx_lines) + [c for c in prod_ctx if c not in ctx_lines]
                    if ctx_lines and prod_ctx:
                        state["double"] = True   # R-9: 方式文脈とProduction同part文脈が併存(単一ブロックへ統合して入力)
                    state["ctx"] = merged
                    if ctx_lines:
                        head, rest = prompt.split(TR.TRANSLATE_TARGET_LABEL, 1)
                        head = head.split(TR.TRANSLATE_CONTEXT_LABEL, 1)[0]
                        prompt = head + TR.TRANSLATE_CONTEXT_LABEL + "\n".join(f"- {c}" for c in merged) + "\n\n" + TR.TRANSLATE_TARGET_LABEL + rest
                elif kind == "verify" and useV and state["ctx"]:
                    tail = "# 対訳\n"
                    assert TR.VERIFY_HEAD.endswith(tail) and prompt.startswith(TR.VERIFY_HEAD)
                    prompt = TR.VERIFY_HEAD[:-len(tail)] + VERIFY_CONTEXT_LABEL + "\n".join(f"- {c}" for c in state["ctx"]) + "\n\n" + tail + prompt[len(TR.VERIFY_HEAD):]
                n0 = len(inner.calls)
                t0 = time.time()
                r = None
                try:
                    r = inner(kind, prompt)
                finally:
                    dt = time.time() - t0
                    state["wall"] += dt
                    c = inner.calls[-1] if len(inner.calls) > n0 else {}
                    led = {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "cond": name, "unit": u["unit"], "kind": kind, "wall_s": round(dt, 2), "model": c.get("response_model"), "usage": c.get("usage"), "cost_jpy": c.get("cost_jpy")}
                    with open(ledger_p, "a", encoding="utf-8") as f:
                        f.write(json.dumps(led, ensure_ascii=False) + "\n")
                    state["log"].append({"kind": kind, "prompt": prompt, "response": r, "wall_s": round(dt, 2), "cost_jpy": c.get("cost_jpy"), "usage": c.get("usage")})
                return r

        w = W()
        tmp = tempfile.mkdtemp()
        try:
            res = TR.translate_part(u["unit"], sents, level=u["level"], family=u["family"], cache_dir=tmp, llm=w)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        cost = sum((c.get("cost_jpy") or 0) for c in inner.calls)
        spent_run += cost
        row = {"unit": u["unit"], "cond": name, "split": a.split, "slug": u["slug"], "level": u["level"], "family": u["family"],
               "parts": [{"part": e["part"], "kind": e["kind"], "stratum": e["stratum"], "sids": [s["sid"] for s in e["sentences"]]} for e in u["entries"]],
               "ctx_sentences": len(ctx_lines), "ctx_chars": sum(len(x) for x in ctx_lines), "double_ctx_block": state["double"],
               "ja": res["ja"], "complete": res["coverage"]["complete"], "paragraphs": res["coverage"]["paragraphs"], "paragraphs_translated": res["coverage"]["paragraphs_translated"],
               "failures": res["meta"]["failures"], "api_calls": res["meta"]["api_calls"], "wall_s": round(state["wall"], 2), "cost_jpy": round(cost, 4),
               "calls": [{"kind": x["kind"], "wall_s": x["wall_s"], "cost_jpy": x["cost_jpy"], "usage": x["usage"]} for x in state["log"]]}
        with open(calls_p, "a", encoding="utf-8") as f:
            f.write(json.dumps({"unit": u["unit"], "log": state["log"]}, ensure_ascii=False) + "\n")
        with open(parts_p, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(name, u["unit"], "cost", row["cost_jpy"], "run", round(spent_run, 4), "complete", row["complete"], "calls", row["api_calls"], flush=True)
    print("DONE", name, "run_spent", round(spent_run, 4), "trial_total", round(spent_total(), 4))


if __name__ == "__main__":
    main()
