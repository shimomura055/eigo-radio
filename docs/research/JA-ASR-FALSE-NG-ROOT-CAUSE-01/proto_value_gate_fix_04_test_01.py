import sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import proto_value_gate_fix_04 as F
import er078_asr_unified_judge_01 as uj
import er078_asr_value_guard_01 as vg
import eval_common_02 as E
import er066_ja_asr_orthographic_equivalence_01_cases as c1
import er066_ja_asr_orthographic_equivalence_01_cases_02 as c2


def G(c, a): return F.reading_match_final_gate(c, a).state
def PRE(c, a): return vg.value_guard(c, a, "ja").kind


# ---------------- v3 から継承(基準1〜3の正例・既知負例・警告) ----------------
def test_kana_numeral_notation_pass():
    for c, a in [("体の活動がいちばん低い", "体の活動が一番低い"), ("体の活動が一番低い", "体の活動がいちばん低い"),
                 ("三日間の旅", "みっかかんの旅"), ("四月に会う", "しがつに会う"), ("三人で行く", "さんにんで行く"),
                 ("百円です", "ひゃくえんです"), ("七月に行く", "しちがつに行く"), ("十代の若者", "じゅうだいの若者"),
                 ("三日待った", "みっか待った"), ("三十人で行く", "さんじゅうにんで行く"), ("二百円です", "にひゃくえんです"),
                 ("二十四日に会う", "にじゅうよっかに会う")]:
        assert G(c, a) == "PASS", (c, a, F.reading_match_final_gate(c, a))


def test_ambiguous_kana_numeral_absorbed():
    # 系統スイープで発見: 曖昧かな数詞(いつか=5日 / 'someday')を内包する読み(いつかかん=5日間)は吸収して置換できる
    assert G("それは5日間です", "それはいつかかんです") == "PASS"
    assert G("それはいつかかんです", "それは5日間です") == "PASS"
    assert G("それは5日間です", "それはよっかかんです") == "NG_PROTECTED"


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


def test_warning_preserved_for_registered_kana_numerals():
    for c, a in [("二人で行く", "ふたりで行く"), ("六日に着く", "むいかに着く"), ("3人でついたちに会った", "三人で一日に会った"), ("20歳になった", "はたちになった")]:
        v = F.reading_match_final_gate(c, a)
        assert v.state == "PASS" and "JA_NUMERIC_IRREGULAR_READING" in v.warnings, (c, a, v)


def test_warning_added_for_irregular_kana_notation():
    v = F.reading_match_final_gate("三日間の旅", "みっかかんの旅")
    assert v.state == "PASS" and "JA_NUMERIC_IRREGULAR_READING" in v.warnings, v
    v2 = F.reading_match_final_gate("体の活動が一番低い", "体の活動がいちばん低い")
    assert v2.state == "PASS" and v2.warnings == (), v2


# ---------------- 基準7: 合成負例一式(Opus M-2〜M-5。全件がPASS以外であること) ----------------
# M-2(a): 弱い読み(WEAK_KANA_NUMERALS)は置換候補にならない。v3ではPASSになった実例(F2前=DIFF、置換でinsert扱い+region数詞でUNKNOWN->PASS)
M2_NEG = [("とおくの町で7日", "とおくの町で8日、なのか"), ("とおくの町で7日滞在", "とおくの町で8日滞在なのか"),
          ("とおくの町で8日", "とおくの町で9日、しようか"),
          ("7日に会う。何なのか", "8日に会う。何なのか"), ("8日に会う。どうしようか", "9日に会う。どうしようか")]
# M-3: 長いかな数詞の前半/後半に一致して置換されてはならない(v3は10人/百円/十代/2時でPASS。値が違う)
M3_NEG = [("10人で行く", "さんじゅうにんで行く"), ("百円です", "にひゃくえんです"), ("十代の若者", "にじゅうだいの若者"),
          ("2時に会う", "にじゅうじに会う"), ("三十人で行く", "じゅうにんで行く"),
          ("二百円です", "ひゃくえんです"), ("1日に会う", "じゅういちにちに会う")]
# 誤った音便・連濁(期待読みに無い)
SOKU_NEG = [("3本ください", "さんほんください"), ("3分待つ", "さんふん待つ"), ("8本です", "はちほんです"), ("6歳の子", "ろくさんの子"), ("三日待った", "さんにち待った")]
# 同値atom並び(同じ値のatomが並ぶ文で片方だけ変わる)
TWIN_NEG = [("三人と三人", "さんにんと四人"), ("3日と3日", "みっかと4日"), ("3日と3日", "4日とみっか"), ("三人と三人で", "四人とさんにんで")]
# 否定語近接の数詞
NEGATION_NEG = [("三日間は待たない", "みっかかんは待つ"), ("三日間待たない", "みっかかん待つ"), ("一番ではない", "いちばんである")]


def test_basis7_m2_weak_reads_excluded():
    for c, a in M2_NEG:
        assert PRE(c, a) == "DIFF", (c, a)
        assert G(c, a) == "NG_PROTECTED", (c, a)
    for v, u in [(7, "day"), (8, "day"), (10, "tsu")]:
        assert not (set(F._cand_reads(v, u)) & set(vg.WEAK_KANA_NUMERALS)), (v, u)


