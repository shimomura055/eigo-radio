# REPORT_01 — Family X／Y／Z　TTS Retry・Fallback・Local Rewrite・Human Review 仕様の全体棚卸し(統合報告)

管理ID: TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_02(統合) / 2026-10-26 / **read-only**(API 0・JPY0・コード/SSOT/run dir編集0)。到達上限Status=調査完了(AUDITED)。
ユーザー原文: `docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_USER.md`(構成=原文§9の順)。完成条件: ユーザーが星取表を見れば、XYZそれぞれの音声部位について『何回失敗すると、何が起こり、なぜそうなっているのか』を理解できること。
統合元(編集しない): `COMMON_CORE_01.md`(委任_01X)・`FAMILY_X_01.md`・`FAMILY_Y_01.md`・`FAMILY_Z_01.md`(各 `*_01.json` 付き)。Y Style profileの優先事実確認=`Y_F01_STYLE_PROFILE_CHECK_01.md`。構造化版=`consolidated_01.json`。
読取時のHEAD: 31c41ea76〜2dbc3841e(作業ツリー。関係するコードファイルは `git status --porcelain` で未変更)。

**表記ルール**: 表のセルは事実(ファイル:行・文書)のみ。Claude/Fable/Opusの技術的見解・解釈は「所見(事実ではない)」欄に分離。根拠が見つからないものは『理由不明・記録なし』と書く。「3回NG」は必ず『通常n+Fallback m+LR後k=総N』で書く(技術エラー再試行は別枠で総Nに含めない)。分類は原文§7(A: 承認済みの合理的な差異/B: 承認済み仕様との不一致/C: 未承認・根拠不明)。コードの存在だけでPRODUCTION_WIREDとは判断せず、実走証拠のないものは『未検証』と明記する。

---

## 1. 結論: XYZのRewrite／Fallback仕様は整合しているか

### 1-1. 結論(1段落)

**『大部分は整合しているが、完全には整合していない』。** LR(Local Rewrite)の有無の差は、(i)承認済みの対象外(日本語・Key Phrase)と、(ii)呼出関数の違い+`enable_connected_speech_equivalence_layer`(以下cs)の渡し方でほぼ説明できる。2026-10-19ユーザー決定(『両ASRが同じ箇所の誤読に合意すること』の削除、基本フロー=初回→最大2回再生成→なおNGならRewrite)は、X/Y/Zの英語ナレーション全部位で実装と一致する(実行コードに『両ASR合意』条件は0件。er020のdocstringのみ)。一方で、次の3系統が残る。

1. **承認根拠が見つからずLRが無い部位(C)**: Zの登場人物のセリフ(dialogue。ユーザー原文は『NG→既存のLocal Rewrite処理へ』と書くが、dialogueに既存LRは無い)、Adv Key Phrase英語解説、shell固定英語。
2. **承認済み仕様と実装の不一致(B)**: LRの再入(OPEN-376)、LR再TTSのStyle脱落(OPEN-312)、Z `topic_intro_en`がTopic introの5 roleに解決されない件、古い記述の残存。
3. **3文書の突合で見えた横断問題**: ASRはPASSだがdisfluency/repetition QAでNGになる音声は、cooldown(固定600秒)を払った後にLRが不発でHRへ落ちる(U-03。X実走とY Voice 1)/Y runnerのStyle profileが`default`固定で、設計・台帳・DEV Trialの『`fx_20261017`継承』と異なる(U-15。承認も除外も記録なし)。

### 1-2. 数値の要約

| 項目 | X | Y | Z | 計 |
|---|---|---|---|---|
| 星取表①の行数(部位×レベル) | 16 | 19 | 14 | 49 |
| LRあり(○) | 10 | 9 | 3 | 22 |
| LRなし(×。TTSなしの『—』を除く) | 6 | 9 | 11 | 26 |
| 分類A(承認済み・一致) | 14 | 15 | 7 | 36 |
| 分類B(承認済み仕様との不一致) | 0 | 0 | 2 | 2 |
| 分類C(未承認・根拠不明) | 2 | 3 | 5 | 10 |
| 総4(通常+Fallback+LR後で最大4回生成) | 12 | 11 | 5 | 28 |
| 総3(LRなし。HR直行) | 4 | 7 | 9 | 20 |

(行ごとの分類は星取表①の『仕様・実装一致』欄の先頭。行の分類が『A』でも、別欄に併記したB/Cの発見(U-xx)が付く行がある。TTSなしの固定mp3=Y-B-00は集計外。)

### 1-3. ユーザーが星取表を見て最初に知るべきこと

- 『3回失敗』の意味は部位で違う: Adv英語=同一Styleで3回(総4に至るのはLR後1回を含む)、Std英語・日本語=標準2回+3回目はminimal Style(Fallback)、Zセリフ=文脈付き2回+3回目は従来方式、Key Phrase英語=前段2+ENGLISH_LOCK後段2=総4。星取表①の【総N】欄が正。
- 同じ『Fallback』でも4種類ある(F-Style/F-Prompt/F-Tech。F-Model・F-Voiceに当たる切替は3文書とも確認されなかった)。§2の凡例を参照。
- cooldown(固定600秒)とLRは『cs』1本で同時にON/OFFされる(別々に切れない)。LRが無い部位は『関数がLRを持たない』か『csを渡していない』のどちらかで、Family固有の承認だけでは説明できない箇所がある。
- ZセリフのLR無しは『ユーザーが不採用とした』のではなく、『既存LRが無い状態でFable判断(J-1)がHR/STOP直行を選んだ』。ユーザーは後日その状態を認識し、採否を本調査後へ保留した(§3-2)。→ ユーザー判断事項(§8-1)。

## 2. 星取表①: 全Family・全音声部位

### 2-1. 凡例・用語(3文書の用語をここで統一。統一の根拠は付録A)

| 略号 | 意味 |
|---|---|
| 【総N】 | 通常n+Fallback m+LR後k=総N。技術エラー再試行(各TTS呼出内で即時1回再呼出・待機なし)は別枠で総Nに含めない |
| 通常 | 同一設定(Style・Prompt・モデル・Voice・速度)での品質NG再試行 |
| F-Style | Styleを切替える救済。Std英語/日本語の3回目=minimal短文Style、Key Phrase英語の後半2回=ENGLISH_LOCK prefix |
| F-Prompt | Prompt方式を切替える救済。Z dialogue ctx方式の3回目=ctx Style→従来Dialogue Style |
| F-Tech | 技術失敗(TTS例外[技術retry1回後]/発話区間検出失敗。L2は異常長も)の時だけ、同一attempt内でminimal短文Styleへ即再TTS。attemptは進まない |
| J | 統一judge: Primary=OpenAI gpt-4o-mini-transcribe→NGならSecondary=Azure Speech STT(原則1回)。NG_BOTH/NG_PROTECTED/NG_EXCLUDED/NG_SECONDARY_UNAVAILABLEは不合格。Primary PASSならSecondary不要(KP英語phrase[3-ASR多数決・Primary+Secondary両方必須]とforce_secondaryを除く) |
| cs / cd | cs=`connected_speech_enabled_for(segment_id)`。cd=cooldown固定600秒(通算最終attempt直前・cs=Trueのみ・単一sleep)。cs=Trueでcd+LRが同時に有効 |
| LR | Local Rewrite: NG span特定→Luna候補5件→7 Gate QA+全文性→最小変更1本→再TTS1回(`script_version=v1`) |
| Lock / HRQ / Gate BLOCK | Lock=ER-011 Review Lock(HUMAN_REVIEW_REQUIRED。同一canonical_textは0 API callでブロック)。HRQ=Human Review queue(英語=er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl、日本語=er007_output/ja_asr_cascade_01/…。表示用append-only)。Gate BLOCK=Assemble前Audio Validation Gateが組立を止める |
| 生成関数L1〜L8 | COMMON_CORE_01 §1: L1=voice01.generate_charon_english / L2=news_tail_fix.generate_news_narration_wide_margin / L3=crosslevel.generate_english_segment_with_fallback / L4=n3_tts.generate_a2_segment_with_slowdown(→L3) / L5=repro01.generate_narration_snippet_verified_strict / L6=repro01.generate_key_phrase_component_verified / L7=日本語(voice01.generate_charon_japanese / n3_tts.generate_a2_japanese_with_fallback) / L8=er012_b.generate_voice_body_wide_margin。**LRを持つ関数はL1・L2・L3(L4経由含む)のみ**。L5〜L8は関数自体にLR呼出が無い |

**runnerの終端の差(最終NG後の挙動はFamilyで違う)**: Xは segment のASR NGでrunnerは停止せず、Assemble前Gateが BLOCK する(exit 3は上流失敗時のみ)。Yはtts stageがrc=0で続行し、gate stageのY style gate BLOCK または assemble の Audio Validation Gate で `YE2EStop` rc=2。Zは全clip処理後に `FamilyZTtsClipFailedStop` rc=2(STOP sentinelは作らない)。どの場合もLock(HUMAN_REVIEW_REQUIRED)は同じく書かれ、解除は `approve_regenerate`(次の1回だけ)または `record_human_approval`(canonical sha一致のみ)。

### 2-2. 早見表: 何回失敗すると何が起こるか(部位をまとめた版)

| # | 部位グループ | 1回目NG | 2回目NG | 3回目NG | 4回目 | 最終NG | なぜそうなっているか(既存記録) |
|---|---|---|---|---|---|---|---|
| P1 | **Adv英語**(X Adv topic_intro/preview/comment/本文/chunk/in_one_line、Y Adv topic_intro/preview/comment/本文8、Z Adv narrator/Preview/Comment)【総4】 | 同一Styleで再TTS②(待機0) | 固定600秒待機→同一Styleで③ | LR: NG span特定→Luna候補→7 Gate→1本採用(語差分なし/候補なし→HR) | LR再TTS1回(Style保持は部位で違う: U-02。NGなら理論上LR再入: U-01) | Lock+英語HRQ→Gate BLOCK/STOP | 2026-09-26ユーザー決定(B)10分cooldown(D)HR前にLR、2026-10-19決定(発動条件) |
| P2 | **Std英語**(X Std topic_intro/本文/chunk/in_one_line、Y Std topic_intro/本文、Z Std narrator)【総4】 | 標準②(同一Style) | 固定600秒→F-Style: minimal短文Styleで③(Secondary必須) | LR: NG span特定→書換え(語差分なし/候補なし→HR)。本文系で6%減速後の最終NGの場合はLRなしでHR(U-09) | LR再TTS1回(minimal Style・再入なし)。本文系は6%減速後の再検証もある | Lock+英語HRQ→Gate BLOCK/STOP | 標準2+minimal1=2026-09-04ユーザー決定(CURRENT_SPEC.md:1857)、2026-10-21『Fallback機構は現行仕様を維持』、+P1と同じLR決定 |
| P3 | **Zセリフ(ctx方式)**(Std/Adv)【総3】 | ctx Styleで再TTS② | 固定600秒(5秒刻みSTOP確認)→F-Prompt: 従来Dialogue Styleで③ | **LRなし**→Lock+HR/STOP(rc=2) | なし(4回目なし) | Lock→TERMINAL_NG→STOP | 2026-10-26ユーザー原文§2(ctx→ctx→cd→従来方式・総3)。『NG→既存のLocal Rewrite』段は未配線(U-05) |
| P4 | **Zセリフ(legacy方式)**【総3】 | 同一従来Styleで② | ③(cdなし) | **LRなし**→Lock+HR/STOP | — | Lock→STOP | LR/cd非配線の理由は記録なし(U-05) |
| P5 | **日本語**(X/Y/Z Std japanese_title/preview/comment/KP意味、X/Yポイント解説)【総3】 | 標準② | F-Style: JA minimal instructionで③ | **LRなし・cdなし**→Lock+日本語HRQ | — | Lock→Gate BLOCK/STOP | ユーザー2026-10-15『日本語: 現時点では原則Human Review』(時限表現・U-20) |
| P6 | **Key Phrase英語phrase**【総4】 | 前段②(X/Z=K2、Y=MINIMAL: U-15) | F-Style: ENGLISH_LOCKで③ | ENGLISH_LOCK④ | 4回目=最終 | Lock+英語HRQ(slot4のみ)→STOP | 2026-09-26 (C)『適用しない=Heading readout、Key Phrase』、KPは4回構成(CURRENT_SPEC.md:2885(1))。LR/cdなし |
| P7 | **LRなしの英語**(Adv KP英語解説、shell固定英語、Z topic_intro_en)【総3】 | 同一Styleで② | ③(Z Std topic_intro_enのみ=minimal短文Style) | **LRなし・cdなし**→Lock+HRQ | — | Lock→HR/STOP | 承認根拠なし(U-08)。Z topic_intro_enは承認済みTopic introの配線漏れ(U-06) |
| P8 | 固定mp3・Z shell(コピー) | TTSなし | — | — | — | — | — |

読み方: 『3回目NG』の列は『3回目が不合格になったとき何が起こるか』。P1〜P2は総4(LR後1回を含む)、P3〜P5・P7は総3、P6は総4。ただしP1のLR再入は理論上総4を超え得る(U-01)。

### 2-3. 星取表①(全49行。Family→レベル→部位の順。列=ユーザー指定10列+生成関数(L番号)+runtime証拠)

セルは事実のみ。『仕様・実装一致』欄の先頭アルファベットがその行の分類(A/B/C)、U-xxは§5の統合ID。runtime証拠が『未検証』の行は、記録済みrunに該当経路の実走がない(コードの存在だけでPRODUCTION_WIREDとは判断していない)。

