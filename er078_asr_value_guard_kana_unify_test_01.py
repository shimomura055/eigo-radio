# JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07A: OPEN-517 F1+F2 / OPEN-523 / OPEN-524 のProduction適用test。mock/純関数のみ・API 0・費用0円。
# 承認済み安全条件(CURRENT_SPEC.md:2855 値・否定の最終ANDゲート)を READING_MATCH PASS にも効かせる不具合是正の固定。合格範囲は狭まるのみ。
# 構成: (1)期待読み表parity (2)F1: READING_MATCH最終ゲート (3)F2: かな数詞表記統一(正例・警告) (4)基準7合成負例(M-2〜M-5, Production関数)
#       (5)OPEN-524 語境界 (6)OPEN-523 弱いかな数詞 (7)basis別/Candidate E/force_secondary/_ortho_unlock_primary (8)rollback定数の復元 (9)静的
import inspect
import re
import unittest.mock as mock

import pytest

import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as ja
import er066_ja_asr_orthographic_equivalence_01_trial as tr
import er078_asr_unified_judge_01 as uj
import er078_asr_value_guard_01 as vg
from er078_asr_unified_judge_01 import AttemptCtx, PrimaryResult, unified_judge


class Sec:
    def __init__(self, text="x"):
        self.text, self.calls = text, 0

    def __call__(self, ctx):
        self.calls += 1
        return self.text


def _ctx(canon, **kw):
    return AttemptCtx(canonical_text=canon, wav_sha256=kw.pop("sha", "sha-A"), audio_seconds=10.0, **kw)


def judge(canon, text, basis="READING_MATCH", label="PHONETIC_MATCH", lang="ja", sec=None, **ctxkw):
    sec = sec or Sec("x")
    r = unified_judge(_ctx(canon, **ctxkw), PrimaryResult(True, text, label=label, equivalence_basis=basis), sec, lang=lang, role="comment")
    return r, sec


def gate(canon, text, **kw):
    """READING_MATCH PASSのPrimary最終ゲート結果を Production関数(unified_judge)で判定: PASS / NG_PROTECTED / DEMOTE_P3。"""
    r, sec = judge(canon, text, **kw)
    if r.reason_code in ("final_gate_value_diff", "final_gate_negation_diff"):
        assert r.state == uj.NG_PROTECTED and sec.calls == 0
        return "NG_PROTECTED"
    if r.audit_record.get("p3_entry") == "primary_pass_demoted_ambiguous_value":
        return "DEMOTE_P3"
    assert r.state in uj.PASSING_STATES and sec.calls == 0, (r.state, r.reason_code)
    return "PASS"


def PRE(c, a):
    return vg.value_guard(c, a, "ja").kind


# ============================================================ (1) 期待読み表parity(R-6)
def test_expected_reading_table_parity_with_trial_cands():
    """移設した表はTrial `_cands` と n=1..20000×全助数詞で完全一致。`expected_reads`との差は『弱い読み除外』『値が一意でない読み除外』のみ=
    実測の意図差分は3件(day:なのか=7・ようか=8、tsu:とお=10)。非一意除外は0件(固定)。"""
    weak_removed, nonuniq_removed = [], []
    for u in vg.COUNTERS:
        rev = {}
        for n in range(1, vg.ER_REV_MAX + 1):
            c = tr._cands(n, u)
            assert vg._er_cands(n, u) == c, (n, u)            # 移設の完全一致
            for r in c:
                if r:
                    rev.setdefault(r, set()).add(n)
        for n in range(1, vg.ER_REV_MAX + 1):
            got = vg.expected_reads(n, u)
            for x in (y for y in tr._cands(n, u) if y):
                if x in vg.WEAK_KANA_NUMERALS:
                    weak_removed.append((u, n, x))
                    assert x not in got
                elif rev[x] != {n}:
                    nonuniq_removed.append((u, n, x))
                    assert x not in got
                else:
                    assert x in got
            assert set(got) <= {y for y in tr._cands(n, u) if y}   # 追加はゼロ
    assert sorted(weak_removed) == [("day", 7, "なのか"), ("day", 8, "ようか"), ("tsu", 10, "とお")]
    assert nonuniq_removed == []


