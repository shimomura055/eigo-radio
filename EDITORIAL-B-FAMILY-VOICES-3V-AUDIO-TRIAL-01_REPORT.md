# EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01

管理ID: EDITORIAL-B-FAMILY-VOICES-3V-AUDIO-TRIAL-01(Lane B、Audio Trial)。
Production module(`er012_b_family_voices_production_01.py`・
`er012_b_family_production_runner_01.py`)・registry
(`er012_b_family_editorial_type_registry_01.py`)・Contractは無編集。
SSOT・Git操作なし。

## 入力・実装

- 基準記事: `er012_output/editorial_b_voices_3v_person_voice_trial_02/
  b1b_run01_attempt2/article.md`(497語、B-3V-3=(a)で承認済み)。6区切り
  構造(Hook/3 Voices/Tension/Closing、`##`/`###`混在見出し)を新規parser
  (`split_six_voice_sections`)で正しく分解できた(実測確認)。
- 新規Trialファイル: `er012_editorial_b_voices_3v_audio_trial_01.py`
  (root)。Production TTS関数(`b1prod.generate_voice_body_wide_margin`・
  `voice01.generate_charon_english`・`point_headings.generate`・
  `news_tail_fix.generate_news_narration_wide_margin`・Key Phrase生成
  primitive群)は全て**引数で呼ぶだけ**(Production側は無変更)。3声構造に
  必要な新ロジック(6区切りparser・3声版parts builder・3声版Assembly
  timeline builder・3声版required_structure・3声版loader)のみ本ファイルへ
  新規追加した。

## Voice割当・実発話確認

Voice 1(応募者)=Algieba / Voice 2(採用担当)=Erinome / Voice 3(経営者)=
Schedar(Fable決定、承認済み候補内)。3 voices全て技術的availability
OK(sample生成成功)。ASR照合: point_one(Algieba)は1回ミスマッチ後2回目で
`EXACT_MATCH`、point_two(Erinome)・point_three(Schedar)は1回目で
`EXACT_MATCH`/`NORMALIZED_MATCH`(通常のretry cascade範囲内、Human Review
Lockは一度も発動せず)。16 segment全て`status=OK`・`asr_verified=True`・
clipping無し。disfluency_checked=Trueをpreview/comment_1-4/in_one_line/
point_one_heading/point_two_headingで確認(共有Production必須辞書どおり)、
point_three_headingも実測でTrue(必須ではないが実際にQA済み)。OPEN-121/
OPEN-122安全機構(repetition QA・connected speech equivalence layer)を
point_one/two/threeへ同一規約(enable=True)で対称適用した(実測
`repetition_qa_checked=True`を3声全てで確認)。

## Comment 1-4・Preview

Comment 1・4は既存確定Contract(`registry.COMMENT_ROLES`)をそのまま
LLM生成(人数非依存の文言のため無変更で使用可能、実際に3V記事向けへ生成
成功)。Comment 2・3は design.md B-1 の3V版ドラフト文言をLLM再生成せず
そのまま使用(`TRIAL_ONLY_MANUAL_DRAFT_NOT_LLM_GENERATED`、未承認・
Trial-only、registryへは書かない。Trial-01`qa/comments_1_to_4.json`と
同一方式)。

## Audio Validation Gate(既定OFF経路+opt-in ON経路)

既定OFF経路(`verify_episode_audio_validation_gate(out_dir,"B1")`、
required_structure=None): **PASS**。opt-in ON経路(Trial側正本
`build_required_structure_3v()`、16 segment・point_one/two/three命名、
既存B_FAMILY_B1_REQUIRED_SEGMENTS+Voice 3の1段拡張): **PASS**。
ON経路の有効性をnegative controlで実証: (1) voice_3名を意図的に誤らせると
`VOICE_MISMATCH`で正しくBLOCKED、(2) point_threeをrequired一覧から外すと
`UNEXPECTED_EXTRA_SEGMENT`で正しくBLOCKED(design.md B-5が新規発見した
「Voice 3欠落を検知できない」failure modeに対する対策として機能することを
実測確認)。

## Assembly・実測尺

`B_Family_3V_Audio_Trial_01_B1B.wav`(48kHz/2ch)。duration=**356.613秒**
(目標380〜400秒、範囲外・約6〜11%不足)。clipping無し、peak=0.95
(headroom safety valve未発動、閾値0.98未満)。Tensionスロットを3者統合
版として実際に音声化(「Why They See It Differently」)。

## Fact/content integrity

記事本文からの抽出(build_parts_3v)がsection本文と完全一致することを
6項目で確認(全てTrue)。Key Phrase used_formのうち2件("screen a résumé"
"be reduced to a score")は記事内の非連続語・活用形からのcanonicalization
(既存Production Key Phrase選定/正規化の通常挙動、逐語一致ではない設計
どおり)。詳細: `er012_output/editorial_b_voices_3v_audio_trial_01/b1b/
audit/content_integrity_check.json`。

## Gate 7 (a)〜(l)

標準player形式(Seek+Segment名+voice+実発話script+個別音声を同一行、
`audio_review_player.py`共通部品)で33 timeline行+5 Key Phrase行、
「未取得」行0件を実測確認。

## 費用(¥93.82、上限¥120)

TTS(gemini)=¥57.69 / LLM(openai、Key Phrase選定・canonicalization+
Comment/Preview生成)=¥33.41 / ASR検証(openai_asr)=¥2.72。

## Gate 1分類: **USER_DECISION_REQUIRED**

3 voices・6区切り構造・Comment 2/3・Audio Validation Gate(両経路)・
Fact/content integrityは全て成立したが、**実測尺356.6秒が目標
380〜400秒の範囲外**(約6〜11%不足)のため、B-3V-2の成功基準
(「3声・構造・Gate・尺・整合すべて成立」)を完全には満たさない。VALIDATED
とは分類せず、尺の扱い(目標レンジ自体の見直し/許容範囲拡大/本文追加の
要否)をユーザー判断待ちとする。

## Production配線に必要な項目(未承認、実装なし)

1. registryの`build_required_structure()`を可変voice数シグネチャへ拡張
   (現状2声固定)。
2. Gate辞書`DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`/
   `B_FAMILY_A2_SLOWDOWN_TARGET_SEGMENTS`へ`point_three`/
   `point_three_heading`の登録要否(現状未登録、B1では従来からpoint_one/
   twoも対象外のため対称、A2化する場合は要検討)。
3. Comment 2/3の3V文言をContract化(Role prompt自体の正式書き換え、
   現状はTrial-only手動ドラフト)。
4. mode/level命名方針の確定(OPEN-132)。
5. Voice 3(Schedar)の「fallbackから本採用への格上げ」自体のユーザー
   正式承認(design.md B-2既出論点)。

## 試聴artifact

`file:///C:/Users/tensh/eigo-radio/er012_output/editorial_b_voices_3v_audio_trial_01/player.html`

## 新規ファイル

- `er012_editorial_b_voices_3v_audio_trial_01.py`(root、新規)
- `er012_output/editorial_b_voices_3v_audio_trial_01/`(新規出力一式)

---
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SPsKBAZP5KEqdTH9TnkJdp
