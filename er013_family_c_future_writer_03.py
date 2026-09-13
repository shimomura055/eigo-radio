# ============================================================
# er013_family_c_future_writer_03.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-FINAL-TUNING-TRIAL-03
# ============================================================
# 目的: er013_family_c_future_writer_02.py(無編集のまま保持)からの
# 最終調整。ユーザー方針(2026-09-13、本ファイルヘッダのREPORT参照):
# 「Trial-02で解消済みの構成(統計冒頭/study found型研究説明/製品名列挙/
# 研究解説感)は維持したまま、(a)想像枠内のhedging過多を抑える、
# (b)わくわく/不安/葛藤の感情強度を上げる、(c)A2を標準分量へ近づける、
# を行う。Fact Safetyは一切弱めない、研究解説っぽさを再流入させない」。
#
# --- Trial-02実データからの発見(本タスクで実施した根拠確認) ---
# er013_output/family_c_future_trial_02/{a2,b1}/writer_raw_article.txt を
# 実際に解析した結果、[[IMAGINED: ...]]枠そのものは既にhedging少なめ・
# 現在形の情景描写になっていた(A2: 枠内59文中hedge語0件)。一方、
# hedging過多(may/could/might多用)は、各[[IMAGINED]]ブロックの直後に
# 続く「その場面が引き起こす反応・葛藤」の段落(枠外)に集中していた
# (例: "At first, this could feel like freedom. A person might stop
# thinking about the floor every evening. A room could become ready for
# guests..."、A2で枠外hedge語54件)。つまりTrial-02の設計では、特定の場面に
# 直結する人物の反応・選択・葛藤までもが「枠外の一般論」として扱われ、
# 既存の境界原則(枠外では未来を断定しない)によりhedgingを強いられていた。
# この発見を踏まえ、本v3では「特定の想像場面から直接生まれる反応・感情・
# 選択」は、その場面の[[IMAGINED]]枠を広げて枠内に含めるよう明示的に
# Writerへ指示する(枠を細切れにせず、場面+その場面の直接的な余波までを
# 1つの想像単位として書く)。複数の場面・テーマ全体にまたがる一般的な
# 示唆・まとめは、従来どおり枠外でhedging付きのまま維持する(境界原則
# 自体は緩めない)。
#
# --- A2標準分量の根拠 ---
# CURRENT_SPEC.mdをGrepしたが、A-FamilyのA2本文に対する明示的な語数
# ターゲット数値(hard word_count target)は見つからなかった(見つかった
# のはA2英語ナレーション速度「約135 WPMを目安」という音声速度目安のみ、
# CURRENT_SPEC.md 573行目)。ユーザー指示書が例示した「450〜600語」を
# Family C A2の目安としてそのまま採用し(本ファイル・REPORTで根拠を
# 明記した近似値であり、新しいProduction仕様として正式化するものでは
# ない)、B1はA2よりやや長い自然な分量として500〜700語を目安とする。
# 実測: Trial-02の word_count は A2=1161語/B1=1145語で、この目安の
# 約2倍に達していた(短縮対象)。
#
# 既存A-Family/B-Familyのファイルは一切importしない(独立経路、Trial-01
# /02と同じ方針)。writer_02のマーカー定数のみ再利用しimportする(値の
# 二重管理を避けるため)。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import er013_family_c_future_writer_02 as fcw2

IMAGINED_OPEN_TEMPLATE = fcw2.IMAGINED_OPEN_TEMPLATE
IMAGINED_CLOSE = fcw2.IMAGINED_CLOSE
FACT_OPEN_TEMPLATE = fcw2.FACT_OPEN_TEMPLATE
FACT_CLOSE = fcw2.FACT_CLOSE
META_OPEN = fcw2.META_OPEN
META_CLOSE = fcw2.META_CLOSE
MAX_FACT_EXCEPTIONS = fcw2.MAX_FACT_EXCEPTIONS

# Trial限定の目安(CURRENT_SPECに明示のA2 word_count正式値は無いため、
# ユーザー指示書の例示値をそのまま採用。恒久Production仕様ではない)。
WORD_COUNT_TARGET_RANGE = {
    "a2": (450, 600),
    "b1": (500, 700),
}

LEVEL_GUIDANCE = {
    "a2": (
        "A2レベル: 短く明確な文を使ってください。[[IMAGINED]]の枠外・"
        "移行文での仮定・未来のhedgingは\"might\"/\"could\"/明確な条件節"
        "(\"If ... , ...\")のような単純な形を使ってください。1文はできる"
        "だけ1つの内容にとどめてください。"
        f"英文本文(マーカーを除いた読者向け本文)の分量は、全体で"
        f"{WORD_COUNT_TARGET_RANGE['a2'][0]}〜{WORD_COUNT_TARGET_RANGE['a2'][1]}"
        "語程度を目安にしてください(超過している場合は、場面や感情の"
        "描写を削るのではなく、重複した言い回し・説明的な接続文を削って"
        "短くしてください)。"
    ),
    "b1": (
        "B1レベル: A2よりやや複雑な文・仮定法・条件構文を使ってよいですが、"
        "難解な専門語は避けてください。[[IMAGINED]]の枠外・移行文での仮定・"
        "未来のhedgingは\"might\"/\"could\"に加え、やや複雑な仮定法"
        "(\"If this trend continued, cities could ...\"のような)も使って"
        "よいです。"
        f"英文本文(マーカーを除いた読者向け本文)の分量は、全体で"
        f"{WORD_COUNT_TARGET_RANGE['b1'][0]}〜{WORD_COUNT_TARGET_RANGE['b1'][1]}"
        "語程度を目安にしてください(超過している場合は、場面や感情の"
        "描写を削るのではなく、重複した言い回し・説明的な接続文を削って"
        "短くしてください)。"
    ),
}

