# RISK-FLAGGER-PRODUCTION-WIRING-01 委任_06 = Phase 2 C1(追加のみ)実装ログ

- 日付: 2026-10-10 / 実行: Sonnet(実行層) / ユーザーGo: 2026-10-10 / 課金API 0件 / git操作 0件(add/commit/checkout/branch/stash/push 未実施。`git status --porcelain`・`git check-ignore`・`git show`・`git diff --stat`の読み取りのみ)
- 設計正本: `docs/pm/design/2026-10-10_RISK-FLAGGER-PRODUCTION-WIRING-01_DESIGN_03.md`(1〜14節+15節 Opus再レビュー・15-2是正v3.1)
- 範囲: 追加のみ。既存Production関数の挙動変更・削除なし。er012_e / er019 entertainment runner / jaw / audio runner は無変更(`git diff --stat`で確認済み)。
- 編集した既存ファイルは2つだけ(追加のみ): `er005_output/cost_baseline_01/pricing_snapshot.json`(+36行)、`er006_model_routing_contract_01.py`(+9行)。
- 使用モデル(PM_GOVERNANCE 25節): 本作業のLLM呼出0件。コード中の予定モデル=RF `gpt-6-luna`/`gemini-3.5-flash-lite`、W-1 R0 `gpt-6-luna`・R1/R2 `gpt-6-astra`(いずれもユーザー指定/採用済み、旧モデルなし)。

## 1. 追加ファイル(すべて新規)

| ファイル | 内容 |
|---|---|
| `er053_en_sentence_splitter_01.py` (+`_test_01.py`) | 共通splitter。Trial `vs_sentence_segments_l6`(L5503)・`_VS_L6_ABBREV`(L5477-5480、33語)・`_vs_l6_abbrev_period`(L5485)・`_VS_SENT_END_RE`(L4944)を移植。`split_sentences_en(text)->[(sid,text)]`、`SPLITTER_VERSION="en_split_v1"`。標準ライブラリ`re`のみ |
| `er053_risk_flagger_production_01.py` (+test) | RF本体。A3/A4 system promptをbyte-identical移植(sha 9d995042…/c87b95e5…、import時assert)、台帳parser(FIX01補正regex+完全性assert)、入力構築、4条件逐次(luna A3/A4→gemini35fl A3/A4)、validate_flags、技術retry(transient 2/format 1)、RF_UNAVAILABLE/PARTIAL記録(WARN+entry_point.json)、OR統合、MODEL_STATS、記事sha不変assert、単価fail-closed(最初のAPI呼出前)、Gemini REST adapter(thinkingをoutput_tokensに含め`cl.record`)、Lunaは手動記録なし、`budget_check`フック |
| `er053_review_queue_01.py` (+test) | Queue保存。`review_queue/post_en/<article_id>/<level>__<rf_run_id>/{queue.json,queue.md,inputs/,raw/}`+追記専用`index.jsonl`(O_EXCL lock+fsync)。保存失敗時はout_dir fallback+WARN+entry_point.json。`review_state`なし |
| `review_queue/post_en/README.md` | ChatGPT向けの読み方 |
| `er053_cost_aggregate_01.py` (+test) | stage集計の非OpenAI(Gemini)対応版を**新関数**として追加(既存`compute_stage_cost_breakdown`は無変更)。呼出側切替はC3 |
| `er053_b3_annotation_contract_01.py` (+test) | 注記済みB3入力契約 V1〜V10 |
| `er053_family_x_factlock_ja_writer_01.py` (+test) | W-1 Writer本体(どのrunnerからも未呼出)。Prompt5・regex5・関数をTrialからbyte-identical移植 |
| `er053_dev_b3_fixture_adapter_01.py` | DEV専用fixture adapter(Production不参照をtestで固定) |
| `er053_dangling_reference_check_01.py` (+test) | dangling grep list走査 |
| `er053_output/risk_flagger_production_wiring_01/` | 証跡: `ledger_scan_er019_output.json`、`dangling_baseline_c1.json`、`golden/w1_golden_prompts_01.json`(+生成script `gen_w1_golden_01.py`)、`stub_e2e_01/`(stub E2Eサマリ+X09サンプル) |

## 2. 編集した既存ファイル(追加のみ)

