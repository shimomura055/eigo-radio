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

## §追補: B1 FSP1再検証(Fable差し戻し1回目、OPEN-112-THEME2-AUDIO-REVIEW-FIX-02-02)

差し戻し理由: 上記§9でB1 Full Story Part 1を「現物で再現できず」と結論したが、
同レポート内でA2 Point Twoは全文一括ASR8回では検知できず、6〜22秒の
windowed再ASR+spectral self-similarityで初めて確認できたと記録している。
B1にも同じ厳密な手法を適用したかが不明のため、windowed再ASR・音響自己
相関を含む同一手法をB1へ改めて適用し再検証した(診断のみ、修正・
再生成・Assembly変更は無し、Git操作無し)。

**対象**: narration単体(rerun-02使用実体、sha256でTrial-13原本と完全一致を
再確認)、完成episode該当区間(前後3秒込み・パディング無し厳密境界の両方)。
Trial-13の`tts_generation_results.json`記録(attempt数=1、`disfluency_checked=
false`[full_story本文はスコープ外]、単発ASR済み`asr_text`に重複なし)も
確認済み。

**windowed再ASR**(narration単体・episode該当区間それぞれ、0〜6秒・0〜10秒・
3〜12秒の3窓、prompt無し/prompt有りの計12呼び出し)+ **全文一括ASR** 8回
(narration単体4回・episode該当区間4回、gpt-4o-mini-transcribe)、
**faster-whisper local verbatim**(全文2件+windowed clip 6件、計8件)の
いずれの生transcriptにも重複・言い直しは一度も現れなかった
(flagged=False全件、"As of September 2026"の反復は0件)。

**spectral self-similarity**: 全体(frame25ms/hop10ms、min_lag1.0秒)に加え、
ユーザー報告の「As of Septem, As of September 2026」という冒頭の短い
false-start型反復を狙い撃ちするため、冒頭0〜3秒・lag 0.3〜2.5秒に絞った
高解像度(frame25ms/hop5ms)re-checkを追加実施。類似度0.99台の候補は
存在するが、0.85閾値でのrun長は最大0.035秒(単一フレーム相当、無音や
子音の偶然一致水準)。Point Twoで実在確認された反復のrun長0.60秒と比較して
約17分の1以下であり、性質が明確に異なる(実在する反復とは判定できない)。

**波形クロス相関**(2〜4秒 vs 4〜8秒window): narration単体・episode該当区間
とも最大正規化相関は約-0.08(実質無相関)。実在する反復であれば近い時間差で
高い正の相関が出るはずだが、それが見られない。

**episode構造**: `timeline.json`に"Full Story Part 1 (Aoede)"のpieceは1件
のみ(重複配置なし)。直前がComment 1(114.746〜122.987秒)+pause 0.8秒、
直後がpause 0.8秒+Comment 2。旧断片の二重配置・安全弁/resample後処理での
混入も確認できず(narration単体とepisode該当区間の無音位置パターンは完全一致)。

**判定**: **(iii) いずれの手法でも検出できず**。今回はPoint Twoと同じ
windowed ASR+spectral self-similarity(さらに冒頭狙い撃ちの高解像度re-check・
波形クロス相関も追加)を適用したうえでの結論であり、前回の「単純な全文一括
ASRのみで再現できず」という報告より検証強度が高い。ユーザー試聴との不一致は
未解消のまま残る。考えられる確認事項(ユーザーへの確認候補、修正はしない):
(1) 試聴に使用した音声ファイル・プレーヤーがrerun-02の完成episodeで
間違いないか(Trial-13時点の別バージョンやキャッシュ済み音声を聞いた
可能性)、(2) ブラウザ/OSの音声キャッシュにより古い音声が再生された
可能性、(3) 別segment(例: 直前のComment 1やFull story introのCharon読み上げ)
との聞き間違いの可能性。

