# VERIFY_04 公開検証(委任_04、2026-10-27、API 0)
- 公開URL: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/ (commit 802bbf853。約5〜6分でPages反映、キャッシュバスタ付き)
- HTTP 200: index.html / data/articles.json / data/uk_train_speaker_playback__b1b__prod.json / data/melos__b1b__prod.json / form_logic.js。公開index.htmlに`cap_by_kind`表示あり。
- headless Chrome(公開URL、実DOM): `browser_check_04.mjs` pass=38 fail=0(`browser_check_04_public_output.txt`)。8記事すべてで候補行数=データ件数、グループ見出し`フレーズ（N件／上限7件）`/`単語（N件／上限5件）`、全行`正式訳`+AI理由あり、shortfall時の注記に`上限12件・フレーズ最大7・単語最大5`。12件満載(uk_train Advanced)で①<=3/①+②<=5/①+②+③<=12の上限が不変、送信フロー正常、Console error/exception 0。
- UI回帰: `browser_check_02.mjs` pass=19 fail=0、`browser_check_03.mjs` pass=9 fail=0(公開、`browser_check_0{2,3}_public_rerun_04.txt`)。
