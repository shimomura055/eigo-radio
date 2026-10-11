import sys, os, json, glob
sys.path.insert(0, "er053_output/open258_phase0_trial_01")
from open258_phase0_common import *

ev = json.load(open(EVID, encoding="utf8"))
G = ev["impact_estimate_from_logs"]["groups"]
RESCUE_GROUPS = [2, 7, 8, 11, 17, 20, 21, 23, 24, 26, 27, 31, 33, 36]   # 設計書V1の14群(whisper small一致)
META_GROUP = 35
NEG_GROUPS = [12, 3, 4, 5, 18, 1, 6, 22, 42]   # 追加の誤PASSリスク検証用(whisperと不一致の真のTTS誤り候補)


def strings(o, out):
    if isinstance(o, str): out.append(o)
    elif isinstance(o, list):
        for e in o: strings(e, out)
    elif isinstance(o, dict):
        for e in o.values(): strings(e, out)


_HIST = None
def _hist_shas(seg, path):
    global _HIST
    if _HIST is None:
        _HIST = []
        for l in open("er011_output/attempt_history.jsonl", encoding="utf8"):
            try: _HIST.append(json.loads(l))
            except Exception: pass
    return {h["canonical_text_sha256"] for h in _HIST if h.get("segment_id") == seg and h.get("theme_id") and h["theme_id"] in path and h.get("canonical_text_sha256")}


def find_canonical(run, seg, proxy, primary_asr):
    """sha256照合で原稿候補を探し、複数あればこのattemptのPrimary転写に最も近いものを選ぶ。"""
    lock = os.path.join(run, "audit", "review_lock_state.json")
    targets = set(_hist_shas(seg, run.replace("\\", "/")))
    if os.path.exists(lock):
        o = json.load(open(lock, encoding="utf8"))
        t = (o.get(seg) or {}).get("canonical_text_sha256")
        if t: targets.add(t)
    cands = []
    for f in glob.glob(run + "/**/*", recursive=True):
        fn = f.replace("\\", "/")
        if "/attempts/" in fn or os.path.isdir(f) or os.path.getsize(f) > 3_000_000: continue
        try:
            if f.endswith(".json"):
                strings(json.load(open(f, encoding="utf8")), cands)
            elif f.endswith(".md") or f.endswith(".txt"):
                cands += open(f, encoding="utf8").read().splitlines()
        except Exception:
            continue
    hits = set()
    for s_ in set(cands):
        for v in (s_, s_.strip()):
            if hashlib.sha256(v.encode("utf-8")).hexdigest() in targets:
                hits.add(v)
    if proxy and any(hashlib.sha256(v.encode("utf-8")).hexdigest() in targets for v in (proxy, proxy.strip())):
        hits.add(proxy)
    if hits:
        import difflib
        best = max(hits, key=lambda h: difflib.SequenceMatcher(None, javal.normalize_ja(h), javal.normalize_ja(primary_asr)).ratio())
        return best, f"sha256照合で原稿確定(候補{len(hits)}件中、Primary転写に最近接)"
    return proxy, "PROXY(後続合格attemptのASR文字列。原稿sha照合不可)"


def meta_canonical():
    return "AIの電話に人間が出演。問題は「キャスト変更」のお知らせでした", "ユーザー確定事実/設計書11節の原稿"


rows = []
def add(gi, role):
    x = G[gi]; d_ = x["dir"].replace("\\", "/"); run = os.path.dirname(os.path.dirname(d_))
    for a in x["attempts"]:
        if gi == META_GROUP:
            canon, csrc = meta_canonical()
        else:
            canon, csrc = find_canonical(run, x["seg"], x["proxy_canonical"], a["asr"])
        fs = glob.glob(f'{d_}/{x["seg"]}_attempt{a["n"]}_*.wav')
        if not fs: rows.append({"group": gi, "seg": x["seg"], "attempt": a["n"], "audio_missing": True, "role": role}); continue
        p = fs[0].replace("\\", "/")
        agree_now = bool(a.get("whisper_agrees_now") or a.get("whisper_agrees"))
        r = {"group": gi, "dir": d_, "seg": x["seg"], "attempt": a["n"], "wav": p, "sha256": sha(p), "duration_s": round(dur(p), 2),
             "canonical": canon, "canonical_source": csrc, "primary_asr": a["asr"], "existing_cls_logged": a["cls"],
             "whisper_small_logged": a.get("whisper_small"), "whisper_small_agrees_proxy": agree_now}
        r["role"] = role if role != "RESCUE" else ("B_rescue_candidate" if agree_now else "C_negative_in_rescue_group")
        r.update(exclusion_check(canon, a["asr"]))
        rows.append(r)

for gi in [META_GROUP]: add(gi, "A_meta")
for gi in RESCUE_GROUPS: add(gi, "RESCUE")
for gi in NEG_GROUPS: add(gi, "C_negative")
# dedupe by sha(同一音声は1回だけ)
seen = {}
for r in rows:
    if r.get("audio_missing"): continue
    s = r["sha256"]
    if s in seen: r["duplicate_of"] = seen[s]
    else: seen[s] = f'g{r["group"]}_{r["seg"]}_a{r["attempt"]}'
json.dump(rows, open(OUT + "/manifest_all_candidates_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
for r in rows:
    if r.get("audio_missing"): print("MISSING", r); continue
    print(r["group"], r["role"], r["seg"], r["attempt"], r["duration_s"], r["primary_cls"], "EX:", r["existing_exclusions"], "EXTRA:", r["extra_exclusions"], "DUP" if r.get("duplicate_of") else "", "|", r["canonical_source"][:10])
