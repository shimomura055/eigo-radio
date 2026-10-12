# -*- coding: utf-8 -*-
"""FAMILY-X-COFFEE-FINAL-V5-PRODUCTION-WIRING-01 委任_03: Audio Validation相当の記録(再計算のみ、API呼出なし、音声再生成なし)。
assembly_manifest_v5_01.json の provenance から全role(Std30/Adv29)のwav sha256を再計算し、manifest記録と照合、A2減速適用有無・既存QA参照を1表にする。"""
import os, json, hashlib
ROOT = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(ROOT, "er057_output", "coffee_final_v5")
V4 = os.path.join(ROOT, "er057_output", "coffee_final_v4")
RUN = os.path.join(ROOT, "er019_output", "family_x_audio_production_wiring_01", "coffee_prices__run_v5_ms_01")
J = lambda p: json.load(open(p, encoding="utf-8"))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    man = J(os.path.join(D, "assembly_manifest_v5_01.json"))["levels"]
    v4s = {r["id"]: r for r in J(os.path.join(V4, "gen_summary_v4.json"))["results"]}
    res = {"std": J(os.path.join(RUN, "a2", "audit", "tts_generation_results.json")), "adv": J(os.path.join(RUN, "b1b", "audit", "tts_generation_results.json"))}
    lines = ["# AUDIO_VALIDATION_V5_01 (Audio Validation Gate 相当の記録、再計算のみ)", "",
             "- 位置づけ: runner `--stage assemble` のAudio Validation Gateは**通していない**(Trial assembler `er057_coffee_final_v5_build_01.py` で組立)。本書はその代替としての事後記録(wav sha256再計算、減速有無、既存QA参照)。API呼出・音声再生成なし。",
             "- 生成: `er057_coffee_final_v5_audio_validation_01.py`(assembly_manifest_v5_01.json / gen_summary_v4.json / v5 tts_generation_results.json から)。",
             "- 全体QA(peak/clipping/headroom/長さ/内部無音/RMS/mp3整合)は `qa_v5_01.json`、known anomaly照合は `known_anomaly_compare_v5.json`、検出器は `anomaly_v5_std.json`/`anomaly_v5_adv.json`。",
             "- A2減速列: 「適用(6%)」=ファイル名`*_slow6`かつv4 gen_summaryにslowdown記録あり。「なし(JA経路)」=Production runnerのJA生成経路(generate_a2_japanese_with_reading_safety)は6%減速post-process対象外で、v5 results の trim_info/attempts_log にも減速記録なし。「記録なし(流用)」=Trial/既承認wavで減速記録なし(v4と同一sha)。Adv=A2減速の対象外。", ""]
    summary = {}
    for lv, title in (("std", "Standard"), ("adv", "Advanced")):
        pr = man[lv]["provenance"]
        lines += [f"## {title} ({len(pr)} role)", "", "| role | origin | style | wav sha256(再計算,先頭12) | manifest一致 | v4と同一 | A2減速 | 既存QA参照 |", "|---|---|---|---|---|---|---|---|"]
        v4p = J(os.path.join(V4, "assembly_manifest_v4_01.json"))["levels"][lv]["provenance"]
        ok = 0; missing = []
        for role, r in pr.items():
            path = r["path"]
            if not os.path.exists(path):
                missing.append(role); lines.append(f"| {role} | {r['origin']} | {r['style'][:40]} | **FILE MISSING** | - | - | - | - |"); continue
            s = sha(path); match = (s == r["sha256"]); ok += match
            same = (role in v4p and v4p[role]["sha256"] == s)
            # 減速
            if lv == "std" and role in ("full_story_part1", "full_story_part2", "full_story_part3"):
                e = v4s.get(f"std_part{role[-1]}", {}); sd = e.get("slowdown") or {}
                slow = f"適用(6%, 実測{sd.get('slowdown_pct_actual')}%)"
                qa = f"v4 gen_summary_v4.json std_part{role[-1]}: {e.get('status')}/{e.get('classification')}, slow_asr {((e.get('slow_asr') or {}).get('classification'))}"
            elif lv == "std" and role == "in_one_line":
                slow = "適用(6%, ファイル名std_in_one_line_slow6)"; qa = "v4継続(coffee_final_audio_assembly_01/segments、IOL 2文版)。v4 PLAY_EVIDENCE/qa_v4_01.json"
            elif lv == "adv" and role in ("full_story_part1", "full_story_part2", "full_story_part3"):
                e = v4s.get(f"adv_part{role[-1]}", {}); slow = "対象外(Adv)"
                qa = f"v4 gen_summary_v4.json adv_part{role[-1]}: {e.get('status')}/{e.get('classification')}"
            elif lv == "adv" and role == "in_one_line":
                slow = "対象外(Adv)"; qa = "v4継続(adv_in_one_line_raw、2文版)"
            elif r["origin"] == "R" and "v5" in r["style"] and lv == "std":
                e = res["std"]["segments"][role]; slow = "なし(JA経路)"
                qa = f"v5 results a2: status {e['status']}, asr_verified {e['asr_verified']}, {e['audio_classification']}, attempt {e['call_count']}"
            elif r["origin"] == "R" and "v5" in r["style"] and lv == "adv":
                n = role[2]; e = res["adv"]["key_phrases"][n]["explanation"]; slow = "対象外(Adv)"
                qa = f"v5 results b1b: status {e['status']}, asr_verified {e['asr_verified']}, {e['audio_classification']}, disfluency_checked {e['disfluency_checked']}, call_count {e['call_count']}"
            else:
                slow = "記録なし(流用)" if lv == "std" else "対象外(Adv)"
                qa = "v4/Trial流用(v4と同一sha)。Trial QA: coffee_final_listening_tone_trial_01 / v4 qa_v4_01.json"
            lines.append(f"| {role} | {r['origin']} | {r['style'][:40]} | {s[:12]} | {'OK' if match else '**MISMATCH**'} | {'同一' if same else '**v5新規**'} | {slow} | {qa} |")
        summary[lv] = {"roles": len(pr), "sha_match": ok, "missing": missing}
        lines += ["", f"- 小計: {len(pr)} role、sha再計算一致 {ok}/{len(pr)}、欠落 {missing or 'なし'}", ""]
    json.dump(summary, open(os.path.join(D, "audio_validation_v5_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(D, "AUDIO_VALIDATION_V5_01.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(summary)


if __name__ == "__main__":
    main()
