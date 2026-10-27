# IMPL_PLAN_01 実装計画(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01。設計のみ・実装は次委任以降)

前提: DESIGN_01のOpus条件A GO後に着手。承認(`APPROVED_FOR_PRODUCTION`)済みのため新flag/既定OFFは設けない(Production配線)。ただしKCPの`protection_enabled()`(既存・単一読取点)は変更しない。到達目標=PRODUCTION_WIRED(全6経路が揃うまで一括判定しない)。

## 1. 作業分解・依存・並列化(Charter 2: 独立作業は並列)

| ID | 作業 | 主な対象 | 依存 | 並列 | 見積(wall) |
|---|---|---|---|---|---|
| F-0 | Opus条件A反映(設計修正) | DESIGN_01 | Opus結果 | - | 0.5h |
| F-1 | 共通核の`level`引数化・複数選定・`items[]`結果・描画・Validator複数item・`run_part2`のStep B撤去・schema v2(v1読取互換) | `er120_part2_grammar_production_01.py` | F-0 | F-2/F-3の設計IFを先に固定すれば並行可 | 3h |
| F-2 | `pregen_stage`・`grammar_explanations.json`・`form_grammar_items`・`finalize_stage`(LLM 0)・`study_dir_for`・`stage_names` | `er120_part2_wiring_01.py` | F-1のIF | F-3と並行 | 2h |
| F-3 | 文法HR level化・依頼書(解説全文)・`pick`・`discover_dirs(level)`・CLI `--level/--ids`・統合依頼書のlevel表示 | `er119_grammar_review_01.py`/`er119_kp_human_review_cli_01.py`/`er119_kp_wiring_01.py` | F-1のIF | F-2と並行 | 2h |
| F-4X | Xadapter: scaffold両level・`--stage study_text`のlevel許容・tts/assemble/player入口・`build_player_html`にStd節差込・記事別page script→共通関数 | `er019_family_x_audio_production_runner_01.py` | F-2,F-3 | F-4Y/F-4Zと並行 | 2h |
| F-4Y | Yadapter: UNIT/DEPENDENTS・`stage_kp`両level・`_assert_study_ready`(tts_a2)・`stage_pages`level別差込・検証置換 | `er121_family_y_runner_01.py` | F-2,F-3 | 並行 | 2h |
| F-4Z | Zadapter: DEPENDENTS/ALL_STAGES・`load_level_inputs`・`build_pages(study_html_by_level)`・検証置換 | `er026_*`/`er062_*`/`er063_*` | F-2,F-3 | 並行 | 2h |
| F-5 | フォームデータ接続(`export_form_data_01.main`に`--grammar`/自動接続、`grammar_status`3値、`body`=解説全文)。**フォーム担当委任と契約共有**(UI不変) | `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`・`build_data_01.py`・`user_test/selection_form_v3/data/*`(フォーム担当の所有) | F-2のIF | 並行 | 1h(契約)+フォーム側 |
| F-6 | KCP改修: level別sidecar・`cmd_from_form`文法照合(id/title/body/件数)・文法review `pick`のatomic適用・凍結v2(items[])・`guard_grammar`にpart2_expl追加・M8再バインドのitem反復 | `er128_kp_confirmed_content_01.py`ほか(KCP所有) | F-1 | F-4と並行 | 3h |
| F-7 | 検証置換(`*_ON_STANDARD_PAGE`→`*_WRONG_LEVEL_SECTION`)・旧Dangling Grep | 各runner | F-4 | - | 0.5h |
| F-8 | test更新/新設(TEST_PLAN_01)。mock(`er120_part2_mock_01.py`再利用)でF-1/F-2と**同時進行(TDD)** | 各testファイル | F-1 IF | 並行 | 4h |
| F-9 | evidence(EVIDENCE_PLAN_01) | runner実行 | F-4,F-6,F-8 | X/Y/Z並行 | 2.5h |
| F-10 | SSOT更新(CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS/OPERATIONS_01)・旧Adv限定の履歴化(ADV_ONLY_INVENTORY §7) | SSOT | F-9 | - | 1h |

クリティカルパス: F-0 → F-1(3h) → F-2/F-3(2h) → F-4X/Y/Z並行(2h) → F-6統合(1h) → F-9(2.5h) → F-10(1h) ≈ **12h wall**(直列なら約24h)。

