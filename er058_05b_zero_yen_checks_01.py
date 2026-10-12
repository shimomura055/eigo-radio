# -*- coding: utf-8 -*-
"""委任_05B 0円追加確認の再現script(保存ログ・保存attempt・既存validatorの純関数のみ。API呼出なし・Production書込なし)。
出力: er058_output/trial_abc/zero_yen_checks_05B/zero_yen_checks_05B.json
 (1) S1(数値安全条件)の穴: 英語`N%`変更の4件、日本語の漢数字/表記差
 (2) KP 2段目(English Lock)救済実績: attempt_history.jsonl と保存attempt json
 (3) 日本語minimalの指示文読み上げ(leakage) Flash-Lite期の再発率
 (4) 400"Model tried to generate text"の同一Prompt再試行実績
"""
import collections, glob, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
OUT = os.path.join(ROOT, "er058_output", "trial_abc", "zero_yen_checks_05B")
os.makedirs(OUT, exist_ok=True)
res = {}

# ---------------- (1) S1 ----------------
import er058_trial_c_en_asr_compare_01 as t  # noqa
sys.stdout = open(1, "w", encoding="utf-8", closefd=False, buffering=1)
sample = json.load(open(os.path.join(ROOT, "er058_output", "trial_c", "sample_C_01.json"), encoding="utf-8"))
en = []
for it in sample:
    canon = it.get("canonical")
    if not canon:
        continue
    for mt, y in t.mutations(canon):
        if mt != "number":
            continue
        cp = t.cls(canon, y, it["segment_id"])
        g = t.gate_reason({**it, "primary_text": y, "length_ok": True, "repetition_flagged": False, "disfluency_flagged": False}, cp)
        en.append({"id": it["id"], "gate": g, "class": cp.classification, "numneg": t.numneg(cp),
                   "content_diffs": [(d["canonical"], d["asr"]) for d in cp.protected.content_word_diffs][:2]})
res["s1_en_number_mutations"] = {"n": len(en), "blocked": sum(1 for r in en if r["gate"]), "not_blocked": [r for r in en if not r["gate"]]}
import er007_ja_asr_validator_01 as j  # noqa
import er007_ja_secondary_asr_01 as sj  # noqa
sys.stdout = open(1, "w", encoding="utf-8", closefd=False, buffering=1)
ja = []
for c, a in [("二人で行きました。", "2人で行きました。"), ("20％の人が来ました。", "20パーセントの人が来ました。"), ("三十人が来ました。", "30人が来ました。"),
             ("2026年に始まります。", "二千二十六年に始まります。"), ("十分待ちました。", "10分待ちました。"), ("100円でした。", "百円でした。"),
             ("三人で行きました。", "四人で行きました。"), ("30人が来ました。", "40人が来ました。"), ("三十人が来ました。", "四十人が来ました。")]:
    r = j.classify_ja_asr_match(c, a, allow_reading_resolver=False)
    ja.append({"canonical": c, "asr": a, "class": r.classification, "should_pass": r.should_pass, "number_mismatches": r.protected.number_mismatches,
               "scg_exclusion": sj._scg_exclusion_reason(r, c, a)})
res["s1_ja_pairs"] = ja

# ---------------- (2) KP 2段目 ----------------
rows = [json.loads(l) for l in open(os.path.join(ROOT, "er011_output", "attempt_history.jsonl"), encoding="utf-8") if l.strip()]
kp = [r for r in rows if re.fullmatch(r"kp\d_en", r["segment_id"]) and r["timestamp"] >= "2026-09-01"]
seen, u = set(), []
for r in kp:
    k = (r["timestamp"], r["theme_id"], r["segment_id"], r.get("tts_attempts_this_call"))
    if k not in seen:
        seen.add(k)
        u.append(r)
res["kp_attempt_history_since_20260901"] = {"rows_raw": len(kp), "calls_dedup": len(u),
                                            "by_attempts_status": {"%s|%s" % k: v for k, v in collections.Counter((r.get("tts_attempts_this_call"), r.get("result_status")) for r in u).items()}}
