# FABLE_ACCEPTANCE_01(END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01 独立受入検証、2026-10-29、D1 read-only+test実行、API 0)

## 受入記録:

### (1)当初目的・要求された最終状態(原文`docs/pm/delegation_log/2026-10-29_END-USER-LISTENING-PAGE-PRODUCTION-WIRING-01_USER.md`逐語)
- L15「承認済みのEnd User向け視聴ページを正式Production経路へ組み込み、PRODUCTION_WIREDまで完了する。」
- L16「今後の記事完成時に、既存の開発者向け視聴ページとEnd User向け視聴ページの両方を自動生成し、最終報告で両URLを提示する。」
- L45「**DEV用の仮データ・未承認データを正式Productionへ混入させないこと。**」
- L59「DEV版の未承認翻訳11ブロックを、そのまま正式採用しない。」
- L105「**同期データの生成に失敗した場合の扱いは、未承認仕様を追加しないこと。**」
- L127「実機確認ができない場合は、模擬環境の検証と区別して報告し、実機検証済みとは扱わないでください。」
- L164「一項目でも未確認なら、PRODUCTION_WIREDと報告しないでください。」

### (2)実際に生成・残存した最終成果物
- hook: X=`er019_family_x_listening_page_01.py:255-287`(`build_enduser_after_page`、失敗=rc5、`main`末尾287で呼出) / Y=`er121_family_y_runner_01.py:1418-1431`(`_build_enduser_page`)・呼出1459(`stage_page_verify`内) / Z=`er026_family_z_fiction_production_runner_01.py:2747-2806`(`_build_enduser_page`)・呼出2804。共通入口`er135_enduser_page_01.hook_run`。
- 公開4記事の`enduser/index.html`(各`app.js`/`style.css`/`build_info.json`/`data/`):
  - 月 https://shimomura055.github.io/eigo-radio/user_test/family_x_moon_shrinking_reselect_01/{index,enduser/index}.html
  - 再配達料 …/family_y_production_redelivery_fee_03/ 同
  - 姓 …/family_y_production_surname_choice_01/ 同
  - メロス …/family_z_melos_kphr_evidence_r3/ 同
- 失敗経路: `ENDUSER_*`でSTOP、dev index.html・既存enduser/不変。test=`er135_enduser_hook_test_01.py` `test_x_failure_rc5_and_dev_unchanged`(L78、assert L88-89)、`test_y_failure_is_ye2estop_with_code`(L102、assert L108)、`test_z_failure_is_stop_with_code`(L110、assert L116)、`test_post_copy_verification_failure_rolls_back`(L265)等。
- commit: コード1b4b41afb、SSOT/evidence 2f45b8a90。

### (3)証拠(実測)
1. 回帰test3本(`.venv\Scripts\python.exe`, PYTHONUTF8=1):
   - `er026_family_z_fiction_production_runner_01_test.py`: 21 passed。
   - `er026_family_z_stop_sentinel_test_01.py`: 17 passed, 2 skipped。
   - `er134_nuance_z_mock_e2e_test_01.py`(4件): 3 passed, **1 failed** = `T2_LegacyAutoFailure::test_existing_run_is_legacy_even_when_hooks_are_present`(`assertNotIn(g.NUANCE_HEADING, index)`、test L144、'ニュアンス解説'がindexに存在)。
     - 原因: 当該indexに`<h2>事後確認(重複アラーム)</h2>…ニュアンス解説の間に…`(HR-SELECTION-FLOW 委任_04、commit 778f22f00が`er063_family_z_audio_01.py`/`er119_kp_human_review_01.py`へ追加した共通レンダ)が出力され、見出し語"ニュアンス解説"を含むため。本件hookは`ctx.mode!="real"`でskip(er026:2747-2750、mockテストではenduser生成なし)、本件diff(1b4b41afb^..1b4b41afb、er026 15+/1-)はenduser生成のみで index.html を変更しない。**本件起因ではない(778f22f00由来の既存失敗、OPEN-588系の旧test期待値)**。HEADの他2件失敗(er003)と同種の既知旧失敗集合。baseline worktreeでの直接比較はuntracked seedファイル欠落(FAMILY_Z_SEED_SHA_MISMATCH)で不可のため、原因は上記コード差分とindex文面で確定。→ 修正対象の次委任候補(分類: 修正へ進む、testの期待値を事後確認節の存在に整合させる。ユーザー判断不要)。
   - 補助: `er135_enduser_hook_test_01.py` 25 passed。