FAMILY_C_FUTURE_WRITER_V3_DEVELOPER_MESSAGE = fcw2.FAMILY_C_FUTURE_WRITER_V2_DEVELOPER_MESSAGE

# ------------------------------------------------------------
# Writer Prompt本体(v2から継承。想像枠の書き方・感情強度・分量の3点を
# 調整。禁止語リスト・FACT例外・META・境界原則はv2のまま無変更で維持)。
# ------------------------------------------------------------
FAMILY_C_FUTURE_WRITER_V3_PROMPT_TEMPLATE = """テーマ: {topic}

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
- 記事を短くするために、場面や感情の描写を削って上記の研究解説的な
  要約表現へ戻すこと(分量調整は、重複した言い回し・説明的な接続文を
  削ることで行ってください)。

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
   ください。各場面につき最低1回は、人物が感じる具体的な楽しみ・不安・
   葛藤を、行動または短い台詞(セリフ)で示してください(単なる形容詞の
   羅列[例: "この状況は不安だ"]ではなく、何をした/何を言ったかで示す)。
   記事のどこかで、期待・希望と、不安・懸念という2つの感情の対立を
   はっきり対比させてください。
5. 時点数・間隔・分岐の選び方はテーマ依存です。数年後→10年後のような
   複数時点、複数の別の未来(希望/不安などの分岐)、単一の時点を深く描く
   構成、のいずれでも構いません。機械的に3時点へ当てはめる必要は
   ありません(Layer2/3材料のimagined_futuresを全て使い切る必要はなく、
   このテーマに最も意味のある未来変化を選んでください)。
6. 持ち帰りの一行: 記事の終わりに、聞き手が持ち帰る印象(わくわく/
   不安の余韻)を一行で残してください。事実の要約にしないでください。

構成は##等の短い見出しで区切ってください(後工程での区切り把握のため)。
見出しの文言・数は自由です。

【想像した未来の場面の書き方(重要な変更点)】
具体的な未来の場面・情景を描くときは、必ず次の形式で挟んでください:

{imagined_open_example}
(ここに、その場面の英語の本文。読み手が「これは想像された未来だ」と
自然に理解できる入口の一文から始めてください。例: "Picture a Tuesday
evening in 2035, when ..."のような、時間軸を含む自然な導入文。)
{imagined_close}

この枠の中では、入口の一文で既に「これは想像だ」と示せているため、
"might"/"could"/"may"/"perhaps"/"possibly"のようなhedging語を使う
必要はありません。現在形・断定調で、情景・人物の行動・選択・感情を
はっきりと描いてください(例: "The robot pauses. She watches it,
unsure whether to help."のように)。

**この枠は、場面の情景描写だけで終わらせず、その場面から直接生まれる
人物の反応・気持ち・その場での選択までを、同じ枠の中に含めてください**
(例: 場面の中でロボットが失敗し、その場でその人がどう感じ、次に
何をするかまでを枠内で描く)。枠を閉じるのは、その1つの具体的な場面
から離れ、複数の場面にまたがる一般的な示唆・まとめ・別の話題へ移る
ときにしてください。ただし、この場面の中で「現在は既に〜だ」という
現在の事実の主張を新たに作らないでください。

枠を離れて一般的な示唆・まとめを書くとき(例: 「もしこうした変化が
広がれば」)は、従来どおり"might"/"could"のようなhedgingや"If ... ,
..."の条件節を使い、未来を確定事実であるかのように断定しないで
ください。

上記のマーカー(角括弧2つ)は、実際に本文中にそのまま書いてください
(このマーカーは最終読者向け出力では自動的に取り除かれます)。

【内部メモ(読者には見せません)】
本文の最後に、以下の形式で内部メモを1つだけ書いてください(読者向け
出力からは自動的に完全に取り除かれます)。なぜこの時点数・間隔・
分岐構成を選んだかを1〜2文で説明してください:

{meta_open}
(この記事の時点数・間隔・分岐構成を選んだ理由。1〜2文。)
{meta_close}

{level_guidance}

英文のみを出力してください(日本語の解説・見出し訳は不要です)。"""


def build_family_c_writer_v3_prompt(topic: str, level: str, world_package_text: str,
                                     gate_feedback: str = "") -> str:
    level_key = level.lower()
    if level_key not in LEVEL_GUIDANCE:
        raise ValueError(f"未知のlevel: {level!r}(a2/b1のいずれかを指定してください)")
    imagined_open_example = IMAGINED_OPEN_TEMPLATE.format(timeframe="around 2035")
    fact_open_example = FACT_OPEN_TEMPLATE.format(ref_id="WS-003")
    prompt = FAMILY_C_FUTURE_WRITER_V3_PROMPT_TEMPLATE.format(
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


def generate_family_c_article_v3(client, model: str, reasoning_effort: str, prompt: str) -> dict:
    """独立Writer呼び出し(plain text出力、web_search toolなし)。v2と同一の
    呼び出し形状(developer message・引数)を再利用する。"""
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        input=[
            {"role": "developer", "content": FAMILY_C_FUTURE_WRITER_V3_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    text = response.output_text
    if not text or not text.strip():
        raise RuntimeError("Family C Writer(v3)応答が空です")
    return {"raw_text": text, "model": response.model, "response_id": response.id}
