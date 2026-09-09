# ============================================================
# er012_editorial_b_voices_4v_article_trial_01.py
# 管理ID: EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01
# ============================================================
# Lane: Lane B(Lane A・SSOT統合タスクとは完全に独立)。**Trial専用**
# (Production/Trial-07/registry/Contract編集禁止、SSOT・Git操作禁止)。
#
# テーマ固定(ユーザー決定2026-09-09): "Should companies use AI to screen
# job applicants?"。4V=案A(ユーザー決定、DECISION_LOG PM-CLOSEOUT-
# CONSOLIDATION-30/B-3V4V-1=(c)): Voice 1=Applicant(Algieba)/
# Voice 2=Recruiter・Hiring Manager(Erinome)/Voice 3=Business・
# Efficiency(Schedar)/Voice 4=Fairness・Legal・HR Governance(Sulafat)。
# 4V 1本のみ先行(B1B、テキストのみ、音声なし)。
#
# 本ファイルは`er012_editorial_b_voices_trial_07.py`(2 Voices、5区切り)の
# Writer経路(`run_voices_pattern_run03`等)を土台に、新規ファイルとして
# 複製・4V化したものである(Opusレビュー指摘0-A: Trial-07自体は
# `er012_editorial_b_family_production_phase1_test_01.py`がProduction定数
# とのbyte一致をテストしているため編集禁止)。Trial-07本体は一切変更して
# いない。Production(`er012_b_family_voices_production_01.py`・
# `er012_b_family_editorial_type_registry_01.py`・
# `er012_b_family_production_runner_01.py`)は読み取り専用importのみで
# 変更していない。
#
# Ledger: `er012_output/ai_screening_ledger_trial_01/research/
# verified_fact_ledger.txt`(EDITORIAL-B-FAMILY-VOICES-AI-SCREENING-
# LEDGER-TRIAL-01で作成済み、全41 fact中39件CONFIRMED・2件PARTIALLY_
# CONFIRMEDのため本Trialでは不採用、VALIDATED)。本ファイルはこの既存
# Ledger・`perspective_map.md`を読み取り専用で参照するのみで、新規
# Research呼び出しは行わない。
#
# Fact Checker A'(opt-in、OPEN-131-MULTI-VOICE-FACT-ATTRIBUTION-
# PRODUCTION-WIRING-01): Production経路(`runner.run_fact_check_b1`→
# `b1prod.run_fact_checker`→`r3.build_fact_check_prompt`)の呼び出し
# チェーンをそのまま踏襲するが、`runner.run_fact_check_b1`自体は内部で
# `registry.is_fact_attribution_mode_enabled("b_family_voices")`を
# ハードコード呼び出ししており、Production registry側の
# `fact_attribution_mode`は既定Falseのまま(本Trialではregistryを編集
# しない)。そのため本ファイルは、Trial側の`editorial_type`相当の辞書
# (`family`/`fact_attribution_mode`キーを持つ、下記
# `TRIAL_EDITORIAL_TYPE_4V`)に対して、`registry.is_fact_attribution_mode_
# enabled()`と同じ判定ロジックをTrial側関数として複製し(Production関数
# 自体は変更しない)、有効と判定された場合のみ`registry.build_voice_
# attribution_block()`(Production、無変更)を呼んでblockを作り、
# `b1prod.run_fact_checker(topic, article_text, voice_attribution_
# block=block)`(Production、無変更。内部で`r3.build_fact_check_prompt`
# を呼ぶ)へ渡す。これによりopt-in ON状態を、Production registryを一切
# 編集せずに再現する。
#
# 命名: segment命名は`point_one/point_two`互換維持+`point_three/
# point_four`は使わず(Fable決定により本Trialでは`voice_1..voice_4`
# 命名、Markdown見出しラベルもこれに準じる。理由: 4V記事はvoice_a/bという
# 2声固定の命名を継承する意味が無く、`voice_1..voice_4`の方が構造として
# 明確なため。OPEN-129 required_structureの正本統合はOPEN-132で追跡)。
#
# 禁止: 音声生成、Production/Trial-07/registry/Contract編集、SSOT・Git
# 操作、3V作業、閾値変更、バックグラウンド待機。
#
# STOP条件: Ledger未確定/費用上限到達(¥300)/見出し数が7にならない状態が
# retry上限まで継続/Production・Trial-07・registryへの書込みが必要/4V
# 記事が賛否2対2に分割/新規failure mode/Fact A'がProduction関数経由で
# 呼べない。
#
# 到達してよいStatus: REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。
from __future__ import annotations

import itertools
import json
import os
import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er002_ja_web_research_r3 as r3
import er003_v1_b1_scaffold_01_generate as b1s
import er003_v1_en_direct_ab_01_generate as ab01
import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_articles_generate as gen
import er003_v1_n3_01_evidence_compression_editor as ec_editor
import er005_cost_logger as cl
import er008_shared_point_blueprint_01 as blueprint_mod
import er006_model_routing_contract_01 as routing
import er008_directional_fact_precheck_08 as dfp
import er008_point_overlap_qa_18 as overlap_qa
import er010_ledger_local_rewrite_09 as local_rewrite
import er012_b_family_editorial_type_registry_01 as registry  # Production, 読み取り専用import
import er012_b_family_voices_production_01 as b1prod  # Production, 読み取り専用import

THEME_ID = "editorial_b_voices_4v_article_trial_01"
OUT_DIR = "er012_output/editorial_b_voices_4v_article_trial_01"
os.makedirs(OUT_DIR, exist_ok=True)

# EDITORIAL-B-FAMILY-VOICES-AI-SCREENING-LEDGER-TRIAL-01の既存成果物を
# 読み取り専用で参照する(このファイルは複製・上書きしない)。
LEDGER_SOURCE_DIR = "er012_output/ai_screening_ledger_trial_01/research"
LEDGER_PATH = f"{LEDGER_SOURCE_DIR}/verified_fact_ledger.txt"
PERSPECTIVE_MAP_PATH = f"{LEDGER_SOURCE_DIR}/perspective_map.md"

TOPIC_EN = "Should companies use AI to screen job applicants?"

# テーマ説明(TOPIC_JA相当、Trial-07のTOPIC_JAと同じ役割: Writer向け
# COMMON_BLOCK_TEMPLATEの{topic}へ挿入する日本語の中立的なテーマ説明。
# Ledger・perspective_map.mdの内容のみに基づき新規に執筆した[新しい主張・
# 数字は追加していない]。4者の役割紹介はperspective_map.mdの要約と一致)。
TOPIC_JA = (
    "2026年9月時点、多くの企業が採用選考の一部にAI(応募書類の自動スクリー"
    "ニング、適性・性格の自動スコアリング、動画面接での表情・話し方の自動"
    "評価など)を取り入れつつある。この記事の中心テーマは、『企業は採用選考"
    "にAIを使うべきか』の賛否をどちらか一つに決めることではなく、この同じ"
    "状況について、全く異なる利害・責任・経験を持つ4人—実際にAIによって"
    "評価される応募者(Applicant)、実際にAIツールを業務で使う、または"
    "使うかどうかを判断する採用担当・人事責任者(Recruiter・Hiring "
    "Manager)、コスト・採用スピード・スケーラビリティの観点から評価する"
    "経営・事業効率の担当者(Business・Efficiency)、そして合法性・公平性・"
    "監査可能性を検証する弁護士・規制当局・HRガバナンス専門家(Fairness・"
    "Legal・HR Governance)—が、それぞれ何を経験し、何を大切にし、何を"
    "心配し、何を守ろうとしているのかを、実在する調査・訴訟・法規制に"
    "基づいて具体的に描き、そのうえで、なぜ同じ状況が、それぞれが背負って"
    "いるものによって全く違う重みで見えるのかを理解することである。"
)

LABEL = "B1B"
RUN_ID = "run01"
LEVEL_OUT_DIR = f"{OUT_DIR}/{LABEL.lower()}_{RUN_ID}"

# ============================================================
# Voice assignment(ユーザー決定、DECISION_LOG PM-CLOSEOUT-CONSOLIDATION-30
# 「voice割当決定」節、2026-09-08。既存2V[Algieba/Erinome/Aoede]は不変、
# Schedar/Sulafatはユーザー承認によりfallbackから本採用へ格上げ済み[本
# 格上げはProduction配線ではなく本Trial限定の使用、Production配線は別途]）。
# ============================================================
VOICE_STAKEHOLDER_LABEL = {
    "voice_1": "Applicant",
    "voice_2": "Recruiter/Hiring Manager",
    "voice_3": "Business/Efficiency",
    "voice_4": "Fairness/Legal/HR Governance",
}
VOICE_TTS_NAME_TRIAL_ONLY = {  # 参考記録のみ、本Trialは音声生成しない
    "voice_1": "Algieba", "voice_2": "Erinome", "voice_3": "Schedar", "voice_4": "Sulafat",
}

# ============================================================
# Fact Attribution Mode(OPEN-131)opt-in判定: Trial側editorial_type相当
# 辞書。Production registryのEDITORIAL_TYPESへは一切追加しない(registry
# 編集禁止)。`family`/`fact_attribution_mode`キーはregistry.is_fact_
# attribution_mode_enabled()と同じ意味論を持つ(Opusレビュー1-MED対応）。
# ============================================================
TRIAL_EDITORIAL_TYPE_4V = {
    "family": "B",
    "fact_attribution_mode": True,  # Trial側でopt-in ONを強制(Production既定Falseは無変更)
}


def is_fact_attribution_mode_enabled_trial(et: dict) -> bool:
    """registry.is_fact_attribution_mode_enabled()と同一の判定ロジックを
    Trial側editorial_type辞書に対して複製したもの(Production関数は
    変更しない、Production EDITORIAL_TYPESへの新規editorial_type追加も
    しない)。"""
    return et.get("family") == "B" and bool(et.get("fact_attribution_mode"))


def run_fact_check_a_prime_4v(article_text: str, ledger_text: str, out_dir: str) -> dict:
    """Fact Checker A'(opt-in)をProduction関数経由(`registry.build_voice_
    attribution_block()`→`b1prod.run_fact_checker()`[内部で`r3.build_
    fact_check_prompt()`を呼ぶ]）で実行する。Production側`runner.
    run_fact_check_b1()`は`registry.is_fact_attribution_mode_enabled(
    "b_family_voices")`をハードコード呼び出ししており、Production
    registryのfact_attribution_mode既定Falseのままではopt-in ONを再現
    できないため、本関数はTrial側の判定(`is_fact_attribution_mode_
    enabled_trial()`、上記TRIAL_EDITORIAL_TYPE_4V)でON/OFFを決めたうえで、
    `registry.build_voice_attribution_block()`・`b1prod.run_fact_checker()`
    という同一のProduction関数を直接呼び出す(Production関数自体は無
    変更、`runner.run_fact_check_b1()`という関数名を経由していないだけで
    呼び出しチェーンの実体[build_voice_attribution_block→run_fact_checker
    →build_fact_check_prompt]は同一)。"""
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    enabled = is_fact_attribution_mode_enabled_trial(TRIAL_EDITORIAL_TYPE_4V)
    block = registry.build_voice_attribution_block(ledger_text) if enabled else ""
    with open(f"{out_dir}/audit/voice_attribution_block_used.txt", "w", encoding="utf-8") as f:
        f.write(block if block else "(fact_attribution_mode_enabled=False、blockは空文字列)")
    # build_fact_check_prompt自体はpure(API呼び出しなし)なので、実際に
    # b1prod.run_fact_checker内部で使われるprompt全文を、追加コスト無しで
    # 事前に同一関数を呼び出して証跡保存する(Opusレビュー1-MED「ON実行時
    # の実block文字列をファイル保存」に対応)。
    fc_prompt_for_evidence = r3.build_fact_check_prompt(TOPIC_JA, article_text, [], voice_attribution_block=block)
    with open(f"{out_dir}/audit/fact_check_prompt_with_attribution.txt", "w", encoding="utf-8") as f:
        f.write(fc_prompt_for_evidence)

    print(f"[4V-ARTICLE-TRIAL-01] Fact Checker A'呼び出し開始(fact_attribution_mode_enabled={enabled})...")
    fc_record = b1prod.run_fact_checker(TOPIC_JA, article_text, voice_attribution_block=block)
    fc_record["fact_attribution_mode_enabled"] = enabled
    with open(f"{out_dir}/fact_qa.json", "w", encoding="utf-8") as f:
        json.dump(fc_record, f, ensure_ascii=False, indent=2, default=str)
    print(f"[4V-ARTICLE-TRIAL-01] Fact Checker A'完了。final_status={fc_record.get('final_status')} "
          f"verdict={(fc_record.get('result') or {}).get('verdict')}")
    return fc_record


# ============================================================
# B Family Common Skeleton(Layer2)+ Voices Focus Module(Layer3)、
# ANCHOR挿入方式(Trial-04/05/07と同じ手法、Production側template自体は
# 変更しない)。
# ============================================================
ANCHOR = "【Spoken-first原則(数字の扱い)】"

