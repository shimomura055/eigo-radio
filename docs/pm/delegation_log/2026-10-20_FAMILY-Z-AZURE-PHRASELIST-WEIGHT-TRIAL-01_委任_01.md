# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 委任_01(ユーザー2026-10-20指示原文保存[T-0]+既存実装/SDK仕様調査+事前登録Trial設計+Trial専用harness+基準条件A[録音2]の実走[小額]+付帯: 録音2 wav実体パスの検証・是正)。2026-10-20。
並行タスク衝突確認: 並行委任なし(FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01 委任_08まで完了・push済み、最新commit bf10cb914)。SSOT編集権: 無し(追記文案はRESULT_PACKETへ)。ただし付帯作業の是正対象(`docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/MELOS_REGEN_RUN_E2E_05_RECORD_01.md`)は編集可。`docs/pm/ACTIVE_TASK.md`は先頭へ自委任ヘッダを追記するのみ。

## 性質/到達上限Status/禁止事項
- 性質: Trial(Offline/Trial専用経路)。Production設定・発音判定仕様・Prompt・閾値・Gate・HR Lockは**変更しない**。Trial harnessは`er084_azure_phraselist_weight_trial_01_*.py`(新規)と`er084_output/azure_phraselist_weight_trial_01/`に閉じ、Production moduleは読取/関数呼出のみ(判定ロジックは変更せずそのまま呼ぶ)。
- 到達上限Status(本委任): `PLW_PHASE_A_DESIGN_HARNESS_READY_BASELINE_A_DONE_PENDING_FABLE`。Trial全体の到達上限=VALIDATED(Production採用はユーザーのみ)。
- 禁止: (1)A案・A'案・P1/P2の実装・暗黙採用(判定ロジック変更禁止)。(2)Production ASR設定(`er006_secondary_asr_01.py`のPhraseList・重み)の変更。(3)文脈B・反復Cの有料実走(委任_02、Fable照合後)。本委任の有料実走は**基準条件A(録音2)のみ**。(4)HR Lock・承認記録・run_e2e_04/05成果物の変更(読取のみ)。(5)`git add -A/-u/-f`・amend・rebase・force push・stash。(6)結果を見てから条件・指標を変える(設計は実走前に文書化・commitし、変更は設計書の改訂履歴に残す)。
- 修正範囲の線引き(11-8): 本委任に不具合修正は含まない(付帯作業は記録上の誤記の是正)。
- Opus独立技術レビューGate(11-3): 本委任=非該当(Trial設計)。設計書完成後にFableが任意レビュー(1日2回枠)の要否を判断するため、設計書に「Opusレビュー観点案(5件以内)」を含める。
- 費用/日次: 当日(JST 2026-10-20)既使用JPY28.79(出典: `docs/pm/RESULT_PACKET_FZAQ7.md`)/残JPY971.21/本委任見積JPY≤12(根拠: 基準条件A=録音2 wav約10秒×5条件×3回=15呼出≈150秒、Azure STT USD1.0/audio hour=160JPY/USD→約JPY6.7、SDK反映確認の追加呼出・予備を含め≤12。TTS 0・LLM 0)/改善見込み中/承認区分C(ユーザー承認済みTrial・300円以下・日次内)。
- T-3: 上限¥12(Guardrail、本委任分)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。Trial全体のFable枠は設計書の見積に基づき委任_02で確定(案件合算300円以下を前提に設計。超える設計になる場合はその旨と理由を明記)。
- 時間見込み: 全体3〜4h(T-0 10分/SDK・実装調査45分/設計書60分/harness 60分/条件A実走+集計30分/付帯15分/報告20分)。並列化: SDK調査と録音2 wav特定は独立、先行可。直列化理由: 条件A実走はharness+SDK重み反映確認の後。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-2/T-3)
E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。**本委任文は本メッセージ全文を一字一句そのまま保存する(要旨版はFAIL)。**
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`): TTSを伴う委任は`TTS_EXECUTION_MODE=STANDARD`を明示する。本委任はTTSを生成しない(文脈Bの新規TTSは委任_02で`TTS_EXECUTION_MODE=STANDARD`明示)。T-2追記(7-5)4点は委任_02で適用。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 定型文は上記「性質」欄に記載済み。

## ユーザー指示(原文)
原文は別ファイル`docs/pm/delegation_log/2026-10-20_FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01_USER.md`に逐語保存(sha256 7d7b9e1690ac0e7674c47abcdcdfecf1b99a6fab8adc49100dfc5b1e8aa63358)。

## 本委任の作業
### W1. 既存実装・SDK仕様の調査(JPY0)
- `er006_secondary_asr_01.py`のPhraseList注入箇所(Grep `PhraseListGrammar|phrase_list|addPhrase|add_phrase`、L70付近)とAzure STT呼出形態(SDK `azure-cognitiveservices-speech`か REST/Fast transcriptionか、認識モード=`recognize_once`/continuous、言語、`SpeechConfig`のproperty)を関数:行で記録。
- インストール済みSDKの版と、PhraseListの**重みAPIの有無**を**SDKのソース/型定義から実証**する。重みAPIが無い版なら、ある版への更新可否(Trial環境内のみ、別venv)を調査し、設計書に明記。
- 「重み未指定」の実効値: SDK docstring/ソース・pipパッケージ同梱doc。**実機で検証する方法**を設計(SDK診断ログ/`Speech_LogFilename`で送信JSONに重みが載るかを確認し、未指定・1.0・1.5・2.0でログ差分を比較=「重み反映の証拠」)。
- 過去結果の再利用: ITEM1_PHONETIC_EQUIVALENCE_ROOT_CAUSE_01.md §4、asr_consistency_part3c1_01_result.json、HR_LOCK_PART3C1_ROOT_CAUSE_01.md §3を引用し「同一wav反復の情報価値」を事前評価。
### W2. 録音2 wavの特定と付帯是正(JPY0)
- 録音2=run_e2e_04 Std part3_c1のattempt2の音声。HRページ・attempts配下・result.json・RESULT_PACKET_FZQI10.mdを突き合わせ、wav実体パスとsha256を確定。委任_07の記録は`full_story_part3_c1.wav`(sha 713252…)としたが、LR版(`He drank`)6%減速版の可能性が高い(`full_story_part3_c1_original.wav` sha 40c6907e…が別に存在)。誤記なら`MELOS_REGEN_RUN_E2E_05_RECORD_01.md`を訂正(訂正履歴1行付き)し、`human_approved_segments.json`への影響の有無をRESULT_PACKETへ(承認記録の再書込みはしない)。
### W3. 事前登録Trial設計書(`docs/research/FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/TRIAL_DESIGN_01.md`、実走前にcommit)
- §1 目的・仮説(H1/H2/H3/H0)、§2 条件(A/B/C)、§3 指標と事前固定の判定基準、§4 試行数・費用見積、§5 実行順序・並列化、§6 都合のよい採用の防止、§7 Opusレビュー観点案(5件以内)、§8 E-1既存仕様照合。
### W4. Harness(`er084_azure_phraselist_weight_trial_01_lib.py`/`_run.py`/`_eval.py`/`_test_01.py`)
- lib/run/eval/test(API 0、約10件)。費用記録は`er005_cost_logger`をTrial専用THEME_TAG(`PLW_TRIAL_01`)で。
### W5. 基準条件Aの実走(有料、≤JPY12)
- 録音2 wav × {PLなし, PLあり未指定, 1.0, 1.5, 2.0} × 3回=15呼出。生転写・NBest・SDK logの重み記述を保存。Production判定offline注入(Primary=既存OpenAI転写`Mello drank`、Secondary=各条件のAzure転写)。「未指定=1.0か」の実測結論。
### W6. 報告
- `docs/pm/RESULT_PACKET_PLW1.md`: (1)T-0 (2)W1要点 (3)W2結果 (4)設計書の要点 (5)Aの結果表 (6)決定論性の実測と委任_02推奨構成の修正点 (7)費用 (8)Git (9)判断候補 (10)一覧外Read理由。判定整合行1行。

## Git
- commit 1: delegation_log 2件(+check)。msg: `FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 委任_01: ユーザー2026-10-20指示原文保存(PhraseList重み1.0/1.5/2.0比較Trial承認・Production非変更)`
- commit 2: 設計書+design_matrix+harness+test。msg: `FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01 委任_01: 事前登録Trial設計+harness+test(API 0)`
- commit 3: 条件A結果+付帯是正。
- trailer: `Delegation: FAMILY-Z-AZURE-PHRASELIST-WEIGHT-TRIAL-01/委任_01`
- SSOT編集権: 無し。

(注記: 本ファイルは委任文の保存版。実行コマンド全文・事前指定Read/Grep一覧・SSOT追記文案の節は、委任文本体のとおり適用した。)
