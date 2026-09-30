# 2026-10-01 OPEN-233-SELF-RECOVERY-TRIAL-01 委任_26

## 内容
既存Evidenceの実文開示。新規API課金・Trial実行・コード変更・SSOT変更は
禁止。成果物は新規doc 1本のみ。費用¥0。

## 作業
1. `er052_output/open233_self_recovery_flow_runner_01_iter7/instances_s1
   /instances_s2`の`neg1_meta_b3prod_a2.json`・`neg3_hormuz_prodrunner_
   b1b.json`を読み、cycle単位でBefore/Ledger確認済みFact/Checker issue/
   Stage2 materiality・basis/Rewrite後の実文(EN/JA)を逐語抽出した。
2. `er052_output/open233_self_recovery_flow_runner_01_rep15/instances_s1
   /hormuz_run03_standard.json`(主)と`_rep14`版(補助比較)を読み、
   cycle1〜3の全claim・全Rewrite段階・JA fail-open guard違反・
   `ja_en_equivalence_verdict`推移を逐語抽出した。
3. Ledger原文(`er019_output/family_x_refresh_e2e_01/meta/run_03/
   ledger/...`のMUSE-HC-006/012、`.../hormuz/run_03/ledger/...`の
   HF-009)を逐語引用した。
4. `docs/pm/design_open233_self_recovery_flow_01.md`(§5-8 J-1ラダー、
   委任_21 A-3のneg1 disputed判定根拠、委任_24のA-3 neg3両論併記、
   §7-0正解ラベル表)と`docs/pm/opus_l2_review_open233_self_recovery_
   04.md`(Q2、neg3のBLOCKING妥当判定)を逐語引用した。
5. `er052_open233_self_recovery_flow_runner_01.py`のJ-1実装
   (`paired_rewrite`・プロンプトテンプレート、同一callでJA/EN同時
   生成であることを確認)、`escalate_to_paragraph`発火条件
   (`repeat_fact_ids_for_recheck`、同一fact_id再出現のみが条件で
   ①③の実際の試行結果は問わない)、`ja_deviation_unresolved`への
   Escalation機構(`ja_pending_deviation`)をコード読解で確認した。
6. `docs/pm/open233_evidence_disclosure_neg1_neg3_hormuz_01.md`を新規
   作成し、上記を(1)neg1、(2)neg3、(3)hormuz_run03_standard(A元記事/
   B最初の判定/C各Rewrite段階/D最終Escalation直接原因/E生成順序/
   F段落Rewrite要否の再評価)、(4)worker結論、の構成で整理した。
   json不記載の情報(等価QA判定理由テキスト本文)は「記録なし」と明記し、
   推測で埋めていない。

## 主な発見(doc本体に詳細)
- neg1(MUSE-HC-006 hookclaim)は真にdisputedな境界事例(rep11 2/2
  BLOCKING、rep12 2/2非BLOCKING、iter7 s1 BLOCKING/s2非BLOCKING)。
- neg3(HF-009 scope反転)はOpus #4 Q2が「BLOCKING妥当、negative群
  ラベル側が誤っている可能性が高い」と判定済み(design doc既存記載の
  再確認、新規判断はしていない)。
- hormuz_run03_standard(rep15)の段落Rewrite(cycle2)は、同型claim
  (①③)が語/文レベルで解決済みだったにもかかわらず、`escalate_to_
  paragraph`(同一fact_id再出現のみを条件とする決定論ルール)により
  ①③を一度も試さず④へ直行していたことをコードとログ両方で確認した。
  段落単位の同時生成(JA/EN 1 call)がEN/JA間の情報量非対称
  (JA側で「政治の発言が大きく変わっても」相当の1文が丸ごと削除され
  たがEN側は維持)を生み、`ja_en_equivalence_verdict: FAIL`経由で
  STAGE4_ESCALATION(`ja_deviation_unresolved`)へ至った。等価QA自体の
  判定理由テキストはJSON Evidenceに保存されておらず特定不能。

## 検証
- 読み取りのみ(Read/Grep)。コード変更・SSOT変更・API呼び出しなし。
- `git diff --stat`: 新規doc 3件(本開示doc・本delegation_log・
  ACTIVE_TASK_C233AC/RESULT_PACKET_C233AC)以外に差分なし(確認予定、
  commit前に再確認する)。

## 費用
¥0(API呼び出しなし)。

Management-ID: OPEN-233-SELF-RECOVERY-TRIAL-01
