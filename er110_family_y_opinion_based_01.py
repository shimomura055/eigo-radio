# -*- coding: utf-8 -*-
"""er110_family_y_opinion_based_01.py
FAMILY-Y-VOICES-DESIGN-01 委任_18 Phase 2: 『実在意見ベースの3 Voice生成Trial』のDEV/Trial専用runner(日本語R0)。

位置づけ(重要):
  - **未配線のDEV/Trial module**。どのProduction runner・既存er110 moduleからもimportされない(testでGrep固定)。
    import時にAPI呼出0・ファイル副作用0・client生成0。環境変数・flag・CLI引数でProduction挙動が変わる経路はない
    (環境変数読取り・コマンド行引数の解釈を一切使わない。run先は固定、引数なし)。
  - 既存 er110_family_y_persona_pipeline_01.py / er110_family_y_persona_text_trial_01.py / er110_family_y_text_trial_01.py は**無変更**。
    本fileは API入口・構造タグ(pl.tag_structure/structure_fire)・Leakage Gate(pl.run_gate_pl)・記号QA・Ctx等を import して呼出で再利用し、
    OPUS_REVIEW_04のOF-Y6-04/05/06に従い、**Voice Promptだけを本file内に複製して3か所(規則4・7・9)を置換**する
    (これはDEV経路内の変更で、Production Prompt(X/Z)の編集ではない)。
  - 新しい合格基準・閾値は作らない。決定論部分は『出典IDの照合(UNMAPPED検出)』と『予算の歯止め(累計27円で新規呼出停止)』のみ。

流れ(1 process = 1 run、再起動なし):
  Persona Sheet(実在意見から手で転記済み=SHEETS) -> Voice x3(並列, gpt-6.1-sol) -> 出典対応の付番(gpt-6-luna)と機械照合
  -> UNMAPPEDのVoiceだけ各1回再生成 -> 構造タグ(発火なら該当1本を1回だけ再生成) -> Voices Leakage Gate -> 最終の出典対応(記録のみ) -> R0 markdown
  (Tension Gateは省略。Tension/Closing自体も作らない: 本Phaseは3 Voiceのみ)
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

import er053_family_x_factlock_ja_writer_01 as w1
import er110_family_y_text_trial_01 as y0
import er110_family_y_persona_text_trial_01 as p
import er110_family_y_persona_pipeline_01 as pl

MANAGEMENT_ID = "FAMILY-Y-VOICES-DESIGN-01"
THEME_TAG = "FAMILY_Y_OPINION_BASED_01"
y0.THEME_TAG = THEME_TAG       # cost loggerのstageタグ(本process内のみ差替え。plのimport後に設定)
MODEL_TOP = pl.MODEL_TOP        # gpt-6.1-sol(最新世代最上位系)
MODEL_CHEAP = pl.MODEL_CHEAP    # gpt-6-luna(機械照合用の付番・構造タグ・Leakage判定。理由=低コストで足りる判定・付番のみ)
SLOTS = pl.SLOTS

RUN_DIR = "er110_output/family_y_opinion_based_01/sns_age_limit/run_01"
LEDGER_MD = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_01/BUDGET_LOG_OB_01.md"
BUDGET_STOP_JPY = 27.0          # OF-Y6-08: Phase 2累計がこの額に達したら新規呼出を止める
SLOT_HEADING = {"voice_1": "One Voice", "voice_2": "Another Voice", "voice_3": "A Third Voice"}
SLOT_OWNER = {"voice_1": "ONE", "voice_2": "TWO", "voice_3": "THREE"}

# ============================================================
# World frame(0円・agent作成。status_quoは空=統計・数字・制度の事実を本文に入れない)
# ============================================================
WORLD_FRAME = {
    "question_ja": "日本で、子どものSNS利用に、年齢による制限や禁止を設けるべきか。",
    "title_ja": "子どものSNS、それぞれの声",
    "setting": {"country": "日本", "institution_type": "SNS(動画やメッセージのやり取りができるアプリを含む)", "population": "子どもと、その家族", "era": "現在"},
    "status_quo": [],
    "shared_premise_ja": "日本の話。SNSには、動画やメッセージのやり取りができるアプリも含める。",
    "premise_variants": [],
    "fact_scopes": {"domestic": [], "foreign_reference_only": [], "out_of_scope": []},
    "distinctions": [
        {"term_ja": "年齢による制限", "definition_ja": "一定の年齢になるまで、使い方や機能に決まりを設けること。"},
        {"term_ja": "利用禁止", "definition_ja": "一定の年齢になるまで、アカウントを持つこと自体を認めないこと。"},
        {"term_ja": "年齢確認", "definition_ja": "アカウントを作る時に、本人の年齢や身元を確かめること。"},
    ],
    "unverified": [],
    "self_check_ja": ["国は日本。外国の制度・統計・数字は使わない。", "出来事は経験欄にあるものだけ。"],
}

# 導入文(固定文=API 0円。OF-Y6-10: 実在の人物ではなく複数の公開意見をもとに構成した、の趣旨。Voiceごとの出典説明は入れない)
INTRO_JA = "これから聞くのは、実在の特定の人の話ではない。ネットなどで公開されている複数の意見をもとに、組み立てた声だ。"

# ============================================================
# Persona Sheet(実在の声から転記。根拠は source_ids。TBSのみが根拠の項目はtbs_only。PERSONAS_02.mdの転記表と一致させる)
#   kind: E=出来事・具体的な事情を含む声 / O=意見・見方の声。IDは英字のみ(Voice本文に数字が出る誘因を避ける)
# ============================================================
def _it(i, kind, sources, text):
    return {"id": i, "kind": kind, "source_ids": list(sources), "text_ja": text}


SHEETS = {
    "voice_1": {
        "gender": "女性", "age_label": "小さい子どもを育てている親(年齢は明示しない)",
        "role_ja": "小さい子どもを育てている親",
        "daily_life_ja": "子どもを見守りながら暮らしている(出来事は経験欄にあるものだけ)",
        "contact_point_ja": "子どもの動画やアプリの使い方を、親として見守り、設定する立場",
        "experiences": [
            _it("ONE_a", "E", ["MR-T010-05"], "刺激の強いコンテンツや課金のしくみを、子どもが興味のままに選んでしまうことが、実際にあった。本人に話をすると、じゃあやらない、となることも多い。"),
            _it("ONE_b", "E", ["MR-T015-06"], "時間制限を決めていても、やめられない。終わったあとは、イライラしてしまう。(本文に主語はない。子どもの様子として語るのが自然だが断定しない)"),
            _it("ONE_c", "E", ["MR-T003-09"], "親の見守り機能の設定は、結構ややこしかった。子どもがどうしても使いたいという時に、もっと簡単に対応できるといいと思う。"),
            _it("ONE_d", "E", ["TBS-07"], "長い移動の時など、静かにしてほしい時に、子どもが見てくれていると正直助かる。制限がかかると、親もしんどくなる時がある。"),
            _it("ONE_e", "O", ["MR-T015-10"], "大人であってもやめられないことがあるので、全面的に制限があるべきだ、という考え。"),
            _it("ONE_f", "O", ["MR-T008-02"], "いじめや中傷、危ない人との接触に遭う頻度は変わらなくても、子どもは危険を危険と気づかない、助けを求められない、ということがありそう。しかも恩恵は少ない。"),
        ],
        "troubles_ja": "見守りの設定が分かりにくい。制限をかけると、使えない時の対応が自分に返ってくる。",
        "wishes_honest_ja": "はっきりした制限があると安心できる。ただ、静かにしてほしい時に助かっている自分もいる。",
        "wishes_public_ja": "子どもを危険から守りたい。",
        "emotion_habit_ja": "白状するように認める。自分の都合にも気づいて、少し引っかかる。",
        "values_ja": "子どもが危険に気づけない・助けを求められないことが心配。",
        "interests_ja": "見守りの設定や、使いたい時の対応が簡単であってほしい。制限が自分の負担に返らないでほしい。",
        "contradiction_or_weakness_ja": "制限を望む一方で、静かにしてほしい時には自分も画面に助けられている。大人でもやめられないと言いながら、自分も例外ではない。",
        "speech_style": {
            "first_person": "私",
            "sentence_length_pattern_ja": "短い断片をつなぐように事実を並べ、途中で言い直す(実在の声の、事実を短く並べて言い切らない言い方を言い換えたもの)",
            "question_back_frequency_ja": "ほとんどしない",
            "assertion_or_hedging_ja": "言い切りと言い淀みが半々。自分の都合を認める所は声が小さくなる",
            "vocabulary_layer_ja": "日常の子育ての言葉。くだけすぎず、硬くもない",
        },
        "entry_mood_ja": "ある出来事を、事実のまま短く置くところから入る",
        "opening_type": "出来事・場面の描写から",
        "identity_cue_ja": "小さい子どもがいる親であることを、経験欄の内容に沿って自然に出す(子の名前・年齢の細部・新しい場面は足さない)",
        "claim_core_ja": "子どもには、はっきりした制限があるほうが安心できる。ただ、自分も画面に助けられている時があって、制限の話は自分にも返ってくる。",
        "known_fact_id": "", "known_fact_usage_ja": "",
    },
    "voice_2": {
        "gender": "男性", "age_label": "高校生(学年・年齢は明示しない)",
        "role_ja": "高校生",
        "daily_life_ja": "友達との連絡にSNSを使う年代の高校生(出来事は経験欄にあるものだけ)",
        "contact_point_ja": "親の見守りや、規制の対象になる側",
        "experiences": [
            _it("TWO_a", "O", ["MR-T010-02"], "投稿を見られるのは安心感がなく、SNSの良さも消えてしまう感じがする。投稿まで保護者が見えるのをルールにするのは少し嫌。でも、悪口や脅しに対面した時にすぐ大人につなぐのは欠かせないとも思う。難しいが、微調整が必要だと思っている。"),
            _it("TWO_b", "O", ["MR-T033-02"], "保護者には知られたくない内容もある。利用者を意識しないルール作りでは、抜け道を探されて、作った意味がなくなる。"),
            _it("TWO_c", "O", ["MR-T041-03"], "未成年である以上、保護者の監視は仕方がない。でも、過度な規制や監視は、かえって子どもが心を閉ざす原因になる。闇雲にルールを作るのはやめてほしい。"),
            _it("TWO_d", "O", ["MR-T019-03"], "あれもダメこれもダメと制限されると、我慢するばかりで発散する場がなく、制限が外れた時に、今まで我慢していたものが一気に出てしまう。"),
            _it("TWO_e", "E", ["MR-T017-04"], "高校生でアカウントを作れないと、模試などの登録の時に困る。"),
            _it("TWO_f", "O", ["MR-T101-02"], "今は子ども同士がSNSのアカウントで連絡を取ることが多いので、年齢で制限をかけることには反対。別の対策として、安全フィルターをかけるなどがいいと思う。"),
            _it("TWO_g", "O", ["MR-T010-17"], "スマホはあくまで親に与えられたものだから、家庭にとって望ましくない使われ方をしているなら避けるべき。それは多くの場合、依存や中毒だと思う。"),
            _it("TWO_h", "E", ["TBS-02"], "友達同士で、しばらくスマホを見ないなんてできる?と聞き合って、できない、と笑う。"),
        ],
        "troubles_ja": "親に投稿まで見られると、SNSの良さが消える。かといって、悪口や脅しの時に大人につなげないのも困る。",
        "wishes_honest_ja": "見張られすぎたくない。禁止も強すぎないでほしい。",
        "wishes_public_ja": "未成年だから保護者の監視は仕方がない、と受け止めている。",
        "emotion_habit_ja": "嫌だと思う気持ちを口にしながら、言いながら考えて、自分で留保を足す。",
        "values_ja": "信頼されること。ただし、本当に困った時には大人に頼れること。",
        "interests_ja": "親に見られすぎないこと。模試などの登録ができること。友達と連絡が取れること。",
        "contradiction_or_weakness_ja": "投稿を見られるのは嫌なのに、悪口や脅しの時には、大人につなげることが欠かせないと思っている。",
        "speech_style": {
            "first_person": "僕",
            "sentence_length_pattern_ja": "言いながら迷いを重ねる長い一文が1つあり、ほかは短く言い直す(実在の声の、逆接をつないで迷いを言葉にする長い一文を言い換えたもの)",
            "question_back_frequency_ja": "ほとんどしない",
            "assertion_or_hedging_ja": "留保が多い。最後は、微調整が必要、のようにやわらかく収める",
            "vocabulary_layer_ja": "高校生の普通の話し言葉",
        },
        "entry_mood_ja": "投稿まで見られるのは少し嫌だ、という本音をそのまま口にするところから入る",
        "opening_type": "感情・本音の吐露から",
        "identity_cue_ja": "高校生であることを、年代や学校への軽い言及で自然に出す(新しい場面・親との会話は足さない)",
        "claim_core_ja": "見張られすぎるのも、禁止が強すぎるのも逆効果だと思う。でも、悪口や脅しの時にすぐ大人につなげる仕組みは欠かせないので、微調整してほしい。",
        "known_fact_id": "", "known_fact_usage_ja": "",
    },
    "voice_3": {
        "gender": "女性", "age_label": "中学生(学年は明示しない)",
        "role_ja": "中学生",
        "daily_life_ja": "学校に通う中学生(出来事は経験欄にない。意見と仮定で語る)",
        "contact_point_ja": "自分たちの年代に、SNSの目安があるかどうかの当事者",
        "experiences": [
            _it("THREE_a", "O", ["MR-T157-01"], "今の未成年はSNSの使い方をまだ理解できていないと思う。SNSに関する教育が十分になるまでは、未成年のSNSには規制をしておいたほうがいい。"),
            _it("THREE_b", "O", ["MR-T026-01"], "未成年でも、一定の年齢になって、保護者の監督のもとなら、やってもいいと思う。それより下の年齢はよくない。(元の本文は年齢の数字で区切っている。数字は語りに出さない)"),
            _it("THREE_c", "O", ["MR-T158-01"], "DMの機能など、小学生や中学生だと不安だけれど、高校生ならある程度は判断できるだろう、という機能が多い。"),
            _it("THREE_d", "O", ["MR-T014-13"], "自分で良し悪しを判断できるようになってから、アカウントを作れるようになるべきだと思う。"),
            _it("THREE_e", "O", ["MR-T049-02"], "本人確認をしておけば、匿名のアカウントでも、誹謗中傷のような軽率な言動を抑えられる。"),
            _it("THREE_f", "O", ["MR-T058-01"], "同じ教室に、SNSを自由に使える子と使えない子がいた場合、自由に使える子たちだけでグループができて、使えない子はそこから排除されるかもしれない。(本文はここまで。規制への賛否は本文からは言えないので、この項目だけで結論を作らない)"),
            _it("THREE_g", "O", ["MR-T020-05"], "保護者がすべて管理できるとは限らないので、最低ラインは国が決める。(高校生の声)"),
        ],
        "troubles_ja": "判断がつかないまま使うと、危ないことや、教室での排除が起きるかもしれない。",
        "wishes_honest_ja": "判断できるようになるまでは、はっきりした目安があってほしい。",
        "wishes_public_ja": "未成年を守るために、社会として最低ラインを決めてほしい。",
        "emotion_habit_ja": "迷わず、静かに言い切る。理由を短く積んで、落ち着いて話す。",
        "values_ja": "判断できるようになってから使うこと。使えない子が排除されないこと。",
        "interests_ja": "共通の目安があること。教室で使える子・使えない子に分かれないこと。",
        "contradiction_or_weakness_ja": "なし(迷わず言い切る人。迷い・例外・自己ツッコミを足さない)",
        "speech_style": {
            "first_person": "わたし",
            "sentence_length_pattern_ja": "中くらいの長さの文を、理由を短く積むように並べる(実在の声の、理由をつなげて言い切る運びを言い換えたもの)",
            "question_back_frequency_ja": "しない",
            "assertion_or_hedging_ja": "と思う、べき、で迷いなく言い切る。留保や例外を足さない",
            "vocabulary_layer_ja": "中学生の普通の話し言葉。硬すぎない",
        },
        "entry_mood_ja": "自分の考えを、最初の1文ではっきり言うところから入る",
        "opening_type": "主張・意見の表明から",
        "identity_cue_ja": "中学生であることを、年代への軽い言及で自然に出す(新しい場面・友達の出来事は足さない)",
        "claim_core_ja": "自分で判断できるようになるまでは、社会として共通の目安や最低ラインがあったほうがいい。迷いはない。",
        "known_fact_id": "", "known_fact_usage_ja": "",
    },
}
for _s in SHEETS.values():
    for _x in _s["experiences"]:
        _x["tbs_only"] = bool(_x["source_ids"]) and all(i.startswith("TBS") for i in _x["source_ids"])

OPENING_GUIDE = {
    "出来事・場面の描写から": "語り出しは、経験欄にある出来事を1つ、事実のまま短く置くことから始める(新しい場面・人物・会話は足さない)。",
    "感情・本音の吐露から": "語り出しは、この争点についての自分の気持ち・本音をそのまま口にすることから始める。他の誰かの言い分を打ち消す言い方(〜と言うけど、〜じゃなくて)で始めない。",
    "主張・意見の表明から": "語り出しは、自分の考えを最初の1文ではっきり言うことから始める。他の誰かの言い分を打ち消す言い方で始めない。",
}

# 補った表現の種別(出典を持たず、編集で足してよい範囲。人物・会話・出来事は含まない)
SUPP_KINDS = ("口調・言い回し", "感情の言い方", "年代・立場の手がかり", "仮定・意見の言い換え", "聞き手への呼びかけ・つなぎ", "なし")


def allowed_ids(slot: str) -> list:
    return [x["id"] for x in SHEETS[slot]["experiences"]]


def event_ids(slot: str) -> list:
    return [x["id"] for x in SHEETS[slot]["experiences"] if x["kind"] == "E"]


# ============================================================
# Voice Prompt(VOICE_PROMPT_TMPLを複製。置換: 規則4(場面描写・相手の言葉)・規則7(伝聞例)・規則9(感覚的細部の補足可)。OF-Y6-04)
#   残置: 規則1・2・3(語り出しの型を追記)・5・6・8・10・11。Production(X/Z)のPromptではない。
# ============================================================
VOICE_PROMPT_OB = """次の人物「本人」が、ラジオで自分の考えを語る、一人称の語りを1段落だけ書いてください。

