## 管理ID

PM-CLOSEOUT-CONSOLIDATION-131(4TYPE FOLLOWUP A/B/C+Voices可変Writerの統合、OPEN-151 Status訂正)
並行タスク衝突確認: 並行してEDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09(er013_*/er013_output/のみ、Git操作なし)が走る。本タスクはer013_*・`er013_output/`をaddしない・触らない。Git操作は本タスクのみ。

## 性質/到達上限Status/禁止事項

- 性質: Closeout統合(¥0)。(A)4TYPE補完A/B/Cの成果物(`er014_output/four_type_observation_01/{news,trend,discovery}/`)のGit記録、(B)**OPEN-151のStatus訂正**: Sonnet報告はPRODUCTION_WIREDだが、Fable照合でユーザー指定11項目のうち「Comment Contract整合(新規topic入口でComment未接続)」「Gate辞書整合(3V保守版Fact Safetyゲートが2Vの5区切り構造で構造的に不発)」が未充足、2V記事もREVIEW_REQUIRED+残存flagで3attempt上限到達のため**PARTIAL(Writer可変化は完了、Production path全体は未完)**へ訂正(OPEN_ITEMS/CURRENT_SPEC/DECISION_LOG/REPORTのplaceholder・Status表記を統一)、(C)比較ページ更新、(D)最終REPORT(4TYPE補完)作成、(E)SSOT反映(DECISION_LOG、OPEN-135/149/150への結果追記)、(F)transcript退避、(G)ACTIVE_TASK更新。
- 禁止: API呼び出し/記事の再生成・修正/Production・Trialコード変更/`run_project_regression.py --pattern`に`_test`を含まないglob/`git add -A`・`.`・`stash`・`clean`・`amend`・`rebase`・`force push`/er013系のadd/新規OPEN行の追加(候補はREPORTに列挙)/仕様Statusの格上げ。
- STOP条件: push失敗3回→報告。

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

