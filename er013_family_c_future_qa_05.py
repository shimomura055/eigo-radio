# ============================================================
# er013_family_c_future_qa_05.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05
# ============================================================
# 目的: v5契約(見出し3つ固定・場面間に余分な見出しを挟まない・2つ目の
# [[IMAGINED]]ブロック直後から統合示唆段落・枠外での"will"禁止)を、
# 決定的(非LLM、¥0)に検証する追加診断モジュール。
#
# 既存er013_family_c_future_qa_01/02/03は一切編集しない(本ファイルは
# それらの戻り値[imagined_blocks・unhedged_future_claims_outside_markers_
# heuristicなど]を受け取って追加チェックするだけの、新規・独立モジュール)。
# 既存Fact Safety Gate(scan_editorial_gate_v3・Ledger Deviation Checker・
# Fact Checker A')を置き換えるものではなく、v5専用の追加診断として
# 既存Gateへ論理積(AND)で合成する用途を想定する。
#
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import re

# "## " のような見出し行("### "以下の下位見出しはカウント対象外。
# v5契約は"##"のみを見出し境界として使う前提)。
_HEADING_RE = re.compile(r'(?m)^##(?!#)')

_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')


def count_headings(text: str) -> int:
    """"## "見出しの数を数える(決定的、¥0)。"""
    return len(_HEADING_RE.findall(text or ""))


def scan_v5_structure_gate(article_no_meta_with_markers: str, reader_text: str,
                            imagined_blocks: list, unhedged_future_hits: list) -> dict:
    """v5構造契約を決定的に検証する。

    - heading_count: reader_text(マーカー除去済み最終読者向け本文)の
      見出し数は3固定(1つ目の場面/2つ目の場面/統合示唆)。
    - headings_between_scenes: 1つ目・2つ目の[[IMAGINED]]ブロックの
      あいだ(article_no_meta_with_markersのoffsetベース)に見出しが
      1つを超えて挟まっていないか(=余分な節が割り込んでいないか)。
    - headings_after_scene2: 2つ目のブロックの直後から記事末尾までに
      見出しがちょうど1つ(統合示唆用)だけ存在するか。
    - unhedged_future_hits: 既存er013_family_c_future_qa_01の
      detect_unhedged_future_claims()の戻り値をそのまま受け取り、
      件数0を要求する(枠外での"will"断定を許さない)。

    imagined_blocksは fcq_v1.extract_imagined_blocks() の戻り値
    ({"timeframe", "body", "start", "end"}のlist、article_no_meta_
    with_markers上のoffset)をそのまま渡すことを想定する。
    """
    fail_reasons = []
    heading_count = count_headings(reader_text)
    if heading_count != 3:
        fail_reasons.append(f"heading_count={heading_count}(v5契約は3固定: 場面1/場面2/統合示唆)")

    imagined_blocks = imagined_blocks or []
    if len(imagined_blocks) != 2:
        fail_reasons.append(f"imagined_blocks_count={len(imagined_blocks)}(v5契約は2固定)")
        headings_between = None
        headings_after = None
    else:
        text = article_no_meta_with_markers or ""
        between_text = text[imagined_blocks[0]["end"]:imagined_blocks[1]["start"]]
        headings_between = count_headings(between_text)
        if headings_between > 1:
            fail_reasons.append(
                f"headings_between_scenes={headings_between}"
                "(1つ目と2つ目の場面のあいだに余分な見出し・節が挟まっている)")
        after_text = text[imagined_blocks[1]["end"]:]
        headings_after = count_headings(after_text)
        if headings_after != 1:
            fail_reasons.append(
                f"headings_after_scene2={headings_after}"
                "(2つ目の場面のあとは統合示唆用の見出し1つだけのはず)")

    unhedged_future_hits = unhedged_future_hits or []
    if unhedged_future_hits:
        fail_reasons.append(
            f"unhedged_will_outside_markers={len(unhedged_future_hits)}件: "
            + " / ".join(unhedged_future_hits[:3]))

    return {
        "overall_status": "PASS" if not fail_reasons else "FAIL",
        "fail_reasons": fail_reasons,
        "heading_count": heading_count,
        "imagined_blocks_count": len(imagined_blocks),
        "headings_between_scenes": headings_between,
        "headings_after_scene2": headings_after,
        "unhedged_future_hits_count": len(unhedged_future_hits),
    }


def count_events_per_scene(imagined_blocks: list) -> list:
    """診断用(non-blocking、報告用の参考値): 各[[IMAGINED]]ブロック本文の
    文数を数える(出来事列挙の上限[目安3つ程度]が守られているかの一次
    診断。ブロッキングGateではない。文数=出来事の数そのものではないが、
    出来事の連続列挙度合いの粗い代理指標として使う)。"""
    results = []
    for b in imagined_blocks or []:
        body = b.get("body", "") or ""
        sentences = [s for s in _SENTENCE_SPLIT_RE.split(body) if s.strip()]
        results.append({"timeframe": b.get("timeframe"), "sentence_count": len(sentences)})
    return results