テーマ: @@QUESTION@@
【3人に共通の前提(この前提で語る)】
@@PREMISE@@
【区別の定義(取り違えない)】
@@DISTINCTIONS@@

【人物(Persona。本文に全項目を説明しない。背景は言い方・内容・感情に自然に現れればよい)】
@@SHEET@@

【語りの作り方(厳守)】
1. 約260〜300字。話し言葉の常体(「〜だ」「〜なんだ」「〜と思う」「〜だよね」など)。「です・ます」調にしない。新聞・教材のような文章にしない。
2. 冒頭の3文以内に、この人物がどんな人か(立場・年代など)が聞き手に自然に分かる手がかりを入れる。手がかり: @@CUE@@。「私は〜の者です」「〜をしています」のような自己紹介の文は書かない。
3. 本人として、自由に主観的に語る。調査や事実の説明・言い換えにしない。理屈の正しさより「この人が本当にそう言いそうか」を優先する。聞き終えた人が「この人は何を言いたいのか」を一言で言えるようにする。@@OPENING@@語りの順序や結び方は決めず、この人の話し方から自然に決める。「矛盾・弱さ」が「なし」の人物は、迷い・例外・自己ツッコミを足さず、言い切る。
4. 具体論(出典ルール): 人物の「経験・意見」欄(IDつき)にある内容だけを材料にし、1つ、多くても2つだけを選ぶ。具体的な出来事・場面・人物・相手の言葉は、「経験・意見」欄に書かれている範囲のものだけを使い、物・場所・時間帯・相手の言葉・自分の動きを新しく足さない。相手や自分の言葉は、欄に書かれている場合だけ、括弧を使わず地の文に溶かして書く。欄に出来事がない人物は、出来事を作らず、仮定(もし〜なら)・意見・感想の形で語る。抽象名詞(責任・価値・判断・根拠・余地・視点・基準など)で言い換えない。1文に抽象名詞は2つまで。
5. 気持ちが動くところがあれば、感情の名前を並べず、言い方・行為・間に出す。ただし行為は「経験・意見」欄にあるものか、話し方・間の工夫だけにする。
6. 「話し方」(文の長さ・問い返し・断言/留保・語彙)を、実際の文に反映する。自分や聞き手への問いかけの文は、文末を「？」にする。
7. 世の中の出来事の扱い: 人物が書けるのは、「経験・意見」欄にある個別の出来事と意見だけ。「この前」「ある子が」「友達が」「先生が」のように、欄にない人物や出来事を新しく作らない(伝聞も作らない)。「多くの人が〜」「最近は〜が増えている」のような、頻度・傾向・原因の一般化は、欄にない限り書かない。人の気持ちや考え方を推測で述べるときは、「〜と思う」「〜気がする」のように本人の推測だと分かる形にする。
8. 事実を使う場合は、本人が主語の伝聞・印象で1文だけ、数字・調査名・年月を使わず、論証の根拠にしない。調査・研究・報告が主語の文は書かない。@@FACT@@
9. 数字(算用数字・漢数字の数量表現)を使わない。実在の人名・組織名・製品名・出来事を出さない。「経験・意見」欄にない出来事(誰が何と言った、何があった)を新しく作らない。補ってよいのは、口調・言い回し・感情の言い方だけで、人物・会話・出来事・場所・物の追加はしない。
10. 役割語(〜じゃ、〜わよ、〜ぜ等)・方言の演出・擬音・過度な感嘆・泣き笑い・「！」の連発をしない。比喩は多くても1つ。
11. 括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字を使わない。

