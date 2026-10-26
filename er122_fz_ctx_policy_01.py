# -*- coding: utf-8 -*-
"""FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02: Family Z dialogue の TTS attempt policy(ctx -> ctx -> 180秒cooldown -> 従来方式、総3回)。

ユーザー正式決定(APPROVED_FOR_PRODUCTION 2026-10-26)の中核。clip単位の単一policy objectと永続stateを、初回・retry・fallback・regeneration・resume・
中断後の再開・Human Review Lock の全経路が通る。決定者が1つなので経路間で方式がずれない。

- 総TTS試行(ループ反復)は初回を含め最大3回。3回目が従来方式Fallbackそのもので、4回目は存在しない。
- 1〜2回目=文脈・感情付きStyle(`style_prefix_override`=ctx style)。2回目NG後に180秒(er127.COOLDOWN_SECONDS、唯一の定義[TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02、
  2026-10-26ユーザー正式決定。旧600秒は2026-10-26に180秒へ変更]。実時間で数える。待機本体は er127.cooldown_core に委譲)。
  3回目=Style引数None(=現行の承認済み従来Dialogue Style。文脈・感情情報を一切渡さない)。
- 永続state(`<level_dir>/audit/dialogue_ctx_attempt_state.json`、tmp+os.replaceで原子書込)。**TTS呼出より前に** `n_started` を書く=TTS中に落ちても消費済み
  (3回超過は構造的に起きない)。再開は消費済みの試行を再実行せず、`n_started+1`から続ける。cooldownは前回の完了時刻からの実経過時間で数える。
- 二重計上の防止(Opus M-1): 各試行に `counted`(guarded呼出が戻り record_outcome 済み)の印。`carried_log()` は未計上行のみ返す。
- 再生成とresumeの判別(Opus M-4): 明示信号(`explicit_regenerate`[--only-clips対象]・Review Lockの`consuming_regenerate_approval`・本文/policy/ctx style不一致)だけが
  新規サイクル。`record_outcome`直後に結果dict+wav shaをDONE_OKとして保存し、明示信号なしでshaが一致すれば保存結果を採用する(API 0。確定直後〜checkpoint前の
  クラッシュで合格済みclipを作り直さない)。
- Local Rewrite: Z dialogueには未配線(既存仕様。EXISTING_SPEC_CHECK_01 §2)。本policyは新設しない。3回NG -> STOPPED -> record_outcome -> HUMAN_REVIEW_REQUIRED(Lock) -> STOP。
- 本moduleは er012_b / er003_n3 から import されない(hookはduck typing)。Production経路の既定はOFFではなく「新規run=fz_ctx_v1」だが、
  ロールバック=`Z_DIALOGUE_CTX_POLICY_DEFAULT = "legacy"` の1行。env/flag/起動script/.envではON/OFFしない。
"""
from __future__ import annotations

import hashlib
import json
import os
import time

MANAGEMENT_ID = "FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01"
POLICY_CTX = "fz_ctx_v1"
POLICY_LEGACY = "legacy"
Z_DIALOGUE_CTX_POLICY_DEFAULT = POLICY_CTX      # ロールバック: "legacy" に戻す1行(前例 A3_SECONDARY_LENGTH_REEVAL)。単一flag読取関数=resolve_run_policy
MAX_TOTAL_ATTEMPTS = 3
CTX_ATTEMPTS = 2
STATE_SCHEMA = "fz_dialogue_ctx_attempt_state_v1"
STATE_RELPATH = "audit/dialogue_ctx_attempt_state.json"
POLICY_RELPATH = "audit/dialogue_tts_policy.json"      # run_dir相対(run単位。levelをまたいで方式が混在しない: Opus R-2)
POLICY_SCHEMA = "fz_dialogue_tts_policy_v1"
SLICE_SECONDS = 5.0
RUN_STATE_FILENAMES = ("tts_generation_results.json", "tts_checkpoint.json", "review_lock_state.json", "human_approved_segments.json")


def cooldown_seconds() -> float:
    """固定180秒(ユーザー正式決定2026-10-26。旧600秒)。唯一の定義 er127_tts_block_policy_01.COOLDOWN_SECONDS を参照する(複製しない)。"""
    import er127_tts_block_policy_01 as er127
    return float(er127.COOLDOWN_SECONDS)


class _Runtime:
    """時間の注入点(test/driver用。既定=実時間)。cooldownは実時間の経過で数える。"""
    clock = staticmethod(time.time)
    sleep = staticmethod(time.sleep)


