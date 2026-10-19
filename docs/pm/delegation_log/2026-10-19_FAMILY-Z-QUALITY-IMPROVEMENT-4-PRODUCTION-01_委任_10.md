# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_10(ユーザー2026-10-19指示原文保存+run_e2e_04 Standard `full_story_part3_c1` Human Review Lockの原因分析: 既存対策(M1複数発音候補/Primary・Secondary ASR/PASS_WITH_WARNING等自動救済/Pronunciation Ledger)の発動実績と停止理由をruntime evidenceで明確化、A(TTS誤発音)/B(ASR・検査側の問題)の切り分け、配線漏れ・不具合があれば承認済み仕様内で修正+Regression、HR依頼が必要なら判断ポイントを具体化。**HR Lockは維持。新規TTS生成禁止。原則JPY0(A/B切り分けに不可欠な既存wavへのASR再実行のみ上限JPY5)**)。日付: 2026-10-19(JST)。

## 性質・到達上限Status・禁止事項
- 性質: 調査・分析(runtime evidence主体)+承認済み仕様内の不具合修正(見つかった場合のみ)。
- 到達上限Status: `HR_LOCK_ROOT_CAUSE_ANALYZED_PENDING_FABLE`(修正を行った場合は`..._WIRING_FIXED_TESTED_PENDING_FABLE`)。
- 禁止: HR Lockの解除・`review_lock_state.json`の変更/新規TTS生成・assemble・pages再生成/安全機構の無効化・品質基準(閾値・判定条件・許容候補)の緩和による通過/未承認の新仕様・新品質基準のProduction採用(候補提案は可、QCD付き)/推測を事実として書くこと(推測は「推測」と明記)/`er019_*`・`run_mey_01`への接触(並行agentが作業中)。
- 固定ブロック: **E-1**(既存仕様照合: CURRENT_SPEC「Audio Validation Gate」「Human Review Lock」「PASS_WITH_WARNING」「Secondary ASR」「複数発音候補」「Pronunciation Ledger」「EN ASR semantic equivalence(er021)」「Pronunciation Resolution Core(er025)」、OPEN-318(固有名の読み揺れ)、OPEN-419、Family Z音声仕様(er063)をGrepし、各対策の「仕様上の発動条件」を関数名:行で特定してから実績と突合)/**D-1**(修正が必要な場合: 既存機構の配線修正のみ。方式変更・閾値変更はUSER_DECISION候補として提案)/**G-1**(変更ファイルのみ明示add、`git add -A/-u/-f`・amend・rebase・force push・stash・clean・reset --hard・checkout -f禁止、secret_scan hits=0後commit、push=`C:\Users\tensh\eigo-radio-crbn`で`git pull --ff-only; git merge --ff-only work/post-merge-01; git push origin main`、戻って`git merge --ff-only origin/main`。**並行agentあり(FAMILY-X-B3-FACT-MIN2-PRODUCTION-01 委任_02: er019/run_mey_01/user_test/middle_east_text_review_01とSSOTを編集)**: 共有SSOT(OPEN_ITEMS.md/DECISION_LOG.md/docs/pm/USER_DECISION_REGISTER_01.md/docs/pm/REPORT_LEDGER.md/CURRENT_SPEC.md)は「編集直前に`git status --porcelain <file>`でcleanを確認(dirtyなら60秒間隔で最大10回待つ)→再読→自分の行のみ編集→直ちにadd→commit」を1ファイル群につき1回で短時間に完了、`.git/index.lock`があれば待ち再試行、non-ffは`pull --ff-only`後再試行、conflictはSTOP。ACTIVE_TASK.mdは先頭に自ブロック追記(gitignore対象、commit不要))/**F-1**(原則JPY0。既存attempt wavへのASR再実行が切り分けに不可欠な場合のみ上限JPY5、実費を出典付き報告。新規TTS 0)/**T-0**(本委任文を全文そのまま`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_10.md`へ保存し`check_delegation_prompt.py`実行。要約保存=FAIL逸脱)/**T-2・T-3**(報告=`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI10.md`)。

## ユーザー指示原文(2026-10-19、逐語。`C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_HR-LOCK-ANALYSIS_USER.md`へ以下「## Family Z Melos Human Review Lock」から「最短で解決してください。」までを原文のまま(1文字も変えず)保存し、文字数とsha256を報告)

## Family Z Melos Human Review Lock — 原因分析・既存対策の動作確認依頼

今回のHuman Review依頼について、**現時点では判断を保留します。**

Human Reviewそのものを否定しているわけではありません。これまでHuman Reviewへの移行を極力減らすため、発音候補の許容、複数ASRによる検証、自動救済などの対策を重ねてきました。

にもかかわらず、今回それらの対策がどう働き、なぜHuman Reviewに至ったのかという分析がありません。

**問題はHuman Reviewが発生したことではなく、その理由と既存対策の有効性が説明されていないことです。**

### 1. 既存対策の発動状況を確認

今回のStandard Part 3冒頭の1クリップについて、以下を調査してください。

1. **M1（複数発音候補の許容）**は発動したか。登録候補と実際の判定結果、不一致理由は何か。
2. **Primary／Secondary ASR**はそれぞれ発動したか。各回の認識結果と判定理由は何か。
3. **PASS_WITH_WARNINGなどの自動救済**は適用されたか。適用されなかった場合、その理由は何か。
4. **3回のTTS生成**それぞれについて、どの検査で、何を根拠にNGとなったのか。
5. 前回PASSした同一クリップと今回の違いは何か。テキスト、Voice、Style、速度、発音辞書、検査条件などを比較すること。

推測ではなく、実際のruntime evidenceに基づいて回答してください。

### 2. 問題の本質を切り分ける

今回の問題は、主に次のどちらなのか明確にしてください。

- **A：TTS自体の誤発音** — 実際に「Melos」が不適切に発音されている可能性が高い。
- **B：ASR・検査側の問題** — 音声は許容範囲なのに、認識や判定・救済機構の問題でNGになっている。

現時点で区別できなければ、その旨と不足している証拠を明示してください。

既存対策の配線漏れや不具合が判明した場合は、承認済み仕様の範囲で原因究明・修正・Regression検証まで自律的に進めてください。

ただし、安全機構を無効化したり、品質基準を緩めたりして通過させることは禁止します。

### 3. Human Reviewを依頼する場合の要件

既存の自動対策を正常に適用してもなおHuman Reviewが必要な場合は、次を明示してください。

- **何を疑っているのか**（TTSの誤発音、ASRの誤認識など）
- **人間に何を確認してほしいのか**（具体的な発音箇所・期待する発音・許容判断のポイント）
- **各録音の機械判定結果と、判断が必要な理由**
- **人間の判断によって何が確定し、次の処理がどう変わるのか**

単に「3つの録音を聞いて選んでください」という依頼は認めません。

### 4. 再発防止・QCD

今回の事象が既存対策で防げなかった理由を明確にし、同様のHuman Reviewを量産時に繰り返さないための改善要否を評価してください。

既存のPronunciation Ledgerや自動救済機構を優先的に活用し、重複する仕組みを安易に追加しないこと。

新しい仕様・品質基準変更が必要な場合は、Productionへ無断採用せず、QCD影響とともに提案してください。

### 5. 今回の到達条件

- Human Review Lockは維持する。
- 既存対策の動作実績と停止理由を明確化する。
- 承認済み仕様内の不具合なら自律的に修正・検証する。
- 最終的に人間の試聴判断が必要な場合のみ、判断ポイントを具体化して再提示する。
- #116の未解決事項とStatusを適切に管理する。

**今回の目的は、単にこの1クリップを通すことではありません。これまで構築してきた自動品質保証の仕組みが正常に機能しているかを確認し、不要なHuman Reviewを減らすことです。**

品質を守りつつ、不要な再生成・追加Trial・ユーザー判断待ちを避け、最短で解決してください。
## Fable指示(分析要件)
1. **対策別の発動実績表**(ユーザー§1の1〜5に1対1対応、全てevidenceファイル:キー/行を出典に): 対象clip=`run_e2e_04/a2` Standard `full_story_part3_c1`(attempt1〜3)。各attemptについて: 期待テキスト/Primary ASR(エンジン名・認識文・スコア)/Secondary ASR(エンジン名・認識文・スコア、発動有無と発動条件)/M1複数発音候補(Pronunciation Ledger `er006_output/pronunciation_ledger_01/ledger.json`に「Melos」の登録があるか、登録候補、照合結果、不一致理由)/EN ASR semantic equivalence(er021 telemetry)・Pronunciation Resolution Core(er025 telemetry)の呼出有無と結果/PASS_WITH_WARNING等の自動救済の判定(適用・不適用の理由を判定コードの条件式と照合)/最終判定(TRUE_CONTENT_MISMATCH / ASR_VALIDATION_UNCERTAIN / NG_BOTH等)とHR Lockへ至った遷移。
2. **前回PASSとの差分**(run_e2e_03同clip vs run_e2e_04 attempt1〜3): テキスト(sha)、Voice、Style文字列(sha)、速度(生成時指示・後処理減速の有無。**本clipはNarrationかDialogueか、③の6%減速がNarrationへ適用されていないか**を必ず確認: ③はStd Dialogue限定の仕様)、Pronunciation Ledger版、ASR設定(モデル・言語・閾値)、検査条件(Gate版、`FAMILY_Z_ROLE_STYLE_VERSION`等)、前回ASRの認識文。差分が「仕様上許容される確率的揺れ」か「仕様逸脱・配線差」かを区分。
3. **A/B切り分け**: 既存evidence(2系統ASRの認識文、音響的手掛かり)で判定。不足なら、既存attempt wavおよびrun_e2e_03 PASS版wavに対して**既存のASR経路のみ**(新規TTS禁止)で再評価してよい(上限JPY5、同一設定で比較)。結論を「A寄り/B寄り/区別不能(不足証拠を列挙)」で明記し、根拠を並べる。
4. **配線漏れ・不具合の判定**: 各対策について「仕様どおり発動した/仕様上発動条件外だった/発動すべきなのに発動しなかった(配線漏れ・不具合)」の3区分。「発動すべきなのに発動しなかった」があれば、承認済み仕様の範囲で修正(関数:行)+Regression test追加+全test実行+commit。修正後の再判定は**既存wavに対するoffline再評価**で行い(新規TTS禁止)、その結果が自動PASS相当になっても**HR Lockは解除しない**(Fable報告→人間判断)。
5. **HR依頼の再提示案**(自動対策を正常適用してもなおHRが必要な場合のみ): 何を疑っているか/人間に確認してほしい具体箇所(秒位置・期待発音「メロス /ˈmɛlɒs/」・許容判断のポイント)/各録音の機械判定結果と人間判断が必要な理由/人間判断で何が確定し次の処理がどう変わるか(例: attempt N承認→Lock解除→gate→assemble→pages。全却下→再生成の条件)。HRページ`user_test/family_z_melos_hr_run04/index.html`は、この要件を満たす説明文へ更新する(音声ファイル・構成は不変。内部情報除外)。HRが不要になった場合はページ冒頭に「保留中(Fable判定待ち)」を記載するだけに留める。
6. **再発防止評価(ユーザー§4)**: 本事象が既存対策で防げなかった理由(仕様上の空白か、配線不具合か、確率的揺れか)と、量産時の再発見込み(固有名を含む物語でのHR率の実績: run_e2e_03/04のclip数とHR数、他Family Zラン)を数値で。改善候補は既存機構(Pronunciation Ledgerへの「Melos」登録・候補追加、Secondary ASRの適用条件、PASS_WITH_WARNINGの既存条件)を優先し、新仕様が必要なものは「候補・QCD影響・Production未採用」として区分(採用しない)。
7. 文書: `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\HR_LOCK_PART3C1_ROOT_CAUSE_01.md`(§1発動実績表/§2前回差分/§3 A/B切り分け/§4配線判定と修正/§5 HR再提示案/§6再発防止評価/§7 E-1)。

## 事前指定Read一覧
- `C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\a2\audit\tts_generation_results.json`、`review_lock_state.json`、`cost_by_stage_04.json`、同`audit`配下のASR/validation関連json(全件列挙して読む)
- `C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04\a2\narration\attempts\full_story_part3_c1_attempt*`(wavと付随json)
- `C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_03\a2\audit\tts_generation_results.json`(同clipのPASS記録)と対応するwav/json
- `C:\Users\tensh\eigo-radio\er063_family_z_audio_01.py`(TTS生成→ASR検証→救済→HR Lockの判定関数群。`FamilyZTtsClipFailedStop`、PASS_WITH_WARNING判定、Secondary ASR呼出条件、Pronunciation Ledger参照箇所)
- `C:\Users\tensh\eigo-radio\er006_output\pronunciation_ledger_01\ledger.json`(「Melos」「メロス」のGrep)
- `C:\Users\tensh\eigo-radio\er021_output\en_asr_semantic_equivalence_production_wiring_01\telemetry.jsonl`・`C:\Users\tensh\eigo-radio\er025_output\pronunciation_resolution_core_telemetry_01\telemetry.jsonl`(当該clip・当該時刻の行)
- `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\PHASE3_RUN_E2E_04_RECORD_01.md`、`C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI7.md`・`RESULT_PACKET_FZQI9.md`
- `C:\Users\tensh\eigo-radio\user_test\family_z_melos_hr_run04\index.html`

## 事前指定Grep一覧+追記位置・更新位置の手順
- `CURRENT_SPEC.md`: Grep `PASS_WITH_WARNING|Secondary ASR|複数発音候補|Pronunciation Ledger|Human Review Lock|Audio Validation Gate|semantic equivalence`→各対策の仕様上の発動条件を§7に行番号付きで記録(編集しない。修正を行った場合のみ該当節に「配線修正(2026-10-19、委任_10)」を1行追記)。
- `OPEN_ITEMS.md`: `OPEN-318|OPEN-419`→OPEN-419に本分析の結論(A/B、配線判定、修正有無)とStatusを追記。OPEN-318に本事象を実績として1行追記。
- `docs/pm/USER_DECISION_REGISTER_01.md`: `#116`→「2026-10-19 ユーザー: 判断保留、原因分析指示。分析結果=<結論>。Status=<HR再提示/HR不要・Fable判定待ち>」を追記。
- `DECISION_LOG.md`: 末尾に「2026-10-19 ユーザー指示(HR Lock原因分析、Lock維持)受領、分析結論、修正有無」。`docs/pm/REPORT_LEDGER.md`: 1行。`docs/pm/ACTIVE_TASK.md`: 先頭固定ヘッダ。

## 実行コマンド全文(作業dir=`C:\Users\tensh\eigo-radio`)
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\docs\pm\tools\check_delegation_prompt.py --file C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_10.md --json-out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_委任_10.md_check.json`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\stop_scope_check_01.py --managed-id FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 --run-dir C:\Users\tensh\eigo-radio\er026_output\family_z_production_e2e_01\melos\run_e2e_04 --out C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FZQI10_stop_check.json`
- `certutil -hashfile C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-19_FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01_HR-LOCK-ANALYSIS_USER.md SHA256`
- `rg -n "Melos|melos|メロス" C:\Users\tensh\eigo-radio\er006_output\pronunciation_ledger_01\ledger.json`
- `rg -n "part3_c1" C:\Users\tensh\eigo-radio\er021_output\en_asr_semantic_equivalence_production_wiring_01\telemetry.jsonl C:\Users\tensh\eigo-radio\er025_output\pronunciation_resolution_core_telemetry_01\telemetry.jsonl C:\Users\tensh\eigo-radio\er006_output\audio_retry_cascade_prod_01\human_review_queue.jsonl`
- 修正を行った場合: `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -m pytest C:\Users\tensh\eigo-radio -q -k "er063 or family_z or asr or pronunciation" --ignore=C:\Users\tensh\eigo-radio\er082_output`
- `C:\Users\tensh\eigo-radio\.venv\Scripts\python.exe -I C:\Users\tensh\eigo-radio\tools\secret_scan_01.py --staged`
- ASR再評価が必要な場合: er063の既存ASR検証関数をoffline呼出する最小script `C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01\asr_reeval_part3c1_10.py`を作成して実行(入力=既存wav4本、出力=`..._result.json`、実費記録)。

## SSOT追記文(要点)
- OPEN-419: 「2026-10-19 HR Lock原因分析(委任_10): 対策別発動実績=<M1/Primary/Secondary/救済の結論>、前回差分=<結論>、A/B=<結論>、配線判定=<仕様どおり/配線漏れ修正済み>、HR=<再提示/不要>。Lock維持。」

## Git(明示add対象・コミットメッセージ・trailer)
- commit 1: delegation_log 2件(+check/stop_check)、HR_LOCK_PART3C1_ROOT_CAUSE_01.md、(修正時)er063等コード+test、(更新時)`user_test/family_z_melos_hr_run04/index.html`、(ASR再評価時)script+result。msg: `FAMILY-Z-QUALITY-IMPROVEMENT-4-PRODUCTION-01 委任_10: run_e2e_04 Std part3_c1 HR Lockの原因分析(既存対策の発動実績・前回差分・A/B切り分け<結論>、Lock維持、新規TTS 0)`(修正があれば末尾に「+配線修正+Regression」)
- commit 2: SSOT(OPEN_ITEMS/DECISION_LOG/REGISTER/REPORT_LEDGER/[CURRENT_SPEC])。

## 報告(RESULT_PACKET項目: `C:\Users\tensh\eigo-radio\docs\pm\RESULT_PACKET_FZQI10.md`)
4行: (1)整合(E-1: 各対策の仕様上の発動条件[行番号]と実績の突合結果、3区分)(2)Production到達経路(修正なし/修正あり:箇所)(3)成果物とcommit sha、ユーザー§1の1〜5への回答(表)、§2のA/B結論と根拠、Narration/Dialogue区分と6%減速の適用有無、修正内容とtest結果、HR再提示案の要点(または不要の根拠)、再発防止評価(数値)、実費(ASR再評価分、出典)(4)撤去/残置。`判定整合:`・`判断候補:`(新仕様候補はQCD付きで区分)・T-0 check・自己チェック(Lock不変[`review_lock_state.json` sha前後一致]/新規TTS 0/品質基準不変/原文逐語保存の文字数とsha256)。