出力はこの人物の語りの本文のみ(見出し・ラベル・説明なし。1段落)。"""


def render_persona_ob(sheet: dict, who_ja: str) -> str:
    """OF-Y6-05: 『成人』『{age}歳』の固定出力をやめ、age_labelを使う(未成年に対応)。経験欄はID・種別つき(出典IDは書かない)。"""
    ss = sheet["speech_style"]
    ex = "\n".join(f"  - [{x['id']}] ({'出来事を含む声' if x['kind'] == 'E' else '意見の声'}) {x['text_ja']}" for x in sheet["experiences"])
    return (f"人物: {who_ja}(声は{sheet['gender']}の{sheet['age_label']}。一人称は「{ss['first_person']}」)\n役割・生活: {sheet['role_ja']}。{sheet['daily_life_ja']}\n"
            f"この争点との接点: {sheet['contact_point_ja']}\n経験・意見(ここにある内容だけを材料にする):\n{ex}\n困りごと: {sheet['troubles_ja']}\n"
            f"本音: {sheet['wishes_honest_ja']} / 建前: {sheet['wishes_public_ja']}\n感情の癖: {sheet['emotion_habit_ja']}\n大切にしていること: {sheet['values_ja']}\n"
            f"利害: {sheet['interests_ja']}\n矛盾・弱さ: {sheet['contradiction_or_weakness_ja']}\n"
            f"話し方(英語にしても残る型):\n  - 文の長さ: {ss['sentence_length_pattern_ja']}\n  - 問い返し: {ss['question_back_frequency_ja']}\n  - 断言/留保: {ss['assertion_or_hedging_ja']}\n"
            f"  - 語彙の層: {ss['vocabulary_layer_ja']}\n語り出しの気分: {sheet['entry_mood_ja']}\nこの人が言いたいことの芯(方向性。そのまま読み上げず、本人の言葉で): {sheet['claim_core_ja']}")


WHO_JA = {"voice_1": "小さい子どもを育てている親", "voice_2": "高校生", "voice_3": "中学生"}


def build_voice_prompt_ob(wf: dict, slot: str, emphasize: bool = False) -> str:
    sheet = SHEETS[slot]
    ds = "\n".join(f"- {d['term_ja']}: {d['definition_ja']}" for d in wf.get("distinctions", [])) or "(なし)"
    fact = "知っている事実はない。調査・統計・制度・他の国や組織の動きにはふれない(経験・意見の欄の内容だけで語る)。"
    opening = f"冒頭の型(指定): {sheet['opening_type']}。{OPENING_GUIDE[sheet['opening_type']]} "
    prompt = (VOICE_PROMPT_OB.replace("@@QUESTION@@", wf["question_ja"]).replace("@@PREMISE@@", wf["shared_premise_ja"]).replace("@@DISTINCTIONS@@", ds)
              .replace("@@SHEET@@", render_persona_ob(sheet, WHO_JA[slot])).replace("@@CUE@@", sheet["identity_cue_ja"]).replace("@@FACT@@", fact)
              .replace("@@OPENING@@", opening))
    if emphasize:
        prompt += (f"\n\n【今回の追加指示】この人の語り出しの気分「{sheet['entry_mood_ja']}」と冒頭の型「{sheet['opening_type']}」を、語り出し・展開・結びの全体に強く反映する。"
                   "他の人の語りと似た起伏・結びにならないよう、この人の話し方と気分から出てくる流れにする。出典ルール(欄にない出来事を作らない)は変えない。")
    return prompt


# ============================================================
# 出典対応の機械照合(OF-Y6-07)
# ============================================================
EVENT_WORD_RE = re.compile(r"(この前|このあいだ|この間|先日|昨日|さっき|あの時|あのとき|ある日|あるとき|言われ|頼まれ|怒られ|叱られ|聞かれ|見られた|取り上げ|してくれ|してきた|してた|しちゃった|だった|でした|ていた|ました)")
PAST_END_RE = re.compile(r"た(?:[。？！]|$)")
PAST_EXCLUDE_RE = re.compile(r"(思った|感じた|気がした|分かった|わかった|知った|考えた|気づいた|気付いた|なった|だった。?$)")
HYPO_RE = re.compile(r"(もし|たら|なら(?!ない)|れば|かもしれ|かも|だろう|はず|べき|ほうがいい|ありそう|ないと)")


def event_like(sentence: str) -> bool:
    if EVENT_WORD_RE.search(sentence):
        return True
    return bool(PAST_END_RE.search(sentence) and not PAST_EXCLUDE_RE.search(sentence))


MAP_DEVELOPER = "あなたは、語りの各文が、与えられた根拠メモのどの項目に基づくかを付番する検査者です。内容の良し悪しは評価せず、付番だけを行います。"

SCHEMA_MAP = pl._schema(
    "yob_provenance_map",
    items=pl._arr(pl._obj(idx=pl._INT, source_ids=pl._arr(pl._STR), supplement_kinds=pl._arr(pl._enum(*SUPP_KINDS)), is_event_claim=pl._BOOL, note_ja=pl._STR)))


def build_map_prompt(slot: str, sentences: list) -> str:
    memo = "\n".join(f"- [{x['id']}] ({'出来事を含む声' if x['kind'] == 'E' else '意見の声'}) {x['text_ja']}" for x in SHEETS[slot]["experiences"])
    sup = "\n".join(f"- {k}" for k in SUPP_KINDS if k != "なし")
    body = "\n".join(f"{i}: {s}" for i, s in enumerate(sentences))
    return f"""次の語り(一人称)の各文について、根拠メモのどの項目に基づくかを付番してください。

