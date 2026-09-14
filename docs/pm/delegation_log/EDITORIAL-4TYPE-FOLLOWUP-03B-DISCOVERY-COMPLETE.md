## 管理ID

EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE
並行タスク衝突確認: 並行して Trend完成(`.../trend/`)・Voices OPEN-151完成(er012_*・`.../voices/`・SSOT・Git)・Family C Trial-09(er013)が走る。本タスクは`er014_output/four_type_observation_01/discovery/`配下のみを書き、SSOT・Git・ACTIVE_TASK・RESULT_PACKET.mdを触らない。RESULT_PACKETは`docs/pm/RESULT_PACKET_4T_DISCOVERY_COMPLETE.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 既存仕様内の個別修正で**Discovery A2/B1+Key Phraseを完成**させる(新仕様Trialではない)。ユーザー方針(2026-09-14): 「Ledger修正→A2/B1該当文rewrite→正式QA→canonical確定→Key Phrase A2/B1生成→完成まで進める。既存仕様内で直せる個別修正は途中でユーザー判断を求めず、完成まで進めること」。
- 手順: (1)限定Verification(既存`vfl01`Verification、web_search)で F002(Koudenburg et al. 2011 Study 2: 参加者60名のうち動画視聴はfluent 18+disrupted 19=37名、23名はベースライン)と「46名 vs 公開抄録n=41」(6分30秒の沈黙研究)を確認(Research全体の再実行禁止)。(2)Ledger修正(旧版を`research/verified_fact_ledger_v1_before_fix.txt`として保存、差分を`research/ledger_fix_diff.md`に記録。F002のscope/numeric_value/notes_for_writerを「動画を見たのは37名」が明確になるよう修正、46/41は確認結果に従い断定度を整合)。(3)A2(`discovery/a2/article.md`=No Jargon修正済み版)とB1B(`discovery/b1b/article.md`)の該当文(「60 students watched…」「Sixty students watched…」「46 students」等)を**既存正式rewrite経路**(`er010_ledger_local_rewrite_09.rewrite_ng_item`+`apply_diff_qa_to_resolved_rewrite`、修正Ledger基準)で修正。No Jargon修正済み状態を維持(専門語scanをbefore/afterで再実行し0件を確認)。修正前テキストを`a2_before_fact_fix/`・`b1b_before_fact_fix/`へ退避。(4)正式QA(Fact Checker・Ledger Deviation・diff QA・Directional)をA2/B1Bで再実行。(5)A2/B1BのCross-Level Consistency突合表。(6)**canonical article確定**(A2/B1Bとも Fact Checker が FAIL でない状態。REVIEW_REQUIREDは指摘内容を記録し、Ledger修正で解消できるものは最大1回追加修正、できないものは記録して進む)。(7)**Key Phrase生成**: 現行正式Key Phrase Production仕様(CURRENT_SPECで特定、A2/B1Bそれぞれ)で生成、既存Validator(選定・日本語gloss・平易さ・redundancy・article整合)を通常どおり実行。追加QAは作らない。
- 費用上限: ¥170(限定Verification+rewrite×2レベル+QA再実行+Key Phrase×2。Fact Checker A'が1回¥25〜50かかる前提で、A'再実行はA2/B1B各1回を基本とし、追加修正時のみ+1回)。段階ごとに次段階見込み込みで事前判定するガードにすること(前回は段階間チェックのため超過後停止した)。
- 禁止: Research全体再実行/仕様変更/新Validator・QA/Prompt改善/QA緩和/Factの意味変更/Git/SSOT/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`。
- STOP条件(ユーザー指定): 新Production仕様が必要/既存Gateの緩和・変更が必要/Ledger修正だけでは解消できない構造問題/想定を大きく超える追加コスト(上限¥170)/最終的に人間判断しかできない品質問題/Key Phrase正式pathがDiscovery B1Bに未対応(未承認実装が必要)。STOP時は「実施済み対応・残った問題・ユーザーが判断すべき具体的選択肢」を提示。

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

> Discovery: 方針は確定です。Ledger修正 → A2/B1該当文rewrite → 正式QA → canonical確定 → Key Phrase A2/B1生成 → 完成まで進める。F002の視聴者数37 vs 60/46 vs 41の不一致を限定Verificationして正しいLedgerへ修正。その後、A2/B1B双方の該当文を既存rewrite経路で修正。No Jargonは既に個別修正済みなので、その状態を維持。Fact Checker / Ledger Deviation / diff QA等、既存の正式QAを通し、canonical article確定後にKey Phraseを再生成してください。既存仕様内で直せる個別修正は途中でユーザー判断を求めず、完成まで進めること。
> 最終REPORT(Discovery): Ledger修正内容/A2/B1 rewrite差分/Fact Checker/Ledger Deviation/No Jargon確認/Key Phrase A2/B1/Production 1生成セット総原価/最終Status。

