# PNMH Trial 委任_04 層A/B/C集計 (API 0)。入力: er093_output/pnmh_trial_01/asr_raw.jsonl, dataset_manifest.json, paid_calls.jsonl, tts_log.jsonl
import sys, os, json, re, difflib, time, itertools, collections
import er093_pnmh_trial_01_core as C
val, P, pronouncing = C.val, C.P, C.P.pronouncing
OUT = "er093_output/pnmh_trial_01"
man = json.load(open(f"{OUT}/dataset_manifest.json", encoding="utf8"))
raw = [json.loads(l) for l in open(f"{OUT}/asr_raw.jsonl", encoding="utf8")]
M = {m["clip_id"]: m for m in man}

def strip(p): return re.sub(r"\d", "", p)
def phon_variants(toks):
    L = []
    for t in toks:
        ps = pronouncing.phones_for_word(t)
        if not ps: return None
        L.append({tuple(strip(p).split()) for p in ps})
    n = 1
    for s in L: n *= len(s)
    if n > 256: return None
    return {tuple(x for part in c for x in part) for c in itertools.product(*L)}

def focal(canonical, text):
    """canonical(byUs入り)と転写のtoken差分から focal span(転写側tokens, canonical側tokens)を返す。LINEの大小文字・句読点は tokenizeが吸収。"""
    ct, at = val.tokenize(canonical), val.tokenize(text)
    sm = difflib.SequenceMatcher(None, ct, at, autojunk=False)
    cs, as_ = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal": continue
        cs += ct[i1:i2]; as_ += at[j1:j2]
    return cs, as_, ct, at

def spoken_tokens(m): return val.tokenize(m["spoken_token"].replace("-", " "))

def layer_a(m, text):
    """A1 focal spanの綴り一致(despace小文字)、A2 音素一致(spoken tokenとCMU・ストレス無視)、A3 garbage(辞書外かつ非一致)、A4 多語化。
    focal region = spoken text(TTS入力)と転写のtoken差分に基づくのではなく、転写内で carrier の前後アンカー('launched'/'with' と ','/'an'/'.'直前)に挟まれたtokens。"""
    ct = val.tokenize(m["canonical"]); at = val.tokenize(text)
    # byus位置の前後アンカー
    k = ct.index("byus"); pre = ct[k - 1]; post = ct[k + 1] if k + 1 < len(ct) else None
    try:
        i = len(at) - 1 - at[::-1].index(pre) if False else at.index(pre)
    except ValueError:
        return {"focal": None, "A1": False, "A2": False, "A3": True, "A4": False, "note": "anchor_missing"}
    j = at.index(post, i + 1) if post and post in at[i + 1:] else len(at)
    span = at[i + 1:j]
    sp = spoken_tokens(m)
    despace = lambda t: "".join(t)
    vs, va = phon_variants(sp), phon_variants(span) if span else None
    a1 = despace(span) == despace(sp)
    a2 = bool(vs and va and (vs & va))
    oov = (va is None) and bool(span)
    return {"focal": " ".join(span), "A1": a1, "A2": a2, "A3": bool(oov or (not a2 and not span)), "A4": len(span) >= 2,
            "A2_vs_byus": bool(va and phon_variants(["byus"]) and (va & phon_variants(["byus"])))}

# ---- 判定
rows = []
t_cur = t_v3 = 0.0; n_t = 0
for r in raw:
    m = M[r["clip_id"]]; text = r["text"]
    a = layer_a(m, text)
    t0 = time.perf_counter(); cur = C.judge(m["canonical"], text, "current"); t1 = time.perf_counter(); v3 = C.judge(m["canonical"], text, "v3"); t2 = time.perf_counter()
    t_cur += t1 - t0; t_v3 += t2 - t1; n_t += 1
    rows.append({"clip_id": r["clip_id"], "fid": m["fid"], "label_S1": m["label_S1"], "voice": m["voice"], "spoken_token": m["spoken_token"], "engine": r["method"], "rep": r["rep"],
                 "text": text, "A": a, "B_cls": cur[0], "B_final": cur[1], "C_cls": v3[0], "C_final": v3[1],
                 "rescued": (not C.is_pass(cur[1])) and C.is_pass(v3[1]), "new_ng": C.is_pass(cur[1]) and not C.is_pass(v3[1])})
timing = {"n_judgements": n_t, "current_ms_per_judge": round(t_cur / n_t * 1000, 3), "v3_ms_per_judge": round(t_v3 / n_t * 1000, 3)}

# ---- クリップ単位(rep1)のcascade
def pick(cid, eng, rep=1):
    for x in rows:
        if x["clip_id"] == cid and x["engine"] == eng and x["rep"] == rep: return x
