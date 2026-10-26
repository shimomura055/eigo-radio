# -*- coding: utf-8 -*-
"""FAMILY-Y-STYLE-PROFILE-FIX-01 委任_04: Std Human Review承認後の『ユーザー指定takeの採用』手続き(run_style_fix_01対応版・take指定対応)。

先例 `er121_e1_hr_adopt_r0_01.py`(run_01・attempt固定)を一般化したもの。既存関数(asm.record_human_approval / record_y_human_approval /
er008 apply_a2_slowdown / er121_e1_slowed_asr_recheck_01 と同じ正式経路関数)を呼ぶだけで、新Gate/flag/迂回は無い。er121_*.py等は編集していない。
使い方:
  dry-run(既定・何も書かない・API 0):  .venv\\Scripts\\python.exe docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/hr_adopt_style_fix_01.py --level a2 --segment preview --take 1 --dry-run
  減速後ASR再検証(y_voice_1のみ・ASR 1回の有料):  ... --level a2 --segment y_voice_1 --take N --recheck   (本委任では実行しない)
  採用(--apply・ユーザー承認発言の逐語ファイル必須):  ... --apply --user-statement-ref <path>

**承認の主体はユーザーのみ**: --apply は、ユーザー本人の承認発言を逐語保存したファイル(--user-statement-ref)に対象segment・take番号が書かれている場合にだけ働く。
採用できるのは lock state が HUMAN_REVIEW_REQUIRED のsegmentだけ(自動PASS済み/承認済みsegmentは対象外)。
y_voice_1 は採用時に6%減速(ffmpeg atempo、API 0)を適用し、減速後ASR再検証(--recheck)がPASSで、かつ採用候補・減速後wavのsha256が再検証時と一致する場合にのみ採用できる。
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import shutil
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

DEFAULT_RUN = "er121_output/family_y_production_01/redelivery_fee/run_style_fix_01"
APPROVED_BY = "user"
TAG = "ysp5"
ALLOWED = {("a2", "y_voice_1"), ("a2", "preview")}   # 委任_04時点でStd HR対象になり得た2 segment


def _sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _lj(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _sj(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2, default=str)


def _attempt_files(run, level, segment, take):
    base = f"{run}/{level}/narration/attempts"
    js = [f for f in glob.glob(f"{base}/{segment}_attempt{take}_*.json") if "postslowdown" not in f]
    if len(js) != 1:
        raise SystemExit(f"[REFUSED] {segment} take {take} の候補attemptが特定できません(候補={js})。attempts={sorted(os.path.basename(x) for x in glob.glob(f'{base}/{segment}_attempt*.json'))}")
    return js[0][:-5] + ".wav", js[0]


def _canonical(run, level, segment, ent):
    if ent and ent.get("canonical_text"):
        return ent["canonical_text"]
    if segment in (_lj(f"{run}/{level}/support_texts.json")):
        return _lj(f"{run}/{level}/support_texts.json")[segment]
    return _lj(f"{run}/{level}/parts.json")["segments"][segment]


def _would_be_entry(ent, att, route, canon):
    """採用後にtop-level entryへ反映するStyle記録(採用attemptの実測値)。fallbackは短文Styleで承認Styleと異なる(instruction_text無し)。"""
    new = dict(ent or {})
    new["canonical_text"] = canon
    new["voice"], new["model"], new["tts_backend"] = att.get("voice"), att.get("model"), att.get("tts_backend")
    new["fallback_used"] = (route == "minimal_fallback")
    if isinstance(att.get("instruction_text"), str):
        new["style_prefix"] = att["instruction_text"]          # 実際に送信したinstruction(承認Styleのtake)
    else:
        new.pop("style_prefix", None)                           # fallback等: 送信Style実測なし→Gateは一致扱いにしない
    return new


def plan(run: str, level: str, segment: str, take: int) -> dict:
    if (level, segment) not in ALLOWED:
        raise SystemExit(f"[REFUSED] ({level},{segment}) は採用対象外です。対象={sorted(ALLOWED)}")
    wav, js = _attempt_files(run, level, segment, take)
    att = _lj(js)
    route = att.get("route", "")
    lock = _lj(f"{run}/{level}/audit/review_lock_state.json").get(segment) or {}
    res = _lj(f"{run}/{level}/audit/tts_generation_results.json")["segments"].get(segment)
    skipped = (res or {}).get("status") == "SKIPPED_NOT_SELECTED"
    canon = _canonical(run, level, segment, None if skipped else res)
    nar = f"{run}/{level}/narration/{segment}.wav"
    needs_slow = (level, segment) == ("a2", "y_voice_1")
    wb = _would_be_entry(None if skipped else res, att, route, canon)
    ev = None
    try:
        import er019_family_x_style_profile_01 as sp
        role = "FULL_STORY" if segment == "y_voice_1" else None
        prof_id = (wb.get("style_profile") or (res or {}).get("style_profile") or {}).get("profile_id") or _lj(f"{run}/audit/style_profile.json").get("profile_id")
        wb.setdefault("style_profile", (res or {}).get("style_profile") or {"profile_id": prof_id})
        if role:
            ev = sp.evaluate_segment_evidence(wb, level, prof_id, role)
    except Exception as e:     # 予測は参考表示のみ(判定はGateが再実測する)
        ev = {"note": f"style predict skipped: {type(e).__name__}: {e}"}
    return {"run": run, "level": level, "segment": segment, "take": take, "route": route,
            "lock_state": lock.get("state"), "adoptable": lock.get("state") == "HUMAN_REVIEW_REQUIRED",
            "results_entry_status": (res or {}).get("status"), "results_entry_reconstructed_from_attempts": skipped,
            "attempt_wav": wav, "attempt_json": js, "attempt_wav_sha256": _sha(wav), "recorded_attempt_sha256": att.get("sha256"),
            "canonical_text_sha256": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
            "dst": nar, "current_dst_sha256": _sha(nar) if os.path.exists(nar) else None,
            "needs_a2_slowdown": needs_slow, "slowdown_recheck_file": f"{run}/a2/hr_adopt_prep/y_voice_1_take{take}_slowed_asr_recheck.json" if needs_slow else None,
            "fallback_used_after_adoption": wb["fallback_used"], "style_prefix_measured": isinstance(wb.get("style_prefix"), str),
            "predicted_style_eval": ev,
            "will_write": [nar, nar.replace(".wav", "_original.wav") if needs_slow else None, f"{run}/{level}/audit/human_approved_segments.json(+y_binding)",
                           f"{run}/{level}/audit/review_lock_state.json(RESOLVED/HUMAN_APPROVED)", f"{run}/{level}/audit/tts_generation_results.json(top-level entry: Style実測・adopted_*)",
                           f"{run}/{level}/audit/{TAG}_user_approval_record_{segment}.json"],
            "after_apply_next": "--stages provision_shell,gate,assemble,pages,page_verify を1起動(API 0)"}


def recheck(run: str, level: str, segment: str, take: int) -> dict:
    """減速後ASR再検証(有料: ASR 1回+必要ならSecondary)。先例er121_e1_slowed_asr_recheck_01と同じ正式関数(apply_a2_slowdown_postprocess)。"""
    if (level, segment) != ("a2", "y_voice_1"):
        raise SystemExit("[REFUSED] 減速後再検証はa2 y_voice_1のみ")
    import er005_cost_logger as cl
    import er003_v1_n3_01_tts_generate as n3
    import er019_family_x_audio_production_runner_01 as xr
    import er109_xz_scope_01 as scope
    import er078_secondary_run_scope_01 as srs
    p = plan(run, level, segment, take)
    prep = f"{run}/a2/hr_adopt_prep"
    work = f"{prep}/slow_recheck_work_take{take}"
    os.makedirs(work, exist_ok=True)
    cl.init_logger(f"{prep}/y_voice_1_take{take}_slowed_asr_recheck_cost_log.jsonl")
    shutil.copyfile(p["attempt_wav"], f"{work}/{segment}.wav")
    canon = _lj(f"{run}/a2/audit/tts_generation_results.json")["segments"][segment]["canonical_text"]
    tts_input = xr._pnap_supply(canon, n3.tts_safe_news_en(canon))
    result = {"status": "OK"}

    @srs.with_secondary_run
    @scope.family_scope("Y")
    def go():
        with cl.logging_context("run_style_fix_01", "y_voice_1_slowed_asr_recheck"):
            return n3.apply_a2_slowdown_postprocess(segment, work, tts_input, result, is_last_slot=True, log_human_review=False)
    r = go()
    rec = {"segment": segment, "attempt": take, "source_attempt_wav": p["attempt_wav"], "source_attempt_sha256": p["attempt_wav_sha256"],
           "slowed_wav_sha256": _sha(f"{work}/{segment}.wav"), "status": r.get("status"), "asr_verified": r.get("asr_verified"),
           "post_slowdown_final_classification": r.get("post_slowdown_final_classification"), "post_slowdown_asr_text": r.get("post_slowdown_asr_text"),
           "slowdown_info": r.get("slowdown_info"), "recheck_pass": bool(r.get("status") == "OK" and r.get("asr_verified") is True),
           "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    _sj(p["slowdown_recheck_file"], rec)
    return rec


def check_slowed_recheck(p: dict) -> dict:
    path = p["slowdown_recheck_file"]
    if not os.path.isfile(path):
        raise SystemExit(f"[REFUSED] 減速後ASR再検証の実測結果がありません: {path}(--recheck で実測してから採用する)")
    rc = _lj(path)
    if rc.get("recheck_pass") is not True or rc.get("asr_verified") is not True or rc.get("status") != "OK":
        raise SystemExit(f"[REFUSED] 減速後ASR再検証がPASSでないため採用できません: status={rc.get('status')} label={rc.get('post_slowdown_final_classification')}")
    if rc.get("source_attempt_sha256") != p["attempt_wav_sha256"]:
        raise SystemExit("[REFUSED] 減速後ASR再検証の対象wavが採用候補attemptと不一致")
    import tempfile
    import er008_a2_postprocess_slowdown_01 as slow
    with tempfile.TemporaryDirectory() as td:
        tmp = os.path.join(td, "chk.wav")
        slow.apply_a2_slowdown(p["attempt_wav"], tmp)
        if _sha(tmp) != rc.get("slowed_wav_sha256"):
            raise SystemExit("[REFUSED] 採用時に生成される減速後wavが再検証したwavとsha256不一致(検証した音と違う音は採用しない)")
    return {"path": path, "judgement": rc.get("post_slowdown_final_classification"), "slowed_wav_sha256": rc.get("slowed_wav_sha256")}


def apply(run: str, level: str, segment: str, take: int, statement_ref: str) -> dict:
    import er003_v1_n3_01_assemble as asm
    import er121_family_y_audio_01 as ya
    p = plan(run, level, segment, take)
    if not p["adoptable"]:
        raise SystemExit(f"[REFUSED] {segment} のlock stateが {p['lock_state']} です(HUMAN_REVIEW_REQUIREDのみ採用対象。自動PASS済み/承認済みは対象外)")
    if p["attempt_wav_sha256"] != p["recorded_attempt_sha256"]:
        raise SystemExit("[REFUSED] 採用候補wavのsha256が記録と不一致(試聴したものと違う音は採用しない)")
    if not (os.path.isfile(statement_ref) and os.path.getsize(statement_ref) > 0):
        raise SystemExit(f"[REFUSED] --user-statement-ref が存在しません: {statement_ref}")
    stmt = open(statement_ref, encoding="utf-8").read()
    if segment not in stmt or str(take) not in stmt:
        raise SystemExit(f"[REFUSED] ユーザー承認発言ファイルに対象({segment}/take {take})の記載がありません: {statement_ref}")
    recheck_ref = check_slowed_recheck(p) if p["needs_a2_slowdown"] else None
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
        shutil.copyfile(dst, prev_dst)
    att = _lj(p["attempt_json"])
    res = _lj(res_path)
    ent = res["segments"].get(segment) or {}
    if ent.get("status") == "SKIPPED_NOT_SELECTED" or not ent:
        ent = {"status": "OK", "language": att.get("language"), "reconstructed_from_attempts": True}   # --only-segments実行で消えたentryをattemptsから再構成
    canon = _canonical(run, level, segment, ent)
    ent = _would_be_entry(ent, att, att.get("route", ""), canon)
    ent.setdefault("style_profile", (res["segments"].get(segment) or {}).get("style_profile"))
    slow_info = None
    if p["needs_a2_slowdown"]:
        import er008_a2_postprocess_slowdown_01 as slow
        orig = dst.replace(".wav", "_original.wav")
        if os.path.exists(orig) and not os.path.exists(orig.replace(".wav", f".pre_{TAG}_adopt.wav")):
            shutil.copyfile(orig, orig.replace(".wav", f".pre_{TAG}_adopt.wav"))
        shutil.copyfile(p["attempt_wav"], orig)
        slow_info = slow.apply_a2_slowdown(orig, dst)
    else:
        shutil.copyfile(p["attempt_wav"], dst)
    new_sha = _sha(dst)
    if segment == "y_voice_1":      # Y本文: y_binding(承認時のVoice/Style/model)付きで記録(OPEN-535)
        ya.record_y_human_approval(lvdir, segment, canon, tts_voice=att.get("voice"), style_profile=ent.get("style_profile"),
                                   tts_model=att.get("model"), approved_by=APPROVED_BY)
    else:
        asm.record_human_approval(lvdir, segment, canon, approved_by=APPROVED_BY)
    lock = _lj(lock_path)
    le = lock[segment]
    le["prior_state"], le["prior_final_status"] = le.get("state"), le.get("final_status")
    le["state"], le["final_status"], le["updated_at"] = "RESOLVED", "HUMAN_APPROVED", now
    le["adopted_attempt_audio_path"], le["adopted_audio_sha256"] = p["attempt_wav"], new_sha
    le["reason"] = f"個別Human Approval({now}、FAMILY-Y-STYLE-PROFILE-FIX-01)。ユーザーが{segment} take {take}を試聴し採用を承認。原文={statement_ref}。この1segment・1takeへの個別承認のみ。"
    lock[segment] = le
    _sj(lock_path, lock)
    ent["adopted_attempt_audio_path"], ent["adopted_audio_sha256"], ent["sha256"] = p["attempt_wav"], new_sha, new_sha
    ent["text"], ent["asr_text"] = canon, att.get("asr_text")
    ent[f"{TAG.upper()}_HUMAN_APPROVAL_NOTE"] = f"[{now}] 個別Human Approval: {segment} take {take}を採用。ASR NG記録は維持。TTS生成0。原文={statement_ref}"
    if slow_info:
        ent["slowdown_applied"], ent["slowdown_info"], ent["original_path"] = True, slow_info, dst.replace(".wav", "_original.wav")
        ent["post_slowdown_asr_recheck"] = recheck_ref
        ent["duration_seconds"] = slow_info["dst_duration_seconds"]
    res["segments"][segment] = ent
    _sj(res_path, res)
    rec = {"level": level, "segment": segment, "approved_by": APPROVED_BY, "approved_at": now, "user_statement_source": statement_ref, "adopted_take": take,
           "adopted_attempt_wav": p["attempt_wav"], "adopted_audio_sha256": new_sha, "replaced_audio": prev_dst, "slowdown_info": slow_info,
           "fallback_used": ent.get("fallback_used"), "style_prefix_measured": isinstance(ent.get("style_prefix"), str),
           "scope": "this single segment / this take only; NOT a general ASR/QA exemption; no TTS API call"}
    _sj(f"{lvdir}/audit/{TAG}_user_approval_record_{segment}.json", rec)
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", default=DEFAULT_RUN)
    ap.add_argument("--level", required=True, choices=["a2", "b1b"])
    ap.add_argument("--segment", required=True)
    ap.add_argument("--take", required=True, type=int)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="既定。何も書かない・API 0")
    g.add_argument("--recheck", action="store_true", help="y_voice_1の減速後ASR再検証(有料ASR 1回)")
    g.add_argument("--apply", action="store_true")
    ap.add_argument("--user-statement-ref")
    a = ap.parse_args(argv)
    try:
        if a.recheck:
            print(json.dumps(recheck(a.run_dir, a.level, a.segment, a.take), ensure_ascii=False, indent=1))
        elif a.apply:
            if not a.user_statement_ref:
                print("[REFUSED] --apply には --user-statement-ref(ユーザー承認発言の逐語ファイル)が必須です", file=sys.stderr)
                return 2
            print(json.dumps(apply(a.run_dir, a.level, a.segment, a.take, a.user_statement_ref), ensure_ascii=False, indent=1))
        else:
            print(json.dumps({"dry_run": True, "api_calls": 0, "plan": plan(a.run_dir, a.level, a.segment, a.take)}, ensure_ascii=False, indent=1))
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
