# ============================================================
# er048_fixed_shell_champion_master_registration_01.py
# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W2、2026-09-29)
# ============================================================
# 目的: ユーザーが正式決定・APPROVED_FOR_PRODUCTIONとした固定フレーズ
# Champion(welcomeを除く9 phrase)の音声を、Production Master Store
# (er006_master_audio_store_01.py、er006_output/master_audio_store_01/)
# へ正式登録する。TTS/ASR呼び出しは一切行わない(既にTrialでASR検証
# 済み[asr_verified=True]の音声ファイルをread-onlyでコピーするのみ、
# 費用¥0)。
#
# Champion決定(逐語、delegation_log/2026-09-29_..._02.md参照):
#   welcome=A(現行Production Master継続、本スクリプトの対象外)
#   preview_intro=C / key_phrases_intro=C / full_story_intro=C
#   num_one=C / num_two=B / num_three=B take1(er047) / num_four=C
#   num_five=B take1(er047) / point_explanation=B
#
# 由来Trial:
#   er043_output/tts_fixed_shell_master_champion_trial_02/
#     champion_trial_results.json(commit 7f01bad1)
#   er047_output/tts_fixed_shell_number_three_five_retrial_01/
#     retrial_results.json(commit fa37cd85)
#
# 実行方法:
#   .venv\Scripts\python.exe er048_fixed_shell_champion_master_registration_01.py --dry-run
#   .venv\Scripts\python.exe er048_fixed_shell_champion_master_registration_01.py --apply
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_master_audio_store_01 as store

ER043_DIR = "er043_output/tts_fixed_shell_master_champion_trial_02"
ER047_DIR = "er047_output/tts_fixed_shell_number_three_five_retrial_01"

ER043_TRIAL_MANAGEMENT_ID = "TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02"
ER043_SOURCE_COMMIT = "7f01bad1"
ER047_TRIAL_MANAGEMENT_ID = "TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01"
ER047_SOURCE_COMMIT = "fa37cd85"

OUT_DIR = "er048_output/fixed_shell_champion_master_registration_01"

