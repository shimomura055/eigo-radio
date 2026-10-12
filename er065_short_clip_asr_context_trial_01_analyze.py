# -*- coding: utf-8 -*-
"""Trial結果のオフライン集計(無料)。results_01_*.jsonlを読み、target領域の転写・Production判定(classify_asr_match)・
文脈効果・非決定性・false accept・防止条件を集計して analysis_01.json / analysis_tables_01.md を出力する。
Production判定関数は読取のみで呼び、telemetry書込はno-op化(+write guardでtrial dir外書込を遮断)。"""
from __future__ import annotations

import collections
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, ".")
import er065_short_clip_asr_context_trial_01_lib as L

OUT = sys.argv[1] if len(sys.argv) > 1 else "er065_output/short_clip_asr_context_trial_01"
L.install_write_guard([OUT])
import er006_preprod_hardening_01_validation as val  # noqa: E402

val.semantic_equivalence.append_telemetry_log = lambda *a, **k: None  # telemetry追記を無効化(Production state保護)

manifests = {}
for p in glob.glob(OUT + "/conditions_manifest_*_01.json"):
    for c in json.load(open(p, encoding="utf-8"))["conditions"]:
        manifests[c["cond_id"]] = c

recs = []
for p in sorted(glob.glob(OUT + "/results_01_*_*.jsonl")):
    if p.endswith("results_01.jsonl"):
        continue
    for line in open(p, encoding="utf-8"):
        recs.append(json.loads(line))


def nt(s):
    return L.norm_tokens(s)


_cls_cache = {}


def classify(canon, text):
    key = (canon, text)
    if key not in _cls_cache:
        if not text.strip():
            _cls_cache[key] = ("EMPTY", False)
        else:
            r = val.classify_asr_match(canon, text)
            _cls_cache[key] = (r.classification, bool(r.should_pass))
    return _cls_cache[key]


STRICT = {"EXACT_MATCH", "NORMALIZED_MATCH"}


def err_kind(canon_focus, tok):
    if tok is None:
        return "missing"
    f = canon_focus.lower().replace("'s", "")
    t = tok.lower().replace("'s", "")
    if t == f:
        return "exact"
    if f.startswith(t) and 0 < len(f) - len(t) <= 2:
        return "final_char_loss"
    if t.startswith(f) and 0 < len(t) - len(f) <= 2:
        return "extra_final_char"
    if t[:2] == f[:2]:
        return "spelling_variant"
    return "other"


def analyze(r):
    c = manifests[r["cond_id"]]
    res = r["result"]
    if not res.get("ok"):
        return None
    text = res.get("text") or ""
    canon = c["canonical_target"]
    ti = c["target_index"]
    al = L.region_by_alignment(c["expected_parts"], ti, text)
    out = {"job_id": r["job_id"], "cond_id": r["cond_id"], "target_id": r["target_id"], "recipe_id": r["recipe_id"], "engine": r["engine"],
           "variant": r["variant"], "rep": r["rep"], "group": c.get("group"), "kind": c.get("kind"), "text": text,
           "align_region": al["region_text"], "total_sec": c["total_sec"], "pre_ctx_sec": c["pre_ctx_sec"], "post_ctx_sec": c["post_ctx_sec"],
           "n_ctx": c["n_ctx_clips"], "same_voice": c["ctx_all_same_voice"], "ctx_has_focus": c["ctx_has_focus_word"],
           "elapsed": res.get("elapsed"), "jpy": res.get("jpy"), "label_hint": c.get("label_hint"), "category": c.get("category")}
    region = al["region_text"]
    out["region_method"] = "alignment"
    if res.get("words"):
        ws = L.strip_words_punct(res["words"])
        rw = L.region_by_words(ws, c["target_span"]["start"], c["target_span"]["end"])
        out["ts_region"] = rw["region_text"]
        out["ts_min_conf"] = rw["min_conf"]
        region_ts = rw["region_text"]
        out["region_ts_available"] = True
        out["region"] = region_ts
        out["region_method"] = "timestamps"
    else:
        out["region"] = region
    out["whole_cls"], out["whole_pass"] = classify(" ".join(c["expected_parts"]), text) if len(c["expected_parts"]) > 1 else classify(canon, text)
    out["region_cls"], out["region_pass"] = classify(canon, out["region"])
    out["region_strict"] = out["region_cls"] in STRICT
    out["align_cls"], out["align_pass"] = classify(canon, region)
    ct = nt(canon)
    rt = nt(out["region"])
    out["exact_tokens"] = (rt == ct)
    focus = nt(c["focus_word"])
    ftok = focus[0] if focus else None
    # focus語に対応する領域内token(最初にcanonical focusと先頭2文字が一致するもの、無ければ最初のtoken)
    idx = None
    for i, t in enumerate(rt):
        if ftok and t.replace("'s", "")[:2] == ftok.replace("'s", "")[:2]:
            idx = i
            break
    out["focus_token"] = rt[idx] if idx is not None else None
    out["focus_err"] = err_kind(ftok or "", out["focus_token"])
    out["focus_exact"] = out["focus_err"] == "exact"
    # accept: 語末子音切り詰め/対照(intact)は「最終語が正しく認識されたか」、それ以外はProduction判定PASS(領域)
    out["accept"] = bool(out["focus_exact"]) if c.get("category") in ("synthetic_final_consonant_loss", "intact_control") else bool(out["region_pass"])
    if res.get("logprobs"):
        out["lp"] = L.logprob_region(res["logprobs"], nt(out["align_region"]))
    return out


