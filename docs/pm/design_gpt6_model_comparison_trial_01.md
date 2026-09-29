# GPT-6 Model Comparison Trial 設計書(Phase A) — GPT6-MODEL-COMPARISON-TRIAL-01

作成日: 2026-09-29。管理ID: `GPT6-MODEL-COMPARISON-TRIAL-01`(Phase A、委任_01)。

**本ファイルの性質**: Phase A(Trial計画確定のみ)。**Phase B(大量実行)は本ファイルでは
実施しない**。Production code・Prompt・Checker・Model Routing Contractは一切変更しない。
Opus起動なし。到達Status: `USER_DECISION_REQUIRED`(GPT-6候補が複数存在し選定はユーザー
判断のため、詳細は末尾)。

**T-0 delegation prompt check結果(1行)**: `docs/pm/delegation_log/
2026-09-29_GPT6-MODEL-COMPARISON-TRIAL-01_01.md_check.json` → `status: FAIL`(理由:
「実行コマンド全文」中の2行(`probe: ...\gpt6_probe.py`のscratchpad部分、`価格:
curl -s <公式価格ページURL>`)がplaceholder形式と判定されたため。委任文はT-0の指示通り
逐語保存しており、実際のprobe実行は§1-3のとおり具体的な絶対パス・model_id引数で実施した
[placeholderはあくまで委任文側の一般化表現])。必須キーワード8項目は全てOK、固定ブロック
E-1/D-1/G-1/F-1も全てOK。TTS関連warning2件は本タスクがTTSを一切伴わないため誤検知
(委任文中の「T-2: TTSなし」という否定文言に反応したものと推定、実害なし)。

---

## 1. 対象モデル(推測禁止、実確認結果)

### 1-1. 現行baseline

`gpt-5.6-luna`(`er006_model_routing_contract_01.py:33` `WRITER_MODEL`。Checker
[`vfl01.run_deviation_check()`]はデフォルト引数`model: str = MODEL`で
`MODEL = routing.WRITER_MODEL`を継承)。reasoning effort実測値: `"high"`
(`er003_v1_en_direct_vfl_01_generate.py:58` `REASONING_EFFORT =
r3.WRITER_REASONING_EFFORT`、さらに`er002_ja_web_research_r3.py:42`
`WRITER_REASONING_EFFORT = restore.WRITER_REASONING_EFFORT  # "high"`まで遡って確認)。

### 1-2. GPT-6候補(実在確認済み、API実行結果)

2026-09-29、`GET https://api.openai.com/v1/models`(環境変数`OPENAI_API_KEY`で認証、
出力からkey本文は一切含めていない)を実行し、全132モデルのidを取得した。
`gpt-6`を含むidは以下**3件**存在した(推測ではなくAPI実測)。

| model_id | 現行baselineとの対応 |
|---|---|
| `gpt-6-luna` | `gpt-5.6-luna`と同一codename系統(Production全Roleが使用する現行baselineの後継候補) |
| `gpt-6-sol` | `gpt-5.6-sol`(2026-08-22以前の旧Approved Model)と同一codename系統 |
| `gpt-6-astra` | 現行Contractに対応するcodenameなし(新規系統) |

参考: `gpt-5.x`系は`gpt-5`/`gpt-5.1`/`gpt-5.2`/`gpt-5.3`/`gpt-5.4`/`gpt-5.5`/
`gpt-5.6-{luna,sol,terra}`まで実在を確認した(`gpt-5.6-terra`は現行Contract未使用の
第3のcodenameが既に存在することが判明、GPT-6側の`gpt-6-astra`と合わせて「luna/sol以外の
codenameも実在する」という事実は本Trial設計の候補選定に影響しうるため記録する)。

**候補選定はユーザー判断へ回す**(3候補のうちどれを比較対象とするかは本委任の推測禁止
条項に従い決定しない)。ただし現行Production全Roleが`gpt-5.6-luna`に統一されている事実
(`docs/pm/gpt6_trial_preparation_01.md`§1-1)を踏まえると、**`gpt-6-luna`が最も自然な
第一候補**であることは事実として記録する(選定そのものはユーザー判断)。

### 1-3. endpoint / API互換性(probe実測)

