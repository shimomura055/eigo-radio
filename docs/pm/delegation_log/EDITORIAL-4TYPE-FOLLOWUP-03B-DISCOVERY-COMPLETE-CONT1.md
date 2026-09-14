## 管理ID

EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE(継続、Fable修正指示1回目)
並行タスク衝突確認: 並行して Voices OPEN-151完成(er012_*・`.../voices/`・SSOT・Git担当)が走る。本タスクは`er014_output/four_type_observation_01/discovery/`配下のみを書き、SSOT・Git・ACTIVE_TASK・RESULT_PACKET.mdを触らない。前任エージェントは停止済み(driver `run_discovery_complete.py`は`overall_status=COMPLETE`で完走済み、RESULT_PACKET未作成)。前任がもし`docs/pm/RESULT_PACKET_4T_DISCOVERY_COMPLETE.md`を作成していても上書きせず、本タスクは`docs/pm/RESULT_PACKET_4T_DISCOVERY_COMPLETE_2.md`(新規)へ書く。新driverは`run_discovery_complete_2.py`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 既存仕様内の個別修正でDiscovery A2/B1+Key Phraseを**完成**させる継続。ユーザー方針: 「既存仕様内で直せる個別修正は途中でユーザー判断を求めず完成まで進める」。
- 前回driver結果(`discovery/run_result_complete.json`、Fable確認済み): F002 Verification=AMBIGUOUS(条件表上flow18+disrupted19=37名が動画視聴、baserate23名は非視聴。ただし論文が編集気づき4名除外と記すためN計算が不整合→「除外前の正確な視聴者数を一意に確定するのは避けるべき」)。F011=VERIFIED(46名が正、41名は別研究)。A2/B1BともF011文はrewrite解決、**F002文はLocal Rewriteが`resolved=false, human_review_required=true`**。A2最終QA: Fact Checker PASS/LEDGER_COMPLIANT。**B1B最終QA: Fact Checker FAIL**(retry未適用)。Key Phrase A2=CANONICALIZATION_PASS+REDUNDANCY_PASS。**Key Phrase B1B=KEY_WORDS_STRUCTURE_INVALID**(1回のみ)。jargon A2/B1B=0。本タスク前回実費¥100.88。
- 残作業(順番): 
  (1) **F002文の修正完了**: Ledger F002がAMBIGUOUS結果を反映した記述(「動画視聴者数を特定の数字で断定しない。条件表上は37名(18+19)が動画視聴、23名は非視聴、除外後の内訳は論文内で不整合」)になっているか確認し、未反映なら修正。A2/B1Bの該当文(例: B1B「Sixty students watched a six-minute conversation.」)を、**既存Local Rewrite経路のhuman_review escalation後の正式手順**(`er010_ledger_local_rewrite_09`および呼び出し元での「人手/operator修正テキストを与えてdiff QA(`apply_diff_qa_to_resolved_rewrite`: Fact Checker A'+Ledger Deviation)で受理判定する」経路)で修正する。修正文は人数を断定しない表現(例: "In a second experiment, students watched a six-minute video of a conversation." / A2側も同趣旨)とし、効果方向・4秒沈黙・「多くは沈黙に気づかなかった」等の他のFact要素は変更しない。**operator修正テキストを与える経路が既存コードに存在しない場合のみSTOP**(存在有無をRESULT_PACKETにコード箇所付きで記録)。修正前テキストは`a2_before_f002_fix/`・`b1b_before_f002_fix/`へ退避。
  (2) **B1B Fact Checker FAILの原因確認**: `discovery/b1b/audit/`配下の最新fact_check JSONからFAIL理由(原文)を読み、F002文起因なら(1)で解消後にB1B最終QA(Fact Checker・Ledger Deviation・Directional)を再実行。F002以外の理由なら、Ledger修正で解消できる範囲で限定修正(既存rewrite経路)を最大1回、それでもFAILならSTOP。A2はPASS済みのため、(1)でA2を修正した場合のみA2最終QAを再実行。
  (3) **Key Phrase B1B**: 既存正式入口(`run_key_phrases`、前回driverと同じ呼び出し)を最大3回まで再呼び出し(内部仕様・Validatorは変更しない。Trial-09と同じ「入口の再呼び出し」方式)。3回とも構造不合格ならSTOPとし、失敗理由(`KEY_WORDS_STRUCTURE_INVALID`の詳細)を記録。
  (4) jargon scan最終(A2/B1B=0確認)、Cross-Level Consistency突合表を**最終テキスト**で作成(`discovery/cross_level_consistency.md`。Trendで「rewrite前テキストを引用した突合表」が発生したため、必ず最終ファイルからの引用であることを明記)。
  (5) `production_set_cost.json`更新(Discovery Production 1生成セット総原価=Research ¥58.37+A2初回 ¥45.88+前回修正 ¥157.32+前回driver ¥100.88+本タスク実費。Key Phrase費を明記、50:50配賦なし)、`aggregate_usage.py`集計、`progress_log.md`1行追記。
- 費用上限: 本タスク¥90(段階ごとに次段階見込み込みで事前判定するガード。diff QA×2レベル・B1B最終QA・KP B1B×3を想定)。
- 禁止: Research全体再実行/仕様変更/新Validator・QA/Prompt改善/QA緩和/Factの意味変更/retry上限変更/Git/SSOT/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`/前任driverの再実行。
- STOP条件: 新Production仕様が必要/既存Gate緩和・変更が必要/Ledger修正で解消できない構造問題/費用上限¥90超過見込み/operator修正経路が存在しない/最終的に人間判断しかできない品質問題。STOP時は「実施済み対応・残った問題・ユーザーが判断すべき具体的選択肢」を提示。

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

1. `er014_output/four_type_observation_01/discovery/run_discovery_complete.py` 全文(前任driver。rewrite経路・QA・Key Phrase呼び出し・費用ガードを再利用して`run_discovery_complete_2.py`を派生)。
2. `er014_output/four_type_observation_01/discovery/run_result_complete.json` L1-70(結果要約。上記に転記済みだが実値確認用)。
3. `er014_output/four_type_observation_01/discovery/research/verified_fact_ledger.txt`: Grep `F002|F011` → 該当fact範囲のみ。
4. `er014_output/four_type_observation_01/discovery/b1b/audit/`: Glob `*fact*.json` → 最新FAILの`verdict`/`contradictions`/`unsupported`部分のみ。
5. `er014_output/four_type_observation_01/discovery/a2/article.md`・`b1b/article.md`: Grep `students watched|Sixty|60 |46 |six-minute` → 該当行のみ。
6. `er010_ledger_local_rewrite_09.py`: Grep `^def |human_review|manual|operator|escalat|apply_diff_qa_to_resolved_rewrite` → human_review後の正式escalation経路(operator修正テキスト受け入れ関数・引数)の該当範囲のみ。
7. `er003_v1_n3_01_articles_generate.py`: Grep `human_review_required|manual_rewrite|operator|escalat` → Production側でhuman_review後にどう扱うか(該当範囲のみ)。
8. `er014_output/four_type_observation_01/discovery/key_phrases/b1b/keywords_runtime_metadata.json` 全文(STRUCTURE_INVALID理由)。
9. `er014_output/four_type_observation_01/discovery/production_set_cost.json` 全文。

## 事前指定Grep一覧+追記位置・更新位置の手順

- driver `discovery/run_discovery_complete_2.py`(新規): F002 operator修正+diff QA(A2/B1B)→B1B(必要ならA2)最終QA→KP B1B最大3回→jargon最終→Cross-Level→cost。出力: `discovery/a2/`・`b1b/`(最終canonical)、`reader_facing_article.txt`・`reader_facing_article_b1b.txt`(最終同期)、`a2_before_f002_fix/`・`b1b_before_f002_fix/`、`rewrite_log.md`(追記: F002旧→新、経路名、diff QA結果)、`jargon_scan_final.json`、`cross_level_consistency.md`、`key_phrases/b1b/`、`run_result_complete_2.json`、`cost_summary_complete_2.json`、`observation_complete.json`、`production_set_cost.json`。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE-CONT1.md --json-out docs\pm\delegation_log\EDITORIAL-4TYPE-FOLLOWUP-03B-DISCOVERY-COMPLETE-CONT1_check.json`
2. 実行: `.venv\Scripts\python.exe er014_output\four_type_observation_01\discovery\run_discovery_complete_2.py`(driver内でbudget_jpy=90固定。全文コマンドと固定値をRESULT_PACKETへ記録)
3. 集計: `.venv\Scripts\python.exe er014_output\four_type_observation_01\aggregate_usage.py --run-dir er014_output\four_type_observation_01\discovery --out er014_output\four_type_observation_01\discovery\observation_complete.json`
(回帰不要: Production/Trialコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETにOPEN-135/150末尾追記案を記載。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補ファイル一覧」(前任driver分も含めdiscovery/配下全体)を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_4T_DISCOVERY_COMPLETE_2.md`に: 1) 最終Status(A2/B1B/Key Phrase A2/B1B)、2) Ledger修正内容(F002/F011 旧→新、Verification source URL・内容。前任分も含め通しで記載)、3) A2/B1B rewrite差分(F011・F002それぞれ旧文→新文、使用経路[Local Rewrite / operator escalation]、diff QA結果)、4) Fact Checker(A2/B1B最終verdict・残指摘)、5) Ledger Deviation・diff QA・Directional、6) No Jargon最終0件確認、7) Cross-Level Consistency(最終テキスト引用)、8) Key Phrase A2/B1B(英語phrase/日本語gloss/位置、Validator結果、B1B再呼び出し回数)、9) actual model_id、10) **Discovery Production 1生成セット(共通Research/Ledger+A2+B1、Key Phrase込み)総原価=¥xx.xx**(内訳、前任driver¥100.88+本タスク実費)、11) API token、12) Open Item候補、13) commit対象候補一覧、14) T-0・事前指定外Read・STOP有無(STOP時は実施済み対応・残問題・選択肢)。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥90)
- [x] 並行タスク衝突回避あり(discovery/配下限定・Git操作なし・別RESULT_PACKET名)
