# -*- coding: utf-8 -*-
"""KP-PHRASE7-WORD5-PRODUCTION-01 委任_02: Key Phrase最大7件(P7)+Key Word最大5件(W5')の分離抽出 Prompt・message・呼出wrapper。

ユーザー正式採用(APPROVED_FOR_PRODUCTION 2026-10-27)。新規flagなしの既定ON正規実装(Fable確定D1=R0。旧3+5へはgit revert)。
旧Prompt 2(`er105.PROMPT_2_TEXT`)・Prompt 2-V(`er119_kp_prompt_2v_01`)は本文・shaとも無変更で残置する(旧runのresume・復帰の部品)。

- P7(call1・フレーズ最大7): Trial-02で用いたP7と**同一の生成式**(`ft.PROMPT_2_TEXT`から冒頭の件数文と条件6だけ置換)。
  Trial module(`er124_kp_phrase_word_trial_01`)は**importしない**(Production moduleからTrialへ依存しない)。同一性はtestがer124を
  test専用importして照合する(`er119_kp_p7w5_test_01`)。
- W5'(call2・Key Word最大5): Trial-02のW5と、補足1行(KP含有語の扱い)だけが違う。W5は「一律除外しない」だったが、ユーザー原文
  「すでに選定されたKey Phraseに含まれる単語は、Key Word候補から除外する。」を逐語で反映する(Fable確定D4)。
- 返答schemaはP7・W5'とも2-Vと同一(phrase/reason_ja/word_count)。wrapper `make_p7_selector_fn`/`make_w5_selector_fn`はテスト時に
  call1用とcall2用を取り違えないためのfail-closedな差し込み点(Opus M-5)。API呼出は実運用時のみ。
- A/B/C(strategy_l経路)は本moduleをimportしない(`er119_isolation_test_01`)。
"""
from __future__ import annotations

import hashlib
from typing import Callable, Optional

import er105_kp_fulltext_selector_01 as ft
import er119_kp_prompt_2v_01 as p2v

KP_PHRASE_MAX = 7
KP_WORD_MAX = 5
KP_CANDIDATE_TOTAL_MAX = KP_PHRASE_MAX + KP_WORD_MAX    # 12

P7_ID = "kp_prompt_p7"
W5P_ID = "kp_prompt_w5p"

# ---- P7(Trial-02 P7と同一の生成式。er124からコピーせずPrompt 2から生成する) ---------------------------------------------------------------
_P2_HEAD = "以下の記事から、英語上級者が学ぶ価値のある単語・フレーズ・表現・イディオムを**3つ**選んでください。\n"
_P2_COND6 = "6. **3件選定**：条件を満たす候補から3件選ぶ。適切な候補が不足する場合のみ3件未満とし、数合わせはしない。\n"
_P7_HEAD = ("以下の記事から、英語上級者が学ぶ価値のあるフレーズ・表現・イディオム(2語以上の連続した語句)を、"
            "学習価値の高い順に**最大7つ**選んでください(単語単体は別の枠で選ぶため、ここでは選びません)。\n")
_P7_COND6 = ("6. **最大7件・順位付け**：条件を満たす候補から、学習価値の高い順に最大7件を選び、1位から順に並べる。"
             "互いに同一、または一方がもう一方を含む類似の表現を重ねて選ばない。"
             "適切な候補が不足する場合のみ7件未満とし、数合わせはしない。"
             "各候補に、選んだ理由を日本語で1文(40字以内)添える。\n")
assert _P2_HEAD in ft.PROMPT_2_TEXT and _P2_COND6 in ft.PROMPT_2_TEXT, "Prompt 2の想定文言が変わっています(P7の差分基準が崩れた)"
P7_TEXT = ft.PROMPT_2_TEXT.replace(_P2_HEAD, _P7_HEAD, 1).replace(_P2_COND6, _P7_COND6, 1)
P7_SHA256 = hashlib.sha256(P7_TEXT.encode("utf-8")).hexdigest()
P7_SHA256_PINNED = "2e93019300f960e5ff3070dd83b12a81566b8ceb87b44b335d554a7a711eb291"
assert P7_SHA256 == P7_SHA256_PINNED, "P7が固定shaと一致しません(変更にはユーザー承認が必要)"

# ---- W5'(Trial-02 W5の補足2行目1箇所だけをユーザー原文逐語へ) ---------------------------------------------------------------------------
W5P_CONTAINED_WORD_LINE = "- すでに選定されたKey Phraseに含まれる単語は、Key Word候補から除外する。\n"   # ユーザー原文の逐語(Fable確定D4)
W5P_TEXT = (
    "以下の記事から、英語上級者が学ぶ価値のある**単語単体(1語)**を、学習価値の高い順に**最大5つ**選んでください"
    "(すでに選ばれたフレーズ・表現は、記事本文の後ろに示します)。\n"
    "\n"
    "以下の5条件を、記載順に適用してください。順番を入れ替えたり、条件を追加したりしないでください。\n"
    "\n"
    "1. **本文一致（絶対条件）**：本文中に実在する単語だけを、本文に現れる形のまま抜き出す。変更・言い換え・追加・創作は禁止。\n"
    "2. **1語（絶対条件）**：スペースを含まない1語だけを出力する。2語以上は出力禁止。\n"
    "3. **上級者向けの学習価値**：上級者でも学ぶ価値のある単語を優先する。\n"
    "4. **易しい語の除外**：基本語や、上級者なら知っている易しい単語は除外する。\n"
    "5. **単語単体の学習価値**：意味の明確さ・他の文脈での汎用性・難易度を考慮する。固有名詞・数字・この記事だけでしか使えない語は、考慮の際に避ける。"
    "ただし必須条件にはしない。\n"
    "\n"
    "補足:\n"
    "- 条件3・4を、条件5より必ず優先する。条件5を理由に、条件3・4に適合する単語を不当に除外しない。\n"
    + W5P_CONTAINED_WORD_LINE +
    "- 条件1・2(本文一致と1語)は必須。\n"
    "\n"
    "出力: 条件を満たす単語から、学習価値の高い順に最大5件を選び、1位から順に並べる。"
    "適切な候補が不足する場合のみ5件未満とし、数合わせはしない(簡単すぎる語や不自然な語で5件に揃えない)。"
    "各候補に、選んだ理由を日本語で1文(40字以内)添える。\n"
    "\n"
    "**出力直前に各候補を本文と照合し、改変がないこと、1語であることを再確認してください。語数も併記してください。**")
