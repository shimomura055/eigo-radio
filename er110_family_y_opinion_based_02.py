# -*- coding: utf-8 -*-
"""er110_family_y_opinion_based_02.py
FAMILY-Y-VOICES-DESIGN-01 委任_20 Phase 1: 『実在意見ベースの3 Voice生成』改善Trial(R0改善版)のDEV/Trial専用module。

位置づけ(重要):
  - **未配線のDEV/Trial module**。どのProduction runner・既存er110 moduleからもimportされない(testでGrep固定)。
    import時にAPI呼出0・ファイル副作用0・client生成0・既存moduleのglobal書換0(patchは `patched_ob()` のwith内だけ)。
    環境変数・flag・CLI引数でProduction挙動が変わる経路はない。
  - er110_family_y_opinion_based_01.py(run_01の再現性のため)と、既存er110 moduleは**無変更**。本fileは 01 の runner・出典照合・予算の歯止めを
    呼出で再利用し、(1)新しいPersona Sheet(SHEETS_02) (2)改訂Voice Prompt(人物像を先に確立→一人称の語り→自然な展開) (3)テーマ定義を入れたWorld frame
    (4)同一主張の反復検出(記録専用) だけを差し替える。差し替えは `patched_ob()` のwith内だけで、抜けると元に戻る。
  - **有料runは予算承認ファイルが無い限り起動しない**: `er110_output/family_y_opinion_based_02/BUDGET_APPROVED.json` ({"cap_jpy": <数値>}) が
    存在する場合のみ main() がAPIを呼ぶ。承認が無い場合は起動しない(API 0)。委任_21ではFableの委任文(ユーザー決定2026-10-24 日次一元管理)を根拠に作成(approved_by記載)。起動はrun_02a/run_02bの各1回(引数はrun名のみ)。
  - 新しい合格基準・閾値は作らない。反復検出は記録専用(合否に使わない)。出典照合・UNMAPPED再生成・予算の歯止めは 01 のまま。
"""
from __future__ import annotations

import contextlib
import copy
import json
import os
import re
import sys
import traceback

import er053_family_x_factlock_ja_writer_01 as w1
import er110_family_y_text_trial_01 as y0
import er110_family_y_persona_pipeline_01 as pl
import er110_family_y_opinion_based_01 as ob

MANAGEMENT_ID = ob.MANAGEMENT_ID
RUN_DIRS_02 = {"run_02a": "er110_output/family_y_opinion_based_02/sns_age_limit/run_02a", "run_02b": "er110_output/family_y_opinion_based_02/sns_age_limit/run_02b",
               "run_03": "er110_output/family_y_opinion_based_02/sns_age_limit/run_03"}
RUN_DIR_02 = RUN_DIRS_02["run_02a"]     # 後方互換(testのmonkeypatch用)。main(run_name)が RUN_DIRS_02 から選ぶ
LEDGER_DIR_02 = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_01"
APPROVAL_FILE = "er110_output/family_y_opinion_based_02/BUDGET_APPROVED.json"
LEDGER_MD_02 = "docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_01/BUDGET_LOG_OB_02.md"
REPEAT_OVERLAP_THRESHOLD = 0.30        # 記録専用。run_01の目視評価(One/Thirdで反復あり)に合わせた1サンプル較正。合否に使わない
SLOTS = ob.SLOTS

# ============================================================
# World frame(テーマ定義を反映。THEME_DEFINITION_01.md と一致させる。数字・制度の事実は入れない)
# ============================================================
WORLD_FRAME_02 = copy.deepcopy(ob.WORLD_FRAME)
WORLD_FRAME_02["shared_premise_ja"] = ("日本の話。SNSには、動画やメッセージのやり取りができるアプリも含める。話題の中心は、子どものSNS利用に、年齢による制限や禁止を設けるべきか、という点。"
                                       "親が子の投稿を見張ることそのものの是非は中心の話題にしない(制限に賛成・反対する理由として少しふれるのはよい)。")
