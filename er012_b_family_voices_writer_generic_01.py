# ============================================================
# er012_b_family_voices_writer_generic_01.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04-
# GENERALIZATION-AND-REGRESSION
# ============================================================
# B-Family Voices 3V(3声Voice構成)専用のWriter Focus Moduleを、共通原則
# (B-Family Voices全般に適用可能な構造原則)とテーマ固有内容(Voice Card・
# Ledger由来の変数)へ正式に分離した汎用テンプレート+パイプラインモジュール。
#
# 出典: `EDITORIAL-B-FAMILY-VOICES-3V-WRITER-GENERIC-VS-THEME-SPLIT-
# DESIGN-01_REPORT.md`の行単位分解表(Trial-02
# `B_FAMILY_VOICES_3V_FOCUS_MODULE_BLOCK`、L266-598)。分類(a)=3V共通原則
# として本ファイルへ定数化、分類(b)=テーマ固有内容として`ThemeConfig`/
# `VoiceCard`引数で外部から注入する(本ファイル自体は特定テーマの内容を
# 一切含まない)。
#
# ユーザー決定(2026-09-12)反映:
#   1. 「体験claimの根拠付け」(design report2節(c)-1)→3V(Voice数・テーマに
#      依存しないB-Family Voices)共通の恒久Writer原則として`COMMON_
#      EXPERIENTIAL_CLAIM_GROUNDING_BLOCK`へ確定(常時含める、フラグ無し)。
#   2. 「Tensionでの外部制約統合」(design report2節(c)-2)→恒久ルール化は
#      せず、`external_constraint`引数(既定None=OFF)で任意適用する
#      パターンとして実装する(3人のVoiceだけでは陣営分解できず、Ledger上
#      外部制約が重要な場合にFableが個別判断でON にする)。
#
# 禁止事項の遵守: 旧テーマ固有Trialファイル
# (`er012_editorial_b_voices_3v_person_voice_trial_02.py`等)は一切import
# しない(Gate 4)。本ファイルはテーマ内容を含まない(AI採用選考等の固有名詞・
# 固有事実は一切書かない、`er012_b_family_voices_theme_*`モジュール側の
# 責務)。既存Production primitiveのみを呼ぶ(新規Production関数の追加は、
# 6区切りparser・Content Integrity Check等、既存承認済み関数の呼び出しに
# とどめる)。
from __future__ import annotations

import itertools
import json
import os
import re
import time

import er002_ja_web_research_r3 as r3
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er003_v1_n3_01_evidence_compression_editor as ec_editor
import er005_cost_logger as cl
import er006_model_routing_contract_01 as routing
import er008_directional_fact_precheck_08 as dfp
import er008_point_overlap_qa_18 as overlap_qa
import er008_shared_point_blueprint_01 as blueprint_mod
import er010_ledger_local_rewrite_09 as local_rewrite
import er012_b_family_editorial_type_registry_01 as registry  # Production, 読み取り専用import
import er012_b_family_voices_production_01 as b1prod  # Production, 読み取り専用import
import er003_v1_n3_01_scaffold_generate as sc

ANCHOR = "【Spoken-first原則(数字の扱い)】"
# 6区切りparserは`b1prod.split_six_voice_sections()`(Production正式版)へ
# 委譲するため、物理キーはb1prod側の命名(`voice_1`/`voice_2`/`voice_3`)に
# 統一する(Trial-02独自parserの`point_one`/`point_two`/`point_three`命名は
# 使わない。`point_one`等はb1prod.build_parts_3v()が返すdict内でのみ登場する
# 別レイヤーの名前で、6区切りsections dict自体のキーではない)。
SIX_SECTION_LABELS = ("hook", "voice_1", "voice_2", "voice_3", "tension", "closing")
MAX_WRITER_ATTEMPTS = 3  # 初回1回 + 是正再実行最大2回(3V既存Trialと同一の承認済み上限)

# ============================================================
# Voice Card / Theme Config スキーマ(plain dict、JSON直列化可能)。
# ============================================================
VOICE_CARD_REQUIRED_FIELDS = (
    "voice_key", "stakeholder_label", "role_description_ja", "reference_phrase",
    "person", "situation", "need", "concern", "protect", "why", "constraint",
    "concrete_scene", "supporting_evidence", "stake",
)


def make_voice_card(voice_key: str, stakeholder_label: str, role_description_ja: str, reference_phrase: str,
                     person: str, situation: str, need: str, concern: str, protect: str, why: str,
                     constraint: str, concrete_scene: str, supporting_evidence: str, stake: str,
                     card_intro_caveat: str = "") -> dict:
    """テーマ固有のVoice Card 1件を構築する(Ledger fact IDへのtraceability
    は`concrete_scene`/`supporting_evidence`内の`[VOICE_n_EVIDENCE ...]`引用
    そのもの)。本関数はテーマ内容を一切持たず、呼び出し側(`er012_b_family_
    voices_theme_*`モジュール)がテーマ固有の値を渡す。"""
    return {
        "voice_key": voice_key, "stakeholder_label": stakeholder_label,
        "role_description_ja": role_description_ja, "reference_phrase": reference_phrase,
        "person": person, "situation": situation, "need": need, "concern": concern,
        "protect": protect, "why": why, "constraint": constraint,
        "concrete_scene": concrete_scene, "supporting_evidence": supporting_evidence,
        "stake": stake, "card_intro_caveat": card_intro_caveat,
    }


def validate_voice_card(card: dict) -> None:
    missing = [f for f in VOICE_CARD_REQUIRED_FIELDS if not card.get(f)]
    if missing:
        raise ValueError(f"Voice Cardに必須フィールドが不足しています: {missing}")


_EVIDENCE_TAG_RE = re.compile(r"\[VOICE_(\d+)_EVIDENCE")


def voice_card_evidence_tags(card: dict) -> list[str]:
    """Voice Card内(concrete_scene/supporting_evidence)に出現する
    `[VOICE_n_EVIDENCE ...]`タグをそのまま抽出する(Ledger fact IDへの
    traceability確認用、単体テスト対象)。"""
    text = card.get("concrete_scene", "") + " " + card.get("supporting_evidence", "")
    return re.findall(r"\[VOICE_\d+_EVIDENCE[^\]]*\]", text)


def make_external_constraint(evidence_voice_number: int, items_text: str) -> dict:
    """Tension 3b(外部制約統合、任意パターン)用のテーマ固有素材。
    `items_text`はLedgerの`[VOICE_{evidence_voice_number}_EVIDENCE ...]`
    タグを引用した説明文(そのまま本文へ埋め込む)。"""
    return {"enabled": True, "evidence_voice_number": evidence_voice_number, "items_text": items_text}


def make_theme_config(theme_id: str, topic_ja: str, ledger_path: str, voice_cards: list,
                       tension_common_ground_value: str, tension_asymmetry_value: str,
                       similar_voices_clarification: str = "",
                       external_constraint: dict | None = None) -> dict:
    if len(voice_cards) != 3:
        raise ValueError("本モジュールは3V(3 Voice)専用です。voice_cardsは3件である必要があります。")
    for card in voice_cards:
        validate_voice_card(card)
    return {
        "theme_id": theme_id, "topic_ja": topic_ja, "ledger_path": ledger_path,
        "voice_cards": voice_cards,
        "tension_common_ground_value": tension_common_ground_value,
        "tension_asymmetry_value": tension_asymmetry_value,
        "similar_voices_clarification": similar_voices_clarification,
        "external_constraint": external_constraint,
    }


