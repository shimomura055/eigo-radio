# FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_01: 直近X/Z KPの機械分類census(API 0・read-only)
import glob, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.chdir(ROOT)
OUT = "docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/census_items_02_extended.json"
import time
MIN_MTIME = time.mktime((2026,10,15,0,0,0,0,0,-1))   # 2026-10-15以降(直近)
DEM = {"this", "that", "these", "those"}
POSS = {"my", "your", "his", "her", "their", "our", "its"}
PRON = {"you", "they", "he", "she", "i", "we", "yourself", "himself", "herself", "themselves"}
IRREG_PAST = {"took","gave","made","went","came","saw","got","kept","held","held","drew","drove","fell","rose","ran","began","brought","bought","thought","told","said","met","sat","stood","wrote","spoke","broke","chose","found","left","lost","paid","sold","sent","spent","built","caught","taught","threw","grew","knew","wore","won","hit","cut","put","set"}
def toks(s): return re.findall(r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*", s or "")
def flags(kp, gloss):
    t=[w.lower() for w in toks(kp)]; f=[]
    if len(t)>5: f.append("over5")
    if any(w in DEM for w in t): f.append("demonstrative")
    if any(w in POSS for w in t): f.append("possessive_residual")
    if any(w in PRON for w in t): f.append("pronoun_residual")
    if t and (t[0] in IRREG_PAST or (t[0].endswith("ed") and len(t[0])>4) or t[0].endswith("ing") and len(t[0])>5 or (t[0].endswith("s") and not t[0].endswith("ss") and len(t)>1 and t[0] not in {"its","this","has","was"})):
        f.append("tense_or_inflection_residual?")
    g=gloss or ""
    if re.search(r"(その|この|あの|あなた|彼女|彼ら|彼)", g): f.append("gloss_deictic_or_person")
    return f
seen={}
for fp in sorted(glob.glob("er0*_output/**/keywords_canonicalized.json", recursive=True)):
    p=fp.replace("\\","/")
    if "outer_retry" in p: continue
    m=re.search(r"/(a2|b1b)/key_phrases/keywords_canonicalized\.json$", p)
    if not m: continue
    lv=m.group(1); base=p[:m.start()]
    try: d=json.load(open(fp,encoding="utf-8"))
    except Exception: continue
    its=d.get("items",[])
    if not its: continue
    if os.path.getmtime(fp) < MIN_MTIME: continue
    key=(base,lv)
    if key in seen: continue
    seen[key]=(os.path.getmtime(fp),its)
# 同一theme+levelは最新runのみ(重複run除去しすぎない: run単位は残す)
rows=[]
for (base,lv),(mt,its) in seen.items():
    fam="Z" if "er026_output" in base else "X"
    # explanation(b1bのみ)
    expl={}
    cand=[base+"/key_phrases/b1b/kp_explanations.json", base+"/b1b/audit/tts_generation_results.json", base+"/audit/tts_generation_results.json"]
    for c in cand:
        if lv=="b1b" and os.path.exists(c):
            try:
                x=json.load(open(c,encoding="utf-8"))
                src=(x.get("key_phrase_explanations_text") or {}).get("items") or x.get("items") or {}
                for k,v in src.items():
                    e=v.get("english_explanation") if isinstance(v,dict) else None
                    if e: expl[int(k) if str(k).isdigit() else k]=e
            except Exception: pass
    for it in its:
        rk=it.get("rank")
        rows.append(dict(family=fam,fulltext=bool(it.get("fulltext_source_ref")),run=base,level=lv,rank=rk,source_span=it.get("source_span"),
            display_phrase=it.get("display_phrase"),key_phrase=it.get("key_phrase"),used_form=it.get("used_form"),
            gloss=it.get("japanese_gloss"),reason=it.get("normalization_reason"),
            explanation=expl.get(rk) if lv=="b1b" else None,
            flags=flags(it.get("used_form") or it.get("key_phrase"), it.get("japanese_gloss"))))
json.dump(rows,open(OUT,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
runs={(r["run"]) for r in rows}
print("runs",len(runs),"items",len(rows),"X",sum(r['family']=='X' for r in rows),"Z",sum(r['family']=='Z' for r in rows))
import collections
c=collections.Counter(f for r in rows for f in r["flags"]); print(c)
