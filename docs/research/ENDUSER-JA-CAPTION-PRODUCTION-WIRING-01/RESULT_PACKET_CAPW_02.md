# RESULT_PACKET_CAPW_02 ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01 委任_02(Opus反映→push→公開9dir一括再produce→6経路runner→公開URL実操作→SSOT)

worktree=wt_cap(`...\scratchpad\wt_cap`)。切替commit=`e25f16293`(`er135_enduser_rules_01.py:12` rev01-i)+再produce commit `77babf1c5`を**同一push**=`4df50f8bf`(origin/main、**2026-10-31 17:15:15 JST**)。並行Worker周知用: 以後 origin/main の ASSET_BUILD_ID=rev01-i。rev01-h時代にbuildしたpages dirは`publish-copy`/`verify-consistency`が rc=3(`ENDUSER_ASSET_MISMATCH`)で止まる=該当pages dirは`page_verify`段を含めて再実行(enduser再同期)すること。SSOT commitは報告本文のhash参照。
詳細証跡=`docs/research/ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01/RUNTIME_EVIDENCE_01.md`+`evidence_02/`(以下 ev/)。API呼出0・開発実費0円。

## 1 Status(Family x レベル)= 全 PRODUCTION_WIRED_PENDING_FABLE(Fable独立受入待ち。実機iOS/Android未確認)
X: ai_chat_sponsored_persuasion / jwst_mystery_emission_line / meta_waddle_world / moon_shrinking_reselect / untidiness_family_resource x Std,Adv。Y: redelivery_fee_03 / surname_choice_01 x Std,Adv。Z: melos_kphr_evidence_r3 / yuki_onna_01 x Std,Adv。対象外=凍結 family_z_in_a_grove_01(rev01-e)。
## 2 公開URL(全て `https://shimomura055.github.io/eigo-radio/user_test/<dir>/enduser/index.html?lv=std|adv`、`?caption=0`でOFF)
`family_x_ai_chat_sponsored_persuasion_01` `family_x_jwst_mystery_emission_line_01` `family_x_meta_waddle_world_01` `family_x_moon_shrinking_reselect_01` `family_x_untidiness_family_resource_01` `family_y_production_redelivery_fee_03` `family_y_production_surname_choice_01` `family_z_melos_kphr_evidence_r3` `family_z_yuki_onna_01`。build-id=rev01-i 9/9(17:23:27確認、push後約8分)。
## 3 ON/OFF実動作(公開URL実操作)
初期ON・OFFで領域解放(バー113px・余白23px=rev01-h同一)・ONへ戻すと現在の訳とバー高が復帰・`?caption=0`再読込でOFF・レベル切替で保持・ON時URLから`caption`削除・再生中切替でcurrentTime/paused不変: 全54組(9dir x Std/Adv x PC/スマホ/320px) PASS(`ev/observe_public_summary.md`)。
## 4 PC/スマホ結果
chromium公開 54/54 PASS(error 0)+WebKit(iOS近似)スマホ 6/6 PASS。観測した文3,003・キャプション有り2,517・**期待値が空欄の文486**(`ja_align`由来の期待値と全文一致=誤表示0)・再生中サンプル4,320(キャプション=点灯日本語 不一致0)。ON時バー高 PC176.4/スマホ172.8px(0〜2行一定=R-1是正)。残: 320px幅の再生中nowLabel省略(ev/RUNTIME_EVIDENCE 6、操作影響なし)。
## 5 既存再生・英日ハイライトへの影響
無し(再生・点灯ロジックのコード無変更、追加は`capUpdate()`呼出2箇所のみ)。公開9dir verify(298項目級・PC+mobile、英文クリック=OPEN-624・英日連動=OPEN-618・K/J/F/G/V等)= 8dir NG0、X metaは公開負荷時に`G part_boundary`の1回NGのち単独再実行 TOTAL 298 NG 0。unit er135 9本+er136 PASS(`ev/unit_tests.txt`)。diff gate: 公開9dirの変更は4file(app.js/style.css/index.html/build_info.json)のみ、article.json/sync/音声/本文/訳 byte不変(`ev/diff_gate_out.jsonl`)。
## 6 retry/fallback/regeneration/resume整合
`ASSET_BUILD_ID`1行で全経路。正式runner X/Y/Z 3経路を**rev01-h時代のpages dirに再実行**し rev01-i 化(rc=0、hook_run browser verify NG0、CAP検査群28項目OK、runner出力observe 18/18 PASS)。rev01-h pages dirは`verify-consistency`/`publish-copy`が rc=3で止まり公開へ漏れない(`ev/r5_*`)。stage skip機構なし(`er121`/`er026` `_select_stages`、enduserは`stage_page_verify`内/Xはbuilder末尾)。
## 7 Regression/Validator・間欠NGの原因と扱い
vocab_each_item=検査側競合(確定・再現`ev/repro_vocab_flake.py`、検査是正)/glossary_links=検査側競合(推定・未再現、到達待ちに是正)/G part_boundary=公開負荷による環境NG(単独再実行NG0)/webkit初回1件=observe側`play()`未処理拒否(是正)。是正後は再produce9・runner3・公開verify9で vocab/glossary NG 0。新規CAP検査の陰性対照2件(blank caption→NG4、旧CSS→NG4)で検出力を確認(`ev/negative_controls/`)。
## 8 量産単価・開発実費
量産単価+0円(新LLM/TTS/ASR/embedding呼出なし)。開発実費0円(ダミーキー+dead proxyで構造的にAPI 0。build_info cost/judge全0、`ev/diff_gate_out.jsonl` api0欄)。
## 9 SSOT/Git
CURRENT_SPEC(End Userページ節に日本語キャプション仕様)・OPEN-628(PRODUCTION_WIRED_PENDING_FABLE)・DECISION_LOG(ENDUSER-JA-CAPTION-PRODUCTION-WIRING-01-DECISION-01)。commit/pushは報告本文のhash。Opus条件Aレビュー=`OPUS_REVIEW_01.md`(R-1/R-4/M-1〜M-5/R-5〜R-8全て反映)。
## 10 残Open Item
新規OPENなし(OPEN-628内に記録): 実機iOS/Android未確認(実害なし)・320px nowLabel省略(実害なし)・glossary間欠の未再現(再発時は製品側として別OPEN)。

