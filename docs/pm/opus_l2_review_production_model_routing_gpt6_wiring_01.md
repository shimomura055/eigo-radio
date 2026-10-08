# PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 Opus独立レビュー(条件C、read-only、¥0)

管理ID: PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 / 日付: 2026-10-08 / 条件C(重要変更のProduction採用前) / 総合判定: 小規模な修正をしてから配線に進む(逐語保存、委任_02)

## 総合判定: 小規模な修正をしてから配線に進む
方針(全工程を6-lunaへ)には技術的な支障は見当たりません。ただし、計画書の前提とコードの実態がずれている箇所が3つあります(下記M1〜M3)。そのまま配線すると、費用ガード(Budget Guard)が無言で効かなくなります。ユーザー判断が必須の点はありません(論点5の監視閾値はFableが決めてよい範囲)。

## コードで確認した事実(計画書にない、または誤っている点)
- **F1: 予算ガードが「止まらない側」に倒れる(fail-open)**: Productionの予算ガード`er012_e_family_entertainment_two_level_runner_01.compute_cost_jpy_so_far`(L115-139)は、単価が見つからないmodelを`except StopIteration: usd = 0.0`で処理します。同じパターンが`er019_family_x_entertainment_production_runner_01.compute_stage_cost_breakdown`(L259-263)と、`er003_v1_n3_01_advanced_adaptation_generate`/`er003_v1_n3_01_standard_a2_generate`の`_compute_cost_jpy`にもあります。単価が未登録のままだと、cost.jsonが0円になるだけでなく、**`--budget-jpy`による停止が一切効かなくなります**。
- **F2: Fictionの`model_id != "gpt-5.6-luna"`は「model判定」ではなく「費用集計のフィルタ」**: `er026:696`と`er018:425,445`です。切り替えてもパイプラインは止まりませんが、Family Zの費用が**無言で0円**になります。単価の読み込みも、`er018:425`の`load_luna_pricing`が5.6専用です(`trial02.load_pricing`も同じ形と推定されますが未確認)。
- **F3: Fact Checkのmodelを実際に決めているのはWRITER_FACT_CHECK_MODELではない**: `vfl01.run_deviation_check(..., model: str = MODEL)`(L773)の既定値`MODEL = routing.WRITER_MODEL`(L57)で決まります。この値はimport時に固定されます。さらに関数内部に`require_model`がありません。つまりJA/EN Fact Checkは、実質`WRITER_MODEL`に連動して切り替わり、fail-closed(契約外modelを呼び出し前に拒否する仕組み)の対象外です。
- **F4: kp_explanationは契約変更で必ず止まる**: `er019_family_x_kp_explanation_01`はL43の`MODEL = "gpt-5.6-luna"`(直書き)でL259の`require_model("KEY_PHRASE_ADVANCED_EXPLANATION", MODEL)`を呼びます。`SUPPORT_MODEL`だけを変えると契約違反の例外が出て、Family Xが停止します。止まる側に倒れるので安全ですが、確実に起きる障害です。
- **F5: 一部は不一致を検知しない**: gather_topic(L29)、topic_adapter(L21)、coverage_gate(L17)は`require_model`を呼ばないため、契約を変えても**5.6のまま黙って動き続けます**。

## 論点別
1. **段階配線: 修正必要** 派生キーを個別定数へ分ける構造変更(案a)は勧めません。F3のとおりFact Check経路では分離が見かけだけになり、変更量とリスクだけが増えます。代わりに次の構成を推奨します。
   - Phase 0: `require_model_or_override`を使うprobe harness(Production code無編集)で、未確認工程を全部先に確認する。対象はBlueprint/Proper Noun/Std A2/Research/Gate/Support/KP/Query/Topic、費用は約¥20。
   - Phase 1: 単価登録と、単価lookupを未登録modelで止める形(fail-closed)への修正(M1)。
   - Phase 2: 定数7行と直書き箇所の修正(M2/M4)を一括でcommitする。
   - Phase 3: Production 1記事を最初から最後まで通す(E2E)。
   probeで問題が出た工程だけを`require_model_or_override`で5.6に残します。こうすると5.6と6-lunaの併存期間が短くなり、切り戻しもrevert 1回で済みます。計画書の3段階案でも可ですが、その場合はPhase 1の前に派生3キーのprobeが必須です。
2. **fail-closed: 修正必要** `require_model`本体は無変更で、未知model・未指定を拒否し続けます。直書き箇所の扱いは次のとおりです。
   - kp_explanation: `MODEL = routing.SUPPORT_MODEL`へ変更(必須、F4)。
   - gather_topic / topic_adapter / coverage_gate: routing参照へ寄せる。今回やらない場合は、5.6のまま残ることをOPEN-241に明記する(F5)。
   - Fiction: 費用集計の修正として必須(F2)。
   `run_deviation_check`に`require_model("WRITER_FACT_CHECK", model)`を足すのは任意です(O1)。ただし既定値はWRITER_MODEL由来なので、足すなら既定値を`routing.WRITER_FACT_CHECK_MODEL`に揃える必要があります。