A = [x for x in (analyze(r) for r in recs) if x]
json.dump(A, open(OUT + "/analysis_records_01.json", "w", encoding="utf-8"), ensure_ascii=False)


def rate(xs, f):
    xs = list(xs)
    return (sum(1 for x in xs if f(x)), len(xs))


def fmt(t):
    n, d = t
    return f"{n}/{d} ({100*n/d:.0f}%)" if d else "-"


lines = []
add = lines.append

# ---------------- B: Melos main
M = [a for a in A if a["group"] == "main"]
add("## B-1. Melos target take x recipe x engine: 正認識率(target領域がcanonical 'Melos said.' と一致)\n")
for eng in ("openai", "azure", "whisper-small"):
    sub = [a for a in M if a["engine"] == eng and a["variant"] == "base"]
    if not sub:
        continue
    add(f"### engine={eng} (base variant) — exact_tokens(領域=melos said) / focus(Melos)語一致 / Production判定PASS(領域, CS受理含む)\n")
    add("| recipe | n | exact_tokens | focus(Melos)一致 | Prod classify PASS | strict(EXACT/NORMALIZED) | 平均秒 |")
    add("|---|---|---|---|---|---|---|")
    recs_by = collections.defaultdict(list)
    for a in sub:
        recs_by[a["recipe_id"]].append(a)
    order = [r for r in ["R00_alone", "Npre3", "Npre8", "Npre14", "Npre27", "Npost3", "Npost8", "Npost14", "Nboth", "Dpre3", "Dpre5", "Dpre6", "Dpre8", "Dpre11", "Dpre14", "Dpre25", "Dpost3", "Dpost8", "Dboth", "Rpre", "Rpost", "Rboth", "Rwin5", "Rwin7"] if r in recs_by]
    for rid in order:
        xs = recs_by[rid]
        add(f"| {rid} | {len(xs)} | {fmt(rate(xs, lambda x: x['exact_tokens']))} | {fmt(rate(xs, lambda x: x['focus_exact']))} | {fmt(rate(xs, lambda x: x['region_pass']))} | {fmt(rate(xs, lambda x: x['region_strict']))} | {statistics.mean(x['total_sec'] for x in xs):.1f} |")
    add("")

# ---------------- ctx effect: by kind and seconds band
add("## B-2/C. 文脈量・同一/異ナレーター別(Melos main, base)\n")
add("| engine | 条件群 | 文脈秒(前後合計) | n | exact_tokens | focus一致 | Prod PASS |")
add("|---|---|---|---|---|---|---|")
bands = [(0, 0.01), (2, 4), (4, 7), (7, 11), (11, 16), (16, 22), (22, 30)]
for eng in ("openai", "azure", "whisper-small"):
    for kind in ("alone", "same_voice", "diff_voice", "mixed_real"):
        for lo, hi in bands:
            xs = [a for a in M if a["engine"] == eng and a["variant"] == "base" and a["kind"] == kind and lo <= (a["pre_ctx_sec"] + a["post_ctx_sec"]) < hi]
            if xs:
                add(f"| {eng} | {kind} | {lo}-{hi} | {len(xs)} | {fmt(rate(xs, lambda x: x['exact_tokens']))} | {fmt(rate(xs, lambda x: x['focus_exact']))} | {fmt(rate(xs, lambda x: x['region_pass']))} |")
add("")

