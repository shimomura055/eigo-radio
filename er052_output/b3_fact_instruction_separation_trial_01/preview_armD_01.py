# Phase1 設計検証 (API 0件・Production不変更): 案D(決定論assemble)を既存9テーマの selected_fact_ids でオフライン再現し、
# (a) Facts側に命令形が残るか (b) 台帳notesがConstraints側に全部入るか (c) parse_brief_md / dryrun_annotate が通るか を確認する。
# 実行 (repo root): py -I er052_output/b3_fact_instruction_separation_trial_01/preview_armD_01.py
import json, os, re, sys
sys.path.insert(0, os.getcwd())
import er052_factlock_astra_e2e_runner_01 as run
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, "armD_preview_01"); os.makedirs(OUT, exist_ok=True)
R = "er052_output/factlock_astra_e2e_trial_01/g0_real_annotation_01"
THEMES = ["semiconductor_earnings","small_bag","space_weapons","hormuz","central_bank_mortgage","meta","byd_recall","openai_copyright","streaming_price"]
HEAD = re.compile(r"^\[(VERIFIED|AMBIGUOUS[^\]]*)\]\s+([A-Za-z0-9_\-]+): (.*)$"); FLD = re.compile(r"^  (\w+): (.*)$")
LINK = re.compile(r"\s*\(\[[^\]]*\]\(https?://[^)]*\)\)|\s*\(https?://[^)]*\)")   # ([host](url)) 形式の出典リンクを除去
IMP = re.compile(r"(ないこと|こと[。]?$|書かない|断定しない|付け加えない|補わない|混同しない|扱わない|分けて扱う|区別する|区別して|として扱う|言い換えない|一般化しない|帰属させない|結び付けない|同一視しない)")
def parse(t):
    f, order, cur = {}, [], None
    for ln in t.replace("\r\n", "\n").split("\n"):
        m = HEAD.match(ln)
        if m: cur = m.group(2); f[cur] = {"tag": m.group(1), "claim": m.group(3)}; order.append(cur); continue
        m = FLD.match(ln)
        if m and cur: f[cur][m.group(1)] = m.group(2)
    return f, order
res = []
for th in THEMES:
    d = f"{R}/{th}/shared"
    facts, order = parse(open(f"{d}/ledger.txt", encoding="utf-8").read())
    ev = json.load(open(f"{d}/fact_selection_evidence_original.json", encoding="utf-8"))
    sel = [f for f in order if f in set(ev["selected_fact_ids"])]
    bullets = [f"- {LINK.sub('', facts[f]['claim']).strip()}" for f in sel]
    cons = [(f, LINK.sub("", facts[f]["notes_for_writer"]).strip()) for f in sel if facts[f].get("notes_for_writer")]
    amb = [(f, LINK.sub("", facts[f]["ambiguity_note"]).strip()) for f in sel if facts[f].get("ambiguity_note")]
    story = ev["selected_storyline"]
    brief = "# Selected Fact Brief\n\n## Storyline\n" + story + "\n\n## Selected Facts\n" + "\n".join(bullets) + "\n"
    constraints = "【Writerへの注意(事実ではない。台帳の notes_for_writer をそのまま転記)】\n" + "\n".join(f"- ({f}) {t}" for f, t in cons) + "\n"
    storyline_p, facts_p = run.parse_brief_md(brief)           # W-1 R0 の parse_brief_md が通るか
    ann = run.dryrun_annotate(brief)                             # 決定論の仮注記が通るか (Facts節のみ対象)
    n_tag = len(re.findall(r"【事実\d+】", ann))
    imp_in_facts = [b for b in bullets if IMP.search(b)]
    open(os.path.join(OUT, f"{th}__brief.md"), "w", encoding="utf-8").write(brief)
    open(os.path.join(OUT, f"{th}__constraints.md"), "w", encoding="utf-8").write(constraints)
    res.append({"theme": th, "selected": sel, "fact_bullets": len(bullets), "constraints": len(cons), "ambiguity_notes_selected": len(amb),
                "imperative_pattern_in_fact_bullets": len(imp_in_facts), "imperative_texts": imp_in_facts,
                "parse_brief_md_ok": bool(storyline_p and facts_p), "dryrun_annotate_tags": n_tag,
                "tags_equal_bullets": n_tag == len(bullets), "brief_chars": len(facts_p),
                "link_markup_remaining": sum(1 for b in bullets if "](" in b)})
json.dump(res, open(os.path.join(H, "armD_preview_summary_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in res: print({k: v for k, v in r.items() if k not in ("selected", "imperative_texts")})
