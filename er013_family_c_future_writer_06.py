# ============================================================
# er013_family_c_future_writer_06.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-V6-CORE-PROVOCATION-REDESIGN-TRIAL-06
# ============================================================
# 目的: v5(見出し3固定/感情変化1/選択1/出来事数/場面順固定/hedging細則
# などが積み重なったPrompt、合計約16項目)を踏まえ、Writerへの制約を
# 最小限(5点)へ絞り直す。Writerの第一目的は、選ばれたCore Provocation
# を読者に最も面白く体験させること。
#
# 数えている制約は以下の5点のみ(CONSTRAINT_LIST参照、v5の16項目と比較
# するため個数をコードで明示管理する):
#   1. Future(imagined) / Current Factの区別を[[IMAGINED: timeframe]]...
#      [[/IMAGINED]] と [[FACT: ref_id]]...[[/FACT]] マーカーで示すこと
#      (マーカー自体はer013_family_c_future_writer_02.pyから無改変で再利用)
#   2. Fact Safety(想像上の未来を現在の事実であるかのように書かない/
#      与えられたLedger以外の統計を creation しない)
#   3. 語数(reader向け本文、マーカー除去後で約350語)
#   4. 英語レベル(A2)
#   5. Research解説記事に戻さない(「研究によると」型の解説構造ではなく、
#      Core Provocationを中心にした場面・語りとして書く)
#
# 見出し数・場面数・感情変化数・選択の数・場面順・出来事数などのv5細則は
# 意図的に指定しない(最初は制約を減らす、というユーザー方針)。
# 3方向(3 Voices)による強化は「目標」としてのみ示し、固定構造として
# 強制しない(3方向を機械的に書き分けさせることは、Core Provocation
# preservationより優先しない)。
#
# 既存er013_family_c_future_*_01〜05.pyは一切編集しない(新規ファイル、
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
MAX_FACT_EXCEPTIONS = fcw2.MAX_FACT_EXCEPTIONS  # 2、無変更のまま再利用

WORD_TARGET = 350
WORD_ACCEPTABLE_RANGE = (280, 420)  # 目安(約350語)からの許容幅、non-blocking表示用

CONSTRAINT_LIST = [
    "Future(imagined)/Current Factの区別を専用マーカーで示す",
    "Fact Safety(想像上の未来を現在の事実であるかのように書かない/Ledger外の統計を創作しない)",
    "語数(reader向け本文、約350語)",
    "英語レベル(A2)",
    "Research解説記事に戻さない(場面・語り中心)",
]
CONSTRAINT_COUNT = len(CONSTRAINT_LIST)  # 5(v5の概算16項目との比較用)

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
    "Provocation, not a summary of studies."
)

WRITER_PROMPT_TEMPLATE = """[Core Provocation -- this must drive the whole article]
{core_provocation}

[Provocative Future Premise selected for this article]
{premise}

[Theme]
{theme_label}

[Verified current-fact material you may draw on -- background guardrail only, not the \
subject of the article. Cite AT MOST {max_fact} of these, and only if it genuinely \
helps ground the story]
{ledger_excerpt}

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
- If you refer to a real, currently-true fact from the material above, wrap ONLY that
  sentence in {fact_open_example} ... {fact_close} (ref_id must match one of the
  material's ids above). Use at most {max_fact} such wrapped sentences in the whole
  article. Never let a {fact_open_prefix} marker appear inside an {imagined_open_prefix}
  block.
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


def build_family_c_writer_v6_prompt(core_provocation: str, premise: str, theme_label: str,
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


def generate_family_c_article_v6(client, model: str, reasoning_effort: str, prompt: str) -> dict:
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
        raise RuntimeError("Family C Writer(v6)応答が空です")
    return {"raw_text": text, "model": response.model, "response_id": response.id}