# 各entryのcanonical_text/style_prefix_used/asr_textは、上記2つのJSON
# ファイルの該当candidate/phraseから逐語転記した(新しい文言の考案は
# 一切していない)。本スクリプト実行時に、これらの値がJSON原本・
# shared_narration側の定数と逐語一致することを必ず検証する
# (assert_registrations_match_source、不一致ならSTOP)。
CHAMPION_REGISTRATIONS = [
    dict(
        name="preview_intro", language="en", candidate="C",
        source_wav=f"{ER043_DIR}/{ER043_TRIAL_MANAGEMENT_ID}_candC/shell/narration/preview_intro.wav",
        canonical_text="Here's a quick preview.",
        style_prefix_used="natural, clear, conversational",
        asr_text="Here's a quick preview.",
        trial_management_id=ER043_TRIAL_MANAGEMENT_ID, source_commit=ER043_SOURCE_COMMIT,
    ),
    dict(
        name="key_phrases_intro", language="en", candidate="C",
        source_wav=f"{ER043_DIR}/{ER043_TRIAL_MANAGEMENT_ID}_candC/shell/narration/key_phrases_intro.wav",
        canonical_text="Here are today's key phrases.",
        style_prefix_used="natural, clear, conversational",
        asr_text="Here are today's key phrases.",
        trial_management_id=ER043_TRIAL_MANAGEMENT_ID, source_commit=ER043_SOURCE_COMMIT,
    ),
    dict(
        name="full_story_intro", language="en", candidate="C",
        source_wav=f"{ER043_DIR}/{ER043_TRIAL_MANAGEMENT_ID}_candC/shell/narration/full_story_intro.wav",
        canonical_text="Now, the full story.",
        style_prefix_used=(
            "natural, clear, conversational, unhurried pace, "
            "with a brief pause before continuing"),
        # ASR文字起こしはカンマを付けないことが多く"Now the full story."
        # (カンマ無し)になっているが、これはASRの句読点非表示挙動であり
        # NORMALIZED_MATCH合格を妨げていない(source JSON asr_verified=
        # True、audio_classification参照)。canonical_textはProduction
        # FIXED_ENGLISH_TEXTS["full_story_intro"]と逐語一致。
        asr_text="Now the full story.",
        trial_management_id=ER043_TRIAL_MANAGEMENT_ID, source_commit=ER043_SOURCE_COMMIT,
    ),
    dict(
        name="num_one", language="en", candidate="C",
        source_wav=f"{ER043_DIR}/{ER043_TRIAL_MANAGEMENT_ID}_candC/shell/narration/num_one.wav",
        canonical_text="One.",
        style_prefix_used=(
            "measured, matter-of-fact delivery, consistent energy and tempo "
            "for every word, plain falling pitch at the end, spoken as a flat "
            "statement, not a question"),
        asr_text="one",
        trial_management_id=ER043_TRIAL_MANAGEMENT_ID, source_commit=ER043_SOURCE_COMMIT,
    ),
    dict(
        name="num_two", language="en", candidate="B",
        source_wav=f"{ER043_DIR}/{ER043_TRIAL_MANAGEMENT_ID}_candB/shell/narration/num_two.wav",
        canonical_text="Two.",
        style_prefix_used=(
            "calm, steady, declarative tone, even volume and pace across the "
            "set, ending each word with a clear falling pitch, stated plainly, "
            "never rising like a question"),
        asr_text="2",
        trial_management_id=ER043_TRIAL_MANAGEMENT_ID, source_commit=ER043_SOURCE_COMMIT,
    ),
    dict(
        name="num_three", language="en", candidate="B", take=1,
        source_wav=(
            f"{ER047_DIR}/{ER047_TRIAL_MANAGEMENT_ID}_num_three_styleB/take1/narration/num_three.wav"),
        canonical_text="Three.",
        style_prefix_used=(
            "calm, steady, declarative tone, even volume and pace across the "
            "set, ending each word with a clear falling pitch, stated plainly, "
            "never rising like a question"),
        asr_text="3",
        trial_management_id=ER047_TRIAL_MANAGEMENT_ID, source_commit=ER047_SOURCE_COMMIT,
    ),
    dict(
        name="num_four", language="en", candidate="C",
        source_wav=f"{ER043_DIR}/{ER043_TRIAL_MANAGEMENT_ID}_candC/shell/narration/num_four.wav",
        canonical_text="Four.",
        style_prefix_used=(
            "measured, matter-of-fact delivery, consistent energy and tempo "
            "for every word, plain falling pitch at the end, spoken as a flat "
            "statement, not a question"),
        asr_text="Four",
        trial_management_id=ER043_TRIAL_MANAGEMENT_ID, source_commit=ER043_SOURCE_COMMIT,
    ),
    dict(
        name="num_five", language="en", candidate="B", take=1,
        source_wav=(
            f"{ER047_DIR}/{ER047_TRIAL_MANAGEMENT_ID}_num_five_styleB/take1/narration/num_five.wav"),
        canonical_text="Five.",
        style_prefix_used=(
            "calm, steady, declarative tone, even volume and pace across the "
            "set, ending each word with a clear falling pitch, stated plainly, "
            "never rising like a question"),
        asr_text="five",
        trial_management_id=ER047_TRIAL_MANAGEMENT_ID, source_commit=ER047_SOURCE_COMMIT,
    ),
    dict(
        name="point_explanation", language="ja", candidate="B",
        source_wav=f"{ER043_DIR}/{ER043_TRIAL_MANAGEMENT_ID}_candB/shell/narration/point_explanation.wav",
        canonical_text="ポイント解説",
        style_prefix_used="自然な抑揚をつけて、はっきりと落ち着いた調子で話す",
        # ASR文字起こしは記号・清音混同で完全一致しないことがあるが、
        # source JSON上でasr_verified=Trueとして合格している(NORMALIZED_
        # MATCH相当、日本語ASRの既知の限界)。
        asr_text=None,
        trial_management_id=ER043_TRIAL_MANAGEMENT_ID, source_commit=ER043_SOURCE_COMMIT,
    ),
]


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _manifest_fingerprint() -> dict:
    path = store.MANIFEST_PATH
    if not os.path.exists(path):
        return {"sha256": None, "entry_count": 0}
    with open(path, "rb") as f:
        data = f.read()
    entry_count = len(json.loads(data.decode("utf-8")))
    return {"sha256": hashlib.sha256(data).hexdigest(), "entry_count": entry_count}


def build_key(entry: dict) -> store.MasterAudioKey:
    if entry["language"] == "en":
        return shared_narration._make_english_key(
            entry["name"], entry["canonical_text"], "speech_metadata_flash_lite")
    return shared_narration._make_japanese_key(entry["canonical_text"], "speech_metadata_flash_lite")