# ---------------- target take別 alone
add("## B-3. take別: 単独clip(R00_alone)のASR結果分布(全エンジン・全rep、target領域転写)\n")
add("| target | Prod判定(本番ログ) | engine | 転写の内訳(回数) |")
add("|---|---|---|---|")
tn = {}
for cid, c in manifests.items():
    if c["recipe_id"] == "R00_alone" and c["group"] == "main":
        tn[c["target_id"]] = c["target_note"]
for tid in sorted(tn):
    for eng in ("openai", "azure", "whisper-small", "whisper-medium"):
        xs = [a for a in M if a["target_id"] == tid and a["recipe_id"] == "R00_alone" and a["engine"] == eng and a["variant"] in ("base", "nophrase")]
        if xs:
            cnt = collections.Counter((a["region"] if a["variant"] == "base" else "(nophrase)" + a["region"]) for a in xs)
            add(f"| {tid} | {tn[tid][:40]} | {eng} | " + "; ".join(f"`{k}` x{v}" for k, v in cnt.most_common()) + " |")
add("")

# ---------------- nondeterminism
add("## B-4. 非決定性(同一音声・同一条件で2回呼出した結果の一致)\n")
add("| engine | variant | 比較ペア数 | target領域転写が2回で一致 | 全文転写が一致 | 領域の判定(exact)が不一致 |")
add("|---|---|---|---|---|---|")
for eng in ("openai", "azure"):
    for variant in ("base", "prompt_word", "prompt_prev"):
        by = collections.defaultdict(dict)
        for a in A:
            if a["engine"] == eng and a["variant"] == variant:
                by[a["cond_id"]][a["rep"]] = a
        pairs = [(d[1], d[2]) for d in by.values() if 1 in d and 2 in d]
        if pairs:
            same_reg = sum(1 for p, q in pairs if p["region"] == q["region"])
            same_all = sum(1 for p, q in pairs if p["text"].strip().lower() == q["text"].strip().lower())
            flip = sum(1 for p, q in pairs if p["exact_tokens"] != q["exact_tokens"])
            add(f"| {eng} | {variant} | {len(pairs)} | {same_reg}/{len(pairs)} ({100*same_reg/len(pairs):.0f}%) | {same_all}/{len(pairs)} ({100*same_all/len(pairs):.0f}%) | {flip} |")
add("")

# ---------------- spelling distribution of Melos token
add("## B-5. 誤認識の種類(target領域のfocus語トークンの内訳、Melos main、全文脈条件、base)\n")
add("| engine | recipe群 | exact | spelling_variant | final_char_loss | extra_final_char | other/missing |")
add("|---|---|---|---|---|---|---|")
for eng in ("openai", "azure", "whisper-small"):
    for lab, f in (("alone", lambda a: a["kind"] == "alone"), ("文脈あり(全て)", lambda a: a["kind"] != "alone")):
        xs = [a for a in M if a["engine"] == eng and a["variant"] == "base" and f(a)]
        if not xs:
            continue
        c = collections.Counter(a["focus_err"] for a in xs)
        add(f"| {eng} | {lab} (n={len(xs)}) | {c['exact']} | {c['spelling_variant']} | {c['final_char_loss']} | {c['extra_final_char']} | {c['other']+c['missing']} |")
add("")

# ---------------- ASR param variants (prompt)
add("## E-3. ASRへ文脈情報を与える(OpenAI prompt) vs 与えない\n")
add("| variant | recipe | n | exact_tokens | focus一致 | Prod PASS |")
add("|---|---|---|---|---|---|")
for variant in ("base", "prompt_word", "prompt_prev"):
    for rid in ("R00_alone", "Npre3"):
        xs = [a for a in M if a["engine"] == "openai" and a["variant"] == variant and a["recipe_id"] == rid
              and (variant != "base" or a["target_id"] in {x["target_id"] for x in A if x["variant"] != "base" and x["recipe_id"] == rid})]
        if xs:
            add(f"| {variant} | {rid} | {len(xs)} | {fmt(rate(xs, lambda x: x['exact_tokens']))} | {fmt(rate(xs, lambda x: x['focus_exact']))} | {fmt(rate(xs, lambda x: x['region_pass']))} |")
for variant in ("base", "nophrase"):
    xs = [a for a in M if a["engine"] == "azure" and a["variant"] == variant and a["recipe_id"] == "R00_alone"]
    if xs:
        add(f"| azure {variant} (PhraseList={'Melos' if variant=='base' else 'なし'}) | R00_alone | {len(xs)} | {fmt(rate(xs, lambda x: x['exact_tokens']))} | {fmt(rate(xs, lambda x: x['focus_exact']))} | {fmt(rate(xs, lambda x: x['region_pass']))} |")
