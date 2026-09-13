# ============================================================
# er013_family_c_future_writer_05.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-V5-EMOTION-RECOVERY-AND-CONSTRAINT-STABILITY-TRIAL-05
# ============================================================
# 目的: er013_family_c_future_writer_04.py(無編集のまま保持)からの
# respec。Trial-04の残課題(B1で統合示唆段落が2場面の間に挿入され、
# "will"を含む未hedge断定文が複数出現しFuture Framing QA v2が
# REVIEW_REQUIRED)と、Fable直読による所見(A2が出来事列挙化し感情強度が
# Trial-03比で2→1に後退)への対処として、以下5点をv4契約に追加する
# (ユーザー指示書が列挙した5項目をそのまま検証する初回アーム)。
#
# --- v4→v5の変更点 ---
# 1. 場面内に感情の"起伏"1つ(v4は「感情1つに限定」という静的な指定
#    だったため、結果として1感情語を置くだけで満たせてしまい、Trial-04で
#    出来事列挙+末尾感情語1つ、という後退を招いた。v5では「1つの感情
#    状態から別の状態への変化」を明示的に要求する)。
# 2. 場面内に明確な"選択"1つ(行動またはセリフで示す、具体的な二択的
#    選択。単なる心情描写ではなく、実際に何をした/言ったかで示す)。
# 3. 出来事列挙の上限(1場面あたり具体的な出来事は3つ程度までとし、
#    それ以上の細かい動作の連続列挙を避ける、というPrompt上のガイダンス。
#    ハードGateではなく目安。実測はcount_events_per_scene()で診断)。
# 4. 統合示唆段落の配置固定(2つ目の[[IMAGINED]]ブロックが閉じた直後、
#    記事の3つ目[最後]の見出しの中でのみ。1つ目と2つ目の場面の
#    あいだに統合示唆・一般論を書かないことを明示)。記事の見出し数を
#    3つに固定する構造契約へ変更(v4は見出し数を自由としていた)。
# 5. 枠外(3つ目の見出し全体)でのhedging契約: "will"のような断定的な
#    未来助動詞を明示的に禁止し、"might"/"could"/"may"または"If ... ,
#    ..."の条件節を使うことを明示する(v4は一般的なhedging指示のみで、
#    "will"を名指しで禁止していなかった)。
#
# 上記5点はいずれもv4契約(禁止表現・FACT例外・[[IMAGINED]]枠内の書き方
# の原則[反応・選択まで枠内に含める、枠内hedging不要]・語数目安)に
# "追加"するものであり、既存の安全側の設計(Fact Safety・数値/研究語/
# 製品名禁止)は一切変更しない。
#
# 場面選択(select_scenes_for_v4)・World Package絞り込み(build_trimmed_
# world_package_text)はv4の決定的ロジック(¥0、非LLM)をそのまま再利用
# する(v5独自ロジックではないため、writer_04からimportする。編集はしない)。
#
# 既存A-Family/B-Family・既存er013_*_01/_02/_03/_04は一切import変更・
# 編集しない(writer_02のマーカー定数、writer_03の呼び出し関数、
# writer_04の場面選択/World Package絞り込みロジックのみ再利用)。
# Status: Trial専用、未承認draft実装(`APPROVED_FOR_PRODUCTION`ではない)。
# ============================================================
from __future__ import annotations

import er013_family_c_future_writer_02 as fcw2
import er013_family_c_future_writer_03 as fcw3  # generate_family_c_article_v3()を再利用(汎用関数、v5専用ロジックなし)
import er013_family_c_future_writer_04 as fcw4  # select_scenes_for_v4/build_trimmed_world_package_textを再利用(¥0、非LLM、v5でも無変更)

IMAGINED_OPEN_TEMPLATE = fcw2.IMAGINED_OPEN_TEMPLATE
IMAGINED_CLOSE = fcw2.IMAGINED_CLOSE
FACT_OPEN_TEMPLATE = fcw2.FACT_OPEN_TEMPLATE
FACT_CLOSE = fcw2.FACT_CLOSE
META_OPEN = fcw2.META_OPEN
META_CLOSE = fcw2.META_CLOSE
MAX_FACT_EXCEPTIONS = fcw2.MAX_FACT_EXCEPTIONS

# v4の決定的ロジックをそのまま再輸出(v5 run scriptから参照するため)。
select_scenes_for_v5 = fcw4.select_scenes_for_v4
build_trimmed_world_package_text = fcw4.build_trimmed_world_package_text

# generate_family_c_article_v3()は developer message・引数を汎用的に扱う
# ため、v5でもそのまま再利用する(重複実装を避ける、v3/v4と同じ方針)。
generate_family_c_article_v5 = fcw3.generate_family_c_article_v3

# Trial限定の目安(v4の380-520/450-620から変更しない。語数超過問題は
# v4で既に解消済みであり、v5の目的は感情・没入感の回復であって語数
# 目安自体の再調整ではないため)。
WORD_COUNT_TARGET_RANGE = {
    "a2": (380, 520),
    "b1": (450, 620),
}

