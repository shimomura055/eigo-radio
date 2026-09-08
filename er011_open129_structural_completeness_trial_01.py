# ============================================================
# er011_open129_structural_completeness_trial_01.py
# OPEN-129-AUDIO-GATE-STRUCTURAL-COMPLETENESS-TRIAL-01(Lane B)
# ============================================================
# 目的: 現行Audio Validation Gate(er003_v1_n3_01_assemble.py::
# verify_episode_audio_validation_gate())は「tts_generation_results.json
# に記録済みのsegmentの状態」だけを検証し、「構造上あるべきsegment数・
# 種類・voice割当との一致」を検証しない(OPEN-129)。本ファイルはTrial専用
# (Production無変更・Gate/registry無編集・TTS/LLM呼び出し無し、¥0)。
#
# ここで実装する check_structural_completeness() はTrial側の新規関数
# であり、既存のverify_episode_audio_validation_gate()やer012_b_family_
# voices_a2_production_01.check_required_segments_completeness()を
# 置き換えるものではない(どちらも無変更、read-onlyでimportするのみ)。
#
# 実行方法:
#   .venv/Scripts/python.exe er011_open129_structural_completeness_trial_01.py
#
# 出力: er011_output/open129_structural_completeness_trial_01/ 配下へ
#   - gate_capability_matrix.json (現行Gateの検証/非検証表)
#   - reproduction_cases/<path_id>/<case>.json (一時コピー、5ケース分)
#   - reproduction_results.json (現行Gate vs Trial実装の検知結果)
#   - false_reject_sweep.json (既存完成episode全件でのfalse reject確認)

from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
import traceback

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO_ROOT)

import er003_v1_n3_01_assemble as asm  # noqa: E402  Production、read-onlyでimportのみ(無変更)

