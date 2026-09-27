# 委任文全文(2026-09-27、KEY-PHRASE-DB-HYBRID-TRIAL-03、Sonnet委任 追加評価run)

管理ID: KEY-PHRASE-DB-HYBRID-TRIAL-03(追加評価run、ユーザー指定 2026-09-27)。一時ファイル `docs/pm/ACTIVE_TASK_KPH4.md` / `docs/pm/RESULT_PACKET_KPH4.md`(commitしない)。委任文全文を `docs/pm/delegation_log/2026-09-27_KEY-PHRASE-DB-HYBRID-TRIAL-03_02.md` に保存しcommitに含める。Guardrail **¥60**(STOP閾値 ¥50)、事前見積>¥50なら実行前にSTOP報告。APIキーは環境変数のみ。

## ユーザー指定(逐語)
「https://shimomura055.github.io/eigo-radio/user_test/articles_2026_0918.html / Why We Wake Before the Alarm / なぜ目覚まし前に目が覚める？ / When AI Helps Choose Who Gets Hired / AIが採用を選ぶとき / Digital Twins: A Copy of the Real World / デジタルツインとは何か / 上記記事のA2/B1の６本文」
Fable解釈: Trial-03の「新規記事評価」は、新規生成(¥44)ではなく**この既存3記事×A2/B1=6本文**を対象に行う。新規記事生成はしない。既存記事(Family A legacy)は**read-onlyの入力**としてのみ使用し、記事側artifactは一切変更しない。

## 先出しRead
- `KEY-PHRASE-DB-HYBRID-TRIAL-03_REPORT.md`(確定版方式、§7 9観点、§9 cost分解、STOP条件8項目)
- `er028_key_phrase_db_hybrid_trial_03_run.py` / `_stage1.py`(確定版ルールを**無変更**で使う。バグ修正が必要になっても本runでは変更せず報告のみ)
- `user_test/articles_2026_0918.html` から3記事の本文パス(article.md/text)・既存Production Key Phrase(公開済み最終5件)・レベル(A2/B1)を特定。パス特定根拠をRESULT_PACKETに記録。

## 作業
1. 6本文に確定版Trial-03方式(DB screening → compact shortlist + Topic見出し再利用 → Strategy L 1回)を適用。記事全文非送信assertion有効。**共有ストア(pronunciation ledger / master audio store / human_review_queue / telemetry)へ書き込まない**(Strategy L経路で書き込みが発生する場合はTrial-local化しREPORTに明記)。
2. 出力: `er028_output/key_phrase_db_hybrid_trial_03/run_02_user_test_0918/`(6本文の shortlist / prompt / 選定結果 / cost / structural gate結果)。
3. 比較: 各本文で「Trial-03選定5件」vs「既存Production公開KP 5件」を並べ、§7の9観点で評価。一致件数、入替え候補の妥当性、重要語保持(記事の核心語句)、単語比率(word vs phrase)、既知bug A〜E再発の有無、STOP条件8項目の該当有無。
4. cost: 本文ごとのinput/output tokens・¥、6本文平均、Trial-03 §9(Family X 6本文)との比較。これらは300〜400語級か、長い記事かも記録(§9の「長い記事での効果は未検証」への回答になる)。
5. REPORT §15「追加評価run(既存user_test 2026-09-18 3記事×A2/B1)」を追記。Status候補(`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`)を提案(確定はFable/ユーザー)。**Production配線・APPROVED_FOR_PRODUCTION化は行わない。**
6. unit test(er028 30件)無変更でPASS再確認。

Git: 新規出力・REPORT・delegation_logのみpath指定add(`git add -A`禁止、他Agent[er022_* / er019_* / er025_* / SSOT 3点]のstageを外さない、index.lockリトライ)。トレーラー `Management-ID: KEY-PHRASE-DB-HYBRID-TRIAL-03`。push origin main。reset/amend/rebase/force push禁止。RESULT_PACKETに費用合計・commit hash・変更ファイル・6本文比較表の要約を記載。
