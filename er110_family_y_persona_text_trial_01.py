# -*- coding: utf-8 -*-
"""er110_family_y_persona_text_trial_01.py
FAMILY-Y-VOICES-DESIGN-01 委任_08 Phase B: Family Y「Persona→Voice」DEV/Trial専用 module(テキスト段階)。

位置づけ(重要):
  - Family Yは未採用(Production採用はユーザー判断待ち)。本moduleは**どのProduction runnerからも参照されない**
    (参照0はtestでGrep固定)。環境変数・flag・CLI引数でProduction挙動が変わる経路もない。
  - 既存 er110_family_y_text_trial_01.py(旧Y Trial)は**無変更**。本fileはそのAPI呼出/Leakage schema等の部品を
    importして読取り利用するのみ。X/Zの.py・Prompt・閾値・辞書は変更しない。
  - 新しい合格基準・Validatorは追加しない。Leakage Checkは旧B承認13項目(Voice 7 + Tension 6)の日本語移植をそのまま使う。
    変更点は「判定対象セクションを、Gate前にVoice 3本・Gate後にTension 1本へ分けて渡す」ことだけ(項目の定義は不変)。
  - 決定論モニタ(monitors)は記録専用でGateにしない。
構成(OF-Y3-04: Tension+ClosingはGate通過後のVoice本文から生成):
  Persona Sheet(手作業, Arm H)→ Voice×3(別call)→ Voice Leakage Gate → Tension+Closing → Tension Leakage Gate
  → 見出し(JA+EN)→ 忠実英訳(Y wrapper, 話者コントラスト保持)→ Std簡易化(Y wrapper)
"""
from __future__ import annotations

import json
import os
import re

import er003_audio_tts_asr_safety as safety
import er053_family_x_factlock_ja_writer_01 as w1
import er110_family_y_text_trial_01 as y0     # 旧Y Trial(無変更)。chat/resp_meta/YStop/Leakage schema等を読取り利用

MANAGEMENT_ID = "FAMILY-Y-VOICES-DESIGN-01"
THEME_TAG = "FAMILY_Y_PERSONA_TRIAL_01"
MODEL_TOP = y0.MODEL_TOP        # gpt-6.1-sol(25節: 最新世代最上位系)
MODEL_CHEAP = y0.MODEL_CHEAP    # gpt-6-luna(M7校正済みLeakage判定器・見出し・評価補助。理由は各evidenceに記録)
y0.THEME_TAG = THEME_TAG       # cost loggerのstageタグ(旧Y Trialのchat()がmodule変数を参照するため、本process内のみ差替え)

VOICE_SLOTS = ("voice_1", "voice_2", "voice_3")
TTS_VOICE_FIXED = {"voice_1": "Algieba", "voice_2": "Zephyr", "voice_3": "Schedar"}
PARA_ROLES = ("voice_1", "voice_2", "voice_3", "tension")        # 本文4パート(リード廃止=案A)
YStop = y0.YStop

# ============================================================
# 共通前提(OF-Y3-02: Comment 1とSheetの両方に固定する具体案)
# ============================================================
COMMON_PREMISE_JA = ("学校が、登校した生徒のスマホを朝にまとめて預かり、下校のときに返す(登校している間はずっと預かる)"
                     "ルールにするかどうか。")

