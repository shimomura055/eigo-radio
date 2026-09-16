## 管理ID

`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-03`(親: `USER-TEST-NEWS-2EP-COMPLETION-01`、前段: `-CORRECTION-01`、`-RESUME-02`)。現在main=`222d4cbe`以降(別agentのpushで進んでいる可能性あり)。報告は`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME3.md`(新規)へ。

**並行タスクあり(重要)**: 別sonnet-workerが`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01` Phase A(read-only監査+`docs/pm/PM_GOVERNANCE.md`/`docs/pm/PM_BRIEF.md`/`DECISION_LOG.md`/`docs/pm/ACTIVE_TASK.md`編集+commit/push)を実行中。衝突回避ルール: (1)本タスクのSSOT編集(DECISION_LOG/OPEN_ITEMS/PM_GOVERNANCE)とgit操作は**最後(手順7以降)にまとめて**行う。(2)SSOT編集開始前に`git status --porcelain docs/pm/PM_GOVERNANCE.md docs/pm/PM_BRIEF.md DECISION_LOG.md OPEN_ITEMS.md`を確認し、自分が行っていない変更が残っていれば5分間隔で最大30分待ち、clean(=相手がcommit済み)になってから編集する。30分経っても残る場合はSSOT編集をスキップし、その旨をRESULT_PACKETに記録して成果物commitのみ行う(FableがSSOT反映を別委任する)。(3)commit前に`git fetch origin`→origin/mainが進んでいれば`git merge origin/main --no-edit`(rebase/force push禁止、競合時はSTOP報告)。(4)`docs/pm/ACTIVE_TASK.md`は最後に1回だけ固定ヘッダ形式で上書き(UDR-deferred欄に「PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01 Phase A(進行中または設計案提示済み、Fable照合待ち)」「OPEN-159 DEFERRED」「Family C 2仕様 APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE」を引継ぎ)。(5)ファイルの全文Write禁止(Editで局所追記)。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー正式判断(2026-09-17、RESUME-03)を受け、Space Weapons B1の2 segmentを人間承認→B1 Assembly/Gate→Theme 2(AI Control)一式→player 4本→URL 4本→Sheet投入情報→SSOT→commit/pushまで、既存Production正式経路で**4本完成まで進める**。
- 到達上限Status: 記事処理=`USER_TEST_READY`(親タスク受入条件[Article生成成功/Verified Fact Ledger整合/Fact QA規定内/Previewあり/Key Phrase 5件/Comment・解説あり/Full Story完成/A2・B1整合/全音声segment生成/Audio Validation PASS/Assembly PASS/playerでepisode参照可能/timeline・seek情報あり/unified.html互換/内部情報がuser画面に出ない/local path参照なし/URL生成済み]を4本すべて満たしたときのみ)。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`への変更禁止。
- 禁止: 不要なTTS再生成(承認対象segmentの再生成含む)、不要なWriter/Research/Fact Checker再実行、新モデル試行、Prompt改善Trial、Productionコード改修(root直下`er0*.py`)、validator修正、QA緩和の恒久化(CURRENT_SPECへの記載禁止)、`user_test/unified.html`改修、Google Sheet編集、複数案検証、`git add -A`/`stash`/`amend`/`rebase`/`force push`、wavのcommit。
- コスト目安: Theme 2一式+B1残り≒¥300〜500。本タスク累計が**¥1,000**を超える見込みならSTOP。

## ユーザー判断(原文要旨、忠実転記)

### 1. Space Weapons B1の2 segment: 承認して続行
- `preview`: 現final wavを採用。ASR EXACT_MATCH確認済みを根拠にHuman Approvalを正式記録。TTS再生成しない。
- `full_story_part1`: **attempt1 wav**(`.../b1b/narration/attempts/full_story_part1_attempt1_englishstyleprefixwidemargin.wav`想定)をsha256照合のうえ再利用。attempt1はASR NORMALIZED_MATCHかつ`Troy Meink`正読確認済み。現attempt2は不採用(退避、削除しない)。Human Approvalを正式記録。TTS再生成しない。B1 slowdown等の必須post-processがあれば既存正式関数で適用しevidence記録(RESUME-02のA2手順と同様)。
- その後B1 Assembly→Audio Validation Gateまで正式Production経路で完了。

### 2. Theme 2向け限定事前承認(本親タスク`USER-TEST-NEWS-2EP-COMPLETION-01`の範囲内のみ)
ASRが**EXACT_MATCHまたはNORMALIZED_MATCH**でcanonical本文との一致を確認できており、Human Review Lockの原因が**repetition QA/disfluency QAのみの明らかな誤検知**である場合、Sonnetは今回のユーザー事前承認を根拠にHuman Approvalを正式記録(reason="ユーザー事前承認2026-09-17 RESUME-03: repetition/disfluency QA誤検知クラス、ASR <分類>一致")し、STOPせず続行してよい。**必ず従来どおりSTOP**: 固有名詞の実際の誤読/数字の誤読/否定・意味内容の変化/`ASR_VALIDATION_UNCERTAIN`/`TRUE_CONTENT_MISMATCH`/音声とcanonical本文の実質的不一致/今回確認済みの誤検知クラスでは説明できない新しい問題。これはProduction Gateの恒久緩和・仕様変更ではなく、今回のNews 2EP完成タスク限定のHuman Approval委譲。**すべてruntime evidenceを残し、最終報告に列挙**(segment/level/ASR分類/QA flag内容/承認理由/evidence path)。

### 3. QA誤検知2件をOpen Item登録(コード・Validator・Prompt変更なし、記事完成をブロックしないdeferred)
- **Open Item A**: 文境界をまたぐ正当な単語反復をdisfluency/repetition QAが誤検知する問題(例: `...weapons in space. Space security...`)。
- **Open Item B**: `U.S.`等の句読点付き表記のtokenization/canonical repeat count不整合により、本文に正当に存在する反復を0回等と誤認し、音声側の正常な反復を誤検知する問題。

### 親タスク再開(上記処理後、4本完成まで)
1.Space Weapons B1 Assembly/Gate 2.Theme 2「AIは本当に人間の制御を超える可能性があるのか」(Research→Verified Fact Ledger→A2/B1→QA→Scaffold/Comment/Preview→Key Phrase→TTS→Assembly→Audio Validation Gate) 3.user-test player 4本 4.web URL 4本 5.Sheet投入用情報 6.必要SSOT反映 7.commit/push。

### 報告フォーマット運用(D: PM文書再確認・記録)
PM_GOVERNANCE.md 9-8(★★★★報告ここから★★★★〜★★★★報告ここまで★★★★の正式報告ブロック、L953〜)と12-4/12-4-1(未回答フル再掲、L1450〜)は既存。ユーザー再指示の要点「**Feedback・判断がないまま新しい進捗報告を追加する場合、差分報告禁止。前回Full報告+新内容+最新Status+完了/未完了+UDR+Open Item+cost+Git+runtime evidence+次に必要な判断を統合した最新Full Reportを丸ごと再掲(直近1件だけで現状を全把握できる状態を維持)。Feedback後はそれを取り込んだ新基準から構成。分割worker/continuation worker使用時もユーザー向け最終報告担当は同ルール適用、worker断片報告をそのまま出さない」が12節に**明文化されているか確認**し、抜けていれば12-11「Full Report累積再掲ルール(2026-09-17ユーザー再指示)」として追記(PM運用ルール、Product仕様ではない)。既にあれば追記せず該当節番号のみ報告。

### STOP条件(以下のみ)
Theme 2で実質的な音声誤読/ASR uncertain・content mismatch/新しい仕様判断が必要/Productionコード変更が必要/新しい未承認QA緩和が必要/予期しないProduction blocker/4本完成に必要な正式pathが存在しない/コスト¥1,000超見込み。事前承認済みのrepetition/disfluency既知誤検知だけを理由にSTOPしない。

### Closeout(4本完成時、Gate 3/5/7)
4 player実体/Audio Validation Gate/runtime evidence/actual model_id・routing/Human Approval履歴/CURRENT_SPEC(無変更)/DECISION_LOG/OPEN_ITEMS/commit・push/未処理UDR/APPROVED_FOR_PRODUCTION未配線項目/未報告Trial、を確認してから完了報告。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一ファイル再読禁止。D-1: Grep→該当行範囲Read。G-1: git出力最小化。F-1: transcript退避不要。T-1: 事前指定Read/Grep一覧に従い、一覧外の追加Readは理由をRESULT_PACKETに1行記録。T-0: 委任文を`docs/pm/delegation_log/USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-03.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。

