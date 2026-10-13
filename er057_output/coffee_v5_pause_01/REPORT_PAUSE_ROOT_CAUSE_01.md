# REPORT_PAUSE_ROOT_CAUSE_01 (FAMILY-X-COFFEE-V5-PAUSE-ROOT-CAUSE-01 委任_01、2026-10-13、オフライン測定・費用JPY0・Production不変)
測定手法: local faster-whisper small(費用0)で語timestamp取得 -> 原稿(`tts_input_texts.json`、Std 37文/Adv 28文)の文末tokenをdifflib整列でASR語へ写像(ASR句読点に依存しない、全文末を写像) -> 文末語の終端〜次語開始(±0.25s)に重なる無音run(RMS<-40dBFS、10msフレーム、最小50ms)の長さを文末後ポーズとした。各Partの最終文(ファイル末)は除外(Adv 25境界/Std 34境界)。感度(-35/-45dBFS)は`sentence_end_pause_stats.json`。モデル: 本測定にTTS/LLM呼出なし(音声は全て既存、TTS=gemini-3.8-flash-lite-tts)。

## 1. 音声の由来(全て原稿tts_input sha256 = 同一: Part1 627f1c7f / Part2 1eebc297 / Part3 677de141 [Adv]、Std 13740eca / ebeffd9e / 93624443)
| 版 | Full Story音声 | 生成日時(JST) | style sha(先頭12) | 減速 | 経路 | wav sha(Part1/2/3先頭12) |
|---|---|---|---|---|---|---|
| PD8 Trial(pace_trial_02) | Adv Part1-3 | 2026-10-12 10:41 | 329ff46a5ec3(PD8、「Warm...never flat or sleepy.」のみ) | なし | Trial(`er057_pace_trial_02_gen.py`、Standard sync DEV) | b20b1208 / b00c1234 / a148fd7d |
| v3 Adv | PD8の**再利用**(provenance origin=T) | (同上) | 329ff46a | なし | Trial assembler | 同上 |
| v3 Std | PD8+6%減速 | - | 329ff46a | 6% | Trial | e9c2685d / 4734c08b / a3909766 |
| v4 / **v5** Adv | **v4で新規生成**(origin=R、v5は流用) | 2026-10-12 15:12 | **3eadf4f6f788**(P8 = PD8 + 追加3文: "Let the pitch rise and fall a little more on key words. Add a touch more brightness and a hint of a smile in the voice, while staying unhurried. Articulate crisply: ...") | なし | Trial(`er057_coffee_final_v4_gen_01.py`、Standard sync DEV、**v5 Production runnerは未経由**) | 8b616edc / c79194e1 / f8831096 |
| v4 / **v5** Std | v4で新規生成+6%減速 | 2026-10-12 15:12 | 3eadf4f6f788 | 6%(atempo、実5.96-5.99%) | 同上 | 6546b00f / dd032240 / cb3c33166(slow6) |
| F5(final_v2) | 新規生成 | 2026-10-12 07:23 | 9228209bec75(F5「warm, gently upbeat...not hurried.」) | Stdのみ6% | Trial | 5b711b91 / 2d7c291b / fa1f978f |
全てmodel_version=gemini-3.8-flash-lite-tts(応答実測)、voice=Aoede、speech_metadata方式。出典: generation_log_02.jsonl / generation_log_v4.jsonl / generation_log_03.jsonl / 各assembly_manifest provenance。
**確定: v5のFull Story音声はPD8 Trial takeの再利用ではない。** v3 Advのみ再利用で、v4で`P8`(PD8本文+3文追加の別Prompt)により6本とも新規生成、v5はそれをsha一致で流用(Std/Adv Full Story 6本とも不変)。Fableの過去説明「v5のFull Story音声はTrialと同一take」は **v3 Advまでは正、v4/v5には誤り**(別take・別Prompt)。v5でruntime生成されたのはStd Preview/Comment1-4(R2)とAdv KP解説(P3)のみ。

