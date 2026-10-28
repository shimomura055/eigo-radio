# JA-ASR-FALSE-NG-ROOT-FIX-02 委任_03 統合評価ハーネス(API 0・socket guard・決定的)。事前登録=PREREGISTERED_03.md(+補遺)。
# 再現: PYTHONUTF8=1 .venv/Scripts/python.exe -X utf8 docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/eval_unified_03.py [out_json_path]
import collections, hashlib, json, os, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02")
import eval_unified_01 as U1
import eval_unified_02 as U2E
import proto_unified_03 as U
import proto_unified_02 as UP2
import eval_common_02 as E
import er007_ja_secondary_asr_01 as sec
import er078_asr_unified_judge_01 as uj

OUT = "docs/research/JA-ASR-FALSE-NG-ROOT-FIX-02/"
J = U1.J
MOON = U1.MOON
NEG_SHA_PREREG = U2E.NEG_SHA_PREREG
F = U.Flags
CFG = {"L0": F(), "L1": F(True), "L1(R1off)": F(True, r1=False), "L1+L2": F(True, True), "L1+L2+L3": F(True, True, True), "L1+L2+L3(R1off)": F(True, True, True, r1=False)}
FIN_ON, FIN_OFF = "L1+L2+L3", "L1+L2+L3(R1off)"
PASSCAT = ("PASS", "PASS_W_PROD", "PASS_W_NEW")

# ---- judge memo(同一入力の再判定を避ける。結果は決定的) ----
_memo = {}
_real_judge = U.judge


def _cached_judge(canon, prim, sec_text, wav, flags=F(), *, retry_mode=False, phrase_list_hash=""):
    k = (canon, prim, sec_text, flags, retry_mode, phrase_list_hash)
    if k not in _memo:
        _memo[k] = _real_judge(canon, prim, sec_text, wav, flags, retry_mode=retry_mode, phrase_list_hash=phrase_list_hash)
    return _memo[k]


U.judge = _cached_judge


def slim(r):
    return {"cat": r["cat"], "reason": r["reason"], "route": r["route"], "labels": r["warning_labels"], "layers": [a.get("layer") for a in r.get("layers", [])],
            "blocked": r.get("blocked", False), "needs_azure": r.get("needs_new_azure_call", False), "beta_blocked_by": r.get("beta_blocked_by")}


def judge_cfgs(canon, prim, sec_text, wav):
    return {n: slim(U.judge(canon, prim, sec_text, wav, f)) for n, f in CFG.items()}


def dist(canon, draws, sec_text, wav, flags, n):
    """全(first, extras)組合せの等重み分布。retry起因の誤PASS(N=1ならNG→合意でPASS_W_NEW)・BoN起因の件数も返す。"""
    cats, bon = collections.Counter(), collections.Counter()
    retry_fired = 0
    retry_induced, bon_induced, hr_combos = [], [], []
    for first, ex in U.combos(len(draws), n):
        r = U.consensus(canon, draws, sec_text, wav, flags, first, ex, n_max=3)
        cats[r["cat"]] += 1
        retry_fired += int(r["retry_fired"])
        b = U.best_of_n_ref(canon, draws, sec_text, wav, flags, first, ex)
        bon[b] += 1
        if n > 1:
            r1 = U.consensus(canon, draws, sec_text, wav, flags, first, (), n_max=3)
            if r["cat"] in PASSCAT and r1["cat"] == "NG":
                retry_induced.append({"first": first, "extras": list(ex), "route": r["route"]})
            if b in PASSCAT and r1["cat"] == "NG":
                bon_induced.append({"first": first, "extras": list(ex)})
            if r["cat"] == "HR":
                hr_combos.append({"first": first, "extras": list(ex), "contra": r.get("contra_idx")})
    return {"n_combos": sum(cats.values()), "cats": dict(cats), "bon": dict(bon), "retry_fired": retry_fired, "retry_induced_pass": retry_induced, "bon_induced_pass": bon_induced, "hr_combos": hr_combos}


def stored_order(canon, draws, sec_text, wav, flags, n):
    """記録順(参考): first=0、extras=1..n-1。"""
    r = U.consensus(canon, draws, sec_text, wav, flags, 0, tuple(range(1, n)), n_max=3)
    return {"cat": r["cat"], "reason": r.get("reason"), "route": r.get("route"), "retry_fired": r["retry_fired"], "extra_draws": r["extra_openai_draws"], "labels": r["warning_labels"],
            "retry_block": r.get("retry_block"), "contra": r.get("contradictions"), "passing_idx": r.get("passing_idx")}


