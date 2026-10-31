# ============================================================
# er109_hr_lock_rejudge_01.py  (API 0 / 費用0 / 読取専用 + 候補file・追記logの書込のみ)
# ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_04 (Opus M2/M12、WIRING_DESIGN_03 §E-4)
# HR Lock済みsegment(Family X/Z)の保存転写を、現行judge(er109込み)で**再判定**し、『再生成承認候補』を列挙する明示CLI。
#   - 自動解除はしない。er011_human_review_lock_01(A/B/C共有)は編集しない・呼ばない(approve_regenerateは人間が候補を見て実行する。
#     実行する場合は approved_by="user:er109_rejudge:<candidate_id>" を渡すだけ。本CLIは approve_regenerate を呼ばない=AST testで固定)。
#   - scopeはデータ側のFamilyで決める(M2): <level_dir>のoutput rootがX/Zの許可リストにあるときだけ。違えば拒否(--scope指定は設けない)。
#       許可root: er019_output/ = Family X、er026_output/ = Family Z。それ以外(A/B/C・不明)は拒否。
#   - 候補の条件: lockのcanonical text sha256が results の text と一致 / attemptごとに記録sha256と現在のwav sha256が一致(不一致・欠落は候補外=INSUFFICIENT_EVIDENCE)
#       / 保存転写(Primary・Secondary、KPはWhisperも)で再判定。KPで3票が揃わなければINSUFFICIENT_EVIDENCE。
#   - 区分: PASS(全attemptが警告なしで合格) / PASS_WITH_WARNING(合格だが警告あり=事後試聴必須) / INSUFFICIENT_EVIDENCE / NOT_CANDIDATE(再判定でもNG)。
# 出力: <level_dir>/audit/er109_hr_rejudge_candidates.json(最新) + <level_dir>/audit/er109_hr_rejudge_log.jsonl(実行ごとの追記)。--no-write で書込なし。
# 使い方: python er109_hr_lock_rejudge_01.py --level-dir <.../a2|b1b> [--segment-id ID ...] [--no-write]
#         python er109_hr_lock_rejudge_01.py --scan [--no-write]     # er019_output/ er026_output/ 配下の全levelを走査
# ============================================================
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys
import re
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import er109_xz_scope_01 as xz

# データ側Familyの許可リスト(M2)。output rootの先頭ディレクトリ -> Family。これ以外は拒否。
_JA_CHARS = re.compile(r"[぀-ヿ㐀-鿿]")
OUTPUT_ROOT_FAMILY = {"er019_output": "X", "er026_output": "Z"}
LOCKED_STATES = ("HUMAN_REVIEW_REQUIRED", "HUMAN_REVIEW_LOCKED")
CLASS_PASS, CLASS_PWW, CLASS_INSUFF, CLASS_NOT = "PASS", "PASS_WITH_WARNING", "INSUFFICIENT_EVIDENCE", "NOT_CANDIDATE"


class RefusedFamily(ValueError):
    pass


def family_of_level_dir(level_dir: str) -> str:
    """level_dirのデータ側Family。X/Zのoutput rootのみ許可、違えばRefusedFamily。"""
    rel = os.path.relpath(os.path.abspath(level_dir), ROOT).replace("\\", "/")
    top = rel.split("/")[0]
    fam = OUTPUT_ROOT_FAMILY.get(top)
    if fam is None or rel.startswith(".."):
        raise RefusedFamily(f"{level_dir!r}: output root {top!r} はFamily X/Zの許可リスト{sorted(OUTPUT_ROOT_FAMILY)}にありません(A/B/C・不明は拒否)")
    return fam