add("")

# ---------------- D: counterexamples
add("## D. 反例セット: 単独 vs 文脈結合(誤PASSリスク)\n")
CE = [a for a in A if a["group"] in ("synthetic", "natural_ng")]
# 単独clipの結果(同engine/同variant/同rep)を基準に、文脈条件でのPASS化を数える
alone = {}
for a in CE:
    if a["recipe_id"] == "R00_alone":
        alone.setdefault((a["target_id"], a["engine"], a["variant"]), []).append(a)
add("| group | engine | target群 | 条件 | n | 領域=canonical(exact_tokens) | Prod classify PASS(領域) | 全文Prod PASS |")
add("|---|---|---|---|---|---|---|---|")
for grp in ("synthetic", "natural_ng"):
    for eng in ("openai", "azure"):
        for cond_lab, f in (("単独", lambda a: a["recipe_id"] == "R00_alone"), ("同一voice文脈", lambda a: a["kind"] == "same_voice"), ("異voice文脈", lambda a: a["kind"] == "diff_voice")):
            xs = [a for a in CE if a["group"] == grp and a["engine"] == eng and a["variant"] == "base" and f(a)]
            if xs:
                add(f"| {grp} | {eng} | 全 | {cond_lab} | {len(xs)} | {fmt(rate(xs, lambda x: x['exact_tokens']))} | {fmt(rate(xs, lambda x: x['region_pass']))} | {fmt(rate(xs, lambda x: x['whole_pass']))} |")
add("")

add("### D-2. 反例target別(OpenAI、全rep・全文脈): 領域がcanonical一致した回数\n")
add("| group | target | category/defect | 単独 PASS | 同voice文脈 PASS | 異voice文脈 PASS | 単独の転写例 |")
add("|---|---|---|---|---|---|---|")
tinfo = {}
for cid, c in manifests.items():
    if c["group"] in ("synthetic", "natural_ng"):
        tinfo[c["target_id"]] = (c["group"], c.get("category"), c.get("defect"))
for tid, (g, cat, de) in sorted(tinfo.items(), key=lambda kv: (kv[1][0], kv[0])):
    def cell(f):
        xs = [a for a in CE if a["target_id"] == tid and a["engine"] == "openai" and a["variant"] == "base" and f(a)]
        return fmt(rate(xs, lambda x: x["region_pass"])) if xs else "-"
    ex = collections.Counter(a["region"] for a in CE if a["target_id"] == tid and a["engine"] == "openai" and a["recipe_id"] == "R00_alone")
    add(f"| {g} | {tid} | {cat} / {(de or '')[:50]} | {cell(lambda a: a['recipe_id']=='R00_alone')} | {cell(lambda a: a['kind']=='same_voice')} | {cell(lambda a: a['kind']=='diff_voice')} | " + "; ".join(f"`{k}`x{v}" for k, v in ex.most_common(2)) + " |")
add("")

# false accept counts + guards
add("### D-3. false accept(既知欠陥を含むsynthetic音声が、文脈付きASRでcanonical一致扱い)と防止条件の評価\n")
good = [a for a in A if a["group"] == "main" and a["target_id"] in ("a2_att1", "a2_att3")]  # 本番がPASSにしたtake(参考: 正解側の代理)


def false_accept(a):  # synthetic: 欠陥既知 -> PASSなら確定false accept
    return a["region_pass"]


syn = [a for a in A if a["group"] == "synthetic"]
add("| engine | 条件 | n | false accept (領域Prod PASS) | strict一致(EXACT/NORMALIZED) |")
add("|---|---|---|---|---|")
for eng in ("openai", "azure", "whisper-small"):
    for lab, f in (("単独", lambda a: a["recipe_id"] == "R00_alone"), ("文脈あり", lambda a: a["recipe_id"] != "R00_alone")):
        xs = [a for a in syn if a["engine"] == eng and a["variant"] == "base" and f(a)]
        if xs:
            add(f"| {eng} | {lab} | {len(xs)} | {fmt(rate(xs, false_accept))} | {fmt(rate(xs, lambda x: x['region_strict']))} |")
add("")


# ---------------- D-4 flips / D-5 guards
idx = collections.defaultdict(list)
for a in A:
    idx[(a["target_id"], a["engine"], a["variant"], a["recipe_id"])].append(a)


