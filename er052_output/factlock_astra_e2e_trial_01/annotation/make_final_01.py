# -*- coding: utf-8 -*-
"""委任_09: 統合版mdから annotation/final/<slug>/ を作る(機械的・手直しなし)。
JSON側 selected_fact_brief_text は、元evidence本文を空行で区切った各断片を元brief(prep座標)内で順に位置特定し、
b3_annotation_check_01.align_md が返す注記イベント(印・定義済み挿入)を同じ位置へ再適用して作る(md側と同一規則)。"""
import json, os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
sys.path.insert(0, BASE)
import b3_annotation_check_01 as c
rd = lambda p: open(p, encoding="utf-8", newline="").read()
B3DIR = lambda S: "storyline_b3_v2" if S in ("hormuz", "streaming_price") else "storyline_b3"   # 委任_10: B3 v2採用テーマ
res = {}
for S in sys.argv[1:]:
    M = os.path.join(HERE, "out", "merged", S); F = os.path.join(HERE, "final", S); os.makedirs(F, exist_ok=True)
    mdp = os.path.join(M, "merged_selected_brief_factlock.md")
    shutil.copyfile(mdp, os.path.join(F, "selected_brief_factlock.md"))
    shutil.copyfile(os.path.join(M, "merged_annotation.json"), os.path.join(F, "annotation.json"))
    brief = rd(os.path.join(BASE, "stage_r", S, B3DIR(S), "selected_brief.md"))
    al = c.align_md(brief, rd(mdp)); assert al["ok"], al["reason"]
    P = al["brief_prepped"]
    ins = {}  # offset -> {"mark":[], "op":[], "tag":[]}
    for off, kind, t in al["events"]:
        ins.setdefault(off, {"mark": [], "op": [], "tag": []})["mark" if kind == "mark" else "tag"].append(t)
    for off, s in al["ops"]:
        ins.setdefault(off, {"mark": [], "op": [], "tag": []})["op"].append(s)
    evp = os.path.join(BASE, "stage_r", S, B3DIR(S), "fact_selection_evidence.json")
    ev = json.load(open(evp, encoding="utf-8"))
    _txt = c.prep(ev["selected_fact_brief_text"]); SEP = "\n\n"   # v1: blank-line sep; v2 form (storyline + newline-separated bullets) falls back to line sep (delegation 10)
    def _locate(segs_):
        q = 0
        for sg_ in segs_:
            f_ = P.find(sg_, q)
            if f_ < 0: return False
            q = f_ + len(sg_)
        return True
    if not _locate(_txt.split(SEP)): SEP = "\n"
    segs = _txt.split(SEP)
    pos, out_parts = 0, []
    for sg in segs:
        st = P.find(sg, pos); assert st >= 0, ("segment not found", sg[:30])
        en = st + len(sg); buf = []
        for o in range(st, en + 1):
            d = ins.get(o)
            if d:
                buf += d["mark"]
                if o < en: buf += d["op"] + d["tag"]
            if o < en: buf.append(P[o])
        out_parts.append("".join(buf)); pos = en
    out = dict(ev); out["selected_fact_brief_text"] = SEP.join(out_parts)
    json.dump(out, open(os.path.join(F, "fact_selection_evidence_factlock.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    r = c.check_json(out, ev, c.norm_nl(brief), None)
    # md側と同数の印か
    mdtags = re.findall(r"【(?:事実\d+|中核数値|周辺数値)】", rd(mdp)); jt = re.findall(r"【(?:事実\d+|中核数値|周辺数値)】", out["selected_fact_brief_text"])
    res[S] = {"status": r["status"], "aligned": r.get("aligned"), "reason": r.get("reason"), "other_keys_identical": r.get("other_keys_identical"),
              "inserted_ops": r.get("inserted_ops"), "n_fact_tags": len(r["fact_tags"]), "md_tag_count": len(mdtags), "json_tag_count": len(jt)}
    print(S, res[S])
_p = os.path.join(HERE, "final", "final_json_check.json")
_cur = json.load(open(_p, encoding="utf-8")) if os.path.exists(_p) else {}
_cur.update(res)
json.dump(_cur, open(_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
