# -*- coding: utf-8 -*-
"""M1複数発音候補の配線test(ASR-M1-OOV-MULTI-PRONUNCIATION-PRODUCTION-01 委任_03)。
API 0 / 有料呼出なし。ASR(routing.transcribe / Azure)はmock、LedgerはREAD専用snapshotをpatch。
対象: er006_secondary_asr_01.evaluate_attempt_with_cascade_detail の各挿入点。"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.getcwd())
import er006_m1_multi_candidate_01 as M  # noqa: E402
import er006_secondary_asr_01 as sec  # noqa: E402

LED = json.load(open("er006_output/pronunciation_ledger_01/ledger.json", encoding="utf-8"))
CANON = "Melos said."
HIT = "Mello said."       # M1が受理する転写
MISS = "Marcus said."     # entity_like UNCERTAINだがM1不受理


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    sec._reset_m1_freeze_cache()
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda: LED)
    yield
    sec._reset_m1_freeze_cache()


class Calls:
    def __init__(self, monkeypatch, p2=None, s=None):
        self.p2 = p2
        self.s = list(s or [])
        self.n_p2 = 0
        self.n_az = 0
        monkeypatch.setattr(sec.routing, "transcribe", self._p2)
        monkeypatch.setattr(sec, "get_full_text_via_azure_stt_with_phrase_list", self._az)

    def _p2(self, wav, language="en-US"):
        self.n_p2 += 1
        return self.p2, None

    def _az(self, wav, language="en-US", phrases=None):
        self.n_az += 1
        t = self.s.pop(0) if self.s else None
        return t, None


def run(asr, canon=CANON, **kw):
    kw.setdefault("cascade_enabled", True)
    return sec.evaluate_attempt_with_cascade_detail(canon, asr, [], "dummy.wav", **kw)


def test_primary1_fires_no_extra_asr(monkeypatch):
    c = Calls(monkeypatch)
    d = run(HIT)
    assert d["verified"] and d["final_status"] == M.ACCEPT_REASON
    au = d["m1_multi_candidate"]
    assert au["step"] == "primary_1" and au["m1_layer_invoked"] is True and au["candidate_set_hash"]
    assert c.n_p2 == 0 and c.n_az == 0  # 追加ASR 0(コスト0)
    assert d["steps"][-1]["step"] == "m1_multi_candidate"
    assert d["human_review_required"] is False


def test_audit_has_traceability_fields(monkeypatch):
    Calls(monkeypatch)
    au = run(HIT)["m1_multi_candidate"]
    for k in ("candidate_set_hash", "secondary_agree", "step", "reason"):
        assert k in au


def test_primary2_fires(monkeypatch):
    # AUW 委任_03b: DESIGN_01 §4-9 / ユーザー原文「Primary NG→原則Secondary」に追随(旧: Primary#2(同一音声のOpenAI再転写)で
    # M1が受理され step=primary_2 でPASS)。新設計: Primary#2は廃止(routing.transcribeは呼ばれない)。
    # 安全側の意図(M1受理は独立した転写でのみ起きる/Primary不受理をPrimary再転写でPASSにしない)は、
    # 「Primary#2相当の転写があっても使わない」「Secondary転写がHITなら secondary_1 でM1受理」で残す。
    c = Calls(monkeypatch, p2=HIT)
    d = run(MISS)
    assert c.n_p2 == 0, "Primary#2は廃止"
    assert not d["verified"] and d["asr_judgement"]["state"] == "NG_SECONDARY_UNAVAILABLE"  # Secondary未取得=PASS不可
    assert d["m1_multi_candidate_rejected"][0]["step"] == "primary_1"  # 不受理も到達証跡
    assert d["m1_multi_candidate_rejected"][0]["m1_layer_invoked"] is True
    c2 = Calls(monkeypatch, p2=HIT, s=[HIT])
    d2 = run(MISS)
    assert d2["verified"] and d2["m1_multi_candidate"]["step"] == "secondary_1"
    assert c2.n_p2 == 0 and c2.n_az == 1


def test_secondary1_fires_with_other_transcript(monkeypatch):
    seen = []
    real = M.m1_multi_candidate_judge

    def spy(*a, **k):
        seen.append(k.get("secondary_asr_text"))
        return real(*a, **k)

    monkeypatch.setattr(sec.m1_multi, "m1_multi_candidate_judge", spy)
    c = Calls(monkeypatch, p2=MISS, s=[HIT])
    d = run(MISS)
    assert d["verified"] and d["m1_multi_candidate"]["step"] == "secondary_1"
    assert c.n_az == 1
    assert seen[-1] == MISS  # 手元にある他方(Primary#1転写)を矛盾検査用に渡す


def test_secondary2_fires(monkeypatch):
    # AUW 委任_03b: DESIGN_01 §4-9 / ユーザー原文「重複呼出防止」に追随(旧: Secondary#1がMISSならSecondary#2を呼びM1受理 step=secondary_2)。
    # 新設計: Secondaryは1回のみ(#2廃止)。Secondary#1がMISSならNG(次slotで再生成)。#2のHITは消費されない。
    c = Calls(monkeypatch, p2=MISS, s=[MISS, HIT])
    d = run(MISS)
    assert not d["verified"]
    assert c.n_az == 1, "Secondaryは1回のみ"
    assert c.n_p2 == 0
    assert "m1_multi_candidate" not in d


def test_all_miss_goes_to_human_review_unchanged(monkeypatch):
    # AUW 委任_03b: DESIGN_01 §4-3/§4-9 / ユーザー原文「両NGで再生成→3回NGでLR/HR」に追随
    # (旧: 4 step全MISSで即HR+stop_retrying、M1到達4 step)。新設計: Primary+Secondary 1回の2 stepでM1到達、
    # 途中slotはHR/stop_retryingにせず次slotで再生成、最終slot NGのみHR(安全側の最終出口は維持)。
    monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review", lambda span: None)  # Ledger/Perplexity実呼出を防ぐ
    Calls(monkeypatch, p2=MISS, s=[MISS, MISS])
    d = run(MISS)
    assert not d["verified"] and not d["human_review_required"] and not d["stop_retrying"]
    assert d["final_status"] == "ASR_VALIDATION_UNCERTAIN"
    assert len(d["m1_multi_candidate_rejected"]) == 2  # primary_1 + secondary_1 でM1到達
    Calls(monkeypatch, p2=MISS, s=[MISS, MISS])
    d3 = run(MISS, attempt_ctx={"slot": 3, "is_last_slot": True})
    assert not d3["verified"] and d3["human_review_required"]
    assert d3["final_status"] == "ASR_VALIDATION_UNCERTAIN"


def test_forced_secondary_m1_keeps_pass(monkeypatch):
    c = Calls(monkeypatch, s=[HIT])
    d = run("Melos said.", force_secondary=True)  # PrimaryはEXACT PASS、SecondaryがMello
    assert d["verified"] and not d["human_review_required"]
    assert d["m1_multi_candidate"]["step"] == "secondary_forced"
    assert c.n_az == 1


def test_forced_secondary_unexplained_still_hr(monkeypatch):
    # AUW 委任_03b: DESIGN_01 §4-7に追随(旧: Secondary不同意で即HR)。新設計: HRは最終slot NGのみ(途中slotは次slotで再生成)。
    # 説明できないSecondary転写をPASS扱いしない安全側は不変。
    monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review", lambda span: None)
    Calls(monkeypatch, s=[MISS])
    d = run("Melos said.", force_secondary=True)
    assert not d["verified"] and not d["human_review_required"]
    Calls(monkeypatch, s=[MISS])
    d3 = run("Melos said.", force_secondary=True, attempt_ctx={"slot": 3, "is_last_slot": True})
    assert not d3["verified"] and d3["human_review_required"]


def test_forced_secondary_contradiction_rejects(monkeypatch):
    real = M.m1_multi_candidate_judge

    def contra(*a, **k):
        r = real(*a, **k)
        assert k.get("secondary_asr_text") == "Melos said."  # Primary転写を渡している
        r.accepted, r.reason = False, M.R_SECONDARY_CONTRADICTION
        r.audit["no_match_reason"] = "contradiction:protected_fail"
        return r

    monkeypatch.setattr(sec.m1_multi, "m1_multi_candidate_judge", contra)
    monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review", lambda span: None)
    Calls(monkeypatch, s=[HIT])
    d = run("Melos said.", force_secondary=True)
    # AUW 委任_03b: DESIGN_01 §4-7に追随(旧: ここで即human_review_required)。新設計: HRは最終slot NGのみ。矛盾拒否(誤受理0)は不変。
    assert not d["verified"] and not d["human_review_required"]
    assert d["m1_multi_candidate_rejected"][0]["reason"] == M.R_SECONDARY_CONTRADICTION
    Calls(monkeypatch, s=[HIT])
    d3 = run("Melos said.", force_secondary=True, attempt_ctx={"slot": 3, "is_last_slot": True})
    assert not d3["verified"] and d3["human_review_required"]


def test_cascade_disabled_never_fires(monkeypatch):
    c = Calls(monkeypatch)
    d = run(HIT, cascade_enabled=False)
    assert not d["verified"] and "m1_multi_candidate" not in d and not d.get("m1_multi_candidate_rejected")
    assert c.n_p2 == 0 and c.n_az == 0
    assert sec._M1_FROZEN_CACHE == {}  # 凍結も作らない


def test_m1_enabled_false_restores_legacy(monkeypatch):
    # AUW 委任_03b: DESIGN_01 §4-9に追随(旧: m1_enabled=Falseで4 step消費後に即HR)。新設計: m1_enabled=FalseでもM1経路は不発
    # (m1_multi_candidate無し・M1でPASSしない)、Secondaryは1回のみ。HRは最終slot NGのみ。
    monkeypatch.setattr(sec, "_resolve_unresolved_entity_for_review", lambda span: None)
    c = Calls(monkeypatch, p2=HIT, s=[HIT, HIT])
    d = run(HIT, m1_enabled=False)
    assert not d["verified"] and not d["human_review_required"] and "m1_multi_candidate" not in d
    assert c.n_p2 == 0 and c.n_az == 1
    Calls(monkeypatch, p2=HIT, s=[HIT, HIT])
    d3 = run(HIT, m1_enabled=False, attempt_ctx={"slot": 3, "is_last_slot": True})
    assert not d3["verified"] and d3["human_review_required"] and "m1_multi_candidate" not in d3


def test_non_en_us_never_fires(monkeypatch):
    Calls(monkeypatch, p2=HIT, s=[HIT, HIT])
    d = run(HIT, language="ja-JP")
    assert "m1_multi_candidate" not in d and not d["verified"]


def test_freeze_reused_across_retries(monkeypatch):
    Calls(monkeypatch)
    h1 = run(HIT)["m1_multi_candidate"]["candidate_set_hash"]
    # Ledgerが変わっても(Tier3 upsert等)同一segmentでは凍結物を再利用
    monkeypatch.setattr(sec.pronun_ledger, "_load", lambda: {"entries": {}})
    h2 = run(HIT)["m1_multi_candidate"]["candidate_set_hash"]
    assert h1 == h2
    sec._reset_m1_freeze_cache()  # 新segment相当
    d3 = run(HIT)
    assert "m1_multi_candidate" not in d3  # 空snapshot=候補なし


def test_freeze_failure_is_fail_closed(monkeypatch):
    def boom(*a, **k):
        raise OSError("x")
    monkeypatch.setattr(sec.m1_multi, "freeze_candidates", boom)
    Calls(monkeypatch, p2=HIT, s=[HIT, HIT])
    d = run(HIT)
    assert not d["verified"] and "m1_multi_candidate" not in d  # 従来挙動(HR)


def test_exact_match_label_has_priority(monkeypatch):
    spy = []
    monkeypatch.setattr(sec.m1_multi, "m1_multi_candidate_judge", lambda *a, **k: spy.append(1))
    Calls(monkeypatch)
    d = run("Melos said.")  # EXACT_MATCH
    assert d["verified"] and d["final_status"] == "EXACT_MATCH" and not spy


def test_case_a_label_before_m1(monkeypatch):
    spy = []
    real = M.m1_multi_candidate_judge
    monkeypatch.setattr(sec.m1_multi, "m1_multi_candidate_judge",
                        lambda *a, **k: (spy.append(1), real(*a, **k))[1])
    Calls(monkeypatch)
    d = run("Kristie said.", canon="Christie said.")
    assert d["final_status"] != M.ACCEPT_REASON
    assert d["verified"] and not spy  # 既存ラベル(Case A/homophone)が先に成立しM1は不発


def test_f1_content_residual_blocks_m1(monkeypatch):
    # 内容語差分(said->went)が残る場合、Melos近似一致でもM1は不発(非PASS)
    Calls(monkeypatch, p2="Mello went.", s=["Mello went.", "Mello went."])
    d = run("Mello went.")
    assert not d["verified"] and "m1_multi_candidate" not in d


def test_negation_number_not_in_scope(monkeypatch):
    Calls(monkeypatch, p2="Mello did wait five days.", s=["x", "x"])
    d = run("Mello did wait five days.", canon="Melos did not wait five days.")
    assert not d["verified"] and "m1_multi_candidate" not in d


def test_kp_path_uses_same_cascade(monkeypatch):
    Calls(monkeypatch)
    d = run(HIT, enable_non_latin_cascade=True)  # KP経路フラグ。m1_enabled既定True
    assert d["verified"] and d["m1_multi_candidate"]["step"] == "primary_1"


def test_dialogue_and_point_headings_segment_id_none(monkeypatch):
    Calls(monkeypatch)
    d = run(HIT, segment_id=None)
    assert d["verified"] and d["m1_multi_candidate"]["candidate_set_hash"]
    sec._reset_m1_freeze_cache()
    d2 = run(HIT, segment_id="full_story_part1")
    assert d2["m1_multi_candidate"]["candidate_set_hash"] == d["m1_multi_candidate"]["candidate_set_hash"]


def test_post_slowdown_rescue_keeps_m1_audit(monkeypatch):
    import er003_v1_n3_01_tts_generate as g
    Calls(monkeypatch)
    res = {}
    ok = g._post_slowdown_cascade_rescue(res, CANON, HIT, sec.val.classify_asr_match(CANON, HIT),
                                         "dummy.wav", "full_story_part1")
    assert ok is True
    p = res["post_slowdown_cascade"]
    assert p["verified"] and p["final_status"] == M.ACCEPT_REASON
    assert any(s["step"] == "m1_multi_candidate" for s in p["steps"])


def test_wrapper_passes_m1_enabled(monkeypatch):
    Calls(monkeypatch, p2=HIT, s=[HIT, HIT])
    monkeypatch.setattr(sec, "_log_human_review", lambda d: None)
    out = {}
    v, st, cls = sec.evaluate_attempt_with_cascade(CANON, HIT, [], "d.wav", cascade_enabled=True,
                                                   detail_out=out, m1_enabled=False)
    assert not v
    sec._reset_m1_freeze_cache()
    v, st, cls = sec.evaluate_attempt_with_cascade(CANON, HIT, [], "d.wav", cascade_enabled=True, detail_out=out)
    assert v and out["final_status"] == M.ACCEPT_REASON
