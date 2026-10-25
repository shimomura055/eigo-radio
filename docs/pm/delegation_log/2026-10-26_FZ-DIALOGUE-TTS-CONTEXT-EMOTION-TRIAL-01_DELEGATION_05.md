## 管理ID
FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_05(2026-10-26 JST、追加2作品のPhase 1b=Fable感情レビュー結果の反映→TTS生成(48 call)→解析→試聴ページ公開→3作品横断整理。SSOT本体の編集はしない)。並行タスク: FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01 委任_01が稼働中で、共有SSOT(`OPEN_ITEMS.md`/`CURRENT_SPEC.md`/`DECISION_LOG.md`/`docs/pm/ACTIVE_TASK.md`/`docs/pm/REPORT_LEDGER.md`/`docs/pm/USER_DECISION_REGISTER_01.md`)の編集権とX runner出力・`user_test/family_x_*`を所有している。**本委任は共有SSOTを編集せず、追記文案をRESULT_PACKETに記載するのみ**(8-Y SSOT編集の直列化)。本委任の所有=`docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/`・`er118_*`・`er118_output/fz_dialogue_context_tts_trial_02/`・`user_test/fz_dialogue_context_trial_02/`・`docs/pm/delegation_log/2026-10-26_FZ-*`・`docs/pm/RESULT_PACKET_FZDC5.md`。gitは`git commit --only <paths>`(index.lock競合時は30秒待って再試行、3回失敗なら未commitで報告)。X runnerプロセスには触れない(TTS APIのrate共有はあるが別プロセス・別出力で競合しない)。