W5P_SHA256 = hashlib.sha256(W5P_TEXT.encode("utf-8")).hexdigest()
W5P_SHA256_PINNED = "12d3370876d189f016cc49e26b2abcbe2618f028b380fe7fcff479554fa693b8"   # D4逐語1文版(2026-10-27実測。DESIGN_01の187f1b87…は旧2文案)
assert W5P_SHA256 == W5P_SHA256_PINNED, "W5'が固定shaと一致しません(変更にはユーザー承認が必要): " + W5P_SHA256


# ---- message組立(Prompt本文は不変・本文後置方式。2-Vと同形) ---------------------------------------------------------------------------
def build_p7_message(article_text: str, shown_phrases: Optional[list] = None, diagnostic_note: Optional[str] = None) -> str:
    """P7 + 本文。補完(shown_phrasesあり)のときだけ『すでに選ばれた表現(これらは選ばない)』節を本文の後ろに置く。再選定noteはその後ろ。"""
    msg = P7_TEXT + ft.BODY_DELIMITER + article_text
    if shown_phrases is not None:
        msg += p2v.ALREADY_DELIMITER + "\n".join(f"- {p}" for p in shown_phrases)
    if diagnostic_note:
        msg += ft.NOTE_DELIMITER + diagnostic_note
    return msg


def p7_prefix_intact(user_message: str) -> bool:
    return user_message.startswith(P7_TEXT + ft.BODY_DELIMITER)


def build_w5_message(article_text: str, shown_phrases: list, diagnostic_note: Optional[str] = None) -> str:
    msg = W5P_TEXT + ft.BODY_DELIMITER + article_text + p2v.ALREADY_DELIMITER + "\n".join(f"- {p}" for p in shown_phrases)
    if diagnostic_note:
        msg += ft.NOTE_DELIMITER + diagnostic_note
    return msg


def w5_prefix_intact(user_message: str) -> bool:
    return user_message.startswith(W5P_TEXT + ft.BODY_DELIMITER)


# ---- 呼出wrapper(Opus M-5: テストでcall1(P7)/call2(W5')/旧2-Vを取り違えないための明示的な差し込み点) -----------------------------------------
def make_p7_selector_fn(user_message: str, *, client=None, model: Optional[str] = None) -> Callable:
    """P7(call1/フレーズ補完)用。schemaは2-Vと同一。送信messageの先頭がP7でなければ即例外(fail-closed)。"""
    if not p7_prefix_intact(user_message):
        raise ft.FulltextSelectionError("P7 selectorに渡されたmessageの先頭がP7でない(Prompt取り違え)")
    return p2v.make_vocab_selector_fn(user_message, client=client, model=model)


def make_w5_selector_fn(user_message: str, *, client=None, model: Optional[str] = None) -> Callable:
    """W5'(call2/単語補完)用。schemaは2-Vと同一。送信messageの先頭がW5'でなければ即例外(fail-closed)。"""
    if not w5_prefix_intact(user_message):
        raise ft.FulltextSelectionError("W5' selectorに渡されたmessageの先頭がW5'でない(Prompt取り違え)")
    return p2v.make_vocab_selector_fn(user_message, client=client, model=model)


class PromptSpec:
    """run_vocab_selection(一般化)に渡すPrompt仕様。call時に毎回モジュール属性を引く(mock.patch.objectが効く)。"""

    def __init__(self, *, prompt_id: str, sha256: str, max_items: int, single_word_only: bool, kind: str):
        self.prompt_id, self.sha256, self.max_items, self.single_word_only, self.kind = prompt_id, sha256, max_items, single_word_only, kind

    def build_message(self, text: str, shown: list, note: Optional[str]) -> str:
        raise NotImplementedError

    def prefix_intact(self, msg: str) -> bool:
        raise NotImplementedError

    def make_call(self, msg: str, model: Optional[str]) -> Callable:
        raise NotImplementedError


class _P7Spec(PromptSpec):
    def build_message(self, text, shown, note):
        return build_p7_message(text, shown_phrases=shown, diagnostic_note=note)

    def prefix_intact(self, msg):
        return p7_prefix_intact(msg)

    def make_call(self, msg, model):
        return make_p7_selector_fn(msg, model=model)


class _W5Spec(PromptSpec):
    def build_message(self, text, shown, note):
        return build_w5_message(text, shown, diagnostic_note=note)

    def prefix_intact(self, msg):
        return w5_prefix_intact(msg)

    def make_call(self, msg, model):
        return make_w5_selector_fn(msg, model=model)


SPEC_P7 = _P7Spec(prompt_id=P7_ID, sha256=P7_SHA256, max_items=KP_PHRASE_MAX, single_word_only=False, kind="phrase")
SPEC_W5P = _W5Spec(prompt_id=W5P_ID, sha256=W5P_SHA256, max_items=KP_WORD_MAX, single_word_only=True, kind="word")
