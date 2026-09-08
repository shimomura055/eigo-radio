# ============================================================
# er011_open129_structural_completeness_production_wiring_evidence_01.py
# OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-PRODUCTION-WIRING-01
# ============================================================
# 目的: 本タスクで実装した「Production正式Gate
# (er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate)」の
# opt-in引数`required_structure`(既定None=OFF)が、実際に:
#   (1) 既存の完成episode全件(false reject 0)を、Gate自身が持つ他の
#       既存チェック(status/disfluency/slowdown/asset hash)も含めて
#       "そのまま"通すこと
#   (2) 4経路(A_FAMILY_A2/A_FAMILY_B1/B_FAMILY_B1/B_FAMILY_A2)×
#       5ケース(baseline/delete_segment/voice_swap/reorder/extra_segment)
#       で、delete/voice_swap/extra(12件)を正しく検知し、baseline/reorder
#       (8件)は検知しないこと
# を、Trial側の並行実装ではなく、実際に配線したProduction関数
# (asm.verify_episode_audio_validation_gate、registry.build_required_
# structure、asm.derive_a_family_required_structure)を直接呼び出して
# 実測する(read-only。既存Production実ファイルは一切変更しない。
# 一時コピーはos.path上の一時ディレクトリにのみ書く)。
#
# 実行方法:
#   .venv/Scripts/python.exe er011_open129_structural_completeness_production_wiring_evidence_01.py
# 出力: er011_output/open129_production_wiring_evidence_01/ 配下
# 費用: ¥0(TTS/LLM呼び出しなし)
from __future__ import annotations

import copy
import json
import os
import sys
import traceback

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_ROOT)

import er003_v1_n3_01_assemble as asm  # noqa: E402  Production、無変更
import er012_b_family_editorial_type_registry_01 as registry  # noqa: E402  Production、無変更

OUT_DIR = f"{REPO_ROOT}/er011_output/open129_production_wiring_evidence_01"
CASES_DIR = f"{OUT_DIR}/reproduction_cases"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# Part 1: 既存完成episode全件のfalse reject確認(実ディレクトリへ直接、
# read-only。Gate自体は副作用を持たない[ファイル読み取りのみ]ため、
# 実ディレクトリへ直接実行しても安全)。
# ============================================================
EXISTING_EPISODES = [
    # (path_id, out_dir, gate_level, voice_a, voice_b)
    ("A_FAMILY_A2", "er003_output/n3_01/hanshin/a2", "A2", None, None),
    ("A_FAMILY_A2", "er003_output/n3_01/health/a2", "A2", None, None),
    ("A_FAMILY_A2", "er003_output/n3_01/household/a2", "A2", None, None),
    ("A_FAMILY_A2", "er011_output/open112_trend_theme2_b_final_audio_rerun_04/a2", "A2", None, None),
    ("A_FAMILY_B1", "er003_output/n3_01/hanshin/b1b", "B1", None, None),
    ("A_FAMILY_B1", "er003_output/n3_01/health/b1b", "B1", None, None),
    ("A_FAMILY_B1", "er003_output/n3_01/household/b1b", "B1", None, None),
    ("A_FAMILY_B1", "er011_output/open112_trend_theme2_b_final_audio_rerun_04/b1b", "B1", None, None),
    ("B_FAMILY_B1", "er012_output/editorial_b_family_production_phase1_02/b1b", "B1", "Algieba", "Erinome"),
    ("B_FAMILY_A2", "er012_output/editorial_b_family_voices_a2_production_wiring_01/a2",
     "B_FAMILY_A2", "Algieba", "Erinome"),
    ("B_FAMILY_A2", "er012_output/editorial_b_voices_a2_free_address_02/a2", "B_FAMILY_A2", "Algieba", "Erinome"),
    ("B_FAMILY_A2", "er012_output/editorial_b_voices_a2_free_address_03/a2", "B_FAMILY_A2", "Algieba", "Erinome"),
    ("B_FAMILY_A2", "er012_output/editorial_b_voices_a2_free_address_04/a2", "B_FAMILY_A2", "Algieba", "Erinome"),
]


def required_structure_for(path_id: str, voice_a: str, voice_b: str) -> dict:
    if path_id == "A_FAMILY_A2":
        return asm.derive_a_family_required_structure("A2")
    if path_id == "A_FAMILY_B1":
        return asm.derive_a_family_required_structure("B1")
    if path_id == "B_FAMILY_B1":
        return registry.build_required_structure("b1", voice_a, voice_b)
    if path_id == "B_FAMILY_A2":
        return registry.build_required_structure("a2", voice_a, voice_b)
    raise ValueError(path_id)


