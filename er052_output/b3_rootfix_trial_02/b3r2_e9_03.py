# -*- coding: utf-8 -*-
"""ROOTFIX-02 Phase 2b 段階2: E9 (Writer R0 only) for D-det v2. DEV/Trial only; not Production.
  run   : 6 themes x R0 x 1 (paid, cap JPY20, technical retry only)  -> e9/<theme>/Ddetv2/
  eval  : deterministic M10 measures + articles dump (no API)         -> e9/eval_e9_03.json, e9/e9_articles_03.md
mainで実行すること(Trial runnerがer012_e系をimportするため)。対照は ROOTFIX-01 E9 既存出力(新規callなし)。"""
import sys, os, re, json, time, difflib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b3r2_driver_01 as DR
import b3r2_eval_01 as E
import b3r2_rank_02 as R2
E.RK = R2
from b3sep_common_01 import THEMES, E9_THEMES, theme_inputs, rj, rd, wj, wt, sha, MODEL
import b3sep_build_01 as B
T1 = DR.T1
E9 = f"{HERE}/e9"
CAP9 = 20.0
ARM = "Ddetv2"


class Stop(RuntimeError):
    pass


def spent9():
    if not os.path.exists(DR.LEDGER_COST):
        return 0.0
    rows = [json.loads(l) for l in open(DR.LEDGER_COST, encoding="utf-8") if l.strip()]
    return sum(r["jpy"] for r in rows if str(r.get("arm", "")).startswith("E9_"))


def build_inputs(th):
    ti = theme_inputs(th)
    ev = ti["ev"]
    ids = [i for i in ev["selected_fact_ids"] if i in B.parse_ledger(ti["ledger"])[0]]
    der = E.ddet(ti["ledger"], ids, ev["selected_storyline"])
    brief_plain, annotated, side = E.build_annotated(ti["ledger"], ids, ev["selected_storyline"], der)
    d = B.assemble_D(ti["ledger"], ids, ev["selected_storyline"], E.BASE_VARIANT)
    import er052_factlock_astra_e2e_runner_01 as run
    story_m, facts_ann = run.parse_brief_md(annotated)
    news = B.compose_news_field(facts_ann, d["constraints_text"])
    return ti, der, annotated, story_m, news, d