WORLD_FRAME_02["distinctions"] = ob.WORLD_FRAME["distinctions"] + [
    {"term_ja": "段階的な制限", "definition_ja": "子どもの成長や年齢に合わせて、使える機能や範囲を少しずつ広げていくこと。"},
]


def _it(i, kind, sources, text):
    return ob._it(i, kind, sources, text)


# ============================================================
# Persona Sheet 02(PERSONAS_04.md の機械可読版。委任_21でOpus OF-Y7-01〜05を反映)。V1は01を継承(TBS-07由来はONE_dとcontradictionの2か所のみ)。V2は自由重視・年齢による全面禁止に反対。
# V3は『中学生の保護者』本人の声(MR 6件、すべて属性ラベル=中学生の保護者)。声は男性(V2と別人として聞き分けるため。出典に性別なし)。
# ============================================================
def _v1():
    """V1(小さい子の親)。委任_21 OF-Y7-01/02: TBS-07由来の内容はONE_dとcontradiction_or_weakness_jaの2か所だけ。ONE_e(MR-T015-10)削除。『自分も例外ではない』『安心』を外す。"""
    s = copy.deepcopy(ob.SHEETS["voice_1"])
    s["experiences"] = [x for x in s["experiences"] if x["id"] != "ONE_e"]            # OF-Y7-02: 大人を含めた制限の主張であり、子どもの年齢制限の理由に使うと意味が逆向きになる
    for x in s["experiences"]:
        if x["id"] == "ONE_d":
            x["text_ja"] = ("長い移動の時など、静かにしてほしい時に、子どもが見てくれていると正直助かる。制限がかかると、親もしんどくなる時がある。"
                            "(この項目は出典が一件だけ。語りでは一文だけで触れ、言い直しを重ねない)")
    s["persona_sketch_ja"] = "小さい子どもを見守る親。子が刺激の強いものを選んでしまうのを見て、守りたい気持ちが強い。見守りの設定が面倒で、もっと簡単だといいとも思っている。"
    s["stake_ja"] = "子どもの安全。子は危険を危険と気づけず、助けも求められないかもしれないこと。"
    s["troubles_ja"] = "見守り機能の設定が分かりにくい。時間制限を決めても、子どもがやめられず、終わったあとにイライラする。"
    s["wishes_honest_ja"] = "年齢に応じた、はっきりした決まりがほしい。見守りの設定は、もっと簡単であってほしい。"
    s["emotion_habit_ja"] = "事実を短く置いて、言い切らずに言い直す。"
    s["interests_ja"] = "見守りの設定や、子がどうしても使いたいという時の対応が簡単であってほしい。"
    s["contradiction_or_weakness_ja"] = "制限を望む一方で、静かにしてほしい時には自分も画面に助けられている(ONE_dの一文だけ。語りでは1か所、解消しない)。"
    s["speech_style"] = dict(s["speech_style"], assertion_or_hedging_ja="言い切りと言い淀みが半々")
    s["arc_ja"] = ("守る立場の親(冒頭は出来事の描写から)→刺激の強いものや課金を子が選んだ経験、時間制限でもやめられない様子、見守り設定の面倒→年齢に応じた決まりを望む気持ち→"
                   "「矛盾・弱さ」欄の葛藤(1か所・一文だけ。解消しない)→**結びは葛藤を抱えたまま、決めきれない気持ちのまま終える(『〜してほしい』と言い切って結ばない。冒頭の主張の言い直しにしない)**")
    s["claim_core_ja"] = "子には、年齢に応じたはっきりした決まりがほしい。子は危険に気づけず、助けも求められないかもしれないから。ただ、自分の中には割り切れない気持ちも残っている。"
    return s


