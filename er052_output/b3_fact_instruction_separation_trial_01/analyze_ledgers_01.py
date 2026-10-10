# Phase1 read-only offline analysis (no API). Run from repo root: py -I er052_output/b3_fact_instruction_separation_trial_01/analyze_ledgers_01.py
import re, json, difflib, sys, os
R = "er052_output/factlock_astra_e2e_trial_01/g0_real_annotation_01"
THEMES = ["semiconductor_earnings","small_bag","space_weapons","hormuz","central_bank_mortgage","meta","byd_recall","openai_copyright","streaming_price"]
PROBLEM = {"semiconductor_earnings","small_bag","space_weapons","hormuz","central_bank_mortgage"}
HEAD_RE = re.compile(r"^\[(VERIFIED|AMBIGUOUS[^\]]*)\]\s+([A-Za-z0-9_\-]+): (.*)$")
FIELD_RE = re.compile(r"^  (scope|conditions|numeric_value|date_or_period|causal_strength|ambiguity_note|notes_for_writer): (.*)$")
IMP = re.compile(r"(ないこと|こと[。]?$|書かない|断定しない|付け加えない|補わない|混同しない|扱わない|分けて扱う|区別する|区別して|として扱う|扱う[。]?$|言い換えない|一般化しない|帰属させない|結び付けない|同一視しない|しない[。]?$|限定する|記述する|整理する|記載する|ない[。]$)")
def parse_ledger(t):
    facts, order, cur = {}, [], None
    for ln in t.replace("\r\n","\n").split("\n"):
        m = HEAD_RE.match(ln)
        if m: cur = m.group(2); facts[cur] = {"tag":m.group(1),"claim":m.group(3)}; order.append(cur); continue
        m = FIELD_RE.match(ln)
        if m and cur: facts[cur][m.group(1)] = m.group(2)
    return facts, order
def sents(t):
    out=[]
    for para in t.split("\n"):
        para=re.sub(r"^\s*-\s*","",para).strip()
        for s in re.findall(r"[^。]+。?", para):
            if s.strip(): out.append(s.strip())
    return out
def lcs(a,b):
    return difflib.SequenceMatcher(None,a,b,autojunk=False).find_longest_match(0,len(a),0,len(b)).size
rows=[]
for th in THEMES:
    d=f"{R}/{th}/shared"
    ledger=open(f"{d}/ledger.txt",encoding="utf-8").read()
    brief=open(f"{d}/brief_original.md",encoding="utf-8").read().replace("\r\n","\n")
    ev=json.load(open(f"{d}/fact_selection_evidence_original.json",encoding="utf-8"))
    facts,order=parse_ledger(ledger)
    sel=ev["selected_fact_ids"]
    story, body = brief.split("## Storyline\n",1)[1].split("\n## Selected Facts\n",1)
    bs=[s for s in sents(body)]
    imp_brief=[s for s in bs if IMP.search(s) and not s.startswith("Storyline")]
    notes_all=[(f,facts[f]["notes_for_writer"]) for f in order if facts[f].get("notes_for_writer")]
    notes_sel=[(f,n) for f,n in notes_all if f in sel]
    surv=[]
    for f,n in notes_sel:
        best=max((lcs(n,s) for s in bs),default=0)
        surv.append({"fact":f,"note_len":len(n),"best_common_substring_with_any_brief_sentence":best,"verbatim_like(>=12)":best>=12})
    notes_imp=[f for f,n in notes_all if IMP.search(n)]
    # Arm D preview sizes
    claim_only=sum(len(facts[f]["claim"]) for f in sel)
    claim_cond=sum(len(facts[f]["claim"])+len(facts[f].get("conditions",""))+len(facts[f].get("scope","")) for f in sel)
    notes_len=sum(len(facts[f].get("notes_for_writer","")) for f in sel)
    rows.append({"theme":th,"problem_theme":th in PROBLEM,"ledger_facts":len(order),"ambiguous_facts":sum(1 for f in order if facts[f]['tag'].startswith('AMBIGUOUS')),
        "selected":len(sel),"selected_ids":sel,"ledger_notes_total":len(notes_all),"ledger_notes_imperative_form":len(notes_imp),
        "notes_on_selected":len(notes_sel),"brief_imperative_sentences":len(imp_brief),"brief_imperative_texts":imp_brief,
        "notes_survival":surv,"brief_chars_selected_facts":len(body),"storyline_dup_line_in_facts":body.lstrip().startswith("Storyline"),
        "brief_has_fact_ids":bool(re.search(r"\b[A-Z]{1,5}-?\d+",body)),
        "armD_claim_only_chars":claim_only,"armD_claim_scope_conditions_chars":claim_cond,"armD_notes_chars":notes_len})
json.dump(rows,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"ledger_stats_01.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"ledger_stats_01.md"),"w",encoding="utf-8") as w:
    w.write("| theme | 問題 | ledger facts | selected | ledger notes(総/命令形) | selected上のnotes | briefの命令文数 | notes逐語級残存(>=12字) | Storyline重複行 | brief字数 | 案D claim字数 | 案D claim+scope+cond字数 | 案D notes字数 |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        sv=sum(1 for s in r["notes_survival"] if s["verbatim_like(>=12)"])
        w.write(f"| {r['theme']} | {'Y' if r['problem_theme'] else '-'} | {r['ledger_facts']} | {r['selected']} | {r['ledger_notes_total']}/{r['ledger_notes_imperative_form']} | {r['notes_on_selected']} | {r['brief_imperative_sentences']} | {sv}/{r['notes_on_selected']} | {'Y' if r['storyline_dup_line_in_facts'] else '-'} | {r['brief_chars_selected_facts']} | {r['armD_claim_only_chars']} | {r['armD_claim_scope_conditions_chars']} | {r['armD_notes_chars']} |\n")
print(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"ledger_stats_01.md"),encoding="utf-8").read())