def _sha256_file(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _code_commit() -> dict:
    try:
        h = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=20).stdout.strip()
        d = subprocess.run(["git", "status", "--porcelain", "--", "er109_xz_scope_01.py", "er078_asr_unified_judge_01.py", "er006_secondary_asr_01.py",
                            "er104_kp_three_asr_vote_01.py", "er019_family_x_validation_inheritance_01.py", "er109_asr_orthographic_equivalence_01.py",
                            "er109_ukus_spelling_01.py", "er109_ukus_pairs_v1.json"],
                           cwd=ROOT, capture_output=True, text=True, timeout=20).stdout.strip()
        return {"commit": h, "judge_files_dirty": bool(d)}
    except Exception as exc:  # noqa: BLE001
        return {"commit": None, "error": f"{type(exc).__name__}: {exc}"}


def _results_text(results: dict, segment_id: str):
    """results(tts_generation_results.json)から segment_id のcanonical textとentryを返す。KPは kp{rank}_en。"""
    segs = (results.get("segments") or {})
    if segment_id in segs and isinstance(segs[segment_id], dict):
        e = segs[segment_id]
        return (e.get("canonical_text") or e.get("text")), e, False
    if segment_id.startswith("kp") and segment_id.endswith("_en"):
        rank = segment_id[2:-3]
        e = (((results.get("key_phrases") or {}).get(rank) or {}).get("english"))
        if isinstance(e, dict):
            return (e.get("canonical_text") or e.get("text")), e, True
    return None, None, False


def _attempt_sha(att: dict):
    aj = att.get("asr_judgement") if isinstance(att.get("asr_judgement"), dict) else {}
    return aj.get("audio_sha256")


def _old_judgement(att: dict) -> dict:
    aj = att.get("asr_judgement") if isinstance(att.get("asr_judgement"), dict) else {}
    return {"state": aj.get("state"), "reason_code": aj.get("reason_code"), "verified": att.get("verified"),
            "audio_classification": att.get("audio_classification")}


def _rejudge_attempt_nonkp(canonical: str, seg_id: str, level: str, att: dict, res_entry: dict) -> dict:
    import er019_family_x_validation_inheritance_01 as vi
    entry = {"text": canonical, "asr_text": att.get("asr_text"), "sha256": _attempt_sha(att) or "", "asr_judgement": att.get("asr_judgement"),
             # ASR-FLAP-T-PRODUCTION-WIRING-01: 保存attemptの出自(voice/model)。asr_judgement.tts_provenanceがあればそちらが優先。無ければ適用外(fail-closed)
             "voice": att.get("voice"), "model": att.get("model")}
    if isinstance(res_entry, dict) and res_entry.get("local_rewrite"):
        entry["local_rewrite"] = res_entry.get("local_rewrite")
    if not att.get("asr_text"):
        return {"state": CLASS_INSUFF, "reason": "no_stored_primary_transcript"}
    rj = vi.rejudge_with_current_judge(entry, level, seg_id, force_lang="en")
    rec = rj.get("asr_judgement_inherited") or {}
    ustate, ureason = rj.get("unified_state"), rj.get("unified_reason_code")
    if ustate in ("NG_SECONDARY_UNAVAILABLE",) or (ureason or "") in ("secondary_unavailable",):
        return {"state": CLASS_INSUFF, "reason": f"stored_secondary_transcript_missing({ureason})", "unified_state": ustate}
    out = {"unified_state": ustate, "reason": ureason, "ok": bool(rj.get("ok")), "warnings": list(rec.get("warnings") or []),
           "orthographic_equivalence": rec.get("orthographic_equivalence"), "final_gate": rec.get("final_gate"),
           "value_guard": rec.get("value_guard"), "negation_guard": rec.get("negation_guard")}
    if rj.get("ok"):
        out["state"] = CLASS_PWW if out["warnings"] else CLASS_PASS
    else:
        out["state"] = CLASS_NOT
    return out