def _v2():
    """V2(高校生)。OF-Y7-03: wishes_publicを出典のある言い方へ(MR-T041-03除外済み)。OF-Y7-04: 葛藤を『自分で判断したい↔本当に危ない時は大人に頼りたい』へ。監視は任意の理由1か所。"""
    return {
        "gender": "男性", "age_label": "高校生(学年・年齢は明示しない)",
        "role_ja": "高校生",
        "daily_life_ja": "友達との連絡にSNSを使う年代の高校生(出来事は経験欄にあるものだけ)",
        "contact_point_ja": "年齢による制限や禁止の対象になる側",
        "persona_sketch_ja": "友達との連絡にSNSを使う高校生。年齢で一律に縛られるのは困る。自分で判断して使う余地がほしい。ただ、本当に危ない時には大人に頼りたいとも思っている。",
        "stake_ja": "友達との連絡や、模試などの登録ができなくなること。自分で考えて使う余地を取り上げられること。",
        "arc_ja": "高校生としての立場(冒頭は本音から)→連絡や登録に困るという実際の困りごと→自分で判断したいという気持ち→本当に危ない時は大人に頼りたいという葛藤(1か所だけ。解消しない)→**結びはやり方への具体的な注文**",
        "experiences": [
            _it("TWO_a", "O", ["MR-T101-02"], "今は子ども同士がSNSのアカウントで連絡を取ることが多いので、年齢で制限をかけることには反対。別の対策として、安全フィルターをかけるなどがいいと思う。"),
            _it("TWO_b", "O", ["MR-T005-06"], "SNSを禁止するような極端な制限は控えたほうがいい。制限だけを一方的にするのではなく、未成年への講習や呼びかけももっと活発にするべきだと思う。"),
            _it("TWO_c", "O", ["MR-T082-02"], "保護者はあくまで保護者で、子どもの人生は子ども本人のもの。中学生くらいから(人によってはもっと前から)は、自分で判断することが、これから生きる上で必要だと思う。"),
            _it("TWO_d", "O", ["MR-T019-03"], "あれもダメこれもダメと制限されると、我慢するばかりで発散する場がなく、制限が外れた時に、今まで我慢していたものが一気に出てしまう。"),
            _it("TWO_e", "E", ["MR-T017-04"], "高校生でアカウントを作れないと、模試などの登録の時に困る。"),
            _it("TWO_f", "O", ["MR-T010-02"], "悪口や脅しに遭った時に、すぐ大人につなげることは欠かせないと思う。難しいが、微調整が必要だと思っている。"
                                         "(任意・語るなら理由として一か所だけ短く: 親に投稿まで見られる前提だと、SNSの良さが消える気がして少し嫌。ここは主題にしない)"),
            _it("TWO_g", "O", ["MR-T033-02"], "利用する側のことを考えないルールでは、抜け道を探されて、作った意味がなくなる。"),
        ],
        "troubles_ja": "年齢でアカウントを持てなくなると、友達との連絡や、模試などの登録に困る。",
        "wishes_honest_ja": "自分で判断して使う余地がほしい。縛られすぎたくない。ただ、本当に危ない時には、大人に頼れるようにしておきたい。",
        "wishes_public_ja": "極端に禁止するのでなく、安全フィルターや講習など、別の対策があっていい。",
        "emotion_habit_ja": "嫌だと思う気持ちを口にしながら、言いながら考えて、自分で留保を足す。",
        "values_ja": "自分で判断する余地があること。ただし、本当に危ない時には大人に頼れること。",
        "interests_ja": "友達と連絡が取れること。模試などの登録ができること。極端に禁止されないこと。",
        "contradiction_or_weakness_ja": "自分で判断して使いたいのに、本当に危ない時には大人に頼りたい(語りでは1か所だけ。解消しない)。",
        "speech_style": {
            "first_person": "僕",
            "sentence_length_pattern_ja": "言いながら迷いを重ねる長い一文が1つあり、ほかは短く言い直す(実在の声の、逆接をつないで迷いを言葉にする長い一文を言い換えたもの)",
            "question_back_frequency_ja": "ほとんどしない",
            "assertion_or_hedging_ja": "留保が多い。禁止への反対は言い切り、最後は、やり方を変えてほしい、という具体的な注文で収める",
            "vocabulary_layer_ja": "高校生の普通の話し言葉",
        },
        "entry_mood_ja": "年齢で一律に縛られるのは困る、という本音をそのまま口にするところから入る",
        "opening_type": "感情・本音の吐露から",
        "identity_cue_ja": "高校生であることを、年代や学校への軽い言及で自然に出す(新しい場面・親との会話は足さない)",
        "claim_core_ja": "年齢で一律に禁止されるのは困る。友達との連絡や登録にも関わるし、自分で判断する余地がほしい。ただ、本当に危ない時に大人に頼れる道は残してほしい。",
        "known_fact_id": "", "known_fact_usage_ja": "",
    }


