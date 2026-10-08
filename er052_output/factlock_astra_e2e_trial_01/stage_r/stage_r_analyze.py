import sys, os, re, json, hashlib
sys.path.insert(0, "er052_output/factlock_astra_e2e_trial_01")
import b3_annotation_check_01 as c
base = "er052_output/factlock_astra_e2e_trial_01/stage_r"
new6 = ["byd_recall","openai_copyright","central_bank_mortgage","inbound_tourism","streaming_price","semiconductor_earnings"]
old4 = {"meta":"er052_output/open233_b3_trial_01/runs/meta/nb/V0/b2/storyline_b3",
        "hormuz":"er052_output/open233_b3_trial_01/runs/hormuz/nb/V0/b2/storyline_b3",
        "space_weapons":"er052_output/open233_b3_trial_01/runs/space_weapons/nb/V0/b2/storyline_b3",
        "small_bag":"er052_output/gpt6_wiring_e2e_01/run_02/storyline_b3"}
def rd(p): return open(p, encoding="utf-8", newline="").read()
def lf_sha(p):
    return hashlib.sha256(rd(p).replace("\r\n","\n").replace("\r","\n").encode("utf-8")).hexdigest()
slugs = [s for s in new6 if os.path.exists(f"{base}/{s}/research_ledger/verified_fact_ledger.txt")] + list(old4)
# schema
rows = []; frozen = {}
for s in slugs:
    lp = f"{base}/{s}/research_ledger/verified_fact_ledger.txt"
    led = c.parse_ledger(rd(lp)); sch = c.ledger_schema(led)
    fc = sch["field_counts"]
    nver = sum(1 for r in led.values() if r["status"]=="VERIFIED")
    q_no_nv = [rid for rid,r in led.items() if "numeric_value" not in r["fields"] and c.QUANT_WORD_RE.search(c.strip_scope(r["statement"]))]
    rows.append((s, len(led), nver, fc.get("numeric_value",0), fc.get("date_or_period",0), q_no_nv, sch))
    f = {"ledger": {"path": lp, "sha256_lf": lf_sha(lp)}}
    sd = f"{base}/{s}/storyline_b3"
    for fn in ("selected_brief.md","fact_selection_evidence.json","full_ledger.json"):
        p = f"{sd}/{fn}"
        if os.path.exists(p): f[fn] = {"path": p, "sha256_lf": lf_sha(p)}
        else: f[fn] = None
    frozen[s] = f
json.dump({"note":"LF正規化後sha256(CRLF/CR->LF、UTF-8)。B3未生成のテーマはnull。","themes":frozen}, open(f"{base}/FROZEN_INPUTS_SHA256.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
out = ["# 台帳スキーマ点検(仕様v2 §8、b3_annotation_check_01.ledger_schemaを使用)\n",
 "| slug | 記録数 | VERIFIED | numeric_value欄あり | date_or_period欄あり | 量語あり&numeric_value欄なし | 代替規則(nv) | 代替規則(date) |","|---|---|---|---|---|---|---|---|"]
for s,n,v,nv,dp,q,sch in rows:
    out.append(f"| {s} | {n} | {v} | {nv} | {dp} | {len(q)}件{(' '+','.join(q)) if q else ''} | {'適用' if sch['numeric_value_fallback_to_statement'] else '不要'} | {'適用' if sch['date_or_period_fallback_to_statement'] else '不要'} |")
out.append("\n欄名ごとの件数と警告:")
for s,n,v,nv,dp,q,sch in rows:
    out.append(f"- {s}: field_counts={sch['field_counts']}; warnings={sch['warnings']}")
open(f"{base}/LEDGER_SCHEMA_CHECK.md","w",encoding="utf-8").write("\n".join(out)+"\n")
# old vs new B3
res = {}
for s,od in old4.items():
    ev_o = json.load(open(f"{od}/fact_selection_evidence.json",encoding="utf-8"))
    ev_n = json.load(open(f"{base}/{s}/storyline_b3/fact_selection_evidence.json",encoding="utf-8"))
    led = rd(f"{base}/{s}/research_ledger/verified_fact_ledger.txt")
    ledn = set(c.digit_runs(led))
    def extra(ev): return sorted(set(c.digit_runs(ev["selected_fact_brief_text"])) - ledn)
    res[s] = {"old_ids": ev_o["selected_fact_ids"], "new_ids": ev_n["selected_fact_ids"],
      "old_len": len(ev_o["selected_fact_brief_text"]), "new_len": len(ev_n["selected_fact_brief_text"]),
      "old_nums_not_in_ledger": extra(ev_o), "new_nums_not_in_ledger": extra(ev_n),
      "same_text": ev_o["selected_fact_brief_text"]==ev_n["selected_fact_brief_text"],
      "old_storyline": ev_o["selected_storyline"], "new_storyline": ev_n["selected_storyline"],
      "new_soft_warnings": ev_n.get("soft_warnings")}
json.dump(res, open(f"{base}/OLD4_B3_DIFF.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
for r in rows: print(r[:5], r[5])
