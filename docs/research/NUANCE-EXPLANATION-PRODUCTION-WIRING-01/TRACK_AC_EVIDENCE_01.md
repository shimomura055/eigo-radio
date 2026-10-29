# TRACK_AC_EVIDENCE_01 — NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02B(Track A: 表示・page_verify一般化 / Track C: HR統合)

実施日: 2026-10-29。API呼出 0・費用 0円。Production承認: ユーザー2026-10-29 正式採用(`docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_USER.md`)。
本委任の範囲は「表示」「page_verify一般化」「HR統合(フォーム/exporter/確定)」のみ。**runner配線(N0/N1/finalize の呼出)は委任_02C**であり、本委任の時点ではニュアンス解説を生成・確定結果へ書き込む経路は存在しない(`nuance_result.json` が無い=従来通り何も表示しない)。

## 1. 変更一覧(file:line は変更後の現在値)

### Track A: 表示・数・検証
| ファイル | 内容 | 位置 |
|---|---|---|
| `er120_part2_grammar_production_01.py` | `NUANCE_HEADING="ニュアンス解説"`(『Deeper Understanding』不使用=R-12)/`NUANCE_RESULT_FILENAME`/`NUANCE_ADOPTED` | :164-166 |
| 同 | `NUANCE_REQUIRED_FIELDS`・`render_nuance_html_block`(独立コーナー1ブロック。CSS付与は引数制御) | :1489,:1520 |
| 同 | `compose_study_html(part1_html, result, nuance=None)`: Part 1 → 文法 → ニュアンス。**最初の非空ブロックだけがCSSを持つ**。文法0件は固定文面を出さず**ブロック自体を出さない** | :1535 |
| 同 | `count_nuance_blocks` / `count_empty_study_sections`(`<h3>`で始まる空の `section.study` を検出) / `verify_nuance_in_section`(節単位の逐語一致=M-7) | :1545,:1553,:1565 |
| 同 | `retire_part2_md`(旧0件runの固定文面mdを `.legacy_zero_p2.md` へ決定論退避。削除しない=M-6) | :1419 |
| 同 | `ZERO_P2` 定数を撤去(R-13)。旧固定文面は旧md判定のための `_LEGACY_ZERO_GRAMMAR_BODY` のみ残置 | :163 |
| `er120_part2_wiring_01.py` | `nuance_for_display`(ADOPTEDのみ返す。ADOPTEDで必須項目欠落/`level_key`不一致=`Part2Stale`。REJECTED/NONE/FAILED_TECHNICAL/ファイル無し=None) | :442 |
| 同 | `expected_block_counts` / `verify_outputs`(期待数 0 or 1 を返す。**0件はmd不在を要求**=M-6)/`_verify_grammar_outputs` | :462,:469,:496 |
| 同 | `compose_page_html(part1_html, result, *, nuance)`: **`nuance`は必須keyword**(R-6。呼出元の渡し忘れはTypeError) | :611 |
| 同 | `finalize_stage`/`write_md`/`public_study_html`: 0件はmdを書かず、旧mdがあれば退避。公開(Std/Public)builderはPart 2を呼ばない(従来通り) | :309,:377,:624 |
| `er121_family_y_runner_01.py` | `_blocks_in_page_order`(存在するブロック同士の相対順=M-5。文法0件でも例外にならない)/`_verify_part2_outputs`(期待数0or1)/compose呼出に `nuance=` | :1028,:1037,:1067,:1302 |
| `er026_family_z_fiction_production_runner_01.py` | `_verify_part2_outputs`(期待数0or1・ニュアンスブロック)/DEV詳細ページにニュアンス解説が載らないことの検査/compose 2箇所に `nuance=` | :1843,:2644,:2645 |
| `er019_family_x_audio_production_runner_01.py` | compose 2箇所に `nuance=` | :4092,:4094 |