OUT_DIR = f"{REPO_ROOT}/er011_output/open129_structural_completeness_trial_01"
CASES_DIR = f"{OUT_DIR}/reproduction_cases"


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# Part 1: 4経路の「構造上あるべき」定義(Trial専用、Production registry
# 無編集。B_FAMILY_A2はer012_b_family_editorial_type_registry_01.py::
# B_FAMILY_A2_REQUIRED_SEGMENTSと同じsegment一覧+voice roleを踏襲し、
# key phrase側の網羅(既存registryが未対応)をTrialとして追加する)。
#
# 重要な発見(Gate 3相当の指摘): 現行verify_episode_audio_validation_gate()
# はB-Family B1・A-Family B1のどちらもlevel="B1"という同一文字列で呼ばれる
# (er012_b_family_production_runner_01.py::asm.load_b1_sources()がA-Family
# 用のload_b1_sources()をそのまま共有呼び出しするため)。しかし実際の構造は
# 異なる(B-FamilyはA-Family B1に無いtension_reflectionを持ち、point_one/
# point_twoがA-Familyの単一narratorではなくvoice_a/voice_bの2役)。つまり
# 「level文字列だけでは構造を一意に決定できない」という設計上の欠落自体が
# OPEN-129の一部であり、本Trialでは4経路をlevel文字列ではなくfamily込みの
# path_idで区別する(A_FAMILY_A2 / A_FAMILY_B1 / B_FAMILY_B1 / B_FAMILY_A2)。
# key_phrase_subkey_count: 実データを横断確認すると、rank毎のsub-key名称
# 自体が生成era/familyで揺れている(A_FAMILY_A2="english"/"japanese_meaning"、
# A_FAMILY_B1="english"/"japanese"、B_FAMILY_B1="en"/"ja_charon"、B_FAMILY_A2は
# 観測範囲内で"english"/"japanese"と"english"/"japanese_meaning"の両方が実在)。
# この命名揺れ自体は別の問題(schema drift、OPEN-129の主眼である「segment集合
# の完全性」とは別軸)であり、本Trialでは名称を固定せず「各rankに2件の
# sub-entryが存在するか」という件数ベースでのみ構造完全性を判定する
# (命名揺れによるfalse reject を避けるため。命名統一自体は本Trialの
# スコープ外、Part 5のUSER_DECISION_REQUIRED候補として報告する)。
REQUIRED_STRUCTURE_BY_PATH = {
    "A_FAMILY_A2": {
        "segments": (
            ("topic_intro", "Aoede"), ("japanese_title", "Aoede"), ("preview", "Aoede"),
            ("comment_1", "Aoede"), ("comment_2", "Aoede"), ("comment_3", "Aoede"), ("comment_4", "Aoede"),
            ("point_one_heading", "Aoede"), ("point_two_heading", "Aoede"),
            ("full_story_part1", "Aoede"), ("full_story_part2", "Aoede"),
            ("point_one", "Aoede"), ("point_two", "Aoede"),
            ("in_one_line", "Aoede"),
        ),
        "key_phrase_ranks": 5, "key_phrase_subkey_count": 2,
    },
    "A_FAMILY_B1": {
        # full_story_part1/2・point_one/two・in_one_lineは、既存Production
        # データ実測(n3_01 3テーマ・rerun_04で全て一致)でvoiceフィールド自体が
        # 常にNone(未記録)であるため、expected_voice=Noneとして「記録が無い
        # ことは既知の後方互換」として扱う(false reject防止、Part 3参照)。
        "segments": (
            ("topic_intro", "Charon"), ("preview", "Charon"),
            ("comment_1", "Charon"), ("comment_2", "Charon"), ("comment_3", "Charon"), ("comment_4", "Charon"),
            ("point_one_heading", "Aoede"), ("point_two_heading", "Aoede"),
            ("full_story_part1", None), ("full_story_part2", None),
            ("point_one", None), ("point_two", None),
            ("in_one_line", None),
        ),
        "key_phrase_ranks": 5, "key_phrase_subkey_count": 2,
    },
    "B_FAMILY_B1": {
        "segments": (
            ("topic_intro", "Charon"), ("preview", "Charon"),
            ("comment_1", "Charon"), ("comment_2", "Charon"), ("comment_3", "Charon"), ("comment_4", "Charon"),
            ("point_one_heading", "Aoede"), ("point_two_heading", "Aoede"),
            ("point_one", "voice_a"), ("point_two", "voice_b"),
            ("full_story_part1", None), ("full_story_part2", None),
            ("tension_reflection", None), ("in_one_line", None),
        ),
        "key_phrase_ranks": 5, "key_phrase_subkey_count": 2,
    },
    "B_FAMILY_A2": {
        # er012_b_family_editorial_type_registry_01.py::B_FAMILY_A2_REQUIRED_
        # SEGMENTS(15件)と同一のsegment一覧+role。key phrase側はTrial追加分。
        "segments": (
            ("topic_intro", "Charon"), ("japanese_title", "Aoede"), ("preview", "Aoede"),
            ("comment_1", "Aoede"), ("comment_2", "Aoede"), ("comment_3", "Aoede"), ("comment_4", "Aoede"),
            ("point_one_heading", "Aoede"), ("point_two_heading", "Aoede"),
            ("full_story_part1", "Aoede"), ("full_story_part2", "Aoede"),
            ("tension_reflection", "Aoede"), ("in_one_line", "Aoede"),
            ("point_one", "voice_a"), ("point_two", "voice_b"),
        ),
        "key_phrase_ranks": 5, "key_phrase_subkey_count": 2,
    },
}


