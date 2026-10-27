## 管理ID

SLOT-23-CONSUMER-DESIGN-01 委任_07G(F班(commit 62663d4e9)が検出した不具合D-F1の是正: `er120_part2_wiring_01.py:512-533` `public_study_html`がPart 1を`level=="b1b"`のときだけ生成するため、X標準公開builder(`er019_family_x_listening_page_01.py:143-148`)がdisplay_spec付きStdで`X_PART1_BLOCK_COUNT(a2 page)` STOP。承認済み仕様(USER_04 §2: Std②=①と同等の日本語詳細解説、Std Part 1=①+②)との矛盾=11-8「修正へ進む」。API 0(ページ生成のみ。TTS/LLMなし)。並行Agent: なし。あなたの所有=`er120_part2_wiring_01.py`(`public_study_html`の該当分岐のみ)、`er120_part2_wiring_integration_test_01.py`/新規`er120_public_study_html_level_test_01.py`、`er019_family_x_listening_page_01.py`(必要最小限)、`docs/research/SLOT-23-CONSUMER-DESIGN-01/{FIX_DF1_01,EVIDENCE_RESULT_07,BROWSER_CHECK_07}.md`+`evidence_runs/x2/`+`screenshots/`、`..._DELEGATION_07G.md`(+check.json)、`docs/pm/RESULT_PACKET_S23G.md`(gitignore)。SSOT権なし。pathspec付きcommit、`git push origin HEAD:main`、run dir不追跡。時間見込み約1h。

## 実施事項

1. 是正: `public_study_html`のPart 1分岐を、`er128.display_spec_of(run, level)`(flag非経由)または`er119.vocab_enabled(level, review)`ベースへlevel化。Part 1 HTMLは`er003_kp_general_explanation_01.study_html_for_audio_dir(audio_dir, level=)`(B班API)で生成。**display_spec無しのa2=従来どおりPart 1なし、b1b=従来どおり**(golden: 既存Adv出力バイト同一、Y/Zの既存ページ出力バイト同一=F班のY/Z `_s23f` pages sha、旧run `run_p2_evidence_r3`/`run_style_fix_01` sha不変)。Validator・Gateは緩めない。
2. test: display_spec付きa2でPart 1ちょうど1個(①+②)、無しa2で0個、b1b不変、Part 1→Part 2順、`er120_*`/`er019_x_highlight_wiring_test_01`/`er121_y_highlight_wiring_test_01`/`er026_z_highlight_wiring_test_01`/`er128_*`回帰PASS(既知OPEN-543失敗は記録)。
3. X公開ページ再取得(API 0): F班のX複製run `er019_output/family_x_audio_production_wiring_01/part2_hr_evidence_01__run_gpg5_x_01_s23f`で標準builderを再実行→`index.html`出力、`check_page(public)`PASS、G3 PASS、Part 1=Std/Adv各1個(①3+②2、日本語解説)、`data-hl`=確定件数、③訳リスト逐語、public `⏸`0、確定レコードcmp同一、builder再実行でsha同一。`EVIDENCE_RESULT_07.md`+ブラウザ検証(1280/375/390、F班toolを再利用)`BROWSER_CHECK_07.md`。
4. AI島(`ai_island_temple__run_form_prod_01`)への影響確認: display_spec付きa2で`public_study_html`が正しくPart 1を返すことを**dry(関数呼出のみ、ファイル書込なし)**で確認(HR承認前のためbuilder実行・公開はしない)。
5. commit: `SLOT-23-CONSUMER-DESIGN-01 委任_07G: D-F1是正(public_study_htmlのPart 1 b1b限定をdisplay_spec/levelベースへ)+X Std/Adv公開ページevidence再取得(API 0)`。Secret grep 0件。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: なし。

## 事前指定Read一覧

`docs/pm/RESULT_PACKET_S23F.md`(4) D-F1・`evidence_runs/x/17_listening_page_public.txt`/`18_public_study_html_probe.txt`、`er120_part2_wiring_01.py:490-540`、`er019_family_x_listening_page_01.py:120-170`、`IMPL_B_01.md` §2(公開API)、`er128_kp_confirmed_content_01.py`(Grep `def display_spec_of` ±10)、`docs/research/SLOT-23-CONSUMER-DESIGN-01/tools/{verify_page_s23f_01,browser_check_s23f_01}.py`。

## 報告

`RESULT_PACKET_S23G.md`: (0)T-0、(1)差分、(2)golden・test、(3)X公開page evidence(a〜i相当)・ブラウザ、(4)AI島影響、(5)判断候補、(6)必須4行+「判定整合」、(7)SSOT文案(OPEN-562 X経路)、commit hash・raw URL。末尾5行要約。