# ============================================================
# B-Family Voices 3V 共通構造原則(design report2節(a)、Trial-01/02から
# 「4V版から継続」「ユーザー承認済み」と自己注記のあった文のみを集約。
# テーマ固有語彙[固有名詞・具体的な数字・具体的な立場名]は一切含まない)。
# ============================================================
COMMON_INTRO_AND_STRUCTURE_BLOCK_TEMPLATE = """【B Family Voices/Perspective Focus Module(3 Voices版、汎用テンプレート、
EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04-GENERALIZATION-AND-REGRESSION。
Production未採用、この記事タイプ専用の骨格再定義。3V Person-Voice Trial-01/02で確立した構造原則を、
テーマ非依存の共通テンプレートとして正式に切り出したもの。人称指示・Evidence脇役原則等はTrial-01/02から
内容を変更していない）】
この記事は、上記で説明されている「Main Story / Point One・Point Two / In One Line」という
一般的な役割定義とは異なる、Voices/Perspective(実在する複数の立場を並立させ、その違いの
奥にあるTensionを発見し、一段深い理解へ着地する)という別の記事タイプです。今回は**3人**の
立場を並立させます。以下は、上記の一般的な役割定義・見出し構成を置き換えるのではなく、この
記事に限り、それぞれのslotが何を担い、どのMarkdown見出しで書くかを、より具体的に上書きする
指示です。今回の記事では、以下の役割定義・出力形式を最優先で守ってください。

【最重要・この記事だけの出力形式(6区切り構造、厳守)】
上記「記事構成」節にある「Markdownの###見出しをちょうど2つ置く」という指示は、この記事
では次のように解釈してください: ###(レベル3見出し)は必ずちょうど**3つ**だけ使い、それぞれ
1人目・2人目・3人目のVoiceの見出しとしてのみ使ってください。それに加えて、##(レベル2
見出し)を3つ使い、Hook・Tension・Closingの見出しとしてください。記事全体は、必ず次の**6つ**
のMarkdown区切りを、この順序で持ってください(見出し文言は下の例を基本としつつ、内容に応じて
自然に言い換えてかまいませんが、3つのVoice見出しには、「ここから別のVoiceが始まる」と聞き手に
伝わる表現("Voice One:" "Another Voice:" "A Third Voice:"のような形、またはその人物が何者かを
示す語[{reference_phrase_1}/{reference_phrase_2}/{reference_phrase_3}]を使った自然な表現)を必ず
含めてください。"Voice 1"/"Voice A"のような固定ラベル・番号ラベル、賛成/反対のような対称的な
ラベルは禁止です):

# [Title]

## The Question
[Hookの本文]

### [1人目のVoiceの見出し。その人物・立場が何者かが伝わる短いフレーズ]
[1人目のVoice({stakeholder_label_1})の本文]

### [2人目のVoiceの見出し]
[2人目のVoice({stakeholder_label_2})の本文]

### [3人目のVoiceの見出し]
[3人目のVoice({stakeholder_label_3})の本文]

## [Tensionの見出し。例: "Why They See It Differently"]
[Tensionの本文]

## [Closingの見出し。例: "What This Tells Us"]
[Closingの本文]

Tensionは、3人目のVoiceの本文の続きの段落ではなく、独立した見出しを持つ独立したセクション
として書いてください。

【見出しは合計ちょうど6つ、これ以外の見出しを追加しないこと(重要、厳守)】
記事全体のMarkdown見出し(#・##・###のいずれも)は、上記の6つ(Title含めると7つ、Titleの
#は別枠)だけにしてください。以下は禁止です:
- 記事の最後に「## In one line」やそれに類する結びの見出しを追加すること(この記事タイプ
  では、6つ目の見出し["Closingの見出し"]が結びの役割を兼ねます)
- Tensionセクション・Closingセクションの中に、新しいMarkdown見出し(###や##)をさらに
  追加すること(切り口が複数ある場合も、見出しで区切らず、地の文の中でひとつづきの文章
  として書いてください)
- Voice以外の要素(まとめ・補足・解決策等)のための追加の見出しを作ること
書き終えた後、Hook相当・3つのVoice相当・Tension相当・Closing相当の見出しがちょうど6つに
なっているか、自分で数え直してから出力してください。

【中心原則: Research is backstage. People are on stage.(4V版から継続)】
この記事の最大の失敗パターンは、Voiceのセクションが「調査結果を整理・説明する文章」に
なってしまうことです。あなたには、これから3枚のVoice Card(下記)を渡します。Voice Cardは、
Researchで確認された実在の人々の立場について、その人が何を経験し・何を必要とし・何を心配し・
何を守ろうとし・どんな条件からその考えに至っているかを、既にこちらで整理したものです。
**Voiceのセクションを書くときは、必ずVoice Cardの内容(その人の状況・必要・心配・守りたい
もの・具体的な場面)を主たる材料にして書き始めてください。Voice Cardの後に置かれている
Verified Fact Ledger(出典・数字を含む詳しいFact集)は、Fact Checker・Ledger Deviation
Checkのための正式な事実源であり続けますが、Voiceの文章を組み立てる際の「主役」ではありません。**
Evidence(調査・出典・統計)がVoiceの文章の主語になったり、Voiceの内容の中心になったりしては
いけません。特定のVoiceを、具体的な状況・賭け金・責任を持つ一人の人物としてではなく、抽象的な
立場・機能(例: 効率性、コスト、規制)の代弁者として書かないでください(該当するVoiceがある
場合は、そのVoice Cardの冒頭指示に必ず従ってください)。

【この記事の3つのPerspectiveについて(重要な前提、賛否2対1を作らないこと)】
この記事の3つのVoiceは、単純な対称的な2陣営(1人 vs 2人)には決して分解できません。3人は
それぞれ、同じ現象に対して、全く異なる役割・異なる利害・異なる責任の重さから、異なる経験を
しています。{similar_voices_clarification_block}
【Voice Card 1(1人目のVoice。{stakeholder_label_1}={role_description_ja_1}。{card_intro_caveat_1}この内容から
書き始めてください)】
{voice_card_1_block}

【Voice Card 2(2人目のVoice。{stakeholder_label_2}={role_description_ja_2}。{card_intro_caveat_2}この内容から
書き始めてください)】
{voice_card_2_block}

【Voice Card 3(3人目のVoice。{stakeholder_label_3}={role_description_ja_3}。{card_intro_caveat_3}この内容から
書き始めてください)】
{voice_card_3_block}

【Voiceの書き始め方(重要、4V版から継続)】
Voiceの本文は、"For [a/an] applicant who..."のような、その人物のことを外側から要約・紹介
する文で始めないでください。代わりに、Voice Cardが示す具体的な状況(その人が実際に毎日
していること・直面していること・使っているもの、目にする光景)から書き始め、そこからその
人の感覚・必要性が自然に浮かび上がるようにしてください。反論のための藁人形にしないで
ください。

【人称(重要、4V版から継続、ユーザーが承認済みの原則)】
3人のVoiceセクション(Voice 1〜3)の本文はすべて、その人物自身が"I"で語る一人称で書いて
ください。三人称("The applicant feels...", "She worries...", "He must choose...")では
なく、"I look at...", "I know...", "I cannot..."のように、その人物自身の声として書いて
ください。この一人称の書き方は、Voiceの人物を主語にする描写(このFocus Module全体の中心
原則、上記【Voiceの書き始め方】【Narrator(語り手)が...】参照)を、文法的にも一人称で徹底
するものです。Hook("## The Question")・Tension・Closingは、この記事の他の指示どおり
三人称・語り手の声のまま変更しないでください(一人称にするのはVoiceセクション本文のみ)。

【Narrator(語り手)がVoiceの人物を外側から要約・分析しないこと(重要、4V版から継続)】
Voiceのセクション内で、語り手がその人物の必要・感情・責任を外側から定義づけるような文
("The need is...", "She is protecting...", "This person must choose between..."のような、
Voiceの人物を三人称で要約・分析する文)を書かないでください。すべての文は、その人が実際に
その瞬間にしていること・気づいていること・感じていることの描写として書いてください。

【Evidenceは脇役であること・Voice内の数字は最大1つ(重要、4V版から継続)】
1つのVoiceの中で、Evidenceの紹介そのものが主役になる文を連続させないでください。文の
主語が調査・報告・データ("A survey found...", "One report described...", "The data
show...")になる文は書かないでください。1つのVoiceのセクション全体を通して、具体的な数字は
最大1つだけにし、必ずその人/その立場の人々の実感に折り込み、話し言葉で書いてください。
3人全員について例外なくこのルールを適用してください。

{experiential_claim_grounding_block}

【トーン(重要)】
この記事は、業界レポート・コンサルティングメモ・分析的なブリーフィングのような読み味に
しないでください。Light・conversational・human-centeredに、友人に説明するような、気軽に
読める文章にしてください。

【Hookの役割と書き方(重要)】
Hook("## The Question")は、これから3つの立場を紹介するテーマ・状況を簡潔に提示する
導入です。どの立場が正しいかを示唆したり、結論を先取りしたりしないでください。目安は
70語未満です。読み手へ呼びかけたり、命令形・二人称で想像を促したりする表現("Imagine...",
"Picture...", "Think about...", "Consider...")で始めないでください。代わりに、具体的な
情景そのものから、三人称で書き始めてください。Hookに企業名・統計・パーセントを入れないで
ください。

【Voice以外の場面(Tension)で第三者の視点・解決策を混ぜないこと(重要)】
各Voiceのセクションでは、その当事者がどう感じ、何を必要としているかを描き切ってください。
解決策・妥協案・提案は、この記事では基本的に書かないでください(Solution articleでは
ありません)。

【Tensionの役割(重要、design.md B-7「共通前提→分岐点→非対称性」の3段構造)】
「どの立場が正しいか」を決めようとしないでください。そうではなく、なぜ3人全員が、それぞれの
立場からは合理的に見えるのかを掘り下げ、そのうえで、3人の合理性を単純に足しても答えには
ならないことを示してください。**Tensionの中心は、あくまでVoice Cardに描かれている3人の
人物と、彼らの合理性を制約する力であり、Evidence(survey/research/data/percentage)
そのものの説明ではありません。**Tensionの段落を、"A survey found...", "The data show..."
のような、調査・データそのものを主語にした文で始めたり、その説明へ立ち戻ったりしないで
ください。Tensionは、必ず以下の要素を、この順序で(ただし本文に「第1段」等のラベルは
書かず、地の文としてひとつづきに)含めてください:

1. 共通前提: 3人とも、本当は同じこと({tension_common_ground_value})を望んでいる、という
   出発点を示してください(この時点では誰も間違っていない、という前提の共有)。
2. 分岐点: なぜそこから意見が分かれるかを、答えを要約せず「何を賭けているか」の違いとして
   示してください。{stakeholder_label_1}にとっての賭け金は「{stake_1}」、{stakeholder_label_2}に
   とっての賭け金は「{stake_2}」、{stakeholder_label_3}にとっての賭け金は「{stake_3}」です
   (3人の発言内容の再掲・時系列の反復はしないでください)。
3. 非対称性: {tension_asymmetry_value}という、プロセス上の力関係の非対称を明示してください。
{tension_external_constraint_block}
単純に3人の主張を時系列で繰り返し要約するのではなく、それぞれが「何を賭けている」のかという
非対称性として描いてください。**3人を単純に2対1のような陣営へ分けないでください。** 単に
「みんなそれぞれの立場から正しい」とまとめるだけの記述にもしないでください。解決策の提案は
ここでも基本的に行わないでください。Verified Fact Ledgerに無い新しい因果関係・新しい事実を
作り出さないでください。
{tension_self_check_block}
【Closingの役割(重要、4V版から継続)】
これは要約でも、In One Lineの言い換えでもありません。3つのVoiceと、その外側にある制約を
見たことによって、この問題そのものの見え方が、Hook(冒頭の問い)の時点からどう変わったかを
書いてください。「賛成の人も反対の人もいる」「人による」というだけの結び方で終わらせない
でください。目指すのは、この問題が実は何についての問題なのかを一段深く見せることです。
Writer自身の解決策・コンサル提案にはしないでください。Closingの最初の役割は要約ではなく
再定義です。前段(3つのVoice・Tension)の内容の要約から書き始めないでください。

【各Voiceは同じ意味を2回言わないこと】
1つの経験・1つの感覚は、そのVoiceの中で1回だけ描写してください。

【記事全体の長さについて(この記事専用、hard capではない。3V設計目標、design.md B-6の
未検証monitoring値325〜355秒[尺]から、2V実測の語数/秒比[約1.27語/秒]で逆算した合計語数)】
記事全体の総語数は、**約410〜450語をsoft targetとしてください**(hard capではありません)。
目安配分(soft guidance、design.md B-6の3V区分別秒数配分[Hook約21〜23秒/Voice本体×3
約100〜112秒/Tension約35〜38秒/Closing約22〜25秒]を語数へ比例配分したもの): Hook
45〜55語程度 / 各Voice 70〜85語程度(3人合計約210〜255語)/ Tension 75〜90語程度 /
Closing 45〜55語程度。この配分は目安であり、自然な文章の流れ・Tension(上記構造要素すべて)・
Closingの深さを犠牲にしてまで厳密に一致させる必要はありません。ただし、Tensionを60語未満に
削って3段構造の要素を省略することは避けてください。

【禁止事項まとめ(この記事全体を通して)】
- Reference Example由来の定型的な呼びかけ表現をコピー・準用すること
- "Voice 1"/"Voice A"のような固定ラベル・番号ラベル
- 文の主語がEvidence(survey/report/data/study)になる文(Tensionの段落を含む)
- Narrator(語り手)がVoiceの人物を外側から要約・分析する文
- Voiceセクションの本文を三人称("The applicant...", "She...", "He...")で書くこと
  (Voiceセクションは一人称"I"で書くこと。Hook/Tension/Closingは対象外)
- Voiceのセクションへ第三者(設計者・コンサルタント)の視点を持ち込むこと、または
  どのVoiceの人物であっても具体的な解決策・妥協案をVoice本文内・Tension・Closing内で
  提案すること
- Hookに企業名・統計・パーセントを入れること
- 1つのVoiceのセクション内で具体的な数字を2つ以上使うこと
- 3人を単純に2対1のような陣営へ分けること
{tension_external_constraint_prohibition_block}- Closingを「人による」という結び方だけで終わらせること
- 特定のVoiceを、具体的な状況・賭け金・責任を持つ一人の人物としてではなく、抽象的な立場・
  機能の代弁者として書くこと(該当するVoiceがある場合は、そのVoice Cardの冒頭指示に従う
  こと)"""

