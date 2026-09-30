# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_stage2_calibration_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1、委任_08 作業A)
# ============================================================
# 目的: 委任_07で発見されたStage2較正リスク(per-claim Stage2でReal-but-
# fixable群[B1-c/B4-a]がQUALITYへ誤降格)に対し、Fable判定(§1、Safety方向の
# 較正=ユーザー指示の自律範囲)に基づき、rubric較正Trialを実行する。
#
# variant:
# - R1 = 現行rubric(er052_open233_self_recovery_stage2_production_01.
#   MATERIALITY_RUBRIC、対照)。既存出力(B1/B4計6claim分)を再利用し新規
#   callは行わない。
# - R2 = 較正rubric(本ファイルRUBRIC_R2)。QUALITYを「Ledgerに記録された
#   観測同士の関係付け・強調・言い回し」に限定し、Ledgerに無い新規の具体的
#   主張(製品・仕組み・動機・理由・因果・数値・主体・時期)を最優先で
#   BLOCKINGへ倒す。batch(instance単位1call)で新規call。
# - R3 = R2のLLM出力 + post-hoc deterministic floor(Stage1のunsupported_
#   new_claim=trueかつR2のbasisがledger_claim/ledger_scope/ledger_
#   conditions/notes_for_writerのいずれでもない場合、BLOCKINGへ強制)。
#   新規APIコールなし(R2の出力を再利用)。
#
# 重要な設計制約(既存er051/er052系Trialと同一原則):
# - Production code(er003_v1_en_direct_vfl_01_generate.py)は一切変更しない。
# - Model Routing Contractは経由しない。
# - API keyは環境変数のみ。保存jsonにはprompt本体ではなくsha256のみ記録。
# - 既存er052_open233_self_recovery_stage2_production_01.pyは変更しない
#   (rubric較正はTrial専用の本ファイル内で完結させる)。
from __future__ import annotations

import argparse
import json
import os
import time

import er003_v1_en_direct_vfl_01_generate as vfl01
import er050_gpt6_checker_comparison_trial_01 as g6
import er052_open233_self_recovery_phase1_step3_stage1_compare_01 as step3cmp
import er052_open233_self_recovery_stage2_production_01 as s2p

OUT_DIR = "er052_output/open233_self_recovery_stage2_calibration_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233l_a.json"
TOTAL_BUDGET_JPY = 12.0  # 委任_08 作業A Guardrail
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3
N_RUNS = 2  # design書委任文の想定どおりn=2

RUBRIC_R2 = """【材料性(materiality)の判定基準・較正版(R2、委任_08)】
- QUALITY: Ledgerに記録された観測同士の関係付け・強調・言い回しに限る。Ledgerが実際に
  記録した2つ以上の観測を、因果接続詞・強調・言い回しでつないでいるだけで、新しい具体的
  主張を何も追加していない場合のみQUALITYとする。
- BLOCKING: Ledgerに存在しない新規の具体的主張(製品仕様・仕組み・動機・理由・因果関係・
  数値・主体・時期のいずれか)を1つでも追加している場合はBLOCKINGとする。Ledgerのclaim/
  scope/numeric_value/date_or_period/conditionsのいずれかと矛盾する場合、Ledgerが別の
  原因・別の主体を明記しているのに異なるものを述べる場合、notes_for_writerが明示的に
  禁じた断定をしている場合も同様にBLOCKINGとする。「Ledgerの観測と矛盾しない関係付け
  だから」という理由だけでQUALITYへ倒してはならない。新規の具体的主張が1つでも含まれる
  かどうかを最優先で確認すること。
- ACCEPTABLE: Ledgerに無い新規の固有名詞・数値・時期・主体・因果・仕組みを一切加えず
  (Ledgerに既出の固有名詞を繰り返すことはこの制約に抵触しない)、Ledgerが確認した事象の
  一般常識レベルの背景説明・条件付きの一般論にとどまる場合のみ。
- 上記のどれに該当するか迷う場合は、BLOCKINGとしてください(fail-closed)。"""

