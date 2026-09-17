## 管理ID

`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-04`(親: `USER-TEST-NEWS-2EP-COMPLETION-01`、前段: `-RESUME-03` `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME3.md`[累積Full Report、既読扱い可・必要箇所のみGrep])。現在main=`1cceb843`以降。報告は`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME4.md`(新規、累積Full形式)へ。

**並行タスクあり(衝突回避ルール)**: 別sonnet-workerが`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B`(er012 B-Family module実装+Personalized News A2生成[音声stage含む]+SSOT編集+commit/push)を実行中。(1)**本タスクの音声stage(TTS/ASR/Assembly/Gate=共有store `er006_output/master_audio_store_01/manifest.json`・`pronunciation_ledger_01/ledger.json`・`human_review_queue.jsonl`への書き込み)は、marker `docs/pm/RESULT_PACKET_PN_A2_PHASE_B.md` が存在するまで開始しない**(5分間隔で最大120分待つ。超過時は記事stage完了までで停止し`WIRING…`ではなく「音声stage待ち」として報告)。記事stage(Local Rewrite/Ledger Deviation/Fact Checker/B1 Writer/Scaffold text/Key Phrase選定)はOpenAIのみで共有storeに触れないため即実行可。(2)SSOT編集(DECISION_LOG/OPEN_ITEMS)とgit操作は最後にまとめて行い、編集前に`git status --porcelain DECISION_LOG.md OPEN_ITEMS.md CURRENT_SPEC.md docs/pm/PM_GOVERNANCE.md`で自分以外の未commit変更が無いことを確認(あれば5分間隔で最大30分待つ)。commit前に`git fetch origin`→進んでいれば`git merge origin/main --no-edit`(rebase/force push禁止、競合時はSTOP)。全文Write禁止。(3)`docs/pm/ACTIVE_TASK.md`は最後に1回だけ固定ヘッダ形式で上書き(UDR-deferred: OPEN-159/160/161 DEFERRED、Family C 2仕様 APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE、PHASE-Bの状態を引継ぎ)。(4)root直下`er0*.py`は変更しない。

## 性質/到達Status/禁止事項

