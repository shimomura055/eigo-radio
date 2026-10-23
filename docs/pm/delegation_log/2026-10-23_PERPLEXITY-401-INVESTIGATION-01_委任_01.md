FABLE-DELEGATION-MARKER: PERPLEXITY-401-INVESTIGATION-01-委任_01-20261023

# 委任_01: Perplexity API 401(OPEN-473)の調査・原因究明・承認済み仕様内での復旧判断。秘密情報(APIキー等)をログ・報告・commitへ出さない。新規サービス導入・未承認仕様変更なし。API費用≤5円(疎通確認の最小呼出のみ、理由記録)。

## 背景
『開いた窓』Phase 4で固有名詞発音調査(Perplexity)が401で失敗(PHASE4_RESULT_01.md:43)。ユーザー指示(原文=`docs/pm/delegation_log/2026-10-23_ASR-QUALITY-2ITEMS-COMPREHENSIVE-01_USER_02.md` §4、①PN agentが保存中。未着なら数分待つ): 4点調査(Production利用実態/今回のエラー/原因と復旧/代替手段)、対応原則(自律調査・既存仕様内修正・検証、秘密非出力、ユーザー操作が不可欠な場合のみ理由・操作・放置影響を報告、OPEN-473更新)。A/Bと独立に進める。

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_PERPLEXITY-401-INVESTIGATION-01_委任_01.md`(index 361以降、先頭MARKER一致)。
2. ACTIVE_TASK自分の行のみ(並行: PN/UKUS配線設計、FAMILY-Y 委任_08[有料run中の可能性、pythonプロセスをkillしない])。OPEN-473 Status=`INVESTIGATING`。

## 調査
1. **Production利用実態**: Perplexityを呼ぶモジュール・関数(Grep: perplexity/pplx/sonar)、呼出条件(どの工程: 固有名詞発音調査=er006_secondary_asr_01.py:347-390 の事後Ledger登録経路? PNAP供給? Research?)、X/Z/A/B/Cのどの経路か、flag/既定、最後に成功したruntime証拠(ログ・Ledger sources・usage log)の日時、成功時の費用。
2. **今回のエラー**: 401が出た処理・対象語(Vera/Framton/Bertie?)・呼出経路・時刻・レスポンス(秘密をマスクして)・リトライ/フォールバックの挙動(401後に処理が止まったか、継続したか)、他のrun(X 2記事、melos)でも401が出ていたか(いつから)。
3. **原因切り分け**: 環境変数名の有無(値は出さない)、.env読込経路、キー形式の妥当性(長さ・prefixのみ)、エンドポイント/モデル名/認証ヘッダ形式が現行API仕様と一致するか、最小疎通呼出(1回、≤1円)で401が再現するか、別の正当な呼出でも401か(=キー無効/失効/残高/権限)。Claude側で解決可能か(設定・コード不具合)、ユーザー操作が必要か(キー再発行・課金・権限)。
4. **代替手段**: Perplexity不通時の現行フォールバック(事後Ledger登録が行われない→将来の同語でHR再発? PNAPはcmu_oov/ledger証拠で受理するか、①RET採用後は本文実体表で代替されるか)、承認済み発音品質と自動処理を維持できるかの評価(影響範囲: Khaite型の綴り供給B階層は人承認なので影響小? 等、証拠付き)。

## 成果物
`docs/research/PERPLEXITY-401-INVESTIGATION-01/INVESTIGATION_01.md`(秘密なし)。OPEN-473更新(原因・影響範囲・対応方針・ユーザー操作要否)、DECISION_LOG、REPORT_LEDGER。既存仕様内で修正可能な不具合(例: ヘッダ形式・env名の不一致)があれば修正→検証→commit(Production変更はその範囲のみ、Prompt/閾値変更なし、変更内容を明記)。commit時はsecret_scan `--staged` hits=0必須、`git push origin HEAD:main`。

## 禁止
APIキー・トークンの出力/commit、新規サービス、仕様変更、キーの作成・書換え(ユーザー操作)、他agentファイル編集。

## 報告(docs/pm/RESULT_PACKET_PPLX1.md)
(1)利用実態(工程・条件・X/Z・runtime証拠) (2)401の発生箇所・対象・時系列 (3)原因切り分け結果と復旧可否(Claude側/ユーザー側) (4)代替経路の品質評価 (5)ユーザー操作が必要な場合: 理由・具体操作・放置した場合の影響 (6)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。