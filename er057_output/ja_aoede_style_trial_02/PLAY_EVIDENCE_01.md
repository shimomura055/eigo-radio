# PLAY_EVIDENCE_01 (2026-10-12、Gate 7(a)〜(n))
- URL: https://shimomura055.github.io/eigo-radio/user_test/coffee_ja_style_trial_02/index.html (HTTP 200)
- 実測(`play_verify_01.py` → `play_evidence_01.json`): HTTP 全109件(index + mp3 108)200 / Playwright(headless Chromium)で audio 108/108 を実際にplay()し currentTime>0・paused=false・readyState>=3・error無し=全PASS / audio行すべて(108/108)に再生ボタン・Voice名(Aoede)・scriptが同一行 / audio最低幅360px / `file:///`・`C:\` 無し / A2・B1表示なし。
- (a)(b)(c)(d)(f)(g)(i): 本ページは部品比較Trial(完成episode・本文・Intro等は対象外と明記)。Preview/Comment全5件(b)(c)、KP日本語(e)は全件掲載。通しは単純連結(preview→comment_1..4、0.8秒pause)とKPコーナー(現行assemble順再現)で、click-seekはaudio個別行で代替。
- (e)(n): Key Phrasesは左=英語・右=日本語の2列table、`English:`/`日本語:`等ラベル文字列なし(label_strings_present=False)。
- (h): voice=Aoede(各行表示)。(j): 未取得segmentなし。(k): Standard同期(DEV Trial、Production既定=Batch)を明記。(l)(m): 上記のとおり。
