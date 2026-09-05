# OPEN-112-TREND-THEME2-B-A2-B1-FULL-AUDIO-TRIAL-13

管理ID: OPEN-112-TREND-THEME2-B-A2-B1-FULL-AUDIO-TRIAL-13
作成日: 2026-09-05
Status: **USER_DECISION_REQUIRED**(B1: Audio Validation Gateにより正常にSTOP。
A2: Assembly段階の出力安全装置(clipping防止assert)により未処理の例外でSTOP。
どちらもoverride・fallback追加・手動unblockは一切行っていない)

Sonnet実行: 3回(**ユーザーが上限超過を明示承認した例外**。これが最後)。
1回目はB1 TTS途中(point_two_heading完了直後)でユーザーの誤操作により停止
(内容面の問題ではない)。2回目で状態確認の上、既存Production経路のみで
再開・完走を試み、B1のAudio Validation Gate停止・A2のclipping assert停止
まで到達した(§1〜15、下記2回目時点の記録)。3回目(§16)は45分待機の上で
状態確認からやり直し、2回目が起動したbackground processの完走を見届けた上で、
Assembly専用モードにより最終状態を再確認・確定した。

---

## 1. 経緯・状態確認結果(Sonnet 2回目・再開時)

再開前に以下を確認した。

- `er011_output/open112_trend_theme2_b_full_audio_trial_13/` 配下: Support stage
  (b1b/a2とも parts.json・support_texts.json・key_phrases一式・
  support_fact_check.json)は1回目で完了済み。B1 narration:
  topic_intro/preview/comment_1-4/point_one_heading/point_two_heading の
  8 segmentが1回目でTTS+ASR verified=true・final_status=OK・attempt=1で
  RESOLVED済み(`b1b/audit/review_lock_state.json`)。A2は音声(narration)
  未着手(TTS/ASR呼び出しゼロ)。
- Gate/Lock: `b1b/audit/review_lock_state.json`・`er011_output/attempt_history.jsonl`
  とも、1回目分はすべてaction="PROCEED"・result_status="OK"のみで、
  Gate/Lock停止の記録は無かった。
- 1回目費用(実測): 約$0.095(~¥15.11、@¥159/$)。Trial-12までの累計¥68.1と
  合わせて再開時点の累計は約¥83.2(¥1,000上限比 約8.3%)。
- `git status --short`: 本タスクのOUT_DIR配下ファイルおよび
  `er011_output/attempt_history.jsonl`・`er006_output/master_audio_store_01/
  {manifest.json,reuse_telemetry.jsonl}`(Master Audio Store自身の実行時データ、
  設定値ではない)のみ変化。Production/SSOTコードは無変更。

### 再開方式(Trial script内のみの最小限追加)

`er006_pool_pilot_01_support.py::run_support_for_theme()`には既存出力の
再利用/skip機構が無く、無条件に再実行するとLLMでSupport文面を非決定的に
再生成してしまう(=1回目でRESOLVED済みのB1 segmentのcanonical_text_sha256を
壊すリスクがある)。そのため、Trial script (`er011_open112_trend_theme2_b_
full_audio_trial_13.py`)内だけに、両levelのSupport出力ファイルが既に
揃っていればSupport stageをskipしてAudio stageへ直接進む、という
resumeガード(`support_stage_already_done()`)を追加した。Production関数
(`sup.run_support_for_theme`/`tts_gen.generate_*_segments`/
`asm.stage_assemble_*`)自体は一切変更していない。

### 重要な判明事項: RESOLVED状態は実際には「再TTSしない」ブロックをしない

当初、既存のReview Lock機構(`er011_human_review_lock_01.py`、
`@review_lock.guarded_generate`)により、1回目でRESOLVED済み(検証PASS済み)の
segmentは2回目実行時に自動的に0 API callで再利用されると想定していたが、
実際にコードを確認・実行結果で検証した結果、これは誤りだった。

`er011_human_review_lock_01.py::check_before_generation()`のコメント
(240〜250行目)に明記されている通り、**RESOLVED状態は「監査用の記録に留め、
ブロックはしない」という既存の意図的な設計**である(A2 6%減速retryの正当な
再挑戦を誤ってブロックしないための設計)。実際にブロックされるのは
`HUMAN_REVIEW_REQUIRED`と`HUMAN_APPROVED`の2状態のみで、`RESOLVED`は
むしろ`proceed=True`を返す。

この結果、再開run実行時、1回目でRESOLVED済みだった8 segment
(topic_intro・preview・comment_1〜4・point_one_heading・point_two_heading)は、
**「再利用」ではなく「新しいTTS take」として再生成**され、独立に
ASR再検証されて再びOK(RESOLVEDのまま、ただし音声ファイルは新しいtakeに
上書き)となった。これは当初の指示「検証PASS済みsegmentの音声は再利用
(再TTSしない)」に反する結果であり、Production側の既存挙動(意図的な設計)を
正確に理解していなかったことが原因である。金額影響は軽微
(該当8 segment分のTTS+ASR再課金、下記§12参照)だが、事実として報告する。
今後、真に「再TTSしない」再開を行うには、Trial scriptまたは呼び出し側で
wavファイルの存在とReview Lockの`RESOLVED`+text hash一致を明示的に確認し、
segment単位でPython呼び出しそのものをskipする追加ロジックが必要になる
(本Trialでは未実装、Production側のReview Lock機構だけでは実現できないと
判明した)。

