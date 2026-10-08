# -*- coding: utf-8 -*-
"""ASTRA-REVISE-MATRIX-02 prep (no API). hormuz R0 (existing Fact Lock v1) + small_bag annotated brief."""
import hashlib, json, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT); sys.path.insert(0, ROOT)
import er052_factlock_writer_trial_01_run as h

FL = "er052_output/factlock_writer_trial_01"
B2 = f"{FL}/astra_revise_matrix_02"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

# ---- hormuz: selection rule b2 r1 completed
cand = [(f"{FL}/runs/hormuz/control/b{b}__factlock__r{r}") for b in (2, 1, 3, 4) for r in (1, 2)]
chosen = None
for d in cand:
    mf = f"{d}/manifest.json"
    if os.path.exists(mf) and json.load(open(mf, encoding="utf-8")).get("exit_reason") == "completed" and os.path.exists(f"{d}/ja_writer/original.md"):
        chosen = d; break
assert chosen.endswith("b2__factlock__r1"), chosen
orig = f"{chosen}/ja_writer/original.md"
wt = f"{chosen}/ja_writer/original_with_tags.md"
r0 = h.strip_tags(open(orig, encoding="utf-8").read()).strip() + "\n"
assert h.strip_tags(open(wt, encoding="utf-8").read()).strip() + "\n" == r0, "with_tags strip != original"
os.makedirs(f"{B2}/inputs/hormuz", exist_ok=True)
open(f"{B2}/inputs/hormuz/R0.md", "w", encoding="utf-8", newline="").write(r0)
info = {"chosen_run": chosen, "original_md": orig, "original_sha": sha(orig), "R0_sha": hashlib.sha256(r0.encode()).hexdigest(),
        "with_tags_equals_strip": True, "ledger": f"{chosen}/research_ledger/verified_fact_ledger.txt",
        "ledger_sha": sha(f"{chosen}/research_ledger/verified_fact_ledger.txt"),
        "b3_brief": f"{chosen}/storyline_b3/selected_brief.md", "b3_brief_sha": sha(f"{chosen}/storyline_b3/selected_brief.md"),
        "annotated_brief": f"{FL}/briefs/hormuz/b2/selected_brief_factlock.md", "annotated_brief_sha": sha(f"{FL}/briefs/hormuz/b2/selected_brief_factlock.md"),
        "r0_chars_total": len(r0)}
json.dump(info, open(f"{B2}/inputs/hormuz/R0_SOURCE.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("hormuz", info)

# ---- small_bag annotated brief
E2E = "er052_output/gpt6_wiring_e2e_01/run_02"
src = f"{E2E}/storyline_b3/selected_brief.md"
text = open(src, encoding="utf-8").read()
head, facts = text.split("## Selected Facts\n", 1)
facts = facts.strip()
# 元briefのSelected Factsは箇条書きでなく1段落。文境界で3事実(ELLE / 秋ランウェイまとめ / Who What Wear 10月)に分け、本文は逐語。
cut1 = facts.index("Fall 2026のランウェイまとめでは")
cut2 = facts.index("さらに、Who What Wearの2026年10月")
f1, f2, f3 = facts[:cut1].strip(), facts[cut1:cut2].strip(), facts[cut2:].strip()
assert (f1 + f2 + f3).replace("\n", "") == facts.replace("\n", "")
f3 = f3.replace("さらに、Who What Wearの", "Who What Wearの", 1) if False else f3  # 逐語保持(変更しない)
CORE = [("C1", ["2026年9月"], "ELLEの紹介時期"), ("C2", ["2026年10月"], "micro見解の時期")]
PERI = ["Fall 2026", "2026年"]   # 'Fall 2026'(季節名)・Storyline冒頭の'2026年'
lits = {"2026年9月": "【中核数値】", "2026年10月": "【中核数値】", "Fall 2026": "【周辺数値】", "2026年": "【周辺数値】"}
pat = re.compile("|".join(re.escape(l) for l in sorted(lits, key=len, reverse=True)))
ann = lambda s: pat.sub(lambda m: m.group(0) + lits[m.group(0)], s)
out = ann(head) + "## Selected Facts\n" + "\n".join(f"- 【事実{i}】{ann(f)}" for i, f in enumerate((f1, f2, f3), 1)) + "\n"
rest = re.sub("|".join(re.escape(l) + r"【(?:中核|周辺)数値】" for l in sorted(lits, key=len, reverse=True)), " ", out)
left = h.extract_numbers(h.TAG_RE.sub(" ", rest))
assert not left, [t["surface"] for t in left]
d = f"{B2}/inputs/small_bag"
os.makedirs(d, exist_ok=True)
open(f"{d}/selected_brief_factlock.md", "w", encoding="utf-8", newline="").write(out)
core_json = {"slug": "small_bag", "brief": "e2e_run_02", "source_brief": src,
             "core": [{"id": c, "literals": l, "role": r} for c, l, r in CORE], "peripheral": PERI,
             "reason": "記事の軸は『数値』ではなく編集上の注目の区別。時期(2026年9月=ELLE紹介、2026年10月=micro見解)のみ中核(2件)。Fall 2026(季節名)と2026年(storyline冒頭)は周辺。",
             "max_core_per_article": 3}
json.dump(core_json, open(f"{d}/core_numbers.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(out)
print({"src_sha": sha(src), "ledger_sha": sha(f"{E2E}/research_ledger/verified_fact_ledger.txt"), "annotated_sha": sha(f"{d}/selected_brief_factlock.md")})