| Family | レベル | 音声部位 | 通常TTS上限 | Retry条件 | Fallback有無・種類 | Rewrite有無 | Rewrite発動条件 | 最終NG時 | 仕様・実装一致 | 生成関数 | runtime証拠 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| X | Standard | [X-S01] topic_intro(英語・Aoede) | 【総4】通常2+F1+LR後1(標準②は同一Style) | J NG全種+長さNG+TTS非OK/発話区間検出失敗。disfluency/repetition QAなし | F-Style: 3回目=minimal短文Style(Secondary必須) | ○ | 標準2+F1の全NG+cs=True+最終Primary転写にcanonicalとの語差分あり(無い=NO_NG_SPAN→HR)。cdは通算3回目直前。LR再TTS=minimal Styleで1回(再入なし) | STOPPED→Lock+英語HRQ(slot3 NG時)→Gate BLOCK | **A** — 一致(静的)。B: LR再TTSがrole Styleを落とす(U-02) | L3 | LR/cd実走なし(記録済みrunはatt=1のみ)=未検証 |
| X | Standard | [X-S02] 日本語: japanese_title・preview・comment_1〜4・KP日本語意味 | 【総3】通常2+F1+LR後0 | JA統一judge(Primary NG→Secondary1回・SCG等)+長さ+読み解決/TTS前gate(記号・外来語) | F-Style: 3回目=JA minimal instruction | × | —(日本語はLRなし・cdなし。ユーザー2026-10-15「日本語:現時点では原則HR」) | STOPPED→Lock+日本語HRQ(slot3)→Gate BLOCK | **A** — 一致 | L7 | HR終端の実走あり(2026-10-21 mey_02 comment_2、10-25 ms_03 japanese_title) |
| X | Standard | [X-S03] shell固定日本語『ポイント解説』(A2のみ生成) | 【総3】通常2+F1+LR後0 | JA統一judge+長さ | F-Style: 3回目=JA minimal instruction(max_attempts=6指定は関数内で3にクランプ) | × | —(日本語はLRなし) | STOPPED→Lock+日本語HRQ→SharedNarrationBlockedError(runtime停止)+Gate BLOCK | **A** — 一致(JA)。組立での使用有無は未確認 | L7 | 実走記録なし=未検証 |
| X | Standard | [X-S04] full_story_part1〜3(英語・6%減速) | 【総4】通常2+F1+LR後1(減速後の取り直しは通算3の内数) | 内側=L3と同じ+repetition QA。外側=6%減速後を統一judgeで再検証し、NGなら残予算で取り直し(同一Styleの通常再生成) | F-Style: 標準2回NG後に3回目=minimal短文Style | ○ | 内側が標準2+F1を使い切り+cs=True+語差分あり。cdは通算3回目直前。減速後再検証の最終NGはLRなしでHR(U-09) | (a)内側全滅かつLR不発/NG (b)減速後が通算3回目でNG→finalize→いずれもLock+英語HRQ→Gate BLOCK | **A** — 一致(静的)。B: U-02 / C: U-09 | L4(→L3) | 2026-10-21 pp_01でF-Style+cd実走。決定後のLR実走なし(決定前: hormuz等のRETTS_FAILEDのみ) |
| X | Standard | [X-S05] full_story chunk _k{j}(段落が2つ以上のpart) | 【総4】chunkごとに通算3(上記と同じ)+LR後1 | 本文と同じ(chunk単位)+chunk単位の6%減速 | F-Style(chunk単位) | ○ | chunk単位で同上 | chunk STOPPED→Lock。親=CHUNKS_NOT_ALL_VALIDATED(承認で迂回不可)+BLOCKED_STD_CHUNK_SLOWDOWN_GATE→Gate BLOCK | **A** — 一致(静的) | L4 | 2026-10-26 stdchunk_ev_01で減速後取り直しを実走。chunkのLR/HRは未検証 |
| X | Standard | [X-S06] in_one_line(英語・6%減速) | 【総4】通算3+LR後1 | 本文と同じ+disfluency QA | F-Style | ○ | 同上(+文数不変Gate) | 同上(Lock+英語HRQ→Gate BLOCK) | **A** — 一致(静的) | L4(→L3) | 決定後の実走なし=未検証 |
| X | Standard | [X-S07] Key Phrase英語phrase kpN_en | 【総4】前段2(K2)+後段2(F-Style・ENGLISH_LOCK)+LR後0(KPは全体『3回』の唯一の例外) | 3-ASR多数決(OpenAI/Azure/Whisper・2/3)NG+長さ+disfluency。Azure/Whisper障害=技術STOP | F-Style: 前半2回NG→ENGLISH_LOCK prefixで後半2回 | × | —(ユーザー2026-09-26 (C)で明示除外+2026-10-15「学習対象表現を置換しない」) | slot4 NG→STOPPED→Lock+英語HRQ(slot4のみ)→Gate BLOCK | **A** — 一致 | L6 | STOPPED実走あり(2026-10-22 small_bag kp1_english) |
| X | Advanced | [X-A01] topic_intro(英語・Charon) | 【総4】通常3(同一Style)+F0+LR後1 | J NG全種+長さNG+TTS非OK/発話区間検出失敗(異常長は次attempt)。disfluency/repetition QAなし | F-Tech: TTS例外(技術retry1回後)/発話区間検出失敗時のみ、attempt内でminimal短文Styleへ即再TTS。ASR NGでは切替なし | ○ | 通常3回全NG+cs=True+最終Primary転写に語差分あり(無い=NO_NG_SPAN→HR)。cdは3回目直前。LR再TTS=1回(再入に上限なし: U-01) | STOPPED→Lock+英語HRQ(slot3 NG時・LR前に書込)→Gate BLOCK | **A** — 一致(静的)。B: U-01 | L1 | LR/cd実走なし(att=1のみ)=未検証 |
| X | Advanced | [X-A02] preview(英語・Charon) | 【総4】通常3(同一Style)+F0+LR後1 | J NG全種+長さNG+TTS非OK/発話区間検出失敗(異常長は次attempt)+disfluency QA | F-Tech(同上) | ○ | 通常3回全NG+cs=True+最終Primary転写に語差分あり(無い=NO_NG_SPAN→HR)。cdは3回目直前。LR再TTS=1回(再入に上限なし: U-01) | STOPPED→Lock+英語HRQ(slot3 NG時・LR前に書込)→Gate BLOCK | **A** — 一致(静的)。B: U-01 | L1 | LR実走=2026-09-27(決定前)のみ |
| X | Advanced | [X-A03] comment_1〜4(英語・Charon) | 【総4】通常3(同一Style)+F0+LR後1 | J NG全種+長さNG+TTS非OK/発話区間検出失敗(異常長は次attempt)+disfluency QA | F-Tech(同上) | ○ | 通常3回全NG+cs=True+最終Primary転写に語差分あり(無い=NO_NG_SPAN→HR)。cdは3回目直前。LR再TTS=1回(再入に上限なし: U-01)。ただしASR差分なしのNG(disfluency等)ではLR不発(U-03) | STOPPED→Lock+英語HRQ(slot3 NG時・LR前に書込)→Gate BLOCK | **A** — 一致(静的)。C: U-03 | L1 | 2026-10-25 23:57〜10-26 00:07 r2 comment_4: 3回ともEXACT_MATCH・ASR PASS、disfluency flagged(`now.`/`Now,`)でverified=False→cd600.004秒→LR記録なし(NO_NG_SPAN)→STOPPED |
| X | Advanced | [X-A04] full_story_part1〜3(単一段落part・PD06) | 【総4】通常3(同一Style)+F0+LR後1 | J NG全種+長さNG+TTS非OK/発話区間検出失敗/異常長+repetition QA | F-Tech(attempt内。異常長もminimal fallback対象: CC-F6) | ○ | 通常3回全NG+cs=True+最終Primary転写に語差分あり(無い=NO_NG_SPAN→HR)。cdは3回目直前。LR再TTS=1回(再入に上限なし: U-01)。LR再TTSはrole Styleを渡さない(U-02) | STOPPED→Lock+英語HRQ(slot3 NG時・LR前に書込)→Gate BLOCK | **A** — 一致。B: U-01, U-02 | L2 | 2026-10-24 word_gacha part3: cd600.003秒→LR→再TTS PASS_WITH_WARNING(RESOLVED) |
| X | Advanced | [X-A05] full_story chunk _k{j} | 【総4】chunkごとに通常3+LR後1 | 本文と同じ(chunk単位)。chunk失敗後も後続chunk継続 | F-Tech | ○ | chunk単位で同上 | chunk entry STOPPED→Lock。親=CHUNKS_NOT_ALL_VALIDATED(承認で迂回不可)→Gate BLOCK | **A** — 一致(静的) | L2 | retryは実走(r2 part1_k3 2026-10-26)。chunkのcd・LR・HRは未検証 |
| X | Advanced | [X-A06] in_one_line(英語) | 【総4】通常3+F0+LR後1 | J NG全種+長さNG+TTS非OK/発話区間検出失敗/異常長+disfluency QA | F-Tech | ○ | 通常3回全NG+cs=True+最終Primary転写に語差分あり(無い=NO_NG_SPAN→HR)。cdは3回目直前。LR再TTS=1回(再入に上限なし: U-01)(+文数不変Gate) | STOPPED→Lock+英語HRQ(slot3 NG時・LR前に書込)→Gate BLOCK | **A** — 一致(静的)。B: U-01, U-02 | L2 | LR実走=2026-10-11(決定前)のみ |
| X | Advanced | [X-A07] Key Phrase英語phrase kpN_en | 【総4】前段2(K2)+後段2(F-Style・ENGLISH_LOCK)+LR後0 | 3-ASR多数決(2/3)NG+長さ+disfluency。Azure/Whisper障害=技術STOP | F-Style: 前半2回NG→ENGLISH_LOCK prefixで後半2回 | × | —(ユーザー2026-09-26 (C)明示除外) | slot4 NG→STOPPED→Lock+英語HRQ(slot4のみ)→Gate BLOCK | **A** — 一致 | L6 | STOPPED実走あり(2026-10-22 coffee kp1_english。ENGLISH_LOCK使用実績あり) |
| X | Advanced | [X-A08] Key Phrase英語解説 kpN_explanation_en | 【総3】通常3(同一Style・F0)+LR後0 | 統一judge+長さ+disfluency QA+非ラテン救済 | なし | × | —(5 role外・csを渡さない。承認根拠なし: U-08) | STOPPED→Lock+英語HRQ(slot3)→Gate BLOCK | **C** — 仕様記録なし(C: U-08) | L5 | 失敗/再試行0件=未検証 |
| X | Adv/Std共通 | [X-A09] shell固定英語9(welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five。Adv/Std共通key) | 【総3】通常3(Master Audio Store再利用で生成0あり)+F0+LR後0 | 統一judge+TTS非OK/異常長 | F-Tech | × | —(role=None・csを渡さない。承認根拠なし: U-08) | STOPPED→Lock+HRQ→SharedNarrationBlockedError(runtime停止)+Gate BLOCK | **C** — 仕様記録なし(C: U-08) | L1 | 399 entry全OK・失敗0=未検証 |
| Y | Standard | [Y-S-01] shell固定英語9(welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five) | 【総3】通常3+F0+LR後0(Master Audio Store再利用で生成0あり) | 統一judge+長さ+TTS非OK/異常長/発話区間検出失敗(repetition/disfluency対象外) | F-Tech(attempt内のみ。品質NGでは切替なし) | × | —(cs未指定・role=None。個別の承認記録なし: U-08) | STOPPED→Lock+英語HRQ→SharedNarrationBlockedError/assemble BLOCK | **C** — 仕様記録なし(C: U-08) | L1 | Y runは全件Store再利用(生成0)=未検証 |
| Y | Standard | [Y-S-01b] shell固定日本語 point_explanation『ポイント解説』 | 【総3】通常2+F1+LR後0(max_attempts=6指定は関数内で3にクランプ) | JA統一judge+長さ | F-Style: 3回目=MINIMAL_JA | × | —(日本語はLRなし) | STOPPED→Lock+日本語HRQ。ただしY a2 timelineは未使用(U-17) | **A** — 一致(JA)。未使用clipがgate対象(C: U-17) | L7 | Y runはStore再利用(生成0) |
| Y | Standard | [Y-S-02] topic_intro(英語) | 【総4】通常2+F1+LR後1 | J NG全種+長さNG+TTS非OK/発話区間検出失敗/異常長 | F-Style: 3回目=minimal instruction(Secondary必須) | ○ | 標準2+F1の全NG+cs=True(connected_speech_enabled_for('topic_intro')=True)。LR再TTS=minimal系1回 | LR不成立→STOPPED→Lock+英語HRQ。Y Gate対象外 | **A** — 一致(静的) | L3 | LR/cd実走なし(att=1のみ)=未検証 |
| Y | Standard | [Y-S-03] japanese_title(日本語タイトル) | 【総3】通常2+F1+LR後0 | JA統一judge+長さ+TTS前STOP(記号/外来語gate) | F-Style: 3回目=MINIMAL_JA | × | —(日本語はLRなし。ユーザー2026-10-15 L148,160) | STOPPED→Lock+日本語HRQ | **A** — 一致 | L7 | 実走なし=未検証 |
| Y | Standard | [Y-S-04] 日本語支援文 preview/comment_1/comment_2/comment_3(Stdはcomment_2を維持) | 【総3】通常2+F1+LR後0 | Y-S-03と同じ | F-Style: 3回目=MINIMAL_JA | × | —(日本語はLRなし) | STOPPED→Lock+日本語HRQ。解除=ユーザー承認 or support再生成 | **A** — 一致 | L7 | E-1 a2 preview: 標準2+F1→3NG→HR(日本語HRQ行15)→approve_regenerate(Fable名義)→再STOPPED→ユーザー承認 |
| Y | Standard | [Y-S-05] ナレーター本文5(y_lead/y_intro_1〜3/y_closing・6%減速) | 【総4】通常2+F1+LR後1(減速後取り直しは通算3の内数) | J NG全種+長さNG+TTS非OK/発話区間検出失敗/異常長+repetition QA+減速後ASR NG | F-Style: 標準2回NG→3回目=minimal instruction | ○ | 標準2+F1の全NG+cs=True(FULL_STORY)。減速後NGではLRしない(U-09) | STOPPED→Lock。減速後最終NG→HR+Lock+HRQ。成功でもY Gate(本文8 segment+chunk)がLOCAL_REWRITE_RECOVERY/STD_FALLBACK_USED_OR_UNKNOWN/減速欠落をBLOCK→ユーザー承認要(U-16) | **A** — 一致(静的) | L4(→L3) | 本部位の実走なし=未検証(runは各att=1) |
| Y | Standard | [Y-S-06] Voice本文3(y_voice_1 Algieba/y_voice_2 Zephyr/y_voice_3 Schedar・6%減速) | 【総4】通常2+F1+LR後1 | Y-S-05と同じ | F-Style: 3回目=minimal instruction | ○ | Y-S-05と同じ | Y-S-05と同じ。E-1: LR成功→Y Gate BLOCK(2違反)→ユーザー承認 | **A** — 一致(静的+runtime) | L4(→L3) | E-1 a2 y_voice_1: 標準2+F1(minimal)+LR後1=総4、cd600.003s、LR RESOLVED、英語HRQ行129、Y Gate BLOCK→ユーザー承認(6%減速版)。y_voice_2(E-3)はattempt1 Repetition flag→attempt2 OK |
| Y | Standard | [Y-S-07] 本文chunk y_<segment>_k<j>(段落2つ以上のときのみ。現行Y契約は各Voice1段落) | 【総4】chunkごとにY-S-05と同じ | Y-S-05と同じ(chunk単位) | F-Style(chunk単位) | ○ | chunk単位で同上 | chunk単位でLock/Gate BLOCK。親=CHUNKS_NOT_ALL_VALIDATED | **A** — 一致(静的) | L4 | 実記事では不発火(dev入力att=1)=未検証 |
| Y | Standard | [Y-S-08] Key Phrase英語 kp{rank}_en(3件) | 【総4】前段2(Yはdefault profileのためMINIMAL。X/ZはK2)+後段2(F-Style・ENGLISH_LOCK)+LR後0 | 3-ASR多数決NG+非ラテン再判定+disfluency | F-Style: MINIMAL2回NG→ENGLISH_LOCK2回 | × | —(ユーザー2026-09-26 (C)明示除外) | 4回NG→STOPPED→Lock+英語HRQ(slot4のみ)→Audio Gate BLOCK | **A** — 一致。前段がK2でない点はU-15 | L6 | MINIMAL内retry実走(E-3 kp3)。ENGLISH_LOCK段は未検証 |
| Y | Standard | [Y-S-09] Key Phrase日本語意味 meaning_{i}(3件) | 【総3】通常2+F1+LR後0 | JA統一judge+長さ | F-Style: 3回目=MINIMAL_JA | × | —(日本語はLRなし) | STOPPED→Lock+日本語HRQ→Audio Gate BLOCK | **A** — 一致 | L7 | 実走なし(att=1)=未検証 |
| Y | Advanced | [Y-B-00] Intro/Notification1-3/Outro(固定mp3) | TTSなし | — | — | — | — (音声ファイル読込のみ) | — | 対象外 | — | — |
| Y | Advanced | [Y-B-01] shell固定英語9(Y-S-01と同一key) | 【総3】通常3+F0+LR後0(Store再利用で生成0あり) | 統一judge+長さ+TTS非OK/異常長/発話区間検出失敗 | F-Tech(attempt内のみ) | × | —(cs未指定。承認記録なし: U-08) | STOPPED→Lock+英語HRQ→SharedNarrationBlockedError/assemble BLOCK | **C** — 仕様記録なし(C: U-08) | L1 | Y runは全件Store再利用=未検証 |
| Y | Advanced | [Y-B-02] topic_intro(英語) | 【総4】通常3(同一Style)+F0+LR後1 | J NG全種+長さNG+TTS非OK/発話区間検出失敗/異常長 | F-Tech(attempt内のみ。品質NGでは切替なし) | ○ | 通常3回全NG+cs=True。cdは3回目直前。LR再TTS=1回(Style保持) | LR不成立→STOPPED→Lock+英語HRQ。Y Gate対象外 | **A** — 一致(静的)。B: U-01 | L1 | LR/cd実走なし(att=1のみ)=未検証 |
| Y | Advanced | [Y-B-03] preview/comment_1/comment_3(Comment 2は2026-10-26承認で削除) | 【総4】通常3+F0+LR後1 | Y-B-02+disfluency gate | F-Tech(同上) | ○ | Y-B-02と同じ | Y-B-02と同じ | **A** — 一致(静的)。B: U-01 | L1 | LR/cd実走なし(att=1のみ)=未検証 |
| Y | Advanced | [Y-B-04] ナレーター本文5(y_lead/y_intro_1〜3/y_closing=Tension+Closing) | 【総4】通常3(同一Style)+F0+LR後1 | J NG全種+長さNG+TTS非OK/発話区間検出失敗/異常長+repetition QA | F-Tech(attempt内のみ。異常長もminimal fallback) | ○ | 通常3回全NG+cs=True(FULL_STORY)+語差分あり。cdは3回目直前。LR再TTSはrole Styleを渡さない(U-02) | LR不成立→STOPPED→Lock。成功でもY Gate(本文8 segment+chunk)がLOCAL_REWRITE_RECOVERYをBLOCK→ユーザー承認要(U-16) | **A** — 一致(静的)。B: U-01,U-02 | L2 | 本部位の実走なし=未検証 |
| Y | Advanced | [Y-B-05] Voice本文3(y_voice_1/2/3) | 【総4】通常3+F0+LR後1 | Y-B-04と同じ | F-Tech(Y-B-04と同じ) | ○ | Y-B-04と同じ | Y-B-04と同じ。E-1: LR成功→Y Gate BLOCK→ユーザー承認 | **A** — 一致(静的+runtime)。C: U-03(repetition単独NG) | L2 | E-1 b1b y_voice_1: Repetition QA flagで3回→cd600.004s→LR RESOLVED(attempts_log 4行=通常3+LR後1)→Lock(累積7)→Y Gate BLOCK→2026-10-26ユーザー承認。英語HRQ行なし(U-04) |
| Y | Advanced | [Y-B-06] 本文chunk y_<segment>_k<j> | 【総4】chunkごとにY-B-04と同じ | Y-B-04と同じ(chunk単位) | F-Tech | ○ | chunk単位で同上 | chunk失敗後も後続chunk継続。親=CHUNKS_NOT_ALL_VALIDATED。chunk単位でGate BLOCK | **A** — 一致(静的) | L2 | 実記事では不発火(dev入力att=1)=未検証 |
| Y | Advanced | [Y-B-07] Key Phrase英語 kp{rank}_en(3件。phrase_repeatは新規生成せず同一entry複製) | 【総4】前段2(Yはdefault profileのためMINIMAL。X/ZはK2)+後段2(F-Style・ENGLISH_LOCK)+LR後0 | 3-ASR多数決NG+非ラテン再判定+disfluency | F-Style: MINIMAL2回NG→ENGLISH_LOCK2回 | × | —(ユーザー2026-09-26 (C)明示除外) | 4回NG→STOPPED→Lock+英語HRQ(slot4のみ)→Audio Gate BLOCK | **A** — 一致。前段がK2でない点はU-15 | L6 | MINIMAL内retry実走(E-3 kp3: attempt1 TRUE_CONTENT_MISMATCH→attempt2 OK)。ENGLISH_LOCK段は未検証 |
| Y | Advanced | [Y-B-08] Key Phrase英語解説 kp{rank}_explanation_en(3件) | 【総3】通常3(単一Style)+F0+LR後0 | 統一judge+長さ+disfluency。text-gate非OKならTTSなしでSTOPPED | なし | × | —(5 role外。承認根拠なし: U-08) | 3NG→STOPPED→Lock→Audio Gate BLOCK | **C** — 仕様記録なし(C: U-08) | L5 | 実走なし(att=1)=未検証 |
| Z | Standard | [Z-A2-NARR] 地の文(narrator) full_story_part{n}_c{k}・100語超はchunk _k{j}(6%減速・PD06) | 【総4】通常2(PD06)+F1+LR後1(減速後取り直しは通算3の内数) | 統一judge NG全種+長さ+repetition QA。減速後再検証NGも通算3の残予算で取り直し。無音/異常長=技術失敗扱い | F-Style: 3回目=minimal instruction(Secondary必須)。直前にcd | ○ | 標準2+F1の全NG+cs=True(clip_idがFULL_STORYに解決)。書換え1回→LR再TTS1回(minimal Style・cdなし・force_secondary) | LR None→STOPPED→Lock(HUMAN_REVIEW_REQUIRED)→全clip処理後にFamilyZTtsClipFailedStop rc=2(HR+STOP。STOP sentinelは作らない)。減速後最終NGはLRなしでfinalize→HR Lock | **A** — 一致(Std chunk経由のLR/F-Style/exhaustはruntime未検証)。B: U-02 / C: U-09 | L4(→L3) | Std LR実走1件(the_monkeys_paw run_sf_prod_01 part1_c10・非chunk時代)、cd発生 a2 6件(重複あり)。Std chunk実run: 正常経路のみ(LR/強制NG/exhaust未取得) |
| Z | Standard | [Z-A2-DIALOGUE-CTX] 登場人物のセリフ(dialogue) policy=fz_ctx_v1(新規runの既定) | 【総3】ctx2+F-Prompt1(従来方式)+LR後0(4回目なし) | 統一judge NG全種+長さ+disfluency/repetition QA。NG判定はattempt直後。無音/異常長=attempt内でminimal fallback | F-Prompt: 3回目=ctx Style→従来Dialogue Style(文脈・話者・前後セリフ除外)。直前に固定600秒(5秒刻みSTOP確認・起点=2回目NG確定時刻)。F-Tech: attempt内でminimal短文Styleへ | × | —(未配線。ユーザー原文は『NG→既存のLocal Rewrite処理へ』と記載: U-05) | STOPPED→Lock→state TERMINAL_NG→全clip後rc=2(HR+STOP) | **C** — 前段(ctx→ctx→cd→従来方式・総3)は一致。LR段=仕様記録なし(C: U-05) | L8(attempt_hook=er122 policy) | E-1〜E-5(Std): 正常/強制NG→cd600.001s→従来方式PASS/cd中kill→再開/3回強制NG→TERMINAL_NG+HR Lock+rc=2。強制NGはrepetition QA gate上書き=ASR由来のn=3 HRQ追記は未観測 |
| Z | Standard | [Z-A2-DIALOGUE-LEGACY] 登場人物のセリフ(dialogue) policy=legacy(既存run・ロールバック時) | 【総3】通常3(同一従来Style)+F0+LR後0 | 統一judge+長さ+QA(ctxと同じ) | F-Techのみ(attempt内minimal)。cdなし | × | —(未配線。理由の承認記録なし: U-05) | STOPPED→Lock→rc=2 | **C** — 仕様記録なし(C: U-05) | L8(attempt_hookなし) | 過去Z run dialogue a2 347 entry(重複あり): 2回以上16/3回以上6/notOK 4(the_open_window part1_c14・part3_c2が3回STOPPED) |
| Z | Standard | [Z-A2-TOPIC] Topic intro(topic_intro_en・Aoede) | 【総3】通常2+F1+LR後0 | 統一judge | F-Style: 3回目=minimal。cdなし | × | —(clip_id topic_intro_enがresolve_narrative_roleで未分類=cs=False。5 roleのTopic introには含まれるはず: U-06) | STOPPED→Lock(HUMAN_REVIEW_REQUIRED)→全clip処理後にFamilyZTtsClipFailedStop rc=2(HR+STOP。STOP sentinelは作らない) | **B** — 不一致(B: U-06) | L3 | Z topic_intro a2 34 entry: 再試行0・notOK 0=cd/LRの実データなし |
| Z | Standard | [Z-A2-JA] 日本語: japanese_title/preview/comment_1〜3 | 【総3】通常2+F1+LR後0 | JA統一judge(Primary→Secondary+全文Validator+SCG)+長さ | F-Style: 3回目=minimal。cdなし | × | —(日本語はLRなし。ユーザー2026-10-15) | STOPPED→Lock(HUMAN_REVIEW_REQUIRED)→全clip処理後にFamilyZTtsClipFailedStop rc=2(HR+STOP。STOP sentinelは作らない)(最終slot NGで日本語HRQ追記) | **A** — 一致 | L7 | a2 comment 102 entry(重複あり): 2回以上22/3回以上7/notOK 7、LR=0 |
| Z | Standard | [Z-A2-KPEN] Key Phrase英語 kp{r}_en | 【総4】前段2(K2)+後段2(F-Style・ENGLISH_LOCK)+LR後0 | 3-ASR多数決+disfluency。Azure circuit open時は段2をskip(技術STOP) | F-Style: K2→ENGLISH_LOCK | × | —(ユーザー2026-09-26 (C)明示除外) | 通算4 NG→STOPPED→Lock(HRQ=通算4のみ)→rc=2 | **A** — 一致 | L6 | a2 kp_english 138 entry: 再試行0 |
| Z | Standard | [Z-A2-KPJA] Key Phrase日本語意味 kp{r}_ja | 【総3】通常2+F1+LR後0 | JA統一judge | F-Style: 3回目=minimal | × | —(日本語・KP) | STOPPED→Lock(HUMAN_REVIEW_REQUIRED)→全clip処理後にFamilyZTtsClipFailedStop rc=2(HR+STOP。STOP sentinelは作らない) | **A** — 一致 | L7 | a2 kp_japanese_meaning 138 entry: 2回以上1 |
| Z | Advanced | [Z-B1B-NARR] 地の文(narrator) full_story_part{n}_c{k}・100語超はchunk _k{j}(PD06) | 【総4】通常3(同一PD06)+F0+LR後1 | 統一judge NG全種+長さ+repetition QA | F-Techのみ(attempt内。品質NGにFallbackなし)。attempt3直前にcd600秒 | ○ | 通算3回全NG+cs=True。書換え1回→LR再TTS1回(PD06を渡さず標準ENGLISH_STYLE_PREFIX: U-02。再入に上限なし: U-01) | LR None→STOPPED→Lock(HUMAN_REVIEW_REQUIRED)→全clip処理後にFamilyZTtsClipFailedStop rc=2(HR+STOP。STOP sentinelは作らない) | **A** — 一致。B: U-01, U-02 | L2 | Adv LR実走9件(melos run_e2e_01/02/04・run_kga3_off_z_01・run_kgcpw_z_01/_e5_a2_01/_e5_b1b_01、the_open_window run_sf_prod_01_preserve_20261023)、cd b1b 3件。LR再入深さ2の実例あり(run_e2e_01 part1_c18) |
| Z | Advanced | [Z-B1B-DIALOGUE-CTX] 登場人物のセリフ(dialogue) policy=fz_ctx_v1(新規runの既定) | 【総3】ctx2+F-Prompt1+LR後0(減速後NGも通算に数える) | 統一judge+長さ+QA+減速後(atempo約1.06高速化)再検証 | F-Prompt(3回目・直前に固定600秒)+F-Tech(attempt内) | × | —(未配線: U-05) | STOPPED→finalize/Lock→TERMINAL_NG→rc=2。M-3(ii): 行会計で従来方式(3回目)未到達のまま停止する稀ケースあり(U-07) | **C** — 前段一致。LR段=記録なし(C: U-05)/M-3(ii)=C(U-07) | L8(→n3.generate_with_a2_slowdown_outer_loop) | E-1/E-2/E-4/E-6(Adv)実走(強制NGあり)。M-3(i)併発は未観測 |
| Z | Advanced | [Z-B1B-DIALOGUE-LEGACY] 登場人物のセリフ(dialogue) policy=legacy | 【総3】通常3(同一従来Style・減速後NGも通算3に含む)+F0+LR後0 | 統一judge+長さ+QA+減速後再検証 | F-Techのみ(attempt内)。cdなし | × | —(未配線。理由の承認記録なし: U-05) | STOPPED→finalize/Lock→rc=2 | **C** — 仕様記録なし(C: U-05) | L8 | Z b1b dialogue 369 entry(重複あり): 2回以上14/3回以上5/notOK 4 |
| Z | Advanced | [Z-B1B-TOPIC] Topic intro(topic_intro_en・Charon) | 【総3】通常3(同一Style)+F0+LR後0 | 統一judge | F-Tech(attempt内のみ。品質NGにFallbackなし。L1共通) | × | —(clip_id未分類=cs=False: U-06) | STOPPED→Lock(HUMAN_REVIEW_REQUIRED)→全clip処理後にFamilyZTtsClipFailedStop rc=2(HR+STOP。STOP sentinelは作らない) | **B** — 不一致(B: U-06) | L1 | b1b topic_intro 34 entry: 再試行0 |
| Z | Advanced | [Z-B1B-PREVCOM] Preview英語(E1)/Comment 1-3英語(E2_UPBEAT) | 【総4】通常3(同一Style)+F0+LR後1 | 統一judge+disfluency QA | F-Tech(attempt内のみ。品質NGにFallbackなし)。attempt3直前にcd600秒 | ○ | 通算3回全NG+cs=True。LR再TTS=1回(元Style転送) | LR None→STOPPED→Lock(HUMAN_REVIEW_REQUIRED)→全clip処理後にFamilyZTtsClipFailedStop rc=2(HR+STOP。STOP sentinelは作らない) | **A** — 一致(LR実走なし=未検証)。B: U-01 | L1 | b1b comment 102 entry: 2回以上1・LR 0=LR/cd実走なし=未検証 |
| Z | Advanced | [Z-B1B-KPEN] Key Phrase英語 kp{r}_en | 【総4】前段2(K2)+後段2(F-Style・ENGLISH_LOCK)+LR後0 | 3-ASR多数決+disfluency | F-Style: K2→ENGLISH_LOCK | × | —(ユーザー2026-09-26 (C)明示除外) | 通算4 NG→STOPPED→Lock→rc=2 | **A** — 一致 | L6 | b1b kp_english 136 entry: 2回以上5・notOK 3・fallback 3 |
| Z | Advanced | [Z-B1B-KPEXPL] Key Phrase英語解説 kp{r}_explanation_en(P7) | 【総3】通常3(同一P7)+F0+LR後0 | 統一judge+disfluency | なし | × | —(5 role外・cs未指定: U-08) | STOPPED→Lock(HUMAN_REVIEW_REQUIRED)→全clip処理後にFamilyZTtsClipFailedStop rc=2(HR+STOP。STOP sentinelは作らない) | **C** — 一致(列挙外)。除外の承認記録は未確認(C: U-08) | L5 | b1b kp_explanation 130 entry: 再試行0 |