def check_structural_completeness(tts_results: dict, path_id: str,
                                   voice_a: str = None, voice_b: str = None) -> dict:
    """Trial専用の構造完全性チェック。tts_generation_results.jsonの
    dict(既にmemory上にloadしたもの)を受け取り、副作用なしで結果を返す。
    Production Gateとは独立(呼ばない・置き換えない)。"""
    spec = REQUIRED_STRUCTURE_BY_PATH[path_id]
    segs = (tts_results.get("segments") or {})
    kp = (tts_results.get("key_phrases") or {})
    expected_names = [n for n, _ in spec["segments"]]

    missing = []
    voice_mismatches = []
    for name, expected_voice in spec["segments"]:
        entry = segs.get(name)
        if entry is None:
            missing.append(name)
            continue
        resolved_expected = expected_voice
        if resolved_expected == "voice_a":
            resolved_expected = voice_a
        elif resolved_expected == "voice_b":
            resolved_expected = voice_b
        actual_voice = entry.get("voice")
        # 既存データにvoiceフィールドが未記録(None)の既知後方互換ケースは
        # 検証しない(false reject防止)。expected側がNone(役割未定義)の
        # 場合も同様にskipする。
        if resolved_expected is not None and actual_voice is not None and actual_voice != resolved_expected:
            voice_mismatches.append(f"{name}: expected={resolved_expected} actual={actual_voice}")

    extra_segments = sorted(n for n in segs if n not in expected_names)

    kp_missing = []
    expected_ranks = {str(i) for i in range(1, spec["key_phrase_ranks"] + 1)}
    expected_subkey_count = spec["key_phrase_subkey_count"]
    for rank_str in sorted(expected_ranks, key=int):
        sub = kp.get(rank_str)
        if sub is None:
            kp_missing.append(f"kp{rank_str}(all)")
            continue
        if len(sub) < expected_subkey_count:
            kp_missing.append(f"kp{rank_str}(has {len(sub)}, expected {expected_subkey_count}: {sorted(sub)})")
    extra_kp_ranks = sorted(r for r in kp if r not in expected_ranks)

    complete = not (missing or voice_mismatches or kp_missing or extra_segments or extra_kp_ranks)
    return {
        "path_id": path_id,
        "expected_segment_count": len(expected_names),
        "actual_segment_count": len(segs),
        "missing_segments": missing,
        "voice_mismatches": voice_mismatches,
        "extra_segments": extra_segments,
        "expected_key_phrase_ranks": len(expected_ranks),
        "kp_missing": kp_missing,
        "extra_key_phrase_ranks": extra_kp_ranks,
        "complete": complete,
    }


# ============================================================
# Part 2: 既存の完成episode(false reject確認対象・reproduction元データ)
# ============================================================
EXISTING_EPISODES = [
    # (path_id, out_dir[audit/tts_generation_results.jsonの親], voice_a, voice_b)
    ("A_FAMILY_A2", "er003_output/n3_01/hanshin/a2", None, None),
    ("A_FAMILY_A2", "er003_output/n3_01/health/a2", None, None),
    ("A_FAMILY_A2", "er003_output/n3_01/household/a2", None, None),
    ("A_FAMILY_A2", "er011_output/open112_trend_theme2_b_final_audio_rerun_04/a2", None, None),
    ("A_FAMILY_B1", "er003_output/n3_01/hanshin/b1b", None, None),
    ("A_FAMILY_B1", "er003_output/n3_01/health/b1b", None, None),
    ("A_FAMILY_B1", "er003_output/n3_01/household/b1b", None, None),
    ("A_FAMILY_B1", "er011_output/open112_trend_theme2_b_final_audio_rerun_04/b1b", None, None),
    ("B_FAMILY_B1", "er012_output/editorial_b_family_production_phase1_02/b1b", "Algieba", "Erinome"),
    ("B_FAMILY_A2", "er012_output/editorial_b_family_voices_a2_production_wiring_01/a2", "Algieba", "Erinome"),
    ("B_FAMILY_A2", "er012_output/editorial_b_voices_a2_free_address_02/a2", "Algieba", "Erinome"),
    ("B_FAMILY_A2", "er012_output/editorial_b_voices_a2_free_address_03/a2", "Algieba", "Erinome"),
    ("B_FAMILY_A2", "er012_output/editorial_b_voices_a2_free_address_04/a2", "Algieba", "Erinome"),
]

