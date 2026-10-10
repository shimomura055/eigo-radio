# B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-01 Phase1: read-only trace (no API). Run: py -I trace_5themes_01.py
import re, json, difflib, os, sys
sys.stdout.reconfigure(encoding="utf-8")
R = "er052_output/factlock_astra_e2e_trial_01/g0_real_annotation_01"
THEMES = ["semiconductor_earnings","small_bag","space_weapons","hormuz","central_bank_mortgage","meta","byd_recall","openai_copyright","streaming_price"]
IMP = re.compile(r"(ないこと|[^。]こと$|書かない|断定しない|付け加えない|補わない|混同しない|扱わない|分けて扱う|区別する|区別して|として扱う|扱う$|とは書|と断定|同一視しない|一般化しない|帰属させない|しない$)")
EPI = re.compile(r"(ではない|確認でき|確認され|確定でき|認定され|主張|見込み|未提示|不明|断定)")
FIELD_RE = re.compile(r"^  (scope|conditions|numeric_value|date_or_period|causal_strength|ambiguity_note|notes_for_writer): (.*)$")
HEAD_RE = re.compile(r"^\[(VERIFIED|AMBIGUOUS[^\]]*)\]\s+([A-Za-z0-9_\-]+): (.*)$")
def parse_ledger(t):
    facts, cur = {}, None
    for ln in t.replace("\r\n","\n").split("\n"):
        m = HEAD_RE.match(ln)
        if m: cur = m.group(2); facts[cur] = {"tag":m.group(1),"claim":m.group(3)}; continue
        m = FIELD_RE.match(ln)
        if m and cur: facts[cur][m.group(1)] = m.group(2)
    return facts
def sents(t):
    out=[]
    for para in t.split("\n"):
        para=re.sub(r"^\s*-\s*","",para).strip()
        if not para: continue
        for s in re.findall(r"[^。]+。?", para):
            s=s.strip()
            if s: out.append(s)
    return out
def best(s, facts):
    res=[]
    for fid,f in facts.items():
        for k,v in f.items():
            if k=="tag": continue
            sm=difflib.SequenceMatcher(None,s,v,autojunk=False)
            m=sm.find_longest_match(0,len(s),0,len(v))
            res.append((m.size, fid, k, v[m.a-m.a+m.b:m.b+m.size] if False else s[m.a:m.a+m.size]))
    res.sort(reverse=True)
    return res[:2]
out={}
for th in THEMES:
    d=f"{R}/{th}/shared"
    ledger=open(f"{d}/ledger.txt",encoding="utf-8").read()
    brief=open(f"{d}/brief_original.md",encoding="utf-8").read().replace("\r\n","\n")
    facts=parse_ledger(ledger)
    story, body = brief.split("## Storyline\n",1)[1].split("\n## Selected Facts\n",1)
    rows=[]
    for part,txt in (("Storyline",story),("SelectedFacts",body)):
        for s in sents(txt):
            imp=bool(IMP.search(s)); epi=bool(EPI.search(s))
            if not(imp or epi): continue
            b=best(s,facts)
            rows.append({"part":part,"sentence":s,"imperative_pattern":imp,"epistemic_pattern":epi,
                         "best_matches":[{"len":x[0],"fact":x[1],"field":x[2],"common":x[3]} for x in b]})
    out[th]={"n_ledger_facts":len(facts),"rows":rows}
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"trace_candidates_raw_01.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
for th,v in out.items():
    print("=====",th,v["n_ledger_facts"])
    for r in v["rows"]:
        b=r["best_matches"][0]
        print(("I" if r["imperative_pattern"] else "-")+("E" if r["epistemic_pattern"] else "-"),r["part"][:5],"|",r["sentence"][:90],"|",b["len"],b["fact"],b["field"],"|",b["common"][:40])
