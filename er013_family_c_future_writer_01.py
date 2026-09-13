# ============================================================
# er013_family_c_future_writer_01.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-PROTOTYPE-TRIAL-01
# ============================================================
# 目的: 新Family C(Future、独立経路、1人ナレーター)専用のWriter Prompt
# 構築+生成関数。A-Family共通Prompt(Main Story/Point One/Point Two/
# In One Line固定、COMMON_BLOCK_TEMPLATE)、B-Family(複数Voice前提)の
# どちらにも縛られない独立Writerとする(ユーザー決定: 既存A-Familyへの
# 新型追加案は不採用、Family Cとして独立設計)。
#
# 既存A-Family/B-Familyのファイルは一切importしない(独立経路)。
# 想像した未来の場面は、[[IMAGINED: <timeframe>]] ... [[/IMAGINED]]の
# 明示マーカーで区切って書かせる(QA側[er013_family_c_future_qa_01.py]が
# 機械的に抽出・ルーティングするための規約)。
#
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

IMAGINED_OPEN_TEMPLATE = "[[IMAGINED: {timeframe}]]"
IMAGINED_CLOSE = "[[/IMAGINED]]"

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

FAMILY_C_FUTURE_WRITER_DEVELOPER_MESSAGE = (
    "あなたは、聞き手が強くわくわくする、または強い不安を感じる、印象に"
    "残る「未来を描く記事」を書くWriterです。ナレーターは1人です(視点を"
    "複数の話者に切り替えないでください)。この記事は、現在の根拠を解説"
    "する記事ではありません。研究・出典・データの説明を記事の主役にしない"
    "でください。"
)

# ------------------------------------------------------------
# Writer Prompt本体(型固定なし。最低限必要な要素のみ指定する)。
# ------------------------------------------------------------
FAMILY_C_FUTURE_WRITER_PROMPT_TEMPLATE = """テーマ: {topic}

【使ってよい材料(3層Ledger。この範囲外の具体的な現在の事実・数字・
固有名詞を新たに作り出さないでください)】
{three_layer_ledger_text}

【記事の目的】
聞き手が、描かれる未来に強くわくわくする、または強い不安を感じる、
印象に残る記事を書いてください。研究・出典・データの説明は制作時の
裏付けとして使うだけで、聞き手への解説として前面に出さないでください。

【最低限の構成要素(型は固定しません。テーマに最も合う展開を選んで
ください)】
1. 時間軸の宣言: この記事がいつの未来を描くか、記事のどこかで読み手に
   自然に伝わるようにしてください。
2. 未来像(意味のある1〜3通り。Ledgerの[IMAGINED_FUTURE]の材料を使って
   構いません。数合わせの分岐は作らないでください。1通りでも意味が
   あれば十分です): それぞれの未来について、その未来の具体的な姿と、
   そこに至る変化・条件の両方に触れてください。重点はテーマに合わせて
   選んでください。
3. 持ち帰りの一行: 記事の終わりに、聞き手が持ち帰る印象(わくわく/
   不安の余韻)を一行で残してください。事実の要約にしないでください。

構成は##等の短い見出しで区切ってください(後工程での区切り把握のため)。
見出しの文言・数は自由です(Main Story/Point One/Point Two等の固定名は
不要です)。

【想像した未来の場面の書き方(重要)】
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
の外側では、未来を確定事実であるかのように断定しないでください(will/
断定形を使う場合も、記事の文脈から「これは想像・予測である」と聞き手が
理解できるようにしてください)。逆に、現在の事実は、Ledgerの[PRESENT_FACT]
の範囲内で正確に保ってください。

{level_guidance}

英文のみを出力してください(日本語の解説・見出し訳は不要です)。"""


def build_family_c_writer_prompt(topic: str, level: str, three_layer_ledger_text: str) -> str:
    level_key = level.lower()
    if level_key not in LEVEL_GUIDANCE:
        raise ValueError(f"未知のlevel: {level!r}(a2/b1のいずれかを指定してください)")
    imagined_open_example = IMAGINED_OPEN_TEMPLATE.format(timeframe="around 2035")
    return FAMILY_C_FUTURE_WRITER_PROMPT_TEMPLATE.format(
        topic=topic, three_layer_ledger_text=three_layer_ledger_text,
        imagined_open_example=imagined_open_example, imagined_close=IMAGINED_CLOSE,
        level_guidance=LEVEL_GUIDANCE[level_key])


def generate_family_c_article(client, model: str, reasoning_effort: str, prompt: str) -> dict:
    """独立Writer呼び出し(plain text出力、web_search toolなし=Writerは
    Ledger範囲内でのみ執筆する設計。既存A/B-Family Writerと同じ
    responses.create呼び出し構造だが、developer message/promptは完全に
    独立)。"""
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        input=[
            {"role": "developer", "content": FAMILY_C_FUTURE_WRITER_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("Family C Writer応答が空です")
    return {"raw_text": text, "model": response.model, "response_id": response.id}
