## 管理ID

SLOT-23-CONSUMER-DESIGN-01 委任_04E(E班: Family Zの配線。設計正本=`DESIGN_03.md`/`CONTRACT_03.md`/`IMPL_PLAN_03.md`(commit 71e39f4df)、A班成果=commit 22f3a09ef(`er_learning_highlight_01.py`/`er128_kp_highlight_01.py`/`er_user_listening_page_common_01.script_block(highlights=)`、`RESULT_PACKET_S23A.md`(1)の呼出例。CONTRACT_03はC班がA班実装に合わせて更新中=A班実装の署名・class `lk-meaning`・原因コードが正)、B班=委任_04B進行中(`er003_kp_general_explanation_01.py` level化=`generate_for_kp_items(level=)`/`study_html_for_audio_dir(audio_dir, level=)`、`er128.display_spec_of(run, level)`=`IMPL_B_01.md`)。ユーザー正式決定=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`。API 0(testはmock)。並行Agent: B班(er003/er128/er119=**編集禁止**)、C班(er019系・CONTRACT_03=編集禁止)、D班(er121系=編集禁止)。KCP委任_04(Z run)は完了済み=Z系編集可。あなたの所有=`er063_family_z_audio_01.py`(`:2528,2557-2610`付近の`script_block`呼出・③訳リスト・凡例・CSS連結・`has_vocab_on_page`系)、`er026_family_z_fiction_production_runner_01.py`(`stage_pages`(`:2476`付近)・`stage_kp`のPart 1 stage(`kp_part1_b1b`/`kp_part1_ja_b1b`)のlevel化(`kp_part1_a2`/`kp_part1_ja_a2`新設、`ensure_stage`・DEPENDENTS整合)・`load_level_inputs`のfail-closed確認のlevel化・Validator・`page_verify`へのG3ハイライト検査・アダプタ)、`er062_family_z_writer_01.py`(DEPENDENTS/来歴台帳に新stage追加が必要な場合のみ)、Z test(`er026_*`/`er063_*`/`er062_*`該当・新規`er026_z_highlight_wiring_test_01.py`)、`docs/research/SLOT-23-CONSUMER-DESIGN-01/IMPL_E_01.md`、`..._DELEGATION_04E.md`(+check.json)、`docs/pm/RESULT_PACKET_S23E.md`(gitignore)。**マーク発行(`new_review`接続)はしない**(M14)。**実run・再ビルド・公開はしない**。pathspec付きcommit、`git push origin HEAD:main`。時間見込み約2.5h。

## Fable決定(反映)

- 表示範囲(DisplayUnit列)=Zページに表示されるクリップ台本すべて(公開順、Part別)。`article_text`=`canonical_article_text(...)`後の本文(候補生成に使った本文、`text_sha256`一致必須)。クリップ台本と本文の句読点・引用符差はA班の単調整列で吸収(A班のoffline toolは`segment_plan` clipsで代用=実ページのscriptと同文か確認し記録)。
- 表示有効化=`er128.display_spec_of`が真のrunのみ。マーク無し旧run=従来バイト同一(golden test: 既存run(例: `melos/run_p2_evidence_r3`)のpages出力が変更前後でバイト同一)。
- Std Part 1=①+②、Adv同型、配置=Part 1→Part 2(文法)。Validator: vocab対象levelではPart 1ブロックがちょうど1個(0個・2個はSTOP)・判断記録なし=STOP(M11)。`load_level_inputs`(a2)でも`kp_general_explanations.json`の存在とsignature一致をfail-closed確認(Advと同型)。
- Z lint(`er063:2639`)の禁止語(`英語:|日本語:|EN:|JA:`)を凡例・訳リストで使わない(A班の`meaning_list_html`/`legend_html`文言を確認)。
- B班APIが未着地の間はハイライト配線・Validator・page_verifyを先に進め、Part 1 level化配線は`git fetch`+`git log origin/main --grep "委任_04B"`で着地を10分間隔・最大90分待ってから実装(未着地なら当該部分を未実装と明記して報告)。
- Z固有: `--regenerate-stage kp_part1_a2`/`kp_part1_ja_a2`の明示再生成をAdvと同型で用意(DEPENDENTSへは追加しない=既存方針)。

## 実施事項

1. アダプタ+解決: `resolve_highlights(article_text, cands_doc, items, display_units)`→ISSUEならpages生成前にSTOP(原因コード付き)。NOTICEはauditへ。
2. 描画: `script_block(..., highlights=...)`、クリップ直下(または節末)に`meaning_list_html`、凡例1行、`HIGHLIGHT_CSS`連結(マーク無しrunは連結しない)。`⏸`(dev)と共存、public混入0。クリップをまたぐ語句は片ごとに同一`data-hl`。
3. Std Part 1: `stage_kp`の`kp_part1_<lv>`/`kp_part1_ja_<lv>`をlevel化、`stage_pages`でStd節に`study_html_for_audio_dir(level=)`(Part 1→Part 2順)。旧経路撤去(`SPEC_CONFLICT_02.md`のZ分、`er063:2592`コメント含む)。完了基準=Part 1系の`"b1b"`リテラルが既定引数以外0件(Grep結果を`IMPL_E_01.md`に)。
4. `page_verify`: 既存検査+`verify_highlights(level_section_html, expected)`+Part 1ちょうど1個(vocab level)+Part 2一致。
5. test: 新規配線test(mock run: ハイライトあり/なし、Std Part 1 1/0/2個、display_spec無しバイト同一、クリップ跨ぎ、`⏸`非混入、lint禁止語0)、既存`er026_*`/`er063_*`/`er062_*`回帰(既知の並列干渉dry-run検査は単体再実行で記録)。
6. commit: `SLOT-23-CONSUMER-DESIGN-01 委任_04E: Family Z配線(本文ハイライト・③訳リスト・Std Part 1 stage level化・Validator・page_verify G3、マーク発行未接続、API 0)`。Secret grep 0件。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: なし。

## 事前指定Read一覧

`DESIGN_03.md`(§B/§C/§D/§E Z節)、`CONTRACT_03.md`、`IMPL_PLAN_03.md`(E班)、`docs/pm/RESULT_PACKET_S23A.md`(1)(4)(5)、`er_learning_highlight_01.py`(公開関数docstring)、`er063_family_z_audio_01.py:2500-2660`、`er026_family_z_fiction_production_runner_01.py:2040-2120,2460-2560`、`er062_family_z_writer_01.py:60-75`、`SPEC_CONFLICT_02.md`(Z該当行)、`CURRENT_SPEC.md:2087-2089`。

## 報告

`RESULT_PACKET_S23E.md`: (0)T-0、(1)差分・配線点(file:line)、(2)golden・test結果、(3)旧経路撤去Grep、(4)B班API待ちの有無、(5)判断候補、(6)必須4行+「判定整合」、commit hash・raw URL。末尾5行要約。