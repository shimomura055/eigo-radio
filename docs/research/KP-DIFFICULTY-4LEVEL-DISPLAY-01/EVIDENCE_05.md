# EVIDENCE_05 (KP-DIFFICULTY-4LEVEL-DISPLAY-01 委任_05, 2026-10-30)
目的: §7 #2(X/Y/Z x Std/Adv適用)・#3(正式runtimeでの難易度表示・判定証拠)を、mockなしの正式Production経路の実runで充足。

## 1. 実行方法
- 基点: origin/main(Prompt v2 sha 402d3b1a)。既存run(X ai_island_temple/run_kp75_ev_01、Y redelivery_fee/run_kp75_ev_01、Z melos/run_kp75_ev_01)を `<run>__kpd05` へコピーしKP候補状態だけ除去。**元runは不変**(tree sha256 前後一致: X 4394f246…/40files、Y c166ad54…/76files、Z ea63dd5b…/44files。`kpd05_run_result.json` src_unchanged=true)。
- 正式KP段: X=`er119_kp_wiring_01.run_kp_with_review`をer019:997と同一引数で、Y=`er121_family_y_runner_01._kp_review_step`、Z=`er026_family_z_fiction_production_runner_01._kp_review_step`(real mode、hookなし=実の候補生成、guard=Cap guard)。HR確定・TTS・ページ生成は未実施(全て KP_REVIEW_PENDING で停止)。直列実行、Cap 15円固定。
- 実行スクリプト: kpd05_run_01.py(生成)、kpd05_run2_01.py(後付け+完全実証)、kpd05_harvest_01.py(集計・export)、kpd05_live_verify_01.py(Playwright)。

## 2. 重要な逸脱(隠さず記録)
初回run(kpd05_run_01.py)は`test_state_isolation_01`をimportしており(HR queue等の本番監査logへ書かない隔離のため)、これが**難易度API呼出を遮断**(`er119_kp_difficulty_01.make_difficulty_fn`を差替え)。結果、生成・他段は実API(11.44円)で完了したが全6docが `difficulty_grading.status=FAILED_OPEN`(n_unknown=全件、候補は全件残存=fail-open実機確認)。
是正: (A)生成済み6docへ本番と同一関数`dg.apply_to_candidates`(gpt-6-luna、実API、process=A2_SUPPORT/B1_SUPPORT)を適用しdoc更新(原doc=`kp_candidates.blocked_fail_open.json`保存、candidates_sha256再計算、候補id順・他field不変を確認)。(B)Capの都合で全面再生成は不可のため、生成+難易度が**1 callチェーン**で付く完全実証は**X a2の1セットのみ**(新copy `__kpd05full`、遮断解除)。Y/Zの生成+難易度の完全一括は未実証(Y/Zは(A)の後付け適用)。

## 3. Family x level 証跡
| set | 候補 | status | model_id | prompt sha | graded/unknown | 易 | 中 | 難 | 激難 | routing | 生成call数 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| X Std(a2) | 10 | OK | gpt-6-luna | 402d3b1a | 10/0 | 3 | 5 | 2 | 0 | A2_SUPPORT=gpt-6-luna | 5 |
| X Adv(b1b) | 10 | OK | 同 | 同 | 10/0 | 1 | 7 | 2 | 0 | B1_SUPPORT=gpt-6-luna | 5 |
| Y Std | 8 | OK | 同 | 同 | 8/0 | 2 | 6 | 0 | 0 | 同 | 6 |
| Y Adv | 11 | OK | 同 | 同 | 11/0 | 2 | 7 | 2 | 0 | 同 | 5 |
| Z Std | 8 | OK | 同 | 同 | 8/0 | 4 | 4 | 0 | 0 | 同 | 10(外側retry含む) |
| Z Adv | 9 | OK | 同 | 同 | 9/0 | 2 | 7 | 0 | 0 | 同 | 5 |
- response_id・cost logger行: `kpd05_out/kpd05_evidence.json`(grading.response_id)、`kpd05_cost_logger_raw.jsonl`(provider=openai/model_id=gpt-6-luna、全call記録)。X a2完全実証: `kpd05_run2_result.json` full(difficulty callが同一run最終call、resp_01fd4e64…、status=OK 10/10)。
- Gateでないこと: 全6セットで候補id順序・他field(difficulty除く)が付与前docと完全一致、P7/W5' prompt shaも不変(`kpd05_evidence.json` order_ids_unchanged/other_fields_unchanged/p7_w5_prompt_sha_equal_pre=true)、候補件数は付与前後で同一。激難は0件(Prompt v2のheld-outで想定内、標本6セット)。
- 失敗経路: 初回runで難易度遮断→FAILED_OPEN(候補全残存・全件未判定)が実機で再現。

