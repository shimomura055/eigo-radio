# ============================================================
# er064_kp_noway_01_prompts.py  (FAMILY-X-KP-NO-WAY-MINIMAL-FIX-TRIAL-01 委任_01、Trial専用・Production非接続)
# P0X = P0(Production現行逐語)に「構文の一部の断片」ガード1段落だけを追加した選定Prompt。
# 追加位置: P0の「数値を補わないと意味が成立しない句は選ばない」段落の直後(既存の"単独で意味が成立する句を選ぶ"原則の一般化)。
# P0の他の文字・候補ブロック・出力schema・gate・canonicalizationは一切変更しない。特定語・特定記事・評価語句は含めない(testで固定)。
# ============================================================
from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.getcwd())
import er064_kp_int_01_prompts as PR  # noqa: E402
import er064_kp_opt_01_prompt_build as B1  # noqa: E402

# 既存P0内の挿入アンカー(この段落の直後に追加する。逐語一致をtestで確認)
ANCHOR_PARAGRAPH = ("「ソロ旅行を～％とする」のように、数値を補わないと意味が成立しない句・日本語グロス(数値の穴埋めを必要とする不完全な表現)は選ばないでください。"
                    "それ単体で意味が成立する句・グロスを選んでください。")

# 追加する1段落(これが唯一の差分)
ADDED_PARAGRAPH = ("切り出した語句が、本文ではto不定詞・前置詞句・目的語などが続いて初めて意味が成立する構文の一部で、その語句だけでは意味や用法が十分に伝わらない場合は、"
                   "候補の語句に本文で隣り合う語を加えて、意味が成立する1〜5語の形をdisplay_phraseにしてください(source_candidate_idは元の候補のままで構いません)。"
                   "is・have・canなどの有限の助動詞はdisplay_phraseに含められないため、含めずに意味が成立する形にできない場合は、その候補を選ばないでください。")


def head_p0x() -> str:
    h = B1.before_static()
    assert h.count(ANCHOR_PARAGRAPH) == 1, "P0 anchor paragraph not found exactly once"
    return h.replace(ANCHOR_PARAGRAPH, ANCHOR_PARAGRAPH + "\n\n" + ADDED_PARAGRAPH)


def render_p0x(cand_block: str) -> str:
    """PR.render('P0', ...) と同一の接合。headだけをP0Xに差し替える。"""
    return head_p0x().rstrip() + "\n\n" + cand_block.strip("\n") + "\n" + B1.BEFORE_GUIDANCE.rstrip() + "\n"


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