## 2. 文末無音(ms、-40dBFS、最小50ms)
| 音声 | 文末数 | 平均 | 中央 | 最大 | 文末無音合計(s)/尺(s) 比率 | 分布 [<150 / 150-300 / 300-500 / 500-800 / 800-1200 / >=1200] |
|---|---|---|---|---|---|---|
| v5=v4 Adv(P8新take) | 25 | **475** | 470 | 740 | 11.87/153.4 = 7.7% | 1 / 2 / 12 / 10 / 0 / 0 |
| PD8 Trial take(=v3 Adv) | 25 | **490** | 490 | 750 | 12.26/151.3 = 8.1% | 0 / 0 / 14 / 11 / 0 / 0 |
| F5 Adv(final_v2) | 25 | 438 | 430 | 710 | 10.94/132.9 = 8.2% | 0 / 6 / 9 / 10 / 0 / 0 |
| v5=v4 Std(6%減速後、聴感) | 34 | **525** | 505 | 1050 | 17.85/152.4 = 11.7% | 1 / 3 / 13 / 12 / 5 / 0 |
| (v5 Std減速前相当 = 実測raw / 実測/1.06) | 34 | 498 / 495 | 485 / 476 | 970 / 991 | - | raw: 1 / 4 / 12 / 13 / 4 / 0 |
| v3 Std(PD8+6%) | 34 | 622 | 595 | 1060 | 21.14/148.9 = 14.2% | 0 / 0 / 6 / 25 / 3 / 0 |
| F5 Std(slow6) | 34 | 517 | 515 | 820 | 17.58/136.4 = 12.9% | 0 / 3 / 12 / 18 / 1 / 0 |
Part別平均: v5 Adv 456/496/460、PD8 483/437/581、F5 Adv 440/409/480; v5 Std 694/399/473(Part1に800ms以上4件: 'too.'1000、'continue.'1050、'delay.'910、'away.'820)、v3 Std 670/633/550、F5 Std 496/537/519。
v4完成版 = v5と同一wav(Full Story 6本とも sha一致)のため上表のv5と同値。音声ファイル内の間(上表)と Assembly の間(下記3)は別。Std 6%減速の寄与: 文末無音は+6%(平均で約+30ms)に過ぎない。
文末以外の語間無音(>=50ms、文末に対応しないrun)の本数/合計: v5 Adv 172本/17.6s、PD8 169本/17.6s、F5 Adv 110本/10.0s; v5 Std 150本/13.3s、F5 Std 106本/9.0s。→ **P8/PD8系(unhurried)はF5より文中の小さな無音が約+55%多い**(文末無音自体はほぼ同等)。

## 3. Assembly(segment間)の間: 全版で同一
timeline pauseは v3/v4/v5/F5 の Std・Adv ともに同値(Adv: 0.5/0.65/0.4/0.65/0.5/0.4/0.5/0.4/0.8x9、Std: 同+1.0(EN->JA)/0.8(JA->EN)/0.5)。最終wav上の実効gap(timeline pause位置の無音run実測)は pause + 各clipの先頭/末尾無音(lead 0.2-0.4s、trail 0.2-0.5s)で、Comment<->Full Story間 Adv 1.29-1.43s、Std 1.29-1.62s、全版で差は最大0.16s(v5 vs F5: Adv平均1347 vs 1355ms、Std 1360 vs 1364ms)。`segment_silence_and_effective_gaps.json`。**Assemblyは原因ではない**(ただしsegment間は約1.3-1.6sあり、これ自体が長い可能性は別途ユーザー判断)。
Std Preview/Comment(R2 vs v4 P2): 内部無音合計 preview 2.18 vs 2.40s、comment1 0.26 vs 0.73、comment2 2.45 vs 2.46、comment3 2.56 vs 2.18、comment4 2.92 vs 2.54s(comment4は文章も変更)。Adv KP解説(P3 vs P0)は内部無音が減少(kp1 0.30 vs 0.44s等)。R2/P3は間を増やしていない。

