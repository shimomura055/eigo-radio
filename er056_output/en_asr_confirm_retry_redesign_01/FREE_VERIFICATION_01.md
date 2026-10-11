# FREE_VERIFICATION_01 — 無料検証(保存済み音声・ASR転写・既存Validatorのみ。有料API 0)

管理ID: FAMILY-X-EN-ASR-CONFIRM-RETRY-REDESIGN-01 委任_01 / 2026-10-11
使用したもの: (a) 既存JSON(attempt記録・`tts_generation_results.json`・`review_lock_state.json`・queue・telemetry・`raw_usage_log.jsonl`)、(b) 既存Validator `classify_asr_match` の**純関数呼び出し**、(c) ローカル faster-whisper(small/medium、CPU、無料)、(d) ffmpeg(6%減速の再現、無料)。**OpenAI/Azure/Gemini/LLMは一切呼んでいない。**
スクリプト(read-only): `er056_en_asr_retry_replay_01.py`(collect / qcd / scenarios / mutations / local / medium)、`er056_en_asr_local_wav_check_01.py`。結果JSON: 本ディレクトリの `replay_results_01.json`、`qcd_model_01.json`、`qcd_scenarios_01.json`、`mutation_safety_01.json`、`local_wav_check_01.json`、`local_proxy_results_01.json`、`local_proxy_medium_followup_01.json`。
**重要な限界**: 真の音声の正解ラベル(人間が聴いてどう聞こえるか)はない。ローカルASRやValidatorは「第三の系統の意見」であり、人間試聴の代替ではない。

## 4-1. Coffee 各 attempt の Primary/Secondary 判定の再現(Validator再実行)
`classify_asr_match(canonical=tts_input, asr_text, segment_id="full_story_part2")` を attempt json の転写へ適用(canonicalは `a2_parts.json` の `part2` を `tts_safe_news_en` に通したもの)。
| 音声 | step | 記録された分類 | 再現した分類 | diff(原稿→ASR) |
|---|---|---|---|---|
| 初回(15:13) | primary_1 | NORMALIZED_MATCH | NORMALIZED_MATCH | なし |
| 標準1回目(15:16) | primary_1 | TRUE_CONTENT_MISMATCH | TRUE_CONTENT_MISMATCH (0.9607) | `showed→show`(非entity)、`us→u s`×3(entity-like)。`cost→costs`は benign plural で無視 |
| 標準2回目(15:18) | primary_1 / primary_2 | ASR_VALIDATION_UNCERTAIN ×2 | UNCERTAIN ×2 (0.9668) | `us→u s`×3 のみ(`entity_like_source=capitalized`) |
| 標準2回目 | secondary_1 / secondary_2 (Azure) | TRUE_CONTENT_MISMATCH ×2 | TCM ×2 (0.9695) | `raw bean→robbing`、`appear→(脱落)`、`us→u s` |
| fallback(15:31) | primary | (json は Azure forced の分類) | NUMERIC_EQUIVALENCE_MATCH (PASS) | なし(段落改行のみ) |
**全ての記録済み分類を再現できた**(Validator不具合・記録不整合は検出されず)。偽NGの原因は Validator の仕様どおりの挙動(F-5)と Azure の転写。
**F-5 の合成再現**(`mutation_safety_01.json`): 原稿の `US data`→`U.S. data` のみ = `NUMERIC_EQUIVALENCE_MATCH`(PASS)、`cost→costs` のみ = `HIGH_SIMILARITY_SAFE`(PASS)、**両方同時 = `ASR_VALIDATION_UNCERTAIN`(NG、Coffee標準2回目と同一パターン)**。2つの軽微な差の同時発生で despace 等価が崩れ、`US`↔`U.S.` が entity-like 扱いになる。

