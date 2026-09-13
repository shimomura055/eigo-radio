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


# ============================================================
# OPEN-141-TARGET-SENTENCE-DIFF-QA-PRODUCTION-WIRING-01(ユーザー承認
# 2026-09-13、差分QA案IのPoint Overlap rule-based再計算部分)。
# ============================================================
# Local Rewrite受理直後、対象文がPoint One/Twoの本文に属する場合のみ、
# 既存のrule-based Point Overlap(上記flag_possible_paraphrase、LLM再呼び出し
# なし・¥0)をそのsectionについて再計算する
# (`er011_open141_target_sentence_diff_qa_integration_trial_b_01.py`
# recompute_point_overlap_if_in_point_section()のProduction移植)。
# sectionsは呼び出し元(A-Family: er003_v1_n3_01_articles_generate.
# split_common_sections_for_point_qa()、B-Family: 同関数をそのまま流用、
# `{'point_one_body','point_two_body','full_story'}`を含む辞書または
# 想定構造が見つからない場合はNone)をそのまま渡す。この関数自身は
# 記事構造のparsingを行わない(呼び出し元の既存分割ロジックへ一切変更を
# 加えないため)。B-Family 3V(Point One/Two見出しを持たない構造)では
# sectionsが常にNoneまたは対象文が該当しないため、applicable=Falseとなる
# (想定通りの安全な無効化、新しい構造判定基準を追加しない)。
# 判定結果は記録のみ(non-blocking)であり、Trial版と同様この結果を理由に
# Local Rewriteの受理/不受理を変更しない(受理判定はFact Checker A'の
# verdict='FAIL'およびLedger Deviation Checkerの対象文再評価のみで行う、
# er010_ledger_local_rewrite_09.run_diff_qa_for_accepted_rewrite参照)。
def recompute_point_overlap_for_target_sentence(sections, target_sentence: str,
                                                  replacement_text: str = None) -> dict:
    if not sections:
        return {"applicable": False, "reason": "sections_not_available"}
    point_one_body = sections.get("point_one_body", "") or ""
    point_two_body = sections.get("point_two_body", "") or ""
    if target_sentence in point_one_body:
        key, other_key = "point_one", "point_two_body"
    elif target_sentence in point_two_body:
        key, other_key = "point_two", "point_one_body"
    else:
        return {"applicable": False, "reason": "target_not_in_point_one_or_two"}
    body = sections[f"{key}_body"]
    if replacement_text and target_sentence in body:
        body = body.replace(target_sentence, replacement_text, 1)
    overlap_vs_story = flag_possible_paraphrase(body, sections["full_story"])
    overlap_vs_other = flag_possible_paraphrase(body, sections[other_key])
    return {
        "applicable": True, "point": key,
        "overlap_vs_full_story": overlap_vs_story,
        "overlap_vs_other_point": overlap_vs_other,
        "flagged": overlap_vs_story["flagged"] or overlap_vs_other["flagged"],
    }