def majority_pass(recs_):
    return bool(recs_) and sum(1 for r in recs_ if r["accept"]) * 2 > len(recs_)


def label_of(tid):
    g = tinfo.get(tid)
    if not g:
        return None
    if g[0] == "synthetic":
        if g[1] == "intact_control":
            return "good_control"
        return "known_defect_trunc" if g[1] == "synthetic_final_consonant_loss" else "known_defect_word"
    return "natural_ng_proxy"


add("### D-4. 単独ではNGなのに文脈付きでPASSに反転した観測(flip = false accept候補)\n")
add("| label | engine | 単独NGのtarget数 | 文脈付き観測数(単独NG target) | うちPASS反転 | 反転したtarget:recipe |")
add("|---|---|---|---|---|---|")
for lab in ("known_defect_word", "known_defect_trunc", "natural_ng_proxy", "good_control"):
    for eng in ("openai", "azure", "whisper-small"):
        tot = fl = 0
        ntg = 0
        ex = []
        for tid in sorted({a["target_id"] for a in A if label_of(a["target_id"]) == lab}):
            al_ = idx.get((tid, eng, "base", "R00_alone"), [])
            if not al_ or majority_pass(al_):
                continue
            ntg += 1
            for (t2, e2, v2, rid), rs in idx.items():
                if t2 == tid and e2 == eng and v2 == "base" and rid != "R00_alone":
                    for r in rs:
                        tot += 1
                        if r["accept"]:
                            fl += 1
                            ex.append(f"{tid}:{rid}")
        if ntg:
            add(f"| {lab} | {eng} | {ntg} | {tot} | {fl} | {', '.join(sorted(set(ex)))[:140]} |")
add("")

# --- 委任_02追加: D-4反転13件のtarget別内訳(実効標本)
add("### D-4b. (委任_02追加) natural_ng_proxy(OpenAI)のPASS反転観測をtarget別に集計(D-4の単位=全rep観測。D-5のG0=target x recipe単位[rep1のみ]で母集団が異なる)\n")
add("| target | 単独 | 文脈付き観測数 | 反転(PASS)観測数 |")
add("|---|---|---|---|")
_tot = _fl = 0
for tid in sorted({a["target_id"] for a in A if label_of(a["target_id"]) == "natural_ng_proxy"}):
    al_ = idx.get((tid, "openai", "base", "R00_alone"), [])
    if not al_:
        continue
    alone_pass = majority_pass(al_)
    obs_t = [r for (t2, e2, v2, rid), rs in idx.items() if t2 == tid and e2 == "openai" and v2 == "base" and rid != "R00_alone" for r in rs]
    add(f"| {tid} | {'PASS' if alone_pass else 'NG'} | {len(obs_t)} | {sum(1 for r in obs_t if r['accept'])} |")
    if not alone_pass:
        _tot += len(obs_t)
        _fl += sum(1 for r in obs_t if r["accept"])
add(f"\n単独NG target合計: 文脈付き観測 {_tot}件、反転 {_fl}件(D-4と同一母集団)。\n")

add("### D-5. false accept防止条件の評価(OpenAI文脈付きASRを一次、条件を重ねたときの受理数)\n")
obs = []
for (tid, eng, var, rid), rs in idx.items():
    if eng != "openai" or var != "base" or rid == "R00_alone":
        continue
    lab = label_of(tid)
    if lab is None:
        continue
    alone_ = idx.get((tid, "openai", "base", "R00_alone"), [])
    wh = idx.get((tid, "whisper-small", "base", rid), [])
    lps = [r["lp"]["min_logprob"] for r in rs if r.get("lp")]
    obs.append({"label": lab, "tid": tid, "rid": rid, "p1": rs[0]["accept"], "pall": all(r["accept"] for r in rs) and len(rs) >= 2,
                "has2": len(rs) >= 2, "alone": majority_pass(alone_), "lp": min(lps) if lps else None,
                "wh": (wh[0]["accept"] if wh else None)})
