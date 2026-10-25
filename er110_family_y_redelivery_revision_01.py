# -*- coding: utf-8 -*-
"""er110_family_y_redelivery_revision_01.py
FAMILY-Y-VOICES-DESIGN-01 委任_28: 『宅配の再配達は有料にすべきか?』構成・原稿改善Trial(DEV/Trial専用)。

位置づけ(重要):
  - **Family YのDEV/Trial経路**。Production runner・.env・起動scriptから参照されない(testでGrep固定)。import時にAPI呼出0・ファイル副作用0。
    環境変数・flagでProduction挙動が変わる経路はない。既存の `er110_family_y_redelivery_audio_01.py`(委任_27=従来挙動)は**無変更**で、
    本moduleは明示的にサブコマンドを指定したときだけ新工程を実行する(Trial比較のため従来版との併存)。
  - 改善は手動修正ではなく生成方式(Prompt/工程)として実装する:
      ① 人物紹介ナレーション(新stage `intro`: 3本を1 callで生成、Voice本文を読み取り専用で渡し、先取り禁止を決定論で検査)
      ② AI編集アナウンス廃止 + Leadの生成工程での作り直し(新stage `lead`: テーマ範囲データ内の情報・問題提起)
      ③ In One Line除外(本moduleの原稿・音声計画に `in_one_line` を持たない。他Familyの生成・組立コードは無変更)
      ④ Tension+Closing抜本改善(新stage `closing`: 切り口パラメータ[ANGLES]を与えたPromptで案ごとに1 call。生成物は手書き禁止)
  - Voice 1〜3本文(委任_25 R0)は無変更で、byte一致を検査する。
  - **有料runは `REV/BUDGET_APPROVED.json` と明示 `--paid` が無い限り起動しない**。
"""
from __future__ import annotations

import argparse
import contextlib
import glob
import hashlib
import json
import os
import re

import er053_family_x_factlock_ja_writer_01 as w1
import er110_family_y_persona_text_trial_01 as p
import er110_family_y_redelivery_audio_01 as rr
import er110_family_y_text_trial_01 as y0

MANAGEMENT_ID = "FAMILY-Y-VOICES-DESIGN-01"
THEME_TAG = "FAMILY_Y_REDELIVERY_REVISION_01"
REV = f"{rr.ROOT}/revision_01"
APPROVAL_FILE = f"{REV}/BUDGET_APPROVED.json"
THEME_DATA = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/THEME_DATA_02.json"
OLD_ARTICLE = f"{rr.RD}/y_writer/gate_r0/article_final.md"       # 委任_27の日本語原稿(比較用・読取りのみ)
CAP_JPY = 40.0                                                   # 委任_28の個別上限
PAGE_NOTICE_JA = "本コンテンツのVoiceは、実在する人々の意見を参考に、AIが編集・構成したものであり、特定の実在人物の発言を再現したものではありません。"
SLOTS = rr.SLOTS

# ============================================================
# 文量目標(委任_27実測: リード142[本体88+開示54]/V1 260/V2 260/V3 273/Closing 202、計1137字)
# ============================================================
LEAD_RANGE = (115, 160)
INTRO_RANGE = (32, 62)
CLOSING_RANGE = (175, 245)
MAX_SENT = 55            # 聞き取りやすさの上限(Promptでは45字以内を要求、検査は余裕を持たせた上限)

# ============================================================
# 共通の検査語
# ============================================================
AI_ANNOUNCE_RE = re.compile(r"(実在|公開されている|公開された|ネットなど|組み立てた|組み立て|AI|人工知能|複数の意見をもと|特定の人の話)")
IOL_RE = re.compile(r"(In one line|IN ONE LINE|ひとこと)", re.I)
CLAIM_WORDS_RE = re.compile(r"(有料|賛成|反対|請求|払う|払っ|払わ|料金|負担すべき|べきだ)")      # 人物紹介が本人の主張・結論を先取りしない
OBVIOUS_RE = re.compile(r"(立場(や暮らし)?(に)?(よって|ごとに|が違|で違)|人それぞれ|答えが(分か|違|割れ)|考え(方)?が(違|異な|分か)|大事にしたい(もの|こと)は(違|異な))")
DIGIT_RE = re.compile(r"[0-9０-９]")
INTRO_ROLE_RE = {
    "voice_1": re.compile(r"(ドライバー|配達|配って|荷物を運)"),
    "voice_2": re.compile(r"(共働き|仕事|家を空け|留守)"),
    "voice_3": re.compile(r"(ロッカー|営業所|宅配ボックス|受け取り方|受け取る)"),
}
INTRO_OBJECT_WORDS = ("宅配ボックス", "置き配", "ロッカー", "営業所", "時間指定", "指定", "不在票", "送料", "コンビニ")   # 紹介文が使う具体物は、その人物自身の語りに出てくるものだけ
PREVIEW_RE = re.compile(r"(三人|三つの声|3人)")

# ============================================================
# テーマ範囲(データ。THEME_DEFINITION_02 §1〜2・世界観 distinctions の転記。新しい事実を足さない。数字・企業名なし)
# ============================================================
SCOPE_LINES = (
    "再配達とは、受取人の不在などで荷物を渡せず、配達員があらためて届けに行くこと。",
    "有料化とは、再配達に、通常の配送料とは別に、受取人が料金を払う仕組みにすること。",
    "有料化の考え方には幅がある: すべての再配達から取る/くり返し不在の場合だけ取る/料金は取らず別の手段で減らす(運賃全体や割引の見直し、受け取り手段の整備)。",
    "関係する話題: 時間帯指定、置き配、宅配ボックス、営業所やロッカーでの受け取り。",
    "争点になりやすいこと: 不在は誰の都合で起きるのか/料金を取ると行動が変わるのか/誰が負担する設計にするのか。",
)

