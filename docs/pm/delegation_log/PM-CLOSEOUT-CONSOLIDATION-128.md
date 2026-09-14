## 管理ID

PM-CLOSEOUT-CONSOLIDATION-128(EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01の統合)
並行タスク衝突確認: 並行タスクなし。Git操作は本タスクのみ。

## 性質/到達上限Status/禁止事項

- 性質: Closeout統合(¥0、API呼び出しなし)。4記事観測(News=OK/Trend=B1 OK・A2 NG_REVIEW_REQUIRED/Discovery=OK/Voices=STOP[USER_DECISION_REQUIRED])の成果物を、(A)ユーザー確認用比較ページ、(B)root REPORT(費用3区分・API token表・Claude Code利用量表・Open Item候補)、(C)SSOT(DECISION_LOG記録、OPEN_ITEMSは既存行への追記のみ、新規Open Item登録はしない=ユーザー判断待ち)、(D)transcript退避1件、(E)Git commit/push、(F)ACTIVE_TASK更新、にまとめる。
- 禁止: API呼び出し/記事の再生成・修正/Production・Trialコードの変更/`run_project_regression.py --pattern`に`_test`を含まないglob/`git add -A`・`.`・`stash`・`clean`・`amend`・`rebase`・`force push`/新規OPEN-1xx行の追加(候補はREPORTに列挙するだけ)/いかなる仕様Statusの変更(4記事生成はTrialではないため、VALIDATED/APPROVED等を付与しない)。
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

> 4. ユーザー確認用Artifact: 4記事を一度に読み比べられる比較ページを作成してください。最低限: News/Trend/Discovery/Voices Voice 1/Voices Voice 2 のReader-facing本文全文を掲載。各記事について、Topic/Level/article type/word count程度だけを簡潔に併記。QAの大量の技術情報は本文比較ページには載せすぎないこと。ユーザーがまず記事そのものを読めることを優先。直接開けるリンクを報告してください。
> 5. コスト計測: 5-A 量産時1記事生成API原価(News/Trend/Discovery/Voices、retryなし部分/retry追加分/Research・Ledger生成/Writer/QA/rewrite・regeneration、表記「量産時1記事単価(Standard同期・今回実測)」)/5-B 開発・Trial/検証費(別計上)。
> 6. API token使用量: provider/actual model_id/input/output/cached/total/calls、記事単位、retryは通常生成分/retry追加分を可能なら分離。
> 7. Claude Code側のトークン・利用量: 取得できる実測値/取得できない値/代替指標を明確に分ける。代替指標として最低限、Claude Code tool call数/Read/Grep等のtool use数/delegation数/4記事全体のsession usage delta。記事生成API tokenとClaude Code tokenを同じ表に合算しないこと。
> 11. 最終報告形式: A記事/B品質(status・主要QA・retry・word count)/C量産コスト表/D API token表/E Claude Code利用量表/F費用区分(量産API原価・開発・Trial/検証費・Claude Code subscription usage)/G問題(品質・コスト・retry・routing・Voices仕様、Open Item候補として)。
> 12. 4記事生成成功を理由に新仕様をVALIDATED/APPROVEDへ変更しない。Voices 2VがTrial扱いになる場合のみGate 1を明示。

## 事前指定Read一覧

