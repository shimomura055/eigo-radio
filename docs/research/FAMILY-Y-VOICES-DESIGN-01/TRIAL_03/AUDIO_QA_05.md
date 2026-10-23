# AUDIO_QA_05: 委任_11 Std V1再生成(言い換え案B2、最大2テイク)の正式Gate結果

証跡: `er110_output/family_y_persona_trial_01/audio/it3/a2/audit/{tts_generation_results,review_lock_state}.json`、`.../it3/raw_usage_log.jsonl`、`.../it3/stop_check_fyt8_tts.json`(rc=0非停止)。言い換え=`V1_REWRITE_DIFF_02.md`。V1以外のsegmentは本文不変のため再利用(再生成0)。Gate・閾値・HR Lockは無変更。

## 実行方法の注記(テイク上限2の担保)
既存パイプラインはStd=標準2テイク+minimal_fallback1テイク(通算3)が固定。委任_11は「3テイク目禁止・fallbackに落とさない」のため、1回限りの起動script(scratchpad、1起動のみ・再起動なし)で`review_lock.PRODUCTION_MAX_TTS_ATTEMPTS`をそのprocess内だけ3->2へ**下げて**起動した(Gate・閾値・判定ロジックは無変更、上限を緩める方向の変更なし、repo内のコード変更0)。結果、標準2テイクのみでfallbackは実行されず、不一致なら`HUMAN_REVIEW_REQUIRED/STOPPED`になる。

## Standard(a2)full_story_part1(V1、Algieba)
| 試行 | 経路 | ASR(主) | Repetition QA method D' | 結果 |
|---|---|---|---|---|
| 1 | 標準 | TRANSCRIPT_STYLE_NORMALIZED_MATCH | flagged: run長0.78s、time_a 9.69s、lag 0.56s、類似度0.738 | 再試行 |
| 2 | 標準 | NORMALIZED_MATCH | flagged: run長0.60s(閾値0.6s到達)、time_a 18.01s、lag 1.95s、類似度0.763 | 上限2到達 -> **HUMAN_REVIEW_REQUIRED / STOPPED** |
- method A(n-gram)はいずれもflagなし。ASR転写は両テイクとも原稿どおり(`next morning`->`the next day`でAzure誤転写リスク回避。今回Azureの不一致判定は発生せず、D'のみが停止理由)。
- cumulative_tts_attempts=2。fallback未実行。Y style gateは未到達(Std V1がOKでないため全編通し未組立)。
- 観測: flag位置がテイクごとに移動(委任_10: 6.58s/31.5s/33.4s、今回: 9.69s/18.01s)。言い換えで語句反復を崩しても、D'の類似度0.74〜0.76(閾値0.7)が文の切れ目付近で出る=特定の語句の反復ではなく、Std Algiebaの発話リズム(短文のリズム・同じ音響パターンの繰り返し)にD'が反応している可能性(仮説、未検証)。2テイクの試行回数では再現しない。

## 案A(人間試聴承認)の材料
- 最終テイク: `er110_output/family_y_persona_trial_01/audio/it3/a2/narration/full_story_part1.wav`(attempt8=`.../narration/attempts/full_story_part1_attempt8_customa3c4625e.wav`)。1テイク目=`attempt7_customa3c4625e.wav`(0.78s、境界超過が大きい)。
- ページ上の該当パート: https://shimomura055.github.io/eigo-radio/user_test/family_y_trial_03/index.html のStandardタブ「Full Story Part 1 — 人物1【人間確認待ちのテイク】」(`audio/std_part_04.mp3`)。聴いて(1)同じ語句の二重読み・つかえ・繰り返しがないか、(2)原稿どおり読まれているかを確認。問題なければ承認(`human_approval`経路)でStd通しを組み立て可能(API 0)。
- 次の一手(いずれもFable判断): A=人間試聴承認(見込み高、API 0、即時) / B3=さらなる英文変更(見込み低: 位置がテイクごとに移動するため) / D'の偽陽性そのものの是正はOPEN-469(X/Z共有module=本委任スコープ外)。
