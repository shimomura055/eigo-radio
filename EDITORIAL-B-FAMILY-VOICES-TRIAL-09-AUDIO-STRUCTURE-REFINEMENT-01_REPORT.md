# EDITORIAL-B-FAMILY-VOICES-TRIAL-09-AUDIO-STRUCTURE-REFINEMENT-01_REPORT

管理ID: EDITORIAL-B-FAMILY-VOICES-TRIAL-09-AUDIO-STRUCTURE-REFINEMENT-01
Lane: Lane B / Voices-Perspective。種別: Trial音声化(ユーザー判断反映版、2026-09-07)。
Production採用なし(一人称/Voice A・B固定/Voices Comment Prompt/Tension第4 beat/
新音声構造/KP canonicalization、いずれもAPPROVED_FOR_PRODUCTIONを付与していない)。
TTSはStandard同期(`TTS_EXECUTION_MODE=STANDARD`)。commit権は本タスクのみ。

入力: `er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/article.md`(本文無変更、
title/hook/one voice/another voice/tension/closingの5区切り構造そのまま)。

## 1. 使用voice
- Voice A(One Voice本文): **Algieba**
- Voice B(Another Voice本文): **Erinome**
- Narrator(Voice A/B見出し・Hook・Tension・Closing): **Aoede**(既存Production
  point_headings.generate/news_tail_fix経路そのまま)
- Comment 1〜4・topic_intro・Preview: **Charon**(既存Production voice01.generate_charon_english
  そのまま)

## 2. Algieba/Erinome使用可否
現行Gemini TTSランタイム(`gemini-2.5-pro-preview-tts`)で、既存voice指定と同じ引数経路
(`er002_gemini_client.make_tts_call_fn(voice_name)` / `er006_batch_tts_wiring_01.
make_batch_tts_call_fn(model_name, voice_name)`)にAlgieba/Erinomeをそのまま渡して単発生成を
実施した結果、両方ともAPI呼び出しレベルで**問題なく利用可能**(status=OK、単発take)。

## 3. 変更理由
変更なし(第一候補どおりAlgieba/Erinomeを採用)。