### Track C: HR統合
| ファイル | 内容 | 位置 |
|---|---|---|
| `er128_kp_confirmed_content_01.py` | 定数 `SCHEMA_NUANCE`/`FILE_NUANCE="confirmed_nuance.json"`/`FILE_NUANCE_SPEC`/`FILE_NUANCE_CANDIDATE` | :63,:70-72 |
| 同 | `_nuance_problems`(G0/G1での整合検査)・`_nuance_quotes`(再束縛時に採用引用が新本文に残ることを要求) | :525,:791 |
| 同 | `cmd_from_form(..., grammar_pending=False)`: `selection.nuance={decision,candidate_sha256,id}` を検証。**未回答(候補あり)=ISSUE rc=4(何も保存しない)**/候補なしでnuance送信=ISSUE/LEGACY(`nuance_spec.json`なし)でnuance送信=CliError/古いフォーム(sha不一致)=ISSUE/採用+②①のpool_conflicts選択=ISSUE/**M-4: 確定①②の全idが `overlap_check.against[]` に無ければ採用はISSUE**(不採用は受理)/pool同一性変化(M-3: `pool_identity_sha`)=ISSUE | :1432,:1710 |
| 同 | `_write_nuance_sidecar`: 文法sidecarの**直後**に `confirmed_nuance.json` を書く(コミット点=KP確定レコード保存は不変)。`nuance_state`は **`confirmation_id` + `pool_identity_sha` + `text_sha256`** で結合(M-3: `candidates_sha256`では結合しない=confirm-reviseで誤STALEにならない)/改ざん=IntegrityViolation | :1797,:1816 |
| 同 | `previous_nuance_decision`(R-11: revoke後の再確定で旧採否を既定表示。明示送信は必須)/`_archive_prior_nuance_files`(旧sidecarを `confirmed_nuance.RECONFIRM_SUPERSEDED*` へ退避。削除しない)/`guard_nuance`(確定後の候補再生成はrevoke必須) | :1848,:1792,:1861 |
| 同 | `nuance_id_of`/`nuance_pool_identity_sha`/`nuance_presented_ids`(**exporterと同一の提示集合**) | :1683,:1688,:1695 |
| 同 | **R-4: SUPPRESSED状態は設けない**(人間の採用を自動で覆す経路なし。重複はISSUE)/**R-1: `--grammar-pending`と結合しない**(ニュアンスは文法の確定を待たずに確定) | (test固定) |
| `er128_form_readable_restore_01.py` | 照合コード **AIF2**(`nuance_spec`付きデータ専用。`n8=sha256("v1\n"+decision+":"+candidate_sha256)[:8]`、候補なし=0)。`nuance_spec`なし=**AIF1のまま出力バイト不変**。ニュアンス本文ブロックはデータJSONと逐語照合/AIF1⇄AIF2の取違え・採否書換え・本文改変・ブロック削除は拒否 | :49-50,:141,:168,:187,:365-397,:478-489 |
| `user_test/selection_form_v3/form_logic.js` | `nuanceDecision/chooseNuance/nuanceConflicts/nuanceBlocked/nuanceBodyText`・`makeCode(..., nuanceSel)`(AIF2)・`buildReadable`(未決定ならthrow)・`buildStructured`(`schema_minor=2`+`selection.nuance`)・`validateArticle`(欠落データ拒否)。別候補sha向けの旧回答は引き継がない | :53-74,:215-222,:293-339,:373-380 |
| `user_test/selection_form_v3/index.html` | ニュアンス欄(採用/不採用ラジオ・pool_conflicts警告[赤]・grammar_conflicts/shared_termsは警告のみ・技術失敗の注記[R-5]・前回確定の既定表示[R-11])/`guard()`が未回答・重複で送信/コピーを止める | :9-10,:81,:86-108,:133-137 |
| `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py` | `--nuance-study-dir`: `form_nuance_bundle`を直接読んで `nuance_spec`/`nuance`(または `nuance_note_ja`)を出力。`nuance_spec.json`なし=キーを出さない(従来とバイト同一)。候補doc不整合=データを出さずrc=4 | :234,:271-277,:342-349 |
| `er120_part2_wiring_01.py` `form_nuance_bundle` | N1の候補docから `nuance_spec`/`nuance` を組立て。FAILED_TECHNICAL=「候補なし(技術失敗)。本物の0件ではありません」(R-5)/鮮度(candidates_sha256は**HR提示時のみ**)/重複判定 verdict!=pass はHRに出さない | :540 |

### 委任範囲外として未着手(02C)
runnerへのN0/N1挿入・M-1/M-2、finalizeでの `nuance_result.json` 書込み位置・DEPENDENTS(R-3/R-7)、CLI `nuance-show`/`nuance-select`。

## 2. テスト(全てmock・API 0)
- 新規 `er120_nuance_display_test_01.py`: **11 PASS**(ニュアンス{採用/不採用/候補なし/技術失敗/結果なし} × 文法{採用/0件} × Part 1{有/無} × X/Y/Z配置 × Std/Adv = 120組で、見出し・空枠・固定文面・プレースホルダー・二重CSSが無く Part 1 → 文法 → ニュアンスの順/`verify_outputs`が期待数を返す/Std・Adv取違え・数不一致・禁止語・空枠の検出/`nuance_result`のfail-closed/旧0件mdの退避/`compose_page_html`の`nuance`必須keyword・全呼出元が渡している/ZERO_P2が本番moduleに無い)。
- 新規 `er128_nuance_hr_test_01.py`: **37 PASS**(採用/不採用/未回答ISSUE/不正決定・古いフォーム/確定後ロック/M-4被覆欠落[採用=ISSUE・不採用=受理]/pool_conflicts[選べば採用不可・選ばなければ採用可]/grammar_conflictsは警告のみ/pool同一性変化ISSUE/候補なし・FAILED_TECHNICAL・LEGACY・仕様マーク有で候補doc無し=ISSUE/M-3 confirm-reviseで誤STALEにならない・sidecar不変・record印の引継ぎ/sidecar改ざん/引用再束縛/R-11 revoke→再確定で旧採否の既定表示と旧sidecar退避/R-1 `--grammar-pending`非結合/SUPPRESSED廃止/exporter提示集合の同一性/**node(form_logic.js)とPython(復元ツール)の人間可読コピーのバイト一致[採用・不採用・候補なし・LEGACY]**/復元payloadが node `buildStructured` と一致/AIF1バイト不変・LEGACYはAIF1のまま/採否書換え・本文改変・ブロック削除・AIF1⇄AIF2取違えの拒否/フォームJSの未回答・重複ブロック/index.htmlの構文・ニュアンス欄の描画[仕様マーク無しは非表示・採用/不採用ラジオ・技術失敗の注記・前回確定の既定表示]/exporterのキー追加が仕様マークの有る時だけ)。
- 追加: `er121_y_highlight_wiring_test_01.py::MarkedPipeline::test_adopted_nuance_is_verified_per_section_by_the_real_validator`(**Yの実validator `r._verify_part2_outputs`**に、採用結果+ページ節を与え、採用=1個PASS・取違え/欠落/重複/不採用なのに掲載=STOP・結果ファイル無し=従来どおり、を確認。1 PASS)。Z/Xはcompose呼出元(6経路の合成はT1_Matrixで検査)と共通の `p2w.verify_outputs`(T2で節単位検査)を通る。Zの実validatorを通すE2E fixtureは重いため、Z/X実validator単位の採用ケースtestは未追加(§5の未実施)。
- 既存testの更新(旧仕様の期待値を新仕様へ):
  - `er120_part2_grammar_production_01_test_01.py`: ZERO_P2のassertを削除(R-13)。
  - `er120_part2_wiring_integration_test_01.py`/`er120_part2_pregen_test_01.py`/`er120_public_study_html_level_test_01.py`/`er119_grammar_review_test_01.py`/`er003_kp_general_explanation_01_runner_integration_test_01.py`/`er019_x_highlight_wiring_test_01.py`/`er026_z_highlight_wiring_test_01.py`/`er121_y_highlight_wiring_test_01.py`/`er121_family_y_runner_01_test_01.py`: 「文法ブロックちょうど1個」→「0 or 1」、compose呼出に `nuance=`、er134の許可importer追加。
  - `er128_form_readable_restore_test_01.py::test_extra_unknown_version`: 未対応版の見本を `AIF2`→`AIF3` に変更(AIF2は本委任で対応版になったため)。