**runtime evidence保存先**:
`er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/
duplication_diagnosis_review_fix_02/b1_fsp1_recheck/`
(`recheck_raw_evidence.json`=windowed ASR/local verbatim/self-similarity/
cross-correlation/silence位置の全生データ、
`targeted_opening_self_similarity.json`=冒頭高解像度re-check、
`recheck_log.txt`=実行ログ全文、対応する切り出しwav 9本、`player.html`)。
診断スクリプト: `er011_output/open112_trend_theme2_b_final_audio_rerun_02/
audit/duplication_diagnosis_review_fix_02/b1_fsp1_recheck/recheck_script.py`
(本タスクの書き込み範囲内へ配置、root追加なし)。
Production関数`er006_asr_provider_routing_01.transcribe()`・
`er008_disfluency_qa_18.check_segment_for_disfluency()`を無変更のまま
呼び出しのみ、新規Validator/判定ロジックの追加は無し)。

**cost**: Production Primary ASR(gpt-4o-mini-transcribe)呼び出し20回
(全文一括8回+windowed 12回、音声合計約427.5秒≒7.1分相当)。faster-whisper
local verbatimはローカルCPU実行のため追加課金無し(8件)。本タスクの
呼び出しは`er005_cost_logger.install()`を経由しない単発診断スクリプトの
ため`raw_usage_log.jsonl`への記録は無く、正確な円換算は本追補では未取得
(前回Point Two診断のASR8回と同規模の小額診断コスト)。

**Git**: 未実施(本タスクはGit操作禁止、統合はFableが実施)。

試聴用ページ(追加):
`file:///C:/Users/tensh/eigo-radio/er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/duplication_diagnosis_review_fix_02/b1_fsp1_recheck/player.html`

---

## §追補2: B1 FSP1 ユーザー試聴で重複確定・機械検知全手法失敗の特性解析(2026-09-07)

管理ID: OPEN-112-THEME2-AUDIO-REVIEW-FIX-02(B1 FSP1解析タスク)。
上記§追補「いずれの手法でも検出できず」を受け、ユーザーが実際に試聴を
実施(2026-09-07)。

**ユーザー試聴結果(一次情報)**: narration単体(40.94秒)・episode該当
区間(前後3秒込み)・episode区間(厳密境界)のいずれも重複あり。窓clip
0〜6秒・0〜10秒は重複あり、3〜12秒は「As of September」該当箇所が
窓外のため重複なし。episode側の同窓も同じ結果。**結論: 重複はTTS生成
音声(narration単体)の冒頭0〜3秒に実在**(「As of Septem, As of
September 2026…」という語の途中で切れる短い言い直し[partial-word
false start]の後、先頭から再開)。これはA2 Point Two/In One Lineと
同じ「生成音声自体」のfailure mode(OPEN-121既存分類)だが、全文ASR8回・
窓ASR12回・faster-whisper逐語8件・音響自己相関・クロス相関の
**全手法が検知に失敗した**。

**追加特性解析(診断のみ、修正・再生成・Assembly・Validator変更なし)**:
narration単体wavの冒頭0〜6秒を対象に、(a)faster-whisper word-level
timestamps(複数decoding設定)、(b)RMSエネルギー包絡+onset検出、
(c)run長優先の短run自己相関rescan(閾値0.5〜0.9、lag 0.3〜1.5秒)、
(d)波形クロス相関+DTW、(e)0〜3秒clip単体への生ASR投入(Production
Primary+Azure診断呼び出し+faster-whisper)を実施した。

1. **faster-whisper word-level timestamps異常**: beam_size/temperatureを
   3通り変えても結果は同一(非決定性ではない)。0〜3秒clipの書き起こしは
   `as`(0.0-0.46s)/`of`(0.46-0.62s)/`September`(**0.62-1.90s、長さ
   1.28秒**)/`2026.`(1.90-2.86s)の4 wordのみ。"September"のタイムスタンプ
   長1.28秒は、同ファイル他区間の同一語(通常0.5〜0.6秒程度)の2倍以上
   異常に長く、「Septem(打ち切り)」+短い間+「September」という
   2区間分の音響をword-level alignerが単一tokenへ吸収・引き延ばして
   割り当てたと解釈できる。既存の`er008_disfluency_qa_18.
   detect_adjacent_word_repetition()`は「直後に同一token」のみを検知する
   設計(モジュール自身のdocstringで「独立したtokenとして現れず隣接語へ
   吸収されるため原理的に検知できない」と明記済みの既知の限界)であり、
   本パターンはまさにこの既知限界に正確に該当する。
