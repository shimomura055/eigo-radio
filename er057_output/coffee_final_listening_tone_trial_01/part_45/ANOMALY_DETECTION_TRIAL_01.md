# ANOMALY_DETECTION_TRIAL_01(委任_01C §5 Phase 2・3、無料ローカル解析、費用JPY 0)

管理ID: FAMILY-X-COFFEE-FINAL-LISTENING-TONE-TRIAL-01 委任_01C / 2026-10-11。DEV/Trial専用。Production Validator/Gate/Prompt/Routingは変更していない(検知スクリプトはProductionから参照されず、既存経路へ接続していない)。
スクリプト: `er057_audio_anomaly_detect_trial_01.py`(検知)・`er057_anomaly_page_build_01c.py`(ページ生成)・`part_45/whisper_words_01c.py`(local word timestamps)。使用: numpy 2.5.1 / scipy 1.18.0 / soundfile 0.14.0 / lameenc 1.8.4 / Pillow 12.3.0 / faster-whisper 1.2.1(`small`、CPU int8、`local_files_only=True`、ネットワーク・API不使用)。**有料API・LLM不使用**(最新モデル原則の対象外=モデル呼出なし。使用したASRはローカル小型whisperで検知用の補助信号のみ)。
候補一覧: `ANOMALY_CANDIDATES_01.md` / `.json`。確認ページ(Pages): https://shimomura055.github.io/eigo-radio/user_test/coffee_tone_trial_01/anomaly/index.html

## 1. Phase 2: 既存Audio QAとの重複確認(コードで列挙、worktree版/main版の該当関数)
| 既存の検査 | 場所 | 何を見るか | 本Trial検知器との関係 |
|---|---|---|---|
| segment指標 peak/RMS/clipping(`|x|>=0.999`の個数)/LUFS | `er002_common.measure_metrics` L1158-1175 | segment単位の峰値・クリップ個数 | **clip と重複**(clipは0.985以上が3連続=より早期、位置の時刻付き)。clip以外は未カバー |
| Headroom安全弁 | `er003_v1_n3_01_assemble.apply_headroom_safety_valve` L980-1017 | 完成ミックス峰値>0.98ならスカラー縮小、>1.0なら中止 | 全体peakのみ。位置・短いクリップは見ない(clipと一部重複) |
| 先頭/末尾無音のtrim | `er003_b1_p3u_audio.find_speech_bounds/trim_english_keyword_silence` L186-250 | 発話区間の前後の無音除去(安全マージン保持) | **edge_abruptと隣接**(trimは無音を削るだけで「語頭が急に始まる」は見ない)。内部の無音は見ない |
| 異常長音声(hallucination)検知 | `er003_audio_tts_asr_safety.detect_duration_anomaly` L189 | 文字数に対し長すぎる音声を破棄 | long_gapとは別(総尺のみ) |
| ASR一致判定(Primary/Secondary/cascade/意味等価) | `generate_narration_snippet_verified_strict`、`secondary_asr.*`、`classify_asr_match` | 転写と原稿の内容一致 | asr_mismatch/low_confの上位互換(本Trialは補助)。音響的異常(クリック・欠落・音量急変)は見ない |
| disfluency QA | `er008_disfluency_qa_18.py`(local faster-whisper small) | 短いsegmentの隣接同一語の繰り返し | 本Trialはword確率・原稿差分で別観点。繰り返しは本Trialでは見ない |
| Repetition QA | `er011_open121_repetition_qa_production_01.py` | ngram繰り返し+スペクトル長ラグ類似 | 別観点(繰り返し) |
| Audio Validation Gate | `er003_v1_n3_01_assemble.verify_episode_audio_validation_gate`(L470-)・`_segment_gate_status`・`_segment_missing_mandatory_a2_slowdown`・`_segment_missing_mandatory_disfluency_qa`・`_segment_asset_hash_stale`・構造完全性(OPEN-129) | status・減速・disfluency・sha・entry集合 | **音響的な異音は一切見ない**(ステータスと処理履歴の検査) |
**重複しない領域(本Trialの付加価値候補)**: click/pop・発話中の欠落・不自然な長い無音・語頭語末の急な開始・音量階段・位置付きの局所クリップ。既存QAは「ASRが読めるか」と「全体peak/処理履歴」が中心で、ASRが読めてしまう軽微な音響劣化(人間には異音に聞こえる)は検知できない設計。

## 2. Phase 3: 検知方式の全編適用結果
解析対象: Standard/Advanced 完成音声。segment wav 60本(計488.35秒、24kHz mono、`_original.wav`除く)+assembled(Standard 298.655秒/Advanced 291.26秒、48kHz stereo)+**公開mp3(episode 2本+segment mp3 41本、decode後同じ検知器)**。