rules = [
    ("G0 文脈付きOpenAI領域が受理(無対策。受理=切詰/対照synthetic[category]は最終語の綴り一致[focus_exact]、それ以外はProduction classify_asr_match PASS)", lambda o: o["p1"]),
    ("G1 +単独clipもPASS(単独整合)", lambda o: o["p1"] and o["alone"]),
    ("G2 +2回呼出し両方PASS", lambda o: o["pall"]),
    ("G3a +領域token min logprob >= -0.5", lambda o: o["p1"] and o["lp"] is not None and o["lp"] >= -0.5),
    ("G3b +領域token min logprob >= -1.5", lambda o: o["p1"] and o["lp"] is not None and o["lp"] >= -1.5),
    ("G4 +独立engine(whisper-small, 領域timestamp)もPASS", lambda o: o["p1"] and o["wh"] is True),
    ("G5 +単独整合 かつ whisperもPASS", lambda o: o["p1"] and o["alone"] and o["wh"] is True),
]
add("| 条件 | known_defect_word(語欠落/誤語) 受理=false accept | known_defect_trunc(語末切詰) 受理=false accept | good_control 受理=true accept | natural_ng_proxy 受理 |")
add("|---|---|---|---|---|")
for nm, f in rules:
    cells = []
    for lab in ("known_defect_word", "known_defect_trunc", "good_control", "natural_ng_proxy"):
        xs = [o for o in obs if o["label"] == lab and (nm.startswith("G2") is False or o["has2"])]
        cells.append(fmt((sum(1 for o in xs if f(o)), len(xs))))
    add(f"| {nm} | " + " | ".join(cells) + " |")
add("")

add("### D-6. 語末子音を切り詰めた既知欠陥音声(synthetic)の単独ASR(OpenAI/whisper-small/Azure)\n")
add("| target | defect | OpenAI単独 | Azure単独 | whisper単独 |")
add("|---|---|---|---|---|")
for tid in sorted(t for t in tinfo if tinfo[t][0] == "synthetic"):
    cells = []
    for eng in ("openai", "azure", "whisper-small"):
        rs = idx.get((tid, eng, "base", "R00_alone"), [])
        cells.append("; ".join(f"`{r['region']}`" + ("(P)" if r["accept"] else "(NG)") for r in rs) or "-")
    add(f"| {tid} | {(tinfo[tid][2] or '')[:45]} | " + " | ".join(cells) + " |")
add("")

# ---------------- 処理時間
add("### 処理時間(ASR 1呼出あたり秒、中央値)\n")
add("| engine | 音声長 | 中央値秒 | n |")
add("|---|---|---|---|")
for eng in ("openai", "azure", "whisper-small"):
    for lo, hi in ((0, 3), (3, 8), (8, 16), (16, 40)):
        xs = [a["elapsed"] for a in A if a["engine"] == eng and lo <= a["total_sec"] < hi and a["elapsed"]]
        if xs:
            add(f"| {eng} | {lo}-{hi}s | {statistics.median(xs):.2f} | {len(xs)} |")
add("")

# ---------------- OpenAI logprob: 正解 vs 欠陥
add("### D-7. OpenAI target領域token logprob(min)の分布: 領域PASS観測のうち good_control vs known_defect vs Melos\n")
add("| label | PASS観測n | min_logprob 中央値 | 5%点 | 最小 |")
add("|---|---|---|---|---|")
for lab in ("good_control", "known_defect_word", "known_defect_trunc", "natural_ng_proxy"):
    xs = [a["lp"]["min_logprob"] for a in A if a["engine"] == "openai" and a.get("lp") and a["accept"] and label_of(a["target_id"]) == lab]
    if xs:
        xs.sort()
        add(f"| {lab} | {len(xs)} | {statistics.median(xs):.2f} | {xs[max(0,int(0.05*len(xs)))]:.2f} | {xs[0]:.2f} |")
add("")


add("### C-2. 文脈clipに作品固有語(Melos)が含まれるか否かの効果(Melos main, base, 文脈あり条件のみ)\n")
add("| engine | 文脈にMelos語を含む | n | focus(Melos)一致 | exact_tokens | Prod PASS |")
add("|---|---|---|---|---|---|")
for eng in ("openai", "azure", "whisper-small"):
    for hf in (False, True):
        xs = [a for a in M if a["engine"] == eng and a["variant"] == "base" and a["kind"] != "alone" and bool(a["ctx_has_focus"]) == hf]
        if xs:
            add(f"| {eng} | {'含む' if hf else '含まない'} | {len(xs)} | {fmt(rate(xs, lambda x: x['focus_exact']))} | {fmt(rate(xs, lambda x: x['exact_tokens']))} | {fmt(rate(xs, lambda x: x['region_pass']))} |")
add("")

add("### B-6. 領域抽出の整合性: timestamp領域(Azure/whisper) と 文字列整列領域の一致率\n")
add("| engine | 文脈あり観測数 | 領域が一致 |")
add("|---|---|---|")
for eng in ("azure", "whisper-small", "whisper-medium"):
    xs = [a for a in A if a["engine"] == eng and a["kind"] != "alone" and a.get("ts_region") is not None]
    if xs:
        add(f"| {eng} | {len(xs)} | {fmt(rate(xs, lambda x: x['ts_region'] == x['align_region']))} |")