現行Checker(`vfl01.run_deviation_check()`、`er003_v1_en_direct_vfl_01_generate.py:773-852`)
の呼び出し形式をGrepで特定した:

- endpoint: **Responses API**(`client.responses.create()`。Chat Completions APIではない)
- reasoning: `reasoning={"effort": REASONING_EFFORT}`(`REASONING_EFFORT = "high"`)
- structured output: `text={"format": {"type": "json_schema", **schema}}`(`"strict": True`)
- input形式: `input=[{"role": "developer", "content": ...}, {"role": "user", "content": ...}]`
- 戻り値取得: `response.output_text`をJSON parse、`response.usage.input_tokens` /
  `output_tokens` / `usage.output_tokens_details.reasoning_tokens`

この**同一形式**で`gpt-6-luna`・`gpt-6-astra`の2候補に対し最小probe(固定の短い
developer/userメッセージ、`strict: true`のJSON schema、`reasoning={"effort": "high"}`)を
各1回実行した(scratchpad上の自作スクリプト`gpt6_probe.py`、repoに追加していない、
Production/Trial実行コードとは独立)。

| model_id | 実行結果 | model_returned | elapsed(秒) | input/output/reasoning tokens |
|---|---|---|---|---|
| `gpt-6-luna` | **SUCCESS**(reasoning受理・json_schema strict受理) | `gpt-6-luna` | 3.778 | 73/22/0 |
| `gpt-6-astra` | **SUCCESS**(同上) | `gpt-6-astra` | 3.196 | 73/23/0 |

両候補とも、現行Checkerと完全同一の呼び出し形式(Responses API・`reasoning`パラメータ・
`json_schema strict`)を**エラーなく受理**した。両candidateとも`reasoning_tokens=0`が
返った(このprobeの入力は自明なタスクのため、reasoning effort="high"を指定しても実際に
reasoning tokenが消費されなかった可能性が高いが、断定はしない。Phase B実行時の実
fixture[複雑な判定]では非ゼロになる可能性がある)。`gpt-6-sol`は費用上限(¥5、probe
1〜2 call)の都合上probeを実行していない(**未確認**、Phase B候補選定前に必要なら
追加probe要)。

### 1-4. 単価(未確認)

公式価格ページ(`https://openai.com/api/pricing/`)へ`curl`を実行したが、HTTP 403
(bot対策等によりコマンドラインからの直接取得不可と判断)。**GPT-6系(luna/sol/astra
いずれも)の単価は本タスクでは取得できず、「未確認(ユーザー提示待ち)」とする**。
推測値・現行`gpt-5.6-luna`単価の流用は行わない。参考情報としてのみ、現行`gpt-5.6-luna`
単価(`er005_output/cost_baseline_01/pricing_snapshot.json`: input $0.20/M・cached
$0.02/M・output $1.20/M)を`docs/pm/gpt6_trial_preparation_01.md`§3-2から引用するが、
これはGPT-6の単価ではない。

### 1-5. 利用可能設定(probe実測)

probe応答から確認できた範囲: `reasoning={"effort": "high"}`受理・`text.format.type=
"json_schema"`+`strict: true`受理・structured output(`ok: boolean`, `note: string`の
2フィールドschema)を正しくJSON化して返却。`temperature`パラメータは今回のprobeでは
指定していない(未確認、現行Checkerコードも`temperature`を指定していないため今回は
テスト対象に含めなかった)。

---

## 2. 比較対象Role

**第1優先(本Trialの主対象)**: Ledger / Deviation Checker
(`vfl01.run_deviation_check()`)。JA Fact Check・EN Advanced・EN Standardの3箇所で
**完全同一の1関数**が使われている(`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_
REPORT.md`§1-0で確認済み、区別は`hook_aware`/`source_article_text`等の引数のみ)。
OPEN-233の主目的に対応し、§3のEvidenceが最も揃っている。

**第2段以降(候補列挙のみ、本管理IDのPhase B範囲外・別Phase)**:
1. Writer(JA Original/R1/R2、`WRITER_MODEL`)
2. Translation(Advanced忠実英訳、`NATURAL_ENGLISH_ADAPTATION`)
3. Standard simplification(`STANDARD_A2_ADAPTATION`)
4. Comment/Key Phrase(`SUPPORT_MODEL`、reasoning effortがhigh/medium混在する点に注意
   [`KEY_PHRASE_ADVANCED_EXPLANATION`はmedium])

