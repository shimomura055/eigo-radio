# EDITORIAL-B-FAMILY-VOICES-TRIAL-08-AUDIO-FIRST-PERSON-CHECK-01

Lane B / Voices-Perspective。Trial音声化(ユーザー承認2026-09-07)。
Production採用ではない。5区切り骨格・Contract・一人称・Editor例外・
Leakage基準は引き続き`APPROVED_FOR_PRODUCTION`にしていない。

スクリプト: `er012_editorial_b_voices_trial_08_audio.py`(root)
成果物: `er012_output/editorial_b_voices_trial_08_audio/`
試聴ページ: `er012_output/editorial_b_voices_trial_08_audio/player.html`
(file:///形式、音声+完全スクリプト同一ページ)

## 0. Closeout(音声化の完了状況)

- **版1(一人称、P1): 完成。** 5:58→実測4:58.7(298.665秒)、peak=0.928、
  clipping無し、headroom safety valve不要(閾値0.98未満)。
  Standard TTS一発で全13標準segment+Trial追加segment(tension_reflection)+
  Key Phrase 5件が`status=OK`(retryなし、ASR検証PASS)。
- **版2(三人称、P3): 未完成(Gate停止、override無し)。** Voice A(point_one)は
  三人称でも1回目からEXACT_MATCHでPASS。**Voice B(point_two)は三人称化後、
  3回ともAudio Validation Gateで`TRUE_CONTENT_MISMATCH`となりSTOPPED**、
  Production Gate(`verify_episode_audio_validation_gate`)がepisode全体の
  Assemblyを中止した。overrideもfallback追加も行っていない
  (§5参照、USER_DECISION_REQUIRED)。

## 1. 音声化した版

| 版 | 内容 | 状態 |
|---|---|---|
| P1 | Trial-07記事そのまま(一人称) | 完成 |
| P3 | Voice A/Bのみ機械的に三人称変換、他はP1の音声を再利用 | Voice A(point_one)完成/Voice B(point_two)Gate停止 |

## 2. Standard同期の証拠

`raw_usage_log.jsonl`全件で`tts_execution_mode=STANDARD`のみ確認
(Batch値は0件)。使用model_id: `gemini-2.5-pro-preview-tts` /
`gemini-3.1-flash-tts-preview`(TTS)、`gpt-4o-mini-transcribe`(ASR)、
`gpt-5.6-luna`(Support/Writer text、Model Routing Contract承認済み)。

## 3. 5区切り→既存B1構造マッピングと不整合の観察

マッピング: Hook(The Question、2文+2文にバランス分割)→Full Story Part1/2、
One Voice→Point One、Another Voice→Point Two、What the Seat Really Means→
In One Line。**Where the Difference Comes From(Tension)は既存11-partに
対応slotが無い。** Production関数(`load_b1_sources`/`apply_b1_gain`は
`b1_segments`辞書をgenericにiterateする実装のため無変更のまま拡張可能、
`build_b1_timeline`のみ11個固定segment名をハードコード)は無変更のまま、
Trial専用の`build_b1_voices_timeline()`でPoint Two本文の直後・Comment 4の
前に第4のAoede地の文beatを追加した(pause=0.7秒、既存の
HEADING_TO_BODY_PAUSE_SECONDS_B1を流用、新しい値は発明していない)。
**これは既存B1に存在しないAoede→Aoede連続遷移であり、Production採用には
正式なslot設計判断が必要**(USER_DECISION_REQUIRED)。

## 4. Preview/Comment/Key Phraseの生成結果と整合観察

Production Support経路(`sc.run_b1_scaffold`/`sc.run_key_phrases`)を無変更で
使用。全文は`p1/b1b/b1_support_texts.json`。

- Preview/Comment1-4は、ROLE prompt自体には"Point One/Point Two"という
  文言が含まれるにもかかわらず、生成結果は"two views"/"the two voices"と
  自然に言い換えられ、"Point"という語は一度も出力されなかった(良好、
  ただし非決定的でありProduction採用を保証するものではない)。
- **Comment 2の役割衝突を観察**: Hookを文単位でバランス分割したため、
  疑問文("Why can the same office feel secure...")がpart2側に入った。
  Comment 2の役割(前半回収+後半への問い)が生成した問いが、直後に
  Full Story Part 2で読まれる疑問文とほぼ同内容になり、軽い重複感がある。
  Hookの分割点を「疑問文はpart1側に含める」等に変えれば緩和できるが、
  これは記事の実質的な構造判断であり本Trialでは変更していない。
- **Key Phrase Canonicalizationが一人称記事で初回STOPした(重要な発見)**:
  1回目の選定でrank3候補「give me distance」→正規形「give someone
  distance」が、Hard Requirement Validator(Rule7、
  `er003_key_words_canonicalization.py`の`_PERSON_DEPENDENT_TO_GENERIC`
  閉じた語彙集合)により`CANONICALIZATION_INVALID`で停止した
  (`run_key_phrases()`はcanonicalization失敗時にselectionへの自動retryを
  行わない設計のため、そのまま止まる)。原因を直接確認したところ、
  `_PERSON_DEPENDENT_TO_GENERIC`辞書(my/your/his/her/its/their/our/
  you/they/he/she/yourself/himself/herself/themselves/yours/theirs)に
  **一人称の"I"/"me"が含まれていない**(三人称の一般記事では出現しないため
  未整備だったと推測される)。今回はKey Phrase選定を独立に再実行し
  (Production関数は無変更、単なる再呼び出し)、2回目の選定で"me"を含む
  候補を避けた5件が`CANONICALIZATION_PASS`/`REDUNDANCY_PASS`となり
  以後のTTSへ進めた。**Voices(一人称記事)をProduction採用する場合、
  この語彙集合へ"I"/"me"を追加するかどうかは正式なSpec判断が必要**
  (USER_DECISION_REQUIRED)。証跡: 現在のdisk上の
  `p1/b1b/key_phrases/canonicalization_runtime_metadata.json`は2回目
  (成功)の記録(1回目の失敗記録は同一パスへの再実行で上書きされ消失した。
  失敗の内容はこのセッション中に直接確認済みで上記の通り正確に再現できる。
  検証可能な一次証拠として`_PERSON_DEPENDENT_TO_GENERIC`辞書自体は現在も
  `er003_key_words_canonicalization.py` 297-315行に存在し、"I"/"me"が
  無いことは今も直接確認できる)。

## 5. TTS結果(segment別attempt・Gate停止・重複monitoring)

- P1: 全13標準segment+tension_reflection+KP5件、すべて1回目でOK
  (Gate停止0件)。
- P3: point_one(3P)は1回目でEXACT_MATCH/OK。**point_two(3P)は3回とも
  `TRUE_CONTENT_MISMATCH`でSTOPPED。** 実際のASR文字起こしを原文と
  比較すると差分は「comma1箇所」「do not→don't」「emダッシュの
  トークン化差("need—or"→"need"+"or")」のみで、内容的な欠落・幻聴は
  無い(`audit/third_person_diff.txt`と`audit/stopped_audio_evidence/
  point_two_result.json`参照)。overrideは行わず、最終attempt音声を
  `p3/b1b/audit/stopped_audio_evidence/point_two_last_attempt_status_
  STOPPED.wav`へ保全した(未検証、参考用としてplayer.htmlにも掲載)。
- **OPEN-121 Method A(n-gram3語)+Method D(自己相関)によるmonitoring
  (gate化せず)**: P1の全14 segment×(単体wav+episode該当区間)、P3の
  point_one/point_two単体wavで実行(いずれもローカルfaster-whisper、
  API課金無し)。Method D自己相関のbest_run_lengthは全segmentで
  0.01〜0.14秒(実在の重複bugの実測値[1秒以上]と比べ十分小さく、
  疑わしい反復は無し)。**Method AがP1のpoint_twoを1件flag**
  (`audit/monitoring_p1.json`)。詳細確認の結果、これは実際のTTS重複
  ではなく、**Method Aのcanonical crosscheck自体の既知の限界**
  (原文の"need—or do not need—around me"というemダッシュ直結表現を、
  canonicalテキスト側の単純split()トークナイザが"need—or"を1トークン
  として扱ってしまい、ASR側の分離済みトークンと数が合わず、正当な
  2回目の"do not need"を意図的反復として認識できない)による
  false positiveと判断した(P3の同箇所は"don't"表記ゆれのため
  flagされず、この解釈と整合)。gate化していないため実害無し、
  monitoring専用ロジックの改善余地として記録する。

## 6. Assembly結果

- P1: `p1/b1b/assembled/Voices_Trial08_B1B_VOICES_TRIAL08_P1.wav`
  (298.665秒、peak=0.928、clipping無し、headroom valve未適用)。
- P3: Gate停止によりAssembly未実施(`p3/b1b/run_summary_assemble.json`
  相当は`GATE_BLOCKED`)。

## 7. 三人称変換の差分(原文)

`audit/third_person_diff.txt`(Voice A/B双方、単語unified diff)。
LLM 1回呼び出し(model=gpt-5.6-luna、Model Routing Contract経由)、
指示は「人称代名詞・それに伴う動詞のみ変更、他は一切変更しない」。
実測差分は代名詞・所有格・動詞の3人称一致のみで、文の追加・削除・
語順変更・数値/事実の変化は無い。**1点、意味的な副作用を観察**:
Voice Aの"I miss the same desk... They helped me start..."は原文では
"They"=机・引き出し・眺め(物)、"me"=話者、という異なる指示対象だったが、
機械的変換後は両方とも"they/them"になり、"They miss...They helped
them..."と**同一代名詞が2つの異なる指示対象を指す**形になった
(文法的には成立するが、リスナーが聞いて誤読しうる曖昧さを新たに生んだ)。
一人称→三人称の機械的変換が「意味を変えない」を機械的には満たしても、
聞き手の理解容易性には副作用がありうる実例。

## 8. 比較観点の客観整理(最終判断はユーザー)

- 誰のVoiceか分かりやすいか: P1は"One Voice:"/"Another Voice:"見出しが
  Aoedeで読まれた後すぐ一人称"I"で始まるため、切替点は明瞭。P3は
  Voice Aのみ聴取可能("the employee...they")。
- Narratorが一人称を読む違和感: 客観指標なし、要試聴判断
  (player.htmlのVoice A(1P) vs Voice B(1P)行で確認可能)。
- 実在人物のquoteと誤認しそうか: 客観指標なし、要試聴判断。
- Voice切替の自然さ: Comment 3が"we will hear two views about what a
  desk means..."と自然に前振りしており、構造的には切替が予告されている。
- Voices Familyとしての自然さ: 上記4.のComment/Preview観察を参照。

## 9. Cost

累計 **¥39.49**(内訳: openai(Support text)¥5.90、gemini(TTS)¥31.86、
openai_asr(検証)¥1.73)。上限¥500に対し十分な余裕。ログ:
`audit/raw_usage_log.jsonl`。

## 10. USER_DECISION_REQUIRED

1. 一人称Voiceの正式採用判断(本Trialは音声化確認のみ、Contract化しない)。
2. 5区切り→11-part構造拡張(Tension用の4th beat)をProduction仕様として
   正式にslot設計するか。
3. Key Phrase Canonicalization Rule7の閉じた語彙集合へ"I"/"me"を追加するか
   (一人称記事をProductionで扱う場合、初回STOPが起きやすい実測を確認済み)。
4. P3 point_two(Voice B三人称)のHuman Review承認可否(§5のASR差分を
   人間が試聴して判断。override未実施のまま保留)。
5. 三人称機械的変換の代名詞衝突リスク(§7)をどう扱うか
   (Voices個別記事ごとの人手レビューを要求するか等)。

## 11. SSOT登録案

`OPEN_ITEMS.md`へ「Lane B Voices音声化Trialの構造・KP・Gate観察」として
新規項番登録を提案(本ReportをFableへ引き渡し、正式登録はFable判断)。

---
証跡: `er012_output/editorial_b_voices_trial_08_audio/`配下
(`audit/`に各stageのsummary json、`p1/b1b/`・`p3/b1b/`にProduction同型の
narration/audit/assembled一式)。Git操作は未実施(Fableが統合)。
