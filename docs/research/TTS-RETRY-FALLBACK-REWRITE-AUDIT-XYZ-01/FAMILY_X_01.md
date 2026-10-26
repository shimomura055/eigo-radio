# FAMILY_X_01 — Family X(Standard/Advanced)のRetry・Fallback・Local Rewrite・Human Review棚卸し

管理ID: TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_01X / 2026-10-26 / **read-only**(API 0・JPY0・コード/SSOT/run dir変更0)
対象HEAD `764901e3a`(作業ツリー読取)。共用関数の正本=`COMMON_CORE_01.md`(関数コード L1-L8 を以下で引用)。構造化版=`family_x_01.json`(19行)。
表記: 表のセルは事実(ファイル:行・文書)のみ。技術的見解は「9. 所見(事実ではない)」へ分離。**「3回NG」は必ず「通常n+Fallback m+LR後k=総N」で書く**(技術別枠[attempt内 `_call_tts_with_retry` max_retry=1]は総Nに含めない)。

## 0. Family Xの結論(事実ベース)

1. **Xは英語5 role(topic_intro/preview/comment/本文[chunk含む]/in_one_line)で「3回NG→cooldown 600秒→LR→HR」、日本語・Key Phrase・shell・Key Phrase解説では「LRなし」**。この差は(a)日本語=ユーザー2026-10-15指示「日本語:現時点では原則Human Review」(`docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`:148,160)、(b)KP英語phrase=ユーザー2026-09-26決定「適用しない=Heading readout、Key Phrase」(DECISION_LOG.md:9711付近)+2026-10-15「Key Phrase:学習対象の表現を別表現に置き換えない」(同:161)で承認根拠あり=**分類A**。(c)**KP英語解説とshell固定英語は承認記録が見つからない=分類C**(下記X-F5/X-F6)。
2. **2026-10-19ユーザー決定の基本フロー(TTS初回→最大2回再生成→なおNGならRewrite)は、X英語5 roleの実コードと一致**し、Adv本文はword_gacha(2026-10-24)でcooldown600.003秒→LR→再TTS PASS_WITH_WARNINGの実走を確認。「両ASR合意」条件の実行コードは0件(er020のdocstringのみ)。
3. **仕様と不一致(B)**: LR再TTSでAdvのLRが**再入**し得る(X-F1、実記録に深さ2が3件。**既知=OPEN_ITEMS.md:885 OPEN-376 D-B4**)/LR再TTSでrole Styleが落ちる(X-F2、既知OPEN-312)。
4. **根拠なし(C)**: 非ASR起因NG(disfluency等)ではLRのNG spanが取れず「cooldown 10分→LR不発→HR」(X-F3、2026-10-26実走)/HR queue行がLR成功時も残る(X-F4、**既知=OPEN-376 D-B5**)/KP解説・shellのLR有無(X-F5/X-F6)/Std減速後最終NGでLRしない(X-F7)。
5. Xのrunner(er019)は独立のretryループ・固定回数定数を持たない(`KP_EXPLANATION_MAX_ATTEMPTS=3` のみ。Grep 6.)。旧ルール残置: `stop_retrying`分岐(cascade OFF専用)、`shared_narration`の`max_attempts=6`(関数内で3に固定)。

## 1. Xの正式Production音声構成(完全一覧)

音声化されるのは次の19区分。Intro/Notification/Outro は **SFX(TTSなし)**(`er019_family_x_audio_plan_01.py:277-298,333-355`)。学習テキストPart 1/2(Vocabulary & Expressions・文法)は**テキスト/HTMLのみで音声なし**(`er019:part1_study_html_for_player` 616, `run_part2_*` 654-698)。Key Phrase末尾の英語phrase再掲(`phrase_repeat`)は`en_r`の複製でTTS 0(`er019:1790付近`)。