def _v3():
    """V3(中学生の保護者)。OF-Y7-01: 『全部禁止も全部解禁も違う』はvalues 1か所のみ(補った整理)。OF-Y7-05: 結びはたとえか心配の像、仮定と『うちの子』(細部なし)で語る。声=男性(推奨)。"""
    return {
        "gender": "男性", "age_label": "中学生の子どもを育てている親(年齢は明示しない)",
        "role_ja": "中学生の子どもを育てている親",
        "daily_life_ja": "中学生の子どもを育てながら暮らしている(出来事は経験欄にない。意見と気がかりで語る)",
        "contact_point_ja": "子どもに、いつ・どこまでSNSを使わせるかを、親として判断する立場",
        "persona_sketch_ja": "中学生の子を持つ親。子の成長に合わせて、使える範囲を少しずつ広げていきたいと考えている。",
        "stake_ja": "子どもに、いつ・どこまで許すかを、親として決めなければならないこと。準備のないまま、急にSNSに触れさせてしまうこと。",
        "arc_ja": ("判断する側の親(冒頭は立場の描写から)→子の成長に合わせて広げるという考え(年齢は大凡の目安、できれば力に合わせて)→準備なしに急に触れる心配→"
                   "**結びは、泳ぐ練習のたとえか、心配の像(例: 準備なしに放り出された子)で終える(『〜してほしい』の望みで結ばない。冒頭の言い直しにしない)**。"
                   "**出来事は足さない。『もし〜なら』の仮定と、仮定の中での『うちの子』(名前・年齢・出来事・会話の細部なし)だけで具体性を出す**"),
        "experiences": [
            _it("THREE_a", "O", ["MR-T032-03"], "子どもは成長の段階によって、自分で判断できる範囲が大きく変わる。大凡のものでしかないが、年齢に応じて、理解できる物事や、身を守れる行動範囲を変えるべきだ。"),
            _it("THREE_b", "O", ["MR-T003-03"], "年齢で区切るというより、できれば、その子の力に合わせて、ステップアップできるような機能がほしい。"),
            _it("THREE_c", "O", ["MR-T008-12"], "SNSにもよるが、いくつかの段階に分けて区別する必要がある気がする。(元の本文は年齢の数字で三つの段階に区切っている。数字は語りに出さない)"),
            _it("THREE_d", "O", ["MR-T005-11"], "禁止されていた年齢を過ぎて、急にSNSに触れた時、何の準備もしていなかったら、事故につながる。海に出る前に、泳ぐ練習をするべきだ。"),
            _it("THREE_e", "O", ["MR-T027-05"], "高校生になれば、一定の判断ができる年齢と考えられる。"),
            _it("THREE_f", "O", ["MR-T174-01"], "子どもは、ペアレンタルコントロールを突破するという前提で、ルールを作ってほしい。(元の本文の後半の一文だけ。前半の罰則の話は使わない)"),
        ],
        "troubles_ja": "禁止が外れる日を境に、準備のないまま急にSNSに触れるのが心配。年齢だけでは子どもの力は測れないし、子どもは親の制限を突破するものだ、という前提で考えておく必要もあると思っている。",
        "wishes_honest_ja": "子の力に合わせて、少しずつ使える範囲が広がる形がいい。",
        "wishes_public_ja": "年齢や成長に応じて、段階を分けた制限があってほしい。",
        "emotion_habit_ja": "落ち着いて、考えながら話す。決めきれない所は、気がする、大凡、できれば、と留保を添える。親としての心配がにじむ。",
        "values_ja": "(補った整理・出典本文にない言い方)全部禁止でも全部解禁でもなく、子の成長に合わせて少しずつ広げること。準備のないまま急に放り出されないこと。",
        "interests_ja": "子が準備なしに放り出されないこと。機能や使える範囲が、段階で広がること。",
        "contradiction_or_weakness_ja": "なし(迷いを告白する人ではない。年齢は大凡の目安、という留保は出典にあるので語ってよいが、自己ツッコミや例外は足さない)",
        "speech_style": {
            "first_person": "わたし",
            "sentence_length_pattern_ja": "中くらいの長さの文を、考えを一つずつ置くように並べる。途中で一度、たとえ話を入れる(実在の声の、たとえで準備の大切さを言う運びを言い換えたもの)",
            "question_back_frequency_ja": "しない",
            "assertion_or_hedging_ja": "気がする、大凡、できれば、で留保しつつ、段階を分けることは言い切る",
            "vocabulary_layer_ja": "子育て中の親の普通の話し言葉。くだけすぎず、硬くもない",
        },
        "entry_mood_ja": "自分が、子どもにいつ・どこまで使わせるかを判断する側の親だ、という立場を短く置くところから入る",
        "opening_type": "自分の状況・立場の描写から",
        "identity_cue_ja": "中学生の子どもを育てている親であることを、判断する立場として自然に出す。『うちの子』は、もし〜ならという仮定の中でだけ使ってよい(子の名前・年齢の細部・実際の出来事・会話は足さない)",
        "claim_core_ja": "子の成長や力に合わせて、使える範囲を少しずつ広げてほしい。年齢はあくまで目安で、準備のないまま急に触れるのが心配。",
        "known_fact_id": "", "known_fact_usage_ja": "",
    }