---

## 3. Checker fixtureの固定

**方針**: 存在確認・sha256・現行判定の記録のみ。コピー・実行はしていない
(全パスは本タスクで実sha256sum/Python jsonロードにより実測、以下は実測結果)。

### 3-1. 重大事故群(ER-009-N1危険fixture 9種)

`er009_ledger_deviation_recalibration_02_test.py:24-63`(`FIXTURES`辞書)。基準Ledger・
結果ファイルとも存在確認OK(実sha256実測):

| ファイル | sha256 |
|---|---|
| `er006_output/pool_pilot_01/pool_n9_tip_screens/research/verified_fact_ledger.txt` | `d0d732fd02e6e3b5df5239dcb7152e72011275a4665e5124b8bf9182c7081b95` |
| `er006_output/pool_pilot_01/pool_n9_tip_screens/false_negative_fixture_results.json` | `5a9053a7d36dece6edf8f159cf874240eb4241847f7bd614149ae712a638c47e` |

9種のfixture名=category(逐語、コード上のkeyと完全一致): `changed_number`/
`changed_actor`/`changed_scope`/`changed_causality`/`changed_certainty`/
`changed_negation`/`changed_comparison`/`changed_time`/`unsupported_new_claim`。
各fixtureの記事断片本文はtest file内に直接記載済み(§4-1参照、本書への転記省略)。
gold判定: 全9種とも「MAJOR(かつ対応するchanged_*フラグ=true)」が正解(fixtureの設計
意図そのもの、既存9/9 PASS実績が`false_negative_fixture_results.json`に記録済み)。

### 3-2. 調査REPORT A群5件(重大、明らかに止めるべき)

| # | パス | sha256 | 現行判定(実測) |
|---|---|---|---|
| A-1 | `er019_output/family_x_b3_production_wiring_01/run_01/audit/fact_fidelity_fix_01_recheck_summary.json` | `f24825e468a9bc0a78f5622a897a300a007487994c8f4fdc97eabc893d5f97b1` | **注意**: 本ファイルは是正後recheckの結果(`b1b`/`a2`とも`overall_status: LEDGER_COMPLIANT`)であり、「検出漏れ」自体を再現したfixtureではない(A-1は時制driftの検出漏れ**事例**の参照であり、修正後の再検証結果を記録したものである点をgoldラベル設定時に注意) |
| A-2/A-3 | `er037_output/family_xy_concreteness_control_trial_01/hormuz/task_a_advanced/A3_deviation.json` | `9e664e1ae373f629a58d283a5ad94334bbe76fe3dcf959a2c53f4b0b11d26877` | MAJOR×3件、origin=ja_source、flags=`changed_fact+changed_comparison`/`changed_fact+unsupported_new_claim`/`changed_fact+changed_scope+changed_causality+unsupported_new_claim` |
| A-4 | `er039_output/family_xy_concreteness_control_trial_02/meta/cells/AN2-T1_deviation.json` | `44fed56e96561ad5d5383805e00d3974340912e98bb97512d8a537a004e4f483` | MAJOR×1件、origin=translation、flags=`changed_scope` |
| A-5 | `er045_output/family_x_no_heading_segmentation_trial_01/meta/v2/must_fix_retry_result.json` | `04e2a7f2d26958e15731f10de4722a728c2832871e449cec69dff1c500d1b3c8` | must-fix retry適用対象(rollback反転、"put back the feature"のchanged_causality/意味反転相当。1件、`fact_id=MUSE-HC-012`) |

(sha256は全て実測64桁。表記上の桁揺れがある場合は本文中の値を正とする。)

### 3-3. 調査REPORT B群4件(過剰品質の可能性)