## 4. 条件差分(Full Story)
| 項目 | PD8 | v4=v5 | F5 |
|---|---|---|---|
| TTS Prompt | PD8本文(1文) | P8(PD8+3文、「smile」「Articulate crisply」等) | F5 |
| モデル/voice | gemini-3.8-flash-lite-tts / Aoede | 同 | 同 |
| 原稿 | tts_input sha一致(単一行、段落/改行0、句読点同一) | 同一 | 同一(`tts_safe_news_en`適用) |
| speech_metadata/実行方式 | speech_metadata_flash_lite、Standard sync DEV | 同 | 同 |
| 話速指示 | unhurried | unhurried(2回) | not hurried |
| 後処理 | なし(Adv) | Std: atempo 6%、Adv: なし。音量: 全体RMS基準+headroom(v5 Adv safety valve発動 約-0.6dB、Std未発動) | Std 6% |
| Assembly | pause同一 | 同一 | 同一 |
原稿コピー差: v5原稿(`er019_output/coffee_prices/run_v5_ms_01`)は v4(Tone由来)コピーで、Full Story音声は原稿からではなく`tone_trial parts.json`起点のtts_inputをv4が生成(sha一致で同一確認)。OPEN-326の既述通り原稿の正本は未決。

## 5. 承認済み仕様の適用
Full Story: P8(3eadf4f6、承認A=Coffee Full Story専用)がv4生成で逐語送信(generation_log_v4 style_sha256一致)、6%減速(Std)適用済み。v5 runnerでは Full Story はroleが`FULL_STORY=P8`でprofile解決できるが**v5では未実行(v4音声流用)**(STYLE_APPLICATION_EVIDENCE_V5、WIRING_CHECKLIST #3/#19)。Std R2/Adv P3はruntime発火済み。逸脱・実装バグは検出なし。

## 6. 原因分類と判断
- 仕様未反映: 該当せず。実装バグ: 該当せず(Assembly同一、Style逐語一致)。後処理: Std 6%減速で文末無音は+約6%のみ、主因ではない。
- **TTS生成差(同一Style・同一原稿の別take間のばらつき)が測定で確認できた**: Adv v5 take vs PD8 take(文面は同一、Promptは3文差)で文ごとの文末無音の差 SD=194ms・平均差-16ms・相関r=0.08(n=25、最大差480ms)、Std v5 vs v3(同一原稿、P8新take vs PD8 take、共に6%)で SD=195ms・平均差-97ms・相関0.55(n=34)。つまり**文単位の間の長短はtakeごとにほぼ独立に揺れ**、平均水準はv5/PD8/F5で有意差が出ない(v5 Adv 475 vs PD8 490 vs F5 438、感度-35/-45dBFSでも順序同じ)。
- したがって「v5がPace Trial 02(PD8)より文末の間が長い」は文末無音の測定では**裏付けられない**。v5 Std Part1に800ms以上が4件ある(take固有、F5 Std最大820、v3 Std最大1060)。v5 Std/Adv の聴感上の長い間の候補は、(a) 文中の小無音が多い(語間+55%、P8/PD8共通の「unhurried」影響)、(b) Std Part1のtake固有の長い文末(1000/1050ms)、(c) segment間実効gap約1.3-1.6s(全版同一)、(d) WPM低下(Std v5 162.2、Adv 180.7)。この中で測定が示すのは(a)(b)(c)で、因果の強さは聴感確認が必要。

## 7. 是正案(未実施・新Style/ポーズ基準のためUSER_DECISION_REQUIRED、Production実装禁止)
| 案 | 内容 | 影響(v5実測で試算) | 費用 |
|---|---|---|---|
| A 後処理: 文末超長無音のキャップ | 文末無音を上限Xmsへ短縮(音声DSP、TTS不要) | X=600: Adv 6文/-0.58s、Std 13文/-2.08s; X=700: Adv 2文/-0.07s、Std 6文/-1.22s; X=500: Adv 10文/-1.44s、Std 17文/-3.63s | JPY0(offline) |
| B 後処理: segment先頭/末尾無音trim | lead/trailを例えば100msへ(実効gap 約1.3-1.6s -> 約0.9-1.1s想定) | 全segment境界で約-0.4-0.5s | JPY0(offline) |
| C Prompt: 'unhurried'二重表現を緩和(例 1回のみ/"relaxed but flowing") | P8の2文目"while staying unhurried"削除等でtake傾向を変える | takeばらつき(SD約190ms)が大きく、単回比較では判定不能 | 6 call(Part1-3 x Std/Adv)で TTS約JPY7+ASR約JPY1.5=約9/候補、3候補約27 |
推奨: まずA/B(JPY0、ユーザー試聴Trial)。Cはtakeばらつきが大きいため、複数take(N>=3/条件)が要り費用対効果は低い。
