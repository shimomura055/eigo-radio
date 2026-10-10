# -*- coding: utf-8 -*-
"""er053_en_sentence_splitter_01.py
RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C1(追加のみ、2026-10-10)。

Risk Flagger(Review Queue)が英語記事を「文」に分けるための共通splitter(Production module)。
標準ライブラリ`re`のみ。Trial module(er052*)はimportしない。

移植元(コピー、Trial側は無変更):
  er052_open233_self_recovery_flow_runner_01.py
    - _VS_SENT_END_RE        (L4944)
    - _VS_L6_ABBREV          (L5477-5480、略語33語)
    - _VS_L6_ABBREV_WORD_RE  (L5481)
    - _vs_l6_abbrev_period   (L5485)
    - vs_sentence_segments_l6(L5503)
略語(`U.S.` `Mr.` `Jan.`など)直後の`.`では文を切らない。それ以外は`. `/`! `/`? `/日本語句点/改行で切る。
見出し行(`# ...`)も1文として扱う。`\n`でも分割する。文IDは `s1, s2, ...`。

他経路(er003_ja_to_en_translation.split_sentences / er010 split_sentences / Trial側 /
POST-EN Trialの`_split_sentences`)は変更しない。本moduleはそれらをimportしない。
"""
from __future__ import annotations

import re

SPLITTER_VERSION = "en_split_v1"

# 文末判定(Trial `_VS_SENT_END_RE` と同一)。改行も区切りとする。
_SENT_END_RE = re.compile(r"[.!?]+[\"”’'」』)\]]*(?=\s|$)|[。！？]+[\"”’」』)\]]*|\n")

# 直後の`.`が文末にならない略語(固定リスト33語、小文字・末尾の`.`なし)。
# `no`は直後が数字のとき(`No. 5`)だけ、`st`は直後が大文字のとき(`St. Louis`)だけ略語として扱う。
ABBREV = frozenset({
    "u.s", "u.k", "u.n", "mr", "mrs", "ms", "dr", "prof", "sr", "jr",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
    "st", "no", "vs", "e.g", "i.e", "inc", "co", "ltd", "corp", "a.m", "p.m"})
_ABBREV_WORD_RE = re.compile(r"([A-Za-z]+(?:\.[A-Za-z]+)*)$")


def _abbrev_period(text: str, m) -> bool:
    g = m.group(0)
    if g[0] != "." or len(g) > 1:  # `...`・`."`(閉じ引用符が続く)は略語ではなく文末
        return False
    w = _ABBREV_WORD_RE.search(text[max(0, m.start() - 12):m.start()])
    if not w:
        return False
    ab = w.group(1).lower()
    if ab not in ABBREV:
        return False
    nxt = text[m.end():].lstrip()[:1]
    if ab == "no":
        return nxt.isdigit()
    if ab == "st":
        return nxt.isupper()
    return True


def sentence_spans_en(text: str) -> list:
    """[(start, end)] を返す(元本文の座標、前後の空白は除去済み、空文は含まない)。"""
    segs, pos = [], 0
    for m in _SENT_END_RE.finditer(text):
        if m.group(0) != "\n" and _abbrev_period(text, m):
            continue
        end = m.start() if m.group(0) == "\n" else m.end()
        segs.append((pos, end))
        pos = m.end()
    segs.append((pos, len(text)))
    out = []
    for a, b in segs:
        while a < b and text[a].isspace():
            a += 1
        while b > a and text[b - 1].isspace():
            b -= 1
        if b > a:
            out.append((a, b))
    return out


def split_sentences_en(text: str) -> list:
    """英語記事を文に分ける。戻り値: [(sid, sentence_text)]、sid は s1, s2, ...(1始まり)。"""
    return [(f"s{i}", text[a:b]) for i, (a, b) in enumerate(sentence_spans_en(text), start=1)]