# ============================================================
# Persona Sheet 最終版(手作業 = Arm H。DESIGN_PROPOSAL_04 §3。Opus所見OF-Y3-01/02/03/07/09/12/13反映)
# ============================================================
SHEETS = {
    "voice_1": {
        "tts_voice": "Algieba", "gender": "男性", "first_person": "俺",
        "label": "設備工事会社の現場監督(父親)",
        "profile": "43歳。設備工事会社の現場監督で、帰りは遅い。妻と、高校に通う娘の3人暮らし。持ち家は地方都市。",
        "relation": "娘は全日制の高校。保護者会は仕事で半分しか行けず、学校の様子は娘の話とお知らせで知る。",
        "experience": ("以前、夜は居間のカゴにスマホを預けるルールを娘と決めたが守られず、取り上げた翌朝の食卓が気まずくなった。"
                       "娘に「みんなグループで話してる。私だけ返事が遅れると外される」と言われ、言い返せなかった。"
                       "自分は現場で若手がスマホを見ると怒るのに、家では食事中に自分も見ていて、娘に指摘された。"),
        "values": "決めたことは守る、が信条。ただ、怒鳴って押さえつけた自分の父のようにはなりたくない。",
        "rhythm": "短い文の連続が基本(1文は約8〜16字、平均15字前後)。長い文は後悔や言い訳を言う場面で1つだけ(約40字)。",
        "speaking": [
            "短い文でぼそっと言い切る。1文が長くなるのは、後悔や言い訳を言うところだけ",
            "問い返しはほとんどしない。断言と、自分への突っ込みで話す",
            "現場の言葉(現場、段取り、若手、怒る)が日常の言い回しに混ざる",
            "「うちの娘」「俺は」を主語にすることが多い",
            "最後に、自分を少し笑うような一言を置く",
        ],
        "feel_reason": ("学校が朝に預かって下校時に返すと決めてくれるなら、正直助かる。家で毎晩、自分だけが悪者になる役を引き受けるのに疲れている。"
                        "でも、それを学校に頼って楽になりたいだけではないか、という引っかかりもある。"),
        "unique": "学校からは見えない夜の家の中の攻防。親が悪者役を一人で担う消耗と、取り上げた翌朝の食卓の気まずさ。",
        "claim": ("学校が朝に一律で預かって下校時に返すと決めてくれれば、「学校もそう言ってる」と言える。"
                  "俺ひとりが悪者にならずに済む。"),
        "seeds": [
            "居間の充電カゴと、取り上げた翌朝の食卓の沈黙",
            "娘の「私だけ返事が遅れると外される」に言い返せなかったこと",
            "現場で若手を怒る自分が、家では食事中に見ていて娘に指摘されたこと",
        ],
        "identity_cue": "現場の仕事で帰りが遅いこと、または高校に通う娘がいることを、冒頭の2文以内に出来事や状況として自然に出す(自己紹介文にしない)",
        "identity_keywords": ["現場", "娘", "仕事"],
        "order": "主張 → 具体的な場面 → 感情・引っかかり",
        "closing_type": "自嘲的な断言(自分を少し笑って言い切る。まとめや教訓にしない)",
        "closing_example": "例(そのまま使わず、同じ型で本人の言葉で): 結局、楽したいだけなんだよな、俺は。",
        "fact": {"id": "JP-03", "tag_no": 1,
                 "text": "国の通知は、高校については校内での携帯電話の使用を制限すべきだという考え方を示している(持ち込み禁止ではなく、校内使用の制限)。",
                 "allowed": "本人が主語の伝聞・印象の言い方で1文だけ。例: 「国も、高校は校内で使うのは控えさせる考えらしいって、聞いたことがある」",
                 "forbidden": "「持ち込み禁止」と言い換える/年月・通知名・数字を出す/「だから禁止が正しい」と論証に使う/「〜という」「〜ことが分かった」型の報告調"},
        "heading_seed": "Tired of being the bad guy",
        "tension_object": "夜の居間のカゴ",
    },
    "voice_2": {
        "tts_voice": "Zephyr", "gender": "女性", "first_person": "私",
        "label": "高校の養護教諭(保健室の先生)",
        "profile": "54歳。県立の全日制高校の養護教諭。勤続は長い。夫と2人暮らしで、息子は独立している。",
        "relation": "保健室は「取り調べない、没収しない」を自分の流儀にしている。担任や生徒指導の先生とは対等に話せる立場。",
        "experience": ("朝いちばんに来て「頭が痛い」「眠い」と言う子に、よく聞くと明け方まで友達と通話したり動画を見たりしていた子がいた。"
                       "ベッドで休む子の枕元で、スマホの画面が光っているのを見たことがある。昼間に先生に取り上げられた翌日から、保健室に顔を出さなくなった子もいた。"
                       "最近、先生から「禁止にしたら保健室に来る子は減る?」と聞かれて、答えに詰まった。"),
        "values": "「ここなら本当のことを言える」と子どもが思える場所を守りたい。取り締まる側に立つと、その場所がなくなる。",
        "rhythm": "短い断片(5〜8字、2つまで)と、言い淀みながら続く長めの文(約35〜55字、3〜4つ)を行き来する。平均は約30字。中くらいの文を並べない。",
        "speaking": [
            "問い返しが多い。自分に問い、聞き手にも問いかける(「〜なんだろう」「〜でしょう?」)",
            "短い断片をぽつりと置く(「眠い、って。」「頭が痛い、って。」)",
            "中くらいの長さの文を、言い淀みながらゆっくり続ける(「〜かな」「〜と思う」「〜じゃないかな」)",
            "職業の言葉(保健室、ベッド、朝いちばん)と、「あの子」「子ども」という呼び方",
            "断言は少ない。断言するときは短く一言で言い切る(「それは、違う」)",
        ],
        "feel_reason": ("保健室まで没収の場にしたくない。朝に預かる仕組みで「対策した」と安心されたら、夜のことを打ち明けてくれる子の行き場がなくなるのが怖い。"
                        "本当に言いたいのは、取り上げるかどうかより、そのあと誰が子どもの話を聞くのか、ということ。"),
        "unique": "朝の保健室で、子どもの様子の変化を一人ずつ見てきたこと。取り上げられた後に子どもがどう振る舞うか。取り締まらない場所の価値。",
        "claim": "保健室まで没収の場にしたくない。禁止で「対策した」と安心されたら、夜のことを打ち明けてくれる子の行き場がなくなる、と私は思う。",
        "seeds": [
            "この前の朝、ベッドで寝ている子の枕元で画面が光っていたこと",
            "昼間に取り上げられた翌日から、保健室に来なくなったある子のこと",
            "先生に「禁止にしたら保健室に来る子は減る?」と聞かれて答えに詰まったこと",
        ],
        "identity_cue": "朝いちばんに保健室へ来る子の様子から語り出し、その顔を毎朝見る立場であることが自然に分かるようにする(自己紹介文にしない)",
        "identity_keywords": ["保健室", "朝いちばん", "ベッド"],
        "order": "具体的な場面(朝の保健室) → 感情 → 主張(この人だけ主張が最後に来る)",
        "closing_type": "問い返し(自分や聞き手に問いを残す。答えは言わない)",
        "closing_example": "例(そのまま使わず、同じ型で本人の言葉で): 取り上げて、それで安心してしまって、本当にいいのかな。",
        "fact": None,
        "heading_seed": "The sleepy faces in the morning",
        "tension_object": "朝の保健室のベッドの枕元で光る画面",
    },
    "voice_3": {
        "tts_voice": "Schedar", "gender": "男性", "first_person": "僕",
        "label": "昼は倉庫で働き、夜は定時制高校に通う生徒(19歳)",
        "profile": "19歳。県立定時制高校(夜間)の3年生。昼は食品配送センターで仕分けのシフト勤務。母(パート)と中学生の妹の3人暮らしで、生活費の一部を入れている。",
        "relation": "中学のころは学校に行けない時期があった。定時制では先生が話を聞いてくれて、初めて授業が分かると思えた。学校は好きで、ここで卒業したい。",
        "experience": ("休憩中に、次の週のシフト変更の連絡が来る。返事が遅いと、他の人に回される。以前、授業中に職場から着信が続いたのに出られず、"
                       "あとで「連絡がつかないのは困る」と言われてシフトを減らされかけた。クラスの子が授業中にスマホを触って没収され、揉めたのを見て、"
                       "あれは違うと思い、自分は授業中は鞄の奥に入れている。"),
        "values": "守れる約束と、守れない約束を分けたい。信用は自分で作るものだと思っている。",
        "rhythm": "中くらいの短い文(約12〜24字、平均約18字)を重ね、「でも」で切り返す。長い文は作らない。言い切りの一文は短くする。",
        "speaking": [
            "短い文を重ねる。「でも」で言い返すように続ける",
            "約束と条件をはっきり言う(「約束する。でも、〜は無理だ」)",
            "仕事の言葉(シフト、仕分け、休憩、連絡、回される)が自然に出る",
            "「僕は」で始める文が多い。若者言葉は無理に入れない",
            "言い切るところは短く、言いにくいところは少し長くなる",
        ],
        "feel_reason": ("授業中に触らないことは約束できる。でも、朝から預けっぱなしにするのは守れない約束になる。仕事の連絡が切れたら、信用をなくして、"
                        "仕事か学校かの二択になってしまう。全員一律に決める前に、自分のような生徒の事情を聞いてほしい。"),
        "unique": "生計と学校の両立。一律のルールが働く生徒の生活にどう当たるか。守れる約束と守れない約束の違い。",
        "claim": "授業中は鞄の奥に入れると約束する。でも、朝から預けっぱなしにするのは、仕事の連絡が切れるから守れない。",
        "seeds": [
            "休憩中に来るシフト変更の連絡と、返事が遅いと他の人に回される仕事",
            "授業中に着信が続いて出られず、あとで言われたこと",
            "授業中に触って没収され、揉めたクラスの子を見て、自分は鞄の奥に入れていること",
        ],
        "identity_cue": "昼は倉庫で働き、夜に定時制へ通っていることを、冒頭の2文以内に自分の生活の事実として自然に出す(自己紹介文にしない)",
        "identity_keywords": ["倉庫", "定時制", "仕分け", "シフト"],
        "order": "主張 → 具体的な場面 → 感情",
        "closing_type": "約束と要求(自分が守る約束を言い、その代わりに求めることを一つ言う)",
        "closing_example": "例(そのまま使わず、同じ型で本人の言葉で): 授業中は絶対に触らない。だから、決める前に僕らの話を聞いてほしい。",
        "fact": None,
        "heading_seed": "The shift I can't lose",
        "tension_object": "休憩中に届くシフトの連絡",
    },
}


def derive_not_my_point(sheets: dict = None) -> dict:
    """他2人の『自然に生まれる主張』を決定論で連結(LLM呼出0)。"""
    sheets = sheets or SHEETS
    return {s: [sheets[o]["claim"] for o in VOICE_SLOTS if o != s] for s in VOICE_SLOTS}


NUM_RE = y0.NUM_RE
FIRST_PERSON_RE = y0.FIRST_PERSON_RE
SENT_SPLIT_RE = y0.SENT_SPLIT_RE
LABEL_START_RE = y0.LABEL_START_RE
ROLE_WORD_RE = re.compile(r"(〜じゃ|ですわ|あたくし|でござる|のじゃ|だぜ|だわよ)")
INTERVIEW_RE = re.compile(r"(取材|話を聞い|聞いてみ|インタビュー|直撃|we talked|we spoke)", re.I)