clips = []
for m in man:
    o, z = pick(m["clip_id"], "openai"), pick(m["clip_id"], "azure")
    cur_casc = C.is_pass(o["B_final"]) or C.is_pass(z["B_final"])      # Production現行: Primary PASSなら終了、不可ならSecondary許容集合(M1は未再現)
    v3_casc = C.is_pass(o["C_final"]) or C.is_pass(z["C_final"])
    cur_both = C.is_pass(o["B_final"]) and C.is_pass(z["B_final"])      # 感度分析(KP両方PASS必須の読み)
    v3_both = C.is_pass(o["C_final"]) and C.is_pass(z["C_final"])
    clips.append({"clip_id": m["clip_id"], "fid": m["fid"], "label": m["label_S1"], "voice": m["voice"], "spoken": m["spoken_token"],
                  "openai_text_focal": o["A"]["focal"], "azure_text_focal": z["A"]["focal"],
                  "A_openai": {k: o["A"][k] for k in ("A1", "A2", "A3", "A4")}, "A_azure": {k: z["A"][k] for k in ("A1", "A2", "A3", "A4")},
                  "B_openai": o["B_final"], "B_azure": z["B_final"], "C_openai": o["C_final"], "C_azure": z["C_final"],
                  "cascade_current": cur_casc, "cascade_v3": v3_casc, "both_current": cur_both, "both_v3": v3_both,
                  "rescued_primary": o["rescued"], "rescued_secondary": z["rescued"], "rescued_cascade": (not cur_casc) and v3_casc,
                  "new_ng_cascade": cur_casc and not v3_casc,
                  "tts_autocorrect_suspect": (m["label_S1"].startswith("NEG") and all(x["A"].get("A2_vs_byus") for x in (o, z)))})
# ---- A5 反復
a5 = []
for cid in sorted({x["clip_id"] for x in rows if x["rep"] == 2}):
    for eng in ("openai", "azure"):
        x1, x2 = pick(cid, eng, 1), pick(cid, eng, 2)
        a5.append({"clip_id": cid, "engine": eng, "text1": x1["text"], "text2": x2["text"], "same_text": x1["text"] == x2["text"],
                   "judge1_v3": x1["C_final"], "judge2_v3": x2["C_final"], "judge1_cur": x1["B_final"], "judge2_cur": x2["B_final"],
                   "flip_v3": C.is_pass(x1["C_final"]) != C.is_pass(x2["C_final"]), "flip_cur": C.is_pass(x1["B_final"]) != C.is_pass(x2["B_final"])})
# ---- 集計
def summ(sel):
    return {"n": len(sel), "cur_pass": sum(1 for c in sel if c["cascade_current"]), "v3_pass": sum(1 for c in sel if c["cascade_v3"]),
            "rescued": sum(1 for c in sel if c["rescued_cascade"]), "new_ng": sum(1 for c in sel if c["new_ng_cascade"])}
pos = [c for c in clips if c["label"] == "POS"]; neg = [c for c in clips if c["label"].startswith("NEG")]; unl = [c for c in clips if c["label"].startswith("UNLAB")]
bi = [c for c in clips if c["fid"] == "BI"]; neg_nobi = [c for c in neg if c["fid"] != "BI"]
suspect = [c["clip_id"] for c in clips if c["tts_autocorrect_suspect"]]
per_engine = {}
for eng in ("openai", "azure"):
    rr = [x for x in rows if x["engine"] == eng and x["rep"] == 1]
    per_engine[eng] = {
        "n": len(rr), "A4_multiword_rate": sum(1 for x in rr if x["A"]["A4"]), "A1_spelling_match": sum(1 for x in rr if x["A"]["A1"]), "A2_phoneme_match": sum(1 for x in rr if x["A"]["A2"]),
        "A3_garbage": sum(1 for x in rr if x["A"]["A3"]),
        "layerB_phoneme_match_not_spelling": sum(1 for x in rr if x["A"]["A2"] and not x["A"]["A1"]),
        "layerB_those_cur_pass": sum(1 for x in rr if x["A"]["A2"] and not x["A"]["A1"] and C.is_pass(x["B_final"])),
        "layerB_those_v3_pass": sum(1 for x in rr if x["A"]["A2"] and not x["A"]["A1"] and C.is_pass(x["C_final"])),
        "layerB_phoneme_mismatch_n": sum(1 for x in rr if not x["A"]["A2"]),
        "layerB_phoneme_mismatch_v3_pass": sum(1 for x in rr if not x["A"]["A2"] and C.is_pass(x["C_final"])),
        "layerB_phoneme_mismatch_cur_pass": sum(1 for x in rr if not x["A"]["A2"] and C.is_pass(x["B_final"])),
        "rescued": sum(1 for x in rr if x["rescued"]), "new_ng": sum(1 for x in rr if x["new_ng"]),
    }