RUBRIC_R2_PRIME = """【材料性(materiality)の判定基準・較正版(R2'、委任_10)】
以下の手順を**この順番のまま**、各claimに対して段階的に適用してください(前の
ステップでBLOCKINGと確定したら、それ以降のステップは評価しない)。

ステップ1(新規の具体的主張チェック、最優先): このclaimは、Ledgerに存在しない
新規の具体的主張(製品仕様・仕組み・動機・理由・因果関係・数値・主体・時期の
いずれか)を1つでも追加しているか? YESならBLOCKING。
  例(BLOCKINGになる新規具体的主張): 「この現象は、開発チームが過去に行った
  類似のテストと同じ結果だった」(Ledgerに無い『過去の類似テスト』という
  具体的事実を新規追加)。「AIだけでは対応できない場合に人が引き継ぐ」
  (Ledgerに無い具体的な運用フローを新規追加)。
ステップ2(矛盾チェック): Ledgerのclaim/scope/numeric_value/date_or_period/
  conditionsのいずれかと矛盾するか、Ledgerが明記する原因・主体と異なるものを
  述べているか、notes_for_writerが明示的に禁じた断定をしているか? YESなら
  BLOCKING。
ステップ3(Ledger観測の言い換えチェック): Ledgerが実際に記録した1つの観測を、
  語順変更・同義語・平易な言い換えで述べ直しているだけで、新しい主体・数値・
  時期・仕組みを一切加えていないか? YESならACCEPTABLE(言い換え)。
ステップ4(Ledger観測同士の関係付けチェック): Ledgerが実際に記録した2つ以上の
  観測を、因果接続詞・強調・言い回しでつないでいるだけで、新しい具体的主張を
  何も追加していないか? YESならQUALITY。
  例(QUALITY): Ledgerに「人は匿名の相手には話しにくい」という観測と「氏名を
  明かすと話しやすくなる」という観測が別々に記録されている場合、「氏名を
  知っているかどうかで話しやすさが変わる」とまとめて述べるのはQUALITY
  (両方ともLedgerの観測そのものであり、新しい仕組みや因果を追加していない)。
ステップ5(一般常識の背景・条件付き一般論チェック): Ledgerに無い新規の固有
  名詞・数値・時期・主体・因果・仕組みを一切加えず、Ledgerが確認した事象の
  一般常識レベルの背景説明、または「〜であれば/〜の場合」という条件付きの
  一般論(特定の主体・数値・時期を名指ししない)にとどまっているか? YESなら
  ACCEPTABLE。
  例(ACCEPTABLE、一般常識の背景): ある海峡が石油輸送の要衝であるという
  Ledger記載の事実について、「主要な航路は地理的に重要な意味を持つことが
  多い」と一般論として補足する(特定の新事実を追加していない)。
  例(ACCEPTABLE、条件付き一般論): ある商品の価格変動についてのLedger記載の
  事実について、「原材料費が上がれば、関連する製品の価格にも影響しうる」と
  一般的な条件文で補足する(特定の企業名・数値・時期を新たに主張していない)。
ステップ6(fail-closed): 上記のどれにも明確に該当しない、または判断に迷う
  場合は、BLOCKINGとしてください。"""

R3_FLOOR_SAFE_BASIS = {"ledger_claim", "ledger_scope", "ledger_conditions", "notes_for_writer"}

# ------------------------------------------------------------
# RUBRIC_R3_NATURAL_INTERPRETATION(委任_12、iteration4、2026-09-30
# ユーザー指示「許容線の再設計」)。注意: 本ファイル内の既存識別子
# "R3"(RUBRIC_R2 + apply_r3_floor)は委任_08で不採用となった別概念
# (R2 LLM出力+post-hoc floor)であり、本定数はそれとは無関係の新規
# rubric本文である(名称衝突を避けるため変数名は"R3_NATURAL_
# INTERPRETATION"とし、旧R3[floor combo]とは呼称・実体ともに区別する)。
# 位置づけ: RUBRIC_R2(委任_08採用)を置き換える委任_12の新rubric。
# 最重要原則(ユーザー逐語): 「確認済みの事実同士を、人間が普通に読めば
# 自然に導く範囲でつなぐ解釈は許容する。Eigo Radioは英語学習用コンテンツ
# であり、因果を100%立証できない限りNGにはしない」。判断軸は「完全に
# 証明されているか」ではなく「確認済みFactから人間が普通に読めば自然に
# 導く範囲か」。deterministic safety floor(changed_actor/number/negation/
# comparison/time、§4-3、changed_certaintyは委任_12でfloor対象外化)は
# 本rubricとは独立に維持される(post-hocでBLOCKING強制)。
RUBRIC_R3_NATURAL_INTERPRETATION = """【材料性(materiality)の判定基準・自然な解釈版(R3、委任_12、2026-09-30)】
最重要原則: 確認済みのFact同士を、人間が普通に読めば自然に導く範囲で
つなぐ「解釈」は許容してください。Eigo Radioは英語学習用コンテンツであり、
「因果関係を100%立証できない限りNG」にはしません。判断は「完全に証明
されているか」ではなく「確認済みFactから人間が普通に読めば自然に導ける
範囲か」で行ってください。自然な解釈はOK、新しい事実を発明したらNGです。

- BLOCKING(以下のいずれかに明確に該当する場合のみ):
  (a) Ledgerのclaim/scope/numeric_value/date_or_period/conditionsのいずれ
      かと矛盾する。
  (b) Ledgerに無い人物・数字・出来事・具体的な行動・仕組み(メカニズム)を
      新たに追加している(例: 確認されていない具体的な売買行動を事実として
      追加する、確認されていない仕組み・運用フローを新規主張する)。
  (c) 根拠のない人物・組織の意図や動機を断定している。
  (d) Ledgerが記録した事実と逆方向の因果を述べている(Ledgerが原因Xを
      明記しているのに、正反対または別の特定の原因を断定する)。
  (e) 主体・数値・否定・比較・時期のいずれかについて、Ledgerと矛盾する
      重大な変更を加えている。
- QUALITY(Rewriteはしない、通過させる): 確認済みのFact同士を、人間が
  普通に読めば自然に導く範囲でつないだ解釈。断定がやや強い場合や、
  一つの解釈として自然に成り立つ推測("〜が影響した可能性がある"
  "〜が背景かもしれない"程度の解釈、条件付きの一般的な結び付け、市場や
  読者が特定の要因を重視したとみられるという程度の記述)を含む。上記
  BLOCKING列挙に明確に該当しない限りQUALITYとしてください。
- ACCEPTABLE: Ledgerに無い新規の固有名詞・数値・時期・主体・因果・仕組み
  を一切加えず(Ledgerに既出の固有名詞を繰り返すことはこの制約に抵触
  しない)、Ledgerが確認した事象の一般常識レベルの背景説明・条件付きの
  一般論にとどまる。
- tie-break(重要、R2からの変更点): 上記のどれに該当するか迷う場合、
  BLOCKING列挙(a)〜(e)のいずれかに明確に該当しなければQUALITYとして
  ください(NG列挙への該当が明確な場合のみBLOCKING)。「解釈としてやや
  強い」というだけの理由でBLOCKINGへ倒さないでください。ただし、
  Ledgerに無い具体的な人物・数字・出来事・行動・仕組みを新規に追加して
  いる場合は、断定の強さに関わらずBLOCKINGとしてください。"""