## 4. Schedar/Sulafat比較sample
Voice Aの先頭3文("Every morning, I look for an empty desk. Someone else may have used it
yesterday, and someone new may sit there tomorrow. I cannot leave papers in a drawer, and I
sometimes worry about using a desk or keyboard after someone else.")を、Algieba/Erinome/
Schedar/Sulafat/Aoedeの5 voiceで同一生成した(単発take、ASR retry cascadeなし、比較目的のみ)。
全5件status=OK。音源: `er012_output/editorial_b_voices_trial_09_audio/audit/voice_samples/
sample_{voice}.wav`、結果一覧: 同ディレクトリ`voice_sample_results.json`。player.htmlにも
5voice横並びで掲載。最終的な聞き分け判断はユーザー。

## 5. Comment 1〜4全文と役割適合セルフチェック
Voices Family用Comment Editorial Contract(Trial限定ROLE prompt、Production Prompt無変更)で
生成。生成後、既存Production `vfl01.run_deviation_check`(無変更)でLedger Deviation Check
→**LEDGER_COMPLIANT**(deviations 0件)。さらにLLM自己チェック(引用付き、4件とも
`compliant=true`)を実施。

- **Comment 1**: "Even a familiar workplace can feel very different from one person to
  another." — セルフチェック: compliant。The Questionの具体的状況を先取りせず、Point要約や
  Discovery口調も無い、との判定(evidence_quote空)。
- **Comment 2**: "The question asks how the same office can feel different to different
  people. Now, you will hear two voices, one after the other, each speaking from a different
  point of view." — セルフチェック: compliant。Voice A/B内容の先取りなし、見出し文言("The desk
  that lets work begin"等)を言っていない、Point One/Two表現もなし、との判定。
- **Comment 3**: "You have heard two people describe their experience of the same workplace.
  The question now is not which voice is right. It is why the same situation can feel
  different to different people." — セルフチェック: compliant。Tensionの答えを先に説明せず、
  どちらの声も「正しい」と評価していない、との判定。
- **Comment 4**: "Instead of asking who is right, let's ask what is making this situation feel
  different for each person. That question takes us below the surface of the disagreement." —
  セルフチェック: compliant。Closingの要約・結論の先取りなし、解決策提案もなし、との判定。

Preview("In this episode, we look at the debate over assigned desks and shared seating. Why
does this choice matter at work, and what can a desk mean to the person using it?")は既存
Production Prompt(`b1s.PREVIEW_ROLE`)を無変更で使用。

証跡: `er012_output/editorial_b_voices_trial_09_audio/b1b/b1_support_texts.json`(全文)、
`b1b/audit/support_ledger_deviation.json`、`b1b/audit/comment_self_check.json`(引用付き
セルフチェック全文)。

## 6. SFX配置(意図した timeline)
既存Production Point用SFX(`POINT_NOTIFICATION_MP3_PATH`)を無変更のまま再利用、新規SFX制作
なし。意図した配置は以下(Trial専用`build_b1_voices_timeline_trial09`で実装、`asm.load_b1_
sources`/`apply_b1_gain`/`assemble_with_timeline`/`apply_headroom_safety_valve`はいずれも
Production無変更):

Intro→Welcome→Topic intro→Notification1→Preview intro→Preview→Notification2→Key phrases
intro→Key Phrase×5→Notification3→Full story intro→**Comment 1**→**Hook Part1/Part2(Aoede、
見出し非読み上げ、単一block扱い)**→**Comment 2**→**[既存Point SFX]**→**Narrator: "One Voice:
The desk that lets work begin."(Aoede)**→**Voice A本文(Algieba)**→**[既存Point SFX]**→
**Narrator: "Another Voice: The freedom to move."(Aoede)**→**Voice B本文(Erinome)**→
**Comment 3**→**Tension(Aoede、見出し非読み上げ)**→**Comment 4**→**Closing(Aoede、見出し
非読み上げ、In One Line)**→Outro。

**Trial限定の解釈判断(要ユーザー確認)**: 指示文の並び("...Closing→Key Phrase→その他既存
episode必須要素...は既存B1構造どおり")について、Key PhraseをClosing直後へ literal に移動する
解釈と、「Key phrases intro含む周辺要素は既存B1構造の位置(Preview直後)のまま」という解釈の
両方が読み得たため、本Trialでは**後者(既存位置のまま)**を採用した。位置を変更する場合は別途
指示が必要。

**実測**: Gate停止(§9参照)により1本化Assemblyが完了せず、実際の`timeline.json`(開始秒等)は
今回未生成。構造自体は各segmentが個別に生成・ASR検証済みであり、fallback player(§9)で構造順
に確認できる。

## 7. Narrator heading読み上げ結果
- One Voice見出し("One Voice: The desk that lets work begin.")→ASR="One voice, the desk that
  lets work begin."(NORMALIZED_MATCH、**OK**)。
- Another Voice見出し("Another Voice: The freedom to move.")→ASR="the freedom to move"
  ("Another Voice"部分が脱落、**ASR_VALIDATION_UNCERTAIN**→リトライせず`HUMAN_REVIEW_LOCKED`、
  詳細は§9)。

## 8. heading非読み上げ結果
Hook("The Question")/Tension("Where the Difference Comes From")/Closing("What the Seat
Really Means")のheading文字列はいずれもTTS入力に含めず、本文のみ生成した(意図どおり)。

## 9. 一人称の聞こえ方(客観整理)
- Voice A本文(Algieba)ASR: "Every morning, I look for an empty desk. ..."(**EXACT_MATCH**、
  canonical textと一字一句一致)。
- Voice B本文(Erinome)ASR: "Some mornings, I choose a quiet corner because I need to think.
  ..."(**NORMALIZED_MATCH**)。
- 両方とも直前にNarrator(Aoede)が"One Voice: .../Another Voice: ..."を読み上げてから始まる
  ため、構造上は「誰の声か」がNarratorの一言で明示されてから一人称本文に入る設計。実際の
  聞こえ方(切替の自然さ・実在人物との誤認のしにくさ)はplayer.htmlでの試聴が必要(客観指標=
  ASR一致度は良好、主観評価はユーザー判断待ち)。

## 10. Voice A/Bの聞き分け(客観整理)
Voice A=Algieba、Voice B=Erinomeで生成、いずれもASR検証PASS(EXACT_MATCH/NORMALIZED_MATCH)。
§4の比較sample(同一textを5voiceで生成)をplayer.htmlに並べたので、AlgiebaとErinomeの音質差
(および他候補Schedar/Sulafat・Narrator Aoedeとの差)はそちらで直接比較できる。定量的な音響
指標(ピッチ・話速等)による自動判定は本Trialでは実施していない(客観データはASR一致のみ)。

## 11. 完成試聴artifact(URL・構成)
`er012_output/editorial_b_voices_trial_09_audio/player.html`
(`file:///C:/Users/tensh/eigo-radio/er012_output/editorial_b_voices_trial_09_audio/player.html`)

**§9(Gate)の結果、1本化assembled episode audioは今回未生成**(§12参照)。player.htmlは
Gate状態に応じて自動的に以下を出力する設計:
- Gate通過時: 1本化wav + seek可能timelineテーブル + 完全スクリプト(segmentごとvoiceラベル
  付き) + voice比較sample。
- **今回の実際の出力(Gate blocked)**: 構造順(1〜13)にsegment単体wavを個別再生できる
  fallback player + BLOCKED理由の全文表示 + 完全スクリプト + voice比較sample。ブロックされた
  point_two_headingの行は、**Human Review Lockで保存された最終attempt音声(未検証、evidence
  専用)**を明示ラベル付きで再生可能にした(`status=HUMAN_REVIEW_LOCKED, UNVALIDATED
  evidence-only`)。

## 12. Tension+Comment 3/4の流れ
Comment 3("...The question now is not which voice is right. It is why the same situation can
feel different to different people.")→Tension本文("The disagreement is not really about
movement. It is about where stability comes from. ...")→Comment 4("Instead of asking who is
right, let's ask what is making this situation feel different for each person. ...")→Closing
("The real question is not fixed desks or shared desks. ...")という接続をテキストレベルで
確認した。Comment3→Tensionは「対立の中身」から「なぜ違って感じるか」へ、Comment4→Closingは
「表面的対立」から「一段深い問い」へ、それぞれ視点が移る設計どおりの流れになっている(音声上の
実際の連続性は、1本化Assembly完了後に確認が必要、§9・§16参照)。

## 13-15(音声類似度monitoring)
本Trialのタスク範囲外(ユーザー指定18項目のうち本タスク対象外のため未実施)。

## 16. Trial status
**Gate-mediated partial completion**。14 segment中13segmentがVALIDATED(ASR EXACT_MATCH/
NORMALIZED_MATCH、1回目のattemptでPASS、retryなし)。**point_two_heading("Another Voice: The
freedom to move.")のみ、既存Audio Validation Gate/Human Review Lock機構により
`HUMAN_REVIEW_LOCKED`となり、1本化episode Assemblyがブロックされた**。overrideは一切行って
いない(D4準拠)。同一canonical textはTrial-08の初回attemptで正常にPASSしており(ASR="Another
voice, the freedom to move."、NORMALIZED_MATCH)、今回のみ非決定的なTTS/ASRの揺れで発生した
可能性が高い。音声化自体(全13segmentの生成・SFX配置設計・player.html構築)は完了させた。

## 17. USER_DECISION_REQUIRED
1. **Voice B見出しのHuman Review承認/再生成可否**: `er012_output/editorial_b_voices_trial_09_
   audio/b1b/audit/stopped_audio_evidence/point_two_heading_last_attempt_status_
   HUMAN_REVIEW_LOCKED.wav`を試聴のうえ、(a) 内容的に問題なければ`record_human_approval()`で
   承認するか、(b) 再生成を許可する場合は`approve_regenerate()`をユーザー自身の明示指示で
   実行するか(いずれもSonnetが自動実行しない設計、ER-011 Human Review Lockの意図どおり)。
   これが解決すれば1本化episode Assemblyを再実行できる。
2. Voice A(Algieba)/Voice B(Erinome)の正式固定可否。
3. Voices Family用Comment 1〜4 Editorial Contract(候補Prompt)のProduction採用可否。
4. Tension slot(既存11-part固定schemaに対応slot無し)の正式追加可否・設計。
5. Key PhraseをClosing直後へ移動する解釈と、既存位置(Preview直後)据え置きの解釈のどちらが
   意図どおりか(§6参照、本Trialは後者を採用)。
6. 新音声構造(Narrator heading+別voice Voice A/B+SFX再利用)全体のProduction採用可否。

## 18. SSOT登録案
`OPEN_ITEMS.md` OPEN-120行へ(h) Trial-09として要旨を追記済み(本Reportへのリンク含む)。
`DECISION_LOG.md` `EDITORIAL-B-FAMILY-VOICES-SERIES-02-05`エントリへ短い追記を実施済み。
Production採用判断(§17)は別途ユーザー承認後、新規エントリまたは同エントリへの追記で記録する。

## TTS結果サマリ(segment別status)
| segment | status | ASR classification |
|---|---|---|
| topic_intro | OK | NORMALIZED_MATCH |
| preview | OK | EXACT_MATCH |
| comment_1 | OK | EXACT_MATCH |
| comment_2 | OK | NORMALIZED_MATCH |
| comment_3 | OK | NORMALIZED_MATCH |
| comment_4 | OK | EXACT_MATCH |
| point_one_heading (Narrator) | OK | NORMALIZED_MATCH |
| point_two_heading (Narrator) | **HUMAN_REVIEW_LOCKED** | ASR_VALIDATION_UNCERTAIN |
| point_one (Voice A, Algieba) | OK | EXACT_MATCH |
| point_two (Voice B, Erinome) | OK | NORMALIZED_MATCH |
| full_story_part1 (Hook, 再利用) | OK(Trial-08流用) | EXACT_MATCH |
| full_story_part2 (Hook, 再利用) | OK(Trial-08流用) | EXACT_MATCH |
| tension_reflection (再利用) | OK(Trial-08流用) | NORMALIZED_MATCH |
| in_one_line (Closing, 再利用) | OK(Trial-08流用) | NORMALIZED_MATCH |
| Key Phrase 1〜5 (英日、再利用) | OK(Trial-08流用) | - |

証跡: `er012_output/editorial_b_voices_trial_09_audio/b1b/audit/tts_generation_results.json`、
`b1b/audit/reused_from_trial08.json`(text hash一致確認、`hash_match: true`)。

## Standard同期の証拠
実行前に`os.environ["TTS_EXECUTION_MODE"] = "STANDARD"`をscript冒頭で設定(Batch API不使用)。
`tts_generation_results.json`の各attemptに`tts_execution_mode`フィールドが記録されており、
全件`"STANDARD"`。

## cost
累積 **約31.11円**(上限800円、大幅に余裕あり)。内訳: gemini(TTS)29.39円、openai(Comment/
Preview/Ledger Deviation/自己チェック等)0.71円、openai_asr(ASR検証)1.01円。Key Phrase・
Hook・Tension・Closingの音声はTrial-08から再利用したため重複TTSコストを回避した。

## 触れなかったもの(確認)
Productionコード・Prompt・Validator・Assembly本体は無変更(Trial adapter経由でのみ利用)。
Lane A(`er011_*`)・CURRENT_SPEC.mdは未変更。
