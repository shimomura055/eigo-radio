## 管理ID
`NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01`(初回委任、**Production配線タスク=HIGHリスク、速度より安定性**)。**並行タスクあり**: 別sonnet-workerが`TOPIC-DISCOVERY-ANGLE-BROAD-LUNA-TRIAL-01`(er016_*、`_TD`一時ファイル)を実行中。本タスクはer016_*に触らない(Topic Discovery Trialへ変更を加えない)。一時ファイルは標準`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`。commit時`index.lock`は10秒待ち再試行(最大3回)。他タスクのstaged変更が混在していれば自タスクのパスだけを`git commit <paths>`で対象指定。`ACTIVE_TASK*`/`RESULT_PACKET*`/`.env`はaddしない。履歴操作禁止。trailer `Management-ID:` 必須。

## ユーザー正式判断(2026-09-25)
Standard A2 の v5「6,000語ライン+自然さ優先」仕様を**正式採用**。Status → `APPROVED_FOR_PRODUCTION`。まだ`PRODUCTION_WIRED`ではない。Production配線を完了させ、**Gate 3をすべて満たした場合のみ**`PRODUCTION_WIRED`。1項目でも未確認なら`APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`のままSTOPして報告。

### 正式採用仕様(逐語、SSOTへ記録)
Standard A2では、頻出上位約6,000語以内=原則そのまま使用可、必要に応じてKey Words/Phrases側で学習補助/6,000語を超える語=より簡単で自然な表現がある場合は置換を強く優先、ただし置換によって英文の自然さや意味を損なわない/固有名詞は別扱い/不可欠な専門語は、簡単な代替で意味が失われる場合は残してよい/難語の説明を本文へ追加してStoryを膨らませない。v5 Promptを正式Standard A2として採用。**「6000語超を必ず置換」ではない**(septic tank/wastewater/artery等は必要語として残り得る。municipalitiesのように自然な簡単語へ置換できる難語は優先的に平易化)。
### 分離事項
Metaのscope曖昧性(some parts of the calls ↔ parts of some calls)は本仕様と分離。個別Prompt対応を追加せず、OPEN-177の既存サブ項目として保持。

## 性質/禁止
- Production配線。Production変更は本委任の範囲内(下記)に限定。**Production Prompt本文はv5逐語(`er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/prompt_standard_v5_6000.txt`とsha256一致をコードでassert)**。Trial script(`er015_*`)をProductionからimportしない(Trial専用に残さない=Production側に自前で持つ)。既存Production挙動(既存Family A/B line、Ledger、Gate、Audio)を壊さない。新規記事テーマの選定はしない(検証入力は既存Sewer/Meta Advanced固定)。追加Prompt改変・Variation禁止。費用上限**¥20**(runtime発火はSewer/Meta各1 call+retry検証の最小限)。`git add -A`/`stash`/`amend`禁止。
- STOP条件: Advanced Natural→Standard A2の正式初回経路が存在せず、経路の設計(入口・Production contract付与・downstream接続)に仕様判断が必要/既存Production経路との競合/regression失敗/¥20超過見込み。STOPでも**実施済み部分(SSOT記録・モジュール・テスト・runtime evidence)はcommit**し、未完了項目を列挙。

## 固定ブロック
E-1/D-1/G-1/F-1(前回同一)。T-0: 本委任文を`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01.md`へ保存し`check_delegation_prompt.py`実行、結果をRESULT_PACKETへ1行(FAILでも継続)。

## 事前指定Read一覧
- `docs/pm/PM_BRIEF.md`: Grep `Gate 3|PRODUCTION_WIRED|runtime evidence|regression|test`→Gate 3の正式定義行。`docs/pm/PM_GOVERNANCE.md`: Grep `Gate 3`→定義本文のみ。
- `CURRENT_SPEC.md`: Grep `Entertainment英語版生成方式|Entertainment生成方式|WRITER_MODEL|Key Words|Phrases|keywords`→行829(Advanced行)と関連仕様行の形式。
- `DECISION_LOG.md`: Grep `NEWS-STANDARD-A2-PROMPT-V2-TRIAL-01|NEWS-NATURAL-ADVANCED`→直近エントリ形式。
- `OPEN_ITEMS.md`: Grep `OPEN-177|OPEN-178|OPEN-179`→現行文言(更新対象)、最大番号。
- Production経路の偵察: `er012_b_family_production_runner_01.py`(Grep `def |import er003|articles_generate|scaffold|retry|fallback|WRITER_MODEL|effort`)、`er003_v1_n3_01_articles_generate.py`(Grep `def |WRITER_MODEL|responses.create|retry|fallback|COMMON_BLOCK|contract|In one line`)、`er003_v1_n3_01_scaffold_generate.py`(Grep `def |keyword|key_phrase|Key Words|extract`→Key Words/Phrasesの役割と入力)、`er003_v1_en_direct_vfl_01_generate.py`(Grep `def run_deviation_check|def `)、`Grep pattern="Natural English Adaptation|adaptation|advanced_natural|standard_a2" -i glob="er0*.py" -l`(Advanced/Standardの既存Production実装有無)、`Grep pattern="retry|fallback|regenerat" -i glob="er012_*.py,er003_v1_n3_*.py" -l`(retry/fallback/regeneration経路)。
- v5 Prompt: `er015_output/news_standard_a2_vocab_6000_cutoff_trial_01/prompt_standard_v5_6000.txt`(逐語、developer文含む)、`er015_news_standard_a2_vocab_6000_cutoff_trial_01.py`(Grep `def call_|def _price|effort`→呼び出し条件: `gpt-5.6-luna` effort high)。
- 検証入力: `er015_output/news_natural_advanced_standard_a2_trial_01/a1_advanced_sewer.md`、`er015_output/news_ja_to_en_adaptation_trial_01/arms/arm3/output.md`(sha256記録)。
- 既存テスト実行方法: PM_BRIEF Grep `pytest|unittest|_test_01.py`。