g = collections.defaultdict(list)
for f in glob.glob(os.path.join(ROOT, "**", "attempts", "kp[1-5]_en_attempt*.json"), recursive=True):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    g[os.path.relpath(os.path.dirname(os.path.dirname(f)), ROOT) + "|" + d.get("segment_id", "")].append(d)
seq = collections.Counter()
el = []
for k, v in g.items():
    v.sort(key=lambda d: (d["attempt_number"], d.get("saved_at", "")))
    seq[(len(v), tuple(bool(d.get("verified")) for d in v))] += 1
    if len(v) >= 3:
        el.append({"group": k, "routes": [d["route"] for d in v], "verified": [bool(d.get("verified")) for d in v],
                   "classes": [d.get("audio_classification") for d in v], "saved": v[0].get("saved_at", "")[:10], "model": v[0].get("model")})
res["kp_saved_attempt_groups"] = {"n_groups": len(g), "sequences": {str(k): v for k, v in seq.items()}, "english_lock_stage_reached": sorted(el, key=lambda r: r["saved"])}

# ---------------- (3) JA leakage ----------------
c = collections.Counter()
for f in glob.glob(os.path.join(ROOT, "**", "attempts", "*_attempt*.json"), recursive=True):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        continue
    if d.get("language") != "ja" or d.get("model") != "gemini-3.8-flash-lite-tts":
        continue
    kind = "minimal" if "minimalfallback" in f else "standard"
    grp = "ab_trial(指示文同居の旧方式)" if "ab_trial" in f else "production_speech_metadata"
    leak = bool(re.search(r"(翻訳|言い換え).*(読み上げ|日本語のまま)|The message below", d.get("asr_text") or ""))
    c["%s|%s|n" % (grp, kind)] += 1
    if leak:
        c["%s|%s|LEAK" % (grp, kind)] += 1
    if d.get("length_ok") is False:
        c["%s|%s|length_not_ok" % (grp, kind)] += 1
res["ja_flash_lite_leakage"] = dict(c)

# ---------------- (4) 400 ----------------
KEY = "tried to generate text"
files = subprocess.run(["grep", "-rl", KEY, "--include=*.json", "--include=*.jsonl", "."], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout.split()
files = [f for f in files if "docs/pm" not in f.replace("\\", "/") and "node_modules" not in f and "er058_output" not in f]


def lists(o):
    if isinstance(o, list):
        if o and all(isinstance(x, dict) for x in o) and any("attempt" in x for x in o):
            yield o
        for x in o:
            yield from lists(x)
    elif isinstance(o, dict):
        for v in o.values():
            yield from lists(v)


c = collections.Counter()
for f in files:
    txt = open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore").read()
    try:
        objs = [json.loads(txt)] if f.endswith(".json") else [json.loads(l) for l in txt.splitlines() if l.strip()]
    except Exception:
        continue
    for o in objs:
        for lst in lists(o):
            for i, it in enumerate(lst):
                if KEY not in json.dumps(it, ensure_ascii=False):
                    continue
                c["400_events"] += 1
                ty = it.get("instruction_type")
                same = [x for x in lst[i + 1:] if x.get("instruction_type") == ty and x.get("attempt", 0) > it.get("attempt", 0)]
                if not same:
                    c["no_later_same_prompt_attempt"] += 1
                    continue
                n = same[0]
                if KEY in json.dumps(n, ensure_ascii=False):
                    c["next=400_again"] += 1
                elif n.get("verified") is True or (n.get("status") == "OK" and n.get("verified") in (None, True)):
                    c["next=generated_and_verified"] += 1
                elif n.get("status") == "OK":
                    c["next=generated_but_ASR_NG"] += 1
                else:
                    c["next=other_fail"] += 1
res["http400_same_prompt_retry"] = {"files": len(files), **dict(c)}
json.dump(res, open(os.path.join(OUT, "zero_yen_checks_05B.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: (v if k not in ("s1_en_number_mutations", "kp_saved_attempt_groups") else "...") for k, v in res.items()}, ensure_ascii=False, indent=1)[:3000])
