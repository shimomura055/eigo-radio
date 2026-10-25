# API 0 / read-only: 既存コーパス(eval_open517_api0_03の771件)に含まれない保存済みJA attempt(canonical, Primary転写)を集める(R-1 未知データ)。
# 出典: (S1) er*_output/**/tts_generation_results*.json の segments[*].attempts_log[*](asr_judgement.primary.text優先、無ければasr_text)
#       (S2) er*_output/**/attempts/*.json (language=ja)  ※attempt_pool_01収集後に増えたもの・pool未収載のもの
#       (S3) er*_output/**/human_review_queue.jsonl の canonical_text × steps[provider=openai_asr].text(Primary転写)
#       (S4) docs/research・er*_output配下の*.json/*.jsonl(20MB未満、本案件dir除く)で、canonical系キー(canonical/canonical_text/canon)と転写系キー(asr_text/openai_text/primary_text)を同じdictに持つ日本語record
# 除外: eval_open517_api0_03.out.json の771件の(canon, asr)キーと一致するもの。重複(canon, asr)は1件に集約(出典は全てsourcesに保持)。
# 出力: unknown_pool_02.json。再現: リポジトリrootで PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/collect_unknown_pool_02.py
import collections, glob, json, os, sys, unicodedata
D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
corpus = json.load(open(D + "open517_api0_eval_03.out.json", encoding="utf8"))["rows"]
known = {(r["canon"], r["asr"]) for r in corpus}


def family(path):
    p = path.replace("\\", "/")
    if "/family_x_" in p or p.startswith("er019_output"): return "X"
    if p.startswith("er026_output") or p.startswith("er063_output"): return "Z"
    if p.startswith("er110_output"): return "Y"
    return "legacy/other"


pool = {}
nrec = collections.Counter()


def add(canon, asr, src, label, basis):
    if not canon or not isinstance(asr, str) or not asr:
        return
    k = (canon, asr)
    nrec["scanned"] += 1
    if k in known:
        nrec["in_corpus"] += 1
        return
    e = pool.setdefault(k, {"canon": canon, "asr": asr, "sources": [], "labels": set(), "bases": set()})
    if len(e["sources"]) < 5:
        e["sources"].append(src)
    e["labels"].add(label); e["bases"].add(basis)


for p in glob.glob("er*_output/**/tts_generation_results*.json", recursive=True) + glob.glob("docs/research/**/tts_generation_results*.json", recursive=True):
    try:
        d = json.load(open(p, encoding="utf8"))
    except Exception:
        continue
    segs = d.get("segments") if isinstance(d, dict) else None
    if not isinstance(segs, dict):
        continue
    for key, s in segs.items():
        if not isinstance(s, dict) or s.get("language") != "ja":
            continue
        canon = s.get("canonical_text") or s.get("text")
        for a in s.get("attempts_log") or []:
            j = a.get("asr_judgement") or {}
            pr = j.get("primary") or {}
            asr = pr.get("text") or a.get("asr_text")
            add(canon, asr, p.replace("\\", "/") + "#" + key, pr.get("label") or a.get("audio_classification"), pr.get("equivalence_basis"))
for p in glob.glob("er*_output/**/attempts/*.json", recursive=True):
    try:
        d = json.load(open(p, encoding="utf8"))
    except Exception:
        continue
    if not isinstance(d, dict) or d.get("language") != "ja" or d.get("asr_text") is None:
        continue
    pp = p.replace("\\", "/")
    base = os.path.dirname(os.path.dirname(os.path.dirname(pp)))
    tp = base + "/audit/tts_generation_results.json"
    try:
        s = json.load(open(tp, encoding="utf8")).get("segments", {}).get(d.get("segment_id")) or {}
    except Exception:
        s = {}
    add(s.get("canonical_text") or s.get("text"), d.get("asr_text"), pp, d.get("audio_classification"), None)
for p in glob.glob("er*_output/**/human_review_queue.jsonl", recursive=True):
    for line in open(p, encoding="utf8", errors="replace"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        for st in r.get("steps") or []:
            if st.get("provider") == "openai_asr":
                add(r.get("canonical_text"), st.get("text"), p.replace("\\", "/") + "#hrq", st.get("classification"), None)
import re
_JA = re.compile(r"[぀-ヿ一-鿿]")


def walk(o, src):
    if isinstance(o, dict):
        c = next((o[k] for k in ("canonical", "canonical_text", "canon") if isinstance(o.get(k), str)), None)
        t = next((o[k] for k in ("asr_text", "openai_text", "primary_text") if isinstance(o.get(k), str)), None)
        if c and t and _JA.search(c) and _JA.search(t):
            add(c, t, src, o.get("audio_classification") or o.get("classification"), None)
        for v in o.values():
            walk(v, src)
    elif isinstance(o, list):
        for v in o:
            walk(v, src)


for root in ("docs/research", *sorted(glob.glob("er*_output"))):
    for p in glob.glob(root + "/**/*.json*", recursive=True):
        pp = p.replace("\\", "/")
        if "JA-ASR-FALSE-NG-ROOT-CAUSE-01" in pp or os.path.getsize(p) > 20_000_000 or "tts_generation_results" in pp or "/attempts/" in pp or pp.endswith("human_review_queue.jsonl"):
            continue
        try:
            if pp.endswith(".jsonl"):
                for line in open(p, encoding="utf8", errors="replace"):
                    try:
                        walk(json.loads(line), pp + "#s4")
                    except Exception:
                        pass
            else:
                walk(json.load(open(p, encoding="utf8")), pp + "#s4")
        except Exception:
            continue
rows = []
for k, e in sorted(pool.items(), key=lambda kv: (kv[1]["sources"][0], kv[0])):
    rows.append({"canon": e["canon"], "asr": e["asr"], "sources": e["sources"], "family": family(e["sources"][0]),
                 "labels": sorted(str(x) for x in e["labels"]), "bases": sorted(str(x) for x in e["bases"])})
json.dump(rows, open(D + "unknown_pool_02.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print("scanned records:", nrec["scanned"], "in 771-corpus:", nrec["in_corpus"], "unknown unique (canon,asr):", len(rows))
print("by family:", dict(collections.Counter(r["family"] for r in rows)))
print("with label PHONETIC_MATCH/READING_RESOLVED_MATCH:", sum(1 for r in rows if any(l in ("PHONETIC_MATCH", "READING_RESOLVED_MATCH") for l in r["labels"])))
print("with basis READING_MATCH:", sum(1 for r in rows if "READING_MATCH" in r["bases"]))
