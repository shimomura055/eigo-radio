# -*- coding: utf-8 -*-
"""FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01 委任_02: Family Z dialogue の TTS attempt policy(ctx -> ctx -> 180秒cooldown -> 従来方式 -> LR -> ctx -> ctx -> 180秒 -> 従来方式、総6回)。

FZ-DIALOGUE-LR-ADOPTION-01(APPROVED_FOR_PRODUCTION 2026-10-29): ZセリフにもLRを正式導入し、最大TTS6回・LR1回・待機2回へ拡張した(state v2)。
  phase B1(①②ctx→180秒→③従来) → 非OKなら phase LR(LR LLMは最大1回) → 書換え本文保存で phase B2(①'②'ctx→180秒→③'従来) → 非OKは終端(Human Review)。
  決定者は本policyの1つのまま。B1/B2の区切りはProfile(er127.PROFILES["Z_DLG_CTX"].block_attempts)から取る。LR呼出契約(er127.lr_recoverのblk)は
  ZLrBlockAdapterがこのstateを唯一の永続先として満たす(BlockProgressの別ファイルを併用しない)。v1のTERMINAL_NG(3回消費済み)は自動ではLRへ進まない
  (移行はtools/fz_dialogue_lr_resume_01.pyだけ)。

ユーザー正式決定(APPROVED_FOR_PRODUCTION 2026-10-26)の中核。clip単位の単一policy objectと永続stateを、初回・retry・fallback・regeneration・resume・
中断後の再開・Human Review Lock の全経路が通る。決定者が1つなので経路間で方式がずれない。

- 総TTS試行(ループ反復)は初回を含め最大6回(ブロック内3回×2)。各ブロックの3回目が従来方式Fallbackで、7回目は存在しない。
- 1〜2回目=文脈・感情付きStyle(`style_prefix_override`=ctx style)。2回目NG後に180秒(er127.COOLDOWN_SECONDS、唯一の定義[TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02、
  2026-10-26ユーザー正式決定。旧600秒は2026-10-26に180秒へ変更]。実時間で数える。待機本体は er127.cooldown_core に委譲)。
  3回目=Style引数None(=現行の承認済み従来Dialogue Style。文脈・感情情報を一切渡さない)。
- 永続state(`<level_dir>/audit/dialogue_ctx_attempt_state.json`、tmp+os.replaceで原子書込)。**TTS呼出より前に** `n_started` を書く=TTS中に落ちても消費済み
  (3回超過は構造的に起きない)。再開は消費済みの試行を再実行せず、`n_started+1`から続ける。cooldownは前回の完了時刻からの実経過時間で数える。
- 二重計上の防止(Opus M-1): 各試行に `counted`(guarded呼出が戻り record_outcome 済み)の印。`carried_log()` は未計上行のみ返す。
- 再生成とresumeの判別(Opus M-4): 明示信号(`explicit_regenerate`[--only-clips対象]・Review Lockの`consuming_regenerate_approval`・本文/policy/ctx style不一致)だけが
  新規サイクル。`record_outcome`直後に結果dict+wav shaをDONE_OKとして保存し、明示信号なしでshaが一致すれば保存結果を採用する(API 0。確定直後〜checkpoint前の
  クラッシュで合格済みclipを作り直さない)。
- Local Rewrite: 2026-10-29以降は配線済み(上記)。LR不可(NO_NG_SPAN・入力転写全滅・候補全滅)・LR後の最終NGは STOPPED -> record_outcome -> HUMAN_REVIEW_REQUIRED(Lock) -> STOP。
  (2026-10-26〜10-29の「Z dialogueにLocal Rewriteは未配線/追加しない」は履歴。UDR-TRA-1はsupersede)
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
LR_MANAGEMENT_ID = "FZ-DIALOGUE-LR-ADOPTION-01"
MAX_TOTAL_ATTEMPTS = 6
CTX_ATTEMPTS = 2                 # ブロック内の文脈・感情付き試行数(①②)。③はブロックの最後(Profile.cooldown_before)
PHASE_B1, PHASE_LR, PHASE_B2 = "B1", "LR", "B2"
LR_NOT_STARTED, LR_PENDING, LR_TEXT_SAVED, LR_RESOLVED, LR_UNRESOLVED, LR_NOT_APPLICABLE = (
    "NOT_STARTED", "PENDING", "TEXT_SAVED", "RESOLVED", "UNRESOLVED", "NOT_APPLICABLE")
LR_TERMINAL_STATES = (LR_UNRESOLVED, LR_NOT_APPLICABLE)       # LR終了(成功以外)=clipは終端化する(再実行でLR LLMを再び回さない、M4(b))
STATE_SCHEMA_V1 = "fz_dialogue_ctx_attempt_state_v1"
STATE_SCHEMA = "fz_dialogue_ctx_attempt_state_v2"
STATE_RELPATH = "audit/dialogue_ctx_attempt_state.json"
POLICY_RELPATH = "audit/dialogue_tts_policy.json"      # run_dir相対(run単位。levelをまたいで方式が混在しない: Opus R-2)
POLICY_SCHEMA = "fz_dialogue_tts_policy_v1"
SLICE_SECONDS = 5.0
RUN_STATE_FILENAMES = ("tts_generation_results.json", "tts_checkpoint.json", "review_lock_state.json", "human_approved_segments.json")


def cooldown_seconds() -> float:
    """固定180秒(ユーザー正式決定2026-10-26。旧600秒)。唯一の定義 er127_tts_block_policy_01.COOLDOWN_SECONDS を参照する(複製しない)。"""
    import er127_tts_block_policy_01 as er127
    return float(er127.COOLDOWN_SECONDS)


def _profile():
    import er127_tts_block_policy_01 as er127
    return er127.PROFILES["Z_DLG_CTX"]


def block_attempts() -> int:
    """1ブロックのTTS回数(=3)。数値を複製せずProfileから取る(O7: 『通算n = ordinal + ブロック長*depth』のブロック長もここ)。"""
    return int(_profile().block_attempts)


def lr_enabled() -> bool:
    """Z_DLG_CTXのLR可否はProfile(星取表)だけが決める(flag・envなし)。"""
    return bool(_profile().lr)


def _is_content_ng_row(row: dict) -> bool:
    """attempt行が『ASR内容不一致NG』か(M5)。PASS系の統一判定でverified=Falseの行(反復検査・disfluency単独NG)・技術STOP・ASR未取得の行は含めない。"""
    if not isinstance(row, dict) or row.get("status") != "OK" or row.get("verified") is not False or not row.get("asr_text"):
        return False
    import er078_asr_unified_judge_01 as uj
    state = (row.get("asr_judgement") or {}).get("state")
    if state is None:
        return str(row.get("audio_classification") or "") not in ("EXACT_MATCH", "NORMALIZED_MATCH")
    return state not in uj.PASSING_STATES and state not in uj.TECHNICAL_STOP_STATES


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
        if d.get("schema") not in (None, STATE_SCHEMA, STATE_SCHEMA_V1):
            raise _stop_type()(f"[STOP][Z-DIALOGUE-CTX-STATE] attempt stateのschemaが未知です({d.get('schema')!r}, {self.path})。課金前にSTOPしました。")
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
    """clip単位。dialogue()内で1個作り、Std(単一呼出)/Adv(外側ループの各pass)で共有する。B1/LR/B2の3 phaseを持つ(FZ-DIALOGUE-LR-ADOPTION-01)。"""

    def __init__(self, level_dir: str, clip_id: str, canonical_text: str, ctx_style: str, ctx_style_sha256: str, *, out_path: str,
                 stop_check, explicit_regenerate: bool = False, consuming_regenerate_approval: bool = False, policy_id: str = POLICY_CTX,
                 meta: dict | None = None):
        self.store = StateStore(level_dir)
        self.level_dir = level_dir
        self.clip_id = clip_id
        self.out_path = out_path
        self.ctx_style = ctx_style
        self.ctx_style_sha256 = ctx_style_sha256
        self.canonical_text = canonical_text                # 元原稿(LR block内でもLock key/M1 anchorは元原稿)
        self.canonical_text_sha256 = _sha256_text(canonical_text)
        self.policy_id = policy_id
        self.stop_check = stop_check
        self.meta = dict(meta or {})
        self.explicit_regenerate = bool(explicit_regenerate)
        self.consuming_regenerate_approval = bool(consuming_regenerate_approval)
        self._carried_done = False
        self._saved_result = None
        self.decision = None
        self.st = self._normalize(self._open())
        self.prior_counted_rows = sum(int(a.get("rows") or 0) for a in self.st["attempts"] if a.get("counted"))
        self.n_started_at_open = self.st["n_started"]
        self.restored_from_process_state = bool(self.st["n_started"] > 0 and self.st["status"] == "IN_PROGRESS")

    # ---- state v2 の既定値(v1は読み取り時に補う。v1のphaseは常にB1=TERMINAL_NG(n=3)を自動ではLRへ進めない) ----
    @staticmethod
    def _normalize(st: dict) -> dict:
        st.setdefault("phase", PHASE_B1)
        st.setdefault("lr", {"state": LR_NOT_STARTED, "text": None, "text_sha": None})
        st.setdefault("ng_transcripts", [])
        st.setdefault("cooldowns", {})
        cd = st.get("cooldown")
        if cd and cd.get("required_before_n") is not None:
            st["cooldowns"].setdefault(str(cd["required_before_n"]), cd)
        return st

    # ---- 開始判定(新規サイクル / 続行 / 保存結果の採用) ----
    def _new_state(self, history: list) -> dict:
        return {"clip_id": self.clip_id, "canonical_text_sha256": self.canonical_text_sha256, "policy": self.policy_id,
                "ctx_style_sha256": self.ctx_style_sha256, "status": "IN_PROGRESS", "n_started": 0, "attempts": [], "cooldown": None,
                "done": None, "history": history, "created_at": now_iso(), "cycle": len(history) + 1,
                "phase": PHASE_B1, "lr": {"state": LR_NOT_STARTED, "text": None, "text_sha": None}, "ng_transcripts": [], "cooldowns": {}}

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
            if ex.get("status") == "IN_PROGRESS" and ex.get("phase") in (PHASE_LR, PHASE_B2):
                # M4(a): LR phase以降(LR LLM消費済み/書換え本文保存済み)の進行中サイクルは、本文/policy/ctx styleの同一性が崩れても_restartで
                # n=0から作り直さない(LR・TTSの二重消費になる)。安全側で停止し、人が判断する。stateは書き換えない。
                raise _stop_type()(
                    f"[STOP][Z-DIALOGUE-CTX-LR-STATE] {self.clip_id}: LR phase({ex.get('phase')})の進行中stateと本文/policy/ctx styleの同一性が一致しません"
                    f"(本文sha {str(ex.get('canonical_text_sha256'))[:12]}→{self.canonical_text_sha256[:12]}、ctx style {str(ex.get('ctx_style_sha256'))[:12]}→"
                    f"{self.ctx_style_sha256[:12]})。消費済みLR/TTSを忘れて作り直さないため課金前にSTOPしました(stateは変更していません。Fable/担当者の確認が必要)。")
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
        # TERMINAL_NG・明示信号なし: 全試行消費済み(または終端)。remaining()=0のまま(API 0。Review Lockが先にblockする)
        self.decision = "terminal_ng:attempts_exhausted"
        return ex

    def _restart(self, ex: dict, reason: str) -> dict:
        hist = list(ex.get("history") or [])
        hist.append({"ended_status": ex.get("status"), "n_started": ex.get("n_started"), "reason_for_restart": reason, "restarted_at": now_iso(),
                     "cycle": ex.get("cycle"), "prev_canonical_text_sha256": ex.get("canonical_text_sha256"),
                     "prev_ctx_style_sha256": ex.get("ctx_style_sha256"), "prev_policy": ex.get("policy"),
                     "ended_phase": ex.get("phase"), "ended_lr_state": (ex.get("lr") or {}).get("state")})
        self.decision = f"new:{reason}"
        st = self._new_state(hist)
        self.store.put(self.clip_id, st)
        return st

    # ---- 状態参照 ----
    @property
    def phase(self) -> str:
        return self.st.get("phase") or PHASE_B1

    @property
    def lr(self) -> dict:
        return self.st["lr"]

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

    def block_end(self) -> int:
        """現phaseで許される通算nの上限(B1=ブロック長、B2=2×ブロック長、LRはTTSなし=現在値)。"""
        L = block_attempts()
        return {PHASE_B1: L, PHASE_B2: 2 * L}.get(self.phase, int(self.st["n_started"]))

    def remaining(self) -> int:
        if self.st["status"] != "IN_PROGRESS":
            return 0
        return max(0, self.block_end() - int(self.st["n_started"]))

    @property
    def n_started(self) -> int:
        return int(self.st["n_started"])

    def b1_exhausted(self) -> bool:
        """元ブロック(B1)の試行を使い切って(再開時)いるか。True なら B1 leaf を再び呼ばずLR段へ進む。"""
        return self.phase == PHASE_B1 and self.n_started >= block_attempts()

    def prior_generations(self) -> int:
        """Adv外側ループへ渡す『前プロセスで計上済み』の生成行数(Opus M-1)。現在のブロックに属する分(ブロック相対)。"""
        L = block_attempts()
        depth = 1 if self.phase == PHASE_B2 else 0
        lo, hi = depth * L, (depth + 1) * L
        return int(sum(int(a.get("rows") or 0) for a in self.st["attempts"] if a.get("counted") and lo < int(a.get("n") or 0) <= hi))

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
        """record_outcome(外側guard)が済んだ直後に呼ぶ。終了済み試行を計上済みにする。"""
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

    def note_post_slowdown_ng(self, n: int, asr_text: str | None, classification: str | None = None) -> None:
        """Adv: 通算attempt nの減速後再検証がNGだったときの転写(LR入力候補、M5)。同一attempt内では減速後転写を優先して走査する。"""
        if not asr_text:
            return
        ent = {"n": int(n), "source": "post_slowdown", "asr_text": asr_text, "classification": classification,
               "canonical_text_sha256": self.canonical_text_sha256, "recorded_at": now_iso()}
        lst = self.st["ng_transcripts"]
        if not any(e.get("n") == ent["n"] and e.get("source") == "post_slowdown" for e in lst):
            lst.append(ent)
            self.store.put(self.clip_id, self.st)

    def last_attempt_row(self) -> dict | None:
        """HRQ登録用の『最後に実行されたattemptの最後のlog行』(再開時にleaf結果が無いとき用)。"""
        for a in reversed(self.st["attempts"]):
            rows = a.get("log_rows") or []
            if rows:
                return rows[-1]
        return None

    def attempts_log_all(self) -> list:
        out = []
        for a in self.st["attempts"]:
            out.extend(a.get("log_rows") or [])
        return out

    # ---- hook(er012_b.generate_voice_body_wide_margin が呼ぶ) ----
    def before_attempt(self, attempt: int, max_attempts: int, out_path: str) -> dict:
        st = self.st
        n = int(st["n_started"]) + 1
        if st["status"] != "IN_PROGRESS" or n > self.block_end():
            return {"stop": True, "reason": f"ATTEMPT_BUDGET_EXHAUSTED(phase={self.phase}。総試行{MAX_TOTAL_ATTEMPTS}回[ブロック{block_attempts()}回x2]を使い切り、またはLR段階。{MAX_TOTAL_ATTEMPTS + 1}回目は存在しない)"}
        self.stop_check(f"tts_attempt:{self.clip_id}:n{n}")
        L = block_attempts()
        depth = 0 if n <= L else 1
        o = n - depth * L
        if o in _profile().cooldown_before:
            self._cooldown_before_fallback(n)
        mode = "ctx" if o <= CTX_ATTEMPTS else "legacy_fallback"
        st["n_started"] = n
        st["attempts"].append({"n": n, "mode": mode, "block": depth, "ordinal": o, "started_epoch": RUNTIME.clock(), "started_at": now_iso(),
                               "finished": False, "verified": None, "counted": False, "rows": 0})
        self.store.put(self.clip_id, st)     # TTS呼出より前に書く(TTS中に落ちても消費済み)
        self._cur = st["attempts"][-1]
        return {"stop": False, "style_prefix_override": (self.ctx_style if mode == "ctx" else None), "n": n, "mode": mode}

    def attempt_ctx_kwargs(self, attempt: int) -> dict:
        """leafの統一judgeへ渡すattempt_ctxの追加引数(er012_bが任意メソッドとして呼ぶ)。slot=通算n、total_slots=6(最終slotはn=6だけ=LR前の③でHRQを書かない)、
        LR block(n>ブロック長)は script_version='v1'(LR_REWRITTEN警告)・m1_anchor_text=元原稿。"""
        a = self._cur
        n = int(a["n"])
        d = {"slot_offset": n - int(attempt), "total_slots": MAX_TOTAL_ATTEMPTS}
        if n > block_attempts():
            d["script_version"] = "v1"
            d["m1_anchor_text"] = self.canonical_text
        return d

    def _cooldown_before_fallback(self, n: int) -> None:
        """ブロック内2回目NG後(n=3,6)の固定180秒(旧600秒)。起点=直前試行の最終NG確定時刻(無ければ完了時刻、完了前に落ちていれば開始時刻)。実時間で数える(再開しても180秒未満にならない)。"""
        st = self.st
        prev = st["attempts"][-1] if st["attempts"] else None
        ref = None
        if prev:
            ref = prev.get("final_ng_epoch") or prev.get("finished_epoch") or prev.get("started_epoch")
        if ref is None:
            return
        total = cooldown_seconds()
        cd = st["cooldowns"].get(str(n)) or (st.get("cooldown") if (st.get("cooldown") or {}).get("required_before_n") == n else None) or {}
        if cd.get("required_before_n") != n or cd.get("ref_epoch") != ref:
            cd = {"required_before_n": n, "ref_epoch": ref, "ref_at": now_iso(ref), "requested_seconds": total, "started_epoch": RUNTIME.clock(),
                  "started_at": now_iso(), "ended_epoch": None, "waited_seconds_this_process": 0.0, "resumed": False, "process_starts": 1}
        else:
            cd["resumed"] = True
            cd["process_starts"] = int(cd.get("process_starts", 1)) + 1
        st["cooldown"] = cd
        st["cooldowns"][str(n)] = cd
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
        st["cooldowns"][str(n)] = cd
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
        L = block_attempts()
        return (f"文脈・感情付きTTS方式の通算{self.n_started}回の試行(上限{MAX_TOTAL_ATTEMPTS}回=ブロック{L}回x2[LRを挟む]、各ブロックの1〜{CTX_ATTEMPTS}回目=文脈・感情付き、"
                f"{L}回目=従来方式)でもASR検証に合格しませんでした(この呼出のmax_attempts={max_attempts}、phase={self.phase})")

    def attempt_metadata(self) -> dict:
        a = getattr(self, "_cur", None) or {}
        return {"tts_mode": a.get("mode"), "overall_attempt_n": a.get("n"), "dialogue_tts_policy": self.policy_id,
                "dialogue_block_depth": a.get("block"), "dialogue_block_ordinal": a.get("ordinal")}

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
            r["dialogue_block_depth"] = a.get("block")
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
        if not verified and not technical_failure:
            # M5: LR入力候補。ASR内容不一致NGの転写だけ(PASS転写・反復検査のみNG・技術STOPは含めない)
            lst = self.st["ng_transcripts"]
            for r in rows:
                if _is_content_ng_row(r) and not any(e.get("n") == a["n"] and e.get("source") == "pre_slowdown" for e in lst):
                    lst.append({"n": a["n"], "source": "pre_slowdown", "asr_text": r["asr_text"], "classification": r.get("audio_classification"),
                                "canonical_text_sha256": self.canonical_text_sha256, "recorded_at": now_iso()})
        self.store.put(self.clip_id, self.st)

    # ---- LR phase(FZ-DIALOGUE-LR-ADOPTION-01) ----
    def enter_lr_phase(self, result: dict | None = None) -> bool:
        """元ブロック(B1)が非OKで終わった(技術STOPを除く)ときにdriverが呼ぶ。LR可(Profile.lr)・未使用(lr.state=NOT_STARTED)・IN_PROGRESS・phase=B1のときだけ
        phase=LRへ進める(status据置=IN_PROGRESS)。ブロックの途中で終わった(stop_retrying・行会計の予算切れ)場合は未実施slotを`skipped`で閉じ、LR block
        のn=4〜6を保つ。戻り値False=LR段へ進めない(driverは終端化する)。"""
        st = self.st
        if not lr_enabled() or st["status"] != "IN_PROGRESS" or self.phase != PHASE_B1 or self.lr["state"] != LR_NOT_STARTED:
            return False
        L = block_attempts()
        if int(st["n_started"]) < L:
            for k in range(int(st["n_started"]) + 1, L + 1):
                st["attempts"].append({"n": k, "mode": "skipped", "block": 0, "ordinal": k, "finished": True, "verified": None, "counted": True, "rows": 0,
                                       "skipped": True, "skipped_reason": "block_closed_early(stop_retrying/行会計の予算切れ)", "log_rows": []})
            st["n_started"] = L
        st["phase"] = PHASE_LR
        st["lr"]["state"] = LR_PENDING
        self.store.put(self.clip_id, st)
        return True

    def select_lr_input(self, canonical_text: str, protect_fn=None) -> dict:
        """LR入力転写の選択(JC-1/M5、Zセリフ限定。X/Yの『最終attemptの転写のみ』は不変)。現サイクル・同一本文shaの`ng_transcripts`(ASR内容不一致NGのみ)を
        新しい順(同一attempt内は減速後転写優先)に走査し、NG span(`identify_ng_span`)が見つかり、かつ`protect_fn`(確定内容との重なり判定)に掛からない最初の転写を返す。
        戻り値 {"found": bool, "n", "source", "asr_text", "ng_span", "skipped": [...]}。found=False=LR不可(TTS 0でHR)。"""
        import er020_tts_retry_local_rewrite_01 as er020
        cands = [t for t in self.st["ng_transcripts"] if t.get("canonical_text_sha256") == self.canonical_text_sha256 and t.get("asr_text")]
        cands.sort(key=lambda t: (-int(t["n"]), 0 if t.get("source") == "post_slowdown" else 1))
        skipped = []
        for t in cands:
            span = er020.identify_ng_span(canonical_text, t["asr_text"])
            if not span.get("found"):
                skipped.append({"n": t["n"], "source": t["source"], "reason": "NO_NG_SPAN"})
                continue
            if protect_fn is not None:
                pr = protect_fn(span, t["asr_text"]) or {}
                if pr.get("protected"):
                    skipped.append({"n": t["n"], "source": t["source"], "reason": "OVERLAPS_CONFIRMED_CONTENT", "stops": pr.get("stops"),
                                    "ng_span": span.get("canonical_span_with_context")})
                    continue
            sel = {"found": True, "n": t["n"], "source": t["source"], "asr_text": t["asr_text"], "ng_span": span, "skipped": skipped}
            self.lr["input"] = {"n": t["n"], "source": t["source"], "asr_text": t["asr_text"],
                                "ng_changed_words": span.get("canonical_changed_words"), "skipped": skipped}
            self.store.put(self.clip_id, self.st)
            return sel
        self.lr["input"] = {"n": None, "source": None, "asr_text": None, "skipped": skipped, "reason": "NO_USABLE_LR_INPUT"}
        self.store.put(self.clip_id, self.st)
        return {"found": False, "skipped": skipped}

    def save_lr_text(self, rewritten: str) -> None:
        """書換え本文をTTS前に永続化してphase=B2へ(LR 1回の構造的保証: 保存済みと異なる本文での2回目は拒否)。"""
        lr = self.lr
        if self.st["status"] != "IN_PROGRESS" or self.phase not in (PHASE_LR, PHASE_B2):
            raise RuntimeError(f"save_lr_text: phase={self.phase}/status={self.st['status']} ではLR本文を保存できません")
        if lr.get("text") and lr["text"] != rewritten:
            raise RuntimeError("save_lr_text: 保存済みのLR本文と異なる本文でのLR再実行は禁止(LR最大1回)")
        if lr.get("text") == rewritten and self.phase == PHASE_B2:
            return      # resume時の再保存(冪等)
        lr.update({"text": rewritten, "text_sha": _sha256_text(rewritten), "state": LR_TEXT_SAVED, "saved_at": now_iso()})
        self.st["phase"] = PHASE_B2
        self.store.put(self.clip_id, self.st)

    def save_lr_audit(self, audit: dict) -> None:
        self.lr["audit"] = _jsonable(audit)
        self.store.put(self.clip_id, self.st)

    def mark_lr_outcome(self, recovery_status: str | None) -> None:
        """lr_recoverがNone(非RESOLVED)で終わったときにdriverが呼ぶ。LR block(B2)のTTSを始めていればUNRESOLVED、始める前に終わった(NO_NG_SPAN・候補全滅・
        LR例外)ならNOT_APPLICABLE。どちらもLR終了=clipは終端化される(M4(b): 新規TTS 0でも再実行がLR LLMを再び回さない)。"""
        self.lr["state"] = LR_UNRESOLVED if self.n_started > block_attempts() else LR_NOT_APPLICABLE
        self.lr["outcome_status"] = recovery_status
        self.lr["ended_at"] = now_iso()
        self.store.put(self.clip_id, self.st)

    def mark_lr_not_applicable(self, reason: str) -> None:
        """LR入力転写が無い(全転写がNO_NG_SPAN/確定内容と重なる)=LR不可。TTS 0・LR LLM 0で終端化。"""
        self.lr["state"] = LR_NOT_APPLICABLE
        self.lr["outcome_status"] = reason
        self.lr["ended_at"] = now_iso()
        self.store.put(self.clip_id, self.st)

    def settle_lr_state(self, result: dict) -> None:
        """採用結果(OK)がLR block(phase=B2・LR本文保存済み)のものなら、evidenceに残す前にlr.stateをRESOLVEDにする(finish()も同じ遷移を行う=冪等)。"""
        if isinstance(result, dict) and result.get("status") == "OK" and self.phase == PHASE_B2 and self.lr.get("text") and self.lr.get("state") != LR_RESOLVED:
            self.lr["state"] = LR_RESOLVED
            self.lr["ended_at"] = now_iso()
            self.store.put(self.clip_id, self.st)

    # ---- 結果確定(dialogue()から) ----
    def evidence(self, extra: dict | None = None) -> dict:
        st = self.st
        real = [a for a in st["attempts"] if not a.get("skipped")]
        last = real[-1] if real else {}
        mode = last.get("mode")
        eff = last.get("effective_mode")
        d = {"policy": self.policy_id, "final_mode": eff or mode, "final_attempt_n": last.get("n"), "n_started": st["n_started"],
             "decision": self.decision, "resumed_from_process_state": self.restored_from_process_state, "n_started_at_open": self.n_started_at_open,
             "ctx_style_sha256": self.ctx_style_sha256,
             "attempts": [{k: a.get(k) for k in ("n", "mode", "effective_mode", "verified", "started_at", "finished_at", "rows", "technical_failure", "counted",
                                                 "block", "ordinal", "skipped")} for a in st["attempts"]],
             "cooldown": st.get("cooldown"), "cooldowns": st.get("cooldowns"), "cycle": st.get("cycle"), "history": st.get("history") or [],
             "phase": st.get("phase"), "lr_state": (st.get("lr") or {}).get("state"), "lr_text_sha": (st.get("lr") or {}).get("text_sha"),
             "lr_input": (st.get("lr") or {}).get("input"), "lr_migration": (st.get("lr") or {}).get("migration"),
             "block_attempts": block_attempts(), "max_total_attempts": MAX_TOTAL_ATTEMPTS}
        if extra:
            d.update(extra)
        return d

    def _attach_final_adoption(self, result: dict) -> None:
        """LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_06(B1、記録追記のみ): 採用takeの最小記録`final_adoption`を結果dictへ追記する
        (er127.BlockRunの記録と同形。Z会話の採用は最後に実行したattempt)。style_mode=PRIMARY(ctx Style採用)/FALLBACK(従来Dialogue Style・minimal)。
        sent_style_sha=ctx Style採用時のみctx style sha(それ以外は送信Styleがctx styleでないためNone)。Gate判定・回数・待機・採否は不変。
        FZ-DIALOGUE-LR-ADOPTION-01: 通算n>ブロック長(LR block採用)は depth=1・ordinal=n-ブロック長・slot=①'②'③'(元ブロック採用は従来と同じdepth=0)。
        記録の失敗で採用を止めない。"""
        try:
            import er127_tts_block_policy_01 as er127
            real = [a for a in self.st["attempts"] if not a.get("skipped")]
            last = real[-1] if real else None
            if not last:
                return
            eff = last.get("effective_mode") or last.get("mode")
            n = int(last["n"])
            depth = 0 if n <= block_attempts() else 1
            ordinal = n - depth * block_attempts()
            result["final_adoption"] = {
                "depth": depth, "ordinal": ordinal, "slot": er127._slot_label(ordinal, depth),
                "style_mode": "PRIMARY" if eff == "ctx" else "FALLBACK",
                "sent_style_sha": self.ctx_style_sha256 if eff == "ctx" else None,
                "attempt_audio_sha": _sha256_file(self.out_path), "source": "tts_attempt"}
        except Exception:     # noqa: BLE001
            pass

    def finish(self, result: dict, *, technical_stop: bool = False) -> dict:
        """採用はfinish()のみで確定する(Opus R-2)。status OK -> DONE_OK(結果dict+wav shaを保存)。非OK -> 実際に試行した結果ならTERMINAL_NG。
        Review Lockのblock結果(HUMAN_REVIEW_LOCKED、試行0)ではstateを変えない。
        FZ-DIALOGUE-LR-ADOPTION-01: technical_stop=True(Secondary/Whisper不能等の技術STOP)は品質NGではない=IN_PROGRESSのまま(LR・終端に入れない)。
        LR phase以降は、LR終了状態(UNRESOLVED/NOT_APPLICABLE)でも終端化する(M4(b))。B1の非OKを終端にせずLRへ進めるのはdriverの`enter_lr_phase`だけ。"""
        if not isinstance(result, dict):
            return result
        status = result.get("status")
        if status == "HUMAN_REVIEW_LOCKED":
            return result
        if status == "OK":
            self._attach_final_adoption(result)
            if self.phase == PHASE_B2 and self.lr.get("text"):
                self.lr["state"] = LR_RESOLVED
                self.lr["ended_at"] = now_iso()
            self.st["status"] = "DONE_OK"
            real = [a for a in self.st["attempts"] if not a.get("skipped")]
            self.st["done"] = {"result": _jsonable(result), "wav_sha256": _sha256_file(self.out_path),
                               "saved_at": now_iso(), "final_mode": (real[-1].get("effective_mode") if real else None)}
        elif technical_stop:
            pass
        elif (self.st["n_started"] > self.n_started_at_open or self.st["n_started"] >= MAX_TOTAL_ATTEMPTS
              or self.lr.get("state") in LR_TERMINAL_STATES):
            self.st["status"] = "TERMINAL_NG"
        self.store.put(self.clip_id, self.st)
        return result


# ============================================================
# LR呼出契約adapter(er127.lr_recover が要求する blk を、本stateを唯一の永続先として満たす)
# ============================================================
class _AdapterPolicy:
    def __init__(self, profile):
        self.profile = profile


class ZLrBlockAdapter:
    """`er127.lr_recover(blk, ...)`が読む/書く属性は `er127.LR_RECOVER_BLK_ATTRS` / `LR_RECOVER_PROGRESS_ATTRS` に固定(ASTテスト)。
    BlockProgress(別ファイル)は使わない=状態の二重化と6時間失効による『LR LLM再実行』を避ける。resumed=LR本文がstateに保存済み。"""

    def __init__(self, policy: DialogueAttemptPolicy):
        self._p = policy
        self.depth = 0
        self.policy = _AdapterPolicy(_profile())
        self.total_slots = int(_profile().total_slots)
        self._open_ordinal = None
        self.lr_outcome = None
        self.progress = self

    # ---- progress契約 ----
    @property
    def resumed(self) -> bool:
        return bool(self._p.lr.get("text"))

    def lr_state(self) -> dict:
        lr = self._p.lr
        return {"used": bool(lr.get("text")), "text": lr.get("text"), "text_sha": lr.get("text_sha"), **({"audit": lr["audit"]} if lr.get("audit") else {})}

    def save_lr_text(self, rewritten: str) -> None:
        self._p.save_lr_text(rewritten)

    def save_lr_audit(self, audit: dict) -> None:
        self._p.save_lr_audit(audit)

    # ---- blk契約 ----
    def done(self, ordinal, verified) -> None:      # 元ブロックのattemptはpolicy(hook)が閉じる。LR前に開いたままのordinalは無い(_open_ordinal=None)
        return None
