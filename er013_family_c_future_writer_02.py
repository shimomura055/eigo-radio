# ============================================================
# er013_family_c_future_writer_02.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-REDESIGN-TRIAL-02
# ============================================================
# 目的: Trial-01(er013_family_c_future_writer_01.py、無編集で保持)からの
# 再設計(作業A項目1「記事構成」・項目3「Writer Prompt」)。ユーザー方針
# 「記事の主役はResearchではなく、未来の生活場面→そこで何が起きるか→
# 人の生活・感情・選択に何をもたらすか→楽しみ/期待/不安/葛藤」に沿い、
# 場面主役の構成へ全面変更する。時点数・間隔・時系列/分岐はテーマ依存で
# Writerに選ばせる(機械的に3時点へ当てはめない)。
#
# 前回→今回の変更点(設計理由は本ファイルdocstring内および
# EDITORIAL-FUTURE-FAMILY-C-REDESIGN-TRIAL-02_REPORT.md参照):
#   - Writerへ渡す材料はWorld Scaffold経由のみ(生の統計・製品名を含む
#     Layer1原文は渡さない、er013_family_c_future_ledger_02.py参照)。
#   - 禁止事項を明文化: 統計値・比率・年次データ・"study/research/survey/
#     report found/show"型表現・製品名/型番/仕様列挙・研究説明構造。
#   - 現在事実の明示的な言及は、World Scaffoldに基づく平易な言い換えで
#     1記事あたり最大2件のみ許可し、[[FACT: <scaffold_id>]]...
#     [[/FACT]]マーカーで明示させる(編集Gate側で機械的に件数カウント)。
#   - 想像場面のマーカー([[IMAGINED: <timeframe>]]...[[/IMAGINED]])は
#     Trial-01から維持(有効な機構として活かす)。
#   - 内部メタ([[META]]...[[/META]]): 時点数・間隔・分岐の選択理由を
#     読者向け本文に出さず、内部監査用メモとして1回だけ出力させる
#     (QA側で抽出・除去し、読者向け本文には一切残さない)。
#
# 既存A-Family/B-Familyのファイルは一切importしない(独立経路)。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

IMAGINED_OPEN_TEMPLATE = "[[IMAGINED: {timeframe}]]"
IMAGINED_CLOSE = "[[/IMAGINED]]"
FACT_OPEN_TEMPLATE = "[[FACT: {ref_id}]]"
FACT_CLOSE = "[[/FACT]]"
META_OPEN = "[[META]]"
META_CLOSE = "[[/META]]"

MAX_FACT_EXCEPTIONS = 2

LEVEL_GUIDANCE = {
    "a2": (
        "A2レベル: 短く明確な文を使ってください。仮定・未来のhedgingは"
        "\"might\"/\"could\"/明確な条件節(\"If ... , ...\")のような単純な"
        "形を使ってください。1文はできるだけ1つの内容にとどめてください。"
    ),
    "b1": (
        "B1レベル: A2よりやや複雑な文・仮定法・条件構文を使ってよいですが、"
        "難解な専門語は避けてください。仮定・未来のhedgingは\"might\"/"
        "\"could\"に加え、やや複雑な仮定法(\"If this trend continued, "
        "cities could ...\"のような)も使ってよいです。"
    ),
}

FAMILY_C_FUTURE_WRITER_V2_DEVELOPER_MESSAGE = (
    "あなたは、聞き手が強くわくわくする、または強い不安を感じる、印象に"
    "残る「未来を描く記事」を書くWriterです。ナレーターは1人です(視点を"
    "複数の話者に切り替えないでください)。この記事の主役は、未来の生活"
    "場面・そこで人に起きること・人の生活や感情や選択への影響・楽しみや"
    "期待や不安や葛藤です。Researchや現在の事実の解説を記事の主役に"
    "しないでください。"
)

