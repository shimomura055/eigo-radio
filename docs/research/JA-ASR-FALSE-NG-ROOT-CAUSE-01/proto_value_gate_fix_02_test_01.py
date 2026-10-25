import sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import proto_value_gate_fix_02 as F
import er078_asr_unified_judge_01 as uj

def G(c, a): return F.reading_match_final_gate(c, a).state

def test_kana_numeral_notation_pass():
    for c, a in [("体の活動がいちばん低い", "体の活動が一番低い"), ("体の活動が一番低い", "体の活動がいちばん低い"),
                 ("三日間の旅", "みっかかんの旅"), ("四月に会う", "しがつに会う"), ("三人で行く", "さんにんで行く"),
                 ("百円です", "ひゃくえんです"), ("七月に行く", "しちがつに行く"), ("十代の若者", "じゅうだいの若者"),
                 ("三日待った", "みっか待った")]:
        assert G(c, a) == "PASS", (c, a, F.reading_match_final_gate(c, a))

def test_wrong_kana_reading_still_ng():
    assert G("三日待った", "さんにち待った") == "NG_PROTECTED"
    assert G("一分待つ", "いちふん待つ") == "DEMOTE_P3"

def test_value_change_still_ng():
    assert G("一番低い", "二番低い") == "NG_PROTECTED"
    assert G("一番低い", "にばん低い") == "NG_PROTECTED"
    assert G("三人で行く", "よにんで行く") == "NG_PROTECTED"
    assert G("三日間の旅", "みっかめの旅") == "NG_PROTECTED"

def test_known_negatives():
    for c, a in [("三日間の猶予", "三日目の猶予"), ("三日目", "3日間"), ("3~5日待つ", "35日待つ"), ("月のしわ、8,900本超", "月野氏は八万九千本町。")]:
        assert G(c, a) == "NG_PROTECTED", (c, a)

def test_negation_and_normal():
    assert G("彼女は来ない", "彼女は来る") == "NG_PROTECTED"
    assert G("三人で行く", "3人で行く") == "PASS" and G("今日は晴れ", "きょうは晴れ") == "PASS"

def test_deterministic_and_restores():
    b, p = uj.APPROVED_EQUIVALENCE_BASES, uj._protected
    with F.apply_in_process():
        assert "READING_MATCH" not in uj.APPROVED_EQUIVALENCE_BASES
    assert uj.APPROVED_EQUIVALENCE_BASES is b and uj._protected is p
    assert F.unify_kana_numerals("いちばん", "一番") == F.unify_kana_numerals("いちばん", "一番")
