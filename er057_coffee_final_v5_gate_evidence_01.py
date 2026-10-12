# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01 委任_03: M3 Assembly Gate オフライン実行(read-only、API呼出なし、¥0)。
v5 out_dir の audit/tts_generation_results.json に m3_assembly_gate を直接適用し、gate_evidence/ へ保存する。
元ファイルは変更しない。fallback_used=True 改変は deepcopy(メモリ上のコピー)で行い、改変コピーもgate_evidenceへ別名保存する。"""
import os, sys, json, copy
ROOT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ROOT)
import er019_family_x_style_profile_01 as sp
RUN = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "coffee_prices__run_v5_ms_01")
OUT = os.path.join(ROOT, "er057_output", "coffee_final_v5", "gate_evidence")
PROFILE = "coffee_final_v5"
LV = {"a2": "a2", "b1b": "b1b"}


def load(level):
    return json.load(open(os.path.join(RUN, level, "audit", "tts_generation_results.json"), encoding="utf-8"))


def main():
    os.makedirs(OUT, exist_ok=True)
    summary = {"profile": PROFILE, "note": "offline m3_assembly_gate; runner --stage assemble is NOT run (Trial assembler used)", "levels": {}}
    for level in ("a2", "b1b"):
        res = load(level)
        g = sp.m3_assembly_gate(PROFILE, level, res, approvals=None)
        json.dump(g, open(os.path.join(OUT, f"style_profile_gate_{level}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        # 改変コピー(fallback_used=True): 元ファイルは変更せずメモリ上のdeepcopyのみ
        bad = copy.deepcopy(res)
        n = 0
        if level == "a2":
            for k in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
                if isinstance(bad["segments"].get(k), dict):
                    bad["segments"][k]["fallback_used"] = True; n += 1
        else:
            for r in bad["key_phrases"].values():
                e = r.get("explanation")
                if isinstance(e, dict):
                    e["fallback_used"] = True; n += 1
        gb = sp.m3_assembly_gate(PROFILE, level, bad, approvals=None)
        json.dump(bad, open(os.path.join(OUT, f"tts_generation_results_{level}__MODIFIED_COPY_fallback_true.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(gb, open(os.path.join(OUT, f"style_profile_gate_{level}__modified_copy_fallback_true.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        # b1b: m3_assembly_gateはKP解説のfallback_usedを判定しない(判定対象は status!=OK / local_rewrite_recovery / M4 style sha)。
        # そのため status を改変した別コピーでもBLOCK動作を確認する。
        gs = None
        if level == "b1b":
            bad2 = copy.deepcopy(res)
            bad2["key_phrases"]["1"]["explanation"]["status"] = "FALLBACK_USED"
            gs = sp.m3_assembly_gate(PROFILE, level, bad2, approvals=None)
            json.dump(gs, open(os.path.join(OUT, "style_profile_gate_b1b__modified_copy_kp1_status_not_ok.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        def scoped(gate):  # FULL_STORY(v4流用でrunner生成なし)を除いた判定
            bl = [x for x in gate["blocked"] if not x["segment"].startswith("full_story_part")]
            return {"status": "BLOCK" if bl else "PASS", "blocked": bl}
        targets = [c for c in g["checked"] if not c.startswith("full_story_part")]
        summary["levels"][level] = {
            "real_status_all_targets": g["status"], "real_blocked_segments": {x["segment"]: x["violations"] for x in g["blocked"]},
            "real_scoped_excluding_full_story": scoped(g), "scoped_targets": targets,
            "modified_fallback_true_entries_changed": n, "modified_fallback_true_scoped": scoped(gb),
            "modified_kp1_status_not_ok_scoped": scoped(gs) if gs else None}
        print(level, "REAL all", g["status"], "| scoped", scoped(g)["status"], targets, "| MOD fallback scoped", scoped(gb)["status"], "|", scoped(gs)["status"] if gs else "-")
    json.dump(summary, open(os.path.join(OUT, "gate_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
