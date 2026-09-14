## 管理ID

EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01(記事4/4: Voices 2 Voices)
並行タスク衝突確認: 並行タスクなし(News/Trend/Discovery記事は完了済み)。本タスクもGit操作を行わない。SSOT・`docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`は編集しない。RESULT_PACKETは`docs/pm/RESULT_PACKET_4T_VOICES.md`(新規)。

## 性質/到達上限Status/禁止事項

- 性質: 既存Production記事タイプ(B-Family Voices、2 Voices=Voice A/B、`PRODUCTION_WIRED` 2026-09-09、`er012_b_family_production_runner_01.py` level="a2")の**正常生成観測**。新仕様Trialではない。生成成功を理由にいかなる仕様Statusも変更しない。
- 事前確認済み(News記事担当の`path_survey.md`、CURRENT_SPEC L637-658): 2 Voices(Voice A=Algieba/Voice B=Erinome、5区切りHook/Voice A/Voice B/Tension/Closing、Narrator見出し=Aoede)がProduction配線済み。3 Voicesは`APPROVED_FOR_PRODUCTION`だが未配線(5項目未実装)。ユーザーは2 Voicesを希望しており、**2 Voicesは正式pathでそのまま生成できる**(Trial扱い不要、Production仕様の書き換え不要)。着手時にCURRENT_SPEC該当行で再確認し、もし2 Voices正式pathの実行に未承認の実装変更が必要と判明した場合は実装せずSTOP。
- Topic: **Is personalized news good for us?**。狙い: 単純な善悪ではなく、(a) personalizationが情報取得を便利・relevantにする側面、(b) filter bubble/worldview narrowing/editorial controlなどの懸念、の双方が強く成立する記事。ただし既存Voices仕様(Voice A/Bの役割・構造・Prompt)を優先し、テーマの狙いはResearch topic文とテーマ入力で伝える(Promptは変更しない)。
- Ledger供給(Fable判断、他3記事と同じ先例踏襲): B-Family Productionが要求する入力(Verified Fact Ledger/Reference等)をCURRENT_SPEC・runnerの引数から確認し、Research/Verification(`vfl01`+web_search、News driverと同一構造)で作成して投入。Sonnet自身の知識で事実を補わない。B-Family固有の前処理(例: Ledger canonical spelling[OPEN-146]、Key Phrase等)が正式pathに含まれるならそのまま実行。
- 3V保守版Fact Safetyゲート(`VOICE_FACT_SAFETY_GATE_MODE_DEFAULT=True`、B-Family既定ON、OPEN-120 runtime evidence待ち): 今回の生成で**自然発火した場合はその証跡(発火箇所・verdict・処理)を必ず記録**する(これはOPEN-120が待っている実データ証跡になる)。発火しなければ「未発火」と記録。
- レベル: A2(正式runnerの`level="a2"`)。音声化(TTS)なし(runnerにTTS工程が含まれる場合は本文生成まででTTS工程を無効化できるフラグがあればそれを使い、無ければTTS工程の直前で止められる引数を探す。**runnerの改造は禁止**。どうしても本文のみで止められない場合はTTSを実行せずSTOPし、本文生成までの費用で報告)。
- **仕様変更禁止**: Prompt改善/QA追加/retry方式変更/新Validator/Story構造変更/Model routing変更/Production wiring変更/QA緩和は一切行わない。問題は可能な範囲で生成を完了し「Open Item候補」として報告。fail-closed(GATE_BLOCKED等)で停止した場合は再生成せず結果を記録。
- 費用上限: 本記事セット(2 Voices)¥160(Research込み・retry込み)。超過見込みで停止し報告。
- 禁止操作: `git add/commit/push`/`run_project_regression.py --pattern`に`_test`を含まないglob/PATH上の素`python`/er013_*・SSOT・er012_*編集。
- STOP条件: 2 Voices正式pathに未承認の実装変更が必要/Fact Safety重大問題/費用上限。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