SHEETS_02 = {"voice_1": _v1(), "voice_2": _v2(), "voice_3": _v3()}
# 委任_22(run_03): 世界設定の用語定義は、その人物の経験欄・主張に対応する用語だけを渡す(定義の内容がV1の意見として混入するのを防ぐ。Sheetのデータであり、コードに人物名の分岐はない)
SHEETS_02["voice_1"]["relevant_terms"] = ["年齢による制限"]
SHEETS_02["voice_2"]["relevant_terms"] = ["年齢による制限", "利用禁止"]
SHEETS_02["voice_3"]["relevant_terms"] = ["年齢による制限", "段階的な制限"]

for _s in SHEETS_02.values():
    for _x in _s["experiences"]:
        _x["tbs_only"] = bool(_x["source_ids"]) and all(i.startswith("TBS") for i in _x["source_ids"])

WHO_JA_02 = {"voice_1": "小さい子どもを育てている親", "voice_2": "高校生", "voice_3": "中学生の子どもを育てている親"}

OPENING_GUIDE_02 = dict(ob.OPENING_GUIDE)
OPENING_GUIDE_02["自分の状況・立場の描写から"] = "語り出しは、自分がどんな立場の人で、この争点で何を判断する側(される側)にいるかを、短く置くことから始める(新しい場面・出来事・会話は足さない)。他の誰かの言い分を打ち消す言い方で始めない。"