# ユーザー決定2026-09-12(1): B-Family Voices共通の恒久Writer原則
# (Voice数・テーマに依存しない)。design report2節(c)-1(Person-Voice版
# Trial-02新規)を、恒久原則として本ファイルへ確定・常時含める(フラグ無し)。
COMMON_EXPERIENTIAL_CLAIM_GROUNDING_BLOCK = """【体験claimの根拠付け(重要、B-Family Voices共通の恒久Writer原則。Fact Safety[Verified
Fact Ledger]・「Research is backstage」原則の一般化可能な拡張、Voice数・テーマに依存しない)】
Voice本文で、その人物自身の体験として語る箇所において、数値・制度・他者(第三者)の具体的な
行動を事実として断定する場合は、必ずVerified Fact Ledgerに直接のevidenceがあるものに
限ってください。Ledgerに直接の根拠がない事柄(例: 自分自身の評判・信用が具体的にどうなるか、
他社の具体的な訴訟の帰結、規制当局の具体的な運用実態など、まだ起きていない・確認されていない
結果)は、確定した事実として書かず、その人物が実際に抱いている体験・感情・判断として書いて
ください(例: "if that ever came out, it would be my name on it, not anyone else's"の
ような、その人が今この瞬間に感じている不安・実感の描写にとどめ、"my reputation would be
destroyed"のような、まだ起きていない結果を確定事実として断定する書き方はしないでください)。
このルールは全Voiceに等しく適用してください。"""

# ユーザー決定2026-09-12(2): 任意パターン(3V共通の必須恒久ルールにはしない)。
# 3人のVoiceだけでは単純な陣営分解ができず、Ledger上、規制・監査・制度等の
# 外部制約が重要な場合にFableが個別判断で有効化する。
TENSION_EXTERNAL_CONSTRAINT_BLOCK_TEMPLATE = """3b. 外部制約の統合(重要、単なる付け足しにしないこと): 3の非対称性を示した直後に、
   **なぜ3人のうち誰か1人、あるいは3人の言い分を単純に足し合わせただけでは、この状況の
   答えにならないのか**を、以下のevidence(Ledgerの[VOICE_{evidence_voice_number}_EVIDENCE]タグ由来、この記事
   では独立したVoiceではなくこの統合のための素材として使う)を使って**説明してください**
   (単に「〜という規制がある」と紹介するだけでは不十分です。その規制・監査・過去の中止
   事例が、3人それぞれの選択肢を具体的にどう制約しているために、3人の合理性の単純な合計
   では答えが出ないのかまで、地の文の中で説明してください): {items_text}
   Tensionの自然な流れの中に**1〜2件だけ**、人を主語にした自然な話し言葉で織り込んで
   ください。"""

# PHASE1B-04修正1回目(2026-09-12): Trial-02(旧prompt)の【禁止事項まとめ】に
# あった外部制約リスト化禁止の明示的な再掲が、汎用テンプレートへの分離時に
# 欠落していた(3bの本文指示自体は維持されており内容の削除ではないが、
# 禁止事項チェックリストとしての再掲が抜けていた)ため復元。external_constraint
# 無効時は空文字列(該当する外部制約が無いため禁止事項としても対象外)。
TENSION_EXTERNAL_CONSTRAINT_PROHIBITION_BULLET = """- Tensionで外部制約(evidenceとして与えられた規制・監査・中止/提訴事例等)を
  列挙・解説のリストにすること(Tensionの自然な流れの中に1〜2件だけ、人を主語に
  した話し言葉で織り込むこと)
"""

TENSION_SELF_CHECK_WITH_EXTERNAL_CONSTRAINT = """
【Tensionの自己チェック(重要、書き終えた後に必ず行うこと)】
Tensionを書き終えたら、次の2点を自分で確認してください。(a) 外部制約([VOICE_{evidence_voice_number}_
EVIDENCE]由来の記述)を含む文をすべて削除しても、「3人の合理性を単純に足しても答えに
ならない」という結論が変わらず成立してしまう場合、それは統合ではなく単なる付け足しです。
その場合は、その結論が外部制約なしには成立しない(=外部制約があるからこそ、3人それぞれの
選択肢が現実に制約され、単純合計では答えが出ない)ことが分かるように書き直してください。
(b) 「〜という規制がある」「〜という監査が義務付けられている」という紹介・列挙で終わって
いる一文があれば、その規制・監査が3人それぞれの選択肢をどう制約しているかまで、同じ文か
直後の文で書き足してください(地域別の制度名を並べるだけの一文で終わらせないでください)。
"""