---
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
(T-0の保存名は`docs/pm/delegation_log/EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_VOICES.md`とする。)
---

## ユーザー指示(原文)

> D. Voices Topic: Is personalized news good for us? 今回は: 2 Voices で生成してください。ただし作業開始前にCURRENT_SPEC / Production実装を確認し、2 Voicesが現在の正式仕様・正式pathでサポートされている場合→そのProduction pathを使用/3 Voicesのみが正式Production仕様で、2 Voicesが未承認/Trial専用の場合→新しいProduction仕様を勝手に実装しない、2 Voicesを今回限定Trialとして生成可能ならその範囲で実施し、Statusを明記、実装変更が必要ならSTOPして報告。ユーザーは今回の記事について2 Voicesを希望していますが、これは既存Production仕様を書き換えてよいという承認ではありません。Voicesのテーマは、単純な善悪ではなく、personalizationが情報取得を便利・Relevantにする側面/filter bubble / worldview narrowing / editorial controlなどの懸念の双方が強く成立する記事を狙う。ただし既存Voices仕様を優先してください。
> 各記事について、現在の正式QAを通常どおり実施する。QAを今回のために緩めないこと。5-A 量産時1記事生成API原価(Voicesが2 Voiceを1記事セットとして生成する場合は、2 Voicesセット全体/可能ならVoice 1 / Voice 2内訳)。6. API token使用量。7. Claude Code側の利用量。8. 各記事開始前後でusage snapshot、中間ログ保存。

## 事前指定Read一覧

1. `CURRENT_SPEC.md` L637-658(B-Family Voices Production仕様: 構造・Voice割当・runner・3V未配線の記述)。
2. `er012_b_family_production_runner_01.py`: Grep `^def |add_argument|level|ledger|reference|tts|audio|__main__` → runnerの入口・引数・入力ファイル(Ledger/Reference/theme)・TTS工程の位置・本文生成までで止める手段の該当範囲のみRead。
3. `er012_b_family_voices_a2_production_01.py`: Grep `^def |ledger|VOICE_FACT_SAFETY|gate` → 入力とゲート呼び出し箇所のみRead。
4. `er012_b_family_editorial_type_registry_01.py`: Grep `VOICE_FACT_SAFETY_GATE_MODE_DEFAULT|def get_editorial_type_a2` → 該当範囲のみRead。
5. `er014_output/four_type_observation_01/news/run_news_a2.py`: Grep `def |researcher|verification|verified_fact_ledger` → Research→Verification→Ledger保存の関数範囲のみRead(流用)。
6. `er014_output/four_type_observation_01/aggregate_usage.py`: Grep `add_argument|def ` → 引数・関数一覧のみ(再利用。B-Family固有のaudit形式でuncategorizedが出た場合は手動補完し、ツール改修はしない)。
7. `docs/pm/RESULT_PACKET_4T_DISCOVERY.md` L1-60(書式・費用区分に揃える)。

## 事前指定Grep一覧+追記位置・更新位置の手順

- **Step 0(Claude Code側利用量、¥0)**: Discovery委任(taskId `a7fead3da74d3b08e`)のtranscriptを退避し`measure_delegation_task.py --task-id a7fead3da74d3b08e`で集計、`er014_output/four_type_observation_01/claude_usage_log.md`にDiscovery行を追加(Fable通知の最終ターン値: tokens 141,324・tool_uses 69・1,314秒を併記)。
- driver: `er014_output/four_type_observation_01/voices/run_voices_2v_a2.py`(新規。Research→Verification→Ledger保存→B-Family正式runner/関数の呼び出し。monkeypatch・再実装禁止。費用上限¥160ガード)。出力先`er014_output/four_type_observation_01/voices/`(`research/verified_fact_ledger.txt`+生JSON、Voice A/Voice Bを含むreader-facing本文[`reader_facing_article.txt`=5区切り全文、加えて`voice_a.txt`/`voice_b.txt`に分割保存]、各QA・ゲート生JSON、`raw_usage_log.jsonl`、`cost_summary.json`)。正式pathの出力先が固定ならそちらで生成し完了後コピー。
- 集計: `aggregate_usage.py --run-dir er014_output/four_type_observation_01/voices --out .../voices/observation.json`。費用は2 Voicesセット全体と、可能ならVoice A/Voice B別(Writer呼び出しがVoice別ならresponse_id突合で分離、共通工程[Research/QA]は「共通」として明記)。
- 中間ログ: `er014_output/four_type_observation_01/progress_log.md`に「Voices: 開始/終了時刻・費用・token・status」を1行追記。
- `docs/pm/RESULT_PACKET_4T_VOICES.md`は新規作成。

