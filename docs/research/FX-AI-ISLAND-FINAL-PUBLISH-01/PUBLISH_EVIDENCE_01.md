# PUBLISH_EVIDENCE_01 (FX-AI-ISLAND-FINAL-PUBLISH-01 委任_01、API 0)
## 公開URL
Std/Adv共通ページ(1 index.html内にStd/Adv): https://shimomura055.github.io/eigo-radio/user_test/family_x_ai_island_form_01/index.html (Std/Advは同一ページ内、音声は audio/ 配下47件)
## 手順根拠
- 前例: Word Gacha(`user_test/family_x_word_gacha_01/`==候補`..._candidate_b7_01/`はdiff空、commit dffd5b4f4初公開・0bff5a518差替え)。公開先=候補ページ名から`_candidate_b7_01`を除いたパス。AI島公開先=`user_test/family_x_ai_island_form_01/`(既存hr_01/02.htmlは残置、indexは新規)。
- 索引ページ=無し(Grepで公開記事一覧へのlink不在)。CURRENT_SPECに公開記事台帳なし(新設せず)。
- 根拠: CURRENT_SPEC.md:3187(AI島完成版=candidate b7_01を提出、最終試聴承認後に公開)、docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/B7_PUBLISHED_ARTICLES_01.md:8,22、OPEN_ITEMS.md OPEN-561/582。ユーザー承認=docs/pm/delegation_log/2026-10-29_FX-AI-ISLAND-FINAL-PUBLISH-01_USER.md §1。
## 同一性(試聴物との突合)
- 候補index.html git blob sha256先頭16=743d6fd06a0cb947(作業ツリーCRLF版=ac3fd71d5c5a2d0a。RUNTIME_EVIDENCE_01.md:35,41と一致)。公開index.html=候補blobとcmp一致。
- audio 47件: 候補と公開でsha256全件一致(diff空)。std_18.mp3=6323e844…(Z方式comment_3)、ai_island_temple_standard.mp3=24d6a78b…、ai_island_temple_advanced.mp3=bafe5938…、adv_00=fd00cf85…、adv_21=089a7f3c…、std_00=4d21cc91…(RUNTIME_EVIDENCE_01.md:41と一致=ユーザー試聴物と同一、Adv byte同一[docs/pm/RESULT_PACKET_FXC3P2.md:4])。
- Std C3 audit: passed_excerpt_sha256=c0326dc10ccc…、response_id=resp_0907239a0a8fede9…(RUNTIME_EVIDENCE_01.md:10,18)。
## 検証
- local page_verify(Playwright 156.0、tool=docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/tools/b7_local_page_verify_01.py): page_verify_public_local_01.json = HTTP200、audio 47/47再生、console error 0、4xx 0、file scheme 0、LR赤4、⏸10、fallback 0、旧LR注記0。
- Live(Pages反映後): live_verify_01.json = index.html及び47 mp3 全てHTTP 200・Content-Length>0・repoとbyte一致(bad=[])。
- 解説表示(html Grep): Key Phrase 8 / Preview 4 / Part 1 4 / Part 2 2 / Comment 1-4 各2(Std/Adv)。Std Comment 3 Z方式承認本文=live htmlに1件一致。
- 候補ページ `user_test/family_x_ai_island_form_01_candidate_b7_01/` は前例(Word Gacha)に従い残置。
- NUX1ゲート: RESULT_PACKET_NUX1.md 1行目=「AI島重大欠落=未特定(調査中)」→公開続行(委任_01 §2-5)。公開commit=9a2fb4b52。
## 環境メモ
Playwright(py 3.14)が未導入だったため pip install --user playwright + playwright install chromium を実施(ツール導入のみ、API 0)。