## 性質/到達上限Status/禁止事項
- 性質: Trial(DEV専用経路、Production変更0)。到達上限: VALIDATED(限定)の候補提示まで(Status確定とFable評価はFable。ユーザー試聴判断を残す)。Production配線・採用なし。
- 禁止: Production file/Prompt/閾値/reuse key/Gate/flagの変更、事前登録基準(`PREREGISTERED_CRITERIA_02.md`)の変更(追加分析は「事前登録外」として別節)、感情情報の書き換え(Fable判定は下記のとおり。LLM出力文言の編集禁止)、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。
- 費用上限: 上限¥30(Guardrail、ユーザー承認の追加Trial上限=2作品合計。既使用0.1938円を含む)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する——**ただし本件はユーザー明示の上限30円のため超過は不可**。先読みguard(実績+次clip見積>Cap)で停止したら、その時点の生成済みarmで解析へ進み、2 take完結できなかったclipを明記して報告する。暴走疑い時(想定外の大量API発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない)はSTOPし、原因・既使用額・想定追加額・残作業を報告する。
- Opus独立技術レビューGate: 非該当(Round 1 `OPUS_REVIEW_01.md`を再利用。新しい処理フローなし)。
- 時間見込み: 全体約60〜75分(review反映5分、gen-session 2作品直列 各約5〜8分、analyze/page 10分、横断整理・docs 20分、Git 5分)。並列化: 2作品のgen-sessionはcost log共有のCap判定遅延を避けるため**直列**(委任_04推奨どおり)。解析・ページ雛形は生成完了を待たず準備可。
- 費用/日次: 当日(JST 2026-10-26)既使用JPY約0.4(出典: RESULT_PACKET_FZDC4=0.37円時点。X委任_01が並行で消費中、起動前に`py docs/pm/tools/daily_dev_cost_01.py`で実測)/残JPY約999/本委任見積JPY約27(根拠: 48 TTS call×約0.53円+ASR 1.2円+retry予備、BUDGET_PLAN_02.md、上限=Guardrail 30円)/改善見込み中/承認区分: C:承認済みscope内(ユーザー2026-10-26指示、30円)。
- 前委任(委任_04)のQDC記録: 目的=選定・費用計画・設計差分・感情LLM/結果=完了(2作品16件、ACCEPTED 12/NO_EXPLICIT_CUE 3/DISCARDED 1、test 54 PASS、実費0.1938円)/次の一手=本委任。Fable受入記録(Gate 7): 当初目的(ユーザー原文逐語)=「追加2作品で同様の比較を実施し、前後の文脈や登場人物の感情をTTSへ渡すことで、セリフの自然さ・感情表現が実際に改善するか検証してください。」/最終成果物=SELECTION_02/BUDGET_PLAN_02/BUDGET_LOG_02/DESIGN_02/EMOTION_CANDIDATES_02.md、er118改修(commit 948e29a5c)/証拠=RESULT_PACKET_FZDC4.md、EMOTION_CANDIDATES_02.md全16件をFableが読了/一致=選定基準(6〜10件/作品、2語以下は1件、感情多様性)・30円内計画・方式同一・事前登録無変更/不一致=なし(怒りの明示例は原文に無く対象外と記録済み)/判定=ACCEPTED(Phase 0/1aとして)。判定整合: 重大NG=なし/主因=なし/是正対象=なし/STOP理由=なし/提示=Phase 1bへ。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`、ユーザー正式決定、費用上限[Cap]を伴う全委任で常時有効): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。禁止事項/性質欄の費用上限記載は次の定型文に従う。「上限¥X(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」旧来の「上限¥X、超えそうなら実行前STOP」のみの記載(継続条件・STOP条件の書き分けが無いもの)は使用しない。既存7-5(4)「想定外の全再生成が判明したらAPI実行前にSTOP」は本T-3の「暴走疑い時のSTOP」に該当する条件として維持する(置き換えではない)。ユーザー承認済みの総予算・個別run上限・STOP条件を優先し、Fable/Workerが独自に過度に厳しい停止条件を追加しない(2026-10-05)。

## ユーザー指示(原文)
`docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01_USER_02.md`(逐語保存済み)。本委任に関わる要点: 「各条件2takeを基本」「前回の事前登録評価基準は結果に合わせて緩めないでください。追加分析を行う場合は元の判定と区別してください」「機械指標だけで主観的な音声品質を最終決定せず、ユーザー試聴による比較判断を残してください」「今回の追加Trial予算上限：30円」「『賢者の贈り物』の既存Trial結果とも比較できるようにする」「本Trialの結果が良好でも、Productionへの配線は行わず」。

## Fable感情レビュー結果(16件。EMOTION_CANDIDATES_02.mdを全件読了のうえ決定。これを`emotion_review.json`へ転記する)
- open_window: part1_c7=accept(NO_EXPLICIT_CUE、状態行なしのまま)/part1_c10=accept/part1_c12=accept/part2_c4=accept/part2_c6=accept/part3_c8=accept(NO_EXPLICIT_CUE)/part3_c9=accept/part3_c11=accept。
- monkeys_paw: part1_c4=accept/part1_c13=accept/part1_c15=accept(sceneの"At home"は直前の「After their visitor left」から自然に導ける範囲とFable判断。観察として記録)/part2_c2=accept(NO_EXPLICIT_CUE)/part2_c6=**discard**(決定論検査DISCARDEDのとおり中立、規則は変えない)/part2_c8=accept("distressed"は強度語denyを通過し「Her face was wet with tears」で根拠あり)/part2_c10=accept/part3_c1=accept。
- `summary_ja`はEMOTION_CANDIDATES_02.mdの「場面(日本語・選定時)」の内容に合う事実ベースの短文とする(Sonnet下書きがそれに沿っていればそのまま可。原文にない感情語を足さない)。
- Fable観察(記録のみ、変更不要): open_window part2_c6で決定論manner_words「stared」と直後地の文(Veraの恐怖)が叔母のセリフCONTEXTに入る。設計どおり(Round 1と同一抽出)だが、結果解釈時に留意。

## KPI provenance欄
機械指標(話速・F0幅・RMS・ASR一致・leakage・comparison_valid)は全て fresh(本委任の生成分)。①(Production既存clip)は reuse(読取専用、Production記録)。E2E自己確認: No(Trial、Production初回pathではない)。

## Opus台帳更新
該当なし(OPUS_REVIEW_01の指摘は委任_02で反映済み)。

## 事前指定Read一覧
- `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/DESIGN_02.md` §3(指標割当)・§7(委任_05手順)
- `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/PREREGISTERED_CRITERIA_02.md` §3・§5・§6
- `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/EVAL_01.md` §2・§6(Round 1結果、横断整理用)・`TRIAL_RESULT_01.md` §7
- `er118_output/fz_dialogue_context_tts_trial_02/{open_window,monkeys_paw}/llm/emotion_review.json`(全文、短い)
- `docs/pm/RESULT_PACKET_FZDC4.md`(全文)

## 事前指定Grep一覧+追記位置・更新位置の手順
1. 反映: 上記Fable判定を両`emotion_review.json`の`fable_decision`へ転記(accept/discard)、`summary_ja`確認。`PHASE1_GO.json`を`cap_jpy=30, scope="Phase 1b", arms=["ctx","base"], approved_by="Fable(委任_05、ユーザー2026-10-26追加Trial承認30円)"`に更新。
2. 起動前: `py docs/pm/tools/daily_dev_cost_01.py`、`py tools/stop_scope_check_01.py --managed-id FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 --run-dir er118_output/fz_dialogue_context_tts_trial_02 --out er118_output/fz_dialogue_context_tts_trial_02/stop_check_委任_05.json`(rc=3なら起動しない)。Get-Dateで起動時刻を記録、起動間隔150秒以上、同一コマンド5分3回禁止。外部停止・原因不明rc≠0が2回続いたら再起動せずSTOP。
3. 生成(直列): open_window → monkeys_paw。各gen-session後に実費を`BUDGET_LOG_02.md`へ追記(cost log実測)。
4. 解析(API 0): 各作品`analyze`→`page-all`。事前登録02の写像を作品ごとに機械適用し、`EVAL_02.md`(新規)に「作品別の事前登録判定」と「追加分析(事前登録外): 3作品合算・改善clipと非改善clipの特徴(手がかり語の明確さ・語数・話者・感情種別・take安定性)」を**別節で区別**して記載。過剰演技監視・leakage・ASR逐語一致・comparison_validも作品別に。
5. 公開: `user_test/fz_dialogue_context_trial_02/index.html`(+mp3。wav不追跡)に、2作品×8セリフ×A(①+base_t1)/B(ctx_t1/ctx_t2)、本文・場面感情の短い説明(`summary_ja`)・前後文脈・改善版=Bの明示・Round 1(賢者)ページ`user_test/fz_dialogue_context_trial_01/index.html`への相互リンク。noindex・PAGE_NOTICE。`py -I tools\user_test_page_standard_check_01.py --page user_test\fz_dialogue_context_trial_02\index.html` rc=0(Y用notice checkは対象外)。公開URL=`https://shimomura055.github.io/eigo-radio/user_test/fz_dialogue_context_trial_02/index.html`。
6. `TRIAL_RESULT_02.md`(新規): ユーザー原文§4の5項目に対応する事実、§7の3作品横断整理、Status候補(事前登録写像どおり。REJECTED/VALIDATED(限定)の候補と根拠)、Fable評価欄(空欄)、ユーザー試聴の論点。
7. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01_DELEGATION_05.md`(Nは616前後、`--index -1`不可、「委任_05」「RESULT_PACKET_FZDC5」を含むものを探す)。

## 実行コマンド全文
- `py docs/pm/tools/daily_dev_cost_01.py`
- `py tools/stop_scope_check_01.py --managed-id FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 --run-dir er118_output/fz_dialogue_context_tts_trial_02 --out er118_output/fz_dialogue_context_tts_trial_02/stop_check_委任_05.json`
- `$env:PYTHONUTF8=1; $env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er118_fz_dialogue_context_tts_trial_01.py --work open_window gen-session`
- `$env:PYTHONUTF8=1; $env:TTS_EXECUTION_MODE="STANDARD"; .venv\Scripts\python.exe er118_fz_dialogue_context_tts_trial_01.py --work monkeys_paw gen-session`
- `$env:PYTHONUTF8=1; py er118_fz_dialogue_context_tts_trial_01.py --work open_window analyze`
- `$env:PYTHONUTF8=1; py er118_fz_dialogue_context_tts_trial_01.py --work monkeys_paw analyze`
- `$env:PYTHONUTF8=1; py er118_fz_dialogue_context_tts_trial_01.py page-all`
- `py -I tools\user_test_page_standard_check_01.py --page user_test\fz_dialogue_context_trial_02\index.html`
- `python docs/pm/tools/check_delegation_prompt.py --file docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01_DELEGATION_05.md --json-out docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01_DELEGATION_05.md_check.json`
- secret grep: `git grep -n -I -E "(sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|BEGIN (RSA|OPENSSH) PRIVATE KEY)" -- docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 user_test/fz_dialogue_context_trial_02 er118_fz_dialogue_context_tts_trial_01.py`
(gen-sessionのサブコマンド名・環境変数の扱いがscriptと異なる場合はscriptの`--help`に従い、実行した全コマンドを引数実値でRESULT_PACKETに記録)

## SSOT追記文(本委任は編集しない。RESULT_PACKETに文案のみ)
- OPEN-516行末追記案: 「【Round 2(委任_04/05、2026-10-26)】ユーザー指示(原文=…_USER_02.md)で追加2作品(開いた窓・猿の手、各8セリフ)を同一方式・同一事前登録02で比較。実費<x>円/上限30円。作品別事前登録判定=<…>。追加分析(事前登録外)=<…>。試聴ページ=https://shimomura055.github.io/eigo-radio/user_test/fz_dialogue_context_trial_02/index.html。Status候補=<…>(Fable評価・ユーザー試聴待ち)。」
- DECISION_LOG案: 「2026-10-26 FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_04/05: ユーザー承認の追加比較Trial(2作品、30円)を実施。Production配線なし。<結果要約>。」

## Git(明示add対象・コミットメッセージ・trailer)
- add対象: `docs/research/FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01/{EVAL_02,TRIAL_RESULT_02,BUDGET_LOG_02}.md`、`user_test/fz_dialogue_context_trial_02/`(index.html・mp3のみ)、`docs/pm/delegation_log/2026-10-26_FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01_DELEGATION_05.md`(+_check.json)、er118 script/testに変更があればそれ。wav/raw_usage_log/PHASE1_GO/STOP/lock/RESULT_PACKET/emotion_review.jsonは既存方針どおり(Round 1で追跡していたものに倣う)。
- メッセージ案: 「FZ-DIALOGUE-TTS-CONTEXT-EMOTION-TRIAL-01 委任_05: 追加2作品(開いた窓・猿の手)のA/B生成・解析・試聴ページ公開(実費<x>円/30円、Production変更0)」
- `git commit --only <paths>` → `git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。
- SSOT編集権: なし(X委任_01が保有)。

## 報告(RESULT_PACKET項目)
`docs/pm/RESULT_PACKET_FZDC5.md`(新規)。「現在の状態/何をやったか/何が分かったか/何が残ったか/判断候補/補足」+RESULT_PACKET 4行+判定整合行。必ず含める: (1)16件の反映結果、(2)起動時刻一覧と各gen-sessionの実費(cost log実測)・累計/30円・日次累計、(3)作品別の事前登録02判定(a〜g・主指標分離件数・Status候補)と追加分析(別節)、(4)ユーザー原文§4の5項目への回答(機械所見としての範囲を明示)、(5)3作品横断の傾向(改善clip/非改善clipの特徴)、(6)公開URL・standard check rc、(7)SSOT追記文案、(8)commit hash・push結果・raw.githubusercontent.com URL、(9)check_delegation結果。