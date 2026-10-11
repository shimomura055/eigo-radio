# CURRENT_SPEC_SURVEY_01 — 英語ASR確認・TTS再生成フローの現行仕様整理

管理ID: FAMILY-X-EN-ASR-CONFIRM-RETRY-REDESIGN-01 委任_01 / 日付 2026-10-11 / 有料API: 0 / Production変更: なし

## 0. 前提と読み方
- 調査対象コード: `main`(HEAD f8e63c8b 時点の作業ツリー)。行番号は特記なき限り `main` のもの。
- **重要な差分**: Coffee実runは worktree `eigo-radio-tone`(branch `feature/coffee-new-tone-01`)のコードで実行された。このbranchは main に未mergeで、`main` との違いは (i) role Style値(F1.5/E2_UPBEAT/J2、`er033_tts_flash_lite_family_x_styles_01.py`)、(ii) A2 Full Storyのfallback/Local Rewrite再TTSが「減速指示連結済みの承認Style」を使う(`fallback_style_prefix`引数、委任_06)。`main` ではfallbackは `natural, clear, conversational`(後述)。本書は `main` を正とし、branch差分は「[branch]」と明記する。
- SSOT行番号は `CURRENT_SPEC.md`=CS、`OPEN_ITEMS.md`=OI。全文読込はせず Grep で特定した。
- ここで言う「Primary ASR」= OpenAI `gpt-4o-mini-transcribe`、「Secondary ASR」= Azure Speech STT(en-US)(`er006_asr_provider_routing_01.py`、CS:1945)。

## 1. 現行フロー図(テキスト)

### 1-A. Standard(A2)の英語本文 role(Full Story part1-3 / in_one_line。topic_intro は fallback 経路のみ同じ)
```
generate_a2_segment_with_slowdown   [er003_v1_n3_01_tts_generate.py:197-268]  ← 外側ループ max_slowdown_attempts=3 (L251)
 └ for i in 1..3:
    ├ generate_english_segment_with_fallback  [er003_v1_crosslevel_audio_02_common.py:78-289]  (Review Lock guard L78)
    │   ├ 標準経路 = generate_narration_snippet_verified_strict(max_attempts=2) [crosslevel:142 / repro01:196-446]
    │   │    attempt1: TTS(role Style+減速指示) → Primary ASR → classify_asr_match
    │   │       PASS → 戻る
    │   │       NG   → evaluate_attempt_with_cascade [er006_secondary_asr_01.py:342-400]
    │   │              ・entity/homophone由来のASR_VALIDATION_UNCERTAINのみ → Primary#2 → Secondary#1 → Secondary#2 (L723-833)
    │   │              ・それ以外(TRUE_CONTENT_MISMATCH 等)は Secondary を呼ばず即 attempt2 へ
    │   │    attempt2: 同一Promptで再TTS → 同上
    │   ├ (2回NG) → 10分cool-down [er020:56-90、Full Story等5role+CS層ON時のみ] → fallback 1回 [crosslevel:165-259]
    │   │       _run_a2_minimal_fallback_attempt [crosslevel:292-355]: **別Prompt**(main: "natural, clear, conversational"; [branch]: 承認Style維持)
    │   │       force_secondary=True → Primary PASS でも Azure を必ず1回呼び、Azure NG なら不合格 (er006_secondary_asr_01.py:699-721)
    │   └ (3回NG) → Local Rewrite(5role+CS層ON時) [crosslevel:252-258, 282-288 → er020:677-]
    │           Luna が問題span周辺を書き換え → 7 Gate → 再TTS(**fallback と同じ関数・同じPrompt**)1回
    │           失敗 → status=STOPPED/ASR_VALIDATION_UNCERTAIN → Review Lock が HUMAN_REVIEW_REQUIRED
    ├ OK なら apply_a2_slowdown_postprocess [n3_tts:117-194]: 6% time-stretch → **Primary ASR 1回のみ**で再検証 (Secondary なし)
    │       NG → status=STOPPED → 外側ループが 1. に戻り、**標準2+fallback1(+LR1) を丸ごとやり直す** (TTS最大 3×(3+1)=12)
    └ OK なら終了
```
### 1-B. Advanced(B1B)の英語本文 role
- Full Story / in_one_line: `news_tail_fix.generate_news_narration_wide_margin` [er003_v1_sing01_news_tail_fix.py:61-333]。**同一Prompt(role Style)で最大3回**(L138)。attempt3 の直前のみ10分cool-down(L143)。minimal fallback は「TTS技術的失敗/発話区間検出失敗」時のみ**同じattempt内で**別Prompt(L172-182)。ASRは Primary → (entity/homophoneのみ)cascade。3回NGで Local Rewrite(L290-324)。6%減速post-processなし(Advanced)。
- Comment / Preview / Topic intro: `voice01.generate_charon_english` [er003_v1_sing01_voice01_generate.py:47-323]。構造は同じ(同一Prompt最大3回、技術的失敗時のみ同attempt内で `natural, clear, conversational` fallback [L172-213]、cool-down、Local Rewrite)。