---

## 2. 使用したProduction経路とTrial adapterの範囲

- `er006_pool_pilot_01_support.py::run_support_for_theme()`(内部で
  `er003_v1_n3_01_scaffold_generate.py::split_article_text/run_b1_scaffold/
  run_a2_scaffold/run_key_phrases`を無変更で呼ぶ)— 1回目のみ実行、
  2回目はTrial scriptのresumeガードでskip。
- `er003_v1_n3_01_tts_generate.py::generate_b1_segments/generate_a2_segments`
  — 無変更のまま呼び出し。内部で`voice01.generate_charon_english`・
  `news_tail_fix.generate_news_narration_wide_margin`・
  `point_headings.generate`・`shared_narration.ensure_*`・
  `crosslevel_audio_02_common.generate_english_segment_with_fallback`・
  `generate_a2_segment_with_slowdown`等、既存の確立済み生成関数をそのまま使用。
- `er003_v1_n3_01_assemble.py::stage_assemble_b1/stage_assemble_a2`
  — 無変更のまま呼び出し。Audio Validation Gate/Human Review Lockは
  この内部で自動発火。
- Trial adapter(`er011_open112_trend_theme2_b_full_audio_trial_13.py`)は
  (a) Trial-12のarticle.mdをOUT_DIR配下へバイト同一でコピーする、
  (b) 上記Production関数を順に呼ぶ、(c) B1側Assembly Gate停止(RuntimeError)が
  A2側の独立実行を妨げないようtry/exceptで分離する、
  (d) 2回目のみ、Support stage出力の存在確認によるresume skip、の4点のみを
  行い、Validator・閾値・retry上限・pause値等は一切変更していない。

---

## 3. B1: Preview/Key Phrase/Comment全文

**Preview**:
> This episode looks at how young people in Japan think about travel, including
> freedom, personal interests, and time. But the label "young Japanese travelers"
> may hide important differences between groups. Listen to see what the surveys
> show about these different preferences and what "slow travel" means in this
> story. By the end, you will have a clearer view of what young travelers may
> want from a trip.

**Comment 1**: Listen for the difference between how long people imagine
traveling and how long their planned trips are.

**Comment 2**: So far, the key point is that people may imagine longer trips,
but their actual plans are still short. So, are travel habits really changing,
or are only people's attitudes changing?

**Comment 3**: The main idea is simple: people may want more freedom in how
they travel, but their actual plans are still short. This shows a gap between
changing attitudes and current travel schedules. Next, we will look more
closely at two sides of this story.

**Comment 4**: Together, these points show that young travelers do not all
want the same kind of trip. For some, control over time matters, while others
may still want to visit famous sights. Now, let's bring these ideas together
in the closing summary.

**Key Phrase(5件、英語表現 / 日本語訳)**:
1. story with two different speeds / 2つの異なる速さで進む状況
2. room for one's own pace / 自分のペースで過ごせる余地
3. median of about two nights / 中央値は約2泊
4. point to / ～を示す、～を指し示す
5. emerging preference / 現れつつある好み・傾向

**Full Story Part1/Part2・Point One/Two本文・In One Line**は§8の記事本文
(parts.json)と同一(Trial-12から無変更)。TTS自体は全segment
final_status=OK(下記§4)。

---

## 4. B1: segment別TTS/ASR結果

`b1b/audit/review_lock_state.json`より(全22 lock entry)。

| segment | final_status | cumulative TTS attempts | cumulative ASR calls | 備考 |
|---|---|---|---|---|
| topic_intro | OK | 2 | 2 | 1回目attempt=1でRESOLVED後、再開runで**意図せず再TTS**(§1参照)、2回目もOK |
| preview | OK | 2 | 2 | 同上 |
| comment_1〜4 | OK(各) | 2 | 2 | 同上(4 segmentとも) |
| point_one_heading | OK | 2 | 2 | 同上 |
| point_two_heading | OK | 2 | 2 | 同上 |
| full_story_part1 | OK | 1 | 1 | 再開runで新規(1回のみ、再利用の意味はない=元々未着手) |
| full_story_part2 | OK | 1 | 1 | 同上 |
| point_one | OK | 1 | 1 | 同上 |
| point_two | OK | 1 | 1 | 同上 |
| in_one_line | OK | 1 | 1 | 同上 |
| kp1_en | OK | 1 | 1 | 新規 |
| kp1_ja_charon | OK | 1 | 1 | 新規 |
| kp2_en | OK | 1 | 1 | 新規 |
| kp2_ja_charon | OK | 1 | 1 | 新規 |
| kp3_en | OK | 1 | 1 | 新規 |
| **kp3_ja_charon** | **STOPPED** | 3 | 3 | 標準経路2回+fallback経路1回(計3回)。ASR分類は毎回`TRUE_CONTENT_MISMATCH`(canonical「中央値は約2泊」に対し、標準経路2回とも「中央値は約二泊。」、fallback1回は「中央地は約二泊。」とASR認識された。内容自体は一致しているが、算用数字/漢数字の表記ゆれ・「値」/「地」の同音混同をValidatorの数字保護ゲートが数字消失相当として誤判定したもの。**2026-09-06訂正(OPEN-112-TREND-THEME2-RECORD-CONSOLIDATION-18)**: 旧記載「中央値は約回数泊。」は誤記。証跡: `b1b/audit/tts_generation_results.json`のkey_phrases."3".japanese、Opus診断-15で確認) |
| **kp4_en** | **STOPPED** | 4 | 4 | Minimal instruction 2回+English language lock 2回(計4回)。ASR分類は毎回`TRUE_CONTENT_MISMATCH`("point to"の期待に対し"Point two."と誤読、Point見出しとの混同と推定) |
| **kp4_ja** | **STOPPED** | 0(TTS呼び出し前に停止) | 0 | canonical gloss「～を示す、～を指し示す」に未発話のplaceholder記号「～」が残存しているとして、TTS呼び出し前のplaceholder検出でSTOPPED(kp4_enのSTOPPEDとは独立の原因であり、kp4_enの結果を待って未着手になったものではない)。**2026-09-06訂正(OPEN-112-TREND-THEME2-RECORD-CONSOLIDATION-18)**: 旧記載「(未実行)/kp4_enがSTOPPEDのため生成自体に到達せず」は誤り。`review_lock_state.json`にkp4_ja(_charon)のentryが存在しないのはTTS/ASR呼び出し自体が発生しなかったためで、原因はplaceholder検出である。証跡: `b1b/audit/tts_generation_results.json`のkey_phrases."4".japanese(`reason: "canonical_textに未発話のplaceholder記号が残っています: ['～']"`)、Opus診断-15で確認 |
| kp5_en | OK | 1 | 1 | 新規 |
| kp5_ja_charon | OK | 1 | 1 | 新規 |