## 2. ファイル所有・競合回避
- F-1/F-2/F-3/F-4/F-7/F-8は本系(GRAMMAR-PREGEN)所有。**`er128_kp_confirmed_content_01.py`・`er119_kp_human_review_01.py`・`er119_kp_human_review_cli_01.py`・フォームdata/exporterはKCP/FORM所有**。実装時は(1)当該Agentの完了確認 (2)`git show origin/main:<path>`基準で差分を取得 (3)所有Agentに契約(DESIGN_01 §3-(c)(e))を渡し本系で改修するか同Agentへ依頼するかをFableが決める。
- `git add`は変更ファイルのみpathspec指定(`-A`禁止)。無関係な既存差分(`er*_output`等の未commit変更)に触れない。

## 3. 変更の要点(関数単位)
- F-1: `LEVELS`、`level`引数を`build_candidates_doc`/`finalize_review_record`/`zero_result`/`build_result`/`result_from_frozen`へ。`select_from_candidates`→`select_from_candidates_v2(doc, review, mode)`(`pick`、`candidate_ids`)。`GRAMMAR_MAX=2`、`PREGEN_MAX=8`。`grammar_selection_signature`はschema別式(v1式は完全に保存)。`require_fresh_part2`/`_expected_outcome`/`verify_selection_matches_outputs`は`items`を走査(AND追加。既存検査は弱めない)。`render_markdown`/`render_html_block`は`items`(1件はバイト同一)。`run_part2`は`generate_explanation`を呼ばず`explanations`/`frozen`を受ける。
- F-2: `pregen_stage`はF-1の`generate_explanation(cand, None)`のみ呼ぶ(Prompt/`_run_llm`無変更)。`explain_signature`有効性判定。原子的更新。`part2_failed.json`(stage=`part2_expl`)。`finalize_stage`はLLM 0。`form_grammar_items`は純関数(API 0)。
- F-3: `LEVEL_KEY`定数→`level_key(level)`。依頼書は解説全文を載せる(PRODUCTION-HR-PACKET-FORMAT-01の新形式[原稿・推奨・AI評価]を壊さない: 文法側のパケット形式は既存OPEN-557の範囲に沿う。パケット様式の変更は不要・追記のみ)。
- 後方互換の固定: 既存Adv runの`grammar_human_review.json`(v1)/`part2_result.json`(v1)/`confirmed_grammar*.json`(v1)を**そのまま読める**(書換え・再署名しない)。旧runのページ再生成(pages/page_verify)がバイト同一になること。

## 4. 旧ルール撤去・残置の確認手順(Charter 8)
実装後に以下をGrepで0件(現行コード/現行仕様に限る。履歴文書は許容)を確認し、残存はADV_ONLY_INVENTORY_01 §7の「履歴化/維持」に一致することを示す:
`ON_STANDARD_PAGE`, `Standardには出さ`, `Advanced=b1bのみ`, `適用レベル=Advancedのみ`, `LEVEL = "Advanced"`(定数直書き), `LEVEL_KEY = "b1b"`, `level == "b1b"`(文法処理内), `"advanced" and study_html`, `label == "Advanced"`(study差込), `generate_explanation(`の呼出点(pregen以外0)。

## 5. 既定値・Production到達経路(安全性)
- 新flagなし。正式runnerの`--stage`/既定経路が新フローになる(承認済みProduction採用)。ただしA/B/C Family・共有moduleへ文法kindを持ち込まない(`er119_isolation_test_01`維持)。
- DefaultOff: 該当なし(承認済み仕様の本配線)。代わりに「文法候補0件・HR不在宣言なし」の既存既定(rc=4待機)を維持することをtestで固定。
- 実装中の未承認機能混入なし: Prompt sha・閾値・辞書・正規表現を編集しない(sha不変testで保証)。

## 6. リスクと緩和
| リスク | 緩和 |
|---|---|
| Std本文の候補が0件ばかり/偽陽性 | EVIDENCEで実測。Prompt無変更の方針を維持し、偏りは事実として報告(D-a) |
| 複数item化でKCP凍結の既存testが壊れる | v1読取互換+v1式署名固定。KCP test(`er128_*_test`)を先に通す |
| 事前生成の課金増(誤って全run/全resumeで再生成) | signature一致skip+呼出回数spy test(T3)+`PREGEN_MAX`+予算guard |
| Xの記事別page scriptが共通関数を通らない | `public_study_html(level=)`へ集約し、script内の直接組立をGrepで検出 |
| フォームとのデータ契約ずれ | `explanation_full==事前生成物`をKCP側でISSUE化(F-6)。双方のtestで同じfixtureを使用 |
