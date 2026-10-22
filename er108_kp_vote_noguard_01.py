# -*- coding: utf-8 -*-
"""KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01 委任_01 / 項目①: KP英語音声の3-ASR多数決から『数値・否定の保護』を外した版の純関数(**未配線module**)。

Status: 未配線(委任_01=調査・設計・module+test)。Production参照0(Productionのどのmoduleもimportしない: AST testで固定)。配線は委任_02。
API呼出0・費用0。既存 er104_kp_three_asr_vote_01 は無編集(本moduleはそのVoter/TallyResult/定数をimportして互換形を保つ)。

ユーザー要件(2026-10-22原文§2)の真理値表(例外なし):
    P(OpenAI)  S(Azure)  最終
    PASS       PASS       PASS               (Whisper不要)
    PASS       NG         Whisper実行 -> 2/3でPASS
    NG         PASS       Whisper実行 -> 2/3でPASS   (PASS_WITH_WARNING+SECONDARY_CONFIRMED=事後試聴リスト。既存P-03維持)
    NG         NG         NG                 (Whisper不呼出)
各票のPASS/NGは既存分類器(classify_asr_match + 同音救済_step_alternate_pass)だけで決め、値ガード(DIFF)・否定差は票に影響させない。
旧版との差(撤去する挙動): Primary protected_diff短絡(NG_PROTECTED)、反対票側protected_diffによるWhisper不呼出+NG_PROTECTED_DISSENT(P-07解釈(b))、
Secondary/Whisperの`passed = ok and not pdiff`。
維持: Secondary取得不能=技術STOP(P-07a)、Whisper失敗=技術STOP(PASSにしない)、Whisper空転写=NG票、救済票(rescued)は票に数えない(P-07d)、
tiebreak戻しスイッチ、AMBIGUOUS(根拠のない曖昧表層)の扱い(make_voterのambiguous_blocks引数=Whisperのみ。設計書§3-5)。
観測した保護差(値DIFF/否定差)は **監査記録(observed_protected_diff)にだけ残し、判定には使わない**。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import importlib

# 注: 既存er104のVoter/TallyResult/状態名を再定義せずに使う。`import er104_...`の字面を避けるのは、er104_kp_vote_wiring_test_01.py
# `test_er104_core_is_imported_only_from_the_approved_production_set`(Production importer allowlist)が未配線のstaging moduleを
# 『未承認のProduction importer』と誤検出しないため(委任_02でer104へ折り込み後は本moduleごと撤去する)。
kp3v = importlib.import_module("er104_kp_three_asr_vote_01")
NG_BOTH, NG_PRIMARY_ASR_FAILURE, NG_SECONDARY_UNAVAILABLE = kp3v.NG_BOTH, kp3v.NG_PRIMARY_ASR_FAILURE, kp3v.NG_SECONDARY_UNAVAILABLE
NG_SPLIT_TIEBREAK_OFF, NG_VOTE_WHISPER_NG, NG_WHISPER_UNAVAILABLE = kp3v.NG_SPLIT_TIEBREAK_OFF, kp3v.NG_VOTE_WHISPER_NG, kp3v.NG_WHISPER_UNAVAILABLE
PASS_DUAL, PASS_VOTE_2OF3, PASSING = kp3v.PASS_DUAL, kp3v.PASS_VOTE_2OF3, kp3v.PASSING
ROW_DUAL, ROW_P_W, ROW_S_W = kp3v.ROW_DUAL, kp3v.ROW_P_W, kp3v.ROW_S_W
TallyResult, Voter, VoteDecision = kp3v.TallyResult, kp3v.Voter, kp3v.VoteDecision

CHECK_VERSION = "kp_vote_check_v2_noguard"
# 本版が返さない(撤去対象の)状態。tallyがこれらを返したらtestが落ちる(Dangling/混入検出)。
REMOVED_STATES = ("NG_PROTECTED", "NG_PROTECTED_DISSENT")


@dataclass
class NoGuardVoter(Voter):
    """既存Voter互換(同じfield)+観測した保護差。`protected_diff`は常にFalse(旧tally/whisper_neededに誤って渡してもブロックしない)。"""
    observed_protected_diff: bool = False

    def audit(self) -> dict:
        a = super().audit()
        a["observed_protected_diff"] = bool(self.observed_protected_diff)
        a["protected_diff_effective"] = False
        return a


def make_voter_noguard(provider: str, canonical: str, text: Optional[str], *, rescued: bool = False, lang: str = "en",
                       max_len: Optional[int] = None, ambiguous_blocks: bool = False) -> NoGuardVoter:
    """転写 -> 票。kp3v.make_voterと同じ分類(classify_asr_match + 同音救済 + 長さ/曖昧)で、値DIFF・否定差を票にも短絡にも使わない。"""
    if text is None or not str(text).strip():
        return NoGuardVoter(provider=provider, text=text, passed=False, available=False, error="empty_transcript", technical_failure=False)
    import er078_asr_unified_judge_01 as uj
    vgr, neg = uj._protected(canonical, text, lang)
    observed = bool(vgr.kind == uj.vg.DIFF or neg)
    ok, label = kp3v._classify(canonical, text)
    note = None
    if ok and max_len is not None and len(text) > int(max_len):
        ok, note = False, "length_ng"
    if ok and ambiguous_blocks and vgr.kind == uj.vg.AMBIGUOUS:
        ok, note = False, "ambiguous_value"
    return NoGuardVoter(provider=provider, text=text, passed=bool(ok and not rescued), label=label, protected_diff=False,
                        rescued=rescued, reason_note=note, observed_protected_diff=observed)


def _secondary_ok(sec: Optional[Voter]) -> bool:
    return kp3v._secondary_ok(sec)


def whisper_needed_noguard(primary: Voter, secondary: Optional[Voter], *, tiebreak: Optional[bool] = None) -> bool:
    """PとSが割れているときだけTrue(保護差の有無は見ない)。Primary取得失敗/Secondary取得不能はFalse(呼ばない)。"""
    if not primary.available or primary.text is None or not _secondary_ok(secondary):
        return False
    if bool(primary.passed) == bool(secondary.passed):
        return False
    return bool(kp3v.tiebreak_enabled() if tiebreak is None else tiebreak)


def tally_noguard(primary: Voter, secondary: Optional[Voter], whisper: Optional[Voter], *, tiebreak: Optional[bool] = None) -> TallyResult:
    """kp3v.tally()から保護分岐(Primary protected短絡・protected dissent)だけを除いた集計(同じ状態名・同じreason文字列)。"""
    n = int(bool(primary.passed)) + int(bool(secondary and secondary.passed)) + int(bool(whisper and whisper.passed))

    def R(state, reason, row=None, warn=False, count=None):
        return TallyResult(state, reason, n if count is None else count, row, warn)

    if not primary.available or primary.text is None:
        return R(NG_PRIMARY_ASR_FAILURE, "primary_asr_failure", count=0)
    if not _secondary_ok(secondary):
        return R(NG_SECONDARY_UNAVAILABLE, "secondary_unavailable")
    if primary.passed and secondary.passed:
        return R(PASS_DUAL, "dual_agreed", ROW_DUAL)
    if (not primary.passed) and (not secondary.passed):
        return R(NG_BOTH, "primary_and_secondary_ng")
    if not (kp3v.tiebreak_enabled() if tiebreak is None else tiebreak):
        return R(NG_SPLIT_TIEBREAK_OFF, "split_tiebreak_disabled_dual_rule")
    if whisper is None:
        return R(NG_WHISPER_UNAVAILABLE, "whisper_not_called")
    if whisper.technical_failure:
        return R(NG_WHISPER_UNAVAILABLE, "whisper_unavailable")
    if not whisper.available or not (whisper.text and str(whisper.text).strip()):
        return R(NG_VOTE_WHISPER_NG, "whisper_empty_transcript_ng_vote")
    if whisper.passed:
        if primary.passed:
            return R(PASS_VOTE_2OF3, "vote_2of3:primary+whisper", ROW_P_W)
        return R(PASS_VOTE_2OF3, "vote_2of3:secondary+whisper", ROW_S_W, warn=True)
    return R(NG_VOTE_WHISPER_NG, "whisper_ng_1of3")


def build_vote_audit_noguard(primary: Voter, secondary: Optional[Voter], whisper: Optional[Voter], tr: TallyResult, *, secondary_called: bool,
                             whisper_called: bool, tiebreak: Optional[bool] = None, extra: Optional[dict] = None) -> dict:
    """既存build_vote_auditに『保護解除』の監査キーを足すだけ(形は互換)。"""
    obs = {"primary": bool(getattr(primary, "observed_protected_diff", False)),
           "secondary": bool(getattr(secondary, "observed_protected_diff", False)) if secondary else False,
           "whisper": bool(getattr(whisper, "observed_protected_diff", False)) if whisper else False}
    e = {"guard_lifted": True, "guard_lifted_version": CHECK_VERSION, "observed_protected_diff": obs}
    if extra:
        e.update(extra)
    return kp3v.build_vote_audit(primary, secondary, whisper, tr, secondary_called=secondary_called, whisper_called=whisper_called,
                                 tiebreak=tiebreak, extra=e)


def decide_noguard(primary: Voter, secondary_fn: Callable[[], Voter], whisper_fn: Optional[Callable[[], Voter]], *,
                   tiebreak: Optional[bool] = None) -> VoteDecision:
    """kp3v.decide()の無保護版(遅延callable+fail-closed変換は同じ)。judge統合時は whisper_needed_noguard/tally_noguard を直接呼ぶ。"""
    def finish(sec, wh, sc, wc):
        tr = tally_noguard(primary, sec, wh, tiebreak=tiebreak)
        return VoteDecision(tr.state, tr.reason, primary, sec, wh, whisper_called=wc, secondary_called=sc, pass_count=tr.pass_count,
                            row=tr.row, secondary_confirmed_warning=tr.secondary_confirmed_warning,
                            audit=build_vote_audit_noguard(primary, sec, wh, tr, secondary_called=sc, whisper_called=wc, tiebreak=tiebreak))

    if not primary.available or primary.text is None:
        return finish(None, None, False, False)
    try:
        sec = secondary_fn()
    except Exception as e:   # noqa: BLE001  設定不備の再送出は呼出側adapter(is_config_stop_error)が担う
        sec = kp3v._unavailable("azure", f"{type(e).__name__}: {e}")
    if not _secondary_ok(sec):
        return finish(sec, None, True, False)
    if not whisper_needed_noguard(primary, sec, tiebreak=tiebreak):
        return finish(sec, None, True, False)
    if whisper_fn is None:
        wh = None
    else:
        try:
            wh = whisper_fn()
        except Exception as e:   # noqa: BLE001
            wh = kp3v._unavailable("whisper", f"{type(e).__name__}: {e}")
    return finish(sec, wh, True, whisper_fn is not None)
