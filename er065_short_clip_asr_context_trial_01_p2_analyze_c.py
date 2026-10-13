# -*- coding: utf-8 -*-
"""委任_03 C: NG時Fallback比較(オフライン無料)。委任_01の実測(analysis_records_01.json: Melos 7 take、synthetic/natural_ng反例)と
phase2新規(b_records_02.json)を入力に、Fallback方式別に『NG takeがどれだけ救済されるか』『既知欠陥が誤って救済されないか』を数える。
方式: (F0) 現行(Production classify_asr_match region_pass) / (F1) 同条件繰返し(OpenAI rep1,rep2のどちらかがPASS/exact) /
      (F2) 前後音声追加再評価(文脈付きrecipeのどれかがexact) / (F3) 別engine再評価(Azure or whisperがexact) /
      (F4-Trial) 文脈付き音韻判定: ASR転写が連結発音で説明できる(PHON_EXPLAINED_FUSION)→HR候補へ(独立証拠なしでは許容にしない)
      (F5-Trial) F4 + 音響の独立証拠(geminate長)→許容。"""
import collections, glob, json, sys
sys.path.insert(0, ".")
import er065_short_clip_asr_context_trial_01_lib as L
import er065_short_clip_asr_context_trial_01_p2_phon as P
OUT = "er065_output/short_clip_asr_context_trial_01/phase2"
BASE = "er065_output/short_clip_asr_context_trial_01"
canon = {}
for p in glob.glob(BASE + "/conditions_manifest_*_01.json"):
    for c in json.load(open(p, encoding="utf-8"))["conditions"]:
        canon[c["cond_id"]] = c["canonical_target"]
old = json.load(open(BASE + "/analysis_records_01.json", encoding="utf-8"))
recs = []
for o in old:
    cn = canon.get(o["cond_id"])
    if not cn: continue
    recs.append({"group": o["group"], "target": o["target_id"], "recipe": o["recipe_id"], "engine": o["engine"], "variant": o["variant"], "rep": o["rep"],
                 "canon": cn, "region": o["region"], "exact": o["exact_tokens"], "prod_pass": o["region_pass"], "category": o.get("category"),
                 "label_hint": o.get("label_hint"), "n_ctx": o["n_ctx"], "src": "委任_01"})
for x in json.load(open(OUT + "/b_records_02.json", encoding="utf-8")):
    recs.append({**x, "src": "委任_03", "n_ctx": 0 if x["recipe"] == "R00_alone" else 1, "variant": "base", "label_hint": None, "category": None})
for r in recs:
    ex = P.explain_diff(r["canon"], r["region"]) if r["region"].strip() else {"verdict": "EMPTY"}
    r["phon"] = ex["verdict"]