# ============================================================
# Closing 切り口(委任_28 §2。Sonnet考案: 3人の本文・テーマ本質の分析から導いた。分析と却下案は EVAL_01.md)
# 切り口の指示文(brief)は **Promptの入力**であり、Closing本文はこのPromptから生成する(手書き禁止)。
# ============================================================
ANGLES = {
    "A": {
        "name": "「不在」という言葉の向こう側",
        "aim": "同じ「不在」という言葉が3人には別々の重さで響いている(ドライバーには不在票を入れる瞬間、共働きの受取人には指定したのに不在側にされる言葉、受け取り方を工夫する人には手間をかけて避けるもの)。「不在」の一言が、届く時間が合わなかった分まで受け取る側の落ち度に聞こえさせていないか、料金が付くのは不在か、届け方と受け取り方のずれか、と問う。",
        "brief": ("『不在』という同じ言葉が、3人には別々の重さで響いていることに注目する切り口。"
                  "ドライバーにとって不在は、不在票を入れて次の家へ向かう瞬間。共働きの受取人にとっては、時間を指定したのに、いつの間にかそちら側にされてしまう言葉。"
                  "営業所やロッカーで受け取る人にとっては、手間をかけて出さないようにしているもの。同じ『不在』でも、誰の側から呼ぶかで、落ち度に聞こえる人と聞こえない人がいる。"
                  "『不在』の一言が、届く時間が合わなかった分まで、受け取る側のせいに聞こえさせていないか、という新しい見方を示し、"
                  "『料金が付くのは、不在に対してか、届け方と受け取り方のずれに対してか』『あなたに不在票が入っていた日は、本当にあなたの不在だったのか』のような、聞き手が自分の経験から考えられる問いにして渡す。"),
        "revision_note": "v1(初回)は3人の『手間の数え始め』を論じ、切り口名の『不在という言葉』からそれた上、既存Leakage項目leak_tension_reverts_to_researchがv1生成物(言葉の見直し)をFAILし、局所書き換えで切り口が失われた。v2は『不在』が3人にとって持つ意味の違いという形で、切り口と『3人がなぜ違う答えに至るか』の掘り下げを両立させたPrompt(brief)に改訂。",
    },
    "B": {
        "name": "料金は、誰の何を動かせるのか",
        "aim": "有料化という手段が3人の困りごとのうち何を動かせて何を動かせないかを仕分ける。料金が届くのは受け取る側の工夫(営業所・ロッカー・くり返しの不在)であり、時間指定が守られないことや料金の組み方は、受取人が払っても動かない。「取るか取らないか」の前に「その料金は誰に届く合図か」を問う。",
        "brief": ("有料化という『手段』が、3人の困りごとのうち何を動かせて何を動かせないかを仕分ける切り口。"
                  "『最初は無料で、くり返す人から』のように料金が行動を変える合図になるのは、受け取る側の工夫(営業所やロッカーで受け取る、くり返し不在にしない)。"
                  "一方、時間指定が守られない、届く日時が分からない、料金の組み方や送料の側にある話は、受け取る人が払っても動かない。"
                  "『料金は誰の行動に届く合図なのか』という新しい見方を示し、『有料にする前に、その料金で変わるのは誰の何か』『あなたが今困っていることは、料金で動くことか』のような考えるポイントを問いにして渡す。"),
    },
    "C": {
        "name": "誰も相手を悪者にしていない三人",
        "aim": "3人は自分の立場を語りながら、全員が相手側の事情に一歩寄っている(ドライバーは客を責めない、受取人は配達員の大変さが分かる、営業所で受け取る人は自分が恵まれた側かもしれないと言う)。争点は「誰が悪いか」ではなく、「どこまで歩み寄り、どこから先は譲れないか」の線の位置だと示す。",
        "brief": ("3人の語りに共通して現れている『相手への歩み寄り』に注目する切り口。"
                  "ドライバーは、きついと言いながらお客さんに請求する話にはしたくないと言う。受取人は、配達員さんの大変さは分かると言いながら、自分が払うのは納得できないと言う。"
                  "受け取り方を工夫する人は、有料でいいと言いながら、自分は選べる恵まれた側かもしれないと言う。誰も相手を悪者にしていない。"
                  "だから争点は『誰が悪いか』ではなく、『相手の事情をどこまで受け止め、どこから先は譲れないか』という線の位置にある、という新しい見方を示し、"
                  "『あなたなら、配達する人の事情に、どこまで寄り添えるか。どこから先は、受け入れられないか』のような、聞き手が自分の線を探す問いで締める。"),
    },
}

# ============================================================
# Closing 新規則(従来 p.TENSION_RULES との差分は DESIGN_01 §2。従来版は無変更で、本moduleの生成中だけprocess内で差替える)
# ============================================================
CLOSING_DEVELOPER = ("あなたは日本語のラジオ読み物の語り手(ナレーター)です。3人の語りを聞き終えた聞き手に向けて、"
                     "3人の語りを聞いたあとだからこそ見える新しい見方を、耳で聞いて一度で分かる具体的な言葉で示し、聞き手が自分で考えたくなる問いで終わります。")
CLOSING_RULES = """- 語り手(ナレーター)の声。一人称(私・俺・僕・わたし)は使わない。話し言葉の常体。
- 骨格(地の文のひと続きで。「第1に」などのラベルは書かない): (1)3人の語りのどれかを、3人の本文に出てきた具体物の言葉で1文だけ受ける(省いてもよい。3人の意見を順に要約し直さない) → (2)【切り口】に沿って、3人の語りの中には直接は出てこない新しい見方・発見・論点を2〜3文で示す → (3)切り口から導かれた、聞き手が自分の暮らしや経験から考えられる具体的な問いで締める。
- 「立場や暮らしによって考えが違う」「答えが分かれる」「人それぞれ」のような、当然の結論で終わらせない。3人を単純な2対1の陣営に分けない。
- 締めの問いの文末は「？」。「あなたはどう思う?」のような形式的な問いは書かない。結論・正解・解決策・勝者の決定はしない。
- 3人の語りの事実・主張と矛盾しない。3人の本文にない出来事・数字・制度・企業名を事実として足さない。仮定は「もし〜なら」の問いの形でだけ使う。「取材した」「話を聞いた」など実在の取材者がいるような言い方をしない。
- 1文は45字以内。1文に抽象名詞(責任・価値・判断・根拠・余地・視点・基準・立場・意味など)は2つまで。二重否定を使わない。哲学的な一般化をしない。
- 括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字を使わない。"""