def run_false_reject_sweep() -> dict:
    results = []
    for path_id, out_dir, gate_level, voice_a, voice_b in EXISTING_EPISODES:
        full_out_dir = f"{REPO_ROOT}/{out_dir}"
        entry = {"path_id": path_id, "out_dir": out_dir, "gate_level": gate_level}
        if not os.path.exists(f"{full_out_dir}/audit/tts_generation_results.json"):
            entry["status"] = "SKIPPED_FILE_NOT_FOUND"
            results.append(entry)
            continue
        rs = required_structure_for(path_id, voice_a, voice_b)
        # (a) OFF(既定): 既存呼び出しと同一(required_structure未指定)。
        try:
            asm.verify_episode_audio_validation_gate(full_out_dir, gate_level)
            entry["gate_off_result"] = "PASS"
        except RuntimeError as e:
            entry["gate_off_result"] = "BLOCKED"
            entry["gate_off_message"] = str(e)[:400]
        # (b) ON(opt-in、本タスクで追加した引数): 実Production Gateへ
        # required_structureを渡して実行。
        try:
            asm.verify_episode_audio_validation_gate(full_out_dir, gate_level, required_structure=rs)
            entry["gate_on_result"] = "PASS"
        except RuntimeError as e:
            entry["gate_on_result"] = "BLOCKED"
            entry["gate_on_message"] = str(e)[:600]
        # false_reject(OPEN-129機能起因)の定義: OFF(既存Gate)ではPASSして
        # いたのに、ON(構造完全性チェック追加後)でだけBLOCKEDになった場合
        # のみを数える。OFF時点で既にBLOCKEDな episode(disfluency/slowdown/
        # asset hash等、OPEN-129とは無関係な既知の別metadata gap、
        # OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-TRIAL-01 Part 2に
        # 記載済み)は、本機能の起因ではないため対象外とする。
        entry["false_reject"] = (entry["gate_off_result"] == "PASS" and entry["gate_on_result"] == "BLOCKED")
        entry["status"] = "OK"
        results.append(entry)
    false_rejects = [r for r in results if r.get("false_reject")]
    return {"episodes": results, "total": len(results),
            "false_reject_count": len(false_rejects),
            "false_reject_path_ids": [r["path_id"] + ":" + r["out_dir"] for r in false_rejects]}


# ============================================================
# Part 2: 4経路×5ケースの検知reproduction(実Gate関数を、一時コピーへ実行)
# ============================================================
REPRODUCTION_SOURCE = {
    "A_FAMILY_A2": ("er003_output/n3_01/hanshin/a2", "A2"),
    "A_FAMILY_B1": ("er003_output/n3_01/hanshin/b1b", "B1"),
    "B_FAMILY_B1": ("er012_output/editorial_b_family_production_phase1_02/b1b", "B1"),
    "B_FAMILY_A2": ("er012_output/editorial_b_family_voices_a2_production_wiring_01/a2", "B_FAMILY_A2"),
}
REPRODUCTION_VOICE_AB = {
    "A_FAMILY_A2": (None, None), "A_FAMILY_B1": (None, None),
    "B_FAMILY_B1": ("Algieba", "Erinome"), "B_FAMILY_A2": ("Algieba", "Erinome"),
}
DELETE_TARGET = {
    "A_FAMILY_A2": "full_story_part2", "A_FAMILY_B1": "full_story_part2",
    "B_FAMILY_B1": "full_story_part2", "B_FAMILY_A2": "full_story_part2",
}
VOICE_SWAP_PAIR = {
    "A_FAMILY_A2": ("point_one", "Algieba", "single-narrator-comment"),
    "A_FAMILY_B1": ("topic_intro", "point_one_heading", "swap"),
    "B_FAMILY_B1": ("point_one", "point_two", "swap"),
    "B_FAMILY_A2": ("point_one", "point_two", "swap"),
}
CASES = ("baseline", "delete_segment", "voice_swap", "reorder", "extra_segment")
EXPECTED_DETECTION = {
    "baseline": False, "delete_segment": True, "voice_swap": True,
    "reorder": False, "extra_segment": True,
}


