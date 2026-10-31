# probe(Cap 15円/止め線12円): 1〜2 partを方式A/B/D/Eで再翻訳しtoken・出力形式・時間を実測。Production関数 translate_part をそのまま呼ぶ。
# 出力先は引数の証跡dir+使い捨てcache(tempdir)のみ。Production cache・公開dirへは書かない。
import json, os, sys, time, tempfile, shutil, argparse
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv; load_dotenv(r"C:\Users\tensh\eigo-radio\.env")
import er135_enduser_translate_01 as TR
import ctx_methods_02 as CM
ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--cap", type=float, default=12.0)
ap.add_argument("--targets", required=True, help="JSON list of [article_json_path, level, part_key, family]"); ap.add_argument("--methods", default="A,B,D,E")
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
spent = 0.0; results = []
for path, lv, pk, fam in json.loads(a.targets):
    art = json.load(open(path, encoding="utf-8")); part = [p for p in art["levels"][lv]["parts"] if p["key"] == pk][0]
    sents = [{"sid": s["sid"], "en": s["text"], "para": pi} for pi, pa in enumerate(part["paragraphs"]) for s in pa]
    for m in a.methods.split(","):
        if spent >= a.cap: print("STOP: cap reached", spent); sys.exit(3)
        ctx = CM.build_context(m, art, lv, pk)
        class W:
            def __init__(s): s.inner = TR.DefaultLLM(); s.calls = s.inner.calls; s.log = []; s.t = 0.0
            def __call__(s, kind, prompt):
                if kind == "translate" and ctx:
                    prompt = prompt.replace(TR.TRANSLATE_TARGET_LABEL, TR.TRANSLATE_CONTEXT_LABEL + "\n".join(f"- {c['en']}" for c in ctx) + "\n\n" + TR.TRANSLATE_TARGET_LABEL, 1)
                t0 = time.time(); r = s.inner(kind, prompt); dt = time.time() - t0; s.t += dt
                s.log.append({"kind": kind, "prompt": prompt, "response": r, "wall_s": round(dt, 2)}); return r
        w = W(); tmp = tempfile.mkdtemp()
        try:
            res = TR.translate_part(f"{lv}:{pk}", sents, level=lv, family=fam, cache_dir=tmp, llm=w)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        cost = sum(c["cost_jpy"] or 0 for c in w.calls); spent += cost
        row = {"article": os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(path)))), "level": lv, "part": pk, "method": m, "context_sentences": len(ctx), "context_chars": sum(len(c["en"]) for c in ctx),
               "calls": [{"kind": c["kind"], "usage": c["usage"], "cost_jpy": c["cost_jpy"], "model": c["response_model"]} for c in w.calls],
               "wall_s": round(w.t, 2), "cost_jpy": round(cost, 4), "ja": res["ja"], "coverage_complete": res["coverage"]["complete"], "failures": res["meta"]["failures"], "api_calls": res["meta"]["api_calls"]}
        results.append(row); json.dump(w.log, open(os.path.join(a.out, f"log_{row['article']}_{lv}_{pk}_{m}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(row["article"], lv, pk, m, "ctx", len(ctx), "cost", row["cost_jpy"], "spent", round(spent, 4), "ok", row["coverage_complete"], flush=True)
json.dump({"spent_jpy": round(spent, 4), "rows": results}, open(os.path.join(a.out, "probe_result_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("TOTAL", round(spent, 4))
