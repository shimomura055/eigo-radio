# AUW 委任_02b: 値ガード(er078_asr_value_guard_01)のUnit test。API 0。
# 期待値の正本: DESIGN_01 §5-7(9例)+追加固定ケース、DESIGN_02_ADDENDUM_01 §1-2/§1-6、Fable補正("one")。
import pytest

import er078_asr_value_guard_01 as vg
from er078_asr_value_guard_01 import value_guard as g

EQ, DF, AM, UK, NV = vg.EQUAL, vg.DIFF, vg.AMBIGUOUS, vg.UNKNOWN, vg.NO_VALUES

# (id, lang, src, hyp, expected)
NINE_EXAMPLES = [
    ("1_三人_3人", "ja", "三人で行きました。", "3人で行きました。", EQ),
    ("2_三人_四人", "ja", "三人で行きました。", "四人で行きました。", DF),
    ("3_三十人_30人", "ja", "三十人が来ました。", "30人が来ました。", EQ),
    ("4_三十人_40人", "ja", "三十人が来ました。", "40人が来ました。", DF),
    ("5a_十分_10分_マーカーなし", "ja", "十分待ちました。", "10分待ちました。", AM),
    ("5b_十分間_10分間_マーカーあり", "ja", "十分間待ちました。", "10分間待ちました。", EQ),
    ("5c_三十分_30分", "ja", "三十分待ちました。", "30分待ちました。", EQ),
    ("6_100円_百円", "ja", "100円でした。", "百円でした。", EQ),
    ("7a_EN_20%_20percent", "en", "The rate is 20% today.", "The rate is 20 percent today.", EQ),
    ("7b_JA_20%_20パーセント", "ja", "20％の人が来ました。", "20パーセントの人が来ました。", EQ),
    ("8_EN_20%_30%", "en", "The rate is 20% today.", "The rate is 30% today.", DF),
    ("8_JA_20%_30%", "ja", "20％の人が来ました。", "30％の人が来ました。", DF),
    ("9_EN_25%_26%", "en", "The rate is 25% today.", "The rate is 26% today.", DF),
    ("9_JA_25%_26%", "ja", "25％の人が来ました。", "26％の人が来ました。", DF),
]

ADDENDUM_1_6 = [
    ("一人で/ひとりで", "ja", "一人で行きます。", "ひとりで行きます。", EQ),
    ("一つ/ひとつ", "ja", "一つ選びます。", "ひとつ選びます。", EQ),
    ("二十歳/はたち", "ja", "二十歳になりました。", "はたちになりました。", EQ),
    ("二〇二六年/2026年", "ja", "二〇二六年に始まりました。", "2026年に始まりました。", EQ),
    ("1万2000人/一万二千人", "ja", "1万2000人が来ました。", "一万二千人が来ました。", EQ),
    ("数十人/十数人", "ja", "数十人が来ました。", "十数人が来ました。", DF),
    ("十分な/充分な(単独)", "ja", "十分な量です。", "充分な量です。", AM),
    ("3分の1/3分の1(同表層)", "ja", "3分の1になりました。", "3分の1になりました。", EQ),
    ("3分の1/1/3(構文不一致)", "ja", "3分の1になりました。", "1/3になりました。", UK),
    ("EN for->4", "en", "He waited for the bus.", "He waited 4 the bus.", AM),
    ("EN 4->for", "en", "He bought 4 books.", "He bought for books.", AM),
    ("3〜5日/35日(OPEN-334)", "ja", "3〜5日かかります。", "35日かかります。", DF),
    ("3人/3日(助数詞違い)", "ja", "3人来ました。", "3日来ました。", DF),
    ("2026年/二千二十六年", "ja", "2026年です。", "二千二十六年です。", EQ),
    ("3,000円/三千円", "ja", "3,000円です。", "三千円です。", EQ),
    ("EN 5/$5", "en", "It costs 5 today.", "It costs $5 today.", DF),
    ("EN 5/5%", "en", "It grew 5 today.", "It grew 5% today.", DF),
    ("EN 28/28th", "en", "On 28 people left.", "On 28th people left.", DF),
    ("1.5倍/1.6倍", "ja", "1.5倍になりました。", "1.6倍になりました。", DF),
    ("JA 欠落 三人/数字なし", "ja", "三人で行きました。", "で行きました。", DF),
    ("JA 追加 数字なし/三人", "ja", "で行きました。", "三人で行きました。", DF),
    ("JA 値なし", "ja", "これは本です。", "これは本です。", NV),
    ("EN 値なし", "en", "This is a book.", "This is a book.", NV),
    ("EN 4 vs 5", "en", "There are four people here.", "There are five people here.", DF),
    ("EN twenty-five/25", "en", "There were twenty-five people.", "There were 25 people.", EQ),
    ("EN 単位違い 3 hours/3 days", "en", "It took 3 hours.", "It took 3 days.", DF),
]

# Fable補正: "one"
ONE_CASES = [
    ("one脱落(代名詞的)", "en", "One of the students left.", "Of the students left.", UK),
    ("one挿入", "en", "The students left.", "One of the students left.", UK),
    ("one脱落(冠詞的)", "en", "I have one apple.", "I have apple.", UK),
    ("one vs two(明確な数量: 相手側に別の数詞)", "en", "I have one apple.", "I have two apple.", DF),
    ("one vs 2", "en", "I have one apple.", "I have 2 apple.", DF),
    ("one vs 1(同値)", "en", "I have one apple.", "I have 1 apple.", EQ),
]