> 最終成果物: News(A2既存/新規B1/A2・B1比較リンク/1 Production生成セット原価)、Trend(修正Ledger/再生成B1/再生成A2/Fact Checker結果/旧Factとの差分/1 Production生成セット原価)、Discovery(No Jargon修正版A2/新規・修正版B1/A2・B1 Key Phrase再生成/専門用語除去確認/1 Production生成セット原価)、Open Items(A-Family Fact Research最適化 MEDIUM/DEFERRED、No Jargon compliance instability LOW/DEFERRED)、Voices(2/3可変Writer Gate 3状況、PRODUCTION_WIRED未達の場合は不足項目を明示)。
> STOP条件: Ledger修正だけではTrend Fact矛盾を解消できない/Discovery No Jargon修正でFact意味が維持できない/新しいUSER_DECISION_REQUIREDが発生した→勝手に追加仕様を作らずSTOPして報告。
> コスト報告: PM_GOVERNANCE 15-8「Production 1生成セット総原価」主指標、50:50配賦禁止。Claude Code usageは9-10形式(別項目、週間利用枠換算が取得不能なら明記)。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_4T_NEWS_B1.md`、`docs/pm/RESULT_PACKET_4T_TREND_FIX.md`、`docs/pm/RESULT_PACKET_4T_DISCOVERY_FIX.md`、`docs/pm/RESULT_PACKET_VOICES_VAR.md` 各全文。
2. `er014_output/four_type_observation_01/{news,trend,discovery}/production_set_cost.json` 各全文、`er014_output/four_type_observation_01/voices/cost_summary.json`。
3. `er014_output/four_type_observation_01/trend/research/ledger_fix_diff.md` 全文、`er014_output/four_type_observation_01/discovery/rewrite_log.md` 全文。
4. `er014_output/four_type_observation_01/index.html`: Grep `<h2|<section|id=` → 構造のみ(更新用)。
5. `EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01_REPORT.md`: Grep `PRODUCTION_WIRED|placeholder|<commit|TBD|Comment Contract|不発` → Status表記・placeholder箇所のみ。
6. `docs/pm/tools/README.md`: Grep `collect_subagent_transcripts` → 使用法のみ。
7. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- **比較ページ更新** `er014_output/four_type_observation_01/index.html`: News=A2(既存)+B1(新規、369語、OK)/Trend=修正Ledger後のB1(OK)+A2(再生成後もFact Checker FAIL→NG、折りたたみで掲載し理由1行)+「旧run1」へのリンク/Discovery=No Jargon修正版A2+新規B1B(専門語0件、ただしA2/B1Bとも「60 students watched」がLedger精度不足によりFact Checker FAIL指摘中、Key Phrase未生成、と1行注記)/Voices=2V記事本文(Hook/Voice A/Voice B/Tension/Closing、395語、REVIEW_REQUIRED残存と1行注記)。各記事にTopic/Level/type/word count/statusのみ。
- **最終REPORT** `EDITORIAL-4TYPE-FOLLOWUP-01_REPORT.md`(新規root): 節=News/Trend/Discovery/Open Items/Voices/コスト表/Claude Code usage/STOP・UDR一覧。コスト表は15-8標準: `| Family | Production 1生成セット | 総原価 |` News=共通Research/Ledger+A2+B1=¥98.32/Trend=共通Research/Ledger+A2+B1(初回run1 ¥87.98+修正run ¥75.25=¥163.23、うち「修正Ledger後の1セット」として¥123.98[Research¥48.73+修正run¥75.25])/Discovery=共通Research/Ledger+A2+B1=¥261.57(Key Phrase未実施、うち修正・B1追加¥157.32)/Voices=正式1生成セット(Research/Ledger+2V Writer/QA/Gate)=¥99.01。直接費内訳は各production_set_cost.jsonから機械分離できる分のみ、50:50配賦なし。Claude Code usage(9-10形式): 委任ごとのtool uses(A 52/B 78/C 81/D 54/E 157)と所要秒(A 912/B 1479/C 2042/D 277/E 2686)、cumulative_usageは退避後に`measure_delegation_task.py`で実測して「Claude Code development/audit usage(参考)」欄に記載、週間利用枠換算: 取得不能。
- **SSOT訂正・追記**: `OPEN_ITEMS.md`: Grep `^\| OPEN-151 ` → 行内の`PRODUCTION_WIRED`表記を「PARTIAL(Writer 2/3可変化・3Vバイト不変・2V実生成は完了[commit d5c4df57/a3a68cd3]。未充足: Comment Contract整合[新規topic入口でComment未接続、3Vと同じ限界]/Gate辞書整合[3V保守版Fact Safetyゲートが2Vの5区切り構造で構造的に不発]/2V記事はREVIEW_REQUIRED+残存flagで3attempt上限到達。Fable判定2026-09-14: PRODUCTION_WIREDとしない)」へ訂正し、placeholder(`<commit>`等)を実値で置換。`CURRENT_SPEC.md`: Grep `OPEN-151|2/3可変` → 同様にPRODUCTION_WIRED表記をPARTIAL+未充足3点へ訂正。`DECISION_LOG.md`: Grep `EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT` → 当該エントリの結果表記をPARTIALへ訂正(履歴として「Sonnet報告PRODUCTION_WIRED→Fable照合でPARTIAL」と明記)、placeholder置換。REPORT本体(`EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01_REPORT.md`)の冒頭に「Fable照合注記: 到達StatusはPARTIAL(理由3点)」を追記(本文は改変しない)。
- `DECISION_LOG.md`: Grep `PM-CLOSEOUT-CONSOLIDATION-130` → 直後(既存のVoicesエントリの後)に新エントリ「PM-CLOSEOUT-CONSOLIDATION-131」(下記①)+索引1行。
- `OPEN_ITEMS.md`: Grep `^\| OPEN-135 ` → 末尾に「(2026-09-14 4TYPE補完) News B1追加OK(セット¥98.32)。Trend: Ledger修正[Google XRメガネ2026-05-19発表]後B1 OK、A2は再生成2回後もFact Checker FAIL[Galaxy XR既提供との矛盾]→STOP(UDR)。Discovery: No Jargon修正A2/B1B完了(専門語0)、B1B追加OK、ただしLedger F002の精度不足[N=60中動画視聴37]でA2/B1BともFact Checker FAIL指摘→Key Phrase未実施、STOP(UDR)。」。Grep `^\| OPEN-149 ` → 末尾に「(2026-09-14) 4TYPE補完でFact Checker A'再実行が1回¥25〜50を占め、Discovery修正の総費用¥157.32の約半分がA'。Trend/Discoveryとも上流Ledger精度不足を最終A'が検出した事例2件(本Open Itemの論点を裏付け)。」。Grep `^\| OPEN-150 ` → 末尾に「(2026-09-14) 個別修正完了: A2専門語12→0、B1B 1→0(既存rewrite経路、Fact意味維持確認)。検出語一覧はEDITORIAL-4TYPE-FOLLOWUP-01_REPORT.md参照。」
- transcript退避: taskId `afb1b9e8ae1922d96,a3d6494875a3d9c62,ab932907e63391e5c,a77459a021a55d10b,a4ec0dbcc6b868d3e,a0476de3de929f06a,a19d58276a52ec60f,abea07a3485438139,a59133a0b41e1b0e3,a4b02507e3f411d54,afe3ca0bc8494e7b8`(未退避分のみ。既存ファイルがあればskip)。
- `docs/pm/ACTIVE_TASK.md`: 固定ヘッダで上書き(管理ID=本タスク、UDR-blocking=Trend A2追加Ledger修正の可否/Discovery Ledger F002修正+rewrite+KPの可否/Voices 2V記事のREVIEW_REQUIRED残存の扱い、UDR-deferred=OPEN-148/149/150/134等、APPROVED未配線=OPEN-151(PARTIAL、未充足3点)/OPEN-83/145/146(+OPEN-120)、STOP条件=なし、次アクション=Trial-09完了待ち→ユーザー報告、報告単位Status: 4TYPE補完=PARTIAL(UDR 3件) / Voices可変Writer=PARTIAL / Family C=Trial-09進行中)。
- RESULT_PACKETは`docs/pm/RESULT_PACKET.md`へ上書き。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-131.md --json-out docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-131_check.json`
2. 退避: `.venv\Scripts\python.exe docs\pm\tools\collect_subagent_transcripts.py --tasks-dir "C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks" --subagents-dir "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents" --transcripts-dir "docs\pm\transcripts" --only-task-ids afb1b9e8ae1922d96,a3d6494875a3d9c62,ab932907e63391e5c,a77459a021a55d10b,a4ec0dbcc6b868d3e,a0476de3de929f06a,a19d58276a52ec60f,abea07a3485438139,a59133a0b41e1b0e3,a4b02507e3f411d54,afe3ca0bc8494e7b8 --apply`
3. 集計(A/B/C/D/Eの5件): `.venv\Scripts\python.exe docs\pm\tools\measure_delegation_task.py --task-id afb1b9e8ae1922d96`(以下 a3d6494875a3d9c62 / ab932907e63391e5c / a77459a021a55d10b / a4ec0dbcc6b868d3e についても同形式で実行)
4. `git status --porcelain` → 明示add → commit → `git push origin main`(classifierブロック時は同一コマンド最大3回再試行)。
(回帰不要: コード変更なし。)

