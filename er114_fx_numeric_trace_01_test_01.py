# -*- coding: utf-8 -*-
"""er114_fx_numeric_trace_01 の照合規則テスト(API 0、読み取りのみ)。"""
import er114_fx_numeric_trace_01 as T


def present(surf, text):
    keys = [T.skey(s) for s in T.P.extract_surfaces(text)]
    return T.ja_present(surf, text, keys)


def test_ja_exact_and_comma_variants():
    assert present("8,900本超", "記録した崖は8,900本超だった")
    assert present("約5,470本", "5470本ほど")           # 約の有無・カンマ無しを許容
    assert not present("約5,470本", "5000本ほど")        # 値が違えば不一致


def test_ja_range_notation_variants():
    assert present("約42〜46", "半径は約42〜46 m縮んだ")
    assert present("約42〜46", "半径は約42から46メートル縮んだ")   # 波ダッシュ→「から」の書き換えを許容
    assert not present("約42〜46", "半径は約44 m縮んだ")


def test_ja_scale_units():
    assert present("約4億年", "約4億年前に始まったと仮定する")
    assert present("2億5,000万ドル", "2億5000万ドルで和解した")


def test_ambiguous_bare_small_integer():
    assert T.is_ambiguous("1") and T.is_ambiguous("7")
    assert not T.is_ambiguous("約5,470本") and not T.is_ambiguous("25%")


def test_en_values_and_spelled_numbers():
    assert T.en_present("7か月", "fell by 25% in seven months")
    assert T.en_present("25%", "fell by 25% in seven months")
    assert T.en_present("約42〜46", "shrank by about 42 to 46 meters")
    assert T.en_present("8,900本超", "more than 8,900 wrinkles")
    assert not T.en_present("約5,470本", "more than 8,900 wrinkles")
    assert T.en_present("2026年9月3日", "x") is None            # 日付は英訳では未評価


def test_en_unit_hint_prevents_false_positive():
    assert not T.en_present("7か月", "seven people came")        # 単位ヒント(month)が無ければ不一致
