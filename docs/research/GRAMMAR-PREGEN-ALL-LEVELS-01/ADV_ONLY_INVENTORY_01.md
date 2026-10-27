# ADV_ONLY_INVENTORY_01 旧Advanced限定仕様・旧コード条件・SSOT不整合の棚卸し(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01、read-only・API 0)

基準: `origin/main`(93915b971)。判定語=**撤去**(コード条件・検査を除く)/**更新**(新仕様に書換え)/**履歴化**(現行仕様として参照されないよう「旧仕様・2026-10-27ユーザー決定で置換」と注記して残す)/**維持**(今回の決定と矛盾せず変更しない)。
原則: 今回のユーザー決定(原文`docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_USER.md` §1,§3,§6)が優先。**範囲を狭める判定はしない**。維持は「今回の4項目の対象外であることが原文で明らか」なものだけ。

## 0. 重要な事実: 「Part 2はAdvancedのみ」の出所(原文照合)
- 2026-10-25ユーザー原文(`docs/pm/delegation_log/2026-10-25_PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md`:90)は「**Standard／Advancedなど、既存Productionで対象となるレベルについて**…検証する」。Advanced限定とは書いていない。
- 限定は**AI側の設計判断**: `docs/research/PART2-GRAMMAR-PRODUCTION-WIRING-01/DESIGN_02.md:5,77`(「適用レベル=Advancedのみ(Trial-07/08の全実績がAdvanced、Part 1前例と整合)。Standard(a2)は新仕様のため非適用」)、`er120_part2_grammar_production_01.py:42`のコメント(「Standard(a2)への拡張は新仕様=行わない」)、`DECISION_LOG.md:21`の実行記録(「適用レベル=Advancedのみ」)。
- → 今回の決定(§1「旧仕様を根拠にStandardを対象から外してはならない」)により、**これらはユーザー原文に基づかない旧AI判断として置換**。旧記述は履歴化。

## 1. ユーザー§6-1「文法解説をAdvancedに限定する旧記述・コード条件・表示条件」

### 1-A. SSOT/設計文書
| # | 場所 | 内容 | 判定 |
|---|---|---|---|
| S1 | `CURRENT_SPEC.md:2099` | 「Part 2はAdvancedのみ・Part 1直後」 | **更新**(Std/Adv両方・Advは従来どおりPart 1直後、StdはPart 2のみ) |
| S2 | `CURRENT_SPEC.md:2096-2098`(見出し「KP Human Review・文法Human Review・Part 2…Family別Status」) | Status本文(X/Y/Z PRODUCTION_WIRED) | **維持**(Advのevidence事実。履歴)。末尾に「Std追加=GRAMMAR-PREGEN-ALL-LEVELS-01、未配線」を追記 |
| S3 | `CURRENT_SPEC.md:2080`(見出し「Family X/Z 学習テキスト Part 1…(Advancedのみ)」) | **Part 1(Vocabulary & Expressions)**のAdv限定 | **維持**(今回は文法解説のみ。Part 1をStdへ広げる決定は無い。要確認事項としてFableへ。DESIGN_01 §7 Q3) |
| S4 | `CURRENT_SPEC.md:3104`(Yの接続状況) | 「Part 2…コード接続済み(Advancedのみ)」の事実記述 | **履歴化**(注記追加のみ) |
| S5 | `DECISION_LOG.md:21` | 「適用レベル=Advancedのみ」(実行記録) | **履歴化**(エントリは不変。新エントリで置換を記録) |
| S6 | `OPEN_ITEMS.md:1034`(OPEN-519)内「Advancedのみ(Trial-07/08の全実績がAdvanced。Standard拡張は新仕様=行わない)」「Advancedのみ(Standardは新仕様のため非適用)」 | 同上 | **更新**(OPEN-519末尾にGRAMMAR-PREGEN-ALL-LEVELS-01参照と「Std非適用は2026-10-27ユーザー決定で撤回」を追記。本体行は書換えず) |
| S7 | `OPEN_ITEMS.md:999`(OPEN-484)・`:1047`(OPEN-532)の「Advancedのみ」 | 各OPENの文脈(KP一般化/Chunk TTS)でPart 2文法限定ではない可能性 | 要照合のうえ該当時のみ履歴化(委任_02で個別確認。Part 2文法に関する記述でなければ**維持**) |
| S8 | `docs/research/PART2-GRAMMAR-PRODUCTION-WIRING-01/DESIGN_02.md:5,77` | 適用レベル=Adv | **履歴化**(設計履歴。新DESIGN_01が現行) |
| S9 | `docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/OPERATIONS_01.md:133` | 「Standard(a2)ページには出ません(Advancedのみ)」 | **更新**(運用手順: Std文法HRの操作・Stdページに出る) |
| S10 | `docs/pm/RESULT_PACKET_YPL9.md:18` | 実走事実の記述 | **維持**(一時ファイル・履歴) |
| S11 | `docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/DESIGN_02.md` §10-1/付録3 | 「文法解説はユーザー未閲覧のStep B確定後生成(`stepB_generated_frozen`)」前提 | **更新**(事前生成→`form_displayed`が正規経路。`stepB_generated_frozen`は旧run互換の残置経路へ降格)。UDR-FORM-1は今回のユーザー決定で解消 |
| S12 | `docs/pm/USER_DECISION_REGISTER_01.md:489`(UDR-FORM-1) | 「フォーム『文法名+解説全文・最大2』と現行Part 2『英文1つ選択→解説後生成・最大1』のどちらに揃えるか」 | **解消**(2026-10-27ユーザー決定: 事前生成+最大2件を正式採用。Fable推奨(a)と一致) |

### 1-B. コード条件(Advanced限定の実体)
| # | 場所 | 条件 | 判定 |
|---|---|---|---|
| C1 | `er120_part2_grammar_production_01.py:42` `LEVEL="Advanced"` と使用箇所(:759/:986→現:747-768,:968-1010,:1128,:1134,:1147) | 候補doc・確定record・結果の`level`固定 | **更新**: `level`を引数化(`"b1b"`/`"a2"`、記録値は`Advanced`/`Standard`)。既存Adv成果物の記録値は不変 |
| C2 | 同`STEPA_PROMPT`:55(「Advancedレベル」「- レベル: Advanced」固定語)・`STEPB_PROMPT`:118/例示 | Prompt本文のAdv語 | **維持**(承認済みPrompt・sha固定。**Std本文にも同一Promptを無変更で適用**。DESIGN_01 §6 D-a) |
| C3 | `er119_grammar_review_01.py:24` `LEVEL_KEY="b1b"`、`:110` `pending_summary(level="Advanced")`、`:128` `article_key.level`、`:364` 依頼書題「(Advanced)」、`:411` `discover_dirs` | 文法HRのlevel固定 | **更新**(level引数化。共有NG registryのlevelキー=`a2`/`b1b`で別管理) |
| C4 | `er120_part2_wiring_01.py:26-27` `CAND_STAGE="part2_cand_b1b"`/`FINAL_STAGE="part2_b1b"`、`:237` `public_study_html`の`<audio_dir>/b1b` | stage名・公開ページ入力のb1b固定 | **更新**(level別stage名。`b1b`名は不変で互換、`a2`を追加) |
| C5 | `er128_kp_confirmed_content_01.py:848` `grammar_state` `level=...or "b1b"`、`:1253-1268` `_write_grammar_sidecar`の`gr.discover_dirs(run)[0]`、凍結`load_frozen_grammar`:862(単一`candidate_id`) | KCP文法保護のlevel/件数前提 | **更新**(KCP実装側。level別study_dir・凍結の複数item化。KCP担当と接続。IMPL_PLAN F-6) |
| C6 | X: `er019_family_x_audio_production_runner_01.py:760`(`level == "b1b"`の候補抽出)・`:3525`(`--stage study_text`の`"b1b" in levels`)・`:3548`(`parser.error` Adv限定)・`:3585`(入口検査`"b1b" in levels`)・`:715-717`(`_part2_failed_markers` b1bのみ)・`:3649-3664`(player Part 2連結`if "b1b" in levels`)・`:3022`(`build_player_html`: study_htmlをAdv節直後のみ)・`:628-631`コメント | 全てAdv限定 | **更新/撤去**(Stdの条件分岐を追加。`parser.error`は`--stage study_text --level a2`許容へ更新。コメントは更新) |
| C7 | Y: `er121_family_y_runner_01.py:34-48,319`(stage/unit名b1bのみ)・`:583-650`(`stage_kp`: 文法は1回だけ)・`:790-905`(`_part2_dir`/`_part2_inputs` b1b本文)・`:1016`(`tts_b1b`のみ入口検査)・`:1113`(`if lvd["id"] == "advanced"`)・`:925-947`(`_verify_part2_outputs`: Part 2==1個) | Adv限定 | **更新**(level別。入口検査は`tts_a2`にも) |
| C8 | Z: `er026_family_z_fiction_production_runner_01.py:1554,1562-1566`(`_part2_dir`/`_part2_inputs` b1b)・`:2307`(`load_level_inputs`はb1bのみ`_assert_part2_final`)・`:1685-1710`(`_verify_part2_outputs`==1個/`ON_STANDARD_PAGE`)・`:2419`; `er063_family_z_audio_01.py:2588`(`label == "Advanced"`); `er062_family_z_writer_01.py:64-72`(DEPENDENTS/ALL_STAGESにb1bのみ) | Adv限定 | **更新**(`std_adjust → part2_cand_a2 → part2_expl_a2 → part2_a2`を追加) |
| C9 | 表示条件の**逆向き検証**(Stdに載ったらSTOP): Y `FAMILY_Y_PART2_ON_STANDARD_PAGE`(:945)、Z `FAMILY_Z_PART2_ON_STANDARD_PAGE`(:1708) | 旧仕様の防御検査 | **撤去し置換**: 「各levelの文法ブロックは**自levelの節にだけ**ある」検査(`PART2_BLOCK_IN_WRONG_LEVEL_SECTION`)へ。Z開発確認用`standard.html/advanced.html`に文法/Part 1が載っていないこと(従来どおり)は**維持** |
| C10 | `er119_kp_human_review_01.py:525` 「vocab(単語解説5件)はAdvanced(b1b)のみ」 | **Part 1の単語解説**の制約(文法ではない) | **維持** |

## 2. ユーザー§6-2「Standardで文法候補の生成やHuman Reviewを実行しない旧経路」
- 上記C6-C8のとおり、候補抽出(X:760 / Y:`_part2_cand_step` 1回 / Z:`_part2_cand_step` 1回)はb1b本文のみ。`ensure_grammar_review`のreviewファイル(`grammar_candidates.json`/`grammar_human_review.json`)もlevel別に持たない(`study_dir`が1つ)。**更新**: levelごとに`study_dir`を持つ(`<out>/a2/study_text`=Std新設。Adv既存path不変)。
- 統合依頼書`write_unified_request`(`er119_kp_wiring_01.py:102`)のpending要素は`kind=grammar`にlevel表示が無く「文法(Part 2)」1項目(:113)。**更新**(level別項目)。`pending_banner`(同:130,138)も同様。
- CLI `er119_kp_human_review_cli_01.py` `grammar-show`/`grammar-select`(:14-16,:101-164)は`--level`無し(`discover_dirs`先頭)。**更新**(`--level`追加。未指定でlevelが複数ある場合は拒否)。

## 3. ユーザー§6-3「文法解説を選定後に生成する旧処理」
| # | 場所 | 内容 | 判定 |
|---|---|---|---|
| P1 | `er120_part2_grammar_production_01.py:1163` `run_part2`(選定後に`generate_explanation`) | 選定1件にだけStep B | **更新**: 解説は`pregen_stage`で全候補へ先に生成。`run_part2`は**生成しない**(事前生成物を参照。無ければfail-closed。旧run互換のみ`legacy_postselect`) |
| P2 | `er120_part2_wiring_01.py:111` `finalize_stage`(Step B 0/1 call)・各runnerの`run_part2_final_x`(X:674)/`_part2_final_step`(Y:848,Z:1622) | Part 1後のStep B | **更新**: 呼出元は残すが内部は**LLM 0 call**(確定済み事前生成/凍結からresult組立)。stage名`part2_b1b`は互換のため維持 |
| P3 | `explain_signature`(er120:1105)に`ref_ja`を含む | 解説の来歴にPart 1 T1訳(ref_ja)を使う | **更新**: 事前生成は`ref_ja=None`(選定前にPart 1訳が無い)。signatureは`ref_ja=None`固定のkeyに。`ref_ja`不一致はKCP `pool_ref_ja_issue`(ISSUE)が担う(実測重複0/28、稀) |
| P4 | `CURRENT_SPEC`/OPERATIONS_01「確定後にStep B」の運用記述 | 旧順序 | **更新** |

## 4. ユーザー§6-4「ユーザー確定後に英語・日本語訳・解説が再生成・上書きされる経路」(文法分)
| # | 場所 | 経路 | 判定 |
|---|---|---|---|
| R1 | 旧`finalize_stage`の`cached_result`不一致時の再Step B(`run_part2`内、`explain_signature`不一致) | 確定後でも`ref_ja`/モデル等の変化で解説が再生成され得る | KCP M6で確定済みはfrozen(`result_from_frozen`)になり是正済み(**維持**)。事前生成方式では「確定=事前生成物のsha固定」で同等以上 |
| R2 | `--regenerate-stage part2_cand_b1b`・reextract・reselect・omit・ng | 確定後の再抽出/別候補 | KCP `guard_grammar`でrevoke必須(**維持**。Std levelにも同じguardを適用: IMPL F-6) |
| R3 | 本文変更(Local Rewrite/ER-020/STALE再生成) | 確定文法の退避・再生成 | KCP M8で逐語span残存なら再バインド、残らなければISSUE(**維持**。Stdにも適用) |
| R4 | 事前生成物の再生成(`--regenerate-stage part2_expl_<lv>`、新設) | **新規経路** | 新設: 確定済み(confirmed_grammar/frozenあり)は`guard_grammar`で拒否。未確定でも既存の`explain_signature`一致は再利用(API 0) |
| R5 | KCP `cmd_from_form`(er128:1244)がform記載の`explanation_full`/`title`を**候補doc・事前生成と照合せず**sidecarに書く | 悪意なき不一致(フォーム側データと実run)で任意文が確定され得る | **更新**(照合追加: id∈候補、title==construct_ja、explanation_full==事前生成物、件数≤2。不一致はISSUE) |

## 5. ユーザー§6-5「Family間でフォーム連携・文法公開処理が異なる部分」
| # | 差 | 内容 | 判定 |
|---|---|---|---|
| F1 | 公開ページbuilder | Y=共有`ya.render_y_page`(level別`study_html`)・Z=共有`a63.build_pages`(level別)・**X=記事別個別script+`build_player_html`(Adv節直後固定)** | **更新**: 共通関数`er120_part2_wiring_01.public_study_html(audio_dir, level=...)`/`study_html_for_level`に統一し、X `build_player_html`にStd節の文法ブロックを追加。Xの記事別page scriptは共通関数呼出に揃える(IMPL F-7) |
| F2 | study dir | X=`<out>/<lv>/study_text`、Y/Z=`<out>/study_text`(フラット) | **更新**: `study_dir_for(family, out_dir, level)`の単一関数。Adv既存pathは不変、Std=`<out>/a2/study_text`(X既存規約に統一) |
| F3 | 来歴 | Y/Z=provenance ledger+`_stage_precheck`、X=無し | **維持**(Family固有のledgerはadapter側。核は共通) |
| F4 | 入力本文 | X=`article.md`(`paragraphs_from_article_md`)、Y=`ys.canonical_body`、Z=`canonical_article_text`+`topic_title` | **維持**(adapter。levelを引数化するだけ) |
| F5 | フォーム連携(form export) | `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`は`grammar`を引数で受けるが`main()`は未接続(常に空・「要生成」注記) | **更新**(DESIGN_01 §3-(c): `form_grammar_items(study_dir)`を提供しexporterへ接続。**フォーム側の担当委任と接続契約を共有**) |
| F6 | Z開発確認用`standard.html`/`advanced.html` | 文法/Part 1を載せない運用 | **維持**(index.htmlのみが公開対象) |

## 6. ユーザー§6-6「旧仕様を参照するretry／fallback／Validator／テスト」
| # | 場所 | 内容 | 判定 |
|---|---|---|---|
| T1 | `er120_part2_grammar_production_01_test_01.py:593` | `m.LEVEL == "Advanced"` assert | **更新**(level引数化後は`LEVELS`定数/既定値のassertへ。Prompt byte一致testは**維持**) |
| T2 | `er120_part2_wiring_integration_test_01.py:131,153-157,297` | `load_level_inputs(ctx,"a2")`は対象外、`assertNotIn("Grammar & Sentence Structure", std)`、`gp < Standard節` | **更新**(Std文法あり前提へ反転。「Stdの節にだけStdブロック」へ) |
| T3 | `er119_grammar_review_test_01.py:439` `test_public_builder_and_standard_never_call_part2` | StdからPart 2描画を呼ばない | **更新**(共通builder1つを両levelが呼ぶ、へ。「builder1つ」の趣旨は**維持**) |
| T4 | `er121_family_y_runner_01_test_01.py:585,647` | KP(b1b/a2)と文法が1待機にまとまる(文法1件)/`assertNotIn(mk, std_part, "Standardの節に学習テキストが出ている")` | **更新**(文法pendingがlevel別2件。Std節に出るのは文法ブロックのみ、Part 1(Vocabulary)は出ない=`mk`をPart 1マーカーに限定) |
| T5 | `er003_kp_general_explanation_01_runner_integration_test_01.py:212,255-264,291,307,572` | Part 1のAdv限定assert(`standard.html`に`class='study'`が無い等) | **維持**(Part 1は対象外)。ただしStd節に文法`class='study'`が出る箇所は個別更新 |
| T6 | `er119_z_wiring_test_01.py:84` | pending(level)=["a2","b1b"]、文法除く | **更新**(文法pendingも両level) |
| T7 | `er128_kp_confirmed_content_02b_test_01.py`(Part 2凍結M6) | 単一`candidate_id`前提 | **更新**(複数item凍結) |
| T8 | `er119_isolation_test_01.py:59` `assertNotIn("KIND_GRAMMAR", ...)` | A/B/C・共有moduleが文法kindを持ち込まない隔離 | **維持**(重要。今回の変更でA/B/Cに影響を出さない) |
| T9 | 旧retry/fallback | `_run_llm`の技術retry1回・モデル不一致STOP・fallbackなし、`MAX_RESELECT=2`/`MAX_REEXTRACT=1`、exhausted時自動ZERO禁止 | **維持**(事前生成のStep Bも同じ`_run_llm`を通す。回避しない) |
| T10 | Validator `require_fresh_part2`(er120:1272)・`_expected_outcome`:1236・`verify_selection_matches_outputs`:1333 | 単一選定を前提 | **更新**(複数item。fail-closedの厳しさは維持・AND追加のみ) |

## 7. 撤去・残置の最終方針(Dangling Reference対策)
- **コード上の撤去**: C9(`*_ON_STANDARD_PAGE`)→置換、`run_part2`内の選定後Step B(P1)、runnerの`parser.error` Adv限定(C6)。撤去後Grep: `ON_STANDARD_PAGE`/`Standardには出さ`/`Advanced=b1bのみ`/`適用レベル=Advancedのみ`が**現行コード/現行仕様**に残らないこと(履歴文書のみ許容)。
- **履歴化**: S4,S5,S8,S10(注記のみ。本文不変)。現行参照されないよう、CURRENT_SPECの該当節に「2026-10-27 GRAMMAR-PREGEN-ALL-LEVELS-01: 本記述のAdvanced限定は旧AI設計判断(ユーザー原文に無し)であり、ユーザー決定で置換」を1行追記(履歴の削除はしない)。
- **維持**: Part 1のAdv限定(S3,C10,T5,T8)。範囲外であることを`DESIGN_01`§7 Q3で明記し、Stdへ広げる提案はしない(新仕様候補。Fableへ報告のみ)。
