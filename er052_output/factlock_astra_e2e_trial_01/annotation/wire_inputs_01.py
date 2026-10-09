# -*- coding: utf-8 -*-
"""委任_10: annotation/final/<slug>/ を runner入力 inputs/<slug>/ へ配置(コピーのみ、手直しなし)。
runnerの入力規約(委任_05 result.md 4節): selected_brief_annotated.md / fact_selection_evidence_annotated.json / annotation.json。
元B3・台帳・原JSONは置かない(runnerが stage_r を参照し、FROZEN_INPUTS_SHA256.json と照合する)。"""
import hashlib, json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
out = {}
for S in sys.argv[1:]:
    F = os.path.join(HERE, "final", S); D = os.path.join(BASE, "inputs", S); os.makedirs(D, exist_ok=True)
    m = {"selected_brief_factlock.md": "selected_brief_annotated.md", "fact_selection_evidence_factlock.json": "fact_selection_evidence_annotated.json",
         "annotation.json": "annotation.json"}
    for a, b in m.items():
        shutil.copyfile(os.path.join(F, a), os.path.join(D, b))
    if S in ("hormuz", "streaming_price"):   # B3 v2採用テーマ: 原B3/原JSONは storyline_b3_v2 を inputs へ置き、凍結shaをinput_manifest.jsonで照合させる
        V = os.path.join(BASE, "stage_r", S, "storyline_b3_v2")
        shutil.copyfile(os.path.join(V, "selected_brief.md"), os.path.join(D, "selected_brief.md"))
        shutil.copyfile(os.path.join(V, "fact_selection_evidence.json"), os.path.join(D, "fact_selection_evidence.json"))
        pins = json.load(open(os.path.join(BASE, "stage_r", "FROZEN_INPUTS_SHA256.json"), encoding="utf-8"))["themes"][S]
        man = {"ledger_sha256_lf": pins["ledger"]["sha256_lf"], "brief_sha256_lf": pins["storyline_b3_v2"]["selected_brief.md"]["sha256_lf"],
               "json_sha256_lf": pins["storyline_b3_v2"]["fact_selection_evidence.json"]["sha256_lf"]}
        json.dump(man, open(os.path.join(D, "input_manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        m = dict(m, **{"selected_brief.md": "selected_brief.md", "fact_selection_evidence.json": "fact_selection_evidence.json", "input_manifest.json": "input_manifest.json"})
    out[S] = {b: sha(os.path.join(D, b)) for b in m.values()}
p = os.path.join(BASE, "inputs", "WIRING_SHA256.json")
cur = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
cur.update(out); json.dump(cur, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(sorted(cur))
