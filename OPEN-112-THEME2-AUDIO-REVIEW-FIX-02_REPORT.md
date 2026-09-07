# OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 サブタスクA レポート

管理ID: OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 / サブタスクA
対象: `er011_output/open112_trend_theme2_b_final_audio_rerun_02/`
(Theme 2, A2/B1) の完成音声、ユーザー試聴で報告された重複3件
到達Status: **`USER_DECISION_REQUIRED`**(新規 OPEN-121)

## 1. 重複3件それぞれの根本原因

| # | Segment | 現物で再現 | 根本原因 |
|---|---|---|---|
| 1 | B1 / Full Story Part 1 | **できず** | ユーザー報告の症状を、現行rerun-02音声(narration単体・assembled episode該当区間の両方)で確認できなかった。sha256もTrial-13原本と完全一致。 |
| 2 | A2 / Point Two | **確認** | Trial-13時点のGemini TTS生成自体のhallucination。冒頭2文がまるごと1回逐語反復(offset≈9.63秒、spectral self-similarity run長0.60秒)。 |
| 3 | A2 / In One Line | **確認 → 修正済み** | 同上。主節全体が1回逐語反復(offset≈8.2秒)。 |

## 2. 同一failure modeか

Point Two・In One Lineは同一failure mode(TTS生成時に、直前まで読んだ
内容の一部/全部をそのまま読み直すhallucination。time-stretch・コピー・
Assemblyでは発生しない、生成そのものの欠陥)。B1 Full Story Part 1は
現物で再現できず、同一failure modeか判定不能。

## 3. 各segmentでASRが実際に返した内容

- Point Two: Production Primary ASR(gpt-4o-mini-transcribe)は複数回
  (final版・pre-slowdown原本とも各4回、計8回)呼び出しても**一度も**
  重複を検知しなかった。6〜22秒を切り出して再ASRして初めて
  "…still showed strong interest in famous tourist places. Young
  travelers are not one single market. Women aged 29 and under still
  showed strong interest in famous tourist places at about 45%…" と
  重複transcriptを確認。
- In One Line: 同ASRを4回呼び出すと3回は重複を含むtranscriptを返し、
  1回は平滑化して重複なしのtranscriptを返した(非決定的)。

## 4. transcriptに重複が残っていたか/消えていたか

Trial-13生成時点で記録された`asr_text`/`post_slowdown_asr_text`は
**両segmentとも重複が消えた(平滑化済み)状態**で記録されていた。
ただし、In One Lineのみ既存disfluency QA(faster-whisper local
verbatim)の生transcriptには重複が正しく残っていた
(`disfluency_evidence.transcript`に重複文字列がそのまま存在)。

## 5. 過去の類似対策の管理ID・仕様・実装箇所

ER-008-N8-QA-CONTENT-SPEED-HARDENING-18/19(`er008_disfluency_qa_18.py`)。
faster-whisperによるローカルverbatim word-level ASRで、隣接する
同一token(`detect_adjacent_word_repetition`)を検知する。モジュール
docstring自身が「単語がまるごと繰り返されるパターンの検知に限る」
「意図的に狭い定義(false positiveを避けるため)」と明記。適用範囲は
short/high-riskセグメント(comment_1-4・point見出し・in_one_line)のみ
(ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19、`disfluency_qa=(name ==
"in_one_line")`のように明示的スコープ限定)。full_story/point本文は
対象外。

## 6. それが今回なぜ機能しなかったか

- Point Two: そもそもdisfluency_qa自体が承認スコープ外(本文segment)
  で未適用。Production Primary ASRも一度も重複を捉えられなかった。
- In One Line: disfluency_qaは適用され、生transcriptには重複が正しく
  記録されていたが、判定ロジックが「直後に同一token」のみを検知する
  設計のため、句・文単位の反復(直後の単語は異なる)を原理的に検知
  できなかった(flagged=False)。

## 7. 初回/retry/fallback/regeneration/Assembly間の仕様整合

sha256比較で、Trial-13の初回生成からrerun-02へのコピーはbit単位で
無改変であることを確認済み(Assembly/コピー起因ではない)。6%
time-stretch前の`_original.wav`にも同一比率で重複が存在するため、
post-process(time-stretch)でも発生していない。両segmentともretryは
発生していない(Trial-13時点でattempt1が一発でASR"合格"していた)。

## 8. 修正内容

