# GPT6-MODEL-COMPARISON-TRIAL-01 REPORT (Phase A / Phase B)

**Status(Phase A)**: Trial計画確定のみ。**Status(Phase B、委任_02)**:
Step 1(重大fixture群)を実行し、`gpt-6-luna`に重大見逃し1件を検出したため
ユーザー決定どおり**STOPし、Step 2/Step 3は実行していない**。Trial終了Status候補
=`USER_DECISION_REQUIRED`(詳細は§Phase B-5)。Production code・Prompt・Checker・
Model Routing Contractの変更は一切行っていない。Opus起動なし。

本REPORTはPhase A/Phase Bの要約であり、詳細は設計書`docs/pm/design_gpt6_model_
comparison_trial_01.md`(§9にPhase B追記あり)を正とする。

---

# Phase B(委任_02、2026-09-29)

## Phase B-1. `gpt-6-sol`互換性probe結果

1 call実行(`er050_output/gpt6_sol_probe_result.json`)。**SUCCESS**。

| 項目 | 結果 |
|---|---|
| status | SUCCESS(エラーなし・timeoutなし) |
| model_returned | `gpt-6-sol` |
| response_id | `resp_004c44a5ce42091a006abb79fcebfc87d0ab7947c4cacc6fff` |
| reasoning="high" | 受理(reasoning_tokens=17、Phase Aのluna/astra probeでは0だったが今回は非ゼロを観測) |
| text.format.type=json_schema + strict:true | 受理、schemaどおりのJSONを返却 |
| elapsed_seconds | 3.716 |
| input/output tokens | 67 / 40 |

**比較対象には追加していない**(ユーザー決定どおり、Luna/Solで不足時の第二候補としての
位置づけを維持)。参考換算費用: ¥0.0098(無視できる額)。

## Phase B-2. Trial実行条件(sha256固定の証明)

`er050_gpt6_checker_comparison_trial_01.py::verify_fixed_constants()`が起動時に
以下3点をPhase A記録済みsha256と突合し、不一致ならRuntimeErrorでSTOPする設計
(実行時に例外なく通過、固定性確認済み):