【根拠メモ(この人物が語ってよい経験・意見)】
{memo}

【補った表現の種別(出典ではなく編集で足してよい範囲。人物・会話・出来事は含まない)】
{sup}

【語り(文ごとに番号付き)】
{body}

【付番の規則】
- すべての文を、idx=0から順に1件ずつ出力する。
- source_ids: その文の内容が基づく根拠メモのID(複数可)。根拠メモにない出来事・場面・人物・会話・数量を含む文には、無理にIDを付けず空配列にし、is_event_claim を true にする。
- supplement_kinds: 口調・感情の言い方・つなぎなど、出典を持たない補いが文に含まれるときに種別を付ける。補いがなければ「なし」だけを入れる。
- note_ja: 判断の根拠を一言で。"""


def check_mapping(slot: str, sentences: list, parsed: dict) -> dict:
    """luna付番を機械照合。UNMAPPED = (許可リスト外のID) or (IDも補い種別もない) or (出来事らしい文でE-IDがなく仮定・意見の形でもない) or (is_event_claimでIDなし) or (付番漏れ)。"""
    allow, ev = set(allowed_ids(slot)), set(event_ids(slot))
    tbs_only = {x["id"] for x in SHEETS[slot]["experiences"] if x["tbs_only"]}
    by = {}
    for it in parsed.get("items", []):
        by[it["idx"]] = it
    rows, unmapped, tbs_rows = [], [], []
    for i, s in enumerate(sentences):
        it = by.get(i)
        reasons = []
        if it is None:
            ids, supp, claim = [], [], False
            reasons.append("NOT_LABELED")
        else:
            ids, supp, claim = list(it["source_ids"]), [k for k in it["supplement_kinds"] if k != "なし"], bool(it["is_event_claim"])
        bad = [x for x in ids if x not in allow]
        if bad:
            reasons.append("ID_NOT_IN_ALLOWLIST:" + ",".join(bad))
        ev_like = event_like(s)
        if it is not None and not ids and not supp:
            reasons.append("NO_ID_NO_SUPPLEMENT")
        if claim and not ids:
            reasons.append("EVENT_CLAIM_WITHOUT_ID")
        if ev_like and not (set(ids) & ev) and not HYPO_RE.search(s):
            reasons.append("EVENT_LIKE_WITHOUT_E_ID")
        verdict = "UNMAPPED" if reasons else ("補った表現のみ" if not ids else "OK")
        rows.append({"idx": i, "text": s, "source_ids": ids, "supplement_kinds": supp, "is_event_claim": claim, "event_like": ev_like, "reasons": reasons, "verdict": verdict,
                     "note": (it or {}).get("note_ja", "")})
        if reasons:
            unmapped.append(i)
        if ids and all(x in tbs_only for x in ids):
            tbs_rows.append(i)
    return {"slot": slot, "n_sentences": len(sentences), "n_unmapped": len(unmapped), "unmapped_idx": unmapped, "tbs_only_idx": tbs_rows, "rows": rows}


def split_sentences(text: str) -> list:
    return [s.strip() for s in p.SENT_SPLIT_RE.split(text) if s.strip()]


# ============================================================
# 予算の歯止め・台帳(OF-Y6-08)
# ============================================================
def cost_jpy(rd: str) -> float:
    import glob
    import er053_cost_aggregate_01 as ca      # 遅延import(importでgenai等を読まない)
    return round(sum(ca.compute_stage_cost_breakdown_multi(f)["total_jpy"] for f in glob.glob(f"{rd}/raw_usage_log*.jsonl")), 3)


def stage_costs(rd: str) -> dict:
    import glob
    import er053_cost_aggregate_01 as ca
    out = {}
    for f in glob.glob(f"{rd}/raw_usage_log*.jsonl"):
        for k, v in ca.compute_stage_cost_breakdown_multi(f)["by_stage_jpy"].items():
            out[k] = round(out.get(k, 0.0) + v, 3)
    return out


class Run:
    def __init__(self, rd: str, ledger_md: str = LEDGER_MD):
        self.rd, self.ledger_md = rd, ledger_md
        self.seen: dict = {}
        self.t0 = time.time()
        self.trace: list = []

    def guard(self, note: str):
        if os.path.exists(os.path.join(self.rd, "STOP")):
            raise pl.PipelineStop("STOP_SENTINEL", f"{self.rd}/STOP が存在する({note})")
        c = cost_jpy(self.rd)
        if c >= BUDGET_STOP_JPY:
            raise pl.PipelineStop("BUDGET_STOP_27", f"Phase 2累計 {c} JPY >= {BUDGET_STOP_JPY} JPY のため新規呼出を止める({note})", {"cost_jpy": c})
        return c

    def flush(self, label: str):
        """新しく発生したstage費用を台帳(md)とtraceに追記する。"""
        cur = stage_costs(self.rd)
        new = {k: round(v - self.seen.get(k, 0.0), 3) for k, v in cur.items() if round(v - self.seen.get(k, 0.0), 3) > 0}
        self.seen = cur
        total = round(sum(cur.values()), 3)
        ent = {"label": label, "new_stage_costs_jpy": new, "run_total_jpy": total, "elapsed_s": round(time.time() - self.t0, 1)}
        self.trace.append(ent)
        w1.wj(os.path.join(self.rd, "budget_trace.json"), self.trace)
        os.makedirs(os.path.dirname(self.ledger_md), exist_ok=True)
        with open(self.ledger_md, "a", encoding="utf-8") as f:
            for k, v in sorted(new.items()):
                f.write(f"| {label} | {k} | {v} | {total} |\n")
        print(f"[OB] {label}: +{round(sum(new.values()), 3)} JPY run_total={total} JPY elapsed={ent['elapsed_s']}s", flush=True)
        return ent


# ============================================================
# 生成・付番・再生成
# ============================================================
def generate_voice_ob(ctx: pl.Ctx, run: Run, wf: dict, slot: str, *, extra: str = "", emphasize: bool = False, tag: str = "") -> dict:
    """Voice 1本を別callで生成。構造契約/記号QA違反は1回だけ再生成(既存generate_voice_plと同じ機構)。残ればYStop。"""
    prompt = build_voice_prompt_ob(wf, slot, emphasize) + extra
    fp = SHEETS[slot]["speech_style"]["first_person"]
    cur, hist, calls = prompt, [], []
    for k in (1, 2):
        run.guard(f"{slot}{tag} try{k}")
        raw, meta = pl.call_text(ctx, stage=f"ob_{slot}{tag}" + ("" if k == 1 else "_regen"), model=MODEL_TOP, effort="high", developer=pl.VOICE_DEVELOPER, user=cur)
        calls.append(meta)
        probs = []
        try:
            final, sym = p._fin(raw)
            probs += pl.check_voice_pl(final, fp)
            if pl.safety.symbol_gate_requires_stop(sym):
                probs.append(f"SYMBOL:{sym}")
            if {t for m in w1.TAG_RE.finditer(raw) for t in w1.tag_ids(m.group(0))}:
                probs.append("UNEXPECTED_FACT_TAG")
        except w1.TagLeak as e:
            final, probs = "", [f"TAG_LEAK:{e}"]
        hist.append(probs)
        if not probs:
            return {"slot": slot, "text": final, "raw": raw, "calls": calls, "problems_per_try": hist, "monitors": pl.voice_monitors_pl(final, fp),
                    "prompt_sha256": w1.sha_text(prompt), "prompt": prompt}
        if k == 1:
            cur = prompt + "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {x}" for x in probs)
    raise y0.YStop("VOICE_CONTRACT_STOP", f"{slot}: 再生成後も契約違反 {hist[-1]}", hist)


def map_voice(ctx: pl.Ctx, run: Run, slot: str, text: str, stage: str) -> dict:
    run.guard(f"map {slot} {stage}")
    sents = split_sentences(text)
    r = pl.call_json(ctx, stage=f"ob_map_{slot}_{stage}", model=MODEL_CHEAP, effort="medium", developer=MAP_DEVELOPER, user=build_map_prompt(slot, sents), schema=SCHEMA_MAP)
    res = check_mapping(slot, sents, r["parsed"])
    res["meta"] = r["meta"]
    res["stage"] = stage
    return res


def unmapped_extra(mp: dict) -> str:
    bad = "\n".join(f"- {mp['rows'][i]['text']}(理由: {','.join(mp['rows'][i]['reasons'])})" for i in mp["unmapped_idx"])
    return ("\n\n【前回の出力の問題(今回は避けてください)】\n次の文は、「経験・意見」欄にない出来事・場面・人物・会話を含むか、欄の項目に対応づけられませんでした。\n" + bad +
            "\n「経験・意見」欄にある内容だけで語り直してください。欄に出来事がない場合は、出来事を作らず、仮定・意見・感想の形にしてください。")


def run_pipeline(client, rd: str, *, wf: dict = None, ledger_md: str = LEDGER_MD) -> dict:
    wf = wf or WORLD_FRAME
    os.makedirs(rd, exist_ok=True)
    ctx = pl.Ctx(client, rd, "ob")
    run = Run(rd, ledger_md)
    state = {"management_id": MANAGEMENT_ID, "models": {"writer": MODEL_TOP, "judge": MODEL_CHEAP}, "stages": {}}

    def save():
        w1.wj(os.path.join(rd, "state.json"), state)

    # ---- 1. Voice x3 並列生成 ----
    run.guard("start")
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {s: ex.submit(generate_voice_ob, ctx, run, wf, s) for s in SLOTS}
        gen = {s: f.result() for s, f in futs.items()}
    texts = {s: gen[s]["text"] for s in SLOTS}
    state["stages"]["gen"] = {s: {"text": texts[s], "monitors": gen[s]["monitors"], "problems_per_try": gen[s]["problems_per_try"], "prompt_sha256": gen[s]["prompt_sha256"]} for s in SLOTS}
    for s in SLOTS:
        w1.wt(os.path.join(rd, f"{s}_prompt.txt"), gen[s]["prompt"])
    save()
    run.flush("gen")
    # ---- 2. 出典対応の付番+機械照合 ----
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {s: ex.submit(map_voice, ctx, run, s, texts[s], "m1") for s in SLOTS}
        maps = {s: f.result() for s, f in futs.items()}
    state["stages"]["map1"] = {s: {k: v for k, v in maps[s].items() if k != "meta"} for s in SLOTS}
    save()
    run.flush("map1")
    # ---- 3. UNMAPPEDのVoiceだけ各1回再生成(構造より優先) ----
    regen_unmapped = {}
    todo = [s for s in SLOTS if maps[s]["n_unmapped"] > 0]
    if todo:
        with ThreadPoolExecutor(max_workers=3) as ex:
            futs = {s: ex.submit(generate_voice_ob, ctx, run, wf, s, extra=unmapped_extra(maps[s]), tag="_unmapregen") for s in todo}
            g2 = {s: f.result() for s, f in futs.items()}
        run.flush("unmapped_regen")
        with ThreadPoolExecutor(max_workers=3) as ex:
            futs = {s: ex.submit(map_voice, ctx, run, s, g2[s]["text"], "m2") for s in todo}
            m2 = {s: f.result() for s, f in futs.items()}
        for s in todo:
            regen_unmapped[s] = {"before": texts[s], "after": g2[s]["text"], "n_unmapped_before": maps[s]["n_unmapped"], "n_unmapped_after": m2[s]["n_unmapped"],
                                 "problems_per_try": g2[s]["problems_per_try"]}
            texts[s] = g2[s]["text"]
            gen[s] = g2[s]
            maps[s] = m2[s]
        run.flush("map2")
    state["unmapped_regen"] = regen_unmapped
    save()
    # ---- 4. 構造タグ(発火なら該当1本を1回だけ再生成。再生成後のUNMAPPEDは記録のみ) ----
    run.guard("structure1")
    tag1 = pl.tag_structure(ctx, texts, "ob_structure1")
    run.flush("structure1")
    struct_regen, tag2 = None, None
    if tag1["fire"]["fired"]:
        s = tag1["fire"]["regenerate_slot"]
        g3 = generate_voice_ob(ctx, run, wf, s, emphasize=True, tag="_structregen")
        run.flush("structure_regen")
        m3 = map_voice(ctx, run, s, g3["text"], "m3")
        struct_regen = {"slot": s, "before": texts[s], "after": g3["text"], "n_unmapped_after": m3["n_unmapped"]}
        texts[s] = g3["text"]
        gen[s] = g3
        maps[s] = m3
        tag2 = pl.tag_structure(ctx, texts, "ob_structure2")      # 記録のみ(2回目の是正はしない)
        run.flush("structure2_map3")
    state["structure"] = {"tags_before": {k: v for k, v in tag1.items() if k != "meta"}, "regen": struct_regen, "tags_after": ({k: v for k, v in tag2.items() if k != "meta"} if tag2 else None)}
    save()
    # ---- 5. Voices Leakage Gate(Tension Gateは省略)。予算が22円を超えていればGateをskipして記録(書換がsol呼出で膨らむため) ----
    gate_status, final = None, dict(texts)
    c_now = cost_jpy(rd)
    if c_now > 22.0:
        gate_status = "SKIPPED_BUDGET"
    else:
        run.guard("gate")
        personas_text = {s: render_persona_ob(SHEETS[s], WHO_JA[s]) for s in SLOTS}
        fps = {s: SHEETS[s]["speech_style"]["first_person"] for s in SLOTS}
        gate = pl.run_gate_pl(ctx, kind="voices", stage="ob_voices_gate", texts=texts, out_dir=os.path.join(rd, "gate_voices"), wf=wf, personas_text=personas_text, first_persons=fps)
        gate_status, final = gate["status"], dict(gate["final_texts"])
        state["gate"] = {k: v for k, v in gate.items() if k not in ("history", "final_texts")}
        run.flush("gate")
    state["gate_status"] = gate_status
    save()
    # ---- 6. 最終本文の出典対応(記録のみ。ここで再生成はしない) ----
    final_maps = {}
    try:
        for s in SLOTS:        # 直列(予算の歯止めを1call毎に効かせる)。予算到達なら残りは記録して省略(R0本文は確定済み)
            final_maps[s] = map_voice(ctx, run, s, final[s], "final")
    except pl.PipelineStop as e:
        state["final_map_skipped"] = {"code": e.code, "done": sorted(final_maps)}
    run.flush("final_map")
    state["final_texts"] = final
    state["final_maps"] = {s: {k: v for k, v in final_maps[s].items() if k != "meta"} for s in final_maps}
    state["final_cost_jpy"] = cost_jpy(rd)
    article = f"# {wf['title_ja']}\n\n{INTRO_JA}\n\n" + "\n\n".join(f"## {SLOT_HEADING[s]}\n\n{final[s]}" for s in SLOTS) + "\n"
    w1.wt(os.path.join(rd, "article_ja.md"), article)
    w1.wj(os.path.join(rd, "voices_final.json"), final)
    save()
    return state


def write_partial(rd: str):
    """STOP時: state.jsonにある到達時点のVoice本文からarticle_ja_partial.mdを残す(到達時点の成果。確定稿ではない)。"""
    try:
        st = json.load(open(os.path.join(rd, "state.json"), encoding="utf-8"))
        texts = st.get("final_texts") or {s: v["text"] for s, v in st["stages"]["gen"].items()}
        for s, r in (st.get("unmapped_regen") or {}).items():
            texts[s] = r["after"]
        reg = (st.get("structure") or {}).get("regen")
        if reg:
            texts[reg["slot"]] = reg["after"]
        nl = chr(10)
        art = "# (途中停止時点の本文。確定稿ではない)" + nl + nl + (nl + nl).join(f"## {SLOT_HEADING[s]}" + nl + nl + texts[s] for s in SLOTS if s in texts) + nl
        w1.wt(os.path.join(rd, "article_ja_partial.md"), art)
    except Exception:  # noqa: BLE001
        pass


def main() -> int:
    rd = RUN_DIR
    if os.path.exists(os.path.join(rd, "entry_point.json")):
        print(f"[OB] already launched: {rd}/entry_point.json exists (再起動不可)", flush=True)
        return 5
    os.makedirs(rd, exist_ok=True)
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    cl.install(os.path.join(rd, "raw_usage_log.jsonl"))
    w1.wj(os.path.join(rd, "entry_point.json"), {"runner": "er110_family_y_opinion_based_01.py", "management_id": MANAGEMENT_ID, "run_dir": rd, "started": pl.now_iso(),
                                                 "writer_model": MODEL_TOP, "judge_model": MODEL_CHEAP, "budget_stop_jpy": BUDGET_STOP_JPY, "flags": "なし(環境変数・CLI引数なし)"})
    try:
        client = vfl01.get_client()
        st = run_pipeline(client, rd)
        w1.wj(os.path.join(rd, "run_status.json"), {"status": "DONE", "gate_status": st.get("gate_status"), "final_cost_jpy": st.get("final_cost_jpy")})
        print("[OB] DONE", flush=True)
        return 0
    except (pl.PipelineStop, y0.YStop) as e:
        code = getattr(e, "code", type(e).__name__)
        write_partial(rd)
        w1.wj(os.path.join(rd, "run_status.json"), {"status": "STOP", "code": code, "message": str(e)})
        print(f"[OB] STOP {code}: {e}", flush=True)
        return 4
    except Exception as e:  # noqa: BLE001
        w1.wj(os.path.join(rd, "run_status.json"), {"status": "ERROR", "error": repr(e), "trace": traceback.format_exc()})
        print(f"[OB] ERROR {e!r}", flush=True)
        return 4


if __name__ == "__main__":
    sys.exit(main())