## 実行コマンド全文

(すべて `C:\Users\tensh\eigo-radio` で実行)
1. T-0: `.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_VOICES.md --json-out docs\pm\delegation_log\EDITORIAL-4TYPE-NEW-ARTICLE-PRODUCTION-OBSERVATION-01_VOICES_check.json`
2. Step 0退避: `.venv\Scripts\python.exe docs\pm\tools\collect_subagent_transcripts.py --tasks-dir "C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\tasks" --subagents-dir "C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\294958fe-da6e-491c-8a02-4f864d8195c8\subagents" --transcripts-dir "docs\pm\transcripts" --only-task-ids a7fead3da74d3b08e --apply`
3. Step 0集計: `.venv\Scripts\python.exe docs\pm\tools\measure_delegation_task.py --task-id a7fead3da74d3b08e`
4. 生成: `.venv\Scripts\python.exe er014_output\four_type_observation_01\voices\run_voices_2v_a2.py`(driver内でtopic/out_dir/level="a2"/budget_jpy=160/TTS無効を固定。全文コマンドと固定値をRESULT_PACKETへ記録)
5. 集計: `.venv\Scripts\python.exe er014_output\four_type_observation_01\aggregate_usage.py --run-dir er014_output\four_type_observation_01\voices --out er014_output\four_type_observation_01\voices\observation.json`
(回帰実行は不要: Production/Trialコード変更なし。)

## SSOT追記文

本タスクではSSOTを編集しない。RESULT_PACKETに「Open Item候補」を列挙(3Vゲート発火の有無を含む)。

## Git(明示add対象・コミットメッセージ・trailer)

本タスクではGit操作を行わない。RESULT_PACKETに「commit対象候補ファイル一覧」を列挙。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_4T_VOICES.md`に: 1) status(OK/GATE_BLOCKED/STOP)と使用path(2 Voices正式pathである根拠行、Trial扱いではないことの明記)、2) 記事: level・5区切り各語数・合計語数・相対パス(全文/voice_a/voice_b)、3) Ledger: CONFIRMED件数、4) 主要QA結果(B-Family正式QA: repetition QA/Fact Safety 3V保守版ゲート[発火有無・verdict]/Ledger Deviation/Fact Checker/その他runnerが実行する全ゲート)・retry回数・fallback有無、5) actual model_id(provider別)、6) 費用: 量産時1記事単価(Standard同期・今回実測)=2 Voicesセット¥xx.xx、Voice A/Voice B内訳(可能なら)、共通工程内訳(Research/Ledger・Writer・QA・rewrite/regeneration・retry追加分・retryなし部分)、開発・検証費=¥0(2V確認等で量産外の追加API callがあれば別計上)、7) API token(provider/model_id/input/output/cached/total/calls、通常/retry)、8) Step 0のClaude Code側集計(Discovery行)、9) Open Item候補(3Vゲート runtime evidenceの有無を明記)、10) commit対象候補一覧、11) T-0結果・事前指定外Read(理由付き)・STOP有無。

## Fable自己チェック(送信前)

- [x] Read一覧に行範囲/Grepパターンあり
- [x] 追記位置手順あり
- [x] コマンドに引数実値あり
- [x] 禁止事項・費用上限あり(¥160)
- [x] 並行タスク衝突回避あり(並行なし・Git操作なし)
