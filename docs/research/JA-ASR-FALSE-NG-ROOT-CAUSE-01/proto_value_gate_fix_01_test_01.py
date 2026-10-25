import sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import proto_value_gate_fix_01 as F
import er078_asr_unified_judge_01 as uj

def test_f2_canonicalize():
    assert F.canonicalize_kana_counter("活動がいちばん低い") == "活動が一番低い"
    assert F.canonicalize_kana_counter("にどと") == "二度と"
    assert F.canonicalize_kana_counter("よんばん") == "四番" and F.canonicalize_kana_counter("きゅうど") == "九度"
    assert F.canonicalize_kana_counter("みっか") == "みっか"            # 不規則助数詞は対象外
    assert F.canonicalize_kana_counter("いっかい") == "いっかい"

def test_ichiban_not_false_ng():
    v = F.reading_match_final_gate("体の活動がいちばん低い", "体の活動が一番低い")
    assert v.state == "PASS", v
    assert F.reading_match_final_gate("体の活動が一番低い", "体の活動がいちばん低い").state == "PASS"
    assert F.reading_match_final_gate("体の活動がいちばん低い", "体の活動が一番低い", fix_f2=False).state == "NG_PROTECTED"  # F2なしでは誤NG(再現)

def test_f2_does_not_hide_value_change():
    assert F.reading_match_final_gate("一番低い", "二番低い").state == "NG_PROTECTED"
    assert F.reading_match_final_gate("いちばん低い", "にばん低い").state == "NG_PROTECTED"
    assert F.reading_match_final_gate("一度だけ", "二度だけ").state == "NG_PROTECTED"

def test_known_negatives_ng():
    for c, a in [("三日間の猶予", "三日目の猶予"), ("三日目", "3日間"), ("3~5日待つ", "35日待つ"),
                 ("三日待った", "さんにち待った"), ("月のしわ、8,900本超", "月野氏は八万九千本町。")]:
        assert F.reading_match_final_gate(c, a).state == "NG_PROTECTED", (c, a)
    assert F.reading_match_final_gate("一分待つ", "いちふん待つ").state == "DEMOTE_P3"

def test_negation():
    assert F.reading_match_final_gate("彼女は来ない", "彼女は来る").state == "NG_PROTECTED"

def test_normal_equal():
    assert F.reading_match_final_gate("三人で行く", "3人で行く").state == "PASS"
    assert F.reading_match_final_gate("今日は晴れ", "きょうは晴れ").state == "PASS"

def test_apply_in_process_restores():
    b, p = uj.APPROVED_EQUIVALENCE_BASES, uj._protected
    with F.apply_in_process():
        assert "READING_MATCH" not in uj.APPROVED_EQUIVALENCE_BASES
    assert uj.APPROVED_EQUIVALENCE_BASES is b and uj._protected is p   # 2026-10-25(07A): READING_MATCHはProduction適用済みで元から集合に無い

def test_idempotent():
    s = "いちばん一番にどと"
    assert F.canonicalize_kana_counter(F.canonicalize_kana_counter(s)) == F.canonicalize_kana_counter(s)