RUNTIME = _Runtime()


def now_iso(epoch: float | None = None) -> str:
    t = RUNTIME.clock() if epoch is None else epoch
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t))


def _sha256_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()


def _sha256_file(path: str):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _jsonable(obj):
    return json.loads(json.dumps(obj, ensure_ascii=False, default=str))


def _atomic_write_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, path)


def _stop_type():
    import er063_family_z_audio_01 as z
    return z.FamilyZDialogueCtxStop


# ============================================================
# run単位のpolicy固定(単一flag読取関数)
# ============================================================
def resolve_run_policy(run_dir: str, *, write: bool = True) -> dict:
    """run単位のdialogue TTS policyを返す(Opus R-2)。固定ファイルがあればそれ(キー無し=legacy扱いの規則を含む)、無ければ:
    既に結果/checkpoint等のrun stateがあるrun(旧方式で生成済み・公開済みを含む)=legacy(方式混在を防ぐ)、新規run=コード既定(Z_DIALOGUE_CTX_POLICY_DEFAULT)。
    決定は run_dir/audit/dialogue_tts_policy.json へ原子的に保存し、以後は読むだけ。LLM・API呼出なし。"""
    p = f"{run_dir}/{POLICY_RELPATH}"
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            rec = json.load(f)
        if rec.get("policy") in (POLICY_CTX, POLICY_LEGACY):
            return rec
    legacy_evidence = [f"{run_dir}/{lv}/audit/{n}" for lv in ("a2", "b1b") for n in RUN_STATE_FILENAMES
                       if os.path.exists(f"{run_dir}/{lv}/audit/{n}")]
    if legacy_evidence:
        policy, reason = POLICY_LEGACY, "既存のrun state(旧方式で生成済み)があるため方式混在を避けlegacyで固定"
    else:
        policy, reason = Z_DIALOGUE_CTX_POLICY_DEFAULT, "新規run: コード既定"
    rec = {"schema": POLICY_SCHEMA, "management_id": MANAGEMENT_ID, "policy": policy, "reason": reason, "code_default": Z_DIALOGUE_CTX_POLICY_DEFAULT,
           "legacy_evidence": legacy_evidence, "decided_at": now_iso()}
    if write:
        _atomic_write_json(p, rec)
    return rec


