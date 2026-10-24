# trial_direct_ledger_phoneme_03_test_01.py -- E2W(fail-closed、OF-OOV-07/08)の単体test。API 0・共有state書込0。
# 実行: .venv\Scripts\python.exe -m pytest docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/trial_direct_ledger_phoneme_03_test_01.py -q
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, ROOT)
import trial_direct_ledger_phoneme_01 as T
import er006_m1_multi_candidate_01 as m1
from trial_direct_ledger_phoneme_02_test_01 import LEDGER, T0, SEG, G, GOT, entry


def w(canonical, asr, whisper, secondary=None, seg=SEG, ledger=LEDGER):
    fz = m1.freeze_candidates(canonical, ledger_snapshot=ledger, segment_started_at=T0)
    return T.judge_e2w(canonical, asr, fz, segment_id=seg, whisper_text=whisper, secondary_asr_text=secondary, ledger=ledger)


# ---- OF-OOV-07: fail-closed ----
def test_whisper_none_rejects():
    r = w(G, GOT, None)
    assert not r["accepted"] and r["reason"] == "E2W_NO_WHISPER_AGREEMENT:WHISPER_UNAVAILABLE"


def test_whisper_empty_rejects():
    assert not w(G, GOT, "")["accepted"]
    assert not w(G, GOT, "   ")["accepted"]


def test_whisper_failure_exception_path_is_none_mapped_to_reject(monkeypatch):
    import er008_disfluency_qa_18 as dq
    import er006_secondary_asr_01 as sec
    def boom(*a, **k): raise RuntimeError("model load fail")
    monkeypatch.setattr(sec.disfluency_qa, "transcribe_verbatim", boom)
    wt = sec._connected_speech_equivalence_local_asr_text("nonexistent.wav")
    assert wt is None                       # 既存Production関数はNoneを返す
    assert not w(G, GOT, wt)["accepted"]    # E2WはNoneを不受理にする


def test_whisper_disagree_other_word_rejects():
    r = w(G, GOT, G.replace("gacha", "gutter"))
    assert not r["accepted"] and r["whisper_state"] == "WHISPER_NO_POSITIVE_AGREEMENT"


def test_whisper_uncertain_no_agreement_is_rejected():
    # 旧: 矛盾しなければ受理(uncertain_no_agreement)。新: 位置の語がLedger読みと一致しなければ不受理
    r = w(G, GOT, G.replace("gacha", "gotta"))
    assert not r["accepted"]


def test_whisper_dropped_word_at_position_rejects():
    r = w(G, GOT, G.replace(" a gacha at", " at"))
    assert not r["accepted"]


# ---- 正の一致 ----
def test_whisper_same_homophone_accepts():
    r = w(G, GOT, GOT)
    assert r["accepted"] and r["whisper_state"] == "AGREE_LEDGER_CMU_PRON" and r["whisper_word"] == "gotcha"


def test_whisper_writes_canonical_accepts():
    r = w(G, GOT, G)
    assert r["accepted"] and r["whisper_state"] == "AGREE_CANONICAL_SPELLING"


def test_whisper_other_ledger_equal_cmu_word_accepts_gatcha_not_in_cmu_rejects():
    assert not w(G, GOT, G.replace("gacha", "gatcha"))["accepted"]  # CMU未収録 -> 一致扱いにしない


# ---- OF-OOV-08: 位置だけで判定(他の箇所の小さな差は無視)、ただし位置が確定しなければ不受理 ----
LONG_C = ("The team opened the lobby and found a gacha near the entrance after lunch, and then everyone moved slowly "
          "toward the stage where the host was waiting with several prizes for the winners.")
LONG_P = LONG_C.replace("gacha", "gotcha")


def test_other_difference_elsewhere_in_whisper_does_not_block():
    wh = LONG_P.replace("slowly", "quickly").replace("several", "seven")   # gacha位置の両隣は一致
    r = w(LONG_C, LONG_P, wh)
    assert r["accepted"], r["reason"]


def test_neighbor_unaligned_rejects_fail_closed():
    wh = LONG_P.replace("found a gotcha near", "found the gotcha next")      # 両隣が崩れる
    r = w(LONG_C, LONG_P, wh)
    assert not r["accepted"] and r["reason"].startswith("E2W_NO_WHISPER_AGREEMENT:WHISPER_")


def test_range_two_words_rejects():
    wh = LONG_P.replace("gotcha", "got you")
    r = w(LONG_C, LONG_P, wh)
    assert not r["accepted"] and "RANGE_NOT_1WORD" in r["reason"]


# ---- OF-183: Azure転写が手元にあり矛盾なら不受理(不受理方向のみ) ----
def test_secondary_contradiction_still_rejects():
    r = w(G, GOT, GOT, secondary=G.replace("unexpected", "expected"))
    assert not r["accepted"]


# ---- E2単独(judge_direct)は変更なし=採用候補でないことの確認 ----
def test_e2_alone_unchanged_accepts_without_independent_evidence():
    fz = m1.freeze_candidates(G, ledger_snapshot=LEDGER, segment_started_at=T0)
    assert T.judge_direct(G, GOT, fz, segment_id=SEG, ledger=LEDGER)["accepted"]