# ------------------------------------------------------------
# RUBRIC_R3_PRIME(委任_12、R3単体較正でSafety側誤降格5件[Meta-1/Meta-2/
# hormuz-HF009/A2A3-1/A4-1]を実測したため、fail-closed側へ2点を明確化した
# 改訂版。作業B受入条件「Safety側誤降格0」未達時の1回限りの再較正
# (delegation文どおり)。
# ------------------------------------------------------------
RUBRIC_R3_PRIME = RUBRIC_R3_NATURAL_INTERPRETATION + """

【R3'追加明確化(委任_12、Safety側誤降格の是正)】
以下の2種類は、上記tie-breakでQUALITYへ倒す対象にせず、明確にBLOCKING
に該当するものとして扱ってください:
1. Ledgerが確認していない人物の内心・信念・認識(例:「相手が実際には
   AIだと思っていた」「〜だと思い込んでいた」等、本人が実際にそう思って
   いたという主観的事実)を、状況から推測できるからといって確定した事実
   として述べている場合。これは根拠のない断定(上記(c))に該当します。
2. Ledgerが特定の指標・商品・期間(例: 特定の先物価格や特定の期間の
   観測)についてのみ確認しているのに、それを「市場全体」「価格全般」
   のようなより広い対象・範囲へ一般化して述べている場合。これは新しい
   具体的主張(範囲の追加、上記(b))に該当します。
上記2種類に該当するかどうかを、tie-breakでQUALITYへ倒す前に必ず先に
確認してください。"""


# ------------------------------------------------------------
# RUBRIC_R3_DOUBLE_PRIME(R3''、委任_13 作業B項目2)。Opus L2レビュー#3
# 論点2の文案どおり、R3'追加明確化の2項目を「例示」から「原則」へ
# 書き換える。R3'は「内心の断定」全般・「Ledger観測のscope一般化」全般を
# 一律BLOCKING扱いにしたため、B4-d(驚きという一般的な反応の記述)と
# B1-c(市場の見方の記述、ユーザーが許容例として明示した型)を過剰に
# BLOCKINGへ倒していた(委任_13較正較差、Opus L2 #3論点2)。R3''は
# 対象を「開示・認識の有無そのもの」と「Ledgerの観測値そのもののscope」に
# 限定し、A4-1(利用者の誤認断定)・Meta-1/Meta-2・hormuz-HF009(観測値
# scope拡大)はBLOCKINGのまま維持しつつ、B4-d/B1-cをQUALITYへ戻すことを
# 狙う。RUBRIC_R3_PRIME自体は変更せず(既存iteration4証跡の再現性維持)、
# 新定数として追加する。
# ------------------------------------------------------------
RUBRIC_R3_DOUBLE_PRIME = RUBRIC_R3_NATURAL_INTERPRETATION + """

【R3''追加明確化(委任_13、Opus L2レビュー#3論点2の文案どおり、R3'の
2項目を例示から原則へ置換)】
以下の2種類は、上記tie-breakでQUALITYへ倒す対象にせず、明確にBLOCKING
に該当するものとして扱ってください:
1. 他者の内心を断定する記述のうち、それが「知らされていたか/同意して
   いたか/誤認していたか」という開示・認識の有無そのものを事実として
   述べる場合はBLOCKINGとしてください。驚き・関心・安心などの一般的な
   感情や反応の描写にとどまり、誰が何をしたかという事実関係を変えない
   ものはQUALITYとしてください。
2. Ledgerが特定の指標・銘柄・期間について観測した数値や値動きを、より
   広い対象(市場全体・価格全般など)の観測事実として述べ替える場合は
   BLOCKINGとしてください。市場参加者や読者が何を重視していたとみられる
   かという見方・関心の記述は、これに当たりません。
上記2種類に該当するかどうかを、tie-breakでQUALITYへ倒す前に必ず先に
確認してください。"""


