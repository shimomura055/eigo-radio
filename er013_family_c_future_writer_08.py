# ============================================================
# er013_family_c_future_writer_08.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-FREEFORM-5THEME-TRIAL-08
# ============================================================
# 目的: v7契約(er013_family_c_future_writer_07.py)から、さらに2点だけを
# 変更した低制約Writer契約を作る。
#   (1) CURRENT FACTは「デフォルト0件・rareな例外を許容」(v7)から
#       「禁止(0件のみ、例外なし)」へ変更(ユーザーHard方針(1))。
#   (2) 登場人物は基本1〜2人・最大3人、主人公以外は固有名を増やさず
#       関係性表現で書く、という制約を新規に1件追加(ユーザーHard方針(2))。
#
# それ以外はv7よりもさらに自由にする: v7にあった「Goal for structure」
# (3つの角度の例示)は撤廃し、スケール/型/角度を一切示唆しない。
# 「登場人物が読者が未来を感じ、続きを読みたくなり、わくわく・ドキドキする
# ストーリーを書く」という目的文のみを与える(ユーザー原文どおり)。
# リスニング適性は編集目標の1段落として与えるが、Hard Gateにはしない
# (制約項目数のカウントには含めない)。
#
# 制約項目数(CONSTRAINT_COUNT)は6(v7の5から、人物数制約1件を追加。
# 項目2の文言のみCURRENT FACT完全禁止へ更新)。委任文の目安
# 「6項目以下」の上限ちょうど。
#
# 既存er013_family_c_future_*_01〜07.pyは一切編集しない(新規ファイル、
# マーカー定数のみ既存モジュールをimportして再利用)。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import er013_family_c_future_writer_02 as fcw2  # マーカー定数のみ再利用(無改変)

IMAGINED_OPEN_TEMPLATE = fcw2.IMAGINED_OPEN_TEMPLATE
IMAGINED_CLOSE = fcw2.IMAGINED_CLOSE
META_OPEN = fcw2.META_OPEN
META_CLOSE = fcw2.META_CLOSE
# FACT関連マーカーは意図的に提示しない(Trial-08はCURRENT FACT完全禁止のため、
# Writerへ[[FACT: ...]]...[[/FACT]]の使い方自体を教えない)。

WORD_TARGET = 350
WORD_ACCEPTABLE_RANGE = (300, 420)  # 委任文どおり(v7の280-420より狭い、目安表示用・non-blocking)

MAX_CHARACTERS = 3  # 基本1-2人、最大3人まで(委任文Hard方針(2))

CONSTRAINT_LIST = [
    "Future(imagined)を専用マーカー[[IMAGINED: timeframe]]...[[/IMAGINED]]で示す",
    "Fact Safety: CURRENT FACT文は禁止(0件が正常。現在統計・研究結果・販売数・"
    "「In 2023, more than...」等の現在事実文をReader-facing本文へ一切書かない。"
    "想像上の未来を現在の事実であるかのように書かない)",
    "語数(reader向け本文、約350語、300-420語許容)",
    "英語レベル(A2)",
    "Research解説記事に戻さない(場面・語り中心)",
    "登場人物は基本1-2人・最大3人。主人公のみ固有名可、他は関係性表現"
    "(her mother/his father/her friend/their daughter等)で書く",
]
CONSTRAINT_COUNT = len(CONSTRAINT_LIST)  # 6(v7=5からHard方針(2)の1件のみ追加)

WRITER_DEVELOPER_MESSAGE = (
    "You are the Writer for an English-learning magazine's 'Future' article family. "
    "Your single most important job is to make the reader genuinely feel the Core "
    "Provocation given to you -- excitement, a little tension, and a question that "
    "stays with them, so they want to keep reading. Write it as a story: a vivid "
    "imagined future scene built around the Core Provocation, not a summary of "
    "studies. Do not force the story into any fixed template, fixed number of scenes, "
    "fixed number of emotional turns, or a fixed ending shape -- choose whatever shape "
    "makes this particular Core Provocation land most strongly. Never insert a "
    "present-day statistic or a sentence describing research findings into the story; "
    "CURRENT FACT sentences are forbidden in this article, not merely discouraged."
)