- 回帰: 下記 §4。

## 3. 4組合せのHTML断片(`compose_page_html`の実出力。X/b1b。CSSは`<style>…STUDY_CSS…</style>`と略記)
(A) 文法採用 × ニュアンス採用:
`<style>…</style><section class='study'><h3>Vocabulary &amp; Expressions</h3>…</section><section class='study'><h3>Grammar &amp; Sentence Structure</h3>…</section><section class='study'><h3>ニュアンス解説</h3><div class='study-item'><h4>at least</h4><dl><dt>ポイント</dt><dd>at least が示す『最低限』という語感</dd><dt>解説</dt><dd><p><b>at least</b> は『少なくとも』という最低ラインを示します。</p>…</dd><dt>本文の英文</dt><dd>At least she was safe.</dd><dt>日本語訳</dt><dd>少なくとも彼女は無事だった。</dd></dl></div></section>`
(B) 文法採用 × ニュアンス不採用: `<style>…</style>` + Vocabulary節 + Grammar節(ニュアンス節なし。長さ582)
(C) 文法0件 × ニュアンス採用: `<style>…</style>` + Vocabulary節 + ニュアンス解説節(**Grammar節・固定文面とも無し**。長さ508)
(D) 文法0件 × ニュアンス不採用: `<style>…</style>` + Vocabulary節のみ(長さ189。Part 1も無い場合は空文字列でCSSも出さない=テスト済)
生成物の全文: `docs/research/NUANCE-EXPLANATION-PRODUCTION-WIRING-01/track_ac_html_fragments_01.txt`(生成スクリプトは `er120_nuance_display_test_01.py::T1_Matrix` が同じ関数を同じ組合せで検査)。