## 4. 実表示(公開フォーム)
- export: `export_form_data_01.convert`(PRODUCTION_FORMAL_PATH)で6セットをdata化(`kpd05_out/kpd05_form_data/`)、validateArticle=[]。
- 正式フォーム `https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/?a=kpd05_<x|y|z>__<a2|b1b>` に「【表示確認用】難易度バッジ確認 …」の一時エントリ6件を追加(commit ab04afd2c)→Pages反映後にPlaywright(PC 1280x900/mobile 390x844): バッジ数=候補数=doc、label列がdocと一致、横溢れなし、JSエラーなし = **60 checks全PASS**(`kpd05_live_live.json`)。スクショ12枚=`kpd05_shots/kpd05_live_{pc,mobile}_kpd05_*.png`。
- 一括画面: `--set-batch`(export_form_data_01)を公開フォームのarticles.jsonへ入れると**公開フォーム全体が一括画面へ切替わる**ため避け、一時ページ `user_test/kpd05_batch_tmp/`(index.html/form_logic.jsは公開版の無変更コピー、6セットbatchキー)で確認: 6 chip x PC/mobile = **28 checks全PASS**(`kpd05_live_livebatch.json`)、スクショ12枚`kpd05_shots/kpd05_livebatch_*`。URL=`https://shimomura055.github.io/eigo-radio/user_test/kpd05_batch_tmp/`(除去済み)。
- 除去: commit a5b46b7cb でarticles.jsonを基点(8527107f2)の内容へ復元(`git diff 8527107f2 -- user_test`=空)・一時data/ページ削除。除去後live確認(articles.jsonにkpd05なし、data/ページ404、本文に「表示確認用」なし)= `kpd05_live_liveafter.json` 12 checks PASS。公開露出期間は約13:50〜13:56(JST、Pages反映遅延込みで約6分+除去反映)。

## 5. 費用
実費13.49円(cost logger実測、gpt-6-luna単価、Cap 15円内): 初回生成11.44(6セット、約1.9円/セット)+後付け難易度6call 0.49(0.081円/call)+X a2完全実証1.56(うち難易度call約0.08)。
追加量産単価(難易度のみ): 0.081円/call x 2(Std+Adv)=約0.16円/記事セット(70円の約0.23%)。委任_02推定0.11より増(Prompt v2の出力増)。
本日(JST)累計: daily_cost.py下限 994.4円(開始時)→996.3円(中間)。本委任実費13.49円を含めると日次1,000円を超過した可能性が高い(daily_costはgemini_batch等を0円扱いの概算下限)。

## 6. §7 12項目(Fable受入#11以外)
| # | 判定 | 根拠 |
|---|---|---|
| 1 正式初回Production経路 | 充足 | 3 Familyの正式KP段を実行 |
| 2 X/Y/Z x Std/Adv適用 | **充足** | 6セット全てdoc付与(status OK)。生成+難易度1 callチェーンはX a2のみ、他5は後付け適用(逸脱節2) |
| 3 正式runtime表示・判定証拠 | **充足** | model_id/sha/response_id/cost logger/export/ライブURL PC・mobile実表示(単体60+一括28) |
| 4 test | 充足 | 委任_02/04のtest(コード無変更) |
| 5 retry/fallback/resume | 充足 | 委任_02 |
| 6 DEV/Trial専用でない | 充足 | |
| 7 actual model_id/Prompt/routing | 充足 | gpt-6-luna、sha 402d3b1a、SUPPORT_MODEL |
| 8 SSOT | 充足 | OPEN-622/DECISION-05/CURRENT_SPEC |
| 9 Dangling | 充足 | 本番コード変更なし |
| 10 Git | 充足 | origin/main |
| 11 Fable受入 | 未(Fable) | |
| 12 承認仕様と実動作一致 | 充足 | 4段階表示・Gateでない・候補不変・fail-open実機確認。未確認項目=Y/Zの完全1 callチェーン(後付け適用で同一関数・同一Promptを実API確認)。Fableが重大でなければPRODUCTION_WIRED可、気になる場合は追加費用約3.4円でY/Z各1セット完全実証(Cap要再設定) |