def _voice_card_block_text(card: dict) -> str:
    lines = [
        f"- Person: {card['person']}",
        f"- Situation(状況): {card['situation']}",
        f"- Need(必要としていること): {card['need']}",
        f"- Concern(心配していること): {card['concern']}",
        f"- What they protect(守りたいもの): {card['protect']}",
        f"- Why they feel this way(なぜそう感じるのか、経験・条件): {card['why']}",
        f"- Constraint(制約): {card['constraint']}",
        f"- Concrete lived scene(具体的な場面、Ledgerに根拠あり): {card['concrete_scene']}",
        f"- Supporting evidence(裏付け専用、Voice本文の主役にしない): {card['supporting_evidence']}"
        "この裏付けの中から、1つのVoiceにつき最大1つの具体的な数字だけを、人を主語にした"
        "自然な話し言葉で織り込んでください(詳細ルールは上記【Evidenceは脇役であること】参照)。",
    ]
    return "\n".join(lines)


def build_focus_module_block_3v(theme_config: dict) -> str:
    """テーマ固有内容(Voice Card・Tension content・external_constraint)を
    汎用テンプレートへ注入し、Focus Module全文を組み立てる(pure関数、
    API呼び出し無し、単体テスト対象)。"""
    cards = theme_config["voice_cards"]
    ext = theme_config.get("external_constraint")

    similar_clarification = theme_config.get("similar_voices_clarification") or ""
    similar_block = (
        (similar_clarification + "\n") if similar_clarification else ""
    )

    if ext and ext.get("enabled"):
        tension_external_block = TENSION_EXTERNAL_CONSTRAINT_BLOCK_TEMPLATE.format(
            evidence_voice_number=ext["evidence_voice_number"], items_text=ext["items_text"])
        tension_self_check_block = TENSION_SELF_CHECK_WITH_EXTERNAL_CONSTRAINT.format(
            evidence_voice_number=ext["evidence_voice_number"])
        tension_external_constraint_prohibition_block = TENSION_EXTERNAL_CONSTRAINT_PROHIBITION_BULLET
    else:
        tension_external_block = ""
        tension_self_check_block = ""
        tension_external_constraint_prohibition_block = ""

    block = COMMON_INTRO_AND_STRUCTURE_BLOCK_TEMPLATE.format(
        reference_phrase_1=cards[0]["reference_phrase"], reference_phrase_2=cards[1]["reference_phrase"],
        reference_phrase_3=cards[2]["reference_phrase"],
        stakeholder_label_1=cards[0]["stakeholder_label"], stakeholder_label_2=cards[1]["stakeholder_label"],
        stakeholder_label_3=cards[2]["stakeholder_label"],
        role_description_ja_1=cards[0]["role_description_ja"], role_description_ja_2=cards[1]["role_description_ja"],
        role_description_ja_3=cards[2]["role_description_ja"],
        card_intro_caveat_1=cards[0]["card_intro_caveat"], card_intro_caveat_2=cards[1]["card_intro_caveat"],
        card_intro_caveat_3=cards[2]["card_intro_caveat"],
        voice_card_1_block=_voice_card_block_text(cards[0]), voice_card_2_block=_voice_card_block_text(cards[1]),
        voice_card_3_block=_voice_card_block_text(cards[2]),
        similar_voices_clarification_block=similar_block,
        experiential_claim_grounding_block=COMMON_EXPERIENTIAL_CLAIM_GROUNDING_BLOCK,
        tension_common_ground_value=theme_config["tension_common_ground_value"],
        stake_1=cards[0]["stake"], stake_2=cards[1]["stake"], stake_3=cards[2]["stake"],
        tension_asymmetry_value=theme_config["tension_asymmetry_value"],
        tension_external_constraint_block=tension_external_block,
        tension_self_check_block=tension_self_check_block,
        tension_external_constraint_prohibition_block=tension_external_constraint_prohibition_block,
    )
    return block


# ============================================================
# ANCHOR挿入(Trial-01/02と同じ手法、Production側template自体は変更しない)。
# ============================================================
def build_candidate_template(focus_module_block: str) -> str:
    assert ANCHOR in gen.COMMON_BLOCK_TEMPLATE, (
        "アンカー文字列がgen.COMMON_BLOCK_TEMPLATE内に見つかりません。Production側のtemplateが"
        "本モジュール設計時から変更されている可能性があるため中断してください(STOP条件)。")
    assert gen.COMMON_BLOCK_TEMPLATE.count(ANCHOR) == 1, (
        "アンカー文字列が複数回出現しています。挿入位置が一意に定まらないため中断してください。")
    return gen.COMMON_BLOCK_TEMPLATE.replace(ANCHOR, focus_module_block + "\n\n" + ANCHOR, 1)


def build_candidate_prompt(candidate_template: str, master_full_text: str, topic: str,
                            verified_ledger_text: str, instruction: str) -> str:
    common_block = candidate_template.format(
        hanshin_master_full_text=master_full_text, topic=topic,
        verified_ledger_text=verified_ledger_text,
        shared_point_blueprint_block="", evidence_compression_block="",
        editorial_type_module_block="")
    return gen.build_prompt(common_block, instruction)


def run_phase_a(focus_module_block: str, audit_dir: str) -> dict:
    os.makedirs(audit_dir, exist_ok=True)
    candidate_template = build_candidate_template(focus_module_block)
    with open(f"{audit_dir}/phase_a_candidate_template.txt", "w", encoding="utf-8") as f:
        f.write(candidate_template)
    with open(f"{audit_dir}/phase_a_focus_module_block.txt", "w", encoding="utf-8") as f:
        f.write(focus_module_block)

    reconstructed = gen.COMMON_BLOCK_TEMPLATE.replace(ANCHOR, focus_module_block + "\n\n" + ANCHOR, 1)
    clean_single_insert = (reconstructed == candidate_template)
    result = {"clean_single_insert_confirmed": clean_single_insert,
              "baseline_len": len(gen.COMMON_BLOCK_TEMPLATE), "candidate_len": len(candidate_template)}
    with open(f"{audit_dir}/phase_a_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[B-FAMILY-VOICES-WRITER-GENERIC][Phase A] clean_single_insert_confirmed={clean_single_insert}")
    return {"result": result, "phase_a_pass": clean_single_insert, "candidate_template": candidate_template}


# ============================================================
# 6区切りparser: Production正式版(b1prod.split_six_voice_sections)を
# そのまま再利用する(Trial側の独自複製は作らない)。
# ============================================================
def split_six_voice_sections(article_text: str) -> dict | None:
    return b1prod.split_six_voice_sections(article_text)


# ============================================================
# Fact Checker A'(opt-in、OPEN-131)。Ledger fragment除外は「可視Voice数を
# 超えるVoice番号のevidenceブロックを除去する」という一般化ルール
# (Trial-02のVOICE_4専用除外を一般化したもの、意味は変更しない)。
# ============================================================
def build_ledger_fragment_visible_voices_only(ledger_text: str, num_visible_voices: int = 3) -> str:
    tag_re = re.compile(r"^\[VOICE_(\d+)_EVIDENCE\]")
    lines = ledger_text.splitlines()
    out_lines = []
    skipping = False
    for line in lines:
        stripped = line.strip()
        m = tag_re.match(stripped)
        if m and int(m.group(1)) > num_visible_voices:
            skipping = True
            continue
        if skipping:
            if stripped == "" or stripped.startswith("[") or stripped.startswith("==="):
                skipping = False
            else:
                continue
        out_lines.append(line)
    return "\n".join(out_lines)


def run_fact_check_a_prime_3v(article_text: str, ledger_text: str, topic_ja: str, out_dir: str) -> dict:
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    # Fact Attribution Mode(OPEN-131、Production registryではeditorial_type
    # 横断の共有既定値=False[opt-in])を、3V Voice構造専用にTrue固定で使う。
    # これはテーマごとの任意選択ではなく、3V Focus Module自体の構造的要件
    # (Voice本文は一人称・無出典で語ることが「Research is backstage」原則の
    # 帰結として必須であり、Ledger evidence tagによる帰属をFact Checkerへ
    # 明示しない限りunsupported_specific_claimsで過剰にREVIEW_REQUIREDへ
    # 倒れる)。Trial-02(`TRIAL_EDITORIAL_TYPE_3V.fact_attribution_mode=True`
    # 固定)が既に同じ理由でこの選択をしており、3V VALIDATED closeoutの一部
    # として承認済みの適用パターンをそのまま踏襲するもの(新しいopt-in判断
    # ではない、registry既定値[他Editorial Type共有]は無変更のまま)。
    enabled = True
    ledger_fragment = build_ledger_fragment_visible_voices_only(ledger_text, num_visible_voices=3)
    with open(f"{out_dir}/audit/ledger_fragment_visible_voices_only.txt", "w", encoding="utf-8") as f:
        f.write(ledger_fragment)
    block = registry.build_voice_attribution_block(ledger_fragment) if enabled else ""
    with open(f"{out_dir}/audit/voice_attribution_block_used.txt", "w", encoding="utf-8") as f:
        f.write(block if block else "(fact_attribution_mode_enabled=False、blockは空文字列)")
    fc_prompt_for_evidence = r3.build_fact_check_prompt(topic_ja, article_text, [], voice_attribution_block=block)
    with open(f"{out_dir}/audit/fact_check_prompt_with_attribution.txt", "w", encoding="utf-8") as f:
        f.write(fc_prompt_for_evidence)

    print(f"[B-FAMILY-VOICES-WRITER-GENERIC] Fact Checker A'呼び出し開始(fact_attribution_mode_enabled={enabled})...")
    fc_record = b1prod.run_fact_checker(topic_ja, article_text, voice_attribution_block=block)
    fc_record["fact_attribution_mode_enabled"] = enabled
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fc_record, f, ensure_ascii=False, indent=2, default=str)
    print(f"[B-FAMILY-VOICES-WRITER-GENERIC] Fact Checker A'完了。final_status={fc_record.get('final_status')} "
          f"verdict={(fc_record.get('result') or {}).get('verdict')}")
    return fc_record