## 4-2. 保存音声のローカル独立ASR再転写(Secondary候補・第三の系統)と6%減速の再現
`local_wav_check_01.json`(faster-whisper segment text、`U .S.`→`U.S.` の分かち書きのみ整形)。
| 音声 | OpenAI Primary | Azure | local small | local medium |
|---|---|---|---|---|
| 初回 | PASS | (未実施) | NORMALIZED_MATCH | UNCERTAIN(`People`脱落 + `U.S.`) |
| 初回を6%減速(**ffmpeg再現**、実測5.977%、50.32→53.33秒) | **UNCERTAIN(実run、本文は未保存)** | — | NUMERIC_EQUIVALENCE_MATCH | UNCERTAIN(`People`脱落 + `U.S.`) |
| 標準1回目 | TCM(`show coffee costs`) | (未実施) | **NORMALIZED_MATCH(`showed coffee cost`)** | **NORMALIZED_MATCH** |
| 標準2回目 | UNCERTAIN | TCM(`robbing`) | **NORMALIZED_MATCH** | **NORMALIZED_MATCH** |
| fallback | PASS | TCM(forced、転写欠落) | **NORMALIZED_MATCH** | **NORMALIZED_MATCH** |
| LR最終(`data from the United States`、`raw-bean`) | PASS | TCM(`Robbing/Robbins`) | **TCM(`robbing`/`robbings`)** | NORMALIZED_MATCH |
読み取り: (1) 6%減速自体は内容を壊さない(減速音声を local small は PASS)。(2) 標準1・2回目・fallback の3音声は、独立した2モデルとも原稿一致=**偽NGだった可能性が高い**。(3) LR音声は 2/4 系統(Azure・local small)が `robbing` と聴き、**本物の発音曖昧さの可能性**を否定できない。(4) local medium でも `People` 脱落のような**局所脱落**が出る=ローカルASR単独を最終権威にはできない。

## 4-3. 過去のattempt記録からの再計算(narrative5 = Full Story/Comment/Preview/Topic intro/In One Line)
入力: Flash-Lite期(2026-09-27〜、model=gemini-3.8-flash-lite-tts。fallback route は main では model を 2.5-pro と誤記録し tts_backend も保存しないため、同一ディレクトリに Flash-Lite 標準attemptがあるものを含めた)の英語attempt記録421件+Coffee snapshot → 332 call(同一segment・`loop_attempt_index==1`で区切る)。うち narrative5 = 160 call。**注意: データには A/B Trial(`tts_gemini_3_8_flash_lite_ab_trial_01/b` 等)・回帰テスト由来が混在**し、Production実runのみではない。
| 指標 | narrative5(n=160) | OTHER(n=172: Key Phrase 77、共有殻 num_* 47、見出し/導入 ほか) |
|---|---|---|
| 1回目で合格 | 134 (83.8%) | 135 (78.5%) |
| 2回目で合格 | 13 | 8 |
| 3回目で合格 | 2 | 6 |
| 未合格 | 11 (6.9%) | 23 (13.4%) |
OTHER の内訳: **Key Phrase 77 call = 74 が1回目合格(96%)、2回目2、未合格1** → 現行構成のまま十分(対象外維持の根拠)。**共有殻 num_* 47 call = 17 が未合格(36%)** → OPEN-222(極短語の言語ドリフト)で、Secondary確認では救えない(TTS側の問題)。
narrative5 のNG attempt 41行の種別(Validatorで再現できたもの): 内容語差(非entity) 10 / entityのみ 3 / 数値・否定 4 / 低類似度 1 / **再判定ではPASS 6**(分類はPASS系なのに `verified=False`=長さ・Repetition QA・Disfluency QA 等のASR以外のgate、または Validator 更新後に合格化)/ 原稿・転写が復元不能 17。
**新方式での完成率(下限/上限)**: 現行 149/160 (93.1%) → 下限 147 (91.9%) / 上限 153 (95.6%)(定義は QCD §(7))。narrative5 の未合格11 callの内訳: **A/B Trial arm(`ab_trial_01/b`)由来6**(point_one/two・full_story_part1/2・in_one_line、うち5はfallback混在=Prompt不整合のデータ)、Production系5(hormuz Full Story part1 は**数値・否定差が3回連続**=本物のTTS読み違いの可能性が高く新方式でもHR、meta comment_2 は entity-only で1回目にcascade `stop_retrying`、meta in_one_line ×2 は内容語UNCERTAINで1回目に打切り=**新方式なら3回目まで継続+Secondary確認の対象**、Coffee part2)。上限と下限の差6件は Secondary 救済対象型の未合格call。