## 4. 既存回帰(er120/er128/er119/er121/er019/er026/er003統合/er134 = 86ファイル)
対象: er003統合 / er019 / er026 / er119 / er120 / er121 / er128 / er134 のtest 86ファイル(`.venv/Scripts/python.exe -m pytest <86 files> -q`、1プロセス・約18分)。
結果(本委任の最終変更後): **2138 passed / 15 failed / 1 error(teardown) / 3 skipped / 2291 subtests passed**。(この後にY実validatorのtest 1件を追加し、`er121_y_highlight_wiring_test_01.py` 全体=25 PASSを個別に再確認。新規2ファイル含む3ファイル合算 73 PASS。)

失敗15+1の分類(本委任の変更が原因のものは0件):

| # | test | 分類と根拠 |
|---|---|---|
| 1 | `er003…runner_integration…::ZPart1Tests::test_kp_expression_change_needs_two_step_regeneration_with_hints` | 既存失敗。HEAD(93ad8ee76)のcleanなworktreeでも同じtestが失敗。 |
| 2 | `er019_x_std_chunk_opus…::R4HunkClassifierTest::…` | 既存失敗(HEADで同様に失敗)。 |
| 3 | `er119_grammar_review…::test_public_builder_and_standard_never_call_part2` | 既存失敗(HEADで同様に失敗。`compose_page_html(`出現数2≠1。本委任以前から)。 |
| 4 | `er119_isolation…::test_only_x_z_runners_import_er119` | 既存失敗(HEADで同様。importerにer121/er123/er124が居る旧不整合)。 |
| 5 | `er119_z_wiring…::test_part1_items_follow_vocab_confirmed_five` | 既存失敗(HEADで同様。`_part1_items_b1b`属性が無い)。 |
| 6 | `er121_family_y_structure_match…::test_a2_common_calls_not_dropped` | 既存失敗(HEADで同様。`RuntimeError`許可リスト漏れ)。 |
| 7 | `er128_kp_confirmed_content…::TestIsolation::test_abc_and_shared_functions_do_not_import_er128` | 既存失敗(HEADで同様。別委任のer129がer128をimport)。 |
| 8 | `er119_grammar_review…::test_grammar_files_not_tracked_dirs` | 環境起因。`er119_output/`(未追跡)が2026-10-25から実リポジトリに存在する(本委任のtestが作ったものではない。日付で確認)。 |
| 9-14 | `er121_*::test_no_network_or_real_client_attempts` ×4・`FullMockRun::test_api_boundary_only_mock_kinds_and_no_real_client`・`StageFramework::test_default_mode_is_dry_run…`+ 1 teardown error(`NoResidualReferences`) | 1プロセスにまとめて走らせたときだけ出る順序依存の汚染。これらのtestは単独実行で全PASS。**HEADのcleanなworktreeでも、`er003統合`または`er119`のtest群の直後に`er121_family_y_audio_chunk_test_01.py`を走らせると同じ`test_no_network_or_real_client_attempts`が失敗する**ことを再現(= 本委任の変更に依存しない)。ブロック発生元は`er121_family_y_audio_chunk_test_01.py`のTestPlan/TestGenerateAndAssemble(実client生成を遮断カウンタが検出。blockwatch計測で7 testが+1〜+2ずつ加算)。 |
| 15 | `er121_family_y_voice_table…::test_existing_run_01_and_public_pages_not_modified` | 本委任の変更(`user_test/selection_form_v3/form_logic.js`・`index.html`=公開フォームの更新)が**未commit**の間だけ失敗する「tracked公開ファイルを変更していない」検査。commit(1f9ad586d)後に `er121_family_y_voice_table_test_01.py` 9 PASSを確認済み。 |