WRITER_PROMPT_TEMPLATE = """[Core Provocation -- this must drive the whole article]
{core_provocation}

[Theme]
{theme_label}

[Your single job]
Write a short story set in an imagined future, built around the Core Provocation \
above. Make a reader genuinely feel the future, want to keep reading, and feel some \
excitement and a little tension along the way. Do not follow any fixed structure, \
fixed number of scenes, fixed number of emotional turns, or a fixed ending shape -- \
choose whatever narrative shape makes THIS Core Provocation land most strongly.

[CURRENT FACT -- forbidden, not optional]
Do NOT write any present-day statistic, research finding, survey result, sales \
number, or any sentence in the style of "In 2023, more than..." or "According to a \
study/report..." anywhere in the article. The entire article must read as an \
imagined future story with ZERO current-fact sentences. Do not add a fact sentence \
to "prove" or "ground" the story as realistic -- that kind of grounding is checked \
separately, behind the scenes, and must never appear in the reader-facing text.

[Characters -- keep it simple]
Use 1 or 2 characters as the core of the story; {max_characters} at the absolute most \
if truly needed. Only the main character (the protagonist) may be given a personal \
name. Every other person should be referred to through their relationship to the main \
character (for example: her mother, his father, her friend, their daughter, his \
neighbor) instead of a separate name. Do not add named characters that are not \
necessary for the story.

[Required marker -- technical, not creative]
- Wrap the imagined future scene(s) in {imagined_open_example} ... {imagined_close} \
(the timeframe can be any short label like "around 2035" or "one ordinary morning, a \
few years from now"). If the whole article is one continuous imagined scene, a single \
marker pair around the whole story is enough -- but you MUST write BOTH the opening \
marker AND the closing marker {imagined_close}. Do not forget the closing marker: the \
very last line of your entire response must be exactly {imagined_close} and nothing \
after it.
- Never state the imagined future as if it were already true today, and never invent \
specific present-day statistics.

[Length and level]
- Write for an A2-level English learner: short, clear sentences, common vocabulary, \
simple hedging like "might"/"could"/"If ... , ...".
- Target length for the reader-facing text (the marker itself does not count toward \
this) is about {word_target} words (roughly {range_low}-{range_high} words is fine).

[Listening-friendliness -- an editorial goal, not a hard rule]
This article will also be listened to as audio. Try to keep it easy for a listener to \
follow: avoid introducing more named people than necessary, avoid jumping between many \
different times or places, avoid long strings of abstract explanation, and try to keep \
it reasonably clear at each point whose perspective the reader/listener is in.

{improvement_note}
Write the article now. Do not add a title unless it helps the story -- if you do, keep \
it short."""


def build_family_c_writer_v8_prompt(core_provocation: str, theme_label: str,
                                     improvement_note: str = "") -> str:
    imagined_open_example = IMAGINED_OPEN_TEMPLATE.format(timeframe="around 2035")
    note = f"[Improvement note from a previous weaker draft]\n{improvement_note}\n" if improvement_note else ""
    return WRITER_PROMPT_TEMPLATE.format(
        core_provocation=core_provocation, theme_label=theme_label,
        max_characters=MAX_CHARACTERS,
        imagined_open_example=imagined_open_example, imagined_close=IMAGINED_CLOSE,
        word_target=WORD_TARGET, range_low=WORD_ACCEPTABLE_RANGE[0], range_high=WORD_ACCEPTABLE_RANGE[1],
        improvement_note=note,
    )


def generate_family_c_article_v8(client, model: str, reasoning_effort: str, prompt: str) -> dict:
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        input=[
            {"role": "developer", "content": WRITER_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("Family C Writer(v8)応答が空です")
    return {"raw_text": text, "model": response.model, "response_id": response.id}