def read_cap(path: str = None) -> dict:
    return rr.read_cap(path or APPROVAL_FILE)


def require_paid(paid_flag: bool, approval_path: str = None) -> dict:
    if not paid_flag:
        raise RuntimeError("[NO_PAID_FLAG] --paid が無いため有料runを起動しません")
    return read_cap(approval_path)


def total_cost_jpy(rev_dir: str = None) -> float:
    import er053_cost_aggregate_01 as ca
    rev_dir = rev_dir or REV
    return round(sum(ca.compute_stage_cost_breakdown_multi(f)["total_jpy"] for f in glob.glob(f"{rev_dir}/**/raw_usage_log*.jsonl", recursive=True)), 3)


def guard(note: str, cap: float):
    c = total_cost_jpy()
    if c > cap:
        raise RuntimeError(f"[BUDGET_GUARD] cost so far {c} JPY > cap {cap} JPY ({note})")
    print(f"[Y-REVISION] cost so far {c} JPY ({note})")


# ============================================================
# 入力(読取りのみ)
# ============================================================
def load_theme_sheets() -> dict:
    d = json.load(open(THEME_DATA, encoding="utf-8"))
    return d["sheets"]


def load_old_ja() -> dict:
    ps = y0.parse_article(open(OLD_ARTICLE, encoding="utf-8").read())["paragraphs"]
    return {"lead_with_disclosure": ps[0], "voice_1": ps[1], "voice_2": ps[2], "voice_3": ps[3], "closing": ps[4]}


# ============================================================
# ② Lead(新stage)
# ============================================================
LEAD_TMPL = """次のテーマで、読み物の最初の1段落(リード)だけを書いてください。

【テーマ】@@PREMISE@@

【テーマの範囲(リードで使ってよい事柄はこの中だけ。これ以外の事実・出来事・数字・企業名は足さない)】
@@SCOPE@@

【リードの役割】
このあと、立場も暮らしも違う3人が、それぞれの暮らしから意見を語ります。聞き手が「これは自分にも関係がある」「どう決めるのがよいのだろう」と思い、3人の声を聞きたくなるように、テーマへの興味を引く情報と問題提起を自然に置いてください。

【書き方】
- 構成(地の文のひと続き。ラベルは書かない): (1)誰もが思い当たる、具体的な場面か問いから入る(新しい出来事を作らない) → (2)この話題の面白さや難しさが分かる情報を、テーマの範囲から1〜2つ入れる → (3)問題提起を1つ → (4)最後に「ここに、立場も暮らしも違う三人の声を並べる」という趣旨の予告。
- 語り手(ナレーター)の声。一人称(私・俺・僕・わたし)は使わない。話し言葉の常体(「〜だ」「〜だよね」など)。「です・ます」調にしない。
- 約125〜150字、1段落、3〜4文。1文は45字以内。
- 3人の立場・結論・職業の詳細は先に言わない。賛成か反対かの結論を先取りしない。数字は使わない。
- 「実在の人の話ではない」「ネットの意見をもとにした」「AIが組み立てた」のような、声の作り方についての説明は書かない。
- 「取材した」「話を聞いた」など実在の取材者がいるような言い方をしない。
- 括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字を使わない。

出力はリードの本文のみ(見出し・ラベルなし)。"""


def build_lead_prompt() -> str:
    return LEAD_TMPL.replace("@@PREMISE@@", rr.PREMISE_JA).replace("@@SCOPE@@", "\n".join(f"- {x}" for x in SCOPE_LINES))


def check_lead(text: str) -> dict:
    v = []
    t = (text or "").strip()
    if not t:
        v.append("EMPTY")
    if "\n" in t:
        v.append("MULTI_PARAGRAPH")
    if y0.FIRST_PERSON_RE.search(t):
        v.append("HAS_FIRST_PERSON")
    if y0.LEAD_BAD_RE.search(t):
        v.append("HAS_INTERVIEWER_EXPRESSION")
    if y0.LABEL_START_RE.match(t):
        v.append("LABEL_AT_START")
    if DIGIT_RE.search(t):
        v.append("HAS_DIGIT")
    if y0.DESU_MASU_RE.search(t):
        v.append("DESU_MASU")
    if AI_ANNOUNCE_RE.search(t):
        v.append("HAS_AI_EDIT_ANNOUNCEMENT")
    if not PREVIEW_RE.search(t):
        v.append("NO_PREVIEW_OF_THREE_VOICES")
    if not (LEAD_RANGE[0] <= len(t) <= LEAD_RANGE[1]):
        v.append(f"LENGTH={len(t)}")
    if any(len(s) > MAX_SENT for s in y0.SENT_SPLIT_RE.split(t) if s.strip()):
        v.append("SENTENCE_TOO_LONG")
    return {"ok": not v, "violations": v}


# ============================================================
# ① 人物紹介(新stage。3本を1 callで)
# ============================================================
INTRO_DEVELOPER = "あなたは日本語のラジオ読み物の語り手(ナレーター)です。これから語る人物を、聞き手に短く自然に紹介します。"
INTRO_SCHEMA = {"name": "family_y_voice_intros", "strict": True,
                "schema": {"type": "object", "additionalProperties": False, "required": list(SLOTS),
                           "properties": {s: {"type": "string"} for s in SLOTS}}}