`b1b/run_summary_tts.json`のsegment_status/key_phrase_statusも上記と一致。

kp4_en Master Audio Store内部(`shared_narration.ensure_key_phrase_english_
component`)では、raw usage log上さらに細かい内部試行(SUCCESS 1回→
`INVALID_AUDIO`(parse error)1回→SUCCESS 3回、計5回のgemini_batch呼び出し)が
記録されている。これはKey Phrase英語Component専用の既存4段階retry構成
(独立したProduction機構、review_lock側のcumulative_tts_attemptsとは別会計)で、
本Trialからは一切override・fallback追加をしていない。

---

## 5. B1: Assembly結果(Gate停止)

`stage_assemble_b1(theme)`は以下の`RuntimeError`で停止した(Trial scriptの
try/exceptがそのままGATE_BLOCKEDとして捕捉、override・追加fallback・
human_approved_segments.json等による手動unblockは一切行っていない)。

```
EPISODE_BLOCKED_BY_AUDIO_VALIDATION: B1のepisode assemblyを中止しました。
以下のsegmentが今回のrunでVALIDATED/HUMAN_APPROVED状態ではありません、
または必須post-processのevidenceがありません:
['kp3_japanese=STOPPED', 'kp4_english=STOPPED', 'kp4_japanese=STOPPED']。
未検証・stale・STOPPEDの音声、または6% slowdown等の必須post-processを
経ていない音声をそのまま完成扱いにすることは許可されていません
(ER-008-AUDIO-VALIDATION-GATE-AND-EVIDENCE-MAJOR-AUDIT-05、
ER-008-N8-PRODUCTION-WIRING-AND-FOLLOWUP-19)。該当segmentを再生成するか、
post-processを適用してから再度assemblyを実行してください。
```

このRuntimeErrorは`load_b1_sources`/`apply_b1_gain`段階(音声ミックス処理に
入る前のsegment検証)で発生しており、`b1b/assembled/`・`b1b/audit/
gain_report.json`・`b1b/audit/timeline.json`は一切生成されていない
(空ディレクトリのみ存在)。**B1の完成音声は存在しない。**

---

## 6. A2: Preview/Key Phrase/Comment×4全文・Reading Resolver発火箇所

**Preview(日本語)**:
> 日本の若い世代には、旅先で自分らしく過ごしたいという思いが見られます。
> いくつかの調査を通して、旅行の楽しみ方がどう変わっているのかを考えます。

**Comment 1**: 若い人たちが求める旅行のペースと、実際に考えている旅行の
長さの関係に注目してください。

**Comment 2**: 前半では、ゆっくり自分のペースで旅をしたい人がいても、
長い休みを想像したときの旅行は約1週間でした。では、実際に旅行を計画
している人の滞在日数は、どのくらいなのでしょうか。

**Comment 3**: ここまでの話から、若い人の間では、自分のペースで旅行
したい気持ちが見えます。ただ、実際に考えられている旅行は、まだ短い
ものが多く、ゆっくりした旅行が長い滞在を意味するとは限りません。
これからは、ゆっくり旅行することの意味と、同じ年代でも旅行の目的が
違うことに注目します。

**Comment 4**: ここまで見てきたのは、若い旅行者の旅の楽しみ方は一つ
ではない、ということです。自分で時間を使いたい人もいれば、有名な
場所や食を楽しみたい人もいて、同じ年代でも求めるものは違います。
それでは、この話のポイントを英語でまとめて聞いてみましょう。

**Key Phrase(5件、英語表現 / 日本語訳)**:
1. at one's own pace / 自分のペースで
2. median / 中央値
3. room to choose / 選べる余地・自由
4. not fully match / 完全には一致しない
5. month off / 1か月丸ごとの休み

**A2 japanese_title**: 「ゆっくりした旅」を求める若い世代、旅の計画はまだ短い
(Trial script実行時にProductionの`tts_gen.JAPANESE_TITLES`辞書へ1エントリ
追記して使用、既存パターン踏襲、production側ファイル自体は無変更)。