# reproduction(5ケース×4経路)の元データとして使う代表episode(各経路1件)
REPRODUCTION_SOURCE = {
    "A_FAMILY_A2": "er003_output/n3_01/hanshin/a2",
    "A_FAMILY_B1": "er003_output/n3_01/hanshin/b1b",
    "B_FAMILY_B1": "er012_output/editorial_b_family_production_phase1_02/b1b",
    "B_FAMILY_A2": "er012_output/editorial_b_family_voices_a2_production_wiring_01/a2",
}
REPRODUCTION_VOICE_AB = {
    "A_FAMILY_A2": (None, None), "A_FAMILY_B1": (None, None),
    "B_FAMILY_B1": ("Algieba", "Erinome"), "B_FAMILY_A2": ("Algieba", "Erinome"),
}

# 各経路で削除/voice入れ替え対象に使う代表segment名(実データに存在確認済み)
DELETE_TARGET = {
    "A_FAMILY_A2": "full_story_part2", "A_FAMILY_B1": "full_story_part2",
    "B_FAMILY_B1": "full_story_part2", "B_FAMILY_A2": "full_story_part2",
}
VOICE_SWAP_PAIR = {
    # A-Family A2は全segmentがAoede単一narratorのため、意味のあるswap対象が
    # 無い(voiceの多様性が無い経路)。この場合は「swap」ではなく「誤ったvoice
    # 値への書き換え」で代替する(comment)。
    "A_FAMILY_A2": ("point_one", "Algieba", "single-narrator-comment"),
    "A_FAMILY_B1": ("topic_intro", "point_one_heading", "swap"),  # Charon <-> Aoede
    "B_FAMILY_B1": ("point_one", "point_two", "swap"),  # Algieba <-> Erinome
    "B_FAMILY_A2": ("point_one", "point_two", "swap"),  # Algieba <-> Erinome
}


def run_gate_readonly(out_dir_temp: str, level_for_gate: str) -> dict:
    """Production Gate(verify_episode_audio_validation_gate)を、一時コピー
    ディレクトリに対してread-onlyで実行する(Production側は無変更・無編集)。
    levelはGateの引数であり、B1系は"B1"、A2系は"A2"を渡す(Gate自体の呼び分け
    そのままを再現。B_FAMILY_A2のみ既存呼び出し規約通り"B_FAMILY_A2")。"""
    try:
        asm.verify_episode_audio_validation_gate(out_dir_temp, level_for_gate)
        return {"gate_result": "PASS", "detected": False, "message": None}
    except RuntimeError as e:
        return {"gate_result": "BLOCKED", "detected": True, "message": str(e)[:300]}
    except Exception as e:  # noqa: BLE001
        return {"gate_result": "ERROR", "detected": None, "message": f"{type(e).__name__}: {e}"}


GATE_LEVEL_FOR_PATH = {
    "A_FAMILY_A2": "A2", "A_FAMILY_B1": "B1", "B_FAMILY_B1": "B1", "B_FAMILY_A2": "B_FAMILY_A2",
}


def normalize_baseline_for_gate_reproduction(data: dict) -> dict:
    """current_gate(Production、read-only import)側のreproduction比較専用の
    正規化。既存archival dataには、本Trialの対象外である別の既知metadata
    ギャップ(例: disfluency_checked未記録の旧データ、STOPPED状態でHuman
    Review承認recordが別ファイルにあるためこのコピーには含まれないケース)が
    混在しており、これらはOPEN-129(構造完全性)とは独立した既知事象
    (ER-008-N8-FINAL-QA-HARDENING-21等、Part 3参照)である。これらの
    confoundを除去し、reproductionの5ケースが「構造上の変更」のみに起因して
    current_gateの挙動を変えるかを見るため、コピー上でのみstatus/
    disfluency_checked/slowdown_appliedを正規化する(実ファイル・Production
    側は一切変更しない)。"""
    data = copy.deepcopy(data)
    for name, entry in (data.get("segments") or {}).items():
        entry["status"] = "OK"
        entry["disfluency_checked"] = True
        entry["slowdown_applied"] = True
    for rank, kp in (data.get("key_phrases") or {}).items():
        for sub_key, sub_entry in kp.items():
            sub_entry["status"] = "OK"
            sub_entry["disfluency_checked"] = True
    return data