INTRO_TMPL = """3人の人物がそれぞれ語る前に、語り手(ナレーター)が1人ずつ短く紹介する文を書いてください。紹介のあと、すぐ本人の語りに切り替わります。

【3人に共通の話題】@@PREMISE@@

@@PERSONS@@

【書き方】
- 紹介の目的: 聞き手が「これから、誰が、どんな立場で話すのか」を分かったうえで本人の語りを聞けるようにすること。人物の特徴・背景・立場を、聞いて一度で分かる言葉で伝える。
- 語り手(ナレーター)の声。一人称(私・俺・僕・わたし)は使わない。話し言葉の常体(「です・ます」調にしない)。1人につき1〜2文、約35〜55字。
- 本人の主張・結論・賛否は先取りしない。「有料」「料金」「賛成」「反対」「払う」「請求」の語は紹介文に使わない。本人の語りに出てくる具体的な出来事や言い回しを、紹介文で使い切らない(本人の語りの文をそのまま写さない)。
- 紹介文に出す具体物(宅配ボックス・置き配・ロッカー・営業所・時間指定・不在票など)は、その人物自身の【本人の語り】に出てくるものだけにする(他の人物の語りにしか出てこない物は使わない)。
- 人物の情報は上の【人物】にあることだけ。年齢・名前・家族構成・勤務先など、新しい事実は足さない。
- 順番が分かる言い方で始める(1人目は「最初に話すのは」、2人目は「次は」、3人目は「最後は」など、自然な言い方でよい)。
- 「実在の人の話ではない」「ネットの意見をもとにした」「AIが組み立てた」のような、声の作り方についての説明は書かない。「話を聞いた」「取材した」と言わない。数字は使わない。
- 括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字を使わない。

出力はJSON: voice_1, voice_2, voice_3 の3つの文字列(それぞれ紹介文のみ。見出し・ラベルなし)。"""


def person_block(slot: str, sheets_theme: dict, voices: dict) -> str:
    i = SLOTS.index(slot) + 1
    sh = sheets_theme[slot]
    daily = re.sub(r"(\(出来事は経験欄にあるものだけ\)|（出来事は経験欄にあるものだけ）)", "", sh["daily_life_ja"]).strip()
    cue = re.sub(r"\(.*?\)", "", sh["identity_cue_ja"]).strip()
    return (f"【人物{i}】{sh['role_ja']}\n  暮らしの様子: {daily}\n  人物の出し方の目安: {cue}\n"
            f"  本人の語り(整合を取るための読み取り専用。内容を先取りしない): {voices[slot]}")


def build_intro_prompt(sheets_theme: dict, voices: dict) -> str:
    persons = "\n\n".join(person_block(s, sheets_theme, voices) for s in SLOTS)
    return INTRO_TMPL.replace("@@PREMISE@@", rr.PREMISE_JA).replace("@@PERSONS@@", persons)


def _shingles(s: str, n: int) -> set:
    t = rr._norm_ja(s)
    return {t[i:i + n] for i in range(len(t) - n + 1)}


def check_intro(text: str, slot: str, voice_body: str) -> dict:
    v = []
    t = (text or "").strip()
    if not t:
        return {"ok": False, "violations": ["EMPTY"]}
    if "\n" in t:
        v.append("MULTI_LINE")
    if y0.FIRST_PERSON_RE.search(t):
        v.append("HAS_FIRST_PERSON")
    if y0.LEAD_BAD_RE.search(t):
        v.append("HAS_INTERVIEWER_EXPRESSION")
    if y0.LABEL_START_RE.match(t):
        v.append("LABEL_AT_START")
    if DIGIT_RE.search(t):
        v.append("HAS_DIGIT")
    if y0.DESU_MASU_RE.search(t):
        v.append("DESU_MASU")
    if AI_ANNOUNCE_RE.search(t):
        v.append("HAS_AI_EDIT_ANNOUNCEMENT")
    if CLAIM_WORDS_RE.search(t):
        v.append("FORESHADOWS_CLAIM_WORD")
    if not INTRO_ROLE_RE[slot].search(t):
        v.append("ROLE_NOT_CONVEYED")
    for w in INTRO_OBJECT_WORDS:
        if w in t and w not in voice_body:
            v.append(f"INTRO_OBJECT_NOT_IN_OWN_VOICE:{w}")
    if _shingles(t, 10) & _shingles(voice_body, 10):
        v.append("COPIES_VOICE_BODY_10CHARS")
    if not (INTRO_RANGE[0] <= len(t) <= INTRO_RANGE[1]):
        v.append(f"LENGTH={len(t)}")
    return {"ok": not v, "violations": v}


# ============================================================
# ④ Closing(新stage。切り口ごとに1 call)
# ============================================================
def build_closing_prompt(voices: dict, angle_id: str) -> str:
    a = ANGLES[angle_id]
    sheets = rr.SHEETS_R
    vs = "\n\n".join(f"【人物{i + 1}の語り({sheets[s]['label']})】\n{voices[s]}" for i, s in enumerate(SLOTS))
    objs = "\n".join(f"- 人物{i + 1}: {sheets[s]['tension_object']}" for i, s in enumerate(SLOTS))
    claims = "\n".join(f"- 人物{i + 1}: {sheets[s]['claim']}" for i, s in enumerate(SLOTS))
    return (f"3人の人物が、次の同じ案について、それぞれの暮らしから意見を語り終えました。語り手として、最後の1パート(Tension+Closing)を書いてください。\n\n"
            f"【3人に共通の前提】{rr.PREMISE_JA}\n\n{vs}\n\n【3人の主張の要点(参考。要約し直さない)】\n{claims}\n"
            f"【対比に使える具体物(3人の本文に出てきたものを優先して使う)】\n{objs}\n\n"
            f"【この回の切り口(必ずこの切り口で書く)】\n切り口の名前: {a['name']}\n{a['brief']}\n\n"
            f"【書き方】\n{CLOSING_RULES}\n- 長さ: 約190〜230字、1段落。\n\n出力は最終パートの本文のみ(見出し・ラベルなし)。")


