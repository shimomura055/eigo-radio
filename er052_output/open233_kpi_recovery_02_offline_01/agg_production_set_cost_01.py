"""最新Production仕様 Standard+Advanced 1セットの実測原価集計(委任_16、¥0、API無し)。
raw_usage_log.jsonl(er019_output配下)の実測tokensに価格表(er005_output/cost_baseline_01/pricing_snapshot.json、USD_JPY=160)を適用。
ログに無い項目は集計しない(推計で埋めない)。advanced/standardのwriter/check分離は入力token>=3500=check(分類ヒューリスティック=推計)。"""
import glob, json, os, statistics, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
JPY = 160.0
PR = json.load(open(ROOT + "/er005_output/cost_baseline_01/pricing_snapshot.json", encoding="utf8"))["prices"]
def pr(provider, model, meter, tier="Standard"):
    for p in PR:
        if p["provider"] == provider and p["meter"] == meter and p.get("tier", "Standard") == tier and (model is None or p["model"] == model):
            return p["price"]
    return None
LUNA6 = (0.10, 0.01, 0.50)  # CURRENT_SPEC 2330行(gpt-6-luna Standard)
def cost(r):
    """USD->JPY。失敗call=0。戻り値(円, 区分)"""
    if not r.get("success", True): return 0.0
    m = r.get("model_id"); it = r.get("input_tokens") or 0; ct = r.get("cached_input_tokens") or 0; ot = r.get("output_tokens") or 0
    if m == "gpt-5.6-luna": a, b, c = 0.20, 0.02, 1.20
    elif m == "gpt-6-luna": a, b, c = LUNA6
    elif m == "gpt-5.6-sol": a, b, c = 5.0, 0.5, 30.0
    elif m == "gpt-4o-mini-transcribe": a, b, c = 1.25, 1.25, 5.0
    elif m and m.startswith("gemini"):
        tier = "Batch" if r.get("tts_execution_mode") == "BATCH" else "Standard"
        a = pr("gemini", m, "input_tokens", tier); c = pr("gemini", m, "output_tokens", tier); b = a
        if a is None: return None
    elif m == "azure-speech-stt":
        return (r.get("audio_duration_submitted_seconds") or 0) / 3600 * 1.0 * JPY
    else: return None
    usd = (max(it - ct, 0) * a + ct * b + ot * c) / 1e6 + (r.get("web_search_call_count") or 0) / 1000 * 10.0
    return usd * JPY
def cat(r):
    s = r.get("stage") or "unlabeled"; m = r.get("model_id") or ""
    if m.startswith("gemini"): return "TTS(" + ("Batch" if r.get("tts_execution_mode") == "BATCH" else "Standard同期") + ")"
    if m in ("gpt-4o-mini-transcribe", "azure-speech-stt"): return "ASR"
    if s in ("research",): return "Research"
    if s == "ledger": return "Ledger"
    if s.startswith("storyline"): return "Storyline/Writer前段"
    if s in ("ja_original", "ja_r1", "ja_r2"): return "JA生成(ja_original/r1/r2)"
    if s.startswith("ja_"): return "JA検査(check/must_fix/retry)"
    if s in ("advanced", "standard"):
        return s.capitalize() + (":英語Stage1相当check(推計)" if (r.get("input_tokens") or 0) >= 3500 else ":英語writer/再生成(推計)")
    if "scaffold" in s: return "scaffold"
    return "other:" + s
rows = []
for f in sorted(glob.glob(ROOT + "/er019_output/**/raw_usage_log.jsonl", recursive=True)):
    cs = collections.defaultdict(float); n = collections.Counter(); unk = 0
    for l in open(f, encoding="utf8"):
        try: r = json.loads(l)
        except Exception: continue
        c = cost(r)
        if c is None: unk += 1; c = 0.0
        k = cat(r); cs[k] += c; n[k] += 1
    rows.append({"file": os.path.relpath(f, ROOT).replace("\\", "/"), "cats": {k: round(v, 3) for k, v in cs.items()}, "calls": dict(n), "unpriced_calls": unk, "total": round(sum(cs.values()), 3)})
