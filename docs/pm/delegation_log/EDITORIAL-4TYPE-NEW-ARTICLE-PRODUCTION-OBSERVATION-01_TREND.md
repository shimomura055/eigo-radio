## 管理ID

EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01(記事2/4: Trend Synthesis)
並行タスク衝突確認: 並行タスクなし(Family C Trial-07・News記事は完了済み)。本タスクもGit操作を行わない(4記事完了後にFableがCONSOLIDATIONで統合)。SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は編集しない。RESULT_PACKETは`docs/pm/RESULT_PACKET_4T_TREND.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 既存Production記事タイプ(Trend Synthesis、`PRODUCTION_WIRED`)の**正常生成観測**。新仕様Trialではない。生成成功を理由にいかなる仕様Statusも変更しない。
- Topic: **The end of the smartphone as the main interface**。意味: 「スマートフォンが消える」予測ではなく、**スマートフォン画面が人間とデジタル世界をつなぐ中心インターフェースではなくなっていく可能性**をTrendとして扱う。signal候補例(固定角度にしない): AI assistants/AI agents/smart glasses/voice・earbuds/wearables/ambient computing/cars・homes becoming interfaces。Trend Synthesisの現行正式仕様に従い**複数signalから一つのTrendを構成**する。
- Ledger供給(Fable判断、News記事1/4と同じ先例踏襲): Research/Verification(`vfl01.build_researcher_prompt`/`run_researcher`相当+`build_verification_prompt`/`run_verification`相当、OpenAI web_search)でVerified Fact Ledgerを作成→Trend Production正式初回経路`er006_pool_pilot_01_writer.py::run_writer_for_theme(..., editorial_mode="trend_synthesis", trend_gate_checklist=...)`(→`run_one_pattern`)へ投入。Researcherへ渡すtopic文には「複数の独立したsignal(製品・利用動向・企業方針等)を、それぞれ出典付きで収集する」旨を英語で含める(Sonnet自身の知識で事実を補わない)。CURRENT_SPEC L760「手動供給のみ」との表記不一致はOpen Item候補として記録済み(News R1)。
- Trend Gate 6条件+Mode判定2問チェックリスト(CURRENT_SPEC L761: 自動判定なし、呼び出し時に手動判定結果を渡し`run_metadata.json`へ記録): Sonnetが**作成済みLedgerの内容に基づいて**各条件を正直に判定し(根拠1行ずつ)、その判定結果を`trend_gate_checklist`として渡す。条件を満たさないと判定した場合は生成を強行せずSTOPして報告(Gate定義は下記Read 1で確認)。
- レベル: A2のみ。音声化(TTS)なし。日本語タイトル供給(CURRENT_SPEC L763)は本文生成には不要なため行わない(TTSを行わないため)。
- **仕様変更禁止**: Prompt改善/QA追加/retry方式変更/新Validator/Story構造変更/Model routing変更/Production wiring変更/QA緩和は一切行わない。問題は可能な範囲で生成を完了し「Open Item候補」として報告。Fact Safety上の重大問題で正常生成不能な場合のみSTOP。
- 費用上限: 本記事¥130(Research込み・retry込み)。超過見込みで停止し報告。
- 禁止操作: `git add/commit/push`/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`/er013_*・SSOT編集/Production関数のmonkeypatch・再実装。
- STOP条件: Trend Gate不成立/Fact Safety重大問題/費用上限/正式関数の実行にコード修正が必要と判明(修正せず報告)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(T-0の保存名は`docs/pm/delegation_log/EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_TREND.md`とする。)
---

## ユーザー指示(原文)

> B. Trend Topic: The end of the smartphone as the main interface。意味: 「スマートフォンが消える」という予測ではなく、スマートフォン画面が、人間とデジタル世界をつなぐ中心インターフェースではなくなっていく可能性をTrendとして扱う。例となるsignal候補: AI assistants/AI agents/smart glasses/voice / earbuds/wearables/ambient computing/cars / homes becoming interfaces。ただし、これをそのまま記事角度として固定しないこと。Trend Synthesisの現行正式仕様に従い、複数signalから一つのTrendを構成してください。
> 各記事について、現在の正式QAを通常どおり実施する。QAを今回のために緩めないこと。5-A 量産時1記事生成API原価(retryなし部分/retry追加分/Research・Ledger生成/Writer/QA/rewrite・regeneration)。6. API token使用量(provider/model_id/input/output/cached/total/calls)。7. Claude Code側の利用量: 取得できる実測値/取得できない値/代替指標を明確に分ける。8. 各記事開始前後でusage snapshot。

## 事前指定Read一覧