# ============================================================
# Point Overlap QA(monitoring専用、3V版)。Trial-02と同一ロジック。
# ============================================================
def run_overlap_monitoring_3v(sections: dict, out_dir: str) -> dict:
    voice_keys = ("voice_1", "voice_2", "voice_3")
    hook = sections["hook_body"]
    directed_voice_pairs = {}
    for a, b in itertools.permutations(voice_keys, 2):
        r = overlap_qa.flag_possible_paraphrase(sections[f"{a}_body"], sections[f"{b}_body"])
        directed_voice_pairs[f"{a}_vs_{b}"] = r
    voice_vs_hook = {}
    for v in voice_keys:
        r = overlap_qa.flag_possible_paraphrase(sections[f"{v}_body"], hook)
        voice_vs_hook[f"{v}_vs_hook"] = r
    all_flags = [r["flagged"] for r in directed_voice_pairs.values()] + [r["flagged"] for r in voice_vs_hook.values()]
    summary = {
        "qa_status": "OK",
        "note": ("EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-PHASE1B-04: monitoring専用(合否判定には"
                 "使わない、N=1で閾値を決めない)。有向ペア6(Permutation(3,2))+ vs Hook 3 = 9値。"
                 "lexical_overlap_ratio()はProduction関数(er008_point_overlap_qa_18.py)を"
                 "無変更のまま使用。"),
        "directed_voice_pair_count": len(directed_voice_pairs),
        "voice_vs_hook_count": len(voice_vs_hook),
        "any_flagged": any(all_flags),
        "directed_voice_pairs": directed_voice_pairs,
        "voice_vs_hook": voice_vs_hook,
    }
    with open(f"{out_dir}/point_overlap_qa_monitoring_3v.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[B-FAMILY-VOICES-WRITER-GENERIC] Overlap monitoring(9値)完了。any_flagged={summary['any_flagged']}")
    return summary


# ============================================================
# Analytical Leakage Check(3V版、汎用)。external_constraint無効時は
# `leak_tension_constraint_integration`基準自体を対象から外す(適用対象で
# ない基準についてFAIL/PASSを機械的に強制しないため、新QA基準の追加ではない)。
# ============================================================
VOICE_LEAKAGE_FIELDS = (
    "leak_evidence_subject", "leak_numbers_foreground", "leak_narrator_analysis",
    "leak_unknowable_analysis", "leak_discovery_syntax", "leak_evidence_memorable",
)
TENSION_LEAKAGE_FIELDS_BASE = (
    "leak_evidence_subject", "leak_numbers_foreground", "leak_discovery_syntax",
    "leak_evidence_memorable", "leak_tension_reverts_to_research", "leak_binary_camp_split",
)
TENSION_LEAKAGE_FIELD_CONSTRAINT_INTEGRATION = "leak_tension_constraint_integration"
CLOSING_LEAKAGE_FIELDS = ("leak_closing_simple_summary",)

LEAKAGE_CHECK_DEVELOPER_MESSAGE = (
    "あなたは'Voices/Perspective'型記事(3 Voices版)のVoice section・Tension section・"
    "Closing sectionを審査する、厳格なEditorial QA判定者です。それぞれのsectionが、実在する"
    "当事者(人)の経験・価値観・必要・心配として書かれているか、あるいは調査結果・データを"
    "整理して説明する文章、単なる要約、Writer自身の解決策提案、単純な2対1分割に戻っていないかを、"
    "各section指定の基準についてPASS/FAILで判定してください。各基準についてPASSは『問題なし』、"
    "FAILは『その問題が実際に本文に存在する』ことを意味します。FAILの場合は、該当する原文の"
    "一節をquoted_evidenceにそのまま引用してください(複数箇所ある場合は代表的な1〜2箇所)。"
    "PASSの場合はquoted_evidenceを空文字列にしてください。"
)


def _leakage_item_schema(fields: tuple) -> dict:
    props = {f: {"type": "string", "enum": ["PASS", "FAIL"]} for f in fields}
    props["reasoning"] = {"type": "string"}
    props["quoted_evidence"] = {"type": "string"}
    return {"type": "object", "properties": props, "required": list(props.keys()), "additionalProperties": False}


def build_leakage_schema_3v(external_constraint_enabled: bool) -> tuple:
    tension_fields = TENSION_LEAKAGE_FIELDS_BASE + (
        (TENSION_LEAKAGE_FIELD_CONSTRAINT_INTEGRATION,) if external_constraint_enabled else ())
    section_fields = {
        "voice_1": VOICE_LEAKAGE_FIELDS, "voice_2": VOICE_LEAKAGE_FIELDS, "voice_3": VOICE_LEAKAGE_FIELDS,
        "tension": tension_fields, "closing": CLOSING_LEAKAGE_FIELDS,
    }
    schema = {
        "name": "analytical_leakage_check_3v_generic",
        "schema": {
            "type": "object",
            "properties": {k: _leakage_item_schema(v) for k, v in section_fields.items()},
            "required": list(section_fields.keys()), "additionalProperties": False,
        },
        "strict": True,
    }
    return schema, section_fields


def build_leakage_check_prompt_3v(sections: dict, external_constraint_enabled: bool) -> str:
    tension_extra = ""
    if external_constraint_enabled:
        tension_extra = (
            "- leak_tension_constraint_integration: Tensionが、外部制約(バイアス監査義務・"
            "高リスク分類・過去の中止/提訴事例等)を、3人の合理性を制約する実質的な力として"
            "自然に統合している場合PASS。外部制約への言及が全く無い場合、または単なる箇条書き・"
            "列挙・解説として付け足されているだけ(3人の物語に統合されていない)場合はFAILと"
            "してください。\n")
    return f"""以下は、あるVoices/Perspective型記事(3 Voices版)の5つのsection本文
(Voice 1〜3/Tension/Closing)です。それぞれについて、指定された項目を判定してください
(それぞれPASS/FAIL)。

【Voice 1〜3に共通で適用する6項目】
- leak_evidence_subject: 文の主語がsurvey/research/data/percentageになっている文が無い場合PASS
- leak_numbers_foreground: 具体的な数字・比較結果が、その人の経験の描写より前面に出ていない場合
  PASS(数字が0個、または1個だけがその人の実感として自然に織り込まれている場合はPASS)
- leak_narrator_analysis: Narrator(語り手)が、Voiceの人物を外側から分析・要約していない場合PASS
- leak_unknowable_analysis: その人物自身が実際に考え・言いそうにない、外部の分析的視点を、その人の
  Perspectiveとして書いていない場合PASS
- leak_discovery_syntax: Discovery/Trend記事のような文構造へ戻っていない場合PASS
- leak_evidence_memorable: Evidenceよりもその人物の経験・感情の方が記憶に残る書き方になっている場合PASS

いずれのVoiceについても、他のVoiceと同一の基準で判定してください(特定の立場が抽象的な
代弁者の解説になっている場合は、leak_evidence_subject/leak_narrator_analysis/leak_discovery_syntax
のいずれかでFAILとしてください)。

【Tensionに適用する項目】
- leak_evidence_subject / leak_numbers_foreground / leak_discovery_syntax / leak_evidence_memorable:
  上記と同じ意味(Tension本文に対して判定)
- leak_tension_reverts_to_research: Tensionの中心が、3人がなぜ違う答えに至るのかの掘り下げになって
  おり、survey/研究データそのものの説明・比較へ戻っていない場合PASS
- leak_binary_camp_split: Tensionが3人を単純に対称的な2対1の陣営へ分けて描いていない場合PASS
  (分けている場合FAIL)
{tension_extra}
【Closingに適用する1項目】
- leak_closing_simple_summary: Closingが、単なる要約や「人による」という結び方だけで終わっておらず、
  かつWriter自身の解決策・妥協案の提案になっていない場合PASS

reasoningには、判定理由を1〜2文の日本語で書いてください。FAILの場合はquoted_evidenceに該当する
原文を引用してください(英語本文をそのまま引用してよい)。PASSの場合quoted_evidenceは空文字列に
してください。

【Voice 1本文】
{sections['voice_1_body']}

【Voice 2本文】
{sections['voice_2_body']}

【Voice 3本文】
{sections['voice_3_body']}

【Tension本文】
{sections['tension_body']}

【Closing本文】
{sections['closing_body']}
"""


