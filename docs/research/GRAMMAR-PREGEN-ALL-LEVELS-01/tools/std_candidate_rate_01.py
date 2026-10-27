# DEV script (GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02S): Standard(a2)本文でのStep A''候補率計測。
# Productionの er120_part2_grammar_production_01.extract_candidates を無変更でimportして呼ぶだけ(Prompt/閾値/model不変)。
# Production非接触: 書込みは --out 配下のみ。Step B(解説生成)は呼ばない。
import argparse, hashlib, json, os, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import subprocess, types
ER120_REV = os.environ.get("ER120_REV", "438ac1b22")   # 並行Agent(委任_02)が作業ツリーのer120を編集中のため、コミット固定版を読む(無改変・Production関数そのまま)
_src = subprocess.run(["git", "show", f"{ER120_REV}:er120_part2_grammar_production_01.py"], capture_output=True, check=True).stdout
g = types.ModuleType("er120_part2_grammar_production_01")
g.__file__ = f"git:{ER120_REV}:er120_part2_grammar_production_01.py"
sys.modules["er120_part2_grammar_production_01"] = g
exec(compile(_src.decode("utf-8"), g.__file__, "exec"), g.__dict__)

# 入力: family:path (X=er019 a2/article.md, Y=translate/a2.md, Z=writer/std.md)
def paragraphs_for(family, path):
    text = open(path, encoding="utf-8").read()
    label = next((l.strip()[2:].strip() for l in text.splitlines() if l.strip().startswith("# ")), "Untitled")
    if family == "X":
        return g.paragraphs_from_article_md(text), label
    if family == "Y":
        import er121_family_y_structure_01 as ys   # 既存Production関数(Y runner _part2_inputsと同一)
        return ys.canonical_body(text).split("\n\n"), label
    if family == "Z":
        import er026_family_z_fiction_production_runner_01 as zr   # Z runner _part2_inputs_z相当
        return zr.canonical_article_text(text).split("\n\n"), label
    raise SystemExit("family must be X/Y/Z")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--articles", nargs="+", required=True, help="FAMILY=path ...")
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget-jpy", type=float, default=7.0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    spent = 0.0
    rows = []
    for spec in a.articles:
        fam, path = spec.split("=", 1)
        paras, label = paragraphs_for(fam, path)
        slug = hashlib.sha1(path.encode()).hexdigest()[:8]
        def guard(stage, est):
            if spent + 0.9 > a.budget_jpy:   # 実測上限0.88/call
                raise SystemExit(f"BUDGET_GUARD: spent={spent} cap={a.budget_jpy}")
        t0 = time.time()
        doc = g.extract_candidates(paras, label, budget_guard=guard)
        el = round(time.time() - t0, 1)
        cost = doc["audit"].get("total_cost_jpy") or 0.0
        spent += cost
        cands = doc["candidates"]
        tt = doc["tier_table"]
        row = dict(family=fam, path=path, label=label, n_paragraphs=len(paras), n_words=sum(len(p.split()) for p in paras),
                   n_features=len(tt), n_eligible=len(cands),
                   tiers=[c.get("tier") for c in cands], classes=[c.get("feature_class") for c in cands],
                   examples=[dict(para=c.get("para"), sentence=c.get("sentence"), tier=c.get("tier")) for c in cands[:3]],
                   not_eligible_reasons=[t["why_not"] for t in tt if not t["eligible"]][:12],
                   cost_jpy=cost, elapsed_sec=el, model=doc.get("model"), prompt_sha256=g.STEPA_PROMPT_SHA256,
                   usage=[c.get("usage") for c in doc["audit"].get("calls", [])], retried=doc["audit"].get("retried_for_parse"))
        rows.append(row)
        json.dump(doc, open(os.path.join(a.out, f"cand_{fam}_{slug}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        with open(os.path.join(a.out, "raw_usage_log.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(ts=time.strftime("%Y-%m-%dT%H:%M:%S%z"), family=fam, path=path, cost_jpy=cost, usage=row["usage"], model=row["model"]), ensure_ascii=False) + "\n")
        print(fam, label, "elig=", len(cands), "cost=", cost, "sec=", el, flush=True)
    summ = dict(rows=rows, total_cost_jpy=round(spent, 4), er120_rev=ER120_REV, er120_blob_sha256=hashlib.sha256(_src).hexdigest(),
                prompt_sha256=g.STEPA_PROMPT_SHA256, model=g.MODEL)
    json.dump(summ, open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("TOTAL", summ["total_cost_jpy"])

if __name__ == "__main__":
    main()
