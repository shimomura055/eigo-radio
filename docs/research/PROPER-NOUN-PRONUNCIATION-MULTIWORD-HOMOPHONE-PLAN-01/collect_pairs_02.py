"""PNMH-PLAN-01 委任_02 (R-05): pairs_01.jsonl に加えて、追加の保存物から(canonical, ASR転写)ペアを集める(API 0・read-only)。
追加: (a) MDJF golden 193件(golden_rejudge.pyのcases()と同じ走査) (b) **/human_review_queue.jsonl の steps[*].text
(c) FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01 の runtime_evidence_{x,z}.json と fixtures_real_transcripts.json
(d) tts_generation_results.json の standard_attempts_log/attempts/segment直下のasr_text(pairs_01で未収集の形式)。
出力: pairs_02.jsonl (pairs_01+追加、重複除去、各行に origin 種別を付与)。"""
import json, glob, os, sys, hashlib, ast
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
os.chdir(ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))
pairs = {}
def add(c, a, origin, src):
    if not c or not a or not isinstance(c, str) or not isinstance(a, str): return
    k = hashlib.sha1((c + "\x00" + a).encode("utf8")).hexdigest()
    e = pairs.setdefault(k, {"canonical": c, "asr": a, "origins": set(), "sources": []})
    e["origins"].add(origin)
    if len(e["sources"]) < 3: e["sources"].append(src)
# base: pairs_01
for l in open(os.path.join(HERE, "pairs_01.jsonl"), encoding="utf8"):
    o = json.loads(l); add(o["canonical"], o["asr"], "pairs_01", (o.get("sources") or [""])[0])
n_base = len(pairs)
# (a) golden 193 (golden_rejudge.pyのcases()と同一の走査・重複除去)
RUNS = {
 "run_mey_02": "er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_02",
 "run_fxpw_01": "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01",
 "run_pp_01": "er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_01",
 "run_e2e_06(Z)": "er026_output/family_z_production_e2e_01/melos/run_e2e_06",
 "run_byus_01(参考)": "er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01",
}
golden = set(); golden_seen = set()
for rname, root in RUNS.items():
    for dirpath, _, files in os.walk(root):
        if "tts_generation_results.json" not in files: continue
        f = os.path.join(dirpath, "tts_generation_results.json")
        d = json.load(open(f, encoding="utf8"))
        for sid, seg in (d.get("segments") or {}).items():
            canon = seg.get("canonical_text") or seg.get("text")
            if not canon: continue
            outs = []
            for log_key in ("attempts_log", "standard_attempts_log", "attempts"):
                for i, a in enumerate(seg.get(log_key) or []):
                    if not isinstance(a, dict): continue
                    j = a.get("asr_judgement") or {}
                    outs += [a.get("asr_text"), (j.get("secondary") or {}).get("text")]
            j = seg.get("asr_judgement") or {}
            outs += [seg.get("asr_text"), (j.get("primary") or {}).get("text"), (j.get("secondary") or {}).get("text")]
            for txt in outs:
                if txt:
                    key = (f, sid, canon, txt)
                    if key in golden_seen: continue
                    golden_seen.add(key)
                    golden.add(hashlib.sha1((canon + "\x00" + txt).encode("utf8")).hexdigest())
                    add(canon, txt, "golden_mdjf", f.replace("\\", "/"))
n_golden_rows = len(golden_seen)
# (d) 全 tts_generation_results.json の追加形式
def walk(o, src, trail=""):
    if isinstance(o, dict):
        canon = o.get("canonical_text") or o.get("text")
        if isinstance(canon, str):
            for lk in ("attempts_log", "standard_attempts_log", "attempts"):
                for a in (o.get(lk) or []):
                    if isinstance(a, dict):
                        j = a.get("asr_judgement") or {}
                        add(canon, a.get("asr_text"), "tts_results_ext", src)
                        add(canon, (j.get("secondary") or {}).get("text"), "tts_results_ext", src)
            j = o.get("asr_judgement")
            if isinstance(j, dict):
                add(canon, o.get("asr_text"), "tts_results_ext", src)
                add(canon, (j.get("primary") or {}).get("text"), "tts_results_ext", src)
                add(canon, (j.get("secondary") or {}).get("text"), "tts_results_ext", src)
        for k, v in o.items(): walk(v, src, trail + "/" + str(k))
    elif isinstance(o, list):
        for v in o: walk(v, src, trail)
for p in glob.glob("**/tts_generation_results.json", recursive=True):
    if ".venv" in p: continue
    try: walk(json.load(open(p, encoding="utf8")), p.replace("\\", "/"))
    except Exception: pass
# (b) human_review_queue.jsonl
n_hr = 0
for p in glob.glob("**/human_review_queue.jsonl", recursive=True):
    if ".venv" in p: continue
    for l in open(p, encoding="utf8", errors="replace"):
        try: o = json.loads(l)
        except Exception: continue
        c = o.get("canonical_text"); st = o.get("steps")
        if isinstance(st, str):
            try: st = ast.literal_eval(st)
            except Exception: st = []
        for s in st or []:
            if isinstance(s, dict) and s.get("text"):
                add(c, s["text"], "human_review_queue", p.replace("\\", "/")); n_hr += 1
# (c) runtime evidence + fixtures
D = "docs/research/FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01"
fx = json.load(open(f"{D}/fixtures_real_transcripts.json", encoding="utf8"))
b = fx["byus_part1_att1"]; add(b["canonical"], b.get("primary_asr"), "runtime_fixture", "fixtures:byus"); add(b["canonical"], b.get("secondary_asr"), "runtime_fixture", "fixtures:byus")
for k, v in fx["family_z"].items():
    if isinstance(v, dict):
        for kk, vv in v.items():
            if kk in ("canonical", "canonical_text"): c = vv
        for kk, vv in v.items():
            if isinstance(vv, str) and kk not in ("canonical", "canonical_text") and "asr" in kk: add(c, vv, "runtime_fixture", f"fixtures:{k}")
for fam in ("x", "z"):
    r = json.load(open(f"{D}/runtime/runtime_evidence_{fam}.json", encoding="utf8"))
    cn = r.get("canonical") or (b["canonical"] if fam == "x" else None)
    if fam == "z":
        for k, v in fx["family_z"].items():
            if isinstance(v, dict) and r.get("segment") == k: cn = v.get("canonical") or v.get("canonical_text")
    aj = r.get("asr_judgement") or {}
    for t in (r.get("primary_transcript"), (aj.get("primary") or {}).get("text"), (aj.get("secondary") or {}).get("text")):
        add(cn, t, "runtime_fixture", f"runtime_evidence_{fam}.json")
out = os.path.join(HERE, "pairs_02.jsonl")
with open(out, "w", encoding="utf8", newline="\n") as f:
    for e in pairs.values():
        e["origins"] = sorted(e["origins"]); f.write(json.dumps(e, ensure_ascii=False) + "\n")
from collections import Counter
oc = Counter(o for e in pairs.values() for o in e["origins"])
print(json.dumps({"pairs_01": n_base, "total_pairs_02": len(pairs), "new_vs_01": len(pairs) - n_base, "golden_rows": n_golden_rows,
                  "golden_unique_pairs": len(golden), "hr_step_texts": n_hr, "by_origin": oc}, ensure_ascii=False))