- 性質: RESUME-03でSTOPしたTheme 2(AI Control)A2記事のLedger Deviationを**Fable判断(下記)に従い既存正式経路で是正**し、B1生成→A2/B1音声→player 2本→URL 4本(最終SHA)→Sheet投入用2行→SSOT→commit/pushで**親タスク4本完成**まで進める。
- 到達Status: 記事処理=`USER_TEST_READY`(親タスク17項目×4本すべて充足時のみ)。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`変更禁止。
- 禁止: 不要なTTS/Writer/Research再実行、新モデル試行、Prompt改善Trial、Productionコード改修、validator修正、Gate緩和、Ledger拡充Trial機構(`FAMILY-A-NEWS-STAGE4-LEDGER-ENRICHMENT-*`等、Production未採用)の使用、Ledgerへの手動fact追加、記事本文の手書き(Writer/Local Rewrite経路外での直接編集)、`user_test/unified.html`改修、Google Sheet編集、`git add -A`/`stash`/`amend`/`rebase`/`force push`、wavのcommit。
- コスト: 本タスク≒¥150〜300想定。親タスク累計(現在約¥313)が**¥1,000**を超える見込みならSTOP。

## Fable判断(2026-09-17、PM自律判断方針[承認済み大方針から一意に導ける低risk・低cost判断はUDRにしない]に基づく。ユーザーへは報告済み扱い)

**Theme 2 A2のLedger Deviation MAJOR(「superintelligence / intelligence explosion / singularityは仮説であり、これらのテストでは観測されていない」の一文)の扱い**:
- 判断: **(a') 当該一文をLedgerが直接裏付ける語彙・範囲に収める最小是正**を、既存Local Rewrite機構(残りcycle 2/3)で行う。Ledgerに無い個別概念名(superintelligence/intelligence explosion/singularity)を**記事から外し**、Ledgerが裏付ける表現(例: 「severe loss-of-control scenarios are hypothesized and were not observed in these tests; experts disagree about how likely they are」= Ledger構造化ファイル L197-231「Conditions required for severe loss of control / Hypothesized severe active loss-of-control scenarios」・L273-288「Expert warnings and disagreement…」[2026 International AI Safety Report]の範囲)へ置き換える。
- 根拠: Fact Safety(記事の主張はVerified Fact Ledgerへ遡及可能でなければならない)からの一意な帰結であり、記事を「より慎重」にする方向=Gate緩和ではない。Ledgerへの事実追加(Ledger拡充)はProduction正式経路に存在しない(Trialのみ)ため使わない。ユーザーのTheme 2指示(仮説と事実の分離、事実認定しない)はLedger語彙の範囲で満たす。
- 不採用: (b)再Research/Ledger拡充(Production経路なし・Research再実行禁止)、(c)当該一文の人間承認(Fact Safetyの人間判断による緩和=禁止)。
- 実施方法: Local Rewrite cycle 2(必要なら3)に、Ledger Deviation Checkerの指摘(`.../ai_control/a2/audit/deviation_full_record.json`、`local_rewrite_cycles.json`)をそのまま入力し既存機構で書き直し→Ledger Deviation Checker再判定。既存Local Rewrite入力に「Ledger外の個別概念名を用いない」旨の追加指示を渡せる正式引数がある場合のみ使う(Prompt本文の改変は禁止。引数が無ければ既定のLocal Rewriteを残りcycleで実行)。3 cycle使い切って未解消なら既存Diagnostic Full Retry(Writer再実行、article retry 2/2)を1回。それでも未解消なら**STOP**(USER_DECISION_REQUIRED)。
- B1でも同種のLedger Deviationが出た場合は同じ判断を適用(既存Local Rewrite→Full Retry→STOP)。
- Fact Checker `REVIEW_REQUIRED`はER-010-NO9どおりnon-blocking advisory(追加修正しない)。

## ユーザー既承認事項(RESUME-03、本親タスク限定)

- **Theme 2向け限定事前承認**: ASRが`EXACT_MATCH`/`NORMALIZED_MATCH`で本文一致確認済みで、Human Review Lockの原因が**repetition QA/disfluency QAのみの明らかな誤検知**(OPEN-160/161クラス)の場合、Human Approvalを正式記録(reason="ユーザー事前承認2026-09-17 RESUME-03: repetition/disfluency QA誤検知クラス、ASR <分類>一致")して続行可。**必ずSTOP**: 固有名詞の実際の誤読/数字の誤読/否定・意味内容の変化/`ASR_VALIDATION_UNCERTAIN`/`TRUE_CONTENT_MISMATCH`/実質的不一致/既知誤検知クラスで説明できない新問題。恒久緩和ではない。すべてruntime evidenceを残し報告に列挙。
- Space Weapons A2/B1は完成済み(A2 364.848s/B1 382.984s、Gate PASS、player/URL到達確認済み、commit `c2af33f2`)。再生成しない。

## 手順

1. T-0(委任文を`docs/pm/delegation_log/USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-04.md`へ保存、`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果を1行記録、FAILでも継続)。
2. Theme 2 A2是正(上記Fable判断)→`status=OK`確定→Scaffold(日本語タイトル/Preview/Key Phrase 5件/Comment)→Key Phrase選定。
3. Theme 2 B1生成(同一Ledger、B1-B Direct、`run_pipeline.py`のB1段)→Fact Checker/Ledger Deviation→Cross-level確認(A2/B1の日付・数値・方向性・因果の矛盾なし、目視比較で可・その旨明記)→Scaffold。
4. marker確認→音声stage(A2→B1: TTS→ASR/Validation→Assembly→Gate)。Human Review Lockは事前承認条件に照らして判定。
5. player 2本(既存`build_web_player_common.py`、Space Weaponsと同形式)+web mp3。
6. Git成果物commit(明示add、wav除外)→push→**FINAL_MAIN_SHAで4本のrawcdn URL**(Space Weapons 2本も最終SHAで再生成)→User-Agent付きGET到達確認(unified.html/player.html=200、episode.mp3 Range=206、CDN遅延60秒×最大3回)。
7. Sheet投入用2行(記事タイトル(English)/記事タイトル(日本語)/記事の概要(日本語、2〜3文)/ノーマル(A2)=URL/Advanced(B1)=URL/備考=最新ニュース)。
8. SSOT(衝突回避ルール): DECISION_LOGに本IDエントリ(Fable判断の内容と根拠・実施結果・Human Approval一覧・4本完成・Closeout)。OPEN_ITEMS: 変更不要なら無変更(必要ならOPEN-160/161行へevidence追記のみ)。CURRENT_SPEC無変更。
9. Closeout(Gate 3/5/7): 4 player実体/Audio Validation Gate/runtime evidence/actual model_id・routing/Human Approval履歴/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/commit・push/未処理UDR/APPROVED未配線/未報告Trialを確認。
10. RESULT_PACKET/ACTIVE_TASK/SSOTを別commitでpush。メッセージ`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-04: AI Control A2 Ledger Deviation是正(Local Rewrite)+B1生成+A2/B1音声完成+player 4本+URL+Sheet情報`、trailer `Task-ID: USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-04`。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)
E-1: 同一ファイル再読禁止。D-1: Grep→該当行範囲Read。G-1: git出力最小化。F-1: transcript退避不要。T-1: 事前指定外Readは理由をRESULT_PACKETに1行記録。

## 事前指定Read/Grep一覧
- `er014_output/user_test_news_2ep_01/ai_control/a2/audit/deviation_full_record.json`、`local_rewrite_cycles.json`、`run_result*.json`(現在の状態・残cycle)
- `er014_output/user_test_news_2ep_01/ai_control/research/verified_fact_ledger_structured.json` L190-290(loss-of-control関連fact)
- `er014_output/user_test_news_2ep_01/ai_control/run_pipeline.py`(自作driver、resume/段階実行の方法)、`er003_v1_n3_01_articles_generate.py`: Grep `def run_local_rewrite|local_rewrite|def run_one_pattern|diagnostic_full_retry|human_review_required`→Local Rewriteの継続実行方法と引数のみ
- `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME3.md` 7-8節(URL形式・Sheet行の書式)
- `DECISION_LOG.md`: Grep `^## USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-03`(直近エントリ書式)、`OPEN_ITEMS.md` L306/L308(OPEN-160/161)
- `docs/pm/PM_BRIEF.md` L135-159(固定ヘッダ)

## 報告(`docs/pm/RESULT_PACKET_NEWS_2EP_RESUME4.md`、★★★★報告ここから/ここまで★★★★で囲む累積Full形式)