def test_production_module_does_not_import_trial():
    src = inspect.getsource(vg)
    assert "er066_ja_asr_orthographic_equivalence_01_trial" not in re.sub(r"#.*|\"\"\"[\s\S]*?\"\"\"", "", src)


# ============================================================ (2) F1: READING_MATCH PASSにも最終ANDゲート
def test_reading_match_removed_from_approved_bases_and_other_bases_unchanged():
    assert "READING_MATCH" not in uj.APPROVED_EQUIVALENCE_BASES
    assert uj.APPROVED_EQUIVALENCE_BASES == frozenset({"HOMOPHONE_MATCH_NUMBER_EXCEPTION", "TIER1_DIFF_ANCHORED", "TIER1_NUMERIC_EQUIVALENCE"})
    assert uj.READING_MATCH_FINAL_GATE is True and uj.READING_MATCH_BASIS == "READING_MATCH"


KNOWN_NEG = [("三日間の猶予", "三日目の猶予"), ("三日目", "3日間"), ("3~5日待つ", "35日待つ"), ("月のしわ、8,900本超", "月野氏は八万九千本町。"),
             ("8,900本です", "89,000本です"), ("三日待ちます", "さんにち待ちます")]


@pytest.mark.parametrize("canon,asr", KNOWN_NEG)
def test_known_negatives_blocked_by_final_gate(canon, asr):
    assert gate(canon, asr) == "NG_PROTECTED"


def test_reading_match_negation_diff_blocked():
    assert gate("彼女は来ない", "彼女は来る") == "NG_PROTECTED"
    r, _ = judge("彼女は来ない", "彼女は来る")
    assert r.reason_code == "final_gate_negation_diff" and r.audit_record["final_gate"]["applied"] is True


def test_reading_match_ambiguous_demotes_to_p3_and_normal_passes_with_primary_pass_reason():
    assert gate("一分待つ", "いちふん待つ") == "DEMOTE_P3"
    r, sec = judge("今日は晴れ", "きょうは晴れ")
    assert r.state == uj.PASS and r.reason_code == "primary_pass" and sec.calls == 0
    assert r.audit_record["final_gate"]["applied"] is True and "skipped" not in r.audit_record["final_gate"]


def test_other_approved_bases_still_skip_final_gate():
    for basis in sorted(uj.APPROVED_EQUIVALENCE_BASES):
        r, sec = judge("三日間の猶予", "三日目の猶予", basis=basis)
        assert r.state == uj.PASS and sec.calls == 0 and r.audit_record["final_gate"]["skipped"] == f"approved_equivalence:{basis}"
        assert r.reason_code == f"primary_pass_approved_equivalence:{basis}"


def test_en_reading_match_also_final_gated():
    r, sec = judge("He bought 4 books.", "He bought 5 books.", lang="en")
    assert r.state == uj.NG_PROTECTED and r.reason_code == "final_gate_value_diff" and sec.calls == 0


def test_normal_attempts_not_ng():
    for c, a in [("今日は晴れです。", "きょうははれです。"), ("体の活動が一番低い", "体の活動がいちばん低い"), ("三人で行く", "3人で行く"),
                 ("二十歳になりました。", "はたちになりました。"), ("八百屋に行く", "やおやに行く"), ("十分待ちました", "十分待ちました")]:
        assert gate(c, a) in ("PASS", "DEMOTE_P3"), (c, a)
    assert gate("体の活動が一番低い", "体の活動がいちばん低い") == "PASS"