add("")

add("### D-8. 語末子音を切り詰めた既知欠陥(B2『The ruler smiled and said,』)のASR結果: 切り詰め量別\n")
add("| 切り詰め(ms) | engine | 条件 | 領域転写 | Prod判定 |")
add("|---|---|---|---|---|")
for ms_, tid in ((0, "ctl_B2_intact"), (70, "syn_B2_trunc70"), (140, "syn_B2_trunc140"), (220, "syn_B2_trunc220"), (300, "sweep_B2_trunc300"), (380, "sweep_B2_trunc380"), (460, "sweep_B2_trunc460")):
    for eng in ("openai", "whisper-small"):
        for rid in ("R00_alone", "SSpre", "SDpre"):
            rs = idx.get((tid, eng, "base", rid), [])
            if rs:
                add(f"| {ms_} | {eng} | {rid} | " + "; ".join(f"`{r['region']}`" for r in rs) + " | " + "; ".join("P" if r["accept"] else "NG" for r in rs) + " |")
add("")

add("### D-9. 誤った語(Melos→ruler)に差し替えた既知欠陥: 文脈に正しい名前『Melos』が有る/無いとき\n")
add("| 条件 | engine | 領域転写 | Prod判定 |")
add("|---|---|---|---|")
for rid in ("R00_alone", "NMpre_name3", "NMpre_name14", "NMpre_noname7", "NMpre_diffvoice"):
    for eng in ("openai", "whisper-small"):
        rs = idx.get(("syn_name_ruler", eng, "base", rid), [])
        if rs:
            add(f"| {rid} | {eng} | " + "; ".join(f"`{r['region']}`" for r in rs) + " | " + "; ".join("P" if r["accept"] else "NG" for r in rs) + " |")
add("")


add("### C-3. 同じ付加秒数での 同一ナレーター文脈 vs 異ナレーター文脈 (前置文脈、Melos main、base)\n")
add("| 付加秒(約) | 同一voice recipe(秒) | 異voice recipe(秒) | engine | 同一voice: Prod PASS / focus一致 | 異voice: Prod PASS / focus一致 |")
add("|---|---|---|---|---|---|")
pairs = [("3s", "Npre3", "Dpre3"), ("7-8s", "Npre8", "Dpre8"), ("13s", "Npre14", "Dpre14"), ("23-26s", "Npre27", "Dpre25")]
secs = {}
for a in M:
    secs[a["recipe_id"]] = round(a["pre_ctx_sec"] + a["post_ctx_sec"], 1)
for lab, rn, rd in pairs:
    for eng in ("openai", "azure", "whisper-small"):
        xn = [a for a in M if a["engine"] == eng and a["variant"] == "base" and a["recipe_id"] == rn]
        xd = [a for a in M if a["engine"] == eng and a["variant"] == "base" and a["recipe_id"] == rd]
        if xn and xd:
            add(f"| {lab} | {rn}({secs[rn]}) | {rd}({secs[rd]}) | {eng} | {fmt(rate(xn, lambda x: x['region_pass']))} / {fmt(rate(xn, lambda x: x['focus_exact']))} | {fmt(rate(xd, lambda x: x['region_pass']))} / {fmt(rate(xd, lambda x: x['focus_exact']))} |")
add("")

add("### C-4. Standard(a2) vs Advanced(b1b): 同一recipe・OpenAI/Azure/whisper (base)\n")
add("| recipe | engine | Std a2(6take) Prod PASS | Adv b1b(1take) Prod PASS |")
add("|---|---|---|---|")
for rid in ("R00_alone", "Npre3", "Dpre3", "Rboth", "Rwin5"):
    for eng in ("openai", "azure", "whisper-small"):
        xs = [a for a in M if a["engine"] == eng and a["variant"] == "base" and a["recipe_id"] == rid]
        std = [a for a in xs if a["target_id"].startswith("a2")]
        adv = [a for a in xs if a["target_id"].startswith("b1b")]
        if std and adv:
            add(f"| {rid} | {eng} | {fmt(rate(std, lambda x: x['region_pass']))} | {fmt(rate(adv, lambda x: x['region_pass']))} |")
add("")


