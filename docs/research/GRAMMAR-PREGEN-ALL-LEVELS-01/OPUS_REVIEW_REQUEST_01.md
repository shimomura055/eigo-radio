# OPUS_REVIEW_REQUEST_01: 独立技術レビュー依頼(条件A=新しい構造・処理フローの設計)

管理ID: GRAMMAR-PREGEN-ALL-LEVELS-01 委任_01。対象設計: `DESIGN_01.md`(文法解説の事前生成・Std/Adv全6経路・最大2件採用)。根拠事実: `CURRENT_FLOW_01.md`・`ADV_ONLY_INVENTORY_01.md`。計画: `IMPL_PLAN_01.md`・`TEST_PLAN_01.md`・`EVIDENCE_PLAN_01.md`・`COST_ESTIMATE_01.md`。承認根拠(ユーザー正式決定、逐語): `docs/pm/delegation_log/2026-10-27_GRAMMAR-PREGEN-ALL-LEVELS-01_USER.md` §1,§3,§5,§6。
Opus台帳: 依頼は`docs/pm/OPUS_FINDINGS_LEDGER.md`へ条件A依頼(2026-10-27)として記録(Fable記入)。PM_GOVERNANCE 11-3(条件A)・11-5。

## レビューの前提(変更不可の制約)
- 承認済みの解説品質・文章量・学習内容(`STEPA_PROMPT`/`STEPB_PROMPT`のsha、`eligible7`、Trial-08 Tier規則、`TOP_N`)は**無変更**。レビューは「いつ・何件・どのlevelで生成/選定/確定/公開するか」の構造に限る。
- 範囲を狭める提案(Standardを対象から外す等)は不可(ユーザー§1)。技術的に困難な点は代替実装案で。
- 既存の安全装置(`_run_llm`の技術retry1回・モデル不一致STOP・fallbackなし、reselect/reextract上限、exhausted時の自動ZERO禁止、KCP G1〜G4/M6/M8、Human Review待機rc=4)は回避しない。

