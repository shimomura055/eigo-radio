# ASR-FLAP-T-PRODUCTION-WIRING-01 委任_02A 集計(API 0)。Trial flapt_probe_analyze_02.py と同一判定基準。
# 実行: PYTHONUTF8=1 <venv python> docs/research/ASR-FLAP-T-PRODUCTION-WIRING-01/tools/flapt_probe_analyze_03.py
import collections, hashlib, json, os
W = "docs/research/ASR-FLAP-T-PRODUCTION-WIRING-01"
T = "docs/research/ASR-FLAP-T-EQUIVALENCE-TRIAL-01"
OBS = ["latter", "metal", "betting", "atom", "waiting", "coating", "the latter one"]
SYS = ["openai", "azure", "whisper"]
EXPECT = [f"{v}|pro" for v in ["Zephyr", "Schedar", "Algieba", "Charon", "Aoede", "Fenrir", "Puck"]]
MODEL = {"fl": "gemini-3.8-flash-lite-tts", "pro": "gemini-2.5-pro-preview-tts"}
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

def verdict(rows):
    items = {r["item"]: r for r in rows}
    obs, ex = [], 0
    anyd = []
    for it in OBS:
        r = items.get(it)
        if not r: continue
        c = r["class"]
        nd = sum(1 for s in SYS if c.get(s) == "FLAP_D"); ne = sum(1 for s in SYS if c.get(s) == "EXACT")
        if nd >= 2: obs.append(it)
        if nd >= 1: anyd.append(it)
        if ne >= 2: ex += 1
    if len(obs) >= 2: v = "FLAP_DEMONSTRATED"
    elif not anyd and ex >= 5: v = "T_SPELLED"
    else: v = "INDETERMINATE"
    return v, obs, anyd, ex

rows = []
for d in ("probe_03a", "probe_03b"):
    for l in open(f"{W}/{d}/results.jsonl", encoding="utf8"): rows.append(json.loads(l))
by = collections.defaultdict(list); fails = []
for r in rows:
    (by[f"{r['voice']}|{r['path']}"].append(r) if r.get("status") == "OK" else fails.append(r["clip_key"]))
combos = {}
for k in EXPECT:
    rs = by.get(k, [])
    v, obs, anyd, ex = verdict(rs) if rs else ("UNOBTAINED", [], [], 0)
    cat = {"flap_demonstrated": "confirmed", "FLAP_DEMONSTRATED": "confirmed", "T_SPELLED": "not_confirmed", "INDETERMINATE": "not_confirmed", "UNOBTAINED": "未取得"}[v]
    combos[k] = {"clips": len(rs), "clips_expected": 7, "probe_verdict": v, "judgement": cat, "flap_observed_items(>=2 systems)": obs,
                 "d_spelled_items(>=1 system)": anyd, "t_spelled_exact_items(>=2 systems)": ex,
                 "d_transcripts": sum(1 for r in rs for s in SYS if r["class"].get(s) == "FLAP_D"),
                 "t_transcripts": sum(1 for r in rs for s in SYS if r["class"].get(s) == "EXACT"),
                 "total_transcripts": 3 * len(rs), "model": rs[0]["model"] if rs else None, "voice_sent": rs[0]["voice_sent"] if rs else None,
                 "clip_sha256": {r["item"]: r["clip_sha256"] for r in rs},
                 "transcripts": {r["item"]: {s: r["asr"][s]["text"] for s in SYS} for r in rs},
                 "asr_cost_jpy": round(sum(r.get("asr_cost_jpy", 0) for r in rs), 3)}
# 速度
sp = json.load(open(f"{W}/probe_03c/results.json", encoding="utf8"))
n02 = {}
for d in ("probe_02", "probe_02b"):
    for l in open(f"{T}/{d}/results.jsonl", encoding="utf8"):
        r = json.loads(l)
        if r.get("status") == "OK" and r["variant"] == "normal": n02[(r["voice"], r["path"], r["item"])] = r
spd = {}
for r in sp["rows"]:
    k = f"{r['voice']}|{r['path']}"
    spd.setdefault(k, []).append(r)
speed = {}
for k, rs in spd.items():
    ok = [r for r in rs if r["status"] == "OK"]
    v, obs, anyd, ex = verdict(ok)
    nobs = []
    base = [n02[(r["voice"], r["path"], r["item"])] for r in ok if (r["voice"], r["path"], r["item"]) in n02]
    bv, bobs, banyd, bex = verdict(base)
    azure_empty = sum(1 for r in ok if r["class"].get("azure") == "EMPTY")
    speed[k] = {"fast106_verdict": v, "fast106_observed(>=2 systems)": obs, "fast106_d_spelled(>=1)": anyd, "normal_observed(>=2)": bobs, "normal_d_spelled(>=1)": banyd,
                "clips": len(ok), "azure_EMPTY_clips": azure_empty, "maintained": v == "FLAP_DEMONSTRATED",
                "d_transcripts": sum(1 for r in ok for s in SYS if r["class"].get(s) == "FLAP_D")}
out = {"combos": combos, "speed_106": speed, "failed_clips": fails}
json.dump(out, open(f"{W}/voice_probe_03.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
for k, c in combos.items(): print(k, c["clips"], c["probe_verdict"], c["flap_observed_items(>=2 systems)"], c["d_transcripts"], c["t_transcripts"], c["t_spelled_exact_items(>=2 systems)"])
for k, s in speed.items(): print("SPEED", k, s["fast106_verdict"], s["fast106_observed(>=2 systems)"], "normal", s["normal_observed(>=2)"], "azEMPTY", s["azure_EMPTY_clips"])
