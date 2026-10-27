# B5_FINAL_HUMAN_REPORT_01: 最終Human報告用資料 生成器(未配線の読取専用CLI)+混入防止test+保存run資料(委任_09 / Phase B B5、API 0)

管理ID: LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01。委任文=`…_委任_09.md`。ユーザー原文=`…_USER.md` §2・§6。設計=INTEGRATION_01 §1/F-3/F-13/F-14・OPUS_REVIEW_01(M-7/R-5)・W4_FINAL_HUMAN_REPORT_DESIGN_01・W4_SAMPLE_01.html。前提=`er129_lr_display_reflection_01.py`(e56c9a04f)。

## 0. 結論
1. 新module `er131_final_human_report_01.py`(読取専用CLI、**未配線**=E2E_STAGES・公開ページ生成器・TTS・ASRのどこからもimportされない)+test `er131_final_human_report_01_test_01.py`(**37件PASS**、約14秒)+生成資料 `final_human_report/`(18資料+index)。有料API 0・LLMなし。run dir・既存Productionコード・公開ページ生成器・SSOT無編集。
2. 入力は `er129.build_lr_ledger(only_events=False)` が**唯一**(採用take解決・LR差分・三者一致はer129。er131に独自の採用attempt規則なし。testでAST/文字列確認)。W4 §3の独自読取規則は使っていない。
3. 表示=LR赤(変更後 太字+二重下線、変更前 取消線、前後英文・変更語句・理由)/Fallback濃青(対象テキスト全体+注記: 発動の事実・最終採用Style名・切替元Style・範囲)/重複=青区間内に赤語句/実行履歴=灰枠/記録欠落=「記録なし」/記録衝突=黄色の文字警告(青にしない)/TTS未実行(evidence runの対象外clip)=灰。時刻・cooldown・pathは非表示(sha先頭8桁のみ)。
4. Fable補足(1)(2)(3)の反映: Y E-1 a2 `y_voice_1`=Fallback発動なし+「記録衝突(採用attemptはrole Style)」を黄色警告文で表示 / Z猿の手Std `full_story_part1_c10`=LR赤+Fallback「記録なし」 / 告げ口心臓Adv `kp2_en`=ENGLISH_LOCK青(`mock`、sha dcd08dca)。

## 1. CLI
`python er131_final_human_report_01.py --run <run dir> --family X|Y|Z|A|B|C [--level a2|b1b|both] [--slug S] [--out-root DIR]`
出力=`final_human_report/<FAMILY>/<slug>/<run>/{standard,advanced}.html`(a2=standard、b1b=advanced)。`write_index()`で目次`final_human_report/index.html`(noindex、学習者向けindexからリンクしない)。出力先が`user_test/`・`er*_output`・run dir配下ならrc=2で拒否(何も書かない)。
Role網羅: er129の全clip(固定殻/固定MPは「対象外」、連結親は子chunk単位、SKIPPED系は「TTS未実行」で記録欠落と区別)。A/B/C=`attempts_log`+`fallback_used`がある範囲で**Fallback有無のみ**(Style名・LRは「記録なし/記録形式なし」)、無ければ「表示不可」(音声方式は不変。実測: er012 e_family meta で動作確認、commit対象外)。

## 2. 混入防止5層(test)
| 層 | 内容 | test |
|---|---|---|
| 1 | er131のlocal importは`er129`のみ(公開ページ生成器・TTS・ASR・KP表示・Prompt module prefix禁止)。逆向き: 他の全`*.py`・`tools/*.py`がer131をimportしない。E2E stage側にer131が無い | test_layer1_* |
| 2 | 生成前後でrun dir(wav/mp3除く)のsize+sha256一致 | test_layer2_* |
| 3 | `user_test/`・`er*_output`・run dir配下はPermissionError/rc=2。公開index群に`final_human_report`が0件 | test_layer3_* |
| 4 | 保存run 6件でFHR語0件(下表)+公開HTML 19件で0件 | test_layer4_* |
| 5 | `check_page(public)`追加検査の仕様(下記)をmodule関数`check_page_fhr_contamination`で実装・test。**配線は統合commit** | test_layer5_* |