## 事前指定Read一覧

1. `er014_output/four_type_observation_01/discovery/run_discovery_fix_b1b_kp.py` 全文(前回driver。rewrite経路・Key Phrase呼び出し部分を再利用し`run_discovery_complete.py`を派生。費用ガードを事前判定型に修正)。
2. `er014_output/four_type_observation_01/discovery/research/verified_fact_ledger.txt` 全文(修正対象)。
3. `er014_output/four_type_observation_01/discovery/a2/audit/post_fix_fact_qa.json` 全文(FAIL指摘の原文・URL)。
4. `docs/pm/RESULT_PACKET_4T_DISCOVERY_FIX.md` 全文(前回結果・Key Phrase入口の調査結果)。
5. `CURRENT_SPEC.md`: Grep `Key Phrase` → A2/B1BのKey Phrase Production仕様(スクリプト・関数・Validator・出力形式)の定義範囲のみRead。
6. `er003_v1_n3_01_scaffold_generate.py`: Grep `^def .*key_phrase|^def run_key_phrases|KEY_PHRASE` → 入口・引数のみ(前回調査で特定済みなら該当範囲)。
7. `er014_output/four_type_observation_01/discovery/production_set_cost.json` 全文(累積更新用)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- driver: `discovery/run_discovery_complete.py`(新規。限定Verification→Ledger修正→A2/B1B rewrite→QA→Cross-Level→Key Phrase。費用上限¥170、事前判定ガード)。
- 出力: `discovery/a2/`(最終canonical)・`discovery/b1b/`(同)・`reader_facing_article.txt`・`reader_facing_article_b1b.txt`・`a2_before_fact_fix/`・`b1b_before_fact_fix/`・`research/verified_fact_ledger.txt`(修正版)+`_v1_before_fix.txt`+`ledger_fix_diff.md`・`rewrite_log.md`(追記: 事実修正の旧→新)・`jargon_scan_final.json`・`cross_level_consistency.md`・`key_phrases/a2/`・`key_phrases/b1b/`(正式pathの出力形式+Validator結果)・`cost_summary_complete.json`・`observation_complete.json`・`production_set_cost.json`(更新: Discovery Production 1生成セット(共通Research/Ledger+A2+B1)総原価=Research ¥58.37+A2初回 ¥45.88+前回修正 ¥157.32+本タスク。完成セット内訳とKey Phrase費を明記、50:50配賦なし)。
- 中間ログ: `progress_log.md`に「Discovery complete: …」1行追記。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE.md --json-out docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE_check.json`
2. 実行: `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_complete.py`(driver内でledger_path/out_dir/budget_jpy=170を固定。全文コマンドと固定値をRESULT_PACKETへ記録)
3. 集計: `.venv\Scripts\python.exe er014_output\four_type_observation_01\aggregate_usage.py --run-dir er014_output\four_type_observation_01\discovery --out er014_output\four_type_observation_01\discovery\observation_complete.json`
(回帰不要: Production/Trialコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-135/150末尾追記案(Discovery完成結果)を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補ファイル一覧」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_4T_DISCOVERY_COMPLETE.md`に: 1) 最終Status(A2/B1B/Key Phrase A2/B1B)、2) Ledger修正内容(旧→新、Verification source URL・内容)、3) A2/B1B rewrite差分(旧文→新文、使用経路、diff QA結果、Fact意味維持)、4) Fact Checker(A2/B1B verdict・残指摘)、5) Ledger Deviation・diff QA発火・Directional、6) No Jargon確認(jargon scan最終0件)、7) Cross-Level Consistency、8) Key Phrase A2/B1B(一覧: 英語phrase/日本語gloss/位置、Validator結果)、9) actual model_id、10) **Discovery Production 1生成セット(共通Research/Ledger+A2+B1、Key Phrase込み)総原価=¥xx.xx**(完成セット内訳、本タスク実費)、11) API token、12) Open Item候補、13) commit対象候補一覧、14) T-0・事前指定外Read・STOP有無(STOP時は実施済み対応・残問題・選択肢)。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥170、事前判定ガード)
- [x] 並行タスク衝突回避あり(discovery/配下限定・Git操作なし)