# ------------------------------------------------------------
# RUBRIC_R3_TRIPLE_PRIME(R3'''、委任_13 作業C是正)。R3''単体較正実測
# (er052_output/open233_self_recovery_r3dprime_calibration_01/
# summary_r3dprime_calibration.json)で、B4-d("Meta had run a test that
# produced exactly this kind of surprise.")が2/2ともBLOCKINGのままで
# あることが判明した(受入条件「B4-d/B1-cがQUALITY 2/2」のうちB4-dが未達)。
# モデルの実際のrewrite_hintを確認すると、「相手がAIだと思っていた、
# または人間だと知って驚いた」という*個別の具体的な認識*として解釈して
# いた(R3''項目1の「認識の有無を事実として述べる場合」に該当すると
# 素直に読める、fail-closedとしては妥当な解釈)。是正は原則文のみを
# 修正し(新しい例示は追加しない、委任文の制約どおり)、「Ledgerが既に
# 一般的な傾向として記録している内容を、個別の実例に対する断定ではなく
# 抽象的な言い換えとして参照しているだけの場合」を項目1の適用除外として
# 明確化する。
# ------------------------------------------------------------
RUBRIC_R3_TRIPLE_PRIME = RUBRIC_R3_NATURAL_INTERPRETATION + """

【R3'''追加明確化(委任_13、R3''単体較正でB4-d[驚きの一般的傾向の言い換え]が
2/2ともBLOCKINGだったため、原則文のみをさらに1回限定する。新しい例示は
追加しない)】
以下の2種類は、上記tie-breakでQUALITYへ倒す対象にせず、明確にBLOCKING
に該当するものとして扱ってください:
1. 他者の内心を断定する記述のうち、それが「知らされていたか/同意して
   いたか/誤認していたか」という開示・認識の有無そのものを、特定の
   個別の事実(誰が・いつ・どの状況で実際にそう思った/感じたか)として
   断定している場合はBLOCKINGとしてください。一方、Ledgerが既に一般的な
   傾向・現象として記録している内容を、個別の新しい事実を追加せずに
   抽象的な言い換え・要約として参照しているだけの場合(例えば、ある
   一般的な反応のカテゴリ自体が起きたと述べるにとどまり、特定の個人が
   実際にそう認識していたという新しい個別の事実を追加しない場合)は、
   このBLOCKINGに該当しません。驚き・関心・安心などの一般的な感情や
   反応の描写にとどまり、誰が何をしたかという事実関係を変えないものは
   QUALITYとしてください。
2. Ledgerが特定の指標・銘柄・期間について観測した数値や値動きを、より
   広い対象(市場全体・価格全般など)の観測事実として述べ替える場合は
   BLOCKINGとしてください。市場参加者や読者が何を重視していたとみられる
   かという見方・関心の記述は、これに当たりません。
上記2種類に該当するかどうかを、tie-breakでQUALITYへ倒す前に必ず先に
確認してください。"""


# ------------------------------------------------------------
# RUBRIC_R4_HOOK_AWARE(委任_16 B-2、2026-09-30ユーザー新方針A「Hook-aware」
# §2原因2是正)。委任_14 B-5のHook-aware機構はfloor不発火時のchanged_scope
# 単独発火のみを対象とするpost-hoc downgradeであり、ユーザーが実例として
# 指摘したMeta hook("Ring, ring. A call seemed to come from an AI
# agent...")の実際のflag(changed_fact/changed_certainty/
# unsupported_new_claim)はこの対象外だった(監査
# `docs/pm/audit_hook_aware_and_rewrite_qa_open233_01.md`§A-1・design書
# §6-4)。本rubricはpost-hoc downgradeを置き換えるのではなく(既存floor・
# post-hoc機構はそのまま維持)、Stage2のLLM判定自体にsection_type入力
# (title/hook/in_one_line/body、`detect_claim_section_type`)と、Title/Hook/
# 場面描写/attention grabberに対する原則文を追加する。RUBRIC_R3_TRIPLE_
# PRIME本文は変更しない(既存iteration4/5/6証跡の再現性維持、追記のみ)。
#
# **委任_16 代表ケースTrial実測での是正(作業C、最小修正1回)**: 当初案は
# 適用対象をtitle/hook/in_one_lineの3種としていたが、代表ケース2/3
# (`bgroup_B3`、Safety-critical 10claimの1つ、B3因果"so"claim)を実行した
# ところ、このclaimがsection_type="in_one_line"(In one line欄に集約された
# 要約文)に分類され、Hook-aware原則により意図せずQUALITYへ降格した
# (誤降格、較正済みSafety-critical条件「B3は誤降格0件」に抵触)。
# In one lineは§5-7の役割定義上「短く圧縮して締める」機能であり、
# ユーザー指示(§1)が明示した対象は「Title/Hook/場面描写/attention
# grabber」のみでIn one lineは含まれない。適用対象をtitle/hookの2種のみに
# 限定する(in_one_line/bodyは通常基準のみで判定、既存HOOK_SECTION_TYPES
# [post-hoc downgrade用]はtitle/hook/in_one_lineのまま変更しない、
# post-hoc機構とrubric側の適用範囲は別々に定義されているため相互に影響
# しない)。再実行結果は
# `er052_output/open233_self_recovery_flow_runner_01_rep7/summary_rep7_
# b3_refix.json`参照。
# ------------------------------------------------------------
RUBRIC_R4_HOOK_AWARE = RUBRIC_R3_TRIPLE_PRIME + """

【Hook-aware原則(委任_16 B-2、2026-09-30ユーザー新方針A、代表ケースTrial
実測でtitle/hookの2種のみへ限定[in_one_lineは誤降格の実測により対象外])】
対象claimのsection_type(title/hook/in_one_line/body)がtitle・hookの
いずれかの場合、以下を追加で適用してください。Title・Hook(冒頭の呼びかけ・
情景描写)・attention grabberについては、通常の本文のFact文と同じ基準で
過剰にBLOCKINGにしないでください。確認済みのFactから人間が自然に導ける
演出・情景描写・呼びかけ(具体的な新しい人物・数字・出来事・行動・仕組みを
新たに発明しないもの)は、QUALITYまたはACCEPTABLEとしてください。一方、
section_typeがtitle/hookであることを理由に、確認済みのFactにない新しい
具体的な人物・数字・出来事・行動・仕組みの発明を見逃さないでください
(その場合は通常の本文と同様にBLOCKINGとしてください)。section_typeが
in_one_lineまたはbodyの場合は本項目を適用せず、上記の通常基準のみで
判定してください(In one lineは要約を短く圧縮して締める機能であり、
Hook/Titleの演出許容とは役割が異なります)。"""