- `pricing_snapshot.json`: `gemini-3.5-flash-lite`(provider=gemini, tier=Standard)を3エントリ追加(input 0.30 / cached_input 0.03 / output 2.50 USD per 1M、output=thinking込み)。出典URLと取得日時(xm_prices_01.json 2026-10-10T04:50Z転記+実装時再確認2026-10-10T08:19Z、公式pricing page raw html sha256=919eb066…)を`source_url`に併記。既存エントリは完全不変(testで固定)。`last_updated`欄は変更していない。
- `er006_model_routing_contract_01.py`: `PROCESS_MODEL_MAP`に4キー追加のみ(`FAMILY_X_RF_LUNA`=gpt-6-luna / `FAMILY_X_RF_GEMINI`=gemini-3.5-flash-lite / `FAMILY_X_FACTLOCK_R0`=gpt-6-luna / `FAMILY_X_FACTLOCK_REVISE`=gpt-6-astra、全てリテラル固定)。既存キー・`PROCESS_PROVIDER_MAP`は不変(testで固定)。

## 3. テスト結果(すべてAPI呼出0)

- 新規 `er053_*_test_01.py` 7本: **150 passed / 0 failed**(splitter 20、RF 44、Queue 13、cost/pricing/routing 9、契約+adapter 25、W-1 35、dangling 4)。
- 既存の関連test(er006 routing 5本、er019 runner/audio/ja_writer、er012_e、er015/er019 kp/er033 の pricing/routing参照test): 100+92 passed。**既存2件がFAIL**(下記4-1)。`er015_standard_a2_6000_generation_first_trial_01_test_01.py`は収集時に`STANDARD_A2_PROMPT_V5`の文面ガードでRuntimeError(今回の変更と無関係の既存ガード。本作業はそのPromptに触れていない)。

## 4. C1で判明した設計上の問題・解釈(Fable確認用)

### 4-1. 既存test 2件がrouting追加でFAIL(想定どおりの帰結、修正は未実施=本委任の編集許可範囲外)
- `er006_model_routing_gpt6_wiring_test_01.py::RoutingConstantsTest::test_process_map_openai_models_all_gpt6_luna`(「mapのgpt-系は全てgpt-6-luna」)
- `er006_model_routing_pricing_coverage_test_01.py::PricingCoverageTest::test_gpt6_astra_prices_registered_standard_only` の最終行 `assertNotIn("gpt-6-astra", routing.PROCESS_MODEL_MAP.values())`(「astraはrouting未割当」)
- どちらもW-1採用(Astraをroutingへ入れる)前の不変条件。最小更新案: 前者は `k != "FAMILY_X_FACTLOCK_REVISE"` を除外条件に、後者は `assertNotIn` を「astraに割り当たるキーが`FAMILY_X_FACTLOCK_REVISE`だけ」への置換。**このまま2ファイルをmainへcommitするとmain側のtestが赤くなる**ため、commit前に更新許可(または同時更新)が必要。

### 4-2. 契約検証の解釈(DESIGN_03/15-2の字義と実Trial成果物9本の不整合。契約module docstringに明記)
実Trial注記成果物 annotation/final 9本を契約PASSにするため、次の3点を解釈・追加した。Lane B(manifest/注記仕様)側との擦り合わせが必要な可能性があるため**USER_DECISION候補(軽微・仕様の明確化)**として報告する。
1. **V6**: 字義「印の総数==サイドカーnumbers件数」は9本中5本で不一致(numbersは distinct surface の一覧、同じ数字がStorylineとFactsに出れば印は複数回出る)。→ 出現ベース(全ての印の直前がnumbersのsurfaceで class対応[core=中核/peripheral=周辺]、numbersの各surfaceが印付きで最低1回出現、変形印なし)に置換。
2. **V5**: 字義「Facts節の空でない全行がFACT_LINE_RE一致」は2本(small_bag, openai_copyright)で不一致。B3既存出力形式の「Storyline:」/「Storyline：」重複行(Facts節先頭、Storylineと同一内容のときのみ)を1行だけ除外。
3. **V10**: 「Storyline完全一致」は注記済みStorylineに数値印が付く(5本)ため、**印・タグ除去後**に完全一致を要求。
- 原B3(未注記)を注記済みとして渡すと9本全てV5でFAIL、事実1の1文字改変は(sha整合しても)9本全てV10でFAIL(testで固定)。