| 定数 | sha256(Phase A記録=今回実測、完全一致) |
|---|---|
| `DEVIATION_PROMPT_TEMPLATE` | `d3ad565d6d2b3b156c01156295d02c2c14ac33816767ea05af4eb963e5afefc9` |
| `DEVIATION_DEVELOPER_MESSAGE` | `28d7efc6d289a246ddcf71da118ca175af86dd2001fe1ca4725a5c534c299b2b` |
| `DEVIATION_JSON_SCHEMA`(sort_keys） | `bf6858126fc5888b43d84f06e0c9f6f550415516d2c9ca6ef6269f7229ed407f` |

A/B/Meta群fixture(A2A3/A4/A5/B1/B2/B3/B4/Meta run_03 Standard)は、既存audit json
保存済みの`prompt`文字列からテンプレート逆展開方式(`extract_inputs_from_prompt()`)で
`verified_ledger_text`/`article_text`/`source_article_text`を復元し、
`verify_reconstruction()`で再度テンプレートへ通した結果が保存済み`prompt`と
**byte単位で完全一致**することを全8件で検証済み(mock test
`test_reconstruction_matches_for_all_audit_fixtures`、および実行時`load_audit_fixture()`
内で例外なく通過)。A2A3/A4/B1/B2/B3/B4/Metaのsha256は設計書§3の実測値と完全一致
(mock test `test_audit_fixture_sha256_matches_design_doc`でも固定)。

model引数のみが2モデル間で異なり、他の`client.responses.create()`引数
(`input`/`reasoning`/`text`)が完全一致することもmock test
`test_model_is_only_varying_argument`で検証済み。

**A-1は実行対象外**(design書自身が「検出漏れ自体を再現したfixtureではない」と明記
済みの是正後recheckファイルのみで、promptキーを持たず再実行不可。ハーネス内
`A1_NOTE`に理由を記録)。**A5は設計書記載パス(`must_fix_retry_result.json`、retry後
COMPLIANT結果)ではなく、同一run内の是正前ファイル(`meta/deviation_check_trial.json`、
MAJOR検出時点の原本、fact_id=MUSE-HC-012が完全一致)を実際のfixture inputとして採用**
(新規fixtureの捏造ではなく、既存実データの中から再現可能な原本を採用しただけ、
REPORT内に理由明記)。

## Phase B-3. Step 1: 重大fixture群結果(ER-009-N1 9種 + A2A3 + A4 + A5、新旧各1回)

| fixture | gold(期待) | gpt-5.6-luna(baseline) | gpt-6-luna | 判定 |
|---|---|---|---|---|
| er009_changed_number | MAJOR, changed_number=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| **er009_changed_actor** | **MAJOR, changed_actor=true** | **MINOR(changed_actor=true だがseverity=MINOR)** | **LEDGER_COMPLIANT(0 MAJOR)** | **両者MISS(baselineもMISS)** |
| er009_changed_scope | MAJOR, changed_scope=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| er009_changed_causality | MAJOR, changed_causality=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| er009_changed_certainty | MAJOR, changed_certainty=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| er009_changed_negation | MAJOR, changed_negation=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| er009_changed_comparison | MAJOR, changed_comparison=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| er009_changed_time | MAJOR, changed_time=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| er009_unsupported_new_claim | MAJOR, unsupported_new_claim=true | MAJOR, flag=true | MAJOR, flag=true | 両者PASS |
| A2A3 | LEDGER_DEVIATION(MAJORx3件相当) | MAJORx2 | MAJORx2(flag構成が一部異なる) | 両者PASS(MAJOR維持) |
| A4 | LEDGER_DEVIATION | MAJORx1(changed_scope) | MAJORx2(unsupported_new_claim+changed_certainty) | 両者PASS(MAJOR維持、gpt-6は検出件数増) |
| A5 | LEDGER_DEVIATION、changed_fact | MAJORx1(changed_fact) | MAJORx1(changed_fact+changed_negation) | 両者PASS(MAJOR維持) |

**BLOCKING維持率(ER-009-N1、9件中)**: baseline 8/9(88.9%)、gpt-6-luna 8/9(88.9%)。
**新たな重大見逃し**: `er009_changed_actor`で発生。ただし**baselineも同一n=1実行で
同時に見逃した**(baselineはseverity=MINORと判定、Ledger Deviation Checkerの
prompt上のルール「10種のいずれかが明確にtrueならMAJORにする」に本来従えば
changed_actor=trueでMAJORになるはずだが、モデルがMINORのまま返した。post-hoc
validationはMAJOR→MINORの自動降格のみを行い、MINOR→MAJORへの補正は行わない設計
のため、この非対称性がそのまま出力に反映されている)。gpt-6-luna側はそもそも
`changed_actor`フラグ自体をfalseと判定し、deviation自体を報告しなかった
(baselineより検出力が低い可能性、または単なる非決定性の可能性のいずれも否定できない
=n=1のみでは切り分け不可)。

**ユーザー決定「gpt-6-luna に重大見逃しがあれば STOP」に該当するため、Step 2/Step 3は
実行せず本委任をここでSTOPした**(Step2/3の追加実行はしていない)。

## Phase B-4. Cost / Latency(Step 1のみ)

| model | n | 参考換算合計(¥) | latency中央値(秒) | latency最大(秒) | input tok平均 | output tok平均 | reasoning tok平均 |
|---|---|---|---|---|---|---|---|
| gpt-5.6-luna | 12 | 5.72 | 7.85 | 42.06 | 5113.8 | 1628.7 | 1361.6 |
| gpt-6-luna | 12 | 5.13(同一参考レート換算、実単価未確認) | 9.24 | 33.94 | 5113.8 | 1375.2 | 1107.9 |

累計参考換算(Step1のみ): ¥10.85(`er050_output/gpt6_checker_comparison_trial_01/
summary_step1.json`の`cumulative_ref_jpy`)。Sol probe(¥0.0098)を含めても
**累計¥10.86**で、Guardrail上限¥300の3.6%程度。error率0%(24/24 call成功)。
retry機構は本harnessでは使用していない(must-fix retry等はProduction側の機構、
Trial harnessは単発run_deviation_check()呼び出しのみ)。

gpt-6-lunaはreasoning tokens平均が baseline比 約-18.6%(1361.6→1107.9)、
output tokens平均も約-15.6%少ない。latency中央値はgpt-6-lunaの方がやや遅い
(7.85秒→9.24秒)が、最大値はgpt-6-lunaの方が短い(42.06秒→33.94秒)。n=12のみで
統計的な結論は出せない。

**GPT-6単価は未確認のため、上記参考換算はgpt-5.6-luna単価をそのままGPT-6にも
適用した仮の値であり、実費ではない**。token数(input/output/reasoning)を一次記録
として`er050_output/gpt6_checker_comparison_trial_01/step1/**/run_1.json`へ保存済み。

## Phase B-5. リスク / 未解決問題 / Trial終了Status候補

- **最大のリスク**: `er009_changed_actor`のMISSが「gpt-6-luna固有の検出力低下」なのか
  「Checker自体(prompt+モデル)の単純な非決定性」なのかを、本Trialのn=1実行では
  切り分けられない。baselineも同一n=1で同時にMISSしたことは、後者(非決定性)の
  可能性を示唆するが、断定はできない(Step3で計画していた非決定性測定[n=5反復]は
  STOPにより未実行のため、この切り分けに必要なデータが取得できていない)。
- 発見事項: post-hoc validationがMAJOR→MINORの自動降格のみを行い、MINOR→MAJORへの
  補正を行わない設計上の非対称性が、今回のchanged_actor MISSで可視化された
  (baseline側: changed_actor=trueなのにseverity=MINORのまま出力された)。これは
  Production Checkerの既存設計そのものであり、本Trialで新たに変更・提案するもの
  ではない。設計判断が必要と考えられる場合はユーザー/Fable判断へ回す
  (Production code変更はしていない)。
- Step 2(境界・過剰品質群)・Step 3(非決定性)は未実行のため、Over-blocking改善・
  Stability改善の実測データは**本委任では取得できていない**。
- Sol probeはSUCCESSしたが、比較対象への追加はユーザー決定どおり見送り。

**Trial終了Status候補**: `USER_DECISION_REQUIRED`。根拠: (1)ユーザー事前決定の
STOP条件(gpt-6-lunaの重大見逃し)に文字どおり該当したため機械的にSTOPしたが、
(2)同一fixtureをbaselineも同時に見逃しており、これがgpt-6-luna固有の後退か
既存Checkerの非決定性かの区別ができていない。続行(Step3非決定性測定の先行実行、
または当該fixtureのみ追加反復)するか、ここで`REJECTED`として打ち切るかは
Product判断が必要(**Claudeが独自に続行判断はしない**)。

**USER_DECISION_REQUIRED候補fixture**: `er009_changed_actor`
(baseline/gpt-6-luna両方が同一n=1実行でMISSした事実、post-hoc validationの
非対称設計、n=1のみでの評価の限界、の3点をあわせて判断材料とする)。

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