## SSOT追記文

① DECISION_LOG新エントリ: 「2026-09-14: PM-CLOSEOUT-CONSOLIDATION-131(4TYPE補完統合)。News B1追加OK(News 1生成セット¥98.32)。Trend: 限定Verificationで公式発表(blog.google 2026-05-19)確認→Ledger修正→B1 OK、A2は2回再生成後もFact Checker FAIL(Galaxy XR既提供との矛盾、記事側の一般化)→ユーザーSTOP条件『Ledger修正だけでは解消できない』該当でSTOP(UDR)。Discovery: No Jargon個別修正A2/B1B(既存rewrite経路、専門語0、Fact意味維持)、B1B追加OK、ただしLedger F002精度不足(N=60中動画視聴37)によるFact Checker FAILがA2/B1B共通→Key Phrase未実施、STOP(UDR)。Voices可変Writer: Sonnet報告PRODUCTION_WIRED→Fable照合でPARTIAL(Comment Contract未接続/3Vゲート2V不発/2V記事REVIEW_REQUIRED残存)。費用: 4TYPE補完合計¥359.74(A ¥28.16+B ¥75.25+C ¥157.32+E ¥99.01)、Claude Code usage別記。」

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add: `er014_output/four_type_observation_01/news/`(新規分: run_news_b1b.py、b1b/、reader_facing_article_b1b.txt、cross_level_consistency.md、production_set_cost.json、observation_b1b.json、cost_summary_b1b.json、raw_usage_log_b1b.jsonl等)、`er014_output/four_type_observation_01/trend/`(新規・更新分: run_trend_fix_regen.py、research/[修正版・v1_before_fix・ledger_fix_diff.md]、run1_before_fix/、再生成a2/・b1b/、reader_facing_article*.txt、run_result.json、cost_summary.json、raw_usage_log.jsonl、observation_fix.json、production_set_cost.json、trend_gate_checklist.json)、`er014_output/four_type_observation_01/discovery/`(新規・更新分: run_discovery_fix_b1b_kp.py、a2/、a2_before_fix/、b1b/、reader_facing_article*.txt、jargon_scan_*.json、rewrite_log.md、cost_summary_fix.json、production_set_cost.json、run_result_fix.json、observation_fix.json、raw_usage_log*.jsonl)、`er014_output/four_type_observation_01/index.html`、`er014_output/four_type_observation_01/progress_log.md`、`EDITORIAL-4TYPE-FOLLOWUP-01_REPORT.md`、`EDITORIAL-B-FAMILY-VOICES-VARIABLE-VOICE-COUNT-PRODUCTION-WIRING-01_REPORT.md`(注記追記)、`docs/pm/RESULT_PACKET_4T_NEWS_B1.md`、`docs/pm/RESULT_PACKET_4T_TREND_FIX.md`、`docs/pm/RESULT_PACKET_4T_DISCOVERY_FIX.md`、`docs/pm/RESULT_PACKET_VOICES_VAR.md`(未commitなら)、`docs/pm/delegation_log/EDITORIAL-4TYPE-FOLLOWUP-0{1,2,3}-*.md`+`_check.json`、`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-131.md`+`_check.json`、`docs/pm/transcripts/`新規分、`OPEN_ITEMS.md`、`DECISION_LOG.md`、`CURRENT_SPEC.md`。er013系・`writer_generic_before.py`・無関係既存差分はaddしない。音声等大容量なし想定(あれば除外し報告)。
- コミットメッセージ: `PM-CLOSEOUT-CONSOLIDATION-131: 4TYPE補完(News B1追加/Trend Ledger修正再生成/Discovery No Jargon修正+B1B)のGit記録+OPEN-151をPARTIALへ訂正+最終REPORT+比較ページ更新` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`へ: 1) commit hash(full)・push結果、2) add件数、3) 比較ページ・REPORTの相対パス、4) コスト表(15-8形式)の実値、5) Claude Code usage(5委任のcumulative_usage実測・tool uses・秒)、6) OPEN-151訂正箇所(ファイル・行)、7) SSOT追記位置、8) transcript退避結果(件数)、9) T-0・事前指定外Read、10) STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0)
- [x] 並行タスク衝突回避あり(er013不可・並行側Git操作なし)