新しいValidator原則・判定ロジックは一切追加・変更していない。
`er011_open112_theme2_audio_review_fix_02_regenerate.py`(root新規)で、
既存Production関数(`generate_a2_segment_with_slowdown`、無変更・
パラメータもProduction呼び出しと同一)を呼び直した。

- **A2 In One Line**: 1回で`status=OK`(disfluency_checked=True・
  flagged=False、実際に重複なし)。`stage_assemble_a2()`(無変更)を
  再実行し完成episodeへ反映。
- **A2 Point Two**: 再生成2回とも別の内容不一致(canonical「showed」→
  ASR「show」、今回の重複バグとは無関係)で`TRUE_CONTENT_MISMATCH`、
  既存Human Review Cost Guard(ER-011-HUMAN-REVIEW-COST-GUARD-01)が
  `HUMAN_REVIEW_LOCKED`へ到達。既存Gateを独自に回避せず、Trial-13原本
  (sha256で原本一致を確認済み、既知の重複入り)のまま据え置いた。
- **B1 Full Story Part 1**: 症状を再現できないため何もしていない。

## 9. segment単体runtime evidence

`er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/
duplication_diagnosis_review_fix_02/player.html`に、3件それぞれの
修正前/修正後(該当する場合)narration単体wavをまとめた。In One Lineは
修正後、gpt-4o-mini-transcribe 5回・spectral self-similarityとも重複
消失を確認(run長最大0.18秒=背景ノイズ水準)。

## 10. 完成episode runtime evidence

同ページに、修正後の完成episode(A2, `stage_assemble_a2()`再実行後)
から各該当区間を切り出した音声を格納。A2 duration 375.226秒→
366.181秒(In One Line修正分の約9.045秒減)、peak 0.98・clipping無し
(headroom safety valve、Point One起因、修正前と同一挙動)。B1は
未変更(341.975秒のまま)。

## 11. ASR/Validatorで今回failure modeを検知・防止できる証拠

現状の仕組みでは体系的に防止できない: (a) Production Primary ASRの
全文一括書き起こしは非決定的にこの種の反復を平滑化する(実測: 同一
音声への複数回呼び出しで結果が変動)。(b) 既存disfluency QAは対象
segmentが限定的かつ判定ロジックが単語単位に限定されているため、
句・文単位の反復は原理的に検知できない。windowed(短い区間に区切って
再ASR)+spectral self-similarityの組み合わせは今回の診断で有効性を
実証したが、これはProduction Validatorとして未配線・未承認(本タスク
の診断ツールとして使用したのみ)。

## 12. regression

`run_project_regression.py`: collected=2110, passed=2107, failed=3
(`er003_test_bad.FixtureTests.test_case_0`、`er003_test_p2j_
investigate`内2件。いずれも本タスク以前から存在する既知の無関係
failure、新規failureなし)。

## 15. 新規USER_DECISION_REQUIREDの有無

あり。新規OPEN-121登録。要決定事項:
1. Point Two残存重複の扱い(`approve_regenerate()`の明示承認 or
   現状の重複入り音声のまま据え置くか)。
2. disfluency QAをn-gram/句単位反復検知へ拡張するか(既存の「意図的に
   狭い定義」の変更、false positive増リスクとの兼ね合い)。
3. disfluency QAの適用スコープをfull_story/point本文segmentへ拡張
   するか(処理コスト再評価要)。
4. Production ASRの非決定的平滑化への対策(複数回ASR多数決・逐語
   ローカルASR併用等)を新acceptance条件として採用するか。
5. B1 Full Story Part 1: 症状が現物で再現できないことについて、
   ユーザーへ確認(試聴環境・キャッシュ等の可能性)。

## 16. wiring/SSOT/Git反映

Production Validator/disfluency判定ロジックのwiring変更なし
(既存関数を無変更のまま再呼び出ししたのみ)。SSOT: `OPEN_ITEMS.md`へ
OPEN-121新規登録、`DECISION_LOG.md`へ
`OPEN-112-THEME2-AUDIO-REVIEW-FIX-02`エントリ追加。Git commit hashは
このReportのcommit後にコミットメッセージへ記載(後続参照)。

## 試聴用ページ(file:///)

- 完成episode(修正反映済み):
  `file:///C:/Users/tensh/eigo-radio/er011_output/open112_trend_theme2_b_final_audio_rerun_02/player.html`
- 診断・修正前後の切り出し比較:
  `file:///C:/Users/tensh/eigo-radio/er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/duplication_diagnosis_review_fix_02/player.html`
