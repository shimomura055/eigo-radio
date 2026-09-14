# ============================================================
# er013_family_c_future_writer_07.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-PROVOCATION-SCALE-COMPARISON-TRIAL-07
# ============================================================
# 目的: v6契約(er013_family_c_future_writer_06.py)からCURRENT FACT
# 「最低1件挿入」という暗黙の圧力を撤廃する。v6のReader-facing出力(Trial-06/
# 06b/06_bmi)は、home_robotsテーマで両方とも
# "In 2023, more than 2.1 million home floor-cleaning robots..." という
# 現在統計の一文をStory本文中に挿入していた。これはユーザー人間評価で
# 「Reader-facing本文に現在統計を入れるのは明確にNG」と明示的に否定された。
#
# v6の実際のprompt文言(WRITER_PROMPT_TEMPLATE)は "Cite AT MOST {max_fact}
# ... and only if it genuinely helps ground the story" であり、文言上は
# 「最大件数」の指定であって「最低1件」の明示的な指示は無かった。しかし
# ledger_excerptを「you may draw on」として目立つ形でそのまま提示していた
# ため、実運用では毎回1件のFACTマーカーが挿入される結果になっていた
# (Trial-06/06b、Trial-06_bmiはledgerがBCI収集の複数候補で1件に絞る動機が
# 弱く0件だった)。v7では、この「目立つ形でledgerを提示する」設計自体を
# 撤廃し、デフォルト0件を明示的な既定値として指示する。
#
# 制約は増やさない(v6と同じ5項目、CONSTRAINT_COUNT=5のまま。項目2の
# 定義文言のみCURRENT FACTのデフォルト0件化を反映して更新)。
#
# 既存er013_family_c_future_*_01〜06.pyは一切編集しない(新規ファイル、
# マーカー定数のみ既存モジュールをimportして再利用)。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import er013_family_c_future_writer_02 as fcw2  # マーカー定数のみ再利用(無改変)

IMAGINED_OPEN_TEMPLATE = fcw2.IMAGINED_OPEN_TEMPLATE
IMAGINED_CLOSE = fcw2.IMAGINED_CLOSE
FACT_OPEN_TEMPLATE = fcw2.FACT_OPEN_TEMPLATE
FACT_CLOSE = fcw2.FACT_CLOSE
META_OPEN = fcw2.META_OPEN
META_CLOSE = fcw2.META_CLOSE
MAX_FACT_EXCEPTIONS = fcw2.MAX_FACT_EXCEPTIONS  # 2、無変更のまま再利用(上限のみ、下限ではない)

WORD_TARGET = 350
WORD_ACCEPTABLE_RANGE = (280, 420)  # 目安(約350語)からの許容幅、non-blocking表示用

CONSTRAINT_LIST = [
    "Future(imagined)/Current Factの区別を専用マーカーで示す",
    "Fact Safety(想像上の未来を現在の事実であるかのように書かない/Ledger外の統計を"
    "創作しない/CURRENT FACT文はデフォルト0件とし、その事実自体が記事を明確に"
    "面白くする場合のみ任意で使う。Fact Safetyを証明する目的の統計・研究説明は"
    "本文へ挿入しない)",
    "語数(reader向け本文、約350語)",
    "英語レベル(A2)",
    "Research解説記事に戻さない(場面・語り中心)",
]
CONSTRAINT_COUNT = len(CONSTRAINT_LIST)  # 5(v6と同数。項目2の定義文言のみ更新)

THREE_DIRECTIONS_GOAL = (
    "convenience appeal (why this future feels good and easy)",
    "a quiet shift (a small change in who is really deciding things)",
    "a value-challenging question (something the reader has to sit with afterward)",
)

WRITER_DEVELOPER_MESSAGE = (
    "You are the Writer for an English-learning magazine's 'Future' article family. "
    "Your single most important job is to make the reader genuinely feel the Core "
    "Provocation given to you -- excitement, a little tension, and a question that "
    "stays with them. Do not write a research explainer. Write it as a story: a vivid "
    "imagined future scene (or a small number of scenes) built around the Core "
    "Provocation, not a summary of studies. Never insert a present-day statistic or a "
    "sentence describing research findings into the story just to prove the future is "
    "realistic -- that kind of grounding is checked separately, behind the scenes, and "
    "should almost never appear in the reader-facing text itself."
)