def check_closing(text: str) -> dict:
    v = []
    t = (text or "").strip()
    if not t:
        return {"ok": False, "violations": ["EMPTY"]}
    if "\n" in t:
        v.append("MULTI_PARAGRAPH")
    if y0.FIRST_PERSON_RE.search(t):
        v.append("HAS_FIRST_PERSON")
    if y0.LABEL_START_RE.match(t):
        v.append("LABEL_AT_START")
    if y0.LEAD_BAD_RE.search(t):
        v.append("HAS_INTERVIEWER_EXPRESSION")
    if DIGIT_RE.search(t):
        v.append("HAS_DIGIT")
    if y0.DESU_MASU_RE.search(t):
        v.append("DESU_MASU")
    if AI_ANNOUNCE_RE.search(t):
        v.append("HAS_AI_EDIT_ANNOUNCEMENT")
    if OBVIOUS_RE.search(t):
        v.append("OBVIOUS_CONCLUSION_PHRASE")
    if not re.search(r"[？?]\s*$", t):
        v.append("NOT_ENDING_WITH_QUESTION")
    if not (CLOSING_RANGE[0] <= len(t) <= CLOSING_RANGE[1]):
        v.append(f"LENGTH={len(t)}")
    if any(len(s) > MAX_SENT for s in y0.SENT_SPLIT_RE.split(t) if s.strip()):
        v.append("SENTENCE_TOO_LONG")
    return {"ok": not v, "violations": v}


# ============================================================
# 生成(有料)
# ============================================================
def _chat_text(client, *, prompt: str, developer: str, stage: str, effort: str, model: str) -> str:
    resp = y0.chat(client, model=model, effort=effort, user=prompt, developer=developer, stage=stage)
    return resp, resp.output_text.strip()


def _gen_single(client, *, out_dir: str, name: str, prompt: str, developer: str, stage: str, checker, effort: str = "high", model: str = None) -> dict:
    """1 call(+契約違反時のみ再生成1回。既存generate_lead/generate_tensionと同方式)。"""
    import er003_audio_tts_asr_safety as safety
    model = model or y0.MODEL_TOP
    os.makedirs(out_dir, exist_ok=True)
    w1.wt(os.path.join(out_dir, f"{name}_prompt.txt"), prompt)
    calls, hist, cur = [], [], prompt
    for k in (1, 2):
        resp, raw = _chat_text(client, prompt=cur, developer=developer, stage=stage + ("" if k == 1 else "_regen"), effort=effort, model=model)
        calls.append({**y0.resp_meta(resp), "prompt_sha256": w1.sha_text(cur)})
        w1.wt(os.path.join(out_dir, f"{name}_raw_try{k}.txt"), raw)
        probs = []
        try:
            final, sym = p._fin(raw)
            probs += checker(final)["violations"]
            if safety.symbol_gate_requires_stop(sym):
                probs.append(f"SYMBOL:{sym}")
        except w1.TagLeak as e:
            final, probs = "", [f"TAG_LEAK:{e}"]
        hist.append(probs)
        if not probs:
            w1.wt(os.path.join(out_dir, f"{name}.txt"), final + "\n")
            w1.wj(os.path.join(out_dir, f"{name}_meta.json"), {"calls": calls, "problems_per_try": hist, "sha256": w1.sha_text(final), "chars": len(final)})
            return {"text": final}
        if k == 1:
            cur = prompt + "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {x}" for x in probs)
    raise y0.YStop(f"{name.upper()}_CONTRACT_STOP", f"{name}: 再生成後も契約違反 {hist[-1]}", hist)


def generate_lead(client, out_dir: str) -> dict:
    return _gen_single(client, out_dir=out_dir, name="lead", prompt=build_lead_prompt(), developer=rr.LEAD_DEVELOPER, stage="yrv_lead", checker=check_lead)


def generate_intros(client, voices: dict, out_dir: str, effort: str = "high") -> dict:
    import er003_audio_tts_asr_safety as safety
    os.makedirs(out_dir, exist_ok=True)
    prompt = build_intro_prompt(load_theme_sheets(), voices)
    w1.wt(os.path.join(out_dir, "intro_prompt.txt"), prompt)
    calls, hist, cur = [], [], prompt
    for k in (1, 2):
        resp = y0.chat(client, model=y0.MODEL_TOP, effort=effort, user=cur, developer=INTRO_DEVELOPER, schema=INTRO_SCHEMA, stage="yrv_intro" + ("" if k == 1 else "_regen"))
        raw = json.loads(resp.output_text)
        calls.append({**y0.resp_meta(resp), "prompt_sha256": w1.sha_text(cur)})
        w1.wj(os.path.join(out_dir, f"intro_raw_try{k}.json"), raw)
        probs, finals = [], {}
        for s in SLOTS:
            try:
                f, sym = p._fin(raw.get(s, ""))
                finals[s] = f
                probs += [f"{s}:{x}" for x in check_intro(f, s, voices[s])["violations"]]
                if safety.symbol_gate_requires_stop(sym):
                    probs.append(f"{s}:SYMBOL:{sym}")
            except w1.TagLeak as e:
                finals[s] = ""
                probs.append(f"{s}:TAG_LEAK:{e}")
        hist.append(probs)
        if not probs:
            w1.wj(os.path.join(out_dir, "intros.json"), finals)
            w1.wj(os.path.join(out_dir, "intro_meta.json"), {"calls": calls, "problems_per_try": hist, "chars": {s: len(finals[s]) for s in SLOTS}})
            return {"intros": finals}
        if k == 1:
            cur = prompt + "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {x}" for x in probs)
    raise y0.YStop("INTRO_CONTRACT_STOP", f"intro: 再生成後も契約違反 {hist[-1]}", hist)


