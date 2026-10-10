# Phase1 read-only: ledger.txt の notes_for_writer / ambiguity_note が Researcher draft / Verification のどちら由来かを、
# 現行 build_verified_ledger_text の規則 (er003_v1_en_direct_vfl_01_generate.py L279-310) と照合する。API なし。
import json, re, os, sys
H=os.path.dirname(os.path.abspath(__file__))
S="er052_output/factlock_astra_e2e_trial_01/stage_r"
HEAD=re.compile(r"^\[(VERIFIED|AMBIGUOUS[^\]]*)\]\s+([A-Za-z0-9_\-]+): (.*)$"); FLD=re.compile(r"^  (\w+): (.*)$")
res={}
for th in ["semiconductor_earnings","central_bank_mortgage","byd_recall","openai_copyright","streaming_price","inbound_tourism"]:
    led=open(f"{S}/{th}/research_ledger/verified_fact_ledger.txt",encoding="utf-8").read().replace("\r\n","\n")
    dr={f["fact_id"]:f for f in json.load(open(f"{S}/{th}/research_ledger/fact_ledger_draft.json",encoding="utf-8"))["facts"]}
    ve={v["fact_id"]:v for v in json.load(open(f"{S}/{th}/research_ledger/fact_ledger_verification.json",encoding="utf-8"))["verifications"]}
    cur=None; rows=[]; 
    parsed={}
    for ln in led.split("\n"):
        m=HEAD.match(ln)
        if m: cur=m.group(2); parsed[cur]={"tag":m.group(1)}; continue
        m=FLD.match(ln)
        if m and cur: parsed[cur][m.group(1)]=m.group(2)
    n_notes=n_notes_eq=n_amb=n_amb_from_verif=n_amb_from_draft=0; draft_amb_not_shown=0
    for fid,p in parsed.items():
        d=dr[fid]
        if "notes_for_writer" in p:
            n_notes+=1; n_notes_eq+= (p["notes_for_writer"]==d.get("notes_for_writer"))
        if "ambiguity_note" in p:
            n_amb+=1
            if p["ambiguity_note"]==(d.get("ambiguity") or ve[fid]["verification_notes"]):
                if d.get("ambiguity"): n_amb_from_draft+=1
                else: n_amb_from_verif+=1
        if p["tag"]=="VERIFIED" and d.get("ambiguity"): draft_amb_not_shown+=1
    res[th]={"facts":len(parsed),"notes_in_ledger":n_notes,"notes_identical_to_researcher_draft":n_notes_eq,
             "ambiguity_note_lines":n_amb,"ambiguity_note_from_researcher_ambiguity":n_amb_from_draft,"ambiguity_note_from_verifier_notes":n_amb_from_verif,
             "researcher_ambiguity_present_but_not_printed_for_VERIFIED":draft_amb_not_shown}
json.dump(res,open(os.path.join(H,"ledger_provenance_check_01.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
for k,v in res.items(): print(k,v)
