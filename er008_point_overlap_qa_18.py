# ============================================================
# er008_point_overlap_qa_18.py
# ER-008-N8-QA-CONTENT-SPEED-HARDENING-18: Point One/TwoとFull Storyの
# 意味重複を検知する第1段階(安価なローカルチェック)
# ============================================================
# 背景: No.8のPoint One(A2/B1とも)が、Full Story Part1で既出の論理
# (「小さな確実なコスト vs 小確率だが大きな損失」)をほぼそのまま
# 言い換えているだけで、CURRENT_SPECの「Point One/Twoは深掘り・背景・
# 意味付けとし、Full Storyの代替にしない」という原則に反していた。
# Validator/QAはこれまで一切存在しなかった(er008_point_blueprint_
# validator_01.pyはShared Point Blueprint使用時のfact_id重複しか
# チェックせず、No.8はBaseline方式[blueprint=None]のため対象外だった)。
#
# 設計: 新規LLM呼び出し無し・追加API課金無しのlexical overlapを第1段階
# とする。Stop word(機能語)を除いた content word の重複率(Jaccard
# coefficient)が閾値を超えたら「Full Storyの言い換えの疑いが強い」と
# 判定する。第2段階(境界ケースのみLLM判定)は別途、既存のfact-check系
# LLM呼び出しパターンを踏襲して実装することを想定するが、今回はNo.8での
# 実証(第1段階の検知能力の確認)までをスコープとする。

from __future__ import annotations

import re

# 英語の一般的なstop word(機能語)。過検知回避のため、内容語だけを
# 比較対象にする(新規の大規模語彙辞書は作らない、既存方針を踏襲)。
_STOPWORDS = frozenset("""
a an the this that these those it its they them their there here
is are was were be been being do does did have has had will would
can could may might must shall should
to of in on at for with without by from as into onto over under
and or but so if then than because when while though although
he she his her him we us our you your i my me
not no nor
one two three
""".split())


def _content_words(text: str) -> set:
    words = re.findall(r"[A-Za-z']+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def lexical_overlap_ratio(point_text: str, full_story_text: str) -> dict:
    """point_textの内容語のうち、full_story_textにも出現する語の割合
    (overlap coefficient: |A∩B| / |A|、Pointを基準にした一方向の指標。
    Jaccardではなく敢えてPoint基準にする理由: Full Storyの方が長文のため
    対称なJaccardだと分母が肥大しoverlapが常に低く出て閾値判定が効かない)。
    """
    point_words = _content_words(point_text)
    story_words = _content_words(full_story_text)
    if not point_words:
        return {"overlap_ratio": 0.0, "shared_words": [], "point_word_count": 0}
    shared = point_words & story_words
    return {
        "overlap_ratio": round(len(shared) / len(point_words), 3),
        "shared_words": sorted(shared),
        "point_word_count": len(point_words),
        "story_word_count": len(story_words),
    }


# ER-008-15/16実データ(No.5-8の通常のPoint文)から目視で確認した限り、
# 通常の「別角度のPoint」はoverlap_ratioがおおよそ0.15-0.35程度に収まる
# (固有名詞・トピック語が共通するのは当然のため、0にはならない)。No.8
# Point Oneの実測(下記実証テストで0.5超)を踏まえ、暫定閾値を0.45とした。
#
# **2026-08-29追記(ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19)**:
# ユーザー承認により暫定閾値を0.40へ引き下げる(より積極的にflagする側へ
# 調整、実ユーザー検証中にfalse positive/negative実績を蓄積し、再調整
# する前提の暫定値のまま。永久仕様とはみなさない、OPEN Item扱い継続)。
OVERLAP_FLAG_THRESHOLD = 0.40


def flag_possible_paraphrase(point_text: str, full_story_text: str,
                              threshold: float = OVERLAP_FLAG_THRESHOLD) -> dict:
    result = lexical_overlap_ratio(point_text, full_story_text)
    result["flagged"] = result["overlap_ratio"] >= threshold
    result["threshold"] = threshold
    return result
