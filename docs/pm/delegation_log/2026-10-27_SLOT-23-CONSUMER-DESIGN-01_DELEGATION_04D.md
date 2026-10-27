## 管理ID

SLOT-23-CONSUMER-DESIGN-01 委任_04D(D班: Family Yの配線。設計正本=`DESIGN_03.md`/`CONTRACT_03.md`/`IMPL_PLAN_03.md`(commit 71e39f4df)、A班成果=commit 22f3a09ef(`er_learning_highlight_01.py`/`er128_kp_highlight_01.py`/`er_user_listening_page_common_01.script_block(highlights=)`、`RESULT_PACKET_S23A.md`(1)の呼出例)、B班=委任_04B進行中(`er003_kp_general_explanation_01.py` level化=`generate_for_kp_items(level=)`/`study_html_for_audio_dir(audio_dir, level=)`、`er128.display_spec_of(run, level)`=`IMPL_B_01.md`に公開API予定)。ユーザー正式決定=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`。API 0(testはmock)。並行Agent: B班(er003/er128/er119=**編集禁止**)、C班(er019系・`CONTRACT_03.md`=編集禁止。CONTRACT_03はC班がA班実装に合わせて更新中=A班実装の署名・class `lk-meaning`・原因コードが正)、KCP委任_04(Z run実行中=Z系編集禁止)。あなたの所有=`er121_family_y_audio_01.py`(`:1467`付近の`script_block`呼出・③訳リスト・凡例・CSS連結)、`er121_family_y_runner_01.py`(`stage_pages`(`:1192`付近)・Validator(`:1021-1026`)・Std Part 1生成stageのlevel化・`page_verify`へのG3ハイライト検査追加・アダプタ)、`er121_family_y_structure_01.py`(必要時のみ)、Y test(`er121_*test*`該当・新規`er121_y_highlight_wiring_test_01.py`)、`docs/research/SLOT-23-CONSUMER-DESIGN-01/IMPL_D_01.md`、`..._DELEGATION_04D.md`(+check.json)、`docs/pm/RESULT_PACKET_S23D.md`(gitignore)。**マーク発行(`new_review`接続)はしない**(M14)。**実run・再ビルド・公開はしない**。pathspec付きcommit、`git push origin HEAD:main`。時間見込み約2.5h。

## Fable決定(反映)

- 表示範囲(DisplayUnit列)=Yページに表示される台本ブロックすべて(公開順)。`article_text`=Y候補生成に使った本文(`text_sha256`一致必須。Yの候補生成入力を特定して記録)。
- 表示有効化=`er128.display_spec_of`が真のrunのみ。マーク無し旧run(例: `_03`再配達)=従来バイト同一(golden test: `run_style_fix_01`等の既存runでpages出力が変更前後でバイト同一)。
- Std Part 1=①+②、Adv同型、配置=Part 1→Part 2(文法)。Validator(`:1021-1026`「StandardにPart 1があるとSTOP」)は**撤去**し、vocab対象levelではPart 1ブロックがちょうど1個(0個・2個はSTOP)・判断記録なし=STOPへ置換(M11)。
- B班APIが未着地の間はハイライト配線・Validator・page_verifyを先に進め、Part 1 level化配線は`git fetch`+`git log origin/main --grep "委任_04B"`で着地を10分間隔・最大90分待ってから実装(未着地なら当該部分を未実装と明記して報告)。
- Y Voice説明文(`PAGE_NOTICE_JA`)・`audience=dev|public`マーカー・Style継承(OPEN-537 WIRED)の挙動は変更しない(回帰testで担保)。

## 実施事項

1. アダプタ+解決: `resolve_highlights(article_text, cands_doc, items, display_units)`→ISSUEならpages生成前にSTOP(原因コード付き)。NOTICEはauditへ記録。
2. 描画: `script_block(..., highlights=hl.highlights_for_text(...))`、各ブロック直下(または節末)に`meaning_list_html`、凡例1行、`HIGHLIGHT_CSS`連結(マーク無しrunは連結しない=バイト同一)。`⏸`(dev)と共存、public混入0。
3. Std Part 1: Y runnerのPart 1生成stage(Adv用の既存stage名・パス・poolがb1b限定=`SPEC_CONFLICT_02.md`のY分)をlevel化、`study_html_for_audio_dir(level=)`でStd節へ描画(Part 1→Part 2順)。旧経路撤去の完了基準=Part 1系の`"b1b"`リテラルが既定引数以外0件(Grep結果を`IMPL_D_01.md`に)。
4. `page_verify`: 既存検査+`verify_highlights(level_section_html, expected)`+Part 1ちょうど1個(vocab level)+Part 2一致。
5. test: 新規配線test(mock run: ハイライトあり/なし、Std Part 1 1/0/2個、display_spec無しバイト同一、`⏸`非混入)、既存`er121_*`回帰(既知失敗=`StudyTextWiring`旧2件test(OPEN-543)は本委任で新仕様(≤1件)へ更新してよい。他は記録)。
6. commit: `SLOT-23-CONSUMER-DESIGN-01 委任_04D: Family Y配線(本文ハイライト・③訳リスト・Std Part 1 level化・Validator置換・page_verify G3、マーク発行未接続、API 0)`。Secret grep 0件。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: なし。

## 事前指定Read一覧

`DESIGN_03.md`(§B/§C/§D/§E Y節)、`CONTRACT_03.md`、`IMPL_PLAN_03.md`(D班)、`docs/pm/RESULT_PACKET_S23A.md`(1)(4)、`er_learning_highlight_01.py`(公開関数docstring)、`er121_family_y_audio_01.py:1400-1500`、`er121_family_y_runner_01.py:580-620,1000-1060,1180-1220`、`SPEC_CONFLICT_02.md`(Y該当行)。

## 報告

`RESULT_PACKET_S23D.md`: (0)T-0、(1)差分・配線点(file:line)、(2)golden・test結果、(3)旧経路撤去Grep、(4)B班API待ちの有無、(5)判断候補、(6)必須4行+「判定整合」、commit hash・raw URL。末尾5行要約。