_CURRENT_ANGLE = {"id": None}


def _rewrite_prompt_with_angle(orig):
    def f(voices, tension, flagged):
        base = orig(voices, tension, flagged)
        aid = _CURRENT_ANGLE["id"]
        if not aid:
            return base
        a = ANGLES[aid]
        return base + "\n\n【この最終パートの切り口(書き換え後も必ず保つ。切り口を別の内容にすり替えない)】\n切り口の名前: " + a["name"] + "\n" + a["brief"]
    return f


@contextlib.contextmanager
def patched_closing_module():
    """Closing局所書き換えPrompt(p.build_tension_rewrite_prompt)が読む共通前提・規則を、process内だけ今回の新規則へ差替える(finallyで復元)。"""
    prev = (p.COMMON_PREMISE_JA, p.TENSION_RULES, y0.THEME_TAG, p.build_tension_rewrite_prompt)
    p.COMMON_PREMISE_JA = rr.PREMISE_JA
    p.TENSION_RULES = CLOSING_RULES
    y0.THEME_TAG = THEME_TAG
    p.build_tension_rewrite_prompt = _rewrite_prompt_with_angle(prev[3])
    try:
        yield
    finally:
        p.COMMON_PREMISE_JA, p.TENSION_RULES, y0.THEME_TAG, p.build_tension_rewrite_prompt = prev
        _CURRENT_ANGLE["id"] = None


def generate_closing(client, voices: dict, angle_id: str, out_dir: str) -> dict:
    """生成 → 決定論検査 → Leakage Gate(既存run_gate: 判定→局所書き換え→再判定) → Gate後の再検査。"""
    _CURRENT_ANGLE["id"] = angle_id
    g = _gen_single(client, out_dir=out_dir, name="closing", prompt=build_closing_prompt(voices, angle_id), developer=CLOSING_DEVELOPER,
                    stage=f"yrv_closing_{angle_id}", checker=check_closing)
    gt = os.path.join(out_dir, "gate")
    if not os.path.exists(os.path.join(gt, "gate_result.json")):
        r = p.run_gate(client, kind="tension", stage=f"yrv_closing_{angle_id}_gate", texts={"tension": g["text"]}, out_dir=gt, voices_ctx=voices,
                       judge_model=y0.MODEL_CHEAP, judge_effort="high")
        print(f"[Y-REVISION] closing {angle_id} gate status={r['status']} judgements={r['n_judgements']}")
    final = p.load_gated_or_stop(gt)["tension"]
    post = check_closing(final)
    w1.wj(os.path.join(out_dir, "post_gate_check.json"), post)
    if not post["ok"]:
        raise y0.YStop("CLOSING_POST_GATE_STOP", f"closing {angle_id}: Gate後の検査違反 {post['violations']}")
    w1.wt(os.path.join(out_dir, "closing_final.txt"), final + "\n")
    return {"text": final}


# Lead/人物紹介は「最終パート」ではないため、Tension専用2項目は適用外(補助適用であり、承認済みGateの定義は変更しない)
LEADINTRO_NA_FIELDS = ("leak_tension_reverts_to_research", "leak_binary_camp_split")


def leadintro_gate_result(path: str = None) -> dict:
    d = json.load(open(path or f"{REV}/gate_lead_intro/leak_check.json", encoding="utf-8"))
    app, na = [], []
    for it in d["flagged_items"]:
        ap = [x for x in it["fail_fields"] if x not in LEADINTRO_NA_FIELDS]
        nn = [x for x in it["fail_fields"] if x in LEADINTRO_NA_FIELDS]
        if ap:
            app.append({**it, "fail_fields": ap})
        if nn:
            na.append({**it, "fail_fields": nn})
    return {"applicable_flagged": app, "not_applicable_flagged": na, "note": "Tension専用2項目[leak_tension_reverts_to_research/leak_binary_camp_split]はLead・人物紹介に適用外(最終パートの判定項目)"}


def cmd_gen(a):
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    cap = min(require_paid(a.paid)["cap_jpy"], CAP_JPY)
    os.makedirs(REV, exist_ok=True)
    cl.install(f"{REV}/raw_usage_log.jsonl")
    client = vfl01.get_client()
    r0 = rr.load_r0()
    voices = {s: r0[s] for s in SLOTS}
    w1.wj(f"{REV}/entry_point.json", {"runner": "er110_family_y_redelivery_revision_01.py", "management_id": MANAGEMENT_ID, "src_r0": rr.SRC_R0,
                                       "production_reachable": False, "writer_model": y0.MODEL_TOP, "judge_model": y0.MODEL_CHEAP,
                                       "cap_jpy": cap, "stages": a.stages, "module_sha256": hashlib.sha256(open("er110_family_y_redelivery_revision_01.py", "rb").read()).hexdigest()})
    stages = [x.strip() for x in a.stages.split(",") if x.strip()]
    prev_tag = y0.THEME_TAG
    y0.THEME_TAG = THEME_TAG
    try:
        if "lead" in stages and not os.path.exists(f"{REV}/lead/lead.txt"):
            generate_lead(client, f"{REV}/lead")
            guard("after lead", cap)
        if "intro" in stages and not os.path.exists(f"{REV}/intro/intros.json"):
            generate_intros(client, voices, f"{REV}/intro")
            guard("after intro", cap)
        if "leadintro_gate" in stages:
            if not os.path.exists(f"{REV}/gate_lead_intro/leak_check.json"):
                lead = w1.rdt(f"{REV}/lead/lead.txt").strip()
                intros = json.load(open(f"{REV}/intro/intros.json", encoding="utf-8"))
                comb = chr(10).join([lead] + [intros[s] for s in SLOTS])
                chk = p.run_leak(client, "tension", {"tension": comb}, model=y0.MODEL_CHEAP, effort="high", stage="yrv_leadintro_leak")
                os.makedirs(f"{REV}/gate_lead_intro", exist_ok=True)
                w1.wj(f"{REV}/gate_lead_intro/leak_check.json", {**chk, "note": "既存Tension項目セットをLead+人物紹介(ナレーター文)へ補助適用。Leadには従来Leakage項目なし", "text_sha256": w1.sha_text(comb)})
                guard("after leadintro gate", cap)
            res = leadintro_gate_result()
            w1.wj(f"{REV}/gate_lead_intro/applicable_result.json", res)
            if res["applicable_flagged"]:
                raise y0.YStop("LEADINTRO_LEAKAGE_FLAGGED", str(res["applicable_flagged"]))
        with patched_closing_module():
            for aid in ANGLES:
                if f"closing_{aid}" in stages and not os.path.exists(f"{REV}/closing_{aid}/closing_final.txt"):
                    guard(f"before closing {aid}", cap)
                    generate_closing(client, voices, aid, f"{REV}/closing_{aid}")
                    guard(f"after closing {aid}", cap)
    finally:
        y0.THEME_TAG = prev_tag
    print("[Y-REVISION] gen完了", stages)