## 実行手順
### STEP 1 SSOT記録(Trial結果に関わらず実施)
- CURRENT_SPEC 行829: Standard(A2)部分を「Standard = v5(6,000語ライン+自然さ優先、正式採用仕様の逐語要約)、`APPROVED_FOR_PRODUCTION`(2026-09-25ユーザー正式承認)。配線Status: [STEP 5の結果で `PRODUCTION_WIRED` または `WIRING INCOMPLETE`]。v1 REJECTED/v2 superseded/v3 VALIDATED/v4 REJECTED/v5 VALIDATED→APPROVED の履歴」へ更新(Advanced部分は変更しない)。
- DECISION_LOG: 管理ID本IDで追記: User formally approved Standard A2 v5 (6000-cutoff), status=APPROVED_FOR_PRODUCTION, date 2026-09-25, supporting Trials(`NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-TRIAL-01`ほかv1〜v4の各ID)、正式仕様逐語、「6000語超を必ず置換ではない」注記、配線結果(STEP 5後に追記)。
- OPEN_ITEMS: OPEN-177を更新(Standard A2 v5の配線項目を追加、Meta scope曖昧性サブ項目は保持、完了したサブ項目のみclose)。新規乱立しない。

### STEP 2 偵察(判断材料、変更なし)
Production正式初回経路の現状: (a) Japanese Entertainment R2(Original→R1→R2)のProduction入口の有無、(b) Advanced Natural AdaptationのProduction実装の有無、(c) 記事→scaffold/TTS/assembleが要求するProduction contract(`# Title`+2つの`### `+`## In one line`)、(d) retry/fallback/regenerationの経路とPromptの一元管理方法、(e) Key Words/Phrasesの抽出元(記事本文か)と役割。→`recon.md`に事実列挙。**(a)(b)が存在しない場合、Standardを「正式初回経路」へ繋ぐ先が無い**ため、その旨を明記(勝手に経路設計しない)。

### STEP 3 Productionモジュール実装(既存Family命名に従う。例 `er003_v1_n3_01_standard_a2_generate.py`)
- `STANDARD_A2_DEVELOPER`/`STANDARD_A2_PROMPT_V5`定数(逐語)、`STANDARD_A2_PROMPT_SHA256`定数と起動時assert(Trial fileとの一致確認はテスト側で実施、Production実行時はTrial fileに依存しない)。
- `generate_standard_a2(advanced_text: str, *, model=WRITER_MODEL, effort="high", max_retries=1) -> StandardA2Result(text, model_id_actual, response_id, usage, cost_jpy, attempts)`: 既存`er003_v1_n3_01_articles_generate.py`のAPI呼び出し・cost計算・retry方針(空出力/API失敗時の同一Prompt再試行、fallbackモデルは既存Productionに定義があればそれに従い、無ければfallbackなし)を**同じ関数/設定を再利用**して実装(重複実装しない)。regeneration(再生成)経路が既存にあれば同じ関数を呼ぶよう接続、無ければ「未接続」と記録。
- 機械チェック(既存関数を再利用): Advanced→Standardで数字・固有名詞の追加/欠落がないこと(既存`run_deviation_check`が使えるなら使用、Ledger不要の簡易版なら`er002`/`er003`既存の数字・固有名詞diffを再利用)、タイトル行が存在すること。失敗時は結果に`checks_failed`を記録(自動で本文修正しない)。
- runtime evidence: `er003_output/…/standard_a2/runtime_evidence.json`(既存Production出力規約に従う)に model_id実値/response_id/usage/cost/prompt sha256/checks。
- CLI: `--advanced-file <path> --out-dir <dir>`。