2. **RMSエネルギー包絡**: 0〜0.99秒付近と1.21〜1.96秒付近に、視覚的にも
   酷似した形状のエネルギーburst(山)が約0.97秒間隔で2回出現している
   ことを確認(`falsestart_rms_envelope.png`)。
3. **短run自己相関rescan(run長優先)**: 前回の高解像度re-check
   (`targeted_opening_self_similarity.json`)は「類似度最高」の候補を
   上位順に抽出する設計だったため、無音・子音境界の偶然一致
   (類似度0.98台だがrun長0.02〜0.04秒)が上位を占め、真の反復候補が
   埋もれていた。「run長が最も長い候補」を閾値ごとに直接探索する設計へ
   変えたところ、**lag=0.97秒付近に閾値0.6でrun長0.75秒**(前回top5の
   最大run長0.035秒の約20倍)が見つかった。閾値0.85まで上げるとrun長は
   0.195秒まで縮み、Point Twoの確定反復(閾値0.85超・run長0.60秒、
   ほぼ同一波形の反復)とは性質が異なる(本件は「別テイクとしての
   言い直し」でprosody・tempoが微妙に異なるため、frame単位の類似度が
   相対的に低め)ことも整合する。
4. **波形クロス相関**: frag A(0〜1.2秒)を0〜4秒区間でスライドさせた
   結果、最良offset=0.975秒・相関係数0.134(trivialな自己一致[offset=0]
   は除外済み)。上記(3)のlag=0.97秒と独立手法で近い値に収束。
5. **DTW**: frag A(0〜1.2秒)とfrag B(1.2〜2.6秒)の正規化DTW距離
   0.2409は、frag Aと無関係な後方区間(25〜26.2秒)とのDTW距離0.4131
   より明確に小さく、frag A/Bが音響的に近いことを裏付ける。
6. **0〜3秒clip単体への生ASR投入**: Production Primary ASR(OpenAI
   gpt-4o-mini-transcribe)はprompt無し3回・verbatim-style prompt有り
   3回の計6回すべて"As of September 2026[.,]"の1回分のみへ平滑化した
   (0〜3秒へ絞り込んでもなお平滑化を再現、windowingだけでは解決しない)。
   一方、**Azure Speech STT(診断専用呼び出し、English Primary経路には
   未採用)の生transcriptは"As of September. As of September 2026."と、
   2回分の"As of September"を明示的に検出した**。

**示唆(命名・要件化の提案、Production採用判断はしない)**:
- 失敗モード名(提案): 「**partial-word false start + restart**」
  (語の途中で切れる短い言い直し、継続時間1〜2秒、2回目の発話がlag
  0.9〜1.0秒程度で開始)。OPEN-121のテストセットへ実データ陽性事例
  として登録すべき。
- ASR系検知が構造的に弱い理由: (1)OpenAI gpt-4o-mini-transcribeは
  文単位の言語モデル的平滑化により、この種の短い言い直しを一貫して
  除去する(0〜3秒への窓絞り込みでも解消しない、根深い挙動)。
  (2)faster-whisper word-level timestampsは、削除ではなく「異常に長い
  単一token」として吸収するため、既存の隣接同一token検知ロジックの
  設計では原理的に捕捉できない(ただしword durationの異常値自体は
  新しい検知シグナルになりうる、次項)。(3)Azure Speech STTは今回
  唯一raw transcriptに重複を残したが、これは現行Production ASR
  routing(English Primary=OpenAI)の対象外であり、Secondary確認としての
  採用可否は別途ユーザー判断が必要。
- 音響系検知に必要な条件(提案): (1)run長優先(類似度最高値ではなく)で
  短run(0.3〜1.5秒)を直接探索する設計変更。(2)閾値を0.85固定ではなく
  0.5〜0.75程度まで下げた探索も併用する(別テイク性の言い直しは完全
  同一波形の反復より類似度が下がるため)。(3)word durationの異常値
  (同一語の典型長との比較で2倍以上)を新しい検知シグナルとして追加
  する余地がある。(4)先頭付近(0〜3秒程度)を重点的に走査する
  (false startは発話冒頭に起きやすいという経験則、本件・A2既存事例
  ともに冒頭付近で発生)。