def _rejudge_attempt_kp(canonical: str, att: dict) -> dict:
    import er139_flapt_provenance_01 as _flapt_prov     # ASR-FLAP-T-PRODUCTION-WIRING-01: 保存attemptの出自をhydrateして票を再構築
    with _flapt_prov.rejudge_context(dict(att, sha256=_attempt_sha(att) or att.get("sha256")), tag="hr_kp_rejudge", speedup_possible=False):   # KP音声に高速化はない
        return _rejudge_attempt_kp_impl(canonical, att)


def _rejudge_attempt_kp_impl(canonical: str, att: dict) -> dict:
    import er104_kp_three_asr_vote_01 as kp3v
    aj = att.get("asr_judgement") if isinstance(att.get("asr_judgement"), dict) else {}
    vote = aj.get("vote") if isinstance(aj.get("vote"), dict) else {}
    p_text = att.get("asr_text") or (vote.get("primary") or {}).get("text")
    s_text = (vote.get("secondary") or {}).get("text") or (aj.get("secondary") or {}).get("text")
    w_text = (vote.get("whisper") or {}).get("text") if vote.get("whisper_called") else None
    max_len = att.get("max_len")
    if not p_text or not s_text:
        return {"state": CLASS_INSUFF, "reason": "kp_primary_or_secondary_transcript_missing"}
    pv = kp3v.make_voter("openai", canonical, p_text, lang="en", max_len=max_len)
    sv = kp3v.make_voter("azure", canonical, s_text, lang="en", max_len=max_len)
    wv = None
    if kp3v.whisper_needed(pv, sv):
        if not w_text:
            return {"state": CLASS_INSUFF, "reason": "kp_split_vote_needs_whisper_transcript_but_none_stored"}
        wv = kp3v.make_voter("whisper", canonical, w_text, lang="en", max_len=max_len, ambiguous_blocks=True)
    tr = kp3v.tally(pv, sv, wv)
    warnings = []
    for v in (pv, sv, wv):
        if v is not None and v.passed and v.ortho_applied:
            warnings += [w for w in v.ortho_warnings if w not in warnings]
    if tr.secondary_confirmed_warning:
        warnings.append("SECONDARY_CONFIRMED")
    out = {"unified_state": tr.state, "reason": tr.reason, "ok": bool(tr.verified), "warnings": warnings, "vote_row": tr.row,
           "votes": {"primary": pv.audit(), "secondary": sv.audit(), "whisper": (wv.audit() if wv else None)}}
    out["state"] = (CLASS_PWW if warnings else CLASS_PASS) if tr.verified else CLASS_NOT
    return out


