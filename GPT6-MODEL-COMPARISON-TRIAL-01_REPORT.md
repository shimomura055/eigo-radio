# GPT6-MODEL-COMPARISON-TRIAL-01 REPORT (Phase A)

**Status**: Phase A(Trial計画確定のみ)。**Phase Bは未実行**。Production code・
Prompt・Checker・Model Routing Contractの変更は行っていない。Opus起動なし。

本REPORTはPhase Aの要約であり、詳細は設計書`docs/pm/design_gpt6_model_comparison_
trial_01.md`を正とする(本REPORTは同設計書へのポインタと、実施したAPI確認結果の
要約のみを収録する)。

---

## 1. 対象モデル実確認結果(要約)

- 現行baseline: `gpt-5.6-luna`(reasoning effort実測値`"high"`)。
- `GET https://api.openai.com/v1/models`実行(2026-09-29、環境変数key使用・keyは
  一切出力に含めていない)。全132モデル中、`gpt-6`を含むidが**3件実在**:
  `gpt-6-luna` / `gpt-6-sol` / `gpt-6-astra`。推測ではなくAPI実測。
- endpoint/API互換性probe(scratchpad上の自作スクリプト、現行`vfl01.run_deviation_
  check()`と同一のResponses API呼び出し形式[`reasoning={"effort":"high"}`+
  `text.format.type="json_schema"`+`strict:true`]を使用): `gpt-6-luna`・
  `gpt-6-astra`の計2 callとも**SUCCESS**(エラーなし、`reasoning_tokens=0`)。
  `gpt-6-sol`は費用上限(¥5、probe 1〜2 callまで)の都合上probe未実施(未確認)。
- 単価: `curl`で公式価格ページ取得を試みたがHTTP 403、**未確認(ユーザー提示待ち)**。
  推測値・旧モデル単価の流用はしていない。

## 2. Fixture構成(要約)

- 重大事故群: ER-009-N1危険fixture 9種(存在確認OK、sha256実測)+調査REPORT A群5件
  (存在確認OK、sha256実測、うちA-1は「検出漏れ事例」の是正後recheckのみ記録)。
- 過剰品質/境界群: B群4件+Meta run_03 Standard translation MAJOR 1件(全件存在確認
  OK、sha256実測)。
- 非決定性群: Hormuz run_01〜03(存在確認OK)、run_02/run_03のLedgerがsha256完全一致
  (同一入力での非決定性測定に使用可能)、run_03内でAdvanced(COMPLIANT)/Standard
  (MAJOR)の判定不一致を実データで確認。
- category被覆: 10category中6種(changed_fact/scope/causality/certainty/comparison/
  unsupported_new_claim)は実運用incidentデータあり。**4種(changed_number/actor/
  negation/time)はER-009-N1合成fixtureのみでfixture不足**(実データなし、新規作成は
  未実施)。

## 3. 比較条件・受入条件案・費用/Guardrail案・リスク

設計書§4〜§8を参照(Prompt/Schema/Validatorのsha256固定・model引数のみ差替え、
重大fixture維持率100%等の受入条件案とその根拠、GPT-6単価未確認のため現行単価仮置きの
概算費用[Checkerのみ約¥162〜180程度、確定額ではない]、Guardrail段階発火案、API非互換・
単価未確定・goldラベル再現性・fixture数の少なさ等のリスク)。

## 4. 未解決・未確認事項

- GPT-6候補3件のうちどれを比較対象とするか(ユーザー判断待ち)。
- GPT-6単価(未取得)。
- `gpt-6-sol`のendpoint互換性(probe未実施)。
- Trial harnessがModel Routing Contractを経由するか直接指定するかの方式(Phase B設計時に確定)。

## 5. Phase A終了時点のStatus

`USER_DECISION_REQUIRED`(候補選定・単価確認がユーザー判断待ちのため)。
**Phase B(大量実行)は本タスクでは開始していない**。

## 6. Evidence

- 設計書: `docs/pm/design_gpt6_model_comparison_trial_01.md`
- delegation記録: `docs/pm/delegation_log/2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_01.md`
  (T-0 check結果: `status: FAIL`、理由は委任文中のplaceholder表記2箇所、必須項目8件は
  全てOK。詳細は設計書冒頭を参照)
- probe実行ログ(要約、詳細は上記1節): `gpt-6-luna`/`gpt-6-astra`各1 call SUCCESS