### 1-C. 共通 ASR 判定の順序(1 attempt)
```
routing.transcribe (Primary) → val.classify_asr_match [er006_preprod_hardening_01_validation.py:1159-1291]
  Tier1 数値/通貨/%/年/時刻/分数/ローマ数字/略語の値等価 (5role限定, :1208-1239) → NUMERIC_EQUIVALENCE_MATCH
  _classify_asr_match_core (:958-1135): EXACT / NORMALIZED / despace / protected_check(数字・否定) / 内容語差
       ・数字/否定差 → (同音数字rescueのみ例外) TRUE_CONTENT_MISMATCH
       ・非entity内容語差 → Connected Speech 3パターン(:1076-1088) 該当でなければ TRUE_CONTENT_MISMATCH
       ・entityのみ/homophoneのみ → ASR_VALIDATION_UNCERTAIN(should_retry=False)
       ・差なしで ratio>=0.98 → HIGH_SIMILARITY_SAFE
  標準contraction展開 (OPEN-123, :1246-1261) → TRANSCRIPT_STYLE_NORMALIZED_MATCH
evaluate_attempt_with_cascade_detail [er006_secondary_asr_01.py:459-864]
  (i)   TRUE_CONTENT_MISMATCH かつ protected 通過 かつ CS Equivalence Layer ON (:542-591): 音韻カテゴリ該当時のみ Azure+local whisper で corroboration
  (ii)  ASR_VALIDATION_UNCERTAIN かつ 5role かつ sub_reason が plural_only/entity_only (:593-674): **Tier3** Azure corroboration → SECONDARY_ASR_CORROBORATED_MATCH
  (iii) 非ラテン文字主体(Key Phrase 経路のみ) (:676-697)
  (iv)  force_secondary(fallback経路のみ) (:699-721)
  (v)   entity-like / homophone-like の UNCERTAIN: CMU辞書で即PASS可なら0 call、でなければ Primary#2→Secondary#1→Secondary#2→Human Review (:723-864)
```
Tier名の整理: Tier1=数値等価、Tier2=未実装(wanna/gonna、Phase C対象外 = er021:11)、Tier3=複数形/固有名詞のcorroboration救済。

## 2. 要求項目 (a)〜(g)

### (a) Primary / Secondary ASR の発火条件・判定条件
| 段 | 条件 | 判定 | 根拠 |
|---|---|---|---|
| Primary | 全TTS attemptで1回(Key Phrase のみ prompt付き) | `classify_asr_match`(上記) | repro01:329, crosslevel:325 / CS:1945 |
| Primary#2 | Primary が entity-like または homophone-like の **ASR_VALIDATION_UNCERTAIN** で、CMU辞書で即PASSできない場合 | 同一音声を再転写 | er006_secondary_asr_01.py:741-765 / CS:1997 |
| Secondary#1,#2 | Primary#2 でも未解決の場合に **同一音声** を Azure(Phrase List付き)で最大2回 | `classify_asr_match`(Azure転写) | :773-827 / CS:1997 `CASCADE_CONFIG` max_secondary_attempts=2 (:169-175) |
| Secondary(Tier3) | 5role、Primary UNCERTAIN、sub_reason=plural_only/entity_only(差分ちょうど1トークン) | Azureが diff位置でcanonical語を支持したときのみ救済 | :593-674 / CS:2000 |
| Secondary(CS層) | TRUE_CONTENT_MISMATCH で protected_check 通過、音韻環境カテゴリA〜G該当 | Azure+local faster-whisper の corroboration≥1 | :542-591 / CS:2007 |
| Secondary(forced) | **fallback/Local Rewrite再TTS経路のみ**。Primary PASSでも必ず1回 | Azureも合格しない限り不合格 | :699-721 / CS:1911 |
| Secondary(post-slowdown) | **呼ばれない**。Primary 1回のみ | `classify_asr_match`のみ | n3_tts:134-193 |