注: Zのshell/番号音声は既存Master資産のコピー（TTSなし）のため行に含めない。Y-B-00（固定mp3）はTTSなしの参考行。

## 3. 星取表②: Local Rewriteの適用有無と理由(承認根拠つき)

### 3-1. 全部位の表

理由区分(原文§4): ①ユーザーが明示的にRewriteを不採用 ②品質保護等で承認済み仕様として対象外 ③実装当時の技術的制約 ④共通仕様の適用漏れ・配線漏れ ⑤設計・承認記録に理由なし。『セリフだから書き換えられない』『原作保護のため』といった説明は、実際の設計・承認根拠が存在する場合だけ『既存の決定理由』として記載し、Claude/Fable/Opusの解釈は§3-3の『所見』へ分離した。

| Family | 音声部位 | Rewrite | 理由区分(原文§4の5区分) | 不適用・例外の理由(記録に基づく事実) | ユーザー承認の有無 | 根拠資料 | 分類 | 関連ID・併記 |
|---|---|---|---|---|---|---|---|---|
| X | Adv 英語5 role(topic_intro/preview/comment_1〜4/本文・chunk/in_one_line) | ○ | —(適用部位) | 2026-09-26 (A)(C)(D)で承認。2026-10-19で発動条件を『初回→最大2回再生成→なおNGならRewrite』に確定 | 有: 2026-09-26 (A)LR+Natural English QA・(C)5 role適用・(D)HR前にLR、2026-10-19 発動条件(『両ASR合意』削除・初回→最大2回再生成→なおNGならRewrite) | DECISION_LOG.md:9711-9716; docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md §3-4; CURRENT_SPEC.md:2176,2886 | A | B: U-01(再入)・U-02(Style脱落)/C: U-03(非ASR起因NGで不発) |
| X | Std 英語(topic_intro/本文・chunk/in_one_line) | ○(内側が標準2+F1を使い切った場合) | —(適用部位) | 同上。ただし6%減速後の再検証が最終NGの場合はLRなしで直接HR(コード内docstringのみ: n3:317-319。AUW 委任_06eが『ユーザー原文L39-49「3回NGでLR/HR」の末端』と記録) | 有(適用部位)。減速後最終NGでLRなしは逐語承認を未確認 | DECISION_LOG.md:9711-9716; docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md §3-4; CURRENT_SPEC.md:2176,2886; er003_v1_n3_01_tts_generate.py:309-319 | A | B: U-02/C: U-09 |
| X | 日本語(japanese_title/preview/comment/KP日本語意味/ポイント解説) | × | ①+② | 区分①+②: ユーザー2026-10-15『日本語Local Rewrite: 現行の英語用機構を機械的に流用しない。安全な実装が成立していない場合はHuman Reviewへ』『日本語: 現時点では原則Human Review』(時限表現)。技術的背景は開発側記録(identify_ng_spanが純日本語でfound=False/OPEN-290(E))として区別 | 有(2026-10-15) | docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md:148,160; CURRENT_SPEC.md:2885(3); OPEN_ITEMS.md:793(OPEN-290) | A | 追跡: U-20(時限表現・OPEN-290未クローズ) |
| X | Key Phrase英語phrase(Adv/Std) | × | ①+② | 区分①+②: ユーザー2026-09-26 (C)『適用しない=Heading readout、Key Phrase』(要旨。除外理由の逐語記録なし)+2026-10-15『Key Phrase: 学習対象の表現を別表現に置き換えない』(…_01.md:161)。KPは4回構成(CURRENT_SPEC.md:2885(1)) | 有 | DECISION_LOG.md:9711-9716; …ASR-TTS-UNIFIED…_01.md:147,161; CURRENT_SPEC.md:2885(1); er020:117-121 | A |  |
| X | Adv Key Phrase英語解説 | × | ⑤ | 区分⑤: 5 role(2026-09-26)にも除外2 role(Heading,Key Phrase)にも名指しされない(resolve_narrative_role=None)。『LRは5 roleのみ』という列挙型の正式仕様はあるが、KP解説/shellを外した理由の記録はない。er019:1212-1213は『TTS①②③、3回NGでLR/HR』に揃えると書くがLR配線なし | 不明 | CURRENT_SPEC.md:2873,2885(2),2886; er019_family_x_audio_production_runner_01.py:1202-1215; er020:121,135-176 | C | U-08 |
| X | shell固定英語(welcome/preview_intro/key_phrases_intro/full_story_intro/num_one〜five) | × | ⑤ | KP解説と同じ(role=None・csを渡さない) | 不明 | shared_narration:220-233; er020:135-176 | C | U-08 |
| Y | Adv/Std topic_intro・Adv preview/comment | ○ | —(適用部位) | 共通核のLRがそのまま有効(Yは専用経路を持たない)。YL-A05『再試行・fallback・LR(英語5role)→HR Lock』を適用 | 有(5 role適用の承認。Yへは台帳YL-A05=APPLYと2026-10-25 ユーザー原文§4-1の一般規定) | DECISION_LOG.md:9711-9716; docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md §3-4; CURRENT_SPEC.md:2176,2886; SPEC_LEDGER_03.md YL-A05 | A | B: U-01 |
| Y | Adv/Std 本文8 segment(y_lead/y_intro_1〜3/y_voice_1〜3/y_closing)+chunk | ○(LR成功後の採用にはY Gateで人間承認が要る) | —(LRは適用)。採用側のGateはU-16 | LR自体は有効(connected_speech_enabled_for(y_*)=FULL_STORY)。成功してもy_style_gateがLOCAL_REWRITE_RECOVERYをBLOCK(record_human_approvalが必要)。同型のXのM3はOPEN-312(LR再TTSがrole Styleを落とす)の検知で、REGISTER #6=Deferred | LR適用は有(上記)。Y Gateの人間承認要件にはY固有のユーザー承認なし | er121_family_y_audio_01.py:706-709; er019_family_x_style_profile_01.py:742-743; OPEN_ITEMS.md:815; USER_DECISION_REGISTER_01.md:24 | A(LR)/C(Gate: U-16) | B: U-01,U-02/C: U-03(repetition単独NG) |
| Y | 日本語(japanese_title/支援文/KP日本語意味/ポイント解説) | × | ①+② | 区分①+②: ユーザー2026-10-15『日本語Local Rewrite: 現行の英語用機構を機械的に流用しない。安全な実装が成立していない場合はHuman Reviewへ』『日本語: 現時点では原則Human Review』(時限表現)。技術的背景は開発側記録(identify_ng_spanが純日本語でfound=False/OPEN-290(E))として区別(Y棚卸しは『原文L146』のpathを特定できなかったが、実ファイルは左記…_01.md:148,160) | 有(2026-10-15) | docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md:148,160; CURRENT_SPEC.md:2885(3); OPEN_ITEMS.md:793(OPEN-290) | A |  |
| Y | Key Phrase英語(Adv/Std) | × | ①+② | 区分①+②: ユーザー2026-09-26 (C)『適用しない=Heading readout、Key Phrase』(要旨。除外理由の逐語記録なし)+2026-10-15『Key Phrase: 学習対象の表現を別表現に置き換えない』(…_01.md:161)。KPは4回構成(CURRENT_SPEC.md:2885(1)) | 有 | DECISION_LOG.md:9711-9716; …ASR-TTS-UNIFIED…_01.md:147,161; CURRENT_SPEC.md:2885(1); er020:117-121 | A | 前段がK2でなくMINIMAL(U-15) |
| Y | Adv Key Phrase英語解説 | × | ⑤ | 区分⑤: 5 role(2026-09-26)にも除外2 role(Heading,Key Phrase)にも名指しされない(resolve_narrative_role=None)。『LRは5 roleのみ』という列挙型の正式仕様はあるが、KP解説/shellを外した理由の記録はない。er019:1212-1213は『TTS①②③、3回NGでLR/HR』に揃えると書くがLR配線なし | 不明 | CURRENT_SPEC.md:2873,2885(2),2886; er019_family_x_audio_production_runner_01.py:1202-1215; er020:121,135-176 | C | U-08 |
| Y | shell固定英語9 | × | ⑤ | KP解説と同じ(role=None・csを渡さない)。Y runはStore再利用 | 不明 | shared_narration:220-233; er121_family_y_audio_01.py:440 | C | U-08 |
| Y | Intro/Notification/Outro(固定mp3) | — | — | TTSなし。音声ファイルの読込のみ | — | er121_family_y_audio_01.py:773-775 | — |  |
| Z | 地の文(narrator) Std/Adv・chunk | ○ | —(適用部位) | clip_id `full_story_part{n}_c{k}[_k{j}]` がFULL_STORYに解決(er020:152-156)。2026-10-19決定が適用 | 有: 2026-09-26 (A)LR+Natural English QA・(C)5 role適用・(D)HR前にLR、2026-10-19 発動条件(『両ASR合意』削除・初回→最大2回再生成→なおNGならRewrite) | DECISION_LOG.md:9711-9716; docs/pm/delegation_log/2026-10-19_FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md §3-4; CURRENT_SPEC.md:2176,2886 | A | B: U-01,U-02/C: U-09 |
| Z | Adv Preview英語・Comment英語 | ○ | —(適用部位) | PREVIEW/COMMENT roleに解決 | 有: 2026-09-26 (A)LR+Natural English QA・(C)5 role適用・(D)HR前にLR、2026-10-19 発動条件(『両ASR合意』削除・初回→最大2回再生成→なおNGならRewrite) | CURRENT_SPEC.md:2176 | A | LR実走なし=未検証(U-23) |
| Z | Topic intro(topic_intro_en、Std/Adv) | × | ④ | 承認済み5 roleにTopic introは含まれるが、Zのclip_id `topic_intro_en` が未分類(cs=False)。IMPLEMENTATION_DESIGN_02.md:34『既存C/Xと同じ扱い』はXについて事実と異なる | Z topic introを除外する承認記録は未確認 | CURRENT_SPEC.md:2176; er020:112,156; RUNTIME_EVIDENCE_02.md:18 | B | U-06 |
| Z | 日本語(japanese_title/preview/comment/KP日本語意味)Std | × | ①+② | 区分①+②: ユーザー2026-10-15『日本語Local Rewrite: 現行の英語用機構を機械的に流用しない。安全な実装が成立していない場合はHuman Reviewへ』『日本語: 現時点では原則Human Review』(時限表現)。技術的背景は開発側記録(identify_ng_spanが純日本語でfound=False/OPEN-290(E))として区別 | 有(2026-10-15) | DECISION_LOG.md:21596-21598; docs/pm/delegation_log/2026-10-15_ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md:148,160; CURRENT_SPEC.md:2885(3); OPEN_ITEMS.md:793(OPEN-290) | A |  |
| Z | Key Phrase英語(Std/Adv) | × | ①+② | 区分①+②: ユーザー2026-09-26 (C)『適用しない=Heading readout、Key Phrase』(要旨。除外理由の逐語記録なし)+2026-10-15『Key Phrase: 学習対象の表現を別表現に置き換えない』(…_01.md:161)。KPは4回構成(CURRENT_SPEC.md:2885(1)) | 有 | DECISION_LOG.md:9711-9716; …ASR-TTS-UNIFIED…_01.md:147,161; CURRENT_SPEC.md:2885(1); er020:117-121 | A |  |
| Z | Adv Key Phrase英語解説 | × | ⑤ | 区分⑤: 5 role(2026-09-26)にも除外2 role(Heading,Key Phrase)にも名指しされない(resolve_narrative_role=None)。『LRは5 roleのみ』という列挙型の正式仕様はあるが、KP解説/shellを外した理由の記録はない。er019:1212-1213は『TTS①②③、3回NGでLR/HR』に揃えると書くがLR配線なし(Z doc: 『5 role列挙外のため非適用』) | 不明 | CURRENT_SPEC.md:2873,2885(2),2886; er019_family_x_audio_production_runner_01.py:1202-1215; er020:121,135-176 | C | U-08(Z docはAとしたがC(低)へ統一) |
| Z | 登場人物のセリフ(dialogue) ctx方式(Std/Adv) | × | ⑤(区分①不採用の記録なし・②名指し除外なし・③技術的制約の記録なし・④配線漏れか意図的かは記録から確定不能) | LR呼出がgenerate_voice_body_wide_marginに存在しない(git log -S local_rewrite → 0件)。LR配線(2026-09-26 commit cdcbf37b6)は er012_b を変更していない。Fable判断J-1(DESIGN_02.md:6,61)『LR新設は新仕様でユーザー承認事項』は設計判断でありユーザー承認ではない | なし(ユーザー原文は『NG→既存のLocal Rewrite処理へ』と書く。除外・不採用の承認は記録なし) | FZ-CONTEXT…_USER.md:30,32,36,136; DESIGN_02.md:6,61; OPUS_REVIEW_01.md:63-70; EXISTING_SPEC_CHECK_01.md §2,§3; OPEN-528 Deferred(1) | C | U-05(時系列は§3-2) |
| Z | 登場人物のセリフ(dialogue) legacy方式(Std/Adv・既存run) | × | ⑤ | ctx導入前から未配線。理由は記録なし(全Z run dialogue 667 entryでaudio_text_deviation=0) | なし | EXISTING_SPEC_CHECK_01.md §2 | C | U-05 |
| Z | shell/番号音声(provision_shellで既存Master資産をコピー) | — | — | TTSなし(コピー) | — | er063:1941-1964 | — |  |