**A2 Reading Resolver発火箇所**: `review_lock_state.json`の全24 segment
(`reading_resolver_info`フィールド)を確認したところ、**全segmentでnull
(発火なし)**。すべてのA2日本語/英語segmentがattempt 1回でASR一致
(`EXACT_MATCH`/`NORMALIZED_MATCH`/`PHONETIC_MATCH`)し、Reading Resolver
(数字・分数の読み替え処理)による訂正介入が必要になったケースは無かった。

---

## 7. A2: segment別結果

`a2/audit/review_lock_state.json`(全24 entry)より、**全segment
final_status=OK・cumulative_tts_attempts=1・cumulative_asr_calls=1**
(review lock会計上は初回で成功、リトライ0回)。

- topic_intro, japanese_title, preview, comment_1〜4, point_one_heading,
  point_two_heading, full_story_part1, full_story_part2, point_one,
  point_two, in_one_line, kp1_en, meaning_1, kp2_en, meaning_2, kp3_en,
  meaning_3, kp4_en, meaning_4, kp5_en, meaning_5 — 全24 segmentとも`OK`。

ただしMaster Audio Store内部(Key Phrase英語Component生成、review lockとは
別会計の既存retry機構)では、raw usage log上以下の内部再試行が記録されている
(いずれも最終的にSUCCESS、Production既存のfallback範囲内、本Trialからの
override・追加fallbackは無し):
- `kp1_english`: 1回目`TIMEOUT`(600秒)→2回目`SUCCESS`
- (kp4_englishはB1側で既に生成済みのMaster Audio Store共有音声を
  A2でも再利用、A2側では新規1回のみ`SUCCESS`)

`a2/run_summary_tts.json`のsegment_status/key_phrase_statusも全て`OK`と一致。

---

## 8. A2: Assembly結果(未処理の例外でクラッシュ)

`stage_assemble_a2(theme)`は、全24 segmentの検証をパスし、
`load_a2_sources`→`apply_a2_gain`→`build_a2_timeline`→
`assemble_with_timeline`まで正常に完了した後、最終的な音声書き出し
(`common.write_wav_float`、`er002_common.py`414行目の既存クリッピング
防止安全装置)で以下の`AssertionError`を発生させ、**Trial scriptの
except節(`except RuntimeError`)では捕捉されない未処理の例外としてscript
全体がクラッシュした**:

```
AssertionError: 出力にクリッピングの恐れがあります(peak=1.0350188975890593)
  at er002_common.py:414 write_wav_float()
  呼び出し元: er003_v1_n3_01_assemble.py:744 stage_assemble_a2()
```

このため`a2/assembled/`・`a2/audit/gain_report.json`・
`a2/audit/timeline.json`・`run_summary_assemble.json`は一切生成されて
いない(空ディレクトリのみ存在)。**A2の完成音声も存在しない。**

これは`er011_human_review_lock_01.py`が扱うHuman Review
Lock/Audio Validation Gate(D4で言及されている「Gate/Lock」)とは別種の、
`er002_common.py::write_wav_float()`に既存する出力クリッピング防止の
安全装置(assert)である。全segmentのTTS/ASRは個別に検証PASSしているが、
それらをmix/gain調整した最終ミックスのpeakが1.0を超えたため、Production
自身がこの安全装置により出力を拒否した。この安全装置(Production既存の
ものであり、本Trialが新規に追加したものではない)を回避・無効化・
迂回する対応(例: 独自の正規化処理を追加する、閾値を緩める等)は
一切行っていない。峰値超過の原因(どのgain/どのsegmentの組み合わせが
1.0を超えたか)についての深掘りデバッグも、Production側のgain/mix計算
コードの変更を要する可能性が高いため実施していない
(Sonnet実行2回目=本管理IDの最後の1回のため、追加調査・再試行は行わず
ここでSTOPし、ユーザー判断を仰ぐ)。

なお、このミックス計算は全入力segment音声・gain設定が固定されている限り
決定論的であり、再実行しても同じpeak値・同じAssertionErrorになると
考えられる(Production側のgain/mix計算コードを変更しない限り解消しない
可能性が高い)。

---

## 9. Cross-level仕様準拠確認

B1・A2ともAssemblyが完了しなかったため、Pause 0.8秒/0.7秒・Outro減衰・
音量調整(RMS基準)等、**Assembly段階で適用される仕様の実際の適用結果は
確認できない**(`timeline.json`/`gain_report.json`が生成されていないため)。

確認できたのは以下(TTS/ASR段階、CURRENT_SPEC.mdと照合):
- **Key Phrase発音品質3条件**(`CURRENT_SPEC.md:157`): 個別単語パッチではなく
  既存のcommon promptで生成(無変更)。機械的にはASR classification
  (EXACT_MATCH/NORMALIZED_MATCH/PHONETIC_MATCH)でPASSした10件(A2は5件×2
  +B1は3件×2、B1のkp3_ja/kp4_enは未PASS)を確認。主観的音声品質は
  ユーザー試聴が必要(音声ファイル自体が完成していないため試聴不可)。
- **A2英語ナレーション約135 WPM目安 + 6%減速post-process**
  (`CURRENT_SPEC.md:89`、`A2_SLOWDOWN_TARGET_SEGMENTS`定数): A2の
  point_one_heading/point_two_heading/full_story_part1/2/point_one/
  point_two/in_one_lineは`generate_a2_segment_with_slowdown`
  経由で生成され、全segment final_status=OK(post-process後の再ASR検証も
  含めて合格、`apply_a2_slowdown_postprocess`のロジックにより、
  post-process後不一致ならSTOPPEDになる設計のため、OKである以上6%
  time-stretchは適用済みと判断できる)。