def make_case_data(base: dict, path_id: str, case: str) -> dict:
    data = copy.deepcopy(base)
    segs = data.setdefault("segments", {})
    if case == "baseline":
        pass
    elif case == "delete_segment":
        name = DELETE_TARGET[path_id]
        segs.pop(name, None)
    elif case == "voice_swap":
        info = VOICE_SWAP_PAIR[path_id]
        if info[2] == "swap":
            name_a, name_b, _ = info
            if name_a in segs and name_b in segs:
                va = segs[name_a].get("voice")
                vb = segs[name_b].get("voice")
                segs[name_a]["voice"] = vb
                segs[name_b]["voice"] = va
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
            "status": "OK", "voice": "Aoede", "text": "injected by trial",
            "canonical_text": "injected by trial", "sha256": None, "path": None,
        }
    else:
        raise ValueError(case)
    return data


CASES = ("baseline", "delete_segment", "voice_swap", "reorder", "extra_segment")
EXPECTED_DETECTION = {
    "baseline": False, "delete_segment": True, "voice_swap": True,
    "reorder": False,  # JSON dict内のkey順序は現行アーキテクチャで意味を持たない(仕様通りのnegative control)
    "extra_segment": True,
}


def run_reproduction() -> dict:
    results = {}
    for path_id, src_out_dir in REPRODUCTION_SOURCE.items():
        results[path_id] = {}
        base = load_json(f"{src_out_dir}/audit/tts_generation_results.json")
        normalized_base = normalize_baseline_for_gate_reproduction(base)
        voice_a, voice_b = REPRODUCTION_VOICE_AB[path_id]
        for case in CASES:
            case_data = make_case_data(base, path_id, case)  # 現実のraw値(trial_check・保存用artifact)
            case_data_for_gate = make_case_data(normalized_base, path_id, case)  # current_gate比較専用(正規化済み)

            case_path = f"{CASES_DIR}/{path_id}/{case}.json"
            save_json(case_path, case_data)

            temp_out_dir = f"{CASES_DIR}/{path_id}/_gate_tmp_{case}"
            save_json(f"{temp_out_dir}/audit/tts_generation_results.json", case_data_for_gate)

            gate = run_gate_readonly(temp_out_dir, GATE_LEVEL_FOR_PATH[path_id])
            trial = check_structural_completeness(case_data, path_id, voice_a, voice_b)
            results[path_id][case] = {
                "expected_detection": EXPECTED_DETECTION[case],
                "current_gate": gate,
                "trial_check": {"detected": not trial["complete"], "detail": trial},
            }
    return results


def run_false_reject_sweep() -> dict:
    results = []
    for path_id, out_dir, voice_a, voice_b in EXISTING_EPISODES:
        full_path = f"{REPO_ROOT}/{out_dir}/audit/tts_generation_results.json"
        entry = {"path_id": path_id, "out_dir": out_dir}
        if not os.path.exists(full_path):
            entry["status"] = "SKIPPED_FILE_NOT_FOUND"
            results.append(entry)
            continue
        try:
            data = load_json(full_path)
            check = check_structural_completeness(data, path_id, voice_a, voice_b)
            entry["status"] = "OK"
            entry["complete"] = check["complete"]
            entry["false_reject"] = not check["complete"]
            entry["detail"] = check
        except Exception as e:  # noqa: BLE001
            entry["status"] = "ERROR"
            entry["error"] = f"{type(e).__name__}: {e}\n{traceback.format_exc()[-800:]}"
        results.append(entry)
    false_rejects = [r for r in results if r.get("false_reject")]
    return {"episodes": results, "total": len(results),
            "false_reject_count": len(false_rejects),
            "false_reject_path_ids": [r["path_id"] + ":" + r["out_dir"] for r in false_rejects]}


