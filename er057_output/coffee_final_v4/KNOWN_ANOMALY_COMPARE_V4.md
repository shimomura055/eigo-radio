# KNOWN_ANOMALY_COMPARE_V4 (v3既知の低レベル異音3件の新旧比較、local faster-whisper small + 検知器、生データ known_anomaly_compare_v4.json)
v4は全編再生成のため音声が別物(TTSは確率的)。v3の該当箇所と同一の語列(前後3語)をv4で探し、その位置のPart内検知結果を比較した。
| 箇所 | v3(検知器) | v4で対応する位置 | v4(検知器、±1.5秒) |
|---|---|---|---|
| Adv Part1 13.3s "When you see a price tag that makes you..." | click low(13.318) | 14.08s(price tag) | 検知なし。Part1の候補は level_step low 3件のみ(8.7/25.9/34.5s、別位置) |
| Adv Part3 39.85s "...do beans cost now, but also when does..." | click low(39.852、"now, but"間) | 41.4s(but) | 検知なし。Part3の候補は click low 2件(37.3/49.5s、別位置) |
| Std Part2 32.07s "at least about nine months to appear" | click low(32.07) | 34.4s(nine) | spec_jump low 1件(33.618s、at直前付近。click ではなく低confidence) |
新規異音: medium/high候補(非固定音源)は両Levelとも0件。low候補は Std 13件/Adv 12件(v3はそれぞれ非固定low中心)。v4の生成ログ(Primary ASR文)に "wanna" は0件。再生成は明確な異常がないため実施せず。