3. **費用記録: 修正必要** 6-lunaの単価をpricing_snapshot.jsonへ追記するのは、定数変更**以前か同じcommit**で行います。書式は既存の5.6エントリ(L192-227)と同じ形でよく、追記する値は0.10/0.01/0.50と、cache writes 0.125を別meterで1件です。あわせて、F1の4関数を「Production経路で単価が見つからなければ例外」に変えます。さらに静的test「PROCESS_MODEL_MAPに出てくるOpenAI modelはすべてsnapshotに単価がある」を新設します。散らばった単価の直書き(101ファイル)はTrialの凍結扱いとし、一元化は別タスクで構いません。
4. **受入条件: 修正必要** 1 call probeは「互換確認」としては十分です。ただし呼び出し方のパターン別に確認項目を分けてください。
   - json_schema strict+reasoning effort: 返答がschemaに合うか、指定したeffort値が受け付けられるか。
   - web_search: web_search_call_countが記録されるか、引用を正しく読めるか。
   - 長文出力(Std A2): 途中で切れていないか。
   加えて、Production E2E 1本(Family X)で次の3点を実測する受入を追加します。
   - process別のmodel_idがraw_usage上ですべて6-lunaになっている(定数からの推測は不可、F3)。
   - cost.jsonが0より大きい。
   - 予算ガードの累計も0より大きい。
   未確認工程は「互換のみ確認、品質は未検証」と明記してください。
5. **STOP増: OK(別の論点として切り出すのは妥当)** 今回のTrialでは、Gate由来のSTOPが3/24から5/24(約13%→21%)に増えています。nが小さいため、本当の差は不確かです。Production量産の最初の10本で次のどちらかに当たったら、条件D(QCD悪化)として見直す、という再評価トリガーを今のうちに決めておくことを推奨します。
   - EN Advanced deviation STOPが3本以上
   - 保留が1記事あたり0.3以上
6. **切り戻し: 修正必要** 「定数7行を戻す」だけでは足りません。切り戻しの範囲は次のとおりです。
   - 定数と直書き修正のcommitをrevertする。
   - 単価の追記とfail-closed化は戻さない。
   - 常駐processは再起動が必要(既定値がimport時に固定されているため、F3)。
   旧Trial scriptは89ファイルを書き換えず、「本日以降の再実行は`require_model_or_override`で5.6を明示指定」とDECISION_LOGに記録します。今回の変更で必ず落ちるtestは更新が必要です。`er052_all6_writer_trial_01_test_01.py`(L45/54/65で5.6を前提)と`er006_model_routing_contract_01_test.py:24`です。
7. **タイミング: OK(条件1点)** Fact Lock Trialの生成完了後に配線する判断は妥当です。条件は、Fact Lock Trialがどのmodelで動いているかの確認です。5.6で動いているなら、6-lunaではFact Checkが厳しめになるため結論がそのまま当てはまりません。その場合、Fact Lockを採用する前に6-lunaで小規模な再確認を入れてください。配線の順序は「6-luna配線(commit) → E2E → Fact Lock配線(別commit)」とし、同じcommitに混ぜないでください(原因の切り分けができなくなるため)。

## M(必須)
- M1: 6-luna単価の追記を定数変更より先に行う。F1の4関数を未登録modelで例外にする。単価網羅の静的testを新設する。
- M2: Family Zの費用集計(er026:696と、その単価読み込み)を、routing由来のmodelで単価を引く形に直す。
- M3: 受入はraw_usageのprocess別model_id実測と、Production E2E 1本で行う(F3)。
- M4: kp_explanationのMODELをrouting参照に変える。SUPPORT_MODEL切替と同じcommitにする。
- M5: 派生キーを含む未確認工程は、パターン別probeを定数変更の前に行う。
- M6: 必ず落ちるtest 2件を更新し、切り戻し手順に「process再起動」と「単価は戻さない」を書き足す。

## O(任意)
- O1: run_deviation_checkにrequire_modelを入れ、既定値をWRITER_FACT_CHECK_MODELへ揃える。
- O2: gather_topic / topic_adapter / coverage_gateをroutingに寄せる(やらない場合はOPEN-241に明記)。
- O3: 論点5の再評価トリガー(最初の10本でEN STOP 3本以上、または保留0.3以上)をSSOTに記録する。

## 関連ファイル
- docs/pm/design_production_model_routing_gpt6_wiring_01.md
- er012_e_family_entertainment_two_level_runner_01.py(L105-147)
- er019_family_x_entertainment_production_runner_01.py(L240-276)
- er003_v1_en_direct_vfl_01_generate.py(L57, L773-810)
- er019_family_x_kp_explanation_01.py(L43, L259)
- er026_family_z_fiction_production_runner_01.py(L682-704)
- er052_all6_writer_trial_01_test_01.py

範囲の補足: Phase 2の「Production側Fact Checker / Ledger Deviation v2」の5.6箇所は、今回の読み取り範囲では特定していません。