### 4-3. その他の軽微な点
- **F8 `clean_ja_for_next`の許容差**: 設計の許容差は`call_astra`の3点のみだが、F8はTrialが関数内で`er052_factlock_writer_trial_01_run`をimportして`fl.strip_tags`を呼ぶため、Trial非import方針と両立するには「import行削除+`fl.`接頭辞除去」が不可避。挙動は同一(testで正規化後のソース一致+実Trial成果物8本の最終文一致を確認)。
- **chain_method**: 委任文の指定に従い`"W-1"`を記録(DESIGN_03 2-4の旧値`factlock_r0_luna__astra_r1_r2_independent`は`chain_method_detail`に併記)。chain_methodの値を厳密に読むコードは現Productionに無い(grep確認)。
- **R0 model_id不一致**は記録のみ(`model_mismatch`)。新規STOP条件は追加していない(設計どおり)。Astra不一致は`call_astra`で`ProvenanceViolation`=STOP。
- **`unlocated_flags[]`**は現状常に空(未知のsentence_idはvalidate違反→format retry 1回→その条件がRF_UNAVAILABLE)。Trial同等の挙動を維持。部分採用にするかはC2以降の設計判断(新仕様判断のため未実装)。
- **splitter**: Trial由来の既知の限界を継承(`1st. Next`のように数字+`st`の直後が大文字だと略語`St.`扱いで切れない)。変更しない。
- **article_id**: `er053_review_queue_01.derive_article_id(out_dir)`(out_dirのbasename)を共通関数として置いた。C2でwriter側、C3でaudio側の呼出を揃える。
- 混在改行: 一部のファイルはCRLF(Writeツール由来)、他はLF。リポジトリ自体が混在(`core.autocrlf=true`)のため問題なし。
- `default_call_fn`(実API呼出部)はC1ではstubのみで検証(実API未実行)。Gemini REST/Luna SDKの実呼出確認は開発用確認run(累計¥300枠、本委任では未実行)で行う。

## 5. 台帳走査(¥0)

`er019_output/**/verified_fact_ledger.txt` **17件**を`parse_ledger_complete`で走査: **PASS 17 / FAIL 0**(決定論も二重実行で確認)。加えてPOST-EN Trial manifestの台帳(実記事11本)でstub E2Eも完走(完全性assertがUNAVAILABLEにならない)。証跡: `er053_output/risk_flagger_production_wiring_01/ledger_scan_er019_output.json`、`.../stub_e2e_01/summary.json`。

## 6. Dangling reference baseline(C1時点)

Production scope 9ファイルの合計 **385件**: er012_e 201 / entertainment runner 16 / jaw 148 / audio runner 20(うち`MAJOR`等の語) / 新規C1モジュール(W-1・RF・Queue・契約・splitter)は**0件**。内訳は`dangling_baseline_c1.json`。C2後に0または`SUPERSEDED`注記のみを確認する基準。

## 7. C2/C3への持ち越し

- C2: Writer差替え(`er019 ja_writer`→`run_w1_writer`)/旧Checker撤去(jaw・er012_e・entertainment runner)/契約検証の組込み(`validate_annotated_b3`をWriter入口に)/再利用分岐(revision2.md)でchain_method="W-1"かつannotated_md_sha256一致の確認(穴B)/RF呼出(Advanced直後・Standard直後、`budget_check`に`efam.assert_budget_ok`を渡す、`cl.logging_context`の外)/M1(a)無条件ON化(`_advanced_in_one_line`)/U-1(旧Writer記事STOP)/U-2(`--ja-article`封鎖)/E5 sha test(`test_E5_build_original_prompt_source_pre_c2_only`)をgolden出力比較へ置換/既存test 2件の更新(4-1)。
- C3: audio runner TTS直前の三者sha照合(`ensure_rf_record`)/`compute_cost_jpy_so_far`のfail-closed化(G-4)/runnerのcost.jsonを`compute_stage_cost_breakdown_multi`へ切替/Astra pricing note更新(OPEN-246文言)。
- 共通: S3-2(派生元sha観測記録)の採否はFable判断(C1では未実装)。

## 8. 禁止事項の遵守

DECISION_LOG / OPEN_ITEMS / CURRENT_SPEC / REPORT / REPORT_LEDGER / `docs/pm/ACTIVE_TASK.md` / `docs/pm/RESULT_PACKET.md` は未編集。git書き込み操作なし。Agent起動なし。