B_FAMILY_VOICES_4V_FOCUS_MODULE_BLOCK = """【B Family Voices/Perspective Focus Module(4 Voices版、EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01。
Production未採用、この記事タイプ専用の骨格再定義。2 Voices版[Trial-07]を土台に4 Voicesへ拡張した）】
この記事は、上記で説明されている「Main Story / Point One・Point Two / In One Line」という
一般的な役割定義とは異なる、Voices/Perspective(実在する複数の立場を並立させ、その違いの
奥にあるTensionを発見し、一段深い理解へ着地する)という別の記事タイプです。今回は2人ではなく
**4人**の立場を並立させます。以下は、上記の一般的な役割定義・見出し構成を置き換えるのでは
なく、この記事に限り、それぞれのslotが何を担い、どのMarkdown見出しで書くかを、より具体的に
上書きする指示です。今回の記事では、以下の役割定義・出力形式を最優先で守ってください。

【最重要・この記事だけの出力形式(7区切り構造、厳守)】
上記「記事構成」節にある「Markdownの###見出しをちょうど2つ置く」という指示は、この記事
では次のように解釈してください: ###(レベル3見出し)は必ずちょうど**4つ**だけ使い、それぞれ
1人目・2人目・3人目・4人目のVoiceの見出しとしてのみ使ってください。それに加えて、##(レベル2
見出し)を3つ使い、Hook・Tension・Closingの見出しとしてください。記事全体は、必ず次の**7つ**
のMarkdown区切りを、この順序で持ってください(見出し文言は下の例を基本としつつ、内容に応じて
自然に言い換えてかまいませんが、4つのVoice見出しには、「ここから別のVoiceが始まる」と聞き手に
伝わる表現("Voice One:" "Another Voice:" "A Third Voice:" "A Fourth Voice:"のような形、または
その人物が何者かを示す語[the applicant/the recruiter/...]を使った自然な表現)を必ず含めて
ください。"Voice 1"/"Voice A"のような固定ラベル・番号ラベル、賛成/反対のような対称的なラベルは
禁止です):

# [Title]

## The Question
[Hookの本文]

### [1人目のVoiceの見出し。その人物・立場が何者かが伝わる短いフレーズ]
[1人目のVoice(Applicant)の本文]

### [2人目のVoiceの見出し]
[2人目のVoice(Recruiter・Hiring Manager)の本文]

### [3人目のVoiceの見出し]
[3人目のVoice(Business・Efficiency)の本文]

### [4人目のVoiceの見出し]
[4人目のVoice(Fairness・Legal・HR Governance)の本文]

## [Tensionの見出し。例: "Why They See It Differently"]
[Tensionの本文]

## [Closingの見出し。例: "What This Tells Us"]
[Closingの本文]

Tensionは、4人目のVoiceの本文の続きの段落ではなく、独立した見出しを持つ独立したセクション
として書いてください。

【見出しは合計ちょうど7つ、これ以外の見出しを追加しないこと(重要、厳守)】
記事全体のMarkdown見出し(#・##・###のいずれも)は、上記の7つ(Title含めると8つ、Titleの
#は別枠)だけにしてください。以下は禁止です:
- 記事の最後に「## In one line」やそれに類する結びの見出しを追加すること(この記事タイプ
  では、7つ目の見出し["Closingの見出し"]が結びの役割を兼ねます)
- Tensionセクション・Closingセクションの中に、新しいMarkdown見出し(###や##)をさらに
  追加すること(切り口が複数ある場合も、見出しで区切らず、地の文の中でひとつづきの文章
  として書いてください)
- Voice以外の要素(まとめ・補足・解決策等)のための追加の見出しを作ること
書き終えた後、Hook相当・4つのVoice相当・Tension相当・Closing相当の見出しがちょうど7つに
なっているか、自分で数え直してから出力してください。

【中心原則: Research is backstage. People are on stage.(2V版から継続)】
この記事の最大の失敗パターンは、Voiceのセクションが「調査結果を整理・説明する文章」に
なってしまうことです。あなたには、これから4枚のVoice Card(下記)を渡します。Voice Cardは、
Researchで確認された実在の人々の立場について、その人が何を経験し・何を必要とし・何を心配し・
何を守ろうとし・どんな条件からその考えに至っているかを、既にこちらで整理したものです。
**Voiceのセクションを書くときは、必ずVoice Cardの内容(その人の状況・必要・心配・守りたい
もの・具体的な場面)を主たる材料にして書き始めてください。Voice Cardの後に置かれている
Verified Fact Ledger(出典・数字を含む詳しいFact集)は、Fact Checker・Ledger Deviation
Checkのための正式な事実源であり続けますが、Voiceの文章を組み立てる際の「主役」ではありません。**
Evidence(調査・出典・統計)がVoiceの文章の主語になったり、Voiceの内容の中心になったりしては
いけません。

【この記事の4つのPerspectiveについて(重要な前提、賛否2対2を作らないこと)】
この記事の4つのVoiceは、単純な「賛成2人 vs 反対2人」のような対称的な2陣営には決して分解
できません。4人はそれぞれ、AIによる採用選考という同じ現象に対して、全く異なる役割・
異なる利害・異なる責任の重さから、異なる経験をしています。Voice 1(Applicant)は評価
される側、Voice 2(Recruiter・Hiring Manager)は実際にツールを使う側、Voice 3
(Business・Efficiency)は導入を判断する経営側、Voice 4(Fairness・Legal・HR Governance)
は事後に合法性・公平性を検証する側です。Voice 2・3はAIの効率性を実感していますが、Voice 2は
それに伴う「応募者の不信に応える」という実務負担も抱えており、Voice 3は効率化の裏で
「差別・評判リスク」という代償も意識しています。Voice 4は規制の必要性を語りますが、
地域によって規制の成熟度が異なるという別の緊張も抱えています。それぞれのVoiceを、単なる
「AI賛成派/反対派」の代弁者として単純化しないでください。それぞれの意見の背後にある、
具体的な経験・守りたいもの・立場上の制約まで、Voice Cardの内容を使って丁寧に描いてください。

【Voice Card 1(1人目のVoice。Applicant=AIスクリーニングを受ける応募者。この内容から
書き始めてください)】
- Person: 求職者として、企業の採用選考でAIによる評価(書類スクリーニング、適性・性格の
  自動採点、動画面接での表情・話し方の評価など)を受ける側の人。
- Situation(状況): 応募書類を送り、動画面接を受け、その評価の一部または全部をAIが行って
  いることを知っている、あるいは後から知る。
- Need(必要としていること): 自分の実力・人柄を正確に見てもらうこと、なぜ不採用になったのか
  理由を理解できること。
- Concern(心配していること): AIが人間の採用担当者より偏っている(biased)のではないかという
  広い不信感、人種・民族に基づく偏りが悪化するのではという懸念、異議を申し立てる手段が
  ないまま機械的に評価され不利益を受けるリスク。
- What they protect(守りたいもの): 公正に見てもらう機会そのもの、評価の理由を理解し
  納得できること。
- Why they feel this way(なぜそう感じるのか、経験・条件): 実際に、スキル評価では良い
  結果を出したにもかかわらず、AIによる動画面接評価で身振り・表情を低く採点されて不採用と
  なり、その後長期の失業状態に陥ったと証言する女性求職者の実例がある。また、ある応募者は
  AIによる「信頼性・誠実さ」スコアリングを、オプトアウトも異議申し立てもできないまま
  受けさせられたとして提訴した実例もある。
- Constraint(制約): 選考プロセスにAIが使われるかどうか、どう使われるかについて発言権を
  持たない、判断される側の立場。
- Concrete lived scene(具体的な場面、Ledgerに根拠あり): 動画面接で、ソフトウェアが自分の
  声のトーン・表情・身振りをスコアリングしていると知りながら話す、あるいは、なぜ次の段階へ
  進めなかったのか説明のないまま結果だけを受け取る。resource: [VOICE_1_EVIDENCE 1-03]
  (BBC Worklife、動画面接評価で低評価となり長期失業に陥った女性求職者)、
  [VOICE_1_EVIDENCE 1-04](CVS Health応募者、HireVue/Affectivaの表情・声のトーン分析を
  オプトアウトも異議申し立てもできないまま受け提訴)。
- Supporting evidence(裏付け専用、Voice本文の主役にしない): 米国の就労中求職者の49%が
  AIツールは人間より偏っていると考えている[VOICE_1_EVIDENCE 1-01]、米国成人の約79%が
  AIによる人種・民族の偏り悪化を懸念している[VOICE_1_EVIDENCE 1-02]。この裏付けの中から、
  1つのVoiceにつき最大1つの具体的な数字だけを、人を主語にした自然な話し言葉で織り込んで
  ください(詳細ルールは下記【Voice内の数字】参照)。

【Voice Card 2(2人目のVoice。Recruiter・Hiring Manager=実際にAIツールを使う、または
使うかどうかを判断する採用担当・人事責任者。この内容から書き始めてください)】
- Person: 採用業務を実際に担当し、履歴書スクリーニング・面接日程調整・求人票作成などの
  複数の業務段階で日常的にAIツールを使っている人。
- Situation(状況): 大量の応募者を効率的に処理する必要がある一方、応募者側のAIへの不信に
  日々向き合っている。
- Need(必要としていること): 大量の応募を効率的に処理すること、候補者を適切な職種に
  マッチングさせること。
- Concern(心配していること): 応募者側の不信(Voice 1)に応えるために、バイアス監査結果や
  透明性資料を用意しなければならないという実務上のプレッシャー、応募者自身がAIを使って
  書いた応募書類をどう評価すべきか判断が割れていること(AI活用力の証と見るべきか、努力
  不足の表れと見るべきか)。
- What they protect(守りたいもの): 効率的に仕事を進める能力と、それに伴う説明責任を
  同時に果たすこと。
- Why they feel this way(なぜそう感じるのか、経験・条件): 実際に大手雇用主(NBCUniversal)が
  ニューヨーク市の法律に基づき、使用するAIツールについて独立監査を受け、その結果を公開
  している実例があり、採用担当者は「使えば便利だが、説明責任も伴う」という板挟みの中で
  日々判断している。
- Constraint(制約): 会社としてAIを導入するかどうかの最終決定権は無く(それはVoice 3の
  領域)、既に導入されたツールを日々運用しながら、応募者の不信にも規制にも対応しなければ
  ならない「現場」の立場。
- Concrete lived scene(具体的な場面、Ledgerに根拠あり): 履歴書スクリーニングソフトを
  使って大量の応募を処理した後、応募者からの疑問に答えるためのバイアス監査の要約資料を
  準備する。resource: [VOICE_2_EVIDENCE 2-04](NBCUniversalのAEDT通知、独立監査の実施)、
  [VOICE_2_EVIDENCE 2-05](採用担当者が応募者の不信に文書で応える実務上のプレッシャー)。
- Supporting evidence(裏付け専用): HRリーダーの91%が採用プロセスで実際にAIを使っている
  [VOICE_2_EVIDENCE 2-01]、採用担当者の87%が採用プロセスの少なくとも1段階でAIを使用
  [VOICE_2_EVIDENCE 2-03]。この裏付けの中から、1つのVoiceにつき最大1つの具体的な数字
  だけを、人を主語にした自然な話し言葉で織り込んでください。

【Voice Card 3(3人目のVoice。Business・Efficiency=コスト・採用スピード・スケーラビリティの
観点から評価する経営・事業効率の担当者。この内容から書き始めてください)】
- Person: 経営者・事業責任者として、AI採用選考の導入可否を、コスト・スピード・
  スケーラビリティの観点から評価する人。
- Situation(状況): 採用にかかる時間・コストの指標を見ながら、AI導入によって何がどれだけ
  変わったかを追っている。
- Need(必要としていること): 事業を回すのに十分な速さ・十分な規模で人を採用しつつ、
  コストを持続可能な水準に保つこと。
- Concern(心配していること): 効率化のメリットと、差別が生じた場合の法的リスク・企業の
  評判(reputation)への打撃という代償を天秤にかけなければならないこと。
- What they protect(守りたいもの): 会社が採用をスケールさせ続ける能力と、会社の評判。
- Why they feel this way(なぜそう感じるのか、経験・条件): 実際に、業種・規模の異なる
  複数の企業(ホテルチェーン、ITベンダー、クラウド企業)で、AI導入後に採用期間が数週間から
  数日へ大幅に短縮された、あるいはコストが大きく下がったという事例が積み重なっている。
- Constraint(制約): 法規制の詳細や応募者側の不信をゼロから作り出す立場ではないが、
  AIを導入する・使い続けるという決定そのものの責任と、それが裏目に出た場合の結果を
  引き受ける立場。
- Concrete lived scene(具体的な場面、Ledgerに根拠あり): 採用にかかる日数・コストの
  ダッシュボードを見て、AI導入後の改善を確認する一方で、偏りが公になった場合の見出しに
  なりうるリスクも同時に意識している。resource: [VOICE_3_EVIDENCE 3-01](ホテルチェーンの
  採用期間が約6週間から5日間へ短縮)、[VOICE_3_EVIDENCE 3-05](差別が生じた場合の倫理的・
  法的リスクと評判へのダメージ)。
- Supporting evidence(裏付け専用): 企業の57%が既に採用選考でAIを使用し、74%がAIによって
  採用の質が向上したと回答[VOICE_3_EVIDENCE 3-04]。この裏付けの中から、1つのVoiceにつき
  最大1つの具体的な数字だけを、人を主語にした自然な話し言葉で織り込んでください。

【Voice Card 4(4人目のVoice。Fairness・Legal・HR Governance=合法性・公平性・監査可能性を
検証する弁護士・規制当局・HRガバナンス専門家。この内容から書き始めてください)】
- Person: 弁護士・規制当局・HRガバナンス専門家として、AI採用選考の合法性・公平性・監査
  可能性を事後に検証する人。
- Situation(状況): 既に広く使われているAI採用ツールについて、法規制への適合・監査記録・
  過去の失敗事例を確認している。
- Need(必要としていること): 応募者が不当に差別されないこと、AIの意思決定過程が監査可能で
  あること、企業に説明責任を持たせること。
- Concern(心配していること): 地域・国によって規制の成熟度に大きな差があること(ニューヨーク
  市やEUには具体的な監査義務があるが、日本にはまだ同等の法律がない)。
- What they protect(守りたいもの): 応募者が差別されない権利、監査プロセスの実効性。
- Why they feel this way(なぜそう感じるのか、経験・条件): 実際に、過去の採用データから
  学習したAIが女性を不利に評価するようになった社内ツールが中止された事例、動画面接
  ツールが生体情報プライバシー法違反で和解に応じた事例など、監査されないまま使われた
  AIが実害を生んだ実例が既に存在し、それがニューヨーク市の年次バイアス監査義務やEU AI
  Actの高リスク分類という具体的な法規制を生む土壌になっている。
- Constraint(制約): AIツールを自ら作る・使う立場ではなく、既に広く使われた後に事後的に
  線引きをする側であり、企業の導入スピードと規制の整備スピードのずれの中で仕事をしている。
- Concrete lived scene(具体的な場面、Ledgerに根拠あり): 企業が公開したバイアス監査の
  開示資料を確認する、あるいは何年も後になって、当時は監査されなかったツールが実害を
  生んでいたことを訴訟記録から知る。resource: [VOICE_4_EVIDENCE 4-01](ニューヨーク市
  Local Law 144、年次バイアス監査義務)、[VOICE_4_EVIDENCE 4-03](Amazonの社内採用
  ツールが女性を不利に評価し中止された事例)。
- Supporting evidence(裏付け専用): EU AI Actは採用のためのAIシステムを「high-risk」に
  分類している[VOICE_4_EVIDENCE 4-02]。この裏付けの中から、1つのVoiceにつき最大1つの
  具体的な数字だけを、人を主語にした自然な話し言葉で織り込んでください。

【Voiceの書き始め方(重要、2V版から継続)】
Voiceの本文は、"For [a/an] applicant who..."のような、その人物のことを外側から要約・紹介
する文で始めないでください。代わりに、Voice Cardが示す具体的な状況(その人が実際に毎日
していること・直面していること・使っているもの、目にする光景)から書き始め、そこからその
人の感覚・必要性が自然に浮かび上がるようにしてください。反論のための藁人形にしないで
ください。

【Narrator(語り手)がVoiceの人物を外側から要約・分析しないこと(重要、2V版から継続)】
Voiceのセクション内で、語り手がその人物の必要・感情・責任を外側から定義づけるような文
("The need is...", "She is protecting...", "This person must choose between..."のような、
Voiceの人物を三人称で要約・分析する文)を書かないでください。すべての文は、その人が実際に
その瞬間にしていること・気づいていること・感じていることの描写として書いてください。

【Evidenceは脇役であること・Voice内の数字は最大1つ(重要、2V版から継続)】
1つのVoiceの中で、Evidenceの紹介そのものが主役になる文を連続させないでください。文の
主語が調査・報告・データ("A survey found...", "One report described...", "The data
show...")になる文は書かないでください。1つのVoiceのセクション全体を通して、具体的な数字は
最大1つだけにし、必ずその人/その立場の人々の実感に折り込み、話し言葉で書いてください。
4人全員について同じルールを適用してください。

【トーン(重要)】
この記事は、業界レポート・コンサルティングメモ・分析的なブリーフィングのような読み味に
しないでください。Light・conversational・human-centeredに、友人に説明するような、気軽に
読める文章にしてください。

【Hookの役割と書き方(重要)】
Hook("## The Question")は、これから4つの立場を紹介するテーマ・状況を簡潔に提示する
導入です。どの立場が正しいかを示唆したり、結論を先取りしたりしないでください。目安は
80語未満です。読み手へ呼びかけたり、命令形・二人称で想像を促したりする表現("Imagine...",
"Picture...", "Think about...", "Consider...")で始めないでください。代わりに、具体的な
情景そのものから、三人称で書き始めてください(例: ある応募者が採用選考の一場面に直面する
情景、AIツールが応募書類を処理する情景など)。Hookに企業名・統計・パーセントを入れないで
ください。

【Voice以外の場面(Tension)で第三者の視点・解決策を混ぜないこと(重要)】
各Voiceのセクションでは、その当事者がどう感じ、何を必要としているかを描き切ってください。
解決策・妥協案・提案は、この記事では基本的に書かないでください(Solution articleでは
ありません)。

【Tensionの役割(重要、4Voices版で新規設計。2軸交差ベース)】
「どの立場が正しいか」を決めようとしないでください。そうではなく、なぜ4人全員が、それぞれの
立場からは合理的に見えるのかを掘り下げてください。**Tensionの中心は、あくまでVoice Cardに
描かれている4人の人物であり、Evidence(survey/research/data/percentage)ではありません。**
Tensionの段落を、"A survey found...", "The data show..."のような、調査・データそのものを
主語にした文で始めたり、その説明へ立ち戻ったりしないでください。以下の2つの軸の交差として
4人の違いを掘り下げてください(これは執筆時の思考の補助であり、本文に「軸1」「軸2」という
ラベルをそのまま書く必要はありません):
- 軸1: 当事者性の強さ(この状況の結果を直接その身に引き受けるか、それとも決定・監督する側
  かという違い)。Applicantは当事者性が最も強く(結果を直接引き受ける側)、Business・
  Efficiencyは当事者性が最も弱く(決定する側)、Recruiter・Hiring Managerは中間(現場で
  日々運用する側)、Fairness・Legal・HR Governanceも中間(事後に検証する側)に位置します。
- 軸2: AI活用への態度(推進寄りか慎重寄りか)。Business・Efficiencyは最も推進寄り、
  Applicantは最も慎重寄り、Recruiter・Hiring Managerは実務上の便益を実感しつつ説明責任の
  重さも感じる両義的な立場、Fairness・Legal・HR Governanceは公平性・合法性の観点から
  慎重寄りです。
単純に4人の主張を時系列で繰り返し要約するのではなく、それぞれが「何を賭けている」のか
(Applicantにとっては機会そのものを失うこと、Recruiter・Hiring Managerにとっては効率と
説明責任の両立、Business・Efficiencyにとっては採用の速さ・規模を保てるかどうか、
Fairness・Legal・HR Governanceにとっては監査可能性・合法性を保証できるかどうか)という
非対称性として描いてください。**4人を単純に「賛成2人 vs 反対2人」のような2つの陣営へ
分けないでください。** 単に「みんなそれぞれの立場から正しい」とまとめるだけの記述にも
しないでください。解決策の提案はここでも基本的に行わないでください。Verified Fact
Ledgerに無い新しい因果関係・新しい事実を作り出さないでください。

【Closingの役割(重要、2V版から継続)】
これは要約でも、In One Lineの言い換えでもありません。4つのVoiceを見たことによって、この
問題そのものの見え方が、Hook(冒頭の問い)の時点からどう変わったかを書いてください。「AIに
賛成の人も反対の人もいる」「人による」というだけの結び方で終わらせないでください。目指す
のは、この問題が実は何についての問題なのかを一段深く見せることです。Writer自身の解決策・
コンサル提案にはしないでください。Closingの最初の役割は要約ではなく再定義です。前段
(4つのVoice・Tension)の内容の要約から書き始めないでください。

【各Voiceは同じ意味を2回言わないこと】
1つの経験・1つの感覚は、そのVoiceの中で1回だけ描写してください。

【記事全体の長さについて(この記事専用、hard capではない。4V設計目標、design.md B-6の
未検証monitoring値380〜430秒[尺]の語数換算に基づく、後述の語数・尺見積り参照)】
記事全体の総語数は、**約400語をsoft targetとしてください**(hard capではありません)。
目安配分(soft guidance): Hook 55〜65語程度 / 各Voice 60〜75語程度(4人合計約260〜290語)/
Tension 65〜80語程度 / Closing 40〜55語程度。この配分は目安であり、自然な文章の流れ・
Tension/Closingの深さを犠牲にしてまで厳密に一致させる必要はありません。

【禁止事項まとめ(この記事全体を通して)】
- Reference Example由来の定型的な呼びかけ表現をコピー・準用すること
- "Voice 1"/"Voice A"のような固定ラベル・番号ラベル
- 文の主語がEvidence(survey/report/data/study)になる文(Tensionの段落を含む)
- Narrator(語り手)がVoiceの人物を外側から要約・分析する文
- Voiceのセクションへ第三者(設計者・コンサルタント)の視点を持ち込むこと、または
  どのVoiceの人物であっても具体的な解決策・妥協案をVoice本文内・Tension・Closing内で
  提案すること
- Hookに企業名・統計・パーセントを入れること
- 1つのVoiceのセクション内で具体的な数字を2つ以上使うこと
- 4人を単純に「賛成2人 vs 反対2人」のような対称的な2陣営へ分けること
- Closingを「人による」という結び方だけで終わらせること"""


