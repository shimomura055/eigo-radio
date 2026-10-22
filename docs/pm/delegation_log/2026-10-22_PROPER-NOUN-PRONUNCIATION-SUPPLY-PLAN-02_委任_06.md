FABLE-DELEGATION-MARKER: PNPS-STAGE1-VERDICT-委任_06-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_06: Stage 1のFable判定記録とStage 2計画v4の提出Status記録。API 0・JPY0・コード無変更)

## 0. 運用ルール
他agent稼働中: (C-3)記事A再制作=`er019_output/paycheck_personality/run_pp_02/`・`user_test/paycheck_personality_e2e_02/`・OPEN-437/442。あなたはSSOT行とPNPS docsのみ。共有ファイル編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。`git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan hits=0。push=`git push origin HEAD:main`。一時ファイルはforce-add禁止。SSOT全文読込禁止。他人の未commit差分を混ぜない。

## 1. 記録するFable判定(逐語。`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/STAGE1_IMPLEMENTATION_DESIGN_01.md`末尾、OPEN-441、CURRENT_SPECのStage 1節Status、DECISION_LOGへ)
---
Fable判定(2026-10-22): Stage 1=`PRODUCTION_WIRED`(条件付き残事項あり)。根拠=X/Z共通の`evaluate_attempt_with_cascade_detail`内に配線、判定基準・自動PASS条件は不変(ON/OFFで実関数の判定出力一致、保存HR 79行の再判定差分0、4,032ペアはバイト一致、Ledger upsertキー無し呼出は配線前版とバイト一致)。実関数での発火=X(crosslevel)・Z(er063 kp_en)でmock注入により最終slot NG→調査→出典ページ照合→Ledger登録/USE_LEDGER/否定記録/SKIP_NEGATIVE_CACHEの各分岐を記録。実機で一般語(`good morning`/`main story`)の調査不呼出とLedger命中時の調査0を確認。出典ページ照合は保存済み調査結果3語の実HTTP取得で動作確認。`mini`隔離(OPEN-436の枠)はPhrase List差分18文(mini由来のみ)・M1候補集合差0・判定差分0。**残事項(完了と誤認しない)**: (1)実調査API(Perplexity)の端から端の確認は枠切れ(401、UDR #134未回答)のため未実施。枠復旧後に1語で確認する。(2)否定記録・別type採用の自然発生は未観測(過去データで発火0)。(3)「引用実在確認」はStage 1では弱い照合(出典ページに名称・発音表記の出現確認)のみ。本来の引用確認はStage 2の調査形式変更(Prompt変更=別承認)と同時。費用JPY0。
---
## 2. Stage 2計画v4
- OPEN-441→`STAGE1_PRODUCTION_WIRED(残事項あり) / STAGE2_PLAN_V4_SUBMITTED_PENDING_USER`。
- `docs/pm/USER_DECISION_REGISTER_01.md`: #142(Stage 2設計方針)に「計画v4提出(2026-10-22)。判断事項=(1)Stage 2 Trial実行とCap JPY100、(2)既存1:1同音判定とL1の安全条件変更(1837(B)例外、推定/公式発音をcanonical側基準に使う)、(3)G2P(g2p_en等)の導入(Trial内利用はFable可・本番依存はユーザー)、(4)#134 Perplexity枠(Stage 1残事項・Stage 2 R1の前提)。Fable推奨=(1)はG2PをTrial内で試す前提で実施(Cap JPY100)、(2)はTrial結果後、(3)Trial結果後、(4)復旧推奨(Stage 1/2の前提、外部課金のため金額確認はユーザー)」を追記。
- REPORT_LEDGER行。T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_委任_06.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: PNPS-STAGE1-VERDICT-委任_06-20261022` を含むAgent tool_useの0始まり通番、262前後)。
- commit(対象のみ)→push→到達確認。`docs/pm/RESULT_PACKET_PNPS6.md`へ短い報告(変更ファイル・commit・RESULT_PACKET 4行・JPY0)。