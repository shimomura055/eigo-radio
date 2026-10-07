# 2026-10-07 OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01 委任_01(W1/W2バグ修正[スイッチ付き]+Stage1候補化率・r3リンク情報の棚卸し、¥0)

Management-ID: OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01(委任_01)

## 並行タスク(衝突回避)
委任_02(設計v2、`docs/pm/checker_action_policy_01/`、opus review保存)が並行。本委任の書込先: runner/checkerコード+tests、`er052_output/open233_stage2_01/precheck/`、delegation_log。SSOT/ACTIVE_TASK/RESULT_PACKET編集禁止、git禁止(後でまとめる)。**API禁止(¥0、既存ログのみ)**。Production変更禁止: 対象runner `er052_open233_self_recovery_flow_runner_01.py` と `er052_open233_stage1_coverage_checker_01.py` はCheckerのTrial/DEV runner(PRODUCTION_WIRED前)だが、**新規挙動は全て環境変数/構成スイッチで既定OFF**にし、既定挙動を変えない(回帰テストで確認)。held-out(`er052_output/open233_stage0_01/reclass/split.json`)の項目は参照しない。

## 事前指定Read
- `docs/pm/checker_action_policy_01/design_01.md` §1(W1〜W3の原因箇所: runner L425-454、L6030-6074、stage1 checker L1032 `run_recheck_scope`)
- `er052_output/open233_control_checker_polysemy_trial_01/eval/RCA_jb9k_qvqc.md`(qvqc rep2のログ所在)
- `er052_output/open233_stage0_01/reclass/{RECLASS.md,known_relation_ng.jsonl,split.json}`(dev項目のみ)
- 既存テスト(`er052_output/open233_polysemy_trial_02/tests/`、runner用のtests をGlob)

## 作業
1. **W1(タイトル`# `記法の保存)**: Rewriteがタイトルの`# `を落とし、タイトルがHook文S1.1として判定される経路を特定し、スイッチ `OPEN233_FIX_W1_TITLE_MARKUP=1` で記法を保持する修正。単体テスト(qvqc rep2の実データを固定fixtureに: ON=タイトルがtitle単位として扱われる/OFF=現行挙動)。
2. **W2(構造要素の前後対をRecheckへ配線)**: `STRUCTURAL_PAIRS_TO_RECHECK: True` が `run_recheck_scope` へ何も渡していない箇所を特定し、スイッチ `OPEN233_FIX_W2_STRUCTURAL_RECHECK=1` で前後対(before/after)をRecheckの判定単位に渡す修正。単体テスト(ON=タイトル前後対がRecheck入力に含まれる/OFF=現行)。
3. 回帰: 既存テスト全件(件数報告)。両スイッチOFFで差分0であることを、qvqc rep2・jb9k rep1の保存済みログに対する決定論部分のreplay(API無し)で確認できる範囲で確認(確認できない部分は明記)。
4. **Stage1候補化率(¥0)**: dev既知NG(known_relation_ng.jsonl の dev 100件のうち、Checkerログが存在する記事=本番経路Trial 18本+E2E_02等Checkerを通した記事)について、Stage1が該当文をfinding候補として拾っていたか(候補化率)、Stage2の判定(BLOCKING/QUALITY/格下げ)、2nd opinion結果を、既存run JSONから集計 → `er052_output/open233_stage2_01/precheck/stage1_candidate_rate.md` + json。ガード対象型(否定・不在/全称/方向・極性/主体/数値)別に分ける。Checkerログが無い記事(B3 Trialは--no-checker)は対象外として件数を明記。
5. **r3 support_fact_ids の棚卸し**: Stage1 r3の出力に support_fact_ids が存在するか/保存されているか(§83 R9で未保存)/保存するための最小変更点(スイッチ `OPEN233_SAVE_R3_SUPPORT_IDS=1`、既定OFF)を実装し、既存ログからの事後復元が可能かを確認。devで評価JSONのfact_id(oracle)との一致率を、復元できる範囲で算出(できなければ「要replay」と明記)。
6. **replay対象の特定**: 現行Stage1版と同じ版のログが残る記事一覧(版識別子・件数、B3 Trialの版違い有無)→ `precheck/replay_targets.json`。
7. T-0: 本委任文を `docs/pm/delegation_log/2026-10-07_OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01_01.md` へ保存+check.json。

## 報告
14行以内: W1/W2の修正箇所(ファイル・関数)とテスト結果、OFF時差分0の確認範囲、Stage1候補化率(型別、分母)、Stage2格下げ率、r3 support_fact_idsの有無・一致率(または要replay)、replay対象件数と版、既存テスト件数、ファイルパス。