| # | Lv | 音声部位 | 生成関数(ファイル:行) | leaf |
|---|---|---|---|---|
| 1 | Adv | topic_intro | `voice01.generate_charon_english`(er019:1506) | L1 |
| 2 | Adv | preview | 同(er019:1523) | L1 |
| 3 | Adv | comment_1〜4 | 同(er019:1523) | L1 |
| 4 | Adv | full_story_part1〜3(単一段落part) | `news_tail_fix.generate_news_narration_wide_margin`(er019:1562) | L2 |
| 5 | Adv | full_story_part{n}_k{j}(2段落以上=chunk) | 同(`_generate_x_body_part_chunked` er019:1348/1358) | L2 |
| 6 | Adv | in_one_line | 同(er019:1562) | L2 |
| 7 | Adv | Key Phrase英語phrase kpN_en | `_kp_english_generate_fn`(er019:1661)→`kp_en_k2_store.ensure_key_phrase_english_component_styled`(既定profile=K2)/`kp_vote…x_vote`→`generate_key_phrase_component_verified`(repro01:797) | L6 |
| 8 | Adv | Key Phrase英語解説 kpN_explanation_en | `generate_key_phrase_explanation_en_verified`(er019:1205)→`repro01.generate_narration_snippet_verified_strict` | L5 |
| 9 | Adv/Std | shell固定英語(welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five) | `shared_narration.ensure_fixed_english_segment`(er006_audio_cost_pilot_02_shared_narration.py:220)→`voice01.generate_charon_english`(Master Audio Store経由) | L1 |
| 10 | Std | topic_intro(英語) | `crosslevel.generate_english_segment_with_fallback`(er019:1934) | L3 |
| 11 | Std | japanese_title(日本語) | `n3_tts.generate_a2_japanese_with_reading_safety`(er019:1945) | L7 |
| 12 | Std | preview・comment_1〜4(日本語) | 同(er019:1963) | L7 |
| 13 | Std | full_story_part1〜3(英語・6%減速) | `n3_tts.generate_a2_segment_with_slowdown`(er019:1991) | L4(→L3) |
| 14 | Std | full_story_part{n}_k{j}(chunk) | 同(`_generate_x_body_part_chunked_a2` er019:1372/1386) | L4 |
| 15 | Std | in_one_line(英語・6%減速) | 同(er019:1991) | L4 |
| 16 | Std | Key Phrase英語phrase | #7と同一(Store key level=None共有) | L6 |
| 17 | Std | Key Phrase日本語意味 kpN_japanese_meaning | `generate_a2_japanese_with_reading_safety`(er019:2093) | L7 |
| 18 | Std | shell固定日本語『ポイント解説』(A2のみ生成) | `ensure_fixed_japanese_segment`(shared_narration:236)→`voice01.generate_charon_japanese` | L7 |
| (9') | Std | shell固定英語 | #9と同一key(B1で既存ならTTS 0) | L1 |

(#9は構造化JSONでは Adv/Std 別の2行。#18 は Std 順序 `FAMILY_X_A2_SEGMENT_ORDER_V2` に「ポイント解説」が無いが `ensure_all_shared_narration_a2` は無条件に生成する(shared_narration:286-294)。組立で使うかは未確認。)

## 2. 星取表①(X行・全部位)

凡例: 通常=同一設定の品質NG最大回数。「技術別枠」=attempt内`_call_tts_with_retry`(max_retry=1,待機なし)。F-Tech/F-Style/…は固定ラベル。Primary=OpenAI `gpt-4o-mini-transcribe`、Secondary=Azure STT(Primary NG時のみ1回)。いずれも「統一judge」(`er006_secondary_asr_01.py:874`/JA `er007_ja_secondary_asr_01.py`)。

| Family | Lv | 音声部位 | 通常TTS上限 | Retry条件 | Fallback有無・種類 | Rewrite | Rewrite発動条件 | 最終NG時 | 仕様・実装一致 |
|---|---|---|---|---|---|---|---|---|---|
| X | Adv | topic_intro | 通常3(同一Style)+技術別枠 | 統一judge NG全種+length NG+非OK/発話区間検出失敗/異常長。disfluency/repetition QAなし | **F-Tech**のみ(TTS例外・発話区間検出失敗時、attempt内で minimal短文Styleへ即再TTS)。ASR NGでは切替なし | ○ | 通常3回全NG+`cs`=True+最終Primary転写に語差分あり。cooldown 600秒は3回目直前 | STOPPED→Lock(HUMAN_REVIEW_REQUIRED)+英語HR queue→Assemble Gate BLOCK | 一致(静的)/runtime証拠なし(未検証) |
| X | Adv | preview | 同上 | 同上+disfluency QA | F-Tech | ○ | 同上 | 同上 | 一致(静的)/LR実走=2026-09-27(決定前)のみ |
| X | Adv | comment_1〜4 | 同上 | 同上+disfluency QA | F-Tech | ○(ただしASR差分無しのNGでは不発:X-F3) | 同上 | 同上 | 一致(静的)/2026-10-26 comment_4でcooldown→LR不発→STOPPED実走(X-F3) |
| X | Adv | full_story_part1〜3(単一段落) | 通常3(同一Style=PD06)+技術別枠 | 統一judge+length+repetition QA+非OK/発話区間検出失敗/異常長 | **F-Tech**(異常長もfallback対象 news_tail:171) | ○ | 同上。LR再TTSは1回・role Style脱落(X-F2)・再入あり得る(X-F1) | 同上 | 一致(2026-10-24 word_gacha part3実走)+B(X-F1,X-F2) |
| X | Adv | full_story chunk `_k{j}` | chunkごとに通常3 | 同上(chunk単位)。chunk失敗後も後続chunk継続 | F-Tech | ○(chunk単位) | 同上 | chunk entry STOPPED→Lock、親=CHUNKS_NOT_ALL_VALIDATED(承認で迂回不可)→Gate BLOCK | 一致(静的)/chunkのcooldown・LR・HRはruntime証拠なし(未検証) |
| X | Adv | in_one_line | 通常3 | 統一judge+length+disfluency QA | F-Tech | ○(+文数不変Gate 8) | 同上 | 同上 | 一致(静的)/LR実走=2026-10-11(決定前)のみ。B(X-F1,X-F2) |
| X | Adv | Key Phrase英語phrase | **4**=STYLED(K2)2+ENGLISH_LOCK2(全体3回の唯一の例外) | 3-ASR多数決(OpenAI・Azure・Whisper,2/3)NG+length+disfluency QA。Azure/Whisper障害=技術STOP | **F-Style**(前半2回NG→ENGLISH_LOCK、3回目以降) | **×** | — | slot4(最終)NG→STOPPED→Lock+英語HR queue→Gate BLOCK | 一致/実走=2026-10-22 coffee kp1_english STOPPED(HR終端) |
| X | Adv | Key Phrase英語解説 | 通常3(同一Style、OF-AUW-12で旧2→3) | 統一judge+length+disfluency QA+非ラテン救済 | なし | **×** | — | STOPPED→Lock+英語HR queue(slot3)→Gate BLOCK | **仕様記録なし(C)**/runtime証拠なし(未検証) |
| X | Adv/Std | shell固定英語(welcome等9個) | 通常3 | 統一judge+非OK/異常長 | F-Tech | **×** | — | STOPPED→Lock+HR queue→`SharedNarrationBlockedError`+Gate BLOCK | **仕様記録なし(C)**/全399 entry OK・失敗0(未検証) |
| X | Std | topic_intro(英語) | 通常2+**Fallback1**(F-Style)=総3 | 統一judge+length+非OK。標準②は同一Style | **F-Style**(3回目=minimal短文Style、`force_secondary=True`) | ○ | 標準2+fallback1全NG+`cs`=True+語差分あり。cooldownは通算3回目直前 | 同上 | 一致(静的)/runtime証拠なし(未検証)+B(X-F2) |
| X | Std | japanese_title・preview・comment_1〜4・KP日本語意味 | 通常2+Fallback1(F-Style)=総3 | JA統一judge(Primary NG→Secondary 1回,SCG等)+length+読み解決 | **F-Style**(JA minimal instruction) | **×** | — | STOPPED→Lock+**日本語**HR queue(slot3)→Gate BLOCK(cooldownなし) | 一致/実走=2026-10-21 mey_02 comment_2・10-25 ms_03 japanese_titleでHR終端 |
| X | Std | full_story_part1〜3(英語・6%減速) | 通算3(標準2+F-Style1)を減速後再検証の取り直しと共有 | 内側=L3と同じ+repetition QA。外側=6%減速後を統一judgeで再検証、NGなら残予算で取り直し(同一Style) | **F-Style**(標準2回NG後)。減速後取り直しはFallbackではなく通常再生成 | ○(内側全滅時のみ)。**減速後再検証の最終NGはLRなしでHR** | 内側L3が標準+fallbackを使い切り+`cs`=True+語差分あり | (a)内側全滅かつLR不発/NG (b)減速後が通算3回目でNG→finalize→いずれもLock+HR queue→Gate BLOCK | 一致(静的)/10-21 pp_01 fallback+cooldown実走。LR(決定後)runtime証拠なし(未検証)。B(X-F2),C(X-F7) |
| X | Std | full_story chunk `_k{j}` | chunkごと通算3 | 本文と同じ+chunk単位減速 | F-Style | ○(chunk単位) | 同上 | chunk STOPPED→Lock、親CHUNKS_NOT_ALL_VALIDATED、追加Gate BLOCKED_STD_CHUNK_SLOWDOWN_GATE | 一致(静的)/10-26 stdchunk_ev_01で減速後取り直し実走。chunk LR/HR未検証 |
| X | Std | in_one_line(英語・6%減速) | 通算3 | 本文と同じ+disfluency QA | F-Style | ○(+文数不変Gate) | 同上 | 同上 | 一致(静的)/決定後runtime証拠なし(未検証) |
| X | Std | Key Phrase英語phrase | 4(Advと同一) | Advと同一 | F-Style(ENGLISH_LOCK) | **×** | — | slot4 NG→Lock+HR queue | 一致/実走=2026-10-22 small_bag kp1_english STOPPED |
| X | Std | shell固定日本語「ポイント解説」 | 通常2+Fallback1=総3 | JA統一judge | F-Style | **×** | — | STOPPED→Lock+JA HR queue→`SharedNarrationBlockedError` | 一致(JA)/使用有無は未確認 |

## 3. 星取表②(X行): Local Rewriteの適用有無と理由

理由区分: ①ユーザーが明示的に不採用 ②品質保護等で承認済み仕様として対象外 ③技術的制約で未対応 ④共通仕様の適用漏れ/配線漏れ ⑤設計・承認記録に理由なし。

| Family | 音声部位 | Rewrite | 不適用・例外の理由(記録に基づく) | ユーザー承認 | 根拠資料 | 分類 |
|---|---|---|---|---|---|---|
| X | Adv topic_intro/preview/comment/本文/chunk/in_one_line | ○ | (適用部位) | 有: 2026-09-26(A)Local Rewrite+Natural English QA・(C)5 role適用・(D)HR前にLR。2026-10-19 発動条件(両ASR合意)削除 | DECISION_LOG.md:9711-9728、`2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md` §3 | A(+B: X-F1,X-F2 / +C: X-F3) |
| X | Std topic_intro・本文・chunk・in_one_line(英語) | ○(内側が使い切った場合) | (適用部位)。ただし**減速後再検証の最終NG**ではLRを行わず直接HR | 有(適用部位)。減速後最終NGでLR無しは**不明**: 記録はAUW 委任_06eのコード内docstring(n3:309-319)のみ | CURRENT_SPEC.md:2176(2026-09-26 修正1回目でA2経路配線)、n3:317-319 | A(適用部位)/C(減速後最終NG: X-F7) |
| X | Std 日本語(japanese_title・preview・comment・KP日本語意味・ポイント解説) | × | **①+②**: ユーザー2026-10-15「日本語Local Rewrite:現行の英語用機構を機械的に流用しない。安全な実装が成立していない場合はHuman Reviewへ進める」(L148)・「日本語:現時点では原則Human Review」(L160)。技術的背景(開発側記録): `identify_ng_span`が純日本語で`found=False`、Gate7全候補0.0(OPEN-290(E))。**時限表現『現時点では』あり** | 有(L148,L160逐語) | `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`:148,160、CURRENT_SPEC.md:2885(3)、OPEN_ITEMS.md:793 | A |
| X | Adv/Std Key Phrase英語phrase | × | **①+②**: ユーザー2026-09-26(C)「適用しない=Heading readout、Key Phrase」(要旨。除外理由の逐語記録なし)+ユーザー2026-10-15「Key Phrase:学習対象の表現を別表現に置き換えない」(L161)。KP4回構成=2026-09-01決定 | 有 | DECISION_LOG.md:9711、`…_01.md`:147,161、CURRENT_SPEC.md:2885(1) | A |
| X | Adv Key Phrase英語解説 | × | **⑤**: 5 role(2026-09-26)にも除外2 role(Heading,Key Phrase)にも名指しされない(`resolve_narrative_role('kp1_explanation_en')`=None)。`er019:1208-1212`は「統一フロー『TTS①②③、3回NGでLR/HR』に揃える」とコメントするが、LR配線・cooldownは無い。KP解説の回数変更は『ユーザー決定の逐語は無く3回へ揃えた』(CURRENT_SPEC.md:2885(2)) | **不明** | er019:1202-1215、CURRENT_SPEC.md:2885(2)、er020:121 | **C**(X-F5) |
| X | Adv/Std shell固定英語(welcome〜num_five) | × | **⑤**: 同上(5 roleにも除外にも名指しなし。role=None)。`ensure_fixed_english_segment`は`cs`未指定 | **不明** | shared_narration:220-233、er020:135-176 | **C**(X-F6) |

## 4. X部位別の処理フロー(現行・実コード)

(順序はコードどおり。cooldown=固定600秒sleep(`er020:57`)。技術別枠は各TTS呼出で `_call_tts_with_retry` が即時1回再試行する。HR queueの書込はslot最終NG時に統一judgeが行う。)

### 4-1. Adv 英語(topic_intro / preview / comment / 本文 / chunk / in_one_line) — leaf L1/L2
```
通常TTS① (role Style, 技術別枠あり) → Primary ASR → NGなら Secondary(Azure) 1回 → [disfluency/repetition QA]
 PASS → OK(Primary NG・Secondary PASS=PASS_WITH_WARNING→事後試聴リスト)
 NG(NG_BOTH等) → 通常TTS② (同一Style・待機0) → 同判定
 NG → 【cooldown 600秒】(cs=True) → 通常TTS③ (同一Style) → 同判定。この③のNG判定時に HR queue 行が書かれる(LR前, CC-F4)
 NG → LR: 最終Primary転写との語差分でNG span特定(なし→NO_NG_SPAN→HRへ)
        → Luna候補5件→7 Gate QA等→最小変更1本採用(なし→NO_CANDIDATE_PASSED_QA→HRへ)
        → LR再TTS×1 (script v1, force_secondary無し, news_tail系=role Style脱落/voice01系=Style維持)
           → 統一judge(正解=書換え後文)+元と同じdisfluency/repetition QA
              PASS → OK(LR_REWRITTEN警告付PASS_WITH_WARNING)= RESOLVED_BY_LOCAL_REWRITE (record_outcome=RESOLVED)
              NG  → 同関数内でLR再入(X-F1: 再TTS関数が cs=True のまま) → … 非有界
 すべて失敗 → STOPPED → Lock=HUMAN_REVIEW_REQUIRED → Assemble Audio Validation Gate BLOCK
              (同一canonical_textの再runは approve_regenerate / record_human_approval まで0 API)
技術失敗(TTS例外[技術再試行1回後]/発話区間検出失敗[/news_tailのみ 異常長]) → 同一attempt内で F-Tech: minimal短文Styleで即再TTS (attemptは進まない)
```
表記: 「通常3 + Fallback 0 + LR後1(再入時+k) = 総4」。(F-Techは別枠で+最大2/attempt。)

### 4-2. Std 英語 topic_intro — leaf L3
```
標準TTS① (role Style) → Primary → NGならSecondary → PASS: OK
 NG → 標準TTS② (同一Style) → 同判定
 NG → 【cooldown 600秒】 → F-Style: minimal短文Style TTS③ (force_secondary=True: Primary PASSでもSecondary必須)
 NG → LR(同条件) → LR再TTS×1 = _run_a2_minimal_fallback_attempt直呼び(minimal Style, force_secondary, 再入なし)
        PASS → OK(RESOLVED)  / NG → STOPPED → Lock + 英語HR queue → Gate BLOCK
```
表記: 「通常2 + Fallback 1(F-Style) + LR後1 = 総4」。

### 4-3. Std 英語 本文 / chunk / in_one_line — leaf L4(L3 + 6%減速)
```
[内側 L3: 標準① → 標準② → (cooldown)→ F-Style③ → NG全滅ならLR(4-2と同じ)] で生成回数をカウント(count_tts_generations_in_result)
 内側OK → 6% time-stretch(*_original.wav退避) → 減速後wavをPrimary/Secondaryで再検証(正解=LR採用済みなら書換え後文)
    OK → 完了
    NG → 通算生成回数 < 3 なら通常ペースから取り直し(残予算をmax_attemptsとして内側へ。通算で3回目直前なら cooldown 600秒)
         通算 = 3 または外側3周 → 最終slotの減速後NG → LRなし → finalize_a2_slowdown_final_ng
              → Lock=HUMAN_REVIEW_REQUIRED + 英語HR queue 1行 → Gate BLOCK
 内側が全滅(LR不発/NG) → STOPPED → Lock + HR queue → Gate BLOCK
```
表記: 「通常2 + Fallback 1(F-Style) [+ 減速後取り直しは同じ通算3の内数] + LR後1 = 総4(LR再TTS後は減速後再検証をさらに1回)」。

### 4-4. Std 日本語(japanese_title / preview / comment / KP日本語意味 / ポイント解説) — leaf L7
```
標準TTS① (JA Style) → JA Primary → NGなら Secondary(Azure) 1回(+SCG等) → PASS: OK
 NG → 標準TTS② → 同判定
 NG → F-Style: JA minimal instruction TTS③ → 同判定。③のNG時に JA HR queue 行
 NG → STOPPED → Lock=HUMAN_REVIEW_REQUIRED → Gate BLOCK   (LRなし・cooldownなし)
```
表記: 「通常2 + Fallback 1(F-Style) + LR後0 = 総3」。

### 4-5. Key Phrase英語phrase(Adv/Std共通) — leaf L6
```
STYLED(K2)① → 3-ASR多数決(OpenAI/Azure/Whisper,2/3) → NGなら STYLED② → NGなら F-Style: ENGLISH_LOCK③ → ④(最終slot)
  最終NG → STOPPED → Lock + 英語HR queue(slot4のみ書込)。Azure/Whisper circuit open時は後半スキップ(技術STOP)
```
表記: 「通常2 + Fallback 2(F-Style: ENGLISH_LOCK) + LR後0 = 総4」。cooldownなし。

### 4-6. Key Phrase英語解説(Adv) — leaf L5
```
通常TTS①②③(同一Style) → 全NG → STOPPED → Lock + 英語HR queue(slot3) → Gate BLOCK   (cs未指定: cooldownなし・LRなし)
```
表記: 「通常3 + Fallback 0 + LR後0 = 総3」。

### 4-7. shell固定英語 / 固定日本語
```
英語: 通常TTS①②③(voice01, cs未指定) → 全NG → STOPPED → Lock + HR queue → SharedNarrationBlockedError(runtime停止) + Gate BLOCK
日本語(ポイント解説): 標準2 + JA minimal1(voice01.generate_charon_japanese、max_attempts=6→3固定) → STOPPED → Lock + JA HR queue → SharedNarrationBlockedError
```
Master Audio Store: 同一keyが既にあれば新規TTS 0。

## 5. 発見(X)

| ID | 内容(事実) | 分類 | QCD影響 |
|---|---|---|---|
| X-F1 (=CC-F1) | Adv(voice01/news_tail)のLR再TTSが`__wrapped__`を`cs`=Trueのまま呼ぶため、再TTSがNGならLRが再入する(voice01:363-369,:323 / news_tail:370-377,:325)。再入カウンタ無し。実記録: `hormuz__run_03_baseline/b1b/…comment_4`(2026-09-28)、`meta__run_regen_01/b1b/…in_one_line`(2026-10-11)=X、他に`run_e2e_01/…full_story_part1_c18`(Z)。仕様側は「`lr_used==0`=LR再TTSがNGなら`None`→HR(2回目LRなし)」(ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01.md:28)・「LR後v1=標準Prompt・1 attempt」(CURRENT_SPEC.md:2886)・ユーザー2026-10-15「Rewriteの発火・再TTS回数を正しく計数し、累積上限を守る」(…_01.md:164) | **B・既知=OPEN-376(D-B4)**。新規起票不要(PRINCIPLE_NONCOMPLIANCE_ANALYSIS_01.md:103『境界:Fableが意味変更か否か判定してから』) | Q: 中(書換え連鎖で元原稿から逸脱し得る)/ C: Luna+TTS/ASR追加/ D: 小/ 修正は再TTSのみLR無効化の1箇所規模と見込まれるが本調査では未実施 |
| X-F2 (=CC-F2) | LR再TTSのStyle: Adv本文/chunk/in_one_line(news_tail)=role Style脱落(:370-377)、Std全英語=minimal Style(crosslevel:425-427)、Adv topic_intro/preview/comment(voice01)=維持(:363-369)。M3 Style Gateが記録で検知しBLOCK→人間承認が必要。既知=OPEN-312(Deferred, REGISTER #6)・OPEN-274 | **B**(既知OPEN。新規起票不要) | Q: 中(LR発火時のみ)/ D: Gate BLOCKで人手待ち |
| X-F3 (=CC-F3) | 非ASR起因NG(disfluency QA等)ではPrimary転写==canonicalのため`NO_NG_SPAN`→LR不発。実走: `part2_hr_evidence_01__run_r2/b1b/comment_4`(2026-10-26): 3attempt全て`EXACT_MATCH`・disfluency flagged(`now. Now,`)→cooldown600.004秒→LR不発→STOPPED。決定文・CURRENT_SPECとも非ASR起因NGのLR要否は未記録。OPENに`NO_NG_SPAN`を扱う項目なし | **C** | Q: HR増/ C: cooldown10分+TTS3回が無駄/ D: 人手待ち。**判断候補**(A既判断なし/D新規:LRを非ASR起因NGへ拡張するか、cooldownをASR NG時に限るか) |
| X-F4 (=CC-F4) | HR queue行はslot3 NG時(LR前)に書かれ、LR成功後も残る(word_gacha part3: queue 2行、最終status OK)。Lockは正しくRESOLVED | **既知=OPEN-376(D-B5)**(LRで解決したsegmentでもHR queueに行が残る)。新規起票不要 | Q: 低(誤認リスク)/ D: queue監視の手間 |
| X-F5 | KP英語解説(Adv): 3回・cs未指定・cooldown/LRなし。承認根拠なし(表②) | **C** | Q: 低-中(3回NG→HR直行)/ 実走で解説の失敗0件 |
| X-F6 | shell固定英語: 同上 | **C** | Q: 低(固定短文・Store再利用、失敗0/399) |
| X-F7 | Std減速後再検証の最終NG(通算3回目)はLRなしでHR(`finalize_a2_slowdown_final_ng` docstring (iii):n3:317-319=AUW 委任_06e「ユーザー原文L39-49『3回NGでLR/HR』の末端」)。ユーザー逐語の承認は未確認 | **C** | Q: 低-中/ D: 減速由来の稀なNGで人手 |
| X-F8 | 日本語LRなし=ユーザー2026-10-15「現時点では原則Human Review」(時限)。OPEN-290(E)は『当面なし』案のままOPEN(ユーザー判断待ちラベル) | A(ただしOPEN-290が未クローズ) | — |
| X-F9 | X runner(er019)に RUN_LOCK/RESTART_STORM は無い(Z/Y/KP/er077のみ実装, Grep)。PM_GOVERNANCE.md 26-4『STOPセンチネルはFamily Z runnerに実装済み。他Familyへの展開は必要時に別途判断する』 | A(仕様どおり未展開) | D: X連続再実行のstorm防止は手順(実行層の自己停止ルール)頼み |
| X-F10 | Adv(同一Style3回)とStd(標準2+minimal1)の差=CURRENT_SPEC.md:1857が3関数のみ名指し(2026-09-04)+2026-10-21ユーザー「Fallback機構は現行仕様を維持」(…FALLBACK-APPROVAL-FINAL-ASSEMBLY_USER.md:9-15)。2026-10-15 §2「再生成では原稿・Prompt・…を維持」との文面差は10-21決定が後日付で上書き | A | — |

追加の残置(実害なし): `stop_retrying`→`ASR_VALIDATION_UNCERTAIN`分岐(cascade OFF専用 er006:961,:1238)。`ensure_fixed_japanese_segment`の`max_attempts=6`(shared_narration:243。voice01:487で`min(6,3)`)。

## 6. 古いルールの残存・矛盾(Grep結果)

- `er019` 独自retryループ/固定回数定数: `for attempt in range`=0件、`max_attempts =`=0件、定数は`KP_EXPLANATION_MAX_ATTEMPTS = 3`(er019:1202)のみ(PRODUCTION_MAX_TTS_ATTEMPTS=3と同値)。
- 「両ASR合意」の実行コード: 0件(er020:754のdocstringのみ。`er078_asr_unified_judge_01.py:838`の同語は`force_secondary`の別意味)。
- 旧`_post_slowdown_cascade_rescue`: 実行コード0(n3:134のコメントのみ)。`U2_FORCE_SECONDARY_SCOPE`死定数: 撤去済み(er078:89コメント)。
- Chunk Std拡張(2026-10-26)後: `drop_cached_std_chunks_without_slowdown`(er117)・`apply_legacy_partial_retry`で旧方式のresumeを保護。retry/fallback/LR上限は不変(CURRENT_SPEC.md:2957)。コード側の旧retry規則の残存は見つからず。
- 古い記述との矛盾(文書): CURRENT_SPEC.md:2873『再生成②③(原稿・Prompt・モデル・Voice・速度を維持)』はStdの③=minimal fallback(F-Style)と文面上食い違う(10-21ユーザー決定で現行維持が確認済みのため実害なし=A)。

## 7. 2026-10-19 ユーザー決定との照合

逐語(`docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md` §3):
> **「両ASRが同じ箇所の誤読に合意すること」というRewrite発動条件を削除する。** Status：`APPROVED_FOR_PRODUCTION` 基本フロー：TTS初回生成 → Primary／Secondaryによる承認済み検証 → NGなら最大2回のTTS再生成 → なおNGならRewriteへ進む。 既存の音韻同等性判定やその他の承認済み品質・安全条件を省略することは認めない。

> (§4) **正式に許可されたRewrite後は、書換え後の原稿を正解として、すべての後続音声検査を行うこと。**

| 決定項目 | Xの実装 | 判定 |
|---|---|---|
| 「両ASR合意」条件の削除 | 実行コード0件(Grep 6.)。LR呼出は『通算TTS使い切り+`cs`=True』のみ | 一致 |
| 基本フロー(初回→最大2回再生成→Rewrite) | Adv=同一Styleで①②③後にLR。Std=標準①②+F-Style③後にLR(③がminimalなのは10-21決定で維持) | 一致(静的)。Adv本文は2026-10-24実走で確認 |
| 承認済み検証の省略禁止 | LR再TTSも統一judge+disfluency/repetition QAを再実施(Std LR再TTSは`force_secondary=True`) | 一致 |
| 書換え後原稿を正解に全後続検査 | Std減速後再検証=`resolve_expected_text_after_local_rewrite`(n3:220)、X継承=`er019_family_x_validation_inheritance_01.py:277`、Lock/承認keyは元原稿 | 一致(静的)。Xのlive evidence=OPEN-283『live未観測・monitor継続』のまま |
| 失敗時のHR最終移行 | STOPPED→Lock(元原稿key) | 一致 |
| 別の未承認Rewrite条件を追加しない | 追加なし。ただしLR再入(X-F1)は『回数』が文面に無いため、決定の範囲外の挙動 | B(X-F1) |
| cooldown | 10-19決定は言及なし。2026-09-26決定(B)が現行維持(`er020:57`、10-26 Z ctx仕様も同定数を再利用) | 一致(変更記録なし) |

## 8. Runtime evidence 有無(部位別)

実走パスはすべて `er019_output/family_x_audio_production_wiring_01/<run>/<level>/audit/tts_generation_results.json`、LR記録は `er011_output/local_rewrite_recovery/<theme>/<level>/`。

| 部位 | retry | fallback | cooldown | LR | HR/STOP終端 |
|---|---|---|---|---|---|
| Adv本文 | あり(coffee fxpw_01 part1 2回, 2026-10-16) | なし(Adv=F-Techのみ、実走0) | あり(manga_ai_chat_byus part1/part3, 10-21。word_gacha part3 10-24 600.003秒) | **あり・決定後**(word_gacha part3 10-24 RESOLVED)。決定前: hormuz等 | 決定前: hormuz part2 RETTS_FAILED。決定後の本文HR: 未観測 |
| Adv comment | あり | なし | あり(r2 comment_4 10-26, 600.004秒) | 決定前のみ成功(hormuz, 09-28)。**決定後=NO_NG_SPAN不発**(10-26) | STOPPED(10-26 r2 comment_4) |
| Adv preview / topic_intro / in_one_line | previewあり・他なし | なし | なし | preview(09-27)・in_one_line(10-11)=決定前のみ | 未観測 |
| Adv chunk | あり(r2 part1_k3 10-26) | なし | なし | なし(未検証) | なし(未検証) |
| Adv KP phrase | あり(ms_03 kp3 10-25) | あり(ENGLISH_LOCK使用: coffee/small_bag jre_01 10-22) | — | — | STOPPED(coffee jre_01・small_bag jre_01, 10-22) |
| Adv KP解説・shell | **なし(失敗/再試行0件。399+α entry全OK)** | — | — | — | — |
| Std英語本文 | あり(tesla/uk_train 10-23〜26で減速後取り直し) | あり(pp_01 part2 10-21 fallback_used+cooldown1,総3回。meta 10-11) | あり(pp_01) | 決定前のみ(hormuz a2/small_bag a2=RETTS_FAILED) | 未観測(Std本文のHR終端は決定後なし) |
| Std JA | あり(2回目成功: l3_01 等) | JA minimal: 実走確認未(fallback_used True の JA entry: 未確認) | なし(JAは設計上なし) | なし(設計上) | HR終端あり(mey_02 comment_2 10-21、ms_03 japanese_title 10-25、meta japanese_title 10-11) |
| Std KP phrase | あり | あり(small_bag jre_01 10-22) | — | — | STOPPED(small_bag jre_01) |

(決定後=2026-10-19以降。未観測=記録済みrunに該当entryなし=「未検証」と表記。)

## 9. 所見(事実ではない)

1. **X英語5 roleのLRは仕様どおり動いているが、LRが救えるNGは『ASRが語を取り違えた』場合に限られる**。disfluency/反復などASRはPASSするNGでは、10分cooldownを払った後にNO_NG_SPANでHRへ落ちる。単価(TTS 3回+10分待機)とDeliveryの両面で効率が悪い。ただしこれを「設計意図」と読める根拠(承認記録)も「欠陥」と読める根拠も見つからないため、ユーザー判断事項として整理した(RESULT_PACKET参照)。
2. **LR再入(X-F1)は『Rewrite回数』の定義が文書に無い**ことが原因とみられる(文書は1回と読めるがコードは非有界)。本調査では修正しない。再入の無効化は受理面を広げず、既存仕様との整合是正(11-8範囲内)として扱える可能性が高い。
3. **KP解説とshellにLRが無い理由**は「5 role名指し」という列挙型の承認が、名指しされなかった部位を暗黙に除外した結果とみられる。現状で失敗0件なので実害はなく、優先度は低い。
4. **Stdの『標準2+minimal1』は10-21ユーザー決定で維持が確認済み**で、Advとの差(Adv=同一Style3回)も仕様文書上は説明可能。ユーザーが星取表で混乱しやすい点なので、「同じ3回でもStdの3回目はStyleが変わる」ことを明記すると理解しやすい。
5. **JA LRなし**は『現時点では』という時限表現のまま。OPEN-290(E)が未クローズのため、いつ再検討するかの期日・条件は記録なし。

## 10. 参照文書
- 仕様: `CURRENT_SPEC.md` 1857, 2176, 2873-2886, 2957 / `DECISION_LOG.md` 9711-9728, 21944 / `docs/pm/USER_DECISION_REGISTER_01.md` #119(L286), #5(L22), #6(L24), #8(L26), #13(L31) / `OPEN_ITEMS.md` OPEN-274(L777), -283(L786), -290(L793), -312(L815), -371(L880), -422(L934), -432(L944) / `docs/pm/PM_GOVERNANCE.md` 26-4
- ユーザー原文: `docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md`、`2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`(L17-255内)、`2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_FALLBACK-APPROVAL-FINAL-ASSEMBLY_USER.md`
- 設計・レビュー: `docs/research/FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01/{ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01.md, ITEMS23_WIRING_ASSURANCE_01.md, OPUS_REVIEW_G_01_VERBATIM.md, OPUS_REVIEW_H_01_VERBATIM.md}`、`docs/research/FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01/FALLBACK_INVESTIGATION_01.md`、`docs/research/FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01/{EXISTING_SPEC_CHECK_01.md, DESIGN_02.md}`、`docs/pm/recon_connected_speech_scope_01.md`、`docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/`
- 過去Trial/報告: `TTS-COOLDOWN-LOCAL-REWRITE-TRIAL-01_REPORT.md`、`TTS-LOCAL-REWRITE-NATURAL-ENGLISH-QA-TRIAL-02_REPORT.md`、`TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01_REPORT.md`、`OPEN-113-LOCAL-REWRITE-*_REPORT.md`
- 変更履歴(`git log --oneline --since=2026-10-15 -- er020… er003_v1_n3_01_tts_generate.py er019…`): d00f41c8b・7ca0df0ad(Chunk Std)、4413a532b(10-19 LR条件削除+OPEN-283)、5737b77f2(A3 length)、4019b5fe1・cc01cd8f3・9fb1d7fec(統一judge)、7768af1d2(Z ctx)ほか
- 共通核: `COMMON_CORE_01.md` / `common_core_01.json`
- 注: `ER-011_REPORT.md`・`ER-020_REPORT.md` はrepo rootに存在しない(Glob確認)。
