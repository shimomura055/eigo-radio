# 委任_07｜FAMILY-Y-PRODUCTION-LAUNCH-01 E-1(宅配)の停止3件への対処: ユーザー試聴パッケージ・ER-020ハイフン正規化の不具合是正・OPEN整理

## 背景(Fableから。まず `docs/pm/RESULT_PACKET_YPL6.md` と `docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/EVIDENCE_02.md`(特に5節)・`OPEN_TRACKING_05.md` を読む)
委任_06(commit `fb768a357`)でE-1 `er121_output/family_y_production_01/redelivery_fee/run_01/` は次の3件で停止:
1. a2 `preview`(日本語): 正本「思いどおり」をASRが毎回「思い通り」と転写し表記差でNG(音声は正しく読まれている)。決定論で再現。
2. b1b/a2 `y_voice_1`(英語): ASR一致だがRepetition QAの短ラグ検査(D')が閾値0.6秒の境界(0.60〜0.83秒)でflag。再試行でも通らない。
3. その後ER-020 Local Rewriteが自動起動し `redeliveries`→`repeat deliveries` に書換え。原因は `er020_tts_retry_local_rewrite_01.py:206-231` `identify_ng_span` がハイフン付きASR転写(`re-deliveries`)を正規化しないこと。書換え音声はY Gateが `LOCAL_REWRITE_RECOVERY` でBLOCK(正しい挙動)。R0音声(書換え前)は保全済み。

**Fable判断**:
- 1・2は、既存のHuman Review経路(ER-011/ER-020承認フロー)でユーザーがR0音声を試聴して採用可否を決める。閾値変更・Y向け新Gateは採らない(D'境界問題はOPENとして追跡のみ)。NG音声の最終採用承認 `approved_by="user"` は**ユーザーのみ**。あなたもFableも付けない。
- 3は実装不具合(11-8分類=修正へ進む/B)として自律是正する。仕様・閾値の変更ではなく、ASR転写の正規化漏れの是正(合格範囲は「本来一致していたもの」に戻るだけ)。
- 委任_06が3つ目のsegment(b1b `y_voice_1`)にもapprove_regenerateを1回適用した件は、Fableが追認する(取消不要)。
- Y自律枠(Cap)は170円→**200円**へFableが更新する(7-7の案件300円以下・承認済みScope内。ユーザー新規承認ではない)。ただし本委任の有料支出は**上限5円**(mp3変換等はAPI 0)。日次は `py docs/pm/tools/daily_dev_cost_01.py` 表示値+94.28円が実累計で、1,480円を超える見込みなら有料処理をしない。

## 並行agent(衝突回避)
- (A) KP HR/Part 2 evidence R1〜R4(X/Z runner実走中の可能性。er019/er026/er062/er119/er120系ファイルとそのrun dir所有)。(B) JA ASR 委任_10(er078系・`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/`・OPEN-517行・DECISION_LOG 1件追記を所有)。
- 本委任で編集してよいもの: `er020_tts_retry_local_rewrite_01.py`(+test)、`er121_*`(runner/test/構造は必要最小)、`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/`配下、`user_test/family_y_production_redelivery_fee_01/`(新規、試聴用)、`OPEN_ITEMS.md`(OPEN-520/484行と新規1行まで。OPEN-517行は触らない)、`CURRENT_SPEC.md`/`DECISION_LOG.md`(必要最小・直前再Read・一時index方式で自分のhunkのみ)、`docs/pm/RESULT_PACKET_YPL7.md`、`docs/pm/delegation_log/`。
- **er020の編集は最後に行い、編集前に X/Z runner のprocessが生きていないこと(RUN_LOCKファイル・`Get-Process python*` のコマンドライン)を確認する。生きていれば最大20分待ってから再確認し、それでも生きていればer020編集だけ未実施で報告する**(新processが途中から新コードを読むのを避ける)。

## やること
### 1. ユーザー試聴パッケージ(API 0)
- E-1のHR Lock 3 segment(a2 `preview`、b1b `y_voice_1`、a2 `y_voice_1`)のR0音声(書換え前・最終判定対象のattempt)を特定し、`user_test/family_y_production_redelivery_fee_01/listening/` に mp3(既存の公開mp3と同じ変換方法。wavはcommitしない)と `index.html`(限定共有の注記=`er121_family_y_structure_01.PAGE_NOTICE_JA`と同文、各segmentの本文・ASR転写・NG理由(表記差/D'値)・「ユーザー承認待ち」の明記)を作る。公開mp3は`user_test/`配下のみという既存規則に従う。
- 各segmentについて、ユーザーが承認した場合にFable/Sonnetが実行する**正式承認コマンド**(ER-011/ER-020のCLI・引数・`approved_by="user"`の付与方法・承認後の再開コマンド(`.venv\Scripts\python.exe`表記))を `docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/E1_HUMAN_REVIEW_01.md` に書く。承認後にE-1が組立→ページ→限定公開まで進むために必要な残工程・見積費用(API 0か有料か)も書く。**コマンドは実行しない**。
- a2 `preview` について: 試聴承認以外の正規経路(例: 既存の日本語支援文の再生成・正式Local Rewrite)が既存仕様に存在するなら、名称・費用・リスク・なぜ委任_06が推奨度低としたかを1段落で併記(新機構は作らない)。

### 2. ER-020 `identify_ng_span` ハイフン正規化の是正(API 0、最後に実施)
- 現象の再現test(本文 `redeliveries`、ASR `re-deliveries` で NG span が立つ)を先に書き、是正後にNG span 0になることと、本当の不一致(例 `deliveries` vs `delivery` 等、既存testの負例)が引き続き検出されることを固定。正規化は既存のASR比較で使っている正規化関数(er078/er020内に既にあるもの)を再利用し、独自の新規規則を増やさない。Local Rewriteの発火条件・Prompt・回数上限は不変。
- 回帰: 遮断harness(`netblock_harness_01/sitecustomize.py`)下で er020系+ `ProductionModuleUnchanged` 系testを実行(sha固定testがあれば期待値を更新し、更新理由をcommit messageに書く)。
- 本是正が、E-1の `y_voice_1` のケースで「Local Rewriteが起動しなかった」ことになるかを、保存転写を使ったdry判定で確認して記録。

### 3. OPEN整理・SSOT
- OPEN_TRACKING_05 の YPL6-O1〜O8 を、OPEN-520(Y立上げ)の追記またはOPEN-484等既存項目への追記で記録(新規採番は、既存へ入らないものだけ・11-8分類付き)。O1(D'境界)=D(ユーザー判断候補・急がない)、O2=本委任で是正(是正後はCLOSE候補)、O3=OPEN-517/333系へ参照、O5=修正へ進む(別委任)、O4/O6/O7=実害なし、O8=Cap 200へ更新を記録。
- `BUDGET_PLAN_04`(または最新)にCap 200円とその根拠(7-7)を追記。累計は委任_06までで約166.85円。
- CURRENT_SPEC: Part 1/Part 2/文法HRのY接続状況(コード接続済み・文法HRありの実走は未)を、既存のY節へ1〜2行。
- DECISION_LOG: 1件(ER-020ハイフン正規化の不具合是正+E-1はHuman Review待ち)。他agentの未commit差分を巻き込まない一時index方式。

### 4. Git・ログ
- 禁止=`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。対象pathのみcommit→`git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。secret grep 0件。wav/raw_usage_log/STOP/lock/RUN_LOCK不追跡。作業ブランチ `work/post-merge-01`。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_DELEGATION_07.md`(直近既知index=600付近(JA ASR 委任_10)。601以降を順に試し、先頭行が「# 委任_07｜FAMILY-Y-PRODUCTION-LAUNCH-01」のものだけ採用)。

## 報告(`docs/pm/RESULT_PACKET_YPL7.md`+最終報告)
1. 試聴パッケージ: 各segmentのmp3 path・index.htmlのraw URL・本文/転写/NG理由の要約(ユーザーがそのまま判断できる粒度)
2. 承認後の残工程と費用見積(API 0/有料の別)、承認コマンド文書のpath
3. ER-020是正: 原因・変更内容・test結果・E-1 y_voice_1でのdry判定結果・X/Z runner process確認の結果
4. OPEN/SSOT差分の要約、commit sha、raw URL
5. 費用(本委任・Y累計/200・日次実累計)
6. RESULT_PACKET 4行+判定整合行
7. ユーザー判断が要る事項(27-3分類。推奨付き。試聴承認の選択肢を具体化)
事実と推測を分ける。PRODUCTION_WIREDの語は使わない。