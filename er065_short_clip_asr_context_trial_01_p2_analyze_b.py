# -*- coding: utf-8 -*-
"""委任_03 B/C 集計(オフライン無料)。phase2のresults_01_*_02.jsonl(新規ASR)と、委任_01の analysis_records_01.json(既存実測)を
同じ指標で並べる。target領域のExact/focus語/Production判定/音韻判定(Trial)を出す。"""
import collections, glob, json, os, sys, re
sys.path.insert(0, ".")
import er065_short_clip_asr_context_trial_01_lib as L
import er065_short_clip_asr_context_trial_01_p2_phon as P
import er006_preprod_hardening_01_validation as val
import er021_en_asr_semantic_equivalence_production_01 as _se
_se.append_telemetry_log = lambda *a, **k: None
OUT = "er065_output/short_clip_asr_context_trial_01/phase2"
L.install_write_guard([OUT])

man = {}
for p in glob.glob(OUT + "/manifest_*_02.json"):
    for c in json.load(open(p, encoding="utf-8"))["conditions"]:
        man[c["cond_id"] + "|" + c["group"]] = c
new = []
for p in sorted(glob.glob(OUT + "/results_01_*_02.jsonl")):
    for l in open(p, encoding="utf-8"):
        new.append(json.loads(l))

_cache = {}
def prod(canon, text):
    k = (canon, text)
    if k not in _cache:
        if not text.strip(): _cache[k] = ("EMPTY", False)
        else:
            r = val.classify_asr_match(canon, text); _cache[k] = (r.classification, bool(r.should_pass))
    return _cache[k]

def focus_tok(rt, f="melos"):
    for t in rt:
        if t[:2] == f[:2]: return t
    return None

rows = []
for r in new:
    res = r["result"]
    if not res.get("ok"): continue
    grp = r.get("group")
    c = man.get(r["cond_id"] + "|" + grp)
    if c is None: continue
    text = res.get("text") or ""
    canon = c["canonical_target"]
    if res.get("words"):
        ws = L.strip_words_punct(res["words"])
        region = L.region_by_words(ws, c["target_span"]["start"], c["target_span"]["end"])["region_text"]
        # 全体alone(target領域=全体)の場合はtimestamp領域がぶれるので全文を使う
        if c["n_ctx_clips"] == 0: region = " ".join(L.norm_tokens(text))
    else:
        region = L.region_by_alignment(c["expected_parts"], c["target_index"], text)["region_text"] if c["n_ctx_clips"] else " ".join(L.norm_tokens(text))
    ex = P.explain_diff(canon, region)
    cls, ok = prod(canon, region)
    rows.append({"group": grp, "target": r["target_id"], "recipe": r["recipe_id"], "engine": r["engine"].replace("whisper-", "whisper:"),
                 "rep": r["rep"], "canon": canon, "region": region, "exact": L.norm_tokens(canon) == L.norm_tokens(region),
                 "focus_token": focus_tok(L.norm_tokens(region)), "prod_cls": cls, "prod_pass": ok, "phon": ex["verdict"],
                 "cat": c.get("category"), "dur": c["total_sec"], "ctx_pre": c["pre_ctx_sec"], "ctx_post": c["post_ctx_sec"]})