def evaluate_level(level_dir: str, segment_ids=None) -> dict:
    """1 levelのHR Lock済みsegmentを再判定して候補を返す(読取のみ)。X/Z以外のrootはRefusedFamily。"""
    fam = family_of_level_dir(level_dir)            # M2: データ側Familyで決める。--scopeは受け付けない
    level = os.path.basename(os.path.abspath(level_dir))
    lock_path = os.path.join(level_dir, "audit", "review_lock_state.json")
    res_path = os.path.join(level_dir, "audit", "tts_generation_results.json")
    report = {"level_dir": level_dir.replace("\\", "/"), "family": fam, "level": level, "candidates": [], "skipped": [],
              "execution": {**_code_commit(), "scope": fam, "ran_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "api_calls": 0}}
    if not os.path.exists(lock_path):
        report["skipped"].append({"reason": "no_review_lock_state"})
        return report
    lock = json.load(open(lock_path, encoding="utf-8"))
    results = json.load(open(res_path, encoding="utf-8")) if os.path.exists(res_path) else {}
    import er109_asr_orthographic_equivalence_01 as e109
    report["execution"]["er109_version"] = e109.LAYER_VERSION
    report["execution"]["flag_enabled"] = e109.is_enabled()
    for seg_id, le in sorted(lock.items()):
        if not isinstance(le, dict) or le.get("state") not in LOCKED_STATES:
            continue
        if segment_ids and seg_id not in segment_ids:
            continue
        canonical, res_entry, is_kp = _results_text(results, seg_id)
        ident = {"theme_id": le.get("theme_id"), "level": le.get("level") or level, "segment_id": seg_id,
                 "lock": {"state": le.get("state"), "reason": le.get("reason"), "updated_at": le.get("updated_at"),
                          "canonical_text_sha256": le.get("canonical_text_sha256")}}
        cand = {"candidate_id": None, "identification": ident, "attempts": [], "class": CLASS_INSUFF, "basis": {}, "note": None}
        base_id = f"{ident['theme_id']}/{ident['level']}/{seg_id}"
        if not canonical:
            cand.update(candidate_id=base_id + "@no_text", note="results側にcanonical textが無い=候補外(INSUFFICIENT_EVIDENCE)")
            report["candidates"].append(cand)
            continue
        ident["canonical_text"], ident["canonical_text_sha256"] = canonical, _text_hash(canonical)
        if _JA_CHARS.search(canonical):
            # er109は英語ASR(en)専用。日本語segmentは対象外(英語judgeに強制langで通さない)=候補外
            cand.update(candidate_id=f"{ident['theme_id']}/{ident['level']}/{seg_id}@{ident['canonical_text_sha256'][:8]}", **{"class": CLASS_NOT},
                        note="日本語を含むsegment=er109(英語ASR専用)の対象外。再判定しない(NOT_CANDIDATE)")
            report["candidates"].append(cand)
            continue
        cand["candidate_id"] = f"{base_id}@{ident['canonical_text_sha256'][:8]}"
        if ident["canonical_text_sha256"] != le.get("canonical_text_sha256"):
            cand["note"] = "lockのcanonical text sha256とresultsのtextが不一致=候補外(INSUFFICIENT_EVIDENCE)"
            report["candidates"].append(cand)
            continue
        attempts = [a for a in (le.get("last_attempts_log") or []) if isinstance(a, dict)]
        if not attempts:
            cand["note"] = "last_attempts_logが空=候補外(INSUFFICIENT_EVIDENCE)"
            report["candidates"].append(cand)
            continue
        states = []
        with (xz.run_scope("X") if fam == "X" else xz.run_scope("Z")):      # データ側Familyで決めたscope(リテラル分岐)
            for att in attempts:
                rec_sha = _attempt_sha(att)
                wav = att.get("attempt_audio_path")
                cur_sha = _sha256_file(wav) if wav else None
                row = {"attempt": att.get("attempt"), "wav_path": wav, "recorded_sha256": rec_sha, "current_sha256": cur_sha,
                       "sha_match": bool(rec_sha and cur_sha and rec_sha == cur_sha),
                       "stored_transcripts": {"primary": att.get("asr_text"),
                                              "secondary": (((att.get("asr_judgement") or {}).get("secondary") or {}).get("text")
                                                            or (((att.get("asr_judgement") or {}).get("vote") or {}).get("secondary") or {}).get("text")),
                                              "whisper": ((((att.get("asr_judgement") or {}).get("vote") or {}).get("whisper") or {}).get("text"))},
                       "old": _old_judgement(att)}
                if not row["sha_match"]:
                    row["new"] = {"state": CLASS_INSUFF, "reason": "wav_sha256_missing_or_mismatch(記録shaと現在の音声が一致しない/音声欠落=候補外)"}
                else:
                    try:
                        row["new"] = (_rejudge_attempt_kp(canonical, att) if is_kp else _rejudge_attempt_nonkp(canonical, seg_id, ident["level"], att, res_entry))
                    except Exception as exc:  # noqa: BLE001
                        row["new"] = {"state": CLASS_INSUFF, "reason": f"rejudge_error:{type(exc).__name__}: {exc}"}
                states.append(row["new"]["state"])
                cand["attempts"].append(row)
        if CLASS_INSUFF in states:
            cand["class"] = CLASS_INSUFF
        elif CLASS_NOT in states:
            cand["class"] = CLASS_NOT
        elif CLASS_PWW in states:
            cand["class"] = CLASS_PWW
        else:
            cand["class"] = CLASS_PASS
        cand["any_attempt_passes_now"] = any(s in (CLASS_PASS, CLASS_PWW) for s in states)
        cand["basis"] = {"er109_version": e109.LAYER_VERSION,
                         "per_attempt": [{"attempt": r["attempt"], "orthographic_equivalence": (r["new"].get("orthographic_equivalence")),
                                          "final_gate": r["new"].get("final_gate")} for r in cand["attempts"] if r["new"].get("orthographic_equivalence")]}
        cand["note"] = ("再生成承認候補(自動解除なし)。人間が確認のうえ必要な場合のみ er011_human_review_lock_01.approve_regenerate(out_path, text, "
                        f"approved_by='user:er109_rejudge:{cand['candidate_id']}') を実行する。" +
                        (" 警告付き合格を含む=事後試聴必須。" if cand["class"] == CLASS_PWW else ""))
        report["candidates"].append(cand)
    return report


def write_outputs(report: dict) -> list:
    audit_dir = os.path.join(report["level_dir"], "audit")
    os.makedirs(audit_dir, exist_ok=True)
    p1 = os.path.join(audit_dir, "er109_hr_rejudge_candidates.json")
    p2 = os.path.join(audit_dir, "er109_hr_rejudge_log.jsonl")
    with open(p1, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    with open(p2, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"ran_at": report["execution"]["ran_at"], "family": report["family"], "level_dir": report["level_dir"],
                            "candidates": [{"id": c["candidate_id"], "class": c["class"]} for c in report["candidates"]],
                            "commit": report["execution"].get("commit")}, ensure_ascii=False) + "\n")
    return [p1, p2]


def scan_level_dirs() -> list:
    out = []
    for root in OUTPUT_ROOT_FAMILY:
        for p in glob.glob(os.path.join(ROOT, root, "**", "audit", "review_lock_state.json"), recursive=True):
            out.append(os.path.dirname(os.path.dirname(p)))
    return sorted(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="X/Zの既存HR Lock済みsegmentをer109込みの現行judgeで再判定し、再生成承認候補を列挙する(自動解除なし)")
    ap.add_argument("--level-dir")
    ap.add_argument("--segment-id", action="append")
    ap.add_argument("--scan", action="store_true", help="er019_output/ er026_output/ 配下の全levelを走査")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--summary-out", help="全levelの集計jsonの出力先(任意)")
    a = ap.parse_args(argv)
    dirs = scan_level_dirs() if a.scan else [a.level_dir]
    if not dirs or dirs == [None]:
        ap.error("--level-dir か --scan が必要")
    reports, summary = [], {"levels": 0, "locked_segments": 0, "by_class": {}, "refused": []}
    for d in dirs:
        try:
            rep = evaluate_level(d, set(a.segment_id) if a.segment_id else None)
        except RefusedFamily as exc:
            summary["refused"].append(str(exc))
            print("REFUSED:", exc, file=sys.stderr)
            continue
        if not rep["candidates"]:
            continue
        reports.append(rep)
        summary["levels"] += 1
        for c in rep["candidates"]:
            summary["locked_segments"] += 1
            summary["by_class"][c["class"]] = summary["by_class"].get(c["class"], 0) + 1
        if not a.no_write:
            write_outputs(rep)
    summary["reports"] = reports
    if a.summary_out:
        os.makedirs(os.path.dirname(os.path.abspath(a.summary_out)), exist_ok=True)
        with open(a.summary_out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "reports"}, ensure_ascii=False))
    for rep in reports:
        for c in rep["candidates"]:
            print(f"  [{c['class']}] {c['candidate_id']}")
    return 2 if summary["refused"] and not reports else 0


if __name__ == "__main__":
    sys.exit(main())