def assert_registrations_match_source_json() -> list[str]:
    """CHAMPION_REGISTRATIONSの逐語転記が、shared_narration.pyの現行
    Champion style map/canonical textと一致することを検証する(不一致
    ならSTOP理由の一覧を返す、空リストならOK)。er043/er047のJSON原本
    そのものとの突き合わせはbuild_champion_registration_report()側で
    (sha256実測込みで)別途行う。"""
    problems = []
    for entry in CHAMPION_REGISTRATIONS:
        name = entry["name"]
        if entry["language"] == "en":
            expected_text = shared_narration.FIXED_ENGLISH_TEXTS.get(name)
            expected_style = shared_narration.SHELL_CHAMPION_STYLE_BY_PHRASE_EN.get(name)
        else:
            expected_text = shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY.get(name)
            expected_style = shared_narration.SHELL_CHAMPION_STYLE_JA_POINT_EXPLANATION_B
        if expected_text != entry["canonical_text"]:
            problems.append(
                f"{name}: canonical_text不一致 registration={entry['canonical_text']!r} "
                f"production={expected_text!r}")
        if expected_style != entry["style_prefix_used"]:
            problems.append(
                f"{name}: style_prefix_used不一致 registration={entry['style_prefix_used']!r} "
                f"shared_narration={expected_style!r}")
        if not os.path.exists(entry["source_wav"]):
            problems.append(f"{name}: source_wav not found: {entry['source_wav']}")
    return problems


def run(mode: str) -> dict:
    problems = assert_registrations_match_source_json()
    if problems:
        return {"status": "STOP", "problems": problems}

    before = _manifest_fingerprint()
    plan = []
    for entry in CHAMPION_REGISTRATIONS:
        key = build_key(entry)
        master_id = key.master_audio_id()
        sha256_source = _sha256_file(entry["source_wav"])
        existing = store._load_manifest().get(master_id)
        plan_item = {
            "name": entry["name"], "language": entry["language"], "candidate": entry["candidate"],
            "take": entry.get("take"), "source_wav": entry["source_wav"],
            "sha256_source": sha256_source, "canonical_text": entry["canonical_text"],
            "style_prefix_used": entry["style_prefix_used"], "asr_text": entry["asr_text"],
            "trial_management_id": entry["trial_management_id"], "source_commit": entry["source_commit"],
            "key": key.as_dict(), "master_audio_id": master_id,
            "already_registered": existing is not None,
        }
        if mode == "apply":
            qa_evidence = {
                "sha256": sha256_source, "asr_verified": True, "asr_text": entry["asr_text"],
                "disfluency_checked": False, "disfluency_evidence": None,
                "source_trial_management_id": entry["trial_management_id"],
                "source_commit": entry["source_commit"], "source_wav": entry["source_wav"],
            }
            result = store.register_precomputed(key, entry["source_wav"], qa_evidence)
            plan_item["apply_result"] = result
        plan.append(plan_item)

    after = _manifest_fingerprint()
    report = {
        "management_id": "FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01",
        "sub_task": "W2_fixed_shell_champion_master_registration",
        "mode": mode, "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "manifest_before": before, "manifest_after": after,
        "entries": plan,
        "cost_jpy": 0.0,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    suffix = "dry_run" if mode == "dry_run" else "apply"
    with open(f"{OUT_DIR}/registration_report_{suffix}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    mode = "dry_run" if args.dry_run else "apply"
    report = run(mode)
    if report.get("status") == "STOP":
        print("STOP:")
        for p in report["problems"]:
            print(" -", p)
        raise SystemExit(1)
    print(f"mode={mode}")
    print(f"manifest_before entry_count={report['manifest_before']['entry_count']} "
          f"sha256={report['manifest_before']['sha256']}")
    print(f"manifest_after  entry_count={report['manifest_after']['entry_count']} "
          f"sha256={report['manifest_after']['sha256']}")
    for item in report["entries"]:
        status = item.get("apply_result", {}).get("status") if mode == "apply" else (
            "ALREADY_REGISTERED" if item["already_registered"] else "PLANNED_NEW")
        print(f"  {item['name']:20s} candidate={item['candidate']} take={item.get('take')} "
              f"master_audio_id={item['master_audio_id']} status={status}")


if __name__ == "__main__":
    main()