## 4-4. Cascade / Local Rewrite / cool-down の過去実績
- **Cascade発火後の結果**(英語attempt記録1,601件中、`primary_2` 以降まで進んだ23件): 救済 **8**(`secondary_1` で NORMALIZED 6、`primary_2` で HIGH_SIMILARITY_SAFE 1、Tier3 corroboration 1)/ 不救済 **15**(4step全て UNCERTAIN 12、Secondary が TCM 3)。→ **entity/homophone 型 UNCERTAIN での Secondary 救済率は 35%(8/23)**。
- **Local Rewrite 実績**(`er011_output/local_rewrite_recovery` 18記録): RESOLVED_BY_LOCAL_REWRITE **8**(comment_4×3、preview、full_story_part1/2/3 各1、in_one_line)/ 再TTS不合格 7 / 候補なし(7 Gate不通過)3。+Coffee(worktree)で comment_2 が RESOLVED、part2 が不合格。→ LR成功率 約47% だが、**新方式では自動発火しない**ため、この約8件はSecondary/再生成で救われなければHR化する(未測定=リスクR-6)。
- **cool-down→3回目**(`cooldown_events` を持つ10 segment): 3回目(標準)で合格 3(family_x_b3 の full_story_part1×2、comment_4)/ fallback合格 1(meta part3)/ LR救済 4 / 不合格 2(b3 part2、Coffee part2)。標準3回目が通った3件は**同一Prompt**(B1B)。→ **同一Promptの再試行でも通る**ことの実例(新方式の前提を支持)。cool-down自体の効果は対照がなく**未確定**。

## 4-5. 人間レビューqueue 67行(全期間、`human_review_queue.jsonl`)の Secondary 挙動
| cascade step 列 | 行数 |
|---|---|
| P1 UNC → P2 UNC → S1 TCM → S2 TCM | 26 |
| P1 UNC → P2 UNC → S1 UNC → S2 UNC | 23 |
| P1 NORMALIZED → **secondary_forced TCM** | 5(重複除き4) |
| Tier3 経由 + 上記パターン | 5+4+3 |
| その他 | 1 |
- Secondary(Azure)が TCM を返した行は 34(全体の51%)。Azure diff の上位: `''→two`(22: 数詞を挿入)、`elle→l`(18)、人名の綴り崩れ(`gruen→grune/grun`、`l mimoun→el mimoon` ほか)、`u s→us`(6)、`m→am`(6)。
- **forced-Secondary(Primary PASS・Azure NG)4件**: `sweets→suites`/`deviations→dev`、`dates→states`+`m→am`、`move→(脱落)`、`money→(脱落)`。Primary が PASS している以上、**Azure側の誤認識・脱落・表記差がほとんど**に見える(人間聴取は未実施)。
→ Azure を「最終権威」にする forced / TCM 確認は偽NGを生みやすい。Azure を **PASS側の救済にのみ**使う目標設計は妥当だが、救済率は低い(上記 35%)。

## 4-6. 英語ASR NG の種別分布(`er021_output/.../telemetry.jsonl`、5,067行 = ユニーク255組)
| sub_reason | ユニーク組 |
|---|---|
| content_word(非entity内容語差) | 87 |
| protected_number | 79 |
| entity_only | 73 |
| low_ratio | 7 |
| plural_only | 5 |
| protected_negation | 3 |
| homophone_only | 1 |
(Trial/テスト再生を含む。Primary NG のうち **数値・否定は 82/255 = 32%**=Secondaryを呼ばず再生成する対象。内容語差 34%、entity 29% が Secondary 確認の主対象。)

