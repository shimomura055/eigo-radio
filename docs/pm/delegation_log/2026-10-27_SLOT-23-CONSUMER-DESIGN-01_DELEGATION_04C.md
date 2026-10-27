## 管理ID

SLOT-23-CONSUMER-DESIGN-01 委任_04C(C班: Family Xの配線。設計正本=`DESIGN_03.md`/`CONTRACT_03.md`/`IMPL_PLAN_03.md`(commit 71e39f4df)、A班成果=commit 22f3a09ef(`er_learning_highlight_01.py`/`er128_kp_highlight_01.py`/`er_user_listening_page_common_01.script_block(highlights=)`、`RESULT_PACKET_S23A.md`(1)の呼出例、`OFFLINE_RESOLVE_01.md`)、B班=委任_04B進行中(`er003_kp_general_explanation_01.py` level化=`generate_for_kp_items(level=)`/`study_html_for_audio_dir(audio_dir, level=)`、`er128.display_spec_of(run, level)`、`er119`両level vocab=`IMPL_B_01.md`に公開API予定)。ユーザー正式決定=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`。API 0(testはmock)。並行Agent: B班(上記3ファイル=**編集禁止**)、D班(er121系=編集禁止)、KCP委任_04(Z run実行中=Z系編集禁止・run dir不可)。あなたの所有=`er019_family_x_audio_production_runner_01.py`(player `_build_level_table`付近・study_text stage・失敗marker/案内のlevel化・Validator)、新規標準builder `er019_family_x_listening_page_01.py`(`tools/build_aif3_listening_page_01.py`を昇格・AI島固有文言除去)、`er019_nws2_final_page_01.py`(正式入口=`CURRENT_SPEC.md:2095`の`study_html_for_audio_dir`呼出のlevel化+`display_spec`検出STOPの共通module import)、新規共通module `er019_x_page_guard_01.py`(`display_spec`付きrunを旧per-article script(`er019_*page*.py` 14本)が処理したらSTOP。各scriptへは1行importのみ追加)、`audio_review_player`のCSS(`PLAYER_STANDARD_CSS`にHIGHLIGHT_CSS連結)、X test(`er019_*test*`該当・新規`er019_x_highlight_wiring_test_01.py`)、`CONTRACT_03.md`(**A班実装に合わせて更新**: 署名`resolve_highlights(article_text, cands_doc, items, display_units, *, units, lr_rebound)`、class `lk-meaning`、原因コード=A班名称(alias表)、ISSUEは`result["issues"]`、`verify_highlights(level_section_html, expected)`、跨ぎ片の`surface`規約)、`docs/research/SLOT-23-CONSUMER-DESIGN-01/IMPL_C_01.md`、`..._DELEGATION_04C.md`(+check.json)、`docs/pm/RESULT_PACKET_S23C.md`(gitignore)。**マーク発行(`new_review`接続)はしない**(M14)。**AI島の実生成・再ビルド・公開はしない**(HR承認後の別委任)。pathspec付きcommit、`git push origin HEAD:main`。時間見込み約3h。

## Fable決定(反映)

- 表示範囲(DisplayUnit列)=ページに表示される本文単位すべて(Xは段落+「In one line」節も表示されるなら含める。A班の残ISSUE 1件=`year over year`はこれで解消。分類B)。
- 表示有効化=`er128.display_spec_of`(flag非経由)が真のrunのみ。マーク無し旧run=従来バイト同一(golden test: 既存run 1件のplayer/公開ページ出力が変更前後でバイト同一)。
- Std Part 1=①+②、Adv同型、配置=Part 1→Part 2(文法)。Validator: vocab対象levelではPart 1ブロックがちょうど1個(0個・2個はSTOP)、判断記録なし=STOP(M11)。
- B班APIが未着地の間はハイライト配線・builder・guard・Validator・CONTRACT更新を先に進め、Part 1 level化配線は`git fetch`+`git log origin/main --grep "委任_04B"`で着地を10分間隔・最大90分待ってから実装(未着地なら当該部分を未実装と明記して報告)。

## 実施事項

1. アダプタ: X=`article_text`は`{source_dir}/{lv}/article.md`(候補生成に使った本文、`text_sha256`一致必須)、`cands_doc`=`<run>/<lv>/key_phrases/kp_candidates.json`、items=`er_learning_highlight_01.items_from_record(確定レコード)`、DisplayUnits=player/公開ページの段落単位(+In one line)。`resolve_highlights`→ISSUEならページ生成前にSTOP(原因コード付き)。
2. player(`_build_level_table`付近): ハイライトがあるrunのみ`render_script_html`(escape)に切替(M13、無い場合は従来の未escape出力を維持=バイト同一)、③訳リスト、凡例、CSS連結。`audience=dev`の`⏸`と共存。
3. 標準builder `er019_family_x_listening_page_01.py`: Std/Adv節、Part 1(両level、`study_html_for_audio_dir(level=)`)、Part 2、ハイライト、`check_page(public)`+`verify_highlights`+Part 2の4者一致+Part 1ちょうど1個(vocab level)をPASSしないと出力しない。AI島固有文言(SLUG固定・「後続反映予定」)を除去し引数化。`tools/build_aif3_listening_page_01.py`は昇格後、標準builderへの薄いwrapperか廃止(`docs/research/AI-ISLAND-FORM-PRODUCTION-01`の文書に注記)。
4. 旧経路撤去(R4/S一覧のX分): `er019`の失敗marker(`:434-436`)、案内コマンド`--level b1b`固定(`:439-443`)、b1b固定パス(`:461-524,573-624`)、`study_text` stageのb1b限定(`:603-614`)をlevel化。完了基準=Part 1系関数内の`"b1b"`リテラルが既定引数以外0件(Grep結果を`IMPL_C_01.md`に)。
5. test: 新規配線test(mock run: ハイライトあり/なし、Std Part 1 1個/0個/2個、display_spec無しバイト同一、guardのSTOP、In one line含む解決)、既存`er019_*`回帰(既知失敗OPEN-543は記録)。
6. commit: `SLOT-23-CONSUMER-DESIGN-01 委任_04C: Family X配線(本文ハイライト・③訳リスト・Std Part 1 level化・標準公開builder・旧per-article script guard・Validator、マーク発行未接続、API 0)`。Secret grep 0件。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: なし。

## 事前指定Read一覧

`DESIGN_03.md`(§B/§C/§D/§E X節)、`CONTRACT_03.md`、`IMPL_PLAN_03.md`(C班)、`docs/pm/RESULT_PACKET_S23A.md`(1)(4)、`er_learning_highlight_01.py`(公開関数docstring)、`er019_family_x_audio_production_runner_01.py:420-640,2930-3080`、`tools/build_aif3_listening_page_01.py`、`er019_nws2_final_page_01.py:1-40`、`CURRENT_SPEC.md:2095`。

## 報告

`RESULT_PACKET_S23C.md`: (0)T-0、(1)差分・配線点(file:line)、(2)golden(バイト同一)・test結果、(3)旧経路撤去Grep、(4)B班API待ちの有無、(5)判断候補、(6)必須4行+「判定整合」、commit hash・raw URL。末尾5行要約。