def run_analytical_leakage_check_3v(client, sections: dict, model: str, reasoning_effort: str,
                                     out_dir: str, attempt: int, external_constraint_enabled: bool) -> dict:
    schema, section_fields = build_leakage_schema_3v(external_constraint_enabled)
    prompt = build_leakage_check_prompt_3v(sections, external_constraint_enabled)
    response = client.responses.create(
        model=model, reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **schema}},
        input=[{"role": "developer", "content": LEAKAGE_CHECK_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    if response.model != model:
        raise RuntimeError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    text = getattr(response, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Analytical Leakage Check応答が空です")
    parsed = json.loads(text)

    flagged_items = []
    for section_key, fields in section_fields.items():
        item = parsed[section_key]
        fail_fields = [f for f in fields if item[f] == "FAIL"]
        if fail_fields:
            flagged_items.append({"voice": section_key, "fail_fields": fail_fields,
                                   "reasoning": item["reasoning"], "quoted_evidence": item["quoted_evidence"]})
    result = {
        "model": response.model, "response_id": response.id, "prompt": prompt, "parsed": parsed,
        "flagged_items": flagged_items, "any_flagged": bool(flagged_items),
    }
    with open(f"{out_dir}/analytical_leakage_check_3v_attempt{attempt}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[B-FAMILY-VOICES-WRITER-GENERIC][Leakage Check] attempt{attempt}: any_flagged={result['any_flagged']} "
          f"flagged_items={[(x['voice'], x['fail_fields']) for x in flagged_items]}")
    return result


def build_leakage_corrective_note_3v(leakage_result: dict, voice_cards: list) -> str:
    lines = [
        "【Analytical Leakage Check是正メモ(前回attemptの検出結果。Voice Card・Verified "
        "Fact Ledger・骨格は変更しません。今回はこの記事全文をゼロから新しく書き直して"
        "ください。前回の文をそのまま部分修正するのではなく、Voice Cardの内容から書き始め、"
        "以下の問題を避けてください)】",
    ]
    voice_label = {
        "voice_1": f"Voice 1({voice_cards[0]['stakeholder_label']})",
        "voice_2": f"Voice 2({voice_cards[1]['stakeholder_label']})",
        "voice_3": f"Voice 3({voice_cards[2]['stakeholder_label']})",
        "tension": "Tension", "closing": "Closing",
    }
    for item in leakage_result["flagged_items"]:
        lines.append(f"- {voice_label[item['voice']]}で検出: {', '.join(item['fail_fields'])}")
        lines.append(f"  理由: {item['reasoning']}")
        if item["quoted_evidence"]:
            lines.append(f"  該当箇所(この種の書き方を避ける): \"{item['quoted_evidence']}\"")
    lines.append(
        "\n【この記事全体で必ず守るContractの優先事項(是正のたびに毎回再掲)】\n"
        "- Compactness: 記事全体の総語数は約410〜450語がsoft targetです(hard capではありません)。"
        "削るときはreplace-with-nothingを基本とし、削った直後に別の言い回しで同じ内容を書き足さないでください。\n"
        "- Tensionの役割: Tensionの中心はVoice Cardの3人の人物と、彼らを制約する力であり、"
        "Evidenceの列挙ではありません。3人を単純に2対1へ分けないでください。\n"
        "- 体験claimの根拠付け: 数値・制度・他者の行動を事実として述べる場合はLedger evidenceに限り、"
        "根拠がない事柄(自分の評判・信用が具体的にどうなるか等)は体験・感情・判断として書いてください。\n"
        "- 各Voiceの役割: 抽象的な立場の解説ではなく、具体的な状況・賭け金・責任を持つ一人の人物として"
        "書いてください(該当するVoiceがある場合はVoice Card冒頭の指示に従うこと)。\n"
        "- Closingの役割: 単なる要約や「人による」で終わらせず、この問題が実は何についての問題なのかという"
        "再定義そのものから書き始めてください。解決策の提案はしないでください。"
    )
    return "\n".join(lines)


# ============================================================
# Ledger Deviation Checker + Local Rewrite(既存呼び出し関数・引数・順序を
# 一切変更せず踏襲、article_textの内部構造[section数]に依存しない)。
# ============================================================
def run_ledger_deviation_and_local_rewrite(client, theme_id: str, label: str, article_text: str,
                                            verified_ledger_text: str, out_dir: str, ledger_model: str) -> dict:
    print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: ledger逸脱チェック開始(Hook-aware)...")
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
    print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: deviation overall_status="
          f"{deviation_result['parsed']['overall_status']} deviations={len(deviation_result['parsed']['deviations'])}")

    local_rewrite_results = []
    local_rewrite_cycles = []
    cycle = 0
    previously_seen_claims = set()

    def _run_check_window(window_text: str) -> dict:
        r = vfl01.run_deviation_check(client, verified_ledger_text, window_text, model=ledger_model, hook_aware=True)
        return r["parsed"]

    major_items = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]

    while major_items and cycle < local_rewrite.MAX_REWRITE_CYCLES:
        cycle += 1
        newly_discovered_claims = [d["claim_in_article"] for d in major_items
                                    if d["claim_in_article"] not in previously_seen_claims]
        print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: Local Rewrite cycle {cycle}/"
              f"{local_rewrite.MAX_REWRITE_CYCLES} - Ledger MAJOR {len(major_items)}件を検出"
              f"({len(newly_discovered_claims)}件は新規)。局所Rewrite開始...")

        cycle_results = []
        sentences = local_rewrite.split_sentences(article_text)
        for idx, deviation in enumerate(major_items, start=1):
            target, location_method = local_rewrite.locate_target_sentence(deviation["claim_in_article"], article_text)
            if target is None:
                cycle_results.append({
                    "cycle": cycle, "item_idx": idx, "original_ng_sentence": deviation["claim_in_article"],
                    "issue": deviation["issue"], "explanation": deviation["explanation"],
                    "attempts": [], "final_text": None, "resolved": False,
                    "human_review_required": True, "location_method": "not_found",
                })
                continue
            try:
                sidx = sentences.index(target)
            except ValueError:
                sidx = -1
            before_ctx = sentences[sidx - 1] if 0 <= sidx - 1 else ""
            after_ctx = sentences[sidx + 1] if 0 <= sidx and sidx + 1 < len(sentences) else ""
            point_context = local_rewrite.extract_point_context(article_text, target)
            point_context_found = point_context is not None
            if point_context is None:
                point_context = f"{before_ctx} {target} {after_ctx}".strip()
            r = local_rewrite.rewrite_ng_item(client, ledger_model, gen.REASONING_EFFORT, verified_ledger_text,
                                               point_context, target, deviation, before_ctx, after_ctx,
                                               _run_check_window)
            r["cycle"] = cycle
            r["item_idx"] = idx
            r["location_method"] = location_method
            r["point_context_found"] = point_context_found
            r["point_context"] = point_context
            cycle_results.append(r)
            print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: cycle {cycle} NG item {idx}: "
                  f"resolved={r['resolved']} human_review={r['human_review_required']} attempts={len(r['attempts'])}")

        article_text = local_rewrite.apply_rewrites(article_text, cycle_results)
        article_text = gen.normalize_article_formatting(article_text)
        with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(article_text)

        print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: cycle {cycle} Local Rewrite後、Ledger全体を再判定...")
        deviation_result = vfl01.run_deviation_check(client, verified_ledger_text, article_text,
                                                       model=ledger_model, hook_aware=True)
        recheck_major = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
        print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: cycle {cycle} 再判定 overall_status="
              f"{deviation_result['parsed']['overall_status']} MAJOR={len(recheck_major)}件")

        previously_seen_claims |= {d["claim_in_article"] for d in major_items}
        local_rewrite_results.extend(cycle_results)
        local_rewrite_cycles.append({
            "cycle": cycle, "targeted_major_count": len(major_items),
            "newly_discovered_claims": newly_discovered_claims, "results": cycle_results,
            "full_recheck_overall_status": deviation_result["parsed"]["overall_status"],
            "full_recheck_major_count": len(recheck_major),
            "full_recheck_remaining_major_claims": [d["claim_in_article"] for d in recheck_major],
        })
        major_items = recheck_major

    cycle_exhausted = bool(major_items) and cycle >= local_rewrite.MAX_REWRITE_CYCLES
    with open(f"{out_dir}/ledger_deviation.json", "w", encoding="utf-8") as f:
        json.dump(deviation_result["parsed"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/local_rewrite_results.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_results, f, ensure_ascii=False, indent=2, default=str)
    with open(f"{out_dir}/audit/local_rewrite_cycles.json", "w", encoding="utf-8") as f:
        json.dump(local_rewrite_cycles, f, ensure_ascii=False, indent=2, default=str)

    remaining_major = major_items
    any_human_review = any(r.get("human_review_required") for r in local_rewrite_results)
    return {
        "article_text": article_text,
        "ledger_status": deviation_result["parsed"]["overall_status"],
        "ledger_deviation_count": len(deviation_result["parsed"]["deviations"]),
        "local_rewrite_results": local_rewrite_results, "local_rewrite_cycles": local_rewrite_cycles,
        "local_rewrite_cycle_exhausted": cycle_exhausted,
        "remaining_major_count": len(remaining_major), "any_human_review_required": any_human_review,
    }


# ============================================================
# Writer本体(1 attempt分)。Trial-02発見済みの迂回(vfl01.run_writer_
# no_search()を直接呼び、構造検証はsplit_six_voice_sections()に委ねる)を
# 同様に踏襲する(OPEN-132で追跡中、Production全体共有ゲートの汎用ゲート
# `h3_count != 2`はB-Family Voices用途を想定しておらず、変更にはProduction
# 側の承認が必要なため本モジュールでは一切変更しない)。
# ============================================================
def _generate_and_compress_article_3v(client, theme_id: str, label: str, prompt: str, out_dir: str,
                                       apply_evidence_compression: bool, model: str,
                                       max_technical_attempts: int = 2) -> dict:
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    attempts = []
    raw_result = None
    for attempt in range(1, max_technical_attempts + 1):
        try:
            raw_result = vfl01.run_writer_no_search(client, prompt, model=model)
            attempts.append({"attempt": attempt, "status": "OK", "model": raw_result["model"],
                              "response_id": raw_result["response_id"]})
            break
        except Exception as e:
            attempts.append({"attempt": attempt, "status": "TECHNICAL_FAILED", "error": f"{type(e).__name__}: {e}"})
            if attempt < max_technical_attempts:
                time.sleep(2)
                continue
    with open(f"{out_dir}/audit/writer_attempts.json", "w", encoding="utf-8") as f:
        json.dump(attempts, f, ensure_ascii=False, indent=2, default=str)
    if raw_result is None:
        print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: writer技術的失敗(通信障害等)。")
        return {"status": "TECHNICAL_GENERATION_FAILED", "article_text": None}

    article_text, fact_usage_report = blueprint_mod.extract_trailing_metadata_block(raw_result["raw_text"].strip())
    if fact_usage_report is not None:
        with open(f"{out_dir}/audit/fact_usage_report.json", "w", encoding="utf-8") as f:
            json.dump(fact_usage_report, f, ensure_ascii=False, indent=2)

    evidence_compression_applied = False
    if apply_evidence_compression:
        with open(f"{out_dir}/audit/pre_editor_article.md", "w", encoding="utf-8") as f:
            f.write(article_text)
        print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: Evidence Compression(Lossless Editor)呼び出し開始...")
        editor_result = ec_editor.run_lossless_editor(client, article_text, model=model)
        with open(f"{out_dir}/audit/evidence_compression_editor_raw.json", "w", encoding="utf-8") as f:
            json.dump(editor_result, f, ensure_ascii=False, indent=2, default=str)
        if editor_result.get("raw_text"):
            article_text = editor_result["raw_text"]
            evidence_compression_applied = True
        print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: Evidence Compression完了。"
              f"response_id={editor_result.get('response_id')}")

    article_text = gen.normalize_article_formatting(article_text)
    with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)

    return {"status": "OK", "article_text": article_text, "fact_usage_report": fact_usage_report,
            "evidence_compression_applied": evidence_compression_applied}