# ============================================================ (3) F2: かな書き数詞の表記統一
def test_kana_numeral_notation_pass():
    for c, a in [("体の活動がいちばん低い", "体の活動が一番低い"), ("体の活動が一番低い", "体の活動がいちばん低い"), ("三日間の旅", "みっかかんの旅"),
                 ("四月に会う", "しがつに会う"), ("三人で行く", "さんにんで行く"), ("百円です", "ひゃくえんです"), ("七月に行く", "しちがつに行く"),
                 ("十代の若者", "じゅうだいの若者"), ("三日待った", "みっか待った"), ("三十人で行く", "さんじゅうにんで行く"),
                 ("二百円です", "にひゃくえんです"), ("二十四日に会う", "にじゅうよっかに会う"), ("24日に会う", "にじゅうよっかに会う")]:
        assert gate(c, a) == "PASS", (c, a)


def test_ambiguous_kana_numeral_absorbed():
    assert gate("それは5日間です", "それはいつかかんです") == "PASS"
    assert gate("それはいつかかんです", "それは5日間です") == "PASS"
    assert gate("それは5日間です", "それはよっかかんです") == "NG_PROTECTED"


def test_wrong_kana_reading_still_ng():
    assert gate("三日待った", "さんにち待った") == "NG_PROTECTED"
    assert gate("一分待つ", "いちふん待つ") == "DEMOTE_P3"


def test_value_change_still_ng():
    for c, a in [("一番低い", "二番低い"), ("一番低い", "にばん低い"), ("三人で行く", "よにんで行く"), ("三日間の旅", "みっかめの旅")]:
        assert gate(c, a) == "NG_PROTECTED", (c, a)


def test_warning_preserved_for_registered_kana_numerals():
    for c, a in [("二人で行く", "ふたりで行く"), ("六日に着く", "むいかに着く"), ("3人でついたちに会った", "三人で一日に会った"), ("20歳になった", "はたちになった")]:
        r, _ = judge(c, a)
        assert r.state == uj.PASS_WITH_WARNING and "JA_NUMERIC_IRREGULAR_READING" in r.warning_labels, (c, a, r.state)


def test_warning_added_for_irregular_kana_notation_via_f2():
    r, _ = judge("三日間の旅", "みっかかんの旅")
    assert r.state == uj.PASS_WITH_WARNING and "JA_NUMERIC_IRREGULAR_READING" in r.warning_labels
    assert r.audit_record["value_guard"]["kana_unify"]["fired"] is True
    r2, _ = judge("体の活動が一番低い", "体の活動がいちばん低い")
    assert r2.state == uj.PASS and r2.warning_labels == [] or r2.warning_labels == ()


def test_f2_fired_value_identity():
    for c, a in [("三日間の旅", "みっかかんの旅"), ("体の活動がいちばん低い", "体の活動が一番低い"), ("百円です", "ひゃくえんです")]:
        g, info = vg.value_guard_kana_unified_detail(c, a)
        assert info.fired and g.kind in ("EQUAL", "NO_VALUES"), (c, a, info)
        assert vg.extract_atoms_ja(info.canon2)[0].key() == vg.extract_atoms_ja(info.text2)[0].key()


# ============================================================ (4) 基準7 合成負例(Opus M-2〜M-5。Production関数で全件PASS以外)
M2_NEG = [("とおくの町で7日", "とおくの町で8日、なのか"), ("とおくの町で7日滞在", "とおくの町で8日滞在なのか"), ("とおくの町で8日", "とおくの町で9日、しようか"),
          ("7日に会う。何なのか", "8日に会う。何なのか"), ("8日に会う。どうしようか", "9日に会う。どうしようか")]
M3_NEG = [("10人で行く", "さんじゅうにんで行く"), ("百円です", "にひゃくえんです"), ("十代の若者", "にじゅうだいの若者"), ("2時に会う", "にじゅうじに会う"),
          ("三十人で行く", "じゅうにんで行く"), ("二百円です", "ひゃくえんです"), ("1日に会う", "じゅういちにちに会う")]
