# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1 ⑥、委任_09)
# ============================================================
# 目的: design_open233_self_recovery_flow_01.md §3〜§8で確定したStage 1→2→3
# →Recheckの一連のSelf-Recovery Flowを、既存の個別実測モジュール
# (er052_open233_self_recovery_{precheck,stage2_production,stage2_calibration,
# stage3_rewrite_trial}_01.py)をimportして1本のTrial runnerへ統合し、
# 代表fixture群に対して通しで実行する(統合dry-run、委任_09)。
#
# 重要な設計制約(既存er051/er052系Trialと同一原則、本ファイルも遵守):
# - Production code(er003/er009/er010/er012/er019)は一切変更しない
#   (本ファイルはer010.rewrite_ng_item/generate_rewriteを直接呼ばず、
#   §5-2-補2確定案どおりE-2[最小1-shot Prompt]のみを使う独立実装のため、
#   er010に対するmonkeypatchも行わない)。
# - Model Routing Contractは経由しない。API keyは環境変数のみ。
#   保存jsonにはprompt本体ではなくsha256のみ記録。
# - **[委任_09で実際に検出・修正した実装上の注意]** 既存Trialモジュール
#   (`er052_open233_self_recovery_stage3_rewrite_trial_01.py`='s3rt')の
#   `simple_llm_call`は、そのモジュール自身の`record_call`/
#   `save_budget_state`(`s3rt.BUDGET_STATE_PATH`=既存委任_08の証跡
#   ファイル)を内部で呼ぶため、そのまま流用すると**他委任の既存証跡
#   ファイルを上書き汚染する**(本委任の実行中に実際に発生、
#   `git checkout`で復元済み)。本ファイルは`s3rt`のPrompt定数
#   (`J1_DEVELOPER_MSG`)とpure関数(`extract_json_obj`)のみを読み取り
#   専用で借用し、API呼び出し・budget記録は本ファイル自身の
#   `simple_llm_call`(下記)で完結させる。
# - 真のProduction JA Fact Check(er002系)・JA Writer O cascade(er019)は
#   呼び出さない。V4A variant checker(er051)をJA/EN両方の文面に適用する
#   近似で代用する(委任_08と同一のスコープ限界、§5-4-補2に既述)。
#
# 本ファイル固有の設計判断(委任_09、Trial限定・報告のみ・独断でrubric等を
# 変更しない):
# 1. Stage 1は「既存fixtureに同一入力のV4A出力が既に存在する場合は再利用
#    (0 call)、無ければ新規実行」(委任文どおり)。fixture一覧・reuse元
#    パスはbuild_target_instances()に列挙する(全て既存artifact/実データ
#    由来、新規fixtureの捏造はしない)。
# 2. Stage 3のRewrite機構は、claimのorigin文字列だけでなく「fixtureが
#    JA/EN双方の本文(article_text+source_article_text)を実際に持つか」
#    も条件に加えて選択する(paired local rewrite[J-1]はJA/EN双方の本文が
#    ある場合のみ意味を持つため)。JA/EN pairingが無いfixture(例: B1=JA
#    Original単体チェック)は、claimが検出された「その言語のテキスト単体」
#    への局所編集+同一言語でのRecheckとする(委任_08のdelete型実測[B1-c
#    はJA本文への直接削除+JA Recheck]と同一方式の一般化)。
# 3. replace_with_ledger_value型・narrow_scope型(単一言語)は、委任_08で
#    確定した第一候補E-2(最小1-shot Prompt)一本化とする(E-1
#    escalationはn=2実測で一度も発火しておらず[§5-4-補2]、E-1固有の
#    per-claim機械検証[verify_fn]は個別fixtureごとの正解文字列を要求する
#    ため、任意fixtureを横断する本汎用runnerでは実装しない。最終的な
#    正否は全文Recheck[fail-closed]が担保する、既存設計の権限分担どおり)。
# 4. guard抵触時の段階的フォールバック(§5-2/§5-4)は、本runnerでは
#    「対象文局所編集の1回再試行」までを実装し、その次段階(旧案B/
#    既存全文must-fix retryへのフォールバック)は「全文に対する最小編集
#    指示(対象文以外は変えないという指示付きの全文Rewrite、J-2/旧案Bの
#    近似)」として言語を問わず統一実装する(委任_08のJ-2実装[JA]の
#    考え方をEN/JA共通の汎用フォールバックへ一般化したもの、既知の限界
#    として報告する)。
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import time

import er003_ja_to_en_translation as jtr
import er003_v1_en_direct_vfl_01_generate as vfl01
import er010_ledger_local_rewrite_09 as er010
import er050_gpt6_checker_comparison_trial_01 as g6
import er051_open233_checker_trial_variant_01 as trial
import er052_open233_self_recovery_phase1_step3_stage1_compare_01 as step3cmp
import er052_open233_self_recovery_precheck_01 as precheck
import er052_open233_self_recovery_s1d_trial_01 as s1d
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_self_recovery_stage2_hook_01 as s2h
import er052_open233_self_recovery_stage2_production_01 as s2p
import er052_open233_self_recovery_stage3_rewrite_trial_01 as s3rt

# 委任_10(iteration 2): 既存委任_09の出力(OUT_DIR_ITER1、budget_state_
# c233m.json)は変更しない。iteration 2の出力は別ディレクトリへ書く
# (rewrite_hint/J-1改善/claim identity正規化/delete再出現確認/S1-U variant
# を含む再実行、委任文§0)。Stage1(V4A)は既存V4A出力(OUT_DIR_ITER1と同一
# fixture)をそのまま再利用するため、reuseパス自体はcommitted_09時点の
# 既存artifactを参照し続ける(Stage1のprompt自体は不変のため二重課金しない)。
OUT_DIR_ITER1 = "er052_output/open233_self_recovery_flow_runner_01"
OUT_DIR_ITER2 = "er052_output/open233_self_recovery_flow_runner_01_iter2"
# 委任_11(iteration 3): 既存iteration1/2の出力(OUT_DIR_ITER1/OUT_DIR_ITER2)
# は変更しない。iteration 3の出力は別ディレクトリへ書く(Opus L2 #2の
# バグ修正2件+停止判定是正+段落単位Rewrite+測定是正+Rewrite由来逸脱検出+
# S1-U安価代替の反映後の再実行、委任文§0/§4)。Stage1(V4A)は既存出力を
# sha256一致で再利用する(build_target_instances()のstage1_source自体は
# iteration 1時点のartifactを参照し続ける、二重課金防止)。
OUT_DIR_ITER3 = "er052_output/open233_self_recovery_flow_runner_01_iter3"
# 委任_12(iteration4): 既存iteration1/2/3の出力(OUT_DIR_ITER1/ITER2/ITER3)
# は変更しない。iteration4の出力は別ディレクトリへ書く(Stage2 rubric R3
# [自然な解釈基準]+floor改訂[changed_certainty除外]+追加測定7項目の反映後の
# 再実行、委任文§0/§2/§3)。入力deviation集合はiteration3と同一固定
# (paired比較のため、Stage1 reuseパス自体はiteration1時点のartifactを
# 参照し続ける、二重課金防止は変更しない)。
OUT_DIR_ITER4 = "er052_output/open233_self_recovery_flow_runner_01_iter4"
# 委任_13(iteration5): 既存iteration1〜4の出力(OUT_DIR_ITER1/ITER2/ITER3/
# ITER4)は変更しない。iteration5の出力は別ディレクトリへ書く(Opus L2 #3
# 所見反映=R3''+Stage2 2-of-2+cite-or-release+品質劣化検出v2+Rewrite品質
# 制約の反映後、29 instance n=2で再実行、委任文§2/§3/§4)。入力deviation
# 集合はiteration3/4と同一固定(paired比較のため、Stage1 reuseパス自体は
# iteration1時点のartifactを参照し続ける、二重課金防止は変更しない)。
OUT_DIR_ITER5 = "er052_output/open233_self_recovery_flow_runner_01_iter5"
# 委任_14(iteration6): 既存iteration1〜5の出力(OUT_DIR_ITER1〜4/
# OUT_DIR_ITER5)は変更しない。iteration6の出力は別ディレクトリへ書く
# (丸め許容+floor-cited variant+最小変更ラダー+セクション役割維持+
# Hook-aware統合+コスト5分割の反映後、29 instance n=2で再実行、
# 委任文§3-D)。入力deviation集合はiteration3〜5と同一固定(paired比較の
# ため、Stage1 reuseパス自体はiteration1時点のartifactを参照し続ける、
# 二重課金防止は変更しない)。
OUT_DIR_ITER6 = "er052_output/open233_self_recovery_flow_runner_01_iter6"
# 委任_16(iteration7-rep、2026-09-30): 既存iteration1〜6の出力
# (OUT_DIR_ITER1〜5/OUT_DIR_ITER6)は変更しない。J-1最小変更ラダー(B-1)+
# Hook-aware Stage2 rubric拡張(B-2)の反映後、代表5ケースのみをn=2で実行
# する(委任文§3-C、29 instance全量再実行は本委任スコープ外)。出力は
# 新規ディレクトリ(`_rep7`)へ書く。
OUT_DIR_REP7 = "er052_output/open233_self_recovery_flow_runner_01_rep7"
# 委任_17(2026-09-30): 既存iteration1〜6・rep7の出力(OUT_DIR_ITER1〜6/
# OUT_DIR_REP7)は変更しない。Hook専用Stage2(s2h、title/hookのclaimのみを
# 別Prompt・別callで判定し、既存body Stage2[R3''']とは完全に分離する)の
# 反映後、代表5ケースのみをn=2で再実行する(委任文§3-B、広いTrialは
# スコープ外)。出力は新規ディレクトリ(`_rep8`)へ書く。
OUT_DIR_REP8 = "er052_output/open233_self_recovery_flow_runner_01_rep8"
# 委任_18(2026-09-30): 既存iteration1〜6・rep7・rep8の出力(OUT_DIR_ITER1〜6/
# OUT_DIR_REP7/OUT_DIR_REP8)は変更しない。局所QA統合/全体Rewrite経路是正
# (⑥の例外化+precheck合成マーカー実文解決)/不要Rewrite4件の解決策
# (disclosure-gap downgrade)/Escalation 2 run是正(fact_id複数箇所cycle
# 緩和)/degenerate output guardの反映後、代表12 instanceのみをn=2で
# 再実行する(委任文§3-B、広いTrialはスコープ外)。出力は新規ディレクトリ
# (`_rep9`)へ書く。
OUT_DIR_REP9 = "er052_output/open233_self_recovery_flow_runner_01_rep9"
# 委任_19(2026-09-30): 既存iteration1〜6・rep7〜rep9の出力(OUT_DIR_ITER1〜6/
# OUT_DIR_REP7〜9)は変更しない。full_recheck_required条件(f)新設
# (repeat_fact_id)/find_sentence_context locateバグ是正/escalate_to_
# paragraph(A-2)の反映後、限定7 instance(hormuz_run03_standard/
# neg3_hormuz_prodrunner_b1b/bgroup_B3/hormuz_run02_advanced/
# safety_er009_changed_number/safety_A2A3/safety_A5)のみをn=2で再実行する
# (委任文§2 B、広いTrialはスコープ外)。出力は新規ディレクトリ(`_rep10`)へ
# 書く。
OUT_DIR_REP10 = "er052_output/open233_self_recovery_flow_runner_01_rep10"
# 委任_20(2026-09-30、Opus L2レビュー#4是正W1〜W5): 既存iteration1〜6・
# rep7〜rep10の出力(OUT_DIR_ITER1〜6/OUT_DIR_REP7〜10)は変更しない。
# W1(JA fail-openガード封鎖)/W2(Stage1同一fact_id列挙)/W3(全文Recheck
# 条件更新)の反映後、fastpathが実際に起動できる代表4 instance
# (hormuz_run03_standard/bgroup_B3/meta_run03_standard/
# neg1_meta_b3prod_a2)のみをn=2で再実行する(委任文§3 W4、広いTrialは
# スコープ外)。出力は新規ディレクトリ(`_rep11`)へ書く。
OUT_DIR_REP11 = "er052_output/open233_self_recovery_flow_runner_01_rep11"
# 委任_21(2026-09-30、rep11で判明した3欠陥の是正+微小Trial rep12): 既存
# iteration1〜6・rep7〜rep11の出力(OUT_DIR_ITER1〜6/OUT_DIR_REP7〜11)は
# 変更しない。A-1(JA fail-openガードの言語判定是正)/A-2(局所QA
# find_sentence_context複数文needle是正)の反映後、`bgroup_B3`/
# `neg1_meta_b3prod_a2`/`meta_run03_standard`/`hormuz_run02_standard`の
# 限定4 instanceのみをn=2で再実行する(委任文§2 B、広いTrialはスコープ外)。
# 出力は新規ディレクトリ(`_rep12`)へ書く。
OUT_DIR_REP12 = "er052_output/open233_self_recovery_flow_runner_01_rep12"
# 委任_22(2026-10-01、bgroup_B3の等価QA gating是正+Gate 9項目確認+広い
# Trial iteration 7): 既存iteration1〜6・rep7〜rep12の出力(OUT_DIR_
# ITER1〜6/OUT_DIR_REP7〜12)は変更しない。Part A(A-1是正、
# `resolve_ja_ok_after_equivalence_gating`新設)の再確認として`bgroup_B3`
# のみをn=2で再実行する(委任文§1 A-2、出力は新規ディレクトリ`_rep13`)。
OUT_DIR_REP13 = "er052_output/open233_self_recovery_flow_runner_01_rep13"
# Part B(委任文§2、広いTrial iteration 7、29 instance)の出力は別ディレクト
# リ(`_iter7`)へ書く。
OUT_DIR_ITER7 = "er052_output/open233_self_recovery_flow_runner_01_iter7"
# 委任_23(2026-10-01、iter7未達2点の原因特定・設計修正・少数ケース確認):
# 既存iteration1〜7・rep7〜13の出力は変更しない。A-2(hormuz_run03_standard
# real_run Escalation真因是正: JA/EN等価gatingの過剰保守[determinate JA
# でも既に確認済みのja_okをREVIEW_REQUIREDだけで覆していた]+reuse fixture
# 向けsame_fact_id決定論フォールバック)/B-2(⑥[全体Rewrite/削除]を標準
# ラダーから外す、iter7実測で7/7が最終STAGE4だった=Evidence 0件のため
# feature flag既定OFF)の反映後、`hormuz_run03_standard`×n=2+`safety_A4`
# ×n=1の少数ケースを再実行する(委任文§2 D、budget_stateパス明示)。
# 出力は新規ディレクトリ(`_rep14`)へ書く。
OUT_DIR_REP14 = "er052_output/open233_self_recovery_flow_runner_01_rep14"
# 委任_24(2026-10-01、hormuz_run03_standard第三要因[ラダー未昇段のまま
# §3-3安全網が先に発火]の是正+少数確認): 既存iteration1〜7・rep7〜14の
# 出力は変更しない。A-2(同一claim再発を、④段落水準まで既に試行済みの
# 場合[escalated_to_paragraph=True]のみSTAGE4[same_claim_fact_id_
# reblocked]へ回し、未昇段の場合は§6-6 A-2の既存ラダー前進機構[escalate_
# to_paragraph]へ合流させループを継続)の反映後、`hormuz_run03_standard`
# ×n=2(reuse Stage1)+`bgroup_B4`×n=1+`safety_A2A3`×n=1の少数ケースを
# 再実行する(委任文§2 B、budget_stateパス明示)。出力は新規ディレクトリ
# (`_rep15`)へ書く。
OUT_DIR_REP15 = "er052_output/open233_self_recovery_flow_runner_01_rep15"
# 委任_30(2026-10-01、Hook境界群の最終小修正+重大誤解原則のrunner既定化+
# 実記事代表5ケースend-to-end確認): 既存iteration1〜7・rep7〜15の出力は
# 変更しない。Part2(本既定化、ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT=
# True)反映後、`hormuz_run03_standard`/`neg1_meta_b3prod_a2`/
# `neg3_hormuz_prodrunner_b1b`/`meta_run03_standard`/`bgroup_B3`の5
# instanceをStage1 fresh・n=2で再実行する(委任文Part3、budget_stateパス
# 明示)。出力は新規ディレクトリ(`_rep16`)へ書く。
OUT_DIR_REP16 = "er052_output/open233_self_recovery_flow_runner_01_rep16"
# 委任_30 Part3続き(neg3 FAIL是正の反映後、sample2残り4 instanceの再開):
# sample1完走時点でrep16単体が既に¥10.3338(Part3当初Guardrail¥10をわずかに
# 超過、check_budgetは呼び出し前判定のため最終callで超過すること自体は
# 既存の仕様どおり)。委任全体Guardrail¥15(Part1[¥0.7637]+本委任neg3
# 単体fix検証[¥0.0758]を含む)の残り約¥3.8の範囲内でsample2を完走させる
# ため、rep16単体の上限をここまで引き上げる(委任全体の新しい支出枠を
# 追加するものではなく、既承認の¥15の範囲内でのサブGuardrail再配分)。
# 委任_31(2026-10-01、rep16の残3点の是正と再確認): 既存iteration1〜7・
# rep7〜16の出力は変更しない。Part1の是正((a)actor置換ガード常時評価・
# (b)Hook境界拡張+body rubric V5)反映後、`neg1_meta_b3prod_a2`/
# `neg3_hormuz_prodrunner_b1b`をStage1 fresh・n=2で再実行する(委任文
# Part2、budget_stateパス明示)。出力は新規ディレクトリ(`_rep17`)へ書く。
# Part2のGuardrail¥8のうち、Safety-critical 8claim V5再確認(別budget
# state、`er052_open233_element_trial_safety_control_03.py`)で既に
# ¥1.6243を使用済みのため、本rep17自身の上限は残り約¥6.37の範囲内で
# 自己停止するよう¥6.3に設定する(委任全体Guardrail¥10を超えないための
# サブGuardrail配分)。
OUT_DIR_REP17 = "er052_output/open233_self_recovery_flow_runner_01_rep17"
# 委任_32(iter8、2026-10-01、広いTrial iteration8=重大誤解原則・要素Trial
# 修正の横断安定性確認、ユーザー承認済み): 既存iteration1〜7・rep7〜17の
# 出力(OUT_DIR_ITER1〜7/OUT_DIR_REP7〜17)は変更しない。本委任は29
# instance全量(うち9 instanceはn=2、20 instanceはn=1)を、既定構成
# (Stage1 V4-A+重大誤解原則/Stage2 V5/Hook V4、ENABLE_MISCONCEPTION_
# PRINCIPLE_DEFAULT=True)でStage1 fresh再実行する(reuse fixtureは原則
# 配線前の出力のため使わない。Safety 12 fixtureのみ構造上の理由で
# reuseのまま、詳細はREPORT§30参照)。出力は新規ディレクトリ(`_iter8`)へ書く。
OUT_DIR_ITER8 = "er052_output/open233_self_recovery_flow_runner_01_iter8"
# 委任_33(rep18、2026-10-01、design書§4-25/§9-1): 既存iteration1〜8・
# rep7〜17の出力(OUT_DIR_ITER1〜8/OUT_DIR_REP7〜17)は変更しない。body
# rubric V6(委任_32で検出したB3[HF-007]/A2A3-0[HF-003]誤降格の是正)の
# full flow確認として、`bgroup_B3`(Stage1 fresh・n=2)・`safety_A2A3`
# (Stage1 reuse・n=2)・`meta_run03_standard`(Stage1 fresh)をfull flowで
# 再実行する(委任文Guardrail¥13の一部、詳細はREPORT§31参照)。出力は
# 新規ディレクトリ(`_rep18`)へ書く。
OUT_DIR_REP18 = "er052_output/open233_self_recovery_flow_runner_01_rep18"
# 委任_34(rep19、2026-10-01、委任文§2 B): 既存iteration1〜8・rep7〜18の
# 出力(OUT_DIR_ITER1〜8/OUT_DIR_REP7〜18)は変更しない。iter8の
# meta_run03_standard(s1/s2)のcycle1 Stage1出力(fresh、同一事実の多箇所
# 列挙を含む、両sample同一内容)をそのままreuse入力として固定
# (`stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`、
# `stage1_mode="reuse"`へ上書き)し、現行既定構成(V6・actorガード・局所
# QA・JA fail-open封鎖・escalate_to_paragraph OFF・⑥OFF)で2回
# (iter8のs1/s2それぞれ1run)実行する。出力は新規ディレクトリ(`_rep19`)へ書く。
OUT_DIR_REP19 = "er052_output/open233_self_recovery_flow_runner_01_rep19"
# 委任_35(rep20、2026-10-01、委任文§2 B): 既存iteration1〜8・rep7〜19の
# 出力(OUT_DIR_ITER1〜8/OUT_DIR_REP7〜19)は変更しない。(d)是正(floorの
# fact_id単位broadcast廃止+same_fact_id_locations列挙のcycle1限定+
# iol_degenerate guard追加)後、rep19と同じfrozen fixture
# (`stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`、
# OUT_DIR_REP19から読み込む、再freezeしない)をn=2で再検証する。Safety
# 対照(changed_number/changed_actor fixture各1件full flow n=1、
# Safety-critical 8のStage2のみn=1)も同じOUT_DIR_REP20・同じbudget
# stateで実行する。出力は新規ディレクトリ(`_rep20`)へ書く。
OUT_DIR_REP20 = "er052_output/open233_self_recovery_flow_runner_01_rep20"
# 委任_36(rep21、2026-10-01、委任文§2 C): 既存iteration1〜8・rep7〜20の
# 出力(OUT_DIR_ITER1〜8/OUT_DIR_REP7〜20)は変更しない。rep20 sample2
# cycle2のladder_exhausted_without_full_rewrite根本原因(claim_textが
# 同一fact_idの非隣接2文を“…” and “…”で結合した合成claimの場合、
# locate_target()が1文fuzzy matchしか試みず断片の一方を見落とす、§6-18)の
# 是正(locate_multi_quote_span新設+locate_target/run_paired_local_rewriteの
# ja_target決定への組み込み)後、rep19/rep20と同じfrozen fixture
# (`stage1_fixtures/meta_run03_standard_iter8_cycle1_frozen.json`、
# OUT_DIR_REP19から読み込む、再freezeしない)をn=2で再検証する。Safety
# 対照(changed_number fixture1件full flow n=1)も同じOUT_DIR_REP21・同じ
# budget stateで実行する。出力は新規ディレクトリ(`_rep21`)へ書く。
OUT_DIR_REP21 = "er052_output/open233_self_recovery_flow_runner_01_rep21"
OUT_DIR = OUT_DIR_REP21
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233am_36_rep21.json"
TOTAL_BUDGET_JPY = 6.5  # 委任_36 Guardrail¥7のうち、¥0.5をhard marginとして
# 残し、本runnerのAPI呼び出し全体(rep21本体+Safety対照)を¥6.5で自己停止
# する。
MAX_RETRIES_PER_CALL = 2
MAX_CONSECUTIVE_ERRORS = 3
MODEL = "gpt-6-luna"
MAX_CYCLES = 2
# 委任_11 作業B-3(§3-3停止判定の是正): 別claim(fact_id同一だが本文相違、
# またはfact_id無しの新規claim)に限り、blocking件数が厳密に減少している
# 場合だけcycle 3を1回許可する(上限3、Opus L2 #2論点1推奨3)。
HARD_MAX_CYCLES = MAX_CYCLES + 1
CLAIM_TEXT_SIMILARITY_THRESHOLD = 0.75

# 委任_23 B-2(iter7実測、29 instance全量規模): ⑥(全体Rewrite/削除、
# `6_full_article`)が7件(18.4%)発生したが、①〜⑤([委任_14既定で②⑤は
# ①④へ統合済み]・delete含む)の試行記録を精査した結果、7件とも最終的に
# STAGE4_ESCALATIONへ到達しており(worst_cost内訳の主因、safety_A4は
# 7 rewrite operations)「⑥が必要だった」Evidence(⑥使用がそのまま
# 解消[RESOLVED_REWRITE]に至った例)が0/7だった(REPORT§23 B参照)。
# ①〜④/delete全段でguardが失敗した場合、⑥を試みず直ちにStage4
# (stage4_reason="ladder_exhausted_without_full_rewrite")へ回す。
# コードは削除せずfeature flag(既定OFF)として残す。Trueに戻すと
# iter7以前と同じ①〜⑥の挙動に戻る(再有効化はFable/ユーザー判断、
# 設計書§5-10参照)。
ENABLE_LADDER_LEVEL_6_FULL_REWRITE = False

# 委任_27 Part1-1(design書§0-4/§5-11、ユーザー上位原則「重大誤解原則」の
# 明文化に伴う是正): §6-6 A-2で導入した`escalate_to_paragraph`(同一
# fact_idのclaimが別文言・別箇所で再出現した場合、①単語・接続詞/③1文を
# 飛ばし④段落水準から試す「同じFactが再登場したら段落Rewrite」ルール)を
# 廃止する。上位原則は「各箇所は独立に初期単位から判断する」であり、
# 再出現という事実だけでラダーの開始水準を引き上げるのは原則と整合しない。
# コードは削除せず、本flag(既定OFF)でガードする(再有効化時の参照用)。
# 同一fact_id再発の検出・記録自体(`prior_blocking_records`・
# `same_claim_reblocked_escalated_to_paragraph`ログ・§3-3の
# `same_claim_fact_id_reblocked`STAGE4判定)は無変更(Rewriteが効かな
# かったことの実証によるfail-closedという別の安全機構であり、本委任の
# スコープ外)。
ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP = False

# 委任_30 Part2(design書§0/§9-1「既定構成の確定(要素Trial反映)」):
# 上位原則「重大誤解原則」(2026-10-01ユーザー指示)をStage1/Stage2(body)/
# Hook専用Stage2の既定経路へ実配線する。委任_27〜29の要素Trial(Hormuz
# Trial A、Safety対照群n=2公式測定、Meta要素Trial B/C、委任_30 Part1の
# Hook V4 boundary-1是正)で、Safety-critical/Safety12/Hormuz許容・NG/
# Hook許容・境界・NG群のいずれも非回帰(false downgrade/false pass 0件)を
# 確認済みのため、既定をTrueへ昇格する。Falseに戻すと重大誤解原則配線前
# (iteration1〜7・rep7〜15と同一)の挙動に戻る(再有効化はFable/ユーザー
# 判断、既存iteration/rep証跡は本フラグの既定値変更と無関係[既にOUT_DIRが
# 固定済み])。
# 委任_31 Part1(b)(design書§4-24): body rubricの既定をV4からV5(neg1の
# 不要Rewrite是正の防御層、「受け手側の驚き・反応は新規Factではない」の
# 1段落追加)へ昇格する。Safety-critical 8claim(B3を含む、n=1、
# `er052_open233_element_trial_safety_control_03.py`)で誤降格0件を確認
# 済み(priming再測定の要件どおり)。Falseに戻すと重大誤解原則配線前
# (iteration1〜7・rep7〜15と同一)の挙動に戻る。
#
# 委任_33(design書§4-25/§7-0-iter32): 広いTrial iteration8(委任_32)で
# full flow(Stage1→Stage2→Rewrite→Recheck)実行時にB3(HF-007)/A2A3-0
# (HF-003)の誤降格を新規検出したため、V5からV6(既存BLOCKING列挙(d)/(b)の
# 許容/NG対比例示を追加、新しい判定基準の追加ではない)へ昇格する。rep18
# (`er052_open233_self_recovery_rep18_v6_confirm_01.py`)でSafety-critical
# 8claim/Hormuz許容5・NG5/bgroup_B3・safety_A2A3のfull flow再確認を実施
# 済み(詳細はREPORT§31)。Falseに戻すと重大誤解原則配線前(iteration1〜7・
# rep7〜15と同一)の挙動に戻る。
ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT = True
BODY_RUBRIC_DEFAULT = (
    s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V6
    if ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT else s2c.RUBRIC_R3_TRIPLE_PRIME
)
HOOK_RUBRIC_DEFAULT = (
    s2h.HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V4
    if ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT else s2h.HOOK_RUBRIC
)

# 委任_27 Part1-2(design書§0-4/§5-11): 問題種類→初期Rewrite単位の写像。
# Stage1のdeterministic floor flag(dev)から決定論(¥0、LLM呼び出しなし)
# で問題種類を分類し、ラダーの開始水準を決める。devにfloor flagが一つも
# 無い場合(既存fixture互換)は`unspecified`とし、既存の挙動(①から開始)
# を維持する(後方互換、既存unittestの結果を変えない)。
LADDER_LEVEL_RANK = {"1_word_connective": 1, "3_sentence": 2, "4_paragraph": 3}
PROBLEM_KIND_INITIAL_RANK = {
    "term_scope": 1, "causality": 1, "actor": 1, "time": 1, "unspecified": 1,
    "sentence_logic": 2, "multi_sentence": 3,
    "rounding": 0,  # 0 = Rewriteを試行しない(levels=[]、§0-4「原則Rewriteなし」)
}
# §4-3既存の残り5種(term_scope/causality/actor/time以外でfloor対象の
# floor flag)。このうち1個だけ該当すれば1文水準(sentence_logic)、2個
# 以上同時該当すれば段落水準(multi_sentence、複数文の整合崩れ)とする。
_LOGIC_FLOOR_FLAGS = (
    "changed_negation", "changed_comparison", "changed_certainty",
    "changed_fact", "unsupported_new_claim",
)


def classify_problem_kind(dev: dict) -> str:
    """委任_27 Part1-2: Stage1 deterministic floor flag(dev)から問題種類を
    分類する(¥0、決定論)。優先順位はterm_scope→rounding→causality→
    actor→timeの順(dev flagが複数同時に立つ場合、より限定的な初期単位を
    優先する)。"""
    if not isinstance(dev, dict):
        dev = {}
    if dev.get("changed_scope"):
        return "term_scope"
    if dev.get("changed_number") and dev.get("changed_number_suppressed_reason"):
        return "rounding"
    if dev.get("changed_causality"):
        return "causality"
    if dev.get("changed_actor"):
        return "actor"
    if dev.get("changed_time"):
        return "time"
    logic_hits = [f for f in _LOGIC_FLOOR_FLAGS if dev.get(f)]
    if len(logic_hits) >= 2:
        return "multi_sentence"
    if len(logic_hits) == 1:
        return "sentence_logic"
    return "unspecified"


def filter_levels_by_problem_kind(levels: list, dev: dict) -> list:
    """levels(①→③→④の順に構築済み)を、classify_problem_kindが決めた
    初期水準未満のlevelを除外して返す。初期水準より上位への昇段(guard
    失敗時のfallback)は妨げない(「初期単位」は開始点であり上限では
    ない)。rounding(初期rank0)のみ例外的に空listを返す(Rewrite不試行、
    §0-4「原則Rewriteなし」)。"""
    initial_rank = PROBLEM_KIND_INITIAL_RANK.get(classify_problem_kind(dev), 1)
    if initial_rank <= 0:
        return []
    return [lv for lv in levels if LADDER_LEVEL_RANK.get(lv["name"], 1) >= initial_rank]


# 委任_27 Part1-3(design書§0-5): 主体・対象の置換ガード。Rewrite後に
# 新しく現れた一般的な役割名詞(主体語)が、Ledger本文(fact本文全体を
# 含むledger_text、¥0・決定論の部分文字列一致)に一語も含まれない場合は
# Rewriteを却下する(未確認の具体主体への置換防止)。新しい主体語が
# 一つも導入されていない場合(既存語の保持・削除のみ)は常にTrueを返す
# (このガードの対象外)。
_ACTOR_NOUN_PATTERN = re.compile(
    r"\b(users?|employees?|workers?|staff|contractors?|agents?|executives?|"
    r"customers?|clients?|spokespeople|spokesperson|engineers?|managers?|"
    r"officials?|residents?|drivers?|passengers?|patients?|students?|teachers?|"
    r"analysts?|traders?|investors?|shareholders?)\b",
    re.IGNORECASE,
)


def extract_actor_nouns(text: str) -> set:
    return {m.group(0).lower() for m in _ACTOR_NOUN_PATTERN.finditer(text or "")}


def actor_rewrite_guard_ok(before_text: str, after_text: str, ledger_text: str) -> bool:
    new_actors = extract_actor_nouns(after_text) - extract_actor_nouns(before_text)
    if not new_actors:
        return True
    ledger_lower = (ledger_text or "").lower()
    return all(a in ledger_lower for a in new_actors)


# 委任_12(iteration4、§4-3改訂): changed_certaintyをfloorから除外する。
# 理由(ユーザー指示・自然な解釈基準への是正): ユーザーNG列挙5項目
# (actor/number/negation/comparison/time)にchanged_certaintyは含まれず、
# 「断定がやや強い」はQUALITY側(許容)に整理された。委任_04で追加した
# changed_certaintyのfloor化はB4-dを安全側(fail-closed)に倒すための
# 暫定措置だったが、B4-d(確実性強化)は委任_12でQUALITYへ再ラベルされた
# ため(§7-0改訂)、floorに残すとStage2 rubric(R3)のQUALITY判定と矛盾する。
# pre-check floor(detected_by=="precheck")は変更なく維持する。
FLOOR_FLAGS = [
    "changed_actor", "changed_number", "changed_negation",
    "changed_comparison", "changed_time",
]

# 委任_11 作業B-5(§8測定是正、Opus L2 #2論点5/6): 群別Escalation率算出のため、
# 「実run(現行Production記事に相当する6 instance)」を明示的に区別する
# (合成Safety/B群/negativeは正解ラベル付きfixtureであり、実記事の分母には
# 混ぜない、Opus L2 #2論点5)。
REAL_RUN_INSTANCE_IDS = frozenset({
    "hormuz_run01_advanced", "hormuz_run02_advanced", "hormuz_run03_advanced",
    "hormuz_run03_standard", "meta_run03_standard", "meta_run03_advanced",
})

# 委任_11 作業B-5(§8測定是正、Opus L2 #2論点6): 記事単位(Standard+Advanced
# 合算)のコスト・合否を集計するためのarticle_id -> instance_idグループ
# (Standardが存在しないrun_01/run_02はAdvanced単体、既知のデータ限界)。
ARTICLE_GROUPS = {
    "hormuz_run01": ["hormuz_run01_advanced"],
    "hormuz_run02": ["hormuz_run02_advanced"],
    "hormuz_run03": ["hormuz_run03_advanced", "hormuz_run03_standard"],
    "meta_run03": ["meta_run03_advanced", "meta_run03_standard"],
}

# 委任_11 作業B-5(§8測定是正、Opus L2 #2論点2): S1-U追加BLOCKの正解ラベル
# 照合用(委任_09/_10で確定した既知のStage1 recall miss実例=真陽性、
# negative群でのS1-U追加BLOCKは偽陽性、それ以外はラベル無し)。
KNOWN_RECALL_MISS_INSTANCE_IDS = frozenset({"bgroup_B2_hormuz", "bgroup_B3", "hormuz_run02_advanced"})

# 委任_12(iteration4、§8追加測定7項目): 「正常記事」= §7-0/§7-5で正解
# ラベルが全claim ACCEPTABLE(=一切のBLOCKING claimを含まないことが期待
# される)instance群。negative候補7件+Normal群2件(hormuz_run03_advanced/
# meta_run03_advanced)。この群に限り「Stage1/Stage2でBLOCKされた=自然な
# 解釈なのに誤ってBLOCKされた」を機械的・一意に定義できる(B/Safety群は
# instance内にBLOCKINGが混在するclaim単位judgeであり、instance単位では
# 判定できないため対象外、報告時に限界として明記する)。
NORMAL_GROUP_INSTANCE_IDS = frozenset(
    {fid for fid, _ in step3cmp.NEGATIVE_SOURCE_FILES} | {"hormuz_run03_advanced", "meta_run03_advanced"}
)

_HEDGE_WORD_RE = re.compile(r"\b(may|might|possibly|perhaps|could|seem(?:s|ed)?|appear(?:s|ed)?)\b", re.IGNORECASE)


def measure_rewrite_quality_degradation(before_text: str, after_text: str) -> dict:
    """委任_12(iteration4、§8): Rewrite前後で読み物品質を損ねたか候補判定
    (決定論、¥0)。観点: 文数減少率・弱め表現[may/might/possibly/seems等]の
    増加数・段落数変化・タイトル(先頭行)変更。閾値は保守的(過検出よりは
    見逃し側)に設定し、「候補」であることを明記する(人間の主観評価の
    代替ではない)。"""
    def _sentence_count(t: str) -> int:
        return len([s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s.strip()])

    def _paragraph_count(t: str) -> int:
        return len(s2p.split_paragraphs(t))

    def _title(t: str) -> str:
        lines = [ln for ln in t.strip().split("\n") if ln.strip()]
        return lines[0].strip() if lines else ""

    sc_before, sc_after = _sentence_count(before_text), _sentence_count(after_text)
    pc_before, pc_after = _paragraph_count(before_text), _paragraph_count(after_text)
    hedge_before = len(_HEDGE_WORD_RE.findall(before_text))
    hedge_after = len(_HEDGE_WORD_RE.findall(after_text))
    title_before, title_after = _title(before_text), _title(after_text)

    sentence_drop_rate = round((sc_before - sc_after) / sc_before, 4) if sc_before else 0.0
    hedge_increase = hedge_after - hedge_before
    paragraph_delta = pc_after - pc_before
    title_changed = title_before != title_after and bool(title_before) and bool(title_after)

    degradation_candidate = (
        sentence_drop_rate >= 0.2 or hedge_increase >= 3 or paragraph_delta < 0 or title_changed
    )
    return {
        "sentence_count_before": sc_before, "sentence_count_after": sc_after,
        "sentence_drop_rate": sentence_drop_rate,
        "hedge_word_count_before": hedge_before, "hedge_word_count_after": hedge_after,
        "hedge_word_increase": hedge_increase,
        "paragraph_count_before": pc_before, "paragraph_count_after": pc_after,
        "paragraph_delta": paragraph_delta,
        "title_changed": title_changed,
        "degradation_candidate": degradation_candidate,
    }


# ------------------------------------------------------------
# 品質劣化検出v2(委任_13、iteration5、Opus L2レビュー#3論点6-B/総合項目5)。
# iteration4の`measure_rewrite_quality_degradation`(文数/段落数/hedge語数/
# タイトル変更)は、実際にiter4で起きた4種類の劣化(hook喪失・重複段落・
# 接続破断・語彙難化)のうち3種類(neg1 cycle2の重複段落、neg2の接続破断、
# neg3/neg5/B2の語彙難化)を検出できなかった(Opus L2 #3論点6-B実例)。
# v2は(a)連続段落の類似度による重複検出、(b)段落先頭の孤立逆接語検出、
# (c)平均文長・難語率比較、(d)タイトル・第1段落変更の常時フラグ、を追加する
# (決定論・¥0、既存v1関数は変更せずiter4比較用に残す)。
# ------------------------------------------------------------
_PARAGRAPH_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "for", "with",
    "is", "are", "was", "were", "it", "its", "that", "this", "as", "by", "at",
    "be", "had", "have", "has", "not", "so", "from", "than", "then",
})
_WORD_RE = re.compile(r"[A-Za-z']+")
_CONTRASTIVE_OPENER_RE = re.compile(r"^(But|However|Yet|Still|Though|Nevertheless)\b", re.IGNORECASE)
_VOWEL_GROUP_RE = re.compile(r"[aeiouyAEIOUY]+")


def _split_paragraphs_nonheading(text: str) -> list:
    return [p.strip() for p in text.split("\n\n") if p.strip() and not p.strip().startswith("#")]


def _normalize_tokens_for_jaccard(text: str) -> set:
    words = [w.lower() for w in _WORD_RE.findall(text)]
    return {w for w in words if w not in _PARAGRAPH_STOPWORDS and len(w) > 2}


def _jaccard_similarity(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    union = len(a | b)
    return len(a & b) / union if union else 0.0


def detect_duplicate_paragraphs(after_text: str, threshold: float = 0.4) -> list:
    """(a) 連続段落の類似度(正規化後token Jaccard >= threshold)による重複検出。
    neg1 cycle2実例(「Meta tested having trained contract workers...」の直後に
    「Meta had tested having trained human contractors...」という、ほぼ同一内容の
    段落が連続した事故)を検出対象とする。閾値は当初案(0.6)ではこの実例
    (jaccard=0.5)を検出できなかったため0.4へ調整した(同一記事内の他の
    隣接段落ペア12組の実測ではjaccard最大0.292、次点との差が明確なため
    過検出リスクは低いと判断、委任_13 iteration5)。"""
    paragraphs = _split_paragraphs_nonheading(after_text)
    tokensets = [_normalize_tokens_for_jaccard(p) for p in paragraphs]
    flagged = []
    for i in range(len(paragraphs) - 1):
        sim = _jaccard_similarity(tokensets[i], tokensets[i + 1])
        if sim >= threshold:
            flagged.append({"index_a": i, "index_b": i + 1, "jaccard": round(sim, 3),
                             "paragraph_a": paragraphs[i][:160], "paragraph_b": paragraphs[i + 1][:160]})
    return flagged


def detect_orphan_contrastive_paragraphs(before_text: str, after_text: str) -> list:
    """(b) 段落先頭の孤立逆接語(But/However/Yet/Still等)検出。neg2実例
    (「People who asked Muse...」等の対応主張が削られた結果、「But sometimes,
    a human was speaking instead.」という先行文のない逆接で段落が始まった事故)
    を検出対象とする。Rewrite前には存在しなかった(=Rewriteで新規に生じた)
    逆接始まりの段落のみをflagする(誤検出抑制、before_textにも同一段落が
    既に存在する場合はflagしない)。"""
    before_paragraphs = {p for p in _split_paragraphs_nonheading(before_text)}
    after_paragraphs = _split_paragraphs_nonheading(after_text)
    flagged = []
    for i, p in enumerate(after_paragraphs):
        first_line = p.split("\n", 1)[0].strip()
        first_sentence = re.split(r"(?<=[.!?])\s+", first_line)[0] if first_line else ""
        if _CONTRASTIVE_OPENER_RE.match(first_sentence) and p not in before_paragraphs:
            flagged.append({"paragraph_index": i, "opening": first_sentence[:100]})
    return flagged


def _syllable_estimate(word: str) -> int:
    return max(1, len(_VOWEL_GROUP_RE.findall(word)))


def _difficulty_stats(text: str) -> dict:
    """(c) 平均文長・難語率の算出(音節数[母音塊カウント]>=3、または文字数
    >=9の語を「難語」とみなす簡易ヒューリスティック、決定論・¥0)。"""
    words = _WORD_RE.findall(text)
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if not words or not sentences:
        return {"avg_sentence_len": 0.0, "difficult_word_ratio": 0.0, "word_count": len(words)}
    difficult = sum(1 for w in words if _syllable_estimate(w) >= 3 or len(w) >= 9)
    return {
        "avg_sentence_len": round(len(words) / len(sentences), 2),
        "difficult_word_ratio": round(difficult / len(words), 4),
        "word_count": len(words),
    }


def _paragraph_title(t: str) -> str:
    lines = [ln for ln in t.strip().split("\n") if ln.strip()]
    return lines[0].strip() if lines else ""


def _first_body_paragraph(t: str) -> str:
    paras = _split_paragraphs_nonheading(t)
    return paras[0] if paras else ""


def _hook_paragraph_block(t: str) -> str:
    """委任_31 Part1(b)是正(design書§4-24): Hookセクションの範囲を
    「冒頭段落全体(Hook導入文+その締め文)」へ拡張する。`_first_body_
    paragraph`(段落①のみ)の既知の限界(§4-14コメント参照、「hookが実質
    2段落以上にまたがる記事であっても常にparas[0]のみをhook候補として
    扱う」)を、neg1実例(段落①=場面描写、段落②=“Meta had run a test
    that caused exactly this surprise.”という1文の締め文)に限定して解消
    する。第2段落を無条件にHookへ含めると、hormuz/meta_run03_standard/
    bgroup_B3/neg3実測(段落②が複数文・具体的な数字/日付を含む本文段落)で
    Safety回帰(本文のmaterial claimをHook専用[緩やか]rubricへ誤って
    振り分けるリスク)が生じるため、意図的に保守的な決定論ヒューリスティック
    (¥0)で絞る: 第2段落が(a)1文のみ、かつ(b)数字を含まない場合に限り
    Hookへ含める(「締め文」=曖昧な演出の1文という想定に合致する場合のみ)。
    それ以外(複数文、または具体的な数字/日付を含む)は従来どおり段落①のみ
    を返す(body/in_one_lineの既存ルーティングは変更しない)。"""
    paras = _split_paragraphs_nonheading(t)
    if not paras:
        return ""
    if len(paras) < 2:
        return paras[0]
    second = paras[1]
    sentence_count = len([s for s in re.split(r"(?<=[.!?])\s+", second.strip()) if s])
    has_digit = bool(re.search(r"\d", second))
    if sentence_count <= 1 and not has_digit:
        return paras[0] + "\n\n" + second
    return paras[0]


def measure_rewrite_quality_degradation_v2(before_text: str, after_text: str,
                                            changed_fragments: list | None = None) -> dict:
    """委任_13(iteration5)品質劣化検出v2。(a)重複段落、(b)孤立逆接語、
    (c)文長・難語率上昇、(d)タイトル/第1段落(hook)変更、を検出する。
    (a)(b)(c)のいずれかを検出した場合のみ`needs_regeneration=True`とし、
    Stage3側で1回だけ再生成する判断材料に使う((d)はhookが正当な理由で
    変わる場合[BLOCKING claim自体がhookにある場合]があるため、単独では
    再生成トリガにしない、常時フラグとして報告のみ)。
    `changed_fragments`(before_fragment/after_fragmentのペアlist、
    single_text_rewrite/paired_rewriteが返すもの)を渡すと、全文平均
    (段落・記事丸ごとの変化が薄まる、実測でneg3/B2のような1文だけの局所
    難語化は全文平均では閾値未満になることを確認)に加え、実際に書き換え
    られた断片同士でも難語率・文長を比較し、いずれかが閾値を超えれば
    `vocab_difficulty_increased=True`とする(局所的な語彙難化の検出感度を
    上げるための追加判定、全文判定を置き換えるものではない)。"""
    dup = detect_duplicate_paragraphs(after_text)
    orphan = detect_orphan_contrastive_paragraphs(before_text, after_text)
    stats_before = _difficulty_stats(before_text)
    stats_after = _difficulty_stats(after_text)
    sentence_len_increase = round(stats_after["avg_sentence_len"] - stats_before["avg_sentence_len"], 2)
    difficulty_ratio_increase = round(stats_after["difficult_word_ratio"] - stats_before["difficult_word_ratio"], 4)
    vocab_difficulty_increased_wholetext = bool(
        (stats_before["avg_sentence_len"] and sentence_len_increase >= 3.0) or difficulty_ratio_increase >= 0.05
    )

    fragment_stats_before = fragment_stats_after = None
    fragment_sentence_len_increase = fragment_difficulty_ratio_increase = 0.0
    vocab_difficulty_increased_fragment = False
    pairs = [(p.get("before"), p.get("after")) for p in (changed_fragments or [])
             if p.get("before") and p.get("after")]
    if pairs:
        before_concat = " ".join(b for b, _ in pairs)
        after_concat = " ".join(a for _, a in pairs)
        fragment_stats_before = _difficulty_stats(before_concat)
        fragment_stats_after = _difficulty_stats(after_concat)
        fragment_sentence_len_increase = round(
            fragment_stats_after["avg_sentence_len"] - fragment_stats_before["avg_sentence_len"], 2)
        fragment_difficulty_ratio_increase = round(
            fragment_stats_after["difficult_word_ratio"] - fragment_stats_before["difficult_word_ratio"], 4)
        vocab_difficulty_increased_fragment = bool(
            (fragment_stats_before["avg_sentence_len"] and fragment_sentence_len_increase >= 3.0)
            or fragment_difficulty_ratio_increase >= 0.05
        )
    vocab_difficulty_increased = vocab_difficulty_increased_wholetext or vocab_difficulty_increased_fragment

    title_changed = _paragraph_title(before_text) != _paragraph_title(after_text)
    first_paragraph_changed = _first_body_paragraph(before_text) != _first_body_paragraph(after_text)

    reasons = []
    if dup:
        reasons.append(f"duplicate_paragraph(jaccard={dup[0]['jaccard']})")
    if orphan:
        reasons.append(f"orphan_contrastive_opener({orphan[0]['opening']!r})")
    if vocab_difficulty_increased_wholetext:
        reasons.append(
            f"vocab_difficulty_increased_wholetext(sentence_len+{sentence_len_increase},"
            f"difficult_ratio+{difficulty_ratio_increase})"
        )
    if vocab_difficulty_increased_fragment:
        reasons.append(
            f"vocab_difficulty_increased_fragment(sentence_len+{fragment_sentence_len_increase},"
            f"difficult_ratio+{fragment_difficulty_ratio_increase})"
        )

    return {
        "duplicate_paragraphs": dup, "duplicate_paragraph_detected": bool(dup),
        "orphan_contrastive_paragraphs": orphan, "orphan_contrastive_detected": bool(orphan),
        "stats_before": stats_before, "stats_after": stats_after,
        "sentence_len_increase": sentence_len_increase,
        "difficulty_ratio_increase": difficulty_ratio_increase,
        "fragment_stats_before": fragment_stats_before, "fragment_stats_after": fragment_stats_after,
        "fragment_sentence_len_increase": fragment_sentence_len_increase,
        "fragment_difficulty_ratio_increase": fragment_difficulty_ratio_increase,
        "vocab_difficulty_increased_wholetext": vocab_difficulty_increased_wholetext,
        "vocab_difficulty_increased_fragment": vocab_difficulty_increased_fragment,
        "vocab_difficulty_increased": vocab_difficulty_increased,
        "title_changed": title_changed, "first_paragraph_changed": first_paragraph_changed,
        "hook_or_title_changed": title_changed or first_paragraph_changed,
        "needs_regeneration": bool(dup) or bool(orphan) or vocab_difficulty_increased,
        "reasons": "; ".join(reasons),
    }


# ------------------------------------------------------------
# 委任_14 作業B-4(2026-09-30ユーザー新方針item5): Title=引きつける/
# Hook=演出・興味喚起/本文=ストーリー性・読みやすさ/In one line=短く圧縮
# して締める、という各パートの役割をRewrite後も維持しているかを決定論的に
# 検出する(¥0)。In one lineの長文化(語数+30%超)・タイトル/In one lineへの
# 数字追加・Hookの縮小/レトリック消失・タイトルのレトリック消失を検出し、
# measure_rewrite_quality_degradation_v2と統合して既存の再生成トリガへ
# 合流させる(新しい再生成機構は作らない)。
# ------------------------------------------------------------
_DIGIT_RE = re.compile(r"\d")
_RHETORICAL_MARKER_RE = re.compile(r'[?!]|"[^"]{3,}"|\bimagine\b|\bwhat if\b', re.IGNORECASE)


def measure_section_role_violation(before_text: str, after_text: str) -> dict:
    title_before, title_after = _paragraph_title(before_text), _paragraph_title(after_text)
    hook_before, hook_after = _first_body_paragraph(before_text), _first_body_paragraph(after_text)
    iol_before, iol_after = _extract_in_one_line_text(before_text), _extract_in_one_line_text(after_text)

    iol_words_before = len(_WORD_RE.findall(iol_before))
    iol_words_after = len(_WORD_RE.findall(iol_after))
    iol_length_increase_ratio = (
        round((iol_words_after - iol_words_before) / iol_words_before, 4) if iol_words_before else 0.0
    )
    iol_too_long = iol_words_before > 0 and iol_length_increase_ratio > 0.30

    numbers_added_title = len(_DIGIT_RE.findall(title_after)) > len(_DIGIT_RE.findall(title_before))
    numbers_added_iol = len(_DIGIT_RE.findall(iol_after)) > len(_DIGIT_RE.findall(iol_before))

    hook_words_before = len(_WORD_RE.findall(hook_before))
    hook_words_after = len(_WORD_RE.findall(hook_after))
    hook_shrank = hook_words_before > 0 and hook_words_after < hook_words_before * 0.5
    hook_markers_before = len(_RHETORICAL_MARKER_RE.findall(hook_before))
    hook_markers_after = len(_RHETORICAL_MARKER_RE.findall(hook_after))
    hook_flattened = hook_before != hook_after and hook_markers_before > 0 and hook_markers_after == 0

    title_markers_before = len(_RHETORICAL_MARKER_RE.findall(title_before))
    title_markers_after = len(_RHETORICAL_MARKER_RE.findall(title_after))
    title_flattened = title_before != title_after and title_markers_before > 0 and title_markers_after == 0

    # 委任_18 2-1(c)(disclosure §1-1-4「タイトル全文削除→空文字列の検出
    # 漏れ」是正): 削除型Rewriteでtitle/hookが空文字、またはtitleが極端に
    # 短縮(語数<3)された場合をFAILとして検出する(¥0、決定論)。既存の
    # hook_shrank(50%未満)より厳しい「空/ほぼ空」専用の判定を別フラグとして
    # 持ち、呼び出し側run_instanceでこれを検出したcycleはRecheckの結果に
    # 関わらず無条件でSTAGE4へ回す(単なる再生成トリガではなくhard block、
    # 既存needs_regenerationとは異なる新しい安全装置)。
    title_words_after = len(_WORD_RE.findall(title_after))
    title_degenerate = bool(title_before.strip()) and title_after != title_before and (
        not title_after.strip() or title_words_after < 3
    )
    hook_degenerate = bool(hook_before.strip()) and hook_after != hook_before and not hook_after.strip()
    # 委任_35(design書§6-16、Rewrite品質ガード追加): title_degenerate/
    # hook_degenerateと同じ理由で、「## In one line」見出し自体が削除され
    # 空文字列抽出になった場合(rep19実測cycle3、見出し行ごと消失し
    # `_extract_in_one_line_text`が空文字を返した、§32-3参照)をFAILとして
    # 検出する。iol_too_long(長文化)とは別の「消失」専用フラグであり、
    # 既存のneeds_regeneration系トリガとは異なる新しい安全装置ではなく、
    # title_degenerate/hook_degenerateと同じ既存hard-block機構へ単に合流
    # させる(run_instance側の判定行への追加のみ)。
    iol_degenerate = bool(iol_before.strip()) and iol_after != iol_before and not iol_after.strip()

    reasons = []
    if iol_too_long:
        reasons.append(f"in_one_line_too_long(+{round(iol_length_increase_ratio * 100, 1)}%)")
    if numbers_added_title:
        reasons.append("numbers_added_to_title")
    if numbers_added_iol:
        reasons.append("numbers_added_to_in_one_line")
    if hook_shrank:
        reasons.append(f"hook_shrank({hook_words_before}->{hook_words_after}words)")
    if hook_flattened:
        reasons.append("hook_rhetorical_markers_lost")
    if title_flattened:
        reasons.append("title_rhetorical_markers_lost")
    if title_degenerate:
        reasons.append(f"title_degenerate(words_after={title_words_after})")
    if hook_degenerate:
        reasons.append("hook_degenerate(emptied)")
    if iol_degenerate:
        reasons.append("in_one_line_degenerate(heading_removed_or_emptied)")

    return {
        "in_one_line_length_increase_ratio": iol_length_increase_ratio, "in_one_line_too_long": iol_too_long,
        "numbers_added_to_title": numbers_added_title, "numbers_added_to_in_one_line": numbers_added_iol,
        "hook_word_count_before": hook_words_before, "hook_word_count_after": hook_words_after,
        "hook_shrank": hook_shrank, "hook_rhetorical_markers_lost": hook_flattened,
        "title_rhetorical_markers_lost": title_flattened,
        "title_word_count_after": title_words_after,
        "title_degenerate": title_degenerate, "hook_degenerate": hook_degenerate,
        "iol_degenerate": iol_degenerate,
        "section_role_violated": bool(reasons), "reasons": "; ".join(reasons),
    }


# ------------------------------------------------------------
# Rewrite品質制約(委任_13、iteration5、Fable追加指示): 対象レベル
# (Standard=A2、Advanced=B1B)の語彙・文長制約+hook保持+削除優先を、
# rewrite_hintへ追記する形でStage3 Promptへ注入する(既存テンプレート
# 自体[E2/J1/FULL_TEXT_FALLBACK]は変更せず、既に{rewrite_hint}を埋め込む
# 箇所があるため非侵襲)。語彙制約文はProduction Prompt定数
# (er012_b_family_voices_a2_production_01.A2_TABLE_PRINCIPLES_JA、
# CURRENT_SPEC.md「B1(独立生成Natural Spoken News English)」節)を読んで
# 要約引用したもの(Production自体は呼び出さない、read-only参照)。
# ------------------------------------------------------------
QUALITY_CONSTRAINT_COMMON = (
    "\n\n[Quality constraints for this rewrite]\n"
    "1. Preserve the title and the opening hook/narrative device unless the BLOCKING claim itself is "
    "located there; if the flagged issue is elsewhere, do not remove or flatten the title/hook.\n"
    "2. If deleting the unsupported part fully resolves the issue, prefer deletion over rephrasing. "
    "Do not add new information, new vocabulary, or new claims while rewriting.\n"
    "3. Do not repeat, in a different paragraph, content that already appears elsewhere in the article."
)
LEVEL_CONSTRAINT_A2 = (
    "\n4. This article targets CEFR-A2 English listeners (Standard level; source: CURRENT_SPEC.md "
    "\"CEFR-A2 structure/audio spec\", quoted via er012_b_family_voices_a2_production_01."
    "A2_TABLE_PRINCIPLES_JA). Keep vocabulary plain and everyday; average sentence length about 11 "
    "words, no sentence longer than about 18 words; one idea per sentence; avoid dense financial or "
    "technical vocabulary (e.g. prefer \"prices went up a little, then went back down\" over \"prices "
    "pared gains\")."
)
LEVEL_CONSTRAINT_B1B = (
    "\n4. This article targets B1 (Advanced) English listeners (source: CURRENT_SPEC.md \"B1 "
    "[independently-generated Natural Spoken News English]\" section). Use natural spoken news "
    "English, adult tone, not as simplified as A2, but keep Clause Density/Concept Density/"
    "Long-distance Dependency low: one main idea per sentence, avoid stacking financial jargon where "
    "a plainer phrase works just as well."
)


def infer_article_level(instance_id: str) -> str | None:
    """instance_id命名規則("_a2"/"_standard"=Standard/A2、"_b1b"/"_advanced"=
    Advanced/B1B、既存NEGATIVE_SOURCE_FILES・hormuz/meta run instanceの
    命名規則[委任文脈で既に確定]に基づく判定。該当しない場合(B1/B2/B3/B4等
    のJA単体較正fixture)はNoneを返し、レベル別制約を付与しない(既存挙動を
    変えない安全側デフォルト)。"""
    s = instance_id.lower()
    if "b1b" in s or "advanced" in s:
        return "b1b"
    if "a2" in s or "standard" in s:
        return "a2"
    return None


def level_constraint_text(level: str | None) -> str:
    if level == "a2":
        return QUALITY_CONSTRAINT_COMMON + LEVEL_CONSTRAINT_A2
    if level == "b1b":
        return QUALITY_CONSTRAINT_COMMON + LEVEL_CONSTRAINT_B1B
    return QUALITY_CONSTRAINT_COMMON


REGENERATION_EMPHASIS_TEMPLATE = (
    "\n\n[Regeneration notice] Your previous attempt at this same fix had a quality problem: {reasons}. "
    "Resolve the Ledger deviation again, but this time specifically avoid that problem."
)


class TrialAbort(RuntimeError):
    pass


# ------------------------------------------------------------
# budget state(既存er052系と同一パターン)
# ------------------------------------------------------------
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
        raise TrialAbort(f"累計¥{state['cumulative_jpy']:.3f}が委任_09 Guardrail¥{TOTAL_BUDGET_JPY}に到達")


def save_json(path: str, payload: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def record_call(state: dict, consecutive_errors: list, label: str, cost_jpy: float, ok: bool,
                 recovery_stage: str, usage: dict | None = None) -> None:
    state["cumulative_calls"] += 1
    if ok:
        state["cumulative_jpy"] += cost_jpy
        state["history"].append({"label": label, "cost_jpy": cost_jpy, "recovery_stage": recovery_stage,
                                  "usage": usage})
        consecutive_errors[0] = 0
    else:
        state["cumulative_errors"] += 1
        consecutive_errors[0] += 1
    save_budget_state(state)
    if consecutive_errors[0] >= MAX_CONSECUTIVE_ERRORS:
        raise TrialAbort(f"API errorが{MAX_CONSECUTIVE_ERRORS}call連続(STOP条件)")


def simple_llm_call(client, state, consecutive_errors, call_log, label, developer_msg, prompt,
                     model: str = MODEL) -> str | None:
    """`s3rt.simple_llm_call`と同一の単純1-shot呼び出しロジックだが、本runner
    自身の`check_budget`/`record_call`/`save_budget_state`(本ファイル冒頭
    定義、budget_state_c233m.json)のみを使う独立実装(委任_09で実装)。
    **重要な修正**: 当初実装は`s3rt.simple_llm_call`をそのまま呼んでいたが、
    `s3rt.simple_llm_call`内部の`record_call`は`s3rt`モジュール自身の
    `save_budget_state`(`s3rt.BUDGET_STATE_PATH`=既存委任_08の
    `er052_output/open233_self_recovery_stage3_rewrite_trial_01/
    budget_state_c233l_b.json`)へ書き込むため、本runner実行のたびに
    **既存committment_08の証跡ファイルを上書き汚染する**実害があった
    (本委任の実行中に実際に発生・検出し、`git checkout`で復元済み。
    詳細はdelegation_log/RESULT_PACKET参照)。加えて`s3rt.check_budget`は
    `s3rt.TOTAL_BUDGET_JPY`(¥30、本runnerのGuardrail¥45とは別値)を
    参照するため、Guardrail判定も本runner側の意図と一致しない別軸だった
    (今回は¥30に達する前に完走したため実害は生じなかったが、潜在的な
    二重基準リスクだった)。本関数はこの2点を解消する。"""
    check_budget(state)
    last_err = None
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            t0 = time.time()
            response = client.responses.create(
                model=model, reasoning={"effort": vfl01.REASONING_EFFORT},
                input=[{"role": "developer", "content": developer_msg}, {"role": "user", "content": prompt}],
            )
            elapsed = round(time.time() - t0, 3)
            usage = s2p._extract_usage(response)
            cost = round(s2p.official_cost_jpy(usage), 4)
            call_log.append({"label": label, "recovery_stage": "stage3_rewrite", "cost_jpy": cost,
                              "usage": usage, "elapsed_seconds": elapsed,
                              "prompt_sha256": s2p.sha256_text(prompt)})
            record_call(state, consecutive_errors, label, cost, True, "stage3_rewrite", usage)
            return response.output_text.strip()
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    call_log.append({"label": label, "recovery_stage": "stage3_rewrite", "error": last_err})
    record_call(state, consecutive_errors, label, 0.0, False, "stage3_rewrite")
    return None


# ------------------------------------------------------------
# claim identity(同一claim/fact_id再発検出、§3-3/§5-3/§6-1 A5/A7)
# 委任_10で正規化を強化(claim identity trackingの脆弱性補強、Opus L2 #1
# 論点5): fact_idが無い場合のfallback hashは、表記揺れ(引用符の有無・
# 大小文字・空白の数)だけで別claim扱いされてしまう既知の脆弱性があった
# ため、hash化前に正規化する。fact_idがある場合はfact_idが最優先(不変)。
# ------------------------------------------------------------
def normalize_claim_text(s: str) -> str:
    s = s2p._strip_wrapping_quotes(s or "")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def claim_identity(dev: dict) -> str:
    fact_id = (dev.get("related_fact_id") or "").strip()
    if fact_id:
        return f"fact:{fact_id}"
    claim = normalize_claim_text(dev.get("claim_in_article") or "")
    return "claim:" + hashlib.sha256(claim.encode("utf-8")).hexdigest()[:16]


def find_matching_prior_record(dev: dict, prior_records: list, threshold: float = CLAIM_TEXT_SIMILARITY_THRESHOLD):
    """委任_11 作業B-3(§3-3停止判定の是正、Opus L2 #2論点1推奨3): 従来の
    claim_identity()単独(fact_id一致のみ)による停止判定は、設計§3-3の原意
    (「Rewriteが当該claimに効かなかったことが実証された場合」)より厳しく、
    同一fact_idに紐づく*別の文*(兄弟文カスケード、例: bgroup_B4のhook文/
    タイトル)まで「同一claim再発」として即Stage4にしていた
    (safety_A2A3/safety_A4/meta_run03_standard/meta_run03_advanced/
    bgroup_B4/neg1_meta_b3prod_a2で実測)。本関数はfact_idが一致する場合、
    正規化claim本文の近似一致(SequenceMatcher比率>=threshold)も要求する。
    fact_idが無いclaim(hashベースidentity)は従来通り厳密一致のみ
    (Opus L2 #1論点5で確定した保守的挙動を維持、変更しない)。
    一致するprior recordがあれば返し(=「同一claimが再発した」)、無ければ
    Noneを返す(=「別claいとして扱い、cycle 3の1回限り緩和対象になり得る」)。"""
    fact_id = (dev.get("related_fact_id") or "").strip()
    claim_text_norm = normalize_claim_text(dev.get("claim_in_article") or "")
    ident = claim_identity(dev)
    # 委任_24 A-2(§6-13): 同一fact_idのprior recordは複数cycleにまたがって
    # 複数件蓄積され得る(各cycleごとに1件追記)。呼び出し側が本関数の返り値
    # (escalated_to_paragraph等)で「直近の試行状態」を判定するため、
    # 最も新しい(最後に追記された)一致レコードを優先して返すよう、
    # 逆順(直近cycle優先)で走査する(既存呼び出し元はいずれもprior_records
    # がidentity単位で高々1件しか無い場面で単体テストされており、この
    # 順序変更で既存の一致/不一致判定結果自体は変わらない)。
    for rec in reversed(prior_records):
        if fact_id:
            if rec["fact_id"] != fact_id:
                continue
            prior_text = rec["claim_text_norm"]
            if claim_text_norm and prior_text and (
                claim_text_norm == prior_text
                or difflib.SequenceMatcher(None, claim_text_norm, prior_text).ratio() >= threshold
            ):
                return rec
        else:
            if rec["identity"] == ident:
                return rec
    return None


# ------------------------------------------------------------
# Stage 1: 既存出力の再利用 or 新規V4A実行(routing述語=overall_status、§3-1)
# ------------------------------------------------------------
def run_ja_en_equivalence_check(client, state, consecutive_errors, call_log, label,
                                 ja_text: str, en_text: str) -> dict:
    """委任_11 作業B-6(§4 Rewrite由来新規逸脱検出、Opus L2 #2論点4推奨2):
    paired local rewrite(J-1)実行後のJA↔EN等価チェック(1 call)。既存
    Production資産(`er003_ja_to_en_translation.py`の翻訳忠実性QA:
    プロンプトテンプレート`build_fidelity_qa_prompt`+JSON Schema
    `FIDELITY_QA_JSON_SCHEMA`+パーサ`parse_and_validate_fidelity_qa_output`)
    をread-onlyで借用する(`make_fidelity_qa_fn`は使わない。同関数は独自に
    `OpenAI()`クライアントを生成しdotenvを読み直すため、本runner自身の
    client/budget/telemetryパターン[§既存simple_llm_call/record_callと
    同一原則]と二重管理になるのを避けるため)。verdict(PASS/
    REVIEW_REQUIRED/FAIL)を記録するのみで、flow制御(fail-closed判定)
    には使わない(既存Recheck機構と重複する権限を持たせない、測定・
    報告専用)。"""
    check_budget(state)
    prompt = jtr.build_fidelity_qa_prompt(ja_text, en_text)
    last_err = None
    response = None
    t0 = time.time()
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            response = client.responses.create(
                model=MODEL, reasoning={"effort": vfl01.REASONING_EFFORT},
                text={"format": {"type": "json_schema", **jtr.FIDELITY_QA_JSON_SCHEMA}},
                input=prompt,
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    elapsed = round(time.time() - t0, 3)
    if response is None:
        call_log.append({"label": label, "recovery_stage": "ja_en_equivalence", "error": last_err})
        record_call(state, consecutive_errors, label, 0.0, False, "ja_en_equivalence")
        return {"verdict": None, "api_failure": True}
    try:
        parsed = jtr.parse_and_validate_fidelity_qa_output(response.output_text)
    except Exception:  # noqa: BLE001
        parsed = {"verdict": None}
    usage = s2p._extract_usage(response)
    cost = round(s2p.official_cost_jpy(usage), 4)
    call_log.append({"label": label, "recovery_stage": "ja_en_equivalence", "cost_jpy": cost, "usage": usage,
                      "elapsed_seconds": elapsed, "prompt_sha256": s2p.sha256_text(prompt),
                      "verdict": parsed.get("verdict"),
                      # 委任_27 Part1-4(¥0): 判定理由文もcall_logへ保存する。
                      "notes": parsed.get("notes")})
    record_call(state, consecutive_errors, label, cost, True, "ja_en_equivalence", usage)
    return {"verdict": parsed.get("verdict"), "api_failure": False, "raw": parsed}


def detect_rewrite_new_precheck_findings(ledger_text: str, baseline_findings: list, updated_text: str) -> list:
    """委任_11 作業B-6(§4 Rewrite由来新規逸脱検出、Opus L2 #2論点4推奨3、
    決定論・¥0): 編集後テキストへprecheckを再実行し、Rewrite前(baseline)に
    無かった新規finding(Ledger未出の数値・固有名詞の増加等)を検出する。
    誤検知を避けるため(field,kind)組の集合差分のみを見る(文言そのものの
    差異は問わない)。"""
    post_findings = precheck.run_precheck(ledger_text, updated_text)
    baseline_keys = {(f["field"], f["kind"]) for f in baseline_findings}
    return [f for f in post_findings if (f["field"], f["kind"]) not in baseline_keys]


def stage1_reuse(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d["parsed"] if "parsed" in d else d


# ------------------------------------------------------------
# 委任_20 W2(Opus L2レビュー#4 Q1(c)推奨): Stage1初回/Recheckのdeviation
# schemaへ「同一factを主張する記事内の他箇所を列挙する」フィールドを追加
# する(追加API callなし、¥0限界コスト)。er051(trial、他Trialとも共有
# されるモジュール)自体は変更せず、run_recheck()が既に行っている
# 「schemaだけ本runner内でローカルに拡張する」既存パターンをStage1初回
# 側にも適用する(stage1_fresh()自体は変更せず、別関数として追加する。
# 既存iteration1〜6/rep7〜10の再現性に影響しない)。
# ------------------------------------------------------------
SAME_FACT_ID_ENUMERATION_INSTRUCTION = """

For EACH deviation you report, also add a field "same_fact_id_locations": a JSON array of \
strings. In this array, quote verbatim every OTHER place in the article (if any) that asserts \
or restates the SAME underlying fact as this deviation, including the title, the hook/lead \
sentence, and the "In one line" summary if present, in addition to any other body sentences. \
Each quoted string must be an exact verbatim substring of the article text. If there are no \
other locations, return an empty array."""


def build_deviation_schema_with_enumeration(item_schema: dict) -> dict:
    """既存のdeviation item schema(trial.build_trial_deviation_item_schemaの
    出力)へ`same_fact_id_locations`(文字列配列)を追加する(委任_20 W2)。"""
    props = dict(item_schema["properties"])
    props["same_fact_id_locations"] = {"type": "array", "items": {"type": "string"}}
    required = list(item_schema["required"]) + ["same_fact_id_locations"]
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}


def expand_same_fact_id_locations(deviations: list, article_text: str) -> list:
    """委任_20 W2: 各deviationの`same_fact_id_locations`を、独立した追加
    deviationへ展開する(¥0・決定論)。展開後は既存の複数claim処理
    (`_run_stage3_cycle`が各claimを独立にladder①から試す既存機構、
    委任_18)がそのまま使われる(新しいRewrite機構は作らない)。

    - `same_fact_id_locations`が無い/空/フィールド自体が存在しない場合
      (reuse fixture[stage1_mode=reuse]のjsonに本フィールドが無い場合を
      含む)は何も追加しない(安全側fallback、既存動作を変えない)。
    - 各locationはarticle_text中の逐語substringとして実在する場合のみ
      採用する(fail-closedで幻覚を弾く)。元のclaim_in_articleと同一、
      またはfixed既に採用済みの場合は重複追加しない。
    """
    out = list(deviations)
    seen_texts = {(d.get("claim_in_article") or "").strip() for d in deviations}
    for d in deviations:
        locations = d.get("same_fact_id_locations")
        if not isinstance(locations, list):
            continue
        for loc in locations:
            loc_s = (loc or "").strip() if isinstance(loc, str) else ""
            if not loc_s or loc_s in seen_texts:
                continue
            if loc_s not in article_text:
                continue  # fail-closed: 逐語で実在しない候補は採用しない
            new_dev = dict(d)
            new_dev["claim_in_article"] = loc_s
            new_dev["detected_by_enumeration"] = True
            new_dev["enumeration_source_claim"] = (d.get("claim_in_article") or "").strip()
            out.append(new_dev)
            seen_texts.add(loc_s)
    return out


# ------------------------------------------------------------
# 委任_23 A-2(b)(iter7実測`hormuz_run03_standard`の真因是正): §6-8で
# 「reuse fixtureへの安全側fallback」として明記されていたとおり、
# stage1_mode=reuseのinstance(29 instance中26/29)は`same_fact_id_
# locations`フィールドを持たない旧jsonをそのまま読み込むため、LLMベースの
# 列挙(委任_20 W2、fresh instance限定)が一切効かない。`hormuz_run03_
# standard`はcycle0のStage1初回がbodyのclaim(HF-009)しか検出できず、
# in_one_line側の同一fact言及は**cycle1のRecheck(fresh call、既に
# 列挙済み)**まで発見されないため、cycle0とcycle1で2回に分けてRewrite
# する形になり、HARD_MAX_CYCLES(3)を消費し尽くした後もja_pending_
# deviationが解消しないままSTAGE4_ESCALATIONへ至っていた(REPORT§23 A)。
# 本フォールバックは、reuse fixtureのdeviationについてclaim_in_articleの
# 数値・金額・%トークン、および文分割(split_sentences_generic、見出し行
# [#始まり]は除外=既知の限界)した記事内の他文とのキーワード重複を¥0・
# 決定論で計算し、cycle0の時点でbody+in_one_line等の複数箇所をまとめて
# claimへ追加する(既存`expand_same_fact_id_locations`と同じfail-closed
# 方針[逐語substring実在確認]を経由させ、新しいRewrite機構は作らない)。
# ------------------------------------------------------------
_NUMERIC_TOKEN_RE = re.compile(r"\$?\d[\d,]*\.?\d*%?")
_KEYWORD_WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']{2,}")
_KEYWORD_STOPWORDS_EN = frozenset("""
a an the and or but if then so to of in on at for with by from as is was were are
be been being it its this that these those he she they his her their after before
than not no did do does had has have about into over across up down out would could
should will shall may might one also
""".split())
# 委任_23 A-2(b): キーワード一致の最低必要数(この値以上の非stopword
# 共有語があれば候補とする)。実データ(hormuz_run03_standard cycle0
# en_text_before_rewrite、claim="Oil prices did not fall across the whole
# market after the plan was withdrawn.")で較正した: 閾値3は、実際に
# cycle1のRecheck(fresh LLM enumeration)が検出したin_one_line文
# ("The fee plan vanished, but oil prices stayed high...")を正しく
# 候補化しつつ、無関係な本文文(例: "Trump said he would drop the 20
# percent fee plan."、共有語1語のみ)を誤って候補化しない(REPORT§23 A)。
# 閾値2は同記事で5件中4件が無関係な過剰候補化(共有語2語のみの文が多数
# 一致)、閾値4は真陽性のin_one_line文まで取りこぼす(0件)ため、いずれも
# 採用しなかった。この較正は1 fixtureの実データによるものであり、他
# fixtureへの一般化は未検証(§9-1既知の限界と同じ性質、既知の限界として
# 記録する)。
_KEYWORD_OVERLAP_MIN_SHARED = 3


def extract_distinctive_numeric_tokens(text: str) -> frozenset:
    """決定論・¥0。テキスト中の数値・金額・%表記トークンをそのまま抽出する
    (changed_number/changed_time等、数値差分が本質の逸脱型の手掛かり)。"""
    return frozenset(_NUMERIC_TOKEN_RE.findall(text or ""))


def extract_distinctive_keywords_en(text: str) -> frozenset:
    """決定論・¥0。EN文中の非stopword・3文字以上の単語を小文字化して抽出
    する(changed_actor等、数値を伴わない逸脱型の手掛かり)。"""
    words = {w.lower() for w in _KEYWORD_WORD_RE.findall(text or "")}
    return frozenset(w for w in words if w not in _KEYWORD_STOPWORDS_EN)


def deterministic_same_fact_id_location_fallback(deviations: list, article_text: str) -> list:
    """委任_23 A-2(b): `same_fact_id_locations`フィールドを持たないreuse
    fixture向けの¥0決定論フォールバック。既にフィールドを持つdeviation
    (fresh instanceのLLMベース列挙)は上書きしない。数値/金額/%トークンが
    1つでも一致、またはstopword除外後の非stopword単語が
    `_KEYWORD_OVERLAP_MIN_SHARED`件以上一致する記事内の他文
    (`split_sentences_generic`、見出し行除外は既知の限界)を候補として
    `same_fact_id_locations`へ設定する(実際の追加・重複排除・逐語実在
    確認は呼び出し側が既存`expand_same_fact_id_locations`へ渡して行う、
    二重処理を避ける)。

    既知の限界(正直に記録): (a) 見出し行(#始まり、記事タイトル)は
    `split_sentences_generic`が除外するため候補化されない(実データでは
    title側は該当claimがACCEPTABLE判定だったため実害は確認されていない)。
    (b) LLMによる意味理解を伴わないため、数値もキーワード重複も乏しい
    paraphraseは検出できない。(c) 閾値の選び方はこの1 fixtureの実データ
    (§6-6既知の限界、REPORT§23 A)による較正であり、他fixtureへの一般化は
    未検証。過剰候補化の場合もStage2(独立LLM materiality判定)がACCEPTABLE
    として screen するため安全側(Stage2 API call増による¥コスト増のみ、
    Safety regressionではない)。"""
    out = []
    for d in deviations:
        if isinstance(d.get("same_fact_id_locations"), list):
            out.append(d)
            continue
        claim_text = (d.get("claim_in_article") or "").strip()
        d2 = dict(d)
        if not claim_text:
            d2["same_fact_id_locations"] = []
            out.append(d2)
            continue
        numeric_tokens = extract_distinctive_numeric_tokens(claim_text)
        keywords = extract_distinctive_keywords_en(claim_text)
        locations = []
        for s in split_sentences_generic(article_text):
            s_stripped = s.strip()
            if not s_stripped or s_stripped == claim_text:
                continue
            s_numeric = extract_distinctive_numeric_tokens(s_stripped)
            s_keywords = extract_distinctive_keywords_en(s_stripped)
            numeric_match = bool(numeric_tokens & s_numeric)
            keyword_match = len(keywords & s_keywords) >= _KEYWORD_OVERLAP_MIN_SHARED
            if numeric_match or keyword_match:
                locations.append(s_stripped)
        d2["same_fact_id_locations"] = locations
        d2["same_fact_id_locations_source"] = "deterministic_fallback_c233_23"
        out.append(d2)
    return out


def stage1_fresh_with_enumeration(client, state, consecutive_errors, call_log, label, fixture,
                                   developer_message: str = vfl01.DEVIATION_DEVELOPER_MESSAGE) -> dict:
    """委任_20 W2: `stage1_fresh()`と同一のretry/cost計上パターンだが、
    schemaへ`same_fact_id_locations`を追加したローカル拡張版(`run_recheck()`
    と同じ「schemaだけローカルに拡張する」既存パターンを踏襲、er051は
    read-onlyのまま)。呼び出し元(`run_instance`)がこのinstanceについて
    Stage1を新規実行する場合のみ使う(reuse fixtureには影響しない)。

    委任_30 Part2(design書§0/§9-1「既定構成の確定」): `developer_message`
    引数を追加した(既定値は既存の`vfl01.DEVIATION_DEVELOPER_MESSAGE`で
    既存呼び出し元の挙動は無変更)。`run_instance`からは重大誤解原則配線版
    (`trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE`)が既定で渡る
    (`ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT`、既定True)。schemaのenum
    拡張(same_fact_id_locations)自体は変更しない(委任_28/29の要素Trial
    [`stage1_fresh_with_misconception_principle`]はenum非対応だったため
    別関数だったが、本関数は両方を同時に持つ既定経路として統合する)。"""
    check_budget(state)
    include_origin = fixture.get("source_article_text") is not None
    prompt_template = trial.build_trial_prompt_template("V4A")
    prompt = prompt_template.format(verified_ledger_text=fixture["ledger_text"],
                                     article_text=fixture["article_text"])
    prompt += vfl01.RELATED_FACT_ID_INSTRUCTION
    if include_origin:
        prompt += vfl01.ORIGIN_INSTRUCTION_TEMPLATE.format(source_article_text=fixture["source_article_text"])
    prompt += SAME_FACT_ID_ENUMERATION_INSTRUCTION
    item_schema = build_deviation_schema_with_enumeration(
        trial.build_trial_deviation_item_schema(True, include_origin))
    schema = {
        "name": "open233_self_recovery_stage1_v4a_enum",
        "schema": {"type": "object", "properties": {"deviations": {"type": "array", "items": item_schema}},
                   "required": ["deviations"], "additionalProperties": False},
        "strict": True,
    }
    last_err = None
    response = None
    t0 = time.time()
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            response = client.responses.create(
                model=MODEL, reasoning={"effort": vfl01.REASONING_EFFORT},
                text={"format": {"type": "json_schema", **schema}},
                input=[{"role": "developer", "content": developer_message},
                       {"role": "user", "content": prompt}],
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    elapsed = round(time.time() - t0, 3)
    if response is None:
        call_log.append({"label": label, "recovery_stage": "stage1_initial", "error": last_err})
        record_call(state, consecutive_errors, label, 0.0, False, "stage1_initial")
        return {"overall_status": "LEDGER_DEVIATION", "deviations": [], "_stage1_api_failure": True}
    raw_parsed = json.loads(response.output_text)
    parsed = vfl01._apply_deviation_post_hoc_validation(raw_parsed)
    parsed_trial = trial.classify_parsed_result_trial(parsed, "V4A")
    parsed_trial["deviations"] = expand_same_fact_id_locations(parsed_trial["deviations"], fixture["article_text"])
    usage = s2p._extract_usage(response)
    cost = round(s2p.official_cost_jpy(usage), 4)
    call_log.append({"label": label, "recovery_stage": "stage1_initial", "cost_jpy": cost, "usage": usage,
                      "elapsed_seconds": elapsed, "prompt_sha256": s2p.sha256_text(prompt)})
    record_call(state, consecutive_errors, label, cost, True, "stage1_initial", usage)
    return parsed_trial


def stage1_fresh(client, state, consecutive_errors, call_log, label, fixture) -> dict:
    check_budget(state)
    last_err = None
    result = None
    t0 = time.time()
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = trial.run_trial_deviation_check(
                client, fixture["ledger_text"], fixture["article_text"], MODEL, "V4A",
                include_related_fact_id=True, source_article_text=fixture.get("source_article_text"),
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    elapsed = round(time.time() - t0, 3)
    if result is not None:
        cost = round(s2p.official_cost_jpy(result["usage"]), 4)
        call_log.append({"label": label, "recovery_stage": "stage1_initial", "cost_jpy": cost,
                          "usage": result["usage"], "elapsed_seconds": elapsed,
                          "prompt_sha256": s2p.sha256_text(result["prompt"])})
        record_call(state, consecutive_errors, label, cost, True, "stage1_initial", result["usage"])
        return result["parsed"]
    call_log.append({"label": label, "recovery_stage": "stage1_initial", "error": last_err})
    record_call(state, consecutive_errors, label, 0.0, False, "stage1_initial")
    # fail-closedとしてBLOCKING-candidate扱い(§6-1 A7)。deviationsは空だが
    # overall_statusをLEDGER_DEVIATIONにしてルーティングだけ強制する。
    return {"overall_status": "LEDGER_DEVIATION", "deviations": [], "_stage1_api_failure": True}


def stage1_fresh_with_misconception_principle(client, state, consecutive_errors, call_log, label,
                                               fixture) -> dict:
    """委任_28 Part0-1(design書§0/§4-18): `stage1_fresh()`と同一の呼び出し
    (developer messageへ重大誤解原則[`trial.V4A_DEVELOPER_MSG_WITH_
    MISCONCEPTION_PRINCIPLE`]を使う点のみが異なる、既存`stage1_fresh()`
    自体は一切変更しない)だが、**cost計上は`record_call`/`check_budget`
    (本runner自身の固定`BUDGET_STATE_PATH`/`TOTAL_BUDGET_JPY`を参照する
    module-level関数)を経由せず、渡された`state`/`consecutive_errors`
    のみを直接更新し、ファイル書き込みは一切行わない**(委任_28実測中に
    本関数経由でrep15の既存budget state証跡を誤って上書きする事故が
    実際に発生し[`git checkout`で復元・実害なし確認済み]、原因は
    `record_call`内部の`save_budget_state(state)`が引数`state`の中身に
    関わらず本runner自身の固定pathへ書き込む副作用だったため、本関数
    自体の設計をこの副作用を持たないよう是正した。`simple_llm_call`の
    docstringが記録する委任_09のs3rt事故と同根の問題)。呼び出し元
    (Meta要素Trial[委任_28]専用)が、戻り値を使って自分自身のbudget
    state/fileへの計上・保存を行う。本関数はmain()のデフォルト経路へは
    配線しない。"""
    last_err = None
    result = None
    t0 = time.time()
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = trial.run_trial_deviation_check(
                client, fixture["ledger_text"], fixture["article_text"], MODEL, "V4A",
                include_related_fact_id=True, source_article_text=fixture.get("source_article_text"),
                developer_message_override=trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE,
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    elapsed = round(time.time() - t0, 3)
    if result is not None:
        cost = round(s2p.official_cost_jpy(result["usage"]), 4)
        call_log.append({"label": label, "recovery_stage": "stage1_initial", "cost_jpy": cost,
                          "usage": result["usage"], "elapsed_seconds": elapsed,
                          "prompt_sha256": s2p.sha256_text(result["prompt"])})
        state["cumulative_calls"] = state.get("cumulative_calls", 0) + 1
        state["cumulative_jpy"] = state.get("cumulative_jpy", 0.0) + cost
        state.setdefault("history", []).append({"label": label, "cost_jpy": cost, "usage": result["usage"]})
        consecutive_errors[0] = 0
        return result["parsed"]
    call_log.append({"label": label, "recovery_stage": "stage1_initial", "error": last_err})
    state["cumulative_calls"] = state.get("cumulative_calls", 0) + 1
    state["cumulative_errors"] = state.get("cumulative_errors", 0) + 1
    consecutive_errors[0] += 1
    return {"overall_status": "LEDGER_DEVIATION", "deviations": [], "_stage1_api_failure": True}


# ------------------------------------------------------------
# S1-U variant(委任_10、§3-1): Stage1(V4A)がACCEPTABLEだった場合に限り、
# S1-D(materiality一体型、1 call)を追加実行し、BLOCKING判定claimのみを
# union(fail-closed)でStage2以降へ送る(Stage1 recall miss対策)。V4Aの
# 出力自体は変更せず、追加のBLOCKING claimが見つかった場合のみメイン
# フローへ合流させる(既存のACCEPTABLE_STAGE1経路そのものは変更しない)。
# ------------------------------------------------------------
def stage1_union_screen(client, state, consecutive_errors, call_log, label, fixture) -> dict:
    check_budget(state)
    last_err = None
    result = None
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            result = s1d.run_s1d_check(client, fixture["ledger_text"], fixture["article_text"],
                                        source_article_text=fixture.get("source_article_text"), model=MODEL)
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    if result is None:
        call_log.append({"label": label, "recovery_stage": "stage1_union_screen", "error": last_err})
        record_call(state, consecutive_errors, label, 0.0, False, "stage1_union_screen")
        return {"blocking_deviations": [], "api_failure": True}
    call_log.append({"label": label, "recovery_stage": "stage1_union_screen", "cost_jpy": result["cost_jpy"],
                      "usage": result["usage"], "elapsed_seconds": result["elapsed_seconds"],
                      "prompt_sha256": result["prompt_sha256"]})
    record_call(state, consecutive_errors, label, result["cost_jpy"], True, "stage1_union_screen", result["usage"])
    blocking = [d for d in result["parsed"]["deviations"] if d.get("materiality") == "BLOCKING"]
    # S1D出力のキー(claim_in_article/related_fact_id_guess/changed_*)をV4A
    # deviations互換のキー名へ変換する(severity=MAJOR固定、related_fact_id
    # はrelated_fact_id_guessをそのまま採用、originはS1Dが出力しないためNone)。
    converted = []
    for d in blocking:
        converted.append({
            "claim_in_article": d.get("claim_in_article", ""), "origin": None,
            "related_fact_id": d.get("related_fact_id_guess", ""), "severity": "MAJOR",
            **{k: d.get(k, False) for k in FLOOR_FLAGS},
        })
    return {"blocking_deviations": converted, "api_failure": False}


# ------------------------------------------------------------
# Stage 1 Recheck(prior_issuesあり、A1)。trial variant(V4A)+
# vfl01.build_prior_issues_instruction()を組み合わせた本runner専用関数
# (er051側は変更しない、read-onlyで部品を借用するだけ)。
# ------------------------------------------------------------
def build_recheck_schema(include_related_fact_id: bool, include_origin: bool) -> dict:
    # 委任_20 W2: Recheckにも同一fact_id列挙フィールドを追加する(¥0、
    # 追加callなし)。
    item_schema = build_deviation_schema_with_enumeration(
        trial.build_trial_deviation_item_schema(include_related_fact_id, include_origin))
    props = {"deviations": {"type": "array", "items": item_schema},
              "prior_issues_resolved": {"type": "array", "items": vfl01.PRIOR_ISSUE_RESOLVED_ITEM_SCHEMA}}
    required = ["deviations", "prior_issues_resolved"]
    return {
        "name": "open233_self_recovery_recheck_v4a_prior",
        "schema": {"type": "object", "properties": props, "required": required, "additionalProperties": False},
        "strict": True,
    }


def run_recheck(client, state, consecutive_errors, call_log, label, fixture, article_text: str,
                 prior_issues: list, enable_fact_id_enumeration: bool = False) -> dict:
    """委任_35(design書§6-16、追加原因(d)の是正): `same_fact_id_locations`
    列挙(委任_20 W2)は、初回Stage1検出(cycle1の入力を作る1回)でのみ行い、
    以後のRecheck呼び出し(cycle番号に関わらず、本関数の呼び出しは全て
    初回Stage1より後)では新規候補を再列挙しない(既定`enable_fact_id_
    enumeration=False`)。Rewrite後のテキストから毎回新しい候補文を
    探し続けることがcycleごとの検出対象増加(rep19実測、cycle1:2件原本->
    cycle2:12件->cycle3:5件)の一因だった(REPORT§32-3)。未解消のまま
    残るclaim自体は、prior_issuesに基づく通常のRecheck判定
    (overall_status/deviations)でこれまでどおり継続して検出される
    (`prior_issues_resolved`で確認、新規列挙ではなく既存claimの再判定)。
    `enable_fact_id_enumeration=True`を明示すれば旧来どおりの列挙を行う
    (後方互換、既存呼び出し側[本runner外からの直接利用]のデフォルト変更
    による無断広域変更を避ける)。"""
    check_budget(state)
    prompt_template = trial.build_trial_prompt_template("V4A")
    prompt = prompt_template.format(verified_ledger_text=fixture["ledger_text"], article_text=article_text)
    prompt += vfl01.RELATED_FACT_ID_INSTRUCTION
    include_origin = fixture.get("source_article_text") is not None
    if include_origin:
        prompt += vfl01.ORIGIN_INSTRUCTION_TEMPLATE.format(source_article_text=fixture["source_article_text"])
    prompt += vfl01.build_prior_issues_instruction(prior_issues)
    if enable_fact_id_enumeration:
        prompt += SAME_FACT_ID_ENUMERATION_INSTRUCTION
    schema = build_recheck_schema(True, include_origin)

    last_err = None
    response = None
    t0 = time.time()
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            response = client.responses.create(
                model=MODEL, reasoning={"effort": vfl01.REASONING_EFFORT},
                text={"format": {"type": "json_schema", **schema}},
                input=[{"role": "developer", "content": vfl01.DEVIATION_DEVELOPER_MESSAGE},
                       {"role": "user", "content": prompt}],
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    elapsed = round(time.time() - t0, 3)
    if response is None:
        call_log.append({"label": label, "recovery_stage": "stage1_recheck", "error": last_err})
        record_call(state, consecutive_errors, label, 0.0, False, "stage1_recheck")
        # fail-closed: API失敗はBLOCKING-candidate扱い(§6-1 A7)
        return {"overall_status": "LEDGER_DEVIATION", "deviations": [], "all_prior_issues_resolved": False,
                "_recheck_api_failure": True}

    raw_parsed = json.loads(response.output_text)
    parsed = vfl01._apply_deviation_post_hoc_validation(raw_parsed)
    parsed_trial = trial.classify_parsed_result_trial(parsed, "V4A")
    # 委任_20 W2(委任_35で既定False化、§6-16): Recheckが検出した同一
    # fact_id別箇所の展開は、enable_fact_id_enumeration=True明示時のみ行う。
    if enable_fact_id_enumeration:
        parsed_trial["deviations"] = expand_same_fact_id_locations(parsed_trial["deviations"], article_text)
    resolved = raw_parsed.get("prior_issues_resolved", [])
    parsed_trial["prior_issues_resolved"] = resolved
    parsed_trial["all_prior_issues_resolved"] = (
        len(resolved) == len(prior_issues) and all(bool(r.get("resolved")) for r in resolved)
    )
    usage = s2p._extract_usage(response)
    cost = round(s2p.official_cost_jpy(usage), 4)
    call_log.append({"label": label, "recovery_stage": "stage1_recheck", "cost_jpy": cost, "usage": usage,
                      "elapsed_seconds": elapsed, "prompt_sha256": s2p.sha256_text(prompt),
                      "overall_status": parsed_trial["overall_status"],
                      "all_prior_issues_resolved": parsed_trial["all_prior_issues_resolved"]})
    record_call(state, consecutive_errors, label, cost, True, "stage1_recheck", usage)
    return parsed_trial


# ------------------------------------------------------------
# cite-or-release(委任_13、iteration5、Opus L2レビュー#3論点4推奨1・2)。
# 確認call(旧`_recheck_confirm`)のschemaへ`remaining_sentence`(未解消と
# 判断する根拠として、現在の記事本文中に実在する文の逐語引用)を必須化する。
# vfl01(Production)は変更せず、Trial側でschema/instructionを組み立てる。
# 引用が本文に実在すればStage4(正しい、fail-closed維持)、実在しなければ
# resolved扱いへ機械的に上書きする(根拠のない未解消を排除、fail-closedを
# 緩めない方向の厳格化)。あわせてRewrite前後の対象文ペア(before→after)を
# instructionへ添える(モデルが消えた文を探し回る必要をなくす)。
# ------------------------------------------------------------
CONFIRM_PRIOR_ISSUE_RESOLVED_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "index": {"type": "integer"},
        "resolved": {"type": "boolean"},
        "explanation": {"type": "string"},
        "remaining_sentence": {
            "type": "string",
            "description": "resolved=falseの場合のみ: 未解消の根拠として、現在の記事本文中に"
                            "実在する文をそのまま逐語引用する(要約・言い換え不可)。resolved=true"
                            "の場合は空文字列にする。",
        },
    },
    "required": ["index", "resolved", "explanation", "remaining_sentence"],
    "additionalProperties": False,
}

CITE_OR_RELEASE_INSTRUCTION = (
    "\n\n【追加指示(委任_13、cite-or-release)】各項目についてresolved=falseと判定する場合、"
    "その根拠として、現在の記事本文(article_text)に実在する文をそのまま逐語引用して"
    "remaining_sentenceへ記載してください(要約や言い換えは不可、記事本文に無い文を"
    "書いてはいけません)。resolved=trueの場合、remaining_sentenceは空文字列(\"\")にしてください。"
)


def build_before_after_instruction(before_after_pairs: list) -> str:
    """委任_13(iteration5、Opus L2レビュー#3論点4推奨2): Rewrite前後の対象文
    ペアをinstructionへ添える(single_text_rewrite/paired_rewriteが返す
    before_fragment/after_fragmentのうち、両方が判明しているものだけを使う。
    全文フォールバック等でfragmentが特定できない場合は対象から除く)。"""
    pairs = [p for p in before_after_pairs if p.get("before") and p.get("after") is not None]
    if not pairs:
        return ""
    lines = ["\n\n【追加指示: 今回のRewriteで変更された対象文】",
             "以下の文は、前回指摘の解消を試みるために変更されました(未解消判定の参考にしてください):"]
    for pair in pairs:
        after_display = pair["after"] if pair["after"] else "(削除されました)"
        lines.append(f"- before: {pair['before']}\n  after: {after_display}")
    return "\n".join(lines)


def build_recheck_schema_confirm(include_related_fact_id: bool, include_origin: bool) -> dict:
    item_schema = trial.build_trial_deviation_item_schema(include_related_fact_id, include_origin)
    props = {"deviations": {"type": "array", "items": item_schema},
              "prior_issues_resolved": {"type": "array", "items": CONFIRM_PRIOR_ISSUE_RESOLVED_ITEM_SCHEMA}}
    required = ["deviations", "prior_issues_resolved"]
    return {
        "name": "open233_self_recovery_recheck_confirm_v4a_prior_cite",
        "schema": {"type": "object", "properties": props, "required": required, "additionalProperties": False},
        "strict": True,
    }


def apply_cite_or_release(parsed_confirm: dict, article_text: str) -> dict:
    """resolved=falseの各項目について、remaining_sentenceが現在の記事本文に
    実在するかを機械検証する。実在すれば(cite)そのままresolved=false
    (Stage4行き、正しい)。実在しなければ(根拠なき未解消)resolved=trueへ
    機械的に上書きする(release)。空白正規化のみ行い、部分一致(strip後の
    厳密substring)で判定する(fail-closedを緩めない、過剰な緩和防止)。"""
    resolved_list = parsed_confirm.get("prior_issues_resolved", [])
    normalized_article = re.sub(r"\s+", " ", article_text)
    out_list = []
    released_count = 0
    for item in resolved_list:
        orig_resolved = bool(item.get("resolved"))
        remaining = (item.get("remaining_sentence") or "").strip()
        final_resolved = orig_resolved
        overridden = False
        if not orig_resolved:
            normalized_remaining = re.sub(r"\s+", " ", remaining).strip()
            cited_exists = bool(normalized_remaining) and (normalized_remaining in normalized_article)
            if not cited_exists:
                final_resolved = True
                overridden = True
                released_count += 1
        out_list.append({**item, "resolved": final_resolved, "cite_or_release_overridden": overridden})
    all_resolved = len(out_list) > 0 and all(bool(it["resolved"]) for it in out_list)
    return {"prior_issues_resolved": out_list, "all_prior_issues_resolved": all_resolved,
            "released_count": released_count}


def run_recheck_confirm(client, state, consecutive_errors, call_log, label, fixture, article_text: str,
                         prior_issues: list, before_after_pairs: list) -> dict:
    """cite-or-release対応の確認call。run_recheck()とほぼ同一だが、schema・
    instructionをConfirm専用のものへ差し替え、応答後にapply_cite_or_release
    で機械検証する。"""
    check_budget(state)
    prompt_template = trial.build_trial_prompt_template("V4A")
    prompt = prompt_template.format(verified_ledger_text=fixture["ledger_text"], article_text=article_text)
    prompt += vfl01.RELATED_FACT_ID_INSTRUCTION
    include_origin = fixture.get("source_article_text") is not None
    if include_origin:
        prompt += vfl01.ORIGIN_INSTRUCTION_TEMPLATE.format(source_article_text=fixture["source_article_text"])
    prompt += vfl01.build_prior_issues_instruction(prior_issues)
    prompt += CITE_OR_RELEASE_INSTRUCTION
    prompt += build_before_after_instruction(before_after_pairs)
    schema = build_recheck_schema_confirm(True, include_origin)

    last_err = None
    response = None
    t0 = time.time()
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            response = client.responses.create(
                model=MODEL, reasoning={"effort": vfl01.REASONING_EFFORT},
                text={"format": {"type": "json_schema", **schema}},
                input=[{"role": "developer", "content": vfl01.DEVIATION_DEVELOPER_MESSAGE},
                       {"role": "user", "content": prompt}],
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    elapsed = round(time.time() - t0, 3)
    if response is None:
        call_log.append({"label": label, "recovery_stage": "stage1_recheck_confirm", "error": last_err})
        record_call(state, consecutive_errors, label, 0.0, False, "stage1_recheck_confirm")
        # fail-closed: API失敗はBLOCKING-candidate扱い(§6-1 A7)
        return {"overall_status": "LEDGER_DEVIATION", "deviations": [], "all_prior_issues_resolved": False,
                "_recheck_api_failure": True}

    raw_parsed = json.loads(response.output_text)
    parsed = vfl01._apply_deviation_post_hoc_validation(raw_parsed)
    parsed_trial = trial.classify_parsed_result_trial(parsed, "V4A")
    cite_result = apply_cite_or_release({"prior_issues_resolved": raw_parsed.get("prior_issues_resolved", [])},
                                         article_text)
    parsed_trial["prior_issues_resolved"] = cite_result["prior_issues_resolved"]
    parsed_trial["all_prior_issues_resolved"] = cite_result["all_prior_issues_resolved"]
    parsed_trial["cite_or_release_released_count"] = cite_result["released_count"]
    usage = s2p._extract_usage(response)
    cost = round(s2p.official_cost_jpy(usage), 4)
    call_log.append({"label": label, "recovery_stage": "stage1_recheck_confirm", "cost_jpy": cost, "usage": usage,
                      "elapsed_seconds": elapsed, "prompt_sha256": s2p.sha256_text(prompt),
                      "overall_status": parsed_trial["overall_status"],
                      "all_prior_issues_resolved": parsed_trial["all_prior_issues_resolved"],
                      "cite_or_release_released_count": cite_result["released_count"]})
    record_call(state, consecutive_errors, label, cost, True, "stage1_recheck_confirm", usage)
    return parsed_trial


# ------------------------------------------------------------
# Stage 2: R2 rubric、instance単位batch(§4-8/A9)、floor適用
# ------------------------------------------------------------
# 委任_14 作業B-1(2026-09-30ユーザー新方針item1): floorへ渡す前に、
# Stage1 LLMが"changed_number"=trueとしたclaimのうち、記事側の数値が
# related_fact_idのLedger numeric_valueの「通常の四捨五入」で得られる
# 近似値でしかない場合はchanged_numberをfloor対象から除外する(precheck.
# changed_number_is_natural_rounding_only、決定論・¥0)。他のfloor flag
# (changed_actor/negation/comparison/time)は無変更、changed_numberが唯一
# 発火していた場合のみfloor自体が不発火になる。fail-closed維持: 判定不能
# (fact_id不明・numeric_value非単一等)の場合は常にFalseを返す既存設計
# のため、従来どおりfloorが発火する。
def _sanitize_dev_for_rounding(dev: dict, claim_text: str, ledger_text: str) -> dict:
    if not dev.get("changed_number"):
        return dev
    if precheck.changed_number_is_natural_rounding_only(claim_text, dev.get("related_fact_id"), ledger_text):
        dev2 = dict(dev)
        dev2["changed_number"] = False
        dev2["changed_number_suppressed_reason"] = "natural_rounding(委任_14 B-1)"
        return dev2
    return dev


# 委任_35(design書§6-16、追加原因(d)の是正): deterministic floor
# (FLOOR_FLAGS)は、Stage1が違反を体現する当該claim文に直接付与したflagに
# のみ適用し、`expand_same_fact_id_locations`(委任_20 W2)が同一
# `related_fact_id`を共有する他claimへ複製したflag(`detected_by_
# enumeration=True`、dev自体はdict(d)でコピーされたもの)には適用しない。
# 複製claimは引き続きStage2(独立LLM判定、llm_materiality)で評価され、
# その文自体が実際に違反していればllm_materiality=BLOCKINGとなり
# final_materialityもBLOCKINGのまま維持される(fail-closedは失われない)。
# floorを素通しするのは「LLMが独立にACCEPTABLE/QUALITYと判定した複製claim
# まで強制的にBLOCKINGへ昇格させる」部分のみであり、これがrep19実測
# (REPORT§32-1 claim#5/#6等)で確認された誤分類の直接原因だった。
def apply_floor(materiality: str, dev: dict, detected_by: str) -> tuple:
    if detected_by == "precheck":
        return "BLOCKING", "precheck_floor"
    if dev.get("detected_by_enumeration"):
        return materiality, None
    triggered = [k for k in FLOOR_FLAGS if bool(dev.get(k))]
    if triggered:
        return "BLOCKING", "deterministic_floor:" + ",".join(triggered)
    return materiality, None


# ------------------------------------------------------------
# 委任_14 作業B-2(floor-cited variant): 現行floor(floor-strict)は
# FLOOR_FLAGSのいずれかがtrueであれば無条件にBLOCKINGへ強制する。
# floor-cited variantは、Stage1が対象claimに対しLedgerの具体的値
# (numeric_value/date_or_period/明示的なclaim文)を名指しできる場合
# (related_fact_idがLedgerに実在し、Stage1のissue/explanationが当該
# fact_idの具体的field[numeric_value/date_or_period/claim]のいずれかに
# 言及している場合)に限りfloorを発火させる。反実仮想として両方を計算し
# (追加API callなし、¥0)、instance結果へ両方の判定を記録する(実際の
# フロー制御は既存floor-strictのまま変更しない、fail-closed維持)。
# ------------------------------------------------------------
def floor_cited_eligible(dev: dict, ledger_text: str) -> bool:
    fact_id = (dev.get("related_fact_id") or "").strip()
    if not fact_id:
        return False
    facts = precheck.parse_ledger_text(ledger_text)
    fact = next((f for f in facts if f.get("fact_id") == fact_id), None)
    if fact is None:
        return False
    probe_text = " ".join(str(dev.get(k) or "") for k in ("issue", "explanation"))
    if not probe_text.strip():
        return False
    citable_fields = [fact.get("numeric_value"), fact.get("date_or_period"), fact.get("claim")]
    for field_val in citable_fields:
        if not field_val:
            continue
        # 簡易引用判定: fieldの内容の一部(4文字以上の連続部分文字列、数字を
        # 含む短いtoken)がissue/explanation中に言及されているかを、数値
        # token・4文字以上の語のoverlapで判定する(決定論・¥0、専用の新しい
        # 安全装置ではなく既存precheckの数値抽出を再利用)。
        field_numbers = precheck.extract_percentages(str(field_val)) | {
            v for v in precheck.extract_counts(str(field_val))}
        probe_numbers = precheck.extract_percentages(probe_text) | {
            v for v in precheck.extract_counts(probe_text)}
        if field_numbers and probe_numbers and (field_numbers & probe_numbers):
            return True
        field_words = {w.lower() for w in re.findall(r"[A-Za-z]{4,}", str(field_val))}
        probe_words = {w.lower() for w in re.findall(r"[A-Za-z]{4,}", probe_text)}
        if field_words and len(field_words & probe_words) >= 2:
            return True
    return False


def apply_floor_cited(materiality: str, dev: dict, detected_by: str, ledger_text: str) -> tuple:
    """floor-cited variant(委任_14 B-2)。precheck floorはfloor-strictと
    同じ(precheckは既にLedger実値との機械照合による具体的な引用そのもの
    のため、cite-or-releaseの精神上、常にcited扱い)。deterministic floor
    (Stage1 LLM flag由来)は、floor_cited_eligible()がTrueの場合のみ発火
    させる。"""
    if detected_by == "precheck":
        return "BLOCKING", "precheck_floor"
    # 委任_35: apply_floorと同じ理由(§6-16参照)で、same_fact_id_locations
    # 複製claim(detected_by_enumeration=True)はfloor-cited反実仮想からも
    # 除外する(本関数は実フロー制御には使われないが、記録の一貫性のため)。
    if dev.get("detected_by_enumeration"):
        return materiality, None
    triggered = [k for k in FLOOR_FLAGS if bool(dev.get(k))]
    if triggered and floor_cited_eligible(dev, ledger_text):
        return "BLOCKING", "deterministic_floor_cited:" + ",".join(triggered)
    return materiality, None


# ------------------------------------------------------------
# 委任_14 作業B-5(Hook-aware統合、監査結果[docs/pm/audit_hook_aware_and_
# rewrite_qa_open233_01.md]に基づく)。Production HOOK_CLAUSE
# (er003_v1_en_direct_vfl_01_generate.py L579-595)は「Hook文では
# changed_scope/changed_comparisonの2種のみ緩和可、他8種は常時検査」と
# 定める。Self-Recoveryのdeterministic floor(FLOOR_FLAGS)は
# changed_comparisonを含むため、changed_comparisonをHook-awareで緩和する
# とfail-closedのfloor(既存安全装置)を弱めることになり、governanceの
# 「既存の安全装置を独自判断で回避・無効化しない」に抵触する。本委任では
# floorに含まれないchanged_scopeのみをHook-aware緩和の対象とし、
# changed_comparisonは対象外のまま維持する(Fable原案[§2]からの意図的な
# 縮小、監査文書に理由を記録、拡大にはFable/ユーザー判断が必要)。
# 判定は決定論的post-hoc(dev flagsのみで判定、LLMのHook解釈に依存しない
# 設計としたことでStage2 promptは変更していない、監査文書に設計理由を
# 記録)。
# ------------------------------------------------------------
HOOK_SECTION_TYPES = frozenset({"title", "hook", "in_one_line"})
HOOK_AWARE_ELIGIBLE_FLAG = "changed_scope"
HOOK_AWARE_OTHER_FLAGS = [
    "changed_fact", "changed_causality", "changed_certainty", "changed_number",
    "changed_actor", "changed_negation", "changed_comparison", "changed_time",
    "unsupported_new_claim",
]

_IN_ONE_LINE_TEXT_RE = re.compile(r"^##\s+In [Oo]ne [Ll]ine[…\.]*\s*\n(.+)", flags=re.MULTILINE | re.DOTALL)


def _extract_in_one_line_text(full_text: str) -> str:
    m = _IN_ONE_LINE_TEXT_RE.search(full_text or "")
    return m.group(1).strip() if m else ""


def detect_claim_section_type(claim_text: str, full_text: str) -> str:
    """claimがTitle/Hook(第1段落、委任_31 Part1(b)是正後は条件を満たす
    場合に限り第2段落=締め文も含む`_hook_paragraph_block`)/In one line/
    本文のどこに位置するかを決定論的に判定する(委任_14 B-5、¥0)。位置
    特定にはlocate_best_sentence(既存)を再利用し、新しいマッチング
    ロジックは発明しない。"""
    if not full_text:
        return "body"
    title = _paragraph_title(full_text)
    hook = _hook_paragraph_block(full_text)
    in_one_line = _extract_in_one_line_text(full_text)
    target, _method = locate_best_sentence(claim_text, full_text)
    probe = target or claim_text or ""
    probe_tokens = _normalize_tokens_for_jaccard(probe)

    def _overlaps(section_text: str, threshold: float) -> bool:
        if not section_text:
            return False
        if probe.strip() and (probe.strip() in section_text or section_text.strip() in probe):
            return True
        return _jaccard_similarity(probe_tokens, _normalize_tokens_for_jaccard(section_text)) >= threshold

    if _overlaps(title, 0.4):
        return "title"
    if _overlaps(in_one_line, 0.4):
        return "in_one_line"
    if _overlaps(hook, 0.3):
        return "hook"
    return "body"


# ------------------------------------------------------------
# Hook専用Stage2(委任_17、§2原因是正: Hook演出許容を共通rubricから分離)。
# detect_claim_section_typeの判定基準(既存、変更なし):
# - title: 記事先頭行(`_paragraph_title`、Markdown見出し記号を含む生の
#   1行)とのJaccard類似度[閾値0.4]または部分文字列一致。
# - hook: 本文第1段落+条件を満たす場合のみ第2段落(`_hook_paragraph_
#   block`=`_split_paragraphs_nonheading`が返す最初の段落、「#」始まりの
#   見出し行は除外される)との類似度[閾値0.3]。**委任_31 Part1(b)是正
#   (design書§4-24)**: 旧実装は常に`paras[0]`のみをhook候補として扱い、
#   2段落目以降(neg1実例の締め文「Meta had run a test that caused
#   exactly this surprise.」のような1文の演出)は「body」に誤分類される
#   既知の限界があった。第2段落が(a)1文のみ・(b)数字を含まない場合に
#   限り、Hook導入文の締め文とみなして含める(hormuz/meta_run03_
#   standard/bgroup_B3/neg3実測: 第2段落が複数文・具体的な数字/日付を
#   含む本文段落であるため対象外のまま、Safety回帰なしを確認済み)。
# - in_one_line: 「## In one line」見出し直後の1段落(`_extract_in_one_
#   line_text`)との類似度[閾値0.4]。**in_one_lineはHook専用Stage2の対象
#   外**(下記HOOK_ONLY_STAGE2_SECTION_TYPESに含まれない、§5-7の役割定義
#   どおり「短く圧縮して締める」機能でありHook演出とは役割が異なる。
#   委任_16でbgroup_B3がin_one_line区分に分類されたままHook-aware原則の
#   適用対象から除外されていたにもかかわらず誤降格したため[prompt
#   priming]、委任_17ではAPI call自体を分離することで構造的に遮断する)。
# - 上記いずれにも該当しなければ「body」。
#
# HOOK_ONLY_STAGE2_SECTION_TYPES(title/hookの2種のみ)に該当するclaimは
# Hook専用Stage2(er052_open233_self_recovery_stage2_hook_01、別Prompt・
# 別call)へ、それ以外(body/in_one_line)は既存Stage2
# (s2c.RUBRIC_R3_TRIPLE_PRIME、変更なし)へ振り分ける(run_stage2参照)。
# ------------------------------------------------------------
HOOK_ONLY_STAGE2_SECTION_TYPES = frozenset({"title", "hook"})


def build_title_hook_context(full_text: str) -> str:
    """Hook専用Stage2(委任_17 A-2)の入力用に、Title(見出し行)とHook段落
    (本文第1段落+条件を満たす場合のみ締め文の第2段落、委任_31 Part1(b)
    是正)のみを抽出して返す(¥0、決定論)。既存のローカル文脈±1段落
    (`s2p.build_local_context`)とは異なり、対象範囲をTitle/Hookのみへ
    意図的に限定する(委任文§3 A-2「入力=Ledger全文+source context+
    タイトル・hook段落+対象claim」)。"""
    title = _paragraph_title(full_text)
    hook = _hook_paragraph_block(full_text)
    return f"タイトル: {title}\n\nHook段落(本文第1段落+該当する場合は締め文): {hook}"


def apply_hook_aware_downgrade(materiality: str, dev: dict, section_type: str, floor_reason) -> tuple:
    """floor適用後のmaterialityに対し、Hook section×changed_scope単独×
    floor不発火の場合のみBLOCKING->QUALITYへpost-hoc downgradeする
    (委任_14 B-5)。changed_scopeがFLOOR_FLAGSに含まれないため、既存floor
    には一切触れない。"""
    if materiality != "BLOCKING" or floor_reason is not None:
        return materiality, None
    if section_type not in HOOK_SECTION_TYPES:
        return materiality, None
    if not dev.get(HOOK_AWARE_ELIGIBLE_FLAG):
        return materiality, None
    if any(dev.get(f) for f in HOOK_AWARE_OTHER_FLAGS):
        return materiality, None
    return "QUALITY", "hook_aware_scope_downgrade"


# ------------------------------------------------------------
# 委任_18 2-2(disclosure §1-2-2/§1-2-3、neg2_meta_refresh_a2/
# meta_run03_advanced=MUSE-HC-012パターン是正)。方式選択: disclosure文書
# §2-2で提示された(i)共通rubricの例示リスト追記[委任_16 B-2がprompt
# priming[Safety-critical bgroup_B3誤降格]を起こした前例あり]と(ii)
# deterministic post-Stage2条件の2案のうち、本委任は(ii)を採用する
# (理由: (i)は較正セット全体の再実行が必要でGuardrail ¥25/Phase B ¥20内に
# 収まらず、かつ委任_16の実測済みpriming riskを再度負うことになる。(ii)は
# ¥0・追加API callなし・既存floor/hook-aware downgradeと同じpost-hoc
# 判定パターンを踏襲でき、対象を狭い決定論条件に限定できるため安全側)。
#
# 条件(Ledgerが確認済みの「開示不備」から『読者/利用者はその時点で知る
# 手段がなかった』という論理的帰結を導く記述のみを対象とする):
# 1. floor不発火(floor_reason is None、既存floor[Safety側安全装置]には
#    一切触れない)。
# 2. unsupported_new_claim または changed_certainty のいずれかが立っている
#    (このパターンの実測フラグ、disclosure §1-2-2/§1-2-3)。
# 3. FLOOR_FLAGS+changed_scope(数値/時間/主体/比較/scopeという事実その
#    ものの変化)がいずれも立っていない(floorが本来カバーすべき種類の
#    変化には適用しない)。
# 4. claim文言が「知る手段がなかった/気づかなかった」系の**否定形**
#    (DISCLOSURE_GAP_NEGATION_RE)を含む(方向性を否定形のみへ限定。
#    neg1のような肯定形の主観断定[「驚いた」「気づいた」等]には適用しない、
#    disclosure §1-2-5でneg1はこの緩和の対象外と整理済み)。
# 5. claimがLedger本文に無い新しい数値・固有名詞を追加していない(既存
#    precheckの抽出器を再利用、¥0、「新しい具体的Factの発明」を機械的に
#    排除する)。
#
# Trial限定の判定候補であり、Production採用(APPROVED_FOR_PRODUCTION)には
# 別途ユーザー承認が必要(本委任はTrialコード[er052]のみを変更し、
# Production[er003/er009/er010/er012/er019]には一切配線しない)。
# ------------------------------------------------------------
DISCLOSURE_GAP_NEGATION_RE = re.compile(
    r"\b(did not|didn't|could not|couldn't|had no way to|were not aware|"
    r"was not aware|no way of knowing|could not tell|couldn't tell|"
    r"didn't realize|did not realize|did not know|didn't know)\b",
    re.IGNORECASE,
)
DISCLOSURE_GAP_DISQUALIFYING_FLAGS = FLOOR_FLAGS + ["changed_scope"]


def apply_disclosure_gap_downgrade(materiality: str, dev: dict, floor_reason, claim_text: str,
                                    ledger_text: str) -> tuple:
    if materiality != "BLOCKING" or floor_reason is not None:
        return materiality, None
    if any(dev.get(f) for f in DISCLOSURE_GAP_DISQUALIFYING_FLAGS):
        return materiality, None
    if not (dev.get("unsupported_new_claim") or dev.get("changed_certainty")):
        return materiality, None
    if not DISCLOSURE_GAP_NEGATION_RE.search(claim_text or ""):
        return materiality, None
    # 新規の数値を追加していないか(既存precheck抽出器の再利用、¥0)。
    claim_numbers = precheck.extract_percentages(claim_text) | set(precheck.extract_counts(claim_text))
    ledger_numbers = precheck.extract_percentages(ledger_text) | set(precheck.extract_counts(ledger_text))
    if claim_numbers - ledger_numbers:
        return materiality, None
    # 新規の固有名詞(人物・組織等)を追加していないか。claimの固有名詞候補
    # (extract_proper_nouns、既存precheck抽出器の再利用)が、ledger_text中に
    # (大小文字を問わず)一切現れなければ「新規」とみなす(extract_proper_
    # nouns同士を厳密比較すると"The AI"のような隣接語の連結差で誤検出する
    # ため、部分文字列包含という緩い基準にする、fail-closed側=新規と
    # 判定されればdowngradeしない、を維持)。
    claim_actors = precheck.extract_proper_nouns(claim_text or "")
    ledger_lower = (ledger_text or "").lower()
    new_actors = {a for a in claim_actors if precheck._strip_possessive(a).lower() not in ledger_lower}
    if new_actors:
        return materiality, None
    return "QUALITY", "disclosure_gap_negative_inference_downgrade(委任_18 2-2)"


def run_stage2(client, state, consecutive_errors, call_log, label, fixture, claims: list) -> list:
    """claims: list of dict(claim_text, origin, related_fact_id, dev[元deviation])。
    戻り値: 各claimにmateriality/basis/rewrite_kind/floor_appliedを付与したlist。"""
    check_budget(state)
    claim_records = []
    for c in claims:
        local_context, fallback = s2p.build_local_context(fixture["article_text"], c["claim_text"])
        # 委任_16 B-2(§2原因2是正、2026-09-30ユーザー新方針A)で、Stage2の
        # 判定自体にsection_type(title/hook/in_one_line/body)をLLM入力
        # として渡すRUBRIC_R4_HOOK_AWAREを一旦導入したが、代表ケースTrial
        # (作業C)でSafety-critical claim(bgroup_B3)の誤降格が再現し
        # (run_stage2下部のコメント・REPORT§17参照)、実配線をRUBRIC_R3_
        # TRIPLE_PRIMEへ復帰した。section_type自体はPython側の計算
        # (detect_claim_section_type、¥0)として引き続きclaim_recordsへ
        # 保持する(post-hoc downgrade[§6-4、changed_scope限定、既存の
        # まま安全に稼働中]・測定[§8-7]で使うため)が、**LLMプロンプトへは
        # 渡さない**(claim_records_for_stage2で除外、iteration6と同一の
        # プロンプト内容を維持し、未検証の側作用[prompt priming疑い]の
        # 混入を避ける)。
        section_type = detect_claim_section_type(c["claim_text"], fixture["article_text"])
        claim_records.append({**c, "local_context": local_context, "fallback_used": fallback,
                               "section_type": section_type})
    claim_records_for_stage2 = [{k: v for k, v in c.items() if k != "section_type"} for c in claim_records]

    # ------------------------------------------------------------
    # 委任_17(§2原因是正): 委任_16 B-2はHook-aware原則文をRUBRIC_R3_
    # TRIPLE_PRIME本体へ追記し同一batch call内へtitle/hook/body/in_one_line
    # の全claimを混在させたため、Safety-critical claim(bgroup_B3)がQUALITY
    # へ誤降格するprompt priming(原則文がプロンプト中に存在するだけで
    # section_type条件上は無関係なclaimの判定にも寛容化バイアスが波及する
    # 現象)が実測され、実配線をRUBRIC_R3_TRIPLE_PRIMEへ復帰した(旧コメント
    # 参照、REPORT§16)。委任_17は原則文の追記ではなく、**title/hookに
    # 位置するclaimのみを完全に別のPrompt・別のAPI call(Hook専用Stage2、
    # er052_open233_self_recovery_stage2_hook_01=s2h)へ分離**することで
    # priming経路そのものを構造的に遮断する。body/in_one_lineのclaimは
    # 既存どおりs2c.RUBRIC_R3_TRIPLE_PRIME(本文は一切変更しない、iteration
    # 4/5/6と同一のプロンプト内容)で判定する。2グループの判定は互いに
    # 別のcallであるため、一方のprompt文言が他方の判定へ波及する経路が
    # 存在しない(REPORT§17)。
    # ------------------------------------------------------------
    hook_indices = [i for i, c in enumerate(claim_records)
                    if c["section_type"] in HOOK_ONLY_STAGE2_SECTION_TYPES]
    body_indices = [i for i, c in enumerate(claim_records) if i not in hook_indices]

    judgments_by_index: dict = {}
    failclosed_indices: set = set()
    stage2_route_by_index: dict = {}

    def _run_stage2_group(group_indices: list, group_kind: str, call_fn) -> None:
        if not group_indices:
            return
        group_claims = [claim_records_for_stage2[i] for i in group_indices]
        group_label = f"{label}_stage2_{group_kind}"
        last_err = None
        result = None
        for _ in range(1 + MAX_RETRIES_PER_CALL):
            try:
                result = call_fn(group_claims)
                break
            except Exception as e:  # noqa: BLE001
                last_err = f"{type(e).__name__}: {e}"
                time.sleep(1.0)
        if result is None:
            call_log.append({"label": group_label, "recovery_stage": "stage2_second_judge",
                              "stage2_variant": group_kind, "error": last_err})
            record_call(state, consecutive_errors, group_label, 0.0, False, "stage2_second_judge")
            for i in group_indices:
                failclosed_indices.add(i)
                stage2_route_by_index[i] = f"{group_kind}_api_failure_failclosed"
            return
        call_log.append({"label": group_label, "recovery_stage": "stage2_second_judge",
                          "stage2_variant": group_kind, "cost_jpy": result["cost_jpy"],
                          "usage": result["usage"], "elapsed_seconds": result["elapsed_seconds"],
                          "prompt_sha256": result["prompt_sha256"]})
        record_call(state, consecutive_errors, group_label, result["cost_jpy"], True,
                    "stage2_second_judge", result["usage"])
        judgments = result["parsed"].get("judgments", [])
        for local_idx, global_idx in enumerate(group_indices):
            match = next((j for j in judgments if j.get("claim_index") == local_idx), None)
            if match is None:
                failclosed_indices.add(global_idx)
                stage2_route_by_index[global_idx] = f"{group_kind}_schema_index_mismatch_failclosed"
            else:
                judgments_by_index[global_idx] = match
                stage2_route_by_index[global_idx] = group_kind

    # body/in_one_line: 既存Stage2(R3'''、プロンプト内容は不変)。
    # 委任_30 Part2(design書§0/§9-1「既定構成の確定」): 重大誤解原則V4
    # (`BODY_RUBRIC_DEFAULT`、既定`ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT`=
    # True)を既定へ昇格する。V4は委任_29 Part1(Safety-critical 8claim+
    # Safety12+Hormuz許容5/NG5、n=2公式測定)で全件PASS確認済み
    # (REPORT§27-2)。旧挙動(V4適用前のRUBRIC_R3_TRIPLE_PRIME単体)は
    # `ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT=False`で復帰できる(既存
    # iteration1〜7・rep7〜15の再現性はそれらのOUT_DIRが既に固定済みの
    # 証跡のため本フラグの既定値変更とは無関係、新規runのみに影響)。
    _run_stage2_group(
        body_indices, "body",
        lambda cl: s2c.run_stage2_batch_variant(
            client, fixture["ledger_text"], fixture.get("source_article_text"),
            cl, BODY_RUBRIC_DEFAULT, model=MODEL,
        ),
    )
    # title/hook: Hook専用Stage2(s2h、別Prompt・別call。入力はLedger全文+
    # source context+タイトル・hook段落のみ、対象claimを含む段落±1段落の
    # ような広い文脈は渡さない)。委任_30 Part2: Hook rubricも同様にV4
    # (`HOOK_RUBRIC_DEFAULT`)を既定へ昇格する(委任_30 Part1でboundary-1
    # 残存の解消をn=2で確認済み、元Hook/NG4群も非回帰を確認済み)。
    title_hook_text = build_title_hook_context(fixture["article_text"]) if hook_indices else ""
    _run_stage2_group(
        hook_indices, "hook",
        lambda cl: s2h.run_stage2_hook_batch(
            client, fixture["ledger_text"], fixture.get("source_article_text"),
            title_hook_text, cl, model=MODEL, hook_rubric_text=HOOK_RUBRIC_DEFAULT,
        ),
    )

    out = []
    for i, c in enumerate(claim_records):
        if i in failclosed_indices:
            materiality, basis, rewrite_kind, rewrite_hint = (
                "BLOCKING", "none", "replace_with_ledger_value", "")
            floor_reason = "stage2_api_failure_failclosed"
        else:
            match = judgments_by_index.get(i)
            if match is None:
                materiality, basis, rewrite_kind, rewrite_hint = (
                    "BLOCKING", "none", "replace_with_ledger_value", "")
                floor_reason = "schema_index_mismatch_failclosed"
            else:
                materiality, basis, rewrite_kind = match["materiality"], match["basis"], match["rewrite_kind"]
                rewrite_hint = match.get("rewrite_hint", "") or ""
                floor_reason = None
        detected_by = c.get("detected_by", "stage1_llm")
        # 委任_14 B-1: floor評価直前にchanged_numberの丸め誤検出を除去する
        # (precheck floor[detected_by=="precheck"]は既に丸め対応済みの
        # check_number_mismatch経由のため対象外、ここではdeterministic
        # floor[Stage1 LLM flag由来]のみ対象)。
        dev_for_floor = (
            _sanitize_dev_for_rounding(c["dev"], c["claim_text"], fixture["ledger_text"])
            if detected_by != "precheck" else c["dev"]
        )
        final_materiality, floor_applied = apply_floor(materiality, dev_for_floor, detected_by)
        if floor_applied:
            floor_reason = floor_applied
        # 委任_14 B-2: floor-cited variantを反実仮想として同時計算し記録する
        # (実際のフロー制御には使わない、floor-strict[既存]のまま)。
        cited_materiality, cited_floor_applied = apply_floor_cited(
            materiality, dev_for_floor, detected_by, fixture["ledger_text"])
        # 委任_14 B-5: Hook-aware post-hoc downgrade(floor不発火時のみ、
        # changed_scope単独発火時のみ)。changed_comparisonは既存
        # deterministic floor(Safety側安全装置)の対象のままとし、本委任
        # では独自判断で緩和しない(監査文書に理由を記録)。委任_16 B-2で
        # section_typeはStage2入力(claim_records)へ既に付与済みのため
        # ここでは再計算せずc["section_type"]を再利用する(¥0、二重計算回避)。
        section_type = c.get("section_type") or detect_claim_section_type(
            c["claim_text"], fixture["article_text"])
        hook_materiality, hook_reason = apply_hook_aware_downgrade(
            final_materiality, dev_for_floor, section_type, floor_reason)
        if hook_reason:
            final_materiality = hook_materiality
            floor_reason = hook_reason
        # 委任_18 2-2: disclosure-gap negative inference downgrade
        # (MUSE-HC-012パターン、body claim。hook_aware[title/hook×
        # changed_scope]とは条件が排他的だが、念のためfloor_reasonの
        # 最新値[hook downgrade適用後]を渡し二重適用を防ぐ)。
        disclosure_materiality, disclosure_reason = apply_disclosure_gap_downgrade(
            final_materiality, dev_for_floor, floor_reason, c["claim_text"], fixture["ledger_text"])
        if disclosure_reason:
            final_materiality = disclosure_materiality
            floor_reason = disclosure_reason
        out.append({**c, "dev": dev_for_floor, "materiality": final_materiality, "llm_materiality": materiality,
                    "basis": basis,
                    "rewrite_kind": rewrite_kind if rewrite_kind != "none" else "replace_with_ledger_value",
                    "rewrite_hint": rewrite_hint, "floor_reason": floor_reason,
                    "section_type": section_type,
                    # 委任_17: このclaimがStage2のどちらの経路(body=s2c.
                    # RUBRIC_R3_TRIPLE_PRIME/hook=s2h Hook専用Stage2)を
                    # 通ったかのEvidence(¥0、call_logのlabel/stage2_variant
                    # と同じ情報をclaim単位でも直接確認できるようにする)。
                    "stage2_route": stage2_route_by_index.get(i, "unknown"),
                    "floor_cited_materiality": cited_materiality, "floor_cited_reason": cited_floor_applied})
    return out


# ------------------------------------------------------------
# Stage 2の2-of-2安定化(委任_13、iteration5、Opus L2レビュー#3論点3推奨3)。
# negative/Normal群(NORMAL_GROUP_INSTANCE_IDS、Stage1がV4AでPASS経験のある
# 記事)かつfloor不発(floor_reason is None、deterministic floor/precheck
# floorのfail-closedを経由しない)でStage2がBLOCKINGの場合のみ、同一Stage2
# をもう1回呼び、両方BLOCKINGの場合のみRewriteへ進む(1回でもQUALITY/
# ACCEPTABLEなら通過+ログ)。Stage2判定はrun間で非決定的(neg2/neg5とも
# n=3で2:1に割れる実測、Opus L2 #3論点3)であるため、安定化を狙う。
# 記事あたり+¥0.2程度(トリガしたclaim数×Stage2単価)。
# ------------------------------------------------------------
def stage2_two_of_two_eligible(inst: dict, result: dict) -> bool:
    return (
        result["materiality"] == "BLOCKING"
        and result.get("floor_reason") is None
        and inst["instance_id"] in NORMAL_GROUP_INSTANCE_IDS
    )


def apply_stage2_two_of_two(client, state, consecutive_errors, call_log, label_prefix, fixture,
                             stage2_results: list, inst: dict) -> tuple:
    eligible = [r for r in stage2_results if stage2_two_of_two_eligible(inst, r)]
    if not eligible:
        return stage2_results, []
    claims_for_second = [{"claim_text": r["claim_text"], "origin": r.get("origin"),
                           "related_fact_id": r.get("related_fact_id"), "dev": r["dev"],
                           "detected_by": r.get("detected_by", "stage1_llm")} for r in eligible]
    second_results = run_stage2(client, state, consecutive_errors, call_log,
                                 f"{label_prefix}_2of2", fixture, claims_for_second)
    second_by_identity = {claim_identity(r["dev"]): r for r in second_results}
    log_entries = []
    out = []
    for r in stage2_results:
        ident = claim_identity(r["dev"])
        if ident in second_by_identity:
            r2 = second_by_identity[ident]
            both_blocking = r2["materiality"] == "BLOCKING"
            log_entries.append({
                "claim_identity": ident, "first_materiality": r["materiality"],
                "second_materiality": r2["materiality"],
                "two_of_two_result": "BLOCKING(both agree)" if both_blocking else "DOWNGRADED(1/2 non-blocking)",
            })
            if not both_blocking:
                r = {**r, "materiality": r2["materiality"], "two_of_two_downgraded": True,
                     "two_of_two_second_materiality": r2["materiality"],
                     "two_of_two_second_basis": r2.get("basis")}
        out.append(r)
    return out, log_entries


# ------------------------------------------------------------
# Stage 3: Rewrite dispatch
# ------------------------------------------------------------
def locate_best_sentence(claim_text: str, full_text: str, ambiguous_margin: float = 0.08) -> tuple:
    """exact substring優先、無ければSequenceMatcher近傍探索(JA/EN共通の
    簡易汎用実装。専用の日本語文分割モジュールは実装しない、既知の限界
    として§5-4-補2と同一の位置づけ)。
    委任_10で追加: 最有力候補と次点候補のスコア差がambiguous_margin未満の
    場合は「ambiguous」として扱い、単一文を編集対象に確定させず
    呼び出し側の全文フォールバック(既存guard機構)へ委ねる(J-1改善、
    誤った文を編集してしまうリスクの低減)。"""
    if claim_text and claim_text.strip() in full_text:
        return claim_text.strip(), "exact_substring"
    sentences = re.split(r"(?<=[。.!?])", full_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    scored = sorted(
        ((difflib.SequenceMatcher(None, claim_text, s).ratio(), s) for s in sentences),
        key=lambda x: x[0], reverse=True,
    )
    if not scored:
        return None, "not_found"
    best_ratio, best = scored[0]
    second_ratio = scored[1][0] if len(scored) > 1 else 0.0
    # 文字単位SequenceMatcherは短い文同士だと偶然の一致でも比率が高くなり
    # やすいため(語単位jaccardより緩い)、閾値0.5(実測値: 言い換え一致
    # 0.92、無関係文0.41)をfail-closed側の下限として採用する。
    if best_ratio >= 0.5 and (best_ratio - second_ratio) >= ambiguous_margin:
        return best, f"sequence_matcher(ratio={round(best_ratio, 2)})"
    if best_ratio >= 0.5:
        return None, f"ambiguous(best={round(best_ratio, 2)},second={round(second_ratio, 2)})"
    return None, "not_found"


# ------------------------------------------------------------
# J-1(paired JA/EN local rewrite)ロケータ改善(委任_10、§5-4)
# ------------------------------------------------------------
# 開き引用符と閉じ引用符が異なる文字のペア(「」『』“”)はregexで安全に
# 抽出できるが、開き=閉じが同一文字("のみ)はfinditerの逐次マッチングだと
# 「1個目の引用が短すぎて{8,220}を満たさない場合、2個目の開き引用符を
# 1個目の閉じ引用符と誤ってペアリングしてしまう」既知のバグがある
# (委任_10のtestで実際に検出、隣接する2つの引用の間の非引用テキストを
# 誤抽出する)。そのため"はstr.split()による厳密なペアリングで処理する。
_BRACKET_QUOTE_PATTERNS = [
    re.compile(r"“([^”\n]{8,220})”"),
    re.compile(r"「([^」\n]{4,220})」"),
    re.compile(r"『([^』\n]{4,220})』"),
]
# 桁の並びのみ比較する(%等の記号は言語間で表記が揺れる[例: "20%"と"20
# percent"]ため比較対象から除く、位置比マッピングの数値トークン一致用)。
_DIGIT_TOKEN_RE = re.compile(r"\d+(?:\.\d+)?")


def extract_quoted_fragment(hint: str) -> str | None:
    """rewrite_hint文字列中の最長の引用断片(逐語引用)を抽出する(委任_10、
    §4-5で追加したrewrite_hintを対象文特定の第一キーとして使うための補助)。
    引用符が無ければNone(呼び出し側は既存のlocate_best_sentenceへfallback)。"""
    if not hint:
        return None
    candidates = []
    for pat in _BRACKET_QUOTE_PATTERNS:
        for m in pat.finditer(hint):
            frag = m.group(1).strip()
            if frag:
                candidates.append(frag)
    # 直双引用符(")は開き=閉じが同一文字のため、split()で厳密にペアリング
    # する(奇数indexの要素だけが引用符の内側)。
    parts = hint.split('"')
    for i in range(1, len(parts), 2):
        frag = parts[i].strip()
        if len(frag) >= 8:
            candidates.append(frag)
    if not candidates:
        return None
    return max(candidates, key=len)


def extract_quoted_fragment_present_in(hint: str, text: str) -> str | None:
    """委任_20 W1(iii): `extract_quoted_fragment`と同じ候補抽出だが、
    hint中に複数の引用(例:「元の文」を「置換後の文」に、のような
    rewrite_hint)が含まれる場合、textに逐語で実在する候補を優先して
    返す。`extract_quoted_fragment`単体は最長一致の候補を返すため、
    置換後の文の方が元の文(textに実在するはずの文)より長い場合に
    誤って置換後の文(textにまだ存在しない)を返してしまう既知の曖昧性が
    あり(rep10 hormuz_run03_standard実データで実際に発生、置換後の文が
    元の文より1文字長かった)、本関数はそれを避けるためtext中の実在を
    条件に含める。実在する候補が無ければNoneを返す(呼び出し側は保守的に
    skipする)。"""
    if not hint:
        return None
    candidates = []
    for pat in _BRACKET_QUOTE_PATTERNS:
        for m in pat.finditer(hint):
            frag = m.group(1).strip()
            if frag:
                candidates.append(frag)
    parts = hint.split('"')
    for i in range(1, len(parts), 2):
        frag = parts[i].strip()
        if len(frag) >= 8:
            candidates.append(frag)
    present = [c for c in candidates if c in text]
    if not present:
        return None
    return max(present, key=len)


# ------------------------------------------------------------
# 委任_36(§6-18、meta_run03_standard sample2 rep20 cycle2根本原因是正)
# ------------------------------------------------------------
# rep20 sample2 cycle2で実測した非収束パターン: Stage2 LLMがsame_fact_id_
# locations(複数箇所)を1つのclaimへ要約する際、claim_textが
# “They could not tell if it was AI or a person” and “They did not realize
# it.”のように、記事中の非隣接2文を“…”断片として"and"で結合した合成文に
# なった。この場合、従来のlocate_target()はclaim_text全体に対する1文
# fuzzy match(locate_best_sentence)しか試みないため、2断片のうち一方
# (ratio最大の1文)しか捕捉できず、もう一方の問題文がladder①〜④の
# いずれでも編集対象に入らないまま(guard_ok=False)ladder_exhausted_
# without_full_rewriteへ至った(sample1では同じfactが毎cycle単一文の
# claim_textとして現れ、既存のdisclosure_gap_negative_inference_downgrade
# floorでQUALITYへ降格されたため、この経路を踏まなかった)。
# 本修正は、claim_text自体が2つ以上のbracket-quote断片を含み、かつ全断片が
# full_text中に逐語で実在する場合に限り、それらを包含する最小スパンを
# 返す(いずれかの断片が不在・2段落以上に跨る・max_span_charsを超える場合は
# Noneを返し、既存のlocate_best_sentence経路へfail-closedで委ねる。単一
# 断片[従来通りextract_quoted_fragmentが拾う最長1件のみ]の場合は
# not_multi_quoteで即return Noneとし、既存の全既知ケース[test_01.py既存
# TestLocateTarget等]の挙動には一切影響しない)。
def extract_all_quoted_fragments(text: str) -> list:
    """`extract_quoted_fragment`の複数版。text中のbracket-quote断片
    (“”/「」/『』、_BRACKET_QUOTE_PATTERNS共用)を出現順にすべて返す
    (直引用符"の分割抽出は複数断片では既知のペアリング曖昧性[委任_10]が
    あるため対象外とし、安全側に絞る)。"""
    if not text:
        return []
    found = []
    for pat in _BRACKET_QUOTE_PATTERNS:
        for m in pat.finditer(text):
            frag = m.group(1).strip()
            if frag and frag not in found:
                found.append(frag)
    return found


def locate_multi_quote_span(claim_text: str, full_text: str, max_span_chars: int = 600) -> tuple:
    """claim_textが2つ以上のbracket-quote断片を結合した合成claimであり、
    かつ全断片がfull_text中に逐語で実在する場合のみ、それらを包含する
    最小スパン(最初の断片の開始〜最後の断片の終了)を返す。空行(段落区切り)
    を跨ぐ場合・max_span_charsを超える場合・断片が1つ以下・いずれかの断片が
    不在の場合はNoneを返す(fail-closed、呼び出し側は既存経路へ委ねる)。"""
    fragments = extract_all_quoted_fragments(claim_text)
    if len(fragments) < 2:
        return None, "not_multi_quote"
    positions = []
    for frag in fragments:
        idx = full_text.find(frag)
        if idx < 0:
            return None, "fragment_not_present"
        positions.append((idx, idx + len(frag)))
    span_start = min(p[0] for p in positions)
    span_end = max(p[1] for p in positions)
    if span_end <= span_start:
        return None, "invalid_span"
    span_text = full_text[span_start:span_end]
    if (span_end - span_start) > max_span_chars:
        return None, "span_too_long"
    if "\n\n" in span_text:
        return None, "span_crosses_paragraph"
    return span_text, "multi_quote_span"


def split_sentences_generic(text: str) -> list:
    """見出し行(#開始)を除いた本文を句点等(全角。！？/半角.!?)で分割する
    汎用関数(JA/EN共通、位置比計算用)。"""
    lines = [line.strip() for line in text.splitlines()
             if line.strip() and not line.strip().startswith("#")]
    flat = " ".join(lines)
    parts = re.split(r"(?<=[。！？.!?])\s*", flat)
    return [p.strip() for p in parts if p.strip()]


def split_ja_sentences(text: str) -> list:
    """JA本文を句点(全角。！？)で分割する(見出し行除外、単語間空白を仮定
    しないJA向けの分割、位置比マッピング用)。"""
    lines = [line.strip() for line in text.splitlines()
             if line.strip() and not line.strip().startswith("#")]
    flat = "".join(lines)
    parts = re.split(r"(?<=[。！？])", flat)
    return [p.strip() for p in parts if p.strip()]


_JA_CHAR_RE = re.compile(r"[぀-ゟ゠-ヿ一-鿿]")


def is_predominantly_ja(text: str, threshold: float = 0.15) -> bool:
    """委任_21 A-1: テキストがJA(ひらがな/カタカナ/漢字)主体かどうかを
    文字比率で判定する(¥0・決定論)。`ja_fail_open_guard`の分割器選択
    (JA=`split_ja_sentences`[句点。！？]/非JA=`split_sentences_generic`
    [.!?を含む汎用分割])に使う。rep11実データ(`bgroup_B3`)で
    `source_article_text`(本来JAのはずのfixtureフィールド)が実際には
    英語であり、句点分割が機能せず全文が1文として扱われ「1文丸ごと消失」
    という粗い誤検知を生んだ(既知の構造的限界)ことへの是正。空白を除いた
    全文字数に対するJA文字数の比率がthreshold未満なら非JAとみなす。"""
    if not text:
        return False
    ja_chars = len(_JA_CHAR_RE.findall(text))
    total_chars = len(re.sub(r"\s", "", text))
    if total_chars == 0:
        return False
    return (ja_chars / total_chars) >= threshold


def locate_target(claim_text: str, rewrite_hint: str, full_text: str) -> tuple:
    """対象文特定の統合ロケータ(委任_10、§5-4): 第一キー=rewrite_hintの
    引用断片(exact substring)、第二キー(委任_36追加)=claim_text自体が
    複数bracket-quote断片を結合した合成claimの場合の包含スパン
    (locate_multi_quote_span、§6-18)、第三キー=claim_textによる
    locate_best_sentence(exact/SequenceMatcher)、第四キー=
    er010.locate_target_sentence(英語word-overlap、read-only借用)。
    いずれも失敗(またはambiguous)の場合はNoneを返し、呼び出し側の全文
    フォールバックに委ねる。"""
    hint_fragment = extract_quoted_fragment(rewrite_hint)
    if hint_fragment and hint_fragment in full_text:
        return hint_fragment, "rewrite_hint_quote"
    multi_span, multi_method = locate_multi_quote_span(claim_text, full_text)
    if multi_span:
        return multi_span, multi_method
    target, method = locate_best_sentence(claim_text, full_text)
    if target is not None:
        return target, method
    try:
        fb_target, fb_method = er010.locate_target_sentence(claim_text, full_text)
    except Exception:  # noqa: BLE001
        fb_target, fb_method = None, "er010_fallback_error"
    if fb_target is not None:
        return fb_target, f"er010_word_overlap({fb_method})"
    return None, method


def locate_paragraph_block(target_sentence: str | None, full_text: str) -> tuple:
    """委任_11 作業B-4(§5段落単位Rewriteへの拡張、Opus L2 #2論点1推奨4):
    Rewrite対象単位を「引用文(1文)」から「同一含意を持つ段落ブロック」へ
    拡張するための段落特定。段落は空行(\\n\\n)区切りとする。target_sentence
    を含む段落の直前blockが見出し行(#開始)のみで構成される場合は、見出し/
    タイトル/hook行も対象へ含める(bgroup_B4[hook文+タイトル]・
    neg1_meta_b3prod_a2[タイトル]で実測された兄弟文カスケードへの対策)。
    見つからない場合は(None, None)を返し、呼び出し側は文単位の既存経路
    (locate_targetの結果そのもの)にフォールバックする。"""
    if not target_sentence:
        return None, None
    blocks = full_text.split("\n\n")
    for i, block in enumerate(blocks):
        if target_sentence.strip() and target_sentence.strip() in block:
            if i > 0 and blocks[i - 1].strip().startswith("#"):
                combined = blocks[i - 1] + "\n\n" + block
                return combined, (i - 1, i)
            return block, (i, i)
    return None, None


def locate_ja_counterpart_by_position(en_target: str, en_full: str, ja_full: str) -> tuple:
    """J-1改善(委任_10、§5-4): EN対象文のen_full内での文位置比を、JA全文の
    句点分割へ写像し(対訳記事はほぼ同順序で対応するという構造的近似)、
    写像先window(±2文)内で数値トークン(桁数・%等、言語非依存)一致を
    優先しつつ候補を選ぶ。数値トークンが無ければwindow中央(推定位置その
    もの)を採用する(固有名詞は言語間で一致しないため主キーにしない、
    既知の限界として報告する)。"""
    en_sentences = split_sentences_generic(en_full)
    ja_sentences = split_ja_sentences(ja_full)
    if not en_sentences or not ja_sentences:
        return None, "position_mapping_empty"

    en_index = None
    for i, s in enumerate(en_sentences):
        if en_target.strip() and (en_target.strip() in s or s in en_target.strip()):
            en_index = i
            break
    if en_index is None:
        best_i, best_ratio = 0, 0.0
        for i, s in enumerate(en_sentences):
            ratio = difflib.SequenceMatcher(None, en_target, s).ratio()
            if ratio > best_ratio:
                best_i, best_ratio = i, ratio
        en_index = best_i

    ratio_pos = en_index / max(1, len(en_sentences) - 1)
    ja_index_guess = round(ratio_pos * (len(ja_sentences) - 1))
    lo = max(0, ja_index_guess - 2)
    hi = min(len(ja_sentences), ja_index_guess + 3)
    window = ja_sentences[lo:hi]
    if not window:
        return None, "position_mapping_empty_window"

    en_digits = set(_DIGIT_TOKEN_RE.findall(en_target))
    if en_digits:
        for s in window:
            if en_digits & set(_DIGIT_TOKEN_RE.findall(s)):
                return s, f"ja_position_ratio+digit_match(idx={ja_index_guess})"
    center_idx = min(len(window) - 1, max(0, ja_index_guess - lo))
    return window[center_idx], f"ja_position_ratio(idx={ja_index_guess})"


# ------------------------------------------------------------
# 委任_14 作業B-3(最小変更ラダー、2026-09-30ユーザー新方針item3): Rewriteは
# 「最小変更」第一原則。①単語・接続詞のみ ②文の一部 ③1文 ④段落 ⑤より広い
# 範囲 ⑥記事全体、の順に試し、前段で直れば後段へ進まない。実装上は
# API呼び出し回数を無制限に増やさないため、①②を1つの「単語・接続詞のみ」
# 水準(E1_MINIMAL_WORD)に、④⑤を1つの「段落」水準(既存E2_PARAGRAPH)に
# 集約する(6段階の意図[小さい範囲から順に試し、前段で直れば止まる]は
# 保持しつつ、呼び出し段数を実務的な4水準[単語・接続詞/1文/段落/記事全体]
# に圧縮。詳細はdesign書§5-7・監査文書に記録)。B3型(接続詞"so"の因果、
# 2026-09-30ユーザー新方針item4)はこの水準①で"so"→"while"/"meanwhile"
# 相当への置換または文分割により解消を試みる。
# ------------------------------------------------------------
E1_MINIMAL_WORD_DEVELOPER_MSG = (
    "You are fixing a fact deviation flagged by a Ledger Deviation Checker, using the SMALLEST "
    "possible edit: swap a single word or connective, or split one sentence into two at a "
    "connective. Do not rewrite the sentence's content or structure beyond that. You may be given "
    "Japanese or English text."
)
E1_MINIMAL_WORD_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[Sentence flagged as a Ledger deviation]
{target_sentence}

[Checker's issue]
{issue}

[Rewrite hint]
{rewrite_hint}

Try to resolve the issue using ONLY a minimal edit: swap a single word, swap a connective (for \
example "so" -> "while" / "meanwhile" / "at the same time", or a causal connective that wrongly \
implies one thing caused another -> a connective that only states they happened together), remove a \
single qualifying word or short phrase, or split this one sentence into two sentences at a connective \
(without adding any new fact and without changing any other word). Do NOT rewrite the sentence's \
content or structure beyond this. Do NOT make the tone flatter, and do NOT remove its hook or \
storytelling value. Preserve the original intent and meaning wherever the Ledger allows. Keep the \
same language as the input sentence. Return ONLY the revised sentence (or two sentences if you split \
it), nothing else. If this issue genuinely CANNOT be resolved by such a minimal edit, return an empty \
string (do not attempt a larger rewrite)."""

E2_GENERIC_DEVELOPER_MSG = (
    "You are fixing a fact deviation flagged by a Ledger Deviation Checker, using the smallest "
    "possible edit (single-shot, no escalation). You may be given Japanese or English text."
)
E2_GENERIC_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[Sentence flagged as a Ledger deviation]
{target_sentence}

[Checker's issue]
{issue}

[Rewrite hint]
{rewrite_hint}

Rewrite ONLY this sentence to resolve the issue (delete the unsupported part, replace it with what the \
Ledger actually supports, or narrow its scope to match the Ledger, per the rewrite hint above). Keep the \
same language as the input sentence. Return ONLY the revised sentence, nothing else. If the issue is \
best resolved by deleting the sentence entirely, return an empty string."""

FULL_TEXT_FALLBACK_DEVELOPER_MSG = (
    "You are the article writer. You must revise the full article text to fix ONE flagged sentence, "
    "while keeping every other sentence character-for-character identical. The text may be Japanese or "
    "English."
)
FULL_TEXT_FALLBACK_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[Full article text]
{full_text}

[Sentence to fix]
{target_sentence}

[Checker's issue / rewrite_hint]
{issue}
{rewrite_hint}

Rewrite ONLY the sentence above (per the rewrite_hint). Do NOT change any other sentence in the article, \
not even punctuation or spacing. Return the FULL revised article text, nothing else (no explanation, no \
code fences)."""

J1_GENERIC_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[JA target sentence]
{ja_target}

[EN target sentence (translation of the same claim)]
{en_target}

[rewrite_hint]
{rewrite_hint}

Revise ONLY the JA target sentence and ONLY the EN target sentence (paired, minimal, local edit; do not \
touch anything else). Return strict JSON: {{"ja_revised": "...", "en_revised": "..."}}"""

# 委任_11 作業B-4(§5段落単位Rewrite、Opus L2 #2論点1推奨4): 引用文1文だけ
# でなく、同一含意を持つ段落ブロック(見出し/タイトル/hook行を含み得る)を
# 対象にする。「この段落内で同じ含意を述べる全ての文を削除・限定せよ」を
# 明記する(兄弟文カスケード対策)。
E2_PARAGRAPH_DEVELOPER_MSG = (
    "You are fixing a fact deviation flagged by a Ledger Deviation Checker. You must revise a paragraph "
    "block (which may include a heading/title/hook line) using the smallest edit that removes the "
    "unsupported claim from EVERY sentence in the block that states or implies it. You may be given "
    "Japanese or English text."
)
E2_PARAGRAPH_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[Paragraph block flagged as containing a Ledger deviation (may include a heading/title/hook line)]
{paragraph_block}

[Sentence originally flagged]
{target_sentence}

[Checker's issue]
{issue}

[Rewrite hint]
{rewrite_hint}

Rewrite this paragraph block to resolve the issue. Delete or narrow EVERY sentence in this block \
(including any heading/title/hook line) that states or implies the same unsupported claim, per the \
rewrite hint above. Keep the same language as the input. Leave sentences unrelated to this issue \
unchanged, character-for-character, wherever possible. Return ONLY the revised paragraph block text, \
nothing else (no explanation, no code fences)."""

J1_PARAGRAPH_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[JA paragraph block (may include a heading/title/hook line)]
{ja_block}

[EN paragraph block (translation of the same paragraph)]
{en_block}

[Originally flagged sentences]
JA: {ja_target}
EN: {en_target}

[rewrite_hint]
{rewrite_hint}

Revise BOTH paragraph blocks (paired, minimal edits). Delete or narrow EVERY sentence in EACH block \
(including any heading/title/hook line) that states or implies the same unsupported claim, per the \
rewrite_hint above. Leave sentences unrelated to this issue unchanged wherever possible. Return strict \
JSON: {{"ja_revised": "<full revised JA paragraph block>", "en_revised": "<full revised EN paragraph block>"}}"""

# 委任_16 B-1(J-1最小変更ラダー、2026-09-30ユーザー指示§2原因1是正): paired
# JA/EN rewrite(J-1)もsingle_text_rewriteと同じ①単語・接続詞のみ→③1文
# (既存J1_GENERIC)→④段落(既存J1_PARAGRAPH、対象文を含むブロックが両言語で
# 特定できる場合のみ)の順に試すladderへ再設計する(§5-7既知の限界の解消)。
# 水準①はJA側の接続詞置換(「〜ので/そのため/だから」→「一方/その間/
# 同じ頃」等)またはEN側のso→while/meanwhile相当の接続詞置換・文分割のみを
# 許可し、それ以外の書き換えは行わない(既存E1_MINIMAL_WORD_PROMPT_TEMPLATE
# と同じ最小編集原則をpaired版へ拡張)。
J1_MINIMAL_WORD_DEVELOPER_MSG = (
    "You are a bilingual (Japanese/English) editor fixing a Ledger deviation flagged by a Checker, "
    "using the SMALLEST possible edit to a paired JA/EN sentence: swap a single word or connective in "
    "BOTH languages (for example JA 　ので/そのため/だから -> "
    "一方/その間/同じ頃; EN \"so\" -> \"while\"/\"meanwhile\"/\"at the "
    "same time\"), or split each sentence into two at that connective. Do not change anything else."
)
J1_MINIMAL_WORD_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[JA target sentence]
{ja_target}

[EN target sentence (translation of the same claim)]
{en_target}

[Checker's issue]
{issue}

[rewrite_hint]
{rewrite_hint}

Try to resolve the issue using ONLY a minimal edit to BOTH sentences: swap a single word, swap a \
causal connective that wrongly implies one thing caused another for a connective that only states \
they happened together (JA: ので/そのため/だから -> 一方/\
その間/同じ頃等; EN: "so" -> "while"/"meanwhile"/"at the same time"), remove \
a single qualifying word or short phrase, or split each sentence into two at that connective (without \
adding any new fact and without changing any other word). Do NOT rewrite the sentence's content or \
structure beyond this. Return strict JSON: {{"ja_revised": "...", "en_revised": "..."}}. If this issue \
genuinely CANNOT be resolved by such a minimal edit, return {{"ja_revised": "", "en_revised": ""}} (do \
not attempt a larger rewrite)."""


def single_text_rewrite(client, state, consecutive_errors, call_log, label_prefix, fixture, target_text_field,
                         claim_rec: dict) -> dict:
    """claim_rec['dev']の言語テキスト(target_text_field='article_text'固定、
    JA単体fixtureもarticle_text側にJA本文が入っている、g6.load_audit_fixture
    の仕様どおり)に対する単一言語local rewrite。delete型はまず決定論的削除を
    試し、それ以外(replace_with_ledger_value/narrow_scope)はE-2汎用Promptを
    使う。guard抵触(対象文が特定できない/置換後も同じ問題文言が残る)時は
    1回だけ全文最小編集フォールバックを試す。"""
    full_text = fixture[target_text_field]
    claim_text = claim_rec["claim_text"]
    rewrite_kind = claim_rec["rewrite_kind"]
    dev = claim_rec["dev"]
    issue = dev.get("issue") or dev.get("explanation") or claim_text
    # 委任_10: Stage2出力のrewrite_hint(LLM生成、対象文引用+修正指示+fact_id)を
    # 優先して使う。空の場合(schema_index_mismatch等のfail-closed経路)のみ
    # 旧来の合成文字列へfallbackする。
    rewrite_hint = claim_rec.get("rewrite_hint") or f"materiality={claim_rec['materiality']}, basis={claim_rec['basis']}"
    # 委任_13(iteration5): Rewrite品質制約(レベル別語彙・文長制約+hook保持+
    # 削除優先、+regeneration時は強調文)をrewrite_hintへ追記する(既存
    # テンプレートは変更せず、既存の{rewrite_hint}埋め込み箇所を使う非侵襲策)。
    rewrite_hint = rewrite_hint + claim_rec.get("extra_constraint", "")

    target_sentence, locate_method = locate_target(claim_text, rewrite_hint, full_text)
    method_used = None
    updated_text = full_text
    found = target_sentence is not None
    after_fragment = None  # 委任_13: cite-or-release用のbefore/afterペア(単一文置換時のみ判明)

    delete_reoccurrence_detected = False
    if rewrite_kind == "delete":
        if found:
            updated_text = full_text.replace(target_sentence, "", 1)
            method_used = f"deterministic_delete({locate_method})"
            after_fragment = ""
            # 委任_10: delete型のclaim単位再出現確認(§2-4)。exact substring
            # 一致だけでなく、言い換えによる同一claimの再出現もfuzzy match
            # (locate_best_sentence)で検出し、見つかった場合はguard抵触
            # として全文フォールバックへ回す(削除漏れ・重複箇所の見逃し対策)。
            reoccur_target, _reoccur_method = locate_best_sentence(claim_text, updated_text)
            delete_reoccurrence_detected = reoccur_target is not None
        else:
            method_used = "delete_target_not_found"
    ladder_level_used = None
    if rewrite_kind != "delete":
        if found:
            # 委任_14 作業B-3(最小変更ラダー): ①単語・接続詞のみ(E1) ->
            # ③1文(既存E2_GENERIC) -> ④段落(既存E2_PARAGRAPH、対象文を含む
            # 段落ブロックが特定できる場合のみ)、の順に試し、guardを満たした
            # 最初の水準で止める(前段で直れば後段へ進まない)。
            levels = []
            prompt_l1 = E1_MINIMAL_WORD_PROMPT_TEMPLATE.format(
                ledger_text=fixture["ledger_text"], target_sentence=target_sentence,
                issue=issue, rewrite_hint=rewrite_hint,
            )
            levels.append({"name": "1_word_connective", "prompt": prompt_l1,
                            "dev_msg": E1_MINIMAL_WORD_DEVELOPER_MSG,
                            "label": f"{label_prefix}_e1_minimal_word", "target": target_sentence,
                            "tag": "e1_minimal_word_edit", "allow_empty_as_delete": False})
            prompt_l3 = E2_GENERIC_PROMPT_TEMPLATE.format(
                ledger_text=fixture["ledger_text"], target_sentence=target_sentence,
                issue=issue, rewrite_hint=rewrite_hint,
            )
            levels.append({"name": "3_sentence", "prompt": prompt_l3, "dev_msg": E2_GENERIC_DEVELOPER_MSG,
                            "label": f"{label_prefix}_e2_rewrite", "target": target_sentence,
                            "tag": "e2_generic_rewrite", "allow_empty_as_delete": True})
            # 委任_11 作業B-4: 対象文を含む段落ブロック(見出し/タイトル行を
            # 含み得る)が特定できれば水準④として追加する(兄弟文カスケード対策)。
            paragraph_block, _ = locate_paragraph_block(target_sentence, full_text)
            if paragraph_block:
                prompt_l4 = E2_PARAGRAPH_PROMPT_TEMPLATE.format(
                    ledger_text=fixture["ledger_text"], paragraph_block=paragraph_block,
                    target_sentence=target_sentence, issue=issue, rewrite_hint=rewrite_hint,
                )
                levels.append({"name": "4_paragraph", "prompt": prompt_l4,
                                "dev_msg": E2_PARAGRAPH_DEVELOPER_MSG,
                                "label": f"{label_prefix}_e2_paragraph_rewrite", "target": paragraph_block,
                                "tag": "e2_paragraph_rewrite", "allow_empty_as_delete": True})

            # 委任_19 A-2: 同一fact_idが過去cycleで既にBLOCKINGだった
            # claim(別文言・別箇所での再出現)は、①単語・接続詞/③1文の
            # 局所ラダーが既に効果不足と実証されたとみなし、④段落水準
            # から試す(該当ブロックが無ければ levels が空になり、既存の
            # ⑥全体フォールバックへ自然に委ねる、新しいNG経路は作らない)。
            if ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP and claim_rec.get("escalate_to_paragraph"):
                levels = [lv for lv in levels if lv["name"] not in ("1_word_connective", "3_sentence")]
            # 委任_27 Part1-2(§0-4/§5-11): 問題種類→初期Rewrite単位の写像
            # (escalate_to_paragraphの再出現ベース判断とは独立の、問題種類
            # ベースの初期水準選択。初期水準より上位への昇段は妨げない)。
            problem_kind = classify_problem_kind(dev)
            claim_rec["problem_kind"] = problem_kind
            levels = filter_levels_by_problem_kind(levels, dev)

            for lv in levels:
                revised = simple_llm_call(client, state, consecutive_errors, call_log, lv["label"],
                                           lv["dev_msg"], lv["prompt"], model=MODEL)
                if revised is None:
                    method_used = f"{lv['tag']}_api_failure"
                    continue
                if revised == "" and not lv["allow_empty_as_delete"]:
                    method_used = f"{lv['tag']}_declined"
                    continue
                candidate = full_text.replace(lv["target"], revised, 1)
                if candidate != full_text and claim_text.strip() not in candidate:
                    # 委任_31 Part1(a)是正(design書§4-24): 主体置換ガードを
                    # problem_kindに関係なく常に評価する。旧実装は
                    # `problem_kind == "actor"`の場合のみ評価していたため、
                    # classify_problem_kindの優先順位(term_scope>actor)に
                    # よりchanged_scope/changed_actorが同時に真のclaimでは
                    # ガードが一度も発火しない設計上の盲点があった(委任_30
                    # Trial C期待2で発見)。actor_rewrite_guard_ok自体は
                    # 新しい主体語が導入されない場合は常にTrueを返す
                    # no-opのため(§0-5既存仕様)、常時評価してもunspecified/
                    # term_scope等の既存経路への非回帰影響はない。
                    if not actor_rewrite_guard_ok(
                            lv["target"], revised, fixture["ledger_text"]):
                        method_used = f"{lv['tag']}_actor_guard_rejected({locate_method})"
                        continue
                    updated_text = candidate
                    method_used = f"{lv['tag']}({locate_method})"
                    ladder_level_used = lv["name"]
                    # paragraph水準はtarget_sentence単位のafter断片を一意に
                    # 特定できないため(段落内の他文も変わり得る)、
                    # cite-or-release用のafter_fragmentはNoneのまま(既知の限界)。
                    after_fragment = revised if lv["target"] == target_sentence else None
                    break
                method_used = f"{lv['tag']}_guard_failed({locate_method})"
        else:
            method_used = "target_not_found"

    guard_ok = (updated_text != full_text and claim_text.strip() not in updated_text
                and not delete_reoccurrence_detected) if found else False
    # 委任_18 2-1(b)(d): 対象文が一度も特定できない場合(found=False)は、
    # ①〜④のladderが一度も試行されていない(§1-1-1で機械確認済みの根本
    # 原因)。この場合に⑥全体フォールバックを「試行して失敗した最後の
    # 手段」として使うのは不適切なため、Rewriteを試みずStage4
    # (target_not_locatable)へ回す(呼び出し側run_instanceが処理)。
    # found=True(対象文は特定できたが、ladder全段でguardが失敗、または
    # delete再出現検出)の場合は、①〜④の試行ログがcall_logに残っている
    # 正当な最後の手段として、従来どおり⑥を試みる(disclosure §1-1-3で
    # ⑥が①より安全だった実例があるため、この経路は残す)。
    if not found:
        return {"updated_text": full_text, "method": method_used, "guard_ok": False,
                "target_sentence": None, "locate_method": locate_method,
                "delete_reoccurrence_detected": delete_reoccurrence_detected,
                "before_fragment": None, "after_fragment": None,
                "ladder_level_used": None, "target_not_locatable": True}
    if not guard_ok:
        after_fragment = None
        # 委任_23 B-2: ⑥を標準ラダーから外す(既定OFF、iter7実測で7/7が
        # ⑥使用後も最終的にSTAGE4に至り「⑥が必要だった」Evidenceが0件
        # だったため)。target_not_locatableと同じパターンで、呼び出し側
        # run_instanceへladder_exhausted_without_full_rewriteを返し、
        # ⑥のAPI callを試みず直ちにStage4へ回す(feature flag、既定OFF)。
        if not ENABLE_LADDER_LEVEL_6_FULL_REWRITE:
            return {"updated_text": full_text, "method": (method_used or "") + "+ladder6_disabled",
                    "guard_ok": False, "target_sentence": target_sentence, "locate_method": locate_method,
                    "delete_reoccurrence_detected": delete_reoccurrence_detected,
                    "before_fragment": target_sentence, "after_fragment": None,
                    "ladder_level_used": None, "target_not_locatable": False,
                    "ladder_exhausted_without_full_rewrite": True}
        # guard抵触(ラダー全段で置換後も同じclaim文言が残存、またはdelete
        # 再出現検出) -> 全文最小編集フォールバック(水準⑥、§5-2/§5-4の
        # フォールバック段2に相当。found=Trueで①〜④[delete型は0]を実際に
        # 試行した記録がある場合のみ到達する、委任_18 2-1(d))。
        prompt = FULL_TEXT_FALLBACK_PROMPT_TEMPLATE.format(
            ledger_text=fixture["ledger_text"], full_text=full_text,
            target_sentence=target_sentence or claim_text, issue=issue, rewrite_hint=rewrite_hint,
        )
        fallback_text = simple_llm_call(client, state, consecutive_errors, call_log,
                                              f"{label_prefix}_fulltext_fallback",
                                              FULL_TEXT_FALLBACK_DEVELOPER_MSG, prompt, model=MODEL)
        if fallback_text:
            updated_text = fallback_text
            method_used = (method_used or "") + "+fulltext_fallback"
            guard_ok = updated_text != full_text
            if guard_ok:
                ladder_level_used = "6_full_article"
        else:
            method_used = (method_used or "") + "+fulltext_fallback_api_failure"
    elif rewrite_kind == "delete":
        ladder_level_used = "0_delete"

    return {"updated_text": updated_text, "method": method_used, "guard_ok": guard_ok,
            "target_sentence": target_sentence, "locate_method": locate_method,
            "delete_reoccurrence_detected": delete_reoccurrence_detected,
            "before_fragment": target_sentence, "after_fragment": after_fragment,
            "ladder_level_used": ladder_level_used, "target_not_locatable": False}


def paired_rewrite(client, state, consecutive_errors, call_log, label_prefix, fixture, claim_rec: dict) -> dict:
    """JA/EN pairing(article_text=EN, source_article_text=JA)がある場合の
    paired local rewrite(J-1一般化)。JA側は言及先が特定できない場合が
    多いため、claim_textはEN側(article_text)から検出したものを使い、対応する
    JA文はsource_article_text側で同一claim_text/related_fact_idに近い文を
    best-effortで探す(専用の対訳アラインメントは実装しない、既知の限界)。"""
    en_full = fixture["article_text"]
    ja_full = fixture["source_article_text"]
    claim_text = claim_rec["claim_text"]
    dev = claim_rec["dev"]
    # 委任_10: Stage2出力のrewrite_hint(LLM生成)を優先して使う。空の場合
    # (fail-closed経路等)のみ旧来の合成文字列へfallbackする。
    rewrite_hint = claim_rec.get("rewrite_hint") or (
        f"materiality={claim_rec['materiality']}, basis={claim_rec['basis']}, "
        f"issue={dev.get('issue') or dev.get('explanation') or ''}"
    )
    # 委任_13(iteration5): single_text_rewriteと同様、Rewrite品質制約を
    # rewrite_hintへ追記する(既存テンプレートは変更しない非侵襲策)。
    rewrite_hint = rewrite_hint + claim_rec.get("extra_constraint", "")

    en_target, en_method = locate_target(claim_text, rewrite_hint, en_full)
    # JA側ロケータ改善(委任_10、§5-4): 第一キー=rewrite_hintの引用断片
    # (もしJA本文中に逐語引用があれば)、第二キー=claim_text自体での
    # lexical探索(claim_textはEN文のため通常は失敗する、既知の限界)、
    # 第三キー=Ledger claim文言でのlexical探索(既存)、第四キー(NEW)=
    # EN対象文のen_full内での文位置比をJA全文へ写像する構造的近似
    # (対訳記事がほぼ同順序で対応するという仮定、locate_ja_counterpart_
    # by_position)。
    # 委任_36追加(§6-18): en_targetがmulti_quote_span(複合引用claim、上記
    # locate_target参照)で特定された場合、rewrite_hintの引用断片は
    # Stage2 LLMが生成した別文言の言い換えであることが多く、en_targetの
    # スパンと無関係な箇所をja_full中から拾ってしまうリスクがある(rep20
    # sample2 cycle2実測: hint_fragmentがen_targetスパンより前の別文に対応
    # するJA文を拾い、EN/JAが不整合なまま3段のladderが全てguard失敗した)。
    # この場合はhint_fragment一致より位置写像(既存第四キー)を優先する
    # (失敗時は以下の既存優先順位へfail-closedで委ねる、非multi_quote_span
    # の既存経路は一切変更しない)。
    ja_target, ja_method = None, "not_attempted"
    if en_method == "multi_quote_span" and en_target is not None:
        ja_target, ja_method = locate_ja_counterpart_by_position(en_target, en_full, ja_full)
    hint_fragment = extract_quoted_fragment(rewrite_hint)
    if ja_target is None and hint_fragment and hint_fragment in ja_full:
        ja_target, ja_method = hint_fragment, "rewrite_hint_quote"
    if ja_target is None:
        ja_target, ja_method = locate_best_sentence(claim_text, ja_full)
    if ja_target is None:
        # claim_textのEN文言でJA側から探せない場合、related_fact_idの
        # Ledger claim文言をprobeとして再探索する(近似、完全一致は保証しない)。
        facts = precheck.parse_ledger_text(fixture["ledger_text"])
        fact = next((f for f in facts if f.get("fact_id") == (dev.get("related_fact_id") or "")), None)
        if fact and fact.get("claim"):
            ja_target, ja_method = locate_best_sentence(fact["claim"], ja_full)
    if ja_target is None and en_target is not None:
        ja_target, ja_method = locate_ja_counterpart_by_position(en_target, en_full, ja_full)

    en_located = en_target is not None
    ja_located = ja_target is not None
    guard_ok = False
    method = None
    updated_en = en_full
    updated_ja = ja_full
    # 委任_30 Part3 FAIL是正(小修正1回、neg3_hormuz_prodrunner_b1b根本原因、
    # design書§9-1追記予定): 下記`en_located and ja_located`分岐の外側
    # (片側のみ特定できた新設elif分岐)でもこれらの変数が未定義にならない
    # よう既定値を与える(後段のcite-or-release判定式が参照するため)。
    use_paragraph = False
    en_revised = None

    # 委任_18 2-1(b)(d): EN/JA双方とも対象文が一度も特定できない場合
    # (single_text_rewriteと同一原則)、①〜④のladderは意味を持たず、
    # 既存のJA全文フォールバック→EN全文フォールバックの連鎖([6_full_article]
    # 相当)を「試行して失敗した最後の手段」として使うのは不適切。
    # Rewriteを試みずStage4(target_not_locatable)へ回す。片方のみ特定
    # できた場合(既存のJA全文フォールバック+EN局所編集等の部分回復)は
    # 変更しない(既知の正当な回復経路のため、対象を完全未特定の場合のみに限定)。
    if not en_located and not ja_located:
        return {"updated_en_text": en_full, "updated_ja_text": ja_full, "method": "j1_target_not_locatable",
                "guard_ok": False, "en_target": None, "ja_target": None,
                "before_fragment": None, "after_fragment": None, "ladder_level_used": None,
                "target_not_locatable": True}

    ladder_level_used = None
    if en_located and ja_located:
        # 委任_16 B-1(最小変更ラダー、§2原因1是正): ①単語・接続詞のみ(新設
        # J1_MINIMAL_WORD)→③1文(既存J1_GENERIC)→④段落(既存J1_PARAGRAPH、
        # 対象文を含むブロックが両言語で特定できる場合のみ)の順に試し、
        # guardを満たした最初の水準で止める(single_text_rewriteと同一原則)。
        ja_block, _ = locate_paragraph_block(ja_target, ja_full)
        en_block, _ = locate_paragraph_block(en_target, en_full)
        has_paragraph_block = bool(ja_block) and bool(en_block)
        issue = dev.get("issue") or dev.get("explanation") or ""

        levels = []
        prompt_l1 = J1_MINIMAL_WORD_PROMPT_TEMPLATE.format(
            ledger_text=fixture["ledger_text"], ja_target=ja_target, en_target=en_target,
            issue=issue, rewrite_hint=rewrite_hint,
        )
        levels.append({"name": "1_word_connective", "prompt": prompt_l1,
                        "dev_msg": J1_MINIMAL_WORD_DEVELOPER_MSG,
                        "label": f"{label_prefix}_j1_e1_minimal_word",
                        "ja_target": ja_target, "en_target": en_target,
                        "tag": "j1_e1_minimal_word", "use_paragraph": False})
        prompt_l3 = J1_GENERIC_PROMPT_TEMPLATE.format(
            ledger_text=fixture["ledger_text"], ja_target=ja_target, en_target=en_target,
            rewrite_hint=rewrite_hint,
        )
        levels.append({"name": "3_sentence", "prompt": prompt_l3, "dev_msg": s3rt.J1_DEVELOPER_MSG,
                        "label": f"{label_prefix}_j1_paired_rewrite",
                        "ja_target": ja_target, "en_target": en_target,
                        "tag": "j1_paired_rewrite", "use_paragraph": False})
        if has_paragraph_block:
            prompt_l4 = J1_PARAGRAPH_PROMPT_TEMPLATE.format(
                ledger_text=fixture["ledger_text"], ja_block=ja_block, en_block=en_block,
                ja_target=ja_target, en_target=en_target, rewrite_hint=rewrite_hint,
            )
            levels.append({"name": "4_paragraph", "prompt": prompt_l4, "dev_msg": s3rt.J1_DEVELOPER_MSG,
                            "label": f"{label_prefix}_j1_paired_rewrite_paragraph",
                            "ja_target": ja_block, "en_target": en_block,
                            "tag": "j1_paired_rewrite_paragraph", "use_paragraph": True})

        # 委任_19 A-2(single_text_rewriteと同一原則): 同一fact_idが過去
        # cycleで既にBLOCKINGだったclaim(別文言・別箇所での再出現)は
        # ①単語・接続詞/③1文を飛ばし④段落水準から試す。該当ブロックが
        # 両言語で特定できなければlevelsが空になり、既存のJA全文
        # フォールバック(⑥相当)へ自然に委ねる。
        if ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP and claim_rec.get("escalate_to_paragraph"):
            levels = [lv for lv in levels if lv["name"] not in ("1_word_connective", "3_sentence")]
        # 委任_27 Part1-2(single_text_rewriteと同一原則、§0-4/§5-11)。
        problem_kind = classify_problem_kind(dev)
        claim_rec["problem_kind"] = problem_kind
        levels = filter_levels_by_problem_kind(levels, dev)

        for lv in levels:
            raw = simple_llm_call(client, state, consecutive_errors, call_log, lv["label"],
                                        lv["dev_msg"], lv["prompt"], model=MODEL)
            try:
                parsed = s3rt.extract_json_obj(raw) if raw else {}
            except Exception:  # noqa: BLE001
                parsed = {}
            ja_revised = parsed.get("ja_revised", "")
            en_revised = parsed.get("en_revised", "")
            candidate_ja = ja_full.replace(lv["ja_target"], ja_revised, 1) if ja_revised else ja_full
            candidate_en = en_full.replace(lv["en_target"], en_revised, 1) if en_revised else en_full
            level_guard_ok = (
                bool(ja_revised) and bool(en_revised)
                and candidate_ja != ja_full and candidate_en != en_full
                and claim_text.strip() not in candidate_en
            )
            # 委任_31 Part1(a)是正(design書§4-24): single_text_rewriteと
            # 同一理由でproblem_kindに関係なく常に評価する(委任_30 Trial C
            # 期待2で発見したterm_scope>actor優先順位による盲点の是正)。
            if level_guard_ok and not actor_rewrite_guard_ok(
                    lv["en_target"], en_revised, fixture["ledger_text"]):
                level_guard_ok = False
            if level_guard_ok:
                updated_ja, updated_en = candidate_ja, candidate_en
                guard_ok = True
                use_paragraph = lv["use_paragraph"]
                method = lv["tag"]
                ladder_level_used = lv["name"]
                break
    elif en_located != ja_located:
        # 委任_30 Part3 FAIL是正(小修正1回、neg3_hormuz_prodrunner_b1b根本
        # 原因、design書§9-1追記予定): 片側のみ対象文が特定できた場合(既知の
        # 限界、例: EN側が別cycleで既に解決済みのため元claim文言が現存の
        # 記事に残っていない)、従来は`if en_located and ja_located:`の外側
        # (この関数本体)でlevels構築自体が一度も実行されず、method=None
        # のまま直後の`if not guard_ok:`→⑥(disabled)経路へ落ちて0 call
        # でStage4に至っていた(本委任で実測・特定)。⑥(JA/EN全文フォール
        # バック、`ENABLE_LADDER_LEVEL_6_FULL_REWRITE`既定OFF)は再有効化
        # せず、特定できた側だけを対象に既存`single_text_rewrite`
        # (①〜④の非⑥ローカル編集ラダー、新規テンプレートは追加しない)を
        # 適用する(未特定側は変更しない)。
        only_located_field = "article_text" if en_located else "source_article_text"
        only_full_text = en_full if en_located else ja_full
        mini_fixture = {"ledger_text": fixture["ledger_text"], only_located_field: only_full_text}
        single_result = single_text_rewrite(
            client, state, consecutive_errors, call_log, f"{label_prefix}_j1_single_side",
            mini_fixture, only_located_field, claim_rec)
        if single_result.get("guard_ok"):
            if en_located:
                updated_en = single_result["updated_text"]
            else:
                updated_ja = single_result["updated_text"]
            guard_ok = True
            method = f"j1_single_side_{'en' if en_located else 'ja'}({single_result.get('method')})"
            ladder_level_used = single_result.get("ladder_level_used")

    # 委任_13: cite-or-release用のbefore/afterペア(単一文置換時のみ判明。
    # paragraph-level rewriteはtarget_sentence単位のafter断片を一意に
    # 特定できないため既知の限界としてNoneのまま)。
    en_after_fragment = en_revised if (guard_ok and not use_paragraph and en_located and ja_located) else None

    if not guard_ok:
        # 委任_23 B-2: ⑥を標準ラダーから外す(既定OFF、iter7実測で7/7が
        # ⑥使用後も最終的にSTAGE4に至り「⑥が必要だった」Evidenceが0件
        # だったため)。single_text_rewriteと同一パターンで、⑥(JA全文
        # フォールバック→EN側対応)のAPI callを試みず直ちにStage4へ回す
        # (feature flag、既定OFF)。
        if not ENABLE_LADDER_LEVEL_6_FULL_REWRITE:
            return {"updated_en_text": en_full, "updated_ja_text": ja_full,
                    "method": (method or "") + "+ladder6_disabled", "guard_ok": False,
                    "en_target": en_target, "ja_target": ja_target,
                    "before_fragment": en_target, "after_fragment": None,
                    "ladder_level_used": None, "target_not_locatable": False,
                    "ladder_exhausted_without_full_rewrite": True}
        # 委任_11 作業B-1(バグA是正、Opus L2 #2論点1推奨1): 従来はen_target/
        # ja_targetのいずれかが特定できない(j1_pair_not_located)場合、この
        # 全文フォールバックへ到達せず早期returnしていたため、テキストが
        # 一切変わらないままcycle2で同一fact_idが再検出され、claim_identity()
        # 一致により即Stage4していた(safety_A2A3で実測、Opus L2 #2論点1)。
        # 本is正では、locate失敗の場合も含め必ずJA全文フォールバックを試みる。
        ja_target_for_fb = ja_target or claim_text
        prompt_fb = FULL_TEXT_FALLBACK_PROMPT_TEMPLATE.format(
            ledger_text=fixture["ledger_text"], full_text=ja_full, target_sentence=ja_target_for_fb,
            issue=dev.get("issue") or "", rewrite_hint=rewrite_hint,
        )
        ja_fallback = simple_llm_call(client, state, consecutive_errors, call_log,
                                            f"{label_prefix}_j1_fulltext_fallback",
                                            FULL_TEXT_FALLBACK_DEVELOPER_MSG, prompt_fb, model=MODEL)
        if ja_fallback:
            updated_ja = ja_fallback
            ja_guard_ok = updated_ja != ja_full
            # 委任_11 作業B-2(バグB是正、Opus L2 #2論点1推奨2/論点4推奨1):
            # JA全文フォールバック後にEN側を無編集のまま残すと、JA/EN記事対が
            # 構造的に乖離する(safety_A4で実測)。EN側も同一rewrite_hintで
            # 必ず1 call編集する(en_targetが特定できればE-2局所編集、
            # できなければEN側も全文フォールバック)。
            if en_target is not None:
                prompt_en = E2_GENERIC_PROMPT_TEMPLATE.format(
                    ledger_text=fixture["ledger_text"], target_sentence=en_target,
                    issue=dev.get("issue") or dev.get("explanation") or claim_text, rewrite_hint=rewrite_hint,
                )
                en_revised_fb = simple_llm_call(client, state, consecutive_errors, call_log,
                                                      f"{label_prefix}_j1_en_fallback_edit",
                                                      E2_GENERIC_DEVELOPER_MSG, prompt_en, model=MODEL)
                if en_revised_fb is not None:
                    updated_en = en_full.replace(en_target, en_revised_fb, 1)
                    method = "j1_failed+ja_fulltext_fallback+en_local_edit"
                    en_after_fragment = en_revised_fb
                else:
                    updated_en = en_full
                    method = "j1_failed+ja_fulltext_fallback+en_local_edit_api_failure"
            else:
                prompt_en_fb = FULL_TEXT_FALLBACK_PROMPT_TEMPLATE.format(
                    ledger_text=fixture["ledger_text"], full_text=en_full, target_sentence=claim_text,
                    issue=dev.get("issue") or dev.get("explanation") or claim_text, rewrite_hint=rewrite_hint,
                )
                en_fallback = simple_llm_call(client, state, consecutive_errors, call_log,
                                                    f"{label_prefix}_j1_en_fulltext_fallback",
                                                    FULL_TEXT_FALLBACK_DEVELOPER_MSG, prompt_en_fb, model=MODEL)
                if en_fallback:
                    updated_en = en_fallback
                    method = "j1_failed+ja_fulltext_fallback+en_fulltext_fallback"
                else:
                    updated_en = en_full
                    method = "j1_failed+ja_fulltext_fallback+en_fulltext_fallback_api_failure"
            guard_ok = ja_guard_ok
        else:
            updated_ja = ja_full
            updated_en = en_full
            method = "j1_failed+ja_fulltext_fallback_api_failure"
            guard_ok = False
        # 委任_16 B-1: ①③④のladderがguardを満たせず(またはそもそも両言語の
        # 対象文が特定できず)全文フォールバックへ落ちたケースは、水準⑥
        # (既存FULL_TEXT_FALLBACKに相当)としてladder_level_usedへ記録する
        # (guard_okがTrueの場合のみ、実際に解消できた水準として記録する)。
        if guard_ok:
            ladder_level_used = "6_full_article"

    return {"updated_en_text": updated_en, "updated_ja_text": updated_ja, "method": method, "guard_ok": guard_ok,
            "en_target": en_target, "ja_target": ja_target,
            "before_fragment": en_target, "after_fragment": en_after_fragment,
            "ladder_level_used": ladder_level_used, "target_not_locatable": False}


def run_stage3_for_claim(client, state, consecutive_errors, call_log, label_prefix, fixture,
                          current_en_text: str, current_ja_text: str | None, claim_rec: dict) -> dict:
    """1 claim分のRewriteを実行し、更新後の(en_text, ja_text)を返す。"""
    use_pairing = (
        claim_rec.get("origin") == "ja_source"
        and current_ja_text is not None
        and fixture.get("source_article_text") is not None
    )
    working_fixture = dict(fixture)
    working_fixture["article_text"] = current_en_text
    if current_ja_text is not None:
        working_fixture["source_article_text"] = current_ja_text

    if use_pairing:
        res = paired_rewrite(client, state, consecutive_errors, call_log, label_prefix, working_fixture, claim_rec)
        # 委任_16 B-1: paired J-1もsingle_text_rewriteと同じ①③④ladderを
        # 適用するようpaired_rewrite自体を再設計した(§5-7既知の限界を解消、
        # 詳細design書§5-8)。ladder_level_usedはpaired_rewriteが実際に
        # 解消できた水準をそのまま返す(Noneの場合は全水準とも解消できず
        # 未解決、既存集計側のunresolved_or_api_failureへフォールバック)。
        return {"mechanism": "paired_ja_en(J-1)", "en_text": res["updated_en_text"],
                "ja_text": res["updated_ja_text"], "method": res["method"], "guard_ok": res["guard_ok"],
                "before_fragment": res.get("before_fragment"), "after_fragment": res.get("after_fragment"),
                "ladder_level_used": res.get("ladder_level_used"),
                "target_not_locatable": res.get("target_not_locatable", False),
                # 委任_23 B-2: ⑥ feature flag(既定OFF)時、①〜④/delete全段で
                # guardが失敗した場合に立つ(呼び出し側run_instanceがSTAGE4へ回す)。
                "ladder_exhausted_without_full_rewrite": res.get(
                    "ladder_exhausted_without_full_rewrite", False)}
    else:
        res = single_text_rewrite(client, state, consecutive_errors, call_log, label_prefix, working_fixture,
                                   "article_text", claim_rec)
        return {"mechanism": "single_text_local(E-2/delete-generic)", "en_text": res["updated_text"],
                "ja_text": current_ja_text, "method": res["method"], "guard_ok": res["guard_ok"],
                "before_fragment": res.get("before_fragment"), "after_fragment": res.get("after_fragment"),
                "target_not_locatable": res.get("target_not_locatable", False),
                "ladder_level_used": res.get("ladder_level_used"),
                "ladder_exhausted_without_full_rewrite": res.get(
                    "ladder_exhausted_without_full_rewrite", False)}


# ============================================================
# 委任_18 2-4(局所QA統合、2026-09-30ユーザー新方針item1/7/9): 基本形
# 「最小修正 → 修正文+前後文確認 → 問題解消・周辺影響なしなら終了」を
# 実装する。Production局所QA(`er010_ledger_local_rewrite_09.
# extract_point_context`[L97-114]・`classify_deviation_role`[L211-235]・
# `evaluate_target_sentence_status`[L238-273]、いずれも決定論の純粋関数、
# 既に`import er010_ledger_local_rewrite_09 as er010`済みのため read-only
# importで再利用しProduction自体は一切変更しない)の設計思想(対象文単位の
# window判定)を踏襲し、全文Recheck(`run_recheck`/`run_recheck_confirm`)の
# 代わりに「修正文+前後1文」だけを見る軽量な1 callをまず試す。
#
# 全文Recheckを残す条件(§1-4-5の実測: 55 instance-run中4件[うち3件
# Safety群]で全文Recheckがcycle1のRewrite対象とは別のLedger fact由来の
# 新規BLOCKING claimを検出した実績があるため、これらの条件に該当する
# cycleは局所QAで代替せず既存の全文Recheckをそのまま使う、既存の安全側
# 挙動を変えない):
#   (a) このcycleで段落単位[4_paragraph]・全体[6_full_article]・削除
#       [0_delete]のいずれかのladder水準が使われた(局所QAの前後1文
#       windowでは変更範囲を捉えきれない)。
#   (b) このcycleで2件以上のclaimをRewriteした(claim間の相互作用を
#       局所QAのwindow単体では検出できない)。
#   (c) paired(J-1、JA・EN双方変更)が使われた(§1-4-5の対象外条件と
#       同様、複雑度が高いため既存のJA/EN双方の全文Recheckを維持)。
#   (d) deterministic floor由来のclaim(floor_reason起動)が含まれる
#       (Safety側安全装置、既存のfail-closed全文確認を弱めない)。
#   (e) Safety fixture(instance_idが"safety_"始まり、Safety-critical
#       10 claim/Safety 12を含む可能性がある群)。
# 上記いずれにも該当しない場合のみ局所QA 1 callを試し、
# 「元問題解消かつ新規逸脱なしかつ隣接文への影響なし」なら全文Recheckを
# 省略してcycleを解決とする(既存のcite-or-release confirm[委任_13]は
# 局所QAの出力[prior_issue_resolved]へ統合され、この経路では別途呼ばない
# ため重複callが解消される)。条件に該当する場合、または局所QAが問題を
# 検出した場合は、既存の全文Recheckフロー(下記、無変更)へそのまま
# フォールバックする(安全側、既存の正しい経路を壊さない)。
# ============================================================
LOCAL_QA_ESCALATION_LADDER_LEVELS = frozenset({"4_paragraph", "6_full_article", "0_delete", None})


def full_recheck_required(rewrite_records: list, blocking_claims: list, instance_id: str,
                           repeat_fact_ids: frozenset = frozenset(), ja_guard_ok: bool | None = None,
                           ja_equivalence_verdict: str | None = None) -> tuple:
    """委任_18 2-4/委任_19 A-1/委任_20 W3是正: 全文Recheckを残す条件
    (a)〜(h)を判定する(¥0、決定論)。Trueの場合は既存の全文Recheckフロー
    をそのまま使う(理由のlistも返し、cycle_recordへEvidenceとして記録する)。

    委任_20 W3(Opus L2レビュー#4 Q1(b)推奨、前提: W1でJA fail-openガード
    [ja_fail_open_guard]とja_en_equivalence_verdictのgating化が既に導入
    済み): (c)を「paired かつ(ladder≥④ or JA ガード不通過)」へ縮小する。
    (a)は既にrewrite_records全件[paired含む]についてladder≥④を判定して
    いるため、狭めた(c)が追加で捕捉するのは「paired・ladder①〜③・かつ
    JAガード不通過」の場合のみ(rep10 hormuz cycle2は実際にはladder=
    4_paragraphだったため(a)で捕捉されるが、ladder①〜③でも同型の欠陥が
    起きた場合に備える保守的な追加条件)。(b)
    multiple_claims_rewritten_same_cycleは実証例なし(disclosure §1-4-5の
    meta_run03_standard sample2は(d)floorでも捕捉される)だが、保守側で
    維持する(削除の実証的根拠がないため)。(e)safety_fixtureは
    instance_idの命名規約(Trial fixture限定)に依存しており、Production
    記事には該当する信号がない。Production配線時は「Ledger factが
    Safety-critical指定」等の実信号へ置換が必須(Trial限定条件、
    Productionへ外挿不可)。(g)(h)は本委任で新設。

    委任_19 A-1: 委任文は「paired J-1はラダー①〜③の局所変更なら条件から
    外す」ことを求めていたが、本委任のrep10実測前調査(rep9
    `hormuz_run03_standard`sample1、`cycle_limit_exhausted_after_recheck`)
    により、paired J-1(origin=ja_source、JA→EN翻訳由来)のclaimはHormuz/
    Meta系記事で見出し・one-line要約・本文の複数箇所に同一fact_idの主張が
    分散して現れる実例が確認された。局所QA fastpathは対象文±1文の
    windowしか見ないため、「記事の別箇所に同じfactの問題が初めて存在する」
    ことを構造的に検出できない。paired J-1のcycle1(このinstanceで初めて
    その問題が検出された回)でfastpathを許すと、全文Recheckが従来
    発見していた「cycle2以降で別箇所から同一fact_idが再検出される」という
    事実そのものが二度と分からなくなり(全文Recheckを一度も経由しない
    まま`RESOLVED_REWRITE`として静かに完了し、Rewriteされなかった見出し等
    がそのまま残る)、既存の安全な挙動(cycleを重ねた末に正しくSTAGE4へ
    到達する)より悪化する。この具体的な反証により、(c)「paired J-1は
    常に全文Recheckを要する」は**ラダー水準に関わらず維持する**(狭める
    と4件[disclosure §1-4-5]どころか新規のhormuz実例を取りこぼすリスクが
    あるため)。代わりに、同種のリスク(single_text_rewrite側でも理論上は
    起こり得る)への一般的な安全網として(f)を新設する。"""
    reasons = []
    if any((r.get("ladder_level_used") in LOCAL_QA_ESCALATION_LADDER_LEVELS) for r in rewrite_records):
        reasons.append("paragraph_or_full_or_delete_rewrite")
    if len(rewrite_records) > 1:
        reasons.append("multiple_claims_rewritten_same_cycle")
    # 委任_20 W3: (c)を「paired かつ(ladder≥④ or JAガード不通過)」へ縮小。
    paired_records = [r for r in rewrite_records if r.get("mechanism", "").startswith("paired")]
    if paired_records:
        paired_high_ladder = any(
            r.get("ladder_level_used") in LOCAL_QA_ESCALATION_LADDER_LEVELS for r in paired_records)
        if paired_high_ladder or ja_guard_ok is False:
            reasons.append("both_ja_en_changed(paired_j1)")
    if any(c.get("floor_reason") for c in blocking_claims):
        reasons.append("deterministic_floor_claim")
    if instance_id.startswith("safety_"):
        reasons.append("safety_fixture")
    # 委任_20 W3新設(g): title/hook/in_one_line(前後1文が成立しない
    # section)を含む場合、局所QAのwindow概念が成立しないため全文Recheckへ
    # 回す。
    if any((c.get("section_type") in HOOK_SECTION_TYPES) for c in blocking_claims):
        reasons.append("short_section_no_window(title_hook_in_one_line)")
    # 委任_20 W3新設(h): JA/EN等価チェックが非PASS(FAIL/REVIEW_REQUIRED)
    # の場合、全文Recheckを維持する(rep10で唯一のFAILが実際のJA破損と
    # 一致した実測を踏まえ、測定専用から昇格)。
    if ja_equivalence_verdict not in (None, "PASS"):
        reasons.append("ja_en_equivalence_not_pass")
    # 委任_19 A-1新設(f): このcycleのBLOCKING claimのfact_idが、この
    # instanceの過去cycleで一度でもBLOCKINGとして検出されたfact_idと
    # 一致する場合(同一claim完全一致は既存`matched_records`が即Stage4で
    # 別途捕捉するため、ここに到達するのは「同一fact_id・別文言」の
    # ケースのみ)、fastpathを許さず全文Recheckへ回す(hormuz型の多箇所
    # 分散を検出する既存の唯一の手段が全文Recheckであるため)。
    current_fact_ids = {(c.get("dev", {}).get("related_fact_id") or "").strip() for c in blocking_claims}
    if current_fact_ids & set(repeat_fact_ids):
        reasons.append("same_fact_id_reappeared_across_cycles")
    return bool(reasons), reasons


def resolve_ja_ok_after_equivalence_gating(ja_ok: bool, ja_equivalence_verdict: str | None,
                                            current_ja_text: str | None) -> dict:
    """委任_22 A-1是正(rep12 `bgroup_B3`実データで判明したKPI後退): 全文
    Recheckが実際に判定したja_ok(引数、`ja_recheck_parsed`由来)を、JA/EN
    等価チェックの結果(`ja_en_equivalence_verdict`)でさらにgatingするか
    どうかを決定する(¥0、決定論)。

    委任_20 W1(ii)は「FAIL/REVIEW_REQUIREDならja_okを無条件でFalseへ倒す」
    方式だった。`bgroup_B3`のfixtureは`source_article_text`(「JA」側)が
    実際には英語であり(委任_21 A-1で`ja_fail_open_guard`について特定した
    のと同じ構造的限界)、JA↔EN等価チェック自体が両者を比較できず
    `REVIEW_REQUIRED`を返す。実際の全文Recheckは英語版・JA版とも
    `LEDGER_COMPLIANT`かつ`all_prior_issues_resolved=True`だったにも
    関わらず、無条件gatingがja_okを強制Falseへ倒し続けた結果、次cycleで
    blocking_count=0(新規逸脱なし)でも`ja_pending_deviation`が解消されず
    `STAGE4_ESCALATION(ja_deviation_unresolved)`へ強制到達していた
    (2/2、rep12)。

    是正後の方式: `FAIL`(等価チェックが実際に不一致を検出した場合)は
    従来どおりja_okをFalseへ倒す(次段のRewriteへ、最終的にSTAGE4)。
    `REVIEW_REQUIRED`かつ`is_predominantly_ja`で判定したJA側言語が非JA
    (indeterminate、等価チェック自体が判定不能)の場合は、ja_okを強制せず
    全文Recheckの実際の判定をそのまま使う(STAGE4直行を強制しない、
    `full_recheck_required`の(h)条件により全文Recheck自体は既に維持
    されているため安全側は保たれる)。`REVIEW_REQUIRED`かつJA側言語が
    正常(判定可能)の場合は従来どおりgatingする(理由を記録)。

    委任_23 A-2是正(iter7実データで判明した新たなKPI後退、
    `hormuz_run03_standard` real_run Escalation 2/10のうち1件の真因、
    REPORT§23 A参照): 上記「JA側言語が正常な場合は従来どおりgating」は、
    `ja_ok`(引数、この全文RecheckがEN/JA双方ともLEDGER_COMPLIANTかつ
    all_prior_issues_resolved=Trueと**既に確認した**結果)がTrueの場合も
    無条件でFalseへ倒しており、`full_recheck_required`の(h)条件により
    このcycleで**実際に実行された**全文Recheckの確定的な判定結果を、
    より弱い根拠(`ja_en_equivalence_verdict`はその作成時[委任_11]の
    docstringで「flow制御には使わない、測定・報告専用」と明記されていた
    check。委任_20 W1(ii)は`FAIL`の実測[rep10、JA破損と一致]を根拠に
    gatingへ昇格したが、rep10のja_recheck自体も独立に`LEDGER_DEVIATION`
    だったため[§6-7]、`ja_ok`が既にTrueの状況でこの追加gatingが実際に
    真の見逃しを捕捉した実測は一度も存在しない)で上書きしてしまう
    構造的な過剰保守だった。是正: `REVIEW_REQUIRED`かつJA側言語が正常
    (判定可能)でも、`ja_ok`(入力、全文Recheckの確定判定)が既にTrueの
    場合はgatingしない(信頼できる独立確認[EN/JA双方のLedger Recheck]が
    既に得られているため)。`ja_ok`が既にFalseの場合はgating自体が
    no-op(元々False)であり挙動は変わらない。`FAIL`分岐は変更しない
    (rep10実測の唯一の根拠がFAILであり安全側を維持する)。JA fail-open
    ガード(§6-7(iii)、本関数とは独立に`run_instance`側で適用)は本是正
    後も無変更のまま機能し続けるため、rep10型の実際のJA破損(指摘文が
    逐語残存/段落外JA文の理由なき消失)は引き続き検出される(二重の
    安全網のうち、実測で価値が一度も確認されなかった層のみを縮小する)。"""
    result = {"ja_ok": ja_ok, "blocked_by_equivalence": False, "lang_indeterminate": None,
              "not_gated_indeterminate_lang": False, "not_gated_already_confirmed_resolved": False}
    if ja_equivalence_verdict == "FAIL":
        if ja_ok:
            result["ja_ok"] = False
            result["blocked_by_equivalence"] = True
    elif ja_equivalence_verdict == "REVIEW_REQUIRED":
        lang_indeterminate = (not is_predominantly_ja(current_ja_text)) if current_ja_text else None
        result["lang_indeterminate"] = lang_indeterminate
        if lang_indeterminate:
            result["not_gated_indeterminate_lang"] = True
        elif ja_ok:
            # 委任_23 A-2: 全文Recheckが既にEN/JA双方の解消を確認済み
            # (ja_ok=True入力)の場合は、根拠の弱いequivalence REVIEW_
            # REQUIREDだけでこれを覆さない(上記docstring参照)。
            result["not_gated_already_confirmed_resolved"] = True
    return result


def ja_fail_open_guard(ja_text_before: str, ja_text_after: str, blocking_claims: list) -> dict:
    """委任_20 W1(iii)(Opus L2レビュー#4 §0/Q1(b)提案): ¥0・決定論の
    JA fail-openガード。paired rewrite(J-1)でJA本文がこのcycleで変化した
    場合に、(i)指摘されたBLOCKING claimのJA文(rewrite_hint中の引用断片、
    既存`extract_quoted_fragment`と同じ抽出方法。paired_rewriteの
    JA対象文特定[第一キー]と同一の考え方を流用する)がRewrite後も逐語で
    残っていないか、(ii)そのJA文を含む段落ブロック(既存
    `locate_paragraph_block`)の外側にあった他のJA文が理由なく消えて
    いないか、を機械的に判定する(追加API callなし)。

    rep10 `hormuz_run03_standard` sample1 cycle2の実データ(指摘JA文が
    一字一句残存したまま、別段落の"報道時点では約2.6%高..."が消失し
    `RESOLVED_REWRITE_THEN_DOWNGRADE`として誤って完了した事故)を再現
    できることをunittestで確認する(fixtureとして使用)。

    rewrite_hintから引用断片を抽出できないclaim(underspecified rewrite_
    hint)は対象外とする(このガードを理由に既存動作を不必要に広げない、
    保守側で見送る)。

    委任_21 A-1是正(rep11 `bgroup_B3`実データで判明したKPI後退): 従来は
    無条件で`split_ja_sentences`(句点。！？のみ)を使っていたため、
    `source_article_text`(本来JAのはずのfixtureフィールド)が実際には
    英語だった場合に句点分割が機能せず全文が1文として扱われ、些細な変更
    でも「1文丸ごと消失」という粗い誤検知を生んでいた(rep11で2/8 sample
    がこの誤発火によりSTAGE4へ回りKPI後退)。`is_predominantly_ja`で
    ja_text_before/after双方の言語を判定し、JA主体なら`split_ja_
    sentences`、非JA(英語等)主体なら既存EN分割器`split_sentences_
    generic`(.!?を含む)を使う。いずれの分割器でも1文以下にしか分割
    できない場合(句読点が実質存在しない等、判定不能)は、違反判定を行わず
    `indeterminate=True`を返す(ガード不発火=安全側だが、呼び出し側は
    これを理由に全文Recheck条件へ倒す。STAGE4への直行はしない)。"""
    if ja_text_before == ja_text_after:
        return {"ok": True, "violations": [], "checked": False, "indeterminate": False}
    lang_ok = is_predominantly_ja(ja_text_before) and is_predominantly_ja(ja_text_after)
    splitter = split_ja_sentences if lang_ok else split_sentences_generic
    sentences_before = splitter(ja_text_before)
    sentences_after_set = set(splitter(ja_text_after))
    indeterminate = len(sentences_before) <= 1
    violations = []
    checked_any = False
    if not indeterminate:
        for c in blocking_claims:
            hint = c.get("rewrite_hint") or ""
            flagged = extract_quoted_fragment_present_in(hint, ja_text_before)
            if not flagged:
                continue
            checked_any = True
            fact_id = (c.get("dev", {}) or {}).get("related_fact_id") or c.get("related_fact_id")
            # (i) 指摘されたJA文がRewrite後も逐語で残っていないか
            if flagged in ja_text_after:
                violations.append({"type": "flagged_ja_sentence_unchanged", "sentence": flagged,
                                    "related_fact_id": fact_id})
            # (ii) 対象段落(既存locate_paragraph_blockで特定)外のJA文が消失していないか
            block, _ = locate_paragraph_block(flagged, ja_text_before)
            window = block if block else flagged
            for s in sentences_before:
                if s in window:
                    continue
                if s not in sentences_after_set:
                    violations.append({"type": "unexplained_ja_sentence_deletion", "sentence": s,
                                        "related_fact_id": fact_id})
    return {"ok": not violations, "violations": violations, "checked": checked_any,
            "indeterminate": indeterminate}


def find_sentence_context(full_text: str, needle: str) -> tuple:
    """needle(Rewrite後の対象文、after_fragment)がfull_text中のどの文に
    対応するかを`split_sentences_generic`(既存、¥0)で特定し、前後各1文を
    返す(見つからなければ(None, None, None))。

    委任_19 A-1是正: rep9実測(REPORT§18)でlocal QA fastpathの3試行中2件が
    `revised_sentence_not_locatable_in_context`で失敗していた原因を調査した
    結果、`locate_target`(→`locate_best_sentence`)の文分割
    (`re.split(r"(?<=[。.!?])", full_text)`、改行を跨いで結合しない)と、
    本関数が使う`split_sentences_generic`の文分割(見出し行除外+改行を
    スペースで結合してから分割)が異なる方式であるため、Rewrite対象として
    特定された`target_sentence`の境界と、Rewrite後にfind_sentence_contextが
    再分割した際の文境界が完全には一致しないケースがあることが分かった
    (根本原因の完全な再現はできなかったが、分割方式の不一致が濃厚)。
    exact substring不一致時、SequenceMatcher近似(既存`locate_best_sentence`
    と同型、閾値0.85)へfail-closedでfallbackする(十分高い一致度が
    得られない場合は従来どおりNoneのまま、全文Recheckへフォールバックする
    安全側動作は変えない)。

    委任_21 A-2是正(rep11実データ`meta_run03_standard` sample1 cycle1で
    判明した真因): `needle`(after_fragment)は`locate_target`の第一キー
    (`extract_quoted_fragment`によるrewrite_hint中の引用断片)がそもそも
    複数文にまたがる場合(実例: rewrite_hintの引用が「Also, some calls
    needed user information to continue. That information might
    accidentally be shared...」の2文だった)、Rewrite後のneedleも同じく
    2文にまたがる。旧実装は`split_sentences_generic`が返す単一文の要素
    each `s`に対して`needle_s in s`および1文単位のSequenceMatcherしか
    試みておらず、needleがどの単一文よりも長い(2文分)ため両方とも
    一致せず`revised_sentence_not_locatable_in_context`で毎回skipして
    いた(局所QA fastpathがcallに一度も到達しない主因)。本是正は、
    needle自体を同じ分割器で分割した文数kを求め、k>1の場合は連続する
    k文の結合ウィンドウに対してexact containment→SequenceMatcherの順で
    追加照合する(k=1の場合の既存動作は変更しない、fail-closedの閾値
    0.85も維持)。"""
    if not needle or not needle.strip():
        return None, None, None
    needle_s = needle.strip()
    sentences = split_sentences_generic(full_text)
    for i, s in enumerate(sentences):
        if needle_s in s:
            before_ctx = sentences[i - 1] if i > 0 else ""
            after_ctx = sentences[i + 1] if i + 1 < len(sentences) else ""
            return before_ctx, s, after_ctx
    needle_sentence_count = len(split_sentences_generic(needle_s)) or 1
    if needle_sentence_count > 1:
        k = needle_sentence_count
        for i in range(0, len(sentences) - k + 1):
            window = " ".join(sentences[i:i + k])
            if needle_s in window or window in needle_s:
                before_ctx = sentences[i - 1] if i > 0 else ""
                after_ctx = sentences[i + k] if i + k < len(sentences) else ""
                return before_ctx, window, after_ctx
        best_i, best_ratio = None, 0.0
        for i in range(0, len(sentences) - k + 1):
            window = " ".join(sentences[i:i + k])
            ratio = difflib.SequenceMatcher(None, needle_s, window).ratio()
            if ratio > best_ratio:
                best_ratio, best_i = ratio, i
        if best_i is not None and best_ratio >= 0.85:
            before_ctx = sentences[best_i - 1] if best_i > 0 else ""
            after_ctx = sentences[best_i + k] if best_i + k < len(sentences) else ""
            return before_ctx, " ".join(sentences[best_i:best_i + k]), after_ctx
    best_i, best_ratio = None, 0.0
    for i, s in enumerate(sentences):
        ratio = difflib.SequenceMatcher(None, needle_s, s).ratio()
        if ratio > best_ratio:
            best_ratio, best_i = ratio, i
    if best_i is not None and best_ratio >= 0.85:
        before_ctx = sentences[best_i - 1] if best_i > 0 else ""
        after_ctx = sentences[best_i + 1] if best_i + 1 < len(sentences) else ""
        return before_ctx, sentences[best_i], after_ctx
    return None, None, None


LOCAL_QA_DEVELOPER_MSG = (
    "You are performing a local QA check after a minimal, local edit to a news article, using the same "
    "fact-verification standard as a Ledger Deviation Checker. You are given ONLY the edited sentence and "
    "its immediate neighbors (not the full article) plus the specific Verified Fact Ledger entries relevant "
    "to this edit. Judge strictly whether the prior issue is resolved, whether the revised sentence itself "
    "introduces any NEW deviation from the Ledger, and whether the (unchanged) neighboring sentences are "
    "still consistent given the edit."
)
LOCAL_QA_PROMPT_TEMPLATE = """[Verified Fact Ledger entries relevant to this edit]
{ledger_excerpt}

[Prior issue that was flagged before this edit]
{prior_issue}

[Sentence immediately before the edited sentence (unchanged context)]
{before_ctx}

[Revised sentence]
{revised_sentence}

[Sentence immediately after the edited sentence (unchanged context)]
{after_ctx}

Answer strict JSON with these fields:
- prior_issue_resolved (boolean): does the revised sentence resolve the prior issue above?
- new_deviation_in_revised_sentence (boolean): does the revised sentence itself now contain a NEW \
deviation from the Ledger entries above (a different fact error, not the original issue)?
- new_deviation_explanation (string): if new_deviation_in_revised_sentence is true, explain briefly; \
otherwise empty string.
- adjacent_sentence_affected (boolean): given the edit, does either neighboring sentence now read as \
inconsistent, contradictory, or factually orphaned (e.g. refers back to something the edit removed)?
- adjacent_sentence_explanation (string): if adjacent_sentence_affected is true, explain briefly; \
otherwise empty string."""

LOCAL_QA_JSON_SCHEMA = {
    "name": "open233_self_recovery_local_qa",
    "schema": {
        "type": "object",
        "properties": {
            "prior_issue_resolved": {"type": "boolean"},
            "new_deviation_in_revised_sentence": {"type": "boolean"},
            "new_deviation_explanation": {"type": "string"},
            "adjacent_sentence_affected": {"type": "boolean"},
            "adjacent_sentence_explanation": {"type": "string"},
        },
        "required": ["prior_issue_resolved", "new_deviation_in_revised_sentence",
                     "new_deviation_explanation", "adjacent_sentence_affected",
                     "adjacent_sentence_explanation"],
        "additionalProperties": False,
    },
    "strict": True,
}


def build_ledger_excerpt(ledger_text: str, fact_id: str) -> str:
    """委任_18 2-4: 局所QAの入力を「当該Ledger fact群(関連factのみ)」に
    絞る(¥0、既存precheck.parse_ledger_text[決定論]を再利用)。fact_idが
    Ledgerに実在しない場合はledger_text全体へ安全側fallbackする。"""
    if not fact_id:
        return ledger_text
    facts = precheck.parse_ledger_text(ledger_text)
    fact = next((f for f in facts if f.get("fact_id") == fact_id), None)
    if fact is None:
        return ledger_text
    lines = [f"fact_id: {fact_id}"]
    for key in ("claim", "numeric_value", "date_or_period"):
        if fact.get(key):
            lines.append(f"{key}: {fact[key]}")
    return "\n".join(lines)


def run_local_qa(client, state, consecutive_errors, call_log, label, ledger_excerpt: str,
                  prior_issue: str, before_ctx: str, revised_sentence: str, after_ctx: str) -> dict:
    check_budget(state)
    prompt = LOCAL_QA_PROMPT_TEMPLATE.format(
        ledger_excerpt=ledger_excerpt, prior_issue=prior_issue or "",
        before_ctx=before_ctx or "", revised_sentence=revised_sentence, after_ctx=after_ctx or "",
    )
    last_err = None
    response = None
    t0 = time.time()
    for _ in range(1 + MAX_RETRIES_PER_CALL):
        try:
            response = client.responses.create(
                model=MODEL, reasoning={"effort": vfl01.REASONING_EFFORT},
                text={"format": {"type": "json_schema", **LOCAL_QA_JSON_SCHEMA}},
                input=[{"role": "developer", "content": LOCAL_QA_DEVELOPER_MSG},
                       {"role": "user", "content": prompt}],
            )
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0)
    elapsed = round(time.time() - t0, 3)
    if response is None:
        call_log.append({"label": label, "recovery_stage": "local_qa", "error": last_err})
        record_call(state, consecutive_errors, label, 0.0, False, "local_qa")
        # fail-closed: API失敗は「未解消」扱い(呼び出し側が全文Recheckへ
        # フォールバックする、§6-1 A7と同一原則)。
        return {"prior_issue_resolved": False, "new_deviation_in_revised_sentence": True,
                "new_deviation_explanation": "local_qa_api_failure", "adjacent_sentence_affected": False,
                "adjacent_sentence_explanation": "", "_api_failure": True}
    parsed = json.loads(response.output_text)
    usage = s2p._extract_usage(response)
    cost = round(s2p.official_cost_jpy(usage), 4)
    call_log.append({"label": label, "recovery_stage": "local_qa", "cost_jpy": cost, "usage": usage,
                      "elapsed_seconds": elapsed, "prompt_sha256": s2p.sha256_text(prompt),
                      "prior_issue_resolved": parsed.get("prior_issue_resolved"),
                      "new_deviation_in_revised_sentence": parsed.get("new_deviation_in_revised_sentence"),
                      "adjacent_sentence_affected": parsed.get("adjacent_sentence_affected")})
    record_call(state, consecutive_errors, label, cost, True, "local_qa", usage)
    parsed["_api_failure"] = False
    return parsed


def run_local_qa_fastpath(client, state, consecutive_errors, call_log, label_prefix, fixture,
                           current_en_text: str, blocking_claims: list, before_after_pairs: list) -> dict:
    """委任_18 2-4: cycle内の全claimについて局所QAを実行し、全件が
    「解消・新規逸脱なし・隣接文影響なし」ならfastpath成功(全文Recheckを
    省略)。1件でも問題があれば{"success": False}を返し、呼び出し側は
    既存の全文Recheckフローへフォールバックする(呼び出し元がclaim毎の
    before_after_pairsのafter[Noneでない]を持つ前提、full_recheck_required
    がFalseの場合のみ呼ばれるため、対象claimは全て単一文水準の局所編集で
    after_fragmentが判明している)。"""
    results = []
    for claim, pair in zip(blocking_claims, before_after_pairs):
        after_fragment = pair.get("after")
        if not after_fragment:
            results.append({"claim_identity": claim_identity(claim["dev"]), "prior_issue_resolved": False,
                             "new_deviation_in_revised_sentence": False, "adjacent_sentence_affected": False,
                             "skipped_reason": "after_fragment_unknown"})
            continue
        before_ctx, located_sentence, after_ctx = find_sentence_context(current_en_text, after_fragment)
        if located_sentence is None:
            results.append({"claim_identity": claim_identity(claim["dev"]), "prior_issue_resolved": False,
                             "new_deviation_in_revised_sentence": False, "adjacent_sentence_affected": False,
                             "skipped_reason": "revised_sentence_not_locatable_in_context"})
            continue
        ledger_excerpt = build_ledger_excerpt(fixture["ledger_text"], claim["dev"].get("related_fact_id", ""))
        prior_issue = claim["dev"].get("issue") or claim["dev"].get("explanation") or claim["claim_text"]
        qa = run_local_qa(client, state, consecutive_errors, call_log,
                           f"{label_prefix}_local_qa_{claim_identity(claim['dev'])[:20]}",
                           ledger_excerpt, prior_issue, before_ctx, located_sentence, after_ctx)
        qa["claim_identity"] = claim_identity(claim["dev"])
        results.append(qa)
    success = bool(results) and all(
        r.get("prior_issue_resolved") and not r.get("new_deviation_in_revised_sentence")
        and not r.get("adjacent_sentence_affected") and not r.get("skipped_reason")
        for r in results
    )
    return {"success": success, "results": results}


# ------------------------------------------------------------
# instance構築(委任_09対象: Hormuz run01/02/03、Meta run03、B群4、
# negative候補7、Safety群12)
# ------------------------------------------------------------
SAFETY_STAGE1_DIR = "er051_output/open233_checker_trial_01/trial_02/step1"
BGROUP_STAGE1_DIR = "er051_output/open233_checker_trial_01/trial_02/step2"
STEP3_STAGE1_DIR = "er051_output/open233_checker_trial_01/trial_02/step3"
NEG_STAGE1_DIR = "er052_output/open233_self_recovery_phase1_step3_stage1_compare_01/c_negative"


def build_target_instances() -> list:
    instances = []

    # --- Safety群12(er009 9種+A2A3+A4+A5) ---
    for fx in g6.step1_fixtures():
        instances.append({
            "instance_id": f"safety_{fx['id']}", "group": "safety", "fixture": fx,
            "stage1_mode": "reuse", "stage1_source": f"{SAFETY_STAGE1_DIR}/{fx['id']}/V4A/run_1.json",
            "expected_group_label": "BLOCKING(Safety、§7-1)",
        })

    # --- B群4(B1/B2_hormuz/B3/B4) ---
    for fx in g6.step2_fixtures():
        if fx["id"] == "Meta_run03_standard":
            continue
        instances.append({
            "instance_id": f"bgroup_{fx['id']}", "group": "b_group", "fixture": fx,
            "stage1_mode": "reuse", "stage1_source": f"{BGROUP_STAGE1_DIR}/{fx['id']}/V4A/run_1.json",
            "expected_group_label": "claim単位混在(§7-0)",
            # B2_hormuz/B3は真のProduction V0では検出済みのReal-but-fixable
            # 群だが、V4A単発実行では非検出(recall欠落、§10/§14既知の限界)
            # になり得る。その場合はfixture自体のbaseline_parsed(V0、既に
            # MAJOR検出済み)へ代替してStage2/3の経路自体は検証する
            # (代替した事実は結果へ明記し、Stage1 recall miss発生として
            # 別途報告する。V4Aが実際に検出したと偽装しない)。
            "substitute_baseline_on_stage1_miss": fx["id"] in ("B2_hormuz", "B3"),
            # S1-U variant対象(委任_10、§3-1): B2_hormuz/B3はStage1(V4A)
            # recall miss実例(§10/§14既知の限界)であり、S1-U(S1-D union)が
            # これを追加検出できるかを実測する。
            "s1u_eligible": fx["id"] in ("B2_hormuz", "B3"),
        })

    # --- Meta run_03 Standard(既存V4A再利用) ---
    meta_std = next(fx for fx in g6.step2_fixtures() if fx["id"] == "Meta_run03_standard")
    instances.append({
        "instance_id": "meta_run03_standard", "group": "meta", "fixture": meta_std,
        "stage1_mode": "reuse", "stage1_source": f"{BGROUP_STAGE1_DIR}/Meta_run03_standard/V4A/run_1.json",
        "expected_group_label": "BLOCKING→Rewrite→PASS(§7-1、現行は既存retry1回で通過)",
        "s1u_eligible": True,
    })

    # --- Meta run_03 Advanced(V4A未実測、新規Stage1call) ---
    meta_adv = g6.load_audit_fixture(
        "meta_run03_advanced",
        "er019_output/family_x_refresh_e2e_01/meta/run_03/b1b/audit/deviation_checks/advanced_attempt1.json",
        "現行Production実測=LEDGER_COMPLIANT(V0)。V4Aでの再判定は本委任で新規実行。",
    )
    instances.append({
        "instance_id": "meta_run03_advanced", "group": "meta", "fixture": meta_adv,
        "stage1_mode": "fresh", "stage1_source": None,
        "expected_group_label": "Normal群(§7-5、Stage1のみでACCEPTABLE到達が期待)",
        "s1u_eligible": True,
    })

    # --- Hormuz run_03 Advanced/Standard(既存V4A再利用) ---
    for fx in g6.step3_fixtures():
        if fx["id"] not in ("hormuz_run03_advanced", "hormuz_run03_standard"):
            continue
        label = "Normal群(§7-5)" if fx["id"] == "hormuz_run03_advanced" else "BLOCKING(Safety群、§7-1、narrow_scope)"
        instances.append({
            "instance_id": fx["id"], "group": "hormuz", "fixture": fx,
            "stage1_mode": "reuse", "stage1_source": f"{STEP3_STAGE1_DIR}/{fx['id']}/V4A/run_1.json",
            "expected_group_label": label, "s1u_eligible": True,
        })

    # --- Hormuz run_01/run_02 Advanced(現行Production STOP実例、V4A未実測) ---
    for run_id, path in [
        ("hormuz_run01_advanced",
         "er019_output/family_x_refresh_e2e_01/hormuz/run_01/b1b/audit/deviation_checks/advanced_attempt1.json"),
        ("hormuz_run02_advanced",
         "er019_output/family_x_refresh_e2e_01/hormuz/run_02/b1b/audit/deviation_checks/advanced_attempt1.json"),
    ]:
        fx = g6.load_audit_fixture(
            run_id, path,
            "現行Production実測=LEDGER_DEVIATION(V0、origin=ja_source、JA_RECHECK_REQUIRED STOP実例)。"
            "Standard(a2)は当該run内でStandardが生成される前にAdvanced段でSTOPしたため存在しない"
            "(既知のデータ限界、run_01/run_02ともAdvancedのみ)。V4Aでの再判定は本委任で新規実行。",
        )
        instances.append({
            "instance_id": run_id, "group": "hormuz", "fixture": fx,
            "stage1_mode": "fresh", "stage1_source": None,
            "expected_group_label": "BLOCKING→Rewrite→PASSが期待(現行Production STOP実例)",
            "s1u_eligible": True,
        })

    # --- negative候補7(Normal群、既存V4A再利用) ---
    for fixture_id, path in step3cmp.NEGATIVE_SOURCE_FILES:
        fx = step3cmp.load_negative_fixture(fixture_id, path)
        instances.append({
            "instance_id": fixture_id, "group": "negative", "fixture": fx,
            "stage1_mode": "reuse", "stage1_source": f"{NEG_STAGE1_DIR}/{fixture_id}/V4A/run_1.json",
            "expected_group_label": "ACCEPTABLE(Normal群、§7-5)", "s1u_eligible": True,
        })

    return instances


# ------------------------------------------------------------
# 委任_18 2-1(a)(b): precheck合成マーカーの実文解決(§1-1-2/§1-1-3の
# 根本原因是正)。precheckのarticle_evidenceは診断用の合成文字列
# (例: "count values found in article not matching any ledger fact:
# [30000000.0]")であり記事本文には一言一句存在しない。これをそのまま
# claim_textとしてlocate_target()へ渡すと必ずfound=Falseになり、
# ①〜④のladderが一度も試行されないまま⑥全体フォールバックへ落ちる
# (disclosure §1-1-1で機械確認済み)。本関数はfinding固有の生の実測値
# (foreign_values/other_dates_raw/matched_phrase/article_evidence[list])
# を使って記事本文中の実文(その値を含む文)を検索し、見つかればそれを
# claim_textとして使う(以降は既存locate_target()の通常経路[exact
# substring→SequenceMatcher→er010 word-overlap]がそのまま機能し、
# ①〜④のladderが正しく試行される)。見つからなければ
# (None, "not_locatable")を返し、呼び出し側(run_instance)は
# Rewriteを試みずStage4(target_not_locatable)へ回す(2-1(b)(d)、
# ⑥全体フォールバックを「locate未試行の代替」として使わない)。
# ------------------------------------------------------------
def resolve_precheck_target_sentence(article_text: str, finding: dict) -> tuple:
    kind = finding.get("kind")
    sentences = split_sentences_generic(article_text)

    if kind == "number_mismatch":
        for v in finding.get("foreign_values") or []:
            for s in sentences:
                nums = precheck.extract_percentages(s) | set(precheck.extract_counts(s))
                if v in nums:
                    return s, "precheck_number_locate"
        return None, "not_locatable"
    if kind == "date_mismatch":
        for (y, m, d) in finding.get("other_dates_raw") or []:
            for rep in _date_representations_safe(y, m, d):
                for s in sentences:
                    if rep and rep in s:
                        return s, "precheck_date_locate"
        return None, "not_locatable"
    if kind == "actor_missing":
        candidates = finding.get("article_evidence")
        candidates = candidates if isinstance(candidates, list) else []
        for cand in candidates:
            for s in sentences:
                if cand and cand in s:
                    return s, "precheck_actor_locate"
        return None, "not_locatable"
    if kind == "comparison_marker":
        phrase = finding.get("matched_phrase")
        if phrase:
            for s in sentences:
                if phrase.lower() in s.lower():
                    return s, "precheck_comparison_locate"
        return None, "not_locatable"
    if kind == "negation_marker":
        # article_evidence(stripped、既に記事本文へ小文字化一致で実在確認
        # 済みの文言)から、大小文字を問わず対応する実文を探す。
        phrase = finding.get("article_evidence")
        if isinstance(phrase, str) and phrase:
            for s in sentences:
                if phrase.lower() in s.lower():
                    return s, "precheck_negation_locate"
        return None, "not_locatable"
    return None, "not_locatable"


def _date_representations_safe(year: int, month: int, day: int) -> list:
    try:
        return precheck._date_representations(year, month, day)
    except Exception:  # noqa: BLE001
        return []


# ------------------------------------------------------------
# precheck floor claim構築(§3-1/§4-3、findingが既存Stage1 MAJOR claimの
# related_fact_idと重複しない場合のみ追加)
# ------------------------------------------------------------
def build_precheck_floor_claims(fixture: dict, existing_fact_ids: set) -> list:
    findings = precheck.run_precheck(fixture["ledger_text"], fixture["article_text"])
    out = []
    for f in findings:
        if f["field"] in existing_fact_ids:
            continue
        # 委任_18 2-1(a): claim_textを合成マーカーではなく実文へ解決する。
        resolved_sentence, resolve_method = resolve_precheck_target_sentence(fixture["article_text"], f)
        evidence_str = f.get("article_evidence") if isinstance(f.get("article_evidence"), str) \
            else str(f.get("article_evidence"))
        claim_text = resolved_sentence if resolved_sentence is not None else evidence_str
        dev = {
            "claim_in_article": claim_text,
            "issue": f"precheck detected {f['kind']} vs ledger_value={f['ledger_value']}",
            "explanation": f"deterministic precheck finding (kind={f['kind']})",
            "related_fact_id": f["field"], "origin": None,
            **{k: False for k in FLOOR_FLAGS},
        }
        out.append({"claim_text": claim_text, "origin": None, "related_fact_id": f["field"],
                     "dev": dev, "detected_by": "precheck",
                     # 委任_18 2-1(b): 実文へ解決できなかった場合のフラグ
                     # (run_instanceがRewriteを試みずStage4へ回すための合図)。
                     "precheck_target_locatable": resolved_sentence is not None,
                     "precheck_locate_method": resolve_method})
    return out


# ------------------------------------------------------------
# instance単位オーケストレーション(Stage1→2→3→Recheck、cycle上限2)
# ------------------------------------------------------------
def run_instance(client, state, consecutive_errors, inst: dict, enable_s1u: bool = False,
                  stage1_cache: dict | None = None, instances_subdir: str = "instances",
                  use_enumeration_stage1: bool = True,
                  use_misconception_principle: bool = ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT) -> dict:
    instance_id = inst["instance_id"]
    fixture = inst["fixture"]
    call_log: list = []
    t0 = time.time()

    if inst["stage1_mode"] == "reuse":
        stage1_parsed = stage1_reuse(inst["stage1_source"])
        stage1_call_used = False
        # 委任_23 A-2(b): reuse fixtureは`same_fact_id_locations`フィールド
        # を持たないため(§6-8「reuse fixtureへの安全側fallback」)、¥0
        # 決定論フォールバックで数値/キーワード一致による同一fact言及箇所の
        # 候補列挙を試み、既存`expand_same_fact_id_locations`(fail-closed、
        # 逐語実在確認)で実際に追加する。fresh instance(LLMベース列挙
        # フィールドを既に持つ)は`deterministic_same_fact_id_location_
        # fallback`内部でスキップされ上書きしない。
        if stage1_parsed.get("overall_status") == "LEDGER_DEVIATION" and isinstance(
                stage1_parsed.get("deviations"), list):
            enumerated = deterministic_same_fact_id_location_fallback(
                stage1_parsed["deviations"], fixture["article_text"])
            stage1_parsed = dict(stage1_parsed)
            stage1_parsed["deviations"] = expand_same_fact_id_locations(enumerated, fixture["article_text"])
    else:
        # 委任_13(iteration5、n=2実行): Stage1(fresh mode)はcycle1の入力
        # (ledger_text+article_text+source_article_text)が同一である限り、
        # sha256一致で再利用する(instance_idの末尾サンプル番号[_s1/_s2]を
        # 除いた基底キーでcache共有、二重課金防止)。stage1_cacheが渡されない
        # 場合[resume再実行等]は従来どおり毎回新規callする。
        stage1_call_used = False
        cache_key = None
        if stage1_cache is not None:
            cache_key = hashlib.sha256(
                (fixture["ledger_text"] + "␟" + fixture["article_text"] + "␟"
                 + (fixture.get("source_article_text") or "")).encode("utf-8")
            ).hexdigest()
        if cache_key is not None and cache_key in stage1_cache:
            stage1_parsed = stage1_cache[cache_key]
        else:
            # 委任_20 W2(既定True): 同一fact_id別箇所列挙フィールド付きの
            # Stage1初回callを使う(追加callなし、¥0限界コスト)。
            # 委任_30 Part2(design書§0/§9-1): 重大誤解原則(既定True、
            # `ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT`)をdeveloper message
            # として既定配線する(`use_enumeration_stage1=False`の場合は
            # 旧`stage1_fresh`[enum非対応・原則非対応]のまま、後方互換)。
            stage1_developer_message = (
                trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE
                if (use_enumeration_stage1 and use_misconception_principle)
                else vfl01.DEVIATION_DEVELOPER_MESSAGE
            )
            if use_enumeration_stage1:
                stage1_parsed = stage1_fresh_with_enumeration(
                    client, state, consecutive_errors, call_log, f"{instance_id}_stage1", fixture,
                    developer_message=stage1_developer_message)
            else:
                stage1_parsed = stage1_fresh(client, state, consecutive_errors, call_log,
                                              f"{instance_id}_stage1", fixture)
            stage1_call_used = True
            if cache_key is not None:
                stage1_cache[cache_key] = stage1_parsed

    # S1-U variant(委任_10、§3-1): --s1u有効時、このinstanceがs1u_eligible
    # かつStage1(V4A)がACCEPTABLE(PASS)だった場合のみ、S1-D 1 callを追加して
    # recallを補強する(union、fail-closed)。既にLEDGER_DEVIATIONの場合は
    # 追加callを行わない(コストをかけない)。
    # 委任_11 作業B-5(§8測定是正、Opus L2 #2論点2): `s1u_caught_recall_miss`
    # を`s1u_additional_block`へ改名し(「実際にmissを捕捉したか」ではなく
    # 「追加BLOCKINGを検出したか」を素直に表す名前へ)、正解ラベル照合の
    # 真偽列(`s1u_additional_block_label`)を追加する(既知recall miss=
    # true_positive、negative群=false_positive、それ以外=unlabeled)。
    s1u_screen_used = False
    s1u_additional_blocking_count = 0
    s1u_additional_block = False
    s1u_additional_block_label = None
    if enable_s1u and inst.get("s1u_eligible") and stage1_parsed.get("overall_status") != "LEDGER_DEVIATION":
        s1u_screen_used = True
        s1u_result = stage1_union_screen(client, state, consecutive_errors, call_log,
                                          f"{instance_id}_s1u_screen", fixture)
        s1u_additional_blocking_count = len(s1u_result["blocking_deviations"])
        if s1u_result["blocking_deviations"]:
            s1u_additional_block = True
            if instance_id in KNOWN_RECALL_MISS_INSTANCE_IDS:
                s1u_additional_block_label = "true_positive"
            elif inst["group"] == "negative":
                s1u_additional_block_label = "false_positive"
            else:
                s1u_additional_block_label = "unlabeled"
            stage1_parsed = {"overall_status": "LEDGER_DEVIATION",
                              "deviations": s1u_result["blocking_deviations"]}

    stage1_recall_miss_substituted = False
    if (inst.get("substitute_baseline_on_stage1_miss") and stage1_parsed.get("overall_status") != "LEDGER_DEVIATION"
            and fixture.get("baseline_parsed", {}).get("overall_status") == "LEDGER_DEVIATION"):
        # V4A単発実行がSafety観点で既知BLOCKINGのfixtureを非検出(recall
        # miss、§10/§14既知の限界)だったため、Stage2/3経路自体を検証する
        # 目的で実Production V0 baseline(既にMAJOR検出済み)へ代替する。
        # V4Aが検出したかのように偽装はせず、代替した事実をそのまま記録する。
        stage1_recall_miss_substituted = True
        stage1_parsed = fixture["baseline_parsed"]

    overall_status = stage1_parsed.get("overall_status")
    if overall_status != "LEDGER_DEVIATION":
        elapsed = round(time.time() - t0, 3)
        result = {
            "instance_id": instance_id, "group": inst["group"], "expected_group_label": inst["expected_group_label"],
            "final_state": "ACCEPTABLE_STAGE1", "stage4_reason": None, "cycles": [],
            "stage1_call_used": stage1_call_used, "stage1_recall_miss_substituted": stage1_recall_miss_substituted,
            "s1u_screen_used": s1u_screen_used, "s1u_additional_blocking_count": s1u_additional_blocking_count,
            "s1u_additional_block": s1u_additional_block, "s1u_additional_block_label": s1u_additional_block_label,
            "call_log": call_log,
            "total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4),
            "total_calls": len(call_log), "elapsed_seconds": elapsed,
        }
        save_json(f"{OUT_DIR}/{instances_subdir}/{instance_id}.json", result)
        return result

    # 委任_11 作業B-3(§3-3停止判定の是正): fact_id一致+claim本文近似一致
    # (find_matching_prior_record)で「同一claim再発」を判定する(旧来の
    # fact_id単独一致による過剰なStage4を是正、Opus L2 #2論点1)。
    prior_blocking_records: list = []
    prev_cycle_blocking_count = None
    extra_cycle_granted = False
    current_en_text = fixture["article_text"]
    current_ja_text = fixture.get("source_article_text")
    cycles_log = []
    final_state, stage4_reason = None, None
    # 委任_20 W1(i)(Opus L2レビュー#4 §0): JA recheckが未解消
    # (ja_ok=False)のまま次cycleへ進んだ事実を保持する。この状態のまま
    # loopが「not blocking_claims」downgrade経路(RESOLVED_STAGE2_DOWNGRADE/
    # RESOLVED_REWRITE_THEN_DOWNGRADE)へ抜けた場合は、JA側の未解消を
    # 握り潰さずSTAGE4_ESCALATION(ja_deviation_unresolved)を強制する
    # (rep10 hormuz_run03_standard sample1 cycle2のfalse PASS再発防止)。
    ja_pending_deviation = False

    # 委任_11 作業B-6(§4 Rewrite由来新規逸脱検出、Opus L2 #2論点4推奨3):
    # Rewrite前(オリジナル記事)のprecheck findingをbaselineとして保持し、
    # 各cycleのRewrite後テキストと比較する(¥0、決定論)。
    baseline_precheck_en = precheck.run_precheck(fixture["ledger_text"], fixture["article_text"])
    baseline_precheck_ja = (
        precheck.run_precheck(fixture["ledger_text"], fixture["source_article_text"])
        if fixture.get("source_article_text") is not None else []
    )

    stage1_deviations = [d for d in stage1_parsed.get("deviations", []) if d.get("severity") == "MAJOR"]
    cycle = 1
    while True:
        working_fixture = dict(fixture)
        working_fixture["article_text"] = current_en_text
        if current_ja_text is not None:
            working_fixture["source_article_text"] = current_ja_text

        existing_fact_ids = {(d.get("related_fact_id") or "") for d in stage1_deviations}
        precheck_claims = build_precheck_floor_claims(working_fixture, existing_fact_ids)

        llm_claims = [{"claim_text": d.get("claim_in_article", ""), "origin": d.get("origin"),
                       "related_fact_id": d.get("related_fact_id"), "dev": d, "detected_by": "stage1_llm"}
                      for d in stage1_deviations]

        stage2_input_claims = [c for c in llm_claims]
        stage2_results = []
        if stage2_input_claims:
            stage2_results = run_stage2(client, state, consecutive_errors, call_log,
                                         f"{instance_id}_c{cycle}_stage2", working_fixture, stage2_input_claims)
        # precheck floor claimsはStage2をスキップし直接BLOCKING確定。rewrite_hintは
        # precheck findingのissue文言(deterministic、fact_idを含む)をそのまま使う
        # (LLM生成ではないが、対象claim文言の逐語引用+fact_idという要件は満たす)。
        for pc in precheck_claims:
            hint = (f"{pc['claim_text'][:60]!r} を、fact_id={pc['dev'].get('related_fact_id', '')}の"
                    f"Ledger値へ置換する。issue: {pc['dev'].get('issue', '')}")
            stage2_results.append({**pc, "materiality": "BLOCKING", "llm_materiality": None,
                                    "basis": "precheck_floor", "rewrite_kind": "replace_with_ledger_value",
                                    "rewrite_hint": hint, "floor_reason": "precheck_floor",
                                    "section_type": detect_claim_section_type(
                                        pc["claim_text"], working_fixture["article_text"]),
                                    # 委任_17: precheck floor claimはStage2自体を経由しない
                                    # (run_stage2を呼ばない)ため、stage2_route
                                    # (body/hook振り分け)は該当なし。
                                    "stage2_route": "precheck_floor_bypass",
                                    "floor_cited_materiality": "BLOCKING", "floor_cited_reason": "precheck_floor"})

        # 委任_13(iteration5、Stage2 2-of-2安定化): precheck floor claim
        # (floor_reason="precheck_floor")は対象外なので混在させても安全。
        stage2_results, stage2_two_of_two_log = apply_stage2_two_of_two(
            client, state, consecutive_errors, call_log, f"{instance_id}_c{cycle}", working_fixture,
            stage2_results, inst)

        blocking_claims = [c for c in stage2_results if c["materiality"] == "BLOCKING"]
        non_blocking_claims = [c for c in stage2_results if c["materiality"] != "BLOCKING"]

        cycle_record = {
            "cycle": cycle, "stage2_results": stage2_results,
            "blocking_count": len(blocking_claims), "non_blocking_count": len(non_blocking_claims),
            "stage2_two_of_two_log": stage2_two_of_two_log,
        }

        if not blocking_claims:
            # 委任_20 W1(i): 直前cycleでJA recheckが未解消(ja_pending_
            # deviation=True)のまま、このcycleでEN側由来のstage1_deviations
            # だけがblocking_claimsへ再構築され空になった場合(rep10
            # hormuz_run03_standard sample1 cycle2の実データで観測)、
            # 「解消」として静かにdowngradeせず、JA側の未解消を理由に
            # STAGE4_ESCALATIONへ回す(false PASS再発防止、fail-closed)。
            if ja_pending_deviation:
                final_state = "STAGE4_ESCALATION"
                stage4_reason = "ja_deviation_unresolved"
            else:
                final_state = "RESOLVED_STAGE2_DOWNGRADE" if cycle == 1 else "RESOLVED_REWRITE_THEN_DOWNGRADE"
            cycles_log.append(cycle_record)
            break

        # 委任_11 作業B-3(§3-3停止判定の是正、Opus L2 #2論点1推奨3): fact_id
        # 一致だけでなく正規化claim本文の近似一致も要求する
        # (find_matching_prior_record)。一致すれば「Rewriteが当該claimに
        # 効かなかったことが実証された」として従来どおり即Stage4。一致
        # しない場合(fact_idが同じでも別文=兄弟文カスケードではない、
        # またはfact_id無しの新規claim)は、cycle上限(MAX_CYCLES)超過時でも
        # 直前cycleよりblocking件数が厳密に減少していればcycle 3を1回だけ
        # 許可する(上限HARD_MAX_CYCLES、Opus L2 #2論点1「残る7件のうち
        # meta_run03_standard/B4等は進捗しているのに打ち切られている」の
        # 是正)。
        matched_records = []
        matched_claim_by_identity = {}
        if cycle > 1:
            for c in blocking_claims:
                m = find_matching_prior_record(c["dev"], prior_blocking_records)
                if m is not None:
                    matched_records.append(m)
                    matched_claim_by_identity[m["identity"]] = c

        # 委任_24 A-2(§6-13、rep14で判明した第三要因の是正): 同一claim
        # 再発は「Rewriteが当該claimに効かなかったことの実証」だが、それ
        # だけで直ちにSTAGE4へ回すのは、まだ最小変更ラダー(①単語・接続詞 ->
        # ③1文 -> ④段落)を昇段しきっていない場合に、ラダーが昇段して
        # いないこと自体を「Stage3 Rewrite品質の限界」と誤認し、§3-3安全網
        # (本判定)を§6-6 A-2のラダー前進機構より先に発火させてしまう
        # (rep14 hormuz_run03_standard実データ、DECISION_LOG本委任エントリ
        # 参照)。前回このclaim(identity単位、fact_id一致時はfact_id、
        # fact_id欠落時はhashベース厳密一致)のRewriteが既に④段落水準まで
        # 試行済み(`escalated_to_paragraph=True`、prior_blocking_records
        # へ記録)だった場合のみ、「ラダーを昇段しきった上での再発」として
        # 従来どおり直ちにSTAGE4(same_claim_fact_id_reblocked)へ回す。まだ
        # ①・③水準までしか試していない場合はSTAGE4にせず、当該claimへ
        # `escalate_to_paragraph=True`を明示的に付与したうえでループを継続
        # する(cycle上限[MAX_CYCLES/HARD_MAX_CYCLES]自体は変更しない)。
        # これは新しい機構ではなく、既存の§6-6 A-2 fact_id再出現ラダー
        # 前進機構(下記repeat_fact_ids_for_recheck)へ合流させるものであり、
        # fact_idが同じであればいずれ自動的にも設定されるが、fact_id欠落
        # claim(hashベースidentity)を取りこぼさないためidentity単位でも
        # 明示的に設定する。既存のfact_id単独一致判定・cycle上限・JA fail-
        # open封鎖・等価FAIL gatingは無変更。
        exhausted_matched_records = [m for m in matched_records if m.get("escalated_to_paragraph")]
        escalatable_matched_records = [m for m in matched_records if not m.get("escalated_to_paragraph")]
        if exhausted_matched_records:
            final_state = "STAGE4_ESCALATION"
            stage4_reason = "same_claim_fact_id_reblocked"
            cycle_record["repeat_claim_ids"] = sorted({m["identity"] for m in exhausted_matched_records})
            cycle_record["ladder_exhausted_before_reblock"] = True
            cycles_log.append(cycle_record)
            break
        if escalatable_matched_records:
            cycle_record["same_claim_reblocked_escalated_to_paragraph"] = sorted(
                {m["identity"] for m in escalatable_matched_records})
            for m in escalatable_matched_records:
                claim = matched_claim_by_identity.get(m["identity"])
                if claim is not None:
                    claim["escalate_to_paragraph"] = True

        if cycle > MAX_CYCLES:
            # 委任_18 2-3(b)(meta_run03_standard sample2実測、disclosure
            # §1-3-2): 同一fact_idのclaimが記事内の複数箇所に分散し、
            # cycleごとに1箇所ずつしか検出されない場合(この時点で
            # matched_recordsは空=claim本文は別物と既に判定済み)、
            # blocking件数が厳密に減少していなくても、その中に「過去cycleで
            # 一度でもBLOCKINGとして見たfact_idの、新しい箇所(別文言)」が
            # 含まれていれば、cycle上限3を超えない範囲で1回だけ追加cycleを
            # 許可する(「箇所ごとに①からladder」の最小対応、cycle_limit_
            # exhaustedによる誤ったSTAGE4を防ぐ)。
            current_fact_ids = {
                (c["dev"].get("related_fact_id") or "").strip() for c in blocking_claims
                if (c["dev"].get("related_fact_id") or "").strip()
            }
            prior_fact_ids = {r["fact_id"] for r in prior_blocking_records if r["fact_id"]}
            same_fact_id_new_location = bool(current_fact_ids & prior_fact_ids)
            progress_shown = (
                prev_cycle_blocking_count is not None and len(blocking_claims) < prev_cycle_blocking_count
            )
            allow_extra_cycle = (
                not extra_cycle_granted and cycle == MAX_CYCLES + 1
                and (progress_shown or same_fact_id_new_location)
            )
            if allow_extra_cycle:
                extra_cycle_granted = True
                cycle_record["extra_cycle_granted"] = True
                if same_fact_id_new_location and not progress_shown:
                    cycle_record["extra_cycle_reason"] = "same_fact_id_new_location(委任_18 2-3b)"
            else:
                final_state = "STAGE4_ESCALATION"
                stage4_reason = "cycle_limit_exhausted"
                cycles_log.append(cycle_record)
                break

        # 委任_19 A-2(hormuz_run03_standard cycle枯渇是正、disclosure非該当の
        # rep9新規観測): このcycleのBLOCKING claimのfact_idが、過去cycleで
        # 一度でもBLOCKINGとして見たfact_id(=同一問題が別文言・別箇所で
        # 再出現)と一致する場合、①単語・接続詞/③1文の局所ラダーは既に
        # 効果が乏しいと実証済みとみなし、④段落水準から試す
        # (`escalate_to_paragraph`)。cycle数そのものの上限(MAX_CYCLES/
        # HARD_MAX_CYCLES)は変更しない(既存の安全上限に触れない、狭い
        # ラダー選択のみの変更)。段落ブロックが見つからない場合は既存の
        # ⑥全体フォールバックへ自然にフォールバックする(新しいNG経路は
        # 作らない)。**既知の限界**: hormuz_run03_standardの実例(cycle3が
        # 見出し/one-line要約、cycle1-2が本文)のように同一fact_idの問題が
        # 「別の段落・別のセクション」に分散する場合、対象claimを含む段落
        # 単位のRewriteでは他セクションまでは直せない(Phase2課題item8、
        # 多箇所分散Rewriteの根本解決ではなく、同一段落内での再発防止に
        # 限定した部分対応であることをFableへ正直に報告する)。
        repeat_fact_ids_for_recheck = frozenset(
            (c["dev"].get("related_fact_id") or "").strip() for c in blocking_claims
        ) & frozenset(r["fact_id"] for r in prior_blocking_records if r["fact_id"])
        for c in blocking_claims:
            fid = (c["dev"].get("related_fact_id") or "").strip()
            if fid and fid in repeat_fact_ids_for_recheck:
                c["escalate_to_paragraph"] = True

        for c in blocking_claims:
            prior_blocking_records.append({
                "identity": claim_identity(c["dev"]),
                "fact_id": (c["dev"].get("related_fact_id") or "").strip(),
                "claim_text_norm": normalize_claim_text(c["dev"].get("claim_in_article") or ""),
                # 委任_24 A-2(§6-13): このRewrite試行で④段落水準まで既に
                # 試行済みか(escalate_to_paragraphが今cycleで付与済みか)を
                # 記録する。次cycleで同一claimが再発した際、matched_records
                # 判定がこのフラグを見て「ラダー昇段しきった上での再発
                # (直ちにSTAGE4)」か「まだ昇段の余地がある再発(ループ継続)」
                # かを区別する。
                "escalated_to_paragraph": bool(c.get("escalate_to_paragraph")),
            })
        prev_cycle_blocking_count = len(blocking_claims)

        # 委任_12(iteration4、§8): Rewrite品質劣化候補判定用にRewrite前
        # テキストを保持する(¥0、決定論比較)。
        en_text_before_rewrite = current_en_text
        ja_text_before_rewrite = current_ja_text

        # 委任_13(iteration5、Rewrite品質制約): 対象レベル(Standard=A2、
        # Advanced=B1B)の語彙・文長制約+hook保持+削除優先をrewrite_hintへ
        # 追記する(infer_article_level、既知の限界: B1/B2/B3/B4等のJA単体
        # 較正fixtureはlevel None=共通制約のみ)。
        article_level = infer_article_level(instance_id)
        base_constraint = level_constraint_text(article_level)

        def _run_stage3_cycle(claims_list, en_text, ja_text, extra_constraint, label_suffix=""):
            en_out, ja_out = en_text, ja_text
            records, pairs = [], []
            for c in claims_list:
                c2 = dict(c)
                c2["extra_constraint"] = extra_constraint
                r = run_stage3_for_claim(
                    client, state, consecutive_errors, call_log,
                    f"{instance_id}_c{cycle}_{claim_identity(c['dev'])[:20]}{label_suffix}",
                    working_fixture, en_out, ja_out, c2)
                en_out = r["en_text"]
                if r["ja_text"] is not None:
                    ja_out = r["ja_text"]
                records.append({"claim_identity": claim_identity(c["dev"]), "rewrite_kind": c["rewrite_kind"],
                                 "mechanism": r["mechanism"], "method": r["method"], "guard_ok": r["guard_ok"],
                                 "ladder_level_used": r.get("ladder_level_used"),
                                 "section_type": c.get("section_type"),
                                 # 委任_18 2-1(b): 対象文が一度も特定できずRewrite自体を
                                 # 試みなかったclaim(呼び出し側run_instanceがStage4へ回す)。
                                 "target_not_locatable": r.get("target_not_locatable", False),
                                 # 委任_23 B-2: ⑥ feature flag(既定OFF)時、①〜④/delete
                                 # 全段でguardが失敗したclaim(呼び出し側run_instanceが
                                 # STAGE4へ回す)。
                                 "ladder_exhausted_without_full_rewrite": r.get(
                                     "ladder_exhausted_without_full_rewrite", False)})
                pairs.append({"before": r.get("before_fragment"), "after": r.get("after_fragment")})
            return en_out, ja_out, records, pairs

        # Stage 3: 各BLOCKING claimに対しRewrite dispatch(1回目)
        current_en_text, current_ja_text, rewrite_records, before_after_pairs = _run_stage3_cycle(
            blocking_claims, current_en_text, current_ja_text, base_constraint)

        # 委任_18 2-1(b): 対象文が一度も特定できず(single_text_rewrite/
        # paired_rewriteがRewriteを試みずtarget_not_locatable=Trueを返した)
        # claimが1件でもあれば、他claimの結果を保存したうえでこの記事の
        # cycleを打ち切り、Stage4(target_not_locatable)へ回す(⑥全体
        # フォールバックを未試行の代替として使わない、2-1(d))。
        unlocatable_records = [r for r in rewrite_records if r.get("target_not_locatable")]
        if unlocatable_records:
            final_state = "STAGE4_ESCALATION"
            stage4_reason = "target_not_locatable"
            cycle_record["rewrite_records"] = rewrite_records
            cycle_record["unlocatable_claim_ids"] = sorted(
                {r["claim_identity"] for r in unlocatable_records})
            cycles_log.append(cycle_record)
            break

        # 委任_23 B-2: ⑥ feature flag(既定OFF)時、①〜④/delete全段でguardが
        # 失敗したclaimが1件でもあれば、target_not_locatableと同じパターンで
        # この記事のcycleを打ち切り、直ちにStage4(ladder_exhausted_without_
        # full_rewrite)へ回す(⑥を未試行のまま追加cycleへ進まない、iter7実測
        # で⑥使用7件全てが最終的にSTAGE4だった=⑥が必要だったEvidenceが
        # 0件だったため)。
        ladder_exhausted_records = [r for r in rewrite_records if r.get("ladder_exhausted_without_full_rewrite")]
        if ladder_exhausted_records:
            final_state = "STAGE4_ESCALATION"
            stage4_reason = "ladder_exhausted_without_full_rewrite"
            cycle_record["rewrite_records"] = rewrite_records
            cycle_record["ladder_exhausted_claim_ids"] = sorted(
                {r["claim_identity"] for r in ladder_exhausted_records})
            cycles_log.append(cycle_record)
            break

        # 委任_13(iteration5、品質劣化検出v2+同一cycle内1回だけの再生成):
        # (a)重複段落/(b)孤立逆接語/(c)語彙難化のいずれかを検出した場合のみ、
        # 元のen_text_before_rewriteへ戻し、制約を強調して1回だけ再生成する
        # (d)タイトル/hook変更は正当な理由がある場合もあるため単独では
        # 再生成トリガにしない(needs_regenerationの定義どおり)。
        quality_degradation_v2 = measure_rewrite_quality_degradation_v2(
            en_text_before_rewrite, current_en_text, changed_fragments=before_after_pairs)
        # 委任_14 B-4(2026-09-30ユーザー新方針item5): Title/Hook/In one line
        # の役割維持を品質劣化v2と統合し、同じ再生成トリガへ合流させる
        # (段落以上のRewriteへ進まず、既存の同一cycle内1回だけの再生成
        # 機構[委任_13]をそのまま再利用する、新しい機構は作らない)。
        section_role = measure_section_role_violation(en_text_before_rewrite, current_en_text)
        regenerated = False
        if quality_degradation_v2["needs_regeneration"] or section_role["section_role_violated"]:
            regenerated = True
            combined_reasons = "; ".join(
                r for r in (quality_degradation_v2["reasons"], section_role["reasons"]) if r)
            emphasized_constraint = base_constraint + REGENERATION_EMPHASIS_TEMPLATE.format(
                reasons=combined_reasons)
            current_en_text, current_ja_text, rewrite_records, before_after_pairs = _run_stage3_cycle(
                blocking_claims, en_text_before_rewrite, ja_text_before_rewrite, emphasized_constraint,
                label_suffix="_regen")
            quality_degradation_v2_after_regen = measure_rewrite_quality_degradation_v2(
                en_text_before_rewrite, current_en_text, changed_fragments=before_after_pairs)
            section_role_after_regen = measure_section_role_violation(en_text_before_rewrite, current_en_text)
        else:
            quality_degradation_v2_after_regen = None
            section_role_after_regen = None

        cycle_record["rewrite_records"] = rewrite_records
        cycle_record["quality_degradation_v2"] = quality_degradation_v2
        cycle_record["section_role_violation"] = section_role
        cycle_record["quality_degradation_v2_regenerated"] = regenerated
        if quality_degradation_v2_after_regen is not None:
            cycle_record["quality_degradation_v2_after_regen"] = quality_degradation_v2_after_regen
        if section_role_after_regen is not None:
            cycle_record["section_role_violation_after_regen"] = section_role_after_regen
        cycle_record["quality_degradation_en"] = measure_rewrite_quality_degradation(
            en_text_before_rewrite, current_en_text)
        if ja_text_before_rewrite is not None and current_ja_text is not None:
            cycle_record["quality_degradation_ja"] = measure_rewrite_quality_degradation(
                ja_text_before_rewrite, current_ja_text)
        # 委任_12(iteration4、作業D読み比べページ用): Rewrite前後の全文を
        # cycle_recordへ保存する(サイズ抑制のため、実際にRewriteが発火した
        # cycleのみ。en_text_before_rewrite==current_en_textなら保存しない)。
        if current_en_text != en_text_before_rewrite:
            cycle_record["en_text_before_rewrite"] = en_text_before_rewrite
            cycle_record["en_text_after_rewrite"] = current_en_text
        if ja_text_before_rewrite is not None and current_ja_text != ja_text_before_rewrite:
            cycle_record["ja_text_before_rewrite"] = ja_text_before_rewrite
            cycle_record["ja_text_after_rewrite"] = current_ja_text

        # 委任_20 W1(iii)(Opus L2レビュー#4 §0/Q1(b)): ¥0決定論JA fail-open
        # ガード。paired rewriteでJA本文がこのcycleで変化した場合、
        # 指摘JA文の逐語残存/対象段落外JA文の消失を機械的に判定する。
        ja_guard_result = None
        if ja_text_before_rewrite is not None and current_ja_text is not None:
            ja_guard_result = ja_fail_open_guard(ja_text_before_rewrite, current_ja_text, blocking_claims)
            cycle_record["ja_fail_open_guard"] = ja_guard_result

        # 委任_18 2-1(c)(disclosure §1-1-4是正): title/hookが空文字・極端
        # 短縮(語数<3)になった場合、既存needs_regeneration(1回だけ再生成
        # を試みるが、再生成後も同じ結果ならそのまま通過してしまう既存の
        # ガード漏れ)とは別に、無条件hard blockとしてSTAGE4へ回す
        # (再生成を1回試みた後の結果[regenerated時]を優先して判定する)。
        # 委任_35(design書§6-16): iol_degenerate(「## In one line」見出し
        # 自体の削除・消失)も同じhard block条件へ合流させる(rep19実測
        # cycle3、§32-3参照)。
        final_section_role = section_role_after_regen if section_role_after_regen is not None else section_role
        if (final_section_role.get("title_degenerate") or final_section_role.get("hook_degenerate")
                or final_section_role.get("iol_degenerate")):
            final_state = "STAGE4_ESCALATION"
            stage4_reason = "degenerate_rewrite_output"
            cycle_record["degenerate_rewrite_detected"] = True
            cycles_log.append(cycle_record)
            break

        # 委任_11 作業B-6(§4 Rewrite由来新規逸脱検出、Opus L2 #2論点4):
        # (a) 決定論precheckの再実行(¥0、baseline比較で新規finding検出)。
        rewrite_new_findings_en = detect_rewrite_new_precheck_findings(
            fixture["ledger_text"], baseline_precheck_en, current_en_text)
        rewrite_new_findings_ja = (
            detect_rewrite_new_precheck_findings(fixture["ledger_text"], baseline_precheck_ja, current_ja_text)
            if current_ja_text is not None else []
        )
        cycle_record["rewrite_new_precheck_findings_count"] = (
            len(rewrite_new_findings_en) + len(rewrite_new_findings_ja))
        if rewrite_new_findings_en or rewrite_new_findings_ja:
            cycle_record["rewrite_new_precheck_findings"] = rewrite_new_findings_en + rewrite_new_findings_ja
        # (b) paired rewrite(J-1)が使われた場合のみ、JA↔EN等価チェック1 call
        # (既存の翻訳忠実性QA資産を借用)。委任_20 W1(ii)是正: 従来は
        # flow制御に使わず測定専用だったが、rep10でFAILが実際のJA破損と
        # 一致した実測を踏まえ、ja_ok/full_recheck_required双方のgatingへ
        # 昇格した(下記en_ok/ja_ok計算・full_recheck_required呼び出し参照)。
        if current_ja_text is not None and any(rr["mechanism"].startswith("paired") for rr in rewrite_records):
            eq_result = run_ja_en_equivalence_check(
                client, state, consecutive_errors, call_log, f"{instance_id}_c{cycle}_ja_en_equivalence",
                current_ja_text, current_en_text)
            cycle_record["ja_en_equivalence_verdict"] = eq_result.get("verdict")
            # 委任_27 Part1-4(¥0): 等価QAの判定理由文(verdict単独ではなく
            # 根拠)をjsonへ保存する。従来はverdict文字列のみが記録され、
            # なぜFAIL/REVIEW_REQUIREDになったかの実文が失われていた。
            eq_raw = eq_result.get("raw") or {}
            cycle_record["ja_en_equivalence_reason"] = {
                "notes": eq_raw.get("notes"),
                "meaning_changes": eq_raw.get("meaning_changes"),
                "important_omissions": eq_raw.get("important_omissions"),
                "unsupported_additions": eq_raw.get("unsupported_additions"),
                "number_name_negation_issues": eq_raw.get("number_name_negation_issues"),
            }

        # 委任_18 2-4(局所QA fastpath)/委任_19 A-1(f新設)/委任_20 W3:
        # 全文Recheckを残す条件(a)〜(h)に該当しない場合のみ、局所QA 1
        # call/claimを試す。全件「解消・新規逸脱なし・隣接文影響なし」なら
        # このcycleを解決として全文Recheck(run_recheck/run_recheck_confirm)
        # を省略する。該当する、または局所QAが問題を検出した場合は、既存の
        # 全文Recheckフロー(下記、無変更)へそのままフォールバックする。
        recheck_required, recheck_required_reasons = full_recheck_required(
            rewrite_records, blocking_claims, instance_id, repeat_fact_ids_for_recheck,
            ja_guard_ok=(ja_guard_result["ok"] if ja_guard_result is not None else None),
            ja_equivalence_verdict=cycle_record.get("ja_en_equivalence_verdict"))
        # 委任_20 W1(iii): JA fail-openガード不通過は無条件で全文Recheckへ
        # 回す(局所QA fastpathを試みない。局所QAはJA本文を独立確認しない
        # ため、ガード違反を見逃す構造的リスクがある)。
        if ja_guard_result is not None and not ja_guard_result["ok"]:
            recheck_required = True
            recheck_required_reasons = recheck_required_reasons + ["ja_fail_open_guard_violation"]
        # 委任_21 A-1: ガードが「判定不能」(分割器がJA/非JA判定後も1文以下
        # にしか分割できない)の場合、違反判定は行わない(ok=Trueのまま、
        # ja_okを強制的にFalseへは倒さない)が、局所QA fastpathは信頼できる
        # 判断材料を欠くため全文Recheckへ倒す(安全側、STAGE4直行にはしない)。
        if ja_guard_result is not None and ja_guard_result.get("indeterminate"):
            recheck_required = True
            recheck_required_reasons = recheck_required_reasons + ["ja_fail_open_guard_indeterminate"]
        cycle_record["full_recheck_required"] = recheck_required
        cycle_record["full_recheck_required_reasons"] = recheck_required_reasons
        if not recheck_required:
            local_qa_outcome = run_local_qa_fastpath(
                client, state, consecutive_errors, call_log, f"{instance_id}_c{cycle}",
                working_fixture, current_en_text, blocking_claims, before_after_pairs)
            cycle_record["local_qa_fastpath_attempted"] = True
            cycle_record["local_qa_fastpath_results"] = local_qa_outcome["results"]
            cycle_record["local_qa_fastpath_success"] = local_qa_outcome["success"]
            # 委任_20 W1(iii)是正: 前cycle以前から持ち越したJA未解消
            # (ja_pending_deviation、このcycleに入った時点の値)がある場合、
            # 局所QA(EN側のみ)の成功だけではJA側の未解消を確認できない
            # ため、fastpathでの即時解決を許さない(既存の全文Recheckへ
            # フォールバックする)。
            if local_qa_outcome["success"] and not ja_pending_deviation:
                cycles_log.append(cycle_record)
                final_state = "RESOLVED_REWRITE"
                break
        else:
            cycle_record["local_qa_fastpath_attempted"] = False

        # Recheck(全文、prior_issuesあり、A1。局所QA fastpathが不成立
        # [未該当、または局所QAが問題を検出]の場合のみ到達する、既存挙動
        # は無変更)
        prior_issues = [{"fact_id": c["dev"].get("related_fact_id", ""),
                          "claim_in_article": c["claim_text"],
                          "issue": c["dev"].get("issue", ""), "explanation": c["dev"].get("explanation", "")}
                         for c in blocking_claims]
        recheck_fixture = dict(working_fixture)
        recheck_fixture["article_text"] = current_en_text
        if current_ja_text is not None:
            recheck_fixture["source_article_text"] = current_ja_text
        recheck_parsed = run_recheck(client, state, consecutive_errors, call_log,
                                      f"{instance_id}_c{cycle}_recheck", recheck_fixture, current_en_text,
                                      prior_issues)
        # JA側も別途Recheck(paired rewriteが使われていた場合のみ、JA本文の
        # Ledger整合を独立に確認する。§5-4の「JA側1call+EN側1call」に対応)
        ja_recheck_parsed = None
        if current_ja_text is not None and any(rr["mechanism"].startswith("paired") for rr in rewrite_records):
            ja_recheck_parsed = run_recheck(client, state, consecutive_errors, call_log,
                                             f"{instance_id}_c{cycle}_ja_recheck", recheck_fixture,
                                             current_ja_text, prior_issues)

        cycle_record["recheck_overall_status"] = recheck_parsed.get("overall_status")
        cycle_record["recheck_all_prior_issues_resolved"] = recheck_parsed.get("all_prior_issues_resolved")
        if ja_recheck_parsed is not None:
            cycle_record["ja_recheck_overall_status"] = ja_recheck_parsed.get("overall_status")

        en_ok = (recheck_parsed.get("overall_status") == "LEDGER_COMPLIANT"
                 and recheck_parsed.get("all_prior_issues_resolved"))
        ja_ok = True if ja_recheck_parsed is None else (
            ja_recheck_parsed.get("overall_status") == "LEDGER_COMPLIANT"
            and ja_recheck_parsed.get("all_prior_issues_resolved"))

        # 委任_20 W1(ii)(Opus L2レビュー#4 §0/Q1(b)推奨): 従来は測定専用
        # だったja_en_equivalence_verdictを、paired rewrite使用cycleに限り
        # gating化する。委任_22 A-1でgating方式を整理した
        # (`resolve_ja_ok_after_equivalence_gating`、詳細はそちらの
        # docstring参照)。
        ja_equivalence_verdict = cycle_record.get("ja_en_equivalence_verdict")
        gating_result = resolve_ja_ok_after_equivalence_gating(ja_ok, ja_equivalence_verdict, current_ja_text)
        ja_ok = gating_result["ja_ok"]
        if gating_result["lang_indeterminate"] is not None:
            cycle_record["ja_equivalence_lang_indeterminate"] = gating_result["lang_indeterminate"]
        if gating_result["blocked_by_equivalence"]:
            cycle_record["ja_ok_blocked_by_equivalence"] = True
        if gating_result["not_gated_indeterminate_lang"]:
            cycle_record["ja_equivalence_review_required_not_gated_indeterminate_lang"] = True
        if gating_result["not_gated_already_confirmed_resolved"]:
            cycle_record["ja_equivalence_review_required_not_gated_already_confirmed_resolved"] = True
        # 委任_20 W1(iii): JA fail-openガード不通過はja_okをFalseへ倒す
        # (全文Recheckがself-contradictionなく「解消」を返した場合でも、
        # ¥0決定論ガードが指摘JA文の逐語残存/対象段落外JA文消失を検出した
        # 場合は未解消として扱う)。
        if ja_ok and ja_guard_result is not None and not ja_guard_result["ok"]:
            ja_ok = False
            cycle_record["ja_ok_blocked_by_guard"] = True
        # 委任_20 W1(i): このcycle終了時点のja_ok最終値を保持する(次cycleで
        # 「not blocking_claims」downgrade経路に入った際、JA未解消を握り
        # 潰さないためのfail-closedフラグ)。このcycleでja_recheck_parsedが
        # None(paired rewriteがこのcycleでは使われなかった)の場合は、
        # 「JA側を今cycleは検査していない」だけであり「解消した」わけでは
        # ないため、前cycle以前から持ち越したja_pending_deviationの値を
        # 保持する(誤って安全側フラグを消さない、fail-closed)。
        if ja_recheck_parsed is not None:
            ja_pending_deviation = not ja_ok

        # 委任_11 作業B-5是正(§8測定是正、Opus L2 #2論点7「安全≠成功」):
        # overall_status=LEDGER_COMPLIANTかつall_prior_issues_resolved=False
        # という自己矛盾する応答(fail-openの継ぎ目、iter2の5 instanceで
        # 実際に未検査のまま合格していた)は、次cycleの空deviationsによる
        # 静かな降格(RESOLVED_REWRITE_THEN_DOWNGRADE)を許さず、追加1 call
        # で再確認する(iteration 3で有効化)。
        en_ambiguous = (recheck_parsed.get("overall_status") == "LEDGER_COMPLIANT"
                        and not recheck_parsed.get("all_prior_issues_resolved"))
        if en_ambiguous and not en_ok:
            # 委任_13(iteration5、cite-or-release): run_recheck() ->
            # run_recheck_confirm()へ切替。remaining_sentence必須化+
            # Rewrite前後の対象文ペア(before_after_pairs)をinstructionへ
            # 添え、resolved=falseの根拠が現在の記事本文に実在しない場合は
            # 機械的にresolved=trueへ上書きする(fail-closedを緩めず、
            # 根拠なき未解消を排除、Opus L2レビュー#3論点4推奨1・2)。
            confirm_parsed = run_recheck_confirm(client, state, consecutive_errors, call_log,
                                                  f"{instance_id}_c{cycle}_recheck_confirm", recheck_fixture,
                                                  current_en_text, prior_issues, before_after_pairs)
            cycle_record["recheck_confirm_overall_status"] = confirm_parsed.get("overall_status")
            cycle_record["recheck_confirm_all_prior_issues_resolved"] = confirm_parsed.get(
                "all_prior_issues_resolved")
            cycle_record["recheck_confirm_cite_or_release_released_count"] = confirm_parsed.get(
                "cite_or_release_released_count", 0)
            if (confirm_parsed.get("overall_status") == "LEDGER_COMPLIANT"
                    and confirm_parsed.get("all_prior_issues_resolved")):
                en_ok = True
                cycle_record["recheck_reconfirmed"] = True
            else:
                cycle_record["recheck_reconfirmed"] = False

        cycles_log.append(cycle_record)

        if en_ok and ja_ok:
            final_state = "RESOLVED_REWRITE"
            break

        if cycle_record.get("recheck_reconfirmed") is False:
            # 再確認でも解消未確認(自己矛盾が解消しない) -> 次cycleの空
            # deviationsによる静かな降格を許さずfail-closedでSTAGE4
            final_state = "STAGE4_ESCALATION"
            stage4_reason = "unconfirmed_after_reverify"
            break

        # 未解消 -> 次cycleのStage1 deviationsをRecheck結果から再構築
        stage1_deviations = [d for d in recheck_parsed.get("deviations", []) if d.get("severity") == "MAJOR"]
        # 委任_20 W1(i)是正(Opus L2レビュー#4 §0): 旧実装はEN側
        # recheck_parsed[MAJOR deviations]のみから次cycleを再構築しており、
        # JA側ja_recheck_parsedのMAJOR deviationsが常に握り潰され(JA側
        # LEDGER_DEVIATIONが「解消」として消える)、rep10
        # hormuz_run03_standard sample1 cycle2でfalse PASS
        # (RESOLVED_REWRITE_THEN_DOWNGRADE)を引き起こした。JA側MAJOR
        # deviationsも同一fact_idの重複を避けつつ合流させ、次cycleの
        # blocking_claims候補から脱落しないようにする(origin=ja_sourceを
        # 明示し、次cycleがpaired rewriteで再挑戦できるようにする)。合流
        # してもStage2が再度非BLOCKINGへ倒す等でblocking_claimsが空になる
        # 場合は、上記ja_pending_deviationフラグがSTAGE4_ESCALATIONへ強制
        # 誘導する(fail-closedの二重の安全網)。
        if ja_recheck_parsed is not None:
            existing_dev_fact_ids = {(d.get("related_fact_id") or "") for d in stage1_deviations}
            ja_major_deviations = [
                d for d in ja_recheck_parsed.get("deviations", []) if d.get("severity") == "MAJOR"]
            for d in ja_major_deviations:
                fid = (d.get("related_fact_id") or "")
                if fid and fid in existing_dev_fact_ids:
                    continue
                d = dict(d)
                d["origin"] = "ja_source"
                stage1_deviations.append(d)
                if fid:
                    existing_dev_fact_ids.add(fid)
        cycle += 1
        if cycle > HARD_MAX_CYCLES:
            final_state = "STAGE4_ESCALATION"
            stage4_reason = "cycle_limit_exhausted_after_recheck"
            break

    elapsed = round(time.time() - t0, 3)
    result = {
        "instance_id": instance_id, "group": inst["group"], "expected_group_label": inst["expected_group_label"],
        "final_state": final_state, "stage4_reason": stage4_reason, "cycles": cycles_log,
        "stage1_call_used": stage1_call_used, "stage1_recall_miss_substituted": stage1_recall_miss_substituted,
        "s1u_screen_used": s1u_screen_used, "s1u_additional_blocking_count": s1u_additional_blocking_count,
        "s1u_additional_block": s1u_additional_block, "s1u_additional_block_label": s1u_additional_block_label,
        "call_log": call_log,
        "total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4),
        "total_calls": len(call_log), "elapsed_seconds": elapsed,
    }
    save_json(f"{OUT_DIR}/{instances_subdir}/{instance_id}.json", result)
    return result


# ------------------------------------------------------------
# 委任_33(design書§8-x、REPORT§31): `silent_pass_candidate`自動検知の実装。
# 委任_32(REPORT§30-3C)で、`escalation_zero_breakdown.silent_pass_
# candidate`は常に0を返す非稼働プレースホルダであり、B3/A2A3-0の誤降格
# 2件はSAFETY_CRITICAL_SUB_IDS(r3d、8claim名指しリスト)との手動照合で
# 初めて検出できたことが判明した。本関数は、各instanceのcycle別
# stage2_results(claim_text/related_fact_id/materiality、既存run_instance
# が既に保存している実測値)と、Safety-critical 8claimの正本定義
# (`SAFETY_CRITICAL_CLAIM_DEFS`、s2c.build_eval_groups()/g6フィクスチャの
# 実データから書き起こした固定の(instance_id, related_fact_id,
# 逐語核心句)の組)とを自動照合し、最終materiality(floor/hook/disclosure-
# gap適用後の実効値)がBLOCKING以外になった箇所を機械的に検出する。
# related_fact_idはinstance内で複数sub_idが共有し得るため(例:
# safety_A5のA5-0/A5-1はともにMUSE-HC-012)、claim_textの逐語核心句との
# 併せ技で誤マッチを避ける(新規fixture捏造なし、既存実データからの
# 逐語引用のみ)。
SAFETY_CRITICAL_CLAIM_DEFS = {
    "bgroup_B3": [
        {"sub_id": "B3", "related_fact_id": "HF-007", "text_substring": "flashy 20% plan"},
    ],
    "safety_A2A3": [
        {"sub_id": "A2A3-0", "related_fact_id": "HF-003", "text_substring": "repay the money"},
    ],
    "safety_A4": [
        {"sub_id": "A4-0", "related_fact_id": "MUSE-HC-006",
         "text_substring": "completed the exchanges with users"},
        {"sub_id": "A4-1", "related_fact_id": "MUSE-HC-012",
         "text_substring": "actually speaking with human staff"},
    ],
    "safety_A5": [
        {"sub_id": "A5-0", "related_fact_id": "MUSE-HC-012",
         "text_substring": "temporarily put back the feature"},
    ],
    "meta_run03_standard": [
        {"sub_id": "Meta-1", "related_fact_id": "MUSE-HC-010",
         "text_substring": "needed user information to continue"},
        {"sub_id": "Meta-2", "related_fact_id": "MUSE-HC-012",
         "text_substring": "needed user information to continue"},
    ],
    "bgroup_B4": [
        {"sub_id": "B4-a", "related_fact_id": "MUSE-HC-002",
         "text_substring": "take over when AI alone has trouble"},
    ],
}


def detect_safety_critical_misdowngrades(instance_results: list) -> list:
    """SAFETY_CRITICAL_CLAIM_DEFSに登録されたinstanceのみを対象に、cycleご
    とのstage2_results実測値から、最終materiality(floor/hook/disclosure-gap
    適用後)がBLOCKING以外になった箇所を機械的に検出する(¥0、新規API呼び
    出しなし、既存run_instance結果jsonへの後処理のみ)。"""
    rows = []
    for r in instance_results:
        defs = SAFETY_CRITICAL_CLAIM_DEFS.get(r.get("instance_id"))
        if not defs:
            continue
        for cycle_idx, c in enumerate(r.get("cycles", [])):
            for sr in c.get("stage2_results", []):
                fact_id = (sr.get("related_fact_id") or "").strip()
                text = sr.get("claim_text") or ""
                for d in defs:
                    if d["related_fact_id"] != fact_id or d["text_substring"] not in text:
                        continue
                    if sr.get("materiality") != "BLOCKING":
                        rows.append({
                            "instance_id": r["instance_id"], "sub_id": d["sub_id"],
                            "cycle_index": cycle_idx, "materiality": sr.get("materiality"),
                            "llm_materiality": sr.get("llm_materiality"),
                            "floor_reason": sr.get("floor_reason"),
                            "claim_text": text,
                        })
    return rows


# ------------------------------------------------------------
# 測定集計(§8-1/§8-2/§8-3/§8-4)
# ------------------------------------------------------------
def aggregate_measurements(instance_results: list) -> dict:
    n = len(instance_results)
    # 委任_33: silent_pass_candidate自動検知(¥0、詳細は関数定義コメント参照)。
    safety_critical_misdowngrade_rows = detect_safety_critical_misdowngrades(instance_results)
    initial_block = sum(1 for r in instance_results if r["final_state"] != "ACCEPTABLE_STAGE1")
    rescreen_auto_resolved = sum(1 for r in instance_results if r["final_state"] == "RESOLVED_STAGE2_DOWNGRADE")
    rewrite_progressed = sum(1 for r in instance_results
                              if any(c.get("rewrite_records") for c in r["cycles"]))
    rewrite_auto_resolved = sum(1 for r in instance_results if r["final_state"] in
                                 ("RESOLVED_REWRITE", "RESOLVED_REWRITE_THEN_DOWNGRADE"))
    final_stop = sum(1 for r in instance_results if r["final_state"] == "STAGE4_ESCALATION")

    # 委任_11 作業B-5是正(§8測定是正、Opus L2 #2論点7「安全≠成功」):
    # 従来はfinal_state=="RESOLVED_REWRITE"限定で集計しており、
    # "RESOLVED_REWRITE_THEN_DOWNGRADE"の5 instance(iter2実測)がどの
    # バケットにも入らず「誤PASS候補0」が未検査のまま報告されていた。
    # 分母をRESOLVED_*全体(RESOLVED_REWRITE+RESOLVED_REWRITE_THEN_
    # DOWNGRADE)へ拡張する。
    _resolved_states = ("RESOLVED_REWRITE", "RESOLVED_REWRITE_THEN_DOWNGRADE")
    true_resolved = sum(1 for r in instance_results if r["final_state"] in _resolved_states
                         and any(c.get("recheck_all_prior_issues_resolved") for c in r["cycles"]))
    quality_pass = sum(1 for r in instance_results if r["final_state"] == "RESOLVED_STAGE2_DOWNGRADE"
                        and any(c["materiality"] == "QUALITY" for c in r["cycles"][0]["stage2_results"]))
    unresolved_unknown = sum(1 for r in instance_results if r["final_state"] in _resolved_states
                              and not any(c.get("recheck_all_prior_issues_resolved") for c in r["cycles"]))

    quality_claims = []
    for r in instance_results:
        for c in r["cycles"]:
            for sr in c.get("stage2_results", []):
                if sr["materiality"] == "QUALITY":
                    quality_claims.append({"instance_id": r["instance_id"], "claim_text": sr["claim_text"]})

    total_calls = sum(r["total_calls"] for r in instance_results)
    total_cost = round(sum(r["total_cost_jpy"] for r in instance_results), 4)
    latencies = sorted(r["elapsed_seconds"] for r in instance_results)

    def percentile(vals, p):
        if not vals:
            return None
        idx = min(len(vals) - 1, int(round(p / 100 * (len(vals) - 1))))
        return vals[idx]

    completion = sum(1 for r in instance_results if r["final_state"] != "STAGE4_ESCALATION")
    retry_count = sum(1 for r in instance_results if any(c.get("rewrite_records") for c in r["cycles"]))
    loop_count = sum(1 for r in instance_results if len(r["cycles"]) >= MAX_CYCLES
                      and any(c.get("rewrite_records") for c in r["cycles"]))

    # S1-U variant集計(委任_10、§4/§9-1、委任_11で改名): screen_used=実際に
    # 1 call追加したinstance数、additional_block=そのうちBLOCKING claimを
    # 新規発見できた件数(旧名caught_recall_miss。「実際にmissを捕捉したか」
    # ではなく「追加BLOCKINGを検出したか」を素直に表す名前へ改名、Opus L2
    # #2論点2)。true/false_positiveは正解ラベル照合(既知recall miss vs
    # negative群)。s1u_extra_cost_jpy=S1-U screen call自体の総コスト
    # (下流Stage2/3コスト増は含まない、別途instance側total_cost_jpyの
    # 差分比較で評価する)。
    s1u_screen_used = sum(1 for r in instance_results if r.get("s1u_screen_used"))
    s1u_additional_block = sum(1 for r in instance_results if r.get("s1u_additional_block"))
    s1u_true_positive = sum(1 for r in instance_results
                             if r.get("s1u_additional_block_label") == "true_positive")
    s1u_false_positive = sum(1 for r in instance_results
                              if r.get("s1u_additional_block_label") == "false_positive")
    s1u_extra_cost = round(sum(
        c.get("cost_jpy", 0.0) for r in instance_results for c in r.get("call_log", [])
        if c.get("recovery_stage") == "stage1_union_screen"
    ), 4)

    # 委任_11 作業B-5(§8測定是正、Opus L2 #2論点5): 群別Escalation率
    # (合成Safety/B群/negativeを分母に混ぜず、実run6 instanceも別枠で出す)。
    group_totals: dict = {}
    for r in instance_results:
        g = r["group"]
        group_totals.setdefault(g, {"n": 0, "escalated": 0})
        group_totals[g]["n"] += 1
        if r["final_state"] == "STAGE4_ESCALATION":
            group_totals[g]["escalated"] += 1
    group_escalation_rates = {
        g: {"n": v["n"], "escalated": v["escalated"],
            "rate": round(v["escalated"] / v["n"], 4) if v["n"] else None}
        for g, v in group_totals.items()
    }
    real_run_results = [r for r in instance_results if r["instance_id"] in REAL_RUN_INSTANCE_IDS]
    real_run_n = len(real_run_results)
    real_run_escalated = sum(1 for r in real_run_results if r["final_state"] == "STAGE4_ESCALATION")
    real_run_escalation_rate = round(real_run_escalated / real_run_n, 4) if real_run_n else None

    # 委任_11 作業B-5(§8測定是正、Opus L2 #2論点6): 記事単位
    # (Standard+Advanced合算)のコスト・合否(ARTICLE_GROUPS参照)。
    by_instance_id = {r["instance_id"]: r for r in instance_results}
    article_aggregates: dict = {}
    for article_id, members in ARTICLE_GROUPS.items():
        present = [by_instance_id[m] for m in members if m in by_instance_id]
        if not present:
            continue
        article_aggregates[article_id] = {
            "members": [r["instance_id"] for r in present],
            "total_cost_jpy": round(sum(r["total_cost_jpy"] for r in present), 4),
            "escalated": any(r["final_state"] == "STAGE4_ESCALATION" for r in present),
        }
    article_costs = [a["total_cost_jpy"] for a in article_aggregates.values()]
    worst_article_cost = max(article_costs) if article_costs else None

    # 委任_11 作業B-6(§4 Rewrite由来新規逸脱検出集計、Opus L2 #2論点4): 決定論
    # precheckの新規finding件数、JA↔EN等価チェックのverdict内訳(測定専用、
    # flow制御には使っていない)。
    rewrite_new_precheck_findings_total = sum(
        c.get("rewrite_new_precheck_findings_count", 0) for r in instance_results for c in r["cycles"])
    ja_en_equivalence_verdicts = [
        c.get("ja_en_equivalence_verdict") for r in instance_results for c in r["cycles"]
        if "ja_en_equivalence_verdict" in c
    ]
    ja_en_equivalence_fail_count = sum(1 for v in ja_en_equivalence_verdicts if v == "FAIL")
    ja_en_equivalence_review_required_count = sum(
        1 for v in ja_en_equivalence_verdicts if v == "REVIEW_REQUIRED")
    unconfirmed_after_reverify_count = sum(
        1 for r in instance_results if r.get("stage4_reason") == "unconfirmed_after_reverify")

    return {
        "n_instances": n,
        "self_recovery_6": {
            "initial_block_count": initial_block,
            "rescreening_auto_resolved_count": rescreen_auto_resolved,
            "rewrite_progressed_count": rewrite_progressed,
            "rewrite_auto_resolved_count": rewrite_auto_resolved,
            "final_stop_count": final_stop,
            "user_decision_required_count": final_stop,
        },
        "escalation_zero_breakdown": {
            "true_resolved_all_prior_issues_resolved_true": true_resolved,
            "quality_pass": quality_pass,
            "all_prior_issues_resolved_unconfirmed": unresolved_unknown,
            # 委任_33(design書§8-x): 旧実装は常に0固定の非稼働プレース
            # ホルダだった(委任_32 REPORT§30-3Cで開示)。
            # SAFETY_CRITICAL_CLAIM_DEFSとの自動照合に置換する。
            "silent_pass_candidate": len({
                (row["instance_id"], row["sub_id"])
                for row in safety_critical_misdowngrade_rows
            }),
            "silent_pass_candidate_rows": safety_critical_misdowngrade_rows,
        },
        "quality_claims": quality_claims,
        "qcd": {
            "total_calls": total_calls, "total_cost_jpy": total_cost,
            "avg_cost_per_instance_jpy": round(total_cost / n, 4) if n else 0,
            "latency_p50": percentile(latencies, 50), "latency_p95": percentile(latencies, 95),
            "completion_rate": round(completion / n, 4) if n else 0,
            "retry_rate": round(retry_count / n, 4) if n else 0,
            "loop_rate": round(loop_count / n, 4) if n else 0,
        },
        "final_stop_reasons": [r["stage4_reason"] for r in instance_results if r["stage4_reason"]],
        "s1u_variant": {
            "screen_used_count": s1u_screen_used, "additional_block_count": s1u_additional_block,
            "additional_block_true_positive_count": s1u_true_positive,
            "additional_block_false_positive_count": s1u_false_positive,
            "extra_cost_jpy": s1u_extra_cost,
        },
        "group_escalation_rates": group_escalation_rates,
        "real_run": {
            "n": real_run_n, "escalated": real_run_escalated, "rate": real_run_escalation_rate,
        },
        "article_level": {
            "aggregates": article_aggregates, "worst_cost_jpy": worst_article_cost,
        },
        "rewrite_deviation_qa": {
            "rewrite_new_precheck_findings_total": rewrite_new_precheck_findings_total,
            "ja_en_equivalence_calls": len(ja_en_equivalence_verdicts),
            "ja_en_equivalence_fail_count": ja_en_equivalence_fail_count,
            "ja_en_equivalence_review_required_count": ja_en_equivalence_review_required_count,
            "unconfirmed_after_reverify_count": unconfirmed_after_reverify_count,
        },
        "iter4_additional_measures": _iter4_additional_measures(instance_results),
        "iter5_additional_measures": _iter5_additional_measures(instance_results),
        "iter6_additional_measures": _iter6_additional_measures(instance_results),
    }


# ------------------------------------------------------------
# 委任_12(iteration4、§8追加測定7項目)。既存measurementに影響を与えない
# 追加ブロックとして分離する(既存key/値は変更しない)。
# ------------------------------------------------------------
def _iter4_additional_measures(instance_results: list) -> dict:
    normal_present = [r for r in instance_results if r["instance_id"] in NORMAL_GROUP_INSTANCE_IDS]
    unnecessary_rewrite = [r for r in normal_present if any(c.get("rewrite_records") for c in r["cycles"])]
    stage1_false_block = [r for r in normal_present if r["final_state"] != "ACCEPTABLE_STAGE1"]
    stage2_false_block_claims = 0
    for r in normal_present:
        for c in r["cycles"]:
            stage2_false_block_claims += sum(
                1 for sr in c.get("stage2_results", []) if sr["materiality"] == "BLOCKING")

    degradation_candidates = []
    for r in instance_results:
        for ci, c in enumerate(r["cycles"], start=1):
            for lang_key in ("quality_degradation_en", "quality_degradation_ja"):
                qd = c.get(lang_key)
                if qd and qd.get("degradation_candidate"):
                    degradation_candidates.append({
                        "instance_id": r["instance_id"], "cycle": ci, "lang": lang_key.split("_")[-1],
                    })

    rewrite_op_total = sum(len(c.get("rewrite_records", [])) for r in instance_results for c in r["cycles"])
    rewrite_op_by_article: dict = {}
    by_instance_id = {r["instance_id"]: r for r in instance_results}
    grouped_members = {m for members in ARTICLE_GROUPS.values() for m in members}
    for article_id, members in ARTICLE_GROUPS.items():
        present = [by_instance_id[m] for m in members if m in by_instance_id]
        if not present:
            continue
        rewrite_op_by_article[article_id] = sum(
            len(c.get("rewrite_records", [])) for r in present for c in r["cycles"])
    for r in instance_results:
        if r["instance_id"] in grouped_members:
            continue
        cnt = sum(len(c.get("rewrite_records", [])) for c in r["cycles"])
        if cnt:
            rewrite_op_by_article[r["instance_id"]] = cnt
    n_articles = len(rewrite_op_by_article) if rewrite_op_by_article else 0
    rewrite_op_per_article_avg = (
        round(sum(rewrite_op_by_article.values()) / n_articles, 4) if n_articles else 0.0
    )

    stage4_reason_breakdown: dict = {}
    for r in instance_results:
        if r.get("stage4_reason"):
            stage4_reason_breakdown[r["stage4_reason"]] = stage4_reason_breakdown.get(r["stage4_reason"], 0) + 1

    return {
        "normal_group_note": (
            "『正常記事』= negative候補7件+Normal群2件(hormuz_run03_advanced/"
            "meta_run03_advanced)。§7-0でinstance内claimが全てACCEPTABLE"
            "であることが期待される群に限定(B/Safety群はclaim単位で"
            "BLOCKING/非BLOCKINGが混在するためinstance単位のこの指標には"
            "含めない、限界として明記)。"
        ),
        "unnecessary_rewrite": {
            "n_normal_group": len(normal_present),
            "count": len(unnecessary_rewrite),
            "rate": round(len(unnecessary_rewrite) / len(normal_present), 4) if normal_present else None,
            "instance_ids": [r["instance_id"] for r in unnecessary_rewrite],
        },
        "natural_interpretation_blocked": {
            "stage1_false_block_count": len(stage1_false_block),
            "stage1_false_block_instance_ids": [r["instance_id"] for r in stage1_false_block],
            "stage2_false_block_claim_count": stage2_false_block_claims,
        },
        "rewrite_quality_degradation_candidates": {
            "count": len(degradation_candidates), "detail": degradation_candidates,
        },
        "rewrite_operations": {
            "total": rewrite_op_total, "per_article_avg": rewrite_op_per_article_avg,
            "by_article": rewrite_op_by_article,
        },
        "stage4_reason_breakdown": stage4_reason_breakdown,
    }


# ------------------------------------------------------------
# 委任_13(iteration5、追加7項目)。既存iter4_additional_measuresには
# 影響を与えない追加ブロックとして分離する。
# ------------------------------------------------------------
# Opus L2レビュー#3論点3実測: neg5でRewriteされたclaim("Concerns about
# US-Iran attacks, the sea blockade, and tanker safety continued on July
# 14. So the flashy 20% plan left the stage.")は、正解BLOCKINGのB3
# ("...links the continuing concerns causally to the plan's withdrawal.")
# と同一文であり、「不要Rewrite」に数えるのはプロジェクト自身の再ラベル
# 表と矛盾する(§7-0是正)。iter4の`unnecessary_rewrite`(v1、分子に
# neg5を含む)は変更せず残し、本ブロックで是正後の分子(v2、neg5を除外)を
# 別途報告する。
UNNECESSARY_REWRITE_V2_EXCLUDE_INSTANCE_IDS = frozenset({"neg5_hormuz_div_a2"})


def _iter5_additional_measures(instance_results: list) -> dict:
    normal_present = [r for r in instance_results if r["instance_id"] in NORMAL_GROUP_INSTANCE_IDS]
    unnecessary_rewrite_v1 = [r for r in normal_present if any(c.get("rewrite_records") for c in r["cycles"])]
    unnecessary_rewrite_v2 = [r for r in unnecessary_rewrite_v1
                               if r["instance_id"] not in UNNECESSARY_REWRITE_V2_EXCLUDE_INSTANCE_IDS]

    qd_v2_dup = qd_v2_orphan = qd_v2_vocab = qd_v2_needs_regen = qd_v2_regenerated = 0
    qd_v2_regen_resolved = 0
    qd_v2_detail = []
    for r in instance_results:
        for ci, c in enumerate(r["cycles"], start=1):
            qd = c.get("quality_degradation_v2")
            if not qd:
                continue
            if qd.get("duplicate_paragraph_detected"):
                qd_v2_dup += 1
            if qd.get("orphan_contrastive_detected"):
                qd_v2_orphan += 1
            if qd.get("vocab_difficulty_increased"):
                qd_v2_vocab += 1
            if qd.get("needs_regeneration"):
                qd_v2_needs_regen += 1
                qd_v2_detail.append({"instance_id": r["instance_id"], "cycle": ci, "reasons": qd.get("reasons")})
            if c.get("quality_degradation_v2_regenerated"):
                qd_v2_regenerated += 1
                qd_after = c.get("quality_degradation_v2_after_regen") or {}
                if not qd_after.get("needs_regeneration"):
                    qd_v2_regen_resolved += 1

    two_of_two_triggered = 0
    two_of_two_downgraded = 0
    two_of_two_confirmed_blocking = 0
    for r in instance_results:
        for c in r["cycles"]:
            log = c.get("stage2_two_of_two_log") or []
            two_of_two_triggered += len(log)
            for entry in log:
                if entry["two_of_two_result"].startswith("DOWNGRADED"):
                    two_of_two_downgraded += 1
                else:
                    two_of_two_confirmed_blocking += 1

    cite_or_release_triggered = 0
    cite_or_release_released_total = 0
    for r in instance_results:
        for c in r["cycles"]:
            released = c.get("recheck_confirm_cite_or_release_released_count")
            if released is not None:
                cite_or_release_triggered += 1
                cite_or_release_released_total += released

    return {
        "unnecessary_rewrite_v2_corrected": {
            "n_normal_group": len(normal_present),
            "count_v1_uncorrected": len(unnecessary_rewrite_v1),
            "count_v2_corrected": len(unnecessary_rewrite_v2),
            "rate_v2_corrected": (
                round(len(unnecessary_rewrite_v2) / len(normal_present), 4) if normal_present else None
            ),
            "instance_ids_v2": [r["instance_id"] for r in unnecessary_rewrite_v2],
            "excluded_as_duplicate_of_blocking": sorted(UNNECESSARY_REWRITE_V2_EXCLUDE_INSTANCE_IDS
                                                          & {r["instance_id"] for r in unnecessary_rewrite_v1}),
        },
        "quality_degradation_v2": {
            "duplicate_paragraph_detected_count": qd_v2_dup,
            "orphan_contrastive_detected_count": qd_v2_orphan,
            "vocab_difficulty_increased_count": qd_v2_vocab,
            "needs_regeneration_count": qd_v2_needs_regen,
            "needs_regeneration_detail": qd_v2_detail,
            "regenerated_count": qd_v2_regenerated,
            "regenerated_and_resolved_count": qd_v2_regen_resolved,
        },
        "stage2_two_of_two": {
            "triggered_claim_count": two_of_two_triggered,
            "downgraded_count": two_of_two_downgraded,
            "confirmed_blocking_count": two_of_two_confirmed_blocking,
        },
        "cite_or_release": {
            "confirm_calls_with_field": cite_or_release_triggered,
            "released_count_total": cite_or_release_released_total,
        },
    }


# ------------------------------------------------------------
# 委任_14(iteration6、2026-09-30ユーザー新方針item8/9): 不要Rewrite内訳・
# 最小変更ラダー段別分布・セクション役割違反・Hook-aware由来BLOCK回避・
# 丸め誤検出回避・floor-strict/cited比較・記事単位コスト5分割。
# ------------------------------------------------------------
def compute_cost_breakdown_5way(instance_results: list) -> dict:
    """委任_14 B-6(item9): 記事単位(instance単位、既存article-level合算
    [ARTICLE_GROUPS]とは別枠、instance粒度)のRewiteなし平均/あり平均/
    Rewrite率/全記事平均/worstを算出する(¥0、既存total_cost_jpy/
    rewrite_recordsの再集計のみ、新規API呼び出しなし)。"""
    with_rewrite = []
    without_rewrite = []
    for r in instance_results:
        had_rewrite = any(c.get("rewrite_records") for c in r.get("cycles", []))
        (with_rewrite if had_rewrite else without_rewrite).append(r["total_cost_jpy"])
    all_costs = with_rewrite + without_rewrite
    n = len(all_costs)

    def _avg(vals):
        return round(sum(vals) / len(vals), 4) if vals else None

    return {
        "n_instances": n,
        "no_rewrite_count": len(without_rewrite), "no_rewrite_avg_cost_jpy": _avg(without_rewrite),
        "with_rewrite_count": len(with_rewrite), "with_rewrite_avg_cost_jpy": _avg(with_rewrite),
        "rewrite_rate": round(len(with_rewrite) / n, 4) if n else None,
        "overall_avg_cost_jpy": _avg(all_costs),
        "worst_cost_jpy": max(all_costs) if all_costs else None,
    }


def _iter6_additional_measures(instance_results: list) -> dict:
    normal_present = [r for r in instance_results if r["instance_id"] in NORMAL_GROUP_INSTANCE_IDS]
    unnecessary_rewrite_v1 = [r for r in normal_present if any(c.get("rewrite_records") for c in r["cycles"])]
    unnecessary_rewrite_v2 = [r for r in unnecessary_rewrite_v1
                               if r["instance_id"] not in UNNECESSARY_REWRITE_V2_EXCLUDE_INSTANCE_IDS]

    # ラダー段別分布(委任_14 item7/8): 実際にRewriteが試行されたclaim単位で、
    # どの水準で解消したか(0_delete/1_word_connective/3_sentence/4_paragraph/
    # 6_full_article/paired_j1_not_laddered)を集計する。
    ladder_distribution: dict = {}
    for r in instance_results:
        for c in r["cycles"]:
            for rec in c.get("rewrite_records", []):
                lvl = rec.get("ladder_level_used") or "unresolved_or_api_failure"
                ladder_distribution[lvl] = ladder_distribution.get(lvl, 0) + 1

    # セクション役割違反(委任_14 B-4)
    role_violation_count = 0
    role_violation_detail = []
    for r in instance_results:
        for ci, c in enumerate(r["cycles"], start=1):
            sr = c.get("section_role_violation")
            if sr and sr.get("section_role_violated"):
                role_violation_count += 1
                role_violation_detail.append({
                    "instance_id": r["instance_id"], "cycle": ci, "reasons": sr.get("reasons"),
                })

    # Hook-aware由来BLOCK回避件数(委任_14 B-5)
    hook_aware_downgrade_count = 0
    hook_aware_detail = []
    for r in instance_results:
        for c in r["cycles"]:
            for sr in c.get("stage2_results", []):
                if sr.get("floor_reason") == "hook_aware_scope_downgrade":
                    hook_aware_downgrade_count += 1
                    hook_aware_detail.append({
                        "instance_id": r["instance_id"], "section_type": sr.get("section_type"),
                        "claim_text": sr.get("claim_text", "")[:80],
                    })

    # 丸め誤検出回避件数(委任_14 B-1): dev内でchanged_number_suppressed_
    # reasonが記録されたclaim(floor評価直前にchanged_numberを除外した件数)。
    rounding_suppressed_count = 0
    for r in instance_results:
        for c in r["cycles"]:
            for sr in c.get("stage2_results", []):
                if sr.get("dev", {}).get("changed_number_suppressed_reason"):
                    rounding_suppressed_count += 1

    # floor-strict vs floor-cited比較(委任_14 B-2)。Safety群(group=="safety"、
    # 12 instance)を対象にhard gate(false-negative候補0)を確認する。
    # 「false-negative候補」= floor-strictはdeterministic floorで発火した
    # (floor_reason startswith "deterministic_floor:")が、floor-citedは
    # 発火せず(floor_cited_reason is None)、かつLLM自体の判定
    # (llm_materiality)もBLOCKINGではなかった(floor無しではQUALITY/
    # ACCEPTABLEへ抜ける)claim。
    floor_divergence_all = []
    floor_divergence_safety = []
    for r in instance_results:
        for c in r["cycles"]:
            for sr in c.get("stage2_results", []):
                fr = sr.get("floor_reason") or ""
                if not fr.startswith("deterministic_floor:"):
                    continue
                if sr.get("floor_cited_reason") is not None:
                    continue
                if sr.get("llm_materiality") == "BLOCKING":
                    continue
                entry = {"instance_id": r["instance_id"], "group": r["group"],
                         "claim_text": sr.get("claim_text", "")[:100], "floor_reason": fr}
                floor_divergence_all.append(entry)
                if r["group"] == "safety":
                    floor_divergence_safety.append(entry)

    return {
        "unnecessary_rewrite_v3": {
            "n_normal_group": len(normal_present),
            "count": len(unnecessary_rewrite_v2),
            "rate": round(len(unnecessary_rewrite_v2) / len(normal_present), 4) if normal_present else None,
            "instance_ids": [r["instance_id"] for r in unnecessary_rewrite_v2],
        },
        "ladder_level_distribution": ladder_distribution,
        "section_role_violation": {
            "count": role_violation_count, "detail": role_violation_detail,
        },
        "hook_aware_downgrade": {
            "count": hook_aware_downgrade_count, "detail": hook_aware_detail,
        },
        "rounding_false_positive_suppressed_count": rounding_suppressed_count,
        "floor_variant_comparison": {
            "false_negative_candidates_all_groups": len(floor_divergence_all),
            "false_negative_candidates_safety_group": len(floor_divergence_safety),
            "safety_group_hard_gate_passed": len(floor_divergence_safety) == 0,
            "detail_safety_group": floor_divergence_safety,
            "detail_all_groups": floor_divergence_all,
        },
        "cost_breakdown_5way": compute_cost_breakdown_5way(instance_results),
    }


def compute_s1u_counterfactual(instance_results: list) -> dict:
    """委任_12(iteration4、§2項目6): S1-Uが付加したclaimを除外した反実仮想
    を0 callで算出する。S1-Uはstage1_parsedがACCEPTABLE(PASS)の場合のみ
    発火し、s1u_additional_block=Trueのinstanceはs1u_result由来claimのみで
    以降の全cascadeが発生している(run_instance実装、S1-U発火条件参照)。
    よって「S1-Uが無かった場合」は当該instanceが丸ごとACCEPTABLE_STAGE1
    (cost 0、call 0)だったと機械的に置換できる(新規APIコール無し)。"""
    counterfactual = []
    for r in instance_results:
        if r.get("s1u_additional_block"):
            counterfactual.append({
                **r, "final_state": "ACCEPTABLE_STAGE1", "stage4_reason": None, "cycles": [],
                "call_log": [], "total_cost_jpy": 0.0, "total_calls": 0,
                "s1u_screen_used": False, "s1u_additional_blocking_count": 0,
                "s1u_additional_block": False, "s1u_additional_block_label": None,
            })
        else:
            counterfactual.append(r)
    with_s1u = aggregate_measurements(instance_results)
    without_s1u = aggregate_measurements(counterfactual)
    return {
        "with_s1u": {
            "final_stop_count": with_s1u["self_recovery_6"]["final_stop_count"],
            "real_run_escalation_rate": with_s1u["real_run"]["rate"],
            "group_escalation_rates": with_s1u["group_escalation_rates"],
            "total_cost_jpy": with_s1u["qcd"]["total_cost_jpy"],
        },
        "without_s1u_counterfactual": {
            "final_stop_count": without_s1u["self_recovery_6"]["final_stop_count"],
            "real_run_escalation_rate": without_s1u["real_run"]["rate"],
            "group_escalation_rates": without_s1u["group_escalation_rates"],
            "total_cost_jpy": without_s1u["qcd"]["total_cost_jpy"],
        },
        "instances_removed_by_counterfactual": [
            r["instance_id"] for r in instance_results if r.get("s1u_additional_block")
        ],
        "known_recall_miss_instances_among_removed": sorted(
            KNOWN_RECALL_MISS_INSTANCE_IDS & {
                r["instance_id"] for r in instance_results if r.get("s1u_additional_block")
            }
        ),
    }


# ------------------------------------------------------------
# 委任_13(iteration5、n=2実測): Opus L2レビュー#3論点6-A(iv)「iter4の
# フロー実測はn=1に戻っており、real_run Escalation 0%という改善はrun間
# 分散の範囲内で説明でき、証明になっていない」への対応。29 instanceを
# sample1/sample2の2回独立実行し(Stage1はsha256一致で再利用、Stage2/
# Stage3の非決定性のみが両sample間の差を生む)、instance単位final_state
# 一致率・群別Escalation率のWilson CI・記事単位costのsample間最大値を
# 算出する。
# ------------------------------------------------------------
def wilson_score_interval(successes: int, n: int, z: float = 1.96) -> tuple:
    if n == 0:
        return (0.0, 0.0)
    phat = successes / n
    denom = 1 + (z ** 2) / n
    center = phat + (z ** 2) / (2 * n)
    margin = z * ((phat * (1 - phat) / n + (z ** 2) / (4 * n ** 2)) ** 0.5)
    lo = max(0.0, (center - margin) / denom)
    hi = min(1.0, (center + margin) / denom)
    return (round(lo, 4), round(hi, 4))


def combine_n2_measures(sample_results_list: list) -> dict:
    """sample_results_list: [sample1_instance_results, sample2_instance_results]
    (各要素は同一29 instanceのunsuffixed instance_idを持つ独立run結果)。"""
    by_id_per_sample = [{r["instance_id"]: r for r in results} for results in sample_results_list]
    all_ids = sorted(by_id_per_sample[0].keys())

    per_instance_agreement = []
    for iid in all_ids:
        states = [by_id.get(iid, {}).get("final_state") for by_id in by_id_per_sample]
        per_instance_agreement.append({
            "instance_id": iid, "final_states_by_sample": states,
            "agreed": len(set(states)) == 1,
        })
    agreement_count = sum(1 for a in per_instance_agreement if a["agreed"])
    agreement_rate = round(agreement_count / len(all_ids), 4) if all_ids else None

    # 群別Escalation率(sample1+sample2を合算した分母・分子、Wilson CI付き)。
    group_of: dict = {}
    for by_id in by_id_per_sample:
        for iid, r in by_id.items():
            group_of[iid] = r["group"]
    group_escalation_combined: dict = {}
    for group in sorted(set(group_of.values())):
        escalated = 0
        total = 0
        for by_id in by_id_per_sample:
            for iid, r in by_id.items():
                if group_of.get(iid) != group:
                    continue
                total += 1
                if r["final_state"] == "STAGE4_ESCALATION":
                    escalated += 1
        lo, hi = wilson_score_interval(escalated, total) if total else (0.0, 0.0)
        group_escalation_combined[group] = {
            "escalated": escalated, "total": total,
            "rate": round(escalated / total, 4) if total else None,
            "wilson_ci_95": [lo, hi],
        }

    # real_run(6 instance×2 sample=12)のEscalation率(iter3-iv是正対応)。
    real_run_escalated = sum(
        1 for by_id in by_id_per_sample for iid, r in by_id.items()
        if iid in REAL_RUN_INSTANCE_IDS and r["final_state"] == "STAGE4_ESCALATION"
    )
    real_run_total = sum(1 for by_id in by_id_per_sample for iid in by_id if iid in REAL_RUN_INSTANCE_IDS)
    real_run_lo, real_run_hi = wilson_score_interval(real_run_escalated, real_run_total) if real_run_total else (0.0, 0.0)

    # 記事単位cost(worst、2 sample中の最大値)。既存article_level集計を
    # 各sampleへ適用し、article_idごとの最大costを取る(Cap余裕の保守評価)。
    per_sample_article_costs: dict = {}
    for by_id in by_id_per_sample:
        grouped_members = {m for members in ARTICLE_GROUPS.values() for m in members}
        for article_id, members in ARTICLE_GROUPS.items():
            present = [by_id[m] for m in members if m in by_id]
            if not present:
                continue
            cost = round(sum(r["total_cost_jpy"] for r in present), 4)
            per_sample_article_costs.setdefault(article_id, []).append(cost)
        for iid, r in by_id.items():
            if iid in grouped_members:
                continue
            per_sample_article_costs.setdefault(iid, []).append(r["total_cost_jpy"])
    worst_article_cost_across_samples = (
        max((max(v) for v in per_sample_article_costs.values()), default=0.0)
    )

    # 委任_14(iteration6、item9): sample1+sample2を合算したinstance_resultsで
    # 不要Rewrite率v3・ラダー段別分布・セクション役割違反・Hook-aware・
    # floor-strict/cited比較・コスト5分割を算出する(n=2結合、非決定性の
    # 影響を1回のrunよりも安定的に見るため)。
    combined_instance_results = [r for results in sample_results_list for r in results]
    iter6_combined = _iter6_additional_measures(combined_instance_results) if combined_instance_results else {}

    return {
        "n_samples": len(sample_results_list),
        "per_instance_final_state_agreement": {
            "agreement_count": agreement_count, "n_instances": len(all_ids), "rate": agreement_rate,
            "disagreements": [a for a in per_instance_agreement if not a["agreed"]],
        },
        "group_escalation_rates_combined_wilson_ci": group_escalation_combined,
        "real_run_combined": {
            "escalated": real_run_escalated, "total": real_run_total,
            "rate": round(real_run_escalated / real_run_total, 4) if real_run_total else None,
            "wilson_ci_95": [real_run_lo, real_run_hi],
        },
        "article_level_cost_worst_across_samples": {
            "worst_cost_jpy": worst_article_cost_across_samples,
            "by_article_per_sample": per_sample_article_costs,
        },
        "iter6_additional_measures_combined": iter6_combined,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--groups", default="safety,b_group,meta,hormuz,negative",
                         help="comma-separated subset of safety,b_group,meta,hormuz,negative")
    parser.add_argument("--n_runs", type=int, default=1,
                         help="委任_13(iteration5): 2を指定すると29 instanceをsample1/"
                              "sample2で独立に2回実行する(Stage1はsha256一致で再利用、"
                              "instances_s1//instances_s2へ別保存、既定1=iter4互換)")
    parser.add_argument("--resume", action="store_true",
                         help="既に er052_output/.../instances/<id>.json が存在するinstanceは"
                              "再実行せずキャッシュ結果を再利用する(重複課金防止)")
    parser.add_argument("--s1u", action="store_true",
                         help="委任_10 S1-U variant: s1u_eligibleなinstanceがStage1(V4A)で"
                              "ACCEPTABLEだった場合、S1-D 1 callを追加してBLOCKING claimを"
                              "union(fail-closed)で拾う(recall対策の実測、既定は無効)")
    parser.add_argument("--instance_ids", default=None,
                         help="委任_20 W4: comma-separated instance_id allowlist。指定時は"
                              "--groupsフィルタ後にさらにこのIDへ絞り込む(既定None=無効、"
                              "既存呼び出しの挙動は変えない)")
    parser.add_argument("--force_fresh_stage1", default=None,
                         help="委任_20 W4: comma-separated instance_id list。指定された"
                              "instanceのstage1_modeを'fresh'へ上書きする(既定reuseの"
                              "instanceでもW2[同一fact_id列挙]を検証するためStage1を新規"
                              "実行させる、既定None=無効)")
    args = parser.parse_args()
    selected_groups = {g.strip() for g in args.groups.split(",") if g.strip()}
    selected_instance_ids = (
        {s.strip() for s in args.instance_ids.split(",") if s.strip()} if args.instance_ids else None
    )
    force_fresh_stage1_ids = (
        {s.strip() for s in args.force_fresh_stage1.split(",") if s.strip()} if args.force_fresh_stage1 else set()
    )

    client = vfl01.get_client()
    state = load_budget_state()
    consecutive_errors = [0]

    instances = [inst for inst in build_target_instances() if inst["group"] in selected_groups]
    if selected_instance_ids is not None:
        instances = [inst for inst in instances if inst["instance_id"] in selected_instance_ids]
    for inst in instances:
        if inst["instance_id"] in force_fresh_stage1_ids:
            inst["stage1_mode"] = "fresh"
            inst["stage1_source"] = None
    # 委任_13(iteration5): stage1_cacheはsample1/sample2間で共有する
    # (Stage1[fresh mode]はcycle1入力が同一である限りsha256一致で再利用、
    # 二重課金防止)。--n_runs=1(既定)ではiter1〜4と同じ挙動(cache自体は
    # 作るが同一sample内でのみ参照されるため実質無効化)。
    stage1_cache: dict = {}
    stopped, stop_reason = False, None
    sample_instance_results: list = []  # [[sample1の29件], [sample2の29件], ...]

    for sample_idx in range(1, args.n_runs + 1):
        subdir = "instances" if args.n_runs == 1 else f"instances_s{sample_idx}"
        instance_results = []
        for inst in instances:
            cache_path = f"{OUT_DIR}/{subdir}/{inst['instance_id']}.json"
            if args.resume and os.path.exists(cache_path):
                with open(cache_path, encoding="utf-8") as f:
                    instance_results.append(json.load(f))
                continue
            try:
                result = run_instance(client, state, consecutive_errors, inst, enable_s1u=args.s1u,
                                       stage1_cache=stage1_cache, instances_subdir=subdir)
                instance_results.append(result)
            except TrialAbort as e:
                stopped = True
                stop_reason = str(e)
                break
        sample_instance_results.append(instance_results)
        if stopped:
            break

    # 後方互換: 既存iter1〜4のsummary構造(measurements/s1u_counterfactual)は
    # sample1の結果に対して算出する(--n_runs=1なら従来と完全に同一)。
    instance_results = sample_instance_results[0] if sample_instance_results else []
    measurements = aggregate_measurements(instance_results) if instance_results else {}
    s1u_counterfactual = compute_s1u_counterfactual(instance_results) if instance_results else {}

    # 委任_13(iteration5、n=2実測): sample2が完走している場合のみ算出する
    # (--n_runs=1、またはsample2がTrialAbortで未完走の場合はNone)。
    n2_combined = None
    measurements_per_sample = None
    if len(sample_instance_results) >= 2 and all(
            len(r) == len(instances) for r in sample_instance_results[:2]):
        n2_combined = combine_n2_measures(sample_instance_results[:2])
        measurements_per_sample = [
            aggregate_measurements(sample_instance_results[0]),
            aggregate_measurements(sample_instance_results[1]),
        ]

    summary = {
        "stopped": stopped, "stop_reason": stop_reason,
        "n_runs": args.n_runs,
        "n_instances_completed": len(instance_results),
        "n_instances_planned": len(instances),
        "cumulative_jpy": round(state["cumulative_jpy"], 4),
        "cumulative_calls": state["cumulative_calls"],
        "cumulative_errors": state["cumulative_errors"],
        "measurements": measurements,
        "s1u_counterfactual": s1u_counterfactual,
        "n2_combined": n2_combined,
    }
    save_json(f"{OUT_DIR}/summary_flow_runner.json", {
        "summary": summary,
        "instance_results_sample1": [
            {k: v for k, v in r.items() if k != "call_log"} for r in instance_results
        ],
        "instance_results_sample2": (
            [{k: v for k, v in r.items() if k != "call_log"} for r in sample_instance_results[1]]
            if len(sample_instance_results) >= 2 else None
        ),
        "measurements_sample2": measurements_per_sample[1] if measurements_per_sample else None,
    })
    # 委任_12(iteration4で実際に発生・修正): summary_flow_runner.jsonへの
    # 保存(save_json、UTF-8ファイル出力)は完了しているが、Windowsコンソール
    # (cp932)への標準出力printがensure_ascii=Falseだと一部の日本語記号で
    # UnicodeEncodeErrorを起こし、そこでプロセスが異常終了する実害があった
    # (本委任で実際に発生、証跡ファイル自体は既に保存済みで無事)。
    # コンソール表示のみensure_ascii=Trueへ変更する(保存物には影響しない)。
    print(json.dumps({k: v for k, v in summary.items() if k not in ("measurements", "n2_combined")},
                      ensure_ascii=True, indent=2))
    print(json.dumps(measurements, ensure_ascii=True, indent=2))
    if n2_combined:
        print(json.dumps(n2_combined, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
