# -*- coding: utf-8 -*-
"""WRITER-DEV-RISK-FLAGGER-POST-EN-TRIAL-01 Phase1(JPY0, API非呼び出し): 英語稿の棚卸・台帳完全性確認・入力の固定。
既存成果物の読み取りのみ。新規生成なし。dev-check promptからの復元=既存本文の抽出であり再生成ではない。"""
import json, os, re, sys, glob, hashlib, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RUNS = os.path.join(REPO, "er052_output", "factlock_astra_e2e_trial_01", "runs")
sys.path.insert(0, os.path.join(REPO, "er052_output", "writer_dev_risk_flagger_01", "detectors"))
import ledger_restore_01 as LR
HDR = re.compile(r"^\[(?P<st>[A-Z_]+)(?:\s+-\s+[^\]]*)?\]\s+(?P<id>[^\s:]+):\s*(?P<text>.*)$")
LR._HDR = HDR
BROAD = re.compile(r"^\[")
def sha(b): return hashlib.sha256(b).hexdigest()
def rel(p): return os.path.relpath(p, REPO).replace("\\", "/")

# (unit, theme, kind, subpath, route, status_label)
UNITS = [
 ("U01","meta","file","new/b1b/article.md","Advanced B1b(英語Advanced)","採用稿(ADOPTED。Advanced checker RESOLVED_STAGE2_DOWNGRADE)"),
 ("U02","hormuz","file","new/b1b/article.md","Advanced B1b","採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRADE)"),
 ("U03","space_weapons","file","new/b1b/article.md","Advanced B1b(B1回復後の最終稿)","採用稿(ADOPTED。Adv RESOLVED_REWRITE_THEN_DOWNGRADE)"),
 ("U04","small_bag","file","new/b1b/article.md","Advanced B1b","採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRADE)"),
 ("U05","byd_recall","file","new/b1b/article.md","Advanced B1b","採用稿(ADOPTED。Adv RESOLVED_REWRITE_THEN_DOWNGRADE)"),
 ("U06","streaming_price","file","new/b1b/article.md","Advanced B1b","採用稿(ADOPTED。Adv RESOLVED_STAGE2_DOWNGRADE)"),
 ("U07","openai_copyright","prompt","new/b1b/audit/deviation_checks/advanced_attempt1.json","Advanced B1b(B1回復後のJA R2由来)","【STOP稿】翻訳後Hard STOP Check(JA_RECHECK_REQUIRED)で止まった英語生成稿。完成記事ではない。article.mdは存在せず、dev-check promptの『検証対象の記事』欄から復元"),
 ("U08","semiconductor_earnings","prompt","new/b1b/audit/deviation_checks/advanced_attempt1.json","Advanced B1b","【STOP稿】翻訳後Hard STOP Check(JA_RECHECK_REQUIRED)で止まった英語生成稿。完成記事ではない。article.mdは存在せず、dev-check promptから復元"),
 ("X09","hormuz","prompt","new/b1b_prev_b1/audit/deviation_checks/advanced_attempt1.json","Advanced B1b_prev_b1(B1回復前の初回英語稿)","【追加・既知例用】B1回復前の英語稿(ja_source MAJORでSTOPし、JA再生成=B1回復の起点となった稿)。採用稿ではない。dev-check promptから復元"),
 ("X10","space_weapons","file","new/b1b_prev_b1/article.md","Advanced B1b_prev_b1(B1回復前稿)","【追加・既知例用】B1回復前の英語稿(attempt2でdev-check COMPLIANTだったがB1回復で置換された)。最終採用稿ではない"),
 ("X11","openai_copyright","prompt","new/b1b_prev_b1/audit/deviation_checks/advanced_attempt1.json","Advanced B1b_prev_b1(B1回復前の初回英語稿)","【追加・最重要既知例用・STOP稿】B1回復前に翻訳後Hard STOP Check(changed_actor MAJOR, ja_source)で止まった英語生成稿。完成記事ではない。dev-check promptから復元"),
]
KNOWN = {
 "OpenAI actor drift文": r"put articles together",
 "Semiconductor不在断定文": r"does not explain how the two are connected",
 "Hormuz oil prices(Brent→oil prices)": r"oil prices shot up|oil prices",
 "Space『blow up Earth』": r"blow up Earth",
 "Space『capabilities未説明』断定": r"not (?:explained|disclosed)[^.]*capabilit|capabilities",
 "BYD In one line": r"## In one line",
}