def test_basis7_m3_longer_kana_numeral_not_replaced():
    for c, a in M3_NEG:
        assert G(c, a) == "NG_PROTECTED", (c, a, F.value_guard_fixed_detail(c, a)[1])
        _, info = F.value_guard_fixed_detail(c, a)
        assert not info.fired, (c, a, info)


def test_basis7_soku_rendaku_negatives():
    for c, a in SOKU_NEG:
        assert G(c, a) in ("NG_PROTECTED", "DEMOTE_P3"), (c, a)
    assert G("3本ください", "さんぼんください") == "PASS"
    assert G("一分待つ", "いっぷん待つ") in ("PASS", "DEMOTE_P3")


def test_basis7_twin_atoms():
    for c, a in TWIN_NEG:
        assert G(c, a) == "NG_PROTECTED", (c, a)
    assert G("三人と三人", "さんにんと3人") == "PASS"


def test_basis7_negation_adjacent():
    for c, a in NEGATION_NEG:
        assert G(c, a) == "NG_PROTECTED", (c, a)
    assert G("三日間は待たない", "みっかかんは待たない") == "PASS"


def test_basis7_negation_uses_original_text():
    # M-4: negation_diffは置換前の元テキストで判定する(F2の置換後テキストで判定しない)
    import unittest.mock as mock
    seen = []
    orig = uj.negation_diff
    def spy(c, t, lang):
        seen.append((c, t)); return orig(c, t, lang)
    with mock.patch.object(uj, "negation_diff", spy):
        F.reading_match_final_gate("三日間は待たない", "みっかかんは待つ")
    assert seen and all(s == ("三日間は待たない", "みっかかんは待つ") for s in seen), seen


def test_basis7_monotonic_guard_blocks_hijack_even_if_other_layers_disabled():
    # M-2(b): 弱い読みの除外と対象限定(eligibility)を人為的に外しても、単調性ガードがF2前の結果(DIFF)を採用する
    import unittest.mock as mock
    orig_cr = F._cand_reads
    def permissive(v, u):
        return orig_cr(v, u) + (["なのか"] if (v, u) == (7, "day") else [])
    import collections
    with mock.patch.object(F, "_cand_reads", permissive), mock.patch.object(F, "_eligible_budget", lambda p, s: {"7日": 1, "8日": 1}):
        c, a = "とおくの町で7日", "とおくの町で8日、なのか"
        g, info = F.value_guard_fixed_detail(c, a)
        assert g.kind == "DIFF" and not info.fired and info.fallback == "monotonic_guard", (g.kind, info)
        assert G(c, a) == "NG_PROTECTED"
    # v3(凍結)は同じ入力でPASSだった事実の固定(回帰ではなく証跡): v3のhole
    import proto_value_gate_fix_03 as F3
    assert F3.reading_match_final_gate("とおくの町で7日", "とおくの町で8日、なのか").state == "PASS"


def test_basis7_f2_off_for_primary_ng_and_secondary_gates():
    # M-4: kana_unify既定False。引数なしではF2は働かない(純関数)
    c, a = "体の活動が一番低い", "体の活動がいちばん低い"
    g, _ = F.protected(c, a, "ja")
    assert g.kind == "DIFF"
    g2, _ = F.protected(c, a, "ja", kana_unify=True)
    assert g2.kind in ("EQUAL", "NO_VALUES")
    # Primary NG(P1)の6件(v2はここを解除してしまった)は、apply_in_process下でも判定が変わらない
    L = c1.POSITIVE + [(x[0], x[1], x[2]) for x in c2.POSITIVE_02]
    E.api0_guard_on()
    try:
        for i in (25, 27, 29, 42, 43, 44):
            cc, aa = L[i][0], L[i][1]
            b = E.primary_stage(cc, aa, False)
            with F.apply_in_process():
                f = E.primary_stage(cc, aa, False)
            assert (b["state"], b["label"]) == (f["state"], f["label"]) or (b["state"] in uj.PASSING_STATES and f["state"] not in uj.PASSING_STATES and b["label"] in ("PHONETIC_MATCH", "READING_RESOLVED_MATCH")), (i, b, f)
    finally:
        E.api0_guard_off()


def test_existing_guard_hole_is_not_made_worse_by_f2():
    # 既存のvalue_guard(KANA_NUMERALS正規表現に語境界が無い)が『にじゅうよっか』内の『よっか』を4日atomとして拾う既存の穴(F2とは無関係。別OPEN候補)。
    # F2は発動せず、F2前の結果と同一であること(悪化させない)を固定する。
    for c, a in [("4日に会う", "にじゅうよっかに会う"), ("4日に会う", "さんじゅうよっかに会う")]:
        g, info = F.value_guard_fixed_detail(c, a)
        assert not info.fired and g.kind == PRE(c, a) == "EQUAL", (c, a, info, g.kind)   # 既存の穴(Production現行も同じ)。F2は無関与


def test_f2_fired_value_identity():
    # F2が発動した場合、置換されたかな列はunit内で一意な読みで、置換後の表層はpartner atomと同一
    for c, a in [("三日間の旅", "みっかかんの旅"), ("体の活動がいちばん低い", "体の活動が一番低い"), ("百円です", "ひゃくえんです")]:
        g, info = F.value_guard_fixed_detail(c, a)
        assert info.fired and g.kind in ("EQUAL", "NO_VALUES"), (c, a, info, g.kind)
        assert vg.extract_atoms_ja(info.canon2)[0].key() == vg.extract_atoms_ja(info.text2)[0].key()
