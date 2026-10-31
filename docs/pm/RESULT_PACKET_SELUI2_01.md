# RESULT_PACKET SELECTION-UI-TWO-TIER-01 委任_01 (2026-10-31, API 0, 費用0)
結果: 選定UIを2階層化(トップ=一覧・進捗・一括コピー / 個別=`?set=<slug>__<level>`、上下「Topへ戻る」)。UI版sel-v3-rev05-a。公開URL実操作 PC・mobile 各33チェック全PASS(原文§5の1〜12、戻る/再読込、無効URL、er128 18/18、別batch非混在)。Regression: node 86 PASS(新規05含む)・sub04_tools_test 9 OK・er128 restore test PASS。
URL(test batch, latest=null): トップ https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/index.html?batch=twotier-a-18sets-test / Std例 ...&set=moon_shrinking__a2 / Adv例 ...&set=moon_shrinking__b1b
証跡: docs/research/SELECTION-UI-TWO-TIER-01/{DESIGN_01,EVIDENCE_01}.md, live_result_{pc,mobile}.json, smoke_*.json, shots/
(1)既存仕様整合: 原文§3の維持項目(form_logic.js純関数・localStorageキー`eigo-kp-form-v3:b:<id>`・Done署名・BATCH1書式)無変更。照合=user_test/selection_form_v3/index.html(init/renderTop/render)、tools/publish_selection_batch_01.py:53(版regex)、selection_form_logic_test_01.js:720-748
(2)未承認機能の既定値: 該当なし(承認済み表示UIのみ。Production制作経路・Prompt・閾値・辞書は差分0)。確認=git diff 92a4e79c3..HEAD --stat(user_test/selection_form_v3/{index.html,form_logic.js版1行,data/batches/*}のみ)
(3)最終成果物: 公開済みtest batch 2件(latest=null)+公開UI。実報告は未発行(Fableがpublish toolで作成)。成功終了。原文の要求(2階層・上下Top・保持・一括コピー1回・公開実操作)に適合
(4)撤去/残置: 旧1ページUIの記事切替セレクタ・チップのボタン化・`?a=`のURL書換を撤去(`a`は`set`同義で受理=互換)。旧検証script sub02a_verify.py/sub04_verify.py は旧UI用の履歴証跡として残置(新UIでは非実行、Ctx/copy_checks/er128_dryのみ再利用)。grep: `activate(` は個別ページ初期表示1箇所のみ
判定整合: 重大NG=なし
副次修正: スマホ390pxで候補.flag(nowrap)の横overflow(rev04既存)を是正、live smoke toolを2階層UI対応に更新。
判断候補: なし(停止根拠なし)。旧form1_selection_form_v3_test_01.py 5件失敗はsparse worktree fixture欠落の環境要因(変更前stashと同一)。