def extract_from_prompt(path):
    d = json.load(open(path, encoding="utf-8"))
    p = d["prompt"]
    a = p.split("【検証対象の記事】", 1)[1].split("【判定対象は次の10種類", 1)[0].strip()
    led = p.split("【Verified Fact Ledger】", 1)[1].split("【検証対象の記事】", 1)[0].strip()
    return a, led, d

inv, ledgers, out_units = [], {}, []
bad = []
for uid, theme, kind, sub, route, status in UNITS:
    base = os.path.join(RUNS, theme, "new"); src_base = os.path.join(RUNS, theme)
    src = os.path.join(src_base, sub)
    led_path = os.path.join(base, "research_ledger", "verified_fact_ledger.txt")
    led_txt = open(led_path, encoding="utf-8").read()
    if kind == "file":
        raw = open(src, "rb").read()
        text = raw.decode("utf-8")
        recovered_from = None
        embedded_ledger_match = None
        gen_ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(os.path.getmtime(src)))
    else:
        text, emb_led, d = extract_from_prompt(src)
        raw = text.encode("utf-8")
        recovered_from = rel(src)
        embedded_ledger_match = (emb_led.strip() == led_txt.strip())
        gen_ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(os.path.getmtime(src)))
    outp = os.path.join(HERE, "inputs", "%s_%s.md" % (uid, theme))
    open(outp, "w", encoding="utf-8", newline="\n").write(text.strip() + "\n")
    hits = {}
    for k, pat in KNOWN.items():
        ms = [ln.strip() for ln in text.splitlines() if re.search(pat, ln)]
        if ms: hits[k] = ms
    # ledger completeness
    lines = led_txt.splitlines()
    n_broad = sum(1 for ln in lines if BROAD.match(ln))
    n_hdr = sum(1 for ln in lines if HDR.match(ln))
    facts = LR.parse_ledger_text(led_txt)
    ids = [f["fact_id"] for f in facts]
    ok = (n_broad == n_hdr == len(facts)) and len(set(ids)) == len(ids)
    states = [HDR.match(ln).group("st") for ln in lines if HDR.match(ln)]
    ledgers[theme] = dict(path=rel(led_path), sha256=sha(led_txt.encode("utf-8")), file_bytes_sha256=sha(open(led_path,"rb").read()),
                          expected_heading_lines=n_broad, regex_heading_lines=n_hdr, parsed_facts=len(facts), ids=ids, states=states, ok=ok)
    if not ok: bad.append(theme)
    out_units.append(dict(unit=uid, theme=theme, input_path=rel(outp), input_sha256=sha(open(outp,"rb").read()),
                          source_path=rel(src), source_kind=("article.md" if kind=="file" else "recovered_from_dev_check_prompt"),
                          source_file_sha256=sha(open(src,"rb").read()), text_sha256_stripped=sha(text.strip().encode("utf-8")),
                          route=route, status=status, gen_mtime=gen_ts, chars=len(text.strip()),
                          embedded_ledger_equals_research_ledger=embedded_ledger_match, known_hits=hits, ledger=theme))
    if kind == "file":
        out_units[-1]["file_text_equals_input"] = (text.strip() == open(outp, encoding="utf-8").read().strip())
json.dump(dict(units=out_units, ledgers=ledgers), open(os.path.join(HERE, "manifest_post_en_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("units", len(out_units), "ledger_bad", bad)
for u in out_units: print(u["unit"], u["theme"], u["chars"], u["source_kind"], u["embedded_ledger_equals_research_ledger"], list(u["known_hits"]))
for t, l in ledgers.items(): print(t, l["expected_heading_lines"], l["regex_heading_lines"], l["parsed_facts"], l["ok"], sorted(set(l["states"])))
