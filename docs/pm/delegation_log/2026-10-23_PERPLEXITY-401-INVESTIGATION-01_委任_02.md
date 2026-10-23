FABLE-DELEGATION-MARKER: PERPLEXITY-401-INVESTIGATION-01-委任_02-RECOVERY-CHECK-20261023

# 委任_02: ユーザーがPerplexityクレジットを10ドル追加チャージ済み(2026-10-23共有)。最小疎通1回(sonar、max_tokens=5、1円以下)で復旧確認→OPEN-473 Close。秘密情報(キー値)は出力・保存しない。コード変更0。

## T-0
1. ユーザー原文(短文)を `docs/pm/delegation_log/2026-10-23_PERPLEXITY-401-INVESTIGATION-01_USER.md` へ逐語保存(jsonl最新userメッセージ「Perplexity APIのクレジットを…」)。
2. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_PERPLEXITY-401-INVESTIGATION-01_委任_02.md`(index 366以降、先頭MARKER一致)。
3. ACTIVE_TASK自分の行のみ(並行agent多数。pythonプロセスは自分が起動したPIDのみ終了可)。

## 実施
- 前回と同じ最小疎通(`docs/research/PERPLEXITY-401-INVESTIGATION-01/INVESTIGATION_01.md` の手順、`er006_pronunciation_research_01.py:92` と同一エンドポイント/認証方式)を1回実行。HTTP 200なら復旧。401/402等なら本文(秘密マスク)を記録し、原因候補(反映遅延/別プロジェクトへのチャージ/キー再発行要)を整理して終了。
- 200の場合: 正式関数 `research_pronunciations()` を1 topic(例: "Bertie")で1回だけ呼び、Ledger登録経路が通常どおり動くか(登録/否定記録の挙動、費用)を確認(≤1円)。Production成果物・Ledger本体への副作用があれば内容を記録(本来の挙動の範囲内なら可)。
- 復旧後の運用注意(残高監視・自動チャージ推奨)を `INVESTIGATION_01.md` 末尾に追記。
- OPEN-473=`CLOSED(2026-10-23 ユーザーが$10チャージ→疎通200確認)`(未復旧なら `USER_ACTION_DONE_STILL_FAILING` と原因候補)、DECISION_LOG、REPORT_LEDGER。
- commit(明示add)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_PPLX2.md)
疎通結果(HTTPコード・費用)、正式関数の動作確認結果、OPEN-473 Status、commit・raw URL。RESULT_PACKET 4行+「判定整合: 重大NG=なし/あり」。