## 観点(各項に「採用/修正/不採用+理由」で回答してほしい)
1. **工程順変更の副作用**(設計§1,§3-(a)): 事前生成を「候補抽出直後・KP候補生成/待機の前」に置く位置は妥当か。失敗時にKP/support発注前に止まる(X scaffold・Y/Z `stage_kp`冒頭)ことで、資源無駄・再開コスト・RESTART_STORM等の副作用が増えないか。事前生成が候補全件(最大8)×直列で数分かかる点と、並列化(スレッド)の是非(`cl.logging_context`/budget guardのスレッド安全性)。Part 1(T1訳)より前に解説が確定的に作られることで、Part 1の訳との整合(`ref_ja`喪失)にどんな穴があるか(実測重複0/28、`pool_ref_ja_issue`のISSUE化で足りるか。逆方向=確定した文法の訳をPart 1のT1に再利用する案の要否)。
2. **Std本文への候補抽出の妥当性**(設計§3-(a),§6 D-a): Prompt無変更(「Advancedレベル」固定語のままStd本文を入力)の適用は、Trial-07/08の検証範囲(全てAdvanced本文)を外れる。偽陽性/過少抽出のリスクをどう評価するか。「Prompt無変更+実測報告」(推奨)で必要十分か、level差込(sha変更)が必須か(後者は別承認が要るため、必須と判断する場合はその根拠)。Std候補0件が常態化した場合の機能価値の扱い(ZERO固定文面をStd公開ページに出す是非、設計D-d)。
3. **事前生成とKCP M6凍結の整合**(設計§3-(e)): 事前生成物の`explanations_sha256`を`decision`に固定し、フォーム経路は`explanation_full==事前生成物`の照合→凍結v2(`items[]`、`source=form_displayed`)とする案。(a)v1凍結(単一`candidate_id`)との読取互換、(b)CLI経路(フォームなし)の凍結源(`hr_displayed`)の扱い、(c)確定済みitemの据え置き`input_sha`(Y/Z provenance)と`part2_expl_<lv>`の新stageの組合せで解消不能STOPが生じないか、(d)`cmd_from_form`でsidecar書込とreview `pick`適用を同一review_lock内でatomic化する案の妥当性と競合(KP selectとの順序)。
4. **重複生成・重複実行の防止**(設計§3-(b)): Step B呼出点を`pregen_stage`1か所に集約し、`run_part2`/`finalize_part2`からStep B生成を撤去、無ければ`Part2Stale`でfail-closed、旧runのみ`legacy_postselect`を許可する案で、(i)resume/再finalize/regenerateの各経路で二重課金が起きないか (ii)`legacy_postselect`が新経路の抜け穴(ユーザー未閲覧の解説が公開される)にならないか (iii)`--regenerate-stage part2_expl_<lv>`を未確定のみ許可する規則は十分か。
5. **2件採用の公開表示と選定モデル**(設計§2,§3-(a),§6 D-e/D-h): (i)`items[]`結果とv2 review/署名(v1署名式の保存で既存Adv確定を壊さない)の整合、(ii)表示順=本文出現順の妥当性、(iii)autoはTOP1のみ(既存承認条件)の維持、(iv)`select_from_candidates`の複数化に伴う`_expected_outcome`/`require_fresh_part2`のAND追加が既存fail-closedを弱めないか、(v)verdicts(SELECTED/NOT_SELECTED/NG)を「提示した全候補」に拡張する扱い。
6. **Family差の解消とadapter境界**(設計§3-(d)): 共通核に`level`引数を足し、X/Y/Zは入力本文・stage台帳・ページ差込のadapterのみにする分割は妥当か。特にXの公開ページが「記事別script+`build_player_html`」で共通builderを持たない点を`public_study_html(level=)`へ集約する案の実効性、Z `build_pages`の`study_html`をlevel別dictにするAPI変更(後方互換)、Y/Zの`*_ON_STANDARD_PAGE`検査を`*_WRONG_LEVEL_SECTION`へ置換する際に検査力が下がらないか。study dir規約(Adv既存path不変/Std=`<out>/a2/study_text`)の妥当性。
7. **費用**(設計§3-(g)・`COST_ESTIMATE_01.md`): 実測(Step B JPY0.05-0.11/call、候補数X約3.0/Y約2.3/Z約0.7、増分X約0.9/Y約0.8/Z約0.34 JPY/記事セット)の外挿は妥当か。n小・Std候補数未観測の不確実性に対し`PREGEN_MAX=8`とevidence内計測(<=8本)で足りるか。事前生成の費用を下げる余地(例: 上位K件のみ生成、未選択候補の遅延生成)と、それがユーザー要件(全候補の解説を見て採否を決める)に反しないか。
8. **evidence十分性**(`EVIDENCE_PLAN_01.md`): 方式A(copy-runで本文・音声再利用、3run x 両level=6経路、<=JPY40)でPRODUCTION_WIRED受入(ユーザー§8)に十分か。「正式初回Production」を方式Aで満たすとみなす是非と、方式B(新規記事E2E)を次の通常制作へ相乗りさせる運用の妥当性。不足する検証があれば指摘。
9. **旧仕様撤去・Dangling Reference**(`ADV_ONLY_INVENTORY_01.md`): 撤去/更新/履歴化/維持の判定に漏れ・誤りはないか。「Part 1のAdv限定は維持(今回の対象外)」の扱いと、Std学習ページがPart 2のみで構成される点の妥当性(ユーザー意図の確認事項はFableに残す)。
10. **A/B/C不変・隔離**: `er119_isolation_test_01`(文法kindを共有moduleへ持ち込まない)・新flagなし(承認済みProduction配線)・`protection_enabled()`の既定との整合に問題はないか。

## 事実として確認済み(再調査不要)
- Advanced限定の出所はユーザー原文(`2026-10-25_PART2-GRAMMAR-PRODUCTION-WIRING-01_USER.md`:90は「Standard／Advancedなど…」)ではなくAI設計判断(`PART2-GRAMMAR-PRODUCTION-WIRING-01/DESIGN_02.md:5,77`)。
- 共有ページ構造(`er_user_listening_page_common_01.py:51-70`)はlevel別`study_html`を既に受ける。`compose_study_html`は`part1_html`空でCSSを含む(`er120:1421`)。Y `stage_pages`は`if lvd["id"] == "advanced"`(:1113)、Z `er063:2588`は`label == "Advanced"`の条件のみがAdv限定。
- 現行`_write_grammar_sidecar`(er128:1253)は`gr.discover_dirs(run)[0]`でlevelを区別せず、`cmd_from_form`は文法itemを候補doc/事前生成と照合しない。凍結`load_frozen_grammar`(:862)は単一`candidate_id`。
- 候補文とPart 1引用英文の重なり: 18 run・28候補で0件。Step B実測JPY0.05-0.11/call。

## 期待する回答形式
各観点の採否、重大/中/軽の所見、実装時の必須修正、追加すべきtest。Fableは照合のうえ11-3に従い次工程へ進む(Opusレビュー自体はユーザー承認Gateではない。Production採用は人間ユーザーのみ)。