def build_candidate_template() -> str:
    assert ANCHOR in gen.COMMON_BLOCK_TEMPLATE, (
        "アンカー文字列がgen.COMMON_BLOCK_TEMPLATE内に見つかりません。Production側のtemplateが"
        "本Trial設計時から変更されている可能性があるため中断してください(STOP条件)。")
    assert gen.COMMON_BLOCK_TEMPLATE.count(ANCHOR) == 1, (
        "アンカー文字列が複数回出現しています。挿入位置が一意に定まらないため中断してください。")
    return gen.COMMON_BLOCK_TEMPLATE.replace(
        ANCHOR, B_FAMILY_VOICES_4V_FOCUS_MODULE_BLOCK + "\n\n" + ANCHOR, 1)


def build_candidate_prompt(candidate_template: str, master_full_text: str, topic: str,
                            verified_ledger_text: str, instruction: str) -> str:
    # Reconciliation finding(本Trial実行時に新規発見): gen.COMMON_BLOCK_TEMPLATEは
    # OPEN-112-TREND-SYNTHESIS-MODE-PRODUCTION-WIRING-01でTrial-07作成後に
    # `{editorial_type_module_block}` placeholderが追加されており、Trial-07の
    # build_candidate_prompt()と同じ`.format()`呼び出し方法だと今日実行すると
    # KeyErrorになる(Trial-07自体は無変更のまま、今日再実行すれば同じ現象が
    # 起きる、Production側の後方互換設計[gen.build_common_block()の既定値
    # editorial_type_module_block=""]に合わせてここでは明示的に""を渡す)。
    common_block = candidate_template.format(
        hanshin_master_full_text=master_full_text, topic=topic,
        verified_ledger_text=verified_ledger_text,
        shared_point_blueprint_block="", evidence_compression_block="",
        editorial_type_module_block="")
    return gen.build_prompt(common_block, instruction)


def run_phase_a(audit_dir: str) -> dict:
    os.makedirs(audit_dir, exist_ok=True)
    candidate_template = build_candidate_template()
    with open(f"{audit_dir}/phase_a_candidate_template.txt", "w", encoding="utf-8") as f:
        f.write(candidate_template)
    with open(f"{audit_dir}/phase_a_focus_module_block.txt", "w", encoding="utf-8") as f:
        f.write(B_FAMILY_VOICES_4V_FOCUS_MODULE_BLOCK)

    reconstructed = gen.COMMON_BLOCK_TEMPLATE.replace(
        ANCHOR, B_FAMILY_VOICES_4V_FOCUS_MODULE_BLOCK + "\n\n" + ANCHOR, 1)
    clean_single_insert = (reconstructed == candidate_template)
    result = {"clean_single_insert_confirmed": clean_single_insert,
              "baseline_len": len(gen.COMMON_BLOCK_TEMPLATE), "candidate_len": len(candidate_template)}
    with open(f"{audit_dir}/phase_a_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[4V-ARTICLE-TRIAL-01][Phase A] clean_single_insert_confirmed={clean_single_insert}")
    return {"result": result, "phase_a_pass": clean_single_insert, "candidate_template": candidate_template}