## 事前指定Read/Grep一覧

- `.../space_weapons/b1b/audit/review_lock_state.json` L40-60・L451-560、`.../b1b/narration/attempts/full_story_part1_attempt1_*.json`(sha256・asr_text)、`preview_attempt3_*.json`(sha256)
- `er003_v1_n3_01_tts_generate.py`: Grep `SLOWDOWN_TARGET|apply_.*slowdown|B1B|b1b`→B1に必須post-processがあるか
- `docs/pm/delegation_log/USER-TEST-NEWS-2EP-COMPLETION-01.md`: Theme 2関連節
- `docs/pm/delegation_log/USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-02.md`: A2承認手順の記述(必要なら)
- `er014_output/user_test_news_2ep_01/ai_control/run_pipeline.py`・`build_web_player_common.py`: 全体(自作driverのため)
- `docs/pm/PM_GOVERNANCE.md`: L953-990(9-8)、L1422-1580(12節)
- `OPEN_ITEMS.md` L304(OPEN-159書式)、`DECISION_LOG.md` L7852-7862
- `docs/pm/PM_BRIEF.md` L135-159(固定ヘッダ)

## 手順

1. T-0。
2. B1 `preview`承認(現final wav sha256=attempt3記録値と照合)、`full_story_part1` attempt1 wav採用(sha256照合、attempt2を`_attempt2_rejected.wav`へ退避)、必須post-process確認・適用、Human Approval正式記録、review state整合→B1 Assembly→Gate。PASSしなければSTOP。
3. Theme 2 `ai_control/run_pipeline.py`実行(Research 1回→Ledger→A2/B1→Fact Checker/Ledger Deviation→Cross-level確認→Scaffold→TTS→ASR/Validation→Assembly→Gate、A2/B1)。Human Review Lockが出たら事前承認条件に照らして判定(該当=承認記録して続行、非該当=STOP)。
4. player 4本(unified.html `src`互換、Key Phraseは英語+日本語意味のみ、内部情報・SFX/jingle非表示、local path参照なし)+web mp3。
5. Sheet投入用2行を作成(記事タイトル(English)/記事タイトル(日本語)/記事の概要(日本語、2〜3文)/ノーマル(A2)=rawcdn URL/Advanced(B1)=rawcdn URL/備考=最新ニュース)。
6. 成果物commit(明示add、wav除外)→push→FINAL_MAIN_SHAでURL 4本組み立て→到達確認。
7. SSOT(衝突回避ルールに従い最後に): DECISION_LOG 1エントリ、OPEN_ITEMS A/B登録、PM_GOVERNANCE 12-11追記(未記載の場合のみ)。CURRENT_SPEC無変更。
8. RESULT_PACKET/ACTIVE_TASK/SSOTを別commitでpush(URLのSHAは成果物commitのもので有効)。

