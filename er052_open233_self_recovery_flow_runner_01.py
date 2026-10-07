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
import collections
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
import er052_open233_stage1_coverage_checker_01 as cov  # 委任_06: Stage 1再設計(Trial、既定legacy_v4a=不変)
import er052_open233_stage1_reclassify_01 as reclf  # 委任_04(CHECKER-FLOOR-PRODUCTION-E2E-01): Checker再分類(4観点)。既定OFF
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
# 委任_42(rep22、2026-10-02、受け渡し修正[Checkerの違反範囲をそのままRewriteへ]
# の限定Trial): 既存rep7〜21の出力は変更せず、新規ディレクトリ(`_rep22`)へ書く。
OUT_DIR_REP22 = "er052_output/open233_self_recovery_flow_runner_01_rep22"
OUT_DIR = OUT_DIR_REP22
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233an_42_rep22.json"
TOTAL_BUDGET_JPY = 14.5  # 委任_42 Guardrail¥15のうち、¥0.5をhard marginとして
# 残し、本runnerのAPI呼び出し全体(rep22のT1/T2/T3)を¥14.5で自己停止する
# (委任_36までの¥6.5/¥7と同じ構成。暴走疑い時のみSTOP、T-3方針)。
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

# 委任_42(2026-10-02、OPEN-233 受け渡し修正、ユーザー指示§1): Rewrite対象の
# 決定方式の切替(Trial専用。Production正式pathには存在しない定数)。
# - "violation_span"(既定=新方式): Checkerが返した違反箇所(claim_in_article、
#   runner内ではclaim_text)だけを入力に、文字単位の照合(L0〜L4、ちょうど1箇所)
#   で記事側の範囲を確定し、その範囲をそのままRewriteへ渡す。照合できない指摘は
#   類似度・単語重なり・判定役の引用へ落とさず、新reason
#   `violation_span_unverified`でStage 4(人間確認、fail-closed)にする。
# - "legacy"(旧方式): 委任_36までの`locate_target`(判定役hint引用→包含スパン→
#   類似度→単語重なり)。比較・切り戻し用に残す(対象決定の既定経路からは呼ばれない)。
HANDOFF_MODE_VIOLATION_SPAN = "violation_span"
HANDOFF_MODE_LEGACY = "legacy"
HANDOFF_MODE = HANDOFF_MODE_VIOLATION_SPAN

# 委任_49(Opus独立レビュー#6後のFable採否、設計書§2-1・§2-2・§5): すべてTrial専用スイッチ、
# 既定=現行の挙動(委任_42の照合・日本語と英語の両方を扱う方式)のまま。Productionに存在しない。
# - VS_MATCH_EXT(既定False): Trueなら照合に次の3点を足す。(1)A1 末尾句読点(L5_edge_punct、
#   L0〜L4で確定しなかった場合に限り、両端の`. , ; : ! ?`を除いた文字列が英語本文にちょうど1箇所)
#   (2)A2-a 位置ラベル(確定範囲が構造ラベル行そのものなら確定不能`label_only`)
#   (3)単語境界(英語本文への一致は、一致箇所の先頭側・末尾側の両方が単語境界であること。
#   確定が減る方向のみの安全側の条件。日本語本文には適用しない)。
# - JA_MODE(既定"paired"=現行): "english_only"なら`run_instance`冒頭でcurrent_ja_textをNoneにし、
#   日本語側の処理(paired書き換え・JA Recheck・JAガード・日英等価・JA指摘の合流・JA precheck)を
#   迂回する。`fixture["source_article_text"]`は変えない(CheckerとStage 2へは元の日本語を渡し続ける)。
VS_MATCH_EXT = False
JA_MODE_PAIRED = "paired"
JA_MODE_ENGLISH_ONLY = "english_only"
JA_MODE = JA_MODE_PAIRED
# A2-a(委任_49): 記事の構造ラベル行の語彙。`er019_output/`配下のa2/b1b記事21本の見出しをGrepで確認
# したところ、本文ではない区切りの行は`## In one line`の1種類のみ(他は先頭の`# タイトル`行=違反箇所に
# なりうるため対象外、`### 小見出し`=本文の見出し)。ラベル行の定義: 行頭の`#`群と空白を除いた
# 残りが語彙(大文字小文字を同一視)に一致する行。
VS_STRUCTURAL_LABELS = frozenset({"in one line"})
VS_EDGE_PUNCT = ".,;:!?"

# 委任_57(2026-10-03、Opus独立レビュー#7の4ガード付き説明文後段分離「P-strict-closed」、設計書
# design_open233_explanatory_mixed_countermeasures_01.md §5): Trial専用スイッチ、既定False=委任_55時点と同一。
# Productionに存在しない。有効化・Production採用はユーザー承認待ち(`USER_DECISION_REQUIRED`)。
# ONのとき、`_resolve_claim_string`で既存の照合(L0〜L5・label_only)が確定不能(explanatory_mixed/mismatch/
# label_only)だった場合にのみ`vs_explain_split_resolve`を試す(照合経路は`_resolve_claim_string`の1箇所のまま。
# Stage 1初回・Recheck・Rewrite周回・retry・fallbackは全て同じ経路)。規則(英語本文のみ。日本語本文だけでは新たに確定しない):
#   引用符(“ ” " 「」『』)で囲まれた断片を全て取り出し、各断片を英語本文で既存照合(L0〜L3、VS_MATCH_EXT=ONなら
#   L5・単語境界)により「ちょうど1箇所」に確定。引用符の外の残り(各区間)が、(v)位置語(VS_EXPLAIN_POSITION_REJECT_RE。
#   見出し・In one line・冒頭を名指しするものは、どの断片もその要素と重ならなければ拒否)、(iii)対比・参照語
#   (VS_EXPLAIN_CONTRAST_REF_EN_RE/_JA_RE)、(ii)長さ(英語6語以上・日本語11文字以上)、(i)記事本文の3語以上の逐語、
#   (iv)記事内で断片の直前・直後に逐語で連続、のいずれにも当たらないときだけ採用。断片なし・不一致・複数一致・
#   閉じ忘れ・入れ子・構造ラベルだけ・上記のいずれかに該当は確定不能(`explain_split_rejected:<理由>`)。
VS_EXPLAIN_SPLIT = False
# 委任_66(2026-10-04、Opus独立レビュー#9[条件A]のFable採否に基づくL6「完結文復元」、設計書
# design_open233_span_sentence_restore_01.md §4・§6): Trial専用スイッチ、既定False=委任_65時点と同一。
# Productionに存在しない。有効化・Production採用はユーザー承認待ち(`USER_DECISION_REQUIRED`)。
# ONのとき(かつVS_MATCH_EXT=ON、英語本文のみ)、`_resolve_claim_string`でL0〜L5・P-strict-closedの
# いずれでも確定しなかったclaim(mismatch/explanatory_mixed)にだけ`vs_sentence_restore_resolve`(決定論、
# 追加LLM callなし)を試す。断片が途中切断・省略記号・Checkerが記事にない語を1〜6語混ぜた型で、断片(または
# 逐語で一意な連続語列[アンカー])を含む完結文(最大2文)が記事内で一意に決まるときだけ、その文を範囲として復元する。
# 類似度・単語重なりは使わない。一意でなければ復元しない(従来どおりunresolvable)。
VS_SENTENCE_RESTORE = False
VS_EXPLAIN_CONTRAST_REF_EN_RE = re.compile(
    r"\b(ledger|source|but|instead|not|should|however|rather|whereas|contrary|versus)\b|n't", re.I)
VS_EXPLAIN_CONTRAST_REF_JA_RE = re.compile(r"台帳|原文|ではなく|ではない|しかし|べき|一方|対して|ところが")
VS_EXPLAIN_POSITION_REJECT_RE = re.compile(
    r"\b(paragraph|closing|elsewhere|section|ending|conclusion)\b|段落|末尾|結び", re.I)
VS_EXPLAIN_MAX_EN_WORDS = 6   # 残りの1区間が英語でこの語数以上なら拒否
VS_EXPLAIN_MAX_JA_CHARS = 11  # 残りの1区間が(CJKを含み)この文字数以上なら拒否
VS_EXPLAIN_MIN_VERBATIM_WORDS = 3  # 残りが記事本文の逐語で、かつこの語数以上なら拒否(日本語は8文字以上)

# 委任_53(2026-10-03、OPEN-233 Checker説明文混入12件の対策、設計書 design_open233_countermeasures_after_
# handoff_01.md §3、Opus独立レビュー#6 論点6でレビュー済みの形): Trial専用スイッチ、既定"legacy"=現行の挙動のまま。
# Productionに存在しない。判定基準(何を逸脱とするか・severity・10種類のflag)は変えない。変えるのは
# 「違反箇所の出力形式」だけ。
# - "violation_spans": Trial側のStage 1初回・Recheckのschemaから`claim_in_article`を外し、代わりに
#   `violation_spans`(文字列配列、記事本文の逐語引用だけ。位置の説明・理由・接続語は`issue`/`explanation`へ)を
#   要求する。受け取り側は各要素を既存の照合(`_resolve_claim_string`、VS_MATCH_EXT=ONならL5・単語境界も)で
#   要素ごとに確定し、全要素が確定した場合だけ確定とする(1つでも確定不能なら全体を確定不能=人間確認)。
#   空配列は確定不能(`violation_spans_empty`)。`claim_in_article`(Stage 2への表示・prior_issues・同一判定の
#   元)はコードが配列から組み立てる(改行区切り)。`same_fact_id_locations`は別のまま(統合しない)。
#   固定fixture(配列が無い)は既存の`claim_in_article`経路で読む(アダプタ)。
CHECKER_SPANS_MODE_LEGACY = "legacy"
CHECKER_SPANS_MODE_VIOLATION_SPANS = "violation_spans"
CHECKER_SPANS_MODE = CHECKER_SPANS_MODE_LEGACY
# 委任_60(2026-10-04ユーザー決定[4回目]、判断D=案1)で導入し、委任_61(2026-10-04ユーザー決定
# [5回目]、選択肢3、`APPROVED_FOR_PRODUCTION`、自己修復機構本体がProduction未接続のため
# `PRODUCTION_WIRED`ではない)で対象を**時期(`changed_time`)だけ**へ縮小: 時期の機械判定
# floorだけを、追加確認2回で2回とも重大でない場合に限り軽微以下へ戻す(Trial専用スイッチ、
# 既定"off"=従来どおりfloorがBLOCKING確定)。比較・方向・主体・数値・否定のfloor、precheck
# floorは対象外で決定論のまま(下の`floor_verify_target`参照)。旧"comparison_time"は廃止
# (指定すると`ValueError`)。CLI `--floor-verify-mode`。
FLOOR_VERIFY_MODE_OFF = "off"
FLOOR_VERIFY_MODE_TIME_ONLY = "time_only"
FLOOR_VERIFY_MODES = (FLOOR_VERIFY_MODE_OFF, FLOOR_VERIFY_MODE_TIME_ONLY)
FLOOR_VERIFY_MODE = FLOOR_VERIFY_MODE_OFF

# OPEN-233-KPI-RECOVERY-REDESIGN-02 委任_01 作業2-3(2026-10-04、ユーザー指示の技術是正): NORMAL群の
# Stage 2「2-of-2」(`apply_stage2_two_of_two`、1回目BLOCKING→2回目が非BLOCKINGなら降格)は、Productionに
# 存在しない評価用Trial補助(`NORMAL_GROUP_INSTANCE_IDS`=正解ラベル付きinstance限定)で、過剰Majorの
# 見かけ上の改善に寄与している(委任_68 recount: 14件降格)。KPI評価を歪めないため既定OFFとする
# (旧挙動は`STAGE2_NORMAL_TWO_OF_TWO=True`で再現。既存テストの旧挙動確認用)。適用位置は`run_instance`の
# 呼び出し側(関数自体は不変)。Production未変更。有効化はTrial比較の再現目的のみ。
STAGE2_NORMAL_TWO_OF_TWO = False

# 作業2-2: 「KPI確認構成」(rep23〜25の構成[`HANDOFF_MODE`=violation_span、`VS_MATCH_EXT`、
# `VS_EXPLAIN_SPLIT`、`JA_MODE`=english_only、`FLOOR_VERIFY_MODE`=time_only]に、L6完結文復元
# `VS_SENTENCE_RESTORE`を加え、NORMAL群2-of-2をOFFにしたもの)。各Trial起動スクリプトは
# `apply_kpi_trial_switches()`でこの構成を適用する(個別に4〜6個のglobalを書き換えない)。
# 既定のglobal値は変更しない(`apply_kpi_trial_switches`を呼ぶまで旧既定のまま)。Trial専用、
# Production未配線・`APPROVED_FOR_PRODUCTION`ではない。
# SUPERSEDED by OPEN233_APPROVED_FLOW_SWITCHES(2026-10-06、OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01): 下記の
# `FLOOR_VERIFY_MODE=time_only`・`CAUSAL_FLOOR=True`は旧仕様(数字以外の機械的強制重大化を含む)。新規E2E/配線は承認構成を使う。
# 旧構成の再現(既存テスト・旧E2E script)のため値は変更せず残す。
KPI_TRIAL_SWITCHES = {
    "HANDOFF_MODE": "violation_span",
    "VS_MATCH_EXT": True,
    "VS_EXPLAIN_SPLIT": True,
    "VS_SENTENCE_RESTORE": True,
    "JA_MODE": "english_only",
    "FLOOR_VERIFY_MODE": "time_only",
    "STAGE2_NORMAL_TWO_OF_TWO": False,
    # 委任_03(Fable再設計判断3/5): 確認役(`STAGE2_DOWNGRADE_VERIFY`)は実測(NORMAL群47.3%)で不採用のため外した
    # (コードは残置、既定OFF)。代わりにTier 0=因果floor、Tier 1'=S1(Stage 2第2意見)をON。
    # 注: 因果floor語彙の¥0 hold-out評価は採用条件(誤停止<=2%)を満たさなかった(replay_guards_04、REPORT§53)。語彙の最終採否は
    # Fable判断待ち。ここでの`CAUSAL_FLOOR`ONは「Fable指定の構成」の記録であり、有料runの実行可否を意味しない。
    # 委任_04: 語彙は`known6`(既知G_H 6語+既存ヘッジ語。hold-out評価で誤停止0.19%・閉鎖15/16、Fable判断1で確定)。
    "CAUSAL_FLOOR": True,
    "CAUSAL_FLOOR_VOCAB": "known6",
    "STAGE2_SECOND_OPINION": True,
    # 委任_06(Fable評価2・3): N1′=再確認結果・未解消prior issueを必ず次cycleのStage 2へ合流(`unconfirmed_after_reverify`廃止)。
    # `RECHECK_BEFORE_AFTER_PAIRS`(N3′)はA/B(委任_06 作業4)で採否を決めるまで本構成へ含めない(既定OFF)。
    "RECHECK_MERGE_UNRESOLVED": True,
    "STRUCTURAL_ELEMENT_REWRITE": True,  # 委任_07
    # 委任_08(Opus#13・Fable評価1/2/5): actor_guardをAG1-strict+2条件ANDへ是正、構造要素書き換えの前後対をRecheckへ渡す。
    "ACTOR_GUARD_MODE": "ag1_strict",
    "STRUCTURAL_PAIRS_TO_RECHECK": True,
    # 委任_11(Opus#14後のFable評価、設計書§18): 既定ONの新スイッチ(legacy挙動は各スイッチOFFで保持)
    "STAGE4_ALLOWLIST": True,
    "LADDER_LOCATION_CARRY": True,
    "REWRITE_REVERT_GUARD": True,
    "SPAN_FALLBACK_CHAIN": True,
    "JUDGE_ONLY_CYCLE_AFTER_CAP": True,
    "LAST_RESORT_DELETE": True,
    "MATERIALITY_BLOCKING_PIN": True,
    # 既定OFF(事前固定条件を¥0 replayで満たしたときだけ委任_12でON、`replay_verdict_reuse_01`/`agg_sibling_locations_cycle1_01`)
    "STAGE2_VERDICT_REUSE_NONBLOCKING": False,
    "STAGE2_SIBLING_LOCATIONS_CYCLE1": False,
}


# 委任_06(OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01、Opus#16後のFable確定構成、Trial専用・Production未配線・
# `APPROVED_FOR_PRODUCTION`ではない)。全て既定=legacy(rep30挙動不変)。`KPI_TRIAL_SWITCHES`へは含めない(段階Aスクリプトが明示設定)。
STAGE1_MODE_LEGACY, STAGE1_MODE_COVERAGE_UNION = "legacy_v4a", "coverage_union"
STAGE1_MODES = (STAGE1_MODE_LEGACY, STAGE1_MODE_COVERAGE_UNION)
STAGE1_MODE = STAGE1_MODE_LEGACY      # coverage_union=文ID網羅3'-R+Ledger逆照合5-liteの2経路∪(`er052_open233_stage1_coverage_checker_01`)
STAGE1_ROUTES = "both"                # coverage_unionの経路: both/r3_only/r5_only(段階Aの経路別測定用)
F3_PRECHECK_ALWAYS = False            # F3: Stage 1が非検出(候補0)でもprecheck floorを実行(早期PASS returnの前に配線)
# 委任_11(Opus#17後Fable評価、Trial専用・既定不変): r5-V・経路別reasoning effort・否定是正案a。
STAGE1_R5_MODE = "full"               # full=5-lite(従来) / verify_supported=r5-V(r3がSUPPORTEDにした単位+関係単位のみ検証。routes=bothの順次実行)
STAGE1_R3_REASONING = "high"          # r3の推論effort(high/medium/low)。既定high=従来(vfl01.REASONING_EFFORT)
STAGE1_R5_REASONING = "high"          # r5/r5-Vの推論effort(high/medium/low)
STAGE1_NEGATION_MODE = "legacy"       # legacy=従来の決定論否定検査 / a=是正案a(対比構文除外・なし追加・英語Ledger対応・not only除外)
STAGE1_FAIL_CLOSED = False            # H1: Stage 1 API失敗はPASSへ抜けず、再実行1回→なお失敗なら許可リスト`api_failure`でSTOP
# 委任_18(E2E-ACCEPTANCE-01、Trial専用・Production未配線・既定=従来): Rewrite後Recheckの新Stage 1仕様(Opus#16 論点8/9)。
# coverage_union=Recheckを「変更単位+前後1単位」の3'-R+5-lite(対象限定)で行い、Rewrite発生記事は最終出口前に3'-R全文を1回行う。
RECHECK_MODE_LEGACY, RECHECK_MODE_COVERAGE_UNION = "legacy_v4a", "coverage_union"
RECHECK_MODES = (RECHECK_MODE_LEGACY, RECHECK_MODE_COVERAGE_UNION)
RECHECK_MODE = RECHECK_MODE_LEGACY
STAGE1_RECLASSIFY = False             # 委任_04(CHECKER-FLOOR-PRODUCTION-E2E-01): Checker再分類(4観点)を合流前filterとして初回/Recheck/出口へ適用。既定OFF=従来
RUN_CALL_HOOK = None                  # E2E Waste検知用(既定None=無効)。`check_budget`の冒頭で呼ばれる(call前、state渡し)


def apply_kpi_trial_switches() -> dict:
    """`KPI_TRIAL_SWITCHES`をこのモジュールのglobalへ適用し、適用後の値を返す(Trial起動スクリプト用)。"""
    g = globals()
    for k, v in KPI_TRIAL_SWITCHES.items():
        g[k] = v
    g["FLOOR_VERIFY_MODE"] = validate_floor_verify_mode(KPI_TRIAL_SWITCHES["FLOOR_VERIFY_MODE"])
    return {k: g[k] for k in KPI_TRIAL_SWITCHES}


# OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 委任_04(2026-10-06、Opus M5): ユーザー承認済み2点(Checker再分類4観点の正式採用/後段機械判定は数字のみ)
# を反映した「承認構成」。E2E scriptと将来のProduction配線が共用する(E2E scriptにだけ置くとTrial専用になるため定数化)。
# `KPI_TRIAL_SWITCHES`(上、`FLOOR_VERIFY_MODE=time_only`・`CAUSAL_FLOOR=True`)は旧仕様でSUPERSEDED by OPEN233_APPROVED_FLOW_SWITCHES(2026-10-06)。
# globalの既定値は旧挙動のまま(`apply_open233_approved_flow_switches()`を呼ぶまで不変)。PRODUCTION_WIRED未(E2E・runtime evidence後に判定)。
# 旧E2E(`er052_open233_e2e_acceptance_01.apply_switches`)から引き継ぐ値=Stage 1 coverage_union/Recheck新仕様/S1ON等(Fable判断: S1はStage 2承認構成の一部として維持)。
OPEN233_APPROVED_FLOW_SWITCHES = {
    **{k: v for k, v in KPI_TRIAL_SWITCHES.items() if k not in ("FLOOR_VERIFY_MODE", "CAUSAL_FLOOR")},
    # --- 本承認で変更(数字以外の機械的強制重大化の廃止) ---
    "FLOOR_MODE": "number_only",            # apply_floor発火集合=changed_numberのみ
    "FLOOR_VERIFY_MODE": "off",             # 時期verify廃止(時期floor自体が無い)
    "CAUSAL_FLOOR": False,                  # Tier 0因果floor+補助ベルト(G_H/issue_actor)停止
    "STAGE2_DOWNGRADE_VERIFY": False,       # 確認役(降格verify)OFF
    "TIER0_G_L_ENABLED": False,
    "PRECHECK_MODE": "number_only",         # precheckは数字(number_mismatch)のみStage 2スキップBLOCKING
    "STAGE1_RECLASSIFY": True,              # Checker再分類(4観点)を合流前filterとして初回/Recheck/出口へ
    # --- 旧E2Eから引き継ぎ(明示) ---
    "STAGE2_SECOND_OPINION": True,          # S1維持
    "RECHECK_BEFORE_AFTER_PAIRS": False,
    "STAGE2_VERDICT_REUSE_NONBLOCKING": True,
    "STAGE2_SIBLING_LOCATIONS_CYCLE1": True,
    "STAGE1_MODE": "coverage_union",
    "STAGE1_ROUTES": "both",
    "STAGE1_R5_MODE": "full",
    "STAGE1_R3_REASONING": "medium",
    "STAGE1_R5_REASONING": "high",
    "STAGE1_NEGATION_MODE": "a",
    "F3_PRECHECK_ALWAYS": True,
    "STAGE1_FAIL_CLOSED": True,
    "RECHECK_MODE": "coverage_union",
    "MAX_CYCLES": 2,
    "HARD_MAX_CYCLES": 3,
    "MODEL": "gpt-6-luna",
}


def apply_open233_approved_flow_switches() -> dict:
    """承認構成をこのmoduleのglobalへ適用し、適用後の値(全キー)を返す。値の妥当性もここで検証する。"""
    g = globals()
    for k, v in OPEN233_APPROVED_FLOW_SWITCHES.items():
        g[k] = v
    validate_floor_verify_mode(g["FLOOR_VERIFY_MODE"])
    floor_fire_flags()
    filter_precheck_findings([])
    assert_open233_approved_flow_switches()
    return {k: g[k] for k in OPEN233_APPROVED_FLOW_SWITCHES}


def assert_open233_approved_flow_switches() -> dict:
    """現在のglobalが承認構成と一致することをassertする(E2E開始前・テスト用)。不一致はAssertionError(全不一致を列挙)。"""
    g = globals()
    bad = {k: (g.get(k), v) for k, v in OPEN233_APPROVED_FLOW_SWITCHES.items() if g.get(k) != v}
    if bad:
        raise AssertionError(f"not in OPEN233 approved flow switches (actual, expected): {bad}")
    return {k: g[k] for k in OPEN233_APPROVED_FLOW_SWITCHES}


def validate_floor_verify_mode(mode: str) -> str:
    """`off`/`time_only`以外(廃止した`comparison_time`を含む)は`ValueError`。"""
    if mode not in FLOOR_VERIFY_MODES:
        raise ValueError(f"floor-verify-mode must be one of {FLOOR_VERIFY_MODES}, got {mode!r}")
    return mode


# 配列から組み立てたclaim文字列→要素listの対応(`resolve_violation_spans`が配列経路へ入るための索引)。
# `claim_text`は多数の関数を文字列のまま渡るため、文字列そのものを鍵にする(組み立ては決定論)。
_VS_SPANS_REGISTRY: dict = {}
VS_SPANS_EMPTY_PREFIX = "(violation_spans empty) "

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
# 委任_55(design書§4-26、2026-10-03): 線引きの正式採用(ユーザー決定、
# `APPROVED_FOR_PRODUCTION`、`PRODUCTION_WIRED`未達)に伴いV6→V7へ昇格(V6は
# 定数として残す)。V7は条件付き→断定の一律BLOCKINGと「迷えばBLOCKING」を
# 置き換え、肯定形の自然な推論を許容する。機械floor等は不変。
BODY_RUBRIC_DEFAULT = (
    s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B
    if ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT else s2c.RUBRIC_R3_TRIPLE_PRIME
)
# 委任_60: V7→V7b(判定原則文の整合。V7(3)の「比較・時期の差は一律BLOCKING」を基底R3(e)
# に揃え「Ledgerと矛盾する重大な変更(数値改変・主体取り違え・否定反転・方向反転・時期
# 取り違え)は重大」へ。V7は定数として残す。要再較正=
# `er052_open233_element_trial_safety_control_06.py`)。
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


# 委任_08(Opus#13・Fable評価1、2026-10-04): actor_guard是正(AG1-strict)用の「細粒度」日英同義語表。評価前に確定(語彙確定の証跡、
# 本表はこのcommit以降、差分0確認・負例テストの結果を見て変更しない)。Trial専用、Production未配線。
# クラス分割の原則(Fable評価1):
#   - employee / contractor / worker / staff、customer / client / user / passenger は**別クラス**(例: Meta案件の核心「Meta社員ではなく
#     外部の契約者」の区別を消さない)。executive/manager/official/analyst/trader/investor/shareholder等も別クラス。
#   - 複数の英語語形(単数・複数・ハイフン有無)は同じクラスに入れてよい。日本語表現は1エントリずつ辞書的対応またはLedger逐語の根拠を持つもののみ。
#   - 表に無い主体語は許容されない(fail-closed)。日本語は語の境界(前後が漢字・カタカナ・長音でない)で照合するため、複合語は
#     (「クレジットカード利用者」のように)複合語そのものを1エントリとして列挙する。
#   - 英語の複合語 `contract worker(s)` / `contract staff` / `contracted worker(s)` は contractor クラスとして扱う(`ACTOR_EN_COMPOUNDS`)。
# 注記: 本guardは「主体語の置換」だけを見る。限定・範囲(scope)の一般化・縮小を守るものではない(scopeの担保はRecheck)。
# 根拠コメント: [L]=Ledger逐語(4種のLedger[Tip/Meta/Hormuz/Handbag]のGrep棚卸し)、[D]=辞書的対応。
ACTOR_SYNONYM_CLASSES = {
    # クラス名: {"en": 英語語形, "ja": 日本語表現(複合語含む)}
    "user": {"en": ["user", "users"],
             "ja": ["利用者", "ユーザー", "使用者",
                    "クレジットカード利用者",  # [L] Tip F-001/F-004 scope「ニューヨーク市タクシーのクレジットカード利用者」↔ credit-card user(s)
                    "対象ユーザー"]},          # [L] Meta scope「米国のMuse提供地域・対象ユーザー」
    "customer": {"en": ["customer", "customers"], "ja": ["顧客", "お客", "お客様"]},  # [L] Tip「顧客」、[D] 顧客=customer
    "client": {"en": ["client", "clients"], "ja": ["クライアント", "依頼者", "依頼人"]},  # [D] customerと別クラス(顧客を含めない)
    "passenger": {"en": ["passenger", "passengers"], "ja": ["乗客"]},  # [L] Tip「メニューを偶然見た乗客」
    "employee": {"en": ["employee", "employees"], "ja": ["従業員", "社員"]},  # [L] Tip/Meta「従業員」「Meta従業員」
    "worker": {"en": ["worker", "workers"], "ja": ["労働者", "作業員"]},  # [D] 契約スタッフは含めない(contractorクラス)
    "staff": {"en": ["staff"], "ja": ["スタッフ", "職員"]},  # [D] 「契約スタッフ」は複合語のためcontractor側の1エントリ(語境界でマッチしない)
    "contractor": {"en": ["contractor", "contractors"],  # + ACTOR_EN_COMPOUNDS(contract worker(s)/contract staff)
                   "ja": ["契約スタッフ",  # [L] Meta MUSE-HC-006/HC-012「訓練を受けた人間の契約スタッフ」↔ contractor / contract worker
                          "契約労働者", "契約社員", "請負業者", "業務委託"]},  # [L] Meta「請負業者」、[D]
    "agent": {"en": ["agent", "agents"], "ja": ["エージェント"]},  # [L] Meta「AIエージェント」「人間の訓練済みエージェント」
    "executive": {"en": ["executive", "executives"], "ja": ["経営者", "経営陣", "幹部", "役員", "エグゼクティブ"]},  # [D] Handbag F001 retail executives
    "manager": {"en": ["manager", "managers"], "ja": ["管理者", "マネージャー", "管理職"]},  # [D]
    "official": {"en": ["official", "officials"], "ja": ["当局", "当局者", "政府関係者", "政府当局"]},  # [D] Hormuz系
    "spokesperson": {"en": ["spokesperson", "spokespeople"],
                     "ja": ["広報担当者", "広報担当", "広報", "報道官", "スポークスパーソン"]},  # [L] Meta「Metaの広報担当者Daniel Roberts」
    "engineer": {"en": ["engineer", "engineers"], "ja": ["エンジニア", "技術者"]},  # [D]
    "resident": {"en": ["resident", "residents"], "ja": ["住民"]},  # [D]
    "driver": {"en": ["driver", "drivers"], "ja": ["運転手", "ドライバー", "運転者"]},  # [D](Handbag「mass-market behavioral driver」は主体でなく要因だが表は辞書的対応)
    "patient": {"en": ["patient", "patients"], "ja": ["患者"]},  # [D]
    "student": {"en": ["student", "students"], "ja": ["学生"]},  # [D]
    "teacher": {"en": ["teacher", "teachers"], "ja": ["教師", "教員", "先生"]},  # [D]
    "analyst": {"en": ["analyst", "analysts"], "ja": ["アナリスト", "分析者"]},  # [D]
    "trader": {"en": ["trader", "traders"], "ja": ["トレーダー"]},  # [D]
    "investor": {"en": ["investor", "investors"], "ja": ["投資家", "投資者"]},  # [D]
    "shareholder": {"en": ["shareholder", "shareholders"], "ja": ["株主"]},  # [D]
}
# 英語の複合主体語 → クラス(単純な主体語[contract workのworker等]を別クラスへ誤分類しない)。語境界・ハイフン/空白のゆれを許容する。
ACTOR_EN_COMPOUNDS = [
    (r"\bcontract(?:ed)?[ -](?:workers?|staff)\b", "contractor"),  # [D] 契約スタッフ/契約労働者
]


ACTOR_GUARD_MODE = "legacy"  # 委任_08: `legacy`(既定、従来の英語部分一致) / `ag1_strict`(KPI構成。AG1-strict+2条件AND)

_JA_EDGE_CHARS = "一-龥々ァ-ヶー"  # 日本語の語の境界判定用: 前後が漢字・カタカナ・長音のときは語の一部とみなし一致としない
_EN_WORD_TO_CLASS = {w.lower(): cls for cls, d in ACTOR_SYNONYM_CLASSES.items() for w in d["en"]}


def actor_classes_in_text(text: str) -> dict:
    """英語テキスト中の主体語を同値クラス単位で返す({クラス名: 語形の集合})。複合語(contract worker等)は先に
    contractorクラスとして取り、その範囲は単独語(worker)の抽出から除く。語境界は`\\b`。"""
    out: dict = {}
    t = text or ""
    masked = t
    for pat, cls in ACTOR_EN_COMPOUNDS:
        for m in re.finditer(pat, t, re.IGNORECASE):
            out.setdefault(cls, set()).add(m.group(0).lower())
            masked = masked[:m.start()] + " " * (m.end() - m.start()) + masked[m.end():]
    for m in _ACTOR_NOUN_PATTERN.finditer(masked):
        w = m.group(0).lower()
        out.setdefault(_EN_WORD_TO_CLASS.get(w, w), set()).add(w)
    return out


def actor_class_in_ja_text(cls: str, text: str) -> list:
    """日本語(または日英混在)本文に、クラスの日本語表現が語の境界付きで存在するか(存在した表現のlist)。
    英語語形は`\\b`単語境界で照合する。"""
    d = ACTOR_SYNONYM_CLASSES.get(cls) or {"en": [], "ja": []}
    t = re.sub(r"https?://[^\s)\]]+", " ", text or "")  # URL内の語(`personal-ai-agent`等)を主体表現として拾わない
    hits = [j for j in d["ja"]
            if re.search(r"(?<![" + _JA_EDGE_CHARS + r"])" + re.escape(j) + r"(?![" + _JA_EDGE_CHARS + r"])", t)]
    hits += [e for e in d["en"] if re.search(r"\b" + re.escape(e) + r"\b", t, re.IGNORECASE)]
    if cls == "contractor":
        hits += [m.group(0) for pat, c in ACTOR_EN_COMPOUNDS if c == cls for m in re.finditer(pat, t, re.IGNORECASE)]
    return hits


def actor_class_named_in_issue(cls: str, issue_text: str) -> list:
    """Checkerのissue/explanation(英語)が、クラスの英語語形を単語境界で名指ししているか(名指しされた語形のlist)。"""
    return [w for w in sorted(actor_classes_in_text(issue_text).get(cls, set()))]


def _ag1_related_blocks(ledger_text: str, related_fact_ids) -> list:
    if isinstance(related_fact_ids, str):
        related_fact_ids = [x for x in re.split(r"[,、/\s]+", related_fact_ids.strip()) if x]
    blocks = []
    for fid in related_fact_ids or []:
        b = floor_verify_fact_block(ledger_text, fid)  # 無ければNone(Ledgerに無いid=誤り、(ii)不成立=fail-closed)
        if b:
            blocks.append(b)
    return blocks


def actor_rewrite_guard_decision(before_text: str, after_text: str, ledger_text: str,
                                 related_fact_ids=None, issue_text: str = "") -> dict:
    """委任_08 AG1-strict+2条件AND。新主体クラス(after−before、クラス単位)ごとに許容根拠を判定する。
    (i) 元文に同クラスあり(=新主体ではない) / (ii) 関連fact本文に同クラス表現(語境界付き)あり /
    (iii) Ledgerの他factに同クラス表現あり ∧ Checker issue/explanationがその英語語形を単語境界で名指し(2条件AND、片方だけでは不可)。
    いずれも満たさない新主体クラスが1つでもあれば拒否(ok=False)。`related_fact_id`欠落・Ledgerに無いid→(ii)不成立(fail-closed)。
    注記: 本guardは主体語の置換だけを見る。scope(限定・一般化)を守るものではない(scopeはRecheckが担保)。"""
    after_cls = actor_classes_in_text(after_text)
    before_cls = actor_classes_in_text(before_text)
    new = {c: w for c, w in after_cls.items() if c not in before_cls}
    blocks = _ag1_related_blocks(ledger_text, related_fact_ids)
    # 委任_09(Fable判断1・2): `related_fact_id`が空(None/空文字/空list=Checker出力仕様上の欠落)のときだけ、Ledger全体を照合先にする
    # fallback(`ledger_wide_fallback`、現行guardの元の設計意図=ledger_text全体との照合への復帰)。idが指定されているのにLedgerに
    # 無い(誤id)場合は従来どおりfail-closed。関連factがある場合は従来のAG1-strict(関連fact優先、他factは2条件ANDのみ)で、fallbackは発動しない。
    _ids = related_fact_ids
    if isinstance(_ids, str):
        _ids = [x for x in re.split(r"[,、/\s]+", _ids.strip()) if x]
    related_empty = not _ids
    per = []
    for c in sorted(new):
        rel_hits = [h for b in blocks for h in actor_class_in_ja_text(c, b)]
        led_hits = actor_class_in_ja_text(c, ledger_text or "")
        iss_hits = actor_class_named_in_issue(c, issue_text or "")
        if rel_hits:
            basis, ok = "related_fact", True
        elif related_empty and led_hits:
            basis, ok = "ledger_wide_fallback", True
        elif led_hits and iss_hits:
            basis, ok = "ledger_and_issue", True
        else:
            basis, ok = None, False
        per.append({"class": c, "new_words": sorted(new[c]), "ok": ok, "basis": basis,
                    "related_fact_hits": sorted(set(rel_hits))[:6], "ledger_hits": sorted(set(led_hits))[:6],
                    "issue_named": iss_hits, "related_blocks_found": len(blocks), "related_fact_empty": related_empty})
    return {"mode": "ag1_strict", "ok": all(p["ok"] for p in per), "new_classes": per}


def actor_rewrite_guard_ok(before_text: str, after_text: str, ledger_text: str,
                           related_fact_ids=None, issue_text: str = "", decision_out: list | None = None) -> bool:
    """`ACTOR_GUARD_MODE`=`legacy`(既定): 従来どおり(英語の主体語をLedger本文に部分一致で照合)。
    `ag1_strict`: `actor_rewrite_guard_decision`(関連fact・issueは呼び出し側が渡す。未指定=fail-closedで(ii)不成立)。
    `decision_out`(list)を渡すと、ag1_strictの判定詳細(`actor_guard_decision`)をappendする。"""
    if ACTOR_GUARD_MODE == "ag1_strict":
        dec = actor_rewrite_guard_decision(before_text, after_text, ledger_text, related_fact_ids, issue_text)
        if decision_out is not None:
            decision_out.append(dec)
        return dec["ok"]
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

# OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01 委任_04(2026-10-06、ユーザー決定[APPROVED_FOR_PRODUCTION]、PRODUCTION_WIRED未):
# 後段の機械判定(deterministic floor)は数字(`changed_number`)のみ残す。`FLOOR_FLAGS`自体は不変
# (フラグ持ち回り・降格禁止・反実仮想記録が依存)。`apply_floor`の「発火集合」だけを`FLOOR_MODE`で切り替える。
# 既定=legacy_5flags(旧挙動、既存テスト維持)。承認構成は`OPEN233_APPROVED_FLOW_SWITCHES`で適用する。
MECHANICAL_FLOOR_FLAGS = ("changed_number",)
FLOOR_MODE_LEGACY, FLOOR_MODE_NUMBER_ONLY = "legacy_5flags", "number_only"
FLOOR_MODES = (FLOOR_MODE_LEGACY, FLOOR_MODE_NUMBER_ONLY)
FLOOR_MODE = FLOOR_MODE_LEGACY


def floor_fire_flags() -> list:
    """`apply_floor`が強制BLOCKINGの根拠にするフラグ集合(`FLOOR_MODE`依存)。"""
    if FLOOR_MODE not in FLOOR_MODES:
        raise ValueError(f"FLOOR_MODE must be one of {FLOOR_MODES}, got {FLOOR_MODE!r}")
    return list(MECHANICAL_FLOOR_FLAGS) if FLOOR_MODE == FLOOR_MODE_NUMBER_ONLY else list(FLOOR_FLAGS)


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


def actor_guard_context(claim_rec: dict) -> tuple:
    """claim_recから(related_fact_id[str], Checker issue+explanation[str])を取り出す(欠落は空=fail-closed側)。"""
    dev = (claim_rec or {}).get("dev") or {}
    fid = (claim_rec or {}).get("related_fact_id") or dev.get("related_fact_id") or ""
    issue = " ".join(str(x) for x in (dev.get("issue"), dev.get("explanation")) if x)
    return fid, issue


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
    if RUN_CALL_HOOK is not None:  # 委任_18: E2E Waste検知フック(既定None=従来と同一)
        RUN_CALL_HOOK(state)
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


def find_matching_prior_record(dev: dict, prior_records: list, threshold: float = CLAIM_TEXT_SIMILARITY_THRESHOLD,
                                claim_norm: str | None = None):
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
    # 委任_42 仕様(7): `claim_norm`(確定範囲を正規化した表現、受け渡し修正の
    # 新方式)が渡された場合はそれを使う(生の引用符付き文字列のままだと周回間の
    # 同一判定が揺れる、Opus L2レビュー#5 §3-8)。未指定なら従来どおり。
    claim_text_norm = (claim_norm if claim_norm is not None
                       else normalize_claim_text(dev.get("claim_in_article") or ""))
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


# 委任_53: 違反箇所の出力形式(Trial専用追記ブロック、`CHECKER_SPANS_MODE="violation_spans"`のときだけ
# Stage 1初回・Recheckの両方のPromptへ追記する)。設計書§3-2(委任_48修正版)の文面。「文の一部だけが
# 問題でも、その語句を含む文全体を引用」の行は使わない(最初から文全体Rewriteへ広げないため)。
# 判定基準(何を逸脱とするか、severity、10種類のflag)には触れない。
VIOLATION_SPANS_INSTRUCTION = """

【追加指示: 違反箇所の書き方(Trial専用。判定基準は変えない)】
この指示は「違反箇所の書き方」だけに関するものです。どの箇所をdeviationとして報告するか、severityや10種類のフラグの判定基準は変えないでください。ここでいう逐語は【検証対象の記事】本文からの引用であり、Ledgerとの文言一致の話ではありません。引用は英語の記事本文からのみ行ってください。
各deviationについて、"violation_spans"(文字列の配列)に、その逸脱に該当する箇所を、記事本文から一字一句そのまま引用してください。要約・言い換え・勝手な結合は禁止です。複数箇所なら、別々の原文範囲として、箇所ごとに別の配列要素にしてください。
- 各要素は、記事本文をそのままコピーした文字列にします。語の置換・語順変更・省略(…や...)・翻訳・要約はしません。
- 文の一部だけが問題の場合は、その語句・節だけを引用してかまいません(文全体に広げる必要はありません)。ただし、引用は記事内でちょうど1箇所に定まる長さにしてください。同じ語句が記事内の別の場所にも出てくる場合は、前後の語を足して1箇所に定まるようにしてください(足すのは問題の語句の前後の連続した語だけで、説明や接続語は入れないでください)。
- どの語句が問題かはissueに書いてください。
- 大文字・小文字、句読点、アポストロフィ、ダッシュ、空白を変えないでください。文末の句読点を補ったり別の記号に替えたりしないでください(記事で「,」や「:」が続くところを「.」で終えない)。引用符(“ ”)で囲まないでください。見出しは先頭の「#」を除いた文字列で引用してください。
- 位置の説明(「見出し」「冒頭」「段落5」「…で始まる段落」など)、あなた自身の説明文、接続語(and / および 等)を、各要素に入れないでください。位置や理由はissue・explanationに書いてください。
- 見出し・冒頭文・"In one line"が同じ事実を主張しているなら、それぞれ別の要素として、本文のとおりに引用してください。
- 離れた複数箇所は1つの文字列につなげず、別々の要素にしてください。間にある逸脱でない文は含めないでください。連続した複数文が1つの逸脱を構成する場合に限り、記事のとおり連続した1要素にしてください。
- 該当箇所を記事本文の特定の文字列として指せない場合(記事全体の含意など)は、violation_spansを空配列にし、issueにその理由を書いてください。推測で引用を作らないでください。引用できないことを理由に、deviationの報告を省略しないでください。"""


def build_deviation_schema_with_spans(item_schema: dict) -> dict:
    """委任_53: deviation item schemaから`claim_in_article`を外し、`violation_spans`(文字列配列)を足す
    (`build_deviation_schema_with_enumeration`と同じ「ローカルにコピーして拡張する」手口。er003・er051は
    変更しない)。strictモードなので全propertyをrequiredへ入れる。"""
    props = {k: v for k, v in item_schema["properties"].items() if k != "claim_in_article"}
    props["violation_spans"] = {"type": "array", "items": {"type": "string"}}
    required = [k for k in item_schema["required"] if k != "claim_in_article"] + ["violation_spans"]
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}


def assemble_claim_from_violation_spans(deviation: dict) -> dict:
    """委任_53: `violation_spans`(配列)を持つdeviationの`claim_in_article`を、コードが配列から組み立てる
    (要素を改行で連結)。組み立てた文字列と要素listの対応を`_VS_SPANS_REGISTRY`へ登録し、
    `resolve_violation_spans`が配列経路(要素ごとの照合)へ入れるようにする。空配列は、Stage 2への表示用に
    `issue`を添えた文字列にし(確定は`violation_spans_empty`で不能=人間確認)、配列が無いdeviation
    (固定fixture)は何もしない(既存の`claim_in_article`経路)。"""
    spans = deviation.get("violation_spans")
    if CHECKER_SPANS_MODE != CHECKER_SPANS_MODE_VIOLATION_SPANS or not isinstance(spans, list):
        return deviation
    elems = [(s if isinstance(s, str) else "").strip() for s in spans]
    if not elems:
        text = (VS_SPANS_EMPTY_PREFIX + (deviation.get("issue") or "")).strip()
    else:
        text = "\n".join(elems)
    _VS_SPANS_REGISTRY[text.strip()] = elems
    d2 = dict(deviation)
    d2["claim_in_article"] = text
    d2["claim_assembled_from_violation_spans"] = True
    return d2


def adopt_violation_spans(deviations: list) -> list:
    """委任_53: deviations全体へ`assemble_claim_from_violation_spans`を適用する(legacyでは恒等)。"""
    if CHECKER_SPANS_MODE != CHECKER_SPANS_MODE_VIOLATION_SPANS:
        return deviations
    return [assemble_claim_from_violation_spans(d) for d in deviations]


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
            # 委任_53: 展開された別箇所のdeviationは、元の`violation_spans`(その逸脱の範囲)を引き継がない
            # (`same_fact_id_locations`は別のまま、既存の`claim_in_article`経路で照合する)。legacyではキー自体が無い。
            new_dev.pop("violation_spans", None)
            new_dev.pop("claim_assembled_from_violation_spans", None)
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
    if CHECKER_SPANS_MODE == CHECKER_SPANS_MODE_VIOLATION_SPANS:  # 委任_53(既定OFF)
        prompt += VIOLATION_SPANS_INSTRUCTION
        item_schema = build_deviation_schema_with_spans(item_schema)
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
    parsed_trial["deviations"] = adopt_violation_spans(parsed_trial["deviations"])  # 委任_53(legacyでは恒等)
    parsed_trial["deviations"] = expand_same_fact_id_locations(parsed_trial["deviations"], fixture["article_text"])
    usage = s2p._extract_usage(response)
    cost = round(s2p.official_cost_jpy(usage), 4)
    call_log.append({"label": label, "recovery_stage": "stage1_initial", "cost_jpy": cost, "usage": usage,
                      "elapsed_seconds": elapsed, "prompt_sha256": s2p.sha256_text(prompt)})
    record_call(state, consecutive_errors, label, cost, True, "stage1_initial", usage)
    return parsed_trial


def stage1_effort_for_label(lbl: str) -> str:
    """委任_11: Stage 1 coverage_unionの経路別reasoning effort。labelがr3系(r3/r3_rerun/..._retry)ならR3、r5系(r5/r5v)ならR5。
    既定high=従来(vfl01.REASONING_EFFORT)。不正値はValueError(黙って既定へ戻さない)。"""
    eff = STAGE1_R3_REASONING if lbl.startswith("r3") else STAGE1_R5_REASONING
    if eff not in cov.REASONING_EFFORTS:
        raise ValueError(f"unknown reasoning effort: {eff!r}")
    return vfl01.REASONING_EFFORT if eff == "high" else eff


def make_stage1_call_fn(client, state, consecutive_errors, call_log, label, recovery_stage: str = "stage1_initial",
                        effort_override: str | None = None):
    """委任_18: coverage module用の`call_fn`(retry/cost計上/budget check)を作る。委任_06の`stage1_coverage_fresh`内の実装を
    そのまま関数化しただけ(既定`recovery_stage="stage1_initial"`では従来と同一)。Recheck/出口3'-Rでは`recovery_stage`だけ変える。"""
    def call_fn(lbl, developer_message, prompt, schema):
        check_budget(state)
        full_label = f"{label}_{lbl}"
        effort = stage1_effort_for_label(lbl)
        if effort_override is not None:  # 委任_04 M3: 再分類callはlabel依存にせずeffortを明示固定(Trial02と同一=medium)
            if effort_override not in cov.REASONING_EFFORTS:
                raise ValueError(f"unknown reasoning effort: {effort_override!r}")
            effort = vfl01.REASONING_EFFORT if effort_override == "high" else effort_override
        last_err, response, t0 = None, None, time.time()
        for _ in range(1 + MAX_RETRIES_PER_CALL):
            try:
                response = client.responses.create(
                    model=MODEL, reasoning={"effort": effort},
                    text={"format": {"type": "json_schema", **schema}},
                    input=[{"role": "developer", "content": developer_message}, {"role": "user", "content": prompt}])
                break
            except Exception as e:  # noqa: BLE001
                last_err = f"{type(e).__name__}: {e}"
                time.sleep(1.0)
        elapsed = round(time.time() - t0, 3)
        if response is None:
            call_log.append({"label": full_label, "recovery_stage": recovery_stage, "error": last_err})
            record_call(state, consecutive_errors, full_label, 0.0, False, recovery_stage)
            return None, {"error": last_err, "cost_jpy": 0.0}
        usage = s2p._extract_usage(response)
        cost = round(s2p.official_cost_jpy(usage), 4)
        call_log.append({"label": full_label, "recovery_stage": recovery_stage, "cost_jpy": cost, "usage": usage,
                          "elapsed_seconds": elapsed, "prompt_sha256": s2p.sha256_text(prompt), "reasoning_effort": effort})
        record_call(state, consecutive_errors, full_label, cost, True, recovery_stage, usage)
        meta = {"cost_jpy": cost, "usage": usage, "elapsed_seconds": elapsed, "prompt_sha256": s2p.sha256_text(prompt),
                "reasoning_effort": effort}
        try:
            return json.loads(response.output_text), meta
        except ValueError as e:
            return None, {**meta, "error": f"json_decode: {e}"}

    return call_fn


def make_reclassify_filter(client, state, consecutive_errors, call_log, label, fixture, protected_claims=()):
    """委任_04(Opus M1/M3): `STAGE1_RECLASSIFY`ON時のみ、coverage moduleの`candidate_filter`(合流前、1箇所)を作る。OFFならNone(従来と完全同一)。
    call_fnはmodel=MODEL・effort=medium固定・recovery_stage=`stage1_reclassify`。初回/Recheck/出口の3関数が同じ関数を使う。"""
    if not STAGE1_RECLASSIFY:
        return None
    call_fn = make_stage1_call_fn(client, state, consecutive_errors, call_log, label, recovery_stage=reclf.RECOVERY_STAGE,
                                  effort_override=reclf.EFFORT)
    return reclf.make_candidate_filter(fixture, call_fn, protected_claims)


def reclassify_summary(info) -> dict | None:
    """run jsonへ残す再分類の要約(E2E集計用)。info=`candidate_filter`のaudit値(None=再分類OFF)。"""
    if info is None:
        return None
    keys = ("status", "n_model_entries", "n_targets", "n_protected_keys", "n_excluded_claims", "n_excluded_entries",
            "n_excluded_with_changed_number", "n_failclosed", "cost_jpy", "effort", "prompt_sha256")
    return {"reclassify_status": info.get("status"), **{k: info.get(k) for k in keys if k != "status"}}


def stage1_coverage_fresh(client, state, consecutive_errors, call_log, label, fixture, r3_precomputed=None) -> dict:
    """委任_06: `STAGE1_MODE=coverage_union`のStage 1(文ID網羅3'-R+Ledger逆照合5-liteの2経路∪)。LLM呼び出しは
    `make_stage1_call_fn`(委任_18で関数化)の`call_fn`を`cov.run_stage1_coverage`へ注入して行う。経路のAPI失敗
    (module内で再実行1回後も失敗)は`_stage1_api_failure=True`で返す(H1: 呼び出し側でfail-closed)。"""
    call_fn = make_stage1_call_fn(client, state, consecutive_errors, call_log, label)
    res = cov.run_stage1_coverage(fixture, call_fn, routes=STAGE1_ROUTES, segment_fn=vs_sentence_segments_l6,
                                  initial_extra=CAUSAL_SENTENCE_INITIAL_EN, negation_mode=STAGE1_NEGATION_MODE,
                                  r5_mode=STAGE1_R5_MODE, r3_precomputed=r3_precomputed,
                                  candidate_filter=make_reclassify_filter(client, state, consecutive_errors, call_log, label, fixture))
    parsed = cov.to_stage1_parsed(res)
    if STAGE1_RECLASSIFY:  # OFFでは従来と完全同一(キーも足さない)
        parsed["stage1_reclassify"] = reclassify_summary(res["audit"].get("candidate_filter"))
    return parsed


def run_recheck_coverage(client, state, consecutive_errors, call_log, label, fixture, article_text: str,
                         prior_issues: list, before_text: str, protected_claims=()) -> dict:
    """委任_18(`RECHECK_MODE=coverage_union`): `run_recheck`と同形の戻り値(overall_status/deviations/prior_issues_resolved/
    all_prior_issues_resolved/prior_issues_resolved_by_index)を、変更単位+前後1単位の3'-R+5-lite(対象限定)で作る。
    API失敗(再実行1回後も)は`run_recheck`と同じくfail-closed(LEDGER_DEVIATION・未解消・`_recheck_api_failure`)。"""
    rf = dict(fixture)
    rf["article_text"] = article_text
    call_fn = make_stage1_call_fn(client, state, consecutive_errors, call_log, label, recovery_stage="stage1_recheck")
    # 委任_04 M2: 前回指摘と同文の候補は再分類の対象外(候補のまま残しStage 2が再判定)。prior_issues_resolvedは再分類後の候補で計算される。
    _prot = [pi.get("claim_in_article") or "" for pi in prior_issues or []] + list(protected_claims or [])
    res = cov.run_recheck_scope(rf, call_fn, before_text, prior_issues, segment_fn=vs_sentence_segments_l6,
                                initial_extra=CAUSAL_SENTENCE_INITIAL_EN, negation_mode=STAGE1_NEGATION_MODE,
                                candidate_filter=make_reclassify_filter(client, state, consecutive_errors, call_log, label, rf, _prot))
    if res["api_failure"]:
        return {"overall_status": "LEDGER_DEVIATION", "deviations": [], "all_prior_issues_resolved": False,
                "_recheck_api_failure": True, "recheck_coverage_audit": res["audit"]}
    devs = cov.candidates_to_deviations(res["candidates"])
    all_res, by_idx = aggregate_prior_issues_resolved(prior_issues, res["prior_issues_resolved"])
    return {"overall_status": "LEDGER_DEVIATION" if devs else "LEDGER_COMPLIANT", "deviations": devs,
            "prior_issues_resolved": res["prior_issues_resolved"], "all_prior_issues_resolved": all_res,
            "prior_issues_resolved_by_index": by_idx, "variant": "coverage_union_recheck",
            "recheck_coverage_audit": res["audit"]}  # audit["candidate_filter"]に再分類info(OFFならNone)


def run_exit_check_coverage(client, state, consecutive_errors, call_log, label, fixture, article_text: str,
                            protected_claims=()) -> dict:
    """委任_18(`RECHECK_MODE=coverage_union`): Rewrite発生記事の最終出口前の3'-R全文1回。候補は`deviations`(Stage 2へ渡す形)で返す。"""
    rf = dict(fixture)
    rf["article_text"] = article_text
    call_fn = make_stage1_call_fn(client, state, consecutive_errors, call_log, label, recovery_stage="stage1_exit_check")
    res = cov.run_exit_full_r3(rf, call_fn, segment_fn=vs_sentence_segments_l6, initial_extra=CAUSAL_SENTENCE_INITIAL_EN,
                               negation_mode=STAGE1_NEGATION_MODE,
                               candidate_filter=make_reclassify_filter(client, state, consecutive_errors, call_log, label, rf,
                                                                       protected_claims))
    return {"api_failure": res["api_failure"], "deviations": cov.candidates_to_deviations(res["candidates"]),
            "audit": res["audit"]}


def stage1_fresh_dispatch(client, state, consecutive_errors, call_log, label, fixture, developer_message,
                          use_enumeration_stage1: bool = True) -> dict:
    """委任_06: Stage 1新規実行の分岐。`STAGE1_MODE`既定(legacy_v4a)では従来の2経路([`stage1_fresh_with_enumeration`]/[`stage1_fresh`])
    を従来どおり呼ぶだけ(引数・戻り値とも不変)。`coverage_union`のときだけ`stage1_coverage_fresh`へ分岐する。"""
    if STAGE1_MODE not in STAGE1_MODES:
        raise ValueError(f"unknown STAGE1_MODE: {STAGE1_MODE!r}")
    if STAGE1_MODE == STAGE1_MODE_COVERAGE_UNION:
        return stage1_coverage_fresh(client, state, consecutive_errors, call_log, label, fixture)
    if use_enumeration_stage1:
        return stage1_fresh_with_enumeration(client, state, consecutive_errors, call_log, label, fixture,
                                             developer_message=developer_message)
    return stage1_fresh(client, state, consecutive_errors, call_log, label, fixture)


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
    if CHECKER_SPANS_MODE == CHECKER_SPANS_MODE_VIOLATION_SPANS:  # 委任_53(既定OFF)
        item_schema = build_deviation_schema_with_spans(item_schema)
    props = {"deviations": {"type": "array", "items": item_schema},
              "prior_issues_resolved": {"type": "array", "items": vfl01.PRIOR_ISSUE_RESOLVED_ITEM_SCHEMA}}
    required = ["deviations", "prior_issues_resolved"]
    return {
        "name": "open233_self_recovery_recheck_v4a_prior",
        "schema": {"type": "object", "properties": props, "required": required, "additionalProperties": False},
        "strict": True,
    }


def aggregate_prior_issues_resolved(prior_issues, items) -> tuple:
    """委任_07(件数一致バグの是正)+委任_08(Opus#13・Fable評価4の3穴修正): Recheck応答の`prior_issues_resolved`項目を
    index別に集約し、(all_resolved: bool, by_index: {index(str): bool|None})を返す。
    式: all_resolved = 「全項目が dict かつ `resolved is True`」 ∧ 「{0..n-1} ⊆ 返却indexの集合」(n=prior issue数)。
    - 同index複数項目(1 issueを2項目で返す等)は、全てtrueのときだけそのindexをtrue(旧式の件数一致`len(items)==n`は使わない)。
    - 範囲外index・int以外のindex・非dict項目・`resolved`が`True`以外(文字列"false"・1・None等)が1つでもあればFalse(安全側)。
    - indexが欠けたprior issueは未解消扱い(by_index値None)。
    - prior issueが0件のときは、全項目がdictかつ`resolved is True`ならTrue(空を含む。範囲外判定の対象となるindexが無いため)。
    旧式: `len(items)==len(prior_issues) and all(resolved)`(Checkerが1 issueを2項目で返すだけでFalse)。"""
    n = len(prior_issues or [])
    groups: dict = {}
    clean = True  # 非dict・resolvedがTrue以外・範囲外index/非int indexが1つでもあれば偽
    for it in items or []:
        if not isinstance(it, dict):
            clean = False
            continue
        idx = it.get("index")
        ok_idx = isinstance(idx, int) and not isinstance(idx, bool) and 0 <= idx < n
        if n > 0 and not ok_idx:
            clean = False
        if it.get("resolved") is not True:
            clean = False
        if ok_idx:
            groups.setdefault(idx, []).append(it.get("resolved") is True)
    by_index = {str(i): (all(groups[i]) if i in groups else None) for i in range(n)}
    if n == 0:
        return clean, by_index
    return clean and all(v is True for v in by_index.values()), by_index


def run_recheck(client, state, consecutive_errors, call_log, label, fixture, article_text: str,
                 prior_issues: list, enable_fact_id_enumeration: bool = False,
                 before_after_pairs: list | None = None) -> dict:
    """委任_06 N3′(`RECHECK_BEFORE_AFTER_PAIRS`ON かつ `before_after_pairs`が非空のときのみ): prompt末尾の
    prior_issues指示の直後へ、再確認(`run_recheck_confirm`)と同形式の「書き換え前後の対」ブロックを追加する
    (cite-or-release指示は含めない)。Checker本体template(er003/er051)・Schema・判定規則は不変。OFF時は従来とバイト同一。

    委任_35(design書§6-16、追加原因(d)の是正): `same_fact_id_locations`
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
    ba_block = ""
    # 委任_08(Fable評価5): `STRUCTURAL_PAIRS_TO_RECHECK`ON時は、構造要素を書き換えた対(`structural`印付き)に限定して対ブロックを渡す
    # (`RECHECK_BEFORE_AFTER_PAIRS`とは独立。追加call 0)。`RECHECK_BEFORE_AFTER_PAIRS`ONなら全対(従来どおり)。
    _ba_use = before_after_pairs if RECHECK_BEFORE_AFTER_PAIRS else (
        [p_ for p_ in (before_after_pairs or []) if p_.get("structural")] if STRUCTURAL_PAIRS_TO_RECHECK else [])
    if _ba_use:
        ba_block = build_before_after_instruction(_ba_use)
        prompt += ba_block
    if enable_fact_id_enumeration:
        prompt += SAME_FACT_ID_ENUMERATION_INSTRUCTION
    if CHECKER_SPANS_MODE == CHECKER_SPANS_MODE_VIOLATION_SPANS:  # 委任_53(既定OFF、schemaは下で差し替え)
        prompt += VIOLATION_SPANS_INSTRUCTION
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
    parsed_trial["deviations"] = adopt_violation_spans(parsed_trial["deviations"])  # 委任_53(legacyでは恒等)
    # 委任_20 W2(委任_35で既定False化、§6-16): Recheckが検出した同一
    # fact_id別箇所の展開は、enable_fact_id_enumeration=True明示時のみ行う。
    if enable_fact_id_enumeration:
        parsed_trial["deviations"] = expand_same_fact_id_locations(parsed_trial["deviations"], article_text)
    resolved = raw_parsed.get("prior_issues_resolved", [])
    parsed_trial["prior_issues_resolved"] = resolved
    # 委任_07(技術是正、Fable事前判断1): 件数一致式(`len(resolved)==len(prior_issues)`)は、Checkerが1 prior issueを
    # 同indexの複数項目へ分けて返すだけで偽の自己矛盾(COMPLIANT∧all_prior=False)を生み、再確認callが毎回発生していた。
    # index別集約へ是正する(Checkerの判定規則は不変、応答の集約方法のみ)。indexが欠けたprior issueは未解消(安全側)。
    parsed_trial["all_prior_issues_resolved"], parsed_trial["prior_issues_resolved_by_index"] = (
        aggregate_prior_issues_resolved(prior_issues, resolved))
    usage = s2p._extract_usage(response)
    cost = round(s2p.official_cost_jpy(usage), 4)
    call_log.append({"label": label, "recovery_stage": "stage1_recheck", "cost_jpy": cost, "usage": usage,
                      "elapsed_seconds": elapsed, "prompt_sha256": s2p.sha256_text(prompt),
                      **({"before_after_block_len": len(ba_block)} if ba_block else {}),
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
# 委任_06(OPEN-233-KPI-RECOVERY-REDESIGN-02、Opus#12後): N1′ 再検査結果の正規化(純関数、追加call 0)。
# 「未解消のprior issueは必ず次cycleのStage 2を通る」を1規則に統一する(再確認DEVIATIONを捨ててSTAGE4へ直行して
# いた`unconfirmed_after_reverify`経路と、通常Recheckの`DEVIATION∧all_prior=False`で未解消priorがdeviationsに
# 無いと脱落する潜在ギャップの両方を是正)。Trial専用(`RECHECK_MERGE_UNRESOLVED`、既定OFF)。Production未配線:
# Productionが自己回復flowを持たない間は、呼び出し側が`NEXT_CYCLE`を`STOP`へ写像する(OPEN-233-A1-PROD)。
# ------------------------------------------------------------
RECHECK_MERGE_UNRESOLVED = False   # N1′(既定OFF=旧挙動: 再確認が解消未確認ならSTAGE4`unconfirmed_after_reverify`)
STRUCTURAL_PAIRS_TO_RECHECK = False  # 委任_08: 構造要素を書き換えた場合に限り、その前後の対をRecheckへ渡す(KPI構成ON)
RECHECK_BEFORE_AFTER_PAIRS = False  # N3′(既定OFF): 通常Recheckへも「書き換え前後の対」ブロックを渡す
# 委任_07(技術是正、Fable事前判断2): ladderで対象範囲がタイトル・`## In one line`・見出し等の構造要素にかかるとき、
# 決定論deleteを選ばず(常に`title_degenerate`等のhard blockになる)、E1(語句)→③(文)→④(段落)の書き換えへ回す。
# 書き換え案が空になる場合は却下して次の水準へ進める(Human Reviewへ倒す新経路なし)。既定OFF(旧挙動)、KPI構成でON。
STRUCTURAL_ELEMENT_REWRITE = False

# 委任_11(OPEN-233-KPI-RECOVERY-REDESIGN-02、Opus#14後のFable評価採用設計、設計書§18)。全て既定OFF(legacy挙動を保持)、
# `KPI_TRIAL_SWITCHES`でON。Trial専用、Production未配線・`APPROVED_FOR_PRODUCTION`ではない。
STAGE4_ALLOWLIST = False                # I-2: STAGE4の出口を許可リスト(`stage4_allowlist_decision`)へ集約。許可外は記録してfunnelへ
LADDER_LOCATION_CARRY = False           # B′: 同一箇所(前cycleの置換範囲と1文字以上重なる)は前levelより上位から昇段(位置のみ、fact_idは問わない)
REWRITE_REVERT_GUARD = False            # A2: 箇所の過去状態へ戻る候補を決定論で却下(同cycle内で上位levelへ)
SPAN_FALLBACK_CHAIN = False             # D: 引用分割の狭い緩和・複数範囲の引用形式変換・位置を取れないBLOCKINGのcarry(H-1)
JUDGE_ONLY_CYCLE_AFTER_CAP = False      # G: 上限到達後は「判定だけのcycle」(Stage 2+S1、Rewriteなし)へ遷移
LAST_RESORT_DELETE = False              # T: ladder枯渇/上限後BLOCKINGの最終手段(構造要素以外の0_delete+全文Recheck、1記事1回)
MATERIALITY_BLOCKING_PIN = False        # S-4: 本文が変わっていない箇所(正規化span集合+fact_id)で過去にBLOCKING確定したものは再判定で覆さない
STAGE2_VERDICT_REUSE_NONBLOCKING = False   # S-4: 一致した2-of-2非BLOCKINGの再利用(既定OFF、¥0 replayで重大抑制0件が条件)
STAGE2_SIBLING_LOCATIONS_CYCLE1 = False    # 第二段階案: 同fact_id兄弟箇所をcycle 1のStage 2 batchへ前倒し(Rewriteへは渡さない)

RECHECK_DECISION_PASS = "PASS"
RECHECK_DECISION_NEXT_CYCLE = "NEXT_CYCLE"
RECHECK_DECISION_STOP = "STOP"


def _recheck_ok(r) -> bool:
    return bool(r) and r.get("overall_status") == "LEDGER_COMPLIANT" and bool(r.get("all_prior_issues_resolved"))


def _unresolved_prior_indices(source: dict, n_prior: int) -> list:
    """sourceの`prior_issues_resolved`でresolved=falseの項目index(未返却のindexも未解消扱い=fail-closed)。
    `all_prior_issues_resolved`がTrueなら空。"""
    if source.get("all_prior_issues_resolved"):
        return []
    got = {}
    for it in (source.get("prior_issues_resolved") or []):
        try:
            got[int(it.get("index"))] = bool(it.get("resolved"))
        except (TypeError, ValueError):
            continue
    return [i for i in range(n_prior) if not got.get(i, False)]


def multi_range_to_quote_form(text: str) -> str:
    """改行連結された複数範囲を`“A” and “B”`の引用形式へ変換する(単一範囲ならそのまま)。決定論・¥0。"""
    parts = [p.strip() for p in (text or "").split("\n") if p.strip()]
    if len(parts) < 2:
        return (text or "").strip()
    return " and ".join("“" + p + "”" for p in parts)


def normalize_recheck_outcome(recheck: dict, confirm: dict | None, prior_blocking_claims: list,
                              prior_issues: list | None = None, api_failure_is_stop: bool = False) -> dict:
    """再検査結果(Recheck、必要なら再確認)を`PASS`/`NEXT_CYCLE`/`STOP`へ正規化する純関数(API呼び出しなし)。
    - PASS: Recheck、または(Recheckが`COMPLIANT∧all_prior=False`の自己矛盾で再確認を呼んだ場合)再確認が
      `LEDGER_COMPLIANT∧all_prior=True`。
    - NEXT_CYCLE: それ以外。次cycleのstage1_deviations=(i)判定元の全文検査deviationsのMAJOR ∪
      (ii)判定元`prior_issues_resolved`でresolved=falseの元blocking claimのdev(fact_idで(i)と重複するものは除く)。
      判定元=自己矛盾で再確認を呼んだ場合は再確認、そうでなければRecheck。(ii)のdevは、現行本文の置換後の文が
      単一で特定できているとき`claim_in_article`をその文へ差し替える(Stage 2/Rewriteが現行本文で位置を引けるように)。
      (i)(ii)とも空なら`deviations=[]`(呼び出し側の既存`not blocking_claims`経路でRESOLVED_REWRITE_THEN_DOWNGRADE。
      再確認経由なら`reverify_deviation_without_major=True`を監査用に返す)。
    - STOP: `api_failure_is_stop=True`かつ判定元がAPI失敗のときのみ(Production写像用。Trialは既定Falseで、API失敗は
      未解消扱いとしてNEXT_CYCLEへ合流させる=fail-closed)。"""
    ambiguous = (recheck.get("overall_status") == "LEDGER_COMPLIANT"
                 and not recheck.get("all_prior_issues_resolved"))
    used_confirm = ambiguous and confirm is not None
    source = confirm if used_confirm else recheck
    if _recheck_ok(recheck) or (used_confirm and _recheck_ok(confirm)):
        return {"decision": RECHECK_DECISION_PASS, "deviations": [], "merged_from": [], "source": "recheck" if _recheck_ok(recheck) else "reverify",
                "reverify_deviation_without_major": False, "n_dedup_dropped": 0}
    if api_failure_is_stop and source.get("_recheck_api_failure"):
        return {"decision": RECHECK_DECISION_STOP, "deviations": [], "merged_from": [], "source": "reverify" if used_confirm else "recheck",
                "reverify_deviation_without_major": False, "n_dedup_dropped": 0}
    major = [d for d in (source.get("deviations") or []) if d.get("severity") == "MAJOR"]
    merged = list(major)
    labels = ["reverify_major" if used_confirm else "recheck_major"] * len(major)
    fids = {(d.get("related_fact_id") or "").strip() for d in major}
    fids.discard("")
    dropped = 0
    seen_prior = set()
    n_prior = len(prior_blocking_claims)
    for i in _unresolved_prior_indices(source, n_prior):
        dev = dict(prior_blocking_claims[i]["dev"])
        fid = (dev.get("related_fact_id") or "").strip()
        if fid and fid in fids:
            dropped += 1
            continue
        if prior_issues is not None and i < len(prior_issues):
            cur = (prior_issues[i].get("claim_in_article") or "").strip()
            if cur and "\n" not in cur:
                dev["claim_in_article"] = cur
            elif cur and SPAN_FALLBACK_CHAIN:
                # 委任_11 D(ii)(Opus#14 L2221、Fable評価2/7): 複数範囲(改行連結)をskipせず`“A” and “B”`の引用形式へ変換する
                # (次cycleの断片照合[`_vs_resolve_in_text_core`、接続詞だけの残り]が通る形)。
                dev["claim_in_article"] = multi_range_to_quote_form(cur)
        key = (fid, (dev.get("claim_in_article") or "").strip())
        if key in seen_prior:
            dropped += 1
            continue
        seen_prior.add(key)
        merged.append(dev)
        labels.append("unresolved_prior" if used_confirm else "normal_gap")
    return {"decision": RECHECK_DECISION_NEXT_CYCLE, "deviations": merged, "merged_from": labels,
            "source": "reverify" if used_confirm else "recheck",
            "reverify_deviation_without_major": bool(used_confirm and not merged), "n_dedup_dropped": dropped}


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
    triggered = [k for k in floor_fire_flags() if bool(dev.get(k))]
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
    """委任_42(受け渡し修正、仕様(2)): 区分判定の入口。`HANDOFF_MODE`が
    新方式(既定)なら、Checkerの文字列から確定した範囲が各区分ブロック
    (title/in_one_line/hook)に含まれるかの包含判定(`detect_claim_section_
    type_by_spans`、類似度による1文選びを使わない)。旧方式
    (`HANDOFF_MODE="legacy"`)なら従来の`detect_claim_section_type_legacy`。"""
    if HANDOFF_MODE == HANDOFF_MODE_VIOLATION_SPAN:
        return detect_claim_section_type_by_spans(claim_text, full_text)
    return detect_claim_section_type_legacy(claim_text, full_text)


_VS_SECTION_RANK = {"title": 0, "in_one_line": 1, "hook": 2, "body": 3}


def detect_claim_section_type_by_spans(claim_text: str, full_text: str) -> str:
    """委任_42 仕様(2): 確定範囲(`resolve_violation_spans`、EN本文に対する
    照合)が各区分ブロックに含まれるかの包含判定。確定範囲が複数区分に
    またがる場合は最も保護の強い区分(title>in_one_line>hook>body)を返す
    (hook保持等の制約は範囲ごとに適用される=rewrite側は区分で緩めない)。
    範囲を確定できない場合はbody(その指摘は後段で`violation_span_unverified`
    としてStage 4になるため、区分は結果に影響しない)。類似度は使わない。"""
    if not full_text:
        return "body"
    resolution = resolve_violation_spans(claim_text, full_text, None)
    if resolution["status"] != "resolved":
        return "body"
    title = _paragraph_title(full_text)
    hook = _hook_paragraph_block(full_text)
    in_one_line = _extract_in_one_line_text(full_text)
    best = "body"
    for rng in resolution["ranges"]:
        probe = rng.strip()
        section = "body"
        if probe:
            for name, block in (("title", title), ("in_one_line", in_one_line), ("hook", hook)):
                if block and (probe in block or block.strip() in probe):
                    section = name
                    break
        if _VS_SECTION_RANK[section] < _VS_SECTION_RANK[best]:
            best = section
    return best


def detect_claim_section_type_legacy(claim_text: str, full_text: str) -> str:
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
# 委任_04(Opus R2): `FLOOR_FLAGS`参照から明示リストへ切り離し(挙動不変。降格禁止=AI BLOCKING維持であり上書きではない)。
DISCLOSURE_GAP_DISQUALIFYING_FLAGS = [
    "changed_actor", "changed_number", "changed_negation", "changed_comparison", "changed_time", "changed_scope",
]


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


# ------------------------------------------------------------
# 委任_60(OPEN-233-SELF-RECOVERY-TRIAL-01、2026-10-04ユーザー決定[4回目]、判断D=案1、
# Opus独立レビュー#8の代替案F5)を、委任_61(ユーザー決定[5回目]、選択肢3)で時期のみへ縮小:
# 時期の機械判定(floor)の追加確認による解放。`FLOOR_VERIFY_MODE="time_only"`のときだけ有効
# (既定"off"、Trial専用、`PRODUCTION_WIRED`ではない)。
#
# 対象(`floor_verify_target`): Stage 2のLLM判定が非BLOCKINGで、`apply_floor`だけが
# BLOCKINGへ昇格させた指摘のうち、trueのfloorフラグが`changed_time`のみのもの。
# `changed_comparison`/`changed_actor`/`changed_number`/`changed_negation`が1つでもtrueなら
# 対象外(従来どおりBLOCKING確定、理由コード`out_of_scope_flag:<flag名>`)。precheck floorも対象外。
# 決定論の不一致確認(CONFIRMED): claimの日付・時刻・期間(time)が関連factブロックに無ければ、
# 確認を呼ばずBLOCKING維持(維持方向にのみ働く)。
# CONFIRMED以外は自動解放せず確認経路へ進む(自動解放[文字一致・上昇/下落語の有無]なし)。
# 確認: 対象claim 1件ごとに独立した呼び出しを2回(`run_floor_verify_call`)。2回とも非
# BLOCKINGで、かつ`ledger_citation`が関連factブロックの逐語引用である場合だけ解放。
# 1回でもBLOCKING・API失敗・schema不一致・引用が空/非逐語は、BLOCKING固定。
# `dev`のフラグは書き換えない(解放情報は`floor_verify`フィールド)。
# ------------------------------------------------------------
FLOOR_VERIFY_FLAGS = ("changed_time",)
# 委任_61: 比較・方向も決定論のみ(委任_60では追加確認の対象だったが、方向反転が解放されたため除外)。
FLOOR_VERIFY_DETERMINISTIC_ONLY_FLAGS = ("changed_comparison", "changed_actor", "changed_number", "changed_negation")

_FV_MONTH = (r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|"
             r"Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)")
_FV_MONTH_INDEX = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8,
                   "sep": 9, "oct": 10, "nov": 11, "dec": 12}
# CONFIRMED規則(time)の抽出パターン(コード定数。日英の表記を同じトークンへ正規化する)。
FLOOR_VERIFY_TIME_PATTERNS = {
    "month_day_en": re.compile(r"\b" + _FV_MONTH + r"\.?\s+(\d{1,2})(?:st|nd|rd|th)?\b", re.IGNORECASE),
    "day_month_en": re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?" + _FV_MONTH + r"\b", re.IGNORECASE),
    "month_day_ja": re.compile(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日"),
    "month_day_slash": re.compile(r"(?<![\d/])(\d{1,2})/(\d{1,2})(?![\d/])"),
    "iso_date": re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"),
    "year": re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)"),
    "clock_hhmm": re.compile(r"(?<![\d:])(\d{1,2}):(\d{2})(?![\d:])"),
    "clock_ampm": re.compile(r"\b(\d{1,2})\s?([ap])\.?m\.?(?![a-z])", re.IGNORECASE),
    "clock_ja": re.compile(r"(\d{1,2})\s*時(?!間)"),
    "period_en": re.compile(r"(\d+(?:\.\d+)?)[\s-]*(day|week|month|year|hour|minute)s?\b", re.IGNORECASE),
    "period_ja": re.compile(r"(\d+(?:\.\d+)?)\s*(日間|週間|か月|ヶ月|カ月|年間|時間|分間)"),
    "relative": re.compile(r"\b(next day|the following day|the day after|the day before|the previous day)\b|"
                           r"(翌日|前日)", re.IGNORECASE),
}
_FV_PERIOD_JA_UNIT = {"日間": "day", "週間": "week", "か月": "month", "ヶ月": "month", "カ月": "month",
                      "年間": "year", "時間": "hour", "分間": "minute"}
_FV_RELATIVE_NORM = {"next day": "next_day", "the following day": "next_day", "the day after": "next_day",
                     "翌日": "next_day", "the day before": "prev_day", "the previous day": "prev_day",
                     "前日": "prev_day"}
# CONFIRMED規則(comparison)の抽出パターン(コード定数。数値つきの比較のみ。数値を伴わない
# 方向語[rise/fall等]は決定論では扱わず確認経路へ回す)。
_FV_NUM = r"(\d[\d,]*(?:\.\d+)?)"
FLOOR_VERIFY_COMPARISON_PATTERNS = {
    "percent": re.compile(_FV_NUM + r"\s*(?:%|percent|％)", re.IGNORECASE),
    "times": re.compile(_FV_NUM + r"\s*(?:x|times|-fold|倍)(?![a-z])", re.IGNORECASE),
    "bound_en": re.compile(r"\b(?:at least|at most|more than|less than|fewer than|over|under|up to|nearly|"
                           r"almost|above|below|exceed(?:s|ed|ing)?)\s+\$?" + _FV_NUM
                           + r"(?:\s*(million|billion|thousand))?", re.IGNORECASE),
    "bound_ja": re.compile(_FV_NUM + r"\s*(?:万|億)?\s*(?:以上|以下|超|未満|を超え|を上回|を下回)"),
}
FLOOR_VERIFY_COMPARISON_WORDS = {"twice": 2.0, "double": 2.0, "doubled": 2.0, "triple": 3.0, "tripled": 3.0}
_FV_COUNT_MULT = {"million": 1e6, "billion": 1e9, "thousand": 1e3}
_FV_ANY_NUM_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")

FLOOR_VERIFY_RUBRIC_ADDENDUM = """

【追加確認(floor verify)での追加指示(委任_60、委任_61で時期のみへ縮小、2026-10-04ユーザー決定)】
この確認は、自動判定(deterministic floor)が時期の理由だけでBLOCKINGへ引き上げた指摘を、
独立に検証するものです。上記の判定原則に従い、次のとおり判定してください。
- 台帳と矛盾する重大な変更(時期の取り違え)は重大(BLOCKING)です。
- 時期のニュアンスの差で、事実関係の核心が保たれていれば軽微(QUALITY)または
  問題なし(ACCEPTABLE)です。
- Checkerの指摘は検証すべき仮説です。仮説が正しいか、関連factブロックの該当箇所を
  逐語で引用して(ledger_citation)検証してください。引用できない場合、または判断できない
  場合はBLOCKINGとしてください。単に文字が一致する・上昇/下落の語が台帳にある、という
  だけでは問題なしの根拠になりません。"""

FLOOR_VERIFY_DEVELOPER_MESSAGE = (
    "あなたはVerified Fact LedgerとFact Safetyの独立監査担当です。自動判定が時期の理由で"
    "BLOCKINGにした特定のclaimについて、Checkerの指摘を検証すべき仮説として、Ledgerの該当箇所を"
    "引用して独立に再評価してください。"
)

FLOOR_VERIFY_PROMPT_TEMPLATE = """これは、自動判定(deterministic floor)が機械的にBLOCKINGへ引き上げた指摘の、独立した追加確認です。
以下の関連factブロック(Ledger逐語)・対象claim・ローカル文脈・Checkerの指摘(仮説)だけを見て、
あなた自身の判断でmaterialityを判定してください。

【関連factブロック(Verified Fact Ledgerより逐語、fact_id={related_fact_id})】
{fact_block}

【対象claim(確定範囲)】
{claim_text}

【対象claimを含む段落±1段落(ローカル文脈)】
{local_context}

【機械判定のフラグ】
{flag_names}

【Checkerの指摘(検証すべき仮説)】
Checkerは次の問題を指摘した: {issue}
この指摘が正しいか、Ledgerの該当箇所を引用して検証せよ。

{rubric}

materiality(BLOCKING/QUALITY/ACCEPTABLE)、ledger_citation(関連factブロックからの逐語引用。
一字一句そのまま。要約・言い換え禁止)、basis(判定根拠の分類)、explanation(短い説明)を返してください。"""

FLOOR_VERIFY_JSON_SCHEMA = {
    "name": "open233_floor_verify_v1",
    "schema": {
        "type": "object",
        "properties": {
            "materiality": {"type": "string", "enum": ["BLOCKING", "QUALITY", "ACCEPTABLE"]},
            "ledger_citation": {"type": "string"},
            "basis": {"type": "string", "enum": [
                "ledger_claim", "ledger_scope", "ledger_numeric_value", "ledger_date_or_period",
                "ledger_conditions", "notes_for_writer", "unsupported_relationship", "nuance_only", "none"]},
            "explanation": {"type": "string"},
        },
        "required": ["materiality", "ledger_citation", "basis", "explanation"],
        "additionalProperties": False,
    },
    "strict": True,
}

_FV_SEVERITY_ORDER = {"ACCEPTABLE": 0, "QUALITY": 1, "BLOCKING": 2}


def floor_verify_target(llm_materiality, floor_applied, dev: dict) -> tuple:
    """(is_target, reason, triggered_flags)。FLOOR_VERIFY_MODEが有効で、LLM判定が非
    BLOCKINGかつdeterministic floor(precheck floorでない)だけがBLOCKINGにした指摘のうち、
    trueのfloorフラグが`changed_time`のみのものだけを対象にする(委任_61)。比較・方向・主体・
    数値・否定のいずれかがtrueなら対象外(`out_of_scope_flag:<flag名>`)。"""
    triggered = [k for k in FLOOR_FLAGS if bool(dev.get(k))]
    if FLOOR_VERIFY_MODE != FLOOR_VERIFY_MODE_TIME_ONLY:
        return False, "mode_off", triggered
    if not (floor_applied or "").startswith("deterministic_floor:"):
        return False, "not_deterministic_floor", triggered
    if llm_materiality == "BLOCKING" or llm_materiality is None:
        return False, "llm_materiality_blocking", triggered
    for f in triggered:
        if f in FLOOR_VERIFY_DETERMINISTIC_ONLY_FLAGS:
            return False, f"out_of_scope_flag:{f}", triggered
    if not triggered or any(f not in FLOOR_VERIFY_FLAGS for f in triggered):
        return False, "flag_outside_time_only", triggered
    return True, "time_floor_only_llm_non_blocking", triggered


def floor_verify_fact_block(ledger_text: str, fact_id) -> str | None:
    """関連factブロック(Ledger本文の逐語、`related_fact_id`のブロック)。無ければNone
    (全文へはフォールバックしない=確認不能)。"""
    # `related_fact_id`が「HF-002, HF-007」のように複数の場合は、全てのブロックを逐語のまま
    # 連結して返す(1つでも見つからなければNone=確認不能)。
    fids = [x for x in re.split(r"[,、/\s]+", (fact_id or "").strip()) if x]
    if not fids:
        return None
    by_id: dict = {}
    for block in (ledger_text or "").split("\n\n"):
        lines = [ln for ln in block.split("\n") if ln.strip() != ""]
        if not lines:
            continue
        header = lines[0]
        m1 = precheck.FACT_HEADER_V1.match(header)
        m2 = precheck.FACT_HEADER_V2.match(header)
        found = m1.group(2) if m1 else (m2.group(1) if m2 else None)
        if found and found not in by_id:
            by_id[found] = block.strip("\n")
    if any(f not in by_id for f in fids):
        return None
    return "\n\n".join(by_id[f] for f in fids)


def _fv_float(s: str) -> float:
    return round(float(s.replace(",", "")), 4)


def floor_verify_time_tokens(text: str) -> set:
    """日付・時刻・期間・相対日の正規化トークン集合(日英の表記差を吸収)。"""
    out: set = set()
    t = text or ""
    P = FLOOR_VERIFY_TIME_PATTERNS
    for m in P["month_day_en"].finditer(t):
        out.add(("md", _FV_MONTH_INDEX[m.group(1)[:3].lower()], int(m.group(2))))
    for m in P["day_month_en"].finditer(t):
        out.add(("md", _FV_MONTH_INDEX[m.group(2)[:3].lower()], int(m.group(1))))
    for m in P["month_day_ja"].finditer(t):
        out.add(("md", int(m.group(1)), int(m.group(2))))
    for m in P["month_day_slash"].finditer(t):
        a, b = int(m.group(1)), int(m.group(2))
        if 1 <= a <= 12 and 1 <= b <= 31:
            out.add(("md", a, b))
    for m in P["iso_date"].finditer(t):
        out.add(("y", int(m.group(1))))
        out.add(("md", int(m.group(2)), int(m.group(3))))
    for m in P["year"].finditer(t):
        out.add(("y", int(m.group(1))))
    for m in P["clock_hhmm"].finditer(t):
        out.add(("clock", int(m.group(1)), int(m.group(2))))
    for m in P["clock_ampm"].finditer(t):
        h = int(m.group(1)) % 12 + (12 if m.group(2).lower() == "p" else 0)
        out.add(("clock", h, 0))
    for m in P["clock_ja"].finditer(t):
        out.add(("clock", int(m.group(1)), 0))
    for m in P["period_en"].finditer(t):
        out.add(("period", _fv_float(m.group(1)), m.group(2).lower()))
    for m in P["period_ja"].finditer(t):
        out.add(("period", _fv_float(m.group(1)), _FV_PERIOD_JA_UNIT[m.group(2)]))
    for m in P["relative"].finditer(t):
        key = (m.group(1) or m.group(2)).lower()
        out.add(("rel", _FV_RELATIVE_NORM[key]))
    return out


def floor_verify_comparison_numbers(text: str) -> set:
    """数値つき比較(%、倍、以上/以下等)に現れる数値の集合。委任_61で比較が追加確認の対象外に
    なったため、`floor_verify_confirmed`からは呼ばれない(未使用、将来用に残置)。"""
    out: set = set()
    t = text or ""
    P = FLOOR_VERIFY_COMPARISON_PATTERNS
    for key in ("percent", "times", "bound_ja"):
        for m in P[key].finditer(t):
            out.add(_fv_float(m.group(1)))
    for m in P["bound_en"].finditer(t):
        v = _fv_float(m.group(1))
        if m.group(2):
            v = v * _FV_COUNT_MULT[m.group(2).lower()]
        out.add(v)
    for w, v in FLOOR_VERIFY_COMPARISON_WORDS.items():
        if re.search(r"\b" + w + r"\b", t, re.IGNORECASE):
            out.add(v)
    return out


def floor_verify_fact_numbers(fact_block: str) -> set:
    nums = {_fv_float(m.group(0)) for m in _FV_ANY_NUM_RE.finditer(fact_block or "")}
    nums |= {round(float(v), 4) for v in precheck.extract_percentages(fact_block or "")}
    nums |= {round(float(v), 4) for v in precheck.extract_counts(fact_block or "")}
    # 倍数語(twice/double等)がfactブロックにある場合は対応する数値も存在とみなす。
    for w, v in FLOOR_VERIFY_COMPARISON_WORDS.items():
        if re.search(r"\b" + w + r"\b", fact_block or "", re.IGNORECASE):
            nums.add(v)
    return nums


def floor_verify_confirmed(claim_text: str, fact_block: str, triggered: list) -> dict:
    """決定論の不一致確認(CONFIRMED)。維持方向(BLOCKINGのまま)にだけ働く。"""
    info = {"confirmed": False, "basis_tokens": []}
    if "changed_time" in triggered:
        missing = floor_verify_time_tokens(claim_text) - floor_verify_time_tokens(fact_block)
        if missing:
            info["confirmed"] = True
            info["basis_tokens"].append({"flag": "changed_time", "missing_in_fact_block": sorted(
                [list(x) for x in missing], key=str)})
    if "changed_comparison" in triggered:  # 委任_61: 対象外のため通常は到達しない(防御的に残置)
        missing_n = floor_verify_comparison_numbers(claim_text) - floor_verify_fact_numbers(fact_block)
        if missing_n:
            info["confirmed"] = True
            info["basis_tokens"].append({"flag": "changed_comparison",
                                         "missing_in_fact_block": sorted(missing_n)})
    return info


def _fv_norm(s: str) -> str:
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return " ".join(s.split())


def run_floor_verify_call(client, claim_text: str, local_context: str, fact_block: str, issue: str,
                           flag_names: list, related_fact_id: str = "", rubric_text: str | None = None,
                           model: str = MODEL) -> dict:
    """追加確認1回分(claim 1件、batchに混ぜない)。Stage 2と同じモデル・reasoning設定。"""
    rubric = rubric_text if rubric_text is not None else (BODY_RUBRIC_DEFAULT + FLOOR_VERIFY_RUBRIC_ADDENDUM)
    prompt = FLOOR_VERIFY_PROMPT_TEMPLATE.format(
        related_fact_id=related_fact_id or "(不明)", fact_block=fact_block, claim_text=claim_text,
        local_context=local_context or "(なし)", flag_names=", ".join(flag_names),
        issue=issue or "(指摘文なし)", rubric=rubric)
    t0 = time.time()
    response = client.responses.create(
        model=model,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **FLOOR_VERIFY_JSON_SCHEMA}},
        input=[{"role": "developer", "content": FLOOR_VERIFY_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    elapsed = round(time.time() - t0, 3)
    parsed = json.loads(response.output_text)
    usage = s2p._extract_usage(response)
    return {"prompt_sha256": s2p.sha256_text(prompt), "parsed": parsed, "model": response.model,
            "response_id": response.id, "usage": usage,
            "cost_jpy": round(s2p.official_cost_jpy(usage), 4), "elapsed_seconds": elapsed}


class FloorVerifyCallError(RuntimeError):
    pass


def _fv_validate_call(res: dict, fact_block: str) -> dict:
    p = res.get("parsed") or {}
    rec = {"materiality": p.get("materiality"), "basis": p.get("basis"),
           "ledger_citation": p.get("ledger_citation"), "explanation": p.get("explanation"),
           "prompt_sha256": res.get("prompt_sha256"), "cost_jpy": res.get("cost_jpy", 0.0),
           "response_id": res.get("response_id"), "valid": False, "invalid_reason": None,
           "citation_verbatim": False}
    if p.get("materiality") not in _FV_SEVERITY_ORDER or not isinstance(p.get("ledger_citation"), str):
        rec["invalid_reason"] = "schema_mismatch"
        return rec
    cit = _fv_norm(p["ledger_citation"])
    if not cit:
        rec["invalid_reason"] = "ledger_citation_empty"
        return rec
    rec["citation_verbatim"] = cit in _fv_norm(fact_block)
    if not rec["citation_verbatim"]:
        rec["invalid_reason"] = "ledger_citation_not_verbatim"
        return rec
    rec["valid"] = True
    return rec


def floor_verify_evaluate(call_fn, ledger_text: str, claim_text: str, local_context: str,
                           dev: dict, llm_materiality: str, floor_applied: str,
                           short_circuit: bool = True) -> dict:
    """1 claimの追加確認の全体判定。`call_fn(claim_text, local_context, fact_block, issue,
    flag_names, related_fact_id)`は結果dict(`run_floor_verify_call`互換)を返すか、
    `FloorVerifyCallError`を送出する。戻り値の`released`がTrueのときだけ
    `final_materiality`(2回の確認とStage 2の3つのうち最も重い非BLOCKING値)を使う。"""
    is_target, reason, triggered = floor_verify_target(llm_materiality, floor_applied, dev)
    fv = {"mode": FLOOR_VERIFY_MODE, "target": is_target, "target_reason": reason,
          "triggered_flags": triggered, "llm_materiality": llm_materiality,
          "confirmed": False, "confirmed_basis": [], "fact_block_found": None, "calls": [],
          "n_calls": 0, "released": False, "blocking_fixed_reason": None, "release_note": None,
          "final_materiality": "BLOCKING", "cost_jpy": 0.0}
    if not is_target:
        return fv
    fact_id = dev.get("related_fact_id")
    fact_block = floor_verify_fact_block(ledger_text, fact_id)
    fv["fact_block_found"] = fact_block is not None
    if fact_block is None:
        # 確認不能。確認経路へ進んでも、引用できる関連factブロックが無く解放条件(逐語引用)を満たせない
        # ため呼び出しを省略しBLOCKING固定(費用なし、結果は同じ)。
        fv["blocking_fixed_reason"] = "fact_block_unavailable"
        return fv
    conf = floor_verify_confirmed(claim_text, fact_block, triggered)
    fv["confirmed"], fv["confirmed_basis"] = conf["confirmed"], conf["basis_tokens"]
    if conf["confirmed"]:
        fv["blocking_fixed_reason"] = "confirmed_by_deterministic_mismatch"
        return fv
    issue = dev.get("issue") or dev.get("explanation") or ""
    flag_names = [f.replace("changed_", "") for f in triggered]
    results = []
    for _i in range(2):
        try:
            res = call_fn(claim_text, local_context, fact_block, issue, flag_names, fact_id or "")
        except FloorVerifyCallError as e:
            fv["calls"].append({"valid": False, "invalid_reason": f"api_failure: {e}"})
            fv["n_calls"] += 1
            fv["blocking_fixed_reason"] = "verify_api_failure"
            return fv
        rec = _fv_validate_call(res, fact_block)
        fv["calls"].append(rec)
        fv["n_calls"] += 1
        fv["cost_jpy"] = round(fv["cost_jpy"] + (rec.get("cost_jpy") or 0.0), 4)
        results.append(rec)
        if short_circuit and (not rec["valid"] or rec["materiality"] == "BLOCKING"):
            break
    invalid = [r for r in results if not r["valid"]]
    if invalid:
        fv["blocking_fixed_reason"] = invalid[0]["invalid_reason"]
        return fv
    if any(r["materiality"] == "BLOCKING" for r in results):
        fv["blocking_fixed_reason"] = ("verify_blocking_disagree" if any(
            r["materiality"] != "BLOCKING" for r in results) else "verify_blocking_both")
        return fv
    if len(results) < 2:
        fv["blocking_fixed_reason"] = "verify_incomplete"
        return fv
    heaviest = max([llm_materiality] + [r["materiality"] for r in results], key=lambda m: _FV_SEVERITY_ORDER[m])
    fv.update({"released": True, "final_materiality": heaviest,
               "release_note": "2回の追加確認とも非BLOCKING(逐語引用あり)。最終値はStage2+確認2回のうち最も重い非BLOCKING値"})
    return fv


def floor_verify_summarize(stage2_results_iter) -> dict:
    """runtime evidence用の集計(対象件数/CONFIRMED件数/確認呼び出し件数/解放件数/BLOCKING固定の
    理由別件数/費用)。`floor_verify`フィールドを持つclaimのみ対象。"""
    s = {"n_floor_verify_records": 0, "n_target": 0, "n_confirmed": 0, "n_verify_calls": 0, "n_released": 0,
         "blocking_fixed_by_reason": {}, "target_reason_counts": {}, "out_of_scope_flag": {},
         "cost_jpy": 0.0}
    for r in stage2_results_iter:
        fv = r.get("floor_verify")
        if not fv:
            continue
        s["n_floor_verify_records"] += 1
        s["target_reason_counts"][fv["target_reason"]] = s["target_reason_counts"].get(fv["target_reason"], 0) + 1
        if not fv["target"]:
            if fv["target_reason"].startswith("out_of_scope_flag:"):
                k2 = fv["target_reason"].split(":", 1)[1]
                s["out_of_scope_flag"][k2] = s["out_of_scope_flag"].get(k2, 0) + 1
            continue
        s["n_target"] += 1
        s["n_confirmed"] += 1 if fv["confirmed"] else 0
        s["n_verify_calls"] += fv["n_calls"]
        s["cost_jpy"] = round(s["cost_jpy"] + fv.get("cost_jpy", 0.0), 4)
        if fv["released"]:
            s["n_released"] += 1
        else:
            k = fv["blocking_fixed_reason"] or "unknown"
            s["blocking_fixed_by_reason"][k] = s["blocking_fixed_by_reason"].get(k, 0) + 1
    return s


# ------------------------------------------------------------
# 委任_02(OPEN-233-KPI-RECOVERY-REDESIGN-02、Opus独立レビュー#11[条件A]→Fable評価1〜11、2026-10-04):
# 後段Safetyの三層構造(Trial専用、`STAGE2_DOWNGRADE_VERIFY`既定OFF、Production未配線・`APPROVED_FOR_PRODUCTION`ではない)。
#   Tier 0(決定論、¥0): `stage2_release_guard`=G_L(Ledger構造化欄×Checker flag)+補助ベルト(G_H/issue_actor、既知の型向け)。
#       該当したら確認役を呼ばずBLOCKING固定。
#   Tier 1(確認役、call 1回): Checker MAJORをStage 2が非BLOCKING(QUALITY/ACCEPTABLE)にしたもの全てを対象に、
#       別promptの確認役(`floor_verify`の一般化)が「RELEASE」かつLedger逐語引用が照合できたときだけ解除する。
#       Stage 2本体(1回目)は不変(指摘を見せない=本体の較正を崩さない)。
#   Tier 2(失敗時): UPHOLD/引用非逐語/API失敗/schema不一致/Tier 0該当は全てBLOCKING→既存Rewriteラダー。Human Reviewへ新経路なし。
#       Rewriteの`rewrite_hint`はCheckerのissue/explanation+Ledgerのnotes_for_writer/conditionsから決定論で合成する。
# Guard・確認役は毎cycleの現行本文(`run_stage2`が毎周回呼ばれる)で再評価する。Sol等の強モデルは使わない。
# ------------------------------------------------------------
STAGE2_DOWNGRADE_VERIFY = False

# ---- Tier 0: G_L(Ledger構造化欄×Checker flag)。語彙・閾値は定数(¥0 replay `replay_guards_03_gl.py`で評価)。
# ¥0 replay(委任_02 作業3、降格534件・流出16行)の結果: G_Lは流出16/16を閉じるが、正当降格518件のうち108件(20.8%、NORMAL群110件中
# 12件=10.9%)も固定BLOCKINGにする(G_B[causality flagのみ]は132件25.5%・NORMAL 24.6%)。補助ベルトに対する上積みは1行
# (rep24 cycle 2のB3「and」版)だけで、確認役(Tier 1)が閉じられる見込み。確認役のreplay採否基準(ii)[NORMAL群のBLOCKING化率≤10%]は
# Tier 0の該当分も含むため、G_Lを有効にするとTier 1の前にNORMAL群が10.9%となり基準を超える。よって既定は無効
# (`TIER0_G_L_ENABLED=False`、補助ベルトのみ)。確認役replayでG_L有効時の反実仮想も併記する。コードと語彙は残す。
TIER0_G_L_ENABLED = False
GL_CAUSAL_STRENGTH_BLOCK_VALUES = ("CAUSAL_STATED_BY_SOURCE", "CORRELATIONAL")
GL_CAUSAL_PROHIBIT_RE = re.compile(
    r"(原因|理由|因果|きっかけ|せい)[^。]{0,16}(書かない|記述しない|扱わない|断定しない|確認できない|混同しない)"
    r"|(だけが|のみが|単独の)(原因|理由)|因果関係は[^。]{0,10}(確認|示)")
GL_CERTAINTY_PROHIBIT_RE = re.compile(
    r"(確定形|断定形|確定として|断定)[^。]{0,14}(書かず|書かない|しない|扱わない|避け)|確定として扱わない|と書かず|と書かない")
_GL_FIELD_RE = re.compile(r"^\s+(causal_strength|notes_for_writer|conditions|scope):\s*(.*)$")

# ---- Tier 0補助ベルト(委任_01のD*の定義のまま。「既知の型への補助」であり主構造ではない)
AUX_CONN_RE = re.compile(r"\b(so|because|therefore|as a result|led to|leading to)\b", re.I)
AUX_HEDGE_RE = re.compile(r"\b(could|may|might|can|would|possibly|perhaps|probably|likely|seems?|appears?)\b", re.I)
AUX_ACTOR_ISSUE_RE = re.compile(
    r"payer|liable|who would (?:pay|be)|who pays|responsib|"
    r"identif(?:y|ies|ied) [^.]{0,40} as (?:the )?(?:payer|responsible|party|actor)|支払|負担者|主体|担当者", re.I)
_AUX_JA_RE = re.compile(r"[぀-ヿ一-鿿]")

# ---- 委任_03(OPEN-233-KPI-RECOVERY-REDESIGN-02、Fable再設計判断3): Tier 0 因果floor(G_Hの一般化)の語彙。
# 【hold-out手順】この語彙は、流出16行・Checker指摘文・降格534件の文面を一切見ずに、標準的な言語学的目録
# (下記出典)のみから構築し、評価(`replay_guards_04_causal_floor.py`)より前にcommitした(git履歴で確認可)。
# 既に委任_01/02で既知だったG_H補助ベルト6語(so/because/therefore/as a result/led to/leading to)は「既知」、
# それ以外は目録由来。評価後に変更してよいのは`can`/`would`のA/B選択(`CAUSAL_FLOOR_CAN_WOULD_AS_HEDGE`)のみ。
# 日本語記事は対象外(英語claimのみ=`_AUX_JA_RE`で日本語文字を含むclaimは除外)。
# 出典(因果接続語):
#   [CGEL] Huddleston & Pullum 2002, The Cambridge Grammar of the English Language, ch.8 (Adjuncts: reason/result/purpose)
#   [Quirk] Quirk et al. 1985, A Comprehensive Grammar of the English Language, 8.4-8.5(理由・結果・目的の節/接続副詞 11.x)
#   [Halliday] Halliday & Hasan 1976 Cohesion in English, 5.4(causal conjunction: so/therefore/hence/consequently/because/since/for this reason)
#   [PDTB] Penn Discourse Treebank 2.0 annotation manual (Contingency.Cause: reason/result の明示的connective一覧)
#   [Levin] Levin 1993 English Verb Classes and Alternations(因果動詞: cause/lead/result/force/drive/trigger/spark/prompt/push/fuel/make)
# 各項目は小文字の語/句(空白は柔軟一致)。動詞は目録の見出し語と規則的な屈折形を持つ。
CAUSAL_CONNECTIVES_EN = (
    # 接続詞・前置詞(理由・結果・目的)[CGEL][Quirk][Halliday][PDTB]
    "so", "because", "since", "as", "now that", "so that", "in order to", "so as to",
    "due to", "owing to", "thanks to", "because of", "on account of", "in response to",
    # 接続副詞(結果)[Halliday][Quirk 10.x/11.x][PDTB]
    "therefore", "thus", "hence", "consequently", "accordingly", "as a result", "as a consequence",
    "for this reason", "that is why", "that's why", "which is why", "the reason", "reason why",
    # 因果動詞(原形・三単現・過去・-ing)[Levin]
    "lead to", "leads to", "led to", "leading to",
    "result in", "results in", "resulted in", "resulting in",
    "cause", "causes", "caused", "causing",
    "drive", "drives", "drove", "driven", "driving",
    "prompt", "prompts", "prompted", "prompting",
    "trigger", "triggers", "triggered", "triggering",
    "spark", "sparks", "sparked", "sparking",
    "force", "forces", "forced", "forcing",
    "make", "makes", "made", "making",
    "push", "pushes", "pushed", "pushing",
    "fuel", "fuels", "fueled", "fuelled", "fueling", "fuelling",
    "stem from", "stems from", "stemmed from", "stemming from",
)
# 文頭の`following`(結果節を従える分詞構文「Following X, Y」)は文頭位置のみ因果とみなす(前置詞`following`の
# 時系列用法[after]との混同を、文頭限定で抑える)[CGEL ch.8 §Temporal/causal adjuncts]。
CAUSAL_SENTENCE_INITIAL_EN = ("following",)

# 出典(ヘッジ・推測・帰属=因果を断定していない):
#   [Hyland] Hyland 1998 Hedging in Scientific Research Articles(epistemic modals/lexical verbs/adverbs/attribution)
#   [Palmer] Palmer 2001 Mood and Modality(epistemic possibility/evidentiality: reportedly/allegedly/apparently)
#   [CGEL] Huddleston & Pullum 2002 ch.3(modal auxiliaries)・ch.8(modal adjuncts: possibly/perhaps/probably/presumably)
# 推測・可能性・他者の見解の帰属に限定する(Fable判断3)。`can`/`would`は別枠(A/B)。
HEDGE_MARKERS_EN = (
    "may", "might", "could", "possibly", "perhaps", "probably", "presumably", "likely", "unlikely",
    "appear", "appears", "appeared", "seem", "seems", "seemed", "apparently",
    "reportedly", "allegedly", "supposedly",
    "is said to", "are said to", "was said to", "were said to",
    "is expected to", "are expected to", "expected to", "is believed to", "are believed to", "believed to",
    "is thought to", "are thought to", "thought to", "according to",
)
# 帰属型ヘッジ(「some say」「analysts say」「officials say」等: 見解の持ち主を名指す主体+言明動詞)[Hyland][Palmer]。
HEDGE_ATTRIBUTION_SUBJECTS_EN = ("some", "many", "analysts", "analyst", "officials", "official", "critics", "critic",
                                 "experts", "expert", "observers", "observer", "sources", "source", "economists",
                                 "economist", "insiders", "people")
HEDGE_ATTRIBUTION_VERBS_EN = ("say", "says", "said", "believe", "believes", "think", "thinks", "suggest", "suggests",
                              "argue", "argues", "argued", "expect", "expects", "warn", "warns", "warned", "claim",
                              "claims", "claimed", "speculate", "speculated")
# `can`/`would`の扱い(Fable判断3のA/B): A=ヘッジに含める(`can`=可能性の能力用法、`would`=仮定・婉曲)、B=含めない。
HEDGE_CAN_WOULD_EN = ("can", "would")
# 採用版は¥0 replay(`replay_guards_04_causal_floor.py`)の結果で決める(誤停止≤2%かつ閉鎖最大の方)。
# 評価結果(委任_03): A/Bは閉鎖13/16・正当降格誤停止13件(2.51%)で完全に同値(can/wouldを含む該当claimが無い)。
# どちらも採用条件(誤停止<=2%)を満たさず、版の選択は未確定(Fable判断待ち)。暫定でA(True)のまま。
CAUSAL_FLOOR_CAN_WOULD_AS_HEDGE = True

# 委任_03 作業3: Tier 0 因果floorと Tier 1' S1(第2意見)のTrial専用スイッチ(既定OFF、`KPI_TRIAL_SWITCHES`でON。
# Production未配線・`APPROVED_FOR_PRODUCTION`ではない)。OFFのとき既存挙動と完全に同一。
CAUSAL_FLOOR = False
STAGE2_SECOND_OPINION = False
# 委任_04(Fable判断1): Tier 0の有効語彙の選択。`"known6"`=既知G_H 6語(so/because/therefore/as a result/led to/leading to)+
# 既存ヘッジ語(`AUX_CONN_RE`/`AUX_HEDGE_RE`、有効・既定)、`"inventory"`=目録由来の拡張語彙(評価用、無効=KPI構成では使わない)。
# 根拠(`replay_guards_04_causal_floor.json`、降格534件・流出16行のhold-out評価): known6(+issue_actor)=閉鎖15/16
# [「and」版除き15/15]・正当降格誤停止0.19%(1件)で事前基準(誤停止<=2%かつ閉鎖15/15)を満たす唯一の構成。inventory=閉鎖の上積み0・
# 誤停止+13件(2.51%: `lead to`6[同一の否定文]/`as`4/`caused`3/`make`1)で不採用。語彙は結果を見て削らない(hold-outの趣旨)。
CAUSAL_FLOOR_VOCAB = "known6"


def _norm_apostrophe(s: str) -> str:
    return (s or "").replace("’", "'").replace("‘", "'")


def _build_phrase_re(phrases) -> "re.Pattern":
    alts = sorted(set(phrases), key=len, reverse=True)
    body = "|".join(re.escape(p).replace(r"\ ", r"\s+") for p in alts)
    return re.compile(r"(?<![\w'-])(?:" + body + r")(?![\w-])", re.I)


CAUSAL_CONNECTIVES_RE = _build_phrase_re(CAUSAL_CONNECTIVES_EN)
CAUSAL_SENTENCE_INITIAL_RE = re.compile(
    r"(?:^|[.!?]\s+|[\"“”]\s*)(?:" + "|".join(CAUSAL_SENTENCE_INITIAL_EN) + r")\b", re.I)
HEDGE_RE_BASE = _build_phrase_re(HEDGE_MARKERS_EN)
HEDGE_RE_CAN_WOULD = _build_phrase_re(HEDGE_CAN_WOULD_EN)
HEDGE_ATTRIBUTION_RE = re.compile(
    r"\b(?:" + "|".join(HEDGE_ATTRIBUTION_SUBJECTS_EN) + r")\s+(?:" + "|".join(HEDGE_ATTRIBUTION_VERBS_EN) + r")\b", re.I)


def causal_vocab_hits(claim_text: str, can_would_as_hedge=None) -> dict:
    """claim文(英語)の因果接続語・ヘッジ語の一致を返す(決定論・¥0)。`can_would_as_hedge`省略時は
    `CAUSAL_FLOOR_CAN_WOULD_AS_HEDGE`。"""
    c = _norm_apostrophe(claim_text)
    cw = CAUSAL_FLOOR_CAN_WOULD_AS_HEDGE if can_would_as_hedge is None else bool(can_would_as_hedge)
    conn = [m.group(0).lower() for m in CAUSAL_CONNECTIVES_RE.finditer(c)]
    if CAUSAL_SENTENCE_INITIAL_RE.search(c):
        conn.append("following(sentence_initial)")
    hedge = [m.group(0).lower() for m in HEDGE_RE_BASE.finditer(c)]
    hedge += [m.group(0).lower() for m in HEDGE_ATTRIBUTION_RE.finditer(c)]
    if cw:
        hedge += [m.group(0).lower() for m in HEDGE_RE_CAN_WOULD.finditer(c)]
    return {"connectives": conn, "hedges": hedge}


def causal_floor_guard(dev: dict, claim_text: str, can_would_as_hedge=None) -> tuple:
    """Tier 0 因果floor: 英語claim ∧ `changed_causality` ∧ 因果接続語 ∧ ヘッジ語なし。(blocked, reason)。
    reason=`changed_causality_floor`。日本語文字を含むclaimは対象外。"""
    c = claim_text or ""
    if _AUX_JA_RE.search(c) or not (dev or {}).get("changed_causality"):
        return False, ""
    if CAUSAL_FLOOR_VOCAB == "known6":
        if AUX_CONN_RE.search(_norm_apostrophe(c)) and not AUX_HEDGE_RE.search(_norm_apostrophe(c)):
            return True, "changed_causality_floor"
        return False, ""
    if CAUSAL_FLOOR_VOCAB != "inventory":
        raise ValueError(f"unknown CAUSAL_FLOOR_VOCAB: {CAUSAL_FLOOR_VOCAB!r}")
    h = causal_vocab_hits(c, can_would_as_hedge)
    if h["connectives"] and not h["hedges"]:
        return True, "changed_causality_floor"
    return False, ""


def ledger_block_fields(block) -> dict:
    """関連factブロック(Ledger逐語、複数factは連結済み)から`causal_strength`/`notes_for_writer`/`conditions`/`scope`を取る
    (各キー: 出現順のlist)。構造化欄が無ければ空list。"""
    out = {"causal_strength": [], "notes_for_writer": [], "conditions": [], "scope": []}
    for ln in (block or "").split("\n"):
        m = _GL_FIELD_RE.match(ln)
        if m:
            out[m.group(1)].append(m.group(2).strip())
    return out


def g_l_guard(dev: dict, block) -> tuple:
    """Tier 0 G_L: (blocked, reason)。判別力は`replay_guards_03_gl.py`で評価。
    (1) changed_causality ∧ Ledger関連factの`causal_strength`∈{CAUSAL_STATED_BY_SOURCE, CORRELATIONAL}
    (2) changed_causality ∧ `notes_for_writer`に因果の禁止文  (3) changed_certainty ∧ `notes_for_writer`に断定の禁止文"""
    f = ledger_block_fields(block)
    if dev.get("changed_causality"):
        for v in f["causal_strength"]:
            if v in GL_CAUSAL_STRENGTH_BLOCK_VALUES:
                return True, "gl_causal_strength:" + v
        for n in f["notes_for_writer"]:
            if GL_CAUSAL_PROHIBIT_RE.search(n):
                return True, "gl_notes_causal"
    if dev.get("changed_certainty"):
        for n in f["notes_for_writer"]:
            if GL_CERTAINTY_PROHIBIT_RE.search(n):
                return True, "gl_notes_certainty"
    return False, ""


def g_h_guard(dev: dict, claim_text: str) -> tuple:
    """補助ベルトG_H: 英語claim ∧ changed_causality ∧ 因果接続語 ∧ ヘッジ語なし。"""
    c = claim_text or ""
    if (not _AUX_JA_RE.search(c)) and dev.get("changed_causality") and AUX_CONN_RE.search(c) and not AUX_HEDGE_RE.search(c):
        return True, "aux:g_h"
    return False, ""


def issue_actor_guard(dev: dict, claim_text: str) -> tuple:
    """補助ベルトissue_actor: 英語claim ∧ Checker issue文が支払者・責任主体等の主体付与を名指し。"""
    if (not _AUX_JA_RE.search(claim_text or "")) and AUX_ACTOR_ISSUE_RE.search(dev.get("issue") or ""):
        return True, "aux:issue_actor"
    return False, ""


def stage2_release_guard(claim: dict, ledger_fact, article_ctx=None) -> tuple:
    """Tier 0: (blocked: bool, reason: str)。claim=`claim_text`と`dev`を持つdict、ledger_fact=関連factブロック(Ledger逐語、
    無ければNone)。G_Lを先に、次に補助ベルト(`reason`は`aux:`接頭辞)。決定論・¥0。`article_ctx`は将来用(現状未使用)。"""
    dev = claim.get("dev") or {}
    if TIER0_G_L_ENABLED:
        hit, reason = g_l_guard(dev, ledger_fact)
        if hit:
            return True, reason
    # 委任_03: 因果floor(語彙は目録由来、`CAUSAL_FLOOR`ON時のみ)。補助ベルトG_H/issue_actorの前に評価する。
    if CAUSAL_FLOOR:
        hit, reason = causal_floor_guard(dev, claim.get("claim_text") or "")
        if hit:
            return True, reason
    hit, reason = g_h_guard(dev, claim.get("claim_text") or "")
    if hit:
        return True, reason
    hit, reason = issue_actor_guard(dev, claim.get("claim_text") or "")
    if hit:
        return True, reason
    return False, ""


# ---- Tier 1: 確認役(floor_verifyの一般化)。rubricは最初から単一定義(Opus#11論点4: ACCEPTABLE重複定義を持ち込まない)。
DV_RUBRIC = """【判定の唯一の基準】
英語学習者に、記事の本質について重大な誤解を与えるものだけを止めます(UPHOLD_BLOCKING)。それ以外は解除します(RELEASE)。
正式な基準(3定義、Stage 2の基底rubricと同一の文言)は次のとおりです。
- BLOCKING(以下のいずれかに明確に該当する場合のみ):
  (a) Ledgerのclaim/scope/numeric_value/date_or_period/conditionsのいずれかと矛盾する。
  (b) Ledgerに無い人物・数字・出来事・具体的な行動・仕組み(メカニズム)を新たに追加している(例: 確認されていない具体的な売買行動を事実として追加する、確認されていない仕組み・運用フローを新規主張する)。
  (c) 根拠のない人物・組織の意図や動機を断定している。
  (d) Ledgerが記録した事実と逆方向の因果を述べている(Ledgerが原因Xを明記しているのに、正反対または別の特定の原因を断定する)。
  (e) 主体・数値・否定・比較・時期のいずれかについて、Ledgerと矛盾する重大な変更を加えている。
- QUALITY(解除してよい): 確認済みのFact同士を、人間が普通に読めば自然に導く範囲でつないだ解釈。断定がやや強い場合や、一つの解釈として自然に成り立つ推測を含む。上記BLOCKING(a)〜(e)に明確に該当しない限りQUALITYです。
- ACCEPTABLE(解除してよい): Ledgerに無い新規の固有名詞・数値・時期・主体・因果・仕組みを一切加えず、Ledgerが確認した事象の一般常識レベルの背景説明・条件付きの一般論にとどまる。
BLOCKINGに該当するかどうか、またはどの定義に当たるか判断に迷う場合は、UPHOLD_BLOCKINGとしてください(fail-closed)。
Checkerの指摘は検証すべき仮説です。仮説が正しいかを、関連factブロックの該当箇所を逐語で引用して(ledger_citation)検証してください。
引用できない場合、判断できない場合も、UPHOLD_BLOCKINGとしてください。"""

DV_DEVELOPER_MESSAGE = (
    "あなたはVerified Fact LedgerとFact Safetyの独立監査担当です。別の判定者が重大(BLOCKING)ではないと判定した"
    "claimについて、Checkerの指摘を検証すべき仮説として、Ledgerの該当箇所を逐語で引用して独立に再評価してください。")

DV_PROMPT_TEMPLATE = """これは、重大(BLOCKING)ではないと一度判定された指摘の、独立した確認です。
以下の関連factブロック(Ledger逐語)・対象claim・ローカル文脈・Checkerの指摘(仮説)だけを見て、
あなた自身の判断でverdictを決めてください。

【関連factブロック(Verified Fact Ledgerより逐語、fact_id={related_fact_id})】
{fact_block}

【対象claim(確定範囲)】
{claim_text}

【対象claimを含む段落±1段落(ローカル文脈)】
{local_context}

【Checkerの指摘(検証すべき仮説)】
Checkerは次の問題を指摘した: {issue}
この指摘が正しいか、Ledgerの該当箇所を引用して検証せよ。

{rubric}

verdict(UPHOLD_BLOCKING/RELEASE)、ledger_citation(関連factブロックからの逐語引用。一字一句そのまま。
要約・言い換え禁止。関連factブロックの連続した1か所[1行の一部、または1行全体]だけを引用すること。
離れた行・欄[例: 見出し行とconditions行]をつなげて1つの引用にしてはいけない[つなげると無効になる])、
basis(判定根拠の分類)、explanation(短い説明)を返してください。"""

DV_JSON_SCHEMA = {
    "name": "open233_downgrade_verify_v1",
    "schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["UPHOLD_BLOCKING", "RELEASE"]},
            "ledger_citation": {"type": "string"},
            "basis": {"type": "string", "enum": [
                "ledger_claim", "ledger_scope", "ledger_numeric_value", "ledger_date_or_period",
                "ledger_conditions", "notes_for_writer", "unsupported_relationship", "nuance_only", "none"]},
            "explanation": {"type": "string"},
        },
        "required": ["verdict", "ledger_citation", "basis", "explanation"],
        "additionalProperties": False,
    },
    "strict": True,
}
DV_VERDICTS = ("UPHOLD_BLOCKING", "RELEASE")


def downgrade_verify_target(dev: dict, final_materiality, floor_verify_rec, detected_by) -> tuple:
    """(is_target, reason)。Checker severity=MAJOR ∧ Stage 2最終materiality∈{QUALITY, ACCEPTABLE} ∧ floor_verifyで
    解放済みでない ∧ precheckでない。QUALITYとACCEPTABLEで要件は同一。"""
    if not STAGE2_DOWNGRADE_VERIFY:
        return False, "switch_off"
    return checker_major_downgraded_target(dev, final_materiality, floor_verify_rec, detected_by)


def checker_major_downgraded_target(dev: dict, final_materiality, floor_verify_rec, detected_by) -> tuple:
    """スイッチ非依存の対象判定(確認役・Tier 0・S1共通): Checker severity=MAJOR ∧ Stage 2最終materiality非BLOCKING ∧
    floor_verify解放済みでない ∧ precheckでない。"""
    if (dev or {}).get("severity") != "MAJOR":
        return False, "not_checker_major"
    if final_materiality not in ("QUALITY", "ACCEPTABLE"):
        return False, "final_blocking"
    if (floor_verify_rec or {}).get("released"):
        return False, "floor_verify_released"
    if detected_by == "precheck":
        return False, "precheck"
    return True, "checker_major_downgraded"


def run_downgrade_verify_call(client, claim_text: str, local_context: str, fact_block: str, issue: str,
                               related_fact_id: str = "", rubric_text: str | None = None,
                               model: str = MODEL) -> dict:
    """確認役1回分(claim 1件、batchに混ぜない)。Stage 2と同じモデル・reasoning設定(floor_verifyと同じ)。"""
    rubric = rubric_text if rubric_text is not None else DV_RUBRIC
    prompt = DV_PROMPT_TEMPLATE.format(
        related_fact_id=related_fact_id or "(不明)", fact_block=fact_block, claim_text=claim_text,
        local_context=local_context or "(なし)", issue=issue or "(指摘文なし)", rubric=rubric)
    t0 = time.time()
    response = client.responses.create(
        model=model,
        reasoning={"effort": vfl01.REASONING_EFFORT},
        text={"format": {"type": "json_schema", **DV_JSON_SCHEMA}},
        input=[{"role": "developer", "content": DV_DEVELOPER_MESSAGE},
               {"role": "user", "content": prompt}],
    )
    elapsed = round(time.time() - t0, 3)
    parsed = json.loads(response.output_text)
    usage = s2p._extract_usage(response)
    return {"prompt_sha256": s2p.sha256_text(prompt), "parsed": parsed, "model": response.model,
            "response_id": response.id, "usage": usage,
            "cost_jpy": round(s2p.official_cost_jpy(usage), 4), "elapsed_seconds": elapsed}


def _dv_validate_call(res: dict, fact_block: str) -> dict:
    """verdictがenum内・引用が空でなく関連factブロックの逐語(`_fv_norm`による空白・引用符字形の正規化後)であることだけを
    決定論で検査する(逐語引用は「Ledgerと向き合った根拠が監査できる形で残る」ことと捏造引用の排除までの保証)。"""
    p = res.get("parsed") or {}
    rec = {"verdict": p.get("verdict"), "basis": p.get("basis"), "ledger_citation": p.get("ledger_citation"),
           "explanation": p.get("explanation"), "prompt_sha256": res.get("prompt_sha256"),
           "cost_jpy": res.get("cost_jpy", 0.0), "response_id": res.get("response_id"), "valid": False,
           "invalid_reason": None, "citation_verbatim": False}
    if p.get("verdict") not in DV_VERDICTS or not isinstance(p.get("ledger_citation"), str):
        rec["invalid_reason"] = "schema_mismatch"
        return rec
    cit = _fv_norm(p["ledger_citation"])
    if not cit:
        rec["invalid_reason"] = "ledger_citation_empty"
        return rec
    rec["citation_verbatim"] = cit in _fv_norm(fact_block)
    if not rec["citation_verbatim"]:
        rec["invalid_reason"] = "ledger_citation_not_verbatim"
        return rec
    rec["valid"] = True
    return rec


def _dv_strip_quotes(s: str) -> str:
    return re.sub(r"[「」『』“”\"]", "", s or "").strip()


def downgrade_verify_rewrite_hint(dev: dict, block) -> tuple:
    """Tier 2: 解除不可にしたclaimの`rewrite_hint`(決定論)。Checkerのissue/explanation+Ledgerの`notes_for_writer`/
    `conditions`から合成する(Stage 2のhintは降格時には空のため)。引用符は除く(対象文の特定に使われる
    `extract_quoted_fragment`へ、Ledger文の引用断片が混入しないようにする)。戻り値(hint, hint_source)。"""
    f = ledger_block_fields(block)
    issue = _dv_strip_quotes((dev or {}).get("issue") or (dev or {}).get("explanation") or "")
    parts = []
    if issue:
        parts.append("Checkerの指摘: " + issue[:400])
    fid = (dev or {}).get("related_fact_id") or ""
    notes = [_dv_strip_quotes(n) for n in f["notes_for_writer"] if n]
    conds = [_dv_strip_quotes(c) for c in f["conditions"] if c]
    if notes:
        parts.append("Ledgerのnotes_for_writer: " + " / ".join(notes)[:400])
    if conds:
        parts.append("Ledgerのconditions: " + " / ".join(conds)[:300])
    parts.append(f"fact_id={fid}のLedgerが確認している範囲に収まるよう、該当文から未確認の因果・主体・断定・範囲の拡大を除いて書き直す。")
    src = ["checker_issue" if issue else None, "ledger_notes_for_writer" if notes else None,
           "ledger_conditions" if conds else None]
    return " ".join(parts), "+".join(x for x in src if x) or "generic"


def downgrade_verify_evaluate(call_fn, ledger_text: str, claim: dict, local_context: str, dev: dict,
                               final_materiality: str, floor_verify_rec, detected_by: str) -> dict:
    """1 claimの降格確認の全体判定。`call_fn(claim_text, local_context, fact_block, issue, related_fact_id)`は
    `run_downgrade_verify_call`互換のdictを返すか`FloorVerifyCallError`を送出する。戻り値の`released`がTrueのときだけ
    Stage 2の最終materialityを維持する。それ以外(`target`がTrue)は`blocking`=True(BLOCKINGへ戻す)で、Rewrite経路へ進む
    (Human Reviewへ倒す新経路なし)。"""
    is_target, reason = downgrade_verify_target(dev, final_materiality, floor_verify_rec, detected_by)
    dv = {"switch": STAGE2_DOWNGRADE_VERIFY, "target": is_target, "target_reason": reason,
          "stage2_final_materiality": final_materiality, "tier0_blocked": False, "tier0_reason": None,
          "fact_block_found": None, "call": None, "n_calls": 0, "released": False, "blocking": False,
          "blocking_reason": None, "hint": None, "hint_source": None, "cost_jpy": 0.0}
    if not is_target:
        return dv
    fact_id = dev.get("related_fact_id")
    fact_block = floor_verify_fact_block(ledger_text, fact_id)
    dv["fact_block_found"] = fact_block is not None
    blocked, g_reason = stage2_release_guard(claim, fact_block)
    if blocked:
        dv.update(tier0_blocked=True, tier0_reason=g_reason, blocking=True, blocking_reason="tier0:" + g_reason)
    elif fact_block is None:
        # 引用できる関連factブロックが無く解除条件(逐語引用)を満たせない=BLOCKING維持(Tier 2。呼び出し省略、費用なし)
        dv.update(blocking=True, blocking_reason="fact_block_unavailable")
    else:
        issue = dev.get("issue") or dev.get("explanation") or ""
        try:
            res = call_fn(claim.get("claim_text") or "", local_context, fact_block, issue, fact_id or "")
        except FloorVerifyCallError as e:
            dv["call"] = {"valid": False, "invalid_reason": f"api_failure: {e}"}
            dv["n_calls"] = 1
            dv.update(blocking=True, blocking_reason="verify_api_failure")
        else:
            rec = _dv_validate_call(res, fact_block)
            dv["call"], dv["n_calls"] = rec, 1
            dv["cost_jpy"] = round(rec.get("cost_jpy") or 0.0, 4)
            if not rec["valid"]:
                dv.update(blocking=True, blocking_reason=rec["invalid_reason"])
            elif rec["verdict"] != "RELEASE":
                dv.update(blocking=True, blocking_reason="verify_upheld_blocking")
            else:
                dv["released"] = True
    if dv["blocking"]:
        dv["hint"], dv["hint_source"] = downgrade_verify_rewrite_hint(dev, fact_block)
    return dv


def downgrade_verify_summarize(stage2_results_iter) -> dict:
    """runtime evidence用の集計(対象/Tier 0該当[理由別]/確認call数/RELEASE/UPHOLD/非逐語/失敗/費用)。`downgrade_verify`
    フィールドを持つclaimのみ対象。"""
    s = {"n_records": 0, "n_target": 0, "n_tier0_blocked": 0, "tier0_by_reason": {}, "n_verify_calls": 0,
         "n_released": 0, "n_upheld": 0, "n_citation_not_verbatim": 0, "n_failure": 0, "n_fact_block_unavailable": 0,
         "blocking_by_reason": {}, "cost_jpy": 0.0}
    for r in stage2_results_iter:
        dv = r.get("downgrade_verify")
        if not dv:
            continue
        s["n_records"] += 1
        if not dv["target"]:
            continue
        s["n_target"] += 1
        s["n_verify_calls"] += dv["n_calls"]
        s["cost_jpy"] = round(s["cost_jpy"] + dv.get("cost_jpy", 0.0), 4)
        if dv["tier0_blocked"]:
            s["n_tier0_blocked"] += 1
            k = dv["tier0_reason"] or "?"
            s["tier0_by_reason"][k] = s["tier0_by_reason"].get(k, 0) + 1
        elif dv["released"]:
            s["n_released"] += 1
        else:
            br = dv["blocking_reason"] or "unknown"
            s["blocking_by_reason"][br] = s["blocking_by_reason"].get(br, 0) + 1
            if br == "verify_upheld_blocking":
                s["n_upheld"] += 1
            elif br in ("ledger_citation_not_verbatim", "ledger_citation_empty"):
                s["n_citation_not_verbatim"] += 1
            elif br in ("verify_api_failure", "schema_mismatch"):
                s["n_failure"] += 1
            elif br == "fact_block_unavailable":
                s["n_fact_block_unavailable"] += 1
    return s


def observe_section_type(claim_text: str, full_text: str) -> str:
    """委任_02 作業2-7(記録専用、判定・振り分けには使わない): claimの本文断片(引用符内、無ければclaim全体)が、title/
    `## In one line`直下/hook段落の各テキストに(正規化後)含まれるかの単純包含で区分を観測する。`detect_claim_section_type`
    (確定範囲による包含判定)が`body`を返すclaimを、In one lineとして記録上だけ区別する(Opus#11補1の計測是正)。"""
    if not full_text:
        return "body"
    claim = (claim_text or "").strip()
    frags = [f[2] for f in _vs_explain_extract_fragments(claim)[0]] or [claim]
    probes = [vs_norm_str(x, True) for x in frags if x and x.strip()]
    blocks = (("title", _paragraph_title(full_text)), ("in_one_line", _extract_in_one_line_text(full_text)),
              ("hook", _hook_paragraph_block(full_text)))
    for name, block in blocks:
        nb = vs_norm_str(block or "", True)
        if nb and any(len(p) >= 12 and (p in nb or (len(nb) > 12 and nb in p)) for p in probes):
            return name
    return "body"


def sentence_restore_summarize(instance_results) -> dict:
    """委任_66 runtime evidence用の集計(L6発火/復元成功/候補0/候補複数/ガード不通過(理由別)/issue_focus_absent/
    2文復元の焦点文ガード発火)。Rewrite記録(`rewrite_records[*].handoff`)の`sentence_restore`を数える。
    発火=statusがrestored/cand0/cand_multi/guard_rejected(not_fired/not_applicableは数えない)。"""
    s = {"n_records_with_l6_attempt": 0, "l6_fired": 0, "restored": 0, "restored_two_sentences": 0, "cand0": 0,
         "cand_multi": 0, "guard_rejected": 0, "guard_rejected_by_reason": {}, "not_fired_or_na": 0,
         "exception": 0, "issue_focus_absent": 0, "focus_guard_fired": 0, "restored_claims": []}
    for res in instance_results:
        for cyc in res.get("cycles", []):
            for rr in cyc.get("rewrite_records", []) or []:
                h = rr.get("handoff") or {}
                sr = h.get("sentence_restore") or (h.get("resolution") or {}).get("sentence_restore")
                if not sr:
                    continue
                s["n_records_with_l6_attempt"] += 1
                st = sr.get("status")
                if st in ("restored", "cand0", "cand_multi", "guard_rejected"):
                    s["l6_fired"] += 1
                if st == "restored":
                    s["restored"] += 1
                    if sr.get("n_sentences") == 2:
                        s["restored_two_sentences"] += 1
                    s["restored_claims"].append({"instance": res.get("instance_id"), "cycle": cyc.get("cycle"),
                                                 "claim": sr.get("original_claim"), "restored": sr.get("restored_sentence")})
                elif st in ("cand0", "cand_multi"):
                    s[st] += 1
                elif st == "guard_rejected":
                    s["guard_rejected"] += 1
                    k = str(sr.get("reason"))
                    s["guard_rejected_by_reason"][k] = s["guard_rejected_by_reason"].get(k, 0) + 1
                elif st == "exception":
                    s["exception"] += 1
                else:
                    s["not_fired_or_na"] += 1
                if h.get("issue_focus_absent"):
                    s["issue_focus_absent"] += 1
                if h.get("focus_guard_fired"):
                    s["focus_guard_fired"] += 1
    return s


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
        # 委任_60(案1、既定OFF): 比較・時期のfloorだけがBLOCKINGにした指摘の追加確認。
        # 基準は`llm_materiality`(上の`materiality`)で、`apply_floor`の結果を上書きする形では
        # なく、確認が解放を確定した場合だけ最終値を別途セットする(`dev`は書き換えない)。
        # cycleごと・Recheck由来も同じ経路(run_stage2は毎周回呼ばれ、状態は引き継がない)。
        floor_verify_rec = None
        if (FLOOR_VERIFY_MODE != FLOOR_VERIFY_MODE_OFF and floor_applied
                and i not in failclosed_indices and judgments_by_index.get(i) is not None):
            def _fv_call(claim_text, local_context, fact_block, issue, flag_names, related_fact_id,
                         _i=i):
                check_budget(state)
                vlabel = f"{label}_floorverify_c{_i}_{len(call_log)}"
                try:
                    res = run_floor_verify_call(client, claim_text, local_context, fact_block, issue,
                                                flag_names, related_fact_id, model=MODEL)
                except Exception as e:  # noqa: BLE001
                    call_log.append({"label": vlabel, "recovery_stage": "floor_verify",
                                      "error": f"{type(e).__name__}: {e}"})
                    record_call(state, consecutive_errors, vlabel, 0.0, False, "floor_verify")
                    raise FloorVerifyCallError(f"{type(e).__name__}: {e}") from e
                call_log.append({"label": vlabel, "recovery_stage": "floor_verify",
                                  "cost_jpy": res["cost_jpy"], "usage": res["usage"],
                                  "elapsed_seconds": res["elapsed_seconds"],
                                  "prompt_sha256": res["prompt_sha256"]})
                record_call(state, consecutive_errors, vlabel, res["cost_jpy"], True, "floor_verify",
                            res["usage"])
                return res
            floor_verify_rec = floor_verify_evaluate(
                _fv_call, fixture["ledger_text"], c["claim_text"], c.get("local_context", ""),
                dev_for_floor, materiality, floor_applied)
            if floor_verify_rec["released"]:
                final_materiality = floor_verify_rec["final_materiality"]
                floor_reason = "floor_verify_released:" + floor_applied
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
        # 委任_02(Opus#11→Fable評価1〜3、既定OFF`STAGE2_DOWNGRADE_VERIFY`): Checker MAJORをStage 2が非BLOCKINGにした
        # もの(最終値、floor/hook/disclosure適用後)を、Tier 0(決定論Guard)→Tier 1(確認役、call 1回)で再確認する。
        # 解除できないもの(Tier 0該当/UPHOLD/非逐語/失敗)はBLOCKINGへ戻し、Tier 2のhintを付けて既存Rewriteラダーへ
        # (Human Reviewへ倒す新経路なし)。`run_stage2`は毎cycle呼ばれるため現行本文で毎回再評価される。
        downgrade_verify_rec = None
        if STAGE2_DOWNGRADE_VERIFY and i not in failclosed_indices and judgments_by_index.get(i) is not None:
            def _dv_call(claim_text, local_context, fact_block, issue, related_fact_id, _i=i):
                check_budget(state)
                vlabel = f"{label}_dgverify_c{_i}_{len(call_log)}"
                try:
                    res = run_downgrade_verify_call(client, claim_text, local_context, fact_block, issue,
                                                    related_fact_id, model=MODEL)
                except Exception as e:  # noqa: BLE001
                    call_log.append({"label": vlabel, "recovery_stage": "downgrade_verify",
                                      "error": f"{type(e).__name__}: {e}"})
                    record_call(state, consecutive_errors, vlabel, 0.0, False, "downgrade_verify")
                    raise FloorVerifyCallError(f"{type(e).__name__}: {e}") from e
                call_log.append({"label": vlabel, "recovery_stage": "downgrade_verify",
                                  "cost_jpy": res["cost_jpy"], "usage": res["usage"],
                                  "elapsed_seconds": res["elapsed_seconds"],
                                  "prompt_sha256": res["prompt_sha256"]})
                record_call(state, consecutive_errors, vlabel, res["cost_jpy"], True, "downgrade_verify",
                            res["usage"])
                return res
            downgrade_verify_rec = downgrade_verify_evaluate(
                _dv_call, fixture["ledger_text"], {**c, "dev": dev_for_floor}, c.get("local_context", ""),
                dev_for_floor, final_materiality, floor_verify_rec, detected_by)
            if downgrade_verify_rec["target"] and downgrade_verify_rec["blocking"]:
                final_materiality = "BLOCKING"
                floor_reason = "downgrade_verify_blocking:" + str(downgrade_verify_rec["blocking_reason"])
                rewrite_hint = ((downgrade_verify_rec["hint"] + (" " + rewrite_hint if rewrite_hint else ""))
                                if downgrade_verify_rec["hint"] else rewrite_hint)
        # 委任_03(Fable再設計判断3): Tier 0 決定論Guard(因果floor+補助ベルト)。Checker MAJORをStage 2が非BLOCKINGにした
        # もの(最終値、floor/hook/disclosure適用後。確認役が既に処理した分は対象外)を、文面確認でBLOCKINGへ戻す(¥0)。
        # 解除不可claimはTier 2のhintを付けて既存Rewriteラダーへ(Human Reviewへ倒す新経路なし)。毎cycle現行本文で再評価。
        tier0_rec = None
        if (CAUSAL_FLOOR and i not in failclosed_indices and judgments_by_index.get(i) is not None
                and not (downgrade_verify_rec and downgrade_verify_rec.get("target"))):
            t0_target, t0_target_reason = checker_major_downgraded_target(
                dev_for_floor, final_materiality, floor_verify_rec, detected_by)
            tier0_rec = {"target": t0_target, "target_reason": t0_target_reason, "blocked": False, "reason": None,
                         "hint": None, "hint_source": None}
            if t0_target:
                _blk = floor_verify_fact_block(fixture["ledger_text"], dev_for_floor.get("related_fact_id"))
                t0_blocked, t0_reason = stage2_release_guard({**c, "dev": dev_for_floor}, _blk)
                if t0_blocked:
                    tier0_rec.update(blocked=True, reason=t0_reason)
                    tier0_rec["hint"], tier0_rec["hint_source"] = downgrade_verify_rewrite_hint(dev_for_floor, _blk)
                    final_materiality = "BLOCKING"
                    floor_reason = ("changed_causality_floor" if t0_reason == "changed_causality_floor"
                                    else "tier0:" + t0_reason)
                    rewrite_hint = ((tier0_rec["hint"] + (" " + rewrite_hint if rewrite_hint else ""))
                                    if tier0_rec["hint"] else rewrite_hint)
        out.append({**c, "dev": dev_for_floor, "materiality": final_materiality, "llm_materiality": materiality,
                    "basis": basis,
                    "rewrite_kind": rewrite_kind if rewrite_kind != "none" else "replace_with_ledger_value",
                    "rewrite_hint": rewrite_hint, "floor_reason": floor_reason,
                    "section_type": section_type,
                    # 委任_02 作業2-7(記録専用、判定は変えない): `detect_claim_section_type`が`body`でも、本文断片が
                    # `## In one line`直下等に含まれる場合の観測値(Opus#11補1の計測是正)。
                    "section_type_observed": observe_section_type(c["claim_text"], fixture["article_text"]),
                    # 委任_17: このclaimがStage2のどちらの経路(body=s2c.
                    # RUBRIC_R3_TRIPLE_PRIME/hook=s2h Hook専用Stage2)を
                    # 通ったかのEvidence(¥0、call_logのlabel/stage2_variant
                    # と同じ情報をclaim単位でも直接確認できるようにする)。
                    "stage2_route": stage2_route_by_index.get(i, "unknown"),
                    "floor_cited_materiality": cited_materiality, "floor_cited_reason": cited_floor_applied,
                    # 委任_60: 追加確認の記録(スイッチ有効かつdeterministic floor発火のclaimのみ。
                    # 既定OFFでは付かない=従来の出力と同一)。
                    **({"floor_verify": floor_verify_rec} if floor_verify_rec is not None else {}),
                    # 委任_02: 降格確認(Tier 0/1/2)の記録(スイッチ有効のclaimのみ。既定OFFでは付かない)。
                    **({"downgrade_verify": downgrade_verify_rec} if downgrade_verify_rec is not None else {}),
                    # 委任_03: Tier 0(因果floor/補助ベルト)の記録(`CAUSAL_FLOOR`ONのclaimのみ。OFFでは付かない)。
                    **({"tier0": tier0_rec} if tier0_rec is not None else {})})
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
        # 委任_60: 追加確認で解放済みのclaimはそれ以上動かさない(降格対象から外す)。
        and not (result.get("floor_verify") or {}).get("released")
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
# 委任_03(OPEN-233-KPI-RECOVERY-REDESIGN-02、Fable再設計判断5): Tier 1' S1(Stage 2第2意見、Trial専用・既定OFF
# `STAGE2_SECOND_OPINION`、Production未配線・`APPROVED_FOR_PRODUCTION`ではない)。仕様は
# `docs/pm/design_open233_stage2_safety_downgrade_01.md` §8(Opus#10の3修正)。既存`apply_stage2_two_of_two`
# (NORMAL群限定・BLOCKING→降格の向き)とは別関数で、向きが逆(降格を確定させる条件を厳しくする)。
#   対象: Checker MAJOR ∧ Stage 2 1回目の最終materiality非BLOCKING ∧ floor_verify解放済みでない ∧ precheckでない。
#   第2意見: 対象claimのみのbatch(`run_stage2`、body/hookはclaimごとの経路どおり、同一rubric・本文・Ledger)。比較は
#   第2回の最終`materiality`(hook-aware/disclosure降格後)。割れたら(第2回がBLOCKING)BLOCKING。API失敗・schema不一致・
#   claim_index欠落は`run_stage2`のfail-closed(BLOCKING)をそのまま採用。2回とも非BLOCKINGなら重い方を採用(安全側)。
#   Tier 2: 割れたclaimにも`downgrade_verify_rewrite_hint`のhintを付ける(Human Reviewへ倒す新経路なし)。
# ------------------------------------------------------------
S1_MATERIALITY_RANK = {"ACCEPTABLE": 1, "QUALITY": 2, "BLOCKING": 3}


def stage2_second_opinion_eligible(result: dict) -> bool:
    return bool(
        result.get("materiality") != "BLOCKING"
        and (result.get("dev") or {}).get("severity") == "MAJOR"
        and not (result.get("floor_verify") or {}).get("released")
        and result.get("detected_by", "stage1_llm") != "precheck"
        and result.get("stage2_route") != "precheck_floor_bypass"
        and result.get("llm_materiality") is not None)


def _s1_second_status(r2: dict) -> str:
    fr = r2.get("floor_reason")
    if fr == "stage2_api_failure_failclosed":
        return "api_failure"
    if fr == "schema_index_mismatch_failclosed":
        return "schema_mismatch"
    return "ok"


def apply_stage2_second_opinion(client, state, consecutive_errors, call_log, label_prefix, fixture,
                                stage2_results: list, instance_id=None, cycle=None) -> tuple:
    """(新stage2_results, `stage2_downgrade_confirm_log`のlist)。対象が無ければcallせず(results, [])。"""
    eligible_idx = [i for i, r in enumerate(stage2_results) if stage2_second_opinion_eligible(r)]
    if not eligible_idx:
        return stage2_results, []
    n_before = len(call_log)
    claims = [{"claim_text": stage2_results[i]["claim_text"], "origin": stage2_results[i].get("origin"),
               "related_fact_id": stage2_results[i].get("related_fact_id"), "dev": stage2_results[i]["dev"],
               "detected_by": stage2_results[i].get("detected_by", "stage1_llm")} for i in eligible_idx]
    second = run_stage2(client, state, consecutive_errors, call_log, f"{label_prefix}_s1", fixture, claims)
    new_calls = call_log[n_before:]
    batch_cost = round(sum(c.get("cost_jpy") or 0.0 for c in new_calls), 4)
    shas = [c.get("prompt_sha256") for c in new_calls if c.get("prompt_sha256")]
    out = list(stage2_results)
    log = []
    for k, i in enumerate(eligible_idx):
        r, r2 = stage2_results[i], second[k]
        status = _s1_second_status(r2)
        split = r2["materiality"] == "BLOCKING"
        anomaly = bool(r2.get("floor_reason")) and status == "ok"
        rec = {"instance_id": instance_id, "cycle": cycle, "route": r.get("stage2_route"),
               "claim_identity": claim_identity(r["dev"]), "claim_text": (r.get("claim_text") or "")[:200],
               "first_materiality": r["materiality"], "first_basis": r.get("basis"),
               "second_materiality": r2["materiality"], "second_basis": r2.get("basis"),
               "second_floor_reason": r2.get("floor_reason"), "second_floor_anomaly": anomaly,
               "second_status": status, "confirmed_downgrade": not split, "split": split,
               "prompt_sha256": shas, "batch_cost_jpy": batch_cost, "batch_n_claims": len(eligible_idx)}
        if split:
            block = floor_verify_fact_block(fixture["ledger_text"], (r["dev"] or {}).get("related_fact_id"))
            hint, hint_source = downgrade_verify_rewrite_hint(r["dev"], block)
            r2_hint = r2.get("rewrite_hint") or ""
            rec["hint_source"] = hint_source
            out[i] = {**r, "materiality": "BLOCKING",
                      "floor_reason": ("s1_second_opinion_failclosed:" + status if status != "ok"
                                       else "s1_second_opinion_blocking"),
                      "rewrite_kind": r2.get("rewrite_kind") or r.get("rewrite_kind") or "replace_with_ledger_value",
                      "rewrite_hint": (hint + (" " + r2_hint if r2_hint else "")),
                      "second_opinion": rec}
        else:
            heavier = max(r["materiality"], r2["materiality"], key=lambda m: S1_MATERIALITY_RANK.get(m, 3))
            out[i] = {**r, "materiality": heavier, "second_opinion": rec}
        log.append(rec)
    return out, log


def s1_summarize(instance_results) -> dict:
    """runtime evidence用の集計(対象/一致/割れ/失敗/異常/費用)。`cycles[*].stage2_downgrade_confirm_log`を数える。"""
    s = {"n_target": 0, "n_confirmed": 0, "n_split": 0, "n_api_failure": 0, "n_schema_mismatch": 0,
         "n_floor_anomaly": 0, "batches": 0, "cost_jpy": 0.0, "split_claims": []}
    for res in instance_results:
        for cyc in res.get("cycles", []):
            lg = cyc.get("stage2_downgrade_confirm_log") or []
            for e in lg:
                s["n_target"] += 1
                s["n_confirmed"] += 1 if e["confirmed_downgrade"] else 0
                s["n_split"] += 1 if e["split"] else 0
                s["n_api_failure"] += 1 if e["second_status"] == "api_failure" else 0
                s["n_schema_mismatch"] += 1 if e["second_status"] == "schema_mismatch" else 0
                s["n_floor_anomaly"] += 1 if e["second_floor_anomaly"] else 0
                if e["split"]:
                    s["split_claims"].append({"instance_id": res.get("instance_id"), "cycle": cyc.get("cycle"),
                                              "claim": e["claim_text"][:120], "second": e["second_materiality"],
                                              "status": e["second_status"]})
            if lg:
                # 同一cycleの全claimは同じbatch費用を共有する(重複計上しない。body/hook 2 callの合計が`batch_cost_jpy`)
                s["batches"] += 1
                s["cost_jpy"] = round(s["cost_jpy"] + lg[0]["batch_cost_jpy"], 4)
    return s


def tier0_summarize(instance_results) -> dict:
    """Tier 0(因果floor/補助ベルト)の発火集計。`stage2_results[*].tier0`を数える(対象/発火[理由別])。"""
    s = {"n_records": 0, "n_target": 0, "n_blocked": 0, "blocked_by_reason": {}, "blocked_claims": []}
    for res in instance_results:
        for cyc in res.get("cycles", []):
            for sr in cyc.get("stage2_results", []):
                t = sr.get("tier0")
                if not t:
                    continue
                s["n_records"] += 1
                if not t["target"]:
                    continue
                s["n_target"] += 1
                if t["blocked"]:
                    s["n_blocked"] += 1
                    s["blocked_by_reason"][t["reason"]] = s["blocked_by_reason"].get(t["reason"], 0) + 1
                    s["blocked_claims"].append({"instance_id": res.get("instance_id"), "cycle": cyc.get("cycle"),
                                                "reason": t["reason"], "claim": (sr.get("claim_text") or "")[:120]})
    return s


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


# ============================================================
# 委任_42(2026-10-02、OPEN-233 受け渡し修正、ユーザー指示§1・§2、設計書
# design_open233_violation_span_handoff_01.md、Opus L2レビュー#5反映)
# ------------------------------------------------------------
# 問題: Checkerが複数文を違反として返しているのに、後段(locate_target)が
# 判定役の引用・包含スパン・類似度・単語重なりで1文だけ選んでRewriteへ渡して
# いた(rep21 sample1 cycle1: 2文のclaimのうち1文しか対象にならず取りこぼし)。
# 是正(ユーザー基本線): ①Checkerが示した違反範囲を後段で再推測しない
# ②複数文は複数文のまま・離れた複数箇所は複数範囲として渡す ③別AI(判定役)の
# 引用でRewrite対象を決めない ④類似度・単語重なりで1文へ縮小しない
# ⑤文ID・文字オフセットは採用しない ⑥最小修正優先(語句→文全体→必要最小範囲)。
#
# 実装: `resolve_violation_spans`が、Checkerの文字列だけを入力に、次の
# **文字単位の照合のみ**で記事側の範囲を確定する(定義は無料集計
# `er052_output/open233_handoff_log_aggregation_01/aggregate_01.py`[委任_41]と
# 同一。importはせず移植):
#   L0 そのまま含まれる / L1 文字列全体を囲む1組の引用符・括弧を外す /
#   L2 空白・改行の連続・曲線/直線の引用符の同一視 / L3 大文字小文字の同一視 /
#   L4 引用断片が2つ以上あり、断片以外の残りがつなぎ語・句読点・空白だけの
#      場合に限り、各断片を別々の範囲にして各々L0〜L3で照合
#      (残りに説明文がある場合は分解せず確定不能)。
# 確定の条件=対象本文に「ちょうど1箇所」。0箇所・2箇所以上は確定不能。照合は
# EN本文・JA本文の両方に対して行い、どちらで確定したかを保持する。
# 確定不能の指摘は類似度等へ落とさず`violation_span_unverified`でStage 4。
# ============================================================
_VS_QUOTE_PAIRS = [("“", "”"), ('"', '"'), ("‘", "’"), ("「", "」"), ("『", "』")]
_VS_CURLY_MAP = {"’": "'", "‘": "'", "‚": "'", "‛": "'", "“": '"', "”": '"', "„": '"'}
_VS_FRAG_RE = re.compile(r"“([^”]+)”|「([^」]+)」|『([^』]+)』")
_VS_CONNECT_RE = re.compile(r"\b(and|or)\b|[&,;、，；と/／.。:：]|および|\s", re.I)
# 文分割(範囲を含む文全体への拡張[水準③]専用。確定には使わない)。改行も区切りとする。
_VS_SENT_END_RE = re.compile(r"[.!?]+[\"”’'」』)\]]*(?=\s|$)|[。！？]+[\"”’」』)\]]*|\n")


def vs_find_all(text: str, sub: str) -> list:
    out, i = [], 0
    if not sub:
        return out
    while True:
        j = text.find(sub, i)
        if j < 0:
            return out
        out.append((j, j + len(sub)))
        i = j + len(sub)


def vs_norm_with_map(text: str, lower: bool) -> tuple:
    chars, spans = [], []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            j = i
            while j < n and text[j].isspace():
                j += 1
            chars.append(" ")
            spans.append((i, j))
            i = j
            continue
        ch2 = _VS_CURLY_MAP.get(ch, ch)
        if lower:
            lo = ch2.lower()
            ch2 = lo if len(lo) == 1 else ch2
        chars.append(ch2)
        spans.append((i, i + 1))
        i += 1
    return "".join(chars), spans


def vs_norm_str(s: str, lower: bool) -> str:
    return vs_norm_with_map(s.strip(), lower)[0]


def vs_strip_one_pair(s: str):
    s = s.strip()
    if len(s) >= 2:
        for o, c in _VS_QUOTE_PAIRS:
            if s[0] == o and s[-1] == c:
                return s[1:-1].strip()
    return None


def _vs_wordch(text: str, i: int) -> bool:
    """位置iの文字が単語を構成するか(英数字・`_`、および英数字に挟まれたアポストロフィ)。"""
    if i < 0 or i >= len(text):
        return False
    ch = text[i]
    if ch.isalnum() or ch == "_":
        return True
    if ch in ("'", "’") and 0 < i < len(text) - 1 and text[i - 1].isalnum() and text[i + 1].isalnum():
        return True
    # 委任_66(Opus#9論点8、VS_MATCH_EXT配下・新スイッチなし): 数字に挟まれた`.`/`,`(2.6の`.`、1,000の`,`)は
    # 数値の一部=語構成文字。`2.6 percent`の`6 percent…`を「語境界を満たす」と誤って確定しない。
    if (VS_MATCH_EXT and ch in (".", ",") and 0 < i < len(text) - 1
            and text[i - 1].isdigit() and text[i + 1].isdigit()):
        return True
    return False


def vs_word_boundary_ok(text: str, span: tuple) -> bool:
    """委任_49(VS_MATCH_EXT): 一致箇所[a,b)の先頭側・末尾側の両方が単語境界か。一致箇所の端の文字が
    単語構成文字のとき、その外側の隣の文字が単語構成文字であれば境界ではない(語の途中への一致)。
    端の文字が句読点・引用符などの場合は、その外側がどうであれ境界とみなす。"""
    a, b = span
    if a >= b:
        return False
    if _vs_wordch(text, a) and _vs_wordch(text, a - 1):
        return False
    if _vs_wordch(text, b - 1) and _vs_wordch(text, b):
        return False
    return True


def vs_match_levels(cand: str, text: str, lang: str | None = None) -> tuple:
    """candをL0〜L3でtextへ照合する。返値 (status, level, stripped_used, spans)。
    status: 'ok'(ちょうど1箇所)/'multi'(2箇所以上)/'none'。
    委任_49: VS_MATCH_EXTがTrueかつlang=="EN"のとき、'ok'(ちょうど1箇所)に単語境界の条件を課す
    (満たさなければその段階では確定せず次の段階へ。複数箇所一致の扱いは変えない=確定が減る方向のみ)。
    VS_MATCH_EXTがFalseなら委任_42と同一の挙動。"""
    ext = VS_MATCH_EXT and lang == "EN"
    raw = cand.strip()
    stripped = vs_strip_one_pair(raw)
    for label, v, st in (("L0", raw, False), ("L1", stripped, True)):
        if v:
            occ = vs_find_all(text, v)
            if len(occ) == 1:
                if not ext or vs_word_boundary_ok(text, occ[0]):
                    return "ok", label, st, occ
            elif len(occ) >= 2:
                return "multi", label, st, occ
    for label, lower in (("L2", False), ("L3", True)):
        nt, nm = vs_norm_with_map(text, lower)
        for v, st in ((raw, False), (stripped, True)):
            if not v:
                continue
            nv = vs_norm_str(v, lower)
            if not nv:
                continue
            occ = vs_find_all(nt, nv)
            if len(occ) == 1:
                s, e = occ[0]
                sp = (nm[s][0], nm[e - 1][1])
                if not ext or vs_word_boundary_ok(text, sp):
                    return "ok", label, st, [sp]
            elif len(occ) >= 2:
                return "multi", label, st, [(nm[a][0], nm[b - 1][1]) for a, b in occ]
    return "none", None, False, []


def vs_edge_punct_match(claim: str, text: str, lang: str | None) -> dict | None:
    """委任_49 A1(VS_MATCH_EXT、英語本文のみ): 候補文字列の両端の句読点(`. , ; : ! ?`)を除いた
    文字列が本文にちょうど1箇所(一致箇所の先頭側・末尾側とも単語境界)なら確定とする。
    語は1字も足さない・落とさない・置換しない。文単位への拡張はしない。両端以外の句読点は除かない。
    返値: {"status": "ok"/"multi", "spans", "stripped", "edge_removed": (先頭側, 末尾側)} または None。"""
    if not VS_MATCH_EXT or lang != "EN":
        return None
    raw = claim.strip()
    for v, st in ((raw, False), (vs_strip_one_pair(raw), True)):
        if not v:
            continue
        core = v.strip()
        core2 = core.lstrip(VS_EDGE_PUNCT + " ")
        core3 = core2.rstrip(VS_EDGE_PUNCT + " ")
        if not core3 or core3 == core:
            continue
        lead = core[:len(core) - len(core2)]
        trail = core2[len(core3):]
        stt, _lv, _s, spans = vs_match_levels(core3, text, lang)
        if stt == "ok":
            return {"status": "ok", "spans": spans, "stripped": st, "edge_removed": (lead, trail)}
        if stt == "multi":
            return {"status": "multi", "spans": spans, "stripped": st, "edge_removed": (lead, trail)}
    return None


def vs_split_fragments(claim: str) -> tuple:
    frags = [next(g for g in m.groups() if g is not None) for m in _VS_FRAG_RE.finditer(claim)]
    rest = _VS_FRAG_RE.sub("", claim)
    rest_clean = _VS_CONNECT_RE.sub("", rest)
    return frags, rest, rest_clean


def vs_resolve_in_text(claim: str, text: str, lang: str | None = None) -> dict:
    """1つの本文(EN or JA)に対しclaimの範囲を確定する。返値 dict:
    status(ok/multi/none/explanatory/frag_unresolved)、level、spans[(a,b)]。
    langはVS_MATCH_EXT(委任_49)の単語境界・L5が英語本文("EN")にだけ効くための指定(既定None=従来どおり)。
    L5(末尾句読点)は、L0〜L4で確定しなかった場合(none/explanatory/frag_unresolved)に限って試す。"""
    res = _vs_resolve_in_text_core(claim, text, lang)
    if res["status"] in ("none", "explanatory", "frag_unresolved"):
        e = vs_edge_punct_match(claim, text, lang)
        if e is not None:
            return {"status": e["status"], "level": "L5_edge_punct", "spans": e["spans"],
                    "stripped": e["stripped"], "edge_removed": e["edge_removed"]}
    return res


def _vs_resolve_in_text_core(claim: str, text: str, lang: str | None = None) -> dict:
    st, lv, strp, spans = vs_match_levels(claim, text, lang)
    if st == "ok":
        return {"status": "ok", "level": lv, "spans": spans, "stripped": strp}
    if st == "multi":
        return {"status": "multi", "level": lv, "spans": spans, "stripped": strp}
    frags, _rest, rest_clean = vs_split_fragments(claim)
    if len(frags) >= 2 and rest_clean == "":
        sp, lvs, bad = [], [], None
        for f in frags:
            s2, l2, _st2, spans2 = vs_match_levels(f, text, lang)
            if s2 != "ok":
                bad = (f, s2)
                break
            sp.append(spans2[0])
            lvs.append(l2)
        if bad:
            return {"status": "frag_unresolved", "level": "L4", "spans": [], "bad_fragment": bad[0],
                    "bad_status": bad[1]}
        return {"status": "ok", "level": "L4", "spans": sp, "frag_levels": lvs, "stripped": False}
    if len(frags) >= 1 and rest_clean != "":
        return {"status": "explanatory", "level": None, "spans": []}
    return {"status": "none", "level": None, "spans": []}


def vs_merge_spans(spans: list, text: str) -> list:
    """複数範囲の整理(仕様(1)): 重なる、または間が空白だけで隣接する範囲は
    1つに結合する(段落区切り`\\n\\n`はまたがない)。一方が他方を含む場合は
    大きい方へ吸収される。記事順(開始位置昇順)で返す。"""
    merged: list = []
    for a, b in sorted(set(spans)):
        if merged:
            pa, pb = merged[-1]
            gap = text[pb:a] if a > pb else ""
            if a <= pb or (gap.strip() == "" and "\n\n" not in gap):
                merged[-1] = (pa, max(pb, b))
                continue
        merged.append((a, b))
    return merged


def resolve_violation_spans(claim_text: str, en_text: str | None, ja_text: str | None = None) -> dict:
    """委任_53: 入口。`CHECKER_SPANS_MODE="violation_spans"`で、`claim_text`が
    `assemble_claim_from_violation_spans`が配列から組み立てた文字列なら、配列の各要素を
    `_resolve_claim_string`(委任_42の照合そのまま)で要素ごとに確定し、全要素が確定したときだけ確定
    (`_resolve_spans_array`)。それ以外(legacy・固定fixture・same_fact_id_locationsの展開文字列)は
    従来どおり`_resolve_claim_string`(挙動不変)。"""
    if CHECKER_SPANS_MODE == CHECKER_SPANS_MODE_VIOLATION_SPANS:
        key = (claim_text or "").strip()
        if key in _VS_SPANS_REGISTRY:
            return _resolve_spans_array(claim_text, _VS_SPANS_REGISTRY[key], en_text, ja_text)
    return _resolve_claim_string(claim_text, en_text, ja_text)


def _resolve_spans_array(claim_text: str, elems: list, en_text: str | None, ja_text: str | None) -> dict:
    """委任_53 設計書§3-1: 配列の各要素を既存の照合で確定する。1要素でも確定不能なら全体を確定不能
    (fail-closed、`reason`は要素の理由、`failed_span_index`・`reason_detail`に要素番号)。空配列は
    `violation_spans_empty`。要素ごとの結果は`array_elements`に残す(集計用)。確定した範囲は同じ言語の
    本文で記事順に結合する(`vs_merge_spans`)。言語が要素で割れた場合は確定不能(`mixed_lang`)。"""
    out = {"status": "unverified", "reason": None, "claim_text": claim_text, "lang": None, "level": None,
           "ranges": [], "spans": [], "raw_spans": [], "per_lang": {}, "both_langs_ok": False,
           "from_violation_spans": True, "array_elements": []}
    if not elems:
        out["reason"] = "violation_spans_empty"
        return out
    results = []
    for i, e in enumerate(elems):
        r = _resolve_claim_string(e, en_text, ja_text)
        results.append(r)
        out["array_elements"].append({"index": i, "text": e, "status": r["status"], "reason": r.get("reason"),
                                       "lang": r.get("lang"), "level": r.get("level")})
    bad = next((i for i, r in enumerate(results) if r["status"] != "resolved"), None)
    if bad is not None:
        out["reason"] = results[bad].get("reason") or "mismatch"
        out["failed_span_index"] = bad
        out["reason_detail"] = f"span[{bad}]:{out['reason']}"
        if results[bad].get("detail"):
            out["detail"] = results[bad]["detail"]
        return out
    langs = {r["lang"] for r in results}
    if len(langs) != 1:
        out["reason"] = "mixed_lang"
        out["reason_detail"] = "span_langs:" + ",".join(str(r["lang"]) for r in results)
        return out
    lang = langs.pop()
    text = en_text if lang == "EN" else ja_text
    raw = [sp for r in results for sp in r["raw_spans"]]
    merged = vs_merge_spans(raw, text)
    out.update({"status": "resolved", "lang": lang, "level": "SPANS:" + ",".join(str(r["level"]) for r in results),
                "raw_spans": raw, "spans": merged, "ranges": [text[a:b] for a, b in merged],
                "both_langs_ok": all(r["both_langs_ok"] for r in results),
                "per_lang": results[0]["per_lang"], "stripped": any(r.get("stripped") for r in results)})
    return out


def _resolve_claim_string_base(claim_text: str, en_text: str | None, ja_text: str | None = None) -> dict:
    """委任_42 仕様(1): Checkerの`claim_text`だけを入力に、記事側の範囲を確定する
    (再推測ではなく照合)。類似度・単語重なり・判定役の引用・位置比は使わない。
    返値: {"status": "resolved"|"unverified", "lang": "EN"|"JA"|None,
    "level": "L0".."L4"|None, "ranges": [記事側の文字列(記事順・結合後)],
    "spans": [(a,b)(結合後)], "raw_spans": [(a,b)(結合前)], "reason":
    unverified時の原因("mismatch"/"multi_match"/"explanatory_mixed"/
    "empty_claim"/"no_text"), "per_lang": {...}, "both_langs_ok": bool}。
    EN・JAの両方で確定できた場合はEN側を採用する(両方確定した事実は保持)。"""
    claim = (claim_text or "").strip()
    out = {"status": "unverified", "reason": None, "claim_text": claim_text, "lang": None, "level": None,
           "ranges": [], "spans": [], "raw_spans": [], "per_lang": {}, "both_langs_ok": False}
    if not claim:
        out["reason"] = "empty_claim"
        return out
    results = {}
    if en_text is not None:
        results["EN"] = vs_resolve_in_text(claim, en_text, "EN")
    if ja_text is not None:
        results["JA"] = vs_resolve_in_text(claim, ja_text, "JA")
    if not results:
        out["reason"] = "no_text"
        return out
    out["per_lang"] = {k: {"status": v["status"], "level": v.get("level")} for k, v in results.items()}
    ok_langs = [k for k, v in results.items() if v["status"] == "ok"]
    if ok_langs:
        lang = "EN" if "EN" in ok_langs else "JA"
        r = results[lang]
        text = en_text if lang == "EN" else ja_text
        merged = vs_merge_spans(r["spans"], text)
        out.update({"status": "resolved", "lang": lang, "level": r["level"], "raw_spans": list(r["spans"]),
                    "spans": merged, "ranges": [text[a:b] for a, b in merged],
                    "both_langs_ok": len(ok_langs) == 2, "stripped": r.get("stripped", False),
                    "frag_levels": r.get("frag_levels")})
        if r.get("edge_removed") is not None:
            out["edge_removed"] = list(r["edge_removed"])
        # 委任_49 A2-a(VS_MATCH_EXT): 確定範囲が構造ラベル行そのものなら確定不能(人間確認)
        if VS_MATCH_EXT and lang == "EN":
            lab = [text[a:b] for a, b in merged if vs_is_structural_label_range(text, (a, b))]
            if lab:
                out.update({"status": "unverified", "reason": "label_only", "lang": None, "level": None,
                            "ranges": [], "spans": [], "raw_spans": [], "label_only_ranges": lab})
        return out
    sts = [v["status"] for v in results.values()]
    if "multi" in sts:
        out["reason"] = "multi_match"
    elif "explanatory" in sts:
        out["reason"] = "explanatory_mixed"
    elif "frag_unresolved" in sts:
        out["reason"] = "mismatch"
        out["detail"] = "fragment_unresolved"
    else:
        out["reason"] = "mismatch"
    return out


_VS_EXPLAIN_OPEN_CLOSE = {"“": "”", "「": "」", "『": "』"}
_VS_EXPLAIN_CONNECTIVE = frozenset({"and", "or", "also", "&", "および", "と", "かつ", "また"})
_VS_EXPLAIN_HEAD_RE = re.compile(r"\b(headline|title|heading)\b|見出し|タイトル", re.I)
_VS_EXPLAIN_ONELINE_RE = re.compile(r"in one line|one-line|one line|\bsummary\b|要約", re.I)
_VS_EXPLAIN_OPENING_RE = re.compile(r"\b(opening|lead|hook)\b|冒頭", re.I)
_VS_EXPLAIN_SEG_EDGE = " \t\r\n.,;:、，；。:()（）[]【】—–-/…\"'“”‘’「」『』"
_VS_EXPLAIN_CJK_RE = re.compile(r"[぀-ヿ一-鿿]")


def _vs_explain_extract_fragments(claim: str) -> tuple:
    """引用符で囲まれた断片を出現順に取り出す。返値 (frags[(start,end,inner)], balanced, remainder_segments[str])。
    “”「」『』は入れ子なしの単純対応。直線"は交互。閉じ忘れ・閉じだけが残る場合は balanced=False。"""
    frags, i, n = [], 0, len(claim)
    balanced = True
    segs, last = [], 0
    while i < n:
        ch = claim[i]
        if ch in _VS_EXPLAIN_OPEN_CLOSE or ch == '"':
            close = _VS_EXPLAIN_OPEN_CLOSE.get(ch, '"')
            j = claim.find(close, i + 1)
            if j < 0:
                balanced = False
                break
            frags.append((i, j + 1, claim[i + 1:j]))
            segs.append(claim[last:i])
            last = j + 1
            i = j + 1
            continue
        if ch in "”」』":
            balanced = False
            break
        i += 1
    segs.append(claim[last:])
    return frags, balanced, segs


def _vs_explain_structure_elements(text: str) -> dict:
    """記事の構造から決定論的に取れる要素: 見出し行(最初の`# `行)・`## In one line`直下の1行・見出し直後の最初の段落。"""
    out = {}
    m = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    if m:
        out["headline"] = (m.start(1), m.end(1))
    m = re.search(r"(?mi)^##[ \t]*In one line[ \t]*\n(.+?)(?:\n[ \t]*\n|\Z)", text, re.S)
    if m:
        out["one_line"] = (m.start(1), m.start(1) + len(m.group(1).rstrip()))
    m = re.search(r"(?m)^#[ \t]+.+?$", text)
    if m:
        mm = re.search(r"\S.*?(?:\n[ \t]*\n|\Z)", text[m.end():], re.S)
        if mm:
            out["opening"] = (m.end() + mm.start(), m.end() + mm.end())
    return out


# 委任_02 作業2-6(Opus#11論点8・Fable評価7、`VS_EXPLAIN_SPLIT`配下・新スイッチなし): 規則Q=断片が記事に逐語で
# 照合できないとき、断片と記事の引用符の字形(" ' “ ” ‘ ’ 「 」 『 』 等)を同一クラスへ写像(文字数不変)して再照合する。
# 一意(ちょうど1箇所)のときだけ採用し、範囲は記事側の原文のまま(語は変えない)。
_VS_Q_GLYPH_MAP = {c: "'" for c in "’‘‚‛`´'“”„\"「」『』"}


def vs_quote_glyph_norm(s: str) -> str:
    """引用符の字形を1クラスへ写像する(文字数不変=スパンの座標を保つ)。"""
    return "".join(_VS_Q_GLYPH_MAP.get(ch, ch) for ch in s)


# 規則U-2(1): 説明文の位置語が名指す構造要素のうち、閉じた語彙で決定論に取れるもの(見出し行・`## In one line`直下の1行)。
# `opening`は対象外(従来どおり、断片が既に含まれなければ棄却)。
VS_EXPLAIN_U2_ELEMENTS = ("headline", "one_line")


def vs_explain_split_resolve(claim_text: str, en_text: str | None) -> dict:
    """委任_57 P-strict-closed(Trial専用、`VS_EXPLAIN_SPLIT`ON時のみ`_resolve_claim_string`から呼ばれる)。
    英語本文のみ。返値: {"status": "resolved"/"unverified", "reason": None / "explain_split_rejected:<理由>",
    "fragments": [断片(逐語)], "dropped_remainders": [{"seg", "verdict"}], "spans": [(a,b)(結合後)],
    "raw_spans": [(a,b)(結合前)], "ranges": [記事側の文字列], "level": "P:<断片数>"}。
    語は足さない・落とさない・置換しない(断片は逐語で本文にちょうど1箇所、残りは確定範囲に含めず捨てる)。"""
    claim = (claim_text or "").strip()
    out = {"status": "unverified", "reason": None, "fragments": [], "dropped_remainders": [], "spans": [],
           "raw_spans": [], "ranges": [], "level": None}

    def rej(r: str, **kw) -> dict:
        out["reason"] = "explain_split_rejected:" + r
        out.update(kw)
        return out
    en = en_text
    if en is None:
        return rej("no_en_text")
    frags, balanced, segs = _vs_explain_extract_fragments(claim)
    if not frags:
        return rej("no_quote")
    if not balanced:
        return rej("unbalanced_quote")
    out["fragments"] = [f[2] for f in frags]
    spans = []
    for (_s, _e, inner) in frags:
        st, _lv, _stp, sp = vs_match_levels(inner, en, "EN")
        if st == "ok":
            spans.append(sp[0])
            continue
        if st == "none":
            e = vs_edge_punct_match(inner, en, "EN")
            if e is not None and e["status"] == "ok":
                spans.append(e["spans"][0])
                continue
            if e is not None and e["status"] == "multi":
                return rej("fragment_multi_match", detail=inner)
            # 規則Q(委任_02): 引用符の字形だけの差を同一視して再照合(一意のときだけ採用)
            st2, _l2, _s2, sp2 = vs_match_levels(vs_quote_glyph_norm(inner), vs_quote_glyph_norm(en), "EN")
            if st2 == "ok":
                spans.append(sp2[0])
                out.setdefault("q_used", []).append(inner)
                continue
        return rej("fragment_multi_match" if st == "multi" else "fragment_not_in_article", detail=inner)
    merged = vs_merge_spans(spans, en)
    if VS_MATCH_EXT and any(vs_is_structural_label_range(en, m) for m in merged):
        return rej("label_only")
    nt, _ = vs_norm_with_map(en, True)
    el = _vs_explain_structure_elements(en)
    added_elements: list = []
    seginfo = []
    for sg in segs:
        s = sg.strip(_VS_EXPLAIN_SEG_EDGE).strip()
        if not s:
            continue
        rec = {"seg": s}
        seginfo.append(rec)
        out["dropped_remainders"] = seginfo
        m = VS_EXPLAIN_POSITION_REJECT_RE.search(s)
        if m:
            rec["verdict"] = "position_word:" + m.group(0)
            return rej(rec["verdict"])
        want = []
        if _VS_EXPLAIN_HEAD_RE.search(s):
            want.append("headline")
        if _VS_EXPLAIN_ONELINE_RE.search(s):
            want.append("one_line")
        if _VS_EXPLAIN_OPENING_RE.search(s):
            want.append("opening")
        dang = [w for w in want if w in el and not any(sa < el[w][1] and el[w][0] < sb for sa, sb in spans)]
        if dang:
            if any(w not in VS_EXPLAIN_U2_ELEMENTS for w in dang):
                rec["verdict"] = "dangling_position:" + ",".join(dang)
                return rej(rec["verdict"])
            # 規則U-2(1)(委任_02): 位置語が閉じた語彙(headline/one-line)の構造要素を名指ししているときは、棄却せず
            # その要素(見出し行・`## In one line`直下の1行)そのものを範囲へ加える(拡張のみ)。
            added_elements.extend(w for w in dang if w not in added_elements)
            rec["u2_added"] = list(dang)
        m = VS_EXPLAIN_CONTRAST_REF_EN_RE.search(s) or VS_EXPLAIN_CONTRAST_REF_JA_RE.search(s)
        if m:
            rec["verdict"] = "contrast_or_reference_word:" + m.group(0)
            return rej(rec["verdict"])
        if s.lower() in _VS_EXPLAIN_CONNECTIVE:
            rec["verdict"] = "connective"
            continue
        cjk = bool(_VS_EXPLAIN_CJK_RE.search(s))
        if (len(s) >= VS_EXPLAIN_MAX_JA_CHARS) if cjk else (len(s.split()) >= VS_EXPLAIN_MAX_EN_WORDS):
            # 委任_11 D(i)(Fable評価7): 狭い緩和。残りが閉じた語彙の位置語(headline/one_line=U-2要素)を含み、かつ
            # 以降の逐語一致・隣接一致の棄却(不完全な引用の兆候)に当たらない場合に限り語数制限を外す(それらの棄却は残す)。
            if SPAN_FALLBACK_CHAIN and any(w in VS_EXPLAIN_U2_ELEMENTS and w in el for w in want):
                rec["too_long_relaxed"] = True
            else:
                rec["verdict"] = "remainder_too_long"
                return rej("remainder_too_long")
        ns = vs_norm_str(s, True)
        if ns and ns in nt and s.lower().lstrip("#").strip() not in VS_STRUCTURAL_LABELS:
            long_ok = (len(s) >= 8) if cjk else (len(s.split()) >= VS_EXPLAIN_MIN_VERBATIM_WORDS)
            if long_ok:
                rec["verdict"] = "remainder_verbatim_in_article"
                return rej("remainder_verbatim_in_article")
        nss = ns.strip(_VS_EXPLAIN_SEG_EDGE)
        adj = False
        for (a, b) in spans:
            pre = vs_norm_with_map(en[max(0, a - 400):a], True)[0].rstrip(_VS_EXPLAIN_SEG_EDGE)
            post = vs_norm_with_map(en[b:b + 400], True)[0].lstrip(_VS_EXPLAIN_SEG_EDGE)
            if nss and (pre.endswith(nss) or post.startswith(nss)):
                adj = True
                break
        if adj:
            rec["verdict"] = "remainder_adjacent_in_article"
            return rej("remainder_adjacent_in_article")
        rec["verdict"] = "dropped"
    if added_elements:
        merged = vs_merge_spans(list(spans) + [el[w] for w in added_elements], en)
        out["added_elements"] = list(added_elements)
    out.update({"status": "resolved", "reason": None, "spans": merged, "raw_spans": list(spans),
                "ranges": [en[a:b] for a, b in merged],
                "level": "P:%d" % len(frags) + ("+Q" if out.get("q_used") else "") + ("+U2" if added_elements else "")})
    return out


# ============================================================
# 委任_66: L6「完結文復元」(Trial専用、`VS_SENTENCE_RESTORE`ON時のみ。設計書§4+Opus#9是正)。
# ユーザー指示(2026-10-04[6回目]): spanが途中切断・...省略でも、断片を含む意味の通る完結文が記事内で
# 一意に特定できるなら、その文を対象範囲として復元する。複数候補・本当に一意に決められない場合のみ例外。
# 決定論のみ(追加LLM callなし)。類似度・単語重なり・SequenceMatcherで範囲を選ばない。範囲は拡張のみ。
# ============================================================
VS_L6_LEVEL = "L6:sentence_restore"
VS_L6_MIN_FRAG_WORDS = 3         # 断片(切断型・省略記号の各部分)の最小語数(fixture 3語連続の一意率95.5%)
VS_L6_MIN_FRAG_CHARS = 12
VS_L6_MIN_ANCHOR_WORDS = 4       # アンカー(逐語で記事に連続する語列)の最小語数(4語連続の一意率98.3%)
VS_L6_MIN_ANCHOR_CHARS = 20
VS_L6_MAX_UNMATCHED_TOKENS = 6   # アンカー外(記事にない語)の連続語数の上限(実例最大5)
VS_L6_MIN_COVER_RATIO = 0.5      # アンカーがclaim文字数に占める割合の下限(逐語連続部分の長さだけ。類似度ではない)
VS_L6_MAX_SENTENCES = 2
VS_L6_MAX_RESTORED_CHARS = 700   # fixture単文の最大575字を超える余裕
# 穴B(Opus#9): 先頭・末尾アンカーの記事上の語間隔 <= claim側の語間隔 + α。αの根拠: Checkerが中間のN語を
# M語へ置換した場合の差|N-M|を許す。アンカー外の最大(VS_L6_MAX_UNMATCHED_TOKENS=6)の約半分で、実例
# (B3 s2: 記事gap=claim gap=1語、A2A3: アンカー1個)は差0。replayで実例・合成・ストレスの全件を再確認済み。
VS_L6_GAP_ALPHA = 3
# 穴A(Opus#9): アンカー外の連続語のうち、記事に逐語で存在する連続部分(この語数以上)は復元範囲の内側に
# 存在すること。1〜2語は`so`/`the`のように記事中どこにでもあり偶然の一致と区別できないため対象外
# (3語連続の一意率95.5%が「偶然では起きにくい」下限=VS_L6_MIN_FRAG_WORDSと同じ)。
VS_L6_RESIDUAL_MIN_WORDS = 3
_VS_L6_ELL_RE = re.compile(r"\s*(?:\.{3,}|…+|・{2,}|(?:\.\s){2,}\.)\s*")
_VS_L6_EDGE = ".,;:!?\"'“”‘’「」『』()[]— \t\r\n"
_VS_L6_CJK_RE = re.compile(r"[぀-ヿ一-鿿]")
# L6用の文分割で、直後の`.`が文末にならない略語(固定リスト、小文字・末尾の`.`なし。決定論)。
# `no`は直後が数字のとき(`No. 5`)だけ、`st`は直後が大文字のとき(`St. Louis`)だけ略語として扱う。
_VS_L6_ABBREV = frozenset({
    "u.s", "u.k", "u.n", "mr", "mrs", "ms", "dr", "prof", "sr", "jr",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
    "st", "no", "vs", "e.g", "i.e", "inc", "co", "ltd", "corp", "a.m", "p.m"})
_VS_L6_ABBREV_WORD_RE = re.compile(r"([A-Za-z]+(?:\.[A-Za-z]+)*)$")
_VS_L6_QUOTE_PAIRS = (("“", "”"), ("‘", "’"), ("「", "」"))


def _vs_l6_abbrev_period(text: str, m) -> bool:
    g = m.group(0)
    if g[0] != "." or len(g) > 1:  # `...`・`."`(閉じ引用符が続く)は略語ではなく文末
        return False
    w = _VS_L6_ABBREV_WORD_RE.search(text[max(0, m.start() - 12):m.start()])
    if not w:
        return False
    ab = w.group(1).lower()
    if ab not in _VS_L6_ABBREV:
        return False
    nxt = text[m.end():].lstrip()[:1]
    if ab == "no":
        return nxt.isdigit()
    if ab == "st":
        return nxt.isupper()
    return True


def vs_sentence_segments_l6(text: str) -> list:
    """L6専用の文分割(委任_66、Opus#9論点1)。既存`vs_sentence_segments`(水準③・P-strict-closed等が使用)は
    `.`+空白で必ず文を切るため`U.S. officials`・`Mr. Trump`・`Jan. 5`で文が割れ、「完結文」が文の途中までに
    なる。既存関数を変えると水準③等の挙動が変わるため変えず、L6用に略語(`_VS_L6_ABBREV`)直後の`.`では
    切らない版を別に持つ(略語直後のピリオドで切らないだけで、他は同一)。"""
    segs, pos = [], 0
    for m in _VS_SENT_END_RE.finditer(text):
        if m.group(0) != "\n" and _vs_l6_abbrev_period(text, m):
            continue
        end = m.start() if m.group(0) == "\n" else m.end()
        segs.append((pos, end))
        pos = m.end()
    segs.append((pos, len(text)))
    out = []
    for a, b in segs:
        while a < b and text[a].isspace():
            a += 1
        while b > a and text[b - 1].isspace():
            b -= 1
        if b > a:
            out.append((a, b))
    return out


class _VsL6Art:
    """L6が1記事に対して使う、正規化済み本文・文分割・出現位置の探索(元本文の座標で返す)。"""

    def __init__(self, text: str):
        self.text = text
        self.nt, self.nm = vs_norm_with_map(text, True)
        self.segs = vs_sentence_segments_l6(text)

    def occ(self, nv: str, boundary: bool) -> list:
        out = []
        if not nv:
            return out
        for a, b in vs_find_all(self.nt, nv):
            if boundary and not vs_word_boundary_ok(self.nt, (a, b)):
                continue
            out.append((self.nm[a][0], self.nm[b - 1][1]))
        return out


def _vs_l6_norm(s: str) -> str:
    return vs_norm_with_map(s.strip(), True)[0]


def _vs_l6_strip_edge(s: str) -> str:
    return s.strip(_VS_L6_EDGE)


def _vs_l6_quote_balanced(s: str) -> bool:
    return s.count("“") == s.count("”") and s.count('"') % 2 == 0


def _vs_l6_sentence_group(art: _VsL6Art, a: int, b: int) -> list:
    return [s for s in art.segs if s[0] < b and s[1] > a]


def _vs_l6_range_from(art: _VsL6Art, hit: list) -> tuple:
    """文群hitから(start, end, 拒否理由)。引用符が閉じていなければ隣接文で閉じられるか試す(2文以内)。"""
    text = art.text
    if not hit:
        return None, None, "no_sentence"
    if len(hit) > VS_L6_MAX_SENTENCES:
        return None, None, "spans_more_than_%d_sentences" % VS_L6_MAX_SENTENCES
    s, e = hit[0][0], hit[-1][1]
    if "\n\n" in text[s:e]:
        return None, None, "crosses_paragraph"
    if not _vs_l6_quote_balanced(text[s:e]):
        idx, jdx = art.segs.index(hit[0]), art.segs.index(hit[-1])
        ok = False
        for (i0, j0) in ((idx - 1, jdx), (idx, jdx + 1)):
            if i0 < 0 or j0 >= len(art.segs) or (j0 - i0 + 1) > VS_L6_MAX_SENTENCES:
                continue
            ss, ee = art.segs[i0][0], art.segs[j0][1]
            if "\n\n" not in text[ss:ee] and _vs_l6_quote_balanced(text[ss:ee]):
                s, e, ok = ss, ee, True
                break
        if not ok:
            return None, None, "unbalanced_quote_not_closable_within_%d_sentences" % VS_L6_MAX_SENTENCES
    if e - s > VS_L6_MAX_RESTORED_CHARS:
        return None, None, "restored_too_long(%d)" % (e - s)
    if vs_is_structural_label_range(text, (s, e)):
        return None, None, "label_only"
    return s, e, None


def _vs_l6_anchor_scan(art: _VsL6Art, part: str) -> dict:
    """partが記事に全体一致しないとき、先頭側・末尾側の「逐語で記事に連続する最長の語列(アンカー)」を探す。
    返値: {"n", "toks", "head": (k, span|None, text)|None, "tail": (j, span|None, text)|None}。
    spanがNoneのアンカーは記事に2箇所以上=曖昧(位置を決めない)。類似度は使わない。"""
    toks = _vs_l6_norm(part).split()
    n = len(toks)
    res = {"n": n, "toks": toks, "head": None, "tail": None}
    if n < VS_L6_MIN_ANCHOR_WORDS:
        return res

    def variants(seg_tokens, side):
        s = " ".join(seg_tokens)
        yield s
        s2 = s.rstrip(_VS_L6_EDGE) if side == "head" else s.lstrip(_VS_L6_EDGE)
        if s2 != s and s2:
            yield s2

    for k in range(n - 1, VS_L6_MIN_ANCHOR_WORDS - 1, -1):
        found = None
        for v in variants(toks[:k], "head"):
            o = art.occ(v, True)
            if o:
                found = (v, o)
                break
        if found:
            v, o = found
            if len(o) == 1 and len(_vs_l6_strip_edge(v)) >= VS_L6_MIN_ANCHOR_CHARS:
                res["head"] = (k, o[0], v)
            elif len(o) >= 2:
                res["head"] = (k, None, v)
            break
    for j in range(1, n - VS_L6_MIN_ANCHOR_WORDS + 1):
        found = None
        for v in variants(toks[j:], "tail"):
            o = art.occ(v, True)
            if o:
                found = (v, o)
                break
        if found:
            v, o = found
            if len(o) == 1 and len(_vs_l6_strip_edge(v)) >= VS_L6_MIN_ANCHOR_CHARS:
                res["tail"] = (j, o[0], v)
            elif len(o) >= 2:
                res["tail"] = (j, None, v)
            break
    return res


def _vs_l6_locate_part(art: _VsL6Art, part: str, relaxed: bool = False) -> dict:
    """1つの断片(正規化前)を記事内の範囲(元本文の座標)へ。kind: exact/anchor/none/too_short/multi。"""
    core = _vs_l6_strip_edge(part)
    if not core:
        return {"kind": "none", "spans": [], "detail": "empty"}
    nv = _vs_l6_norm(core)
    words = nv.split()
    if (len(words) < VS_L6_MIN_FRAG_WORDS or len(nv) < VS_L6_MIN_FRAG_CHARS) and not (relaxed and len(words) >= 1):
        return {"kind": "too_short", "spans": [], "detail": f"words={len(words)},chars={len(nv)}"}
    occ_any = art.occ(nv, False)
    if len(occ_any) >= 2:
        return {"kind": "multi", "spans": occ_any, "detail": "fragment_occurs_%d_times" % len(occ_any)}
    if len(occ_any) == 1:
        a, b = occ_any[0]
        t = art.text
        ok_head = not (_vs_wordch(t, a) and _vs_wordch(t, a - 1))
        ok_tail = not (_vs_wordch(t, b - 1) and _vs_wordch(t, b))
        return {"kind": "exact", "spans": [(a, b)], "detail": {"ok_head": ok_head, "ok_tail": ok_tail}}
    an = _vs_l6_anchor_scan(art, core)
    sp = [an[side][1] for side in ("head", "tail") if an[side] and an[side][1] is not None]
    ambiguous = [s for s in ("head", "tail") if an[s] and an[s][1] is None]
    if not sp:
        return {"kind": "none", "spans": [], "detail": {"anchor": an, "ambiguous_anchor": ambiguous}}
    return {"kind": "anchor", "spans": sp, "detail": {"anchor": an, "ambiguous_anchor": ambiguous}}


def _vs_l6_residual_check(art: _VsL6Art, toks: list, covered: list, rng: tuple) -> tuple:
    """穴A(Opus#9論点1): アンカーが覆わないclaimの語のうち、記事に逐語で存在する連続部分
    (VS_L6_RESIDUAL_MIN_WORDS語以上)は、復元範囲の内側にも存在すること。記事の外側にしか無ければ、
    Checkerが別の文の語を混ぜた(=黙って縮小する)可能性があるため復元しない。返値(ok, 詳細list)。"""
    n = len(toks)
    cov = set()
    for lo, hi in covered:
        cov.update(range(lo, hi))
    runs, i = [], 0
    while i < n:
        if i in cov:
            i += 1
            continue
        j = i
        while j < n and j not in cov:
            j += 1
        runs.append((i, j))
        i = j
    detail = []
    for lo, hi in runs:
        p = lo
        while p < hi:
            best = None
            for q in range(hi, p + VS_L6_RESIDUAL_MIN_WORDS - 1, -1):
                v = " ".join(toks[p:q])
                for vv in (v, v.strip(_VS_L6_EDGE)):
                    if len(vv.split()) < VS_L6_RESIDUAL_MIN_WORDS:
                        continue
                    o = art.occ(vv, True)
                    if o:
                        best = (q, vv, o)
                        break
                if best:
                    break
            if best is None:
                p += 1
                continue
            q, vv, o = best
            inside = [x for x in o if x[0] >= rng[0] and x[1] <= rng[1]]
            detail.append({"run": vv, "occurrences": len(o), "inside_restored_range": len(inside)})
            if not inside:
                return False, detail
            p = q
    return True, detail


def vs_sentence_restore_resolve(claim_text: str, en_text: str | None) -> dict:
    """委任_66 L6(Trial専用、`VS_SENTENCE_RESTORE`ON時のみ`_resolve_claim_string`から呼ばれる)。英語本文のみ。
    返値info: status(restored/cand0/cand_multi/guard_rejected/not_fired/not_applicable)、reason、restore_reason、
    fired_by、fragments、anchors、restored_sentence、span、n_sentences、n_candidates、focus_spans、residual_check。
    例外が出たら復元しない(status="exception"、呼び出し側はunresolvableのまま=安全側)。"""
    info = {"attempted": True, "status": "not_fired", "reason": None, "restore_reason": None, "fired_by": [],
            "fragments": [], "anchors": [], "restored_sentence": None, "span": None, "n_sentences": None,
            "n_candidates": 0, "focus_spans": [], "residual_check": [], "original_claim": claim_text}
    try:
        return _vs_sentence_restore_core(claim_text, en_text, info)
    except Exception as e:  # noqa: BLE001
        info.update(status="exception", reason=repr(e)[:200])
        return info


def _vs_sentence_restore_core(claim_text: str, en_text: str | None, out: dict) -> dict:
    if en_text is None:
        out.update(status="not_fired", reason="no_en_text")
        return out
    art = _VsL6Art(en_text)
    raw = (claim_text or "").strip()
    if _VS_L6_CJK_RE.search(raw):
        out.update(status="not_applicable", reason="claim_is_japanese")
        return out
    core = vs_strip_one_pair(raw)
    core = raw if core is None else core
    out["claim_core"] = core
    # 説明文混入型の除外: 断片全体が記事に出現せず、引用符の外側に「3語以上かつ記事に逐語で存在しない語句」がある
    # claimは、Checkerの説明文が混じっているとみなし触らない(P-strict-closedの領域、Opus#7の4ガードを迂回しない)。
    if not art.occ(_vs_l6_norm(_vs_l6_strip_edge(core)), False):
        frags_, _bal, segs_ = _vs_explain_extract_fragments(raw)
        if frags_:
            expl = [sg for sg in segs_ if len(_vs_l6_strip_edge(sg).split()) >= 3
                    and _vs_l6_norm(_vs_l6_strip_edge(sg)) not in art.nt]
            if expl:
                out.update(status="not_fired", reason="explanatory_mixed_left_to_P",
                           detail=[_vs_l6_strip_edge(x) for x in expl])
                return out
    head_ell = bool(re.match(r"^\s*(?:\.{3,}|…+|・{2,})", core))
    tail_ell = bool(re.search(r"(?:\.{3,}|…+|・{2,})\s*$", core))
    parts = [p for p in _VS_L6_ELL_RE.split(core) if _vs_l6_strip_edge(p)]
    mid_ell = len(parts) >= 2
    if not parts:
        out.update(status="not_fired", reason="empty")
        return out
    if mid_ell:
        out["fired_by"].append("ellipsis_mid")
    if tail_ell:
        out["fired_by"].append("ellipsis_tail")
    if head_ell:
        out["fired_by"].append("ellipsis_head")
    longest = max(parts, key=lambda p: len(_vs_l6_norm(_vs_l6_strip_edge(p))))
    locs = [_vs_l6_locate_part(art, p, relaxed=(mid_ell and p is not longest)) for p in parts]
    out["fragments"] = [{"part": p, "kind": lc["kind"],
                         "detail": (lc["detail"] if lc["kind"] != "anchor" and lc["kind"] != "none" else None)}
                        for p, lc in zip(parts, locs)]
    kinds = [lc["kind"] for lc in locs]
    if any(k == "too_short" for k in kinds):
        out.update(status="guard_rejected", reason="fragment_too_short")
        return out
    if any(k == "none" for k in kinds):
        amb = [lc["detail"].get("ambiguous_anchor") for lc in locs if lc["kind"] == "none"]
        out.update(status="cand0", reason="no_verbatim_anchor_in_article", detail={"ambiguous": amb})
        return out

    cand_lists, focus, anchor_infos = [], [], []
    for p, lc in zip(parts, locs):
        if lc["kind"] == "anchor":
            an = lc["detail"]["anchor"]
            n, toks = an["n"], an["toks"]
            h = an["head"] if an["head"] and an["head"][1] is not None else None
            t = an["tail"] if an["tail"] and an["tail"][1] is not None else None
            if h and t and t[0] < h[0]:
                out.update(status="guard_rejected", reason="anchors_overlap_in_claim")
                return out
            covered = ([(0, h[0])] if h else []) + ([(t[0], n)] if t else [])
            unmatched = n - sum(hi - lo for lo, hi in covered)
            if unmatched < 0:
                out.update(status="guard_rejected", reason="negative_unmatched")
                return out
            if unmatched > VS_L6_MAX_UNMATCHED_TOKENS:
                out.update(status="cand0", reason=f"unmatched_run_too_long({unmatched}>{VS_L6_MAX_UNMATCHED_TOKENS})")
                return out
            cover = (len(h[2]) if h else 0) + (len(t[2]) if t else 0)
            if cover / max(1, len(_vs_l6_norm(_vs_l6_strip_edge(p)))) < VS_L6_MIN_COVER_RATIO:
                out.update(status="cand0", reason="anchor_cover_below_%.2f" % VS_L6_MIN_COVER_RATIO)
                return out
            gap_info = None
            if h and t:
                if t[1][0] < h[1][1]:
                    out.update(status="cand0", reason="head_tail_anchors_out_of_order")
                    return out
                art_gap = len(_vs_l6_norm(art.text[h[1][1]:t[1][0]]).split())
                claim_gap = t[0] - h[0]
                gap_info = {"article_gap_words": art_gap, "claim_gap_words": claim_gap}
                if art_gap > claim_gap + VS_L6_GAP_ALPHA:
                    out.update(status="guard_rejected", reason="anchor_gap_inconsistent(%d>%d+%d)" % (
                        art_gap, claim_gap, VS_L6_GAP_ALPHA), detail=gap_info)
                    return out
            out["fired_by"].append("anchor_with_substituted_words(unmatched=%d)" % unmatched)
            anchor_infos.append({"part": p, "head": ({"k": h[0], "text": h[2], "span": h[1]} if h else None),
                                 "tail": ({"j": t[0], "text": t[2], "span": t[1]} if t else None),
                                 "ambiguous": lc["detail"].get("ambiguous_anchor"), "unmatched": unmatched,
                                 "toks": toks, "covered": covered, "gap": gap_info})
            lo = min(a for a, _ in lc["spans"])
            hi = max(b for _, b in lc["spans"])
            cand_lists.append([(lo, hi)])
            focus.append((lo, hi))
        else:
            cand_lists.append(list(lc["spans"]))
            if lc["kind"] == "exact":
                focus.append(lc["spans"][0])
            else:
                focus.extend(lc["spans"])
    for lc in locs:
        if lc["kind"] == "exact":
            d = lc["detail"]
            if not d["ok_head"]:
                out["fired_by"].append("truncated_head")
            if not d["ok_tail"] and not tail_ell:
                out["fired_by"].append("truncated_tail")
    out["anchors"] = [{k2: v2 for k2, v2 in ai.items() if k2 not in ("toks", "covered")} for ai in anchor_infos]
    if not out["fired_by"]:
        out.update(status="not_fired", reason="exact_and_boundary_ok_but_base_unresolved")
        return out

    import itertools
    groups = []
    for combo in itertools.product(*cand_lists):
        if any(y[0] < x[1] for x, y in zip(combo, combo[1:])):
            continue
        a, b = min(c[0] for c in combo), max(c[1] for c in combo)
        hit = _vs_l6_sentence_group(art, a, b)
        s, e, why = _vs_l6_range_from(art, hit)
        groups.append({"span": (s, e), "why": why, "frag_span": (a, b), "n_sent": len(hit)})
    valid = [g for g in groups if g["why"] is None]
    if not valid:
        why = collections.Counter(g["why"] for g in groups).most_common(1)
        out.update(status="cand0", reason=(why[0][0] if why else "no_ordered_combination"))
        return out
    uniq = sorted({g["span"] for g in valid})
    out["n_candidates"] = len(uniq)
    if len(uniq) >= 2:
        out.update(status="cand_multi", reason="%d_candidate_sentence_groups" % len(uniq),
                   detail=[art.text[a:b] for a, b in uniq])
        return out
    s, e = uniq[0]
    restored = art.text[s:e]
    if art.text.count(restored) != 1:
        out.update(status="cand_multi", reason="restored_text_occurs_%d_times" % art.text.count(restored))
        return out
    # 穴A: 残余包含検査(アンカー型のみ)
    for ai in anchor_infos:
        ok, det = _vs_l6_residual_check(art, ai["toks"], ai["covered"], (s, e))
        out["residual_check"].extend(det)
        if not ok:
            out.update(status="guard_rejected", reason="residual_outside_restored_range")
            return out
    # 文数は復元範囲に含まれる文の数(引用符を隣接文で閉じて範囲が広がった場合も数える)。
    n_sent = sum(1 for sg in art.segs if sg[0] >= s and sg[1] <= e)
    reasons = sorted({f.split("(")[0] for f in out["fired_by"]})
    out.update(status="restored", reason=None, restored_sentence=restored, span=(s, e), n_sentences=n_sent,
               restore_reason=reasons, focus_spans=sorted({tuple(x) for x in focus}))
    return out


def vs_l6_issue_quoted_phrases(issue: str) -> list:
    """Checkerの`issue`中で引用符(“…”/‘…’/「…」/"…")に囲まれた語句(Opus#9論点4(a))。直線の二重引用符も
    LLMの出力で一般的なため含める(含めるほど「すべて不在」の成立が難しくなる=Rewriteする側へ倒れる)。"""
    out = []
    for pat in (r"“([^”]+)”", r"‘([^’]+)’", r"「([^」]+)」", r"\"([^\"]+)\""):
        out.extend(m.group(1).strip() for m in re.finditer(pat, issue or ""))
    return [p for p in dict.fromkeys(out) if p]


def vs_l6_focus_absent(phrases: list, restored_text: str, claim_text: str = "") -> dict:
    """引用符付き語句があり、そのすべてが復元範囲に(単語境界つきで)存在しないとき absent=True。
    語句が無ければabsent=False(通常どおりRewrite)。claim由来かの印(`in_claim`)は記録のみ。"""
    nt = vs_norm_str(restored_text, True)
    nclaim = vs_norm_str(claim_text or "", True)

    def present(p, hay):
        v = vs_norm_str(p, True)
        return bool(v) and any(vs_word_boundary_ok(hay, sp) for sp in vs_find_all(hay, v))
    rows = [{"phrase": p, "in_restored_range": present(p, nt), "in_claim": present(p, nclaim)} for p in phrases]
    return {"phrases": rows, "absent": bool(rows) and not any(r["in_restored_range"] for r in rows)}


def vs_l6_focus_guard(sr: dict, target: str, revised: str, full_text: str) -> dict:
    """Opus#9論点4(b): 2文を復元した場合、E1の結果の変更位置が「元の断片またはアンカーを含む文」の内側に
    収まるかを書き戻し前に検査する(先頭・末尾の共通部分を除いた変更域が、焦点文だけと重なるか)。"""
    if target == revised:  # 変更なし
        return {"ok": True, "changed_region": None, "focus_sentences": [], "outside_sentences_touched": []}
    start = sr["span"][0]
    p = 0
    mx = min(len(target), len(revised))
    while p < mx and target[p] == revised[p]:
        p += 1
    s = 0
    while s < mx - p and target[len(target) - 1 - s] == revised[len(revised) - 1 - s]:
        s += 1
    ca, cb = start + p, start + len(target) - s
    segs = vs_sentence_segments_l6(full_text)
    focus_sents = [sg for sg in segs if any(sg[0] < fb and sg[1] > fa for fa, fb in sr["focus_spans"])]
    if ca == cb:
        touched = [sg for sg in segs if sg[0] <= ca <= sg[1] and start <= ca <= start + len(target)]
    else:
        touched = [sg for sg in segs if sg[0] < cb and sg[1] > ca]
    outside = [sg for sg in touched if sg not in focus_sents]
    return {"ok": not outside, "changed_region": [ca, cb], "focus_sentences": [list(x) for x in focus_sents],
            "outside_sentences_touched": [list(x) for x in outside]}


def _resolve_claim_string(claim_text: str, en_text: str | None, ja_text: str | None = None) -> dict:
    """照合の入口(1箇所)。委任_66: 既存の照合+P-strict-closed(`_resolve_claim_string_p`)で確定せず、
    `VS_SENTENCE_RESTORE`かつ`VS_MATCH_EXT`がONなら、英語本文に限りL6(`vs_sentence_restore_resolve`)を試す
    (P→L6の順。Pは説明文を外す・L6は断片を文へ広げる=目的が逆で、L6→Pだと説明文付き断片をL6が先に文へ広げて
    Pの4ガードを回避してしまうため)。OFF(既定)なら従来と同一の結果を返す。対象はreasonがmismatch/
    explanatory_mixedのときだけ(multi_match・label_only・empty_claim・no_textは触らない)。"""
    out = _resolve_claim_string_p(claim_text, en_text, ja_text)
    if (not VS_SENTENCE_RESTORE or not VS_MATCH_EXT or out["status"] == "resolved" or en_text is None
            or out.get("reason") not in ("mismatch", "explanatory_mixed")):
        return out
    info = vs_sentence_restore_resolve(claim_text, en_text)
    pub = {k: info.get(k) for k in (
        "attempted", "status", "reason", "restore_reason", "fired_by", "fragments", "anchors", "restored_sentence",
        "span", "n_sentences", "n_candidates", "focus_spans", "residual_check", "original_claim", "claim_core")}
    pub["base_reason"] = out.get("reason")
    if info["status"] != "restored":
        out["sentence_restore"] = pub
        return out
    s, e = info["span"]
    pl = dict(out.get("per_lang") or {})
    pl["EN"] = {"status": "ok", "level": VS_L6_LEVEL}
    out.update({"status": "resolved", "reason": None, "lang": "EN", "level": VS_L6_LEVEL,
                "ranges": [en_text[s:e]], "spans": [(s, e)], "raw_spans": [(s, e)], "per_lang": pl,
                "both_langs_ok": False, "stripped": False, "sentence_restore": pub})
    out.pop("label_only_ranges", None)
    out.pop("detail", None)
    return out


def _resolve_claim_string_p(claim_text: str, en_text: str | None, ja_text: str | None = None) -> dict:
    """照合の入口(1箇所)。既存の照合(`_resolve_claim_string_base`)で確定しない(explanatory_mixed/mismatch/
    label_only)場合にだけ、`VS_EXPLAIN_SPLIT`ONなら委任_57の`vs_explain_split_resolve`(P-strict-closed)を試す。
    OFF(既定)なら既存の照合の結果をそのまま返す(挙動不変)。拒否時も`reason`は既存の値のまま(下流の分岐を
    変えない)で、拒否理由コードは`explain_split`(`reason`=`explain_split_rejected:<理由>`)へ記録する。"""
    out = _resolve_claim_string_base(claim_text, en_text, ja_text)
    if (not VS_EXPLAIN_SPLIT or out["status"] == "resolved"
            or out.get("reason") not in ("explanatory_mixed", "mismatch", "label_only")):
        return out
    r = vs_explain_split_resolve(claim_text, en_text)
    info = {"attempted": True, "status": r["status"], "reason": r["reason"], "fragments": r["fragments"],
            "dropped_remainders": r["dropped_remainders"], "base_reason": out.get("reason")}
    if r["status"] != "resolved":
        out["explain_split"] = info
        return out
    pl = dict(out.get("per_lang") or {})
    pl["EN"] = {"status": "ok", "level": r["level"]}
    out.update({"status": "resolved", "reason": None, "lang": "EN", "level": r["level"], "ranges": r["ranges"],
                "spans": r["spans"], "raw_spans": r["raw_spans"], "per_lang": pl, "both_langs_ok": False,
                "stripped": False, "explain_split": info})
    out.pop("label_only_ranges", None)
    out.pop("detail", None)
    return out


def vs_is_structural_label_range(text: str, span: tuple) -> bool:
    """委任_49 A2-a: 範囲が、構造ラベル行(`## In one line`等、`VS_STRUCTURAL_LABELS`)そのもの
    (行頭の`#`群と前後の空白を除いて一致)か。範囲が複数行にまたがる場合は偽。"""
    a, b = span
    seg = text[a:b]
    if "\n" in seg.strip():
        return False
    ls = text.rfind("\n", 0, a) + 1
    le = text.find("\n", b)
    le = len(text) if le < 0 else le
    line_core = text[ls:le].strip().lstrip("#").strip().lower()
    seg_core = seg.strip().lstrip("#").strip().lower()
    return bool(seg_core) and line_core == seg_core and seg_core in VS_STRUCTURAL_LABELS


def vs_sentence_segments(text: str) -> list:
    """水準③(範囲を含む文全体への拡張)専用の文分割。(開始,終了)のlistを返す。"""
    segs, pos = [], 0
    for m in _VS_SENT_END_RE.finditer(text):
        end = m.start() if m.group(0) == "\n" else m.end()
        segs.append((pos, end))
        pos = m.end()
    segs.append((pos, len(text)))
    out = []
    for a, b in segs:
        while a < b and text[a].isspace():
            a += 1
        while b > a and text[b - 1].isspace():
            b -= 1
        if b > a:
            out.append((a, b))
    return out


def vs_expand_to_sentences(spans: list, text: str) -> list:
    """水準③: 各範囲を、その範囲を含む文全体(複数文にまたがる範囲はそれらの文)へ
    拡張した文字列のlistを返す(拡張後に重なる/隣接するものは結合、段落は
    またがない。範囲自体が`\\n\\n`を含む場合はその範囲のまま)。"""
    segs = vs_sentence_segments(text)
    expanded = []
    for a, b in spans:
        if "\n\n" in text[a:b]:
            expanded.append((a, b))
            continue
        hit = [s for s in segs if s[0] < b and s[1] > a]
        if hit:
            expanded.append((min(a, hit[0][0]), max(b, hit[-1][1])))
        else:
            expanded.append((a, b))
    return [text[a:b] for a, b in vs_merge_spans(expanded, text)]


def vs_replace_once(text: str, target: str, replacement: str):
    """仕様(5): 書き戻し直前に、現在の本文でtargetが「ちょうど1箇所」であることを
    再確認してから`.replace(target, replacement, 1)`する。再確認に失敗したら
    None(推測で置換しない)。"""
    if not target or text.count(target) != 1:
        return None
    return text.replace(target, replacement, 1)


def claim_span_text(resolution: dict) -> str | None:
    """周回間の同一判定・Recheckへ渡す`prior_issues`用の、確定範囲の表現
    (複数なら記事順に改行で連結)。確定不能ならNone(呼び出し側は生のclaim
    文字列にフォールバックする)。"""
    if not resolution or resolution.get("status") != "resolved":
        return None
    return "\n".join(resolution["ranges"])


def annotate_claim_span_identity(claim: dict, en_text: str | None, ja_text: str | None) -> dict:
    """委任_42 仕様(7): cycle開始時点の本文でclaimの範囲を確定し、claimへ記録する
    (`claim["span_resolution_cycle_start"]`、`claim["claim_span_text"]`)。
    新方式(`HANDOFF_MODE`)以外では何もしない。"""
    if HANDOFF_MODE != HANDOFF_MODE_VIOLATION_SPAN:
        return claim
    res = resolve_violation_spans(claim.get("claim_text", ""), en_text, ja_text)
    claim["span_resolution_cycle_start"] = {k: res.get(k) for k in (
        "status", "lang", "level", "reason", "ranges", "both_langs_ok", "per_lang", "detail")}
    if res.get("explain_split") is not None:  # 委任_11(Opus#14 論点3、記録専用): explain_splitの棄却理由・断片・残りの判定を残す(従来は落ちていた)
        claim["span_resolution_cycle_start"]["explain_split"] = res["explain_split"]
    if res.get("sentence_restore") is not None:  # 委任_66(記録専用): L6の試行結果
        claim["span_resolution_cycle_start"]["sentence_restore"] = res["sentence_restore"]
    claim["claim_span_text"] = claim_span_text(res)
    return claim


# ------------------------------------------------------------
# 委任_42 仕様(3): Rewrite呼び出し(1指摘=1回の呼び出し、全範囲を配列で渡し、
# 範囲ごとの書き換え結果を同じ個数・同じ順序の配列で返させる)。範囲を含む段落を
# 読み取り専用の文脈として付ける。Stage 2のrewrite hintは「書き換え指示文」と
# してのみ渡す(対象決定には使わない)。
# ------------------------------------------------------------
VS_RANGES_JSON_TAIL = (
    "Return strict JSON only, with exactly this shape: {{\"revised_ranges\": [\"...\", ...]}}. The array "
    "MUST contain exactly {n} string(s), in the same order as the numbered ranges above (Range 1 first). "
    "No explanation, no code fences."
)
VS_RANGES_COMMON_RULES = (
    "The ranges above are the EXACT text(s) the Checker flagged; edit ONLY inside them. Do NOT edit "
    "anything outside the ranges (the paragraph context is read-only; never return it). Inside a range, "
    "any part that does not need to change must be returned character-for-character unchanged (same "
    "words, punctuation, capitalization, spacing). The rewrite hint tells you HOW to fix; any quotation "
    "inside it does not change which text is flagged."
)
E1_RANGES_DEVELOPER_MSG = (
    "You are fixing a fact deviation flagged by a Ledger Deviation Checker, using the SMALLEST possible "
    "edit: swap a single word or connective, remove a short qualifier, or split one sentence into two at a "
    "connective. You may be given Japanese or English text."
)
E1_RANGES_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[Flagged range(s) (the exact text the Checker flagged as a Ledger deviation; article order)]
{ranges_block}

[Paragraph context (read-only)]
{context_block}

[Checker's issue]
{issue}

[Rewrite hint (an instruction on how to fix)]
{rewrite_hint}

Try to resolve the issue using ONLY a minimal edit inside the range(s): swap a single word, swap a \
connective (for example "so" -> "while" / "meanwhile", or a causal connective that wrongly implies one \
thing caused another -> a connective that only states they happened together), remove a single \
qualifying word or short phrase, or split one sentence into two at a connective (without adding any new \
fact and without changing any other word). Do NOT rewrite the content or structure beyond this. Do NOT \
make the tone flatter, and do NOT remove its hook or storytelling value. Preserve the original intent \
and meaning wherever the Ledger allows. Keep the same language as the input. """ + VS_RANGES_COMMON_RULES + """ \
If this issue genuinely CANNOT be resolved by such a minimal edit, return {{"revised_ranges": []}} (do \
not attempt a larger rewrite). """ + VS_RANGES_JSON_TAIL
# 委任_66(Opus#9論点4(c)): L6復元時のみ、E1 Promptへ元の断片(焦点)を併記する(範囲=復元文、焦点=断片)。
E1_RANGES_FOCUS_BLOCK = (
    "[Checker's flagged fragment (the focus inside the range above; the range is the complete sentence(s) "
    "containing it, restored because the Checker's quotation was cut off or partly altered)]\n{fragment}\n\n")
E1_RANGES_PROMPT_TEMPLATE_L6 = E1_RANGES_PROMPT_TEMPLATE.replace(
    "[Paragraph context (read-only)]\n{context_block}",
    "{focus_block}[Paragraph context (read-only)]\n{context_block}", 1)
E2_RANGES_DEVELOPER_MSG = (
    "You are fixing a fact deviation flagged by a Ledger Deviation Checker, using the smallest possible "
    "edit (single-shot, no escalation). You may be given Japanese or English text."
)
E2_RANGES_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[Flagged sentence(s) (the sentence(s) containing the exact text the Checker flagged; article order)]
{ranges_block}

[Paragraph context (read-only)]
{context_block}

[Checker's issue]
{issue}

[Rewrite hint (an instruction on how to fix)]
{rewrite_hint}

Rewrite ONLY the flagged sentence(s) above to resolve the issue (delete the unsupported part, replace it \
with what the Ledger actually supports, or narrow its scope to match the Ledger, per the rewrite hint). \
Keep the same language as the input. A sentence that needs no change must be returned \
character-for-character unchanged. If one flagged sentence is best resolved by deleting it entirely, \
return an empty string for that element. Do NOT edit anything outside the flagged sentence(s) (the \
paragraph context is read-only; never return it). """ + VS_RANGES_JSON_TAIL
E4_RANGES_DEVELOPER_MSG = (
    "You are fixing a fact deviation flagged by a Ledger Deviation Checker. You must revise paragraph "
    "block(s) (which may include a heading/title/hook line) using the smallest edit that removes the "
    "unsupported claim from EVERY sentence in the block(s) that states or implies it. You may be given "
    "Japanese or English text."
)
E4_RANGES_PROMPT_TEMPLATE = """[Verified Fact Ledger]
{ledger_text}

[Paragraph block(s) flagged as containing a Ledger deviation (may include a heading/title/hook line)]
{ranges_block}

[Text originally flagged by the Checker (inside the block(s) above)]
{flagged_block}

[Checker's issue]
{issue}

[Rewrite hint (an instruction on how to fix)]
{rewrite_hint}

Rewrite each paragraph block to resolve the issue. Delete or narrow EVERY sentence in the block(s) \
(including any heading/title/hook line) that states or implies the same unsupported claim, per the \
rewrite hint. Keep the same language as the input. Leave sentences unrelated to this issue unchanged, \
character-for-character, wherever possible. """ + VS_RANGES_JSON_TAIL


def vs_format_ranges(ranges: list) -> str:
    return "\n".join(f"Range {i}:\n<<<\n{t}\n>>>" for i, t in enumerate(ranges, 1))


def vs_parse_revised_ranges(raw: str) -> tuple:
    """Rewrite応答から`revised_ranges`(str配列)を取り出す。(list, None)または(None, エラー種別)。"""
    try:
        parsed = s3rt.extract_json_obj(raw)
    except Exception:  # noqa: BLE001
        return None, "parse_failure"
    lst = parsed.get("revised_ranges") if isinstance(parsed, dict) else None
    if not isinstance(lst, list) or not all(isinstance(x, str) for x in lst):
        return None, "parse_failure"
    return lst, None


def vs_apply_replacements(full_text: str, targets: list, revised: list) -> tuple:
    """範囲ごとに、書き戻し直前に現在の本文で「ちょうど1箇所」を再確認して置換する
    (仕様(5))。(新本文|None, 失敗した範囲のindex|None)を返す。"""
    cur = full_text
    for i, (t, r) in enumerate(zip(targets, revised)):
        nxt = vs_replace_once(cur, t, r)
        if nxt is None:
            return None, i
        cur = nxt
    return cur, None


STRUCTURAL_REWRITE_HINT_SUFFIX = (
    " [Structural element] The flagged text is (part of) the article's title, a heading, the In-one-line text, or the "
    "opening line. Do NOT delete it and do NOT return an empty string: rewrite it as a short, natural, non-empty "
    "statement (at least 3 words) that keeps only what the Ledger supports and drops the unsupported or wrong detail."
)


def structural_element_reasons(full_text: str, spans: list, ranges: list) -> list:
    """委任_07: 範囲が構造要素にかかるか、位置(文字オフセット)の重なりで決定論判定する(¥0)。理由listを返す(空=構造要素でない)。
    - `title`: 先頭の非空行(`_paragraph_title`と同じ行)
    - `heading`: `#`で始まる行(`## In one line`等の見出し行そのもの)
    - `in_one_line`: `In one line`見出し直下の本文(次の空行まで)
    - `preflight_degenerate`: 範囲を削除した場合に`measure_section_role_violation`がtitle/hook/iolのdegenerateを返す。
    文字列の部分一致ではなく位置の重なりで判定する(本文中の語がタイトルにも現れるだけでは構造要素扱いにしない)。"""
    reasons: list = []
    lines, pos = [], 0
    for ln in full_text.split("\n"):
        lines.append((pos, pos + len(ln), ln))
        pos += len(ln) + 1
    nonblank = [(a, b, ln) for a, b, ln in lines if ln.strip()]
    title_span = (nonblank[0][0], nonblank[0][1]) if nonblank else None
    heading_spans = [(a, b) for a, b, ln in lines if ln.strip().startswith("#")]
    iol_spans, in_iol = [], False
    for a, b, ln in lines:
        core = ln.strip().lstrip("#").strip().lower()
        if ln.strip().startswith("#"):
            in_iol = core in VS_STRUCTURAL_LABELS
            continue
        if in_iol:
            if not ln.strip():
                if iol_spans:
                    in_iol = False
                continue
            iol_spans.append((a, b))

    def _hit(refs: list) -> bool:
        return any(s0 < r1 and r0 < s1 for (s0, s1) in spans for (r0, r1) in refs)

    if title_span and _hit([title_span]):
        reasons.append("title")
    if _hit(heading_spans):
        reasons.append("heading")
    if _hit(iol_spans):
        reasons.append("in_one_line")
    if not reasons:
        cur, _bad = vs_apply_replacements(full_text, list(ranges), [""] * len(ranges))
        if cur is not None and cur != full_text:
            sr = measure_section_role_violation(full_text, cur)
            if sr.get("title_degenerate") or sr.get("hook_degenerate") or sr.get("iol_degenerate"):
                reasons.append("preflight_degenerate")
    return reasons


def structural_ladder_exhausted_verified(rewrite_records: list) -> dict:
    """委任_12(Fable照合1、I-2整合): `blocking_structural_after_ladder`を返してよいかを関数内で検証する(名前の洗い替え防止)。
    「構造要素であること(`structural_element_reasons`由来の`structural_element_rewrite`/`structural_blocking`印)∧
    ladderの計画levelを全て実試行済み(昇段済み)」の両方を満たすrecordが1件以上あるときだけ`verified=True`。
    degenerate(空・極端短縮)は「そのlevelの試行失敗」でありladder内で昇段される。構造要素でないdegenerate・
    ladder未試行のdegenerateは`verified=False`(許可リスト外のまま記録される)。LLM callなし。"""
    details = []
    for r in rewrite_records or []:
        h = (r.get("handoff") or {})
        structural = bool(h.get("structural_element_rewrite") or h.get("structural_blocking"))
        planned = list(h.get("levels_planned") or [])
        attempted = set(h.get("levels_attempted") or [])
        ladder_done = bool(h.get("structural_blocking")) or (bool(planned) and set(planned) <= attempted)
        details.append({"claim_identity": r.get("claim_identity"), "structural": structural,
                        "ladder_done": ladder_done, "levels_planned": planned, "levels_attempted": sorted(attempted)})
    ok = any(d["structural"] and d["ladder_done"] for d in details)
    return {"verified": ok, "details": details}


def structural_verified_record(rewrite_records: list, note: str = "") -> dict:
    """OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01 委任_B3(Opus R5-b、記録のみ): `blocking_structural_after_ladder`でSTAGE4へ進む箇所で
    「構造要素∧ladder実試行済み」を実際に検証できたかを`cycle_record["structural_verified"]`へ残す。挙動・ラベルは変えない。LLM callなし。"""
    v = structural_ladder_exhausted_verified(rewrite_records)
    reason = "structural_element_and_ladder_done" if v["verified"] else "structural_element_ladder_exhaustion_not_verified"
    return {"verified": bool(v["verified"]), "reason": reason + (":" + note if note else ""), "details": v["details"]}


def select_last_resort_targets(blocking_claims: list, rewrite_records: list) -> dict:
    """OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01 委任_B(実装不具合是正、E2E neg7のRCA): T(最終手段の決定論削除)の対象は、
    ladderが枯渇したclaim(record単位=index)だけにする。従来はclaim_identity(=fact_id単位)で選んでいたため、同じfact_idの
    別claim(同cycleで既にRewrite成功済み/carry-forward済み)まで再対象化し、文が既に変わっていて位置特定不能(span_unverified)
    →`_t_fail`→`blocking_structural_after_ladder`(構造要素でないのに)へ誤写像されていた。LLM callなし。
    返値: {"indices": T対象のindex(rewrite_recordsとblocking_claimsは同順同数)、"skipped": 除外した同identityのrecord、
    "aligned": 両listの長さが一致したか}。長さ不一致(想定外)ならidentityで選ぶ従来動作へ戻し`aligned=False`を記録する(fail-closed側)。"""
    ex_idx = [i for i, r in enumerate(rewrite_records) if r.get("ladder_exhausted_without_full_rewrite")]
    ex_ids = {rewrite_records[i]["claim_identity"] for i in ex_idx}
    if len(blocking_claims) != len(rewrite_records):
        idx = [i for i, c in enumerate(blocking_claims) if claim_identity(c["dev"]) in ex_ids]
        return {"indices": idx, "skipped": [], "aligned": False}
    skipped = []
    for i, r in enumerate(rewrite_records):
        if i in ex_idx or r.get("claim_identity") not in ex_ids:
            continue
        done = bool(r.get("guard_ok")) or str(r.get("method") or "").startswith("covered_by_earlier_rewrite")
        skipped.append({"index": i, "claim_identity": r.get("claim_identity"), "method": r.get("method"),
                        "t_skipped_reason": "already_rewritten_in_cycle" if done else "not_ladder_exhausted"})
    return {"indices": ex_idx, "skipped": skipped, "aligned": True}


def classify_last_resort_failures(t_claims: list, t_records: list, pre_t_records: list,
                                  en_before: str, ja_before: str | None, en_now: str, ja_now: str | None) -> list:
    """同委任_B: T(最終手段)で`guard_ok=False`だったrecordを、Human Reviewへ送る前に分類する(名前の洗い替え防止、LLM callなし)。
    - `covered_by_earlier_rewrite`: 位置特定不能だが、cycle開始時点の本文では確定でき、その範囲が同cycleで成功した先行Rewriteの置換単位に
      全て含まれる(=対象は既に書き換え済みで本文に無い)。解消扱い(解消の判定は従来どおり全文Recheck)。
    - `unlocatable_not_covered`: 位置特定不能で、先行Rewriteにも含まれない(本文に残っている可能性がある=fail-closed)。非構造の位置特定失敗。
    - `located_guard_failed`: 位置は特定できたがT削除のguardに失敗(本文に残る未解消claim=fail-closed、従来どおり)。
    返値: failedなrecordだけのlist(t_recordsのindex・kind・構造検証付き)。"""
    units = []
    for r in pre_t_records or []:
        units.extend(collect_replaced_units(r, r.get("claim_identity", "")))
    out = []
    for i, r in enumerate(t_records):
        if r.get("guard_ok"):
            continue
        c = t_claims[i]
        if str(r.get("method") or "").startswith("covered_by_earlier_rewrite"):
            # 委任_B3(Opus R5-a): T内のcarry-forwardで解消済み扱いのrecord。`select_last_resort_targets`と判定を揃える
            kind = "covered_by_earlier_rewrite"
        elif r.get("target_not_locatable"):
            kind = "unlocatable_not_covered"
            if units:
                cf = carry_forward_resolution(
                    {"cycle_replaced_units": units, "cycle_start_en_text": en_before, "cycle_start_ja_text": ja_before,
                     "cycle_claim_info": {}, "dev": c.get("dev") or {}},
                    c["claim_text"], en_now, ja_now)
                if cf is not None and cf["covered"] and not cf["remaining"]:
                    kind = "covered_by_earlier_rewrite"
        else:
            kind = "located_guard_failed"
        out.append({"index": i, "claim_identity": r.get("claim_identity"), "kind": kind,
                    "structural_verification": structural_ladder_exhausted_verified([r])})
    return out


def rewrite_ranges_ladder(client, state, consecutive_errors, call_log, label_prefix, fixture,
                           target_text_field, claim_rec: dict) -> dict:
    """委任_42 仕様(2)〜(6)(9): 確定範囲を対象にした最小修正優先ラダー。
    水準①(語句・接続詞の最小編集)=確定範囲そのもの(文の一部ならその断片、複数文なら
    その複数文)。①が不成立の場合のみ水準③=範囲を含む文全体(複数範囲ならそれぞれを含む
    文)へ拡張。それでも不成立の場合のみ水準④=範囲を含む段落。⑥は既定OFF(既存flag)。
    水準選択ロジック(`filter_levels_by_problem_kind`/`escalate_to_paragraph`)の意味は
    変えない(対象範囲の与え方だけ変える)。範囲を確定できない場合はRewriteを試みず
    `target_not_locatable`+`span_unverified`を返す(呼び出し側がStage 4へ)。"""
    full_text = fixture[target_text_field]
    claim_text = claim_rec["claim_text"]
    rewrite_kind = claim_rec["rewrite_kind"]
    dev = claim_rec["dev"]
    lang = "EN" if target_text_field == "article_text" else "JA"
    issue = dev.get("issue") or dev.get("explanation") or claim_text
    rewrite_hint = claim_rec.get("rewrite_hint") or f"materiality={claim_rec['materiality']}, basis={claim_rec['basis']}"
    rewrite_hint = rewrite_hint + claim_rec.get("extra_constraint", "")

    resolution = claim_rec.get("span_resolution")
    if (not resolution or resolution.get("status") != "resolved" or resolution.get("lang") != lang
            or any(full_text.count(r) != 1 for r in resolution.get("ranges", []))):
        resolution = resolve_violation_spans(
            claim_text, full_text if lang == "EN" else None, full_text if lang == "JA" else None)
    handoff = {"mode": HANDOFF_MODE_VIOLATION_SPAN, "checker_claim_text": claim_text, "text_lang": lang,
               "resolution": {k: resolution.get(k) for k in (
                   "status", "lang", "level", "reason", "detail", "ranges", "raw_spans", "spans",
                   "per_lang", "both_langs_ok", "frag_levels", "stripped", "explain_split", "sentence_restore")
                   if k not in ("explain_split", "sentence_restore") or resolution.get(k) is not None},
               "level_attempts": [], "level_used": None, "span_unverified": False}

    if resolution["status"] != "resolved":
        handoff["span_unverified"] = True
        handoff["span_unverified_reason"] = resolution.get("reason")
        return {"updated_text": full_text, "method": "violation_span_unverified", "guard_ok": False,
                "target_sentence": None, "locate_method": f"violation_span_unverified({resolution.get('reason')})",
                "delete_reoccurrence_detected": False, "before_fragment": None, "after_fragment": None,
                "ladder_level_used": None, "target_not_locatable": True, "span_unverified": True,
                "span_unverified_reason": resolution.get("reason"), "handoff": handoff}

    ranges = list(resolution["ranges"])
    spans = list(resolution["spans"])
    locate_method = f"violation_span({lang},{resolution['level']})"
    # 委任_66(L6、Opus#9論点4(a)): 復元範囲に対して、Checkerの`issue`が引用符で挙げた語句がすべて範囲に存在しない
    # (例: 前cycleで既に直った接続語`so`を指す古い引用)場合は、Rewriteせず(不要Rewriteを避け)、全文Recheckに
    # 判定を任せる(Recheckで再指摘されれば次cycleで通常処理)。引用符付き語句が`issue`に無ければ通常どおりRewrite。
    l6 = resolution.get("sentence_restore") if resolution.get("level") == VS_L6_LEVEL else None
    if l6 and l6.get("status") == "restored":
        # 委任_12(Fable照合3a): 引用語句の非存在は「該当文(復元範囲)」ではなく「現行本文全体」に対して判定する
        # (本文のどこかに存在するなら、Checkerの引用は実在する=Recheckのみで済ませず通常どおりRewrite側へ倒す)。
        fa = vs_l6_focus_absent(vs_l6_issue_quoted_phrases(dev.get("issue") or ""), full_text,
                                l6.get("claim_core") or claim_text)
        fa["haystack"] = "current_full_text"
        handoff["issue_focus_check"] = fa
        if fa["absent"]:
            handoff["issue_focus_absent"] = True
            return {"updated_text": full_text, "method": "issue_focus_absent_recheck_only", "guard_ok": False,
                    "target_sentence": None, "locate_method": locate_method,
                    "delete_reoccurrence_detected": False, "before_fragment": None, "after_fragment": None,
                    "ladder_level_used": None, "target_not_locatable": False, "span_unverified": False,
                    "ladder_exhausted_without_full_rewrite": False, "handoff": handoff}
    sentence_units = vs_expand_to_sentences(spans, full_text)
    context_blocks: list = []
    for u in sentence_units:
        blk, _ = locate_paragraph_block(u, full_text)
        if blk and blk not in context_blocks:
            context_blocks.append(blk)
    context_block = "\n\n".join(context_blocks) if context_blocks else "(not available)"

    method_used = None
    updated_text = full_text
    guard_ok = False
    ladder_level_used = None
    after_fragment = None
    before_fragment = " ".join(ranges)
    delete_reoccurrence_detected = False

    # 委任_07(Fable事前判断2): 構造要素(タイトル・In one line・見出し・先頭段落)にかかるdeleteは常に劣化する(空のタイトル等
    # =`degenerate_rewrite_output`のhard block)。KPI構成(`STRUCTURAL_ELEMENT_REWRITE`ON)では、deleteを選ばず書き換え(E1→③→④)へ回し、
    # 空・劣化した案は却下して次の水準へ進める(Human Reviewへ倒す新経路なし)。
    # 委任_11 T(最終手段、Fable評価9): ladderを経ず、構造要素以外の該当文を既存`0_delete`(決定論削除+再出現ガード)で削除する。
    # 構造要素(title/heading/in_one_line/preflight_degenerate)にかかる場合は削除せず「ladder枯渇(構造要素)」として返す
    # (呼び出し側が`blocking_structural_after_ladder`へ)。LLM callなし。1記事1回の制限は呼び出し側(run_instance)が持つ。
    if claim_rec.get("last_resort_delete") and LAST_RESORT_DELETE:
        rewrite_kind = "delete"
        st_reasons_t = structural_element_reasons(full_text, spans, ranges)
        handoff["last_resort_delete"] = {"structural_reasons": st_reasons_t}
        if st_reasons_t:
            handoff["structural_blocking"] = True
            return {"updated_text": full_text, "method": "last_resort_delete_structural_blocked", "guard_ok": False,
                    "target_sentence": " ".join(ranges), "locate_method": locate_method,
                    "delete_reoccurrence_detected": False, "before_fragment": " ".join(ranges),
                    "after_fragment": None, "ladder_level_used": None, "target_not_locatable": False,
                    "ladder_exhausted_without_full_rewrite": True, "handoff": handoff}

    structural_rewrite = False
    if STRUCTURAL_ELEMENT_REWRITE and rewrite_kind == "delete":
        st_reasons = structural_element_reasons(full_text, spans, ranges)
        if st_reasons:
            structural_rewrite = True
            handoff["structural_element_rewrite"] = {"reasons": st_reasons, "original_rewrite_kind": "delete"}
            rewrite_kind = "narrow_scope"
            rewrite_hint = rewrite_hint + STRUCTURAL_REWRITE_HINT_SUFFIX

    if rewrite_kind == "delete":
        whole = {u.strip() for u in sentence_units}
        del_units = ranges if all(r.strip() in whole for r in ranges) else list(sentence_units)
        handoff["delete_units"] = del_units
        handoff["delete_expanded_to_sentence"] = del_units is not ranges and del_units != ranges
        cur, bad = vs_apply_replacements(full_text, del_units, [""] * len(del_units))
        attempt = {"level": "0_delete", "targets": del_units}
        if cur is None:
            attempt["result"] = "writeback_failed"
            method_used = "delete_writeback_failed"
        else:
            norm_after = vs_norm_str(cur, True)
            delete_reoccurrence_detected = any(
                vs_norm_str(r, True) and vs_norm_str(r, True) in norm_after for r in ranges)
            attempt["delete_reoccurrence_detected"] = delete_reoccurrence_detected
            if cur != full_text and not delete_reoccurrence_detected:
                updated_text, guard_ok = cur, True
                method_used = f"deterministic_delete({locate_method})"
                ladder_level_used = "0_delete"
                after_fragment = ""
                attempt["result"] = "success"
                handoff["level_used"] = "0_delete"
            else:
                attempt["result"] = "guard_failed"
                method_used = "deterministic_delete_guard_failed"
        handoff["level_attempts"].append(attempt)
        before_fragment = " ".join(del_units)
    else:
        levels = []
        if l6 and l6.get("status") == "restored":
            # 委任_66(Opus#9論点4(c)): L6復元時のみ、範囲=復元文・焦点=Checkerの元の断片を併記する。
            e1_prompt = E1_RANGES_PROMPT_TEMPLATE_L6.format(
                ledger_text=fixture["ledger_text"], ranges_block=vs_format_ranges(ranges),
                focus_block=E1_RANGES_FOCUS_BLOCK.format(fragment=l6.get("claim_core") or claim_text),
                context_block=context_block, issue=issue, rewrite_hint=rewrite_hint, n=len(ranges))
        else:
            e1_prompt = E1_RANGES_PROMPT_TEMPLATE.format(
                ledger_text=fixture["ledger_text"], ranges_block=vs_format_ranges(ranges),
                context_block=context_block, issue=issue, rewrite_hint=rewrite_hint, n=len(ranges))
        levels.append({
            "name": "1_word_connective", "tag": "e1_minimal_word_edit", "targets": ranges,
            "label": f"{label_prefix}_e1_minimal_word", "dev_msg": E1_RANGES_DEVELOPER_MSG,
            "prompt": e1_prompt,
            "allow_empty": False})
        levels.append({
            "name": "3_sentence", "tag": "e2_generic_rewrite", "targets": sentence_units,
            "label": f"{label_prefix}_e2_rewrite", "dev_msg": E2_RANGES_DEVELOPER_MSG,
            "prompt": E2_RANGES_PROMPT_TEMPLATE.format(
                ledger_text=fixture["ledger_text"], ranges_block=vs_format_ranges(sentence_units),
                context_block=context_block, issue=issue, rewrite_hint=rewrite_hint, n=len(sentence_units)),
            "allow_empty": True})
        blocks: list = []
        all_units_have_block = True
        for u in sentence_units:
            blk, _ = locate_paragraph_block(u, full_text)
            if not blk:
                all_units_have_block = False
                break
            if blk not in blocks:
                blocks.append(blk)
        if all_units_have_block and blocks:
            levels.append({
                "name": "4_paragraph", "tag": "e2_paragraph_rewrite", "targets": blocks,
                "label": f"{label_prefix}_e2_paragraph_rewrite", "dev_msg": E4_RANGES_DEVELOPER_MSG,
                "prompt": E4_RANGES_PROMPT_TEMPLATE.format(
                    ledger_text=fixture["ledger_text"], ranges_block=vs_format_ranges(blocks),
                    flagged_block=vs_format_ranges(ranges), issue=issue, rewrite_hint=rewrite_hint,
                    n=len(blocks)),
                "allow_empty": True})
        if ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP and claim_rec.get("escalate_to_paragraph"):
            levels = [lv for lv in levels if lv["name"] not in ("1_word_connective", "3_sentence")]
        problem_kind = classify_problem_kind(dev)
        claim_rec["problem_kind"] = problem_kind
        handoff["problem_kind"] = problem_kind
        levels = filter_levels_by_problem_kind(levels, dev)
        # 委任_11 B′(Fable評価4): 同一箇所(前cycleで置換した範囲と今回確定spanが1文字以上重なる)は、前に試したlevel以下を飛ばして
        # 上位から昇段する(位置のみで判定、fact_idは問わない)。呼び出し側が`location_prior_levels`を付与したときだけ効く。
        _prior_lv = list(claim_rec.get("location_prior_levels") or [])
        if _prior_lv:
            _max_rank = max(LADDER_LEVEL_RANK.get(n, 1) for n in _prior_lv)
            handoff["location_carry"] = {"prior_levels": _prior_lv, "skipped_levels": [
                lv["name"] for lv in levels if LADDER_LEVEL_RANK.get(lv["name"], 1) <= _max_rank]}
            levels = [lv for lv in levels if LADDER_LEVEL_RANK.get(lv["name"], 1) > _max_rank]
        handoff["levels_planned"] = [lv["name"] for lv in levels]

        for lv in levels:
            targets = lv["targets"]
            attempt = {"level": lv["name"], "targets": list(targets)}
            if lv["name"] == "1_word_connective":
                attempt["target_equals_confirmed_ranges"] = (list(targets) == ranges)
            handoff["level_attempts"].append(attempt)
            raw = simple_llm_call(client, state, consecutive_errors, call_log, lv["label"],
                                   lv["dev_msg"], lv["prompt"], model=MODEL)
            if raw is None:
                attempt["result"] = "api_failure"
                method_used = f"{lv['tag']}_api_failure"
                continue
            revised, err = vs_parse_revised_ranges(raw)
            if err:
                attempt["result"] = err
                method_used = f"{lv['tag']}_{err}"
                continue
            if lv["name"] == "1_word_connective" and (len(revised) == 0 or any(not r.strip() for r in revised)):
                attempt["result"] = "declined"
                method_used = f"{lv['tag']}_declined"
                continue
            if len(revised) != len(targets):
                attempt["result"] = "count_mismatch"
                attempt["returned_count"] = len(revised)
                method_used = f"{lv['tag']}_count_mismatch"
                continue
            if structural_rewrite and any(not r.strip() for r in revised):
                # 委任_07: 構造要素の書き換えで空文字を返す案は、deleteと同じ劣化になるため却下(次の水準へ)。
                attempt["result"] = "declined_empty_structural"
                method_used = f"{lv['tag']}_declined_empty_structural"
                continue
            attempt["revised"] = list(revised)
            changed = [r != t for t, r in zip(targets, revised)]
            attempt["each_target_changed"] = changed
            # 委任_11 A2(Fable評価5): 範囲ごとに、箇所の過去状態(原文・前cycleまでの本文)へ戻る候補を決定論で却下する
            # (同cycle内で上位levelへ進む。前後の文脈つきで照合するため、短い語が別の場所にあるだけでは却下しない)。
            if REWRITE_REVERT_GUARD and claim_rec.get("article_state_history"):
                rv = [revert_to_prior_state_detected(claim_rec["article_state_history"], full_text, t, r)
                      for t, r in zip(targets, revised)]
                if any(rv):
                    attempt["result"] = "revert_rejected"
                    attempt["revert_detected_by_range"] = rv
                    method_used = f"{lv['tag']}_revert_rejected({locate_method})"
                    continue
            if (lv["name"] == "1_word_connective" and l6 and l6.get("status") == "restored"
                    and l6.get("n_sentences") == 2 and len(targets) == 1):
                # 委任_66(Opus#9論点4(b)): 2文復元時、E1の変更が「断片/アンカーを含む文」の外側に及んだら
                # E1失敗扱い(既存の失敗経路=次の水準へ)。
                fg = vs_l6_focus_guard(l6, targets[0], revised[0], full_text)
                attempt["focus_guard"] = fg
                if not fg["ok"]:
                    attempt["result"] = "focus_guard_rejected"
                    handoff["focus_guard_fired"] = True
                    method_used = f"{lv['tag']}_focus_guard_rejected({locate_method})"
                    continue
            candidate, bad_idx = vs_apply_replacements(full_text, targets, revised)
            if candidate is None:
                attempt["result"] = "writeback_failed"
                attempt["writeback_failed_index"] = bad_idx
                method_used = f"{lv['tag']}_writeback_failed({locate_method})"
                continue
            if not (candidate != full_text and all(changed)):
                attempt["result"] = "guard_failed"
                method_used = f"{lv['tag']}_guard_failed({locate_method})"
                continue
            if structural_rewrite or STAGE4_ALLOWLIST:
                # 委任_12(Fable照合1): degenerate(title/hook/In one lineの空・極端短縮)は構造要素書き換えに限らず「そのlevelの試行失敗」として
                # 同cycle内で上位levelへ昇段する(許可リストON時。許可名への写像はしない)。
                sr_chk = measure_section_role_violation(full_text, candidate)
                if sr_chk.get("title_degenerate") or sr_chk.get("hook_degenerate") or sr_chk.get("iol_degenerate"):
                    attempt["result"] = "degenerate_structural"
                    method_used = f"{lv['tag']}_degenerate_structural"
                    continue
            _ag_fid, _ag_issue = actor_guard_context(claim_rec)
            _ag_dec: list = []
            _ag_ok = all(actor_rewrite_guard_ok(t, r, fixture["ledger_text"], _ag_fid, _ag_issue, _ag_dec)
                         for t, r in zip(targets, revised))
            if _ag_dec:
                attempt["actor_guard_decision"] = _ag_dec
            if not _ag_ok:
                attempt["result"] = "actor_guard_rejected"
                method_used = f"{lv['tag']}_actor_guard_rejected({locate_method})"
                continue
            attempt["result"] = "success"
            attempt["before_after"] = [{"before": t, "after": r} for t, r in zip(targets, revised)]
            if structural_rewrite:  # 委任_08(Fable評価5): 構造要素の書き換え前後の対(4_paragraphでafter_fragmentがNoneでも渡せるよう別記録)
                handoff["structural_pair"] = {"before": " ".join(targets), "after": " ".join(revised)}
            updated_text, guard_ok = candidate, True
            method_used = f"{lv['tag']}({locate_method})"
            ladder_level_used = lv["name"]
            handoff["level_used"] = lv["name"]
            if lv["name"] != "4_paragraph":
                before_fragment = " ".join(targets)
                after_fragment = " ".join(revised)
            break

    handoff["levels_attempted"] = [a.get("level") for a in handoff["level_attempts"]]  # 委任_11: 実際に試行したlevel一覧(`escalated_to_paragraph`是正用)
    if not guard_ok:
        after_fragment = None
        if not ENABLE_LADDER_LEVEL_6_FULL_REWRITE:
            return {"updated_text": full_text, "method": (method_used or "") + "+ladder6_disabled",
                    "guard_ok": False, "target_sentence": before_fragment, "locate_method": locate_method,
                    "delete_reoccurrence_detected": delete_reoccurrence_detected,
                    "before_fragment": before_fragment, "after_fragment": None,
                    "ladder_level_used": None, "target_not_locatable": False,
                    "ladder_exhausted_without_full_rewrite": True, "handoff": handoff}
        prompt = FULL_TEXT_FALLBACK_PROMPT_TEMPLATE.format(
            ledger_text=fixture["ledger_text"], full_text=full_text,
            target_sentence="\n".join(ranges), issue=issue, rewrite_hint=rewrite_hint)
        fallback_text = simple_llm_call(client, state, consecutive_errors, call_log,
                                         f"{label_prefix}_fulltext_fallback",
                                         FULL_TEXT_FALLBACK_DEVELOPER_MSG, prompt, model=MODEL)
        if fallback_text:
            updated_text = fallback_text
            method_used = (method_used or "") + "+fulltext_fallback"
            guard_ok = updated_text != full_text
            if guard_ok and STAGE4_ALLOWLIST:
                _sr6 = measure_section_role_violation(full_text, updated_text)
                if _sr6.get("title_degenerate") or _sr6.get("hook_degenerate") or _sr6.get("iol_degenerate"):
                    guard_ok = False  # 委任_12: degenerateなlevel6案は試行失敗(元本文のまま)
                    updated_text = full_text
                    method_used += "+degenerate_structural"
            if guard_ok:
                ladder_level_used = "6_full_article"
                handoff["level_used"] = "6_full_article"
        else:
            method_used = (method_used or "") + "+fulltext_fallback_api_failure"

    return {"updated_text": updated_text, "method": method_used, "guard_ok": guard_ok,
            "target_sentence": before_fragment, "locate_method": locate_method,
            "delete_reoccurrence_detected": delete_reoccurrence_detected,
            "before_fragment": before_fragment, "after_fragment": after_fragment,
            "ladder_level_used": ladder_level_used, "target_not_locatable": False, "handoff": handoff}


def single_text_rewrite(client, state, consecutive_errors, call_log, label_prefix, fixture, target_text_field,
                         claim_rec: dict) -> dict:
    """claim_rec['dev']の言語テキスト(target_text_field='article_text'固定、
    JA単体fixtureもarticle_text側にJA本文が入っている、g6.load_audit_fixture
    の仕様どおり)に対する単一言語local rewrite。delete型はまず決定論的削除を
    試し、それ以外(replace_with_ledger_value/narrow_scope)はE-2汎用Promptを
    使う。guard抵触(対象文が特定できない/置換後も同じ問題文言が残る)時は
    1回だけ全文最小編集フォールバックを試す。
    委任_42: `HANDOFF_MODE`が新方式(既定)なら`rewrite_ranges_ladder`(Checkerの
    違反範囲をそのまま対象にする)へ委ねる。以下の本体は旧方式(legacy)用。"""
    if HANDOFF_MODE == HANDOFF_MODE_VIOLATION_SPAN:
        return rewrite_ranges_ladder(client, state, consecutive_errors, call_log, label_prefix, fixture,
                                      target_text_field, claim_rec)
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
                            lv["target"], revised, fixture["ledger_text"], *actor_guard_context(claim_rec)):
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


def _paired_en_target_from_span(claim_rec: dict, claim_text: str, en_full: str) -> tuple:
    """委任_42 仕様(8): paired(origin=ja_source)でEN側の対象を、Checkerの文字列から
    確定した**単一の範囲**に差し替える。確定範囲が単一のEN範囲でなければ
    (en_target=None, 理由付きmethod, resolution)を返す(呼び出し側`run_stage3_for_claim`が
    複数範囲/JAのみ確定を片側経路へ回すため、通常ここへは単一範囲しか来ない)。"""
    res = claim_rec.get("span_resolution")
    if (not res or res.get("status") != "resolved" or res.get("lang") != "EN"
            or any(en_full.count(r) != 1 for r in res.get("ranges", []))):
        res = resolve_violation_spans(claim_text, en_full, None)
    if res["status"] == "resolved" and len(res["ranges"]) == 1:
        return res["ranges"][0], f"violation_span(EN,{res['level']})", res
    return None, f"violation_span_not_single_en_range({res.get('reason') or len(res.get('ranges', []))})", res


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

    # 委任_42 仕様(2)(8): 新方式では、EN側の対象は「Checkerの文字列から確定した
    # 単一の範囲」に差し替える(判定役hint引用・類似度・単語重なり・包含スパンを
    # 使わない)。JA側の対応決定(下記の既存処理)は本委任では変更しない(暫定。
    # JA側の構造見直し[英語だけ直す化]は並行調査+Opusレビュー後の別委任)。
    # 確定範囲が複数・JA本文でのみ確定の場合は`run_stage3_for_claim`が本関数を
    # 呼ばず、片側経路(`single_text_rewrite`)へ回す。
    paired_handoff = None
    en_span_resolution = None
    if HANDOFF_MODE == HANDOFF_MODE_VIOLATION_SPAN:
        en_target, en_method, en_span_resolution = _paired_en_target_from_span(claim_rec, claim_text, en_full)
        paired_handoff = {"mode": HANDOFF_MODE_VIOLATION_SPAN, "checker_claim_text": claim_text,
                          "text_lang": "EN(paired)", "level_attempts": [], "level_used": None,
                          "span_unverified": False,
                          "resolution": {k: en_span_resolution.get(k) for k in (
                              "status", "lang", "level", "reason", "detail", "ranges", "raw_spans", "spans",
                              "per_lang", "both_langs_ok", "frag_levels", "stripped")}}
    else:
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
    if (HANDOFF_MODE == HANDOFF_MODE_LEGACY and en_method == "multi_quote_span"
            and en_target is not None):
        # (委任_42: 新方式では使わない[仕様(8)]。旧方式の比較・切り戻し用のみ)
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
                "target_not_locatable": True, "handoff": paired_handoff}

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

        # 委任_42 仕様(4): 水準①のEN対象=確定範囲そのもの(文の一部ならその断片)、
        # 水準③で初めて範囲を含む文全体へ拡張する(旧方式は常に文全体)。
        en_target_l3 = en_target
        if HANDOFF_MODE == HANDOFF_MODE_VIOLATION_SPAN and en_span_resolution:
            _exp = vs_expand_to_sentences(en_span_resolution["spans"], en_full)
            if len(_exp) == 1:
                en_target_l3 = _exp[0]

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
            ledger_text=fixture["ledger_text"], ja_target=ja_target, en_target=en_target_l3,
            rewrite_hint=rewrite_hint,
        )
        levels.append({"name": "3_sentence", "prompt": prompt_l3, "dev_msg": s3rt.J1_DEVELOPER_MSG,
                        "label": f"{label_prefix}_j1_paired_rewrite",
                        "ja_target": ja_target, "en_target": en_target_l3,
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
            if HANDOFF_MODE == HANDOFF_MODE_VIOLATION_SPAN:
                # 委任_42 仕様(5)(6): EN側は書き戻し直前に「ちょうど1箇所」を再確認して
                # 置換(失敗なら置換せず水準失敗)。guardは「Checkerが指した範囲
                # [①は範囲、③④は拡張後の対象]が実際に変化したこと」(旧
                # `claim_text.strip() not in candidate_en`は引用符付き文字列では
                # 常に成立し取りこぼしを検出できなかった)。JA側の置換・guardは
                # 既存のまま(暫定、変更しない)。
                candidate_ja = ja_full.replace(lv["ja_target"], ja_revised, 1) if ja_revised else ja_full
                _en_cand = vs_replace_once(en_full, lv["en_target"], en_revised) if en_revised else None
                candidate_en = _en_cand if _en_cand is not None else en_full
                level_guard_ok = (
                    bool(ja_revised) and bool(en_revised)
                    and candidate_ja != ja_full and candidate_en != en_full
                    and en_revised != lv["en_target"]
                )
                paired_handoff["level_attempts"].append({
                    "level": lv["name"], "targets": [lv["en_target"]],
                    "target_equals_confirmed_ranges": (
                        lv["en_target"] == en_target if lv["name"] == "1_word_connective" else None),
                    "ja_target": lv["ja_target"], "revised": [en_revised], "ja_revised": ja_revised,
                    "writeback_ok": _en_cand is not None if en_revised else False,
                    "each_target_changed": [en_revised != lv["en_target"]],
                    "result": "success_pending_actor_guard" if level_guard_ok else "guard_failed"})
            else:
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
                    lv["en_target"], en_revised, fixture["ledger_text"], *actor_guard_context(claim_rec)):
                level_guard_ok = False
                if paired_handoff is not None:
                    paired_handoff["level_attempts"][-1]["result"] = "actor_guard_rejected"
            if level_guard_ok:
                updated_ja, updated_en = candidate_ja, candidate_en
                guard_ok = True
                use_paragraph = lv["use_paragraph"]
                method = lv["tag"]
                ladder_level_used = lv["name"]
                if paired_handoff is not None:
                    paired_handoff["level_attempts"][-1]["result"] = "success"
                    paired_handoff["level_used"] = lv["name"]
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
        if paired_handoff is not None and single_result.get("handoff"):
            paired_handoff = dict(single_result["handoff"])
            paired_handoff["via_paired_single_side"] = True
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
                    "ladder_exhausted_without_full_rewrite": True, "handoff": paired_handoff}
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
            "ladder_level_used": ladder_level_used, "target_not_locatable": False,
            "handoff": paired_handoff}


def collect_replaced_units(result: dict, claim_identity_str: str) -> list:
    """委任_42(rep22 T3で判明した不具合の是正): このStage 3の1 claim分のRewriteで実際に
    置換された範囲(前→後)を、同一cycle内の後続claimが参照できるよう取り出す
    (成功した水準の`before_after`、delete型は削除単位、pairedはJA側の対象も)。
    新方式以外・未成功なら空list。"""
    if not result.get("guard_ok"):
        return []
    h = result.get("handoff") or {}
    units = []
    for att in h.get("level_attempts", []):
        if att.get("result") != "success":
            continue
        targets = list(att.get("targets") or [])
        revised = [ba.get("after", "") for ba in att.get("before_after", [])] if att.get("before_after") else (
            att.get("revised") or [""] * len(targets))
        lang = "JA" if (h.get("text_lang") == "JA") else "EN"
        units.append({"claim_identity": claim_identity_str, "lang": lang, "before_units": targets,
                      "after_units": list(revised)})
        if att.get("ja_target") and att.get("ja_revised"):
            units.append({"claim_identity": claim_identity_str, "lang": "JA", "before_units": [att["ja_target"]],
                          "after_units": [att["ja_revised"]]})
    return units


PRIOR_ISSUE_TEXT_SOURCE_CURRENT = "current_text"
PRIOR_ISSUE_TEXT_SOURCE_ORIGINAL = "original_text"


def resolve_prior_issue_text(original_text: str, rewrite_record: dict | None, all_units: list,
                             en_now: str | None, ja_now: str | None) -> tuple:
    """委任_01(OPEN-233-KPI-RECOVERY-REDESIGN-02) 作業2-1(不具合是正、ユーザー指示):
    Recheckへ渡す`prior_issues`の`claim_in_article`は、Rewrite**前**のspan文ではなく、現行本文
    (Rewrite後)の置換後の文でなければならない(旧: Rewrite前の文を渡していたため、Checkerが本文に
    存在しない文を検証対象として受け取っていた)。決定論(¥0、追加call・類似度推測なし)。
    置換後の文は、このclaimのRewriteで実際に置換された範囲(`collect_replaced_units`)の`after_units`、
    またはcarry-forward(同一cycleの先行claimが既に書き換えた範囲)なら、先行claimの置換単位の`after`。
    全ての範囲について置換後の文が非空で、かつ現行本文(単位の言語側)に逐語で存在するときだけ
    `("\n".join(after), "current_text")`を返す。それ以外(Rewrite未成功・delete型で後が空・carry-forwardの
    置換元が見つからない・現行本文に無い等)は従来どおり元のtextと`"original_text"`を返す
    (Checker Prompt・Schema・er003の`build_prior_issues_instruction`は不変)。"""
    rec = rewrite_record or {}
    ident = rec.get("claim_identity", "")
    own = collect_replaced_units(rec, ident) if rec else []
    afters: list = []
    langs: list = []
    for u in own[:1]:  # 最初の単位=主たる書き換え(pairedのJA副単位は使わない)
        for a in u["after_units"]:
            afters.append(a)
            langs.append(u["lang"])
    h = rec.get("handoff") or {}
    for cov in (h.get("carry_forward_covered") or []):
        r = cov.get("range")
        found = None
        for u in all_units:
            for i, b in enumerate(u["before_units"]):
                if r and r in b and i < len(u["after_units"]):
                    found = (u["after_units"][i], u["lang"])
                    break
            if found:
                break
        if found is None:
            return original_text, PRIOR_ISSUE_TEXT_SOURCE_ORIGINAL
        afters.append(found[0])
        langs.append(found[1])
    if not afters:
        return original_text, PRIOR_ISSUE_TEXT_SOURCE_ORIGINAL
    seen, uniq = set(), []
    for a, lg in zip(afters, langs):
        s = (a or "").strip()
        now = ja_now if lg == "JA" else en_now
        if not s or now is None or s not in now:
            return original_text, PRIOR_ISSUE_TEXT_SOURCE_ORIGINAL
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return "\n".join(uniq), PRIOR_ISSUE_TEXT_SOURCE_CURRENT


def carry_forward_resolution(claim_rec: dict, claim_text: str, en_now: str | None, ja_now: str | None):
    """委任_42(rep22 T3で判明): 同一cycleで先行claimのRewriteが同じ文を書き換えた結果、後続
    claimのCheker文字列が現在の本文から消えている場合の扱い。cycle開始時点の本文で
    Checker文字列から範囲を確定し(再推測ではなく照合)、各範囲が先行claimのRewrite対象
    (置換済みの単位)に含まれていれば「先行Rewriteで既に書き換え済み」とみなす。
    返値: None(該当せず=従来どおり確定不能として扱う)または
    {"lang", "covered": [...], "remaining": [記事に現存する未書き換えの範囲], "res0"}。
    先行Rewriteに含まれず現存もしない範囲が1つでもあれば None(本当の確定不能)。"""
    units = claim_rec.get("cycle_replaced_units") or []
    if not units or claim_rec.get("cycle_start_en_text") is None:
        return None
    res0 = resolve_violation_spans(claim_text, claim_rec.get("cycle_start_en_text"),
                                   claim_rec.get("cycle_start_ja_text"))
    if res0["status"] != "resolved":
        return None
    lang0 = res0["lang"]
    now_text = en_now if lang0 == "EN" else ja_now
    if now_text is None:
        return None
    covered, remaining = [], []
    for r in res0["ranges"]:
        # 委任_B3(Opus R1): 範囲rが現在(置換後)の本文にまだ存在するなら「書き換え済み」とは言えない(同文複数出現で片方だけ書換の抜け道を塞ぐ、安全側)
        _r_still_present = r in now_text
        cov = None if _r_still_present else next(
            (u for u in units if u["lang"] == lang0 and any(r in b for b in u["before_units"])), None)
        partial = False
        if cov is None and not _r_still_present:
            # 委任_04(rep26 A2A3で判明した照合漏れの是正): 先行Rewriteの置換単位(`before_unit`)が、この範囲の一部(部分文字列)
            # だけを書き換えた場合(例: 先行claimがL1語レベルで文末の節だけを置換し、後続claimの範囲は文全体)。範囲は現在の本文から
            # 消えており(置換済み)、従来は確定不能(STAGE4)になった。先行指摘と後続指摘が「同じ指摘」(issue文字列・related_fact_id・
            # trueのflag集合が全て一致)の場合に限り、先行Rewriteで書き換え済みとみなす。解消の判定は従来どおり全文Recheckが担う
            # (残れば次cycleで再指摘される)。異なる指摘は従来どおり確定不能(Human Reviewへ倒す新経路ではなく、倒す経路を減らす方向のみ)。
            info = claim_rec.get("cycle_claim_info") or {}
            dev_now = claim_rec.get("dev") or {}
            for u in units:
                if u["lang"] != lang0 or not any(b and b in r for b in u["before_units"]):
                    continue
                prior = info.get(u["claim_identity"])
                if (prior is not None and prior["issue"] == (dev_now.get("issue") or "")
                        and (prior["related_fact_id"] or "") == (dev_now.get("related_fact_id") or "")
                        and prior["true_flags"] == _dev_true_flags(dev_now)):
                    cov, partial = u, True
                    break
        if cov is not None:
            covered.append({"range": r, "covered_by_claim": cov["claim_identity"], **({"partial_overlap": True} if partial else {})})
        elif now_text.count(r) == 1:
            remaining.append(r)
        else:
            return None
    if not covered:
        return None
    return {"lang": lang0, "covered": covered, "remaining": remaining, "res0": res0}


def _dev_true_flags(dev: dict) -> list:
    """委任_49(記録専用): Checkerの10種類のflagのうちtrueのもの(名前の昇順)。"""
    return sorted(k for k in CHECKER_FLAG_NAMES if (dev or {}).get(k) is True)


CHECKER_FLAG_NAMES = ("changed_fact", "changed_scope", "changed_causality", "changed_certainty", "changed_number",
                      "changed_actor", "changed_negation", "changed_comparison", "changed_time",
                      "unsupported_new_claim")


def _resolution_used_l6(resolution: dict) -> bool:
    """委任_05: 確定がL6(sentence_restore)の復元を含むか(配列経路はlevelが`SPANS:...`に要素のlevelを含む)。"""
    return VS_L6_LEVEL in str(resolution.get("level") or "")


def l6_carry_forward_precedence(claim_rec: dict, claim_text: str, resolution: dict,
                                en_now: str | None, ja_now: str | None):
    """委任_05(rep27 safety_A4 s1・A5 s1の是正、決定論・追加call 0): L6が復元した文が、同一cycleの先行claimの
    Rewriteで既に書き換え済みの文だった場合、carry-forward(`covered_by_earlier_rewrite_in_cycle`)を優先する。
    旧: 先行RewriteでCheckerの引用文字列(引用符なし版)が本文から消える→`mismatch`→L6が書き換え済みの文を復元→
    2回目のRewrite(ladder枯渇→STAGE4)。rep24(L6 OFF)ではmismatch→carry-forwardで合格していた。
    (1)carry-forward判定(委任_04の部分一致を含む、cycle開始時点の本文での照合)で全範囲が先行Rewrite済みなら採用。
    (2)(1)で確定しない場合でも、L6の復元範囲がすべて同cycleの先行Rewriteの置換後の文(`after_units`)と一致する場合は、
    その置換単位のclaimでcovered扱いにする。それ以外(未書き換えの範囲が残る・先行Rewriteと無関係)は従来どおりL6の結果を使う
    (返値None)。`covered`の`range`は、`resolve_prior_issue_text`が置換後の文を引けるよう置換前の単位にする。"""
    units = claim_rec.get("cycle_replaced_units") or []
    pre = carry_forward_resolution(claim_rec, claim_text, en_now, ja_now)
    if pre is not None and not pre["remaining"]:
        pre["l6_precedence"] = {"skipped_reason": "carry_forward_precedence", "rule": "cycle_start_match",
                                "l6_restored_ranges": list(resolution.get("ranges") or []),
                                "sentence_restore": resolution.get("sentence_restore")}
        return pre
    lang = resolution.get("lang")
    ranges = list(resolution.get("ranges") or [])
    if not ranges or lang is None:
        return None
    covered = []
    for r in ranges:
        hit = None
        for u in units:
            if u["lang"] != lang:
                continue
            for i, a in enumerate(u["after_units"]):
                if (a or "").strip() and r.strip() == a.strip() and i < len(u["before_units"]):
                    hit = (u, i)
                    break
            if hit:
                break
        if hit is None:
            return None
        covered.append({"range": hit[0]["before_units"][hit[1]], "covered_by_claim": hit[0]["claim_identity"],
                        "via": "l6_restored_equals_after_unit"})
    return {"lang": lang, "covered": covered, "remaining": [], "res0": None,
            "l6_precedence": {"skipped_reason": "carry_forward_precedence", "rule": "restored_equals_after_unit",
                              "l6_restored_ranges": ranges, "sentence_restore": resolution.get("sentence_restore")}}


def _carry_forward_comparison(claim_rec: dict, cf: dict) -> list:
    """委任_49 2-4(記録専用、carry-forwardの動作は変えない): carry-forwardが発動したとき、先行指摘
    (同一cycleで同じ文を先に書き換えたclaim)と後続指摘(今回のclaim)の`issue`が同じ内容か異なるか
    (文字列一致と、`related_fact_id`・trueのflag集合の一致)を記録する。"""
    info = claim_rec.get("cycle_claim_info") or {}
    dev = claim_rec.get("dev") or {}
    out = []
    for cov in cf.get("covered", []):
        prior = info.get(cov.get("covered_by_claim"))
        if prior is None:
            out.append({"covered_by_claim": cov.get("covered_by_claim"), "comparison": "prior_info_unavailable"})
            continue
        fl_now = _dev_true_flags(dev)
        out.append({"covered_by_claim": cov.get("covered_by_claim"),
                    "issue_string_equal": (prior["issue"] == (dev.get("issue") or "")),
                    "same_related_fact_id": ((prior["related_fact_id"] or "") == (dev.get("related_fact_id") or "")),
                    "true_flags_equal": (prior["true_flags"] == fl_now),
                    "prior_issue": prior["issue"], "following_issue": dev.get("issue") or "",
                    "prior_related_fact_id": prior["related_fact_id"],
                    "following_related_fact_id": dev.get("related_fact_id") or "",
                    "prior_true_flags": prior["true_flags"], "following_true_flags": fl_now})
    return out


def run_stage3_for_claim_spans(client, state, consecutive_errors, call_log, label_prefix, fixture,
                                current_en_text: str, current_ja_text: str | None, claim_rec: dict,
                                use_pairing: bool) -> dict:
    """委任_42: 新方式のStage 3入口(範囲の確定+同一cycle内の先行Rewriteによる書き換え済みの扱い)。
    現在の本文でCheckerの文字列から範囲を確定する。確定できず、かつその文字列がcycle開始
    時点の本文では確定でき、その範囲が同一cycleの先行claimのRewrite対象に含まれていた
    場合(rep22 T3で判明: LLM claimとprecheck floor claimが同じ文を指し、先行Rewriteで文が
    変わると後続の文字列が現在の本文から消える)は、確定不能(Stage 4)ではなく「先行Rewriteで
    既に書き換え済み」として扱う(Rewriteを重ねない=不要Rewriteを増やさない。解消の判定は
    全文Recheckが担う)。現存する未書き換えの範囲が残る場合はそれだけをRewriteする。"""
    claim_text = claim_rec["claim_text"]
    resolution = resolve_violation_spans(claim_text, current_en_text, current_ja_text)
    cf = None
    l6_precedence = None
    if resolution["status"] != "resolved":
        cf = carry_forward_resolution(claim_rec, claim_text, current_en_text, current_ja_text)
    elif _resolution_used_l6(resolution) and claim_rec.get("cycle_replaced_units"):
        # 委任_05(OPEN-233-KPI-RECOVERY-REDESIGN-02、rep27 A4/A5のHuman Review是正): L6が、同cycleの先行Rewriteで
        # 書き換え済みの文を「復元」して返した場合、carry-forward判定をL6より先に適用する(二重Rewrite防止)。
        cf = l6_carry_forward_precedence(claim_rec, claim_text, resolution, current_en_text, current_ja_text)
        if cf is not None:
            l6_precedence = cf.get("l6_precedence")
    cf_comparison = _carry_forward_comparison(claim_rec, cf) if cf is not None else None
    if cf is not None:
        if not cf["remaining"]:
            handoff = {"mode": HANDOFF_MODE_VIOLATION_SPAN, "checker_claim_text": claim_text,
                       "resolution": {"status": "covered_by_earlier_rewrite_in_cycle", "lang": cf["lang"],
                                      "ranges": [c["range"] for c in cf["covered"]],
                                      # 委任_66(記録専用): cycle開始時点の確定がL6の復元だった場合、その記録を残す
                                      **({"cycle_start_level": (cf.get("res0") or {}).get("level"),
                                          "sentence_restore": (cf.get("res0") or {}).get("sentence_restore")}
                                         if (cf.get("res0") or {}).get("sentence_restore") is not None else {}),
                                      # 委任_05(記録専用): L6がこの文を復元したが、carry-forwardを優先して二重Rewriteしなかった
                                      **({"l6_skipped": l6_precedence} if l6_precedence is not None else {})},
                       "carry_forward_covered": cf["covered"], "level_attempts": [], "level_used": None,
                       "span_unverified": False, "skipped_covered_by_earlier_rewrite": True,
                       "carry_forward_comparison": cf_comparison}
            return {"mechanism": ("paired_ja_en(J-1)" if use_pairing else "single_text_local(E-2/delete-generic)"),
                    "en_text": current_en_text, "ja_text": current_ja_text,
                    "method": "covered_by_earlier_rewrite_in_cycle", "guard_ok": False,
                    "before_fragment": None, "after_fragment": None, "ladder_level_used": None,
                    "target_not_locatable": False, "span_unverified": False,
                    "ladder_exhausted_without_full_rewrite": False, "handoff": handoff}
        now_text = current_en_text if cf["lang"] == "EN" else current_ja_text
        raw_spans = [(now_text.find(r), now_text.find(r) + len(r)) for r in cf["remaining"]]
        merged = vs_merge_spans(raw_spans, now_text)
        resolution = {"status": "resolved", "lang": cf["lang"], "level": "carry_forward",
                      "ranges": [now_text[a:b] for a, b in merged], "spans": merged, "raw_spans": raw_spans,
                      "per_lang": {}, "both_langs_ok": False, "claim_text": claim_text, "reason": None,
                      "carry_forward_covered": cf["covered"]}
    res = _run_stage3_spans_core(client, state, consecutive_errors, call_log, label_prefix, fixture,
                                 current_en_text, current_ja_text, claim_rec, use_pairing, resolution)
    if cf is not None and isinstance(res.get("handoff"), dict):
        res["handoff"]["carry_forward_covered"] = cf["covered"]
        res["handoff"]["carry_forward_comparison"] = cf_comparison
    return res


def _run_stage3_spans_core(client, state, consecutive_errors, call_log, label_prefix, fixture,
                            current_en_text: str, current_ja_text: str | None, claim_rec: dict,
                            use_pairing: bool, resolution: dict) -> dict:
    """委任_42 仕様(1)(2)(8): 新方式のStage 3入口。Checkerの文字列を、EN本文・JA本文の
    両方に対して照合して範囲を確定し(どちらで確定したかを保持)、次のとおり振り分ける。
    - 確定不能(0箇所/複数箇所/説明文混在): Rewriteを試みず`span_unverified`
      (呼び出し側がStage 4`violation_span_unverified`へ)。他の指摘は通常どおり処理される。
    - originが`ja_source`でEN本文で単一範囲に確定: 既存の`paired_rewrite`(EN側の対象だけ
      新方式の確定範囲に差し替え、JA側の対応決定は既存処理のまま変更しない)。
    - originが`ja_source`でEN本文で複数範囲に確定、またはJA本文でのみ確定: **暫定**
      (JA側の構造見直し[英語だけ直す化]は別委任のため本委任では最小対応に留める)。
      確定できた言語側だけを新方式で直す既存の片側経路(`single_text_rewrite`)に入れ、
      もう一方は既存の再検査(JA Recheck)に任せる。`locate_multi_quote_span`+位置比優先は
      使わない。該当件数は`handoff["ja_provisional_path"]`で記録する。
    - originが`ja_source`でない: EN本文で確定した範囲を単一言語のladderで直す。JA本文
      でのみ確定した場合は、JA側を直す経路を持たないため確定不能(fail-closed)とする。"""
    working_fixture = dict(fixture)
    working_fixture["article_text"] = current_en_text
    if current_ja_text is not None:
        working_fixture["source_article_text"] = current_ja_text
    claim_text = claim_rec["claim_text"]
    claim_rec = dict(claim_rec)
    claim_rec["span_resolution"] = resolution
    mechanism_single = "single_text_local(E-2/delete-generic)"
    mechanism_paired = "paired_ja_en(J-1)"

    def _unverified(reason: str, detail: str | None = None) -> dict:
        handoff = {"mode": HANDOFF_MODE_VIOLATION_SPAN, "checker_claim_text": claim_text,
                   "resolution": {k: resolution.get(k) for k in (
                       "status", "lang", "level", "reason", "detail", "ranges", "per_lang", "both_langs_ok")},
                   "level_attempts": [], "level_used": None, "span_unverified": True,
                   "span_unverified_reason": reason, "span_unverified_detail": detail}
        if resolution.get("sentence_restore") is not None:  # 委任_66(記録専用): L6の試行結果(復元しなかった理由)
            handoff["sentence_restore"] = resolution["sentence_restore"]
        return {"mechanism": mechanism_paired if use_pairing else mechanism_single,
                "en_text": current_en_text, "ja_text": current_ja_text, "method": "violation_span_unverified",
                "guard_ok": False, "before_fragment": None, "after_fragment": None, "ladder_level_used": None,
                "target_not_locatable": True, "span_unverified": True, "span_unverified_reason": reason,
                "ladder_exhausted_without_full_rewrite": False, "handoff": handoff}

    if resolution["status"] != "resolved":
        reason = resolution.get("reason") or "mismatch"
        # 委任_49 4-3: JA_MODE=english_onlyでは日本語本文を照合へ渡さない(current_ja_textがNone)。
        # Checker文字列が(記録だけのために見た)元の日本語本文でしか確定しない場合は、確定不能のまま
        # 理由コードで残す(日本語側を直す経路がないため。`ja_only_match_origin_not_ja_source`を
        # originがja_sourceの指摘にも適用した扱い)。記録のためだけに照合し、範囲の確定には使わない。
        if (JA_MODE == JA_MODE_ENGLISH_ONLY and reason == "mismatch" and current_ja_text is None
                and fixture.get("source_article_text") is not None):
            res_ja = resolve_violation_spans(claim_text, None, fixture["source_article_text"])
            if res_ja["status"] == "resolved":
                return _unverified("ja_only_match_english_only",
                                   "Checker文字列は元の日本語本文でのみ確定する(JA_MODE=english_onlyでは日本語側を"
                                   "直さないため確定不能として扱う、fail-closed)")
        return _unverified(reason)

    lang = resolution["lang"]
    n_ranges = len(resolution["ranges"])
    if not use_pairing:
        if lang == "JA":
            return _unverified("ja_only_match_origin_not_ja_source",
                               "Checker文字列はJA本文でのみ確定したが、originがja_sourceでなく"
                               "JA側を直す経路を持たないため確定不能として扱う(fail-closed)")
        res = single_text_rewrite(client, state, consecutive_errors, call_log, label_prefix, working_fixture,
                                  "article_text", claim_rec)
        return {"mechanism": mechanism_single, "en_text": res["updated_text"], "ja_text": current_ja_text,
                "method": res["method"], "guard_ok": res["guard_ok"],
                "before_fragment": res.get("before_fragment"), "after_fragment": res.get("after_fragment"),
                "target_not_locatable": res.get("target_not_locatable", False),
                "span_unverified": res.get("span_unverified", False),
                "ladder_level_used": res.get("ladder_level_used"),
                "ladder_exhausted_without_full_rewrite": res.get("ladder_exhausted_without_full_rewrite", False),
                "handoff": res.get("handoff")}

    if lang == "EN" and n_ranges == 1:
        res = paired_rewrite(client, state, consecutive_errors, call_log, label_prefix, working_fixture, claim_rec)
        handoff = res.get("handoff") or {}
        handoff["ja_provisional_path"] = False
        return {"mechanism": mechanism_paired, "en_text": res["updated_en_text"], "ja_text": res["updated_ja_text"],
                "method": res["method"], "guard_ok": res["guard_ok"],
                "before_fragment": res.get("before_fragment"), "after_fragment": res.get("after_fragment"),
                "ladder_level_used": res.get("ladder_level_used"),
                "target_not_locatable": res.get("target_not_locatable", False),
                "span_unverified": False,
                "ladder_exhausted_without_full_rewrite": res.get("ladder_exhausted_without_full_rewrite", False),
                "handoff": handoff}

    # 暫定(JA側の構造見直しまで): 確定できた言語側だけを新方式で直す片側経路
    provisional_reason = ("en_multiple_ranges" if lang == "EN" else "ja_only_match")
    field = "article_text" if lang == "EN" else "source_article_text"
    only_text = current_en_text if lang == "EN" else current_ja_text
    mini_fixture = {"ledger_text": fixture["ledger_text"], field: only_text}
    res = single_text_rewrite(client, state, consecutive_errors, call_log, f"{label_prefix}_j1_single_side",
                              mini_fixture, field, claim_rec)
    handoff = res.get("handoff") or {}
    handoff["ja_provisional_path"] = True
    handoff["ja_provisional_reason"] = provisional_reason
    handoff["ja_provisional_note"] = ("暫定(委任_42): 確定できた言語側だけを直し、もう一方は既存のJA Recheckに"
                                       "任せる。JA側の構造見直しは別委任")
    new_en, new_ja = current_en_text, current_ja_text
    if res.get("guard_ok"):
        if lang == "EN":
            new_en = res["updated_text"]
        else:
            new_ja = res["updated_text"]
    return {"mechanism": mechanism_paired, "en_text": new_en, "ja_text": new_ja,
            "method": f"j1_single_side_{lang.lower()}({res.get('method')})", "guard_ok": res.get("guard_ok", False),
            "before_fragment": res.get("before_fragment"), "after_fragment": res.get("after_fragment"),
            "ladder_level_used": res.get("ladder_level_used"),
            "target_not_locatable": res.get("target_not_locatable", False),
            "span_unverified": res.get("span_unverified", False),
            "ladder_exhausted_without_full_rewrite": res.get("ladder_exhausted_without_full_rewrite", False),
            "handoff": handoff}


def run_stage3_for_claim(client, state, consecutive_errors, call_log, label_prefix, fixture,
                          current_en_text: str, current_ja_text: str | None, claim_rec: dict) -> dict:
    """1 claim分のRewriteを実行し、更新後の(en_text, ja_text)を返す。"""
    use_pairing = (
        claim_rec.get("origin") == "ja_source"
        and current_ja_text is not None
        and fixture.get("source_article_text") is not None
    )
    if HANDOFF_MODE == HANDOFF_MODE_VIOLATION_SPAN:
        return run_stage3_for_claim_spans(client, state, consecutive_errors, call_log, label_prefix, fixture,
                                          current_en_text, current_ja_text, claim_rec, use_pairing)
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
    起こり得る)への一般的な安全網として(f)を新設する。

    【委任_49 4-5: docstringとコードの食い違いの訂正(挙動は変えない)】上の「(c)は
    ラダー水準に関わらず維持する」「paired J-1は常に全文Recheckを維持」は委任_19時点の記述で、
    その後の委任_20 W3で(c)は「pairedかつ(ladder>=④ or JAガード不通過)」へ縮小された。
    **現在のコードの(c)は縮小後のもの**(`paired_records`があり、かつladder>=④またはja_guard_ok
    が偽のときだけ`both_ja_en_changed(paired_j1)`を理由に加える。paired J-1でもladder①〜③で
    JAガードを通れば、(c)単独では全文Recheckにならない)。したがって、日本語側の処理を迂回すると
    (JA_MODE=english_only、委任_49)(c)は常に不成立になり、`origin=="ja_source"`の指摘も他の
    理由(a)(b)(d)〜(h)に該当しなければ局所QA fastpathで合格しうる。この補正として、
    english_onlyではja_sourceの指摘を書き換えた周回に限り全文Recheckを必須にする
    (`english_only_ja_source_requires_full_recheck`)。"""
    reasons = []
    if any((r.get("ladder_level_used") in LOCAL_QA_ESCALATION_LADDER_LEVELS) for r in rewrite_records):
        reasons.append("paragraph_or_full_or_delete_rewrite")
    # 委任_49 4-2(Opus独立レビュー#6の必須補正): JA_MODE=english_onlyでは日本語側のガード(JA Recheck・
    # JA fail-openガード・paired判定による(c))が働かないため、originがja_sourceの指摘を書き換えた周回は
    # 局所QA fastpath(対象文の前後だけを見る)を使わず全文Recheckを必須にする(全文検査なしの合格を許さない)。
    # originがja_source以外の指摘の扱いは変えない。JA_MODEが既定(paired)なら何も追加しない。
    if JA_MODE == JA_MODE_ENGLISH_ONLY and any(c.get("origin") == "ja_source" for c in blocking_claims):
        reasons.append("english_only_ja_source_requires_full_recheck")
    if len(rewrite_records) > 1:
        reasons.append("multiple_claims_rewritten_same_cycle")
    # 委任_20 W3: (c)を「paired かつ(ladder≥④ or JAガード不通過)」へ縮小。
    paired_records = [r for r in rewrite_records if r.get("mechanism", "").startswith("paired")]
    if paired_records:
        paired_high_ladder = any(
            r.get("ladder_level_used") in LOCAL_QA_ESCALATION_LADDER_LEVELS for r in paired_records)
        if paired_high_ladder or ja_guard_ok is False:
            reasons.append("both_ja_en_changed(paired_j1)")
    # 委任_66(L6、Opus#9論点4(a)): issue_focus_absentでRewriteを見送ったclaimがあるcycleは、局所QA(Rewrite前後の
    # 文だけを見る)では確認できないため、必ず全文Recheckで判定する。
    if any(((r.get("handoff") or {}).get("issue_focus_absent")) for r in rewrite_records):
        reasons.append("issue_focus_absent_recheck_only")
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
                # OPEN-238: 対象文特定も厳格版抽出("third party"文を誤って対象にしない)
                nums = precheck.extract_percentages_strict(s) | set(precheck.extract_counts(s))
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
#
# 委任_04(OPEN-233-CHECKER-FLOOR-PRODUCTION-E2E-01、Opus M4、PRODUCTION_WIRED未): 承認構成では数字(number_mismatch)のみ残す。
# date/actor/negation/comparison markerは「AIを強制的に重大へ上書きする機械判定」のため廃止(Stage 2をスキップしない)。
# 絞り込みはこの1関数(`filter_precheck_findings`)のみ。`build_precheck_floor_claims`(初回・F3・次cycle)が共用する。
# 既定=legacy_all(旧挙動、既存テスト維持)。
PRECHECK_KINDS_NUMBER_ONLY = ("number_mismatch",)
PRECHECK_MODE_LEGACY, PRECHECK_MODE_NUMBER_ONLY = "legacy_all", "number_only"
PRECHECK_MODES = (PRECHECK_MODE_LEGACY, PRECHECK_MODE_NUMBER_ONLY)
PRECHECK_MODE = PRECHECK_MODE_LEGACY


def filter_precheck_findings(findings: list) -> list:
    if PRECHECK_MODE not in PRECHECK_MODES:
        raise ValueError(f"PRECHECK_MODE must be one of {PRECHECK_MODES}, got {PRECHECK_MODE!r}")
    if PRECHECK_MODE == PRECHECK_MODE_LEGACY:
        return list(findings)
    return [f for f in findings if f.get("kind") in PRECHECK_KINDS_NUMBER_ONLY]


def build_precheck_floor_claims(fixture: dict, existing_fact_ids: set) -> list:
    findings = filter_precheck_findings(precheck.run_precheck(fixture["ledger_text"], fixture["article_text"]))
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
# ------------------------------------------------------------
# 委任_49 作業2(記録専用): 合否・重大度・書き換え対象の決定には一切使わない。
# ------------------------------------------------------------
PASS_FINAL_STATES = ("ACCEPTABLE_STAGE1", "RESOLVED_STAGE2_DOWNGRADE", "RESOLVED_REWRITE",
                     "RESOLVED_REWRITE_THEN_DOWNGRADE")


def raw_deviation_record(d: dict) -> dict:
    """Checkerが返した指摘1件の記録(MINORを含む全件用)。`passed_downstream`=後段へ渡る(MAJOR)か。"""
    return {"severity": d.get("severity"), "claim_in_article": d.get("claim_in_article"),
            "related_fact_id": d.get("related_fact_id"), "origin": d.get("origin"), "issue": d.get("issue"),
            "explanation": d.get("explanation"), "true_flags": _dev_true_flags(d),
            "enumeration_source_claim": bool(d.get("enumeration_source_claim")),
            "same_fact_id_locations": d.get("same_fact_id_locations"),
            "passed_downstream": d.get("severity") == "MAJOR"}


def _norm_for_residual(t: str) -> str:
    return " ".join((t or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').split())


def compute_residual_at_pass(instance_id: str, final_state: str | None, final_en_text: str | None,
                             cycles: list, raw_stage1: list, raw_rechecks: list) -> dict:
    """委任_49 2-1: `SAFETY_CRITICAL_CLAIM_DEFS`の`text_substring`が、最終状態が合格系(人間確認なし)
    のとき最終英語本文に残っているかを、指摘されたかどうかに関係なく記録する。既存の
    `detect_safety_critical_misdowngrades`(指摘された後の降格のみ)とは別(併存)。
    記録: 該当定義名・残存の有無・その実行で一度でもBLOCKINGで指摘されたか(Stage 2の最終materialityが
    BLOCKINGで、claim_textに部分文字列を含む=fact_idは問わない/同一fact_idも別記録)。"""
    defs = _safety_critical_defs(instance_id)  # 委任_55: 期待QUALITYの監視用定義(Meta-1/2)は対象外
    passed = final_state in PASS_FINAL_STATES
    out = {"applicable_defs": len(defs), "final_state": final_state, "final_state_is_pass_family": passed,
           "defs": []}
    if not defs:
        return out
    fin = _norm_for_residual(final_en_text or "")
    for d in defs:
        sub = _norm_for_residual(d["text_substring"])
        flagged_any_fact = flagged_same_fact = flagged_nonblocking = False
        for c in cycles or []:
            for sr in c.get("stage2_results", []):
                if sub in _norm_for_residual(sr.get("claim_text") or ""):
                    if sr.get("materiality") == "BLOCKING":
                        flagged_any_fact = True
                        if (sr.get("related_fact_id") or "").strip() == d["related_fact_id"]:
                            flagged_same_fact = True
                    else:
                        flagged_nonblocking = True
        in_raw = []
        for src, devs in [("stage1", raw_stage1 or [])] + [(f"recheck_c{r['cycle']}", r["deviations"])
                                                          for r in (raw_rechecks or [])]:
            for x in devs:
                if sub in _norm_for_residual(x.get("claim_in_article") or ""):
                    in_raw.append({"source": src, "severity": x.get("severity"),
                                   "related_fact_id": x.get("related_fact_id")})
        out["defs"].append({
            "sub_id": d["sub_id"], "related_fact_id": d["related_fact_id"], "text_substring": d["text_substring"],
            "remains_in_final_en": sub in fin if final_en_text is not None else None,
            # 委任_08(Fable評価6): `text_pattern`版(定義にtext_patternが無ければ旧と同値)。旧新並記
            "remains_in_final_en_pattern": (safety_def_matches(d, final_en_text or "", True) if final_en_text is not None else None),
            "ever_blocking_flagged": flagged_any_fact, "ever_blocking_flagged_same_fact_id": flagged_same_fact,
            "ever_flagged_but_never_blocking": (flagged_nonblocking and not flagged_any_fact),
            "in_checker_raw_deviations_any_severity": in_raw,
            "pass_with_residual_unflagged": bool(passed and sub in fin and not flagged_any_fact),
            "pass_with_residual_unflagged_pattern": bool(passed and final_en_text is not None
                                                          and safety_def_matches(d, final_en_text, True) and not flagged_any_fact)})
    return out


def _en_title_line(text: str | None) -> str | None:
    """英語本文の見出し(`# `で始まる最初の行。`## `等は含めない)。"""
    for line in (text or "").splitlines():
        if line.startswith("# "):
            return line.strip()
    return None


def _wobble_observe(registry: dict, records: list, cycle: int, stage2_results: list, en_text: str) -> list:
    """委任_49 2-3(設計書§4-3のC3、記録専用): 同じ確定範囲・同じfact_idの最終判定(materiality)が周回間で
    変わったら、両周回のflag・LLM判定・floor理由・降格理由(basis)を記録する。同一周回内の比較はしない。"""
    new = []
    for c in stage2_results:
        fid = (c.get("related_fact_id") or "").strip()
        res = resolve_violation_spans(c.get("claim_text") or "", en_text, None)
        txt = "\n".join(res["ranges"]) if res["status"] == "resolved" else (c.get("claim_text") or "")
        key = (fid, " ".join(txt.split()))
        obs = {"cycle": cycle, "materiality": c.get("materiality"), "llm_materiality": c.get("llm_materiality"),
               "floor_reason": c.get("floor_reason"), "basis": c.get("basis"),
               "true_flags": _dev_true_flags(c.get("dev") or {}), "range_resolved": res["status"] == "resolved"}
        prev_obs = [o for o in registry.get(key, []) if o["cycle"] < cycle]
        if prev_obs and prev_obs[-1]["materiality"] != obs["materiality"]:
            rec = {"related_fact_id": fid, "range": key[1], "from": prev_obs[-1], "to": obs}
            records.append(rec)
            new.append(rec)
        registry.setdefault(key, []).append(obs)
    return new


def _record_carry_forward_recheck(rewrite_records: list, resolved_items, source: str) -> None:
    """委任_49 2-4(記録専用): carry-forwardで「先行Rewriteで書き換え済み」とされたclaimが、その周回のRecheck
    (`prior_issues_resolved`、indexはblocking claimの順)で解消扱いになったかを、handoffへ記録する。
    全文Recheckを経ない周回(局所QA fastpath)ではNone。"""
    by_idx = {}
    for it in (resolved_items or []):
        if isinstance(it, dict) and isinstance(it.get("index"), int):
            by_idx[it["index"]] = bool(it.get("resolved"))
    for i, rec in enumerate(rewrite_records):
        h = rec.get("handoff") if isinstance(rec, dict) else None
        if isinstance(h, dict) and h.get("carry_forward_covered"):
            h["carry_forward_recheck_resolved"] = by_idx.get(i) if resolved_items is not None else None
            h["carry_forward_recheck_source"] = source


# ============================================================
# 委任_11(OPEN-233-KPI-RECOVERY-REDESIGN-02、Opus#14後のFable評価、設計書§18): 位置座標の引継ぎ(I-1最小実装)・STAGE4許可リスト(I-2)
# の決定論ヘルパー。全て¥0・LLM callなし。Trial専用。
# ============================================================
STAGE4_ALLOWED_REASONS = frozenset({
    "blocking_confirmed_unlocatable_after_cap", "blocking_structural_after_ladder", "post_T_new_blocking", "api_failure"})
# 現行本文の具体的箇所についてStage 2(+S1)がBLOCKINGを確定したこと(funnel通過)を要する理由
STAGE4_FUNNEL_REQUIRED_REASONS = frozenset({
    "blocking_confirmed_unlocatable_after_cap", "blocking_structural_after_ladder", "post_T_new_blocking"})


def stage4_allowlist_decision(reason: str, context: dict | None = None) -> dict:
    """I-2: STAGE4(Human Review)へ進めてよいかを1箇所で決める。許可reason(4種)のみ許可し、BLOCKING由来の3種は
    Stage 2(+S1)がその周で確定済み(`context["funnel_passed"]`)であることも要する。許可外は`action="funnel"`
    (呼び出し側が判定だけのcycle/次cycleへ戻す)で、`violation`へ記録名を残す。"""
    ctx = context or {}
    if reason not in STAGE4_ALLOWED_REASONS:
        return {"allowed": False, "reason": reason, "action": "funnel", "violation": "reason_not_in_allowlist"}
    if reason in STAGE4_FUNNEL_REQUIRED_REASONS and not ctx.get("funnel_passed", False):
        return {"allowed": False, "reason": reason, "action": "funnel", "violation": "not_funnelled"}
    return {"allowed": True, "reason": reason, "action": "stage4", "violation": None}


def h1_rerun_stage1(first_parsed: dict, rerun_fn) -> dict:
    """委任_06 H1: Stage 1 API失敗の再実行1回。legacy_v4aは`rerun_fn`を1回呼ぶ(戻り値がなお失敗ならSTOPは呼び出し側)。
    coverage_unionは各経路をmodule内で再実行1回済みのため追加で呼ばず、初回結果をそのまま返す。"""
    if STAGE1_MODE == STAGE1_MODE_COVERAGE_UNION:
        return first_parsed
    return rerun_fn()


def stage1_api_failure_stop_result(inst: dict, call_log: list, t0: float, raw_stage1_all: list, fixture: dict,
                                   stage1_call_used: bool) -> dict:
    """委任_06 H1: Stage 1のAPI失敗が(再実行後も)残った場合のfail-closed結果。PASSへ抜けず、既存許可リスト関数
    (`stage4_allowlist_decision("api_failure")`=許可)でSTAGE4_ESCALATIONへ。後段(Stage 2〜)は実行しない。"""
    d = stage4_allowlist_decision("api_failure", {})
    iid = inst["instance_id"]
    return {
        "instance_id": iid, "group": inst["group"], "expected_group_label": inst["expected_group_label"],
        "final_state": "STAGE4_ESCALATION", "stage4_reason": d["reason"], "cycles": [],
        "stage1_call_used": stage1_call_used, "stage1_recall_miss_substituted": False,
        "s1u_screen_used": False, "s1u_additional_blocking_count": 0, "s1u_additional_block": False,
        "s1u_additional_block_label": None, "call_log": call_log,
        "total_cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4), "total_calls": len(call_log),
        "elapsed_seconds": round(time.time() - t0, 3),
        "switches": {"JA_MODE": JA_MODE, "VS_MATCH_EXT": VS_MATCH_EXT, "HANDOFF_MODE": HANDOFF_MODE,
                     "STAGE1_FAIL_CLOSED": True, "STAGE1_MODE": STAGE1_MODE},
        "stage4_allowlist": {"decisions": [{"cycle": 0, "decision": d, "legacy_reason": None}],
                              "n_rerouted_legacy_exits": 0, "final_reason_outside_allowlist": False},
        "stage1_api_failure_stop": True,
        "all_deviations_raw": {"stage1": raw_stage1_all, "rechecks": []},
        "residual_at_pass": compute_residual_at_pass(iid, "STAGE4_ESCALATION", fixture["article_text"], [],
                                                     raw_stage1_all, []),
        "severity_wobble": [], "en_title_rewritten": False, "en_title_changes": [],
    }


def _revert_norm(s: str) -> str:
    return re.sub(r"\s+", " ", vs_quote_glyph_norm(s or "")).strip()


def revert_to_prior_state_detected(prior_states: list, current_text: str, target: str, revised: str,
                                   ctx_chars: int = 30) -> bool:
    """A2: 書き換え候補`revised`(`target`の置換案)が、この箇所の過去の状態(prior_states=原文・前cycleまでの本文)と同じか。
    現行本文での`target`の前後ctx_chars字(正規化後)を添えた形が過去本文に完全一致するときだけ真(位置つきの照合)。
    削除案(空)・targetが現行本文に一意でない場合は判定しない。"""
    if not (revised or "").strip() or not prior_states or current_text.count(target) != 1:
        return False
    pos = current_text.find(target)
    left = _revert_norm(current_text[:pos])[-ctx_chars:]
    right = _revert_norm(current_text[pos + len(target):])[:ctx_chars]
    needle = left + (" " if left else "") + _revert_norm(revised) + (" " if right else "") + right
    needle = needle.strip()
    if _revert_norm(target) == _revert_norm(revised):
        return False
    return any(needle and needle in _revert_norm(p) for p in prior_states)


def _occurrences(text: str, sub: str) -> list:
    if not sub:
        return []
    out, i = [], text.find(sub)
    while i >= 0:
        out.append((i, i + len(sub)))
        i = text.find(sub, i + 1)
    return out


def claim_ranges_in_text(claim: dict, text: str) -> list:
    """claimの確定範囲(`span_resolution_cycle_start["ranges"]`)の現行本文での座標[(a,b)]。確定不能なら空。"""
    sr = claim.get("span_resolution_cycle_start") or {}
    if sr.get("status") != "resolved":
        return []
    out = []
    for r in sr.get("ranges") or []:
        occ = _occurrences(text, r)
        if occ:
            out.append(occ[0])
    return out


def location_prior_levels(regions: list, claim: dict, text: str) -> tuple:
    """B′: claimの確定範囲が、前cycleまでの置換範囲(regions)と1文字以上重なるか。(重なったlevel名のlist, 重なった件数)。"""
    cl = claim_ranges_in_text(claim, text)
    levels: set = set()
    n = 0
    for rg in regions:
        for (c, d) in _occurrences(text, rg["text"]):
            if any(a < d and c < b for (a, b) in cl):
                levels |= set(rg["levels"])
                n += 1
                break
    return sorted(levels), n


def update_regions_after_rewrite(regions: list, pre_text: str, rewrite_records: list, cycle: int) -> list:
    """I-1最小実装: Rewriteで置換された範囲(置換後の文字列)を、前の置換範囲との重なりを引き継いで保持する。
    置換後が空(削除)の範囲は保持しない。座標は文字列としてではなく本文中の出現位置で再計算される(`location_prior_levels`)。"""
    out = list(regions)
    for rec in rewrite_records:
        h = rec.get("handoff") or {}
        for att in h.get("level_attempts", []):
            if att.get("result") != "success":
                continue
            lvl = att.get("level")
            for t, r in zip(att.get("targets") or [], att.get("revised") or [""] * len(att.get("targets") or [])):
                inherited: set = set()
                tr = _occurrences(pre_text, t)
                keep = []
                for rg in out:
                    ov = any(a < d and c < b for (c, d) in _occurrences(pre_text, rg["text"]) for (a, b) in tr[:1])
                    if ov:
                        inherited |= set(rg["levels"])
                    else:
                        keep.append(rg)
                out = keep
                if (r or "").strip():
                    out.append({"text": r, "levels": sorted(inherited | {lvl}), "cycle": cycle})
    return out


def _span_key(text_ranges: list, fact_id: str):
    return (frozenset(re.sub(r"\s+", " ", vs_quote_glyph_norm(r)).strip().lower() for r in text_ranges),
            (fact_id or "").strip())


def claim_materiality_key(claim_text: str, fact_id: str, en_text: str):
    """S-4: materialityを本文に紐づけるキー=(箇所の正規化span集合, fact_id)。確定不能ならNone。"""
    res = resolve_violation_spans(claim_text, en_text, None)
    if res.get("status") != "resolved" or not res.get("ranges"):
        return None
    return _span_key(res["ranges"], fact_id)


def run_instance(client, state, consecutive_errors, inst: dict, enable_s1u: bool = False,
                  stage1_cache: dict | None = None, instances_subdir: str = "instances",
                  use_enumeration_stage1: bool = True,
                  use_misconception_principle: bool = ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT) -> dict:
    instance_id = inst["instance_id"]
    fixture = inst["fixture"]
    call_log: list = []
    t0 = time.time()

    # 委任_06: coverage_unionはE2E評価(fresh Stage 1)のため、reuse fixtureでも保存済みV4A出力を使わず新規実行する(legacyでは従来どおり)。
    if inst["stage1_mode"] == "reuse" and STAGE1_MODE != STAGE1_MODE_COVERAGE_UNION:
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
                 + (fixture.get("source_article_text") or "")
                 + (f"␟{STAGE1_MODE}:{STAGE1_ROUTES}" if STAGE1_MODE != STAGE1_MODE_LEGACY else "")
                 + (f"␟{STAGE1_R5_MODE}:{STAGE1_R3_REASONING}:{STAGE1_R5_REASONING}:{STAGE1_NEGATION_MODE}"
                    if (STAGE1_R5_MODE, STAGE1_R3_REASONING, STAGE1_R5_REASONING, STAGE1_NEGATION_MODE) != ("full", "high", "high", "legacy")
                    else "")).encode("utf-8")
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
            # 委任_06: 分岐は`stage1_fresh_dispatch`へ集約(既定legacy_v4aは従来の2経路をそのまま呼ぶ)。
            stage1_parsed = stage1_fresh_dispatch(
                client, state, consecutive_errors, call_log, f"{instance_id}_stage1", fixture,
                stage1_developer_message, use_enumeration_stage1)
            stage1_call_used = True
            # 委任_06 H1(fail-closed時): API失敗は再実行1回(coverage_unionは経路ごとにmodule内で再実行済み)。
            if STAGE1_FAIL_CLOSED and stage1_parsed.get("_stage1_api_failure"):
                stage1_parsed = h1_rerun_stage1(
                    stage1_parsed, lambda: stage1_fresh_dispatch(
                        client, state, consecutive_errors, call_log, f"{instance_id}_stage1_rerun", fixture,
                        stage1_developer_message, use_enumeration_stage1))
            # API失敗の結果は(fail-closed時)cacheへ入れない(同一入力の再利用でSTOPが握り潰されるのを避ける)。
            if cache_key is not None and not (STAGE1_FAIL_CLOSED and stage1_parsed.get("_stage1_api_failure")):
                stage1_cache[cache_key] = stage1_parsed

    # 委任_49 2-2(記録専用): Checker(Stage 1)が返した指摘の全件(MINORを含む)。後段へ渡すのは従来どおりMAJORのみ。
    raw_stage1_all = [raw_deviation_record(d) for d in (stage1_parsed.get("deviations") or [])]
    raw_rechecks: list = []
    severity_wobble_registry: dict = {}
    severity_wobble_records: list = []
    en_title_changes: list = []

    # 委任_06 H1(fail-closed): Stage 1 API失敗(再実行後も)はPASSへ抜けない。許可リスト`api_failure`でSTAGE4へ(後段は実行しない)。
    # 既定OFF(`STAGE1_FAIL_CLOSED`)では従来どおり(API失敗=deviations空のLEDGER_DEVIATIONが後段へ進む)。
    stage1_audit = stage1_parsed.get("stage1_coverage_audit")  # coverage_union時のみ(経路別候補・欠落ID・再実行・費用等)
    if STAGE1_FAIL_CLOSED and stage1_parsed.get("_stage1_api_failure"):
        r_stop = stage1_api_failure_stop_result(inst, call_log, t0, raw_stage1_all, fixture, stage1_call_used)
        if stage1_audit is not None:
            r_stop["stage1_coverage"] = stage1_audit
        save_json(f"{OUT_DIR}/{instances_subdir}/{instance_id}.json", r_stop)
        return r_stop

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
    # 委任_06 F3(`F3_PRECHECK_ALWAYS`、既定OFF): Stage 1が非検出(候補0)でも、決定論precheck floorの該当を確認してから早期PASS
    # (ACCEPTABLE_STAGE1 return)へ進む。該当があれば早期returnせず、下の通常ループ(precheck floor→BLOCKING→Rewrite)へ入る。
    f3_precheck_hits = None
    if F3_PRECHECK_ALWAYS and overall_status != "LEDGER_DEVIATION":
        f3_precheck_hits = len(build_precheck_floor_claims(fixture, set()))
    if overall_status != "LEDGER_DEVIATION" and not f3_precheck_hits:
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
            # 委任_49 作業2(記録専用)
            "switches": {"JA_MODE": JA_MODE, "VS_MATCH_EXT": VS_MATCH_EXT, "HANDOFF_MODE": HANDOFF_MODE,
                         **({"CHECKER_SPANS_MODE": CHECKER_SPANS_MODE} if CHECKER_SPANS_MODE != CHECKER_SPANS_MODE_LEGACY else {}),
                         **({"VS_EXPLAIN_SPLIT": True} if VS_EXPLAIN_SPLIT else {}),
                         **({"VS_SENTENCE_RESTORE": True} if VS_SENTENCE_RESTORE else {}),
                         **({"STAGE2_NORMAL_TWO_OF_TWO": True} if STAGE2_NORMAL_TWO_OF_TWO else {}),
                         **({"FLOOR_VERIFY_MODE": FLOOR_VERIFY_MODE} if FLOOR_VERIFY_MODE != FLOOR_VERIFY_MODE_OFF else {}),
                         **({"STAGE2_DOWNGRADE_VERIFY": True} if STAGE2_DOWNGRADE_VERIFY else {}),
                         **({"CAUSAL_FLOOR": True} if CAUSAL_FLOOR else {}),
                         **({"STAGE2_SECOND_OPINION": True} if STAGE2_SECOND_OPINION else {}),
                         **({"RECHECK_MERGE_UNRESOLVED": True} if RECHECK_MERGE_UNRESOLVED else {}),
                         **({"RECHECK_BEFORE_AFTER_PAIRS": True} if RECHECK_BEFORE_AFTER_PAIRS else {}),
                         **({"STRUCTURAL_ELEMENT_REWRITE": True} if STRUCTURAL_ELEMENT_REWRITE else {}),
                         **({"ACTOR_GUARD_MODE": ACTOR_GUARD_MODE} if ACTOR_GUARD_MODE != "legacy" else {}),
                         **({"STRUCTURAL_PAIRS_TO_RECHECK": True} if STRUCTURAL_PAIRS_TO_RECHECK else {})},
            "all_deviations_raw": {"stage1": raw_stage1_all, "rechecks": []},
            "residual_at_pass": compute_residual_at_pass(instance_id, "ACCEPTABLE_STAGE1", fixture["article_text"],
                                                         [], raw_stage1_all, []),
            "severity_wobble": [], "en_title_rewritten": False, "en_title_changes": [],
        }
        if stage1_audit is not None:  # 委任_06(記録専用)
            result["stage1_coverage"] = stage1_audit
        if stage1_parsed.get("stage1_reclassify") is not None:  # 委任_04(記録専用)
            result["stage1_reclassify"] = stage1_parsed["stage1_reclassify"]
        if f3_precheck_hits is not None:
            result["f3_precheck_always"] = {"precheck_floor_hits": f3_precheck_hits}
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
    if JA_MODE == JA_MODE_ENGLISH_ONLY:
        # 委任_49 作業4(設計書§5): 日本語側の処理を迂回する(`fixture["source_article_text"]`は変えない=
        # CheckerとStage 2へは元の日本語を渡し続ける。`working_fixture`は`current_ja_text`がNoneのとき
        # source_article_textを上書きしないため、元の日本語が維持される)。
        current_ja_text = None
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
        if (fixture.get("source_article_text") is not None and JA_MODE != JA_MODE_ENGLISH_ONLY) else []
    )

    stage1_deviations = [d for d in stage1_parsed.get("deviations", []) if d.get("severity") == "MAJOR"]
    cycle = 1
    # 委任_11: Opus#14後のFable評価の状態(全て新スイッチOFFなら未使用=legacy)
    allowlist_log: list = []            # I-2: STAGE4許可リスト判定の記録(許可・許可外の両方)
    switch_fired: dict = {}             # スイッチ別の発火回数(記録専用)
    t_used = False                      # T(最終手段)は1記事1回
    carry_blocking: list = []           # H-1: 書き換えられなかった(位置を取れなかった)BLOCKING。空でない間はPASSを返さない
    rewritten_regions: list = []        # I-1最小: 前cycleまでの置換範囲(置換後文字列+試行level)
    en_text_before_rewrite = current_en_text  # 委任_18: coverage Recheckのbefore(各cycleのRewrite直前で更新される)
    exit_check_done = False             # 委任_18: 出口3'-R全文は1記事1回
    exit_check_log: list = []
    reclassify_protected: list = []     # 委任_04 M2: 過去cycleの指摘文(出口3'-Rの再分類で同文候補を対象外にする保護)
    article_state_history: list = []    # A2: 過去の本文(原文・前cycleまで)
    pinned_blocking: dict = {}          # S-4: キー(span集合,fact_id)->BLOCKING確定済みのStage 2結果
    nonblocking_registry: dict = {}     # S-4: 一致した2-of-2非BLOCKINGの結果(再利用スイッチ用)
    pass_blocked_by_carry = 0
    unrewritten_blocking_pass = 0       # 事前基準: 書き換えられていないBLOCKINGによるPASS件数(0であること)

    def _allow(reason: str, ctx: dict, legacy: str | None = None) -> dict:
        d = stage4_allowlist_decision(reason, ctx)
        allowlist_log.append({"cycle": cycle, "decision": d, "legacy_reason": legacy})
        return d

    def _exit_gate(cyc_rec: dict) -> dict | None:
        """委任_18(RECHECK_MODE=coverage_union): Rewrite発生記事(本文が原文から変わった)がRESOLVED_*で出口へ向かう直前に、3'-R全文を1回行う。
        戻り値: None=そのまま出口 / {"action":"api_failure"}=fail-closed(許可リスト`api_failure`) / {"action":"reenter","deviations":[...]}=
        新規CANDIDATEを次cycleのStage 2(funnel)へ合流させる。1記事1回(`exit_check_done`)。"""
        nonlocal exit_check_done
        if RECHECK_MODE != RECHECK_MODE_COVERAGE_UNION or exit_check_done or current_en_text == fixture["article_text"]:
            return None
        exit_check_done = True
        r = run_exit_check_coverage(client, state, consecutive_errors, call_log, f"{instance_id}_exit", fixture, current_en_text,
                                    protected_claims=list(reclassify_protected))
        devs = [d for d in r["deviations"] if d.get("severity") == "MAJOR"]
        a_ = r["audit"]
        entry = {"cycle": cycle, "n_candidates": len(devs), "api_failure": bool(r["api_failure"]), "n_calls": a_.get("n_calls"),
                 "n_judged_units": a_.get("n_judged_units"), "total_cost_jpy": a_.get("total_cost_jpy"),
                 "missing_after_rerun": a_.get("missing_after_rerun")}
        if STAGE1_RECLASSIFY:
            entry["reclassify"] = reclassify_summary(a_.get("candidate_filter"))
        exit_check_log.append(entry)
        cyc_rec["exit_check"] = entry
        if r["api_failure"]:
            return {"action": "api_failure"}
        return {"action": "reenter", "deviations": devs} if devs else None

    while True:
        working_fixture = dict(fixture)
        working_fixture["article_text"] = current_en_text
        if current_ja_text is not None:
            working_fixture["source_article_text"] = current_ja_text
        judge_only = bool(STAGE4_ALLOWLIST and JUDGE_ONLY_CYCLE_AFTER_CAP and cycle > HARD_MAX_CYCLES)

        # 第二段階案(既定OFF): cycle 1のStage 2 batchへ、同fact_id兄弟箇所の決定論列挙を足す(Rewriteへは渡さない=Stage 2がBLOCKINGにした箇所だけ)
        if STAGE2_SIBLING_LOCATIONS_CYCLE1 and cycle == 1:
            _base = [dict(d, same_fact_id_locations=None) for d in stage1_deviations]
            _enum = deterministic_same_fact_id_location_fallback(_base, current_en_text)
            _seen = {(d.get("claim_in_article") or "").strip() for d in stage1_deviations}
            _added = []
            for e in _enum:
                for loc in (e.get("same_fact_id_locations") or []):
                    ls = (loc or "").strip()
                    if ls and ls not in _seen and ls in current_en_text:
                        nd = dict(e)
                        nd.pop("same_fact_id_locations", None)
                        nd["claim_in_article"] = ls
                        nd["detected_by_enumeration"] = True
                        nd["enumeration_source_claim"] = (e.get("claim_in_article") or "").strip()
                        _added.append(nd)
                        _seen.add(ls)
            if _added:
                stage1_deviations = list(stage1_deviations) + _added
                switch_fired["STAGE2_SIBLING_LOCATIONS_CYCLE1"] = switch_fired.get("STAGE2_SIBLING_LOCATIONS_CYCLE1", 0) + len(_added)

        existing_fact_ids = {(d.get("related_fact_id") or "") for d in stage1_deviations}
        precheck_claims = build_precheck_floor_claims(working_fixture, existing_fact_ids)

        llm_claims = [{"claim_text": d.get("claim_in_article", ""), "origin": d.get("origin"),
                       "related_fact_id": d.get("related_fact_id"), "dev": d, "detected_by": "stage1_llm"}
                      for d in stage1_deviations]

        # 委任_11 D(iii)(H-1): 前cycleで書き換えられなかった(位置を取れなかった)BLOCKINGを、Stage 2を通さずBLOCKINGのまま持ち越す。
        # 同fact_idのRecheck指摘があれば、その`claim_in_article`で位置を取り直す(Recheckは位置の再取得だけに使う)。
        carried_results: list = []
        if carry_blocking:
            for cr in carry_blocking:
                cfid = (cr["dev"].get("related_fact_id") or "").strip()
                new_dev = dict(cr["dev"])
                relocated = False
                if cfid:
                    for lc in list(llm_claims):
                        if (lc["related_fact_id"] or "").strip() == cfid:
                            new_dev["claim_in_article"] = lc["dev"].get("claim_in_article", new_dev.get("claim_in_article"))
                            llm_claims.remove(lc)
                            relocated = True
                            break
                carried_results.append({**cr, "dev": new_dev, "claim_text": new_dev.get("claim_in_article", ""),
                                        "carried_blocking": True, "carried_relocated": relocated})
            switch_fired["SPAN_FALLBACK_CHAIN.carry_injected"] = switch_fired.get("SPAN_FALLBACK_CHAIN.carry_injected", 0) + len(carried_results)
            carry_blocking = []
        # S-4(既定OFF): 一致した2-of-2非BLOCKING(span集合+fact_idの完全一致)の再利用。Stage 2 callを省く。
        reused_results: list = []
        if STAGE2_VERDICT_REUSE_NONBLOCKING and nonblocking_registry:
            _keep = []
            for lc in llm_claims:
                k_ = claim_materiality_key(lc["claim_text"], lc["related_fact_id"], current_en_text)
                if k_ is not None and k_ in nonblocking_registry:
                    reused_results.append({**nonblocking_registry[k_], "claim_text": lc["claim_text"], "dev": lc["dev"],
                                           "reused_nonblocking_verdict": True})
                    switch_fired["STAGE2_VERDICT_REUSE_NONBLOCKING"] = switch_fired.get("STAGE2_VERDICT_REUSE_NONBLOCKING", 0) + 1
                else:
                    _keep.append(lc)
            llm_claims = _keep
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
        # 委任_01(KPI-RECOVERY-REDESIGN-02) 作業2-3: 既定OFF(`STAGE2_NORMAL_TWO_OF_TWO`)。
        # 委任_03(Tier 1' S1、既定OFF`STAGE2_SECOND_OPINION`): Tier 0非該当のChecker MAJOR→Stage 2非BLOCKING全件に
        # 第2意見を取り、割れたらBLOCKING(毎cycle・Recheck由来にも同じ経路)。
        if STAGE2_SECOND_OPINION:
            stage2_results, stage2_downgrade_confirm_log = apply_stage2_second_opinion(
                client, state, consecutive_errors, call_log, f"{instance_id}_c{cycle}", working_fixture,
                stage2_results, instance_id, cycle)
        else:
            stage2_downgrade_confirm_log = None
        if STAGE2_NORMAL_TWO_OF_TWO:
            stage2_results, stage2_two_of_two_log = apply_stage2_two_of_two(
                client, state, consecutive_errors, call_log, f"{instance_id}_c{cycle}", working_fixture,
                stage2_results, inst)
        else:
            stage2_two_of_two_log = []

        # S-4 BLOCKING固定: 本文が変わっていない箇所(正規化span集合+fact_id)で過去にBLOCKING確定したものは、再判定の揺れで覆さない
        # (判定だけのcycle[G]でも同じ。S1を通った後の結果にだけ適用する=Stage 2単独の非BLOCKINGで閉じない)。
        if MATERIALITY_BLOCKING_PIN and HANDOFF_MODE == HANDOFF_MODE_VIOLATION_SPAN:
            for i_, r_ in enumerate(stage2_results):
                if r_["materiality"] == "BLOCKING":
                    continue
                k_ = claim_materiality_key(r_.get("claim_text", ""), (r_["dev"].get("related_fact_id") or ""), current_en_text)
                if k_ is not None and k_ in pinned_blocking:
                    pr_ = pinned_blocking[k_]
                    stage2_results[i_] = {**r_, "materiality": "BLOCKING", "basis": "materiality_pinned",
                                          "floor_reason": "materiality_pinned", "pinned_from_cycle": pr_["_cycle"],
                                          "rewrite_kind": pr_.get("rewrite_kind") or r_.get("rewrite_kind"),
                                          "rewrite_hint": pr_.get("rewrite_hint") or r_.get("rewrite_hint"),
                                          "pinned_original_materiality": r_["materiality"]}
                    switch_fired["MATERIALITY_BLOCKING_PIN"] = switch_fired.get("MATERIALITY_BLOCKING_PIN", 0) + 1
        if STAGE2_VERDICT_REUSE_NONBLOCKING and HANDOFF_MODE == HANDOFF_MODE_VIOLATION_SPAN:
            for r_ in stage2_results:
                so_ = r_.get("second_opinion") or {}
                if r_["materiality"] != "BLOCKING" and so_.get("confirmed_downgrade") and not r_.get("floor_reason"):
                    k_ = claim_materiality_key(r_.get("claim_text", ""), (r_["dev"].get("related_fact_id") or ""), current_en_text)
                    if k_ is not None:
                        nonblocking_registry[k_] = {kk: vv for kk, vv in r_.items() if kk not in ("claim_text", "dev")}
        stage2_results = stage2_results + carried_results + reused_results

        blocking_claims = [c for c in stage2_results if c["materiality"] == "BLOCKING"]
        non_blocking_claims = [c for c in stage2_results if c["materiality"] != "BLOCKING"]
        # 委任_42 仕様(7): cycle開始時点の本文で、各BLOCKING claimの範囲を確定して
        # 記録する(周回間の同一判定・Recheckの`prior_issues`を、生の引用符付き
        # 文字列ではなく正規化後の確定範囲へ揃えるため。Stage 2へ渡す`claim_text`
        # 表示は変更しない)。確定不能の場合は従来どおり生のclaim文字列を使う。
        for c in blocking_claims:
            annotate_claim_span_identity(c, current_en_text, current_ja_text)
            if MATERIALITY_BLOCKING_PIN and HANDOFF_MODE == HANDOFF_MODE_VIOLATION_SPAN:
                _sr = c.get("span_resolution_cycle_start") or {}
                if _sr.get("status") == "resolved" and _sr.get("ranges"):
                    pinned_blocking[_span_key(_sr["ranges"], c["dev"].get("related_fact_id") or "")] = {
                        "rewrite_kind": c.get("rewrite_kind"), "rewrite_hint": c.get("rewrite_hint"), "_cycle": cycle}

        cycle_record = {
            **({"judge_only_cycle": True} if judge_only else {}),
            "cycle": cycle, "stage2_results": stage2_results,
            "blocking_count": len(blocking_claims), "non_blocking_count": len(non_blocking_claims),
            "stage2_two_of_two_log": stage2_two_of_two_log,
            **({"stage2_downgrade_confirm_log": stage2_downgrade_confirm_log}
               if stage2_downgrade_confirm_log is not None else {}),
        }
        # 委任_49 2-3(記録専用): 重大度の揺れ(同じ確定範囲・同じfact_idの最終判定が周回間で変わった)
        _wob = _wobble_observe(severity_wobble_registry, severity_wobble_records, cycle, stage2_results,
                               current_en_text)
        if _wob:
            cycle_record["severity_wobble"] = _wob

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
            g_ = _exit_gate(cycle_record) if final_state != "STAGE4_ESCALATION" else None  # 委任_18
            if g_ is not None:
                if g_["action"] == "api_failure":
                    final_state, stage4_reason = "STAGE4_ESCALATION", _allow("api_failure", {})["reason"]
                else:
                    stage1_deviations, final_state, stage4_reason = g_["deviations"], None, None
                    cycle += 1
                    continue
            break

        _newroute = bool(STAGE4_ALLOWLIST and HANDOFF_MODE == HANDOFF_MODE_VIOLATION_SPAN)
        # 委任_11 T後: 最終手段(削除)の後にStage 2(+S1)がBLOCKINGを確定したら、追わずに許可リスト内の出口へ(Fable評価9)
        if _newroute and LAST_RESORT_DELETE and t_used:
            d_ = _allow("post_T_new_blocking", {"funnel_passed": True})
            final_state, stage4_reason = "STAGE4_ESCALATION", d_["reason"]
            cycles_log.append(cycle_record)
            break
        # 委任_11 D(iii): 前cycleで位置を取り直そうとして取れなかった持ち越しBLOCKINGだけが残る(再取得されず・他に処理対象なし)
        # なら、これ以上同じ文字列で再試行しない(Recheckで位置の再取得は既に1回試みた)。上限後に位置特定不能のBLOCKINGとして許可リストの出口へ。
        if _newroute and SPAN_FALLBACK_CHAIN and carried_results and all(
                c.get("carried_blocking") and not c.get("carried_relocated") and
                (c.get("span_resolution_cycle_start") or {}).get("status") != "resolved" for c in blocking_claims):
            d_ = _allow("blocking_confirmed_unlocatable_after_cap", {"funnel_passed": True})
            final_state, stage4_reason = "STAGE4_ESCALATION", d_["reason"]
            cycle_record["unlocatable_carried_claim_ids"] = sorted({claim_identity(c["dev"]) for c in blocking_claims})
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
        if cycle > 1 and not judge_only:
            for c in blocking_claims:
                _span_txt = c.get("claim_span_text")
                m = find_matching_prior_record(
                    c["dev"], prior_blocking_records,
                    claim_norm=(normalize_claim_text(_span_txt) if _span_txt else None))
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
        if exhausted_matched_records and _newroute:
            # 委任_11 I-2: `same_claim_fact_id_reblocked`は出口として廃止(許可リスト外)。記録して、④段落まで試行済みの箇所として
            # Rewriteへ進め(ladderに残りlevelなし)、枯渇したらT/構造要素の出口(許可リスト内)へ。
            _allow("same_claim_fact_id_reblocked", {"funnel_passed": True}, legacy="same_claim_fact_id_reblocked")
            cycle_record["repeat_claim_ids"] = sorted({m["identity"] for m in exhausted_matched_records})
            cycle_record["same_claim_reblocked_rerouted_to_ladder_exhaust"] = True
            for m in exhausted_matched_records:
                claim = matched_claim_by_identity.get(m["identity"])
                if claim is not None:
                    claim["location_prior_levels"] = sorted(set(claim.get("location_prior_levels") or []) | {"4_paragraph"})
            exhausted_matched_records = []
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

        cap_terminal_T = False
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
                not extra_cycle_granted and cycle == MAX_CYCLES + 1 and not judge_only
                and (progress_shown or same_fact_id_new_location)
            )
            if allow_extra_cycle:
                extra_cycle_granted = True
                cycle_record["extra_cycle_granted"] = True
                if same_fact_id_new_location and not progress_shown:
                    cycle_record["extra_cycle_reason"] = "same_fact_id_new_location(委任_18 2-3b)"
            elif _newroute and JUDGE_ONLY_CYCLE_AFTER_CAP:
                # 委任_11 G/T(Fable評価8/9): 上限=Rewrite回数の上限であって判定回数の上限ではない。この周のStage 2+S1(Tier 0・BLOCKING固定を
                # 含む経路)が既にBLOCKINGを確定している。`cycle_limit_exhausted`は出口として廃止(許可リスト外)し、
                # 位置を特定できなければ`blocking_confirmed_unlocatable_after_cap`、できればT(最終手段)へ。
                _allow("cycle_limit_exhausted", {"funnel_passed": True}, legacy="cycle_limit_exhausted")
                _unloc = [c for c in blocking_claims
                          if (c.get("span_resolution_cycle_start") or {}).get("status") != "resolved"]
                if _unloc:
                    d_ = _allow("blocking_confirmed_unlocatable_after_cap", {"funnel_passed": True})
                    final_state, stage4_reason = "STAGE4_ESCALATION", d_["reason"]
                    cycle_record["unlocatable_claim_ids"] = sorted({claim_identity(c["dev"]) for c in _unloc})
                    cycles_log.append(cycle_record)
                    break
                if not LAST_RESORT_DELETE or t_used:
                    d_ = _allow("blocking_structural_after_ladder", {"funnel_passed": True})
                    final_state, stage4_reason = "STAGE4_ESCALATION", d_["reason"]
                    cycle_record["structural_verified"] = structural_verified_record(
                        [], "cap_terminal_no_rewrite_this_cycle_T_already_used_or_disabled")
                    cycles_log.append(cycle_record)
                    break
                cap_terminal_T = True
                cycle_record["cap_terminal_last_resort"] = True
                for c in blocking_claims:
                    c["last_resort_delete"] = True
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
                "claim_text_norm": (normalize_claim_text(c["claim_span_text"]) if c.get("claim_span_text")
                                    else normalize_claim_text(c["dev"].get("claim_in_article") or "")),
                # 委任_24 A-2(§6-13): このRewrite試行で④段落水準まで既に
                # 試行済みか(escalate_to_paragraphが今cycleで付与済みか)を
                # 記録する。次cycleで同一claimが再発した際、matched_records
                # 判定がこのフラグを見て「ラダー昇段しきった上での再発
                # (直ちにSTAGE4)」か「まだ昇段の余地がある再発(ループ継続)」
                # かを区別する。
                "escalated_to_paragraph": bool(c.get("escalate_to_paragraph")),
            })
        prev_cycle_blocking_count = len(blocking_claims)

        # 委任_11 B′(Fable評価4): 同一箇所(前cycleの置換範囲と1文字以上重なる)は、前levelより上位から昇段する(位置のみ、fact_idは問わない)
        if LADDER_LOCATION_CARRY and HANDOFF_MODE == HANDOFF_MODE_VIOLATION_SPAN and rewritten_regions:
            _lc_rec = {}
            for c in blocking_claims:
                lv_, n_ = location_prior_levels(rewritten_regions, c, current_en_text)
                if lv_:
                    c["location_prior_levels"] = sorted(set(c.get("location_prior_levels") or []) | set(lv_))
                    _lc_rec[claim_identity(c["dev"])] = c["location_prior_levels"]
            if _lc_rec:
                cycle_record["location_carry"] = _lc_rec
                switch_fired["LADDER_LOCATION_CARRY"] = switch_fired.get("LADDER_LOCATION_CARRY", 0) + len(_lc_rec)

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
            cycle_replaced_units: list = []
            cycle_claim_info: dict = {}
            for c in claims_list:
                c2 = dict(c)
                c2["extra_constraint"] = extra_constraint
                # 委任_49 2-4(記録専用): carry-forward発動時に先行指摘のissueを比較するため
                c2["cycle_claim_info"] = dict(cycle_claim_info)
                # 委任_42(rep22 T3の是正): 同一cycle内で先行claimが書き換えた範囲を後続claimへ
                # 渡す(同じ文を指す複数claimの後続が、書き換え済みで文字列が消えたことを
                # 確定不能[Stage 4]と誤認しないため)。
                c2["cycle_start_en_text"] = en_text
                c2["cycle_start_ja_text"] = ja_text
                c2["cycle_replaced_units"] = list(cycle_replaced_units)
                if REWRITE_REVERT_GUARD and article_state_history:
                    c2["article_state_history"] = list(article_state_history)  # A2: 過去状態(原文・前cycleまでの本文)
                r = run_stage3_for_claim(
                    client, state, consecutive_errors, call_log,
                    f"{instance_id}_c{cycle}_{claim_identity(c['dev'])[:20]}{label_suffix}",
                    working_fixture, en_out, ja_out, c2)
                en_out = r["en_text"]
                if r["ja_text"] is not None:
                    ja_out = r["ja_text"]
                cycle_replaced_units.extend(collect_replaced_units(r, claim_identity(c["dev"])))
                cycle_claim_info[claim_identity(c["dev"])] = {
                    "issue": (c["dev"].get("issue") or ""), "related_fact_id": (c["dev"].get("related_fact_id") or ""),
                    "true_flags": _dev_true_flags(c["dev"])}
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
                                     "ladder_exhausted_without_full_rewrite", False),
                                 # 委任_42 仕様(9): 受け渡しの記録(Checker文字列/確定範囲/
                                 # 照合レベル/確定不能理由/水準別の対象と結果/before・after/
                                 # guard結果/JA暫定経路)。次回以降の集計を記録値でできるように。
                                 "span_unverified": r.get("span_unverified", False),
                                 "handoff": r.get("handoff")})
                _sp = (r.get("handoff") or {}).get("structural_pair")
                if _sp:  # 委任_08: 構造要素の書き換えは、水準に関わらずbefore/after全体の対を持つ(`structural`印付き)
                    pairs.append({"before": _sp["before"], "after": _sp["after"], "structural": True})
                else:
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
        carry_new: list = []
        if unlocatable_records and _newroute and SPAN_FALLBACK_CHAIN:
            # 委任_11 D(iii)/I-2: `violation_span_unverified`/`target_not_locatable`は出口として廃止(許可リスト外)。位置を取れなかった
            # BLOCKINGはRewriteせずcarry listへ保持し(PASS禁止、H-1)、全文Recheckで位置を再取得させる。取れなければ上限後に
            # `blocking_confirmed_unlocatable_after_cap`(許可リスト内)。
            for r_ in unlocatable_records:
                _allow("violation_span_unverified" if r_.get("span_unverified") else "target_not_locatable",
                       {"funnel_passed": True},
                       legacy="violation_span_unverified" if r_.get("span_unverified") else "target_not_locatable")
            _ids = {r_["claim_identity"] for r_ in unlocatable_records}
            for c in blocking_claims:
                if claim_identity(c["dev"]) in _ids:
                    carry_new.append({k_: v_ for k_, v_ in c.items() if k_ not in ("last_resort_delete",)})
            cycle_record["carry_blocking_unlocatable_ids"] = sorted(_ids)
            cycle_record["violation_span_unverified_claim_ids"] = sorted(
                {r["claim_identity"] for r in unlocatable_records if r.get("span_unverified")})
            switch_fired["SPAN_FALLBACK_CHAIN.carry_new"] = switch_fired.get("SPAN_FALLBACK_CHAIN.carry_new", 0) + len(carry_new)
            unlocatable_records = []
        if unlocatable_records:
            final_state = "STAGE4_ESCALATION"
            # 委任_42: 新方式で範囲を確定できなかった指摘(0箇所/複数箇所/説明文混在)は
            # 新reason`violation_span_unverified`(類似度等へ落とさずfail-closed)。
            span_unverified_records = [r for r in unlocatable_records if r.get("span_unverified")]
            stage4_reason = "violation_span_unverified" if span_unverified_records else "target_not_locatable"
            if span_unverified_records:
                cycle_record["violation_span_unverified_claim_ids"] = sorted(
                    {r["claim_identity"] for r in span_unverified_records})
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
        if ladder_exhausted_records and _newroute:
            # 委任_11 I-2/T: `ladder_exhausted_without_full_rewrite`は出口として廃止(許可リスト外)。API失敗だけで枯渇したなら`api_failure`、
            # 既にTを試みた/構造要素/T無効なら`blocking_structural_after_ladder`、それ以外はT(構造要素以外の0_delete+全文Recheck、1記事1回)。
            _ex_ids = {r_["claim_identity"] for r_ in ladder_exhausted_records}
            _api_only = all(
                (r_.get("handoff") or {}).get("level_attempts") and all(
                    a_.get("result") in ("api_failure", "parse_failure") for a_ in (r_.get("handoff") or {}).get("level_attempts", []))
                for r_ in ladder_exhausted_records)
            _allow("ladder_exhausted_without_full_rewrite", {"funnel_passed": True}, legacy="ladder_exhausted_without_full_rewrite")
            _already_T = any(c.get("last_resort_delete") for c in blocking_claims
                             if claim_identity(c["dev"]) in _ex_ids)
            _struct = any(((r_.get("handoff") or {}).get("structural_blocking")) for r_ in ladder_exhausted_records)
            if _api_only:
                d_ = _allow("api_failure", {})
                _stop = d_["reason"]
            elif _already_T or _struct or t_used or not LAST_RESORT_DELETE:
                d_ = _allow("blocking_structural_after_ladder", {"funnel_passed": True})
                _stop = d_["reason"]
                cycle_record["structural_verified"] = structural_verified_record(
                    ladder_exhausted_records, "ladder_exhausted_already_T_or_struct_or_T_disabled")
            else:
                _stop = None
            if _stop:
                final_state, stage4_reason = "STAGE4_ESCALATION", _stop
                cycle_record["rewrite_records"] = rewrite_records
                cycle_record["ladder_exhausted_claim_ids"] = sorted(_ex_ids)
                cycles_log.append(cycle_record)
                break
            # T: 枯渇したclaimだけを構造要素以外の決定論削除へ(他のclaimの結果は保持)
            # 委任_B(OPEN-233-CHECKER-SELECTIVITY-RECLASSIFY-01): 対象はrecord単位(index)で選ぶ。同fact_idで同cycleにRewrite成功済み/
            # carry-forward済みのclaimは再対象化しない(`t_skipped_reason=already_rewritten_in_cycle`)。
            _sel = select_last_resort_targets(blocking_claims, rewrite_records)
            _t_idx = _sel["indices"]
            t_claims = [blocking_claims[i_] for i_ in _t_idx]
            cycle_record["t_target_selection"] = {"indices": _t_idx, "skipped": _sel["skipped"], "aligned": _sel["aligned"]}
            for c in t_claims:
                c["last_resort_delete"] = True
            _pre_t_records = list(rewrite_records)
            _t_en, _t_ja, t_records, t_pairs = _run_stage3_cycle(
                t_claims, current_en_text, current_ja_text, base_constraint, label_suffix="_T")
            # 委任_B: Human Reviewへ送る前に失敗の種類を確認する(本文に残る未解消 / 非構造の位置特定失敗 / 既に書き換え済み)。
            _t_cls = classify_last_resort_failures(t_claims, t_records, _pre_t_records, en_text_before_rewrite,
                                                   ja_text_before_rewrite, current_en_text, current_ja_text)
            cycle_record["last_resort_failure_classification"] = _t_cls
            _t_covered = {x_["index"] for x_ in _t_cls if x_["kind"] == "covered_by_earlier_rewrite"}
            for i_ in _t_covered:  # 既に書き換え済み=解消扱い(failとして数えない)。記録は「先行Rewriteで被覆」へ
                t_records[i_] = dict(t_records[i_], method="covered_by_earlier_rewrite_in_cycle(T)", target_not_locatable=False,
                                     span_unverified=False, t_covered_by_earlier_rewrite=True)
            _t_loc_fail = [x_ for x_ in _t_cls if x_["kind"] == "located_guard_failed"]
            _t_unloc = [x_ for x_ in _t_cls if x_["kind"] == "unlocatable_not_covered"]
            if _t_loc_fail or _t_unloc:
                if _t_loc_fail:
                    # 本文に残る未解消claimでT削除のguardも通らない=最終手段も尽きた(fail-closed、従来どおり)
                    d_ = _allow("blocking_structural_after_ladder", {"funnel_passed": True})
                    final_state, stage4_reason = "STAGE4_ESCALATION", d_["reason"]
                    cycle_record["structural_verified"] = structural_verified_record(rewrite_records + t_records, "T_located_guard_failed")
                else:
                    # 委任_B3(Fable判断、Opus R2): 非構造の位置特定失敗(先行Rewriteにも含まれず本文に残る可能性がある)を「構造上修正不能」と
                    # 呼ばない。H-1 carryは次cycleでBLOCKING注入→post_T_new_blocking STAGE4に必ず落ちるだけで費用増のためcarryせず、
                    # SPAN_FALLBACK_CHAINの有効/無効にかかわらずその場でfail-closed(許可リスト内`blocking_confirmed_unlocatable_after_cap`、
                    # 許可リスト・Human Review基準は不変)。区別は記録のみ(sub_reason / structural_verified=False)。
                    d_ = _allow("blocking_confirmed_unlocatable_after_cap", {"funnel_passed": True})
                    final_state, stage4_reason = "STAGE4_ESCALATION", d_["reason"]
                    cycle_record["stage4_sub_reason"] = "t_target_unlocatable_nonstructural"
                    cycle_record["structural_verified"] = {"verified": False, "reason": "t_target_unlocatable_nonstructural",
                                                           "details": []}
                cycle_record["rewrite_records"] = rewrite_records + t_records
                cycle_record["ladder_exhausted_claim_ids"] = sorted(_ex_ids)
                cycle_record["last_resort_delete_failed"] = True
                cycles_log.append(cycle_record)
                break
            # 削除を現行本文へ反映(_run_stage3_cycleは各claimの結果を連鎖させて返す)
            current_en_text, current_ja_text = _t_en, _t_ja
            t_used = True
            switch_fired["LAST_RESORT_DELETE"] = switch_fired.get("LAST_RESORT_DELETE", 0) + len(t_claims)
            cycle_record["last_resort_delete_applied"] = sorted(_ex_ids)
            _t_pos = {i_: k_ for k_, i_ in enumerate(_t_idx)}
            new_records, new_pairs = [], []
            for i_, (r_, p_) in enumerate(zip(rewrite_records, before_after_pairs)):
                if i_ in _t_pos:
                    new_records.append(t_records[_t_pos[i_]])
                    new_pairs.append(t_pairs[_t_pos[i_]])
                else:
                    new_records.append(r_)
                    new_pairs.append(p_)
            rewrite_records, before_after_pairs = new_records, new_pairs
        if ladder_exhausted_records and not _newroute:
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
        if cap_terminal_T:
            t_used = True
            switch_fired["LAST_RESORT_DELETE"] = switch_fired.get("LAST_RESORT_DELETE", 0) + len(blocking_claims)
        # 委任_11: `escalated_to_paragraph`を「実際に4_paragraphを試行したか」(試行level一覧)へ是正し、置換範囲(I-1最小)・過去本文(A2)を更新する
        if LADDER_LOCATION_CARRY or REWRITE_REVERT_GUARD:
            _base_i = len(prior_blocking_records) - len(blocking_claims)
            for i_, (c_, r_) in enumerate(zip(blocking_claims, rewrite_records)):
                if _base_i + i_ >= 0:
                    _lv_att = list(((r_.get("handoff") or {}).get("levels_attempted")) or [])
                    prior_blocking_records[_base_i + i_]["levels_attempted"] = _lv_att
                    if LADDER_LOCATION_CARRY:
                        prior_blocking_records[_base_i + i_]["escalated_to_paragraph"] = "4_paragraph" in _lv_att
            if current_en_text != en_text_before_rewrite:
                rewritten_regions = update_regions_after_rewrite(rewritten_regions, en_text_before_rewrite,
                                                                 rewrite_records, cycle)
                article_state_history.append(en_text_before_rewrite)
        # 委任_49 2-5(記録専用): 英語の見出し(`# `行)が書き換えられたら前後を記録
        _t_before, _t_after = _en_title_line(en_text_before_rewrite), _en_title_line(current_en_text)
        cycle_record["en_title_rewritten"] = bool(_t_before != _t_after)
        if _t_before != _t_after:
            cycle_record["en_title_before"], cycle_record["en_title_after"] = _t_before, _t_after
            en_title_changes.append({"cycle": cycle, "before": _t_before, "after": _t_after})
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
            if _newroute:
                # 委任_11 I-2: 構造要素(title/hook/In one line)を空・極端短縮にする書き換え=構造要素のladder枯渇として許可リスト内の出口へ
                # 委任_12(Fable照合1): degenerateを許可名へ写像しない。構造要素∧ladder実試行済みを検証できたときだけ
                # `blocking_structural_after_ladder`(通常はladder内で昇段済み=ここへは来ない防御経路)。検証できなければ許可リスト外として記録のまま。
                _ver = structural_ladder_exhausted_verified(rewrite_records)
                cycle_record["degenerate_structural_verification"] = _ver
                if _ver["verified"]:
                    cycle_record["structural_verified"] = structural_verified_record(rewrite_records, "degenerate_rewrite")
                    d_ = _allow("blocking_structural_after_ladder", {"funnel_passed": True})
                else:
                    d_ = _allow("degenerate_rewrite_output", {"funnel_passed": True}, legacy="degenerate_rewrite_output")
                stage4_reason = d_["reason"]
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
        if carry_new:  # 委任_11 D(iii): 位置を取れなかったBLOCKINGがある周は、局所QAで閉じず必ず全文Recheck(位置の再取得)
            recheck_required = True
            recheck_required_reasons = recheck_required_reasons + ["carry_blocking_unlocated_relocate_via_recheck"]
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
                _record_carry_forward_recheck(rewrite_records, None, "local_qa_fastpath_no_full_recheck")
                cycles_log.append(cycle_record)
                final_state = "RESOLVED_REWRITE"
                g_ = _exit_gate(cycle_record)  # 委任_18
                if g_ is not None:
                    if g_["action"] == "api_failure":
                        final_state, stage4_reason = "STAGE4_ESCALATION", _allow("api_failure", {})["reason"]
                    else:
                        stage1_deviations, final_state, stage4_reason = g_["deviations"], None, None
                        cycle += 1
                        continue
                break
        else:
            cycle_record["local_qa_fastpath_attempted"] = False

        # Recheck(全文、prior_issuesあり、A1。局所QA fastpathが不成立
        # [未該当、または局所QAが問題を検出]の場合のみ到達する、既存挙動
        # は無変更)
        # 委任_01(KPI-RECOVERY-REDESIGN-02) 作業2-1(不具合是正): `claim_in_article`は、Rewrite前の
        # span文ではなく現行本文(Rewrite後)の置換後の文を渡す。特定できなければ従来の元text
        # (`prior_issue_text_source`=original_text)。Checker Prompt・Schemaは不変。
        _rec_by_ident = {r_["claim_identity"]: r_ for r_ in rewrite_records}
        _all_units = [u_ for r_ in rewrite_records
                      for u_ in collect_replaced_units(r_, r_["claim_identity"])]
        prior_issues = []
        prior_issue_text_sources = []
        for c in blocking_claims:
            _orig = c.get("claim_span_text") or c["claim_text"]  # 委任_42 仕様(7): 新方式では確定範囲
            _txt, _src = resolve_prior_issue_text(_orig, _rec_by_ident.get(claim_identity(c["dev"])),
                                                  _all_units, current_en_text, current_ja_text)
            prior_issue_text_sources.append(_src)
            prior_issues.append({"fact_id": c["dev"].get("related_fact_id", ""),
                                 "claim_in_article": _txt,
                                 "issue": c["dev"].get("issue", ""),
                                 "explanation": c["dev"].get("explanation", "")})
        cycle_record["prior_issue_text_sources"] = prior_issue_text_sources
        reclassify_protected.extend(pi_["claim_in_article"] for pi_ in prior_issues if pi_.get("claim_in_article"))
        recheck_fixture = dict(working_fixture)
        recheck_fixture["article_text"] = current_en_text
        if current_ja_text is not None:
            recheck_fixture["source_article_text"] = current_ja_text
        if RECHECK_MODE == RECHECK_MODE_COVERAGE_UNION:  # 委任_18: 新Stage 1仕様のRecheck(変更単位+前後1単位、既定legacy_v4a=従来)
            recheck_parsed = run_recheck_coverage(client, state, consecutive_errors, call_log,
                                                  f"{instance_id}_c{cycle}_recheck", recheck_fixture, current_en_text,
                                                  prior_issues, en_text_before_rewrite)
            _ra = recheck_parsed.get("recheck_coverage_audit") or {}
            cycle_record["recheck_coverage"] = {k: _ra.get(k) for k in (
                "scope_ids", "changed_ids", "n_scope", "n_judged_units", "n_union_candidates", "n_calls", "total_cost_jpy",
                "n_prior_claim_hits", "missing_after_rerun")}
            cycle_record["recheck_coverage"]["api_failure"] = bool(recheck_parsed.get("_recheck_api_failure"))
            if STAGE1_RECLASSIFY:
                cycle_record["recheck_coverage"]["reclassify"] = reclassify_summary(_ra.get("candidate_filter"))
        else:
            recheck_parsed = run_recheck(client, state, consecutive_errors, call_log,
                                          f"{instance_id}_c{cycle}_recheck", recheck_fixture, current_en_text,
                                          prior_issues, before_after_pairs=before_after_pairs)
        if RECHECK_BEFORE_AFTER_PAIRS:
            cycle_record["recheck_before_after_pairs_n"] = len(
                [p_ for p_ in before_after_pairs if p_.get("before") and p_.get("after") is not None])
        elif STRUCTURAL_PAIRS_TO_RECHECK:
            cycle_record["recheck_structural_pairs_n"] = len(
                [p_ for p_ in before_after_pairs if p_.get("structural") and p_.get("before") and p_.get("after") is not None])
        # JA側も別途Recheck(paired rewriteが使われていた場合のみ、JA本文の
        # Ledger整合を独立に確認する。§5-4の「JA側1call+EN側1call」に対応)
        ja_recheck_parsed = None
        if current_ja_text is not None and any(rr["mechanism"].startswith("paired") for rr in rewrite_records):
            ja_recheck_parsed = run_recheck(client, state, consecutive_errors, call_log,
                                             f"{instance_id}_c{cycle}_ja_recheck", recheck_fixture,
                                             current_ja_text, prior_issues)

        # 委任_49 2-2/2-4(記録専用): Recheckが返した指摘の全件(MINORを含む)と、carry-forwardされた
        # claimがこのRecheckで解消扱いになったか
        raw_rechecks.append({
            "cycle": cycle,
            "deviations": [raw_deviation_record(d) for d in (recheck_parsed.get("deviations") or [])],
            "ja_deviations": ([raw_deviation_record(d) for d in (ja_recheck_parsed.get("deviations") or [])]
                              if ja_recheck_parsed is not None else None)})
        _record_carry_forward_recheck(rewrite_records, recheck_parsed.get("prior_issues_resolved"),
                                      "full_recheck")
        cycle_record["recheck_overall_status"] = recheck_parsed.get("overall_status")
        cycle_record["recheck_all_prior_issues_resolved"] = recheck_parsed.get("all_prior_issues_resolved")
        # 委任_05(記録専用、合否・分岐には使わない): neg3 `unconfirmed_after_reverify`のRCA用に、Recheckの
        # `prior_issues_resolved`(Checkerの項目別の解消判定・説明)と、渡した`prior_issues`の件数を残す(従来は未記録)。
        cycle_record["recheck_prior_issues_resolved"] = recheck_parsed.get("prior_issues_resolved")
        cycle_record["recheck_prior_issues_resolved_by_index"] = recheck_parsed.get("prior_issues_resolved_by_index")  # 委任_07
        cycle_record["recheck_prior_issues_sent_count"] = len(prior_issues)
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
        confirm_parsed = None
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
            # 委任_05(記録専用): 再確認が返した指摘(MINORを含む全件)と項目別の解消判定(従来は未記録)
            cycle_record["recheck_confirm_deviations"] = [
                raw_deviation_record(d_) for d_ in (confirm_parsed.get("deviations") or [])]
            cycle_record["recheck_confirm_prior_issues_resolved"] = confirm_parsed.get("prior_issues_resolved")
            if (confirm_parsed.get("overall_status") == "LEDGER_COMPLIANT"
                    and confirm_parsed.get("all_prior_issues_resolved")):
                en_ok = True
                cycle_record["recheck_reconfirmed"] = True
            else:
                cycle_record["recheck_reconfirmed"] = False

        cycles_log.append(cycle_record)

        carry_blocking = list(carry_new)  # 次cycleへ持ち越す(空でない間はPASSを返さない)
        if en_ok and ja_ok and carry_new:
            # 委任_11 H-1(Opus#14): Stage 2がBLOCKINGと確定し、書き換えられなかった箇所を、Recheck1回の「解消/準拠」だけでPASSさせない
            pass_blocked_by_carry += 1
            cycle_record["pass_blocked_by_carry_blocking"] = True
            en_ok = False
        if en_ok and ja_ok:
            final_state = "RESOLVED_REWRITE"
            g_ = _exit_gate(cycle_record)  # 委任_18
            if g_ is not None:
                if g_["action"] == "api_failure":
                    final_state, stage4_reason = "STAGE4_ESCALATION", _allow("api_failure", {})["reason"]
                else:
                    stage1_deviations, final_state, stage4_reason = g_["deviations"], None, None
                    cycle += 1
                    continue
            break

        if cycle_record.get("recheck_reconfirmed") is False and not RECHECK_MERGE_UNRESOLVED and not _newroute:
            # 再確認でも解消未確認(自己矛盾が解消しない) -> 次cycleの空
            # deviationsによる静かな降格を許さずfail-closedでSTAGE4
            # (旧挙動。委任_06 N1′ `RECHECK_MERGE_UNRESOLVED`ON時はこの経路を使わず、下で次cycleのStage 2へ合流させる)
            final_state = "STAGE4_ESCALATION"
            stage4_reason = "unconfirmed_after_reverify"
            break

        # 未解消 -> 次cycleのStage1 deviationsをRecheck結果から再構築
        stage1_deviations = [d for d in recheck_parsed.get("deviations", []) if d.get("severity") == "MAJOR"]
        if RECHECK_MERGE_UNRESOLVED or _newroute:
            if _newroute and not RECHECK_MERGE_UNRESOLVED and cycle_record.get("recheck_reconfirmed") is False:
                # 委任_11 I-2: `unconfirmed_after_reverify`は出口として廃止(許可リスト外)。次cycleのStage 2(funnel)へ合流させる
                _allow("unconfirmed_after_reverify", {"funnel_passed": False}, legacy="unconfirmed_after_reverify")
            # 委任_06 N1′: 未解消のprior issueは必ず次cycleのStage 2を通す(純関数`normalize_recheck_outcome`)
            _norm = normalize_recheck_outcome(recheck_parsed, confirm_parsed, blocking_claims, prior_issues)
            cycle_record["recheck_merge"] = {
                "decision": _norm["decision"], "source": _norm["source"], "merged_from": _norm["merged_from"],
                "n_merged": len(_norm["deviations"]), "n_dedup_dropped": _norm["n_dedup_dropped"],
                "reverify_deviation_without_major": _norm["reverify_deviation_without_major"],
                "merged_claims": [{"fact_id": d_.get("related_fact_id"), "claim": d_.get("claim_in_article"),
                                   "label": lb_} for d_, lb_ in zip(_norm["deviations"], _norm["merged_from"])]}
            if _norm["reverify_deviation_without_major"]:
                cycle_record["reverify_deviation_without_major"] = True
            if _norm["decision"] == RECHECK_DECISION_NEXT_CYCLE:
                stage1_deviations = _norm["deviations"]
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
            if _newroute and JUDGE_ONLY_CYCLE_AFTER_CAP:
                # 委任_11 G: 上限到達はRewriteの上限であって判定の上限ではない。`cycle_limit_exhausted_after_recheck`は出口として廃止
                # (許可リスト外)し、ループ冒頭で「判定だけのcycle」(Stage 2+S1、Rewriteなし)へ遷移する。
                _allow("cycle_limit_exhausted_after_recheck", {"funnel_passed": False},
                       legacy="cycle_limit_exhausted_after_recheck")
                switch_fired["JUDGE_ONLY_CYCLE_AFTER_CAP"] = switch_fired.get("JUDGE_ONLY_CYCLE_AFTER_CAP", 0) + 1
                if cycle > HARD_MAX_CYCLES + 2:  # 無限ループ防止(通常は到達しない: 判定cycleは必ずbreakするか、T後に1回だけ続く)
                    final_state, stage4_reason = "STAGE4_ESCALATION", "cycle_limit_exhausted_after_recheck"
                    break
            else:
                final_state = "STAGE4_ESCALATION"
                stage4_reason = "cycle_limit_exhausted_after_recheck"
                break

    if final_state in ("RESOLVED_REWRITE", "RESOLVED_STAGE2_DOWNGRADE", "RESOLVED_REWRITE_THEN_DOWNGRADE") and carry_blocking:
        unrewritten_blocking_pass += 1  # 事前基準: 0であること(構造上は起きない。起きたら記録して検知する)
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
        # 委任_49 作業2(記録専用。合否・重大度・書き換え対象の決定には使わない)
        "switches": {"JA_MODE": JA_MODE, "VS_MATCH_EXT": VS_MATCH_EXT, "HANDOFF_MODE": HANDOFF_MODE,
                         **({"CHECKER_SPANS_MODE": CHECKER_SPANS_MODE} if CHECKER_SPANS_MODE != CHECKER_SPANS_MODE_LEGACY else {}),
                         **({"VS_EXPLAIN_SPLIT": True} if VS_EXPLAIN_SPLIT else {}),
                         **({"VS_SENTENCE_RESTORE": True} if VS_SENTENCE_RESTORE else {}),
                         **({"STAGE2_NORMAL_TWO_OF_TWO": True} if STAGE2_NORMAL_TWO_OF_TWO else {}),
                         **({"FLOOR_VERIFY_MODE": FLOOR_VERIFY_MODE} if FLOOR_VERIFY_MODE != FLOOR_VERIFY_MODE_OFF else {}),
                         **({"STAGE2_DOWNGRADE_VERIFY": True} if STAGE2_DOWNGRADE_VERIFY else {}),
                         **({"CAUSAL_FLOOR": True} if CAUSAL_FLOOR else {}),
                         **({"STAGE2_SECOND_OPINION": True} if STAGE2_SECOND_OPINION else {}),
                         **({"RECHECK_MERGE_UNRESOLVED": True} if RECHECK_MERGE_UNRESOLVED else {}),
                         **({"RECHECK_BEFORE_AFTER_PAIRS": True} if RECHECK_BEFORE_AFTER_PAIRS else {}),
                         **({"STRUCTURAL_ELEMENT_REWRITE": True} if STRUCTURAL_ELEMENT_REWRITE else {}),
                         **({"ACTOR_GUARD_MODE": ACTOR_GUARD_MODE} if ACTOR_GUARD_MODE != "legacy" else {}),
                         **({"STRUCTURAL_PAIRS_TO_RECHECK": True} if STRUCTURAL_PAIRS_TO_RECHECK else {})},
        "all_deviations_raw": {"stage1": raw_stage1_all, "rechecks": raw_rechecks},
        "residual_at_pass": compute_residual_at_pass(instance_id, final_state, current_en_text, cycles_log,
                                                     raw_stage1_all, raw_rechecks),
        "severity_wobble": severity_wobble_records, "en_title_rewritten": bool(en_title_changes),
        "en_title_changes": en_title_changes,
    }
    if stage1_audit is not None:  # 委任_06(記録専用)
        result["stage1_coverage"] = stage1_audit
    if stage1_parsed.get("stage1_reclassify") is not None:  # 委任_04(記録専用、E2E集計用)
        result["stage1_reclassify"] = stage1_parsed["stage1_reclassify"]
    if f3_precheck_hits is not None:
        result["f3_precheck_always"] = {"precheck_floor_hits": f3_precheck_hits}
    if RECHECK_MODE != RECHECK_MODE_LEGACY:  # 委任_18(記録専用、legacyではキーを足さない)
        result["switches"] = {**result["switches"], "RECHECK_MODE": RECHECK_MODE}
        result["recheck_exit_check"] = {"done": exit_check_done, "log": exit_check_log}
    if STAGE1_MODE != STAGE1_MODE_LEGACY or F3_PRECHECK_ALWAYS or STAGE1_FAIL_CLOSED:
        result["switches"] = {**result["switches"], "STAGE1_MODE": STAGE1_MODE, "STAGE1_ROUTES": STAGE1_ROUTES,
                              "F3_PRECHECK_ALWAYS": F3_PRECHECK_ALWAYS, "STAGE1_FAIL_CLOSED": STAGE1_FAIL_CLOSED,
                              "STAGE1_R5_MODE": STAGE1_R5_MODE, "STAGE1_R3_REASONING": STAGE1_R3_REASONING,
                              "STAGE1_R5_REASONING": STAGE1_R5_REASONING, "STAGE1_NEGATION_MODE": STAGE1_NEGATION_MODE}
    _new_sw = {k: globals()[k] for k in ("STAGE4_ALLOWLIST", "LADDER_LOCATION_CARRY", "REWRITE_REVERT_GUARD",
                                          "SPAN_FALLBACK_CHAIN", "JUDGE_ONLY_CYCLE_AFTER_CAP", "LAST_RESORT_DELETE",
                                          "MATERIALITY_BLOCKING_PIN", "STAGE2_VERDICT_REUSE_NONBLOCKING",
                                          "STAGE2_SIBLING_LOCATIONS_CYCLE1") if globals()[k]}
    if _new_sw:  # 委任_11(記録専用): 新スイッチの状態・許可リスト判定・発火回数・事前基準の計測値
        result["switches"] = {**result["switches"], **_new_sw}
        _viol = [e for e in allowlist_log if not e["decision"]["allowed"]]
        result["stage4_allowlist"] = {
            "decisions": allowlist_log, "n_rerouted_legacy_exits": len(_viol),
            "final_reason_outside_allowlist": bool(final_state == "STAGE4_ESCALATION"
                                                   and stage4_reason not in STAGE4_ALLOWED_REASONS),
            "t_used": t_used, "carry_blocking_remaining": len(carry_blocking),
            "pass_blocked_by_carry": pass_blocked_by_carry, "switch_fired": switch_fired,
            "unrewritten_blocking_pass": unrewritten_blocking_pass}
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
        # 委任_08(Opus#13・Fable評価6、計測の是正): `text_pattern`=「因果接続語+目印」型(正規表現、大小文字無視)。旧`text_substring`は
        # 残し旧新並記(「and the flashy 20% plan」等の因果でない文は新パターンに一致しない)。
        {"sub_id": "B3", "related_fact_id": "HF-007", "text_substring": "flashy 20% plan",
         "text_pattern": r"\b(so|because|therefore|as a result|led to)\b[^.]{0,40}flashy 20% plan"},
    ],
    "safety_A2A3": [
        {"sub_id": "A2A3-0", "related_fact_id": "HF-003", "text_substring": "repay the money"},
    ],
    "safety_A4": [
        {"sub_id": "A4-0", "related_fact_id": "MUSE-HC-006",
         "text_substring": "completed the exchanges with users"},
        {"sub_id": "A4-1", "related_fact_id": "MUSE-HC-012",
         "text_substring": "actually speaking with human staff", "expected": "ACCEPTABLE"},
        # 委任_57(2026-10-03、Fable判断=ユーザー正式採用の線引き[例2]の適用): A4-1は問題なし
        # (ACCEPTABLE)へ再ラベルし、Meta-1/Meta-2と同じ監視用へ移した。旧: BLOCKING(Safety-critical)。
    ],
    "safety_A5": [
        {"sub_id": "A5-0", "related_fact_id": "MUSE-HC-012",
         "text_substring": "temporarily put back the feature"},
    ],
    # 委任_55(2026-10-03、ユーザー決定=線引きの正式採用、`APPROVED_FOR_PRODUCTION`、
    # `PRODUCTION_WIRED`未達): Meta-1/Meta-2(「Also, some calls needed user
    # information to continue.」)は軽微(QUALITY)と確定したため、Safety-criticalから
    # 外した。削除はせず`expected: "QUALITY"`を付けて「過剰品質の監視用」として残す
    # (`detect_safety_critical_misdowngrades`/`compute_residual_at_pass`の対象外、
    # `_safety_critical_defs`が`expected`がBLOCKINGの定義だけを返す)。旧: Safety-critical
    # (BLOCKING維持、〜2026-10-02、委任_29〜委任_49)。監視は
    # `detect_over_quality_monitor_blocks`(最終materialityがBLOCKINGのまま=過剰品質の記録)。
    "meta_run03_standard": [
        {"sub_id": "Meta-1", "related_fact_id": "MUSE-HC-010",
         "text_substring": "needed user information to continue", "expected": "QUALITY"},
        {"sub_id": "Meta-2", "related_fact_id": "MUSE-HC-012",
         "text_substring": "needed user information to continue", "expected": "QUALITY"},
    ],
    "bgroup_B4": [
        {"sub_id": "B4-a", "related_fact_id": "MUSE-HC-002",
         "text_substring": "take over when AI alone has trouble"},
    ],
    # 委任_02(KPI-RECOVERY-REDESIGN-02、Opus#11論点12・Fable評価6、計測の是正、新しい仕様ではない): neg5はB3と同一文
    # ("Concerns about US-Iran attacks, ... continued on July 14. So the flashy 20% plan left the stage.")を含み、
    # プロジェクト自身のv2訂正で正BLOCKING扱い(`UNNECESSARY_REWRITE_V2_EXCLUDE_INSTANCE_IDS`)だが、手作業の本定義に
    # 未登録だったため流出が数えられていなかった。`registered_in`付きの定義は旧定義(委任_01まで、流出10行)の集計から
    # 分けて数える(`safety_critical_dual_summary`、旧値/新値の並記)。
    "neg5_hormuz_div_a2": [
        {"sub_id": "B3-same@neg5", "related_fact_id": "HF-007", "text_substring": "flashy 20% plan",
         "text_pattern": r"\b(so|because|therefore|as a result|led to)\b[^.]{0,40}flashy 20% plan",
         "registered_in": "OPEN-233-KPI-RECOVERY-REDESIGN-02/delegation_02"},
    ],
}


# 委任_03 作業2-3(Fable判断2026-10-04、ユーザー未確認・否認されれば戻す): rep24 cycle 2のB3「and」版
# (「…continued on July 14, and the flashy 20% plan left the stage.」)は正式基準(重大=事実関係の重大な誤解)で
# 問題なし(ACCEPTABLE。「and」は因果を主張しない。確認役も2回ともRELEASE)。`text_substring`「flashy 20% plan」の部分一致で
# Safety-critical流出に計上されていたため、A4-1(委任_57)と同じ方式で再ラベルする。定義(`SAFETY_CRITICAL_CLAIM_DEFS`)は
# 変えず、集計側で旧値(上書きなし)/新値(上書き後)を並記する。`match_all`の部分文字列を全て含み`match_none`のいずれも含まない
# (正規化後)claimだけが対象。
CORRECT_LABEL_OVERRIDES = [
    {"id": "B3_and_version", "instance_ids": ("bgroup_B3", "neg5_hormuz_div_a2"), "related_fact_id": "HF-007",
     "match_all": ("and the flashy 20% plan",), "match_none": ("so the flashy 20% plan",), "label": "ACCEPTABLE",
     "decided_by": "Fable判断2026-10-04、OPEN-233-KPI-RECOVERY-REDESIGN-02委任_03、ユーザー未確認"},
]


def label_override_for(instance_id, related_fact_id, claim_text):
    """該当する`CORRECT_LABEL_OVERRIDES`の項目(無ければNone)。"""
    n = _norm_same_sentence(claim_text or "")
    for o in CORRECT_LABEL_OVERRIDES:
        if instance_id in o["instance_ids"] and (related_fact_id or "") == o["related_fact_id"]                 and all(_norm_same_sentence(m) in n for m in o["match_all"])                 and not any(_norm_same_sentence(m) in n for m in o["match_none"]):
            return o
    return None


def safety_def_matches(d: dict, text: str, use_pattern: bool = False) -> bool:
    """委任_08: 定義`d`が`text`に一致するか。`use_pattern`かつ`text_pattern`があれば正規表現(大小文字無視)、無ければ旧`text_substring`の部分一致。"""
    if use_pattern and d.get("text_pattern"):
        return re.search(d["text_pattern"], text or "", re.IGNORECASE) is not None
    return d["text_substring"] in (text or "")


def _safety_critical_defs(instance_id) -> list:
    """`SAFETY_CRITICAL_CLAIM_DEFS`のうち、期待がBLOCKINGの定義(`expected`省略時=BLOCKING)だけ。
    `expected`がQUALITY等の定義は「過剰品質の監視用」でSafety-critical検出の対象外(委任_55)。"""
    return [d for d in (SAFETY_CRITICAL_CLAIM_DEFS.get(instance_id) or [])
            if d.get("expected", "BLOCKING") == "BLOCKING"]


def detect_over_quality_monitor_blocks(instance_results: list) -> list:
    """委任_55: `expected`がBLOCKING以外の監視用定義(Meta-1/Meta-2等、期待QUALITY)について、
    最終materialityがBLOCKINGのまま(=過剰品質)だった箇所を記録する(¥0、記録専用、判定・状態遷移
    には使わない)。`detect_safety_critical_misdowngrades`とは逆向き。"""
    rows = []
    for r in instance_results:
        defs = [d for d in (SAFETY_CRITICAL_CLAIM_DEFS.get(r.get("instance_id")) or [])
                if d.get("expected", "BLOCKING") != "BLOCKING"]
        for cycle_idx, c in enumerate(r.get("cycles", [])):
            for sr in c.get("stage2_results", []):
                fact_id = (sr.get("related_fact_id") or "").strip()
                text = sr.get("claim_text") or ""
                for d in defs:
                    if d["related_fact_id"] != fact_id or d["text_substring"] not in text:
                        continue
                    if sr.get("materiality") == "BLOCKING":
                        rows.append({
                            "instance_id": r["instance_id"], "sub_id": d["sub_id"],
                            "cycle_index": cycle_idx, "expected": d.get("expected"),
                            "materiality": sr.get("materiality"),
                            "llm_materiality": sr.get("llm_materiality"),
                            "floor_reason": sr.get("floor_reason"), "claim_text": text})
    return rows


def detect_safety_critical_misdowngrades(instance_results: list, defs_by_instance: dict | None = None,
                                         use_pattern: bool = False) -> list:
    """SAFETY_CRITICAL_CLAIM_DEFSに登録されたinstanceのみを対象に、cycleご
    とのstage2_results実測値から、最終materiality(floor/hook/disclosure-gap
    適用後)がBLOCKING以外になった箇所を機械的に検出する(¥0、新規API呼び
    出しなし、既存run_instance結果jsonへの後処理のみ)。
    委任_02: `defs_by_instance`(instance_id→定義list)を渡すと、その定義で検出する(自動導出
    `derive_safety_critical_from_labels`の集計用)。省略時は登録済み定義(neg5を含む)。"""
    rows = []
    for r in instance_results:
        defs = (_safety_critical_defs(r.get("instance_id")) if defs_by_instance is None
                else (defs_by_instance.get(r.get("instance_id")) or []))
        if not defs:
            continue
        for cycle_idx, c in enumerate(r.get("cycles", [])):
            for sr in c.get("stage2_results", []):
                fact_id = (sr.get("related_fact_id") or "").strip()
                text = sr.get("claim_text") or ""
                for d in defs:
                    if d["related_fact_id"] != fact_id or not safety_def_matches(d, text, use_pattern):
                        continue
                    if sr.get("materiality") != "BLOCKING":
                        rows.append({
                            "instance_id": r["instance_id"], "sub_id": d["sub_id"],
                            "cycle_index": cycle_idx, "materiality": sr.get("materiality"),
                            "llm_materiality": sr.get("llm_materiality"),
                            "floor_reason": sr.get("floor_reason"),
                            "claim_text": text,
                            "registered_in": d.get("registered_in"),
                            "related_fact_id": fact_id,
                        })
    return rows


# 委任_02 作業2-5(Opus#11論点12・Fable評価6): Safety-critical集合を手作業のリストだけに頼らず、「正BLOCKINGのラベルが付いた
# claim(正規化した同一文を含む)」から自動で導く補助集計。ラベル(`SAFETY_CRITICAL_CLAIM_DEFS`の期待BLOCKING定義)の
# `text_substring`を(空白・引用符字形・大小文字を正規化して)本文に含む他instanceへ、同じ(related_fact_id, text_substring)の
# 定義を複製する。記事本文は`build_target_instances()`のfixture(決定論)。
def _norm_same_sentence(s: str) -> str:
    return _norm_for_residual(s).casefold()


def normalized_same_as_labeled(claim_text: str, labeled_instance_id: str) -> bool:
    """claim文が、`labeled_instance_id`の正BLOCKINGラベル(`text_substring`)を正規化後に含むか。"""
    n = _norm_same_sentence(claim_text or "")
    return any(_norm_same_sentence(d["text_substring"]) in n for d in _safety_critical_defs(labeled_instance_id))


def derive_safety_critical_from_labels(instances: list | None = None) -> dict:
    """instance_id→導出した定義list(ラベル元のinstance自身は除く。手作業登録済みのinstanceも導出に含める=
    登録漏れの検出に使うため)。`instances`省略時は`build_target_instances()`。"""
    insts = instances if instances is not None else build_target_instances()
    derived: dict = {}
    for src_id, defs in SAFETY_CRITICAL_CLAIM_DEFS.items():
        for d in defs:
            if d.get("expected", "BLOCKING") != "BLOCKING" or d.get("registered_in"):
                continue  # 元ラベルは旧定義(手作業・期待BLOCKING)だけ。neg5等の登録は導出元にしない
            needle = _norm_same_sentence(d["text_substring"])
            for inst in insts:
                iid = inst["instance_id"]
                if iid == src_id:
                    continue
                if needle in _norm_same_sentence(inst["fixture"].get("article_text") or ""):
                    derived.setdefault(iid, []).append(
                        {"sub_id": f"{d['sub_id']}@derived", "related_fact_id": d["related_fact_id"],
                         "text_substring": d["text_substring"], "derived_from": src_id})
    return derived


def safety_critical_dual_summary(instance_results: list, derived: dict | None = None) -> dict:
    """旧値(委任_01まで: 手作業登録の流出行)と新値(登録済み[neg5含む]+自動導出の和集合)を並記する。"""
    reg_rows = detect_safety_critical_misdowngrades(instance_results)
    old_rows = [r for r in reg_rows if not r.get("registered_in")]
    derive_error = None
    if derived is not None:
        der = derived
    else:
        try:
            der = derive_safety_critical_from_labels()
        except Exception as e:  # noqa: BLE001  # fixture未構築などの環境差。集計だけ空にして記録する
            der, derive_error = {}, f"{type(e).__name__}: {e}"
    der_rows = detect_safety_critical_misdowngrades(instance_results, defs_by_instance=der)

    def _key(r):
        return (r["instance_id"], r["cycle_index"], _norm_same_sentence(r["claim_text"]))
    new_union = {_key(r): r for r in reg_rows}
    for r in der_rows:
        new_union.setdefault(_key(r), r)
    # 委任_03: `CORRECT_LABEL_OVERRIDES`(Fable判断、ユーザー未確認)適用後の値を並記(上の値は上書きなしの旧値/新値)。
    def _not_overridden(r):
        return label_override_for(r["instance_id"], r.get("related_fact_id"), r["claim_text"]) is None
    reg_rows_ov = [r for r in reg_rows if _not_overridden(r)]
    new_union_ov = {k: r for k, r in new_union.items() if _not_overridden(r)}
    override_dropped = [{"instance_id": r["instance_id"], "cycle_index": r["cycle_index"], "sub_id": r["sub_id"]}
                        for k, r in new_union.items() if not _not_overridden(r)]
    return {"derive_error": derive_error, "old_definition_rows": len(old_rows), "old_definition_unique": len({(r["instance_id"], r["sub_id"]) for r in old_rows}),
            "registered_rows_new": len(reg_rows), "derived_rows": len(der_rows),
            "new_definition_rows": len(new_union),
            "after_label_override_registered_rows": len(reg_rows_ov),
            "after_label_override_new_definition_rows": len(new_union_ov),
            "after_label_override_dropped": override_dropped,
            "new_definition_unique": len({(k[0], k[2]) for k in new_union}),
            "new_definition_detail": [{"instance_id": r["instance_id"], "sub_id": r["sub_id"],
                                       "cycle_index": r["cycle_index"], "materiality": r["materiality"]}
                                      for r in new_union.values()]}


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
            # 委任_02: `silent_pass_candidate`/`_rows`は旧定義(委任_01まで、手作業登録=neg5登録前)の値のまま。
            # 新定義(neg5登録+正BLOCKINGラベルからの自動導出)は`safety_critical_dual`へ並記する。
            "silent_pass_candidate": len({
                (row["instance_id"], row["sub_id"])
                for row in safety_critical_misdowngrade_rows if not row.get("registered_in")
            }),
            "silent_pass_candidate_rows": [row for row in safety_critical_misdowngrade_rows
                                           if not row.get("registered_in")],
            "safety_critical_dual": safety_critical_dual_summary(instance_results),
            # 委任_55: 過剰品質の監視用(Meta-1/Meta-2、期待QUALITY)。記録専用。
            "over_quality_monitor_rows": detect_over_quality_monitor_blocks(instance_results),
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
    parser.add_argument("--vs-match-ext", action="store_true",
                         help="委任_49: 照合の追補(L5末尾句読点・位置ラベル・単語境界)を有効化(既定OFF=委任_42の照合)")
    parser.add_argument("--vs-explain-split", action="store_true",
                         help="委任_57: 説明文混入のTrial専用後段分離P-strict-closedを有効化(既定OFF。有効化・Production採用はユーザー承認待ち)")
    parser.add_argument("--vs-sentence-restore", action="store_true",
                         help="委任_66: L6完結文復元(Trial専用、VS_MATCH_EXTも必要。既定OFF。有効化・Production採用はユーザー承認待ち)")
    parser.add_argument("--ja-mode", default=JA_MODE_PAIRED, choices=[JA_MODE_PAIRED, JA_MODE_ENGLISH_ONLY],
                         help="委任_49: english_onlyで日本語側の処理を迂回(既定paired=現行)")
    parser.add_argument("--checker-spans-mode", default=CHECKER_SPANS_MODE_LEGACY,
                         choices=[CHECKER_SPANS_MODE_LEGACY, CHECKER_SPANS_MODE_VIOLATION_SPANS],
                         help="委任_53: violation_spansでCheckerの違反箇所を配列で受ける(既定legacy=現行)")
    parser.add_argument("--floor-verify-mode", default=FLOOR_VERIFY_MODE_OFF,
                         choices=list(FLOOR_VERIFY_MODES),
                         help="委任_61: time_onlyで時期のfloorだけ追加確認(2回とも非重大のときだけ解放)を有効化(既定off=従来、比較・方向等は決定論維持)")
    parser.add_argument("--stage2-normal-two-of-two", action="store_true",
                         help="委任_01(KPI-RECOVERY-REDESIGN-02): NORMAL群Stage 2 2-of-2をON(旧挙動の再現用、既定OFF=Production非存在のTrial補助を使わない)")
    parser.add_argument("--stage2-downgrade-verify", action="store_true",
                         help="委任_02(Opus#11→Fable評価): Checker MAJORをStage 2が非BLOCKINGにしたものをTier 0決定論Guard+Tier 1確認役で再確認し、解除不可はBLOCKING→Rewriteへ戻す(既定OFF=従来)")
    parser.add_argument("--kpi-trial-config", action="store_true",
                         help="委任_01: KPI確認構成(KPI_TRIAL_SWITCHES: rep23〜25構成+L6完結文復元+NORMAL群2-of-2 OFF)を適用。個別の--vs-*等より優先")
    args = parser.parse_args()
    globals()["STAGE2_NORMAL_TWO_OF_TWO"] = bool(args.stage2_normal_two_of_two)
    globals()["STAGE2_DOWNGRADE_VERIFY"] = bool(args.stage2_downgrade_verify)
    globals()["FLOOR_VERIFY_MODE"] = validate_floor_verify_mode(args.floor_verify_mode)
    globals()["VS_MATCH_EXT"] = bool(args.vs_match_ext)
    globals()["VS_EXPLAIN_SPLIT"] = bool(args.vs_explain_split)
    globals()["VS_SENTENCE_RESTORE"] = bool(args.vs_sentence_restore)
    globals()["JA_MODE"] = args.ja_mode
    globals()["CHECKER_SPANS_MODE"] = args.checker_spans_mode
    if args.kpi_trial_config:
        apply_kpi_trial_switches()
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
    if FLOOR_VERIFY_MODE != FLOOR_VERIFY_MODE_OFF:
        # 委任_60: 案1の追加確認のruntime evidence(全sampleの全cycle・全stage2_results)。
        summary["floor_verify"] = floor_verify_summarize(
            sr for res in sample_instance_results for r in res for cyc in r.get("cycles", [])
            for sr in cyc.get("stage2_results", []))
    if STAGE2_DOWNGRADE_VERIFY:
        # 委任_02: 降格確認(Tier 0/1/2)のruntime evidence(全sampleの全cycle・全stage2_results)。
        summary["downgrade_verify"] = downgrade_verify_summarize(
            sr for res in sample_instance_results for r in res for cyc in r.get("cycles", [])
            for sr in cyc.get("stage2_results", []))
    if CAUSAL_FLOOR:
        summary["tier0"] = tier0_summarize(r for res in sample_instance_results for r in res)
    if STAGE2_SECOND_OPINION:
        summary["s1_second_opinion"] = s1_summarize(r for res in sample_instance_results for r in res)
    if VS_SENTENCE_RESTORE:
        summary["sentence_restore"] = sentence_restore_summarize(
            r for res in sample_instance_results for r in res)
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