# ============================================================
# 7区切り構造(Hook/Voice 1/Voice 2/Voice 3/Voice 4/Tension/Closing)専用
# parser(Trial-07 split_five_voice_sections()の4V版。Production側の
# split_common_sections_for_point_qa()・split_five_voice_sections()は
# いずれも5見出し構造専用でこの7見出し構造を解釈できないため、Trial側で
# 新規実装する)。
# ============================================================
_HEADING_RE = re.compile(r"^(#{2,3})[ \t]+(.+?)\s*$", re.MULTILINE)
SEVEN_SECTION_LABELS = ("hook", "voice_1", "voice_2", "voice_3", "voice_4", "tension", "closing")


def split_seven_voice_sections(article_text: str) -> dict | None:
    """7区切り構造を見出し出現順(Hook/Voice 1/Voice 2/Voice 3/Voice 4/
    Tension/Closing)に抽出する。ちょうど7つの##または###見出しがTitleの
    後に連続して登場することを前提とする。想定外の場合はNoneを返す。"""
    title_match = re.match(r"^#[ \t]+.+?\s*\n", article_text)
    if not title_match:
        return None
    body = article_text[title_match.end():]
    matches = list(_HEADING_RE.finditer(body))
    if len(matches) != 7:
        return None
    result = {}
    for i, label in enumerate(SEVEN_SECTION_LABELS):
        heading_text = matches[i].group(2).strip()
        heading_level = len(matches[i].group(1))
        content_start = matches[i].end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        result[f"{label}_heading"] = heading_text
        result[f"{label}_heading_level"] = heading_level
        result[f"{label}_body"] = body[content_start:content_end].strip()
    preamble = body[:matches[0].start()].strip()
    result["unexpected_preamble_before_first_heading"] = preamble
    return result


def seven_section_length_report(article_text: str) -> dict | None:
    sections = split_seven_voice_sections(article_text)
    if sections is None:
        return None
    counts = {key: ab01.compute_word_count(sections[f"{key}_body"]) for key in SEVEN_SECTION_LABELS}
    counts["total_of_seven_sections"] = sum(counts.values())
    counts["headings"] = {key: sections[f"{key}_heading"] for key in SEVEN_SECTION_LABELS}
    counts["unexpected_preamble_before_first_heading"] = sections["unexpected_preamble_before_first_heading"]
    return counts


# ============================================================
# Point Overlap QA(monitoring専用、4V版、Opusレビュー2-HIGH/3-MED対応):
# lexical_overlap_ratio()は非対称指標(|A∩B|/|A|)のため、有向ペアで
# 計算する。4 Voice間の有向ペアはPermutation(4,2)=12、各VoiceとHookとの
# 比較(Voiceを基準、Hookを比較対象)4を加えて合計16値。合否判定には
# 使わない(記録のみ、N=1で閾値を決めない)。
# ============================================================
def run_overlap_monitoring_4v(sections: dict, out_dir: str) -> dict:
    voice_keys = ("voice_1", "voice_2", "voice_3", "voice_4")
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
        "note": ("EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01: monitoring専用(合否判定には"
                 "使わない、N=1で閾値を決めない、Opusレビュー3-MED)。有向ペア12(Permutation"
                 "(4,2))+ vs Hook 4 = 16値。lexical_overlap_ratio()はProduction関数"
                 "(er008_point_overlap_qa_18.py)を無変更のまま使用。"),
        "directed_voice_pair_count": len(directed_voice_pairs),
        "voice_vs_hook_count": len(voice_vs_hook),
        "total_values": len(directed_voice_pairs) + len(voice_vs_hook),
        "any_flagged": any(all_flags),
        "directed_voice_pairs": directed_voice_pairs,
        "voice_vs_hook": voice_vs_hook,
    }
    with open(f"{out_dir}/point_overlap_qa_monitoring_4v.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[4V-ARTICLE-TRIAL-01] Overlap monitoring(16値)完了。any_flagged={summary['any_flagged']}")
    return summary


# ============================================================
# Analytical Leakage Check(4V版、Opusレビュー2-HIGH対応): Production側
# ANALYTICAL_LEAKAGE_JSON_SCHEMA(er012_b_family_voices_a2_production_01.py)
# はvoice_a/voice_b固定・additionalProperties:False・strict:Trueのため
# 4Voiceでは使えない。Trial側で新規スキーマ・promptを作成する(2V版
# [Trial-07]と同じ6/5/1基準を土台に、4V版ではTensionに「賛否2対2分割」
# 検知項目を追加する)。
# ============================================================
VOICE_LEAKAGE_FIELDS = (
    "leak_evidence_subject", "leak_numbers_foreground", "leak_narrator_analysis",
    "leak_unknowable_analysis", "leak_discovery_syntax", "leak_evidence_memorable",
)
TENSION_LEAKAGE_FIELDS = (
    "leak_evidence_subject", "leak_numbers_foreground", "leak_discovery_syntax",
    "leak_evidence_memorable", "leak_tension_reverts_to_research",
    "leak_binary_camp_split",  # 4V新規: 4人を単純に賛成2人vs反対2人に分けていないか
)
CLOSING_LEAKAGE_FIELDS = ("leak_closing_simple_summary",)

LEAKAGE_CHECK_DEVELOPER_MESSAGE = (
    "あなたは'Voices/Perspective'型記事(4 Voices版)のVoice section・Tension section・"
    "Closing sectionを審査する、厳格なEditorial QA判定者です。それぞれのsectionが、実在する"
    "当事者(人)の経験・価値観・必要・心配として書かれているか、あるいは調査結果・データを"
    "整理して説明する文章、単なる要約、Writer自身の解決策提案、単純な2陣営分割に戻っていないかを、"
    "各section指定の基準についてPASS/FAILで判定してください。各基準についてPASSは『問題なし』、"
    "FAILは『その問題が実際に本文に存在する』ことを意味します。FAILの場合は、該当する原文の"
    "一節をquoted_evidenceにそのまま引用してください(複数箇所ある場合は代表的な1〜2箇所)。"
    "PASSの場合はquoted_evidenceを空文字列にしてください。"
)


def _leakage_item_schema(fields: tuple[str, ...]) -> dict:
    props = {f: {"type": "string", "enum": ["PASS", "FAIL"]} for f in fields}
    props["reasoning"] = {"type": "string"}
    props["quoted_evidence"] = {"type": "string"}
    return {"type": "object", "properties": props, "required": list(props.keys()), "additionalProperties": False}


ANALYTICAL_LEAKAGE_JSON_SCHEMA_4V = {
    "name": "analytical_leakage_check_4v",
    "schema": {
        "type": "object",
        "properties": {
            "voice_1": _leakage_item_schema(VOICE_LEAKAGE_FIELDS),
            "voice_2": _leakage_item_schema(VOICE_LEAKAGE_FIELDS),
            "voice_3": _leakage_item_schema(VOICE_LEAKAGE_FIELDS),
            "voice_4": _leakage_item_schema(VOICE_LEAKAGE_FIELDS),
            "tension": _leakage_item_schema(TENSION_LEAKAGE_FIELDS),
            "closing": _leakage_item_schema(CLOSING_LEAKAGE_FIELDS),
        },
        "required": ["voice_1", "voice_2", "voice_3", "voice_4", "tension", "closing"],
        "additionalProperties": False,
    },
    "strict": True,
}

LEAKAGE_CHECK_PROMPT_TEMPLATE_4V = """以下は、あるVoices/Perspective型記事(4 Voices版)の6つのsection本文
(Voice 1〜4/Tension/Closing)です。それぞれについて、指定された項目を判定してください
(それぞれPASS/FAIL)。

【Voice 1〜4に共通で適用する6項目】
- leak_evidence_subject: 文の主語がsurvey/research/data/percentageになっている文が無い場合PASS
- leak_numbers_foreground: 具体的な数字・比較結果が、その人の経験の描写より前面に出ていない場合
  PASS(数字が0個、または1個だけがその人の実感として自然に織り込まれている場合はPASS)
- leak_narrator_analysis: Narrator(語り手)が、Voiceの人物を外側から分析・要約していない場合PASS
- leak_unknowable_analysis: その人物自身が実際に考え・言いそうにない、外部の分析的視点を、その人の
  Perspectiveとして書いていない場合PASS
- leak_discovery_syntax: Discovery/Trend記事のような文構造へ戻っていない場合PASS
- leak_evidence_memorable: Evidenceよりもその人物の経験・感情の方が記憶に残る書き方になっている場合PASS

【Tensionに適用する6項目】
- leak_evidence_subject / leak_numbers_foreground / leak_discovery_syntax / leak_evidence_memorable:
  上記と同じ意味(Tension本文に対して判定)
- leak_tension_reverts_to_research: Tensionの中心が、4人がなぜ違う答えに至るのかの掘り下げになって
  おり、survey/研究データそのものの説明・比較へ戻っていない場合PASS
- leak_binary_camp_split: Tensionが4人を単純に「賛成2人 vs 反対2人」のような対称的な2つの陣営へ
  分けて描いていない場合PASS(分けている場合FAIL)

【Closingに適用する1項目】
- leak_closing_simple_summary: Closingが、単なる要約や「人による」という結び方だけで終わっておらず、
  かつWriter自身の解決策・妥協案の提案になっていない場合PASS

reasoningには、判定理由を1〜2文の日本語で書いてください。FAILの場合はquoted_evidenceに該当する
原文を引用してください(英語本文をそのまま引用してよい)。PASSの場合quoted_evidenceは空文字列に
してください。

【Voice 1本文】
{voice_1_body}

【Voice 2本文】
{voice_2_body}

【Voice 3本文】
{voice_3_body}

【Voice 4本文】
{voice_4_body}

【Tension本文】
{tension_body}

【Closing本文】
{closing_body}
"""


class LeakageCheckModelMismatchError(RuntimeError):
    pass


_LEAKAGE_SECTION_FIELDS_4V = {
    "voice_1": VOICE_LEAKAGE_FIELDS, "voice_2": VOICE_LEAKAGE_FIELDS,
    "voice_3": VOICE_LEAKAGE_FIELDS, "voice_4": VOICE_LEAKAGE_FIELDS,
    "tension": TENSION_LEAKAGE_FIELDS, "closing": CLOSING_LEAKAGE_FIELDS,
}


