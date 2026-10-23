"""ASR-TIME-NUMERAL-EQUIVALENCE-01 replay基盤(1/2): リポジトリ内の全 .json/.jsonl から (canonical, asr) 対を抽出し pairs_01.jsonl に保存する。
前身: docs/research/FAMILY-Z-AFTER-TWENTY-YEARS-PRODUCTION-01/replay482b.py (抽出ロジックを一般化、判定は行わない)。API 0・読み取り専用。
使い方: py <this> [--root .] [--out pairs_01.jsonl]
"""
import re, json, os, argparse, hashlib
CK = ("canonical", "canonical_text", "expected", "expected_text", "source_text", "script_text", "clip_text", "src", "canon", "original_text", "tts_input", "text")
AK = ("asr", "asr_text", "primary_text", "secondary_text", "transcript", "asr_transcript", "primary_asr_text", "secondary_asr_text", "hyp", "adopted_text", "transcript_text")
NUMRE = re.compile(r"\d|\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\b", re.I)
SKIP = {".git", ".venv", "node_modules", "__pycache__"}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default="."); ap.add_argument("--out", default="pairs_01.jsonl"); a = ap.parse_args()
    pairs = {}; nfiles = 0
    for root, ds, fs in os.walk(a.root):
        ds[:] = [d for d in ds if d not in SKIP]
        for f in fs:
            if not f.endswith((".json", ".jsonl")): continue
            p = os.path.join(root, f)
            if os.path.abspath(p) == os.path.abspath(a.out): continue
            try: t = open(p, encoding="utf-8", errors="ignore").read()
            except Exception: continue
            nfiles += 1
            if not re.search(r"\d", t): continue
            objs = []
            try: objs = [json.loads(t)]
            except Exception:
                for l in t.splitlines():
                    try: objs.append(json.loads(l))
                    except Exception: pass
            def walk(o):
                if isinstance(o, dict):
                    cs = [o[k] for k in CK if isinstance(o.get(k), str) and NUMRE.search(o[k])]
                    as_ = [o[k] for k in AK if isinstance(o.get(k), str)]
                    for c in cs:
                        for x in as_:
                            if c != x and len(c) < 3000 and len(x) < 3000: pairs.setdefault((c, x), p.replace("\\", "/"))
                    for v in o.values(): walk(v)
                elif isinstance(o, list):
                    for v in o: walk(v)
            for o in objs: walk(o)
    with open(a.out, "w", encoding="utf-8") as fo:
        for (c, x), p in pairs.items():
            fo.write(json.dumps({"id": hashlib.sha1((c + "\x00" + x).encode()).hexdigest()[:12], "canon": c, "asr": x, "src": p}, ensure_ascii=False) + "\n")
    print("files", nfiles, "pairs", len(pairs))
if __name__ == "__main__": main()