# 場面あたりの語数目安(prompt内の目安表示用、hard gateではない。v4から
# 無変更。実際の語数gateはWORD_COUNT_TARGET_RANGE[level]の記事全体
# レンジのみ)。
PER_SCENE_WORD_BUDGET_GUIDANCE = {
    "a2": 110,
    "b1": 140,
}
SYNTHESIS_PARAGRAPH_WORD_BUDGET_GUIDANCE = {
    "a2": 70,
    "b1": 90,
}

# 1場面あたりの出来事数の目安(ハードGateではなく、Prompt上のガイダンス
# としてのみ使用。診断はer013_family_c_future_qa_05.count_events_per_
# scene()で行う[non-blocking])。
PER_SCENE_EVENT_COUNT_GUIDANCE = 3


LEVEL_GUIDANCE_V5 = {
    "a2": (
        "A2レベル: 短く明確な文を使ってください。3つ目の見出し(統合示唆・"
        "持ち帰りの一行)での仮定・未来のhedgingは\"might\"/\"could\"/"
        "明確な条件節(\"If ... , ...\")のような単純な形を使ってください。"
        "1文はできるだけ1つの内容にとどめてください。"
        f"英文本文(マーカーを除いた読者向け本文)の分量は、全体で"
        f"{WORD_COUNT_TARGET_RANGE['a2'][0]}〜{WORD_COUNT_TARGET_RANGE['a2'][1]}"
        "語程度を目安にしてください(超過している場合は、場面や感情の"
        "描写を削るのではなく、重複した言い回し・説明的な接続文を削って"
        "短くしてください)。"
        f"各[[IMAGINED]]場面は、目安として{PER_SCENE_WORD_BUDGET_GUIDANCE['a2']}語程度"
        "までにまとめてください。"
    ),
    "b1": (
        "B1レベル: A2よりやや複雑な文・仮定法・条件構文を使ってよいですが、"
        "難解な専門語は避けてください。3つ目の見出し(統合示唆・持ち帰りの"
        "一行)での仮定・未来のhedgingは\"might\"/\"could\"に加え、やや"
        "複雑な仮定法(\"If this trend continued, cities could ...\"の"
        "ような)も使ってよいです。"
        f"英文本文(マーカーを除いた読者向け本文)の分量は、全体で"
        f"{WORD_COUNT_TARGET_RANGE['b1'][0]}〜{WORD_COUNT_TARGET_RANGE['b1'][1]}"
        "語程度を目安にしてください(超過している場合は、場面や感情の"
        "描写を削るのではなく、重複した言い回し・説明的な接続文を削って"
        "短くしてください)。"
        f"各[[IMAGINED]]場面は、目安として{PER_SCENE_WORD_BUDGET_GUIDANCE['b1']}語程度"
        "までにまとめてください。"
    ),
}

FAMILY_C_FUTURE_WRITER_V5_DEVELOPER_MESSAGE = fcw2.FAMILY_C_FUTURE_WRITER_V2_DEVELOPER_MESSAGE