def run_analytical_leakage_check_4v(client, sections: dict, model: str, reasoning_effort: str,
                                     out_dir: str, attempt: int) -> dict:
    prompt = LEAKAGE_CHECK_PROMPT_TEMPLATE_4V.format(
        voice_1_body=sections["voice_1_body"], voice_2_body=sections["voice_2_body"],
        voice_3_body=sections["voice_3_body"], voice_4_body=sections["voice_4_body"],
        tension_body=sections["tension_body"], closing_body=sections["closing_body"])
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **ANALYTICAL_LEAKAGE_JSON_SCHEMA_4V}},
        input=[
            {"role": "developer", "content": LEAKAGE_CHECK_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    if response.model != model:
        raise LeakageCheckModelMismatchError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    text = getattr(response, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Analytical Leakage Check応答が空です")
    parsed = json.loads(text)

    flagged_items = []
    for section_key, fields in _LEAKAGE_SECTION_FIELDS_4V.items():
        item = parsed[section_key]
        fail_fields = [f for f in fields if item[f] == "FAIL"]
        if fail_fields:
            flagged_items.append({"voice": section_key, "fail_fields": fail_fields,
                                   "reasoning": item["reasoning"], "quoted_evidence": item["quoted_evidence"]})
    result = {
        "model": response.model, "response_id": response.id, "prompt": prompt, "parsed": parsed,
        "flagged_items": flagged_items, "any_flagged": bool(flagged_items),
    }
    with open(f"{out_dir}/analytical_leakage_check_4v_attempt{attempt}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[4V-ARTICLE-TRIAL-01][Leakage Check] attempt{attempt}: any_flagged={result['any_flagged']} "
          f"flagged_items={[(x['voice'], x['fail_fields']) for x in flagged_items]}")
    return result


def build_leakage_corrective_note_4v(leakage_result: dict) -> str:
    lines = [
        "【Analytical Leakage Check是正メモ(前回attemptの検出結果。Voice Card・Verified "
        "Fact Ledger・骨格は変更しません。今回はこの記事全文をゼロから新しく書き直して"
        "ください。前回の文をそのまま部分修正するのではなく、Voice Cardの内容から書き始め、"
        "以下の問題を避けてください)】",
    ]
    voice_label = {"voice_1": "Voice 1(Applicant)", "voice_2": "Voice 2(Recruiter/Hiring Manager)",
                   "voice_3": "Voice 3(Business/Efficiency)", "voice_4": "Voice 4(Fairness/Legal/HR Governance)",
                   "tension": "Tension", "closing": "Closing"}
    for item in leakage_result["flagged_items"]:
        lines.append(f"- {voice_label[item['voice']]}で検出: {', '.join(item['fail_fields'])}")
        lines.append(f"  理由: {item['reasoning']}")
        if item["quoted_evidence"]:
            lines.append(f"  該当箇所(この種の書き方を避ける): \"{item['quoted_evidence']}\"")
    lines.append(
        "\n【この記事全体で必ず守るContractの優先事項(是正のたびに毎回再掲)】\n"
        "- Compactness: 記事全体の総語数は約400語がsoft targetです(hard capではありません)。"
        "削るときはreplace-with-nothingを基本とし、削った直後に別の言い回しで同じ内容を書き足さないでください。\n"
        "- Tensionの役割: Tensionの中心はVoice Cardの4人の人物であり、Evidenceではありません。"
        "4人を単純に賛成2人vs反対2人へ分けないでください。\n"
        "- Closingの役割: 単なる要約や「人による」で終わらせず、この問題が実は何についての問題なのかという"
        "再定義そのものから書き始めてください。解決策の提案はしないでください。"
    )
    return "\n".join(lines)


# ============================================================
# Ledger Deviation Checker + Local Rewrite(Trial-07から呼び出し関数・
# 引数・順序を一切変更せずそのまま踏襲。article_textの内部構造[section数]
# に依存しない、記事全体テキストへの適用のためそのまま流用可能)。
# ============================================================
def run_ledger_deviation_and_local_rewrite(client, theme_id: str, label: str, article_text: str,
                                            verified_ledger_text: str, out_dir: str, ledger_model: str) -> dict:
    print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: ledger逸脱チェック開始(Hook-aware)...")
    deviation_result = vfl01.run_deviation_check(
        client, verified_ledger_text, article_text, model=ledger_model, hook_aware=True)
    print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: deviation overall_status="
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
        print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: Local Rewrite cycle {cycle}/"
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
            print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: cycle {cycle} NG item {idx}: "
                  f"resolved={r['resolved']} human_review={r['human_review_required']} attempts={len(r['attempts'])}")

        article_text = local_rewrite.apply_rewrites(article_text, cycle_results)
        article_text = gen.normalize_article_formatting(article_text)
        with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
            f.write(article_text)

        print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: cycle {cycle} Local Rewrite後、Ledger全体を再判定...")
        deviation_result = vfl01.run_deviation_check(client, verified_ledger_text, article_text,
                                                       model=ledger_model, hook_aware=True)
        recheck_major = [d for d in deviation_result["parsed"]["deviations"] if d["severity"] == "MAJOR"]
        print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: cycle {cycle} 再判定 overall_status="
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
# Reconciliation finding(本Trial実行時に新規発見、Opusレビュー未指摘の
# 追加failure mode): `gen._generate_and_compress_article()`は内部で
# `vfl01.run_writer_with_technical_retry()`→`er002_ja_free_markdown_
# restore_r2.validate_point_structure()`を呼ぶが、この関数は
# `h3_count != 2`を無条件でSTRUCTURE_INVALIDにする、Production全体で
# 共有される技術的構造ゲート(Trial-07[2V、###がちょうど2つ]では偶然
# 素通りしていたが、4Vは###がちょうど4つになるため必ず弾かれる、実測
# 確認済み: attempt1でstatus=STRUCTURE_INVALID_POINT_COUNT_OR_BODY・
# h3_count=4で実際に失敗した)。この汎用ゲートはB-Family Voices用途を
# 想定しておらず、変更にはProduction側の承認が必要なため本Trialでは
# 一切変更しない。代わりに、Production primitive `vfl01.run_writer_
# no_search()`(Web検索無し生成、無変更)を直接呼び、通信障害のみの
# 技術的retry(最大2回、Production既定と同じ回数)をTrial側で複製し、
# 構造検証は本ファイル独自の`split_seven_voice_sections()`(7見出し
# 限定)に委ねる(呼び出し元`run_voices_pattern_4v()`が担当)。
# ============================================================
def _generate_and_compress_article_4v(client, theme_id: str, label: str, prompt: str, out_dir: str,
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
        print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: writer技術的失敗(通信障害等)。")
        return {"status": "TECHNICAL_GENERATION_FAILED", "article_text": None}

    article_text, fact_usage_report = blueprint_mod.extract_trailing_metadata_block(raw_result["raw_text"].strip())
    if fact_usage_report is not None:
        with open(f"{out_dir}/audit/fact_usage_report.json", "w", encoding="utf-8") as f:
            json.dump(fact_usage_report, f, ensure_ascii=False, indent=2)

    evidence_compression_applied = False
    if apply_evidence_compression:
        with open(f"{out_dir}/audit/pre_editor_article.md", "w", encoding="utf-8") as f:
            f.write(article_text)
        print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: Evidence Compression(Lossless Editor)呼び出し開始...")
        editor_result = ec_editor.run_lossless_editor(client, article_text, model=model)
        with open(f"{out_dir}/audit/evidence_compression_editor_raw.json", "w", encoding="utf-8") as f:
            json.dump(editor_result, f, ensure_ascii=False, indent=2, default=str)
        if editor_result.get("raw_text"):
            article_text = editor_result["raw_text"]
            evidence_compression_applied = True
        print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: Evidence Compression完了。"
              f"response_id={editor_result.get('response_id')}")

    article_text = gen.normalize_article_formatting(article_text)
    with open(f"{out_dir}/article.md", "w", encoding="utf-8") as f:
        f.write(article_text)

    return {"status": "OK", "article_text": article_text, "fact_usage_report": fact_usage_report,
            "evidence_compression_applied": evidence_compression_applied}


# ============================================================
# Writer + Fact A' + Ledger Deviation + Directional Precheckの1 attempt分
# (Trial-07 run_voices_pattern_run03の4V版。Point Role Planningは
# 呼ばない[point_planning.run_point_role_planning/run_point_value_qaは
# point_one/point_two固定schemaのため4Voiceへ一般化できず、本Trialの
# 必須項目にも含まれないため意図的に省略、Reportに明記])。
# ============================================================
def run_voices_pattern_4v(client, theme_id: str, label: str, prompt: str, verified_ledger_text: str,
                           out_dir: str, apply_evidence_compression: bool = True,
                           apply_directional_fact_precheck: bool = True) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    with open(f"{out_dir}/audit/prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    writer_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)

    gen_result = _generate_and_compress_article_4v(
        client, theme_id, label, prompt, out_dir, apply_evidence_compression, writer_model)
    if gen_result["status"] != "OK":
        return {"label": label, "status": gen_result["status"], "article_text": None}
    article_text = gen_result["article_text"]

    sections = split_seven_voice_sections(article_text)
    if sections is None:
        return {
            "label": label, "status": "STRUCTURE_NOT_SEVEN_SECTIONS", "article_text": article_text,
            "metrics": gen.compute_metrics(article_text),
        }

    print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: Overlap monitoring(16値)開始...")
    overlap_summary = run_overlap_monitoring_4v(sections, out_dir)

    metrics = gen.compute_metrics(article_text)
    seven_section_report = seven_section_length_report(article_text)
    with open(f"{out_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    if seven_section_report is not None:
        with open(f"{out_dir}/seven_section_length_report.json", "w", encoding="utf-8") as f:
            json.dump(seven_section_report, f, ensure_ascii=False, indent=2)
    print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: metrics={metrics} seven_section_report={seven_section_report}")

    fc_record = run_fact_check_a_prime_4v(article_text, verified_ledger_text, out_dir)
    fc_status = fc_record.get("final_status")
    verdict = (fc_record.get("result") or {}).get("verdict")
    if verdict == "FAIL":
        print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: Fact CheckerがFAILと判定。NG_REVIEW_REQUIREDとして報告します。")
        return {
            "label": label, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": metrics, "seven_section_report": seven_section_report, "sections": sections,
            "fact_status": fc_status, "fact_verdict": verdict, "fact_check_result": fc_record,
            "point_overlap_qa_monitoring": overlap_summary,
        }

    ledger_model = routing.require_model(gen._writer_process(label), routing.WRITER_MODEL)
    ledger_result = run_ledger_deviation_and_local_rewrite(
        client, theme_id, label, article_text, verified_ledger_text, out_dir, ledger_model)
    article_text = ledger_result["article_text"]
    sections = split_seven_voice_sections(article_text)  # Local Rewrite後に再抽出

    if ledger_result["remaining_major_count"] or ledger_result["any_human_review_required"]:
        print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: Local Rewrite cycleを尽くしてもLedger MAJOR残存/"
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
        print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: 比較方向Fact事前チェック開始(rule-based、¥0)...")
        vfl_path = f"{out_dir}/research/stage_b3_vfl.json"  # 本Trialでは存在しない、Layer 2のみ実行(¥0)
        directional_result = dfp.audit_article_directional_facts(article_text, verified_ledger_text, vfl_path=vfl_path)
        directional_precheck_status = directional_result["overall_status"]
        with open(f"{out_dir}/audit/directional_fact_precheck.json", "w", encoding="utf-8") as f:
            json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[4V-ARTICLE-TRIAL-01][{theme_id}] {label}: 比較方向Fact事前チェック完了。overall_status={directional_precheck_status}")

    return {
        "label": label, "status": "OK", "article_text": article_text,
        "metrics": gen.compute_metrics(article_text), "sections": sections,
        "seven_section_report": seven_section_length_report(article_text),
        "fact_status": fc_status, "fact_verdict": verdict, "fact_check_result": fc_record,
        "ledger_status": ledger_result["ledger_status"],
        "ledger_deviation_count": ledger_result["ledger_deviation_count"],
        "local_rewrite_cycles": ledger_result["local_rewrite_cycles"],
        "local_rewrite_cycle_exhausted": ledger_result["local_rewrite_cycle_exhausted"],
        "point_overlap_qa_monitoring": overlap_summary,
        "directional_fact_precheck_status": directional_precheck_status,
    }


# ============================================================
# Writer + Analytical Leakage Checkパイプライン(Trial-07 run_trial07_
# pipeline()の4V版。既存上限[初回1回+是正再実行最大2回=合計最大3
# attempts]を省略せず維持する)。
# ============================================================
MAX_WRITER_ATTEMPTS = 3  # 初回1回 + 是正再実行最大2回(既存上限、Trial-07同一)


def run_pipeline_4v(client, theme_id: str, label: str, base_prompt: str, verified_ledger_text: str,
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

        print(f"[4V-ARTICLE-TRIAL-01] Writer attempt {attempt}/{MAX_WRITER_ATTEMPTS} 開始(out_dir={attempt_dir})...")
        t0 = time.time()
        with cl.logging_context(theme_id, f"writer_{label.lower()}_attempt{attempt}"):
            result = run_voices_pattern_4v(client, theme_id, label, prompt_for_attempt, verified_ledger_text, attempt_dir)
        result["elapsed_seconds"] = round(time.time() - t0, 1)

        entry = {"attempt": attempt, "out_dir": attempt_dir, "status": result.get("status")}
        final_result = result
        final_attempt_dir = attempt_dir

        if result.get("status") != "OK" or not result.get("article_text"):
            entry["leakage_check"] = None
            entry["any_flagged"] = None
            attempt_history.append(entry)
            print(f"[4V-ARTICLE-TRIAL-01] attempt {attempt}: status={result.get('status')}のためLeakage Checkをスキップします。")
            break

        sections = result.get("sections") or split_seven_voice_sections(result["article_text"])
        if sections is None:
            entry["leakage_check"] = {"qa_status": "SKIPPED_NO_SEVEN_SECTIONS"}
            entry["any_flagged"] = None
            attempt_history.append(entry)
            final_result["sections"] = None
            print(f"[4V-ARTICLE-TRIAL-01] attempt {attempt}: 7区切り構造が検出できずLeakage Checkをスキップしました。")
            break

        leakage = run_analytical_leakage_check_4v(client, sections, writer_model, gen.REASONING_EFFORT, attempt_dir, attempt)
        entry["leakage_check"] = leakage
        entry["any_flagged"] = leakage["any_flagged"]
        attempt_history.append(entry)
        final_result["sections"] = sections
        final_result["analytical_leakage_check"] = leakage

        if not leakage["any_flagged"]:
            print(f"[4V-ARTICLE-TRIAL-01] attempt {attempt}: Analytical Leakage Check flagged項目なし。確定。")
            break
        if attempt == MAX_WRITER_ATTEMPTS:
            print(f"[4V-ARTICLE-TRIAL-01] attempt {attempt}: 最大attempt数に到達。flagged項目が残った状態の"
                  f"記事を最終結果として記録します(Report側でUSER_DECISION_REQUIRED候補として扱う)。")
            break
        corrective_note = build_leakage_corrective_note_4v(leakage)

    with open(f"{out_dir_base}_attempt_history.json", "w", encoding="utf-8") as f:
        json.dump(attempt_history, f, ensure_ascii=False, indent=2, default=str)

    return {"final_result": final_result, "final_attempt_dir": final_attempt_dir,
            "attempt_history": attempt_history, "total_attempts": len(attempt_history)}


# ============================================================
# EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01: 再開専用関数。
# 前回セッションがユーザーの誤操作によりattempt3の
# run_ledger_deviation_and_local_rewrite()呼び出し中(Writer生成・Evidence
# Compression・Fact Checker A'は完了済み、fact_qa.json保存済み・verdict=
# PASS確認済み)で中断していたため、attempt1/2の既存生成物(article.md・
# fact_qa.json・ledger_deviation.json・analytical_leakage_check_4v_
# attemptN.json等)はそのまま再利用し(再生成しない)、attempt3のみ
# Ledger Deviation Checker以降(Local Rewrite→比較方向Fact事前チェック→
# Analytical Leakage Check)を、run_voices_pattern_4v/run_pipeline_4vと
# 完全に同一のPrimitive呼び出しで続行する。Writer/Fact Checkerロジック
# 自体は一切変更・再実行しない。
# ============================================================
def run_writer_stage_resume_from_interrupted_attempt3() -> dict:
    if not os.path.exists(LEDGER_PATH):
        raise SystemExit(f"Ledger not found at {LEDGER_PATH}. STOP条件(Ledger未確定)。")
    with open(LEDGER_PATH, encoding="utf-8") as f:
        verified_ledger_text = f.read()

    client = vfl01.get_client()
    cl.install(f"{LEVEL_OUT_DIR}/raw_usage_log_4v_writer.jsonl")  # 既存logへ追記継続(累計費用を維持)

    attempt3_dir = f"{LEVEL_OUT_DIR}_attempt3"
    article_path = f"{attempt3_dir}/article.md"
    if not os.path.exists(article_path):
        raise SystemExit(f"{article_path}が見つかりません。中断状態が想定と異なります(STOP)。")
    with open(article_path, encoding="utf-8") as f:
        article_text = f.read()

    with open(f"{attempt3_dir}/fact_qa.json", encoding="utf-8") as f:
        fc_record = json.load(f)
    fc_status = fc_record.get("final_status")
    verdict = (fc_record.get("result") or {}).get("verdict")
    if verdict == "FAIL":
        raise SystemExit("attempt3のFact CheckerがFAILと記録されています。想定外の中断状態のためSTOPします。")

    writer_model = routing.require_model(gen._writer_process(LABEL), routing.WRITER_MODEL)

    print("[4V-ARTICLE-TRIAL-01][RESUME] attempt3: Ledger Deviation Checker + Local Rewriteを再開...")
    ledger_result = run_ledger_deviation_and_local_rewrite(
        client, THEME_ID, LABEL, article_text, verified_ledger_text, attempt3_dir, writer_model)
    article_text = ledger_result["article_text"]
    sections = split_seven_voice_sections(article_text)  # Local Rewrite後に再抽出

    if ledger_result["remaining_major_count"] or ledger_result["any_human_review_required"]:
        print("[4V-ARTICLE-TRIAL-01][RESUME] attempt3: Local Rewrite cycleを尽くしてもLedger MAJOR残存/"
              "human_review_required。NG_REVIEW_REQUIREDとして報告します。")
        attempt3_result = {
            "label": LABEL, "status": "NG_REVIEW_REQUIRED", "article_text": article_text,
            "metrics": gen.compute_metrics(article_text), "sections": sections,
            "fact_status": fc_status, "fact_verdict": verdict,
            "ledger_status": ledger_result["ledger_status"],
            "ledger_deviation_count": ledger_result["ledger_deviation_count"],
            "local_rewrite_cycles": ledger_result["local_rewrite_cycles"],
            "local_rewrite_cycle_exhausted": ledger_result["local_rewrite_cycle_exhausted"],
        }
    else:
        print("[4V-ARTICLE-TRIAL-01][RESUME] attempt3: 比較方向Fact事前チェック開始(rule-based、¥0)...")
        vfl_path = f"{attempt3_dir}/research/stage_b3_vfl.json"  # 本Trialでは存在しない、Layer 2のみ実行(¥0)
        directional_result = dfp.audit_article_directional_facts(article_text, verified_ledger_text, vfl_path=vfl_path)
        directional_precheck_status = directional_result["overall_status"]
        with open(f"{attempt3_dir}/audit/directional_fact_precheck.json", "w", encoding="utf-8") as f:
            json.dump(directional_result, f, ensure_ascii=False, indent=2, default=str)
        print(f"[4V-ARTICLE-TRIAL-01][RESUME] attempt3: 比較方向Fact事前チェック完了。"
              f"overall_status={directional_precheck_status}")

        attempt3_result = {
            "label": LABEL, "status": "OK", "article_text": article_text,
            "metrics": gen.compute_metrics(article_text), "sections": sections,
            "seven_section_report": seven_section_length_report(article_text),
            "fact_status": fc_status, "fact_verdict": verdict, "fact_check_result": fc_record,
            "ledger_status": ledger_result["ledger_status"],
            "ledger_deviation_count": ledger_result["ledger_deviation_count"],
            "local_rewrite_cycles": ledger_result["local_rewrite_cycles"],
            "local_rewrite_cycle_exhausted": ledger_result["local_rewrite_cycle_exhausted"],
            "directional_fact_precheck_status": directional_precheck_status,
        }

    entry3 = {"attempt": 3, "out_dir": attempt3_dir, "status": attempt3_result.get("status")}
    if attempt3_result.get("status") != "OK" or sections is None:
        entry3["leakage_check"] = None
        entry3["any_flagged"] = None
        final_result = attempt3_result
    else:
        leakage = run_analytical_leakage_check_4v(client, sections, writer_model, gen.REASONING_EFFORT, attempt3_dir, 3)
        entry3["leakage_check"] = leakage
        entry3["any_flagged"] = leakage["any_flagged"]
        attempt3_result["sections"] = sections
        attempt3_result["analytical_leakage_check"] = leakage
        final_result = attempt3_result
        print(f"[4V-ARTICLE-TRIAL-01][RESUME] attempt3(最終attempt、MAX_WRITER_ATTEMPTS到達): "
              f"Analytical Leakage Check any_flagged={leakage['any_flagged']}。この結果を最終結果として確定します。")

    # attempt1/2は前回セッションで完了済みの既存生成物をそのまま再利用する
    # (再生成しない)。attempt_history再構築のためleakage jsonのみ読み込む。
    attempt_history = []
    for n in (1, 2):
        adir = f"{LEVEL_OUT_DIR}_attempt{n}"
        with open(f"{adir}/analytical_leakage_check_4v_attempt{n}.json", encoding="utf-8") as f:
            leakage_n = json.load(f)
        attempt_history.append({"attempt": n, "out_dir": adir, "status": "OK",
                                 "leakage_check": leakage_n, "any_flagged": leakage_n["any_flagged"]})
    attempt_history.append(entry3)

    with open(f"{LEVEL_OUT_DIR}_attempt_history.json", "w", encoding="utf-8") as f:
        json.dump(attempt_history, f, ensure_ascii=False, indent=2, default=str)

    with open(f"{LEVEL_OUT_DIR}/summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "attempt_history": attempt_history,
            "total_attempts": len(attempt_history),
            "final_attempt_dir": attempt3_dir,
            "final_result": {k: v for k, v in final_result.items() if k not in ("article_text", "sections")},
            "resume_note": ("EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01: attempt3はユーザーの誤操作による"
                            "前回セッション中断からの再開(Ledger Deviation Checker以降のみ再実行、Writer/"
                            "Evidence Compression/Fact Checker A'は前回生成物を再利用、再生成なし)。"),
        }, f, ensure_ascii=False, indent=2, default=str)

    print(f"[4V-ARTICLE-TRIAL-01][RESUME] 完了。total_attempts={len(attempt_history)} "
          f"final_status={final_result.get('status')} fact_verdict={final_result.get('fact_verdict')} "
          f"ledger_status={final_result.get('ledger_status')}")
    return {"pipeline": {"final_result": final_result, "final_attempt_dir": attempt3_dir,
                         "attempt_history": attempt_history, "total_attempts": len(attempt_history)},
            "status": "DONE"}


def run_writer_stage() -> dict:
    if not os.path.exists(LEDGER_PATH):
        raise SystemExit(f"Ledger not found at {LEDGER_PATH}. STOP条件(Ledger未確定)。")
    with open(LEDGER_PATH, encoding="utf-8") as f:
        verified_ledger_text = f.read()

    os.makedirs(LEVEL_OUT_DIR, exist_ok=True)
    phase_a = run_phase_a(f"{LEVEL_OUT_DIR}/audit")
    if not phase_a["phase_a_pass"]:
        print("[4V-ARTICLE-TRIAL-01] Phase Aで意図しない差分を検出したため、Writerへ進まずSTOPします。")
        return {"phase_a": phase_a, "pipeline": None, "status": "STOP_PHASE_A_UNEXPECTED_DIFF"}

    client = vfl01.get_client()
    cl.install(f"{LEVEL_OUT_DIR}/raw_usage_log_4v_writer.jsonl")
    master_full_text = ab01.load_master_full_text()

    candidate_prompt = build_candidate_prompt(
        phase_a["candidate_template"], master_full_text, TOPIC_JA, verified_ledger_text, gen.B1_B_DIRECT_INSTRUCTION)
    with open(f"{LEVEL_OUT_DIR}/audit_candidate_prompt_base.txt", "w", encoding="utf-8") as f:
        f.write(candidate_prompt)

    print(f"[4V-ARTICLE-TRIAL-01] Writer + Analytical Leakage Checkパイプライン開始(最大{MAX_WRITER_ATTEMPTS} attempts)...")
    pipeline_result = run_pipeline_4v(client, THEME_ID, LABEL, candidate_prompt, verified_ledger_text, LEVEL_OUT_DIR)

    with open(f"{LEVEL_OUT_DIR}/summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "attempt_history": pipeline_result["attempt_history"],
            "total_attempts": pipeline_result["total_attempts"],
            "final_attempt_dir": pipeline_result["final_attempt_dir"],
            "final_result": {k: v for k, v in (pipeline_result["final_result"] or {}).items()
                              if k not in ("article_text", "sections")},
        }, f, ensure_ascii=False, indent=2, default=str)

    final_result = pipeline_result["final_result"] or {}
    print(f"[4V-ARTICLE-TRIAL-01] 完了。total_attempts={pipeline_result['total_attempts']} "
          f"final_status={final_result.get('status')} fact_verdict={final_result.get('fact_verdict')} "
          f"ledger_status={final_result.get('ledger_status')}")
    return {"phase_a": phase_a, "pipeline": pipeline_result, "status": "DONE"}


# ============================================================
# Comment 1〜4(確定版Contract+Comment2/3の4V版文言)。Comment 1/4は
# registry.COMMENT_ROLES(Production、無変更。voice数に依存しない文言)を
# 使い実際にb1s.run_support_text()(Production primitive、無変更)経由で
# LLM生成する。Comment 2/3のRole prompt(registry.py)は"One Voice"
# "Another Voice"「2つの声」という2V固定文言をハードコードしており
# (Opusレビュー6-HIGH)、4V記事へそのまま使うと誤った文言(2声前提)が
# 生成されてしまうため、design.md B-1の手動ドラフト(未承認・Trial-only、
# LLM再生成せず、registryへは一切書かない)をそのまま採用する。
# ============================================================
COMMENT_2_TEXT_4V_DRAFT = (
    "Now, you will hear four different voices, one after another. Each person will share "
    "their own view on what you just heard."
)
COMMENT_3_TEXT_4V_DRAFT = (
    "You have heard four different ways of experiencing the same situation. Instead of "
    "deciding which view is right, let us ask why the situation feels different to each "
    "person. Next, we will look more closely at where that difference comes from."
)


def run_comments_1_and_4(client, sections: dict, out_dir: str) -> dict:
    model = routing.require_model("B1_SUPPORT", routing.SUPPORT_MODEL)
    comment_roles = registry.COMMENT_ROLES  # Production, 無変更

    c1_context = f"【これから聞く本文(The Question)】\n{sections['hook_body']}"
    c1 = b1s.run_support_text(client, comment_roles["comment_1"], c1_context, model=model)

    c4_context = (f"【聞き終えた内容(視点の違いの深掘り)】\n{sections['tension_body']}\n\n"
                  f"【これから聞く結びの見出しのみ(内容は伏せる)】\n{sections['closing_heading']}")
    c4 = b1s.run_support_text(client, comment_roles["comment_4"], c4_context, model=model)

    result = {
        "comment_1": {"text": c1["text"], "status": c1["status"], "llm_generated": True},
        "comment_2": {"text": COMMENT_2_TEXT_4V_DRAFT, "llm_generated": False,
                      "status": "TRIAL_ONLY_MANUAL_DRAFT_NOT_LLM_GENERATED",
                      "source": "design.md B-1(未承認・Trial-only、registryへ書かない)"},
        "comment_3": {"text": COMMENT_3_TEXT_4V_DRAFT, "llm_generated": False,
                      "status": "TRIAL_ONLY_MANUAL_DRAFT_NOT_LLM_GENERATED",
                      "source": "design.md B-1(未承認・Trial-only、registryへ書かない)"},
        "comment_4": {"text": c4["text"], "status": c4["status"], "llm_generated": True},
    }
    with open(f"{out_dir}/comments_1_to_4.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    print(f"[4V-ARTICLE-TRIAL-01][Comments] comment_1={c1['text'][:60]!r} comment_4={c4['text'][:60]!r}")
    return result


# ============================================================
# Pairwise Voice Distinctness Check(未承認仕様候補、Opusレビュー2-HIGH起点。
# 判定軸=stakeholder position/constraint/responsibility/what they
# protect/reasoning。有向12ペア[個別呼び出し]+一括判定[1回で4 Voiceを
# 同時評価]を実測比較する)。
# ============================================================
DISTINCTNESS_AXES = ("stakeholder_position", "constraint", "responsibility", "what_they_protect", "reasoning")
DISTINCTNESS_JUDGMENT_ENUM = ["SAME", "SIMILAR", "DIFFERENT"]

DISTINCTNESS_DEVELOPER_MESSAGE = (
    "あなたは、Voices/Perspective型記事の複数Voice間の『多様性』(役割・理由・主張の違い)を"
    "審査する、厳格なEditorial QA判定者です。Voice本文を読み、指定された判定軸それぞれに"
    "ついて、同一(SAME)・類似(SIMILAR)・異なる(DIFFERENT)のいずれかを判定してください。"
    "語彙・言い回しの違いではなく、内容としての立場・制約・責任・守るもの・推論構造の違いを"
    "見てください(語彙が違っても推論構造が同じならSAME/SIMILARと判定し、逆に語彙が似ていても"
    "立場・責任が明確に異なればDIFFERENTと判定してください)。"
)


def _distinctness_axis_schema() -> dict:
    return {"type": "object",
            "properties": {"judgment": {"type": "string", "enum": DISTINCTNESS_JUDGMENT_ENUM},
                            "reasoning": {"type": "string"}},
            "required": ["judgment", "reasoning"], "additionalProperties": False}


PAIRWISE_DISTINCTNESS_JSON_SCHEMA = {
    "name": "pairwise_voice_distinctness_check",
    "schema": {
        "type": "object",
        "properties": {axis: _distinctness_axis_schema() for axis in DISTINCTNESS_AXES},
        "required": list(DISTINCTNESS_AXES), "additionalProperties": False,
    },
    "strict": True,
}

PAIRWISE_DISTINCTNESS_PROMPT_TEMPLATE = """以下は、あるVoices/Perspective型記事の2つのVoice本文です。

【Voice X({label_x})本文】
{text_x}

【Voice Y({label_y})本文】
{text_y}

5つの判定軸(stakeholder_position=当事者としての立場、constraint=制約、responsibility=責任、
what_they_protect=何を守ろうとしているか、reasoning=推論の筋道)それぞれについて、Voice Xと
Voice Yが同一/類似/異なるかを判定してください。reasoningフィールドには判定理由を1〜2文の
日本語で書いてください。
"""


def run_pairwise_distinctness_check_single(client, text_x: str, label_x: str, text_y: str, label_y: str,
                                            model: str, reasoning_effort: str = "low") -> dict:
    prompt = PAIRWISE_DISTINCTNESS_PROMPT_TEMPLATE.format(label_x=label_x, text_x=text_x, label_y=label_y, text_y=text_y)
    response = client.responses.create(
        model=model, reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **PAIRWISE_DISTINCTNESS_JSON_SCHEMA}},
        input=[{"role": "developer", "content": DISTINCTNESS_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    if response.model != model:
        raise RuntimeError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    text = getattr(response, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Distinctness Check応答が空です")
    parsed = json.loads(text)
    return {"model": response.model, "response_id": response.id, "parsed": parsed,
            "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}


BATCH_PAIR_KEYS = ("voice_1_voice_2", "voice_1_voice_3", "voice_1_voice_4",
                   "voice_2_voice_3", "voice_2_voice_4", "voice_3_voice_4")

BATCH_DISTINCTNESS_JSON_SCHEMA = {
    "name": "batch_pairwise_voice_distinctness_check",
    "schema": {
        "type": "object",
        "properties": {pair: {
            "type": "object",
            "properties": {axis: _distinctness_axis_schema() for axis in DISTINCTNESS_AXES},
            "required": list(DISTINCTNESS_AXES), "additionalProperties": False,
        } for pair in BATCH_PAIR_KEYS},
        "required": list(BATCH_PAIR_KEYS), "additionalProperties": False,
    },
    "strict": True,
}

BATCH_DISTINCTNESS_PROMPT_TEMPLATE = """以下は、あるVoices/Perspective型記事(4 Voices)の4つのVoice本文です。

【Voice 1(Applicant)本文】
{voice_1}

【Voice 2(Recruiter/Hiring Manager)本文】
{voice_2}

【Voice 3(Business/Efficiency)本文】
{voice_3}

【Voice 4(Fairness/Legal/HR Governance)本文】
{voice_4}

4人の中から2人を選ぶ組み合わせ(voice_1_voice_2, voice_1_voice_3, voice_1_voice_4,
voice_2_voice_3, voice_2_voice_4, voice_3_voice_4)ごとに、5つの判定軸
(stakeholder_position/constraint/responsibility/what_they_protect/reasoning)を
同一(SAME)/類似(SIMILAR)/異なる(DIFFERENT)で判定してください。4人全員を一度に比較した
うえで、各ペアの違いを判定してください。reasoningフィールドには判定理由を1〜2文の日本語で
書いてください。
"""


def run_batch_distinctness_check(client, sections: dict, model: str, reasoning_effort: str = "low") -> dict:
    prompt = BATCH_DISTINCTNESS_PROMPT_TEMPLATE.format(
        voice_1=sections["voice_1_body"], voice_2=sections["voice_2_body"],
        voice_3=sections["voice_3_body"], voice_4=sections["voice_4_body"])
    response = client.responses.create(
        model=model, reasoning={"effort": reasoning_effort},
        text={"format": {"type": "json_schema", **BATCH_DISTINCTNESS_JSON_SCHEMA}},
        input=[{"role": "developer", "content": DISTINCTNESS_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    if response.model != model:
        raise RuntimeError(f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
    text = getattr(response, "output_text", None)
    if not text or not text.strip():
        raise RuntimeError("Batch Distinctness Check応答が空です")
    parsed = json.loads(text)
    return {"model": response.model, "response_id": response.id, "parsed": parsed,
            "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}


def run_distinctness_check_full(client, sections: dict, out_dir: str) -> dict:
    # reasoning_effort="low": Trial限定のコスト管理選択(未承認仕様候補、
    # Contract化された基準ではない。Analytical Leakage Check等の既存
    # Contract相当QAはgen.REASONING_EFFORT["high"]のまま変更していない)。
    model = routing.require_model(gen._writer_process(LABEL), routing.WRITER_MODEL)
    voice_keys = ("voice_1", "voice_2", "voice_3", "voice_4")
    t0 = time.time()
    directed_results = {}
    for a, b in itertools.permutations(voice_keys, 2):
        key = f"{a}_vs_{b}"
        r = run_pairwise_distinctness_check_single(
            client, sections[f"{a}_body"], VOICE_STAKEHOLDER_LABEL[a],
            sections[f"{b}_body"], VOICE_STAKEHOLDER_LABEL[b], model=model)
        directed_results[key] = r
        print(f"[4V-ARTICLE-TRIAL-01][Distinctness] directed {key}: "
              f"{{axis: r['parsed'][axis]['judgment'] for axis in DISTINCTNESS_AXES}}")
    directed_elapsed = round(time.time() - t0, 1)

    t1 = time.time()
    batch_result = run_batch_distinctness_check(client, sections, model=model)
    batch_elapsed = round(time.time() - t1, 1)

    direction_agreement = []
    method_agreement = []
    pair_unordered = [("voice_1", "voice_2"), ("voice_1", "voice_3"), ("voice_1", "voice_4"),
                       ("voice_2", "voice_3"), ("voice_2", "voice_4"), ("voice_3", "voice_4")]
    for a, b in pair_unordered:
        pair_key = f"{a}_{b}"
        fwd = directed_results[f"{a}_vs_{b}"]["parsed"]
        rev = directed_results[f"{b}_vs_{a}"]["parsed"]
        batch = batch_result["parsed"][pair_key]
        for axis in DISTINCTNESS_AXES:
            direction_agreement.append(fwd[axis]["judgment"] == rev[axis]["judgment"])
            method_agreement.append(batch[axis]["judgment"] == fwd[axis]["judgment"])

    direction_agreement_rate = round(sum(direction_agreement) / len(direction_agreement), 3)
    method_agreement_rate = round(sum(method_agreement) / len(method_agreement), 3)

    summary = {
        "note": ("EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01: Pairwise Voice Distinctness Check"
                 "(未承認仕様候補、Opusレビュー2-HIGH起点)。有向12ペア(個別呼び出し)+一括判定"
                 "(1回で4 Voice・6ペア同時評価)を実測比較。reasoning_effort='low'(コスト管理の"
                 "ためのTrial限定の選択、既存Contract化QAの基準ではない)。"),
        "directed_pair_count": len(directed_results), "directed_elapsed_seconds": directed_elapsed,
        "batch_elapsed_seconds": batch_elapsed,
        "direction_agreement_rate": direction_agreement_rate,
        "direction_agreement_comparisons": len(direction_agreement),
        "method_agreement_rate": method_agreement_rate,
        "method_agreement_comparisons": len(method_agreement),
        "method_agreement_definition": "batch_result[pair][axis].judgment == directed_forward[a_vs_b][axis].judgment",
        "directed_results": directed_results, "batch_result": batch_result,
    }
    with open(f"{out_dir}/pairwise_voice_distinctness_check.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[4V-ARTICLE-TRIAL-01][Distinctness] 完了。direction_agreement_rate={direction_agreement_rate} "
          f"method_agreement_rate={method_agreement_rate} directed_elapsed={directed_elapsed}s batch_elapsed={batch_elapsed}s")
    return summary


# ============================================================
# 既存2V記事参照(Reconciliation finding、本Trial実行時に新規発見):
# `er012_b_family_voices_production_01`(Production)には`ARTICLE_PATH`
# 定数が存在しない。design.md B-6が実測基準として引用している
# `EDITORIAL-B-FAMILY-VOICES-TRIAL-09-HEADING-REGEN-AND-FULL-EPISODE-03_
# REPORT.md`(301.795秒実測、pause除く)に対応する実article.md
# (`er012_output/editorial_b_voices_trial_09_audio/b1b/article.md`)を
# Trial側で直接参照する(Production・Trial-07への書込み・変更は一切
# 行わない、読み取り専用)。
# ============================================================
EXISTING_2V_ARTICLE_PATH_TRIAL09 = "er012_output/editorial_b_voices_trial_09_audio/b1b/article.md"


# ============================================================
# Overlap QAの¥0 control群(Opusレビュー3-MED対応)。合否判定には使わず、
# 実測記録のみ(閾値0.40はここでも変更しない)。
# ============================================================
_POSITIVE_CONTROL_SYNONYM_MAP = {
    "applicant": "candidate", "Applicant": "Candidate", "applicants": "candidates",
    "resume": "application", "résumé": "application", "resumes": "applications",
    "interview": "conversation", "hired": "selected", "job": "role",
    "fair": "just", "score": "rate", "scores": "rates", "scored": "rated",
    "camera": "webcam", "video": "recorded", "AI": "the automated system",
}


def _build_positive_control_text(source_text: str) -> str:
    text = source_text
    for old, new in _POSITIVE_CONTROL_SYNONYM_MAP.items():
        text = re.sub(rf"\b{re.escape(old)}\b", new, text)
    return text


DETERMINISTIC_CONTROL_TEXT_A = (
    "The overnight warehouse supervisor checks a scanner before every shift. The rules on the "
    "screen were written by people she has never met, and she cannot change them even when a "
    "case in front of her does not fit the pattern. She has to enforce a decision she did not "
    "make, and she is the one who has to look the affected worker in the eye afterward. What she "
    "wants is a process she can actually explain when someone asks why."
)
DETERMINISTIC_CONTROL_TEXT_B = (
    "The overnight charge nurse logs into a dashboard before every shift. The thresholds on the "
    "chart were set by people she has never met, and she cannot override them even when a "
    "patient in front of her does not fit the pattern. She has to carry out a decision she did "
    "not make, and she is the one who has to look the affected patient in the eye afterward. "
    "What she wants is a process she can actually explain when someone asks why."
)

THEME_VOCAB_DUMMY_TEXT_A = (
    "The AI screening tool flags applicants using an algorithm trained on past hiring data, and "
    "the recruiter trusts the AI screening score because the algorithm has passed an internal "
    "audit for bias in applicant screening."
)
THEME_VOCAB_DUMMY_TEXT_B = (
    "The applicant distrusts the AI screening algorithm because no audit of the screening tool "
    "has ever been shown to applicants, and the recruiter cannot explain how the AI algorithm "
    "screens each applicant."
)


def run_overlap_controls(sections: dict, out_dir: str) -> dict:
    voice_1 = sections["voice_1_body"]
    positive_text = _build_positive_control_text(voice_1)
    positive_result = overlap_qa.flag_possible_paraphrase(positive_text, voice_1)
    deterministic_result = overlap_qa.flag_possible_paraphrase(DETERMINISTIC_CONTROL_TEXT_A, DETERMINISTIC_CONTROL_TEXT_B)

    negative_result = None
    if os.path.exists(EXISTING_2V_ARTICLE_PATH_TRIAL09):
        with open(EXISTING_2V_ARTICLE_PATH_TRIAL09, encoding="utf-8") as f:
            existing_2v_article = f.read()
        existing_sections = b1prod.split_five_voice_sections(existing_2v_article)
        if existing_sections is not None:
            negative_result = overlap_qa.flag_possible_paraphrase(
                existing_sections["voice_a_body"], existing_sections["voice_b_body"])

    theme_dummy_result = overlap_qa.flag_possible_paraphrase(THEME_VOCAB_DUMMY_TEXT_A, THEME_VOCAB_DUMMY_TEXT_B)

    summary = {
        "note": "Opusレビュー3-MED対応。¥0のcontrol群、閾値0.40は合否に使わず記録のみ。",
        "positive_control": {"description": "Voice 1本文の語彙のみ最小限改変した複製(reasoning同一、高overlap期待)",
                              "positive_text": positive_text, "result": positive_result},
        "deterministic_control": {"description": "職名だけ違い推論構造が同一の合成ダミーペア(語彙は大きく変える、低overlap期待=指標の盲点の実証)",
                                   "text_a": DETERMINISTIC_CONTROL_TEXT_A, "text_b": DETERMINISTIC_CONTROL_TEXT_B,
                                   "result": deterministic_result},
        "negative_control": {"description": "既存2V実採用ペア(Trial-07最終記事)の再計算(低overlap期待)",
                              "result": negative_result},
        "theme_vocab_dummy": {"description": "テーマ語彙(AI/screening/applicant/algorithm/audit)を意図的に多く共有する合成ダミーペア(reasoningは異なる、偽陽性リスク確認)",
                               "text_a": THEME_VOCAB_DUMMY_TEXT_A, "text_b": THEME_VOCAB_DUMMY_TEXT_B,
                               "result": theme_dummy_result},
    }
    with open(f"{out_dir}/overlap_qa_controls.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[4V-ARTICLE-TRIAL-01][Overlap Controls] positive={positive_result['overlap_ratio']} "
          f"deterministic={deterministic_result['overlap_ratio']} "
          f"negative={(negative_result or {}).get('overlap_ratio')} theme_dummy={theme_dummy_result['overlap_ratio']}")
    return summary


# ============================================================
# 語数・尺見積り(monitoring専用、design.md B-6の2V実測定数を引用し語数/秒比
# で4V estimated durationを換算する。音声は生成していないため実測ではない)。
# ============================================================
TWO_V_FIXED_PARTS_SECONDS = 95.5
TWO_V_VARIABLE_PARTS_SECONDS = 193.2  # Hook+Comment2-4+VoiceA/B見出し・本体+Tension+Closing(pause除く)
TWO_V_COMMENT_2_4_SECONDS = 35.6
TWO_V_PAUSE_SECONDS = 13.0
FOUR_V_TARGET_RANGE_SECONDS = (380, 430)  # design.md B-6由来、未検証monitoring値


def build_word_count_and_duration_estimate(sections: dict, out_dir: str) -> dict:
    variable_word_count_4v = sum(
        ab01.compute_word_count(sections[f"{k}_body"])
        for k in ("hook", "voice_1", "voice_2", "voice_3", "voice_4", "tension", "closing")
    )
    variable_word_count_2v = None
    if os.path.exists(EXISTING_2V_ARTICLE_PATH_TRIAL09):
        with open(EXISTING_2V_ARTICLE_PATH_TRIAL09, encoding="utf-8") as f:
            existing_2v_article = f.read()
        existing_sections = b1prod.split_five_voice_sections(existing_2v_article)
        if existing_sections is not None:
            variable_word_count_2v = sum(
                ab01.compute_word_count(existing_sections[f"{k}_body"])
                for k in ("hook", "voice_a", "voice_b", "tension", "closing"))

    estimate = None
    if variable_word_count_2v:
        seconds_per_word = TWO_V_VARIABLE_PARTS_SECONDS / variable_word_count_2v
        estimated_variable_seconds_4v = round(seconds_per_word * variable_word_count_4v, 1)
        two_v_variable_segment_count = 7
        four_v_variable_segment_count = 11
        estimated_pause_seconds_4v = round(
            TWO_V_PAUSE_SECONDS * (four_v_variable_segment_count / two_v_variable_segment_count), 1)
        estimated_total_seconds_4v = round(
            TWO_V_FIXED_PARTS_SECONDS + TWO_V_COMMENT_2_4_SECONDS + estimated_variable_seconds_4v
            + estimated_pause_seconds_4v, 1)
        estimate = {
            "seconds_per_word_2v_variable_parts": round(seconds_per_word, 4),
            "estimated_variable_seconds_4v": estimated_variable_seconds_4v,
            "estimated_pause_seconds_4v": estimated_pause_seconds_4v,
            "estimated_total_seconds_4v": estimated_total_seconds_4v,
            "within_4v_target_range": FOUR_V_TARGET_RANGE_SECONDS[0] <= estimated_total_seconds_4v <= FOUR_V_TARGET_RANGE_SECONDS[1],
        }

    result = {
        "note": ("音声は生成していない(テキストのみTrial)。design.md B-6の2V実測定数を引用し、"
                 "語数/秒比で4V estimated durationをmonitoring目的でのみ換算した(gate・正式検証ではない)。"),
        "variable_word_count_4v": variable_word_count_4v,
        "variable_word_count_2v_reference": variable_word_count_2v,
        "estimate": estimate,
        "four_v_target_range_seconds_design_md": FOUR_V_TARGET_RANGE_SECONDS,
    }
    with open(f"{out_dir}/word_count_and_duration_estimate.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[4V-ARTICLE-TRIAL-01][Duration Estimate] variable_word_count_4v={variable_word_count_4v} estimate={estimate}")
    return result


# ============================================================
# OPEN-129整合(Gate 3 item 8参照、Opusレビュー4-MED対応): 4V required_
# structure(Trial側定義、voice_map方式)。妥当性レビューのみ(Gate突合は
# segment/音声が存在しないため実施しない、正本統合はOPEN-132で追跡)。
# ============================================================
REQUIRED_STRUCTURE_4V_TRIAL = (
    ("topic_intro", "narrator_charon"), ("preview", "narrator_charon"),
    ("comment_1", "narrator_charon"), ("comment_2", "narrator_charon"),
    ("comment_3", "narrator_charon"), ("comment_4", "narrator_charon"),
    ("voice_1_heading", "narrator_aoede_en"), ("voice_2_heading", "narrator_aoede_en"),
    ("voice_3_heading", "narrator_aoede_en"), ("voice_4_heading", "narrator_aoede_en"),
    ("voice_1", "voice_1"), ("voice_2", "voice_2"), ("voice_3", "voice_3"), ("voice_4", "voice_4"),
    ("full_story_part1", None), ("full_story_part2", None),
    ("tension_reflection", None), ("in_one_line", None),
)


def review_required_structure_4v_trial() -> dict:
    segment_names = [name for name, _role in REQUIRED_STRUCTURE_4V_TRIAL]
    voice_roles = [role for _name, role in REQUIRED_STRUCTURE_4V_TRIAL if role in ("voice_1", "voice_2", "voice_3", "voice_4")]
    review = {
        "note": ("OPEN-129整合(Gate 3 item 8)、Opusレビュー4-MED対応。voice_map方式(Trial側定義、"
                 "registry非編集)。B_FAMILY_B1_REQUIRED_SEGMENTS(Production、2声)と同型のvoice_map"
                 "拡張として妥当か[segment数18、voice_1..4がそれぞれちょうど1回登場]をレビューする"
                 "のみで、Gateへの実際の突合[assemble.py::verify_episode_audio_validation_gate()]は"
                 "音声・segmentが存在しないため実施しない。正本統合はOPEN-132で追跡。"),
        "segment_count": len(segment_names),
        "segment_names_unique": len(set(segment_names)) == len(segment_names),
        "voice_roles_present": sorted(set(voice_roles)) == ["voice_1", "voice_2", "voice_3", "voice_4"],
        "each_voice_role_appears_exactly_once": all(voice_roles.count(v) == 1 for v in ("voice_1", "voice_2", "voice_3", "voice_4")),
        "segment_names": segment_names,
    }
    with open(f"{OUT_DIR}/required_structure_4v_trial_review.json", "w", encoding="utf-8") as f:
        json.dump(review, f, ensure_ascii=False, indent=2)
    print(f"[4V-ARTICLE-TRIAL-01][OPEN-129 review] {review}")
    return review


def run_qa_stage() -> dict:
    """Writer stage完了後、summary.jsonから最終article_textを読み込み、
    Comment 1〜4・Distinctness Check・Overlap Controls・語数/尺見積り・
    OPEN-129 required_structureレビューをまとめて実行する。"""
    summary_path = f"{LEVEL_OUT_DIR}/summary.json"
    if not os.path.exists(summary_path):
        raise SystemExit(f"{summary_path} が見つかりません。先に`write`stageを実行してください。")
    with open(summary_path, encoding="utf-8") as f:
        summary = json.load(f)
    final_attempt_dir = summary["final_attempt_dir"]
    article_path = f"{final_attempt_dir}/article.md"
    if not os.path.exists(article_path):
        raise SystemExit(f"{article_path} が見つかりません(Writer stageがOKで終わっていない可能性)。")
    with open(article_path, encoding="utf-8") as f:
        article_text = f.read()
    sections = split_seven_voice_sections(article_text)
    if sections is None:
        raise SystemExit("最終article.mdが7区切り構造を満たしていません(STOP条件)。")

    qa_out_dir = f"{OUT_DIR}/qa"
    os.makedirs(qa_out_dir, exist_ok=True)

    client = vfl01.get_client()
    cl.install(f"{OUT_DIR}/raw_usage_log_4v_qa_stage.jsonl")

    # 再開安全性(EDITORIAL-B-FAMILY-VOICES-4V-ARTICLE-TRIAL-01: 前回セッション
    # 中断からの再開時、既にLLM callが完了し保存済みの成果物は再生成せず
    # そのまま再利用する。中断が無かった通常実行時はファイルが存在しないため
    # 従来どおり毎回新規実行される、既存動作への影響はない)。
    comments_path = f"{qa_out_dir}/comments_1_to_4.json"
    if os.path.exists(comments_path):
        print("[4V-ARTICLE-TRIAL-01] comments_1_to_4.json既存のため再利用(再生成しない)。")
        with open(comments_path, encoding="utf-8") as f:
            comments = json.load(f)
    else:
        comments = run_comments_1_and_4(client, sections, qa_out_dir)

    distinctness_path = f"{qa_out_dir}/pairwise_voice_distinctness_check.json"
    if os.path.exists(distinctness_path):
        print("[4V-ARTICLE-TRIAL-01] pairwise_voice_distinctness_check.json既存のため再利用(再生成しない)。")
        with open(distinctness_path, encoding="utf-8") as f:
            distinctness = json.load(f)
    else:
        distinctness = run_distinctness_check_full(client, sections, qa_out_dir)

    overlap_controls = run_overlap_controls(sections, qa_out_dir)
    duration_estimate = build_word_count_and_duration_estimate(sections, qa_out_dir)
    structure_review = review_required_structure_4v_trial()

    qa_summary = {
        "final_attempt_dir": final_attempt_dir,
        "comments": {k: v for k, v in comments.items()},
        "distinctness_summary": {k: v for k, v in distinctness.items() if k not in ("directed_results", "batch_result")},
        "overlap_controls_summary": {k: v["result"] for k, v in overlap_controls.items() if k != "note"},
        "duration_estimate": duration_estimate,
        "structure_review": structure_review,
    }
    with open(f"{qa_out_dir}/qa_stage_summary.json", "w", encoding="utf-8") as f:
        json.dump(qa_summary, f, ensure_ascii=False, indent=2, default=str)
    print("[4V-ARTICLE-TRIAL-01] QA stage完了。")
    return qa_summary


def main() -> None:
    stage = sys.argv[1] if len(sys.argv) > 1 else "write"
    if stage == "write":
        run_writer_stage()
    elif stage == "resume_attempt3":
        run_writer_stage_resume_from_interrupted_attempt3()
    elif stage == "qa":
        run_qa_stage()
    else:
        run_writer_stage()


if __name__ == "__main__":
    main()