| # | パス | sha256 | 現行判定(実測) |
|---|---|---|---|
| B-1 | `er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/ja_writer/audit/deviation_checks/ja_original_attempt1.json` | `e33d7fb09fdacfcfc931271ad4176f951ada0f1753fe20781ed4124b5faa51b2` | MAJOR×1件、origin=(なし、JA側は`source_article_text`未指定のためorigin判定自体を行わない)、flags=`changed_scope+unsupported_new_claim` |
| B-2(Hormuz) | `er019_output/family_x_refresh_e2e_01/hormuz/run_02/b1b/audit/deviation_checks/advanced_attempt1.json` | `0594e838284f32c2963d78b85000474451ac741a9cbcd06e03a7f773d04e97b1` | MAJOR×1件、origin=ja_source、flags=`changed_causality` |
| B-3 | `er037_output/family_xy_concreteness_control_trial_01/hormuz/task_b_cleanup/B1_deviation.json` | `4bf6f67ce7d18ca1b79a40b28350e89126921e10d4a4cf7ba40c40cb530fe525` | MAJOR×1件、origin=ja_source、flags=`changed_causality` |
| B-4 | `er019_output/family_x_b3_production_wiring_01/run_01/b1b/audit/deviation_checks/advanced_attempt1.json` | `bb21c160629c725afa3e82b58e8d1d1a32454ddb89a7e7d6e8a05f9dbf82f768` | MAJOR×4件、origin=ja_source×3・translation×1、flags組合せ複数(`changed_causality+unsupported_new_claim`/`changed_scope+unsupported_new_claim`/`unsupported_new_claim`単独/`changed_scope+changed_causality+unsupported_new_claim`) |

### 3-4. Meta run_03 Standard translation MAJOR(追加、非決定性・origin検証用)

`er019_output/family_x_refresh_e2e_01/meta/run_03/a2/audit/deviation_checks/
standard_attempt1.json`(sha256実測
`4016b8cb25a13dbc1809c0a147e7e992f64808ee0ff396189c0fa342a04e79a0`)。overall_status=
`LEDGER_DEVIATION`、MAJOR×1件、**origin=translation**(JA由来ではなく英訳由来のMAJOR
という、origin付きEvidenceの中では珍しい型)、`related_fact_id=MUSE-HC-010`、
flags=`changed_fact+changed_certainty`。

### 3-5. category被覆表(10category×fixture出典)

| category | ER-009-N1(9種fixture) | A/B群・Meta実データ | 被覆状況 |
|---|---|---|---|
| changed_fact | — | A-2/A-3、Meta MAJOR | 実データあり |
| changed_scope | — | A-4、B-1、B-4 | 実データあり |
| changed_causality | ○ | A-2/A-3、B-2、B-3、B-4(、A-5は意味反転として近縁) | fixture+実データ両方あり |
| changed_certainty | ○ | Meta MAJOR | fixture+実データ両方あり |
| changed_number | ○ | **なし** | **fixture不足**(ER-009-N1の合成fixtureのみ、実運用incidentの実データなし) |
| changed_actor | ○ | **なし** | **fixture不足**(同上) |
| changed_negation | ○ | **なし**(A-5は意味反転だが`changed_negation`フラグとして記録された実データではない) | **fixture不足**(同上) |
| changed_comparison | ○ | A-2/A-3 | fixture+実データ両方あり |
| changed_time | ○ | (A-1は「時制drift」と説明されるが該当jsonはrecheck後COMPLIANT結果のみで検出時のflag付きデータは未取得) | **fixture不足**(実データでの検出時flag付き実例が本タスクでは確認できず) |
| unsupported_new_claim | ○ | A-2/A-3、B-1、B-4 | fixture+実データ両方あり |

**結論**: 10category中4種(changed_number/changed_actor/changed_negation/
changed_time)は、実運用incidentの実データが本タスクの調査範囲では見つからず、
ER-009-N1の合成fixtureのみに依存している。Phase B実行時にこれら4categoryの判定力を
評価する場合、合成fixtureのみで評価する(実データ不足はfixture不足として記録、
新規fixtureの追加作成は本タスクでは行わない)。

### 3-6. 非決定性群

- Hormuz run_01〜03(`er019_output/family_x_refresh_e2e_01/hormuz/run_01,02,03/`、
  3ディレクトリとも存在確認OK)。
- Hormuz run_02/run_03の`verified_fact_ledger.txt`は**sha256完全一致**を実測確認
  (`9bd6834e68e7e4378ba0ebccdd84c0128df2a5cd0aca7c1e84df612ae77ae1a6`、両ファイルとも
  同一)。`notes_for_writer`出現数もgrep実測で両ファイルとも**12件**一致。