1. `CURRENT_SPEC.md` L740-765(Trend Synthesis Production配線表: 配線方式・Mode指定・Focus Module・Engagement・retry整合・Research/Ledger供給・Trend Gateチェックリスト記録)。Trend Gate 6条件+Mode判定2問の**定義本文**はGrep `Trend Gate|Mode判定` でCURRENT_SPEC内の定義位置を特定し該当範囲のみRead。
2. `er006_pool_pilot_01_writer.py`: Grep `^def run_writer_for_theme|editorial_mode|trend_gate_checklist|run_metadata` → シグネチャ・引数の渡し方・出力先の該当範囲のみRead。
3. `er014_output/four_type_observation_01/news/run_news_a2.py` 全文(前記事のdriver。Research→Verification→Ledger保存部分を流用し、記事生成呼び出しを`run_writer_for_theme(editorial_mode="trend_synthesis")`へ置き換える)。
4. `er014_output/four_type_observation_01/aggregate_usage.py`: Grep `add_argument|def ` → 引数と関数一覧のみ(再利用)。
5. `docs/pm/tools/README.md`: Grep `measure_delegation_task|collect_subagent_transcripts` → 使用法の該当範囲のみRead(Step 0用)。
6. `docs/pm/RESULT_PACKET_4T_NEWS.md` L1-40(News記事のobservation書式・費用区分の付け方を揃えるため)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- **Step 0(Claude Code側利用量の観測、¥0)**: 前記事(News)の委任2件のtranscriptを退避し累積usageを集計する。(a)`collect_subagent_transcripts.py`でtaskId `a1c286e44afabde21`(News再委任)を`docs/pm/transcripts/`へ退避(`ae39a6a0807fea6e1`[News初回]は退避済み)。(b)`measure_delegation_task.py`(README記載の使用法)で両transcriptの累積input/output/cache_read/cache_write tokens・tool_uses・turn数を集計し、`er014_output/four_type_observation_01/claude_usage_log.md`(新規)に表で記録: 列=記事/委任ID(短縮8桁)/役割(初回STOP・再委任)/累積input/累積output/cache_read/cache_write/tool_uses/turns/所要秒。併記: Fableから通知された最終ターン値(News初回: tokens 93,138・tool_uses 39・410秒/News再委任: tokens 144,148・tool_uses 78・1,345秒)。取得できない値(セッション利用枠delta等)は「取得不能」と明記し推定しない。
- driver: `er014_output/four_type_observation_01/trend/run_trend_a2.py`(新規、薄いrunner。Research→Verification→Ledger保存→Trend Gateチェックリスト判定の記録→`run_writer_for_theme(editorial_mode="trend_synthesis", trend_gate_checklist=<判定結果>)`。費用上限¥130ガード)。出力先`er014_output/four_type_observation_01/trend/`(`research/verified_fact_ledger.txt`+生JSON、`trend_gate_checklist.json`[各条件の判定と根拠1行]、`reader_facing_article.txt`、QA結果json、`run_metadata.json`、`raw_usage_log.jsonl`、`cost_summary.json`)。正式pathの出力先が固定されている場合はそちらで生成し完了後にこのdirへコピー(元は残す)。
- 集計: `aggregate_usage.py --run-dir er014_output/four_type_observation_01/trend --out .../trend/observation.json`(News記事と同じ書式)。工程別区分(research/verification/writer/各QA/retry)はNews R1と同じ手法(logging_contextラベルまたはresponse_id突合)で分ける。
- 中間ログ: `er014_output/four_type_observation_01/progress_log.md`に「Trend: 開始/終了時刻・費用・token・status」を1行追記。
- `docs/pm/RESULT_PACKET_4T_TREND.md`は新規作成。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_TREND.md --json-out docs\pm\delegation_log\EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_TREND_check.json`
2. Step 0退避: `.venv\Scripts\python.exe docs\pm\tools\collect_subagent_transcripts.py --tasks-dir "C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks" --subagents-dir "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents" --transcripts-dir "docs\pm\transcripts" --only-task-ids a1c286e44afabde21 --apply`
3. Step 0集計: `.venv\Scripts\python.exe docs\pm\tools\measure_delegation_task.py <README記載の引数で docs\pm\transcripts\a1c286e44afabde21_recovered.jsonl と docs\pm\transcripts\ae39a6a0807fea6e1_recovered.jsonl を対象>`(実際に使った全文コマンドをRESULT_PACKETへ記録)
4. 生成: `.venv\Scripts\python.exe er014_output\four_type_observation_01\trend\run_trend_a2.py`(driver内でtopic/out_dir/level="a2"/editorial_mode="trend_synthesis"/budget_jpy=130を固定。全文コマンドと固定値をRESULT_PACKETへ記録)
5. 集計: `.venv\Scripts\python.exe er014_output\four_type_observation_01\aggregate_usage.py --run-dir er014_output\four_type_observation_01\trend --out er014_output\four_type_observation_01\trend\observation.json`
(回帰実行は不要: Production/Trialコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETに「Open Item候補」を列挙。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補ファイル一覧」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_4T_TREND.md`に: 1) status(生成成功/PARTIAL/STOP)と使用path(根拠行)、2) 記事: level・word count・`reader_facing_article.txt`相対パス、3) Ledger: CONFIRMED件数・signal数・Verification結果、4) Trend Gate 6条件+Mode判定2問の判定と根拠、5) 主要QA結果(Fact Checker/Ledger Deviation/Local Rewrite・diff QA発火有無/Point Overlap・Value QA各attempt/Directional Precheck)・retry回数・fallback有無、6) actual model_id(provider別)、7) 費用: 量産時1記事単価(Standard同期・今回実測)=¥xx.xx、内訳(Research/Ledger・Writer・QA・rewrite/regeneration・retry追加分・retryなし部分)、開発・検証費=¥0(あれば別計上)、8) API token: provider/model_id/input/output/cached/total/calls(通常/retry)、9) Step 0のClaude Code側集計結果(表、取得不能項目の明記)、10) Open Item候補、11) commit対象候補一覧、12) T-0結果・事前指定外Read(理由付き)・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり(measure_delegation_task.pyの引数はREADME確認後に全文記録)
- [x] 禁止事項・費用上限あり(¥130)
- [x] 並行タスク衝突回避あり(並行なし・Git操作なし)
