# ============================================================
# er013_family_c_future_writer_08_b1.py
# 管理ID: USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1
# ============================================================
# 目的: er013_family_c_future_writer_08.py(Trial-08、Family C free-form
# Writer契約)から派生した、B1向け独立生成Writer契約。
#
# er013_family_c_future_writer_08.py自体は一切編集しない(新規ファイル、
# マーカー定数のみ既存モジュールをimportして再利用)。writer_08の6項目の
# Hard rule(CURRENT FACT完全禁止/登場人物1-2名・最大3名等)はそのまま
# 継承する。writer_08との違いは以下の2点のみ:
#   (1) 難易度をA2からB1(独立生成Natural Spoken English、adult tone、
#       A2ほど強く簡略化しない、B2より聞き取りやすい)へ変更する
#       (CURRENT_SPEC.md「B1(独立生成Natural Spoken News English)」節の
#       難易度思想を参考にするが、本Writerはニュース記事ではなくFamily C
#       の物語記事であり、同節が定める語数の数値上限自体は存在しない
#       [「全体語数 上限なし」]。そのため本Writerの語数目安[WORD_TARGET/
#       WORD_ACCEPTABLE_RANGE]はCURRENT_SPEC由来の確定値ではなく、
#       Trial限定の暫定目安である[超過は必ず報告する運用])。
#   (2) 単純翻訳・単純難化ではなく、参照するA2版記事と同一のStory core
#       (登場人物・設定・出来事の順序・転換点・結末・Core Provocation)を
#       維持しながら独立生成する、という指示を追加する(参照本文の
#       逐語訳・パラフレーズ化を明示的に禁止する)。
#
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# Production Writer(er013_family_c_future_writer_08.py本体)は無変更。
# ============================================================
from __future__ import annotations

import er013_family_c_future_writer_08 as writer08  # マーカー定数・hard rule文言の参照元(無改変)

IMAGINED_OPEN_TEMPLATE = writer08.IMAGINED_OPEN_TEMPLATE
IMAGINED_CLOSE = writer08.IMAGINED_CLOSE
META_OPEN = writer08.META_OPEN
META_CLOSE = writer08.META_CLOSE

# Trial限定の暫定語数目安(CURRENT_SPEC.mdのB1 News節には数値上限が存在しない
# ため、writer_08[A2、350語/300-420語]を土台に、B1はA2ほど圧縮しない分
# やや長くなる想定で暫定設定。超過は必ずreport)。
WORD_TARGET = 400
WORD_ACCEPTABLE_RANGE = (340, 480)

MAX_CHARACTERS = writer08.MAX_CHARACTERS  # 3(writer_08と同一、基本1-2人・最大3人)

CONSTRAINT_LIST = [
    "Future(imagined)を専用マーカー[[IMAGINED: timeframe]]...[[/IMAGINED]]で示す",
    "Fact Safety: CURRENT FACT文は禁止(0件が正常。現在統計・研究結果・販売数・"
    "「In 2023, more than...」等の現在事実文をReader-facing本文へ一切書かない。"
    "想像上の未来を現在の事実であるかのように書かない)",
    "語数(reader向け本文、約400語、340-480語目安。CURRENT_SPEC上のB1 News節に"
    "数値上限はなく、これはTrial限定の暫定目安。超過時は必ず報告する)",
    "英語レベル(B1、独立生成Natural Spoken English、adult tone、A2ほど強く"
    "簡略化しない、B2相当の難しい英文よりlisteningで追いやすい)",
    "Research解説記事に戻さない(場面・語り中心)",
    "登場人物は基本1-2人・最大3人。主人公のみ固有名可、他は関係性表現"
    "(her mother/his father/her friend/their daughter等)で書く",
    "同一Story core維持: 参照するA2版記事の登場人物・設定・出来事の順序・"
    "転換点・結末・Core Provocationを維持したまま、B1向けに独立生成する"
    "(参照本文の逐語訳・単純なパラフレーズ化は禁止)",
]
CONSTRAINT_COUNT = len(CONSTRAINT_LIST)

WRITER_DEVELOPER_MESSAGE = (
    "You are the Writer for a B1-level (independently generated, natural spoken "
    "English, adult tone) retelling of an existing Family C 'Future' story. Your job "
    "is to write your OWN B1-level English telling of the SAME story core (same "
    "characters, same setting, same sequence of key events, same turning point, same "
    "ending, same Core Provocation) as the reference A2-level story you are given. Do "
    "NOT translate or lightly paraphrase the reference sentence-by-sentence -- write "
    "genuinely independent B1 prose. B1 here means: natural spoken English, not as "
    "heavily simplified as A2, but still clearly easier to follow by listening than "
    "B2 -- keep clause density, concept density, and long-distance dependencies lower "
    "than a literary or academic style would use, without hard vocabulary or "
    "sentence-length rules. Never insert a present-day statistic or a sentence "
    "describing research findings into the story; CURRENT FACT sentences are "
    "forbidden in this article, not merely discouraged."
)