- **B1 Navigator/Support(Charon)音声**(`CURRENT_SPEC.md:136`):
  topic_intro/preview/comment_1〜4/kp日本語meaning等はCharon音声で生成
  (無変更の`voice01.generate_charon_english`/
  `generate_charon_japanese_with_reading_safety`)。
- **A2 Key Phrase pause(番号→phrase間、+0.2秒)**(`CURRENT_SPEC.md:265`)・
  **ポーズ0.7秒/0.8秒**(`CURRENT_SPEC.md:159-163`)・**Outro音量**
  (`CURRENT_SPEC.md:165`): いずれも`stage_assemble_b1/a2`内部
  (`build_b1_timeline`/`build_a2_timeline`等)で適用される仕様であり、
  両levelともAssembly未完了のため**適用結果を確認できない**。

**既存`player_final.html`形式の生成**: Assemblyが完了していないため、
完成音声ファイルが存在せず、player生成は未実施。

---

## 10. Gate/Lock停止の詳細(該当segment・原文・ASR結果・attempt履歴)

### B1 kp3_ja_charon(STOPPED)
- 原文(日本語gloss): 「中央値は約2泊」
- canonical_text_sha256: `3b8c5fd5730fb06abca275715810a64287cd33a5239c0a2b72011cb2ecebd5eb`
- attempt 1(標準経路): ASR文字起こし「中央値は約二泊。」、`audio_classification=TRUE_CONTENT_MISMATCH`、verified=false
- attempt 2(標準経路): ASR文字起こし「中央値は約二泊。」(同様)、`audio_classification=TRUE_CONTENT_MISMATCH`、verified=false
- attempt 3(fallback経路): ASR文字起こし「中央地は約二泊。」、`audio_classification=TRUE_CONTENT_MISMATCH`、verified=false
- **2026-09-06訂正(OPEN-112-TREND-THEME2-RECORD-CONSOLIDATION-18)**: 旧版は3回とも「中央値は約回数泊。」と記載していたが誤り。正しくは上記の通り(標準経路2回は「中央値は約二泊。」、fallback経路1回は「中央地は約二泊。」)。証跡: `b1b/audit/tts_generation_results.json`のkey_phrases."3".japanese。
- 標準経路2回+fallback経路1回(計3回)で`STOPPED`→`HUMAN_REVIEW_REQUIRED`へ遷移。
  budget_guard_triggered=false(累積上限には未到達、既定retry上限(3回)を
  使い切っての正常なSTOP)。

### B1 kp4_en(STOPPED)
- 原文(英語used_form): "point to"
- canonical_text_sha256: `2f2b81e22d39ecfa8a97dfb491282e849632cc41c4b24c993065681b03120416`
- attempt 1: ASR文字起こし"Point two."、`audio_classification=TRUE_CONTENT_MISMATCH`、verified=false
- attempt 2: ASR文字起こし"Point two."(同様)、`audio_classification=TRUE_CONTENT_MISMATCH`、verified=false
- Minimal instruction 2回+English language lock 2回(計4回)で`STOPPED`→
  `HUMAN_REVIEW_REQUIRED`へ遷移。budget_guard_triggered=false。
- kp4_ja(日本語meaning「～を示す、～を指し示す」)は、canonical gloss内に
  未発話のplaceholder記号「～」が残存しているとして、TTS呼び出し前の
  placeholder検出で独立にSTOPPEDした(kp4_enのSTOPPEDとは別原因であり、
  「kp4_enがSTOPPEDだったため未着手」ではない)。**2026-09-06訂正
  (OPEN-112-TREND-THEME2-RECORD-CONSOLIDATION-18)**: 旧版の「kp4_enが
  STOPPEDのため生成自体に到達していない」という記載は誤り。証跡:
  `b1b/audit/tts_generation_results.json`のkey_phrases."4".japanese
  (`reason: "canonical_textに未発話のplaceholder記号が残っています:
  ['～']"`)。したがってB1側のSTOPPED件数は、TTS/ASR段階でのkp3_ja_charon・
  kp4_enに加え、TTS呼び出し前段階のkp4_jaを合わせて**計3件**である
  (§5のRuntimeErrorメッセージが元々列挙していた
  `['kp3_japanese=STOPPED', 'kp4_english=STOPPED',
  'kp4_japanese=STOPPED']`という3件と整合)。

いずれもD4に従い、override・fallback追加・retry上限緩和・
`human_approved_segments.json`等による手動unblockは一切行っていない
(既定retryが上限まで発火した回数をそのまま記録した)。

### A2側のGate/Lock停止
A2はTTS/ASR段階でHuman Review Lock相当の停止は無し(全24 segment OK)。
ただしAssembly段階で§8記載の`write_wav_float`クリッピング防止assertが
発火し、未処理の例外としてscript全体を停止させた(D4が定義する
「Audio Validation Gate/Human Review Lock」とは異なる種類の、既存の
出力安全装置)。

---

## 11. Cost Trace(1回目/2回目/累計、¥1,000上限との比較)