# ------------------------------------------------------------
# Writer Prompt本体(場面主役の構成。型は固定しない)。
# ------------------------------------------------------------
FAMILY_C_FUTURE_WRITER_V2_PROMPT_TEMPLATE = """テーマ: {topic}

【使ってよい材料(この範囲外の具体的な現在の事実・数字・固有名詞・
製品名を新たに作り出さないでください)】
{world_package_text}

【記事の主役(最重要)】
この記事の主役は、未来の生活場面・そこで何が起きるか・それが人の生活や
感情や選択にもたらすもの・楽しみや期待や不安や葛藤です。Research・現在の
事実・統計・製品情報は、その未来像を無根拠にしないための内部の足場に
すぎません。読者に説明する必要がなければ、本文には出さないでください。

【固く禁止する表現(1つでも本文に出た場合、記事は不合格になります)】
- 統計値・比率・パーセンテージ・年次データ・具体的な販売台数や調査対象
  人数などの数字(想像した未来の時間軸を表す表現[例: "around 2035"、
  "a decade from now"]は数字を含んでも構いません。禁止されるのは調査・
  統計・過去/現在の実績データとしての数字です)。
- "study/studies/research/survey/report/researcher/scientist"のような、
  研究・調査であることを示す語、および"found/shows/showed/suggests/
  indicates/according to"のような研究結果を読者へ説明する言い回し。
- 製品名・型番・企業名・ブランド名の列挙。
- Researchの結果を読者へ解説する構造(「〜という調査結果があります」
  「〜という研究が示しています」のように、記事が現在の根拠を説明する
  ための記事になること)。

【現在の事実に触れてよい例外(最大{max_fact_exceptions}件のみ)】
未来像の説得力にどうしても必要で、読者に説明が必要な現在の事実がある
場合に限り、記事全体で最大{max_fact_exceptions}件まで、Worldscaffoldの
statementを平易に言い換えた一文として本文に含めてよいです。その場合は
必ず次の形式で挟んでください(数字・出典・固有名詞は入れないでください、
Worldscaffoldの言い換えのみ):

{fact_open_example}
(ここに、Worldscaffoldのいずれか1項目を平易に言い換えた1文。数字・
出典・固有名詞は含めないでください。)
{fact_close}

このマーカーを使わない現在事実への言及(地の文でさりげなく現在の様子に
触れる程度の1文)は、統計・研究・製品情報でない限り問題ありません。

【最低限の構成要素(型は固定しません。テーマに最も合う展開を選んで
ください)】
1. 入口: 統計から始めず、いきなり生活場面から始めてください。時間軸
   (いつの未来を描くか)は、場面の中で自然に伝わるようにしてください。
2. 場面で起きること: 具体的な未来の場面で、何が起きるかを描いてください。
3. 人の生活・感情・選択への影響: その出来事が、登場する人(または聞き手
   自身)の生活・感情・選択にどう影響するかを描いてください。
4. 楽しみ/期待/不安/葛藤: 読み手が持つであろう感情の対立や揺れを描いて
   ください。
5. 時点数・間隔・分岐の選び方はテーマ依存です。数年後→10年後のような
   複数時点、複数の別の未来(希望/不安などの分岐)、単一の時点を深く描く
   構成、のいずれでも構いません。機械的に3時点へ当てはめる必要は
   ありません(Layer2/3材料のimagined_futuresを全て使い切る必要はなく、
   このテーマに最も意味のある未来変化を選んでください)。
6. 持ち帰りの一行: 記事の終わりに、聞き手が持ち帰る印象(わくわく/
   不安の余韻)を一行で残してください。事実の要約にしないでください。

構成は##等の短い見出しで区切ってください(後工程での区切り把握のため)。
見出しの文言・数は自由です。

【想像した未来の場面の書き方】
具体的な未来の場面・情景を描くときは、必ず次の形式で挟んでください:

{imagined_open_example}
(ここに、その場面の英語の本文。読み手が「これは想像された未来だ」と
自然に理解できる入口の一文から始めてください。例: "Picture a Tuesday
evening in 2035, when ..."のような、時間軸を含む自然な導入文。マーカー
内部は、通常の記事のように一文ごとに"might"を繰り返す必要はありません。
自然で引き込まれる語りにしてください。ただし、この場面の中で「現在は
既に〜だ」という現在の事実の主張を新たに作らないでください。)
{imagined_close}

上記のマーカー(角括弧2つ)は、実際に本文中にそのまま書いてください
(このマーカーは最終読者向け出力では自動的に取り除かれます)。マーカー
の外側では、未来を確定事実であるかのように断定しないでください。

【内部メモ(読者には見せません)】
本文の最後に、以下の形式で内部メモを1つだけ書いてください(読者向け
出力からは自動的に完全に取り除かれます)。なぜこの時点数・間隔・
分岐構成を選んだかを1〜2文で説明してください:

{meta_open}
(この記事の時点数・間隔・分岐構成を選んだ理由。1〜2文。)
{meta_close}

{level_guidance}

英文のみを出力してください(日本語の解説・見出し訳は不要です)。"""


def build_family_c_writer_v2_prompt(topic: str, level: str, world_package_text: str,
                                     gate_feedback: str = "") -> str:
    level_key = level.lower()
    if level_key not in LEVEL_GUIDANCE:
        raise ValueError(f"未知のlevel: {level!r}(a2/b1のいずれかを指定してください)")
    imagined_open_example = IMAGINED_OPEN_TEMPLATE.format(timeframe="around 2035")
    fact_open_example = FACT_OPEN_TEMPLATE.format(ref_id="WS-003")
    prompt = FAMILY_C_FUTURE_WRITER_V2_PROMPT_TEMPLATE.format(
        topic=topic, world_package_text=world_package_text,
        max_fact_exceptions=MAX_FACT_EXCEPTIONS,
        fact_open_example=fact_open_example, fact_close=FACT_CLOSE,
        imagined_open_example=imagined_open_example, imagined_close=IMAGINED_CLOSE,
        meta_open=META_OPEN, meta_close=META_CLOSE,
        level_guidance=LEVEL_GUIDANCE[level_key])
    if gate_feedback:
        prompt += (
            "\n\n【前回の下書きが編集Gateで不合格になった理由(必ず今回は"
            "避けてください)】\n" + gate_feedback
        )
    return prompt


def generate_family_c_article_v2(client, model: str, reasoning_effort: str, prompt: str) -> dict:
    """独立Writer呼び出し(plain text出力、web_search toolなし)。"""
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        input=[
            {"role": "developer", "content": FAMILY_C_FUTURE_WRITER_V2_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("Family C Writer(v2)応答が空です")
    return {"raw_text": text, "model": response.model, "response_id": response.id}