### STEP 4 テスト・runtime発火
- 単体テスト `er003_v1_n3_01_standard_a2_generate_test_01.py`: Prompt sha256がTrial fileと一致/API mockでretry動作(空出力→1回再試行→失敗でraise)/出力parse/チェック関数。
- 既存regression: PM_BRIEF記載のテストコマンドで既存テスト一式を実行(失敗が出たら本タスク由来か確認、既存失敗は事実記録)。
- runtime発火(実API、各1 call): Sewer Advanced・Meta Advanced → Production module → 出力とevidence保存。v5 Trial出力との差(同一Promptだが非決定的)を記録し、6,000超残存語・不自然置換の有無を既存の帯測定(Trial scriptからimportせず、`wordfreq`直接)で確認。
- `actual model_id`が`gpt-5.6-luna`であること、routing(呼び出し経路: runner→module)を記録。

### STEP 5 Gate 3チェックリスト(全項目○のときのみ`PRODUCTION_WIRED`)
1 Production正式初回経路へv5実装(runnerから呼ばれる位置に接続されているか)/2 retry・fallback・regenerationで同一仕様/3 Trial専用scriptだけに残していない/4 Advanced Natural→Standard A2の正式経路との整合(Advanced経路の存在含む)/5 Key Words/Phrasesとの役割分担に矛盾なし/6 Production正式pathでruntime発火/7 actual model_id・routing確認/8 regression・validator・integration test/9 Sewer・MetaでProduction経路から期待挙動/10 CURRENT_SPEC/11 DECISION_LOG/12 OPEN_ITEMS/13 Git/14 Dangling Reference Check(`Grep "er015_" glob="er003_*.py,er012_*.py"`=0、`Grep "STANDARD_A2_PROMPT_V5"`が定義1箇所+参照)。→`gate3_checklist.md`に○×と根拠。×が1つでもあれば Status=`APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE`としてCURRENT_SPEC/DECISION_LOGに反映しSTOP。

### STEP 6 REPORT `NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01_REPORT.md`
§1 正式採用仕様(逐語)/§2 偵察結果(初回経路・Advanced経路・contract・retry・Key Words)/§3 実装(モジュール・関数・Prompt sha256・呼び出し経路)/§4 retry・fallback・regeneration整合/§5 runtime evidence(Sewer/Meta、model_id実値、cost)/§6 テスト結果(単体・regression)/§7 Sewer/Meta Production実行結果(全文+6,000超残存語)/§8 CURRENT_SPEC更新(逐語)/§9 DECISION_LOG更新(逐語)/§10 OPEN_ITEMS更新(逐語)/§11 Git/§12 Dangling Reference Check/§13 Gate 3チェックリスト/§14 未完了事項/§15 最終Status/§16 Fable記入欄`[Fable記入]`。

## 実行コマンド全文
```
cd C:\Users\tensh\eigo-radio
.venv\Scripts\python.exe er003_v1_n3_01_standard_a2_generate.py --advanced-file er015_output\news_natural_advanced_standard_a2_trial_01\a1_advanced_sewer.md --out-dir er003_output\standard_a2_wiring_01\sewer
.venv\Scripts\python.exe er003_v1_n3_01_standard_a2_generate.py --advanced-file er015_output\news_ja_to_en_adaptation_trial_01\arms\arm3\output.md --out-dir er003_output\standard_a2_wiring_01\meta
.venv\Scripts\python.exe -m pytest er003_v1_n3_01_standard_a2_generate_test_01.py -q
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01.md --json-out docs\pm\delegation_log\NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01.md_check.json
git status --short
```
(モジュール名・出力規約は偵察で判明した既存Family命名に合わせて変更可。変更した場合は実コマンドをRESULT_PACKETに記録。)

## SSOT追記文
STEP 1・STEP 5のとおり(逐語はREPORT §8–10に転記)。

## Git
明示add: 新規Productionモジュール・テスト、`er003_output/standard_a2_wiring_01/`配下(evidence)、`CURRENT_SPEC.md`、`DECISION_LOG.md`、`OPEN_ITEMS.md`、REPORT、`docs/pm/delegation_log/NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01.md`、同`_check.json`。runnerを変更した場合はそれも(変更内容をREPORT §3に逐語diff)。
メッセージ: `NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01: Standard A2 v5(6,000語ライン+自然さ優先)をユーザー正式採用としてSSOT記録し、Productionモジュール・テスト・runtime evidenceを実装(最終Status: [PRODUCTION_WIRED|APPROVED_FOR_PRODUCTION / WIRING INCOMPLETE])`
trailer: `Management-ID: NEWS-STANDARD-A2-VOCAB-6000-CUTOFF-PRODUCTION-WIRING-01`

## 報告(RESULT_PACKET)
0. T-0 1. 偵察結果の要点(初回経路・Advanced経路の有無) 2. 実装ファイル・関数・Prompt sha256 3. retry/fallback/regeneration整合 4. runtime evidence(model_id実値、cost合計、¥20以内) 5. テスト結果(単体・regression、失敗があれば本タスク由来か) 6. Sewer/Meta出力の6,000超残存語・不自然置換有無 7. SSOT更新逐語 8. Gate 3チェックリスト(○×)と最終Status 9. `git status --short`・commit SHA・push 10. 未完了事項・仕様判断が必要な点(事実列挙)、一覧外Read理由。
</content>