# ------------------------------------------------------------
# 委任_27 Part1-5(OPEN-233-SELF-RECOVERY-TRIAL-01、design書§0/§4-18):
# ユーザー上位原則「重大誤解原則」(2026-10-01)をStage2 body判定の最初の
# 問いとして追加する変種。RUBRIC_R3_TRIPLE_PRIME本文は変更せず(既存
# iteration証跡の再現性維持、委任_13/16の教訓どおり)、新定数として追加
# する。priming再測定の要件(委任_16の教訓): 本変種を実際にStage2判定へ
# 配線する場合は、Safety-critical 10 claim + Safety 12 fixtureを必ず
# 同時に対照群として測定し、1件でも誤降格すれば不採用とする(design書
# §4-18・§9-1⑰)。
# ------------------------------------------------------------
MISCONCEPTION_PRINCIPLE_TEXT = """
【重大誤解原則(2026-10-01ユーザー指示、最初の問い)】
まず「この違いは英語学習者に記事の本質について重大な誤解を与えるか」を
判断してください。主要な意味・主体・方向・規模・時間軸を誤認させる場合
のみBLOCKINGとしてください。用語の近似・一般化(例: Brent futures→
oil prices、Brent crude futures→crude prices)・数値丸め(例: 2.6%→
about 3%、above 85 dollars→about 85 dollars)・確認済みFactから自然に
導ける解釈や演出は、厳密には違うというだけの理由でBLOCKINGにしないで
ください。一方、以下のような違いは記事の本質的な誤解を招くため明確に
BLOCKINGとしてください: 特定の指標(例: Brent futures)を無関係な
商品(例: gasoline prices)や世界全体の価格(world energy prices)へ
一般化する、1企業の株価を株式市場全体の動きとして述べる、方向を反転
させる(上昇→下落)、主体を別の主体へ入れ替える、継続していた出来事を
一度消えて戻った出来事として述べる、未確認の人物・行動・動機・具体的な
数字を追加する、因果関係を逆転させる。"""

RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE = (
    RUBRIC_R3_TRIPLE_PRIME + "\n" + MISCONCEPTION_PRINCIPLE_TEXT
)

# ------------------------------------------------------------
# 委任_27 Part2(Hormuz要素Trial A実測、最小修正1回、design書§9-1⑰):
# 初回実測(n=2)でaccept-1("Oil prices did not fall across the whole
# market after the plan was withdrawn.")が2/2ともBLOCKING(false
# BLOCK)のままだった。rewrite_hintを確認すると、LLMは「market全体」を
# 「Brent先物という同じ対象内での一般化」ではなく「無関係な範囲への
# 拡張」と解釈していた。NG群(gasoline/world energy/all crude
# benchmarks)・Safety対照群(B3因果/er009 changed_scope)はいずれも
# 正しくBLOCKING(false PASS 0件)のままだったため、区別の閾値だけを
# 明確化する最小修正を1回行う(rubric本文・MISCONCEPTION_PRINCIPLE_
# TEXT自体は変更せず、新定数として追加し初回実測との再現性を保つ)。
# ------------------------------------------------------------
MISCONCEPTION_PRINCIPLE_TEXT_V2 = MISCONCEPTION_PRINCIPLE_TEXT + """

【追加明確化(委任_27 Part2、Trial A実測でのfalse BLOCK是正、最小修正
1回)】
Brent先物の値動きを「market全体」「oil prices全般」のように、同じ
原油(oil)という対象のままより一般的な言い方に置き換えているだけの
場合は、これも許容される一般化に含めてください(例: "Oil prices did
not fall across the whole market" は、石油という同じ対象内での一般化
であり許容されます)。一方、別の商品(gasoline等)や石油を超えた対象
(world energy全体)へ範囲を広げる場合、または複数の指標をまとめて
「どれも同じだった」のように一般化する場合は、引き続きBLOCKINGと
してください。"""

RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V2 = (
    RUBRIC_R3_TRIPLE_PRIME + "\n" + MISCONCEPTION_PRINCIPLE_TEXT_V2
)


class TrialAbort(RuntimeError):
    pass


def load_budget_state() -> dict:
    if os.path.exists(BUDGET_STATE_PATH):
        with open(BUDGET_STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def save_budget_state(state: dict) -> None:
    os.makedirs(os.path.dirname(BUDGET_STATE_PATH), exist_ok=True)
    with open(BUDGET_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def check_budget(state: dict) -> None:
    if state["cumulative_jpy"] >= TOTAL_BUDGET_JPY:
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.3f}が委任_08 作業A Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# ------------------------------------------------------------
# batch call(rubric差替え版、s2p.run_stage2_batchと同一構造だがrubric_textを
# 引数化する。s2p.py自体は変更しない)
# ------------------------------------------------------------
def run_stage2_batch_variant(client, verified_ledger_text: str, source_article_text: str | None,
                              claims: list, rubric_text: str, model: str = s2p.MODEL) -> dict:
    blocks = []
    for i, c in enumerate(claims):
        blocks.append(
            f"[claim_index={i}]\nclaim: {c['claim_text']}\n"
            f"ローカル文脈(段落±1): {c['local_context']}\n"
            f"origin: {c.get('origin') or '(不明)'}\n"
            f"related_fact_id: {c.get('related_fact_id') or '(不明)'}\n"
            # 委任_16 B-2: section_type(title/hook/in_one_line/body、
            # `detect_claim_section_type`、決定論・¥0)をStage2入力へ
            # 付与する(RUBRIC_R4_HOOK_AWAREのHook-aware原則が参照する)。
            # section_type未付与(旧callerとの後方互換)の場合は'body'扱い。
            f"section_type(title/hook/in_one_line/body): {c.get('section_type') or 'body'}"
        )
    claims_block = "\n\n".join(blocks)
    prompt = s2p.BATCH_PROMPT_TEMPLATE.format(
        verified_ledger_text=verified_ledger_text,
        source_article_text=source_article_text or "(なし)",
        claims_block=claims_block,
        materiality_rubric=rubric_text,
        rewrite_hint_instruction=s2p.REWRITE_HINT_INSTRUCTION,
    )
    t0 = time.time()
    response = client.responses.create(
        model=model,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **s2p.BATCH_JSON_SCHEMA}},
        input=[
            {"role": "developer", "content": s2p.STAGE2_PROD_DEVELOPER_MESSAGE},
            {"role": "user", "content": prompt},
        ],
    )
    elapsed = round(time.time() - t0, 3)
    parsed = json.loads(response.output_text)
    usage_dict = s2p._extract_usage(response)
    return {
        "prompt_sha256": s2p.sha256_text(prompt), "parsed": parsed, "model": response.model,
        "response_id": response.id, "usage": usage_dict,
        "cost_jpy": round(s2p.official_cost_jpy(usage_dict), 4), "elapsed_seconds": elapsed,
    }


# ------------------------------------------------------------
# 評価セット(14 instance相当、13 batch call)の構築
# ------------------------------------------------------------
def _claim(sub_id, claim_text, correct_label, origin=None, related_fact_id=None,
           unsupported_new_claim=False):
    return {
        "sub_id": sub_id, "claim_text": claim_text, "correct_label": correct_label,
        "origin": origin, "related_fact_id": related_fact_id,
        "unsupported_new_claim": unsupported_new_claim,
    }