def n3_cases():
    d = json.load(open(OUT + "n3_redraw_02.json", encoding="utf8"))
    clips = {c["id"]: c for c in json.load(open(J + "n3_clips_01.json", encoding="utf8"))}
    az, stored = {}, {}
    for l in open(J + "phase3_run/usage_log.jsonl", encoding="utf8"):
        r = json.loads(l)
        if r["stage"] == "N3_asr":
            az[r["item"]] = r["azure_text"]
            stored[r["item"]] = r["openai_text"]
    new = collections.defaultdict(list)
    ts = collections.defaultdict(list)
    for x in d["draws"]:
        new[x["id"]].append((x["draw"], x["text"]))
        ts[x["id"]].append(x["ts"])
    return clips, az, stored, {k: [t for _, t in sorted(v)] for k, v in new.items()}, ts


def main():
    outp = sys.argv[1] if len(sys.argv) > 1 else OUT + "eval_unified_03.out.json"
    E.api0_guard_on()
    dwav = E.dummy_wav()
    res = {"production_sha256": {f: hashlib.sha256(open(f, "rb").read()).hexdigest()[:16] for f in ("er007_ja_secondary_asr_01.py", "er078_asr_unified_judge_01.py", "er078_asr_value_guard_01.py", "er007_ja_asr_validator_01.py")},
           "head_consts": {"READING_MATCH_FINAL_GATE": uj.READING_MATCH_FINAL_GATE, "JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED": sec.JA_SECONDARY_VALUE_EQUIVALENCE_ENABLED},
           "versions": {"layer": U.LAYER_VERSION, "rule": U.RULE_VERSION}, "new_warn": U.NEW_WARN, "configs": list(CFG)}
    # ---- コーパス(Phase 1/2と同一 + L3_NEG/POS + N3_redraw) ----
    base = U1.corpus()
    neg_rows = [[c["group"], c["tag"], c["canon"], c["primary"], sn, st] for c in base if c["truth"] == "NEG" for sn, st in c["scen"].items()]
    neg_sha = hashlib.sha256(json.dumps(sorted(neg_rows), ensure_ascii=False).encode()).hexdigest()
    assert neg_sha == NEG_SHA_PREREG, neg_sha
    res["neg_set"] = {"n": len(neg_rows), "sha256": neg_sha}
    n3c, _, _, _ = U2E.n3_redraw_cases()
    corpus = base + U2E.l3_cases() + n3c
    rows = []
    for c in corpus:
        for sn, st in c["scen"].items():
            rows.append({"group": c["group"], "truth": c["truth"], "tag": c["tag"], "canon": c["canon"], "primary": c["primary"], "scenario": sn, "secondary": st,
                         "n3": c.get("n3"), "res": judge_cfgs(c["canon"], c["primary"], st, dwav)})
    res["rows"] = rows
    p1 = json.load(open(OUT + "eval_unified_01.out.json", encoding="utf8"))["rows"]
    key = lambda r: (r["group"], r["tag"], r["canon"], r["primary"], r["scenario"], r["secondary"])
    cur = {key(r): r for r in rows}
    mis = []
    for r in p1:
        c = cur[key(r)]["res"]["L0"]
        if (c["cat"] != "NG") != (r["res"]["M0"]["cat"] != "NG") or (c["cat"] == "NG" and c["reason"] != r["res"]["M0"]["reason"]):
            mis.append(list(key(r))[:3])
    res["parity"] = {"n_compared": len(p1), "L0_vs_M0_mismatch": len(mis), "examples": mis[:10]}
    # ---- 正例6音声 ----
    pos = []
    for p in U1.load_positives():
        draws = [t for _, t in p["openai"]]
        tags = [t for t, _ in p["openai"]]
        a0 = p["azure"][0][1] if p["azure"] else None
        per_draw = [dict(tag=tg, text=t, res=judge_cfgs(MOON, t, a0, dwav)) for tg, t in zip(tags, draws)]
        ent = {"run": p["run"], "attempt": p["attempt"], "sha16": p["sha16"], "tags": tags, "draws": draws, "azure": p["azure"], "whisper_local": p["whisper_local"], "per_draw": per_draw, "cons": {}}
        for fn in (FIN_ON, FIN_OFF):
            for n in (1, 2, 3):
                ent["cons"][f"{fn}|N{n}"] = dist(MOON, draws, a0, dwav, CFG[fn], n)
                ent["cons"][f"{fn}|N{n}|stored_order"] = stored_order(MOON, draws, a0, dwav, CFG[fn], n)
        ent["hr_cand"] = UP2.hr_candidate(MOON, [(t, a0) for t in draws])
        pos.append(ent)
    res["positives"] = pos
    # ---- 正例拡張4wav(新規draw) ----
    pe = json.load(open(OUT + "pos_ext_03.json", encoding="utf8"))["items"]
    rd = json.load(open(OUT + "redraw_03.json", encoding="utf8"))
    ext = []
    for it in pe:
        new = [x for x in rd["draws"] if x["wav_sha256"] == it["sha256"]]
        draws = [it["stored_openai"]] + [x["text"] for x in sorted(new, key=lambda x: x["draw"])]
        tags = ["stored"] + [f"draw{x['draw']}" for x in sorted(new, key=lambda x: x["draw"])]
        sc = it["azure_stored"]
        canon = it["canonical"]
        per_draw = [dict(tag=tg, text=t, res=judge_cfgs(canon, t, sc, dwav)) for tg, t in zip(tags, draws)]
        e = {"run": it["run"], "seg": it["seg"], "sha16": it["sha256"][:16], "dur_s": it["dur_s"], "canonical": canon, "azure": sc, "tags": tags, "draws": draws, "same_sha_as": it["same_sha_as"],
             "ts": [x["ts"] for x in new], "per_draw": per_draw, "cons": {}}
        for fn in (FIN_ON, FIN_OFF):
            for n in (1, 2, 3):
                e["cons"][f"{fn}|N{n}"] = dist(canon, draws, sc, dwav, CFG[fn], n)
        e["hr_cand"] = UP2.hr_candidate(canon, [(t, sc) for t in draws])
        ext.append(e)
    res["pos_ext"] = ext
    # ---- 負例N3 (stored + 新4 draw = 5 draws) ----
    clips, az, stored, new, ts = n3_cases()
    n3 = {}
    for cid in sorted(clips):
        draws = [stored[cid]] + new[cid]
        canon = clips[cid]["canonical"]
        ent = {"type": clips[cid]["type"], "tts_input": clips[cid]["tts_input"], "canon": canon, "azure": az[cid], "draws": draws, "ts": ts[cid], "scn": {}}
        for scn, sectxt in (("real", az[cid]), ("S_canon", canon)):
            for fn in ("L0", FIN_ON, FIN_OFF):
                for n in (1, 2, 3):
                    ent["scn"][f"{scn}|{fn}|N{n}"] = dist(canon, draws, sectxt, dwav, CFG[fn], n)
        ent["hr_cand"] = UP2.hr_candidate(canon, [(t, az[cid]) for t in draws])
        n3[cid] = ent
    res["n3"] = n3
    # ---- run単位(参考) ----
    runs = {}
    for run in ("run_ms_03", "run_reselect_01"):
        ps = [p for p in pos if p["run"] == run]
        for fn in (FIN_ON, FIN_OFF):
            for n in (1, 2, 3):
                seq = []
                done = None
                extra = 0
                for p in sorted(ps, key=lambda x: x["attempt"]):
                    s = p["cons"][f"{fn}|N{n}|stored_order"]
                    extra += s["extra_draws"]
                    seq.append({"attempt": p["attempt"], "cat": s["cat"]})
                    if s["cat"] in PASSCAT:
                        done = p["attempt"]; break
                    if s["cat"] == "HR":
                        done = f"HR@{p['attempt']}"; break
                runs[f"{run}|{fn}|N{n}"] = {"done_at": done, "seq": seq, "extra_openai_draws": extra}
        l0 = []
        for p in sorted(ps, key=lambda x: x["attempt"]):
            l0.append({"attempt": p["attempt"], "cat": p["per_draw"][0]["res"]["L0"]["cat"]})
        runs[f"{run}|L0"] = {"seq": l0}
    res["run_level"] = runs
    E.api0_guard_off()
    s = json.dumps(res, ensure_ascii=False, sort_keys=True, indent=1)
    open(outp, "w", encoding="utf-8", newline="\n").write(s)
    print("sha256", hashlib.sha256(s.encode("utf-8")).hexdigest(), "rows", len(rows), "L0_vs_M0_mismatch", res["parity"]["L0_vs_M0_mismatch"])


if __name__ == "__main__":
    main()