def normalize_for_gate(data: dict) -> dict:
    """構造完全性以外の既存チェック(status/disfluency/slowdown)を無条件で
    通す状態へ正規化する(実ファイルは変更しない、一時コピー専用)。これに
    より、5ケースの結果差が構造完全性チェックのみに起因することを保証する
    (Trial-01と同じ手法)。"""
    data = copy.deepcopy(data)
    for entry in (data.get("segments") or {}).values():
        entry["status"] = "OK"
        entry["disfluency_checked"] = True
        entry["slowdown_applied"] = True
    for kp in (data.get("key_phrases") or {}).values():
        for sub_entry in kp.values():
            sub_entry["status"] = "OK"
            sub_entry["disfluency_checked"] = True
    return data


def make_case_data(base: dict, path_id: str, case: str) -> dict:
    data = copy.deepcopy(base)
    segs = data.setdefault("segments", {})
    if case == "baseline":
        pass
    elif case == "delete_segment":
        segs.pop(DELETE_TARGET[path_id], None)
    elif case == "voice_swap":
        info = VOICE_SWAP_PAIR[path_id]
        if info[2] == "swap":
            name_a, name_b, _ = info
            if name_a in segs and name_b in segs:
                va, vb = segs[name_a].get("voice"), segs[name_b].get("voice")
                segs[name_a]["voice"], segs[name_b]["voice"] = vb, va
        else:
            name_a, wrong_voice, _ = info
            if name_a in segs:
                segs[name_a]["voice"] = wrong_voice
    elif case == "reorder":
        items = list(segs.items())
        if len(items) >= 2:
            items[0], items[1] = items[1], items[0]
        data["segments"] = dict(items)
    elif case == "extra_segment":
        segs["unexpected_bonus_segment"] = {
            "status": "OK", "voice": "Aoede", "text": "injected by production wiring evidence script",
            "canonical_text": "injected by production wiring evidence script", "sha256": None, "path": None,
        }
    else:
        raise ValueError(case)
    return data


def run_reproduction() -> dict:
    results = {}
    for path_id, (src_out_dir, gate_level) in REPRODUCTION_SOURCE.items():
        results[path_id] = {}
        base = load_json(f"{REPO_ROOT}/{src_out_dir}/audit/tts_generation_results.json")
        normalized_base = normalize_for_gate(base)
        voice_a, voice_b = REPRODUCTION_VOICE_AB[path_id]
        rs = required_structure_for(path_id, voice_a, voice_b)
        for case in CASES:
            case_data_for_gate = make_case_data(normalized_base, path_id, case)
            temp_out_dir = f"{CASES_DIR}/{path_id}/_gate_tmp_{case}"
            save_json(f"{temp_out_dir}/audit/tts_generation_results.json", case_data_for_gate)

            try:
                asm.verify_episode_audio_validation_gate(temp_out_dir, gate_level, required_structure=rs)
                detected = False
                message = None
            except RuntimeError as e:
                detected = True
                message = str(e)[:600]

            results[path_id][case] = {
                "expected_detection": EXPECTED_DETECTION[case],
                "detected": detected,
                "message": message,
                "match_expected": detected == EXPECTED_DETECTION[case],
            }
    return results


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    sweep = run_false_reject_sweep()
    save_json(f"{OUT_DIR}/false_reject_sweep.json", sweep)
    print("=== false reject sweep (real Production Gate, required_structure ON) ===")
    print(f"total={sweep['total']} false_reject_count={sweep['false_reject_count']}")
    if sweep["false_reject_path_ids"]:
        print("false rejects:", sweep["false_reject_path_ids"])

    reproduction = run_reproduction()
    save_json(f"{OUT_DIR}/reproduction_results.json", reproduction)
    print("\n=== reproduction detection (real Production Gate) ===")
    total_cases = 0
    total_match = 0
    for path_id, cases in reproduction.items():
        for case, r in cases.items():
            total_cases += 1
            total_match += 1 if r["match_expected"] else 0
            print(f"{path_id:14s} {case:16s} expected={r['expected_detection']!s:5s} "
                  f"detected={r['detected']!s:5s} match={r['match_expected']}")
    print(f"\nmatch_expected: {total_match}/{total_cases}")

    detect_cases = [(p, c) for p, cs in reproduction.items() for c, r in cs.items()
                     if EXPECTED_DETECTION[c]]
    detect_hits = sum(1 for p, c in detect_cases if reproduction[p][c]["detected"])
    print(f"detection rate (delete/voice_swap/extra only): {detect_hits}/{len(detect_cases)}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
