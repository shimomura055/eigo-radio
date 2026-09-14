# 管理ID

EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE(継続CONT2、Fable修正指示2回目)
並行タスク衝突確認: 並行タスクなし(Voices・Trend・Trial-09は完了済み)。本タスクは`er014_output/four_type_observation_01/discovery/`配下のみを書き、SSOT・Git・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_4T_DISCOVERY_COMPLETE_3.md`(新規)。driverは`run_discovery_complete_3.py`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: Discovery A2/B1B+Key Phraseの**完成**(最終ステップ)。前回CONT1(`docs/pm/RESULT_PACKET_4T_DISCOVERY_COMPLETE_2.md`)の到達点: B1B=F002/F009/F014修正済み・記事全体final QA PASS。A2=F002文をoperator escalationで修正(文単位diff QA PASS)したが**記事全体final QAは未再実行**(budget STOP)。Key Phrase B1B=旧本文に対する3回の呼び出しがすべて未完成で、**現在の最終本文に対しては未生成**。Key Phrase A2=原driverが(F002文修正前の)A2本文に対して生成済み。
- 残作業(順番):
  (1) **A2記事全体final QA再実行**: 現行最終A2(`discovery/a2/article.md`=`reader_facing_article.txt`と同期していることを確認)に対し、既存正式QA(Fact Checker A'・Ledger Deviation Checker・Directional Precheck)を1回再実行し`a2/audit/post_fix_fact_qa.json`等を最新化。FAILの場合: 指摘がLedger修正で解消できる範囲なら限定修正(既存rewrite経路+diff QA)を最大1回→再QA。それでもFAILならSTOP。
  (2) **Key Phrase A2の最終本文整合確認**(API不要): `key_phrases/a2/keywords_canonicalized.json`の5件の`source_sentence`(または相当フィールド)が最終A2本文に**そのまま存在する**ことをローカル文字列照合で確認。1件でも不在なら、最終A2本文に対して`run_key_phrases()`を1回再実行(Validatorはそのまま)。
  (3) **Key Phrase B1B**: 最終B1B本文(`b1b/article.md`)に対し既存正式入口`run_key_phrases()`(前回driverと同じ呼び出し・同じValidator)を実行。これは「旧本文へのretry」ではなく**確定canonical本文への正規の初回生成**として扱う(旧3回は本文が変わったため無効)。構造不合格(`KEY_WORDS_STRUCTURE_INVALID`等)なら**もう1回だけ**再呼び出し(合計最大2回)。2回とも不合格なら、不合格理由(選ばれたphrase・Validatorのreason原文)を記録してSTOP(Validator変更はProduction QA変更でユーザー判断)。出力先は上書き事故防止のため`key_phrases/b1b_final/`(新規dir)へ書き、成功時のみ`key_phrases/b1b/`へ同期コピーし旧結果を`key_phrases/b1b_old_attempts/`へ退避。
  (4) 最終確認(API不要): jargon scan A2/B1B=0、Cross-Level Consistency突合表を最終テキストから再生成(前回の「F002 video watchers markerがF012『37 studies』に誤ヒット」する表示上の副作用は、markerを除外するかnote付記で解消し、引用文がすべて最終ファイル由来であることを明記)、`reader_facing_article.txt`/`reader_facing_article_b1b.txt`が`a2/article.md`/`b1b/article.md`と一致することを確認。
  (5) `production_set_cost.json`更新(Discovery Production 1生成セット総原価=前回まで¥435.52+本タスク実費。Key Phrase費を明記、50:50配賦なし)、`aggregate_usage.py`集計、`progress_log.md`1行追記。
- 費用上限: 本タスク¥70(A2全体QA≈¥25-30、限定修正発生時+¥15、KP B1B≤2回≈¥5、KP A2再実行発生時≈¥3。段階ごとに次段階見込み込みで事前判定するガード)。
- 禁止: Research全体再実行/仕様変更/新Validator・QA/Prompt改善/QA緩和/Validator変更/Factの意味変更/Git/SSOT/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`/前任driverの再実行/既存Key Phrase結果ファイルの上書き(必ず新dirへ)。
- STOP条件: 新Production仕様が必要/既存Gate緩和・変更が必要/Ledger修正で解消できない構造問題/費用上限¥70超過見込み/Key Phrase B1Bが2回とも不合格/最終的に人間判断しかできない品質問題。STOP時は「実施済み対応・残った問題・ユーザーが判断すべき具体的選択肢」を提示。

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

