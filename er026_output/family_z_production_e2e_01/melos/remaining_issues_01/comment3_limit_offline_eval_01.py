# -*- coding: utf-8 -*-
"""REMAINING-ISSUES-01 項目2: limit_comment3_part の汎用性を API なしで評価する(課金0)。
Melos実Part3(Adv r2 / Std)と、Part3冒頭にネタバレを置いた合成素材3本を入力し、出力段落数と残った内容を表示する。"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
import er062_family_z_writer_01 as w

BASE = os.path.join(os.path.dirname(__file__), "..", "run_e2e_02", "writer")


def part3_of(path, start_prefix):
    t = open(path, encoding="utf-8").read()
    paras = [p for p in t.split("\n\n") if p.strip()]
    i = next(k for k, p in enumerate(paras) if p.startswith(start_prefix))
    return "\n\n".join(paras[i:])


cases = {
    "melos_adv_r2": part3_of(os.path.join(BASE, "r2.md"), "Then he remembered"),
    "melos_std": part3_of(os.path.join(BASE, "std.md"), "He remembered the hands"),
    "synth_mystery_reveal_no_marker": (
        "The detective opened the locked cellar. The old gardener lay dead behind the wine racks.\n\n"
        "The murderer, she realized, had been his own brother all along.\n\n"
        "She called the family into the hall.\n\nNobody spoke.\n\nThe brother lowered his head.\n\n"
        "The rain stopped by morning.\n\nThe case was closed.\n\nShe went home."),
    "synth_travel_marker_in_first_paragraph": (
        "The ship arrived at the island at dawn, and the crew finally saw the lost village.\n\n"
        "The villagers welcomed them with food.\n\nAn old woman told them about the storm.\n\n"
        "That night the captain wrote a letter.\n\nIn the morning they sailed home.\n\n"
        "Years later, the village was forgotten again.\n\nThe captain never returned.\n\nThe end of the voyage came quietly."),
    "synth_fantasy_false_positive_sword": (
        "Mira polished her sword before the morning lesson.\n\nHer teacher watched from the square.\n\n"
        "They practised until noon.\n\nThen a messenger came with a letter from the capital.\n\n"
        "Mira read it twice and smiled.\n\nShe packed her bag.\n\nThe road north was long.\n\n"
        "She walked for three days.\n\nShe met a stranger at a river."),
}
out = {}
for name, txt in cases.items():
    res = w.limit_comment3_part(txt)
    n_all = len([p for p in txt.split("\n\n") if p.strip()])
    kept = [p for p in res.split("\n\n") if p.strip()]
    marker_hits = [bool(w.COMMENT3_ENDING_MARKER_RE.search(p)) for p in kept]
    out[name] = {"paras_total": n_all, "paras_kept": len(kept), "kept_contains_marker_para": any(marker_hits), "kept": kept}
    print(f"== {name}: {len(kept)}/{n_all} paras, kept_has_marker_para={any(marker_hits)}")
    for p in kept:
        print("   -", p[:110])
json.dump(out, open(os.path.join(os.path.dirname(__file__), "comment3_limit_offline_eval_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
