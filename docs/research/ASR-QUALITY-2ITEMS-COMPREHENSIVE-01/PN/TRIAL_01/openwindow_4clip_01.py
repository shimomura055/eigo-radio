# -*- coding: utf-8 -*-
"""『開いた窓』run_sf_prod_01 の停止4clip(a2/b1b x full_story_part1_c14 / full_story_part3_c2)の机上再判定。状態変更なし(stage実行0・音声変更0・HR Lock解除0)。
表: 当該runのStd+Adv TTS canonical和集合(audit/tts_generation_results.json)から gpt-6-luna(cache)で構築 + Z Seed key_roles を宣言。判定は保存ASR転写(HR queue行)で、API 0(NERはcache)。"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
rows = {i: r for i, r, c in load_hr_rows()}
R = "er026_output/family_z_production_e2e_01/the_open_window/run_sf_prod_01"
seed = json.load(open("er026_seeds/the_open_window/seed.json", encoding="utf-8"))
decl = ret.declared_from_z_seed(seed)
k, segs, how = group_key_and_segments(rows[118])
tb_llm = ret.build_entity_table(segs, llm=cached_llm(0), usage_log=USAGE_LOG, tag="openwindow")
tb_decl = ret.build_entity_table(segs, declared=decl, llm=None)          # 宣言のみ(Bertieは宣言外)
tb_both = ret.build_entity_table(segs, declared=decl, llm=cached_llm(0), usage_log=USAGE_LOG, tag="openwindow+decl")
print("table(LLM)", [(e.surface, e.grade, e.category) for e in tb_llm.entries])
print("table(declared only)", [(e.surface, e.grade) for e in tb_decl.entries])
out = {"table_llm": tb_llm.to_dict()["entries"], "table_declared_only": [e.to_dict() for e in tb_decl.entries], "clips": []}
led_cur = ledger_tokens(False)
for lv in ("a2", "b1b"):
    d = json.load(open("%s/%s/audit/tts_generation_results.json" % (R, lv), encoding="utf-8"))["segments"]
    for sid in ("full_story_part1_c14", "full_story_part3_c2"):
        seg = d[sid]
        clip = {"level": lv, "segment": sid, "status": seg.get("status"), "canonical": seg["canonical_text"][:120], "attempts": []}
        for a in seg.get("attempts", []):
            if not a.get("asr_text"):
                continue
            cp = val.classify_asr_match(seg["canonical_text"], a["asr_text"])
            # 机上推定: 保存されたPrimary転写に対し、Secondary=Primary(onoff_differentialと同じmock前提)で原本/RETを判定
            est = None
            if cp.classification == "ASR_VALIDATION_UNCERTAIN":
                kw2 = dict(canonical_text=seg["canonical_text"], primary_cls=cp, secondary_cls=val.classify_asr_match(seg["canonical_text"], a["asr_text"]),
                           primary_text=a["asr_text"], secondary_text=a["asr_text"], judge_state="NG_BOTH", judge_reason_code="secondary_not_accepted",
                           role="FULL_STORY", p3_entry="p3_primary_ng")
                o2 = run_orig(kw2, led_cur); t2 = run_trial(kw2, led_cur, tb_llm)
                est = {"orig": [o2.accept, o2.reason], "ret": [t2.accept, t2.reason]}
            clip["attempts"].append({"estimate_secondary_equals_primary": est, "attempt": a.get("attempt"), "audio_classification": a.get("audio_classification"), "primary_asr": a["asr_text"][:140],
                                     "primary_diffs": [(x["canonical"], x["asr"], x["entity_like"]) for x in cp.protected.content_word_diffs],
                                     "classification_now": cp.classification})
        # HR queue行(最終attemptのPrimary/Secondary)
        hr = [i for i, r in rows.items() if r["wav_path"].replace("\\", "/").endswith("%s/narration/%s.wav" % (lv, sid))]
        clip["hr_rows"] = hr
        evals = []
        for i in hr:
            kw = inputs_for(rows[i])
            if kw is None:
                continue
            o = run_orig(kw, led_cur)
            ev_ = {"row": i, "orig": [o.accept, o.reason], "primary": kw["primary_text"][:120], "secondary": (kw["secondary_text"] or "")[:120]}
            for nm, tb in (("llm_table", tb_llm), ("declared_only", tb_decl), ("llm+declared", tb_both)):
                t = run_trial(kw, led_cur, tb)
                ev_[nm] = [t.accept, t.reason, [(x.canonical, x.asr_primary, x.asr_secondary, x.evidence) for x in t.diffs]]
            evals.append(ev_)
        clip["evals"] = evals
        out["clips"].append(clip)
        print(lv, sid, seg.get("status"), "hr_rows", hr, [ (e["row"], e["orig"], e["llm_table"][:2], e["declared_only"][:2]) for e in evals])
json.dump(out, open(os.path.join(HERE, "openwindow_4clip_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
