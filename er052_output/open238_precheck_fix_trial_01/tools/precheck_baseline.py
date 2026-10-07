"""OPEN-238 precheck baseline (pre-fix). Deterministic, no API calls (JPY 0).
Re-runs er052_open233_self_recovery_precheck_01.run_precheck (approved PRECHECK_MODE=number_only
=> only kind=number_mismatch kept) on existing EN articles + ledgers.
Usage: python precheck_baseline.py [--out DIR] [--precheck-module NAME] [--root ER052_OUTPUT]
Targets are auto-discovered under --root (default: er052_output)."""
import argparse, glob, hashlib, importlib, json, os, re, sys, importlib.abc, importlib.machinery

ROOT_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT_REPO)

QTY_RE = re.compile(r"\b(half|halves|third|thirds|quarter|quarters|fifth|fifths|tenth|tenths|double|doubled|doubling|doubles|triple|tripled|tripling|twice)\b", re.I)


def split_sentences(text):  # same logic as runner.split_sentences_generic
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")]
    flat = " ".join(lines)
    return [p.strip() for p in re.split(r"(?<=[。！？.!?])\s*", flat) if p.strip()]


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def rel(p, root):
    return os.path.relpath(p, root).replace(chr(92), "/")


def discover_dir_runs(root):
    runs = []
    pats = [("allfact_e2e02_p2", "open233_allfact_note_e2e_02/runs/*/nb/p2/rep*"),
            ("polysemy04_control", "open233_polysemy_trial_04/runs/*/control/rep1"),
            ("meta_ent01", "open233_meta_allfact_note_ent_01/runs/meta/nb/p*/rep1")]
    for tag, pat in pats:
        for d in sorted(glob.glob(os.path.join(root, pat))):
            a = os.path.join(d, "b1b", "article.md")
            l = os.path.join(d, "research_ledger", "verified_fact_ledger.txt")
            rid = tag + ":" + rel(d, root)
            if os.path.exists(a) and os.path.exists(l):
                runs.append({"run_id": rid, "en_source": rel(a, root), "ledger_source": rel(l, root),
                             "en": read(a), "ledger": read(l)})
            else:
                runs.append({"run_id": rid, "skipped": "b1b/article.md or research_ledger missing"})
    return runs


def install_stub():
    from unittest.mock import MagicMock

    class F(importlib.abc.MetaPathFinder, importlib.abc.Loader):
        def find_spec(self, name, path, target=None):
            if name.split(".")[0] in ("dotenv", "scipy", "numpy", "openai", "anthropic", "pydub", "soundfile", "requests", "google", "elevenlabs"):
                return importlib.machinery.ModuleSpec(name, self, is_package=True)

        def create_module(self, spec):
            m = MagicMock()
            m.__name__ = spec.name
            m.__path__ = []
            m.__spec__ = spec
            m.__loader__ = self
            return m

        def exec_module(self, m):
            pass
    sys.meta_path.append(F())


def discover_prod_runs(root):
    """prod_e2e_02 runs/*.json hold no EN/ledger for most runs; resolve via the runner's audit-file
    fixtures (read-only; import stubs missing optional deps; no API client is created)."""
    out = []
    files = sorted(glob.glob(os.path.join(root, "open233_prod_e2e_02/runs/*.json")))
    fx = {}
    try:
        install_stub()
        r = importlib.import_module("er052_open233_self_recovery_flow_runner_01")
        fx = {i["instance_id"]: i["fixture"] for i in r.build_target_instances()}
    except Exception as e:
        print("fixture resolution failed:", repr(e))
    for f in files:
        iid = os.path.splitext(os.path.basename(f))[0]
        rid = "prod_e2e02:" + iid
        if iid in fx:
            x = fx[iid]
            en = x["article_text"]
            same = None
            try:
                d = json.load(open(f, encoding="utf-8"))
                b = d["cycles"][0].get("en_text_before_rewrite")
                if b is not None:
                    same = (b.strip() == en.strip())
            except Exception:
                pass
            out.append({"run_id": rid, "en_source": "fixture:" + x["source_path"] + " (prompt article_text)",
                        "ledger_source": "fixture:" + x["source_path"] + " (prompt ledger_text)",
                        "en": en, "ledger": x["ledger_text"], "note": "json en_text_before_rewrite identical=%s" % same})
        else:
            out.append({"run_id": rid, "skipped": "fixture not resolvable"})
    return out