def validate_sheets(sheets: dict = None) -> list:
    """Sheetの決定論整合確認(新Validatorではない)。項目充足・主張が短い・数字なし・声の性別/一人称の整合・事実は最大2件・締めの型が3種。"""
    sheets = sheets or SHEETS
    errs = []
    need = ("tts_voice", "gender", "first_person", "label", "profile", "relation", "experience", "values", "speaking", "feel_reason",
            "unique", "claim", "seeds", "rhythm", "identity_cue", "identity_keywords", "order", "closing_type", "closing_example", "heading_seed",
            "tension_object")
    exp_gender = {"voice_1": "男性", "voice_2": "女性", "voice_3": "男性"}
    for s in VOICE_SLOTS:
        sh = sheets.get(s)
        if not sh:
            errs.append(f"SHEET_MISSING:{s}")
            continue
        for k in need:
            if not sh.get(k):
                errs.append(f"SHEET_EMPTY:{s}:{k}")
        if sh.get("tts_voice") != TTS_VOICE_FIXED[s]:
            errs.append(f"SHEET_TTS_VOICE_MISMATCH:{s}")
        if sh.get("gender") != exp_gender[s]:
            errs.append(f"SHEET_GENDER_MISMATCH:{s}")
        if re.search(r"[0-9０-９]", sh.get("claim", "")) or NUM_RE.search(sh.get("claim", "")):
            errs.append(f"SHEET_CLAIM_HAS_NUMBER:{s}")
        if len([x for x in SENT_SPLIT_RE.split(sh.get("claim", "")) if x.strip()]) > 3:
            errs.append(f"SHEET_CLAIM_NOT_SHORT:{s}")
        if len(sh.get("speaking") or []) < 4:
            errs.append(f"SHEET_SPEAKING_FEATURES_LT4:{s}")
        if sh.get("fact") and not sh["fact"].get("allowed"):
            errs.append(f"SHEET_FACT_NO_ALLOWED_EXPRESSION:{s}")
    if len({sheets[s]["first_person"] for s in VOICE_SLOTS if s in sheets}) != 3:
        errs.append("SHEET_FIRST_PERSON_NOT_DISTINCT")
    if len({sheets[s]["closing_type"].split("(")[0] for s in VOICE_SLOTS if s in sheets}) != 3:
        errs.append("SHEET_CLOSING_TYPE_NOT_DISTINCT")
    if sum(1 for s in VOICE_SLOTS if sheets.get(s, {}).get("fact")) > 2:
        errs.append("SHEET_FACT_COUNT_GT2")
    return errs


def render_sheet(slot: str, sheets: dict = None) -> str:
    sheets = sheets or SHEETS
    sh = sheets[slot]
    nmp = derive_not_my_point(sheets)[slot]
    speaking = "\n".join(f"  - {x}" for x in sh["speaking"])
    seeds = "\n".join(f"  - {x}" for x in sh["seeds"])
    nmp_s = "\n".join(f"  - {x}" for x in nmp)
    if sh.get("fact"):
        f = sh["fact"]
        fact = (f"この人が知っていてよい世の中の事実は次の1つだけ(補助。{f['id']})。\n  内容: {f['text']}\n  使い方: {f['allowed']}\n  禁止: {f['forbidden']}\n"
                f"  この事実を述べる文の終わり(句点の直後)に【事実{f['tag_no']}】を付ける。")
    else:
        fact = "この人が語ってよい世の中の事実はない。調査・統計・制度・他の国や学校の動きにはふれない(個人の出来事と感覚だけで語る)。"
    return (f"人物: {sh['label']}(声は{sh['gender']}の成人。一人称は「{sh['first_person']}」)\n"
            f"年齢・職業・生活: {sh['profile']}\n学校・家庭との関係: {sh['relation']}\n"
            f"過去の経験と現在の悩み: {sh['experience']}\n大切にしている価値観: {sh['values']}\n"
            f"文の長さとリズム(英語にしても残る型。必ず守る): {sh['rhythm']}\n"
            f"話し方の特徴(英語にしても残る型):\n{speaking}\n"
            f"今回の案に何を感じ、なぜそう考えるか: {sh['feel_reason']}\n"
            f"この人だからこそ語れること: {sh['unique']}\n"
            f"この人の主張(聞けば一文で言える。そのまま読み上げず、本人の言葉で): {sh['claim']}\n"
            f"具体論の種(この中から1〜2つを、行為・物・場所・相手の言葉が分かる形で書く):\n{seeds}\n"
            f"この人の領分ではない論点(中心の主張にしない。触れるなら最大1文):\n{nmp_s}\n"
            f"事実: {fact}")


# ============================================================
# Voice Writer Prompt(Voiceごとに別call。Sheet 1枚+共通規則のみ見る)
# ============================================================
VOICE_DEVELOPER = ("あなたは日本語のラジオ読み物の書き手です。与えられた人物本人になりきって、その人が自分の言葉で、"
                   "自分の経験と気持ちから意見を語る短い一人称の語りを書きます。説明文や解説文ではなく、実在しそうな一人の人間の語りにします。")

VOICE_PROMPT_TMPL = """次の人物「本人」が、ラジオで自分の考えを語る、一人称の語りを1段落だけ書いてください。

テーマ: 学校でスマホを禁止すべきか。今回、3人は次の同じ具体案について、それぞれの暮らしと立場から意見を語ります。
【3人に共通の前提(この案を前提に語る)】
@@PREMISE@@

【人物(Persona Sheet。本文に全項目を説明しない。背景は言い方・内容・感情に自然に現れればよい)】
@@SHEET@@

【語りの作り方(厳守)】
1. 約260〜300字。話し言葉の常体(「〜だ」「〜なんだ」「〜と思う」「〜だよね」など)。「です・ます」調にしない。新聞・教材のような文章にしない。
2. 語りの順序: @@ORDER@@
3. 冒頭の2文以内に、この人物がどんな人か(仕事・立場・家族など)が聞き手に自然に分かる手がかりを入れる。手がかり: @@CUE@@。「私は〜の者です」「〜をしています」のような自己紹介の文は書かない。
4. 主張の核は1つだけ。聞けば一文で言える形で、本人の言葉で言い切る(位置は上の「語りの順序」に従う)。Sheetの主張文をそのまま読み上げない。他の論点(主張に直接つながらない悩みや事情)は入れず、締めの一言で主張の核に戻る。
5. 具体論: 具体論の種から1つ、多くても2つだけを選び、出来事を並べ立てず、1つの場面を少し細かく(物・場所・相手の言葉・自分の動き)描く。抽象名詞(責任・価値・判断・根拠・余地・視点・基準など)で言い換えない。1文に抽象名詞は2つまで。
6. 主観・感情: この人の気持ちが動くところを1か所以上。感情の名前を並べず、言い方・行為・間に出す。ためらい(言い淀み・自分への突っ込み)は多くても1か所。
7. 「文の長さとリズム」と「話し方の特徴」(上記)を、文の長さ・問い返し・言い切り・語彙に実際に反映する。3人の語りは、文の長さとリズム、語り出し、言葉の層が互いに違って聞こえなければならない(3人の平均文長が揃ってしまうのは失敗)。自分や聞き手への問いかけの文は、文末を「？」にする。
8. 締め: @@CLOSING@@ 締めはまとめ・教訓・一般論にしない。
9. 世の中の出来事の扱い: 人物が書けるのは、本人が見たり聞いたり経験した個別の出来事(「この前」「ある子が」「娘が」など)だけ。「多くの子が〜」「最近は〜が増えている」のような、頻度・傾向・原因の一般化は、Sheetの事実にない限り書かない。人の気持ちや考え方を推測で述べるときは、「〜と思う」「〜気がする」のように本人の推測だと分かる形にする。
10. 事実を使う場合は、本人が主語の伝聞・印象で1文だけ、数字・調査名・年月を使わず、論証の根拠にしない(主張は事実がなくても成立し、事実は補助の一言)。「調査では〜」「〜という結果が出ている」のように、調査・研究・報告が主語の文は書かない。事実がない人物は、事実を一切入れない。
11. 数字(算用数字・漢数字の数量表現)を使わない。実在の人名・学校名・組織名・製品名・出来事を出さない。Sheetにない出来事(誰が何と言った、何があった)を新しく作らない。感覚的な細部の補足は可。
12. 役割語(〜じゃ、〜わよ、〜ぜ等)・方言の演出・擬音・過度な感嘆・泣き笑い・「！」の連発をしない。比喩は多くても1つ。
13. 括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字を使わない。
14. 他の人の領分(上記)を中心の主張にしない。

出力はこの人物の語りの本文のみ(見出し・ラベル・説明なし。1段落)。"""


