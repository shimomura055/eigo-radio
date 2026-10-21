"""PNMH-PLAN-01: 既存保存物(API 0)から (canonical, ASR転写) ペアを収集する。read-only。
出典: (1) **/tts_generation_results.json の attempts_log (Primary asr_text / Secondary text)、
(2) er021 telemetry (canonical/asr)。出力: pairs_01.jsonl (重複除去)。"""
import json, glob, os, sys, hashlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
pairs = {}
def add(c, a, src, engine, label=None, locus=""):
    if not c or not a: return
    k = hashlib.sha1((c + "\x00" + a).encode("utf8")).hexdigest()
    e = pairs.setdefault(k, {"canonical": c, "asr": a, "sources": [], "engines": set(), "labels": set()})
    e["sources"].append(f"{src}:{locus}")
    e["engines"].add(engine)
    if label: e["labels"].add(label)
def walk(o, src, trail=""):
    if isinstance(o, dict):
        al = o.get("attempts_log")
        canon = o.get("canonical_text") or o.get("text")
        if isinstance(al, list) and isinstance(canon, str):
            for a in al:
                if not isinstance(a, dict): continue
                j = a.get("asr_judgement") or {}
                pt = a.get("asr_text")
                pl = (j.get("primary") or {}).get("label") if isinstance(j, dict) else None
                add(canon, pt, src, "primary", pl, f"{trail}#att{a.get('attempt')}")
                sec = (j.get("secondary") or {}) if isinstance(j, dict) else {}
                if sec.get("text"):
                    add(canon, sec["text"], src, "secondary", sec.get("label"), f"{trail}#att{a.get('attempt')}")
        for k, v in o.items(): walk(v, src, trail + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, src, trail + f"[{i}]")
files = [p for p in glob.glob("**/tts_generation_results.json", recursive=True) if ".venv" not in p]
for p in files:
    try: walk(json.load(open(p, encoding="utf8")), p.replace("\\", "/"))
    except Exception as ex: print("skip", p, ex, file=sys.stderr)
n_real = len(pairs)
tel = "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl"
for i, l in enumerate(open(tel, encoding="utf8")):
    try: o = json.loads(l)
    except Exception: continue
    add(o.get("canonical"), o.get("asr"), tel, "telemetry", o.get("classification"), f"L{i+1}")
out = os.path.join(os.path.dirname(__file__), "pairs_01.jsonl")
with open(out, "w", encoding="utf8", newline="\n") as f:
    for e in pairs.values():
        e["engines"] = sorted(e["engines"]); e["labels"] = sorted(e["labels"]); e["n_src"] = len(e["sources"]); e["sources"] = e["sources"][:3]
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
print("files", len(files), "pairs_from_results", n_real, "total_unique_pairs", len(pairs))