# ============================================================
# Part 3: 現行Gateの検証/非検証表(手動分析結果、コードとして固定化)
# ============================================================
GATE_CAPABILITY_MATRIX = {
    "current_gate": "er003_v1_n3_01_assemble.py::verify_episode_audio_validation_gate()",
    "inputs_checked": [
        "tts_generation_results.json内に実在するsegments/key_phrasesの各entryのstatus"
        "(OK/ASR_VALIDATION_UNCERTAIN/HUMAN_REVIEW_LOCKED/STOPPED)",
        "human_approved_segments.json(canonical_text sha256突合によるHuman Review承認確認)",
        "narration_dir上の実ファイルsha256とtts_generation_results.json記録sha256の突合"
        "(ASSET_HASH_MISMATCH、ファイルが存在する場合のみ)",
        "A2の6% slowdown必須post-process証跡(slowdown_applied、無い場合は_original.wav比率)",
        "disfluency QA必須post-process証跡(disfluency_checked、level別mandatory segment)",
    ],
    "inputs_not_checked": [
        "tts_generation_results.jsonのsegments/key_phrases辞書に、そもそもentry自体が"
        "存在しない(=完全欠落)segmentの検知。存在するentryしか走査しないため、"
        "生成時にentryが書かれなかったsegment(例: 生成script が途中で例外終了し、"
        "そのsegmentの結果を書く前にdisk上の旧wavだけが残った場合)はGate通過対象外として"
        "スキップされ、assembly側は旧wav(未検証)をそのまま読み込む(ER-008-N7-CONTENT-"
        "AUDIO-QA-02と同型の既知failure mode)",
        "voice割当(entry['voice'])が構造上期待される役割(narrator/voice_a/voice_b等)と"
        "一致しているかの突合(voiceフィールド自体はrecordされているが、Gateは一切参照"
        "しない)",
        "余分な(構造上想定されていない)segment/key phraseの混入検知",
        "level文字列(\"B1\"等)がA-Family/B-Familyのどちらの構造を指すかの区別"
        "(現状同一文字列を共有しており、構造定義自体がGate側に存在しない)",
        "segment数の総量(期待15件・14件・13件等)がそもそも揃っているかの直接カウント",
    ],
    "known_failure_modes_grepped": [
        "ER-008-N7-CONTENT-AUDIO-QA-02: Key Phrase 1件のTTSがSTOPPEDでも、disk上の前回"
        "実行(別Key Phraseセット)の古い音声をそのまま使ってしまった(entry自体は存在した"
        "が、別の理由でGate通過前のバグ、Gate導入の直接動機)",
        "ER-008-N8-FINAL-QA-HARDENING-21: disfluency_checked証跡欠落(status==OKのみで"
        "判定していたための取りこぼし)",
        "OPEN-112-THEME2-AUDIO-REVIEW-FIX-02: Point Twoでslowdown_applied=Falseにも"
        "関わらず無関係な旧_original.wavの存在だけで通過した抜け穴",
        "OPEN-129(本Trialの起点、EDITORIAL-B-FAMILY-VOICES-A2-PRODUCTION-WIRING-01"
        "Gate 3 item 8): 上記いずれもentryの'状態'は検証するが、entry自体の'有無の"
        "全体集合一致'は検証しない、という共通する未対策領域",
    ],
}


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    save_json(f"{OUT_DIR}/gate_capability_matrix.json", GATE_CAPABILITY_MATRIX)

    reproduction = run_reproduction()
    save_json(f"{OUT_DIR}/reproduction_results.json", reproduction)

    sweep = run_false_reject_sweep()
    save_json(f"{OUT_DIR}/false_reject_sweep.json", sweep)

    print("=== reproduction detection summary (current_gate / trial_check) ===")
    for path_id, cases in reproduction.items():
        for case, r in cases.items():
            gate_det = r["current_gate"]["detected"]
            trial_det = r["trial_check"]["detected"]
            expected = r["expected_detection"]
            print(f"{path_id:14s} {case:16s} expected={expected!s:5s} "
                  f"current_gate={gate_det!s:5s} trial_check={trial_det!s:5s}")

    print("\n=== false reject sweep ===")
    print(f"total={sweep['total']} false_reject_count={sweep['false_reject_count']}")
    if sweep["false_reject_path_ids"]:
        print("false rejects:", sweep["false_reject_path_ids"])


if __name__ == "__main__":
    main()
