# EDITORIAL-B-FAMILY-VOICES-TRIAL-09-LOCK-RETRY-AND-FULL-ASSEMBLY-02

管理ID: EDITORIAL-B-FAMILY-VOICES-TRIAL-09-LOCK-RETRY-AND-FULL-ASSEMBLY-02(Lane B)
日付: 2026-09-07

対象: `EDITORIAL-B-FAMILY-VOICES-TRIAL-09-AUDIO-STRUCTURE-REFINEMENT-01_REPORT.md`
(`er012_editorial_b_voices_trial_09_audio.py`、出力
`er012_output/editorial_b_voices_trial_09_audio/`)で、Narrator見出し
segment `point_two_heading`("Another Voice: The freedom to move.")が
`ASR_VALIDATION_UNCERTAIN` → `HUMAN_REVIEW_LOCKED` となり1本化Assemblyが
ブロックされている件の、attempt事実確認・分岐判定・調査・Gate 7チェック
リスト拡張。

---

## 1. attempt数の事実確認(一次証拠)

一次証拠: `er012_output/editorial_b_voices_trial_09_audio/b1b/audit/
review_lock_state.json`、`.../audit/raw_usage_log.jsonl`、
`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`
(entry #31、point_two_heading分)。

| 項目 | 値 |
|---|---|
| TTS生成試行(loop attempt) | **1回のみ**(`cumulative_tts_attempts=1`、`attempts/point_two_heading_attempt1_englishstyleprefix.wav`のみ存在、attempt2ファイルは無し) |
| ASR呼び出し(record_outcome計上分) | 1回(attempts_logの計上ルール上、cascade内部呼び出しは別計上) |
| ASR呼び出し実数(raw_usage_log.jsonl直接確認) | Primary(OpenAI gpt-4o-mini-transcribe)×2 + Secondary(Azure STT)×2 = **4回**、加えてHuman Reviewパッケージ充実用のPronunciation Research(Perplexity)×1回 |
| 何回目でHUMAN_REVIEW_LOCKEDになったか | TTS 1回目の生成直後、ASR Cascade4段全て不一致となった時点(2026-09-07T18:01:34、`review_lock_state.json`の`updated_at`) |
| 全4段のASR書き起こし内容(human_review_queue.jsonl) | Primary#1: `"the freedom to move"` / Primary#2: `"the freedom to move"` / Secondary#1(Azure): `"The freedom to move."` / Secondary#2(Azure): `"The freedom to move."` — **4段全てで先頭の"Another Voice:"が欠落、内容は完全に一致** |

比較用(同構造の兄弟segment `point_one_heading`「One Voice: The desk that
lets work begin.」): TTS試行1回目(loop attempt 1)で`NORMALIZED_MATCH`
verified=Trueとなり、正常にRESOLVED(このsegmentは今回の問題を再現しない)。

## 2. 規定されているretry上限(原文引用)

**(A) TTS総試行回数の上限(`er011_human_review_lock_01.py` 74-80行)**:

> ユーザー正式決定(2026-08-28): 同一segmentのTTS生成総試行回数上限を
> 3回とする(初回を含め最大3回、「初回+3 retry」ではない)。
> `PRODUCTION_MAX_TTS_ATTEMPTS = 3`

→ この上限は「初回+retry N回」ではなく「**総attempt3回**」であることが
コード上明記されている。`point_headings.generate()`は
`max_attempts=review_lock.PRODUCTION_MAX_TTS_ATTEMPTS`をそのまま使用
(`er003_v1_sing01_point_headings_aoede.py` 44行、確認済み)。

**(B) しかし、分類ごとに扱いが異なる(`should_retry`)。CURRENT_SPEC.md
「TTS Retry条件(絞り込み)」節(ER-006-AUDIO-RETRY-CASCADE-PROD-01、
2026-08-22、原文)**:

> TTS音声の再生成(regenerate)は、以下に該当する場合のみ行う: 真の内容
> 誤り(true content mismatch)、数値/年/日付の意味的な違い、否定の有無の
> 違い、**重要語の欠落・追加**、TTS技術的失敗(hallucination・
> INVALID_ARGUMENT等)、Human Reviewで実際の音声誤りと確認された場合。
> **固有名詞のASR表記ゆれのみを理由とした繰り返しTTS再生成は行わない**
> (上記ASR-first Retry Policyでのre-verificationを先に尽くす)

**(C) 実装(`er006_preprod_hardening_01_validation.py`
`_classify_asr_match_core()` 910-919行、原文)**:

> ```
> if entity_only_diffs:
>     return ClassificationResult("ASR_VALIDATION_UNCERTAIN", ratio, protected,
>                                  should_pass=False, should_retry=False,
>                                  reason="固有名詞らしき語にのみ音訳差がある(retryでは解決しない可能性が高い): ...")
> ```

`should_retry=False`が直接設定される(TRUE_CONTENT_MISMATCHの
`should_retry=True`とは明確に異なる)。さらにCascade側
(`er006_secondary_asr_01.py` 712-716行、原文):

> ```
> # --- 4 step全て不一致 -> Human Review(TTSは再生成しない、§9の通り
> # 固有名詞だけの表記差ではretryしない) ---
> result["human_review_required"] = True
> result["stop_retrying"] = True
> result["final_status"] = "ASR_VALIDATION_UNCERTAIN"
> ```

**結論**: 分類が`entity_only_diffs`(固有名詞らしき語のみの差)に該当する
場合、TTS blind retryは**設計上そもそも1回のTTS試行しか許可されない**
(3回のTTS試行枠を消費するのは`should_retry=True`となる
`TRUE_CONTENT_MISMATCH`等のみ)。`stop_retrying`はASR Cascade(Primary#2+
Secondary#1+Secondary#2)を1回のTTS音声に対して尽くした上で決まる
(`should_stop_retrying()`の3回連続signature判定[`er006_preprod_
hardening_01_validation.py` 1015-1027行]は`TRUE_CONTENT_MISMATCH`向けの
別ルートであり、entity_only_diffsの即時ロックには関与しない)。

## 3. 分岐判定

**分岐B(既に規定どおりの打ち切り)** と判定した。

根拠: point_two_headingは§1の通りTTS試行1回のみだが、§2(C)の通り、
`ASR_VALIDATION_UNCERTAIN`かつ`entity_only_diffs`分類の場合は
`should_retry=False`が**直接**設定され、TTS blind retryは規定上そもそも
発生しない設計である(3回の総枠は消費されない設計)。ASR Cascade4段
(Primary#2/Secondary#1/Secondary#2)は全て実行済みで(§1参照)、4段目まで
尽くした上でHuman Review Lockへ到達している。これは「規定回数[3回]に
届く前の異常停止」ではなく、「UNCERTAIN(固有名詞様の内容語欠落)は
即Lock、TTS blind retryしない」という**規定どおりの動作**である。

→ 指示に従い、**再生成は行っていない**。新Validator・fallback・
Production overrideの追加も行っていない(調査のみ)。

ただし、後述§4のとおり、「entity_only_diffs」という分類自体が、この
ケースでは編集見出しラベル("Another Voice:")を実在の固有名詞と誤って
同一視した結果であり、§2(B)の規定が本来カバーする「重要語の欠落・追加
→ retryすべき」に実質該当する可能性がある(規定の**文言上の意図**と
**実装の分類ヒューリスティクス**の間にギャップがある)。これは実装の
妥当性に関する調査結果であり、新規対策の実装は行っていない
(`USER_DECISION_REQUIRED`、§8参照)。

## 4. 調査結果((i)〜(vi))

**(i) 同種事例(ASRが見出し先頭語句を脱落する)の過去事例**:
`er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`
(全31件)を全件確認した。直接の同型事例(短い見出しラベル+コロン+
本文、というcanonical_text構造)としては、pool_n7_assigned_desks系の
2件(entry #2,#3,#27)で、canonical_textが`"## Main Story Walk into
some offices today..."`のようにMarkdown見出し記法`"## Main Story"`を
含んでおり、ASR Cascade4段全てが一貫して`"## Main Story"`を脱落させ
`"Walk into some offices today..."`のみ書き起こしていた実例を確認した。
ただしこれは「canonical_textにMarkdown記法が混入したテキスト抽出側の
バグ」が根本原因であり(点二見出しのような正規の編集見出しラベルとは
異なる)、**根本原因は異なる**。しかし症状(短い先頭ラベルが複数ASR
providerで一貫して脱落する)という現象自体は一致しており、「TTSが
短い先頭ラベルを軽視・省略する傾向」自体は本件が初出ではないことを
示す状況証拠として記録する。その他29件(固有名詞の表記ゆれ:
Bisnow/BizNow/Biznow、Kristie Tse/Christy C等)は本件と異なる系統
(実在人名・社名の表記ゆれ)であり、先頭語句脱落パターンではない。

**(ii) Primary ASR(gpt-4o-mini-transcribe)の非決定的揺れの可能性**:
低いと判断する。Primary#1とPrimary#2(同一音声に対する2回目のASR呼び
出し)が**完全に同一のテキスト**(`"the freedom to move"`)を返しており、
非決定的な揺れは観測されなかった。

**(iii) TTS側の実発話欠落の直接確認**: 保全されたwav(`b1b/narration/
attempts/point_two_heading_attempt1_englishstyleprefix.wav`、および
`b1b/audit/stopped_audio_evidence/point_two_heading_last_attempt_
status_HUMAN_REVIEW_LOCKED.wav`、同一内容)に対し、Production Secondary
ASR(Azure、既にCascadeで2回実施済み、§1参照)に加えて、**ローカル
faster-whisper(`er008_disfluency_qa_18.transcribe_verbatim`、無料・
読み取り専用・追加API課金なし)による独立の第三の確認**を実施した。
結果: `"the freedom to move."`(word_count=4)のみを検出し、"Another
Voice"は一切検出されなかった。加えて、音声長を比較したところ、
point_two_heading(実際に発話された4語)の音声長は2.12秒であるのに対し、
兄弟segment point_one_heading(8語、"One voice, the desk that lets
work begin.")は3.89秒であり、仮に"Another Voice:"(2語)を含む全6語が
話されていれば単語あたり秒数(point_one_headingの実測比率、約0.49秒/語)
から推定して約2.9秒程度になるはずのところ、実測2.12秒はこれより明確に
短い。**OpenAI Primary×2・Azure Secondary×2・ローカルfaster-whisper×1の
計3方式・5回の独立ASR確認、および音声長分析が全て一致して「Another
Voice:」の非発話を示しており、ASRの偶発的な聞き逃しではなく、TTS側の
実発話欠落である可能性が高いと判断する。**

**(iv) Secondary ASR等での安全な追加確認の余地**: 上記(iii)で既に
Secondary(Azure)×2・ローカルfaster-whisper×1を実施済みであり、
これ以上の追加確認手段は現時点で見当たらない(追加コストも発生させて
いない、¥0)。

**(v) 既存仕組み(OPEN-119/OPEN-122/OPEN-123)での説明・再利用可能性**:
いずれも本件には適用されない、または適用条件に該当しない。
- **OPEN-119**(非ラテン文字cascade、Key Phrase英語経路限定の
  `enable_non_latin_cascade`)は、`point_headings.generate()`の
  `evaluate_attempt_with_cascade()`呼び出しで明示的に渡されておらず
  (既定False)、かつ本件のASR出力は非ラテン文字ではないため無関係。
- **OPEN-122**(Connected Speech Equivalence Layer)は、
  `classification == "TRUE_CONTENT_MISMATCH"`の場合のみ後段として発火
  する設計(`er006_secondary_asr_01.py` 518-519行)。本件の分類は
  `ASR_VALIDATION_UNCERTAIN`(entity_only_diffs)であり、そもそも
  到達条件を満たさない。また同機能は「語境界の自然な再分節・弱化」を
  説明するものであり、「フレーズ丸ごとの欠落」には設計上対応しない。
- **OPEN-123**(標準contraction展開)は短縮形の表記差対策であり、
  本件は短縮形の問題ではないため無関係。

**(vi) 新規対策の候補(実装せず提示のみ)**:
根本原因は`capitalized_flags()`(`er006_preprod_hardening_01_
validation.py` 451-473行)が、大文字始まりの語を機械的に「固有名詞
候補(entity_like)」とみなす粗いヒューリスティクスであり、編集上の
見出しラベル("Another Voice:"、"One Voice:"のようなTitle Case見出し)を
実在の人名・地名等と区別できない点にある。この結果、本来はCURRENT_
SPEC.md「TTS Retry条件」節が明記する「重要語の欠落・追加」(retry対象)
に該当しうる内容誤りが、「固有名詞ASR表記ゆれ」(retry対象外)の分岐へ
誤って振り分けられ、TTS blind retryの機会(残り2回の枠)が実質的に
失われている。改善候補としては、例えば「見出しラベル(Point heading等、
既知の限定的なsegment種別)では、capitalized_flagsによるentity_like判定
を適用しない、またはdelete型diff(語の完全欠落、置換ではない)には
entity_only_diffs分類を適用しない」といった限定的な修正が考えられるが、
これは新規Validatorロジックの変更であり、本タスクの指示(調査のみ、
新Validator禁止)により**実装していない**。別Trial候補として提示する
のみ(`USER_DECISION_REQUIRED`)。

## 5. Assembly/player

分岐Bのため、**1本化episode Assemblyは実施していない**(Gate未解消、
point_two_headingは引き続きHUMAN_REVIEW_LOCKED)。既存Production
primitive(`build_b1_voices_timeline_trial09`/`assemble_with_timeline`/
`apply_headroom_safety_valve`)は呼び出していない。

player.htmlは、ユーザー新ルール(各音声の再生ボタンと対応scriptを同一行
または直近に配置)に沿って**再構成した**(既存のfallback per-segment
player構造[13 segment、構造順]を維持しつつ、従来は別セクション
[「完全スクリプト」]に分離されていたscript本文を、各segmentの再生
ボタン・voice名と同一グリッド行[`<div class="segrow">`]へ統合。CSS
grid`260px 260px 1fr`で「メタ情報(順序/label/voice/status)」「再生
ボタン」「script本文」を横並びの1行にした)。point_two_heading(行8)は
引き続き`HUMAN_REVIEW_LOCKED`のevidence wav(`stopped_audio_evidence/
point_two_heading_last_attempt_status_HUMAN_REVIEW_LOCKED.wav`)を赤枠
表示のうえ理由を明記している。1本化Assemblyが未実施のため、seek可能
timelineは提供していない(「Timeline(seek可能)」節に明記)。

## 6. Gate 7 音声artifact受入チェックリスト照合

| 項目 | 判定 | 備考 |
|---|---|---|
| (a) 完成episode音声(部品sampleではなく実episode構造) | **未充足** | Gate未解消のためAssembly未実施。fallback per-segment player(構造順13行)のみ |
| (b) Preview | 充足 | 行1 |
| (c) Comment全件 | 充足 | 行2/5/10/12(comment_1〜4) |
| (d) 本文全section | 充足 | Hook(行3-4)/Voice A・B見出し・本文(行6-9、行8は評価不可としてマーク)/Tension(行11)/Closing(行13) |
| (e) Key Phrase英語+日本語gloss | **対象外** | 本player(fallback per-segment player)は元々Key Phraseを含まない構造(Trial-09の既存設計を踏襲、本タスクでは拡張せず) |
| (f) Intro/Outro/SFX/固定文言 | **対象外** | 同上、fallback playerの既存範囲外(固定文言は共有Master Audio Store音声のため個別に別途生成済みだが本playerには含めていない) |
| (g) 実際のsegment order・開始秒・click-seek | 一部充足 | segment orderは明記(1-13)。1本化wavでないためseekは無し(per-segment再生のみ) |
| (h) 各segmentの使用voice名 | 充足 | 各行の再生ボタン欄に明記 |
| (i) A2/B1等レベル別の明確な分離 | 充足 | B1のみ(タイトルに明記) |
| (j) テキスト未取得segmentは「未取得」と明記 | 充足 | 該当なし(全segmentのscriptは既存canonical_textから取得済み) |
| (k) Standard/Batch等TTS方式の明記 | 充足 | 冒頭に「Standard同期」明記 |
| (l) 再生ボタンと対応scriptの同一行配置(新規) | **充足** | 全13行をCSS gridで統合、視線移動・長スクロール不要 |

## 7. cost/model/TTSモード

- 本タスク(調査)で新規に発生したTTS/ASR API課金: **¥0**(TTS/ASR API
  呼び出しは一切行っていない。`raw_usage_log.jsonl`の最終行は本タスク
  開始前と同一[Trial-09原実行時のもの]であることを確認済み)。
- 本タスクで実行した診断: (1) `classify_asr_match()`/`evaluate_
  attempt()`のPure Python再実行(canonical_text/asr_textの2文字列
  比較のみ、API呼び出しなし)、(2) 保全wav 2件に対するローカル
  faster-whisper(`small`、CPU、`compute_type=int8`)による書き起こし
  (無料、ネットワーク課金なし)。
- Trial-09原実行時点(既に発生済み、今回新規発生ではない)の
  point_two_heading関連コスト: Gemini TTS(`gemini-2.5-pro-preview-tts`、
  Standard、1回)+ OpenAI ASR(`gpt-4o-mini-transcribe`、2回)+ Azure
  STT(`azure-speech-stt`、2回)+ Perplexity(`sonar`、pronunciation
  research、1回)。いずれも数円未満〜十数円規模(`raw_usage_log.jsonl`
  参照、詳細は元Trial-09 Reportの管轄)。
- TTS実行モード: `tts_execution_mode="STANDARD"`(point_two_heading
  attempt1のmetadata、`TTS_EXECUTION_MODE=STANDARD`、ユーザー指定どおり)。

## 8. USER_DECISION_REQUIRED

以下は新規仕様候補であり、**実装していない**。ユーザー判断を仰ぐ。

1. `capitalized_flags()`/`entity_only_diffs`分類が、実在の固有名詞と
   編集見出しラベル(Title Case、例: "Another Voice:"、"One Voice:")を
   区別できていない可能性がある(§4(vi))。これにより、本来は「重要語の
   欠落」としてTTS retry対象になるべき内容誤りが、retry対象外の
   「固有名詞ASR表記ゆれ」へ誤分類され、Human Review Lockへ到達する
   前にTTS blind retryの機会(残り2回の枠)が実質的に失われている
   可能性がある。改善候補: (a) 見出し系segment(Point heading等)では
   entity_like判定を適用しない、(b) delete型diff(完全欠落、置換ではない)
   にはentity_only_diffs分類を適用しない、等。別Trialでの検証要否を
   判断してほしい。
2. point_two_heading自体の扱い: 今回は指示どおり再生成していないため
   `HUMAN_REVIEW_LOCKED`のまま(音声は"the freedom to move"のみで
   "Another Voice:"欠落)。人間による最終判断(a. 明示的な
   `approve_regenerate()`でのユーザー承認後の再生成、b. 見出しテキスト
   自体の変更[例えば見出しを話さない構造へ変更]、c. 他の対処)を
   仰ぎたい。

## 9. 変更ファイル一覧

- `EDITORIAL-B-FAMILY-VOICES-TRIAL-09-LOCK-RETRY-AND-FULL-ASSEMBLY-02_REPORT.md`(root、新規、本ファイル)
- `er012_output/editorial_b_voices_trial_09_audio/player.html`(再構成、Gate 7 (l)対応)
- `docs/pm/PM_GOVERNANCE.md`(Gate 7音声artifact受入チェックリストへ(l)追加)
- `DECISION_LOG.md`(本タスクのエントリを1件追記)
- `OPEN_ITEMS.md`(OPEN-120行へ調査結果・ユーザーVoice評価所見を追記)
- `docs/pm/ACTIVE_TASK.md`・`docs/pm/RESULT_PACKET.md`(本タスク用に上書き)

Production・音声生成コード(`er011_*`、`er003_v1_*`、`er006_secondary_
asr_01.py`、`er006_preprod_hardening_01_validation.py`等)は**一切変更
していない**(読み取り・診断呼び出しのみ)。Git操作は実施していない
(Fableが統合commitを行う)。
