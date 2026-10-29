# -*- coding: utf-8 -*-
"""FZ-DIALOGUE-LR-ADOPTION-01 委任_02: 既存clipの状態移行tool(運用ツール。Production経路ではない・どのProductionコードからもimportされない)。

目的(ユーザー原文 docs/pm/delegation_log/2026-10-29_FZ-DIALOGUE-LR-ADOPTION-01_USER.md §3): 『藪の中』Advanced `full_story_part3_c6` のように、
旧仕様(ZセリフLRなし・3回)で #1〜#3 を消費して Human Review Lock(TERMINAL_NG)に到達済みのclipを、#1〜#3 を再実行せず、新仕様のLR段階から正規に再開させる。

  * 既存のHuman Review Lock・試行上限・resume管理を迂回しない: Lockは既存の`review_lock.approve_regenerate`(ユーザーの明示指示でのみ呼ぶAPI)で承認し、
    承認の根拠(原文§3)を`--authorization-ref`で記録する。承認は次の1回の生成(再開)で消費される(`consuming_regenerate_approval`)。
  * 3試行は『消費済み』として引き継ぐ(attempts/log_rows/cooldown/費用・音声・Gate結果は不変。n_started=3のまま)。stateを v2(phase=LR, lr.state=PENDING)へ。
  * LR入力に使う転写(`ng_transcripts`)をstate自身のlog_rowsと`attempt_history.jsonl`から**出典付き**で補完する(M5)。
    attempt_historyのA2_SLOWDOWN_REVERIFYイベントは、segment・level・theme・時刻窓[当該attemptの完了〜減速後NG確定+余裕]・直前のPROCEED event(本文sha一致)で
    照合し、候補がちょうど1件のときだけ採用する(複数=曖昧=中止、0件=補完なしで警告)。
  * 既定=dry-run(何も書かない)。`--apply`のときだけ書く。書込順は M7: state/Lock両ファイルを`*.pre_fzlr_migration`へ退避 → state → Lock → 履歴。
    失敗時は両方を退避から復元する。完全移行済みの2回目は拒否。部分適用(state済み・Lock/履歴未了)は検知して、残りを完了するか(`--apply`)、`--restore`で復元する。
  * 他clipのstate・Lockには一切触れない(--clipで明示した1clipのみ。複数clipの暗黙適用なし)。

使い方(repo rootで): python docs/research/FZ-DIALOGUE-LR-ADOPTION-01/tools/fz_dialogue_lr_resume_01.py --run-dir <run> --level b1b --clip full_story_part3_c6 [--apply --authorization-ref "..."]
rc: 0=成功(dry-runで前提OK含む) / 2=前提違反(書込0) / 3=STOP該当 / 4=書込失敗(復元済み)
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

MANAGEMENT_ID = "FZ-DIALOGUE-LR-ADOPTION-01"
BACKUP_SUFFIX = ".pre_fzlr_migration"
EVENT_NAME = "FZ_DIALOGUE_LR_RESUME_MIGRATION"
ROLLBACK_EVENT = "FZ_DIALOGUE_LR_RESUME_MIGRATION_ROLLED_BACK"
DEFAULT_AUTH_REF = "ユーザー原文§3(2026-10-29 FZ-DIALOGUE-LR-ADOPTION-01): 藪の中c6を#1〜#3再実行なしでLR段階から正規再開"
STATE_RELPATH = "audit/dialogue_ctx_attempt_state.json"
LOCK_RELPATH = "audit/review_lock_state.json"
SLOWDOWN_WINDOW_MARGIN_BEFORE = 5.0
SLOWDOWN_WINDOW_MARGIN_AFTER = 15.0
SLOWDOWN_WINDOW_NO_NG_EPOCH = 900.0


class MigrationError(RuntimeError):
    pass


def _sha(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def _load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _atomic_write_json(path: str, obj) -> None:
    tmp = path + f".tmp{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, path)


def _file_sha(path: str):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _epoch_of(ts: str):
    try:
        return time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%S"))
    except (TypeError, ValueError):
        return None


def paths_of(run_dir: str, level: str, clip: str) -> dict:
    level_dir = f"{run_dir}/{level}"
    return {"level_dir": level_dir, "state": f"{level_dir}/{STATE_RELPATH}", "lock": f"{level_dir}/{LOCK_RELPATH}",
            "out_path": f"{level_dir}/narration/{clip}.wav", "plan": f"{run_dir}/segment_plan_{level}.json"}


def default_stop_scope(run_dir: str, scratch_json: str) -> int:
    """tools/stop_scope_check_01.py を実行して rc を返す(rc=3=STOP該当)。NOTICE本文を自分で解釈しない。"""
    cmd = [sys.executable, os.path.join(REPO, "tools", "stop_scope_check_01.py"), "--managed-id", MANAGEMENT_ID, "--run-dir", run_dir, "--out", scratch_json]
    return subprocess.run(cmd, cwd=REPO, env={**os.environ, "PYTHONUTF8": "1"}, capture_output=True, text=True).returncode


# ------------------------------------------------------------------------------------------ 転写の補完(M5)
def _history_events(history_path: str, clip: str):
    """attempt_history.jsonlから、clipを含む行だけを(行番号, dict)で返す(全行をJSON parseしない)。"""
    if not history_path or not os.path.exists(history_path):
        return
    with open(history_path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if clip not in line:
                continue
            try:
                yield i, json.loads(line)
            except ValueError:
                continue


def collect_ng_transcripts(state: dict, clip: str, level: str, theme_ids: list, history_path: str) -> dict:
    """戻り値 {"transcripts": [...], "warnings": [...], "errors": [...]}。各entryは出典(source_ref)付き。
    (1) stateのlog_rows由来: verified=False かつ ASR内容不一致NG(PASS系の統一判定でverified=Falseの反復検査のみNG・技術STOPは除外)の行
    (2) 減速後NG: 完了(verified=True)後に`final_ng_epoch`が付いたattemptについて、attempt_historyのA2_SLOWDOWN_REVERIFYを時刻窓+直前PROCEED(本文sha)で照合"""
    import er122_fz_ctx_policy_01 as pol
    sha = state["canonical_text_sha256"]
    out, warn, err = [], [], []
    for a in state.get("attempts") or []:
        for r in a.get("log_rows") or []:
            if not a.get("verified") and not a.get("technical_failure") and pol._is_content_ng_row(r):
                out.append({"n": a["n"], "source": "pre_slowdown", "asr_text": r["asr_text"], "classification": r.get("audio_classification"),
                            "canonical_text_sha256": sha, "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                            "source_ref": {"kind": "state.log_rows", "attempt_n": a["n"]}})
                break
    events = list(_history_events(history_path, clip))
    first_started = min((a.get("started_epoch") for a in state.get("attempts") or [] if a.get("started_epoch")), default=None)
    for a in state.get("attempts") or []:
        if not (a.get("verified") is True and a.get("final_ng_epoch")):
            continue
        lo = (a.get("finished_epoch") or a["started_epoch"]) - SLOWDOWN_WINDOW_MARGIN_BEFORE
        hi = a["final_ng_epoch"] + SLOWDOWN_WINDOW_MARGIN_AFTER
        cands = []
        for ln, e in events:
            if (e.get("action") != "A2_SLOWDOWN_REVERIFY" or e.get("segment_id") != clip or e.get("level") != level
                    or (theme_ids and e.get("theme_id") not in theme_ids) or e.get("status") == "OK" or not e.get("post_slowdown_asr_text")):
                continue
            ts = _epoch_of(e.get("timestamp"))
            if ts is None or not (lo <= ts <= hi):
                continue
            proceed = [p for _, p in events if p.get("action") == "PROCEED" and p.get("segment_id") == clip and p.get("level") == level
                       and (not theme_ids or p.get("theme_id") in theme_ids) and p.get("canonical_text_sha256") == sha
                       and _epoch_of(p.get("timestamp")) is not None and (first_started or 0) - SLOWDOWN_WINDOW_MARGIN_BEFORE <= _epoch_of(p["timestamp"]) <= ts]
            if proceed:
                cands.append((ln, e))
        if len(cands) == 1:
            ln, e = cands[0]
            out.append({"n": a["n"], "source": "post_slowdown", "asr_text": e["post_slowdown_asr_text"], "classification": e.get("post_slowdown_classification"),
                        "canonical_text_sha256": sha, "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "source_ref": {"kind": "attempt_history", "line": ln, "run_id": e.get("run_id"), "timestamp": e.get("timestamp"),
                                       "match": "segment+level+theme+time_window+PROCEED(sha)"}})
        elif len(cands) == 0:
            warn.append(f"attempt n={a['n']}: 減速後NGのA2_SLOWDOWN_REVERIFYイベントが見つからない(補完なし)")
        else:
            err.append(f"attempt n={a['n']}: 減速後NGの候補イベントが{len(cands)}件で曖昧(行 {[c[0] for c in cands]})。中止")
    return {"transcripts": out, "warnings": warn, "errors": err}


# ------------------------------------------------------------------------------------------ 計画(読取専用)
def _lock_entry(lock_path: str, clip: str):
    if not os.path.exists(lock_path):
        return None
    return (_load_json(lock_path) or {}).get(clip)


def build_plan(*, run_dir: str, level: str, clip: str, authorization_ref: str = DEFAULT_AUTH_REF, history_path: str | None = None,
               history_theme_ids: list | None = None, stop_scope_fn=None, verify_style: bool = True, scratch_dir: str | None = None) -> dict:
    """前提を全て検査して計画を返す(書込0・API 0)。plan["ok"]がFalseなら書込まない。"""
    import er011_human_review_lock_01 as review_lock
    history_path = history_path or review_lock.ATTEMPT_HISTORY_PATH
    P = paths_of(run_dir, level, clip)
    checks = []

    def chk(cid: str, ok: bool, detail: str = "", warn: bool = False):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail, **({"warn": True} if warn else {})})
        return ok

    plan = {"schema": "fz_dialogue_lr_resume_plan_v1", "management_id": MANAGEMENT_ID, "run_dir": run_dir, "level": level, "clip": clip,
            "authorization_ref": authorization_ref, "checks": checks, "ok": False, "migration": None, "partial": None}
    chk("C0_clip_explicit", bool(clip), "対象clipを--clipで明示(暗黙の複数clip適用なし)")
    # ---- STOP
    import tempfile
    sc = stop_scope_fn or (lambda rd: default_stop_scope(rd, os.path.join(scratch_dir or tempfile.gettempdir(), "_fzlr_stop_scope_check.json")))   # run dirには書かない
    try:
        rc = sc(run_dir)
    except Exception as e:      # noqa: BLE001  helperを実行できない=fail-closed
        rc = f"helper_error:{e}"
    chk("C1_stop_scope_check", rc == 0, f"rc={rc}(0=非停止、3=STOP該当。NOTICE本文は解釈しない)")
    if not os.path.exists(P["state"]):
        chk("C2_state_exists", False, P["state"])
        return plan
    store = _load_json(P["state"])
    st = (store.get("clips") or {}).get(clip)
    if not chk("C2_state_exists", st is not None, f"{P['state']}[{clip}]"):
        return plan
    mig = (st.get("lr") or {}).get("migration")
    if mig:
        plan["partial"] = {"migration_id": mig.get("id"), "steps_done": mig.get("steps_done"), "complete": bool(mig.get("complete"))}
        chk("C3_not_already_migrated", False, f"移行済み(id={mig.get('id')}, steps_done={mig.get('steps_done')}, complete={bool(mig.get('complete'))})")
        return plan
    atts = st.get("attempts") or []
    chk("C3_not_already_migrated", True, "migrationなし")
    chk("C4_terminal_ng_three_consumed", st.get("status") == "TERMINAL_NG" and int(st.get("n_started") or 0) == 3 and [a.get("n") for a in atts] == [1, 2, 3],
        f"status={st.get('status')} n_started={st.get('n_started')} attempts={[a.get('n') for a in atts]}")
    chk("C5_lr_unused_phase_b1", (st.get("phase") in (None, "B1")) and ((st.get("lr") or {}).get("state") in (None, "NOT_STARTED")) and not (st.get("lr") or {}).get("text"),
        f"phase={st.get('phase')} lr={(st.get('lr') or {}).get('state')}")
    chk("C6_policy_fz_ctx_v1", st.get("policy") == "fz_ctx_v1", f"policy={st.get('policy')}")
    chk("C7_attempts_counted_finished", all(a.get("counted") and a.get("finished") for a in atts), f"counted/finished={[(a.get('counted'), a.get('finished')) for a in atts]}")
    # ---- 本文sha
    plan_json = _load_json(P["plan"]) if os.path.exists(P["plan"]) else None
    clip_rec = next((c for c in (plan_json or {}).get("clips") or [] if c.get("id") == clip), None)
    text = clip_rec.get("text") if clip_rec else None
    chk("C8_text_sha_matches_plan", bool(text) and _sha(text) == st.get("canonical_text_sha256") == clip_rec.get("text_sha256"),
        f"state={str(st.get('canonical_text_sha256'))[:12]} plan={str((clip_rec or {}).get('text_sha256'))[:12]} sha(text)={_sha(text or '')[:12]}")
    # ---- Lock
    le = _lock_entry(P["lock"], clip)
    rows_total = sum(int(a.get("rows") or 0) for a in atts)
    chk("C9_lock_human_review_same_text", bool(le) and le.get("state") == "HUMAN_REVIEW_REQUIRED" and le.get("canonical_text_sha256") == st.get("canonical_text_sha256"),
        f"lock_state={(le or {}).get('state')} sha_match={(le or {}).get('canonical_text_sha256') == st.get('canonical_text_sha256')}")
    chk("C10_lock_cumulative_equals_consumed_rows", bool(le) and int(le.get("cumulative_tts_attempts") or -1) == rows_total,
        f"lock.cumulative_tts_attempts={(le or {}).get('cumulative_tts_attempts')} state rows={rows_total}")
    # ---- ctx style(読取専用: notesが新鮮なときだけ。LLMを呼ばない)
    if verify_style:
        ok, detail = _verify_style(run_dir, level, clip, plan_json, P, st)
        chk("C11_ctx_style_sha_matches_style_for", ok, detail)
    else:
        chk("C11_ctx_style_sha_matches_style_for", True, "skipped(--skip-style-verify)。再開時の_open()(M4a)が不一致を安全側停止で検出", warn=True)
    # ---- 転写
    theme_ids = list(dict.fromkeys([os.path.basename(run_dir.rstrip("/\\"))] + list(history_theme_ids or [])))
    col = collect_ng_transcripts(st, clip, level, theme_ids, history_path)
    chk("C12_history_match_unambiguous", not col["errors"], "; ".join(col["errors"]) or f"transcripts={len(col['transcripts'])}")
    for w in col["warnings"]:
        chk("C12w_history_note", True, w, warn=True)
    chk("C13_ng_transcripts_available", bool(col["transcripts"]), f"{len(col['transcripts'])}件(0件だと再開は即LR不可=TTS 0でHRになる)", warn=not col["transcripts"])
    bk = {k: P[k] + BACKUP_SUFFIX for k in ("state", "lock")}
    chk("C14_no_stale_backup", not any(os.path.exists(b) for b in bk.values()), f"{[b for b in bk.values() if os.path.exists(b)]}")
    plan["migration"] = {"transcripts": col["transcripts"], "backups": bk, "rows_total": rows_total,
                         "will_write": [P["state"], P["lock"], history_path], "text_sha256": st.get("canonical_text_sha256")}
    plan["ok"] = all(c["ok"] for c in checks)
    return plan


def _verify_style(run_dir, level, clip, plan_json, P, st):
    try:
        import er122_fz_ctx_notes_01 as notes
        if not plan_json:
            return False, "segment_planが読めない"
        story_key = notes.resolve_story_key(plan_json.get("story_key") or "")
        clips = [{"id": c["id"], "speaker": c["speaker"], "voice_role": c.get("voice_role") or ("narrator" if c["speaker"] == "narrator" else f"dialogue:{c['speaker']}"),
                  "text": c["text"], "part": c.get("part"), "voice": c.get("voice")} for c in plan_json["clips"]]
        prov = notes.NotesProvider(P["level_dir"], story_key, clips)
        if not os.path.exists(prov.path):
            return False, f"notes未生成({prov.path}): 検証にLLMが必要=中止"
        rec = _load_json(prov.path)
        if not prov._fresh_ok(rec):
            return False, "notesが古い/本文不一致(style_forがLLMを再callする状態)=中止"
        prov._rec = rec
        sty = prov.style_for(clip)
        ok = sty["style_sha256"] == st.get("ctx_style_sha256")
        return ok, f"state={str(st.get('ctx_style_sha256'))[:12]} style_for={sty['style_sha256'][:12]}"
    except Exception as e:      # noqa: BLE001
        return False, f"style検証不能: {type(e).__name__}: {e}"


# ------------------------------------------------------------------------------------------ 適用
def _backup(src: str, dst: str) -> None:
    if os.path.exists(dst):
        if _file_sha(dst) != _file_sha(src):
            raise MigrationError(f"退避先が既に存在し内容が異なります: {dst}")
        return
    shutil.copy2(src, dst)


def _restore(P: dict) -> list:
    done = []
    for k in ("state", "lock"):
        b = P[k] + BACKUP_SUFFIX
        if os.path.exists(b):
            shutil.copy2(b, P[k])
            done.append(P[k])
    return done


def apply_migration(plan: dict, *, history_path: str | None = None, fail_after: str | None = None) -> dict:
    """plan["ok"]のときだけ書く。順序 M7: 退避(state/Lock)→state→Lock→履歴。失敗時は両方復元(+rollback event)。fail_after=test用の故障注入('state'|'lock'|'history')。"""
    import er011_human_review_lock_01 as review_lock
    import er122_fz_ctx_policy_01 as pol
    if not plan.get("ok"):
        raise MigrationError("前提違反のため適用しません(書込0): " + "; ".join(c["id"] for c in plan["checks"] if not c["ok"]))
    run_dir, level, clip = plan["run_dir"], plan["level"], plan["clip"]
    history_path = history_path or review_lock.ATTEMPT_HISTORY_PATH
    P = paths_of(run_dir, level, clip)
    auth = plan["authorization_ref"]
    approved_by = f"user:{MANAGEMENT_ID} 原文§3"
    mig_id = f"fzlr-{int(time.time())}-{_sha(run_dir + clip)[:8]}"
    store = _load_json(P["state"])
    st = store["clips"][clip]
    plan_json = _load_json(P["plan"])
    text = next(c["text"] for c in plan_json["clips"] if c["id"] == clip)
    prev_hist_path = review_lock.ATTEMPT_HISTORY_PATH
    wrote = []
    try:
        for k in ("state", "lock"):
            _backup(P[k], P[k] + BACKUP_SUFFIX)
        # ---- step 1: state(v2へ。attempts/log_rows/cooldown/費用は不変。3試行は消費済みのまま)
        new = copy.deepcopy(st)
        new["status"] = "IN_PROGRESS"
        new["phase"] = pol.PHASE_LR
        new["ng_transcripts"] = plan["migration"]["transcripts"]
        new["cooldowns"] = dict(new.get("cooldowns") or {})
        if new.get("cooldown") and new["cooldown"].get("required_before_n") is not None:
            new["cooldowns"].setdefault(str(new["cooldown"]["required_before_n"]), new["cooldown"])
        new["lr"] = {"state": pol.LR_PENDING, "text": None, "text_sha": None, "migration": {
            "id": mig_id, "management_id": MANAGEMENT_ID, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "authorization_ref": auth,
            "from": {"status": st.get("status"), "n_started": st.get("n_started"), "schema": store.get("schema"), "phase": st.get("phase")},
            "consumed": {"n": int(st["n_started"]), "attempt_ns": [a["n"] for a in st["attempts"]], "rows": plan["migration"]["rows_total"],
                         "lock_cumulative_tts_attempts": plan["migration"]["rows_total"]},
            "approve_regenerate": {"approved_by": approved_by, "consumed_by_next_generation": True},
            "transcripts_sources": [t.get("source_ref") for t in plan["migration"]["transcripts"]],
            "steps_done": ["state"], "complete": False}}
        store["clips"][clip] = new
        store["schema"] = pol.STATE_SCHEMA
        _atomic_write_json(P["state"], store)
        wrote.append("state")
        if fail_after == "state":
            raise MigrationError("injected failure after state")
        # ---- step 2: Lock(既存のapprove_regenerate=ユーザーの明示指示の消費。迂回ではない)
        review_lock.ATTEMPT_HISTORY_PATH = history_path
        review_lock.approve_regenerate(P["out_path"], text, approved_by=approved_by)
        wrote.append("lock")
        new["lr"]["migration"]["steps_done"].append("lock")
        _atomic_write_json(P["state"], store)
        if fail_after == "lock":
            raise MigrationError("injected failure after lock")
        # ---- step 3: 履歴(append-only)
        ev = {"run_id": mig_id, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), "theme_id": os.path.basename(run_dir.rstrip("/\\")), "level": level,
              "segment_id": clip, "action": EVENT_NAME, "management_id": MANAGEMENT_ID, "authorization_ref": auth, "migration_id": mig_id,
              "consumed_attempts": int(st["n_started"]), "consumed_rows": plan["migration"]["rows_total"],
              "ng_transcripts": [{k: t[k] for k in ("n", "source", "source_ref")} for t in plan["migration"]["transcripts"]],
              "backups": plan["migration"]["backups"], "note": "n=1..3は消費済み(再実行しない)。LR段階から再開。approve_regenerateは次の生成で1回だけ消費される"}
        os.makedirs(os.path.dirname(history_path) or ".", exist_ok=True)
        with open(history_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(ev, ensure_ascii=False, default=str) + "\n")
        wrote.append("history")
        if fail_after == "history":
            raise MigrationError("injected failure after history")
        new["lr"]["migration"]["steps_done"].append("history")
        new["lr"]["migration"]["complete"] = True
        _atomic_write_json(P["state"], store)
        return {"ok": True, "migration_id": mig_id, "wrote": wrote, "backups": plan["migration"]["backups"]}
    except Exception as e:      # noqa: BLE001  失敗時は両方復元(M7)
        restored = _restore(P)
        try:
            os.makedirs(os.path.dirname(history_path) or ".", exist_ok=True)
            with open(history_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"run_id": mig_id, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), "segment_id": clip, "level": level, "action": ROLLBACK_EVENT,
                                    "migration_id": mig_id, "error": f"{type(e).__name__}: {e}", "wrote_before_failure": wrote, "restored": restored}, ensure_ascii=False) + "\n")
        except OSError:
            pass
        raise MigrationError(f"移行に失敗したため退避から復元しました(restored={restored}): {type(e).__name__}: {e}") from e
    finally:
        review_lock.ATTEMPT_HISTORY_PATH = prev_hist_path


def complete_partial(*, run_dir: str, level: str, clip: str, history_path: str | None = None) -> dict:
    """部分適用(state済み・Lock/履歴未了)を検知して残りを完了する。完全移行済みなら拒否。"""
    import er011_human_review_lock_01 as review_lock
    history_path = history_path or review_lock.ATTEMPT_HISTORY_PATH
    P = paths_of(run_dir, level, clip)
    store = _load_json(P["state"])
    st = (store.get("clips") or {}).get(clip) or {}
    mig = (st.get("lr") or {}).get("migration")
    if not mig:
        raise MigrationError("migrationが無い(部分適用ではない)")
    if mig.get("complete"):
        raise MigrationError("完全移行済みです(2回目のapplyは拒否)")
    approved_by = mig["approve_regenerate"]["approved_by"]
    plan_json = _load_json(P["plan"])
    text = next(c["text"] for c in plan_json["clips"] if c["id"] == clip)
    le = _lock_entry(P["lock"], clip) or {}
    prev = review_lock.ATTEMPT_HISTORY_PATH
    review_lock.ATTEMPT_HISTORY_PATH = history_path
    try:
        if "lock" not in mig["steps_done"]:
            if not (le.get("state") == "REGENERATE_APPROVED" and le.get("approved_by") == approved_by):
                review_lock.approve_regenerate(P["out_path"], text, approved_by=approved_by)
            mig["steps_done"].append("lock")
            _atomic_write_json(P["state"], store)
        if "history" not in mig["steps_done"]:
            ev = {"run_id": mig["id"], "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), "theme_id": os.path.basename(run_dir.rstrip("/\\")), "level": level,
                  "segment_id": clip, "action": EVENT_NAME, "management_id": MANAGEMENT_ID, "authorization_ref": mig["authorization_ref"], "migration_id": mig["id"],
                  "completed_after_partial": True}
            os.makedirs(os.path.dirname(history_path) or ".", exist_ok=True)
            with open(history_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(ev, ensure_ascii=False, default=str) + "\n")
            mig["steps_done"].append("history")
        mig["complete"] = True
        _atomic_write_json(P["state"], store)
    finally:
        review_lock.ATTEMPT_HISTORY_PATH = prev
    return {"ok": True, "completed": True, "migration_id": mig["id"]}


def restore_from_backup(*, run_dir: str, level: str, clip: str, history_path: str | None = None) -> dict:
    import er011_human_review_lock_01 as review_lock
    history_path = history_path or review_lock.ATTEMPT_HISTORY_PATH
    P = paths_of(run_dir, level, clip)
    if not all(os.path.exists(P[k] + BACKUP_SUFFIX) for k in ("state", "lock")):
        raise MigrationError("退避ファイルが揃っていません(復元不可)")
    restored = _restore(P)
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), "segment_id": clip, "level": level, "action": ROLLBACK_EVENT, "restored": restored,
                            "note": "operator --restore"}, ensure_ascii=False) + "\n")
    return {"ok": True, "restored": restored}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--level", default="b1b")
    ap.add_argument("--clip", required=True)
    ap.add_argument("--apply", action="store_true", help="書込む(既定=dry-run)")
    ap.add_argument("--restore", action="store_true", help="部分適用の復元(退避から両ファイルを戻す)")
    ap.add_argument("--authorization-ref", default=DEFAULT_AUTH_REF)
    ap.add_argument("--history-path", default=None)
    ap.add_argument("--history-theme-id", action="append", default=[], help="attempt_history照合に使う追加のtheme_id(複製run用: 元runの名前)")
    ap.add_argument("--skip-style-verify", action="store_true")
    ap.add_argument("--out-json", default=None)
    a = ap.parse_args(argv)
    run_dir = a.run_dir.replace("\\", "/").rstrip("/")
    if a.restore:
        res = restore_from_backup(run_dir=run_dir, level=a.level, clip=a.clip, history_path=a.history_path)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    plan = build_plan(run_dir=run_dir, level=a.level, clip=a.clip, authorization_ref=a.authorization_ref, history_path=a.history_path,
                      history_theme_ids=a.history_theme_id, verify_style=not a.skip_style_verify)
    out = {"mode": "apply" if a.apply else "dry-run", "plan": plan}
    rc = 0
    stop_check = next((c for c in plan["checks"] if c["id"] == "C1_stop_scope_check"), None)
    if plan.get("partial") and not plan["partial"]["complete"] and a.apply:
        out["result"] = complete_partial(run_dir=run_dir, level=a.level, clip=a.clip, history_path=a.history_path)
    elif a.apply:
        if not plan["ok"]:
            rc = 3 if (stop_check and not stop_check["ok"]) else 2
        else:
            try:
                out["result"] = apply_migration(plan, history_path=a.history_path)
            except MigrationError as e:
                out["result"] = {"ok": False, "error": str(e)}
                rc = 4
    else:
        rc = 0 if plan["ok"] else (3 if (stop_check and not stop_check["ok"]) else 2)
    text = json.dumps(out, ensure_ascii=False, indent=1, default=str)
    if a.out_json:
        os.makedirs(os.path.dirname(os.path.abspath(a.out_json)), exist_ok=True)
        with open(a.out_json, "w", encoding="utf-8") as f:
            f.write(text)
    print(text)
    return rc


if __name__ == "__main__":
    sys.exit(main())