SOKU_NEG = [("3本ください", "さんほんください"), ("3分待つ", "さんふん待つ"), ("8本です", "はちほんです"), ("6歳の子", "ろくさんの子"), ("三日待った", "さんにち待った")]
TWIN_NEG = [("三人と三人", "さんにんと四人"), ("3日と3日", "みっかと4日"), ("3日と3日", "4日とみっか"), ("三人と三人で", "四人とさんにんで")]
NEGATION_NEG = [("三日間は待たない", "みっかかんは待つ"), ("三日間待たない", "みっかかん待つ"), ("一番ではない", "いちばんである")]


def test_basis7_synthetic_negatives_all_blocked():
    n = 0
    for grp in (M2_NEG, M3_NEG, SOKU_NEG, TWIN_NEG, NEGATION_NEG):
        for c, a in grp:
            assert gate(c, a) in ("NG_PROTECTED", "DEMOTE_P3"), (c, a)
            n += 1
    assert n == 24
    for c, a in M2_NEG:
        assert PRE(c, a) == "DIFF", (c, a)
    for c, a in M3_NEG:
        _, info = vg.value_guard_kana_unified_detail(c, a)
        assert not info.fired, (c, a, info)


def test_basis7_positives_alongside():
    assert gate("3本ください", "さんぼんください") == "PASS"
    assert gate("一分待つ", "いっぷん待つ") in ("PASS", "DEMOTE_P3")
    assert gate("三人と三人", "さんにんと3人") == "PASS"
    assert gate("三日間は待たない", "みっかかんは待たない") == "PASS"


def test_m2_weak_reads_excluded_from_candidates():
    for v, u in [(7, "day"), (8, "day"), (10, "tsu")]:
        assert not (set(vg.expected_reads(v, u)) & set(vg.WEAK_KANA_NUMERALS)), (v, u)


def test_m4_f2_off_by_default_and_negation_uses_original_text():
    c, a = "体の活動が一番低い", "体の活動がいちばん低い"
    assert uj._protected(c, a, "ja")[0].kind == "DIFF"                         # 既定=F2なし
    assert uj._protected(c, a, "ja", kana_unify=True)[0].kind in ("EQUAL", "NO_VALUES")
    seen = []
    orig = uj.negation_diff
    with mock.patch.object(uj, "negation_diff", lambda cc, tt, ll: (seen.append((cc, tt)), orig(cc, tt, ll))[1]):
        uj._protected("三日間は待たない", "みっかかんは待つ", "ja", kana_unify=True)
    assert seen == [("三日間は待たない", "みっかかんは待つ")]


def test_m4_primary_ng_and_secondary_gates_do_not_use_f2():
    c, a = "体の活動が一番低い", "体の活動がいちばん低い"
    # Primary NG(P1): 値DIFFで即NG_PROTECTED(F2で解除しない)
    sec = Sec(a)
    r = unified_judge(_ctx(c), PrimaryResult(False, a, label="TRUE_CONTENT_MISMATCH"), sec, lang="ja", role="comment")
    assert r.state == uj.NG_PROTECTED and r.reason_code == "p1_value_diff" and sec.calls == 0
    # Secondary側の_protectedは既定(kana_unify=False)
    calls = []
    orig = uj._protected
    with mock.patch.object(uj, "_protected", lambda *aa, **kk: (calls.append(kk.get("kana_unify", False)), orig(*aa, **kk))[1]):
        judge(c, a)
        unified_judge(_ctx("今日は晴れです。", sha="S2"), PrimaryResult(False, "今日は雨です。", label="TRUE_CONTENT_MISMATCH"), Sec("今日は晴れです。"), lang="ja", role="comment")
    assert calls[0] is True and all(x is False for x in calls[1:])      # READING_MATCH PASSの最終ゲートの1回目だけTrue