### 2-1 候補数と信頼度(`ANOMALY_CANDIDATES_01.json` 集計)
| 対象 | 時間 | 音響系候補(clip/click/dropout/long_gap/edge/level_step/spec_jump) | うち high / medium | 候補/分 | ASR系候補(low_conf/mismatch、英語のみ) |
|---|---|---|---|---|---|
| segment wav(両level) | 488.35秒(8.14分) | 24 | 1 / 2 | 2.95 | 35(うち数詞shell `num_*` 10は信頼度が低い短語で参考外) |
| assembled(固定音源を除く) | 589.9秒(両level合計9.83分) | 20 | 0 / 0 | 2.03 | - |
| assembled 固定音源(Intro/Notification/Outro) | 同上に含む | 17(同一素材の繰り返し、固定mp3の既知特性) | 0 / 6(click medium) | - | - |
| 公開mp3(episode+segment) | 約18.3分 | wav解析とほぼ同じ分布(clip 0、high 1=segment mp3のkp3_en先頭click、新規のhigh/mediumなし) | 1 / 2 | - | - |
- **確定**: clip(音割れ)は両levelとも0件(segment最大peak 0.70、assembled peak Standard 0.9504・Advanced 0.9203。headroom安全弁は両level未適用)。発話中の欠落(dropout)は**0件**。語頭語末の急な開始(edge_abrupt)も0件。
- **確定**: 厳密な0(デジタル無音)区間は segment 内に計33か所(≥4ms)あるが、すべて前後が減衰しきった自然なポーズ(前後5msのRMSが発話p95より-55〜-87dB)で、「発話レベルから急に欠落」型(`DROPOUT_ABRUPT_DB=-30`)は0件。この区別をしないと誤検知が約33件になる(初期版は発話内0区間を全て欠落とみなし segment 33件+assembled 188件を誤検知した。改良後0件)。
- **確定(medium以上のsegment候補3件)**: Standard `kp3_en` 0.214秒(high、ratio 107.6、`Take`の語頭 /t/ の破裂。自然な破裂音の可能性が高い)/ Standard `full_story_part2` 40.94秒(medium、ratio 81.1、abs_d2 0.087。ローカルwhisperで `raw beans`→`robbings` と転写された語の位置)/ Advanced `full_story_part1` 12.82秒(medium、`tag that`付近)。
- **確定**: 公開mp3でも新たな音割れ・欠落は出ない(mp3化由来の劣化は検知されず)。

### 2-2 positive control(既知の異常を注入した感度評価。`ANOMALY_CANDIDATES_01.json` の `injection_test`、Standard part3 24kHz mono 48秒の正常音声に注入)
| 異常 | 条件 | 結果 |
|---|---|---|
| clip | 400msを×8・×3倍しクリップ | 2/2 検出(high) |
| click | 1サンプル 振幅0.5 / 0.3 | 検出(medium〜low) |
| click | 1サンプル 0.2 / 0.1 | **未検出**(局所の通常の高周波と区別不能) |
| click | 3サンプル 0.2 | 検出(high) |
| dropout | 0区間 30ms / 10ms / 5ms(発話中) | 3/3 検出(high) |
| level_step | 以降を-12 / -9 / -6dB | 3/3 検出(low信頼度) |
| level_step | +4dB | 判定不能(この試験の増幅でpeak>1となりclipとして別検出されたため) |
| noise burst | 40ms白色雑音(発話p95-20dB / -10dB) | **0/2 未検出**(spec_jumpは感度不足) |
| 途中の無音 | 1.2秒 / 0.5秒 挿入 | 2/2 検出(long_gap+dropout) |
| 末尾の急な切れ | 40秒位置で切断 | 検出(edge_abrupt medium) |
| 語頭の欠落 | 語頭60ms目から開始 | 検出(edge_abrupt medium) |
**注入19ケース(+4dB除く)中15検出(約79%)**。得意=clip・欠落・挿入無音・切断・階段状音量。苦手=微小な単サンプルクリック、広帯域ノイズバースト、発話と区別しにくい微小グリッチ。確定的な異音の検知率保証はできない(注入は人工、実際のTTS不具合の分布とは異なる)。