1. `docs/pm/RESULT_PACKET_4T_NEWS.md`、`docs/pm/RESULT_PACKET_4T_TREND.md`、`docs/pm/RESULT_PACKET_4T_DISCOVERY.md`、`docs/pm/RESULT_PACKET_4T_VOICES.md` 各全文(集約元)。
2. `er014_output/four_type_observation_01/claude_usage_log.md` 全文、`er014_output/four_type_observation_01/progress_log.md` 全文、`er014_output/four_type_observation_01/path_survey.md` 全文。
3. `er014_output/four_type_observation_01/{news,trend,discovery}/observation.json` 各全文(表の数値源)。
4. `er014_output/four_type_observation_01/news/reader_facing_article.txt`、`trend/reader_facing_article_b1b.txt`、`trend/reader_facing_article.txt`(A2、NG)、`discovery/reader_facing_article.txt`(比較ページへ全文転記)。
5. `docs/pm/tools/README.md`: Grep `collect_subagent_transcripts` → 使用法のみ。
6. `docs/pm/PM_BRIEF.md` L133-157(ACTIVE_TASK固定ヘッダ書式)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- **(A) 比較ページ** `er014_output/four_type_observation_01/index.html`(新規、自己完結HTML): 上部に4記事の一覧表(Topic/Level/article type/word count/status のみ)。本文セクション順: News(A2、OK)/Trend(B1、OK。続けてA2本文も折りたたみで掲載し「Fact Checker FAIL→NG_REVIEW_REQUIRED(Google XRメガネ発売時期の矛盾)、Production採用不可」と1行注記)/Discovery(A2、OK)/Voices(未生成: 「2 Voicesで新規トピックを書き起こす正式Production pathが存在しない(a2/b1 runnerは承認済み固定記事の音声再配線専用、新規Writerは3V専用)。ユーザー判断待ち」と簡潔に記載、Voice 1/Voice 2欄は空)。QAの技術詳細は載せない(REPORTへのリンクのみ)。
- **(B) root REPORT** `EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_REPORT.md`(新規)。節構成はユーザー最終報告形式A〜Gに合わせる:
  - A 記事(比較ページの相対パス+4記事の1〜2行説明)
  - B 品質(記事別: status/主要QA verdict/retry回数/word count。Trend A2のFAIL内容、Discovery Point Oneの専門語密度[Fable所見: "parasympathetic activity / fMRI acoustic noise"等がA2超過の疑い、人間確認要]、Trend B1にもA2をFAILさせた「XRメガネはまだ開発段階のデモ」記述が含まれREVIEW_REQUIRED止まりで通過した点[Ledger鮮度の疑い]を記載)
  - C 量産コスト表(必須書式): `| Type | 量産時実測単価 | retry追加分 | 備考 |` News ¥70.16(retry 0)/Trend ¥87.98(B1+A2合算、retry追加分≈¥1.89参考値、A2はNG)/Discovery ¥104.25(retry 0、内訳はobservation.jsonから)/Voices 2V 未生成(¥0)。各行の備考に内訳(Research・Writer・QA・rewrite)。合計。表題「量産時1記事単価(Standard同期・今回実測)」。
  - D API token表(必須書式): `| Type | Model | Input | Output | Cached | Total | Calls |`(observation.jsonの実値。retry分離は可能な範囲、Trendは注記)
  - E Claude Code利用量表(必須書式): `| Type | Claude usage/tokens | Tool uses | Delegations | 備考 |`。Claude usage/tokensには`measure_delegation_task.py`のcumulative_usage(4項目合算、transcript実測)を入れ、input/output/cache内訳は「取得不能」と明記。Delegations(Fable→Sonnet委任回数、Fable実測): News 2(初回STOP+再委任)/Trend 1/Discovery 1/Voices 1。Fable側tool call数(Fable自己申告、概算): News 12/Trend 2/Discovery 1/Voices 3。4記事全体のsession usage delta: 「取得不能(Fable/SonnetからClaude Codeのセッション利用枠・/cost・/usage値を取得する手段がない)」と明記し、代替として全委任のcumulative_usage合計と、Fable通知の最終ターン値(News初回93,138/News再委任144,148/Trend 124,254/Discovery 141,324/Voices 81,961)を「最終ターン値であり累積ではない」と注記して併記。Voices委任(aed06c1b062a335c3)のcumulative_usageは(D)の退避後に`measure_delegation_task.py --task-id aed06c1b062a335c3`で実測して記入。
  - F 費用区分: 量産API原価合計(¥262.39=70.16+87.98+104.25)/開発・Trial・検証費(¥0。News初回STOP・Voices STOPとも¥0)/Claude Code subscription usage(上記E、金額換算不能)。
  - G 問題・Open Item候補(登録はしない): (1)2 Voices新規トピックWriterの正式Production path不在[USER_DECISION_REQUIRED、Voices記事未生成]、(2)CURRENT_SPEC L760「手動供給のみ」表記と先例(Research正式経路で新規Ledger作成)の不一致、(3)`run_writer_for_theme`がB1+A2常時生成でA2単独不可、(4)Trend Gate 6条件の独立定義がCURRENT_SPEC本体に無い、(5)Cost Loggerのstageタグが粗く工程別原価を機械分離できない(response_id突合で事後分類)、(6)Trend A2 Fact Checker FAIL=QA正常動作だが、B1にも同記述が残りREVIEW_REQUIREDで通過→Ledger鮮度(Research時点の情報が発表で古くなる)問題、(7)Discovery Point OneのA2レベル超過の疑い、(8)OPEN-120 3Vゲートruntime evidenceは今回未取得、(9)OPEN-148該当のOverlap retryはDiscoveryで未発生(追加事例なし)、(10)Directional Precheckが3記事すべてでDIRECTION_REVIEW_REQUIRED(既知の常時REVIEW挙動)。
  - H Status/Gate: 4記事生成は新仕様Trialではなく仕様Status変更なし。Voices 2Vは生成未着手のためGate 1判定なし(USER_DECISION_REQUIRED)。