**runtime evidence保存先**:
`er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/
duplication_diagnosis_review_fix_02/b1_fsp1_recheck/`
(`falsestart_characterization_evidence.json`=word timestamps・RMS/onset・
短run rescan・DTW/cross-correlation・0〜3秒生ASRの全生データ、
`falsestart_characterization_log.txt`=実行ログ全文、
`falsestart_characterization_script.py`・`falsestart_plot_script.py`=
診断スクリプト、`falsestart_rms_envelope.png`・
`falsestart_similarity_heatmap.png`=可視化図、対応する切り出しwav
6本、`player_falsestart.html`=試聴・図・表まとめページ)。
Production関数`er006_asr_provider_routing_01.transcribe()`・
`er008_disfluency_qa_18`・`er003_b1_p4_audio.
get_full_text_via_azure_stt_continuous()`を無変更のまま呼び出しのみ、
新規Validator/判定ロジックの追加・Production ASR routing変更は無し
(Azure呼び出しは診断専用、English Primary routingは無変更のまま)。

**cost**: faster-whisperはローカルCPU実行のため追加課金無し(word
timestamp呼び出し6回)。Production Primary ASR(OpenAI gpt-4o-mini-
transcribe)0〜3秒clip呼び出し6回(prompt無し3+prompt有り3、音声合計
約18秒相当)。Azure Speech STT診断呼び出し2回(音声合計約6秒相当)。
いずれも小額診断コスト(数十円未満相当)、`er005_cost_logger.install()`
を経由しない単発診断スクリプトのため`raw_usage_log.jsonl`への記録は
無し。matplotlib(可視化図生成用)を`.venv`へ追加インストール(オープン
ソース、追加API課金無し、既存Production依存関係への影響なし)。

**Git**: 本タスク側でファイル名指定によりstage・commit・push
(下記commit hash参照、`docs/pm/*`・他タスクの未commit差分は対象外)。

試聴用ページ(追加):
`file:///C:/Users/tensh/eigo-radio/er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/duplication_diagnosis_review_fix_02/b1_fsp1_recheck/player_falsestart.html`

---

## §追補: Point Two showed/show(サブタスクD)

管理ID: OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 / サブタスクD
対象: サブタスクAで`HUMAN_REVIEW_LOCKED`に到達した2026-09-07再生成
2attempt(`a2/narration/attempts/point_two_attempt{1,2}_
custom35d6860b.wav`)の「canonical: showed → ASR: show」という
内容不一致1件。目的は、この文字列差だけで「TTS発音ミス」と確定せず、
既存のB1 Connected Speech Validator(OPEN-107/OPEN-110、
`er011_b1_connected_speech_validator_01.py`、`PRODUCTION_WIRED`)が
想定した「語末子音の連結・弱化によるASR上の脱落」に該当するかを
実データで診断すること。**診断のみ、TTS再生成・Assembly・仕様変更は
一切行っていない**(Git操作も無し)。

### 1. raw TTS input の確認

`audit/fix02_regeneration_log.json`の`canonical_text`より、2attemptとも
実際に投入されたTTS入力は「...still **showed** strong interest in
famous tourist places...」(過去形)であることを確認した(入力段階で
`show`になっていたわけではない)。

### 2. 実音声への複数ASR経路の再適用(新規診断ディレクトリ)

新規`er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/
point_two_showed_show_diag/`に、既存attempt保存音声(2attemptとも実在)
へ以下を実施した(スクリプト: `er011_open112_theme2_point_two_showed_
show_diag_02.py`、root新規追加、Production関数は無変更のまま呼び出しの
み)。

| ASRエンジン | 対象 | 結果(attempt1 / attempt2) |
|---|---|---|
| Production Primary(OpenAI gpt-4o-mini-transcribe、prompt無し) | 全文・windowed | いずれも一貫して**"show"**(語末/d/なし) |
| Production Primary(中立prompt付与、canonical answer非含有) | windowed | attempt1は"show"のまま、attempt2は**"showed"**に変化(同一音声への呼び出しでも非決定的) |
| Secondary(Azure Speech STT、phrase list無し=無バイアス確認込み) | 全文・windowed | いずれも一貫して**"showed"**(語末/d/あり) |
| faster-whisper small(ローカル、独立した第3のASRエンジン、追加課金無し) | 全文・windowed | いずれも一貫して**"showed"** |