WRITER_PROMPT_TEMPLATE = """[Core Provocation -- this must drive the whole article]
{core_provocation}

[Provocative Future Premise selected for this article]
{premise}

[Theme]
{theme_label}

[Background material -- for your own understanding only, a safety-boundary reference. \
This is NOT material to quote or summarize in the article. Do not feel any obligation \
to mention it]
{ledger_excerpt}

[CURRENT FACT policy -- default is ZERO]
The default is to write the entire article as an imagined future story, with NO
CURRENT FACT sentence at all. Only add ONE wrapped CURRENT FACT sentence (never more
than {max_fact}) if a specific fact from the background material above would, on its
own, make THIS particular story clearly more interesting to a reader -- this should be
rare. Do not add a fact sentence merely to "ground" or "prove" the story is realistic;
that is a separate, behind-the-scenes safety check, not something the reader needs to
see. Never write a sentence in the style of "In 2023, more than..." or "According to
research/a study/a report..." anywhere in the article, whether wrapped in a marker or
not.

[Goal for structure -- a goal, not a rigid template]
Try to let the Core Provocation come through from a few different angles, for example:
- {angle_1}
- {angle_2}
- {angle_3}
You do not have to use exactly these three angles or in this order. Use whatever
narrative shape makes the Core Provocation strongest. Do not dilute the Core
Provocation by turning the angles into three unrelated mini-stories.

[Required markers -- technical, not creative]
- Wrap every clearly imagined future scene in {imagined_open_example} ... {imagined_close}
  (the timeframe can be any short label like "around 2035" or "one ordinary morning,
  a few years from now").
- If (rarely) you use a real, currently-true fact from the material above, wrap ONLY
  that sentence in {fact_open_example} ... {fact_close} (ref_id must match one of the
  material's ids above). Use at most {max_fact} such wrapped sentences in the whole
  article, and only when it clearly makes the story more interesting. Never let a
  {fact_open_prefix} marker appear inside an {imagined_open_prefix} block.
- Never state the imagined future as if it were already true today, and never invent
  specific statistics that are not in the material above.

[Length and level]
- Write for an A2-level English learner: short, clear sentences, common vocabulary,
  simple hedging like "might"/"could"/"If ... , ...".
- Target length for the reader-facing text (markers do not count toward this) is about
  {word_target} words.

{improvement_note}
Write the article now. Do not add a title unless it helps the story -- if you do, keep
it short."""


def build_family_c_writer_v7_prompt(core_provocation: str, premise: str, theme_label: str,
                                     ledger_excerpt: str, improvement_note: str = "") -> str:
    imagined_open_example = IMAGINED_OPEN_TEMPLATE.format(timeframe="around 2035")
    fact_open_example = FACT_OPEN_TEMPLATE.format(ref_id="HR-001")
    imagined_open_prefix = IMAGINED_OPEN_TEMPLATE.split("{timeframe}")[0]
    fact_open_prefix = FACT_OPEN_TEMPLATE.split("{ref_id}")[0]
    note = f"[Improvement note from a previous weaker draft]\n{improvement_note}\n" if improvement_note else ""
    return WRITER_PROMPT_TEMPLATE.format(
        core_provocation=core_provocation, premise=premise, theme_label=theme_label,
        ledger_excerpt=ledger_excerpt, max_fact=MAX_FACT_EXCEPTIONS,
        angle_1=THREE_DIRECTIONS_GOAL[0], angle_2=THREE_DIRECTIONS_GOAL[1], angle_3=THREE_DIRECTIONS_GOAL[2],
        imagined_open_example=imagined_open_example, imagined_close=IMAGINED_CLOSE,
        fact_open_example=fact_open_example, fact_close=FACT_CLOSE,
        fact_open_prefix=fact_open_prefix, imagined_open_prefix=imagined_open_prefix,
        word_target=WORD_TARGET, improvement_note=note,
    )


def generate_family_c_article_v7(client, model: str, reasoning_effort: str, prompt: str) -> dict:
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
        raise RuntimeError("Family C Writer(v7)応答が空です")
    return {"raw_text": text, "model": response.model, "response_id": response.id}