- **(C) SSOT**: `DECISION_LOG.md`: Grep `PM-CLOSEOUT-CONSOLIDATION-127` → 直後に新エントリ「PM-CLOSEOUT-CONSOLIDATION-128」(下記②)+索引1行。`OPEN_ITEMS.md`: Grep `^\| OPEN-135 ` → 行末尾に「(2026-09-14、4TYPE観測) Discovery S2で新規Topic『Why can silence feel uncomfortable?』をResearch経路+正式関数でA2生成、status OK、retry 0、¥104.25。」を追記。Grep `^\| OPEN-148 ` → 行末尾に「(2026-09-14) 4TYPE観測のDiscovery生成ではOverlap retry未発生(追加事例なし)。」を追記。Grep `^\| OPEN-120 ` → 行末尾に「(2026-09-14) 4TYPE観測ではVoices生成未着手のため3Vゲートruntime evidence未取得。」を追記。新規OPEN行は追加しない。
- **(D) transcript退避**: taskId `aed06c1b062a335c3`(Voices)。
- **(F) ACTIVE_TASK.md**: 固定ヘッダで上書き(管理ID=本タスク、UDR-blocking=4TYPE Voices: 2V新規Writer path不在の対応方針、UDR-deferred=OPEN-148(HIGH)/OPEN-134等、APPROVED未配線=OPEN-83/145/146(+OPEN-120)、STOP条件=なし、次アクション=ユーザー報告、未回答報告=Family C Trial-07(人間評価1〜2)、報告単位Status: 4TYPE観測=3/4完了・Voices UDR / Family C=Trial-07 VALIDATED評価待ち / Discovery S2=PRODUCTION_WIRED)。
- RESULT_PACKETは`docs/pm/RESULT_PACKET.md`へ上書き。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-128.md --json-out docs\pm\delegation_log\PM-CLOSEOUT-CONSOLIDATION-128_check.json`
2. 退避: `.venv\Scripts\python.exe docs\pm\tools\collect_subagent_transcripts.py --tasks-dir "C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks" --subagents-dir "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents" --transcripts-dir "docs\pm\transcripts" --only-task-ids aed06c1b062a335c3 --apply
3. 集計: `.venv\Scripts\python.exe docs\pm\tools\measure_delegation_task.py --task-id aed06c1b062a335c3`
4. `git status --porcelain` → 明示add → commit → `git push origin main`(classifierブロック時は同一コマンド最大3回再試行)。
(回帰実行は不要: Production/Trialコード変更なし。)

## SSOT追記文

② DECISION_LOG新エントリ: 「2026-09-14: PM-CLOSEOUT-CONSOLIDATION-128(EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01)。4記事タイプの正常生成観測: News(AI regulation vs AI race)A2 OK ¥70.16/Trend(The end of the smartphone as the main interface)B1 OK・A2 Fact Checker FAIL→NG_REVIEW_REQUIRED ¥87.98/Discovery S2(Why can silence feel uncomfortable?)A2 OK ¥104.25/Voices 2V(Is personalized news good for us?)未生成=2 Voices新規トピックWriterの正式Production path不在でSTOP(USER_DECISION_REQUIRED)。Ledgerは先例(DECISION_LOG L941、CAR-T/wake-before-alarm)に従いResearch正式経路で作成(Fable判断、仕様変更なし)。量産API原価合計¥262.39、開発・検証費¥0、Claude Code側はtranscript実測cumulative_usage(内訳・セッション枠deltaは取得不能)。仕様Status変更なし。Open Item候補10件はREPORT G節(登録はユーザー判断待ち)。詳細: `EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_REPORT.md`。」

## Git(明示add対象・コミットメッセージ・trailer)

- 明示add: `er014_output/four_type_observation_01/`(一式: path_survey.md、progress_log.md、claude_usage_log.md、aggregate_usage.py、index.html、news/・trend/・discovery/配下[driver・research・記事・QA json・cost・observation]、voices/配下があれば)、`EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_REPORT.md`、`docs/pm/RESULT_PACKET_4T_NEWS.md`、`docs/pm/RESULT_PACKET_4T_TREND.md`、`docs/pm/RESULT_PACKET_4T_DISCOVERY.md`、`docs/pm/RESULT_PACKET_4T_VOICES.md`、`docs/pm/delegation_log/EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_NEWS.md`+`_check.json`、同`_NEWS_R1`2件、同`_TREND`2件、同`_DISCOVERY`2件、同`_VOICES`2件、`docs/pm/delegation_log/PM-CLOSEOUT-CONSOLIDATION-128.md`+`_check.json`、`docs/pm/transcripts/a1c286e44afabde21_recovered.jsonl`、`a5bdd52c4daad7ab8_recovered.jsonl`、`a7fead3da74d3b08e_recovered.jsonl`、`aed06c1b062a335c3_recovered.jsonl`(未commit分のみ)、`OPEN_ITEMS.md`、`DECISION_LOG.md`。無関係既存差分はaddしない。音声等大容量ファイルは含めない(あれば除外して報告)。
- コミットメッセージ: `PM-CLOSEOUT-CONSOLIDATION-128: 4記事タイプ正常生成観測(News/Trend/Discovery生成、Voices 2V path不在でUDR)+比較ページ+費用・token・Claude利用量REPORT` の後に空行、末尾に
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01THnbjj6FiMbJtrKdFteoE4`

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET.md`へ: 1) commit hash(full)・push結果、2) add件数、3) 比較ページ・REPORTの相対パス、4) C/D/E表の実値(REPORTからそのまま転記)、5) Voices委任のcumulative_usage実測値、6) SSOT追記位置、7) T-0・事前指定外Read、8) STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥0)
- [x] 並行タスク衝突回避あり(並行なし)