星取表②の行数=22（A=12 / B=1 / C=7 / 対象外(—)=2）。分類『A(LR)/C(Gate)』は本文8 segment行（LR=A、採用側Y Gate=C）。

### 3-2. Zセリフ(dialogue)にLRが無い件の時系列(事実のみ)

| 日付 | 出来事(誰が何を) | 根拠 |
|---|---|---|
| 2026-09-08 | `er012_b_family_voices_production_01.py` 新規作成(commit 1a7f00810)。LR呼出なし | git log |
| 2026-09-26 | ユーザー決定(B)10分cooldown・(C)Connected Speech/LR適用範囲=『Full Story/Comment/Preview/Topic intro/In One Line』、適用しない=『Heading readout、Key Phrase』・(D)HR前にLR。配線commit cdcbf37b6の変更ファイルは `n3_tts_generate`・`news_tail_fix`・`voice01_generate`・`er020`(新規)とそのtestで、`er012_b` を含まない(本調査でも `git show --stat` を再確認)。`er012_b` のcs引数は作成時(1a7f00810)からあるが、渡し先はjudge内のConnected Speech層(判定)のみでcooldown/LR呼出は無い。同commitの `…PRODUCTION-WIRING-01_REPORT.md` §2 role別表にDialogue/Voices行なし。**ユーザー決定にDialogue/Voicesの名指しは無い** | DECISION_LOG.md:9711-9716; CURRENT_SPEC.md:2176 |
| 2026-10-15 | ユーザー決定(統一フロー): 『3回とも不合格の場合、既存の安全条件に従いLocal RewriteまたはHuman Reviewへ進む』『Dialogue: 複数Voiceの区分・話者帰属・既存Segment構造を維持する』。**dialogueのLR要否は述べていない** | DECISION_LOG.md:21542,21596-21599; …ASR-TTS-UNIFIED…_01.md |
| 2026-10-19 | ユーザー決定(LR発動条件): 『両ASRが同じ箇所の誤読に合意すること』を削除、基本フロー=初回→最大2回再生成→なおNGならRewrite。**音声部位・Family・dialogueを指定していない**(文脈はZナレーション `Melos drank`→`He drank`) | …FAMILY-Z-AUDIO-QA-DEFECT-RESOLUTION-01_USER.md §3-4; CURRENT_SPEC.md:2886 |
| 2026-10-26 | ユーザー原文(Z文脈・感情付きTTS正式採用): 『3回目: 従来方式TTSへFallback…NG → 既存のLocal Rewrite処理へ』(:30)『Local Rewriteで解決できなければ、既存のHuman Review／STOP規則に従う』(:32)『Local Rewriteも既存の回数上限・安全条件を維持』(:36)『3回ともNG → Local Rewrite／Human Review／STOPへ正しく移行』(:136) | …FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md:30,32,36,136 |
| 2026-10-26 | 調査(Fable/Sonnet): dialogueにLR未配線の事実を確認(`generate_voice_body_wide_margin`にLR/cooldown呼出なし) | EXISTING_SPEC_CHECK_01.md §2-§3 |
| 2026-10-26 | **Fable判断J-1**: 『Z dialogueにはLRが未配線。新設せず、3回NG→STOPPED→HR Lock→STOP(原文「Local Rewriteで解決できなければ既存のHuman Review／STOP規則」を満たす)。LR新設は古典作品のセリフをLLMで書換える音声と表示本文の乖離を生む新仕様でありユーザー承認事項』。Opusも『LRを新設せず…既定がユーザー原文に最も忠実。ただしユーザーはLRが存在する前提で書いた可能性が高い。非ブロッキング扱いで埋もれさせず完了報告に明示すること』。CLOSEOUT_01/OPEN_TRACKING_01/OPEN-528 Deferred(1)/UDRは『判断候補・非blocking』として記録 | DESIGN_02.md:6,61; OPUS_REVIEW_01.md:63-70; CLOSEOUT_01.md:25,28; OPEN_ITEMS.md OPEN-528; USER_DECISION_REGISTER_01.md:434,444 |
| 2026-10-26(後日) | ユーザー: 『Local Rewriteは未配線であり、現行ではHuman Review／STOPに進む。…Local Rewriteについては次項の調査結果と照合すること。Local Rewriteの新仕様を独断で追加しない』『特にRewrite不適用の理由は、既存記録で確認できるものと、Claude/Fableの新たな見解を区別すること』『本件は調査のみ。結果を待たずに無断でRewriteの仕様変更・Production改修を行わない』 | …FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_USER.md:69-73,90,94 |

**事実としての整理**: Zセリフの『LRなし』は、**ユーザー承認による除外ではない**(不採用・名指し除外の記録はどこにも無い)。**既存LRが無い状態で、Fableが『HR/STOP直行』を選んだ**(J-1。Opusが同調)。**ユーザーは後日その状態を認識し、採否判断を本調査後へ保留した**。したがって分類は **C(ユーザー判断待ち)**。27-3では『真に新しい判断(D)』の候補(§8-1)。

