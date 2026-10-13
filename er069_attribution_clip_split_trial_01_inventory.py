# -*- coding: utf-8 -*-
"""Phase 1 P1-1 現状棚卸し(JPY0、読取のみ)。python er069_..._inventory.py --out-dir <dir>"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er069_attribution_clip_split_trial_01_lib as L
import er013_family_c_production_01 as fam_c

MELOS = "er026_output/family_z_production_e2e_01/melos/run_e2e_02"
OTHERS = {"melos_run01_article": "er026_output/family_z_production_e2e_01/melos/run_01/article.md",
          "er055_L13_datta": "er055_output/family_z_d_predictive_validation_trial_01/L13/story_en.md",
          "er055_L11_lemon": "er055_output/family_z_d_predictive_validation_trial_01/L11/story_en.md"}


def clips_from_text(path):
    """Production plan_story_segments を同じ引数で使う近似(話者名は不明のため引用ごとに交互voice q0/q1)。"""
    txt = open(path, encoding="utf8").read()
    paras = [p.strip() for p in txt.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    flat, qn = [], 0
    for pi, para in enumerate(paras):
        pos = 0
        for m in fam_c.DEFAULT_QUOTE_RE.finditer(para):
            if m.start() > pos and para[pos:m.start()].strip():
                flat.append((pi, "narrator", para[pos:m.start()]))
            qn += 1
            flat.append((pi, f"q{qn % 2}", m.group(0)))
            pos = m.end()
        if pos < len(para) and para[pos:].strip():
            flat.append((pi, "narrator", para[pos:]))
    segs = fam_c.plan_story_segments(flat)
    return [{"id": s["id"], "voice": s["voice"], "text": s["tts_text"], "word_count": s["word_count"]} for s in segs], txt


def analyze(name, clips, fulltext):
    names = L.find_names(fulltext)
    if "Melos" in fulltext:
        names.add("Melos")
    nar = [c for c in clips if c["voice"] == "narrator"]
    dist = {}
    for c in nar:
        dist[L.bucket(c["word_count"])] = dist.get(L.bucket(c["word_count"]), 0) + 1
    tags = L.tag_info(clips)
    short_adj = [t for t in tags if t["adjacent_to_quote"] and t["wc"] <= 5]
    bounds = []
    for c in clips:
        for b in L.sib_boundaries(c["text"], names):
            b.update({"clip": c["id"], "clip_voice": c["voice"], "clip_wc": c["word_count"]})
            bounds.append(b)
    return {"name": name, "n_clips": len(clips), "n_narrator_clips": len(nar), "names_detected": sorted(names),
            "narrator_wc_distribution": dist,
            "short_tag_like_clips": short_adj,
            "sibilant_boundaries": bounds,
            "sib_boundaries_proper": sum(1 for b in bounds if b["proper_noun"]),
            "sib_boundaries_common": sum(1 for b in bounds if not b["proper_noun"]),
            "sib_boundaries_in_short_clip_le3": [b for b in bounds if b["clip_wc"] <= 3],
            "clips": [{"id": c["id"], "voice": c["voice"], "wc": c["word_count"], "text": c["text"][:140]} for c in clips]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    res = {}
    for lv in ("a2", "b1b"):
        d = json.load(open(f"{MELOS}/segment_plan_{lv}.json", encoding="utf8"))
        full = " ".join(c["text"] for c in d["clips"])
        res[f"melos_e2e02_{lv}"] = analyze(f"melos_e2e02_{lv}", d["clips"], full)
    for k, p in OTHERS.items():
        clips, txt = clips_from_text(p)
        res[k] = analyze(k, clips, txt)
        res[k]["note"] = "近似: 引用話者は交互voice(q0/q1)。実Production planではない"
    json.dump(res, open(f"{a.out_dir}/inventory_01.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    md = ["# P1-1 inventory (JPY0, read-only)\n"]
    for k, v in res.items():
        md.append(f"## {k}\n- clips={v['n_clips']} narrator={v['n_narrator_clips']} narrator語数分布={v['narrator_wc_distribution']}")
        md.append(f"- 歯擦音境界(clip内の語境界、綴り近似): 固有名詞={v['sib_boundaries_proper']} / 一般語={v['sib_boundaries_common']} / うち3語以下clip内={len(v['sib_boundaries_in_short_clip_le3'])}")
        for b in v["sibilant_boundaries"]:
            md.append(f"  - [{'PN' if b['proper_noun'] else 'common'}] {b['clip']} ({b['clip_wc']}語): {b['w1']} + {b['w2']}")
        md.append("- 引用に隣接する5語以下narrator clip:")
        for t in v["short_tag_like_clips"]:
            md.append(f"  - {t['id']} ({t['wc']}語, {'between-quotes' if t['between_quotes'] else 'edge'}, verb={t['has_speech_verb']}): {t['text']}")
        md.append("")
    open(f"{a.out_dir}/inventory_01.md", "w", encoding="utf8").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
