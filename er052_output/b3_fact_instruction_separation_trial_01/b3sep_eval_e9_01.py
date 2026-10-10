# -*- coding: utf-8 -*-
"""E9 evaluation (Writer R0 only): D(Dfull) vs C0. Deterministic measures + files for human reading.
Run: .venv/Scripts/python.exe -X utf8 b3sep_eval_e9_01.py   -> eval/eval_e9_02.json, eval/e9_articles_02.md"""
import sys, os, re, json, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b3sep_common_01 import *
import b3sep_build_01 as B
import er052_factlock_astra_e2e_runner_01 as run
import er052_factlock_writer_trial_01_run as fl
import er003_audio_tts_asr_safety as safety

INTERNAL = re.compile(r"Ledger|台帳|notes|事実ではありません|事実\d+について|Writerへの|fact_id")


def longest_common(a, b):
    m = difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b))
    return m.size, a[m.a:m.a + m.size]


def measure(th, arm):
    od = f"{HERE}/runs/E9/{th}/{arm}"
    final = rd(f"{od}/r0_with_tags.md")
    ann = rd(f"{od}/brief_annotated.md")
    news = rd(f"{od}/news_field.txt")
    ti = theme_inputs(th)
    facts, _ = B.parse_ledger(ti["ledger"])
    ids = ti["ev"]["selected_fact_ids"]
    facts_map = fl.parse_annotated_facts(ann)
    sents = fl.split_sentences(final)
    tags_used = sorted({t for s in sents for t in s["tags"]})
    out_of_range = [t for t in tags_used if t not in facts_map]
    clean = run.clean_ja_for_next(final).strip()
    leak_fail = None
    try:
        run.assert_no_tag_leak(clean)
    except Exception as ex:  # noqa
        leak_fail = str(ex)[:100]
    # notes carry: sentences of selected notes with a >=12 char verbatim overlap with the article that is not explained by the Facts text
    facts_text_only = news.split("\nWriterへの注意")[0]
    carry = []
    for i in ids:
        nt = B.clean(facts[i].get("notes_for_writer", ""))
        for sn in re.findall(r"[^。]+。?", nt):
            sn = sn.strip()
            if len(sn) < 12:
                continue
            n, sub = longest_common(sn, clean)
            if n >= 12 and sub not in facts_text_only:
                carry.append({"fact": i, "overlap": sub})
    instr_tags = [t for t in tags_used if t in facts_map and B.IMP.search(facts_map[t])]
    sym = safety.detect_prohibited_symbols(clean, "ja")
    # tags on sentences whose text is mostly a constraint sentence
    cons_sents = [s.strip() for s in re.findall(r"[^。]+。?", B.clean(" ".join(B.clean(facts[i].get("notes_for_writer", "")) for i in ids))) if len(s.strip()) >= 12]
    tagged_constraint = []
    for s in sents:
        if s["tags"] and not s["is_title"]:
            for c in cons_sents:
                n, sub = longest_common(c, s["text"])
                if n >= 12 and sub not in facts_text_only:
                    tagged_constraint.append({"tags": s["tags"], "sentence": s["text"][:80], "overlap": sub})
                    break
    return {"theme": th, "arm": arm, "chars": len(clean), "n_facts": len(facts_map), "tags_used": tags_used, "tags_out_of_range": out_of_range, "tags_pointing_at_instruction_facts": instr_tags, "instruction_fact_lines_in_input": [t for t in facts_map if B.IMP.search(facts_map[t])],
            "tag_check_pass": (not out_of_range) and leak_fail is None, "tag_leak": leak_fail,
            "notes_verbatim_carry": carry, "tagged_sentences_on_constraint_text": tagged_constraint,
            "internal_terms": sorted(set(INTERNAL.findall(clean))), "fact_ids_in_article": sorted(set(fl.ID_RE.findall(clean))),
            "ledger_ue_verbatim": "Ledger上" in clean, "symbol_gate_hits": [x.get("token") for x in sym], "r0_echo": run.detect_r0_echo(clean),
            "hedge_words": sorted(set(re.findall(r"確定|断定|言い切れ|確認でき|分かっていない|不明", clean)))}


def main():
    rows, art = [], ["# E9 articles (R0 only; read these in full)\n"]
    for th in E9_THEMES:
        for arm in ("C0", "D"):
            if not os.path.exists(f"{HERE}/runs/E9/{th}/{arm}/r0_with_tags.md"):
                print("missing", th, arm)
                continue
            rows.append(measure(th, arm))
            art.append(f"\n\n## {th} / {arm}\n" + rd(f"{HERE}/runs/E9/{th}/{arm}/r0_with_tags.md"))
    wt(f"{HERE}/eval/e9_articles_02.md", "\n".join(art))
    wj(f"{HERE}/eval/eval_e9_02.json", rows)
    for arm in ("C0", "D"):
        r = [x for x in rows if x["arm"] == arm]
        print(arm, "n", len(r), "tag_pass", sum(x["tag_check_pass"] for x in r), "out_of_range", sum(len(x["tags_out_of_range"]) for x in r),
              "notes_carry", sum(len(x["notes_verbatim_carry"]) for x in r), "tagged_on_constraint", sum(len(x["tagged_sentences_on_constraint_text"]) for x in r),
              "internal", [x["theme"] for x in r if x["internal_terms"]], "ids", [x["theme"] for x in r if x["fact_ids_in_article"]],
              "Ledger上", [x["theme"] for x in r if x["ledger_ue_verbatim"]], "sym", sum(len(x["symbol_gate_hits"]) for x in r),
              "echo", sum(x["r0_echo"]["n"] for x in r))
    for x in rows:
        print(x["theme"], x["arm"], "tags", x["tags_used"], "oor", x["tags_out_of_range"], "carry", x["notes_verbatim_carry"], "tc", x["tagged_sentences_on_constraint_text"], "int", x["internal_terms"], "sym", x["symbol_gate_hits"])


if __name__ == "__main__":
    main()
