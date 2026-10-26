# -*- coding: utf-8 -*-
"""CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01 委任_01: Family X/Z/Y x Std/Adv の「chunk分割+0.2秒ポーズ」実発火の集計(read-only、API 0)。

既存run artifact(parts.json / segment_plan_*.json / audit/chunk_plan_*.json / chunk_tts_decision.json / tts_generation_results.json /
chunk_tts_assembly_*.json / timeline.json / raw_usage_log.jsonl)を読むだけ。LLM/TTS clientはimportしない。
分割の再現(replay)は共通planner(er117_chunk_tts_production_01、numpy+標準libのみ)を読取専用で呼ぶ。
使い方: py docs\\research\\CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01\\tools\\chunk_audit_inventory_01.py --out <json> --md <md>
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
import er117_chunk_tts_production_01 as ct  # noqa: E402

X_BASE = "er019_output/family_x_audio_production_wiring_01/"
Z_BASE = "er026_output/family_z_production_e2e_01/"
Y_BASE = "er121_output/family_y_production_01/"

# (family, run_dir, label, wiring_state) wiring_state: post=chunk配線(2026-10-25 13:00頃)以後の生成 / pre=配線前(replayで『現行コードなら』を示す) / textonly=TTS未実行
X_RUNS = [
    ("X", X_BASE + "uk_train_speaker_playback__run_chunk_01", "uk_train chunk_01(配線evidence)", "post"),
    ("X", X_BASE + "part2_hr_evidence_01__run_r1", "part2_hr_evidence run_r1(coffee_prices)", "post"),
    ("X", X_BASE + "part2_hr_evidence_01__run_r2", "part2_hr_evidence run_r2(coffee_prices)", "post"),
    ("X", X_BASE + "moon_shrinking__run_ms_03", "moon_shrinking run_ms_03(配線前の最新正式)", "pre"),
    ("X", X_BASE + "manga_ai_chat_byus__run_byus_01", "manga_ai_chat run_byus_01(配線前)", "pre"),
    ("X", X_BASE + "ai_island_temple__run_ai_01", "ai_island_temple run_ai_01(2026-10-26、TTS未実行)", "textonly"),
]
Z_RUNS = [
    ("Z", Z_BASE + "the_tell_tale_heart/run_chunk_01", "tell_tale_heart run_chunk_01(配線evidence)", "post"),
    ("Z", Z_BASE + "melos/run_p2_evidence_r3", "melos run_p2_evidence_r3(2026-10-25夜)", "post"),
    ("Z", Z_BASE + "melos/run_p2_evidence_r4", "melos run_p2_evidence_r4(2026-10-25夜)", "post"),
    ("Z", Z_BASE + "the_monkeys_paw/run_sf_prod_01", "monkeys_paw run_sf_prod_01(配線前)", "pre"),
    ("Z", Z_BASE + "melos/run_e2e_06", "melos run_e2e_06(配線前)", "pre"),
    ("Z", Z_BASE + "the_gift_of_the_magi/run_sf_prod_01", "gift_of_the_magi run_sf_prod_01(配線前)", "pre"),
    ("Z", Z_BASE + "the_open_window/run_sf_prod_01", "open_window run_sf_prod_01(配線前)", "pre"),
    ("Z", Z_BASE + "after_twenty_years/run_sf_prod_01", "after_twenty_years run_sf_prod_01(配線前)", "pre"),
]
Y_RUNS = [
    ("Y", Y_BASE + "redelivery_fee/run_01", "宅配 redelivery_fee run_01(E-1)", "post"),
    ("Y", Y_BASE + "sns_age_limit/run_01", "SNS年齢制限 sns_age_limit run_01(E-3)", "post"),
]


def jl(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def nparas(text):
    return len(ct.split_x_paragraphs(text))


def attempts(seg):
    seg = seg or {}
    return len(seg.get("attempts_log") or seg.get("attempts") or [])


def raw_tts_calls_by_segment(run_dir):
    """run単位 raw_usage_log.jsonl の stage=tts かつ TTS model のcallをsegment別に数える(Xのみ。levelは区別されない)。"""
    p = os.path.join(run_dir, "raw_usage_log.jsonl")
    c = collections.Counter()
    if not os.path.exists(p):
        return c
    with open(p, encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("stage") == "tts" and "tts" in str(d.get("model_id", "")) and "transcribe" not in str(d.get("model_id", "")) and "stt" not in str(d.get("model_id", "")):
                c[d.get("segment")] += 1
    return c


def x_level(run, lv, state):
    d = os.path.join(run, lv)
    parts = jl(d + "/parts.json")
    if not parts:
        return {"level": lv, "note": "parts.json なし"}
    res = jl(d + "/audit/tts_generation_results.json") or {}
    segs = res.get("segments") or {}
    saved = jl(d + "/audit/chunk_plan_b1b.json") if lv == "b1b" else None
    asm = jl(d + "/audit/chunk_tts_assembly_b1b.json") if lv == "b1b" else None
    out = {"level": lv, "parts": {}, "tts_generated": bool(segs)}
    for n in (1, 2, 3):
        pid, txt = f"full_story_part{n}", parts[f"part{n}"]
        replay = ct.plan_x_part(txt, pid)
        rec = {"words": ct.wc(txt), "paragraphs": nparas(txt),
               "replay_current_code": {"chunked": replay["chunked"], "chunk_words": [c["words"] for c in replay["chunks"]], "reason": replay.get("reason")},
               "applies_at_this_level": lv == "b1b"}
        kids = [k for k in segs if k.startswith(pid + "_k")]
        rec["chunk_entries_in_results"] = kids
        rec["attempts_total_parent_or_chunks"] = (sum(attempts(segs[k]) for k in kids) if kids else attempts(segs.get(pid)))
        if saved:
            sp = (saved.get("plans") or {}).get(pid) or {}
            rec["saved_plan"] = {"chunked": sp.get("chunked"), "chunk_words": [c["words"] for c in sp.get("chunks", [])]}
        if asm:
            ap = (asm.get("parents") or {}).get(pid)
            if ap:
                rec["gap_offsets_in_episode_s"] = ap.get("gap_offsets_in_episode_s")
        out["parts"][pid] = rec
    return out


def x_collect(fam, run, label, state):
    rt = raw_tts_calls_by_segment(run)
    r = {"family": fam, "run": run, "label": label, "wiring_state": state, "exists": os.path.isdir(run),
         "levels": {lv: x_level(run, lv, state) for lv in ("a2", "b1b")}, "raw_usage_tts_calls_by_segment(a2+b1b合算)": dict(rt)}
    return r


def z_level(run, lv):
    d = os.path.join(run, lv)
    sp = jl(os.path.join(run, f"segment_plan_{lv}.json"))
    res = jl(d + "/audit/tts_generation_results.json") or {}
    segs = res.get("segments") or {}
    saved = jl(d + "/audit/chunk_plan_b1b.json") if lv == "b1b" else None
    out = {"level": lv, "tts_generated": bool(segs), "story_clips": []}
    if not sp:
        out["note"] = f"segment_plan_{lv}.json なし"
        return out
    for c in sp.get("clips", []):
        w = c.get("word_count") or ct.wc(c["text"])
        narr = (c.get("voice") == "narrator") or (c.get("speaker") == "narrator")
        e = {"clip_id": c["id"], "voice": c.get("voice"), "words": w, "paragraphs_in_clip": nparas(c["text"]) if "\n" in c["text"] else None,
             "eligible_under_current_rule": bool(lv == "b1b" and narr and w > ct.Z_SPLIT_THRESHOLD_WORDS),
             "std_would_exceed_100_if_extended": bool(lv == "a2" and narr and w > ct.Z_SPLIT_THRESHOLD_WORDS)}
        kids = [k for k in segs if k.startswith(c["id"] + "_k")]
        e["chunk_entries_in_results"] = kids
        e["attempts_total"] = (sum(attempts(segs[k]) for k in kids) if kids else attempts(segs.get(c["id"])))
        e["slowdown_applied"] = (segs.get(c["id"]) or {}).get("slowdown_applied")
        if saved:
            sv = (saved.get("plans") or {}).get(c["id"])
            if sv:
                e["saved_plan"] = {"chunked": sv.get("chunked"), "chunk_words": [x["words"] for x in sv.get("chunks", [])], "boundary_kinds": [x.get("boundary_kind") for x in sv.get("chunks", [])]}
        out["story_clips"].append(e)
    if lv == "b1b":
        tl = jl(d + "/audit/timeline.json") or {}
        out["timeline_chunk_tts"] = (tl.get("chunk_tts") or {}).get("parents")
    return out


def z_collect(fam, run, label, state):
    return {"family": fam, "run": run, "label": label, "wiring_state": state, "exists": os.path.isdir(run),
            "levels": {lv: z_level(run, lv) for lv in ("a2", "b1b")}}


def y_level(run, lv):
    d = os.path.join(run, lv)
    parts = jl(d + "/parts.json") or {}
    segs_txt = parts.get("segments") or {}
    dec = jl(d + "/audit/chunk_tts_decision.json")
    res = jl(d + "/audit/tts_generation_results.json") or {}
    segs = res.get("segments") or {}
    out = {"level": lv, "decision_applied": (dec or {}).get("chunk_tts_applied_at_this_level"), "not_applied_reason": (dec or {}).get("not_applied_reason"),
           "segments": {}}
    for sid, txt in segs_txt.items():
        replay = ct.plan_x_part(txt, sid)
        kids = [k for k in segs if k.startswith(sid + "_k")]
        out["segments"][sid] = {"words": ct.wc(txt), "paragraphs": nparas(txt), "replay_current_code_chunked": replay["chunked"],
                                "replay_reason": replay.get("reason"), "decision_record": ((dec or {}).get("segments") or {}).get(sid),
                                "chunk_entries_in_results": kids, "attempts_total": attempts(segs.get(sid))}
    return out


def y_collect(fam, run, label, state):
    return {"family": fam, "run": run, "label": label, "wiring_state": state, "exists": os.path.isdir(run),
            "levels": {lv: y_level(run, lv) for lv in ("a2", "b1b")}}


def md_tables(inv):
    L = ["# RUNTIME_EVIDENCE_01 用 機械集計(chunk_audit_inventory_01.py 出力。read-only、API 0)", "",
         "`replay_current_code`=現行 `er117_chunk_tts_production_01` plannerを当該本文へ適用した結果。`saved_plan`=当該runが生成時に保存した`audit/chunk_plan_b1b.json`。", ""]
    L += ["## X(本文3 part。Std=a2は仕様上対象外)", "", "| run | 状態 | level | part | 語数 | 段落数 | 現行plannerの分割 | 保存plan | chunk entry | attempts合計 | 追加0.2秒(episode内s) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in inv["X"]:
        for lv, ld in r["levels"].items():
            for pid, p in (ld.get("parts") or {}).items():
                rp = p["replay_current_code"]
                sv = p.get("saved_plan")
                L.append(f"| {r['label']} | {r['wiring_state']} | {lv} | {pid[-5:]} | {p['words']} | {p['paragraphs']} | "
                         f"{'分割' + str(rp['chunk_words']) if rp['chunked'] else '不分割(' + str(rp['reason']) + ')'}{'(但しこのlevelは仕様上対象外)' if lv == 'a2' else ''} | "
                         f"{('chunked ' + str(sv['chunk_words'])) if sv and sv['chunked'] else ('-' if not sv else 'unchunked')} | {len(p['chunk_entries_in_results'])} | {p['attempts_total_parent_or_chunks']} | {p.get('gap_offsets_in_episode_s') or '-'} |")
    L += ["", "## Z(story clip。Adv narrator >100語のみ対象、Std=a2は仕様上対象外)", "", "| run | 状態 | level | clip | voice | 語数 | 現行規則で対象か | (Stdのみ)100語超narrator | 保存plan | chunk entry | attempts |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in inv["Z"]:
        for lv, ld in r["levels"].items():
            sc = ld.get("story_clips", [])
            L.append(f"| {r['label']} | {r['wiring_state']} | {lv} | (全{len(sc)} clip、narrator>100語={sum(1 for x in sc if x['eligible_under_current_rule'] or x['std_would_exceed_100_if_extended'])}、保存planでchunked={sum(1 for x in sc if (x.get('saved_plan') or {}).get('chunked'))}。以下は100語超narratorまたはchunked clipのみ) | | | | | | | |")
            for e in sc:
                if not (e["eligible_under_current_rule"] or e["std_would_exceed_100_if_extended"] or (e.get("saved_plan") or {}).get("chunked")):
                    continue
                sv = e.get("saved_plan")
                L.append(f"| {r['label']} | {r['wiring_state']} | {lv} | {e['clip_id']} | {e['voice']} | {e['words']} | {e['eligible_under_current_rule']} | {e['std_would_exceed_100_if_extended']} | "
                         f"{('chunked ' + str(sv['chunk_words']) + ' ' + str(sv['boundary_kinds'])) if sv and sv['chunked'] else '-'} | {len(e['chunk_entries_in_results'])} | {e['attempts_total']}(slowdown={e.get('slowdown_applied')}) |")
    L += ["", "## Y(8 segment、各1段落契約。Std=a2は仕様上対象外)", "", "| run | level | segment | 語数 | 段落数 | 現行planner分割 | decision記録 | chunk entry | attempts |", "|---|---|---|---|---|---|---|---|---|"]
    for r in inv["Y"]:
        for lv, ld in r["levels"].items():
            for sid, s in ld["segments"].items():
                L.append(f"| {r['label']} | {lv} | {sid} | {s['words']} | {s['paragraphs']} | {s['replay_current_code_chunked']}({s['replay_reason']}) | {s['decision_record'] or ('level対象外: ' + str(ld['not_applied_reason']))} | {len(s['chunk_entries_in_results'])} | {s['attempts_total']} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", required=True)
    a = ap.parse_args()
    os.chdir(ROOT)
    inv = {"X": [x_collect(*t) for t in X_RUNS], "Z": [z_collect(*t) for t in Z_RUNS], "Y": [y_collect(*t) for t in Y_RUNS]}
    inv["planner_version"] = ct.CHUNK_PLANNER_VERSION
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(inv, f, ensure_ascii=False, indent=1)
    with open(a.md, "w", encoding="utf-8") as f:
        f.write(md_tables(inv))
    print("wrote", a.out, a.md)


if __name__ == "__main__":
    main()
