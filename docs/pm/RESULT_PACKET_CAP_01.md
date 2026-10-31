# RESULT_PACKET ENDUSER-JA-CAPTION-TRIAL-01 委任_01(2026-10-31)
- 成果: 日本語キャプション方式Trial(X meta_waddle_world / Y surname_choice / Z melos_kphr_evidence_r3 各Std+Adv)。最終成果物=`user_test/enduser_caption_trial_01/`(assets/ + 6ページ + 一覧index.html)。Production asset rev01-h・er135_enduser_rules_01.py・既公開dirは無変更。API 0。
- 確認: er135 verify(Trial版) X/Y/Z NG 0(270/268/250件、F sentence_click含む)。キャプション=点灯日本語一致 mismatch 0(約135点x12観察)、クリック/シーク/±10秒/一時停止/KP/Vocab/ここから再生で破綻・エラーなし。実機未確認(Playwrightエミュレーション)。
- 気になる点: 固定バー+約60-75px(スマホ画面約22%)。
- 推奨: Status=VALIDATED(Trial)、採否=USER_DECISION_REQUIRED(OPEN-628)。
- 証跡: docs/research/ENDUSER-JA-CAPTION-TRIAL-01/(CURRENT_STATE_01/DESIGN_01/EVIDENCE_01/shots/verify_*.json/tools/)
(1)既存仕様整合: enduser_page_assets/rev01-h/app.js:25-56(jaHtml/ja_align),256-262(jaLight),304-308(selectSentence=再生・シークなし)を無変更で流用。追加はcapUpdateのみ。
(2)未承認機能の既定: Production経路には入らない(別dir user_test/enduser_caption_trial_01/のみ、Production asset/既公開dir無変更)。確認=git diffでrev01-h・既公開dir差分0。
(3)最終成果物: 成功終了。Trialページ6件+一覧(上記path)。ユーザー要求(再生中の日本語を本文下へ見に行かず確認できるかを実物で判断)に対し、実物を比較ON/OFF・現行リンク付きで提供。採否は未決(正式採用なし)。
(4)撤去・残置: 撤去した規則/検査なし。Grep: rev01-h配下と既公開dirに`jcap|capUpdate`は0件(Trial dirのみ)。
判定整合: 重大NG=なし