### 2-3 既知/重点異常の検出可否
- **重点: Standard Full Story Part 3「A coffee price tag may have its own hidden clock」の coffee 付近(ユーザー報告)**: ローカルwhisper(small)のword timestampで coffee = **43.30〜43.56秒(segment内)/ episode 265.45〜265.71秒**(確定。確認ページ FOCUS-STD-P3-coffee)。検知器は±1.0秒以内に候補を出さなかった(**未検出**)。coffee語の窓指標(peak 0.542、max|d2|ratio 8.5、HF比 0.002、窓内最小10msRMS -55dB、ゼロサンプル168)は、同記事の他の coffee 9箇所(peak 0.395〜0.683、ratio 5.4〜9.7、HF比 0.0009〜0.0095)の範囲内で、特異ではない。直前に0.47秒の段落ポーズ、「A」(約60ms)→coffee の間に約40msの無音(/k/破裂前の閉鎖と整合)、coffee→price 間に約20msの無音(/p/閉鎖)がある。これらは自然な子音閉鎖と区別できず異常とは言えない。最も近い候補は **1.82秒後の `hidden`→whisper `hitting`(asr_mismatch_word、episode 267.27秒、whisper確率0.76)**。「coffee」付近で聞こえる違和感が `hidden` の不明瞭さなのか、coffee そのものなのかは**人間試聴で判断が必要**(FOCUSクリップは coffee の前後2.5秒で、`hidden`(coffeeの約1.7秒後)まで含む。STD一覧の asr_mismatch_word「hidden→hitting」行にも個別クリップあり)。
- **既知: Standard part2 の Azure NG 語(`raw bean`→`Robbing`、`raw beans`→`Robbins`、COFFEE_NG_ROOTCAUSE_01)**: ローカルwhisper(small)も `robbing`/`robbings` と転写(asr_mismatch_word 2件、30.22秒・41.07秒)し、両位置の±0.2秒以内に click 候補(40.94秒medium、30.34秒low)も出た。ただし /b/ の語頭破裂は自然な破裂音の可能性があり、**異音の確定ではない**(Advancedの `raw bean(s)` には click 候補なし、whisper も正しく転写)。
- 確定済み異常: 無し(ユーザー確認前)。

### 2-4 誤検知率・追加費用・処理時間
- 誤検知率(=確定異常が無い前提の候補/総時間): segment音響系 2.95件/分(medium以上 0.37件/分)、assembled(固定音源除く)2.03件/分(両levelの重複を含む)。感度とのトレードオフ: level_stepの窓を1.2秒・差10dBにした設定は 1.23件/分(窓0.4秒だと7.6件/分に増え、注入の-6dB階段は検出できない)。spec_jumpは z>=8 で 0.37件/分だが注入ノイズ0/5検出(感度不足)。→ spec_jump は有用性が低い。
- 追加費用: **JPY 0**(API・LLM不使用)。
- 処理時間: 検知器 全segment+assembled+公開mp3 で約8.8秒(CPU、全体で実時間の約1/100)。local whisper(small、CPU int8)は音声488秒に対し185秒(約0.38倍)で、これは任意(ASR系候補・近傍語表示用)。
- 検知結果の再現性: 同一入力・同一閾値で決定論的(スクリプトにseedは注入ノイズのみ、固定7)。

### 2-5 Validator組込み価値の評価(提案のみ、採否はユーザー/Fable判断。本Trialでは組み込んでいない)
- **価値あり(音響系・高信頼度のみ)**: clip(0.985以上3連続)、発話中の急な欠落(abrupt dropout)、語頭/語末の急な開始・切れ、挿入無音の長大化。いずれも既存QAでは検知されず(ASRは読めてしまう)、注入評価で検出でき、実Coffee音声では誤検知0件。**非ブロッキングの警告(Human Review用の候補ログ)として組み込む**案が妥当(ブロックにすると自然な破裂音等の誤検知で正常音声を止めるリスク)。
- **価値が限定的**: click(低信頼度は自然な破裂音と区別しにくい、約2.1件/分の確認負荷)・level_step(自然な語尾減衰と区別しにくい)・spec_jump(感度不足)・ASR系word確率(既存のASR判定と二重)。単独でGateにするのは不適切。
- **注意(重要)**: 検知器は「異音の存在を断定」するものではなく、ユーザーが指摘した coffee 付近の違和感は本方式では**検出できなかった**。人間試聴の代替にはならない。
- 本Trialの `er057_audio_anomaly_detect_trial_01.py` はProductionへ配線されておらず、組込みには別途 Opus独立レビュー(条件A)・ユーザー承認が必要(`APPROVED_FOR_PRODUCTION` ではない)。

## 3. 制約・限界
- 異常の「正解」ラベルが無い(ユーザー試聴前)ため、precision/recallは注入試験(recall)と候補数(誤検知率の上限指標)のみ。
- local whisper(small)の転写・word確率は補助信号。Production ASRとは別系統で、誤認のある語(`robbing`)は音声自体が曖昧か転写誤りかを区別しない。
- 公開mp3の `episode.mp3` が 委任_09 時点のものであることを前提(解析時点の `user_test/coffee_new_tone_01/*/web/` を使用)。
