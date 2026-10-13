# -*- coding: utf-8 -*-
"""Phase 1 P1-2/P1-3: 決定論lint(R2)試作 + Melos原稿への机上適用(before/after)。JPY0・API呼出なし・Production非変更。
python er069_..._deskapply.py --out-dir er069_output/attribution_clip_split_trial_01"""
import sys, os, re, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er069_attribution_clip_split_trial_01_lib as L
import er062_family_z_structure_01 as st

RUN = "er026_output/family_z_production_e2e_01/melos/run_e2e_02"
CFG = {
    "a2": {"text": f"{RUN}/writer/std.md", "plan": f"{RUN}/segment_plan_a2.json", "attr": f"{RUN}/dialogue_attribution_a2.json",
           "repl": [
               ("“Give me three days to see my sister’s wedding,” Melos said. “Then I will return to you.”",
                "“Give me three days to see my sister’s wedding,” Melos answered, looking straight at the ruler. “Then I will return to you.”"),
           ]},
    "b1b": {"text": f"{RUN}/writer/r2.md", "plan": f"{RUN}/segment_plan_b1b.json", "attr": f"{RUN}/dialogue_attribution_b1b.json",
            "repl": [
                ("“Give me three days,” Melos said. “My sister is getting married.",
                 "“Give me three days,” Melos replied, holding the ruler’s gaze. “My sister is getting married."),
                ("“I nearly abandoned you,” he whispered.", "“I nearly abandoned you,” he whispered, his voice breaking."),
            ]},
}
NAMES = {"Melos"}
N_PN, N_OTHER = 4, 3          # 試作しきい値(最小語数)。最終値はUSER_DECISION候補


def plan(paras, speakers, bounds):
    return st.plan_clips(paras, speakers, bounds[0], bounds[1], "x", "narr")


def lint(clips, n_pn=N_PN, n_other=N_OTHER):
    out = []
    for t in L.tag_info(clips):
        if not t["adjacent_to_quote"]:
            continue
        has_pn = any(re.search(rf"\b{n}\b", t["text"]) for n in NAMES)
        n_req = n_pn if has_pn else n_other
        if t["wc"] < n_req:
            out.append({"id": t["id"], "text": t["text"], "wc": t["wc"], "n_required": n_req, "has_proper_noun": has_pn})
    return out


def sentences(paras):
    s = [x for p in paras for x in re.split(r"(?<=[.!?])[”’\"']?\s+", p) if x.strip()]
    return s


def nat_stats(paras):
    s = sentences(paras)
    wc = [len(L.words(x)) for x in s]
    verbs = re.findall(r"\b(said|replied|answered|whispered|asked|called|shouted|cried)\b", " ".join(paras), re.I)
    return {"words": sum(wc), "sentences": len(s), "avg_sentence_len": round(sum(wc) / max(1, len(wc)), 2),
            "speech_verbs": {v.lower(): verbs.count(v) for v in set(x.lower() for x in verbs)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    res, md = {}, ["# P1-3 机上適用 before/after (JPY0, API呼出なし)\n",
                   f"lintしきい値(試作): 固有名詞を含む引用隣接narrator chunk>={N_PN}語 / それ以外>={N_OTHER}語(最終値はUSER_DECISION候補)\n"]
    for lv, c in CFG.items():
        before_text = open(c["text"], encoding="utf8").read()
        plan_json = json.load(open(c["plan"], encoding="utf8"))
        bounds = plan_json["boundaries"]
        spk = json.load(open(c["attr"], encoding="utf8"))["final"]
        title, body = st.split_title_body(before_text)
        pb = st.clean_body_paragraphs(body)
        cb = plan(pb, spk, bounds)
        reg_ok = [x["text"] for x in cb] == [x["text"] for x in plan_json["clips"]]
        after_body = body
        for old, new in c["repl"]:
            assert after_body.count(old) == 1, ("replacement target not unique", old)
            after_body = after_body.replace(old, new)
        pa = st.clean_body_paragraphs(after_body)
        assert len(pa) == len(pb)
        spk_after = {k: v for k, v in spk.items()}
        ca = plan(pa, spk_after, bounds)
        names_set = NAMES
        def bnds(clips):
            return [dict(b, clip=x["id"], clip_wc=x["word_count"]) for x in clips for b in L.sib_boundaries(x["text"], names_set)]
        r = {"regression_reproduces_stored_plan": reg_ok,
             "before": {"n_clips": len(cb), "lint_findings": lint(cb), "pn_sib_boundaries": [b for b in bnds(cb) if b["proper_noun"]],
                        "nat": nat_stats(pb)},
             "after": {"n_clips": len(ca), "lint_findings": lint(ca), "pn_sib_boundaries": [b for b in bnds(ca) if b["proper_noun"]],
                       "nat": nat_stats(pa)},
             "replacements": c["repl"],
             "after_clips_changed": [{"id": x["id"], "voice": x["voice"], "wc": x["word_count"], "text": x["text"]}
                                     for x in ca if x["text"] not in [y["text"] for y in cb]]}
        res[lv] = r
        md.append(f"## {lv}\n- 保存済みclip計画の再現: {reg_ok}\n- clip数 before={len(cb)} after={len(ca)}")
        md.append(f"- lint指摘 before={json.dumps(r['before']['lint_findings'], ensure_ascii=False)}")
        md.append(f"- lint指摘 after ={json.dumps(r['after']['lint_findings'], ensure_ascii=False)}")
        md.append(f"- 固有名詞歯擦音境界 before={[(b['clip'], b['w1'], b['w2'], b['clip_wc']) for b in r['before']['pn_sib_boundaries']]} after={[(b['clip'], b['w1'], b['w2'], b['clip_wc']) for b in r['after']['pn_sib_boundaries']]}")
        md.append(f"- 自然さ(決定論): before={r['before']['nat']} / after={r['after']['nat']}")
        for old, new in c["repl"]:
            md.append(f"- BEFORE本文: {old}\n- AFTER 本文: {new}")
        md.append("- AFTERで変化したclip:")
        for x in r["after_clips_changed"]:
            md.append(f"  - {x['id']} [{x['voice']}] ({x['wc']}語): {x['text']}")
        md.append("")
    os.makedirs(a.out_dir, exist_ok=True)
    json.dump(res, open(f"{a.out_dir}/desk_apply_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    open(f"{a.out_dir}/desk_apply_01.md", "w", encoding="utf8").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