# ============================================================
# Voice Prompt 02: ob.VOICE_PROMPT_OB を複製して (1)語る前の考え方(人物→主張の順・一般論を避ける・自然な展開) を挿入し (2)規則3の順序指定の一文を差し替える。
#   規則4(出典ルール)・7・9・10・11、約260〜300字、常体、自己紹介禁止、構造タグ・記号QAは 01 のまま(捏造禁止・出典ID制約・話法指示は維持)。Production(X/Z)のPromptではない。
# ============================================================
THINK_BLOCK = """【語る前の考え方(出力には書かない)】
A. 先に「人物像」を確かめる。この人の立場・日々の関わり→切実なこと→経験→感情→価値観の順に思い浮かべ、その人から主張が出てくる形にする。先に主張があって、人物を当てはめるのではない。聞き手が「この人だから、こう考えるのだな」と感じられることを目指す。
B. 一般論を並べない。制度や社会全体の説明、「〜するべきだ」の列挙は避け、この人の暮らしの言い方(自分はどうしてほしいか、どう困るか、何が気がかりか)にする。「べき」は、この人の立場からの望みとして言う。
C. 展開は「立場 → 経験・気持ち → 葛藤(「矛盾・弱さ」がある人だけ) → 結び」の自然な流れにする。同じ主張・同じ葛藤・同じ結論を、言い回しだけ変えて繰り返さない。回数で数えるのではなく、各文が直前までの文に、新しい事実・気持ち・向きのどれかを足しているかで判断する。冒頭で言ったことを結びで言い直さず、結びは冒頭より先へ進んだ一言にする。葛藤は無理に解消せず、抱えたまま終えてよい。同じたとえや言い回しは、一度使ったら語りの中で繰り返さない。
D. 【区別の定義】は、用語の意味を取り違えないための前提であり、語る中身ではない。定義にある内容(たとえば段階的に広げる形、禁止と制限の区別)を、経験・意見の欄に根拠のない、この人自身の考えとして述べない。この人の考えは、人物の欄の経験・意見・本音・芯にあるものだけで語る。

"""
_RULE3_OLD = "語りの順序や結び方は決めず、この人の話し方から自然に決める。"
_RULE3_NEW = "細かな順序や結びの言葉は、この人の話し方から自然に決める(ただし上の考え方Cの流れは守る)。"


def _must_replace(src: str, old: str, new: str) -> str:
    if old not in src:
        raise ValueError(f"PROMPT_BASE_CHANGED: {old[:20]}")
    return src.replace(old, new, 1)


def build_prompt_template_02() -> str:
    t = _must_replace(ob.VOICE_PROMPT_OB, "【語りの作り方(厳守)】", THINK_BLOCK + "【語りの作り方(厳守)】")
    return _must_replace(t, _RULE3_OLD, _RULE3_NEW)


VOICE_PROMPT_OB2 = build_prompt_template_02()


def render_persona_ob2(sheet: dict, who_ja: str) -> str:
    """人物像を先に置き、主張の芯を最後に置く(人物→主張の順)。経験欄はID・種別つき(出典IDは書かない)。ob.render_persona_ob と同じ未成年対応(成人/歳を出さない)。"""
    ss = sheet["speech_style"]
    ex = "\n".join(f"  - [{x['id']}] ({'出来事を含む声' if x['kind'] == 'E' else '意見の声'}) {x['text_ja']}" for x in sheet["experiences"])
    return (f"人物: {who_ja}(声は{sheet['gender']}の{sheet['age_label']}。一人称は「{ss['first_person']}」)\n"
            f"人物像(最初にここを踏まえる): {sheet['persona_sketch_ja']}\n役割・生活: {sheet['role_ja']}。{sheet['daily_life_ja']}\n"
            f"この争点との接点: {sheet['contact_point_ja']}\nこの人にとって切実なこと: {sheet['stake_ja']}\n困りごと: {sheet['troubles_ja']}\n"
            f"感情の癖: {sheet['emotion_habit_ja']}\n大切にしていること: {sheet['values_ja']}\n"
            f"経験・意見(ここにある内容だけを材料にする):\n{ex}\n"
            f"本音: {sheet['wishes_honest_ja']} / 建前: {sheet['wishes_public_ja']}\n利害: {sheet['interests_ja']}\n矛盾・弱さ: {sheet['contradiction_or_weakness_ja']}\n"
            f"話し方(英語にしても残る型):\n  - 文の長さ: {ss['sentence_length_pattern_ja']}\n  - 問い返し: {ss['question_back_frequency_ja']}\n  - 断言/留保: {ss['assertion_or_hedging_ja']}\n"
            f"  - 語彙の層: {ss['vocabulary_layer_ja']}\n語り出しの気分: {sheet['entry_mood_ja']}\n語りの流れ(目安。そのまま読み上げない): {sheet['arc_ja']}\n"
            f"この人が言いたいことの芯(方向性。そのまま読み上げず、本人の言葉で): {sheet['claim_core_ja']}")