add("### D-10. Melos各take(本番判定つき): 単独ASRと文脈付きASRの比較(OpenAI。単独で『Melos said』にならないtakeが文脈で『Melos said』と書かれる=masking候補)\n")
add("| target | 本番判定 | OpenAI単独の領域転写 | 文脈付き観測数 | 『melos said』一致 | Prod classify PASS(CS受理含む) | 『melos said』になったrecipe |")
add("|---|---|---|---|---|---|---|")
for tid in sorted({a["target_id"] for a in M}):
    al_ = [a["region"] for a in M if a["target_id"] == tid and a["engine"] == "openai" and a["variant"] == "base" and a["recipe_id"] == "R00_alone"]
    cx = [a for a in M if a["target_id"] == tid and a["engine"] == "openai" and a["variant"] == "base" and a["recipe_id"] != "R00_alone"]
    rids = sorted({a["recipe_id"] for a in cx if a["exact_tokens"]})
    add(f"| {tid} | {tn.get(tid,'')[:34]} | {'; '.join(sorted(set(al_)))} | {len(cx)} | {sum(1 for a in cx if a['exact_tokens'])} | {sum(1 for a in cx if a['region_pass'])} | {', '.join(rids)[:120]} |")
add("")

# --- 委任_02追加(API不要の再集計)
add("### C-2b. (委任_02追加) C-2をa2_att6除外で再集計(Melos main, base, 文脈あり条件のみ。att6は文脈付き『melos said』の真値が未確定のため分離)\n")
add("| engine | 文脈にMelos語を含む | n(att6除外) | focus(Melos)一致 | exact_tokens | Prod PASS |")
add("|---|---|---|---|---|---|")
for eng in ("openai", "azure", "whisper-small"):
    for hf in (False, True):
        xs = [a for a in M if a["engine"] == eng and a["variant"] == "base" and a["kind"] != "alone" and bool(a["ctx_has_focus"]) == hf and a["target_id"] != "a2_att6"]
        if xs:
            add(f"| {eng} | {'含む' if hf else '含まない'} | {len(xs)} | {fmt(rate(xs, lambda x: x['focus_exact']))} | {fmt(rate(xs, lambda x: x['exact_tokens']))} | {fmt(rate(xs, lambda x: x['region_pass']))} |")
add("")
add("### C-2c. (委任_02追加) a2_att6のOpenAI文脈付き『melos said』(exact_tokens)観測の内訳: 文脈clipに『Melos』語を含むか / recipe別\n")
a6 = [a for a in M if a["target_id"] == "a2_att6" and a["engine"] == "openai" and a["variant"] == "base" and a["recipe_id"] != "R00_alone"]
hit = [a for a in a6 if a["exact_tokens"]]
add(f"- att6 文脈付き観測 {len(a6)}件、うち『melos said』 {len(hit)}件。このうち ctx_has_focus_word=true は {sum(1 for a in hit if a['ctx_has_focus'])}件、false は {sum(1 for a in hit if not a['ctx_has_focus'])}件。")
hit_r = collections.Counter(a["recipe_id"] for a in hit)
rid_all = sorted({a["recipe_id"] for a in hit})
add(f"- 『melos said』になったdistinct recipe {len(rid_all)}件: " + ", ".join(f"{r}(ctx_has_focus={'T' if any(a['ctx_has_focus'] for a in hit if a['recipe_id']==r) else 'F'}, x{hit_r[r]})" for r in rid_all))
n_f = sum(1 for r in rid_all if not any(a["ctx_has_focus"] for a in hit if a["recipe_id"] == r))
add(f"- distinct recipeのうち ctx_has_focus_word=false は {n_f}/{len(rid_all)}")
add("")
add("### C-2d. (委任_02追加) Dpre25(異voice前置25秒)の各take(OpenAI, base)\n")
for tid in sorted({a["target_id"] for a in M}):
    xs = [a for a in M if a["target_id"] == tid and a["engine"] == "openai" and a["variant"] == "base" and a["recipe_id"] == "Dpre25"]
    if xs:
        add(f"- {tid}: n={len(xs)}, ctx_has_focus={xs[0]['ctx_has_focus']}, 転写={sorted({a['region'] for a in xs})}, melos said={sum(1 for a in xs if a['exact_tokens'])}")
add("")

json.dump({"n_records": len(A)}, open(OUT + "/analysis_meta_01.json", "w"), indent=1)
open(OUT + "/analysis_tables_01.md", "w", encoding="utf-8").write("\n".join(lines))
print("records", len(A), "-> analysis_tables_01.md")
print(L.write_guard_report()["blocked_write_attempts"])