def build_voice_prompt(slot: str, sheets: dict = None, premise: str = COMMON_PREMISE_JA) -> str:
    sheets = sheets or SHEETS
    sh = sheets[slot]
    return (VOICE_PROMPT_TMPL.replace("@@PREMISE@@", premise).replace("@@SHEET@@", render_sheet(slot, sheets))
            .replace("@@ORDER@@", sh["order"]).replace("@@CUE@@", sh["identity_cue"])
            .replace("@@CLOSING@@", f"{sh['closing_type']}。{sh['closing_example']}"))


def check_voice(text: str, slot: str, sheets: dict = None) -> dict:
    """構造契約(1段落・一人称・ラベルなし)。新しい品質Validatorではない(旧Y Trialのcheck_contractと同種)。"""
    sheets = sheets or SHEETS
    sh = sheets[slot]
    v = []
    t = (text or "").strip()
    if not t:
        v.append("EMPTY")
    if "\n" in t:
        v.append("MULTI_PARAGRAPH")
    if LABEL_START_RE.match(t):
        v.append("LABEL_AT_START")
    if sh["first_person"] not in t:
        v.append(f"NO_FIRST_PERSON:{sh['first_person']}")
    return {"ok": not v, "violations": v}


def voice_monitors(text: str, slot: str, sheets: dict = None) -> dict:
    """記録専用(Gateにしない)。"""
    sheets = sheets or SHEETS
    sh = sheets[slot]
    sents = [s for s in SENT_SPLIT_RE.split(text) if s.strip()]
    lens = [len(s) for s in sents]
    first2 = "".join(sents[:2])
    return {"note": "記録専用。合否に使わない", "chars": len(text), "sentences": len(sents),
            "mean_sentence_chars": round(sum(lens) / max(1, len(lens)), 1), "max_sentence_chars": max(lens) if lens else 0,
            "numbers": NUM_RE.findall(text), "exclamations": text.count("！") + text.count("!"),
            "question_marks": text.count("？") + text.count("?"), "role_words": ROLE_WORD_RE.findall(text),
            "interview_expr": INTERVIEW_RE.findall(text),
            "identity_cue_in_first2": [k for k in sh["identity_keywords"] if k in first2],
            "self_intro_pattern": bool(re.search(r"(者です|をしています|と申します|ものです)", first2)),
            "first_person_count": text.count(sh["first_person"]),
            "other_first_person": [p for p in ("私", "俺", "僕") if p != sh["first_person"] and p in text],
            "ends_with_question": bool(re.search(r"[？?]\s*$", text.strip())),
            "closing_last_sentence": sents[-1].strip() if sents else ""}


def _fin(raw: str) -> tuple:
    clean = w1.clean_ja_for_next(raw)
    final = w1.postprocess_ja(clean).strip()
    return final, safety.detect_prohibited_symbols(final, language="ja")


def generate_voice(client, slot: str, *, out_dir: str, sheets: dict = None, model: str = MODEL_TOP, effort: str = "high") -> dict:
    """Voice 1本をSheetだけから別callで生成。構造契約/記号QA違反は1回だけ再生成(X流)、残ればSTOP。"""
    sheets = sheets or SHEETS
    os.makedirs(out_dir, exist_ok=True)
    prompt = build_voice_prompt(slot, sheets)
    w1.wt(os.path.join(out_dir, f"{slot}_prompt.txt"), prompt)
    calls, hist = [], []
    cur = prompt
    for k in (1, 2):
        resp = y0.chat(client, model=model, effort=effort, user=cur, developer=VOICE_DEVELOPER, stage=f"yp_{slot}" + ("" if k == 1 else "_regen"))
        raw = resp.output_text.strip()
        calls.append({**y0.resp_meta(resp), "prompt_sha256": w1.sha_text(cur)})
        w1.wt(os.path.join(out_dir, f"{slot}_raw_try{k}.txt"), raw)
        probs, tags = [], []
        try:
            final, sym = _fin(raw)
            probs += check_voice(final, slot, sheets)["violations"]
            if safety.symbol_gate_requires_stop(sym):
                probs.append(f"SYMBOL:{sym}")
            tags = sorted({t for m in w1.TAG_RE.finditer(raw) for t in w1.tag_ids(m.group(0))})
            allowed = {f"F{sheets[slot]['fact']['tag_no']}"} if sheets[slot].get("fact") else set()
            if set(tags) - allowed:
                probs.append(f"UNEXPECTED_FACT_TAG:{sorted(set(tags) - allowed)}")
        except w1.TagLeak as e:
            final, probs = "", [f"TAG_LEAK:{e}"]
        hist.append(probs)
        if not probs:
            meta = {"slot": slot, "calls": calls, "problems_per_try": hist, "tags_used": tags, "sha256": w1.sha_text(final),
                    "monitors": voice_monitors(final, slot, sheets)}
            w1.wt(os.path.join(out_dir, f"{slot}.txt"), final + "\n")
            w1.wj(os.path.join(out_dir, f"{slot}_meta.json"), meta)
            return {"text": final, "raw": raw, "meta": meta}
        if k == 1:
            cur = prompt + "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {p}" for p in probs)
    raise YStop("VOICE_CONTRACT_STOP", f"{slot}: 再生成後も契約違反 {hist[-1]}", hist)


# ============================================================
# Leakage Check(旧B承認13項目の日本語移植。判定対象セクションを分けて渡すだけ。定義は不変)
# ============================================================
VOICE_FIELDS = y0.VOICE_LEAKAGE_FIELDS
TENSION_FIELDS = y0.TENSION_LEAKAGE_FIELDS

_VOICE_ITEMS = """【Voice 1〜3に共通で適用する7項目】
- leak_evidence_subject: 文の主語が、調査・研究・データ・割合・報告になっている文が無い場合PASS
- leak_numbers_foreground: 具体的な数字が、その人物自身の経験に属する数値であり、かつその人の経験の描写より前面に出ていない場合PASS(数字が0個、またはその人物自身の経験に属する数字が1個だけ実感として自然に織り込まれている場合はPASS。調査・報告・研究等、本人の経験に属さない外部統計をVoice内で論証材料として使っている場合はFAIL)
- leak_narrator_analysis: 語り手が、Voiceの人物を外側から分析・要約していない場合PASS
- leak_unknowable_analysis: その人物自身が実際に考え・言いそうにない、外部の分析的視点を、その人のPerspectiveとして書いていない場合PASS
- leak_discovery_syntax: 「〜が明らかになった」「〜という傾向がある」のような、発見・傾向を報じる記事の文構造へ戻っていない場合PASS
- leak_evidence_memorable: 調査や事実よりも、その人物の経験・感情の方が記憶に残る書き方になっている場合PASS
- leak_position_blur: このVoiceが、自分の立場の中の迷い・葛藤(nuance)の範囲を超えて、他のVoice(相手側)が中心的に抱えている懸念・反論そのものを、自分の中心的な主張として代弁していない場合PASS(相手側の中心論点をこのVoiceが実質的に引き受けてしまっている場合はFAIL)

いずれのVoiceについても、他のVoiceと同一の基準で判定してください(特定の立場が抽象的な代弁者の解説になっている場合は、leak_evidence_subject/leak_narrator_analysis/leak_discovery_syntaxのいずれかでFAILとしてください)。
"""
_TENSION_ITEMS = """【最終パート(Tension)に適用する6項目】
- leak_evidence_subject / leak_discovery_syntax / leak_evidence_memorable: 上記と同じ意味(最終パート本文に対して判定)
- leak_numbers_foreground(最終パート用): 具体的な数字・比較結果が、3人の合理性を制約する力の描写より前面に出ていない場合PASS(1人の経験ではなく複数人の力関係を扱うため、Voice用の「本人の経験に属する数値」限定はここでは適用しない)
- leak_tension_reverts_to_research: 最終パートの中心が、3人がなぜ違う答えに至るのかの掘り下げになっており、調査・研究データそのものの説明・比較へ戻っていない場合PASS
- leak_binary_camp_split: 最終パートが3人を単純に対称的な2対1の陣営へ分けて描いていない場合PASS(分けている場合FAIL)
"""
_FOOT = "\nreasoningには、判定理由を1〜2文の日本語で書いてください。FAILの場合はquoted_evidenceに該当する原文を引用してください。PASSの場合quoted_evidenceは空文字列にしてください。\n"