> Discovery: Ledger修正 → A2/B1該当文rewrite → 正式QA → canonical確定 → Key Phrase A2/B1生成 → 完成まで進める。既存仕様内で直せる個別修正は途中でユーザー判断を求めず、完成まで進めること。STOP条件: 新しいProduction仕様が必要/既存Gateを緩和・変更する必要がある/Ledger修正だけでは解消できない構造問題/想定を大きく超える追加コスト/最終的に人間判断しかできない品質問題。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_4T_DISCOVERY_COMPLETE_2.md` 全文(前回到達点)。
2. `er014_output/four_type_observation_01/discovery/run_discovery_complete_2.py` 全文(前回driver。final QA関数・Key Phrase呼び出し・費用ガード・operator escalation経路を再利用して`run_discovery_complete_3.py`を派生)。
3. `er014_output/four_type_observation_01/discovery/key_phrases/a2/keywords_canonicalized.json` 全文(source_sentence照合用)。
4. `er014_output/four_type_observation_01/discovery/a2/article.md`・`b1b/article.md` 全文(最終本文。Key Phrase照合・Cross-Level引用に必須)。
5. `er014_output/four_type_observation_01/discovery/production_set_cost.json` 全文。
6. `er014_output/four_type_observation_01/discovery/cross_level_consistency.md` 全文(marker誤ヒット箇所の特定)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- `discovery/run_discovery_complete_3.py`(新規driver、budget_jpy=70)。出力: `a2/audit/`最新化、`key_phrases/b1b_final/`(+成功時`key_phrases/b1b/`同期・`key_phrases/b1b_old_attempts/`退避)、`key_phrases/a2/`(再実行時のみ、旧は`key_phrases/a2_old/`へ退避)、`jargon_scan_final.json`、`cross_level_consistency.md`(再生成)、`run_result_complete_3.json`、`cost_summary_complete_3.json`、`observation_complete.json`、`production_set_cost.json`、`progress_log.md`。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE-CONT2.md --json-out docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE-CONT2_check.json`
2. 実行: `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_complete_3.py`(driver内でbudget_jpy=70固定。全文コマンドと固定値をRESULT_PACKETへ記録)
3. 集計: `.venv\Scripts\python.exe er014_output\four_type_observation_01\aggregate_usage.py --run-dir er014_output\four_type_observation_01\discovery --out er014_output\four_type_observation_01\discovery\observation_complete.json`
(回帰不要: Production/Trialコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-135/150末尾追記案(Discovery最終結果)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補ファイル一覧」(discovery/配下全体+delegation_log 3件+RESULT_PACKET 3件)を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_4T_DISCOVERY_COMPLETE_3.md`に: 1) 最終Status(A2記事/B1B記事/Key Phrase A2/Key Phrase B1B、それぞれOK/未完成)、2) A2記事全体final QA結果(Fact Checker verdict・残指摘・Ledger Deviation・Directional、限定修正の有無と旧→新)、3) Key Phrase A2(5件: 英語phrase/日本語gloss/出典文、最終本文との照合結果、再実行有無)、4) Key Phrase B1B(5件同上、呼び出し回数、Validator結果。不合格時はphrase・reason原文)、5) No Jargon最終、6) Cross-Level Consistency(最終テキスト引用、marker副作用の解消方法)、7) 同期確認(reader_facing_article*.txt = article.md)、8) model_id、9) **Discovery Production 1生成セット(共通Research/Ledger+A2+B1、Key Phrase込み)総原価=¥xx.xx**(内訳、本タスク実費)、10) API token、11) Open Item候補、12) commit対象候補一覧、13) T-0・事前指定外Read・STOP有無(STOP時は実施済み対応・残問題・選択肢)。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥70)
- [x] 並行タスク衝突回避あり(discovery/配下限定・Git操作なし・新dir出力)