### (b) Primary NG後に Secondary を呼ばず TTS 再生成へ進む条件
1. 分類が `TRUE_CONTENT_MISMATCH`(数字・否定差、または非entityの内容語差)で、CS Equivalence Layer の事前チェックが NEVER_ELIGIBLE(または5role外/層OFF)。= **これが最多**(telemetry 255ユニーク組の内訳は FREE_VERIFICATION §4-6)。
2. `TTS_FAILURE`(類似度<0.4)。
3. `ASR_VALIDATION_UNCERTAIN` だが entity-like でも homophone-like でもない(「内容語の差なし・一致率不足」)。
4. 長さ超過(`length_ok=False`)、Disfluency/Repetition QA 不合格。
5. 日本語 SCG と違い、**英語に「Primary TRUE_CONTENT_MISMATCH 時の確認Secondary」は存在しない**(`evaluate_attempt_with_cascade_detail` に該当分岐なし)。
実例: Coffee `full_story_part2` の標準1回目(file attempt2)は `showed→show` の非entity内容語差 → Secondary 0回で再生成(COFFEE_NG_ROOTCAUSE_01 §2)。

### (c) TTS retry 回数と各回の実際の Prompt 差 (Standard A2 本文, `main`)
| 回 | 経路 | Style(speech_metadata.style) | 減速指示 | model / backend / voice | 備考 |
|---|---|---|---|---|---|
| 1 | 標準 | FAMILY_X_ROLE_STYLE_EN["FULL_STORY"] + 減速指示(`_role_style_slower`, er019:875-891) | あり | gemini-3.8-flash-lite-tts / speech_metadata_flash_lite / Aoede | 発音hintがあれば Style に追記(repro01:291-296) |
| 2 | 標準 | 同上(同一Prompt) | あり | 同上 | 即時 |
| 3 | fallback | `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]`="natural, clear, conversational"(repro01:541-545) | **なし** | 同上 | 10分cool-down後、force_secondary。**Prompt が変わる** |
| 3b(任意) | Local Rewrite 再TTS | 3 と同じ関数・同じfallback Style(crosslevel:381-398) | なし | 同上 | **本文が書き換わる**。TTS総数4 |
| 外側 | 6%減速NG時の取り直し | 1〜3b を丸ごと再実行 | あり | 同上 | 最大3周。**TTS総数の上限3は外側ループで破られる** |
[branch] 3 / 3b は F1.5+減速に置換(同一Style)。ただし経路名は minimal_fallback のまま、`force_secondary=True` は残る。
Advanced(B1B) Full Story は 1〜3 が全て同一Prompt(news_tail_fix.py:128,152)。Comment/Preview/Topic intro も同様(voice01:157)。技術的失敗時のみ別Prompt(上記 1-B)。
Key Phrase 英語は別構成: Minimal instruction 最大2回 → English language lock 最大2回 = 合計4回(repro01:633-635、ユーザー正式決定の例外、CS:1692 付近)。

### (d) minimal fallback の発火条件と役割
- 発火: A2 `generate_english_segment_with_fallback` で標準2回とも不合格(crosslevel:165-166)。B1B系は「TTS技術的失敗」時のみ同attempt内で発火。
- 役割(歴史的): 長いStyle指示でモデルがテキストを読まず応答する現象("Model tried to generate text…", crosslevel:50-59)への対症療法。ER-011-…-25/26(CS:1692)で「標準2+fallback1=3」に固定。2026-08-26に Primary PASS でも Azure 必須化(CS:1911, 誤PASS事故の再発防止)。
- 副作用(本調査で確認): (1) Prompt が変わるため、Standard の声質・トーン・速度が1本の中で不連続になりうる([branch] で一部是正)。(2) `force_secondary` により「Primary PASS・Azure NG」で不合格になり、Azure誤認識(Coffee: raw bean→Robbins)で救済できない。(3) Local Rewrite がこの関数を再利用するため Style 問題を引き継ぐ。

### (e) Local Rewrite の発火条件と役割
- 発火: Human Review Lock到達**直前**(3回とも不合格)、かつ `connected_speech_enabled_for(segment_id)`(5role)(crosslevel:252-258, 282-288; news_tail_fix:290-324; voice01:291-319)。承認: CS:1971(2026-09-26)。
- 役割: 問題span周辺のみを Luna で書換え → 7 Gate(意味/role/Fact非矛盾/文脈/Natural English/局所性/非全文) → 再TTS 1回、cool-downなし。成功なら `RESOLVED_BY_LOCAL_REWRITE`(status=OK)。OPEN-256(CLOSED)で全文性検証を位置非依存へ是正(OI:758)。
- **本調査で確認した不具合**: NG span は `last_asr_text`(**Primary転写**)と原稿の差分から特定する(er020:171-, :677-)。fallbackが「Primary PASS・Azure NG」で落ちた場合、Primary転写は原稿と実質同一なので、無関係な差分(`US` vs `U.S.`)が NG span として選ばれ、**実際の問題箇所(Azure が誤聴した raw bean)と無関係な `US data → data from the United States` が書き換えられた**(Coffee: local_rewrite_recovery_full_story_part2.json の `ng_span`)。