def leak_sections_for(kind: str) -> dict:
    if kind == "voices":
        return {s: VOICE_FIELDS for s in VOICE_SLOTS}
    if kind == "tension":
        return {"tension": TENSION_FIELDS}
    raise ValueError(kind)


def leak_schema_for(kind: str) -> dict:
    secs = leak_sections_for(kind)

    def item(fields):
        props = {f: {"type": "string", "enum": ["PASS", "FAIL"]} for f in fields}
        props["reasoning"] = {"type": "string"}
        props["quoted_evidence"] = {"type": "string"}
        return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}
    return {"name": f"family_y_persona_leakage_{kind}", "strict": True,
            "schema": {"type": "object", "properties": {k: item(v) for k, v in secs.items()}, "required": list(secs), "additionalProperties": False}}


def build_leak_prompt(kind: str, sections: dict, language_note: str = "日本語") -> str:
    if kind == "voices":
        head = (f"以下は、ある Voices型記事(3人の人物がそれぞれ一人称で語る)の3つのVoiceセクション本文です(本文の言語: {language_note})。"
                "それぞれについて、指定された項目を判定してください(それぞれPASS/FAIL)。\n\n" + _VOICE_ITEMS + _FOOT)
        body = "\n".join(f"【Voice {i + 1}本文】\n{sections[s]}\n" for i, s in enumerate(VOICE_SLOTS))
    else:
        head = (f"以下は、ある Voices型記事(3人の人物がそれぞれ一人称で語った後の)最終パート[Tension]の本文です(本文の言語: {language_note})。"
                "指定された項目を判定してください(それぞれPASS/FAIL)。\n\n" + _TENSION_ITEMS + _FOOT)
        body = f"【最終パート(Tension)本文】\n{sections['tension']}\n"
    return head + "\n" + body