## 報告(`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME3.md`、**累積Full形式**: RESUME-02までの完了事項も含め、この1件で親タスク全体の現状が分かるように)

0. T-0
1. Space Weapons B1 2 segment承認結果(採用wav・sha256・ASR分類・承認記録path)
2. Space Weapons B1 Assembly/Gate結果(duration)
3. Space Weapons A2(RESUME-02完了分の再掲: Meink再利用・Gate PASS・duration)
4. Theme 2 A2/B1(EN/JAタイトル、語数、Ledger件数、Fact Checker/Ledger Deviation/Cross-level、TTS segment数、Audio Validation/Assembly/Gate、duration)
5. 事前承認に基づくHuman Approval一覧(segment/level/ASR分類/QA flag/理由/evidence path)。STOP該当があればその内容
6. 4本の受入条件チェック(親タスク17項目×4)
7. URL 4本(rawcdn)+到達確認結果
8. Sheet投入用2行(表)
9. 追加APIコスト(本タスク分+親タスク累計、model_id・routing)
10. Git commit/push SHA(成果物/SSOT)
11. Open Item登録内容(番号・要旨)/DECISION_LOG行/PM_GOVERNANCE 12-11の有無・行番号/CURRENT_SPEC無変更証跡
12. Closeout確認(Gate 3/5/7項目の○×)
13. 到達Status(記事処理/固有名詞基盤DEFERRED[OPEN-159]/QA誤検知DEFERRED[OPEN-160/161])
14. 未決事項一覧
15. 無変更証跡(`git status --porcelain er003_*.py er006_*.py er011_*.py CURRENT_SPEC.md`が空[共有ログ差分は別記])/事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(内部識別子`b1b`はpathにのみ可)。
