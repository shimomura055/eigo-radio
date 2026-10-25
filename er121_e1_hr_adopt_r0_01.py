# -*- coding: utf-8 -*-
"""FAMILY-Y-PRODUCTION-LAUNCH-01 委任_07: E-1(宅配 redelivery_fee run_01)のHuman Review承認後に『書換え前(R0本文)の試聴済みattempt』を採用する1回限りの手続き(API 0)。
先例(同じ既存機構の適用): er019_fx_moon_title_individual_approval_01.py / er011_discovery_generalization_towels_trial_11_audio_03_b1b_individual_approval_and_assemble_01.py
(=採用wavをnarrationへ配置 + 既存 asm.record_human_approval() + review_lock_state RESOLVED/HUMAN_APPROVED + results注記。新Gate/flag/迂回なし)。

**承認の主体はユーザーのみ**: --apply は、ユーザー本人の承認発言を逐語保存したファイル(--user-statement-ref)が存在し、そこに対象segmentの
識別子が書かれている場合にだけ働く(AI/Fableは承認を代行しない。この条件を満たさない呼出はrc=2で何も書かない)。既定はdry-run(何も書かない)。
採用対象は er121_e1_hr_listening_page_01.TARGETS の3 segment・試聴ページと同一attemptのみ(attempt番号は引数にできない)。
a2 y_voice_1 は採用時に6%減速(ffmpeg atempo、API 0)を適用する(ユーザーが聴いた音=採用される音。減速後ASR再検証は『ユーザー試聴承認で代替』と記録)。"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import sys
import time

import er121_e1_hr_listening_page_01 as lp

DEFAULT_RUN = lp.RUN
APPROVED_BY = "user"
TAG = "ypl7"


def _sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _lj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _sj(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2, default=str)


def _target(level: str, segment: str):
    for lv, sid, n, route, _mp3, _t in lp.TARGETS:
        if lv == level and sid == segment:
            return n, route
    raise SystemExit(f"[REFUSED] ({level},{segment}) は採用対象外です。対象={[(t[0], t[1]) for t in lp.TARGETS]}")


def plan(run: str, level: str, segment: str) -> dict:
    n, route = _target(level, segment)
    narr = f"{run}/{level}/narration"
    att_wav = f"{narr}/attempts/{segment}_attempt{n}_{route}.wav"
    att_json = f"{narr}/attempts/{segment}_attempt{n}_{route}.json"
    res = _lj(f"{run}/{level}/audit/tts_generation_results.json")["segments"][segment]
    canon = res["canonical_text"]               # 承認key(M3 `_approved`はentry.canonical_textのshaで照合)
    return {"run": run, "level": level, "segment": segment, "attempt": n, "attempt_wav": att_wav, "attempt_json": att_json,
            "dst": f"{narr}/{segment}.wav", "canonical_text_sha256": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
            "attempt_wav_sha256": _sha(att_wav), "recorded_attempt_sha256": _lj(att_json).get("sha256"),
            "needs_a2_slowdown": level == "a2" and segment == "y_voice_1",
            "current_dst_sha256": _sha(f"{narr}/{segment}.wav") if os.path.exists(f"{narr}/{segment}.wav") else None}


def apply(run: str, level: str, segment: str, statement_ref: str) -> dict:
    import er003_v1_n3_01_assemble as asm
    p = plan(run, level, segment)
    if p["attempt_wav_sha256"] != p["recorded_attempt_sha256"]:
        raise SystemExit("[REFUSED] 採用候補wavのsha256が試聴時の記録と不一致(試聴したものと違う音は採用しない)")
    if not (os.path.isfile(statement_ref) and os.path.getsize(statement_ref) > 0):
        raise SystemExit(f"[REFUSED] --user-statement-ref が存在しません: {statement_ref}(ユーザー本人の承認発言の逐語保存が必要)")
    with open(statement_ref, encoding="utf-8") as f:
        stmt = f.read()
    if segment not in stmt or level not in stmt:
        raise SystemExit(f"[REFUSED] ユーザー承認発言ファイルに対象({level}/{segment})の記載がありません: {statement_ref}")
    lvdir = f"{run}/{level}"
    res_path, lock_path = f"{lvdir}/audit/tts_generation_results.json", f"{lvdir}/audit/review_lock_state.json"
    for path in (res_path, lock_path):
        b = path.replace(".json", f".pre_{TAG}_adopt_backup.json")
        if not os.path.exists(b):
            shutil.copyfile(path, b)
    now = time.strftime("%Y-%m-%dT%H:%M:%S")
    dst = p["dst"]
    prev_dst = dst.replace(".wav", f".pre_{TAG}_adopt.wav")
    if os.path.exists(dst) and not os.path.exists(prev_dst):
        shutil.copyfile(dst, prev_dst)             # 書換え版(または最終fallback版)を証跡として保全
    res = _lj(res_path)
    ent = res["segments"][segment]
    slow_info = None
    if p["needs_a2_slowdown"]:
        import er008_a2_postprocess_slowdown_01 as slow
        orig = dst.replace(".wav", "_original.wav")
        if os.path.exists(orig):
            bo = orig.replace(".wav", f".pre_{TAG}_adopt.wav")
            if not os.path.exists(bo):
                shutil.copyfile(orig, bo)
        shutil.copyfile(p["attempt_wav"], orig)
        slow_info = slow.apply_a2_slowdown(orig, dst)
    else:
        shutil.copyfile(p["attempt_wav"], dst)
    new_sha = _sha(dst)
    asm.record_human_approval(lvdir, segment, ent["canonical_text"], approved_by=APPROVED_BY)
    lock = _lj(lock_path)
    le = lock[segment]
    if le.get("state") != "RESOLVED" or le.get("final_status") != "HUMAN_APPROVED":
        le["prior_state"], le["prior_final_status"] = le.get("state"), le.get("final_status")
        le["state"], le["final_status"], le["updated_at"] = "RESOLVED", "HUMAN_APPROVED", now
        le["adopted_attempt_audio_path"], le["adopted_audio_sha256"] = p["attempt_wav"], new_sha
        le["reason"] = f"個別Human Approval({now}、FAMILY-Y-PRODUCTION-LAUNCH-01 E-1)。ユーザーが書換え前(R0本文)のattempt{p['attempt']}を試聴し採用を承認。原文={statement_ref}。この1segment・1attemptへの個別承認のみ(一般的なASR/QA検査免除ではない)。"
    lock[segment] = le
    _sj(lock_path, lock)
    att = _lj(p["attempt_json"])
    ent[f"{TAG.upper()}_HUMAN_APPROVAL_NOTE"] = (
        f"[{now}] 個別Human Approval: ユーザー試聴・R0本文のattempt{p['attempt']}を採用。ASR/QAのNG記録(attempts_log/attempt_history/human_review_queue)は維持。"
        f"narration/{segment}.wavを置換(置換前={os.path.basename(prev_dst)})。TTS生成0。一般仕様ではない。原文={statement_ref}")
    ent["adopted_attempt_audio_path"], ent["adopted_audio_sha256"] = p["attempt_wav"], new_sha
    ent["sha256"] = new_sha
    if "text_before_adoption" not in ent and ent.get("text") not in (None, ent["canonical_text"]):
        ent["text_before_adoption"] = ent.get("text")
    ent["text"] = ent["canonical_text"]
    ent["asr_text"] = att.get("asr_text")
    if ent.get("local_rewrite_recovery"):
        ent["local_rewrite_audio_superseded_by_human_approval"] = True
    if slow_info:
        ent["slowdown_applied"], ent["slowdown_info"], ent["original_path"] = True, slow_info, dst.replace(".wav", "_original.wav")
        ent["post_slowdown_asr_recheck"] = "NOT_RUN: ユーザーが減速後の音を試聴して承認(減速後ASR再検証の代替)"
        ent["duration_seconds"] = slow_info["dst_duration_seconds"]
    res["segments"][segment] = ent
    _sj(res_path, res)
    rec = {"level": level, "segment": segment, "approved_by": APPROVED_BY, "approved_at": now, "user_statement_source": statement_ref,
           "adopted_attempt": p["attempt"], "adopted_attempt_wav": p["attempt_wav"], "adopted_audio_sha256": new_sha,
           "replaced_audio": prev_dst, "canonical_text_sha256": p["canonical_text_sha256"], "slowdown_info": slow_info,
           "scope": "this single segment / this attempt only; NOT a general ASR/QA exemption; no TTS/ASR API call"}
    _sj(f"{lvdir}/audit/{TAG}_user_approval_record_{segment}.json", rec)
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", default=DEFAULT_RUN)
    ap.add_argument("--level", required=True, choices=["a2", "b1b"])
    ap.add_argument("--segment", required=True)
    ap.add_argument("--user-statement-ref", help="ユーザー本人の承認発言を逐語保存したファイル(--apply時に必須)")
    ap.add_argument("--apply", action="store_true", help="指定しなければdry-run(何も書かない)")
    a = ap.parse_args(argv)
    if not a.apply:
        print(json.dumps({"dry_run": True, "plan": plan(a.run_dir, a.level, a.segment)}, ensure_ascii=False, indent=1))
        return 0
    if not a.user_statement_ref:
        print("[REFUSED] --apply には --user-statement-ref(ユーザー承認発言の逐語ファイル)が必須です", file=sys.stderr)
        return 2
    try:
        r = apply(a.run_dir, a.level, a.segment, a.user_statement_ref)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