cost = collections.defaultdict(float)
for l in open(f"{OUT}/paid_calls.jsonl", encoding="utf8"):
    p = json.loads(l); cost[p["method"]] += p["jpy"]
tts_cost = 0.0; tts_n = 0; tts_rows = []
for l in open(f"{OUT}/tts_raw_usage_log.jsonl", encoding="utf8"):
    p = json.loads(l)
    if p.get("provider", "").startswith("gemini"):
        jpy = ((p.get("input_tokens") or 0) * 0.5 + (p.get("output_tokens") or 0) * 6.0) / 1e6 * 160.0   # pricing_snapshot.json gemini-3.8-flash-lite-tts Standard $0.5/$6.0 per M
        tts_cost += jpy; tts_n += 1; tts_rows.append({"voice": p.get("voice"), "mode": p.get("tts_execution_mode"), "in": p.get("input_tokens"), "out": p.get("output_tokens"), "jpy": round(jpy, 5), "model": p.get("model_id")})
res = {"timing": timing, "clips": clips, "rows": rows, "a5": a5,
       "summary": {"POS": summ(pos), "NEG(BI除く)": summ(neg_nobi), "BI": summ(bi), "UNLABELED_F0": summ(unl)},
       "tts_autocorrect_suspect": suspect, "per_engine_layers_rep1": per_engine,
       "cost": {"asr_openai_jpy": round(cost["openai"], 4), "asr_azure_jpy": round(cost["azure"], 4), "tts_jpy": round(tts_cost, 4), "tts_n": tts_n,
                "total_jpy": round(cost["openai"] + cost["azure"] + tts_cost, 4), "tts_rows": tts_rows}}
json.dump(res, open(f"{OUT}/layer_results.json", "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=1)
print(json.dumps(res["summary"], ensure_ascii=False)); print(json.dumps(per_engine, ensure_ascii=False, indent=0)); print(json.dumps(res["cost"], ensure_ascii=False)); print(timing)
for c in clips: print(c["clip_id"], c["label"][:6], "| O:", c["openai_text_focal"], c["B_openai"][:22], "->", c["C_openai"][:30], "| Z:", c["azure_text_focal"], c["B_azure"][:22], "->", c["C_azure"][:30], "| casc", c["cascade_current"], c["cascade_v3"], "both", c["both_current"], c["both_v3"], "susp" if c["tts_autocorrect_suspect"] else "")
for a in a5: print(a["clip_id"], a["engine"], a["same_text"], a["flip_v3"], a["flip_cur"], "|", a["text1"][26:50], "|", a["text2"][26:50])

# ---- 既存wav(run_byus_01)の保存転写(再ASRなし・追加費用0): byUs周辺で綴りが異なる転写の層A/B/C
pairs = [json.loads(l) for l in open(os.path.join(C.PLAN, "pairs_02.jsonl"), encoding="utf8")]
ex = []
seen = set()
for i, p in enumerate(pairs):
    if "run_byus_01" not in " ".join(p["sources"]) and "byus" not in " ".join(val.tokenize(p["canonical"])): continue
    if "byus" not in val.tokenize(p["canonical"]): continue
    cs, as_, ct, at = focal(p["canonical"], p["asr"])
    key = (p["canonical"][:60], " ".join(as_))
    if key in seen: continue
    seen.add(key)
    cur = C.judge(p["canonical"], p["asr"], "current"); v3 = C.judge(p["canonical"], p["asr"], "v3")
    vb = phon_variants(["byus"]); vf = phon_variants([t for t in as_ if t not in ("the", "a")] or ["_"]) if as_ else None
    ex.append({"idx": i, "src": p["sources"][0].split("/")[-1][:60] + "|" + p["sources"][0][-40:], "canon_head": p["canonical"][:70], "diff_canon": " ".join(cs), "diff_asr": " ".join(as_),
               "byus_span_phoneme_eq": bool(vf and vb and (vf & vb)), "B": cur[1], "B_cls": cur[0], "C": v3[1], "C_cls": v3[0], "rescued": (not C.is_pass(cur[1])) and C.is_pass(v3[1])})
res["existing_stored_transcripts"] = ex
json.dump(res, open(f"{OUT}/layer_results.json", "w", encoding="utf8", newline=chr(10)), ensure_ascii=False, indent=1)
print("existing", len(ex))
for e in ex: print(e["idx"], "|", e["diff_canon"], "->", e["diff_asr"], "|", e["B"][:14], "->", e["C"][:26], "| ph_eq", e["byus_span_phoneme_eq"])