def test_m2b_monotonic_guard_blocks_hijack_even_if_other_layers_disabled():
    orig_er = vg.expected_reads
    with mock.patch.object(vg, "expected_reads", lambda v, u: orig_er(v, u) + (["なのか"] if (v, u) == (7, "day") else [])), \
            mock.patch.object(vg, "_eligible_budget", lambda p, s: {"7日": 1, "8日": 1}):
        c, a = "とおくの町で7日", "とおくの町で8日、なのか"
        g, info = vg.value_guard_kana_unified_detail(c, a)
        assert g.kind == "DIFF" and not info.fired and info.fallback == "monotonic_guard", (g.kind, info)
        assert gate(c, a) == "NG_PROTECTED"


# ============================================================ (5) OPEN-524 語境界
def test_open524_kana_numeral_inside_larger_reading_not_equal():
    for c, a in [("4日に会う", "にじゅうよっかに会う"), ("4日に会う", "さんじゅうよっかに会う"), ("にじゅうよっかに会う", "さんじゅうよっかに会う"),
                 ("3日待つ", "みっかかん待つ"), ("14日に会う", "よっかに会う")]:
        assert PRE(c, a) == "DIFF", (c, a)
        assert gate(c, a) == "NG_PROTECTED", (c, a)


def test_open524_correct_readings_unaffected():
    assert PRE("24日に会う", "にじゅうよっかに会う") == "DIFF"            # F2前は従来どおりDIFF(改善は意図しない=合格範囲を広げない)
    assert gate("24日に会う", "にじゅうよっかに会う") == "PASS"           # F2(READING_MATCHの最終ゲート)が既存どおり吸収
    assert PRE("4日に会う", "よっかに会う") == "EQUAL" and PRE("3日", "みっか") == "EQUAL"
    assert PRE("3日間", "みっかかん") == "DIFF"                           # 助数詞違い(F2前は従来どおりDIFF)
    assert PRE("にじゅうよっかに会う", "にじゅうよっかに会う") == "EQUAL"
    assert PRE("ひとりひとり", "ひとりひとり") == "EQUAL"


def test_open524_only_narrows_never_widens():
    # 部分一致印は他atomと一致しない=EQUALをDIFFにするだけで、DIFF/UNKNOWNをEQUALにはしない
    for c, a in [("24日に会う", "にじゅうよっかに会う"), ("34日に会う", "にじゅうよっかに会う"), ("4日", "14日")]:
        with mock.patch.object(vg, "KANA_WORD_BOUNDARY_CHECK", False):
            old = PRE(c, a)
        new = PRE(c, a)
        assert vg._PRIORITY[new] >= vg._PRIORITY[old], (c, a, old, new)


# ============================================================ (6) OPEN-523 弱いかな数詞
def test_open523_weak_kana_does_not_hide_value_drop():
    for c, a in [("6日に会う", "なのかに会う"), ("9日に会う", "ようかに会う"), ("7日に会う", "ようかに会う"), ("10人で行く", "とおで行く"),
                 ("なのかに会う", "6日に会う"), ("11日に会う", "なのかに会う")]:
        assert PRE(c, a) == "DIFF", (c, a)


def test_open523_weak_kana_matching_value_still_unknown_delegated():
    for c, a in [("7日に会う", "なのかに会う"), ("8日に会う", "ようかに会う"), ("十つある", "とおある"), ("なのかに会う", "7日に会う")]:
        assert PRE(c, a) == "UNKNOWN" or PRE(c, a) == "NO_VALUES", (c, a, PRE(c, a))
    assert gate("7日に会う", "なのかに会う") in ("PASS", "DEMOTE_P3")


def test_open523_only_narrows_never_widens():
    for c, a in [("6日に会う", "なのかに会う"), ("7日に会う", "なのかに会う"), ("なのかに会う", "6日に会う"), ("何なのか", "何なのか"), ("9日にしようか", "9日にしようか")]:
        with mock.patch.object(vg, "WEAK_KANA_REGION_COMPAT", False):
            old = PRE(c, a)
        new = PRE(c, a)
        assert vg._PRIORITY[new] >= vg._PRIORITY[old], (c, a, old, new)