def build_eval_groups() -> list:
    g6_step2 = {f["id"]: f for f in g6.step2_fixtures()}
    g6_step1 = {f["id"]: f for f in g6.step1_fixtures()}
    g6_step3 = {f["id"]: f for f in g6.step3_fixtures()}

    b1 = g6_step2["B1"]
    b2 = g6_step2["B2_hormuz"]
    b3 = g6_step2["B3"]
    b4 = g6_step2["B4"]
    meta = g6_step2["Meta_run03_standard"]
    hormuz = g6_step3["hormuz_run03_standard"]

    groups = [
        {
            "group_id": "B1", "fixture": b1,
            "claims": [
                _claim("B1-a", "ホルムズ海峡は、中東から原油を運ぶ船が多く通る重要な海の道だ。",
                       "ACCEPTABLE", unsupported_new_claim=False),
                _claim("B1-b", "「原油価格が高い状態が続けば、ガソリンや輸送費など、私たちの身近な"
                       "価格にも影響する。」", "ACCEPTABLE", unsupported_new_claim=True),
                _claim("B1-c", "「市場が見ているのは『言葉』より海の安全」「投資家が気にしているの"
                       "は、20％の料金案が残るかどうかだけではない」とし、海上の危険がBrent価格の"
                       "反発を説明するかのように述べている。", "BLOCKING", unsupported_new_claim=True),
            ],
        },
        {
            "group_id": "B2", "fixture": b2,
            "claims": [
                _claim("B2", "The disappearance of the fee plan did not lead to a large, lasting "
                       "fall in prices. So the price reacted once, then returned to a high level.",
                       "QUALITY", origin="ja_source", related_fact_id="HF-009",
                       unsupported_new_claim=False),
            ],
        },
        {
            "group_id": "B3", "fixture": b3,
            "claims": [
                _claim("B3", "“Concerns about US-Iran attacks, the sea blockade, and tanker "
                       "safety continued on July 14, so the flashy 20% plan left the stage” "
                       "links the continuing concerns causally to the plan’s withdrawal.",
                       "BLOCKING", origin="ja_source", related_fact_id="HF-007",
                       unsupported_new_claim=True),
            ],
        },
        {
            "group_id": "B4", "fixture": b4,
            "claims": [
                _claim("B4-d", "“Meta had run a test that produced exactly this kind of "
                       "surprise.”", "BLOCKING", origin="translation",
                       related_fact_id="MUSE-HC-006", unsupported_new_claim=True),
                _claim("B4-a", "“A person can take over when AI alone has trouble.”",
                       "BLOCKING", origin="ja_source", related_fact_id="MUSE-HC-002",
                       unsupported_new_claim=True),
                _claim("B4-b", "“People feel differently when they think they are speaking to "
                       "a machine and when they know a person is listening. Names, plans, and "
                       "private matters are easier to share when you know who is hearing them.”",
                       "QUALITY", origin="ja_source", related_fact_id="MUSE-HC-010",
                       unsupported_new_claim=True),
                _claim("B4-c", "“As AI makes calls and reservations, useful features make "
                       "people want to know whether AI or a person is on the other end.”",
                       "QUALITY", origin="ja_source", related_fact_id="MUSE-HC-004",
                       unsupported_new_claim=True),
            ],
        },
        {
            "group_id": "Meta_run03_standard", "fixture": meta,
            "claims": [
                _claim("Meta-1", meta["baseline_parsed"]["deviations"][0]["claim_in_article"],
                       "BLOCKING", origin="translation", related_fact_id="MUSE-HC-010",
                       unsupported_new_claim=True),
                _claim("Meta-2", meta["baseline_parsed"]["deviations"][1]["claim_in_article"]
                       if len(meta["baseline_parsed"]["deviations"]) > 1 else
                       meta["baseline_parsed"]["deviations"][0]["claim_in_article"],
                       "BLOCKING", origin="ja_source", related_fact_id="MUSE-HC-012",
                       unsupported_new_claim=True),
            ],
        },
        {
            "group_id": "hormuz_run03_standard", "fixture": hormuz,
            "claims": [
                _claim("hormuz-HF009", "Oil prices did not fall across the whole market after the "
                       "plan was withdrawn.", "BLOCKING", origin="ja_source",
                       related_fact_id="HF-009", unsupported_new_claim=True),
            ],
        },
    ]

    for fixture_id, path in step3cmp.NEGATIVE_SOURCE_FILES:
        if fixture_id not in ("neg1_meta_b3prod_a2", "neg2_meta_refresh_a2",
                               "neg3_hormuz_prodrunner_b1b", "neg5_hormuz_div_a2"):
            continue
        fx = step3cmp.load_negative_fixture(fixture_id, path)
        devs = fx["baseline_parsed"]["deviations"] if fx.get("baseline_parsed") else []
        claim_text = devs[0]["claim_in_article"] if devs else "(claim not found in baseline)"
        unc = bool(devs[0].get("unsupported_new_claim")) if devs else True
        groups.append({
            "group_id": fixture_id, "fixture": fx,
            "claims": [_claim(fixture_id, claim_text, "NOT_BLOCKING(ACCEPTABLE/QUALITY)",
                               unsupported_new_claim=unc)],
        })

    for fid in ["A2A3", "A4", "A5"]:
        fx = g6_step1[fid]
        path = f"er051_output/open233_checker_trial_01/trial_02/step1/{fid}/V4A/run_1.json"
        with open(path, encoding="utf-8") as f:
            v4a = json.load(f)
        devs = [dv for dv in v4a["parsed"]["deviations"] if dv.get("severity_final") == "BLOCKING"]
        claims = []
        for i, dv in enumerate(devs):
            claims.append(_claim(f"{fid}-{i}", dv.get("claim_in_article", ""), "BLOCKING",
                                  origin=dv.get("origin"), related_fact_id=dv.get("related_fact_id"),
                                  unsupported_new_claim=bool(dv.get("unsupported_new_claim"))))
        groups.append({"group_id": fid, "fixture": fx, "claims": claims})

    return groups


def build_claim_records_for_group(group: dict) -> list:
    fixture = group["fixture"]
    out = []
    for c in group["claims"]:
        local_context, fallback = s2p.build_local_context(fixture["article_text"], c["claim_text"])
        out.append({**c, "local_context": local_context, "fallback_used": fallback})
    return out