# ============================================================
# 同一主張の反復検出(記録専用。合否に使わない)。文ごとに助詞等を除いた2文字連続の集合を作り、短い方に対する重なり率で近さを見る簡易判定。
# ============================================================
_STRIP_RE = re.compile(r"[、。？！\s]")
_FUNC_CHARS = set("はがをにのでともやてたしだねよかなへ")
CONTRAST_RE = re.compile(r"(でも|けど|けれど|ただ|それでも|いや、|とはいえ|かといって|だからって)")


def _norm(s: str) -> str:
    return "".join(c for c in _STRIP_RE.sub("", s) if c not in _FUNC_CHARS)


def _bigrams(s: str) -> set:
    return {s[i:i + 2] for i in range(len(s) - 1)}


def repetition_report(text: str, threshold: float = REPEAT_OVERLAP_THRESHOLD) -> dict:
    sents = ob.split_sentences(text)
    grams = [_bigrams(_norm(s)) for s in sents]
    pairs = []
    for i in range(len(sents)):
        for j in range(i + 1, len(sents)):
            a, b = grams[i], grams[j]
            if len(a) < 4 or len(b) < 4:        # 短すぎる文(相づち等)は比較しない
                continue
            ov = len(a & b) / min(len(a), len(b))
            if ov >= threshold:
                pairs.append({"i": i, "j": j, "overlap": round(ov, 2), "a": sents[i], "b": sents[j]})
    return {"note": "記録専用。合否に使わない。1サンプルで較正した簡易判定(目視確認なしに結論に使わない)", "threshold": threshold, "n_sentences": len(sents),
            "n_repeat_pairs": len(pairs), "repeat_pairs": pairs, "contrast_turns": len(CONTRAST_RE.findall(text)),
            "last_vs_first_echo": bool(grams and len(grams[0]) >= 4 and len(grams[-1]) >= 4 and len(grams[0] & grams[-1]) / min(len(grams[0]), len(grams[-1])) >= threshold)}


# ============================================================
# 01 の runner を、02 の Sheet/Prompt/render/予算で動かす(with内だけ差し替え)
# ============================================================
_ORIG_BUILD = ob.build_voice_prompt_ob


def build_voice_prompt_02(wf: dict, slot: str, emphasize: bool = False) -> str:
    """区別の定義を、Sheetの relevant_terms にある用語だけに絞って 01 のbuilderへ渡す(relevant_terms未指定のSheetは全件のまま)。"""
    terms = SHEETS_02[slot].get("relevant_terms")
    wf2 = copy.deepcopy(wf)
    if terms is not None:
        wf2["distinctions"] = [d for d in wf2.get("distinctions", []) if d["term_ja"] in terms]
    return _ORIG_BUILD(wf2, slot, emphasize)


_PATCH_KEYS = ("SHEETS", "VOICE_PROMPT_OB", "render_persona_ob", "WHO_JA", "OPENING_GUIDE", "BUDGET_STOP_JPY", "LEDGER_MD", "build_voice_prompt_ob")


@contextlib.contextmanager
def patched_ob(cap_jpy: float):
    saved = {k: getattr(ob, k) for k in _PATCH_KEYS}
    try:
        ob.SHEETS, ob.VOICE_PROMPT_OB, ob.render_persona_ob = SHEETS_02, VOICE_PROMPT_OB2, render_persona_ob2
        ob.build_voice_prompt_ob = build_voice_prompt_02
        ob.WHO_JA, ob.OPENING_GUIDE, ob.BUDGET_STOP_JPY, ob.LEDGER_MD = WHO_JA_02, OPENING_GUIDE_02, float(cap_jpy), LEDGER_MD_02
        yield
    finally:
        for k, v in saved.items():
            setattr(ob, k, v)


def run_pipeline_02(client, rd: str, *, cap_jpy: float, ledger_md: str = LEDGER_MD_02) -> dict:
    with patched_ob(cap_jpy):
        st = ob.run_pipeline(client, rd, wf=WORLD_FRAME_02, ledger_md=ledger_md)
    reps = {s: repetition_report(st["final_texts"][s]) for s in SLOTS}
    st["repetition_02"] = reps
    w1.wj(os.path.join(rd, "repetition_report_02.json"), reps)
    w1.wj(os.path.join(rd, "state.json"), st)
    return st