def cmd_run(themes):
    import er019_family_x_ja_writer_o_r1_r2_01 as jaw
    import er052_factlock_writer_trial_01_run as fl
    import er052_factlock_astra_e2e_runner_01 as run
    vfl01, cl, rawp, client = DR._client_setup("e9")
    cur = 0
    for th in themes:
        od = f"{E9}/{th}/{ARM}"
        if os.path.exists(f"{od}/r0_meta.json"):
            print("skip(existing)", od)
            continue
        ti, der, annotated, story_m, news, d = build_inputs(th)
        wt(f"{od}/news_field.txt", news)
        wt(f"{od}/brief_annotated.md", annotated)
        wt(f"{od}/storyline_marked.txt", story_m)
        s0 = spent9()
        if s0 + 1.24 > CAP9:
            raise Stop(f"[STOP] cap: {s0:.2f}+1.24>{CAP9}")
        saved, calls = fl.apply_factlock_patches(), []
        o_fresh, o_prev = jaw.call_fresh, jaw.call_with_previous_response_id

        def fresh(c, developer, user, effort, stage, _o=o_fresh):
            r = _o(c, developer, user, effort, stage)
            calls.append({"stage": stage, "response_id": r.id, "model": r.model, "text": r.output_text.strip(), "user": user})
            return r

        def stop_r1(*x, **k):
            raise run.StopAfterR0()
        jaw.call_fresh, jaw.call_with_previous_response_id = fresh, stop_r1
        t0 = time.time()
        try:
            try:
                jaw.run_ja_writer_o_r1_r2(client, story_m, news, full_ledger_text=None)
            except run.StopAfterR0:
                pass
        finally:
            jaw.call_fresh, jaw.call_with_previous_response_id = o_fresh, o_prev
            fl.restore_factlock_patches(saved)
        lat = time.time() - t0
        jpy, rows, cur = DR._cost_since(rawp, cur)
        if not calls:
            raise Stop("[STOP] no R0 call captured")
        if not str(calls[-1]["model"]).startswith(MODEL):
            raise Stop(f"[STOP] model mismatch {calls[-1]['model']}")
        wt(f"{od}/r0_with_tags.md", calls[-1]["text"])
        wt(f"{od}/r0_prompt.txt", calls[0]["user"])
        wj(f"{od}/r0_meta.json", {"theme": th, "arm": ARM, "calls": [{k: v for k, v in c.items() if k not in ("text", "user")} for c in calls],
                                   "prompt_sha256": sha(calls[0]["user"]), "latency_seconds": round(lat, 1), "n_api_rows": len(rows), "usage": DR._usage(rows)})
        rec = {"arm": "E9_" + ARM, "theme": th, "rep": 1, "kind": "r0", "jpy": round(jpy, 4), "n_api_rows": len(rows), "latency_seconds": round(lat, 1),
               "model": calls[-1]["model"], "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
        DR._append_cost(rec)
        print("done E9", th, rec["jpy"], "total", round(s0 + jpy, 2), flush=True)


INTERNAL = re.compile(r"Ledger|台帳|notes|事実ではありません|事実\d+について|Writerへの|fact_id|中核数値|周辺数値")


def longest_common(a, b):
    m = difflib.SequenceMatcher(None, a, b, autojunk=False).find_longest_match(0, len(a), 0, len(b))
    return m.size, a[m.a:m.a + m.size]


def measure(th):
    import er052_factlock_writer_trial_01_run as fl
    import er052_factlock_astra_e2e_runner_01 as run
    import er003_audio_tts_asr_safety as safety
    od = f"{E9}/{th}/{ARM}"
    final = rd(f"{od}/r0_with_tags.md")
    ann = rd(f"{od}/brief_annotated.md")
    news = rd(f"{od}/news_field.txt")
    ti, der, _, _, _, d = build_inputs(th)
    facts, _ = B.parse_ledger(ti["ledger"])
    ids = [i for i in ti["ev"]["selected_fact_ids"] if i in facts]
    facts_map = fl.parse_annotated_facts(ann)
    sents = fl.split_sentences(final)
    tags_used = sorted({t for s in sents for t in s["tags"]})
    out_of_range = [t for t in tags_used if t not in facts_map]
    clean = run.clean_ja_for_next(final).strip()
    leak_fail = None
    try:
        run.assert_no_tag_leak(clean)
    except Exception as ex:
        leak_fail = str(ex)[:100]
    facts_text_only = news.split("\nWriterへの注意")[0]
    cons_sents = [s.strip() for s in re.findall(r"[^。]+。?", B.clean(" ".join(B.clean(facts[i].get("notes_for_writer", "")) for i in ids))) if len(s.strip()) >= 12]
    carry = []
    for sn in cons_sents:
        n, sub = longest_common(sn, clean)
        if n >= 12 and sub not in facts_text_only:
            carry.append(sub)
    tagged_constraint = []
    for s in sents:
        if s["tags"] and not s["is_title"]:
            for c in cons_sents:
                n, sub = longest_common(c, s["text"])
                if n >= 12 and sub not in facts_text_only:
                    tagged_constraint.append({"tags": s["tags"], "sentence": s["text"][:80], "overlap": sub})
                    break
    cons_lines_tagged = [ln for ln in news.split("\n") if ln.startswith("- ") and "【事実" in ln and "について" in ln[:12]]
    sym = safety.detect_prohibited_symbols(clean, "ja")
    art = R2.nfkc(clean)
    core_s = sorted({R2.nfkc(i["surface"]) for i in der["items"] if i["role"] == "core"})
    per_s = sorted({R2.nfkc(i["surface"]) for i in der["items"] if i["role"] != "core"} - set(core_s))
    core_hit = [s for s in core_s if R2.contains(art, s)]
    per_hit = [s for s in per_s if R2.contains(art, s)]
    article_nums = list(dict.fromkeys(R2.extract_surfaces(clean)))
    news_plain = R2.nfkc(R2.strip_marks(news))
    novel = [s for s in article_nums if not R2.contains(news_plain, s)]
    return {"theme": th, "chars": len(clean), "n_facts": len(facts_map), "tags_used": tags_used, "tags_out_of_range": out_of_range,
            "tag_check_pass": (not out_of_range) and leak_fail is None, "tag_leak": leak_fail,
            "constraint_lines_with_fact_tag": cons_lines_tagged, "notes_verbatim_carry": carry, "tagged_sentences_on_constraint_text": tagged_constraint,
            "internal_terms": sorted(set(INTERNAL.findall(clean))), "fact_ids_in_article": sorted(set(fl.ID_RE.findall(clean))),
            "ledger_ue_verbatim": "Ledger上" in clean, "symbol_gate_hits": [x.get("token") for x in sym], "r0_echo": run.detect_r0_echo(clean),
            "core_surfaces": core_s, "core_in_article": core_hit, "peripheral_surfaces": per_s, "peripheral_in_article": per_hit,
            "article_number_surfaces": article_nums, "article_numbers_not_in_news_field": novel}


def cmd_eval():
    rows, art = [], ["# E9 articles D-det v2 (R0 only; read these in full)\n"]
    for th in E9_THEMES:
        if not os.path.exists(f"{E9}/{th}/{ARM}/r0_with_tags.md"):
            print("missing", th)
            continue
        rows.append(measure(th))
        art.append(f"\n\n## {th} / {ARM}\n" + rd(f"{E9}/{th}/{ARM}/r0_with_tags.md"))
        for arm in ("C0", "D"):
            p = f"{T1}/runs/E9/{th}/{arm}/r0_with_tags.md"
            if os.path.exists(p):
                art.append(f"\n\n### (control ROOTFIX-01 E9 {arm}) {th}\n" + rd(p))
    wt(f"{E9}/e9_articles_03.md", "\n".join(art))
    wj(f"{E9}/eval_e9_03.json", rows)
    r = rows
    print("n", len(r), "tag_pass", sum(x["tag_check_pass"] for x in r), "cons_line_tag", sum(len(x["constraint_lines_with_fact_tag"]) for x in r),
          "carry", sum(len(x["notes_verbatim_carry"]) for x in r), "tagged_on_constraint", sum(len(x["tagged_sentences_on_constraint_text"]) for x in r),
          "internal", [(x["theme"], x["internal_terms"]) for x in r if x["internal_terms"]], "ids", [x["theme"] for x in r if x["fact_ids_in_article"]],
          "Ledger上", [x["theme"] for x in r if x["ledger_ue_verbatim"]], "sym", sum(len(x["symbol_gate_hits"]) for x in r), "echo", sum(x["r0_echo"]["n"] for x in r))
    for x in r:
        print(x["theme"], "core", len(x["core_in_article"]), "/", len(x["core_surfaces"]), "per_in_article", x["peripheral_in_article"], "novel", x["article_numbers_not_in_news_field"])


if __name__ == "__main__":
    try:
        if sys.argv[1] == "run":
            cmd_run(sys.argv[2].split(",") if len(sys.argv) > 2 else E9_THEMES)
        elif sys.argv[1] == "eval":
            cmd_eval()
    except Stop as ex:
        print(ex)
        sys.exit(46)