# ------------------------------------------------------------
# Writer Prompt本体(v4から継承。変更点: 見出し数を3つに固定し、
# 場面ごとの役割・出来事数上限・感情の起伏・明確な選択を明示、統合示唆
# 段落の配置を「2つ目の場面の直後、3つ目の見出しの中でのみ」に固定、
# 3つ目の見出し全体での"will"禁止を明示。禁止語リスト・FACT例外・META・
# [[IMAGINED]]枠内の書き方の原則(反応・選択まで枠内に含める・hedging
# 不要)はv4から無変更で維持する)。
# ------------------------------------------------------------
FAMILY_C_FUTURE_WRITER_V5_PROMPT_TEMPLATE = """テーマ: {topic}

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

【記事の構成(3つの見出しに固定、重要な変更点)】
【使ってよい材料】の[IMAGINED_FUTURE]に列挙されている場面(2つ)を
使い、記事全体を必ず次の3つの見出しで構成してください(見出しの文言は
自由ですが、見出しの"数"は3つに固定してください。4つ以上にも
2つ以下にもしないでください)。
1. 1つ目の見出し: 1つ目の場面(変化が始まったばかりの時期、主に期待・
   意欲寄り)だけを描いてください。他の場面や、複数場面にまたがる
   一般的な示唆・まとめをこの見出しに混ぜないでください。
2. 2つ目の見出し: 2つ目の場面(変化が定着したあとの時期、主に葛藤・
   懸念寄り)だけを描いてください。ここにも一般的な示唆・まとめを
   混ぜないでください。
3. 3つ目の見出し(最後の見出し): 2つの場面が終わったあとの統合示唆
   段落と、持ち帰りの一行だけを書いてください。新しい場面の情景描写は
   ここに含めないでください。

【各場面(1つ目・2つ目の見出しそれぞれ)の書き方(重要な変更点)】
- 出来事は{per_scene_event_count}つ程度までに絞ってください(それ以上の
  細かい動作を次々と列挙しないでください。少ない出来事を、感情・選択
  とともに深く描くことを優先してください)。
- 場面の中で、感情が動く様子("起伏")を1つ描いてください。1つの感情語を
  置くだけでは不十分です。1つの感情状態から別の状態へ変化する様子
  (例: 期待から軽い苛立ちへ、安心から戸惑いへ)を、行動または短い
  台詞で示してください。
- 場面の中で、登場人物が明確に何かを選ぶ場面を1つ含めてください
  (例: 手伝うか待つか、続けるか止めるか、というような具体的な選択を、
  実際に何をした/何を言ったかで示す。心の中の迷いの説明だけで終わらせ
  ないでください)。

【想像した未来の場面の書き方】
具体的な未来の場面・情景を描くときは、必ず次の形式で挟んでください:

{imagined_open_example}
(ここに、その場面の英語の本文。読み手が「これは想像された未来だ」と
自然に理解できる入口の一文から始めてください。例: "Picture a Tuesday
evening in 2035, when ..."のような、時間軸を含む自然な導入文。)
{imagined_close}

この枠の中では、入口の一文で既に「これは想像だ」と示せているため、
"might"/"could"/"may"/"perhaps"/"possibly"のようなhedging語を使う
必要はありません。現在形・断定調で、情景・人物の行動・選択・感情の
起伏をはっきりと描いてください。

**この枠は、場面の情景描写だけで終わらせず、その場面から直接生まれる
人物の感情の起伏と、その場での明確な選択までを、同じ枠の中に含めて
ください**。枠を閉じるのは、その1つの具体的な場面から離れ、複数の
場面にまたがる一般的な示唆・まとめ・別の話題へ移るときにしてください。
ただし、この場面の中で「現在は既に〜だ」という現在の事実の主張を新たに
作らないでください。

【3つ目の見出し(統合示唆段落)の位置(重要な変更点)】
統合示唆段落は、2つ目の[[IMAGINED]]ブロックが閉じた直後から、3つ目
(最後)の見出しの中で始めてください。1つ目と2つ目の場面のあいだに、
統合示唆・一般論・まとめを書かないでください。期待・希望と、不安・
懸念という2つの感情の対立の対比は、この統合示唆段落の中で1回だけ
行ってください(個々の場面の中では、この対比を繰り返さないでください)。

【3つ目の見出し全体でのhedging契約(重要な変更点)】
3つ目の見出し全体([[IMAGINED]]枠の外側、統合示唆段落と持ち帰りの一行を
含む)では、"will"のような断定的な未来助動詞を一切使わないでください。
未来について述べるときは、必ず"might"/"could"/"may"のいずれか、または
"If ... , ..."のような明確な条件節を使ってください(例: "the quiet
house will still be waiting"のような文は禁止、"the quiet house might
still be waiting"のように書き換えてください)。

【持ち帰りの一行】
記事の終わりに、聞き手が持ち帰る印象(わくわく/不安の余韻)を一行で
残してください。事実の要約にしないでください。この一行にも上記の
hedging契約を適用してください。

構成は##等の短い見出しで区切ってください(後工程での区切り把握のため。
見出しは必ず3つにしてください)。

【内部メモ(読者には見せません)】
本文の最後に、以下の形式で内部メモを1つだけ書いてください(読者向け
出力からは自動的に完全に取り除かれます)。各場面の感情の起伏・選択を
どう設計したかを1〜2文で説明してください:

{meta_open}
(各場面の感情の起伏・選択をどう設計したか。1〜2文。)
{meta_close}

{level_guidance}

英文のみを出力してください(日本語の解説・見出し訳は不要です)。"""


def build_family_c_writer_v5_prompt(topic: str, level: str, world_package_text: str,
                                     gate_feedback: str = "") -> str:
    level_key = level.lower()
    if level_key not in LEVEL_GUIDANCE_V5:
        raise ValueError(f"未知のlevel: {level!r}(a2/b1のいずれかを指定してください)")
    imagined_open_example = IMAGINED_OPEN_TEMPLATE.format(timeframe="around 2035")
    fact_open_example = FACT_OPEN_TEMPLATE.format(ref_id="WS-003")
    prompt = FAMILY_C_FUTURE_WRITER_V5_PROMPT_TEMPLATE.format(
        topic=topic, world_package_text=world_package_text,
        max_fact_exceptions=MAX_FACT_EXCEPTIONS,
        fact_open_example=fact_open_example, fact_close=FACT_CLOSE,
        imagined_open_example=imagined_open_example, imagined_close=IMAGINED_CLOSE,
        meta_open=META_OPEN, meta_close=META_CLOSE,
        per_scene_event_count=PER_SCENE_EVENT_COUNT_GUIDANCE,
        level_guidance=LEVEL_GUIDANCE_V5[level_key])
    if gate_feedback:
        prompt += (
            "\n\n【前回の下書きが編集Gateで不合格になった理由(必ず今回は"
            "避けてください)】\n" + gate_feedback
        )
    return prompt