単価根拠: `er005_output/cost_baseline_01/pricing_snapshot.json`
(gemini_batch/openai_asrはraw usage logのofficial応答値をそのまま使用。
gpt-5.6-luna(support stage)とopenai_asrの一部エントリはtoken数×単価
(gpt-5.6-luna: in$0.20/cached$0.02/out$1.20 per 1M tokens、openai_asr:
in$1.25/out$5.00 per 1M tokens)で算出。azure-speech-stt 1件は
$1.00/audio hour×実測秒数で算出)。円換算はTrial-12踏襲の@¥159/$を使用。

| stage | 呼び出し数(entries) | cost (USD) | cost (円換算) |
|---|---|---|---|
| support_b1(2回目でskip、1回目分のみ) | 12 | $0.04316 | ~¥6.86 |
| support_a2(同上) | 9 | $0.02518 | ~¥4.00 |
| tts_b1(1回目分+再開分、KP内部retry・意図しない再TTS含む) | 73 | $0.11934 | ~¥18.98 |
| tts_a2(全新規、KP内部timeout retry含む) | 56 | $0.09798 | ~¥15.58 |
| **Trial-13合計(1回目+2回目)** | **150** | **$0.28566** | **~¥45.42** |
| Trial-12までの累計(既報告値) | - | $0.4283 | ~¥68.1 |
| **Theme2 累計(Trial-12 + Trial-13)** | - | **$0.71396** | **~¥113.52** |

**¥1,000上限比 約11.35%**。上限内。想定外の追加試行(意図しない8 segment
再TTS、§1参照)を含めても上限には全く達していない。

---

## 12. Production変更なし確認

- 変更したProductionコード: **無し**。
- 新規作成したのはTrial script(`er011_open112_trend_theme2_b_full_audio_
  trial_13.py`)のみで、Production関数(`er006_pool_pilot_01_support.py`・
  `er003_v1_n3_01_scaffold_generate.py`・`er003_v1_n3_01_tts_generate.py`・
  `er003_v1_n3_01_assemble.py`・`er002_common.py`・`er011_human_review_
  lock_01.py`等)は一切変更していない。
- `git status --short`で確認した差分は、本タスクの`er011_output/
  open112_trend_theme2_b_full_audio_trial_13/`配下(新規)・
  `er011_output/attempt_history.jsonl`(既存の追記型ログへの追記)・
  `er006_output/master_audio_store_01/{manifest.json,reuse_telemetry.jsonl}`
  (Master Audio Store自身の実行時データ、Key Phrase Component等の
  共有音声キャッシュへの追記であり、設定値・閾値の変更ではない)のみ。
  その他の未追跡ファイルは全て本タスク以前から存在する無関係な既存差分
  であり、一切編集・stageしていない。
- Topic Master・SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)
  への変更: 無し。
- Git操作(commit/push): 無し。
- 他Agent起動: 無し。
- 音声ファイルのSendUserFile等での送付: 無し(そもそも本Trialでは
  B1/A2とも完成音声ファイルが生成されなかったため、送付するものが無い)。

---

## 13. STOP条件該当有無

- **D4(Gate/Lock停止時のoverride禁止)**: 該当。B1はAudio Validation Gate
  (`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`)により正しく停止。override・
  fallback追加・retry上限緩和・手動unblockは一切行っていない。
- **D4類似の別種安全装置**: 該当。A2は`write_wav_float`のクリッピング
  防止assertにより停止(§8)。同じ原則(既存安全装置の回避禁止)を適用し、
  回避・無効化を一切行っていない。
- **D6(¥1,000上限)**: 非該当。累計約¥113.52(約11.35%)、上限に対し
  十分な余裕あり。
- **「想定外の再試行が必要」時のSTOP**: 該当。A2のAssertionErrorは
  Trial scriptの`except RuntimeError`で捕捉されない未処理の例外であり、
  想定していなかった失敗モードだった。これ以上の追加調査・再試行は
  Sonnet実行2回目(本管理IDの最後の1回)のため行わず、ここでSTOPして
  ユーザー判断を仰ぐ。

---

## 14. ユーザーが判断すべき事項

1. **B1 Key Phrase 3(日本語meaning)・Key Phrase 4(英語"point to"・
   日本語meaning)の音声化失敗(計3件)**: kp3_ja_charonはASRが一貫して
   「中央値は約二泊。」(標準経路2回)/「中央地は約二泊。」(fallback1回)
   という表記ゆれ・同音混同を`TRUE_CONTENT_MISMATCH`として誤判定
   (§10訂正参照)。kp4_enはASRが一貫して"Point two."(canonical"point to"
   との混同)を検出した。kp4_jaはTTS呼び出し前のplaceholder記号「～」
   検出で独立にSTOPPED(§10訂正参照)。TTS側の読み違い傾向(特にkp4_enの
   "point to"が"Point Two"見出しと混同されている可能性)・Validator側の
   数字保護ゲートの表記ゆれ誤判定・選定Promptのplaceholder規約不足に
   対し、(a) このまま`HUMAN_REVIEW_REQUIRED`状態で保留するか、(b) 人間
   承認による`REGENERATE_APPROVED`を明示的に付与して再試行するか、
   (c) 該当Key Phraseの表現自体(used_form)を見直すか、(d) Validator側
   修正候補(Opus診断-15・Trial-17で検証済み)を採用するか、方針決定が
   必要(いずれも本Trialの権限外)。
