# Fable受入記録 委任_05(rev01-e、2026-10-29)
受入記録:
(1)当初目的・要求された最終状態: ユーザー原文`docs/pm/delegation_log/2026-10-29_END-USER-LISTENING-PAGE-DEV-REVISION-01_USER_04.md`「目的：学習解説で取り上げている表現が、引用された英文のどの部分に該当するか、一目で分かるようにすること」「`carry over` のように原形で登録されていても、本文中の `carried over` を強調する」「対象が曖昧な場合は、無理に強調しない」「強調のために英文を書き換えない」「本文の1文ハイライト・文クリック再生・シーク・Key Phrase再生には影響させない」「修正版を既存DEV URLへ反映し、公開ページでの検証結果とURLを報告」。許容しない状態=英文の書換え、Production変更、既存機能のRegression。
(2)実際に生成・残存した最終成果物: 公開DEVページ build-id rev01-e(`user_test/dev_enduser_page_01/` index.html:5,10,34 / app.js emphasize():169 / style.css:122 `.target-term{font-weight:700}`)、commit 460a4e371・115178b4e。失敗終了なし。
(3)証拠: `verify_result_rev_e_live_01.json`:3769-3772 summary total=342, ng=[]、`"ok": false` 0件(Fable Grep)。app.js:174,179-182 一致0/複数=太字なし(`no_match`/`multiple_candidates`/`no_english_phrase_in_explanation`/`no_unique_match`)=失敗経路の挙動を確認。`shots_rev_e_live/pc_E_vocab.png`=「carried over」太字(見出し語carry over)、`pc_E_nuance.png`=「Still」太字をFableが目視確認。英文不変=verify(d) textContentバイト一致(Worker報告・JSON ok)。
(4)目的要件との一致: Vocab太字=一致 / ニュアンス太字=一致 / 文法太字=一致(仮データ3件とも"what matters"、実運用データでの複数語構文特定は未確認) / 語形変化対応=一致(carried over, taken a detour) / 曖昧時は非強調=一致(フェイルセーフ実装) / 英文無改変=一致 / 既存機能Regression=一致(rev01-d全チェック継承NG0、transcript署名一致) / DEVのみ・Production無変更=一致(diff 3ファイル+docs) / 公開URL検証=一致。未確認=実機iOS/Android(Playwright 390x844のみ)。
(5)最終受入判定と理由: ACCEPTED。目的(引用英文内で解説対象が一目で分かる)を公開ページ実画面で確認、失敗経路(特定不可→非強調)が実装され英文は不変、Regression NG0。
判定整合: 重大NG=なし