# ============================================================
# 永続state
# ============================================================
class StateStore:
    def __init__(self, level_dir: str):
        self.path = f"{level_dir}/{STATE_RELPATH}"

    def load_all(self) -> dict:
        if not os.path.exists(self.path):
            return {"schema": STATE_SCHEMA, "clips": {}}
        try:
            with open(self.path, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            # 壊れたstateは握りつぶさず退避して技術STOP(消費済み試行を忘れて4回目以降を回さない)
            try:
                os.replace(self.path, self.path + ".corrupt")
            except OSError:
                pass
            raise _stop_type()(f"[STOP][Z-DIALOGUE-CTX-STATE] attempt stateが読めません({self.path})。消費済み試行を確認できないため課金前にSTOPしました"
                               "(.corruptへ退避済み。Fable/担当者の確認が必要)。")
        d.setdefault("clips", {})
        return d

    def get(self, clip_id: str):
        return self.load_all()["clips"].get(clip_id)

    def put(self, clip_id: str, clip_state: dict) -> None:
        d = self.load_all()
        clip_state["updated_at"] = now_iso()
        d["clips"][clip_id] = clip_state
        d["schema"] = STATE_SCHEMA
        _atomic_write_json(self.path, d)


# ============================================================
# policy object
# ============================================================
class DialogueAttemptPolicy:
    """clip単位。dialogue()内で1個作り、Std(単一呼出)/Adv(外側ループの各pass)で共有する。"""

    def __init__(self, level_dir: str, clip_id: str, canonical_text: str, ctx_style: str, ctx_style_sha256: str, *, out_path: str,
                 stop_check, explicit_regenerate: bool = False, consuming_regenerate_approval: bool = False, policy_id: str = POLICY_CTX,
                 meta: dict | None = None):
        self.store = StateStore(level_dir)
        self.level_dir = level_dir
        self.clip_id = clip_id
        self.out_path = out_path
        self.ctx_style = ctx_style
        self.ctx_style_sha256 = ctx_style_sha256
        self.canonical_text_sha256 = _sha256_text(canonical_text)
        self.policy_id = policy_id
        self.stop_check = stop_check
        self.meta = dict(meta or {})
        self.explicit_regenerate = bool(explicit_regenerate)
        self.consuming_regenerate_approval = bool(consuming_regenerate_approval)
        self._carried_done = False
        self._saved_result = None
        self.decision = None
        self.st = self._open()
        self.prior_counted_rows = sum(int(a.get("rows") or 0) for a in self.st["attempts"] if a.get("counted"))
        self.n_started_at_open = self.st["n_started"]
        self.restored_from_process_state = bool(self.st["n_started"] > 0 and self.st["status"] == "IN_PROGRESS")

    # ---- 開始判定(新規サイクル / 続行 / 保存結果の採用) ----
    def _new_state(self, history: list) -> dict:
        return {"clip_id": self.clip_id, "canonical_text_sha256": self.canonical_text_sha256, "policy": self.policy_id,
                "ctx_style_sha256": self.ctx_style_sha256, "status": "IN_PROGRESS", "n_started": 0, "attempts": [], "cooldown": None,
                "done": None, "history": history, "created_at": now_iso(), "cycle": len(history) + 1}

    def _open(self) -> dict:
        ex = self.store.get(self.clip_id)
        if ex is None:
            self.decision = "new:no_state"
            st = self._new_state([])
            self.store.put(self.clip_id, st)
            return st
        same = (ex.get("canonical_text_sha256") == self.canonical_text_sha256 and ex.get("policy") == self.policy_id
                and ex.get("ctx_style_sha256") == self.ctx_style_sha256)
        if not same:
            return self._restart(ex, "state_mismatch(本文/policy/ctx styleが前回と異なる)")
        status = ex.get("status")
        if status == "IN_PROGRESS":
            # 中断後の再開: 消費済み試行は再実行しない。--only-clips等の明示信号が付いていても続行(同一サイクルの再開は新規生成ではない)
            self.decision = f"resume:n_started={ex.get('n_started')}"
            return ex
        if self.explicit_regenerate or self.consuming_regenerate_approval:
            return self._restart(ex, "explicit_regenerate" if self.explicit_regenerate else "consuming_regenerate_approval")
        if status == "DONE_OK":
            done = ex.get("done") or {}
            if done.get("result") and done.get("wav_sha256") and _sha256_file(self.out_path) == done["wav_sha256"]:
                self.decision = "adopt_saved_done_ok"
                self._saved_result = done["result"]
                return ex
            return self._restart(ex, "done_ok_but_saved_wav_missing_or_changed")
        # TERMINAL_NG・明示信号なし: 3回消費済み。remaining()=0のまま(API 0。Review Lockが先にblockする)
        self.decision = "terminal_ng:attempts_exhausted"
        return ex

    def _restart(self, ex: dict, reason: str) -> dict:
        hist = list(ex.get("history") or [])
        hist.append({"ended_status": ex.get("status"), "n_started": ex.get("n_started"), "reason_for_restart": reason, "restarted_at": now_iso(),
                     "cycle": ex.get("cycle"), "prev_canonical_text_sha256": ex.get("canonical_text_sha256"),
                     "prev_ctx_style_sha256": ex.get("ctx_style_sha256"), "prev_policy": ex.get("policy")})
        self.decision = f"new:{reason}"
        st = self._new_state(hist)
        self.store.put(self.clip_id, st)
        return st

    # ---- 状態参照 ----
    def saved_result(self):
        """DONE_OK保存結果の採用(API 0)。無ければNone。"""
        if self._saved_result is None:
            return None
        r = json.loads(json.dumps(self._saved_result))
        dt = dict(r.get("dialogue_tts") or {})
        dt["adopted_saved_result"] = True
        dt["decision"] = self.decision
        r["dialogue_tts"] = dt
        return r

    def remaining(self) -> int:
        if self.st["status"] != "IN_PROGRESS":
            return 0
        return max(0, MAX_TOTAL_ATTEMPTS - int(self.st["n_started"]))

    @property
    def n_started(self) -> int:
        return int(self.st["n_started"])

    def prior_generations(self) -> int:
        """Adv外側ループへ渡す『前プロセスで計上済み』の生成行数(Opus M-1)。"""
        return int(self.prior_counted_rows)

    def carried_log(self) -> list:
        """前プロセスで完了済み・未計上の試行行(1回だけ返す。同一プロセス内の前passは含めない=二重計上防止)。"""
        if self._carried_done:
            return []
        self._carried_done = True
        rows = []
        for a in self.st["attempts"]:
            if a.get("finished") and not a.get("counted"):
                rows.extend(json.loads(json.dumps(a.get("log_rows") or [])))
        return rows

    def mark_counted(self) -> None:
        """guarded呼出が戻った(record_outcome済み)直後に呼ぶ。終了済み試行を計上済みにする。"""
        changed = False
        for a in self.st["attempts"]:
            if a.get("finished") and not a.get("counted"):
                a["counted"] = True
                changed = True
        if changed:
            self.store.put(self.clip_id, self.st)

    def note_final_ng(self) -> None:
        """Adv: 直前passの採否が減速後検証でNGと確定した時刻の記録(cooldownの起点をNG確定時刻に寄せる。採否の判定そのものは変えない)。"""
        for a in reversed(self.st["attempts"]):
            if a.get("finished"):
                a["final_ng_epoch"] = RUNTIME.clock()
                break
        self.store.put(self.clip_id, self.st)

    # ---- hook(er012_b.generate_voice_body_wide_margin が呼ぶ) ----
    def before_attempt(self, attempt: int, max_attempts: int, out_path: str) -> dict:
        st = self.st
        n = int(st["n_started"]) + 1
        if st["status"] != "IN_PROGRESS" or n > MAX_TOTAL_ATTEMPTS:
            return {"stop": True, "reason": "ATTEMPT_BUDGET_EXHAUSTED(総試行3回を使い切り。4回目は存在しない)"}
        self.stop_check(f"tts_attempt:{self.clip_id}:n{n}")
        if n == MAX_TOTAL_ATTEMPTS:
            self._cooldown_before_fallback(n)
        mode = "ctx" if n <= CTX_ATTEMPTS else "legacy_fallback"
        st["n_started"] = n
        st["attempts"].append({"n": n, "mode": mode, "started_epoch": RUNTIME.clock(), "started_at": now_iso(), "finished": False, "verified": None,
                               "counted": False, "rows": 0})
        self.store.put(self.clip_id, st)     # TTS呼出より前に書く(TTS中に落ちても消費済み)
        self._cur = st["attempts"][-1]
        return {"stop": False, "style_prefix_override": (self.ctx_style if mode == "ctx" else None), "n": n, "mode": mode}

    def _cooldown_before_fallback(self, n: int) -> None:
        """2回目NG後の固定180秒(旧600秒)。起点=直前試行の最終NG確定時刻(無ければ完了時刻、完了前に落ちていれば開始時刻)。実時間で数える(再開しても180秒未満にならない)。"""
        st = self.st
        prev = st["attempts"][-1] if st["attempts"] else None
        ref = None
        if prev:
            ref = prev.get("final_ng_epoch") or prev.get("finished_epoch") or prev.get("started_epoch")
        if ref is None:
            return
        total = cooldown_seconds()
        cd = st.get("cooldown") or {}
        if cd.get("required_before_n") != n or cd.get("ref_epoch") != ref:
            cd = {"required_before_n": n, "ref_epoch": ref, "ref_at": now_iso(ref), "requested_seconds": total, "started_epoch": RUNTIME.clock(),
                  "started_at": now_iso(), "ended_epoch": None, "waited_seconds_this_process": 0.0, "resumed": False, "process_starts": 1}
        else:
            cd["resumed"] = True
            cd["process_starts"] = int(cd.get("process_starts", 1)) + 1
        st["cooldown"] = cd
        self.store.put(self.clip_id, st)
        t0 = RUNTIME.clock()
        # 待機本体は er127.cooldown_core(唯一の実装。5秒刻みでSTOP確認、STOP時は例外で即中断。stateは起点を保持=後でresume可)。
        # clock/sleepは本moduleのRUNTIME(test/driver注入点)を明示的に渡す。
        import er127_tts_block_policy_01 as er127
        er127.cooldown_core(ref_epoch=ref, seconds=total, stop_check=self.stop_check, label=self.clip_id, clock=RUNTIME.clock,
                            sleep=RUNTIME.sleep, slice_seconds=SLICE_SECONDS, resumed=bool(cd.get("resumed")))
        end = RUNTIME.clock()
        cd["ended_epoch"] = end
        cd["ended_at"] = now_iso(end)
        cd["waited_seconds_this_process"] = round(end - t0, 3)
        cd["total_elapsed_since_ref_seconds"] = round(end - ref, 3)     # 再開時でも前回NGからの総経過秒(Opus 1(f))
        st["cooldown"] = cd
        self.store.put(self.clip_id, st)
        try:
            import er011_human_review_lock_01 as review_lock
            review_lock.append_attempt_history_event(self.out_path, "CTX_COOLDOWN_BEFORE_FALLBACK", {
                "clip_id": self.clip_id, "attempt_before_cooldown": n - 1, "attempt_after_cooldown": n, "requested_seconds": total,
                "waited_seconds_this_process": cd["waited_seconds_this_process"], "total_elapsed_since_ref_seconds": cd["total_elapsed_since_ref_seconds"],
                "resumed": cd["resumed"]})
        except Exception:
            pass

    def final_reason(self, max_attempts: int) -> str:
        return (f"文脈・感情付きTTS方式の通算{self.n_started}回の試行(上限{MAX_TOTAL_ATTEMPTS}回、1〜2回目=文脈・感情付き、3回目=従来方式)でもASR検証に合格しませんでした"
                f"(この呼出のmax_attempts={max_attempts})")

    def attempt_metadata(self) -> dict:
        a = getattr(self, "_cur", None) or {}
        return {"tts_mode": a.get("mode"), "overall_attempt_n": a.get("n"), "dialogue_tts_policy": self.policy_id}

    def after_attempt(self, attempt: int, rows: list, verified: bool, instruction_type: str, technical_failure: bool = False) -> None:
        a = self._cur
        mode = a["mode"]
        from_min = False
        for r in rows:
            if not isinstance(r, dict):
                continue
            r["tts_mode"] = mode
            r["overall_attempt_n"] = a["n"]
            r["dialogue_tts_policy"] = self.policy_id
            if r.get("instruction_type") == "minimal_fallback":
                from_min = True
                r["tts_mode_effective"] = f"minimal_fallback_in_{'ctx' if mode == 'ctx' else 'legacy'}_attempt"
            elif mode == "ctx":
                import er011_human_review_lock_01 as review_lock
                r["style_prefix"] = review_lock.style_prefix_record(self.ctx_style)
        a["finished"] = True
        a["finished_epoch"] = RUNTIME.clock()
        a["finished_at"] = now_iso()
        a["verified"] = bool(verified)
        a["rows"] = len(rows)
        a["technical_failure"] = bool(technical_failure)
        a["instruction_type"] = instruction_type
        a["effective_mode"] = (f"minimal_fallback_in_{'ctx' if mode == 'ctx' else 'legacy'}_attempt" if (from_min or instruction_type == "minimal_fallback") else mode)
        a["log_rows"] = _jsonable(rows)
        self.store.put(self.clip_id, self.st)

    # ---- 結果確定(dialogue()から) ----
    def evidence(self, extra: dict | None = None) -> dict:
        st = self.st
        last = st["attempts"][-1] if st["attempts"] else {}
        mode = last.get("mode")
        eff = last.get("effective_mode")
        d = {"policy": self.policy_id, "final_mode": eff or mode, "final_attempt_n": last.get("n"), "n_started": st["n_started"],
             "decision": self.decision, "resumed_from_process_state": self.restored_from_process_state, "n_started_at_open": self.n_started_at_open,
             "ctx_style_sha256": self.ctx_style_sha256, "attempts": [{k: a.get(k) for k in ("n", "mode", "effective_mode", "verified", "started_at", "finished_at", "rows",
                                                                                         "technical_failure", "counted")} for a in st["attempts"]],
             "cooldown": st.get("cooldown"), "cycle": st.get("cycle"), "history": st.get("history") or []}
        if extra:
            d.update(extra)
        return d

    def finish(self, result: dict) -> dict:
        """採用はfinish()のみで確定する(Opus R-2)。status OK -> DONE_OK(結果dict+wav shaを保存)。非OK -> 実際に試行した結果ならTERMINAL_NG。
        Review Lockのblock結果(HUMAN_REVIEW_LOCKED、試行0)ではstateを変えない。"""
        if not isinstance(result, dict):
            return result
        status = result.get("status")
        if status == "HUMAN_REVIEW_LOCKED":
            return result
        if status == "OK":
            self.st["status"] = "DONE_OK"
            self.st["done"] = {"result": _jsonable(result), "wav_sha256": _sha256_file(self.out_path),
                               "saved_at": now_iso(), "final_mode": (self.st["attempts"][-1].get("effective_mode") if self.st["attempts"] else None)}
        elif self.st["n_started"] > self.n_started_at_open or self.st["n_started"] >= MAX_TOTAL_ATTEMPTS:
            self.st["status"] = "TERMINAL_NG"
        self.store.put(self.clip_id, self.st)
        return result