### 層4の実測(FHR語=`fhr-`/`FINAL_HUMAN_REPORT`/`LR_REWRITTEN`/`LR_APPLIED`/`FALLBACK_APPLIED`/資料注記文言/Fallback Style表示名)
走査件数[対象数, 命中数]。tts_input=`tts_generation_results.json`のtext系field(text/canonical_text/audio_text_after/instruction_text等)、asr_expected=`er129._lr_info`経由(er020のresolve_expected_text)、style_prompt=attempt jsonのinstruction_text、kp_study=key_phrases/study_text/support、scripts=parts.json/article.md/*_support_texts.json。
| run | tts_input | asr_expected | style_prompt | kp_study | scripts |
|---|---|---|---|---|---|
| X AI島 | 392/0 | 52/0 | 60/0 | 0件(dir無)/0 | 4/0 |
| Z 告げ口心臓 | 165/0 | 57/0 | 52/0 | 71/0 | 0/0 |
| X Word Gacha | 339/0 | 36/0 | 53/0 | 0/0 | 4/0 |
| Z メロス(run_e2e_06=family_z_melos_02) | 275/0 | 97/0 | 82/0 | 48/0 | 0/0 |
| Z 猿の手 | 304/0 | 101/0 | 70/0 | 53/0 | 0/0 |
| Y E-1 | 353/0 | 42/0 | 70/0 | 59/0 | 4/0 |
公開HTML(`user_test/family_x_ai_island_form_01`・`family_x_word_gacha_01`・`family_z_melos_02`・`family_z_monkeys_paw_01`・`family_z_tell_tale_heart_reselect_01`・`family_y_production_redelivery_fee_01/02/03`): 19ファイル、**FHR語・色定義ペア命中0**。
**既存の未是正混入(別集計、FHR語ではない)**: `user_test/family_z_monkeys_paw_01/standard.html`に既存のZ公開ページ注記「Local Rewrite採用(音声は原稿から変更」が1ファイルある(INTEGRATION F-9=B3で撤去予定。本委任では編集しない)。

### 層5: `check_page(public)`へ追加する検査仕様(配線は統合commit。`er_user_listening_page_common_01.check_page`は本委任で編集しない)
公開pageの文字列に次のいずれかが含まれたらNG: (a)`er131.FHR_TOKENS`(`fhr-`・`FINAL_HUMAN_REPORT`・`LR_REWRITTEN`・`LR_APPLIED`・`FALLBACK_APPLIED`・資料注記語「Local Rewrite発動(最終採用音声に反映)」「最終採用音声はFallback Style」「切替元Style:」・Fallback Style表示名3種) (b)色定義ペア`#c00000`と`#0a2a6b`の同居。併せて既存のZ公開ページ注記語「Local Rewrite採用(音声は原稿から変更」は、F-9の撤去後に同checkへ追加(今追加すると猿の手Stdの既存ページが即NGになる)。TTS入力/ASR正解/Style Prompt側は`scan_run_contamination`が同じ語で0件を保証(層4)。

## 3. 生成資料(commit対象、`user_test/`外。公開はGitHub Pages経路。URLはpush後)
| 対象 | 実測内容(資料の表示) | URL |
|---|---|---|
| X AI島 Std | LR 1(`AIs`→`AI agents`、k2)・Fallback 0(元ブロックの試行は履歴に灰で記載)。Std 22単位 | https://shimomura055.github.io/eigo-radio/final_human_report/X/ai_island_temple/run_form_prod_01/standard.html |
| X AI島 Adv | LR 1(`AIs`→`AI systems`)・Fallback 0。24単位。Adv KP解説等5単位は採用take記録なし=「記録なし」(er129のUNKNOWN) | https://shimomura055.github.io/eigo-radio/final_human_report/X/ai_island_temple/run_form_prod_01/advanced.html |
| X Word Gacha Std/Adv | Adv LR 1(`you've`→`you have`)・Fallback 0 | https://shimomura055.github.io/eigo-radio/final_human_report/X/word_gacha/run_wg_01/advanced.html (standard.htmlも同dir) |
| Z メロス(_02=run_e2e_06) Std/Adv | LR 0・Fallback 0=発動なし(49単位、固定殻は対象外) | https://shimomura055.github.io/eigo-radio/final_human_report/Z/melos/run_e2e_06/advanced.html (standard.html) |
| Z 猿の手 Std | LR 1(`guest`→`visitor`、c10)・Fallback「記録なし」(採用take UNKNOWN) | https://shimomura055.github.io/eigo-radio/final_human_report/Z/the_monkeys_paw/run_sf_prod_01/standard.html (advanced.html) |
| Y E-1 Std/Adv | LR案あり→人間承認で原文音声採用(赤なし・「最終音声に反映なし」)・Fallback発動なし。Stdは「記録衝突(採用attemptはrole Style)」警告 | https://shimomura055.github.io/eigo-radio/final_human_report/Y/redelivery_fee/run_01/standard.html / advanced.html |
| Z 告げ口心臓 Std/Adv | Std LR 0・Fallback 0 / Adv LR 0・**Fallback 1**(kp2_en `mock`、ENGLISH_LOCK、青) | https://shimomura055.github.io/eigo-radio/final_human_report/Z/the_tell_tale_heart/run_reselect_01/standard.html / advanced.html |
| tru_ev X adv_16 | **LR+Fallback重複**(in_one_line、`affect`→`influence`が青区間内の赤、英語短文Style) | https://shimomura055.github.io/eigo-radio/final_human_report/X/coffee_prices/run_tru_ev_x_adv_16/advanced.html |
| tru_ev X std_6 / Y std_2b / Z std_4 | 日本語短文Style(Minimal)Fallback(青) | https://shimomura055.github.io/eigo-radio/final_human_report/X/coffee_prices/run_tru_ev_x_std_6/standard.html / https://shimomura055.github.io/eigo-radio/final_human_report/Y/redelivery_fee/run_tru_ev_y_std_2b/standard.html / https://shimomura055.github.io/eigo-radio/final_human_report/Z/the_monkeys_paw/run_tru_ev_z_std_4/standard.html |
| tru_ev X adv_10 | ENGLISH_LOCK(青) | https://shimomura055.github.io/eigo-radio/final_human_report/X/coffee_prices/run_tru_ev_x_adv_10/advanced.html |
| tru_ev Z adv_2 | Z Dialogue切替(従来Dialogue Style、青) | https://shimomura055.github.io/eigo-radio/final_human_report/Z/the_monkeys_paw/run_tru_ev_z_adv_2/advanced.html |
目次: https://shimomura055.github.io/eigo-radio/final_human_report/index.html

## 4. 観測・未観測・注意
- 観測: test 37件PASS、混入0(上表)、生成資料の件数・表示を保存runから実測。
- **er129 testの既存失敗(本委任起因ではない)**: `er129_lr_display_reflection_01_test_01.py::test_u8_no_production_module_imports_er129`が「er129を他moduleがimportしたら失敗」の固定で、同時進行の`er130_adopted_take_classifier_01.py`・`er132_lr_overlay_pages_01.py`と本委任`er131`(いずれも設計上のer129利用者)で失敗する。allowlist化(er130/er131/er132を許可)は統合時にer129 testを更新する必要あり(新規OPEN候補、分類=修正へ進む・実害なし)。本委任ではer129 testを編集していない。
- 未観測: ブラウザでの目視(赤・青の見え方)、GitHub Pages上のURL疎通(push直後は未反映の可能性)、音声プレーヤー埋め込み(W4 Phase B後続。本資料は静的で音声を埋め込まない)、実E2E完了後の自動生成hook(未配線)。
- Adv AI島のKP解説等5単位が「記録なし」になるのはer129の旧記録導出がKP_EXPL(Advance解説)を確定できないため(推測しない設計どおり)。final_adoption配線(委任_06)後のrunでは解消する見込み。