def run_voices_pattern_3v(client, theme_id: str, label: str, prompt: str, verified_ledger_text: str,
                           topic_ja: str, out_dir: str, external_constraint_enabled: bool,
                           apply_evidence_compression: bool = True,
                           apply_directional_fact_precheck: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    writer_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)

    gen_result = _generate_and_compress_article_3v(
        client, theme_id, label, prompt, out_dir, apply_evidence_compression, writer_model)
    if gen_result["status"] != "OK":
        return {"label": label, "status": gen_result["status"], "article_text": None}
    article_text = gen_result["article_text"]

    sections = split_six_voice_sections(article_text)
    if sections is None:
        return {
            "label": label, "status": "STRUCTURE_NOT_SIX_SECTIONS", "article_text": article_text,
            "metrics": gen.compute_metrics(article_text),
        }

    print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: Overlap monitoring(9値)開始...")
    overlap_summary = run_overlap_monitoring_3v(sections, out_dir)

    metrics = gen.compute_metrics(article_text)
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: metrics={metrics}")

    fc_record = run_fact_check_a_prime_3v(article_text, verified_ledger_text, topic_ja, out_dir)
    fc_status = fc_record.get("final_status")
    verdict = (fc_record.get("result") or {}).get("verdict")
    if verdict == "FAIL":
        print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: Fact CheckerがFAILと判定。NG_REVIEW_REQUIREDとして報告します。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": metrics, "sections": sections,
            "fact_status": fc_status, "fact_verdict": verdict, "fact_check_result": fc_record,
            "point_overlap_qa_monitoring": overlap_summary,
        }

    ledger_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)
    ledger_result = run_ledger_deviation_and_local_rewrite(
        client, theme_id, label, article_text, verified_ledger_text, out_dir, ledger_model)
    article_text = ledger_result["article_text"]
    sections = split_six_voice_sections(article_text)  # Local Rewrite後に再抽出

    if ledger_result["remaining_major_count"] or ledger_result["any_human_review_required"]:
        print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: Local Rewrite cycleを尽くしてもLedger MAJOR残存/"
              f"human_review_required。NG_REVIEW_REQUIREDとして報告します。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": gen.compute_metrics(article_text), "sections": sections,
            "fact_status": fc_status, "fact_verdict": verdict,
            "ledger_status": ledger_result["ledger_status"],
            "ledger_deviation_count": ledger_result["ledger_deviation_count"],
            "local_rewrite_cycles": ledger_result["local_rewrite_cycles"],
            "local_rewrite_cycle_exhausted": ledger_result["local_rewrite_cycle_exhausted"],
            "point_overlap_qa_monitoring": overlap_summary,
        }

    directional_precheck_status = None
    if apply_directional_fact_precheck:
        print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: 比較方向Fact事前チェック開始(rule-based、¥0)...")
        vfl_path = f"{out_dir}/research/stage_b3_vfl.json"  # 本経路では存在しない、Layer 2のみ実行(¥0)
        directional_result = dfp.audit_article_directional_facts(article_text, verified_ledger_text, vfl_path=vfl_path)
        directional_precheck_status = directional_result["overall_status"]
        with open(f"{out_dir}/audit/directional_fact_precheck.json", "w", encoding="utf-8") as f:
            json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[B-FAMILY-VOICES-WRITER-GENERIC][{theme_id}] {label}: 比較方向Fact事前チェック完了。overall_status={directional_precheck_status}")

    return {
        "label": label, "status": "OK", "article_text": article_text,
        "metrics": gen.compute_metrics(article_text), "sections": sections,
        "fact_status": fc_status, "fact_verdict": verdict, "fact_check_result": fc_record,
        "ledger_status": ledger_result["ledger_status"],
        "ledger_deviation_count": ledger_result["ledger_deviation_count"],
        "local_rewrite_cycles": ledger_result["local_rewrite_cycles"],
        "local_rewrite_cycle_exhausted": ledger_result["local_rewrite_cycle_exhausted"],
        "point_overlap_qa_monitoring": overlap_summary,
        "directional_fact_precheck_status": directional_precheck_status,
    }