@pytest.mark.parametrize("cid,lang,src,hyp,exp", NINE_EXAMPLES, ids=[c[0] for c in NINE_EXAMPLES])
def test_user_nine_examples(cid, lang, src, hyp, exp):
    assert g(src, hyp, lang).kind == exp


@pytest.mark.parametrize("cid,lang,src,hyp,exp", ADDENDUM_1_6, ids=[c[0] for c in ADDENDUM_1_6])
def test_addendum_patterns(cid, lang, src, hyp, exp):
    assert g(src, hyp, lang).kind == exp


@pytest.mark.parametrize("cid,lang,src,hyp,exp", ONE_CASES, ids=[c[0] for c in ONE_CASES])
def test_fable_correction_one(cid, lang, src, hyp, exp):
    r = g(src, hyp, lang)
    assert r.kind == exp
    if exp == UK:
        assert r.kind != DF  # DIFF(b)へ流用しない


def test_juubun_closed_markers_all_resolve_to_time():
    for mk in vg.JUUBUN_TIME_MARKERS:
        assert g(f"{mk}待ちました。", "10" + mk[1:] + "待ちました。", "ja").kind == EQ, mk
    # マーカー外(な/に/だ/で/以上/以内)は機械的に同値化しない
    for tail in ("な", "に", "だ", "で", "以上", "以内"):
        assert g(f"十分{tail}。", f"10分{tail}。", "ja").kind == AM, tail


def test_juubun_with_other_difference_is_not_rescued_by_ambiguous_alone():
    r = g("十分な量と三人です。", "充分な量と四人です。", "ja")
    assert r.kind == DF  # 別箇所のDIFFが優先(AMBIGUOUSは単独で救済しない)


def test_aggregation_priority():
    assert vg.aggregate([EQ, AM, UK, DF]) == DF
    assert vg.aggregate([EQ, AM, UK]) == UK
    assert vg.aggregate([EQ, AM]) == AM
    assert vg.aggregate([EQ, EQ]) == EQ
    assert vg.aggregate([]) == NV


def test_irregular_reading_warning_flag():
    assert vg.WARN_IRREGULAR_READING in g("二十歳になった。", "はたちになった。", "ja").warnings
    assert vg.WARN_IRREGULAR_READING in g("一人で。", "ひとりで。", "ja").warnings
    assert g("三十人。", "30人。", "ja").warnings == ()  # 規則読みは警告なし


def test_unit_mismatch_between_bare_and_counter():
    # 助数詞辞書外(メートル)の裸数字と辞書内助数詞(キロ)は単位が片側のみ判定できる -> 値ガードでは結論を出さずUNKNOWN(既存判定へ委譲)
    assert g("3メートル。", "3キロ。", "ja").kind == UK
    assert g("3人来ました。", "4キロ来ました。", "ja").kind == DF


def test_unparseable_span_is_unknown_not_silent():
    assert g("万人が来ました。", "10000人が来ました。", "ja").kind == UK


def test_unsupported_lang_raises():
    with pytest.raises(ValueError):
        g("a", "b", "fr")


def test_pure_and_deterministic():
    a = g("三人で行きました。", "3人で行きました。", "ja").to_dict()
    b = g("三人で行きました。", "3人で行きました。", "ja").to_dict()
    assert a == b


# ---- Production同一前処理後の原稿(tts_safe_number_words_en: 2〜12の数詞語を算用数字へ) ----
def test_en_production_preprocessed_manuscript():
    import er003_v1_n3_01_tts_generate as n3
    canon = "We saw three people and ten cars."
    pre = n3.tts_safe_number_words_en(canon)
    assert pre == "We saw 3 people and 10 cars."
    assert g(pre, "We saw three people and ten cars.", "en").kind == EQ
    assert g(pre, "We saw four people and ten cars.", "en").kind == DF
    assert g(pre, "We saw people and ten cars.", "en").kind == DF  # 脱落


def test_en_percent_variants_after_preprocess():
    import er003_v1_n3_01_tts_generate as n3
    pre = n3.tts_safe_number_words_en("Prices rose five percent.")
    assert pre == "Prices rose 5 percent."
    assert g(pre, "Prices rose 5%.", "en").kind == EQ
    assert g(pre, "Prices rose 6%.", "en").kind == DF


# ---- 再利用元との突合(parity)。Trial moduleはtest側のみがimport(Production→Trial importは作らない) ----
def test_parity_er066_spans_and_irregular():
    import er066_ja_asr_orthographic_equivalence_01_trial as t
    samples = ["三人で行きました。", "三十人が来ました。", "100円でした。", "百円でした。", "3,000円", "三千円", "5日間", "2026年", "二千二十六年"]
    for s in samples:
        mine = [(int(a.value), a.unit) for a in vg.extract_atoms_ja(s) if a.kind == "num" and a.unit]
        theirs = [(int(sp.value), sp.counter) for sp in t.find_spans(s)]
        assert mine == theirs, s
    for n in (1, 2, 3, 4, 5, 7, 9, 14, 20, 24, 30):
        for c in ("day", "person", "age", "tsu", "month", "hour", "kai"):
            assert vg.is_irregular_sig(n, c) == t.is_irregular_sig(str(n), c), (n, c)


def test_parity_kana_numerals_with_er066_readings():
    import er066_ja_asr_orthographic_equivalence_01_trial as t
    for kana, (v, unit, _amb) in vg.KANA_NUMERALS.items():
        cands = t._cands(v, unit)
        assert kana in cands, (kana, cands)