2. **A2 Assembly段階のクリッピングassert(peak=1.035)**: 全24 segmentの
   TTS/ASRは個別に成功しているにもかかわらず、最終ミックスが
   Production既存の安全装置(peak<=1.0)に抵触して書き出しを拒否された。
   これはgain/mix計算(`apply_a2_gain`/`build_a2_timeline`/
   `assemble_with_timeline`)側の調査(どのsegmentの組み合わせが
   over-driveを引き起こしたか)が必要な、Production側の潜在的な問題
   である可能性がある。本件の原因調査・対応方針(Production側の
   gain計算見直しが必要か等)はユーザー判断が必要(本Trialの権限外、
   `APPROVED_FOR_PRODUCTION`が無い限りProductionコードは変更できない)。
3. **意図しない8 segment再TTS(§1)**: 「RESOLVED状態は再TTSをブロック
   しない」という既存Production設計を踏まえ、今後同様の「途中停止からの
   再開」タスクを行う場合、Trial script側でwavファイル存在+Review Lock
   RESOLVED+text hash一致を明示的にチェックし、該当segmentの生成関数
   呼び出しそのものをskipする追加ロジックが必要になる。今回はこの
   追加ロジックを実装しなかったため、8 segment分の追加課金(軽微、
   §11参照)が発生した。この設計上の挙動(RESOLVEDが意図的に
   ブロックしない)自体は既存Production仕様であり、本タスクの範囲では
   変更していない。
4. **本管理IDのSonnet実行回数上限(2回)に到達**したため、これ以上の
   Sonnet実行による追加調査・再試行は行わない。次工程(上記1〜3への
   対応)はユーザー判断待ち。

---

## 15. 固定ブロック

- **今回Status**: USER_DECISION_REQUIRED
- **B1音声**: 未完成(Audio Validation Gateにより停止。原因:
  kp3_japanese=STOPPED, kp4_english=STOPPED, kp4_japanese=STOPPED)
- **A2音声**: 未完成(Assembly段階でAssertionError: peak=1.0350188975890593
  によりクラッシュ、write_wav_floatのクリッピング防止安全装置)
- **Gate停止**: あり(B1: Audio Validation Gate正常停止。A2: 出力
  クリッピング防止assertによる未処理例外クラッシュ)
- **累計cost**: 約$0.71396(~¥113.52、@¥159/$)。¥1,000上限比 約11.35%
- **Production変更**: 無し(§12で確認済み)
- **次工程**: ユーザー判断待ち(§14の1〜4)。本管理IDでのSonnet実行は
  2回使い切ったため、追加実行にはユーザーの新しい指示・管理IDが必要。

(注: 上記§1〜15は2回目時点の記録。3回目(§16)でユーザーが実行回数上限
超過を明示承認したため状態確認・完走確認を継続した。最終確定状態・
最終cost・最終固定ブロックは§16末尾を参照。)

---

## 16. 追記(Sonnet 3回目、ユーザーが上限超過を明示承認した例外・2026-09-06)

### 16.1 状態確認結果(45分待機後)

ユーザー決定に従い、まずBashで45分間待機してから状態確認を行った。
2回目Sonnetが起動したbackground process(PID 15772)は、待機開始時点でも
**まだ稼働中**だった(2回目セッションが終了した後もOSプロセスとしては
生き続けていた)。以後、5分以上間隔のポーリングで見守ったところ:

- B1側は§4・§5・§10に記載の通り、kp3_ja_charon(3 attempt、STOPPED)・
  kp4_en(4 attempt、STOPPED)がHuman Review Lockへ到達、他20 segmentは
  RESOLVED。この結果は本セッションのポーリングでも同一の
  `review_lock_state.json`・`attempt_history.jsonl`エントリとして
  観測・再確認した(タイムスタンプ含め完全に一致)。
- A2側はその後も進行を続け、23:41頃に全24 segment(§7記載)が
  final_status=OKでRESOLVEDし、`a2/run_summary_tts.json`・
  `a2/audit/tts_generation_results.json`が生成された。
- プロセスはA2 TTS完了直後(Assembly未着手)に自然終了していた
  (`tasklist`で確認、`audio_timing.json`/`audio_stage_summary.json`が
  一度も生成されていないことから、`stage_assemble_b1`到達前に終了したと
  判断)。異常終了(手順3の「異常終了」に該当)と判断し、既存Production
  経路のみでAssemblyまで続行する対応を行った。
- Gate/Lock: 上記2件のSTOPPED以外に新規のGate停止は無し。
  `budget_guard_triggered`はいずれもfalse。
- `git status --short`: 本タスクのOUT_DIR配下・`attempt_history.jsonl`・
  `er006_output/master_audio_store_01/*`(実行時ログ)以外の差分無し。
  Production/SSOTは無変更。

### 16.2 重要な追加事故: Assembly到達のための再実行が意図しない重複再TTSを招いた

Assemblyへ到達させるため、Trial scriptをそのまま(`main()`)再実行した
ところ、§1で既に判明していた「RESOLVED状態は再TTSをブロックしない」という
既存Production設計により、B1のtopic_intro・preview(2 attempt)・
comment_1〜4が**再び新規TTS/ASR対象として実行され直した**(意図しない
重複課金、既にRESOLVED済みの内容と同じ台本だが別takeの音声に上書きされた)。
この再実行中、システムのメモリ不足によりプロセスが強制終了された
(comment_4完了直後)。