- run_03における「Advanced/Standardで判定が割れた同一JAケース」を実データで確認:
  `b1b`(Advanced)側`advanced_attempt1.json`(sha256
  `ce69cf94890f068dbf421df6914e7eecbfd4f4557f761646d80096443509694a`)は
  `overall_status: LEDGER_COMPLIANT`(deviations=[])、一方`a2`(Standard)側
  `standard_attempt1.json`(sha256
  `88f5ef99a1592c80cfd56372e7db1faa7aebb36308446b6225c106c655af8e38`)はMAJOR×1件・
  origin=ja_source・`changed_scope`・`related_fact_id=HF-009`。**同一JA原文(Hormuz
  run_03)に対しAdvanced=COMPLIANT・Standard=MAJORという判定の不一致を実データで
  確認済み**(prep資料の記載を実ファイル読込で裏付け)。

---

## 4. 比較条件

固定するもの(現行Checkerと完全同一):
- Prompt: `DEVIATION_PROMPT_TEMPLATE`(sha256実測
  `d3ad565d6d2b3b156c01156295d02c2c14ac33816767ea05af4eb963e5afefc9`、1388文字)
- Developer message: `DEVIATION_DEVELOPER_MESSAGE`(sha256実測
  `28d7efc6d289a246ddcf71da118ca175af86dd2001fe1ca4725a5c534c299b2b`)
- JSON schema: `DEVIATION_JSON_SCHEMA`(`json.dumps(sort_keys=True)`のsha256実測
  `bf6858126fc5888b43d84f06e0c9f6f550415516d2c9ca6ef6269f7229ed407f`、`strict: true`)
- Validator: `_apply_deviation_post_hoc_validation()`(MAJORかつ10フラグ全falseなら
  MINORへ自動降格するpost-hoc処理、`er003_v1_en_direct_vfl_01_generate.py:544-561`)
- input(Ledger本文・記事本文・`source_article_text`の有無)は各fixtureのオリジナル値を
  そのまま使用

変えるもの: `model`引数のみ(`gpt-5.6-luna` vs GPT-6候補[§1-2、ユーザー選定待ち])。
reasoning設定は、候補modelが同名パラメータ`reasoning={"effort": "high"}`を受理する
ことを§1-3のprobeで確認済み(`gpt-6-luna`/`gpt-6-astra`とも受理、エラーなし)なので
**同値("high")で揃える**方針とする。仮に受理しないmodelが判明した場合は「差分」として
明記しユーザー判断へ回す(本Trialでは全候補probe済みのgpt-6-luna/gpt-6-astraは受理
確認済み、gpt-6-solは未probeのため要追加確認)。

**実行harness設計(実装はPhase B)**:
- 既存`run_deviation_check(client, verified_ledger_text, article_text, model=...)`を
  そのまま呼び出し、`model`引数だけを候補modelへ差し替える薄いラッパースクリプト
  (Production/Trial双方の`run_deviation_check()`をimportで再利用、Prompt/Schema/
  Validatorの複製はしない)。
- 出力先: `er050_output/gpt6_model_comparison_trial_01/`(新規、既存Trial番号帯
  er045まで使用済みのため次番er050を仮案とする。Phase B実施時に既存番号帯の空き
  状況を再確認する)。
- run単位のaudit json: fixture名・model_id・attempt(反復回数)ごとに`{prompt_sha256,
  raw_parsed, parsed, usage, elapsed_seconds, response_id}`を保存(現行`run_deviation_
  check()`の戻り値構造をそのまま保存する設計、新規フィールド追加は最小限)。
- 反復n回のシード扱い: LLM API呼び出しにseed引数は現行コードで指定していない
  (Responses APIのdeterminism controlは未使用)。n回の反復は「同一input・同一model・
  同一Promptで単純にn回callを繰り返す」方式とし、擬似乱数seed固定は行わない(現行
  Productionの非決定性実測条件をそのまま踏襲する)。

---

## 5. 評価指標

**Quality**:
- 重大fixture BLOCKING維持率 = (ER-009-N1 9種のうちMAJORのまま検出された件数) / 9
- false negative率 = (本来MAJORであるべきfixtureがMAJOR以外と判定された件数) / 全重大fixture数
- false positive率 = (COMPLIANTであるべき入力がMAJORと誤判定された件数) / 全該当fixture数
  (現時点でCOMPLIANT gold fixtureが少ないため、B群4件の「過剰品質」判定継続率を代理指標とする)