## 4-7. 誤PASS防止の合成テスト(`mutation_safety_01.json`)
Secondary転写に見立てた合成テキスト(Coffee part2 原稿に1箇所ずつ変異)を `classify_asr_match` に通し、厳格PASS集合(EXACT/NORMALIZED/TRANSCRIPT_STYLE_NORMALIZED/NUMERIC_EQUIVALENCE)で受理されるかを確認。
- **真の内容誤り 16種 → 誤PASS 0/16**: 数値(6.1→6.7、9→10 months、2→3 numbers)、否定(does not→does、does not→did not)、時制(showed→show、spoke→speak)、重要語(raw省略、raw beans→Robbins、fall→rise、at least→at most)、entity(Reuters→Router=UNCERTAIN)、文末脱落・幻覚追加文・文反復・中間文脱落。
- benign 7種 → 5種を受理(US→U.S.、Don't→Do not、nine↔9、two↔2、raw-bean↔raw bean)。受理されない2種: `cost→costs` 単独(`HIGH_SIMILARITY_SAFE`、厳格集合外=D-3)と、Coffee標準2パターン(`US→U.S.`+`cost→costs` = UNCERTAIN)。
限界: Secondary **ASR自身が**原稿へ補正する性質は含まない(§4-8、QCD §(5) R-1)。

## 4-8. ローカルASR代理検証(Primary NG・Primary PASS対照)
`local_proxy_results_01.json`(small、60本=NG20+Primary PASS対照40。NGはValidatorで再現できた保存音声)。
| Primary側の種別 | 本数 | local small も NG | local small は原稿一致 |
|---|---|---|---|
| 数値・否定(真の誤りと推定) | 4 | **4** | 0 |
| entityのみ | 5 | 5 | 0 |
| 非entity内容語差 | 7 | 4 | **3** |
| 低類似度(UNCERTAIN) | 1 | 0 | 1 |
| Primary再判定でPASS(ASR以外のgate等) | 3 | 1 | 2 |
| Primary PASS対照(良品の標本) | 40 | **13**(32.5%) | 27 |
読み取り: (1) 数値・否定の真誤りは独立ASRでも救済されない=設計の除外条件と整合(自動補正は観測されず、n=4)。(2) entityのみは0/5=固有名詞は独立ASRでも救えにくい(OPEN-257と整合)。(3) 内容語差型は3/7が独立ASRで原稿一致=**救済余地は主にここ**。(4) **良品の32.5%を small が NG にする**=smallは精度不足で最終権威にできない(Primary誤PASS率の推定値ではない)。
**medium追試結果(local_proxy_medium_followup_01.json、費用0)**

- Primary PASS対照13件(smallでNG判定): mediumでもTRUE_CONTENT_MISMATCH 11件、TTS_FAILURE相当1件、NORMALIZED_MATCH 1件。
  不一致の主因は、数値表記(11.04等の小数)・U.S.の分割・raised/raise・oil/oiledなどの表記/活用差と、canonical結合の精度限界が混在する。small側の精度限界だけではない。
- 内容語NG(Primary NG)側: mediumは、NORMALIZED 2件(full_story_part1)・CONNECTED_SPEECH_ACCEPT 1件(comment_3)・EXACT 1件(preview、Primary低類似度)をrescueした。part3はUNCERTAIN、fallback attempt3(full_story_part2)はTRUE_CONTENT_MISMATCHのまま。
- 注意: 対照は複数runの寄せ集めでcanonical結合の精度も限定的なため、Primary false-PASS率の推定値としては使えない。ローカルASRは参考指標であり、Primary/Secondaryの代替ではない。


## 4-9. 特殊条件・手順上の確認(コード読解+上記データ)
| 条件 | 確認結果 |
|---|---|
| Primary ASR障害(転写None) | 現行は `TTS_FAILURE` 扱い(val:966-968)で音声不良と区別されず再生成。新方式はASR技術再試行を提案(TARGET §3-9) |
| Secondary障害/タイムアウト | 現行 `get_full_text_via_azure_stt_with_phrase_list` は error を返す。SCGは UNAVAILABLE=NG扱い。同様に設計 |
| TTS技術的失敗 | B1B は同attempt内に別Prompt fallback(F-8)。新方式は同一Prompt再試行 |
| Key Phrase | 現行4回構成で96%が1回目合格 → 変更不要 |
| 共有殻 num_* | 36%未合格、OPEN-222(言語ドリフト)。Secondaryでは救えない |
| 日本語 | 既に JA SCG(目標型) |
| 3回上限の担保 | 現行は外側ループで破れる(Coffee: TTS 5回、理論最大12)。新方式は fingerprint+attempt上限assert |
