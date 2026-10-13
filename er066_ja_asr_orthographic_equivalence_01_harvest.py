# JA-ASR-ORTHOGRAPHIC-EQUIVALENCE-COMPREHENSIVE-01: 過去事例の横断収集(read-only、API不使用)
import json, os, re, sys, hashlib, glob
JA = re.compile(r"[぀-ヿ一-鿿]")
OUT = "er066_output/ja_asr_orthographic_equivalence_01"
pairs = {}  # key=(canon,asr) -> meta

def add(canon, asr, src, extra=None):
    if not isinstance(canon, str) or not isinstance(asr, str): return
    if not JA.search(canon) or not JA.search(asr): return
    if canon.strip() == asr.strip(): return
    k = (canon, asr)
    m = pairs.setdefault(k, {"canonical": canon, "asr": asr, "sources": []})
    if src not in m["sources"]: m["sources"].append(src)
    if extra: m.setdefault("extra", {}).update(extra)

def walk(node, src, ctx):
    if isinstance(node, dict):
        c = node.get("canonical_text") or node.get("canonical") or node.get("text") or ctx
        for ak in ("asr_text", "transcript", "primary_asr", "secondary_text", "asr", "primary_text"):
            if ak in node and isinstance(node[ak], str):
                cc = node.get("canonical_text") or node.get("canonical") or node.get("text") or ctx
                add(cc, node[ak], src, {"key": ak, "cls": node.get("classification") or node.get("sec_cls") or node.get("status")})
        nctx = node.get("canonical_text") or node.get("canonical") or ctx
        for k, v in node.items():
            if isinstance(v, (dict, list)): walk(v, src, nctx)
    elif isinstance(node, list):
        for v in node: walk(v, src, ctx)

def main():
    files = []
    for root, ds, fs in os.walk("."):
        if any(p in root for p in (".venv", ".git", "node_modules")): continue
        if os.sep + "er066_output" in root: continue
        for f in fs:
            if f.endswith((".json", ".jsonl")) and f != "telemetry.jsonl" and "attempt_history" not in f:
                files.append(os.path.join(root, f))
    for p in files:
        try:
            if os.path.getsize(p) > 60_000_000: continue
            if p.endswith(".jsonl"):
                for l in open(p, encoding="utf-8"):
                    l = l.strip()
                    if l:
                        try: walk(json.loads(l), p.replace("\\", "/"), None)
                        except Exception: pass
            else:
                walk(json.load(open(p, encoding="utf-8")), p.replace("\\", "/"), None)
        except Exception:
            pass
    # HR queue steps
    q = "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl"
    for l in open(q, encoding="utf-8"):
        d = json.loads(l)
        for s in d.get("steps", []):
            add(d.get("canonical_text"), s.get("text"), q, {"key": "hr_step", "cls": s.get("classification") or s.get("step")})
    out = list(pairs.values())
    json.dump(out, open(f"{OUT}/harvest_raw_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(files), "files scanned;", len(out), "unique non-identical JA pairs")
main()
