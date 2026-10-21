"""FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01 委任_01 golden再判定(API 0, offline)。
保存済み転写(primary/secondary)を旧判定関数(git HEAD版)と新判定関数で再判定し、変化を全列挙する。
使い方: .venv/Scripts/python.exe docs/research/FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01/golden_rejudge.py <old_val.py> <out.json>"""
import importlib.util, json, sys, os
sys.path.insert(0, os.getcwd())
import er006_preprod_hardening_01_validation as newv
import er006_secondary_asr_01 as s2
import er021_en_asr_semantic_equivalence_production_01 as se
se.append_telemetry_log = lambda *a, **k: None  # telemetry副作用を出さない
spec = importlib.util.spec_from_file_location("old_val", sys.argv[1])
oldv = importlib.util.module_from_spec(spec); sys.modules["old_val"] = oldv; spec.loader.exec_module(oldv)

RUNS = {
 "run_mey_02": "er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_02",
 "run_fxpw_01": "er019_output/family_x_audio_production_wiring_01/coffee_prices__run_fxpw_01",
 "run_pp_01": "er019_output/family_x_audio_production_wiring_01/paycheck_personality__run_pp_01",
 "run_e2e_06(Z)": "er026_output/family_z_production_e2e_01/melos/run_e2e_06",
 "run_byus_01(参考)": "er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01",
}
def eff(mod, cls):
    """effective pass: should_pass、またはcascadeのCMU alternate層(HOMOPHONE_EQUIVALENT/PROPER_NOUN_ENTITY_ARPABET_CONFIRMED)。M1はLedger依存のため非模擬。"""
    if cls.should_pass: return True, cls.classification
    lab = s2._step_alternate_pass(cls)
    return (lab is not None), (lab or cls.classification)

def cases():
    for rname, root in RUNS.items():
        for dirpath, _, files in os.walk(root):
            if "tts_generation_results.json" not in files: continue
            f = os.path.join(dirpath, "tts_generation_results.json")
            d = json.load(open(f, encoding="utf8"))
            for sid, seg in (d.get("segments") or {}).items():
                canon = seg.get("canonical_text") or seg.get("text")
                if not canon: continue
                for log_key in ("attempts_log", "standard_attempts_log", "attempts"):
                    for i, a in enumerate(seg.get(log_key) or []):
                        if not isinstance(a, dict): continue
                        j = a.get("asr_judgement") or {}
                        for which, txt in (("primary", a.get("asr_text")), ("secondary", (j.get("secondary") or {}).get("text"))):
                            if txt:
                                yield rname, os.path.relpath(f).replace("\\", "/"), sid, "%s#%d" % (log_key, i + 1), which, canon, txt
                # segment直下(Family Z等、attempt単位のsecondaryが無い形式): 最終採用のprimary/secondary転写
                j = seg.get("asr_judgement") or {}
                for which, txt in (("seg_asr_text", seg.get("asr_text")), ("seg_primary", (j.get("primary") or {}).get("text")), ("seg_secondary", (j.get("secondary") or {}).get("text"))):
                    if txt:
                        yield rname, os.path.relpath(f).replace("\\", "/"), sid, "seg", which, canon, txt

rows, changed = [], []
seen = set()
for rname, f, sid, att, which, canon, txt in cases():
    key = (f, sid, canon, txt)  # 同一(canonical, 転写)の重複を除く
    if key in seen: continue
    seen.add(key)
    o = oldv.classify_asr_match(canon, txt, segment_id=sid)
    n = newv.classify_asr_match(canon, txt, segment_id=sid)
    oe = eff(oldv, o); ne = eff(newv, n)
    row = dict(run=rname, file=f, segment=sid, attempt=att, which=which,
               old_cls=o.classification, old_pass=o.should_pass, old_eff=oe[0], old_label=oe[1],
               new_cls=n.classification, new_pass=n.should_pass, new_eff=ne[0], new_label=ne[1],
               old_diffs=o.protected.content_word_diffs, new_diffs=n.protected.content_word_diffs,
               old_numbers=o.protected.number_mismatches, new_numbers=n.protected.number_mismatches)
    rows.append(row)
    if (o.classification, o.should_pass, oe, o.protected.content_word_diffs) != (n.classification, n.should_pass, ne, n.protected.content_word_diffs):
        changed.append(row)
summary = dict(total=len(rows), changed=len(changed),
               ng_to_pass=sum(1 for r in changed if not r["old_eff"] and r["new_eff"]),
               pass_to_ng=sum(1 for r in changed if r["old_eff"] and not r["new_eff"]),
               label_changed_same_eff=sum(1 for r in changed if r["old_eff"] == r["new_eff"]))
json.dump(dict(summary=summary, changed=changed), open(sys.argv[2], "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(json.dumps(summary))
for r in changed:
    print(r["run"], r["segment"], r["attempt"], r["which"], r["old_cls"], "->", r["new_cls"], "| eff", r["old_eff"], "->", r["new_eff"], r["new_label"])