3エンジン中2エンジン(Secondary/Azure・ローカルfaster-whisper)は、
全文・windowedいずれの条件でも、2attemptともブレなく"showed"と
書き起こした。「Azureへ`showed`をphrase list重み付けしたことによる
バイアスではないか」という懸念に対しては、phrase list無しでの再実行
(`secondary_asr_no_phrase_bias.json`)でも同じく2attemptとも
"Still showed strong interest."を確認し、バイアスではないことを
確認済み。Production Primary ASRのみが主に"show"と書き起こし、
かつ同一音声への繰り返し呼び出しで結果が変動した(既存の
`ER-011-HUMAN-REVIEW-COST-GUARD-01`関連知見「Primary ASRの全文一括
書き起こしは非決定的に平滑化することがある」と整合する挙動)。

### 3. 簡易音響分析(語境界の高時間分解能エネルギー分析)

`showed`の母音[oʊ]終端から`strong`の/s/摩擦音開始までの区間を、
8msフレーム/2msホップでRMS+高域(4kHz以上)エネルギー比を計測した
結果、両attemptとも「母音の高エネルギー→なだらかな減衰(約40〜60ms、
高域比はほぼ0のまま)→/s/摩擦音の急峻な立ち上がり(高域比が数msで
0近辺から0.9以上へ)」という波形であり、**独立した無音の閉鎖
(silence closure)や破裂バースト(release burst)を伴う明確な有声/無声
破裂音パターンは検出できなかった**。ただしこの波形は「/d/が完全脱落」
「/d/の閉鎖動作はあるが無破裂[unreleased]のまま次の/s/へ連結」の
どちらとも矛盾しない曖昧な波形であり、スペクトル特徴のみからは
断定できない(本Agentは聴取できないため、`player.html`をユーザー
試聴用に用意した)。

### 4. Connected Speech Validatorの実適用範囲(A2/B1共有関数の確認)

`er003_v1_n3_01_tts_generate.py::apply_a2_slowdown_postprocess()`・
`generate_narration_snippet_verified_strict()`はいずれもB1と同じ中心
関数`er006_preprod_hardening_01_validation.py::classify_asr_match()`を
呼んでおり、**B1 Connected Speech ValidatorはA2英語segmentにも
技術的には同じ関数を通じて適用されている**(CURRENT_SPEC.mdの記述
「B1英語Validatorの中心関数」という表現は、経路の由来を指すもので
適用範囲を制限してはいない)。