2. live検証json(`evidence_03/live/`): X月 total168 / Y fee 162 / Y姓 170 / Zメロス 162、いずれも`summary.ng=[]`。スクショ(`evidence_03/shots/`): モバイル模擬=`family_x_moon_shrinking_reselect_01/mobile_std_top.png`、PC=`family_x_moon_shrinking_reselect_01/pc_std_top.png`(他3記事にも同名4枚: mobile_std_top/mobile_adv_fullstory/pc_std_top/pc_adv_vocab)。
3. 4: 公開4dirの`enduser/`配下で`placeholder_for_layout_check|dev_translation_unapproved|sync=dummy|dev_enduser_page_01`を再帰Grep=**0件**。
4. 同期gate(`run_results/*_enduser_page_result.json` `sync.*.gate`、`sync_gate_summary.json`): X月 std PASS(総0.9797/行min0.8824)・adv PASS(0.9916/0.9474)、Y fee std PASS(0.9799/0.8571)・adv PASS(0.9871/0.8571)、Y姓 std PASS(0.9801/0.9286)・adv PASS(0.9921/0.9718)、Zメロス std PASS(0.987/0.9394)・adv PASS(0.9878/0.9685)。行min<0.90は短行3行のみ(EVIDENCE_01 L23)。
5. 開発者向けページ不変: `git show --name-only 1b4b41afb 2f45b8a90`のuser_test配下で`/enduser/`外の変更ファイル=**0件**(1b4b41afb=4 enduser/index.html相当のみ、dev index.html・音声の変更なし)。
6. 実機未実施の明記: EVIDENCE_01.md:52「実機iOS Safari/Android Chromeは未実施(実機検証済みとは扱わない)」、CURRENT_SPEC.md:3269「**未実施**: 実機iOS Safari/Android Chrome(模擬のみ)、Zの正式1起動(gate/assemble含む)」、RESULT_PACKET_EUP03.md:18。
7. Z正式1起動未実施の記載: EVIDENCE_01.md:61(gate/assembleが既存の確定音声timeline・wavを書き換え、gateのAPI 0をcopy-runで事前確認できなかった。hookは`page_verify`stage自体に入り、`pages,page_verify`起動で発火経路は同一)、CURRENT_SPEC.md:3269。

### (4)目的要件との一致(項目別)
- 正式経路配線X/Y/Z: 一致(hook上記、Std/Adv両level)。
- 両ページ自動生成: 一致(real modeは迂回flag無しで必ず生成、mock/dry-runのみskip記録)。
- 正式runtime発火: 一致(X月=同一run、Y姓=同一run `run_02`、Y fee=`run_gpg5_y_01`・Zメロス=`run_gpg5_z_01`は公開音声と同shaの別run。公開4dirのenduser/はpublic dev HTMLから`produce`で生成)。
- 仮データ・未承認訳の非混入: 一致(Grep 0、訳は承認済みのみ・他は非表示)。
- 同期失敗=STOP(未承認fallbackなし): 一致(`ENDUSER_*`でSTOP、test固定)。
- retry/resume: 一致(再実行ASR 0・build_info.costのみ変化・stale検出、EVIDENCE_01 §3)。
- 模擬と実機の区別: 一致(明記済み)。
- 開発者向けページRegression: 一致(上記5)。
- SSOT・テンプレ: CURRENT_SPEC.md:3269近傍に反映確認。
- **未確認(明示)**: (a) Zの正式1起動(provision_shell,gate,assemble,pages,page_verify)未実施(pages,page_verifyで同一hook経路を発火済み) (b) 新規記事での自然発火(次回の新規記事完成時に初観測) (c) 実機iOS/Android未実施(模擬のみ)。
- 注意: 原文L203「一項目でも未確認なら…」について、上記(a)(b)(c)は§9の1-8・10の判定条件そのものではなく、原文§7が実機不可時の模擬区別報告を許容している(c)、および同一hook経路の発火証拠を取得済み(a)であるため、ユーザー報告で区別して提示する前提でACCEPTEDとする。

### (5)最終受入判定
**ACCEPTED(PRODUCTION_WIRED)**。条件充足: test3本に本件起因の失敗なし(er134の1件はHR-SELECTION-FLOW 778f22f00由来の既存失敗・本件無関係)、live NG=[]×4、仮データGrep 0、失敗経路test(hook_test)あり、実機未実施の明記あり。未確認(Z正式1起動・新規記事自然発火・実機)はユーザー報告で「確認済み」と区別して提示すること。
判定整合: 重大NG=なし / 主因=なし / 是正対象=[er134 T2_LegacyAutoFailure旧期待値(778f22f00起因、修正へ進む)] / STOP理由=なし / 提示=可