def test_open523_ordinary_weak_words_in_both_sides_not_ng():
    for c, a in [("7日に会う。何なのか", "7日に会う。何なのか"), ("今日はどうしようか", "今日はどうしようか"), ("とおくへ行く", "とおくへ行く")]:
        assert PRE(c, a) in ("EQUAL", "NO_VALUES"), (c, a)


# ============================================================ (7) basis別 / Candidate E / force_secondary / ortho
@pytest.mark.parametrize("label", ["PHONETIC_MATCH", "READING_RESOLVED_MATCH"])
def test_both_reading_match_labels_get_f1_and_f2(label):
    assert gate("三日間の猶予", "三日目の猶予", label=label) == "NG_PROTECTED"
    assert gate("三日間の旅", "みっかかんの旅", label=label) == "PASS"
    assert gate("体の活動が一番低い", "体の活動がいちばん低い", label=label) == "PASS"


def test_adapter_maps_phonetic_and_resolved_labels_to_reading_match_basis():
    assert ja._READING_MATCH_CLASSIFICATIONS == ("PHONETIC_MATCH", "READING_RESOLVED_MATCH")
    src = inspect.getsource(ja)
    assert 'basis = "READING_MATCH" if (primary_passed and cls.classification in _READING_MATCH_CLASSIFICATIONS) else None' in src


def test_candidate_e_phonetic_match_value_diff_blocked_via_adapter(monkeypatch):
    # Candidate E(漢字読み総当たり、er011:347-372)由来のPHONETIC_MATCH + 8,900<->89,000相当: adapter実経路で最終ゲートが効く
    monkeypatch.setattr(javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False)
    # 委任_12(OPEN-333 E3): Eの数値entry再検査が同じpairを先に拒否するようになったため、最終Gate(F1)単体を検査するためE3のrollback定数をFalseにする
    # (E3有効時はNG_PROTECTED/p1_value_diffで同じくNG。下の test_candidate_e_value_diff_also_blocked_with_e3_on で固定)。
    import er011_ja_asr_variant_layer_01 as _vl
    monkeypatch.setattr(_vl, "CANDIDATE_E_FULL_DIFF_CHECK", False)
    monkeypatch.setattr(_vl, "CANDIDATE_E_VALUE_GUARD_CHECK", False)
    monkeypatch.setattr(ja, "_azure_stt_strict", lambda *a, **k: (None, "api0_stub"))
    d = ja.evaluate_attempt_ja_with_cascade_detail("月のしわ、8,900本超", "月野氏は八万九千本町。", "dummy.wav", cascade_enabled=True, attempt_ctx={"max_len": 400})
    aj = d["asr_judgement"]
    assert aj["primary"]["equivalence_basis"] == "READING_MATCH" and aj["state"] == uj.NG_PROTECTED and aj["reason_code"] == "final_gate_value_diff"
    assert d["verified"] is False


def test_candidate_e_value_diff_also_blocked_with_e3_on(monkeypatch):
    # 委任_12: E3(既定ON)でも同じ8,900<->89,000相当はNG(Eの段で拒否され NG_PROTECTED/p1_value_diff。PASSには決してならない)
    monkeypatch.setattr(javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False)
    monkeypatch.setattr(ja, "_azure_stt_strict", lambda *a, **k: (None, "api0_stub"))
    d = ja.evaluate_attempt_ja_with_cascade_detail("月のしわ、8,900本超", "月野氏は八万九千本町。", "dummy.wav", cascade_enabled=True, attempt_ctx={"max_len": 400})
    aj = d["asr_judgement"]
    assert aj["state"] == uj.NG_PROTECTED and aj["reason_code"] == "p1_value_diff" and d["verified"] is False
    assert aj["candidate_e_full_diff"]["rejected"] >= 1


