FABLE-DELEGATION-MARKER: PNMH-F2-KPDUAL-VERDICT-委任_09-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_09 [F-2] + FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01 Fable判定記録: (1)多語同音救済PASSへの内部警告記録(ユーザー承認①)の実装とOPEN-439 Closeout、(2)Key Phrase両方PASSのFable判定`PRODUCTION_WIRED`記録。API 0・JPY0)

## 0. 運用ルール・並列注意
他agent稼働中: (E-1b)`er097_*`/`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/`、(記事A調査)`docs/research/FAMILY-X-B3-*`/`run_pp_02/audit`。D-2は完了(commit c9de15878)。あなたの編集対象: `er006_secondary_asr_01.py`(内部警告記録の最小追記のみ)、`er094_*`test、PNMH docs、SSOT行。共有ファイル編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan hits=0。push=`git push origin HEAD:main`。一時ファイルはforce-add禁止。SSOT全文読込禁止。他人の未commit差分(`er011_output/attempt_history.jsonl`等)を混ぜない。

## 1. (1) 内部警告記録(ユーザー回答①、2026-10-22逐語: 「同音救済PASS音声への警告ラベル：承認。内部記録のみとする。人間による試聴義務、Human Reviewへの自動転送、量産停止は追加しない。既存の記録機構を優先利用し、必要最小限の対応とする。警告記録のために追加APIを呼び出さない。」)
- 要件: 多語同音救済(`multiword_homophone_spans`が付いたPASS)に、内部記録用のラベル(例: `asr_judgement.internal_flags += ["MULTIWORD_HOMOPHONE_PASS"]`)を残す。**`warnings`配列には入れない**(`done()`が`PASS_WITH_WARNING`へ変換し事後試聴リストに載る=試聴義務の追加に当たるため)。state・試聴リスト・HR queue・停止条件は不変。既存の記録機構(`asr_judgement`/steps/adapterのadditiveキー)を使い、追加API 0。A-2で既に`multiword_homophone_spans`がsteps/adapter/`asr_judgement.adapter`に残っているため、追加は「集計しやすい単一フラグ」の最小追記に留める(既にそれで足りるなら、フラグ名の明文化とtestのみでもよい。その判断と根拠を報告)。
- test: 多語一致PASSでフラグが立ち、stateがPASSのまま・試聴リスト非掲載・HR非転送であること/1:1同音・通常PASSでは立たないこと/OFF時バイト一致。既存回帰(er094 35件、er096 wiring 62件、er006_multi_diff、secondary_asr_01_test、backcompat_07)PASS。
- SSOT: CURRENT_SPEC多語同音救済節に1行追記(内部記録フラグ名、試聴義務・HR転送・停止なし)。OPEN-439→`CLOSED_PRODUCTION_WIRED`(ユーザー受入2026-10-22、①実装済み、②不採用、③対応不要)。PLAN_SUMMARY Scope台帳更新(L1 Closeout、残=L2 Stage 1/2、U5既存の穴[未回答・悪化させないのみ]、J7)。UDR #138備考。
## 2. (2) Key Phrase両方PASS Fable判定記録(逐語で`docs/research/FAMILY-XZ-ASR-PASS-CONDITION-SPEC-AUDIT-01/IMPLEMENTATION_DESIGN_01.md`末尾とOPEN-440・CURRENT_SPEC新表の節に記入)
---
Fable判定(2026-10-22): `PRODUCTION_WIRED`。根拠=Family X(K2 profile・default `+dual1` profile)とFamily Zの正式初回経路で、KP英語フレーズの両Provider判定・呼出・採否・model_id・routingが記録され、初回dual PASSと、旧Store entry(Primary PASS/Azure NG)のS1不成立→再生成→dual PASSを観測。take part型(保存Azure転写10件)はdual PASS 0/10、実呼出でもNG_BOTH。KP英語解説・その他音声のAzure呼出0。再利用6点はfail-closed helper経由(test固定)。4,032ペア配線前後バイト一致、回帰2,339件PASS(既存失敗5件は無関係と分類)。量産影響(24 KP実測)=初回dual PASS 23/24、HR +約4%/KP(小標本)、追加原価+約JPY0.65〜0.89/10 KP音声、+0.5〜1.0秒/KP。Azure障害時に最終slotの技術STOPがHR Lockへ入る現行挙動(OPEN-371、2026-10-16 #86で当面許容)はdual化で露出が増えるが、障害時限定・実害未観測のため変更せず監視(OPEN-371へ追記)。手順逸脱の自己申告(`git add -f er096_output`、ignored混入0・実害なし)は記録のみ。
---
- OPEN-440→`CLOSED_PRODUCTION_WIRED`。OPEN-371に「KP dual化で露出増、監視、実害観測時に11-8で扱う」追記。UDR #139備考。DECISION_LOGに判定記録。REPORT_LEDGER。
- 記事B(ユーザー受入済み)のStore上KP 7種のS1結果(成立5: can't wait/fan stories/take part/story-maker/bring in、不成立2: think up[Azure「Think.」]/blurt[Primary「Blur.」])はOPEN-431履歴に「情報として記録、承認版は不変、次回X再利用時に再生成」と1行追記。
## 3. T-0・commit・報告
T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01_委任_09.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: PNMH-F2-KPDUAL-VERDICT-委任_09-20261022` を含むAgent tool_useの0始まり通番、259前後)。commit(対象のみ)→push→到達確認。`docs/pm/RESULT_PACKET_PNMH9.md`へ短い報告(実装内容・test結果・SSOT・commit・RESULT_PACKET 4行・JPY0・raw URL)。

## 4. 禁止
warnings配列への追加・state変更・試聴リスト/HR/停止条件の変更、追加API、KP dual/数値丸め/Stage 1のコード変更、他agent担当ファイルの編集。