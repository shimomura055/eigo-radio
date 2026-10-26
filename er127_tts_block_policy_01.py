# -*- coding: utf-8 -*-
"""TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_02: Family X/Y/Z 共通「3回構成ブロック」policy核。

ユーザー正式決定(APPROVED_FOR_PRODUCTION 2026-10-26、原文 docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_USER.md §2〜§4):
  1ブロック = ①標準Style → ②標準Style → (②NG後に180秒待機) → ③Fallback Style。LRあり部位は③NG後にLocal Rewrite(LR)し、
  書換え後の原稿で**同じ3回構成を1回だけ**(LR block: ①'②'→180秒→③')実行する。最大TTS 6回・待機2回。LRなし部位は3回(KP英語のみ4回)。
  技術的エラーの即時再試行(attempt内F-Tech)は別枠として各leafに残る。

本moduleの責務(DESIGN_02.md参照):
  * `PROFILES`/`block_policy_for` — 星取表(ROW_MAPPING_01の9 policy)のコード化。**scope内で解決できないときは例外(fail-closed、Opus M-1)**。
  * `unified_flow_active()` — 唯一の読取関数。`er109_xz_scope_01.current_scope() in {X,Y,Z}`。env/引数/設定dict/起動scriptで変えられない。
    scope外(Family A/B/C=Legacy凍結)は常にFalse=各leafは従来コードをそのまま通る(byte同一)。
  * `cooldown_core` — 180秒の唯一の定義。実時間で数える(resume時は消費済み待機を再度払わない)。5秒刻みでSTOP確認。clock/sleepはRUNTIME経由のtest注入のみ。
  * `BlockRun`/`BlockProgress` — 1ブロックの順序(STOP確認・待機・②NG後の③)と永続state(消費済みattempt・待機起点・LR書換え本文)。
  * `lr_recover` — LR共通ラッパ。再入禁止(depth guard)、外側guardの存在assert、LR block(同じ3回構成)の実行、終端HRQ登録。
  * `register_terminal_hr` — 終端NG1件=HRQ1行(disfluency/repetition単独NG・NO_NG_SPAN等でも欠落しない、Opus M-4)。
本moduleは leaf module(voice01/news_tail_fix/crosslevel/repro01/n3_tts/...)を import しない(leaf側がimportする)。
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

MANAGEMENT_ID = "TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01"
COOLDOWN_SECONDS = 180.0            # 唯一の正式定義(原文§2: 180秒)。旧600秒は er020.LEGACY_COOLDOWN_SECONDS(scope外専用)
SLICE_SECONDS = 5.0                 # 待機中のSTOP確認間隔(U-12是正)
FALLBACK_ORDINAL = 3                # 1ブロック内でFallbackに入る通算番号(KP英語は③④=ENGLISH_LOCK)
BLOCK_ATTEMPTS = 3                  # 1ブロックのTTS回数(er011.PRODUCTION_MAX_TTS_ATTEMPTSと一致をimport時に検査)
LR_BLOCK_SLOT_OFFSET = 3            # LR blockのslotは通算4〜6
PROGRESS_MAX_AGE_SECONDS = 6 * 3600.0   # 古いIN_PROGRESS(落ちたまま放置)を新規サイクル扱いにする上限
PROGRESS_SCHEMA = "tts_block_progress_v1"
UNIFIED_SCOPES = frozenset({"X", "Y", "Z"})
STOP_ALL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er026_output", "family_z_production_e2e_01", "STOP_ALL")


# ---------------------------------------------------------------- 例外
class BlockPolicyError(RuntimeError):
    """X/Y/Z scope内でpolicyを解決できない(segment_id=None/未知ID)。黙ってlegacyへ落とさない(fail-closed、Opus M-1)。"""


class LocalRewriteReentryError(RuntimeError):
    """LR block内からLRを再実行しようとした(OPEN-376/D-B4の構造的禁止)。"""


class LocalRewriteContractError(RuntimeError):
    """lr_recoverを外側guardの外から呼んだ等、呼出契約違反(Opus M-3a)。"""


class TtsBlockStopError(BaseException):
    """待機中/attempt前のSTOP検出(専用型、Opus M-11)。BaseExceptionなので共有moduleの`except Exception`で握り潰されない。
    進行中のrecord_outcome(Lock化)/STOPPED結果の保存/再利用対象化を起こさず、runnerの最上位まで伝播する。"""


# ---------------------------------------------------------------- 時計(test注入点。Productionにenv迂回口は作らない)
class _Runtime:
    clock = staticmethod(time.time)
    sleep = staticmethod(time.sleep)


RUNTIME = _Runtime()


def now_iso(epoch: float | None = None) -> str:
    t = RUNTIME.clock() if epoch is None else epoch
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t))


# ---------------------------------------------------------------- STOP確認
_STOP_CHECK: Optional[Callable[[str], None]] = None


def register_stop_check(fn: Optional[Callable[[str], None]]) -> Optional[Callable[[str], None]]:
    """runnerが自分のSTOP確認関数(where->None、STOP時に例外)を登録する。戻り値=直前の登録(復元用)。
    Z=er063._check_stop_sentinel(run_dir, where)、Y=er062.check_stop_sentinel(where, out_dir)、X=同様のwrapper。"""
    global _STOP_CHECK
    prev = _STOP_CHECK
    _STOP_CHECK = fn
    return prev


def run_stop_check(where: str) -> None:
    """登録済みのSTOP確認を呼ぶ。未登録でも全run共通の STOP_ALL(絶対path)は必ず確認する(待機中に気付けない状態を作らない)。"""
    if _STOP_CHECK is not None:
        _STOP_CHECK(where)
    if os.path.exists(STOP_ALL_PATH):
        raise TtsBlockStopError(f"STOP_ALL が存在するため {where} の前で停止(新規API呼出なし、自動再開しない): {STOP_ALL_PATH}")


# ---------------------------------------------------------------- policy表
@dataclass(frozen=True)
class Profile:
    name: str
    block_attempts: int          # 1ブロック(元原稿側)のTTS回数: 3、KP英語のみ4(前段2+ENGLISH_LOCK 2)
    cooldown_before: tuple       # ブロック内ordinal(1始まり)で、直前NGのあとに180秒待機を入れる位置
    third_style: str             # ③のStyle種別: SAME / FALLBACK_MINIMAL_EN / FALLBACK_MINIMAL_JA / ENGLISH_LOCK / LEGACY_DIALOGUE / NONE
    lr: bool                     # ③NG後にLocal Rewriteしてよいか(表で決まる。cs flagでは決めない)
    total_slots: int             # HRQを書く終端slot(元ブロック+LR block): LRあり6 / LRなし3 / KP 4
    max_tts: int
    max_waits: int
    unified: bool = True         # False=表外(SHELL_EN)/TTSなし(NO_TTS)=leafは現行コードのまま


PROFILES = {
    "EN_LR_STD":    Profile("EN_LR_STD", 3, (3,), "FALLBACK_MINIMAL_EN", True, 6, 6, 2),
    "EN_LR_ADV":    Profile("EN_LR_ADV", 3, (3,), "FALLBACK_MINIMAL_EN", True, 6, 6, 2),
    "JA_STD":       Profile("JA_STD", 3, (3,), "FALLBACK_MINIMAL_JA", False, 3, 3, 1),
    "KP_EN":        Profile("KP_EN", 4, (3,), "ENGLISH_LOCK", False, 4, 4, 1),
    "KP_EXPL":      Profile("KP_EXPL", 3, (3,), "FALLBACK_MINIMAL_EN", False, 3, 3, 1),
    "Z_DLG_CTX":    Profile("Z_DLG_CTX", 3, (3,), "LEGACY_DIALOGUE", False, 3, 3, 1),
    "Z_DLG_LEGACY": Profile("Z_DLG_LEGACY", 3, (3,), "SAME", False, 3, 3, 1),
    "SHELL_EN":     Profile("SHELL_EN", 3, (), "SAME", False, 3, 3, 0, unified=False),
    "NO_TTS":       Profile("NO_TTS", 0, (), "NONE", False, 0, 0, 0, unified=False),
}
POLICY_NAMES = tuple(PROFILES)

# 表外(DESIGN_01 §7 A-1、Fable確認済み=現行維持): shell固定英語。filename_suffix付き(welcome_a2等)も含む。
SHELL_EN_ID_RE = re.compile(r"(welcome|preview_intro|key_phrases_intro|full_story_intro|num_(?:one|two|three|four|five))(?:_[A-Za-z0-9]+)*")
LR_ROLES = frozenset({"FULL_STORY", "COMMENT", "PREVIEW", "TOPIC_INTRO", "IN_ONE_LINE"})
ENGLISH_ADV_LEAVES = frozenset({"L1", "L2"})
ENGLISH_STD_LEAVES = frozenset({"L3", "L4"})
LEAVES = frozenset({"L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"})


def unified_flow_active() -> bool:
    """唯一の読取関数。X/Y/Z run scope内のときだけTrue。env/引数/設定dict/起動scriptでは変えられない(CLAUDE.md安全境界と同形)。
    本件は APPROVED_FOR_PRODUCTION(2026-10-26)でありflagではない=scope内の既定動作。scope外(A/B/C)はFalse。"""
    import er109_xz_scope_01 as xz_scope
    return xz_scope.current_scope() in UNIFIED_SCOPES


@dataclass(frozen=True)
class BlockPolicy:
    profile: Profile
    leaf: str
    segment_id: Optional[str]
    level: Optional[str]


def block_policy_for(leaf: str, segment_id: Optional[str] = None, *, z_dialogue_policy: Optional[str] = None) -> Optional[BlockPolicy]:
    """leaf(L1〜L8)+segment_idからpolicyを決める。scope外はNone(=legacy)。scope内で解決できなければBlockPolicyError(M-1)。
    L1/L2=Adv英語、L3/L4=Std英語、L5=KP解説、L6=KP英語phrase、L7=日本語、L8=Zセリフ(z_dialogue_policy='fz_ctx_v1'|'legacy')。"""
    if leaf not in LEAVES:
        raise BlockPolicyError(f"unknown leaf {leaf!r}")
    if not unified_flow_active():
        return None
    if leaf == "L5":
        return BlockPolicy(PROFILES["KP_EXPL"], leaf, segment_id, "b1b")
    if leaf == "L6":
        return BlockPolicy(PROFILES["KP_EN"], leaf, segment_id, None)
    if leaf == "L7":
        return BlockPolicy(PROFILES["JA_STD"], leaf, segment_id, None)
    if leaf == "L8":
        if z_dialogue_policy not in ("fz_ctx_v1", "legacy"):
            raise BlockPolicyError(f"L8 requires z_dialogue_policy in (fz_ctx_v1, legacy), got {z_dialogue_policy!r}")
        return BlockPolicy(PROFILES["Z_DLG_CTX" if z_dialogue_policy == "fz_ctx_v1" else "Z_DLG_LEGACY"], leaf, segment_id, "b1b")
    # 英語(L1〜L4)
    if not segment_id:
        raise BlockPolicyError(f"{leaf}: X/Y/Z scope内でsegment_idを解決できません(out_pathが標準layoutでない)。legacy(旧600秒・LR後1回)へ黙って落とさず停止します")
    if SHELL_EN_ID_RE.fullmatch(segment_id):
        return BlockPolicy(PROFILES["SHELL_EN"], leaf, segment_id, None)
    import er020_tts_retry_local_rewrite_01 as er020
    role = er020.resolve_narrative_role(segment_id)
    if role in LR_ROLES:
        name = "EN_LR_ADV" if leaf in ENGLISH_ADV_LEAVES else "EN_LR_STD"
        return BlockPolicy(PROFILES[name], leaf, segment_id, "b1b" if leaf in ENGLISH_ADV_LEAVES else "a2")
    raise BlockPolicyError(f"{leaf}: segment_id={segment_id!r} のroleを解決できません(role={role!r})。表にない部位はfail-closedで停止します")


def fingerprint_sha(fp: dict | None) -> str:
    return hashlib.sha256(json.dumps(fp or {}, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()[:16]


def text_sha(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- cooldown_core
def cooldown_core(*, ref_epoch: float | None = None, seconds: float | None = None, stop_check: Optional[Callable[[str], None]] = None,
                  label: str = "", clock=None, sleep=None, slice_seconds: float | None = None, resumed: bool = False,
                  attempt_before: int | None = None, attempt_after: int | None = None) -> dict:
    """180秒待機の唯一の実装。起点=直前attemptのNG確定時刻(ref_epoch。None=いま)。残り=ref+seconds-now を**実時間**で数える
    (resume時に消費済みの待機を再度払わない)。待機中は5秒刻みでSTOP確認(STOP時は例外で即中断、stateの起点は保持)。
    戻り値は旧`maybe_cooldown_before_attempt`と同形のキー+resumed/total_elapsed_since_ref_seconds。"""
    clock = clock or RUNTIME.clock
    sleep = sleep or RUNTIME.sleep
    total = COOLDOWN_SECONDS if seconds is None else float(seconds)
    sl = SLICE_SECONDS if slice_seconds is None else float(slice_seconds)
    started = clock()
    ref = started if ref_epoch is None else float(ref_epoch)
    started_iso = now_iso(started)
    while True:
        remaining = ref + total - clock()
        if remaining <= 0:
            break
        (stop_check or run_stop_check)(f"tts_cooldown:{label}")
        sleep(min(sl, remaining))
    ended = clock()
    return {
        "cooldown_requested_seconds": total,
        "cooldown_actual_seconds": round(ended - started, 3),
        "cooldown_started_at": started_iso,
        "cooldown_ended_at": now_iso(ended),
        "attempt_before_cooldown": attempt_before,
        "attempt_after_cooldown": attempt_after,
        "total_elapsed_since_ref_seconds": round(ended - ref, 3),
        "resumed": bool(resumed),
    }


# ---------------------------------------------------------------- BlockCtx / Progress
@dataclass(frozen=True)
class BlockCtx:
    """leafへ渡すブロック文脈。depth=0が元ブロック、depth=1がLR block(LR再入禁止)。"""
    depth: int = 0
    slot_offset: int = 0
    total_slots: Optional[int] = None
    script_version: str = "v0"
    m1_anchor_text: Optional[str] = None
    lock_text: Optional[str] = None      # Lock key/HRQ lock_canonical_text=元原稿(LR block内でも元原稿のまま)


def _layout_ok(out_path: str) -> bool:
    import er011_human_review_lock_01 as review_lock
    return review_lock._has_valid_narration_layout(out_path)


def segment_id_from_out_path(out_path: str) -> Optional[str]:
    import er011_human_review_lock_01 as review_lock
    if review_lock._has_valid_narration_layout(out_path):
        return review_lock.derive_segment_key(out_path)[2]
    return None


class BlockProgress:
    """1 segmentの永続state。per-segment file(`<level_dir>/audit/tts_block_progress/<segment_id>.json`、tmp+os.replace)で
    並列processのsegment間競合を避ける。layoutが標準でない(単体test等)ときはin-memoryのみ。
    キー=(segment_id, 元原稿sha, Style/Voice/backend/profile/policy指紋)。不一致/DONE/古いIN_PROGRESS/REGENERATE_APPROVED/verified済みattempt有りは新規サイクル。
    書換え本文(lr.text)そのものを保存する=resume時に旧run/旧themeのLR artifactを拾わない(Opus M-2)。"""

    def __init__(self, out_path: str, segment_id: str, orig_text: str, fingerprint: dict):
        self.out_path = out_path
        self.segment_id = segment_id
        self.key = hashlib.sha256(json.dumps({"seg": segment_id, "text": text_sha(orig_text), "fp": fingerprint_sha(fingerprint)},
                                              sort_keys=True).encode("utf-8")).hexdigest()[:24]
        self.fingerprint = fingerprint
        self.persistent = _layout_ok(out_path)
        self.path = None
        if self.persistent:
            norm = out_path.replace("\\", "/")
            level_dir = os.path.dirname(os.path.dirname(norm))
            self.path = f"{level_dir}/audit/tts_block_progress/{segment_id}.json"
        self.state = None
        self.resumed = False
        self._resume_n = {}        # depth -> 前processで開始済みのordinal数(consumed判定)
        self._load_or_new(orig_text)

    # ---- persistence
    def _read(self) -> dict | None:
        if not self.path or not os.path.exists(self.path):
            return None
        try:
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return None

    def _write(self) -> None:
        if not self.path:
            return
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = f"{self.path}.tmp{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2, default=str)
        os.replace(tmp, self.path)

    def _regenerate_approved(self, orig_text: str) -> bool:
        """明示再生成(Lockの REGENERATE_APPROVED 消費)は新規サイクル。`--only-*`の再実行はそれだけでは新規サイクルにしない(Opus M-2)。"""
        if not self.persistent:
            return False
        import er011_human_review_lock_01 as review_lock
        try:
            entry = review_lock._load_store(review_lock._level_out_dir_from_out_path(self.out_path)).get(self.segment_id)
        except (OSError, ValueError):
            return False
        return bool(entry and entry.get("state") == "REGENERATE_APPROVED" and entry.get("canonical_text_sha256") == review_lock._text_hash(orig_text))

    def _new_state(self) -> dict:
        return {"schema": PROGRESS_SCHEMA, "key": self.key, "segment_id": self.segment_id, "fingerprint": self.fingerprint,
                "status": "IN_PROGRESS", "created_epoch": RUNTIME.clock(), "updated_epoch": RUNTIME.clock(),
                "blocks": {}, "lr": {"used": False, "text": None, "text_sha": None}}

    def _load_or_new(self, orig_text: str) -> None:
        prev = self._read()
        usable = (prev is not None and prev.get("key") == self.key and prev.get("status") == "IN_PROGRESS"
                  and (RUNTIME.clock() - float(prev.get("updated_epoch") or 0)) <= PROGRESS_MAX_AGE_SECONDS
                  and not self._regenerate_approved(orig_text)
                  and not any(a.get("verified") for b in (prev.get("blocks") or {}).values() for a in (b.get("attempts") or {}).values()))
        if usable:
            self.state = prev
            self.resumed = True
            for depth, b in (prev.get("blocks") or {}).items():
                self._resume_n[int(depth)] = int(b.get("n_started") or 0)
        else:
            self.state = self._new_state()
            self._write()

    # ---- block state
    def _block(self, depth: int) -> dict:
        return self.state["blocks"].setdefault(str(depth), {"n_started": 0, "attempts": {}, "cooldown": None})

    def consumed(self, depth: int, ordinal: int) -> bool:
        """前processで開始済み(TTS呼出前にn_startedを書く=TTS中に落ちても消費済み)のordinalか。"""
        return ordinal <= self._resume_n.get(depth, 0)

    def prev_ref_epoch(self, depth: int, ordinal: int) -> float | None:
        b = self._block(depth)
        a = (b["attempts"].get(str(ordinal - 1)) or {})
        return a.get("finished_epoch") or a.get("started_epoch")

    def start(self, depth: int, ordinal: int) -> None:
        b = self._block(depth)
        b["n_started"] = max(int(b["n_started"]), ordinal)
        b["attempts"].setdefault(str(ordinal), {})["started_epoch"] = RUNTIME.clock()
        self.state["updated_epoch"] = RUNTIME.clock()
        self._write()

    def finish_attempt(self, depth: int, ordinal: int, verified: bool) -> None:
        b = self._block(depth)
        a = b["attempts"].setdefault(str(ordinal), {})
        a["finished_epoch"] = RUNTIME.clock()
        a["verified"] = bool(verified)
        self.state["updated_epoch"] = RUNTIME.clock()
        self._write()

    def cooldown_record(self, depth: int, ordinal: int) -> dict | None:
        cd = self._block(depth).get("cooldown")
        return cd if cd and cd.get("before_ordinal") == ordinal else None

    def save_cooldown(self, depth: int, ordinal: int, rec: dict) -> None:
        self._block(depth)["cooldown"] = {"before_ordinal": ordinal, **{k: rec.get(k) for k in (
            "cooldown_started_at", "cooldown_ended_at", "cooldown_actual_seconds", "total_elapsed_since_ref_seconds", "resumed")}}
        self._write()

    def lr_state(self) -> dict:
        return self.state["lr"]

    def save_lr_text(self, rewritten: str) -> None:
        self.state["lr"] = {"used": True, "text": rewritten, "text_sha": text_sha(rewritten)}
        self.state["updated_epoch"] = RUNTIME.clock()
        self._write()

    def mark_done(self, final_status: str | None = None) -> None:
        self.state["status"] = "DONE"
        self.state["final_status"] = final_status
        self.state["updated_epoch"] = RUNTIME.clock()
        self._write()


@dataclass
class Step:
    ordinal: int
    skip: bool = False
    style_mode: str = "PRIMARY"          # PRIMARY / FALLBACK(= ordinal == FALLBACK_ORDINAL でFallbackを持つprofile)
    cooldown: Optional[dict] = None
    slot: int = 0
    is_last_slot: bool = False


class BlockRun:
    """1回のleaf呼出(=1ブロック)の進行役。loop型leafは attempt毎に `step(attempt)`→TTS→`done(attempt, verified)`、
    stage型leafはstage跨ぎの通算ordinalで同じ呼出を行う。"""

    def __init__(self, policy: BlockPolicy, ctx: BlockCtx, out_path: str, text: str, max_attempts: int, progress: BlockProgress,
                 label: str):
        self.policy = policy
        self.ctx = ctx
        self.out_path = out_path
        self.text = text
        self.max_attempts = max_attempts
        self.progress = progress
        self.label = label
        self.cooldown_events: list = []
        self.last_ng_epoch: float | None = None
        self.tts_started = 0
        self.depth = ctx.depth
        self._open_ordinal: int | None = None    # step済みでdone未呼出のordinal(次のstep/finishで不合格として自動closeする)
        self.lr_outcome: dict | None = None      # lr_recoverが残す {"recovery":..., "block_result":...}(非RESOLVED時もLR blockのTTS行を呼出元が会計へ戻すため)

    # ---- slots
    @property
    def total_slots(self) -> int:
        return int(self.ctx.total_slots if self.ctx.total_slots is not None else self.policy.profile.total_slots)

    def slot(self, ordinal: int) -> int:
        return self.ctx.slot_offset + ordinal

    def is_last_slot(self, ordinal: int) -> bool:
        return self.slot(ordinal) >= self.total_slots

    def ctx_kwargs(self) -> dict:
        return {"slot_offset": self.ctx.slot_offset, "total_slots": self.total_slots}

    @property
    def lr_allowed(self) -> bool:
        return bool(self.policy.profile.lr) and self.depth == 0

    # ---- per-attempt
    def step(self, ordinal: int) -> Step:
        """attempt開始前に呼ぶ。直前に開始したattemptがdone未呼出なら不合格として閉じる(NG確定時刻=待機の起点を永続化)。
        consumed(前processで開始済み)ならskip=True(stub行を積んで次へ)。STOP確認→(③前なら)180秒待機→n_started永続化→TTS、の順。"""
        slot = self.slot(ordinal)
        last = self.is_last_slot(ordinal)
        if self._open_ordinal is not None:
            self.done(self._open_ordinal, False)
        if self.progress.consumed(self.depth, ordinal):
            return Step(ordinal, skip=True, slot=slot, is_last_slot=last)
        run_stop_check(f"tts_attempt:{self.label}:n{self.ctx.slot_offset + ordinal}")
        cd = None
        prof = self.policy.profile
        if ordinal in prof.cooldown_before and ordinal > 1:
            ref = self.last_ng_epoch if self.last_ng_epoch is not None else self.progress.prev_ref_epoch(self.depth, ordinal)
            prior = self.progress.cooldown_record(self.depth, ordinal) if self.progress.resumed else None
            cd = cooldown_core(ref_epoch=ref, label=self.label, resumed=prior is not None,
                               attempt_before=self.ctx.slot_offset + ordinal - 1, attempt_after=self.ctx.slot_offset + ordinal)
            self.cooldown_events.append(cd)
            self.progress.save_cooldown(self.depth, ordinal, cd)
            try:
                import er011_human_review_lock_01 as review_lock
                review_lock.append_attempt_history_event(self.out_path, "COOLDOWN_BEFORE_BLOCK_ATTEMPT", {
                    "segment": self.label, "policy": prof.name, "depth": self.depth, "attempt_before_cooldown": cd["attempt_before_cooldown"],
                    "attempt_after_cooldown": cd["attempt_after_cooldown"], "requested_seconds": cd["cooldown_requested_seconds"],
                    "actual_seconds": cd["cooldown_actual_seconds"], "resumed": cd["resumed"]})
            except Exception:    # 観測の失敗で生成を止めない
                pass
        self.progress.start(self.depth, ordinal)
        self.tts_started += 1
        self._open_ordinal = ordinal
        mode = "FALLBACK" if (ordinal == FALLBACK_ORDINAL and prof.third_style not in ("SAME", "NONE")) else "PRIMARY"
        return Step(ordinal, skip=False, style_mode=mode, cooldown=cd, slot=slot, is_last_slot=last)

    def done(self, ordinal: int, verified: bool) -> None:
        if self._open_ordinal == ordinal:
            self._open_ordinal = None
        if not verified:
            self.last_ng_epoch = RUNTIME.clock()
        self.progress.finish_attempt(self.depth, ordinal, verified)

    def stub_row(self, ordinal: int) -> dict:
        """前processで消費済み(TTS呼出済み・結果は失われた)attemptのattempts_log行。record_outcomeの実TTS計上を保つ(二重計上しない・取りこぼさない)。"""
        return {"attempt": ordinal, "status": "RESUMED_CONSUMED_BY_PRIOR_PROCESS", "verified": False, "carried_from_prior_process": True,
                "instruction_type": None}

    def finish(self, result: dict | None) -> None:
        """leaf正常終了時(OK/STOPPED/ASR_VALIDATION_UNCERTAIN等の戻り値あり)。例外終了(STOP等)では呼ばない=IN_PROGRESSのまま=後でresume可。"""
        if self._open_ordinal is not None:
            self.done(self._open_ordinal, (result or {}).get("status") == "OK")
        if self.depth == 0:
            self.progress.mark_done((result or {}).get("status"))


def open_block(leaf: str, out_path: str, text: str, *, ctx: Optional[BlockCtx] = None, max_attempts: int = BLOCK_ATTEMPTS,
               fingerprint: Optional[dict] = None, segment_id: Optional[str] = None, z_dialogue_policy: Optional[str] = None) -> Optional[BlockRun]:
    """leafの入口で1回呼ぶ。scope外/表外(SHELL_EN,NO_TTS)はNone=leafは従来コードのまま。scope内で解決不能は例外(fail-closed)。
    fingerprint: Style/Voice/backend/profile等(BlockProgressのkeyに入る。変わると新規サイクル)。"""
    ctx = ctx or BlockCtx()
    seg = segment_id or segment_id_from_out_path(out_path)
    pol = block_policy_for(leaf, seg, z_dialogue_policy=z_dialogue_policy)
    if pol is None or not pol.profile.unified:
        if ctx.depth and pol is None:
            raise BlockPolicyError("LR block(depth>=1)がscope外で呼ばれました")
        return None
    orig = ctx.lock_text if ctx.lock_text is not None else text
    fp = dict(fingerprint or {})
    fp.setdefault("policy", pol.profile.name)
    fp.setdefault("leaf", leaf)
    progress = BlockProgress(out_path, seg or os.path.splitext(os.path.basename(out_path))[0], orig, fp)   # depthはkeyに入れない: LR block(depth1)は同一segmentのprogress fileを共有(blocks["1"])
    return BlockRun(pol, ctx, out_path, text, max_attempts, progress, label=seg or os.path.basename(out_path))


def with_block(leaf: str, *, fingerprint_params: tuple = (), z_policy: Optional[Callable[[dict], Optional[str]]] = None,
               skip_when: Optional[Callable[[dict], bool]] = None):
    """leaf関数(第1・第2引数=text,out_path)へ統一blockを差し込むdecorator。`@guarded_generate`の**内側**に置く:
        @review_lock.guarded_generate("en")
        @er127.with_block("L1", fingerprint_params=("style_prefix_override", "tts_backend"))
        def generate_charon_english(text, out_path, ..., _blk=None): ...
    * 追加kw `tts_block`(BlockCtx。LR blockの呼出だけが渡す)をここで消費し、`_blk`(BlockRun|None)としてleaf本体へ渡す。
    * scope外/表外(SHELL_EN)は `_blk=None` → leaf本体は従来コードのまま(byte同一)。scope内で解決不能はBlockPolicyError(fail-closed)。
    * leaf正常終了(戻り値あり)で `blk.finish(result)`。例外(STOP等)では呼ばない=progressはIN_PROGRESSのまま=resume可。
    guard(`__wrapped__`)経由のLR block呼出: `leaf.__wrapped__(rewritten, out_path, ..., tts_block=BlockCtx(depth=1,...))`。"""
    import functools
    import inspect

    def deco(fn):
        sig = inspect.signature(fn)

        @functools.wraps(fn)
        def wrapper(text, out_path, *args, tts_block=None, **kwargs):
            if tts_block is not None and not isinstance(tts_block, BlockCtx):
                raise TypeError("tts_block must be BlockCtx (LR block context)")
            bound = sig.bind_partial(text, out_path, *args, **kwargs)
            bound.apply_defaults()
            allargs = dict(bound.arguments)
            blk = None
            if not (skip_when and skip_when(allargs)):
                fp = {"leaf": leaf}
                for name in fingerprint_params:
                    v = allargs.get(name)
                    fp[name] = hashlib.sha256(v.encode("utf-8")).hexdigest()[:16] if isinstance(v, str) else v
                blk = open_block(leaf, out_path, text, ctx=tts_block, max_attempts=int(allargs.get("max_attempts") or BLOCK_ATTEMPTS),
                                 fingerprint=fp, z_dialogue_policy=(z_policy(allargs) if z_policy else None))
            if blk is None:
                if tts_block is not None:
                    raise BlockPolicyError("tts_block(LR block)がscope外/表外/skip対象の呼出に渡されました")
                return fn(text, out_path, *args, **kwargs)
            result = fn(text, out_path, *args, _blk=blk, **kwargs)
            blk.finish(result)
            return result
        wrapper.__er127_leaf__ = leaf
        return wrapper
    return deco


def stage_kwargs(blk: Optional[BlockRun], ordinal_offset: int) -> dict:
    """stage型leafが内側のstrict loopへ渡す引数(blkなし=空=従来どおり)。"""
    if blk is None:
        return {}
    return {"block_run": blk, "block_ordinal_offset": ordinal_offset}


# ---------------------------------------------------------------- 終端HRQ
def _is_tech_stop(attempt: dict | None) -> bool:
    try:
        import er078_asr_unified_judge_01 as uj
        aj = (attempt or {}).get("asr_judgement")
        return bool(isinstance(aj, dict) and aj.get("state") in uj.TECHNICAL_STOP_STATES)
    except Exception:
        return False


def register_terminal_hr(*, out_path: str, canonical_text: str, attempt: dict | None, lock_text: str | None = None,
                         expected_source: str | None = None, final_status: str = "TERMINAL_NG") -> bool:
    """終端NG(最後のblockの最後のattemptが不合格)で、HRQ(human_review_queue.jsonl)へ1行を保証する(Opus M-4)。
    judgeが最終slotで既に書いていれば、既存の重複抑止(同一wav_path+canonical_text)で2行目は作られない。
    disfluency/repetition単独NG・NO_NG_SPAN・LR例外等、judge由来の行が出ない終端でも欠落しない(U-03/U-04b)。
    技術STOP(Secondary/Whisper不能)は品質NGではない=登録しない(承認不要・再実行で再開)。戻り値=登録を試みたか。"""
    if not _layout_ok(out_path) or _is_tech_stop(attempt):
        return False
    import er006_secondary_asr_01 as secondary_asr
    a = attempt or {}
    steps = a.get("cascade_steps") or ([{"classification": a.get("audio_classification"), "asr_text": a.get("asr_text")}] if a else [])
    detail = {"canonical_text": canonical_text, "wav_path": out_path, "steps": steps, "cost_guard_triggered": False,
              "final_status": final_status}
    if lock_text is not None and lock_text != canonical_text:
        detail["lock_canonical_text"] = lock_text
    if expected_source is not None:
        detail["expected_text_source"] = expected_source
    secondary_asr._log_human_review(detail)
    return True


def last_attempt_of(result: dict | None) -> dict | None:
    """result(STOPPED/NG)から最後に実行されたattempt行を取り出す(標準+fallback両ログ対応)。"""
    if not isinstance(result, dict):
        return None
    for key in ("fallback_attempts_log", "attempts_log", "standard_attempts_log"):
        log = result.get(key)
        if isinstance(log, list):
            for a in reversed(log):
                if isinstance(a, dict) and a.get("status") == "OK":
                    return a
            if log and isinstance(log[-1], dict):
                return log[-1]
    return None


# ---------------------------------------------------------------- LR共通ラッパ
def lr_recover(blk: BlockRun, *, text: str, out_path: str, last_asr_text: str | None, block_call: Callable[[str, BlockCtx], dict],
               merge: Callable[[dict, dict], dict], last_attempt: dict | None, retry_primitive=None, client=None) -> Optional[dict]:
    """③NG後のLocal Rewrite。回復成功時は merge(block_result, recovery) 済みの完全なresult(status=OK)を返す。回復不可はNone
    (呼出元は従来どおりSTOPPED/ASR_VALIDATION_UNCERTAINを返しLock+HRへ進む)。非RESOLVEDの終端は必ずHRQ1行にする(Opus M-4)。

    契約: (1)depth>=1(LR block内)から呼べない(LocalRewriteReentryError、OPEN-376) (2)外側guardの実行中でなければ呼べない
    (out_path in _ACTIVE_GUARDED_OUT_PATHS、Opus M-3a) (3)LR blockはblock_callが元と同じleaf・同じ引数で実行する(Style/Voice/速度/QA保持、OPEN-312)。
    LR block内のctx: script_version='v1'、m1_anchor_text=元原稿、lock_text=元原稿、slot_offset=3、total_slots=policy.total_slots。"""
    import er011_human_review_lock_01 as review_lock
    if retry_primitive is None:
        import er020_tts_retry_local_rewrite_01 as retry_primitive
    if blk.depth >= 1:
        raise LocalRewriteReentryError("LR block内からLocal Rewriteは再実行できません(OPEN-376/D-B4)")
    if out_path not in review_lock._ACTIVE_GUARDED_OUT_PATHS:
        raise LocalRewriteContractError("lr_recoverは外側guarded_generateの実行中にだけ呼べます(M-3a)")
    if not blk.policy.profile.lr:
        return None
    if not _layout_ok(out_path):
        return None
    theme_id, level, segment_id = review_lock.derive_segment_key(out_path)
    holder: dict = {}
    lr_ctx = BlockCtx(depth=1, slot_offset=LR_BLOCK_SLOT_OFFSET, total_slots=blk.total_slots, script_version="v1",
                      m1_anchor_text=text, lock_text=text)

    def _retts(rewritten: str) -> dict:
        blk.progress.save_lr_text(rewritten)
        try:
            r = block_call(rewritten, lr_ctx)
        except BaseException as exc:      # STOP等はLR例外として握らず、LLM段の外で再送出する
            holder["exc"] = exc
            return {"status": "STOPPED", "reason": "LR_BLOCK_EXCEPTION"}
        holder["block_result"] = r
        return r

    recovery = None
    stored = blk.progress.lr_state() if blk.progress.resumed else {}
    if stored.get("used") and stored.get("text"):
        # resume: LR LLMは再実行しない。保存済みの書換え本文でLR blockを続行(消費済みattemptは skip される)
        rewritten = stored["text"]
        r = _retts(rewritten)
        recovery = {"management_id": retry_primitive.MANAGEMENT_ID, "segment_id": segment_id, "canonical_text": text,
                    "last_asr_text": last_asr_text, "selection": {"selected": {"rewritten_segment": rewritten}},
                    "retts_result": r, "resumed_without_llm": True,
                    "status": "RESOLVED_BY_LOCAL_REWRITE" if r.get("status") == "OK" else "HUMAN_REVIEW_LOCKED_RETTS_FAILED"}
    else:
        try:
            recovery = retry_primitive.run_local_rewrite_recovery(
                segment_id=segment_id, canonical_text=text, last_asr_text=last_asr_text, retts_fn=_retts,
                out_dir=f"er011_output/local_rewrite_recovery/{theme_id}/{level}", client=client)
        except Exception as exc:      # LLM段の例外=LR不可(終端HR)。設定不備([STOP]/init_logger)は握らない
            if "exc" not in holder:
                if isinstance(exc, RuntimeError) and ("init_logger" in str(exc) or "[STOP]" in str(exc)):
                    raise
                recovery = {"status": "HUMAN_REVIEW_LOCKED_LR_EXCEPTION", "error": f"{type(exc).__name__}: {exc}"}
            else:
                raise
    if "exc" in holder:
        raise holder["exc"]
    blk.lr_outcome = {"recovery": recovery, "block_result": holder.get("block_result")}
    if recovery.get("status") == "RESOLVED_BY_LOCAL_REWRITE":
        resolved = merge(dict(recovery["retts_result"]), recovery)
        resolved.setdefault("local_rewrite_recovery", recovery)
        resolved["canonical_text_before_local_rewrite"] = text
        return resolved
    # 非RESOLVED=終端: LR block最終NGなら block の最後のattempt、LR不可(NO_NG_SPAN等)なら元ブロックの最後のattemptでHRQ1行
    br = holder.get("block_result")
    term_attempt = last_attempt_of(br) if br is not None else last_attempt
    term_text = ((recovery.get("selection") or {}).get("selected") or {}).get("rewritten_segment") if br is not None else None
    register_terminal_hr(out_path=out_path, canonical_text=term_text or text, attempt=term_attempt, lock_text=text,
                         expected_source="local_rewrite_text" if term_text else None,
                         final_status=str(recovery.get("status")))
    return None


def lr_unresolved_rows(blk: BlockRun) -> tuple:
    """LRが非RESOLVEDで終わったとき、LR blockが実際に消費したTTS行(標準側, fallback側)を返す。呼出元は自分の戻り値のattempts_logへ戻して
    record_outcomeの実TTS計上(=実TTS呼出数、Opus M-3b)を保つ。LR blockを実行していなければ空。"""
    out = (blk.lr_outcome or {}).get("block_result")
    if not isinstance(out, dict):
        return [], []
    if out.get("fallback_used") is True or out.get("fallback_attempts_log"):
        return list(out.get("standard_attempts_log") or out.get("attempts_log") or []), list(out.get("fallback_attempts_log") or [])
    return list(out.get("attempts_log") or []), []


def lr_attempt_summary(blk: BlockRun) -> dict | None:
    rec = (blk.lr_outcome or {}).get("recovery")
    if not isinstance(rec, dict):
        return None
    return {"status": rec.get("status"), "ng_span_found": (rec.get("ng_span") or {}).get("found"),
            "rewritten_text": (((rec.get("selection") or {}).get("selected")) or {}).get("rewritten_segment"),
            "resumed_without_llm": rec.get("resumed_without_llm", False)}


def merge_logs(*logs) -> list:
    out: list = []
    for lg in logs:
        out.extend(lg or [])
    return out


# ---------------------------------------------------------------- import時自己検査
def _self_check() -> None:
    import er011_human_review_lock_01 as review_lock
    assert review_lock.PRODUCTION_MAX_TTS_ATTEMPTS == BLOCK_ATTEMPTS == FALLBACK_ORDINAL
    assert COOLDOWN_SECONDS == 180.0
    assert set(PROFILES) == {"EN_LR_STD", "EN_LR_ADV", "JA_STD", "KP_EN", "KP_EXPL", "Z_DLG_CTX", "Z_DLG_LEGACY", "SHELL_EN", "NO_TTS"}
    for p in PROFILES.values():
        if p.unified:
            assert p.max_tts == p.total_slots and p.max_waits == len(p.cooldown_before) * (2 if p.lr else 1)


_self_check()