# ------------------------------------------------------------
# R1(既存出力の再利用、0 call)
# ------------------------------------------------------------
R1_EXISTING_MAP = {
    "B1-c": "er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/"
            "per_claim_vs_batch/B1/per_claim_0.json",
    "B1-b": "er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/"
            "per_claim_vs_batch/B1/per_claim_1.json",
    "B4-d": "er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/"
            "per_claim_vs_batch/B4/per_claim_0.json",
    "B4-a": "er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/"
            "per_claim_vs_batch/B4/per_claim_1.json",
    "B4-b": "er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/"
            "per_claim_vs_batch/B4/per_claim_2.json",
    "B4-c": "er052_output/open233_self_recovery_phase1_step4_stage2_unitcost_01/"
            "per_claim_vs_batch/B4/per_claim_3.json",
}


def load_r1_existing() -> dict:
    out = {}
    for sub_id, path in R1_EXISTING_MAP.items():
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        out[sub_id] = {"materiality": d["parsed"]["materiality"], "basis": d["parsed"]["basis"],
                        "source_path": path, "cost_jpy": 0.0, "call_type": "reused_existing_0call"}
    return out


def apply_r3_floor(r2_materiality: str, r2_basis: str, unsupported_new_claim: bool) -> tuple:
    if unsupported_new_claim and r2_basis not in R3_FLOOR_SAFE_BASIS and r2_materiality != "BLOCKING":
        return "BLOCKING", True
    return r2_materiality, False


def guarded_batch_call(state: dict, consecutive_errors: list, label: str, save_path: str, **kwargs) -> dict:
    check_budget(state)
    last_err = None
    result = None
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = run_stage2_batch_variant(**kwargs)
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    state["cumulative_calls"] += 1
    if result is not None:
        state["cumulative_jpy"] += result["cost_jpy"]
        state["history"].append({"label": label, "cost_jpy": result["cost_jpy"], "usage": result["usage"]})
        save_json(save_path, {"label": label, **result})
        consecutive_errors[0] = 0
    else:
        state["cumulative_errors"] += 1
        save_json(save_path, {"label": label, "error": last_err})
        consecutive_errors[0] += 1
    save_budget_state(state)
    if consecutive_errors[0] >= MAX_CONSECUTIVE_ERRORS:
        raise TrialAbort(f"API errorが{MAX_CONSECUTIVE_ERRORS}call連続(STOP条件)")
    return result if result is not None else {"error": last_err}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_runs", type=int, default=N_RUNS)
    args = parser.parse_args()

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]
    groups = build_eval_groups()
    r1_existing = load_r1_existing()

    stopped, stop_reason = False, None
    r2_runs = {}  # group_id -> [run1_parsed, run2_parsed, ...]
    per_claim_rows = []

    try:
        for run_idx in range(1, args.n_runs + 1):
            for group in groups:
                claims = build_claim_records_for_group(group)
                fixture = group["fixture"]
                label = f"{group['group_id']}_R2_run{run_idx}"
                save_path = f"{OUT_DIR}/R2/{group['group_id']}/run_{run_idx}.json"
                res = guarded_batch_call(
                    state, consecutive_errors, label, save_path,
                    client=client, verified_ledger_text=fixture["ledger_text"],
                    source_article_text=fixture.get("source_article_text"),
                    claims=claims, rubric_text=RUBRIC_R2,
                )
                r2_runs.setdefault(group["group_id"], []).append({
                    "run": run_idx, "claims": claims, "result": res,
                })
    except TrialAbort as e:
        stopped = True
        stop_reason = str(e)

    # 集計: claim単位でR1(reused)/R2(実測、n runs)/R3(post-hoc)を並べる
    for group in groups:
        gid = group["group_id"]
        runs = r2_runs.get(gid, [])
        for c in group["claims"]:
            sub_id = c["sub_id"]
            r1 = r1_existing.get(sub_id)
            r2_labels = []
            r3_labels = []
            for run in runs:
                if "error" in run["result"]:
                    continue
                judgments = run["result"]["parsed"].get("judgments", [])
                claim_idx = [cc["sub_id"] for cc in run["claims"]].index(sub_id)
                match = next((j for j in judgments if j.get("claim_index") == claim_idx), None)
                if match is None:
                    continue
                r2_labels.append(match["materiality"])
                r3_label, overridden = apply_r3_floor(match["materiality"], match["basis"],
                                                       c["unsupported_new_claim"])
                r3_labels.append({"label": r3_label, "floor_overridden": overridden,
                                   "r2_basis": match["basis"]})
            per_claim_rows.append({
                "group_id": gid, "sub_id": sub_id, "correct_label": c["correct_label"],
                "origin": c["origin"], "related_fact_id": c["related_fact_id"],
                "unsupported_new_claim": c["unsupported_new_claim"],
                "r1": r1, "r2_labels_by_run": r2_labels, "r3_labels_by_run": r3_labels,
            })

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "n_runs": args.n_runs, "n_groups": len(groups),
    }
    save_json(f"{OUT_DIR}/summary_stage2_calibration.json", {
        "summary": summary, "per_claim_rows": per_claim_rows,
    })
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
