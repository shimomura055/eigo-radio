# PREREGISTRATION_02: B3-ANNOTATION-AUTOMATION-TRIAL-01 Phase 2(2026-10-10、ユーザーGo済み。結果を見て変更しない)

PREREGISTRATION_01(M-A/M-B/Sol/Astra案)はユーザー方針で置換された。本書が実行時の正本。Production/Prompt/CURRENT_SPEC/Production routing変更なし。DEV/Trial専用。

## 1 方式(ユーザー方針)
B3 -> LLM注記1回 -> 機械検査(既存 b3_annotation_check_01.run) -> 保存。
A注記/B注記/A-B統合/Union/多数決/second-pass Checker/自動Correction/新補助Checker は使わない。複数回実行は再現性測定用の独立反復であり合成しない。

## 2 モデル(25節: 開発・評価は最新世代の推奨系)
- Sonnet系: `claude-sonnet-5-5`(Trial時の注記workerと同名)。Anthropic models list(無料)で実在確認済み(2026-10-10、created 2026-09-28)。代替なし。
- Luna: `gpt-6-luna`(Production routing上の正式model_id、er006_model_routing_contract_01.py WRITER_MODEL。OpenAI models listで実在確認)。actual model_id(応答値)を各runに保存。
- Astra/Sol/Haiku等は追加しない。旧/下位モデル不使用。
- 価格: claude-sonnet-5-5 = in $2 / out $10 / cache hit $0.10 per MTok(https://platform.claude.com/docs/en/about-claude/pricing 取得 2026-10-10)。gpt-6-luna = in $0.10 / cached $0.01 / out $0.50(pricing_snapshot.json)。USD/JPY=160。

## 3 Prompt・入力
Phase 1で出所検証済み(sha一致)の既存Trial Prompt `factlock_astra_e2e_trial_01/annotation/prompts/<slug>__A.md` の依頼文を逐語で1つのuserメッセージとして渡す(system無し=dry_runと同一)。改善・v2.1化・補足追加禁止。入力は凍結済みstage_r。Prompt自体の問題はTrial結果と分離して報告する。
Provider既定: 旧TrialはClaude Code subagent実行でAPIパラメータ記録なし -> temperature/top_p等は未指定。Anthropic: max_tokens=16000のみ(必須)。OpenAI: Responses API reasoning.effort=medium, max_output_tokens=16000(dry_run payloadと同一)。

## 4 実験設計
10入力(正式9+inbound_tourismストレス) x 各モデル2反復の独立呼び出し = 40 call(Luna 20 -> Sonnet 20の順)。2反復の理由=同一入力の揺れを対比較で測る最小数(3回以上は費用に見合わない)。技術retryのみ(通信/429/5xx、最大2回)。結果(出力内容)を見た再実行はしない。形式FAIL/STOP返答も再生成しない(そのまま結果)。

## 5 見積・費用ガード
Phase 1見積(estimate_01.json): Sonnet 40call相当 低JPY207/中503/高927、Luna約1/20(約JPY10〜46)。総額 低約JPY217/中約530/高約973(本設計は同一token量)。
- 累計JPY1,200到達で残りを実行せずSTOP。
- 最初のテーマ(各モデル1 call)の実測tokensで見積を再計算し、高位見積の2倍を超える見込みなら停止して報告。

## 6 指標
モデル別: 機械検査PASS率、1記事注記cost(実測)、latency、Fact境界一致/タグP-R-F1(対GT)、中核/周辺分類一致、Fact ID(ledger_ids)一致、本文非改変、反復間(完全一致率・差分箇所数・差分種別)、Claude側内容分析(Fact/指示の分離、境界、分類、書換え、癖、意味上危険な差分件数)。
GTは旧Trialの同一Sonnet系2回出力の決定論統合であり人間正解ではない。GT一致率/F1/Fact ID一致/中核周辺一致は参考指標。形式PASS(機械検査PASS)は意味的正しさを保証しない。
評価母集団=正式9テーマ。inbound_tourismはストレス入力(指標に含めない)。

## 7 Closeout語彙
REJECTED / VALIDATED / USER_DECISION_REQUIRED のみ。VALIDATEDでもAPPROVED_FOR_PRODUCTIONではない(採用は人間ユーザーのみ)。
事前の目安(結果を見て動かさない): VALIDATED候補=機械検査PASSが各モデルの採用候補で高率かつ意味上危険な差分が少数で反復が安定。REJECTED=形式/本文改変が頻発または危険誤注記が多数。それ以外/モデル間で割れる/Prompt由来の問題が大きい=USER_DECISION_REQUIRED。

## 8 やらないこと
結果を見たPrompt修正・再Trial、新補助Checker追加、Production配線、A/B二重化の実行(再検討は条件該当時の提案のみ)、仕様v2/検査script/GT変更。
STOP条件: Sonnet系不明(解消済み)/PromptがAPIで使えない/機械検査の不具合発見/B3入力が過去Trialと意味的に異なる/費用が見積から大幅乖離/新仕様が必要/危険誤注記を見てPrompt修正したくなった場合。