json.dump(rows, open(OUT + "/b_records_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def pct(a, b): return f"{a}/{b} ({100*a/b:.0f}%)" if b else "-"
md = []
md.append("## B-P2-1. 長さ vs s+s融合: Melosの後ろがs始まりでない短尺clip(2語cut)・元clip全体の単独ASR (phase2新規)\n")
md.append("target = `Melos X`の2語cut(語末sの後ろが c/t/h/l/f=非歯擦音) または元clip全体。canonicalは各行。\n")
md.append("| target | canonical | engine | n | exact(綴り全一致) | Melos語が`melos`で一致 | 出力例(focus語の内訳) | Production判定PASS | 音韻説明可(FUSION/HOMOPHONE) |")
md.append("|---|---|---|---|---|---|---|---|---|")
by = collections.defaultdict(list)
for x in rows:
    if x["group"].startswith("p2_len"): by[(x["group"][-2:] + ":" + x["target"], x["engine"])].append(x)
for (t, e), L_ in sorted(by.items()):
    n = len(L_)
    toks = collections.Counter(x["focus_token"] for x in L_)
    md.append(f"| {t} | {L_[0]['canon'][:34]} | {e} | {n} | {pct(sum(x['exact'] for x in L_), n)} | {pct(sum(x['focus_token']=='melos' for x in L_), n)} | {dict(toks)} | {pct(sum(x['prod_pass'] for x in L_), n)} | {pct(sum(x['phon'] in ('PHON_EXPLAINED_FUSION','PHON_HOMOPHONE_ONLY') for x in L_), n)} |")

# 集計: 長さ・条件別
def agg(label, sel):
    out = []
    for eng in ("openai", "azure", "whisper:small", "whisper:medium"):
        xs = [x for x in sel if x["engine"] == eng]
        if xs:
            out.append(f"| {label} | {eng} | {len(xs)} | {pct(sum(x['exact'] for x in xs), len(xs))} | {pct(sum(x['focus_token']=='melos' for x in xs), len(xs))} | {pct(sum(x['prod_pass'] for x in xs), len(xs))} |")
    return out

md.append("\n## B-P2-2. 総括: 評価単位(長さ・s+s有無・文脈)別の正認識率 (Melos main, 新規+委任_01既存実測)\n")
md.append("exact=target領域が canonical と綴り全一致 / melos語=focus語が`melos`と綴り一致 / Prod PASS=Production classify_asr_match(role無)でshould_pass。")
md.append("| 評価単位 | engine | n観測 | exact | Melos語が`melos` | Production PASS |")
md.append("|---|---|---|---|---|---|")
len2v1 = [x for x in rows if x["group"] == "p2_len" and "whole" not in x["target"]]
len2 = [x for x in rows if x["group"] == "p2_len_v2"]
lenwhole = [x for x in rows if x["group"] == "p2_len" and ("c1whole" in x["target"] or "p3c3whole" in x["target"])]
for l in agg("2語cut v2 `Melos X`(X=非s始まり, 0.75-1.2秒, 終端=次語直前)", len2): md.append(l)
for l in agg("2語cut v1(終端が語末+0.06秒: -ed等が欠け得る。参考)", len2v1): md.append(l)
for l in agg("元clip全体(Melos+非s始まり, 2.7-4.6秒)", lenwhole): md.append(l)
# 既存(委任_01)
old = json.load(open("er065_output/short_clip_asr_context_trial_01/analysis_records_01.json", encoding="utf-8"))
mains = [o for o in old if o["group"] == "main" and o["variant"] == "base"]
def oldsel(pred): 
    return [{"engine": o["engine"], "exact": o["exact_tokens"], "focus_token": (o["focus_token"] or None), "prod_pass": o["region_pass"]} for o in mains if pred(o)]
for lab, pred in [("Melos said. 単独2語 (R00_alone, 7 take)", lambda o: o["recipe_id"] == "R00_alone"),
                  ("Melos said. +直前台詞 gap300 (Rpre)", lambda o: o["recipe_id"] == "Rpre"),
                  ("Melos said. +直後台詞 gap300 (Rpost)", lambda o: o["recipe_id"] == "Rpost"),
                  ("Melos said. 前後台詞 gap300 (Rboth)", lambda o: o["recipe_id"] == "Rboth"),
                  ("Melos said. 前後2-3clip (Rwin5/Rwin7 28秒)", lambda o: o["recipe_id"] in ("Rwin5", "Rwin7"))]:
    for l in agg(lab + " [委任_01]", oldsel(pred)): md.append(l)
for rid in ("Rpre", "Rpost", "Rboth"):
    sel = [x for x in rows if x["group"] == "p2_sentence80" and x["recipe"] == rid]
    for l in agg(f"Melos said. {rid} gap80 [委任_03新規]", sel): md.append(l)
# take別(1文単位 gap80 vs gap300)
md.append("\n## B-P2-3. 『1文単位』(直前の台詞+attribution `Melos said.`) gap80ms vs gap300ms: take別 (OpenAI/Azure/whisper-small, Rpre)\n")
md.append("| take | engine | gap300(委任_01) exact/n | gap80(新規) exact/n | gap80 region出力 |")
md.append("|---|---|---|---|---|")
for t in sorted({x["target"] for x in rows if x["group"] == "p2_sentence80"}):
    for eng in ("openai", "azure", "whisper:small"):
        a = [o for o in mains if o["target_id"] == t and o["recipe_id"] == "Rpre" and o["engine"].startswith(eng.split(":")[0]) and (o["engine"] == "whisper-small" if eng.startswith("whisper") else True)]
        b = [x for x in rows if x["group"] == "p2_sentence80" and x["target"] == t and x["recipe"] == "Rpre" and x["engine"] == eng]
        if not b: continue
        md.append(f"| {t} | {eng} | {pct(sum(o['exact_tokens'] for o in a), len(a))} | {pct(sum(x['exact'] for x in b), len(b))} | {'; '.join(sorted({x['region'] for x in b}))} |")
G = [x for x in rows if x["group"] == "p2_general"]
if G:
    md.append("\n## B-P2-4. 一般語(Production音声の実境界)2語窓の単独ASR: 子音連続の型別 正認識率 (phase2新規)\n")
    md.append("型: SS=s/z+s/z, TT=t+t, DD=d+d, NN=n+n, YOD=t/d/s/z+y, SHS=s/z+sh/ch/jh, CTRL=融合しない子音境界(対照)。窓は0.5-1.6秒の2語。exact=2語が綴り全一致。観測=target x engine x rep(OpenAIは3rep)。")
    md.append("| 型 | engine | 観測 | exact | 不一致のうち 音韻説明可(FUSION/HOMOPHONE/VOICING) | 不一致のうち 説明不能 | Production PASS |")
    md.append("|---|---|---|---|---|---|---|")
    for ty in ("SS", "TT", "DD", "NN", "YOD", "SHS", "CTRL"):
        for eng in ("openai", "azure", "whisper:small", "whisper:medium"):
            xs = [x for x in G if x["cat"] == ty and x["engine"] == eng]
            if not xs: continue
            ne = [x for x in xs if not x["exact"]]
            md.append(f"| {ty} | {eng} | {len(xs)} | {pct(sum(x['exact'] for x in xs), len(xs))} | {sum(x['phon'] in ('PHON_EXPLAINED_FUSION','PHON_HOMOPHONE_ONLY','PHON_EXPLAINED_VOICING') for x in ne)} | {sum(x['phon'] in ('NOT_EXPLAINED','NO_PHONOLOGICAL_EVIDENCE') for x in ne)} | {pct(sum(x['prod_pass'] for x in xs), len(xs))} |")
    md.append("\n不一致の全列挙(canonical -> region : 音韻判定 / Production):\n")
    for x in sorted(G, key=lambda x: (x["cat"], x["target"], x["engine"])):
        if not x["exact"]:
            md.append(f"- {x['cat']}/{x['target']} [{x['engine']}] rep{x['rep']} `{x['canon']}` -> `{x['region']}` : {x['phon']} / {x['prod_cls']}")
# ---- 編集音声(s+s融合長のsを単独s長へ短縮した Melos take)
E = [x for x in rows if x["group"] == "p2_edit"]
if E:
    md.append("\n## B-P2-5. Melos said 編集音声(融合長の摩擦区間を単独s相当80msまで短縮)のASR: 元音声との比較\n")
    md.append("| take | engine | 元音声の出力(委任_01, R00_alone) | 編集後の出力(phase2) |")
    md.append("|---|---|---|---|")
    for t in sorted({x["target"] for x in E}):
        base = t.replace("_shortS", "")
        for eng in ("openai", "azure", "whisper:small"):
            o = sorted({r["region"] for r in old_rows if r["target"] == base and r["engine"] == eng and r["recipe"] == "R00_alone"}) if False else sorted({o["region"] for o in old if o["group"] == "main" and o["target_id"] == base and o["recipe_id"] == "R00_alone" and (o["engine"] == eng or (eng == "whisper:small" and o["engine"] == "whisper-small")) and o["variant"] == "base"})
            n = sorted({x["region"] for x in E if x["target"] == t and x["engine"] == eng})
            md.append(f"| {base} | {eng} | {o} | {n} |")
open(OUT + "/analysis_b_02.md", "w", encoding="utf-8").write("\n".join(md))
print("\n".join(md))