def test_force_secondary_path_gets_final_gate_before_secondary():
    sec = Sec("x")
    r = unified_judge(_ctx("三日間の猶予", script_version="v1", force_secondary=True),
                      PrimaryResult(True, "三日目の猶予", label="PHONETIC_MATCH", equivalence_basis="READING_MATCH"), sec, lang="ja", role="x")
    assert r.state == uj.NG_PROTECTED and r.reason_code == "final_gate_value_diff" and sec.calls == 0
    sec2 = Sec("今日は晴れです。")
    r2 = unified_judge(_ctx("今日は晴れです。", sha="Q", script_version="v1", force_secondary=True),
                       PrimaryResult(True, "きょうは晴れです。", label="PHONETIC_MATCH", equivalence_basis="READING_MATCH"), sec2, lang="ja", role="x")
    assert sec2.calls == 1 and r2.state in uj.PASSING_STATES


def test_ortho_unlock_is_not_applied_to_ja_reading_match():
    r, _ = judge("三日間の猶予", "三日目の猶予")
    assert r.state == uj.NG_PROTECTED and "span_unlock" not in r.audit_record["final_gate"]
    assert uj._ortho_unlock_primary(PrimaryResult(True, "x", equivalence_basis="READING_MATCH"), "a", "b", None, False, "ja", {}) is None


# ============================================================ (8) rollback定数(1行で現行挙動を完全復元)
def test_rollback_reading_match_final_gate_false_restores_previous_behavior(monkeypatch):
    monkeypatch.setattr(uj, "READING_MATCH_FINAL_GATE", False)
    for c, a in KNOWN_NEG[:4]:
        r, sec = judge(c, a)
        assert r.state == uj.PASS and sec.calls == 0
        assert r.audit_record["final_gate"]["skipped"] == "approved_equivalence:READING_MATCH"
        assert r.reason_code == "primary_pass_approved_equivalence:READING_MATCH"
    # F2も無効(kana_unifyを渡さない)
    calls = []
    orig = uj._protected
    monkeypatch.setattr(uj, "_protected", lambda *aa, **kk: (calls.append(kk.get("kana_unify", False)), orig(*aa, **kk))[1])
    judge("三日間の旅", "みっかかんの旅")
    assert calls == [False]


def test_rollback_open523_524_constants_restore_previous_guard(monkeypatch):
    monkeypatch.setattr(vg, "KANA_WORD_BOUNDARY_CHECK", False)
    assert PRE("4日に会う", "にじゅうよっかに会う") == "EQUAL"
    monkeypatch.setattr(vg, "WEAK_KANA_REGION_COMPAT", False)
    assert PRE("6日に会う", "なのかに会う") == "UNKNOWN"


def test_rollback_constants_are_plain_module_constants_not_env():
    src = inspect.getsource(uj) + inspect.getsource(vg)
    assert re.search(r"^READING_MATCH_FINAL_GATE = True$", src, re.M)
    assert re.search(r"^KANA_WORD_BOUNDARY_CHECK = True$", src, re.M) and re.search(r"^WEAK_KANA_REGION_COMPAT = True$", src, re.M)
    for name in ("READING_MATCH_FINAL_GATE", "KANA_WORD_BOUNDARY_CHECK", "WEAK_KANA_REGION_COMPAT"):
        assert not re.search(r"(environ|getenv)[^\n]*" + name, src)


# ============================================================ (9) 決定性・純関数
def test_deterministic_and_pure():
    a = vg.value_guard_kana_unified_detail("三日間の旅", "みっかかんの旅")
    b = vg.value_guard_kana_unified_detail("三日間の旅", "みっかかんの旅")
    assert a[0].to_dict() == b[0].to_dict() and a[1] == b[1]
    assert vg.unify_kana_numerals("いちばん", "一番") == vg.unify_kana_numerals("いちばん", "一番")
    assert vg.value_guard_kana_unified("The rate is 25%", "The rate is 26%", "en").kind == "DIFF"