### 3-3. 所見(事実ではない。Claude/Fable/Opusの見解)

1. J-1の理由『音声と表示本文の乖離』は、Z narrator LR(ユーザー承認下で運用済み。audio_text_deviationを記録、表示本文は不変)にも当てはまる。dialogueだけが乖離を理由に除外される根拠としては弱い可能性がある。一方、dialogueは話者の台詞自体を変える点で性質が異なるという見方もあり、判断はユーザー事項(FAMILY_Z_01 所見2)。
2. 実装履歴(`er012_b`が2026-09-08作成、2026-09-26のLR配線で`er012_b`を触っていない)からは、dialogueが未配線なのは『配線対象の列挙に入らなかった結果』の可能性がある。ただし設計・承認記録に理由が無く、『意図的な除外』か『配線漏れ』かは記録から確定できない(FAMILY_Z_01 所見1)。
3. X/Y/Zの『LR有無の差』の大半は呼出関数の違い(L1〜L3 vs L5〜L8)で説明でき、Family固有の承認よりも実装経路の履歴に依存している可能性がある(COMMON_CORE_01 所見4)。
4. dialogueにLRを配線する場合の設計案は `DESIGN_01.md:122` に既にある(ctx policyのn=3の後に1回だけLR再TTS・従来style・max_attempts=1・既存`lr_used==0`・累積15回guard維持)。ctx方式は自前cooldownを持つため、csに載せると二重になる(FAMILY_Z_01 所見3)。
5. KP解説とshell固定英語にLRが無い理由は、『5 role名指し』という列挙型の承認が、名指しされなかった部位を暗黙に除外した結果とみられる(FAMILY_X_01 所見3)。失敗実績0で実害は小さい。

## 4. Family・部位別の実際の処理フロー

### 4-0. 共通部品(全Family共通。差異は各節で明記)

- **1 attempt**: TTS呼出(技術エラーは即時に最大1回再呼出・待機なし=別枠)→(L1/L2のみ)トリム・異常長検査→ASR(J: Primary→NGならSecondary1回)+長さ+(部位により)disfluency/repetition QA→全てPASSで採用。Primary NG・Secondary PASS=`PASS_WITH_WARNING`(自動採用+事後試聴リスト)。
- **cooldown**: 固定600秒の単一sleep(STOP sentinel確認なし。Z dialogue ctxのみ5秒刻み確認)。通算最終attempt(`max_attempts>=3`かつ`attempt==max_attempts`)の直前、cs=Trueのときだけ。LR再TTS(`max_attempts=1`)では発動しない(er020:57-93)。
- **LR**(`run_local_rewrite_recovery` er020:739): ①最終attemptのPrimary転写とcanonicalの最初の語差分(無し→`HUMAN_REVIEW_LOCKED_NO_NG_SPAN`→HR) ②Luna(`gpt-5.6-luna`)が局所書換え候補5件 ③7 Gate QA+全文性(+In One Lineは文数不変Gate) ④全PASSのうち`unchanged_ratio`最大1本(無し→`…NO_CANDIDATE_PASSED_QA`→HR) ⑤`retts_fn(書換え後文)`1回(NG→`…RETTS_FAILED`→HR)。再TTS後は書換え後文を正解として統一judge+元と同じQAを再実施。HR Lockのkeyと人間承認は元の原稿のまま。
- **HR**: 最終slot NG→`guarded_generate`→`record_outcome`→STOPPED→Lock(HUMAN_REVIEW_REQUIRED)。HRQ行は最終slotのASR judge NG時(LR前)に書かれる。累積TTS15回/ASR60回でBUDGET_GUARD。同一canonical_textは`approve_regenerate`(次の1回だけ)または`record_human_approval`まで0 API call。
- **resume/regeneration**: `_generate_or_reuse`は前回OKかつcanonical_text・style_version一致のときだけ再利用。それ以外は再生成だが、Lockが残っていれば0 API callで返る。本文(canonical sha)が変わればLockは無効(新版扱い)。

### 4-1. P1 Adv英語(同一Style3回+cooldown+LR)— X Adv topic_intro/preview/comment/本文/chunk/in_one_line、Y Adv topic_intro/preview/comment/本文8、Z Adv narrator/Preview/Comment(L1またはL2)

```
通常TTS① (role Style・技術別枠あり) → J → [disfluency/repetition QA]
 PASS → 採用
 NG → 通常TTS② (同一Style・待機0)
 NG → 【cooldown 固定600秒】(cs=True) → 通常TTS③ (同一Style) → NG判定時にHRQ行(LR前に書込)
 NG → LR: NG span特定(語差分なし→NO_NG_SPAN→HR) → Luna候補5 → 7 Gate → 1本採用(なし→HR)
      → LR再TTS×1 (v1。L2=role Style脱落/L1=Style保持: U-02)
         PASS → 採用(LR_REWRITTEN警告付PASS_WITH_WARNING。record_outcome=RESOLVED)
         NG  → 同関数内でLR再入(U-01: カウンタなし) … 理論上非有界
 全て失敗 → STOPPED → Lock(HUMAN_REVIEW_REQUIRED) → runner終端(2-1の差)
F-Tech: 技術失敗/発話区間検出失敗(L2は異常長も)→同attempt内でminimal短文Styleに即再TTS(attemptは進まない)
```
表記: 通常3+Fallback0+LR後1=総4(再入時は+k)。
**部位ごとの差**: preview/comment(X・Y・Z)・Y topic_intro・X topic_introは**L1**(LR再TTSはStyle保持、`disfluency_qa`あり[topic_introを除く]、`repetition_qa`なし)。本文/chunk/in_one_line(X・Y・Z)は**L2**(本文/chunkは`repetition_qa`あり、in_one_lineはdisfluency QA。LR再TTSはrole Style脱落)。X in_one_lineはLRに文数不変Gate(Family Xスコープ)が付く。chunkは各chunkが単独で上記を通り、親は`CHUNKS_NOT_ALL_VALIDATED`(承認で迂回不可)。Y本文8(+chunk)はLR成功後にY Gateが`LOCAL_REWRITE_RECOVERY`をBLOCK→ユーザー承認要(U-16)。

### 4-2. P2 Std英語(標準2+F-Style1+cooldown+LR+6%減速)— X Std topic_intro/本文/chunk/in_one_line、Y Std topic_intro/本文8、Z Std narrator(L3、本文系はL4)

```
標準TTS① (role Style) → J → NG → 標準TTS② (同一Style)
 NG → 【cooldown 600秒(通算3回目直前)】 → F-Style: minimal短文StyleのTTS③ (Secondary必須=force_secondary) → NG判定時にHRQ行
 NG → LR → LR再TTS×1 = _run_a2_minimal_fallback_attempt直呼び(minimal Style・force_secondary・再入なし)
      PASS → 採用 / NG → STOPPED → Lock
[本文・chunk・in_one_lineのみ] 内側OK → 6%減速(*_original.wav退避) → 減速後wavをJで再検証(LR採用時は書換え後文が正解)
   NG → 通算生成回数<3なら通常ペースから取り直し(残予算をmax_attemptsに)。通算3回目でNG → LRなし → finalize_a2_slowdown_final_ng → Lock+HRQ(U-09)
```
表記: 通常2+Fallback1+LR後1=総4(減速後取り直しは通算3の内数。LR再TTS後は減速後再検証をさらに1回)。X Std topic_introはcsを渡し、Z Std topic_intro_enは渡さない(U-06)。

### 4-3. P3/P4 Zセリフ(dialogue)— L8 `generate_voice_body_wide_margin`

```
[ctx方式(新規runの既定)]
Lock確認 → [感情notes: level単位1 LLM call(保存済みなら0)]
→ n=1 ctx Style TTS → J → PASS採用 / NG → n=2 ctx Style TTS (待機0) → J → PASS採用
   NG → 【固定600秒(5秒刻みSTOP確認・起点=2回目NG確定時刻・再開時も実時間で10分)】
      → n=3 従来Dialogue Style (style_prefix_override=None) → J → PASS採用
      NG → STOPPED → record_outcome → Lock → state TERMINAL_NG → (LR段なし) → 全clip後 rc=2
各attempt内: 技術失敗/発話区間検出失敗/異常長 → 同nでminimal_fallback 1回(F-Tech)
[Adv] 各passのPASS後にatempo約1.06高速化→減速後再検証。ctxのnは外側/内側ループをまたいで継続(M-3(ii): 行会計が先に尽きると従来方式未到達でSTOP: U-07)
[legacy方式] 同一従来Style①②③ → STOPPED → Lock → rc=2 (cdなし)
```
表記: ctx=通常2+Fallback(F-Prompt)1+LR後0=総3(4回目なし)。legacy=通常3+F0+LR後0=総3。ユーザー原文の『3回目NG→既存のLocal Rewrite処理へ』段は未配線(U-05)。

### 4-4. P5 日本語(Std)— L7

```
[TTS前gate: placeholder/禁止記号/外来語トークン → 該当時はTTSなしでSTOPPED+HRQ]
→ 標準TTS① (JA Style) → JA統一judge(Primary NG→Secondary1回+全文Validator+SCG)+長さ → NG → 標準TTS②
→ NG → F-Style: JA minimal instructionでTTS③ → NG → STOPPED → Lock + 日本語HRQ(slot3) → 終端
```
表記: 通常2+Fallback1+LR後0=総3。LRなし・cooldownなし(JA関数にLR呼出が無い。csを持たない)。X(japanese_title/preview/comment/KP日本語意味/ポイント解説)・Y・Zで同一。

### 4-5. P6 Key Phrase英語phrase(Adv/Std)— L6

```
前段(X/Z: K2 styled、Y: default profileのためMINIMAL) ①② 各回3-ASR多数決(OpenAI/Azure/Whisper・2/3、Primary+Secondary両方必須)
 NG → F-Style: ENGLISH_LOCK prefix ③④ (Azure/Whisper circuit open時は後半skip=技術STOP)
 最終slot(通算4)NG → STOPPED → Lock + 英語HRQ(slot4のみ) → 終端
```
表記: 通常2+Fallback2(F-Style)+LR後0=総4(全体『3回』の唯一の例外)。cooldownなし。

### 4-6. P7 LRなしの英語 — Adv KP英語解説(L5)、shell固定英語(L1・cs未指定)、Z topic_intro_en(Std=L3/Adv=L1、cs=False)

```
KP解説: 通常①②③(同一Style・disfluency QA) → 全NG → STOPPED → Lock + 英語HRQ(slot3) → 終端 (text-gate非OKならTTSなしでSTOPPED)
shell固定英語: Master Audio Store照会(hitなら生成0)→ miss時のみ ①②③(F-Techあり) → STOPPED → Lock + HRQ → SharedNarrationBlockedError(runtime停止)
Z Std topic_intro_en: 標準①② → F-Style(minimal)③ → STOPPED → Lock → rc=2 / Z Adv: ①②③ → STOPPED → Lock → rc=2
```
表記: KP解説・shell=通常3+F0+LR後0=総3。Z Std topic_intro_en=通常2+Fallback1+LR後0=総3。

### 4-7. P8 TTSなし — Y Intro/Notification1-3/Outro(固定mp3の読込)、Z shell/番号音声(Master資産のコピー)

### 4-8. 差異の一覧(フロー上、見落としやすい点)

1. 同じ『3回』でも、Advは同一Style3回、Std/日本語は3回目だけStyleが変わる(F-Style)。星取表①の【総N】と『Fallback有無・種類』欄を見ること。
2. LR再TTSのStyleは部位で違う(L1=保持、L2=脱落、L3=minimal)(U-02)。LR再TTSがNGなら、L1/L2ではLRが再入し得る(U-01)が、L3は再入しない。
3. LR後の再検証: 統一judgeは書換え後文を正解とし、`m1_anchor_text`・Lock/承認keyは元の原稿。L3系(Std)のLR再TTSは`force_secondary=True`。
4. HR queue行はLRより前に書かれる(U-04a)。Repetition/disfluency単独NGの最終STOPPEDでは書かれない(U-04b)。
5. runnerの終端(X=Gate BLOCK、Y=gate/assemble stageでrc=2、Z=tts stage全clip後rc=2)はFamily別(§2-1)。
6. cooldownの待機方式: 単一sleep(STOP確認なし)がX/Y/Zの大半、Z dialogue ctxだけ分割sleep(U-12)。
7. KP英語phraseの前段: X/Z=K2、Y=MINIMAL(default profile。U-15)。

## 5. 発見した仕様不一致・未配線・理由不明箇所(統合一覧)

3文書の発見(X: OPEN-376再入・OPEN-312/274 Style差・非ASR起因NGでLR不発・KP解説/shellの扱い・Std減速後最終NG、Y: Y-F01〜F09、Z: dialogue LRなし・M-3(ii)・cooldown STOP sentinel・topic_intro_en・OPEN-274/371)を、**同一事象は1件に統合**(例: X『非ASR起因NGでNO_NG_SPAN』とY『Repetition QA単独NGでNO_NG_SPAN』[Y-F03]→U-03)。分類はA/B/Cに『修正へ進む/確認/ユーザー判断/現状維持』の推奨を併記(新規OPENは付録B)。
重要度: 高=品質・仕様に直結しProduction成果物へ影響する / 中=品質・Delivery・コストのいずれかに実害がある / 低=実害が小さい・文書のみ・稀。