この失敗を踏まえ、Trial script (`er011_open112_trend_theme2_b_full_audio_
trial_13.py`)に**Production関数は一切変更せず**、`generate_b1_segments`/
`generate_a2_segments`を呼ばずに`asm.stage_assemble_b1`/
`asm.stage_assemble_a2`だけを直接呼ぶ`--assemble-only`モードを追記した
(新規関数`run_assemble_only_stage()`追加、既存`run_audio_stage()`・
Production呼び出し本体は無変更)。このモードで実行した結果:

- **B1**: `EPISODE_BLOCKED_BY_AUDIO_VALIDATION`(§5と同一のRuntimeError、
  `['kp3_japanese=STOPPED', 'kp4_english=STOPPED', 'kp4_japanese=STOPPED']`)
  で正常にGATE_BLOCKED。override・fallback追加・手動unblockは一切
  行っていない。
- **A2**: §8と**完全に同一の**`AssertionError(peak=1.0350188975890593)`
  で書き出し時にクラッシュ(小数点以下まで完全一致。全24 segment音声
  データ・gain計算が決定論的であることの裏付け)。この安全装置
  (`er002_common.py::write_wav_float`)も回避・無効化していない。
  今回は`--assemble-only`モードのtry/except(`except RuntimeError`)でも
  `AssertionError`は捕捉されないため、A2側の例外はscriptを終了させたが、
  B1側は先にGATE_BLOCKEDとして捕捉済みのため実害は無い(両levelとも
  最終的に「未完成」という結論に変わりはない)。

**結論**: B1・A2とも最終状態は2回目時点の§5・§8・§10の記載から変化なし
(同一のGate停止・同一のAssertionError、既存安全装置は一切回避していない)。
追加で判明したのは、Assemblyだけを再実行する安全な方法(`--assemble-only`)
と、その手前で意図しない重複再TTSが実際に発生し得ることの実測確認。

### 16.3 追加コスト(重複再TTS分)

`raw_usage_log_trial13.jsonl`の全エントリ(165件、支払い確定分のみ)を
`pricing_snapshot.json`で再集計した結果:

| 内訳 | USD | 円換算(@¥159/$) |
|---|---|---|
| support_b1 + support_a2(1回目) | $0.06834 | ~¥10.87 |
| tts_b1 + tts_a2(2回目=PID 15772の完走分、本セッションが監視のみ) | $0.20942 | ~¥33.30 |
| tts_b1 重複再TTS分(3回目、topic_intro/preview×2/comment_1-4、システムOOM killまで) | $0.02534 | ~¥4.03 |
| **Trial-13合計(全3回)** | **$0.31116** | **~¥49.47** |
| Trial-12までの累計(既報告値) | $0.4283 | ~¥68.10 |
| **Theme2累計(Trial-12+Trial-13、全実行)** | **$0.73946** | **~¥117.57** |

**¥1,000上限比 約11.76%**。重複再TTS分(~¥4.03)を含めても上限には
全く達していない。`--assemble-only`モード自体・診断用の
`apply_a2_gain()`単体呼び出し(§16.2の原因調査、ファイル書き込み無し)は
TTS/ASR APIを一切呼ばないため追加費用ゼロ。

### 16.4 最終STOP条件・最終固定ブロック(3回目時点、確定)

- **D4(Gate/Lock停止時のoverride禁止)**: 該当。B1のAudio Validation
  Gateは3回目でも同一内容で正しく停止、override等は一切行っていない。
- **D4類似の別種安全装置**: 該当。A2のclipping assertは3回目でも
  完全に同一のpeak値で再現、回避・無効化は一切行っていない。
- **D6(¥1,000上限)**: 非該当。累計約¥117.57(約11.76%)。
- **意図しない重複再TTS(新規判明)**: 発生した。金額影響は軽微
  (~¥4.03)だが、「検証PASS済みsegmentは再利用し再TTSしない」という
  当初前提が2回目・3回目とも成立しなかった事実として記録する。

**最終Status(3回目確定)**: **USER_DECISION_REQUIRED**
(2回目時点の§15から変化なし。B1・A2とも完成音声は存在しない)

- **B1音声**: 未完成(Audio Validation Gateにより停止。原因:
  kp3_japanese=STOPPED, kp4_english=STOPPED, kp4_japanese=STOPPED。
  3回目でも同一結果を再確認)
- **A2音声**: 未完成(Assembly段階でAssertionError:
  peak=1.0350188975890593によりクラッシュ、write_wav_floatの
  クリッピング防止安全装置。3回目でも完全に同一の値で再現)
- **Gate停止**: あり(B1: Audio Validation Gate正常停止。A2: 出力
  クリッピング防止assertによる未処理例外クラッシュ)。いずれもoverride
  なし。
- **TTS方式**: Batch API(Production標準)のみ。Standardへの切り替え・
  混在は一切行っていない。
- **累計cost**: 約$0.73946(~¥117.57、@¥159/$)。¥1,000上限比 約11.76%
- **Production変更**: 無し(Trial script `er011_open112_trend_theme2_b_
  full_audio_trial_13.py`への`--assemble-only`モード追加のみ、
  Production関数は無変更)
- **次工程**: ユーザー判断待ち(§14の1〜3、および本節で判明した
  「RESOLVED状態は再TTSをブロックしない」設計への対応要否)。本管理ID
  でのSonnet実行は3回(ユーザー承認済み上限)使い切ったため、追加実行には
  ユーザーの新しい指示・管理IDが必要。
