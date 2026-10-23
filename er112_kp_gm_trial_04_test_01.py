# -*- coding: utf-8 -*-
"""課題①のDEV部品の決定論test(API 0): 内容語重なり検査、flag規則、M message(再整合用の指示・例の除去)、Cp schema順、Production schema不変。"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.environ["KP04_INSPECT_VERSION"] = "v2"
os.environ["KP04_INSPECT_EFFORT"] = "low"
import er112_kp_gm_trial_04 as X                    # noqa: E402
import er112_kp_gm_trial_04_gen as G                # noqa: E402
import er112_kp_gm_trial_04_c as C                  # noqa: E402
import er003_key_words_gloss_alignment as ga        # noqa: E402


def test_overlap_detects_shared_content_words():
    assert X.overlap("draw a line", "to make a mark by drawing a straight shape") == ["draw"]
    assert X.overlap("an unseen clock", "a device that cannot be seen") == []      # unseen/seen はstemが異なる(限界: 近縁語の見落としは許容、記録のみ)
    assert X.overlap("take the wheel", "to grip the wheel of a vehicle") == ["wheel"]
    assert X.overlap("give way", "to collapse") == []


def test_flag_variants_and_declared_rule():
    o = dict(usage_in_sentence="figurative", gloss_conveys="literal_image_only", invalid=True, overlap=["draw"])
    f = X.flag_variants(o)
    assert f["V1"] is False and f["V1_inv"] is True and f["V2_inv"] is True      # 検査不成立でもliteral_image_onlyならflag(事前宣言のV2_inv)
    assert C.is_flag(o) is True
    assert C.is_flag(dict(usage_in_sentence="literal", gloss_conveys="literal_image_only")) is False
    assert C.is_flag(dict(usage_in_sentence="figurative", gloss_conveys="same_meaning")) is False
    assert C.is_flag(None) is False


def test_m_message_removes_realignment_instructions():
    A = X.all_kps()
    tgt = G._targets([A["draw a line"]])
    m = G.build_m_message(tgt, "ARTICLE")
    for banned in ("判定の参考例", "fall into", "qa_reflects_all_key_phrase_words", "過不足なく", "current_japanese_gloss", "added_content_words", "added_word_mappings"):
        assert banned not in m, banned
    assert "承認済み選定Promptと同一" in m and "直訳調" in m          # 承認済みgloss規則は維持
    full = ga.build_user_message_corrected(tgt, "ARTICLE")
    assert "判定の参考例" in full                                       # Production messageは不変(参照元として変更していない)


def test_cp_schema_audit_fields_after_gloss_and_production_schema_unchanged():
    before = json.dumps(ga.GLOSS_ALIGNMENT_JSON_SCHEMA, sort_keys=True)
    props = list(G.cp_schema()["schema"]["properties"]["items"]["items"]["properties"])
    i = props.index("japanese_gloss")
    assert props[i + 1:i + 5] == ["usage_in_sentence", "usage_meaning_en", "gloss_alone_reading_en", "gloss_conveys"]
    assert json.dumps(ga.GLOSS_ALIGNMENT_JSON_SCHEMA, sort_keys=True) == before


def test_inspect_schema_output_order():
    props = list(X.INSPECT_SCHEMA_V2["schema"]["properties"]["items"]["items"]["properties"])
    assert props == ["rank", "usage_in_sentence", "usage_meaning_en", "ja_expression_shares_figure", "gloss_alone_reading_en", "gloss_conveys"]
    props1 = list(X.INSPECT_SCHEMA["schema"]["properties"]["items"]["items"]["properties"])
    assert props1 == ["rank", "usage_in_sentence", "usage_meaning_en", "gloss_alone_reading_en", "gloss_conveys"]


def test_kp_sets_frozen():
    A, F, N, Ns = X.kp_sets()
    assert len(A) == 115 and len(F) == 41 and len(N) == 74 and len(Ns) == 20 and not (set(F) & set(Ns))
