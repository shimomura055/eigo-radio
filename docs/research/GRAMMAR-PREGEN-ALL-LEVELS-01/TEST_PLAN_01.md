# TEST_PLAN_01 テスト計画(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01。API 0のmock中心。新規は`er120_part2_pregen_test_01.py`ほか)

mock基盤: `er120_part2_mock_01.py`(`mock_extract_call_fn`/`mock_explain_call_fn`)を再利用し、Step B呼出回数を数えるspyを追加。実API呼出はevidence(EVIDENCE_PLAN_01)のみ。不整合な出力を期待値としてassertするtestは書かない。

## 1. 新規/更新test(期待値は「承認済み仕様」に対して書く)

| ID | 内容 | 種別 |
|---|---|---|
| T1 | **Trial-08回帰**: Trial-07/08全29標本の選定結果が不変。`candidates[0]`==`select_tiered`の1件(AI推奨)。Prompt byte一致・sha定数不変(`STEPA/STEPB_PROMPT_SHA256`)。Std level指定でもPrompt文字列が同一 | 維持(既存test拡張) |
| T2 | level引数化: Adv出力が従来とバイト同一(候補doc/review/result v1相当の既存fixture回帰)、Std指定で`level=="Standard"`、NG registryがlevel別、study_dir path | 新規 |
| T3 | **重複防止**: first run `generate_explanation`呼出==候補数(<=8)、resume 0、finalize 0、`--regenerate-stage part2_<lv>` 0、`part2_expl_<lv>`は明示時のみN、確定後の`part2_expl`/`part2_cand`再生成は`guard_grammar`で拒否(0 call)。旧run互換(`legacy_postselect`)で新規Step B 0 | 新規 |
| T4 | 事前生成: 全候補生成/signature一致skip/途中失敗で成功分保持→STOP(`part2_failed.json` stage=`part2_expl`)→再開で未生成分のみ/`PREGEN_MAX`超過を`skipped_over_cap`に記録/モデル不一致STOP/予算guard超過STOP/構造NG技術retry1回後STOP(fallbackなし) | 新規 |
| T5 | 選定v2: pick 0/1/2件、3件・同一id重複・候補外id・stale sha拒否、reason必須規則(pick 2件・top2・omit等は既存規則に準拠)、auto=TOP1のみ、`NO_CANDIDATE_UNREVIEWED`、署名v1/v2の互換(既存Adv確定の署名が不変)・決定論(id順非依存) | 更新+新規 |
| T6 | 結果v2/Validator: v1→items正規化、2件でrequire_fresh OK、**改ざん検出**(explanation_md/sentence/candidate_id/順序/余分item/欠落item/`explanations_sha256`不一致/ZEROと確定の矛盾)がPart2Stale、事前生成物とresultの解説一致(AND追加)、凍結あり時の`frozen:<sha>`判定 | 更新+新規 |
| T7 | 描画: 1件=従来golden(バイト同一)、2件=本文出現順・`<h3>`1つ・item 2つ、ZEROは固定文面、`PAGE_FORBIDDEN_RE`、HTMLエスケープ、md==render_markdown | 更新 |
| T8 | 文法HR: 依頼書に解説全文・題にlevel、`grammar-show/select --level`、`--ids`、level未指定で複数levelある時は拒否、統合依頼書/bannerがlevel別2項目、`declare-absent`が両levelに効く(round/sha一致のみ) | 更新 |
| T9 | Family runner(mock): X/Y/Z各々 (i)両levelの候補/pregenがKP候補生成前、(ii)Std+Adv+KPが1回のrc=4、(iii)pick後に両levelのfinalize OK、(iv)ページ: 各levelの自節に文法ブロック1個ずつ・Part 1はAdvのみ・順序(Adv: Part 1→Part 2)、(v)**負例**: ブロックを他levelの節へ移す/欠落/重複→`*_WRONG_LEVEL_SECTION`でSTOP、(vi)Z開発確認用`standard.html`/`advanced.html`に文法/Part 1が無い | 更新(旧`ON_STANDARD_PAGE`系を反転)+新規 |
| T10 | KCP(F-6): from-formの文法照合(id/title/body/件数>2/重複/候補外→ISSUE)、sidecarが対象level dirへ、文法review `pick`のatomic適用、凍結v2(2 item)、`guard_grammar`が確定後の`part2_cand_<lv>`/`part2_expl_<lv>`/reextract/reselect/omit/ng/unngを拒否(Std含む)、本文変更で各itemの逐語残存→再バインド(API 0)/1つでも欠落→ISSUE、`pool_ref_ja_issue`、凍結v1読取互換 | 更新+新規 |
| T11 | 隔離: `er119_isolation_test_01`(A/B/C・共有moduleに`KIND_GRAMMAR`等を持ち込まない)PASS維持、Production flag新設なし、既定=Human Review待機(rc=4)維持、不在宣言なしで自動確定しない | 維持 |
| T12 | retry/fallback/resume/regenerate行列(DESIGN_01 §4)の各行をmockで再現し、確定itemのsha/文字列が不変であること | 新規 |
| T13 | フォーム契約: `form_grammar_items`→`export_form_data_01.convert(grammar=)`→`form_logic.js`の`grammarRecord`(`body`)→payload `explanation_full`が事前生成物と一致。`grammar_status`3値(`candidates_available`/`no_candidates_found`/`no_candidates_ungenerated`)。`form1_selection_form_v3_test_01.py`の「正式文法候補なし」前提testは「候補あり/なし/未生成」の3系へ更新(UI不変) | 更新(FORM担当と共有) |
| T14 | 費用記録: pregenのaudit(`total_cost_jpy`)がrun cost集計に載る・Step B総数が実call数と一致 | 新規 |
| T15 | Dangling Grep test: ADV_ONLY_INVENTORY §7の撤去語が現行コードに0件(履歴文書を除外するallowlist付き) | 新規 |

## 2. 回帰(必ず実行・PASS確認)
`er120_part2_grammar_production_01_test_01.py`、`er120_part2_wiring_integration_test_01.py`、`er119_grammar_review_test_01.py`、`er119_z_wiring_test_01.py`、`er119_isolation_test_01.py`、`er121_family_y_runner_01_test_01.py`、`er026_family_z_fiction_production_runner_01_test.py`、`er019_family_x_audio_production_runner_01_test_01.py`、`er003_kp_general_explanation_01_runner_integration_test_01.py`(Part 1は不変)、`er128_kp_confirmed_content_test_01.py`/`_02b_test_01.py`、`er063_family_z_audio_01_test_01.py`、`form1_selection_form_v3_test_01.py`、`er_user_listening_page_common`系、KP 7+5関連(`er119_kp_*`)。変更前に基準結果(PASS数)を取り、変更後に同数以上PASSであること。更新が必要なtest(ADV_ONLY_INVENTORY §6 T1-T7)は**期待値を新仕様に更新**(旧Adv限定をassertするtestを残さない)。

## 3. 受入基準(テスト層)
- 上記全PASS、旧Adv限定assertの残存0、Step B総数のspy test PASS、v1成果物の読取互換PASS、既存Adv run(`er121_output/...redelivery_fee/run_01`等)のpages再生成がバイト同一。