### (f) 役割別の仕様差
| role | 経路 | TTS総数上限 | 同一Prompt? | Secondary | cool-down | LR | 減速post-process |
|---|---|---|---|---|---|---|---|
| Standard Full Story part1-3 / in_one_line | n3_tts.generate_a2_segment_with_slowdown → crosslevel | 標準2+fb1(+LR1) ×外側3周 | **No**(3回目が別Prompt) | entity/homophone cascade、fallbackは必須 | あり | あり | あり(Primary1回で再検証) |
| Standard topic_intro | crosslevel(slowdownなし) | 標準2+fb1(+LR1) | No | 同上 | あり | あり | なし |
| Advanced Full Story / in_one_line | news_tail_fix | 3(+技術fallback別Prompt)(+LR1) | Yes(技術失敗時を除く) | entity/homophone cascade | attempt3前 | あり | なし |
| Advanced Comment/Preview/Topic intro | voice01.generate_charon_english | 同上 | Yes(技術失敗時を除く) | 同上 | あり | あり | なし |
| 日本語(title/preview/comment/KP意味) | generate_a2_japanese_with_fallback / generate_charon_japanese | 標準2+fb1(JA) | No(JA minimal) | **JA SCG**(Primary TCM時にAzure1回) | なし(A2 JA経路に呼出なし) | なし | なし |
| Key Phrase 英語 | generate_key_phrase_component_verified | 4(Minimal2+English lock2) | No(設計上別Prompt) | 非ラテン時のみ | なし | なし | なし |
| 共有殻(num_*, welcome 等) | Master Store再利用 / ensure_all_shared_narration | 再利用優先、生成時は標準経路 | — | cascade | — | — | — |
Review Lock: `PRODUCTION_MAX_TTS_ATTEMPTS=3`, 標準2+fallback1(er011_human_review_lock_01.py:80-104)、累計上限 TTS15/ASR60(:68-69)。`RESOLVED` は再実行をブロックしない(:242-252、6%減速retryのため明記)。