HEAD側の比較は、(a) HEADのworktree(93ad8ee76。ignoredな`erXXX_output`が無いため多数のtestがartifact不在で別途失敗する)で同じ失敗ID集合を実行、(b) `er121_*` 17ファイル全体をmainとHEADで並走(main=2 failed[上記6,15のみ]/HEAD=14 failed[artifact不在含む])、(c) 順序依存の再現、で確認した。新たに「mainだけで失敗し、原因が本委任の変更」と特定されたtestは無い。

追加確認(AIF1バイト不変): `er128_form_readable_restore_test_01.py` 55 PASS(従来のAIF1契約fixtureとのバイト一致・公開データ全件×乱択の往復を含む)、`form1_selection_form_v3_test_01.py` は4件失敗だが全てHEADでも同一(`index.html` 9枠数・source docの旧パス・`what節主語`解説不一致 = 公開データ起因。本委任の変更前から)。

## 5. 未実施・申し送り
- CLI `nuance-show` / `nuance-select`(HRをCLIで行う経路)は未実装(V3フォーム→`confirm --from-form` と読みやすいコピー→`restore` の2経路は実装・test済み)。
- `nuance_result.json` の書込み(finalize)、N0/N1の挿入・HR待機(rc=4)、DEPENDENTS(R-3/R-7)は委任_02C。本委任の時点では実run上でニュアンス解説が表示されることはない(`nuance_spec.json`を作る経路が無い=全runがLEGACY扱い)。
- `form_nuance_bundle`/`nuance_pool_identity_sha` は er134 の内部関数(`_pool_entry`等)に依存する箇所がある。er134側の改名で壊れるため、02C以降はer134側のpublic wrapperへ寄せるのが望ましい。
- exporter(`export_form_data_01.py`)は作業開始時に、別作業の未commit差分(最終printの `"grammar"` キー重複2件)が混入していた。本委任のpatch内で単一キーに戻した(HEADと同じ)。
- 公開済みHTML(ZERO_P2固定文面入り15ファイル)は触っていない(R-14)。