# ============================================================
# 組立・検査(無料)
# ============================================================
def render_revised(title: str, lead: str, intros: dict, voices: dict, closing: str) -> str:
    """タイトル1行 + 5パート(空行区切り)。Voiceパートは『紹介1行 + 改行 + 本人の語り』。In One Line・開示文なし。"""
    parts = [lead.strip()] + [f"{intros[s].strip()}\n{voices[s].strip()}" for s in SLOTS] + [closing.strip()]
    return title.strip() + "\n\n" + "\n\n".join(parts) + "\n"


def parse_revised(text: str) -> dict:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", (text or "").strip()) if b.strip()]
    if len(blocks) != 6:
        raise ValueError(f"5パート+タイトルではありません(blocks={len(blocks)})")
    voices = []
    for b in blocks[2:5]:
        ls = b.split("\n")
        if len(ls) != 2:
            raise ValueError("Voiceパートが『紹介1行+本人の語り1行』ではありません")
        voices.append({"intro": ls[0].strip(), "body": ls[1].strip()})
    return {"title": blocks[0], "lead": blocks[1], "voices": voices, "closing": blocks[5]}


def check_revised(text: str, r0: dict) -> dict:
    """組立後の決定論確認: 5パート/Voice本文byte一致/In One Line無/AI編集アナウンス無/ナレーター文に一人称無/開示文(旧)無。"""
    v = []
    if IOL_RE.search(text):
        v.append("IN_ONE_LINE_PRESENT")
    try:
        d = parse_revised(text)
    except ValueError as e:
        return {"ok": False, "violations": v + [str(e)]}
    for i, s in enumerate(SLOTS):
        if d["voices"][i]["body"] != r0[s].strip():
            v.append(f"VOICE_BODY_CHANGED:{s}")
        if y0.FIRST_PERSON_RE.search(d["voices"][i]["intro"]):
            v.append(f"INTRO_HAS_FIRST_PERSON:{s}")
        if not rr.FIRST_PERSON_JA[s] in d["voices"][i]["body"]:
            v.append(f"VOICE_NO_OWN_FIRST_PERSON:{s}")
    for name, t in (("lead", d["lead"]), ("closing", d["closing"])):
        if y0.FIRST_PERSON_RE.match(t[:4]):
            v.append(f"NARRATOR_STARTS_WITH_FIRST_PERSON:{name}")
    narr = "\n".join([d["lead"], d["closing"]] + [x["intro"] for x in d["voices"]])
    if AI_ANNOUNCE_RE.search(narr):
        v.append("HAS_AI_EDIT_ANNOUNCEMENT")
    if rr.DISCLOSURE_JA in text:
        v.append("OLD_DISCLOSURE_PRESENT")
    return {"ok": not v, "violations": v}


def mapping_check_revised(paras_by_lang: dict) -> dict:
    """5パート対応検査の拡張版(rr.mapping_checkの後継): 各言語で『リード/Voice1(紹介+本人)/Voice2/Voice3/Closing』=5パートかつ、
    Voiceパートは紹介行=ナレーター(一人称なし)・本人行=一人称+話者アンカー。paras_by_lang: {lang: {'lead':str,'voices':[{'intro','body'}]*3,'closing':str}}。"""
    rows, ok = [], True
    for lang, d in paras_by_lang.items():
        r = {"lang": lang, "checks": []}
        if len(d.get("voices", [])) != 3:
            r["checks"].append({"check": "VOICE_PART_COUNT", "ok": False})
            ok = False
            rows.append(r)
            continue
        for i, s in enumerate(SLOTS):
            intro, body = d["voices"][i]["intro"], d["voices"][i]["body"]
            if lang == "ja":
                intro_fp = bool(y0.FIRST_PERSON_RE.search(intro))
                fp = rr.FIRST_PERSON_JA[s] in body
                own = bool(re.search(rr.ANCHORS[s]["ja"], body))
            else:
                intro_fp = bool(re.search(r"\b(I|I'm|I've|my|me|myself)\b", intro))
                fp = bool(re.search(r"\b(I|I'm|I've|my|me|myself)\b", body, re.I))
                own = bool(re.search(rr.ANCHORS[s]["en"], body, re.I))
            good = (not intro_fp) and fp and own
            r["checks"].append({"check": f"voice_part_{i + 1}_{s}", "intro_has_first_person": intro_fp, "body_first_person": fp, "body_own_anchor": own, "ok": good})
            ok = ok and good
        for nm in ("lead", "closing"):
            t = d[nm]
            fp0 = bool(y0.FIRST_PERSON_RE.match(t[:4])) if lang == "ja" else bool(re.match(r"^(I|I'm|I've|My|Me)\b", t))
            r["checks"].append({"check": f"{nm}_narrator", "starts_with_first_person": fp0, "ok": not fp0})
            ok = ok and not fp0
        rows.append(r)
    return {"ok": ok, "rows": rows}