json.dump(recs, open(OUT + "/c_records_02.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

md = []
def pct(a, b): return f"{a}/{b} ({100*a/b:.0f}%)" if b else "-"
# --- C-1: Melos 7 take別 × fallback方式 (main, base)
melos = [r for r in recs if r["group"] == "main" and r["variant"] == "base" and r["src"] == "委任_01"]
takes = sorted({r["target"] for r in melos})
md.append("## C-1. Melos 7 take別: Fallback方式ごとの『救済(exact一致 or 現行PASS)』と『音韻説明可(Trial)』\n")
md.append("F0=単独1回(OpenAI rep1) / F1=同条件繰返し(単独OpenAI rep1-2のどちらかexact) / F2=前後音声付き(OpenAI 全文脈recipeのいずれかでexact) / F3=別engine単独(Azure or whisper exactが1回以上) / F4=単独転写のうち音韻説明可(FUSION)の割合(OpenAI+Azure+whisper単独) \n")
md.append("| take | prod判定ラベル(委任_01) | F0 exact | F1 繰返し exact | F2 文脈付き exact(回数/観測) | F3 別engine exact | F4 単独転写が連結発音で説明可 | F4で説明不能の転写例 | 単独転写の内訳(engine:出力) |")
md.append("|---|---|---|---|---|---|---|---|---|")
for t in takes:
    al = [r for r in melos if r["target"] == t and r["recipe"] == "R00_alone"]
    oa = [r for r in al if r["engine"] == "openai"]
    f0 = any(r["exact"] for r in oa if r["rep"] == 1)
    f1 = any(r["exact"] for r in oa)
    ctx = [r for r in melos if r["target"] == t and r["recipe"] != "R00_alone" and r["engine"] == "openai"]
    f2 = sum(r["exact"] for r in ctx)
    f3 = any(r["exact"] for r in al if r["engine"] != "openai")
    ex = sum(r["phon"] in ("EXACT", "PHON_EXPLAINED_FUSION") for r in al)
    nex = sorted({r["region"] for r in al if r["phon"] not in ("EXACT", "PHON_EXPLAINED_FUSION")})
    inv = "; ".join(sorted({f"{r['engine'][:3]}:{r['region']}" for r in al}))
    lab = next((r["label_hint"] for r in melos if r["target"] == t and r["label_hint"]), "")
    md.append(f"| {t} | {lab} | {'Y' if f0 else 'N'} | {'Y' if f1 else 'N'} | {f2}/{len(ctx)} | {'Y' if f3 else 'N'} | {pct(ex, len(al))} | {nex[:4]} | {inv[:200]} |")
# --- C-2: 全体集計(NG takeのみ)
ng_takes = [t for t in takes if t != "a2_att1" and t != "a2_att3"]
md.append("\n## C-2. NG take(att2,4,5,6, b1b_att1の5本; Production判定でNGだったtake)全体の救済率\n")
md.append("観測単位=(take, engine, rep, recipe)。F4は音韻説明可(PHON_EXPLAINED_FUSION)、F4'はVOICING弱説明、NOTは不能。\n")
md.append("| 方式 | 対象観測 | 救済(exactまたは現行PASS) | 音韻説明可(FUSION) | 音韻弱説明(VOICING) | 説明不能(NOT_EXPLAINED) | 音韻証拠なし(OOV等) | 同音綴り違い(HOMOPHONE) |")
md.append("|---|---|---|---|---|---|---|---|")
def row(label, sel):
    n = len(sel)
    c = collections.Counter(r["phon"] for r in sel)
    md.append(f"| {label} | {n} | {pct(sum(r['exact'] or r['prod_pass'] for r in sel), n)} | {pct(c['PHON_EXPLAINED_FUSION'], n)} | {pct(c['PHON_EXPLAINED_VOICING'], n)} | {pct(c['NOT_EXPLAINED'], n)} | {pct(c['NO_PHONOLOGICAL_EVIDENCE'], n)} | {pct(c['PHON_HOMOPHONE_ONLY'], n)} |")
S = lambda **kw: [r for r in melos if r["target"] in ng_takes and all((r[k] == v if not callable(v) else v(r[k])) for k, v in kw.items())]
row("F0/F1 単独OpenAI(全rep)", S(recipe="R00_alone", engine="openai"))
row("F3 単独Azure+Phrase List", S(recipe="R00_alone", engine="azure"))
row("F3 単独whisper-small", S(recipe="R00_alone", engine="whisper-small"))
row("F3 単独whisper-medium", S(recipe="R00_alone", engine="whisper-medium"))
row("F2 文脈付きOpenAI(全recipe)", [r for r in melos if r["target"] in ng_takes and r["recipe"] != "R00_alone" and r["engine"] == "openai"])
row("F2 文脈付きAzure", [r for r in melos if r["target"] in ng_takes and r["recipe"] != "R00_alone" and r["engine"] == "azure"])
# --- C-3: 反例(既知欠陥)の誤説明(false explain)
md.append("\n## C-3. 既知欠陥・NG proxy反例に対する音韻判定の誤説明(= 欠陥を『連結発音で説明可』と誤る件数。独立証拠なしでも『許容』にはならないが、HR候補に載る件数)\n")
md.append("| 群 | engine | 観測 | 現行PASS | FUSION(誤説明候補) | VOICING | HOMOPHONE | NOT_EXPLAINED | 備考 |")
md.append("|---|---|---|---|---|---|---|---|---|")
for g in ("synthetic", "natural_ng"):
    for eng in ("openai", "azure", "whisper-small"):
        sel = [r for r in recs if r["group"] == g and r["engine"] == eng and r["src"] == "委任_01" and r["variant"] == "base"]
        if not sel: continue
        c = collections.Counter(r["phon"] for r in sel)
        md.append(f"| {g} | {eng} | {len(sel)} | {sum(r['prod_pass'] for r in sel)} | {c['PHON_EXPLAINED_FUSION']} | {c['PHON_EXPLAINED_VOICING']} | {c['PHON_HOMOPHONE_ONLY']} | {c['NOT_EXPLAINED']} | |")
fe = [r for r in recs if r["group"] in ("synthetic", "natural_ng") and r["phon"] in ("PHON_EXPLAINED_FUSION", "PHON_EXPLAINED_VOICING") and r["src"] == "委任_01"]
md.append("\nFUSION/VOICINGと判定された反例観測の全列挙(canonical → region):\n")
seen = set()
for r in fe:
    k = (r["target"], r["canon"], r["region"], r["phon"])
    if k in seen: continue
    seen.add(k); md.append(f"- {r['group']}/{r['target']} [{r['engine']}] `{r['canon']}` → `{r['region']}` : {r['phon']}")
open(OUT + "/analysis_c_02.md", "w", encoding="utf-8").write("\n".join(md))
print("\n".join(md))