### (g) 日本語 SCG(OPEN-258)との共通点・相違点
| 項目 | 日本語 SCG (CS:1994, `er007_ja_secondary_asr_01.py:77-330`) | 英語(現行) |
|---|---|---|
| 発火 | Primary=`TRUE_CONTENT_MISMATCH` のとき TTS再生成**前**に Azure 1回 | Primary TCM では**呼ばない**(entity/homophone UNCERTAIN のみ、最大Primary#2+Secondary×2) |
| PASS条件 | Secondary が EXACT/NORMALIZED のみ(PHONETIC不可) | Secondary が `should_pass`(HIGH_SIMILARITY_SAFE 等も含む)+Tier3 corroboration |
| Phrase List | なし(誤PASS防止で意図的に不採用) | あり(ledger phrase。Azureが原稿綴りへ寄る余地) |
| 除外 | 数字差/否定差/固有名詞/類似度<0.4/length_ok=False/同形異音語 | (該当概念なし。protected_checkの数字/否定は Secondary を呼ばず再生成) |
| attempt消費 | しない(確認のみ) | cascade は消費しない(同一音声再転写)。fallbackは別attempt |
| Flag | `JA_SCG_ENABLED` 既定ON | `FEATURE_FLAG_SECONDARY_ASR_ENABLED` 既定ON(er006_secondary_asr_01.py:163) |
| 証跡 | scg_info(secondary_transcript全文等) | steps は attempt json に残るが、**fallback経路は cascade_steps 未保存**・queue は同一wav+同一原稿で重複排除(er011_human_review_lock_01.py:429-452)され Azure 転写が欠落しうる |
共通点: Primary=OpenAI / Secondary=Azure、attempt上限3・Human Review Lock・Queue は不変、Secondary は「救済」にのみ使う思想。
相違の要点: 日本語は「Primary NG → Secondary 1回 → 両NGで再生成」を既に実装済みで、**ユーザー目標フローの前半と同型**。英語はこれが未実装。

## 3. 本調査で見つかった仕様/実装上の発見(後続判断用、実装していない)
| ID | 発見 | 影響 | 根拠 |
|---|---|---|---|
| F-1 | A2 の6%減速 post-process が **Primary 1回のみ**で再検証し、NGなら外側ループが標準2+fallback1(+LR1)を**丸ごと再実行**(最大3周)。「TTS最大3回」は**外側ループで破られる**(理論最大12) | 不要なTTS再生成・所要時間・コスト増。Primary PASS済み音声を捨てる | n3_tts:248-266, er011_human_review_lock_01.py:242-252 |
| F-2 | post-slowdown 転写本文は結果dictの上書きで**永続化されない**(分類名のみ `slowdown_attempts_log`) | 事後検証不能 | n3_tts:149 |
| F-3 | fallback経路は `cascade_steps` を attempt json に保存せず、queue の重複排除で Azure 転写が残らない。**さらに main の fallback attempt json は `model` を `p9a.ENGLISH_MODEL_NAME`(=gemini-2.5-pro-preview-tts)と誤記録し `tts_backend` も保存しない**(Flash-Lite実run 8件で確認: meta__run_regen_01 ほか。[branch] では是正) | 判定根拠の欠落・監査記録の誤り(過去集計でFlash-Lite期のfallbackを取りこぼす) | crosslevel:213-223, er011:429-452 |
| F-4 | Local Rewrite の NG span は Primary転写基準。force_secondary 失敗時は無関係箇所を書換える | 誤った書換え・本文変更 | er020:171, :677- |
| F-5 | Validator: `US` vs `U.S.` は despace が効く単独差では NORMALIZED_MATCH だが、同時に他の軽微差(cost/costs)があると entity-like(`capitalized`)扱いで UNCERTAIN → cascade(Azure×2)を誘発 | 偽NG・Azure費用 | val:1024-1034, 1096-1099(再現: FREE_VERIFICATION §4-1) |
| F-6 | Azure は ASR として OpenAI Primary より誤認識/脱落が多く(`raw bean→robbing`、`M→am`、`two` 挿入、語脱落)、force_secondary / Secondary NG を「最終権威」にすると偽NGになる | 偽Human Review | 人間レビューqueue 67行の分析(FREE_VERIFICATION §4-5) |
| F-7 | RUNTIME_EVIDENCE_01 の費用集計に **Azure の費用(8 call・231.8秒 ≒ ¥10.3、$1/h×160円)が含まれていない可能性**(OpenAI ASR 69 call=¥4.68 と一致し Azure は別枠) | 累計費用の過少表示 | raw_usage_log 再計算(QCD_COMPARISON_01 §8) |
| F-8 | B1B系の「技術的fallback」は同一attempt内で2回目のTTSを行うため、attempt数=3でもTTS呼出は最大6 | 「最大3回」と実TTS数の不一致 | news_tail_fix:172-182, voice01:172-213 |

## 4. SSOT / コード行番号の索引
- CS(`CURRENT_SPEC.md`): 1692(試行上限3、標準2+fb1)、1911(minimal fallback・force_secondary)、1916(6%減速・max3取り直し)、1945(ASR Primary/Secondary)、1971(cool-down+Local Rewrite)、1994(JA SCG)、1997(ASR-first cascade)、2000(EN Semantic Equivalence Tier1/3)、2001(Human Review Route)、2004(retry上限横断監査)、2007(CS Equivalence Layer)。
- OI(`OPEN_ITEMS.md`): 758(OPEN-256 CLOSED)、759(OPEN-257 音韻衝突 未承認)、760(OPEN-258 CLOSED)、405(OPEN-222 極短語ドリフト)、766(OPEN-263)。
- 主要コード: `er006_secondary_asr_01.py`(163,169,342-864)、`er006_preprod_hardening_01_validation.py`(958-1291,1302,1321)、`er003_v1_crosslevel_audio_02_common.py`(78-412)、`er003_v1_repro01_main_generate.py`(196-446,495-588,633-635)、`er003_v1_n3_01_tts_generate.py`(74,117-268)、`er003_v1_sing01_news_tail_fix.py`(61-333)、`er003_v1_sing01_voice01_generate.py`(47-323)、`er020_tts_retry_local_rewrite_01.py`(56-90,120-160,171,677-)、`er011_human_review_lock_01.py`(68-104,199-367,429-452)、`er019_family_x_audio_production_runner_01.py`(405,825-990)、`er033_tts_flash_lite_family_x_styles_01.py`(41-61,94)。
