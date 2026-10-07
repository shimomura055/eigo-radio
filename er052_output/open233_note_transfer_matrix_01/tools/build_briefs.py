# -*- coding: utf-8 -*-
"""OPEN-233-NOTE-TRANSFER-MATRIX-TRIAL-01 Phase A-3/A-4(Trial専用)。
固定brief本文(brief_gen/<slug>/storyline_b3/selected_brief.md)に、6条件(T0/T1/T2 x M0/M1)のNoteブロックだけを足す。
--summary: T1要約文を1回だけ生成(有料1call/テーマ)。--assemble: 決定論でbriefs/<slug>/<T><M>.md とMANIFESTを作る。"""
import argparse, hashlib, json, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT); os.chdir(ROOT)
B = "er052_output/open233_note_transfer_matrix_01"
CTRL = "er052_output/open233_polysemy_trial_02/ledgers/{s}/control/research_ledger/verified_fact_ledger.txt"
POLY = ("注意(多義): この表現は多義的なので、単語だけで機械的に解釈・翻訳せず、原文の文脈・主体・対象・前後関係から"
        "意味を確定して記事化すること。")
SEWER_GROUPS = [["F-003"], ["F-005", "F-006"], ["F-007"], ["F-012"], ["F-018"]]  # 本文3番目の箇条書きはF-005+F-006の統合


def sha(t): return hashlib.sha256(t.encode("utf-8")).hexdigest()


def ledger_notes(s):
    t = open(CTRL.format(s=s), encoding="utf-8").read()
    notes = {}
    for m in re.finditer(r"\[VERIFIED\] (\S+?): .*?\n((?:  .*\n)*)", t + "\n"):
        nm = re.search(r"^  notes_for_writer: (.*)$", m.group(2), re.M)
        notes[m.group(1)] = nm.group(1).strip() if nm else ""
    return notes


def split_brief(s):
    txt = open(f"{B}/brief_gen/{s}/storyline_b3/selected_brief.md", encoding="utf-8").read()
    head, facts = txt.split("\n## Selected Facts\n", 1)
    return head + "\n## Selected Facts\n", facts


def units_of(facts):
    """facts本文を行に分け、箇条書き行(- / ・)をunitとする。unitのline indexを返す。"""
    lines = facts.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("- ") or l.startswith("・")]
    return lines, idx


def groups_for(s, evid):
    ids = evid["selected_fact_ids"]
    return SEWER_GROUPS if s == "sewer" else [[i] for i in ids]


def gen_summary(s):
    import er019_family_x_entertainment_production_runner_01 as r
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er005_cost_logger as cl
    evid = json.load(open(f"{B}/brief_gen/{s}/storyline_b3/fact_selection_evidence.json", encoding="utf-8"))
    notes = ledger_notes(s)
    ids = evid["selected_fact_ids"]
    src = "\n".join(f"- {i}: {notes[i]}" for i in ids)
    prompt = ("以下は、記事化する各factについて台帳が持つ注意事項(notes_for_writer)の原文です。\n"
              "briefに添える注意として1〜3行に要約してください。新しい情報・解釈を加えないでください。"
              "出力は要約本文のみ(見出し・前置き・箇条書き記号なし、1行1文)。\n\n" + src)
    out = f"{B}/ledger/{s}"
    log = f"{out}/summary_usage.jsonl"
    if os.path.exists(f"{out}/notes_summary.txt"):
        raise SystemExit("notes_summary.txt既存(再生成しない)")
    cl.install(log)
    client = vfl01.get_client()
    with cl.logging_context("note_matrix", "t1_summary"):
        resp = client.responses.create(model=vfl01.MODEL, reasoning={"effort": vfl01.REASONING_EFFORT},
                                       input=[{"role": "user", "content": prompt}])
    text = resp.output_text.strip()
    open(f"{out}/notes_summary.txt", "w", encoding="utf-8", newline="").write(text + "\n")
    open(f"{out}/notes_summary_prompt.txt", "w", encoding="utf-8", newline="").write(prompt)
    json.dump({"model": resp.model, "response_id": resp.id, "text_sha256": sha(text),
               "cost": r.compute_stage_cost_breakdown(log)}, open(f"{out}/notes_summary_meta.json", "w"), ensure_ascii=False, indent=1)
    print(s, "summary:", text)


def assemble(s):
    head, facts = split_brief(s)
    evid = json.load(open(f"{B}/brief_gen/{s}/storyline_b3/fact_selection_evidence.json", encoding="utf-8"))
    notes = ledger_notes(s)
    groups = groups_for(s, evid)
    lines, idx = units_of(facts)
    assert len(idx) == len(groups), (s, len(idx), len(groups))
    summary = [x.rstrip() for x in open(f"{B}/ledger/{s}/notes_summary.txt", encoding="utf-8").read().strip().split(chr(10))]
    os.makedirs(f"{B}/briefs/{s}", exist_ok=True)
    man = {"slug": s, "selected_fact_ids": evid["selected_fact_ids"], "groups": groups, "conditions": {}}
    body_ref = None
    for T in ("T0", "T1", "T2"):
        for M in ("M0", "M1"):
            out = []
            nnote = 0
            gi = {i: g for i, g in zip(idx, groups)}
            for i, l in enumerate(lines):
                out.append(l)
                if i in gi:
                    ns = [f"注意: {notes[f]}" for f in gi[i]] if T == "T2" else []
                    if M == "M1":
                        if ns: ns[-1] = ns[-1] + " / " + POLY
                        else: ns = [POLY]
                    out.extend(ns); nnote += len(ns)
            text = "\n".join(out).rstrip("\n")
            if T == "T1":
                text += "\n\n" + "\n".join("注意(要約): " + x if k == 0 else x for k, x in enumerate(summary))
                nnote += len(summary)
            full = head + text + "\n"
            open(f"{B}/briefs/{s}/{T}{M}.md", "w", encoding="utf-8", newline="").write(full)
            man["conditions"][T + M] = {"sha256": sha(full), "note_lines": nnote}
    # 決定論チェック: 本文(Note行・Noteブロックを除いた部分)が6ファイルで一致
    bodies = set()
    for c in man["conditions"]:
        t = open(f"{B}/briefs/{s}/{c}.md", encoding="utf-8").read().split("\n")
        keep = []
        skip_tail = False
        for l in t:
            if l.startswith("注意(要約):"): skip_tail = True
            if skip_tail or l.startswith("注意"): continue
            keep.append(l)
        bodies.add(sha("\n".join(keep).strip("\n")))
    man["body_identical_across_6"] = len(bodies) == 1
    man["body_sha_variants"] = len(bodies)
    man["fixed_body_source_sha256"] = sha(open(f"{B}/brief_gen/{s}/storyline_b3/selected_brief.md", encoding="utf-8").read())
    man["notes_summary_sha256"] = sha("\n".join(summary))
    json.dump(man, open(f"{B}/briefs/{s}/MANIFEST.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(s, man["body_identical_across_6"], {k: v["note_lines"] for k, v in man["conditions"].items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--summary", action="store_true"); ap.add_argument("--assemble", action="store_true")
    ap.add_argument("--slug", required=True); a = ap.parse_args()
    if a.summary: gen_summary(a.slug)
    if a.assemble: assemble(a.slug)
