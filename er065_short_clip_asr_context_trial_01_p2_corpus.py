# -*- coding: utf-8 -*-
"""委任_03 D: 実データ(Production ASRの canonical/asr 対)から、語境界の子音連続での差分を抽出し、
(a) 境界種別ごとの base rate(境界数と、そこで綴り差が出た数)、(b) 差分の3分類(音韻説明可否+独立証拠)、
(c) 既存Production判定(classify_asr_match, telemetry追記は無効化)との比較 を出す。ASR/TTS呼出なし(費用0)。"""
import glob, json, os, sys, re, difflib, collections
sys.path.insert(0, ".")
import er065_short_clip_asr_context_trial_01_p2_phon as P
import er006_preprod_hardening_01_validation as val
import er011_b1_connected_speech_validator_01 as csv3
import er011_connected_speech_equivalence_layer_production_01 as eq
import er021_en_asr_semantic_equivalence_production_01 as _se
_se.append_telemetry_log = lambda *a, **k: None   # 共有telemetryへの追記を無効化(Production state保護)

OUT = "er065_output/short_clip_asr_context_trial_01/phase2"

def collect():
    items = {}
    def walk(d, src):
        if isinstance(d, dict):
            if isinstance(d.get("text"), str) and isinstance(d.get("asr_text"), str):
                items.setdefault((d["text"], d["asr_text"]), (src, d.get("path"), d.get("voice")))
                return
            for v in d.values(): walk(v, src)
        elif isinstance(d, list):
            for v in d: walk(v, src)
    for f in glob.glob("**/tts_generation_results.json", recursive=True):
        if ".venv" in f: continue
        try: walk(json.load(open(f, encoding="utf-8")), f)
        except Exception: pass
    # HR queue steps と er021 telemetry(先頭7155行)
    for l in open("er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl", encoding="utf-8"):
        try: d = json.loads(l)
        except Exception: continue
        c = d.get("canonical_text")
        for s in d.get("steps", []):
            if c and s.get("text"): items.setdefault((c, s["text"]), ("hr_queue:" + s.get("step", ""), d.get("wav_path"), None))
    for n, l in enumerate(open("er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl", encoding="utf-8")):
        if n >= 7155: break
        try: d = json.loads(l)
        except Exception: continue
        if d.get("canonical") and d.get("asr"): items.setdefault((d["canonical"], d["asr"]), ("er021_telemetry", None, None))
    return items

def is_en(s): return bool(re.search(r"[A-Za-z]", s)) and not re.search(r"[぀-ヿ一-鿿]", s)

def main():
    items = collect()
    pairs = [(c, a, v) for (c, a), v in items.items() if is_en(c) and is_en(a)]
    print("pairs", len(pairs))
    base = collections.defaultdict(lambda: {"n": 0, "affected": 0})
    inst = []
    seen_inst = set()
    for c, a, meta in pairs:
        cw, aw = P.tokens(c), P.tokens(a)
        cwc = re.findall(r"[A-Za-z0-9']+", c.replace("’", "'")); awc = re.findall(r"[A-Za-z0-9']+", a.replace("’", "'"))
        if len(cw) < 2 or len(cwc) != len(cw) or len(awc) != len(aw): continue
        sm = difflib.SequenceMatcher(a=cw, b=aw, autojunk=False)
        bad = set()
        regs = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                bad.update(range(i1, max(i2, i1 + 1)))
                regs.append((i1, i2, j1, j2))
        # base rate: 全境界(同一pair内の全語境界)
        phs = {}
        for k in range(len(cw) - 1):
            p1 = P.phones_all(cw[k]); p2 = P.phones_all(cw[k + 1])
            if not p1 or not p2: continue
            bt = P.boundary_type(p1[0][0][-1], p2[0][0][0])
            if not bt: continue
            base[bt]["n"] += 1
            if k in bad or (k + 1) in bad: base[bt]["affected"] += 1
        # 差分region(小さい差分のみ、1-3 canonical語)で境界環境を持つもの
        for (i1, i2, j1, j2) in regs:
            if not (1 <= i2 - i1 <= 3 and 0 <= j2 - j1 <= 4): continue
            lo, hi = max(0, i1 - 1), min(len(cw), i2 + 1)
            alo = max(0, j1 - 1); ahi = min(len(aw), j2 + 1)
            wc, wa = " ".join(cwc[lo:hi]), " ".join(awc[alo:ahi])
            key = (wc, wa)
            if key in seen_inst: continue
            ex = P.explain_diff(wc, wa)
            # 境界環境の有無: 変種に非ORIGがあるか(説明試行の有無)ではなく、region周辺に boundary_type があるか
            env = None
            pw = cw[i1 - 1] if i1 > 0 else None; nw = cw[i2] if i2 < len(cw) else None
            cands = []
            if nw:
                a1 = P.phones_all(cw[i2 - 1]); b1 = P.phones_all(nw)
                if a1 and b1: cands.append(("R", P.boundary_type(a1[0][0][-1], b1[0][0][0])))
            if pw:
                a1 = P.phones_all(pw); b1 = P.phones_all(cw[i1])
                if a1 and b1: cands.append(("L", P.boundary_type(a1[0][0][-1], b1[0][0][0])))
            for k in range(i1, i2 - 1):
                a1 = P.phones_all(cw[k]); b1 = P.phones_all(cw[k + 1])
                if a1 and b1: cands.append(("I", P.boundary_type(a1[0][0][-1], b1[0][0][0])))
            env = [x for x in cands if x[1]]
            if not env: continue
            seen_inst.add(key)
            try:
                pr = val.classify_asr_match(wc, wa, segment_id="full_story_part1")
                prod = pr.classification
            except Exception as e:
                prod = "ERR:" + type(e).__name__
            cs = csv3.classify_connected_speech(wc, wa)["new_judgment"]
            eqj = eq.classify_connected_speech_equivalence(wc, wa)["layer_judgment"]
            inst.append({"canonical_window": wc, "asr_window": wa, "env": env, "src": meta[0], "wav": meta[1],
                         "phon_verdict": ex["verdict"], "three_way": P.three_way(ex)["class"], "prod_classification": prod,
                         "prod_cs_validator": cs, "prod_equivalence_cheap": eqj, "region_rule": [r.get("rule") for r in ex["regions"]]})
    json.dump({"base_rate": base, "n_pairs": len(pairs)}, open(OUT + "/d_base_rate_02.json", "w"), indent=1)
    json.dump(inst, open(OUT + "/d_instances_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("base rate:", {k: v for k, v in base.items()})
    print("instances:", len(inst))
    print(collections.Counter(i["phon_verdict"] for i in inst))
    print(collections.Counter((i["phon_verdict"], i["prod_classification"]) for i in inst).most_common(30))

main()
