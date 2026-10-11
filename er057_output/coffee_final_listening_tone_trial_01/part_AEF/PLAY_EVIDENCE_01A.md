# PLAY_EVIDENCE_01A (Playwright headless Chromium、公開GitHub Pages)

- URL: https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/intro_preview_fullstory/index.html (HTTP 200)
- 実行: `play_evidence_01A.py`、生データ `play_evidence_01A_pages.json`、スクリーンショット `play_evidence_01A_pages_screenshot.png`
- 結果: audio要素39件中39件OK(loadedmetadata: duration>0、実再生でcurrentTime>0.3秒進行、play()例外なし)。HTTP 4xx/5xxなし、consoleエラー0件。
- combo通し再生(A3+B4選択): part_head→A3→part_mid→B4→part_tail の5部品が順に再生され「再生完了」到達。
- HTML内の `file:///`・`C:\`・`C:/`: なし。
- Gate 7 (a)〜(n) 到達状況: (a)実Episode冒頭構造=Intro→Welcome→Topic→JA title→通知音→Preview introの実順序・pauseで構成(本Trialは冒頭〜Preview導入、E/Fは対象segment単独のため「完成Episode全体」ではない=Trial範囲で明記) / (b)Advanced Preview=E0〜E5 / (c)Comment=対象外 / (d)本文=F(Part1冒頭段落のみ、既存全文Part1も併載) / (e)Key Phrase=対象外(委任_01B) / (f)Intro・通知音は読み上げなし(SFX)と明記、Welcome/Preview intro/Topic/JA titleのVoiceを明記 / (g)click-seek=各行のaudio controls(seek可) / (h)各行にVoice名 / (i)Level分離=Standard相当(6%減速)とAdvanced相当を別表で表示、A2/B1表記は使用せず / (j)未取得テキスト(既存Part1全文)は「未取得」と明記 / (k)TTS方式=Standard同期(Batchではない)を各行に明記 / (l)各音声と同一行にScript・Voice・説明・Prompt / (m)公開Pages URL / (n)Key Phrase表示=対象外、Level表示はStandard/Advanced。