| ID | 分類 | 重要度 | Family | 部位 | 事実 | 品質リスク | 量産コスト | Delivery影響 | 既存OPEN重複 | 推奨対応 | 旧ID(3文書) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **U-01** | B(既知 OPEN-376 D-B4) | 中 | X/Y/Z | Adv英語のLR再TTS(voice01系: topic_intro/preview/comment、news_tail系: 本文/in_one_line/chunk) | LR再TTSが `__wrapped__(…, cs=True, max_attempts=1)` を呼ぶため、再TTSがNGだと同関数末尾でLRが再入する。再入を止めるカウンタ/引数は無い(voice01:363-369/:323、news_tail_fix:370-377/:325)。実LR記録に深さ2が3件(X: hormuz__run_03_baseline comment_4[2026-09-28]・meta__run_regen_01 in_one_line[2026-10-11]、Z: run_e2e_01 full_story_part1_c18)。仕様側は「LR再TTSがNGなら次はHR」(ITEMS23_REWRITE_CONDITION_AND_SCRIPT_REF_01.md:28)・「LR後v1=標準Prompt・1 attempt」(CURRENT_SPEC.md:2886)・ユーザー2026-10-15 §6「Rewriteの発火・再TTS回数を正しく計数し、累積上限を守る」。Std(L3)はminimal直呼びで再入なし。Yでは実例なし(E-1は深さ1) | 書換え連鎖で元原稿から逸脱し得る(audio_text_deviationは最初の書換えのみ記録=OPEN-376 D-B6) | 1 LRごとにLuna2呼出+TTS/ASR追加。深さは理論上非有界(実例は3件とも最終RESOLVED) | 小 | OPEN-376(USER_DECISION_REQUIRED(仕様判断)ラベル。PRINCIPLE_NONCOMPLIANCE_ANALYSIS_01.md:103は『境界: 是正が意味変更か否かをFableが判定してから』) | Fableが11-8判定(『LR1回/segment』との整合是正か、意味変更か)→整合是正なら修正へ進む(最小=LR再TTSでのみLR無効化)。意味変更ならユーザー判断。新規OPEN不要 | CC-F1, X-F1 |
| **U-02** | B(既知 OPEN-312/OPEN-274) | 中 | X/Y/Z | LR再TTSのStyle(Adv本文系・Std全英語) | LR再TTSのStyleが部位で違う: Adv本文/chunk/in_one_line(news_tail系)=role Styleを渡さず標準ENGLISH_STYLE_PREFIX(:370-377)、Std全英語=minimal Style(crosslevel:425-427)、Adv topic_intro/preview/comment(voice01系)=保持(:363-369)。『全roleにStyleを適用』との不一致。Y: E-1 b1b y_voice_1 の記録style_prefix=`<default:ENGLISH_STYLE_PREFIX>`。XのM3 Gate/Y GateがLR採用をStyle違反としてBLOCK→人間承認が要る | LR発火時のみ。Styleが通常と違う音声が混ざる(M3/Y Gateが検知) | 0 | Gate BLOCKで人手待ち(E-1で2 segment発生) | OPEN-312(Deferred、USER_DECISION_REGISTER #6)、OPEN-274(未承認候補) | 既存OPENへ追記のみ(Y Gate BLOCKとして顕在化した事実、Zでも同事象)。ユーザー判断は#6でDeferred中 | CC-F2, X-F2, Z-5, Y-F05の一部 |
| **U-03** | C(承認記録なし) | 高 | X/Y/Z(narrator系) | ASRはPASSだがdisfluency/repetition/長さQAでNGになる英語部位(X Adv comment/preview/in_one_line/本文、Y本文8、Z narrator) | LRのNG span特定(identify_ng_span)は最終attemptのPrimary転写とcanonicalの語差分のみ(er020:206)。非ASR起因NGは差分が無くHUMAN_REVIEW_LOCKED_NO_NG_SPAN→LR不発→STOPPED→HR(er020:761,774)。cooldown(固定600秒)は既に払われた後。実例: X Adv comment_4(2026-10-25 23:57〜10-26 00:07 part2_hr_evidence_01__run_r2): 3attempt全てEXACT_MATCH・ASR PASS、disfluency flagged(`now.`/`Now,`)でverified=False→cd600.004秒→LR記録なし→STOPPED(本調査でtts_generation_results.jsonを再確認)。Y: Voice 1 Algieba(旗率72%・take最終OK率38%: OPEN-533)。E-1 b1b y_voice_1は是正前に『ハイフン差の偽span』でLRが発火しRESOLVED、是正後のdry判定はfound=false(E1_HUMAN_REVIEW_01.md §5)。Z narrator(repetition QA有効)も同条件だが実例は未確認。2026-10-19決定『なおNGならRewriteへ』は非ASR起因NGの扱いを書いていない。OPEN_ITEMSに`NO_NG_SPAN`を扱う項目なし(Grep 0件) | HR件数増(自動救済できるNGが人手に回る) | cooldown10分+TTS3回が無駄になる。Y Voice 1では再生成連鎖の追加費用(OPEN-533) | HR待ちで完成が止まる(E-1で実発生) | OPEN-525(閾値・境界)・OPEN-533(再生成率)は関連するがこの点は未記載。NO_NG_SPANを扱うOPENなし | ユーザー判断(§8-2)。新規OPEN起票推奨(横断1件)。Y個別の閾値/再生成率はOPEN-525/533に残す | CC-F3, X-F3, Y-F03 |
| **U-04** | C(承認記録なし)＋既知OPEN-376 D-B5 | 中 | X/Y/Z | 英語HR queue(audio_retry_cascade_prod_01/human_review_queue.jsonl) | (a)HR queue行は最終slot NG判定時にLR前に書かれ(er006:1294-1296)、LRが成功してもqueueに残る(word_gacha part3: queue2行・最終status OK。OPEN-376 D-B5)。(b)Repetition QA/disfluency単独NGはjudge後に判定されるため(news_tail_fix:223-228)、ASR judge上はPASSのまま最終STOPPEDになってもqueue行が出ない(Y E-1 b1b y_voice_1: Lock→STOPPEDだが英語HRQ行なし。er006:641-642)。Lockとtts_generation_results.jsonには記録あり | (a)誤認 (b)queueだけを見る運用では見落とし | 0 | (b)見落とし時は完成遅延 | OPEN-376(D-B5=(a)のみ) | OPEN-376 D-B5へ(b)を追記。queue登録契機の変更は共通核の仕様変更のため設計はFable(必要ならOpus条件A)。新規OPEN不要 | CC-F4, X-F4, Y-F04 |
| **U-05** | C(ユーザー判断待ち。27-3ではD候補) | 中 | Z | 登場人物のセリフ(dialogue)ctx方式/legacy方式(Std/Adv) | dialogueにはLR呼出が無い(generate_voice_body_wide_margin にLR/cooldown呼出なし。`git log -S local_rewrite -- er012_b…` 0件)。ユーザー原文2026-10-26「NG→既存のLocal Rewrite処理へ」(FZ-CONTEXT…_USER.md:30,32,36,136)と実装が食い違う。ユーザーによる不採用の記録は無い。Fable判断J-1(DESIGN_02.md:6,61)が『LR新設は新仕様でユーザー承認事項』として新設せずHR/STOP直行を選択、Opusも同意見(OPUS_REVIEW_01.md:63-70)。ユーザーは後日『Local Rewriteは未配線であり現行ではHR/STOP…調査結果と照合…新仕様を独断で追加しない』(FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_USER.md:69-73)と状態を認識し、判断を本調査後へ保留。時系列は§3-2 | ctx導入後dialogue 3回NGの実績なし(E-1 21 clip)。legacy時代は3回STOPPED 6件(the_open_window、重複あり)。LRで救えたかは未検証 | LR配線の費用は別見積(BUDGET_PLAN_01:23) | HR待ち。頻度はctx後で未測定 | OPEN-528 Deferred(1)(既存。重複) | ユーザー判断(§8-1)。新規OPEN不要 | Z-1 |
| **U-06** | B(承認済み仕様との不一致) | 低 | Z | Topic intro(topic_intro_en、Std/Adv) | 承認済み5 roleにTopic introが含まれるが(CURRENT_SPEC.md:2176)、Zのclip_id `topic_intro_en` は resolve_narrative_role で未分類(本調査でも実測: topic_intro_en=None/False、topic_intro=TOPIC_INTRO/True)。cooldown・LRが非適用。Xのsegment_id `topic_intro` は適用される。IMPLEMENTATION_DESIGN_02.md:34『既存C/Xと同じ扱い』はXについて事実と異なる。除外の承認記録なし。OPEN_ITEMSに`topic_intro_en`の項目なし(Grep 0件) | topic introは短文(34 entryで再試行0)。最終NGで即HR | 0 | 低 | なし(新規) | 修正へ進む候補(共通核 er020 の resolve_narrative_role に追加 or Z側clip_idを `topic_intro` にそろえる。Zの挙動変更[cd600秒+LR有効化]と共有file編集を伴うため、Fableが11-8/Opus要否を判定) | Z-2 |
| **U-07** | C | 低 | Z | Adv dialogue ctx方式 | M-3(ii): Advでminimal_fallbackが併発すると外側の行会計(attempts_log行数、minimal行も計上)が先に尽き、従来方式(3回目)に到達しないままSTOPPED+HR Lock(terminal_before_fallback、er063:959)。ユーザー原文は『3回目で従来方式』。(i)行会計をpolicy基準にする案は既存A2予算規則の変更。未観測 | 稀(未観測) | 0 | HR待ち | OPEN-528 Deferred(2)(既存) | 既存OPENに据置(新規不要)。ユーザー判断は『既存A2予算規則の変更』を伴うため保留 | Z-3 |
| **U-08** | C(低)。A/C境界 | 低 | X/Y/Z | Adv KP英語解説・shell固定英語(Y/Zはshell固定英語をStore再利用/コピー) | LRとcooldownが無い(csを渡さない。resolve_narrative_role('kp1_explanation_en')=None、shell名=None)。承認済み5 roleに名指しされず、除外2 role(Heading,Key Phrase)にも名指しされない。er019:1212-1213のコメントは『統一フロー「TTS①②③、3回NGでLR/HR」に揃える』と書くがLR配線は無い。KP解説の回数変更は『ユーザー決定の逐語は無く3回へ揃えた』(CURRENT_SPEC.md:2885(2))。なお『LRは5 roleのみ』という列挙型の正式仕様(CURRENT_SPEC.md:2873,2886)自体はあり、それに沿っている=A寄りの読みも可能(3文書でX=C、Y=A、Z=Aだった分類を保守的にCへ統一) | 低(固定短文/Store再利用。KP解説の失敗実績0) | 0 | 3回NG→HR直行 | なし | 現状維持(追跡のみ)。ユーザー判断に上げない(実害0・失敗実績0)。コメント訂正はU-11と同時 | X-F5, X-F6, Y shell/KP解説行, Z KPEXPL行 |
| **U-09** | C | 低 | X/Y/Z(Std) | Std本文/chunk/in_one_lineの減速後再検証の最終NG | 6%減速後の再検証が通算3回目でNGの場合はLRを行わずfinalize_a2_slowdown_final_ng→HR(n3:309,317-319 docstring(iii)=AUW 委任_06e『ユーザー原文L39-49「3回NGでLR/HR」の末端』)。ユーザー逐語の承認は未確認。Y-S-05/Z-A2-NARRも同じ関数経由 | 低-中(減速由来の稀なNG) | 0 | 人手待ち(稀) | なし | 確認(Fable。逐語承認が見つからなければC据置)。ユーザー判断に上げない | X-F7 |
| **U-10** | A(動作)／B(文書の旧記述) | 低 | X/Y/Z | Std/JAの『標準2+minimal1』と基本フロー文面 | CURRENT_SPEC.md:2873『再生成②③(原稿・Prompt・モデル・Voice・速度を維持)』と、Std英語・日本語の3回目=minimal Style(Style変更)が文面上食い違う。動作は2026-09-04ユーザー決定(CURRENT_SPEC.md:1857)と2026-10-21ユーザー決定『Fallback機構は現行仕様を維持(Prompt・Style・発動条件・再試行回数は変更しない、X/Z共通)』(…FALLBACK-APPROVAL-FINAL-ASSEMBLY_USER.md:11-15)で承認済み。2026-10-15 §2『各TTS再生成では原稿・Prompt…を維持』は後日付の10-21決定が上書き | なし | なし | なし | なし | 現状維持(動作)。SSOT同期の際に文面へ『Std/JAの3回目=minimal(F-Style)』を追記する案(Fable/SSOT担当) | CC-F7, X-F10, Y-F08 |
| **U-11** | B(古い記述の残存。文書/コメントのみ・挙動影響なし) | 低 | Y/Z/X | 文書・コメント | (1)CURRENT_SPEC.md:2954『対象外: Standard(a2)・…・Family Y』、:2963『Standard本文は仕様上対象外』(実装・承認はY=Std/Adv双方: er121_family_y_structure_01.py:113、2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md:14,32-33)。(2)er121_family_y_audio_01.py:17『Adv(b1b)本文のみ(X同様、Std本文はchunk化しない)』。(3)er019:1212-1213 KP解説のコメント『LR/HR』。(4)er060_output/melos_production_e2e_01/CONFLICT_RESOLUTION_01.md:24 S5『Local Rewrite上限到達でSTOP』(dialogueにLRは無い)。(5)docs/pm/design/2026-10-11_FAMILY-XZ-CROSS-FAMILY-SPEC-REVIEW-01_XZ_MAPPING_01.md:153『Z未配線…known_gap』(narrator側は解消済み) | なし | なし | なし | OPEN-532/PM-SSOT-SYNC-04系に包含(新規不要) | 修正へ進む(SSOT同期は文書のみ。コメント2点はコード編集のため別委任で次回のコード変更時にまとめる) | Y-F02, CC補足, X補足, Z §10 |
| **U-12** | C | 低〜中 | X/Y/Z | narrator/preview/comment/topic_introのcooldown(Z dialogue ctxを除く) | maybe_cooldown_before_attempt は単一の `sleep_fn(cooldown_seconds)`(600秒)でSTOP sentinelを確認しない(er020:64-93)。Z dialogue ctxだけが5秒刻みでSTOP確認し再開時も実時間で10分を保証(er122:298-338)。X runnerにはRUN_LOCK/RESTART_STORMが無い(U-21)。SDK入口等の別guardの有無は本調査で見つからず(未確認)。ユーザー決定2026-09-26『固定10分』はsleepの実装方式を規定していない | なし | なし | cooldown中にSTOPが出ても最大10分後に次TTSが走る可能性(未確認) | なし | 確認(Fable。STOP guardの有無を確認し、無ければ修正へ進む候補: 既存STOP通知の遵守=安全装置の整合) | Z-4 |
| **U-13** | C | 低 | X/Y/Z | Adv英語の異常長音声 | voice01(L1)は異常長を次attemptへ(:232)、news_tail_fix(L2)は異常長もminimal fallbackで即再TTS(:171-178)。同じ『異常長』で処理が異なる。仕様記録なし(Grep未発見) | 低 | 低 | なし | なし | 現状維持(追跡のみ) | CC-F6 |
| **U-14** | 残置(実害なし) | 低 | X/Y/Z | cascade OFF専用の残置コード | stop_retrying→ASR_VALIDATION_UNCERTAIN分岐(voice01:302、news_tail_fix:294、crosslevel、L7:559/:611)はcascade有効時は到達不能(stop_retryingは常にFalse: er006:961/:1238)。`max_attempts=6`指定は関数内でmin(,3)にクランプ(voice01:487、n3:732)。Chunk Std拡張後の旧retry規則のコード残存は見つからず | なし | なし | なし | なし | 現状維持(rollback互換)。撤去はFable判断(撤去対象を増やさない) | CC-F5, X補足 |
| **U-15** | B疑い(記録なし)。高 | 高 | Y | Y runnerのStyle profile(全Y音声) | `er121_family_y_runner_01.py:37 STYLE_PROFILE = "default"` 固定。設計(DESIGN_01.md:84)・台帳(SPEC_LEDGER_03.md:60 YL-A01=APPLY)・DEV Trial(er110:40=fx_20261017)は継承。Y runで実際に送られたStyleは基底6-role Style(PD06/S3/E1/K2/P8-KP/P7は未使用)、X M3は`checked=[]`。`default`の承認/除外の記録は0件。詳細=Y_F01_STYLE_PROFILE_CHECK_01.md | Y全音声のStyleが承認済みprofileと異なる可能性(Style=音声品質) | 切替時は再生成(run_01のtts実績≒JPY28。再生成+再試行の見積は未実施) | 再配達記事完成版の再利用範囲に直結(新out_dir要: M2) | なし(OPEN-415はY導入時の設計課題でありこの点は未記載) | 確認→修正へ進む(Fableが除外記録/意図の有無を確認[read-only 30分]→B確定なら配線方針と再生成見積を次委任)。ユーザー判断は『Yはdefaultでよい』という意図が確認された場合のみ | Y-F01 |
| **U-16** | Std fallback BLOCK=A寄り／LR成功BLOCK=C | 中 | Y | Y本文8 segment(+chunk)のY Gate | Y GateはLOCAL_REWRITE_RECOVERYとStdのfallback_used≠Falseを人間承認なしでBLOCK(er121_family_y_audio_01.py:706-709)。Std本文3回目(minimal)で成功した音声・LR成功した音声は、ASR PASSでも自動採用されない。前者はユーザー2026-10-21『今回の音声に対する個別承認であり、今後すべてのFallback音声を無条件に自動採用してよいという共通仕様変更ではない』(…FALLBACK-APPROVAL-FINAL-ASSEMBLY_USER.md:23)と整合。後者の根拠はOPEN-312(LR再TTSがrole Styleを落とす)でUSER_DECISION_REGISTER #6=Deferred。Y固有のユーザー承認は記録なし | 品質を守る側 | なし | Std本文は3回目到達=必ず人間承認(E-1で2 segment) | OPEN-312(Deferred) | 現状維持。OPEN-312へ『Y本文でGate BLOCKとして顕在(E-1で2 segment)』を追記 | Y-F05 |
| **U-17** | C | 低 | Y | Std共有固定日本語 point_explanation | ensure_all_shared_narration_a2 が生成するが、Y a2 timelineは使わない(er121_family_y_audio_01.py:782-790)。かつ _assert_shared_narration_ok(er019:1255)の対象で、非OKだとY a2のTTS stageがSTOPする。Y runはStore再利用(生成0) | なし | Store miss時のみJA 1 clip | 未使用clipの失敗でY a2が止まるリスク(実績なし) | なし | Fable判断で『Yでは呼ばない』か現状維持 | Y-F06 |
| **U-18** | C | 低 | Y | Y runnerの予算guard | 予算guardは『clip単位1回』(TTS_CLIP_EST_JPY=1.0、er121_family_y_audio_01.py:252-263、runner:985)で、clip内のretry/cooldown/LR再TTSは個別にguardされない(clip内上限はER-011累積15・API STOP guardのみ)。実測: E-1 b1b y_voice_1 stage 5.579円(7 attempt+LR) | なし | Cap近傍での超過余地 | なし | なし | 現状維持(共通guardの設計。変更は費用管理の仕様変更のためFable判断) | Y-F07 |
| **U-19** | C | 低 | Y | approve_regenerateの承認主体 | E-1で`approve_regenerate`を『Fable権限による追加再生成の許可』名義で3 segmentに各1回実行(approved_by="user"は不使用、EVIDENCE_02.md §4に開示)。er011:474-476 docstringは『ユーザーの明示的な指示でのみ呼ぶこと』。Fable名義を許容する規定は特定できず | なし | 再生成追加(5.58+13.75円) | なし | なし | Fable判断(27-3分類)。規定の明文化の要否のみ。ユーザー判断に上げない | Y-F09 |
| **U-20** | A(追跡: OPEN-290未クローズ) | 低 | X/Y/Z | 日本語部位のLR | 日本語LRなしの承認根拠はユーザー2026-10-15『日本語Local Rewrite: 現行の英語用機構を機械的に流用しない。安全な実装が成立していない場合はHuman Reviewへ進める』(…ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md:148)・『日本語: 現時点では原則Human Review』(同:160)。『現時点では』は時限表現。技術的背景(開発側記録): identify_ng_spanが純日本語でfound=False/Gate7全候補0.0(OPEN-290(E))。OPEN-290は『当面なし』案のままOPEN(ユーザー判断待ちラベル)。再検討の期日・条件は記録なし | なし | なし | なし | OPEN-290(既存) | 現状維持。OPEN-290側で再検討の契機を管理 | X-F8 |
| **U-21** | A | 低 | X | X runnerのSTOP機構 | X runner(er019)にRUN_LOCK/RESTART_STORM実装なし(実装はer026(Z)・er062・er077・er119・er121(Y))。PM_GOVERNANCE.md 26-4『STOPセンチネルはFamily Z runnerに実装済み。他Familyへの展開は必要時に別途判断する』 | なし | なし | X連続再実行のstorm防止は実行層の自己停止ルール頼み | なし | 現状維持 | X-F9 |
| **U-22** | C(既存OPEN-371) | 低 | X/Y/Z | 3NGの数え方 | 『3NGにSecondary障害を含まない』条件は未実装(CURRENT_SPEC.md:2886)。Secondary障害時もNGとして数える | 低 | 低 | HR増の可能性 | OPEN-371(既存) | 既存OPENで管理 | Z-6 |
| **U-23** | 未検証(runtime証拠なし) | 低 | X/Y/Z | 実走証拠のない経路 | Std chunkのLR/強制NG fallback/exhaust(X/Y/Z)、Adv chunkのcd・LR・HR、Y topic_intro/preview/commentのretry・LR、Z Adv Preview/CommentのLR、Z dialogue ctxのASR由来最終slot NGのHR queue追記、ENGLISH_LOCK段(Y)、M-3(i)併発(Z Adv)、Std減速後取り直しの最終NG。コードの存在だけでPRODUCTION_WIREDとは判断しない | 未検証 | — | — | — | 判断不要。必要なら後続でevidence取得(自然発火待ちか、単独Trialかはその時にFable判断) | X/Y/Z runtime表 |

統合findings=23件（A系=3/B系=5/C系=12/その他=3）。重要度: 高=2/中(低〜中を含む)=6/低=15。

**統合による分類の変更点**: KP英語解説・shell固定英語は3文書でX=C/Y=A/Z=Aと割れていたため、保守的にC(低)へ統一した(付録A-1 #4)。Y-F05は『Std fallback BLOCK』(A寄り)と『LR成功BLOCK』(C)に分割した(U-16)。

**11-8の線引き(修正範囲)**: 本調査は是正しない。U-01・U-06・U-11は『承認済み仕様・設計原則との矛盾の是正』に当たる可能性が高く、委任範囲内なら修正まで進められる候補(U-01はOPEN-376が仕様判断ラベルのためFableの11-8判定が先)。U-03・U-05は受理面・方式の新設/拡大にあたるためユーザー判断。

## 6. QCD影響と優先順位

優先順位は Q(品質)＞D(納期・速度)＞C(量産単価)。『所要見込み』は所見(事実ではない)。

| 順位 | ID | 品質(Q) | 納期(D) | 量産単価(C) | 次の一手と所要見込み(所見) |
|---|---|---|---|---|---|
| 1 | **U-15** Y runnerのStyle profile `default`固定 | **高**: Y全音声のStyleが承認済みprofile(PD06/S3/E1/K2/P8-KP/P7)と異なる可能性。設計・台帳・DEV Trialは継承 | 再配達記事の完成版(再利用範囲)に直結。切替ならM2で新out_dir(新run)が要る | 切替時は再生成(run_01のtts実績≒JPY28。再生成+再試行の見積は未実施) | Fableがread-only確認(除外記録/意図の有無)約30分→B確定なら配線方針+再生成見積を次委任。QCD上は最優先 |
| 2 | **U-03** 非ASR起因NGでcooldown後にLR不発→HR | 中: 自動救済できるNGが人手に回る | **高**: Y Voice 1(旗率72%・take最終OK率38%)・X comment_4で実発生。HR待ちで止まる | 高: cooldown10分+TTS3回が無駄(Yの再生成費用超過の一因: OPEN-533) | ユーザー判断(§8-2)。選択後に実装・Regression。判断までは現状維持で安全 |
| 3 | **U-05** Zセリフ LRなし | 中(未測定。ctx後は3回NGなし) | 中: HR待ち。頻度は未測定 | LR配線は別見積 | ユーザー判断(§8-1)。判断までは現行維持(HR/STOP)で安全 |
| 4 | **U-01** LR再入 | 中: 書換え連鎖で元原稿から逸脱し得る | 小 | 小(1 LRあたりLuna2+TTS/ASR追加。実例3件は最終RESOLVED) | Fableの11-8判定0.5h→整合是正なら最小修正(LR再TTSでのみLR無効化)+regression。意味変更ならユーザー判断 |
| 5 | **U-06** Z topic_intro_en未分類 | 低(短文・再試行0) | 低 | 0 | 修正へ進む候補(共通核編集のためFableがOpus要否判定)。小さい |
| 6 | **U-12** cooldownがSTOP sentinelを見ない | 低 | 低-中(STOP後最大10分で次TTS) | 0 | まずSTOP guardの有無を確認(Fable)→無ければ修正へ進む(安全装置の整合) |
| 7 | **U-02/U-16** LR再TTSのStyle脱落とY Gate BLOCK | 中: Styleが違う音声を人間承認なしに採用しない側 | 中: Std本文3回目到達=必ず人間承認 | 0 | 既存Deferred(OPEN-312)へ追記のみ。現状維持 |
| 8 | **U-04** HRQ登録契機の不整合 | 低-中: queueだけ見ると見落とし | 低 | 0 | OPEN-376へ追記。設計変更はFable(必要ならOpus条件A) |
| 9 | U-07〜U-11・U-13・U-14・U-17〜U-23 | 低 | 低 | 低 | 追跡・SSOT同期でまとめて対応(U-11=文書/コメント同期)。個別の緊急性なし |

**全体の見立て(所見)**: 品質を直接左右するのはU-15のみ。単価・納期に効くのはU-03(特にY Voice 1)。それ以外は『既存OPENに追記』または『小修正』で足りる。XYZで仕様を統一する大改修が必要という証拠は、今回の調査では見つかっていない(ユーザー原文§9末尾の通り、仕様統一・Production改修は別途ユーザー判断を経て実施)。

## 7. Fable独立評価

(Fableが記入。本欄は空欄)

- 評価者:
- 評価日:
- 判定(整合性・網羅性・分類の妥当性):
- 星取表①②の事実照合の要否:
- 任意Opusレビュー要否(11-3は非該当[調査]):
- 追加確認の指示:

## 8. 必要なユーザー判断事項(本当に判断が必要なものだけ)

正本の分類は `docs/pm/PM_GOVERNANCE.md` 27-3(A既判断/B承認範囲内で自己解決/C現タスクと独立/D真に新しい判断)。**『判断候補』は本Agentの表記であり、`USER_DECISION_REQUIRED` のラベルはFableだけが付ける。**

### 8-1. 判断候補1: Zセリフ(dialogue)へのLocal Rewrite新設の要否(U-05。OPEN-528 Deferred(1)と同一)

- **27-3分類(Claude提案)**: **D(真に新しい判断)**。根拠: A既判断なし(ユーザー原文は『既存のLocal Rewrite』を前提に書き、J-1もユーザー承認ではない: §3-2)/B自己解決不可(LR新設は新仕様でユーザー承認事項: J-1。ユーザー自身が『Local Rewriteの新仕様を独断で追加しない』と指示: FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_USER.md:73)/C独立ではない(本調査の結論そのもの)。
- **事実**: dialogueは3回NG後LRを行わずHR/STOP(総3)。ctx導入後(E-1〜E-6のrun)にdialogue 3回NGの実績なし。legacy時代はdialogue 3回STOPPED 6件(the_open_window、重複あり)。LRで救えたかは未検証。dialogue用LRの設計案は`DESIGN_01.md:122`(n=3後に1回だけ。従来style・max_attempts=1・`lr_used==0`・累積15回guard維持)。
- **選択肢**:
  - **A. 新設する**(3回NG後に書換え→再TTS1回。新構造のためOpus条件A。話者の台詞を書換える=audio_text_deviationを記録し表示本文は不変、というZ narrator LRと同じ運用になる)。
  - **B. 現状維持**(3回NG→HR/STOP。ユーザーが原文で想定した『Local Rewrite段』は空のまま、HR/STOPで人が対応)。
  - (C. 保留: 頻度の実測を待つ)
- **QCD(事実+見込み)**: Q: LRで救えるのは『ASRが語を取り違えた』NGに限られる(U-03)。D: ctx導入後の3回NG頻度が未測定のため、HR待ちの発生率は不明。C: LR配線の費用は別見積(BUDGET_PLAN_01:23)。
- **所見(事実ではない)**: J-1の『音声と表示本文の乖離』はZ narrator LRにも当てはまり、それは承認下で運用済み(§3-3 #1)。一方、dialogueは台詞自体を変える点で性質が異なるという見方もある。ctx導入後の頻度が低ければ、Bのままでも実害は小さい可能性がある(未測定)。推奨は『ユーザーが原文で想定した動作(LRあり)に近づけるか、HR/STOP直行を正式化するか』の明示判断。

### 8-2. 判断候補2: ASRはPASSだがdisfluency/repetition QAでNGになる音声の扱い(U-03)

- **27-3分類(Claude提案)**: **D(真に新しい判断)**(Production挙動の意味的変更を伴う。a=現状維持を除く)。根拠: A既判断なし(2026-09-26『固定10分』・2026-10-19『なおNGならRewrite』のどちらも非ASR起因NGを書いていない)/B不可(受理面・方式の新設/拡大)/C独立ではない。
- **事実**: 非ASR起因NGは、最終attemptのPrimary転写とcanonicalに語差分が無く`NO_NG_SPAN`→LR不発→HR(er020:761,774)。cooldown(600秒)は既に払われている。実例: X Adv comment_4(2026-10-25 23:57〜10-26 00:07: 3回ともEXACT_MATCH・disfluency flagged→cd600.004秒→LR記録なし→STOPPED)。Y Voice 1 Algieba(旗率72%・take最終OK率38%: OPEN-533)。OPEN_ITEMSに`NO_NG_SPAN`を扱う項目は無い。
- **選択肢**:
  - **a. 現状維持**(cd後にLR不発でHR。実害=cooldown10分+TTS3回の無駄とHR増)。
  - **b. 非ASR起因NGはcooldownを省略**(2026-09-26ユーザー決定(B)『固定10分』の発動条件と衝突するため、ユーザー承認が要る)。
  - **c. LRを非ASR起因NGにも拡張**(新仕様。disfluency/repetitionが書換えで直るかは未検証=Trial要)。
- **QCD**: Q: a=HR増/c=書換えで救える可能性(未検証)。D: Y Voice 1で頻度高。C: aは10分+TTS3回の無駄が残る。
- **所見(事実ではない)**: bは最も小さい変更で単価・納期を改善できるが、『cd後に再試行で直る』ケースを失う可能性がある(要データ)。cは効果が未検証。Y Voice 1はPuck化(並行タスク)で頻度が変わる可能性があり、再測定後に判断する選択もある。

### 8-3. 条件付き: Y Style profile(U-15。現時点ではユーザー判断に上げない)

- **27-3分類(Claude提案)**: **B(承認範囲内で自己解決)**。根拠: 設計・台帳・DEV Trialは『`fx_20261017`継承』(DESIGN_01.md:84、SPEC_LEDGER_03.md:60、er110:40)、ユーザー原文は『他FamilyでAPPROVED_FOR_PRODUCTIONの共通仕様はYも適用対象』(…LAUNCH-01_USER.md:162-166)。`default`の承認/除外の記録は0件(Y_F01_STYLE_PROFILE_CHECK_01.md §0)。
- **ユーザー判断になる条件**: Fableの確認で『Yは`default`でよい』という意図・承認が見つかった場合、または既にユーザーが最終試聴PASSした版を再生成する場合。現時点で再配達記事の完成版はまだユーザー最終試聴前(`2026-10-26_FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01_USER.md` 冒頭『目標: …ユーザー最終試聴へ提出する』)。
- **再配達記事の完成版をいま制作した場合の影響**: `Y_F01_STYLE_PROFILE_CHECK_01.md` §5(default固定のまま=現行公開版と同条件で『仕様違反の可能性』を残す/`fx_20261017`へ切替=新out_dirでtts再生成・Voice 2/3の再利用が成立しない)。

### 8-4. ユーザー判断に上げないもの(自律解決可能。理由つき)

| ID | 理由 | 推奨 |
|---|---|---|
| U-01 | Fableの11-8判定(整合是正か意味変更か)が先。OPEN-376が仕様判断ラベルのため、意味変更と判定された場合のみ判断候補になる | 修正へ進む候補(Fable判定後) |
| U-02/U-16 | 既存Deferred(REGISTER #6/OPEN-312)。新たな判断を要しない | OPEN-312へ追記のみ |
| U-04 | 共通核のqueue契機はFable設計判断 | OPEN-376へ追記 |
| U-06 | 承認済みTopic introの配線漏れ(B) | 修正へ進む(共通核編集のためOpus要否はFable) |
| U-08/U-09/U-13 | 実害小・失敗実績0 | 現状維持(追跡) |
| U-10/U-11 | 文書/コメントの同期のみ | SSOT同期へ |
| U-12 | 安全装置(STOP)の整合確認 | 確認→必要なら修正 |
| U-15 | 8-3のとおり(B) | 確認→修正へ進む |
| U-07 | OPEN-528 Deferred(2)。既存A2予算規則の変更を伴うため保留 | 据置 |

---

## 付録A. 3文書の用語・記述の突合と、統合で正とした表現

### A-1. ズレと採用した表現

| # | 論点 | X文書 | Y文書 | Z文書 | 統合で正としたもの | 根拠 |
|---|---|---|---|---|---|---|
| 1 | 技術救済(attempt内minimalへの即再TTS)のラベル | F-Tech | Adv/shared/topic等を『F-Style(F-Prompt可)』と表記 | F-Tech | **F-Tech**(attempt内の技術失敗救済)。Yの該当セルも書換え | COMMON_CORE_01 §1 L1(:179-216)/L2(:171-190)、委任文の固定ラベル |
| 2 | Std/日本語の3回目 | F-Style | 『F-Style/F-Prompt』併記 | F-Style | **F-Style**(Styleがminimal短文に変わる)。F-PromptはZ dialogue ctx(ctx→従来方式)のみ | Z文書 Z-A2-DIALOGUE-CTX、COMMON_CORE_01 L3 |
| 3 | Key Phrase英語の前段 | K2(styled) | MINIMAL(default profileのためK2なし) | K2 | 前段=X/Z:K2、Y:MINIMAL(U-15) | Y_F01_STYLE_PROFILE_CHECK_01.md §4 |
| 4 | Adv KP英語解説・shell固定英語の分類 | C | A(包含規定のみ) | A(名指し除外記録は未確認) | **C(低)**。『LRは5 roleのみ』の列挙型正式仕様はあるが、KP解説/shellを外した理由の記録は無い。A寄りの読みも可能と注記(U-08) | CURRENT_SPEC.md:2873,2885(2),2886; er019:1212-1213 |
| 5 | CURRENT_SPEC.md:2873『再生成②③は原稿・Prompt…維持』とStd『標準2+minimal1』 | A(2026-10-21維持決定) | C(整合不明: Y-F08) | 言及なし | **動作=A／文書の旧記述=B(軽微)**(U-10) | 2026-10-21 …FALLBACK-APPROVAL-FINAL-ASSEMBLY_USER.md:11-15,23 |
| 6 | 日本語LRなしの承認原文 | `…ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01_01.md`:148,160 | 『原文L146』のpath未特定 | 同上を引用 | **X文書が特定したpathが正**。Yの『理由不明・記録なし』は解消(承認あり=A) | 同ファイル:148,160 |
| 7 | LR再入(U-01) | 詳細に記述(CC-F1/X-F1) | 言及なし | 言及なし | Y/Z Adv英語も同じL1/L2を通るためFamily横断で統合。Zに深さ2の実例1件(run_e2e_01 part1_c18) | COMMON_CORE_01 CC-F1; X-F1 |
| 8 | 非ASR起因NG→NO_NG_SPAN(U-03) | CC-F3/X-F3(C) | Y-F03(C+D候補) | 言及なし | 1件に統合。Z narrator(repetition QA有効)も同条件だが実例未確認 | er020:761,774 |
| 9 | HR queueの契機(U-04) | CC-F4/X-F4(LR成功でも残る=OPEN-376 D-B5) | Y-F04(Repetition単独NGでは書かれない) | 言及なし | 1件(a/b)に統合。異なる2事象だが原因は同じ(ASR judgeの最終slot NGで書く設計) | er006:641-642,1294-1296 |
| 10 | cooldownがSTOPを見ない(U-12) | 『X runnerにRUN_LOCK無し』(X-F9) | 言及なし | Z-4 | 共通 `maybe_cooldown_before_attempt`(er020:64-93)の性質としてX/Y/Zに横断化 | er020:64-93 |
| 11 | Y Gateの分類(U-16) | OPEN-312 Deferred | Y-F05(C) | 言及なし | Std fallback BLOCK=A寄り(10-21ユーザー『個別承認』)、LR成功BLOCK=C | …FALLBACK-APPROVAL…_USER.md:23 |
| 12 | 最終NG後のrunner挙動 | runner停止せずGate BLOCK | tts stage rc=0→gate/assemble stageで`YE2EStop` rc=2 | tts stage全clip後`FamilyZTtsClipFailedStop` rc=2 | 矛盾ではなくrunner構造差。§2-1に併記し、星取表①『最終NG時』は各Familyの実態のまま | 各文書の根拠行 |
| 13 | 『3回NG』の総Nの数え方 | 通常n+Fallback m+LR後k=総N | 同 | 同 | 一致(3文書とも)。技術別枠は総Nに含めない | — |
| 14 | cs呼出数(`enable_connected_speech_equivalence_layer`) | 7(Grep実測) | 7(Y文書の行番号と一致: er121_family_y_audio_01.py:386,415,454,467,487,562,602) | 4(er063:1012,1017,1041,1050。Z文書の1004/1015/1037-1042は数行違うため関数名で参照) | 3文書とCOMMON_CORE『cs1本でcd+LR連動』は矛盾しない | Grep実測(本調査) |
| 15 | 行数の差 | md=16行/json=19行 | md=19/json=19 | md=14/json=14 | 統合はmdの16+19+14=49行(Xのjsonは同一部位をAdv/Std別等で細分) | 各ファイル |
| 16 | repro01.py:339のcooldown呼出し | — | cs連動として列挙 | — | COMMON_CORE L5は`cooldown_total_budget`を渡された場合のみ有効。矛盾ではなくL3→L5の通算化経路のみ | COMMON_CORE_01 L5 |
| 17 | Z dialogue ctxのcooldown | cs連動(共通核) | — | `attempt_hook`の別実装(`er122:282-338`) | 矛盾ではない(COMMON_CORE 所見1)。ctx方式は自前cooldownでcsには載らない | FAMILY_Z_01 Z-A2-DIALOGUE-CTX |

### A-2. コードで再確認した事項(API 0)

| 確認 | 結果 |
|---|---|
| `py -c "import er020_tts_retry_local_rewrite_01 as e; e.resolve_narrative_role / connected_speech_enabled_for"` | topic_intro=TOPIC_INTRO/True、**topic_intro_en=None/False**、kp1_explanation_en=None/False、welcome=None/False、japanese_title=None/False、preview=PREVIEW/True、comment_1=COMMENT/True、in_one_line=IN_ONE_LINE/True、y_voice_1・y_voice_1_k2・full_story_part1_c3・full_story_part1=FULL_STORY/True、kp1_en=KEY_PHRASE/False、point_explanation・num_one=None/False |
| `Grep enable_connected_speech_equivalence_layer` in er121_family_y_audio_01.py / er063_family_z_audio_01.py / er019_family_x_audio_production_runner_01.py | 7 / 4 / 7 件 |
| `Grep NO_NG_SPAN|HUMAN_REVIEW_LOCKED_NO_NG_SPAN` in er020 | L761(docstring)・L774(`result["status"] = "HUMAN_REVIEW_LOCKED_NO_NG_SPAN"`) |
| `er020_tts_retry_local_rewrite_01.py:57-93` | `COOLDOWN_SECONDS=600.0`、`maybe_cooldown_before_attempt` は `sleep_fn(cooldown_seconds)` の単発(STOP確認なし) |
| `er003_v1_sing01_news_tail_fix.py:171-190` | 異常長(`detect_duration_anomaly`)で`trimmed=None`→minimal fallbackへ即再TTS(L2)=CC-F6 |
| `Grep 'topic_intro_en|NO_NG_SPAN' OPEN_ITEMS.md` | 0件(U-03・U-06は既存OPENに無い) |
| Y runner | `STYLE_PROFILE="default"`(er121_family_y_runner_01.py:37)、Y run_01の`style_prefix`は基底Style、`y_style_profile_gate.json`の`x_gate.checked=[]`(詳細=Y_F01…md) |

---

## 付録B. OPEN起票・追記候補(確定リスト。SSOT編集権なし=文案のみ。転記はFable)

重複確認: `OPEN_ITEMS.md`をGrepし、OPEN-528(L1043)・OPEN-376(L885)・OPEN-312(L815)・OPEN-274(L777)・OPEN-525(L1040)・OPEN-533(L1048)・OPEN-371(L880)・OPEN-290(L793)・OPEN-532(L1047)・OPEN-415(L927)の存在を確認。`NO_NG_SPAN`・`topic_intro_en`・Y `STYLE_PROFILE` を扱う項目は無い。

### B-1. 新規OPEN候補(3件)

| 仮名称 | 対応 | 11-8分類 | 要旨(文案) |
|---|---|---|---|
| TTS-NONASR-NG-LR-COOLDOWN-POLICY-01 | U-03 | **ユーザー判断要(D候補)** | ASRはPASSだがdisfluency/repetition/長さQAでNGになる英語音声は、最終attemptの転写とcanonicalに語差分が無くLRが`NO_NG_SPAN`で不発となり、cooldown(固定600秒)後にHRへ落ちる(X Adv comment_4 2026-10-25〜26実走、Y Voice 1 Algieba)。仕様記録なし。選択肢=現状維持/非ASR起因NGはcooldown省略/LR拡張(§8-2)。Y個別の閾値・再生成率はOPEN-525/533に残す |
| FAMILY-Y-STYLE-PROFILE-WIRING-CHECK-01 | U-15 | **修正へ進む候補(Bの疑い・確認先行)** | Y runnerが`STYLE_PROFILE="default"`で、設計(DESIGN_01.md:84)・台帳(YL-A01=APPLY)・DEV Trial(er110:40)の`fx_20261017`継承と不一致。承認/除外の記録なし。Fableが意図の有無を確認(read-only 30分)→B確定なら配線方針(Z方式=定数参照+drift test/X方式=`resolve_run_profile`)と新run要否・再生成費用の見積を次委任。OPEN-415(Y導入時の設計課題)を関連項目として参照 |
| FZ-TOPIC-INTRO-EN-ROLE-UNRESOLVED-01 | U-06 | **修正へ進む(B)** | Zのclip_id`topic_intro_en`(Std/Adv)が`resolve_narrative_role`で未分類のため、承認済み5 roleのTopic introに適用されるcooldown・LRが非適用(Xの`topic_intro`は適用)。除外の承認記録なし。是正案=共通核`er020`の`resolve_narrative_role`への追加、またはZ clip_idを`topic_intro`へ統一(共通核の最小編集。Z挙動変更を伴うためFableがOpus要否を判定) |

(U-12は『STOP guardの有無』を確認してから起票要否を決める。確認結果が『guardなし』なら `TTS-COOLDOWN-STOP-SENTINEL-CHECK-01` を修正へ進む候補として起票。)

### B-2. 既存OPENへの追記候補

| OPEN | 追記文案 |
|---|---|
| OPEN-528 | 2026-10-26 TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_02で、Z dialogueのLR無しの時系列を確定(ユーザー承認による除外ではなく、既存LRが無い状態でFable判断J-1がHR/STOP直行を選択。ユーザーは後日状態を認識し採否を本調査後へ保留)。ユーザー判断事項=§8-1(REPORT_01)。M-3(ii)は据置 |
| OPEN-376 | (D-B4) LR再入はY/Z Adv英語も同じ関数(voice01/news_tail_fix)を通るため対象(Zに深さ2の実例: run_e2e_01 full_story_part1_c18)。(D-B5拡張) Repetition QA/disfluency単独NGの最終STOPPEDではHRQ行が書かれない(Y E-1 b1b y_voice_1)。(D-B5) LR成功でもHRQ行が残る(word_gacha part3) |
| OPEN-312 | Y本文8 segmentでもLR再TTSのStyle脱落/Std fallbackが顕在(Y GateがLOCAL_REWRITE_RECOVERY・STD_FALLBACK_USED_OR_UNKNOWNをBLOCK。E-1で2 segment要承認)。Z narrator Adv LR再TTSも同事象。USER_DECISION_REGISTER #6はDeferred |
| OPEN-274 | Z narrator AdvのLR再TTSがPD06を転送せず標準ENGLISH_STYLE_PREFIX、Z Std narratorはminimal(U-02) |
| OPEN-525 | Repetition QA単独NGはLRが発動できずHR直行(`NO_NG_SPAN`)。横断事象としてTTS-NONASR-NG-LR-COOLDOWN-POLICY-01を参照 |
| OPEN-533 | Algieba高旗率(72%)は非ASR起因NGの典型でLRが救えない(U-03)。Voice 1=Puck化後に再測定 |
| OPEN-371 / OPEN-290 | 追記なし(U-22/U-20として本調査で再確認のみ) |
| OPEN-532 / PM-SSOT-SYNC系 | U-10/U-11の文書同期(CURRENT_SPEC.md:2873の文面、:2954,2963のChunk旧記述)を包含 |

---

## 付録C. Y-F01(Y runnerのStyle profile `default`固定)の要約

詳細は `Y_F01_STYLE_PROFILE_CHECK_01.md`。

- **コード**: `er121_family_y_runner_01.py:37 STYLE_PROFILE = "default"`(理由コメントなし)。TTS生成・gate・assembleにそのまま渡り、`default`は基底6-role Styleの素通し(`er019_family_x_style_profile_01.py:229-230,347-358`)。Yは`resolve_run_profile`を呼ばず`audit/style_profile.json`も作らない。
- **設計・承認側**: `DESIGN_01.md:84`『Style: profile `fx_20261017`を継承』・`SPEC_LEDGER_03.md:60` YL-A01=APPLY・DEV Trial `er110:40`は継承。ユーザー原文は個別のStyle名の名指しではなく一般規定(『他Familyで`APPROVED_FOR_PRODUCTION`の共通仕様はYも適用対象』…LAUNCH-01_USER.md:162-166、『既存の正式な速度・Style・TTS設定を継承』…VOICES-DESIGN-01_USER_09.md:64)。`default`を承認/除外した記録は0件(設計・台帳・DECISION_LOG・OPEN_ITEMS・CURRENT_SPEC・UDR・コミット本文)。
- **runtime**: Y run_01の送信Styleは基底(本文=`calm, steady news narration…`、Std本文は更に減速指示連結、KP=MINIMAL、Preview=`calm, conversational`、JA支援=基底)。`fx_20261017`のPD06/S3/E1/K2/P8-KP/P7は1つも使われず、X M3は`checked=[]`。
- **3択の事実**: 継承が仕様か=設計・台帳・Trialでは『継承』(ユーザー原文は一般規定)/`default`が承認済みか=承認記録なし/意図的除外の記録=なし。分類提案=**B疑い・重要度高**(Fable確認先行)。
- **完成版を今制作した場合**: default固定のまま=現行公開版と同条件(仕様違反の可能性を残す)/`fx_20261017`へ切替=tts再生成+新out_dir(M2)。Voice 2/3の再利用は成立しない。是正は未実施。

---

## 付録D. 読込・Grep・実行コマンド(一覧外Readを含む)

- 統合元: `COMMON_CORE_01.md`・`FAMILY_X_01.md`・`FAMILY_Y_01.md`・`FAMILY_Z_01.md`(全文Read)、各`*_01.json`(構造確認のみ)。ユーザー原文 `docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_USER.md`(全文Read)。
- Y-F01確認: `er121_family_y_runner_01.py:25-50,960-968`、`er121_family_y_audio_01.py`(Grep `style_profile|STYLE_PROFILE|x_gate|fx_20261017`、`:239-249,429-431,516-518,672-722`)、`er019_family_x_style_profile_01.py`(`:5-30,165-232,276-283,290-295,326-395,440-460,685-697`)、`er110_family_y_audio_trial_01.py`(Grep)、`CURRENT_SPEC.md`(Grep `fx_20261017|Y化時|配線対象`、`:1268,1690-1710`)、`DECISION_LOG.md`/`OPEN_ITEMS.md`(Grep)、`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/{DESIGN_01.md:60,84; SPEC_LEDGER_01..04; OPEN_TRACKING_01.md:10,22; EVIDENCE_0*; OPUS_REVIEW*}`(Grep)、`docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_{USER,USER_02,USER_03}.md`・`2026-10-25_FAMILY-Y-VOICES-DESIGN-01_USER_09/10.md`・`2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_DELEGATION_02B.md:8`・`2026-10-26_FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01_USER.md`、`er121_output/family_y_production_01/{redelivery_fee,sns_age_limit}/run_01/{b1b,a2}/audit/{tts_generation_results,y_style_profile_gate}.json`・`cost_by_stage.json`。
- 事前指定一覧外Read: `docs/pm/delegation_log/2026-10-21_FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01_FALLBACK-APPROVAL-FINAL-ASSEMBLY_USER.md`(10-21決定の行番号確認)、`…2026-10-26_FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01_USER.md`・`…FZ-CONTEXT-EMOTION-TTS-PRODUCTION-WIRING-01_USER.md`(逐語確認)、`docs/research/FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01/{PLAN_01,INVENTORY_01}.md`(Grepのみ)、`er020_tts_retry_local_rewrite_01.py:57-93`・`er003_v1_sing01_news_tail_fix.py:140-236`、`DECISION_LOG.md:9711-9716`、`OPEN_ITEMS.md:885,1043`、`py -c`によるresolve_narrative_role実測(API 0)。
- T-0: 委任文を `docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01_DELEGATION_02.md` に保存し `check_delegation_prompt.py` を実行(PASS)。