json.dump(rows, open(os.path.join(os.path.dirname(__file__), "agg_production_set_cost_01.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
allc = collections.defaultdict(list)
for r in rows:
    for k, v in r["cats"].items(): allc[k].append(v)
lines = ["# 最新Production Standard+Advanced原価の実測集計(委任_16、¥0、raw_usage_log、USD_JPY=160)", "", "## run別(円、ログ内実測tokens×価格表。TTS/ASRはログのmodel_id別)", ""]
for r in rows:
    lines.append("- " + r["file"] + " total=" + str(r["total"]) + " " + json.dumps(r["cats"], ensure_ascii=False) + (" unpriced=" + str(r["unpriced_calls"]) if r["unpriced_calls"] else ""))
lines += ["", "## 区分別(出現runのみ n/mean/median/max)", ""]
for k, v in sorted(allc.items()):
    lines.append("- %s n=%d mean=%.3f median=%.3f max=%.3f" % (k, len(v), statistics.mean(v), statistics.median(v), max(v)))
open(os.path.join(os.path.dirname(__file__), "agg_production_set_cost_01.md"), "w", encoding="utf8").write("\n".join(lines))
print("\n".join(lines))

# ---- 1セット合成(部品別実測の組合せ。単一runに全部は揃わない=ログ上の制約) ----
by = {r["file"]: r for r in rows}
def g(sub, *keys):
    rr = [v for k, v in by.items() if sub in k][0]
    return sum(rr["cats"].get(x, 0) for x in keys)
def luna_checks(sub, min_in=5000):
    """refresh_e2e run(stage=None)の入力>=5000tok call=英語deviation check(推計)の円(5.6-luna実額)と6-luna換算"""
    f = [k for k in by if sub in k][0]; a = b = 0.0; n = 0
    for l in open(ROOT + "/" + f, encoding="utf8"):
        r = json.loads(l)
        if r.get("stage") is None and (r.get("input_tokens") or 0) >= min_in:
            it, ot = r["input_tokens"], r["output_tokens"]; n += 1
            a += (it * 0.20 + ot * 1.20) / 1e6 * JPY; b += (it * 0.10 + ot * 0.50) / 1e6 * JPY
    return n, round(a, 3), round(b, 3)
RL = g("family_x_b3_production_wiring_01/run_01/raw", "Research", "Ledger")
ST = g("family_x_b3_production_wiring_01/run_01/raw", "Storyline/Writer前段")
comp = {}
for name, txt, aud in (("hormuz", "refresh_e2e_01/hormuz/run_03", "hormuz__run_06_flashlite_full_kp"), ("meta", "refresh_e2e_01/meta/run_03", "audio_production_wiring_01/meta__run_03")):
    ja = g(txt + "/raw", "JA生成(ja_original/r1/r2)", "JA検査(check/must_fix/retry)"); en = g(txt + "/raw", "other:unlabeled")
    tts = g(aud, "TTS(Standard同期)"); asr = g(aud, "ASR"); oth = g(aud, "other:tts", "other:tts_confirmation"); sc = g(aud, "scaffold")
    comp[name] = {"Research+Ledger(b3_production_wiring run_01 n=1、借用)": round(RL, 3), "Storyline(同run_01)": round(ST if name == "hormuz" else 0, 3), "JA生成+JA検査(" + txt + ")": round(ja, 3), "英語Std+Adv(writer+check、" + txt + ")": round(en, 3),
                  "scaffold(audio run)": round(sc, 3), "TTS(Standard同期、flash-lite)": round(tts, 3), "ASR": round(asr, 3), "TTS周辺LLM": round(oth, 3), "英語deviation check call数/5.6実額/6-luna換算": luna_checks(txt)}
    comp[name]["合計(Standard同期)"] = round(sum(v for k, v in comp[name].items() if isinstance(v, float)), 3)
    comp[name]["合計(TTS=Batch、推計=TTS半額)"] = round(comp[name]["合計(Standard同期)"] - tts / 2, 3)
json.dump(comp, open(os.path.join(os.path.dirname(__file__), "agg_production_set_cost_01_composite.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
with open(os.path.join(os.path.dirname(__file__), "agg_production_set_cost_01.md"), "a", encoding="utf8") as fh:
    fh.write("\n\n## 1セット合成(部品別実測の組合せ)\n\n```json\n" + json.dumps(comp, ensure_ascii=False, indent=1) + "\n```\n")
print(json.dumps(comp, ensure_ascii=False, indent=1))