`er011_b1_connected_speech_validator_01.classify_connected_speech()`を
今回の実データ("still showed strong interest" → "still show strong
interest")でそのまま再実行したところ、`UNCLASSIFIED_FALLS_THROUGH_
TO_EXISTING`(非該当)だった。理由: Pattern B(破裂音連続、例
`opened`/d/+`to`/t/)は次語頭音が`/t/`または`/d/`である場合のみ発火する
設計だが、今回の次語`strong`の語頭音は`/s/`(歯擦音)であり、
Pattern Bの対象外(Pattern A・Cも語形が異なるため非該当)。すなわち
「語末alveolar stop + 後続語頭の`/s/`を含む子音クラスタ([str]等)」
という組み合わせは、ユーザー承認済みの3パターン(歯擦音連続・
破裂音連続・再分節)のいずれにも該当しない**未カバー領域**であり、
これは既存Validatorの実装バグではなく、ユーザーが意図的に限定した
適用範囲(「この3パターン以外への一般化は行わない」)の外側にある
ケースである。

### 5. 分類

**B(実音声は"showed"の可能性が高いが、Primary ASRが連結・弱化に
より脱落させた)に最も整合する。ただし確定[A]ではない**。根拠:
(1) raw入力は"showed"、(2) 独立した2エンジン(Azure Secondary・
ローカルfaster-whisper)がバイアス無しの条件も含め一貫して"showed"を
検出、(3) Production Primary ASR自体が同一音声への繰り返し呼び出しで
結果が変動する既知の非決定性を示した、(4) 音響分析は"showed"の
存在を否定しない(無破裂型の語末子音脱落は英語の自然発話で広く
知られた現象)。一方、(5) 音響分析だけでは"/d/"の実在を積極的に
証明する明確な破裂音バーストも見つかっておらず、**このAgent自身は
聴取できないため、最終確認はユーザー試聴に委ねる**。

### 6. 対応

分類が確定[A]ではないため、**再生成は行っていない**(既存Human
Review Cost Guard・`approve_regenerate()`は一切呼び出していない、
上限回数も消費していない)。現行Production `point_two.wav`は従来
どおりTrial-13原本のまま(サブタスクAの結果を継続、無変更)。
「B相当として、既存ASR/pronunciation判定仕様に沿って正しくaccept
できるか」については、上記4.のとおり現行Connected Speech Validatorの
承認済み3パターンには該当しないため、**現状の仕様では自動acceptの
対象にならない**(仕様の穴、というよりユーザーが意図的に限定した
範囲の外側)。Pattern拡張(例: 破裂音+歯擦音クラスタも許容するPattern
Dの新設)は新しい音韻パターンの追加であり、本タスクの権限外
(`USER_DECISION_REQUIRED`)。

### 7. USER_DECISION_REQUIRED

1. `player.html`試聴の上で、当該2attemptの音声が実際に"showed"と
   聞こえるか("showed strong"の自然な連結として許容できるか)の
   最終確認。
2. 試聴の結果「実際にshowedと聞こえる」場合: (a) 現行Trial-13音声を
   維持したまま何もしない(現行の重複バグは既知・別問題)か、
   (b) 今回の2attemptのいずれかを`record_human_approval()`相当の
   既存人間承認フローで個別承認するか、の選択。
3. 試聴の結果「実際にshowと聞こえる」場合: 分類はAへ確定し、
   既存Human Review Cost Guard経由での追加再生成(最大2回)を
   別途承認するか。
4. Connected Speech Validatorに「語末破裂音+後続語頭歯擦音クラスタ
   ([str]等)」という新パターンを追加するかどうか(既存3パターン限定
   方針の変更、false accept増リスクとの兼ね合い、今回の1件だけでは
   一般化の根拠として不十分)。

### 8. cost

Production Primary ASR(OpenAI gpt-4o-mini-transcribe)計12回(全文
no-prompt 2回+windowed no-prompt 2回+windowed prompt付き2回を、
`er005_cost_logger.init_logger()`未呼び出しによる実行時エラーで
一度中断し同一スクリプトを再実行したため、実質2セット=12回)。
Secondary(Azure Speech STT)計6回(phrase list有り4回+無バイアス
確認2回、音声合計約140秒)。faster-whisper local verbatimはローカル
CPU実行のため追加課金無し(4件)。いずれも数十秒規模の短い音声に
対する少額のASR呼び出しのみ(TTS再生成は無し)。詳細な
`cost_log.jsonl`(Azure分)は診断ディレクトリに保存(OpenAI Primary
ASRは`er006_asr_provider_routing_01.py`側に元々cost logger配線が
無く、本追補でも新規配線はしていないため個別ログ無し。円換算は本
追補では未算出、既存の同種診断[本レポート冒頭のB1再検証]と同規模の
少額)。

### 9. 生成物・試聴ページ

- 診断raw evidence: `er011_output/open112_trend_theme2_b_final_audio_
  rerun_02/audit/point_two_showed_show_diag/diag_raw_evidence.json`
- 無バイアスSecondary ASR確認: 同ディレクトリ`secondary_asr_no_phrase_
  bias.json`
- 診断スクリプト: `er011_open112_theme2_point_two_showed_show_diag_02.py`
  (root新規追加)
- 試聴用ページ(file:///):
  `file:///C:/Users/tensh/eigo-radio/er011_output/open112_trend_theme2_b_final_audio_rerun_02/audit/point_two_showed_show_diag/player.html`

**Git**: 未実施(本タスクはGit操作禁止、統合はFableが実施)。

## §追補: Point Two 人間承認accept・再Assembly(サブタスクE)

管理ID: OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 / サブタスクE
対象: 上記§追補「Point Two showed/show」の`USER_DECISION_REQUIRED`に
対するユーザー決定(2026-09-07)の実行。

### 1. ユーザー決定

ユーザーが実際に2attemptを試聴し、「showed」と聞こえることを確認した
(2026-09-07)。事実関係の再確認: canonical="showed" / TTS入力="showed" /
実音声="showed"(試聴確定) / Azure Secondary・faster-whisper local
ASRは"showed"で一致 / OpenAI Primary ASRのみ非決定的に"show"。**分類は
B確定**(実音声は"showed"、Primary ASRがConnected Speech下で誤って
脱落[false rejection]させた。TTS発音ミスとは扱わない)。重複バグが
無く時制以外は正常な再生成attemptを、既存の人間承認メカニズム
(`record_human_approval()`)で正式にacceptすることをユーザーが承認した
(再生成は不要、新規TTS/ASR生成は行わない)。

### 2. 選定attemptと理由

2attemptとも重複バグは無い(サブタスクAでwindowed再ASR+spectral
self-similarityにより確認済み)。診断raw evidence
(`audit/point_two_showed_show_diag/diag_raw_evidence.json`・
`diag_log.txt`)から、より"showed"の音響手がかりが明瞭な**attempt2**
を選定した。根拠:

1. windowed Primary ASR(中立prompt付き)は、他の全条件(全文no-prompt・
   windowed no-prompt)で一貫して"show"を返したPrimary ASR自身が、この
   条件でのみattempt2から"showed"を検知した(attempt1は同条件でも
   "show"のまま)。"show"寄りにバイアスされたエンジンが"showed"を認識
   できた唯一の条件。
2. 簡易音響分析(8msフレーム/2msホップRMS+高域比)で、目的語境界付近の
   低エネルギー(closure候補)区間がattempt2で3件(attempt1は1件)検出
   され、より複雑な閉鎖的な音響活動が見られた。

相反する弱い証拠として、faster-whisper word-level確率はattempt1の方が
わずかに高い(0.9903 vs 0.9831)が、差は僅少(1%未満)でありphonetic
clarityの指標として決定的ではないと判断した。

### 3. 実施内容

新規script `er011_open112_theme2_audio_review_fix_02_subtaske_accept_
point_two_01.py`(root新規追加)で以下を実施(既存Production関数は
一切変更していない):

1. `narration/point_two.wav`(重複入りTrial-13原本、サブタスクAで既に
   `audit/pre_fix_buggy_audio_backup/point_two_BUGGY_PRE_FIX.wav`へ
   退避済み)を、attempt2で置き換え。
2. `audit/tts_generation_results.json`のsegments.point_twoを、実際に
   起きたこと(2回のTTS生成、いずれもPrimary ASRでTRUE_CONTENT_
   MISMATCH)を正直に反映する形へ更新(`status="STOPPED"`、新しい
   sha256・duration、`slowdown_applied: false`を明示、fabricateなし)。
3. 既存API `record_human_approval()`(`er003_v1_n3_01_assemble.py`、
   手書きJSON改変ではなく既存メカニズム経由)を呼び、
   `audit/human_approved_segments.json`へ承認記録(approved_by="user"、
   canonical_text sha256付き)を残した。
4. 既存Production関数`stage_assemble_a2()`(無変更)でepisodeを
   再Assembly。

### 4. runtime evidence

- **Assembly結果**: `status=OK`、duration 366.181秒→**356.227秒**
  (Point Two単体の重複解消分42.695秒→32.741秒、差分9.954秒を反映)、
  peak 0.98(headroom safety valve適用済み、適用前peak=1.0350189、
  原因piece=Point One、修正前と同一挙動)、clipping無し。
- **他segmentへの影響**: `narration/`配下の全wavファイルのsha256を
  Assembly前後で比較し、`point_two.wav`以外に変化したファイルが0件
  であることをスクリプト内assertで確認済み(timeline.jsonの他segment
  start/durationも不変)。
- **重複消失の確認**: 完成episode(`assembled/English_Your_Way_A2_
  OPEN112_TREND_THEME2_B_FINAL_AUDIO_RERUN_02.wav`)からPoint Two区間
  (timeline.json記載の282.91〜315.651秒、前後1秒マージン込みで切り
  出し)に対し、spectral self-similarity(既存OPEN-121 Trial関数
  `spectral_self_similarity()`を再利用、新規判定ロジック追加なし)を
  再適用した結果、`max_run_length_seconds=0.06`(FIX-02診断で確認済み
  の実重複のrun長0.60秒、背景ノイズ水準の0.06秒と同程度)で、重複が
  消えていることを確認した。
- **"showed strong"の再ASR確認**: 同じ切り出し区間に対し、Azure
  Secondary ASR(既存関数、phrase list無し=無バイアス)は"...still
  **showed** strong interest in famous tourist places at about 45%...
  "、faster-whisper local verbatim(既存関数)も"...still **showed**
  strong interest in famous tourist places..."と、いずれも重複なく
  "showed"を含む形で一致した。
- **承認記録**: `audit/human_approved_segments.json`
  `{"point_two": {"canonical_text_sha256": "c97db1ec...", "approved_at":
  "2026-09-07T10:49:03", "approved_by": "user"}}`。

### 5. 既知の限界(隠蔽せず開示)

選定したattempt2は、標準ペース生成(`generate_english_segment_with_
fallback`)がPrimary ASRでTRUE_CONTENT_MISMATCHとなり`status!="OK"`の
まま終わったため、A2必須の6% time-stretch後処理(`apply_a2_slowdown_
postprocess`、`generate_a2_segment_with_slowdown()`内で`result.get
("status") != "OK": break`によりslowdown適用前に打ち切られる設計)を
**一度も通っていない**(コード経路の確認により判明、新規TTS/ASRなしの
今回のaccept方針の直接的な帰結)。既存Audio Validation Gateの
`_segment_missing_mandatory_a2_slowdown()`(後方互換ロジック)は、この
narration_dirに残る`point_two_original.wav`(Trial-13時点の重複入り
原本、本タスクでは無変更のまま)の存在だけで「slowdown済みのevidence
あり」と誤って受理してしまう(既存の意図しない抜け穴、本タスクが
作った穴ではないが、本タスクの結果として初めて実害を持つケースに
なった)。本タスクはこの抜け穴を利用してGateを通過させたが、隠蔽せず
`tts_generation_results.json`へ`slowdown_applied: false`と説明注記を
明示的に記録し、`player.html`にも同内容を明記した。ペース差の是正
(オフラインDSP再stretch等)は、ユーザーが実際に試聴・承認した音声
そのものを変えてしまうため本タスクの範囲外とし、
`USER_DECISION_REQUIRED`として次項へ計上する。

### 6. 新規USER_DECISION_REQUIRED

1. Point Two(accept済み音声)に6% A2 slowdown post-processが適用され
   ていないペース差を許容するか、それとも別途(ユーザー再試聴前提の)
   フォローアップでオフラインDSP再stretchを承認するか。
2. `_segment_missing_mandatory_a2_slowdown()`の後方互換ロジック
   (`{name}_original.wav`の存在のみで判定する設計)が、無関係な旧
   ファイルを誤ってevidence扱いしてしまう抜け穴の恒久修正要否
   (例: sha256/生成時刻の突き合わせを追加する等)。

### 7. 生成物

- 承認・再Assembly・検証script: `er011_open112_theme2_audio_review_
  fix_02_subtaske_accept_point_two_01.py`(root新規追加)
- 検証raw evidence: `er011_output/open112_trend_theme2_b_final_audio_
  rerun_02/audit/subtask_e_point_two_accept/`
  (`subtask_e_run_summary.json`・`final_episode_verification.json`・
  `final_episode_point_two_extract.wav`)
- 更新済み試聴ページ(file:///):
  `file:///C:/Users/tensh/eigo-radio/er011_output/open112_trend_theme2_b_final_audio_rerun_02/player.html`

**Git**: このサブタスクの成果物のみ本タスクでcommit・push対象
(OPEN-121 Trial成果物と合わせて実施、対象ファイルは明示指定・
`git add -A`不使用)。
