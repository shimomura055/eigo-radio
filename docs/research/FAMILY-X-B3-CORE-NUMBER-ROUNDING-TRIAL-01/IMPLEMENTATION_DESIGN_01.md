# Family X 中核数値丸め仕様 Production実装設計書(委任_05 C-1、Opus独立レビュー用)

管理ID: FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01(OPEN-437・OPEN-442、UDR #135) / 2026-10-22
Status: APPROVED_FOR_PRODUCTION_WIRING_IN_PROGRESS(ユーザー正式採用済み。**C-1時点でProduction既存ファイル未編集=PRODUCTION_WIREDではない**)
承認原文: `docs/pm/delegation_log/2026-10-22_FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01_APPROVAL-AND-ARTICLE-A-REMAKE_USER.md` §1(Family Xのみ・Luna low・規則5例外=B3正式指定概数のみ・小数％は概数既定・既概数は再丸めしない・V8採用・S5条件付き採用)
レビュー対象: 11-3条件A(新しい処理フロー)・C(Production採用前)。C-2(配線)はレビュー後。

## 1. 成果物(C-1、すべて新規ファイル)
| 区分 | path | 内容 |
|---|---|---|
| 新module(未配線) | `er095_b3_core_number_rounding_01.py` | 判断Prompt(Trial_02検証済みPrompt v2とバイト一致)・JSON schema・V1〜V8/V8b・overlay生成/永続化/読込・judge call(Luna low)・runner用単一関数 `run_core_number_rounding` |
| test | `er095_b3_core_number_rounding_01_test_01.py` | 47 test(API 0) |
| V8回帰fixture | `er090_output/b3_core_number_rounding_trial_02/evidence/v8_regression_90.json`(生成=`er090_b3_core_number_rounding_trial_03_v8fixture.py`) | 保存済みLuna判断90件 |
| S5 Trial検証 | `er090_b3_core_number_rounding_trial_03_s5.py`、`S5_TRIAL_RESULT_01.md`、`.../evidence/s5_trial_result_01.json` | PASS(§6) |

## 2. 新module設計(a)
- Trial overlay(`er090_..._trial_01_overlay.py`)の純関数を移植。Trialファイルへのimport依存なし(承認規則文はProduction正本 `er003_v1_n3_01_evidence_compression_editor` から逐語import)。Prompt本文・developer message・JSON schema・規則8はTrial_02検証済みと**バイト一致**(testで固定: `test_judge_prompt_identical_to_validated_trial_prompt`)。承認仕様のうちPromptで伝わらない部分(V8・既概数)は**決定論ゲートで強制**(Promptは変更しない=Trial_02で測った判断分布を維持)。
- 検証: V1(concept集合/順序)・V2(surface集合)・V3(通常四捨五入)・V4(単位/限定語)・V5(ヘッジ語)・V6(basis_fact_ids)・V7(同Fact内の他数値との衝突)・**V8**(相対誤差 ≤10%、境界含む、数値化不能は fail-closed で違反)・**V8b**(元surfaceが既に「約/およそ/ほぼ/前後/ほど/近く/程度」付き=既概数は再丸め禁止)。違反concept(いずれか1 surface)はEXACT_REQUIREDへ降格。
- judge: `gpt-6-luna` / effort=`low`、routing contractの**新role `FAMILY_X_B3_CORE_NUMBER_ROUNDING`**(C-2で `er006_model_routing_contract_01.PROCESS_MODEL_MAP` へ追加。1行・既存キー不変・リテラル固定)経由で `require_model` をAPI call前に確認。返却modelが `gpt-6-luna` で始まらなければ fail-closed。overlayのprovenanceへ `model_requested/returned・effort・response_id・usage・user_prompt_sha256・developer_message_sha256・json_schema_sha256` を保存。
- **fail-closed**: judge例外/モデル不一致/不正JSON/概数可0件は、いずれも「丸めなし」overlay(status=`JUDGE_FAILED_FAILCLOSED` 等)を書いて続行。STOP・retry・Human Reviewを増やさない(`BaseException`系・予算超過は握りつぶさない: `Exception`のみ捕捉)。
- **冪等**: 既存overlayが現在の `annotated_md_sha256` に有効なら judge API call 0 で再利用。B3再生成でshaが変われば再判断。

## 3. 配線点(b)・配線表
| # | ファイル:行(現行) | 変更 | 行数 |
|---|---|---|---|
| W1 | `er019_family_x_entertainment_production_runner_01.py:466`(`run_annotation_producer(out_dir)` 直後) | `rounding.run_core_number_rounding(client, out_dir, contract.validate_annotated_b3(out_dir), w1.parse_brief_md, ledger_text)` を1回呼ぶ(+`import er095...`)。`efam.assert_budget_ok` を直後に1行 | +8 |
| W2 | `er053_family_x_factlock_ja_writer_01.py:331`(`news_text = annotated.news_field_text`) | `overlay, rev = rounding.load_overlay_for_writer(out_dir, annotated.annotated_md_sha256)`; `news_text = rounding.apply_to_news_field(...)`(overlay None/0件=従来と同一文字列) | +6 |
| W3 | 同:262,275 `build_r0_prompt` / `build_r0_symbol_regen_prompt` | 省略可能引数 `rounding_overlay=None` を追加し、末尾に `rounding.apply_rule8`(None=従来とバイト一致)。**symbol再生成Promptも同じ規則8を含む**(`build_r0_symbol_regen_prompt`が`build_r0_prompt`を呼ぶため引数を透過) | +8 |
| W4 | 同:343 `ev` | `ev["rounding"] = {overlay_sha256, applied, reason, n_approximate_ok, enabled}` をprovenanceへ | +5 |
| W5 | runner:294 `load_reused_ja_text` | JA再利用時の来歴照合に `ev["rounding"]["overlay_sha256"]` 一致を追加(キー無し=旧記事=legacy許容。キー有りで現在のoverlayと不一致=既存`PROVENANCE_MISMATCH`と同型STOP) | +5 |
| W6(**S5**) | `er053_family_x_factlock_ja_writer_01.py:98,102` | `MARK_RE`→`r"【(?:中核数値|周辺数値|\s*概数表記\s*)】"`、`TAG_LEAK_RE`→`(?:事実|[FＦ]|中核数値|周辺数値|概数表記)` | +2 |
| W7 | `er006_model_routing_contract_01.py:134`付近 | 新role 1行 `"FAMILY_X_B3_CORE_NUMBER_ROUNDING": "gpt-6-luna"` | +1 |
| W8 | 既存test | `er053_family_x_factlock_ja_writer_01_test_01.py::test_w1_rf_queue_contract_referenced_only_by_entertainment_runner_after_c2` の `TRIAL_HARNESS_PREFIXES` に `er090_`(現状 **C-1時点で既にFAIL**: Trial_01の `er090_*_evidence.py` が w1 を import するため。Trial harness群の許容と同型、test側のみ)、および `er095_` を参照許可対象に追加 | +2 |

**Family Z分離**: `er095` を import するのは W1(Family X runner)とW2(w1)のみ。Z runner・Z Writer・audio runner・他Family runnerは import しない(testで固定: `TestIsolation`)。w1 は Family X専用(importerはFamily X runner・Trial harness・契約/producer module。Z production runnerは import しない: `grep -l er053_family_x_factlock_ja_writer_01` で確認済み)。overlay不在ならw1は従来と同一(DefaultOffIsolation)。

## 4. retry / fallback / regeneration / resume での同一適用(c)
丸め指定は `storyline_b3/rounding_overlay.json`(契約sha対象外の新規artifact、`overlay_sha256`+`annotated_md_sha256`で自己検証)に**永続化**し、Writerは常に `load_overlay_for_writer` 1か所からのみ読む。
| 経路 | 適用方法 |
|---|---|
| 初回 | W1でoverlay生成 → W2でWriter入力に反映 |
| R0 symbol再生成(Writer内retry) | `news_text`は関数ローカルで再利用 + W3で規則8も同Prompt |
| `--regenerate-stage writer` / Writer再実行 | runner:464-466の `need_storyline` ブロックは stage∈{storyline_b3,writer,advanced,standard,all} で必ず通る → W1が既存overlayを**API 0で再利用** → W2が読む |
| `--regenerate-stage storyline_b3`(B3再生成) | B3→producer→W1: shaが変わるため**再判断**(古いoverlayは stale として無視) |
| resume / 既存JA記事再利用 | `load_reused_ja_text`(W5)が来歴 `overlay_sha256` を照合。stale/改ざん overlay は無視(丸めなし)で fail-closed |
| Local Rewrite / segment再生成 / 段落retry | 既存のJA/EN本文を直接編集する経路で、news field(Facts+制約)を読まない(`news_field_text`/`constraints_text` の Production参照は w1:331,343 のみ、grepで確認)。数値表記は既に確定した本文中に残る |
| judge失敗 | 丸めなしで続行(従来と同一出力) |

## 5. rollback(d)
`er095_b3_core_number_rounding_01.B3_CORE_NUMBER_ROUNDING_ENABLED`(既定True、module定数1行)。False: judge call 0・overlay無視(Writer入力/Promptは従来とバイト一致、testで固定)。flag名と「既定=承認済みON」を OPEN-437 に記録済み。※本仕様はユーザー正式採用(APPROVED_FOR_PRODUCTION)のため11-7の「未承認・既定OFF」例外には該当せず、既定ONが正。起動script/.envでの切替は設けない。

## 6. S5(Trial環境検証結果、§(e))
`S5_TRIAL_RESULT_01.md` 参照: 漏れfixture 5種 → 現行Production=未検知、S5版=検出+除去 / 253ファイル(Trial2 12arm + 記事A/B/他Production本文)で検知結果の変化0。**S5条件(Trial環境でPASS)充足**。W6はC-2で実装する。

## 7. 検証計画(e)と費用見積(f)
検証計画: (1) unit: `er095..._test_01.py` 47 PASS(Trial test 30件の移植+V8/V8b+永続化/stale/改ざん/flag OFF/fail-closed+judge callモック+Isolation)。(2) V8 90件回帰: 拒否 V8=6件・V8b=11件(うち5件V8と重複)=計12件(全て事前登録ラベルE)、**正しい丸め(ラベルA)の誤拒否0**。(3) C-2 Regression: B3/Writer既存test(`er053_*_test_01.py`, `er019_family_x_b3_*_test_01.py` 等)、Family X既存integration test、S5の本番regex版再実行。(4) C-2 実走: 記事A再制作(B3→Writer→Std/Adv→TTS→ASR・各Validator)。
費用見積(出典付き、いずれもC-2): 
- text: 判断Luna low ≈ 0.12円/記事(Trial2 `luna_low_rep1` 2.00円/18記事 = 0.11円/記事、`judge_eval.json`) + 記事A過去実績のB3以降text(`er019_output/paycheck_personality/run_pp_01` 57.81円 − research 14.78 − ledger 17.96 ≒ **25.1円**)。
- audio(TTS+ASR+KP+scaffold等): 記事B実績 **53.0円**(`docs/pm/RESULT_PACKET_FXBY2.md:4`、text 40.9[是正前26.05含む]+audio 53.0=93.94円)を上限基準、記事A旧audio run実績18.0円(`...paycheck_personality__run_pp_01/raw_usage_log.jsonl`)を下限参考。
- 合計 ≈ 25.2 + (18〜53) = **約43〜78円、リトライ余裕1.5倍で約65〜117円 → 300円以内**(7-7により都度承認不要)。
- TTS実行方式: Batch待ちを避けるD優先で `TTS_EXECUTION_MODE=STANDARD` 推奨(PM_GOVERNANCE.md 709)。Batch換算原価(15節5区分)はC-2報告で併記する。
- **量産時の追加原価**: judge 約0.12円/記事(目標70円比 +0.17%)、再試行なし。V8/V8b/S5は決定論(追加API 0)。

## 8. 既存仕様整合・撤去/残置(確認済み)
- 整合: `CURRENT_SPEC.md:1730`(Spoken-first Number、Ledger=exact維持)、`:2096`(Listener-Friendly Numeric Precision)、`er003_v1_n3_01_evidence_compression_editor.py:121-131`(小数％概数既定。judge Promptへ逐語埋込、検証は `test_decimal_percent_rounding_default_passes`)、`er053_family_x_factlock_ja_writer_01.py:84-95`(規則5。規則8で「【概数表記】指定のみ」の例外。指定のない数字は規則5のまま=Writer自身の丸めは引続き禁止)、`DECISION_LOG.md:14388`・`:20533`、B3契約 `er053_b3_annotation_contract_01`(注記md/sidecar/manifestは無改変、overlayは別ファイル)。
- 撤去する旧規則: なし(追加のみ)。残置: Trial専用 `er090_*` はTrial証跡として残置(Productionから参照しない)。

## 9. Opusレビューで見てほしい論点
1. **V8bの定義**: 「既に概数」を元surfaceのヘッジ語(約/およそ等)で機械判定している。CEO丸め値(167億ドル等)のように表記上は概数でない既概数は機械検出不能で、Promptと判断に依存(Trial2事後再ラベルでは境界B扱い)。この線引きで承認文言「既に概数の数値は再丸めしない」を満たすとみなしてよいか。
2. **Promptを変えない決定**: 承認仕様(V8・既概数)をPromptに書き足さず決定論ゲートだけで強制する案(Trial_02の判断分布を維持)で良いか。Luna lowが10%超/既概数を提案するたびに降格される(Trial2保存90件では12件=13%がV8/V8bで降格)ため、Writerに渡る概数は減る(価値は元々限定的: 指定概数の使用 2/7)。
3. **S5の`MARK_RE`/`TAG_LEAK_RE`同時拡張**: 漏れは検出(TagLeak)ではなく`MARK_RE`により**除去+`marks_echoed`計上**される(正確な`【概数表記】`・空白入りの両形。他の変形は`TAG_LEAK_RE`でTagLeak STOP)。「検出」要件を、除去前の検出(`marks_echoed`/`r0_meta`)で満たすか、STOP(TagLeak)にするか。現設計は不要STOPを増やさない側(除去+記録)。
4. **provenance照合(W5)のlegacy許容**: 旧記事(evidenceに`rounding`キー無し)の再利用は許容、キー有りで不一致のみSTOP。旧JA記事の再利用中にB3が再判断されoverlayが有効化された場合の扱い(現設計=legacyは常に許容)。
5. **失敗時のfail-closed範囲**: `Exception`全般を捕捉して丸めなしで続行(ModelContractViolation=routing未登録も含む)。設定ミスを黙って握りつぶすリスクに対し、overlayの`status/error`をevidenceへ記録+runnerログ出力で十分か。