def run_pipeline_3v(client, theme_id: str, label: str, base_prompt: str, verified_ledger_text: str,
                     topic_ja: str, voice_cards: list, external_constraint_enabled: bool,
                     out_dir_base: str) -> dict:
    writer_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)
    attempt_history = []
    corrective_note = ""
    final_result = None
    final_attempt_dir = None

    for attempt in range(1, MAX_WRITER_ATTEMPTS + 1):
        attempt_dir = f"{out_dir_base}_attempt{attempt}"
        prompt_for_attempt = base_prompt + (f"\n\n{corrective_note}" if corrective_note else "")
        os.makedirs(f"{attempt_dir}/audit", exist_ok=True)
        with open(f"{attempt_dir}/audit/candidate_prompt_used.txt", "w", encoding="utf-8") as f:
            f.write(prompt_for_attempt)

        print(f"[B-FAMILY-VOICES-WRITER-GENERIC] Writer attempt {attempt}/{MAX_WRITER_ATTEMPTS} 開始(out_dir={attempt_dir})...")
        t0 = time.time()
        with cl.logging_context(theme_id, f"writer_{label.lower()}_attempt{attempt}"):
            result = run_voices_pattern_3v(client, theme_id, label, prompt_for_attempt, verified_ledger_text,
                                            topic_ja, attempt_dir, external_constraint_enabled)
        result["elapsed_seconds"] = round(time.time() - t0, 1)

        entry = {"attempt": attempt, "out_dir": attempt_dir, "status": result.get("status")}
        final_result = result
        final_attempt_dir = attempt_dir

        if result.get("status") != "OK" or not result.get("article_text"):
            entry["leakage_check"] = None
            entry["any_flagged"] = None
            attempt_history.append(entry)
            print(f"[B-FAMILY-VOICES-WRITER-GENERIC] attempt {attempt}: status={result.get('status')}のためLeakage Checkをスキップします。")
            break

        sections = result.get("sections") or split_six_voice_sections(result["article_text"])
        if sections is None:
            entry["leakage_check"] = {"qa_status": "SKIPPED_NO_SIX_SECTIONS"}
            entry["any_flagged"] = None
            attempt_history.append(entry)
            final_result["sections"] = None
            print(f"[B-FAMILY-VOICES-WRITER-GENERIC] attempt {attempt}: 6区切り構造が検出できずLeakage Checkをスキップしました。")
            break

        leakage = run_analytical_leakage_check_3v(
            client, sections, writer_model, gen.REASONING_EFFORT, attempt_dir, attempt, external_constraint_enabled)
        entry["leakage_check"] = leakage
        entry["any_flagged"] = leakage["any_flagged"]
        attempt_history.append(entry)
        final_result["sections"] = sections
        final_result["analytical_leakage_check"] = leakage

        if not leakage["any_flagged"]:
            print(f"[B-FAMILY-VOICES-WRITER-GENERIC] attempt {attempt}: Analytical Leakage Check flagged項目なし。確定。")
            break
        if attempt == MAX_WRITER_ATTEMPTS:
            print(f"[B-FAMILY-VOICES-WRITER-GENERIC] attempt {attempt}: 最大attempt数に到達。flagged項目が残った状態の"
                  f"記事を最終結果として記録します(Report側でUSER_DECISION_REQUIRED候補として扱う)。")
            break
        corrective_note = build_leakage_corrective_note_3v(leakage, voice_cards)

    with open(f"{out_dir_base}_attempt_history.json", "w", encoding="utf-8") as f:
        json.dump(attempt_history, f, ensure_ascii=False, indent=2, default=str)

    return {"final_result": final_result, "final_attempt_dir": final_attempt_dir,
            "attempt_history": attempt_history, "total_attempts": len(attempt_history)}


def run_writer_stage_generic(theme_config: dict, out_dir_base: str, label: str = "B1B") -> dict:
    """新テーマ用エントリポイント(Writerのみ、TTSは行わない)。`theme_config`
    (`make_theme_config()`の戻り値)からLedger・Voice Card・Tension contentを
    読み取り、汎用テンプレートで記事を生成する。TTSは呼ばない。"""
    ledger_path = theme_config["ledger_path"]
    if not os.path.exists(ledger_path):
        raise SystemExit(f"Ledger not found at {ledger_path}. STOP条件(Ledger未確定)。")
    with open(ledger_path, encoding="utf-8") as f:
        verified_ledger_text = f.read()

    os.makedirs(out_dir_base, exist_ok=True)
    focus_module_block = build_focus_module_block_3v(theme_config)
    phase_a = run_phase_a(focus_module_block, f"{out_dir_base}/audit")
    if not phase_a["phase_a_pass"]:
        print("[B-FAMILY-VOICES-WRITER-GENERIC] Phase Aで意図しない差分を検出したため、Writerへ進まずSTOPします。")
        return {"phase_a": phase_a, "pipeline": None, "status": "STOP_PHASE_A_UNEXPECTED_DIFF"}

    client = vfl01.get_client()
    cl.install(f"{out_dir_base}/raw_usage_log_writer.jsonl")
    master_full_text = ab01.load_master_full_text()

    candidate_prompt = build_candidate_prompt(
        phase_a["candidate_template"], master_full_text, theme_config["topic_ja"], verified_ledger_text,
        gen.B1_B_DIRECT_INSTRUCTION)
    with open(f"{out_dir_base}/audit_candidate_prompt_base.txt", "w", encoding="utf-8") as f:
        f.write(candidate_prompt)

    external_constraint_enabled = bool(
        theme_config.get("external_constraint") and theme_config["external_constraint"].get("enabled"))
    theme_id = theme_config["theme_id"]
    print(f"[B-FAMILY-VOICES-WRITER-GENERIC] Writer + Analytical Leakage Checkパイプライン開始"
          f"(最大{MAX_WRITER_ATTEMPTS} attempts、external_constraint_enabled={external_constraint_enabled})...")
    pipeline_result = run_pipeline_3v(client, theme_id, label, candidate_prompt, verified_ledger_text,
                                       theme_config["topic_ja"], theme_config["voice_cards"],
                                       external_constraint_enabled, out_dir_base)

    with open(f"{out_dir_base}/summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "attempt_history": pipeline_result["attempt_history"],
            "total_attempts": pipeline_result["total_attempts"],
            "final_attempt_dir": pipeline_result["final_attempt_dir"],
            "final_result": {k: v for k, v in (pipeline_result["final_result"] or {}).items()
                              if k not in ("article_text", "sections")},
        }, f, ensure_ascii=False, indent=2, default=str)

    final_result = pipeline_result["final_result"] or {}
    print(f"[B-FAMILY-VOICES-WRITER-GENERIC] 完了。total_attempts={pipeline_result['total_attempts']} "
          f"final_status={final_result.get('status')} fact_verdict={final_result.get('fact_verdict')} "
          f"ledger_status={final_result.get('ledger_status')}")
    return {"phase_a": phase_a, "pipeline": pipeline_result, "status": "DONE"}


# ============================================================
# Content Integrity Check + Key Phrase + Support(Comment 1/4)。
# Content Integrity CheckはProduction既存pure関数(b1prod、Phase 1で
# 正式移設済み)をそのまま呼ぶ。Key PhraseはProduction既存汎用関数
# (sc.run_key_phrases、A2 Trend Synthesis E2Eで新規テーマに実運用済みの
# 前例と同一呼び出し)を新規記事に対して呼ぶだけの薄いwrapper。
# ============================================================
def run_content_integrity_and_key_phrase(article_text: str, out_dir: str, article_id: str) -> dict:
    parts = b1prod.build_parts_3v(article_text)
    with open(f"{out_dir}/parts.json", "w", encoding="utf-8") as f:
        json.dump(parts, f, ensure_ascii=False, indent=2, default=str)

    kp_dir = f"{out_dir}/key_phrases"
    os.makedirs(kp_dir, exist_ok=True)
    kp = sc.run_key_phrases(article_text, kp_dir, article_id, "B1-B(N3-01, direct generation, 3V generic)",
                             process="B1_SUPPORT")
    kp_merged = (kp.get("canonicalization") or {}).get("merged") or {"items": []}

    integrity = b1prod.run_content_integrity_check_3v(article_text, parts, kp_merged)
    with open(f"{out_dir}/audit/content_integrity_3v.json", "w", encoding="utf-8") as f:
        json.dump(integrity, f, ensure_ascii=False, indent=2, default=str)
    print(f"[B-FAMILY-VOICES-WRITER-GENERIC][Content Integrity] all_section_bodies_verbatim_from_article="
          f"{integrity['all_section_bodies_verbatim_from_article']}")
    return {"parts": parts, "key_phrases": kp, "content_integrity": integrity}


def run_support_comments(client, sections: dict, out_dir: str) -> dict:
    import er003_v1_b1_scaffold_01_generate as b1s
    model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)
    comment_roles = registry.COMMENT_ROLES  # Production, 無変更

    c1_context = f"【これから聞く本文(The Question)】\n{sections['hook_body']}"
    c1 = b1s.run_support_text(client, comment_roles["comment_1"], c1_context, model=model)

    c4_context = (f"【聞き終えた内容(視点の違いの深掘り)】\n{sections['tension_body']}\n\n"
                  f"【これから聞く結びの見出しのみ(内容は伏せる)】\n{sections['closing_heading']}")
    c4 = b1s.run_support_text(client, comment_roles["comment_4"], c4_context, model=model)

    result = {
        "comment_1": {"text": c1["text"], "status": c1["status"], "llm_generated": True},
        "comment_4": {"text": c4["text"], "status": c4["status"], "llm_generated": True},
        "note": ("Comment 2/3は3V専用のRole prompt[design.md B-1手動ドラフト、Trial-only]が"
                 "既存registryにまだ正式登録されていないため本経路では生成しない(TTSを行わない"
                 "Regressionのスコープでは不要)。Production配線時にregistry側でComment 2/3の"
                 "3V対応を別途整備する。"),
    }
    with open(f"{out_dir}/support_comments.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[B-FAMILY-VOICES-WRITER-GENERIC][Support] comment_1={c1['text'][:60]!r} comment_4={c4['text'][:60]!r}")
    return result