def run_leak(client, kind: str, sections: dict, *, model: str, effort: str, stage: str, language_note: str = "日本語") -> dict:
    prompt = build_leak_prompt(kind, sections, language_note)
    resp = y0.chat(client, model=model, effort=effort, user=prompt, developer=y0.LEAKAGE_DEVELOPER_JA, schema=leak_schema_for(kind), stage=stage)
    text = getattr(resp, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Leakage Check応答が空")
    parsed = json.loads(text)
    flagged = []
    for sec, fields in leak_sections_for(kind).items():
        it = parsed[sec]
        fails = [f for f in fields if it[f] == "FAIL"]
        if fails:
            flagged.append({"section": sec, "fail_fields": fails, "reasoning": it["reasoning"], "quoted_evidence": it["quoted_evidence"]})
    return {"kind": kind, "model": model, "effort": effort, "meta": y0.resp_meta(resp), "prompt_sha256": w1.sha_text(prompt), "parsed": parsed,
            "flagged_items": flagged, "any_flagged": bool(flagged), "n_fail_fields": sum(len(x["fail_fields"]) for x in flagged)}


# ============================================================
# Tension + Closing(Gate後のVoice本文から生成。OF-Y3-04 / OF-Y3-13)
# ============================================================
TENSION_DEVELOPER = ("あなたは日本語のラジオ読み物の語り手(ナレーター)です。3人の語りを聞き終えた聞き手に向けて、"
                     "3人の違いと重なりを、耳で聞いて一度で分かる具体的な言葉で整理し、静かに締めくくります。")
TENSION_RULES = """- 語り手(ナレーター)の声。一人称(私・俺・僕・わたし)は使わない。話し言葉の常体。
- 骨格(地の文のひと続きで。「第1に」などのラベルは書かない): (1)3人が共通して望んでいること(1文。「暮らし」「通学」「苦しい」のような抽象語でまとめず、3人の具体的な場面を入れて言う) → (2)3人の違いを、「いつ・どこで困るか」と「何を守りたいか」を、聞き手が覚えている具体物で対比する(3人の主張を順番に要約し直すのではなく、違いの軸として一続きの文にする) → (3)どこが食い違い、どこが重なるか(1〜2文) → (4)締めを1つだけ。
- 締めは、聞き手が自分の生活から答えられる具体的な問いにする(例: 「あなたの家では、夜、スマホはどこに置いてある?」)。問いの文末は「？」にする。「責任」「価値」「判断」などの抽象名詞を主語にした問いは書かない。結論・教訓・解決策・勝者の決定はしない。
- 1文は45字以内。1文に抽象名詞(責任・価値・判断・根拠・余地・視点・基準・立場・意味など)は2つまで。二重否定を使わない。哲学的な一般化をしない。
- 新しい事実・数字・出来事を足さない。3人を単純な2対1の陣営に分けない。「取材した」「話を聞いた」など実在の取材者がいるような言い方をしない。
- 括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字を使わない。"""


def build_tension_prompt(voices: dict, sheets: dict = None) -> str:
    sheets = sheets or SHEETS
    vs = "\n\n".join(f"【人物{i + 1}の語り({sheets[s]['label']})】\n{voices[s]}" for i, s in enumerate(VOICE_SLOTS))
    objs = "\n".join(f"- 人物{i + 1}: {sheets[s]['tension_object']}" for i, s in enumerate(VOICE_SLOTS))
    claims = "\n".join(f"- 人物{i + 1}: {sheets[s]['claim']}" for i, s in enumerate(VOICE_SLOTS))
    return (f"3人の人物が、次の同じ案について、それぞれの暮らしから意見を語り終えました。語り手として、最後の1パート(Tension+Closing)を書いてください。\n\n"
            f"【3人に共通の前提】{COMMON_PREMISE_JA}\n\n{vs}\n\n【3人の主張の要点(参考。要約し直さない)】\n{claims}\n"
            f"【対比に使える具体物(3人の本文に出てきたものを優先して使う)】\n{objs}\n\n【書き方】\n{TENSION_RULES}\n- 長さ: 約200〜240字、1段落。\n\n"
            "出力は最終パートの本文のみ(見出し・ラベルなし)。")


def check_tension(text: str) -> dict:
    v = []
    t = (text or "").strip()
    if not t:
        v.append("EMPTY")
    if "\n" in t:
        v.append("MULTI_PARAGRAPH")
    if FIRST_PERSON_RE.search(t):
        v.append("HAS_FIRST_PERSON")
    if LABEL_START_RE.match(t):
        v.append("LABEL_AT_START")
    return {"ok": not v, "violations": v}


ABSTRACT_NOUNS = ("責任", "価値", "判断", "根拠", "余地", "視点", "基準", "立場", "意味", "目的", "方針", "効果", "環境", "仕組み", "優先", "尊厳")
DOUBLE_NEG_RE = re.compile(r"(ないわけではない|なくはない|ないとは言えない|ないではない|ずにはいられない|ないことはない)")


def tension_monitors(text: str) -> dict:
    sents = [s for s in SENT_SPLIT_RE.split(text) if s.strip()]
    lens = [len(s) for s in sents]
    return {"note": "記録専用。合否に使わない", "chars": len(text), "sentences": len(sents), "max_sentence_chars": max(lens) if lens else 0,
            "sentences_over_45": [s.strip() for s in sents if len(s) > 45],
            "abstract_noun_max_per_sentence": max((sum(s.count(w) for w in ABSTRACT_NOUNS) for s in sents), default=0),
            "double_negatives": DOUBLE_NEG_RE.findall(text), "numbers": NUM_RE.findall(text), "interview_expr": INTERVIEW_RE.findall(text),
            "ends_with_question": bool(re.search(r"[？?]\s*$", text.strip())),
            "last_sentence": sents[-1].strip() if sents else ""}


def generate_tension(client, voices: dict, *, out_dir: str, sheets: dict = None, model: str = MODEL_TOP, effort: str = "high") -> dict:
    os.makedirs(out_dir, exist_ok=True)
    prompt = build_tension_prompt(voices, sheets)
    w1.wt(os.path.join(out_dir, "tension_prompt.txt"), prompt)
    calls, hist, cur = [], [], prompt
    for k in (1, 2):
        resp = y0.chat(client, model=model, effort=effort, user=cur, developer=TENSION_DEVELOPER, stage="yp_tension" + ("" if k == 1 else "_regen"))
        raw = resp.output_text.strip()
        calls.append({**y0.resp_meta(resp), "prompt_sha256": w1.sha_text(cur)})
        w1.wt(os.path.join(out_dir, f"tension_raw_try{k}.txt"), raw)
        probs = []
        try:
            final, sym = _fin(raw)
            probs += check_tension(final)["violations"]
            if safety.symbol_gate_requires_stop(sym):
                probs.append(f"SYMBOL:{sym}")
        except w1.TagLeak as e:
            final, probs = "", [f"TAG_LEAK:{e}"]
        hist.append(probs)
        if not probs:
            meta = {"calls": calls, "problems_per_try": hist, "sha256": w1.sha_text(final), "monitors": tension_monitors(final)}
            w1.wt(os.path.join(out_dir, "tension.txt"), final + "\n")
            w1.wj(os.path.join(out_dir, "tension_meta.json"), meta)
            return {"text": final, "meta": meta}
        if k == 1:
            cur = prompt + "\n\n【前回の出力の問題(今回は避けてください)】\n" + "\n".join(f"- {p}" for p in probs)
    raise YStop("TENSION_CONTRACT_STOP", f"tension: 再生成後も契約違反 {hist[-1]}", hist)


# ============================================================
# 局所書き換え(旧規則 R-P05/R-P07/R-P12/R-P13/R-P14/R-P15 は持ち込まない。Sheet準拠)
# ============================================================
REWRITE_SCHEMA = {"name": "family_y_persona_rewrite", "strict": True,
                  "schema": {"type": "object", "additionalProperties": False, "required": ["rewrites"],
                             "properties": {"rewrites": {"type": "array", "items": {
                                 "type": "object", "additionalProperties": False, "required": ["section", "text"],
                                 "properties": {"section": {"type": "string"}, "text": {"type": "string"}}}}}}}
REWRITE_DEVELOPER = "あなたは日本語ラジオ読み物の編集者です。指定された段落だけを、指摘された問題を直して書き換えます。他の段落には一切触れません。"


def build_voice_rewrite_prompt(texts: dict, flagged: list, sheets: dict = None) -> str:
    sheets = sheets or SHEETS
    blocks = []
    for f in flagged:
        s = f["section"]
        probs = "\n".join(f"  - {x}: {y0.FIELD_MEANING_JA.get(x, x)}" for x in f["fail_fields"])
        blocks.append(f"■ 書き換える語り: {s}\n現在の本文:\n{texts[s]}\n指摘された問題:\n{probs}\n指摘の理由: {f['reasoning']}\n問題の箇所: {f['quoted_evidence']}\n\n"
                      f"【この人物のPersona Sheet】\n{render_sheet(s, sheets)}")
    others = "\n\n".join(f"[{s}]\n{t}" for s, t in texts.items())
    return f"""次のVoices型記事の、指定した語りだけを書き換えてください。他の語りは読み取り専用です。

【3人に共通の前提】{COMMON_PREMISE_JA}

【3人の語り全体(文脈。読み取り専用)】
{others}

{chr(10).join(blocks)}

【書き換えの規則】
- 指摘された問題だけを直し、その人物の一人称・話し方の特徴・語りの順序・締めの型・冒頭2文以内の身元の手がかり・長さ(元の±20%)・話し言葉の常体を保つ。
- 指摘箇所が「調査・研究・報告が主語の文」「報じるような文構造」「外部統計を論証に使う文」の場合は、削除するか、Sheetに許容事実があるときだけ本人が主語の伝聞・印象の1文(数字・調査名・年月なし、論証に使わない)に直す。調査・統計・制度を説明する文は書かない(許容事実の伝聞1文は除く)。
- 人物が書けるのは本人が経験した個別の出来事だけ。頻度・傾向・原因の一般化を足さない。数字(算用数字・漢数字の数量表現)を使わない。
- 他の人物の中心の論点を自分の中心の主張にしない。迷いや複雑な気持ちは残してよい。
- 実在の人名・組織名・製品名を新しく出さない。Sheetにない出来事を創作しない。
- 括弧・コロン・スラッシュ・三点リーダー・波ダッシュ・絵文字を使わない。
- Sheetに許容事実がある人物が事実を述べる文は、その文の終わりの句点の直後に【事実N】を付ける(Nは該当Sheetの指定)。それ以外の文にはタグを付けない。

出力はJSON: 書き換えた語りごとに {{"section": 語りの名前(例 voice_1), "text": 書き換え後の本文}}。指定した語り以外は出力しない。"""


def build_tension_rewrite_prompt(voices: dict, tension: str, flagged: list) -> str:
    f = flagged[0]
    probs = "\n".join(f"  - {x}: {y0.FIELD_MEANING_JA.get(x, x)}" for x in f["fail_fields"])
    vs = "\n\n".join(f"[{s}]\n{t}" for s, t in voices.items())
    return f"""次の最終パート(語り手の声)だけを、指摘された問題を直して書き換えてください。3人の語りは読み取り専用です。

【3人の語り(読み取り専用)】
{vs}

現在の最終パート:
{tension}
指摘された問題:
{probs}
指摘の理由: {f['reasoning']}
問題の箇所: {f['quoted_evidence']}

【書き換えの規則】
{TENSION_RULES}
- 指摘された問題だけを直し、長さ(元の±20%)・話し言葉の常体を保つ。

出力はJSON: {{"section": "tension", "text": 書き換え後の本文}} を1件だけ含む rewrites 配列。"""


def apply_rewrites(cur: dict, rewrites: list, flagged_keys: set, *, sheets: dict = None, tension: bool = False) -> tuple:
    new = dict(cur)
    errors, applied, got = [], [], set()
    for r in rewrites:
        s = r["section"]
        got.add(s)
        if s not in flagged_keys:
            errors.append(f"REWRITE_OUT_OF_SCOPE:{s}")
            continue
        raw = r["text"] or ""
        try:
            final, sym = _fin(raw)
        except w1.TagLeak as e:
            errors.append(f"REWRITE_TAG_LEAK:{s}:{e}")
            continue
        if not final or "\n" in final:
            errors.append(f"REWRITE_NOT_SINGLE_PARAGRAPH:{s}")
            continue
        if safety.symbol_gate_requires_stop(sym):
            errors.append(f"REWRITE_SYMBOL:{s}:{sym}")
            continue
        if not tension:
            c = check_voice(final, s, sheets)
            if not c["ok"]:
                errors.append(f"REWRITE_CONTRACT:{s}:{c['violations']}")
                continue
        else:
            if FIRST_PERSON_RE.search(final):
                errors.append("REWRITE_TENSION_HAS_FIRST_PERSON")
                continue
        new[s] = final
        applied.append(s)
    if got != flagged_keys:
        errors.append(f"REWRITE_SET_MISMATCH: got={sorted(got)} expected={sorted(flagged_keys)}")
    return new, {"applied": applied, "errors": errors}


def run_gate(client, *, kind: str, stage: str, texts: dict, out_dir: str, judge_model: str, judge_effort: str,
             voices_ctx: dict = None, sheets: dict = None, rewrite_model: str = MODEL_TOP, rewrite_effort: str = "medium",
             max_judgements: int = 3) -> dict:
    """Leakage Check → 局所書き換え → 再判定(判定最大3回=初回+書き換え2回)。残ればLEAKAGE_RESIDUAL_STOP(全文書き直しに戻さない)。
    kind='voices': texts={voice_1..3}。kind='tension': texts={'tension': ...}, voices_ctx=Gate通過済みVoice本文(読み取り専用)。"""
    os.makedirs(out_dir, exist_ok=True)
    cur = dict(texts)
    history, status = [], None
    for attempt in range(1, max_judgements + 1):
        chk = run_leak(client, kind, cur, model=judge_model, effort=judge_effort, stage=f"{stage}_leak{attempt}")
        w1.wj(os.path.join(out_dir, f"leak_check_{attempt}.json"), chk)
        entry = {"attempt": attempt, "sha256": {k: w1.sha_text(v) for k, v in cur.items()}, "check": chk}
        history.append(entry)
        if not chk["any_flagged"]:
            status = "PASS"
            break
        if attempt == max_judgements:
            status = "LEAKAGE_RESIDUAL_STOP"
            break
        keys = {f["section"] for f in chk["flagged_items"]}
        new = None
        for rw_try in (1, 2):
            if kind == "voices":
                prompt = build_voice_rewrite_prompt(cur, chk["flagged_items"], sheets)
            else:
                prompt = build_tension_rewrite_prompt(voices_ctx, cur["tension"], chk["flagged_items"])
            resp = y0.chat(client, model=rewrite_model, effort=rewrite_effort, user=prompt, developer=REWRITE_DEVELOPER, schema=REWRITE_SCHEMA,
                           stage=f"{stage}_rewrite{attempt}" + ("" if rw_try == 1 else "_retry"))
            rws = json.loads(resp.output_text)["rewrites"]
            new, det = apply_rewrites(cur, rws, keys, sheets=sheets, tension=(kind == "tension"))
            entry.setdefault("rewrite_calls", []).append({"try": rw_try, "meta": y0.resp_meta(resp), "details": det, "raw_rewrites": rws})
            if not det["errors"]:
                break
            new = None
        if new is None:
            w1.wj(os.path.join(out_dir, "gate_result.json"), {"status": "REWRITE_STOP", "history": history})
            raise YStop("REWRITE_STOP", f"{stage}: 局所書き換えの決定論検査に2回失敗", history)
        for k in cur:
            if k not in keys and new[k] != cur[k]:
                raise YStop("REWRITE_BYTE_FIX_VIOLATION", f"{stage}: flag外の{k}が変化")
        entry["rewritten"] = sorted(keys)
        cur = new
    result = {"stage": stage, "kind": kind, "status": status, "n_judgements": len(history), "history": history,
              "first_judgement_flagged": history[0]["check"]["any_flagged"], "first_judgement_n_fail_fields": history[0]["check"]["n_fail_fields"],
              "final_sha256": {k: w1.sha_text(v) for k, v in cur.items()}}
    w1.wj(os.path.join(out_dir, "gate_result.json"), result)
    w1.wj(os.path.join(out_dir, "final_texts.json"), cur)
    result["final_texts"] = cur
    return result


def load_gated_or_stop(gate_dir: str) -> dict:
    """Acceptance Gate: Gate結果がPASSでない本文は後続へ流さない。"""
    gp = os.path.join(gate_dir, "gate_result.json")
    if not os.path.exists(gp):
        raise YStop("GATE_RESULT_MISSING", f"{gate_dir}: gate_result.jsonがありません")
    st = json.load(open(gp, encoding="utf-8")).get("status")
    if st != "PASS":
        raise YStop("ACCEPTANCE_GATE_NOT_PASSED", f"{gate_dir}: Gate status={st}")
    return json.load(open(os.path.join(gate_dir, "final_texts.json"), encoding="utf-8"))


# ============================================================
# 見出し(別の小LLM call。OF-Y3-16: A2語彙確認。ordinal prefixは決定論で付与)
# ============================================================
HEADING_ORDINALS = ("One Voice", "Another Voice", "A Third Voice")
HEADING_SCHEMA = {"name": "family_y_voice_headings", "strict": True,
                  "schema": {"type": "object", "additionalProperties": False, "required": ["headings"],
                             "properties": {"headings": {"type": "array", "minItems": 3, "maxItems": 3, "items": {
                                 "type": "object", "additionalProperties": False, "required": ["slot", "title_en", "title_ja"],
                                 "properties": {"slot": {"type": "string", "enum": list(VOICE_SLOTS)},
                                                "title_en": {"type": "string"}, "title_ja": {"type": "string"}}}}}}}


def build_heading_prompt(voices: dict, sheets: dict = None) -> str:
    sheets = sheets or SHEETS
    blocks = "\n\n".join(f"【{s}】一行の主張: {sheets[s]['claim']}\n見出しの種(参考。そのまま使わなくてよい): {sheets[s]['heading_seed']}\n本文:\n{voices[s]}" for s in VOICE_SLOTS)
    return f"""ラジオ番組で、3人の語りの直前にナレーターが短い見出しを読み上げます。各語りの見出しを英語と日本語で作ってください。

{blocks}

【英語の見出し(title_en)の条件】
- 英語を学ぶ人が耳で聞いて分かるやさしい語彙(中学校で習う程度の語)だけを使う。難しい語・慣用句・長い関係節は避ける。
- 5〜7語。具体的な名詞句で、そのVoiceへの興味を引く入口にする。主張の結論を断言しない(「〜すべき」「〜は悪い」にしない)。
- 数字を使わない。3つの見出しで同じ名詞を繰り返さない。カンマ・コロン・引用符・疑問符を使わない。
- 良い例の型: "The headaches that start at night" / "The shift I can't lose"。避ける例: "The basket where the phones sleep"(聞き慣れない比喩で負担が大きい)。
【日本語の見出し(title_ja)】ページ表示用(読み上げない)。英語の見出しの意味に合わせて12字以内。
出力はJSON。"""


def check_headings(headings: list) -> dict:
    v = []
    en = [h["title_en"].strip() for h in headings]
    for i, t in enumerate(en):
        n = len(t.split())
        if not (4 <= n <= 9):
            v.append(f"HEADING_WORDS:{i + 1}:{n}")
        if re.search(r"[0-9:;,\"?!]", t):
            v.append(f"HEADING_SYMBOL_OR_DIGIT:{i + 1}")
    words = [set(w.lower() for w in t.split() if len(w) > 3) for t in en]
    for a in range(3):
        for b in range(a + 1, 3):
            if words[a] & words[b]:
                v.append(f"HEADING_REPEATED_WORD:{a + 1}-{b + 1}:{sorted(words[a] & words[b])}")
    return {"ok": not v, "violations": v}


def generate_headings(client, voices: dict, *, out_dir: str, sheets: dict = None, model: str = MODEL_CHEAP, effort: str = "medium") -> dict:
    os.makedirs(out_dir, exist_ok=True)
    prompt = build_heading_prompt(voices, sheets)
    cur, hist = prompt, []
    for k in (1, 2):
        resp = y0.chat(client, model=model, effort=effort, user=cur, schema=HEADING_SCHEMA, stage="yp_headings" + ("" if k == 1 else "_retry"))
        obj = json.loads(resp.output_text)
        by = {h["slot"]: h for h in obj["headings"]}
        hs = [by[s] for s in VOICE_SLOTS]
        chk = check_headings(hs)
        hist.append({"meta": y0.resp_meta(resp), "check": chk, "headings": hs})
        if chk["ok"]:
            out = [{"slot": s, "ordinal": HEADING_ORDINALS[i], "title_en": by[s]["title_en"].strip(), "title_ja": by[s]["title_ja"].strip(),
                    "spoken_en": f"{HEADING_ORDINALS[i]}: {by[s]['title_en'].strip()}"} for i, s in enumerate(VOICE_SLOTS)]
            w1.wj(os.path.join(out_dir, "headings.json"), {"headings": out, "history": hist})
            return {"headings": out, "history": hist}
        cur = prompt + "\n\n【前回の問題(今回は避ける)】\n" + "\n".join(f"- {p}" for p in chk["violations"])
    raise YStop("HEADING_STOP", f"見出しが2回条件を満たさない {hist[-1]['check']}", hist)


# ============================================================
# 学習支援構造のY用role(Comment 1 / Comment 2。Comment 3/4は置かない)。Xのrole定数は無変更
# ============================================================
_LABEL_BAN = ("【重要・出力への制約】出力する文章自体に\"Part 1\"・\"Full Story\"・\"Voice\"のような制作内部の構造ラベルを含めないでください。"
              "リスナーは番組の内部構成を意識しません。")
_C1_COMMON = ("役割: 今回の話題と、その背景・何が問題になっているのかを、はじめて聞く人にもわかるように伝えます。"
              "今回、番組で考える具体案は次のとおりです(必ず言及してください): 「" + COMMON_PREMISE_JA + "」"
              "登場する人の説明、これから話す人の立場や主張の予告はしません。答えや結論は言いません。"
              "与えられた事実の範囲外の新しいFactは追加しません。Previewの問いをそのまま繰り返さず、背景を1段深くします。"
              "「取材した」「話を聞いた」「we talked to」のように、実在の取材者がいるような言い方はしません。")
_C2_COMMON = ("役割: これから、暮らしも立場も違う3人の声を続けて聞くことを案内します。2文にしてください。"
              "人物の職業・年齢などの紹介、Comment 1の内容の繰り返し、3人の主張の予告はしません。"
              "聞き方の手がかりを1つだけ添えてかまいません(例: それぞれが困る場面の違いに耳を傾ける)。"
              "「取材した」「話を聞いた」「we talked to」のように、実在の取材者がいるような言い方はしません。新しいFactを追加しないでください。")
Y_COMMENT_1_ROLE = {
    "b1b": ("あなたはPodcastのナビゲーターです。これから番組の本編に入ります。Comment 1(役割: Theme Introduction)を英語で書いてください。\n\n"
            + _C1_COMMON + "3〜4文の自然な英語にしてください。\n\n" + _LABEL_BAN),
    "a2": ("あなたはPodcastのナビゲーターです。これから番組の本編に入ります。Comment 1(役割: Theme Introduction)を日本語で書いてください。\n\n"
           + _C1_COMMON + "易しい日本語で3〜4文にしてください。\n\n" + _LABEL_BAN),
}
Y_COMMENT_2_ROLE = {
    "b1b": ("あなたはPodcastのナビゲーターです。リスナーはComment 1でテーマの背景を聞き終わりました。Comment 2(役割: Bridge to the Voices)を英語で書いてください。\n\n"
            + _C2_COMMON + "自然な英語で。\n\n" + _LABEL_BAN),
    "a2": ("あなたはPodcastのナビゲーターです。リスナーはComment 1でテーマの背景を聞き終わりました。Comment 2(役割: Bridge to the Voices)を日本語で書いてください。\n\n"
           + _C2_COMMON + "易しい日本語で。\n\n" + _LABEL_BAN),
}

# Comment 1 の背景fact(OF-Y3-11: Y版B3を再実行せず、台帳から手で選ぶ。中立・Voice事実(JP-03)と重ならない・主張に関与しない)
COMMENT1_FACT_IDS = ("NL-01", "FR-02", "OECD-01")


def comment1_facts_block(ledger_text: str) -> str:
    """台帳から指定IDの記述(本文行+scope/conditions/notes_for_writer)を原文のまま抜き出す(LLM 0 call)。"""
    out = []
    blocks = re.split(r"\n\s*\n", ledger_text)
    for fid in COMMENT1_FACT_IDS:
        hit = [b for b in blocks if re.search(rf"\b{re.escape(fid)}:", b)]
        if not hit:
            raise YStop("LEDGER_FACT_MISSING", f"台帳に{fid}がありません")
        out.append(hit[0].strip())
    return "\n\n".join(out)


# ============================================================
# 英語化: Y専用wrapper(OF-Y3-01(b): 話者コントラスト保持の1文。X関数は無変更、must_fix欄経由=旧S2と同方式)
# ============================================================
def y_contrast_must_fix() -> list:
    return [{"fact_id": "", "claim_in_article": "", "issue": "KEEP_SPEAKER_CONTRAST",
             "explanation": ("Paragraphs 1, 2 and 3 are spoken by three different people in the first person, and paragraph 4 is a narrator. "
                             "Keep each speaker's sentence-length contrast, hesitations, questions-back and directness (blunt short sentences versus "
                             "slower flowing ones), and keep who is speaking, even when you simplify the English. "
                             "Do not even out the rhythm across the paragraphs or turn them into a neutral explanation. "
                             "Keep each speaker's concrete objects and workplace words (job, clinic bed, shifts, basket) rather than abstract wording.")}]


EN_FIRST_PERSON_RE = y0.EN_FIRST_PERSON_RE


def split_en_article(text: str) -> dict:
    return y0.split_en_article(text)


def check_en_contract(text: str) -> dict:
    s = split_en_article(text)
    ps, v = s["paragraphs"], []
    if not s["title"]:
        v.append("EN_NO_TITLE")
    if len(ps) != 4:
        v.append(f"EN_PARAGRAPH_COUNT={len(ps)}")
        return {"ok": False, "violations": v, "split": s}
    if not s["in_one_line"]:
        v.append("EN_NO_IN_ONE_LINE")
    for i in (0, 1, 2):
        if not EN_FIRST_PERSON_RE.search(ps[i]):
            v.append(f"EN_VOICE_NO_FIRST_PERSON: paragraph {i + 1}")
    if re.match(r"^(I|I'm|I've|My|Me)\b", ps[3]):
        v.append("EN_NARRATOR_STARTS_WITH_FIRST_PERSON: paragraph 4")
    return {"ok": not v, "violations": v, "split": s}


def _en_sent_lens(p: str) -> list:
    return [len(x.split()) for x in re.split(r"(?<=[.!?])\s+", p.strip()) if x.strip()]


def en_monitors(text: str) -> dict:
    s = split_en_article(text)
    ps = s["paragraphs"]
    out = {"note": "記録専用", "n_paragraphs": len(ps), "words_per_paragraph": [len(p.split()) for p in ps],
           "words_total_body": sum(len(p.split()) for p in ps), "in_one_line_words": len(s["in_one_line"].split())}
    if len(ps) == 4:
        lens = {PARA_ROLES[i]: _en_sent_lens(ps[i]) for i in range(4)}
        out["mean_words_per_sentence"] = {k: round(sum(v) / max(1, len(v)), 1) for k, v in lens.items()}
        v3 = [out["mean_words_per_sentence"][k] for k in VOICE_SLOTS]
        out["voice_mean_sentence_words_range"] = round(max(v3) - min(v3), 1)
        out["max_sentence_words"] = {k: max(v) if v else 0 for k, v in lens.items()}
        out["question_marks"] = {PARA_ROLES[i]: ps[i].count("?") for i in range(4)}
        out["first_person_tokens"] = {PARA_ROLES[i]: len(EN_FIRST_PERSON_RE.findall(ps[i])) for i in range(4)}
        out["we_tokens"] = {PARA_ROLES[i]: len(re.findall(r"\b(we|we're|we've|our|us)\b", ps[i], re.I)) for i in range(4)}
        out["number_tokens"] = {PARA_ROLES[i]: [m.group(0) for m in y0.EN_NUM_RE.finditer(ps[i])] for i in range(3)}
        out["voice_opening_words"] = [re.split(r"\s+", ps[i].strip())[0].lower() for i in range(3)]
    return out


def render_article(title: str, paragraphs: list) -> str:
    return title.strip() + "\n\n" + "\n\n".join(p.strip() for p in paragraphs) + "\n"


def now_iso() -> str:
    return y0.now_iso()