def analyze(pre, run):
    en, ledger = run["en"], run["ledger"]
    sents = split_sentences(en)
    vals = []
    for i, s in enumerate(sents):
        for m in pre.PERCENT_RE.finditer(s):
            vals.append({"value": round(pre._to_float(m.group(1)), 2), "matched_text": m.group(0), "sentence_index": i, "type": "percent"})
        for ph, pct in pre.FRACTION_WORD_TO_PERCENT.items():
            for m in re.finditer(r"\b" + re.escape(ph) + r"\b", s, re.I):
                vals.append({"value": round(pct, 2), "matched_text": m.group(0), "sentence_index": i, "type": "fraction_word"})
        for rx, mult in ((pre.JP_MAN_RE, 1e4), (pre.JP_OKU_RE, 1e8)):
            for m in rx.finditer(s):
                vals.append({"value": pre._to_float(m.group(1)) * mult, "matched_text": m.group(0), "sentence_index": i, "type": "count"})
        for m in pre.COUNT_WORD_RE.finditer(s):
            vals.append({"value": pre._to_float(m.group(1)) * pre._COUNT_MULT[m.group(2).lower()], "matched_text": m.group(0), "sentence_index": i, "type": "count"})
    findings = pre.run_precheck(ledger, en)
    all_kinds = {}
    for f in findings:
        all_kinds[f.get("kind")] = all_kinds.get(f.get("kind"), 0) + 1
    fires = []
    for f in findings:
        if f.get("kind") != "number_mismatch":  # approved PRECHECK_MODE=number_only
            continue
        sent = None
        for v in f.get("foreign_values") or []:
            for s in sents:
                if v in (pre.extract_percentages(s) | set(pre.extract_counts(s))):
                    sent = s
                    break
            if sent:
                break
        fires.append({"kind": f["kind"], "fact_id": f["field"], "foreign_values": f.get("foreign_values"), "sentence": sent})
    qty = []
    for i, s in enumerate(sents):
        ms = [m.group(0) for m in QTY_RE.finditer(s)]
        if ms:
            frac = [v for v in vals if v["sentence_index"] == i and v["type"] == "fraction_word"]
            qty.append({"sentence_index": i, "terms": ms, "sentence": s, "extracted": bool(frac),
                        "extracted_values": [(v["matched_text"], v["value"]) for v in frac]})
    return {"run_id": run["run_id"], "en_source": run["en_source"], "ledger_source": run["ledger_source"],
            "ledger_sha": sha(ledger), "en_sha": sha(en), "n_sentences": len(sents), "note": run.get("note"),
            "extracted_values": vals, "fires": fires, "all_precheck_kinds_before_filter": all_kinds,
            "quantity_expression_sentences": qty}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(ROOT_REPO, "er052_output"))
    ap.add_argument("--out", default=os.path.join(ROOT_REPO, "er052_output", "open238_precheck_fix_trial_01", "baseline"))
    ap.add_argument("--precheck-module", default="er052_open233_self_recovery_precheck_01")
    a = ap.parse_args()
    pre = importlib.import_module(a.precheck_module)
    runs = discover_dir_runs(a.root) + discover_prod_runs(a.root)
    results, skipped = [], []
    for r in runs:
        if "skipped" in r:
            skipped.append({"run_id": r["run_id"], "reason": r["skipped"]})
        else:
            results.append(analyze(pre, r))
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "precheck_baseline.json"), "w", encoding="utf-8") as f:
        json.dump({"precheck_module": a.precheck_module, "mode": "number_only(filter kind=number_mismatch)",
                   "runs": results, "skipped": skipped}, f, ensure_ascii=False, indent=1)
    L = ["# precheck baseline (pre-fix, number_only, JPY 0)", "",
         "runs analyzed=%d skipped=%d" % (len(results), len(skipped)), ""]
    for s in skipped:
        L.append("- SKIPPED %s: %s" % (s["run_id"], s["reason"]))
    L += ["", "## per-run", "", "| run_id | sentences | extracted values | fires | QTY-expr sentences (extracted) |", "|---|---|---|---|---|"]
    for r in results:
        q = r["quantity_expression_sentences"]
        L.append("| %s | %d | %d | %d | %d (%d) |" % (r["run_id"], r["n_sentences"], len(r["extracted_values"]), len(r["fires"]), len(q), sum(1 for x in q if x["extracted"])))
    L += ["", "fires total = %d" % sum(len(r["fires"]) for r in results), "", "## all fires", ""]
    for r in results:
        for f in r["fires"]:
            L.append("- %s | %s | foreign=%s | %s" % (r["run_id"], f["fact_id"], f["foreign_values"], f["sentence"]))
    L += ["", "## quantity-expression sentences (half/third/quarter/fifth/tenth/double/triple/twice); extracted = precheck fraction dict hit", ""]
    for r in results:
        for x in r["quantity_expression_sentences"]:
            L.append("- %s #%d terms=%s extracted=%s %s | %s" % (r["run_id"], x["sentence_index"], x["terms"], x["extracted"], x["extracted_values"] or "", x["sentence"]))
    with open(os.path.join(a.out, "BASELINE.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("runs", len(results), "skipped", len(skipped), "fires", sum(len(r["fires"]) for r in results))


if __name__ == "__main__":
    main()