## Fable受入用の証拠(file:line/path)
- 切替=`er135_enduser_rules_01.py:12`、asset=`enduser_page_assets/rev01-i/{app.js:263-281 capUpdate/capSetOn/capInit,index.html:10,29-31,style.css 末尾}`、派生=`enduser_page_assets/build_rev01i_01.py`。
- verify CAP検査群=`er135_enduser_page_verify_01.py`(`caption_checks`/`caption_expected`、呼出=linked_checks直後)、vocab/glossary是正=同V節・I節。
- 公開観測=`ev/observe_public_{pc,mobile,narrow}/observe.json`+`observe_public_summary.md`、WebKit=`ev/observe_public_webkit_summary.md`、公開verify=`ev/public_verify/`。
- runner=`ev/runner/{runner_x,y,z}.log.txt`+`status_runner.txt`+`snap_before/after.json`、produce=`ev/produce/`、gate=`ev/diff_gate_out.jsonl`、R-5=`ev/r5_*`、陰性対照=`ev/negative_controls/`。

## 判断候補(いずれも停止根拠なし。既判断=A案/初期ON/Trial外観基本/『字幕 ON/OFF』文言/`?caption=`方式は再質問しない)
1. 320px幅で再生中の`nowLabel`(『全体 · Key Phrase 1』等)が省略表示される(390px以上は省略なし、操作・再生に影響なし)。分類=B(承認済み2-2/2-3の副作用。実害なし)。対処案: (a)現状維持(推奨)/(b)320px未満のみラベル短縮(新仕様扱い)。根拠: `ev/RUNTIME_EVIDENCE_01.md` 6、`observe_public_summary.md`末尾。
2. 実機iOS/Android未確認(Playwright Chromium/WebKit模擬のみ)。分類=C(受入時にユーザーが実機を見るか。Fable判断)。
3. glossary間欠NGは未再現のため原因は推定止まり。是正済みで再発0(再produce9・runner3・公開verify9)。再発時は別OPEN。

RESULT_PACKET 4行: (1)既存仕様整合: 原文2-2/2-3・OPEN-618(rev01-f)・OPEN-624(rev01-h)・`er135_enduser_page_01.py:1453-1457/1511-1515`を照合、再生/点灯ロジックのコード無変更。 (2)未承認機能の既定値: 該当なし(ユーザー承認済み。既定ON=`index.html:10 class="capon"`+`capInit Q.get('caption')!=='0'`、公開54/54で確認)。 (3)失敗終了時の最終成果物: 正常終了。最終成果物=origin/mainの公開9dir(rev01-i)+`ev/`。途中失敗(pilot produce 1回=検査側競合、runner初回2回=環境[mirror root資源欠落]、公開verify 1回=負荷NG、Target crashed 1回)はいずれも公開dir無変更/再実行でNG0。 (4)撤去・残置: research側build_rev01i→`enduser_page_assets/`へ移設(旧path Grep 0)、Trial dir assets削除(案内ページ化)。残置=rev01-e/f/g/h asset(履歴)、`tools/ech02_diff_gate_01.py`(rev01-h固定、前回専用)。
判定整合: 重大NG=なし / 提示=可