- 不要BLOCK率 = (B群4件のうちMAJORのまま判定された件数) / 4(現行値=4/4=100%)
- origin判定一致性 = (新modelのorigin判定[ja_source/translation]が旧modelと一致した件数) / origin付きfixture数
- changed_causality判定一致率 = (B-2/B-3/B-4等changed_causality関連fixtureでフラグ一致した件数) / 該当件数
- notes_for_writer依存度 = (notesをLedgerテキストから除去した入力とオリジナル入力とで判定が変わった件数) / 対象fixture数。
  **注記(逐語)**: 「notesの除外はTrial入力の加工であり、Production Ledger生成ロジックの
  変更ではない。実施可否はユーザー判断」。
- 同一input反復一致率 = n回中の多数決一致率(最頻判定が占める割合)と完全一致率
  (n回全てが同一判定になった割合)の両方を算出

**Cost**: 1 call単価(GPT-6は§1-4のとおり未確認のため算出不可、現行`gpt-5.6-luna`の
中央値¥0.9024[`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`§5引用]を
参照値として保持)/fixture全体費用/記事換算(Checker呼び出しは1記事あたりJA original+
JA r2+Advanced+Standardの4箇所相当、`docs/pm/gpt6_trial_preparation_01.md`§3-2の
`ja_original_check`+`ja_r2_check`+advanced相当+standard相当から概算)/現行との差分。

**Delivery**: latency中央値・p95(現行33.16秒中央値、9.55〜84.89秒レンジ、
`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`§5引用)/retry率(must-fix
1回上限、現行機構内)/STOP率(`JARecheckRequiredError`/`RuntimeError`発火率)/
timeout・error率(§1-3のprobeでは2/2 SUCCESS、エラー率0%だが試行数が少なく参考値)。

---

## 6. 受入条件案(根拠付き、ユーザー未確定)

| 項目 | 案 | 根拠 |
|---|---|---|
| 重大fixture BLOCKING維持率 | 100%(9/9維持) | ER-009-N1がそもそも「新Checker候補が既存9/9の検出力を落とさないこと」を検証する目的で設計されたfixtureであるため(9/9が既存の合格基準そのもの、`er009_ledger_deviation_recalibration_02_test.py`冒頭コメント) |
| 新たな重大見逃し | 0件 | 同上 |
| 不要BLOCK率 | 現行比改善(現行=B群4/4=100%MAJOR) | OPEN-233の主目的(過剰品質の是正)。現行REPORT分類で「(iii)品質改善の意味はあるがSTOP必須か疑問=7件」「(iv)過剰品質の可能性が高い=3件」計10件/15件(origin付きMAJOR全体)が改善余地ありと分類されている(`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_REPORT.md`第4章、実測確認済み) |
| 非決定性 | 現行より改善(相対比較) | 現行モデルの非決定性は「未実測」(同REPORT§8-6「Checker非決定性の定量実測は未実施」と明記)であるため、絶対閾値を置けない。Trialで現行モデルもn回反復測定し、GPT-6候補と同時に相対比較する方式とする |
| Cost | 同等以下、または品質改善に見合う | GPT-6単価が未確認(§1-4)のため数値閾値は置けない。単価判明後に再設定 |
| Latency | Production許容範囲内(案: 中央値60秒以内) | 現行中央値33.16秒(§5引用)。60秒案の根拠は「Family X E2E実測でTotal STOP判定までの許容待機時間」の目安であり厳密な計測に基づく数値ではない(**根拠薄弱、ユーザー確認要**) |

閾値を置けない項目(Cost・非決定性の絶対値)は「現行モデルとの同時測定による相対比較」を
基本方針とする。

---

## 7. 想定費用 / Guardrail案

**費用概算(GPT-6単価未確認のため、現行`gpt-5.6-luna`単価での下限参考値のみ)**:

Checker中央値¥0.9024(§5引用)を基準に、9(ER-009-N1)+9(A/B群、Meta追加分含めると
実質10)fixture ×n=5×2モデル(新旧)で概算すると:
- 重大群(9 fixture)×5×2=90回 → 概算¥81.2(現行単価仮置き)
- 境界群(9〜10 fixture、A群5+B群4+Meta1)×5×2=90〜100回 → 概算¥81.2〜¥90.2(同上)
- 非決定性群(Hormuz同一Ledger、Advanced/Standard各1ケース×追加反復)は上記重大群/
  境界群のfixtureと重複するため追加費用は主に反復回数の増分のみ

**合計概算(Checkerのみ、現行単価仮置き)**: 約¥162〜180程度(GPT-6側の実単価が
現行より高い場合はこれを上回る。**確定額ではない**)。

**Guardrail案(段階発火)**:
1. 重大群(ER-009-N1、9 fixture×1回×2モデル=18回、概算¥16)を先行実行し、BLOCKING
   維持率100%を確認できてから次段階へ進む
2. 境界群(A/B群+Meta、9〜10 fixture×1回×2モデル)を実行し、不要BLOCK率を確認
3. 非決定性群(n=5反復)を最後に実行
4. 各段の上限: 段階ごとに実費用を記録し、想定額の2倍を超えたらSTOPしユーザー確認
5. 累計上限: ユーザーが別途Phase B開始時に設定(本Phase Aでは金額を確定しない)
6. STOP条件: error率が有意に高い(例: 20%超)、予算超過、schema非互換(strict
   json_schemaをGPT-6候補が拒否する等)のいずれかで即STOP

---

## 8. リスク

- **API非互換**: §1-3のprobeでは`gpt-6-luna`/`gpt-6-astra`ともResponses API・
  `reasoning`パラメータ・`json_schema strict`を問題なく受理したが、probeは自明な
  タスク1回ずつのみであり、実際のCheckerの複雑なschema(10フラグ+配列構造)や
  長いLedger/記事本文入力での挙動は未検証(Phase Bで要確認)。
- **単価未確定**: §1-4のとおりGPT-6系の単価が一切取得できていない。Cost比較の
  数値評価はPhase B時点でも「単価判明まで保留」となる可能性がある。
- **gold ラベルの再現性**: A群/B群の深刻度分類((i)〜(iv)区分)は調査担当者による
  「1回限りの目視分類」であり(`LEDGER-DEVIATION-CHECK-REDESIGN-INVESTIGATION-01_
  REPORT.md`第4章に明記)、合議・再現性検証は未実施。GPT-6比較の「正解」として
  そのまま使うことにはリスクがある。
- **fixture数の少なさ**: origin付きMAJOR/MINORは15件のみ(Family X Entertainment、
  全てGPT-5.6-luna下で生成されたもの)。統計的に強い結論を出すには小標本。
- **現行モデルの再実行が過去判定と一致しない可能性**: 非決定性自体が未実測の
  ため、GPT-6比較の「現行との差分」がモデル差なのか単なる非決定性のノイズなのか
  切り分けが難しい可能性がある(§4-6の実行harness設計で現行モデルも同時にn回反復
  測定することで緩和を図るが、根本解決ではない)。
- **Contract登録**: Phase B実行時、Trial harnessが`require_model()`のfail-closed
  検証を経由せず`model`引数を直接指定する設計(§4)であれば、Contract変更なしで
  実行可能(`docs/pm/gpt6_trial_preparation_01.md`§6-5で言及済みの
  `require_model_or_override(process, model, override_reason)`をDEV/Trial側で
  使う、またはContractを一切経由しないTrial専用呼び出しのいずれか)。ただし、
  Trial harnessをどちらの方式にするかはPhase B設計時に確定する(本Phase Aでは
  未確定)。

---

## Phase A終了時点のStatus

`USER_DECISION_REQUIRED`。理由:
1. GPT-6候補が3件(`gpt-6-luna`/`gpt-6-sol`/`gpt-6-astra`)実在することが判明し、
   どれを比較対象とするかの選定がユーザー判断待ち(§1-2)。
2. 単価が未確認のため、Cost受入条件・Guardrail金額の確定にはユーザー提示の単価情報
   または別途の公式価格情報取得が必要(§1-4、§7)。
3. `gpt-6-sol`は費用上限の都合上probe未実施(§1-3)。

**Phase B(大量実行)は本Phase Aでは開始していない**(委任範囲外)。