WRITER_PROMPT_TEMPLATE = """[Core Provocation -- this must drive the whole article]
{core_provocation}

[Theme]
{theme_label}

[Reference story -- A2 level, story core ONLY, do not translate or paraphrase \
sentence-by-sentence]
{reference_article}

[Story core you must preserve -- from the reference story above]
{story_core_bullets}

[Your single job]
Write your own independent B1-level telling of the SAME story core described above. \
Make a reader genuinely feel the future, want to keep reading, and feel some \
excitement and a little tension along the way -- but write it as a fresh B1 piece of \
prose in your own words and sentence structures, not a translation or light \
paraphrase of the reference story. You may restructure sentences, add ordinary \
sensory or scene-setting detail, and use a more natural adult narrative voice than \
the A2 reference -- as long as the characters, setting, event order, turning point, \
and ending stay the same.

[CURRENT FACT -- forbidden, not optional]
Do NOT write any present-day statistic, research finding, survey result, sales \
number, or any sentence in the style of "In 2023, more than..." or "According to a \
study/report..." anywhere in the article. The entire article must read as an \
imagined future story with ZERO current-fact sentences. Do not add a fact sentence \
to "prove" or "ground" the story as realistic -- that kind of grounding is checked \
separately, behind the scenes, and must never appear in the reader-facing text.

[Characters -- keep it simple, same characters as the reference story]
Use the same 1-2 characters as the core of the story as the reference (the \
protagonist and her mother); {max_characters} at the absolute most if truly needed. \
Only the main character (the protagonist) may be given a personal name (keep her \
name the same as in the reference story). Every other person should be referred to \
through their relationship to the main character (for example: her mother) instead \
of a separate name. Do not add named characters that are not in the reference story.

[Dialogue attribution -- for downstream audio production]
When the robot or the mother speaks in direct quotation, make the speaker \
unambiguous through the attribution phrase near the quotation (for example: "said \
the robot" / "the robot said" for the robot's speech, and "her mother said" / "said \
her mother" for the mother's speech). This mirrors the reference story's dialogue \
style and is required so an automated process can assign the correct voice to each \
line -- do not rely on context alone to identify a speaker.

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
- Write for a B1-level English learner (adult tone, natural spoken English, not as \
simplified as A2, easier to follow by listening than B2).
- Target length for the reader-facing text (the marker itself does not count toward \
this) is about {word_target} words (roughly {range_low}-{range_high} words is fine; \
this is a Trial-only approximate guideline, not a hard CEFR word-count rule).

[Listening-friendliness -- an editorial goal, not a hard rule]
This article will also be listened to as audio. Try to keep it easy for a listener to \
follow: avoid introducing more named people than necessary, avoid jumping between many \
different times or places, avoid long strings of abstract explanation, and try to keep \
it reasonably clear at each point whose perspective the reader/listener is in.

{improvement_note}
Write the article now. Do not add a title unless it helps the story -- if you do, keep \
it short."""


# Story core bullets(A2版 reader_facing_article.txtから人手抽出、Trial限定の
# 固定コンテキスト。writer_08_b1はhome_robotsテーマ専用ではなく汎用関数だが、
# 呼び出し側[er013_family_c_episode_trial_09b_b1_run.py]は本Trialでは
# home_robotsテーマのみを渡す)。
HOME_ROBOTS_STORY_CORE_BULLETS = """- Protagonist: Maya (only named character). Her home robot manages nearly every \
small daily choice for her (food, clothes, entertainment, messages, route to work) \
so completely that her life has become effortless but passive.
- Inciting incident: On a rainy evening, Maya's mother arrives with one small bag and \
says her doctor says she cannot live alone anymore; she asks Maya to choose between a \
care house or moving in with Maya.
- The robot presents two labeled plans (more sleep for Maya vs. more time with her \
mother) and, when Maya asks it to just choose the better plan, it repeatedly says it \
needs Maya's preference instead of deciding for her.
- Turning point: Maya realizes this is not a comfort-optimization question the robot \
can solve for her the way it solves everything else; when her mother asks "What do \
you want, Maya?", Maya cannot answer.
- Climax action: Maya tells the robot to turn everything off; the house goes dark and \
quiet, and for the first time in years nothing is choosing the next moment for her.
- Ending: Maya, afraid but awake, tells her mother "come in" -- inviting her in \
herself. The story ends on the idea that the first choice that truly belonged to \
Maya was simply the wish to make one.
- Core Provocation: A home robot makes life effortless by quietly choosing hundreds \
of tiny things for its owner until one day the owner must make a genuinely important \
choice and discovers she no longer knows how. Is convenience slowly training humans \
out of having preferences?"""


def build_family_c_writer_v8_b1_prompt(core_provocation: str, theme_label: str,
                                        reference_article: str, story_core_bullets: str,
                                        improvement_note: str = "") -> str:
    imagined_open_example = IMAGINED_OPEN_TEMPLATE.format(timeframe="around 2035")
    note = f"[Improvement note from a previous weaker draft]\n{improvement_note}\n" if improvement_note else ""
    return WRITER_PROMPT_TEMPLATE.format(
        core_provocation=core_provocation, theme_label=theme_label,
        reference_article=reference_article, story_core_bullets=story_core_bullets,
        max_characters=MAX_CHARACTERS,
        imagined_open_example=imagined_open_example, imagined_close=IMAGINED_CLOSE,
        word_target=WORD_TARGET, range_low=WORD_ACCEPTABLE_RANGE[0], range_high=WORD_ACCEPTABLE_RANGE[1],
        improvement_note=note,
    )


def generate_family_c_article_v8_b1(client, model: str, reasoning_effort: str, prompt: str) -> dict:
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
        raise RuntimeError("Family C Writer(v8-B1)応答が空です")
    return {"raw_text": text, "model": response.model, "response_id": response.id}