def length_table(old: dict, new: dict) -> list:
    """パート別字数の新旧(人物紹介は各Voiceパートに含める)。old: load_old_ja()、new: parse_revised()の結果。"""
    rows = []
    o = {"Lead": len(old["lead_with_disclosure"]), "Voice 1": len(old["voice_1"]), "Voice 2": len(old["voice_2"]), "Voice 3": len(old["voice_3"]), "Closing": len(old["closing"])}
    n = {"Lead": len(new["lead"]), "Voice 1": len(new["voices"][0]["intro"]) + len(new["voices"][0]["body"]),
         "Voice 2": len(new["voices"][1]["intro"]) + len(new["voices"][1]["body"]), "Voice 3": len(new["voices"][2]["intro"]) + len(new["voices"][2]["body"]),
         "Closing": len(new["closing"])}
    to, tn = sum(o.values()), sum(n.values())
    for k in o:
        rows.append({"part": k, "old": o[k], "old_ratio": round(o[k] / to, 3), "new": n[k], "new_ratio": round(n[k] / tn, 3), "diff": n[k] - o[k]})
    rows.append({"part": "計", "old": to, "old_ratio": 1.0, "new": tn, "new_ratio": 1.0, "diff": tn - to})
    return rows


# ============================================================
# ① 音声計画(設計のみ。今回は音声化しない。In One Line除外・レベル別ナレーター)
# ============================================================
def revised_segment_plan(level: str) -> list:
    """改善版Full Storyの音声segment計画。ナレーター(リード・人物紹介・Closing)のVoiceは **既存のFull Story設定を参照して導出** する(Aoedeを固定記述しない)。
    Voice 1〜3は既存固定割当。In One Line segmentは含まない(Yのみ廃止。X/Z側の生成・組立コードは無変更)。level: 'a2'(Std) / 'b1b'(Adv)。"""
    if level not in ("a2", "b1b"):
        raise ValueError(level)
    import er110_family_y_audio_trial_01 as old
    narr = old.Y_VOICE_OF["full_story_part1"]
    if old.Y_VOICE_OF["full_story_part3_c3"] != narr:
        raise RuntimeError("既存Yのリードと最終パートのナレーターVoiceが異なります。計画を確定せず停止")
    plan = [("lead", "full_story_part1", narr)]
    for i, (s, seg) in enumerate((("voice_1", "full_story_part2"), ("voice_2", "full_story_part3"), ("voice_3", "full_story_part3_c2")), start=1):
        plan.append((f"intro_{s}", f"{seg}_intro", narr))
        plan.append((s, seg, old.Y_VOICE_OF[seg]))
    plan.append(("closing", "full_story_part3_c3", narr))
    return plan


def main():
    ap = argparse.ArgumentParser(description="Family Y 再配達 構成・原稿改善Trial(DEV/Trial専用)")
    ap.add_argument("cmd", choices=("gen", "assemble", "verify"))
    ap.add_argument("--paid", action="store_true", help="有料run。予算承認ファイルも必要")
    ap.add_argument("--stages", default="lead,intro,leadintro_gate,closing_A,closing_B,closing_C")
    a = ap.parse_args()
    {"gen": cmd_gen, "assemble": cmd_assemble, "verify": cmd_verify}[a.cmd](a)


def cmd_assemble(a):
    r0 = rr.load_r0()
    voices = {s: r0[s] for s in SLOTS}
    lead = w1.rdt(f"{REV}/lead/lead.txt").strip()
    intros = json.load(open(f"{REV}/intro/intros.json", encoding="utf-8"))
    for aid in ANGLES:
        pth = f"{REV}/closing_{aid}/closing_final.txt"
        if not os.path.exists(pth):
            print("skip", aid)
            continue
        txt = render_revised(r0["title"], lead, intros, voices, w1.rdt(pth).strip())
        w1.wt(f"{REV}/article_revised_{aid}.md", txt)
        print(aid, check_revised(txt, r0))


def cmd_verify(a):
    r0 = rr.load_r0()
    srcs = rr.load_sources()
    old = load_old_ja()
    res = {"cases": []}
    for aid in ANGLES:
        pth = f"{REV}/article_revised_{aid}.md"
        if not os.path.exists(pth):
            continue
        txt = open(pth, encoding="utf-8").read()
        d = parse_revised(txt)
        new_texts = {"lead": d["lead"], "closing": d["closing"], **{f"intro_voice_{i + 1}": d["voices"][i]["intro"] for i in range(3)}}
        verb = {k: len(rr.shingle_hits_ja(t, srcs, 20)) for k, t in new_texts.items()}
        res["cases"].append({"angle": aid, "check_revised": check_revised(txt, r0), "mapping": mapping_check_revised({"ja": d}),
                             "verbatim_hits_20": verb, "length_table": length_table(old, d),
                             "closing_monitors": p.tension_monitors(d["closing"]),
                             "closing_bigram_overlap_with_voices": {s: round(len(y0._bigrams(d["closing"]) & y0._bigrams(r0[s])) / max(1, len(y0._bigrams(d["closing"]) | y0._bigrams(r0[s]))), 3) for s in SLOTS},
                             "old_closing_bigram_overlap_with_voices": {s: round(len(y0._bigrams(old["closing"]) & y0._bigrams(r0[s])) / max(1, len(y0._bigrams(old["closing"]) | y0._bigrams(r0[s]))), 3) for s in SLOTS}})
    w1.wj(f"{REV}/verify_result.json", res)
    print(json.dumps([{"angle": c["angle"], "ok": c["check_revised"]["ok"], "mapping_ok": c["mapping"]["ok"], "verbatim": sum(c["verbatim_hits_20"].values())} for c in res["cases"]], ensure_ascii=False))


if __name__ == "__main__":
    main()
