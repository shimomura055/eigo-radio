## 管理ID

EDITORIAL-4TYPE-FOLLOWUP-03-DISCOVERY-NOJARGON-B1-KEYPHRASE
並行タスク衝突確認: 並行して News B1追加(`.../news/`)・Trend再生成(`.../trend/`)・SSOT登録タスク(SSOT+Git)が走る。本タスクは`er014_output/four_type_observation_01/discovery/`配下のみを書き、SSOT・Git・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`を触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_4T_DISCOVERY_FIX.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: **既存Production仕様(No Jargon=PRODUCTION_WIRED)への個別非遵守の修正+生成漏れ補完(B1)+Key Phrase再生成**。新仕様Trialではない。仕様Status変更なし。
- 背景(ユーザー判断): Discovery記事「Why can silence feel uncomfortable?」A2のReader-facing本文に"parasympathetic activity"/"sympathetic activity"/"fMRI acoustic noise"等の高度専門語が出現。CURRENT_SPEC上No Jargon(聞いただけでは理解しにくい高度な専門用語・学術的手法名をそのまま使わず平易なspoken Englishで説明する)はProduction Writer正式原則であり、本件は既存仕様への非遵守/Regression。**新しいNo Jargon Validator/Checker/QAは追加しない**。
- 実施手順:
  (1)**A2修正**: 既存Research/Verified Fact Ledger(`discovery/research/verified_fact_ledger.txt`)を再利用し(Research再実行禁止)、既存No Jargon仕様の範囲内で修正する。優先順: (a)まず**既存の正式rewrite経路**(`er010_ledger_local_rewrite_09.rewrite_ng_item`+`run_diff_qa_for_accepted_rewrite`等、Ledger整合と差分QAを伴う局所書き換え)を当該文に適用して専門語を平易に言い換える(Factの意味・scope・causality・certaintyを変えない。例: "parasympathetic activity was higher during fMRI acoustic noise than during silence"→"the body's calming system was more active during the scanner's noise than during silence"のように、対象・方向・比較・断定度を保つ)。(b)rewrite経路が本用途に使えない/差分QAで意味変化が検出される場合は、Production正式関数`run_one_pattern_staged_discovery_focus()`で同一LedgerからA2を再生成し、専門語の残存をgrepで確認(残存すれば(a)を追加適用)。どちらの経路を使ったかと理由を記録。修正後、Fact Checker/Ledger Deviation/Directional Precheckを通常どおり実行し、旧A2は`discovery/a2_before_fix/`へ退避。
  (2)**B1追加生成**: 同一Ledgerで`run_one_pattern_staged_discovery_focus()`によりB1Bを正式pathで生成。生成後、Reader-facing本文の高度専門語(上記3語+同種の学術手法名・生理学用語)をgrep確認し、残存すれば(1)(a)と同じ正式rewrite経路で修正。A2/B1双方がNo Jargonを満たす状態にする。
  (3)**Key Phrase再生成**: 修正版A2/B1をcanonical articleとして確定した後、現行正式Key Phrase Production仕様(CURRENT_SPECで特定)でA2/B1それぞれのKey Phraseを再生成(旧記事由来のKey Phraseがあれば再利用しない)。既存Validator(選定・日本語gloss・平易さ・redundancy・article整合)を通常どおり実行。追加QAは作らない。
- 費用上限: ¥130(A2修正+B1生成+QA+Key Phrase)。
- 禁止: Research再実行/新Validator・QA追加/Prompt改善/QA緩和/Factの意味変更/Git/SSOT/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件: 専門語を除くとFactの意味が維持できない(差分QAで意味変化)/B1追加生成に新Production仕様が必要/Key Phrase正式pathがDiscovery B1に未対応と判明(未承認実装が必要)/費用上限。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
---

## ユーザー指示(原文)

> Discovery: No Jargon違反を個別修正。新しいNo Jargon Validator / Checker / QAは追加しない。上記専門用語をそのままReader-facing本文に残さないよう、既存No Jargon仕様の範囲内で平易に言い換えた上で記事を再生成または既存正式retry/rewrite経路で修正する。重要: Factの意味・scope・causality・certaintyを変えないこと。
> Discovery: B1も即時生成。既存Research / Verified Fact Ledgerを再利用し、Researchを再実行せずB1を追加生成する。最終成果物としてはA2/B1双方がNo Jargon仕様を満たす状態にすること。
> Discovery: 記事修正後のKey Phrase再生成。専門用語を除いた修正版記事をcanonical articleとして確定した後、Key Phraseを再生成する。古い記事から生成したKey Phraseを再利用しない。A2/B1それぞれについて、現行正式Key Phrase Production仕様を使用する。Key Phrase選定/日本語gloss/No Jargon・平易さ/redundancy/articleとのcontent consistency/既存Validatorを通常どおり確認。必要以上の追加QAを作らない。
> 最終成果物: No Jargon修正版A2/新規・修正版B1/A2/B1 Key Phrase再生成/専門用語がReader-facing本文から除かれた確認/1 Production生成セット原価。

## 事前指定Read一覧

1. `er014_output/four_type_observation_01/discovery/run_discovery_a2.py` 全文(前回driver。Research部を外しB1B生成・修正・Key Phraseを行う`run_discovery_fix_b1b_kp.py`を派生)。
2. `er014_output/four_type_observation_01/discovery/reader_facing_article.txt` 全文(修正対象。専門語の出現箇所を特定)。
3. `CURRENT_SPEC.md`: Grep `No Jargon` → 正式原則の定義範囲のみRead。Grep `Key Phrase` → A2/B1BのKey Phrase Production仕様(スクリプト・関数・Validator)の定義範囲のみRead。
4. `er010_ledger_local_rewrite_09.py`: Grep `^def (rewrite_ng_item|run_diff_qa_for_accepted_rewrite|apply_diff_qa_to_resolved_rewrite|locate_target_sentence|apply_rewrites|extract_point_context)` → シグネチャ+docstringのみ(正式rewrite経路の流用のため)。
5. `er003_discovery_focus_staged_production_01.py`: Grep `^def run_one_pattern_staged_discovery_focus|level` → level="b1b"指定方法の該当範囲のみ。
6. Key Phrase正式スクリプト(Read 3で特定): Grep `^def |add_argument` → 入口・引数のみ。
7. `er014_output/four_type_observation_01/discovery/observation.json` 全文(A2費用、セット原価合算用)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- 専門語検出(決定的、修正前後で実行し記録): 対象語=`parasympathetic|sympathetic activity|fMRI|EKG|counterbalanced|acoustic noise|need for cognition|physiological arousal`+Read 2で見つかる同種語。`discovery/jargon_scan_before.json`/`jargon_scan_after.json`(A2/B1別)。
- 退避: `discovery/a2_before_fix/`へ旧A2一式をコピー。
- driver: `discovery/run_discovery_fix_b1b_kp.py`(新規。費用上限¥130ガード)。出力: `discovery/a2/`(修正版)、`discovery/b1b/`、`reader_facing_article.txt`(A2修正版)、`reader_facing_article_b1b.txt`、`key_phrases/a2/`・`key_phrases/b1b/`(正式pathの出力形式)、`rewrite_log.md`(修正した文の旧→新、使用経路、差分QA結果、Fact意味維持の確認)、`cost_summary_fix.json`、`raw_usage_log`(前回分と混ざる場合は行数差分で分離)。
- `discovery/production_set_cost.json`(新規): 「Discovery Production 1生成セット(共通Research/Ledger+A2+B1)総原価」=Research/Ledger[初回¥58.37]+A2直接費[初回¥45.88]+本修正(A2 rewrite/再生成)+B1直接費+QA+Key Phrase(A2/B1)+retry+rewrite。機械分離できない分は「共通」。50:50配賦禁止。
- 中間ログ: `progress_log.md`に「Discovery fix/B1B/KP: …」1行追記。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-03-DISCOVERY-NOJARGON-B1-KEYPHRASE.md --json-out docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-03-DISCOVERY-NOJARGON-B1-KEYPHRASE_check.json`
2. 実行: `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_fix_b1b_kp.py`(driver内でledger_path/out_dir/budget_jpy=130を固定。全文コマンドと固定値をRESULT_PACKETへ記録)
3. 集計: `.venv\Scripts\python.exe er014_output\four_type_observation_01\aggregate_usage.py --run-dir er014_output\four_type_observation_01\discovery --out er014_output\four_type_observation_01\discovery\observation_fix.json`
(回帰不要: Production/Trialコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOpen Item候補(あれば)を列挙。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補ファイル一覧」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_4T_DISCOVERY_FIX.md`に: 1) status(A2修正/B1生成/KP再生成それぞれ)、2) A2修正: 使用経路(rewrite/再生成)と理由、修正文一覧(旧→新)、差分QA結果、Fact意味維持の確認、jargon scan before/after、3) B1: 語数・相対パス・jargon scan・主要QA(Stage別・Fact Checker・Ledger・Overlap/Value・Directional)・retry回数、4) A2修正後の主要QA、5) Key Phrase: A2/B1のKey Phrase一覧(英/日本語gloss)・Validator結果、6) actual model_id、7) 費用: **Discovery Production 1生成セット(共通Research/Ledger+A2+B1)総原価=¥xx.xx**+直接費内訳(Research/Ledger ¥58.37、A2 Writer[初回]、A2修正、B1 Writer、QA、Key Phrase A2/B1、retry、rewrite、共通)、本タスク実費、8) API token(本タスク分)、9) Open Item候補(No Jargon非遵守の再発観測用に、出現語・箇所を記録)、10) commit対象候補一覧、11) T-0・事前指定外Read・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥130)
- [x] 並行タスク衝突回避あり(discovery/配下限定・Git操作なし)