def read_cap(path: str = None):
    """予算承認ファイルから「1runあたりの上限」(cap_jpy / runs)を読む。無い・不正なら None(= 有料runを起動しない)。runs省略時は1。"""
    try:
        d = json.load(open(path or APPROVAL_FILE, encoding="utf-8"))
        v = float(d["cap_jpy"]) / max(1, int(d.get("runs", 1)))
        return v if v > 0 else None
    except Exception:  # noqa: BLE001
        return None


def main(run_name=None, paid: bool = False) -> int:
    """run_name は RUN_DIRS_02 のキー(run_02a / run_02b / run_03)のみ。有料runは paid=True(CLI `--paid`)かつ予算承認ファイルがある場合のみ(委任_22 起動ガード)。生成設定は同一で、run先と費用台帳だけが別(APIにseed指定はなく、差はサンプリングのばらつき)。"""
    if run_name not in RUN_DIRS_02:
        print(f"[OB2] run名が不正(run_02a / run_02b のいずれかを引数に指定): {run_name!r}", flush=True)
        return 7
    rd = RUN_DIRS_02[run_name]
    ledger_md = f"{LEDGER_DIR_02}/BUDGET_LOG_OB_03.md" if run_name == "run_03" else f"{LEDGER_DIR_02}/BUDGET_LOG_OB_{run_name}.md"
    if os.path.exists(os.path.join(rd, "entry_point.json")):
        print(f"[OB2] already launched: {rd}/entry_point.json exists (再起動不可)", flush=True)
        return 5
    if not paid:
        print("[OB2] 有料runには CLI明示flag `--paid` が必要(委任_22の起動ガード)。flagが無いため起動しない(API 0)", flush=True)
        return 8
    cap = read_cap()
    if cap is None:
        print(f"[OB2] 予算承認ファイル({APPROVAL_FILE})が無い/不正のため、有料runを起動しない(API 0)", flush=True)
        return 6
    os.makedirs(rd, exist_ok=True)
    import er005_cost_logger as cl
    import er003_v1_en_direct_vfl_01_generate as vfl01
    cl.install(os.path.join(rd, "raw_usage_log.jsonl"))
    w1.wj(os.path.join(rd, "entry_point.json"), {"runner": "er110_family_y_opinion_based_02.py", "management_id": MANAGEMENT_ID, "run_name": run_name, "run_dir": rd, "started": pl.now_iso(),
                                                 "writer_model": ob.MODEL_TOP, "judge_model": ob.MODEL_CHEAP, "budget_stop_jpy_per_run": cap, "flags": "なし(予算承認ファイルの金額のみ。引数はrun名のみ)"})
    try:
        client = vfl01.get_client()
        st = run_pipeline_02(client, rd, cap_jpy=cap, ledger_md=ledger_md)
        w1.wj(os.path.join(rd, "run_status.json"), {"status": "DONE", "gate_status": st.get("gate_status"), "final_cost_jpy": st.get("final_cost_jpy")})
        print("[OB2] DONE", flush=True)
        return 0
    except (pl.PipelineStop, y0.YStop) as e:
        code = getattr(e, "code", type(e).__name__)
        with patched_ob(cap):
            ob.write_partial(rd)
        w1.wj(os.path.join(rd, "run_status.json"), {"status": "STOP", "code": code, "message": str(e)})
        print(f"[OB2] STOP {code}: {e}", flush=True)
        return 4
    except Exception as e:  # noqa: BLE001
        w1.wj(os.path.join(rd, "run_status.json"), {"status": "ERROR", "error": repr(e), "trace": traceback.format_exc()})
        print(f"[OB2] ERROR {e!r}", flush=True)
        return 4


if __name__ == "__main__":
    _args = sys.argv[1:]
    _paid = "--paid" in _args
    _pos = [a for a in _args if a != "--paid"]
    sys.exit(main(_pos[0] if len(_pos) == 1 else None, paid=_paid))
